# Claim-to-evidence map — consolidation of 2026-10-28

Each row: a claim in the consolidation note, the exact artifact supporting it,
and how to check it. Strength labels: **THEOREM** (proved), **FINITE** (verified
exhaustively on small instances; not a universal proof), **MEASURED** (this
study's runs), **CLASSICAL** (established prior art, restated),
**NOT ESTABLISHED**.

| # | claim | strength | evidence | how to check |
|---|---|---|---|---|
| 1 | `ε_x(A',G) = ε(A,S_F)` under (H1)+(H2) | **THEOREM** (Lemma 1, restating a standard projection fact) | note §3 | read the proof; `extensions/representation-invariance-2026-10-28/src/preservation.py` |
| 2 | `ε ≤ ε_full ≤ ε + p`, both attained | **THEOREM**, inequality **CLASSICAL** (Cohen et al. 1985 Cor. 1) | note §3 | proof in note; 720 instance/lift triples in `preservation.py` |
| 3 | margin regimes: preserved `p<ℓ`, unsettled `ℓ≤p<u`, void `p≥u` | **THEOREM** (Cor. 2) | note §4 | proof in note; `diagnostic.py::regimes` + 19 regression cases |
| 4 | sharpness under *matched* lifted cardinality or unique extensions | **NOT ESTABLISHED** | note §4 remark | — |
| 5 | 116 certified comparisons: 92 exact + 24 intervals; 43 carry no `p>0` guarantee (28 exact `M=1`, 15 with `M≥1`) | **MEASURED** | `representation-invariance-2026-10-28/results/diagnostic.txt` | `python3 src/diagnostic.py` |
| 6 | radius ladder reconstructs `ε`; `Q_0` UNSAT ⟺ `ε=0`; `Q_n` UNSAT always | **FINITE** (3 679 pairs at `n=4`) + immediate from definitions | `preservation.py` | `python3 src/preservation.py` |
| 7 | ERV varies an observable, not a decision (`LINSAT ∈ P` both ways; 300/300 vs 295/300) | **MEASURED** | `representation-invariance-2026-10-28/results/premises.txt` | `python3 src/premises.py` |
| 8 | `|Closure(A,b)| = 2^rank[A|b]`; `2^rank(A)` wrong on inconsistent systems | **THEOREM** + **MEASURED** (200 systems, 0 mismatches; regression `x=0,x=1`) | same | same |
| 9 | witness tightening is sound on all 594 stored witnesses; 79 loose, max gain 6 | **MEASURED** | `lazy-constraints-2026-10-28/results/stage1.txt`, `data/stage1.json` | `python3 src/replay.py` |
| 10 | tightening improves **0 of 257** reconstructed measurements | **MEASURED** | same | same |
| 11 | retrospective query saving 21/557 pilot, 0/37 hard units — **not** an online runtime measurement | **MEASURED**, lower bound | same | same |
| 12 | lazy loop is exact (subset refutation ⟹ full-query UNSAT; witnesses checked against full `A`) | **THEOREM** | note §7; `PROTOCOL.md` (frozen before measuring) | read the inclusion argument |
| 13 | lazy needs 3–43 % of distance constraints | **MEASURED** | `data/stage2.json` | `python3 src/maketables.py` |
| 14 | 4 units exact under both: 165.3 s → 99.5 s (1.66×) | **MEASURED**, one unit not verified paired | `data/stage2.json` | `maketables.py` Table 4 |
| 15 | 3 **verified-paired** units: 46.0 s → 18.9 s (2.43×); check 23.2 → 3.2 s | **MEASURED** | `data/pairing.json`, `results/pairing.txt` | `python3 src/verify_pairing.py` |
| 16 | `n64_a2.5_k0_W` is **not** paired and its stage-2 exact answer did not reproduce | **MEASURED** | same | same |
| 17 | 5 unresolved units: summed widths 46 (static) vs 60 (lazy) | **MEASURED** | `data/stage2.json` | `maketables.py` Table 4 |
| 18 | removing constraints forces proof length or runtime to increase | **RETRACTED** — logical strength does not determine proof length; this study's own data refutes it | note §7 remark | — |
| 19 | any general speedup, asymptotic improvement, solver ranking, or complexity-class consequence | **NOT ESTABLISHED** | note §8 | — |
| 20 | hybrid lazy/static fallback would help | **NOT ESTABLISHED** (open question; deliberately not run) | note §8 | — |

## Certificates

`extensions/lazy-constraints-2026-10-28/certificates/verified-paired-proofs.tar.gz`
holds CNFs and DRUP proofs for the verified-paired units that produced
refutations. The full ~209 MB artifact set is not in Git. Tables regenerate from
the shipped data; independent re-verification of **all** certificates does not.
