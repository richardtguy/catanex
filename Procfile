release: flask db upgrade
web: gunicorn -k flask_sockets.worker app:app
