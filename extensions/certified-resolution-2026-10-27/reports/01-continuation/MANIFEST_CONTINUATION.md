# Manifest — continuation of 2026-10-27

Provenance for everything the continuation used or produced. Companion to the
original `../MANIFEST.md`, which is unchanged.

## Environment
```
host kernel      : Linux 7.2.5-3-omarchy
python           : Python 3.14.7
python-sat       : 1.9.dev15
numpy            : 2.5.4
gcc              : gcc (GCC) 16.2.1 20260810
cores            : 8
run date         : 2026-10-27
```

The paper pinned numpy 1.26.4; this audit runs 2.5.4. The PCG64 stream is
confirmed stable — every surviving observed-set size was reproduced exactly.
`python-sat` is the paper's exact pin.

## Compiled proof checker

```
source      : https://github.com/marijnheule/drat-trim
commit      : 2e3b2dc0ecf938addbd779d42877b6ed69d9a985   (2024-11-25)
build       : gcc drat-trim.c -std=c99 -D_POSIX_C_SOURCE=200809L -O2 -o drat-trim
source hash : d834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee  drat-trim.c
binary hash : e17cd2e8de37c4c43bf88360ae3d17740781fe971175bf0b0c935ee3aae4ae19  drat-trim
modified?   : no  (git status clean for drat-trim.c; only the binary is untracked)
```

The upstream `Makefile` recipe does not compile against this glibc:
`getc_unlocked` at `drat-trim.c:986` has no visible declaration under
`-std=c99`. `-D_POSIX_C_SOURCE=200809L` exposes it without editing the source
and without changing the language standard.

Proof format emitted by our solver: addition-only DRUP (one DIMACS clause per
line terminated by `0`, no `d` lines, no RAT markers), inspected rather than
assumed. drat-trim reads it natively.

## Original audit sources — imported UNCHANGED
```
8ec39169223d2a6be6cc5ce048593fd93c2b4fa954a3dde03449364cbcd4022e  src/drup.py
facc5f610b3c148e65556f38eede9973eb5cc54ae06ee6230263b9f81482f722  src/encode.py
87a7d1a4fdb75782f26dfbed328f2e9ea36a3808bd6a8d8406d1cd74dde779f6  src/oracle.py
9d74640ce5d5bb1429346bfc6a3f5ee69c167584c1d879089ea59d921b0e329a  src/pilot.py
e92e9e52197ff2d134e8ef688753b99b786f038a0fe0824695cca72ea4e4007c  src/repro_A.py
88c86e6dd055d748c3ebfb040e518185eb11121db86b61f4dc81b43eed883c2f  src/validate.py
1966f7d1645f1ca42f136577019756ddc6f43c1913cf7ff0d953e2bed22d7d91  src/verify.py
```

`encode.py`, `verify.py` and `drup.py` are imported by the continuation as-is.
`verify.py` still imports no SAT library and no encoder, so the lower-bound
check remains independent of both.

## Continuation sources
```
77cf5ceef9e8c9eb9ae434c35855aa0eeb448d1cd6d3b814ded450b39c1d62a7  src/bench.py
d8ab2ec177b3106d6f8817dba22c2052407587a15ea762756ef7fc3a6b4d7a35  src/dratcheck.py
63d02500a3c7632910b27f48ef2fcadaf0a91c2778b39bcd4c75cb379a2be763  src/measure.py
15b1a2491625c3c08489c35df272e9f1481f195cb9f4132f9a28eacaeb16c61f  src/resume_pilot.py
686d4713367b7a45d2c14184043cd4de06154a008f4bdc6985cf9cc39ab6bf31  src/store.py
bf7d6c064e0b6ecb7e63985798ecc3ad6c4fafd0e6d65c6b9474d3caf614c48e  src/summarize.py
94512e95929286747198524bc492dee00d467b3f90b573dd5adb372680dd37c0  src/test_checkpoint.py
```

## Commands run

```
.venv/bin/python continuation-2026-10-27/src/bench.py controls
.venv/bin/python continuation-2026-10-27/src/bench.py small
.venv/bin/python continuation-2026-10-27/src/bench.py large
.venv/bin/python continuation-2026-10-27/src/test_checkpoint.py
.venv/bin/python -u continuation-2026-10-27/src/resume_pilot.py 48
.venv/bin/python -u continuation-2026-10-27/src/resume_pilot.py 64
.venv/bin/python -u continuation-2026-10-27/src/resume_pilot.py 32 --only "2.5:0,2.5:2,2.5:4"
.venv/bin/python continuation-2026-10-27/src/summarize.py
```

## Determinism inputs

```
PILOT_SEED            = 20261026
formula               = gen(n, alpha, k) -> default_rng(PILOT_SEED + 100000*n
                                            + 1000*round(10*alpha) + k)
WalkSAT observed set  = default_rng(PILOT_SEED + 777  + obs_seed_id), K=150,
                        max_flips=3000, p_noise=0.5
CDCL observed set     = random.Random(PILOT_SEED + 3333 + obs_seed_id), R=5, T=8
STAGE_A_SEED (349)    = 20260928 + 777, per instance + id
```

`obs_seed_id` is the original pilot's instance counter, which skips values when
its wall clock fires. See `PROTOCOL_AMENDMENT.md` §3 and
`CONTINUATION_REPORT.md` §6 for the reconstructed mapping and its verification.

## Outputs
```
c47037ccbf03b88ea4a0c423e4ab47443a9c716fea0897f72e28bf99d06a7f6f  data/bench_controls.csv
92f7549fba705b7e33f2fc22443acd441ea003130a8a60797ffc7a5d167c7375  data/bench_large.csv
7370cb5b30ff3dc9f778b51d810530465e6ab66f3e137b160a0540f284a659cc  data/bench_small.csv
65709534cb47b781b098c1feb3cdf277fd5bea607198dbaf9d9d9b0ab0dfcb0d  data/resume_n32_recert.csv
9af06351916859ba5a73165ccd228d68c715e895503f5525cb183c9f201c6a59  data/resume_n48.csv
a75c82dfbc7459c9820a9f0e4be022788806203a4baca4c7bece4d2900fc2a95  data/resume_n64.csv
b9f84378e4f6c20484c0d8ffdaf9fbe52c2181e42a76bd223337abd038e1f49e  data/continuation_summary.json

journal records:
     9 journal/bench_controls.jsonl
    52 journal/bench_large.jsonl
    97 journal/bench_small.jsonl
    76 journal/resume_n32.jsonl
   395 journal/resume_n48.jsonl
   409 journal/resume_n64.jsonl
  1038 total

artifact stores:
764M	artifacts
51M	bench/artifacts
artifact counts: 978 resume, 161 bench
```
