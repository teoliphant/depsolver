import unittest

from depsolver.errors \
    import \
        DepSolverError
from depsolver.requirement_parser \
    import \
        RequirementParser, CommaToken, ComparisonToken, DistributionNameToken, \
        GEQToken, LEQToken, VersionToken, EqualSpecification, GEQSpecification, \
        LEQSpecification

class TestRequirementParser(unittest.TestCase):
    def test_lexer_simple(self):
        tokens = list(RequirementParser().tokenize("numpy >= 1.3.0"))
        self.assertEqual(len(tokens), 3)
        self.assertTrue(isinstance(tokens[0], DistributionNameToken))
        self.assertTrue(isinstance(tokens[1], ComparisonToken))
        self.assertTrue(isinstance(tokens[2], VersionToken))

        tokens = list(RequirementParser().tokenize("numpy <= 1.3.0"))
        self.assertEqual(len(tokens), 3)
        self.assertTrue(isinstance(tokens[0], DistributionNameToken))
        self.assertTrue(isinstance(tokens[1], ComparisonToken))
        self.assertTrue(isinstance(tokens[2], VersionToken))

        tokens = list(RequirementParser().tokenize("numpy == 1.3.0"))
        self.assertEqual(len(tokens), 3)
        self.assertTrue(isinstance(tokens[0], DistributionNameToken))
        self.assertTrue(isinstance(tokens[1], ComparisonToken))
        self.assertTrue(isinstance(tokens[2], VersionToken))

    def test_lexer_invalids(self):
        parser = RequirementParser()
        self.assertRaises(DepSolverError,
                lambda : parser.parse("numpy >= 1.2.3 | numpy <= 2.0.0"))

    def test_lexer_compounds(self):
        tokens = list(RequirementParser().tokenize("numpy >= 1.3.0, numpy <= 2.0.0"))
        self.assertEqual(len(tokens), 7)
        self.assertTrue(isinstance(tokens[0], DistributionNameToken))
        self.assertTrue(isinstance(tokens[1], ComparisonToken))
        self.assertTrue(isinstance(tokens[2], VersionToken))
        self.assertTrue(isinstance(tokens[3], CommaToken))
        self.assertTrue(isinstance(tokens[4], DistributionNameToken))
        self.assertTrue(isinstance(tokens[5], ComparisonToken))
        self.assertTrue(isinstance(tokens[6], VersionToken))

    def test_parser_simple(self):
        parse_dict = RequirementParser().parse("numpy >= 1.3.0")
        self.assertEqual(dict(parse_dict), {"numpy": [GEQSpecification("1.3.0")]})

    def test_parser_invalids(self):
        parser = RequirementParser()
        self.assertRaises(DepSolverError, lambda : parser.parse("numpy >= "))

    def test_parser_compounds(self):
        parse_dict = RequirementParser().parse("numpy >= 1.3.0, numpy <= 2.0.0")
        self.assertEqual(dict(parse_dict), {
                    "numpy": [
                        GEQSpecification("1.3.0"), LEQSpecification("2.0.0"),
                    ]
                })
