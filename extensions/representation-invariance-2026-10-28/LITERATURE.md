# Literature comparison, claim by claim

Written **before** assigning novelty to anything in this note. Each row states a
claim, the closest prior art found, and what — if anything — is left.

Sources were read from their own PDFs, not from abstracts. The 1985 survey's
text layer is OCR (it renders "GÉRARD" as "GBRARD"), so the quoted sentence was
checked against its surrounding paragraph on page 3 of the PDF; it is quoted
verbatim below.

---

## 1. The additive-`p` inequality is classical

> **Cohen, Karpovsky, Mattson, Schatz**, *Covering Radius — Survey and Recent
> Results*, IEEE Transactions on Information Theory **IT-31**(3), May 1985,
> pp. 328 ff. **Corollary 1** (p. 330, following Lemma 1):
>
> "Appending an overall parity check or the zero parity check increases the
> covering radius by one (cf. [2]). **Puncturing a code on `p` coordinates
> reduces the covering radius by at most `p`.**"

This is the same additive-`p` phenomenon as Theorem D, read in the opposite
direction (puncturing rather than extending). **The inequality is not new, and
is not claimed as new.**

Hypothesis comparison, which is the only thing that differs:

| | Cohen et al. 1985, Cor. 1 | Theorem D here |
|---|---|---|
| object | a code `C ⊆ F₂ⁿ` | an observed sample `A ⊆ S_F` |
| radius | `t(C) = max{wt(y + C) : y ∈ F₂ⁿ}` — maximum over the **whole** Hamming space | `ε(A,S_F) = max_{x ∈ S_F} min_{a ∈ A} d_H(x,a)` — maximum over a **proper subset** |
| ambient set under the map | `F₂ⁿ → F₂^{n−p}` unconditionally | **coupled** to the extension by hypothesis (H1), `π(S_G) = S_F` |
| sample under the map | the code maps as a set | separate hypothesis (H2), `π(A') = A` |
| direction | puncture by `p`, radius drops by `≤ p` | extend by `p`, radius rises by `≤ p` |

Theorem D **specialises to** the classical statement when `S_F = {0,1}ⁿ` and
`A = C`. It does not follow from it, because the classical statement has no
subset `S` and no coupling, but the proof is the classical two-line argument and
carries over verbatim once (H1) and (H2) are stated. **Verdict: classical
inequality, solution-relative restatement.** The repository's own
`docs/SOURCE_OF_TRUTH.md` row A1 already labels the underlying Hausdorff
identity "standard metric fact / interpretation, not new", and this is the same
posture one step further.

## 2. The original/auxiliary variable distinction is established, and already certified

> **Bryant, Tan, Heule**, *Certifying Projected Knowledge Compilation*,
> Proc. SAT 2025, LIPIcs vol. 341, paper 8.

Their setting partitions the variables into **data variables** `D` and
**quantified variables** `Y`, compiles `∃Y. φ(D,Y)`, and certifies that the
compiler's output "is logically equivalent to the quantified input formula",
with the soundness argument formally validated in HOL4 and checkers in C and in
CakeML. To certify projection they must represent **Skolem assignments** —
"how the quantified variables can be assigned, given an assignment for the data
variables".

Mapping onto this note's hypotheses:

| this note | their counterpart |
|---|---|
| (H1) `π(S_G) = S_F` | projected logical equivalence, the thing their certifier establishes |
| (H2) `π(A') = A` | the Skolem-assignment side: a witness in `Y` for each retained `D`-assignment. Their machinery **constructs** such a lift for a chosen sample; it does **not** certify that an arbitrary recorded `A'` projects onto `A` |
| extension multiplicity `mult(x)` | exactly why auxiliary variables "increase the number of solutions and should not be counted" |

So **neither projection hypothesis is novel**. (H1) is precisely what their
certifier establishes, with machine-checked soundness in a stronger setting than
anything here. For (H2) the attribution needs narrowing: their Skolem
assignments give a *construction* of a lift for a chosen sample, which covers
every lift used in this note, but they do not certify (H2) for an arbitrary
recorded sample. When the sample is a solver's recorded output, (H2) is an
assumption about the recording procedure. Note that (H2) is a set equality and
is **not** broken by `π` failing to be injective on `A'` — `A' = {(0,0),(0,1)}`
over `A = {0}` satisfies it — so the non-injectivity issue of `NOTE.md` §5 is a
separate matter, about distinct-sample counts and sampling weights.

What that literature does **not** contain, as far as this search found: any
metric or geometric quantity on the projected solution set. A full-text search of
the SAT 2025 paper for *Hamming*, *distance*, *covering radius*, *diameter* and
*metric* returns **no occurrence**. Projected counting cares about `|S_F|`, not
about how `S_F` is spread out.

## 3. Claim-by-claim verdict

| claim | prior art | verdict |
|---|---|---|
| `ε_x` invariant under solution-preserving extension (Lemma 1) | projected equivalence (§2); the Hausdorff identity (repo A1) | **not novel**; a restatement in metric language of the standard projection fact |
| `ε ≤ ε_full ≤ ε + p`, both bounds attained (Theorem D) | Cohen et al. 1985 Cor. 1 (§1) | **inequality classical**; solution-relative form with (H1)/(H2) is a restatement, not a new theorem |
| the margin threshold for **comparisons**: guaranteed at `M ≥ p+1`, guarantee void at `M ≤ p`, each regime witnessed | none found in either literature | **plausibly new, and elementary** — a corollary nobody appears to have needed, because neither field compares two observed samples by covering radius |
| the five preservation controls (isometry, duplicate variable, free padding, varying multiplicity, apparent-geometry change) | each individually standard | **not novel**; their value is as a checklist for this measurement |
| margin distribution of the repository's certified comparisons | — | **new as evidence**, because it is about this repository's own data |
| ETH radius-query interface cost `|A|·r` rows, `D ≤ 2n/r`, admissible `|A| = Θ(n/(log n)²)` | the ETH paper's Def. 2.1; no prior analysis of this query family | **new as a scoped feasibility calculation**, contingent on a theorem this note does not verify |
| the narrow ERV restatement (constraint-count observables, `rank = O(log n)`) | the ERV paper itself | **a correction to its scope**, not a new result |
| trivial `Aut(φ)` with a genuine complementation symmetry | symmetry breaking in SAT routinely uses sign flips as well as permutations | **not novel in substance**; it is a counterexample to one reading of the rigidity paper's `ρ = 0` |

## 4. So what does the combination add?

Stated plainly, because the honest answer is narrow:

**Not** a new inequality, **not** a new treatment of auxiliary variables, and
**not** a new algorithm or bound. What survives is an **application**: a
robustness criterion for certified covering-radius comparisons, together with
the measured margin distribution that says which of this repository's certified
comparisons carry a nonzero guarantee under it. The classical ingredients were
available; the combination of solution-relative resolution, certified margins and
this repository's experimental record is what makes the criterion checkable on
real measurements.

A useful application can survive a classical underlying inequality. It should
not be presented as a theorem contribution, and the framing below does not.

## 5. Not searched, and therefore not claimed either way

* Whether the comparison-margin corollary appears in the covering-code
  literature on *code comparison* or in the discrepancy/Hausdorff-stability
  literature. One search round was performed; a negative result after one round
  is weak evidence.
* Whether any projected-counting work bounds a metric quantity under projection
  in a paper not retrieved by the queries used.
* Priority of the four local papers relative to anything above. No priority
  claim is made, and PDF-internal dates are not treated as evidence.

Queries used: "Cohen Lobstein Sloane covering radius survey puncturing deleting
coordinates decreases covering radius by at most"; "projected model counting
auxiliary variables certified projection SAT 2024 2025". Retrieved and read:
the 1985 survey PDF and the SAT 2025 paper PDF.
