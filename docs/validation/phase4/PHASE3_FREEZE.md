# PHASE3_FREEZE.md — Phase 4, Part 1

SHA-256 checksums for every Phase 3 top-level deliverable, script, and data file, computed **before** any Phase 4 code was written. Full listing: `data/phase3_checksums.txt` (54 files). Phase 3 (and Phase 1, Phase 2) files are not touched anywhere in Phase 4 — any Phase 4 script needing Phase 3 data only **reads** the files listed here.

## Headline Phase 3 results, frozen verbatim (not altered retroactively)

| Result | Value | Source |
|---|---|---|
| WalkSAT held-out blind-zone predictor (`risk_basin`) | test median AUROC **0.658** `[0.636, 0.685]` | `phase2/data/analyze_results_output.txt` (reproduced in Phase 3 `CROSS_PREDICTION.md` test 1) |
| CDCL/Glucose3 held-out blind-zone predictor (`risk_cdcl_recurrence`) | test median AUROC **0.667** `[0.647, 0.700]` | `phase3/CDCL_RESULTS.md`, `phase3/data/analyze_cdcl_results_output.txt` |
| WalkSAT → CDCL cross-prediction | **0.625** `[0.599, 0.667]` | `phase3/CROSS_PREDICTION.md`, `phase3/data/part9_output.txt` |
| CDCL → WalkSAT cross-prediction | **0.526** `[0.487, 0.567]` | `phase3/CROSS_PREDICTION.md`, `phase3/data/part9_output.txt` |
| CDCL apparent fragmentation vs. WalkSAT at matched coverage | **approximately 4–13× lower** (instance 619: `37→8`, ~4.6×; instance 537: `118→9`, ~13.1×) | `phase3/BUDGET_TRAJECTORIES.md`, `phase3/data/part11_cdcl_output.txt` + `phase2/data/part11_output.txt` |
| Portfolio: union improves `ε̂` | **15.6%** (`56/360`) of test instances, strictly | `phase3/PORTFOLIO_GEOMETRY.md`, `phase3/data/part10_output.txt` |

These six numbers are the fixed reference points for every comparison made in this phase. Phase 4 may **explain, stratify, or contextualize** them (Parts 6–13) but does **not** re-run or overwrite the underlying Phase 2/3 computations — any Phase 4 script that needs the raw per-instance data reads the existing frozen JSON files (`phase2/data/stage_b_results_*.json`, `phase3/data/cdcl_stage_b_results_*.json`, `phase3/data/part7_cross_solver_geometry.json`, `phase3/data/part9_cross_prediction.json`, etc.) directly.

## Note on the fragmentation figure's exact wording (flagged for `FRAGMENTATION_REPLICATION_AUDIT.md`)

The "4–13×" figure was computed from **two pre-specified instances only** (Phase 2/3's paired budget-trajectory instances, ids 537 and 619) — it was never a claim about the full 360-instance test set. Part 12 of this phase audits whether this two-instance figure generalizes or needs narrower wording before it can safely appear in an Abstract.
