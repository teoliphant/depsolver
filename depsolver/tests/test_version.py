import sys

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from depsolver.version \
    import \
        BuildVersion, PreReleaseVersion, Version, is_version_valid

V = Version.from_string
P = PreReleaseVersion.from_string
B = BuildVersion.from_string

class TestVersionParsing(unittest.TestCase):
    def test_valid_versions(self):
        versions = [
            "1.2.0", "0.1.2",
            "1.2.0-alpha", "1.2.0-alpha.1",
            "1.2.0+build", "1.2.0+build.1",
            "1.2.0-alpha+build", "1.2.0-alpha.1+build.2",
        ]
        for version in versions:
            self.assertTrue(is_version_valid(version))

    def test_invalid_versions(self):
        versions = [
            "1.2", "1.2.a",
        ]
        for version in versions:
            self.assertFalse(is_version_valid(version))

class TestVersion(unittest.TestCase):
    def test_construction_simple(self):
        r_v = V("1.2.0")
        v = Version(1, 2, 0)
        self.assertEqual(v.__dict__, r_v.__dict__)

    def test_invalid_arguments(self):
        self.assertRaises(Exception, lambda: Version("a", 2, 0))
        self.assertRaises(Exception, lambda: Version(1, "a", 0))
        self.assertRaises(Exception, lambda: Version(1, 2, "a"))

        self.assertRaises(Exception, lambda: Version(1, 2, 0, pre_release="alpha"))
        self.assertRaises(Exception, lambda: Version(1, 2, 0, build="build.1"))

        self.assertRaises(Exception, lambda: V("1.2.a"))

    def test_string_representation(self):
        r_data = [
                (V("1.2.0"), "Version(1, 2, 0)"),
                (V("1.2.0-alpha"), "Version(1, 2, 0, PreReleaseVersion('alpha'))"),
                (V("1.2.0+build"), "Version(1, 2, 0, BuildVersion('build'))")
                ]
        for version, r_version_string in r_data:
            self.assertEqual(repr(version), r_version_string)

class TestVersionComparison(unittest.TestCase):
    def test_simple_eq(self):
        self.assertTrue(V("1.2.0") == V("1.2.0"))
        self.assertFalse(V("1.2.0") == V("1.2.1"))

    def test_simple_neq(self):
        self.assertTrue(V("1.2.0") != V("1.2.1"))
        self.assertFalse(V("1.2.0") != V("1.2.0"))

    def test_simple_ge(self):
        self.assertTrue(V("1.2.1") > V("1.2.0"))
        self.assertFalse(V("1.2.0") > V("1.2.1"))
        self.assertFalse(V("1.2.0") > V("1.2.0"))

    def test_simple_gt(self):
        self.assertTrue(V("1.2.1") >= V("1.2.0"))
        self.assertFalse(V("1.2.0") >= V("1.2.1"))
        self.assertTrue(V("1.2.0") >= V("1.2.0"))

    def test_simple_le(self):
        self.assertFalse(V("1.2.1") < V("1.2.0"))
        self.assertTrue(V("1.2.0") < V("1.2.1"))
        self.assertFalse(V("1.2.0") < V("1.2.0"))

    def test_simple_lt(self):
        self.assertFalse(V("1.2.1") <= V("1.2.0"))
        self.assertTrue(V("1.2.0") <= V("1.2.1"))
        self.assertTrue(V("1.2.0") <= V("1.2.0"))

    def test_rfc_example(self):
        increasing_versions = [
                V("1.0.0-alpha"),
                V("1.0.0-alpha.1"),
                V("1.0.0-beta.2"),
                V("1.0.0-beta.11"),
                V("1.0.0-rc.1"),
                V("1.0.0-rc.1+build.1"),
                V("1.0.0"),
                V("1.0.0+0.3.7"),
                V("1.3.7+build"),
                V("1.3.7+build.2.b8f12d7"),
                V("1.3.7+build.11.e0f985a"),
        ]

        for left, right in zip(increasing_versions[:-1], increasing_versions[1:]):
            self.assertLess(left, right)
            self.assertLessEqual(left, right)

        decreasing_versions = list(reversed(increasing_versions))
        for left, right in zip(decreasing_versions[:-1], decreasing_versions[1:]):
            self.assertGreater(left, right)
            self.assertGreaterEqual(left, right)

class TestPreReleaseVersionComparison(unittest.TestCase):
    def test_simple_eq(self):
        self.assertTrue(V("1.2.0") == V("1.2.0"))
        self.assertFalse(V("1.2.0") == V("1.2.1"))

    def test_simple_neq(self):
        self.assertTrue(V("1.2.0") != V("1.2.1"))
        self.assertFalse(V("1.2.0") != V("1.2.0"))

    def test_simple_ge(self):
        self.assertTrue(V("1.2.1") > V("1.2.0"))
        self.assertFalse(V("1.2.0") > V("1.2.1"))
        self.assertFalse(V("1.2.0") > V("1.2.0"))

    def test_simple_gt(self):
        self.assertTrue(V("1.2.1") >= V("1.2.0"))
        self.assertFalse(V("1.2.0") >= V("1.2.1"))
        self.assertTrue(V("1.2.0") >= V("1.2.0"))

    def test_simple_le(self):
        self.assertFalse(V("1.2.1") < V("1.2.0"))
        self.assertTrue(V("1.2.0") < V("1.2.1"))
        self.assertFalse(V("1.2.0") < V("1.2.0"))

    def test_simple_lt(self):
        self.assertFalse(V("1.2.1") <= V("1.2.0"))
        self.assertTrue(V("1.2.0") <= V("1.2.1"))
        self.assertTrue(V("1.2.0") <= V("1.2.0"))
