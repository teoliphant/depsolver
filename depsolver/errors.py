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
    def __init__(self, package_or_package_id):
        self.requested_package_or_id = package_or_package_id
        self.message = "This pool does not have any package %r" % package_or_package_id
