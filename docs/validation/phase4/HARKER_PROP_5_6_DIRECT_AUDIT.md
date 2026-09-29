# HARKER_PROP_5_6_DIRECT_AUDIT.md — Phase 4, Part 2

## Correct bibliographic identification (the ID supplied to this phase was wrong)

The arXiv identifier given for this task (`1806.10736`) was checked in Phase 3 and belongs to an unrelated paper ("Risk-averse estimation..." by M. Brand). **The correct identifier, found via live search and confirmed by reading the actual PDF's title page, is:**

> Shaun Harker, Miroslav Kramár, Rachel Levanger, Konstantin Mischaikow. **"A Comparison Framework for Interleaved Persistence Modules."** arXiv:1801.06725v1 [math.AT], posted 20 Jan 2018. Published in *Journal of Applied and Computational Topology* 3(1–2):85–118, 2019 (Springer, DOI 10.1007/s41468-019-00026-x).

PDF fetched directly (not via secondary description), saved locally, converted to text with `pdftotext`, and read in full for the relevant sections (§5.2.1, the Lemma 5.7/5.10 proofs, and the surrounding definitions). 31 pages total.

## Exact statement of Proposition 5.6

**Definition 5.5** (their δ-approximation — read verbatim from the PDF): *"Let `(X,d)` be a finite metric space. A subset `Y⊂X` is a δ-approximation of `X` if for every `x∈X` there exists a `y∈Y` such that `d(x,y)≤δ`."*

**This is, precisely, our setup**: `Y=A`, `X=S`, `δ=ε=d_\text{Haus}(A,S)` — their "δ-approximation" condition is word-for-word the definition of directed Hausdorff distance from `X` to `Y` being `≤δ`, which (since `Y⊆X`, exactly our `A⊆S`) is exactly our `HAUSDORFF_IDENTITY.md` §2 setup.

**Rips complex convention (critical — must be tracked explicitly)**: their paper states *"`[x,y]` is an edge in `R(Y,t)` if and only if `d(x,y)≤2t`"* — **their parameter `t` is HALF our radius `r`** (`r=2t`). This is exactly the kind of convention slippage flagged as a risk in Phase 2's `PERSISTENCE_STABILITY.md` §1 — tracked explicitly below.

**Proposition 5.6** (verbatim): *"If `(X,d)` is a finite metric space and `Y` is a δ-approximation of `X`, then the following approximations hold. (i) The persistence modules `(M^R(Y), M^R(X))` are `(τ,σ)`-interleaved, where `τ(t)=t` and `σ(t)=t+δ`. (ii) There exists a matching [...] persistence-diagram-level consequence [...]"*

## The proof, read in full, and its exact correspondence to our theorem

The proof constructs two maps:
- `φ_t := ι_{t*}: H_*(R(Y,t)) → H_*(R(X,t))`, induced by the **inclusion** `ι_t: R(Y,t)↪R(X,t)` — **at the same parameter `t`, zero shift.**
- `ψ_t := γ̃_{t*}: H_*(R(X,t)) → H_*(R(Y,t+δ))`, induced by a map `γ:X→Y` with `d(x,γ(x))≤δ` for all `x` (their **Lemma 5.7**) — a nearest-point-style map, exactly our `φ:S→A`.

**Lemma 5.7's proof, quoted verbatim, is the identical triangle-inequality computation used in our theorem**: *"`d(γ(x),γ(y)) ≤ d(γ(x),x)+d(x,y)+d(y,γ(y)) ≤ δ+2t+δ = 2(t+δ)`"* — **this is our `ε+r+ε` computation exactly**, written in their `t`-parametrized convention (`d(x,y)≤2t` is their edge condition, giving `2(t+δ)` as the new edge condition at the shifted parameter).

## Translating their result into our convention

| Harker et al. (their `t`, edge iff `d≤2t`) | Our convention (radius `r`, edge iff `d≤r`) |
|---|---|
| `Y⊆X`, δ-approximation, `δ` | `A⊆S`, `ε=d_\text{Haus}(A,S)` |
| `φ_t`: `R(Y,t)→R(X,t)` (inclusion, shift `0`) | `A`'s `r`-cluster graph includes into `S`'s `r`-cluster graph at the **same** `r` (shift `0`) — **exactly `H0_THEOREM_AUDIT.md` claim (a)** |
| `ψ_t`: `R(X,t)→R(Y,t+δ)` (nearest-point map, shift `+δ` in `t`) | Since `r=2t`, a shift of `δ` in `t` is a shift of **`2δ=2ε`** in radius `r` — `S`'s `r`-connectivity is recovered in `A` by radius `r+2ε` — **exactly `H0_THEOREM_AUDIT.md` claim (b)** |
| Result stated for **all homological dimensions** (`H_*`, general persistence modules `M^R`) | Our claims (a),(b) are stated **only for `H_0`** (connected components) |

**Once the `t↔r/2` convention is translated, Proposition 5.6(i) is, exactly, our asymmetric theorem — generalized to all homological dimensions, and stated in persistence-module/interleaving language rather than elementary connected-component/chain language.** Restricting Proposition 5.6(i) to `H_0` (where `H_0(R(Y,t))` counts connected components of `R(Y,t)`'s `1`-skeleton — a standard, immediate fact, not something Harker et al. need to say explicitly) and unpacking the interleaving maps `φ_t,ψ_t` into elementary chain-connectivity language recovers claims (a) and (b) **verbatim**, including the exact `+2ε` (not `+3ε`, not any other constant) shift.

## What is NOT addressed by this paper

- **No sharpness/tightness discussion.** A full-text search for "sharp," "tight," "optimal," "cannot be improved," "best possible" near Proposition 5.6 found nothing relevant — the one "optimal" occurrence in the paper (§5.2.3) explicitly disclaims optimality for a *different*, later multiscale-subsampling result, and does not address Proposition 5.6 itself. **The sharpness of the `2ε` constant (Phase 3 `H0_SHARPNESS.md`) is not established, discussed, or claimed anywhere in this paper.**
- **No explicit `r<ε` vs. `r≥ε` case analysis** of when whole `S`-components can go unrepresented in `A` (Phase 3's `FRAGMENTATION_THEOREM.md` threshold proposition) — Proposition 5.6 is a single, all-scales-at-once interleaving statement; the itemized "what exactly can go wrong below the approximation radius" breakdown is not spelled out in what was read.
- **No Hamming-cube-specific discussion** — the paper works with arbitrary finite metric spaces throughout; no combinatorial cube-specific content was found.

## Verdict for this document

`H0_THEOREM_AUDIT.md`'s claims (a) and (b), as stated and proved independently in Phase 2/3, are **confirmed — by direct reading of the primary source, not secondary citation — to be a direct, essentially immediate corollary of Harker, Kramár, Levanger, Mischaikow (2018/2019), Proposition 5.6(i)**, specialized from general persistence modules to `H_0` and restated in elementary language. This is a **stronger and more definitive** conclusion than Phase 3's hedged "very likely, unconfirmed" — Phase 3's caution was warranted (the match was not yet verified) and is now resolved. See `HARKER_COMPARISON_MATRIX.md` for the full itemized classification.
