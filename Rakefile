require 'rake'

APP_DIR = 'app'
PROCESS_WORKERS = 2
HTTP_TIMEOUT = 30
USE_NEWRELIC = {
  web: true,
  background: false
}
NEWRELIC_CMD = 'newrelic-admin run-program '

task default: [:env]

task :env do
  sh 'env'
end

task :deploy do
  Dir.chdir(APP_DIR) do
    # sh 'python manage.py clear_cache'
    sh 'python manage.py migrate'
    sh 'python manage.py bower_install -- --config.interactive=false'
    sh 'python manage.py collectstatic --noinput'
    sh 'python manage.py clean_compress'
    sh 'python manage.py compress'
    sh 'python manage.py cloudflare_load'
  end
end

task :uwsgi do
  cmd = 'uwsgi --module=app.wsgi:application --http-keepalive=0 --master --processes=%{workers} --harakiri=%{timeout} --vacuum --single-interpreter --enable-threads --http :%{port}'

  cmd = cmd % {
    workers: PROCESS_WORKERS,
    timeout: HTTP_TIMEOUT,
    port: ENV['PORT'] || 8000
  }

  cmd = NEWRELIC_CMD + cmd if USE_NEWRELIC[:web]
  Dir.chdir(APP_DIR) do
    sh cmd
  end
end

task :gunicorn do
  cmd = 'gunicorn app.wsgi:application --keep-alive=0 --workers=%{workers} --timeout=%{timeout} --preload --access-logfile=- --error-logfile=- --bind=:%{port}'

  cmd = cmd % {
    workers: PROCESS_WORKERS,
    timeout: HTTP_TIMEOUT,
    port: ENV['PORT'] || 8000
  }

  cmd = NEWRELIC_CMD + cmd if USE_NEWRELIC[:web]

  Dir.chdir(APP_DIR) do
    sh cmd
  end
end

task :sqs do
  cmd = 'python manage.py sqs'

  cmd = NEWRELIC_CMD + cmd if USE_NEWRELIC[:background]

  Dir.chdir(APP_DIR) do
    sh cmd
  end
end

task :celery_broker do
  cmd = 'celery -A app worker -c %{workers} -B'

  workers = PROCESS_WORKERS - 1 if PROCESS_WORKERS > 1

  cmd = cmd % {
    workers: workers
  }

  cmd = NEWRELIC_CMD + cmd if USE_NEWRELIC[:background]

  Dir.chdir(APP_DIR) do
    sh cmd
  end
end

task :celery_worker do
  cmd = 'celery -A app worker -c %{workers}'

  cmd = cmd % {
    workers: PROCESS_WORKERS
  }

  cmd = NEWRELIC_CMD + cmd if USE_NEWRELIC[:background]

  Dir.chdir(APP_DIR) do
    sh cmd
  end
end
