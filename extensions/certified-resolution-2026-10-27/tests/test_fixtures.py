"""Small self-contained fixtures. A clean checkout can run this in seconds.

Everything here is tiny enough that the truth is computed by exhaustive
enumeration, so the certified machinery is checked against ground truth rather
than against itself.

    python extensions/certified-resolution-2026-10-27/tests/test_fixtures.py

drat-trim is optional: without it, the UNSAT side is checked by enumeration
instead and the proof-checking test is reported as skipped.
"""
import os, sys, itertools, json

HERE = os.path.dirname(os.path.abspath(__file__))
EXT = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(EXT, 'src'))

import eqlib
from eqlib import canonical, subsample, h_cover, transfer_bounds, classify, \
    witness_lower_bound, select_radius, decisive_radii
import store
from verify import eval_clauses, hamming, check_witness
from encode import encode_Q
from pysat.solvers import Glucose3

FAILS = []
STUDY_SEED = 20261027


def check(name, ok, detail=''):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}{('  — ' + detail) if detail else ''}")
    if not ok:
        FAILS.append(name)
    return ok


# A fixed 8-variable formula with a known, enumerable solution set.
# Clause format is the repository's own: [(var0, sign), ...], sign in {+1,-1}.
N = 8
CLAUSES = [
    [(0, 1), (1, 1), (2, -1)],
    [(1, -1), (3, 1), (4, 1)],
    [(2, 1), (5, 1), (6, -1)],
    [(0, -1), (4, -1), (7, 1)],
    [(3, -1), (5, -1), (7, -1)],
    [(1, 1), (6, 1), (7, 1)],
]


def truth_eps(clauses, n, A):
    best = -1
    for x in itertools.product((0, 1), repeat=n):
        if eval_clauses(clauses, x):
            best = max(best, min(hamming(x, a) for a in A))
    return None if best < 0 else best


def solution_set(clauses, n):
    return [x for x in itertools.product((0, 1), repeat=n)
            if eval_clauses(clauses, x)]


def certified_eps(clauses, n, A, use_drat=True):
    """Resolve eps with the extension's own certificate standard."""
    import dratcheck
    have = use_drat and dratcheck.binary_provenance().get('exists')
    lo, hi, proofs = 0, n, 0
    while lo < hi:
        r = select_radius(lo, hi, set())
        cnf, nv, _, kind = encode_Q(clauses, n, A, r)
        if kind == 'trivial_unsat':
            hi = r
            continue
        s = Glucose3(bootstrap_with=cnf, with_proof=have)
        sat = s.solve()
        if sat:
            model = s.get_model()
            s.delete()
            pos = {l for l in model if l > 0}
            x = tuple(1 if (i + 1) in pos else 0 for i in range(n))
            ok, msg = check_witness(clauses, n, A, r, x)   # independent
            assert ok, f'witness rejected at r={r}: {msg}'
            lo = r + 1
        else:
            proof = (s.get_proof() or []) if have else []
            s.delete()
            if have and proof:
                import tempfile
                d = tempfile.mkdtemp(prefix='fx-', dir=HERE)
                try:
                    cp = os.path.join(d, 'q.cnf')
                    with open(cp, 'w') as f:
                        f.write(f'p cnf {nv} {len(cnf)}\n')
                        for c in cnf:
                            f.write(' '.join(map(str, c)) + ' 0\n')
                    pp = os.path.join(d, 'q.drup')
                    with open(pp, 'w') as f:
                        f.write('\n'.join(proof) + '\n')
                    res = dratcheck.check(cp, pp, timeout_s=120)
                    assert dratcheck.verified(res), \
                        f'proof rejected at r={r}: {res["verdict"]}'
                    proofs += 1
                finally:
                    import shutil
                    shutil.rmtree(d, ignore_errors=True)
            hi = r
    return lo, proofs, bool(have)


def test_certified_matches_enumeration():
    S = solution_set(CLAUSES, N)
    check('fixture formula has an enumerable, non-trivial solution set',
          len(S) >= 8, f'|S_I| = {len(S)}')
    for name, A in (('singleton', [S[0]]),
                    ('two solutions', canonical(S[:2])),
                    ('half the set', canonical(S[:max(2, len(S) // 2)])),
                    ('whole set', canonical(S))):
        want = truth_eps(CLAUSES, N, A)
        got, nproofs, had = certified_eps(CLAUSES, N, A)
        check(f'certified eps == enumerated eps  [{name}, |A|={len(A)}]',
              got == want, f'certified {got}, enumerated {want}'
              + (f', {nproofs} proofs checked' if had else ', drat-trim absent'))


def test_transfer_and_control():
    S = canonical(solution_set(CLAUSES, N))
    A = S                                   # full solution set: eps(A) = 0
    eA = truth_eps(CLAUSES, N, A)
    ok_all = True
    for rep in range(3):
        B, prov = subsample(A, max(1, len(A) // 3), STUDY_SEED, 'fixture', 'W', rep)
        eB = truth_eps(CLAUSES, N, B)
        h, _ = h_cover(A, B)
        if not (eA <= eB <= eA + h):
            ok_all = False
            print(f"      VIOLATED rep={rep}: {eA} <= {eB} <= {eA}+{h}")
        t = transfer_bounds(dict(lo=eA, hi=eA, certified=True), A, B, N)
        if not (t['lo'] <= eB <= t['hi']):
            ok_all = False
            print(f"      transferred interval excludes the truth: {t} vs {eB}")
    check('eps(A) <= eps(B) <= eps(A) + h(A,B) and the transferred interval '
          'contains the truth, on 3 replicates', ok_all)

    # a larger UNRELATED set can be strictly worse: monotonicity is about
    # inclusion, not cardinality
    small = [tuple([0] * N), tuple([1] * N)]
    big = [tuple([0] * N)] + [tuple(1 if j == i else 0 for j in range(N))
                              for i in range(N)]
    es = truth_eps([], N, small)
    eb = truth_eps([], N, big)
    check('control: larger unrelated set, strictly worse resolution',
          len(big) > len(small) and eb > es,
          f'|A|={len(small)} -> eps={es}; |A|={len(big)} -> eps={eb}')


def test_determinism_and_policy():
    S = canonical(solution_set(CLAUSES, N))
    a, pa = subsample(S, 3, STUDY_SEED, 'f' * 64, 'W', 0)
    b, pb = subsample(S, 3, STUDY_SEED, 'f' * 64, 'W', 0)
    ok = (a == b and pa['B_hash'] == pb['B_hash'] == store.hash_A(a))
    seeds = {subsample(S, 3, STUDY_SEED, 'f' * 64, lab, rp)[1]['seed']
             for lab in ('W', 'C') for rp in range(3)}
    ok &= (len(seeds) == 6)
    check('subsampling is deterministic and seed-distinct across label/replicate',
          ok, f'{len(seeds)} distinct seeds')
    bad = [(lo, hi) for lo in range(0, 20) for hi in range(lo + 1, 21)
           if select_radius(lo, hi, set()) != (lo + hi) // 2]
    check('policy P reduces to plain bisection when nothing is exhausted',
          not bad, f'{len(bad)} mismatches over 210 intervals')
    check('policy D targets the opponent bound then one below it',
          decisive_radii(5, 20, 12, 12) == [12, 11],
          str(decisive_radii(5, 20, 12, 12)))


def test_classification():
    mk = lambda lo, hi: dict(lo=lo, hi=hi)
    cases = [((2, 2), (5, 5), 'certified C > W'), ((5, 5), (2, 2), 'certified W > C'),
             ((3, 3), (3, 3), 'certified equality'), ((2, 7), (4, 6), 'unresolved'),
             ((2, 9), (2, 9), 'unresolved')]
    ok = all(classify(mk(*w), mk(*c))['verdict'] == want for w, c, want in cases)
    check('ordering classification, incl. overlapping intervals are NOT equality', ok)


if __name__ == '__main__':
    print("=" * 92)
    print("CERTIFIED-RESOLUTION EXTENSION — fixtures")
    print("=" * 92)
    test_certified_matches_enumeration()
    test_transfer_and_control()
    test_determinism_and_policy()
    test_classification()
    print(f"\n  {'ALL PASS' if not FAILS else 'FAILURES: ' + '; '.join(FAILS)}")
    sys.exit(1 if FAILS else 0)
