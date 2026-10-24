from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from chess_web.forms import TorneiosForm
from chess_web.models import Torneios

@login_required
def CadastroTorneios(request):
    frm = TorneiosForm(request.POST if request.method == 'POST' else None)

    if request.method == 'POST' and frm.is_valid():
        frm.save()

        return redirect('torneios_ListaTorneios')

    return render(request, 'pages/torneios/cadastro.html', {
        'frm': frm
    })

@login_required
def ListaTorneios(request):
    return render(request, 'pages/torneios/torneios.html',{
        'torneios': Torneios.objects.all(),
        'titulo': 'Torneios cadastrados'
    })

@login_required
def EditarTorneios(request, id):
    candidato = get_object_or_404(Torneios, pk=id)
    frm = TorneiosForm(request.POST if request.method == 'POST' else None, instance=candidato)

    if request.method == 'POST' and frm.is_valid():
        frm.save()

        return redirect('torneios_ListaTorneios')

    return render(request, 'pages/torneios/cadastro.html', {
        'frm': frm,
        'titulo': 'Editar torneios'
    })

@login_required
@require_POST
def ExcluirTorneios(request, id):
    torneios = get_object_or_404(Torneios, pk=id)
    torneios.delete()
    return redirect('torneios_ListaTorneios')

@login_required
def SistemaSuico(request, id):
    from datetime import date
    from django.contrib import messages
    from chess_web.forms import InscricoesForm, GerarRodadaForm, ResultadoForm
    from chess_web.models import Partida
    from chess_web.suico import salvar_inscricoes, gerar_rodada, registrar_resultado, classificacao

    torneio = get_object_or_404(Torneios, pk=id)
    atual = torneio.rodadas_suicas.order_by('-numero').first()
    numero_atual = atual.numero if atual else 0
    inscricoes = InscricoesForm(initial={'usuarios': list(torneio.inscricoes.values_list('usuario_id', flat=True))})
    gerar = GerarRodadaForm(initial={'rodada_atual': numero_atual, 'data': date.today()})
    if request.method == 'POST':
        acao = request.POST.get('acao')
        try:
            if acao == 'inscricoes':
                inscricoes = InscricoesForm(request.POST)
                if inscricoes.is_valid():
                    salvar_inscricoes(torneio.pk, inscricoes.cleaned_data['usuarios'].values_list('pk', flat=True))
                    messages.success(request, 'Participantes salvos. A ordem inicial segue o número de cadastro no sistema.')
                    return redirect('torneios_suico', id=id)
            elif acao == 'gerar':
                gerar = GerarRodadaForm(request.POST)
                if gerar.is_valid():
                    rodada = gerar_rodada(torneio.pk, gerar.cleaned_data['data'], gerar.cleaned_data['rodada_atual'])
                    messages.success(request, f'Rodada {rodada.numero} gerada.')
                    return redirect('torneios_suico', id=id)
            elif acao == 'resultado':
                partida = get_object_or_404(Partida, pk=request.POST.get('partida'), rodada_suica__torneio=torneio)
                frm = ResultadoForm(request.POST)
                if frm.is_valid():
                    registrar_resultado(torneio.pk, partida.pk, frm.cleaned_data['resultado'])
                    messages.success(request, 'Resultado salvo. A classificação foi atualizada.')
                    return redirect('torneios_suico', id=id)
                messages.error(request, 'Selecione vitória das brancas, vitória das pretas ou empate.')
            else:
                messages.error(request, 'Ação inválida.')
        except ValueError as erro:
            messages.error(request, str(erro))
    rodadas = torneio.rodadas_suicas.select_related('folga').prefetch_related('partidas').order_by('-numero')
    jogadores = classificacao(torneio)
    limite = min(torneio.numero_rodadas, len(jogadores) - 1 if len(jogadores) % 2 == 0 else len(jogadores)) if jogadores else 0
    pendente = atual and atual.partidas.exclude(vencedor__in=['B', 'P', 'E']).exists()
    return render(request, 'pages/torneios/suico.html', {
        'torneio': torneio, 'inscricoes': inscricoes, 'gerar': gerar,
        'rodadas': rodadas, 'classificacao': jogadores, 'rodada_atual': numero_atual,
        'limite': limite, 'pode_gerar': len(jogadores) >= 2 and numero_atual < limite and not pendente,
        'pendente': pendente,
    })
