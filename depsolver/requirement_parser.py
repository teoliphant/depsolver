import collections
import re

import six

from depsolver.errors \
    import \
        DepSolverError
from depsolver.constraints \
    import \
        Any, Equal, GEQ, LEQ
from depsolver.version \
    import \
        Version

V = Version.from_string

_DEFAULT_SCANNER = re.Scanner([
    (r"[a-zA-Z_]\w*", lambda scanner, token: DistributionNameToken(token)),
    (r"\d[\w\.\-\+]*", lambda scanner, token: VersionToken(token)),
    (r"==", lambda scanner, token: EqualToken(token)),
    (r">=", lambda scanner, token: GEQToken(token)),
    #(r">", lambda scanner, token: ComparisonToken(token)),
    (r"<=", lambda scanner, token: LEQToken(token)),
    #(r"<", lambda scanner, token: ComparisonToken(token)),
    #(r"!=", lambda scanner, token: ComparisonToken(token)),
    (",", lambda scanner, token: CommaToken(token)),
    (" +", lambda scanner, token: None),
])

class Token(object):
    typ = None
    def __init__(self, value=None):
        self.value = value

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.value)

    # Mostly useful for testing
    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.value == other.value

class CommaToken(Token):
    typ = "comma"

class DistributionNameToken(Token):
    typ = "distribution_name"

class VersionToken(Token):
    typ = "version"

class ComparisonToken(Token):
    typ = "comparison"

class LEQToken(ComparisonToken):
    typ = "leq"

class GEQToken(ComparisonToken):
    typ = "geq"

class EqualToken(ComparisonToken):
    typ = "equal"

def iter_over_requirement(tokens):
    """Yield a single requirement 'block' (i.e. a sequence of tokens between
    comma).

    Parameters
    ----------
    tokens: iterator
        Iterator of tokens
    """
    while True:
        block = []
        token = six.next(tokens)
        try:
            while not isinstance(token, CommaToken):
                block.append(token)
                token = six.next(tokens)
            yield block
        except StopIteration as e:
            yield block
            raise e

_OPERATOR_TO_SPEC = {
        EqualToken: Equal,
        GEQToken: GEQ,
        LEQToken: LEQ,
}

def _spec_factory(comparison_token):
    klass = _OPERATOR_TO_SPEC.get(comparison_token.__class__, None)
    if klass is None:
        raise DepSolverError("Unsupported comparison token %s" % comparison_token)
    else:
        return klass

class RawRequirementParser(object):
    """A simple parser for requirement strings."""
    def __init__(self):
        self._scanner = _DEFAULT_SCANNER

    def tokenize(self, requirement_string):
        scanned, remaining = self._scanner.scan(requirement_string)
        if len(remaining) > 0:
            raise DepSolverError("Invalid requirement string: %r" % requirement_string)
        else:
            return iter(scanned)

    def parse(self, requirement_string):
        parsed = collections.defaultdict(list)
        tokens_stream = self.tokenize(requirement_string)
        for requirement_block in iter_over_requirement(tokens_stream):
            if len(requirement_block) == 3:
                distribution, operator, version = requirement_block
                parsed[distribution.value].append(_spec_factory(operator)(version.value))
            elif len(requirement_block) == 1:
                distribution = requirement_block[0]
                parsed[distribution.value].append(Any())
            else:
                raise DepSolverError("Invalid requirement block: %s" % requirement_block)

        return parsed
