import unittest

from depsolver.package \
    import \
        Package
from depsolver.requirement \
    import \
        Requirement, RequirementParser
from depsolver.requirement_parser \
    import \
        EqualSpecification, GEQSpecification, LEQSpecification
from depsolver.version \
    import \
        Version

V = Version.from_string

class TestRequirementParser(unittest.TestCase):
    def test_simple(self):
        parser = RequirementParser()

        r_requirements = [Requirement("numpy", [GEQSpecification("1.3.0")])]
        requirements = parser.parse("numpy >= 1.3.0")
        self.assertEqual(r_requirements, list(requirements))

        r_requirements = [Requirement("numpy", [GEQSpecification("1.3.0"),
                                                LEQSpecification("2.0.0")])]
        requirements = parser.parse("numpy >= 1.3.0, numpy <= 2.0.0")
        self.assertEqual(r_requirements, list(requirements))

        r_requirements = [Requirement("numpy", [EqualSpecification("1.3.0")])]
        requirements = parser.parse("numpy == 1.3.0")
        self.assertEqual(r_requirements, list(requirements))

        r_requirements = [Requirement("numpy", [EqualSpecification("1.3.0"),
                                                EqualSpecification("1.4.0")])]
        requirements = parser.parse("numpy == 1.3.0, numpy == 1.4.0")
        self.assertEqual(r_requirements, list(requirements))

    def test_repr(self):
        requirement_string = "numpy >= 1.3.0, numpy <= 2.0.0"
        parser = RequirementParser()
        numpy_requirement = list(parser.parse(requirement_string))[0]

        self.assertEqual(repr(numpy_requirement), requirement_string)

    def test_match(self):
        parser = RequirementParser()

        numpy_requirement = list(parser.parse("numpy >= 1.3.0, numpy <= 2.0.0"))[0]
        self.assertFalse(numpy_requirement.match(Package("numpy", V("1.2.0"))))
        self.assertTrue(numpy_requirement.match(Package("numpy", V("1.4.0"))))
        self.assertTrue(numpy_requirement.match(Package("numpy", V("1.5.0"))))

        numpy_requirement = list(parser.parse("numpy == 1.3.0"))[0]
        self.assertFalse(numpy_requirement.match(Package("numpy", V("1.2.0"))))
        self.assertTrue(numpy_requirement.match(Package("numpy", V("1.3.0"))))
        self.assertFalse(numpy_requirement.match(Package("numpy", V("1.4.0"))))
        self.assertFalse(numpy_requirement.match(Package("numpy", V("1.5.0"))))

        numpy_requirement = list(parser.parse("numpy >= 1.3.0"))[0]
        self.assertFalse(numpy_requirement.match(Package("numpy", V("1.2.0"))))
        self.assertTrue(numpy_requirement.match(Package("numpy", V("1.4.0"))))
        self.assertTrue(numpy_requirement.match(Package("numpy", V("1.5.0"))))

        numpy_requirement = list(parser.parse("numpy <= 1.3.0"))[0]
        self.assertTrue(numpy_requirement.match(Package("numpy", V("1.2.0"))))
        self.assertFalse(numpy_requirement.match(Package("numpy", V("1.4.0"))))
        self.assertFalse(numpy_requirement.match(Package("numpy", V("1.5.0"))))
