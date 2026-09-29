# CONFOUND_AUDIT.md — Phase 4, Part 6

All numbers from `scripts/confound_and_conditional_analysis.py`, output `data/confound_conditional_output.txt`, raw data `data/wc_dataset.json` / `data/cw_dataset.json` (built by `scripts/build_cross_solver_dataset.py` from already-frozen Phase 2/3 revealed data — no new solver runs, no leakage concern since this is retrospective diagnostic analysis on already-revealed data, per task item 10).

## Pre-specified confounds examined (per task's 14-item list)

Univariate Spearman correlations, both with the own-solver risk score and with the cross-solver blindness target, for `y∈A_W(I)` (`W→C` direction) and `y∈A_C(I)` (`C→W` direction):

| Confound | corr(confound, own risk) `W→C` | corr(confound, label) `W→C` | corr(confound, own risk) `C→W` | corr(confound, label) `C→W` |
|---|---|---|---|---|
| Hamming weight | `−0.006` | `0.005` | `−0.005` | `0.008` |
| Local `S_I` density (post-reveal, diagnostic only) | `0.010` | `0.075` | `−0.107` | `0.171` |
| **Distance to other solver's observed set** | `−0.404` | **`0.493`** | `−0.377` | **`0.573`** |
| **`\|S_I\|`** | `−0.605` | **`0.501`** | `−0.598` | **`0.690`** |
| `n` | `−0.098` | `0.059` | `−0.063` | `0.079` |
| **Own coverage** | `0.599` | **`−0.495`** | `0.580` | **`−0.686`** |
| **Other solver's coverage** | `0.603` | **`−0.500`** | `0.580` | **`−0.701`** |
| **`ε̂` (own)** | `−0.576` | **`0.488`** | `−0.523` | **`0.637`** |

**Hamming weight is essentially uncorrelated with everything** (`|ρ|<0.01`) — confirms this specific confound (the one that made the January paper's biased-sampler result circular, `phase1/ORIGINAL_EXPERIMENT_AUDIT.md`) is not driving anything here, in either solver. **Distance to the other solver's set, `|S_I|`, coverage (both solvers'), and `ε̂` are all strongly correlated with the blindness label** (`|ρ|` up to `0.70`) — these are the real candidate confounds.

## Two mechanical findings, reported explicitly (items 12–13 of the task's list)

- **Item 12 (compressed variance/granularity)**: `recurrence` (CDCL) has only **5 distinct values** (`1`–`5`, from `R=5` runs); `basin` (WalkSAT) has **93 distinct values** (`1`–`150`, from `K=150` restarts). A score with `5` possible values has structurally less ranking resolution than one with `93` — a genuine, previously-unexamined mechanical asymmetry between the two predictors, independent of any "dynamics" interpretation, and a plausible partial explanation for why `C→W` cross-prediction is weaker than `W→C`.
- **Item 13 (class imbalance / coverage mismatch)**: the `W→C` target (does a WalkSAT-found point have a CDCL-missed neighbor?) has base rate **`88.0%`**; the `C→W` target has base rate **`69.2%`**. This directly reflects that CDCL's calibrated budget (`CDCL_ACCESSIBILITY.md`) gives it **lower mean coverage than WalkSAT on the same instances** (`coverage_W≈0.40` vs. `coverage_C≈0.23`, row-weighted) — CDCL's blind zone is mechanically larger, making "does `y` have *some* CDCL-missed neighbor" an easier-to-satisfy (higher base rate) question almost by construction.

## Item 11 (is WalkSAT risk just a better proxy for "rare solution" status?)

Addressed directly and separately in `RARE_SOLUTION_TEST.md` (Part 10) — flagged here as the single most important remaining question after the mechanical findings above, since `dist_to_other_solver_set` and `|S_I|`/coverage/`ε̂` are exactly the kind of generic "rarity/density" signals that hypothesis predicts should dominate.

## Verdict feeding into `CONDITIONAL_PREDICTION.md`

The confounds are not merely present — several are **strongly** correlated with the target (up to `ρ=0.70`), far exceeding the raw own-risk-score-to-target correlation implicit in the `0.625`/`0.526` AUROCs. This motivates the conditional model in `CONDITIONAL_PREDICTION.md` as the decisive test, rather than treating the univariate pattern alone as conclusive (per instruction: "do not indiscriminately regress on everything and declare residual significance" — the conditional model is the single, pre-specified, decisive test; this document is diagnostic groundwork for it, not itself the verdict).
