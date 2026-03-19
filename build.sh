#!/usr/bin/env bash
# Script de build exécuté par Render à chaque déploiement
set -o errexit   # Arrêter si une commande échoue

echo "==> Installation des dépendances..."
pip install -r requirements.txt

echo "==> Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "==> Application des migrations..."
python manage.py migrate

echo "==> Build terminé ✓"
