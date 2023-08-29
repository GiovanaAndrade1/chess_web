from django.shortcuts import render, redirect, get_object_or_404
from chess_web.forms import TorneiosForm
from chess_web.models import Torneios

def CadastroTorneios(request):
    frm = TorneiosForm(request.POST or None)

    if frm.is_valid():
        frm.save()

        return redirect('torneios_ListaTorneios')

    return render(request, 'pages/torneios/cadastro.html', {
        'frm': frm
    })

def ListaTorneios(request):
    return render(request, 'pages/torneios/torneios.html',{
        'torneios': Torneios.objects.all(),
        'titulo': 'Torneios cadastrados'
    })

def EditarTorneios(request, id):
    candidato = get_object_or_404(Torneios, pk=id)
    frm = TorneiosForm(request.POST or None, instance=candidato)

    if frm.is_valid():
        frm.save()

        return redirect('torneios_ListaTorneios')

    return render(request, 'pages/torneios/cadastro.html', {
        'frm': frm,
        'titulo': 'Editar torneios'
    })

def ExcluirTorneios(request, id):
    torneios = get_object_or_404(Torneios, pk=id)
    torneios.delete()
    return redirect('torneios_ListaTorneios')