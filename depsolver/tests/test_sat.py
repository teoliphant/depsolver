import collections
import unittest

from depsolver.sat \
    import \
        Clause, Literal, is_satisfiable

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

class TestClause(unittest.TestCase):
    def test_simple(self):
        a = Literal("a")
        b = Literal("b")
        clause = Clause([a, b])

        self.assertEqual(clause.literal_names, set(["a", "b"]))

    def test_create_from_string(self):
        clause = Clause.from_string("a | b | ~c")

        self.assertEqual(clause.literal_names, set(["a", "b", "c"]))
        self.assertTrue(clause.evaluate({"a": False, "b": False, "c": False}))

        clause = Clause.from_string("a | b | c")

        self.assertEqual(clause.literal_names, set(["a", "b", "c"]))
        self.assertFalse(clause.evaluate({"a": False, "b": False, "c": False}))

    def test_or(self):
        a = Literal("a")
        b = Literal("b")
        clause = Clause([a, b])
        clause |= Literal("c")

        self.assertEqual(clause.literal_names, set(["a", "b", "c"]))

        a = Literal("a")
        b = Literal("b")
        clause = Clause([a, b])

        c = Literal("c")
        d = Literal("d")
        clause |= Clause([c, d])

        self.assertEqual(clause.literal_names, set(["a", "b", "c", "d"]))

    def test_repr(self):
        a = Literal("a")
        b = Literal("b")
        clause = Clause([a, b])

        self.assertEqual(repr(clause), "C(a | b)")

        a = Literal("a")
        b = ~Literal("b")
        clause = Clause([a, b])

        self.assertEqual(repr(clause), "C(a | ~b)")

    def test_evaluate(self):
        a = Literal("a")
        b = Literal("b")
        clause = Clause([a, b])

        self.assertTrue(clause.evaluate({"a": True, "b": True}))
        self.assertFalse(clause.evaluate({"a": False, "b": False}))

        self.assertRaises(ValueError, lambda: clause.evaluate({"a": False}))

class TestSAT(unittest.TestCase):
    def test_simple(self):
        clause = Literal("a") | Literal("b")

        res, variables = is_satisfiable(set([clause]))
        self.assertTrue(res)
        self.assertTrue(variables in [{"a": True, "b": True}, {"a": True, "b": False},
                                      {"a": False, "b": True}])

        clause = Literal("a") | ~Literal("b")

        res, variables = is_satisfiable(set([clause]))
        self.assertTrue(res)
        self.assertTrue(variables in [{"a": True, "b": True}, {"a": True, "b": False},
                                      {"a": False, "b": False}])

    def test_clauses(self):
        clause1 = Clause([Literal("a")])
        clause2 = Clause([~Literal("a")])

        res, variables = is_satisfiable(set([clause1, clause2]))
        self.assertFalse(res)

        clause1 = Clause([Literal("a"), Literal("b")])
        clause2 = Clause([~Literal("a")])

        res, variables = is_satisfiable(set([clause1, clause2]))
        self.assertTrue(res)
        self.assertTrue(variables, {"a": False, "b": True})

    def test_existing_variables(self):
        clause1 = Clause([Literal("a"), Literal("b")])
        clause2 = Clause([~Literal("a")])

        res, variables = is_satisfiable(set([clause1, clause2]))
        self.assertTrue(res)

        res, variables = is_satisfiable(set([clause1, clause2]),
                collections.OrderedDict({"a": True}))
        self.assertFalse(res)
