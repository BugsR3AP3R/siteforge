#!/usr/bin/env bash
set -o errexit

echo "==> Installation des dépendances..."
pip install -r requirements.txt

echo "==> Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "==> Création des migrations..."
python manage.py makemigrations accounts
python manage.py makemigrations billing
python manage.py makemigrations builder
python manage.py makemigrations dashboard

echo "==> Application des migrations..."
python manage.py migrate

echo "==> Création du superuser (si inexistant)..."
python manage.py shell -c "
from accounts.models import User
import os
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')
if email and password and not User.objects.filter(email=email).exists():
    User.objects.create_superuser(username=email, email=email, password=password)
    print('Superuser créé :', email)
else:
    print('Superuser déjà existant ou variables manquantes.')
"

echo "==> Build terminé ✓"
