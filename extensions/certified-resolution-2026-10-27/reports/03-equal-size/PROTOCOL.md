# Equal-size certified comparison — protocol, dated 2026-10-27

Frozen **before any new equal-size measurement outcome existed**. The cohort
rule, the subsampling rule, the seeds, the bound-transfer mathematics, the
classification rule and the budgets below were all written down first; §4's
method choice was fixed from the *completed* optimization benchmark and before
`prepare_eq.py` or `run_eq.py` were ever run against this cohort.

Scope: `equal-size-certification-2026-10-27/` only. The original audit,
`continuation-2026-10-27/` and `optimization-2026-10-27/` are preserved. No
repository or manuscript is modified; nothing is committed, pushed or
published; instance sizes are not increased.

Read-only reference: <https://github.com/innerlightr-wq/algorithmic-resolution-sat>
(local clone at `../repo`, commit `2bef5a81a1d8a0cefa780d83d947c998533effd5`).

---

## 1. The question, stated precisely

The ordering audit (`../optimization-2026-10-27/data/ordering_audit.csv`)
found, over **32 instances with certified records on both solver sides**:

* **31** certified `ε_C > ε_W`,
* **1** certified equality,
* **0** certified `ε_W > ε_C`, **0** unresolved,
* WalkSAT's recorded set is larger in **31 of the 32** (typically 150 vs 40),
* and the historical equal-size comparison carries **no certified results** at
  all, because the original protocol ran it with proofs disabled.

**The question:** does the resolution advantage persist after matching the
number of distinct solutions in the two recorded sets?

**What this examines:** the geometry of the *existing recorded sets* after
controlled subsampling. It does **not** establish an intrinsic solver ranking,
equal computational effort, or uniform sampling from the full solution space.
The two sets were produced by different procedures under different budgets, and
subsampling one of them does not retroactively equalise those procedures.

**The coverage fact, stated exactly.** Coverage is `|A| / |S_I|`. On the **same**
formula `I`, two observed sets of equal cardinality have **equal coverage
fractions**, because `|S_I|` is one and the same constant in both ratios. This
holds without knowing `|S_I|`. It does **not** mean either fraction has been
computed: no coverage value is reported anywhere here, and none can be without
`|S_I|`.

**Monotonicity applies to inclusion, not to cardinality.** For `B ⊆ A`,
`ε(A) ≤ ε(B)`: adding solutions to a *particular* set cannot worsen its
resolution. A larger set need **not** have better resolution than an unrelated
smaller one, and `src/test_eq.py` contains an explicit control exhibiting a
7-element set with strictly worse resolution than a 2-element set on the same
space.

---

## 2. Cohort — rule R-EQ, frozen before measurement

From the 32 certified `W`-vs-`C` pairs, group by `(n, density)`. Within each
nonempty stratum, order the cells by **sha256 of the original formula**
(ascending hex), and take the first. Strata are visited in ascending
`(n, density)`. Cap: 9 instances; there are 7 nonempty strata, so every stratum
is represented.

The ordering key is the formula hash, which is fixed by `(n, α, k)` and is
independent of **every** outcome — of the size of the existing advantage, of
expected runtime, and of whether any previous equal-size attempt looked
favourable.

The seven strata: `n32_a2.5`, `n48_a2.5`, `n48_a3.5`, `n48_a4.2`, `n64_a2.5`,
`n64_a3.5`, `n64_a4.2`. Selected and unselected instance ids are recorded in
`data/cohort_manifest.json`, written before any new query.

**Historical equal-size sets**, including the previously uncertified `_eqW`
case, are kept in a **separate secondary appendix** (`REPORT.md` §Appendix).
Their provenance is audited, but they are not promoted into the primary cohort:
that selection was outcome-informed (it exists only because the original run
happened to reach it) and its upper bound was never certified.

---

## 3. Equal-size construction

For each selected instance:

1. load and hash the original formula and both frozen observed sets, requiring
   both hashes to match the continuation journal (recovery, never substitution);
2. validate **every** assignment in both sets against the original formula;
3. deduplicate and verify the reported distinct sizes;
4. set `k = min(|A_W|, |A_C|)`;
5. leave the smaller set **unchanged**;
6. draw `k` distinct members uniformly **without replacement** from the larger
   set. If the sets are already equal, both are left unchanged.

**Replicates:** exactly **3** per instance, prespecified.

**PRNG and seeding.** `numpy.random.Generator(PCG64)`. Study seed
**`20261027`**, written here. The per-replicate seed is the first 64 bits of

```
sha256( "<study_seed>|<formula_sha256>|<solver_label>|<replicate_index>" )
```

with the full material string and digest recorded for every replicate.

**Canonicalization.** Each set is deduplicated and sorted lexicographically
*before* sampling, so the sampling frame is independent of the order in which
the solver happened to find the solutions, and a replicate is reproducible from
the seed alone.

**Subsets are never chosen** using resolution, mutual distance, clustering,
oracle witnesses, or any outcome. The actual selected sets and their sha256
hashes are saved — seeds alone are not accepted as provenance
(`data/subsampling_manifest.json`).

If two replicates produce an identical set, the measurement is reused by hash
and the duplication is **reported**; identical measurements are never counted
as independent evidence.

No additional solver solutions are generated, and no oracle witness is ever
added to an observed set.

---

## 4. Method, fixed from the completed optimization benchmark

**Selected: the established baseline encoding and certification path** — the
Sinz-2005 sequential counter rebuilt per radius, with the DRUP proof taken from
the same solve and checked by the pinned `drat-trim` @ `2e3b2dc` under its
strict verdict rule (a line exactly `s VERIFIED`, exit code never trusted).

**Why.** From the completed benchmark (`../optimization-2026-10-27/REPORT.md`
§5, written before this choice was fixed):

* The **query policy** change (A→B) has a clear, large, supported advantage on
  the primary metric — certified width reduction **37 vs 0** on the four hard
  measurements — and provably cannot hurt, since policy P reduces to baseline
  bisection whenever nothing is retired. It is adopted.
* The **incremental encoding** (B→C) has **no clear advantage on the primary
  metric**: total certified width reduction **38 vs 37**, winning three hard
  units and losing one, with no extra exact answers, and 4/4 exact on controls
  for all three methods alike.

Stated plainly, because it cuts the other way: C *was* consistently **20–35 %
faster wherever certified UNSATs dominate** (155 s vs 224 s on the secondary
unit, 123 s vs 173 s across controls), with 2.7× fewer variables. Under a fixed
budget speed does convert into certified information, so this is a real cost of
the conservative choice. Against it: C produced the benchmark's only
uncertified UNSAT, used up to 1.5× the memory, was *slower* on the smallest
instance, and — decisively — changed encoding and state reuse **together**, so
four measurements cannot attribute its behaviour to either.

The brief's tiebreak is explicit: where no alternative has a clear supported
advantage, retain the established baseline. On the primary metric none does, so
the baseline encoding is retained and only the policy improvement is taken.
**Recorded limitation:** this stage may therefore resolve fewer measurements
within budget than the incremental method would have.

Concretely: encoding and certification exactly as method B; query selection by
policy **D** below, which is policy P specialised to the ordering question.
This stage is **not** another encoding or query-policy optimization study, and
no further method comparison is run here.

Preserved unchanged from the validated optimization stage: assumption handling
(none are used, since the static encoding imposes the bound by construction),
the standalone-CNF certification discipline, the checker's strict status
handling, single-counter auxiliary-variable id allocation, and artifact
hashing.

---

## 5. Exploit existing certificates before any new SAT call

For a retained subset `B ⊆ A`, with

```
h(A,B) = max_{a in A} min_{b in B} d_H(a,b)
```

the elementary bounds are

```
            eps(A)  <=  eps(B)  <=  eps(A) + h(A,B)
```

*Lower:* inclusion monotonicity — every `x` has a weakly larger
nearest-neighbour distance in the smaller set.
*Upper:* the triangle inequality — for any `x` and any `a in A`,
`min_b d(x,b) <= d(x,a) + min_b d(a,b) <= d(x,a) + h(A,B)`; minimising over `a`
and then maximising over `x` gives the bound.

So a **certified** interval `[L_A, U_A]` transfers to

```
[ L_A ,  min(n, U_A + h(A,B)) ]
```

Additionally, **every available validated witness** `x` supplies the direct
lower bound `min_{b in B} d_H(x,b)`, which (because `B` is a subset) is weakly
stronger than the same witness's bound for `A`. Each stored witness is
**re-verified** against the original formula before use. The strongest
applicable lower bound is taken.

`h(A,B)` is computed **exactly**, on original-variable assignments only.

A **solver-reported** upper bound is never transferred. The earlier correction
from a reported `[29,30]` to a certified `[29,64]` remains in force, and
`src/test_eq.py` regression-tests that exact case.

These transferred bounds may already certify an ordering with **no new SAT
query**; where they do, that is recorded with full provenance (originating
certificate, subset hash, the exact `h` computation, and the implication) and
zero new work.

---

## 6. Certificate standard, unchanged

For a frozen observed set `B`:

```
Q_r(x) = I(x)  AND  for every b in B:  d_H(x,b) >= r+1
```

* a directly validated witness establishes a lower bound;
* an independently checked UNSAT certificate establishes an upper bound;
* **UNKNOWN tightens neither bound**;
* distance is computed on the **original variables** only.

All encoding, solving, certification reruns, proof checking and required I/O
count in the runtime.

### Policy D — decision-targeted query selection

The objective is a **certified comparison**, not necessarily two exact values.
With the opponent's certified interval `[L_O, U_O]` and the subject's current
certified interval `[lo, hi]`:

1. query `r = U_O` — SAT here gives `lo >= U_O + 1 > U_O`, i.e. **certified
   subject > opponent**;
2. query `r = L_O - 1` — a checked UNSAT here gives `hi <= L_O - 1 < L_O`, i.e.
   **certified opponent > subject**. If step 1 gave a checked UNSAT and step 2
   gives SAT, then for an exact opponent both values coincide: **certified
   equality**;
3. otherwise fall back to the optimization stage's validated policy P (longest
   unexhausted run, upper midpoint) inside `[lo, hi-1]`.

Radii outside `[lo, hi-1]` are skipped as uninformative under monotonicity. A
radius returning UNKNOWN, or whose UNSAT cannot be certified, is retired and
never retried. **Querying stops as soon as the ordering is certified.** If both
values become exact along the way, both are reported.

---

## 7. Budgets, enforced at process level

| limit | value |
|---|---|
| per SAT solver invocation | **60 s** |
| total **new** work per distinct `(I,B)` measurement | **240 s** |
| proof-checker cap | `min(300 s, remaining measurement budget)` |
| computational validation + main comparison, combined | **3 h** |

Every measurement needing new work runs in its **own subprocess** with a hard
wall-clock kill at `240 s + 60 s` grace; overshoot is recorded, not hidden.

**Order:** replicate-major — replicate 0 across every selected instance, then
replicate 1, then replicate 2 — in the predetermined instance order of the
cohort manifest (ascending stratum). Where both solver sides need work, the
side order rotates deterministically by instance index.

Limits are **not** raised after seeing results. Unresolved cases appear in every
summary. Artifacts are written inside this workspace, never to `/tmp` (a 7.7 GB
tmpfs here). Existing artifacts are reused by verified reference (hash) rather
than regenerated.

---

## 8. Conservative classification

For each replicate, both certified intervals are reported:
`W = [L_W, U_W]`, `C = [L_C, U_C]`.

```
certified C > W      iff  L_C > U_W
certified W > C      iff  L_W > U_C
certified equality   iff  both intervals are the SAME SINGLETON
unresolved           otherwise
```

Overlapping intervals establish **nothing** — in particular they do not
establish equality. The valid difference interval is reported too:

```
eps_C - eps_W  in  [ L_C - U_W ,  U_C - L_W ]
```

Per instance, the ordering is summarised as **certified consistently across all
three replicates**, **varies across replicates**, or **partly / entirely
unresolved**.

**Subsampling replicates are nested within one SAT instance.** They are never
counted as independent instances and never used to inflate a significance
claim. The instance count is the honest denominator. No post-hoc p-value is
computed and no population-wide solver ranking is claimed.

Original unequal-size comparisons and equal-size results are kept in
**separate columns** throughout.

This is a targeted follow-up pilot on existing data, not a fresh held-out
study.

---

## 9. Validation required before the main run

`src/test_eq.py`, on cases where exhaustive truth is available: deduplication /
canonicalization / subset cardinality; deterministic reproduction of each
sampled set; subset inclusion and assignment validity; **both** transferred
inequalities against enumeration; exact `h(A,B)`; witness-based lower bounds;
classification of overlapping vs separated intervals; the control showing
larger cardinality alone does not force better resolution; refusal of a
starting upper bound supported only by unchecked UNSAT; resume behaviour and
refusal to reuse evidence across different observed-set hashes; and the
retained proof-checking controls, including rejection of a proof whose
**necessary** step was removed.

Disagreements are investigated before proceeding.

---

## 10. Stopping point

Stop after `REPORT.md`. If the advantage disappears or stays unresolved, that is
reported directly — not rescued by choosing different subsets, dropping hard
instances, changing the cohort, or extending the budget. No manuscript
revision, no GitHub integration, no enlargement, no further research stage.
