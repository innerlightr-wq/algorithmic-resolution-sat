# Claims by evidence level

Levels used throughout: **proved** (mathematics, in `ENCODING.md`);
**witness-verified** (a SAT model independently re-checked by `src/verify.py`);
**proof-checked** (a DRUP proof independently verified by `src/drup.py` against the
standalone CNF); **exhaustively checked** (enumeration of `{0,1}^n`, no solver and
no encoder); **solver-reported** (the solver's UNSAT word alone);
**measured** (a timing or size observation); **unresolved**.

## Proved

| # | Statement | Where |
|---|---|---|
| P1 | `Q_r` is satisfiable ⟺ `ε̂(A,I) > r`, for every integer `0 ≤ r ≤ n` | `ENCODING.md` §2, both directions written out |
| P2 | `ε̂(A,I) = min{ r ∈ {0,…,n} : Q_r unsatisfiable }`, and the set is nonempty because `ε̂ ≤ n` | `ENCODING.md` §2 |
| P3 | Monotonicity: `Q_r` UNSAT and `r ≤ r'` ⟹ `Q_{r'}` UNSAT. This licenses binary search, `O(log n)` queries | `ENCODING.md` §2 |
| P4 | `d_H(x,a) = Σ_i lit(i,a)` with `lit(i,a) = x_i` if `a_i=0` else `¬x_i` — a cardinality constraint over the **original `n` variables only** | `ENCODING.md` §3 |
| P5 | `r ≥ n` ⟹ `Q_r` UNSAT by arithmetic (`d_H ≤ n < r+1`), with no formula built and no solver called | `ENCODING.md` §5, implemented as a separate code path |
| P6 | `r = 0` ⟹ the constraint is the single clause `⋁_i lit(i,a)`, i.e. exactly `x ≠ a`; no auxiliary variables | `ENCODING.md` §5 |
| P7 | On a **fixed** formula, equal numbers of distinct observed solutions imply equal coverage fractions, because `coverage = |A|/|S_I|` and `|S_I|` is the same constant in both ratios — so the comparison needs no knowledge of `|S_I|`, while the common numerical coverage remains unknown without it | `REPORT.md` §6 |
| P8 | **The reduction is standard** (farthest-solution query by bisection). No novelty is claimed for it | `ENCODING.md` §2 |

## Reproduction of the published experiment

| # | Statement | Level |
|---|---|---|
| R1 | The paper's setup is as reported: random 3-SAT, `n ∈ {16,18,20}`, densities `2.5/3.5/4.2`, WalkSAT and Glucose3, **349** paired instances with nonempty observed sets | verified against `generate_instances.py:56–60`, `cdcl_stage_a.py:36`, and the 349 rows of `part10_results.json` |
| R2 | The observed sets `A(I)` are **not stored** anywhere in the repository; only derived summaries are | verified by inspection and by grep over `data/` |
| R3 | `A(I)` is nonetheless **exactly regenerable**, because Stage A seeds `default_rng(STAGE_A_SEED + id)` per instance; regeneration reproduces the published `A_I_size`, `S_I_size` and `eps_hat` | measured — see R4 |
| R4 | Regenerated `A` reproduces the published `A_I_size`, `S_I_size` and `eps_hat` on **349/349** instances | measured (`data/validate_all349.csv`) |
| R5 | Consequently this is a **reproduction of the published experiment**, not merely a fresh reproduction of its design. The one dependency is NumPy's PCG64 stream, confirmed stable (paper used numpy 1.26.4, this audit 2.5.4) | measured |

## Validation of the oracle

| # | Statement | Level |
|---|---|---|
| V1 | On one instance from each of the 9 `(n,α)` cells, `ε̂_oracle = ε̂_brute = ε̂_published` — 9/9 | exhaustively checked **and** proof-checked (all 9) |
| V2 | On all 349 published instances, `ε̂_oracle = ε̂_brute` (**349/349**) and `ε̂_oracle = ε̂_published` (**349/349**) | exhaustively checked (brute force is exactly the enumeration decision) |
| V3 | Every SAT answer used as a lower-bound certificate was re-checked by `src/verify.py`, which imports neither the encoder nor any SAT library | witness-verified, 0 failures |
| V4 | Every upper bound on all **349/349** instances carries a DRUP proof independently verified by `src/drup.py` against the standalone CNF — the proof-check budget was never exceeded | proof-checked |
| V5 | All **four** documented cardinality encodings (`seqcounter`, `totalizer`, `sortnetwrk`, `mtotalizer`) give identical radii on 6 cross-checked instances spanning `n = 16,18,20` | measured (`results/cross_encoding.txt`) |

## Controls (31/31 pass, `results/controls.txt`)

| # | Statement | Level |
|---|---|---|
| C1 | Singleton solution space with `A = S_I` ⟹ `ε̂ = 0` | exhaustively checked |
| C2 | `A = S_I` ⟹ `ε̂ = 0` on a 2-solution formula | exhaustively checked |
| C3 | Full cube: `A = {0^n}` ⟹ `ε̂ = n`; `A = {0^n,1^n}` ⟹ `ε̂ = ⌊n/2⌋`; both at `n = 4,6,8` | exhaustively checked |
| C4 | Observed set missing a distant isolated solution (`S_I = {0⁹,1⁹}`, `A = {0⁹}`) ⟹ `ε̂ = 9`, and the returned witness **is** the unobserved solution | witness-verified + exhaustively checked |
| C5 | Duplicate observed assignments change neither the frozen hash nor `ε̂` | exhaustively checked |
| C6 | Empty `A` ⟹ **categorical failure**, `ε̂` undefined — not `0`, not `n`; a non-solution in `A` is refused, not measured | by construction + checked |
| C7 | Off-by-one: `Q_{k−1}` SAT, `Q_k` UNSAT, `Q_{k−2}` SAT, `Q_{k+1}` UNSAT | solver + witness-verified |
| C8 | A deliberately broken encoder that never advances `top_id` (auxiliary-variable collision) returns `ε̂ = 1` against the true `5`, and the independent exhaustive check **refutes** it with a printed counterexample | refuted by independent check |
| C9 | A deliberately broken encoder using `d_H ≥ r` instead of `≥ r+1` is **rejected by the independent witness verifier** ("witness is at distance 4 < 5") | refuted by independent check |
| C10 | **Control-design finding:** the off-by-one bug is *masked* when `ε̂ = n`, because the search is clamped at `r = n`. A discriminating control must use an instance with `ε̂ < n` | measured; recorded because it nearly produced a false pass |

## Measured costs

| # | Statement | Level |
|---|---|---|
| M1 | `Q_r` is a **3-CNF** (clause widths 2 and 3 only, from the sequential counter) but over `n + n_aux` variables — e.g. instance 40 at `r=3`: `n = 16` original variables, **5 344 total variables**, 9 808 clauses | measured |
| M2 | Auxiliary variables scale as `n_aux ≈ 0.75 · |A| · n · (r+1)` for `seqcounter` | measured over `r = 1..5` on instance 40 |
| M3 | **The distance constraints dominate the encoded problem completely.** The original formula is `26.5 %` of the clauses at `r = 0` but only `0.41 %` at `r = 3` and `0.31 %` at `r = 5` | measured |
| M4 | At `r = 0` there are **no** auxiliary variables and the clause width is `n` | measured |
| M5 | Solving is cheap and **encoding is more expensive than solving** at validation sizes (instance 40: encode `0.078 s`, solve `0.017 s`) | measured |
| M6 | **Proof checking is the dominant cost** of this implementation (instance 40: `2.78 s`, versus `0.017 s` solving) — a property of `src/drup.py`, a pure-Python forward checker, not of the reduction | measured |
| M7 | **Corrected across the full dataset.** Mean encode+solve versus mean enumeration: `n=16` `0.0195 s` vs `0.0193 s` (a tie), `n=18` `0.0295 s` vs `0.0963 s` (**oracle 3.3× faster**), `n=20` `0.0526 s` vs `0.5682 s` (**oracle 10.8× faster**). An earlier single-instance reading suggested enumeration was faster; that generalised wrongly. The crossover is at `n ≈ 16` and the margin grows as `2^n` | measured, 349 instances |
| M8 | Totals over the 349 instances: encode `8.4 s`, solve `3.4 s`, **proof check `767.6 s`** — proof checking is `98 %` of the oracle's wall clock | measured |
| M9 | Query count is `4–5` per instance (median `5`), consistent with `O(log n)` bisection | measured |
| M10 | Encoded sizes over the 349: `max_aux_vars` median `3 267` / max `14 553`; `max_total_clauses` median `6 670` / max `29 450`; DRUP proof lines median `111` / max `16 365` | measured |

## Scope limits — explicitly not claimed

| # | Statement |
|---|---|
| N1 | No claim that the oracle is a practical speedup over enumeration at `n ≤ 20`. M7 shows the opposite |
| N2 | No new theorem. P8 records the reduction as standard |
| N3 | An exact `ε̂` does **not** determine `|S_I|`, the number of connected components, the persistence or connectivity structure, or whether `A` is a uniform sample. None of these is claimed |
| N4 | Exact counting and uniform sampling are recorded as possible later investigations and were **not begun** |
| N5 | The pilot cannot establish that the paper's empirical trade-off generalises to larger `n`: 15 instances per size, no held-out split, and no `|S_I|` denominator |
| N6 | Any complexity comparison must use the **encoded** size (`n + n_aux`, see M1). Substituting the original `n` into a theorem about the enlarged formula would be wrong by a factor of ~334 in variable count on instance 40 alone |
| N7 | `src/drup.py` is my own checker and has **not** been cross-validated against an established tool such as `drat-trim`, which this environment declined to fetch and compile. It rejects a tampered proof and agrees with the exhaustive route wherever both ran, but it is not an independently audited checker |

## Unresolved

| # | Statement |
|---|---|
| U1 | Whether the paper's resolution/connectivity trade-off persists beyond `n = 20` — the pilot measures feasibility, not the phenomenon |
| U2 | Whether a better cardinality encoding (totalizer variants, native PB, or a direct distance propagator) removes the `|A| · n · r` blow-up of M2 |
| U3 | Whether proof checking can be made cheap enough to certify every query at pilot sizes |
