# Consolidation note, 28 October 2026

**Certified SAT Covering-Radius Measurement: Representation Invariance and
Lazy-Constraint Experiments** — Elias De Jesus.

`main.tex` + `references.bib` + `tables_generated.tex` build
`certified-covering-radius-measurement-2026-10-28.pdf`.

## Building

```
python3 ../../extensions/lazy-constraints-2026-10-28/src/maketables.py > tables_generated.tex
latexmk -pdf main.tex
```

`tables_generated.tex` is **generated, not written**: every table in the note is
produced from the recorded measurement data by `maketables.py`. A copy is
committed so the PDF builds without rerunning anything.

## What this note is

A consolidation of two follow-up studies to the antecedent paper
(`paper/algorithmic_resolution_sat_v2.pdf`, Zenodo
[10.5281/zenodo.23038050](https://doi.org/10.5281/zenodo.23038050)). It is a
technical report, not a new theory. Its central additive inequality is
**classical** — Cohen, Karpovsky, Mattson and Schatz (1985), Corollary 1 — and
the note says so.

## Roles of the cited prior work

| work | role here |
|---|---|
| De Jesus, *Algorithmic Resolution…* ([10.5281/zenodo.23038050](https://doi.org/10.5281/zenodo.23038050)) | **antecedent**: source of the observable, the measurement programme, and the comparisons this note qualifies |
| De Jesus, *Encoding-Relative Variance (ERV) Barrier* ([10.5281/zenodo.18269283](https://doi.org/10.5281/zenodo.18269283)) | cited **only** for constraint-count observables being encoding-relative, with three scope corrections stated in §5. Not treated as a P-vs-NP barrier, and not treated as predicting any later result |
| Cohen–Karpovsky–Mattson–Schatz 1985 | **prior art** for the additive-`p` covering-radius bound |
| Bryant–Tan–Heule, SAT 2025 | certifies hypothesis (H1); their Skolem assignments *construct* a lift for a chosen sample but do not certify (H2) for an arbitrary recorded sample |
| Sinz 2005 | the cardinality encoding actually used |
| Wetzler–Heule–Hunt 2014 | the proof checker actually used |
| Dantzig–Fulkerson–Johnson 1954; Clarke et al. 2000, 2002 | constraint-generation / abstraction-refinement precedent for the lazy loop |

## Scope

No new SAT algorithm, no complexity-class consequence, no asymptotic claim, no
solver ranking. The ETH interface analysis explored separately in October 2026 is
**not** included: it is conditional on an unverified preprint and is not needed
for any result here.
