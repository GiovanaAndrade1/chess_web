from django.contrib import admin
from django.urls import path
from chess_web.views import pages, torneios, usuario, partida
#from chess_web import usuario

urlpatterns = [
    path('dashboard', pages.dashboard, name='dashboard'), 
    # Torneios
    path('torneios', torneios.ListaTorneios, name ="torneios_ListaTorneios"),
    path('torneios/adicionarTorneios', torneios.CadastroTorneios, name='torneios_adicionarTorneios'),
    path('torneios/EditarTorneios/<id>', torneios.EditarTorneios, name='torneios_EditarTorneios'),
    path('torneios/ExcluirTorneios/<id>', torneios.ExcluirTorneios, name="torneios_ExcluirTorneios"),
    # Usuários
    path('usuarios', usuario.lista, name = "usuarios_lista"),
    path('usuarios/adicionar', usuario.CadastroUsuario, name= 'usuarios_adicionar'),
    path('usuarios/editar/<id>', usuario.editar, name='usuarios_editar'),
    path('usuarios/excluir/<id>', usuario.excluir, name="usuarios_excluir"),
    path('usuarios/biousuario/<id>', usuario.biousuario, name= "bio_usuario"),
    path('usuarios/perfil/<id>', usuario.Usuario_perfil, name= "usuarios_perfil"),
    #Partida
    path('partida', partida.ListaPartida, name ="partida_ListaPartida"),
    path('partida/adicionarPartida', partida.CadastroPartida, name='partida_adicionarPartida'),
    path('partida/EditarPartida/<id>', partida.EditarPartida, name='partida_EditarPartida'),
    path('partida/ExcluirPartida/<id>', partida.ExcluirPartida, name="partida_ExcluirPartida"),
]

