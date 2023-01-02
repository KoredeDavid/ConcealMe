web: gunicorn anonymous.wsgi --log-file -
release: python manage.py migrate
release: python manage.py collectstatic --no-input

