"""
STAGE B ONLY. This module reveals ground truth (full S_I via exhaustive
enumeration). It must NEVER be imported by run_stage_a.py or
walksat_solver.py or any prospective-predictor code -- this is enforced
structurally (a separate module, not just a separate function) precisely so
that a leakage bug would require an explicit new import statement in Stage-A
code, not an accidental function call within an already-shared module.
"""
import numpy as np


def gen_all_assignments(n):
    N = 1 << n
    idx = np.arange(N, dtype=np.uint32)
    bits = ((idx[:, None] >> np.arange(n)[None, :]) & 1).astype(np.int8)
    return bits


def solve_all_exhaustive(clauses, n):
    assignments = gen_all_assignments(n)
    N = assignments.shape[0]
    sat_mask = np.ones(N, dtype=bool)
    for clause in clauses:
        clause_sat = np.zeros(N, dtype=bool)
        for (var, sign) in clause:
            col = assignments[:, var]
            lit_true = (col == 1) if sign == 1 else (col == 0)
            clause_sat |= lit_true
        sat_mask &= clause_sat
        if not sat_mask.any():
            break
    sat_rows = assignments[sat_mask]
    return [tuple(int(b) for b in row) for row in sat_rows]


def is_satisfiable(clauses, n):
    return len(solve_all_exhaustive(clauses, n)) > 0
