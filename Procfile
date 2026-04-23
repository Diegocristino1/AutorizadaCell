release: python manage.py migrate --noinput
web: gunicorn loja_celulares.wsgi:application --bind 0.0.0.0:${PORT}
