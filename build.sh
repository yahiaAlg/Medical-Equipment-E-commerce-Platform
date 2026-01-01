#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate

# Seed all data
python manage.py seed_all

# Create admin superuser
python manage.py create_admin_user