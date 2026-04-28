#!/bin/bash

echo "=== SocorroAO - Build Iniciando ==="

# Instalar dependências
pip install -r requirements.txt

echo "→ Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "→ Aplicando migrações..."
python manage.py migrate --noinput

echo "→ Build finalizado ==="

# Verificação para ajudar no debug
echo "→ Conteúdo da pasta staticfiles:"
ls -la staticfiles/ || echo "Pasta staticfiles não encontrada!"