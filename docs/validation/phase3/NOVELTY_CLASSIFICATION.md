# NOVELTY_CLASSIFICATION.md — Phase 3, Part 17

Conservative classification of every major Phase 3 statement. Labels: KNOWN MATHEMATICS, KNOWN SAT RESULT, KNOWN TDA RESULT, SPECIALIZED COROLLARY, NEW MATHEMATICAL RESULT, NEW COMPUTATIONAL RESULT, NEW SYNTHESIS/FRAMEWORK, CONJECTURE, NEGATIVE RESULT.

| Result | Label | Basis |
|---|---|---|
| CDCL (Glucose3) exhibits a held-out-predictable blind zone (`risk_cdcl_recurrence`, test AUROC 0.667, `p<0.001`) | **NEW COMPUTATIONAL RESULT** | `CDCL_RESULTS.md` |
| WalkSAT and CDCL blind zones are approximately independent overall but regime-conditional (complementary near-threshold, mildly shared intermediate) | **NEW COMPUTATIONAL RESULT** | `CROSS_SOLVER_GEOMETRY.md` §Part 7 |
| Blind-zone decomposition is not distinguished by Hamming weight, but is by distance-to-visible-set (WalkSAT misses closer, CDCL misses farther) | **NEW COMPUTATIONAL RESULT** | `CROSS_SOLVER_GEOMETRY.md` §Part 8 |
| Cross-prediction is asymmetric (`risk_basin→CDCL` works, `risk_cdcl_recurrence→WalkSAT` does not) | **NEW COMPUTATIONAL RESULT** | `CROSS_PREDICTION.md` |
| Solver-union geometric complementarity: `ε̂_union<min(ε̂_W,ε̂_C)` in 15.6% of instances, modest coverage gain | **NEW COMPUTATIONAL RESULT** (framed strictly geometrically, no portfolio-runtime claim) | `PORTFOLIO_GEOMETRY.md` |
| CDCL shows dramatically less apparent fragmentation than WalkSAT at matched coverage (up to 13× fewer excess components) | **NEW COMPUTATIONAL RESULT** — the single most striking new empirical finding of Phase 3 | `BUDGET_TRAJECTORIES.md` |
| Asymmetric H₀ correspondence theorem (claim (a), zero slack; claim (b), `2ε` slack) | **SPECIALIZED COROLLARY**, most likely of Harker–Kramár–Levanger–Mischaikow (2019) Prop. 5.6 — **reclassified down from Phase 2's implicit "new theorem" framing**, per aggressive prior-art search; exact match not confirmed, but the existence of essentially this precedent was confirmed via a careful, arXiv-verified secondary citation | `H0_THEOREM_AUDIT.md`, `H0_PRIOR_ART_MATRIX.md` |
| Elementary from-scratch derivation of the asymmetric theorem, avoiding interleaving-distance machinery | **NEW SYNTHESIS/FRAMEWORK** (pedagogical/expository contribution — a genuinely simpler self-contained route to a likely-known conclusion, useful for a SAT-audience paper) | `H0_THEOREM_AUDIT.md` |
| Sharpness of the `2ε` constant (extremal Hamming-cube example, exact equality) | **NEW MATHEMATICAL RESULT** — no source found in this search (or Phase 2's) establishes or discusses sharpness for this setting | `H0_SHARPNESS.md` |
| Exact structural theory of `C_A(r)` vs. `C_S(r)` (inclusion-induced map on components, the `r≥ε` threshold for guaranteed `C_A≥C_S`, explicit under-representation counterexample) | **NEW MATHEMATICAL RESULT** (elementary, but the precise threshold characterization and counterexample were not previously stated in this project or found in the literature search) | `FRAGMENTATION_THEOREM.md` |
| General 2-parameter degree-Rips bifiltration stability (Blumberg–Lesnick) | **KNOWN TDA RESULT** — confirmed, read from primary source, explicitly ruled out as a match for our setting | `H0_THEOREM_AUDIT.md` |
| Single-linkage/dendrogram Gromov–Hausdorff stability (Carlsson–Mémoli) | **KNOWN TDA RESULT** | `H0_PRIOR_ART_MATRIX.md` |
| Merge-distortion / density-cluster-tree minimality (Eldridge–Belkin–Wang) | **KNOWN TDA RESULT**, structurally analogous but not identical (asymptotic, not our finite-sample deterministic form) | `H0_PRIOR_ART_MATRIX.md` |
| Manifold-reconstruction theorems (Niyogi–Smale–Weinberger) requiring reach/regularity | **KNOWN TDA RESULT**, confirmed inapplicable without extra structure our setting lacks | `H0_PRIOR_ART_MATRIX.md` |
| SAT sampling bias / solver-specific search dynamics (background literature) | **KNOWN SAT RESULT** (Phase 1 `PRIOR_ART.md`) | — |
| CDCL search-order sensitivity to variable/clause permutation (used as the randomization mechanism) | **KNOWN MATHEMATICS/ENGINEERING** (standard CDCL behavior; not claimed novel) | `CDCL_SOLVER.md` |

## What changed from Phase 2's novelty posture

Phase 2's `NOVELTY_CLASSIFICATION.md` labeled the asymmetric H₀ result "**NEW THEOREM**" (with the caveat "elementary... not found in the literature search performed"). **Phase 3's more aggressive, targeted search materially weakens that label** — not to FALSE, but down to **SPECIALIZED COROLLARY (probable)**. This is exactly the kind of self-correction the task's "final validation gate" framing was designed to catch, and it is reported here without softening: **Phase 2 overstated this one result's novelty; Phase 3 catches and corrects it.** The sharpness result and the exact `C_A` vs. `C_S` structural theory (`FRAGMENTATION_THEOREM.md`) are Phase 3's own, unambiguously original (within the limits of any literature search) contributions that partially compensate — the *theorem itself* is likely known, but *how tight it is* and *exactly when the naive monotonicity holds* were not found anywhere and are verified here.
