from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import CentralDoacao, Doacao


@login_required
def lista(request):
    qs = CentralDoacao.objects.all()
    tipo = request.GET.get('tipo', '')
    status = request.GET.get('status', '')
    if tipo:
        qs = qs.filter(tipo=tipo)
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 9)
    centrais = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'doacoes/lista.html', {
        'centrais': centrais,
        'tipos': CentralDoacao.TIPOS,
        'status_choices': CentralDoacao.STATUS,
        'filtros': {'tipo': tipo, 'status': status},
    })


@login_required
def nova_central(request):
    if request.method == 'POST':
        try:
            c = CentralDoacao(
                nome=request.POST['nome'].strip(),
                tipo=request.POST['tipo'],
                provincia=request.POST['provincia'].strip(),
                municipio=request.POST['municipio'].strip(),
                endereco=request.POST['endereco'].strip(),
                responsavel=request.POST['responsavel'].strip(),
                telefone=request.POST['telefone'].strip(),
                email=request.POST.get('email', '').strip(),
                horario=request.POST.get('horario', '').strip(),
                descricao=request.POST.get('descricao', '').strip(),
                capacidade_total=request.POST.get('capacidade_total', 1000) or 1000,
            )
            lat = request.POST.get('latitude')
            lng = request.POST.get('longitude')
            if lat and lng:
                c.latitude, c.longitude = lat, lng
            c.save()
            messages.success(request, f'Central "{c.nome}" criada com sucesso!')
            return redirect('doacoes_detalhe', pk=c.pk)
        except Exception as e:
            messages.error(request, f'Erro: {str(e)}')
    return render(request, 'doacoes/form.html', {'tipos': CentralDoacao.TIPOS})


@login_required
def detalhe(request, pk):
    central = get_object_or_404(CentralDoacao, pk=pk)
    doacoes = central.doacoes.order_by('-data_doacao')
    paginator = Paginator(doacoes, 10)
    doacoes_page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'doacoes/detalhe.html', {
        'central': central,
        'doacoes': doacoes_page,
        'total_doacoes': doacoes.count(),
        'categorias': Doacao.CATEGORIAS,
    })


@login_required
def registar_doacao(request, pk):
    central = get_object_or_404(CentralDoacao, pk=pk)
    if request.method == 'POST':
        anonimo = request.POST.get('doador_anonimo') == 'on'
        quantidade = int(request.POST.get('quantidade', 1) or 1)
        Doacao.objects.create(
            central=central,
            doador_nome=request.POST.get('doador_nome', 'Anónimo').strip(),
            doador_telefone=request.POST.get('doador_telefone', '').strip(),
            doador_anonimo=anonimo,
            categoria=request.POST.get('categoria', 'outro'),
            descricao=request.POST.get('descricao', '').strip(),
            quantidade=quantidade,
            unidade=request.POST.get('unidade', 'unidades').strip(),
            observacoes=request.POST.get('observacoes', '').strip(),
        )
        central.capacidade_atual = min(
            central.capacidade_total,
            central.capacidade_atual + quantidade
        )
        central.save()
        messages.success(request, 'Doação registada com sucesso! Obrigado!')
    return redirect('doacoes_detalhe', pk=pk)


@login_required
def editar_central(request, pk):
    central = get_object_or_404(CentralDoacao, pk=pk)
    if request.method == 'POST':
        central.nome = request.POST.get('nome', central.nome).strip()
        central.tipo = request.POST.get('tipo', central.tipo)
        central.status = request.POST.get('status', central.status)
        central.horario = request.POST.get('horario', central.horario).strip()
        central.descricao = request.POST.get('descricao', central.descricao).strip()
        central.capacidade_total = request.POST.get('capacidade_total', central.capacidade_total) or central.capacidade_total
        central.save()
        messages.success(request, 'Central actualizada!')
        return redirect('doacoes_detalhe', pk=pk)
    return render(request, 'doacoes/form.html', {'central': central, 'tipos': CentralDoacao.TIPOS, 'status_choices': CentralDoacao.STATUS})