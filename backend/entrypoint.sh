#!/bin/sh

echo "Collect static files"
python manage.py collectstatic --no-input

cp -r /app/collected_static/. /app/backend_static/static/

python manage.py makemigrations foodgram --no-input
python manage.py makemigrations users --no-input

echo "Apply database migrations"
python manage.py migrate --no-input

echo "Add data to database"
python manage.py scv_script

echo "Starting server"
gunicorn backend.wsgi:application --bind 0.0.0.0:8000