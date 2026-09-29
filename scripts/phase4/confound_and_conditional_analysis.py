"""
Phase 4, Parts 6-7: confound audit + conditional predictive test.

For each direction (wc: WalkSAT-risk -> CDCL-blindness; cw: CDCL-risk ->
WalkSAT-blindness):
  1. Univariate Spearman correlations: own-risk-score vs each candidate
     confound, and label_target vs each candidate confound (Part 6).
  2. Two pre-specified logistic models, evaluated via 5-fold GROUP
     cross-validation (grouped by instance id, so no instance's solutions
     appear in both train and eval within a fold -- avoids trivial
     same-row overfitting without requiring a fresh prospective freeze,
     appropriate for this retrospective diagnostic analysis):
       Model A (baseline / confounds only): hamming_weight, local_S_I_density,
         dist_to_other_solver_set, S_I_size (log), n, coverage_own,
         coverage_other, eps_hat_own, regime (one-hot)
       Model B (baseline + own risk score)
     Evaluated by out-of-fold per-instance AUROC (median + instance-level
     bootstrap CI), comparing Model B vs Model A ("conditional discrimination
     improvement") -- this is the Part 7 conditional predictive test.
"""
import json
import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

RNG = np.random.default_rng(20260928 + 10101)


def load(name):
    with open(f"../data/{name}.json") as f:
        return json.load(f)


def build_feature_matrix(rows, risk_col, own_cov_col, other_cov_col, own_eps_col):
    regimes = sorted(set(r["regime"] for r in rows))
    X_base = []
    X_full = []
    y = []
    groups = []
    for r in rows:
        regime_onehot = [1.0 if r["regime"] == reg else 0.0 for reg in regimes[1:]]  # drop first as reference
        base_feats = [
            r["hamming_weight"], r["local_S_I_density"],
            r["dist_to_other_solver_set"] if r["dist_to_other_solver_set"] is not None else -1,
            np.log1p(r["S_I_size"]), r["n"],
            r[own_cov_col], r[other_cov_col], r[own_eps_col],
        ] + regime_onehot
        X_base.append(base_feats)
        X_full.append(base_feats + [r[risk_col]])
        y.append(r["label_target"])
        groups.append(r["id"])
    return np.array(X_base), np.array(X_full), np.array(y), np.array(groups)


def cv_auroc(X, y, groups, n_splits=5):
    """Returns per-instance out-of-fold AUROC list (only instances with both classes present)."""
    gkf = GroupKFold(n_splits=n_splits)
    oof_scores = np.zeros(len(y))
    for train_idx, test_idx in gkf.split(X, y, groups):
        scaler = StandardScaler().fit(X[train_idx])
        Xtr = scaler.transform(X[train_idx])
        Xte = scaler.transform(X[test_idx])
        clf = LogisticRegression(max_iter=2000, C=1.0)
        clf.fit(Xtr, y[train_idx])
        oof_scores[test_idx] = clf.predict_proba(Xte)[:, 1]

    per_instance = {}
    for i, g in enumerate(groups):
        per_instance.setdefault(g, {"scores": [], "labels": []})
        per_instance[g]["scores"].append(oof_scores[i])
        per_instance[g]["labels"].append(y[i])

    aurocs = []
    for g, d in per_instance.items():
        labels = np.array(d["labels"])
        if len(set(labels.tolist())) < 2:
            continue
        aurocs.append(roc_auc_score(labels, d["scores"]))
    return aurocs, oof_scores


def bootstrap_ci(values, n_boot=3000):
    if not values:
        return None, None, None
    values = np.array(values)
    point = float(np.median(values))
    boots = [np.median(RNG.choice(values, size=len(values), replace=True)) for _ in range(n_boot)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return point, float(lo), float(hi)


def analyze_direction(name, rows, risk_col, own_cov_col, other_cov_col, own_eps_col):
    print(f"\n{'='*70}\nDIRECTION: {name}\n{'='*70}")

    # Part 6: univariate confound correlations
    risk = np.array([r[risk_col] for r in rows], dtype=float)
    label = np.array([r["label_target"] for r in rows], dtype=float)
    print("\n--- Part 6: univariate Spearman correlations ---")
    print(f"{'confound':30s} {'corr(confound, own_risk)':>26s} {'corr(confound, label_target)':>30s}")
    confounds = {
        "hamming_weight": [r["hamming_weight"] for r in rows],
        "local_S_I_density": [r["local_S_I_density"] for r in rows],
        "dist_to_other_solver_set": [r["dist_to_other_solver_set"] if r["dist_to_other_solver_set"] is not None else np.nan for r in rows],
        "S_I_size": [r["S_I_size"] for r in rows],
        "n": [r["n"] for r in rows],
        "coverage_own": [r[own_cov_col] for r in rows],
        "coverage_other": [r[other_cov_col] for r in rows],
        "eps_hat_own": [r[own_eps_col] for r in rows],
    }
    for cname, cvals in confounds.items():
        cvals = np.array(cvals, dtype=float)
        mask = ~np.isnan(cvals)
        r1, _ = spearmanr(cvals[mask], risk[mask])
        r2, _ = spearmanr(cvals[mask], label[mask])
        print(f"{cname:30s} {r1:26.4f} {r2:30.4f}")

    # granularity / class balance already reported separately; base rate here:
    print(f"\nBase rate of label_target: {label.mean():.4f}")
    print(f"Own risk score distinct values: {len(set(risk.tolist()))}, range [{risk.min()},{risk.max()}]")

    # Part 7: conditional models via group CV
    print("\n--- Part 7: conditional predictive test (5-fold group CV by instance) ---")
    X_base, X_full, y, groups = build_feature_matrix(rows, risk_col, own_cov_col, other_cov_col, own_eps_col)

    auroc_base, _ = cv_auroc(X_base, y, groups)
    auroc_full, _ = cv_auroc(X_full, y, groups)

    pt_b, lo_b, hi_b = bootstrap_ci(auroc_base)
    pt_f, lo_f, hi_f = bootstrap_ci(auroc_full)
    print(f"Model A (confounds only):        median AUROC = {pt_b} [{lo_b},{hi_b}]  (n_instances={len(auroc_base)})")
    print(f"Model B (confounds + own risk):  median AUROC = {pt_f} [{lo_f},{hi_f}]  (n_instances={len(auroc_full)})")

    diffs = []
    common_g = set(g for g in groups)
    # paired per-instance difference where possible (recompute per-instance separately for A and B on same folds)
    # (approx: use the two auroc lists as paired only if same instance-set; for simplicity report unpaired distributions
    # and also a direct paired bootstrap on the oof score arrays)
    _, oof_base = cv_auroc(X_base, y, groups)
    _, oof_full = cv_auroc(X_full, y, groups)
    # paired instance-level AUROC diff
    per_inst_base = {}
    per_inst_full = {}
    for i, g in enumerate(groups):
        per_inst_base.setdefault(g, {"s": [], "l": []})
        per_inst_base[g]["s"].append(oof_base[i]); per_inst_base[g]["l"].append(y[i])
        per_inst_full.setdefault(g, {"s": [], "l": []})
        per_inst_full[g]["s"].append(oof_full[i]); per_inst_full[g]["l"].append(y[i])
    paired_diffs = []
    for g in per_inst_base:
        lb = np.array(per_inst_base[g]["l"])
        if len(set(lb.tolist())) < 2:
            continue
        ab = roc_auc_score(lb, per_inst_base[g]["s"])
        af = roc_auc_score(lb, per_inst_full[g]["s"])
        paired_diffs.append(af - ab)
    pt_d, lo_d, hi_d = bootstrap_ci(paired_diffs)
    print(f"Paired per-instance improvement (B - A): median = {pt_d} [{lo_d},{hi_d}]  (n={len(paired_diffs)})")

    return {
        "direction": name, "base_rate": float(label.mean()),
        "n_risk_distinct_values": len(set(risk.tolist())),
        "model_A_auroc": {"median": pt_b, "lo": lo_b, "hi": hi_b, "n": len(auroc_base)},
        "model_B_auroc": {"median": pt_f, "lo": lo_f, "hi": hi_f, "n": len(auroc_full)},
        "paired_improvement": {"median": pt_d, "lo": lo_d, "hi": hi_d, "n": len(paired_diffs)},
    }


def main():
    wc = load("wc_dataset")
    cw = load("cw_dataset")

    res_wc = analyze_direction("W -> C  (risk_basin predicting CDCL blindness)", wc,
                                 "basin", "coverage_W", "coverage_C", "eps_hat_W")
    res_cw = analyze_direction("C -> W  (risk_cdcl_recurrence predicting WalkSAT blindness)", cw,
                                 "recurrence", "coverage_C", "coverage_W", "eps_hat_C")

    with open("../data/confound_conditional_results.json", "w") as f:
        json.dump({"wc": res_wc, "cw": res_cw}, f, indent=2)
    print("\nWrote ../data/confound_conditional_results.json")


if __name__ == "__main__":
    main()
