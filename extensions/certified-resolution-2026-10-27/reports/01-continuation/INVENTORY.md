# State of the workspace on disk, verified 2026-10-27

Established by reading the files, not by trusting the previous session's summary.
Every count below was recomputed from the CSVs and logs.

## The previous summary's figures, checked

| claim in the summary | verified? | note |
|---|---|---|
| 349/349 validation | **yes** | 349 rows; `ε̂_oracle = ε̂_brute` 349/349, `= ε̂_published` 349/349, `proof_verified` 349/349, all one certificate class |
| `n = 24` pilot complete | **yes** | 15 rows, 15 SAT, all exact and independently checked |
| `n = 32` pilot complete | **yes, with a correction** | 15 rows, 13 SAT — but **3 of the 13 have an unchecked upper bound** (see below) |
| `n = 48`: eight cases processed | **yes** | 8 rows of 15 cells |
| `n = 64`: two log-only cases | **yes** | 2 lines in `results/pilot_4864.txt`, no CSV, no artifacts |

**The correction.** The original run's "100 %" figures are the *advance rule*
(fraction of satisfiable instances with an exact `ε̂`), not a certification rate.
Counting certificates instead: at `n = 32` ids 1, 3, 5 and at `n = 48` ids 1–5
carry `upper: solver-reported`, i.e. their `ε̂` rests on the solver's bare UNSAT
word. The Python checker's 120 s-per-proof budget was exceeded on those eight.

## The decisive fact: no proof, CNF or witness artifact survives

```
find . -not -path './.venv/*' -not -path './repo/*' \
     \( -name '*.cnf' -o -name '*.drup' -o -name '*.drat' -o -name '*.proof' \
        -o -name '*.json' -o -name '*.pkl' -o -name '*witness*' \)   ->   (nothing)
```

`src/oracle.py:solve_Q` accepts a `cnf_dir`, but `src/pilot.py` and
`src/validate.py` never pass one, so every CNF, proof and witness existed only
in memory. **Nothing can be re-checked without re-deriving it**, which settles
§7's first question: there are no saved `n = 48`/`n = 64` proofs to verify
without rerunning the SAT search.

What makes this recoverable rather than fatal is that the inputs are
deterministic: formulas come from `gen(n, α, k)`, and both observed sets are
seeded from the instance counter. Every surviving `n = 48` and `n = 64` record's
observed-set sizes were reproduced exactly (see `PROTOCOL_AMENDMENT.md` §3).

## Classification of everything on disk

### 1. Completed and independently verified

| where | count | evidence |
|---|---|---|
| published 349-cohort | **349 instances** | `ε̂_oracle = ε̂_brute` (enumeration — no solver, no encoder) **and** a DRUP proof accepted by `src/drup.py`; witness-verified lower bounds, 0 failures |
| pilot `n = 24` | **15 of 15 cells** | exact, upper bound proof-checked; brute-force cross-check available at this size |
| pilot `n = 32` | **10 of 13 satisfiable** | exact, upper bound proof-checked |
| pilot `n = 48` | **2 of 7 satisfiable** (ids 6, 8) | exact, upper bound proof-checked |

### 2. Solver-reported, awaiting proof checking

| where | ids | why |
|---|---|---|
| pilot `n = 32` | 1, 3, 5 | Python proof check exceeded its 120 s budget |
| pilot `n = 48` | 1, 2, 3, 4, 5 (all α = 2.5) | same; these are the 480–760 s rows |

`ε̂` is believed correct in all eight (the lower bounds *are* witness-verified),
but the upper bound is the solver's word alone, so **none of the eight is a
certified exact resolution**.

### 3. Partial searches with valid bounds

| where | what |
|---|---|
| `n = 64` log row 2 | `interval only`: `ε̂_W` unresolved after 7 queries; `ε̂_C = 38`. The interval it established is valid but rests on unchecked UNSAT answers |

### 4. Log-only records with missing artifacts

| where | what survives | what does not |
|---|---|---|
| `n = 64` log rows 1–2 | two printed lines in `results/pilot_4864.txt`: `ε̂_W = 26` / `None`, `ε̂_C = 37` / `38`, 12 / 7 queries, 153 450 aux vars, 307 360 clauses, 177 MB RSS | no CSV row, no CNF, no proof, no witness. Row 1's upper bound was `solver-reported` even then |

These two are retained as **historical, unverified records** and are not
upgraded by anything done in the continuation; the continuation's own
re-measurement of the same two cells is reported separately.

### 5. Never started

| where | cells | which |
|---|---|---|
| `n = 48` | **7 of 15** | (α=3.5, k=1…4) and (α=4.2, k=2…4) — *not* "ids 9–15": the id counter skips when the wall clock fires |
| `n = 64` | **13 of 15** | (2.5, k=2…4), (3.5, k=0…4), (4.2, k=0…4) |

## Preservation

Nothing in `..` was modified. `REPORT.md`, `CLAIMS.md`, `ENCODING.md`,
`MANIFEST.md`, `PILOT_PROTOCOL.md`, `data/*`, `results/*` and `src/*` are
untouched; the original `src/encode.py`, `src/verify.py` and `src/drup.py` are
imported unchanged by the continuation code. All new code, data, artifacts,
journals and documents live under `continuation-2026-10-27/`. No repository was
modified, nothing was committed, pushed or published.
