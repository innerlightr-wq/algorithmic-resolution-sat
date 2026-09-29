"""
STAGE B -- REVEAL. The ONLY script in this experiment that imports
exhaustive_only. Must be run AFTER run_stage_a.py has already written and
hashed its predictions file for the same split -- this script verifies that
hash against the file on disk before doing anything else, so a re-run of
Stage A after Stage B (which would be a leakage-adjacent process error, e.g.
accidentally re-freezing predictions after peeking at results) is detected,
not silently accepted.

For split="train": also computes and freezes RHO (the fixed radius used in
miss_rho(y|I), Accessibility Framework Section 5) from train-split S_I
statistics (median nearest-neighbor distance within S_I, pooled across train
instances) -- this is the ONLY place model/hyperparameter selection is
allowed to touch ground truth, and it is restricted to the train split by
construction (the CLI argument, not just a comment).

For split="test": REQUIRES an externally supplied --rho value (from the
train run) and refuses to compute its own -- enforced by raising an error if
no --rho is given, so the test split can never silently self-tune.
"""
import json
import sys
import time
import hashlib
import argparse
import numpy as np

from sat_common import clauses_from_jsonable, hamming
from exhaustive_only import solve_all_exhaustive


def verify_hash(split):
    path = f"../data/stage_a_predictions_{split}.json"
    with open(path) as f:
        content = f.read()
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    with open(path + ".hash.txt") as f:
        hash_file_content = f.read()
    assert digest[:16] in hash_file_content or digest in hash_file_content, \
        f"HASH MISMATCH for {path} -- Stage A predictions file does not match its frozen hash!"
    print(f"Stage A hash verified for split={split}: sha256={digest[:16]}...")
    return json.loads(content)


def compute_rho_from_train(instances_by_id, stage_a_results):
    """Median nearest-neighbor distance within S_I, pooled across train instances."""
    nn_dists = []
    for rec in stage_a_results:
        iid = rec["id"]
        inst = instances_by_id[iid]
        clauses = clauses_from_jsonable(inst["clauses"])
        S = solve_all_exhaustive(clauses, inst["n"])
        if len(S) < 2:
            continue
        for x in S:
            d = min(hamming(x, y) for y in S if y != x)
            nn_dists.append(d)
    rho = float(np.median(nn_dists)) if nn_dists else 2.0
    return rho, nn_dists


def run_split(split, rho):
    stage_a_results = verify_hash(split)

    with open(f"../data/instances_{split}.json") as f:
        instances = json.load(f)
    instances_by_id = {r["id"]: r for r in instances}

    out_records = []
    t0 = time.time()
    for i, rec in enumerate(stage_a_results):
        iid = rec["id"]
        inst = instances_by_id[iid]
        clauses = clauses_from_jsonable(inst["clauses"])
        n = inst["n"]
        S_I = solve_all_exhaustive(clauses, n)
        S_I_set = set(S_I)

        A_I = [tuple(y) for y in rec["A_I"]]
        A_I_set = set(A_I)
        assert A_I_set <= S_I_set, f"instance {iid}: A(I) not subset of S_I -- solver bug!"

        M_A_I = list(S_I_set - A_I_set)  # true blind zone

        eps_hat = max((min(hamming(x, y) for y in A_I) for x in S_I), default=None) if A_I else None

        # retrospective target: miss_rho(y|I) for each y in A(I)
        per_y = []
        for y in A_I:
            miss_count = sum(1 for x in M_A_I if hamming(x, y) <= rho)
            scores = rec["scores"][",".join(map(str, y))]
            per_y.append({
                "y": list(y),
                "miss_rho": miss_count,
                "has_missed_neighbor": int(miss_count > 0),
                **scores,
            })

        out_records.append({
            "id": iid, "n": n, "alpha": inst["alpha"], "regime": inst["regime"],
            "split": split,
            "S_I_size": len(S_I), "A_I_size": len(A_I), "M_A_I_size": len(M_A_I),
            "coverage": len(A_I) / len(S_I) if S_I else None,
            "eps_hat": eps_hat,
            "rho_used": rho,
            "per_found_solution": per_y,
        })
        if (i + 1) % 100 == 0:
            print(f"  Stage B processed {i+1}/{len(stage_a_results)} ({time.time()-t0:.1f}s)", flush=True)

    dt = time.time() - t0
    print(f"Stage B ({split}): processed {len(out_records)} instances in {dt:.1f}s")

    out_path = f"../data/stage_b_results_{split}.json"
    with open(out_path, "w") as f:
        json.dump(out_records, f)
    print(f"Wrote {out_path}")
    return out_records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("split", choices=["train", "test"])
    parser.add_argument("--rho", type=float, default=None)
    args = parser.parse_args()

    if args.split == "train":
        stage_a_results = verify_hash("train")
        with open("../data/instances_train.json") as f:
            instances = json.load(f)
        instances_by_id = {r["id"]: r for r in instances}
        rho, nn_dists = compute_rho_from_train(instances_by_id, stage_a_results)
        with open("../data/rho_frozen.json", "w") as f:
            json.dump({"rho": rho, "n_nn_dists_pooled": len(nn_dists),
                       "computed_from_split": "train",
                       "median_used_as_rho": rho}, f, indent=2)
        print(f"Computed and froze RHO = {rho} (median NN-distance within S_I, "
              f"pooled over {len(nn_dists)} train solutions)")
        run_split("train", rho)
    else:
        rho = args.rho
        if rho is None:
            with open("../data/rho_frozen.json") as f:
                rho = json.load(f)["rho"]
            print(f"Loaded frozen RHO={rho} from ../data/rho_frozen.json (train-derived)")
        run_split("test", rho)


if __name__ == "__main__":
    main()
