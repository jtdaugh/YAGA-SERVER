web: newrelic-admin run-program uwsgi --module=application.core:app --master --processes=5 --harakiri=30 --vacuum --single-interpreter --enable-threads --http :$PORT
