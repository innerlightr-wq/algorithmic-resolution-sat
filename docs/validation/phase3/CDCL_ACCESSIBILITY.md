# CDCL_ACCESSIBILITY.md — Phase 3, Part 3

## Why `risk_basin` cannot be transplanted directly

WalkSAT's `basin(y)` counts how many of `K` independent *local-search restarts* converge to `y`. CDCL under blocking-clause enumeration has no restart-to-single-solution mapping: one `solve()` call after a permutation/phase seed enumerates *many* distinct solutions in sequence (via blocking clauses) until a budget or UNSAT is hit — there is no "did this restart find `y`" event, only "was `y` among the solutions this particular search-order run happened to enumerate." The CDCL-native analogue is therefore built around **independent search orderings**, not independent restarts.

## Pilot budget calibration (why R=5, T=8)

A first pilot at `R=20` independent-permutation runs × `T=50` solutions/run gave CDCL coverage of **85–100%** on most cells vs. WalkSAT's 20–77% on the same instances (`data/budget_pilot_output.txt`) — CDCL's blocking-clause enumeration is dramatically more sample-efficient per attempt than WalkSAT's restart-based local search (expected: CDCL never "wastes" an attempt failing to find any solution, unlike a WalkSAT restart that can time out with nothing). At that budget, CDCL's blind zone `M_C(I)` would be near-empty for most instances, making a blind-zone comparison uninformative. A second pilot swept `(R,T)∈\{(5,8),(3,5),(4,6)\}` (`data/budget_pilot_output.txt`); **`R=5, T=8`** (40 total solution-discovery attempts) was selected as the primary budget — it gives CDCL coverage broadly comparable in order of magnitude to WalkSAT's on the same instances (e.g. solution-rich: CDCL 7–21% vs. WalkSAT 21–50%; intermediate: CDCL 37–100% vs. WalkSAT 77–100%) while remaining a genuine, non-degenerate blind zone for most cells. **This choice was made by examining aggregate coverage statistics only, before any accessibility-prediction result was computed** — it calibrates the experimental *design*, not the *outcome*, and is documented here rather than tuned post-hoc.

`A_C(I) := ⋃_{run=1}^{5} (\text{first 8 solutions enumerated by that permuted run})`.

A secondary "attempts-matched" budget (`R=1, T=150`, matching WalkSAT's 150 attempts numerically) is also run for the Part 4/10 budget-normalization comparison — see `BUDGET_TRAJECTORIES.md`; it produces near-total coverage on most cells, itself a reportable finding about paradigm-level sample efficiency, not a design flaw.

## CDCL-native prospective predictors, `y∈A_C(I)`

Computed **only** from the `R×T` enumeration runs' internal trajectory (CNF, permutation/phase seeds, and PySAT's `accum_stats()` cumulative `{restarts,conflicts,decisions,propagations}` counters, read and differenced after every individual `solve()`/blocking step) — never from `S_I`:

- **`recurrence(y)`** = number of the `R=5` independent runs in which `y` was among the enumerated solutions. Direct structural analogue of `basin(y)`: both count "how many independent search processes converged on/passed through `y`." `risk_cdcl_recurrence(y) = -recurrence(y)` (low recurrence ⟹ hypothesized high risk, same direction convention as `risk_basin`).
- **`conflicts_to_discovery(y)`** = mean, over runs that found `y`, of `accum_stats()['conflicts']` **incremental since the previous solution in that run** (i.e. conflicts spent between the previous blocking clause and discovering `y`) — the CDCL-native analogue of `disc_flips(y)`. `risk_cdcl_conflicts(y) = +conflicts_to_discovery(y)` (hypothesized: harder-to-reach ⟹ higher risk, mirroring the `disc_flips` hypothesis direction from Phase 2, which — as a reminder from `PHASE2_FREEZE.md` — empirically went the *opposite* direction for WalkSAT; tested fresh here, not assumed).
- **`decisions_to_discovery(y)`**: same construction using the `decisions` counter instead of `conflicts` — a second, related solver-dynamics signal, reported but not selected as primary unless it outperforms on train (mirrors Phase 2's train-only model-selection discipline for `disc_flips` vs. `basin`).
- **`foundneighbor(y)`**: identical definition to Phase 2 (radius-3 Hamming neighbors within `A_C(I)`) — retained unchanged as the "uses only the found set's own geometry" baseline/predictor, exactly as `PHASE2_FREEZE.md` specifies it must not be silently redefined.
- **`hamming_weight(y)`, `random_score(y)`**: unchanged baselines.

## What was explicitly ruled out, and why (per task's exclusion list)

- **VSIDS per-variable activity, per-clause LBD**: not exposed through PySAT's Python API for Glucose3 (`CDCL_SOLVER.md`) — genuinely unavailable, not a leakage concern, documented as a scope limitation rather than worked around with a proxy that might accidentally encode ground truth.
- **"Diversity among solutions already discovered"**: implemented as `foundneighbor(y)` (uses only `A_C(I)`), not a separate feature — avoids double-counting a nearly identical signal under two names.
- **Anything requiring `S_I\A_C(I)`, true cluster labels, or true blind-zone membership**: never computed inside `cdcl_stage_a.py` (verified structurally — see `CDCL_PROTOCOL.md` §2 for the isolation mechanism, stronger than Phase 2's already-strict module separation).

## Primary predictor selection discipline

As in Phase 2, the choice between `risk_cdcl_recurrence` and `risk_cdcl_conflicts`/`risk_cdcl_decisions` as the "primary" CDCL solver-dynamics predictor is made on the **train split only**, inside `analyze_cdcl_results.py`, mirroring `PHASE2_FREEZE.md`'s frozen discipline exactly — see `CDCL_RESULTS.md` for the selected predictor and its train/test numbers.
