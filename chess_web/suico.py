"""Suíço local: pontuação, adversários inéditos e cores estritamente compatíveis.

Não implementa todos os critérios de flutuação do sistema holandês FIDE.
Pontos são calculados em meios pontos inteiros para evitar arredondamento.
"""
from itertools import combinations
import networkx as nx
from django.db import transaction
from django.db.models import F
from chess_web.models import Torneios, Inscricao, RodadaSuica, Partida


def estado(torneio):
    jogadores = {i.usuario_id: {
        'usuario': i.usuario, 'numero': i.numero, 'pontos2': 0,
        'adversarios': set(), 'cores': [], 'folgas': 0, 'vitorias': 0,
    } for i in torneio.inscricoes.select_related('usuario').order_by('numero')}
    for rodada in torneio.rodadas_suicas.order_by('numero'):
        if rodada.folga_id:
            jogadores[rodada.folga_id]['pontos2'] += 2
            jogadores[rodada.folga_id]['folgas'] += 1
    for p in Partida.objects.filter(rodada_suica__torneio=torneio).order_by('rodada', 'pk'):
        a, b = jogadores[p.jogador_branca_id], jogadores[p.jogador_preta_id]
        a['adversarios'].add(p.jogador_preta_id)
        b['adversarios'].add(p.jogador_branca_id)
        a['cores'].append('B')
        b['cores'].append('P')
        if p.vencedor == 'B':
            a['pontos2'] += 2
            a['vitorias'] += 1
        elif p.vencedor == 'P':
            b['pontos2'] += 2
            b['vitorias'] += 1
        elif p.vencedor == 'E':
            a['pontos2'] += 1
            b['pontos2'] += 1
    return jogadores


def classificacao(torneio):
    jogadores = estado(torneio)
    for j in jogadores.values():
        j['pontos'] = j['pontos2'] / 2
        # Buchholz simples: soma dos pontos atuais dos adversários reais.
        # A folga vale 1 ponto, mas não acrescenta adversário virtual.
        j['buchholz'] = sum(jogadores[a]['pontos2'] for a in j['adversarios']) / 2
    return sorted(jogadores.values(), key=lambda j: (-j['pontos2'], -j['buchholz'], -j['vitorias'], j['numero']))


def bloquear_torneio(id):
    # A escrita também serializa as operações no SQLite, onde FOR UPDATE é ignorado.
    Torneios.objects.filter(pk=id).update(numero_rodadas=F('numero_rodadas'))
    return Torneios.objects.select_for_update().get(pk=id)


@transaction.atomic
def salvar_inscricoes(torneio_id, usuarios):
    torneio = bloquear_torneio(torneio_id)
    if torneio.rodadas_suicas.exists():
        raise ValueError('As inscrições ficam fechadas após gerar a primeira rodada.')
    ids = sorted(set(usuarios))
    if len(ids) < 2:
        raise ValueError('Selecione pelo menos dois participantes.')
    torneio.inscricoes.all().delete()
    Inscricao.objects.bulk_create([Inscricao(torneio=torneio, usuario_id=id, numero=n) for n, id in enumerate(ids, 1)])


def orientar(a, b, jogadores):
    opcoes = []
    for branca, preta in [(a, b), (b, a)]:
        custo = 0
        for id, cor in [(branca, 'B'), (preta, 'P')]:
            cores = jogadores[id]['cores']
            saldo = cores.count('B') - cores.count('P')
            novo = saldo + (1 if cor == 'B' else -1)
            if abs(novo) > 2 or cores[-2:] == [cor, cor]:
                break
            custo += abs(novo) * 2 + int(bool(cores) and cores[-1] == cor)
        else:
            opcoes.append((custo, branca, preta))
    return min(opcoes) if opcoes else None


def combinar(ids, jogadores):
    grafo = nx.Graph()
    grafo.add_nodes_from(ids)
    quantidade = len(ids)
    # Diferença de pontos tem precedência sobre a soma de todas as preferências
    # de cores; estas, por sua vez, precedem a ordem inicial de inscrição.
    base_cor = quantidade ** 3 + 1
    base_pontos = (quantidade * 20 + 1) * base_cor
    for a, b in combinations(ids, 2):
        if b in jogadores[a]['adversarios']:
            continue
        orientacao = orientar(a, b, jogadores)
        if orientacao is None:
            continue
        cor, branca, preta = orientacao
        diferenca = abs(jogadores[a]['pontos2'] - jogadores[b]['pontos2'])
        desempate = abs(jogadores[a]['numero'] - jogadores[b]['numero'])
        grafo.add_edge(a, b, weight=diferenca * base_pontos + cor * base_cor + desempate, branca=branca, preta=preta)
    pares = nx.min_weight_matching(grafo)
    if len(pares) * 2 != len(ids):
        return None
    return sorted([(grafo[a][b]['branca'], grafo[a][b]['preta']) for a, b in pares], key=lambda par: min(jogadores[i]['numero'] for i in par))


@transaction.atomic
def gerar_rodada(torneio_id, data, rodada_atual):
    torneio = bloquear_torneio(torneio_id)
    ultima = torneio.rodadas_suicas.order_by('-numero').first()
    numero_atual = ultima.numero if ultima else 0
    if numero_atual != rodada_atual:
        raise ValueError('A rodada mudou. Atualize a página antes de gerar novamente.')
    if Partida.objects.filter(Torneios=torneio, rodada_suica__isnull=True).exists():
        raise ValueError('Este torneio contém partidas manuais. Crie um torneio separado para o sistema suíço; os registros antigos serão preservados.')
    if ultima and ultima.partidas.exclude(vencedor__in=['B', 'P', 'E']).exists():
        raise ValueError('Registre todos os resultados da rodada atual antes de gerar a próxima.')
    jogadores = estado(torneio)
    ids = sorted(jogadores, key=lambda i: jogadores[i]['numero'])
    if len(ids) < 2:
        raise ValueError('Inscreva pelo menos dois participantes.')
    limite = min(torneio.numero_rodadas, len(ids) - 1 if len(ids) % 2 == 0 else len(ids))
    if numero_atual >= limite:
        raise ValueError('O torneio atingiu o limite de rodadas disponíveis.')
    if len(ids) % 2:
        folgas = sorted([i for i in ids if not jogadores[i]['folgas']], key=lambda i: (jogadores[i]['pontos2'], -jogadores[i]['numero']))
    else:
        folgas = [None]
    for folga in folgas:
        ativos = [i for i in ids if i != folga]
        if numero_atual == 0:
            metade = len(ativos) // 2
            pares = [(a, b) if n % 2 == 0 else (b, a) for n, (a, b) in enumerate(zip(ativos[:metade], ativos[metade:]))]
        else:
            pares = combinar(ativos, jogadores)
        if pares is not None:
            break
    else:
        raise ValueError('Não foi possível gerar uma rodada completa sem repetir adversários ou violar os limites de cores. Nenhuma partida foi criada; revise o torneio com o organizador.')
    rodada = RodadaSuica.objects.create(torneio=torneio, numero=numero_atual + 1, folga_id=folga)
    Partida.objects.bulk_create([Partida(
        Torneios=torneio, torneio=torneio.nome, rodada=rodada.numero, rodada_suica=rodada,
        jogador_branca_id=a, jogador_preta_id=b,
        usuario_branca=jogadores[a]['usuario'].nome, usuario_preta=jogadores[b]['usuario'].nome,
        vencedor='', data_partida=data,
    ) for a, b in pares])
    return rodada


@transaction.atomic
def registrar_resultado(torneio_id, partida_id, resultado):
    torneio = bloquear_torneio(torneio_id)
    if resultado not in ('B', 'P', 'E'):
        raise ValueError('Selecione um resultado válido.')
    partida = Partida.objects.get(pk=partida_id, rodada_suica__torneio=torneio)
    if torneio.rodadas_suicas.filter(numero__gt=partida.rodada).exists():
        raise ValueError('Resultados de rodadas anteriores estão fechados para preservar os pareamentos já gerados.')
    partida.vencedor = resultado
    partida.save(update_fields=['vencedor'])
