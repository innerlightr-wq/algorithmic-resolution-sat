# H0_SHARPNESS.md — Phase 3, Part 14

## Question

What is the smallest universal constant `c` such that, for `A⊆S` finite subsets of a metric space with `d_Haus(A,S)=ε`: connectivity in `S` at scale `r` implies corresponding connectivity in `A` by scale `r+cε`? Is `c=2` (proved achievable in `H0_THEOREM_AUDIT.md`) actually the smallest such constant, or can it be improved?

## Answer: `c=2` is sharp — in arbitrary metric spaces, and specifically in the Hamming cube

### Extremal construction

For any integers `r,ε≥1`, let `n=r+2ε` and, in `\{0,1\}^n`, define three disjoint coordinate blocks: `R` (`|R|=r`), `E_1` (`|E_1|=ε`), `E_2` (`|E_2|=ε`):
```
p = 0^n
q = 1 on R, 0 elsewhere              (d(p,q) = r)
a = p flipped on E_1                 (d(p,a) = ε)
b = q flipped on E_2                 (d(q,b) = ε)
S = {p,q,a,b},   A = {a,b}
```

**Verified computationally** (`scripts/h0_sharpness_extremal.py`, output `data/h0_sharpness_extremal_output.txt`) for `(r,ε)∈\{(1,1),(2,1),(3,2),(4,4),(5,3),(10,5),(1,10)\}`, all exact:
- `d(p,a)=d(q,b)=ε=d_\text{Haus}(A,S)` (so `a` is `p`'s unique nearest point in `A`, `b` is `q`'s unique nearest point in `A` — confirmed `d(p,a)<d(p,b)` and `d(q,b)<d(q,a)` in every case).
- `p,q` are directly `r`-connected in `S` (single edge, `d(p,q)=r`).
- **`d(a,b) = r+2ε` exactly**, in every tested case — because the three coordinate blocks `R,E_1,E_2` are pairwise disjoint, the three "legs" `a→p→q→b` accumulate additively with **no cancellation**: `a` and `b` disagree on all of `R` (since `a` matches `p=0` there and `b` matches `q=1` there), all of `E_1` (`a` flipped, `b` matches `p`'s original `0`), and all of `E_2` (`b` flipped, `a` matches `q`'s original `0` there) — `r+ε+ε` disagreements total, forced by construction, not a coincidence of this particular example.

### Why this proves sharpness

`A=\{a,b\}` has only one possible edge. So `a,b` are connected in `A`'s `r'`-cluster graph **if and only if `r'≥d(a,b)=r+2ε`** — at any `r'<r+2ε`, `a` and `b` are in *different* components of `A`, even though their preimages `p,q` are already in the *same* component of `S` at radius `r`. The guarantee "`C_A(r+2ε)≤C_S(r)`" is therefore attained with **equality, not slack**, on this family: the theorem's recovery radius cannot be lowered to `r+cε` for any `c<2` and remain true, because this example would then be a counterexample (at `r'=r+cε<r+2ε`, `a,b` would still be disconnected in `A` while already connected in `S` at `r`).

### Does the Hamming cube permit a sharper constant than arbitrary metric spaces? — **No**

This was the specific, non-obvious question the task flagged (do not assume the general bound is Hamming-sharp without checking). **The extremal construction is realized directly and exactly inside `\{0,1\}^n`** (not merely in some abstract or pathological metric space) — so the Hamming cube, despite being highly structured (vertex-transitive, integer-valued, graph-geodesic), does **not** admit any improvement over the general metric-space bound. The disjoint-coordinate-block trick is exactly what makes the cube "rich enough" to realize the worst case: with `n≥r+2ε` free coordinates, three independent "directions" of slack can always be laid out without interference, so no dimension-counting or combinatorial obstruction in the cube prevents the extremal configuration from existing.

### Scope of the sharpness claim

Sharpness is proved for the theorem **as a universal, worst-case statement over all `(S,A,r)`** — it does *not* claim every SAT instance realizes this worst case (empirically, in Phase 3's actual data, the bound holds with `0` violations across `349×~20` real checks in Phase 2 and is typically far from tight — e.g. the budget-trajectory instances in `BUDGET_TRAJECTORIES.md` show much better *practical* recovery than the worst-case `2ε` bound would suggest, since real SAT solution sets are not adversarially constructed). The extremal example is a **worst-case existence proof**, not a claim about typical SAT geometry.
