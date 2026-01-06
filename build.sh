#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# --- HARD RESET & MIGRATE ---
# Remove db.sqlite3 if it exists (force fresh start)
rm -f db.sqlite3

# Run migrations
python manage.py migrate

# Create a default superuser (so you can login immediately)
# Only runs if user doesn't exist
python manage.py shell <<EOF
from django.contrib.auth.models import User
import os
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser '{username}' created.")
else:
    print(f"Superuser '{username}' already exists.")
EOF

# Collect static files
python manage.py collectstatic --no-input
