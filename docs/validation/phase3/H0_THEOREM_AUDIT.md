# H0_THEOREM_AUDIT.md — Phase 3, Part 12

Re-derives the Phase 2 asymmetric H₀ correspondence theorem from scratch, attacks it for counterexamples, and reports an aggressive literature search. Default assumption applied throughout, per instruction: **this theorem is probably a specialization of known mathematics until proven otherwise.**

## Re-derivation from scratch

Setup: `A ⊆ S` finite subsets of a common metric space, `ε := d_Haus(A,S)` (well-defined, equals the directed distance `S→A` since `A⊆S` makes the reverse direction `0` — `HAUSDORFF_IDENTITY.md`). For `r≥0`, the `r`-cluster graph on a point set `P` connects `p,q` iff `d(p,q)≤r`; `C_P(r)` = number of connected components.

**Claim (a), no false merge, zero slack.** If `x,y∈A` are connected in `A`'s `r`-cluster graph, they are connected in `S`'s `r`-cluster graph.
*Proof.* Any chain `x=p_0,...,p_k=y` in `A` with consecutive distances `≤r` is, term for term, also a chain of points of `S` (since `A⊆S`) with the same consecutive distances. No construction needed — this is immediate from the subset relation. ∎ **No hypothesis beyond `A⊆S` is used; `ε` never appears.**

**Claim (b), guaranteed re-merge, `2ε` slack.** Let `φ:S→A` send each `x` to a nearest point of `A` (`d(x,φ(x))≤ε`, `φ(x)=x` if `x∈A`). If `x,y∈S` are connected in `S`'s `r`-cluster graph, then `φ(x),φ(y)` are connected in `A`'s `(r+2ε)`-cluster graph.
*Proof.* For a chain `x=p_0,...,p_k=y` in `S` with consecutive distances `≤r`: `d(φ(p_i),φ(p_{i+1})) ≤ d(φ(p_i),p_i)+d(p_i,p_{i+1})+d(p_{i+1},φ(p_{i+1})) ≤ ε+r+ε`. So `φ(p_0),...,φ(p_k)` is a chain in `A` with consecutive distances `≤r+2ε`. ∎

**Consequence**: `C_A(r+2ε) ≤ C_S(r)` for all `r≥0`.

This re-derivation is **identical in substance** to Phase 2's `PERSISTENCE_STABILITY.md` §3 proof — reproducing it here from scratch (without looking at the Phase 2 file while writing this section) reconfirms it is a correct, elementary, two-line-per-direction argument, not something that depended on an error in the original derivation.

## Attack for counterexamples

Actively searched for a counterexample to claim (b) with a constant `c<2`, and for a violation of claim (a) under any interpretation of "connected." None found. The brute-force verification carried over unchanged from Phase 2 (`phase2/data/h0_correspondence_verify_output.txt`: 100 random `(S,A)` instances, `n=4..8`, **zero failures** of either claim) plus a **new** extremal construction (`H0_SHARPNESS.md`) that achieves equality in claim (b) exactly, confirming the bound cannot be tightened, not merely that no counterexample happened to be found by random search.

## Extremal examples (summary — full construction in `H0_SHARPNESS.md`)

A family of explicit 4-point Hamming-cube instances (`p,q,a,b`, `n=r+2ε`) where `p,q` are directly `r`-connected in `S={p,q,a,b}` but their nearest-`A` images `a,b` (`A={a,b}`) are connected in `A` at radius `r+2ε` and **at no smaller radius** — verified computationally for 7 `(r,ε)` combinations, all exact. **The constant `2` is sharp, including specifically within the Hamming cube** (not just in abstract/pathological metric spaces) — see `H0_SHARPNESS.md`.

## Literature search performed (aggressive, per instruction)

A dedicated fork searched, with real citation verification (not guessing): Vietoris–Rips filtration stability, persistent H₀ stability, single-linkage/dendrogram stability, "merge distortion," ε-sample/metric-reconstruction literature, and one-sided/asymmetric Gromov–Hausdorff-type Rips stability specifically. Full findings in `H0_PRIOR_ART_MATRIX.md`; headline result:

**Blumberg & Lesnick, "Stability of 2-Parameter Persistent Homology," arXiv:2010.09628 (confirmed via direct PDF read, not secondhand)**, Proposition 3.9, states an asymmetric stability variant specifically for the case `X⊆Y` — **but it is a different theorem**, not a match: it concerns **2-parameter degree-Rips/degree-Čech bifiltrations** (a density/robustness-parameter-augmented persistence module, not plain single-parameter Rips), the distance driving the shift is **Prokhorov distance between the normalized empirical measures** `ν_X,ν_Y` (a measure-theoretic notion sensitive to point *density*, not ordinary Hausdorff distance between point sets), and even their **general** (non-subset) base theorem's radius-shift constant is **3**, not `2` (their `γ_δ = γ_{δ,3}`, and `Proposition 3.7` proves `3` is tight *for that theorem*) — the subset case tightens the story by adding an extra **degree-ratio** shift `κ_{|X|/|Y|}`, not by improving the radius constant. **This is a substantially more sophisticated, differently-motivated result (built for density-outlier robustness) than the plain-Hausdorff, single-parameter, H₀-only statement proved here.**

Critically, **Blumberg & Lesnick's own paper cites a closer precedent**: "Harker et al. have introduced a variant of the standard Rips stability theorem (Theorem 1.1(ii)) for the case where one metric space is a subset of the other [40, Proposition 5.6]" — **S. Harker, M. Kramár, R. Levanger, K. Mischaikow, "A comparison framework for interleaved persistence modules," Journal of Applied and Computational Topology 3(1-2):85–118, 2019** — this is explicitly described as the **single-parameter** analogue of the subset-case variant, i.e. much closer in spirit to the theorem proved here. **This paper's Proposition 5.6 could not be directly retrieved and read within the time available for this pass** (bibliographic existence confirmed via the Blumberg–Lesnick citation and cross-check of the reference-list entry in the actual PDF text; the proposition's exact statement/constant was not independently verified).

## Honest verdict

Per the task's mandated default assumption, and consistent with what was and was not verified: **this theorem should be classified as very likely a specialization of already-published mathematics** — specifically, very likely a special case or close relative of Harker–Kramár–Levanger–Mischaikow (2019) Proposition 5.6, which Blumberg & Lesnick (a peer-reviewed-adjacent, carefully-refereed source) themselves cite as *the* precedent for exactly this "subset-case Rips stability" question. **It should not be classified as a novel theorem.** What this pass adds, and can honestly claim: (i) an independent, elementary, from-scratch derivation not requiring the general interleaving-distance/homotopy-interleaving machinery those papers use (pedagogically simpler, self-contained, useful for a SAT-audience paper that should not need to import multiparameter persistence theory to state the SAT-relevant special case); (ii) a **verified sharp extremal example** (Hamming-cube-realized, `H0_SHARPNESS.md`) establishing that the constant `2` cannot be improved — sharpness was not something the fork's search confirmed or denied for the cited prior-art papers, so this specific fact is this pass's own contribution regardless of the theorem's overall novelty status. See `H0_PRIOR_ART_MATRIX.md` for the full classification table and `NOVELTY_CLASSIFICATION.md` for the final label.
