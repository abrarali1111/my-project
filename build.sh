#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# --- HARD RESET & MIGRATE ---
# Only reset DB if needed, but for now we keep it to ensure fresh start with new models
rm -f db.sqlite3

# Run migrations
python manage.py migrate

# Create the specific superuser 'abrar'
python manage.py shell <<EOF
from django.contrib.auth.models import User
import os

username = 'abrar'
email = 'abrar@example.com'
password = 'Wellcom3'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser '{username}' created successfully!")
else:
    print(f"Superuser '{username}' already exists.")
EOF

# Collect static files
python manage.py collectstatic --no-input
