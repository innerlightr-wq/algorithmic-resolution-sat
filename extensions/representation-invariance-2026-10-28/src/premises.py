"""Independent checks of the premises this exploration depends on, and the
interface-size arithmetic for the ETH design.

All exact: GF(2) linear algebra over integers mod 2, exact rationals, exhaustive
enumeration.  Nothing here audits a claim this exploration does not use.
"""
import itertools, sys, math
from fractions import Fraction

FAILS = []
def check(name, ok, detail=''):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}{('  -- ' + detail) if detail else ''}")
    if not ok: FAILS.append(name)
    return ok

# ===================================================== GF(2) helpers (exact)
def rank2(rows, n):
    rows = [r for r in rows]; piv = []; rk = 0
    for c in range(n):
        p = next((i for i in range(rk, len(rows)) if (rows[i] >> c) & 1), None)
        if p is None: continue
        rows[rk], rows[p] = rows[p], rows[rk]
        for i in range(len(rows)):
            if i != rk and (rows[i] >> c) & 1: rows[i] ^= rows[rk]
        rk += 1
    return rk

def solvable(rows, b, n):
    """Ax = b over GF(2):  solvable iff rank(A) == rank([A|b])."""
    aug = [(rows[i] << 1) | b[i] for i in range(len(rows))]
    return rank2(rows, n) == rank2(aug, n + 1) - (0 if rank2(rows, n) == rank2(aug, n+1) else 0) \
        if False else _solv(rows, b, n)

def _solv(rows, b, n):
    ra = rank2(list(rows), n)
    aug = [(rows[i] | (b[i] << n)) for i in range(len(rows))]
    rb = rank2(aug, n + 1)
    return ra == rb

# =============== P1. ERV premise: the DECISION is encoding-invariant; only the
#                     OBSERVABLE moves.  Theorem 1 is about sign(grad O).
def test_decision_invariant_observable_not(n=6, trials=300):
    rngs = _lcg(4242)
    diff_dec = 0; diff_obs = 0; diff_obs_stale = 0; n_incons = 0; tested = 0
    for _ in range(trials):
        m = 1 + rngs() % (2 * n)
        rows = [rngs() % (1 << n) for _ in range(m)]
        b = [rngs() & 1 for _ in range(m)]
        # decision, computed twice by two genuinely different routes
        d1 = _solv(rows, b, n)                                # Gaussian elimination
        d2 = any(all(bin(r & x).count('1') % 2 == bb for r, bb in zip(rows, b))
                 for x in range(1 << n))                      # brute force
        tested += 1
        if d1 != d2: diff_dec += 1
        # the two encodings' observable O(E) = (#constraints)/n.
        # CORRECTED 2026-10-28 (external review, second pass): this consumer
        # still sized the closure by 2^rank(A).  The closure is spanned by
        # whole EQUATIONS, so the size is 2^rank[A|b] (see test_closure_size).
        # The headline disagreement count is 295/300 EITHER WAY, which is
        # exactly why checking only the headline would have missed this.
        o1 = Fraction(sum(bin(r).count('1') for r in rows) + m, n)   # sparse E1
        rk = rank2(list(rows), n)
        rk_aug = rank2([rows[i] | (b[i] << n) for i in range(m)], n + 1)
        o2 = Fraction((1 << rk_aug), n)                              # closure E2
        if rk_aug != rk: n_incons += 1
        if o1 != o2: diff_obs += 1
        if o1 != Fraction((1 << rk), n): diff_obs_stale += 1
    check('the LINSAT decision is identical under both encodings on every '
          'instance, by two independent computations (GF(2) elimination and '
          'brute force)', diff_dec == 0, f'{tested} systems, 0 disagreements')
    check('while the constraint-count observable O(E) differs between the two '
          'encodings on essentially every instance -- so Theorem 1 varies an '
          'OBSERVABLE, not a classification decision', diff_obs > 0.9 * tested,
          f'{diff_obs} of {tested} instances have O(E1) != O(E2), with the '
          f'closure sized by the AUGMENTED rank')
    check('and the headline count is insensitive to the closure-size bug: it '
          'is identical whether the closure is sized by rank(A) or by '
          'rank[A|b], even though the two differ on the inconsistent systems '
          '-- so this check alone could never have caught the stale '
          'calculation', diff_obs == diff_obs_stale,
          f'{diff_obs} vs {diff_obs_stale} of {tested}, while {n_incons} of '
          f'{tested} systems are inconsistent and so have different closure '
          f'sizes under the two formulas')

def _lcg(seed):
    s = [seed]
    def nxt():
        s[0] = (s[0] * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        return s[0] >> 33
    return nxt

# =============== P2. The closure encoding is exponential except at log rank.
# CORRECTED 2026-10-28 (external review).  The first version computed the span
# of the ROWS OF A, discarding b, and compared it against 2^rank(A).  That is a
# different object from Closure(A,b), whose members are whole EQUATIONS
# including their right-hand sides.  The correct identity is
#       |Closure(A,b)| = 2^rank[A | b]           (augmented rank)
# and 2^rank(A) is wrong in general.  Reviewer's minimal counterexample: the
# equations x = 0 and x = 1 give |Closure| = 4 while 2^rank(A) = 2.  Note those
# two equations are INCONSISTENT, which is exactly when the two ranks differ:
#       rank[A|b] = rank(A)      iff   the system is consistent (Rouche-Capelli)
#       rank[A|b] = rank(A) + 1  iff   it is inconsistent.
# So the alternative repair -- assuming consistency -- also works, and is now
# tested as a separate case.  Either way rank[A|b] <= rank(A) + 1, so the
# log-rank polynomial-size conclusion survives unchanged.
def closure(rows, b):
    """All GF(2) sums of subsets of the EQUATIONS (coefficients and rhs)."""
    span = {0}
    for r, bb in zip(rows, b):
        eq = (bb << 32) | r              # rhs kept above the coefficient block
        span |= {s ^ eq for s in span}
    return span


def test_closure_size(n=10, trials=200):
    rngs = _lcg(1)
    bad_aug, bad_consistent, fullrank, incons = [], [], [], 0
    for _ in range(trials):
        m = n + 2
        rows = [rngs() % (1 << n) for _ in range(m)]
        b = [rngs() & 1 for _ in range(m)]
        rk = rank2(list(rows), n)
        aug = [rows[i] | (b[i] << n) for i in range(m)]
        rk_aug = rank2(aug, n + 1)
        size = len(closure(rows, b))
        if size != (1 << rk_aug):
            bad_aug.append((rk_aug, size))
        if rk_aug == rk:                              # consistent system
            if size != (1 << rk):
                bad_consistent.append((rk, size))
        else:
            incons += 1
            if rk_aug != rk + 1:
                bad_aug.append(('rank gap', rk, rk_aug))
        if rk == n:
            fullrank.append(size)
    check('|Closure(A,b)| = 2^rank[A | b] exactly -- the AUGMENTED rank, since '
          'the closure is spanned by whole equations including their '
          'right-hand sides', not bad_aug,
          f'{trials} systems, 0 mismatches; {incons} were inconsistent, and '
          f'for those rank[A|b] = rank(A) + 1 in every case')
    check('on CONSISTENT systems the two ranks agree (Rouche-Capelli), so '
          '2^rank(A) is also correct there -- adding consistency as a '
          'hypothesis is the alternative repair', not bad_consistent,
          f'{trials - incons} consistent systems, 0 mismatches')
    # REGRESSION: the reviewer's inconsistent minimal example
    rows, b = [0b1, 0b1], [0, 1]                       # x = 0  and  x = 1
    size = len(closure(rows, b))
    rk = rank2(list(rows), 1)
    rk_aug = rank2([rows[i] | (b[i] << 1) for i in range(2)], 2)
    check('REGRESSION (inconsistent system x = 0, x = 1): |Closure| = 4 = '
          '2^rank[A|b], and 2^rank(A) = 2 is wrong -- the case that refuted '
          'the first version of this check',
          size == 4 and (1 << rk_aug) == 4 and (1 << rk) == 2,
          f'|Closure| = {size}, 2^rank[A|b] = {1 << rk_aug}, '
          f'2^rank(A) = {1 << rk}')
    check('the closure encoding is therefore polynomial only on a log-rank '
          'family: rank[A|b] <= rank(A) + 1, so the conclusion survives the '
          'correction, but full-rank systems give |Closure| = 2^(n+1) at worst',
          bool(fullrank) and max(fullrank) >= (1 << n),
          f'{len(fullrank)} of {trials} full-rank instances, '
          f'|Closure| up to {max(fullrank) if fullrank else 0} '
          f'(2^{n} = {1 << n}, 2^{n+1} = {1 << (n+1)})')


# =============== P3. An OR clause is not an XOR equation.
def test_or_is_not_xor(kmax=4):
    rows = []
    for k in range(2, kmax + 1):
        orsat = {x for x in itertools.product((0,1), repeat=k) if any(x)}
        xorsat = {x for x in itertools.product((0,1), repeat=k) if sum(x) % 2 == 1}
        rows.append((k, len(orsat), len(xorsat), orsat == xorsat))
        print(f"       k={k}: |sat(OR)|={len(orsat):>3}  |sat(XOR)|={len(xorsat):>3}  "
              f"equal={orsat == xorsat}")
    check('an OR clause and an XOR equation on the same k variables have '
          'different solution sets for every k >= 2, so a result about GF(2) '
          'linear systems does not transfer to CNF-SAT by renaming',
          all(not r[3] for r in rows), 'sat(OR) = 2^k - 1, sat(XOR) = 2^(k-1)')

# =============== P4. Aut(phi) is variable permutations ONLY, so a zero
#                     quotient reduction does not mean "no symmetry".
def clause_set_aut(clauses, n):
    """Variable permutations sigma with sigma(clauses) = clauses, as Def 3."""
    cs = frozenset(frozenset(c) for c in clauses)
    out = []
    for perm in itertools.permutations(range(1, n + 1)):
        mp = {i + 1: perm[i] for i in range(n)}
        img = frozenset(frozenset((1 if l > 0 else -1) * mp[abs(l)] for l in c)
                        for c in clauses)
        if img == cs: out.append(perm)
    return out

def sat_set(clauses, n):
    out = set()
    for bits in itertools.product((0, 1), repeat=n):
        if all(any((bits[abs(l)-1] == 1) == (l > 0) for l in c) for c in clauses):
            out.add(bits)
    return out

def test_trivial_aut_with_real_symmetry(n=4):
    """Search for a CNF with |Aut(phi)| = 1 (so Delta_theory = 0, rho = 0 and
    the symmetry-breaking efficiency is undefined) whose SOLUTION SET is
    nonetheless closed under global complementation -- an exact two-fold
    redundancy the variable-permutation quotient cannot see."""
    rngs = _lcg(31337)
    lits = [l for v in range(1, n+1) for l in (v, -v)]
    found = None; tried = 0
    while tried < 60000 and found is None:
        tried += 1
        m = 2 + rngs() % 4
        cl = []
        for _ in range(m):
            k = 2 + rngs() % 2
            vs = set()
            while len(vs) < k: vs.add(1 + rngs() % n)
            cl.append(tuple(sorted((v if rngs() & 1 else -v) for v in vs)))
        cl = sorted(set(cl))
        S = sat_set(cl, n)
        if len(S) < 2: continue
        comp_closed = all(tuple(1 - b for b in s) in S for s in S)
        if not comp_closed: continue
        if len(clause_set_aut(cl, n)) != 1: continue
        found = (cl, S)
    if found:
        cl, S = found
        print(f"       witness CNF (n={n}): {cl}")
        print(f"       solutions: {sorted(S)}   |S| = {len(S)}")
        print(f"       |Aut(phi)| = 1  =>  Delta_theory = log|S| - log|S/Aut| = 0, rho = 0")
        print(f"       yet x -> complement(x) is a fixed-point-free involution of S")
    check('a CNF exists with |Aut(phi)| = 1 -- zero quotient reduction, '
          'rho = 0, symmetry-breaking efficiency undefined -- whose solution '
          'set is still closed under global complementation; so zero reduction '
          'under the variable-permutation quotient does not mean the instance '
          'has no exploitable symmetry', found is not None,
          f'found after {tried} random CNFs' if found else f'none in {tried}')
    return found

# =============== P5. A solution-preserving transformation leaves the ensemble.
def test_ensemble_not_preserved(n=64, m=273):
    """A uniform random 3-CNF has every clause of width exactly 3 and density
    m/n.  A definitional (Tseitin) extension adds a variable and clauses of
    widths 2,2,3.  Exact arithmetic, no sampling needed."""
    before = {'n': n, 'm': m, 'density': Fraction(m, n), 'widths': {3: m}}
    # one Tseitin definition  z <-> x1 AND x2  is  (~x1 | ~x2 | z)(x1|~z)(x2|~z)
    after = {'n': n + 1, 'm': m + 3, 'density': Fraction(m + 3, n + 1),
             'widths': {3: m + 1, 2: 2}}
    print(f"       before: n={before['n']} m={before['m']} "
          f"density={before['density']}={float(before['density']):.4f} "
          f"widths={before['widths']}")
    print(f"       after : n={after['n']} m={after['m']} "
          f"density={after['density']}={float(after['density']):.4f} "
          f"widths={after['widths']}")
    check('a single solution-preserving definitional extension changes both the '
          'clause-width distribution and the density, so its image is not in '
          'the uniform random 3-CNF ensemble; a threshold statement about that '
          'ensemble therefore does not transfer to the transformed family',
          after['widths'] != before['widths'] and after['density'] != before['density'],
          f"density {before['density']} -> {after['density']}, and width-2 "
          f"clauses appear where the ensemble has none")

# NOTE.  The interface-size arithmetic that was drafted here has been moved to
# src/interface.py, which supersedes it: the version here used a single weak bar
# and two predicted constants that the computation refuted.

if __name__ == '__main__':
    print('=' * 92); print('PREMISE CHECKS AND INTERFACE ARITHMETIC'); print('=' * 92)
    print('\n-- P1. decision versus observable --'); test_decision_invariant_observable_not()
    print('\n-- P2. closure encoding size --'); test_closure_size()
    print('\n-- P3. OR versus XOR --'); test_or_is_not_xor()
    print('\n-- P4. trivial Aut with a real symmetry --'); test_trivial_aut_with_real_symmetry()
    print('\n-- P5. ensemble preservation --'); test_ensemble_not_preserved()
    print(f"\n  {'ALL PASS' if not FAILS else 'FAILURES: ' + '; '.join(FAILS)}")
    sys.exit(1 if FAILS else 0)
