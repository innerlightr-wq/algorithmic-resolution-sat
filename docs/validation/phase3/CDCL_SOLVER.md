# CDCL_SOLVER.md — Phase 3, Part 2

## Solver identity

- **Package**: `python-sat` (PySAT), version `1.9.dev15`, installed via `pip install python-sat` (MIT license, github.com/pysathq/pysat), a maintained Python wrapper exposing genuine, unmodified upstream C/C++ SAT-solver source trees compiled as extension modules. Installed isolated to the user's local site-packages (`~/.local/lib/python3.12/site-packages`), no system-wide changes.
- **Primary solver used: Glucose 3** (`pysat.solvers.Glucose3`), a well-known, published, competition-grade CDCL solver (Audemard & Simon, based on MiniSat 2.2 with the "glue clause" / LBD-based clause-deletion and aggressive restart policy that distinguishes Glucose from vanilla MiniSat). This is genuine CDCL: clause learning via conflict analysis (first-UIP), VSIDS-style activity-based branching, Luby/geometric restarts, watched-literal unit propagation, LBD-based learned-clause management — **not** a homemade DPLL implementation. Confirmed by inspecting the exposed API (`accum_stats()` reports `restarts`, `conflicts`, `decisions`, `propagations` — internal CDCL counters, not DPLL bookkeeping) and by the enumerated-solution behavior matching expected CDCL search-tree traversal (non-lexicographic solution order, confirmed in the pilot run below).
- **Other solvers confirmed available in this install** (not all used, listed for completeness/future replication): `cadical103/153/195/300`, `kissat404`, `maplechrono`, `maplecm`, `maplesat`, `mergesat3`, `minisat22`, `minisatgh`, `gluecard3/4`, `cryptosat` (CryptoMiniSat), `lingeling`. Glucose3 was chosen over CaDiCaL/MapleSAT/Kissat (all more modern, often stronger competition solvers) specifically **because** it is a well-documented, widely-cited, "canonical" CDCL reference point with a simple, well-understood restart/branching design, making the accessibility-predictor interpretation (§`CDCL_ACCESSIBILITY.md`) easier to reason about; a second solver family is a natural Phase 4 extension, not attempted here (see `FINAL_GATE.md` Q18 for scoping discipline).

## Randomization capabilities actually used

Glucose3 (via PySAT) exposes **no direct RNG-seed parameter** for its internal search (confirmed: `inspect.signature(Glucose3.__init__)` → `bootstrap_with, use_timer, incr, with_proof, warm_start`, no `seed`). Two solver-legitimate randomization mechanisms are used instead, matching the task's explicitly sanctioned list:

1. **Variable relabeling + clause-order shuffling** ("controlled formula permutations that preserve the SAT instance mathematically"): a uniformly random bijection `π:\{1,...,n\}→\{1,...,n\}` relabels every literal, and the clause list is independently shuffled, before handing the CNF to a fresh solver instance. This is a mathematically exact symmetry of the SAT instance (identical solution set under the inverse relabeling) that changes VSIDS's initial activity ordering and the order conflict analysis examines clauses — confirmed empirically to change search dynamics (pilot run, `data/pilot_timing_output.txt`: three different seeds on the same instance produced three different first-discovered solutions and different conflict/decision counts, `94/1600` vs `105/1549` vs `97/1621`).
2. **Initial polarity (phase) randomization** ("polarity initialization"): `set_phases()` is called with a uniformly random `±1` sign per variable before solving, biasing (not forcing — Glucose's phase-saving can override after the first few decisions) the solver's default branch direction.

Both are applied together per independent run, with a fresh `random.Random(seed)` stream per run (`seed = base_seed + run_index`, documented per-instance in `CDCL_PROTOCOL.md`).

## Restart behavior

Glucose3's restart policy is its signature feature: LBD-based (Literal Block Distance) aggressive restarts, far more frequent than classical Luby restarts, triggered when recent conflict LBD trends indicate a "bad" search region. `accum_stats()['restarts']` is read directly from the solver as a genuine internal counter (not synthesized) — confirmed in the pilot to closely track the number of solve() calls under blocking-clause enumeration (since each new blocking clause typically forces at least one restart-equivalent re-solve).

## Branching heuristic

VSIDS (Variable State Independent Decaying Sum) activity-based branching, standard to the MiniSat/Glucose lineage — not exposed as a directly-tunable parameter via PySAT's API, but influenced by the initial variable order (permutation, above) since VSIDS activities start uniform and are shaped early by which clauses are encountered/learned first.

## Enumeration: native vs. blocking clauses

**Solution enumeration is native**: `Glucose3.enum_models(assumptions=[])` is a PySAT-provided generator that internally (a) calls `solve()`, (b) yields the model, (c) adds a blocking clause (negation of the found model) via the solver's own `add_clause`, (d) repeats until UNSAT. This is the standard, correct blocking-clause enumeration technique, implemented once inside PySAT itself (not reimplemented here) — confirmed correct on a small hand-checked 3-variable CNF (all 4 satisfying assignments recovered exactly, matching manual enumeration; `data/pilot_timing_output.txt`).

## Internal statistics accessible

`accum_stats()` → `{restarts, conflicts, decisions, propagations}`, cumulative counters read after each `solve()`/enumeration step (used to derive **incremental** per-solution conflict/decision counts by differencing consecutive readings — `CDCL_ACCESSIBILITY.md` §2). No per-variable VSIDS activity or per-clause LBD is exposed through PySAT's Python API (checked: not in the `dir(g)` method list) — this rules out a direct "VSIDS activity" or "learned-clause participation" feature as originally suggested in the task's candidate list; the conflict/decision/restart counters actually exposed are used instead, documented here as the reason for that substitution rather than silently omitted.

## Performance confirmation

Pilot timing (`data/pilot_timing_output.txt`): enumerating `150` models from `n=20` Phase 2 instances completes in `~0.001s`; full exhaustive-style enumeration (up to `T=100` or until UNSAT) across all `720` Phase 2 instances, `R` independent permuted runs each, is confirmed computationally trivial relative to Phase 2's WalkSAT budget (`~135s` total for Phase 2's WalkSAT Stage A across both splits) — full run timing reported in `CDCL_PROTOCOL.md`/`CDCL_RESULTS.md`.
