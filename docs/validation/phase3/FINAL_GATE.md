# FINAL_GATE.md — Phase 3 final validation gate

Synthesizes all Phase 3 deliverables. Answers the 18 mandated questions directly, in order.

## 1. Does CDCL exhibit a prospectively predictable blind zone?

**Yes.** `risk_cdcl_recurrence` (count of independent permuted search orderings that rediscover a given solution), computed entirely from pre-reveal CDCL trajectory data, predicts which found solutions have undiscovered neighbors, on genuinely held-out test instances, with a programmatically-enforced (not just documented) anti-leakage guard verified to actually trip on a forbidden access attempt.

## 2. Held-out predictive performance versus baselines?

Test median AUROC **0.667 [0.647, 0.700]**, median Spearman **0.346**, instance-level permutation test `p<0.001` (random-baseline sanity check correctly non-significant, `p=0.934`). Beats random (`0.481`), Hamming-weight (`0.492`), found-neighbor-density (`0.467`), and a second candidate solver-dynamics feature that didn't pan out (`risk_cdcl_conflicts`, `0.471`). Survives stratification by regime (`0.615`–`0.761`), `n` (`0.652`–`0.692`), and `|S_I|` tercile (`0.615`–`0.785`) — no collapse anywhere tested.

## 3. Are WalkSAT and CDCL blind zones more overlapping, independent, or more complementary than expected by chance?

**Regime-conditional — not a single answer.** Overall, essentially independent (observed/expected Jaccard ratio `≈1.00`). But: **solution-rich instances are near-perfectly independent** (ratio `1.001`), **intermediate instances show mild positive sharing** (ratio `1.19` — some genuine shared difficulty), and **near-threshold instances are strongly complementary** (ratio `0.00` — near-zero observed overlap against a small but nonzero null expectation, though this regime's tiny `|S_I|` makes the statistic noisy). Mean fraction of `S_I` in each category: `26.4%` shared, `4.3%` WalkSAT-only, `17.0%` CDCL-only (overall); solution-rich alone: `67.8%` shared.

## 4. Is within-solver prediction stronger than cross-solver prediction?

**Yes on average** (within `0.662` vs. cross `0.575`, gap `0.087`) — but **asymmetrically**: `risk_basin→CDCL` cross-predicts well (`0.625`, CI excludes `0.5`), while `risk_cdcl_recurrence→WalkSAT` does not (`0.526`, CI includes `0.5`). The clean "within `≫` cross" reading is only half the story; WalkSAT's dynamics signal is more geometrically portable than CDCL's (hypothesis offered, not proven, in `CROSS_PREDICTION.md`).

## 5. What fraction of blind geometry appears shared versus solver-specific?

Overall: `26.4%` of `S_I` shared-blind, `4.3%` WalkSAT-only-blind, `17.0%` CDCL-only-blind (remainder found by at least one solver). Solution-rich: `67.8%` shared — most of that regime's difficulty is a common obstacle to both paradigms. Near-threshold: `1.0%` shared, `5.2%` CDCL-only — almost no common blind geometry at all in that regime.

## 6. Does combining WalkSAT and CDCL reduce `ε̂` beyond either alone?

**Yes, on 15.6% of instances** (`56/360`), strictly — a real minority effect, strongest in solution-rich (`22.5%`), weakest near-threshold (`5.8%`). Median coverage gain from the union: `+3.6%`.

## 7. Does this support a meaningful geometric interpretation of solver portfolios?

**As a geometric observation, yes; as a practical-performance claim, no such claim is made.** Genuine, non-trivial, regime-patterned complementarity exists at the level of covering radius and coverage; nothing here speaks to runtime cost, engineering value, or whether running two solvers is "worth it."

## 8. Does observer-induced fragmentation occur for CDCL as well as WalkSAT?

**Yes, but far less severely.** On the two paired budget-trajectory instances, CDCL's apparent fragmentation at matched coverage was **4–13× lower** than WalkSAT's (e.g. instance 537: WalkSAT `C_A(1)=118` at `5.46%` coverage vs. CDCL `C_A(1)=9` at `5.86%` coverage). This is a genuine, new, solver-paradigm-level finding, not anticipated at the start of Phase 3.

## 9. How does fragmentation vary by SAT regime and budget?

By regime (WalkSAT, Phase 2 Part 10, `349` instances): solution-rich `99.2%` fragmented, intermediate `42.4%`, near-threshold `9.0%`. By budget (both solvers, Phase 2+3 Part 11): fragmentation generally rises then falls as budget increases, tracking `ε̂`'s decline, but resolution at the *fixed* observed radius is empirically observed to be faster and more complete for CDCL than WalkSAT at comparable budgets, and neither solver fully resolves fragmentation within practical budgets on the most solution-rich tested instance.

## 10. Is the asymmetric H₀ theorem actually new, a known theorem, or a specialized corollary?

**Most likely a specialized corollary** of Harker, Kramár, Levanger, Mischaikow (2019), Proposition 5.6 — confirmed to exist and be cited by Blumberg & Lesnick (2020, verified by direct PDF read) as precisely "a variant of the standard Rips stability theorem for the case where one metric space is a subset of the other." The exact match was **not** independently confirmed (Harker et al.'s Proposition 5.6 itself was not retrieved and read in this pass) — but per the task's mandated default, absence of a disproof is not evidence of novelty, and the weight of evidence points to "known." **This is a downgrade from Phase 2's "NEW THEOREM" label — reported honestly as a self-correction, not minimized.**

## 11. Is the `+2ε` constant sharp in arbitrary metric spaces?

**Yes, proved.** An explicit 4-point construction achieves the bound with exact equality — the guaranteed recovery radius `r+2ε` cannot be lowered for any `c<2` without producing a counterexample.

## 12. Is `+2ε` sharp specifically in Hamming space?

**Yes.** The extremal construction is realized directly inside `\{0,1\}^n` (disjoint coordinate blocks), verified computationally across 7 `(r,ε)` parameter combinations, all exact — the Hamming cube's extra structure (vertex-transitivity, graph-geodesic property) does **not** allow any improvement over the general metric-space bound.

## 13. What is the exact strongest publishable fragmentation theorem?

The three-regime synthesis in `FRAGMENTATION_THEOREM.md`: (i) for `r<ε`, no monotone relationship between `C_A(r)` and `C_S(r)` is guaranteed — proved via an explicit under-representation counterexample where `C_A(r)<C_S(r)`; (ii) for `r≥ε`, `C_A(r)≥C_S(r)` is guaranteed (proved, `877/877` verified, zero violations) — fragmentation-or-equality only, never under-representation; (iii) for any `r_0`, `C_A(r_0+2ε)≤C_S(r_0)` is guaranteed (`H0_THEOREM_AUDIT.md`) and this `2ε` is sharp (Q11–12). Together these give a complete, exact account of when cluster-count comparisons between an algorithmically-sampled set and the true solution space can and cannot be trusted — likely a specialized-corollary-level contribution overall (Q10), but the **exact threshold characterization and sharpness proof were not found anywhere in the literature search** and are this project's own verified contribution.

## 14. Which Phase 2 novelty claims must be weakened or reclassified?

**One, materially**: the asymmetric H₀ theorem, from "NEW THEOREM" (Phase 2 `NOVELTY_CLASSIFICATION.md`) to **"SPECIALIZED COROLLARY (probable)"** (Phase 3, this document + `H0_PRIOR_ART_MATRIX.md`). No other Phase 1 or Phase 2 claim was found to need weakening — the Hausdorff identity and general bottleneck bound were already correctly labeled "known" in Phase 1/2 and remain so; Phase 2's empirical claims (WalkSAT predictor beats baselines, fragmentation is common and regime-dependent) are unaffected by this reclassification and are, if anything, strengthened by Phase 3's independent CDCL replication.

## 15. What is now the strongest defensible central claim of V2?

**Revised from Phase 2's Q11 answer, incorporating Phase 3**: *"Search-algorithm dynamics — across at least two structurally different SAT-solving paradigms (stochastic local search and conflict-driven clause learning) — carry genuine, non-circular, held-out-validated predictive information about where a solver's blind zone will lie, with the specific geometric character of that blind zone (its overlap with other paradigms' blind zones, and the severity of the apparent-fragmentation distortion it induces) depending systematically on both the solver paradigm and the SAT-solvability regime; this behavior is governed by a covering-radius/Hausdorff-distance quantity whose topological reliability consequences are provably bounded (via a very-likely-known but independently re-derived and sharpness-verified stability theorem), not by a claimed new mathematical primitive."* This is more qualified and more defensible than Phase 2's version — it explicitly retracts the overclaimed novelty of the H₀ theorem while *strengthening* the empirical cross-paradigm claim with a second, independent confirmatory dataset.

## 16. The 3–5 strongest results that deserve to appear in the Abstract

1. Two structurally different solver paradigms (WalkSAT, CDCL) each exhibit genuine, held-out, baseline-beating, permutation-significant blind-zone predictability from pre-reveal solver dynamics (AUROC `0.658`/`0.667`).
2. Blind-zone overlap between paradigms is regime-conditional — independent-to-complementary in solution-rich/near-threshold regimes, mildly shared in intermediate regimes — not a single fixed relationship.
3. CDCL produces dramatically more geometrically coherent (less apparently fragmented) samples than WalkSAT at matched coverage — a new, unanticipated, solver-paradigm-level geometric-distortion finding.
4. The corrected, sharp (`+2ε`, proved tight) asymmetric stability theorem for observer-induced fragmentation, honestly framed as very-likely-known-but-independently-verified, with an exact three-regime characterization of when naive cluster-count comparisons can be trusted.
5. The 500-cap-confound correction and the exact discrete distinguishability theorem (Phase 1/2 results), still standing and still among the paper's cleanest, most self-contained contributions.

## 17. What should NOT appear in the Abstract

- Any claim that the asymmetric H₀ theorem is a "new theorem" (per Q10/14 — must be framed as known/specialized, at most "independently re-derived with a novel sharpness result").
- Any portfolio-performance or "combining solvers is worthwhile" claim beyond the narrow, explicitly geometric `ε̂_union` observation (Q6–7) — no runtime or engineering-value claims are supported by this data.
- Overgeneralized "solver dynamics predict blind zones" language without the regime/paradigm qualifiers established in Q3–5, Q8–9 — the honest finding is conditional, not universal.
- Any claim about *why* CDCL fragments less than WalkSAT stated as established fact — `BUDGET_TRAJECTORIES.md`'s explanation is explicitly a hypothesis, not a proven mechanism.

## 18. Is the project ready to draft?

**ONE MORE VALIDATION NEEDED.**

Justification: the mathematical core (Hamming ball theorem, Hausdorff identity, persistence stability with exact sharp constant, exact fragmentation theory) is now thoroughly audited, cross-checked against an aggressive literature search, and honestly labeled — this part is ready. The empirical core has been substantially strengthened by a genuine second solver paradigm with real, working anti-leakage machinery, and the results are coherent and interesting rather than merely "replicated." **What is still missing before drafting**: (a) direct verification of Harker et al. (2019) Proposition 5.6's exact statement — currently a probable-but-unconfirmed classification for the paper's one theorem-shaped claim, and a paper should not go to draft with an unresolved "is this actually citable as known, or do we need to say 'possibly novel'" question hanging over its single mathematical result; (b) the `risk_cdcl_conflicts`/`risk_disc_flips` "wrong-direction" finding recurring in *both* Phase 2 (WalkSAT) and Phase 3 (CDCL) is suspicious enough (two-for-two) that it deserves a specific, small follow-up check (is there a shared confound, e.g. discovery-difficulty correlating with *local S_I density* rather than miss-risk, in both solvers?) before being reported as two independent negative results in a paper, since if it's one shared artifact it should be explained once, not narrated twice as separate surprises. Both are small, bounded, single-session follow-ups — not a new experimental phase — hence "one more validation," not "not ready."

---

## PHASE 3 TERMINAL REPORT

**CDCL**
- Solver: Glucose3 (PySAT 1.9.dev15), genuine CDCL (VSIDS, clause learning, LBD-based restarts), randomized via variable/clause permutation + phase initialization (no direct RNG seed exposed).
- Held-out prediction result: `risk_cdcl_recurrence`, test median AUROC **0.667 [0.647, 0.700]**, permutation `p<0.001`.
- Baselines beaten: random (`0.481`), Hamming-weight (`0.492`), found-neighbor-density (`0.467`), conflicts-to-discovery (`0.471`, near-random — reported as a negative sub-result, not rescued).

**CROSS-SOLVER**
- Overlap: regime-conditional — near-independent overall (ratio `≈1.00`), complementary near-threshold, mildly shared intermediate.
- Cross-prediction: asymmetric — WalkSAT's signal transfers to predicting CDCL's blind zone (`0.625`); CDCL's signal does not transfer to WalkSAT's (`0.526`).
- Portfolio geometry: union improves `ε̂` on `15.6%` of instances; modest, real, regime-patterned, not a performance claim.
- Fragmentation: occurs in both solvers; CDCL shows `4–13×` less apparent fragmentation than WalkSAT at matched coverage — the phase's most striking new finding.
- H₀ theorem: reclassified from "new" to "specialized corollary (probable)"; `+2ε` constant proved sharp, including in the Hamming cube specifically; exact three-regime fragmentation theory newly established and verified (`877/877`, `0` violations).

**Verdict**: **ONE MORE VALIDATION NEEDED** — not ready to draft, not stalled; two small, bounded, single-session checks (Harker et al. Prop. 5.6 direct read; shared-confound check on the conflicts/disc_flips negative result) stand between here and drafting.

**Confirmed**: `~/Downloads/GeometricResolution.pdf` untouched; Phase 1 and Phase 2 files untouched (checksummed in `phase3/PHASE2_FREEZE.md` before any Phase 3 work began); nothing pushed, committed, or uploaded anywhere.
