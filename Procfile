web: gunicorn application.core:app.wsgi_app --workers=5 -b 0.0.0.0:$PORT --preload --access-logfile=- --error-logfile=- --max-requests=10000 --keep-alive=0
