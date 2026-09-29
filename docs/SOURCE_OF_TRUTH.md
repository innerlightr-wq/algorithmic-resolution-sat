# SOURCE_OF_TRUTH.md

Final accepted result set for the V2 manuscript, synthesized from the frozen Phase 1–4 record at `~/scratch/sat-algorithmic-resolution-v2-audit-2026-09-28/`. Phase 4 is authoritative wherever it supersedes an earlier phase's interpretation. All numbers below are read directly from the cited frozen files, not reconstructed from memory.

## A. Mathematical results (Tier 1 — proved, correctly attributed)

| # | Statement | Status | Source |
|---|---|---|---|
| A1 | `ε̂(A,I) = d_Haus(A(I),S_I)` for nonempty `A(I)⊆S_I` | Standard metric fact / interpretation, not new | `phase2/HAUSDORFF_IDENTITY.md` |
| A2 | Open balls: `B_ε(x)∩B_ε(y)=∅ ⟺ ε≤⌈D/2⌉`. Closed balls: `⟺ ε<⌈D/2⌉`. Corrects January's `ε<D/2` | Proved, 45,393 cases verified, 0 mismatches | `phase2/HAMMING_BALL_THEOREM.md` |
| A3 | Asymmetric H₀ correspondence: no false merge (zero slack); `+2ε` recovery | **Direct corollary of Harker–Kramár–Levanger–Mischaikow (2018/2019) Prop. 5.6(i)**, confirmed by direct PDF reading. NOT a new theorem. | `phase4/HARKER_PROP_5_6_DIRECT_AUDIT.md`, `phase4/HARKER_COMPARISON_MATRIX.md` |
| A4 | `+2ε` constant is sharp, incl. in the Hamming cube specifically | Independently verified (7 parameter combos, exact equality); no prior sharpness statement located anywhere searched | `phase3/H0_SHARPNESS.md`, `phase4/SHARPNESS_NOVELTY_AUDIT.md` |
| A5 | Exact `C_A(r)` vs `C_S(r)` structural theory (`r<ε` indeterminate w/ counterexample; `r≥ε ⟹ C_A(r)≥C_S(r)`, 877/877 verified) | Elementary consequence of Harker et al.'s machinery, not found stated explicitly | `phase3/FRAGMENTATION_THEOREM.md` |
| A6 | Coverage and covering-radius resolution are logically independent (star-plus-outlier family; perfect-Hamming-code family, verified to `n=63`) | Proved, elementary; underlying coding facts are standard | `phase2/COVERAGE_RESOLUTION_THEOREM.md` |

## B. Computational results (Tier 2 — new, surviving audit)

| # | Result | Exact value | Source |
|---|---|---|---|
| B1 | WalkSAT held-out blind-zone predictor (`risk_basin`) | Test median AUROC **0.658** `[0.636, 0.685]`, Spearman 0.252, permutation `p=0.000999` | `phase2/EXPERIMENT_RESULTS.md` §4–5 |
| B2 | CDCL/Glucose3 held-out blind-zone predictor (`risk_cdcl_recurrence`) | Test median AUROC **0.667** `[0.647, 0.700]`, Spearman 0.346, permutation `p=0.000999` | `phase3/CDCL_RESULTS.md` |
| B3 | Fragmentation frequency (WalkSAT, 349 instances) | 51.3% overall; solution_rich 99.2%, intermediate 42.4%, near_threshold 9.0% | `phase2/EXPERIMENT_RESULTS.md` §8 |
| B4 | Persistence-stability theorem validated on real data | 0/(349×~20) violations | `phase2/EXPERIMENT_RESULTS.md` §8 |
| B5 | **Matched-coverage paired fragmentation (349 instances)** | WalkSAT median **11.6×** greater excess fragmentation than CDCL, **95% CI [9.6, 13.3]**, `p=5.2×10⁻³¹` (paired Wilcoxon), survives coverage-matching (`p=2.4×10⁻⁷`, n=160) | `phase4/FRAGMENTATION_REPLICATION_AUDIT.md` |
| B6 | **Matched-coverage paired `ε̂` reversal (349 instances)** | WalkSAT mean `ε̂=1.413` vs CDCL `3.516`; `p=5.1×10⁻³⁸` (paired Wilcoxon); survives coverage-matching (`p=2.5×10⁻⁸`) | `phase4/PAIRED_OBSERVER_TEST.md` |
| B7 | Portfolio/union geometric complementarity | `ε̂_union < min(ε̂_W,ε̂_C)` strictly on 15.6% (56/360) of instances | `phase3/PORTFOLIO_GEOMETRY.md` |

## C. Retracted / rejected results (must NOT appear as positive claims)

| # | Claim | Status | Source |
|---|---|---|---|
| C1 | WalkSAT→CDCL cross-prediction (raw AUROC 0.625) as evidence of dynamical transfer | **Retracted — confounded.** Confounds-only models reach AUROC 0.946/0.756 (w/o strongest confound); adding solver-specific risk adds ≈0; coverage-matching shrinks 0.625→0.556 | `phase4/CONDITIONAL_PREDICTION.md`, `phase4/STRATIFIED_ASYMMETRY.md`, `phase4/RESIDUALIZATION.md` |
| C2 | "Rare solution sensing" interpretation | Tested, not supported (per-instance AUROC ≈ chance: 0.533, 0.500) | `phase4/RARE_SOLUTION_TEST.md` |
| C3 | Conjugacy / semiconjugacy language | Explicitly rejected — no state-space map ever constructed | `phase4/CONJUGACY_FILTER.md` |
| C4 | Asymmetric H₀ theorem as "new theorem" | Reclassified: direct corollary (see A3) | `phase4/HARKER_COMPARISON_MATRIX.md` |
| C5 | Universal `ε=d/2` distinguishability threshold (January paper) | False as stated; corrected by A2 | `phase1/AUDIT.md`, `phase2/HAMMING_BALL_THEOREM.md` |
| C6 | January paper's biased-sampler result as primary evidence for predictable blind zones | Circular by construction; superseded by B1/B2 | `phase1/ORIGINAL_EXPERIMENT_AUDIT.md` |
| C7 | Solver-portfolio performance superiority | Never claimed with performance data; only narrow geometric observation (B7) supported | `phase3/PORTFOLIO_GEOMETRY.md` |

## D. Baselines and negative sub-results (report honestly, not hidden)

- WalkSAT: `risk_disc_flips` (0.407 test), `risk_foundneighbor` (0.279 test) both moved in the *opposite* direction from hypothesis — reported, not rescued (`phase2/EXPERIMENT_RESULTS.md`).
- CDCL: `risk_cdcl_conflicts` (0.471 test) near-random, same "hypothesis failed" pattern as WalkSAT's `disc_flips` (`phase3/CDCL_RESULTS.md`).
- CDCL baselines: random 0.481, Hamming-weight 0.492, found-neighbor 0.467.
- Coverage/`ε̂` are empirically near-redundant for WalkSAT alone (`ρ=-0.975`, Phase 2) — but B6 shows they diverge meaningfully once a second solver paradigm is introduced.

## E. Experimental design facts (for methods section)

- 720 random 3-SAT instances (360 train / 360 test), `n∈{16,18,20}`, `α∈{2.5 (solution-rich), 3.5 (intermediate), 4.2 (near-threshold)}`, 40 instances/cell/split, all satisfiable, **no solution cap** (unlike January's 500-cap).
- WalkSAT: `K=150` restarts, `max_flips=3000`, `p_noise=0.5`.
- CDCL: Glucose3 via PySAT 1.9.dev15, genuine CDCL (VSIDS, clause learning, LBD restarts); randomized via variable/clause permutation + phase initialization (no direct RNG seed exposed); primary budget `R=5` independent permuted runs × `T=8` solutions/run (calibrated to give comparable-order-of-magnitude coverage to WalkSAT).
- Freeze-before-reveal architecture: Stage A (pre-reveal, hashed, SHA-256 + UTC timestamp) → Stage B (reveal, hash-verified before proceeding). Phase 4 added a programmatic runtime guard (`guarded_open`) tested to actually trip on a forbidden access attempt.
- `ρ=1.0` (median nearest-neighbor distance within `S_I`, frozen from train split only, reused unchanged on test).
- Independent experimental unit throughout: the SAT instance (never individual solutions) — per-instance metrics, median + instance-level bootstrap CI (5,000 resamples), instance-level permutation test (1,000 permutations).

## F. The central empirical finding (B5+B6 combined) — this is the manuscript's spine

At matched or near-matched coverage, on the **identical** solution space `S_I`, WalkSAT and CDCL trade off in **opposite directions** on two logically-independent geometric diagnostics: WalkSAT achieves significantly better `ε̂` (covering-radius resolution) but dramatically worse apparent connectivity (fragmentation); CDCL achieves worse `ε̂` but dramatically better apparent connectivity. This is a direct, "in the wild" empirical realization of the worst-case logical-independence theorem (A6), produced by two real, unmodified, off-the-shelf solvers, not hand-constructed. Per `PAIRED_OBSERVER_TEST.md`: *"arguably the single strongest, most defensible empirical result to come out of the entire four-phase project."*
