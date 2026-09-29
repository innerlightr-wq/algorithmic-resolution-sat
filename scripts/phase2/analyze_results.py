"""
Phase 2, Parts 8-9: baselines, metrics, model selection on TRAIN, final
evaluation on TEST (touched exactly once, after selection is frozen).

Candidate risk scores (direction chosen so that HIGHER = predicted HIGHER
miss risk):
  risk_basin          = -basin              (solver-dynamics predictor)
  risk_disc_flips      = +disc_flips          (solver-dynamics predictor)
  risk_foundneighbor   = -foundneighbor       (geometry-of-A(I)-only predictor / baseline 4)
  risk_hamming_weight  = sign_hw * hamming_weight  (baseline 2; sign chosen on TRAIN only)
  risk_random          = random_score         (baseline 1, null)

Target labels (retrospective, from stage_b results):
  has_missed_neighbor (binary): AUROC, AUPRC
  miss_rho (continuous count): Spearman rank correlation

Instance is the independent unit throughout (Part 9 instruction): per-
instance metric computed first, then aggregated via median + instance-level
bootstrap CI across instances, never by pooling individual found-solutions
across instances as if independent.
"""
import json
import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score, average_precision_score

RNG = np.random.default_rng(20260928 + 42)
MIN_FOUND_FOR_INSTANCE = 4  # need at least this many found solutions to compute within-instance metrics


def load(split):
    with open(f"../data/stage_b_results_{split}.json") as f:
        return json.load(f)


def per_instance_frame(records):
    """Returns list of dicts, one per qualifying instance, with arrays for each score/label."""
    out = []
    for rec in records:
        pfs = rec["per_found_solution"]
        if len(pfs) < MIN_FOUND_FOR_INSTANCE:
            continue
        basin = np.array([p["basin"] for p in pfs], dtype=float)
        disc_flips = np.array([p["disc_flips"] for p in pfs], dtype=float)
        foundneighbor = np.array([p["foundneighbor"] for p in pfs], dtype=float)
        hw = np.array([p["hamming_weight"] for p in pfs], dtype=float)
        rnd = np.array([p["random_score"] for p in pfs], dtype=float)
        miss_rho = np.array([p["miss_rho"] for p in pfs], dtype=float)
        label = np.array([p["has_missed_neighbor"] for p in pfs], dtype=int)
        out.append({
            "id": rec["id"], "n": rec["n"], "alpha": rec["alpha"], "regime": rec["regime"],
            "S_I_size": rec["S_I_size"], "A_I_size": rec["A_I_size"], "M_A_I_size": rec["M_A_I_size"],
            "coverage": rec["coverage"], "eps_hat": rec["eps_hat"],
            "basin": basin, "disc_flips": disc_flips, "foundneighbor": foundneighbor,
            "hamming_weight": hw, "random_score": rnd,
            "miss_rho": miss_rho, "label": label,
        })
    return out


def safe_auroc(scores, labels):
    if len(set(labels.tolist())) < 2:
        return None
    if np.all(scores == scores[0]):
        return None
    return roc_auc_score(labels, scores)


def safe_auprc(scores, labels):
    if len(set(labels.tolist())) < 2:
        return None
    if np.all(scores == scores[0]):
        return None
    return average_precision_score(labels, scores)


def safe_spearman(scores, target):
    if len(set(scores.tolist())) < 2 or len(set(target.tolist())) < 2:
        return None
    rho, p = spearmanr(scores, target)
    if np.isnan(rho):
        return None
    return rho


def build_risk_scores(inst, hw_sign):
    return {
        "risk_basin": -inst["basin"],
        "risk_disc_flips": inst["disc_flips"],
        "risk_foundneighbor": -inst["foundneighbor"],
        "risk_hamming_weight": hw_sign * inst["hamming_weight"],
        "risk_random": inst["random_score"],
    }


def evaluate_predictor(instances, score_name, hw_sign=1.0):
    aurocs, auprcs, spearmans = [], [], []
    n_skipped_auroc = 0
    n_skipped_spearman = 0
    per_instance_rows = []
    for inst in instances:
        risks = build_risk_scores(inst, hw_sign)
        s = risks[score_name]
        auroc = safe_auroc(s, inst["label"])
        auprc = safe_auprc(s, inst["label"])
        rho = safe_spearman(s, inst["miss_rho"])
        if auroc is None:
            n_skipped_auroc += 1
        else:
            aurocs.append(auroc)
        if auprc is not None:
            auprcs.append(auprc)
        if rho is None:
            n_skipped_spearman += 1
        else:
            spearmans.append(rho)
        per_instance_rows.append({
            "id": inst["id"], "n": inst["n"], "alpha": inst["alpha"], "regime": inst["regime"],
            "auroc": auroc, "auprc": auprc, "spearman": rho,
            "n_found": len(inst["label"]), "n_missed_neighbor_positive": int(inst["label"].sum()),
        })
    return {
        "score_name": score_name,
        "n_instances_total": len(instances),
        "n_instances_auroc_evaluable": len(aurocs),
        "n_instances_skipped_auroc": n_skipped_auroc,
        "median_auroc": float(np.median(aurocs)) if aurocs else None,
        "mean_auroc": float(np.mean(aurocs)) if aurocs else None,
        "median_auprc": float(np.median(auprcs)) if auprcs else None,
        "median_spearman": float(np.median(spearmans)) if spearmans else None,
        "mean_spearman": float(np.mean(spearmans)) if spearmans else None,
        "n_instances_spearman_evaluable": len(spearmans),
        "aurocs": aurocs,
        "spearmans": spearmans,
        "per_instance": per_instance_rows,
    }


def bootstrap_ci(values, n_boot=5000, alpha=0.05, agg=np.median):
    if len(values) == 0:
        return None, None, None
    values = np.array(values)
    point = float(agg(values))
    boots = np.array([agg(RNG.choice(values, size=len(values), replace=True)) for _ in range(n_boot)])
    lo, hi = np.percentile(boots, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return point, float(lo), float(hi)


def permutation_test_auroc(instances, score_name, hw_sign=1.0, n_perm=1000):
    """
    Instance-level permutation test: for each instance, permute the label
    vector (breaking the score-label pairing WITHIN that instance) n_perm
    times, recompute AUROC, average over instances to get a null median-AUROC
    distribution; compare the TRUE median-AUROC to this null distribution.
    """
    true_aurocs = []
    perm_medians = []
    instance_data = []
    for inst in instances:
        risks = build_risk_scores(inst, hw_sign)
        s = risks[score_name]
        label = inst["label"]
        auroc = safe_auroc(s, label)
        if auroc is None:
            continue
        true_aurocs.append(auroc)
        instance_data.append((s, label))

    if not true_aurocs:
        return None
    true_median = float(np.median(true_aurocs))

    for _ in range(n_perm):
        perm_aurocs = []
        for s, label in instance_data:
            perm_label = RNG.permutation(label)
            a = safe_auroc(s, perm_label)
            if a is not None:
                perm_aurocs.append(a)
        if perm_aurocs:
            perm_medians.append(np.median(perm_aurocs))

    perm_medians = np.array(perm_medians)
    p_value = float((np.sum(perm_medians >= true_median) + 1) / (len(perm_medians) + 1))
    return {
        "true_median_auroc": true_median,
        "null_median_auroc_mean": float(np.mean(perm_medians)),
        "null_median_auroc_std": float(np.std(perm_medians)),
        "p_value_one_sided": p_value,
        "n_perm": n_perm,
    }


def stratify_by(instances, key):
    groups = {}
    for inst in instances:
        groups.setdefault(inst[key], []).append(inst)
    return groups


def main():
    train_records = load("train")
    test_records = load("test")
    train_inst = per_instance_frame(train_records)
    test_inst = per_instance_frame(test_records)

    print(f"Train: {len(train_inst)}/{len(train_records)} instances qualify "
          f"(>= {MIN_FOUND_FOR_INSTANCE} found solutions)")
    print(f"Test:  {len(test_inst)}/{len(test_records)} instances qualify\n")

    candidate_scores = ["risk_basin", "risk_disc_flips", "risk_foundneighbor",
                         "risk_hamming_weight", "risk_random"]

    # ---- MODEL SELECTION ON TRAIN ONLY ----
    print("=" * 70)
    print("MODEL SELECTION (TRAIN SPLIT ONLY)")
    print("=" * 70)

    # choose hamming_weight sign on train
    hw_pos = evaluate_predictor(train_inst, "risk_hamming_weight", hw_sign=1.0)
    hw_neg = evaluate_predictor(train_inst, "risk_hamming_weight", hw_sign=-1.0)
    hw_pos_med = hw_pos["median_auroc"] or 0.5
    hw_neg_med = hw_neg["median_auroc"] or 0.5
    chosen_hw_sign = 1.0 if abs(hw_pos_med - 0.5) >= abs(hw_neg_med - 0.5) else -1.0
    print(f"Hamming-weight baseline sign selection: +1 -> median AUROC={hw_pos_med:.4f}, "
          f"-1 -> median AUROC={hw_neg_med:.4f}  => chosen sign = {chosen_hw_sign:+.0f}")

    train_eval = {}
    for name in candidate_scores:
        train_eval[name] = evaluate_predictor(train_inst, name, hw_sign=chosen_hw_sign)
        e = train_eval[name]
        print(f"  {name:22s} median_AUROC={e['median_auroc']} "
              f"median_spearman={e['median_spearman']} "
              f"(n_eval={e['n_instances_auroc_evaluable']}/{e['n_instances_total']})")

    solver_dynamics_candidates = ["risk_basin", "risk_disc_flips"]
    chosen = max(
        solver_dynamics_candidates,
        key=lambda nm: (train_eval[nm]["median_auroc"] if train_eval[nm]["median_auroc"] is not None else -1)
    )
    print(f"\n=> CHOSEN PRIMARY SOLVER-DYNAMICS PREDICTOR (selected on TRAIN only): {chosen}")

    # ---- FINAL EVALUATION ON TEST (touched once) ----
    print("\n" + "=" * 70)
    print("FINAL EVALUATION (TEST SPLIT, TOUCHED ONCE)")
    print("=" * 70)

    test_eval = {}
    for name in candidate_scores:
        test_eval[name] = evaluate_predictor(test_inst, name, hw_sign=chosen_hw_sign)
        e = test_eval[name]
        pt, lo, hi = bootstrap_ci(e["aurocs"]) if e["aurocs"] else (None, None, None)
        pt_s, lo_s, hi_s = bootstrap_ci(e["spearmans"]) if e["spearmans"] else (None, None, None)
        print(f"  {name:22s} median_AUROC={pt} [{lo},{hi}]  "
              f"median_spearman={pt_s} [{lo_s},{hi_s}]  "
              f"(n_eval={e['n_instances_auroc_evaluable']}/{e['n_instances_total']})")

    # permutation test for the CHOSEN predictor on TEST
    perm_result = permutation_test_auroc(test_inst, chosen, hw_sign=chosen_hw_sign, n_perm=1000)
    print(f"\nPermutation test for chosen predictor ({chosen}) on TEST: {perm_result}")

    # permutation test for random baseline on TEST (sanity check -- should be non-significant)
    perm_result_random = permutation_test_auroc(test_inst, "risk_random", hw_sign=chosen_hw_sign, n_perm=1000)
    print(f"Permutation test for risk_random (sanity null check) on TEST: {perm_result_random}")

    # ---- STRATIFICATION CHECKS (Simpson's-paradox-style, per regime and per n) ----
    print("\n" + "=" * 70)
    print("STRATIFIED RESULTS FOR CHOSEN PREDICTOR (TEST SPLIT)")
    print("=" * 70)
    strat_results = {}
    for key in ["regime", "n"]:
        groups = stratify_by(test_inst, key)
        strat_results[key] = {}
        for gval, ginst in groups.items():
            e = evaluate_predictor(ginst, chosen, hw_sign=chosen_hw_sign)
            strat_results[key][str(gval)] = {
                "median_auroc": e["median_auroc"], "n_instances": len(ginst),
                "n_evaluable": e["n_instances_auroc_evaluable"],
            }
            print(f"  {key}={gval}: median_AUROC={e['median_auroc']} "
                  f"(n={len(ginst)}, evaluable={e['n_instances_auroc_evaluable']})")

    # ---- eps_hat / coverage / topology-adjacent correlations (Part 10 prep) ----
    print("\n" + "=" * 70)
    print("PART 10 PREP: coverage vs eps_hat, chosen-predictor vs eps_hat (TEST)")
    print("=" * 70)
    cov = np.array([inst["coverage"] for inst in test_inst])
    eh = np.array([inst["eps_hat"] for inst in test_inst if inst["eps_hat"] is not None])
    cov_eh_pairs = [(inst["coverage"], inst["eps_hat"]) for inst in test_inst if inst["eps_hat"] is not None]
    if len(cov_eh_pairs) > 2:
        c_arr = np.array([p[0] for p in cov_eh_pairs])
        e_arr = np.array([p[1] for p in cov_eh_pairs])
        rho_cov_eh, p_cov_eh = spearmanr(c_arr, e_arr)
        print(f"Spearman(coverage, eps_hat) across TEST instances: rho={rho_cov_eh:.4f}, p={p_cov_eh:.4g}, n={len(c_arr)}")

    # ---- SAVE EVERYTHING ----
    output = {
        "min_found_for_instance": MIN_FOUND_FOR_INSTANCE,
        "chosen_hw_sign": chosen_hw_sign,
        "chosen_primary_predictor": chosen,
        "train_evaluation": {k: {kk: vv for kk, vv in v.items() if kk != "per_instance"} for k, v in train_eval.items()},
        "test_evaluation": {k: {kk: vv for kk, vv in v.items() if kk != "per_instance"} for k, v in test_eval.items()},
        "test_evaluation_per_instance": {k: v["per_instance"] for k, v in test_eval.items()},
        "permutation_test_chosen_predictor": perm_result,
        "permutation_test_random_baseline": perm_result_random,
        "stratified_results_test": strat_results,
        "n_train_instances_qualifying": len(train_inst),
        "n_test_instances_qualifying": len(test_inst),
    }
    with open("../data/analysis_results.json", "w") as f:
        json.dump(output, f, indent=2, default=str)
    print("\nWrote ../data/analysis_results.json")


if __name__ == "__main__":
    main()
