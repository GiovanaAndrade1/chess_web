from django.forms import ModelForm
from chess_web.models import Usuario, Torneios, Partida
from django import forms

class CadastroForm(ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'instagram': forms.TextInput(attrs={'placeholder': 'https://instagram.com/seu_perfil'}),
            'facebook': forms.TextInput(attrs={'placeholder': 'https://facebook.com/seu_perfil'}),
            'twitter': forms.TextInput(attrs={'placeholder': 'https://twitter.com/seu_perfil'}),
        }

class TorneiosForm(ModelForm):
    class Meta:
        model = Torneios
        fields = '__all__'


class PartidaForm(ModelForm):
    class Meta:
        model = Partida
        fields = '__all__'
