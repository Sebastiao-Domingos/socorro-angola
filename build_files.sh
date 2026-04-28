#!/bin/bash

echo "=== SocorroAO - Iniciando Build ==="

# Instalar dependências
pip install -r requirements.txt

echo "→ Coletando static files..."
python manage.py collectstatic --noinput --clear

echo "→ Aplicando migrações no banco..."
python manage.py migrate --noinput

echo "→ Build finalizado com sucesso ==="