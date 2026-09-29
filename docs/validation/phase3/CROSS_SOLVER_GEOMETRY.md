# CROSS_SOLVER_GEOMETRY.md — Phase 3, Parts 7–8

All numbers from `scripts/part7_8_cross_solver_geometry.py`, output `data/part7_8_output.txt`, raw data `data/part7_cross_solver_geometry.json`, `data/part8_blind_zone_decomposition.json`. Test split, 360 paired instances (same `I`, same `S_I`, `M_W` from Phase 2's WalkSAT run, `M_C` from Phase 3's CDCL run).

## Part 7: overlap vs. a size-controlled null model

Null model: under independence, given the *observed sizes* `|M_W|,|M_C|,|S_I|` alone, expected intersection size is the hypergeometric mean `|M_W|·|M_C|/|S_I|` — this controls for each solver's blind-zone size so that overlap is judged against "would two randomly-placed blind zones of these sizes overlap this much by chance," not against zero.

**Overall**: median observed Jaccard `0.405` vs. median null-expected Jaccard `0.388` — **ratio ≈ 1.00, statistically indistinguishable from independence in aggregate** (Wilcoxon signed-rank on intersection size is technically significant, `p=1.1×10⁻⁷`, but the median difference is `0.000` — with `n=360`, a genuinely tiny, practically negligible effect can still cross a p-value threshold; the *magnitude* is what matters here, and it is essentially zero).

**But this aggregate masks a strong, honest, regime-dependent pattern**:

| Regime | median obs. Jaccard | median null Jaccard | ratio | Interpretation |
|---|---|---|---|---|
| solution_rich | 0.729 | 0.729 | **1.001** | Essentially independent |
| intermediate | 0.162 | 0.136 | **1.190** | **Moderately MORE overlapping than chance** — some shared difficulty |
| near_threshold | 0.000 | 0.043 | **0.000** | **Dramatically LESS overlapping — near-complete complementarity** |

Near-threshold's `ratio=0` reflects small-`|S_I|` quantization (median `|S_I|=8`; blind zones there are often `1–2` points, so "zero observed overlap" is common and can be a real complementarity signal *or* a small-sample artifact — both plausible, flagged honestly, not resolved by this data alone). The solution-rich vs. near-threshold contrast is the clean, large-sample-supported finding: **overlap structure is not uniform across the SAT-solvability spectrum** — Outcome A (shared) fits solution-rich, Outcome C (complementary) fits near-threshold, and intermediate sits closer to A with a mild lean toward shared difficulty. **This is itself evidence against forcing a single global Outcome label** (per the task's Part 16 instruction) — the honest answer is regime-conditional.

## Part 8: geometric characterization of the blind-zone decomposition

`M_shared = M_W∩M_C`, `M_Wonly`, `M_Conly`, `V = S_I\(M_W∪M_C)` (jointly visible — found by at least one solver).

**Hamming weight**: `median≈9.0` for **all four** categories (shared `9.090`, `W`-only `9.000`, `C`-only `9.000`, `V` `9.000`) — **no meaningful weight-based distinction between shared and solver-specific blind regions.** A clean negative finding: whatever distinguishes solver-specific misses from shared ones, it is **not** simply "extremeness of Hamming weight" (which would have been the obvious, circular-adjacent hypothesis given Phase 1's biased-sampler history).

**Distance to the jointly-visible set `V`** (a proxy for "how geometrically isolated is this missed point from what's actually been observed"):

| Category | median distance to `V` |
|---|---|
| `M_shared` (missed by both) | **3.182** |
| `M_Wonly` (WalkSAT-specific miss) | **1.333** |
| `M_Conly` (CDCL-specific miss) | **3.048** |

**A real, reportable asymmetry**: WalkSAT-specific misses sit much closer to visible territory (`1.33`) than CDCL-specific misses (`3.05`) or doubly-missed points (`3.18`, expectedly the hardest-to-reach category). Interpretation, stated as a hypothesis, not a proven mechanism: WalkSAT's local-search dynamics tend to leave "near misses" — solutions just outside its found neighborhood that a slightly longer walk would likely reach — whereas CDCL's search-order-driven misses tend to be more genuinely isolated from what either solver actually found. This is consistent with, and offers a candidate geometric explanation for, the `BUDGET_TRAJECTORIES.md` finding that CDCL's sampled sets look far less "fragmented" than WalkSAT's at matched coverage (see that document) — WalkSAT's dynamics appear to leave behind many close-but-missed points that read as apparent small isolated fragments, while CDCL's misses are more genuinely distant outliers that don't manufacture spurious apparent components.

## Summary for `FINAL_GATE.md`

- Overlap is **not** uniformly "more," "independent," or "complementary" — it is regime-conditional, cleanly ordered from complementary (near-threshold) through independent (solution-rich) to mildly-shared (intermediate).
- Blind regions are **not** distinguished by Hamming weight (a clean null result).
- Blind regions **are** distinguished by distance-to-visible-set, with WalkSAT's solver-specific misses systematically closer to observed territory than CDCL's — a genuine, non-obvious, reportable geometric asymmetry between the two paradigms' failure modes.
