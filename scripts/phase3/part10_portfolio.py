"""
Phase 3, Part 10: combined solver coverage ("portfolio geometry"). Uses the
already-computed union quantities in cdcl_stage_b_results (eps_hat_union,
coverage_union, A_union_size), computed there from A_W(I) union A_C(I).
Tests whether eps_union < min(eps_W, eps_C) on a substantial fraction of
instances -- a purely geometric observation, no portfolio-runtime claim.
"""
import json
import numpy as np

def main():
    with open("../data/cdcl_stage_b_results_test.json") as f:
        recs = json.load(f)

    rows = []
    for r in recs:
        eW, eC, eU = r["eps_hat_W"], r["eps_hat_C"], r["eps_hat_union"]
        if eW is None or eC is None or eU is None:
            continue
        rows.append({
            "id": r["id"], "n": r["n"], "alpha": r["alpha"], "regime": r["regime"],
            "S_I_size": r["S_I_size"],
            "eps_W": eW, "eps_C": eC, "eps_union": eU,
            "coverage_W": r["coverage_W"], "coverage_C": r["coverage_C"], "coverage_union": r["coverage_union"],
            "strictly_better": eU < min(eW, eC),
            "improvement_over_best_single": min(eW, eC) - eU,
        })

    n = len(rows)
    n_strict = sum(1 for r in rows if r["strictly_better"])
    print(f"Instances with eps_union computable: {n}")
    print(f"eps_union < min(eps_W, eps_C) strictly: {n_strict}/{n} ({100*n_strict/n:.1f}%)")

    imp = np.array([r["improvement_over_best_single"] for r in rows])
    print(f"Median improvement (min(eW,eC) - eU): {np.median(imp):.3f}")
    print(f"Mean improvement: {np.mean(imp):.3f}")
    print(f"Fraction with improvement > 0: {(imp>0).mean():.3f}")
    print(f"Fraction with improvement == 0 (union = best single): {(imp==0).mean():.3f}")

    cov_gain = np.array([r["coverage_union"] - max(r["coverage_W"], r["coverage_C"]) for r in rows])
    print(f"\nMedian coverage gain (union - max(cov_W,cov_C)): {np.median(cov_gain):.4f}")
    print(f"Mean coverage gain: {np.mean(cov_gain):.4f}")

    print("\nBy regime:")
    for regime in ["solution_rich", "intermediate", "near_threshold"]:
        sub = [r for r in rows if r["regime"] == regime]
        if not sub:
            continue
        ns = sum(1 for r in sub if r["strictly_better"])
        print(f"  {regime}: n={len(sub)}, eps_union<min strictly: {ns}/{len(sub)} ({100*ns/len(sub):.1f}%), "
              f"median_improvement={np.median([r['improvement_over_best_single'] for r in sub]):.3f}")

    with open("../data/part10_portfolio.json", "w") as f:
        json.dump(rows, f, indent=2)
    print("\nWrote ../data/part10_portfolio.json")

if __name__ == "__main__":
    main()
