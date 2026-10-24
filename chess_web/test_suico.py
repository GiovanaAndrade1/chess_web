from datetime import date
from collections import Counter
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from chess_web.models import Usuario, Torneios, Partida, Inscricao, RodadaSuica
from chess_web.suico import gerar_rodada, salvar_inscricoes, registrar_resultado, classificacao, estado, combinar


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class SistemaSuicoTests(TestCase):
    def preparar(self, quantidade=30, rodadas=5):
        usuarios = [Usuario.objects.create_user(f'p{n}@example.com', 'Xadrez!Teste42Segura', nome=f'Jogador {n:02d}') for n in range(quantidade)]
        torneio = Torneios.objects.create(nome='Suíço São João', local='Clube', data='23/10/2026', organizacao='Associação', numero_rodadas=rodadas)
        salvar_inscricoes(torneio.pk, [u.pk for u in usuarios])
        return torneio, usuarios

    def concluir(self, torneio, rodada, resultados=None):
        for n, partida in enumerate(rodada.partidas.order_by('pk')):
            registrar_resultado(torneio.pk, partida.pk, resultados[n % len(resultados)] if resultados else 'B')

    def test_trinta_jogadores_cinco_rodadas(self):
        torneio, usuarios = self.preparar()
        pares_vistos, cores = set(), {u.pk: [] for u in usuarios}
        pontos_esperados = Counter()
        for numero in range(1, 6):
            rodada = gerar_rodada(torneio.pk, date(2026, 10, 23), numero - 1)
            self.assertEqual(rodada.partidas.count(), 15)
            self.assertIsNone(rodada.folga_id)
            presencas = []
            for n, partida in enumerate(rodada.partidas.order_by('pk')):
                a, b = partida.jogador_branca_id, partida.jogador_preta_id
                par = frozenset([a, b])
                self.assertNotIn(par, pares_vistos)
                pares_vistos.add(par)
                presencas.extend([a, b])
                for id, cor in [(a, 'B'), (b, 'P')]:
                    cores[id].append(cor)
                    self.assertLessEqual(abs(cores[id].count('B') - cores[id].count('P')), 2)
                    self.assertNotEqual(cores[id][-3:], ['B'] * 3)
                    self.assertNotEqual(cores[id][-3:], ['P'] * 3)
                resultado = ['B', 'P', 'E'][(n + numero) % 3]
                registrar_resultado(torneio.pk, partida.pk, resultado)
                pontos_esperados[a] += {'B': 2, 'P': 0, 'E': 1}[resultado]
                pontos_esperados[b] += {'B': 0, 'P': 2, 'E': 1}[resultado]
            self.assertCountEqual(presencas, [u.pk for u in usuarios])
            for j in classificacao(torneio):
                self.assertEqual(j['pontos2'], pontos_esperados[j['usuario'].pk])
        self.assertEqual(len(pares_vistos), 75)
        self.assertEqual(sum(pontos_esperados.values()), 150)
        with self.assertRaisesMessage(ValueError, 'limite'):
            gerar_rodada(torneio.pk, date.today(), 5)
        self.assertEqual(RodadaSuica.objects.count(), 5)

    def test_pontuacoes_proximas_e_primeira_rodada(self):
        torneio, usuarios = self.preparar()
        primeira = gerar_rodada(torneio.pk, date.today(), 0)
        for p in primeira.partidas.all():
            self.assertEqual(abs(usuarios.index(p.jogador_branca) - usuarios.index(p.jogador_preta)), 15)
        self.concluir(torneio, primeira)
        antes = estado(torneio)
        segunda = gerar_rodada(torneio.pk, date.today(), 1)
        cruzamentos = sum(antes[p.jogador_branca_id]['pontos2'] != antes[p.jogador_preta_id]['pontos2'] for p in segunda.partidas.all())
        # Dois grupos de 15: exatamente um confronto entre grupos é inevitável.
        self.assertEqual(cruzamentos, 1)

    def test_vinte_nove_folgas_unicas_e_pontuacao(self):
        torneio, usuarios = self.preparar(29)
        folgas = set()
        for numero in range(5):
            rodada = gerar_rodada(torneio.pk, date.today(), numero)
            self.assertEqual(rodada.partidas.count(), 14)
            self.assertNotIn(rodada.folga_id, folgas)
            folgas.add(rodada.folga_id)
            self.assertNotIn(rodada.folga_id, [id for p in rodada.partidas.all() for id in [p.jogador_branca_id, p.jogador_preta_id]])
            self.concluir(torneio, rodada, ['E'])
        tabela = classificacao(torneio)
        self.assertEqual(sum(j['pontos'] for j in tabela), 75)
        self.assertEqual(sum(j['folgas'] for j in tabela), 5)
        self.assertEqual(len(folgas), 5)

    def test_pendencias_duplicacao_e_resultados_anteriores(self):
        torneio, usuarios = self.preparar(6)
        rodada = gerar_rodada(torneio.pk, date.today(), 0)
        with self.assertRaisesMessage(ValueError, 'rodada mudou'):
            gerar_rodada(torneio.pk, date.today(), 0)
        with self.assertRaisesMessage(ValueError, 'todos os resultados'):
            gerar_rodada(torneio.pk, date.today(), 1)
        with self.assertRaisesMessage(ValueError, 'inscrições ficam fechadas'):
            salvar_inscricoes(torneio.pk, [u.pk for u in usuarios[:2]])
        with self.assertRaisesMessage(ValueError, 'resultado válido'):
            registrar_resultado(torneio.pk, rodada.partidas.first().pk, 'X')
        self.concluir(torneio, rodada)
        gerar_rodada(torneio.pk, date.today(), 1)
        with self.assertRaisesMessage(ValueError, 'anteriores estão fechados'):
            registrar_resultado(torneio.pk, rodada.partidas.first().pk, 'E')
        self.assertEqual(torneio.rodadas_suicas.count(), 2)

    def test_empates_buchholz_e_ordem_estavel(self):
        torneio, usuarios = self.preparar(4)
        rodada = gerar_rodada(torneio.pk, date.today(), 0)
        self.concluir(torneio, rodada, ['E'])
        tabela = classificacao(torneio)
        self.assertEqual([j['numero'] for j in tabela], [1, 2, 3, 4])
        self.assertTrue(all(j['pontos'] == .5 and j['buchholz'] == .5 and j['vitorias'] == 0 for j in tabela))

    def test_sem_pares_validos_nao_relaxa_regras(self):
        jogadores = {i: {'numero': i, 'pontos2': 0, 'cores': [], 'adversarios': {1, 2, 3, 4} - {i}} for i in range(1, 5)}
        self.assertIsNone(combinar(list(jogadores), jogadores))
        jogadores = {i: {'numero': i, 'pontos2': 0, 'cores': ['B', 'B'], 'adversarios': set()} for i in range(1, 5)}
        self.assertIsNone(combinar(list(jogadores), jogadores))

    def test_preserva_partidas_manuais(self):
        torneio, usuarios = self.preparar(4)
        p = Partida.objects.create(Torneios=torneio, torneio=torneio.nome, usuario_branca='Nome legado', usuario_preta='Outro legado', vencedor='B', rodada=1, data_partida=date.today())
        with self.assertRaisesMessage(ValueError, 'partidas manuais'):
            gerar_rodada(torneio.pk, date.today(), 0)
        self.assertTrue(Partida.objects.filter(pk=p.pk).exists())
        self.assertFalse(torneio.rodadas_suicas.exists())

    def test_fluxo_web_csrf_e_bloqueio_das_rotas_manuais(self):
        torneio, usuarios = self.preparar(4)
        url = reverse('torneios_suico', args=[torneio.pk])
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(usuarios[0])
        self.assertContains(self.client.get(url), 'Participantes')
        resposta = self.client.post(url, {'acao': 'inscricoes', 'usuarios': [u.pk for u in usuarios]})
        self.assertRedirects(resposta, url)
        resposta = self.client.post(url, {'acao': 'gerar', 'rodada_atual': 0, 'data': '2026-10-23'})
        self.assertRedirects(resposta, url)
        self.assertContains(self.client.get(url), 'Rodada 1')
        self.assertContains(self.client.get(url), 'Pendente')
        partida = Partida.objects.filter(Torneios=torneio).first()
        self.assertRedirects(self.client.get(reverse('partida_EditarPartida', args=[partida.pk])), url)
        self.assertEqual(self.client.post(reverse('partida_ExcluirPartida', args=[partida.pk])).status_code, 403)
        self.assertRedirects(self.client.post(url, {'acao': 'resultado', 'partida': partida.pk, 'resultado': 'E'}), url)
        partida.refresh_from_db()
        self.assertEqual(partida.vencedor, 'E')
        resposta = self.client.post(reverse('partida_adicionarPartida'), {'Torneios': torneio.pk})
        self.assertContains(resposta, 'Use a página do sistema suíço')
        self.assertEqual(Partida.objects.filter(Torneios=torneio).count(), 2)
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(usuarios[0])
        self.assertEqual(cliente.post(url, {'acao': 'gerar', 'rodada_atual': 1, 'data': '2026-10-23'}).status_code, 403)
        self.assertEqual(cliente.post(url, {'acao': 'inscricoes', 'usuarios': [u.pk for u in usuarios]}).status_code, 403)
        self.assertEqual(cliente.post(url, {'acao': 'resultado', 'partida': partida.pk, 'resultado': 'B'}).status_code, 403)
