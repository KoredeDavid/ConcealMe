web: gunicorn anonymous.wsgi --log-file -
web: python manage.py collectstatic --noinput
release: python manage.py migrate
