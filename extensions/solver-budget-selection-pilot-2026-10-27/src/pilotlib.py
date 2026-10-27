"""Core library: fresh formulas, time-budgeted collection, selection schemes.

Everything resolves relative to this file and to the repository's own
`scripts/phase2` / `scripts/phase3` modules, and to the sibling
`certified-resolution-2026-10-27` extension for the certified measurement
machinery.  No absolute path outside this repository.

SOLVER MECHANISMS ARE PRESERVED.  The only change is the stopping rule:
  * WalkSAT keeps `max_flips = 3000`, `p_noise = 0.5` and its restart
    behaviour; the restart COUNT is driven by the clock instead of `K = 150`.
  * CDCL keeps per-run clause permutation, random phase initialisation and
    `enum_models()` truncated at `T = 8`; the run COUNT is driven by the clock
    instead of `R = 5`.

THE TIMED REGION, defined once and used everywhere: the clock starts before
solver construction and covers solver initialisation, search, assignment
validation against the original formula, deduplication, and the collection
logging required to record a discovery.  Resolution measurement is entirely
outside it.  An assignment is admitted only if it was validated and accepted
strictly before the deadline.
"""
import os, sys, time, json, hashlib, random, resource

HERE = os.path.dirname(os.path.abspath(__file__))
EXT = os.path.normpath(os.path.join(HERE, '..'))
REPO = os.path.normpath(os.path.join(EXT, '..', '..'))
SIB = os.path.join(REPO, 'extensions', 'certified-resolution-2026-10-27', 'src')
for _p in (HERE, SIB,
           os.path.join(REPO, 'scripts', 'phase2'),
           os.path.join(REPO, 'scripts', 'phase3')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np
import store
from verify import eval_clauses, hamming
from sat_common import random_3sat_clauses
from walksat_solver import walksat_single_run
from pysat_common import clauses_from_phase2_jsonable, permute_clauses, \
    random_phases, unpermute_model
from pysat.solvers import Glucose3

# ---- frozen study constants (also recorded in PROTOCOL.md) ---------------
# Disjoint from every previous cohort: Stage A used 20260928+777, the n>=24
# pilot used 20261026, the equal-size study used 20261027.
CALIB_SEED = 20261028
STUDY_SEED = 20261029

N_VALUES = (32, 48, 64)
DENSITIES = (2.5, 3.5, 4.2)
FORMULAS_PER_STRATUM = 2                 # -> 18 attempted instances
BUDGETS = (5.0, 30.0)                    # cumulative seconds per solver
K_RETAIN = 40
N_REPLICATES = 3

WALKSAT = dict(max_flips=3000, p_noise=0.5)       # paper's parameters
CDCL = dict(T_per_run=8)                          # paper's truncation

SOLVERS = ('W', 'C')


# ------------------------------------------------------------- formulas
def formula_seed(n, alpha, j, base=STUDY_SEED):
    """Preserves the project's own generation convention; only the base seed
    differs, so these formulas are fresh but generated identically."""
    return base + 100000 * n + 1000 * round(10 * alpha) + j


def make_formula(n, alpha, j, base=STUDY_SEED):
    m = int(round(alpha * n))
    rng = np.random.default_rng(formula_seed(n, alpha, j, base))
    cl = random_3sat_clauses(n, m, rng)
    return cl, dict(n=n, alpha=alpha, j=j, m_clauses=m,
                    generator='scripts/phase2/sat_common.py:random_3sat_clauses',
                    seed=formula_seed(n, alpha, j, base),
                    seed_formula='base + 100000*n + 1000*round(10*alpha) + j',
                    base_seed=base, formula_hash=store.hash_clauses(cl),
                    stratum=f'n{n}_a{alpha}',
                    instance_id=instance_id(n, alpha, j))


def instance_id(n, alpha, j):
    return f'p{n}_a{alpha}_f{j}'


def cohort(base=STUDY_SEED):
    out = []
    for n in N_VALUES:
        for alpha in DENSITIES:
            for j in range(FORMULAS_PER_STRATUM):
                cl, meta = make_formula(n, alpha, j, base)
                out.append((cl, meta))
    return out


def peak_rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


# -------------------------------------------------- time-budgeted collection
class Bank:
    """Ordered distinct discoveries with monotonic acceptance timestamps."""

    def __init__(self):
        self.order = []          # tuples, first-acceptance order
        self._seen = set()
        self.accepted_at = []    # seconds from the start of the timed region
        self.duplicates = 0
        self.rejected_invalid = 0

    def offer(self, x, t_rel):
        """Accept a validated assignment, or count it as a duplicate."""
        if x in self._seen:
            self.duplicates += 1
            return False
        self._seen.add(x)
        self.order.append(x)
        self.accepted_at.append(t_rel)
        return True

    def snapshot(self, deadline):
        """Everything accepted strictly before `deadline`, in order."""
        return [x for x, t in zip(self.order, self.accepted_at) if t < deadline]

    def __len__(self):
        return len(self.order)


def collect_walksat(clauses, n, budget, seed):
    """Unbounded restarts under the clock; parameters unchanged."""
    rng = np.random.default_rng(seed)
    bank = Bank()
    restarts = 0
    t0 = time.perf_counter()
    c0 = time.process_time()
    deadline = t0 + budget
    limited = None
    while time.perf_counter() < deadline:
        found, assignment, flips = walksat_single_run(
            clauses, n, WALKSAT['max_flips'], WALKSAT['p_noise'], rng)
        restarts += 1
        if not found:
            continue
        x = tuple(int(b) for b in assignment)
        if not eval_clauses(clauses, x):          # validation is inside the budget
            bank.rejected_invalid += 1
            continue
        t_rel = time.perf_counter() - t0
        if t_rel >= budget:                       # validated too late: not admitted
            break
        bank.offer(x, t_rel)
    return bank, dict(solver='W', restarts=restarts, budget=budget, seed=seed,
                      elapsed_s=time.perf_counter() - t0,
                      cpu_s=time.process_time() - c0,
                      duplicates=bank.duplicates,
                      rejected_invalid=bank.rejected_invalid,
                      resource_limited=limited,
                      config=dict(WALKSAT), peak_rss_mb=round(peak_rss_mb(), 1))


def collect_cdcl(clauses, n, budget, seed):
    """Unbounded permuted enum_models runs under the clock, T=8 each."""
    rng = random.Random(seed)
    base = clauses_from_phase2_jsonable(clauses)
    bank = Bank()
    runs = 0
    t0 = time.perf_counter()
    c0 = time.process_time()
    deadline = t0 + budget
    limited = None
    while time.perf_counter() < deadline:
        pcl, perm = permute_clauses([list(c) for c in base], n, rng)
        phases = random_phases(n, rng)
        g = Glucose3(bootstrap_with=pcl)
        try:
            g.set_phases(phases)
            runs += 1
            cnt = 0
            for model in g.enum_models():
                y = unpermute_model(model, perm, n)
                x = tuple(int(b) for b in y)
                if not eval_clauses(clauses, x):
                    bank.rejected_invalid += 1
                else:
                    t_rel = time.perf_counter() - t0
                    if t_rel >= budget:
                        cnt = CDCL['T_per_run']
                        break
                    bank.offer(x, t_rel)
                cnt += 1
                if cnt >= CDCL['T_per_run']:
                    break
                if time.perf_counter() >= deadline:
                    break
        finally:
            g.delete()
    return bank, dict(solver='C', runs=runs, budget=budget, seed=seed,
                      elapsed_s=time.perf_counter() - t0,
                      cpu_s=time.process_time() - c0,
                      duplicates=bank.duplicates,
                      rejected_invalid=bank.rejected_invalid,
                      resource_limited=limited,
                      config=dict(CDCL), peak_rss_mb=round(peak_rss_mb(), 1))


def collection_seed(label, formula_hash, base=STUDY_SEED):
    mat = f'{base}|collect|{formula_hash}|{label}'
    return int(hashlib.sha256(mat.encode()).hexdigest()[:16], 16) % (2**32), mat


# --------------------------------------------------------- selection schemes
def prefix_set(bank_list, k):
    """First k distinct validated discoveries, chronological."""
    return list(bank_list[:k]) if len(bank_list) >= k else None


def subsample_seed(formula_hash, label, budget_label, replicate,
                   base=STUDY_SEED):
    mat = f'{base}|{formula_hash}|{label}|{budget_label}|{replicate}'
    dig = hashlib.sha256(mat.encode()).hexdigest()
    return int(dig[:16], 16), mat, dig


def uniform_set(bank_list, k, formula_hash, label, budget_label, replicate,
                base=STUDY_SEED):
    """Uniform draw of k distinct members of the recorded bank.

    The bank is canonicalised first, so the draw is independent of discovery
    order.  Selection consults only the canonical index set and the derived
    seed -- never distance, clustering, observed resolution, or any desired
    ordering.
    """
    frame = sorted(set(bank_list))
    if len(frame) < k:
        return None, None
    seed, mat, dig = subsample_seed(formula_hash, label, budget_label,
                                    replicate, base)
    if len(frame) == k:
        idx = list(range(k))
    else:
        idx = sorted(np.random.default_rng(seed)
                     .choice(len(frame), size=k, replace=False).tolist())
    B = [frame[i] for i in idx]
    return B, dict(prng='numpy.random.Generator(PCG64)', seed=seed,
                   seed_material=mat, seed_digest=dig, frame_size=len(frame),
                   k=k, label=label, budget_label=budget_label,
                   replicate=replicate, indices=idx, B_hash=store.hash_A(B))
