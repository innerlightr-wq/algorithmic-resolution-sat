# Pilot protocol — declared before any pilot instance was generated or solved

Written and committed to this file prior to running `src/pilot.py`. Nothing below
was adjusted after seeing results; deviations, if any, are recorded in `REPORT.md`.

## Sizes and densities

* Primary sizes `n ∈ {24, 32}`.
* `n ∈ {48, 64}` attempted **only** if the feasibility rule below is met at `n = 32`.
* Clause densities `α ∈ {2.5, 3.5, 4.2}` — the paper's three regimes
  (solution_rich / intermediate / near_threshold), `m = round(αn)`.
* **5 instances per `(n, α)` cell**, so 15 per size.

## Instance generation

* `random_3sat_clauses` from the repository's own `scripts/phase2/sat_common.py`,
  imported unchanged.
* `PILOT_SEED = 20261026`; per-instance generator
  `np.random.default_rng(PILOT_SEED + 100000*n + 1000*round(10*α) + k)` for `k = 0..4`.
* **Satisfiability is decided by a complete solver** (Cadical195, no time limit
  below 120 s), not by enumeration, which is infeasible at these sizes.
  SAT, UNSAT and unresolved outcomes are all recorded. **Difficult or UNSAT
  instances are kept in the record and never replaced**, and no planted
  construction is substituted.

## Observed sets A

* **Primary (the paper's own protocol, unchanged):** WalkSAT from
  `scripts/phase2/walksat_solver.py`, `K = 150` restarts, `max_flips = 3000`,
  `p_noise = 0.5`, seeded `default_rng(PILOT_SEED + 777 + id)`.
  This budget is *not* scaled with `n`; whether it still finds solutions at
  `n ≥ 24` is one of the questions, and an empty `A` is recorded as the paper's
  categorical failure, not rescued.
* **Secondary (a new fixed-budget comparison, labelled as new):** CDCL observed
  sets by the repository's Phase-3 method — `R = 5` permuted and
  phase-randomised `Glucose3.enum_models()` runs, each truncated at
  `T = 8` models, seeded `default_rng(PILOT_SEED + 3333 + id)`.
* Any paired WalkSAT-vs-CDCL comparison is additionally reported **at equal
  numbers of distinct observed solutions**, by truncating the larger set to the
  size of the smaller in first-discovery order.

## Limits

| Limit | Value |
|---|---|
| per SAT query | 60 s (interrupt; a timeout yields UNKNOWN, never UNSAT) |
| per instance (all queries for one `ε̂`) | 600 s |
| proof checking | 200 000 RUP steps per proof |
| overall pilot wall clock | 3600 s per size |
| memory | peak RSS recorded per instance via `resource.getrusage`; soft ceiling 8 GB |

## Exhaustive cross-check

* `n = 24`: brute force **is** attempted, chunked to bound memory (`2²⁴ = 16.7 M`
  assignments). Where it completes, it provides an independently checked upper
  bound.
* `n ≥ 32`: brute force is **not** attempted and is not estimated. Upper bounds
  there rest on solver UNSAT plus, where the proof checks, an independently
  verified DRUP proof.

## Advance / stop rule

* Advance from `n` to the next size only if **≥ 60 % of that size's satisfiable
  instances yield an exact `ε̂`** (lower bound witness-verified and upper bound at
  least solver-reported) within the per-instance limit.
* If the rule fails at `n = 32`, `n ∈ {48, 64}` are **not** attempted, and that is
  reported as the feasibility boundary rather than worked around.
* Instances that time out are reported as the interval actually established.

## What this pilot can and cannot establish

It can establish whether the oracle *runs* beyond `n = 20` and at what cost. It
**cannot** establish that the paper's empirical trade-off generalises to larger
instances: the sample is 15 instances per size, there is no held-out split, and
without `|S_I|` no coverage fraction is known in absolute terms.
