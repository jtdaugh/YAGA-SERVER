from flask.ext.security.utils import encrypt_password, verify_password


class BaseUser(object):
    def set_password(self, password):
        self.password = encrypt_password(password)

    def verify_password(self, password):
        return verify_password(password, self.password)
