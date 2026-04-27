"""
SocorroAO — Seed de dados realistas de Angola
Executa com: python manage.py shell < scripts/seed.py
"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.contrib.auth.models import User
from voluntarios.models import Habilidade, Voluntario
from incidentes.models import Incidente, ChecklistItem, CHECKLIST_PADRAO
from doacoes.models import CentralDoacao, Doacao
from django.utils import timezone
from datetime import timedelta
import random

print("🌱 A criar dados de demonstração SocorroAO...")

# ── Superuser ──────────────────────────────────────────────────────────────
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@socorroao.ao', 'admin123')
    admin.first_name = 'Administrador'
    admin.last_name = 'SocorroAO'
    admin.save()
    print("✅ Superuser criado: admin / admin123")

coord = User.objects.create_user('coord1', 'coord@socorroao.ao', 'coord123',
    first_name='Maria', last_name='Silva') if not User.objects.filter(username='coord1').exists() else User.objects.get(username='coord1')

# ── Habilidades ────────────────────────────────────────────────────────────
habs_data = [
    ('Primeiros Socorros', 'saude', '🏥'), ('Enfermagem', 'saude', '💉'),
    ('Medicina Geral', 'saude', '⚕️'), ('Saúde Mental', 'saude', '🧠'),
    ('Condução de Veículos Pesados', 'logistica', '🚛'), ('Gestão de Armazéns', 'logistica', '📦'),
    ('Coordenação Logística', 'logistica', '🗂️'), ('Engenharia Civil', 'engenharia', '🏗️'),
    ('Electrotecnia', 'engenharia', '⚡'), ('Cozinha Colectiva', 'alimentacao', '🍳'),
    ('Distribuição de Alimentos', 'alimentacao', '🥫'), ('Comunicação de Rádio', 'comunicacao', '📡'),
    ('Redes Sociais', 'comunicacao', '📱'), ('Educação Básica', 'educacao', '📚'),
    ('Segurança e Protecção', 'seguranca', '🛡️'), ('Psicologia de Emergência', 'psicologia', '💬'),
]
habs = {}
for nome, cat, icone in habs_data:
    h, _ = Habilidade.objects.get_or_create(nome=nome, defaults={'categoria': cat, 'icone': icone})
    habs[nome] = h
print(f"✅ {len(habs)} habilidades criadas")

# ── Voluntários ────────────────────────────────────────────────────────────
voluntarios_data = [
    ('Ana Paula Neto', '+244 923 456 789', 'ana.paula@email.ao', 'luanda', 'Cazenga', -8.8167, 13.2667, ['Primeiros Socorros', 'Enfermagem'], 12),
    ('João Carlos Lopes', '+244 912 345 678', 'joao.lopes@email.ao', 'luanda', 'Viana', -8.9042, 13.3742, ['Condução de Veículos Pesados', 'Gestão de Armazéns'], 8),
    ('Maria Conceição', '+244 934 567 890', 'maria.c@email.ao', 'benguela', 'Lobito', -12.3486, 13.5456, ['Cozinha Colectiva', 'Distribuição de Alimentos'], 5),
    ('António Sebastião', '+244 945 678 901', 'antonio.s@email.ao', 'huila', 'Lubango', -14.9177, 13.4924, ['Engenharia Civil', 'Electrotecnia'], 15),
    ('Fernanda Dias', '+244 956 789 012', 'fernanda.d@email.ao', 'luanda', 'Samba', -8.8383, 13.2344, ['Comunicação de Rádio', 'Redes Sociais'], 3),
    ('Pedro Manuel Gomes', '+244 967 890 123', 'pedro.gomes@email.ao', 'malanje', 'Malanje', -9.5399, 16.3409, ['Primeiros Socorros', 'Segurança e Protecção'], 7),
    ('Rosa Teixeira', '+244 978 901 234', 'rosa.t@email.ao', 'benguela', 'Benguela', -12.5763, 13.4055, ['Medicina Geral', 'Saúde Mental'], 20),
    ('Carlos Filipe Santos', '+244 989 012 345', 'carlos.f@email.ao', 'luanda', 'Cacuaco', -8.7800, 13.3667, ['Gestão de Armazéns', 'Coordenação Logística'], 9),
    ('Luciana Ferreira', '+244 923 111 222', 'luciana.f@email.ao', 'huambo', 'Huambo', -12.7757, 15.7396, ['Educação Básica', 'Psicologia de Emergência'], 4),
    ('Marcos Augusto', '+244 912 222 333', 'marcos.a@email.ao', 'cabinda', 'Cabinda', -5.5500, 12.1947, ['Primeiros Socorros', 'Comunicação de Rádio'], 6),
    ('Sofia Baptista', '+244 934 333 444', 'sofia.b@email.ao', 'luanda', 'Rangel', -8.8500, 13.2333, ['Enfermagem', 'Saúde Mental'], 11),
    ('Domingos Correia', '+244 945 444 555', 'domingos.c@email.ao', 'uige', 'Uíge', -7.6167, 15.0667, ['Engenharia Civil', 'Condução de Veículos Pesados'], 2),
]

vols = []
disps = ['disponivel', 'disponivel', 'disponivel', 'ocupado', 'disponivel']
for i, (nome, tel, email, prov, mun, lat, lng, hab_names, missoes) in enumerate(voluntarios_data):
    v, created = Voluntario.objects.get_or_create(email=email, defaults={
        'nome': nome, 'telefone': tel, 'provincia': prov, 'municipio': mun,
        'latitude': lat, 'longitude': lng, 'missoes_completadas': missoes,
        'disponibilidade': disps[i % len(disps)], 'verificado': i < 8,
        'bio': f'Voluntário dedicado em {mun}, com experiência em situações de emergência.',
    })
    if created:
        v.habilidades.set([habs[h] for h in hab_names if h in habs])
    vols.append(v)
print(f"✅ {len(vols)} voluntários criados")

# ── Incidentes ─────────────────────────────────────────────────────────────
now = timezone.now()
incidentes_data = [
    {
        'titulo': 'Enchente no Bairro Palanca — Cazenga',
        'descricao': 'Chuvas intensas causaram inundação de mais de 200 habitações no bairro Palanca. Famílias deslocadas necessitam de abrigo e alimentação urgentes. Infraestrutura de saneamento comprometida.',
        'tipo': 'enchente', 'severidade': 'critico', 'status': 'ativo',
        'provincia': 'Luanda', 'municipio': 'Cazenga', 'bairro': 'Palanca',
        'latitude': -8.8167, 'longitude': 13.2667, 'pessoas_afetadas': 1250, 'vol_nec': 15,
        'data_offset': -2,
    },
    {
        'titulo': 'Deslizamento de Terra — Samba',
        'descricao': 'Após chuvas torrenciais, deslizamento de terra soterrou parcialmente 8 residências na encosta do Bairro Mabor. Há relatos de 3 desaparecidos. Acesso difícil por destruição de via.',
        'tipo': 'deslizamento', 'severidade': 'critico', 'status': 'em_atendimento',
        'provincia': 'Luanda', 'municipio': 'Samba', 'bairro': 'Mabor',
        'latitude': -8.8700, 'longitude': 13.2100, 'pessoas_afetadas': 85, 'vol_nec': 10,
        'data_offset': -1,
    },
    {
        'titulo': 'Seca Prolongada — Kunene',
        'descricao': 'Quinto mês consecutivo sem chuvas na região sul. Reservatórios de água secos. Comunidades rurais com severa escassez de água e alimentos. Gado morrendo em grande quantidade.',
        'tipo': 'seca', 'severidade': 'critico', 'status': 'em_atendimento',
        'provincia': 'Cunene', 'municipio': 'Ombadja', 'bairro': '',
        'latitude': -17.0767, 'longitude': 15.7300, 'pessoas_afetadas': 4800, 'vol_nec': 20,
        'data_offset': -14,
    },
    {
        'titulo': 'Incêndio em Mercado Informal — Sambizanga',
        'descricao': 'Incêndio de origem desconhecida destruiu parte do mercado informal. Estima-se 40 bancas afectadas. Comerciantes perderam toda a mercadoria. Sem vítimas mortais reportadas.',
        'tipo': 'incendio', 'severidade': 'medio', 'status': 'em_atendimento',
        'provincia': 'Luanda', 'municipio': 'Sambizanga', 'bairro': 'Mercado 30',
        'latitude': -8.8233, 'longitude': 13.2389, 'pessoas_afetadas': 200, 'vol_nec': 6,
        'data_offset': -3,
    },
    {
        'titulo': 'Acidente Rodoviário em Massa — EN-100',
        'descricao': 'Colisão entre autocarro e camião na EN-100 entre Luanda e Malanje. 23 feridos, 4 em estado grave. Necessidade urgente de evacuação médica e apoio aos familiares.',
        'tipo': 'acidente', 'severidade': 'critico', 'status': 'resolvido',
        'provincia': 'Malanje', 'municipio': 'Caculama', 'bairro': '',
        'latitude': -9.2833, 'longitude': 15.2500, 'pessoas_afetadas': 27, 'vol_nec': 8,
        'data_offset': -5,
    },
    {
        'titulo': 'Surto de Cólera — Margem do Rio Bengo',
        'descricao': 'Confirmados 35 casos de cólera em comunidades ribeirinhas. Fonte: consumo de água contaminada do Rio Bengo. MINSA activado. Necessidade de kits de purificação e medicação.',
        'tipo': 'epidemia', 'severidade': 'medio', 'status': 'monitoramento',
        'provincia': 'Luanda', 'municipio': 'Cacuaco', 'bairro': 'Funda',
        'latitude': -8.7500, 'longitude': 13.3500, 'pessoas_afetadas': 180, 'vol_nec': 12,
        'data_offset': -7,
    },
    {
        'titulo': 'Deslocamento por Conflito — Moxico',
        'descricao': 'Famílias deslocadas de aldeias remotas por tensões locais. Chegaram 120 famílias à sede municipal sem recursos. Necessidade de abrigo, alimentação e documentação.',
        'tipo': 'deslocamento', 'severidade': 'medio', 'status': 'ativo',
        'provincia': 'Moxico', 'municipio': 'Luena', 'bairro': '',
        'latitude': -11.7833, 'longitude': 19.9167, 'pessoas_afetadas': 650, 'vol_nec': 10,
        'data_offset': -4,
    },
    {
        'titulo': 'Inundação Urbana — Viana',
        'descricao': 'Sistema de drenagem sobrecarregado após chuva de 3 horas. Bairros Km 30 e Km 35 com ruas alagadas. Veículos presos. Famílias com água dentro de casa até 50cm.',
        'tipo': 'enchente', 'severidade': 'baixo', 'status': 'resolvido',
        'provincia': 'Luanda', 'municipio': 'Viana', 'bairro': 'Km 30',
        'latitude': -8.9042, 'longitude': 13.3742, 'pessoas_afetadas': 320, 'vol_nec': 5,
        'data_offset': -9,
    },
]

incs = []
for d in incidentes_data:
    inc, created = Incidente.objects.get_or_create(titulo=d['titulo'], defaults={
        'descricao': d['descricao'], 'tipo': d['tipo'],
        'severidade': d['severidade'], 'status': d['status'],
        'provincia': d['provincia'], 'municipio': d['municipio'],
        'bairro': d.get('bairro', ''), 'latitude': d['latitude'], 'longitude': d['longitude'],
        'pessoas_afetadas': d['pessoas_afetadas'], 'voluntarios_necessarios': d['vol_nec'],
        'reportado_por': coord,
    })
    if created:
        # Override the auto date
        Incidente.objects.filter(pk=inc.pk).update(
            data_inicio=now + timedelta(days=d['data_offset'])
        )
        # Allocate some volunteers
        num_vol = random.randint(1, min(4, len(vols)))
        for v in random.sample(vols, num_vol):
            inc.voluntarios_alocados.add(v)
        # Create checklist
        items = CHECKLIST_PADRAO.get(d['tipo'], [])
        done_count = random.randint(0, len(items))
        for i, item in enumerate(items):
            ChecklistItem.objects.create(
                incidente=inc, descricao=item, ordem=i,
                concluido=(i < done_count)
            )
        if d['status'] == 'resolvido':
            Incidente.objects.filter(pk=inc.pk).update(data_resolucao=now + timedelta(days=d['data_offset']+1))
    incs.append(inc)
print(f"✅ {len(incs)} incidentes criados")

# ── Centrais de Doação ─────────────────────────────────────────────────────
centrais_data = [
    {
        'nome': 'Central de Doações do Cazenga', 'tipo': 'geral',
        'provincia': 'Luanda', 'municipio': 'Cazenga',
        'endereco': 'Rua 22 de Março, nº 45, Bairro Hoji Ya Henda', 'responsavel': 'Engª. Filomena Antunes',
        'telefone': '+244 923 100 200', 'email': 'central.cazenga@gmail.com',
        'horario': 'Seg–Sáb 07h–19h', 'status': 'ativo',
        'cap_total': 2000, 'cap_atual': 1340,
        'lat': -8.8167, 'lng': 13.2667,
        'descricao': 'Central principal de apoio à enchente no Cazenga. Aceita água, alimentos e roupas.',
    },
    {
        'nome': 'Ponto de Apoio Sambizanga', 'tipo': 'alimentos',
        'provincia': 'Luanda', 'municipio': 'Sambizanga',
        'endereco': 'Av. Ho Chi Min, junto ao Mercado do Povo', 'responsavel': 'Sr. Raimundo Cosme',
        'telefone': '+244 912 300 400', 'email': '',
        'horario': 'Diariamente 08h–17h', 'status': 'ativo',
        'cap_total': 800, 'cap_atual': 210,
        'lat': -8.8233, 'lng': 13.2389,
        'descricao': 'Especializado em alimentos não perecíveis e géneros alimentares básicos.',
    },
    {
        'nome': 'Central Humanitária de Benguela', 'tipo': 'geral',
        'provincia': 'Benguela', 'municipio': 'Benguela',
        'endereco': 'Rua da SONANGOL, nº 12, Centro', 'responsavel': 'Dra. Helena Brito',
        'telefone': '+244 934 500 600', 'email': 'central.benguela@socorro.ao',
        'horario': 'Seg–Sex 08h–17h, Sáb 08h–12h', 'status': 'ativo',
        'cap_total': 1500, 'cap_atual': 650,
        'lat': -12.5763, 'lng': 13.4055,
        'descricao': 'Central regional para toda a província de Benguela.',
    },
    {
        'nome': 'Ponto Médico de Emergência — Cacuaco', 'tipo': 'medicamentos',
        'provincia': 'Luanda', 'municipio': 'Cacuaco',
        'endereco': 'Junto ao Hospital Municipal de Cacuaco', 'responsavel': 'Enf. João Paulo Mota',
        'telefone': '+244 945 600 700', 'email': '',
        'horario': '24h/7 dias', 'status': 'ativo',
        'cap_total': 500, 'cap_atual': 380,
        'lat': -8.7800, 'lng': 13.3667,
        'descricao': 'Medicamentos, material de primeiros socorros e EPIs. Exclusivo para equipas médicas.',
    },
    {
        'nome': 'Central Sul — Lubango', 'tipo': 'agua',
        'provincia': 'Huíla', 'municipio': 'Lubango',
        'endereco': 'Bairro Shoprite, Rua dos Eucaliptos', 'responsavel': 'Sra. Ângela Vieira',
        'telefone': '+244 956 700 800', 'email': 'sul.lubango@gmail.com',
        'horario': 'Seg–Sáb 06h–20h', 'status': 'ativo',
        'cap_total': 3000, 'cap_atual': 420,
        'lat': -14.9177, 'lng': 13.4924,
        'descricao': 'Central de água potável para apoio à seca no sul de Angola.',
    },
    {
        'nome': 'Armazém de Roupas — Viana', 'tipo': 'roupas',
        'provincia': 'Luanda', 'municipio': 'Viana',
        'endereco': 'Km 30, Complexo Industrial da Viana, Galpão B2', 'responsavel': 'Sr. Osvaldo Mendes',
        'telefone': '+244 967 800 900', 'email': '',
        'horario': 'Seg–Sex 09h–16h', 'status': 'cheio',
        'cap_total': 1200, 'cap_atual': 1200,
        'lat': -8.9100, 'lng': 13.3900,
        'descricao': 'Roupas para todas as idades. Actualmente cheio — aguarda distribuição.',
    },
]

cents = []
for d in centrais_data:
    c, created = CentralDoacao.objects.get_or_create(nome=d['nome'], defaults={
        'tipo': d['tipo'], 'provincia': d['provincia'], 'municipio': d['municipio'],
        'endereco': d['endereco'], 'responsavel': d['responsavel'],
        'telefone': d['telefone'], 'email': d['email'], 'horario': d['horario'],
        'status': d['status'], 'capacidade_total': d['cap_total'],
        'capacidade_atual': d['cap_atual'], 'latitude': d['lat'],
        'longitude': d['lng'], 'descricao': d['descricao'],
    })
    cents.append(c)
print(f"✅ {len(cents)} centrais de doação criadas")

# ── Doações ────────────────────────────────────────────────────────────────
doacoes_sample = [
    (cents[0], 'Carlos Mendonça', 'alimentos', '50 sacos de arroz (5kg cada)', 50, 'sacos'),
    (cents[0], 'Igreja Evangélica do Cazenga', 'agua', 'Bidões de água 20L', 100, 'bidões'),
    (cents[0], 'Empresa TotalEnergies AO', 'alimentos', 'Kits alimentares completos', 200, 'kits'),
    (cents[1], 'Família Rodrigues', 'alimentos', 'Feijão, massa e azeite', 30, 'pacotes'),
    (cents[2], 'Comunidade Portuguesa de Benguela', 'roupas', 'Roupas de inverno diversas', 500, 'peças'),
    (cents[3], 'MINSA — Doação institucional', 'medicamentos', 'Antibióticos, analgésicos e soro', 300, 'unidades'),
    (cents[4], 'Empresa SONANGOL', 'agua', 'Camiões cisterna de água potável', 5, 'camiões'),
    (cents[0], 'Anónimo', 'outro', 'Kits de higiene pessoal', 150, 'kits'),
]
for central, doador, cat, desc, qtd, unid in doacoes_sample:
    if not Doacao.objects.filter(central=central, descricao=desc).exists():
        Doacao.objects.create(
            central=central, doador_nome=doador,
            doador_anonimo=(doador == 'Anónimo'),
            categoria=cat, descricao=desc,
            quantidade=qtd, unidade=unid, entregue=True,
        )
print(f"✅ Doações de exemplo criadas")

print("\n" + "="*55)
print("🎉 Seed completo! SocorroAO está pronto.")
print("="*55)
print("  🔑 Login: admin / admin123")
print("  🔑 Coord: coord1 / coord123")
print("  📍 URL: http://127.0.0.1:8000/")
print("  🔧 Admin: http://127.0.0.1:8000/admin/")
print("="*55)
