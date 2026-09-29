# CROSS_PREDICTION.md — Phase 3, Part 9

All numbers from `scripts/part9_cross_prediction.py`, output `data/part9_output.txt`, raw data `data/part9_cross_prediction.json`. Test split, no retraining anywhere — `risk_basin` and `risk_cdcl_recurrence` keep their frozen Phase 2 / Phase 3 Part 6 definitions and sign conventions unchanged; only the target label (whose blind zone) changes.

## The four tests

| # | Predictor | Target | median AUROC [95% CI] | n evaluable |
|---|---|---|---|---|
| 1 | `risk_basin` (WalkSAT) | WalkSAT's own blind zone (within-solver) | **0.658 [0.636, 0.685]** | 203 |
| 2 | `risk_cdcl_recurrence` (CDCL) | CDCL's own blind zone (within-solver) | **0.667 [0.648, 0.700]** | 169 |
| 3 | `risk_basin` (WalkSAT) | **CDCL's** blind zone (cross-solver) | **0.625 [0.599, 0.667]** | 177 |
| 4 | `risk_cdcl_recurrence` (CDCL) | **WalkSAT's** blind zone (cross-solver) | **0.526 [0.487, 0.567]** | 143 |

## Within vs. cross

Average within-solver median AUROC: `0.662`. Average cross-solver median AUROC: `0.575`. Gap: `0.087` — by the task's stated thresholds, this is "within `≫` cross," pointing toward **solver-specific observational geometry** as the dominant pattern.

## The asymmetry, investigated without overclaiming

The gap is **not symmetric across the two cross-directions**, and this is worth stating plainly rather than averaging it away:

- **`risk_basin → CDCL's blind zone`: AUROC `0.625`**, CI clearly excluding `0.5` — WalkSAT's dynamics-derived score carries **real, statistically credible signal about where CDCL will fail**, only modestly weaker than WalkSAT predicting its own blind zone (`0.658`).
- **`risk_cdcl_recurrence → WalkSAT's blind zone`: AUROC `0.526`**, CI `[0.487, 0.567]` **includes `0.5`** — CDCL's dynamics-derived score carries **little to no** credible signal about where WalkSAT will fail.

**Candidate explanation (hypothesis, not established fact)**: `basin(y)` is a measure of *local-search convergence density* — how many independent random walks, started from different initial states, end up at `y`. This plausibly reflects something close to an intrinsic property of the solution-space neighborhood around `y` (how large/attractive its "basin" is in a landscape sense), which is a property of `S_I`'s geometry more than of WalkSAT's specific mechanics — consistent with it partially transferring to predict a *different* solver's failures. `recurrence(y)` (how many different *variable/clause orderings* rediscover `y` via CDCL search) is plausibly more specific to CDCL's own branching-order sensitivity — a property of how CDCL's search tree happens to be shaped by permutation, which has a less obvious connection to WalkSAT's local-search dynamics. **This is offered as a plausible mechanism, not proven here** — testing it directly (e.g. correlating `basin(y)` with an independent, solver-agnostic local-density estimate of `S_I`) is flagged as a natural next step, not attempted in this pass.

## Reading for `FINAL_GATE.md`

Per the task's own three interpretive buckets: **primarily Outcome B** (within `≫` cross on average), **with a genuine partial exception** — one cross-direction (`W→C`) is nearly as strong as within-solver prediction, suggesting the picture is not "purely solver-specific" so much as "WalkSAT's dynamics signal is more geometrically portable than CDCL's." This nuance should not be collapsed into a single clean verdict.
