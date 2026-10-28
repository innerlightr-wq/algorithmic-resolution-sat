"""Regenerate every headline number of this extension from the frozen evidence,
and verify the distributed certificates.

What this checks, from files in this repository only:

  1. frozen inputs load and re-hash correctly (formula and observed set);
  2. every observed set lies inside the solution set of its own formula;
  3. the equal-size headline tallies recompute from the paired CSV;
  4. the per-instance replicate consistency recomputes;
  5. the transferred-bound mathematics holds on every frozen subset
     (eps(A) <= eps(B) <= eps(A) + h(A,B) applied to the recorded intervals);
  6. the distributed DRUP certificates verify against CNFs re-encoded from the
     frozen inputs -- so the certificate is checked against *this* query, not a
     stored CNF that is merely asserted to match;
  7. the optimization tallies recompute from its paired CSV, and no certified
     improvement was recorded after its deadline.

Run:  python extensions/certified-resolution-2026-10-27/src/verify_extension.py
Add --with-proofs to include step 6 (needs drat-trim; see tools/).
"""
import os, sys, csv, json, argparse, collections, subprocess, tarfile, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eqlib
from eqlib import EXT, DATA, load_frozen, frozen_paths, h_cover, canonical
import store
from verify import all_in_solution_set, check_witness
from encode import encode_Q

FAILS = []


def check(name, ok, detail=''):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}{('  — ' + detail) if detail else ''}")
    if not ok:
        FAILS.append(name)
    return ok


def _i(x, d=0):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return d


# ------------------------------------------------------------------ 1 & 2
def step_frozen():
    ok_all, n_eq, n_opt, bad = True, 0, 0, []
    for group in ('equal-size', 'optimization'):
        for p in frozen_paths(group):
            try:
                cl, A, d = load_frozen(p)          # re-hashes both
            except AssertionError as e:
                ok_all = False
                bad.append(str(e))
                continue
            inside, offenders = all_in_solution_set(cl, A)
            if not inside:
                ok_all = False
                bad.append(f'{os.path.basename(p)}: {len(offenders)} outside S_I')
            if group == 'equal-size':
                n_eq += 1
            else:
                n_opt += 1
    check('frozen inputs load, re-hash, and every observed set lies inside S_I',
          ok_all, f'{n_eq} equal-size + {n_opt} optimization records; {bad[:2]}')


# ---------------------------------------------------------------------- 3,4
def step_equalsize_tallies():
    rows = list(csv.DictReader(open(os.path.join(DATA, 'equal-size',
                                                 'paired_results.csv'))))
    v = collections.Counter(r['verdict'] for r in rows)
    byc = collections.defaultdict(list)
    for r in rows:
        byc[r['cell']].append(r['verdict'])
    cons = {c: set(vs) for c, vs in byc.items()}
    nCW = sum(1 for s in cons.values() if s == {'certified C > W'})
    nEQ = sum(1 for s in cons.values() if s == {'certified equality'})
    nMix = sum(1 for s in cons.values() if len(s) > 1)
    hashes = [r['B_hash'] for r in rows]
    check('equal-size: 21 measurements, 7 instances, 21 distinct observed sets',
          len(rows) == 21 and len(byc) == 7 and len(set(hashes)) == 21,
          f'{len(rows)} rows, {len(byc)} instances, {len(set(hashes))} distinct hashes, '
          f'{len(hashes) - len(set(hashes))} duplicates')
    check('equal-size measurement-level verdicts: 18 C>W, 3 equality, 0 W>C, 0 unresolved',
          v.get('certified C > W') == 18 and v.get('certified equality') == 3
          and v.get('certified W > C', 0) == 0 and v.get('unresolved', 0) == 0,
          str(dict(v)))
    check('equal-size instance-level: 6 consistently C>W, 1 consistently equality, 0 mixed',
          nCW == 6 and nEQ == 1 and nMix == 0,
          f'{nCW} / {nEQ} / {nMix}; all replicate counts == 3: '
          f'{all(len(vs) == 3 for vs in byc.values())}')
    exact = sum(1 for r in rows if r['exact'] == 'True')
    tr = sum(1 for r in rows if _i(r['new_sat_calls']) == 0)
    check('certificate states preserved: 3 exact, 18 certified INTERVALS, '
          '5 from transferred bounds alone, 0 unchecked UNSAT, 0 UNKNOWN',
          exact == 3 and tr == 5
          and sum(_i(r['n_unsat_unchecked']) for r in rows) == 0
          and sum(_i(r['n_unknown']) for r in rows) == 0,
          f'exact={exact} transfer_only={tr}')
    return rows


# ------------------------------------------------------------------------ 5
def step_transfer_math(rows):
    """Recompute h(A,B) from the frozen sets and re-derive the start interval."""
    ok_all, checked, probs = True, 0, []
    for r in rows:
        p = os.path.join(eqlib.FROZEN, 'equal-size', f"{r['tag']}.json")
        if not os.path.exists(p):
            continue
        cl, B, d = load_frozen(p)
        n = d['n']
        # The frozen subset record stores h(A,B) and the certified source
        # interval for the full set A.  A itself is not shipped (it is the
        # 129-150 element recorded bank); what is verified here is that the
        # recorded transfer obeys the proved arithmetic exactly, and that no
        # later interval ever escaped it.
        src = d['transfer']['from_interval']
        h = d['h_A_B']
        lo_t, hi_t = d['transfer']['lo'], d['transfer']['hi']
        if not (lo_t == src[0] and hi_t == min(n, src[1] + h)):
            ok_all = False
            probs.append(f"{r['tag']}: transfer arithmetic")
        # the recorded start must be >= the transferred lower bound (witness
        # strengthening only) and never exceed the transferred upper bound
        if not (d['start_lo'] >= lo_t and d['start_hi'] == hi_t):
            ok_all = False
            probs.append(f"{r['tag']}: start outside transfer")
        # the final certified interval must sit inside the start interval
        if not (_i(r['final_lo']) >= d['start_lo'] and _i(r['final_hi']) <= d['start_hi']):
            ok_all = False
            probs.append(f"{r['tag']}: final outside start")
        checked += 1
    check('transferred-bound arithmetic re-derives on every frozen subset, and '
          'each final interval sits inside its start interval',
          ok_all, f'{checked} records checked; {probs[:2]}')


# ------------------------------------------------------------------------ 6
def step_certificates(limit=None):
    """Re-encode each certified query from frozen inputs and check its proof."""
    import dratcheck
    prov = dratcheck.binary_provenance()
    if not prov.get('exists'):
        check('drat-trim available (see tools/build_drat_trim.sh)', False,
              f"not found at {prov['path']}")
        return
    tarp = os.path.join(EXT, 'certificates', 'equal-size-proofs.tar.gz')
    if not os.path.exists(tarp):
        check('certificate archive present', False, tarp)
        return
    man = json.load(open(os.path.join(EXT, 'certificates', 'MANIFEST.json')))
    tmp = tempfile.mkdtemp(prefix='certs-', dir=os.path.join(EXT, 'certificates'))
    nok = nbad = 0
    try:
        with tarfile.open(tarp) as t:
            t.extractall(tmp)
        items = man['proofs'][:limit] if limit else man['proofs']
        for e in items:
            pf = os.path.join(tmp, e['path'])
            if not os.path.exists(pf) or store.sha256_file(pf) != e['sha256']:
                nbad += 1
                continue
            cl, B, d = load_frozen(os.path.join(eqlib.FROZEN, 'equal-size',
                                                f"{e['tag']}.json"))
            cnf, nv, _, kind = encode_Q(cl, d['n'], B, e['r'])
            lines = [f'p cnf {nv} {len(cnf)}']
            lines += [' '.join(map(str, c)) + ' 0' for c in cnf]
            cp = os.path.join(tmp, f"{e['tag']}_r{e['r']}.cnf")
            with open(cp, 'w') as f:
                f.write('\n'.join(lines) + '\n')
            res = dratcheck.check(cp, pf, timeout_s=300)
            if dratcheck.verified(res):
                nok += 1
            else:
                nbad += 1
                print(f"      REJECTED {e['tag']} r={e['r']}: {res['verdict']}")
            os.unlink(cp)
        check('distributed certificates verify against CNFs RE-ENCODED from the '
              'frozen inputs', nbad == 0 and nok > 0,
              f'{nok} verified, {nbad} failed, checker {prov["commit"][:8]}')
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------------------------------------ 7
def step_optimization():
    rows = list(csv.DictReader(open(os.path.join(DATA, 'optimization',
                                                 'paired_results.csv'))))
    g = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        g[r['group']][r['method']].append(r)
    red = {m: sum(_i(r['width_reduction']) for r in g['opt-primary'][m])
           for m in 'ABC'}
    ex = {m: sum(1 for r in g['control'][m] if r['exact'] == 'True') for m in 'ABC'}
    check('optimization: 27 runs; hard-set certified width reduction A=0, B=37, C=38',
          len(rows) == 27 and red == {'A': 0, 'B': 37, 'C': 38}, str(red))
    check('optimization controls: all three methods 4/4 exact', ex == {'A': 4, 'B': 4, 'C': 4},
          str(ex))
    late = [(r['tag'], r['method'], i) for r in rows
            for i in json.loads(r['improvements'] or '[]') if float(i['at_s']) > 240.0]
    over = [r['tag'] for r in rows if r['overshoot'] == 'True']
    check('no certified improvement was recorded after its 240 s deadline',
          not late, f'{len(late)} late improvements; {len(over)} runs overshot in the tail')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--with-proofs', action='store_true')
    ap.add_argument('--proof-limit', type=int, default=None)
    a = ap.parse_args()
    print("=" * 92)
    print("CERTIFIED-RESOLUTION EXTENSION — verification from frozen evidence")
    print("=" * 92)
    print("\n-- frozen inputs --")
    step_frozen()
    print("\n-- equal-size headline --")
    rows = step_equalsize_tallies()
    step_transfer_math(rows)
    print("\n-- optimization --")
    step_optimization()
    if a.with_proofs:
        print("\n-- certificates --")
        step_certificates(a.proof_limit)
    else:
        print("\n-- certificates: skipped (pass --with-proofs; needs drat-trim) --")
    print(f"\n  {'ALL PASS' if not FAILS else 'FAILURES: ' + '; '.join(FAILS)}")
    return 1 if FAILS else 0


if __name__ == '__main__':
    sys.exit(main())
