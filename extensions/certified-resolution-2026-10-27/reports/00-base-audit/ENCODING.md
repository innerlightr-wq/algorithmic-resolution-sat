# The reduction, its proof, conventions, and auxiliary-variable handling

## 1. Objects

Let `I` be a CNF formula over variables `x_1,…,x_n` and
`S_I = { x ∈ {0,1}^n : I(x) = 1 }`. Let `A ⊆ S_I` be a nonempty finite set of
**distinct** assignments, **frozen** before any query. The target is the paper's
resolution diagnostic

```
ε̂(A, I)  =  max_{x ∈ S_I}  min_{a ∈ A}  d_H(x, a) .
```

This is the one-sided Hausdorff distance from `S_I` to `A`; it is `0` exactly when
`S_I ⊆ A`, and it is at most `n`.

For an integer `r ≥ 0` define

```
Q_r(x)  =  I(x)  ∧  ⋀_{a ∈ A} [ d_H(x, a) ≥ r + 1 ] .
```

## 2. The reduction, proved

> **Proposition.** For every integer `r` with `0 ≤ r ≤ n`,
> `Q_r` is satisfiable **iff** `ε̂(A, I) > r`.

*Proof.* Both directions are immediate once the quantifiers are written out.

(⇒) Suppose `Q_r` has a satisfying assignment `x*`. The first conjunct gives
`I(x*) = 1`, i.e. `x* ∈ S_I`. The remaining conjuncts give `d_H(x*, a) ≥ r+1` for
every `a ∈ A`, hence `min_{a∈A} d_H(x*,a) ≥ r+1`. Since `x* ∈ S_I`, the maximum
over `S_I` is at least this value:
`ε̂(A,I) ≥ min_{a} d_H(x*,a) ≥ r+1 > r`.

(⇐) Suppose `ε̂(A,I) > r`. `S_I` is finite and nonempty (it contains `A`), so the
maximum is attained: there is `x* ∈ S_I` with
`min_{a∈A} d_H(x*,a) = ε̂(A,I) ≥ r+1`. Then `I(x*) = 1` and
`d_H(x*,a) ≥ r+1` for every `a ∈ A`, so `x*` satisfies `Q_r`. ∎

> **Corollary.** `ε̂(A,I) = min { r ∈ {0,…,n} : Q_r is unsatisfiable }`.

*Proof.* Write `U = { r : Q_r unsatisfiable }`. By the Proposition,
`r ∈ U ⟺ ε̂ ≤ r`. So `U = { r : r ≥ ε̂ } ∩ {0,…,n}`, whose minimum is `ε̂`. The
set is nonempty because `ε̂ ≤ n` puts `n ∈ U`. ∎

> **Monotonicity.** If `r ≤ r'` and `Q_r` is unsatisfiable then `Q_{r'}` is
> unsatisfiable.

*Proof.* `d_H(x,a) ≥ r'+1` implies `d_H(x,a) ≥ r+1`, so every model of `Q_{r'}` is a
model of `Q_r`. ∎ This licenses binary search on `r`, which the implementation uses:
`O(log n)` queries instead of `n+1`.

**This is a standard reduction** — a farthest-solution (maximum-distance) query
answered by a sequence of decision queries, the same shape as the textbook
MaxSAT-by-bisection and "solution-diversity" encodings. **No novelty is claimed
for it.** What this audit contributes is a verified implementation, the
certificate discipline of §5, and the measured costs.

## 3. Distance as a cardinality constraint

Fix `a ∈ A` and define, for `i = 1,…,n`, the literal

```
lit(i, a)  =   x_i     if a_i = 0
lit(i, a)  =  ¬x_i     if a_i = 1
```

Then `lit(i,a)` is true under `x` exactly when `x_i ≠ a_i`, so

```
d_H(x, a)  =  Σ_{i=1}^{n} lit(i, a)
```

as a sum of `n` literals over the **original variables only** — no auxiliary
variable ever appears inside a distance expression. The constraint
`d_H(x,a) ≥ r+1` is therefore an `atleast(r+1)` cardinality constraint over those
`n` literals, encoded with Sinz's 2005 sequential counter (`seqcounter`) by
default; `totalizer`, `sortnetwrk` and `mtotalizer` are available and were used as
independent cross-checks of the same answers.

Standard cardinality encodings are **equisatisfiable** in the strong sense needed
here: every model of the original constraint extends to a model of the encoding,
and every model of the encoding restricted to the original variables satisfies the
constraint. So satisfiability is preserved in both directions, and a model of the
encoded `Q_r` projects to a witness over the `n` original variables — which is
exactly what the implementation extracts and what the independent verifier checks.

## 4. Auxiliary variables

Original variables occupy DIMACS ids `1..n`. A single counter `top`, initialised to
`n`, is threaded through the loop over `A`: each cardinality constraint is built
with `top_id = top`, and immediately afterwards `top` is advanced past the largest
id that constraint actually used,

```
top ← max(top, max{ |l| : l a literal of the new clauses }) .
```

Because `top` never decreases and every constraint starts above the previous
maximum, **no auxiliary id is ever shared between two distance constraints**. This
matters: sharing them is not a mild bug but a semantic one, since the counter
variables of constraint `a` would be forced to simultaneously represent the partial
sums of a different constraint `a'`. `tests/test_controls.py` control 8 includes a
deliberately broken encoder that never advances `top`; on a `n = 10` instance with
`|A| = 3` it returns `ε̂ = 1` against the true `5`, and the independent exhaustive
check **refutes** it (counterexample printed).

## 5. Conventions and the edge cases, all handled explicitly

| Case | Convention |
|---|---|
| `r = 0` | `d_H(x,a) ≥ 1` is "at least one literal true", i.e. the single clause `⋁_i lit(i,a)`, which says exactly `x ≠ a`. No auxiliary variables are introduced. `Q_0` unsatisfiable ⟺ `S_I ⊆ A` ⟺ `ε̂ = 0`. |
| `r ≥ n` | `d_H(x,a) ≤ n < r+1` for every `x`, so `Q_r` is unsatisfiable **by arithmetic**. The implementation returns this without building a formula or calling a solver, and labels the upper bound `arithmetic`. |
| `A` empty | `ε̂` is **undefined** — the max is over `S_I` but the inner min is over an empty set. Recorded as the paper's **categorical failure**, never as `0` and never as `n`. |
| `I` unsatisfiable | `S_I = ∅`, so `A ⊆ S_I` forces `A = ∅` and the previous row applies. If a caller supplies a nonempty `A` with an unsatisfiable `I`, the membership check below rejects the input rather than measuring it. |
| `A ⊄ S_I` | Every `a ∈ A` is checked against the original clauses by the independent verifier **before** any query. A violation aborts with a message; nothing is measured. |
| duplicates in `A` | `A` is deduplicated first; the frozen hash is taken of the sorted deduplicated set, so duplicate inputs give an identical hash and an identical radius (control 5). |
| timeout | A solver interrupt returns `UNKNOWN`. It is **never** read as UNSAT. The oracle then reports the interval `[lo, hi]` it actually established. |

## 6. Freezing, and not contaminating the measurement

`A` is deduplicated and hashed (`sha256` of the canonical sorted JSON) **before the
first query**, and the hash is carried into every output row. Witnesses discovered
by the oracle are used only as lower-bound certificates and are **never added to
`A`** — doing so would change `ε̂`, i.e. change the object being measured, and would
make the procedure a coverage-improvement loop rather than a measurement.

## 7. Certificate levels

The implementation distinguishes, and labels separately:

1. **Witness-verified lower bound.** `Q_{k-1}` returned SAT with a model whose
   projection `x*` is checked by `src/verify.py` — plain Boolean evaluation of the
   original clauses plus direct Hamming distances — confirming `x* ∈ S_I` and
   `d_H(x*,a) ≥ k` for all `a ∈ A`, hence `ε̂ ≥ k`. `verify.py` imports neither
   `encode.py` nor any SAT library, so it cannot repeat an encoder bug.
   For `k = 0` no witness is needed; the bound is trivial.
2. **Solver-reported UNSAT upper bound.** `Q_k` reported unsatisfiable, giving
   `ε̂ ≤ k` **on the solver's word**.
3. **Independently checked upper bound**, by either route:
   * *proof-checked* — Glucose3 is run with proof logging, and the emitted DRUP
     proof is verified by `src/drup.py`, a self-contained forward RUP checker
     written for this audit, **against the standalone CNF containing every clause
     of `Q_k`** (original clauses plus all cardinality clauses, with no
     assumptions). Deletion lines are ignored, which is sound: skipping deletions
     only enlarges the accumulated clause set, every accumulated clause is
     inductively implied by the input, and a propagation conflict under a superset
     of implied clauses still witnesses implication by the input. `drup.py` imports
     no SAT library and shares no code with `encode.py`. A tampered proof is
     rejected (demonstrated in the build log).
   * *exhaustively checked* — for `n ≤ 24`, enumeration of `{0,1}^n` confirms that
     no satisfying assignment lies at distance `≥ k+1` from all of `A`. This uses
     neither a solver nor the encoder and is the strongest available check.

**"Certified exact resolution" is used only when level 3 holds** for the upper
bound and level 1 for the lower bound. Level-2-only results are reported as
solver-reported, and intervals are reported as intervals.

## 8. What an exact `ε̂` does *not* give

`ε̂` is a covering radius. It does not determine `|S_I|`, the number of connected
components of `S_I` at any threshold, the full persistence or connectivity
structure, or whether `A` is a uniform sample. None of those is claimed anywhere in
this audit. Exact counting and uniform sampling are recorded in `REPORT.md` as
possible later investigations and were not begun.
