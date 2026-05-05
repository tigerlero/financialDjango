#!/bin/sh

# Wait for database to be ready
echo "Waiting for database..."
while ! pg_isready -h $(echo $DATABASE_URL | sed 's|.*@\(.*\):.*|\1|') -p $(echo $DATABASE_URL | sed 's|.*:\([0-9]*\)/.*|\1|') -U $(echo $DATABASE_URL | sed 's|.*//\(.*\):.*@.*|\1|') 2>/dev/null; do
    echo "Database is unavailable - sleeping"
    sleep 2
done

echo "Database is ready!"

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start gunicorn
exec gunicorn --bind 0.0.0.0:8000 financeapp.wsgi:application
