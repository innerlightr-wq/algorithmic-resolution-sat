# RARE_SOLUTION_TEST.md — Phase 4, Part 10

Tests whether a solver's risk score identifies **solver-agnostic** accessibility (solutions hard/easy to find *regardless of method*) — the specific alternative hypothesis flagged in `CONFOUND_AUDIT.md` item 11. Retrospective characterization: for each `y∈A_W(I)`, is `y` also `∈A_C(I)` ("jointly found")? Symmetrically for `y∈A_C(I)`.

## Results

| Test | Pooled Spearman(risk, jointly-found) | **Per-instance AUROC(risk → jointly-found), median** |
|---|---|---|
| `basin → ` also found by CDCL | `ρ=0.453` (`p≈0`) | **`0.533`** (`n=239` instances) |
| `recurrence → ` also found by WalkSAT | `ρ=0.380` (`p=2.9×10⁻²⁹⁴`) | **`0.500`** (`n=227` instances, exactly chance) |

`23.9%` of WalkSAT-found solutions are also found by CDCL; `55.9%` of CDCL-found solutions are also found by WalkSAT (asymmetric simply because the two found-sets are different sizes, `CONFOUND_AUDIT.md`). Mean `basin` is `6.5` for jointly-found solutions vs. `1.5` for WalkSAT-only — a large, highly significant (Mann-Whitney `p≈0`) pooled difference.

## The decisive pattern: strong pooled correlation, chance-level per-instance discrimination

This is the **same pooled-vs-per-instance divergence** already seen in `RESIDUALIZATION.md`, now isolated specifically for the rare-solution hypothesis: a large, highly significant *pooled* relationship (`ρ=0.45`, `0.38`) coexists with **essentially no within-instance ranking ability** (`0.533`, `0.500` — the second is exactly `0.5`). This pattern is the signature of a **between-instance confound**: instances with systematically higher `|S_I|`/lower coverage/higher `ε̂` (`CONFOUND_AUDIT.md`) simultaneously produce lower `basin`/`recurrence` values *and* lower joint-discovery rates — both effects of the same underlying instance-level difficulty, not of `basin`/`recurrence` genuinely sensing which *specific* solutions within a given instance are rare.

## Verdict on the rare-solution hypothesis

**Not supported in its useful (within-instance) form.** The hypothesis as originally framed in the task ("WalkSAT recurrence identifies solutions that are globally hard to encounter... interpret the asymmetry as evidence that WalkSAT is a better SENSOR of shared solution rarity") would require the per-instance AUROC to be well above chance — it is not (`0.533`, indistinguishable from noise at this sample size; `0.500` for the reverse direction is exact chance). **The interesting positive story flagged as a possible outcome in the task ("WalkSAT exposes intrinsic accessibility structure that CDCL partially overcomes") is not supported by this data** and is explicitly not claimed. The correct, narrow, defensible statement: **both risk scores correlate with joint-discoverability only insofar as they both correlate with the same coarse instance-level difficulty confounds already identified in Parts 6–9** — this is a restatement of the confound-audit conclusion from a different angle, not a new independent finding, and is reported as such rather than inflated into a distinct positive claim.
