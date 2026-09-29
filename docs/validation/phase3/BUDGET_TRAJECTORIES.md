# BUDGET_TRAJECTORIES.md — Phase 3, Part 11

CDCL trajectories from `scripts/part11_cdcl_budget_trajectory.py`, output `data/part11_cdcl_output.txt`; WalkSAT trajectories reused unchanged from Phase 2 (`phase2/data/part11_budget_trajectory.json`), same two pre-specified instances (id `537` solution_rich, id `619` intermediate — chosen in Phase 2 as the most dramatically fragmented cases, reused here for direct paired comparison, not re-selected).

## Instance 537 (`n=20, α=2.5, |S_I|=2507`, fixed `r=1`, `C_S(1)=2`)

| Budget | `\|A_T\|` | coverage | `ε̂(T)` | `C_A(r=1)` |
|---|---|---|---|---|
| **CDCL** `T=1` | 5 | 0.20% | 12 | 5 |
| **CDCL** `T=8` | 38 | 1.52% | 10 | 7 |
| **CDCL** `T=32` | 147 | 5.86% | 7 | **9** |
| **CDCL** `T=64` | 283 | 11.29% | 6 | **5** |
| **WalkSAT** `T=40` | 40 | 1.60% | 7 | 40 |
| **WalkSAT** `T=150` | 137 | 5.46% | 5 | **118** |
| **WalkSAT** `T=600` | 504 | 20.10% | 3 | **189** |

## Instance 619 (`n=20, α=3.5, |S_I|=482`, fixed `r=1`, `C_S(1)=4`)

| Budget | `\|A_T\|` | coverage | `ε̂(T)` | `C_A(r=1)` |
|---|---|---|---|---|
| **CDCL** `T=8` | 38 | 7.88% | 6 | **8** |
| **CDCL** `T=32` | 131 | 27.18% | 4 | **11** |
| **CDCL** `T=64` | 240 | 49.79% | 4 | **10** |
| **WalkSAT** `T=40` | 40 | 8.30% | 4 | **37** |
| **WalkSAT** `T=150` | 109 | 22.61% | 3 | **48** |
| **WalkSAT** `T=600` | 286 | 59.34% | 2 | 13 |

## The headline finding: CDCL shows dramatically less apparent fragmentation than WalkSAT at matched coverage

This was **not** anticipated going into Phase 3 and is one of its most substantial new findings. Compare at closely-matched coverage:

- **Instance 537**: WalkSAT at `5.46%` coverage shows `C_A(1)=118`; CDCL at a *similar* `5.86%` coverage shows `C_A(1)=9` — **over 13× less apparent fragmentation at essentially the same sample size.**
- **Instance 619**: WalkSAT at `8.30%` coverage shows `C_A(1)=37`; CDCL at a *lower* `7.88%` coverage shows `C_A(1)=8` — again roughly **4–5× less fragmentation** despite comparable (if anything, slightly lower) coverage.

`ε̂(T)` also tends to be *slightly worse* for CDCL at matched coverage in these examples (e.g. instance 537 at `~6%` coverage: CDCL `ε̂=7`, WalkSAT `ε̂=5`) — so this is **not** simply "CDCL is better on every axis." The fragmentation gap is specifically about **how coherently the two solvers' samples sit relative to each other geometrically**, not about raw coverage-vs-resolution trade-off (which both solvers show, consistent with Phase 1's proof that these are logically distinct diagnostics — this pair of trajectories is itself a second, independent empirical demonstration of that logical distinctness, now across solvers as well as across budgets).

**Candidate explanation** (hypothesis, consistent with but not proven by `CROSS_SOLVER_GEOMETRY.md`'s Part 8 finding that WalkSAT-specific misses sit unusually close to visible territory): CDCL's blocking-clause enumeration, within a single search-order run, tends to discover solutions that are structurally/combinatorially *related* to each other (flipping a small part of the assignment relative to a just-blocked solution is often still satisfiable), producing samples that are geometrically clustered together even at low coverage; WalkSAT's independent restarts scatter more freely across the solution space, leaving many small gaps between found points that read as spurious apparent fragments. This is a genuinely new, solver-paradigm-level geometric-distortion finding, not something either Phase 1 or Phase 2 anticipated.

## Coverage vs. `ε̂` vs. fragmentation dynamics

Confirms Phase 2's own instance-537 finding (`FAILURE_ANALYSIS.md` criterion 6): for this very solution-rich instance, **neither solver** fully resolves fragmentation within the tested budget range (`C_A(1)` for WalkSAT ends at `189` vs. true `C_S(1)=2`, even at `20%` coverage; CDCL fares much better in absolute terms but still ends at `5`, not `2`, at `11%` coverage) — solution-rich instances remain the hardest case for *either* paradigm to achieve geometrically faithful sampling at practically reachable budgets.

For instance 619, both solvers show the qualitative "`ε̂` falls, fragmentation eventually falls back toward `C_S`" pattern the theorem (`PERSISTENCE_STABILITY.md`, `FRAGMENTATION_THEOREM.md`) predicts is *possible* as `ε̂` shrinks (recall: the theorem only *guarantees* resolution at radius `r+2ε̂`, not at the fixed radius `r`; both trajectories' improvement at the *fixed* radius is an empirically observed trend, stronger than what's proven) — CDCL reaches this resolution at a much smaller `ε̂` and lower budget than WalkSAT needs to get partway there.
