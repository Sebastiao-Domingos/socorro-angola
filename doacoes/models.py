from django.db import models
from django.utils.translation import gettext_lazy as _

class CentralDoacao(models.Model):
    TIPOS = [
        ('agua', '💧 Água'), ('alimentos', '🥫 Alimentos'),
        ('roupas', '👕 Roupas'), ('medicamentos', '💊 Medicamentos'),
        ('higiene', '🧼 Higiene'), ('materiais', '🧱 Materiais de Construção'),
        ('geral', '📦 Geral'),
    ]
    STATUS = [
        ('ativo', 'Activa'), ('cheio', 'Cheia'), ('fechado', 'Fechada'),
    ]

    nome = models.CharField(max_length=150)
    tipo = models.CharField(max_length=15, choices=TIPOS, default='geral')
    provincia = models.CharField(max_length=50)
    municipio = models.CharField(max_length=100)
    endereco = models.TextField()
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    responsavel = models.CharField(max_length=150)
    telefone = models.CharField(max_length=25)
    email = models.EmailField(blank=True)
    horario = models.CharField(max_length=100, blank=True)
    descricao = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='ativo')
    capacidade_total = models.PositiveIntegerField(default=1000)
    capacidade_atual = models.PositiveIntegerField(default=0)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Central de Doação')
        verbose_name_plural = _('Centrais de Doação')
        ordering = ['-data_criacao']

    def __str__(self):
        return f"{self.nome} — {self.municipio}"

    @property
    def percentual_ocupacao(self):
        if self.capacidade_total == 0:
            return 0
        return min(100, int((self.capacidade_atual / self.capacidade_total) * 100))

    @property
    def status_ocupacao(self):
        p = self.percentual_ocupacao
        if p >= 90:
            return 'critico'
        elif p >= 60:
            return 'medio'
        return 'bom'


class Doacao(models.Model):
    CATEGORIAS = [
        ('agua', '💧 Água'), ('alimentos', '🥫 Alimentos'),
        ('roupas', '👕 Roupas'), ('medicamentos', '💊 Medicamentos'),
        ('higiene', '🧼 Higiene'), ('dinheiro', '💰 Dinheiro'),
        ('outro', '📦 Outro'),
    ]

    central = models.ForeignKey(CentralDoacao, on_delete=models.CASCADE, related_name='doacoes')
    doador_nome = models.CharField(max_length=150)
    doador_telefone = models.CharField(max_length=25, blank=True)
    doador_anonimo = models.BooleanField(default=False)
    categoria = models.CharField(max_length=15, choices=CATEGORIAS, default='outro')
    descricao = models.TextField()
    quantidade = models.PositiveIntegerField(default=1)
    unidade = models.CharField(max_length=30, default='unidades')
    valor_estimado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    entregue = models.BooleanField(default=True)
    data_doacao = models.DateTimeField(auto_now_add=True)
    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = _('Doação')
        ordering = ['-data_doacao']

    def __str__(self):
        nome = 'Anónimo' if self.doador_anonimo else self.doador_nome
        return f"Doação de {nome} → {self.central.nome}"