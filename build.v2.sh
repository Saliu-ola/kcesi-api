#!/usr/bin/env bash
# exit on error
set -o errexit

# Activate virtual environment
source /opt/render/project/src/.venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install python-dotenv
pip install python-dotenv

# Use pip to upgrade requirements
pip install --upgrade -r requirements.txt

# Collect static files
python3.7 manage.py collectstatic --no-input

# Make database migrations
python3.7 manage.py makemigrations

# Apply database migrations
python3.7 manage.py migrate

# Dump data (excluding contenttypes) to fixture.json
# python3.7 manage.py dumpdata --exclude=contenttypes > fixture.json

# Debugging: Echo environment variables
# echo "DJANGO_SUPERUSER_USERNAME: $DJANGO_SUPERUSER_USERNAME"
# echo "DJANGO_SUPERUSER_EMAIL: $DJANGO_SUPERUSER_EMAIL"
# echo "DJANGO_SUPERUSER_PASSWORD: $DJANGO_SUPERUSER_PASSWORD"

# Create superuser if environment variables are provided
# if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
#     DJANGO_SUPERUSER_PASSWORD="$DJANGO_SUPERUSER_PASSWORD" python3.7 manage.py createsuperuser --noinput --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL"
# fi

# Deactivate virtual environment
deactivate
