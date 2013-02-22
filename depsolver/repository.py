import collections

from depsolver.package \
    import \
        Package
from depsolver.version \
    import \
        Version

class Repository(object):
    """Creates a new repository instance.
    
    A repository is a a container of packages.

    Parameters
    ----------
    packages: seq
        A sequence of packages
    """
    def __init__(self, packages=None):
        if packages is None:
            packages = []
        self._package_name_to_ids = collections.defaultdict(list)
        for package in packages:
            self._package_name_to_ids[package.name].append(package.unique_name)
        self._id_to_package = dict((p.unique_name, p) for p in packages)

    def iter_packages(self):
        """Return an iterator over every package contained in this repo.
        
        Note
        ----
        Order is undefined.
        """
        return self._id_to_package.itervalues()

    def list_packages(self):
        """Return the list of every package contained in this repo.

        Note
        ----
        Order is undefined.
        """
        return list(self.iter_packages())

    def add_package(self, package):
        """Add the given package to the repo.

        Parameters
        ----------
        package: Package
            Package to look for.
        """
        self._package_name_to_ids[package.name].append(package.unique_name)
        self._id_to_package[package.unique_name] = package

    def has_package(self, package):
        """Returns True if the given package is present in the repo, False
        otherwise.
        
        Parameters
        ----------
        package: Package
            Package to look for.
        """
        return self.find_package(package.name, str(package.version)) is not None

    def has_package_name(self, name):
        """Returns True if one package with the given package name is present in
        the repo, False otherwise.
        
        Parameters
        ----------
        name: str
            Package name to look for.
        """
        return len(self.find_packages(name)) > 0

    def find_package(self, name, version):
        """Find the package with the given name and version (exact match).

        Parameters
        ----------
        name: str
            Name of the package(s) to look for
        version: str
            Name of the package(s) to look for

        Returns
        -------
        package: Package or None
            The package if found, None otherwise.
        """
        package = Package(name, Version.from_string(version))
        return self._id_to_package.get(package.unique_name, None)

    def find_packages(self, name):
        """Returns a list of packages with the given name.

        Parameters
        ----------
        name: str
            Name of the package(s) to look for

        Returns
        -------
        packages: seq
            List of packages found (may be empty if no package found with the
            requested name).

        Notes
        -----
        Even if package A provides package B, find_packages(b_name) will not
        include A
        """
        return [self._id_to_package[package_id] \
                for package_id in self._package_name_to_ids[name]]
