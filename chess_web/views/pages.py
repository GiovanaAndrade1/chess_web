from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from chess_web.models import Usuario, Torneios, Partida
from chess_web.views.usuario import Usuario_perfil

@login_required
def dashboard(request):
    return render(request, 'pages/dashboard.html', {
        'total_usuarios': Usuario.objects.count(),
        'total_torneios': Torneios.objects.count(),
        'total_partidas': Partida.objects.count(),
        'partidas': Partida.objects.order_by('-data_partida', '-pk')[:5],
    })

@login_required
def perfil(request):
    return Usuario_perfil(request, request.user.pk)
