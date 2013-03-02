import re

import six

from depsolver.package \
    import \
        Package
from depsolver.version \
    import \
        Version

_IS_VALID_LITERAL = re.compile("[a-zA-Z_0-9][-+.\w\d]*")

class Literal(object):
    """Creates a simple Literal to be used within clauses.

    Parameters
    ----------
    name: str
        Name of the literal (must consists of alphanumerical characters only)
    """
    def __init__(self, name):
        if not _IS_VALID_LITERAL.match(name):
            raise ValueError("Invalid literal name: %s" % name)
        self._name = name

    @property
    def name(self):
        return self._name

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.name == other._name

    def __hash__(self):
        return hash(repr(self))

    def __repr__(self):
        return "L('%s')" % self.name

    def __or__(self, other):
        return Clause([self, other])

    def __invert__(self):
        return Not(self.name)

    def evaluate(self, values):
        if not self.name in values:
            raise ValueError("literal %s is undefined" % self.name)
        else:
            return values[self.name]

class Not(Literal):
    def __repr__(self):
        return "L('~%s')" % self.name

    def evaluate(self, values):
        return not super(Not, self).evaluate(values)

class Clause(object):
    @classmethod
    def from_string(cls, clause_string):
        literals = []
        for literal_string in clause_string.split("|"):
            literal_string = literal_string.strip()
            if literal_string.startswith("~"):
                if len(literal_string) < 2:
                    raise ValueError("Invalid literal string: %r" % literal_string)
                else:
                    literals.append(Not(literal_string[1:]))
            else:
                literals.append(Literal(literal_string))
        return cls(literals)

    def __init__(self, literals):
        self._literals = frozenset(literals)
        self._literals_set = frozenset(l.name for l in literals)

        self._name_to_literal = dict((literal.name, literal) for literal in literals)

    @property
    def is_assertion(self):
        return len(self._literals) == 1

    @property
    def literals(self):
        return self._literals

    @property
    def literal_names(self):
        return self._literals_set

    def get_literal(self):
        if self.is_assertion:
            return six.next(iter(self._literals))
        else:
            raise ValueError("Cannot get literal from non-assertion clause !")

    def evaluate(self, values):
        ret = False
        for literal in self.literals:
            if not literal.name in values:
                raise ValueError("literal %s value is undefined" % (literal.name,))
            else:
                ret |= literal.evaluate(values)
        return ret

    def satisfies_or_none(self, values):
        """Return True if the clause is satisfied, False if not, None if it
        cannot be evaluated."""
        unset_literals = []
        for literal in self.literals:
            if literal.name in values:
                if literal.evaluate(values):
                    return True
            else:
                unset_literals.append(literal)
        if len(unset_literals) > 0:
            return None
        else:
            return False

    def __or__(self, other):
        if isinstance(other, Clause):
            literals = set(self.literals)
            literals.update(other.literals)
            return Clause(literals)
        elif isinstance(other, Literal):
            literals = set([other])
            literals.update(self.literals)
            return Clause(literals)
        else:
            raise TypeError("unsupported type %s" % type(other))

    def __repr__(self):
        def _simple_literal(l):
            return "~%s" % l.name if isinstance(l, Not) else l.name
        return "C({})".format(" | ".join(_simple_literal(l) for l in self.literals))

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.literals == other.literals

    def __hash__(self):
        return hash(self.literals)

    def is_unit(self, variables):
        """Computes whether this clause is decidable with the given variables,
        and if so, return the variable that can be decided.

        A clause is a unit if all literals but one are False for the given
        variables. If this is the case, the last literal has to be True for the
        clause to be True, and hence

        Parameters
        ----------
        variables: dict
            variable name -> bool mapping

        Returns
        -------
        is_unit: bool
            True if the rule is a unit, False otherwise
        inferred: Literal or None
            If not None, a literal instance representing the literal that can
            be inferred. If is_unit is True and inferred is None, it means the
            clause cannot be True with the given variables.

        Example
        -------
        >>> a = Clause.from_string("A | ~B | ~C")
        >>> a.is_unit({"B": True, "C": True})
        (True, L('A'))
        """
        false_literals = []
        can_be_infered = None
        for literal in self.literals:
            if literal.name in variables and not literal.evaluate(variables):
                false_literals.append(literal)
            elif not literal.name in variables:
                can_be_infered = literal

        if len(false_literals) == len(self.literals):
            return True, None
        elif len(false_literals) == len(self.literals) - 1:
            return True, can_be_infered
        else:
            return False, None

class PackageRule(Clause):
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
            package = Package(name, Version.from_string(version))
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
        super(PackageRule, self).__init__(literals)

    def __or__(self, other):
        if isinstance(other, PackageRule):
            literals = set(self.literals)
            literals.update(other.literals)
            return PackageRule(literals, self._pool)
        elif isinstance(other, Literal):
            literals = set([other])
            literals.update(self.literals)
            return PackageRule(literals, self._pool)
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
