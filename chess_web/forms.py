from django.forms import ModelForm
from chess_web.models import Usuario, Torneios, Partida
from django import forms
from django.contrib.auth.password_validation import validate_password

class CadastroForm(ModelForm):
    password = forms.CharField(label='Senha', required=False, strip=False, widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'password', 'admin', 'descricao', 'instagram', 'facebook', 'twitter']
        widgets = {'descricao': forms.Textarea(attrs={'rows': 3})}
        labels = {'descricao': 'Descrição', 'admin': 'Administrador'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.senha_original = self.instance.password
        self.fields['password'].required = not self.instance.pk
        self.initial['password'] = ''

    def clean_email(self):
        return Usuario.objects.normalize_email(self.cleaned_data['email'])

    def _post_clean(self):
        super()._post_clean()
        password = self.cleaned_data.get('password')
        if password:
            try:
                validate_password(password, self.instance)
            except forms.ValidationError as erro:
                self.add_error('password', erro)

    def clean_admin(self):
        admin = self.cleaned_data['admin']
        if self.instance.pk and not admin:
            if Usuario.objects.filter(pk=self.instance.pk, admin=True).exists() and not Usuario.objects.filter(admin=True).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Não é possível retirar o privilégio do último administrador.')
        return admin

    def save(self, commit=True):
        usuario = super().save(commit=False)
        if self.cleaned_data.get('password'):
            usuario.set_password(self.cleaned_data['password'])
        else:
            usuario.password = self.senha_original
        if commit:
            usuario.save()
        return usuario

class PerfilForm(CadastroForm):
    class Meta(CadastroForm.Meta):
        fields = ['nome', 'email', 'password', 'descricao', 'instagram', 'facebook', 'twitter']

class RegistroForm(CadastroForm):
    confirmar_senha = forms.CharField(label='Confirmar senha', strip=False, widget=forms.PasswordInput)

    class Meta(CadastroForm.Meta):
        fields = ['nome', 'email', 'password']

    def clean(self):
        dados = super().clean()
        if dados.get('password') != dados.get('confirmar_senha'):
            self.add_error('confirmar_senha', 'As senhas não conferem.')
        return dados

class TorneiosForm(ModelForm):
    numero_rodadas = forms.IntegerField(label='Número de rodadas suíças', min_value=1, max_value=30, initial=5, required=False)

    def clean_numero_rodadas(self):
        valor = self.cleaned_data.get('numero_rodadas') or 5
        if self.instance.pk and self.instance.rodadas_suicas.exists() and valor != self.instance.numero_rodadas:
            raise forms.ValidationError('O número de rodadas não pode mudar após o início.')
        return valor

    class Meta:
        model = Torneios
        fields = '__all__'
        labels = {'organizacao': 'Organização', 'premio_primeiro': '1º prêmio', 'premio_segundo': '2º prêmio', 'premio_terceiro': '3º prêmio'}

class PartidaForm(ModelForm):
    def clean_Torneios(self):
        torneio = self.cleaned_data['Torneios']
        if torneio.rodadas_suicas.exists():
            raise forms.ValidationError('Use a página do sistema suíço para registrar resultados deste torneio.')
        return torneio

    class Meta:
        model = Partida
        fields = ['usuario_branca', 'usuario_preta', 'torneio', 'vencedor', 'data_partida', 'rodada', 'Torneios']
        labels = {'usuario_branca': 'Usuário das peças brancas', 'usuario_preta': 'Usuário das peças pretas', 'Torneios': 'Torneio vinculado'}
        widgets = {'data_partida': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')}


class InscricoesForm(forms.Form):
    usuarios = forms.ModelMultipleChoiceField(label='Participantes', queryset=Usuario.objects.order_by('nome', 'pk'), widget=forms.CheckboxSelectMultiple)

    def clean_usuarios(self):
        usuarios = self.cleaned_data['usuarios']
        if usuarios.count() < 2:
            raise forms.ValidationError('Selecione pelo menos dois participantes.')
        return usuarios

class GerarRodadaForm(forms.Form):
    rodada_atual = forms.IntegerField(min_value=0, widget=forms.HiddenInput)
    data = forms.DateField(label='Data das partidas', widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))

class ResultadoForm(forms.Form):
    resultado = forms.ChoiceField(label='Resultado', choices=[('', 'Selecione'), ('B', 'Vitória das brancas'), ('P', 'Vitória das pretas'), ('E', 'Empate')])
