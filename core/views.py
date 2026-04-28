from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from incidentes.models import Incidente, RelatorioIntervencao
from voluntarios.models import Voluntario
from doacoes.models import CentralDoacao, Doacao
import json
from decimal import Decimal
from django.core.paginator import Paginator
from django.db.models import Sum as DSum





class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    stats = {
        'incidentes_ativos': Incidente.objects.filter(status__in=['ativo', 'em_atendimento']).count(),
        'voluntarios': Voluntario.objects.filter(disponibilidade='disponivel').count(),
        'pessoas_ajudadas': Incidente.objects.aggregate(t=Sum('pessoas_afetadas'))['t'] or 0,
        'centrais': CentralDoacao.objects.filter(status='ativo').count(),
    }
    incidentes_recentes = Incidente.objects.filter(
        status__in=['ativo', 'em_atendimento']
    ).select_related('reportado_por').order_by('-data_inicio')[:6]
    return render(request, 'core/home.html', {'stats': stats, 'incidentes_recentes': incidentes_recentes})


@login_required
def dashboard(request):
    now = timezone.now()
    inicio_semana = now - timedelta(days=7)

    stats = {
        'incidentes_ativos': Incidente.objects.filter(status='ativo').count(),
        'incidentes_criticos': Incidente.objects.filter(status='ativo', severidade='critico').count(),
        'incidentes_em_atendimento': Incidente.objects.filter(status='em_atendimento').count(),
        'incidentes_resolvidos': Incidente.objects.filter(status='resolvido').count(),
        'voluntarios_disponiveis': Voluntario.objects.filter(disponibilidade='disponivel').count(),
        'voluntarios_ocupados': Voluntario.objects.filter(disponibilidade='ocupado').count(),
        'total_voluntarios': Voluntario.objects.count(),
        'centrais_ativas': CentralDoacao.objects.filter(status='ativo').count(),
        'doacoes_semana': Doacao.objects.filter(data_doacao__gte=inicio_semana).count(),
        'pessoas_ajudadas': Incidente.objects.aggregate(t=Sum('pessoas_afetadas'))['t'] or 0,
        'novos_esta_semana': Incidente.objects.filter(data_inicio__gte=inicio_semana).count(),
    }

    incidentes_recentes = (Incidente.objects
        .select_related('reportado_por')
        .prefetch_related('voluntarios_alocados')
        .order_by('-data_inicio')[:10])

    top_voluntarios = (Voluntario.objects
        .filter(missoes_completadas__gt=0)
        .order_by('-missoes_completadas')[:5])

    distribuicao_tipo = list(
        Incidente.objects.values('tipo')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    distribuicao_prov = list(
        Incidente.objects.values('provincia')
        .annotate(total=Count('id'))
        .order_by('-total')[:8]
    )

    incidentes_mapa = list(
        Incidente.objects.exclude(latitude=None)
        .filter(status__in=['ativo', 'em_atendimento'])
        .values('id', 'titulo', 'tipo', 'severidade', 'status', 'latitude', 'longitude',
                'provincia', 'municipio', 'pessoas_afetadas')
    )

    return render(request, 'core/dashboard.html', {
        'stats': stats,
        'incidentes_recentes': incidentes_recentes,
        'top_voluntarios': top_voluntarios,
        'distribuicao_tipo': distribuicao_tipo,
        'distribuicao_prov': distribuicao_prov,
        'incidentes_mapa_json': json.dumps(incidentes_mapa, cls=DecimalEncoder),
    })


def login_view(request):

        
    bancos = [
        "🗺️ Mapa de incidentes em tempo real","👥 Banco de voluntários georreferenciado","📦 Gestão de centrais de doação", "📊 Relatórios de intervenção"
    ]

    bancos_textos = [
        "Mapa de incidentes em tempo real",
        "Banco de voluntários georreferenciado",
        "Gestão de centrais de doação",
        "Relatórios de intervenção"
    ]

    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user and user.is_active:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        messages.error(request, 'Utilizador ou palavra-passe incorrectos.')
    return render(request, 'core/login.html' , context={'bancos': bancos, 'bancos_textos': bancos_textos})


def logout_view(request):
    logout(request)
    messages.success(request, 'Sessão encerrada com sucesso.')
    return redirect('home')


@login_required
def mapa(request):
    incidentes = list(
        Incidente.objects.exclude(latitude=None)
        .values('id', 'titulo', 'tipo', 'severidade', 'status', 'latitude',
                'longitude', 'provincia', 'municipio', 'pessoas_afetadas', 'data_inicio')
    )
    centrais = list(
        CentralDoacao.objects.exclude(latitude=None)
        .values('id', 'nome', 'tipo', 'status', 'latitude', 'longitude',
                'provincia', 'municipio', 'telefone', 'capacidade_atual', 'capacidade_total')
    )

    # Convert date to string
    for inc in incidentes:
        if inc.get('data_inicio'):
            inc['data_inicio'] = inc['data_inicio'].strftime('%d/%m/%Y %H:%M')

    return render(request, 'core/mapa.html', {
        'incidentes_json': json.dumps(incidentes, cls=DecimalEncoder),
        'centrais_json': json.dumps(centrais, cls=DecimalEncoder),
        'total_incidentes': len(incidentes),
        'total_centrais': len(centrais),
    })


@login_required
def relatorios(request):
    """Página consolidada de todos os relatórios de intervenção."""
    qs = RelatorioIntervencao.objects.select_related('incidente', 'autor').order_by('-data_criacao')

    incidente_id = request.GET.get('incidente', '')
    autor_id = request.GET.get('autor', '')
    if incidente_id:
        qs = qs.filter(incidente_id=incidente_id)
    if autor_id:
        qs = qs.filter(autor_id=autor_id)

    
    paginator = Paginator(qs, 12)
    relatorios_page = paginator.get_page(request.GET.get('page', 1))


    totais = qs.aggregate(
        total_pessoas=DSum('pessoas_ajudadas'),
        total_relatorios=Count('id'),
    )

    incidentes = Incidente.objects.values('id', 'titulo').order_by('titulo')
    voluntarios_com_rel = Voluntario.objects.filter(
        relatoriointervencao__isnull=False
    ).distinct().values('id', 'nome')

    return render(request, 'core/relatorios.html', {
        'relatorios': relatorios_page,
        'totais': totais,
        'incidentes': incidentes,
        'voluntarios': voluntarios_com_rel,
        'filtros': {'incidente': incidente_id, 'autor': autor_id},
    })


@login_required
def analytics(request):
    """Página de análise e estatísticas avançadas."""

    now = timezone.now()

    # Incidentes por tipo
    por_tipo = list(
        Incidente.objects.values('tipo')
        .annotate(total=Count('id'), afetados=DSum('pessoas_afetadas'))
        .order_by('-total')
    )

    # Incidentes por severidade
    por_sev = list(
        Incidente.objects.values('severidade')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Incidentes por província (top 10)
    por_prov = list(
        Incidente.objects.values('provincia')
        .annotate(total=Count('id'), afetados=DSum('pessoas_afetadas'))
        .order_by('-total')[:10]
    )

    # Incidentes por status
    por_status = list(
        Incidente.objects.values('status')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Evolução últimos 30 dias
    evolucao = []
    for i in range(29, -1, -1):
        dia = (now - timedelta(days=i)).date()
        count = Incidente.objects.filter(data_inicio__date=dia).count()
        evolucao.append({'dia': dia.strftime('%d/%m'), 'total': count})

    # Voluntários por província
    vol_prov = list(
        Voluntario.objects.values('provincia')
        .annotate(total=Count('id'))
        .order_by('-total')[:8]
    )

    # Top habilidades mais requisitadas
    from voluntarios.models import Habilidade
    top_habs = list(
        Habilidade.objects.annotate(total_vols=Count('voluntario'))
        .order_by('-total_vols')[:8]
        .values('nome', 'icone', 'total_vols')
    )

    # Centrais por tipo e ocupação média
    from doacoes.models import CentralDoacao
    cent_stats = list(
        CentralDoacao.objects.values('tipo')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Totais gerais
    totais = {
        'total_incidentes': Incidente.objects.count(),
        'total_resolvidos': Incidente.objects.filter(status='resolvido').count(),
        'total_afetados': Incidente.objects.aggregate(t=DSum('pessoas_afetadas'))['t'] or 0,
        'total_voluntarios': Voluntario.objects.count(),
        'total_verificados': Voluntario.objects.filter(verificado=True).count(),
        'total_missoes': sum(v.missoes_completadas for v in Voluntario.objects.all()),
        'total_doacoes': __import__('doacoes.models', fromlist=['Doacao']).Doacao.objects.count(),
        'total_centrais': CentralDoacao.objects.count(),
    }

    return render(request, 'core/analytics.html', {
        'por_tipo': por_tipo,
        'por_sev': por_sev,
        'por_prov': por_prov,
        'por_status': por_status,
        'evolucao': evolucao,
        'vol_prov': vol_prov,
        'top_habs': top_habs,
        'cent_stats': cent_stats,
        'totais': totais,
        'evolucao_json': json.dumps(evolucao),
        'por_tipo_json': json.dumps(por_tipo),
        'por_prov_json': json.dumps(por_prov),
    })


@login_required
def perfil(request):
    """Página de perfil do utilizador autenticado."""
    incidentes_reportados = Incidente.objects.filter(reportado_por=request.user).order_by('-data_inicio')[:10]

    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name).strip()
        user.last_name = request.POST.get('last_name', user.last_name).strip()
        user.email = request.POST.get('email', user.email).strip()
        user.save()

        # Change password
        old_pw = request.POST.get('old_password', '')
        new_pw = request.POST.get('new_password', '')

        if old_pw and new_pw:
            if request.user.check_password(old_pw):
                request.user.set_password(new_pw)
                request.user.save()
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Palavra-passe alterada com sucesso.')
            else:
                messages.error(request, 'Palavra-passe actual incorrecta.')
        else:
            messages.success(request, 'Perfil actualizado com sucesso.')
        return redirect('perfil')

    return render(request, 'core/perfil.html', {
        'incidentes_reportados': incidentes_reportados,
    })


def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    return render(request, 'errors/500.html', status=500)