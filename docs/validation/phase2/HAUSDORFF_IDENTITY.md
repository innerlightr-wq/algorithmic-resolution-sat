# HAUSDORFF_IDENTITY.md — Phase 2, Part 2

## 1. Definitions

For nonempty finite subsets `X,Y` of a metric space `(M,d)`, the **directed Hausdorff distance** from `X` to `Y` is
```
\vec d(X,Y) = max_{x∈X} min_{y∈Y} d(x,y),
```
and the **(symmetric) Hausdorff distance** is
```
d_Haus(X,Y) = max( \vec d(X,Y), \vec d(Y,X) ).
```
This is the standard textbook definition (computational geometry / shape-matching literature; confirmed generic and citation-independent — it is a direct consequence of the metric axioms and set-membership, not attributed to any single paper).

## 2. Theorem: `ε̂(A,I) = d_Haus(A(I), S_I)` whenever `∅ ≠ A(I) ⊆ S_I`

**Claim.** For `∅ ≠ A(I) ⊆ S_I ⊆ {0,1}^n`,
```
ε̂(A,I) = max_{x∈S_I} min_{y∈A(I)} d_H(x,y) = d_Haus(A(I), S_I).
```

**Proof.**

Step 1 — identify `ε̂(A,I)` with a directed distance. By definition (paper's Def. 3.3), `ε̂(A,I) = max_{x∈S_I} min_{y∈A(I)} d_H(x,y)`. Comparing to §1's definition of directed Hausdorff distance with the roles `X=S_I`, `Y=A(I)`:
```
ε̂(A,I) = \vec d(S_I, A(I)).
```
This step requires no hypothesis beyond `A(I)` nonempty (so the inner `min` is defined) — it is a direct syntactic match, not yet using `A(I)⊆S_I`.

Step 2 — show the reverse directed distance is exactly zero, using `A(I)⊆S_I`.
```
\vec d(A(I), S_I) = max_{y∈A(I)} min_{x∈S_I} d_H(y,x).
```
Fix any `y∈A(I)`. Since `A(I)⊆S_I`, `y∈S_I` too, so `y` itself is a valid choice of `x` in the inner minimization, giving `min_{x∈S_I} d_H(y,x) ≤ d_H(y,y) = 0`. Since distances are non-negative, `min_{x∈S_I} d_H(y,x) = 0` exactly, for every `y∈A(I)`. Taking the max over `y∈A(I)` (nonempty by hypothesis) gives `\vec d(A(I),S_I) = 0`.

Step 3 — combine. `d_Haus(A(I),S_I) = max(\vec d(A(I),S_I), \vec d(S_I,A(I))) = max(0, ε̂(A,I)) = ε̂(A,I)`, since `ε̂(A,I)≥0` always. ∎

**This is the complete, exact identity, with the single hypothesis `∅≠A(I)⊆S_I` (both parts of which are used: nonemptiness for Step 1's `min` to be defined, and the subset relation for Step 2's zero).**

## 3. The `A(I)=∅` case, handled separately

When `A(I)=∅`, `\vec d(S_I,A(I)) = max_{x∈S_I} min_{y∈∅} d(x,y)` — the inner minimum over an empty set is `+∞` by the standard convention (infimum of the empty set in `[0,∞]`), so the directed distance itself is `+∞` under the usual extended-real convention, **not** the paper's chosen sentinel value `n`. The paper's Definition 3.3 convention `ε̂(A,I)=n` in this case is therefore **not** literally the Hausdorff distance (which would be `+∞`, or undefined if one refuses the extended reals) — it is a separate, finite, bounded *engineering* sentinel, chosen for plotting/statistics convenience.

**Recommendation for V2 (cleanest convention):** keep `ε̂(A,I)` defined *only* on `A(I)≠∅` as the genuine Hausdorff distance (Theorem, §2); for `A(I)=∅`, do **not** report a numeric `ε̂` value at all — record a categorical flag (`"total failure"` / `⊤`) instead. This:
- avoids the false unconditional inequality identified in Phase 1 `AUDIT.md` §2 (Proposition 3.1 broke exactly because `ε̂=n` was substituted into an inequality proved only for `A(I)≠∅`);
- avoids silently misrepresenting `+∞` as a finite number `n`, which understates how bad total failure is (a run that finds nothing is qualitatively different from, and worse than, a run whose furthest miss happens to be at Hamming distance `n`, e.g. the antipodal point — conflating them in a bounded numeric scale erases a real distinction);
- matches how failure is usually handled in comparable measurement contexts (e.g. "instance not solved" flags in SAT-competition-style reporting, kept separate from runtime/quality metrics rather than coded as a worst-case number in the same column).

If a single finite sentinel is still wanted for a specific plot (e.g. to include failed runs on a bounded axis), it should be computed and labeled explicitly as a *plotting convention*, not folded back into the formal definition of `ε̂` used in any proposition or theorem (this is exactly the discipline that would have prevented Proposition 3.1's bug).

## 4. Is the identity novel?

**No — and it should not be presented as novel.** Per instruction, this is not labeled novel here. Hausdorff distance (symmetric and directed) is a decades-old, textbook object in computational geometry and shape/point-set comparison; `ε̂(A,I)` is an unmodified instance of the standard directed-Hausdorff-distance formula, and the collapse to the one-sided term (§2, Step 2–3) is a one-line consequence of `A(I)⊆S_I`, not new mathematics (`PRIOR_ART.md` §2 already established this in Phase 1; this document rederives it independently as instructed and confirms the same conclusion). Classification (per `NOVELTY_CLASSIFICATION.md` scheme): **KNOWN MATHEMATICS**.

## 5. Does "algorithmic resolution" remain useful terminology?

**Yes, as an interpretation layer, not as a claim of a new quantity.** Three considerations:

1. **What the renaming buys**: "Hausdorff distance between `A(I)` and `S_I`" is mathematically precise but domain-opaque; "algorithmic resolution" (or, more precisely, "the scale at which an algorithm's output can be trusted to represent the true solution space") communicates the *interpretation* — that this quantity measures a solver's effective measurement precision — to a SAT/algorithms audience that would not automatically supply that reading from "Hausdorff distance" alone. Domain-specific renaming of a standard quantity to carry an interpretive frame is common, legitimate scientific practice (e.g. "effective sample size," "resolution limit" in imaging, both standard-statistics/-optics quantities under interpretation-carrying names) — it becomes illegitimate only when the renaming is used to *imply* novelty of the underlying math, which is exactly the failure mode `PRIOR_ART.md` flagged and this document must not repeat.
2. **What it costs if mislabeled**: presenting `ε̂` as a newly *introduced measurable geometric quantity* (January Abstract's actual wording) overclaims; a referee who recognizes Hausdorff distance will read this as either naivety or salesmanship. The fix is cheap — state the identity upfront (§2) and *then* motivate the domain-specific name as an interpretive convenience, exactly the ordering recommended in `V2_OUTLINE.md` §2.
3. **Net recommendation**: retain "algorithmic resolution" (or a similar domain-facing term) as V2's working name for `ε̂`, but only ever introduce it *after* the Hausdorff/covering-radius identity is stated and cited as standard — never before. This is a labeling/rhetoric decision, not a mathematical one, and is consistent with `FINAL_VERDICT.md`'s "state plainly... under new terminology" recommendation from Phase 1.

## 6. Status label

Hausdorff identity (§2): **PROVED** (one-line consequence of the definitions, not novel — see §4). `A(I)=∅` convention recommendation (§3): design decision, not a theorem. Terminology recommendation (§5): editorial guidance, not a mathematical claim.
