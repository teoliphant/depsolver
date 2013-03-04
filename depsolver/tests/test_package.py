import hashlib
import unittest

import six

from depsolver.package \
    import \
        Package
from depsolver.requirement \
    import \
        Requirement
from depsolver.version \
    import \
        Version

V = Version.from_string
R = Requirement.from_string

class TestPackage(unittest.TestCase):
    def test_construction(self):
        r_provides = set()
        r_id = hashlib.md5(six.b("numpy-1.3.0")).hexdigest()

        package = Package("numpy", V("1.3.0"))
        self.assertEqual(package.provides, r_provides)
        self.assertEqual(package.dependencies, set())
        self.assertEqual(package.id, r_id)

        r_provides = set([R("numpy == 1.3.0")])
        r_id = hashlib.md5(six.b("nomkl_numpy-1.3.0")).hexdigest()

        package = Package("nomkl_numpy", V("1.3.0"), provides=r_provides)
        self.assertEqual(package.provides, r_provides)
        self.assertEqual(package.id, r_id)

    def test_unique_name(self):
        package = Package("numpy", V("1.3.0"))
        self.assertEqual(package.unique_name, "numpy-1.3.0")

    def test_str(self):
        provides = set([R("numpy == 1.3.0")])
        package = Package("nomkl_numpy", V("1.3.0"), provides=provides)
        self.assertEqual(str(package), "nomkl_numpy-1.3.0")

    def test_repr(self):
        package = Package("numpy", V("1.3.0"))
        self.assertEqual(repr(package), "Package('numpy-1.3.0')")

        package = Package("numpy", V("1.6.0"), dependencies=[R("mkl >= 10.3.0")])
        self.assertEqual(repr(package), "Package('numpy-1.6.0; depends (mkl >= 10.3.0)')")

class TestPackageFromString(unittest.TestCase):
    def test_simple(self):
        r_package = Package("numpy", V("1.3.0"))

        self.assertEqual(Package.from_string("numpy-1.3.0"), r_package)
        self.assertRaises(ValueError, lambda: Package.from_string("numpy 1.3.0"))

    def test_dependencies(self):
        r_package = Package("numpy", V("1.6.0"), dependencies=[R("mkl >= 10.3.0")])
        package = Package.from_string("numpy-1.6.0; depends (mkl >= 10.3.0)")

        self.assertEqual(package, r_package)

    def test_provides(self):
        r_package = Package("nomkl_numpy", V("1.6.0"), provides=[R("numpy == 1.6.0")])
        package = Package.from_string("nomkl_numpy-1.6.0; provides (numpy == 1.6.0)")

        self.assertEqual(package, r_package)
