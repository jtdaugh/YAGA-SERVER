class A(object):
    def __bool__(self):
        return False

    __nonzero__ = __bool__

    def foo(self):
        if self:
            1/0


a = A()

a.foo()
