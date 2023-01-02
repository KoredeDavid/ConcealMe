web: gunicorn anonymous.wsgi --log-file -
web: python manage.py collectstatic --no-input
release: python manage.py migrate

