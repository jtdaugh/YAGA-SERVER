class BaseConfig(object):
    LOCALES = ['en']
    BABEL_DEFAULT_LOCALE = 'en'
    SECURITY_PASSWORD_HASH = 'bcrypt'
    WTF_CSRF_ENABLED = False
    SECURITY_DEFAULT_REMEMBER_ME = True

    ROLES = {
        'superuser': 'superuser',
        'test': 'test'
    }
