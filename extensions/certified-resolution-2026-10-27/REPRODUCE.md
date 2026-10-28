# Reproduction — certified resolution extension

All commands are run from the **repository root**. Nothing here depends on an
absolute path outside this repository.

## 0. Environment

```sh
python -m venv .venv
./.venv/bin/pip install -r extensions/certified-resolution-2026-10-27/requirements.txt
./.venv/bin/python -c "import importlib.metadata as m, numpy; \
  print('python-sat', m.version('python-sat'), '| numpy', numpy.__version__)"
# expected: python-sat 1.9.dev15 | numpy 2.5.4
```

Recorded environment for the results as published here:

| | |
|---|---|
| OS / kernel | Linux 7.2.5-3-omarchy |
| Python | 3.13.9 |
| `python-sat` | 1.9.dev15 *(same pin as the September paper)* |
| numpy | 2.5.4 *(paper pinned 1.26.4; see `requirements.txt` for why this is safe)* |
| gcc | 16.2.1 20260810 |
| cores | 8 |

## 1. The proof checker

```sh
sh extensions/certified-resolution-2026-10-27/tools/build_drat_trim.sh
```

Pinned at `2e3b2dc0ecf938addbd779d42877b6ed69d9a985`. The script **verifies the
source sha256** (`d834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee`)
before compiling and refuses to proceed on a mismatch. The binary is not
committed and is git-ignored. The binary hash is compiler-dependent; with gcc
16.2.1 it comes out as `e17cd2e8de37c4c43bf88360ae3d17740781fe971175bf0b0c935ee3aae4ae19`.

A note on why the build needs one extra flag: the upstream `Makefile` uses
`-std=c99` with no feature-test macro, and modern glibc then hides the POSIX
declaration of `getc_unlocked` (used at `drat-trim.c:986`), so the upstream
recipe does not compile. `-D_POSIX_C_SOURCE=200809L` exposes the declaration
**without editing the source** and without changing the language standard.

## 2. Small reproduction example — seconds

```sh
./.venv/bin/python extensions/certified-resolution-2026-10-27/tests/test_fixtures.py
```

Builds a fixed 8-variable formula (92 solutions), computes `ε̂` by **exhaustive
enumeration**, and independently by the certified pipeline, for four observed
sets. Also checks the transferred-bound inequalities against the truth, the
"larger unrelated set can be worse" control, subsampling determinism, and the
query policies. 11 assertions; expected output ends `ALL PASS`.

This is the check to run on a clean checkout. It needs no network, no large
data, and passes with or without drat-trim (without it, the UNSAT side is
cross-checked by enumeration and proof checking is reported as skipped).

## 3. Re-derive every published number, and re-check every certificate

```sh
./.venv/bin/python extensions/certified-resolution-2026-10-27/src/verify_extension.py --with-proofs
```

11 checks. In order, it:

1. loads all 30 frozen measurements and **re-hashes** the formula and observed
   set of each, failing on any drift;
2. confirms every observed assignment really satisfies its own formula;
3. recomputes the equal-size headline tallies from the paired CSV;
4. recomputes per-instance replicate consistency;
5. re-derives the transferred-bound arithmetic on all 21 subsets and confirms
   no final interval escaped its start interval;
6. recomputes the optimization tallies and confirms **no certified improvement
   was recorded after its deadline**;
7. extracts all 29 DRUP certificates, checks each one's sha256 against
   `certificates/MANIFEST.json`, **re-encodes its CNF from the frozen inputs**,
   and runs drat-trim on the pair.

Expected: `ALL PASS`, with `29 verified, 0 failed`.

Step 7 is deliberately stronger than shipping CNFs: a proof is only meaningful
against a specific formula, so the formula is rebuilt from the frozen
`(I, B, r)` rather than trusted from a stored file.

**Runtime is not part of the claim.** Do not expect byte-identical wall-clock
numbers, and do not expect freshly generated proof *files* to match the
distributed ones — a solver may emit a different valid refutation. What must
reproduce is the **mathematics**: the same `ε̂` values and intervals, the same
verdicts, the same hashes for frozen inputs and distributed certificates.

## 4. Regenerating the evidence that is not in Git

Not distributed: the intermediate CNFs (~1.5 GB), the continuation and
optimization proof collections, per-query journals, and run logs. They are
**regenerable**, and they are held in a local archive that is **not published**
(see the manifest written alongside it,
`sat-certified-resolution-evidence-2026-10-27.MANIFEST.txt`).

To regenerate a single query's CNF and proof from frozen inputs:

```python
import sys; sys.path.insert(0, 'extensions/certified-resolution-2026-10-27/src')
from eqlib import load_frozen
from encode import encode_Q
from pysat.solvers import Glucose3

cl, B, d = load_frozen('extensions/certified-resolution-2026-10-27/'
                       'frozen/equal-size/n48_a4.2_k1_eqW_r0.json')
cnf, nvars, naux, kind = encode_Q(cl, d['n'], B, 2)      # radius 2
s = Glucose3(bootstrap_with=cnf, with_proof=True)
print('SAT' if s.solve() else 'UNSAT')
open('q.cnf', 'w').write(f'p cnf {nvars} {len(cnf)}\n'
                         + ''.join(' '.join(map(str, c)) + ' 0\n' for c in cnf))
open('q.drup', 'w').write('\n'.join(s.get_proof() or []) + '\n')
```

then `extensions/certified-resolution-2026-10-27/tools/drat-trim/drat-trim q.cnf q.drup`,
expecting a line exactly `s VERIFIED`.

## 5. Regenerating an observed set from scratch

The observed sets are reproducible from the pilot's own deterministic
procedure, using **this repository's** solver code
(`scripts/phase2/walksat_solver.py`, `scripts/phase3/pysat_common.py`):

```
formula      : random_3sat_clauses(n, round(alpha*n), default_rng(
                 PILOT_SEED + 100000*n + 1000*round(10*alpha) + k))
PILOT_SEED   : 20261026
WalkSAT set  : default_rng(PILOT_SEED + 777  + obs_seed_id), K=150,
               max_flips=3000, p_noise=0.5
CDCL set     : random.Random(PILOT_SEED + 3333 + obs_seed_id), R=5 permuted and
               phase-randomised enum_models runs, truncated at T=8 models each
```

`obs_seed_id` is recorded per measurement in the frozen files. Every frozen
record's hashes were produced this way and re-verified on load, so regeneration
is checkable rather than asserted.

One caveat recorded honestly: `obs_seed_id` is the original pilot's running
instance counter, and it **skips values** when a wall clock fired, so it is not
a function of `(n, α, k)`. The mapping was reconstructed and verified by
reproducing every observed-set size and hash; see
`reports/01-continuation/PROTOCOL_AMENDMENT.md` §3.
