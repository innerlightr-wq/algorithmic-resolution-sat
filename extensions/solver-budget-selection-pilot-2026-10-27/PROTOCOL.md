# Protocol — solver budget / selection pilot, 2026-10-27

**Frozen before any primary collection.** Calibration ran first and is
operational only (§3); no resolution was computed and no solver-ordering
outcome was inspected before this file was written and pushed. The commit SHA
of this file is recorded in every primary-study output.

**This is a prospective pilot, not a powered confirmation study.**

Scope: `extensions/solver-budget-selection-pilot-2026-10-27/`. The manuscript,
the frozen Phase 1–4 record, and the sibling extension are unchanged. No merge,
no release, no manuscript revision. `n` is not increased beyond 64.

---

## 1. Question

Under a **common implementation-level time budget** and **equal retained sample
size**, how do WalkSAT and CDCL (Glucose3) compare when their observed sets are
built by

1. taking the **first distinct discoveries** (chronological prefix), or
2. **uniformly subsampling** the solutions recorded within the budget?

This studies **these implementations and these sampling procedures**. Equal
wall-clock time does **not** equalise abstract algorithmic work: WalkSAT here is
pure Python while Glucose3 is a compiled C solver called through a thin binding,
so a second of budget buys each of them very different amounts of search. That
asymmetry is a property of the comparison and is reported, not corrected.

## 2. Seeds — disjoint from every previous cohort

| | value |
|---|---|
| calibration seed | `20261028` |
| study seed | `20261029` |
| previously used (not reused) | `20260928 + 777` (paper Stage A), `20261026` (n ≥ 24 pilot), `20261027` (equal-size study) |

## 3. Calibration — completed before this freeze

One fresh formula per `(n, density)` stratum (9 formulas) from the
**calibration** seed, inspecting only solver operation, timing, collection
throughput and resource use. Resolution, covering radius, inter-assignment
distance and solver ordering were **not** computed. Results:
`data/calibration.json`.

What it established:

* the time-budgeted collection mechanism runs correctly for both solvers; all
  18 collections used their full 30 s (CPU ≈ wall), **0 resource-limited
  outcomes**;
* **35 of 36** (stratum, solver, budget) cells reached `k = 40`; the single
  exception was WalkSAT at `n = 64, α = 4.2, 5 s` with 14 distinct;
* recorded banks are **much larger than anticipated** — up to **344 436**
  distinct solutions (CDCL, `n = 48, α = 2.5`, 30 s);
* CDCL re-finds heavily under permuted restarts (up to 486 505 duplicates),
  which is inherent to the preserved mechanism;
* for 4 CDCL cells the 5 s and 30 s banks are **identical**, so the
  short-vs-long budget contrast is degenerate there.

### 3.1 The one documented change this forced, made before the freeze

Persisting a 344 k-element bank for every cell would be gigabytes of JSON.
**Collection itself is never capped** — there is no total-solution limit, and a
run that cannot complete its budget is recorded as resource-limited rather than
reported as complete. What changes is only **persistence**:

> For every (instance, solver) collection the study always persists: the bank
> **size**, a canonical **bank hash**, the acceptance **timestamps**, every
> **retained 40-element set** with its hash, and the full collection metadata.
> The **full bank** is additionally written only when it holds **≤ 5 000**
> distinct solutions; above that the record carries
> `bank_persisted: false` and the bank hash stands in its place.

This is a storage decision, not a measurement one: no selection, no bound and
no verdict depends on it. The selected sets — which are what any later
verification needs — are always persisted in full.

## 4. Cohort

* `n ∈ {32, 48, 64}`, density `α ∈ {2.5, 3.5, 4.2}`.
* **2 fresh formulas per stratum → 18 attempted instances.**
* Generation preserves the project's own convention exactly —
  `scripts/phase2/sat_common.py:random_3sat_clauses(n, round(α·n), rng)` — with
  `rng = numpy.random.default_rng(STUDY_SEED + 100000·n + 1000·round(10α) + j)`,
  `j ∈ {0,1}`. Only the base seed differs from previous cohorts.
* **UNSAT, UNKNOWN, collection-failure and insufficient-sample outcomes are
  retained** in the attempted denominator. Difficult instances are never
  replaced.

## 5. Collection

Solver mechanisms and parameters are **preserved**; only the stopping rule
changes from a fixed count to the clock.

| solver | preserved | changed |
|---|---|---|
| WalkSAT | `max_flips = 3000`, `p_noise = 0.5`, restart behaviour | restart **count** driven by the clock instead of `K = 150` |
| CDCL | per-run clause permutation, random phase initialisation, `enum_models()` truncated at `T = 8` per run | run **count** driven by the clock instead of `R = 5` |

**Budgets: 5 s and 30 s cumulative per solver.** One collection process runs
through the **longer** budget, with a snapshot retained at the shorter one, so
the 5 s bank is by construction a prefix of the 30 s bank.

**The timed region** — identical for both solvers: the clock starts before
solver construction and covers solver initialisation, search, validation of each
assignment against the original formula, deduplication, and the collection
logging needed to record a discovery. Resolution measurement is entirely
**outside** it. An assignment is admitted only if it was validated and accepted
**strictly before** the deadline.

Recorded per collection: ordered distinct discoveries, monotonic acceptance
timestamps, seed and solver configuration, duplicate count, restart/run count,
elapsed and CPU time, peak RSS, invalid-assignment rejections, and any
resource-limit or deadline failure.

Collection seeds: `sha256("<study_seed>|collect|<formula_hash>|<solver>")`,
truncated to 32 bits.

Solvers run **sequentially on the same hardware with no competing benchmark
jobs**, and solver order rotates deterministically by instance index.

## 6. Selection — symmetric for both solvers

At each **eligible** instance-budget pair, sets of **exactly `k = 40`** distinct
solutions are built for **both** solvers:

* **prefix** — the first 40 distinct validated discoveries, chronological;
* **uniform** — 40 drawn uniformly without replacement from the complete
  distinct bank recorded by that deadline, after canonicalising the bank
  (dedup + lexicographic sort) so the draw is independent of discovery order.

Three predetermined subsampling seeds, each the first 64 bits of

```
sha256("<study_seed>|<formula_hash>|<solver>|<budget_label>|<replicate>")
```

under `numpy.random.Generator(PCG64)`. **Replicate 0 is the primary random
comparison; replicates 1 and 2 are sensitivity checks, not additional
independent instances.**

Subsets are **never** chosen using distance, clustering, observed resolution, or
any desired solver ordering. Actual selected sets and their hashes are saved.

**Eligibility.** If either solver recorded fewer than 40 distinct solutions at a
budget, that instance-budget pair is **ineligible for the fixed-size resolution
comparison** and **stays in the attempted denominator**. Both collection counts
are reported. An insufficient sample is **not** evidence of poor geometric
resolution — the formula may simply have fewer than 40 solutions, which is
**not** established here and is not claimed.

**Duplication.** When a bank holds exactly 40 distinct solutions, its prefix and
all three subsamples coincide. Evidence is reused by hash and the duplication is
**reported**; duplicates are never counted as independent evidence.

## 7. Measurement method — fixed, not re-searched

The certified method selected by the completed optimization evidence
(`../certified-resolution-2026-10-27/reports/02-optimization/REPORT.md`): the
**baseline sequential-counter encoding** with the DRUP proof taken from the same
solve, plus the **improved query policy**. The incremental encoding showed no
supported advantage on the primary metric (38 vs 37 certified width reduction,
winning three hard units and losing one) and is not used.

**No further encoding or query-policy search is conducted here.**

Certificate standard, unchanged:

* a **validated witness** — re-checked on the **original variables** by direct
  Hamming distance, by a verifier importing no SAT library and no encoder —
  establishes a lower bound;
* an **independently checked UNSAT certificate** (drat-trim pinned at
  `2e3b2dc0ecf938addbd779d42877b6ed69d9a985`, strict verdict rule) establishes an
  upper bound;
* **UNKNOWN never tightens a bound**; an unchecked UNSAT is solver-reported only;
* distances exclude auxiliary variables; oracle witnesses never enter an
  observed set.

Evidence and transferred bounds are reused only where their hypotheses hold, and
all reuse is **hash-keyed** on `(formula hash, observed-set hash)`.

**The target is a certified ordering, not necessarily two exact resolutions.** A
comparison stops as soon as its ordering is established.

## 8. Certification budget and allocation

| limit | value |
|---|---|
| per solver invocation used for measurement | **60 s** |
| total certification work per instance-budget group, shared across its selection schemes | **300 s** |
| calibration + validation + collection + certification, combined | **4 h** |

Encoding, reruns needed for proof production, proof checking and I/O all count.
Deadline overshoots are recorded and any late evidence is separated.

**Allocation rule, predetermined.** Within a group the distinct observed sets are
ordered

```
W-prefix, C-prefix, W-uniform0, C-uniform0, W-uniform1, C-uniform1,
W-uniform2, C-uniform2
```

Phase 1 gives each set an **initial opportunity** of `floor(300 / n_sets)`
seconds, in that order, using plain bisection. Phase 2 then revisits the sets in
the same order **round-robin**, in 30 s slices, now aiming each at the ordering
against its current opponent interval, until the group budget is exhausted.

Unfinished comparisons stay in the results. The budget is **not** extended and
no case is dropped to obtain a cleaner result.

## 9. Outcome classification

For each instance-budget-selection comparison, with certified intervals
`W = [L_W, U_W]`, `C = [L_C, U_C]`:

```
certified C > W     iff  L_C > U_W
certified W > C     iff  L_W > U_C
certified equality  iff  both intervals are the SAME SINGLETON
unresolved          otherwise
```

and the certified difference interval `ε_C − ε_W ∈ [L_C − U_W, U_C − L_W]`.

**Overlapping intervals establish nothing**, and a difference in lower bounds
alone establishes no ordering.

## 10. Planned summary tables

Kept separate, never merged:

1. equal-size **solver** comparison at each common time budget;
2. **prefix vs uniform** within each solver;
3. **short vs long** budget;
4. collection success and insufficient-sample outcomes.

Denominators reported explicitly: **attempted**, satisfiable, **eligible**, and
**certified**.

**The statistical unit is the SAT instance.** Budgets, subset replicates and
selection schemes are repeated observations within an instance. The sample size
is not inflated and **no post-hoc significance test is added**. Any conclusion
that depends on excluding instances where a solver failed to collect 40
solutions is stated as such.

## 11. Reproducibility — two different meanings

* **Frozen formulas and selected sets support repeatable mathematical
  verification**: the same sets give the same certified bounds and verdicts.
* **Re-running time-limited collection may produce different banks**, because
  the number of restarts that fit in 5 s or 30 s varies with machine load.
  Byte-identical time-limited collection is **not** promised and is not a
  success criterion.

## 12. Amendment rule

If a correctness defect later requires a protocol change, the original protocol
is preserved, the amendment is documented and dated, and affected runs are
distinguished. **Hypotheses and budgets are not changed in response to
unfavourable results.**
