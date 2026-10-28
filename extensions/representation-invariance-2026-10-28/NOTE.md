# Certified SAT solution coverage: representation invariance, auxiliary-variable sensitivity, and robust comparison margins

2026-10-28. Companion to the certified-resolution studies in
`extensions/certified-resolution-2026-10-27/` and
`extensions/solver-budget-selection-pilot-2026-10-27/`.

This note is an **application**, not a theorem contribution. Its central
inequality is classical (§3), and the original/auxiliary variable distinction it
relies on is established and already machine-certified elsewhere (§2). What it
adds is a checkable robustness criterion for the certified comparisons this
repository already records, and the measured distribution of that criterion over
them. `LITERATURE.md` gives the claim-by-claim comparison that this framing
rests on.

---

## 1. Summary

Covering-radius resolution `ε̂` is a function of the solution set. When a formula
is re-encoded with auxiliary variables, two things can be asked, and they have
different answers:

* **measured on the original variables**, `ε̂` is *exactly* unchanged (§2);
* **measured on all variables including the auxiliary ones**, it can move, by at
  most the number of auxiliary variables, and that bound is attained (§3).

For a *comparison* of two observed samples, the consequence is a margin
criterion (§4): a certified strict margin `M` is guaranteed against every
solution-preserving re-encoding that adds at most `M − 1` auxiliary variables,
and above that the guarantee is void. Applied to this repository's certified
comparisons (§6), **43 of 116 carry no nonzero-`p` guarantee** — 28 because
their margin is exactly 1, and 15 because their margin is only bounded below by
1 and is otherwise unresolved. Those are different situations and §6 keeps them
apart: for the 28 the criterion also says some extension ties them, while for
the 15 it says nothing beyond the absence of a guarantee.

**No result in this repository changes.** `ε̂` here is computed on the original
variables, which is the invariant case.

## 2. Setting, and the two hypotheses

`F` is a CNF on `n` variables, `S_F = sat(F) ≠ ∅`, and `A ⊆ S_F` is a nonempty
observed sample. Covering-radius resolution is

    ε(A, S) = max_{x ∈ S} min_{a ∈ A} d_H(x, a).

`G` is a formula on `n + p` variables and `π : {0,1}^{n+p} → {0,1}^n` drops the
auxiliary block. Two hypotheses are used throughout, **both required, neither
implying the other**:

* **(H1) the solution set projects:** `π(S_G) = S_F`;
* **(H2) the observed sample projects:** `π(A') = A` for the lifted sample
  `A' ⊆ S_G`.

Both are standard. (H1) is projected logical equivalence, which is exactly what
projected knowledge compilation certifies — Bryant, Tan and Heule (SAT 2025),
with HOL4-validated soundness. (H2) is the lift side. Their Skolem assignments
*construct* a lift satisfying (H2) for a sample one chooses, which is more than
enough for the constructions used below; they do **not** certify that an
arbitrary *recorded* sample `A'` projects exactly onto `A`. For a recorded
sample, (H2) is an assumption about the recording procedure, and §5 shows it can
fail in a way that matters: `π` need not be injective on `A'`. Stating both
hypotheses explicitly matters here because dropping either breaks everything
below.

**Lemma 1 (invariance on the original coordinates).** Under (H1) and (H2),

    ε_x(A', G) := max_{v ∈ S_G} min_{w ∈ A'} d_H(π v, π w) = ε(A, S_F).

*Proof.* `d_H(π v, π w)` depends on `w` only through `π w`, and `π` maps `A'`
onto `A` by (H2), so the inner minimum equals `min_{a ∈ A} d_H(π v, a)`. By (H1)
the outer maximum ranges over exactly `S_F`. ∎

This is a restatement in metric language of the standard projection fact, and is
not claimed as new.

## 3. Auxiliary-variable sensitivity

**Theorem D.** Under (H1) and (H2), with distances taken on all `n + p`
coordinates,

    ε(A, S_F)  ≤  ε_full(A', G)  ≤  ε(A, S_F) + p,

and both bounds are attained.

*Proof.* `d_H(v,w) = d_H(π v, π w) + d_H(v|aux, w|aux) ≥ d_H(π v, π w)` gives the
lower bound via Lemma 1. For the upper bound fix `v ∈ S_G`, put `x = π v ∈ S_F`,
pick `a*` attaining `min_a d_H(x,a) ≤ ε`, and take `w ∈ A'` with `π w = a*`,
available by (H2); then
`min_{w'} d_H(v,w') ≤ d_H(x,a*) + d_H(v|aux, w|aux) ≤ ε + p`. For attainment take
`G` to be free padding, `S_G = S_F × {0,1}^p`: lifting every `a ∈ A` to every
auxiliary value gives `ε_full = ε`; placing all lifts at one auxiliary value
gives `ε_full = ε + p`. ∎

**The additive-`p` inequality is classical.** Cohen, Karpovsky, Mattson and
Schatz, *Covering Radius — Survey and Recent Results*, IEEE Trans. Inform.
Theory IT-31(3), May 1985, Corollary 1: *"Puncturing a code on `p` coordinates
reduces the covering radius by at most `p`."* There the covering radius is taken
over the whole Hamming space; Theorem D is the solution-relative form, where the
maximum runs over `S_F` and the ambient set is coupled to the extension by (H1).
Theorem D specialises to the classical statement at `S_F = {0,1}^n`, and its
proof is the classical one. `LITERATURE.md` §1 has the full hypothesis table.

## 4. Robust comparison margins

Let `A₁, A₂ ⊆ S_F` be two observed samples with a **certified strict margin**
`M = ε(A₁,S_F) − ε(A₂,S_F) ≥ 1`, and consider any solution-preserving extension
by `p` auxiliary variables with lifts of both samples, measured on all
coordinates.

**Corollary D1.**

* `M ≥ p + 1` ⟹ `ε_full(A₁') > ε_full(A₂')` for **every** such extension and
  lift: the ordering is **guaranteed**.
* `M ≤ p` ⟹ the **guarantee is void**: there **exists** an extension and lift
  that ties it (at `M = p`) or strictly reverses it (at `M ≤ p − 1`).

*Proof.* If `M ≥ p+1` then
`ε_full(A₁') ≥ ε(A₁) = ε(A₂) + M > ε(A₂) + p ≥ ε_full(A₂')`. For the second part,
free padding with `A₂` lifted to one auxiliary value and `A₁` to all gives
`ε_full(A₂') = ε(A₂) + p` and `ε_full(A₁') = ε(A₂) + M` exactly, equal at
`M = p` and reversed for `M < p`. ∎

So `p_max = M − 1` is the largest auxiliary-variable count at which the ordering
is guaranteed.

**The second half is an existence statement, and the distinction matters.**
"The guarantee is void" is *not* "the ordering reverses". Adding auxiliary
variables does not automatically reverse anything: a particular encoding may
leave every certified ordering intact, and in the regime `M ≤ p` the criterion
simply stops certifying either way. An earlier draft of this note said that
small-margin comparisons are "destroyed by a single auxiliary variable". That
was wrong, and the corrected statement is the one above.

## 5. Sharpness and the five controls

Exhaustive verification, exact integers and rationals, in `src/preservation.py`
(13 assertions, all pass).

| control | `ε_x` | `ε_full` | evidence |
|---|---|---|---|
| variable permutation + coordinate complementation | exact | exact | 153 600 (isometry, instance) pairs, 0 discrepancies; `|A|` also preserved |
| **uniquely determined duplicate variable** `z = x₀` | exact, 0/120 pairs move | **moves on 80/120** | adds no solution and no information, yet gives one original coordinate weight 2 |
| free padding of `p` variables | exact | both bounds of Theorem D attained, 360× each | the attainment construction of §3 |
| **`x`-dependent extension multiplicity** | exact | within `[ε, ε+p]` | uniform sampling of `S_G` projects to the multiplicity-weighted law: exact total variation `0` for constant multiplicity, `1/6` for `mult(x) = 1 + [x₀=1]` at `n = 3` |
| apparent-geometry change on a small instance | — | — | full `5`-cube, `ε(A₂)=5`, `ε(A₁)=2`, `M=3`: tie at `p=3`, witness reversal at `p=4` |

The margin regimes are verified exactly as Corollary D1 forces: 3 witness
reversals all at `M ≤ p−1`, 2 witness ties exactly at `M = p`, 5 preservations
all at `M ≥ p+1`.

Two consequences worth stating separately, because they bear on equal-size
comparison rather than on `ε̂`:

* uniform sampling of an *extended* formula is a uniform sample of `S_F` **only**
  when the extension has constant multiplicity;
* `π` need not be injective on `A'`, so an extension can report `|A'|` solutions
  whose projection has fewer distinct members. `ε_x` is unaffected; a
  cardinality-matched comparison is.

## 6. Applied to this repository's certified comparisons

From `extensions/certified-resolution-2026-10-27/data/equal-size/` and
`extensions/solver-budget-selection-pilot-2026-10-27/data/`. **No solver was
run**; these are certified intervals already on disk (`src/diagnostic.py`).

**Exact margins and certified lower bounds are counted separately**, because they
support different halves of Corollary D1. A row with `diff_lo = diff_hi = M`
pins `M`, so both halves apply. A row with `diff_lo = m < diff_hi` certifies only
`M ≥ m`: the **safe** half applies (guaranteed for `p ≤ m−1`) but the void half
does not, since `M` may be larger.

| | equal-size | selection pilot |
|---|---|---|
| rows with a difference interval | 21 | 120 |
| certified strict ordering | 18 | 98 |
|  — exact margin (both halves apply) | **0** | **92** |
|  — lower bound only (safe half only) | **18** | **6** |
| certified tie (`M = 0`) | 3 | 12 |
| interval straddles 0 (no ordering) | 0 | 10 |
| margin range | 1 … 10 | 1 … 19 |

**These are comparisons, not independent instances.** The pilot's 120 rows come
from 18 attempted instances across two budgets, three selection schemes and
nested replicates; the equal-size stage's 21 rows come from 7 instances with 3
nested replicates. Nothing below should be read as 116 independent observations.

Margin distribution, with the two kinds kept apart:

**Exact margins (92).** Both halves of Corollary D1 apply.

| margin `M` | comparisons | guaranteed for | and void for |
|---|---|---|---|
| 1 | **28** | `p = 0` only | some extension with `p ≥ 1` |
| 2–3 | 27 | `p ≤ 1`, `p ≤ 2` | `p ≥ 2`, `p ≥ 3` |
| 4–9 | 17 | `p ≤ 3` … `p ≤ 8` | `p ≥ 4` … `p ≥ 9` |
| ≥ 10 | **20** | up to `p ≤ 18` at `M = 19` | `p ≥ 11` … `p ≥ 19` |

**Certified lower bounds only (24).** The safe half applies; the void half does
**not**, because the actual margin is unresolved.

| certified `M ≥` | comparisons | guaranteed for | void half |
|---|---|---|---|
| 1 | **15** | `p = 0` only | **unavailable** — `diff_hi` reaches 13 |
| 2–3 | 2 | `p ≤ 1`, `p ≤ 2` | unavailable |
| 4–9 | 6 | `p ≤ 3` … `p ≤ 8` | unavailable |
| ≥ 10 | 1 | `p ≤ 9` | unavailable |

For the 15 rows certified only as `M ≥ 1`, the correct statement is that **the
available bounds establish no positive auxiliary-variable tolerance** — and
nothing more. It does *not* follow that one auxiliary variable can tie them:
the widest such interval here is `[1, 13]`, which leaves an actual margin of up
to 13 open. `src/diagnostic.py` carries a regression case over synthetic
intervals so this distinction cannot silently collapse again.

The practical reading is one sentence: **measure Hamming distance on the original
variables only, and report the margin beside the verdict.** This repository
already does the former, so §6 documents an invariance that holds rather than
correcting a defect; the second half is a reporting change.

## 7. The oracle convention, including both boundaries

`Q_r(x) = F(x) ∧ ⋀_{a∈A} d_H(x,a) ≥ r+1`; satisfiable ⟹ `ε ≥ r+1`, unsatisfiable
⟹ `ε ≤ r`. Verified on 3 679 `(A,S)` pairs at `n = 4` against brute force: exact
reconstruction and monotonicity in `r` in every case;

* `r = 0`: `Q₀` is unsatisfiable **iff** `A = S_F` **iff** `ε = 0` — correct at
  the bottom of the ladder, no off-by-one;
* `r = n`: demands distance `≥ n+1` in an `n`-cube, so unsatisfiable
  unconditionally, giving the sound but vacuous `ε ≤ n`. Skippable.

## Appendix A — scope correction for the encoding-relative variance model

Checked in `src/premises.py` (6 assertions covering the eight premise issues examined, all pass), and stated as a correction to
the scope of a local note rather than as a result.

`LINSAT ∈ P` under **both** encodings: on 300 random GF(2) systems the decision
agreed between Gaussian elimination and brute force 300/300, while
`O(E₁) ≠ O(E₂)` on 295/300. So the model varies an **observable**, not a
classification decision.

The closure size is `|Closure(A,b)| = 2^{rank[A \mid b]}` — the **augmented**
rank, since the closure is spanned by whole equations including their
right-hand sides. Verified on 200 systems with 0 mismatches. `2^{rank(A)}` is
wrong in general: the inconsistent pair `x = 0`, `x = 1` has `|Closure| = 4`
while `2^{rank(A)} = 2`. The two ranks agree exactly on **consistent** systems
(Rouché–Capelli), so adding consistency as a hypothesis is an equivalent
repair; 43 of the 200 systems were consistent and matched `2^{rank(A)}` there,
and all 157 inconsistent ones had `rank[A \mid b] = rank(A) + 1`. Since
`rank[A \mid b] ≤ rank(A) + 1`, the conclusion is unaffected: the closure
encoding is polynomial only on a log-rank family, and full-rank systems give
`2^{n+1}` at worst.

And `|sat(OR)| = 2^k − 1 ≠ 2^{k−1} = |sat(XOR)|` for every `k ≥ 2`, so a GF(2)
result does not transfer to CNF-SAT by renaming.

The surviving narrow statement: *for `LINSAT` restricted to `rank(A) = O(log n)`
there are two polynomial-time encodings and a constraint-count observable `O`
with `sign(∇O(E₁)) = 0 ≠ sign(∇O(E₂))` when `β ≠ 1`; hence any observable that
is a function of the constraint count is encoding-relative.* This bears on
neither the complexity of `LINSAT` nor on observables that are functions of the
solution set — and **`ε̂` is the latter**, by Lemma 1. The encoding dependence in
§3 is a different mechanism: which coordinates the metric is taken over.

Separately, a reading of the companion rigidity note needs narrowing: its
`Aut(φ)` is **variable permutations only**, and a 4-variable witness CNF
`[(-4,1), (-4,1,3), (-2,-1,4), (-1,4)]` has `|Aut(φ)| = 1` — so zero quotient
reduction, `ρ = 0`, symmetry-breaking efficiency undefined — while its
8-element solution set is closed under global complementation, a fixed-point-free
involution. `ρ = 0` therefore rules out the measured permutation benefit, not
every representation-based algorithm. The observation that random 3-SAT has
`|Aut(φ)| = 1` is untouched.

## Appendix B — feasibility of the ETH shared-summary interface (scoped)

**Scope.** This appendix takes the construction of an OpenAI preprint titled
*ETH is False* (Theorem 1.1: deterministic exact `#F` for fixed `k ≥ 2` in
`(n+m)^{O_k(1)} 2^{O_k(n log log n/√log n)}` bit operations, and
`2^{O_{k,D}(n/√log n)}` when `m ≤ Dn`) and asks only whether its Definition 2.1
design can be applied to the radius-query family. **The paper's theorem is not
verified here, its algorithm was not implemented, and no claim is made about its
correctness or about anything that would follow from it** — in particular no
complexity-class or circuit-size claim. The paper itself notes that its §6.4
rational interpolation gives the weaker exponent
`ρ(n) = n(log log n)²/√log n = n/(log n)^{1/2+o(1)}`.

**The interface exists.** Taking the measurement rows to be partial Hamming
weights `Σ_{i∈S_g}(x_i ⊕ a_i)` makes every distance constraint
`Σ_g y_{g,a} ≥ r+1` a function of the measurements alone, satisfying
Definition 2.1(4) for those constraints, at `|A|·r` rows with coefficient
absolute sum `D ≤ 2n/r`. The base-2 exponent is

    E(n, |A|, r) = |A|·r·log₂(4n/r + 1) + 2n/r.

**The rows are additive, not shared.** Definition 2.1(3) caps the *total* row
count, and partial Hamming weights do not determine individual variables, so
they cannot also serve as the rows that make an original `k`-clause factor
across groups. The `|A|·r` rows are therefore spent on top of whatever the
paper's own design spends.

**It is unavailable in the measured regime.** Optimising over `r ≥ 3`:

| bar | `n = 64` | `n = 10⁴` | `n = 10⁶` | crossover for `|A| = 40` |
|---|---|---|---|---|
| `E < n` (beat exhaustive search) | max `|A| = 1` | 94 | 6 271 | `n ≥ 3 807` (**59×** the measured `n`) |
| `E < n/√(log₂ n)` (keep the paper's saving) | max `|A| = 0` | 8 | 353 | `n ≥ 72 932` (**1 140×**) |

Admissible `|A| = Θ(n/(log₂ n)²)`, constant stable at `0.134–0.140` over
`n = 10⁶…10¹²`. Caveats: the paper's `O_k` constants are unspecified, so the
second bar is a best case for it, and the paper uses natural logarithms while
the table uses `log₂`, making that bar about `1.2×` tighter than its own form.
Neither changes an order of magnitude.

**Conclusion of the appendix.** Even granting the paper's theorem, the best this
interface could buy is replacing a `2^n`-time certified query with a
`2^{n/√log n}`-time one, at variable counts at least 1 140× the measured regime.
A subexponential exponent is not a polynomial one.

## What is not claimed

* **No new inequality.** The additive-`p` bound is Cohen et al. 1985 Cor. 1
  (`LITERATURE.md` §1). Lemma 1 restates a standard projection fact.
* **No novelty in the projection hypotheses.** (H1) and (H2) are established and
  already machine-certified by Bryant–Tan–Heule (SAT 2025).
* **No new SAT algorithm and no complexity lower bound.** This investigation
  establishes no computational improvement, and nothing here is a lower bound.
  A P-versus-NP framing would outrun the evidence entirely. Note that Lemma 1
  does **not** imply re-encoding cannot help: preserving the answer and
  reducing the cost of computing it are compatible, and a representation-based
  speedup is not excluded by anything here — it is simply not demonstrated.
* **No claim that any certified repository result is wrong or changes.** `ε̂` is
  measured on the original variables, where Lemma 1 gives exact invariance.
* **No claim that a particular re-encoding reverses any ordering** (§4).
* **No solver ranking**, and none used. The cross-solver predictive-transfer
  claim remains retracted (`docs/SOURCE_OF_TRUTH.md` C1) and no portfolio
  superiority is claimed (C7).
* **No priority claim** from any date printed in any PDF.
* **Nothing excluded from a denominator.** The 10 straddling pilot rows, the 15
  certified ties, the 24 ineligible pilot cells and the 10 unresolved
  optimization comparisons are all reported as what they are. `UNKNOWN` stays
  unresolved.

## Reproduction

```
src/preservation.py     13 checks  Lemma 1, Theorem D, Corollary D1, 5 controls, oracle ladder
src/premises.py          9 checks  Appendix A, incl. the inconsistent-system regression
src/interface.py         3 checks  Appendix B
src/diagnostic.py        5 checks  §6, reads certified intervals only; incl. the
                                   uncertain-margin regression
```

Each script is self-contained, exits nonzero on any failure, and needs only a
CPython interpreter — no SAT solver, no network, no dependency cache. Total
runtime **23.8 s** over 30 assertions, **0 solver calls**. `src/diagnostic.py` resolves the
certified data from its own location, so the set reproduces from a clean
checkout at any path. `MANIFEST.md` carries the hashes, the claims ledger, the
costs and the list of corrections incorporated.

## Remaining experimental uncertainty

Unchanged by this note, and the reason a further study is not started here:
equal wall-clock time does not equalise algorithmic work (pure-Python WalkSAT
versus compiled Glucose3), the selection scheme drives the ordering as much as
the solver does, and instances were not independently selected. Whether a
matched-effort study with independently selected instances is worthwhile should
follow from `LITERATURE.md` and the corrected evidence above, not automatically.
