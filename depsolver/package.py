import hashlib
import re

from depsolver.requirement \
    import \
        Requirement
from depsolver.version \
    import \
        Version

R = Requirement.from_string
V = Version.from_string

_SECTION_RE = re.compile("(depends|provides)\s*\((.*)\)")

def _parse_name_version_part(name_version, loose):
    parts = name_version.strip().split("-", 1)
    if len(parts) < 2:
        raise ValueError("Invalid package string %s" % name_version)
    else:
        name, version_string = parts
        if loose:
            version = Version.from_loose_string(version_string)
        else:
            version = V(version_string)

        return name, version

def _parse_requirements_string(s):
    m = _SECTION_RE.search(s)
    if m is None:
        raise ValueError("invalid requirement string: %r" % s)
    else:
        requirements_string = m.groups()[1]
        requirements = set()
        for requirement_string in requirements_string.split(","):
            requirements.add(R(requirement_string))
        return requirements

def parse_package_string(package_string, loose=False):
    parts = package_string.split(";")

    if len(parts) < 1:
        raise ValueError("YO")

    name, version = _parse_name_version_part(parts[0], loose)

    dependencies = None
    provides = None

    if len(parts) > 1:
        for part in parts[1:]:
            part = part.strip()
            if part.startswith("depends"):
                dependencies = _parse_requirements_string(part)
            elif part.startswith("provides"):
                provides = _parse_requirements_string(part)
            else:
                raise ValueError("syntax error: %r" % part)

    return name, version, provides, dependencies

class Package(object):
    @classmethod
    def from_loose_string(cls, package_string):
        name, version, provides, dependencies = parse_package_string(package_string, loose=True)
        return cls(name, version, provides, dependencies)

    @classmethod
    def from_string(cls, package_string):
        """Create a new package from a string.

        Example
        -------
        >>> P = Package.from_string
        >>> numpy_1_3_0 = Package("numpy", Version.from_string("1.3.0"))
        >>> P("numpy-1.3.0") == numpy_1_3_0
        True
        >>> P("numpy-1.3.0; depends (mkl <= 10.4.0, mkl >= 10.3.0)")
        Package('numpy-1.3.0; depends (mkl <= 10.4.0, mkl >= 10.3.0)')
        """
        name, version, provides, dependencies = parse_package_string(package_string)
        return cls(name, version, provides, dependencies)

    def __init__(self, name, version, provides=None, dependencies=None):
        """Create a new package instance.

        PackageInfo instances contain exactly all the metadata needed for the
        dependency management.

        Parameters
        ----------
        name: str
            Name of the package (i.e. distribution name)
        version: object
            Instance of Version
        provides: None or sequence
            Sequence of Requirements.
        dependencies: None or sequence
            Sequence of Requirements.
        """
        self.name = name
        self.version = version

        def _sorted(requirements):
            return sorted(requirements, key=lambda req: repr(req))

        if provides is None:
            self.provides = ()
        else:
            self.provides = tuple(_sorted(set(provides)))

        if dependencies is None:
            self.dependencies = ()
        else:
            self.dependencies = tuple(_sorted(set(dependencies)))

        # FIXME: id detail should be implemented outside Package interface
        self.id = hashlib.md5(self.unique_name.encode("ascii")).hexdigest()

    @property
    def unique_name(self):
        return self.name + "-" + str(self.version)

    @property
    def package_string(self):
        strings = ["%s-%s" % (self.name, self.version)]
        if self.dependencies:
            strings.append("depends (%s)" % ", ".join(str(s) for s in self.dependencies))
        if self.provides:
            strings.append("provides (%s)" % ", ".join(str(s) for s in self.provides))
        return "; ".join(strings)

    def __repr__(self):
        return "Package(%r)" % self.package_string

    def __str__(self):
        return self.unique_name

    def __eq__(self, other):
        return self.name == other.name and self.version == other.version \
                and self.provides == other.provides \
                and self.dependencies == other.dependencies

    def __hash__(self):
        return hash(repr(self))
