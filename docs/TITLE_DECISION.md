# TITLE_DECISION.md

## Candidates

1. **Algorithmic Resolution and Solver-Dependent Observational Geometry in SAT Solution Spaces**
2. Coverage Does Not Determine Geometry: Solver-Dependent Observation of SAT Solution Spaces
3. From Coverage to Geometry: Algorithm-Dependent Observation of SAT Solution Spaces
4. Two Diagnostics, Two Rankings: Resolution and Connectivity Fidelity in Algorithmically Sampled SAT Solution Spaces
5. Observer-Dependent Geometry of SAT Solution Spaces: Coverage, Resolution, and Connectivity
6. What Coverage Does Not Tell You: Geometric Resolution and Connectivity Fidelity in SAT Solving
7. Solver-Dependent Observational Geometry of SAT Solution Spaces
8. Algorithmic Resolution Revisited: Coverage, Hausdorff Distance, and Connectivity Fidelity in SAT Solving
9. Same Solutions, Different Geometry: WalkSAT and CDCL as Distinct Observers of SAT Solution Spaces
10. Geometric Resolution and Observer-Induced Fragmentation in SAT Solution Spaces
11. The Limits of Coverage: A Geometric Diagnostic Framework for SAT Solvers

## Evaluation

| # | Accuracy | Discoverability | Mathematical tone | Overclaim risk | Continuity with January paper |
|---|---|---|---|---|---|
| 1 | High — names both core mechanisms (resolution, observational geometry) | High — "algorithmic resolution" is the established search term from the January paper; "SAT solution spaces" is the field's own phrase | High | Low | High — direct lineage from the January title, signals correction/evolution not repudiation |
| 2 | High but slightly rhetorical ("does not determine") | Medium | Medium — catchier, slightly less formal | Low-medium — the "does not" framing is punchy but accurate (A6/B5+B6 support it exactly) | Medium |
| 3 | High | Medium | Medium | Low | Medium |
| 4 | High, very precise | Low — generic phrasing, weak keyword density | High | Low | Low |
| 5 | High | Medium | High | Low | Medium |
| 6 | Medium — "what coverage does not tell you" is catchy but vaguer than needed | Medium | Medium | Low | Low |
| 7 | High, plain | Medium | High | Low | Medium |
| 8 | High, but "Revisited" telegraphs an erratum rather than a substantially new paper | High (reuses January's own keywords) | High | Low | Very high — arguably too tied to the original, risks being read as a mere correction |
| 9 | High, concrete, names the actual solvers used | Medium — solver names are less searchable than general terms | Medium — slightly informal ("Same Solutions, Different Geometry") | Low | Low |
| 10 | High | Medium-high — "observer-induced fragmentation" is now a precisely defined term in this project | High | Low | Medium |
| 11 | Medium — "Limits of Coverage" undersells the positive contribution (the paired reversal, not just a limitation) | Medium | Medium | Low | Low |

## Decision

**Primary title: #1 — "Algorithmic Resolution and Solver-Dependent Observational Geometry in SAT Solution Spaces."**

Reasoning: it preserves the January paper's own coined term ("algorithmic resolution," §V2_DECISION.md's finding that this terminology is worth retaining as a domain-facing label for the standard Hausdorff-distance quantity, per `phase2/HAUSDORFF_IDENTITY.md` §5) for continuity and discoverability by anyone tracking the earlier preprint, while "solver-dependent observational geometry" is the accurate, non-overclaiming description of the actual new contribution (the paired `ε̂`/fragmentation reversal, Section F of `SOURCE_OF_TRUTH.md`) — it does not claim a new theorem, does not mention any rejected concept (conjugacy, cross-solver transfer, portfolio superiority), and reads as continuation-with-correction rather than either a timid erratum or an inflated rebrand.

**Alternative 1: #2 — "Coverage Does Not Determine Geometry: Solver-Dependent Observation of SAT Solution Spaces."** Strong alternative if the venue favors a punchier, claim-forward title; the colon structure foregrounds the paper's single cleanest empirical finding (B5+B6) rather than its framework, which may suit a venue emphasizing novel results over frameworks.

**Alternative 2: #10 — "Geometric Resolution and Observer-Induced Fragmentation in SAT Solution Spaces."** Best if the venue or audience is more topology/TDA-adjacent (e.g. a computational-geometry or TDA-application track) where "observer-induced fragmentation" as a named, formalized phenomenon (Section 11/`FRAGMENTATION_THEOREM.md`) is the more legible hook than "algorithmic resolution" (a SAT-community-specific coinage).

**Rejected patterns, explicitly**: nothing mentioning "conjugacy," "portfolio," "complexity," "hardness," or superiority claims for either solver — consistent with `ABSTRACT_RESULTS.md`'s exclusion list.
