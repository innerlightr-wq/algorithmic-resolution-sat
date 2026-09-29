# ABSTRACT_RESULTS.md — Phase 4, Part 16

## The 3–5 results strong enough for the Abstract

**1. At matched coverage, WalkSAT and CDCL trade off oppositely on two logically-independent geometric diagnostics of the same solution space.**
- Status: **new computational result** (Tier 2), directly instantiating an already-proved theorem (Tier 1: coverage/resolution logical independence).
- Quantitative value: WalkSAT mean `ε̂=1.41` vs. CDCL `3.52` (`p=5.1×10⁻³⁸`, `n=349`, paired); WalkSAT median fragmentation-excess `11.6×` CDCL's (`95% CI [9.6,13.3]`), both surviving coverage-matching.
- Caveat: observational comparison of two specific, audited implementations — not a general claim about local-search vs. systematic-search paradigms.

**2. Two structurally different SAT-solving paradigms each exhibit genuine, held-out, non-circular blind-zone predictability from their own pre-reveal search dynamics.**
- Status: **new computational result** (Tier 2), anti-leakage-verified (programmatic guard, tested to trip correctly).
- Quantitative value: WalkSAT `AUROC=0.658 [0.636,0.685]`; CDCL `AUROC=0.667 [0.647,0.700]`; both `p<0.001` (permutation test), both beat random/Hamming-weight/found-neighbor-density baselines.
- Caveat: modest effect sizes (AUROC well below 1); random-baseline sanity checks correctly non-significant.

**3. The exact discrete Hamming-ball distinguishability theorem, correcting a specific error in the original January 2026 paper.**
- Status: **Tier 1, proved**, exhaustively verified (`45,393` cases, `0` mismatches).
- Quantitative value: `B_ε(x)∩B_ε(y)=∅ ⟺ ε≤⌈D/2⌉` (open balls), replacing the original paper's `ε<D/2`.
- Caveat: none needed — this is a clean, self-contained, fully verified correction.

**4. `ε̂` is exactly the Hausdorff distance between found and true solution sets, and an asymmetric persistence-stability bound (no false merge, `+2ε` recovery, with the constant proved sharp including in the Hamming cube) governs when observed connectivity can be trusted — but this bound is a known result.**
- Status: **Tier 1, proved; explicitly and correctly attributed** as a direct corollary of Harker–Kramár–Levanger–Mischaikow (2019), confirmed by direct primary-source reading.
- Quantitative value: sharp `+2ε` constant, verified extremal construction.
- Caveat: **must not be presented as a new theorem** — present as a citation-grounded application, with the sharpness result as the one independently-verified original piece.

**5. Solution-set coverage and covering-radius resolution are provably, constructively independent quantities.**
- Status: **Tier 1, proved**, via explicit parameterized families (star-plus-outlier; perfect Hamming codes verified up to `n=63`).
- Quantitative value: exact closed-form asymptotic families demonstrating simultaneous coverage→1/resolution→worst and coverage→0/resolution→best.
- Caveat: worst-case existence proof; result 1 above shows this independence is not merely a hand-built curiosity but is realized by real solvers on real instances.

## What should NOT appear in the Abstract

- **Any cross-solver directional-transfer or "shared accessibility structure" claim** (Phase 3's `0.625` vs. `0.526` finding) — retracted in this phase (`FINAL_CLAIM_HIERARCHY.md`); reporting it in the Abstract would contradict the project's own later, more careful analysis.
- **Any conjugacy/semiconjugacy language** — explicitly filtered out (`CONJUGACY_FILTER.md`); not justified by any evidence gathered across all four phases.
- **Any claim that the asymmetric H₀/persistence-stability theorem is novel** — it is a direct corollary of published work (Harker et al. 2019), confirmed by direct reading; only the sharpness result may be described as independently verified, and even that modestly.
- **Any speculative complexity-theoretic claim** — never established anywhere in this project (the January paper's own §7.4 correctly flagged this as "a motivating question, not a result," and nothing in Phases 1–4 changes that status).
- **Any portfolio-performance or "combining solvers is worthwhile" claim** beyond the narrow, explicitly-geometric `ε̂_union` observation (Phase 3 `PORTFOLIO_GEOMETRY.md`) — no runtime or engineering-value evidence exists.
- **The "rare solution sensing" interpretation** — specifically tested and not supported (`RARE_SOLUTION_TEST.md`).
