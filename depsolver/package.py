import hashlib

from depsolver.version \
    import \
        Version

class Package(object):
    @classmethod
    def from_string(cls, package_string):
        """Create a new package from a string.

        Can only construct package instances without provides, dependencies,
        etc... for now.

        Example
        -------
        >>> numpy_1_3_0 = Package("numpy", Version.from_string("1.3.0"))
        >>> Package.from_string("numpy-1.3.0") == numpy_1_3_0
        True
        """
        parts = package_string.strip().split("-", 1)
        if len(parts) < 2:
            raise ValueError("Invalid package string %s" % package_string)
        else:
            name, version_string = parts
            return cls(name, Version.from_string(version_string))

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

        if provides is None:
            self.provides = set()
        else:
            self.provides = set(provides)

        if dependencies is None:
            self.dependencies = set()
        else:
            self.dependencies = set(dependencies)

        # FIXME: id detail should be implemented outside Package interface
        self.id = hashlib.md5(self.unique_name.encode("ascii")).hexdigest()

    @property
    def unique_name(self):
        return self.name + "-" + str(self.version)

    def __repr__(self):
        return "Package(%r, %r)" % (self.name, self.version)

    def __str__(self):
        return self.unique_name

    def __eq__(self, other):
        return self.name == other.name and self.version == other.version \
                and self.provides == other.provides \
                and self.dependencies == other.dependencies
