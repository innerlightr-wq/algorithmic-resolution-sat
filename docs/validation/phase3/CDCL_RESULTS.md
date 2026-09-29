# CDCL_RESULTS.md — Phase 3, Part 6 real results

All numbers from actual runs (`scripts/analyze_cdcl_results.py`, output in `data/analyze_cdcl_results_output.txt`, full JSON in `data/cdcl_analysis_results.json`).

## Model selection (train split only)

| Predictor | Train median AUROC | Train median Spearman |
|---|---|---|
| **`risk_cdcl_recurrence`** | **0.677** | **0.291** |
| `risk_cdcl_decisions` | 0.644 | 0.310 |
| `risk_cdcl_conflicts` | 0.481 | −0.025 |
| `risk_foundneighbor` | (not primary candidate) | — |
| `risk_hamming_weight` (sign `−1` chosen) | 0.482 | 0.015 |
| `risk_random` | 0.508 | 0.002 |

`risk_cdcl_recurrence` selected as primary (highest train AUROC among the three genuine solver-dynamics candidates). **Note**: `risk_cdcl_conflicts` performed near-random on train (`0.481`) — the "harder discovery ⟹ higher risk" hypothesis did not pan out for CDCL, structurally similar to Phase 2's `risk_disc_flips` finding for WalkSAT (`PHASE2_FREEZE.md`) — reported honestly, not rescued.

## Final held-out test evaluation — touched once

| Predictor | Test median AUROC [95% CI] | Test median Spearman [95% CI] |
|---|---|---|
| **`risk_cdcl_recurrence`** | **0.667 [0.647, 0.700]** | **0.346 [0.311, 0.376]** |
| `risk_cdcl_decisions` | 0.632 [0.583, 0.660] | 0.275 [0.236, 0.312] |
| `risk_cdcl_conflicts` | 0.471 [0.444, 0.490] | −0.043 [−0.067, −0.008] |
| `risk_foundneighbor` | 0.467 [0.409, 0.497] | −0.047 [−0.114, 0.012] |
| `risk_hamming_weight` | 0.492 [0.453, 0.539] | −0.011 [−0.063, 0.079] |
| `risk_random` | 0.481 [0.449, 0.514] | −0.001 [−0.036, 0.023] |

(`n=319/360` test instances qualify; `169/319` evaluable for `risk_cdcl_recurrence` AUROC after binary-label degeneracy filtering.)

**Directly comparable to Phase 2's WalkSAT result** (`risk_basin`: test median AUROC `0.658 [0.636,0.685]`): CDCL's `risk_cdcl_recurrence` is at least as strong, slightly higher point estimate (`0.667` vs `0.658`), overlapping CIs — **both solvers show a genuine, comparable-magnitude held-out predictable-blind-zone effect.**

## Permutation test (1,000 permutations, instance-level)

| Predictor | True median AUROC | Null mean | p-value |
|---|---|---|---|
| `risk_cdcl_recurrence` (chosen) | 0.667 | 0.486 | **0.000999** |
| `risk_random` (sanity check) | 0.481 | 0.500 | 0.934 (correctly non-significant) |

## Stratification (test split, `risk_cdcl_recurrence`)

| Stratum | median AUROC | n (evaluable) |
|---|---|---|
| solution_rich | 0.615 | 120 (56) |
| intermediate | 0.671 | 112 (86) |
| near_threshold | 0.761 | 87 (27 — small sample) |
| n=16 | 0.652 | 94 (56) |
| n=18 | 0.668 | 112 (59) |
| n=20 | 0.692 | 113 (54) |
| `\|S_I\|` small tercile | 0.785 | 114 (32) |
| `\|S_I\|` mid tercile | 0.663 | 99 (94) |
| `\|S_I\|` large tercile | 0.615 | 106 (43) |

**Effect survives every stratum tested** — same qualitative pattern as Phase 2's WalkSAT result (strongest near threshold and for small `\|S_I\|`, weakest but still `>0.5` for large solution-rich instances). No collapse, no sign reversal.

## Answer to Question A (part 1): does CDCL replicate the WalkSAT phenomenon?

**Yes, unambiguously.** A structurally different solver paradigm (CDCL via Glucose3, with search-order/phase-based randomization rather than restart-based randomization) exhibits a genuinely analogous, comparably strong (`0.667` vs `0.658`), held-out, non-circular, baseline-beating, permutation-significant blind-zone-predictability effect. This is the single most important confirmatory result of Phase 3 — it upgrades Phase 2's "WalkSAT-specific" finding to a *cross-paradigm* phenomenon (pending the caveats in `CROSS_PREDICTION.md` about whether the underlying *mechanism* is shared or merely analogous).
