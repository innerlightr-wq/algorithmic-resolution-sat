# SHARPNESS_NOVELTY_AUDIT.md — Phase 4, Part 4

Searches performed (live web search, not guessed): "sharp constant Rips complex Hausdorff distance interleaving subsample tight bound persistent homology"; combined with targeted follow-up checks against the two primary sources already read in full (Harker et al. 2018, `HARKER_PROP_5_6_DIRECT_AUDIT.md`; Blumberg–Lesnick 2020, Phase 3 fork).

## A. Is factor 2 known sharp in arbitrary metric spaces?

**Partially — for the general symmetric (Gromov–Hausdorff) setting, yes, this is discussed in the literature**: search results indicate "there are results showing that stability constants for Rips complexes are tight, in the sense that the constant cannot be improved" for the symmetric `d_B ≤ 2·d_{GH}` bound (consistent with Phase 2's `PRIOR_ART.md` finding that this constant is the standard one, and with Phase 2's own literature-verification fork's report that a factor-of-2 tightness discussion exists in this space, e.g. in or around Chazal–de Silva–Oudot-adjacent work). **This is a general, symmetric, Gromov–Hausdorff-distance statement about two unrelated point clouds — not the same setting as ours.**

## B. Is a sharpness construction specifically inside Hamming cubes known?

**Not located.** No source found in this search, in the Phase 2 fork's search, or in the Phase 3 fork's search discusses a Hamming-cube-specific extremal/sharpness construction for any version of this stability bound. **We did not locate an explicit Hamming-cube sharpness statement.** This is stated as an absence, not as a novelty claim from that absence (per the task's explicit instruction) — SAT/Hamming-cube applications of Rips stability appear to be a narrow enough niche that a dedicated sharpness construction there may simply not have been written down, or may exist in a source this search did not surface.

## C. Is our construction merely an obvious realization of a standard extremal example?

**Likely partially yes, and this should be stated plainly.** The general technique — placing two "hub" points connected by a chain through a removed midpoint, with the approximating set's nearest-neighbor slack maximally and independently realized on each side — is a standard type of extremal construction in metric stability arguments generally (the same "worst-case additive triangle inequality" idea appears, in spirit, in essentially any proof that a triangle-inequality-derived bound is tight). **Our specific contribution is not the *idea* of such a construction (which is generic to the field) but its explicit, verified realization inside the discrete Hamming cube via disjoint coordinate blocks** — a concrete combinatorial embedding that had to be checked (and was checked, computationally, across 7 parameter combinations) rather than assumed to transfer automatically from the continuous/abstract-metric-space setting, precisely because the Hamming cube's discreteness was already shown (Phase 1's Theorem 2.1 audit) to break naive continuous-space intuitions in at least one prior instance of this project. **The verification that the standard idea transfers cleanly to this discrete setting, with no obstruction, is the honest scope of this contribution — not the invention of a new extremal-construction technique.**

## Conclusion

- General factor-of-2 tightness: **KNOWN** (symmetric/GH setting).
- Hamming-cube-specific realization: **not located anywhere searched** — reported as an honest gap in the literature as far as this search could determine, not as a confirmed novelty claim.
- Overall label carried into `HARKER_COMPARISON_MATRIX.md` and `FINAL_CLAIM_HIERARCHY.md`: **INDEPENDENT SHARPNESS RESULT** (verified, narrow-scope, likely-straightforward-but-unconfirmed-elsewhere), not "new theorem" and not "novel technique."
