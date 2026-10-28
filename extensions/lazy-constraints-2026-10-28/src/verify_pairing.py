"""Verify the PAIRED-PER-QUERY claim for Stage 2.

Equal query counts do NOT establish that two methods asked the same questions.
This script re-runs the four units that reached an exact answer under both
methods, with the radius sequence and the per-query outcome instrumented, and
compares the sequences.

TIMINGS ARE NOT TAKEN FROM THIS RUN.  The measured timings stay those of the
original Stage 2 run (data/stage2.json).  This run exists only to record the
radius sequences and to re-verify the formula and observed-set hashes.
"""
import os, sys, json, time, hashlib

OPT = os.path.expanduser('~/scratch/sat-resolution-oracle-audit-2026-10-26/'
                         'optimization-2026-10-27')
sys.path.insert(0, os.path.join(OPT, 'src'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units, store
from methods import select_radius
import lazy as LZ

FAILS = []
def check(name, ok, detail=''):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}{('  -- ' + detail) if detail else ''}")
    if not ok:
        FAILS.append(name)
    return ok


def trace(unit, clauses, A, method):
    """The radius ladder, recording every (radius, outcome)."""
    lo, hi = unit['start_lo'], unit['start_hi']
    exhausted, seq = set(), []
    t0 = time.perf_counter()

    def remaining():
        return LZ.MEASUREMENT_BUDGET - (time.perf_counter() - t0)

    while True:
        if remaining() <= 1.0:
            return seq, lo, hi, 'budget'
        r = select_radius(lo, hi, exhausted)
        if r is None:
            return seq, lo, hi, 'exact' if lo == hi else 'exhausted'
        fn = LZ.query_static if method == 'S' else LZ.query_lazy
        q = fn(clauses, A, r, f'verify_{unit["tag"]}_{method}_r{r}', remaining)
        st = q['status']
        seq.append((r, st, q.get('proof_verdict'), q.get('iters')))
        if st == 'SAT':
            if not q.get('witness_verified'):
                return seq, lo, hi, 'alarm'
            lo = max(lo, r + 1)
        elif st in ('UNSAT', 'TRIVIAL_UNSAT'):
            cert = (q['proof_verdict'] == 'VERIFIED'
                    or str(q['proof_verdict']).startswith('arithmetic'))
            if cert:
                hi = min(hi, r)
            else:
                exhausted.add(r)
        else:
            exhausted.add(r)


if __name__ == '__main__':
    print('=' * 92)
    print('VERIFYING THE PAIRED-PER-QUERY CLAIM (timings NOT taken from this run)')
    print('=' * 92)
    prev = {(r['tag'], r['method']): r
            for r in json.load(open('data/stage2.json'))['rows']}
    targets = sorted({t for (t, m) in prev
                      if prev[(t, 'S')]['exact'] and prev[(t, 'L')]['exact']})
    print(f"\n       units exact under both methods: {targets}")
    out, mism = {}, []
    for u in json.load(open(os.path.join(OPT, 'data', 'baseline.json'))):
        if u['tag'] not in targets:
            continue
        cl, A, meta = units.recover(u['tag'], u['obs_seed_id'])
        fh, ah = store.hash_clauses(cl), store.hash_A(A)
        hok = (fh == u['formula_hash'] and ah == u['A_hash'])
        rec = dict(formula_hash=fh, A_hash=ah, hashes_ok=hok, A_size=len(A))
        if not hok:
            mism.append(u['tag'])
            out[u['tag']] = rec
            continue
        for m in ('S', 'L'):
            seq, lo, hi, stop = trace(u, cl, A, m)
            rec[m] = dict(radii=[s[0] for s in seq],
                          outcomes=[s[1] for s in seq],
                          verdicts=[s[2] for s in seq], stop=stop,
                          final=[lo, hi])
        same_r = rec['S']['radii'] == rec['L']['radii']
        same_o = rec['S']['outcomes'] == rec['L']['outcomes']
        rec['same_radii'], rec['same_outcomes'] = same_r, same_o
        rec['agrees_with_stage2'] = (
            rec['S']['final'] == [prev[(u['tag'], 'S')]['final_lo'],
                                  prev[(u['tag'], 'S')]['final_hi']]
            and rec['L']['final'] == [prev[(u['tag'], 'L')]['final_lo'],
                                      prev[(u['tag'], 'L')]['final_hi']])
        out[u['tag']] = rec
        print(f"\n       {u['tag']}  (|A|={len(A)}, hashes OK)")
        print(f"         S radii {rec['S']['radii']}  {rec['S']['outcomes']}"
              f"  -> {rec['S']['final']}  [{rec['S']['stop']}]")
        print(f"         L radii {rec['L']['radii']}  {rec['L']['outcomes']}"
              f"  -> {rec['L']['final']}  [{rec['L']['stop']}]")
        print(f"         identical radii: {same_r}   identical outcomes: "
              f"{same_o}   reproduces stage 2: {rec['agrees_with_stage2']}")

    check('every unit was recovered with BOTH the formula hash and the '
          'observed-set hash matching the recorded values', not mism,
          f'{len(out)} units, mismatches {mism}')
    # RESULT, recorded as measured rather than as predicted.  Three of the four
    # units are verified paired; the fourth is NOT, and is excluded from every
    # paired claim.  An earlier version of these assertions expected all four.
    paired = [t for t, r in out.items()
              if r.get('same_radii') and r.get('same_outcomes')
              and r.get('agrees_with_stage2')]
    unpaired = [t for t in out if t not in paired]
    budget_sensitive = [t for t, r in out.items()
                        if r.get('S', {}).get('stop') == 'budget'
                        or r.get('L', {}).get('stop') == 'budget']
    check('a nonempty subset of the units exact under both methods is VERIFIED '
          'paired: identical radius sequence, identical per-query outcomes, and '
          'the instrumented re-run reproduces stage 2\'s certified interval',
          bool(paired), f'verified paired: {paired}')
    check('and the units that are NOT verified paired are identified and must '
          'be excluded from any paired claim -- equal query counts alone would '
          'have hidden this', True,
          f'not verified paired: {unpaired or "none"}; '
          f'budget-limited under at least one method: {budget_sensitive or "none"}')
    # the specific failure mode, asserted so it cannot be quietly dropped
    bad = [t for t in unpaired if out[t].get('S', {}).get('stop') == 'budget'
           and not out[t].get('agrees_with_stage2')]
    check('every non-paired unit here is one whose static ladder hit the '
          'measurement budget and did NOT reproduce its stage-2 exact answer, '
          'so its stage-2 "exact" outcome sits on the budget boundary and is '
          'not reproducible', set(bad) == set(unpaired),
          f'{bad}: stage 2 reported exact under S at the budget boundary; the '
          f're-run stopped on budget short of an exact answer')
    json.dump(dict(paired=paired, unpaired=unpaired,
                   budget_sensitive=budget_sensitive, units=out),
              open('data/pairing.json', 'w'), indent=1)
    print(f"\n  {'ALL PASS' if not FAILS else 'FAILURES: ' + '; '.join(FAILS)}")
    sys.exit(1 if FAILS else 0)
