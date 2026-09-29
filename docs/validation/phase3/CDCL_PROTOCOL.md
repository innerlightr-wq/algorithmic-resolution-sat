# CDCL_PROTOCOL.md — Phase 3, Parts 4–6

## Instance matching (Part 4)

**All 720 Phase 2 instances used** (360 train + 360 test, same files, same ids) — no subset selection needed, since CDCL/Glucose3 enumeration was confirmed (pilot, `data/pilot_timing_output.txt`) to be computationally trivial (`~0.0004s` per instance at the WalkSAT-comparable budget) relative to Phase 2's own WalkSAT budget. This gives the strongest possible paired comparison: identical `I`, identical `S_I`, only the solver paradigm differs.

## Budget normalization (Part 4)

Three notions compared, as required:
- **A. Equal wall-clock**: CDCL's primary budget (`R=5×T=8=40` total solution-discovery attempts) completes the full 720-instance sweep in `<1s`; WalkSAT's 150-restart budget took `~135s` total across both splits (Phase 2). CDCL is dramatically faster per unit of search effort — itself a reportable cross-paradigm finding (`BUDGET_TRAJECTORIES.md`), not something to normalize away.
- **B. Equal distinct solutions found**: the calibrated primary budget (`CDCL_ACCESSIBILITY.md`) targets *comparable coverage* to WalkSAT's `K=150`, not equal raw attempt count — found to require far fewer CDCL attempts (`R×T=40`) than WalkSAT restarts (`150`) to reach similar coverage, confirming CDCL's higher sample efficiency.
- **C. Equal number of solver attempts**: for CDCL's blocking-clause enumeration specifically, "number of attempts" and "number of distinct solutions found" **collapse into the same quantity** (each `solve()` call either yields exactly one new solution or terminates the enumeration) — a genuine structural difference from WalkSAT, where a restart can fail to find anything at all. Documented explicitly here rather than silently treated as equivalent across paradigms.

Both directions are exercised: the primary Stage A/B pipeline uses the coverage-calibrated `R=5,T=8` budget (Parts 5–6); `BUDGET_TRAJECTORIES.md` (Part 11) separately sweeps `T∈\{1,2,4,8,16,32,64\}` at fixed `R=5` to produce a genuine multi-budget trajectory, directly paired against WalkSAT's own `T∈\{5,...,600\}` restart sweep on the identical two instances.

## Anti-leakage isolation (Part 5), stronger than Phase 2's

In addition to Phase 2's module-separation pattern (a Stage-A script with no import path to ground-truth code), Phase 3 adds a **programmatic runtime guard**: `cdcl_stage_a.py`'s `guarded_open()` wraps every file access and raises `RuntimeError` immediately if the path contains any of `["stage_b_results", "rho_frozen", "stage_b_test_log", "stage_b_train_log"]`. This was **tested directly** (not just asserted): calling `guarded_open("../../phase2/data/stage_b_results_test.json")` from within the Stage-A module correctly raises before any file content is read (confirmed interactively, `scripts/cdcl_stage_a.py` import + direct call). `rho` (the fixed radius used for the retrospective `missᴿ_ρ` target) is deliberately included in the forbidden-path list even though it is only a scalar, not a full solution set, because it was itself derived from revealed `S_I` in Phase 2 — Stage A never needs it and is blocked from ever reading it, eliminating any possibility of a *scalar* leak, not just a set-level one.

Stage A → Stage B ordering is enforced the same way as Phase 2: separate process invocations (`python3 cdcl_stage_a.py {train,test}` completes and writes a hashed file; **only then** is `python3 cdcl_stage_b.py {train,test}` run, which verifies that hash against the file on disk before proceeding — confirmed in `data/cdcl_stage_b_{train,test}_log.txt`, both printing "CDCL Stage A hash verified" as their first line of output).

## Stage A execution

`scripts/cdcl_stage_a.py {train,test}`: `R=5` independent permuted+phase-randomized `Glucose3.enum_models()` runs per instance, each truncated at `T=8` solutions; per-found-solution `recurrence`, `conflicts_to_discovery`, `decisions_to_discovery` (incremental `accum_stats()` differencing), `foundneighbor`, `hamming_weight`, `random_score` computed and frozen. **`0.4s` train, `0.4s` test** (`data/cdcl_stage_a_{train,test}_log.txt`), hashes `4ce9c8e6...` (train), `e94a679d...` (test).

## Stage B execution

`scripts/cdcl_stage_b.py {train,test}`: verifies the Stage-A hash, re-derives `S_I` fresh via Phase 2's `exhaustive_only` module, reads Phase 2's own frozen WalkSAT `A_W(I)` for cross-solver comparison, computes `M_C(I)`, `ε̂_C`, `\text{coverage}_C`, `\text{miss}ᴿ_ρ` (reusing Phase 2's frozen `ρ=1.0`), plus cross-solver set quantities (`M_W`, Jaccard, union coverage/`ε̂`). **`45.9s` train, `43.7s` test** (dominated by exhaustive re-enumeration, not CDCL itself). `data/cdcl_stage_b_results_{train,test}.json` (`~18MB` each — includes full `S_I`/`M_W`/`M_C` point lists for downstream cross-solver analysis, Parts 7–11).

## Evaluation discipline (Part 6)

Identical machinery to Phase 2 (`analyze_cdcl_results.py`, structurally parallel to Phase 2's `analyze_results.py`): train-only model selection (Hamming-weight sign, choice among `risk_cdcl_recurrence`/`risk_cdcl_conflicts`/`risk_cdcl_decisions`), test-split evaluation touched once, instance-level median + `5,000`-resample bootstrap CI, `1,000`-permutation instance-level significance test, stratification by regime/`n`/`\|S_I\|` tercile. See `CDCL_RESULTS.md` for the numbers.
