class _Constraint(object):
    def __init__(self, version):
        self.version = version

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.version)

    # Mostly useful for testing
    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.version == other.version

class Equal(_Constraint):
    pass

class GEQ(_Constraint):
    pass

class LEQ(_Constraint):
    pass
