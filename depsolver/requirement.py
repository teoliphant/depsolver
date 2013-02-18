from depsolver.errors \
    import \
        DepSolverError
from depsolver.constraints \
    import \
        Equal, GEQ, LEQ
from depsolver.requirement_parser \
    import \
        RawRequirementParser
from depsolver.version \
    import \
        MaxVersion, MinVersion, Version

V = Version.from_string

class Requirement(object):
    def __init__(self, name, specs):
        self.name = name

        # transform GE and LE into NOT + corresponding GEQ/LEQ
        # Take the min of GEQ, max of LEQ
        equals = [req for req in specs if isinstance(req, Equal)]
        if len(equals) > 1:
            self._cannot_match = True
            self._equal = None
        elif len(equals) == 1:
            self._cannot_match = False
            self._equal = V(equals[0].version)
        else:
            self._cannot_match = False
            self._equal = None

        geq = [req for req in specs if isinstance(req, GEQ)]
        geq_versions = [V(g.version) for g in geq]
        if len(geq_versions) > 0:
            self._min_bound = max(geq_versions)
        else:
            self._min_bound = MinVersion()

        leq = [req for req in specs if isinstance(req, LEQ)]
        leq_versions = [V(l.version) for l in leq]
        if len(leq_versions) > 0:
            self._max_bound = min(leq_versions)
        else:
            self._max_bound = MaxVersion()

    def __repr__(self):
        r = []
        if self._min_bound != MinVersion():
            r.append("%s >= %s" % (self.name, self._min_bound))
        if self._max_bound != MaxVersion():
            r.append("%s <= %s" % (self.name, self._max_bound))
        if self._equal:
            r.append("%s == %s" % (self.name, self._equal))
        return ", ".join(r)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def match(self, package):
        """Return True if the given package matches this requirement."""
        if not self.name in package.provides:
            return False
        if self._cannot_match:
            return False
        else:
            version = package.version
            if self._equal:
                if version == self._equal:
                    return True
                else:
                    return False
            else:
                if version >= self._min_bound and version <= self._max_bound:
                    return True
                else:
                    return False

class RequirementParser(object):
    def __init__(self):
        self._parser = RawRequirementParser()

    def parse(self, requirement_string):
        for distribution_name, specs in self._parser.parse(requirement_string).iteritems():
            yield Requirement(distribution_name, specs)
