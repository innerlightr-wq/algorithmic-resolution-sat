"""Analysis: four separate tables, explicit denominators, no inflated n.

The statistical unit is the SAT INSTANCE. Budgets, subset replicates and
selection schemes are repeated observations within an instance. No post-hoc
significance test is computed and no population-wide ranking is inferred.
"""
import os, sys, csv, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pilotlib as P
from eqlib import classify

VERD = ('certified C > W', 'certified W > C', 'certified equality', 'unresolved')


def _i(x, d=None):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return d


def iv(lo, hi):
    return None if lo is None or hi is None else dict(lo=lo, hi=hi)


def main():
    rows = list(csv.DictReader(open(os.path.join(P.EXT, 'data',
                                                 'paired_results.csv'))))
    idx = json.load(open(os.path.join(P.EXT, 'data', 'collection_index.json')))
    groups = json.load(open(os.path.join(P.EXT, 'data', 'groups.json')))
    out = {}

    # ---------------------------------------------------- denominators
    attempted = idx['attempted']
    insts = sorted({r['instance_id'] for r in rows})
    elig_groups = [g for g in groups if g.get('eligible')]
    inelig = [g for g in groups if not g.get('eligible')]
    notatt = [g for g in groups if g.get('outcome', '').startswith('not attempted')]
    print("=" * 110)
    print("DENOMINATORS (the statistical unit is the INSTANCE)")
    print("=" * 110)
    print(f"  attempted instances                 : {attempted}")
    print(f"  instances with both collections done: {len(insts)}")
    print(f"  instance-budget groups              : {len(groups)}")
    print(f"    eligible (both solvers >= k=40)   : {len(elig_groups)}")
    print(f"    ineligible (insufficient sample)  : {len(inelig)}")
    print(f"    not attempted (overall cap)       : {len(notatt)}")
    cert_rows = [r for r in rows if r['verdict'] in VERD[:3]]
    print(f"  scheme-level comparisons            : {len(rows)}")
    print(f"    certified                         : {len(cert_rows)}")
    print(f"    unresolved                        : {sum(1 for r in rows if r['verdict']=='unresolved')}")
    print(f"    ineligible                        : {sum(1 for r in rows if r['verdict']=='ineligible')}")
    out['denominators'] = dict(attempted_instances=attempted,
                               instances=len(insts), groups=len(groups),
                               eligible_groups=len(elig_groups),
                               ineligible_groups=len(inelig),
                               not_attempted=len(notatt),
                               comparisons=len(rows), certified=len(cert_rows))

    # ------------------------------------- 1. solver comparison per budget
    print("\n" + "=" * 110)
    print("TABLE 1 — EQUAL-SIZE SOLVER COMPARISON, per common time budget")
    print("=" * 110)
    t1 = {}
    for b in P.BUDGETS:
        for sc in ('prefix', 'uniform0'):
            sel = [r for r in rows if float(r['budget']) == b
                   and r['scheme'] == sc and r['verdict'] != 'ineligible']
            c = collections.Counter(r['verdict'] for r in sel)
            t1[f'b{int(b)}_{sc}'] = dict(c)
            print(f"  budget {b:>4.0f}s  {sc:<9} n={len(sel):>2}  " +
                  '  '.join(f'{k}={c.get(k,0)}' for k in VERD))
    out['table1_solver_by_budget'] = t1
    print("\n  per-instance detail (primary scheme uniform0, and prefix):")
    print(f"  {'instance':<16}{'bud':>5}{'scheme':>10}{'W':>12}{'C':>12}{'diff':>12}  verdict")
    for r in rows:
        if r['scheme'] not in ('prefix', 'uniform0') or r['verdict'] == 'ineligible':
            continue
        wtxt = '[' + str(r['W_lo']) + ',' + str(r['W_hi']) + ']'
        ctxt = '[' + str(r['C_lo']) + ',' + str(r['C_hi']) + ']'
        dtxt = '[' + str(r['diff_lo']) + ',' + str(r['diff_hi']) + ']'
        print(f"  {r['instance_id']:<16}{float(r['budget']):>5.0f}{r['scheme']:>10}"
              f"{wtxt:>12}{ctxt:>12}{dtxt:>12}  {r['verdict']}")

    # ------------------------------ 2. prefix vs uniform WITHIN each solver
    print("\n" + "=" * 110)
    print("TABLE 2 — PREFIX vs UNIFORM, within each solver (same instance, same budget)")
    print("=" * 110)
    t2 = collections.Counter()
    det2 = []
    for b in P.BUDGETS:
        for iid in insts:
            pre = [r for r in rows if r['instance_id'] == iid
                   and float(r['budget']) == b and r['scheme'] == 'prefix'
                   and r['verdict'] != 'ineligible']
            uni = [r for r in rows if r['instance_id'] == iid
                   and float(r['budget']) == b and r['scheme'] == 'uniform0'
                   and r['verdict'] != 'ineligible']
            if not pre or not uni:
                continue
            for lab in ('W', 'C'):
                a = iv(_i(pre[0][f'{lab}_lo']), _i(pre[0][f'{lab}_hi']))
                c = iv(_i(uni[0][f'{lab}_lo']), _i(uni[0][f'{lab}_hi']))
                if a is None or c is None:
                    continue
                # "C>W" slot = uniform, "W" slot = prefix
                v = classify(a, c)
                verdict = {'certified C > W': 'certified uniform > prefix',
                           'certified W > C': 'certified prefix > uniform',
                           'certified equality': 'certified equality',
                           'unresolved': 'unresolved'}[v['verdict']]
                t2[(lab, verdict)] += 1
                det2.append(dict(instance_id=iid, budget=b, solver=lab,
                                 prefix=[a['lo'], a['hi']],
                                 uniform=[c['lo'], c['hi']], verdict=verdict,
                                 diff_lo=v['diff_lo'], diff_hi=v['diff_hi']))
    for lab in ('W', 'C'):
        tot = sum(v for (l, _), v in t2.items() if l == lab)
        print(f"  solver {lab}  n={tot}:  " +
              '  '.join(f'{k[1]}={v}' for k, v in sorted(t2.items()) if k[0] == lab))
    out['table2_prefix_vs_uniform'] = {f'{k[0]}|{k[1]}': v for k, v in t2.items()}
    out['table2_detail'] = det2

    # ----------------------------------------- 3. short vs long budget
    print("\n" + "=" * 110)
    print("TABLE 3 — SHORT vs LONG BUDGET, within each solver and scheme")
    print("=" * 110)
    t3 = collections.Counter()
    det3 = []
    for iid in insts:
        for sc in ('prefix', 'uniform0'):
            s = [r for r in rows if r['instance_id'] == iid and r['scheme'] == sc
                 and float(r['budget']) == 5.0 and r['verdict'] != 'ineligible']
            l = [r for r in rows if r['instance_id'] == iid and r['scheme'] == sc
                 and float(r['budget']) == 30.0 and r['verdict'] != 'ineligible']
            if not s or not l:
                continue
            for lab in ('W', 'C'):
                a = iv(_i(s[0][f'{lab}_lo']), _i(s[0][f'{lab}_hi']))
                c = iv(_i(l[0][f'{lab}_lo']), _i(l[0][f'{lab}_hi']))
                if a is None or c is None:
                    continue
                v = classify(a, c)                  # "C" slot = long budget
                verdict = {'certified C > W': 'certified long > short',
                           'certified W > C': 'certified short > long',
                           'certified equality': 'certified equality',
                           'unresolved': 'unresolved'}[v['verdict']]
                t3[(lab, sc, verdict)] += 1
                det3.append(dict(instance_id=iid, solver=lab, scheme=sc,
                                 short=[a['lo'], a['hi']], long=[c['lo'], c['hi']],
                                 verdict=verdict))
    for lab in ('W', 'C'):
        for sc in ('prefix', 'uniform0'):
            tot = sum(v for (l, s, _), v in t3.items() if l == lab and s == sc)
            if tot:
                print(f"  solver {lab}  {sc:<9} n={tot}:  " +
                      '  '.join(f'{k[2]}={v}' for k, v in sorted(t3.items())
                                if k[0] == lab and k[1] == sc))
    out['table3_short_vs_long'] = {f'{k[0]}|{k[1]}|{k[2]}': v for k, v in t3.items()}
    out['table3_detail'] = det3

    # ----------------------------- 4. collection success / insufficiency
    print("\n" + "=" * 110)
    print("TABLE 4 — COLLECTION SUCCESS AND INSUFFICIENT SAMPLES")
    print("=" * 110)
    print(f"  {'instance':<16}{'slv':>4}{'bank 5s':>10}{'bank 30s':>10}"
          f"{'dups':>10}{'attempts':>10}{'elig5':>7}{'elig30':>7}")
    nfail5 = nfail30 = 0
    for r in idx['rows']:
        if not r['elig5']:
            nfail5 += 1
        if not r['elig30']:
            nfail30 += 1
        print(f"  {r['instance_id']:<16}{r['solver']:>4}{r['b5']:>10}{r['b30']:>10}"
              f"{r['duplicates']:>10}{r['attempts']:>10}"
              f"{('yes' if r['elig5'] else 'NO'):>7}"
              f"{('yes' if r['elig30'] else 'NO'):>7}")
    print(f"\n  solver-instance cells failing to reach k={P.K_RETAIN}: "
          f"5 s {nfail5}/{len(idx['rows'])}, 30 s {nfail30}/{len(idx['rows'])}")
    print(f"  resource-limited collections: "
          f"{sum(1 for r in idx['rows'] if r['resource_limited'])}")
    print("\n  An insufficient sample is NOT evidence of poor geometric resolution:")
    print("  the formula may simply have fewer than k solutions, which is not")
    print("  established here and is not claimed.")
    out['table4_collection'] = dict(cells=len(idx['rows']), fail_k_5s=nfail5,
                                    fail_k_30s=nfail30,
                                    resource_limited=sum(1 for r in idx['rows']
                                                         if r['resource_limited']))

    # --------------------------------------------- replicate sensitivity
    print("\n" + "=" * 110)
    print("REPLICATE SENSITIVITY (uniform0 is primary; 1 and 2 are checks, "
          "NOT extra instances)")
    print("=" * 110)
    rep = collections.defaultdict(list)
    for r in rows:
        if r['scheme'].startswith('uniform') and r['verdict'] != 'ineligible':
            rep[(r['instance_id'], r['budget'])].append((r['scheme'], r['verdict']))
    varied = [k for k, v in rep.items() if len({x[1] for x in v}) > 1]
    print(f"  instance-budget cells with all three replicates: "
          f"{sum(1 for v in rep.values() if len(v) == 3)}")
    print(f"  cells whose verdict VARIES across replicates: {len(varied)}"
          + (f' -> {varied[:5]}' if varied else ''))
    out['replicate_sensitivity'] = dict(
        cells=len(rep), varied=len(varied), varied_cells=[list(k) for k in varied])

    with open(os.path.join(P.EXT, 'data', 'analysis_summary.json'), 'w') as f:
        json.dump(out, f, indent=2, default=str)
    print("\n  wrote data/analysis_summary.json")
    return 0


if __name__ == '__main__':
    sys.exit(main())
