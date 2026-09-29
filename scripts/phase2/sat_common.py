"""
Shared utilities SAFE for both Stage A and Stage B: instance generation and
CNF evaluation. Deliberately contains NO exhaustive-enumeration code (that
lives in exhaustive_only.py, imported only by generation/Stage-B scripts) so
that Stage-A scripts (run_stage_a.py, walksat_solver.py) have no import path
to ground truth at all.
"""


def random_3sat_clauses(n, m, rng):
    clauses = []
    for _ in range(m):
        vars_ = rng.choice(n, size=3, replace=False)
        signs = rng.choice([1, -1], size=3)
        clauses.append(list(zip(vars_.tolist(), signs.tolist())))
    return clauses


def clauses_to_jsonable(clauses):
    return [[[int(v), int(s)] for (v, s) in clause] for clause in clauses]


def clauses_from_jsonable(obj):
    return [[(int(v), int(s)) for (v, s) in clause] for clause in obj]


def eval_assignment(assignment, clauses):
    for clause in clauses:
        sat = False
        for (var, sign) in clause:
            val = assignment[var]
            lit_true = (val == 1) if sign == 1 else (val == 0)
            if lit_true:
                sat = True
                break
        if not sat:
            return False
    return True


def count_violated_clauses(assignment, clauses):
    v = 0
    for clause in clauses:
        sat = False
        for (var, sign) in clause:
            val = assignment[var]
            if (val == 1) if sign == 1 else (val == 0):
                sat = True
                break
        if not sat:
            v += 1
    return v


def hamming(a, b):
    return int(sum(x != y for x, y in zip(a, b)))
