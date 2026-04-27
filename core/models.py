
from django.db import models

class Notificacao(models.Model):
    TIPOS = [
        ('info', 'Informação'), ('alerta', 'Alerta'),
        ('critico', 'Crítico'), ('sucesso', 'Sucesso'),
    ]
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    tipo = models.CharField(max_length=10, choices=TIPOS, default='info')
    lida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_criacao']

    def __str__(self):
        return self.titulo


