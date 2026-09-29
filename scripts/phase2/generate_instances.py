"""
Generates satisfiable random 3-SAT instances for the Phase 2 decisive
experiment and splits them into train/test sets BY INSTANCE (never by
solution -- required by EXPERIMENT_PROTOCOL.md Part 7).

SELECTION EFFECT, documented explicitly per task instruction: instances are
filtered to satisfiable ones using exhaustive_only.is_satisfiable() at
GENERATION time, before any train/test split and before Stage A ever runs.
This exhaustive check is discarded immediately after filtering -- the actual
solution set S_I computed here is NOT written to the instances file and NOT
passed to Stage A; Stage A receives only the CNF clauses. Stage B
re-enumerates S_I fresh from the clauses. This keeps the process boundary
clean even though satisfiability-filtering technically "touches" ground
truth once, at generation time, exactly as the January 2026 paper's own
protocol does ("50 satisfiable instances per condition") -- we are not
introducing a new selection effect, only making the existing one explicit
and structurally isolated from the predictor-construction pipeline.

Output: data/instances_train.json, data/instances_test.json
  Each entry: {id, n, alpha, m_clauses, clauses (jsonable), split}
  NO solution/S_I data included.
"""
import json
import sys
import time
import numpy as np

from sat_common import random_3sat_clauses, clauses_to_jsonable
from exhaustive_only import is_satisfiable

SEED = 20260928 + 2  # distinct from phase 1's seed, this is a fresh experiment

def generate_cell(n, alpha, n_needed, rng, max_attempts_factor=6, label=""):
    m = int(round(alpha * n))
    instances = []
    attempts = 0
    max_attempts = n_needed * max_attempts_factor
    t0 = time.time()
    while len(instances) < n_needed and attempts < max_attempts:
        attempts += 1
        clauses = random_3sat_clauses(n, m, rng)
        if is_satisfiable(clauses, n):
            instances.append(clauses)
    dt = time.time() - t0
    print(f"  [{label}] n={n} alpha={alpha}: got {len(instances)}/{n_needed} "
          f"in {attempts} attempts ({dt:.1f}s)", flush=True)
    if len(instances) < n_needed:
        print(f"  WARNING: only found {len(instances)}/{n_needed} satisfiable "
              f"instances for n={n},alpha={alpha} within {max_attempts} attempts", flush=True)
    return instances


def main():
    rng = np.random.default_rng(SEED)

    n_values = [16, 18, 20]
    alpha_regimes = {
        "solution_rich": 2.5,
        "intermediate": 3.5,
        "near_threshold": 4.2,
    }
    n_train_per_cell = 40
    n_test_per_cell = 40

    train_records = []
    test_records = []
    instance_id = 0

    for n in n_values:
        for regime, alpha in alpha_regimes.items():
            needed = n_train_per_cell + n_test_per_cell
            instances = generate_cell(n, alpha, needed, rng, label=f"{regime}")
            # split deterministically: first n_train -> train, rest -> test
            for i, clauses in enumerate(instances):
                split = "train" if i < n_train_per_cell else "test"
                rec = {
                    "id": instance_id,
                    "n": n,
                    "alpha": alpha,
                    "regime": regime,
                    "m_clauses": len(clauses),
                    "clauses": clauses_to_jsonable(clauses),
                    "split": split,
                }
                if split == "train":
                    train_records.append(rec)
                else:
                    test_records.append(rec)
                instance_id += 1

    with open("../data/instances_train.json", "w") as f:
        json.dump(train_records, f)
    with open("../data/instances_test.json", "w") as f:
        json.dump(test_records, f)

    print(f"\nWrote {len(train_records)} train instances, {len(test_records)} test instances.")
    print("NOTE: these files contain CNF clauses only -- no solution/S_I data.")

if __name__ == "__main__":
    main()
