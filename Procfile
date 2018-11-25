release: flask db upgrade
web: gunicorn --worker-class flask_sockets.worker -w 1 app:app
