# VERSION_HISTORY.md

## January 2026 (v1, `GeometricResolution.pdf`)

The original preprint, "Algorithmic Resolution and Geometric Distinguishability in SAT Solution Spaces," introduced the core idea of this line of work: a solver's output $A(I)$ is an algorithm-dependent observation of the true SAT solution space $S_I$, and this observer-dependence has measurable geometric consequences. It defined the empirical resolution $\hat\varepsilon(A,I)$, reported a geometric distinguishability threshold at $\varepsilon=d/2$, and gave empirical evidence (including a deliberately Hamming-weight-biased sampler) for algorithm-specific blind zones.

## Audit findings

A subsequent four-phase validation program identified specific issues with the January version:

- **Theorem 2.1** (the $\varepsilon=d/2$ distinguishability threshold) is false as stated for arbitrary metric spaces, and specifically false for the discrete Hamming cube: the proof implicitly assumes an exact midpoint exists between any two points, which fails whenever the Hamming distance between them is odd (Hamming distances are integer-valued). A direct counterexample (points at Hamming distance 1, resolution $\varepsilon=1$) and 45,393 exhaustively/systematically verified cases confirmed the failure and established the correct threshold.
- **The 500-solution cap** used in the January experiments was found, on reconstruction, to truncate the true solution set itself (not merely the algorithm's search) for a large fraction of instances at low clause-to-variable ratio and $n\ge18$ — confounding some of the reported coverage measurements with a ground-truth-truncation artifact rather than purely reflecting algorithmic search quality.
- **The deliberately biased sampler** (constructed to prefer low-Hamming-weight solutions, then observed to miss high-Hamming-weight solutions) provided weak, close-to-circular evidence for the "predictable blind zone" claim, since the predictor and the mechanism generating the bias were closely related by construction.

## V2 (this repository, September 2026)

V2 replaces rather than patches these components:

- The false $\varepsilon=d/2$ threshold is replaced by the exact, proved, exhaustively-verified discrete result: $\varepsilon\le\lceil D/2\rceil$ (open balls), $\varepsilon<\lceil D/2\rceil$ (closed balls).
- Experiments are run with no solution cap, using exhaustive enumeration for ground truth throughout.
- Blind-zone prediction is established via a freeze-before-reveal, anti-leakage-verified protocol (a pre-reveal Stage A process, hashed before any ground-truth-revealing Stage B process runs), across two independently audited solver paradigms (WalkSAT and CDCL/Glucose3) rather than a single potentially-circular biased sampler.
- The connectivity-stability machinery this framework relies on is correctly attributed to prior published work (Harker, Kramár, Levanger & Mischaikow, 2019) rather than presented as original.
- A new central empirical result — the matched-coverage paired resolution/fragmentation trade-off between WalkSAT and CDCL — is established and audited across 349 held-out instances, including an explicit, reported retraction of an initially promising but ultimately confounded cross-solver predictive-transfer finding.

## Framing

This is presented as normal scientific correction and development, not as a repudiation of the January work: the core conceptual framework (separating $S_I$ from $A(I)$, and treating this separation as a genuine geometric phenomenon worth measuring) originates there and is retained; what changed is the correctness of one theorem, the rigor of the experimental design, and the strength and honesty of the empirical evidence supporting the framework's central claims.
