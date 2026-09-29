# PHASE2_FREEZE.md — Phase 3, Part 1

SHA-256 checksums for every Phase 2 deliverable, script, and data file, plus Phase 1's top-level deliverables for reference, computed **before** any Phase 3 code was written. Full listing: `data/phase2_checksums.txt` (58 files). Phase 2 (and Phase 1) files are not touched anywhere in Phase 3 — any Phase 3 script that needs Phase 2 data only **reads** the files listed here.

## Exact frozen Phase 2 definitions (recorded for reference, not to be silently altered)

### Instance generation (`phase2/scripts/generate_instances.py`)
- Random 3-SAT, `n∈{16,18,20}`, `α∈{2.5 (solution_rich), 3.5 (intermediate), 4.2 (near_threshold)}`.
- 40 train + 40 test satisfiable instances per `(n,α)` cell → 360+360 = **720 total**.
- Satisfiability filtered via exhaustive check at generation time (selection effect documented in Phase 2, not re-litigated here); solution data discarded immediately, only CNF clauses retained.
- Split by instance (first 40 → train, next 40 → test), fixed at generation, seed `20260928+2`.
- **No solution cap.**

### Train/test split
- By instance, never by solution. Train used for model selection only; test touched once for final evaluation (Phase 2 `EXPERIMENT_PROTOCOL.md` §8).

### WalkSAT implementation (`phase2/scripts/walksat_solver.py`)
- Standard WalkSAT: pick random unsatisfied clause; with probability `p_noise` flip a random variable in it (random walk move), else flip the variable minimizing newly-violated clauses (greedy, ties random).
- `K=150` independent restarts per instance, `max_flips=3000`, `p_noise=0.5`.
- Per-restart log: `{found: bool, assignment, flips_used}`.

### `risk_basin` definition (`phase2/scripts/run_stage_a.py`)
- `basin(y) = ` count of the `K=150` restarts whose converged output equals `y`, for `y∈A(I)`.
- `risk_basin(y) = -basin(y)` (higher = predicted higher miss risk — low basin ⟹ under-sampled region hypothesis).
- Companion predictors computed the same pass: `disc_flips(y)` (mean flips-to-discovery), `foundneighbor(y)` (count of other found solutions within Hamming radius 3).

### Baselines (Phase 2 `EXPERIMENT_PROTOCOL.md` §5)
1. `risk_random`: i.i.d. random score, frozen seed.
2. `risk_hamming_weight`: `sign·hamming_weight(y)`, sign chosen on train split only (chosen: `+1`).
3. `risk_foundneighbor`: uses only `A(I)`'s own geometry (no solver-dynamics).
4. `risk_disc_flips`: second solver-dynamics candidate (not selected as primary; see below).

### Evaluation metrics (Phase 2 `EXPERIMENT_PROTOCOL.md` §6–9)
- Primary binary target: `has_missed_neighbor(y) = 1[missᴿ_ρ(y|I)>0]`, `ρ=1.0` (median nearest-neighbor distance within `S_I`, computed once from the **train split only**, frozen to `phase2/data/rho_frozen.json`, reused unchanged on test).
- Metrics: per-instance AUROC (binary target), AUPRC, Spearman rank correlation (continuous target `missᴿ_ρ`).
- Instance is the independent unit: per-instance metric first, then **median** across instances + **instance-level bootstrap** (5,000 resamples) for CIs; **instance-level permutation test** (1,000 permutations, label-shuffling within each instance) for significance.
- Minimum `4` found solutions per instance required for within-instance ranking metrics (`MIN_FOUND_FOR_INSTANCE=4`); instances below this are excluded and the skip count reported, never silently dropped.

### Phase 2 headline result (frozen, for comparison)
`risk_basin` selected on train (median AUROC 0.652), evaluated once on test: **median AUROC 0.658 [0.636, 0.685]**, median Spearman 0.252, permutation `p<0.001`; beats `risk_random` (0.504) and `risk_hamming_weight` (0.519); survives stratification by regime, `n`, and `|S_I|` tercile.

## Phase 3 ground rule

Phase 3's CDCL predictor is judged against **these exact same** baselines, `ρ`, instance-unit discipline, and metrics — no silent redefinition to make cross-solver numbers agree more favorably. Where Phase 3 must introduce a CDCL-specific analogue (e.g. `recurrence(y)` in place of `basin(y)`, since CDCL enumeration has no "restart" concept in the WalkSAT sense — see `CDCL_ACCESSIBILITY.md`), the analogy is stated explicitly and the original WalkSAT quantities are never redefined to match it.
