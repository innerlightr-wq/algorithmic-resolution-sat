# Algorithmic Resolution and Solver-Dependent Observational Geometry in SAT Solution Spaces

**Author:** Elias De Jesus, Independent Researcher
**ORCID:** [0009-0007-0190-9143](https://orcid.org/0009-0007-0190-9143)
**Status:** Research manuscript, September 2026. Not peer reviewed.

## Summary

A satisfiability solver rarely returns the full solution space of an instance — it returns whatever subset $A(I) \subseteq S_I$ its search strategy and budget happened to produce. This repository contains a geometric framework and a set of validated experiments for distinguishing **how much** of a solution space a solver found from **how faithfully** it represents that space's geometry.

Three quantities are kept explicitly separate:

- **Coverage** — what fraction of $S_I$ was found.
- **Hausdorff / covering resolution** — $\hat\varepsilon(A,I) = \max_{x\in S_I}\min_{y\in A(I)} d_H(x,y)$, exactly the Hausdorff distance between the found and true solution sets (a standard quantity, correctly attributed as such, not claimed as new).
- **Connectivity fidelity** — whether the found subset's apparent connected-component structure, at any Hamming-distance threshold, matches the truth.

## Central finding

On 349 paired held-out random-3-SAT instances, comparing WalkSAT (stochastic local search) against a CDCL solver (Glucose3) on the **same** solution space, each at its own standard budget: WalkSAT achieves significantly better resolution ($\hat\varepsilon$; paired $p=5.1\times10^{-38}$) while showing a median $11.6\times$ (95% CI $[9.6,13.3]$) greater apparent connectivity fragmentation than CDCL. Both effects **survive restricting to the approximately coverage-matched subset** of $160$ instances (coverage within 10 percentage points): resolution $p=2.5\times10^{-8}$, fragmentation $p=2.4\times10^{-7}$. The $349$-instance figures are *not* themselves coverage-matched — see [`docs/ADDENDUM_2026-10-27.md`](docs/ADDENDUM_2026-10-27.md). Neither solver is geometrically superior in an unqualified sense — each better preserves a different, logically independent aspect of the true solution-space geometry. This is reported conservatively; see the paper's Discussion section for exact scope limits.

This repository also reports, in full and without rescue, an initially promising cross-solver predictive-transfer finding that did **not** survive confound analysis and is explicitly retracted in the manuscript (Section 9).

## Repository structure

```
algorithmic-resolution-sat/
├── README.md
├── LICENSE                    Apache License 2.0
├── CITATION.cff
├── requirements.txt
├── paper/
│   ├── main.tex                              LaTeX source
│   ├── references.bib                        bibliography, every entry independently verified
│   ├── algorithmic_resolution_sat_v2.pdf      compiled manuscript
│   └── figures/                               7 figures, generated from frozen data
├── scripts/
│   ├── phase2/     WalkSAT experiment, Hamming-ball theorem, coverage/resolution families
│   ├── phase3/     CDCL (Glucose3) experiment, cross-solver geometry, sharpness proof
│   ├── phase4/     Confound audit, fragmentation replication (the paper's central result)
│   └── figures/    generate_figures.py
├── extensions/                 Post-publication work. Additive; the manuscript is unchanged.
│   ├── certified-resolution-2026-10-27/
│   │                Certified resolution past the n<=20 enumeration ceiling
│   │                (n = 32, 48, 64) + an equal-size control on the central ordering
│   └── solver-budget-selection-pilot-2026-10-27/
│                    Prospective pilot: common time budget, equal retained size,
│                    prefix vs uniform-subsample selection
├── data/
│   ├── phase2/     Frozen WalkSAT results and verification logs
│   ├── phase3/     Frozen CDCL results and verification logs
│   └── phase4/     Frozen confound-audit and fragmentation-replication results
└── docs/
    ├── SOURCE_OF_TRUTH.md          accepted result set, every number traced to its source
    ├── TITLE_DECISION.md           title candidates and selection reasoning
    ├── MANUSCRIPT_V2.md            Markdown draft that preceded the LaTeX conversion
    ├── TABLES.md                   the 5 core tables in Markdown form
    ├── CLAIM_EVIDENCE_AUDIT.md     every Abstract/results claim traced to source data
    ├── VERSION_HISTORY.md          what changed from the January 2026 preprint, and why
    ├── REPRODUCIBILITY.md          environment, dependencies, exact reproduction commands
    ├── LICENSE_NOTE.md             licensing decision record
    └── validation/                 the full narrative audit trail (Phases 1-4, 48 documents)
```

## Post-publication extensions

`extensions/` holds work done after the September 2026 manuscript. It is
**additive**: the paper, its figures and the frozen Phase 1–4 record are
unchanged, and nothing in `extensions/` revises a published claim.

### `certified-resolution-2026-10-27/`

The manuscript measures resolution by **enumerating** `S_I`, which caps its
experiments at `n ≤ 20`. This extension replaces the enumeration with `O(log n)`
SAT queries, each carrying an independently checkable certificate — a satisfying
assignment re-checked on the original variables for a lower bound, a DRUP
refutation accepted by a pinned [drat-trim](https://github.com/marijnheule/drat-trim)
for an upper bound. `UNKNOWN` tightens nothing and a bare solver `UNSAT` is
never treated as certified.

That makes resolution measurable at `n = 32, 48, 64`, and makes the paper's
central ordering testable under a control it did not have. In the larger-`n`
data WalkSAT's recorded set is also *larger* in 31 of 32 instances (typically
150 vs 40), and a smaller observed set mechanically admits a larger covering
radius — so the ordering was confounded with set size. Uniformly subsampling
the larger set down to the smaller one's cardinality, across 7 instances
covering every `(n, density)` stratum with 3 replicates each:
**6 of 7 instances certified `ε_C > ε_W`** (WalkSAT better), **1 certified
equality** — the one that was already an equality at unequal sizes — and
**0 reversals, 0 unresolved**, with the same verdict in all three replicates on
all seven.

### `solver-budget-selection-pilot-2026-10-27/`

A fresh prospective pilot, not a confirmation study: under a **common
implementation-level time budget** and equal retained sample size, how do the
two solvers compare when observed sets are built from first discoveries versus
from a uniform subsample of everything recorded in the budget?

### Scope limits that apply to both

- **Equal cardinality on the same formula implies exactly equal coverage
  fractions**, because `|A|/|S_I|` shares one constant denominator — but the
  numerical fraction remains **unknown**, since `|S_I|` is not computed beyond
  `n ≤ 20`. No coverage value is reported.
- **Random subsampling is uniform within a recorded set, not within `S_I`.** It
  cannot repair a recorded set that was unevenly spread.
- **A higher lower bound alone does not prove one true resolution exceeds
  another.** With interval-valued measurements an ordering is certified only
  when the intervals are disjoint; overlapping intervals establish nothing, not
  even equality.
- **The seven-instance equal-size study does not establish a universal solver
  ranking.** No p-value is computed for it.
- **These extensions measure resolution only.** The connectivity and
  fragmentation findings are **not** extended past `n ≤ 20`.
- **Equal wall-clock time does not equalise abstract algorithmic work**, and
  Python-versus-compiled implementation costs remain relevant throughout.

See also [`docs/ADDENDUM_2026-10-27.md`](docs/ADDENDUM_2026-10-27.md), which
corrects a coverage-matching labelling error in this README and in
`docs/SOURCE_OF_TRUTH.md` without editing the frozen reports.

## Reproducibility

Full instructions in [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md). Quick start:

```bash
pip install -r requirements.txt
# See docs/REPRODUCIBILITY.md for the full, ordered command sequence
# reproducing every number in the paper from scratch.
```

The manuscript is compiled from `paper/main.tex` via a standard `pdflatex → bibtex → pdflatex → pdflatex` sequence.

## Paper

The compiled manuscript is at [`paper/algorithmic_resolution_sat_v2.pdf`](paper/algorithmic_resolution_sat_v2.pdf).

## Provenance

This repository was built from a four-phase validation program (mathematical audit, WalkSAT experiment, CDCL replication and cross-solver geometry, and a final confound-audit/validation gate) whose complete narrative record is preserved in `docs/validation/`. Every numerical claim in the paper is traced to its exact source file in `docs/CLAIM_EVIDENCE_AUDIT.md`. This manuscript supersedes and corrects a January 2026 preprint under a closely related title; see `docs/VERSION_HISTORY.md` for a neutral account of what changed and why.

## License

Code and reproducibility materials are licensed under the Apache License 2.0 (see [`LICENSE`](LICENSE); licensing rationale in [`docs/LICENSE_NOTE.md`](docs/LICENSE_NOTE.md)).

## Citation

See [`CITATION.cff`](CITATION.cff). No DOI is yet assigned; one will be added following Zenodo deposition.
