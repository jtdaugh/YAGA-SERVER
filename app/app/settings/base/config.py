from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import os

import closure
import yuicompressor
from configurations import Configuration
from django.utils import six
from django.utils.translation import ugettext_lazy as _


class InvalidTemplateObjectException(
    Exception
):
    pass


class InvalidTemplateObject(
    object
):
    def __mod__(self, missing):
        raise InvalidTemplateObjectException(missing)

    def __contains__(self, search):
        if search == '%s':
            return True

        return False


class BaseConfiguration(
    Configuration
):
    # -------------------------------------------------------
    # debug mode configuration
    # -------------------------------------------------------
    DEBUG = True
    # -------------------------------------------------------
    # https configuration
    # -------------------------------------------------------
    HTTPS = False
    # -------------------------------------------------------
    # django compressor configuration
    # -------------------------------------------------------
    COMPRESS_OFFLINE = False
    COMPRESS_ENABLED = False
    # -------------------------------------------------------
    # template cache configuration
    # -------------------------------------------------------
    TEMPLATE_CACHE = False
    # -------------------------------------------------------
    # etag configuration
    # -------------------------------------------------------
    USE_ETAGS = False
    # -------------------------------------------------------
    # gzip configuration
    # -------------------------------------------------------
    GZIP = False
    # -------------------------------------------------------
    # global permissions configuration
    # -------------------------------------------------------
    GLOBAL_PERMISSIONS = [
    ]
    # -------------------------------------------------------
    # debug toolbar configuration
    # -------------------------------------------------------
    DEBUG_TOOLBAR = True
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': 'app.utils.show_toolbar'
    }
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'debug_toolbar.panels.versions.VersionsPanel',
    ]
    # -------------------------------------------------------
    # docs configuration
    # -------------------------------------------------------
    USE_DOCS = True
    # -------------------------------------------------------
    # domain configuration
    # -------------------------------------------------------
    APPEND_SLASH = False
    PREPEND_WWW = False
    # -------------------------------------------------------
    # crispy forms configuration
    # -------------------------------------------------------
    CRISPY_FAIL_SILENTLY = False
    CRISPY_TEMPLATE_PACK = 'bootstrap3'
    # -------------------------------------------------------
    # app features configuration
    # -------------------------------------------------------
    # project root configuration
    # -------------------------------------------------------
    PROJECT_ROOT = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        '..',
        '..'
    ))
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    # -------------------------------------------------------
    # local cache configuration
    # -------------------------------------------------------
    VIEW_CACHE = False
    VIEW_CACHE_TIMEOUT = 60 * 60  # one hour
    # -------------------------------------------------------
    # internal ips configuration
    # -------------------------------------------------------
    INTERNAL_IPS = ['127.0.0.1']
    # -------------------------------------------------------
    # action configuration
    # -------------------------------------------------------
    DISABLE_DELETE_SELECTED = True
    # -------------------------------------------------------
    # hosts configuration
    # -------------------------------------------------------
    ALLOWED_HOSTS = ['127.0.0.1']
    USE_X_FORWARDED_HOST = False
    BEHIND_PROXY = False
    # -------------------------------------------------------
    # database configuration
    # -------------------------------------------------------
    DATABASES = {
        'default': {
            'ENGINE': 'transaction_hooks.backends.postgresql_psycopg2',
            'NAME': 'app',
            # 'ENGINE': 'transaction_hooks.backends.sqlite3',
            # 'NAME': os.path.abspath(
            #     os.path.join(PROJECT_ROOT, 'app.sqlite')
            # ),
            'ATOMIC_REQUESTS': True,
            'AUTOCOMMIT': True,
            'CONN_MAX_AGE': None
        }
    }
    # -------------------------------------------------------
    # cache configuration
    # -------------------------------------------------------
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': os.path.abspath(os.path.join(PROJECT_ROOT, 'cache'))
        }
    }
    # CACHES = {
    #     'default': {
    #         'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    #     }
    # }
    # -------------------------------------------------------
    # sessions\message configuration
    # -------------------------------------------------------
    # SESSION_ENGINE = 'django.contrib.sessions.backends.file'
    # SESSION_FILE_PATH = os.path.abspath(
    #      os.path.join(PROJECT_ROOT, 'sessions')
    # )
    MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
    SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
    # SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
    # SESSION_SERIALIZER = 'redis_sessions_fork.serializers.UjsonSerializer'
    SESSION_SAVE_EVERY_REQUEST = False
    # -------------------------------------------------------
    # cookies configuration
    # -------------------------------------------------------
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_DOMAIN = '127.0.0.1'
    CSRF_COOKIE_DOMAIN = '127.0.0.1'
    # -------------------------------------------------------
    # in memory file upload handler configuration
    # -------------------------------------------------------
    FILE_UPLOAD_HANDLERS = (
        'django.core.files.uploadhandler.MemoryFileUploadHandler',
    )
    FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600
    # -------------------------------------------------------
    # password hashers configuration
    # -------------------------------------------------------
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
        'django.contrib.auth.hashers.BCryptPasswordHasher',
        'django.contrib.auth.hashers.PBKDF2PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
        'django.contrib.auth.hashers.SHA1PasswordHasher',
        'django.contrib.auth.hashers.MD5PasswordHasher',
        'django.contrib.auth.hashers.CryptPasswordHasher',
    )
    # -------------------------------------------------------
    # email backend configuration
    # -------------------------------------------------------
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_HOST = '127.0.0.1'
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''
    EMAIL_PORT = 25
    EMAIL_USE_TLS = False
    SERVER_EMAIL = 'root@127.0.0.1'
    DEFAULT_FROM_EMAIL = SERVER_EMAIL
    # -------------------------------------------------------
    # clickjacking protection configuration
    # -------------------------------------------------------
    X_FRAME_OPTIONS = 'DENY'
    # -------------------------------------------------------
    # django sites framework configuration
    # -------------------------------------------------------
    SITE_ID = 1
    # -------------------------------------------------------
    # localization configuration
    # -------------------------------------------------------
    LANGUAGES = (
        ('en', _('English')),
        ('ru', _('Russian')),
    )
    LANGUAGE_CODE = 'en'
    TIME_ZONE = 'UTC'
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True
    # -------------------------------------------------------
    # static files configuration
    # -------------------------------------------------------
    STATICFILES_DIRS = (
    )
    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
        'djangobower.finders.BowerFinder',
        'compressor.finders.CompressorFinder'
    )
    # -------------------------------------------------------
    # django-bower configuration
    # -------------------------------------------------------
    BOWER_COMPONENTS_ROOT = PROJECT_ROOT
    BOWER_PATH = os.path.join(
        PROJECT_ROOT,
        'node_modules',
        '.bin',
        'bower'
    )
    BOWER_INSTALLED_APPS = (
        'modernizr#2.8.3',
        'respond#1.4.2',
        'jquery#2.1.3',
        'bootstrap#3.3.1',
        'font-awesome#4.2.0',
        'handlebars#2.0.0',
        'underscore#1.7.0',
        'json3#3.3.2',
    )
    # -------------------------------------------------------
    # secret key configuration
    # -------------------------------------------------------
    SECRET_KEY = 'SECRET_KEY'
    # -------------------------------------------------------
    # templates configuration
    # -------------------------------------------------------
    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
        'django.template.loaders.eggs.Loader',
    )
    TEMPLATE_DIRS = (
        os.path.abspath(os.path.join(PROJECT_ROOT, 'app', 'templates')),
    )
    # -------------------------------------------------------
    # java configuration configuration
    # -------------------------------------------------------
    JAVA = 'java'
    # -------------------------------------------------------
    # django compressor configuration
    # -------------------------------------------------------
    COMPRESS_PRECOMPILERS = (
        ('text/coffeescript', '{coffee} --bare --compile --stdio'.format(
            coffee=os.path.join(
                PROJECT_ROOT,
                'node_modules',
                '.bin',
                'coffee'
            )
        )),
        ('text/stylus', '{stylus} {cmd}'.format(
            stylus=os.path.join(
                PROJECT_ROOT,
                'node_modules',
                '.bin',
                'stylus'
            ),
            cmd='< {infile} > {outfile}'
        ))
    )
    COMPRESS_CSS_FILTERS = [
        'app.compress_filters.CustomCssAbsoluteFilter',
        'compressor.filters.yui.YUICSSFilter'
    ]
    COMPRESS_JS_FILTERS = [
        'compressor.filters.closure.ClosureCompilerFilter'
    ]
    COMPRESS_YUI_BINARY = '{java} -jar {jar}'.format(
        java=JAVA,
        jar=yuicompressor.get_jar_filename()
    )
    COMPRESS_CLOSURE_COMPILER_BINARY = '{java} -jar {jar}'.format(
        java=JAVA,
        jar=closure.get_jar_filename()
    )
    COMPRESS_OUTPUT_DIR = 'compress'
    COMPRESS_PARSER = 'compressor.parser.LxmlParser'
    # -------------------------------------------------------
    # csrf view configuration
    # -------------------------------------------------------
    CSRF_FAILURE_VIEW = 'app.views.csrf'
    # -------------------------------------------------------
    # project urls path configuration
    # -------------------------------------------------------
    ROOT_URLCONF = 'app.urls'
    # -------------------------------------------------------
    # wsgi script path configuration
    # -------------------------------------------------------
    WSGI_APPLICATION = 'app.wsgi.application'
    # -------------------------------------------------------
    # model auto registration configuration
    # -------------------------------------------------------
    MODELS_AUTO_REGISTRATION = True
    # -------------------------------------------------------
    # storages configuration
    # -------------------------------------------------------
    MEDIA_LOCATION = 'media'
    STATIC_LOCATION = 'static'
    STATIC_ROOT = os.path.abspath(os.path.join(PROJECT_ROOT, 'www', 'static'))
    STATIC_URL = '/{location}/'.format(
        location=STATIC_LOCATION
    )
    FAVICON_STATIC = 'frontend/img/favicon.ico'
    COMPRESS_ROOT = STATIC_ROOT
    COMPRESS_URL = STATIC_URL

    DEFAULT_FILE_STORAGE = 'app.storage.S3MediaStorage'

    AWS_ACCESS_KEY_ID = 'AKIAJSOKYB6HRKACSAMA'
    AWS_SECRET_ACCESS_KEY = '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'
    AWS_STORAGE_BUCKET_NAME = 'yaga-dev'

    S3_HOST = 'https://{bucket}.s3.amazonaws.com/'.format(
        bucket=AWS_STORAGE_BUCKET_NAME
    )
    MEDIA_URL = '{host}media/'.format(
        host=S3_HOST
    )

    AWS_PRELOAD_METADATA = False
    AWS_S3_SECURE_URLS = True
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_FILE_OVERWRITE = False
    # -------------------------------------------------------
    # django accounting configuration
    # -------------------------------------------------------
    LOGIN_URL = 'accounts:sign_in'
    LOGOUT_URL = 'accounts:sign_out'
    LOGIN_REDIRECT_URL = 'index'
    AUTH_USER_MODEL = 'accounts.User'
    # -------------------------------------------------------
    # raven configuration
    # -------------------------------------------------------
    # RAVEN_CONFIG = {
    #     'dsn': '',
    # }
    SENTRY_CLIENT = 'app.utils.SentryCeleryClient'
    # -------------------------------------------------------
    # middleware classes configuration
    # -------------------------------------------------------
    MIDDLEWARE_CLASSES = [
        # bridge storage
        'app.middleware.BridgeMiddleware',
        # request cookies
        'app.middleware.RequestCookiesMiddleware',
        # 'django.contrib.sites.middleware.CurrentSiteMiddleware',
        'app.middleware.CapabilityMiddleware',
        'django.middleware.http.ConditionalGetMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        # django mobile
        'django_mobile.middleware.MobileDetectionMiddleware',
        'django_mobile.middleware.SetFlavourMiddleware',
        # 'django.middleware.locale.LocaleMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        # 'cached_auth.Middleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        # requestprovider
        'requestprovider.middleware.RequestProviderMiddleware',
        # sentry 404
        # 'raven.contrib.django.middleware.Sentry404CatchMiddleware',
    ]
    # -------------------------------------------------------
    # django south migrations
    # -------------------------------------------------------
    # SOUTH_MIGRATION_MODULES = {
    # }
    # -------------------------------------------------------
    # testing configuration
    # -------------------------------------------------------
    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
    # -------------------------------------------------------
    # installed applications configuration
    # -------------------------------------------------------
    INSTALLED_APPS = [
        # django contrib
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.sitemaps',

        # admin
        'django.contrib.admin',

        # haystack
        # 'haystack',

        # local contrib
        'app',
        'accounts',

        # local
        'content',
        'yaga',

        # layout
        'frontend',

        # vendor
        'clear_cache',
        'django_mobile',
        'redis_sessions_fork',
        'reversion',
        'djcelery_email',
        'django_activeurl',
        'django_extensions',
        'compressor',
        'crispy_forms',
        'djangobower',
        'configurations',
        'rest_framework',
        'django_nose',
        'raven.contrib.django',
        'guardian',
    ]
    # -------------------------------------------------------
    # template context processors configuration
    # -------------------------------------------------------
    TEMPLATE_CONTEXT_PROCESSORS = [
        'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.i18n',
        'django.core.context_processors.media',
        'django.core.context_processors.static',
        'django.core.context_processors.tz',
        'django.contrib.messages.context_processors.messages',
        'django.core.context_processors.request',
        # vendor
        'django_mobile.context_processors.flavour',
        # local
        'app.context_processors.environment',
    ]
    # -------------------------------------------------------
    # authentication backends configuration
    # -------------------------------------------------------
    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'guardian.backends.ObjectPermissionBackend',
        'yaga.backends.CodeBackend',
    )
    ANONYMOUS_USER_ID = 'b25d71af-3dd0-4955-9305-ed495e34727b'  # -1
    GUARDIAN_RAISE_403 = True
    # -------------------------------------------------------
    # logging configuration
    # -------------------------------------------------------
    ADMINS = [
        ('hell', 'hellysmile@gmail.com'),
    ]
    MANAGERS = ADMINS
    DEBUG_LOGGER = {
        'level': 'DEBUG',
        'handlers': ['console', 'sentry'],
        'propagate': False,
    }
    ERROR_LOGGER = {
        'level': 'ERROR',
        'handlers': ['console', 'sentry'],
        'propagate': False,
    }
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            },
            'sentry': {
                'level': 'ERROR',
                'class': 'raven.contrib.django.handlers.SentryHandler',
                'formatter': 'verbose'
            }
        },
        'loggers': {
            'amqp': DEBUG_LOGGER,
            'kombu': DEBUG_LOGGER,
            # 'kombu.common': DEBUG_LOGGER,
            # 'kombu.connection': DEBUG_LOGGER,
            'celery': DEBUG_LOGGER,
            # 'celery.worker': DEBUG_LOGGER,
            # 'celery.task': DEBUG_LOGGER,
            # 'celery.app.builtins': DEBUG_LOGGER,
            # 'celery.app': DEBUG_LOGGER,

            'gunicorn': DEBUG_LOGGER,
            # 'gunicorn.http': DEBUG_LOGGER,
            # 'gunicorn.http.wsgi': DEBUG_LOGGER,
            # 'gunicorn.access': DEBUG_LOGGER,
            # 'gunicorn.error': DEBUG_LOGGER,

            # 'configurations.importer': DEBUG_LOGGER,
            'configurations': DEBUG_LOGGER,

            'multiprocessing': DEBUG_LOGGER,

            'django': ERROR_LOGGER,
            # 'django.request': DEBUG_LOGGER,
            # 'django.security': DEBUG_LOGGER,
            # 'django.db.backends': DEBUG_LOGGER,

            'boto': ERROR_LOGGER,

            'requests': DEBUG_LOGGER,

            'yaga': DEBUG_LOGGER
        },
        'root': DEBUG_LOGGER,
    }
    # import logging
    # for logger in logging.root.manager.loggerDict:
    #     LOGGING['loggers'][logger] = DEBUG_LOGGER
    # LOGGING_CONFIG = None
    # -------------------------------------------------------
    # celery configuration
    # -------------------------------------------------------
    MESSAGE_PROTOCOL = 'pickle'
    CELERY_ALWAYS_EAGER = False
    BROKER_URL = 'sqla+sqlite:///{path}/broker.sqlite'.format(
        path=PROJECT_ROOT
    )
    CELERY_RESULT_BACKEND = 'db+sqlite:///{path}/result.sqlite'.format(
        path=PROJECT_ROOT
    )
    CELERY_TASK_SERIALIZER = MESSAGE_PROTOCOL
    CELERYD_LOG_LEVEL = 'DEBUG'
    CELERY_SEND_TASK_ERROR_EMAILS = False
    CELERY_DISABLE_RATE_LIMITS = True
    CELERY_TIMEZONE = TIME_ZONE
    CELERY_ENABLE_UTC = True
    CELERY_TASK_RESULT_EXPIRES = 60 * 60
    CELERY_SEND_TASK_SENT_EVENT = True
    CELERY_MESSAGE_COMPRESSION = 'bzip2'
    CELERY_RESULT_SERIALIZER = MESSAGE_PROTOCOL
    CELERY_ACCEPT_CONTENT = (MESSAGE_PROTOCOL,)
    CELERY_IGNORE_RESULT = False
    CELERYD_HIJACK_ROOT_LOGGER = False
    CELERY_ACKS_LATE = True
    CELERY_REDIRECT_STDOUTS = False
    # CELERYD_TASK_TIME_LIMIT = 60
    # CELERYD_TASK_SOFT_TIME_LIMIT = 30
    # -------------------------------------------------------
    # rest framework configuration
    # -------------------------------------------------------
    REST_FRAMEWORK = {
        'DEFAULT_PARSER_CLASSES': (
            # 'app.utils.UJSONParser',
            'rest_framework.parsers.JSONParser',
        ),
        'DATETIME_FORMAT': '%s',
        'DEFAULT_RENDERER_CLASSES': (
            # 'drf_ujson.renderers.UJSONRenderer',
            # 'app.utils.UJSONRenderer',
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
        ),
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.SessionAuthentication',
            'accounts.authentication.TokenAuthentication'
        ),
        'DEFAULT_THROTTLE_CLASSES': (
            'rest_framework.throttling.AnonRateThrottle',
            'rest_framework.throttling.UserRateThrottle',
            'rest_framework.throttling.ScopedRateThrottle',
        ),
        'DEFAULT_THROTTLE_RATES': {
            'anon': '100/hour',
            'user': '500/hour',
        },
        'TEST_REQUEST_DEFAULT_FORMAT': 'json',
        'TEST_REQUEST_RENDERER_CLASSES': (
            'rest_framework.renderers.JSONRenderer',
        )
    }
    SWAGGER_SETTINGS = {
        'is_superuser': True
    }
    REST_FRAMEWORK_EXTENSIONS = {}
    # -------------------------------------------------------
    # static werkzeug configuration
    # -------------------------------------------------------
    HANDLE_STATIC = False
    # -------------------------------------------------------
    # requests configuration
    # -------------------------------------------------------
    HTTP_RETRIES = 5


class Initialization(
    object
):
    def __init__(self):
        self.implement()
        self.connect()


class Implementation(
    object
):
    def implement(self):
        # -------------------------------------------------------
        # Python 2 capability features
        # -------------------------------------------------------
        # -------------------------------------------------------
        # debug context processor implementation
        # -------------------------------------------------------
        if self.DEBUG:
            self.TEMPLATE_CONTEXT_PROCESSORS.append(
                'django.core.context_processors.debug'
            )
        # -------------------------------------------------------
        # docs implementation
        # -------------------------------------------------------
        if self.USE_DOCS:
            self.INSTALLED_APPS.append(
                'django.contrib.admindocs'
            )
            self.INSTALLED_APPS.append(
                'rest_framework_swagger'
            )
        # -------------------------------------------------------
        # debug toolbar implementation
        # -------------------------------------------------------
        if self.DEBUG_TOOLBAR:
            if not six.PY3:
                self.INSTALLED_APPS.extend((
                    'template_timings_panel',
                ))
                self.DEBUG_TOOLBAR_PANELS.append(
                    'template_timings_panel.panels.TemplateTimings.TemplateTimings'  # noqa
                )

            index = self.MIDDLEWARE_CLASSES.index(
                'django.middleware.http.ConditionalGetMiddleware'
            )
            self.MIDDLEWARE_CLASSES.insert(
                index + 1, 'debug_toolbar.middleware.DebugToolbarMiddleware'
            )

            self.INSTALLED_APPS.append('debug_toolbar')
        # -------------------------------------------------------
        # gzip implementation
        # -------------------------------------------------------
        if self.GZIP:
            index = self.MIDDLEWARE_CLASSES.index(
                'django.middleware.http.ConditionalGetMiddleware'
            )
            self.MIDDLEWARE_CLASSES.insert(
                index + 1, 'django.middleware.gzip.GZipMiddleware'
            )
        # -------------------------------------------------------
        # template debug implementation
        # -------------------------------------------------------
        self.TEMPLATE_DEBUG = self.DEBUG

        if self.TEMPLATE_DEBUG:
            fallback = InvalidTemplateObject()
        else:
            fallback = ''
        self.TEMPLATE_STRING_IF_INVALID = fallback
        # -------------------------------------------------------
        # template cache implementation
        # -------------------------------------------------------
        if self.TEMPLATE_CACHE:
            self.TEMPLATE_LOADERS = (
                (
                    'django.template.loaders.cached.Loader',
                    self.TEMPLATE_LOADERS
                ),
            )
        # -------------------------------------------------------
        # https implementation
        # -------------------------------------------------------
        if self.HTTPS:
            self.SESSION_COOKIE_SECURE = True
            self.CSRF_COOKIE_SECURE = True
            self.SECURE_SSL_REDIRECT = True
            self.SECURE_FRAME_DENY = True
            self.SECURE_BROWSER_XSS_FILTER = True
            self.SECURE_HSTS_INCLUDE_SUBDOMAINS = True
            self.SECURE_HSTS_SECONDS = 5
            self.SECURE_CONTENT_TYPE_NOSNIFF = True
            self.INSTALLED_APPS.append('djangosecure')
            self.MIDDLEWARE_CLASSES.insert(
                1,
                'djangosecure.middleware.SecurityMiddleware'
            )
            self.SECURE_PROXY_SSL_HEADER = (
                'HTTP_X_FORWARDED_PROTO',
                'https'
            )
        # -------------------------------------------------------
        # rest framework implementation
        # -------------------------------------------------------
        self.REST_FRAMEWORK_EXTENSIONS['DEFAULT_CACHE_RESPONSE_TIMEOUT'] = \
            self.VIEW_CACHE_TIMEOUT

    def connect(self):
        pass
