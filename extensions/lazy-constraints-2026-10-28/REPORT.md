# Witness tightening and lazy distance constraints — report

Dated 2026-10-28. Workspace `~/scratch/sat-lazy-constraints-2026-10-28/`.
Protocol frozen **before** any measurement: `PROTOCOL.md`, sha256 prefix
`c2047518cf88033a70f23c5be8951caa`, stamped into `data/stage1.json` and
`data/stage2.json`.

Everything outside this workspace was read-only. No repository file, manuscript,
branch or memory file was modified; nothing was committed or pushed by the
measurement. Observed sets were held fixed throughout; `n` stayed 64 on the
hard units; no instance was added or resampled.

Machine-readable: `data/stage1.json`, `data/stage2.json`. Logs:
`results/stage1.txt`, `results/stage2.txt`. Artifacts (CNFs and DRUP proofs):
`artifacts/`.

---

## Stage 1 — witness tightening

**The opportunity is real and exactly where you said it is.** Both loops compute
the witness's actual distance and then discard it:

```
methods.py:144   min_dist=min(hamming(x, a) for a in A)        # computed
measure.py:172   self.lo = max(self.lo, r + 1)                 # not used
```

A witness `x` satisfying `F` with `min_{a∈A} d_H(x,a) = d` proves `ε ≥ d`, so
`lo ← max(lo, d)` is sound. **594 stored witnesses were replayed** against the
observed sets recovered from each stage's own records — 37 from
`optimization-2026-10-27` through its hash-verifying `units.recover()` (9/9
units, both the formula hash and the observed-set hash required to match, 0
excluded), and 557 from the repository pilot through `collections.tar.gz`. No
witness was unmatched.

| | witnesses | loose (`d > r+1`) | max gain | mean gain |
|---|---|---|---|---|
| `optimization-2026-10-27` (n = 64, the hard units) | 37 | **0** | 0 | 0.000 |
| repository pilot (n = 32, 48, 64) | 557 | **79** (14.2 %) | 6 | 0.316 |
| **total** | **594** | **79** (13.3 %) | 6 | 0.316 |

Gain distribution on the pilot: `{0: 478, 1: 38, 2: 10, 3: 13, 4: 12, 5: 5, 6: 1}`.
No witness produced a *smaller* bound, so the tightening is sound on every
stored witness.

**But the recovered information does not reach the reported intervals.**

> **0 of 257 reconstructed measurements would have a strictly better certified
> lower bound.**

The mechanism is the radius ladder: a loose witness at radius `r` proves
`ε ≥ r+1+g`, but the search then issues a query at a *higher* radius that also
succeeds, and the final `lo` is set by the highest successful radius. Every
loose witness here is dominated by a later successful query.

**Where the value actually is: queries skipped.** Replaying each recorded radius
sequence under the tightened rule, a query at radius `r` is redundant if the
tightened bound already established `ε ≥ r+1`:

| | redundant SAT queries |
|---|---|
| `optimization-2026-10-27` (hard units) | **0 of 37** |
| repository pilot | **21 of 557** (3.8 %) |

This is a **lower bound** on the saving, because after the first skip the policy
would choose different radii and this replay cannot know their answers.

**Verdict on Stage 1.** The bound improvement is mathematically justified and
should be adopted — it is a one-line change, it is sound on all 594 stored
witnesses, and it cannot lose. But on the measurements that matter it recovers
**nothing**: zero interval improvements, and zero skipped queries on the hard
`n = 64` units where the cost actually lies. The likely reason the hard units
show gain 0 on all 37 witnesses is that the cardinality constraint is binding —
the solver satisfies `d ≥ r+1` tightly and has no pressure to exceed it.

*Adopt it as a correctness/tidiness fix, not as a speedup.*

## Stage 2 — lazy distance constraints

Both methods re-run here, interleaved per unit, same radius policy, same
encoder, same solver, same checker, same 120 s per-measurement budget. All 9
units recovered with both hashes matching; **0 excluded**, **0 alarms**.

### The headline: a clean dichotomy

| unit | S total | L total | ratio | S width | L width | constraints L needed |
|---|---|---|---|---|---|---|
| `n64_a2.5_k0_W` | 119.3 s | **80.6 s** | **1.48×** | 0 | 0 | 18–44 / 150 |
| `n64_a3.5_k0_W` | 1.4 s | **1.2 s** | **1.15×** | 0 | 0 | 4–25 / 150 |
| `n64_a4.2_k0_W` | 2.6 s | **1.7 s** | **1.49×** | 0 | 0 | 15–30 / 144 |
| `n64_a3.5_k1_W` | 42.0 s | **16.0 s** | **2.63×** | 0 | 0 | 14–48 / 150 |
| `n64_a2.5_k1_W` | 134.6 s | 120.2 s | 1.12× | 11 | 11 | 23–64 / 150 |
| `n64_a2.5_k1_eqW` | 121.8 s | 120.8 s | 1.01× | **2** | 4 | 4–12 / 40 |
| `n64_a2.5_k2_W` | 121.2 s | 121.2 s | 1.00× | **11** | 15 | 62 / 150 |
| `n64_a2.5_k3_W` | 127.8 s | 119.2 s | 1.07× | **11** | 15 | 51 / 150 |
| `n64_a2.5_k4_W` | 119.5 s | 120.7 s | 0.99× | **11** | 15 | 62 / 150 |

**On every unit that resolves, L wins. On every hard unit that does not, L loses
or ties.**

### Where it works

Four units reached an exact answer under both methods in this run, and all four
agree with each other and with the historical exact values: `ε = 26, 16, 9, 18`.

**Equal query counts do not establish pairing, and checking it changed the
result.** An instrumented re-run (`src/verify_pairing.py`; timings *not* taken
from it) recorded the radius sequence and per-query outcome for these four, with
both hashes re-verified:

| unit | S radii | L radii | paired? | stop S/L |
|---|---|---|---|---|
| `n64_a3.5_k0_W` | 12,14,15 | 12,14,15 | **yes** | exact/exact |
| `n64_a4.2_k0_W` | 12,10,9 | 12,10,9 | **yes** | exact/exact |
| `n64_a3.5_k1_W` | 24,20,18,17 | 24,20,18,17 | **yes** | exact/exact |
| `n64_a2.5_k0_W` | 24,28,26 | 24,28,26,**25** | **NO** | budget/exact |

`n64_a2.5_k0_W` is **not** paired: its static ladder hit the budget, the two
methods asked different radius sequences, and in the re-run the static method
stopped at `[25,28]` **without reaching an exact answer** — so its stage-2
"exact" outcome under S sits on the budget boundary and is not reproducible. It
is excluded from every paired claim.

> **Measured in this run, on the four units exact under both: 165.3 s → 99.5 s
> (1.66×).**
> **On the three units that survive pairing verification: 46.0 s → 18.9 s
> (2.43×), checker time 23.2 s → 3.2 s (7.27×).**

Both are reported. The three-unit ratio is larger, but it is not promoted as a
better headline: it rests on three units, and the fourth is excluded for a
stated reason rather than for its number.

**The saving is mainly in certification, though not only there.** Checker time
per unit: 59.5 → 15.5 s, 22.1 → **2.9 s**, 1.1 → 0.2 s, 0.0 → 0.0 s. Solve time
barely moves (58.0 → 59.5 s on `k0_W`; 18.1 → 8.1 s on `a3.5_k1_W`). Encoding
cost rises slightly, as expected from re-encoding each refinement (0.7 → 2.7 s).

So the mechanism that pays is: **a subset encoding produces a much smaller DRUP
proof, and `drat-trim` is the bottleneck.**

### Where it fails, and why

On the five unresolved units L is worse on four and ties on one. The cause is
visible in the iteration counts: L spent **48–59 refinement iterations inside a
single radius query** on `k2_W`, `k3_W`, `k4_W`, completing **1 query** against
S's 3, and so ended at width 15 against S's 11 — it never advanced past its
starting interval. On `k1_eqW` it reached width 4 against S's 2.

This is the predicted failure mode: hard cases need many constraints, and each
refinement is a fresh solve. The loop pays the full solve cost once per
iteration and the budget runs out mid-refinement.

**One counter-signal worth recording.** On `n64_a2.5_k1_eqW` the lazy proofs
were *larger*, not smaller — 524 081 lines against 245 460 at `r = 31`, with the
CNF 3.3× smaller (12 352 vs 41 024 variables). Refuting the subset is a logically **stronger** statement than refuting the
full query, since `sat(Q_r^A) ⊆ sat(Q_r^S)`. That is a statement about logical
strength only: **it does not force proof length or runtime to increase**, and
this stage's own data refutes that inference — on the four resolved units the
subset proofs are *smaller*, and aggregate checker time falls from 82.7 s to
18.6 s. `k1_eqW` is a measured counter-case, not a general direction. The method
wins when the subset is still refutable *and* the smaller encoding more than
compensates; that held on four units and failed on `eqW`.

### Constraints actually needed

**Fewer constraints do suffice**, everywhere: L terminated using 4–64 of 150
(and 4–12 of 40), i.e. **3 %–43 %** of the observed set. The binding problem on
hard units is the **number of refinement iterations**, not the final constraint
count.

### Certification integrity

| | S | L |
|---|---|---|
| certified UNSAT upper bounds | 12 | 11 |
| unchecked UNSAT (reported, moves no bound) | 1 | 1 |
| `UNKNOWN` | 8 | 5 |
| verified SAT witnesses | 10 | 7 |
| alarms | **0** | **0** |

Every L lower bound came from a witness verified against the **full** observed
set, and every L upper bound from a checker-`VERIFIED` proof of a subset query,
which is sound by the inclusion argument frozen in `PROTOCOL.md`. L's lower
`UNKNOWN` and SAT counts simply reflect its fewer completed queries.

### Verdict on Stage 2

**The mechanism is real, exact, and worth adopting selectively — but it is not a
speedup for the hard queries, which is where the cost lies.** It turns a
certification bottleneck into a 1.66× aggregate saving on measurements that
already complete, and it makes the measurements that do not complete *worse*.

A reasonable next design, not tested here: run S and L concurrently per radius
and take the first to certify, or start lazy and fall back to the full encoding
once the refinement count exceeds a threshold (the resolved units needed ≤ 48
iterations in total across *all* their queries, while the failing units burned
48–59 inside one). That is a hypothesis, not a result.

## Costs

| item | value |
|---|---|
| Stage 1 | no solver, pure replay, seconds |
| Stage 2 total | **1 508.6 s** (25.1 min) against the **75 min** cap |
| per-measurement budget | 120 s (reduced from the baseline stage's 240 s — **stated in the frozen protocol**) |
| measurements | 18 (9 units × 2 methods), 0 excluded |
| witnesses replayed | 594, 0 unmatched |

**Budget caveat.** The 120 s per-measurement budget is half the baseline stage's
240 s. The four resolved units resolved well inside it, so their comparison is
unaffected. The five unresolved comparisons **are** budget-sensitive: with 240 s
S would likely advance further, and L might complete more refinement. The
dichotomy's direction is robust — L completed fewer queries on the hard units at
any budget that cuts a refinement loop short — but the widths quoted for the
unresolved units are specific to this budget.

## What is not claimed

* No solver ranking, and none used. `C1` and `C7` of
  `docs/SOURCE_OF_TRUTH.md` remain retracted.
* Stage 1 makes **no runtime claim**. Its measured effect on reported intervals
  is zero, and the query saving is a lower bound on a divergent replay.
* No exactness is traded for speed: every lower bound comes from a witness
  verified against the **full** observed set, and every upper bound from a
  checker-`VERIFIED` UNSAT proof or an arithmetic triviality.
* No measurement was excluded from a denominator. `UNKNOWN`, budget stops,
  unchecked UNSAT and checker failures are reported as themselves. All 18
  attempted measurements appear above; 0 were excluded.
* **No general speedup is claimed for lazy constraints.** It is faster on the
  four units that resolve and worse on four of the five that do not.
* The `n64_a2.5_k0_W` static run is labelled `budget` yet reached an exact
  answer: the loop checks the remaining budget before asking for the next
  radius, so a measurement that becomes exact exactly as the budget expires is
  labelled `budget`. Both methods returned `ε = 26`. A cosmetic labelling
  artefact, recorded rather than silently relabelled.
* Stage 2 compares against a **re-run** static baseline on this machine, not
  against the timings previously recorded by `optimization-2026-10-27`.
