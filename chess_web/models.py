from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Informe o email.")
        usuario = self.model(email=self.normalize_email(email), **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("admin", True)
        if extra_fields["admin"] is not True:
            raise ValueError("O superusuário precisa ser administrador.")
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser):
    '''
    Usuário registrado no sistema
    '''

    nome = models.CharField(max_length=1000)
    email = models.EmailField(max_length=254, unique=True)
    admin = models.BooleanField('Adminsitrador', default=False)
    descricao = models.CharField(max_length= 2000, blank=True)
    instagram = models.CharField(max_length=1000, blank=True)
    facebook = models.CharField(max_length=1000, blank=True)
    twitter = models.CharField(max_length=1000, blank=True)
    #partidas = models.OneToManyField("Partida")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']
    objects = UsuarioManager()

    def __str__(self):
        return self.nome

    @property
    def is_staff(self):
        return self.admin

    @property
    def is_superuser(self):
        return self.admin

    def has_perm(self, perm, obj=None):
        return self.admin

    def has_module_perms(self, app_label):
        return self.admin

    @property
    def senha(self):
        return self.password

    @property
    def ultimo_acesso(self):
        return self.last_login

class Torneios(models.Model):
    def __str__(self):
        return self.nome

    nome = models.CharField(max_length=200)
    local = models.CharField(max_length=500)
    data = models.CharField(max_length=10, null=False)
    organizacao = models.CharField(max_length=100)
    premio_primeiro = models.CharField(max_length=100, default=0)
    premio_segundo = models.CharField(max_length=100, default=0)
    premio_terceiro = models.CharField(max_length=100, default=0)
    numero_rodadas = models.PositiveSmallIntegerField('Número de rodadas', default=5)

class Partida(models.Model):
    @property
    def resultado_legivel(self):
        return {'B': 'Vitória das brancas', 'P': 'Vitória das pretas', 'E': 'Empate', '': 'Pendente'}.get(self.vencedor, self.vencedor)

    rodada_suica = models.ForeignKey('RodadaSuica', on_delete=models.CASCADE, null=True, blank=True, related_name='partidas')
    jogador_branca = models.ForeignKey(Usuario, on_delete=models.PROTECT, null=True, blank=True, related_name='partidas_brancas')
    jogador_preta = models.ForeignKey(Usuario, on_delete=models.PROTECT, null=True, blank=True, related_name='partidas_pretas')
    usuario_branca = models.CharField(max_length=1000) # nome(Usuário)
    usuario_preta   = models.CharField(max_length=1000) #  nome(Usuário)
    torneio = models.CharField(max_length=1000) #  nome(Torneio)
    vencedor = models.CharField(max_length=1)
    data_partida =  models.DateField()
    rodada =  models.IntegerField()
    Torneios = models.ForeignKey ('Torneios', on_delete=models.deletion.CASCADE)


class Inscricao(models.Model):
    torneio = models.ForeignKey(Torneios, on_delete=models.CASCADE, related_name='inscricoes')
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    numero = models.PositiveIntegerField()

    class Meta:
        ordering = ['numero']
        constraints = [
            models.UniqueConstraint(fields=['torneio', 'usuario'], name='inscricao_usuario_unico'),
            models.UniqueConstraint(fields=['torneio', 'numero'], name='inscricao_numero_unico'),
        ]

    def __str__(self):
        return f'{self.numero} - {self.usuario.nome}'

class RodadaSuica(models.Model):
    torneio = models.ForeignKey(Torneios, on_delete=models.CASCADE, related_name='rodadas_suicas')
    numero = models.PositiveIntegerField()
    folga = models.ForeignKey(Usuario, on_delete=models.PROTECT, null=True, blank=True, related_name='+')

    class Meta:
        ordering = ['numero']
        constraints = [models.UniqueConstraint(fields=['torneio', 'numero'], name='rodada_suica_unica')]
