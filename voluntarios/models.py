

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

PROVINCIAS = [
    ('luanda', 'Luanda'), ('benguela', 'Benguela'), ('huila', 'Huíla'),
    ('cabinda', 'Cabinda'), ('zaire', 'Zaire'), ('uige', 'Uíge'),
    ('cuanza_norte', 'Cuanza Norte'), ('cuanza_sul', 'Cuanza Sul'),
    ('malanje', 'Malanje'), ('lunda_norte', 'Lunda Norte'),
    ('lunda_sul', 'Lunda Sul'), ('moxico', 'Moxico'),
    ('cuando_cubango', 'Cuando Cubango'), ('cunene', 'Cunene'),
    ('namibe', 'Namibe'), ('huambo', 'Huambo'),
    ('bie', 'Bié'), ('kwanza_sul', 'Kwanza Sul'),
]

class Habilidade(models.Model):
    CATEGORIAS = [
        ('saude', '🏥 Saúde'), ('logistica', '🚛 Logística'),
        ('engenharia', '🔧 Engenharia'), ('alimentacao', '🍽️ Alimentação'),
        ('comunicacao', '📡 Comunicação'), ('educacao', '📚 Educação'),
        ('seguranca', '🛡️ Segurança'), ('psicologia', '🧠 Psicologia'),
        ('outro', '⭐ Outro'),
    ]
    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    icone = models.CharField(max_length=10, default='⭐')

    class Meta:
        verbose_name = _('Habilidade')
        verbose_name_plural = _('Habilidades')
        ordering = ['categoria', 'nome']

    def __str__(self):
        return f"{self.icone} {self.nome}"


class Voluntario(models.Model):
    DISPONIBILIDADE = [
        ('disponivel', 'Disponível'),
        ('ocupado', 'Ocupado'),
        ('indisponivel', 'Indisponível'),
    ]

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    nome = models.CharField(max_length=150)
    telefone = models.CharField(max_length=25)
    email = models.EmailField()
    provincia = models.CharField(max_length=30, choices=PROVINCIAS)
    municipio = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    habilidades = models.ManyToManyField(Habilidade, blank=True)
    disponibilidade = models.CharField(max_length=15, choices=DISPONIBILIDADE, default='disponivel')
    bio = models.TextField(blank=True, max_length=500)
    foto = models.ImageField(upload_to='voluntarios/', blank=True, null=True)
    numero_bi = models.CharField(max_length=20, blank=True)
    verificado = models.BooleanField(default=False)
    missoes_completadas = models.PositiveIntegerField(default=0)
    data_nascimento = models.DateField(null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Voluntário')
        verbose_name_plural = _('Voluntários')
        ordering = ['-data_cadastro']

    def __str__(self):
        return self.nome

    @property
    def provincia_display(self):
        return dict(PROVINCIAS).get(self.provincia, self.provincia)

    @property
    def iniciais(self):
        parts = self.nome.split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[-1][0]}".upper()
        return self.nome[:2].upper()


