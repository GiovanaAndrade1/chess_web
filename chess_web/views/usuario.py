from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, login
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.db import transaction
from chess_web.forms import CadastroForm, PerfilForm, RegistroForm
from chess_web.models import Usuario

@login_required
def CadastroUsuario(request):
    if not request.user.admin:
        return HttpResponseForbidden('Somente administradores gerenciam usuários.')
    frm = CadastroForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and frm.is_valid():
        frm.save()
        return redirect('usuarios_lista')
    return render(request, 'pages/usuarios/cadastro.html', {'frm': frm, 'titulo': 'Cadastrar usuário'})

@login_required
def lista(request):
    if not request.user.admin:
        return HttpResponseForbidden('Somente administradores gerenciam usuários.')
    return render(request, 'pages/usuarios/usuarios.html', {'usuarios': Usuario.objects.all(), 'titulo': 'Usuários cadastrados'})

@login_required
def editar(request, id):
    if not request.user.admin and str(request.user.pk) != str(id):
        return HttpResponseForbidden('Você pode editar somente o próprio perfil.')
    with transaction.atomic():
        # Serializa mudanças administrativas para proteger o último administrador.
        list(Usuario.objects.select_for_update().filter(admin=True).order_by('pk'))
        candidato = get_object_or_404(Usuario, pk=id)
        Formulario = CadastroForm if request.user.admin else PerfilForm
        frm = Formulario(request.POST if request.method == 'POST' else None, instance=candidato)
        if request.method == 'POST' and frm.is_valid():
            usuario = frm.save()
            if usuario.pk == request.user.pk:
                update_session_auth_hash(request, usuario)
            return redirect('usuarios_perfil', id=usuario.pk)
    return render(request, 'pages/usuarios/cadastro.html', {'frm': frm, 'titulo': 'Editar usuário'})

@login_required
@require_POST
def excluir(request, id):
    if not request.user.admin:
        return HttpResponseForbidden('Somente administradores gerenciam usuários.')
    with transaction.atomic():
        list(Usuario.objects.select_for_update().filter(admin=True).order_by('pk'))
        candidato = get_object_or_404(Usuario, pk=id)
        if candidato.pk == request.user.pk or (candidato.admin and Usuario.objects.filter(admin=True).count() <= 1):
            return HttpResponseForbidden('Não é possível excluir seu usuário ou o último administrador.')
        from django.db.models.deletion import ProtectedError
        try:
            candidato.delete()
        except ProtectedError:
            return HttpResponseForbidden('Este usuário participa de torneios suíços e seu histórico precisa ser preservado.')
    return redirect('usuarios_lista')

@login_required
def biousuario(request, id):
    return editar(request, id)

@login_required
def Usuario_perfil(request, id):
    if not request.user.admin and str(request.user.pk) != str(id):
        return HttpResponseForbidden('Você pode consultar somente o próprio perfil.')
    usuario = get_object_or_404(Usuario, pk=id)
    return render(request, 'pages/usuarios/usuario_perfil.html', {'usuario': usuario})


def registro(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    frm = RegistroForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and frm.is_valid():
        usuario = frm.save(commit=False)
        usuario.admin = False
        usuario.save()
        login(request, usuario)
        return redirect('inicio')
    return render(request, 'pages/usuarios/registro.html', {'frm': frm})
