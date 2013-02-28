from collections \
    import \
        OrderedDict

def _find_unset_variable(clauses, variables):
    for clause in clauses:
        for l in clause.literal_names:
            if not l in variables:
                return l
    return None

def _try_evaluate(clauses, variables):
    unset = _find_unset_variable(clauses, variables)
    if unset is not None:
        variables[unset] = True
        is_satisfiable, new_variables = _try_evaluate(clauses, variables)
        if is_satisfiable:
            return is_satisfiable, new_variables
        else:
            variables[unset] = False
            is_satisfiable, new_variables = _try_evaluate(clauses, variables)
            if is_satisfiable:
                return is_satisfiable, new_variables
            else:
                variables.popitem()
                return False, variables
    else:
        for clause in clauses:
            if not clause.evaluate(variables):
                return False, variables
        return True, variables

def is_satisfiable(clauses, variables=None):
    """A naive back-tracking implementation of SAT solver.
    
    Parameters
    ----------
    clauses: set
        Set of clauses instance. The set is considered as a conjunction of
        clauses
    variables: mapping
        OrderedDict containing pre-defined variables -> boolean.

    Returns
    -------
    satisfiability: bool
        True if the given instance is satisfiable
    variables: mapping
        If satisfiable, gives one found solution. The solution is a simple
        mapping variable name -> boolean.
    """
    if variables is None:
        variables = OrderedDict()
    result, result_variables = _try_evaluate(clauses, variables)
    return result, dict(result_variables)
