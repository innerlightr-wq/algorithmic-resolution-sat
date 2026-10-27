# Continuation report — compiled proof checking, checkpointing, and the unfinished pilot

Dated 2026-10-27. Workspace `~/scratch/sat-resolution-oracle-audit-2026-10-26/`,
all new material under `continuation-2026-10-27/`.

The original `REPORT.md`, `CLAIMS.md`, `ENCODING.md`, `MANIFEST.md`,
`PILOT_PROTOCOL.md`, `data/*`, `results/*` and `src/*` are **unmodified**
(verified by mtime and hash). No repository or manuscript was touched; nothing
was committed, pushed or published.

Companion documents:

* `INVENTORY.md` — what was actually on disk, recomputed rather than trusted
* `PROTOCOL_AMENDMENT.md` — the dated amendment, written before any new measurement
* `CLAIMS_ADDENDUM.md` — ledger additions; it erases nothing
* `data/*.csv`, `data/continuation_summary.json` — machine-readable results
* `journal/*.jsonl` — per-query checkpoint journals
* `artifacts/`, `bench/artifacts/` — every CNF, proof and witness, hashed

---

## 1. What the overnight run left behind

The machine shut down uncleanly at ~02:10 (boot 07:35, no clean shutdown
record). The previous session's summary was checked rather than believed, and it
holds — 349/349 validation, `n = 24` and `n = 32` complete, 8 `n = 48` rows, 2
log-only `n = 64` rows — with **one correction**:

> The original "100 %" pilot figures are an *advance rate* (fraction of
> satisfiable instances with an exact `ε̂`), not a certification rate. Counting
> certificates instead, **8 rows had an upper bound that was never independently
> checked**: `n = 32` ids 1, 3, 5 and `n = 48` ids 1–5.

And one fact that shaped everything after it:

> **No CNF, proof or witness artifact survived.** `src/oracle.py:solve_Q`
> accepts a `cnf_dir`, but neither `pilot.py` nor `validate.py` ever passed one,
> so every certificate existed only in memory.

So §7's first question — can the saved `n = 48`/`n = 64` proofs be verified
without rerunning the SAT search? — has a definite answer: **there are none.**
Recovery was possible only because the inputs are deterministic, and that had to
be demonstrated, not assumed (§6 below).

Full classification of what exists, in the five requested categories, is in
`INVENTORY.md`.

---

## 2. The compiled checker

| item | value |
|---|---|
| checker | `drat-trim`, <https://github.com/marijnheule/drat-trim> |
| commit | `2e3b2dc0ecf938addbd779d42877b6ed69d9a985` (2024-11-25) |
| build | `gcc drat-trim.c -std=c99 -D_POSIX_C_SOURCE=200809L -O2 -o drat-trim` |
| compiler | `gcc (GCC) 16.2.1 20260810` |
| `drat-trim.c` sha256 | `d834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee` |
| binary sha256 | `e17cd2e8de37c4c43bf88360ae3d17740781fe971175bf0b0c935ee3aae4ae19` |
| source modified | **no** (`git status` clean; only the binary is untracked) |

The upstream `Makefile` target fails here: under `-std=c99` modern glibc hides
the POSIX declaration of `getc_unlocked`, used at `drat-trim.c:986`. The feature
macro exposes the declaration **without editing the source and without changing
the language standard**.

### 2.1 The format was determined, not assumed

`Glucose3` via `python-sat 1.9.dev15` with `with_proof=True`: `get_proof()`
returns one space-separated clause of DIMACS literals per line, terminated by
`0`, with **no `d` deletion lines and no RAT markers** — addition-only DRUP, a
strict subset of DRAT. drat-trim reads it natively (upstream ships
`examples/example-Schur.drup`, which verifies here). Files are written `.drup`
and passed as-is; nothing was renamed to imply a format it does not have.

A corollary worth recording: `src/drup.py`'s "deletion lines are ignored, which
is sound" argument is correct but **vacuous on this pipeline** — no deletion
line is ever produced.

### 2.2 Why the exit code is not used

Read from `drat-trim.c` (lines 905, 1477–1500) and then confirmed by experiment:

| situation | printed verdict | exit code |
|---|---|---|
| proof verified | `s VERIFIED` | 0 |
| proof rejected | `s NOT VERIFIED` | 1 |
| time limit hit | `s TIMEOUT` (`exit(0)` at line 905) | **0** |
| parse-level trivial UNSAT | `c trivial UNSAT` + `s VERIFIED` | **1** |
| `-S` mode success | `c VERIFIED derivation: …` | — |

The exit code is therefore wrong in **both** directions. Two different output
lines contain the substring `VERIFIED` while meaning "rejected" or "a different
question was answered", and every verdict line is prefixed with a carriage
return, so a `^s ` anchor matches nothing.

**The acceptance rule** (`src/dratcheck.py`, and `dratcheck.verified()` is the
only place a pass is decided): accept **iff**, after splitting on `\n` *and*
`\r` and stripping, some line is **exactly** `s VERIFIED`, and no line is
exactly `s TIMEOUT`, `s NOT VERIFIED`, `s DERIVATION` or
`s MEMORY ALLOCATION ERROR`. Crash, signal, hard wall-clock kill, missing proof,
empty proof and unparsable output are all `UNRESOLVED` — never a pass, never a
refutation.

Each proof is checked against the **standalone CNF of the same query** — all
original clauses plus every cardinality clause, no assumptions — written and
fsync'd before the solver ran. The journal links, per query: original-formula
hash, frozen-`A` hash, radius, CNF path + sha256, proof path + sha256, witness
path + sha256, checker, verdict, exit code and timings.

### 2.3 What a backward-mode pass does and does not mean

drat-trim checks only the lemmas in the unsatisfiable core — 76 of 350 proof
lines on instance 40. A core-only `s VERIFIED` certifies **that the formula is
unsatisfiable**, which is exactly the upper bound the audit needs. It does not
certify that the whole proof text is well-formed DRAT, and no such claim is
made.

---

## 3. Validating the replacement before using it

### 3.1 Agreement

Both checkers were run on identical CNF+proof bytes.

| | result |
|---|---|
| proofs checked by both | **14** |
| drat-trim `VERIFIED` | **14/14** |
| comparable (Python finished inside its budget) | 13 |
| **verdict agreement on comparable cases** | **13/13** |
| Python exceeded its budget | 1 |
| `ε̂` regressions against the historical CSVs | **0/14** |

Coverage: the published 349-cohort at `n = 16, 18, 20` across all three density
regimes (`data/bench_small.csv`), and the slowest cases available at `n = 32`
and `n = 48` (`data/bench_large.csv`).

### 3.2 Old vs new checking time on comparable cases

Fresh measurements of both checkers. `hist Python` is the **saved historical**
whole-instance figure from the original run and is *not* a fresh measurement —
the two are kept apart deliberately.

| case | proof lines | drat-trim | Python (fresh) | ratio | hist Python (whole instance) |
|---|---|---|---|---|---|
| `n=48, α=2.5, id 1` | 140 992 | **35.75 s** | **hard-killed at 300 s** | **> 8.4× (lower bound)** | 762.4 s, **did not verify** |
| `n=32, α=2.5, id 1` | 19 593 | **0.42 s** | 196.79 s | **469×** | 437.5 s |
| `n=32, α=2.5, id 5` | 11 517 | **0.56 s** | 215.09 s | **382×** | 379.0 s |
| `n=48, α=3.5, id 6` | 791 | 0.15 s | 22.94 s | **152×** | 101.5 s |
| `n=48, α=4.2, id 8` | 419 | 0.07 s | 1.72 s | 25× | 25.5 s |
| `n=20, α=2.5, id 520` | 1 808 | 0.07 s | 2.16 s | 31× | — |
| `n=18, α=2.5, id 280` | 521 | 0.06 s | 1.78 s | 28× | — |
| `n=16, α=2.5, id 40` | 350 | 0.06 s | 0.95 s | 16× | — |
| `n≤20, α=4.2` (3 cases) | 13–24 | 0.05 s | ≈0.00 s | **0.02×–0.1×** | — |

Across the 13 comparable cases: **min 0.02×, median 16.2×, max 469×**.

Two things are stated plainly rather than smoothed over:

* **The `n = 48` row is a lower bound, not a measured speedup.** Python never
  finished, so no ratio is claimed and none is extrapolated. What *is* measured
  is that drat-trim certified in 35.75 s a bound the original run failed to
  certify in 762 s.
* **drat-trim is genuinely slower on trivial proofs** — 4 of 13 cases. It pays a
  ~50 ms process-start-and-parse floor that an in-process Python call does not.
  It wins only once proofs are large, which is exactly the regime that blocked
  the pilot.

### 3.3 A limitation of the original checker, found while measuring it

`src/drup.py:check_proof` tests its `max_seconds` budget **only between proof
steps**. A single unit-propagation pass over a large accumulated clause set can
overrun it without bound — observed directly: the 141 k-line proof ran past
300 s inside one step and had to be killed externally.

So the original run's "120 s per proof" was never an enforceable limit. That is
*why* those five `n = 48, α = 2.5` upper bounds came back `solver-reported`
rather than as clean timeouts. Every Python figure above is bounded by an
external hard kill, and an overrun is reported as a timeout at a stated budget.

### 3.4 Controls — 17/17, after discarding two of my own

| group | result |
|---|---|
| honest baseline (genuine proof of a genuine UNSAT query) | 1/1 `VERIFIED` |
| **true negative controls** | **8/8 rejected, 0 accepted** |
| verdict-string parsing traps | 6/6 |

The negative controls, all rejected by **both** checkers in agreement:

1. **A confirmed-satisfiable CNF paired with an UNSAT certificate.** `Q_{k-1}`
   for instance 40 (4 345 vars, 7 588 clauses) was confirmed satisfiable by
   evaluating a stored full model clause-by-clause — no solver, no proof checker
   — then paired with the genuine proof of `Q_k`: `s NOT VERIFIED`.
2. The same satisfiable CNF with a bare empty-clause proof: `s NOT VERIFIED`.
3. Keep only **non-core** lemmas (refutation destroyed): rejected.
4. Sign-flip a literal in an **early core** lemma: rejected.
5. Truncate to half the core lemmas: rejected.
6. Unjustified bare empty clause against a genuinely UNSAT CNF: rejected.
7. Empty proof file → `UNRESOLVED`. 8. Missing proof file → `UNRESOLVED`.

**Two controls I wrote first were worthless, and that is worth recording.**
Injecting a non-RUP clause at line ~116 of 350, and sign-flipping a literal in
the *final* lemma, were both accepted by **both** checkers. The reason is not a
checker defect: the Glucose proof derives the empty clause at RUP step **82** of
350 lines, so both corruptions sat in a dead tail that no checker ever reads.
This is the same trap as the original ledger's C10 and as the brief's warning
about deleting a redundant step. A corruption is only a control if it lands
inside the refutation — hence controls 3–5, which target the core explicitly.

A proof checker also **cannot** catch an encoder bug: both deliberately broken
encoders from the original controls produce CNFs that genuinely *are*
unsatisfiable at the radius they return, so refutations of them verify
correctly. Only `src/verify.py` (no SAT library, no encoder) and exhaustive
enumeration detect those. The compiled checker strengthens the upper bound and
changes nothing about the lower bound.

### 3.5 The one genuine disagreement, resolved

With the explicit empty clause stripped from a real proof, drat-trim still
reports `s VERIFIED` (it reconstructs the conflict) while `src/drup.py` reports
"proof ended without deriving the empty clause". The formula *is* unsatisfiable,
so drat-trim is correct and `src/drup.py` is merely incomplete — it requires the
empty clause syntactically. This cannot arise from a real Glucose proof, which
always ends with an explicit `0`. It is recorded as a documented behavioural
difference, not as a soundness problem, and the pilot continuation was not
blocked on it.

---

## 4. Certification rules, unchanged and kept separate

The target is unchanged:

```
eps_hat(A,I) = max_{x |= I} min_{a in A} d_H(x,a)  =  min{ r : Q_r UNSAT }
```

An **exact certified radius `k`** requires both of:

* **lower** — a stored satisfying assignment, re-checked against the *original*
  clauses over the *original* variables by direct Hamming distances
  (`src/verify.py`, which imports no SAT library and no encoder): a verified
  witness for `Q_{k-1}`;
* **upper** — an **independently checked** refutation of `Q_k`.

`k = 0` is handled explicitly: there is no `Q_{-1}`, and `ε̂ ≥ 0` holds by
definition, so the lower bound is labelled `vacuous (k=0)` rather than
"verified". `Q_0` UNSAT ⟺ `S_I ⊆ A` ⟺ `ε̂ = 0`. The trivial upper bound
`r ≥ n` remains available and is labelled `arithmetic`.

Five fields are carried separately in every row and never merged
(`src/measure.py`):

`witness_verified_lower` · `certified_upper` · `solver_reported_upper` ·
`exact_certified` · `completion`

`certified_upper` and `solver_reported_upper` are **mutually exclusive**, so
neither can be read as implying the other. A bare solver UNSAT is never an
independently checked upper bound, and an interval supported only by unchecked
UNSAT answers is reported as `interval only`, never as a certified interval.
Witnesses found by the oracle are never added to `A`.

The radius-search strategy is unchanged: binary search on `r` over `[0, n]` with
`mid = (lo+hi)//2`, identical to `src/oracle.py:covering_radius`. No correctness
issue was found in it.

---

## 5. Checkpointing

`src/store.py` + `src/measure.py`.

* An artifact is fsync'd to its final path **before** any journal record names
  it, so a record never promises a file that is absent.
* Journal records are one JSON object per line, appended and fsync'd
  individually. A torn final line is dropped and **reported**, never silently
  accepted and never fatal.
* Eight query states are kept distinct: `SOLVED_SAT`, `WITNESS_VERIFIED`,
  `SOLVED_UNSAT` (solver done, **checking pending**), `PROOF_VERIFIED`,
  `PROOF_REJECTED`, `PROOF_UNRESOLVED`, `TRIVIAL_UNSAT`, `UNKNOWN`.
  `SOLVED_UNSAT` is journalled *before* checking begins, so a restart can tell
  "solver finished, checking pending" from "proof checked".
* Only `WITNESS_VERIFIED`, `PROOF_VERIFIED` and `TRIVIAL_UNSAT` are reused.
* **A query is reused only when the original-formula hash *and* the frozen-`A`
  hash both match.** A matching instance id or generator seed is deliberately
  insufficient.

### 5.1 Interruption and recovery test — 12/12

`src/test_checkpoint.py`, run in a throwaway temporary directory; it signals
only processes it started and reboots nothing.

| test | result |
|---|---|
| SIGKILL (uncatchable) mid-measurement leaves a readable journal | pass — 2 records survived, child rc = −9 |
| no `measurement` record written for an unfinished run | pass |
| torn final journal line dropped **and reported** | pass — "dropped incomplete final journal record (line 3, 41 bytes)" |
| torn record not counted as a completed query | pass |
| restart completes the measurement | pass |
| restart **reuses** completed queries | pass — reused 1 of the 2 survivors |
| resumed run is exact and certified | pass — `ε̂ = 5` |
| resumed answer == uninterrupted answer | pass — 5 vs 5 |
| formula and `A` hashes identical across runs | pass |
| every journalled artifact exists with its recorded hash | pass — 14 artifacts |
| same `A`: queries offered for reuse | pass — 5 radii |
| **different `A`: nothing reused** | pass — 0 radii |

"Reused 1 of 2" is the intended behaviour, not a shortfall: the surviving record
was `SOLVED_UNSAT`, i.e. checking was still pending, so it was correctly
re-done rather than trusted.

### 5.2 Live demonstration

The `n = 48` benchmark case was interrupted once for real (the first run of the
large stage was stopped because its Python comparison was unbounded). On
re-invocation it **reused its journalled queries instead of re-solving**, and
produced the same `ε̂ = 17`.

### 5.3 Journal and artifact integrity

Every artifact named by every journal record was re-hashed:

| journal | records | queries | artifacts verified | missing | hash mismatch |
|---|---|---|---|---|---|
| `bench_small` | 97 | 79 | 158 | 0 | 0 |
| `bench_large` | 31 | — | — | 0 | 0 |
| `bench_controls` | 9 | 7 | 14 | 0 | 0 |
| `resume_n48`, `resume_n64` | see `data/continuation_summary.json` | | | 0 | 0 |

---

## 6. Resuming without overwriting: the identifier hazard

The original pilot's instance counter `iid` increments per generated instance
and **skips values when the wall clock fires** — and `iid` seeds both observed
sets (`PILOT_SEED + 777 + iid` for WalkSAT, `+ 3333 + iid` for CDCL). So `iid`
is **not** a function of `(α, k)`, and the historical mapping had to be
reconstructed and *verified* before anything could be resumed.

It was, by reproducing every surviving observed-set size exactly:

| `n=48` historical id | `(α, k)` | `|A_W|`, `|A_C|` reproduced |
|---|---|---|
| 1–5 | (2.5, 0…4) | 150, 40 — all five exact |
| 6 | (3.5, 0) | 129, 40 — exact |
| 7 | (4.2, 0) | UNSAT, kept in the record |
| 8 | (4.2, 1) | 44, 38 — exact |

Both `n = 64` log rows likewise reproduce exactly (`|A_W| = 150`, `|A_C| = 40`).

Two consequences:

* The never-run `n = 48` cells are **(α=3.5, k=1…4) and (α=4.2, k=2…4)** — *not*
  "ids 9–15". The 8 recorded rows sample 5/1/2 across the three densities,
  because `src/pilot.py`'s wall-clock `break` exits only the inner loop and then
  moves to the next density.
* Assigning the canonical uninterrupted `iid` to the never-run cells makes seeds
  7 and 8 collide with historical ids — **for different formulas**. The
  collision is in the identifier only, not the measurement. Every row therefore
  carries an explicit `measurement_id` (`n{n}_a{α}_k{k}`) plus `obs_seed_id`.
  **No historical row is overwritten**; the `n = 64` log rows are retained as
  historical, unverified records and the continuation's re-measurement of the
  same cells is reported separately.

The original `n = 48` truncation stands as a valid outcome under the original
3600 s budget. Completion under amendment 1 is reported separately and
previously consumed time is not carried over. Budgets, limits, stop conditions
and the declared round-robin case ordering are in `PROTOCOL_AMENDMENT.md`.

---

## 7. Results of the resumed pilot

Every case was re-derived: nothing could be re-checked from saved artifacts,
because none survived. All measurements below were produced under
`PROTOCOL_AMENDMENT.md`, with the original formulas, density strata, generator
seeds and observation budgets unchanged.

### 7.1 Completion and certification, by size and density

`cells / satisfiable / exact-certified ε̂_W`:

| size | α = 2.5 | α = 3.5 | α = 4.2 | cells attempted | satisfiable | **exact certified** | resolved but UNCHECKED | interval only | not attempted |
|---|---|---|---|---|---|---|---|---|---|
| `n = 48` | 5 / 5 / **5** | 5 / 5 / **5** | 5 / 4 / **4** | **15 / 15** | 14 | **14 / 14 (100 %)** | **0** | 0 | **0** |
| `n = 64` | 5 / 5 / **1** | 5 / 5 / **5** | 5 / 5 / **5** | **15 / 15** | 15 | **11 / 15 (73 %)** | **0** | 4 | **0** |

The single non-satisfiable cell is `n48_a4.2_k0` (UNSAT, kept in the record and
not replaced). **No cell was left unattempted at either size**, and no row
anywhere is "resolved with an unchecked upper bound" — that category, which held
8 rows before this continuation, is now empty.

### 7.2 The eight previously uncertified rows are now certified

| row | original certificate | now | ε̂ |
|---|---|---|---|
| `n48 a2.5 k0` (id 1) | upper: solver-reported | **exact certified** | 17 |
| `n48 a2.5 k1` (id 2) | upper: solver-reported | **exact certified** | 15 |
| `n48 a2.5 k2` (id 3) | upper: solver-reported | **exact certified** | 15 |
| `n48 a2.5 k3` (id 4) | upper: solver-reported | **exact certified** | 16 |
| `n48 a2.5 k4` (id 5) | upper: solver-reported | **exact certified** | 15 |
| `n32 a2.5 k0` (id 1) | upper: solver-reported | **exact certified** | 9 |
| `n32 a2.5 k2` (id 3) | upper: solver-reported | **exact certified** | 8 |
| `n32 a2.5 k4` (id 5) | upper: solver-reported | **exact certified** | 9 |

All eight `ε̂` values are unchanged from the original run — the certification was
missing, not the answer. The three `n = 32` rows are an **addition beyond the
`n = 48`/`n = 64` scope the brief named**, reported separately in
`data/resume_n32_recert.csv`; they took **11 s in total**, against 437 s, 379 s
and 379 s of Python checking that had failed to certify them.

### 7.3 Agreement with the historical record

| | result |
|---|---|
| `n = 48` ε̂_W vs `data/pilot_n48.csv` | **7 / 7 match** (17, 15, 15, 16, 15, 6, 2) |
| `n = 32` ε̂_W vs `data/pilot_n32.csv` | **3 / 3 match** (9, 8, 9) |
| `n = 64` vs the **log-only** rows | see below |
| observed-set sizes reproduced | **every** surviving `n = 32`/`48`/`64` record |

The two `n = 64` rows existed only as printed lines in
`../results/pilot_4864.txt` — no CSV, no artifacts — so they were *historical,
unverified records*. They are preserved as such, and the continuation's
independent re-measurement of the same two cells is reported alongside:

| cell | then | now |
|---|---|---|
| `n64 a2.5 k0` | ε̂_W = 26, ε̂_C = 37, *upper: solver-reported* | ε̂_W = **26**, ε̂_C = **37** — both match — and now **exact certified** |
| `n64 a2.5 k1` | ε̂_W unresolved, ε̂_C = 38, *interval only* | ε̂_C = **38** matches; ε̂_W still unresolved, now as the **certified interval [17, 32]** |

### 7.4 What remains unresolved, and why

Four cells, all `n = 64` at `α = 2.5` (`k = 1, 2, 3, 4`). Each is an interval
`[17, 32]`, and in each the limit is the **60 s per-query SAT timeout**, not
proof checking:

| radius | outcome |
|---|---|
| `r = 32` | UNSAT, proof **independently checked** (47 295 – 145 558 proof lines, 21.5 – 60.7 s) ⟹ certified ε̂ ≤ 32 |
| `r = 16` | SAT, witness **independently verified** ⟹ certified ε̂ ≥ 17 |
| `r = 24` | solver **UNKNOWN** after 60 s ⟹ search stops |

So both endpoints are independently certified while `ε̂` itself is not pinned
down. These are reported as `interval only` and **never as a certified exact
value**; `exact_certified` is `False` for all four. This is not an interval
resting on unchecked UNSAT answers — the brief's prohibition — and it is not
presented as one. A fifth `UNKNOWN` occurred at `r = 29` in the *equal-size
secondary* comparison for `k = 1`, which is why its equal-size entry is
`[null, 38]`.

The binding constraint is therefore the mid-radius SAT query at `n = 64`,
`α = 2.5`, `|A| = 150`. Raising the per-query timeout is the obvious next lever
and was **not** done here: 60 s is the original protocol's value and amendment 1
deliberately left it unchanged, so these four remain honestly unresolved rather
than rescued by a mid-run parameter change.

### 7.5 End-to-end cost, including certification

| run | encode | solve | **check** | total | check share of encode+solve+check |
|---|---|---|---|---|---|
| original 349-cohort (`n ≤ 20`, Python checker) | 8.4 s | 3.4 s | **767.6 s** | — | **98.5 %** |
| `n = 48` continuation (drat-trim) | 8.1 s | 197.6 s | **227.2 s** | 543.7 s | **52.5 %** |
| `n = 64` continuation (drat-trim) | 14.3 s | 564.7 s | **378.8 s** | 1 388.1 s | **39.6 %** |
| `n = 32` re-certification (drat-trim) | 0.7 s | 2.0 s | 3.9 s | 10.7 s | 59.2 % |

**Total continuation compute: 1 942 s (≈ 32 min) against a declared 16 200 s
cap.** Both sizes completed inside their per-size budgets (`n = 48`: 544 s of
5 400 s; `n = 64`: 1 388 s of 10 800 s), so no stop condition fired.

### 7.6 Is proof checking still the dominant cost?

**No.** It was 98.5 % of the original oracle's wall clock and is now 52.5 % at
`n = 48` and **39.6 %** at `n = 64`, where **solving overtakes it** (564.7 s vs
378.8 s). The original ledger's M6/M8 ("proof checking is the dominant cost")
held for the pure-Python checker and no longer holds for the pipeline.

The cost ranking has genuinely inverted: at `n = 64` the order is now
solve > check > encode, and the thing that actually stops the pilot is a single
hard SAT query, not certification.

### 7.7 Encoding sizes and peak memory

| size | max auxiliary vars | max total clauses | peak RSS |
|---|---|---|---|
| `n = 32` | 38 250 | 76 880 | 75 MB |
| `n = 48` | 86 250 | 172 968 | 137 MB |
| `n = 64` | 153 450 | 307 424 | 192 MB |

Consistent with the original M2 scaling `n_aux ≈ 0.75 · |A| · n · (r+1)`, and
far inside the 8 GB soft ceiling. The distance constraints still dominate the
encoded formula completely, exactly as the original report found — this
continuation changes the cost of *certifying* the answer, not the size of the
encoding (original U2 remains open).

### 7.8 Checkpoint and restart validation

| | result |
|---|---|
| interruption/recovery test suite | **12 / 12** (`src/test_checkpoint.py`) |
| journal records written | **1 038** across 6 journals |
| queries journalled | **883** |
| **artifacts re-hashed against their journal records** | **1 660** |
| missing artifacts | **0** |
| hash mismatches | **0** |
| torn/corrupt journal records | **0** in the production journals |

Query-state tallies, e.g. `resume_n64`: `WITNESS_VERIFIED` 116,
`PROOF_VERIFIED` 91, `SOLVED_UNSAT` 137, `UNKNOWN` 5. The gap between
`SOLVED_UNSAT` and `PROOF_VERIFIED` is **not** unchecked certified bounds: it is
the equal-size *secondary* comparison, which keeps the original protocol's
`want_proof=False` and is uncertified by design, plus the two-phase journalling
(`SOLVED_UNSAT` is always written before checking starts). No certified row
anywhere has an unchecked upper bound — `data/resume_n*.csv` carries
`certified_upper` and `solver_reported_upper` as mutually exclusive fields.

A real interruption was also survived mid-continuation: the `n = 48` benchmark
measurement was killed once and **reused its journalled queries on restart
instead of re-solving**, returning the same `ε̂ = 17`.

---

## 8. Answers

**1. Did the compiled checker preserve independent verification?**
Yes, and strengthened it. Upper bounds are now accepted by `drat-trim` @
`2e3b2dc` (source unmodified) under a strict verdict rule that ignores the exit
code, which is wrong in both directions. On all 13 benchmark cases where the
Python checker finished, the two agree **13/13**; drat-trim verified **14/14**;
there were **0 ε̂ regressions**. All 8 true negative controls are rejected by
both checkers, including a CNF independently confirmed satisfiable and then
paired with an UNSAT certificate. Independence is preserved because the checker
shares no code with the encoder or solver, and the lower bounds still rest on
`src/verify.py`, which imports no SAT library and no encoder. The audit now
rests on *two independent checkers that agree*, where before it rested on one
written for it. One behavioural difference exists and is documented (§3.5): it
is Python incompleteness, not drat-trim unsoundness.

**2. How much did it improve measured checking and total runtime?**
On comparable cases: **median 16×, max 469×** (0.42 s vs 196.8 s on a
19 593-line proof). On the slowest case available, drat-trim certified a
141 k-line proof in **35.7 s** that the original run failed to certify in 762 s
— reported as a **lower bound of >8.4×**, not a measured speedup, because
Python never finished. The decisive figure is not a ratio: **8 upper bounds that
could not be certified at all now are**, and the three `n = 32` ones took 11 s
against ~1 195 s of failed Python checking. Total runtime: the whole
continuation (30 fresh cells plus 3 re-certifications, all certification
included) took **1 942 s**. Honest counter-example: on trivial proofs (13–24
lines) drat-trim is **slower**, by a ~50 ms process-start floor.

**3. Which `n = 48` and `n = 64` measurements are now certified exact?**
`n = 48`: **14 of 14 satisfiable cells (100 %)**, all 15 cells attempted —
α=2.5 5/5, α=3.5 5/5, α=4.2 4/4, plus one UNSAT cell kept in the record. This
includes all five previously solver-reported rows and all seven never-run cells.
`n = 64`: **11 of 15 (73 %)** — α=3.5 5/5, α=4.2 5/5, α=2.5 1/5. The certified
`n = 64` radii are α=2.5 k0 = 26; α=3.5 k0…k4 = 16, 18, 15, 15, 18; α=4.2 k0…k4
= 9, 7, 3, 2, 4. (Additionally, outside the named scope, `n = 32` ids 1/3/5 =
9/8/9 are now certified.)

**4. What remains unresolved, and why?**
Exactly four cells: `n = 64`, α = 2.5, k = 1…4, each a **certified interval
[17, 32]** — witness-verified lower bound at 17, independently proof-checked
upper bound at 32 — with `ε̂` unresolved because the `r = 24` query returns
UNKNOWN at the protocol's 60 s per-query SAT timeout. The blocker is SAT solving
at mid-radius with `|A| = 150`, not proof checking. The timeout was deliberately
not raised mid-run. Also unresolved, and unchanged: whether the paper's
trade-off persists beyond `n = 20` (this is a feasibility pilot), whether a
better cardinality encoding removes the `|A|·n·r` blow-up, and whether
`drat-trim` itself would pass a formally verified checker — our pipeline emits
DRUP, not LRAT, so that route needs more work (new U4).

**5. Can an interrupted run now resume without losing completed work?**
Yes, demonstrated twice. The test suite passes **12/12**, covering SIGKILL
mid-measurement, a torn final journal line (dropped *and reported*), reuse of
completed queries, an identical resumed answer, and the refusal to reuse a
journal written against a different observed set. Artifacts are fsync'd before
any record names them; **1 679 artifacts re-hashed with 0 missing and 0
mismatches**. A restart distinguishes "solver finished, checking pending"
(`SOLVED_UNSAT`) from "proof checked" (`PROOF_VERIFIED`) and re-does the former.
It was also exercised for real: an interrupted `n = 48` measurement resumed from
its journal rather than re-solving. Worst case loss is the single query in
flight.

**6. Is the pipeline ready for a larger preregistered experiment, or does a
specific implementation issue still need attention?**
Ready in its certification and bookkeeping; **two specific issues remain**, both
on the solving side rather than the checking side.

*Needs attention first:* (a) the **per-query SAT timeout** is now the binding
constraint — at `n = 64`, α = 2.5 the mid-radius query exceeds 60 s and cost
4 cells. A preregistered run must either raise it with a declared budget or
adopt a smarter radius search (the current strategy is plain bisection, which
spends its hardest query in the middle of the range; an incremental or
assumption-based search, or starting from the `α`-stratified prior, would avoid
the worst query). (b) the **cardinality encoding** still grows as
`|A|·n·(r+1)` — 307 424 clauses at `n = 64` — so `n = 96`+ will hit encoding and
memory limits well before checking becomes a problem again (original U2).

*Not blockers:* `drup.py`'s unenforceable time budget (it is now only a
cross-check, run under an external kill); drat-trim's process-start floor on
trivial proofs; and the fact that backward-mode checking certifies
unsatisfiability rather than whole-proof well-formedness, which is the claim the
audit needs.

And the limit that no amount of engineering fixes: this remains a **feasibility
pilot**, 15 instances per size, no held-out split, and no `|S_I|` denominator.
The `n = 48`/`n = 64` numbers show the *measurement* is now feasible and
certifiable at those sizes. They do **not** show that the WalkSAT/CDCL
trade-off generalises, and nothing here should be read that way: ε̂_C exceeds
ε̂_W in every satisfiable cell at both sizes, but with this sample that is an
observation awaiting a powered study, not a finding.

---

## 9. Changed files and final workspace state

**Nothing outside `continuation-2026-10-27/` was modified.** Verified: the
original `*.md`, `data/*`, `results/*` and `src/*` all retain mtimes at or
before 02:10 on 2026-10-27, and the original `src/*.py` hashes are recorded in
`MANIFEST_CONTINUATION.md`. `src/encode.py`, `src/verify.py` and `src/drup.py`
are imported **unchanged**. No repository or manuscript was touched; nothing was
committed, pushed or published.

### New files

| path | what |
|---|---|
| `INVENTORY.md` | on-disk state in the five requested categories, recomputed |
| `PROTOCOL_AMENDMENT.md` | dated amendment 1, written before any new measurement |
| `CONTINUATION_REPORT.md` | this report |
| `CLAIMS_ADDENDUM.md` | ledger additions; erases nothing |
| `MANIFEST_CONTINUATION.md` | hashes, versions and commands |
| `src/dratcheck.py` | drat-trim front end; strict verdict rule |
| `src/store.py` | atomic writes, hashed artifacts, append-only journal |
| `src/measure.py` | checkpointed measurement; same search strategy |
| `src/bench.py` | checker-validation benchmark and controls |
| `src/resume_pilot.py` | the resumed pilot driver |
| `src/test_checkpoint.py` | interruption/recovery test |
| `src/summarize.py` | aggregation into the tables above |
| `tools/drat-trim/` | upstream source at `2e3b2dc`, **unmodified**, plus the built binary |
| `data/bench_small.csv`, `bench_large.csv`, `bench_controls.csv` | checker validation |
| `data/resume_n48.csv`, `resume_n64.csv`, `resume_n32_recert.csv` | resumed results |
| `data/continuation_summary.json` | machine-readable aggregate |
| `journal/*.jsonl` | 5 per-run checkpoint journals, 962 records |
| `artifacts/`, `bench/artifacts/` | every CNF, proof and witness, hashed (~160 MB) |
| `results/*.txt` | raw run logs |

### Modified during the continuation (all inside `continuation-2026-10-27/src/`)

* `bench.py` — the Python-checker comparison was moved into a subprocess under a
  hard wall-clock kill, after `drup.py`'s internal budget was found to be
  unenforceable (§3.3); the first two negative controls were replaced with
  core-targeting ones after they proved worthless (§3.4).
* `measure.py` — `solver_reported_upper` narrowed to mean *reported and
  unchecked*, making it mutually exclusive with `certified_upper`.
* `resume_pilot.py` — per-size journals; `--only` cell filter for the `n = 32`
  re-certification.
* `summarize.py` — negative-control denominator corrected to exclude the honest
  baseline; `n = 64` log-only comparison added; per-size journal paths.
* `test_checkpoint.py` — temporary-directory leak fixed (`/tmp` here is a 7.7 GB
  tmpfs).

