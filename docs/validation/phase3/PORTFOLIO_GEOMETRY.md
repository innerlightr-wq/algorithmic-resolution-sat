# PORTFOLIO_GEOMETRY.md — Phase 3, Part 10

All numbers from `scripts/part10_portfolio.py`, output `data/part10_output.txt`, raw data `data/part10_portfolio.json`. Test split, 360 instances, `A_union(I) = A_W(I)∪A_C(I)` (WalkSAT's Phase 2 found set union CDCL's Phase 3 found set).

**Framed strictly as a geometric observation about combined sample coverage, not a claim about practical portfolio solver performance** (per task instruction) — no runtime, wall-clock, or "which solver to run" claims are made anywhere below.

## Does `ε̂_union < min(ε̂_W, ε̂_C)` on a substantial fraction of instances?

**Yes, on 56/360 (15.6%) of instances overall** — a genuine, non-trivial minority, not a majority and not negligible. Where it happens, the improvement is real (mean improvement `0.156` Hamming units among instances with `improvement>0`, though the overall median across *all* instances is `0.000` since the majority show no strict improvement — the union simply matches whichever single solver already achieved the better `ε̂`).

| Regime | fraction with `ε̂_union < min(ε̂_W,ε̂_C)` |
|---|---|
| solution_rich | 27/120 (22.5%) |
| intermediate | 22/120 (18.3%) |
| near_threshold | 7/120 (5.8%) |

Regime pattern is consistent with `CROSS_SOLVER_GEOMETRY.md`'s Part 7 finding: solution-rich instances (where blind zones are closer to independent) show the *most* frequent geometric complementarity benefit, near-threshold (where `|S_I|` is tiny and coverage from either solver alone is often already near-total) shows the *least* — there's simply less room for a union to help when one solver already finds almost everything.

## Coverage gain

Median coverage gain from the union (`\text{coverage}_{union} - \max(\text{coverage}_W,\text{coverage}_C)`): `+3.57%`; mean `+4.09%` — modest but consistently non-negative (by construction, a union can never have *lower* coverage than either constituent), and the median being clearly positive (not zero) confirms the two solvers are finding **genuinely different** solutions in the typical case, not just redundant overlapping sets.

## Interpretation

**Geometric complementarity is real but modest and regime-dependent**: combining WalkSAT and CDCL's found sets improves the covering-radius diagnostic on roughly one in six to one in four instances (higher in solution-rich regimes), and reliably improves raw coverage by a few percentage points. This is consistent with, and quantifies, the Part 7 overlap finding — genuine (if partial) complementarity where blind zones are closer to independent, little additional benefit where one solver already achieves near-total coverage on its own. **No claim is made here about whether running two solvers is worth the combined computational cost** — that is a portfolio-engineering question outside this geometric analysis's scope.
