# ASYMMETRY_DEFINITION.md — Phase 4, Part 5

## What was observed (restated precisely, no interpretation)

On the Phase 2/3 test split, using `risk_basin(y) = -\text{basin}(y)` (WalkSAT-derived, computed from WalkSAT's own trajectory only) as a predictor and `\text{has\_missed\_by\_CDCL\_neighbor}(y)` (retrospective, computed from CDCL's blind zone `M_C(I)` after reveal) as the target, for `y∈A_W(I)`:

`\text{AUROC}(risk\_basin(y) \to \text{CDCL blindness}) ≈ 0.625`, `\text{CI}=[0.599,0.667]`, excluding `0.5`.

The reverse direction — `risk_cdcl_recurrence(y) = -\text{recurrence}(y)` (CDCL-derived) predicting `\text{has\_missed\_by\_WalkSAT\_neighbor}(y)` for `y∈A_C(I)` — gives `\text{AUROC}≈0.526`, `\text{CI}=[0.487,0.567]`, including `0.5`.

This is **directional predictive asymmetry**: one direction of cross-prediction (WalkSAT-derived score → CDCL's blind zone) carries statistically credible signal; the other (CDCL-derived score → WalkSAT's blind zone) does not, on the raw (unadjusted, no-confound-control) analysis performed in Phase 3.

## What this is *not* being called, and why

Per instruction, none of the following labels are used unless a later part of this phase produces specific supporting evidence beyond the raw AUROC gap:
- **Causality** — an AUROC gap between two predictive directions says nothing about which solver's dynamics *cause* the other's difficulty; both scores are functions of a instance/solution pair that is fixed before either solver runs.
- **Hierarchy** — no ordering between the solvers ("WalkSAT dynamics are more fundamental than CDCL's") is established by a predictive-transfer asymmetry alone.
- **Conjugacy / semiconjugacy** — these are precise dynamical-systems terms requiring an explicit state-space map `h` intertwining two dynamical systems' transition maps (`h∘T_W=T_C∘h`); nothing in the current data constructs or tests such a map. Addressed formally, and ruled out at the current evidence level, in `CONJUGACY_FILTER.md`.
- **Intrinsic difficulty** — this presumes the asymmetry reflects a property of `S_I` itself rather than of the two specific measurement procedures (`basin`/`recurrence`) used; `RARE_SOLUTION_TEST.md` tests this specific hypothesis rather than assuming it.

## The narrow statistical question this phase actually answers

> **Does `risk_basin(y)` (WalkSAT-derived) retain predictive information about CDCL blindness after controlling for plausible shared instance- and solution-level confounds — Hamming weight, distance to the other solver's observed set, local (post-reveal) solution density, instance regime, `n`, `|S_I|`, solver coverage, `ε̂`, and class-imbalance/calibration differences between the two solvers' risk scores?**

If the answer is yes (signal survives adjustment), the asymmetry reflects something about the **specific solver dynamics** that basin-counting captures, beyond generic geometric confounds — a positive, non-trivial, still appropriately narrow finding, and the strongest evidence this project can offer for "shared accessibility structure" or "directional transfer" language (weakest defensible terms, per `CONJUGACY_FILTER.md`). If the answer is no (signal explained away by confounds), the original raw asymmetry should be reported as **confounded**, and any interpretive language about it retracted accordingly. `CONFOUND_AUDIT.md` through `RESIDUALIZATION.md` (Parts 6–9) carry out this test; `RARE_SOLUTION_TEST.md` (Part 10) tests a specific, named alternative explanation in parallel.
