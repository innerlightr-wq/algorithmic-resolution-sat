# Supplementary Tables

## Table 1 — Core definitions

| Quantity | Definition | Status |
|---|---|---|
| Coverage | $\mathrm{Cov}(A,I) = \|A(I)\|/\|S_I\|$ | Standard |
| Empirical resolution | $\hat\varepsilon(A,I) = \max_{x\in S_I}\min_{y\in A(I)} d_H(x,y) = d_{\mathrm{Haus}}(A(I),S_I)$ | Standard (Hausdorff distance); domain-facing name only |
| Blind zone | $M_A(I) = S_I \setminus A(I)$ | Standard |
| Cluster spectrum / fragmentation | $C_S(r)$ = connected components of $S$ at Hamming threshold $r$; observed fragmentation = $C_{A}(r) - C_S(r)$ at the same $r$ | Standard construction (0-dim persistence); the exact monotonicity conditions (this paper §6) are the contribution |

## Table 2 — Experimental dataset and solver configuration

| Parameter | Value |
|---|---|
| Instances | 720 (360 train / 360 test), split by instance |
| $n$ | $\{16, 18, 20\}$ |
| $\alpha$ regimes | $2.5$ (solution-rich), $3.5$ (intermediate), $4.2$ (near-threshold) |
| Instances per (n,α) cell per split | 40 |
| Solution cap | None (January preprint used a 500-solution cap, removed here) |
| WalkSAT restarts $K$ | 150 |
| WalkSAT max flips | 3000 |
| WalkSAT noise $p$ | 0.5 |
| CDCL solver | Glucose3 (PySAT 1.9.dev15) |
| CDCL randomization | Variable/clause permutation + phase-initialization hints |
| CDCL budget | $R=5$ permuted runs $\times$ $T=8$ solutions/run |
| $\rho$ (miss-radius) | 1.0 (median nearest-neighbor distance in $S_I$, frozen from train split) |
| Statistical unit | SAT instance (never individual solutions) |
| CI method | Instance-level bootstrap, 5,000 resamples |
| Significance test | Instance-level permutation test, 1,000 permutations |

## Table 3 — Held-out blind-zone prediction performance

*(See manuscript Section 8, Table 1 — reproduced here for standalone reference.)*

| Solver | Predictor | Median AUROC [95% CI] | Permutation $p$ |
|---|---|---|---|
| WalkSAT | `risk_basin` | 0.658 [0.636, 0.685] | 0.000999 |
| WalkSAT | random | 0.504 [0.487, 0.519] | 0.347 |
| CDCL | `risk_cdcl_recurrence` | 0.667 [0.647, 0.700] | 0.000999 |
| CDCL | random | 0.481 [0.449, 0.514] | 0.934 |

## Table 4 — Matched-coverage WalkSAT/CDCL comparison (349 paired instances)

| Diagnostic | WalkSAT | CDCL | Paired test | Coverage-matched ($n=160$) |
|---|---|---|---|---|
| Mean excess fragmentation (r=1) | 18.96 | 1.16 | $p=5.2\times10^{-31}$ | $p=2.4\times10^{-7}$ |
| Median fragmentation ratio | — | — | 11.6$\times$ [9.6,13.3] 95% CI | 11.6$\times$ still applies |
| Mean $\hat\varepsilon$ | 1.413 | 3.516 | $p=5.1\times10^{-38}$ | $p=2.5\times10^{-8}$ |
| Fraction fragmented (excess>0) | 50.4% | 42.4% | — | — |

## Table 5 — Claim classification

| Claim | Classification |
|---|---|
| $\hat\varepsilon = d_{\mathrm{Haus}}(A(I),S_I)$ | Known mathematics |
| Corrected Hamming-ball theorem ($\varepsilon \le \lceil D/2\rceil$) | New (elementary correction of a specific published error), exhaustively verified |
| Asymmetric $H_0$ recovery bound (no false merge; $+2\varepsilon$) | Known mathematics — direct corollary of Harker et al. (2019) Prop. 5.6(i) |
| Sharpness of the $+2\varepsilon$ constant, incl. Hamming cube | New computational/mathematical result (narrow scope; no prior statement located) |
| Exact $C_A(r)$ vs $C_S(r)$ threshold theory ($r\ge\varepsilon$ condition) | New (elementary consequence of known machinery, not found stated explicitly) |
| Coverage/resolution logical independence | New (elementary; standard coding-theoretic ingredients) |
| WalkSAT held-out blind-zone prediction | New computational result |
| CDCL held-out blind-zone prediction | New computational result |
| Cross-solver predictive transfer | **Retracted** — confounded, not a finding |
| Matched-coverage paired $\hat\varepsilon$/fragmentation reversal | New computational result (paper's central empirical contribution) |
| Conjugacy / semiconjugacy between solvers | **Rejected** — not supported by any evidence gathered |
| Portfolio/complexity-theoretic implications | Not claimed |
