# Optimization protocol — dated 2026-10-27

Declared **before** the comparison was run. Written after the experimental units
were selected and their baseline bounds re-verified, and **before** any new
timing result existed. Deviations, if any, are recorded in `REPORT.md`.

Scope: `optimization-2026-10-27/` only. The original audit and
`continuation-2026-10-27/` are preserved byte-for-byte. No repository or
manuscript is modified; nothing is committed, pushed or published. No larger
experiment is begun.

---

## 1. Question

Within a fixed per-measurement budget, does a different **query-selection
policy**, or an **incremental cardinality encoding with solver-state reuse**,
produce **more independently certified information** than the continuation's
baseline?

Success = additional certified exact answers, or narrower certified intervals.
Faster encoding, smaller formulas and solver-reported (unchecked) answers are
secondary measurements and are never counted as success.

It is **not** assumed that incremental solving removes the hard boundary query.
A different query order may narrow an interval while leaving the original hard
radius unresolved; that outcome is anticipated and reported as such.

---

## 2. Mathematical target — unchanged

For nonempty `A ⊆ S_I`:

```
eps(A,I) = max_{x |= I}  min_{a in A}  d_H(x, a)
Q_r(x)   = I(x)  AND  for every a in A:  d_H(x,a) >= r+1
```

* a validated satisfying witness with nearest distance `d` establishes `eps >= d`;
* an **independently checked** UNSAT proof for `Q_r` establishes `eps <= r`;
* exactness requires matching certified bounds.

Distance is measured on the **original `n` variables only**. Auxiliary variables
never contribute. Oracle witnesses are never added to `A`.

### 2.1 The AtMost form, derived explicitly

Method C needs an AtMost constraint, because PySAT's `ITotalizer` encodes
AtMostK only. With `agree(x,a) = #{i : x_i = a_i}` and `d_H(x,a) = n - agree(x,a)`:

```
d_H(x,a) >= r+1   <=>   n - agree(x,a) >= r+1   <=>   agree(x,a) <= n - r - 1
```

So the constraint is `AtMost(agreement_literals(a), n - r - 1)`, where

```
agreement_literals(a)[i] =  +(i+1)  if a_i = 1     (true iff x_i = 1 = a_i)
                            -(i+1)  if a_i = 0     (true iff x_i = 0 = a_i)
```

This is the **negation**, literal by literal, of the original encoder's
`dist_literals(a)`. Endpoint conventions, all tested in `src/test_encoding.py`:

| radius | bound `n-r-1` | meaning | check |
|---|---|---|---|
| `r = 0` | `n-1` | at most `n-1` agreements, i.e. `x != a` | matches the original encoder's single-clause case |
| `r = n-1` | `0` | no agreement at all, i.e. `x = complement(a)`, `d_H = n` | `-rhs[0]` forces every literal false |
| `r = n` | `-1` | impossible | recognised as `trivial_unsat` **by arithmetic**, no solver call |
| `r > n` | `< -1` | impossible | same |

`ITotalizer.rhs[k]` is indexed `0..ubound`, and `-rhs[k]` enforces `sum <= k`,
so a radius `r` is imposed by the single literal `-rhs[n-r-1]`. `ubound` is set
to `n - lo - 1`, the largest bound any radius in the search range can need;
since `lo` only ever increases, the bound only ever decreases and no
`increase()` call is required.

Auxiliary-variable identifiers are allocated from one monotonically increasing
counter threaded through every `ITotalizer`, so no two constraints can share an
id. This is asserted in the validation suite, not assumed.

---

## 3. Experimental units

Defined and frozen in `src/units.py` by rules **R-OPT**, **R-CTRL**, **R-START**
(reproduced in that file's header). A **measurement** is one `(I, A)` pair,
identified by `(n, sha256(I), sha256(A), observation_label, query_solver)`. One
`(n, alpha, k)` cell carries four measurements (`_W`, `_C`, `_eqW`, `_eqC`);
they are never merged.

**9 units, under the cap of 12:**

| unit | group | certified start | width | UNKNOWN radii carried in | historical exact |
|---|---|---|---|---|---|
| `n64_a2.5_k1_W` | opt-primary | `[17, 32]` | 15 | `{24}` | — |
| `n64_a2.5_k2_W` | opt-primary | `[17, 32]` | 15 | `{24}` | — |
| `n64_a2.5_k3_W` | opt-primary | `[17, 32]` | 15 | `{24}` | — |
| `n64_a2.5_k4_W` | opt-primary | `[17, 32]` | 15 | `{24}` | — |
| `n64_a2.5_k1_eqW` | opt-secondary | `[29, 64]` | 35 | `{29}` | — |
| `n64_a2.5_k0_W` | control | `[17, 32]` | 15 | `{}` | 26 |
| `n64_a3.5_k1_W` | control | `[17, 32]` | 15 | `{}` | 18 |
| `n64_a3.5_k0_W` | control | `[9, 16]` | 7 | `{}` | 16 |
| `n64_a4.2_k0_W` | control | `[9, 16]` | 7 | `{}` | 9 |

Notes that matter:

* The **fifth unresolved measurement** is `n64_a2.5_k1_eqW`. It belongs to the
  original protocol's *uncertified secondary* comparison (`want_proof=False`),
  so its journal upper bound of 30 is **solver-reported and is not inherited as
  certified**; its certified start is therefore `[29, 64]`, the arithmetic upper
  bound. It is reported in its own group and kept out of the headline
  opt-primary comparison.
* Controls start from a **non-exact historical checkpoint** chosen by R-START
  (earliest prefix of their own journal at which certified `lo < hi` both
  exist). The historical exact answer is held outside the search state and used
  only to check the result afterwards.
* Two controls start at exactly `[17, 32]`, the same interval as the
  opt-primary units, which makes those four pairs directly comparable.
* `A` is **recovered, not substituted**: regenerated from the pilot's own
  deterministic procedure and then required to hash to the recorded value.
  `src/baseline.py` aborts on any mismatch.
* The original formulas, `A`, sampling budgets and solution-generation
  procedure are unchanged.

---

## 4. The three methods

All three share the mathematical target, the certification standard, the
original clause set, the original `A`, the pinned solver (`Glucose3` from
`python-sat 1.9.dev15`) and the pinned checker (`drat-trim` @ `2e3b2dc`).

**A — Baseline.** The continuation's encoding (`src/encode.py`, Sinz-2005
sequential counter, rebuilt per radius) and its query-selection behaviour:
bisection with `mid = (lo+hi)//2`, and **stop on UNKNOWN** (report the interval
established). Run from the unit's certified starting interval.

**B — Query policy only.** Identical encoding, solver configuration and
certification procedure to A. The only change: **after UNKNOWN, keep querying
other radii** under policy P below.

**C — Incremental.** Policy P exactly as in B, but with an incremental
cardinality encoding (`ITotalizer`) and a **persistent, reused** `Glucose3`
whose bound is switched by assumption literals.

B isolates the query policy. C changes encoding *and* state reuse together, so a
C-vs-B difference is attributed to **the combination** and never to either
component alone.

Policy P is constructed so that **B is bit-identical to A until the first
UNKNOWN**: when nothing is excluded, the single run spans `[lo, hi-1]` and P's
upper midpoint is `lo + (hi-lo)//2 = (lo+hi)//2`, the baseline's bisection point,
for **every** interval. (The *lower* midpoint would differ on even-width
intervals and would confound the comparison; it was rejected for that reason.)
Verified exhaustively in `src/test_policy.py`.

---

## 5. Policy P — query selection and timeout handling

State: certified interval `[lo, hi]` (meaning `lo <= eps <= hi`), plus an
**exhausted set** `T` of radii that must not be queried again in this benchmark.
`T` is initialised from the unit's carried-in UNKNOWN radii.

A radius `r` is **useful** iff `r in [lo, hi-1]`. (By monotonicity `eps >= lo`
already implies `Q_r` SAT for every `r <= lo-1`, and `Q_r` UNSAT for `r >= hi`
cannot lower `hi`; so no radius outside `[lo, hi-1]` can move a bound.)

```
candidates C = [lo, hi-1] \ T
1. if C is empty                -> STOP (no useful unattempted radius remains)
2. split C into maximal contiguous runs
3. pick the longest run; tie-break on the smallest start radius
4. query r = start + (end - start + 1) // 2    (upper midpoint, deterministic)
```

Bound updates, and what enters `T`:

| query outcome | bound update | `T` |
|---|---|---|
| SAT, witness **validated** by `src/verify.py` | `lo = max(lo, r+1)` | unchanged |
| SAT, witness **fails** validation | none — hard stop and alarm | — |
| UNSAT, proof **independently checked** | `hi = min(hi, r)` | unchanged |
| UNSAT, proof missing / rejected / check timed out | **none** (solver-reported only) | `r` added |
| UNKNOWN (solver interrupted at the per-invocation limit) | **none** | `r` added |

Adding a radius to `T` on a *failed certification* as well as on UNKNOWN is what
guarantees termination: every query either moves a bound or permanently removes
a radius from the candidate set.

Stop conditions: `lo == hi` (exact), or `C` empty, or the measurement budget
expires. A timed-out radius is **never retried** within this benchmark.

An unchecked UNSAT answer is recorded as solver-reported and **must not tighten
the certified interval**.

---

## 6. Certification under incremental solving

The pinned, already-validated `drat-trim` wrapper (`continuation-2026-10-27/src/dratcheck.py`)
is reused unchanged, including its strict verdict rule: a proof is accepted only
if a line is exactly `s VERIFIED`, with no `s TIMEOUT` / `s NOT VERIFIED` /
`s DERIVATION` / `s MEMORY ALLOCATION ERROR` line; the exit code is recorded but
never decides, because it is unreliable in both directions.

For method C:

* **SAT answers need no rerun.** A model is projected onto the original
  variables and re-checked by `src/verify.py` against the original clauses with
  direct Hamming distances. Assumptions, learned clauses and auxiliary variables
  are irrelevant to that check, so an incremental SAT answer is certified at
  zero extra cost.
* **UNSAT answers are not certified by the incremental solver.** An UNSAT under
  assumptions refutes `formula ∧ assumptions`, not the formula, and a proof
  emitted by a solver carrying learned clauses from earlier queries cannot be
  spliced onto a different query. Learned clauses are never treated as original
  axioms, and proof fragments from different queries are never combined.
* Therefore each candidate upper bound is **re-run in a fresh, proof-producing
  solver on a standalone CNF** containing the original clauses, every
  `ITotalizer` clause, **and the active bound literals as unit clauses** — so
  the checked formula is exactly the query being certified. The resulting DRUP
  proof is checked by drat-trim against that same CNF file.
* **The rerun, its proof generation and its checking all count against C's
  measurement budget**, and are additionally reported as a separate
  certification-rerun cost.

Every certified result binds original formula hash, frozen `A` hash, radius,
encoding name, CNF path + sha256, proof path + sha256, witness path + sha256,
checker name and verdict, through the continuation's `store.py` journal.

---

## 7. Budgets, enforced at process level

| limit | value |
|---|---|
| per SAT solver invocation | **60 s** |
| per measurement per method (encoding + solving + certification reruns + proof checking + required I/O) | **240 s** |
| hard proof-checker timeout | `min(300 s, remaining measurement budget)` |
| measurements × methods | **9 × 3 = 27 runs** (cap: 12 × 3) |
| computational validation + benchmarking, combined | **3 h** |

Enforcement: every (measurement, method) run executes in its **own subprocess**
with a hard wall-clock kill at `240 s + 20 s` grace. An overshoot is recorded,
not hidden. Worst case for the comparison is `27 × 240 s = 108 min`.

Execution: **sequential**, with no competing benchmark jobs. Method order is
rotated deterministically per measurement — for unit index `i` in the fixed
order of §3, the order is `(A,B,C)` rotated left by `i mod 3` — to damp
order effects.

Each method receives the same total budget and the same starting certified
information. Extra solver invocations a method needs for certification count
against its own budget.

Limits are **not** raised after observing results. Incomplete outcomes are
preserved and reported.

Large artifacts are written inside `optimization-2026-10-27/artifacts/`, never to
`/tmp` (a 7.7 GB tmpfs on this machine). Free disk and memory are checked before
the run and the run stops cleanly if they become limiting.

---

## 8. Validation required before any timing

Focused tests, not a repeat of the historical experiments
(`src/test_encoding.py`, `src/test_policy.py`, `src/test_incremental.py`):

1. **Exhaustive tiny-instance check of the new encoding's projected meaning**
   across all radius endpoints: for small `n` and every `r`, the set of original-
   variable assignments satisfying the AtMost encoding equals
   `{x : d_H(x,a) >= r+1 for all a in A}`, by enumeration.
2. **Exact-resolution agreement** with the existing brute-force-validated
   instances on a fixed subset.
3. **Static vs incremental agreement** on the same query, with radii moving both
   **upward and downward**.
4. **Explicit assumption-leakage tests**: assumptions from one query must not
   remain active in the next.
5. **Known SAT and known UNSAT** cases.
6. **The existing effective negative controls**, including corruption of a
   *necessary* proof step. Before calling an accepted corruption a checker
   failure, it must first be established that the altered material was actually
   necessary to the refutation — the continuation found that corruptions landing
   after the empty clause is derived are read by no checker.
7. **A restart test** showing certified bounds survive a kill and **cannot be
   reused for a different `A`**.

If mathematical answers or checker verdicts disagree, the performance comparison
**stops** and the disagreement is investigated first.

If method C cannot preserve independently checkable certification in this round,
that limitation is documented and A-vs-B is completed. The evidence standard is
not weakened to obtain more completed rows.

---

## 9. Reported quantities

Per measurement per method: starting and final certified interval; exactness
reached or not; interval-width reduction; counts of SAT / certified-UNSAT /
unchecked-UNSAT / UNKNOWN queries; time to each certified improvement;
encoding, solving, proof-generation, proof-checking and total wall time;
certification-rerun cost separately; peak memory, formula size, proof size,
artifact storage; and any timeout or resource-limit outcome.

Comparisons are **paired** on identical `(I, A)` measurements. Unresolved-case
results and completed controls are reported **separately**. Speedups are not
reported only on cases where both methods succeeded — failures are shown in the
same table.

**The four hard cases are an optimization set, not a held-out scientific
sample.** Nothing measured on them is evidence about the population of
instances.

---

## 10. Separate audit: the solver-ordering claim

Independently of the optimization, each `eps_C` vs `eps_W` comparison in the
existing certified pilot data is classified as **certified C > W**, **certified
W > C**, **certified equality**, or **unresolved ordering**. For intervals,
`C > W` is established only when `lower_C > upper_W`; overlapping intervals
establish nothing. Denominators are reported explicitly, distinguishing
instances, solver measurements, satisfiable instances and exact measurements.

No coverage fraction is inferred without `|S_I|`, and no general solver ranking
is inferred from this pilot.

---

## 11. Stopping point

Stop after the report. No `n = 96`, no cohort expansion, no model counting, no
connectivity work, no paper revision. No improvement is a valid outcome, and a
failed optimization is reported as a failed optimization — not as evidence that
the approach is impossible.
