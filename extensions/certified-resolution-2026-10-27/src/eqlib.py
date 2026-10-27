"""Portable core for certified resolution measurement and the equal-size study.

Self-contained within this repository: it resolves every path relative to this
file and imports the repository's own `scripts/phase2` and `scripts/phase3`
modules.  No absolute scratch path, no other repository's environment, and no
shared writable dependency inode is used.

Mathematics (all proved and exhaustively validated in the research workspace;
see ../reports/):

    eps(A, I) = max_{x |= I} min_{a in A} d_H(x, a)
    Q_r(x)    = I(x) AND for every a in A: d_H(x, a) >= r + 1
    eps       = min { r : Q_r unsatisfiable }

    For B subset of A, with h(A,B) = max_{a in A} min_{b in B} d_H(a,b):
        eps(A) <= eps(B) <= eps(A) + h(A,B)
    (left: inclusion monotonicity; right: triangle inequality).

Certificate standard, never relaxed:
  * a lower bound needs a SAT model re-checked by `verify.py` on the ORIGINAL
    variables with direct Hamming distances (no SAT library, no encoder);
  * an upper bound needs a DRUP proof accepted by the pinned drat-trim;
  * UNKNOWN tightens nothing; an unchecked UNSAT is solver-reported only;
  * auxiliary variables never contribute to a distance.
"""
import os, sys, json, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
EXT = os.path.normpath(os.path.join(HERE, '..'))
REPO = os.path.normpath(os.path.join(EXT, '..', '..'))
for _p in (HERE,
           os.path.join(REPO, 'scripts', 'phase2'),
           os.path.join(REPO, 'scripts', 'phase3')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import store
from verify import eval_clauses, hamming, all_in_solution_set, check_witness

FROZEN = os.path.join(EXT, 'frozen')
DATA = os.path.join(EXT, 'data')


# --------------------------------------------------------------- frozen I/O
def load_frozen(path):
    """Load a frozen measurement and re-verify its hashes.

    A frozen record carries the original formula and an observed set.  Both
    hashes are recomputed on load, so a tampered or drifted file cannot be
    used silently.
    """
    with open(path) as f:
        d = json.load(f)
    cl = [[(int(v), int(s)) for (v, s) in c] for c in d['clauses']]
    key = 'B' if 'B' in d else 'A'
    A = [tuple(int(b) for b in a) for a in d[key]]
    assert store.hash_clauses(cl) == d['formula_hash'], f'{path}: formula drift'
    want = d.get('B_hash') if key == 'B' else d.get('A_hash')
    if want:
        assert store.hash_A(A) == want, f'{path}: observed-set drift'
    return cl, A, d


def frozen_paths(group):
    d = os.path.join(FROZEN, group)
    return sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith('.json'))


# ------------------------------------------------------------- set handling
def canonical(A):
    """Deduplicate and sort: a discovery-order-free sampling frame."""
    return sorted({tuple(int(b) for b in a) for a in A})


def dedup_preserving_order(A):
    seen, out = set(), []
    for a in A:
        t = tuple(int(b) for b in a)
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def derive_seed(study_seed, formula_hash, label, replicate, extra=''):
    """Deterministic replicate seed, with its full material recorded."""
    material = f'{study_seed}|{formula_hash}|{label}|{replicate}'
    if extra:
        material += f'|{extra}'
    digest = hashlib.sha256(material.encode()).hexdigest()
    return int(digest[:16], 16), material, digest


def subsample(A, k, study_seed, formula_hash, label, replicate, extra=''):
    """Uniform draw of k distinct members, without replacement.

    Selection never consults distance, clustering, observed resolution, or any
    desired ordering -- only the canonical index set and the derived seed.
    """
    import numpy as np
    frame = canonical(A)
    assert k <= len(frame), f'k={k} exceeds |A|={len(frame)}'
    seed, material, digest = derive_seed(study_seed, formula_hash, label,
                                         replicate, extra)
    if k == len(frame):
        idx = list(range(len(frame)))
    else:
        idx = sorted(np.random.default_rng(seed)
                     .choice(len(frame), size=k, replace=False).tolist())
    B = [frame[i] for i in idx]
    return B, dict(prng='numpy.random.Generator(PCG64)', study_seed=study_seed,
                   seed=seed, seed_material=material, seed_digest=digest,
                   frame_size=len(frame), k=k, label=label, replicate=replicate,
                   indices=idx, B_hash=store.hash_A(B))


# ------------------------------------------------------------ bound transfer
def h_cover(A, B):
    """h(A,B) = max_{a in A} min_{b in B} d_H(a,b), exact, original variables."""
    assert B, 'B must be nonempty'
    worst, arg = 0, None
    for a in A:
        d = min(hamming(a, b) for b in B)
        if d > worst:
            worst, arg = d, a
    return worst, arg


def transfer_bounds(cert_A, A, B, n):
    """Transfer a CERTIFIED interval for A to its subset B.

    Refuses outright if the source is not certified: a solver-reported upper
    bound never transfers.
    """
    if not cert_A.get('certified', True):
        raise ValueError('refusing to transfer an uncertified interval')
    h, arg = h_cover(A, B)
    return dict(lo=cert_A['lo'], hi=min(n, cert_A['hi'] + h), h=h,
                h_witness=list(arg) if arg else None,
                from_interval=[cert_A['lo'], cert_A['hi']])


def witness_lower_bound(clauses, B, x):
    """A validated satisfying assignment gives eps(B) >= min_b d_H(x,b)."""
    if not eval_clauses(clauses, x):
        return None, 'x does not satisfy the original formula'
    d = min(hamming(x, b) for b in B)
    return d, f'min distance from the validated witness to B is {d}'


# ---------------------------------------------------------- classification
def classify(W, C):
    """Conservative ordering on certified intervals.

    Overlapping intervals establish NOTHING -- in particular not equality.
    """
    LW, UW = W['lo'], W['hi']
    LC, UC = C['lo'], C['hi']
    if LC > UW:
        v = 'certified C > W'
    elif LW > UC:
        v = 'certified W > C'
    elif LW == UW == LC == UC:
        v = 'certified equality'
    else:
        v = 'unresolved'
    return dict(verdict=v, W=[LW, UW], C=[LC, UC],
                diff_lo=LC - UW, diff_hi=UC - LW)


# ------------------------------------------------------------- query policy
def select_radius(lo, hi, exhausted):
    """Policy P: longest unexhausted run in [lo, hi-1], upper midpoint.

    Equals plain bisection (lo+hi)//2 whenever nothing is exhausted, for every
    interval -- which is what makes "keep going after UNKNOWN" a pure addition
    to the baseline rather than a different search.
    """
    if lo >= hi:
        return None
    cands = [r for r in range(lo, hi) if r not in exhausted]
    if not cands:
        return None
    runs, start, prev = [], cands[0], cands[0]
    for r in cands[1:]:
        if r == prev + 1:
            prev = r
        else:
            runs.append((start, prev))
            start = prev = r
    runs.append((start, prev))
    a, b = max(runs, key=lambda ab: (ab[1] - ab[0] + 1, -ab[0]))
    return a + (b - a + 1) // 2


def decisive_radii(lo, hi, opp_lo, opp_hi):
    """Policy D: radii that can settle an ordering against [opp_lo, opp_hi].

    r = opp_hi      -- SAT there gives lo > opp_hi  => subject > opponent
    r = opp_lo - 1  -- checked UNSAT gives hi < opp_lo => opponent > subject
    """
    out = []
    for r in (opp_hi, opp_lo - 1):
        if lo <= r <= hi - 1 and r not in out:
            out.append(r)
    return out
