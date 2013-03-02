import sys
import unittest

from depsolver.solver.rule \
    import \
        Rule, Literal

def expected_failure_if(condition):
    def dec(f):
        if condition:
            return unittest.expectedFailure(f)
        else:
            return f
    return dec

class TestLiteral(unittest.TestCase):
    def test_simple(self):
        a = Literal("a")
        self.assertTrue(a.evaluate({"a": True}))
        self.assertFalse(a.evaluate({"a": False}))

        self.assertFalse((~a).evaluate({"a": True}))
        self.assertTrue((~a).evaluate({"a": False}))

        self.assertRaises(ValueError, lambda: a.evaluate({}))

    def test_invalid_literal_name(self):
        self.assertRaises(ValueError, lambda: Literal("~a"))

    def test_repr(self):
        a = Literal("a")
        self.assertEqual(repr(a), "L('a')")
        self.assertEqual(repr(~a), "L('~a')")

    def test_clause(self):
        a = Literal("a")
        b = Literal("b")

        clause = a | b
        self.assertTrue(clause.evaluate({"a": True, "b": True}))
        self.assertTrue(clause.evaluate({"a": True, "b": False}))
        self.assertTrue(clause.evaluate({"a": False, "b": True}))
        self.assertFalse(clause.evaluate({"a": False, "b": False}))

class TestRule(unittest.TestCase):
    def test_simple(self):
        a = Literal("a")
        b = Literal("b")
        clause = Rule([a, b])

        self.assertEqual(clause.literal_names, set(["a", "b"]))
        self.assertFalse(clause.is_assertion)

        clause = Rule([a])

        self.assertTrue(clause.is_assertion)

    def test_create_from_string(self):
        clause = Rule.from_string("a | b | ~c")

        self.assertEqual(clause.literal_names, set(["a", "b", "c"]))
        self.assertTrue(clause.evaluate({"a": False, "b": False, "c": False}))

        clause = Rule.from_string("a | b | c")

        self.assertEqual(clause.literal_names, set(["a", "b", "c"]))
        self.assertFalse(clause.evaluate({"a": False, "b": False, "c": False}))

    def test_or(self):
        a = Literal("a")
        b = Literal("b")
        clause = Rule([a, b])
        clause |= Literal("c")

        self.assertEqual(clause.literal_names, set(["a", "b", "c"]))

        a = Literal("a")
        b = Literal("b")
        clause = Rule([a, b])

        c = Literal("c")
        d = Literal("d")
        clause |= Rule([c, d])

        self.assertEqual(clause.literal_names, set(["a", "b", "c", "d"]))

    # FIXME: fix repr not to depend on set order (which is undefined and
    # happened to change on 3.3)
    @expected_failure_if(sys.version_info >= (3, 3))
    def test_repr(self):
        a = Literal("a")
        b = Literal("b")
        clause = Rule([a, b])

        self.assertEqual(repr(clause), "C(a | b)")

        a = Literal("a")
        b = ~Literal("b")
        clause = Rule([a, b])

        self.assertEqual(clause, Rule.from_string("a | ~b"))

    def test_evaluate(self):
        a = Literal("a")
        b = Literal("b")
        clause = Rule([a, b])

        self.assertTrue(clause.evaluate({"a": True, "b": True}))
        self.assertFalse(clause.evaluate({"a": False, "b": False}))

        self.assertRaises(ValueError, lambda: clause.evaluate({"a": False}))

    def test_satisfies_or_none(self):
        clause = Rule.from_string("a | b")

        self.assertTrue(clause.satisfies_or_none({"a": True}))
        self.assertTrue(clause.satisfies_or_none({"b": True}))
        self.assertTrue(clause.satisfies_or_none({}) is None)
        self.assertTrue(clause.satisfies_or_none({"a": False}) is None)
        self.assertTrue(clause.satisfies_or_none({"a": False, "b": False}) is False)
