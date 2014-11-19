web: newrelic-admin run-program uwsgi --module=application.core:app --master --processes=2 --harakiri=30 --vacuum --single-interpreter --enable-threads --http :$PORT
celery_broker: newrelic-admin run-program celery -A application.core.celery worker -c 2 -B -l INFO
celery_wroker: newrelic-admin run-program celery -A application.core.celery worker -c 2 -l INFO
