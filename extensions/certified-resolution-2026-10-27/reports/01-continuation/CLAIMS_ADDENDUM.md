# Claims ledger — addendum 1, dated 2026-10-27

**This file adds to `../CLAIMS.md`; it erases nothing.** Every claim, limitation
and unresolved item in the original ledger still stands unless a row below says
explicitly that it is closed or corrected, and in that case the original wording
is quoted so the change is visible.

Levels are the original ones, plus:
**compiled-proof-checked** — a DRUP proof accepted by `drat-trim` @ `2e3b2dc`
against the standalone CNF of the same query, under the strict verdict rule in
`src/dratcheck.py`.

## Closed: the one gap the original ledger named

> **N7 (original wording)** — "`src/drup.py` is my own checker and has **not**
> been cross-validated against an established tool such as `drat-trim`, which
> this environment declined to fetch and compile. It rejects a tampered proof
> and agrees with the exhaustive route wherever both ran, but it is not an
> independently audited checker."

| # | Statement | Level |
|---|---|---|
| A1 | **N7 is now closed.** `drat-trim` was fetched, pinned and compiled here (commit `2e3b2dc0ecf938addbd779d42877b6ed69d9a985`, binary sha256 `e17cd2e8…`, `drat-trim.c` unmodified — only the build flag `-D_POSIX_C_SOURCE=200809L` was added, because modern glibc hides the POSIX declaration of `getc_unlocked` under `-std=c99`). The two checkers were run on identical CNF+proof bytes | measured |
| A2 | On every benchmark case where the Python checker finished inside its budget, the two checkers **agree** | measured (`data/bench_small.csv`, `data/bench_large.csv`) |
| A3 | Upper bounds are now **compiled-proof-checked**, so the audit no longer rests on a checker written for it. The original route (`src/drup.py`) is retained and still run as the cross-check, not discarded | by construction |

## Corrected

| # | Statement |
|---|---|
| A4 | **The original "100 %" pilot figures are an advance rate, not a certification rate.** `REPORT.md` and the original pilot output report the fraction of satisfiable instances with an *exact* `ε̂`. Counting *certificates* instead: `n = 32` ids 1, 3, 5 and `n = 48` ids 1–5 carry `upper: solver-reported`, so **8 rows across `n = 32` and `n = 48` had an upper bound that was never independently checked**. Neither the original report nor this one claimed otherwise, but the two numbers are easy to conflate and were not separated before |
| A5 | **The original `n = 48` truncation sampled 5/1/2 across the three densities rather than stopping outright**, because `src/pilot.py`'s wall-clock `break` exits only the inner `k` loop and then proceeds to the next density. The 8 recorded rows are therefore (α=2.5, k=0…4), (α=3.5, k=0), (α=4.2, k=0), (α=4.2, k=1) — **not ids 1–8 of a single sweep**. The never-run cells are (α=3.5, k=1…4) and (α=4.2, k=2…4) |
| A6 | **The instance counter `iid` seeds the observed sets and skips values when the wall clock fires**, so `iid` is not a function of `(α, k)`. Reconstructing the historical mapping and reproducing every surviving observed-set size was a prerequisite for resuming at all; both `n = 64` log rows and all 8 `n = 48` rows reproduce exactly | measured |

## New: what the compiled checker actually does and does not guarantee

| # | Statement | Level |
|---|---|---|
| A7 | **`drat-trim`'s exit code is unsafe in both directions.** `s TIMEOUT` is printed with `exit(0)` (`drat-trim.c:905`); a parse-level trivial UNSAT prints `c trivial UNSAT` + `s VERIFIED` yet returns 1, because `sts` keeps its `ERROR` initialiser on that path (`drat-trim.c:1477–1500`). Both confirmed by experiment | measured |
| A8 | **Substring matching on the output is unsafe.** `s NOT VERIFIED` contains `VERIFIED`, and `-S` mode prints `c VERIFIED derivation: …`. Verdict lines are also prefixed with a carriage return, so a `^s ` anchor matches nothing. Acceptance requires a line *exactly* equal to `s VERIFIED` with no `s TIMEOUT` / `s NOT VERIFIED` / `s DERIVATION` / `s MEMORY ALLOCATION ERROR` line | by construction + 6 parsing assertions |
| A9 | Crash, signal, hard wall-clock kill, missing proof, empty proof and unparsable output are all `UNRESOLVED` — never a pass and never a refutation of the proof | by construction |
| A10 | **The solver emits addition-only DRUP**: `Glucose3` via `python-sat 1.9.dev15` returns one space-separated clause per line terminated by `0`, with no `d` deletion lines and no RAT markers. This was inspected, not assumed. It is a strict DRAT subset, which `drat-trim` reads natively; no file was renamed to imply a format it does not have. A corollary: `src/drup.py`'s "deletions are ignored, which is sound" note is correct but **vacuous on this pipeline**, because no deletion line is ever produced | measured |
| A11 | **A backward-mode `s VERIFIED` certifies that the formula is unsatisfiable, not that the whole proof text is well-formed.** `drat-trim` checks only the lemmas in the unsatisfiable core (e.g. 76 of 350 lines on instance 40). That is exactly the claim the audit needs — the upper bound — and nothing more is claimed | proved (soundness of core-only checking) + measured core sizes |

## New: control design, including two of my own bad controls

| # | Statement | Level |
|---|---|---|
| A12 | **Corrupting a proof after the empty clause is derived is not a control.** The Glucose proof for instance 40 derives the empty clause at RUP step 82 of 350 lines. My first attempts — injecting a non-RUP clause at line ~116 and sign-flipping a literal in the *final* lemma — were accepted by **both** checkers, because neither reads the dead tail. Recorded because it would otherwise read as a checker failure, and because it is the same trap as C10 and as "deleting a redundant step" | measured; 2 controls discarded |
| A13 | Controls that *do* invalidate, and are rejected by **both** checkers with agreement: keep only non-core lemmas; sign-flip a literal in an **early core** lemma; truncate to half the core lemmas; an unjustified bare empty clause against a genuinely UNSAT CNF | measured, 4/4 rejected |
| A14 | **An independently-confirmed satisfiable CNF paired with an UNSAT certificate is rejected.** `Q_{k-1}` for instance 40 (4 345 vars, 7 588 clauses) was confirmed satisfiable by evaluating a stored full model clause-by-clause — no solver, no proof checker — and then paired both with the genuine proof of `Q_k` and with a bare empty-clause proof. Both `s NOT VERIFIED` | measured |
| A15 | **A proof checker cannot catch an encoder bug.** Both deliberately broken encoders (C8, C9) produce CNFs that really are unsatisfiable at the radius they return, so a refutation of them verifies correctly. Only `src/verify.py` (no SAT library, no encoder) and exhaustive enumeration detect those bugs. The compiled checker strengthens the upper bound, and changes nothing about the lower bound | proved + measured |
| A16 | **One genuine checker disagreement, and it is Python incompleteness, not `drat-trim` unsoundness.** With the explicit empty clause stripped, `drat-trim` still reports `s VERIFIED` (it reconstructs the conflict) while `src/drup.py` reports "proof ended without deriving the empty clause". The formula *is* unsatisfiable, so `drat-trim` is right; `src/drup.py` requires the empty clause syntactically. The case cannot arise from a real Glucose proof, which always ends with an explicit `0` | measured |

## New: costs, and a limitation of the original checker

| # | Statement | Level |
|---|---|---|
| A17 | **`src/drup.py`'s time budget is not enforceable.** `check_proof` tests `max_seconds` only between proof steps, so one unit-propagation pass over a large accumulated clause set can overrun it without bound. The original run's "120 s per proof" was therefore not a real limit, and the fresh comparison here had to impose an **external hard kill**. Every Python overrun below is reported as a timeout at a stated budget and is **never** extrapolated to an estimated finishing time | measured |
| A18 | **`drat-trim` is slower than the in-process Python checker on trivial proofs**, because it pays a ~50 ms process-start-and-parse floor that an in-process call does not. On the 13–24-line proofs at α=4.2 the Python check is effectively free. The compiled checker wins only once proofs are large — which is exactly the regime that blocked the pilot | measured |
| A19 | **Proof checking is no longer the dominant cost.** The original M6/M8 ("proof checking is `98 %` of the oracle's wall clock") held for the pure-Python checker and **no longer holds for the pipeline**: the check share of encode+solve+check is `52.5 %` at `n = 48` and `39.6 %` at `n = 64`, where solving overtakes it (`564.7 s` solve vs `378.8 s` check). M6 and M8 remain true as statements about `src/drup.py` at `n ≤ 20`; they are superseded as statements about the pipeline | measured |
| A20 | **The binding constraint is now a single SAT query, not certification.** The four unresolved cells are all `n = 64`, α=2.5, and each stops because the `r = 24` query returns UNKNOWN at the protocol's 60 s per-query timeout, while that same cell's `r = 32` refutation was independently checked in 21.5–60.7 s. The cost ranking at `n = 64` is solve > check > encode | measured |
| A21 | **A certified interval is not a certified exact value, and is reported as neither more nor less.** For those four cells both endpoints are independently certified — witness-verified `ε̂ ≥ 17` and proof-checked `ε̂ ≤ 32` — yet `exact_certified` is `False` and the row reads `interval only`. `certified_upper` and `solver_reported_upper` are mutually exclusive fields, so no row can be read as certified on the strength of an unchecked UNSAT | by construction + measured |
| A22 | **All eight previously solver-reported upper bounds are now independently checked**, with every `ε̂` unchanged (`n = 48` ids 1–5 → 17, 15, 15, 16, 15; `n = 32` ids 1, 3, 5 → 9, 8, 9). The certification was missing, not the answer. The three `n = 32` rows took **11 s** against the ~1 195 s of Python checking that had failed to certify them | measured |

## Unresolved — updated

| # | Statement |
|---|---|
| U1 | *(unchanged)* Whether the paper's resolution/connectivity trade-off persists beyond `n = 20` — the pilot measures feasibility, not the phenomenon |
| U2 | *(unchanged)* Whether a better cardinality encoding removes the `|A| · n · r` blow-up |
| U3 | **Answered for `n ≤ 48`, and reframed above it.** "Whether proof checking can be made cheap enough to certify every query at pilot sizes" — yes at `n = 48`, where **14/14 satisfiable cells are exact certified** and checking is no longer dominant (A19). At `n = 64` checking is still affordable (A19), but **11/15** is the certification rate and the four failures are caused by SAT solving, not checking (A20). So the original question is settled; the successor question is whether the mid-radius SAT query can be made tractable at `n ≥ 64` |
| U4 | **New.** `drat-trim` has not itself been verified against a formally verified checker (e.g. `cake_lrat`). Our pipeline emits DRUP, not LRAT, so the LRAT route would need the solver to emit LRAT or `drat-trim`'s `-L` output to be checked in turn. The audit now rests on *two independent checkers that agree*, which is strictly stronger than before, but not on a verified one |
| U5 | **New.** Whether the `n = 64` cells left unattempted under amendment 1's budget behave like the completed ones is unknown and is not inferred |
