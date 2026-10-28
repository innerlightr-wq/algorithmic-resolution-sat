# Manifest, claims ledger, and costs

Companion to `NOTE.md` and `LITERATURE.md`. 2026-10-28.

## Contents

```
NOTE.md           the contribution
LITERATURE.md     claim-by-claim prior-art comparison, read before assigning novelty
MANIFEST.md       this file: ledger, costs, hashes, corrections
src/preservation.py     13 checks  Lemma 1, Theorem D, Corollary D1, 5 controls, oracle ladder
src/premises.py          6 checks  Appendix A
src/interface.py         3 checks  Appendix B
src/diagnostic.py        3 checks  NOTE.md §6, reads certified intervals only
results/*.txt         verbatim output of each
```

Deliberately **not** shipped: third-party PDFs, dependency caches, virtual
environments, SAT proof archives, CNF artifacts. `LITERATURE.md` cites prior art
by full reference instead of redistributing it, and every script runs on a bare
CPython interpreter.

## Claims ledger

Strength: **PROVED** (proof plus exhaustive verification), **MEASURED** (exact,
from data on disk), **CLASSICAL** (established prior art, restated),
**SCOPED** (feasibility calculation contingent on an unverified theorem),
**NOT ESTABLISHED**.

| # | claim | strength |
|---|---|---|
| L1 | under (H1)+(H2), `ε_x(A',G) = ε(A,S_F)` | **CLASSICAL** as a projection fact; PROVED as restated. 600 extension instances, 0 discrepancies |
| D | under (H1)+(H2), `ε ≤ ε_full ≤ ε + p`, both bounds attained | **CLASSICAL** inequality (Cohen–Karpovsky–Mattson–Schatz 1985, Cor. 1); PROVED in solution-relative form. 720 triples, 0 violations; each bound attained 360× |
| D1 | `M ≥ p+1` ⟹ ordering guaranteed; `M ≤ p` ⟹ guarantee void, witnessed | **PROVED**, sharp; not found in either literature (one search round) |
| C1 | Hamming isometries preserve `ε`, `ε_full`, `|A|` exactly | **PROVED**; 153 600 pairs, 0 discrepancies |
| C2 | a uniquely determined duplicate variable fixes `ε_x` but moves `ε_full` | **PROVED**; 0/120 move `ε_x`, **80/120** move `ε_full` |
| C3 | uniform sampling of `S_G` projects uniformly **iff** multiplicity is constant | **PROVED**; exact TV `0, 0, 1/6` |
| C4 | `π` need not be injective on `A'`, so `|π(A')| ≤ |A'|` | **PROVED**, by construction |
| O1 | the radius ladder reconstructs `ε` exactly; `Q₀` UNSAT ⟺ `A = S_F` ⟺ `ε = 0`; `Q_n` UNSAT unconditionally | **PROVED**; 3 679 pairs, no exception |
| A1 | `LINSAT ∈ P` under both encodings; decision invariant, `O(E)` not | **PROVED**; 300/300 agreement, 295/300 observable disagreement |
| A2 | `|Closure(A,b)| = 2^{rank(A)}`, so the closure encoding is polynomial only at `rank = O(log n)` | **PROVED**; 200 systems, 0 mismatches |
| A3 | `|sat(OR)| = 2^k − 1 ≠ 2^{k−1} = |sat(XOR)|` for `k ≥ 2` | **PROVED** |
| A4 | a CNF with `|Aut(φ)| = 1` whose solution set is complement-closed | **PROVED** by witness `[(-4,1), (-4,1,3), (-2,-1,4), (-1,4)]` |
| A5 | one definitional extension leaves the uniform random 3-CNF ensemble | **PROVED**; density `273/64 → 276/65`, width-2 clauses appear |
| B1 | the radius-query interface costs `|A|·r` additive rows with `D ≤ 2n/r`; exponent `E = |A| r log₂(4n/r+1) + 2n/r` | **SCOPED** derivation |
| B2 | admissible `|A| = 1` at `n = 64` (bar `E<n`), `0` under the paper-saving bar; `|A| = 40` needs `n ≥ 3 807` resp. `n ≥ 72 932` | **MEASURED** |
| B3 | admissible `|A| = Θ(n/(log₂ n)²)`, constant `0.134–0.140` | **MEASURED** over `10⁶…10¹²` |
| M1 | 116 certified strict comparisons: 92 exact margins, 24 lower-bound only; 43 at `M = 1`; 21 at `M ≥ 10`; max 19 | **MEASURED** |
| M2 | these are comparisons over ≤ 25 instances with replicates nested, not independent observations | **MEASURED** |
| N1 | any new inequality | **NOT ESTABLISHED** — see `LITERATURE.md` |
| N2 | any improvement to computing or certifying `ε̂` | **NOT ESTABLISHED**; L1 explains why re-encoding cannot help |
| N3 | any SAT algorithm, complexity separation, lower bound, or circuit claim | **NOT ESTABLISHED** and not attempted |
| N4 | correctness of the ETH preprint's Theorem 1.1 | **not assessed**; algorithm not implemented |
| N5 | any solver ranking or cross-solver predictive transfer | **retracted upstream** (`docs/SOURCE_OF_TRUTH.md` C1, C7), not revived |
| N6 | publication priority from a PDF-internal date | **NOT ESTABLISHED** |
| N7 | that any certified repository result is wrong or changes | **NOT CLAIMED**; `ε̂` is measured on the original variables, where L1 gives exact invariance |

## Costs

| script | wall time | solver calls |
|---|---|---|
| `src/preservation.py` | 4.0 s | 0 |
| `src/premises.py` | 0.1 s | 0 |
| `src/interface.py` | 20.1 s | 0 |
| `src/diagnostic.py` | 0.0 s | 0 |
| **total** | **24.2 s** | **0** |

No SAT solver was invoked, no network access is required, no instance was added,
and `n` was not increased beyond the measured `n ≤ 64`. Nothing was excluded
from a denominator: the 10 straddling pilot rows, 15 certified ties, 24
ineligible pilot cells and 10 unresolved optimization comparisons are all
reported as what they are.

## Corrections incorporated

Each was an error of mine, corrected in place with the refutation recorded
rather than the claim widened.

1. **Margin language** (external review). An earlier draft said small-margin
   comparisons are "destroyed by a single auxiliary variable". Wrong twice: the
   second half of Corollary D1 is an **existence** statement — at `M ≤ p` the
   *guarantee is void*, which is not the same as the ordering being reversed,
   and adding auxiliary variables does not automatically reverse anything; and
   it applies only when distances are measured on all coordinates, whereas this
   repository measures on the original variables.
2. **Exact gaps versus certified lower bounds** (external review, and a filter
   bug of mine). The first diagnostic counted only singleton difference
   intervals, discarding 18 of the 21 equal-size rows, then asserted that every
   certified margin is a singleton — false. A row with `diff_lo = m < diff_hi`
   certifies only `M ≥ m` and supports the safe half of the threshold only. The
   two kinds are now counted separately and never pooled.
3. **Comparisons versus independent instances** (external review). 116 is a
   count of measurements over ≤ 25 instances with budgets, schemes and
   replicates nested; it is never presented as 116 observations.
4. **Both hypotheses stated** (external review). (H1) `π(S_G) = S_F` and
   (H2) `π(A') = A` are now separate, named, and used explicitly.
5. **Novelty** (external review). Prior art was searched before novelty was
   assigned; the additive-`p` inequality turned out to be classical and the
   projection hypotheses already machine-certified. `LITERATURE.md` records the
   comparison and the framing was changed from a theorem contribution to an
   application.
6. **ETH interface constants** (my predictions, refuted by the computation).
   `max |A|` at `n = 64` is **1**, not 0; the crossovers are **59×** and
   **1 140×** the measured `n`, not "two and four orders of magnitude"; and the
   asymptotic is `n/(log n)²`, not `(log n)^{3/2}` — the `3/2` fit drifted
   (`0.063 → 0.042`) where exponent 2 is stable (`0.134–0.140`).
7. **Path independence.** `src/diagnostic.py` originally hard-coded absolute
   paths; it now resolves the certified data from its own location, so it
   reproduces from a clean checkout at any path, and fails loudly if the data
   is absent.

## Hashes

`MANIFEST.md` is excluded, since it carries the list.

```
c237f34fb45b761ba225640ed9475ad7  NOTE.md
b944fd705be6f25f9bad6336c5e9ff07  LITERATURE.md
39c166f9536d885780b2e59fdc6bc669  src/diagnostic.py
fa5dee58f2c6659b8838d15c1cef0932  src/interface.py
7ddd89e8d7abe991608d14d49323cec1  src/premises.py
2916707fa9a70f26e4fb0426b8f041f1  src/preservation.py
ba6617876f4ceb1c065efc2fab445004  results/diagnostic.txt
11f0660d27c4c9f5cdf687cf57fb4663  results/interface.txt
f242d8955cbbcaa7c8a09073973fa44a  results/premises.txt
75d578583e0e15462cc70e94e4d3a106  results/preservation.txt
```
