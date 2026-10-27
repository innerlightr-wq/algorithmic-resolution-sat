# ---------------------------------------------------------------------------
# VENDORED, UNMODIFIED, from the certified-resolution research workspace.
# Origin   : audit src/encode.py (query encoder, Sinz-2005 sequential counter)
# sha256   : facc5f610b3c148e65556f38eede9973eb5cc54ae06ee6230263b9f81482f722
# Vendored : 2026-10-27.  Only this provenance header was prepended; the code
#            below is byte-identical to the origin file.
# ---------------------------------------------------------------------------
"""Encoder for the farthest-solution query Q_r.

Q_r(x) = I(x) AND for every a in A: d_H(x,a) >= r+1.

d_H(x,a) = sum_i [ x_i != a_i ] = sum_i lit(i,a),  where
    lit(i,a) = x_i      if a_i = 0
    lit(i,a) = NOT x_i  if a_i = 1
so the Hamming distance to a is the cardinality of a set of literals over the
ORIGINAL n variables only.  Each 'atleast r+1' constraint is encoded with a
documented cardinality encoding (Sinz-2005 sequential counter by default;
totalizer available as an independent cross-check).

Auxiliary variables are allocated from a single monotonically increasing
counter shared by every constraint, so no two constraints can ever reuse an id.
"""
from pysat.card import CardEnc, EncType


def to_dimacs(repo_clauses):
    """repo format [[(var0, sign), ...], ...] (sign in {+1,-1}, var 0-indexed)
    -> DIMACS [[lit, ...], ...] with lit = (var+1)*sign.  Matches the project's
    own scripts/phase3/pysat_common.py:clauses_from_phase2_jsonable."""
    return [[int((v + 1) * s) for (v, s) in c] for c in repo_clauses]

ENCODINGS = {'seqcounter': EncType.seqcounter,
             'totalizer': EncType.totalizer,
             'sortnetwrk': EncType.sortnetwrk,
             'mtotalizer': EncType.mtotalizer}


def dist_literals(a):
    """Literals whose sum is d_H(x,a).  1-indexed DIMACS literals."""
    return [(i + 1) if a[i] == 0 else -(i + 1) for i in range(len(a))]


def encode_Q(repo_clauses, n, A, r, encoding='seqcounter'):
    """Build a standalone CNF for Q_r.

    Returns (cnf_clauses, n_total_vars, n_aux, status) where status is
      'cnf'     -> a real CNF to hand to a solver
      'trivial_unsat' -> r >= n, so d_H >= r+1 > n is unsatisfiable by arithmetic
    No solver is invoked here.
    """
    assert r >= 0, "radius must be nonnegative"
    out = to_dimacs(repo_clauses)

    # radius n (or more): d_H(x,a) <= n < r+1 for every x, so Q_r is UNSAT with
    # no search at all.  Recognised by arithmetic, never by a solver call.
    if r >= n:
        return None, n, 0, 'trivial_unsat'

    top = n                       # next free id; original vars are 1..n
    for a in A:
        lits = dist_literals(a)
        k = r + 1                 # we need d_H >= k, with 1 <= k <= n here
        if k == 1:
            # 'at least one literal true' is a single clause: no aux vars needed,
            # and it says exactly x != a.
            out.append(list(lits))
            continue
        enc = CardEnc.atleast(lits=lits, bound=k, top_id=top,
                              encoding=ENCODINGS[encoding])
        out.extend([list(c) for c in enc.clauses])
        # advance the shared counter past every id this constraint introduced
        used = max([top] + [abs(l) for c in enc.clauses for l in c])
        top = max(top, used)
    return out, top, top - n, 'cnf'


def write_dimacs(path, cnf, nvars):
    with open(path, 'w') as f:
        f.write(f"p cnf {nvars} {len(cnf)}\n")
        for c in cnf:
            f.write(' '.join(str(l) for l in c) + ' 0\n')


# ---------------------------------------------------------------------------
# DELIBERATELY INCORRECT variants, used only by tests/test_controls.py to show
# that the independent checks reject a broken encoder.  Never used elsewhere.
# ---------------------------------------------------------------------------

def encode_Q_BROKEN_collision(repo_clauses, n, A, r, encoding='seqcounter'):
    """BUG: top_id is never advanced, so every distance constraint reuses the
    same auxiliary variable identifiers."""
    out = to_dimacs(repo_clauses)
    if r >= n:
        return None, n, 0, 'trivial_unsat'
    top = n
    for a in A:
        lits = dist_literals(a)
        k = r + 1
        if k == 1:
            out.append(list(lits)); continue
        enc = CardEnc.atleast(lits=lits, bound=k, top_id=top,   # <-- top never advances
                              encoding=ENCODINGS[encoding])
        out.extend([list(c) for c in enc.clauses])
    mx = max([n] + [abs(l) for c in out for l in c])
    return out, mx, mx - n, 'cnf'


def encode_Q_BROKEN_offbyone(repo_clauses, n, A, r, encoding='seqcounter'):
    """BUG: encodes d_H >= r instead of d_H >= r+1."""
    out = to_dimacs(repo_clauses)
    if r > n:
        return None, n, 0, 'trivial_unsat'
    top = n
    for a in A:
        lits = dist_literals(a)
        k = max(r, 1)
        if k == 1:
            out.append(list(lits)); continue
        enc = CardEnc.atleast(lits=lits, bound=k, top_id=top,
                              encoding=ENCODINGS[encoding])
        out.extend([list(c) for c in enc.clauses])
        used = max([top] + [abs(l) for c in enc.clauses for l in c])
        top = max(top, used)
    return out, top, top - n, 'cnf'
