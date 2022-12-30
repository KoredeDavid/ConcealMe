web: gunicorn anonymous.wsgi --log-file -
release: python manage.py collectstatic --noinput
release: python manage.py migrate
