# CONDITIONAL_PREDICTION.md — Phase 4, Part 7

Two pre-specified logistic models (chosen before seeing results, not iterated post-hoc), evaluated via **5-fold group cross-validation by instance** (no instance's solutions split across train/eval within a fold — the appropriate discipline for this retrospective diagnostic analysis, per instance-as-independent-unit throughout this project), out-of-fold per-instance AUROC, instance-level bootstrap CI (`3,000` resamples).

- **Model A (confounds only)**: Hamming weight, local `S_I` density, distance to the other solver's set, `\log(1+|S_I|)`, `n`, own coverage, other solver's coverage, own `ε̂`, regime (one-hot).
- **Model B (Model A + own risk score)**: adds `basin` (for `W→C`) or `recurrence` (for `C→W`).

## Results

| Direction | Model A (confounds only) | Model B (+ own risk) | Paired per-instance improvement (B−A) |
|---|---|---|---|
| `W→C` | median AUROC **0.946** `[0.933, 0.956]` | median AUROC **0.943** `[0.934, 0.953]` | median **`0.000`** `[0.000, ~0.000]` |
| `C→W` | median AUROC **0.875** `[0.855, 0.890]` | median AUROC **0.875** `[0.855, 0.888]` | median **`0.000`** `[0.000, 0.000]` |

**Confounds alone dramatically outperform the raw single-feature AUROC** (`0.625`/`0.526`) — `0.946`/`0.875` vs. `0.625`/`0.526` — and **adding the solver-specific risk score improves discrimination by essentially zero, with a bootstrap CI tightly centered on zero, in both directions.**

## Robustness check: is this driven entirely by the one near-tautological confound?

`dist_to_other_solver_set(y)` — the Hamming distance from `y` to the nearest point the *other* solver found — is close to definitionally related to the target (if `y` is far from everything the other solver found, a missed neighbor of `y` is almost guaranteed if `S_I` is reasonably dense nearby). Re-running **without this one feature**:

| Direction | Model A minus `dist_to_other_solver_set` | Model B (same, + own risk) |
|---|---|---|
| `W→C` | median AUROC **0.756** `[0.709, 0.791]` | median AUROC **0.756** `[0.739, 0.781]` |
| `C→W` | median AUROC **0.804** `[0.761, 0.837]` | median AUROC **0.813** `[0.764, 0.836]` |

**Even excluding the strongest, most tautology-adjacent confound, the remaining generic confounds (local density, `|S_I|`, coverage, `ε̂`, regime, `n`) still dominate** (`0.756`/`0.804`, still far above `0.625`/`0.526`), and adding the own risk score **still adds nothing beyond noise** (CIs fully overlapping in both directions).

## Conclusion for this part

**The conditional predictive test does not support the hypothesis that the solver-specific risk score carries information beyond generic, solver-agnostic geometric confounds.** This holds under two independent model specifications (with and without the strongest single confound). The raw cross-prediction asymmetry (`0.625` vs. `0.526`) is real as a *marginal* correlation, but **is fully subsumed by simple geometric features that have nothing to do with search dynamics** — see `RESIDUALIZATION.md` for an independent confirmation via a different method, and `RARE_SOLUTION_TEST.md` for the positive alternative hypothesis this result is most consistent with.
