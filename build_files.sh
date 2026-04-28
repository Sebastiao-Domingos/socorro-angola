#!/bin/bash
echo "=== SocorroAO Build Script ==="
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py shell < scripts/seed.py
echo "=== Build complete ==="
