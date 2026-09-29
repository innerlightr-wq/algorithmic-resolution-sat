# COVERAGE_RESOLUTION_THEOREM.md — Phase 2, Part 4

Upgrades Phase 1's two isolated witness examples (`V2_THEOREMS.md` T6) to genuine, closed-form, verified **families** indexed by `n` (and, for Family B, by the code parameter `m`), as requested.

## 1. Family A — coverage → 1 while resolution → worst-possible, simultaneously

**Construction**, for each `n≥1`:
```
S_n = {0^n} ∪ {weight-1 vectors of length n} ∪ {1^n}     (|S_n| = n+2)
A_n = S_n \ {1^n}                                          (|A_n| = n+1)
```

**Closed form (PROVED, elementary):**
```
Cov(A_n, S_n)      = (n+1)/(n+2)  → 1  as n→∞
ε̂(A_n, S_n)        = n-1                                  (distance from the omitted point 1^n to its nearest neighbor in A_n, a weight-1 vector, is n-1)
ε̂(A_n,S_n)/diam(S_n) = (n-1)/n   → 1  as n→∞
```

*Proof.* `Cov` is immediate from set sizes. For `ε̂`: every point of `A_n` other than `1^n` (which is excluded) is at Hamming distance `≥n-1` from `1^n` — the weight-1 vectors are at distance exactly `n-1` from `1^n`, and `0^n` is at distance `n`; the minimum over `A_n` is thus `n-1`, achieved by any weight-1 vector, and this is also the maximum over `x∈S_n` of the nearest-`A_n` distance (every other point of `S_n` is in `A_n` itself, distance `0`), so `ε̂ = n-1` exactly. `diam(S_n)=n` (distance from `0^n` to `1^n`). ∎

**Verified** (`scripts/coverage_resolution_families.py`, output in `data/coverage_resolution_families_output.txt`) for `n∈{5,10,20,50,100,500}`: closed-form and brute-force values match exactly (`match=True`) at every `n` tested, including the asymptotic trend — coverage rises from `0.857` (`n=5`) to `0.998` (`n=500`) while normalized `ε̂/n` rises from `0.80` to `0.998` **in lock-step**, both approaching `1`.

**Interpretation.** This is not merely "an example" — it is a one-parameter family with a closed-form, monotonically worsening trade-off: coverage can be made arbitrarily close to `1` (miss an arbitrarily small *fraction* of solutions) while the resolution is *simultaneously* arbitrarily close to the worst possible value on the ambient diameter — because the single missed point is an outlier maximally far from everything else in `A_n`. **A single well-placed miss, however rare in relative terms, can be arbitrarily geometrically catastrophic.**

## 2. Family B — coverage → 0 while resolution stays bounded (in fact improves in normalized terms)

**Construction**, for `m=3,4,5,...`, `n=2^m-1`:
```
S_n = {0,1}^n                              (full Hamming cube)
A_n = binary Hamming code of length n      (perfect code; |A_n| = 2^n/(n+1))
```

**Closed form (STANDARD coding theory, not proved here — cited and verified computationally, §2.1):**
```
Cov(A_n,S_n) = |A_n|/2^n = 1/(n+1)  → 0  as n→∞ (exponentially in m, since n=2^m-1)
ε̂(A_n,S_n)   = 1                                     (CONSTANT — does not grow with n)
ε̂(A_n,S_n)/n = 1/n → 0  as n→∞
```

### 2.1 Verification method and why it scales past brute force

The Hamming code is defined via its parity-check matrix `H` (an `m×n` matrix whose columns are, in order, all `2^m-1` distinct nonzero binary vectors of length `m` — `scripts/coverage_resolution_families.py::hamming_parity_check_matrix`). Covering radius `=1` is verified **exactly** (not merely sampled) per point via **syndrome decoding**: for any `v∈{0,1}^n`, compute `syndrome = Hv mod 2`; if zero, `v` is itself a codeword (distance `0`); if nonzero, the syndrome value (read as an `m`-bit integer, `1..n`) identifies a *unique* column of `H` — flipping that one coordinate is checked (not assumed) to zero the syndrome, certifying distance exactly `1`. This is `O(nm)` per point, so it scales to `n` far beyond brute-force enumeration's reach.

- `n=7` (`m=3`) and `n=15` (`m=4`): **exhaustive** — every one of `2^7=128` and `2^15=32768` points checked, maximum distance found `=1` in both cases (i.e. **every single point of the cube**, not a sample, confirmed within distance 1 of the code).
- `n=31` (`m=5`) and `n=63` (`m=6`): exhaustive enumeration is infeasible (`2^31`, `2^63` points); **200,000 uniformly random points each** checked, each via the same *exact* (not approximate) syndrome computation — maximum distance found `=1` for all sampled points in both cases. The claim that this holds for the *entire* cube (not just the sample) follows from the standard analytic argument restated in §2.2, not from the sampling — the sampling is a spot-check/sanity-check on the construction's correctness, not the proof.
- At `n=63`, `|A_n| = 2^{57} ≈ 1.44×10^{17}` — printed exactly (Python arbitrary-precision integers), illustrating how extreme the coverage collapse becomes (`Cov = 1/64 ≈ 0.0156`) while `ε̂` remains exactly `1`.

### 2.2 Why covering radius is exactly 1 for every `n=2^m-1` (standard fact, cited)

By construction, the `2^m-1` columns of `H` are *all* the nonzero vectors of `{0,1}^m` — i.e. every possible nonzero syndrome value corresponds to exactly one column, hence exactly one single-coordinate flip. So every `v∈\{0,1\}^n` is either a codeword (syndrome `0`) or exactly one flip away from one (syndrome matches a unique column) — covering radius `≤1`, and `=1` exactly since the code is a proper subset (`n≥3`). This is the textbook definition of a **perfect code** (packing radius `=` covering radius `=1`) — standard material (e.g. Cohen–Honkala–Litsyn–Lobstein, *Covering Codes*, already cited in Phase 1 `PRIOR_ART.md` §1; also the classical Hamming/Golay perfect-code classification, van Lint–Tietäväinen). **Not re-derived as new — restated here only to make the family's correctness self-contained and to justify why the syndrome-decoding verification method in §2.1 is guaranteed to find distance `≤1` everywhere, which is exactly what was checked and confirmed.**

## 3. Normalization discussion (as requested)

Three natural normalizations of `ε̂` were considered:
- **Raw `ε̂`** (Hamming distance, un-normalized): appropriate when comparing algorithms/instances at *fixed* `n` (as the January paper's Table 1 does). Not comparable across different `n` — Family B shows raw `ε̂` can stay flat (`=1`) while `n` grows, which would look like "resolution isn't degrading" in absolute terms even as coverage collapses; only the *coverage* axis moves in that family.
- **`ε̂/n`** (normalized by ambient dimension): appropriate for cross-`n` comparison of "how much of the ambient space's extent" is being missed. This is the normalization the January paper's own Definition 3.4 (`ε̃`) already uses.
- **`ε̂/diam(S_I)`** (normalized by the *solution set's own* diameter, not the ambient cube): arguably more meaningful than `ε̂/n` when `S_I` itself is far from filling the cube (as is typical for SAT solution sets — `diam(S_I)` can be much less than `n`), since it asks "how much of the solution set's *own* geometric extent is unresolved" rather than "how much of the whole cube." **Recommend `ε̂/diam(S_I)` as the primary normalized quantity for V2**, with raw `ε̂` retained for same-`n` comparisons (as in the existing Tables) and `ε̂/n` demoted to a secondary/legacy quantity (kept only for continuity with the January paper's Def. 3.4). Family A was reported in both `ε̂/n` and (implicitly, since `diam(S_n)=n` there) `ε̂/diam` — they coincide for Family A because the star construction's diameter equals `n`; Family B's `diam(S_n)=n` too (full cube), so both normalizations coincide for both families here. A case where they would *diverge* (`diam(S_I)≪n`) is exactly the common SAT case (solutions clustered in a small sub-cube) — worth a dedicated small example in V2 if this normalization choice is adopted, not constructed here (out of scope for this pass).

## 4. Does ambient dimension `n` create trivial constraints?

Yes, two, both already known and both respected by the constructions above, stated explicitly per the task's request:
- **`ε̂ ≤ diam(S_I) ≤ n`** (Phase 1 `AUDIT.md` §2, Proposition 3.1, on the `A(I)≠∅` branch) — a hard ceiling on raw `ε̂`. Family A achieves this ceiling in the limit (`ε̂=n-1→` effectively saturating it, off by exactly the one unit reserved for `A(I)` itself being nonempty near the outlier's antipode).
- **`Cov(A,I) > 0` whenever `A(I)≠∅`** (trivial, since `A(I)⊆S_I` nonempty implies at least one solution is found) — coverage can be driven arbitrarily close to `0` (Family B, `1/(n+1)→0`) but never reaches exactly `0` under this convention; this matches `HAUSDORFF_IDENTITY.md` §3's recommendation to keep `A(I)=∅` as a categorical case, separate from the numeric coverage scale.

No other trivial `n`-dependent constraint was found that limits how extreme the two families' divergence can be — both families' key quantities (`Cov→1` & `ε̂/n→1` for A; `Cov→0` & `ε̂` constant for B) are shown to be simultaneously achievable in the limit, confirming Phase 1's qualitative claim with genuine asymptotic families rather than single data points.

## 5. Connections to standard literature — separated from the SAT interpretation

| Fact | Label |
|---|---|
| `ε̂(A,I)` is the covering radius of `A(I)` as a subset covering `S_I` (Hamming metric) | **STANDARD** (coding theory, restricted to a subset of the ambient space rather than the whole space — Phase 1 `PRIOR_ART.md` §1) |
| `A_n` is an `r`-net of `S_I` for `r=ε̂(A_n,S_n)` | **STANDARD** (epsilon-net / metric-entropy terminology, Kolmogorov) |
| Perfect binary Hamming codes have covering radius `=` packing radius `=1`, size `2^n/(n+1)` | **STANDARD** (classical coding theory; Hamming 1950, covering-codes literature) |
| A covering-radius-`1` code is exactly a **dominating set** of the hypercube graph `Q_n` (every vertex is the codeword itself or adjacent to one) | **STANDARD** (graph domination ≡ covering radius 1 for a binary code is a direct translation, not a new observation) — the perfect Hamming code, for `n=2^m-1`, in fact achieves the **exact domination number** `γ(Q_n) = 2^n/(n+1)` of the hypercube graph, a known extremal result for this special family of `n` |
| Family A's star-plus-outlier construction; Family B's application to SAT-solution-space coverage/resolution trade-offs specifically | **SAT-INTERPRETATION** — the *construction* (Family A) and the *framing* ("this is what a SAT solver's blind spot could look like") are this project's contribution; the underlying set-theoretic/coding facts are not |
| Deterministic inequality bounding `Cov(A,I)` from below given `ε̂(A,I)` and *no other structure on `S_I`* | **Does not exist** — Families A and B together constitute a proof by exhibition that no such inequality can hold in general (formalized as Theorem T6 in Phase 1 `V2_THEOREMS.md`, now with families rather than isolated points) |

## 6. Status labels

| Result | Label |
|---|---|
| Family A closed-form coverage/`ε̂` formulas | **PROVED** (elementary, verified `n∈{5,...,500}`, exact match) |
| Family B coverage formula `1/(n+1)` | **STANDARD** (code cardinality is a textbook fact, `\|Hamming code\|=2^n/(n+1)`) |
| Family B covering radius `=1` for all `n=2^m-1` | **STANDARD**, restated (§2.2), verified computationally: exhaustive at `n=7,15`; exact-per-point sampled verification (200,000 points, zero counterexamples) at `n=31,63` |
| No deterministic `Cov` vs. `ε̂` inequality exists without extra structure on `S_I` | **PROVED** by exhibition (Families A, B, generalizing Phase 1's T6 from isolated points to full asymptotic families) |
| Recommended normalization `ε̂/diam(S_I)` for V2 | Design recommendation, not a theorem |
