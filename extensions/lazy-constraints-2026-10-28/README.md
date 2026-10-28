# Lazy distance constraints and witness tightening (2026-10-28)

Two bounded implementation studies of the **certified covering-radius
measurement procedure** used by `extensions/certified-resolution-2026-10-27/`
and `extensions/solver-budget-selection-pilot-2026-10-27/`. Observed sets are
held fixed throughout; no instance was added and `n` was not increased.

The consolidation note that presents both studies in context is
`notes/consolidation-2026-10-28/`.

## What was tested

1. **Witness tightening.** The measurement loops compute a witness's actual
   distance to the observed set, then update the lower bound only to the
   requested threshold `r+1`. A witness at distance `d` proves `ε ≥ d`, so
   `lo ← max(lo, d)` is sound. **Result: sound on all 594 stored witnesses, and
   it improves no reported interval** — 0 of 257 reconstructed measurements.
2. **Lazy distance-constraint generation.** Solve a relaxation carrying
   constraints for a subset `B ⊆ A`, check the candidate against the whole of
   `A`, add the nearest violated constraint, repeat. **Result: exact, needs
   3–43 % of the constraints, faster on units that resolve, worse on units that
   do not.**

## Exactness

`sat(Q_r^A) ⊆ sat(Q_r^B)` for `B ⊆ A`, so a *checked* refutation of the subset
query certifies the full query unsatisfiable; and a candidate verified against
the full `A` is a valid witness whatever `B` produced it. `UNKNOWN` and
unchecked UNSAT tighten no certified bound.

A lazy refutation establishes that `B` already suffices to exclude every
satisfying assignment at distance `> r` from all of `B`. It does **not**
establish that `B` is minimal, that it suffices at a smaller radius, or that
`ε(B,S_F) = ε(A,S_F)`.

## Layout

```
PROTOCOL.md    frozen before any measurement (sha256 in data/PROTOCOL_SHA.txt)
REPORT.md      findings, with every unit reported
CLAIMS.md      claim-to-evidence ledger
src/replay.py          study 1, no solver
src/lazy.py            study 2, static vs lazy
src/verify_pairing.py  radius-sequence and hash verification
src/maketables.py      regenerates every table from data/
results/       verbatim logs
data/          stage1.json, stage2.json, pairing.json, PROTOCOL_SHA.txt
certificates/  proofs for the verified-paired units (tar.gz)
```

## Reproducing

Tables are regenerated from the recorded data with no solver:

```
python3 src/maketables.py --markdown
```

Re-running the measurement needs the `optimization-2026-10-27` stage's own
`units.recover()` (which re-verifies the formula and observed-set hashes), a
SAT solver and a proof checker; see **Environment** below.

## Environment actually used

| component | version |
|---|---|
| CPython | 3.14.7 |
| python-sat | 1.9.dev15 |
| solver | Glucose 3 via PySAT |
| cardinality encoding | sequential counter (`EncType.seqcounter`), Sinz 2005 |
| proof format | DRUP, emitted by Glucose 3 |
| checker | `drat-trim`, commit `2e3b2dc0ecf938addbd779d42877b6ed69d9a985` (2024-11-25) |
| `drat-trim.c` sha256 | `d834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee` |
| compiler | gcc 16.2.1 |

## What is shipped, and what is not

`certificates/verified-paired-proofs.tar.gz` holds the CNFs and DRUP proofs for
the units that pass pairing verification and produced refutations. The **full**
artifact set is ~209 MB and is **not** in Git (`.gitignore` excludes
`extensions/*/artifacts/`); it is regenerable from the frozen inputs, which are
deterministic given the recorded seeds and hashes.

**This distinction matters:** the shipped data regenerate every table, but
independently re-verifying *all* numerical certificates requires the full
artifact set, which is not shipped here. No claim of complete independent
reproducibility is made.
