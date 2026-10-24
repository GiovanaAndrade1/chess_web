from importlib import import_module
from django.test import TestCase, TransactionTestCase, Client, override_settings
from django.urls import reverse
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from chess_web.models import Usuario, Torneios, Partida
from chess_web.forms import CadastroForm, PerfilForm

SENHA = 'Xadrez!Teste42Segura'

class FluxosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = Usuario.objects.create_superuser('admin@example.com', SENHA, nome='Administradora')
        cls.comum = Usuario.objects.create_user('jogador@example.com', SENHA, nome='Jogadora')

    def test_acentos_em_cadastros_e_paginas(self):
        nome = 'João da Conceição'
        senha = 'Ação!Xadrez42Segura'
        self.client.post(reverse('registro'), {'nome': nome, 'email': 'acentos@example.com', 'password': senha, 'confirmar_senha': senha})
        usuario = Usuario.objects.get(email='acentos@example.com')
        self.assertEqual(usuario.nome, nome)
        self.assertTrue(usuario.check_password(senha))
        self.client.post(reverse('usuarios_editar', args=[usuario.pk]), {'nome': nome, 'email': usuario.email, 'password': '', 'descricao': 'São João: ação, coração e estratégia.'})
        usuario.refresh_from_db()
        self.assertEqual(usuario.descricao, 'São João: ação, coração e estratégia.')
        resposta = self.client.get(reverse('perfil'))
        self.assertContains(resposta, nome)
        self.assertContains(resposta, 'Perfil do Usuário')
        self.assertContains(resposta, 'Descrição')
        self.assertContains(resposta, usuario.descricao)
        self.assertIn('charset=utf-8', resposta['Content-Type'])
        self.assertNotContains(resposta, 'Ã')
        self.assertContains(self.client.get(reverse('usuarios_editar', args=[usuario.pk])), 'Descrição')
        self.assertContains(self.client.get(reverse('torneios_adicionarTorneios')), 'Organização')
        torneio = Torneios.objects.create(nome='Torneio São João', local='Açucena', data='23/10/2026', organizacao='Associação')
        torneio.refresh_from_db()
        self.assertContains(self.client.get(reverse('torneios_ListaTorneios')), torneio.nome)
        self.assertContains(self.client.get(reverse('torneios_ListaTorneios')), 'Associação')

    def test_registro_publico(self):
        self.assertContains(self.client.get(reverse('login')), 'Criar conta')
        self.assertEqual(self.client.get(reverse('registro')).status_code, 200)
        dados = {'nome': 'Visitante', 'email': 'visitante@example.com', 'password': SENHA, 'confirmar_senha': SENHA, 'admin': True}
        self.assertRedirects(self.client.post(reverse('registro'), dados), '/')
        usuario = Usuario.objects.get(email=dados['email'])
        self.assertFalse(usuario.admin)
        self.assertTrue(usuario.check_password(SENHA))
        self.assertEqual(int(self.client.session['_auth_user_id']), usuario.pk)
        self.assertEqual(self.client.get(reverse('torneios_adicionarTorneios')).status_code, 200)
        self.assertEqual(self.client.get(reverse('usuarios_lista')).status_code, 403)
        self.assertRedirects(self.client.get(reverse('registro')), '/')
        self.client.logout()
        self.assertContains(self.client.post(reverse('registro'), dados), 'já existe')
        dados['email'] = 'outra@example.com'
        dados['confirmar_senha'] = 'diferente'
        self.assertContains(self.client.post(reverse('registro'), dados), 'As senhas não conferem.')
        dados['password'] = dados['confirmar_senha'] = '123'
        resposta = self.client.post(reverse('registro'), dados)
        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(Usuario.objects.filter(email=dados['email']).exists())
        cliente = Client(enforce_csrf_checks=True)
        self.assertEqual(cliente.post(reverse('registro'), dados).status_code, 403)

    def test_login_dashboard_perfil_logout(self):
        self.assertRedirects(self.client.get('/'), reverse('login') + '?next=/')
        self.assertRedirects(self.client.post(reverse('login'), {'username': self.admin.email, 'password': SENHA}), '/')
        self.assertContains(self.client.get('/'), 'Últimas partidas')
        self.assertContains(self.client.get(reverse('perfil')), 'Administradora')
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        self.assertRedirects(self.client.post(reverse('logout')), reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_senhas_e_manager(self):
        frm = CadastroForm(data={'nome': 'Nova', 'email': 'nova@EXAMPLE.COM', 'password': SENHA})
        self.assertTrue(frm.is_valid(), frm.errors)
        usuario = frm.save()
        self.assertEqual(usuario.email, 'nova@example.com')
        self.assertTrue(usuario.check_password(SENHA))
        anterior = usuario.password
        frm = CadastroForm(data={'nome': 'Editada', 'email': usuario.email, 'password': ''}, instance=usuario)
        self.assertTrue(frm.is_valid(), frm.errors)
        self.assertEqual(frm.save().password, anterior)
        frm = PerfilForm(data={'nome': 'Editada', 'email': usuario.email, 'password': '123', 'admin': True}, instance=usuario)
        self.assertFalse(frm.is_valid())
        self.assertNotIn('admin', frm.fields)
        self.assertNotIn('last_login', frm.fields)
        self.assertEqual(Usuario.REQUIRED_FIELDS, ['nome'])

    def test_permissoes_e_sessao(self):
        self.client.force_login(self.comum)
        for nome in ['usuarios_lista', 'usuarios_adicionar']:
            self.assertEqual(self.client.get(reverse(nome)).status_code, 403)
        for nome in ['usuarios_editar', 'bio_usuario', 'usuarios_perfil']:
            self.assertEqual(self.client.get(reverse(nome, args=[self.admin.pk])).status_code, 403)
        self.client.post(reverse('usuarios_editar', args=[self.comum.pk]), {'nome': 'Jogadora', 'email': self.comum.email, 'password': SENHA + 'Nova', 'admin': True})
        self.comum.refresh_from_db()
        self.assertFalse(self.comum.admin)
        self.assertTrue(self.comum.check_password(SENHA + 'Nova'))
        self.assertEqual(self.client.get('/').status_code, 200)
        self.client.force_login(self.admin)
        self.assertEqual(self.client.post(reverse('usuarios_excluir', args=[self.admin.pk])).status_code, 403)
        resposta = self.client.post(reverse('usuarios_editar', args=[self.admin.pk]), {'nome': self.admin.nome, 'email': self.admin.email, 'password': ''})
        self.assertContains(resposta, 'último administrador')
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.admin)
        resposta = self.client.post(reverse('usuarios_adicionar'), {'nome': 'Terceira', 'email': 'terceira@example.com', 'password': SENHA})
        self.assertEqual(resposta.status_code, 302)
        nova = Usuario.objects.get(email='terceira@example.com')
        self.assertTrue(nova.check_password(SENHA))
        self.assertEqual(self.client.get(reverse('usuarios_excluir', args=[nova.pk])).status_code, 405)
        self.assertEqual(self.client.post(reverse('usuarios_excluir', args=[nova.pk])).status_code, 302)

    def test_torneios_partidas_e_exclusao_post(self):
        self.client.force_login(self.comum)
        dados = {'nome': 'Aberto', 'local': 'IFMG', 'data': '23/10/2026', 'organizacao': 'Clube', 'premio_primeiro': '100', 'premio_segundo': '50', 'premio_terceiro': '25'}
        self.assertRedirects(self.client.post(reverse('torneios_adicionarTorneios'), dados), reverse('torneios_ListaTorneios'))
        torneio = Torneios.objects.get()
        dados_partida = {'usuario_branca': 'Ana', 'usuario_preta': 'Bia', 'torneio': 'Aberto', 'Torneios': torneio.pk, 'vencedor': 'B', 'data_partida': '2026-10-23', 'rodada': 1}
        self.assertRedirects(self.client.post(reverse('partida_adicionarPartida'), dados_partida), reverse('partida_ListaPartida'))
        partida = Partida.objects.get()
        for rota in ['torneios_ListaTorneios', 'partida_ListaPartida']:
            self.assertEqual(self.client.get(reverse(rota)).status_code, 200)
        self.assertEqual(self.client.get(reverse('torneios_EditarTorneios', args=[torneio.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse('partida_EditarPartida', args=[partida.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse('partida_ExcluirPartida', args=[partida.pk])).status_code, 405)
        self.assertEqual(self.client.get(reverse('torneios_ExcluirTorneios', args=[torneio.pk])).status_code, 405)
        self.assertEqual(self.client.post(reverse('partida_ExcluirPartida', args=[partida.pk])).status_code, 302)
        self.assertEqual(self.client.post(reverse('torneios_ExcluirTorneios', args=[torneio.pk])).status_code, 302)
        self.assertFalse(Partida.objects.exists())
        self.assertFalse(Torneios.objects.exists())

    def test_csrf(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.admin)
        torneio = Torneios.objects.create(nome='Aberto', local='IFMG', data='2026-10-23', organizacao='Clube')
        partida = Partida.objects.create(usuario_branca='Ana', usuario_preta='Bia', torneio='Aberto', Torneios=torneio, vencedor='B', data_partida='2026-10-23', rodada=1)
        for rota, pk in [('usuarios_excluir', self.comum.pk), ('torneios_ExcluirTorneios', torneio.pk), ('partida_ExcluirPartida', partida.pk)]:
            self.assertEqual(cliente.post(reverse(rota, args=[pk])).status_code, 403)
        self.assertTrue(Usuario.objects.filter(pk=self.comum.pk).exists())
        self.assertTrue(Torneios.objects.exists())
        self.assertTrue(Partida.objects.exists())

class MigracoesTests(TransactionTestCase):
    def test_perfil_antigo_com_null(self):
        anterior = [('chess_web', '0009_torneios_premio_primeiro_torneios_premio_segundo_and_more')]
        executor = MigrationExecutor(connection)
        final = executor.loader.graph.leaf_nodes()
        try:
            executor.migrate(anterior)
            apps = executor.loader.project_state(anterior).apps
            Antigo = apps.get_model('chess_web', 'Usuario')
            usuario = Antigo.objects.create(nome='Legado', email='legado@example.com', password='hash-preservado', admin=False, descricao=None, facebook=None, instagram=None, twitter=None)
            executor = MigrationExecutor(connection)
            executor.migrate(final)
            Atual = executor.loader.project_state(final).apps.get_model('chess_web', 'Usuario')
            usuario = Atual.objects.get(pk=usuario.pk)
            for campo in ['descricao', 'facebook', 'instagram', 'twitter']:
                self.assertEqual(getattr(usuario, campo), '')
            self.assertEqual(usuario.password, 'hash-preservado')
        finally:
            MigrationExecutor(connection).migrate(final)

    def test_email_longo_interrompe_migracao(self):
        verificar = import_module('chess_web.migrations.0013_alter_usuario_email').verificar_emails
        from django.apps import apps
        from types import SimpleNamespace
        Usuario.objects.create(nome='Legado', email='a' * 245 + '@example.com')
        with self.assertRaisesMessage(RuntimeError, 'maiores que 254'):
            verificar(apps, SimpleNamespace(connection=connection))


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class TrintaUsuariosTests(TestCase):
    def test_trinta_cadastros_e_quinze_partidas_manuais(self):
        for numero in range(1, 31):
            self.client.logout()
            resposta = self.client.post(reverse('registro'), {
                'nome': f'Jogador {numero:02d}',
                'email': f'jogador{numero:02d}@example.com',
                'password': SENHA,
                'confirmar_senha': SENHA,
            })
            self.assertEqual(resposta.status_code, 302)
        self.assertEqual(Usuario.objects.count(), 30)
        self.assertEqual(Usuario.objects.filter(admin=True).count(), 0)
        self.assertEqual(Partida.objects.count(), 0)
        torneio = Torneios.objects.create(nome='Teste 30 jogadores', local='São João', data='23/10/2026', organizacao='Associação')
        self.assertEqual(Partida.objects.count(), 0)
        jogadores = list(Usuario.objects.order_by('email'))
        for indice in range(0, 30, 2):
            resposta = self.client.post(reverse('partida_adicionarPartida'), {
                'usuario_branca': jogadores[indice].nome,
                'usuario_preta': jogadores[indice + 1].nome,
                'torneio': torneio.nome,
                'Torneios': torneio.pk,
                'vencedor': 'B',
                'data_partida': '2026-10-23',
                'rodada': 1,
            })
            self.assertEqual(resposta.status_code, 302)
        partidas = Partida.objects.filter(Torneios=torneio, rodada=1)
        self.assertEqual(partidas.count(), 15)
        nomes = [nome for partida in partidas for nome in (partida.usuario_branca, partida.usuario_preta)]
        self.assertEqual(len(set(nomes)), 30)
        self.assertEqual(set(nomes), {jogador.nome for jogador in jogadores})
        self.assertFalse(Partida.objects.filter(rodada=2).exists())
        self.assertContains(self.client.get(reverse('partida_ListaPartida')), 'Jogador 30')
