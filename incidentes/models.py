from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from voluntarios.models import Voluntario

CHECKLIST_PADRAO = {
    'enchente': [
        'Activar alerta de evacuação nas zonas de risco',
        'Montar pontos de acolhimento temporário',
        'Distribuir água potável e alimentos básicos',
        'Verificar e desligar infraestrutura eléctrica na área inundada',
        'Accionar equipa da Protecção Civil (SNPCB)',
        'Registar famílias deslocadas com dados completos',
        'Garantir atendimento médico de emergência no local',
        'Coordenar transporte para grupos vulneráveis',
    ],
    'incendio': [
        'Evacuar a área imediatamente e estabelecer perímetro de segurança',
        'Contactar Bombeiros e Protecção Civil',
        'Atender feridos e prestar primeiros socorros',
        'Verificar se há vítimas presas no local',
        'Documentar os danos com fotografias',
        'Providenciar abrigo temporário para desalojados',
        'Monitorizar propagação e ajustar perímetro de segurança',
    ],
    'seca': [
        'Mapear e registar famílias mais afectadas (crianças, idosos, doentes)',
        'Instalar pontos de distribuição de água potável',
        'Montar centrais de doação de alimentos e itens básicos',
        'Apoiar acções de produção alimentar de emergência',
        'Activar programas sociais e assistência governamental',
        'Monitorizar o estado nutricional das crianças',
    ],
    'deslizamento': [
        'Evacuar imediatamente a zona de risco geológico',
        'Iniciar busca e resgate de vítimas soterradas',
        'Prestar atendimento médico no local',
        'Isolar a área instável com sinalização adequada',
        'Montar abrigo e alimentação para desalojados',
        'Registar desaparecidos e comunicar às famílias',
        'Documentar a extensão dos danos materiais',
    ],
    'deslocamento': [
        'Registar todas as famílias deslocadas com dados completos',
        'Montar e organizar abrigo temporário seguro',
        'Distribuir kits de higiene e itens de primeira necessidade',
        'Garantir três refeições diárias para todos os deslocados',
        'Providenciar apoio psicossocial e de saúde mental',
        'Identificar e proteger crianças não acompanhadas',
        'Estabelecer comunicação com famílias separadas',
    ],
    'epidemia': [
        'Isolar casos confirmados e suspeitos',
        'Activar protocolo de saúde pública com autoridades do MINSA',
        'Distribuir equipamentos de protecção individual (EPIs)',
        'Garantir acesso a tratamento e medicação',
        'Sensibilizar a comunidade sobre medidas preventivas',
        'Desinfectar locais públicos e habitações afectadas',
    ],
    'acidente': [
        'Garantir segurança no local e isolar a área',
        'Prestar primeiros socorros às vítimas',
        'Contactar serviços de emergência médica (SAMU)',
        'Coordenar transporte das vítimas para unidades hospitalares',
        'Registar e identificar todas as vítimas',
        'Apoiar familiares das vítimas com informação e suporte',
    ],
}


class Incidente(models.Model):
    TIPOS = [
        ('enchente', '🌊 Enchente'), ('incendio', '🔥 Incêndio'),
        ('seca', '☀️ Seca'), ('deslizamento', '⛰️ Deslizamento'),
        ('deslocamento', '🚶 Deslocamento Populacional'),
        ('epidemia', '🦠 Epidemia'), ('acidente', '🚨 Acidente em Massa'),
        ('outro', '⚠️ Outro'),
    ]
    SEVERIDADES = [
        ('baixo', 'Baixo'), ('medio', 'Médio'), ('critico', 'Crítico'),
    ]
    STATUS = [
        ('ativo', 'Activo'), ('em_atendimento', 'Em Atendimento'),
        ('monitoramento', 'Em Monitoramento'), ('resolvido', 'Resolvido'),
    ]

    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS)
    severidade = models.CharField(max_length=10, choices=SEVERIDADES, default='medio')
    status = models.CharField(max_length=20, choices=STATUS, default='ativo')
    provincia = models.CharField(max_length=50)
    municipio = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    pessoas_afetadas = models.PositiveIntegerField(default=0)
    voluntarios_necessarios = models.PositiveIntegerField(default=5)
    voluntarios_alocados = models.ManyToManyField(Voluntario, blank=True, related_name='missoes')
    reportado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    imagem = models.ImageField(upload_to='incidentes/', null=True, blank=True)
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_resolucao = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Incidente')
        verbose_name_plural = _('Incidentes')
        ordering = ['-data_inicio']

    def __str__(self):
        return f"[{self.get_severidade_display()}] {self.titulo}"

    def get_tipo_emoji(self):
        return dict(self.TIPOS).get(self.tipo, '⚠️').split()[0]

    @property
    def progresso_voluntarios(self):
        alocados = self.voluntarios_alocados.count()
        if self.voluntarios_necessarios == 0:
            return 100
        return min(100, int((alocados / self.voluntarios_necessarios) * 100))

    @property
    def duracao(self):
        end = self.data_resolucao or timezone.now()
        delta = end - self.data_inicio
        hours = int(delta.total_seconds() // 3600)
        if hours < 24:
            return f"{hours}h"
        days = delta.days
        return f"{days}d"


class ChecklistItem(models.Model):
    incidente = models.ForeignKey(Incidente, on_delete=models.CASCADE, related_name='checklist')
    descricao = models.CharField(max_length=300)
    concluido = models.BooleanField(default=False)
    responsavel = models.ForeignKey(Voluntario, on_delete=models.SET_NULL, null=True, blank=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    ordem = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return self.descricao


class RelatorioIntervencao(models.Model):
    incidente = models.ForeignKey(Incidente, on_delete=models.CASCADE, related_name='relatorios')
    autor = models.ForeignKey(Voluntario, on_delete=models.SET_NULL, null=True)
    acoes_realizadas = models.TextField()
    pessoas_ajudadas = models.PositiveIntegerField(default=0)
    recursos_utilizados = models.TextField(blank=True)
    problemas_encontrados = models.TextField(blank=True)
    recomendacoes = models.TextField(blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Relatório de Intervenção')
        ordering = ['-data_criacao']