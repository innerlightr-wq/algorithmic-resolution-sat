# Claims — equal-size certified comparison, 2026-10-27

Adds to `../CLAIMS.md`, `../continuation-2026-10-27/CLAIMS_ADDENDUM.md` and
`../optimization-2026-10-27/CLAIMS.md`; erases nothing in any of them.

Levels: **proved** (mathematics); **witness-verified** (SAT model re-checked by
the original `src/verify.py`, no SAT library and no encoder); **proof-checked**
(DRUP proof accepted by pinned `drat-trim` @ `2e3b2dc` under its strict verdict
rule); **transfer-certified** (derived from an already-certified interval by a
proved inequality plus an exact distance computation, with no new SAT call);
**measured**; **unresolved**.

## Proved

| # | Statement | Where |
|---|---|---|
| E1 | For `B ⊆ A` nonempty: `ε(A) ≤ ε(B)`. Inclusion monotonicity — removing solutions cannot improve resolution | `PROTOCOL.md` §5; verified against enumeration on 72 subset cases |
| E2 | `ε(B) ≤ ε(A) + h(A,B)` where `h(A,B) = max_{a∈A} min_{b∈B} d_H(a,b)`, by the triangle inequality | same |
| E3 | Hence a **certified** `[L_A, U_A]` transfers to `[L_A, min(n, U_A + h(A,B))]` | same |
| E4 | Any validated witness `x` gives `ε(B) ≥ min_{b∈B} d_H(x,b)`, which for `B ⊆ A` is weakly stronger than the same witness's bound for `A` | verified, `src/test_eq.py` |
| E5 | On the **same** formula, two observed sets of equal cardinality have **equal coverage fractions**, since `|S_I|` is the same constant in both ratios — true without knowing `|S_I|` | `PROTOCOL.md` §1 |
| E6 | **Cardinality alone does not order resolution.** A 7-element set can have strictly worse resolution than a 2-element set on the same space (`ε = 5` vs `ε = 3`, `n = 6`). Monotonicity applies to **inclusion**, not to size | explicit control, `src/test_eq.py` |
| E7 | Pooling certified evidence across runs keyed on `(formula hash, observed-set hash)` is sound: certified statements about the same `(I, A)` are facts, so the strongest lower and strongest upper bound found in any run may be combined | `src/eqcore.py`; asserted non-contradictory at load |

## Measured — the main result

| # | Statement | Level |
|---|---|---|
| E8 | **7 instances** tested, one per nonempty `(n, density)` stratum (n = 32, 48, 64 × α = 2.5, 3.5, 4.2), selected by sha256 of the original formula. **21 distinct observed sets**, 0 duplicates | measured |
| E9 | WalkSAT's set was larger in **all 7**, so W was subsampled and C left untouched in every case; `k` = 38–40 | measured |
| E10 | **6 of 7 instances certified `ε_C > ε_W`** after equalising distinct-set size; **1 certified equality**; **0 certified `ε_W > ε_C`**; **0 unresolved** | proof-checked + transfer-certified |
| E11 | **7 of 7 instances certified consistently across all three replicates.** No instance varied; none was partly or entirely unresolved | proof-checked |
| E12 | The one equality instance (`n48_a4.2_k1`) was **already** a certified equality at unequal sizes, so **no instance changed its verdict** | proof-checked |
| E13 | **5 of 21 orderings certified from transferred bounds alone**, with zero new SAT calls (`n48_a3.5_k0` ×3, `n64_a4.2_k1` ×2) | transfer-certified |
| E14 | New work totalled **29 certified UNSAT queries, 0 SAT, 0 unchecked UNSAT, 0 UNKNOWN**, in 29 s; the whole comparison took **32 s**; 0 overshoots, 0 hard kills | proof-checked |
| E15 | Two queries sufficed per unresolved measurement (one for the equality case), because policy D targets `r = U_O` then `r = L_O − 1` | measured |
| E16 | Subsampled encodings are ~¼ the size of the full-`A_W` encodings that made the original n=64 measurements hard — which is why this stage was cheap | measured |

## Measured — direction versus magnitude

| # | Statement | Level |
|---|---|---|
| E17 | **Subsampling W can only shrink the gap, never widen it**, since `ε_W(B) ≥ ε_W(A)` and `ε_C` is unchanged. The test is therefore "does the gap survive the worst that equalising can do to W?" | proved + measured |
| E18 | The gap's **upper** end equals the original exact gap (8, 9, 16, 0, 12, 13, 11), because `ε_W`'s certified lower bound did not move | proof-checked |
| E19 | The gap's **lower** end is certified `≥ 1` on five instances, `≥ 7` on `n48_a3.5_k0`, and exactly `0` on the equality instance | proof-checked + transfer-certified |
| E20 | **The magnitude of the advantage is bounded, not pinned down.** Querying stopped at the ordering by design, so equal-size `ε_W` values are intervals; the gap could be as small as 1 on five of the six | measured |

## Measured — the historical equal-size sets (secondary)

| # | Statement | Level |
|---|---|---|
| E21 | The original pilot's equal-size subsets are exact **first-discovery prefixes** `AWf[:k]`, not uniform samples — confirmed on all 7 cohort cells | measured |
| E22 | They were built with `want_proof=False`, so **no upper bound in that comparison was ever independently checked** | measured |
| E23 | Pooling all certified evidence in the project, **every** historical equal-size pair is **unresolved** (upper bounds sit at the arithmetic bound `n`) | measured |
| E24 | The **prefix construction yields a higher certified lower bound for `ε_W` than a uniform subsample of the same size** in 6 of 7 cells (12 vs 9, 20 vs 17, 11 vs 6, 27 vs 24, 24 vs 15, 13 vs 7; equal at 2 in the seventh), consistent with correlated early discoveries covering `S_I` less evenly | measured |
| E25 | For the prefix construction the `ε_W` intervals **overlap `ε_C` from below and extend above it**, so a reversal is **not excluded** there. The present finding is specific to **uniform** subsamples | measured |

## Validation

| # | Statement | Level |
|---|---|---|
| E26 | 11/11 validation checks pass: deduplication/canonicalization/cardinality; deterministic replicate reproduction; subset inclusion and assignment validity; **both** transferred inequalities against enumeration; exact `h(A,B)`; witness lower bounds; classification of overlapping vs separated intervals; the larger-set-worse-resolution control; refusal of an upper bound supported only by unchecked UNSAT; restart and cross-`A` isolation; retained proof-checking controls | measured |
| E27 | The `[29,30]` → `[29,64]` correction is **regression-tested**: an upper bound whose only support is an unchecked UNSAT is refused as a transfer source | measured |

## Not claimed

| # | Statement |
|---|---|
| N-E1 | **No intrinsic solver ranking.** This is the geometry of existing recorded sets after subsampling, on 7 instances |
| N-E2 | **No equal computational effort.** WalkSAT ran 150×3 000 flips; CDCL ran 5 truncated `enum_models` runs at 8 models. Matching cardinality does not match effort, and those budgets were never calibrated |
| N-E3 | **No uniform sampling of `S_I`.** Subsampling makes a recorded set uniform *within itself*; it cannot repair a biased recorded set |
| N-E4 | **No coverage fraction.** E5 gives only the equality of two unknown fractions; `|S_I|` is unavailable |
| N-E5 | **No p-value, no significance claim.** Replicates are nested within instances and are not independent observations; the instance count (7) is the honest denominator |
| N-E6 | **No population-wide inference.** One `n` range, one solver pair, one encoding, 7 instances, one subsampling scheme |
| N-E7 | **No claim about prefix subsets**, which E24–E25 show behave differently and remain unresolved |
| N-E8 | **No symmetric experiment.** Giving C a budget that yields `\|A_C\| ≈ 150` would require generating new solutions, which was forbidden and is a different study |

## Unresolved

| # | Statement |
|---|---|
| U-E1 | The **magnitude** of the equal-size gap on five of the six `C > W` instances: certified to `[1, original gap]`, not pinned down |
| U-E2 | Exact equal-size `ε_W` values — not attempted, since the objective was the ordering |
| U-E3 | Whether the ordering survives **budget-calibrated** rather than cardinality-matched comparison. This is the substantive open question and needs a fresh study |
| U-E4 | Whether the ordering survives the **first-discovery** subsampling scheme, which E25 leaves open |
| U-E5 | Whether any of this generalises beyond 7 instances at n = 32–64 |
