# Equal-size certified comparison — report

Dated 2026-10-27. Workspace `equal-size-certification-2026-10-27/`. The original
audit, `continuation-2026-10-27/` and `optimization-2026-10-27/` are preserved.
No repository or manuscript was modified; nothing was committed, pushed or
published; instance sizes were not increased.

Protocol frozen before measurement: `PROTOCOL.md`. Claims: `CLAIMS.md`.
Manifests: `data/cohort_manifest.json`, `data/subsampling_manifest.json`,
`MANIFEST.md`. Machine-readable: `data/paired_results.csv`,
`data/equalsize_summary.json`, `data/transfer_only.json`. Logs: `results/`.

Read-only reference: <https://github.com/innerlightr-wq/algorithmic-resolution-sat>
(local clone `../repo`, commit `2bef5a8`).

---

## 1. The question and the answer

**Question.** The ordering audit certified `ε_C > ε_W` on 31 of 32 instances —
but WalkSAT's recorded set is larger in 31 of those 32 (typically 150 vs 40),
and a smaller observed set mechanically admits a larger covering radius. Does
the resolution advantage **persist after matching the number of distinct
solutions** in the two recorded sets?

**Answer: it persists, on every instance tested, in every replicate.**

| | instances | measurements |
|---|---|---|
| certified `C > W` | **6 / 7** | 18 / 21 |
| certified equality | **1 / 7** | 3 / 21 |
| certified `W > C` (reversal) | **0** | **0** |
| unresolved | **0** | **0** |
| certified consistently across all 3 replicates | **7 / 7** | — |

The single equality instance (`n48_a4.2_k1`) was *already* a certified equality
at unequal sizes, so **no instance changed its verdict**.

**What this is not.** This examines the geometry of the **existing recorded
sets** after controlled subsampling. It does not establish an intrinsic solver
ranking, equal computational effort, or uniform sampling from `S_I`. The two
sets came from different procedures under different budgets, and subsampling one
of them does not retroactively equalise those procedures.

**The coverage fact, exactly.** Coverage is `|A|/|S_I|`. On the same formula,
two observed sets of equal cardinality have **equal coverage fractions**,
because `|S_I|` is the same constant in both ratios — true without knowing
`|S_I|`. **No coverage value is computed or reported anywhere here**, and none
can be without `|S_I|`.

---

## 2. Cohort and construction

Rule **R-EQ**, frozen before measurement: one instance per nonempty
`(n, density)` stratum among the 32 certified pairs, ordered by **sha256 of the
original formula** — independent of effect size, runtime, and of any previous
equal-size attempt. Seven nonempty strata, cap of nine, so every stratum is
represented. Selected and all 25 unselected ids: `data/cohort_manifest.json`.

| stratum | selected | formula sha256 | of | `\|A_W\|` | `\|A_C\|` | k | subsampled side |
|---|---|---|---|---|---|---|---|
| n32_a2.5 | `n32_a2.5_k4` | `b9b65084cc19a86e…` | 3 | 150 | 40 | 40 | W |
| n48_a2.5 | `n48_a2.5_k0` | `364c8c6b14540c34…` | 5 | 150 | 40 | 40 | W |
| n48_a3.5 | `n48_a3.5_k0` | `03f215283a667ff2…` | 5 | 129 | 40 | 40 | W |
| n48_a4.2 | `n48_a4.2_k1` | `2dd448b98891e48f…` | 4 | 44 | 38 | 38 | W |
| n64_a2.5 | `n64_a2.5_k4` | `0ad6252e5cb2ccde…` | 5 | 150 | 40 | 40 | W |
| n64_a3.5 | `n64_a3.5_k3` | `02cba22532a7a7ba…` | 5 | 150 | 40 | 40 | W |
| n64_a4.2 | `n64_a4.2_k1` | `06151167e21926d3…` | 5 | 140 | 38 | 38 | W |

WalkSAT's set was the larger one in all seven, so **W was subsampled and C was
left untouched** in every case. Three prespecified replicates per instance,
drawn uniformly without replacement from the lexicographically canonicalized
set, seeded from `sha256("20261027|<formula>|<label>|<replicate>")` under
`numpy.random.Generator(PCG64)`. Every assignment in both sets was validated
against the original formula; both set hashes were required to match the
continuation journal (recovery, never substitution).

**21 measurements, 21 distinct subsets, 0 duplicates.** Actual sets and hashes
are saved, not just seeds (`data/subsampling_manifest.json`).

---

## 3. Existing certificates did much of the work

For `B ⊆ A`, with `h(A,B) = max_{a∈A} min_{b∈B} d_H(a,b)`:

```
eps(A)  <=  eps(B)  <=  eps(A) + h(A,B)
```

lower by inclusion monotonicity, upper by the triangle inequality (both
verified against enumeration on 72 subset cases). A **certified** `[L_A, U_A]`
therefore transfers to `[L_A, min(n, U_A + h(A,B))]`, and every re-verified
stored witness `x` additionally gives `eps(B) >= min_{b∈B} d_H(x,b)`.

Certified evidence was pooled across **every journal in the project**, keyed on
`(formula hash, observed-set hash)` rather than on names — which is what makes
pooling safe. This tightened `n64_a2.5_k4`'s starting interval from `[19,54]` to
`[24,47]` by picking up the optimization stage's own certified result for the
same measurement.

**5 of 21 orderings were certified from transferred bounds alone, with zero SAT
calls** — `n48_a3.5_k0` on all three replicates and `n64_a4.2_k1` on two. A
solver-reported upper bound was never transferred; the earlier `[29,30]` →
`[29,64]` correction remains in force and is regression-tested.

---

## 4. Results

Original unequal-size and new equal-size results are kept in separate columns
(`data/paired_results.csv`). `ε_W` is the subsampled side throughout.

| instance | orig `ε_W` | orig `ε_C` | orig verdict | equal-size `ε_W` (r0/r1/r2) | `ε_C` | difference interval | equal-size verdict |
|---|---|---|---|---|---|---|---|
| `n32_a2.5_k4` | `[9,9]` | `[17,17]` | C > W | `[9,16]` ×3 | `[17,17]` | `[1,8]` | **certified C > W** |
| `n48_a2.5_k0` | `[17,17]` | `[26,26]` | C > W | `[17,25]` ×3 | `[26,26]` | `[1,9]` | **certified C > W** |
| `n48_a3.5_k0` | `[6,6]` | `[22,22]` | C > W | `[8,14]` / `[6,15]` / `[6,12]` | `[22,22]` | `[8,14]`/`[7,16]`/`[10,16]` | **certified C > W** |
| `n48_a4.2_k1` | `[2,2]` | `[2,2]` | equality | `[2,2]` ×3 | `[2,2]` | `[0,0]` | **certified equality** |
| `n64_a2.5_k4` | `[24,25]` | `[36,36]` | C > W | `[24,35]` ×3 | `[36,36]` | `[1,12]` | **certified C > W** |
| `n64_a3.5_k3` | `[15,15]` | `[28,28]` | C > W | `[17,27]` / `[15,27]` / `[15,27]` | `[28,28]` | `[1,11]`/`[1,13]`/`[1,13]` | **certified C > W** |
| `n64_a4.2_k1` | `[7,7]` | `[18,18]` | C > W | `[7,16]` / `[7,17]` / `[7,17]` | `[18,18]` | `[2,11]`/`[1,11]`/`[1,11]` | **certified C > W** |

### 4.1 Cost

| | |
|---|---|
| measurements needing new SAT work | 16 of 21 |
| new queries | **29 certified UNSAT, 0 SAT, 0 unchecked UNSAT, 0 UNKNOWN** |
| new solving / checking / wall time | 12 s / 13 s / **29 s** |
| whole comparison | **32 s** |
| budget overshoots, hard kills | **0, 0** |

Two queries sufficed per unresolved measurement (one for the equality case).
Policy D aims directly at the opponent's bound: `r = U_O` then `r = L_O − 1`.
The cheapness is structural — the subsampled sets have `k = 38–40` rather than
`|A_W| = 129–150`, so the encodings are roughly a quarter the size of the ones
that made the original n=64 measurements hard.

### 4.2 Direction is certified; magnitude is not

Querying stopped as soon as the ordering was certified, by design, so the
equal-size `ε_W` values are intervals rather than exact. The consequence is
precise and worth stating:

* `ε_W(B) >= ε_W(A)` always (inclusion monotonicity), and `ε_C` is unchanged, so
  **subsampling W can only shrink the gap, never widen it**. The test is
  therefore exactly "does the gap survive the worst that equalising can do to
  W?"
* The gap's **upper** end equals the original exact gap (8, 9, 16, 0, 12, 13,
  11) because `ε_W`'s certified lower bound did not move.
* The gap's **lower** end is certified `≥ 1` on five instances, `≥ 7` on
  `n48_a3.5_k0`, and exactly `0` on the equality instance.

So: the advantage **did not vanish and did not reverse** on any instance. Whether
it *shrank in magnitude* is bounded but not pinned down — it could be as small
as 1 on five of the six. Reaching exact equal-size values was not the objective
and was not attempted.

---

## 5. Appendix — the historical equal-size sets (secondary, not promoted)

Audited, kept separate, and deliberately **not** promoted into the primary
cohort (`results/appendix_historical.txt`).

Two provenance facts about how the original pilot built them
(`src/pilot.py`: `covering_radius(AWf[:eq], …, want_proof=False)`):

1. `AWf` is deduplicated in **first-discovery order**, so `AWf[:k]` is the
   earliest `k` solutions the solver happened to find — **not a uniform
   sample**. Confirmed: all seven historical sets are exact prefixes.
2. `want_proof=False`, so **no upper bound in that comparison was ever
   independently checked**.

Consequently, pooling all certified evidence in the project, every historical
equal-size pair is **unresolved**:

| cell | historical `ε_W` certified | `ε_C` | verdict |
|---|---|---|---|
| `n32_a2.5_k4` | `[12,32]` | `[17,17]` | unresolved |
| `n48_a2.5_k0` | `[20,48]` | `[26,26]` | unresolved |
| `n48_a3.5_k0` | `[11,48]` | `[22,22]` | unresolved |
| `n48_a4.2_k1` | `[2,48]` | `[2,2]` | unresolved |
| `n64_a2.5_k4` | `[27,64]` | `[36,36]` | unresolved |
| `n64_a3.5_k3` | `[24,64]` | `[28,28]` | unresolved |
| `n64_a4.2_k1` | `[13,64]` | `[18,18]` | unresolved |

One observation that cuts against the headline and is reported as such: the
**first-discovery prefix yields a higher certified lower bound for `ε_W` than a
uniform subsample of the same size** in six of seven cells (12 vs 9, 20 vs 17,
11 vs 6, 27 vs 24, 24 vs 15, 13 vs 7; equal at 2 in the seventh). That is
consistent with early WalkSAT discoveries being correlated and covering `S_I`
less evenly than a uniform draw. For the prefix construction the intervals
**overlap `ε_C` from below and extend above it**, so a reversal is *not
excluded* there. The present finding is therefore specifically about **uniform**
subsamples of the recorded sets; it is not a statement about prefix subsets, and
the historical construction neither supports nor contradicts it.

---

## 6. Answers

**1. How many instances and distinct observed sets were actually tested?**
**7 instances**, one per nonempty `(n, density)` stratum, spanning n = 32, 48,
64 and densities 2.5, 3.5, 4.2. **21 distinct subsampled observed sets** (7 × 3
replicates, all 21 hashes distinct, 0 duplicates), each compared against the
untouched opposite-side set. 25 instances in those strata were not selected and
are listed in the cohort manifest.

**2. How many orderings were certified from transferred bounds alone?**
**5 of 21 measurements**, with **zero** new SAT calls: `n48_a3.5_k0` on all
three replicates and `n64_a4.2_k1` on replicates 0 and 1. Each records its full
provenance — originating certificate, subset hash, the exact `h(A,B)`
computation, and the implication.

**3. After equalizing distinct-set sizes, how often was C > W, W > C, equality,
or unresolved?** At the honest (instance) denominator of 7: **6 certified
`C > W`, 1 certified equality, 0 certified `W > C`, 0 unresolved.** At the
measurement level (21, *not* independent): 18 / 3 / 0 / 0.

**4. Were the outcomes consistent across the three subsampling replicates?**
**Yes — 7 of 7 instances certified consistently**, with the identical verdict in
all three replicates. No instance varied, and none was partly or entirely
unresolved. The underlying intervals did vary slightly between replicates (e.g.
`n48_a3.5_k0`: `[8,14]`, `[6,15]`, `[6,12]`), as different subsets give
different `h(A,B)` and different witness bounds, but never enough to change a
verdict.

**5. Did the original advantage shrink, disappear, reverse, or remain?**
**It remained, certified, on every instance.** Nothing disappeared and nothing
reversed: 0 instances became unresolved and 0 reversed. Distinguishing
certified from unresolved: *certified* is that `ε_C > ε_W` still holds on the
six, that the gap is at least 1 (at least 7 on `n48_a3.5_k0`), and that the
seventh remains an exact equality. *Not certified* is the gap's **magnitude** —
subsampling can only shrink it, and we bounded it to `[1, original gap]` on
five of the six rather than pinning it down, because querying stopped at the
ordering by design.

**6. What limitations remain because the underlying solution-generation budgets
and procedures differ?** The substantive ones, and they are not small:

* Equalising **cardinality is not equalising effort**. WalkSAT ran 150 restarts
  × 3 000 flips; the CDCL side ran 5 permuted `enum_models` runs truncated at 8
  models. Those budgets were never calibrated against each other, and the
  manuscript itself names this ("CDCL's tested budget gave it systematically
  lower mean coverage than WalkSAT on the same instances").
* Only **W was subsampled**, because it was larger in all seven. The symmetric
  experiment — giving C a budget that produces `|A_C| ≈ 150` — would require
  generating new solutions, which is forbidden here and is a different study.
* Neither set is a **uniform sample of `S_I`**. Subsampling makes the recorded
  set uniform *within itself*; it cannot repair a biased recorded set.
* `|S_I|` is unknown, so **no coverage fraction exists** — only the equality of
  two unknown fractions.
* The appendix finding shows the result is specific to **uniform** subsamples;
  prefix subsets behave differently and remain unresolved.
* 7 instances, 3 nested replicates, one `n` range (32–64), one solver pair, one
  encoding. This is a **targeted follow-up pilot on existing data, not a fresh
  held-out study**. No p-value is computed and no population-wide solver
  ranking is claimed.

**7. Does this justify a larger fresh study, or is the evidence still too
limited?** **It justifies one, and it also shows what the study must fix.** The
positive signal is unusually clean for a pilot: 7/7 instances certified
consistently across replicates, 0 reversals, 0 unresolved, spanning three sizes
and all three densities — and it cost **32 seconds**, which means a properly
powered version is cheap, since subsampled sets are a quarter the size of the
ones that made the original measurements hard. But the evidence remains too
limited to generalise, for the reasons in answer 6, and three design
requirements follow for any fresh study: (i) **calibrate the two solvers'
budgets** so cardinality matching is not standing in for effort matching;
(ii) **pre-register both subsampling schemes** — uniform *and*
first-discovery — since they demonstrably disagree; (iii) **certify both sides
from the start** (`want_proof=True` everywhere), because the single reason the
historical equal-size comparison yields nothing is that proofs were disabled.
Until that is done, the honest statement is the certified one: on these seven
recorded instances, matching distinct-set cardinality does not remove the
resolution ordering.
