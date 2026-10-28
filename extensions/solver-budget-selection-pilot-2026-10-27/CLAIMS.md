# Claims — solver budget / selection pilot

`certified` = both certified intervals disjoint (or an identical singleton pair),
every bound carrying a validated witness or an independently checked UNSAT proof.
`measured` = exact finite observation on the stated grid. `unresolved` /
`not claimed` as written. Protocol commit `b0c7a79`, stamped in every output.

## Certified

| # | Claim | Evidence |
|---|---|---|
| S1 | Under **first-discovery prefix** selection at `k = 40`, `ε_C > ε_W` on **30 of 30** eligible instance-budget cells (15 at 5 s, 15 at 30 s). 0 reversals, 0 equalities, 0 unresolved | `data/paired_results.csv` |
| S2 | Under **uniform** selection from the same banks, the same cells give 10 `C>W`, 12 `W>C`, 5 equality, 3 unresolved across both budgets | same |
| S3 | **CDCL's chronological prefix is certified worse than a uniform sample of its own bank in 28 of 30 cells** (2 better, 0 equal) | Table 2 |
| S4 | **WalkSAT's prefix is certified better than or equal to its uniform sample in 25 of 30 cells** (17 uniform-worse, 8 equal, 2 prefix-worse, 3 unresolved) | Table 2 |
| S5 | Prefix selection is budget-independent: 28 of 30 cells certify `ε(5 s) = ε(30 s)` (W 13/15, C 15/15) | Table 3 |
| S6 | Every resolved comparison resolved to **exact singleton intervals on both sides**; 0 alarms, 0 unchecked UNSATs, 0 budget overshoots | `results/certify.txt` |
| S7 | `p32_a4.2_f0` is **UNSAT** (complete solver); `p32_a4.2_f1` is SAT with **exactly 2 models** | `data/ineligible_satisfiability.json` |

## Measured

| # | Claim |
|---|---|
| M1 | 18 attempted instances, 17 satisfiable, 36 groups, **30 eligible**, 6 ineligible, **0 not attempted** |
| M2 | 144 scheme-level comparisons: 110 certified, 10 unresolved, 24 ineligible |
| M3 | Collection 1118 s, **0 resource-limited**; certification 1487 s, max group 300.3 s against a 300 s allocation; total ≈ 60 min against a 4 h cap |
| M4 | **The uniform verdict varies across the three replicates in 20 of 30 instance-budget cells** |
| M5 | Bank-size asymmetry under equal time: at `n=64, α=2.5` WalkSAT 7 045 distinct / 0 duplicates / 7 046 restarts vs CDCL 333 414 distinct / 418 duplicates / 41 730 runs; at `n=32, α=2.5` WalkSAT 9 780 / 9 465 vs CDCL 19 702 / **642 618** |
| M6 | 4 CDCL cells had **identical 5 s and 30 s banks** (enumeration saturated before the short deadline), so their budget contrast carries no information |
| M7 | 5 of 36 solver-instance cells failed `k = 40` at each budget; only **one** (`p64_a4.2_f0`, WalkSAT, 27 of 40 on a formula with ≥ 60 models) is a solver collection failure |
| M8 | Validation before the primary run: **12/12**, including live deadline handling, short-bank-is-a-prefix, order-independent reproducible subsampling, hash-keyed reuse, and the retained encoding/proof controls |

## The careful reading

| # | Statement |
|---|---|
| R1 | **S2 does not establish a reversal.** By M4 the uniform verdict is unstable within an instance, so a certified `W > C` row is a certified statement about one pair of 40-element observed sets, **not** about the instance. The advantage *disappears into instability* under uniform sampling; it does not demonstrably reverse |
| R2 | S1 has no such freedom — the prefix is deterministic given the bank — which is why S1 and S3/S4 are the load-bearing results and S2 is not |
| R3 | S3/S4 identify the mechanism: `enum_models` walks one permuted search tree so consecutive solutions are correlated, while WalkSAT restarts independently. Equalising **cardinality** does not equalise **spread** |

## Not claimed

| # | Statement |
|---|---|
| N1 | **No universal solver ranking.** 18 instances, repeated observations within each, one solver pair, one implementation of each |
| N2 | **No contradiction of the September result.** That used each solver's own standard budget on 349 instances and matched coverage by *restriction* to 160; this pilot equalises *time* and resamples. Different designs, different estimands |
| N3 | **Equal wall-clock time is not equal algorithmic work.** WalkSAT is pure Python, Glucose3 is compiled C; M5 shows the gap directly. Nothing here separates solver paradigm from implementation cost |
| N4 | **No coverage fraction** — that needs `\|S_I\|`, which is not computed |
| N5 | **No post-hoc significance test**, and replicates are never counted as independent instances |
| N6 | **No insufficient sample is read as geometry.** S7 settles two of the three ineligible instances by complete solver; the third is explicitly a collection failure |
| N7 | No extension of the paper's connectivity or fragmentation findings; this measures resolution only |

## Unresolved

| # | Statement |
|---|---|
| U1 | 10 of 144 comparisons hit the 300 s group budget without certifying an ordering |
| U2 | Whether the prefix-versus-uniform asymmetry (S3/S4) holds beyond 18 instances, and whether it survives budget calibration that equalises work rather than wall clock |
| U3 | What estimand a powered study should use, given M4: the uniform ordering is not a stable instance-level property |
