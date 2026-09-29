# FINAL_CLAIM_HIERARCHY.md — Phase 4, Parts 14–15

## Tier 1 — Proved / established mathematics

- `ε̂(A,I) = d_\text{Haus}(A(I),S_I)` exactly (Phase 2 `HAUSDORFF_IDENTITY.md`) — known math, not novel.
- Exact Hamming-ball distinguishability theorem, `ε≤⌈D/2⌉` open / `ε<⌈D/2⌉` closed (Phase 2 `HAMMING_BALL_THEOREM.md`) — corrects the January paper's Theorem 2.1, proved and exhaustively verified.
- Asymmetric H₀ correspondence (no false merge; `+2ε` recovery) — **now confirmed, by direct primary-source reading, to be a DIRECT COROLLARY of Harker–Kramár–Levanger–Mischaikow (2018/2019) Proposition 5.6(i)**, specialized to `H_0` (`HARKER_COMPARISON_MATRIX.md`). Still Tier 1 (it is proved, correctly), but must be cited, not claimed.
- Sharpness of the `+2ε` constant, including a Hamming-cube-realized extremal example (Phase 3 `H0_SHARPNESS.md`) — **the one piece of this theorem-cluster not found addressed anywhere in the literature search** (`SHARPNESS_NOVELTY_AUDIT.md`); still labeled cautiously (independent, narrow-scope, not claimed as a deep new technique).
- Exact `C_A(r)` vs. `C_S(r)` structural theory — the `r<ε`/`r≥ε` threshold, explicit under-representation counterexample (Phase 3 `FRAGMENTATION_THEOREM.md`) — likely derivable from Harker et al.'s machinery by a specialist but not found stated explicitly anywhere; SPECIALIZED COROLLARY / ELEMENTARY CONSEQUENCE.
- Coverage/resolution logical independence, proved via explicit parameterized families (Phase 2 `COVERAGE_RESOLUTION_THEOREM.md`) — elementary, self-contained, not dependent on any TDA machinery.

## Tier 2 — New computational results (genuinely supported after this phase's audit)

- **Held-out WalkSAT blind-zone predictability** (`AUROC≈0.658`) and **held-out CDCL blind-zone predictability** (`AUROC≈0.667`) — both stand, unaffected by this phase (they are *within*-solver results; the confound audit targeted *cross*-solver claims only).
- **Matched-coverage fragmentation difference between WalkSAT and CDCL** — **strengthened, not weakened, by this phase**: replicated across `349` held-out instances (not `2`), median ratio `11.6×` (`95% CI [9.6,13.3]`), survives coverage-matching (`p=2.4×10⁻⁷`). This is now the single most rigorously audited empirical result in the project.
- **The paired `ε̂` reversal** (WalkSAT better resolution, CDCL better connectivity, at matched coverage) — a **new finding surfaced by this phase's own audit work** (`PAIRED_OBSERVER_TEST.md`), not present in Phase 3's framing, and arguably the cleanest empirical link to the project's Tier-1 mathematics.
- **Regime-dependent WalkSAT/CDCL blind-zone overlap** (Phase 3 `CROSS_SOLVER_GEOMETRY.md`) — unaffected by this phase (not targeted by the confound audit, which was specifically about the *predictive*-transfer asymmetry, not the *overlap* finding).

## Cross-solver directional transfer — **downgraded to Tier 3/rejected as a Tier 2 claim**

Phase 3's "`W→C` cross-prediction (`0.625`) `≫` `C→W` (`0.526`)" **does not survive this phase's confound audit** as an independent Tier-2 finding: three convergent methods (conditional model, residualization, coverage-matched stratification) show it is substantially explained by generic geometric confounds, chiefly a coverage-calibration mismatch between the two solvers' tested budgets. **This claim is retracted from Tier 2.** What remains defensible, narrowly: the *raw, unadjusted* correlation exists and is worth reporting as a **methodological cautionary note** (a superficially interesting cross-solver signal that evaporates under confound control — itself a useful finding about how *not* to over-interpret raw cross-prediction numbers), not as a positive discovery about solver dynamics.

## Tier 3 — Interpretations (labeled as such, not stated as fact)

- "Solver-specific observational geometry" (fragmentation difference, `ε̂` reversal) — supported as an *interpretation* of Tier 2 results, appropriately hedged per `PAIRED_OBSERVER_TEST.md`'s caveat (two specific implementations audited, not a claim about "local search vs. systematic search" as paradigms in general).
- "Shared accessibility structure" / "rare solution sensing" — **explicitly tested and not supported** (`RARE_SOLUTION_TEST.md`); should not appear even as a hedged interpretation, since the specific test designed to support it returned a null/artifact result.

## Tier 4 — Speculative / future work (must not appear as established claims)

- Adaptive blind-zone-aware solvers; geometric solver portfolios beyond the narrow `ε̂_union` observation (Phase 3 `PORTFOLIO_GEOMETRY.md`, itself already carefully scoped as geometric-only); conjugacy/semiconjugacy language (**explicitly rejected**, `CONJUGACY_FILTER.md`); any complexity-theoretic implication (never claimed anywhere in this project, and this phase finds no new basis for one).

## Part 15: the central claim

Of the five candidates:

- **(A)** "Solver outputs are Hausdorff approximations whose resolution controls the reliability scale of inferred connectivity" — Tier 1 math, well-supported, but **incomplete on its own** after this phase: `PAIRED_OBSERVER_TEST.md` shows resolution (`ε̂`) and connectivity-fidelity (fragmentation) can move in **opposite directions across solvers**, so "resolution controls reliability" needs the explicit caveat that the *guarantee* (Tier 1 theorem) is a one-directional bound (small `ε̂` ⟹ bounded distortion), not a claim that better `ε̂` always means better-looking connectivity in practice — CDCL's case (worse `ε̂`, better apparent connectivity) is not a counterexample to the theorem (the theorem is an upper bound, not tight in practice) but does show (A) alone, unqualified, could mislead a reader into expecting monotonicity that this project's own data shows does not hold.
- **(B)** "Distinct solver paradigms produce systematically different observational geometries of the same SAT solution spaces" — **strongly, specifically, and now most rigorously supported** (fragmentation replication, `ε̂` reversal, both paired, both `p<10⁻⁷`, both surviving matched-coverage controls).
- **(C)** "Solver dynamics prospectively predict their own blind zones" — well-supported (Tier 2, within-solver), but **narrower** than (B) — a single-solver fact, not a claim about paradigm differences.
- **(D)** "WalkSAT and CDCL expose partially shared but asymmetric accessibility structure" — **the cross-solver directional-transfer component is now retracted** (see above); the "partially shared" (overlap, Phase 3 Part 7) component survives but is regime-conditional, not a clean asymmetric-structure story.
- **(E)** "Coverage alone is insufficient to characterize how faithfully a solver represents solution-space geometry" — true and supported, but this is really a **restatement of (B)'s evidentiary basis**, not a distinct central claim.

**Recommendation: (B) should lead**, directly grounded in `PAIRED_OBSERVER_TEST.md` and `FRAGMENTATION_REPLICATION_AUDIT.md` as its primary evidence. **(C) and (A) are the strongest supporting claims** — (C) for the within-solver predictability result, (A) for the theoretical machinery that explains *why* fragmentation is bounded at all (even though the bound isn't tight enough to make the two solvers' connectivity pictures agree). **(D) and (E) should not be used as the paper's framing claims** — (D)'s strongest component didn't survive audit, and (E) is subsumed by (B). This differs from Phase 3's `FINAL_GATE.md` Q15 answer (which combined a version of B with the now-retracted cross-prediction result as supporting evidence) — this phase's version is narrower and better-supported.
