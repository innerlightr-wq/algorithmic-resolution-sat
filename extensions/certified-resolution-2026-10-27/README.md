# Certified resolution at larger n, and an equal-size control

**Dated 2026-10-27. Not peer reviewed. An extension to the September 2026
manuscript, not a revision of it.**

## What this adds to the paper

The September manuscript measures resolution
`ε̂(A,I) = max_{x∈S_I} min_{a∈A} d_H(x,a)` by **enumerating `S_I`**, which caps
the experiments at `n ≤ 20` — the paper says so itself. Everything here follows
from replacing that enumeration with `O(log n)` SAT queries, each carrying an
independently checkable certificate:

* a **lower** bound needs a satisfying assignment re-checked on the original
  variables by direct Hamming distances (no SAT library, no encoder involved);
* an **upper** bound needs a DRUP refutation accepted by
  [drat-trim](https://github.com/marijnheule/drat-trim) pinned at
  `2e3b2dc0ecf938addbd779d42877b6ed69d9a985`;
* `UNKNOWN` tightens nothing, and a solver's bare `UNSAT` is **solver-reported,
  never certified**.

With that, resolution becomes measurable at `n = 32, 48, 64` — well past the
enumeration ceiling — and the paper's central ordering becomes testable under a
control it did not have.

Three results, in order of importance:

**1. The resolution ordering survives equalising distinct-set size.** The
paper's headline is that WalkSAT achieves better (smaller) `ε̂` than CDCL. In
the larger-`n` work, WalkSAT's recorded set is also *larger* in 31 of 32
instances (typically 150 vs 40), and a smaller observed set mechanically admits
a larger covering radius — so the ordering was confounded with set size. After
uniformly subsampling the larger set down to the smaller one's cardinality, on
7 instances spanning every `(n, density)` stratum, with 3 replicates each:

| | instances | measurements |
|---|---|---|
| certified `ε_C > ε_W` (WalkSAT better) | **6 / 7** | 18 / 21 |
| certified equality | **1 / 7** | 3 / 21 |
| certified `ε_W > ε_C` (reversal) | **0** | **0** |
| unresolved | **0** | **0** |
| same verdict in all 3 replicates | **7 / 7** | — |

The one equality instance was *already* a certified equality at unequal sizes,
so no instance changed its verdict.

**2. Resolution is certifiable at `n = 64`, but not always exactly.** Of 15
instances at `n = 64`, 11 reach an exact certified `ε̂`; 4 end as certified
*intervals* because one mid-radius SAT query exceeds the time limit. Those four
are reported as intervals, never as values.

**3. Proof checking stopped being the bottleneck; solving became it.** Swapping
a pure-Python DRUP checker for the compiled one moved certification from 98 % of
the wall clock down to 40–53 %, which is what made `n = 48` and `n = 64`
reachable at all.

## Scope — what is and is not claimed

* **Equal cardinality on the same formula implies exactly equal coverage
  fractions**, because `|A|/|S_I|` shares one constant denominator. The
  numerical fraction stays **unknown**: `|S_I|` is not computed anywhere here,
  and no coverage value is reported.
* **Random subsampling is uniform within a recorded set, not within `S_I`.** It
  cannot repair a recorded set that was itself unevenly spread.
* **A higher lower bound alone does not prove one true resolution exceeds
  another.** Orderings here are certified only when the intervals are disjoint
  (`L_C > U_W` or `L_W > U_C`); overlapping intervals establish nothing, not
  even equality.
* **The seven-instance equal-size study does not establish a universal solver
  ranking.** It is a targeted follow-up on existing recorded sets, with 7
  instances and nested replicates. No p-value is computed.
* **This work measures resolution only.** The paper's connectivity and
  fragmentation findings have **not** been extended to `n > 20`; nothing here
  speaks to them.
* Equalising cardinality is **not** equalising computational effort. The two
  solvers ran under budgets that were never calibrated against each other —
  which is exactly what the companion pilot in
  `../solver-budget-selection-pilot-2026-10-27/` addresses.

## Layout

```
reports/        the four completed stage reports and claim ledgers, as written,
                with their own manifests:
  00-base-audit/   oracle feasibility + validation on the paper's 349 instances
  01-continuation/ compiled proof checking, checkpointing, n=48 and n=64
  02-optimization/ query-policy vs incremental-encoding comparison (27 runs)
  03-equal-size/   the equal-size certified comparison
src/            portable code; 5 modules vendored byte-identically with
                provenance headers, plus eqlib.py and verify_extension.py
frozen/         original formulas + observed sets for all 30 measurements,
                hash-verified on load — enough to re-derive every number here
certificates/   all 29 equal-size DRUP refutations + sha256 manifest
data/           summary CSVs, cohort and subsampling manifests, ordering audit
tests/          self-contained fixtures checked against exhaustive enumeration
tools/          build script for the pinned drat-trim revision
```

## Evidence availability — stated plainly

Everything needed to **re-derive and re-verify** every number in this extension
is in this directory: the frozen inputs, the certificates, and the code. That
is verified by `src/verify_extension.py --with-proofs`, which re-encodes each
query from the frozen inputs and re-checks its proof — strictly stronger than
checking a proof against a stored CNF asserted to match.

The bulkier intermediate evidence (~1.5 GB of CNFs, the continuation and
optimization proof collections, per-query journals, run logs) is **not** in Git
and is **not published anywhere**. It is held in a local compressed archive with
a manifest, and it is regenerable from the frozen inputs with the commands in
`REPRODUCE.md`. No public download location for it exists, and none is claimed.

## Reproduction

See `REPRODUCE.md`. The short version:

```sh
python -m venv .venv && ./.venv/bin/pip install -r extensions/certified-resolution-2026-10-27/requirements.txt
sh extensions/certified-resolution-2026-10-27/tools/build_drat_trim.sh
./.venv/bin/python extensions/certified-resolution-2026-10-27/tests/test_fixtures.py
./.venv/bin/python extensions/certified-resolution-2026-10-27/src/verify_extension.py --with-proofs
```

## Licence

Apache 2.0, as the rest of this repository. `drat-trim` is third-party, is
**not** vendored here, and carries its own upstream licence; `tools/build_drat_trim.sh`
fetches it at a pinned revision and never modifies its source. See
`../../docs/LICENSE_NOTE.md`.
