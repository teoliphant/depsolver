import collections

from depsolver.errors \
    import \
        DepSolverError
from depsolver.operations \
    import \
        Install, Remove, Update
from depsolver.solver.create_clauses \
    import \
        create_install_rules
from depsolver.solver.rule \
    import \
        Not

def _is_unit(clause, variables):
    false_literals = []
    can_be_infered = None
    for literal in clause.literals:
        if literal.name in variables and not literal.evaluate(variables):
            false_literals.append(literal)
        elif not literal.name in variables:
            can_be_infered = literal

    if len(false_literals) == len(clause.literals):
        return True, None
    elif len(false_literals) == len(clause.literals) - 1:
        return True, can_be_infered
    else:
        return False, None

def infer_literal(variables, literal):
    if isinstance(literal, Not):
        variables[literal.name] = False
    else:
        variables[literal.name] = True

def _run_unit_propagation(clauses, variables):
    # Unit propagatation
    iterate_over = clauses[:]
    for clause in iterate_over:
        is_unit, can_be_infered = _is_unit(clause, variables)
        if is_unit:
            #print "%s is a unit clause: pruned and used to infer %s" % (clause, can_be_infered)
            infer_literal(variables, can_be_infered)
            new_clauses = []
            for _clause in clauses:
                satisfied_or_none = _clause.satisfies_or_none(variables)
                if satisfied_or_none is None:
                    new_clauses.append(_clause)
                elif satisfied_or_none is False:
                    raise DepSolverError("Bug in unit propagation ?")
            #print "Pruned %d clauses" % (len(clauses) - len(new_clauses))
            clauses = new_clauses

    return clauses

def _prune_clauses(clauses, variables):
    # Return clauses \ {clause; clause already satifsies}
    # It also detects whether one clause evaluates to False, in which case it
    # returns None
    new_clauses = []

    # Prune clauses that are known to be already satisfied and detect if one
    # clause evaluates to False
    for clause in clauses:
        evaluated_or_none = clause.satisfies_or_none(variables)
        if evaluated_or_none is None:
            new_clauses.append(clause)
        elif evaluated_or_none is False:
            return None

    return new_clauses

def _run_prune_pure_literals(clauses, variables):
    new_clauses = []
    for clause in clauses:
        if len(clause.literals) == 1:
            literal = clause.literals[0]
            assert not literal.name in variables
            if isinstance(literal, Not):
                variables[literal.name] = False
            else:
                variables[literal.name] = True
        else:
            new_clauses.append(clause)

    return new_clauses

def _run_dpll_iteration(clauses, variables):
    # Return (should_continue, clauses) where:
    #   - should_continue is a bool on whether to continue or not
    #   - clauses is a set of clauses
    new_clauses = _prune_clauses(clauses, variables)
    if new_clauses is None:
        return False, clauses

    clauses = new_clauses
    new_clauses = _run_unit_propagation(clauses, variables)

    clauses = new_clauses
    new_clauses = _run_prune_pure_literals(clauses, variables)

    return True, new_clauses

def _compute_operations(pool, variables, installed_repo,
        id_to_installed_package, id_to_updated_package):
    operations = []

    update_package_ids = set()
    for literal_name, literal_value in variables.iteritems():
        if literal_value is True and not literal_name in id_to_installed_package:
            package = pool.package_by_id(literal_name)
            if installed_repo.has_package_name(package.name):
                to_update_packages = installed_repo.find_packages(package.name)
                assert len(to_update_packages) == 1
                to_update_package = to_update_packages[0]
                update_package_ids.add(to_update_package.id)
                operations.append(Update(to_update_package, pool.package_by_id(literal_name)))
            else:
                operations.append(Install(pool.package_by_id(literal_name)))

    for literal_name, literal_value in variables.iteritems():
        if literal_value is False and literal_name in id_to_installed_package and \
                not literal_name in update_package_ids:
            operations.append(Remove(pool.package_by_id(literal_name)))

    operations.reverse()
    return operations

def decide_from_assertion_rules(clauses, variables):
    for clause in clauses:
        if clause.is_assertion:
            literal = clause.get_literal()
            assert not literal.name in variables
            if isinstance(literal, Not):
                variables[literal.name] = False
            else:
                variables[literal.name] = True

def prune_to_best_version(pool, package_ids):
    # Assume package_ids is already sorted (from max to min)
    if len(package_ids) < 1:
        return []
    else:
        best_package = pool.package_by_id(package_ids[0])
        best_version_only = [package_ids[0]]
        for package_id in package_ids[1:]:
            package = pool.package_by_id(package_id)
            if package.version < best_package.version:
                break
            else:
                best_version_only.append(package_id)

        return best_version_only

def select_new_candidate(pool, policy, decision_queue, id_to_installed_package):
    literal_ids = (l.name for l in decision_queue)
    package_queues = \
        policy._compute_prefered_packages_installed_first(pool,
                id_to_installed_package, literal_ids)

    def package_id_to_version(package_id):
        package = pool.package_by_id(package_id)
        return package.version

    for package_name, package_queue in package_queues.iteritems():
        sorted_package_queue = sorted(package_queue, key=package_id_to_version)[::-1]
        package_queues[package_name] = sorted_package_queue

    for package_name, package_queue in package_queues.iteritems():
        package_queues[package_name] = prune_to_best_version(pool, package_queue)

    if len(package_queues) > 1:
        raise NotImplementedError("More than one package name in select " \
                                  "and install not supported yet")
    else:
        try:
            candidates = package_queues.itervalues().next()
        except StopIteration:
            raise DepSolverError("No candidate in package_queues ?")
        if len(candidates) > 1:
            raise NotImplementedError("More than one package in select " \
                                      "and install not supported yet")
        else:
            return candidates

def solve_job_clauses(clauses, job_clauses, pool, variables,
        id_to_installed_package, id_to_updated_package, policy):
    for job_clause in job_clauses:
        is_satisfied_or_none = job_clause.satisfies_or_none(variables)

        if is_satisfied_or_none is True:
            continue
        if is_satisfied_or_none is False:
            continue

        decision_queue = set(literal \
                for literal in job_clause.literals \
                if not literal.name in variables)

        if len(id_to_updated_package) > 0:
            raise NotImplementedError("update not yet implemented")
        if len(id_to_installed_package) > 0:
            old_decision_queue = decision_queue
            decision_queue = []
            for literal in job_clause.literals:
                if literal.name in id_to_updated_package:
                    decision_queue = old_decision_queue
                    break
                if literal.name in id_to_installed_package:
                    decision_queue.append(literal)
        if len(decision_queue) < 1:
            continue

        candidates = select_new_candidate(pool, policy, decision_queue, id_to_installed_package)
        # Consider new candidate installed
        assert len(candidates) == 1
        candidate = candidates[0]
        assert not candidate in variables
        variables[candidate] = True
        status, new_clauses = _run_dpll_iteration(clauses, variables)
        if status is False:
            raise NotImplementedError("Unsolvable job")
        else:
            clauses = new_clauses

    return clauses

def solve(pool, req, installed_repo, policy):
    id_to_installed_package = dict((p.id, p) for p in installed_repo.iter_packages())
    id_to_updated_package = {}

    clauses = create_install_rules(pool, req)
    job_clauses = clauses[:1]

    def _remove_duplicate(seq):
        _s = set()
        return [item for item in seq if not item in _s and not _s.add(item)]
    clauses = _remove_duplicate(clauses)

    variables = collections.OrderedDict()
    decide_from_assertion_rules(clauses, variables)

    # Handle job rules
    clauses = solve_job_clauses(clauses, job_clauses, pool, variables,
            id_to_installed_package, id_to_updated_package, policy)

    if len(clauses) == 0:
        return _compute_operations(pool, variables, installed_repo,
            id_to_installed_package, id_to_updated_package)

    while True:
        clause = clauses[0]
        satisfied_or_none = clause.satisfies_or_none(variables)
        if satisfied_or_none is True:
            clauses = clauses[1:]
            if len(clauses) < 1:
                break
            else:
                continue
        if satisfied_or_none is False:
            raise DepSolverError("Impossible situation ! And yet, it happned... (SAT bug ?)")

        # TODO: function to find out set of undecided literals of a clause
        decision_queue = list(literal for literal in clause.literals if not
                literal.name in variables)
        candidates = select_new_candidate(pool, policy, decision_queue, id_to_installed_package)
        assert len(candidates) == 1
        candidate = candidates[0]
        assert not candidate in variables
        variables[candidate] = True
        status, new_clauses = _run_dpll_iteration(clauses, variables)
        if status is False:
            variables[candidate] = False
            status, new_clauses = _run_dpll_iteration(clauses, variables)
            if status is False:
                variables.popitem()
        else:
            clauses = new_clauses
            if len(clauses) == 0:
                break

    return _compute_operations(pool, variables, installed_repo,
            id_to_installed_package, id_to_updated_package)
