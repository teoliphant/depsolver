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
from depsolver.solver.policy \
    import \
        DefaultPolicy

P = Package.from_string

mkl_10_3_0 = P("mkl-10.3.0")
mkl_11_0_0 = P("mkl-11.0.0")

class TestDefaultPolicy(unittest.TestCase):
    def test_simple(self):
        """Ensure the policy returns the highest version across a set of
        packages with the same name."""
        r_candidates = [mkl_10_3_0.id, mkl_11_0_0.id]
        repository = Repository([mkl_10_3_0, mkl_11_0_0])

        pool = Pool()
        pool.add_repository(repository)

        policy = DefaultPolicy()

        candidates = policy.prefered_package_ids(pool, {}, r_candidates)
        self.assertEqual(list(candidates), [mkl_11_0_0.id])

    def test_simple_fulfilled_installed(self):
        """Ensure the policy returns the installed version first if it fulfills
        the requirement, even if higher versions are available."""
        r_candidates = [mkl_10_3_0.id, mkl_11_0_0.id]
        repository = Repository([mkl_10_3_0, mkl_11_0_0])

        pool = Pool()
        pool.add_repository(repository)

        policy = DefaultPolicy()

        candidates = policy.prefered_package_ids(pool, {mkl_10_3_0.id: mkl_10_3_0}, r_candidates)
        self.assertEqual(list(candidates), [mkl_10_3_0.id, mkl_11_0_0.id])
