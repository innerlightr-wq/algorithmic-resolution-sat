# FINAL_VERDICT.md

Synthesizes `AUDIT.md`, `PRIOR_ART.md`, `V2_DEFINITIONS.md`, `EXPERIMENT_DESIGN.md`, `ORIGINAL_EXPERIMENT_AUDIT.md`, `V2_THEOREMS.md`, `V2_OUTLINE.md`.

## Strongest surviving contribution of the January paper

The **empirical separation** of "geometric invariants of `S_I`" from "what an algorithm's found set `A(I)` reveals" — concretely, the documented case (Example 5.1) of a geometrically connected solution space that appears fragmented to a biased sampler, plus the general finding that different algorithm families produce systematically different `ε̂`/coverage profiles on identical instances. This survives essentially intact after the audit; it does not depend on Theorem 2.1, and it is now *strengthened*, not merely preserved, by the persistence-stability theorem (T5) that gives it a rigorous "why."

## Most serious mathematical error

**Theorem 2.1's forward direction is false for the discrete Hamming cube** (proved via explicit counterexample and 308-case brute-force check, `AUDIT.md` §1, `V2_THEOREMS.md` T2). It propagates into Remark 3.3, Conclusion (4), and the Abstract's headline `ε=d/2` claim — the paper's single most quotable line is the one that's wrong. A second, independent bug (Proposition 3.1's `A(I)=∅` convention producing a false unconditional inequality, `AUDIT.md` §2) was also found and is unrelated to Theorem 2.1. Both have clean, fully worked fixes (T1 and a hypothesis restriction, respectively) — this is a **repairable** error, not a paper-invalidating one, but it is real and currently sits in the Abstract.

## Is the covering-radius definition standard?

**Yes, exactly.** `ε̂(A,I)` is, without approximation, the Hausdorff distance between `A(I)` and `S_I` under the Hamming metric (T4, algebraic identity, one line once the subset relation `A(I)⊆S_I` is used); equivalently the covering radius of `A(I)` relative to `S_I`, a subset-relative variant of the textbook coding-theory covering radius (`PRIOR_ART.md` §1–2). "Algorithmic resolution" is new terminology for an old, standard object. This should be stated plainly in V2's introduction rather than left implicit — it costs nothing (the paper's contribution was never really about inventing a metric) and preempts the most obvious referee objection.

## Strongest potentially novel extension

The **persistence-stability connection** (T5: `d_B(Dgm(Rips(A(I))),Dgm(Rips(S_I))) ≤ 2ε̂(A,I)`), applied to SAT solution-space sampling. The theorem itself is known (Cohen-Steiner–Edelsbrunner–Harer 2007; Chazal–de Silva–Oudot 2014) and not novel math — but `PRIOR_ART.md`'s search did not find this specific application (Rips-complex stability as the rigorous backbone for "when can I trust an algorithmically-sampled SAT solution space's apparent clustering") anywhere in the SAT-sampling literature, which is otherwise well-developed on the *bias* side (WalkSAT bias, UniGen near-uniform sampling) but not on the *topological-inference-reliability* side. This is classification C (useful, apparently underused recombination) — a real, if modest, contribution, and the cleanest place for V2 to plant a flag.

## Lowest-hanging rigorous result

**T6** (coverage and covering radius are logically independent without extra structure on `S_I`), proved via two small, explicit, fully verified constructions (a star-plus-outlier set for high-coverage/poor-resolution; a perfect `[7,4]` Hamming code covering the full cube for low-coverage/good-resolution — `V2_THEOREMS.md` T6, scripts and output included). This converts the January draft's *unproved* Remark 3.2 into a *proved* theorem with witnesses, at essentially zero additional research cost — it should be in V2 regardless of which thesis is chosen.

## Strongest feasible experiment

The **predictive blind-zone protocol** in `EXPERIMENT_DESIGN.md` (freeze-before-reveal predictions from non-circular, non-`S_I`-leaking predictors — cluster membership/basin size/backbone estimated from `A(I)` or solver internals only — tested against true `M_A(I)` via Mann–Whitney/AUC, with train/test separation across instances and a Simpson's-paradox stratification check). It is feasible at the paper's own scale (`n≤20`, exhaustive enumeration confirmed to run in well under a second per instance) and directly fixes the circularity problem in the January draft's only comparable result (the biased sampler, which is circular by construction, `ORIGINAL_EXPERIMENT_AUDIT.md` §3). This is not yet run at the proposed `N≥200`/cell scale — it is a designed, ready-to-execute protocol, not a result.

## What should be removed from V2

- The Abstract/Conclusion's unqualified `ε=d/2` "universal upper bound" language (replace with `⌈d/2⌉`, and demote from headline to background fact).
- §6.3 "Alignment and Residual" — an unsupported analogy to a different paper's unrelated numeric result, with no computation performed in this paper to back it (`AUDIT.md` §3).
- The "Proposition 6.1" label on what is actually an informal, unproved modeling assumption (`A(I)≈S_I∩supp(μ)`) — either replace with the accessibility-field formulation (`V2_DEFINITIONS.md` §1.3) or explicitly relabel as an assumption.
- `Δ_A(r)` as the *primary* distortion measure — keep as an illustrative special case only, demoted in favor of bottleneck distance (T5).
- The biased-sampler result as the paper's *sole* evidence for "predictable blind zones" — keep it, but explicitly relabel it as a circular sanity check, not primary evidence (`ORIGINAL_EXPERIMENT_AUDIT.md` §3).

## What should be retained

- The core empirical separation of geometric-invariant vs. observer-dependent structure (see "strongest surviving contribution" above).
- Definitions 2.1–2.6, 3.1–3.5 essentially unchanged (only the `A(I)=∅` edge case needs a hypothesis fix, not a redefinition).
- Proposition 3.1, restricted to `A(I)≠∅` (true and correctly proved on that branch).
- The (⇐) direction of Theorem 2.1 (correct, general, no fix needed) and the honest §7.4/§8 limitations sections, which were already appropriately hedged and required no correction.
- All raw Tables 1–4 data as *measurements* — only their interpretation at `α=2.0` needs the cap-confound caveat (`ORIGINAL_EXPERIMENT_AUDIT.md`), not the numbers themselves.

## Revision or substantially new paper?

**Substantially new paper that supersedes and explicitly cites the January draft as prior work**, not a same-title erratum. Reasoning: the two largest additions (T5's stability-theorem framing and the redesigned Phase 5 predictive experiment) are each large enough to be a paper's main contribution on their own, and bundling them with a headline-theorem correction in a "v2/corrected" reissue would make the correction harder to isolate and verify independently — worse for scientific hygiene than a clean new paper with an explicit "supersedes/corrects [January 2026 preprint]" note and a short erratum-style paragraph isolating exactly what was wrong (Theorem 2.1, Remark 3.3, Conclusion (4), Prop. 3.1's edge case) for anyone who only wants the correction.

---

## Terminal summary

- **Original-paper status**: one theorem (2.1) false as stated in general metric spaces (true only for midpoint/geodesic spaces), with three downstream statements (Remark 3.3, Conclusion (4), Abstract) depending on the false direction; one independent bug in Proposition 3.1's `A(I)=∅` convention; empirical machinery and raw data intact.
- **Theorem correction**: `B_ε(x)∩B_ε(y)=∅ ⟺ ε<D/2` (general metric spaces) → `ε≤⌈D/2⌉` for the discrete Hamming cube specifically (general form requires a midpoint/geodesic-space hypothesis the paper never stated).
- **Strongest surviving idea**: empirical separation of intrinsic solution-space geometry (`S_I`) from algorithm-observed geometry (`A(I)`), now backed by a real stability theorem rather than assertion.
- **Strongest V2 direction**: persistence-diagram stability under Hausdorff distance (T5), applied to SAT solution-space sampling — known math, apparently new application.
- **Lowest-hanging rigorous result**: T6, coverage/resolution logical independence, proved by two explicit small constructions, already verified computationally.
- **Proposed decisive experiment**: freeze-before-reveal predictive blind-zone protocol (`EXPERIMENT_DESIGN.md`), non-circular predictors, train/test split across instances, `N≥200` instances/cell — designed, not yet run at scale.
- **Files created**: see directory listing below.
- **Original paper and all repositories**: confirmed untouched — `~/Downloads/GeometricResolution.pdf` was only read (`pdftotext`, `pdfinfo`), never written to; no `git`/network-push commands were issued anywhere in this session; all new files live under `~/scratch/sat-algorithmic-resolution-v2-audit-2026-09-28/`.
