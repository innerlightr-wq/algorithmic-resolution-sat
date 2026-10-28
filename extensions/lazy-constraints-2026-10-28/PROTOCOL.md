# Protocol — witness tightening and lazy distance constraints

Frozen 2026-10-28 **before** any measurement. Workspace
`~/scratch/sat-lazy-constraints-2026-10-28/`. Everything outside this workspace
is read-only; no repository file, manuscript, branch or memory file is modified
by the measurement scripts.

## Question

Two mechanisms, tested separately, on **fixed observed sets**:

1. **Witness tightening.** `measure.py` and `methods.py` both compute a
   witness's actual `min_dist` to the observed set and then update the lower
   bound only to the requested threshold `r + 1`. Since a witness `x ∈ S_F` with
   `min_{a∈A} d_H(x,a) = d` proves `ε ≥ d`, the sound update is
   `lo ← max(lo, d)`. **How much certified information does this recover from
   witnesses already stored and already verified?**
2. **Lazy distance constraints.** A radius query carries one distance constraint
   per observed solution. Start from a subset `S ⊆ A`, solve, check the
   candidate against the **whole** of `A`, and add a violated constraint on
   failure. **Do fewer constraints suffice to certify the same answer, and does
   that reduce total time including certification?**

## Exactness argument, stated before measuring

Write `Q_r^S` for the query carrying distance constraints only for `a ∈ S`.

* `sat(Q_r^A) ⊆ sat(Q_r^S)` for `S ⊆ A`, since `Q_r^S` is a conjunction over a
  sub-family. Hence **`Q_r^S` UNSAT ⟹ `Q_r^A` UNSAT**, and a checked UNSAT
  proof for the subset certifies the full query's upper bound.
* A candidate `x` satisfying `F` and `min_{a∈A} d_H(x,a) ≥ r+1` is a valid
  witness for `Q_r^A` regardless of which `S` produced it. Verification is
  always against the full `A`.
* Therefore the lazy loop is **exact**: it returns only certified SAT witnesses
  and certified-UNSAT upper bounds, both valid for the full query.

Refinement rule: on a candidate that fails the full check, add the **nearest**
`a ∈ A` (the argmin of `d_H(x,a)`) to `S`. That constraint is violated by `x`,
so the same candidate cannot recur.

## Units

The nine experimental units of `optimization-2026-10-27`, recovered through its
own `units.recover(tag, obs_seed_id)`, which re-verifies the formula hash and
the observed-set hash before use. A unit whose hashes do not match is
**excluded and reported**, never silently repaired.

| group | tags | role |
|---|---|---|
| opt-primary | `n64_a2.5_k1_W` … `k4_W` | unresolved, certified start `[17,32]` |
| opt-secondary | `n64_a2.5_k1_eqW` | unresolved, certified start `[29,64]` |
| control | `n64_a2.5_k0_W`, `n64_a3.5_k1_W`, `n64_a3.5_k0_W` | historical exact 26, 18, 16 |

Stage 1 additionally replays every stored witness in
`optimization-2026-10-27/artifacts/`, `continuation-2026-10-27/artifacts/`,
`continuation-2026-10-27/bench/artifacts/` and the repository pilot's
`artifacts/`, with the observed set recovered from that stage's own records.

## Methods compared, Stage 2

* **S (static baseline)** — `Q_r^A` encoded from scratch with every distance
  constraint, `seqcounter`, exactly as `methods.static_query`.
* **L (lazy)** — the loop above, same encoder, same radius policy, same solver,
  same checker.

Both re-run **in this stage on this machine**, interleaved per unit in the
order S then L, so the comparison is paired and not against previously recorded
timings on unknown machine conditions.

## Fixed limits, set now

| limit | value |
|---|---|
| total new computation | **75 min**, hard |
| per-measurement budget | **120 s** (reduced from the baseline stage's 240 s; stated, not hidden) |
| per-solver-invocation | 60 s |
| checker cap per proof | 120 s |
| lazy initial subset `|S₀|` | 4, chosen as the 4 observed solutions pairwise farthest apart by a greedy max-min pass |
| lazy refinement cap | 60 iterations per query |
| radius policy | the baseline's own `methods.select_radius`, identical for both methods |

No escalation: `n` stays 64, no instance is added, no observed set is changed or
resampled, and no third method is introduced after seeing results.

## Recorded per measurement

Total wall time **including certification**, encode/solve/check split, exact
answer obtained or not, final certified interval and its width, number of
solver invocations, and for L the number of distance constraints actually
needed (`|S|` at termination) against `|A|`.

## Reporting rules

* Every attempted unit appears in the denominator. Timeouts, `UNKNOWN`, and
  checker failures are reported, never excluded.
* An UNSAT upper bound counts as certified **only** on a `VERIFIED` checker
  verdict or an arithmetic triviality; an unchecked UNSAT is reported as
  unchecked and does not move a bound.
* A lower bound counts only with a witness verified against the **full** `A`.
* Stage 1 reports recovered information as a certified-interval change, not as
  a runtime claim. **Better bounds are mathematically justified; any runtime
  improvement must be measured, and is reported separately.**
* If L is slower or no better, that is the result and it is reported as such.
* No solver ranking is claimed or used. `C1` and `C7` of
  `docs/SOURCE_OF_TRUTH.md` remain retracted.
