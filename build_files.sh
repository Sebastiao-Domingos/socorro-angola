#!/bin/bash

echo "=== SocorroAO Build Script ==="

# Instala as dependências
pip install -r requirements.txt

# Coleta arquivos estáticos
python manage.py collectstatic --noinput --clear

# Aplica as migrações no banco de produção
python manage.py migrate --noinput

# (Opcional) Seed inicial - remova o --noinput se não for necessário
echo "=== Executando seed ==="
python manage.py shell < scripts/seed.py || echo "Seed finalizado ou não encontrou arquivo."

echo "=== Build complete ==="