# ---------------------------------------------------------------------------
# VENDORED, UNMODIFIED, from the certified-resolution research workspace.
# Origin   : audit src/drup.py (pure-Python DRUP checker, retained as a cross-check)
# sha256   : 8ec39169223d2a6be6cc5ce048593fd93c2b4fa954a3dde03449364cbcd4022e
# Vendored : 2026-10-27.  Only this provenance header was prepended; the code
#            below is byte-identical to the origin file.
# ---------------------------------------------------------------------------
"""A self-contained forward DRUP proof checker.

For each clause C in the proof, check that C is a reverse-unit-propagation (RUP)
consequence of the clauses accumulated so far: assume every literal of C false,
run unit propagation, and require a conflict.  Then add C.  If the empty clause
is derived, the input formula is UNSAT.

Deletion lines are IGNORED, which is SOUND: skipping deletions can only make the
accumulated formula larger, every accumulated clause is (inductively) implied by
the original formula, and a conflict under a superset of implied clauses still
witnesses implication by the original formula.  Deletions exist only to speed up
checkers, never to make a proof valid.

This module imports no SAT library and shares no code with encode.py, so a
successful check is independent of both the solver and the cardinality encoder.
"""
import time


def _propagate(clauses, watch, assign):
    """Unit propagation.  assign: dict var -> bool.  Returns True on conflict."""
    changed = True
    while changed:
        changed = False
        for ci in range(len(clauses)):
            c = clauses[ci]
            unassigned, satisfied = [], False
            for l in c:
                v, want = abs(l), (l > 0)
                if v in assign:
                    if assign[v] == want:
                        satisfied = True
                        break
                else:
                    unassigned.append(l)
            if satisfied:
                continue
            if not unassigned:
                return True                      # conflict
            if len(unassigned) == 1:
                l = unassigned[0]
                assign[abs(l)] = (l > 0)
                changed = True
    return False


def check_proof(cnf, proof_lines, max_lines=None, max_seconds=None):
    """cnf: list of clauses (lists of ints).  proof_lines: DRUP text lines.

    Returns (ok, info).  ok=True means the empty clause was derived and every
    proof step passed its RUP check.
    """
    clauses = [list(c) for c in cnf]
    steps = kept = 0
    t0 = time.perf_counter()
    for raw in proof_lines:
        s = raw.strip()
        if not s:
            continue
        if s.startswith('d'):
            continue                             # deletion: ignored (sound)
        toks = s.split()
        if toks and toks[-1] == '0':
            toks = toks[:-1]
        C = [int(t) for t in toks]
        steps += 1
        if max_lines is not None and steps > max_lines:
            return False, f"proof exceeds the {max_lines}-step checking budget"
        if max_seconds is not None and (time.perf_counter() - t0) > max_seconds:
            return False, (f"proof checking exceeded the {max_seconds}s budget after "
                           f"{steps} of {len(proof_lines)} steps (NOT a refutation of the proof)")
        assign = {}
        for l in C:                              # assume C false
            v, want = abs(l), (l > 0)
            if v in assign and assign[v] != (not want):
                return False, f"step {steps}: clause {C} is self-contradictory under assumption"
            assign[v] = (not want)
        if not _propagate(clauses, None, assign):
            return False, (f"step {steps}: clause {C} is NOT a RUP consequence "
                           f"(no conflict under unit propagation)")
        clauses.append(C)
        kept += 1
        if not C:
            return True, f"empty clause derived and verified after {steps} RUP steps"
    return False, f"proof ended after {steps} steps without deriving the empty clause"
