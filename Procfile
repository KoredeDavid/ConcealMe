web: gunicorn anonymous.wsgi --log-file -
release: python manage.py migrate && python manage.py collectstatic --no-input

