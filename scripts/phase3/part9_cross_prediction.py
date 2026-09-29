"""
Phase 3, Part 9: cross-prediction. Four tests, TEST split only, no retraining:
  1. WalkSAT predictor (risk_basin) -> WalkSAT blind zone   [Phase 2 benchmark, reproduced here for a single consistent report]
  2. CDCL predictor (risk_cdcl_recurrence) -> CDCL blind zone  [Phase 3 Part 6 benchmark, reproduced here]
  3. WalkSAT predictor (risk_basin, scored on y in A_W(I)) -> CDCL blind zone (miss_rho w.r.t. M_C)
  4. CDCL predictor (risk_cdcl_recurrence, scored on y in A_C(I)) -> WalkSAT blind zone (miss_rho w.r.t. M_W)

No retraining/refitting anywhere -- risk_basin and risk_cdcl_recurrence keep
their Phase 2 / Phase 3 Part 6 definitions and sign conventions unchanged;
only the TARGET LABEL changes (whose blind zone is being predicted).
"""
import json
import numpy as np
from sklearn.metrics import roc_auc_score
from scipy.stats import spearmanr

RNG = np.random.default_rng(20260928 + 7777)
MIN_FOUND = 4


def hamming(a, b):
    return sum(x != y for x, y in zip(a, b))


def safe_auroc(scores, labels):
    if len(set(labels.tolist())) < 2 or np.all(scores == scores[0]):
        return None
    return roc_auc_score(labels, scores)


def safe_spearman(scores, target):
    if len(set(scores.tolist())) < 2 or len(set(target.tolist())) < 2:
        return None
    rho, p = spearmanr(scores, target)
    return None if np.isnan(rho) else rho


def bootstrap_ci(values, n_boot=5000, alpha=0.05):
    if not values:
        return None, None, None
    values = np.array(values)
    point = float(np.median(values))
    boots = np.array([np.median(RNG.choice(values, size=len(values), replace=True)) for _ in range(n_boot)])
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return point, float(lo), float(hi)


def main():
    with open("../../phase2/data/stage_b_results_test.json") as f:
        walksat_sb = json.load(f)
    with open("../data/cdcl_stage_b_results_test.json") as f:
        cdcl_sb = json.load(f)
    cdcl_by_id = {r["id"]: r for r in cdcl_sb}

    results = {"within_W": [], "within_C": [], "cross_W_to_C": [], "cross_C_to_W": []}

    for wrec in walksat_sb:
        iid = wrec["id"]
        crec = cdcl_by_id.get(iid)
        if crec is None:
            continue
        M_W = set(tuple(x) for x in crec["M_W"])
        M_C = set(tuple(x) for x in crec["M_C"])

        # within-W (reproduces Phase 2)
        pfs_w = wrec["per_found_solution"]
        if len(pfs_w) >= MIN_FOUND:
            basin = np.array([p["basin"] for p in pfs_w], dtype=float)
            label_w = np.array([p["has_missed_neighbor"] for p in pfs_w], dtype=int)
            a = safe_auroc(-basin, label_w)
            if a is not None:
                results["within_W"].append({"id": iid, "auroc": a})

        # within-C (reproduces Part 6)
        pfs_c = crec["per_found_solution_C"]
        if len(pfs_c) >= MIN_FOUND:
            recur = np.array([p["recurrence"] for p in pfs_c], dtype=float)
            label_c = np.array([p["has_missed_neighbor"] for p in pfs_c], dtype=int)
            a = safe_auroc(-recur, label_c)
            if a is not None:
                results["within_C"].append({"id": iid, "auroc": a})

        # cross W->C: for y in A_W(I), score = risk_basin(y) = -basin(y); label = has M_C-neighbor within rho
        rho = crec["rho_used"]
        if len(pfs_w) >= MIN_FOUND and len(M_C) > 0:
            ys = [tuple(p["y"]) for p in pfs_w]
            basin_w = np.array([p["basin"] for p in pfs_w], dtype=float)
            label_wc = np.array([int(any(hamming(y, x) <= rho for x in M_C)) for y in ys], dtype=int)
            a = safe_auroc(-basin_w, label_wc)
            if a is not None:
                results["cross_W_to_C"].append({"id": iid, "auroc": a})

        # cross C->W: for y in A_C(I), score = risk_cdcl_recurrence(y); label = has M_W-neighbor within rho
        if len(pfs_c) >= MIN_FOUND and len(M_W) > 0:
            ys_c = [tuple(p["y"]) for p in pfs_c]
            recur_c = np.array([p["recurrence"] for p in pfs_c], dtype=float)
            label_cw = np.array([int(any(hamming(y, x) <= rho for x in M_W)) for y in ys_c], dtype=int)
            a = safe_auroc(-recur_c, label_cw)
            if a is not None:
                results["cross_C_to_W"].append({"id": iid, "auroc": a})

    print("Cross-prediction summary (TEST split, no retraining):\n")
    for key, label in [("within_W", "1. risk_basin -> WalkSAT blind zone (within-solver)"),
                        ("within_C", "2. risk_cdcl_recurrence -> CDCL blind zone (within-solver)"),
                        ("cross_W_to_C", "3. risk_basin -> CDCL blind zone (cross-solver)"),
                        ("cross_C_to_W", "4. risk_cdcl_recurrence -> WalkSAT blind zone (cross-solver)")]:
        aurocs = [r["auroc"] for r in results[key]]
        pt, lo, hi = bootstrap_ci(aurocs)
        print(f"{label}")
        print(f"   n_instances_evaluable={len(aurocs)}  median_AUROC={pt} [{lo},{hi}]\n")

    within_avg = np.mean([np.median([r["auroc"] for r in results["within_W"]]),
                           np.median([r["auroc"] for r in results["within_C"]])])
    cross_avg = np.mean([np.median([r["auroc"] for r in results["cross_W_to_C"]]),
                          np.median([r["auroc"] for r in results["cross_C_to_W"]])])
    print(f"Average within-solver median AUROC: {within_avg:.4f}")
    print(f"Average cross-solver median AUROC:  {cross_avg:.4f}")
    print(f"Within - Cross gap: {within_avg-cross_avg:.4f}")
    if within_avg - cross_avg > 0.05:
        print("=> within >> cross: evidence for SOLVER-SPECIFIC observational geometry")
    elif abs(within_avg - cross_avg) <= 0.05 and cross_avg > 0.55:
        print("=> within ~= cross > baseline: evidence for SHARED intrinsic difficulty")
    else:
        print("=> mixed/asymmetric pattern -- see per-direction breakdown, do not overclaim")

    with open("../data/part9_cross_prediction.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nWrote ../data/part9_cross_prediction.json")


if __name__ == "__main__":
    main()
