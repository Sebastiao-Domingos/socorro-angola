#!/bin/bash
echo "=== SocorroAO Build Script ==="
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
echo "=== Build complete ==="
