# ORIGINAL_EXPERIMENT_AUDIT.md — Reaudit of the January experiments (Phase 6)

**The January paper's own code was not found locally** ("Data Availability: Code is available upon request"; no matching script exists near `~/Downloads/GeometricResolution.pdf`). Everything numeric below is an **independent reconstruction** — different RNG stream, different instances, same stated parameters (`n∈{15,18,20}`, `α∈{2.0,3.0,3.5,4.0,4.2}`, 50 satisfiable instances/cell, cap=500) — produced by `scripts/cap_confound_reconstruction.py`, raw output in `cap_confound_output.txt` / `cap_confound_results.json`. Exact per-instance numbers will not match the original paper's Tables 1–2; the qualitative question below (does `|S_I|` exceed the cap near `α=2.0`?) is governed by the ensemble-level first-moment/annealed entropy of random 3-SAT, which is a property of `(n,α)`, not of any one seed, so it should reproduce robustly. This is disclosed as reconstruction, per task instructions, not presented as a replication of the original run.

## 1. The 500-cap confound: **confirmed, and severe**

| `n` | `α` | mean `\|S_I\|` | median `\|S_I\|` | min `\|S_I\|` | max `\|S_I\|` | frac(`\|S_I\|`>500) |
|---|---|---|---|---|---|---|
| 15 | 2.0 | 625.6 | 575 | 205 | 1168 | **0.64** |
| 15 | 3.0 | 86.6 | 71 | 6 | 396 | 0.00 |
| 15 | 3.5–4.2 | ≤35.5 | ≤30 | 1 | ≤154 | 0.00 |
| 18 | 2.0 | 2299.7 | 2203.5 | **527** | 4996 | **1.00** |
| 18 | 3.0 | 172.5 | 131 | 14 | 640 | 0.06 |
| 18 | 3.5–4.2 | ≤61.7 | ≤36 | 1 | ≤313 | 0.00 |
| 20 | 2.0 | 5380.0 | 4664.5 | **1439** | 11064 | **1.00** |
| 20 | 3.0 | 296.9 | 238.5 | 20 | 992 | 0.18 |
| 20 | 3.5–4.2 | ≤97.9 | ≤57.5 | 1 | ≤341 | 0.00 |

(Full table for all cells in `cap_confound_output.txt`.)

**Verdict: the hypothesis is not just plausible, it's the dominant effect at `α=2.0` for `n≥18`.** At `n=18` and `n=20`, `α=2.0`, **every single reconstructed instance** (min `|S_I|` = 527 and 1439 respectively) has more true solutions than the 500-solution cap can hold — meaning the theoretical maximum achievable coverage for *any* capped algorithm (this includes the paper's own DPLL and local-search runs, since the paper states the cap applies "except exhaustive") is bounded above by roughly `500/2300 ≈ 22%` at `n=18` and `500/5380 ≈ 9%` at `n=20` on average — **regardless of algorithm quality**. Any algorithm-vs-algorithm coverage comparison at `α=2.0, n≥18` is therefore measuring, in large part, how differently algorithms saturate a shared low ceiling, not how differently they search.

At `n=15`, the effect is real but softer: 64% of instances exceed the cap, mean `|S_I|=626` against a cap of 500, giving an average ceiling around `500/626 ≈ 80%`. The paper's reported Table 2 coverage at `n=15, α=2.0` is: DPLL 88.8%, Local Search 46.8%, Random 47.0%, Biased 44.8%. DPLL's number is close to the reconstructed ~80% ceiling (plausible — DPLL with unit propagation is a strong, low-redundancy enumerator, so it may be hitting close to the cap-limited ceiling on many instances, i.e. its high coverage figure is *itself* partly a cap artifact, not unconstrained superior search). Local Search/Random/Biased sit well below even that reduced ceiling (~45–47% vs. ~80% ceiling), so for these three algorithms specifically, low coverage at `n=15, α=2.0` **cannot** be fully explained by the cap alone — genuine algorithmic under-coverage is also present, on top of the cap effect. **This is a real, nuanced finding: the cap confound and genuine algorithmic weakness are superimposed at `n=15`, and the cap confound alone plausibly explains most or all of the effect at `n≥18`.** The original paper does not disentangle these, and does not report `n=18,20` coverage tables in the extracted text at all (only `n=15` tables 1–3 appear in the 9-page draft), so this concern may already be implicitly worse in unreported cells.

## 2. Consequence for `ε̂` (resolution) at `α=2.0`

Because `ε̂(A,I)` is the Hausdorff distance from `A(I)` to `S_I` (`V2_DEFINITIONS.md` §0), and a capped `A(I)` necessarily omits a large, essentially **arbitrary** (cap-order-dependent, e.g. "first 500 found by DPLL's branching order") subset of `S_I` when `|S_I|≫500`, the reported `ε̂` values at `α=2.0` (Table 1: DPLL 0.12, Local Search 1.10, Random 1.06, Biased 1.36) partially reflect **which 500 of thousands of solutions the cap happened to retain**, not a clean measurement of each algorithm's geometric blind spot. A cap-truncated `A(I)` is not the same object as an *algorithmically failure-limited* `A(I)`, and the paper's interpretive language ("structured blind zones," Remark 5.1) does not distinguish the two.

## 3. Biased-sampler circularity (cross-reference)

Restated briefly here since it belongs to the same Phase 6 reaudit scope (full protocol fix is in `EXPERIMENT_DESIGN.md` §1): the biased sampler is *constructed* to prefer low-Hamming-weight assignments (§4.2(e) of the paper), then found to have a blind zone concentrated on high-Hamming-weight solutions (Table 4, mean weight 5.2 found vs. 9.8 missed). The predictor (weight) and the mechanism (weight-biased construction) coincide, so this specific result mostly re-confirms the sampler's own design rather than demonstrating a *predictable-from-solver-dynamics* blind zone for an algorithm not hand-built around the predictor. DPLL and local search, which are *not* hand-built around Hamming weight, are the more informative test cases for a genuine "predictable blind zone" claim, and the January draft does not characterize their blind zones with the same rigor it applies to the biased sampler (Table 3 has fewer entries for DPLL/Local Search, none for `α≥3.5`+ where `A(I)` presumably achieves 100% coverage per Table 2 and so has no blind zone to characterize).

## 4. Scale limitations (restated, not newly discovered)

Exhaustive ground truth requires `n≤20` (confirmed practical: the reconstruction's `n=20` runs, vectorized, complete in well under a second per instance). This is a hard ceiling on what any version of this experiment (original or Phase 5's upgrade) can validate against *true* ground truth; it is honestly stated in the paper's own §8.1 and remains the correct, unavoidable limitation — not something this audit found reason to dispute or that Phase 5 removes (see `EXPERIMENT_DESIGN.md` §2.5).

## 5. Which original empirical claims remain supported after this reaudit

| Claim | Status after reaudit |
|---|---|
| "Different algorithms exhibit systematically different resolution profiles" (Table 1, general trend across `α≥3.0`) | **Supported** — the cap confound is concentrated at `α=2.0`; at `α≥3.0` (where `frac(\|S_I\|>500)` is ≤18% and typically 0%), the reported `ε̂`/coverage differences plausibly reflect real algorithmic differences, consistent with the reconstruction's cell-by-cell `\|S_I\|` staying well under 500 for `α≥3.5` uniformly. |
| "Biased sampler has structured (Hamming-weight-linked) blind zone" | **Supported but circular** (§3) — true as measured, but weak evidence for the *general* predictability claim; needs the non-circular predictors of `EXPERIMENT_DESIGN.md`. |
| "Apparent clustering can be observer-induced" (Example 5.1) | **Supported as a single documented instance**; strengthened, not weakened, by `V2_DEFINITIONS.md` §2.2's stability-theorem framing (it is not just anecdote — it's the expected consequence of `ε̂` being comparable to the true cluster-spectrum's feature scale in that example). |
| "α=2.0 shows the lowest coverage / worst resolution across all algorithms" (if read as "hardest instances," i.e. reflecting instance difficulty) | **Not supported as stated — this reaudit's central finding.** At `α=2.0`, low reported coverage for capped algorithms is dominated by `\|S_I\|≫500` cap truncation, especially at `n≥18` where it is a near-total ceiling effect; it should not be read as evidence about algorithmic search quality at this `α` without first controlling for the cap. |
| Cross-`α` monotonic trend narrative implied by Tables 1–2 (resolution/coverage "improving" as `α` increases toward the threshold) | **Confounded** — improvement from `α=2.0` to `α=3.0` in the original tables is at least partly a mechanical consequence of `\|S_I\|` shrinking below the cap (reconstruction: mean `\|S_I\|` drops from 626–5380 at `α=2.0` to 87–297 at `α=3.0`, a 3–18× drop, comfortably under the cap at every `n`), not solely evidence about algorithms finding structure more easily as instances get harder. |

## 6. Recommendation for V2

Either (a) remove the fixed 500-cap and report coverage/resolution only for `α` where `|S_I|` is reliably `≲` cap (a data-driven, per-instance check, not a fixed global threshold), or (b) keep the cap but report **capped coverage relative to the cap-limited ceiling** (`|A(I)|/min(|S_I|,cap)`) as a *separate* column alongside raw coverage (`|A(I)|/|S_I|`), so that cap-driven and algorithm-driven under-coverage are visually and statistically distinguishable. Report `|S_I|` itself (or at least whether `|S_I|>cap`) per instance/cell in every table where the cap is active — its absence from the January draft's tables is the single biggest methodological gap this reaudit found.
