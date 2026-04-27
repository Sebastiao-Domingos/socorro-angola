from incidentes.models import Incidente
from voluntarios.models import Voluntario
from doacoes.models import CentralDoacao

def global_context(request):
    ctx = {
        'total_incidentes_ativos': 0,
        'total_incidentes_criticos': 0,
        'total_voluntarios': 0,
    }
    try:
        ctx['total_incidentes_ativos'] = Incidente.objects.filter(status__in=['ativo','em_atendimento']).count()
        ctx['total_incidentes_criticos'] = Incidente.objects.filter(status='ativo', severidade='critico').count()
        ctx['total_voluntarios'] = Voluntario.objects.filter(disponibilidade='disponivel').count()
    except Exception:
        pass
    return ctx
