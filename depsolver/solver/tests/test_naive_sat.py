import collections

import unittest

from depsolver.solver.rule \
    import \
        Clause, Literal
from depsolver.solver.naive_sat \
    import \
        is_satisfiable

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
