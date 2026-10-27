# Hash manifest — optimization-2026-10-27

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
6ec245a3c07f4e86d78d07542a790f979952a0b91635a5123921a37d61ec9255  src/baseline.py
912e4af7e0eab9660b5758895069fbfba6d4113c1495886e958bc5c3c5757c6d  src/encinc.py
374fe40629361c0771c4c7abf336eac467937e368e16f48636d91aad22bb4fd2  src/methods.py
9844a85209950261d6e8410fee9197b66f759d09b7e25da14b09c2ae0ce6f287  src/ordering.py
f3a40116942030bc0b23a25fa1833a6642391e59bf263656fc4a9209fac56ee5  src/prepare.py
d67e04485083c6b454f971090c5c94b7ac8cd121045592337509cfd2633da8cb  src/runbench.py
b4a6fb5215aaead893c37b4d3328df7a097173b9aad2ca8c116bdce9989ef56f  src/runone.py
9b06e57ae12c178575a1904ea0569dc30c6e1b2755b8df10f931bce0c69a3c16  src/summarize_opt.py
a40eadcac74ce1f6d3540356b3c04aa2136fcfa300e3627ba059366e6021ee09  src/test_encoding.py
7ecf294f44bb6df22de8d4d675c5a9d20a08d66923025d0a3d69714ddd24e7b7  src/test_incremental.py
6622e8c3d5e9b58539896e67acbdd76bfbe609a6b7c0ddabf4e937c95997560f  src/test_policy.py
df7fe9c652284ad766d222e429f838b5b93849723711d714a2212bf150d95177  src/units.py
```

## Documents
```
71e93a609256ced311ef9cd4c974ee5f4fd0c4e575096eb5b7dc53d6ed58dd99  CLAIMS.md
2a9438afe9166d38a0edc63a4dad0d59d2f9f2942ff1662734fff7bde6090127  MANIFEST.md
b3093f2193703c1c3c94b423afe400aef62303c7a4abd90ab5cd9c685d38d521  PROTOCOL.md
a99dbf2804b72fa12c134807481e460b0b83141e393f663957032f436156beec  REPORT.md
```

## Data and machine-readable outputs
```
44fabcf4dcbbf1fec62d6b4c8410e3808572488f6a14961b7a1aafd7446e40cb  data/ordering_audit.csv
afea0b3fe24113e3b68cc9a806b709f6f97543403de34e20ab9914edffde7b8c  data/paired_results.csv
e60548fd8a0cb8dded1ebd57eee79f908a4ba9582f00a87ccf7a8999d344bca9  data/baseline.json
ecce55f4a99d80f32ca646e19f09c851c0dbf2e78f18dd52793516c1e4a7d126  data/optimization_summary.json
b02dca54d975cce677b63f01ac87af44275774ba01bddfbe5022bf2c47460229  data/ordering_summary.json
43a354bc94b2a8104297c4df5d367ec00df3483ac8f82ab0b36290cfd108895e  data/runs.json
```

## Journals and artifacts
```
journal records: 137 lines in 27 files
artifact files : 174
artifact bytes : 611380494
validation     : 6 files
workspace size : 586M
```

## Reproduction commands

```
# from ~/scratch/sat-resolution-oracle-audit-2026-10-26/
.venv/bin/python optimization-2026-10-27/src/units.py            # experimental units
.venv/bin/python optimization-2026-10-27/src/baseline.py          # re-verify every start
.venv/bin/python optimization-2026-10-27/src/test_encoding.py     # 6 checks
.venv/bin/python optimization-2026-10-27/src/test_policy.py       # 7 checks
.venv/bin/python optimization-2026-10-27/src/test_incremental.py  # 13 checks
.venv/bin/python optimization-2026-10-27/src/runbench.py          # 27 runs, ~54 min
.venv/bin/python optimization-2026-10-27/src/summarize_opt.py     # tables
.venv/bin/python optimization-2026-10-27/src/ordering.py          # solver-ordering audit
```
