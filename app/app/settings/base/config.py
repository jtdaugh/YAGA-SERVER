from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

import datetime
import os

import closure
import yuicompressor
from configurations import Configuration
from django.utils import six
from django.utils.translation import ugettext_lazy as _


# import psycopg2.extensions


class InvalidTemplateObjectException(
    Exception
):
    pass


class InvalidTemplateObject(
    object
):
    MUTED_PARAMS = (
        'media',
        'query.q',
        'query.dir'
    )

    def __mod__(self, missing):
        if str(missing) not in self.MUTED_PARAMS:
            raise InvalidTemplateObjectException(missing)

        return ''

    def __bool__(self):
        return False

    __nonzero__ = __bool__

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
        'view_stats'
    ]
    # -------------------------------------------------------
    # self http heartbeat
    # -------------------------------------------------------
    SELF_HEARTBEAT_RUN_EVERY = datetime.timedelta(minutes=5)
    # -------------------------------------------------------
    # flanker configuration
    # -------------------------------------------------------
    USE_FLANKER = True
    FLANKER_DRIVER_ENABLED = True
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

    CLOUDFLARE_BEHIND = False
    # -------------------------------------------------------
    # database configuration
    # -------------------------------------------------------
    DATABASES = {
        'default': {
            'ENGINE': 'transaction_hooks.backends.postgresql_psycopg2',
            'NAME': 'app',
            'ATOMIC_REQUESTS': True,
            'CONN_MAX_AGE': 30,
            'AUTOCOMMIT': True,
            # 'OPTIONS': {
            #     'isolation_level': psycopg2.extensions.ISOLATION_LEVEL_REPEATABLE_READ  # noqa
            # }
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
    REAL_SESSION_ENGINE = 'django.contrib.sessions.backends.file'
    SESSION_ENGINE = 'app.session'
    SESSION_FILE_PATH = os.path.abspath(
        os.path.join(PROJECT_ROOT, 'sessions')
    )
    MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
    # SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'  # noqa
    # SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
    # SESSION_SERIALIZER = 'redis_sessions_fork.serializers.UjsonSerializer'
    SESSION_SERIALIZER = 'mongoengine.django.sessions.BSONSerializer'
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
    # EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
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
        'jquery#2.1.4',
        'bootstrap#3.3.5',
        'bootstrap-select#1.6.5',
        'font-awesome#4.3.0',
        'handlebars#3.0.3',
        'underscore#1.8.3',
        'video.js#5.0.0-29',
        'bootstrap-switch#3.3.2',
        'json3#3.3.2',
        'bootstrap3-dialog#1.34.5',
        'moment#2.10.3',
        'eonasdan-bootstrap-datetimepicker#4.14.30'
    )
    # -------------------------------------------------------
    # secret key configuration
    # -------------------------------------------------------
    SECRET_KEY = 'SECRET_KEY'
    # -------------------------------------------------------
    # templates configuration
    # -------------------------------------------------------
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
            ],
            'OPTIONS': {
                'context_processors': [
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
                ],
                'loaders': [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                    'django.template.loaders.eggs.Loader',
                ]
            }
        },
    ]
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
    COMPRESS_CLOSURE_COMPILER_ARGUMENTS = '--language_in=ECMASCRIPT5'
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
    FAVICON_STATIC = 'frontend/img/favicon.ico'
    MEDIA_LOCATION = 'media'
    STATIC_LOCATION = 'static'

    STATIC_ROOT = os.path.abspath(
        os.path.join(PROJECT_ROOT, 'www', STATIC_LOCATION)
    )
    STATIC_URL = '/{location}/'.format(
        location=STATIC_LOCATION
    )

    DEFAULT_FILE_STORAGE = 'app.storage.S3MediaStorage'

    AWS_REGION = 'us-west-1'
    AWS_ACCESS_KEY_ID = 'AKIAJ3BOSZSPPD7EX7KA'
    AWS_SECRET_ACCESS_KEY = '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'
    AWS_STORAGE_BUCKET_NAME = 'yaga-dev'

    CLOUDFRONT_HOST = 'd2wxdqvi5302or.cloudfront.net'

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
        'yaga.middleware.YagaMiddleware',
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
        'cloudflare',

        # local
        'content',
        'yaga',

        # layout
        'frontend',

        # vendor
        'guardian',
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
        'django_flanker',
        'rest_framework',
        'django_nose',
        'macros',
        'hijack',
        'compat',
        'raven.contrib.django',
    ]
    # -------------------------------------------------------
    # hijack backends configuration
    # -------------------------------------------------------
    SHOW_HIJACKUSER_IN_ADMIN = False
    HIJACK_NOTIFY_ADMIN = False
    HIJACK_LOGIN_REDIRECT_URL = '/'
    # -------------------------------------------------------
    # authentication backends configuration
    # -------------------------------------------------------
    AUTHENTICATION_BACKENDS = (
        'yaga.backends.CodeBackend',
        'django.contrib.auth.backends.ModelBackend',
        'guardian.backends.ObjectPermissionBackend'

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
        'handlers': ['debug', 'sentry'],
        'propagate': False,
    }
    INFO_LOGGER = {
        'level': 'INFO',
        'handlers': ['info', 'sentry'],
        'propagate': False,
    }
    ERROR_LOGGER = {
        'level': 'ERROR',
        'handlers': ['error', 'sentry'],
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
                'format': '%(message)s'
            },
        },
        'handlers': {
            'info': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'debug': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            },
            'error': {
                'level': 'ERROR',
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
            'apns_clerk': ERROR_LOGGER,
            'apns_client': ERROR_LOGGER,

            'celery': INFO_LOGGER,

            'gunicorn': INFO_LOGGER,

            # 'uwsgi': INFO_LOGGER,

            'django': ERROR_LOGGER,
            # 'django.request': DEBUG_LOGGER,
            # 'django.security': DEBUG_LOGGER,
            # 'django.db.backends': DEBUG_LOGGER,

            'boto': ERROR_LOGGER,

            'requests': ERROR_LOGGER,

            'yaga': DEBUG_LOGGER,
            'app': DEBUG_LOGGER
        },
        'root': INFO_LOGGER,
    }
    # import logging
    # for logger in logging.root.manager.loggerDict:
    #     LOGGING['loggers'][logger] = DEBUG_LOGGER
    # LOGGING_CONFIG = None
    # -------------------------------------------------------
    # celery configuration
    # -------------------------------------------------------
    MESSAGE_PROTOCOL = 'bson'
    CELERY_ALWAYS_EAGER = False
    BROKER_URL = 'sqla+sqlite:///{path}/broker.sqlite'.format(
        path=PROJECT_ROOT
    )
    CELERY_RESULT_BACKEND = 'db+sqlite:///{path}/result.sqlite'.format(
        path=PROJECT_ROOT
    )
    # CELERY_RESULT_BACKEND = 'redis://'
    CELERY_TASK_SERIALIZER = MESSAGE_PROTOCOL
    CELERYD_LOG_LEVEL = 'DEBUG'
    CELERY_SEND_TASK_ERROR_EMAILS = False
    CELERY_DISABLE_RATE_LIMITS = True
    CELERY_TIMEZONE = TIME_ZONE
    CELERY_ENABLE_UTC = True
    CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 12
    CELERY_SEND_TASK_SENT_EVENT = True
    CELERY_MESSAGE_COMPRESSION = 'zlib'
    CELERY_RESULT_SERIALIZER = MESSAGE_PROTOCOL
    CELERY_ACCEPT_CONTENT = (MESSAGE_PROTOCOL,)
    CELERY_IGNORE_RESULT = False
    CELERYD_HIJACK_ROOT_LOGGER = False
    CELERY_ACKS_LATE = True
    CELERYD_PREFETCH_MULTIPLIER = 1
    CELERY_REDIRECT_STDOUTS = False
    CELERYD_TASK_SOFT_TIME_LIMIT = 30
    # CELERYD_TASK_TIME_LIMIT = 35
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
    HTTP_RETRIES = 3


class Initialization(
    object
):
    def __init__(self):
        self.implement()
        self.configure()
        self.connect()


class Implementation(
    object
):
    def implement(self):
        # -------------------------------------------------------
        # hosts implementation
        # -------------------------------------------------------
        if self.CLOUDFLARE_BEHIND:
            self.MIDDLEWARE_CLASSES.insert(
                0, 'cloudflare.middleware.CloudFlareMiddleware'
            )
        # -------------------------------------------------------
        # storages implementation
        # -------------------------------------------------------
        self.AWS_S3_CUSTOM_DOMAIN = '{bucket}.s3-{region}.amazonaws.com'.format(  # noqa
            bucket=self.AWS_STORAGE_BUCKET_NAME,
            region=self.AWS_REGION
        )

        self.S3_HOST = '{protocol}://{domain}/'.format(
            protocol='https' if self.AWS_S3_SECURE_URLS else 'http',
            domain=self.AWS_S3_CUSTOM_DOMAIN
        )

        if self.CLOUDFRONT_HOST:
            self.MEDIA_URL = '{protocol}://{host}/{location}/'.format(
                protocol='https' if self.AWS_S3_SECURE_URLS else 'http',
                host=self.CLOUDFRONT_HOST,
                location=self.MEDIA_LOCATION
            )
        else:
            self.MEDIA_URL = '{host}{location}/'.format(
                host=self.S3_HOST,
                location=self.MEDIA_LOCATION
            )
        # -------------------------------------------------------
        # debug context processor implementation
        # -------------------------------------------------------
        if self.DEBUG:
            self.TEMPLATES[0]['OPTIONS']['context_processors'].append(
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
        if self.DEBUG:
            fallback = InvalidTemplateObject()
        else:
            fallback = ''
        self.TEMPLATES[0]['OPTIONS']['string_if_invalid'] = fallback

        self.TEMPLATES[0]['OPTIONS']['debug'] = self.DEBUG
        # -------------------------------------------------------
        # template cache implementation
        # -------------------------------------------------------
        if self.TEMPLATE_CACHE:
            self.TEMPLATES[0]['OPTIONS']['loaders'] = (
                (
                    'django.template.loaders.cached.Loader',
                    self.TEMPLATES[0]['OPTIONS']['loaders']
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

    def configure(self):
        self.COMPRESS_URL = self.STATIC_URL

    def connect(self):
        pass
