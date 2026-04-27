from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Voluntario, Habilidade, PROVINCIAS

@login_required
def lista(request):
    qs = Voluntario.objects.prefetch_related('habilidades').all()
    q = request.GET.get('q', '')
    disponibilidade = request.GET.get('disponibilidade', '')
    provincia = request.GET.get('provincia', '')
    habilidade_id = request.GET.get('habilidade', '')

    if q:
        qs = qs.filter(Q(nome__icontains=q) | Q(municipio__icontains=q) | Q(email__icontains=q))
    if disponibilidade:
        qs = qs.filter(disponibilidade=disponibilidade)
    if provincia:
        qs = qs.filter(provincia=provincia)
    if habilidade_id:
        qs = qs.filter(habilidades__id=habilidade_id)

    paginator = Paginator(qs, 12)
    page = request.GET.get('page', 1)
    voluntarios = paginator.get_page(page)

    return render(request, 'voluntarios/lista.html', {
        'voluntarios': voluntarios,
        'habilidades': Habilidade.objects.all(),
        'provincias': PROVINCIAS,
        'filtros': {'q': q, 'disponibilidade': disponibilidade, 'provincia': provincia, 'habilidade': habilidade_id},
        'total': qs.count(),
    })


@login_required
def cadastrar(request):
    habilidades = Habilidade.objects.all()
    if request.method == 'POST':
        try:
            v = Voluntario(
                nome=request.POST['nome'].strip(),
                telefone=request.POST['telefone'].strip(),
                email=request.POST['email'].strip(),
                provincia=request.POST['provincia'],
                municipio=request.POST['municipio'].strip(),
                bairro=request.POST.get('bairro', '').strip(),
                bio=request.POST.get('bio', '').strip(),
                numero_bi=request.POST.get('numero_bi', '').strip(),
                disponibilidade=request.POST.get('disponibilidade', 'disponivel'),
            )
            lat = request.POST.get('latitude')
            lng = request.POST.get('longitude')
            if lat and lng:
                v.latitude, v.longitude = lat, lng
            if request.FILES.get('foto'):
                v.foto = request.FILES['foto']
            v.save()
            ids = request.POST.getlist('habilidades')
            if ids:
                v.habilidades.set(ids)
            messages.success(request, f'Voluntário {v.nome} cadastrado com sucesso!')
            return redirect('voluntarios_detalhe', pk=v.pk)
        except Exception as e:
            messages.error(request, f'Erro ao cadastrar: {str(e)}')

    return render(request, 'voluntarios/form.html', {
        'habilidades': habilidades,
        'provincias': PROVINCIAS,
        'action': 'Cadastrar',
    })


@login_required
def detalhe(request, pk):
    v = get_object_or_404(Voluntario.objects.prefetch_related('habilidades', 'missoes'), pk=pk)
    missoes = v.missoes.order_by('-data_inicio')[:5]
    return render(request, 'voluntarios/detalhe.html', {'voluntario': v, 'missoes': missoes})


@login_required
def editar(request, pk):
    v = get_object_or_404(Voluntario, pk=pk)
    habilidades = Habilidade.objects.all()
    if request.method == 'POST':
        v.nome = request.POST.get('nome', v.nome).strip()
        v.telefone = request.POST.get('telefone', v.telefone).strip()
        v.email = request.POST.get('email', v.email).strip()
        v.provincia = request.POST.get('provincia', v.provincia)
        v.municipio = request.POST.get('municipio', v.municipio).strip()
        v.bairro = request.POST.get('bairro', v.bairro).strip()
        v.bio = request.POST.get('bio', v.bio).strip()
        v.disponibilidade = request.POST.get('disponibilidade', v.disponibilidade)
        lat = request.POST.get('latitude')
        lng = request.POST.get('longitude')
        if lat and lng:
            v.latitude, v.longitude = lat, lng
        if request.FILES.get('foto'):
            v.foto = request.FILES['foto']
        v.save()
        ids = request.POST.getlist('habilidades')
        v.habilidades.set(ids)
        messages.success(request, 'Perfil actualizado com sucesso!')
        return redirect('voluntarios_detalhe', pk=pk)
    return render(request, 'voluntarios/form.html', {
        'voluntario': v,
        'habilidades': habilidades,
        'provincias': PROVINCIAS,
        'action': 'Actualizar',
    })


@login_required
def atualizar_disponibilidade(request, pk):
    if request.method == 'POST':
        v = get_object_or_404(Voluntario, pk=pk)
        v.disponibilidade = request.POST.get('disponibilidade', v.disponibilidade)
        v.save()
        return JsonResponse({'ok': True, 'status': v.disponibilidade})
    return JsonResponse({'ok': False}, status=400)




def registar_publico(request):
    """Página pública para voluntários se cadastrarem — mobile-first."""
    habilidades = Habilidade.objects.all()
    if request.method == 'POST':
        try:
            v = Voluntario(
                nome=request.POST.get('nome', '').strip(),
                telefone=request.POST.get('telefone', '').strip(),
                email=request.POST.get('email', '').strip(),
                provincia=request.POST.get('provincia', ''),
                municipio=request.POST.get('municipio', '').strip(),
                bairro=request.POST.get('bairro', '').strip(),
                bio=request.POST.get('bio', '').strip(),
                numero_bi=request.POST.get('numero_bi', '').strip(),
                disponibilidade='disponivel',
            )
            lat = request.POST.get('latitude', '').strip()
            lng = request.POST.get('longitude', '').strip()
            if lat and lng:
                v.latitude, v.longitude = lat, lng
            if request.FILES.get('foto'):
                v.foto = request.FILES['foto']
            v.save()
            ids = request.POST.getlist('habilidades')
            if ids:
                v.habilidades.set(ids)
            return redirect('voluntario_sucesso')
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Erro ao cadastrar: {str(e)}')

    return render(request, 'voluntarios/registar_publico.html', {
        'habilidades': habilidades,
        'provincias': PROVINCIAS,
    })


def voluntario_sucesso(request):
    return render(request, 'voluntarios/voluntario_sucesso.html')