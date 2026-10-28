# Solver budget / selection pilot — report

Dated 2026-10-27. Protocol frozen and pushed **before** primary collection at
commit `b0c7a79b2a6eb20f7c58c599407112096d1764be`, which is stamped into every
primary output. **A prospective pilot, not a powered confirmation study.**

Machine-readable: `data/paired_results.csv`, `data/analysis_summary.json`,
`data/collection_index.json`, `data/collections/`, `data/groups.json`,
`data/ineligible_satisfiability.json`. Logs: `results/`.

---

## Conclusion, first

**The resolution ordering reported in the September paper survives a common time
budget only under first-discovery selection. Uniform subsampling of the very
same recorded banks destroys it.**

| at equal retained size `k = 40` | 5 s budget | 30 s budget |
|---|---|---|
| **prefix** (first 40 discoveries) | **15/15 certified `ε_C > ε_W`** | **15/15 certified `ε_C > ε_W`** |
| **uniform** (40 drawn from the bank) | 5 `C>W`, **6 `W>C`**, 3 equality, 1 unresolved | 5 `C>W`, **6 `W>C`**, 2 equality, 2 unresolved |

And the mechanism is identified, not guessed:

| prefix vs uniform, same instance, same budget | result |
|---|---|
| **CDCL** | **prefix worse than uniform in 28 of 30** |
| **WalkSAT** | uniform worse in 17 of 30, equal in 8, prefix worse in only 2 |

CDCL's first 40 discoveries are far more clustered than a uniform sample of its
own bank; WalkSAT's first 40 are already as well spread as a uniform sample.
That asymmetry — a property of `enum_models` walking one search tree versus
independent random restarts — is what the equal-size comparison was measuring.

**But the uniform result does not establish a reversal.** Under uniform
sampling the verdict **varies across the three replicates in 20 of 30
instance-budget cells**. The honest reading is that the ordering *ceases to be a
property of the instance* once sampling is uniform, not that CDCL becomes
better. The 26 certified `W > C` rows are certified facts about specific
observed-set pairs, not about the instances.

---

## 1. Denominators, explicitly

| | count |
|---|---|
| attempted instances | **18** |
| instances with both collections completed | 18 |
| of which satisfiable | **17** (`p32_a4.2_f0` is UNSAT) |
| instance-budget groups | 36 |
| eligible (both solvers reached `k = 40`) | **30** |
| ineligible (insufficient sample) | 6 |
| not attempted (overall cap) | **0** |
| scheme-level comparisons | 144 |
| certified | **110** |
| unresolved | 10 |
| ineligible | 24 |

Collection: 1118 s, **0 resource-limited**. Certification: 1487 s, **0 budget
overshoots, 0 alarms**, max group time 300.3 s against the 300 s allocation.
Total including calibration and validation: ≈ 60 min against the 4 h cap.

## 2. Collection, and what "insufficient sample" actually meant

5 of 36 solver-instance cells failed to reach `k = 40` at either budget. The
protocol forbids reading that as poor geometry, so each was classified with a
complete solver (`data/ineligible_satisfiability.json`):

| instance | complete-solver verdict | correct reading |
|---|---|---|
| `p32_a4.2_f0` | **UNSAT** | no solutions exist; both solvers correctly returned 0. Retained in the attempted denominator, excluded from satisfiable |
| `p32_a4.2_f1` | **SAT, exactly 2 models** | the **formula** has fewer than 40 solutions — established independently, not inferred from the sample |
| `p64_a4.2_f0` | **SAT, ≥ 60 models** | WalkSAT recorded 27 in 30 s while CDCL recorded 68. A genuine **collection** failure, attributable to the implementation |

So of the three ineligible instances, exactly one is a solver failure. No
insufficient sample anywhere is used as evidence about resolution.

The banks themselves show the implementation asymmetry the protocol warned
about. At `n = 64, α = 2.5`: WalkSAT recorded 7 045 distinct in 30 s over 7 046
restarts with **0** duplicates; CDCL recorded 333 414 over 41 730 permuted runs.
At `n = 32, α = 2.5`: WalkSAT 9 780 distinct with 9 465 duplicates; CDCL 19 702
distinct with **642 618** duplicates. Equal wall-clock time buys the two
solvers wildly different amounts of search and of redundancy.

## 3. Table 1 — equal-size solver comparison, per budget

Full per-instance detail in `results/analysis.txt`. The pattern is uniform
across `n` and density: **every** prefix comparison, at both budgets, certifies
`ε_C > ε_W`, with difference intervals that are exact singletons
(`[1,1]` to `[19,19]`). Under uniform selection the same instances split
roughly evenly, with difference intervals as small as `[-1,-1]` and as large as
`[12,12]`.

Two illustrative rows (`results/analysis.txt` has all 60):

```
p48_a2.5_f0   5  prefix    W=[19,19]  C=[25,25]  diff=[6,6]   certified C > W
p48_a2.5_f0   5  uniform0  W=[20,20]  C=[19,19]  diff=[-1,-1] certified W > C
```

Same instance, same budget, same retained size — opposite certified verdicts,
differing only in which 40 of the recorded solutions were kept.

## 4. Table 2 — prefix versus uniform, within each solver

This is the mechanism, and it is the most robust finding here.

| solver | n | certified prefix worse (`uniform > prefix`) | certified prefix better | equality | unresolved |
|---|---|---|---|---|---|
| **W** | 30 | 17 | 2 | 8 | 3 |
| **C** | 30 | **28** | 2 | 0 | 0 |

CDCL's chronological prefix has strictly worse resolution than a uniform sample
of its own bank in 28 of 30 cells. WalkSAT's does not: it is better or equal in
25 of 30. Under `enum_models`, consecutive solutions come from one walk of a
single permuted search tree and are correlated; WalkSAT's come from independent
restarts. Equalising cardinality does nothing about that, which is why the
equal-size question is genuinely two questions.

## 5. Table 3 — short versus long budget

| solver | scheme | n | equality | long worse | short worse | unresolved |
|---|---|---|---|---|---|---|
| W | prefix | 15 | **13** | 0 | 0 | 2 |
| C | prefix | 15 | **15** | 0 | 0 | 0 |
| W | uniform0 | 15 | 4 | 6 | 4 | 1 |
| C | uniform0 | 15 | 3 | 7 | 3 | 2 |

**Prefix selection is essentially budget-independent**: the first 40 distinct
discoveries arrive well inside 5 s, so a 6× longer budget changes nothing (28 of
30 cells certified equal). Uniform selection does move, because the bank grows —
but it moves in both directions, consistent with sampling variability rather
than with a budget effect.

Four CDCL cells had **identical 5 s and 30 s banks** (enumeration saturated
before the short deadline), exactly as calibration predicted; for those the
budget contrast carries no information and is reported as such.

## 6. Replicate sensitivity — the load-bearing caveat

Uniform replicate 0 is the primary comparison; 1 and 2 are sensitivity checks,
**not** extra instances.

> **In 20 of 30 instance-budget cells the uniform verdict varies across the
> three replicates.**

So the uniform column of Table 1 is not a stable per-instance result. A
certified `W > C` row is a certified statement about one pair of 40-element
observed sets; a different seed on the same banks can certify the opposite. This
is why §Conclusion says the advantage *disappears into instability* rather than
*reverses*.

By contrast the prefix result has no such freedom: the prefix is deterministic
given the bank, and it certified `C > W` in 30 of 30 eligible cells.

## 7. Answers

**1. Did the resolution advantage persist under a common time budget and equal
retained size?** **It depends entirely on the selection scheme, and that is the
finding.** Under first-discovery prefix selection it persisted completely:
**30 of 30** eligible comparisons certified `ε_C > ε_W` (15 at each budget), no
reversals, no equalities, nothing unresolved. Under uniform subsampling of the
same banks it did not persist: 10 `C>W`, 12 `W>C`, 5 equality, 3 unresolved
across both budgets.

**2. Did first-discovery prefixes behave differently from random subsamples?**
Yes, decisively, and asymmetrically between solvers. CDCL's prefix is certified
worse than its own uniform sample in **28 of 30** cells; WalkSAT's prefix is
better or equal in **25 of 30**. The paper's ordering under a time budget is
therefore driven by CDCL's first-discovery clustering, not by the content of its
recorded solution set.

**3. Were those differences certified, or merely suggested by bounds?**
**Certified.** All 110 eligible comparisons that resolved did so with exact
singleton intervals on both sides — every bound carries a validated witness or
an independently checked UNSAT proof, 0 alarms, 0 unchecked UNSATs. The 10
unresolved comparisons are reported as unresolved and are not interpreted.

**4. Did the ordering change between the two collection budgets?** Hardly at
all under prefix selection (28 of 30 cells certified *equal* across budgets),
because the first 40 discoveries arrive long before 5 s. Under uniform selection
it moved in both directions (13 long-worse, 7 short-worse, 7 equal, 3
unresolved), which is sampling variability, not a budget effect. Four CDCL cells
had identical banks at both budgets and carry no budget information at all.

**5. How often did either solver fail to supply the required sample?** 5 of 36
solver-instance cells at each budget, spanning 3 instances. Of those, one
instance is **UNSAT**, one has **exactly 2 models** (so no procedure could reach
40), and only **one** — `p64_a4.2_f0`, WalkSAT, 27 of 40 — is a solver
collection failure on a formula with ample solutions. 0 resource-limited
collections.

**6. What remains unresolved because of computation, sample size, or
implementation differences?** (i) 10 comparisons hit the 300 s group budget
without certifying an ordering and stay unresolved. (ii) **Equal wall-clock time
does not equalise algorithmic work**: WalkSAT here is pure Python, Glucose3 is
compiled C behind a thin binding, and the bank sizes (7 045 vs 333 414 at
`n = 64, α = 2.5`) show the gap directly. Nothing here separates "solver
paradigm" from "implementation cost". (iii) 18 instances with repeated
observations inside each is far too small to estimate effect sizes, and no
significance test was computed. (iv) The uniform instability (20 of 30 cells)
means a properly powered study would need many more replicates per instance, or
a different estimand.

**7. Does this justify a larger fresh study?** The prefix-versus-uniform
asymmetry (answer 2) is strong, mechanistically interpretable, and cheap to
measure — it is the part worth powering properly, with budget-calibrated
collection and many replicates. But nothing here supports a solver ranking, and
the headline should not be "the ordering reverses": it is that **the ordering is
a property of the selection rule as much as of the solver**, and the September
result's equal-coverage restriction does not control for it.

## 8. What is not claimed

No universal solver ranking. No claim that the September result is wrong — its
349-instance finding used each solver's own standard budget, which is a
different design from this one, and its coverage-matched subset is a restriction
rather than a resampling. No coverage fraction is computed (that needs `|S_I|`).
No post-hoc significance test. Replicates are never counted as independent
instances. No claim that any insufficient sample reflects geometry. `n` was not
increased; the manuscript was not touched.
