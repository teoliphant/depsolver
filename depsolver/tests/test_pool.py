import unittest

from depsolver.errors \
    import \
        MissingPackageInPool

from depsolver.package \
    import \
        Package
from depsolver.pool \
    import \
        MATCH, MATCH_NAME, MATCH_PROVIDE, Pool
from depsolver.repository \
    import \
        Repository
from depsolver.requirement \
    import \
        Requirement
from depsolver.version \
    import \
        Version

V = Version.from_string
R = Requirement.from_string

mkl_10_1_0 = Package("mkl", V("10.1.0"))
mkl_10_2_0 = Package("mkl", V("10.2.0"))
mkl_10_3_0 = Package("mkl", V("10.3.0"))
mkl_11_0_0 = Package("mkl", V("11.0.0"))

numpy_1_6_0 = Package("numpy", V("1.6.0"), dependencies=[R("mkl")])
numpy_1_6_1 = Package("numpy", V("1.6.1"), dependencies=[R("mkl")])
numpy_1_7_0 = Package("numpy", V("1.7.0"), dependencies=[R("mkl >= 11.0.0")])

nomkl_numpy_1_7_0 = Package("nomkl_numpy", V("1.7.0"), provides=[R("numpy == 1.7.0")])

class TestPool(unittest.TestCase):
    def test_simple(self):
        repo1 = Repository([mkl_10_1_0, mkl_10_2_0])
        pool = Pool()
        pool.add_repository(repo1)

        self.assertEqual(mkl_10_1_0, pool.package_by_id(mkl_10_1_0.id))
        self.assertEqual(mkl_10_2_0, pool.package_by_id(mkl_10_2_0.id))
        self.assertRaises(MissingPackageInPool, lambda: pool.package_by_id(mkl_10_3_0.id))

    def test_add_repository(self):
        """Ensures we do not add the same package twice."""
        repo1 = Repository([mkl_10_1_0, mkl_10_2_0])
        pool = Pool()
        pool.add_repository(repo1)

        repo2 = Repository([mkl_10_1_0])
        pool.add_repository(repo2)

        self.assertEqual(len(pool.what_provides(R("mkl"))), 2)

    def test_matches(self):
        pool = Pool()
        self.assertEqual(pool.matches(mkl_10_1_0, R("mkl")), MATCH)
        self.assertEqual(pool.matches(mkl_10_1_0, R("mkl >= 10.2.0")), MATCH_NAME)
        self.assertEqual(pool.matches(mkl_10_1_0, R("numpy")), False)
        self.assertEqual(pool.matches(nomkl_numpy_1_7_0, R("numpy")), MATCH_PROVIDE)

    def test_what_provides_simple(self):
        repo1 = Repository([numpy_1_6_0, numpy_1_7_0])
        pool = Pool()
        pool.add_repository(repo1)

        self.assertEqual(set(pool.what_provides(R("numpy"))), set([numpy_1_6_0, numpy_1_7_0]))
        self.assertEqual(pool.what_provides(R("numpy >= 1.6.1")), [numpy_1_7_0])

        repo1 = Repository([nomkl_numpy_1_7_0])
        pool = Pool()
        pool.add_repository(repo1)

        self.assertEqual(pool.what_provides(R("numpy")), [nomkl_numpy_1_7_0])

    def test_what_provides_direct_only(self):
        repo1 = Repository([nomkl_numpy_1_7_0])
        pool = Pool()
        pool.add_repository(repo1)

        self.assertEqual(set(pool.what_provides(R("numpy"))), set([nomkl_numpy_1_7_0]))

    def test_what_provides_include_indirect(self):
        repo1 = Repository([numpy_1_6_0, numpy_1_7_0, nomkl_numpy_1_7_0])
        pool = Pool()
        pool.add_repository(repo1)

        self.assertEqual(pool.what_provides(R("numpy >= 1.6.1")), [numpy_1_7_0])
        self.assertEqual(set(pool.what_provides(R("numpy"), 'include_indirect')),
                         set([numpy_1_6_0, numpy_1_7_0, nomkl_numpy_1_7_0]))
        self.assertEqual(set(pool.what_provides(R("numpy >= 1.6.1"), 'include_indirect')),
                         set([numpy_1_7_0, nomkl_numpy_1_7_0]))
        self.assertEqual(set(pool.what_provides(R("numpy >= 1.6.1"), 'direct_only')),
                         set([numpy_1_7_0]))
        self.assertEqual(set(pool.what_provides(R("numpy >= 1.6.1"), 'any')),
                         set([numpy_1_6_0, numpy_1_7_0, nomkl_numpy_1_7_0]))
