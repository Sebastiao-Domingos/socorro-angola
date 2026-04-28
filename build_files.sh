#!/bin/bash

echo "=== SocorroAO - Build Iniciando ==="

# Instala as dependências
pip install -r requirements.txt

echo "→ Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "→ Aplicando as migrações do banco..."
python manage.py migrate --noinput

echo "→ Verificando se a pasta staticfiles foi criada:"
ls -la staticfiles/ || echo "❌ Pasta staticfiles não encontrada!"

echo "=== Build finalizado ==="