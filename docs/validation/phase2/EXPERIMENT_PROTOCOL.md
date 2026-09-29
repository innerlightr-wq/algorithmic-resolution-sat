# EXPERIMENT_PROTOCOL.md — Phase 2, Parts 6–9

Full methodology for the decisive freeze-before-reveal blind-zone prediction experiment. Real experiment, actually run (not a design-only pilot) — results in `EXPERIMENT_RESULTS.md`.

## 1. Overview

Question: **can solver dynamics predict, before ground truth is revealed, which of a solver's found solutions have undiscovered neighbors nearby?** Implements `ACCESSIBILITY_FRAMEWORK.md`'s prospective risk score `r̂ᴾ(y|I)`, `y∈A(I)`, tested against the retrospective target `missᴿ_ρ(y|I)`.

## 2. Instances (Part 7)

`scripts/generate_instances.py`. Random 3-SAT, `n∈{16,18,20}`, three regimes spanning the required range: `α=2.5` (solution-rich), `α=3.5` (intermediate), `α=4.2` (near-threshold). **40 train + 40 test satisfiable instances per `(n,α)` cell**, 9 cells → **360 train + 360 test = 720 total instances**. No solution cap (per task instruction, unlike the January paper's 500-cap).

**Selection effect, documented**: instances are filtered to satisfiable ones via `exhaustive_only.is_satisfiable()` at generation time (acceptance rate 65–100% depending on `α`, worst at `α=4.2`: 80/123 attempts ≈ 65%). This exhaustive check is discarded immediately — only the CNF clauses are retained in `instances_{train,test}.json`; no solution data is written to those files. This mirrors the January paper's own "50 satisfiable instances" protocol; it is not a new selection effect introduced by this experiment.

Train/test split is **by instance**, fixed at generation time (first 40 of each cell → train, next 40 → test) — never by solution within an instance.

## 3. Anti-leakage protocol (Part 6), enforced structurally, not just documented

- `sat_common.py`: shared, safe for both stages (instance generation, CNF evaluation). Contains **no exhaustive-enumeration code**.
- `exhaustive_only.py`: a **separate module**, containing all ground-truth-revealing code (`solve_all_exhaustive`, `is_satisfiable`). Imported **only** by `run_stage_b.py`, `part10_topology_validation.py`, `part11_budget_trajectory.py` (analysis/Stage-B scripts) — never by `run_stage_a.py` or `walksat_solver.py`. This makes a leakage bug require an explicit new `import exhaustive_only` line in Stage-A code, auditable by grep, not just documented as a rule.
- **`run_stage_a.py`** (Stage A, pre-reveal): reads CNF clauses only, runs `K=150` WalkSAT restarts (`max_flips=3000`, `p_noise=0.5`) per instance, computes prospective risk scores (§4) from the restart log alone, and **writes the results to disk with a SHA-256 hash and UTC timestamp in a companion `.hash.txt` file** — executed as a fully separate process invocation, completing and exiting before Stage B ever starts.
- **`run_stage_b.py`** (Stage B, reveal): the only script permitted to import `exhaustive_only`. **Verifies the Stage-A hash against the file on disk before doing anything else** (would raise an assertion error on mismatch — e.g. if Stage A were accidentally re-run after Stage B started). Only then re-enumerates `S_I`, computes `M_A(I)=S_I\A(I)`, and the retrospective target `missᴿ_ρ`.
- **Actually run as separate process invocations** (`python3 run_stage_a.py train`, then, in a separate later Bash call, `python3 run_stage_b.py train`) — not function calls within one script — so the freeze genuinely precedes the reveal in wall-clock time, verified by the timestamps in `data/stage_a_predictions_{train,test}.json.hash.txt` (both predate the corresponding `stage_b_results_*.json` files by construction of the run order, recorded in `data/*_log.txt`).

## 4. Prospective risk scores actually implemented (Part 6/8)

Per `ACCESSIBILITY_FRAMEWORK.md` §4, computed from the `K=150`-restart trajectory log, for each `y∈A(I)`:
- `basin(y)`: count of restarts whose converged output equals `y`.
- `disc_flips(y)`: mean flips-to-discovery among restarts that found `y`.
- `foundneighbor(y)`: count of other found solutions within Hamming radius `3` of `y` (uses only `A(I)`, no trajectory data — the "simplest legitimate" baseline/predictor from `ACCESSIBILITY_FRAMEWORK.md` §4).

**Deprioritized**: `visitdensity_ρ(y)` (full-trajectory proximity tracking) — judged not worth the added memory/runtime cost for this pass; `basin` and `disc_flips` already give two independent solver-dynamics signals. Documented here as a known gap, not silently dropped.

**Risk-score sign convention**: all risk scores are oriented so **higher = predicted higher miss risk**: `risk_basin=-basin`, `risk_disc_flips=+disc_flips` (hypothesized direction, see `EXPERIMENT_RESULTS.md` for the empirical surprise here), `risk_foundneighbor=-foundneighbor`.

## 5. Baselines (Part 8)

1. `risk_random`: i.i.d. random score (frozen seed) — sanity-check null, should show AUROC≈0.5.
2. `risk_hamming_weight`: `sign · hamming_weight(y)`, **sign chosen on the train split only** (both signs evaluated on train; the better-performing sign is frozen and reused, unchanged, on test) — this is the honest, non-circular analogue of the January paper's Hamming-weight-linked biased-sampler result, now used as a baseline to beat rather than as primary evidence (`ORIGINAL_EXPERIMENT_AUDIT.md` §3).
3. `risk_foundneighbor`: legitimate but uses only `A(I)`'s own geometry, no solver-dynamics information — tests whether solver dynamics (`basin`, `disc_flips`) add anything beyond static found-set geometry.
4. `risk_disc_flips`: a second solver-dynamics predictor, used both as a candidate and (relative to `risk_basin`) as a check on which dynamics signal is more informative.

## 6. Target quantities (Part 9)

- **Primary binary target**: `has_missed_neighbor(y) = 1[missᴿ_ρ(y|I) > 0]`, evaluated via per-instance AUROC and AUPRC.
- **Primary continuous target**: `missᴿ_ρ(y|I)` (count of true misses within radius `ρ` of `y`), evaluated via per-instance Spearman rank correlation.
- **`ρ` selection**: computed once from the **train split only** (`run_stage_b.py train`) as the median nearest-neighbor distance within `S_I`, pooled across all train instances' revealed solution sets → **`ρ=1.0`** (96,382 pooled nearest-neighbor distances). Frozen to `data/rho_frozen.json` and reused unchanged for the test split. Test split never computes its own `ρ`.

## 7. Instance as the unit of analysis (Part 9)

Every metric is computed **per instance first** (using only that instance's found solutions, `≥4` required — instances with `<4` found solutions are excluded from within-instance ranking metrics as statistically meaningless, tracked and reported as a skip count, never silently dropped). Aggregation across instances uses the **median** (robust to the occasional degenerate instance) plus **instance-level bootstrap** (`5,000` resamples of instances, not of individual solutions, percentile 95% CI). A dedicated **instance-level permutation test** (`1,000` permutations, label-shuffling **within** each instance before recomputing that instance's AUROC, then comparing the true across-instance median AUROC to the null distribution of permuted medians) avoids the pooled-pseudoreplication error the task explicitly warned against.

## 8. Model selection discipline (Part 6/7)

`scripts/analyze_results.py` performs **all** hyperparameter/model choices (Hamming-weight sign, and which of `risk_basin`/`risk_disc_flips` is the "primary" solver-dynamics predictor to report as the headline result) using **train-split data only**, printed under a clearly labeled "MODEL SELECTION (TRAIN SPLIT ONLY)" section before any test-split number is computed in the same script run. The test split is evaluated exactly once, under a "FINAL EVALUATION (TEST SPLIT, TOUCHED ONCE)" section, using the frozen choices from the train section.

## 9. Additional falsification checks actually run (Part 12, methodology described here; results in `FAILURE_ANALYSIS.md`)

- Stratification of the chosen predictor's test-split AUROC by `regime`, `n`, and (in a follow-up ad hoc check) `|S_I|` tercile — to test whether the effect is an artifact of one stratum (Simpson's-paradox check) or vanishes after controlling for solution-set size (explicit Part 12 falsification criterion).
- `Spearman(coverage, ε̂)` and `Spearman(ε̂, is_fragmented)` computed both marginally and within coverage terciles, to test whether `ε̂` is redundant with raw coverage or carries independent information (explicit Part 12 falsification criterion: "`ε̂` adds no useful information beyond coverage").

## 10. Part 10/11 methodology

- **Part 10** (`part10_topology_validation.py`): for every test instance with `A(I)≠∅, |S_I|≥2` (349/360 qualify), recomputes `S_I` (Stage-B-only), computes the full cluster spectrum `C_S(r), C_A(r)` for `r=0..n` via vectorized pairwise-Hamming-distance matrices (`topology_utils.py` — Gram-matrix trick, `O(N^2 n)` via BLAS, scales to `|S_I|` in the thousands), and **checks the PERSISTENCE_STABILITY.md Theorem 3 bound (`C_A(r+2ε̂)≤C_S(r)`) and the no-false-merge claim directly against real SAT data** — both are code-validation and theorem-demonstration simultaneously, as the task requested.
- **Part 11** (`part11_budget_trajectory.py`): for 2 instances selected as the most dramatically fragmented cases from Part 10 (one `solution_rich`, one `intermediate` — `near_threshold` instances have too few solutions for a meaningful trajectory), reruns WalkSAT with a **single shared random stream** truncated at increasing restart budgets `T∈{5,10,20,40,80,150,300,600}` (so `A_T(I)` is a genuine monotonically-growing anytime sequence, not independent resamples at each `T`), tracking `|A_T(I)|`, `ε̂(T)`, and `C_{A_T}(r)` at the instance's own observed fragmentation radius `r` from Part 10.
