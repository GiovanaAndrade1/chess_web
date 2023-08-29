from django.db import models
from django.contrib.auth.models import AbstractBaseUser

class Usuario(AbstractBaseUser):
    '''
    Usuário registrado no sistema
    '''

    nome = models.CharField(max_length=1000)
    email = models.EmailField(max_length=1000, unique=True)
    admin = models.BooleanField('Adminsitrador', default=False)
    senha = models.CharField(max_length= 1000)
    descricao = models.CharField(max_length= 2000, blank=True)
    instagram = models.CharField(max_length=1000, blank=True)
    facebook = models.CharField(max_length=1000, blank=True)
    twitter = models.CharField(max_length=1000, blank=True)
    #partidas = models.OneToManyField("Partida")

    USERNAME_FIELD = 'email'

    @property
    def senha(self):
        return self.password
    
    @property
    def ultimo_acesso(self):
        return self.last_login
    
class Torneios(models.Model):
    nome = models.CharField(max_length=200)
    local = models.CharField(max_length=500)
    data = models.CharField(max_length=10, null=False) 
    organizacao = models.CharField(max_length=100)
    premio_primeiro = models.CharField(max_length=100, default=0)
    premio_segundo = models.CharField(max_length=100, default=0)
    premio_terceiro = models.CharField(max_length=100, default=0)
    #partidas = models.OneToManyField("Partida")

class Partida(models.Model):
    usuario_branca = models.CharField(max_length=1000) # nome(Usuário)
    usuario_preta   = models.CharField(max_length=1000) #  nome(Usuário)
    torneio = models.CharField(max_length=1000) #  nome(Torneio)
    vencedor = models.CharField(max_length=1)
    data_partida =  models.DateField()
    rodada =  models.IntegerField() 
    Torneios = models.ForeignKey ('Torneios', on_delete=models.deletion.CASCADE)
    