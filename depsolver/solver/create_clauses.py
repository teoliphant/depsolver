import itertools

from depsolver.errors \
    import \
        MissingRequirementInPool
from depsolver.solver.rule \
    import \
        Literal, Not, Rule

# FIXME: all that code below is a lot of crap
def iter_conflict_rules(pool, packages):
    """Create an iterator that yield every rule to fulfill the constraint that
    each package in the packages list conflicts with each other.

    The generated rules are of the form (-A | -B) for every (A, B) in the
    packages sequence (C_2^n / 2 = n(n-1)/2 for n packages)
    """
    for left, right in itertools.combinations(packages, 2):
        yield Rule([Not(left.id), Not(right.id)], pool)

def create_depends_rule(pool, package, dependency_req):
    """Creates the rule encoding that package depends on the dependency
    fulfilled by requirement.

    This dependency is of the form (-A | R1 | R2 | R3) where R* are the set of
    packages provided by the dependency requirement."""
    provided_dependencies = pool.what_provides(dependency_req, 'include_indirect')
    return Rule([Not(package.id)] + \
                 [Literal(provided.id) for provided in provided_dependencies], pool)

def create_install_rules(pool, req):
    """Creates the list of rules for the given install requirement."""
    clauses = []
    clauses_set = set()

    def _append_rule(rule):
        if not rule in clauses_set:
            clauses_set.add(rule)
            clauses.append(rule)

    def _extend_rules(rules):
        for rule in rules:
            _append_rule(rule)

    def _add_dependency_rules(req):
        provided = pool.what_provides(req, 'include_indirect')
        if len(provided) < 1:
            raise MissingRequirementInPool(req)
        else:
            obsolete_provided = pool.what_provides(req, 'any')
            _extend_rules(iter_conflict_rules(pool, obsolete_provided))

            for candidate in provided:
                for dependency_req in candidate.dependencies:
                    _append_rule(create_depends_rule(pool, candidate, dependency_req))
                    _extend_rules(_add_dependency_rules(dependency_req))
            return clauses

    provided = pool.what_provides(req)
    rule = Rule((Literal(p.id) for p in provided), pool)
    _append_rule(rule)
    return _add_dependency_rules(req)
