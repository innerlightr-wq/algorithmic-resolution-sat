# Claims — optimization stage, 2026-10-27

Adds to `../CLAIMS.md` and `../continuation-2026-10-27/CLAIMS_ADDENDUM.md`;
erases nothing in either. Levels: **proved** (mathematics);
**witness-verified** (SAT model re-checked by the original `src/verify.py`);
**proof-checked** (DRUP proof accepted by pinned `drat-trim` @ `2e3b2dc`);
**measured**; **unresolved**.

## Proved

| # | Statement | Where |
|---|---|---|
| O1 | `d_H(x,a) >= r+1` ⟺ `agree(x,a) <= n-r-1`, where `agree` counts coordinates on which `x` equals `a`; the agreement literals are the literal-by-literal **negation** of the original encoder's distance literals | `PROTOCOL.md` §2.1, exhaustively checked in `src/test_encoding.py` |
| O2 | Useful radii are exactly `[lo, hi-1]`: monotonicity makes every `r <= lo-1` already-known SAT, and no `r >= hi` can lower `hi` | `PROTOCOL.md` §5 |
| O3 | Policy P's chosen radius equals the baseline's `(lo+hi)//2` whenever nothing is retired, for **every** interval. Hence method B is identical to method A until the first UNKNOWN | verified on all 2 080 intervals, `src/test_policy.py` |
| O4 | Policy P terminates: every query either moves a certified bound or permanently retires a radius | verified under an adversary that never certifies, `src/test_policy.py` |
| O5 | A backward-mode `s VERIFIED` certifies **unsatisfiability of the formula**, which is the upper bound claimed — not well-formedness of the whole proof text | carried forward from the continuation |

## Measured — the comparison

| # | Statement | Level |
|---|---|---|
| O6 | On the four hard `n=64, α=2.5` measurements the **baseline certifies nothing**: 0 width reduction, 0 exact, 4 UNKNOWN, ~60 s each | measured |
| O7 | The **query-policy change** narrows all four, total certified width reduction **37** of a starting total of 60 | witness-verified + proof-checked |
| O8 | The **incremental method** narrows all four, total **38** — winning three units, losing one. No clear advantage over O7 on the primary metric | witness-verified + proof-checked |
| O9 | **No** previously unresolved measurement became certified exact under any method | measured |
| O10 | The hard boundary query was **not** removed. `k4_W` under C reached `[24,25]` and halted with "no useful unattempted radius", because closing it needs exactly the retired r=24 query | measured |
| O11 | Gains on the hard set come overwhelmingly from **lower** bounds: 9 / 10 validated witnesses versus 4 / 5 certified upper bounds for B / C | measured |
| O12 | On **controls** all three methods are equivalent on the primary metric: 4/4 exact, 44 total reduction each; A and B make **identical query counts** | proof-checked, 12/12 runs |
| O13 | All 12 control runs reproduce the historical exact answer (26, 18, 16, 9); **0 inconsistencies** | proof-checked |
| O14 | `n64_a2.5_k1_eqW` moves from a certified `[29,64]` to a certified `[29,30]` under all three methods. This **converts a solver-reported bound into a checked one**; it is not a narrowing beyond what was previously reported | proof-checked |
| O15 | The incremental method is **20–35 % faster wherever certified UNSATs dominate** (155 s vs 224 s on the secondary unit; 123 s vs 173 s across controls), including its certification reruns | measured |
| O16 | The incremental encoding trades **~10 % more clauses for ~2.7× fewer variables** (337–353 k clauses / 54–56 k vars vs 186–307 k / 95–153 k) and builds once instead of per radius | measured |
| O17 | The incremental method costs **1.5× peak memory** (up to 259 MB vs 169 MB) and produced the benchmark's **only** uncertified UNSAT | measured |
| O18 | On a tiny instance the incremental method is **slower** (`n64_a4.2_k0_W`: 5.0 s vs 2.8 s) — its build cost is not amortised | measured |
| O19 | **4 of 27 runs overshot** the 240 s budget by 0.5–2.8 %, because a 60 s per-invocation timer can start just before the measurement deadline. 0 hard kills, 0 alarms | measured |

## Measured — the solver-ordering audit

| # | Statement | Level |
|---|---|---|
| O20 | Over **32 instance cells with certified records on both solver sides** (64 solver measurements; 28 exact on both): **31 certified `ε_C > ε_W`**, **1 certified equality**, **0 certified `ε_W > ε_C`**, **0 unresolved** | proof-checked + witness-verified |
| O21 | Four of those are cells where `ε_W` is itself **unresolved**; the ordering is still certified there because `L_C > U_W` | proof-checked |
| O22 | **The ordering is confounded with observed-set size in 31 of the 32 cells** (`|A_W| > |A_C|`, typically 150 vs 40). A smaller observed set mechanically admits a larger covering radius | measured |
| O23 | Exactly **one** cell has the confound absent (`n64_a4.2_k3`, `|A_W|=29` vs `|A_C|=30`) and still shows certified `C > W` | proof-checked |
| O24 | The comparison designed to remove the confound — equal-distinct-size — has **zero certified data**, because the original protocol ran it with `want_proof=False` | measured |
| O25 | **28** satisfiable `n=24`/`n=32` instances are excluded from the audit entirely, because the original pilot certified only the W side | measured |

## Not claimed

| # | Statement |
|---|---|
| N-O1 | **No general solver ranking.** O20 is an ordering of these specific recorded measurements, confounded per O22, on a 15-per-size pilot |
| N-O2 | **No coverage fraction** anywhere: that requires `|S_I|`, which is unavailable |
| N-O3 | **No encoding recommendation.** Four measurements cannot settle it; O8 shows no clear advantage on the stated success criterion |
| N-O4 | **No population inference from the hard set.** It is an optimization set, not a held-out sample |
| N-O5 | C-vs-B differences are **not** attributable to either the encoding or the state reuse alone — they changed together by design |
| N-O6 | Failure to reach exactness is **not** evidence that the approach is limited. It is a budget-and-solver limit at one radius, as `k4_W` reaching width 1 shows |

## Unresolved

| # | Statement |
|---|---|
| U-O1 | `ε_W` for the four hard `n=64, α=2.5` measurements. Best certified intervals now `[24,32]`, `[24,30]`, `[23,28]`, `[24,25]` |
| U-O2 | Whether the r=24 query at `n=64, α=2.5, |A|=150` is tractable at all with a larger per-query budget — deliberately not tested, since the 60 s limit was fixed in advance |
| U-O3 | Whether the incremental encoding helps on a properly powered cohort. O15–O18 suggest a speed benefit that converts to certified information only under a fixed budget |
| U-O4 | Whether the certified ordering of O20 survives equalising distinct-set sizes — the question O24 leaves open and the next stage addresses |
