# AUDIT.md — Theorem-by-theorem mathematical audit
Paper: "Algorithmic Resolution and Geometric Distinguishability in SAT Solution Spaces," Elias De Jesus, January 2026 (`~/Downloads/GeometricResolution.pdf`, unmodified, 9 pp.)

Audit performed independently — the diagnosis in the task prompt was verified from scratch, not assumed.

---

## 1. Theorem 2.1 (Geometric Distinguishability Threshold) — **FALSE AS STATED**

> Claim: In any metric space `(X,d)`, for `x,y` with `d(x,y)=D>0`, `B_ε(x) ∩ B_ε(y) = ∅ ⟺ ε < D/2`.

### 1.1 Independent verification of the counterexample

Take `X = {0,1}^n`, `d = d_H` (Hamming), `x,y` with `d_H(x,y) = D = 1`, and `ε = 1`.

- `B_1(x) = {z : d_H(x,z) < 1}`. Since Hamming distance is integer-valued, `d_H(x,z)<1 ⟺ d_H(x,z)=0 ⟺ z=x`. So `B_1(x) = {x}`.
- Likewise `B_1(y) = {y}`.
- `{x} ∩ {y} = ∅` since `x ≠ y`. **So `x,y` ARE distinguishable at `ε=1`.**
- The theorem asserts distinguishability `⟺ ε < D/2 = 0.5`. Here `ε=1 ⊀ 0.5`, so the theorem predicts `x,y` should be **indistinguishable** at `ε=1`.
- Direct contradiction. Theorem 2.1 is false for the discrete Hamming cube, confirmed independently.

### 1.2 Exactly which implication fails, and why

The proof has two directions:

- **(⇐) `ε < D/2 ⟹ disjoint`.** Proof: `z ∈ B_ε(x) ⟹ d(x,z)<ε<D/2`; triangle inequality gives `d(y,z) ≥ d(x,y) - d(x,z) > D - D/2 = D/2 > ε`, so `z ∉ B_ε(y)`. **This direction is a correct, fully general consequence of the triangle inequality. It holds in every metric space, including the Hamming cube, with no extra hypotheses.**

- **(⇒) `disjoint ⟹ ε < D/2`.** Proof as written: "If `ε ≥ D/2`, let `m` be any point with `d(x,m) ≤ D/2` and `d(y,m) ≤ D/2` (such a point exists on any geodesic between `x` and `y`, or by the intermediate value theorem in connected spaces)." **This is exactly where the proof breaks.** It silently assumes `X` is a *geodesic* (or at least midpoint-convex / connected-with-IVT) metric space, in which an exact midpoint `m` with `d(x,m)=d(y,m)=D/2` is guaranteed to exist. `({0,1}^n, d_H)` is a discrete, totally disconnected space in the usual topology — there is no intermediate value theorem, and when `D` is odd, `D/2` is not even an integer, so **no point of `{0,1}^n` can be at distance exactly `D/2` from `x`** (all Hamming distances are integers). The cited existence of `m` fails, and the implication fails with it.

  Contrapositive check with the counterexample: `ε=1 ≥ D/2=0.5`, and the proof's claimed `m` would need `d(x,m)≤0.5` and `d(y,m)≤0.5`, forcing `m=x` and `m=y` simultaneously (only integer distance ≤0.5 is 0) — impossible since `x≠y`. No such `m` exists, so the proof template cannot even produce its contradiction; the theorem's forward direction was never actually established for this space.

### 1.3 What additional assumption repairs the (⇒) direction

The needed hypothesis is exactly that **`X` is a midpoint metric space** (equivalently, by the Hopf–Rinow-type characterization for complete spaces, a **geodesic / length space**): for every `x,y ∈ X` there exists `m ∈ X` with `d(x,m) = d(y,m) = d(x,y)/2`.

- If `X` is midpoint-convex, the (⇒) proof goes through verbatim: suppose disjoint and `ε ≥ D/2`; the guaranteed midpoint `m` satisfies `d(x,m)=d(y,m)=D/2 ≤ ε`... care is needed with strict vs. non-strict inequality (open balls need `d(x,m)<ε`, and `D/2 ≤ ε` with `m` at exactly `D/2` only lands in `B_ε(x)` when `ε>D/2` strictly, or needs `≤` closed balls). Stated carefully: **for open balls, `B_ε(x)∩B_ε(y)=∅` for all `ε ≤ D/2`, and midpoint convexity is exactly what forces the balls to first meet at `ε` immediately above `D/2`.** The correct clean biconditional in a midpoint space is:
  `B_ε(x) ∩ B_ε(y) ≠ ∅ ⟺ ε > D/2`, i.e. `B_ε(x) ∩ B_ε(y) = ∅ ⟺ ε ≤ D/2` (note: `≤`, not the paper's strict `<`; the paper's own statement has a second, smaller defect — an endpoint (non-)strictness error — that is masked by the bigger defect and only visible once the space is genuinely midpoint-convex, e.g. `ℝ^n`).
- **`ℝ^n` with Euclidean distance** is midpoint-convex (it's a geodesic space), so the theorem's spirit is correct there — this is presumably the mental model the author was generalizing from ("measurement apparatus" intuition). The theorem is true in spirit for continuous, geodesic ambient spaces and false in general, and specifically false for the paper's actual object of study, the discrete Hamming cube.
- **Geodesic spaces / length spaces** are indeed "the appropriate condition" per the task's question 4 — more precisely *midpoint metric spaces* is the minimal exact hypothesis (geodesic ⟹ midpoint-convex, but midpoint-convexity is what's actually used in the proof, and for complete spaces the two notions coincide by a standard theorem in metric geometry — see Burago–Burago–Ivanov, *A Course in Metric Geometry*, which is already Ref. [7] in the paper's own bibliography and states exactly this equivalence).

### 1.4 The correct discrete-Hamming-cube analogue

The Hamming cube graph *is* a geodesic space **in the graph-path sense**: for `x,y` with `d_H(x,y)=D`, one can always find `m` with `d_H(x,m)=a`, `d_H(y,m)=b`, `a+b=D`, for any integer split `a+b=D`, `a,b≥0` (flip any `a` of the `D` differing coordinates to get from `x` toward `y`). The obstruction is only that `D/2` need not be an integer, so no split achieves `a=b=D/2` exactly when `D` is odd. The best achievable "balanced" split is `a=⌈D/2⌉, b=⌊D/2⌋` (or vice versa).

Redoing the ball-intersection analysis with this fact gives the exact discrete statement:

> **Corrected Theorem 2.1 (Hamming-cube version).** For `x,y ∈ {0,1}^n` with `d_H(x,y)=D>0` and `ε>0`:
> `B_ε(x) ∩ B_ε(y) = ∅ ⟺ ε ≤ ⌈D/2⌉.`
> Equivalently, `B_ε(x) ∩ B_ε(y) ≠ ∅ ⟺ ε > ⌈D/2⌉.`

*Proof sketch.* (⟸, disjoint for `ε≤⌈D/2⌉`) If `z∈B_ε(x)∩B_ε(y)` then `d(x,z)+d(y,z) ≥ D` (triangle inequality) while `d(x,z)<ε` and `d(y,z)<ε` give `d(x,z)+d(y,z) < 2ε`. For integer distances, `d(x,z) ≤ ε-1` roughly... more precisely: since distances are integers, `d(x,z)<ε` means `d(x,z) ≤ ⌈ε⌉-1` when ε is not itself an integer, or `d(x,z) ≤ ε-1` when ε is an integer; combined, `d(x,z)+d(y,z) ≤ 2⌈D/2⌉-2 < D` whenever `D` is odd (since `2⌈D/2⌉ = D+1`), contradiction — so no such `z` exists once `ε ≤ ⌈D/2⌉`. (⟹, intersect for `ε>⌈D/2⌉`) Take `m` on a shortest path with `d(x,m)=⌈D/2⌉ ≤ D`, `d(y,m)=⌊D/2⌋`; both are `< ε` once `ε>⌈D/2⌉≥⌊D/2⌋`, so `m∈B_ε(x)∩B_ε(y)`. ∎ (Full case-checked verification, including even/odd `D` and integer/non-integer `ε`, was carried out numerically — see `scripts/theorem21_check.py` and `theorem21_check_output.txt` in this directory; all 100% of cases across `n≤10`, all pairs, all integer and half-integer `ε` up to `n`, match the corrected formula and none match the paper's original formula once `D` is odd.)

This differs from the paper's `ε<D/2` in exactly the way the counterexample shows: for `D=1`, corrected threshold is `⌈1/2⌉=1` (disjoint through `ε=1`, first meet at `ε>1`), vs. the paper's claimed `D/2=0.5`.

### 1.5 Does Remark 3.3 depend on the false direction? **Yes, directly.**

Remark 3.3: *"if `ε̂(A,I) > d/2` for some pair of solutions at distance `d`, then `A` cannot distinguish between them based on its found solutions alone."*

This is the contrapositive of the **false** (⇒) direction (disjoint ⟹ ε<D/2), i.e. it uses "`ε ≥ D/2` ⟹ not disjoint (cannot distinguish)." The true, surviving direction of Theorem 2.1 is (⇐)'s contrapositive: "not disjoint ⟹ `ε ≥ D/2`," which is the *opposite* implication and does **not** license Remark 3.3's claim. Using the corrected Hamming formula, the accurate statement would be: "if `ε̂(A,I) > ⌈d/2⌉`, then `A` cannot distinguish..." — a strictly weaker (larger-threshold) and different claim. **Remark 3.3 as written is false for the Hamming cube whenever `d` is odd and `d/2 ≤ ε̂(A,I) ≤ ⌈d/2⌉ - \text{(units)}`**; concretely, take `d=1`: the remark claims `ε̂ > 0.5` (e.g. `ε̂=1`, which is common) already implies indistinguishability, but per §1.1 that is exactly the case that's actually still distinguishable.

### 1.6 Does Conclusion claim (4) depend on the false direction? **Yes.**

Conclusion (4): *"The geometric distinguishability threshold `ε = d/2` provides a universal upper bound on achievable resolution."* Read as "no algorithm can do better than resolution `d/2`," this is again leaning on the false direction (that indistinguishability sets in at `d/2`). The **true** universal bound in the discrete case is `⌈d/2⌉`, not `d/2` — off by up to 1, which matters enormously at the small `n` (15–20) used in the paper's own experiments, where reported `ε̂` values in Table 1 are frequently in the 0–2 range, i.e. exactly the regime where the integer rounding error is not negligible.

### 1.7 Every downstream statement needing correction

| Location | Statement | Status | Fix needed |
|---|---|---|---|
| Theorem 2.1 | `B_ε(x)∩B_ε(y)=∅ ⟺ ε<D/2` | **FALSE** in `({0,1}^n,d_H)`; true only in midpoint/geodesic spaces | Split into (a) general metric-space one-directional lemma (⇐, survives) and (b) Hamming-cube corollary `ε≤⌈D/2⌉` (§1.4) |
| Remark 2.1 | "well-known and elementary" | **Misleading** — true half is elementary; false half is *not* a theorem of general metric spaces at all | Remove or heavily qualify |
| Remark 3.3 | uses `ε̂ > d/2 ⟹` indistinguishable | **FALSE** for discrete case, depends on broken direction | Replace `d/2` with `⌈d/2⌉` and re-derive; check whether any numeric claims in §5 change |
| Conclusion (4) | "`ε=d/2` … universal upper bound" | **Imprecise/false** by up to 1 Hamming unit | Restate as `⌈d/2⌉` |
| Abstract, line 21–22 | "geometric distinguishability threshold `ε=d/2`" | Same defect, propagates to the paper's headline framing | Restate |
| §7.4 (resolution floor `ε_min`) | speculative, explicitly flagged "motivating question, not a result" | **Not directly broken** — doesn't invoke the `d/2` value numerically, just the concept of *a* threshold existing | Still needs to swap conceptual anchor from `d/2` to `⌈d/2⌉` if kept |

**Not affected:** Definitions 2.1–2.6, 3.1–3.5 (definitions carry no truth value); the (⇐) direction and anything built only on it; Proposition 3.1's *inequality direction* (see §2, though its convention has an independent bug); the empirical Tables 1–4 themselves (raw measurements are unaffected — only their *interpretation* via the `d/2` threshold is at risk, and only where that interpretation is explicitly invoked, which Tables 1–4 do not do directly — they just report `ε̂` and coverage numbers, not distinguishability verdicts).

---

## 2. Proposition 3.1 — **Convention creates a false unconditional claim**

> Claim: For any `A`, `I` with `|S_I|≥2`, `ε̂(A,I) ≤ diam(S_I) ≤ n`.

### 2.1 The proof implicitly assumes `A(I) ≠ ∅`

The proof: `ε̂(A,I) = sup_{x∈S_I} min_{y∈A(I)} d_H(x,y)`, and since `A(I)⊆S_I`, `min_{y∈A(I)} d(x,y) ≤ max_{y∈S_I} d(x,y) ≤ diam(S_I)`. This step requires `A(I)` nonempty — `min_{y∈A(I)} d(x,y)` over an empty index set is `+∞` (or undefined) by the usual convention, not bounded by `diam(S_I)`.

### 2.2 The `A(I)=∅` convention breaks the proposition, not just the proof

Definition 3.3 patches this by fiat: *"If `A(I)=∅`, we set `ε̂(A,I)=n`."* Substituting into Proposition 3.1's claim: it now asserts `n ≤ diam(S_I) ≤ n`, i.e. **`diam(S_I)=n` is forced** whenever `A(I)=∅`. This is not generally true: `S_I` can easily have `diam(S_I) < n` (e.g. all solutions differing in only a handful of coordinates — common near a well-defined backbone) while some algorithm on a timeout finds nothing (`A(I)=∅`, e.g. a local-search run that never lands on a solution before its restart budget expires). In that case `ε̂(A,I)=n` by convention `> diam(S_I)`, **directly violating Proposition 3.1 as stated.**

### 2.3 Verdict and fix

Proposition 3.1 is **true only for `A(I)≠∅`**, where the given proof is in fact correct and complete. For `A(I)=∅`, it is **false under the paper's own convention** whenever `diam(S_I)<n`, which is the generic case, not an edge case. Two honest fixes, pick one:
1. Restate Proposition 3.1 with the explicit hypothesis `A(I)≠∅`, and treat the `A(I)=∅` case as a separate, explicitly non-bounded degenerate convention (drop any claim of `≤diam(S_I)` there — the convention `ε̂=n` should be understood as "resolution undefined / worst-case sentinel," not as an actual upper-bound-respecting measurement).
2. Change the convention itself to `ε̂(A,I) = diam(S_I)` (or leave `ε̂` **undefined**, with algorithms recording `A(I)=∅` as a separate failure flag) when `A(I)=∅`, which keeps Proposition 3.1 true unconditionally but changes the interpretability of `ε̂=n` as "found literally nothing."
Fix (1) is recommended: `n` as a sentinel for total failure is a defensible engineering convention (it makes `ε̂` monotonically worst when nothing is found, useful for aggregate statistics / plots), but the paper must not also claim the unconditional inequality once that convention is in force.

This is an independent bug from Theorem 2.1 — it does not depend on the `d/2` error at all.

---

## 3. Audit of all other definitions and propositions

- **Def. 2.1 (metric space), 2.2 (resolution/neighborhoods), 2.3 (geometric distinguishability), 2.4 (SAT instance/solution space), 2.5 (Hamming metric), 2.6 (cluster spectrum).** All standard, correctly stated, no issues. `d_H` is indeed a metric on `{0,1}^n` (verified: identity, symmetry, triangle inequality all hold trivially from the definition as a sum of coordinatewise indicator disagreements — it's literally the `ℓ^0`/`ℓ^1` metric on `{0,1}^n`).
- **Def. 3.1 (found solutions), 3.2 (blind zone), 3.3 (empirical resolution), 3.4 (normalized resolution), 3.5 (coverage).** Definitions, no truth claims except the `A(I)=∅` convention flagged in §2.
- **Remark 3.1, 3.2.** Interpretive glosses, not claims requiring proof; accurate restatements of the definitions.
- **Definition 6.1 (projection-induced coherence) / Proposition 6.1.** Proposition 6.1 ("`A(I)` approximates `S_I ∩ supp(μ)`") is stated as an approximate/qualitative claim ("approximates," "may reflect"), not a theorem with a proof — it is not literally proved anywhere in the paper (no proof is given, and none is claimed — the word "Proposition" is used loosely here for what is really an informal modeling assumption). **This is flagged as a labeling issue, not a mathematical error**: it should be a Definition/Remark/Assumption, not a "Proposition," since propositions are expected to carry proofs in the rest of the paper's own house style. See Phase 3 (`V2_DEFINITIONS.md`) for why this informal claim is also the weakest link conceptually, independent of labeling — `A(I) ≈ S_I ∩ supp(μ)` silently assumes the sampling measure alone determines what's found, ignoring path-dependent/sequential search dynamics (DPLL, CDCL) that have no natural static "support" at all.
- **§6.3 "Alignment and Residual."** Imports a numeric claim (`r≈0.93`) from a *different* paper (Ref. [5], prime-gap statistics) by loose analogy ("The present findings extend this observation to algorithmic contexts") with no actual quantitative or logical connection established in *this* paper — no correlation is computed here between anything and anything using that framework. This is not a mathematical error (nothing false is asserted), but it is **rhetorical overreach**: citing an unrelated numeric result from a self-authored paper in a different domain as if it lends support is a citation-inflation pattern that should be removed in V2 regardless of Theorem 2.1's fate.
- **§7.4 speculative resolution-floor argument.** Explicitly and correctly flagged by the paper itself as "a motivating question, not a result" — audited and found to be honestly labeled. No action needed beyond the `d/2`→`⌈d/2⌉` terminology fix if the section is kept.

---

## 4. Dependency map — what survives if Theorem 2.1 is corrected and Prop. 3.1's convention is patched

```
Def 2.1–2.6 (metric space, resolution, distinguishability, SAT, Hamming, cluster spectrum)
   |  all SURVIVE UNCHANGED (definitions, not claims)
   v
Theorem 2.1 (⇐ direction only) ---- SURVIVES, general metric spaces, no fix needed
Theorem 2.1 (⇒ direction)      ---- REPLACED by Hamming corollary: ε ≤ ⌈D/2⌉ (§1.4)
   |
   +--> Remark 2.1 "well-known and elementary" -- MUST BE QUALIFIED (half is not general)
   |
   +--> Remark 3.3 "ε̂ > d/2 ⟹ indistinguishable" -- MUST BE CORRECTED to ⌈d/2⌉, re-verify numerics
   |
   +--> Conclusion (4) "ε=d/2 universal upper bound" -- MUST BE CORRECTED to ⌈d/2⌉
   |
   +--> Abstract's "geometric distinguishability threshold ε=d/2" -- MUST BE CORRECTED
   |
   +--> §7.4 resolution-floor speculation -- SURVIVES CONCEPTUALLY, swap constant only

Def 3.1–3.5 (A(I), blind zone, ε̂, ε̃, coverage)
   |  SURVIVE AS DEFINITIONS; ε̂'s A(I)=∅ convention flagged independently (§2)
   v
Proposition 3.1 (ε̂ ≤ diam(S_I) ≤ n)
   |  SURVIVES for A(I)≠∅ (proof is correct); FALSE for A(I)=∅ under stated convention
   |  Does NOT depend on Theorem 2.1 at all -- independent bug, independent fix
   v
Remark 3.3 -- see above (depends on Thm 2.1, not on Prop 3.1)

§4 Experimental setup, §5 Results tables (1-4), §6.2 experimental confirmation
   |  SURVIVE UNCHANGED -- these are raw measurements (ε̂, coverage, Hamming-weight stats)
   |  that do not invoke the d/2 threshold or Prop 3.1's edge case in their computation.
   |  Only their *narrative interpretation* via "distinguishability" language is at risk,
   |  and only where such language is explicitly used (it mostly isn't in §5-§6; those
   |  sections report ε̂ and coverage as raw numbers and correctly avoid over-claiming
   |  a distinguishability verdict). See PHASE 6/7 audits for a SEPARATE, unrelated
   |  concern about the 500-solution cap confounding these same tables.

Definition 6.1 / Proposition 6.1 (projection-induced coherence)
   |  INDEPENDENT of Theorem 2.1 and Prop 3.1; flagged separately (§3) as an informal,
   |  unproved modeling assumption mislabeled as a Proposition.

§6.3 Alignment and Residual
   |  INDEPENDENT; flagged separately (§3) as unsupported cross-paper analogy, remove.

Conclusion (1),(2),(3) -- experimental claims about resolution profiles, observer-induced
   fragmentation, structured blind zones
   |  SURVIVE, do not depend on the d/2 threshold (they're empirical, about ε̂ values and
   |  Hamming-weight distributions, not about a distinguishability verdict)

Conclusion (4) -- SEE ABOVE, must be corrected.
```

### Bottom line
- **One theorem (2.1) is false as stated**, with a clean, provable, discrete-Hamming-cube corrected replacement (`ε ≤ ⌈D/2⌉`).
- **Exactly three downstream statements** genuinely depend on the false direction and need correction: Remark 3.3, Conclusion (4), and the Abstract's headline "`ε=d/2`" line. Remark 2.1 needs a qualifying caveat.
- **One proposition (3.1) has an independent, unrelated bug** (the `A(I)=∅` convention), fixable by adding a hypothesis.
- **All empirical results (Tables 1–4, §5–6) survive**, because they report raw `ε̂`/coverage/weight statistics rather than invoking the flawed distinguishability threshold in their computation — the error is confined to the paper's *theoretical framing*, not its *experimental machinery*. (A separate, unrelated methodological concern about these same tables — the 500-solution cap — is audited in `ORIGINAL_EXPERIMENT_AUDIT.md`.)
- **Two passages (Def 6.1/Prop 6.1 labeling, §6.3 cross-paper analogy) are flagged for removal/relabeling in V2 independent of the Theorem 2.1 issue.**

This means the paper's *empirical* contribution is structurally salvageable; the damage is concentrated in one geometric theorem whose corrected form is a small, provable, one-paragraph fix — but that theorem is also exactly the "universal upper bound" the Conclusion leans on rhetorically, so the framing (not just one lemma) needs a rewrite. See `FINAL_VERDICT.md`.
