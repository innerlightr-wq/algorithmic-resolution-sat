"""
Phase 3, Part 6: CDCL held-out blind-zone prediction test. Mirrors Phase 2's
analyze_results.py discipline exactly (PHASE2_FREEZE.md): model selection on
TRAIN only, final evaluation on TEST touched once, instance as independent
unit, median + instance-level bootstrap CI, instance-level permutation test.
"""
import json
import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score, average_precision_score

RNG = np.random.default_rng(20260928 + 4242)
MIN_FOUND_FOR_INSTANCE = 4


def load(split):
    with open(f"../data/cdcl_stage_b_results_{split}.json") as f:
        return json.load(f)


def per_instance_frame(records):
    out = []
    for rec in records:
        pfs = rec["per_found_solution_C"]
        if len(pfs) < MIN_FOUND_FOR_INSTANCE:
            continue
        recurrence = np.array([p["recurrence"] for p in pfs], dtype=float)
        conflicts = np.array([p["conflicts_to_discovery"] for p in pfs], dtype=float)
        decisions = np.array([p["decisions_to_discovery"] for p in pfs], dtype=float)
        foundneighbor = np.array([p["foundneighbor"] for p in pfs], dtype=float)
        hw = np.array([p["hamming_weight"] for p in pfs], dtype=float)
        rnd = np.array([p["random_score"] for p in pfs], dtype=float)
        miss_rho = np.array([p["miss_rho"] for p in pfs], dtype=float)
        label = np.array([p["has_missed_neighbor"] for p in pfs], dtype=int)
        out.append({
            "id": rec["id"], "n": rec["n"], "alpha": rec["alpha"], "regime": rec["regime"],
            "S_I_size": rec["S_I_size"], "A_C_size": rec["A_C_size"], "M_C_size": rec["M_C_size"],
            "coverage_C": rec["coverage_C"], "eps_hat_C": rec["eps_hat_C"],
            "recurrence": recurrence, "conflicts_to_discovery": conflicts, "decisions_to_discovery": decisions,
            "foundneighbor": foundneighbor, "hamming_weight": hw, "random_score": rnd,
            "miss_rho": miss_rho, "label": label,
        })
    return out


def safe_auroc(scores, labels):
    if len(set(labels.tolist())) < 2 or np.all(scores == scores[0]):
        return None
    return roc_auc_score(labels, scores)


def safe_auprc(scores, labels):
    if len(set(labels.tolist())) < 2 or np.all(scores == scores[0]):
        return None
    return average_precision_score(labels, scores)


def safe_spearman(scores, target):
    if len(set(scores.tolist())) < 2 or len(set(target.tolist())) < 2:
        return None
    rho, p = spearmanr(scores, target)
    return None if np.isnan(rho) else rho


def build_risk_scores(inst, hw_sign):
    return {
        "risk_cdcl_recurrence": -inst["recurrence"],
        "risk_cdcl_conflicts": inst["conflicts_to_discovery"],
        "risk_cdcl_decisions": inst["decisions_to_discovery"],
        "risk_foundneighbor": -inst["foundneighbor"],
        "risk_hamming_weight": hw_sign * inst["hamming_weight"],
        "risk_random": inst["random_score"],
    }


def evaluate_predictor(instances, score_name, hw_sign=1.0):
    aurocs, auprcs, spearmans = [], [], []
    n_skipped = 0
    per_instance_rows = []
    for inst in instances:
        risks = build_risk_scores(inst, hw_sign)
        s = risks[score_name]
        auroc = safe_auroc(s, inst["label"])
        auprc = safe_auprc(s, inst["label"])
        rho = safe_spearman(s, inst["miss_rho"])
        if auroc is None:
            n_skipped += 1
        else:
            aurocs.append(auroc)
        if auprc is not None:
            auprcs.append(auprc)
        if rho is not None:
            spearmans.append(rho)
        per_instance_rows.append({
            "id": inst["id"], "n": inst["n"], "alpha": inst["alpha"], "regime": inst["regime"],
            "auroc": auroc, "auprc": auprc, "spearman": rho,
            "n_found": len(inst["label"]), "n_pos": int(inst["label"].sum()),
        })
    return {
        "score_name": score_name, "n_instances_total": len(instances),
        "n_instances_auroc_evaluable": len(aurocs), "n_instances_skipped_auroc": n_skipped,
        "median_auroc": float(np.median(aurocs)) if aurocs else None,
        "median_auprc": float(np.median(auprcs)) if auprcs else None,
        "median_spearman": float(np.median(spearmans)) if spearmans else None,
        "aurocs": aurocs, "spearmans": spearmans, "per_instance": per_instance_rows,
    }


def bootstrap_ci(values, n_boot=5000, alpha=0.05, agg=np.median):
    if not values:
        return None, None, None
    values = np.array(values)
    point = float(agg(values))
    boots = np.array([agg(RNG.choice(values, size=len(values), replace=True)) for _ in range(n_boot)])
    lo, hi = np.percentile(boots, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return point, float(lo), float(hi)


def permutation_test_auroc(instances, score_name, hw_sign=1.0, n_perm=1000):
    true_aurocs, instance_data = [], []
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
    perm_medians = []
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
    return {"true_median_auroc": true_median, "null_median_auroc_mean": float(np.mean(perm_medians)),
            "null_median_auroc_std": float(np.std(perm_medians)), "p_value_one_sided": p_value, "n_perm": n_perm}


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

    print(f"Train: {len(train_inst)}/{len(train_records)} instances qualify (>= {MIN_FOUND_FOR_INSTANCE} found)")
    print(f"Test:  {len(test_inst)}/{len(test_records)} instances qualify\n")

    candidate_scores = ["risk_cdcl_recurrence", "risk_cdcl_conflicts", "risk_cdcl_decisions",
                         "risk_foundneighbor", "risk_hamming_weight", "risk_random"]

    print("=" * 70)
    print("MODEL SELECTION (TRAIN SPLIT ONLY)")
    print("=" * 70)
    hw_pos = evaluate_predictor(train_inst, "risk_hamming_weight", hw_sign=1.0)
    hw_neg = evaluate_predictor(train_inst, "risk_hamming_weight", hw_sign=-1.0)
    hw_pos_med = hw_pos["median_auroc"] or 0.5
    hw_neg_med = hw_neg["median_auroc"] or 0.5
    chosen_hw_sign = 1.0 if abs(hw_pos_med - 0.5) >= abs(hw_neg_med - 0.5) else -1.0
    print(f"Hamming-weight sign: +1 -> {hw_pos_med:.4f}, -1 -> {hw_neg_med:.4f} => chosen {chosen_hw_sign:+.0f}")

    train_eval = {}
    for name in candidate_scores:
        train_eval[name] = evaluate_predictor(train_inst, name, hw_sign=chosen_hw_sign)
        e = train_eval[name]
        print(f"  {name:24s} median_AUROC={e['median_auroc']} median_spearman={e['median_spearman']} "
              f"(n_eval={e['n_instances_auroc_evaluable']}/{e['n_instances_total']})")

    solver_dynamics_candidates = ["risk_cdcl_recurrence", "risk_cdcl_conflicts", "risk_cdcl_decisions"]
    chosen = max(solver_dynamics_candidates,
                 key=lambda nm: (train_eval[nm]["median_auroc"] if train_eval[nm]["median_auroc"] is not None else -1))
    print(f"\n=> CHOSEN PRIMARY CDCL SOLVER-DYNAMICS PREDICTOR (train-selected): {chosen}")

    print("\n" + "=" * 70)
    print("FINAL EVALUATION (TEST SPLIT, TOUCHED ONCE)")
    print("=" * 70)
    test_eval = {}
    for name in candidate_scores:
        test_eval[name] = evaluate_predictor(test_inst, name, hw_sign=chosen_hw_sign)
        e = test_eval[name]
        pt, lo, hi = bootstrap_ci(e["aurocs"])
        pt_s, lo_s, hi_s = bootstrap_ci(e["spearmans"])
        print(f"  {name:24s} median_AUROC={pt} [{lo},{hi}]  median_spearman={pt_s} [{lo_s},{hi_s}]  "
              f"(n_eval={e['n_instances_auroc_evaluable']}/{e['n_instances_total']})")

    perm_result = permutation_test_auroc(test_inst, chosen, hw_sign=chosen_hw_sign, n_perm=1000)
    print(f"\nPermutation test for chosen predictor ({chosen}) on TEST: {perm_result}")
    perm_random = permutation_test_auroc(test_inst, "risk_random", hw_sign=chosen_hw_sign, n_perm=1000)
    print(f"Permutation test for risk_random (sanity check) on TEST: {perm_random}")

    print("\n" + "=" * 70)
    print("STRATIFIED RESULTS FOR CHOSEN PREDICTOR (TEST SPLIT)")
    print("=" * 70)
    strat_results = {}
    for key in ["regime", "n"]:
        groups = stratify_by(test_inst, key)
        strat_results[key] = {}
        for gval, ginst in groups.items():
            e = evaluate_predictor(ginst, chosen, hw_sign=chosen_hw_sign)
            strat_results[key][str(gval)] = {"median_auroc": e["median_auroc"], "n_instances": len(ginst),
                                              "n_evaluable": e["n_instances_auroc_evaluable"]}
            print(f"  {key}={gval}: median_AUROC={e['median_auroc']} (n={len(ginst)}, evaluable={e['n_instances_auroc_evaluable']})")

    # |S_I| tercile stratification
    sizes = np.array([i["S_I_size"] for i in test_inst])
    terc = np.quantile(sizes, [1/3, 2/3])
    strat_results["S_I_size_tercile"] = {}
    for lo, hi, label in [(-1, terc[0], "small"), (terc[0], terc[1], "mid"), (terc[1], 1e18, "large")]:
        subset = [i for i in test_inst if lo < i["S_I_size"] <= hi]
        e = evaluate_predictor(subset, chosen, hw_sign=chosen_hw_sign)
        strat_results["S_I_size_tercile"][label] = {"median_auroc": e["median_auroc"], "n_instances": len(subset),
                                                      "n_evaluable": e["n_instances_auroc_evaluable"]}
        print(f"  S_I_size_tercile={label}: median_AUROC={e['median_auroc']} (n={len(subset)}, evaluable={e['n_instances_auroc_evaluable']})")

    output = {
        "chosen_hw_sign": chosen_hw_sign, "chosen_primary_predictor": chosen,
        "train_evaluation": {k: {kk: vv for kk, vv in v.items() if kk != "per_instance"} for k, v in train_eval.items()},
        "test_evaluation": {k: {kk: vv for kk, vv in v.items() if kk != "per_instance"} for k, v in test_eval.items()},
        "test_evaluation_per_instance": {k: v["per_instance"] for k, v in test_eval.items()},
        "permutation_test_chosen_predictor": perm_result,
        "permutation_test_random_baseline": perm_random,
        "stratified_results_test": strat_results,
        "n_train_instances_qualifying": len(train_inst), "n_test_instances_qualifying": len(test_inst),
    }
    with open("../data/cdcl_analysis_results.json", "w") as f:
        json.dump(output, f, indent=2, default=str)
    print("\nWrote ../data/cdcl_analysis_results.json")


if __name__ == "__main__":
    main()
