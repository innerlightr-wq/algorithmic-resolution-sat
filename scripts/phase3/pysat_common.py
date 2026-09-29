"""
Shared utilities SAFE for Stage A: CNF format conversion (Phase 2's 0-indexed
signed-tuple format -> PySAT's 1-indexed signed-int format) and the
permutation/phase-randomization mechanism documented in CDCL_SOLVER.md.
Contains no ground-truth-revealing code.
"""
import random


def clauses_from_phase2_jsonable(obj):
    """Phase 2 format: [[[var0idx, sign], ...], ...] -> PySAT format: [[lit,...],...]."""
    return [[(v + 1) * s for (v, s) in clause] for clause in obj]


def permute_clauses(clauses, n, rng):
    """
    Returns (permuted_clauses, perm) where perm[i-1] = new label of original
    variable i (1-indexed). A uniformly random bijection + independent clause
    shuffle -- a mathematically exact symmetry of the CNF (identical solution
    set under the inverse relabeling), used only to vary CDCL search dynamics
    (VSIDS initial ordering, conflict-analysis traversal order).
    """
    perm = list(range(1, n + 1))
    rng.shuffle(perm)

    def relabel(lit):
        v = abs(lit)
        sign = 1 if lit > 0 else -1
        return sign * perm[v - 1]

    new_clauses = [[relabel(l) for l in c] for c in clauses]
    rng.shuffle(new_clauses)
    return new_clauses, perm


def random_phases(n, rng):
    return [(v + 1) * rng.choice([1, -1]) for v in range(n)]


def unpermute_model(model, perm, n):
    """model: list of signed ints (permuted-variable space) -> tuple of 0/1 in original variable order."""
    inv = {perm[i]: i + 1 for i in range(n)}
    orig = sorted([inv[abs(l)] * (1 if l > 0 else -1) for l in model], key=abs)
    return tuple(1 if l > 0 else 0 for l in orig)
