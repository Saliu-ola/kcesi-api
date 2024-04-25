#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip
/opt/render/project/src/.venv/bin/python3.7 -m pip install --upgrade pip

# Use pip to upgrade requirements
pip install --upgrade -r requirements.txt


python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate
python manage.py dumpdata --exclude=contenttypes > fixture.json


# # Debugging: Echo environment variables
# echo "DJANGO_SUPERUSER_USERNAME: $DJANGO_SUPERUSER_USERNAME"
# echo "DJANGO_SUPERUSER_EMAIL: $DJANGO_SUPERUSER_EMAIL"
# echo "DJANGO_SUPERUSER_PASSWORD: $DJANGO_SUPERUSER_PASSWORD"

# # Create superuser
# DJANGO_SUPERUSER_PASSWORD="$DJANGO_SUPERUSER_PASSWORD" python manage.py createsuperuser --noinput --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL"

