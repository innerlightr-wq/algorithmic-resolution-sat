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

On 349 paired held-out random-3-SAT instances, comparing WalkSAT (stochastic local search) against a CDCL solver (Glucose3) at matched or near-matched coverage on the **same** solution space: WalkSAT achieves significantly better resolution ($\hat\varepsilon$; paired $p=5.1\times10^{-38}$) while showing a median $11.6\times$ (95% CI $[9.6,13.3]$) greater apparent connectivity fragmentation than CDCL. Neither solver is geometrically superior in an unqualified sense — each better preserves a different, logically independent aspect of the true solution-space geometry. This is reported conservatively; see the paper's Discussion section for exact scope limits.

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
