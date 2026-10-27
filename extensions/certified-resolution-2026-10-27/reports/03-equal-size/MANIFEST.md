# Hash manifest — equal-size-certification-2026-10-27

## Pinned environment
```
kernel      : Linux 7.2.5-3-omarchy
python      : Python 3.14.7
python-sat  : 1.9.dev15
numpy       : 2.5.4
gcc         : gcc (GCC) 16.2.1 20260810
cores       : 8
drat-trim   : commit 2e3b2dc0ecf938addbd779d42877b6ed69d9a985, source UNMODIFIED
              build: gcc drat-trim.c -std=c99 -D_POSIX_C_SOURCE=200809L -O2 -o drat-trim
              binary sha256 e17cd2e8de37c4c43bf88360ae3d17740781fe971175bf0b0c935ee3aae4ae19
reference   : https://github.com/innerlightr-wq/algorithmic-resolution-sat
              local clone ../repo @ 2bef5a81a1d8a0cefa780d83d947c998533effd5 (read-only)
```

## Upstream sources imported UNCHANGED
```
facc5f610b3c148e65556f38eede9973eb5cc54ae06ee6230263b9f81482f722  src/encode.py
1966f7d1645f1ca42f136577019756ddc6f43c1913cf7ff0d953e2bed22d7d91  src/verify.py
8ec39169223d2a6be6cc5ce048593fd93c2b4fa954a3dde03449364cbcd4022e  src/drup.py
9d74640ce5d5bb1429346bfc6a3f5ee69c167584c1d879089ea59d921b0e329a  src/pilot.py
686d4713367b7a45d2c14184043cd4de06154a008f4bdc6985cf9cc39ab6bf31  continuation-2026-10-27/src/store.py
d8ab2ec177b3106d6f8817dba22c2052407587a15ea762756ef7fc3a6b4d7a35  continuation-2026-10-27/src/dratcheck.py
```

## This stage's source
```
9c539d1b04dab73763751c12d3f76d56e0ae8f7fec025c4cc23410a003a0d38e  src/eqcore.py
e6777afeff6163851850bbc9610506f1ddd35199a9da864ca3c237c75455acf8  src/eqmeasure.py
88058d2cf8250d8320063f00d8cad95ff16c59cdf5be63680494dd41a30d8ede  src/prepare_eq.py
80c13c9ac5c592d5b08e7de871faad6a05241d2aa34e7e5b3913307deff217e0  src/run_eq.py
a0d19243a4d41bf38f6a2c9a2f7a84ed8054373308c76eb35466431ef626c6e1  src/runone_eq.py
5f34feed232090863b1a6e3601dfeea3c3099b104df24cd2e1f08902921efb5a  src/summarize_eq.py
a316fba89e8554852b9c4dba1b89e934281fe4b1f5bdd29f900a013a1af9f40e  src/test_eq.py
```

## Documents
```
2ed15bb8205a6991e57d819a75044da7d1a3a39241020f9a879ca092ced1b52d  CLAIMS.md
d8d84a004d1f8bffb1e4c8386b45517699497ab35b7e2689f1e791096f584a36  MANIFEST.md
c2a8d899f721ba123dbac4eb00deb6d3f4fd4b8d65a8d6009fad6dc5fef85891  PROTOCOL.md
9a09f706674a8ff77e79034495d420fc7bb57fb3459bd9433b6a884849ec9a9d  REPORT.md
```

## Data and machine-readable outputs
```
65db46a2646d41bc05fb4188d643773cf5ad2577c1fc58ea1adb00c74a4c6b90  data/paired_results.csv
8bc7ba2788c5e75519b79dc86b2e832f18638bbc8578ba56c63cb980e5fe7770  data/cohort_manifest.json
6e2b22cdfbfc2856e285defe900e406239855981682b30924e70023d79bf4f9a  data/equalsize_summary.json
9e08c7547f2fed26673342619485b95376101ce372b54305dd7168aa172c3ff5  data/runs.json
85a8ab0ba07086ba03964d4cf732a532cf058cf91221afaa7f38f954b634800f  data/subsampling_manifest.json
21a28b90a6db0adaf5b94347a3513894b05baa20fffdfe6a683750f0a18b7584  data/transfer_only.json
```

## Journals and artifacts
```
journal records: 45 lines in 16 files
artifact files : 58
artifact bytes : 29963487
validation     : 0 files
workspace size : 30M
```

## Reproduction commands

```
# from ~/scratch/sat-resolution-oracle-audit-2026-10-26/
.venv/bin/python equal-size-certification-2026-10-27/src/test_eq.py       # 11 checks
.venv/bin/python equal-size-certification-2026-10-27/src/prepare_eq.py    # cohort + subsets + transfer
.venv/bin/python equal-size-certification-2026-10-27/src/run_eq.py        # 21 measurements, ~32 s
.venv/bin/python equal-size-certification-2026-10-27/src/summarize_eq.py  # tables
```

Determinism: study seed `20261027`; per-replicate seed is the first 64 bits of
`sha256("20261027|<formula_sha256>|<solver_label>|<replicate_index>")` under
`numpy.random.Generator(PCG64)`. Every replicate's seed material, digest,
indices and resulting set hash are recorded in `data/subsampling_manifest.json`.
