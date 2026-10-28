# v0.3.0 — Certified covering-radius measurement: representation invariance and lazy constraints

This release consolidates the October 2026 follow-up work on the certified
covering-radius measurement programme, and adds a citable technical report.

## What is new

**A consolidation note** — *Certified SAT Covering-Radius Measurement:
Representation Invariance and Lazy-Constraint Experiments* — in
`notes/consolidation-2026-10-28/`, with LaTeX source, bibliography, generated
tables and a compiled PDF.

**Two extensions:**

- `extensions/representation-invariance-2026-10-28/` — how covering-radius
  resolution behaves under solution-preserving re-encoding, and a margin
  criterion for certified comparisons.
- `extensions/lazy-constraints-2026-10-28/` — two implementation studies:
  witness tightening, and lazy distance-constraint generation.

**Supporting material:** `CLAIM_EVIDENCE_MAP.md`, an appendix to
`docs/SOURCE_OF_TRUTH.md` identifying the current source of truth, updated
`CITATION.cff` carrying the verified DOIs of the two antecedent works.

## Results, stated plainly

- Measured on the **original** variables, `ε̂` is exactly invariant under
  solution-preserving re-encoding. Measured on **all** variables it moves by at
  most the number of auxiliary variables, and that bound is attained. **The
  additive inequality is classical** (Cohen, Karpovsky, Mattson & Schatz 1985,
  Corollary 1); the solution-relative form and the margin criterion are what
  this work adds.
- Of 116 certified comparisons in this repository, **43 carry no guarantee
  beyond zero auxiliary variables**.
- **Witness tightening** is sound on all 594 stored witnesses but improves
  **0 of 257** reconstructed measurements.
- **Lazy distance-constraint generation** is exact and terminates using
  **3–43 %** of the distance constraints. On the three units that pass pairing
  verification it cuts total time including certification from **46.0 s to
  18.9 s**; on the five units that do not resolve it is **worse**, with summed
  interval widths 46 (static) against 60 (lazy).

## Corrections carried in this release

Six claims from earlier drafts are corrected or retracted, each recorded in
`docs/SOURCE_OF_TRUTH.md` Appendix D-C: the margin language, the treatment of
certified intervals bounded only below, the inference that invariance precludes
a cheaper computation, the inference that removing constraints lengthens proofs,
the GF(2) closure-size formula, and the use of equal query counts as evidence of
pairing.

## What this release does **not** claim

No new SAT algorithm. No complexity-class consequence or P-versus-NP
implication. No asymptotic improvement. No general speedup for lazy constraints.
No solver ranking — the retracted cross-solver predictive claim (`C1`) and the
portfolio-superiority claim (`C7`) remain retracted. No priority claim from any
date printed in a PDF.

## Reproducing

Tables regenerate from recorded data with no solver:

```
python3 extensions/lazy-constraints-2026-10-28/src/maketables.py --markdown
```

Environment actually used: CPython 3.14.7, python-sat 1.9.dev15, Glucose 3,
sequential-counter cardinality encoding (Sinz 2005), DRUP proofs checked by
`drat-trim` at commit `2e3b2dc0ecf938addbd779d42877b6ed69d9a985`.

The full certificate set (~209 MB of CNFs and proofs) is not in Git; proofs for
the verified-paired units ship in
`extensions/lazy-constraints-2026-10-28/certificates/`. Tables regenerate from
the shipped data; independent re-verification of **all** certificates does not.
