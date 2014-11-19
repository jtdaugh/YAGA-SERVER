class BaseStorage(object):
    def merge(self, obj):
        for key in dir(obj):
            if not hasattr(self, key):
                setattr(self, key, getattr(obj, key))
