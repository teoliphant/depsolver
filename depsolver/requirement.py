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
    """Requirements instances represent a 'package requirement', that is a
    package + version constraints.

    Arguments
    ---------
    name: str
        Package name
    specs: seq
        Sequence of constraints
    """
    @classmethod
    def from_string(cls, requirement_string):
        """Creates a new Requirement from a requirement string.

        Arguments
        ---------
        requirement_string: str
            The requirement string, e.g. 'numpy >= 1.3.0'

        Examples
        --------

        # This creates a requirement that will match any version of numpy
        >>> Requirement.from_string("numpy")
        numpy *

        # This creates a requirement that will only version of numpy >= 1.3.0
        >>> Requirement.from_string("numpy >= 1.3.0")
        numpy >= 1.3.0
        """
        parser = RequirementParser()
        requirements = parser.parse(requirement_string)
        if len(requirements) != 1:
            raise DepSolverError("Invalid requirement string %r" % requirement_string)
        else:
            return requirements[0]

    def __init__(self, name, specs):
        self.name = name

        self._min_bound = MinVersion()
        self._max_bound = MaxVersion()

        # transform GE and LE into NOT + corresponding GEQ/LEQ
        # Take the min of GEQ, max of LEQ
        equals = [req for req in specs if isinstance(req, Equal)]
        if len(equals) > 1:
            self._cannot_match = True
            self._equal = None
        elif len(equals) == 1:
            self._cannot_match = False
            self._equal = V(equals[0].version)
            self._min_bound = self._max_bound = self._equal
        else:
            self._cannot_match = False
            self._equal = None

        geq = [req for req in specs if isinstance(req, GEQ)]
        geq_versions = [V(g.version) for g in geq]
        if len(geq_versions) > 0:
            self._min_bound = max(geq_versions)

        leq = [req for req in specs if isinstance(req, LEQ)]
        leq_versions = [V(l.version) for l in leq]
        if len(leq_versions) > 0:
            self._max_bound = min(leq_versions)

        if self._min_bound > self._max_bound:
            self._cannot_match = True

    def __repr__(self):
        r = []
        if self._cannot_match:
            r.append("%s None" % self.name)
        elif self._equal:
            r.append("%s == %s" % (self.name, self._equal))
        else:
            if self._min_bound != MinVersion():
                r.append("%s >= %s" % (self.name, self._min_bound))
            if self._max_bound != MaxVersion():
                r.append("%s <= %s" % (self.name, self._max_bound))
            if self._min_bound == MinVersion() and self._max_bound == MaxVersion():
                r.append("%s *" % self.name)
        return ", ".join(r)

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __hash__(self):
        return hash(repr(self))

    def matches(self, provider):
        """Return True if provider requirement and this requirement are
        compatible.

        Arguments
        ---------
        provider: Requirement
            The requirement to match

        Examples
        --------
        >>> req = Requirement.from_string("numpy >= 1.3.0")
        >>> req.matches(Requirement.from_string("numpy"))
        True
        >>> req.matches(Requirement.from_string("numpy >= 1.2.0"))
        True
        >>> req.matches(Requirement.from_string("numpy >= 1.4.0"))
        True
        """
        if self.name != provider.name:
            return False
        if self._cannot_match:
            return False
        if self._equal is None:
            if provider._equal is None:
                if self._min_bound > provider._min_bound:
                    return provider.matches(self)
                else:
                    return self._max_bound >= provider._min_bound
            else:
                if provider._equal >= self._min_bound and provider._equal <= self._max_bound:
                    return True
                else:
                    return False
        else:
            if provider._equal is not None:
                return provider._equal == self._equal
            else:
                return provider.matches(self)

class RequirementParser(object):
    def __init__(self):
        self._parser = RawRequirementParser()

    def iter_parse(self, requirement_string):
        for distribution_name, specs in self._parser.parse(requirement_string).items():
            yield Requirement(distribution_name, specs)

    def parse(self, requirement_string):
        return [r for r in self.iter_parse(requirement_string)]
