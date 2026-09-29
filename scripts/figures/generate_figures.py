"""
Generates all manuscript figures from FROZEN Phase 1-4 data only (read-only
access to ~/scratch/sat-algorithmic-resolution-v2-audit-2026-09-28/). No new
solver runs, no new statistical tests -- every number plotted here already
exists in a frozen phase2/3/4 data file, cited in each figure's caption.
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AUDIT_ROOT = "/Users/eliasdejesus/scratch/sat-algorithmic-resolution-v2-audit-2026-09-28"
OUT = "/Users/eliasdejesus/scratch/sat-algorithmic-resolution-v2-manuscript-2026-09-29/figures"

plt.rcParams.update({
    "font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 150,
})

def hamming(a, b):
    return sum(x != y for x, y in zip(a, b))


# ---------------- Figure 1: conceptual schematic (real instance, MDS projection) ----------------
def fig1_schematic():
    with open(f"{AUDIT_ROOT}/phase3/data/cdcl_stage_b_results_test.json") as f:
        recs = json.load(f)
    rec = next(r for r in recs if r["id"] == 619)  # the pre-specified paired trajectory instance
    S_I = [tuple(x) for x in rec["S_I"]]
    M_W = set(tuple(x) for x in rec["M_W"])
    M_C = set(tuple(x) for x in rec["M_C"])
    A_W = [x for x in S_I if x not in M_W]
    A_C = [x for x in S_I if x not in M_C]

    from sklearn.manifold import MDS
    S_arr = np.array(S_I, dtype=float)
    D = np.zeros((len(S_I), len(S_I)))
    for i in range(len(S_I)):
        for j in range(len(S_I)):
            D[i, j] = hamming(S_I[i], S_I[j])
    mds = MDS(n_components=2, dissimilarity="precomputed", random_state=0, normalized_stress=False)
    coords = mds.fit_transform(D)
    coord_of = {S_I[i]: coords[i] for i in range(len(S_I))}

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.3))
    titles = ["True solution space $S_I$", "WalkSAT observation $A_W(I)$", "CDCL observation $A_C(I)$"]
    found_sets = [set(S_I), set(A_W), set(A_C)]
    for ax, title, found in zip(axes, titles, found_sets):
        xs_found = [coord_of[p][0] for p in S_I if p in found]
        ys_found = [coord_of[p][1] for p in S_I if p in found]
        xs_miss = [coord_of[p][0] for p in S_I if p not in found]
        ys_miss = [coord_of[p][1] for p in S_I if p not in found]
        ax.scatter(xs_miss, ys_miss, s=14, c="lightgray", label="not observed", zorder=1)
        ax.scatter(xs_found, ys_found, s=18, c="#1f77b4", label="observed", zorder=2)
        ax.set_title(title, fontsize=11)
        ax.set_xticks([]); ax.set_yticks([])
    axes[0].legend(loc="upper right", fontsize=8, frameon=False)
    fig.suptitle(f"Instance 619 ($n=20$, $\\alpha=3.5$, $|S_I|={len(S_I)}$) — 2D MDS projection of Hamming distances,\n"
                 f"$|A_W|={len(A_W)}$ ({len(A_W)/len(S_I)*100:.0f}% coverage), "
                 f"$|A_C|={len(A_C)}$ ({len(A_C)/len(S_I)*100:.0f}% coverage)", fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.88])
    fig.savefig(f"{OUT}/figure1_schematic.png", bbox_inches="tight")
    print("Figure 1 written.")


# ---------------- Figure 2: coverage vs resolution (does not determine) ----------------
def fig2_coverage_vs_resolution():
    with open(f"{AUDIT_ROOT}/phase3/data/cdcl_stage_b_results_test.json") as f:
        recs = json.load(f)
    cov_w = [r["coverage_W"] for r in recs if r["eps_hat_W"] is not None]
    eps_w = [r["eps_hat_W"] for r in recs if r["eps_hat_W"] is not None]
    cov_c = [r["coverage_C"] for r in recs if r["eps_hat_C"] is not None]
    eps_c = [r["eps_hat_C"] for r in recs if r["eps_hat_C"] is not None]

    fig, ax = plt.subplots(figsize=(6.2, 5))
    ax.scatter(cov_w, eps_w, s=12, alpha=0.5, c="#1f77b4", label="WalkSAT ($n=360$)")
    ax.scatter(cov_c, eps_c, s=12, alpha=0.5, c="#d62728", label="CDCL ($n=360$)")
    ax.set_xlabel("Coverage $|A(I)|/|S_I|$")
    ax.set_ylabel(r"$\hat\varepsilon(A,I)$ (Hausdorff resolution)")
    ax.set_title("Coverage does not determine geometric resolution")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(f"{OUT}/figure2_coverage_vs_resolution.png", bbox_inches="tight")
    print("Figure 2 written.")


# ---------------- Figure 3: blind-zone prediction AUROC with baselines ----------------
def fig3_auroc_baselines():
    walksat = {
        "risk_basin": (0.658, 0.636, 0.685),
        "Hamming-weight": (0.519, 0.490, 0.543),
        "found-neighbor": (0.279, 0.241, 0.298),
        "disc_flips": (0.407, 0.388, 0.426),
        "random": (0.504, 0.487, 0.519),
    }
    cdcl = {
        "risk_cdcl_recurrence": (0.667, 0.647, 0.700),
        "Hamming-weight": (0.492, 0.453, 0.539),
        "found-neighbor": (0.467, 0.409, 0.497),
        "conflicts_to_discovery": (0.471, 0.444, 0.490),
        "random": (0.481, 0.449, 0.514),
    }
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3), sharey=True)
    for ax, data, title in [(axes[0], walksat, "WalkSAT"), (axes[1], cdcl, "CDCL / Glucose3")]:
        names = list(data.keys())
        medians = [data[n][0] for n in names]
        los = [data[n][0] - data[n][1] for n in names]
        his = [data[n][2] - data[n][0] for n in names]
        colors = ["#1f77b4"] + ["gray"] * (len(names) - 1)
        y_pos = np.arange(len(names))
        ax.barh(y_pos, medians, xerr=[los, his], color=colors, capsize=3)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(names, fontsize=9)
        ax.axvline(0.5, color="black", linewidth=0.8, linestyle="--")
        ax.set_xlabel("Test median AUROC [95% CI]")
        ax.set_title(f"{title} held-out blind-zone prediction")
        ax.set_xlim(0, 1)
    fig.tight_layout()
    fig.savefig(f"{OUT}/figure3_auroc_baselines.png", bbox_inches="tight")
    print("Figure 3 written.")


# ---------------- Figure 4: matched-coverage fragmentation (MAIN empirical figure) ----------------
def fig4_fragmentation():
    with open(f"{AUDIT_ROOT}/phase4/data/fragmentation_replication.json") as f:
        rows = json.load(f)
    # Clip negative excess (under-representation, a distinct phenomenon per
    # FRAGMENTATION_THEOREM.md's r<eps regime -- 25/349 CDCL instances show
    # this) to 0 for this "excess FRAGMENTATION" plot; noted in the caption.
    excess_w = np.clip(np.array([r["excess_W"] for r in rows]), 0, None)
    excess_c = np.clip(np.array([r["excess_C"] for r in rows]), 0, None)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))

    ax = axes[0]
    jitter = np.random.default_rng(0).normal(0, 0.06, size=len(excess_w))
    ax.scatter(np.zeros(len(excess_w)) + jitter, np.log1p(excess_w), s=10, alpha=0.4, c="#1f77b4")
    ax.scatter(np.ones(len(excess_c)) + jitter, np.log1p(excess_c), s=10, alpha=0.4, c="#d62728")
    ax.boxplot([np.log1p(excess_w), np.log1p(excess_c)], positions=[0, 1], widths=0.4,
               showfliers=False, patch_artist=True,
               boxprops=dict(facecolor="none"), medianprops=dict(color="black"))
    ax.set_xticks([0, 1]); ax.set_xticklabels(["WalkSAT", "CDCL"])
    ax.set_ylabel(r"$\log(1 + \mathrm{excess\ components\ at\ } r=1)$")
    ax.set_title("Excess fragmentation, paired\n(349 held-out instances; negative values\n[under-representation, 25/349 for CDCL] clipped to 0)")

    ax = axes[1]
    matched = [r for r in rows if abs(r["coverage_W"] - r["coverage_C"]) < 0.10]
    ewm = [max(r["excess_W"], 0) for r in matched]
    ecm = [max(r["excess_C"], 0) for r in matched]
    ax.scatter(np.log1p(ecm), np.log1p(ewm), s=14, alpha=0.5, c="#2ca02c")
    lims = [0, max(max(np.log1p(ewm)), max(np.log1p(ecm))) * 1.05]
    ax.plot(lims, lims, color="gray", linestyle="--", linewidth=1, label="equal fragmentation")
    ax.set_xlabel(r"$\log(1+\mathrm{excess}_C)$")
    ax.set_ylabel(r"$\log(1+\mathrm{excess}_W)$")
    ax.set_title(f"Coverage-matched instances ($n={len(matched)}$)\nmedian ratio 11.6$\\times$ (95% CI [9.6,13.3])")
    ax.legend(frameon=False, fontsize=8)

    fig.tight_layout()
    fig.savefig(f"{OUT}/figure4_fragmentation_matched_coverage.png", bbox_inches="tight")
    print("Figure 4 written.")


# ---------------- Figure 5: epsilon reversal ----------------
def fig5_epsilon_reversal():
    with open(f"{AUDIT_ROOT}/phase3/data/cdcl_stage_b_results_test.json") as f:
        recs = json.load(f)
    with open(f"{AUDIT_ROOT}/phase4/data/fragmentation_replication.json") as f:
        frag_ids = set(r["id"] for r in json.load(f))
    rows = [r for r in recs if r["id"] in frag_ids and r["eps_hat_W"] is not None and r["eps_hat_C"] is not None]
    eps_w = np.array([r["eps_hat_W"] for r in rows])
    eps_c = np.array([r["eps_hat_C"] for r in rows])

    fig, ax = plt.subplots(figsize=(5.8, 5))
    ax.scatter(eps_c, eps_w, s=12, alpha=0.4, c="#9467bd")
    lims = [0, max(eps_w.max(), eps_c.max()) * 1.05]
    ax.plot(lims, lims, color="gray", linestyle="--", linewidth=1, label="equal $\\hat\\varepsilon$")
    ax.set_xlabel(r"$\hat\varepsilon_C$ (CDCL)")
    ax.set_ylabel(r"$\hat\varepsilon_W$ (WalkSAT)")
    ax.set_title(f"Paired $\\hat\\varepsilon$ comparison ($n={len(rows)}$)\n"
                 f"mean $\\hat\\varepsilon_W$=1.41 vs $\\hat\\varepsilon_C$=3.52, $p=5.1\\times10^{{-38}}$")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{OUT}/figure5_epsilon_reversal.png", bbox_inches="tight")
    print("Figure 5 written.")


# ---------------- Figure 6: regime dependence ----------------
def fig6_regime_dependence():
    with open(f"{AUDIT_ROOT}/phase4/data/fragmentation_replication.json") as f:
        rows = json.load(f)
    regimes = ["solution_rich", "intermediate", "near_threshold"]
    mean_w = [np.mean([r["excess_W"] for r in rows if r["regime"] == reg]) for reg in regimes]
    mean_c = [np.mean([r["excess_C"] for r in rows if r["regime"] == reg]) for reg in regimes]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    x = np.arange(len(regimes))
    width = 0.35
    ax.bar(x - width/2, mean_w, width, label="WalkSAT", color="#1f77b4")
    ax.bar(x + width/2, mean_c, width, label="CDCL", color="#d62728")
    ax.set_xticks(x)
    ax.set_xticklabels(["Solution-rich\n($\\alpha$=2.5)", "Intermediate\n($\\alpha$=3.5)", "Near-threshold\n($\\alpha$=4.2)"])
    ax.set_ylabel("Mean excess fragmentation (components)")
    ax.set_yscale("symlog")
    ax.set_title("Fragmentation gap by SAT regime")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(f"{OUT}/figure6_regime_dependence.png", bbox_inches="tight")
    print("Figure 6 written.")


# ---------------- Figure 7 (optional): budget trajectory, instance 619, both solvers ----------------
def fig7_budget_trajectory():
    with open(f"{AUDIT_ROOT}/phase2/data/part11_budget_trajectory.json") as f:
        walksat_traj = json.load(f)
    with open(f"{AUDIT_ROOT}/phase3/data/part11_cdcl_budget_trajectory.json") as f:
        cdcl_traj = json.load(f)
    w = next(t for t in walksat_traj if t["id"] == 619)
    c = next(t for t in cdcl_traj if t["id"] == 619)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
    ax = axes[0]
    ax.plot([r["coverage"]*100 for r in w["trajectory"]], [r["eps_hat"] for r in w["trajectory"]],
            "o-", color="#1f77b4", label="WalkSAT")
    ax.plot([r["coverage"]*100 for r in c["trajectory"]], [r["eps_hat"] for r in c["trajectory"]],
            "s-", color="#d62728", label="CDCL")
    ax.set_xlabel("Coverage (%)"); ax.set_ylabel(r"$\hat\varepsilon(T)$")
    ax.set_title("Resolution vs. budget (instance 619)")
    ax.legend(frameon=False)

    ax = axes[1]
    ax.plot([r["coverage"]*100 for r in w["trajectory"]], [r["C_A_r"] for r in w["trajectory"]],
            "o-", color="#1f77b4", label="WalkSAT")
    ax.plot([r["coverage"]*100 for r in c["trajectory"]], [r["C_A_r"] for r in c["trajectory"]],
            "s-", color="#d62728", label="CDCL")
    ax.axhline(w["C_S_r_fixed"], color="gray", linestyle="--", linewidth=1, label=f"true $C_S(1)$={w['C_S_r_fixed']}")
    ax.set_xlabel("Coverage (%)"); ax.set_ylabel(r"$C_A(r{=}1)$ (apparent components)")
    ax.set_title("Fragmentation vs. budget (instance 619)")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(f"{OUT}/figure7_budget_trajectory.png", bbox_inches="tight")
    print("Figure 7 written.")


if __name__ == "__main__":
    fig1_schematic()
    fig2_coverage_vs_resolution()
    fig3_auroc_baselines()
    fig4_fragmentation()
    fig5_epsilon_reversal()
    fig6_regime_dependence()
    fig7_budget_trajectory()
    print("\nAll figures written to", OUT)
