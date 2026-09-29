# FAILURE_ANALYSIS.md — Phase 2, Part 12

Actively tries to falsify the V2 thesis per each of the task's six listed failure criteria. No post-hoc feature engineering was applied to the test split after seeing its results — `risk_basin` and its sign/direction were frozen from train-split model selection (`EXPERIMENT_PROTOCOL.md` §8) before `data/analyze_results.py`'s "FINAL EVALUATION" section ever ran.

## Criterion-by-criterion assessment

### 1. "Solver-internal predictors do not beat trivial baselines" — **NOT observed; thesis survives this test**
`risk_basin` (test median AUROC `0.658`, CI `[0.636,0.685]`) clears random (`0.504`) and Hamming-weight (`0.519`) baselines with non-overlapping CIs, and a permutation test gives `p<0.001` (`EXPERIMENT_RESULTS.md` §5). **However**, this must be read alongside the next finding, which is a genuine partial failure.

### 2. "Blind-zone predictions fail on held-out instances" — **NOT observed; thesis survives**
Test-split result (§1 above) is the held-out evaluation itself — the effect was not merely found on train and lost on test; it reproduced at closely comparable magnitude (train `0.652` → test `0.658`).

### 3. "Observed fragmentation is extremely rare" — **NOT observed; thesis survives, with an important qualifier**
51.3% of 349 real test instances show observer-induced fragmentation (Part 10) — far from rare in aggregate. **Qualifier, reported honestly**: this is almost entirely a `solution_rich`-regime phenomenon (99.2% there) and comparatively rare near the SAT/UNSAT threshold (9.0%). A V2 claim of "fragmentation is common" needs the regime caveat attached, not stated as a uniform property of random 3-SAT.

### 4. "`ε̂` adds no useful information beyond coverage" — **PARTIALLY observed; the most serious finding of this phase**
`Spearman(coverage, ε̂) = -0.975` on real data (`EXPERIMENT_RESULTS.md` §7) — for this solver+instance ensemble, `ε̂` and coverage are **almost perfectly (anti-)redundant**. This is a real tension with treating `ε̂` as an independently valuable diagnostic *for this specific empirical setting*, even though Phase 2 Part 4 *proves* they are logically independent in the worst case (adversarial constructions). **Follow-up check performed** (not originally scripted, run ad hoc in response to this finding, methodology fully described, not cherry-picked after seeing a favorable number): does `ε̂` retain predictive power for a *different* target — topological fragmentation — after conditioning on coverage? Result: `Spearman(ε̂, \text{is\_fragmented})` within the **middle coverage tercile** (where the marginal relationship can't just be riding the strong coverage↔fragmentation link at the extremes) is `0.687` (`p≈10⁻³⁴`, `n=232`) — **`ε̂` is not fully redundant with coverage** for predicting fragmentation specifically, even though it is redundant with coverage in raw correlation terms. **Verdict: this criterion is not cleanly "failed" or "passed" — it surfaces a real, reportable nuance that V2 must state carefully rather than oversell `ε̂`'s independence from coverage** (see `V2_DECISION.md` Q9).

### 5. "Persistence distortion is trivial at all tested scales" — **NOT observed; thesis survives**
Excess component counts up to `119` (instance 537, `C_A(1)=121` vs `C_S(1)=2`) — far from trivial. The theorem bound itself held with **zero violations** across ~7,000 checks (Part 10), which is simultaneously a validation of the math and evidence that the *un-corrected* raw cluster counts (`Δ_A(r)`, the January paper's original diagnostic) can be dramatically misleading absent the `2ε̂` correction — exactly the phenomenon the stability theorem exists to control.

### 6. "Effects disappear after controlling for solution-set size or solver budget" — **NOT observed for `risk_basin`'s core effect; PARTIALLY observed for the *fragmentation-resolves-with-budget* claim**
- Solution-set-size stratification (`\|S_I\|` terciles): `risk_basin`'s AUROC holds in every tercile (`0.743`/`0.674`/`0.608`, all `>0.5`), trending down (not vanishing) as `\|S_I\|` grows — an honest, reportable trend, not a failure.
- Budget trajectories (Part 11): the *qualitative* claim ("more budget reduces fragmentation") holds for instance 619 (clean monotonic-ish improvement, though not full resolution by `T=600`) but **essentially does not hold within the tested budget range** for instance 537 (very large `\|S_I\|=2507`; fragmentation barely improves even at `T=600`, `20%` coverage). **This is a genuine, reportable partial failure**: the "budget resolves fragmentation" claim is budget-*and-scale*-dependent, not a universal guarantee at practically reachable budgets for solution-rich instances. State this limitation explicitly in V2, do not round it off to "fragmentation resolves with more search" as a blanket claim.

## Overall verdict on this criterion set

**No criterion triggered a clean, blanket failure of the V2 thesis.** Two criteria (4 and 6) surfaced **real, non-trivial partial limitations** that must be reported with their qualifiers intact:
1. `ε̂` is empirically near-redundant with coverage for this ensemble (though not fully, and not for every target) — V2 should not oversell `ε̂` as adding large amounts of new information beyond coverage in typical random-3-SAT settings, while still being able to cite the worst-case logical-independence proof (Part 4) and the fragmentation-conditional-on-coverage result (above) as the honest, narrower claims that *do* hold.
2. Budget-driven fragmentation resolution is real but scale-limited — solution-rich instances may not resolve within practical restart budgets.

## What would have constituted a genuine, unqualified failure (for calibration)

To be explicit about what a *negative* result would have looked like, so the above is legible as a real test and not a foregone conclusion: `risk_basin`'s test-split CI overlapping `0.5` or overlapping the random baseline's CI; the permutation test's `p`-value for `risk_basin` landing above `0.05`; the `\|S_I\|`-stratified AUROCs crossing below `0.5` in the large-`\|S_I\|` tercile; or fragmentation frequency below, say, `5%` uniformly across regimes. None of these occurred.
