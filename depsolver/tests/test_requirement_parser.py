import unittest

from depsolver.errors \
    import \
        DepSolverError
from depsolver.requirement_parser \
    import \
        RawRequirementParser, CommaToken, DistributionNameToken, EqualToken, \
        GEQToken, LEQToken, VersionToken, EqualSpecification, \
        GEQSpecification, LEQSpecification

class TestRawRequirementParser(unittest.TestCase):
    def test_lexer_simple(self):
        r_tokens = [DistributionNameToken("numpy"), GEQToken(">="),
                VersionToken("1.3.0")]
        tokens = list(RawRequirementParser().tokenize("numpy >= 1.3.0"))
        self.assertEqual(tokens, r_tokens)

        r_tokens = [DistributionNameToken("numpy"), LEQToken("<="),
                VersionToken("1.3.0")]
        tokens = list(RawRequirementParser().tokenize("numpy <= 1.3.0"))
        self.assertEqual(tokens, r_tokens)

        r_tokens = [DistributionNameToken("numpy"), EqualToken("=="),
                VersionToken("1.3.0")]
        tokens = list(RawRequirementParser().tokenize("numpy == 1.3.0"))
        self.assertEqual(tokens, r_tokens)

    def test_lexer_invalids(self):
        parser = RawRequirementParser()
        self.assertRaises(DepSolverError,
                lambda : parser.parse("numpy >= 1.2.3 | numpy <= 2.0.0"))

    def test_lexer_compounds(self):
        r_tokens = [DistributionNameToken("numpy"), GEQToken(">="),
                VersionToken("1.3.0"), CommaToken(","),
                DistributionNameToken("numpy"), LEQToken("<="),
                VersionToken("2.0.0")]
        tokens = list(RawRequirementParser().tokenize("numpy >= 1.3.0, numpy <= 2.0.0"))
        self.assertEqual(tokens, r_tokens)

    def test_parser_simple(self):
        parse_dict = RawRequirementParser().parse("numpy >= 1.3.0")
        self.assertEqual(dict(parse_dict), {"numpy": [GEQSpecification("1.3.0")]})

        parse_dict = RawRequirementParser().parse("numpy <= 1.3.0")
        self.assertEqual(dict(parse_dict), {"numpy": [LEQSpecification("1.3.0")]})

        parse_dict = RawRequirementParser().parse("numpy == 1.3.0")
        self.assertEqual(dict(parse_dict), {"numpy": [EqualSpecification("1.3.0")]})

    def test_parser_invalids(self):
        parser = RawRequirementParser()
        self.assertRaises(DepSolverError, lambda : parser.parse("numpy >= "))

    def test_parser_compounds(self):
        parse_dict = RawRequirementParser().parse("numpy >= 1.3.0, numpy <= 2.0.0")
        self.assertEqual(dict(parse_dict), {
                    "numpy": [
                        GEQSpecification("1.3.0"), LEQSpecification("2.0.0"),
                    ]
                })
