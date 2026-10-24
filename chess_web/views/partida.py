from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from chess_web.forms import PartidaForm
from chess_web.models import Partida

@login_required
def CadastroPartida(request):
    frm = PartidaForm(request.POST if request.method == 'POST' else None)

    if request.method == 'POST' and frm.is_valid():
        frm.save()

        return redirect('partida_ListaPartida')

    return render(request, 'pages/partida/cadastro.html', {
        'frm': frm
    })

@login_required
def ListaPartida(request):
    return render(request, 'pages/partida/partida.html',{
        'partida': Partida.objects.all(),
        'titulo': 'Partidas cadastradas'
    })

@login_required
def EditarPartida(request, id):
    candidato = get_object_or_404(Partida, pk=id)
    if candidato.rodada_suica_id:
        return redirect('torneios_suico', id=candidato.Torneios_id)
    frm = PartidaForm(request.POST if request.method == 'POST' else None, instance=candidato)

    if request.method == 'POST' and frm.is_valid():
        frm.save()

        return redirect('partida_ListaPartida')

    return render(request, 'pages/partida/cadastro.html', {
        'frm': frm,
        'titulo': 'Editar partidas'
    })

@login_required
@require_POST
def ExcluirPartida(request, id):
    partida = get_object_or_404(Partida, pk=id)
    if partida.rodada_suica_id:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden('Partidas suíças não podem ser excluídas individualmente. Registre o resultado na página do torneio.')
    partida.delete()
    return redirect('partida_ListaPartida')