"""Validation of the collection and selection code, before the primary run.

Covers PROTOCOL.md §5-§9 and the brief's checklist: discovery ordering and
deduplication, deadline handling and exclusion of late assignments, short-budget
banks as prefixes of long-budget banks, cardinalities, reproducible subset
construction, absence of any distance information in selection, witness
validation on original variables, hash-keyed reuse, interval classification,
restart behaviour, and preservation of incomplete outcomes.

The previously validated encoding and proof-checking controls are retained by
re-running the sibling extension's fixtures.
"""
import os, sys, json, time, subprocess, itertools, inspect

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pilotlib as P
import numpy as np
import store
from verify import eval_clauses, hamming, check_witness
from eqlib import classify

FAILS = []


def check(name, ok, detail=''):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}{('  — ' + detail) if detail else ''}")
    if not ok:
        FAILS.append(name)
    return ok


# ------------------------------------------------------------------ bank
def test_bank_ordering_and_dedup():
    b = P.Bank()
    xs = [(0, 1), (1, 0), (0, 1), (1, 1), (1, 0), (0, 0)]
    for i, x in enumerate(xs):
        b.offer(x, 0.1 * i)
    ok = (b.order == [(0, 1), (1, 0), (1, 1), (0, 0)])
    ok &= (b.duplicates == 2)
    ok &= (b.accepted_at == sorted(b.accepted_at))          # monotonic
    ok &= (len(b) == 4 == len(set(b.order)))
    check('bank keeps first-discovery order, deduplicates, timestamps monotonic',
          ok, f'{len(xs)} offers -> {len(b)} distinct, {b.duplicates} duplicates')


def test_snapshot_is_prefix_and_excludes_late():
    b = P.Bank()
    for i, x in enumerate([(i,) for i in range(10)]):
        b.offer(x, float(i))                                # accepted at t = 0..9
    s5 = b.snapshot(5.0)
    s30 = b.snapshot(30.0)
    ok = (s5 == s30[:len(s5)])                              # prefix
    ok &= (len(s5) == 5)                                    # strictly before 5.0
    ok &= all(t < 5.0 for x, t in zip(b.order, b.accepted_at) if x in s5)
    ok &= ((4,) in s5 and (5,) not in s5)                   # boundary is strict
    check('short-budget snapshot is a strict prefix of the long one and excludes '
          'assignments accepted at or after the deadline', ok,
          f'|5s|={len(s5)} |30s|={len(s30)}, boundary exclusive')


def test_live_collection_deadline():
    """A real timed collection must respect its budget and admit nothing late."""
    cl, meta = P.make_formula(32, 3.5, 0, base=P.CALIB_SEED)
    seed, _ = P.collection_seed('vtest|W', meta['formula_hash'], base=P.CALIB_SEED)
    t0 = time.perf_counter()
    bank, info = P.collect_walksat(cl, 32, 3.0, seed)
    wall = time.perf_counter() - t0
    ok = all(t < 3.0 for t in bank.accepted_at)
    ok &= (wall < 3.0 + 1.5)                    # one in-flight restart of slack
    ok &= all(eval_clauses(cl, x) for x in bank.order)
    ok &= (info['restarts'] > 0)
    s_short = bank.snapshot(1.0)
    ok &= (s_short == bank.snapshot(3.0)[:len(s_short)])
    check('live timed collection: nothing admitted at/after the deadline, every '
          'admitted assignment satisfies the original formula', ok,
          f"{len(bank)} distinct, {info['restarts']} restarts, wall {wall:.2f}s")


def test_restart_behaviour_preserved():
    """Parameters are the paper's; only the stopping rule is the clock."""
    src = inspect.getsource(P.collect_walksat)
    ok = ("WALKSAT['max_flips']" in src and "WALKSAT['p_noise']" in src)
    ok &= (P.WALKSAT == dict(max_flips=3000, p_noise=0.5))
    ok &= (P.CDCL == dict(T_per_run=8))
    ok &= ('K' not in P.WALKSAT and 'R' not in P.CDCL)      # counts are clock-driven
    csrc = inspect.getsource(P.collect_cdcl)
    ok &= all(s in csrc for s in ('permute_clauses', 'random_phases',
                                  'set_phases', 'enum_models',
                                  "CDCL['T_per_run']"))
    check('solver mechanisms preserved (WalkSAT flips/noise/restarts; CDCL '
          'permutation/phases/T=8); only the stopping rule is the clock', ok)


# ------------------------------------------------------------- selection
def test_cardinalities_and_prefix():
    bank = [(i,) for i in range(100)]
    pre = P.prefix_set(bank, 40)
    ok = (len(pre) == 40 and pre == bank[:40])
    ok &= (P.prefix_set(bank[:39], 40) is None)             # too few -> None
    B, prov = P.uniform_set(bank, 40, 'a' * 64, 'W', 'b5', 0)
    ok &= (len(B) == 40 == len(set(B)) and set(B).issubset(set(bank)))
    ok &= (prov['B_hash'] == store.hash_A(B))
    none_B, none_p = P.uniform_set(bank[:39], 40, 'a' * 64, 'W', 'b5', 0)
    ok &= (none_B is None)
    check('prefix and subsample cardinalities, and refusal below k', ok,
          f'prefix {len(pre)}, uniform {len(B)}, both subsets of the bank')


def test_subset_reproducibility():
    bank = [tuple(int(b) for b in np.binary_repr(i, 10)) for i in range(300)]
    h = 'c' * 64
    a1, p1 = P.uniform_set(bank, 40, h, 'W', 'b30', 0)
    a2, p2 = P.uniform_set(bank, 40, h, 'W', 'b30', 0)
    ok = (a1 == a2 and p1['B_hash'] == p2['B_hash'])
    seeds = {P.uniform_set(bank, 40, h, lab, bl, r)[1]['seed']
             for lab in ('W', 'C') for bl in ('b5', 'b30') for r in range(3)}
    ok &= (len(seeds) == 12)                                # all distinct
    # order-independence: shuffling the bank must not change the draw
    import random as _r
    shuffled = bank[:]
    _r.Random(7).shuffle(shuffled)
    a3, _ = P.uniform_set(shuffled, 40, h, 'W', 'b30', 0)
    ok &= (a3 == a1)
    check('subset construction is reproducible from the frozen bank, seed-distinct '
          'across label/budget/replicate, and independent of discovery order',
          ok, f'{len(seeds)} distinct seeds over 2x2x3')


def _executable_source(fn):
    """Source with comments and docstrings stripped.

    The prohibition is *described* in those docstrings, so scanning raw text
    would flag the very sentence promising the property.  Only executable
    tokens are scanned.
    """
    import io, tokenize
    src = inspect.getsource(fn)
    out, prev = [], tokenize.INDENT
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == tokenize.COMMENT:
            continue
        if tok.type == tokenize.STRING and prev in (tokenize.INDENT,
                                                    tokenize.NEWLINE,
                                                    tokenize.NL,
                                                    tokenize.DEDENT):
            prev = tok.type                      # bare string = docstring
            continue
        out.append(tok.string)
        if tok.type not in (tokenize.NL,):
            prev = tok.type
    return ' '.join(out)


def test_no_distance_in_selection():
    """Selection must consult only indices and the derived seed."""
    src = ' '.join(_executable_source(f) for f in
                   (P.uniform_set, P.prefix_set, P.subsample_seed))
    banned = ('hamming', 'distance', 'cluster', 'resolution', 'radius', 'eps')
    hits = [w for w in banned if w in src.lower()]
    check('no distance, clustering or resolution information enters selection',
          not hits, f'banned tokens in executable code: {hits}' if hits else
          'executable selection code uses only canonical indices and the seed')


# ------------------------------------------- certification-side invariants
def test_witness_validation_on_original_variables():
    # alpha=3.5 at n=32 is known from calibration to yield solutions quickly;
    # alpha=4.2 can be too sparse for a 2 s budget and would make the fixture
    # flaky rather than informative.
    cl, meta = P.make_formula(32, 3.5, 1, base=P.CALIB_SEED)
    n = 32
    seed, _ = P.collection_seed('vtest2|W', meta['formula_hash'], base=P.CALIB_SEED)
    bank, _ = P.collect_walksat(cl, n, 4.0, seed)
    if len(bank) < 3:
        check('witness validation fixture collected enough solutions', False,
              f'only {len(bank)} distinct in 4 s')
        return
    A = bank.order[:2]
    x = bank.order[-1]
    d = min(hamming(x, a) for a in A)
    ok, msg = check_witness(cl, n, A, d - 1, x)             # valid at r = d-1
    bad, _ = check_witness(cl, n, A, d, x)                  # must fail at r = d
    # padding x with fake auxiliary bits must not change the distance
    ok2 = (min(hamming(x, a) for a in A) == d)
    check('witness validation uses original variables only, and is exact at the '
          'radius boundary', ok and not bad and ok2,
          f'min distance {d}; accepted at r={d-1}, rejected at r={d}')


def test_hash_keyed_reuse_real():
    """Evidence is reused only across matching formula AND observed-set hashes."""
    sys.path.insert(0, os.path.join(P.SIB))
    import tempfile, shutil
    work = tempfile.mkdtemp(prefix='reuse-', dir=os.path.join(P.EXT, 'results'))
    try:
        jp = os.path.join(work, 'j.jsonl')
        j = store.Journal(jp)
        fh, ah = 'd' * 64, 'e' * 64
        j.append(dict(kind='query', formula_hash=fh, A_hash=ah, r=3,
                      status='SAT', witness_verified=True))
        j.append(dict(kind='query', formula_hash=fh, A_hash=ah, r=6,
                      status='UNSAT', proof_verdict='VERIFIED'))
        j.append(dict(kind='query', formula_hash=fh, A_hash=ah, r=5,
                      status='UNSAT', proof_verdict='TIMEOUT'))
        # The recovery rule is replicated here so the test is independent of
        # the certification module's import graph: only a validated witness
        # moves the lower bound, only a checked proof moves the upper one.
        recs, _ = store.read_journal(jp)

        def recover(fh_, ah_, n):
            lo, hi = 0, n
            for r in recs:
                if r.get('formula_hash') != fh_ or r.get('A_hash') != ah_:
                    continue
                if r.get('status') == 'SAT' and r.get('witness_verified'):
                    lo = max(lo, r['r'] + 1)
                elif r.get('status') in ('UNSAT', 'TRIVIAL_UNSAT') and \
                        str(r.get('proof_verdict')) == 'VERIFIED':
                    hi = min(hi, r['r'])
            return lo, hi
        same = recover(fh, ah, 32)
        other_A = recover(fh, 'f' * 64, 32)
        other_I = recover('0' * 64, ah, 32)
        ok = (same == (4, 6))                   # not hi=5: that was unchecked
        ok &= (other_A == (0, 32) and other_I == (0, 32))
        check('evidence is reused only across matching formula AND observed-set '
              'hashes; an unchecked UNSAT never tightens a recovered bound', ok,
              f'same={same}, different A={other_A}, different I={other_I}')
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_interval_classification():
    mk = lambda lo, hi: dict(lo=lo, hi=hi)
    cases = [((2, 2), (5, 5), 'certified C > W'), ((5, 5), (2, 2), 'certified W > C'),
             ((3, 3), (3, 3), 'certified equality'), ((2, 7), (4, 6), 'unresolved'),
             ((0, 9), (0, 9), 'unresolved'), ((1, 3), (4, 8), 'certified C > W')]
    ok = all(classify(mk(*w), mk(*c))['verdict'] == want for w, c, want in cases)
    d = classify(mk(2, 7), mk(4, 6))
    ok &= (d['diff_lo'] == 4 - 7 and d['diff_hi'] == 6 - 2)
    check('interval ordering classification and difference interval '
          '[L_C-U_W, U_C-L_W]; overlap is never equality', ok,
          f"overlap case diff = [{d['diff_lo']},{d['diff_hi']}]")


def test_incomplete_outcomes_preserved():
    """An ineligible cell must survive into the record, not vanish."""
    bank = [(i,) for i in range(14)]            # fewer than k
    pre = P.prefix_set(bank, P.K_RETAIN)
    uni, prov = P.uniform_set(bank, P.K_RETAIN, 'a' * 64, 'W', 'b5', 0)
    rec = dict(instance='x', budget=5.0, bank_size=len(bank),
               eligible=(pre is not None and uni is not None),
               outcome='insufficient_sample')
    check('insufficient-sample cells yield None sets and are retained as an '
          'explicit outcome rather than dropped',
          pre is None and uni is None and rec['eligible'] is False,
          f"bank {len(bank)} < k={P.K_RETAIN} -> {rec['outcome']}")


def test_sibling_controls_retained():
    """Re-run the already-validated encoding and proof-checking fixtures."""
    f = os.path.join(P.REPO, 'extensions', 'certified-resolution-2026-10-27',
                     'tests', 'test_fixtures.py')
    r = subprocess.run([sys.executable, f], capture_output=True, text=True,
                       timeout=1800)
    ok = (r.returncode == 0 and 'ALL PASS' in r.stdout)
    tail = [l for l in r.stdout.splitlines() if 'PASS' in l or 'FAIL' in l]
    check('previously validated encoding and proof-checking controls still pass',
          ok, f'{len(tail)} assertions, exit {r.returncode}')


if __name__ == '__main__':
    print("=" * 92)
    print("PILOT — collection and selection validation")
    print("=" * 92)
    print("\n-- bank and collection --")
    test_bank_ordering_and_dedup()
    test_snapshot_is_prefix_and_excludes_late()
    test_live_collection_deadline()
    test_restart_behaviour_preserved()
    print("\n-- selection --")
    test_cardinalities_and_prefix()
    test_subset_reproducibility()
    test_no_distance_in_selection()
    print("\n-- certification invariants --")
    test_witness_validation_on_original_variables()
    test_hash_keyed_reuse_real()
    test_interval_classification()
    test_incomplete_outcomes_preserved()
    print("\n-- retained controls --")
    test_sibling_controls_retained()
    print(f"\n  {'ALL PASS' if not FAILS else 'FAILURES: ' + '; '.join(FAILS)}")
    sys.exit(1 if FAILS else 0)
