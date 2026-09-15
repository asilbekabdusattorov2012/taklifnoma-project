web: python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn bosh_sahifa.wsgi:application --bind 0.0.0.0:$PORT
