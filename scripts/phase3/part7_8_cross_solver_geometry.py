"""
Phase 3, Parts 7-8: cross-solver blind-zone geometry.

Part 7: for every paired test instance, compute Jaccard(M_W,M_C) and the
set-difference fractions, compared against a null model that controls for
each solver's blind-zone SIZE: under independence, given |M_W|,|M_C|,|S_I|,
the expected intersection size (hypergeometric mean) is |M_W|*|M_C|/|S_I|.
Compare observed vs expected via a per-instance ratio and an aggregate
(instance-level) signed comparison.

Part 8: decompose S_I into M_shared, M_Wonly, M_Conly, V (jointly visible),
and characterize each geometrically (Hamming weight, distance to visible
set V) -- test whether shared blind regions look geometrically distinct
from solver-specific blind regions.

Uses the TEST split only (held-out, cleanest single split for this
observational analysis -- no train/test model-selection concern here since
nothing is being fit).
"""
import json
import numpy as np
from scipy.stats import wilcoxon

def hamming(a, b):
    return sum(x != y for x, y in zip(a, b))

def main():
    with open("../data/cdcl_stage_b_results_test.json") as f:
        cdcl_recs = json.load(f)

    rows = []
    part8_rows = []
    for rec in cdcl_recs:
        S_I = [tuple(x) for x in rec["S_I"]]
        M_W = set(tuple(x) for x in rec["M_W"])
        M_C = set(tuple(x) for x in rec["M_C"])
        S_I_set = set(S_I)
        n_S = len(S_I)
        if n_S == 0:
            continue

        inter = M_W & M_C
        union = M_W | M_C
        jaccard = len(inter) / len(union) if union else None

        # null model: independence given sizes (hypergeometric expectation)
        expected_inter = len(M_W) * len(M_C) / n_S if n_S else 0
        expected_union = len(M_W) + len(M_C) - expected_inter
        expected_jaccard = expected_inter / expected_union if expected_union > 0 else None

        rows.append({
            "id": rec["id"], "n": rec["n"], "alpha": rec["alpha"], "regime": rec["regime"],
            "S_I_size": n_S, "M_W_size": len(M_W), "M_C_size": len(M_C),
            "jaccard_observed": jaccard, "jaccard_expected_null": expected_jaccard,
            "intersection_observed": len(inter), "intersection_expected_null": expected_inter,
            "frac_MW_only": len(M_W - M_C) / n_S, "frac_MC_only": len(M_C - M_W) / n_S,
            "frac_shared": len(inter) / n_S, "frac_union": len(union) / n_S,
        })

        # Part 8 decomposition
        M_shared = inter
        M_Wonly = M_W - M_C
        M_Conly = M_C - M_W
        V = S_I_set - union  # jointly visible (found by at least one solver... actually S_I - (M_W u M_C) = found by W or C or both, i.e. NOT missed by both. "jointly visible" per spec.)

        def mean_weight(pts):
            return float(np.mean([sum(p) for p in pts])) if pts else None

        def mean_dist_to_V(pts, V_list, cap=200):
            if not pts or not V_list:
                return None
            V_sample = V_list if len(V_list) <= cap else list(V_list)[:cap]
            dists = []
            for p in (list(pts)[:cap] if len(pts) > cap else pts):
                dists.append(min(hamming(p, v) for v in V_sample))
            return float(np.mean(dists))

        V_list = list(V)
        part8_rows.append({
            "id": rec["id"], "n": rec["n"], "regime": rec["regime"],
            "n_shared": len(M_shared), "n_Wonly": len(M_Wonly), "n_Conly": len(M_Conly), "n_V": len(V),
            "mean_weight_shared": mean_weight(M_shared), "mean_weight_Wonly": mean_weight(M_Wonly),
            "mean_weight_Conly": mean_weight(M_Conly), "mean_weight_V": mean_weight(V_list),
            "mean_dist_to_V_shared": mean_dist_to_V(M_shared, V_list),
            "mean_dist_to_V_Wonly": mean_dist_to_V(M_Wonly, V_list),
            "mean_dist_to_V_Conly": mean_dist_to_V(M_Conly, V_list),
        })

    # aggregate Part 7
    obs = np.array([r["jaccard_observed"] for r in rows if r["jaccard_observed"] is not None])
    exp = np.array([r["jaccard_expected_null"] for r in rows if r["jaccard_expected_null"] is not None
                     and r["jaccard_observed"] is not None])
    print(f"Part 7: {len(rows)} paired test instances")
    print(f"Median observed Jaccard(M_W,M_C): {np.median(obs):.4f}")
    print(f"Median null-expected Jaccard (independence given sizes): {np.median(exp):.4f}")
    ratio = obs / np.where(exp == 0, np.nan, exp)
    ratio = ratio[~np.isnan(ratio)]
    print(f"Median observed/expected ratio: {np.median(ratio):.3f} "
          f"({'MORE' if np.median(ratio)>1 else 'LESS'} overlapping than independence null)")
    try:
        stat, p = wilcoxon(obs - exp)
        print(f"Wilcoxon signed-rank test (observed vs expected intersection... using jaccard here): stat={stat}, p={p:.4g}")
    except Exception as e:
        print(f"Wilcoxon test failed: {e}")

    inter_obs = np.array([r["intersection_observed"] for r in rows])
    inter_exp = np.array([r["intersection_expected_null"] for r in rows])
    stat2, p2 = wilcoxon(inter_obs - inter_exp)
    print(f"Wilcoxon (intersection size observed vs expected): stat={stat2}, p={p2:.4g}, "
          f"median_diff={np.median(inter_obs-inter_exp):.3f}")

    print("\nBy regime:")
    for regime in ["solution_rich", "intermediate", "near_threshold"]:
        sub = [r for r in rows if r["regime"] == regime]
        o = np.array([r["jaccard_observed"] for r in sub if r["jaccard_observed"] is not None])
        e = np.array([r["jaccard_expected_null"] for r in sub if r["jaccard_expected_null"] is not None
                       and r["jaccard_observed"] is not None])
        if len(o):
            print(f"  {regime}: n={len(sub)}, median_obs_jaccard={np.median(o):.4f}, "
                  f"median_exp_jaccard={np.median(e):.4f}, ratio={np.median(o)/np.median(e) if np.median(e)>0 else float('nan'):.3f}")

    print(f"\n\nPart 8: geometric characterization of blind-zone decomposition")
    for field in ["mean_weight_shared", "mean_weight_Wonly", "mean_weight_Conly", "mean_weight_V"]:
        vals = [r[field] for r in part8_rows if r[field] is not None]
        print(f"  {field}: median={np.median(vals):.3f} (n={len(vals)})")
    for field in ["mean_dist_to_V_shared", "mean_dist_to_V_Wonly", "mean_dist_to_V_Conly"]:
        vals = [r[field] for r in part8_rows if r[field] is not None]
        if vals:
            print(f"  {field}: median={np.median(vals):.3f} (n={len(vals)})")

    with open("../data/part7_cross_solver_geometry.json", "w") as f:
        json.dump(rows, f, indent=2)
    with open("../data/part8_blind_zone_decomposition.json", "w") as f:
        json.dump(part8_rows, f, indent=2)
    print("\nWrote ../data/part7_cross_solver_geometry.json and part8_blind_zone_decomposition.json")

if __name__ == "__main__":
    main()
