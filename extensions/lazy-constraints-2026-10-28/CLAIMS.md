# Claims ledger

**MEASURED** = exact, from this stage's own runs; **PROVED** = argued and used;
**NOT ESTABLISHED** = not shown here.

## Stage 1 — witness tightening

| # | claim | strength |
|---|---|---|
| T1 | A witness `x` with `min_{a∈A} d_H(x,a) = d` proves `ε ≥ d`, so `lo ← max(lo, d)` is sound | **PROVED** (definition of `ε` as a max over `S_F`) |
| T2 | `measure.py:172` and `methods.py` compute `min_dist` and update `lo` only to `r+1` | **MEASURED** (source) |
| T3 | The tightening is sound on every stored witness: no replayed witness gives a smaller bound | **MEASURED**; 594 witnesses, min gain 0 |
| T4 | 79 of 594 (13.3 %) stored witnesses are loose; max gain 6, mean 0.316 | **MEASURED** |
| T5 | **0 of 257** reconstructed measurements would gain a better certified lower bound | **MEASURED** |
| T6 | 21 of 557 pilot SAT queries and **0 of 37** hard-unit SAT queries would be skipped | **MEASURED**; a **lower bound**, since the policy diverges after the first skip |
| T7 | All 37 hard-unit (`n = 64`) witnesses have gain exactly 0 | **MEASURED** |
| T8 | The reason for T7 is that the cardinality constraint is binding | **NOT ESTABLISHED** — a plausible mechanism, not tested |
| T9 | Any runtime improvement from the tightening | **NOT ESTABLISHED**; T5 and T6 are the measured effect |

## Stage 2 — lazy distance constraints

| # | claim | strength |
|---|---|---|
| L1 | `sat(Q_r^A) ⊆ sat(Q_r^S)` for `S ⊆ A`, so a checked UNSAT for the subset certifies the full query | **PROVED**, frozen in `PROTOCOL.md` before measuring |
| L2 | A candidate verified against the full `A` is a valid witness whatever `S` produced it | **PROVED**; verification is always against full `A` |
| L3 | Fewer constraints suffice: L terminated on 4–64 of 150 (3 %–43 %) | **MEASURED** |
| L4 | On the 4 units resolved by both in this run, L and S agree, and both match the historical exact values 26, 16, 9, 18 | **MEASURED** |
| L4a | **3 of those 4 are VERIFIED PAIRED**: identical radius sequences, identical per-query outcomes, re-run reproduces the certified interval, both ladders self-terminating | **MEASURED** (`src/verify_pairing.py`) |
| L4b | `n64_a2.5_k0_W` is **NOT** paired: different radius sequences (`24,28,26` vs `24,28,26,25`), static ladder budget-limited, and its stage-2 exact answer **did not reproduce** (re-run stopped at `[25,28]`). Excluded from all paired claims | **MEASURED** |
| L5 | On those 4, aggregate 165.3 s → 99.5 s, **1.66×** with certification included; per unit 1.15×–2.63× | **MEASURED**, but one of the four is not verified paired (L4b) |
| L5a | On the **3 verified-paired** units: 46.0 s → 18.9 s (**2.43×**); solve 19.3→8.5 (2.28×); check 23.2→3.2 (**7.27×**) | **MEASURED** |
| L6 | The saving is **mainly** certification: on the verified-paired units checker time falls 7.27× against 2.28× for solving. Not *only* certification — solve time falls too, and encode time rises | **MEASURED** |
| L7 | On 4 of the 5 unresolved units L ends with a **wider** interval than S; 1 ties | **MEASURED** |
| L8 | The cause is refinement thrashing: 48–59 iterations inside a single radius query, 1 completed query against S's 3 | **MEASURED** |
| L9 | On `k1_eqW` the lazy proofs are **larger** (524 081 vs 245 460 lines at `r = 31`) despite a 3.3× smaller CNF | **MEASURED** |
| L10 | Refuting a subset is a logically **stronger** statement than refuting the full query | **PROVED** (from L1) |
| L10a | ~~L9's direction is therefore the general one~~ | **RETRACTED.** Logical strength does not determine proof length or runtime. Removing constraints does not force either to increase, and this stage's own data refutes the inference: on the four resolved units the subset proofs are *smaller*, with checker time falling 82.7 s to 18.6 s in aggregate. `k1_eqW` is one measured case, not a general direction |
| L11 | 0 alarms; every L bound certified by the same rules as S | **MEASURED** |
| L12 | A general speedup for lazy constraints | **NOT ESTABLISHED** — the opposite on hard units |
| L13 | A hybrid (concurrent S/L, or fall back after an iteration threshold) would help | **NOT ESTABLISHED** — a hypothesis, untested |
| L14 | The unresolved-unit widths hold at other budgets | **NOT ESTABLISHED**; those comparisons are specific to the 120 s budget |

## Not claimed anywhere

No solver ranking (`C1`, `C7` remain retracted). No change to any observed set.
No new instance, no increase in `n`. No repository file, manuscript, branch or
memory file was modified by this stage.
