import hashlib

class Package(object):
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
        self.id = hashlib.md5(self.unique_name).hexdigest()

    @property
    def unique_name(self):
        return self.name + "-" + str(self.version)

    def __repr__(self):
        return "Package(%r, %r)" % (self.name, self.version)

    def __str__(self):
        return self.unique_name
