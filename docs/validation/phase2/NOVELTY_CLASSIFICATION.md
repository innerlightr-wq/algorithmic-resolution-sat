# NOVELTY_CLASSIFICATION.md — Phase 2, Part 13

Labels: **KNOWN MATHEMATICS**, **KNOWN SAT/CSP RESULT**, **NEW SPECIALIZATION/INTERPRETATION**, **NEW THEOREM**, **NEW COMPUTATIONAL RESULT**, **CONJECTURE**, **NEGATIVE RESULT**. Per instruction, the Hausdorff identity and general persistence-stability theorem are **not** labeled new anywhere below.

| Result | Label | Basis |
|---|---|---|
| Exact Hamming-ball theorem (`ε≤⌈D/2⌉` open, `ε<⌈D/2⌉` closed) | **NEW THEOREM** (elementary; a correction of a specific published error, not a discovery of new deep mathematics) | `HAMMING_BALL_THEOREM.md`, self-contained proof + 45,393-case brute-force verification |
| `ε̂(A,I) = d_Haus(A(I),S_I)` | **KNOWN MATHEMATICS** — explicitly not claimed novel per instruction | `HAUSDORFF_IDENTITY.md` |
| General Rips bottleneck bound `d_B≤2ε̂`, all `k` | **KNOWN MATHEMATICS** — explicitly not claimed novel per instruction (Chazal–de Silva–Oudot 2014 + isometry theorem, applied by direct substitution) | `PERSISTENCE_STABILITY.md` §2 |
| Asymmetric H₀-specific correspondence (no-false-merge, exact; guaranteed-re-merge at `2ε̂`) | **NEW THEOREM** (elementary specialization exploiting the `A(I)⊆S_I` structure; not found in the literature search performed, but built from standard chain-argument technique, not new proof technology) | `PERSISTENCE_STABILITY.md` §3, verified 100/100 synthetic instances + 0/349×20 violations on real SAT data (Part 10) |
| Coverage/resolution logical independence, as parameterized families (not isolated points) | **NEW COMPUTATIONAL RESULT** (the underlying coding-theory facts — perfect Hamming codes, covering radius — are **KNOWN MATHEMATICS**; the *combination into an explicit, verified, asymptotic two-family proof of independence, applied to the SAT-resolution question*, is the new part) | `COVERAGE_RESOLUTION_THEOREM.md` |
| Solver-dynamics-based blind-zone prediction beats baselines on held-out instances (`risk_basin`, AUROC `0.658`, `p<0.001`) | **NEW COMPUTATIONAL RESULT** | `EXPERIMENT_RESULTS.md` §4–5 |
| Fragmentation frequency (51.3% overall, regime-dependent 9–99%) across 349 real instances | **NEW COMPUTATIONAL RESULT** (supersedes the January paper's single anecdotal example with a systematic frequency measurement) | `EXPERIMENT_RESULTS.md` §8 |
| Stability theorem validated with zero violations on real SAT solution spaces | **NEW COMPUTATIONAL RESULT** (validates KNOWN MATHEMATICS empirically on a new domain, does not alter the math itself) | `EXPERIMENT_RESULTS.md` §8 |
| `ε̂` near-redundant with coverage empirically (`ρ=-0.975`) but not fully redundant for fragmentation prediction | **NEW COMPUTATIONAL RESULT** (an honest limitation/nuance, not a positive claim) | `FAILURE_ANALYSIS.md` §4 |
| Budget trajectories showing fragmentation resolution is scale-dependent (works for moderate `\|S_I\|`, stalls for very large `\|S_I\|`) | **NEW COMPUTATIONAL RESULT** (partial negative finding) | `EXPERIMENT_RESULTS.md` §9, `FAILURE_ANALYSIS.md` §6 |
| SAT solution-space clustering exists intrinsically (Achlioptas–Ricci-Tersenghi) | **KNOWN SAT/CSP RESULT** (Phase 1 `PRIOR_ART.md` §5; presupposed, not re-derived, by the fragmentation analysis here) | — |
| Local-search/WalkSAT sampling is non-uniform/biased | **KNOWN SAT/CSP RESULT** (Phase 1 `PRIOR_ART.md` §5) | — |

## The one integrated claim being tested, and its classification

Per the task's framing, the potential contribution under test is the **integration**:
```
solver-dependent sampling  +  Hausdorff/covering resolution  +  topology reliability  +  prospective solver accessibility
```
Each piece individually: solver-dependent sampling bias (**KNOWN SAT/CSP RESULT**), Hausdorff/covering resolution (**KNOWN MATHEMATICS**), topology reliability via persistence stability (**KNOWN MATHEMATICS**, general form; **NEW THEOREM** for the sharper H₀-specific asymmetric form), prospective solver accessibility prediction (**NEW SPECIALIZATION/INTERPRETATION** of the general accessibility-field idea from `V2_DEFINITIONS.md`, made concrete and non-circular in `ACCESSIBILITY_FRAMEWORK.md`).

**The integration itself, demonstrated end-to-end on real data with a held-out, non-circular, statistically significant predictive result (Part 6–9) and a zero-violation empirical confirmation of the stability bound on real solution spaces (Part 10), is the project's actual, defensible, novel contribution — classified as NEW COMPUTATIONAL RESULT built on top of KNOWN MATHEMATICS and KNOWN SAT/CSP RESULTS, plus one small NEW THEOREM (the H₀-specific asymmetric correspondence) that made the integration sharper than a naive citation of the general bottleneck bound would have.**

No single piece is being oversold as new mathematics; the integration and its empirical validation are what earns the "new" label.
