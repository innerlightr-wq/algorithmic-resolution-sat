# Optimization report — query strategy and incremental encoding

Dated 2026-10-27. Workspace `optimization-2026-10-27/`. The original audit and
`continuation-2026-10-27/` are unmodified. No repository or manuscript was
touched; nothing was committed, pushed or published; no larger experiment was
begun.

Protocol frozen before the comparison: `PROTOCOL.md`. Claims ledger:
`CLAIMS.md`. Machine-readable: `data/paired_results.csv`,
`data/optimization_summary.json`, `data/ordering_audit.csv`,
`data/ordering_summary.json`. Raw logs: `results/`.

---

## 1. Question and answer in one line

Within a fixed 240 s-per-measurement budget, does a different **query policy**,
or an **incremental cardinality encoding with solver-state reuse**, produce more
**independently certified information** than the continuation's baseline?

**The query policy: yes, decisively.** On the four hard measurements the
baseline certifies *nothing* and the policy change certifies a total interval
narrowing of **37**. **The incremental encoding: no clear advantage on the
primary metric** (38 vs 37), though it is consistently **20–35 % faster**.
Neither produced an exact answer on any hard measurement, and the specific
boundary query that blocked them before still blocks them.

---

## 2. Baseline, re-established from artifacts

All 9 experimental units were re-verified from their own stored evidence, not
from the journal's word (`src/baseline.py`, `data/baseline.json`):

| check | result |
|---|---|
| formula hash matches the recorded value | **9/9** |
| observed-set hash matches (recovery, not substitution) | **9/9** |
| stored CNF **byte-identical** to a fresh re-encoding of that query | **8/8** applicable |
| lower bound re-checked from its stored witness | **9/9** |
| upper bound re-checked by pinned drat-trim, or arithmetic | **9/9** |

Two things the inventory turned up that matter:

* There are **five** unresolved measurements in the four hard cells, not four.
  The fifth is `n64_a2.5_k1_eqW`, from the original protocol's *uncertified
  secondary* comparison.
* That fifth measurement's journal upper bound of 30 came from an **unchecked**
  UNSAT, so it is **not** inherited as certified. Its certified starting
  interval is `[29, 64]` — the arithmetic bound — not `[29, 30]`.

## 3. Experimental units

| unit | group | certified start | width | carried UNKNOWN | historical exact |
|---|---|---|---|---|---|
| `n64_a2.5_k1_W` … `k4_W` | opt-primary | `[17,32]` | 15 | `{24}` | — |
| `n64_a2.5_k1_eqW` | opt-secondary | `[29,64]` | 35 | `{29}` | — |
| `n64_a2.5_k0_W` | control | `[17,32]` | 15 | — | 26 |
| `n64_a3.5_k1_W` | control | `[17,32]` | 15 | — | 18 |
| `n64_a3.5_k0_W` | control | `[9,16]` | 7 | — | 16 |
| `n64_a4.2_k0_W` | control | `[9,16]` | 7 | — | 9 |

9 units × 3 methods = **27 runs in 3 261 s** (54 min), inside the declared 3 h
cap. Controls start from a non-exact historical checkpoint chosen by rule
R-START; their historical exact answers were held outside the search state.

## 4. Validation before timing — 26/26

| suite | result |
|---|---|
| `test_encoding.py` — exhaustive projected meaning of the AtMost encoding at every radius endpoint, literal orientation, auxiliary-id uniqueness, agreement with the original seqcounter | **6/6** |
| `test_policy.py` — policy P equals baseline bisection on all 2 080 intervals, determinism, tie-breaks, termination under an adversary, no retries | **7/7** |
| `test_incremental.py` — static vs incremental on radii ascending *and* descending, assumption-leakage, known SAT/UNSAT, brute-force agreement on 9 published instances, negative controls, restart isolation | **13/13** |

Three defects were caught by this suite rather than by the benchmark:

1. **Policy P's midpoint was wrong.** The lower midpoint equals bisection only
   on odd-width intervals, so B would have diverged from A with no UNKNOWN
   involved and confounded the entire comparison. Replaced by the upper
   midpoint, which provably equals `(lo+hi)//2` on every interval — making
   **B identical to A until the first UNKNOWN** by construction.
2. A `kind` key collision between the query record and the journal record,
   which would have crashed the benchmark on its first write.
3. The `_eqW` starting interval, as described in §2.

## 5. Results

### 5.1 The four hard measurements (opt-primary)

Certified intervals; failures shown alongside successes.

| unit | A | B | C |
|---|---|---|---|
| `k1_W` | `[17,32]` · 0 | `[23,32]` · **6** | `[24,32]` · **7** |
| `k2_W` | `[17,32]` · 0 | `[23,30]` · **8** | `[24,30]` · **9** |
| `k3_W` | `[17,32]` · 0 | `[23,28]` · **10** | `[21,28]` · **8** |
| `k4_W` | `[17,32]` · 0 | `[24,26]` · **13** | `[24,25]` · **14** |
| **total width reduction** | **0** | **37** | **38** |
| exact answers | 0 | 0 | 0 |
| SAT / certified-UNSAT / unchecked-UNSAT / UNKNOWN | 0/0/0/**4** | 9/4/0/10 | 10/5/**1**/7 |
| wall clock | 253 s | 963 s | 962 s |

**Method A certifies nothing on any of the four.** It bisects to r=24, is
interrupted at 60 s, and stops — reproducing the original outcome exactly, at a
cost of ~60 s per measurement for zero information.

**B and C both narrow all four.** The gain is overwhelmingly on the **lower**
bound: 9 and 10 validated witnesses respectively, against 4 and 5 certified
upper bounds. `k1_W`'s upper bound never moved off 32 under either method.

**The hard boundary query was not removed, as the brief warned not to assume.**
Under C, `k4_W` narrowed to `[24,25]` and then stopped with *"no useful
unattempted radius"*: the only radius that could close it is 24, the very query
that was retired for timing out. Three of the four hard units ended on
*"budget"*, with 7–10 UNKNOWN queries between them. Incremental solving changed
how much could be certified around the obstacle; it did not dissolve the
obstacle.

### 5.2 The uncertified-secondary measurement (opt-secondary)

| | A | B | C |
|---|---|---|---|
| `n64_a2.5_k1_eqW` | `[29,30]` · 34 | `[29,30]` · 34 | `[29,30]` · 34 |
| certified UNSATs | 5 | 6 | 6 |
| wall clock | 241 s | 224 s | **155 s** |

All three reach the same certified interval. The substance here is **not** a
narrowing beyond what was known: the original run already *reported* `[29,30]`.
What changed is that the upper bound of 30 is now **independently checked**
rather than solver-reported. C was **31 % faster** than B on this
UNSAT-dominated run despite paying 42 s of certification reruns, because its
persistent solver avoids re-bootstrapping an 82 k-clause formula six times and
its standalone CNF is smaller (78.8 k clauses / 14.3 k vars vs 82 k / 41 k),
making proof checking cheaper too (56 s vs 114 s).

### 5.3 Controls

| unit | historical | A | B | C |
|---|---|---|---|---|
| `n64_a2.5_k0_W` | 26 | `[26,26]` 117 s | `[26,26]` 128 s | `[26,26]` **80 s** |
| `n64_a3.5_k1_W` | 18 | `[18,18]` 40 s | `[18,18]` 41 s | `[18,18]` **35 s** |
| `n64_a3.5_k0_W` | 16 | `[16,16]` 2.0 s | `[16,16]` 1.9 s | `[16,16]` 2.1 s |
| `n64_a4.2_k0_W` | 9 | `[9,9]` 2.8 s | `[9,9]` 2.8 s | `[9,9]` 5.0 s |
| **exact / 4** | | **4** | **4** | **4** |
| total reduction | | 44 | 44 | 44 |
| wall clock | | 162 s | 173 s | **123 s** |

**All 12 control runs reproduce the historical exact answer; 0 inconsistencies.**
A and B made **identical query counts** (6 SAT, 8 certified UNSAT) on the
controls, as the design requires — with no UNKNOWN there is nothing for the
policy change to do, and the 6 % wall-clock spread between them is run-to-run
noise, not a method effect.

### 5.4 Encoding size, proof size, memory, storage

| | A / B (seqcounter, rebuilt per radius) | C (ITotalizer, built once) |
|---|---|---|
| clauses (max) | 186 k – 307 k | 337 k – 353 k |
| variables (max) | 95 k – 153 k | **54 k – 56 k** |
| peak RSS | 98 – 169 MB | 154 – **259 MB** |
| largest proof | 355 k lines / 19.3 MB | 296 k lines / **26.9 MB** |

C trades **~10 % more clauses for ~2.7× fewer variables**, and builds its
encoding once (0.1–1.6 s) instead of per radius. It pays for this in memory,
peaking 1.5× higher. Artifact storage for the whole benchmark: **583 MB**.

### 5.5 Budget enforcement

0 hard kills, 0 alarms. **4 of 27 runs overshot** the 240 s budget, by 1.2 s to
6.8 s (0.5 %–2.8 %): A once, B twice, C once. The cause is structural and worth
recording — the per-invocation 60 s timer can start just before the measurement
deadline, so a run can exceed it by up to one invocation's grace. Recorded, not
hidden.

---

## 6. Answers

**1. Did any previously unresolved measurement become certified exact?**
**No.** Zero of the four hard measurements reached an exact certified value
under any method. `k4_W` came within one radius (`[24,25]` under C) and stopped
because closing it requires exactly the retired r=24 query.

**2. Which intervals narrowed, and by how much?**
All four hard measurements narrowed under both B and C, none under A. Starting
width 15 each: B → 9, 7, 5, 2 (reductions 6, 8, 10, 13; total **37**); C → 8,
6, 7, 1 (reductions 7, 9, 8, 14; total **38**). The secondary measurement went
from a certified `[29,64]` to a certified `[29,30]` under all three methods
(reduction 34), converting a previously solver-reported bound into a checked
one. Controls: all 4 from width 15/15/7/7 to exact, under all three methods.

**3. What did changing the query policy contribute?**
Essentially all of the gain on the hard set: **37 of 38** units of width
reduction, against the baseline's **0**. The mechanism is exactly the intended
one — the baseline treats one UNKNOWN as terminal, while the policy retires
that radius and keeps querying the remaining ranges. Because policy P is
constructed to equal bisection when nothing is retired, B is identical to A
until the first UNKNOWN, and the controls confirm it (identical query counts).
This is the one change with a clear, large, supported advantage.

**4. What did the incremental method contribute after including certification
costs?** On the **primary** metric, essentially nothing: 38 vs 37 total width
reduction, winning three hard units and losing one, with no extra exact
answers. On **secondary** metrics it is consistently better: 20–35 % less wall
clock on every UNSAT-dominated run (155 s vs 224 s on the secondary unit; 123 s
vs 173 s across controls), 2.7× fewer variables, one encoding build instead of
one per radius. Its certification reruns cost 119 s on the hard set, 42 s on
the secondary unit and 36 s on the controls — all counted against it. Against
that, C produced the benchmark's **only** uncertified UNSAT and consumed the
most memory. **Because C and B differ in encoding *and* state reuse
simultaneously, no part of this is attributable to either component alone.**

**5. Were gains consistent across controls, or concentrated in particular
cases?** Concentrated, and the pattern is interpretable. On controls — where no
UNKNOWN occurs — **all three methods are equivalent on the primary metric**
(4/4 exact, 44 total reduction each); the policy change can only help where the
baseline gets stuck. The entire B-over-A gain is concentrated in the four hard
α=2.5 units. C's speed advantage, by contrast, appears consistently wherever
certified UNSATs dominate (secondary unit and controls) and vanishes on tiny
instances where its build cost is not amortised (`n64_a4.2_k0_W`: 5.0 s vs
2.8 s — C is **slower** there).

**6. Which solver-ordering claims are actually certified?**
Over the **32 instance cells with certified records on both solver sides**
(64 solver measurements; 28 cells exact on both sides): **31 certified
`ε_C > ε_W`**, **1 certified equality** (`n48_a4.2_k1`), **0 certified
`ε_W > ε_C`**, **0 unresolved**. By size: n=32 3/3, n=48 13 of 14 plus the one
equality, n=64 15/15 — including the four unresolved cells, where
`L_C > U_W` holds even with `ε_W` unpinned.

**The decisive caveat.** `|A_W| > |A_C|` in **31 of those 32 cells** (typically
150 vs 40), and a smaller observed set mechanically admits a larger covering
radius, so the certified ordering is confounded with set size nearly
everywhere. Exactly **one** cell has the confound absent (`n64_a4.2_k3`, 29 vs
30) and still shows certified `C > W`. The comparison designed to remove the
confound — equal-distinct-size — has **zero certified data**, because the
original protocol ran it with proofs disabled. Separately, **28** satisfiable
n=24/n=32 instances are excluded entirely because the original pilot certified
only the W side. No coverage fraction is computed (that needs `|S_I|`), and no
general solver ranking is inferred from this pilot.

**7. Is there enough evidence to select a method for a fresh preregistered
study, or should the baseline remain?**
**Adopt the query policy; retain the baseline encoding.** The policy change has
a clear, large, supported advantage on the primary metric and provably cannot
hurt (it reduces to the baseline when nothing is retired) — it should be the
default. The incremental encoding does **not** have a clear advantage on
certified information (38 vs 37 across four measurements, one of them a loss),
which is the stated success criterion; its real benefit is wall clock, which
the protocol classifies as secondary. Four measurements is also far too small a
basis for an encoding decision. A fresh study should therefore use the baseline
encoding with the improved policy, and — if encoding is to be revisited —
evaluate it on a properly powered cohort with the per-query timeout raised,
since **the binding constraint is now a single hard SAT query, not
certification**.

---

## 7. What this does not show

The four hard cases are an **optimization set, not a held-out scientific
sample**; nothing measured on them is evidence about the population of
instances. Nine measurements and three methods cannot settle an encoding
question. No claim is made that the mathematical approach is limited: the
failure to reach exactness on the hard set is a *budget and solver* limit at
one radius, demonstrated by the fact that `k4_W` reached width 1. Proof
checking was never the bottleneck in this stage.
