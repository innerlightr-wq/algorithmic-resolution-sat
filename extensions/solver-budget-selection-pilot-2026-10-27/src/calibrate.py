"""Calibration: solver operation, timing, throughput and resource use ONLY.

Deliberately NOT computed here: resolution, covering radius, any distance
between assignments, or any solver-ordering outcome.  The purpose is to find
out whether the time-budgeted collection mechanism works and roughly how many
distinct solutions each solver records -- nothing that could inform the
hypothesis.

At most one fresh formula per (n, density) stratum, generated from the
CALIBRATION seed, which is disjoint from the study seed.
"""
import os, sys, json, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pilotlib as P
import store

OUT = os.path.join(P.EXT, 'data', 'calibration.json')


def main():
    rows = []
    print(f"calibration seed {P.CALIB_SEED} (disjoint from study seed {P.STUDY_SEED})")
    print(f"budgets {P.BUDGETS}  k_retain={P.K_RETAIN}\n")
    print(f"{'stratum':<12}{'solver':>7}{'budget':>8}{'distinct':>9}{'dups':>7}"
          f"{'restarts/runs':>14}{'elapsed':>9}{'cpu':>8}{'RSS MB':>8}  >=k?")
    for n in P.N_VALUES:
        for alpha in P.DENSITIES:
            cl, meta = P.make_formula(n, alpha, 0, base=P.CALIB_SEED)
            for lab in P.SOLVERS:
                seed, _ = P.collection_seed(f'calib|{lab}', meta['formula_hash'],
                                            base=P.CALIB_SEED)
                fn = P.collect_walksat if lab == 'W' else P.collect_cdcl
                bank, info = fn(cl, n, max(P.BUDGETS), seed)
                for b in P.BUDGETS:
                    snap = bank.snapshot(b)
                    rows.append(dict(stratum=meta['stratum'], n=n, alpha=alpha,
                                     solver=lab, budget=b, distinct=len(snap),
                                     eligible=len(snap) >= P.K_RETAIN,
                                     duplicates=info['duplicates'],
                                     attempts=info.get('restarts') or info.get('runs'),
                                     elapsed_s=round(info['elapsed_s'], 2),
                                     cpu_s=round(info['cpu_s'], 2),
                                     peak_rss_mb=info['peak_rss_mb'],
                                     rejected_invalid=info['rejected_invalid'],
                                     formula_hash=meta['formula_hash']))
                    print(f"{meta['stratum']:<12}{lab:>7}{b:>8.0f}{len(snap):>9}"
                          f"{info['duplicates']:>7}"
                          f"{(info.get('restarts') or info.get('runs')):>14}"
                          f"{info['elapsed_s']:>9.1f}{info['cpu_s']:>8.1f}"
                          f"{info['peak_rss_mb']:>8.0f}"
                          f"  {'yes' if len(snap)>=P.K_RETAIN else 'NO'}", flush=True)
    store.atomic_write_text(OUT, json.dumps(dict(
        calibration_seed=P.CALIB_SEED, budgets=list(P.BUDGETS),
        k_retain=P.K_RETAIN, walksat=P.WALKSAT, cdcl=P.CDCL,
        note='operational metrics only; no resolution computed',
        rows=rows), indent=2))
    el = sum(1 for r in rows if r['eligible'])
    print(f"\n  {el}/{len(rows)} (stratum, solver, budget) cells reached k={P.K_RETAIN}")
    print(f"  wrote data/calibration.json")
    return 0


if __name__ == '__main__':
    sys.exit(main())
