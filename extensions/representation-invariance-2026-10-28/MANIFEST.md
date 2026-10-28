# Manifest, claims ledger, and costs

Companion to `NOTE.md` and `LITERATURE.md`. 2026-10-28.

## Contents

```
NOTE.md           the contribution
LITERATURE.md     claim-by-claim prior-art comparison, read before assigning novelty
MANIFEST.md       this file: ledger, costs, hashes, corrections
src/preservation.py  13 checks  Lemma 1, Theorem D, Corollary D1, 5 controls, oracle ladder
src/premises.py      10 checks  Appendix A, incl. the inconsistent-system regression
src/interface.py      3 checks  Appendix B
src/diagnostic.py     4 checks  NOTE.md §6; the regression runs over the production classifier
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
| D1 | `M ≥ p+1` ⟹ ordering guaranteed; `M ≤ p` ⟹ some extension ties or reverses it, witnessed | **PROVED**, sharp; not found in either literature (one search round) |
| D2 | a certified interval `M ∈ [ℓ,u]` gives three regimes: preserved for `p ≤ ℓ−1`, unsettled for `ℓ ≤ p ≤ u−1`, void for `p ≥ u`; exact margins are `ℓ = u` | **PROVED**; implemented as the single shared classifier `regimes()` |
| C1 | Hamming isometries preserve `ε`, `ε_full`, `|A|` exactly | **PROVED**; 153 600 pairs, 0 discrepancies |
| C2 | a uniquely determined duplicate variable fixes `ε_x` but moves `ε_full` | **PROVED**; 0/120 move `ε_x`, **80/120** move `ε_full` |
| C3 | uniform sampling of `S_G` projects uniformly **iff** multiplicity is constant | **PROVED**; exact TV `0, 0, 1/6` |
| C4 | `π` need not be injective on `A'`, so `|π(A')| ≤ |A'|`; this affects distinct-sample counts and sampling weights but does **not** violate (H2), which is a set equality — `A' = {(0,0),(0,1)}` over `A = {0}` satisfies it | **PROVED**, by construction |
| O1 | the radius ladder reconstructs `ε` exactly; `Q₀` UNSAT ⟺ `A = S_F` ⟺ `ε = 0`; `Q_n` UNSAT unconditionally | **PROVED**; 3 679 pairs, no exception |
| A1 | `LINSAT ∈ P` under both encodings; decision invariant, `O(E)` not | **PROVED**; 300/300 agreement, 295/300 observable disagreement (closure sized by augmented rank; the headline is 295/300 either way, so it could not have caught the stale sizing — 151/300 systems are inconsistent) |
| A2 | `|Closure(A,b)| = 2^{rank[A\|b]}` — the **augmented** rank; `2^{rank(A)}` holds only on consistent systems | **PROVED**; 200 systems, 0 mismatches; 157 inconsistent, all with `rank[A\|b] = rank(A)+1`; regression case `x=0, x=1` |
| A3 | `|sat(OR)| = 2^k − 1 ≠ 2^{k−1} = |sat(XOR)|` for `k ≥ 2` | **PROVED** |
| A4 | a CNF with `|Aut(φ)| = 1` whose solution set is complement-closed | **PROVED** by witness `[(-4,1), (-4,1,3), (-2,-1,4), (-1,4)]` |
| A5 | one definitional extension leaves the uniform random 3-CNF ensemble | **PROVED**; density `273/64 → 276/65`, width-2 clauses appear |
| B1 | the radius-query interface costs `|A|·r` additive rows with `D ≤ 2n/r`; exponent `E = |A| r log₂(4n/r+1) + 2n/r` | **SCOPED** derivation |
| B2 | admissible `|A| = 1` at `n = 64` (bar `E<n`), `0` under the paper-saving bar; `|A| = 40` needs `n ≥ 3 807` resp. `n ≥ 72 932` | **MEASURED** |
| B3 | admissible `|A| = Θ(n/(log₂ n)²)`, constant `0.134–0.140` | **MEASURED** over `10⁶…10¹²` |
| M1 | 116 certified strict comparisons: **92 exact** (`ℓ = u`; 28 at `M = 1`, 20 at `M ≥ 10`, max 19) and **24 intervals** (`ℓ < u`; 15 with `ℓ = 1`, widest `[1,13]`). Never pooled; both endpoints used per D2 | **MEASURED** |
| M2 | these are comparisons over ≤ 25 instances with replicates nested, not independent observations | **MEASURED** |
| N1 | any new inequality | **NOT ESTABLISHED** — see `LITERATURE.md` |
| N2 | any improvement to computing or certifying `ε̂` | **NOT ESTABLISHED** — this investigation establishes no computational improvement. Note L1 does **not** imply that re-encoding cannot help: preserving the answer and reducing the cost of computing it are compatible |
| N3 | any SAT algorithm, complexity separation, lower bound, or circuit claim | **NOT ESTABLISHED** and not attempted |
| N4 | correctness of the ETH preprint's Theorem 1.1 | **not assessed**; algorithm not implemented |
| N5 | any solver ranking or cross-solver predictive transfer | **retracted upstream** (`docs/SOURCE_OF_TRUTH.md` C1, C7), not revived |
| N6 | publication priority from a PDF-internal date | **NOT ESTABLISHED** |
| N7 | that any certified repository result is wrong or changes | **NOT CLAIMED**; `ε̂` is measured on the original variables, where L1 gives exact invariance |

## Costs

| script | wall time | solver calls |
|---|---|---|
| `src/preservation.py` | 3.9 s | 0 |
| `src/premises.py` | 0.2 s | 0 |
| `src/interface.py` | 20.9 s | 0 |
| `src/diagnostic.py` | 0.0 s | 0 |
| **total** | **25.1 s** (30 assertions) | **0** |

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

### Second review pass (source-and-data review of PR #2 at `db1f2be`)

8. **The margin correction was incomplete in the code.** `src/diagnostic.py`
   separated exact margins from lower bounds in its printout and then **pooled
   them again** before claiming that one auxiliary variable can produce a tie
   in all 43 margin-one comparisons. Recounted independently and confirmed:
   only **28** of those have an exactly certified margin of 1; the other **15**
   are certified only as `M ≥ 1` with the actual margin unresolved, and for
   those the correct statement is that the available bounds establish **no
   positive auxiliary-variable tolerance** — nothing about ties. The widest
   such interval in this repository is `[1, 13]`. The script was rewritten to
   keep the two kinds apart end to end, and a **regression case over synthetic
   intervals** (including `[1, 8]` and `[1, 13]`) now guards the distinction.
9. **The closure check tested the wrong object.** It computed the span of the
   rows of `A`, discarding `b`, and compared it against `2^{rank(A)}`. The
   closure is spanned by whole **equations**, so the identity is
   `|Closure(A,b)| = 2^{rank[A\|b]}`. Minimal counterexample, now a regression
   case: `x = 0`, `x = 1` gives `|Closure| = 4` while `2^{rank(A)} = 2`. The
   two ranks agree exactly on consistent systems (Rouché–Capelli), so assuming
   consistency is an equivalent repair, and both are tested. Since
   `rank[A\|b] ≤ rank(A) + 1`, the log-rank polynomial-size conclusion
   survives.
10. **Invariance does not imply that re-encoding cannot improve computation.**
    Ledger row N2 said Lemma 1 "explains why re-encoding cannot help". That is
    a non-sequitur: preserving the answer and reducing the cost of computing it
    are compatible. Replaced throughout with *this investigation establishes no
    computational improvement*, which leaves the representation-based idea open
    rather than falsely closing it.
11. **Literature attribution narrowed.** Bryant–Tan–Heule certify (H1),
    projected equivalence, with machine-checked soundness. Their Skolem
    assignments **construct** a lift satisfying (H2) for a sample one chooses;
    they do **not** certify that an arbitrary *recorded* sample `A'` projects
    exactly onto `A`. For a recorded sample, (H2) is an assumption about the
    recording procedure — and `NOTE.md` §5 shows it can fail, since `π` need
    not be injective on `A'`. "Certifies exactly our (H1)/(H2) pair" has been
    removed.


### Third review pass (source review of `0f1dadd`)

12. **The margin regression did not test the production path.** The helper it
    exercised was a parallel copy; the CSV report used separate logic, so the
    tests could pass while production classification regressed. There is now a
    single module-level classifier, `regimes()` / `verdict_at()`, called by both
    the report and the 19 regression cases. Writing the cases against production
    immediately caught two **wrong expectations of mine**: at `p = 0` there are
    no auxiliary variables, so a certified ordering is `preserved`, not `void`.
13. **"The void half is unavailable" was too broad.** For an interval
    `M ∈ [ℓ,u]` the upper endpoint is informative: `p ≥ u` gives `M ≤ p`, so
    some allowed extension does tie or reverse the ordering. Hence the
    three-regime Corollary D2, replacing the two-regime account. `[1,13]` gives
    no one-variable tie but does give a void verdict at `p ≥ 13`.
14. **One stale closure calculation remained.** The observable comparison in
    `src/premises.py` still sized the closure by `2^{rank(A)}` after
    `test_closure_size` had been corrected. Now augmented. Confirmed
    independently: **151 of 300** systems are inconsistent and so change size,
    yet the headline disagreement count is **295/300 either way** — a check is
    now asserted on precisely that insensitivity, so the headline can never
    again stand in for the calculation.
15. **Non-injectivity does not violate (H2).** The prose connected them.
    `A' = {(0,0),(0,1)}` with `A = {0}` has `π(A') = A`, so (H2) holds while
    `π` collapses two members. (H2) fails exactly when the projected set omits
    or adds an original assignment. Non-injectivity is a separate matter —
    distinct-sample counts and sampling weights — and the two are now kept
    apart in `NOTE.md` §2, §5 and `LITERATURE.md`.

## Hashes

`MANIFEST.md` is excluded, since it carries the list.

```
e9112ba75a86244bad5e57145551ae44  NOTE.md
8752f32d40bf88560449a3709f2fa648  LITERATURE.md
99f5b06487fcd26f5b61e892c1ee4e67  src/diagnostic.py
fa5dee58f2c6659b8838d15c1cef0932  src/interface.py
e85393d6844e8c1fd1ae4adbbbd665d7  src/premises.py
2916707fa9a70f26e4fb0426b8f041f1  src/preservation.py
9cb0579b3578046274852f408f32b5c3  results/diagnostic.txt
11f0660d27c4c9f5cdf687cf57fb4663  results/interface.txt
0d426747ad10355a07cfed695c00e375  results/premises.txt
75d578583e0e15462cc70e94e4d3a106  results/preservation.txt
```
