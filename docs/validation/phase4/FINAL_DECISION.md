# FINAL_DECISION.md — Phase 4 final decision

## 1. What exactly does Harker et al. Proposition 5.6 prove?

For `(X,d)` a finite metric space and `Y⊂X` a `δ`-approximation (every `x∈X` has some `y∈Y` with `d(x,y)≤δ` — exactly our `A⊆S`, `δ=ε`), the persistence modules `M^R(Y)`, `M^R(X)` (Vietoris–Rips, their convention: edge iff `d≤2t`) are `(τ,σ)`-interleaved with `τ(t)=t` (zero shift, via the inclusion-induced map) and `σ(t)=t+δ` (shift `δ` in their parameter, via a nearest-point map). Confirmed by direct reading of the full proof (`HARKER_PROP_5_6_DIRECT_AUDIT.md`).

## 2. Is our asymmetric H₀ recovery theorem known, a direct corollary, a specialized corollary, or materially different?

**Direct corollary**, confirmed. Translating their `t↔r/2` convention, Proposition 5.6(i) restricted to `H_0` is exactly our claims (a) (zero-shift inclusion map) and (b) (`+2ε` recovery, since their `t`-shift `δ` becomes a radius-shift `2δ=2ε`). Not "probably" or "very likely" as Phase 3 hedged — **confirmed by direct primary-source reading**.

## 3. Is `+2ε` sharpness known in general metric spaces?

The *general symmetric* (Gromov–Hausdorff) factor-of-2 tightness is discussed in the TDA literature. **No source located anywhere in this project's searches (Phase 2, 3, or 4) discusses sharpness of the specific asymmetric, subset-case bound** — Harker et al.'s paper contains no sharpness/tightness/optimality discussion near Proposition 5.6 (confirmed, full-text search).

## 4. What can safely be said about Hamming-cube sharpness novelty?

**"We did not locate an explicit Hamming-cube sharpness statement."** The extremal construction is a real, verified, self-contained contribution (7 parameter combinations, exact), but the underlying *technique* (worst-case additive triangle-inequality construction) is likely a routine idea to specialists — the honest claim is realization-and-verification in this specific discrete setting, not invention of a new technique (`SHARPNESS_NOVELTY_AUDIT.md`).

## 5. Does WalkSAT → CDCL cross-prediction survive plausible confound controls?

**No.** Three independent methods — a joint conditional model (`CONDITIONAL_PREDICTION.md`: confounds-only AUROC `0.946`/`0.756`(w/o the strongest confound), paired improvement from adding the risk score `≈0`), residualization (`RESIDUALIZATION.md`: residual per-instance AUROC `0.441`, below chance), and coverage-matched stratification (`STRATIFIED_ASYMMETRY.md`: `0.625→0.556` under matching) — all converge on **substantially confounded**, chiefly by a coverage-calibration mismatch between the two solvers' tested budgets.

## 6. Does CDCL → WalkSAT remain near baseline?

**Yes, throughout** — it started near baseline (`0.526`) and stays there or drifts slightly *toward* baseline under every control tested (coverage-matched: `0.546`).

## 7. Is the asymmetry best interpreted as solver-specific dynamics, shared rarity, or unresolved?

**Neither positive interpretation is supported — it should be reported as confounded**, primarily by coverage mismatch, with the "rare solution" hypothesis specifically tested and also not supported at the within-instance level (`RARE_SOLUTION_TEST.md`: per-instance AUROC of risk→joint-discoverability `0.533`/`0.500`, both ≈chance despite strong *pooled* correlations that turn out to be a between-instance artifact).

## 8. Is conjugacy language justified?

**No**, and less so than before this phase's audit (`CONJUGACY_FILTER.md`).

## 9. Is semiconjugacy language justified?

**No**, same reasoning.

## 10. Does the 4–13× fragmentation difference survive aggressive audit?

**Yes, and it is strengthened.** Replicated across `349` held-out instances (not `2`): median ratio `11.6×` (`95% CI [9.6,13.3]`), `p=5.2×10⁻³¹` paired, holds in every regime/`n`/coverage-band stratum, and — critically, unlike the cross-prediction asymmetry — **survives coverage-matching** (`p=2.4×10⁻⁷`).

## 11. At matched coverage on the SAME instance, does solver identity significantly change observed geometry?

**Yes, decisively, in both directions simultaneously**: WalkSAT achieves significantly better `ε̂` (`p=5.1×10⁻³⁸`) while showing dramatically worse fragmentation (`p=5.2×10⁻³¹`) than CDCL, on the same `349` paired instances. This is the project's cleanest empirical result (`PAIRED_OBSERVER_TEST.md`).

## 12. What is the strongest central claim?

**Thesis B**: *"Distinct solver paradigms produce systematically different observational geometries of the same SAT solution spaces"* — grounded in the paired `ε̂`/fragmentation reversal and the replicated fragmentation gap, not in the now-retracted cross-prediction asymmetry (`FINAL_CLAIM_HIERARCHY.md`).

## 13. The 3–5 Abstract-level results

See `ABSTRACT_RESULTS.md` in full; headline five: (1) the matched-coverage `ε̂`/fragmentation trade-off; (2) held-out blind-zone predictability for both solvers; (3) the corrected exact Hamming-ball theorem; (4) the correctly-attributed, sharp persistence-stability bound; (5) proved coverage/resolution logical independence.

## 14. What should explicitly NOT be claimed?

Cross-solver directional transfer / shared accessibility structure; conjugacy/semiconjugacy; H₀-theorem novelty (it is a direct corollary); any complexity-theoretic implication; any portfolio-performance claim beyond the narrow geometric `ε̂_union` observation; the "rare solution sensing" interpretation. Full list in `ABSTRACT_RESULTS.md`.

## 15. What January-paper statements must be corrected or removed?

See `RESEARCH_FREEZE.md` §3 — Theorem 2.1 and its three downstream dependents, Proposition 3.1's `A(I)=∅` convention, the "algorithmic resolution as new quantity" framing, the `α=2.0` cap-truncation misinterpretation, `Δ_A(r)` as primary diagnostic, the circular biased-sampler evidence, and the unsupported §6.3 cross-paper analogy.

## 16. What results are ready for publication?

All Tier 1 (proved math, correctly attributed) and Tier 2 (new computational results surviving this phase's audit) items in `FINAL_CLAIM_HIERARCHY.md` — this is the great majority of the project's output. Only the cross-solver directional-transfer claim is excluded.

## 17. Are there any blockers remaining before drafting?

**No specific blocker remains.** The two substantive questions this phase was commissioned to resolve (Harker et al.'s exact relationship; genuineness of the WalkSAT/CDCL asymmetry) are both **resolved** — the first definitively (direct corollary, confirmed), the second definitively in the negative (confounded, confirmed by three convergent methods, with a genuine, strong, replicated positive result — the paired `ε̂`/fragmentation reversal — emerging in its place as this phase's own contribution. Everything needed to write an honest, well-supported, appropriately-hedged V2 paper is now in hand.

## 18. Final status

# READY TO DRAFT

---

## PHASE 4 FINAL TERMINAL REPORT

**PRIOR ART**
- Harker Prop. 5.6 relationship: **DIRECT COROLLARY** (confirmed by direct primary-source reading; our asymmetric H₀ theorem, translated through their `t↔r/2` convention, is exactly their Proposition 5.6(i) restricted to `H_0`).
- `+2ε` sharpness status: general factor-of-2 tightness is known (symmetric setting); **no Hamming-cube-specific or asymmetric-subset-case sharpness statement was located anywhere** — our extremal construction stands as an independently-verified, narrow-scope, honestly-scoped contribution.

**ASYMMETRY**
- Raw cross-prediction: `W→C=0.625`, `C→W=0.526`.
- Controlled result: **confounded** — confounds-only models reach `0.946`/`0.875` AUROC; adding the solver-specific risk score improves discrimination by `≈0` in both directions; coverage-matching alone shrinks `W→C` to `0.556`.
- Interpretation: **directional predictive asymmetry, substantially explained by a coverage-calibration mismatch between the two solvers' tested budgets — not evidence of solver-specific dynamical transfer.**

**OBSERVER EFFECT**
- Matched-coverage WalkSAT vs. CDCL: tested on `349` held-out instances, paired by identical `S_I`.
- Fragmentation result: WalkSAT median `11.6×` (`95% CI [9.6,13.3]`) more excess apparent fragmentation than CDCL; **survives coverage-matching** (`p=2.4×10⁻⁷`).
- `ε̂`/H₀ result: WalkSAT achieves significantly **better** `ε̂` (`p=5.1×10⁻³⁸`) than CDCL on the same paired instances — the two solvers trade off **oppositely** on these two logically-independent diagnostics.

**CLAIMS**
- Strongest theorem-level statement: the corrected, exact, sharp Hamming-ball/persistence-stability theorem cluster (Tier 1, correctly attributed to Harker et al. for the core result, independently verified for sharpness).
- Strongest computational result: the matched-coverage paired `ε̂`/fragmentation reversal (`PAIRED_OBSERVER_TEST.md`).
- Strongest interpretation: distinct solver paradigms produce systematically different observational geometries of the same solution space (Thesis B).
- Claims rejected: cross-solver dynamical transfer, conjugacy/semiconjugacy, H₀-theorem novelty, rare-solution sensing, any complexity-theoretic or portfolio-performance claim.

**FINAL STATUS**

# READY TO DRAFT

**PRESERVATION**
- `~/Downloads/GeometricResolution.pdf`: unchanged (verified by checksum before and after this phase).
- Phases 1–3: unchanged (Phase 3 checksummed in `phase4/PHASE3_FREEZE.md` before any Phase 4 work began; verified identical after).
- Nothing pushed, committed, or uploaded anywhere.
