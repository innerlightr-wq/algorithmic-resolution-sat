# V2_THEOREMS.md — Candidate statements for V2, labeled by status

Labels used, per task instructions: **PROVED** (proof given below, checked independently, in this document), **KNOWN RESULT** (established elsewhere, cited, directly applicable — not reproved), **CONJECTURE** (plausible, not proved, falsification criteria given), **FALSE** (shown false, with counterexample).

---

## T1. Corrected geometric distinguishability threshold (Hamming cube)

> For `x,y ∈ {0,1}^n`, `d_H(x,y)=D>0`, `ε>0`: `B_ε(x)∩B_ε(y)=∅ ⟺ ε ≤ ⌈D/2⌉.`

**Status: PROVED.** Full proof in `AUDIT.md` §1.4; independently verified by exhaustive brute-force check across `n≤7`, all `(D,ε)` pairs on a half-integer grid — 308/308 cases match, 0 mismatches (`scripts/theorem21_check.py`, output in `theorem21_check_output.txt`).

## T2. Original Theorem 2.1 as literally stated

> `B_ε(x)∩B_ε(y)=∅ ⟺ ε<D/2`, for arbitrary metric spaces.

**Status: FALSE.** Counterexample: `x,y∈{0,1}^3`, `D=1`, `ε=1`. `B_1(x)={x}`, `B_1(y)={y}`, disjoint — but `ε=1 ⊀ D/2=0.5`, so the biconditional's right-hand side is false while the left-hand side is true. 44/308 grid cases mismatch in the brute-force check (`AUDIT.md` §1.1, §1.4). The (⇐) direction alone (`ε<D/2 ⟹ disjoint`) is separately **PROVED** for arbitrary metric spaces (pure triangle-inequality argument, no space-specific hypothesis) — see `AUDIT.md` §1.2.

## T3. Theorem 2.1 restricted to midpoint / geodesic metric spaces

> If `(X,d)` is a midpoint metric space (∀x,y ∃m: d(x,m)=d(y,m)=d(x,y)/2), then `B_ε(x)∩B_ε(y)=∅ ⟺ ε≤D/2` (closed at the boundary — note the corrected strictness vs. the paper's original `<`, see `AUDIT.md` §1.3).

**Status: PROVED** (standard metric-geometry argument, correct once midpoint existence is granted — see `AUDIT.md` §1.3; the midpoint-space hypothesis is the exact minimal repair, and by the standard Hopf–Rinow-type equivalence for complete spaces (Burago–Burago–Ivanov, already Ref. [7] of the January paper), midpoint-convex ⟺ geodesic for complete spaces). Not novel — this is the general form of a standard fact, correctly recoverable once the missing hypothesis is supplied.

## T4. `ε̂(A,I)` is the Hausdorff distance between `A(I)` and `S_I`

> `A(I)⊆S_I ⟹ d_H(S_I,A(I)) = ε̂(A,I)` where `d_H` is the (symmetric) Hausdorff distance under `d_Hamming`.

**Status: PROVED** (one-line algebraic identity, `V2_DEFINITIONS.md` §0 / `PRIOR_ART.md` §2 — the reverse directed term vanishes because `A(I)⊆S_I` puts every found point at distance 0 from itself in `S_I`). Not novel as *mathematics* (Hausdorff distance is textbook) — the contribution, if any, is recognizing the identification, not proving it (trivial once stated).

## T5. Persistence-diagram stability of `A(I)` vs. `S_I`

> `d_B(Dgm_k(Rips(A(I))), Dgm_k(Rips(S_I))) ≤ 2ε̂(A,I)` for all homological dimensions `k`.

**Status: KNOWN RESULT, directly applicable — not reproved.** Follows by direct substitution of T4 into the general Rips-complex bottleneck-stability theorem (Cohen-Steiner–Edelsbrunner–Harer 2007, DOI 10.1007/s00454-006-1276-5; Chazal–de Silva–Oudot 2014, arXiv:1207.3885 — full citations and applicability check in `PRIOR_ART.md` §4, translation caveats in `V2_DEFINITIONS.md` §2.3). Confirmed to require **no geodesic/length-space hypothesis** — safe to import into the discrete Hamming cube without the Theorem-2.1-style error, because Rips complexes are built purely combinatorially from the distance matrix. **This is the single most useful result available for V2** and should be reported honestly as "known, applied here for the first time to this specific SAT-solution-space setting" (classification C, per `PRIOR_ART.md`), not as an original theorem.

## T6. Coverage and covering radius are logically independent without extra structure on `S_I`

> There is no monotone function `f` such that `ε̂(A,I) ≤ f(Cov(A,I))` or `Cov(A,I) ≥ g(ε̂(A,I))` holds for arbitrary finite `S_I⊆{0,1}^n` and arbitrary `A(I)⊆S_I`.

**Status: PROVED**, by two explicit, verified constructions (`scripts/coverage_vs_resolution_examples.py`, output in `coverage_vs_resolution_output.txt`):

- **Example A (high coverage, poor resolution).** `S = {0^n} ∪ {weight-1 vectors} ∪ {1^n}`, `A = S \ {1^n}`. Verified: at `n=50`, `coverage=0.981`, `ε̂=49` (`ε̂/diam=0.98`, i.e. resolution is *worse*, relatively, precisely as coverage approaches 1). Coverage → 1 while normalized `ε̂` also → 1 (both near their "good"/"bad" extremes simultaneously) as `n→∞`.
- **Example B (low coverage, good resolution).** `S = {0,1}^7` (full cube, 128 points), `A` = the `[7,4]` binary Hamming code (16 codewords, a perfect code). Verified: `coverage=0.125`, `ε̂=1` (covering radius of a perfect code equals its packing radius, here exactly 1, vs. `diam=7`).

Since coverage and `ε̂` move in *opposite* directions across these two constructions (high-coverage/poor-resolution vs. low-coverage/good-resolution), no monotone deterministic inequality of the conjectured form can hold in general. **This directly and precisely confirms the paper's own Remark 3.2** ("Coverage and resolution measure different aspects... may have high coverage but poor resolution, or vice versa") — that remark, previously asserted without proof or example, is now a proved statement with explicit witnesses. This is the cleanest, most self-contained new theorem-shaped result to come out of this audit (see `FINAL_VERDICT.md` — "lowest-hanging rigorous result").

## T7. Deterministic coverage/resolution inequality *given* bounded packing structure on `S_I` — CONJECTURE

> If `S_I` has doubling dimension (or packing-number growth) bounded by some `κ`, then `Cov(A,I) ≥ 1 - h(ε̂(A,I), κ, |S_I|)` for some explicit function `h`, tightening as `κ` decreases (i.e., as `S_I` is more "spread out"/low-dimensional in the Hamming metric).

**Status: CONJECTURE.** Motivated by classical epsilon-net/metric-entropy machinery (`PRIOR_ART.md` §3), which bounds *cardinality needed to achieve a radius* for well-behaved (doubling/convex) spaces — the reverse direction needed here (bound coverage *given* an achieved radius and a cardinality budget) was not found in the literature for arbitrary finite subsets, and T6 shows it is false without *some* such structural hypothesis. Whether random 3-SAT solution clusters (per Achlioptas–Ricci-Tersenghi's known geometry, cited in `PRIOR_ART.md` §5) have bounded enough packing structure near a given `α`, `n` to make a concrete, checkable version of `h` provable is open. **Falsification test**: compute empirical packing numbers of reconstructed `S_I` sets (already available from `cap_confound_reconstruction.py`'s enumeration) at several radii, check whether a clean doubling-dimension bound holds across the `α` grid; if packing numbers scale close to `2^n` (no useful bound), the conjecture is likely untestable/false as a *useful* statement for this instance family, and should be dropped rather than pursued further. This is explicitly flagged as the least-supported, most speculative item in this document — do not present as more than a research question in V2.

## T8. Accessibility-weighted resolution as expectation

> `ε̂_p(A,T,I) = E_{run}[ε̂(A,I)]` (over a randomized-ensemble wrapper, `V2_DEFINITIONS.md` §1.3–1.4) is a well-defined random-variable generalization of the January draft's single-run `ε̂(A,I)`, with `ε̂(A,I)` as one sample.

**Status: DEFINITIONAL** (not a theorem — restated here only to flag that no probabilistic *inequality* about `ε̂_p` — e.g. concentration around its mean, tail bounds — is claimed or proved anywhere in this pass; any such claim in V2 would need new work, not reuse of T1–T6.)

## Summary table

| # | Statement | Label |
|---|---|---|
| T1 | Corrected Hamming distinguishability threshold `ε≤⌈D/2⌉` | **PROVED** |
| T2 | Original Theorem 2.1 as stated | **FALSE** |
| T3 | Theorem 2.1 restricted to midpoint/geodesic spaces | **PROVED** (standard) |
| T4 | `ε̂(A,I)` = Hausdorff distance `d_H(S_I,A(I))` | **PROVED** (trivial once stated) |
| T5 | Bottleneck stability: `d_B ≤ 2ε̂(A,I)` | **KNOWN RESULT**, newly applied here |
| T6 | Coverage/resolution logical independence (2 witnesses) | **PROVED** |
| T7 | Coverage/resolution inequality under bounded packing dimension | **CONJECTURE** |
| T8 | Accessibility-weighted resolution as expectation | definitional, no inequality claimed |
