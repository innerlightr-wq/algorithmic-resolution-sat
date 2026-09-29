"""
Phase 4, Part 12: aggressive audit of the "4-13x fragmentation" claim, which
Phase 3 established from only TWO pre-specified instances. This script
computes fragmentation (C_A(1) vs C_S(1), fixed r=1, matching the radius
used in both paired Phase 2/3 trajectory instances) for BOTH solvers across
ALL 360 test instances at their STANDARD (non-trajectory-swept) budgets --
i.e. WalkSAT's K=150-restart A_W(I) and CDCL's R=5,T=8 A_C(I), exactly as
used throughout Phase 2/3's main pipeline -- to test whether the two-instance
finding generalizes.
"""
import json
import sys
import numpy as np

sys.path.insert(0, "../../phase2/scripts")
from topology_utils import pairwise_hamming_matrix, cluster_count_from_dist_matrix


def main():
    with open("../../phase3/data/cdcl_stage_b_results_test.json") as f:
        recs = json.load(f)

    rows = []
    for rec in recs:
        S_I = [tuple(x) for x in rec["S_I"]]
        if len(S_I) < 2:
            continue
        # A_W(I) not stored directly in cdcl_stage_b_results; reconstruct via S_I \ M_W
        M_W = set(tuple(x) for x in rec["M_W"])
        A_W = [x for x in S_I if x not in M_W]
        M_C = set(tuple(x) for x in rec["M_C"])
        A_C = [x for x in S_I if x not in M_C]

        if len(A_W) < 2 or len(A_C) < 2:
            continue

        S_arr = np.array(S_I, dtype=np.int8)
        D_S = pairwise_hamming_matrix(S_arr)
        C_S_1 = cluster_count_from_dist_matrix(D_S, 1)

        A_W_arr = np.array(A_W, dtype=np.int8)
        A_C_arr = np.array(A_C, dtype=np.int8)
        D_AW = pairwise_hamming_matrix(A_W_arr)
        D_AC = pairwise_hamming_matrix(A_C_arr)
        C_AW_1 = cluster_count_from_dist_matrix(D_AW, 1)
        C_AC_1 = cluster_count_from_dist_matrix(D_AC, 1)

        excess_W = C_AW_1 - C_S_1
        excess_C = C_AC_1 - C_S_1

        rows.append({
            "id": rec["id"], "n": rec["n"], "alpha": rec["alpha"], "regime": rec["regime"],
            "S_I_size": len(S_I), "A_W_size": len(A_W), "A_C_size": len(A_C),
            "coverage_W": rec["coverage_W"], "coverage_C": rec["coverage_C"],
            "C_S_1": C_S_1, "C_AW_1": C_AW_1, "C_AC_1": C_AC_1,
            "excess_W": excess_W, "excess_C": excess_C,
        })

    with open("../data/fragmentation_replication.json", "w") as f:
        json.dump(rows, f, indent=2)

    n = len(rows)
    print(f"Instances with |A_W|>=2, |A_C|>=2, |S_I|>=2: {n}/{len(recs)}")

    excess_W = np.array([r["excess_W"] for r in rows])
    excess_C = np.array([r["excess_C"] for r in rows])

    print(f"\nAbsolute fragmentation (excess components at r=1):")
    print(f"  WalkSAT: mean={excess_W.mean():.2f}, median={np.median(excess_W):.2f}, "
          f"frac_fragmented(excess>0)={np.mean(excess_W>0):.3f}")
    print(f"  CDCL:    mean={excess_C.mean():.2f}, median={np.median(excess_C):.2f}, "
          f"frac_fragmented(excess>0)={np.mean(excess_C>0):.3f}")

    # ratio only where WalkSAT excess > 0 (avoid divide-by-zero)
    both_frag = [(r["excess_W"], r["excess_C"]) for r in rows if r["excess_W"] > 0]
    ratios = [w / max(c, 1) for w, c in both_frag]  # +1 smoothing on denominator to avoid div0; documented
    print(f"\nRelative ratio (excess_W / max(excess_C,1)), among {len(both_frag)} instances "
          f"where WalkSAT shows any fragmentation:")
    print(f"  median ratio = {np.median(ratios):.2f}")
    print(f"  mean ratio = {np.mean(ratios):.2f}")
    print(f"  [25th,75th] percentile = [{np.percentile(ratios,25):.2f}, {np.percentile(ratios,75):.2f}]")

    # bootstrap CI on median ratio
    rng = np.random.default_rng(20260929)
    boots = [np.median(rng.choice(ratios, size=len(ratios), replace=True)) for _ in range(3000)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    print(f"  95% bootstrap CI on median ratio: [{lo:.2f}, {hi:.2f}]")

    print(f"\nPaired comparison (Wilcoxon signed-rank, excess_W vs excess_C, all {n} instances):")
    from scipy.stats import wilcoxon
    try:
        stat, p = wilcoxon(excess_W, excess_C)
        print(f"  stat={stat}, p={p:.3g}, median(excess_W - excess_C)={np.median(excess_W-excess_C):.2f}")
    except Exception as e:
        print(f"  failed: {e}")

    print("\n--- Stratified by regime ---")
    for regime in ["solution_rich", "intermediate", "near_threshold"]:
        sub = [r for r in rows if r["regime"] == regime]
        ew = np.array([r["excess_W"] for r in sub])
        ec = np.array([r["excess_C"] for r in sub])
        print(f"  {regime}: n={len(sub)}, mean_excess_W={ew.mean():.2f}, mean_excess_C={ec.mean():.2f}, "
              f"frac_frag_W={np.mean(ew>0):.3f}, frac_frag_C={np.mean(ec>0):.3f}")

    print("\n--- Stratified by n ---")
    for n_val in [16, 18, 20]:
        sub = [r for r in rows if r["n"] == n_val]
        ew = np.array([r["excess_W"] for r in sub])
        ec = np.array([r["excess_C"] for r in sub])
        print(f"  n={n_val}: n_inst={len(sub)}, mean_excess_W={ew.mean():.2f}, mean_excess_C={ec.mean():.2f}")

    print("\n--- Stratified by coverage band (own coverage, W vs C separately) ---")
    for lo_c, hi_c, lbl in [(0, 0.2, "0-20%"), (0.2, 0.5, "20-50%"), (0.5, 1.01, "50-100%")]:
        subW = [r for r in rows if lo_c <= r["coverage_W"] < hi_c]
        subC = [r for r in rows if lo_c <= r["coverage_C"] < hi_c]
        ewv = np.array([r["excess_W"] for r in subW]) if subW else np.array([])
        ecv = np.array([r["excess_C"] for r in subC]) if subC else np.array([])
        print(f"  coverage {lbl}: WalkSAT n={len(subW)} mean_excess={ewv.mean() if len(ewv) else None}; "
              f"CDCL n={len(subC)} mean_excess={ecv.mean() if len(ecv) else None}")

    # coverage-matched comparison (same as Part 8 logic)
    matched = [r for r in rows if abs(r["coverage_W"] - r["coverage_C"]) < 0.10]
    ewm = np.array([r["excess_W"] for r in matched])
    ecm = np.array([r["excess_C"] for r in matched])
    print(f"\n--- Coverage-matched (|cov_W-cov_C|<0.10), n={len(matched)} ---")
    print(f"  mean_excess_W={ewm.mean():.2f}, mean_excess_C={ecm.mean():.2f}")
    if len(matched) > 5:
        statm, pm = wilcoxon(ewm, ecm)
        print(f"  Wilcoxon (matched): stat={statm}, p={pm:.3g}")


if __name__ == "__main__":
    main()
