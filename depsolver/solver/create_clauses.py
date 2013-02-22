import itertools

from depsolver.errors \
    import \
        MissingRequirementInPool
from depsolver.package \
    import \
        Package
from depsolver.requirement \
    import \
        Requirement
from depsolver.solver.sat \
    import \
        Clause, Not, Literal
from depsolver.version \
    import \
        Version

V = Version.from_string

class Rule(Clause):
    """A Rule is a clause where literals are package ids attached to a pool.
    
    It essentially allows for pretty-printing package names instead of internal
    ids as used by the SAT solver underneath.
    """
    @classmethod
    def from_string(cls, packages_string, pool):
        literals = []
        for package_string in packages_string.split("|"):
            package_string = package_string.strip()
            if package_string.startswith("-"):
                is_not = True
                _, name, version = package_string.split("-", 2)
            else:
                is_not = False
                name, version = package_string.split("-")
            package = Package(name, V(version))
            if is_not:
                literals.append(Not(package.id))
            else:
                literals.append(Literal(package.id))
        return cls(literals, pool)

    @classmethod
    def from_packages(cls, packages, pool):
        return cls((Literal(p.id) for p in packages), pool)

    def __init__(self, literals, pool):
        self._pool = pool
        super(Rule, self).__init__(literals)

    def __or__(self, other):
        if isinstance(other, Rule):
            literals = set(self.literals)
            literals.update(other.literals)
            return Rule(literals, self._pool)
        elif isinstance(other, Literal):
            literals = set([other])
            literals.update(self.literals)
            return Rule(literals, self._pool)
        else:
            raise TypeError("unsupported type %s" % type(other))

    def __repr__(self):
        # FIXME: this is moronic
        def _key(l):
            package = self._pool.package_by_id(l.name)
            if isinstance(l, Not):
                # XXX: insert \0 byte to force not package to appear before
                return "\0" + str(package)
            else:
                return str(package)
        def _simple_literal(l):
            package = self._pool.package_by_id(l.name)
            return "-%s" % package if isinstance(l, Not) else "+%s" % str(package)
        return "(%s)" % " | ".join(_simple_literal(l) for l in sorted(self.literals, key=_key))

def iter_conflict_rules(pool, packages):
    """Create an iterator that yield every rule to fulfill the constraint that
    each package in the packages list conflicts with each other.
    
    """
    for left, right in itertools.combinations(packages, 2):
        yield Rule([Not(left.id), Not(right.id)], pool)

def create_depends_rule(pool, package, dependency_req):
    """Creates the rule encoding that package depends on the dependency
    fulfilled by requirement."""
    provided_dependencies = pool.what_provides(dependency_req)
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
        provided = pool.what_provides(req)
        if len(provided) < 1:
            raise MissingRequirementInPool(req)
        else:
            _extend_rules(iter_conflict_rules(pool, provided))

            for candidate in provided:
                for dependency_req in candidate.dependencies:
                    _append_rule(create_depends_rule(pool, candidate, dependency_req))
                    _extend_rules(_add_dependency_rules(dependency_req))
            return clauses

    rule = Rule((Literal(p.id) for p in pool.what_provides(req)), pool)
    _append_rule(rule)
    # Add conflicts for every package with the same name to ensure conflicts
    # are generated against installed packages which version is different than
    # the ones provided by the requirement
    provided = pool.what_provides(Requirement.from_string(req.name))
    _extend_rules(iter_conflict_rules(pool, provided))
    return _add_dependency_rules(req)
