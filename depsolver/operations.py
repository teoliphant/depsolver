class Operation(object):
    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.__dict__ == other.__dict__

class Update(Operation):
    def __init__(self, from_package, to_package):
        self.from_package = from_package
        self.to_package = to_package

    def __repr__(self):
        return "Update from %s to %s" % (self.from_package, self.to_package)

class Install(Operation):
    def __init__(self, package):
        self.package = package

    def __repr__(self):
        return "Install %s" % (self.package,)

class Remove(Operation):
    def __init__(self, package):
        self.package = package

    def __repr__(self):
        return "Remove %s" % (self.package,)

