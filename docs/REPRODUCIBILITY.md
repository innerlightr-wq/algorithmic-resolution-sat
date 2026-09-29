# REPRODUCIBILITY.md

## Environment

- Python 3.12.2
- Dependencies pinned in `requirements.txt` (exact versions from the environment that produced every reported number):
  `python-sat==1.9.dev15`, `numpy==1.26.4`, `scipy==1.13.1`, `scikit-learn==1.5.1`, `matplotlib==3.9.2`, `networkx==3.3`.
- **Solver dependency**: `python-sat` (PySAT) wraps genuine, unmodified upstream solver source (Glucose3 among others) as a compiled extension — no separate Glucose install is needed; `pip install python-sat` (or `pip install -r requirements.txt`) is sufficient.
- LaTeX: TeX Live 2026 (`pdflatex`, `bibtex`); tested against a BasicTeX install with `orcidlink`, `natbib`, `hyperref`, `booktabs`, `microtype`, `subcaption`, `enumitem`, `amsthm`, `geometry`, `caption` installed via `tlmgr --usermode install <pkg>` (no admin rights required).

## Directory map and provenance

```
scripts/phase2/   WalkSAT solver, instance generation, exhaustive ground truth, Hamming-ball
                   and coverage/resolution family verification, Stage A/B freeze-before-reveal
                   pipeline, topology utilities (0-dim persistence / cluster spectrum).
scripts/phase3/   CDCL (Glucose3) accessibility experiment, cross-solver geometry, portfolio
                   analysis, H0 sharpness extremal construction, fragmentation theorem verification.
scripts/phase4/   Cross-solver confound audit: conditional models, residualization,
                   fragmentation replication across the full held-out test set.
scripts/figures/  generate_figures.py -- produces every figure in paper/figures/ from the
                   frozen data below.
data/phase2/      Frozen results: instance definitions (instances_{train,test}.json),
                   held-out prediction results, Hamming-ball / coverage-resolution
                   verification logs, persistence-stability validation, budget trajectories.
data/phase3/      Frozen results: CDCL prediction results, cross-solver overlap/portfolio/
                   cross-prediction analyses, sharpness and fragmentation-theorem verification.
data/phase4/      Frozen results: confound-audit and fragmentation-replication outputs
                   underlying the paper's central Section 10 claims.
```

**Not included in this repository** (regenerable, excluded to keep the repository lean per the request that this not become a dump of the full scratch audit): the large raw per-solution JSON files (`stage_a_predictions_*.json`, `stage_b_results_*.json`, `cdcl_stage_a_predictions_*.json`, `cdcl_stage_b_results_*.json`, `wc_dataset.json`, `cw_dataset.json` — collectively ~65MB across phases). These are fully regenerable from `data/phase2/instances_{train,test}.json` (the frozen CNF instance definitions, which *are* included) by running the Stage A/B scripts below in order; they remain available in the original frozen audit directory `~/scratch/sat-algorithmic-resolution-v2-audit-2026-09-28/` for anyone with access to that machine, and are referenced by exact path throughout `docs/validation/`.

## Reproducing the reported computations, in order

```bash
pip install -r requirements.txt

cd scripts/phase2
python3 generate_instances.py                 # regenerates the 720 instances (fixed seed)
python3 run_stage_a.py train && python3 run_stage_a.py test    # WalkSAT, freeze-before-reveal
python3 run_stage_b.py train && python3 run_stage_b.py test    # reveal + evaluate
python3 analyze_results.py                     # WalkSAT held-out AUROC (Table 1, paper)
python3 hamming_ball_theorem_verify.py         # Theorem 4.1 exhaustive verification
python3 coverage_resolution_families.py        # Propositions 5.1-5.2 verification
python3 part10_topology_validation.py          # persistence-stability check, 349 instances

cd ../phase3
python3 cdcl_stage_a.py train && python3 cdcl_stage_a.py test  # CDCL, freeze-before-reveal
python3 cdcl_stage_b.py train && python3 cdcl_stage_b.py test  # reveal + evaluate
python3 analyze_cdcl_results.py                # CDCL held-out AUROC (Table 1, paper)
python3 h0_sharpness_extremal.py               # Proposition 6.3 sharpness verification
python3 part7_8_cross_solver_geometry.py       # overlap/decomposition analysis
python3 part9_cross_prediction.py              # raw cross-prediction numbers (Section 9)
python3 part10_portfolio.py                    # Appendix D portfolio geometry

cd ../phase4
python3 build_cross_solver_dataset.py          # per-solution dataset for confound audit
python3 confound_and_conditional_analysis.py   # Section 9's retraction evidence
python3 fragmentation_replication.py           # Section 10 / Table 4's central result

cd ../figures
python3 generate_figures.py                    # regenerates every figure in paper/figures/
```

Each script prints its own output and writes results to the corresponding `data/phaseN/` file; comparing a fresh run's output against the frozen `data/phaseN/*_output.txt` files is the intended sanity check. Random-3-SAT generation uses fixed seeds (documented in each script), so instance sets reproduce exactly; the CDCL search-order permutation seeds are likewise fixed per-instance, so held-out AUROC values should reproduce to within floating-point/bootstrap-resampling noise (the bootstrap CI and permutation-test routines use `numpy.random.default_rng` with a fixed seed each).

## Distinction: frozen raw data vs. generated figures

All seven figures in `paper/figures/` are generated fresh by `scripts/figures/generate_figures.py` reading only from files under `data/` (or, when run against the original scratch audit tree, its fuller data directories) — no figure is hand-edited or touched after generation. The frozen `data/phaseN/*.json` and `*_output.txt` files are the authoritative record of every number quoted in the manuscript; where a manuscript sentence cites a specific figure (e.g. "median ratio 11.6$\times$, 95% CI [9.6, 13.3]"), that number can be found verbatim in the corresponding `data/phase4/fragmentation_replication_output.txt` or similar file, traced in full in `docs/CLAIM_EVIDENCE_AUDIT.md`.
