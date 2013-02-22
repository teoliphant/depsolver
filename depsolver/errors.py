class DepSolverError(Exception):
    def __str__(self):
        return self.message

class InvalidVersion(DepSolverError):
    pass

class MissingRequirementInPool(DepSolverError):
    def __init__(self, requirement):
        self.requested_requirement = requirement
        self.message = "This pool does not have any package for requirement %s" % requirement

class MissingPackageInPool(DepSolverError):
    def __init__(self, package_id):
        self.requested_id = package_id
        self.message = "This pool does not have any package with id %s" % package_id
