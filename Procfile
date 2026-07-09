release: . /app/.venv/bin/activate && python manage.py migrate --noinput
web: . /app/.venv/bin/activate && python manage.py collectstatic --noinput && gunicorn biznex.wsgi --log-file - --bind 0.0.0.0:$PORT
