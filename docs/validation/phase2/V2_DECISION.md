# V2_DECISION.md — Phase 2 final decision document

Synthesizes all Phase 2 deliverables. Answers the 13 mandated questions directly.

## 1. What is the exact corrected Hamming-ball theorem?

For `x,y∈{0,1}^n`, `D=d_H(x,y)>0`, real `ε>0`:
- **Open balls**: `B_ε(x)∩B_ε(y)=∅ ⟺ ε≤⌈D/2⌉`.
- **Closed balls**: `B̄_ε(x)∩B̄_ε(y)=∅ ⟺ ε<⌈D/2⌉`.

Proved from the combinatorial lemma `min_z max(d(x,z),d(y,z))=⌈D/2⌉`; verified over 45,393 `(n,D,ε)` cases, `n=1..10`, zero mismatches (`HAMMING_BALL_THEOREM.md`). The January paper's `ε<D/2` has **two** distinct defects: a magnitude error for odd `D` (Phase 1) and a boundary strictness error present for *every* `D`, including even `D` (identified precisely in this phase).

## 2. Is `ε̂` exactly Hausdorff distance under the stated assumptions?

**Yes, exactly**, whenever `∅≠A(I)⊆S_I`: `ε̂(A,I)=d_Haus(A(I),S_I)` (one-line proof from the definitions, `HAUSDORFF_IDENTITY.md`). Not novel math. The `A(I)=∅` case is **not** literally Hausdorff distance (would be `+∞` under the standard convention) — recommend treating it as a categorical flag, not a numeric sentinel.

## 3. What exact persistence-stability theorem applies, with what constant?

`d_B(Dgm_k(Rips(A(I))),Dgm_k(Rips(S_I))) ≤ 2ε̂(A,I)`, for every homological dimension `k`, under the edge-threshold-`≤r` Rips convention (matching the paper's own `C_S(r)`). Constant confirmed as `2`, not `1`, via an explicit interleaving construction derived here and cross-checked against Chazal–de Silva–Oudot (2014) — no geodesic/length-space hypothesis needed. **Additionally**, a sharper, asymmetric, H₀-specific result was proved (not merely cited): `A(I)` can never show a false merge relative to `S_I` at the same radius (zero slack), and any apparent fragmentation is guaranteed to resolve once the radius is loosened by exactly `2ε̂` (`PERSISTENCE_STABILITY.md` §3). Both bounds were validated with **zero violations** on 349 real SAT solution spaces (Part 10).

## 4. What does small `ε̂` actually guarantee about inferred topology?

Precisely: bottleneck distance between the diagrams is `≤2ε̂` (all dimensions), and for connectivity specifically, any merge visible in `A(I)` at radius `r` is guaranteed already true in `S_I` at radius `r` (no false merges, ever), while any fragmentation visible in `A(I)` is guaranteed to disappear by radius `r+2ε̂`. It does **not** guarantee cluster sizes, shapes, exact membership, or higher-dimensional (loop/void) features are preserved at the same tight rate — those require the weaker general `2ε̂` bound only, and no reconstruction-type (homotopy-equivalence) guarantee is available without extra regularity `S_I` is not known to have.

## 5. Can coverage and resolution provably diverge?

**Yes, proved by two explicit, verified, asymptotic families** (not isolated points): a star-plus-outlier family with coverage`→1` while `ε̂/n→1` simultaneously, and a perfect-Hamming-code family with coverage`→0` while `ε̂` stays constant at `1` (verified exactly, via syndrome decoding, up to `n=63`, code size `2^57`). No deterministic inequality between coverage and `ε̂` can hold without extra structural assumptions on `S_I` (`COVERAGE_RESOLUTION_THEOREM.md`).

## 6. Can a solver's blind zone be predicted before ground truth is revealed?

**Yes, for the non-circular, prospectively-well-posed version of the question this phase formalized**: a risk score (`risk_basin`, based on WalkSAT restart-convergence counts, computed from solver trajectories alone) predicts local density of subsequently-revealed missed solutions, frozen before reveal via a genuine two-process (separate script invocations, hash-verified) Stage A/Stage B pipeline.

## 7. Does the predictor beat trivial baselines on genuinely held-out instances?

**Yes.** Test-split (touched once, after train-only model selection) median AUROC `0.658` `[0.636,0.685]` vs. random `0.504` and Hamming-weight `0.519`, non-overlapping CIs, instance-level permutation test `p<0.001` (random-baseline sanity check correctly non-significant, `p=0.35`). Effect survives stratification by regime, `n`, and `\|S_I\|` tercile (`EXPERIMENT_RESULTS.md` §4–6, `FAILURE_ANALYSIS.md` criteria 1–2, 6).

## 8. How common is observer-induced fragmentation?

**51.3% of 349 real test instances overall**, but sharply regime-dependent: **99.2%** in solution-rich regimes (`α=2.5`), 42.4% intermediate, only **9.0%** near the SAT/UNSAT threshold. Not rare in aggregate, but not uniform — any V2 claim must carry the regime qualifier.

## 9. Does `ε̂` explain geometric/topological distortion better than raw coverage?

**Nuanced, honestly reported finding, not a clean yes.** Empirically, `ε̂` and coverage are almost perfectly anti-correlated for this solver+instance ensemble (`ρ=-0.975`) — `ε̂` is *not* adding large amounts of new information beyond coverage in the typical case. However, conditioning on the middle coverage tercile, `ε̂` still strongly predicts fragmentation (`ρ=0.687`, `p≈10⁻³⁴`) — so `ε̂` is not *fully* redundant with coverage, particularly for the fragmentation-prediction task specifically, even though its marginal correlation with coverage is very high. **V2 should state both halves of this finding together, not just the favorable half.**

## 10. Which results are established mathematics versus genuinely new results from this project?

See `NOVELTY_CLASSIFICATION.md` for the full table. Summary: Hausdorff identity and the general `2ε̂` bottleneck bound are **KNOWN MATHEMATICS**, correctly not claimed novel. The corrected Hamming-ball theorem, the H₀-specific asymmetric correspondence theorem, the coverage/resolution family constructions, and every empirical result (predictor beating baselines, fragmentation frequency/regime-dependence, budget trajectories, the `ε̂`-vs-coverage nuance) are genuinely produced by this project, at the "elementary theorem" / "new computational result" level, not deep new mathematics.

## 11. What is the strongest defensible central claim for V2?

**Thesis D, sharpened**: *"Covering radius (`ε̂`, exactly the Hausdorff distance between found and true solution sets) provably controls the reliability scale of connectivity/persistence structure inferred from an algorithmically-sampled SAT solution set — a known stability theorem, here specialized to a sharp, asymmetric, zero-slack-in-one-direction form and validated with zero violations on real solution spaces — and, separately but compatibly, solver-internal search dynamics carry genuine, non-circular, held-out-validated predictive information about where a solver's blind zone will lie, beyond what raw coverage or point geometry alone provide."* This combines the strongest proved math (Q3/Q4) with the strongest held-out empirical result (Q6/Q7), each independently supported, not merely asserted together.

## 12. Is there enough here for a substantially new paper, or should this instead be a corrected revision of the January paper?

**Substantially new paper**, reaffirming Phase 1's `FINAL_VERDICT.md` recommendation and strengthening it: this phase adds a real theorem (H₀ asymmetric correspondence), a real held-out predictive result with proper anti-leakage machinery (something the January draft entirely lacked), a systematic (not anecdotal) fragmentation-frequency characterization, and an honest accounting of where the story is more nuanced than a clean win (`ε̂`-vs-coverage, budget-scale limits). This is comfortably more than an erratum's worth of content, and — per Phase 1's reasoning — bundling it with the Theorem 2.1 correction would make the correction harder for readers to isolate.

## 13. What result, if obtained next, would most increase the significance of the work?

**A second, structurally different solver family (CDCL with randomized restarts, as the original task scoped as a stretch goal) reproducing the `risk_basin`-style predictive result**, to test whether the finding is specific to local-search dynamics (basin-of-attraction structure is a natural WalkSAT concept) or generalizes to systematic-search solvers where "basin size" has no direct analogue and a different solver-dynamics feature (e.g. backtrack-count near a found solution, VSIDS activity) would need to play the same role. A positive result there would upgrade the central claim from "WalkSAT-specific" to "a genuine cross-paradigm phenomenon," which is exactly the generalization the January draft's own Contribution (2) originally gestured at but only tested with sampling-based methods.
