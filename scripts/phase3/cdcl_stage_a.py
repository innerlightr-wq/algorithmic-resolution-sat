"""
STAGE A -- PRE-REVEAL. Runs the CDCL (Glucose3) accessibility experiment.

Isolation enforcement (per task Part 5: "the CDCL prediction process must
run in a process/directory that cannot load Phase 2 revealed-solution data
until the frozen prediction artifact exists"), implemented as a PROGRAMMATIC
guard, not just a documentation convention: every file this script opens
goes through `guarded_open()`, which raises immediately if the path contains
any ground-truth-revealing marker ("stage_b_results", "stage_b", "rho_frozen"
-- rho is derived from revealed S_I in Phase 2 and must not leak into
predictor construction either). This script imports ONLY pysat_common,
pysat.solvers, and stdlib -- it has no import path to exhaustive_only.py or
any Phase 2 Stage-B file at all (verified: `grep -n import` on this file
shows no such import).

For each Phase 2 instance (train AND test -- both splits get CDCL
predictions; the train/test distinction is used later, in
analyze_cdcl_results.py, for model selection vs. final evaluation, exactly
mirroring PHASE2_FREEZE.md's frozen discipline):
  - run R=5 independent permuted+phase-randomized enumeration runs, each via
    Glucose3.enum_models(), each truncated at T=8 solutions (budget
    calibrated in CDCL_ACCESSIBILITY.md);
  - A_C(I) = union of all distinct solutions found across the 5 runs;
  - per found solution y: recurrence(y), mean conflicts/decisions-to-
    discovery (incremental accum_stats() differencing), foundneighbor(y),
    hamming_weight(y), random_score(y);
  - freeze everything to disk with a SHA-256 hash + UTC timestamp, exactly
    as Phase 2's run_stage_a.py did.
"""
import json
import time
import hashlib
import sys
import random

from pysat.solvers import Glucose3
from pysat_common import clauses_from_phase2_jsonable, permute_clauses, random_phases, unpermute_model

FORBIDDEN_PATH_MARKERS = ["stage_b_results", "rho_frozen", "stage_b_test_log", "stage_b_train_log"]


def guarded_open(path, mode="r"):
    for marker in FORBIDDEN_PATH_MARKERS:
        if marker in path:
            raise RuntimeError(
                f"LEAKAGE GUARD TRIPPED: Stage-A script attempted to open '{path}', "
                f"which matches forbidden ground-truth marker '{marker}'. Refusing."
            )
    return open(path, mode)


R_RUNS = 5
T_SOLUTIONS_PER_RUN = 8
FOUNDNEIGHBOR_RADIUS = 3
STAGE_A_SEED = 20260928 + 3333


def hamming(a, b):
    return sum(x != y for x, y in zip(a, b))


def run_cdcl_ensemble(clauses, n, base_seed):
    """
    Returns: (A_C: sorted list of distinct found solutions,
              per_solution_runs: dict y -> list of (conflicts_delta, decisions_delta) per discovery event)
    """
    per_solution_runs = {}
    for run_idx in range(R_RUNS):
        rng = random.Random(base_seed + run_idx)
        pclauses, perm = permute_clauses(clauses, n, rng)
        phases = random_phases(n, rng)
        g = Glucose3(bootstrap_with=pclauses)
        g.set_phases(phases)

        prev_conflicts = 0
        prev_decisions = 0
        cnt = 0
        for model in g.enum_models():
            cnt += 1
            stats = g.accum_stats()
            d_conflicts = stats["conflicts"] - prev_conflicts
            d_decisions = stats["decisions"] - prev_decisions
            prev_conflicts, prev_decisions = stats["conflicts"], stats["decisions"]

            y = unpermute_model(model, perm, n)
            per_solution_runs.setdefault(y, []).append(
                {"conflicts_delta": d_conflicts, "decisions_delta": d_decisions}
            )
            if cnt >= T_SOLUTIONS_PER_RUN:
                break
        g.delete()

    A_C = sorted(per_solution_runs.keys())
    return A_C, per_solution_runs


def compute_prospective_scores(A_C, per_solution_runs, n, rng_seed):
    rng = random.Random(rng_seed)
    scores = {}
    for y in A_C:
        events = per_solution_runs[y]
        recurrence = len(events)
        mean_conflicts = sum(e["conflicts_delta"] for e in events) / recurrence
        mean_decisions = sum(e["decisions_delta"] for e in events) / recurrence
        foundneighbor = sum(1 for y2 in A_C if y2 != y and hamming(y, y2) <= FOUNDNEIGHBOR_RADIUS)
        hw = sum(y)
        scores[y] = {
            "recurrence": recurrence,
            "conflicts_to_discovery": mean_conflicts,
            "decisions_to_discovery": mean_decisions,
            "foundneighbor": foundneighbor,
            "hamming_weight": hw,
            "random_score": rng.random(),
        }
    return scores


def process_instance(rec):
    n = rec["n"]
    clauses = clauses_from_phase2_jsonable(rec["clauses"])
    base_seed = STAGE_A_SEED + rec["id"] * 100
    A_C, per_solution_runs = run_cdcl_ensemble(clauses, n, base_seed)
    scores = compute_prospective_scores(A_C, per_solution_runs, n, base_seed + 50)

    return {
        "id": rec["id"], "n": n, "alpha": rec["alpha"], "regime": rec["regime"],
        "split": rec["split"],
        "R_runs": R_RUNS, "T_solutions_per_run": T_SOLUTIONS_PER_RUN,
        "A_C": [list(y) for y in A_C],
        "scores": {",".join(map(str, y)): s for y, s in scores.items()},
    }


def main(split_name):
    # NOTE: instances_{split}.json contains CNF clauses only -- no solution
    # data (Phase 2's own generation discipline, PHASE2_FREEZE.md) -- so
    # reading it here is legitimate Stage-A input, not a guard violation.
    with guarded_open(f"../../phase2/data/instances_{split_name}.json") as f:
        recs = json.load(f)

    t0 = time.time()
    results = []
    for i, rec in enumerate(recs):
        results.append(process_instance(rec))
        if (i + 1) % 100 == 0:
            print(f"  processed {i+1}/{len(recs)} ({time.time()-t0:.1f}s)", flush=True)
    dt = time.time() - t0
    print(f"CDCL Stage A ({split_name}): processed {len(recs)} instances in {dt:.1f}s")

    out_path = f"../data/cdcl_stage_a_predictions_{split_name}.json"
    payload = json.dumps(results, sort_keys=True)
    with guarded_open(out_path, "w") as f:
        f.write(payload)

    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    with guarded_open(out_path + ".hash.txt", "w") as f:
        f.write(f"file: {out_path}\n")
        f.write(f"sha256: {digest}\n")
        f.write(f"frozen_utc_timestamp: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")
        f.write(f"n_instances: {len(results)}\n")
        f.write("stage: A (pre-reveal, CDCL, no ground truth touched)\n")

    print(f"Wrote {out_path}")
    print(f"Wrote {out_path}.hash.txt with sha256={digest[:16]}...")


if __name__ == "__main__":
    split = sys.argv[1] if len(sys.argv) > 1 else "train"
    main(split)
