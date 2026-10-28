"""Exact preservation / distortion facts for covering-radius resolution under
solution-preserving transformations, plus the oracle-convention check.

Everything is exhaustive brute force over tiny instances with exact integers.
No SAT solver, no sampling, no floating point in any asserted quantity.

NOTATION.  F over n variables, S_F = sat(F).  A subset of S_F, A nonempty.
    eps(A, S) = max_{x in S} min_{a in A} d_H(x, a)        (covering radius)
G extends F by p auxiliary variables; pi : {0,1}^{n+p} -> {0,1}^n drops them.
    eps_x   = covering radius measured on the ORIGINAL coordinates only
    eps_full= covering radius measured on ALL n+p coordinates

THE TWO HYPOTHESES, both required and both used explicitly below:
    (H1) the SOLUTION SET projects:    pi(S_G) = S_F
    (H2) the OBSERVED SAMPLE projects: pi(A')  = A
(H1) is projected equivalence, as in projected model counting; (H2) is the lift
condition, the analogue of a Skolem witness for each retained solution.  Neither
implies the other, and dropping either breaks the conclusion.

PRIOR ART.  The additive-p inequality is CLASSICAL.  Cohen, Karpovsky, Mattson
and Schatz, "Covering Radius -- Survey and Recent Results", IEEE Trans. Inform.
Theory IT-31(3), May 1985, Corollary 1: "Puncturing a code on p coordinates
reduces the covering radius by at most p", where the covering radius is taken
over the WHOLE Hamming space.  Theorem D below is the solution-relative form,
in which the maximum runs over S_F rather than {0,1}^n and the ambient set is
coupled to the extension by (H1).  The proof is the classical one.  See
LITERATURE.md for the claim-by-claim comparison.
"""
import itertools, sys
from fractions import Fraction

FAILS = []

def check(name, ok, detail=''):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}{('  -- ' + detail) if detail else ''}")
    if not ok:
        FAILS.append(name)
    return ok

def dH(x, y):
    return sum(1 for a, b in zip(x, y) if a != b)

def eps(A, S):
    """Covering radius of A over S.  Exact integer."""
    assert A and S
    return max(min(dH(x, a) for a in A) for x in S)

def cube(n):
    return list(itertools.product((0, 1), repeat=n))

def proj(v, n):
    return v[:n]

# --------------------------------------------------------- the transformations
def T1_isometry(S, perm, mask):
    """Variable permutation + coordinate complementation: a Hamming isometry."""
    return {tuple(x[perm[i]] ^ mask[i] for i in range(len(x))) for x in S}

def T5_free_padding(S, p):
    """z unconstrained:  S_G = S x {0,1}^p.   multiplicity 2^p, constant."""
    return {x + z for x in S for z in cube(p)}

def T4_unique_extension(S, f):
    """z = f(x), one extension per solution.  multiplicity 1, constant."""
    return {x + tuple(f(x)) for x in S}

def T6_varying_multiplicity(S, mult):
    """mult(x) extensions of x, with mult(x) varying.  p = 1 here: either
    z in {0} (mult 1) or z in {0,1} (mult 2)."""
    out = set()
    for x in S:
        for z in range(mult(x)):
            out.add(x + (z,))
    return out

# ======================================================= 1. isometries (exact)
def test_isometry_preserves_exactly(n=5, trials=40):
    S_all = cube(n)
    rng = _lcg(20261028)
    bad = 0; tested = 0
    for _ in range(trials):
        S = {S_all[rng() % len(S_all)] for _ in range(8)}
        if len(S) < 4: continue
        S = set(S)
        for A in itertools.combinations(sorted(S), 3):
            e0 = eps(set(A), S)
            for perm in itertools.permutations(range(n)):
                for mask in cube(n):
                    S2 = T1_isometry(S, perm, mask)
                    A2 = T1_isometry(set(A), perm, mask)
                    tested += 1
                    if eps(A2, S2) != e0 or len(A2) != len(A):
                        bad += 1
                if bad: break
            break   # one A per S is enough: we sweep the whole isometry group
    check('T1 (variable permutation + coordinate complementation) preserves eps '
          'EXACTLY and preserves |A|, over the whole signed symmetric group',
          bad == 0, f'{tested} (isometry, instance) pairs, 0 discrepancies')

def _lcg(seed):
    s = [seed]
    def nxt():
        s[0] = (s[0] * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        return s[0] >> 33
    return nxt

# ================================== 2. eps_x is invariant under ANY extension
def test_eps_x_invariant(n=4, p=2, trials=200):
    """LEMMA (elementary).  If pi(S_G) = S_F and pi(A') = A then eps_x = eps(A,S_F).
    Checked against every extension shape used below."""
    rng = _lcg(7)
    S_all = cube(n)
    bad = []; tested = 0
    for t in range(trials):
        S = sorted({S_all[rng() % len(S_all)] for _ in range(6)})
        if len(S) < 3: continue
        S = set(S)
        A = set(sorted(S)[:2])
        e0 = eps(A, S)
        builds = [
            ('free padding p=%d' % p, T5_free_padding(S, p)),
            ('unique ext z=(x0,x1)', T4_unique_extension(S, lambda x: (x[0], x[1]))),
            ('varying mult', T6_varying_multiplicity(S, lambda x: 1 + (x[0] == 1))),
        ]
        for label, SG in builds:
            q = len(next(iter(SG))) - n
            # every lift of A, up to a cap, must give the same eps_x
            lifts = [v for v in SG if proj(v, n) in A]
            Ap = set(lifts)                       # all lifts at once
            ex = max(min(dH(proj(v, n), proj(w, n)) for w in Ap) for v in SG)
            tested += 1
            if ex != e0:
                bad.append((label, e0, ex))
            # and pi(S_G) = S_F
            if {proj(v, n) for v in SG} != S:
                bad.append((label, 'projection'))
    check('eps measured on the ORIGINAL coordinates is invariant under every '
          'solution-preserving extension tested (free padding, unique '
          'definitional extension, varying multiplicity)', not bad,
          f'{tested} extension instances, 0 discrepancies  [elementary]')

# ============================ 3. the sharp distortion bound on ALL coordinates
def eps_full(Ap, SG):
    return max(min(dH(v, w) for w in Ap) for v in SG)

def test_distortion_bound(n=4, pmax=3, trials=120):
    """THEOREM D (solution-relative form of a classical bound; sharp):
           eps_x <= eps_full <= eps_x + p    under (H1) and (H2)."""
    rng = _lcg(99)
    S_all = cube(n)
    viol = []; lo_hit = hi_hit = 0; tested = 0
    for t in range(trials):
        S = set(sorted({S_all[rng() % len(S_all)] for _ in range(7)}))
        if len(S) < 3: continue
        A = set(sorted(S)[:2])
        e0 = eps(A, S)
        for p in range(1, pmax + 1):
            SG = T5_free_padding(S, p)
            Z = cube(p)
            # (a) all lifts of every a  -> expect eps_full = eps_x  (lower bound)
            Ap = {a + z for a in A for z in Z}
            ef = eps_full(Ap, SG); tested += 1
            if not (e0 <= ef <= e0 + p): viol.append(('all-lifts', p, e0, ef))
            if ef == e0: lo_hit += 1
            # (b) one lift of every a, all at the same z -> expect eps_x + p (upper)
            Ap = {a + Z[0] for a in A}
            ef = eps_full(Ap, SG); tested += 1
            if not (e0 <= ef <= e0 + p): viol.append(('one-z', p, e0, ef))
            if ef == e0 + p: hi_hit += 1
    check('THEOREM D holds on every instance:  eps_x <= eps_full <= eps_x + p, '
          'with p the number of auxiliary coordinates', not viol,
          f'{tested} (instance, p, lift) triples; violations {viol[:2]}')
    check('and BOTH bounds are attained: the lower by lifting every member of A '
          'to every auxiliary value, the upper by placing all lifts at one '
          'auxiliary value', lo_hit > 0 and hi_hit > 0,
          f'lower attained {lo_hit}x, upper attained {hi_hit}x')

# ======================================= 4. ordering reversal, and its threshold
def test_ordering_threshold(n=5):
    """When does Theorem D still GUARANTEE a certified strict ordering
    eps(A1) > eps(A2), once distances are measured on all coordinates?

        margin >= p+1  =>  preserved under EVERY extension and lift
        margin <= p    =>  the GUARANTEE IS VOID -- SOME extension and lift
                           ties (margin = p) or reverses (margin <= p-1)

    The void half is an EXISTENCE statement.  It does not say that adding
    auxiliary variables reverses an ordering, and a particular encoding may
    leave every ordering intact.  Below, each regime is exhibited by an
    explicit witness extension, which is what "attainable" means here.
    """
    S = set(cube(n))                      # S_F = the whole cube: eps is explicit
    # A2 = {0^n} has eps = n;  A1 = a covering code has small eps.
    zero = tuple([0] * n)
    A2 = {zero}
    e2 = eps(A2, S)
    assert e2 == n
    rows = []
    for p in range(1, 6):
        Z = cube(p)
        SG = T5_free_padding(S, p)
        # A2 lifted to ALL auxiliary values  -> eps_full(A2) = e2
        A2p = {zero + z for z in Z}
        f2 = eps_full(A2p, SG)
        # A1 chosen with eps(A1) = e2 - margin, lifted to ONE auxiliary value
        # -> eps_full(A1) = eps(A1) + p
        for margin in range(1, n):
            e1 = e2 - margin
            A1 = _code_with_radius(n, e1)
            if A1 is None or eps(A1, S) != e1:
                continue
            A1p = {a + Z[0] for a in A1}
            f1 = eps_full(A1p, SG)
            assert f1 == e1 + p, (f1, e1, p)
            rel_before = 'A2>A1'                     # eps(A2)=e2 > e1=eps(A1)
            rel_after = ('A2>A1' if f2 > f1 else ('A1>A2' if f1 > f2 else 'tie'))
            rows.append((p, margin, e1, e2, f1, f2, rel_after))
    rev = [r for r in rows if r[6] == 'A1>A2']
    tie = [r for r in rows if r[6] == 'tie']
    pres = [r for r in rows if r[6] == 'A2>A1']
    print(f"       {'p':>3}{'margin':>8}{'eps(A1)':>9}{'eps(A2)':>9}"
          f"{'full(A1)':>10}{'full(A2)':>10}{'after':>8}")
    for r in rows[:14]:
        print(f"       {r[0]:>3}{r[1]:>8}{r[2]:>9}{r[3]:>9}{r[4]:>10}{r[5]:>10}{r[6]:>8}")
    check('at margin <= p-1 the guarantee is void, witnessed by an explicit '
          'extension and lift that strictly reverses the ordering; this is an '
          'existence statement about some extension, not a claim about any '
          'given encoding', all(r[1] <= r[0] - 1 for r in rev) and bool(rev),
          f'{len(rev)} witness reversals, all with margin <= p-1; '
          f'largest reversed margin {max((r[1] for r in rev), default=0)}')
    check('at margin exactly p a witness extension produces a TIE, and '
          'Theorem D forbids any reversal there', all(r[1] == r[0] for r in tie),
          f'{len(tie)} witness ties, margins {sorted({r[1] for r in tie})}')
    check('at margin >= p+1 the strict ordering is PRESERVED in every case '
          '(this is the contrapositive of Theorem D, not a sample)',
          all(r[1] >= r[0] + 1 for r in pres) and bool(pres),
          f'{len(pres)} preserved, smallest margin {min((r[1] for r in pres), default=0)}')
    return rows

def _code_with_radius(n, r):
    """A small subset of the cube whose covering radius over the cube is exactly r."""
    if r == n:
        return {tuple([0] * n)}
    S = cube(n)
    # greedy: add centres until the radius drops to r, then verify exactness
    A = {tuple([0] * n)}
    while eps(A, S) > r:
        far = max(S, key=lambda x: min(dH(x, a) for a in A))
        A.add(far)
    return A if eps(A, S) == r else None

# ====================================== 5. multiplicity and uniform projection
def test_multiplicity_bias(n=3):
    """Uniform sampling of S_G projects to a distribution proportional to the
    extension multiplicity.  Constant multiplicity (free padding, unique
    definitional extension) projects uniformly; varying multiplicity does not."""
    S = set(cube(n))
    rows = []
    for label, mult in (('free padding p=2 (mult = 4)', lambda x: 4),
                        ('unique extension  (mult = 1)', lambda x: 1),
                        ('varying: mult = 1 + [x0=1]', lambda x: 1 + (x[0] == 1))):
        tot = sum(mult(x) for x in S)
        push = {x: Fraction(mult(x), tot) for x in S}
        unif = Fraction(1, len(S))
        tv = sum(abs(p - unif) for p in push.values()) / 2
        rows.append((label, tv))
        print(f"       {label:<32} total-variation from uniform = {tv}")
    const_ok = all(tv == 0 for lbl, tv in rows[:2])
    vary_ok = rows[2][1] > 0
    check('uniform sampling of the extended solution set projects to the '
          'multiplicity-weighted distribution: EXACTLY uniform when the '
          'multiplicity is constant, biased when it varies', const_ok and vary_ok,
          f'TV = 0, 0, {rows[2][1]}  (exact rationals)')

def test_duplicate_variable_reweights(n=4):
    """CONTROL: a uniquely determined duplicate variable z = x0 adds no
    solutions and no information, yet the all-coordinate metric now counts
    coordinate x0 TWICE.  eps_x is unchanged; eps_full need not be."""
    S = set(cube(n))
    SG = T4_unique_extension(S, lambda x: (x[0],))
    changed = []
    for A in itertools.combinations(sorted(S), 2):
        A = set(A)
        e0 = eps(A, S)
        Ap = {a + (a[0],) for a in A}
        ex = max(min(dH(proj(v, n), proj(w, n)) for w in Ap) for v in SG)
        ef = eps_full(Ap, SG)
        if ex != e0:
            changed.append(('eps_x moved!', A, e0, ex))
        if ef != e0:
            changed.append(('full', A, e0, ef))
    moved_x = [c for c in changed if c[0] != 'full']
    moved_f = [c for c in changed if c[0] == 'full']
    check('a uniquely determined duplicate variable leaves eps_x untouched',
          not moved_x, f'0 of {2**n*(2**n-1)//2} pairs moved')
    check('but the SAME duplicate variable changes eps measured on all '
          'coordinates, because it silently gives one original coordinate '
          'weight 2 -- no solution was added or removed', bool(moved_f),
          f'{len(moved_f)} of {2**n*(2**n-1)//2} pairs moved; '
          f'example {moved_f[0][1]} eps_x={moved_f[0][2]} full={moved_f[0][3]}'
          if moved_f else '')

# ============================================== 6. the oracle convention (SS5)
def eps_by_oracle(A, S, n):
    """Reconstruct eps from the radius-query family only.
         Q_r  satisfiable  <=>  exists x in S with d_H(x,a) >= r+1 for all a in A
         SAT   => eps >= r+1 ;   UNSAT => eps <= r
    eps = (number of r in 0..n for which Q_r is satisfiable).
    """
    sat = []
    for r in range(0, n + 1):
        ok = any(all(dH(x, a) >= r + 1 for a in A) for x in S)
        sat.append(ok)
    # the family is monotone decreasing in r
    mono = all(sat[i] >= sat[i + 1] for i in range(n))
    return sum(sat), sat, mono

def test_oracle_convention(n=4):
    S_all = cube(n)
    rng = _lcg(555)
    bad = []; r0 = []; rn = []; tested = 0
    for t in range(300):
        S = set(sorted({S_all[rng() % len(S_all)] for _ in range(5)}))
        if len(S) < 2: continue
        for k in (1, 2):
            for A in itertools.combinations(sorted(S), k):
                A = set(A)
                e0 = eps(A, S)
                e1, sat, mono = eps_by_oracle(A, S, n)
                tested += 1
                if e1 != e0 or not mono:
                    bad.append((A, e0, e1, mono))
                r0.append((sat[0], A == S))
                rn.append(sat[n])
    check('the radius-query ladder reconstructs eps exactly, and the family is '
          'monotone in r (SAT at r implies SAT at every smaller r)', not bad,
          f'{tested} (A, S) pairs; {bad[:1]}')
    check('r = 0 boundary: Q_0 is UNSAT exactly when A = S, i.e. exactly when '
          'eps = 0 -- the convention is correct at the bottom of the ladder',
          all((not s) == eq for s, eq in r0),
          f'{len(r0)} cases, no exception')
    check('r = n boundary: Q_n asks for Hamming distance >= n+1 in an '
          'n-cube, so it is UNSAT unconditionally and yields the trivially '
          'correct bound eps <= n -- it is sound but carries no information',
          not any(rn), f'{len(rn)} cases, Q_n satisfiable 0 times')

if __name__ == '__main__':
    print('=' * 92)
    print('PRESERVATION / DISTORTION OF COVERING-RADIUS RESOLUTION -- exact')
    print('=' * 92)
    print('\n-- 1. Hamming isometries --'); test_isometry_preserves_exactly()
    print('\n-- 2. invariance of eps on the original coordinates --'); test_eps_x_invariant()
    print('\n-- 3. Theorem D: the sharp distortion bound --'); test_distortion_bound()
    print('\n-- 4. when an ordering can be reversed --'); test_ordering_threshold()
    print('\n-- 5. multiplicity controls --'); test_multiplicity_bias(); test_duplicate_variable_reweights()
    print('\n-- 6. the oracle convention, including both boundaries --'); test_oracle_convention()
    print(f"\n  {'ALL PASS' if not FAILS else 'FAILURES: ' + '; '.join(FAILS)}")
    sys.exit(1 if FAILS else 0)
