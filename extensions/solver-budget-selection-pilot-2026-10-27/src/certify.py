"""Certified comparisons under the frozen budget and allocation rule.

Per PROTOCOL.md §8: 60 s per solver invocation; 300 s total per
instance-budget group shared across its selection schemes; an initial
opportunity to every distinct observed set, then a predetermined round-robin;
4 h for calibration + validation + collection + certification combined.

Unfinished comparisons are kept. The budget is never extended and no case is
dropped.
"""
import os, sys, json, csv, time, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pilotlib as P
import store
import measure
from eqlib import classify

GROUP_BUDGET = 300.0
SLICE = 30.0
OVERALL_CAP = 4 * 3600
SCHEMES = ('prefix', 'uniform0', 'uniform1', 'uniform2')
PROTO_SHA = open(os.path.join(P.EXT, 'data', 'PROTOCOL_SHA.txt')).read().strip()
COLL = os.path.join(P.EXT, 'data', 'collections')


def set_order(sets):
    """Predetermined order: prefix pair, then uniform0 pair, 1, 2."""
    out = []
    for sc in SCHEMES:
        for lab in ('W', 'C'):
            if (lab, sc) in sets:
                out.append((lab, sc))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--elapsed-before', type=float, default=0.0,
                    help='seconds already spent on calibration/validation/collection')
    a = ap.parse_args()
    t_start = time.perf_counter()

    def overall_left():
        return OVERALL_CAP - a.elapsed_before - (time.perf_counter() - t_start)

    idx = json.load(open(os.path.join(P.EXT, 'data', 'collection_index.json')))
    by = {}
    for r in idx['rows']:
        d = json.load(open(os.path.join(COLL, r['file'])))
        by[(r['instance_id'], r['solver'])] = d

    insts = sorted({r['instance_id'] for r in idx['rows']})
    journal = store.Journal(os.path.join(P.EXT, 'journal', 'certify.jsonl'))
    rows, groups = [], []
    print(f"protocol commit {PROTO_SHA}")
    print(f"group budget {GROUP_BUDGET:.0f}s, slice {SLICE:.0f}s, "
          f"overall cap {OVERALL_CAP/3600:.0f}h "
          f"({a.elapsed_before/60:.0f} min already spent)\n")
    print(f"{'instance':<16}{'bud':>5}{'scheme':>10}"
          f"{'W interval':>13}{'C interval':>13}{'diff':>12}{'s':>7}  verdict")

    for iid in insts:
        for b in P.BUDGETS:
            bl = f'b{int(b)}'
            W, C = by.get((iid, 'W')), by.get((iid, 'C'))
            eW, eC = W['budgets'][bl], C['budgets'][bl]
            grec = dict(protocol_commit=PROTO_SHA, instance_id=iid,
                        stratum=W['stratum'], n=W['n'], alpha=W['alpha'],
                        budget=b, bank_W=eW['bank_size'], bank_C=eC['bank_size'],
                        eligible=(eW['eligible'] and eC['eligible']))
            if not grec['eligible']:
                grec['outcome'] = 'ineligible: insufficient sample'
                groups.append(grec)
                for sc in SCHEMES:
                    rows.append(dict(grec, scheme=sc, verdict='ineligible',
                                     W_lo=None, W_hi=None, C_lo=None, C_hi=None,
                                     diff_lo=None, diff_hi=None,
                                     retained_W=None, retained_C=None))
                print(f"{iid:<16}{b:>5.0f}{'(all)':>10}{'-':>13}{'-':>13}"
                      f"{'-':>12}{0:>7.1f}  INELIGIBLE "
                      f"(banks W={eW['bank_size']} C={eC['bank_size']}, k={P.K_RETAIN})")
                continue
            if overall_left() <= GROUP_BUDGET:
                grec['outcome'] = 'not attempted: overall cap'
                groups.append(grec)
                print(f"{iid:<16}{b:>5.0f}  NOT ATTEMPTED (overall 4 h cap)")
                continue

            sets = {}
            for lab, dd, ee in (('W', W, eW), ('C', C, eC)):
                for sc in SCHEMES:
                    s = ee['sets'].get(sc)
                    if s:
                        sets[(lab, sc)] = s
            order = set_order(sets)
            art = os.path.join(P.EXT, 'artifacts', f'{iid}_{bl}')
            cl = None
            states = {}
            for (lab, sc) in order:
                dd = W if lab == 'W' else C
                if cl is None:
                    # formulas are regenerated from the recorded seed, then
                    # required to hash to the recorded value
                    cl, meta = P.make_formula(dd['n'], dd['alpha'], dd['j'])
                    assert store.hash_clauses(cl) == dd['formula_hash']
                B = [tuple(x) for x in sets[(lab, sc)]['B']]
                assert store.hash_A(B) == sets[(lab, sc)]['B_hash']
                key = f'{iid}_{bl}_{lab}_{sc}'
                states[(lab, sc)] = measure.SetState(
                    key, cl, dd['n'], B, art, journal,
                    dict(instance_id=iid, budget=b, solver=lab, scheme=sc,
                         formula_hash=dd['formula_hash'],
                         A_hash=sets[(lab, sc)]['B_hash'],
                         protocol_commit=PROTO_SHA))

            t_g = time.perf_counter()

            def group_left():
                return min(GROUP_BUDGET - (time.perf_counter() - t_g), overall_left())

            # phase 1: initial opportunity to every distinct set
            init = GROUP_BUDGET / max(1, len(order))
            for k in order:
                if group_left() <= 1.0:
                    break
                states[k].advance(min(init, group_left()),
                                  group_remaining=group_left)
            # phase 2: round-robin, aimed at the ordering
            while group_left() > 1.0:
                progressed = False
                for (lab, sc) in order:
                    if group_left() <= 1.0:
                        break
                    opp = ('C' if lab == 'W' else 'W')
                    if (opp, sc) not in states:
                        continue
                    me, other = states[(lab, sc)], states[(opp, sc)]
                    v = classify(states[('W', sc)].interval(),
                                 states[('C', sc)].interval())
                    if v['verdict'] != 'unresolved':
                        continue
                    if me.exact or me.alarm:
                        continue
                    before = (me.lo, me.hi, me.queries)
                    me.advance(min(SLICE, group_left()), other.interval(),
                               group_remaining=group_left)
                    if (me.lo, me.hi, me.queries) != before:
                        progressed = True
                if not progressed:
                    break

            grec['group_s'] = round(time.perf_counter() - t_g, 2)
            grec['overshoot'] = grec['group_s'] > GROUP_BUDGET + 1.0
            groups.append(grec)
            for sc in SCHEMES:
                if ('W', sc) not in states or ('C', sc) not in states:
                    continue
                sw, sc_ = states[('W', sc)], states[('C', sc)]
                v = classify(sw.interval(), sc_.interval())
                diff_txt = '[' + str(v['diff_lo']) + ',' + str(v['diff_hi']) + ']'
                rows.append(dict(
                    grec, scheme=sc, verdict=v['verdict'],
                    W_lo=sw.lo, W_hi=sw.hi, W_exact=sw.exact,
                    C_lo=sc_.lo, C_hi=sc_.hi, C_exact=sc_.exact,
                    diff_lo=v['diff_lo'], diff_hi=v['diff_hi'],
                    retained_W=len(sw.B), retained_C=len(sc_.B),
                    W_hash=sw.meta['A_hash'], C_hash=sc_.meta['A_hash'],
                    queries_W=sw.queries, queries_C=sc_.queries,
                    sat_W=sw.n_sat, cert_W=sw.n_cert, unchk_W=sw.n_unchecked,
                    unk_W=sw.n_unknown,
                    sat_C=sc_.n_sat, cert_C=sc_.n_cert, unchk_C=sc_.n_unchecked,
                    unk_C=sc_.n_unknown,
                    solve_s=round(sw.solve_s + sc_.solve_s, 2),
                    check_s=round(sw.check_s + sc_.check_s, 2),
                    encode_s=round(sw.encode_s + sc_.encode_s, 2),
                    bytes_written=sw.bytes_written + sc_.bytes_written,
                    max_proof_lines=max(sw.max_proof_lines, sc_.max_proof_lines),
                    alarm=(sw.alarm or sc_.alarm)))
                print(f"{iid:<16}{b:>5.0f}{sc:>10}"
                      f"{f'[{sw.lo},{sw.hi}]':>13}{f'[{sc_.lo},{sc_.hi}]':>13}"
                      f"{diff_txt:>12}"
                      f"{grec['group_s']:>7.1f}  {v['verdict']}", flush=True)
            _write(rows, groups)
    _write(rows, groups)
    print(f"\n  certification wall {time.perf_counter()-t_start:.0f}s")
    print(f"  wrote data/paired_results.csv, data/groups.json")
    return 0


FIELDS = ['protocol_commit','instance_id','stratum','n','alpha','budget','scheme',
          'eligible','bank_W','bank_C','retained_W','retained_C',
          'W_lo','W_hi','W_exact','C_lo','C_hi','C_exact','verdict',
          'diff_lo','diff_hi','W_hash','C_hash','queries_W','queries_C',
          'sat_W','cert_W','unchk_W','unk_W','sat_C','cert_C','unchk_C','unk_C',
          'encode_s','solve_s','check_s','group_s','overshoot','bytes_written',
          'max_proof_lines','alarm','outcome']


def _write(rows, groups):
    p = os.path.join(P.EXT, 'data', 'paired_results.csv')
    with open(p + '.tmp', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)
    os.replace(p + '.tmp', p)
    store.atomic_write_text(os.path.join(P.EXT, 'data', 'groups.json'),
                            json.dumps(groups, indent=2, default=str))


if __name__ == '__main__':
    sys.exit(main())
