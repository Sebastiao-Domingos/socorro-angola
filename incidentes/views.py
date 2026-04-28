from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Incidente, ChecklistItem, RelatorioIntervencao, CHECKLIST_PADRAO
from voluntarios.models import Voluntario


@login_required
def lista(request):
    qs = Incidente.objects.prefetch_related('voluntarios_alocados').all()
    q = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    severidade = request.GET.get('severidade', '')
    status = request.GET.get('status', '')
    provincia = request.GET.get('provincia', '')

    if q:
        qs = qs.filter(Q(titulo__icontains=q) | Q(municipio__icontains=q) | Q(descricao__icontains=q))
    if tipo:
        qs = qs.filter(tipo=tipo)
    if severidade:
        qs = qs.filter(severidade=severidade)
    if status:
        qs = qs.filter(status=status)
    if provincia:
        qs = qs.filter(provincia__icontains=provincia)

    paginator = Paginator(qs, 10)
    incidentes = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'incidentes/lista.html', {
        'incidentes': incidentes,
        'filtros': {'q': q, 'tipo': tipo, 'severidade': severidade, 'status': status, 'provincia': provincia},
        'tipos': Incidente.TIPOS,
        'severidades': Incidente.SEVERIDADES,
        'status_choices': Incidente.STATUS,
        'total': qs.count(),
    })


@login_required
def novo(request):
    if request.method == 'POST':
        try:
            inc = Incidente(
                titulo=request.POST['titulo'].strip(),
                descricao=request.POST['descricao'].strip(),
                tipo=request.POST['tipo'],
                severidade=request.POST['severidade'],
                provincia=request.POST['provincia'].strip(),
                municipio=request.POST['municipio'].strip(),
                bairro=request.POST.get('bairro', '').strip(),
                pessoas_afetadas=request.POST.get('pessoas_afetadas', 0) or 0,
                voluntarios_necessarios=request.POST.get('voluntarios_necessarios', 5) or 5,
                reportado_por=request.user,
            )
            lat = request.POST.get('latitude')
            lng = request.POST.get('longitude')
            if lat and lng:
                inc.latitude, inc.longitude = lat, lng
            if request.FILES.get('imagem'):
                inc.imagem = request.FILES['imagem']
            inc.save()

            # Generate automatic checklist
            items = CHECKLIST_PADRAO.get(inc.tipo, [])
            for i, item in enumerate(items):
                ChecklistItem.objects.create(incidente=inc, descricao=item, ordem=i)

            messages.success(request, f'Incidente registado! Checklist com {len(items)} itens criada automaticamente.')
            return redirect('incidentes_detalhe', pk=inc.pk)
        except Exception as e:
            messages.error(request, f'Erro: {str(e)}')

    return render(request, 'incidentes/form.html', {
        'tipos': Incidente.TIPOS,
        'severidades': Incidente.SEVERIDADES,
    })


@login_required
def detalhe(request, pk):
    inc = get_object_or_404(
        Incidente.objects.prefetch_related('voluntarios_alocados', 'checklist', 'relatorios__autor'),
        pk=pk
    )
    checklist = inc.checklist.all()
    total_check = checklist.count()
    concluidos = checklist.filter(concluido=True).count()
    progresso_check = int((concluidos / total_check * 100)) if total_check else 0

    vol_disponiveis = (Voluntario.objects
        .filter(disponibilidade='disponivel')
        .exclude(id__in=inc.voluntarios_alocados.all())
        .prefetch_related('habilidades')[:20])

    return render(request, 'incidentes/detalhe.html', {
        'incidente': inc,
        'checklist': checklist,
        'progresso_checklist': progresso_check,
        'concluidos': concluidos,
        'total_checklist': total_check,
        'voluntarios_disponiveis': vol_disponiveis,
        'relatorios': inc.relatorios.all(),
        'voluntarios_alocados': inc.voluntarios_alocados.prefetch_related('habilidades').all(),
    })


@login_required
def editar_status(request, pk):
    inc = get_object_or_404(Incidente, pk=pk)
    if request.method == 'POST':
        novo_status = request.POST.get('status')
        if novo_status in dict(Incidente.STATUS):
            inc.status = novo_status
            if novo_status == 'resolvido':
                inc.data_resolucao = timezone.now()
            inc.save()
            messages.success(request, f'Estado actualizado para: {inc.get_status_display()}')
    return redirect('incidentes_detalhe', pk=pk)


@login_required
def alocar_voluntario(request, pk):
    inc = get_object_or_404(Incidente, pk=pk)
    if request.method == 'POST':
        vid = request.POST.get('voluntario_id')
        v = get_object_or_404(Voluntario, pk=vid)
        inc.voluntarios_alocados.add(v)
        v.disponibilidade = 'ocupado'
        v.save()
        messages.success(request, f'{v.nome} alocado ao incidente com sucesso!')
    return redirect('incidentes_detalhe', pk=pk)


@login_required
def remover_voluntario(request, pk, vid):
    inc = get_object_or_404(Incidente, pk=pk)
    v = get_object_or_404(Voluntario, pk=vid)
    inc.voluntarios_alocados.remove(v)
    # Only set available if not in another mission
    if not v.missoes.filter(status__in=['ativo','em_atendimento']).exists():
        v.disponibilidade = 'disponivel'
        v.save()
    messages.success(request, f'{v.nome} removido do incidente.')
    return redirect('incidentes_detalhe', pk=pk)


@login_required
def toggle_checklist(request, pk):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        item_id = data.get('item_id')
        concluido = data.get('concluido', False)
        try:
            item = ChecklistItem.objects.get(pk=item_id, incidente_id=pk)
            item.concluido = concluido
            item.data_conclusao = timezone.now() if concluido else None
            item.save()
            total = ChecklistItem.objects.filter(incidente_id=pk).count()
            done = ChecklistItem.objects.filter(incidente_id=pk, concluido=True).count()
            return JsonResponse({'ok': True, 'progresso': int(done/total*100) if total else 0})
        except ChecklistItem.DoesNotExist:
            return JsonResponse({'ok': False}, status=404)
    return JsonResponse({'ok': False}, status=400)


@login_required
def novo_relatorio(request, pk):
    inc = get_object_or_404(Incidente, pk=pk)
    if request.method == 'POST':
        vid = request.POST.get('voluntario_id')
        v = get_object_or_404(Voluntario, pk=vid)
        RelatorioIntervencao.objects.create(
            incidente=inc,
            autor=v,
            acoes_realizadas=request.POST.get('acoes_realizadas', '').strip(),
            pessoas_ajudadas=request.POST.get('pessoas_ajudadas', 0) or 0,
            recursos_utilizados=request.POST.get('recursos_utilizados', '').strip(),
            problemas_encontrados=request.POST.get('problemas_encontrados', '').strip(),
            recomendacoes=request.POST.get('recomendacoes', '').strip(),
        )
        v.missoes_completadas += 1
        v.save()
        messages.success(request, 'Relatório submetido com sucesso!')
    return redirect('incidentes_detalhe', pk=pk)


def reportar_publico(request):
    """Página pública para a população reportar incidentes — mobile-first."""
    if request.method == 'POST':
        try:
            inc = Incidente(
                titulo=request.POST.get('titulo', '').strip(),
                descricao=request.POST.get('descricao', '').strip(),
                tipo=request.POST.get('tipo', 'outro'),
                severidade=request.POST.get('severidade', 'medio'),
                provincia=request.POST.get('provincia', '').strip(),
                municipio=request.POST.get('municipio', '').strip(),
                bairro=request.POST.get('bairro', '').strip(),
                pessoas_afetadas=request.POST.get('pessoas_afetadas', 0) or 0,
                voluntarios_necessarios=5,
                status='ativo',
            )
            lat = request.POST.get('latitude', '').strip()
            lng = request.POST.get('longitude', '').strip()
            if lat and lng:
                inc.latitude, inc.longitude = lat, lng
            if request.FILES.get('imagem'):
                inc.imagem = request.FILES['imagem']
            inc.save()

            items = CHECKLIST_PADRAO.get(inc.tipo, [])
            for i, item in enumerate(items):
                ChecklistItem.objects.create(incidente=inc, descricao=item, ordem=i)

            # Return success page or JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({'ok': True, 'id': inc.pk})
            
            return redirect('reportar_sucesso')
        
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Erro ao registar: {str(e)}')

    return render(request, 'incidentes/reportar_publico.html', {
        'tipos': Incidente.TIPOS,
        'severidades': Incidente.SEVERIDADES,
    })


def reportar_sucesso(request):
    return render(request, 'incidentes/reportar_sucesso.html')