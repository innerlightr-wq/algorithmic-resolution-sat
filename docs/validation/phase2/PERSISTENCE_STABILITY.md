# PERSISTENCE_STABILITY.md — Phase 2, Part 3

Combines: (A) the general Vietoris–Rips bottleneck-stability bound, derived here by an explicit, elementary interleaving construction specialized to our setting (not merely cited) and cross-checked against verified literature; (B) a sharper, H₀-specific, asymmetric correspondence theorem derived and brute-force-verified independently, which is the strongest safe statement about connectivity/clustering specifically — stronger and more interpretable than the general bound for that one purpose.

## 0. Literature check performed (citations, not guessed)

A dedicated literature-verification pass (background research, live search) confirmed:

1. **Constant is 2, not 1**, for the Hausdorff-distance Rips-stability bound, under the standard "edge `{x,y}` present in `Rips_r` iff `d(x,y)≤r`" convention (the same convention as the January paper's own `C_S(r)`, Def. 2.6). Primary reference: Chazal, F., de Silva, V., Oudot, S., *Persistence Stability for Geometric Complexes*, Geometriae Dedicata 173 (2014), 193–214, DOI 10.1007/s10711-013-9937-z, arXiv:1207.3885. Its stated scope is **totally bounded metric spaces** — no geodesic/length-space/convexity hypothesis — confirmed applicable to the discrete Hamming cube (finite, trivially totally bounded) with no translation risk of the kind that broke the January Theorem 2.1.
2. **Cohen-Steiner–Edelsbrunner–Harer (2007)**, *Stability of Persistence Diagrams*, Discrete & Comput. Geom. 37, 103–120, DOI 10.1007/s00454-006-1276-5, is confirmed to bound diagram distance for **tame functions on a fixed topological space** (sublevel-set persistence) — it is the historical ancestor of the stability idea but is **not** itself the Rips/point-cloud statement. Citing it alone as "the" justification for Rips-complex stability would be a citation error; the correct citation for our setting is item 1.
3. **Isometry theorem** (bottleneck distance = interleaving distance, for pointwise finite-dimensional persistence modules over a field), needed to convert the interleaving bound derived below (§2) into a bottleneck-distance bound: Chazal, Cohen-Steiner, Glisse, Guibas, Oudot, *Proximity of Persistence Modules and their Diagrams*, SoCG 2009 — confirmed to exist and establish exactly this algebraic proximity/interleaving framework. A consolidated book-length treatment (Chazal–de Silva–Glisse–Oudot, Springer Briefs) is very likely the standard follow-up reference but its exact arXiv/DOI identifier could **not** be independently confirmed in the search performed — flagged here rather than guessed; cite the 2009 SoCG paper as the primary, verified source for the isometry theorem, and treat the book as a secondary reference to double-check before submission rather than cite blind.
4. No materially better one-stop 2015–2025 replacement citation was found; item 1 remains the correct primary reference.

## 1. Filtration convention, fixed explicitly

`Rips_r(P)` for finite `P⊆{0,1}^n`: simplex `σ⊆P` is included at parameter `r` iff `diam(σ)≤r` (equivalently, edges present iff `d_H(x,y)≤r`). **This is the same convention as the paper's own Definition 2.6** (`C_S(r)`: `x∼y` iff `d_H(x,y)≤r`), so `C_S(r)` is *exactly* the number of connected components of `Rips_r(S)`, i.e. exactly the value of the `H_0` "Betti number" function of the Rips filtration at parameter `r` — this identification requires no reinterpretation, only the observation that it's already true (worth stating explicitly in V2, since it is what makes persistent homology usable "for free" on top of the paper's existing cluster-spectrum machinery). All constants below (in particular, the factor of `2`) are stated relative to *this* convention; a different convention (e.g. Rips parameter defined as `2r`, or a Čech complex with balls of radius `r/2`) would rescale the constant, which is exactly the ambiguity the task asked to pin down — resolved here by fixing the convention once, matching the paper's own Def. 2.6, and never switching mid-derivation.

## 2. General bound, all homological dimensions — derived directly (not merely cited)

**Claim.** For finite `X,Y` in a common metric space `(M,d)` with (symmetric) Hausdorff distance `d_Haus(X,Y)=δ`, the persistence modules `H_k(Rips_•(X))` and `H_k(Rips_•(Y))` are `2δ`-interleaved, for every `k`. Consequently (isometry theorem, §0 item 3), `d_B(Dgm_k(Rips(X)), Dgm_k(Rips(Y))) ≤ 2δ`.

**Derivation (elementary, self-contained construction).** Since `\vec d(X,Y)≤δ`, choose for each `x∈X` a point `ψ(x)∈Y` with `d(x,ψ(x))≤δ` (exists by definition of directed Hausdorff distance as a max of achieved minima). Symmetrically choose `φ:Y→X` with `d(y,φ(y))≤δ`. For any simplex `σ={x_1,...,x_m}∈Rips_r(X)` (so `d(x_i,x_j)≤r` for all `i,j`), the images `ψ(x_i)` satisfy, by the triangle inequality,
```
d(ψ(x_i),ψ(x_j)) ≤ d(ψ(x_i),x_i) + d(x_i,x_j) + d(x_j,ψ(x_j)) ≤ δ + r + δ = r+2δ,
```
so `{ψ(x_1),...,ψ(x_m)} ∈ Rips_{r+2δ}(Y)`. This defines a simplicial map `Rips_r(X)→Rips_{r+2δ}(Y)` for every `r`, and symmetrically `Rips_r(Y)→Rips_{r+2δ}(X)` via `φ`. These two families of maps form a `2δ`-interleaving of the two Rips filtrations (standard verification: the required commutation with the filtration's internal structure maps holds because `ψ,φ` are single fixed maps applied at every scale, so composites land in the correctly-shifted term). Inducing on homology gives a `2δ`-interleaving of the persistence modules `H_k(Rips_•(X))`, `H_k(Rips_•(Y))`, for every `k`, and the isometry theorem converts this into `d_B(Dgm_k(X),Dgm_k(Y))≤2δ`. ∎

**Specialization to our setting.** Take `X=A(I)`, `Y=S_I`, both `⊆{0,1}^n` under `d_H`. Since `A(I)⊆S_I`, `\vec d(A(I),S_I)=0` (`HAUSDORFF_IDENTITY.md` §2, Step 2 — one may take `φ = \text{id}` exactly, no error at all in this direction), so the construction above needs `δ=\vec d(S_I,A(I))=ε̂(A,I)` only in the `S_I→A(I)` direction (`ψ` from §above), and `0` in the `A(I)→S_I` direction. A valid single `δ` for the interleaving must upper-bound *both* required shifts, so `δ=2ε̂(A,I)` (taking the larger of `0` and `2ε̂(A,I)`, since one direction needs shift `0`, which trivially also satisfies "shift `≤2ε̂(A,I)`"). This confirms, by direct substitution rather than by treating `A(I),S_I` as an unrelated generic pair:

> **`d_B(Dgm_k(Rips(A(I))), Dgm_k(Rips(S_I))) ≤ 2 ε̂(A,I)` for every `k`.**

**Status: KNOWN RESULT, directly applicable — the general machinery is not novel; the substitution into this specific pair `(A(I),S_I)` via the Hausdorff identity is a direct, unsurprising specialization, also not claimed as novel.**

## 3. The sharper, H₀-specific statement — the strongest safe statement for connectivity

The bound in §2 is symmetric-looking (`2ε̂`) but the *actual* situation for `(A(I),S_I)` is asymmetric, because one direction of the interleaving needs *no* shift at all (`A(I)→S_I` is exact, §2). Exploiting this asymmetry directly at the `H_0`/cluster-count level (not routed through the general bottleneck machinery, which would obscure it) gives a strictly more informative pair of statements.

**Theorem (asymmetric H₀ correspondence).** Let `∅≠A(I)⊆S_I⊆{0,1}^n`, `ε̂=ε̂(A,I)`. For every `r≥0`:

**(a) No false merges (exact, zero slack).** If `x,y∈A(I)` lie in the same `r`-cluster of `A(I)` (connected by a chain of points in `A(I)` with consecutive Hamming distances `≤r`), then `x,y` lie in the same `r`-cluster of `S_I`. *Proof*: the same chain, viewed as a chain of points in `S_I` (valid since `A(I)⊆S_I`), witnesses the same connectivity at the same radius `r` — no construction needed, immediate from the subset relation.

**(b) Guaranteed re-merge (with `2ε̂` slack, not less in general).** Let `φ:S_I→A(I)` send each `x∈S_I` to a nearest point of `A(I)` (achieving `d_H(x,φ(x))≤ε̂`, with `φ(x)=x` when `x∈A(I)` already). If `x,y∈S_I` lie in the same `r`-cluster of `S_I`, then `φ(x),φ(y)` lie in the same `(r+2ε̂)`-cluster of `A(I)`. *Proof*: for a chain `x=p_0,...,p_m=y` in `S_I` with consecutive distances `≤r`, `d_H(φ(p_i),φ(p_{i+1})) ≤ d_H(φ(p_i),p_i)+d_H(p_i,p_{i+1})+d_H(p_{i+1},φ(p_{i+1})) ≤ ε̂+r+ε̂`, so `φ(p_0),...,φ(p_m)` is a chain in `A(I)` with consecutive distances `≤r+2ε̂`, connecting `φ(x)` to `φ(y)`.

**Consequence.** `C_{A(I)}(r+2ε̂) ≤ C_{S_I}(r)` for all `r≥0` (each `S_I`-`r`-cluster maps, via `φ`, into a single `A(I)`-`(r+2ε̂)`-cluster, by (b); this cannot increase the count).

**Interpretation.** `A(I)` can only ever **under-connect** relative to `S_I` at the *same* radius `r` — it can *look* more fragmented than `S_I` really is (this is exactly the "observer-induced fragmentation" phenomenon, now proved to be the *only* kind of distortion possible at matched radius, not merely observed once), but it can **never fabricate a merge that isn't already true in `S_I` at that radius** (statement (a)). Any apparent fragmentation in `A(I)` is *guaranteed* to resolve — clusters that were truly one component in `S_I` are guaranteed to become one component again in `A(I)` — once the radius is loosened by `2ε̂`.

**Status: PROVED**, independently, by elementary chain arguments (no general machinery invoked) — and **brute-force verified**: 100 random `(S,A)` instances across `n=4..8` (`|S|` up to 40, `A` a random nonempty subset of `S`), every `r=0..n`, **zero failures** of claim (a), claim (b), or the consequence inequality (`scripts/h0_correspondence_verify.py`, output in `data/h0_correspondence_verify_output.txt`). A worked hand example in that output shows the phenomenon concretely: `S={0000,1100,1111}` (a true single cluster at `r=2`, `C_S(2)=1`), `A=\{0000,1111\}` (`ε̂=2`): raw `C_A(2)=2` (appears fragmented — the missing midpoint `1100` is exactly what would have connected them), while `C_A(2+2·2)=C_A(6)=1=C_S(2)` ✓, confirming re-merge at the guaranteed radius and no smaller guarantee is claimed.

This H₀-specific result is **strictly sharper and more interpretable** than the general §2 bound for the connectivity/cluster-spectrum question specifically (it gives a one-directional guarantee — no false merges, ever, at matched radius — that the symmetric bottleneck bound does not make explicit), and should be the paper's headline stability statement for `C_S(r)`/`C_A(r)`, with §2's general bound retained for higher-dimensional persistence (loops, voids) where no such asymmetric shortcut is available.

## 4. What may legitimately be claimed

- "If `ε̂(A,I)` is small, any cluster-count difference between `C_{A(I)}(r)` and `C_{S_I}(r)` **at radii separated by less than `2ε̂(A,I)`** cannot be trusted as reflecting `S_I`'s true structure — it may be pure observation artifact." (Direct reading of §3's consequence.)
- "`A(I)` cannot show a false merge relative to `S_I` at the same radius — any connectivity claim made from `A(I)` alone (`x,y` connected at radius `r`) is guaranteed true of `S_I` too." (§3(a), zero-slack, unconditionally.)
- "Bottleneck distance between the full persistence diagrams (any homological dimension) of `A(I)` and `S_I` is at most `2ε̂(A,I)`." (§2, general.)
- "Once instance-specific `ε̂(A,I)` is measured, a concrete numeric reliability scale (`2ε̂(A,I)`, or the sharper §3 statement for `H_0` alone) can be reported alongside any cluster-spectrum or persistence-diagram figure derived from `A(I)`."

## 5. What may NOT be claimed

- **Not** "the true cluster structure is recovered/reconstructed" — the bound controls *diagram distance* (or, for §3, cluster-*count* at a shifted radius), not homotopy-type or exact cluster-membership recovery. A homotopy-type reconstruction theorem (e.g. Niyogi–Smale–Weinberger-style) would need extra regularity on `S_I` (a positive-reach/feature-size condition) that random 3-SAT solution clusters are not known to satisfy — this was already flagged in Phase 1 `V2_DEFINITIONS.md` §2.3 and is reaffirmed here, now with the sharper §3 result in hand: even §3's exact "no false merge" guarantee does **not** imply cluster *sizes*, *shapes*, or higher connectivity (paths, cycles) are preserved — only that the coarse merge/split pattern is bounded as stated.
- **Not** "the persistence bound is tight" without further evidence — §2's constant `2` is the best *general* bound achievable by this construction technique for arbitrary `X,Y`; whether it is tight for the *specific* distribution of `(A(I),S_I)` pairs arising from real solvers on random 3-SAT is an empirical question, addressed in Part 10 (`EXPERIMENT_RESULTS.md`), not assumed here.
- **Not** "small `ε̂` guarantees small distortion in dimensions `k≥1` (loops, voids) at the sharper §3-style asymmetric rate" — the zero-slack asymmetric argument in §3 is specific to `H_0` (chains of pairwise-close points); no analogous zero-slack argument was found or is claimed for higher-dimensional features, which must fall back to the symmetric `2ε̂` bound of §2 only.
- **Not** a claim that this integration (Hausdorff identity + Rips stability + SAT solution-space sampling) is new *mathematics* — see `NOVELTY_CLASSIFICATION.md`; both §2 and §3's underlying techniques (interleaving constructions, chain arguments) are standard tools in persistent homology and metric geometry, applied here, not invented here.

## 6. Status labels

| Result | Label |
|---|---|
| General bound `d_B ≤ 2ε̂(A,I)`, all `k` (§2) | **KNOWN RESULT** (Chazal–de Silva–Oudot 2014 + isometry theorem, applied here by direct substitution) |
| Asymmetric H₀ correspondence, no-false-merge + guaranteed-re-merge-at-`2ε̂` (§3) | **PROVED** (elementary, self-contained, independently brute-force verified, 100/100 instances, 0 failures) |
| `C_S(r) = ` component count of `Rips_r(S)` under the paper's own Def. 2.6 convention (§1) | **PROVED** (trivial identification, stated for the record) |
