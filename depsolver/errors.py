class DepSolverError(Exception):
    pass

class InvalidVersion(DepSolverError):
    pass

class MissingPackageInPool(DepSolverError):
    def __init__(self, package_id):
        self.requested_id = package_id
        self.message = "This pool does not have any package with id %s" % package_id
