# #!/usr/bin/env bash
# # Exit on error
# set -o errexit

# # Modify this line as needed for your package manager (pip, poetry, etc.)
# pip install -r requirements.txt
# pip install -U 'channels[daphne]' channels-redis

# # Convert static asset files
# python manage.py collectstatic --no-input

# # Apply any outstanding database migrations
# python manage.py migrate


#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install system dependencies
apt-get update
apt-get install -y build-essential python3-dev libffi-dev libssl-dev

# Install Python dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -U 'channels[daphne]' channels-redis

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate
