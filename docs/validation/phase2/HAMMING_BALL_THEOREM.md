# HAMMING_BALL_THEOREM.md — Exact Hamming-ball-intersection theorem (Phase 2, Part 1)

Re-derives the Phase-1 correction from first principles, independent of the earlier derivation, resolving open/closed and strict/non-strict ambiguity completely. Phase-1's `AUDIT.md` open-ball formula is **confirmed correct** by this independent derivation; this document adds the closed-ball case (not derived in Phase 1) and a sharper diagnosis of exactly where the January paper's proof fails at the boundary.

---

## 1. The central combinatorial lemma

**Lemma.** Let `x,y ∈ {0,1}^n` with `d_H(x,y) = D ≥ 1`. Then
```
min_{z ∈ {0,1}^n} max(d_H(x,z), d_H(y,z)) = ⌈D/2⌉.
```

**Proof.**

*Lower bound.* For any `z`, the triangle inequality gives `d_H(x,z) + d_H(y,z) ≥ d_H(x,y) = D`. Writing `a = d_H(x,z)`, `b = d_H(y,z)`, we have `a+b ≥ D`, hence `max(a,b) ≥ (a+b)/2 ≥ D/2`. Since `a,b` are non-negative integers, `max(a,b)` is an integer, so `max(a,b) ≥ ⌈D/2⌉`.

*Achievability.* Let `Δ ⊆ {1,...,n}`, `|Δ|=D`, be the coordinates where `x,y` differ. For any integer `k` with `0 ≤ k ≤ D`, define `z_k` by: on `Δ`, agree with `y` on exactly `k` of the `D` coordinates (any `k`-subset) and agree with `x` on the remaining `D-k`; off `Δ` (where `x=y` already), set `z_k = x = y`. Then `d_H(x,z_k) = k` (differs from `x` exactly on the `k` coordinates set to `y`'s value) and `d_H(y,z_k) = D-k` (differs from `y` on the other `D-k`). Taking `k = ⌈D/2⌉` gives `d_H(x,z_k) = ⌈D/2⌉`, `d_H(y,z_k) = ⌊D/2⌋`, so `max(d_H(x,z_k), d_H(y,z_k)) = ⌈D/2⌉`. This achieves the lower bound. ∎

This is the exact discrete analogue of "the midpoint of a geodesic segment," except that when `D` is odd, no single point achieves `a=b` exactly (`⌈D/2⌉ ≠ ⌊D/2⌋`) — the hypercube has *near-midpoints*, not exact midpoints, for odd `D`. This is precisely the fact Theorem 2.1's proof needed and did not have (see §4).

## 2. Open-ball theorem

**Theorem (open balls).** For `x,y∈{0,1}^n`, `D=d_H(x,y)>0`, real `ε>0`:
```
B_ε(x) ∩ B_ε(y) = ∅   ⟺   ε ≤ ⌈D/2⌉.
```

**Proof.** `B_ε(x)∩B_ε(y) ≠ ∅ ⟺ ∃z: d(x,z)<ε ∧ d(y,z)<ε ⟺ ∃z: max(d(x,z),d(y,z)) < ε`. Since the minimum of `max(d(x,z),d(y,z))` over all `z` is exactly `⌈D/2⌉` (Lemma §1), such a `z` exists iff `⌈D/2⌉ < ε`. So `B_ε(x)∩B_ε(y) ≠ ∅ ⟺ ε > ⌈D/2⌉`, and taking the complement, `B_ε(x)∩B_ε(y) = ∅ ⟺ ε ≤ ⌈D/2⌉`. ∎

## 3. Closed-ball theorem

**Theorem (closed balls).** For `x,y∈{0,1}^n`, `D=d_H(x,y)>0`, real `ε>0`:
```
B̄_ε(x) ∩ B̄_ε(y) = ∅   ⟺   ε < ⌈D/2⌉.
```

**Proof.** Identical to §2 with `≤` in place of `<` throughout: `B̄_ε(x)∩B̄_ε(y) ≠ ∅ ⟺ ∃z: max(d(x,z),d(y,z)) ≤ ε ⟺ ⌈D/2⌉ ≤ ε`. Complement: `= ∅ ⟺ ε < ⌈D/2⌉`. ∎

**The boundary `ε = ⌈D/2⌉` is the single point where open and closed balls disagree**: open balls are still disjoint there; closed balls already intersect (at the minimizing point `z` from §1, which sits at distance exactly `⌈D/2⌉` from both `x` and `y` — too far for the open ball, exactly on the boundary of the closed one).

## 4. Exact diagnosis of the January theorem, refined

The January paper states (open balls, its Definition 2.2): `B_ε(x)∩B_ε(y)=∅ ⟺ ε<D/2`. Comparing to §2's `ε≤⌈D/2⌉`, there are **two distinct defects**, not one:

1. **Magnitude defect (D odd).** `⌈D/2⌉ = D/2 + 1/2` when `D` is odd. The paper's threshold `D/2` is too small by exactly `1/2`, for every odd `D`. This was the defect identified and verified in Phase 1.
2. **Boundary strictness defect (all D, including D even).** Even when `D` is even, so `⌈D/2⌉ = D/2` and the *magnitude* matches, the paper's inequality is strict (`ε<D/2`) while the correct one is non-strict (`ε≤D/2`). This means the paper mis-predicts the single boundary case `ε=D/2` exactly: the paper's biconditional says `ε<D/2` is required for disjointness, so at `ε=D/2` it predicts the balls **already intersect**; the correct formula (§2) says open balls are **still disjoint** at `ε=D/2` (they only start intersecting once `ε` exceeds `D/2`). **This defect exists for every `D`, even and odd alike, and was not separately isolated in Phase 1's audit** (Phase 1 noted it only informally, in passing, as a "second, smaller defect... masked by the bigger defect"). Verified explicitly: `n=2`, `x=(0,0)`, `y=(1,1)`, `D=2`, `ε=1.0` — `B_1(x)={(0,0)}`, `B_1(y)={(1,1)}`, disjoint, confirmed by brute force; the paper's own formula predicts non-disjoint here since `1.0 ⊀ 1.0`.

Both defects trace to the same root cause identified in Phase 1: the proof's forward direction assumes an exact real-valued midpoint `m` with `d(x,m)=d(y,m)=D/2`, which the discrete cube does not provide even when `D` is even and `D/2` is an integer — what the cube provides instead is the *pair* of near-midpoints at `(⌈D/2⌉,⌊D/2⌋)`, and the correct threshold is governed by the **larger** of that pair, `⌈D/2⌉`, together with the correct (non-strict, for open balls) boundary convention.

## 5. General-metric-space direction that remains valid, restated precisely

The (⇐) direction of the January Theorem 2.1 — `ε<D/2 ⟹ B_ε(x)∩B_ε(y)=∅` — is a correct, general fact about *every* metric space (pure triangle-inequality argument, Phase 1 `AUDIT.md` §1.2). It is **consistent with, but not tight for**, the Hamming-cube result here: since `⌈D/2⌉ ≥ D/2` always, `ε<D/2 ⟹ ε<⌈D/2⌉+something` trivially implies disjointness via the correct formula too — the general direction is simply a weaker, always-true special case, never contradicted by §2–3.

## 6. Exact wording safe for V2

> **Proposition (Hamming-ball intersection, exact).** Let `x,y∈{0,1}^n` with `d_H(x,y)=D>0`, and let `ε>0` be real.
> - Open balls `B_ε(z)={w:d_H(z,w)<ε}`: `B_ε(x)∩B_ε(y)=∅ ⟺ ε≤⌈D/2⌉`.
> - Closed balls `B̄_ε(z)={w:d_H(z,w)≤ε}`: `B̄_ε(x)∩B̄_ε(y)=∅ ⟺ ε<⌈D/2⌉`.
>
> In particular, for **odd** `D` the disjointness threshold is `(D+1)/2`, not `D/2`; for **even** `D` the threshold value coincides with `D/2` but the boundary case `ε=D/2` must be handled with the stated (non-)strictness, not the naive continuous-space convention.

This wording should replace the January Theorem 2.1 wherever the paper needs a Hamming-cube-specific distinguishability statement (per `V2_OUTLINE.md` §2, background material, de-emphasized from headline status).

## 7. Brute-force verification

Script: `scripts/hamming_ball_theorem_verify.py`. Full output: `data/hamming_ball_theorem_verify_output.txt`.

- **`n=1..6`: exhaustive over every pair** `x,y∈{0,1}^n` (`1+6+28+120+496+2016 = 2667` pairs), every `ε` in a grid of integers, half-integers, and values `±0.01` around both `⌈D/2⌉` and `D/2` for each pair's `D`.
- **`n=7..10`: one representative pair per achievable `D=1,...,n`, plus 5 additional randomly-chosen pairs at the same `D`** (transitivity spot-check — the hypercube's distance-transitivity, i.e. that ball-intersection outcomes depend only on `D` and not on which specific pair realizes it, is a property of the hypercube's automorphism group and was *checked*, not assumed: **0 transitivity failures** across all `(n,D)` combinations tested, `n=1..10`).
- **Total: 45,393 `(n,D,ε)` test cases. Open-ball formula: 45,393/45,393 match (100.0000%). Closed-ball formula: 45,393/45,393 match (100.0000%). Zero mismatches for either formula.**
- Explicit boundary demonstrations (script output, reproduced above in §4) confirm both defects in the January formula concretely: `D=2` (even) boundary case at `ε=1.0`, and `D=1,3` (odd) magnitude defect.

## 8. Status label

**PROVED** (elementary combinatorial proof, §1–3, independently re-derived from Phase 1 without assuming its conclusion; exhaustively verified by brute force for `n≤6` and by representative+transitivity-spot-checked sampling for `n=7..10`, 45,393/45,393 cases, zero failures).
