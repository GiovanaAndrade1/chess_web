from django.shortcuts import render, redirect, get_object_or_404
from chess_web.forms import CadastroForm
from chess_web.models import Usuario 
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse

def CadastroUsuario(request):
    frm = CadastroForm(request.POST or None)

    if frm.is_valid():
        # Obter a senha do formulário
        password = frm.cleaned_data.get('password')

        # Criptografar a senha
        senha_criptografada = make_password(password)

        # Salvar o usuário com a senha criptografada
        usuario = frm.save(commit=False)
        usuario.password = senha_criptografada
        usuario.save()

        return redirect('usuarios_lista')

    return render(request, 'pages/usuarios/cadastro.html', {
        'frm': frm,
        'titulo': 'Cadastrar usuário'
    })

def lista(request):
    return render(request, 'pages/usuarios/usuarios.html',{
        'usuarios': Usuario.objects.all(),
        'titulo': 'Usuários cadastrados'
    })

def editar(request, id):
    candidato = get_object_or_404(Usuario, pk=id)
    frm = CadastroForm(request.POST or None, instance=candidato)

    if frm.is_valid():
        # Obter a senha do formulário
        password = frm.cleaned_data.get('password')

        # Criptografar a senha
        senha_criptografada = make_password(password)

        # Salvar o usuário com a senha criptografada
        usuario = frm.save(commit=False)
        usuario.password = senha_criptografada
        usuario.save()

        return redirect('usuarios_lista')

    return render(request, 'pages/usuarios/cadastro.html', {
        'frm': frm,
        'titulo': 'Editar usuários'
    })

def excluir(request, id):
    candidato = get_object_or_404(Usuario, pk=id)
    if candidato.id == 1:
        return HttpResponse('Não é possível excluir este usuário.')
    else:
        candidato.delete()
        return redirect('usuarios_lista')

def biousuario(request, id):
    candidato = get_object_or_404(Usuario, pk=id)
    frm = CadastroForm(request.POST or None, instance=candidato)

    if frm.is_valid():
        frm.save()
        return redirect('usuarios_lista')

    return render(request, 'pages/usuarios/cadastro.html', {
        'frm': frm,
    })
    
def Usuario_perfil(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    return render(request, 'pages/usuarios/usuario_perfil.html', {
        'usuario': usuario,
    })