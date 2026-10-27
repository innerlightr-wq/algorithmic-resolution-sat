# Protocol amendment 1 — dated 2026-10-27

Amends `../PILOT_PROTOCOL.md` (dated 2026-10-26). The original protocol and all
original result files are **unchanged**; everything new lives under
`continuation-2026-10-27/`. Written and saved **before** any continuation
measurement was run. Budgets below were chosen from the benchmark in
`results/bench_*.txt`, not guessed.

## Why an amendment is needed

The overnight run was ended by an unclean machine shutdown at ~02:10 on
2026-10-27 (boot at 07:35, no clean shutdown record). Two things were left
undone, and one was never possible in the first place:

1. `n = 48` stopped after 8 of 15 instances on the original 3600 s-per-size
   wall clock. **That truncation stands as a valid outcome under the original
   budget** and is not retracted or restated.
2. `n = 64` was lost mid-instance. Its two log lines have **no surviving
   artifacts** (see §2 of the continuation report), so they remain *historical,
   unverified records*.
3. Pure-Python proof checking consumed 98 % of all measured time and failed to
   certify the five `n = 48`, `α = 2.5` upper bounds within its 120 s-per-proof
   budget. Those five `ε̂` values were therefore **solver-reported only**.

## 1. Checker replacement

| item | value |
|---|---|
| checker | `drat-trim`, <https://github.com/marijnheule/drat-trim> |
| commit | `2e3b2dc0ecf938addbd779d42877b6ed69d9a985` (2024-11-25) |
| build | `gcc drat-trim.c -std=c99 -D_POSIX_C_SOURCE=200809L -O2 -o drat-trim` |
| compiler | `gcc (GCC) 16.2.1 20260810` |
| `drat-trim.c` sha256 | `d834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee` |
| binary sha256 | `e17cd2e8de37c4c43bf88360ae3d17740781fe971175bf0b0c935ee3aae4ae19` |
| source modified? | **no** — `git status` clean; only the binary is untracked |

The upstream `Makefile` target does not compile here: under `-std=c99` modern
glibc hides the POSIX declaration of `getc_unlocked`, used at `drat-trim.c:986`.
`-D_POSIX_C_SOURCE=200809L` exposes the declaration **without editing the
source and without changing the language standard**. No other deviation.

**Proof format.** The solver is `Glucose3` via `python-sat 1.9.dev15` with
`with_proof=True`. Its `get_proof()` output was inspected, not assumed: every
line is a space-separated clause of DIMACS literals terminated by `0`, with
**no `d` deletion lines and no RAT markers** — i.e. addition-only DRUP, a strict
subset of DRAT, which drat-trim reads natively (the upstream repo ships
`examples/example-Schur.drup` and it verifies here). Proof files are written
with the extension `.drup` and handed to drat-trim as-is; no file is renamed to
imply a format it does not have.

**Acceptance rule.** Taken from `drat-trim.c` (lines 905, 1479–1483, 1500) and
then confirmed by experiment:

* `s VERIFIED` → exit 0, *except* that parse-level trivial UNSAT prints
  `c trivial UNSAT` + `s VERIFIED` and **exits 1**;
* `s NOT VERIFIED` → exit 1;
* `s TIMEOUT` → **exit 0** (`exit(0)` at line 905);
* verdict lines are prefixed with a carriage return, so a `^s ` anchor misses
  them;
* `s NOT VERIFIED` and the `-S`-mode line `c VERIFIED derivation: …` both
  contain the substring `VERIFIED`.

So the exit code is wrong in both directions and substring matching is unsafe.
A proof is accepted **iff**, after splitting on `\n` and `\r` and stripping,
some line is **exactly** `s VERIFIED` and no line is exactly `s TIMEOUT`,
`s NOT VERIFIED`, `s DERIVATION` or `s MEMORY ALLOCATION ERROR`. Crash, signal,
wall-clock kill, missing or empty proof, and unparsable output are all
`UNRESOLVED` — never a pass, never a refutation. Implemented in
`src/dratcheck.py`; `dratcheck.verified()` is the only place a pass is decided.

Each proof is checked against the **standalone CNF of the same query** — all
original clauses plus every cardinality clause, no assumptions — written to disk
before the solver ran. The journal links, per query: original-formula hash,
frozen-`A` hash, radius, CNF path + sha256, proof path + sha256, witness path +
sha256, checker name, verdict, exit code and timing.

## 2. Checkpointing changes

`src/store.py` + `src/measure.py`. An artifact is fsync'd to its final path
**before** any journal record names it, so a record never promises a file that
is absent. Records are appended as JSON lines and fsync'd individually; a torn
final line is dropped and reported, never silently accepted.

Query states are kept distinct and never merged:
`SOLVED_SAT` / `WITNESS_VERIFIED` / `SOLVED_UNSAT` (solver done, **checking
pending**) / `PROOF_VERIFIED` / `PROOF_REJECTED` / `PROOF_UNRESOLVED` /
`TRIVIAL_UNSAT` / `UNKNOWN`. `SOLVED_UNSAT` is journalled before checking
starts, so a restart can tell "solver finished, checking pending" from "proof
checked"; only `WITNESS_VERIFIED`, `PROOF_VERIFIED` and `TRIVIAL_UNSAT` are
reused on resume.

**A query is reused only when the original-formula hash *and* the frozen-`A`
hash both match.** A matching instance id or generator seed is explicitly not
sufficient: an observed set produced by a solver is not guaranteed to be
reproducible bit-for-bit, and reusing a query across a different `A` would
measure a different object.

## 3. Cases to resume, and the identifier hazard

The original pilot's instance counter `iid` increments per generated instance
and **skips numbers when the wall clock fires**, and `iid` seeds the observed
sets (`walksat_A`/`cdcl_A` are seeded `PILOT_SEED + 777 + iid` and
`PILOT_SEED + 3333 + iid`). So `iid` is *not* a function of `(α, k)`. The
historical mapping was reconstructed and **verified by reproducing every
observed-set size**:

| n=48 historical id | (α, k) | `|A_W|`, `|A_C|` reproduced |
|---|---|---|
| 1–5 | (2.5, 0…4) | 150, 40 — all five exact |
| 6 | (3.5, 0) | 129, 40 — exact |
| 7 | (4.2, 0) | UNSAT, kept in the record |
| 8 | (4.2, 1) | 44, 38 — exact |

Both `n = 64` log rows likewise reproduce exactly (`|A_W| = 150`, `|A_C| = 40`).

Consequently the **never-run** `n = 48` cases are (3.5, k=1…4) and
(4.2, k=2…4) — seven cases, not "ids 9–15".

To resume and extend without overwriting anything:

* **Formulas** come from `gen(n, α, k)` and are unchanged — they do not depend
  on `iid`.
* **Historical cases** are re-measured with their recorded `iid`, which
  reproduces their frozen `A` exactly (verified above).
* **Never-run cases** are assigned the `iid` they would have had in an
  uninterrupted run (3.5 → 7,8,9,10; 4.2 → 11…15). Two of those values collide
  with historical ids *for different formulas*; the collision is in the
  identifier only, not the measurement. Every row therefore carries an explicit
  `measurement_id` of the form `n{n}_a{α}_k{k}`, plus `obs_seed_id` recording
  which `iid` seeded `A`. **No historical row is overwritten.**

Work to do, by category:

| category | cases | why |
|---|---|---|
| `n=48` upper bound never certified | ids 1–5 (α=2.5) | Python checker timed out; `ε̂` was solver-reported only |
| `n=48` never started | (3.5, k=1…4), (4.2, k=2…4) | wall clock |
| `n=48` already certified | ids 6, 8 | **regression check only** — the checker changed |
| `n=64` log-only, no artifacts | ids 1, 2 | re-measure; historical values kept as unverified records |
| `n=64` never started | (2.5, k=2…4), (3.5, k=0…4), (4.2, k=0…4) | lost to the shutdown |

`n = 24` and `n = 32` are **not** re-run: all their satisfiable instances were
already exact with independently checked upper bounds.

## 4. Limits and budgets

| limit | original | amended | note |
|---|---|---|---|
| per SAT query | 60 s | **60 s** | unchanged; a timeout yields UNKNOWN, never UNSAT |
| per measurement (one `ε̂`) | 600 s | **900 s** (`n=48`), **1200 s** (`n=64`) | raised because `n=64` solve alone was ~130 s over 12 queries |
| proof checking, per proof | 120 s Python / 200 000 steps | **300 s** drat-trim | hard subprocess kill at 330 s |
| per-size continuation budget | 3600 s | **5400 s** (`n=48`), **10800 s** (`n=64`) | counted fresh; see §5 |
| overall continuation budget | — | **16200 s** (4.5 h) | hard stop |
| memory | 8 GB soft | **8 GB soft** | peak RSS recorded per measurement |

**Previously consumed time is not carried over.** The original `n = 48` run
spent its 3600 s and that outcome stands on its own; the continuation's budget
is a new, separately reported allocation. Any instance completed under the new
budget is reported as "completed under amendment 1", never folded into the
original run's totals.

**Stop conditions.** Stop a size when its per-size budget is exhausted; stop
everything when the overall budget is exhausted; stop immediately and report if
the compiled checker ever returns `PROOF_REJECTED` on a proof the solver
produced, or if a SAT witness fails independent verification. Unlike the
original, exhausting the per-size budget ends that **whole size** rather than
only the current density stratum — the original's `break` exited only the inner
loop, which is why `n = 48` sampled 5/1/2 across the three densities instead of
stopping outright. Remaining cases are reported as not attempted.

## 5. What is deliberately unchanged

* The target: `ε̂(A,I) = max_{x⊨I} min_{a∈A} d_H(x,a)`.
* The radius-search strategy: binary search on `r` over `[0, n]`,
  `mid = (lo+hi)//2`, identical to `src/oracle.py:covering_radius`.
* The encoder (`src/encode.py`) and the independent witness verifier
  (`src/verify.py`), imported unchanged — `verify.py` still imports no SAT
  library and no encoder.
* Instance generation, density strata `{2.5, 3.5, 4.2}`, 5 instances per cell,
  `PILOT_SEED = 20261026`, and the WalkSAT (`K=150`, `max_flips=3000`,
  `p_noise=0.5`) and CDCL (`R=5`, `T=8`) observation budgets — **not** scaled
  with `n`.
* UNSAT instances, unresolved instances and failures stay in the record and are
  never replaced by easier ones.
* The equal-distinct-size comparison keeps the original's `want_proof=False`,
  so it stays an explicitly **uncertified secondary** comparison, exactly as
  before. Nothing that was certified becomes less certified.
* Certification remains two-sided: a witness-verified lower bound **and** an
  independently checked upper bound. For `k = 0` the lower bound is labelled
  `vacuous (k=0)` — `ε̂ ≥ 0` holds by definition and there is no `Q_{-1}` — and
  is not described as "verified". A bare solver UNSAT is never an independently
  checked upper bound.

## 6. What this still cannot establish

Unchanged from the original protocol: 15 instances per size, no held-out split,
and without `|S_I|` no absolute coverage fraction. A few completed larger
instances do **not** show that the WalkSAT/CDCL trade-off generalises. This
remains a feasibility pilot, not a powered empirical study.
