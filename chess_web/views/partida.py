from django.shortcuts import render, redirect, get_object_or_404
from chess_web.forms import PartidaForm
from chess_web.models import Partida

def CadastroPartida(request):
    frm = PartidaForm(request.POST or None)

    if frm.is_valid():
        frm.save()

        return redirect('partida_ListaPartida')

    return render(request, 'pages/partida/cadastro.html', {
        'frm': frm
    })

def ListaPartida(request):
    return render(request, 'pages/partida/partida.html',{
        'partida': Partida.objects.all(),
        'titulo': 'Partidas cadastradas'
    })

def EditarPartida(request, id):
    candidato = get_object_or_404(Partida, pk=id)
    frm = PartidaForm(request.POST or None, instance=candidato)

    if frm.is_valid():
        frm.save()

        return redirect('partida_ListaPartida')

    return render(request, 'pages/partida/cadastro.html', {
        'frm': frm,
        'titulo': 'Editar partidas'
    })

def ExcluirPartida(request, id):
    partida = get_object_or_404(Partida, pk=id)
    partida.delete()
    return redirect('partida_ListaPartida')