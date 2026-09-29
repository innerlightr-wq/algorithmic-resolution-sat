# ACCESSIBILITY_FRAMEWORK.md — Phase 2, Part 5

Formalizes the quantity `EXPERIMENT_PROTOCOL.md`/`EXPERIMENT_RESULTS.md` actually predict and test, with notation designed so that **retrospective** (post-reveal, uses `S_I`) and **prospective** (pre-reveal, Stage-A-only) quantities cannot be typographically confused with each other — this is the single most important anti-leakage safeguard at the *notation* level, requested explicitly by the task.

## 1. Base definition

For randomized solver `A`, instance `I`, budget `T` (e.g. restarts × max-flips, or sample count), and `x∈S_I`:
```
p_{A,T}(x | I) = P_{seed}( x ∈ A(I) ),
```
the probability, over `A`'s internal randomness (seed, restart schedule, tie-breaking — **not** over `I`, which is fixed), that a *single run* of `A` with budget `T` on `I` discovers `x` among its returned solutions. This is `V2_DEFINITIONS.md` §1.3's discovery/accessibility function, restated here with the estimation and leakage discipline made explicit.

## 2. Notation split: retrospective vs. prospective — made impossible to blur

Two **superscript tags**, `ᴿ` (retrospective) and `ᴾ` (prospective), are attached to every derived quantity in this framework. A quantity without a tag is not permitted to appear in any script or document past this point — untagged accessibility-related symbols are treated as a bug.

### 2.1 Retrospective quantities (`ᴿ`) — require `S_I`, computed only at/after Stage B

```
p̂ᴿ_{A,T}(x | I) = (1/K) Σ_{k=1}^K 1[x ∈ A_k(I)],   x ∈ S_I,
```
the Monte Carlo estimate of `p_{A,T}(x|I)` from `K` independent runs (seeds) `A_1(I),...,A_K(I)`, evaluated **only for `x` that are known members of `S_I`** — this requires `S_I` to already be enumerated, hence retrospective by construction (the index set `x∈S_I` is not available before Stage B).
```
Lᴿ_τ(A,I,T) = {x∈S_I : p̂ᴿ_{A,T}(x|I) ≤ τ}
```
the **retrospective low-accessibility region** at threshold `τ` — the task's requested `L_τ` object, tagged `ᴿ` because computing membership requires knowing all of `S_I` (to enumerate the `x`'s being thresholded) and requires the `K`-run estimate `p̂ᴿ`. **`Lᴿ_τ` is a diagnostic/analysis object computed after reveal — it is never an input to any predictor and never touches Stage A code.**

### 2.2 Prospective quantities (`ᴾ`) — Stage-A-legitimate, computed before `S_I` is enumerated

A prospective quantity may only be a function of: the CNF formula, solver trajectories/flips/restarts/clause-violation history, and the solver's own already-discovered solutions `A(I)` (or `A_1(I),...,A_K(I)` across repeated runs) — never of `S_I \ A(I)` or any statistic requiring full enumeration.
```
r̂ᴾ_{A,T}(y | I) = f( trajectory data involving y ),   y ∈ A(I) only,
```
a **prospective risk score**, defined *only* for already-found solutions `y∈A(I)` (not for arbitrary `x∈{0,1}^n`, and not for the unindexable set `S_I\A(I)` — see §3 for why the target domain is deliberately restricted to `A(I)`, not all of `S_I`). Candidate instantiations of `f` (§4) use only basin-size, restart-visit-density, discovery-flip-count, or found-neighbor-density — all computable from `A_1(I),...,A_K(I)` and solver-internal logs alone.

**Rule (enforced in code, not just in this document): any script that computes a `ᴾ`-quantity must not import, open, or call any function that touches full-`S_I` enumeration. `EXPERIMENT_PROTOCOL.md` §3 specifies this as a literal process/file-separation, not just a naming convention.**

## 3. Why the prospective target is "risk score per found solution," not "accessibility of arbitrary `x`"

A naive prospective analogue of `Lᴿ_τ` would be "predict, for every `x∈\{0,1\}^n`, whether `x∈S_I` and whether it will be missed" — but Stage A cannot even enumerate candidate `x`'s worth scoring without already having *some* proxy set to score, and scoring all `2^n` points is both computationally prohibitive for large `n` and conceptually circular (assigning a "miss risk" to a point not known to be a solution at all is not well-posed without first restricting to `S_I`, which is retrospective information).

**Resolution**: the prospective object is defined only over `A(I)` — for each *found* solution `y`, a risk score `r̂ᴾ(y|I)` estimating "how under-explored was `y`'s neighborhood" (§4 gives concrete instantiations). This is well-posed prospectively (needs only `y` and solver logs) and yields a **testable** retrospective hypothesis (§5): does high `r̂ᴾ(y|I)` predict a high density of *actually missed* solutions near `y`, once `S_I` is revealed? This reframing is what makes Part 6's experiment non-circular and well-defined — it was not obvious how to pose "prospective accessibility" without this restriction, and getting the restriction right is itself part of this phase's contribution (see `NOVELTY_CLASSIFICATION.md`: classified as **NEW SPECIALIZATION/INTERPRETATION** of the general accessibility-field idea, not new probability theory).

## 4. Candidate prospective risk scores `r̂ᴾ_{A,T}(y|I)`, `y∈A(I)`

All computed from `K` independent restart/seed runs of `A` on `I`, using only trajectory data, never `S_I`:

| Score | Definition | Rationale |
|---|---|---|
| `basin(y)` | count of the `K` runs whose final output equals `y` | small `basin(y)` ⟹ `y`'s region was rarely converged to ⟹ hypothesize under-sampled neighborhood |
| `visitdensity_ρ(y)` | count of runs whose trajectory passes within Hamming radius `ρ` of `y` at any point (not necessarily converging there) | measures total "search attention" paid to `y`'s neighborhood, independent of whether that attention culminated in landing exactly on `y` |
| `disc_flips(y)` | mean number of flips taken, across runs that found `y`, to first discover it | fast/easy discovery may indicate a "wide," easily-found region (more of its neighborhood plausibly also easy, i.e. low risk); slow/rare discovery may indicate a narrow basin with more undiscovered neighbors |
| `foundneighbor(y)` | `\|\{y'∈A(I): y'≠y, d_H(y,y')≤ρ\}\|` | uses only `A(I)` itself (no solver-internal trajectory data needed) — the simplest legitimate prospective feature, doubles as **Baseline 4** in `EXPERIMENT_PROTOCOL.md` Part 8 |

**Primary hypothesis for Part 6**: `r̂ᴾ(y|I) = -basin(y)` (or `-visitdensity_ρ(y)`, low search-attention ⟹ high predicted risk) correlates, across found solutions `y`, with the true local density of missed solutions near `y` — tested non-circularly because `basin`/`visitdensity` are properties of *solver dynamics*, not of `y`'s geometric features the way Hamming weight was for the January draft's biased sampler (Phase 1 `ORIGINAL_EXPERIMENT_AUDIT.md` §3).

## 5. The retrospective target the prospective score is tested against

After Stage B reveal, define, for each `y∈A(I)` and a fixed radius `ρ` (chosen from `S_I`'s own geometry, e.g. the median nearest-neighbor distance within `S_I` — **chosen on the training split only**, per `EXPERIMENT_PROTOCOL.md` §4, never re-tuned on the test split):
```
missᴿ_ρ(y | I) = |{ x ∈ M_A(I) : d_H(x,y) ≤ ρ }|
```
the count of truly-missed solutions within radius `ρ` of found solution `y` — a purely retrospective quantity (needs `S_I` and `A(I)`, computed at Stage B only). **This — not `Lᴿ_τ` directly — is the primary evaluation target** used in `EXPERIMENT_PROTOCOL.md`/`EXPERIMENT_RESULTS.md`: test whether `r̂ᴾ(y|I)` (frozen before reveal) correlates with `missᴿ_ρ(y|I)` (computed only after reveal) across all `y∈A(I)`, per instance, aggregated with instance as the independent unit (per the task's Part 9 instruction).

`Lᴿ_τ(A,I,T)` (§2.1) is retained as a secondary/diagnostic retrospective quantity — useful for characterizing *how much* of `S_I` is genuinely low-accessibility in absolute terms (e.g. reporting `|Lᴿ_τ|/|S_I|` per cell), but is **not** the primary predictive-test target, since nothing prospective can be compared against it directly (its domain is all of `S_I`, not just `A(I)`) without first solving the "score arbitrary `x`" problem that §3 explains is not well-posed prospectively.

## 6. Summary of the anti-leakage discipline this notation enforces

| Symbol | Tag | Computable at Stage A? | Domain |
|---|---|---|---|
| `p_{A,T}(x\|I)` | (theoretical, untagged — never estimated directly) | — | `x∈S_I` |
| `p̂ᴿ_{A,T}(x\|I)` | ᴿ | **No** | `x∈S_I` |
| `Lᴿ_τ(A,I,T)` | ᴿ | **No** | subset of `S_I` |
| `r̂ᴾ_{A,T}(y\|I)` | ᴾ | **Yes** | `y∈A(I)` only |
| `missᴿ_ρ(y\|I)` | ᴿ | **No** | `y∈A(I)`, counts into `S_I\A(I)` |

Any script that computes both a `ᴾ` and a `ᴿ` quantity in the same process **must** freeze and hash all `ᴾ` outputs to disk before any `ᴿ` computation begins — enforced structurally in `EXPERIMENT_PROTOCOL.md` §3 (Stage A / Stage B as literally separate script invocations, not just separate functions).
