# RESEARCH_FREEZE.md — Phase 4, Part 17

## 1. Manifest of all Phase 1–4 results

| Phase | Directory | Core content |
|---|---|---|
| 1 | `/` (top-level `.md` files) | Mathematical/prior-art audit of the January 2026 paper: Theorem 2.1 error, Proposition 3.1 bug, Hausdorff identity, coverage/resolution independence, 500-cap confound in the original experiments, prior-art map |
| 2 | `phase2/` | Hamming-ball theorem (exact, sharp-boundary corrected), Hausdorff identity re-derivation, general persistence-stability bound + asymmetric H₀ specialization, coverage/resolution families, freeze-before-reveal WalkSAT predictive experiment (`AUROC≈0.658`), 349-instance fragmentation-frequency/regime characterization |
| 3 | `phase3/` | CDCL/Glucose3 replication (`AUROC≈0.667`), cross-solver blind-zone geometry (overlap, cross-prediction, portfolio, budget trajectories — the original, now partially superseded, findings), H₀ theorem sharpness proof, first (hedged, unconfirmed) prior-art search pointing to Harker et al. |
| 4 | `phase4/` (this phase) | Harker et al. Prop. 5.6 confirmed by direct reading (theorem reclassified DIRECT COROLLARY); cross-solver directional-transfer asymmetry confound-audited and **retracted**; fragmentation difference **replicated and strengthened** across the full test set; new paired `ε̂` reversal finding; final claim hierarchy and Abstract-ready result set |

## 2. Exact dataset/scripts that will support V2

- **Instances**: `phase2/data/instances_{train,test}.json` (`720` random-3-SAT instances, `n∈\{16,18,20\}`, `α∈\{2.5,3.5,4.2\}`, no solution cap).
- **WalkSAT**: `phase2/scripts/{walksat_solver,run_stage_a,run_stage_b}.py`, results in `phase2/data/stage_a_predictions_*.json` (hashed), `phase2/data/stage_b_results_*.json`.
- **CDCL**: `phase3/scripts/{cdcl_stage_a,cdcl_stage_b,pysat_common}.py` (Glucose3 via PySAT), results in `phase3/data/cdcl_stage_a_predictions_*.json` (hashed), `phase3/data/cdcl_stage_b_results_*.json`.
- **Topology/persistence**: `phase2/scripts/topology_utils.py` (vectorized cluster-spectrum computation), `phase2/data/part10_results.json` (WalkSAT, `349` instances), `phase4/data/fragmentation_replication.json` (both solvers, `349` instances, the audited headline comparison).
- **Theorem verification**: `phase2/scripts/hamming_ball_theorem_verify.py`, `phase3/scripts/h0_sharpness_extremal.py`, `phase3/scripts/fragmentation_theorem_verify.py`.
- **Cross-solver confound analysis**: `phase4/scripts/{build_cross_solver_dataset,confound_and_conditional_analysis,fragmentation_replication}.py`.

## 3. January-paper statements superseded / corrected

| Original statement | Status |
|---|---|
| Theorem 2.1, `ε<D/2` distinguishability threshold | **Corrected**: `ε≤⌈D/2⌉` (open balls), with a distinct boundary-strictness defect identified beyond the magnitude error |
| Remark 3.3, Conclusion (4), Abstract's "`ε=d/2`" | **Corrected** — depended on the false direction of Theorem 2.1 |
| Proposition 3.1, `A(I)=∅` convention | **Corrected** — convention created a false unconditional inequality; fixed by restricting the hypothesis |
| "Algorithmic resolution" presented as a new quantity | **Corrected framing** — `ε̂` is exactly the Hausdorff distance / subset-relative covering radius (known math), retained only as domain-facing terminology, introduced *after* the identity is stated |
| Table 1–2 coverage/resolution at `α=2.0` | **Corrected interpretation** — substantially a 500-solution-cap truncation artifact, not (only) algorithmic failure (Phase 1 reconstruction) |
| `Δ_A(r)` as the primary distortion diagnostic | **Corrected/demoted** — not stable on its own; replaced by bottleneck-distance/exact `C_A` vs. `C_S` theory as the primary tool |
| Biased-sampler result as primary evidence for "predictable blind zones" | **Corrected/reframed** — circular by construction (Phase 1); superseded by the freeze-before-reveal WalkSAT/CDCL predictive experiments (Phase 2/3), which are non-circular |
| §6.3 "Alignment and Residual" cross-paper analogy | **Removed** — unsupported, no computation performed in the original paper to back it |

## 4. Claims retained unchanged

- Definitions 2.1–2.6, 3.1–3.5 (metric space, resolution, SAT solution space, Hamming metric, cluster spectrum, found solutions, blind zone, coverage) — all structurally sound.
- Proposition 3.1, restricted to `A(I)≠∅` (true and correctly proved on that branch).
- The (⇐) direction of Theorem 2.1 (correct, general, no fix needed).
- The core empirical claim that different algorithms exhibit systematically different resolution profiles and that blind zones are algorithm-specific and structured (now vastly strengthened by non-circular held-out validation across two solver paradigms).

## 5. Claims corrected (see §3)

## 6. New results (not present in the January paper at all)

- Held-out, non-circular, anti-leakage-verified blind-zone predictability for both WalkSAT and CDCL.
- Systematic (349-instance, regime-stratified) fragmentation-frequency characterization, superseding the original single hand-picked example.
- The exact, sharp, correctly-attributed asymmetric H₀ stability theorem and its Hamming-cube-specific extremal sharpness construction.
- The matched-coverage paired observer test: WalkSAT/CDCL trade off oppositely on `ε̂` vs. fragmentation — the project's strongest single empirical demonstration of its own core theoretical distinction (coverage/resolution vs. connectivity independence), and this phase's own original contribution (not present in Phase 3's framing).
- Coverage/resolution logical independence as explicit, verified, asymptotic parameterized families (not merely isolated hand-built examples).

## 7. Known limitations (consolidated across all four phases)

- Ground truth requires exhaustive enumeration, limiting `n≤~22` — a hard, acknowledged ceiling on what any version of this experiment can validate against true `S_I` (January paper §8.1, never disputed).
- Only two solver implementations tested (one WalkSAT configuration, one CDCL solver/Glucose3) — the paired-observer and fragmentation results are about *these specific, audited implementations*, not "local search vs. systematic search" as general paradigms (`PAIRED_OBSERVER_TEST.md` caveat).
- The cross-solver directional-transfer asymmetry, once a candidate headline finding, is now a **retracted, confound-explained result** — reported in this freeze as a methodological lesson, not a positive contribution.
- `ε̂`/coverage were found empirically near-redundant for the WalkSAT-only analysis in Phase 2 (`ρ=-0.975`), a nuance that must be carried into any V2 discussion of the coverage/resolution distinction's practical (as opposed to worst-case) significance — though `PAIRED_OBSERVER_TEST.md`'s cross-solver finding shows the two diagnostics *can* and *do* diverge meaningfully once a second solver paradigm is introduced.
- The `+2ε` sharpness result's broader novelty status (is a Hamming-cube-specific construction "obvious" to a TDA specialist, even if not found written down?) remains honestly uncertain (`SHARPNESS_NOVELTY_AUDIT.md`) — stated as a modest, narrow-scope contribution, not oversold.

## Recommendation

**No additional experiments recommended** beyond what this freeze documents, unless a specific issue arises during drafting or external review (per the task's own stop condition). See `FINAL_DECISION.md` for the exact remaining status.
