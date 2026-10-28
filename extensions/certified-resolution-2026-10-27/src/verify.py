# ---------------------------------------------------------------------------
# VENDORED, UNMODIFIED, from the certified-resolution research workspace.
# Origin   : audit src/verify.py (independent verifier; imports no SAT library, no encoder)
# sha256   : 1966f7d1645f1ca42f136577019756ddc6f43c1913cf7ff0d953e2bed22d7d91
# Vendored : 2026-10-27.  Only this provenance header was prepended; the code
#            below is byte-identical to the origin file.
# ---------------------------------------------------------------------------
"""Independent verifier.  Imports NOTHING from encode.py and no SAT library.

Plain Boolean evaluation of the original clauses, and direct Hamming distances.
Used to check every SAT witness and, at small n, to check UNSAT exhaustively.
"""
from itertools import product


def eval_clauses(clauses, x):
    """clauses in repo format [[(var0, sign), ...], ...]; x a 0/1 tuple."""
    for clause in clauses:
        ok = False
        for (v, s) in clause:
            if (x[v] == 1 and s == 1) or (x[v] == 0 and s != 1):
                ok = True
                break
        if not ok:
            return False
    return True


def hamming(x, y):
    assert len(x) == len(y)
    return sum(1 for i in range(len(x)) if x[i] != y[i])


def check_witness(clauses, n, A, r, x):
    """A witness for 'eps_hat > r' must satisfy I and be at distance >= r+1 from all of A."""
    assert len(x) == n, "witness has wrong length"
    if not eval_clauses(clauses, x):
        return False, "witness does not satisfy the original formula"
    for a in A:
        d = hamming(x, a)
        if d < r + 1:
            return False, f"witness is at distance {d} < {r+1} from an observed assignment"
    return True, "ok"


def exhaustive_eps(clauses, n, A):
    """Reference eps_hat by full enumeration of {0,1}^n.  No solver, no encoder."""
    if not A:
        return None
    best = -1
    for x in product((0, 1), repeat=n):
        if eval_clauses(clauses, x):
            d = min(hamming(x, a) for a in A)
            if d > best:
                best = d
    return best if best >= 0 else None


def exhaustive_Q_unsat(clauses, n, A, r):
    """Independently confirm Q_r is UNSAT by enumeration over the ORIGINAL variables."""
    for x in product((0, 1), repeat=n):
        if eval_clauses(clauses, x) and all(hamming(x, a) >= r + 1 for a in A):
            return False, x
    return True, None


def all_in_solution_set(clauses, A):
    """Every observed assignment must really satisfy the formula."""
    bad = [a for a in A if not eval_clauses(clauses, a)]
    return (not bad), bad
