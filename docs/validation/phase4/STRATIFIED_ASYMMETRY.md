# STRATIFIED_ASYMMETRY.md — Phase 4, Part 8

Raw single-feature per-instance AUROC (own risk score → cross-solver blindness, no confound adjustment), stratified as required. Full output `data/stratified_output.txt`.

## By regime, `n`, `|S_I|` tercile

Neither direction shows a stratum with a dramatically stronger or cleaner signal than the pooled result — both hover in a narrow, unremarkable `0.48`–`0.65` band across every stratum tested, with several strata (solution-rich `C→W`: `0.484`; large-`|S_I|` tercile, both directions: `0.574`/`0.486`) dipping to or below chance:

| Stratum | `W→C` median AUROC | `C→W` median AUROC |
|---|---|---|
| Overall | 0.625 | 0.526 |
| solution_rich | 0.605 | **0.484** |
| intermediate | 0.649 | 0.564 |
| near_threshold | 0.576 | 0.540 |
| n=16 | 0.605 | 0.542 |
| n=18 | 0.634 | 0.501 |
| n=20 | 0.638 | 0.533 |
| `\|S_I\|` small tercile | 0.633 | 0.546 |
| `\|S_I\|` mid tercile | 0.615 | 0.530 |
| `\|S_I\|` large tercile | 0.574 | **0.486** |

## Matched solver coverage — the decisive stratification

Restricting to instances where WalkSAT's and CDCL's coverage on that instance are within `10` percentage points of each other (`\|`coverage_W − coverage_C`\|<0.10`, `171/360` instances qualify):

| Direction | Unmatched (all instances) | **Coverage-matched** |
|---|---|---|
| `W→C` | `0.625` | **`0.556`** |
| `C→W` | `0.526` | **`0.546`** |

**The `W→C` advantage largely evaporates under coverage-matching** (`0.625→0.556`, moving substantially toward `0.5`), while `C→W` is essentially unchanged (`0.526→0.546`, both near chance). This directly corroborates `CONDITIONAL_PREDICTION.md`'s finding via an entirely different, simpler method (a matched-subgroup comparison rather than a regression model) — **the original raw asymmetry was substantially inflated by the fact that CDCL's calibrated budget gives it systematically lower coverage than WalkSAT on the same instances** (`CONFOUND_AUDIT.md`'s item-13 finding), not by a genuine dynamical difference between the two search paradigms.

## Conclusion

**The asymmetry does not survive matched-coverage restriction as a clean, robust effect.** Combined with `CONDITIONAL_PREDICTION.md` and `RESIDUALIZATION.md`, three independent analytical approaches (joint conditional model, residualize-then-test, matched-subgroup comparison) converge: **the original directional asymmetry (`0.625` vs. `0.526`) should be reported as substantially confounded, primarily by a coverage/budget-calibration mismatch between the two solvers, not as evidence of a genuine, robust, solver-specific dynamical difference.**
