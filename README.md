# 🆘 SocorroAO — Sistema Nacional de Coordenação de Voluntários em Desastres

Plataforma web Django para gestão de emergências humanitárias em Angola.

## Stack
- **Backend**: Django 5.0 + Python 3.12
- **Frontend**: Tailwind CSS (CDN) + Vanilla JS + Leaflet.js
- **Database**: SQLite (dev) → PostgreSQL/Render (prod)
- **Deploy**: Vercel (app) + Render (DB)
- **Auth**: Django Auth nativo

## Funcionalidades
- 🗺️ Mapa global de incidentes e centrais de doação (Leaflet.js)
- 🚨 Gestão completa de incidentes (CRUD + ciclo de vida)
- ✅ Checklists operacionais automáticas por tipo de desastre
- 👥 Banco de voluntários com habilidades e geolocalização
- 🤝 Alocação e matching de voluntários a incidentes
- 📦 Centrais de doação georreferenciadas com controlo de capacidade
- 📊 Relatórios pós-intervenção
- 🌍 Multilíngue: Português · English · Français
- 🌓 Tema claro / escuro
- 📱 100% responsivo

## Instalação Local
```bash
git clone https://github.com/seu-user/socorroao.git
cd socorroao
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # editar com as suas variáveis
python manage.py migrate
python manage.py shell < scripts/seed.py
python manage.py runserver
```

## Deploy Vercel + Render

### 1. Render (PostgreSQL)
1. Crie um novo **PostgreSQL** database no Render
2. Copie a `DATABASE_URL` gerada

### 2. Variáveis de ambiente (Vercel)
```
SECRET_KEY=<gerar com python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
DEBUG=False
ALLOWED_HOSTS=seu-app.vercel.app,localhost
DATABASE_URL=postgresql://user:pass@host:5432/dbname
DJANGO_SETTINGS_MODULE=config.settings
```

### 3. Deploy Vercel
```bash
npm i -g vercel
vercel --prod
```

## Credenciais de Demo
- **Admin**: admin / admin123
- **Coordenador**: coord1 / coord123
- **Admin Django**: /admin/

## Estrutura
```
socorroao/
├── config/          # Settings, URLs, WSGI
├── core/            # Dashboard, Home, Mapa, Login
├── voluntarios/     # Gestão de voluntários
├── incidentes/      # Incidentes, Checklists, Relatórios
├── doacoes/         # Centrais de doação
├── templates/       # HTML templates
├── static/          # CSS, JS, imagens
├── scripts/         # seed.py
├── vercel.json      # Config Vercel
├── Procfile         # Config Render/Gunicorn
└── requirements.txt
```

---
*© 2025 SocorroAO — República de Angola 🇦🇴*
