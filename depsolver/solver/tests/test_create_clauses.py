import unittest

from depsolver.package \
    import \
        Package
from depsolver.pool \
    import \
        Pool
from depsolver.repository \
    import \
        Repository
from depsolver.requirement \
    import \
        Requirement
from depsolver.version \
    import \
        Version

from depsolver.solver.create_clauses \
    import \
        create_depends_rule, create_install_rules, iter_conflict_rules, Rule
from depsolver.solver.sat \
    import \
        Not, Literal as L

V = Version.from_string
R = Requirement.from_string

mkl_10_1_0 = Package("mkl", V("10.1.0"))
mkl_10_2_0 = Package("mkl", V("10.2.0"))
mkl_10_3_0 = Package("mkl", V("10.3.0"))
mkl_11_0_0 = Package("mkl", V("11.0.0"))

mkl_spec = R("mkl")

numpy_1_6_0 = Package("numpy", V("1.6.0"), dependencies=[mkl_spec])
numpy_1_6_1 = Package("numpy", V("1.6.1"), dependencies=[mkl_spec])
numpy_1_7_0 = Package("numpy", V("1.7.0"), dependencies=[mkl_spec])

nomkl_numpy_1_6_0 = Package("nomkl_numpy", V("1.6.0"), provides=[R("numpy == 1.6.0")])
nomkl_numpy_1_6_1 = Package("nomkl_numpy", V("1.6.1"), provides=[R("numpy == 1.6.1")])
nomkl_numpy_1_7_0 = Package("nomkl_numpy", V("1.7.0"), provides=[R("numpy == 1.7.0")])

numpy_spec = R("numpy >= 1.4.0")

scipy_0_11_0 = Package("scipy", V("0.11.0"), dependencies=[numpy_spec])
scipy_0_12_0 = Package("scipy", V("0.12.0"), dependencies=[numpy_spec])

class TestRule(unittest.TestCase):
    def setUp(self):
        repo = Repository([mkl_10_1_0, mkl_10_2_0, mkl_10_3_0, mkl_11_0_0, numpy_1_6_0])
        pool = Pool()
        pool.add_repository(repo)

        self.pool = pool

    def test_or(self):
        rule = Rule.from_packages([mkl_10_1_0, mkl_10_2_0], self.pool)
        rule |= Not(mkl_11_0_0.id)

        self.assertTrue(rule.literals, set([mkl_11_0_0.id, mkl_10_1_0.id, mkl_10_2_0.id]))

    def test_repr(self):
        rule_repr = repr(Rule.from_packages([mkl_11_0_0, mkl_10_1_0, mkl_10_2_0], self.pool))
        self.assertEqual(rule_repr, "(+mkl-10.1.0 | +mkl-10.2.0 | +mkl-11.0.0)")

        rule_repr = repr(Rule([Not(mkl_10_2_0.id)], self.pool) \
                | Rule.from_packages([mkl_11_0_0], self.pool))
        self.assertEqual(rule_repr, "(-mkl-10.2.0 | +mkl-11.0.0)")

    def test_from_package_string(self):
        rule = Rule.from_string("mkl-11.0.0", self.pool)
        self.assertEqual(rule, Rule.from_packages([mkl_11_0_0], self.pool))

        rule = Rule.from_string("mkl-10.2.0 | mkl-11.0.0", self.pool)
        self.assertEqual(rule, Rule.from_packages([mkl_10_2_0, mkl_11_0_0], self.pool))

        rule = Rule.from_string("-mkl-10.2.0 | mkl-11.0.0", self.pool)
        self.assertEqual(rule, Rule([Not(mkl_10_2_0.id), L(mkl_11_0_0.id)], self.pool))

        rule = Rule.from_string("-mkl-10.2.0 | -mkl-11.0.0", self.pool)
        self.assertEqual(rule, Rule([Not(mkl_10_2_0.id), Not(mkl_11_0_0.id)], self.pool))

class TestCreateClauses(unittest.TestCase):
    def setUp(self):
        repo = Repository([mkl_10_1_0, mkl_10_2_0, mkl_10_3_0, mkl_11_0_0, numpy_1_6_0])
        pool = Pool()
        pool.add_repository(repo)

        self.pool = pool

    def test_create_depends_rule(self):
        r_rule = Rule.from_string(
                    "-numpy-1.6.0 | mkl-10.1.0 | mkl-10.2.0 | mkl-10.3.0 | mkl-11.0.0",
                    self.pool)
        rule = create_depends_rule(self.pool, numpy_1_6_0, R("mkl"))

        self.assertEqual(rule, r_rule)

    def test_iter_conflict_rules(self):
        # Making sure single package corner-case works
        self.assertEqual(set(), set(iter_conflict_rules(self.pool, [mkl_10_1_0])))

        # 3 packages conflicting with each other -> 3 rules (C_3^2)
        r_rules = set()
        r_rules.add(Rule.from_string("-mkl-10.1.0 | -mkl-10.2.0", self.pool))
        r_rules.add(Rule.from_string("-mkl-10.1.0 | -mkl-10.3.0", self.pool))
        r_rules.add(Rule.from_string("-mkl-10.2.0 | -mkl-10.3.0", self.pool))

        self.assertEqual(r_rules,
                set(iter_conflict_rules(self.pool, [mkl_10_1_0, mkl_10_2_0, mkl_10_3_0])))

class TestCreateInstallClauses(unittest.TestCase):
    def setUp(self):
        repo = Repository([mkl_10_1_0, mkl_10_2_0, mkl_10_3_0, mkl_11_0_0, numpy_1_6_0,
            numpy_1_6_0, numpy_1_6_1, numpy_1_7_0])
        pool = Pool()
        pool.add_repository(repo)

        self.pool = pool

    def test_create_install_rules_simple(self):
        r_rules = set()
        r_rules.add(Rule.from_string(
            "mkl-10.1.0 | mkl-10.2.0 | mkl-10.3.0 | mkl-11.0.0", self.pool))
        r_rules.add(Rule.from_string("-mkl-10.1.0 | -mkl-10.2.0", self.pool))
        r_rules.add(Rule.from_string("-mkl-10.1.0 | -mkl-10.3.0", self.pool))
        r_rules.add(Rule.from_string("-mkl-10.1.0 | -mkl-11.0.0", self.pool))
        r_rules.add(Rule.from_string("-mkl-10.2.0 | -mkl-10.3.0", self.pool))
        r_rules.add(Rule.from_string("-mkl-10.2.0 | -mkl-11.0.0", self.pool))
        r_rules.add(Rule.from_string("-mkl-10.3.0 | -mkl-11.0.0", self.pool))

        self.assertEqual(r_rules,
                set(create_install_rules(self.pool, R("mkl"))))

    def test_create_install_rules_simple_dependency(self):
        # Installed requirement has only one provide
        repo = Repository([mkl_10_1_0, mkl_10_2_0, mkl_10_3_0, mkl_11_0_0, numpy_1_7_0])
        pool = Pool()
        pool.add_repository(repo)

        r_rules = set()
        r_rules.add(Rule.from_string("numpy-1.7.0", pool))
        r_rules.add(Rule.from_string(
            "-numpy-1.7.0 | mkl-10.1.0 | mkl-10.2.0 | mkl-10.3.0 | mkl-11.0.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.1.0 | -mkl-10.2.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.1.0 | -mkl-10.3.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.1.0 | -mkl-11.0.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.2.0 | -mkl-10.3.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.2.0 | -mkl-11.0.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.3.0 | -mkl-11.0.0", pool))

        self.assertEqual(r_rules,
                set(create_install_rules(pool, R("numpy"))))

    def test_multiple_install_provides(self):
        # Installed requirement has > 1 one provide
        repo = Repository([mkl_10_1_0, mkl_10_2_0, mkl_10_3_0, mkl_11_0_0,
            numpy_1_6_1, numpy_1_7_0])
        pool = Pool()
        pool.add_repository(repo)

        r_rules = set()
        r_rules.add(Rule.from_string("numpy-1.7.0 | numpy-1.6.1", pool))
        r_rules.add(Rule.from_string("-numpy-1.7.0 | -numpy-1.6.1", pool))
        r_rules.add(Rule.from_string(
            "-numpy-1.7.0 | mkl-10.1.0 | mkl-10.2.0 | mkl-10.3.0 | mkl-11.0.0", pool))
        r_rules.add(Rule.from_string(
            "-numpy-1.6.1 | mkl-10.1.0 | mkl-10.2.0 | mkl-10.3.0 | mkl-11.0.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.1.0 | -mkl-10.2.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.1.0 | -mkl-10.3.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.1.0 | -mkl-11.0.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.2.0 | -mkl-10.3.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.2.0 | -mkl-11.0.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.3.0 | -mkl-11.0.0", pool))

        self.assertEqual(r_rules,
                set(create_install_rules(pool, R("numpy"))))

    def test_multiple_provided_names_single_install_provide(self):
        # Installed requirement has 1 one provide, but multiple provides for
        # the same name are available in the pool
        repo = Repository([mkl_10_1_0, mkl_10_2_0, mkl_10_3_0, mkl_11_0_0,
            numpy_1_6_1, numpy_1_7_0])
        pool = Pool()
        pool.add_repository(repo)

        r_rules = set()
        r_rules.add(Rule.from_string("numpy-1.7.0", pool))
        r_rules.add(Rule.from_string("-numpy-1.7.0 | -numpy-1.6.1", pool))
        r_rules.add(Rule.from_string(
            "-numpy-1.7.0 | mkl-10.1.0 | mkl-10.2.0 | mkl-10.3.0 | mkl-11.0.0", pool))
        r_rules.add(Rule.from_string(
            "-numpy-1.6.1 | mkl-10.1.0 | mkl-10.2.0 | mkl-10.3.0 | mkl-11.0.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.1.0 | -mkl-10.2.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.1.0 | -mkl-10.3.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.1.0 | -mkl-11.0.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.2.0 | -mkl-10.3.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.2.0 | -mkl-11.0.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.3.0 | -mkl-11.0.0", pool))

        self.assertEqual(r_rules,
                set(create_install_rules(pool, R("numpy == 1.7.0"))))

    def test_complex_scenario_1(self):
        repo = Repository([mkl_10_1_0, mkl_10_2_0, mkl_10_3_0, mkl_11_0_0,
            numpy_1_6_0, numpy_1_6_1, numpy_1_7_0, scipy_0_11_0, scipy_0_12_0])
        pool = Pool()
        pool.add_repository(repo)

        r_rules = set()
        r_rules.add(Rule.from_string("scipy-0.11.0 | scipy-0.12.0", pool))
        r_rules.add(Rule.from_string("-scipy-0.11.0 | -scipy-0.12.0", pool))
        r_rules.add(Rule.from_string(
                    "-scipy-0.11.0 | numpy-1.6.0 | numpy-1.6.1 | numpy-1.7.0",
                    pool))
        r_rules.add(Rule.from_string(
                    "-scipy-0.12.0 | numpy-1.6.0 | numpy-1.6.1 | numpy-1.7.0",
                    pool))
        r_rules.add(Rule.from_string("-numpy-1.7.0 | -numpy-1.6.1", pool))
        r_rules.add(Rule.from_string("-numpy-1.7.0 | -numpy-1.6.0", pool))
        r_rules.add(Rule.from_string("-numpy-1.6.0 | -numpy-1.6.1", pool))
        r_rules.add(Rule.from_string(
            "-numpy-1.7.0 | mkl-10.1.0 | mkl-10.2.0 | mkl-10.3.0 | mkl-11.0.0", pool))
        r_rules.add(Rule.from_string(
            "-numpy-1.6.1 | mkl-10.1.0 | mkl-10.2.0 | mkl-10.3.0 | mkl-11.0.0", pool))
        r_rules.add(Rule.from_string(
            "-numpy-1.6.0 | mkl-10.1.0 | mkl-10.2.0 | mkl-10.3.0 | mkl-11.0.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.1.0 | -mkl-10.2.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.1.0 | -mkl-10.3.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.1.0 | -mkl-11.0.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.2.0 | -mkl-10.3.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.2.0 | -mkl-11.0.0", pool))
        r_rules.add(Rule.from_string("-mkl-10.3.0 | -mkl-11.0.0", pool))

        self.assertEqual(r_rules,
                set(create_install_rules(pool, R("scipy"))))
