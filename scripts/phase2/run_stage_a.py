"""
STAGE A -- PRE-REVEAL. Imports ONLY sat_common and walksat_solver; does NOT
import exhaustive_only anywhere (verified structurally: `import exhaustive`
does not appear in this file, and Python's import system means it is simply
impossible for this process to touch S_I unless that line is added -- an
auditable, not just documented, guarantee).

For each instance (both train and test instances -- the train/test split is
about which instances are used for MODEL SELECTION vs FINAL EVALUATION in
run_stage_b.py / select_and_evaluate.py, not about which instances Stage A
is allowed to process):
  1. Run K independent WalkSAT restarts -> found solutions A(I) + trajectory
     summaries (converged assignment, flip count, per restart).
  2. From A(I) and the restart log ONLY, compute per-found-solution
     prospective risk scores (ACCESSIBILITY_FRAMEWORK.md Section 4):
       - basin(y): count of restarts converging exactly to y
       - disc_flips(y): mean flips-to-discovery among restarts finding y
       - foundneighbor(y): count of other found solutions within radius rho
       - hamming_weight(y): baseline, y's own Hamming weight
       - random_score(y): baseline, iid random number (fixed seed, frozen)
  3. Freeze everything to disk as JSON, log a SHA-256 hash and UTC timestamp
     of the frozen file's content in a companion .hash.txt file, BEFORE any
     Stage B script is invoked (enforced by this being a wholly separate
     process invocation in run_experiment.sh, not merely a separate function
     call within one long-running script).
"""
import json
import time
import hashlib
import sys
import numpy as np

from sat_common import clauses_from_jsonable, hamming
from walksat_solver import walksat_multi_restart

K_RESTARTS = 150
MAX_FLIPS = 3000
P_NOISE = 0.5
FOUNDNEIGHBOR_RADIUS = 3  # fixed constant, not tuned on any data
STAGE_A_SEED = 20260928 + 777


def compute_prospective_scores(runs, n, found_solutions):
    """
    runs: list of {"found","assignment","flips"} from walksat_multi_restart
    found_solutions: sorted list of distinct assignments (tuples) that were
      found by at least one restart -- this IS A(I), constructed here purely
      from `runs`, never from any external ground truth.
    Returns: dict y (as string key) -> {predictor_name: score}
    """
    rng = np.random.default_rng(STAGE_A_SEED)  # frozen, deterministic given instance order

    basin_count = {y: 0 for y in found_solutions}
    flip_list = {y: [] for y in found_solutions}
    for r in runs:
        if r["found"]:
            y = r["assignment"]
            basin_count[y] += 1
            flip_list[y].append(r["flips"])

    scores = {}
    for y in found_solutions:
        disc_flips = float(np.mean(flip_list[y])) if flip_list[y] else float(MAX_FLIPS)
        foundneighbor = sum(
            1 for y2 in found_solutions
            if y2 != y and hamming(y, y2) <= FOUNDNEIGHBOR_RADIUS
        )
        hw = sum(y)
        scores[y] = {
            "basin": basin_count[y],
            "disc_flips": disc_flips,
            "foundneighbor": foundneighbor,
            "hamming_weight": hw,
            "random_score": float(rng.random()),
        }
    return scores


def process_instance(rec):
    n = rec["n"]
    clauses = clauses_from_jsonable(rec["clauses"])
    rng = np.random.default_rng(STAGE_A_SEED + rec["id"])
    runs = walksat_multi_restart(clauses, n, K=K_RESTARTS, max_flips=MAX_FLIPS,
                                  p_noise=P_NOISE, rng=rng)
    found_solutions = sorted(set(r["assignment"] for r in runs if r["found"]))
    scores = compute_prospective_scores(runs, n, found_solutions)

    n_restarts_found = sum(1 for r in runs if r["found"])
    return {
        "id": rec["id"],
        "n": n,
        "alpha": rec["alpha"],
        "regime": rec["regime"],
        "split": rec["split"],
        "K_restarts": K_RESTARTS,
        "max_flips": MAX_FLIPS,
        "n_restarts_that_found_a_solution": n_restarts_found,
        "A_I": [list(y) for y in found_solutions],
        "scores": {",".join(map(str, y)): s for y, s in scores.items()},
    }


def main(split_name):
    with open(f"../data/instances_{split_name}.json") as f:
        recs = json.load(f)

    t0 = time.time()
    results = []
    for i, rec in enumerate(recs):
        results.append(process_instance(rec))
        if (i + 1) % 100 == 0:
            print(f"  processed {i+1}/{len(recs)} ({time.time()-t0:.1f}s)", flush=True)
    dt = time.time() - t0
    print(f"Stage A ({split_name}): processed {len(recs)} instances in {dt:.1f}s")

    out_path = f"../data/stage_a_predictions_{split_name}.json"
    payload = json.dumps(results, sort_keys=True)
    with open(out_path, "w") as f:
        f.write(payload)

    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    with open(out_path + ".hash.txt", "w") as f:
        f.write(f"file: {out_path}\n")
        f.write(f"sha256: {digest}\n")
        f.write(f"frozen_utc_timestamp: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")
        f.write(f"n_instances: {len(results)}\n")
        f.write(f"stage: A (pre-reveal, no ground truth touched)\n")

    print(f"Wrote {out_path}")
    print(f"Wrote {out_path}.hash.txt with sha256={digest[:16]}...")


if __name__ == "__main__":
    split = sys.argv[1] if len(sys.argv) > 1 else "train"
    main(split)
