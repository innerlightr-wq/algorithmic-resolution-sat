# PAIRED_OBSERVER_TEST.md — Phase 4, Part 13

The cleanest possible paired test of the core observer-effect claim: *"two algorithms can observe comparable amounts of the same solution space yet reconstruct its connectivity differently."* Same `349` held-out test instances as `FRAGMENTATION_REPLICATION_AUDIT.md`, same `S_I`, paired by instance, both solvers at their standard Phase 2/3 budgets.

## Result 1: fragmentation (from `FRAGMENTATION_REPLICATION_AUDIT.md`, reproduced here as this test's headline)

WalkSAT median excess-fragmentation `11.6×` that of CDCL (95% CI `[9.6,13.3]`), Wilcoxon `p=5.2×10⁻³¹`, **surviving coverage-matching** (`p=2.4×10⁻⁷` on the `160`-instance matched subset).

## Result 2: `ε̂` — the reverse direction, a genuine and important trade-off

| | WalkSAT | CDCL |
|---|---|---|
| Mean `ε̂` | **1.413** | **3.516** |
| Median `ε̂` | `1.000` | `3.000` |

**Wilcoxon signed-rank, paired, `n=349`: `p=5.1×10⁻³⁸`, median difference `−2.000` — WalkSAT achieves *significantly better* (smaller) `ε̂` than CDCL on the same instances.** This holds even in the **coverage-matched** subset (`n=160`): mean `ε̂_W=0.806` vs. `ε̂_C=1.625`, `p=2.5×10⁻⁸`. By regime: WalkSAT's advantage is consistent across solution-rich (`2.93` vs. `7.08`), intermediate (`0.97` vs. `2.66`), and near-threshold (`0.24` vs. `0.58`).

## The core empirical statement this test establishes

**At matched or near-matched coverage, on the identical solution space, solver identity materially and *oppositely* changes the two geometric diagnostics**: WalkSAT gives **better covering-radius resolution** (`ε̂`) but **dramatically worse apparent connectivity/fragmentation**; CDCL gives **worse covering-radius resolution** but **dramatically better apparent connectivity**. Neither solver dominates the other on both axes simultaneously.

This is not a minor footnote — it is a **direct, paired, statistically overwhelming, cross-solver empirical demonstration of the exact logical-independence result Phase 1 proved abstractly for arbitrary point-set constructions** (`phase1/V2_THEOREMS.md` T6, `phase2/COVERAGE_RESOLUTION_THEOREM.md`: coverage/resolution and connectivity/fragmentation are not reducible to each other, illustrated there via hand-built extremal examples). **Here the same phenomenon is observed "in the wild," produced by two real, unmodified, off-the-shelf SAT-solving paradigms on real random-3-SAT instances, not constructed by hand.** This is arguably the single strongest, most defensible empirical result to come out of the entire four-phase project.

## Answering the question directly

> **At matched coverage on the same instance, does solver identity materially change observed geometry?**

**Yes, decisively, and in a genuinely informative way**: not merely "the numbers differ," but "the two solvers trade off in *opposite directions* on two logically-independent diagnostics that this project's own mathematics (Phase 1/2) already proved could, in principle, diverge." The empirical result validates the theoretical framework's central distinction (coverage/resolution vs. connectivity/topology) rather than merely restating it.

## Caveat, stated plainly

This is an **observational** paired comparison of two specific solver configurations (WalkSAT with the Phase 2 parameters; Glucose3/CDCL with the Phase 3 permutation-based randomization and calibrated budget) — it does not establish that *all* local-search solvers systematically favor resolution over connectivity, or that *all* CDCL solvers systematically favor connectivity over resolution, only that these two specific, real, carefully-audited implementations do so consistently across `349` held-out instances. Generalizing to "local search vs. systematic search as paradigms" would require testing additional solvers in each family (`phase3/FINAL_GATE.md`'s Q13 answer, not attempted in this phase per the stop condition).
