class Specification(object):
    def __init__(self, version):
        self.version = version

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.version)

    # Mostly useful for testing
    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.version == other.version

class EqualSpecification(Specification):
    pass

class GEQSpecification(Specification):
    pass

class LEQSpecification(Specification):
    pass

