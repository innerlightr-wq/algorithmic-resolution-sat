# V2_DEFINITIONS.md — Proposed mathematical framework (Phases 3 & 4)

Depends on: `AUDIT.md` (Theorem 2.1 correction), `PRIOR_ART.md` (novelty map). This is a *design* document — candidate definitions, not a claim that all of them belong in V2 (see `FINAL_VERDICT.md` for what's actually recommended).

---

## 0. The single most important fact this pass surfaced

**`ε̂(A,I)` is exactly the Hausdorff distance between `A(I)` and `S_I`.**

Since `A(I) ⊆ S_I`, the reverse directed distance `\vec d_H(A(I),S_I) = max_{y∈A(I)} min_{x∈S_I} d(y,x) = 0` (every found solution is trivially at distance 0 from itself in `S_I`). So the ordinary symmetric Hausdorff distance collapses to the one directed term the paper already defines:

`d_H(S_I, A(I)) = max( \vec d_H(S_I,A(I)), \vec d_H(A(I),S_I) ) = \vec d_H(S_I,A(I)) = ε̂(A,I).`

Equivalently, `ε̂(A,I)` is the smallest `r` such that `A(I)` is an `r`-net of `S_I` — i.e. the **covering radius of `A(I)` relative to `S_I`** in the Hamming metric (a subset-relative generalization of the coding-theory covering radius, which is normally defined relative to the whole ambient cube — see `PRIOR_ART.md` §1).

This single identity is what makes Phase 4 tractable "for free": it means every classical **Hausdorff-stability** result in computational topology applies directly to the pair `(S_I, A(I))` with no translation work beyond recognizing the identity. Use it as the organizing fact of V2 §2 (formal framework), not as a footnote.

---

## 1. The three objects, formalized

### 1.1 `S_I` — true solution space (unchanged from January draft)
`S_I = {x ∈ {0,1}^n : I(x) = true} ⊆ ({0,1}^n, d_H)`. Fixed, finite, purely a property of the instance. No change needed.

### 1.2 `A(I)` — observed solution set (unchanged, with the `A(I)=∅` convention now cleanly separated)
`A(I) ⊆ S_I`, the (possibly empty) set an algorithm actually returns within its budget. Recommend explicitly splitting the definition of `ε̂` into two cases with different semantic status (fixes the Proposition 3.1 bug in `AUDIT.md` §2):
- `A(I) ≠ ∅`: `ε̂(A,I) = max_{x∈S_I} min_{y∈A(I)} d_H(x,y)`, a genuine covering-radius/Hausdorff-distance measurement, bounded by `diam(S_I) ≤ n` (Prop. 3.1, now unconditionally correct on this branch).
- `A(I) = ∅`: **not a measurement** — record it as a separate categorical flag ("total failure"), and either leave `ε̂` undefined or report it as `⊤` (sentinel), never folded into the same numeric scale/plots as genuine measurements without a visual/statistical break. This avoids the false unconditional inequality while keeping the useful "worst case" bookkeeping.

### 1.3 The accessibility field — replacing the informal "`μ_A`, `A(I) ≈ S_I ∩ supp(μ_A)`" picture

The January draft's Prop. 6.1 (`A(I) ≈ S_I ∩ supp(μ)`) is too weak for two reasons, confirmed by re-reading it against how the tested algorithms actually work:
1. It is stated as an approximation with no error control — not falsifiable as written.
2. It presumes a single static distribution `μ` determines what's found, which is a reasonable model for **Random/Biased Sampling** (§4.2(d)(e) of the paper — literally true by construction there) but not for **DPLL** (deterministic, path-dependent branching order; "support" of a point mass is degenerate) or **local search** (state-dependent Markov dynamics with restarts; not a static sampling distribution at all, more like a random walk with absorbing states at solutions).

**Proposed replacement: a finite-time discovery/accessibility function**, as the task requests:

`p_{A,T}(x | I) = P(algorithm A, run with budget T on instance I, outputs x among its found solutions)`,

defined over the randomness of `A` (seed, restart schedule, tie-breaking) for **fixed** `I`. This is well-defined for every algorithm family in the paper, including deterministic DPLL, by folding in the algorithm's *randomizable* knobs:
- **Randomized algorithms (local search, sampling)**: `p_{A,T}` is the literal marginal probability of `x` appearing in `A(I)` over the algorithm's own random seed, for budget `T` (restarts × flips, or sample count).
- **Deterministic DPLL/CDCL**: define the induced ensemble over a *randomized wrapper* — random variable-branching order, random restarts, random clause-database perturbations (a "randomized CDCL" ensemble is not a hack; virtually every modern CDCL solver already restarts with randomized phase/branching heuristics, so this is a realistic, not artificial, randomization). `p_{A,T}(x|I)` is then the probability, over this induced ensemble, that `x` is discovered by budget `T`. For strictly single-run deterministic DPLL with fixed tie-breaking, `p_{A,T}(x|I) ∈ {0,1}` degenerates to an indicator — a legitimate but uninformative special case; the useful object is the induced ensemble.

Two derived quantities:
- **Accessibility (fixed budget)**: `a_T(x|I) = p_{A,T}(x|I)`, a number in `[0,1]` per solution.
- **Blind-zone-as-low-probability-region (not hard zero)**: the task explicitly asks whether the blind zone should be a hard zero-probability region or a low-accessibility region. **Answer: low-accessibility, not hard zero, is the correct and more falsifiable model**, for a concrete reason verified against the paper's own Table 3/4 data — the biased sampler's blind zone is characterized by a *shifted mean* Hamming weight (9.8 vs 5.2, Table 4), not by an impossible region; biased sampling assigns strictly positive (if tiny) probability to every high-weight assignment. A hard-zero model is only exactly correct for structurally excluded algorithms (e.g. a DPLL variant whose branching order provably can never reach certain assignments given a fixed clause order — a measure-zero pathological case) and should not be the default model.

### 1.4 The map `S_I --(A,T)--> A(I)` as an expectation/thresholding of the accessibility field

`A(I)` (single run) is a realization; its **expected geometric relationship to `S_I`** is best summarized not by `A(I) ≈ S_I ∩ supp(μ_A)` but by the accessibility-weighted version of the resolution quantity:

`ε̂_p(A,T,I) = E_{run}[ max_{x∈S_I} min_{y∈A(I)} d_H(x,y) ]` (expectation over the randomized ensemble), with `ε̂(A,I)` (original, single-run) as one sample of this random variable. This directly supports Phase 5's statistical protocol (repeat across seeds) and gives the paper a principled reason to report seed-to-seed variance, which the January draft's single-run tables (1–4) do not.

---

## 2. Geometric/topological distortion quantities (Phase 4)

### 2.1 The original `Δ_A(r) = |C_{S_I}(r) - C_{A(I)}(r)|` — keep as a cheap diagnostic, not the main tool

This is a legitimate, cheap-to-compute quantity, but it is **not stable**: two very different-looking cluster structures can have the same *count* of components (an off-by-zero coincidence in the number of clusters says nothing about whether they're the *same* clusters, at the *same* scales, of the *same* sizes). It should be retained in V2 only as an illustrative/motivating quantity (exactly its role in Example 5.1), demoted from "the" distortion measure to "a simple special case of §2.2 below."

### 2.2 The correct tool: 0-dimensional persistent homology + bottleneck distance, via **Rips-complex stability under Hausdorff distance**

Let `Rips_r(S)` denote the Vietoris–Rips complex of a finite metric space `S` at scale `r` (simplex on any subset of diameter `≤ r`), and `Dgm_k(Rips(S))` its `k`-dimensional persistence diagram as `r` varies. `C_S(r)` (Def. 2.6) is exactly the number of connected components of `Rips_r(S)` — i.e. `C_S(r) = ` (number of points alive in `Dgm_0(Rips(S))` at parameter `r`). So the cluster spectrum is already, without modification, the "barcode-counting function" of 0-dim persistent homology; **this identification alone is worth stating explicitly in V2** since it immediately hands the paper the right theorem:

> **Rips stability (KNOWN RESULT — Cohen-Steiner–Edelsbrunner–Harer 2007; Chazal–de Silva–Oudot 2014, arXiv:1207.3885; see `PRIOR_ART.md` §4 for exact citations and applicability check):**
> For finite subsets `X, Y` of a common metric space, `d_B(Dgm_k(Rips(X)), Dgm_k(Rips(Y))) ≤ 2 d_H(X,Y)` for every homological dimension `k`, where `d_B` is bottleneck distance and `d_H` is the (here: possibly asymmetric-turned-symmetric, see §0) Hausdorff distance.

Substituting `X = S_I`, `Y = A(I)`, and using §0's identity `d_H(S_I,A(I)) = ε̂(A,I)`:

> **Corollary (the schematic theorem the task asked for, obtained by direct substitution — KNOWN RESULT, not reproved):**
> `d_B(Dgm_k(Rips(A(I))), Dgm_k(Rips(S_I))) ≤ 2 ε̂(A,I)` for all `k`.

This is *exactly* "small covering radius ⇒ observed topology reliable above some scale," made precise: persistence features (births/deaths of connected components, loops, etc.) of the *observed* set `A(I)` are guaranteed to lie within `2ε̂(A,I)` (in the bottleneck/sup-norm sense on birth-death coordinates) of the *true* features of `S_I`. Concretely for `C_S(r)` (0-dim only): if `A(I)`'s cluster spectrum shows a merge/split event at scale `r`, the true spectrum `C_{S_I}` has a corresponding event at some scale in `[r-2ε̂, r+2ε̂]` — **any apparent structural feature of `A(I)` at a scale smaller than `~2ε̂(A,I)` should not be trusted as reflecting `S_I`**; features at scales well above `2ε̂(A,I)` are reliable. This directly reframes and sharpens Example 5.1's "observer-induced fragmentation" finding: it is not merely an anecdote, it is the expected behavior whenever the biased sampler's `ε̂` (Table 1: 1.25–1.67) is comparable to or larger than the scale at which the true cluster spectrum has its only feature (`r=4` in Example 5.1) — `2ε̂≈2.5–3.3` vs. feature scale `4` is *borderline*, exactly consistent with a stability-theorem-predicted risk of spurious splitting, not a coincidence.

### 2.3 Translation caveats — do **not** import silently (per task instruction)

- **No geodesic/length-space hypothesis is needed for the bottleneck bound itself** (confirmed in `PRIOR_ART.md` §4 against primary sources) — it holds for `Rips` complexes of arbitrary finite metric spaces, discrete Hamming cube included, because Rips complexes are built combinatorially from the pairwise-distance matrix alone; no interpolation/midpoint structure is used anywhere in the proof of the stability theorem. This is a genuinely different situation from Theorem 2.1 in `AUDIT.md`, where the geodesic assumption *was* silently smuggled in — good practice here means stating *why* this import is safe, not just asserting it.
- **What the bound does *not* give**: it bounds diagram (birth–death pair) distance, not "the two complexes are homotopy equivalent" or "the cluster counts are equal." A homotopy-type **reconstruction** theorem (recovering `S_I`'s true topology exactly, not just up to `2ε̂` diagram distance) needs additional regularity on `S_I` — e.g. a positive reach / feature-size condition, in the style of Niyogi–Smale–Weinberger manifold-reconstruction theorems — which the Hamming cube does not generically supply (SAT solution clusters have no analogue of "reach" without extra assumptions on the clause structure). **V2 must state the persistence-stability result as a diagram-distance bound only**, and explicitly flag reconstruction-type claims ("we recover the true cluster structure") as a strictly stronger, unproven, and likely false-without-extra-hypotheses claim.
- The bound is in terms of `ε̂`, which per §1.2 is only defined on the `A(I)≠∅` branch — the corollary is vacuous/undefined when `A(I)=∅` (as it should be; no persistence-stability claim can be made from zero data).

---

## 3. Summary of what changes vs. the January draft

| January draft | V2 proposal | Why |
|---|---|---|
| `μ_A`, `A(I) ≈ S_I ∩ supp(μ_A)` (Prop. 6.1) | Discovery/accessibility function `p_{A,T}(x|I)`, low-accessibility (not hard-zero) blind zones | Covers deterministic algorithms (DPLL/CDCL) that Prop 6.1 can't express; falsifiable (§1.3) |
| `ε̂(A,I)` presented as a new "algorithmic resolution" quantity | Same formula, explicitly identified as Hausdorff distance / subset-relative covering radius (§0) | Correct framing per `PRIOR_ART.md`; also what unlocks §2's theorem "for free" |
| `Δ_A(r) = |C_{S_I}(r)-C_{A(I)}(r)|` as the main distortion measure | Kept as a cheap illustrative special case; main tool becomes bottleneck distance between 0-dim (and optionally higher) persistence diagrams of `Rips(S_I)`, `Rips(A(I))` | `Δ_A(r)` is not stable/informative on its own; bottleneck distance is, and comes with a ready-made theorem (§2.2) |
| Theorem 2.1, `ε=d/2` universal bound | `ε ≤ ⌈d/2⌉` (see `AUDIT.md`) | Corrects the false direction |
| Single-run `ε̂(A,I)` reported without variance | `ε̂_p(A,T,I)` as expectation over a randomized-ensemble wrapper, reported with variance across seeds | Needed for Phase 5's predictive protocol and for honest uncertainty reporting |
