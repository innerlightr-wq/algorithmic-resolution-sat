"""
STAGE B -- REVEAL. Verifies the CDCL Stage-A hash first, then:
  - re-derives S_I fresh via Phase 2's exhaustive_only module (imported here
    only -- never from cdcl_stage_a.py or pysat_common.py);
  - reads Phase 2's OWN frozen WalkSAT Stage-A output (A_W(I) per instance)
    for cross-solver comparison -- legitimate at Stage B (reveal) time;
  - reads Phase 2's frozen rho (analysis-stage constant, not part of
    predictor construction);
  - computes CDCL's own retrospective quantities (A_C(I), M_C(I), eps_hat_C,
    coverage_C, miss_rho per CDCL-found solution) and cross-solver
    quantities (M_W(I), overlap, union coverage) needed by Parts 6-11.

Writes phase3/data/cdcl_stage_b_results_{split}.json.
"""
import json
import sys
import time
import hashlib
import numpy as np

sys.path.insert(0, "../../phase2/scripts")
from exhaustive_only import solve_all_exhaustive
from sat_common import clauses_from_jsonable as phase2_clauses_from_jsonable


def verify_hash(split):
    path = f"../data/cdcl_stage_a_predictions_{split}.json"
    with open(path) as f:
        content = f.read()
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    with open(path + ".hash.txt") as f:
        hash_file_content = f.read()
    assert digest[:16] in hash_file_content or digest in hash_file_content, \
        f"HASH MISMATCH for {path} -- CDCL Stage A predictions do not match frozen hash!"
    print(f"CDCL Stage A hash verified for split={split}: sha256={digest[:16]}...")
    return json.loads(content)


def hamming(a, b):
    return sum(x != y for x, y in zip(a, b))


def main():
    split = sys.argv[1] if len(sys.argv) > 1 else "train"

    cdcl_stage_a = verify_hash(split)
    cdcl_by_id = {r["id"]: r for r in cdcl_stage_a}

    with open(f"../../phase2/data/instances_{split}.json") as f:
        instances = json.load(f)
    instances_by_id = {r["id"]: r for r in instances}

    with open(f"../../phase2/data/stage_a_predictions_{split}.json") as f:
        walksat_stage_a = json.load(f)
    walksat_by_id = {r["id"]: r for r in walksat_stage_a}

    with open("../../phase2/data/rho_frozen.json") as f:
        rho = json.load(f)["rho"]
    print(f"Using Phase 2 frozen rho={rho} (train-derived, reused unchanged per PHASE2_FREEZE.md)")

    out_records = []
    t0 = time.time()
    for i, rec in enumerate(cdcl_stage_a):
        iid = rec["id"]
        inst = instances_by_id[iid]
        n = inst["n"]
        clauses = phase2_clauses_from_jsonable(inst["clauses"])
        S_I = solve_all_exhaustive(clauses, n)
        S_I_set = set(S_I)

        A_C = [tuple(y) for y in rec["A_C"]]
        A_C_set = set(A_C)
        assert A_C_set <= S_I_set, f"instance {iid}: A_C(I) not subset of S_I -- CDCL/exhaustive mismatch!"
        M_C = list(S_I_set - A_C_set)

        A_W = [tuple(y) for y in walksat_by_id[iid]["A_I"]]
        A_W_set = set(A_W)
        M_W = list(S_I_set - A_W_set)

        eps_hat_C = max((min(hamming(x, y) for y in A_C) for x in S_I), default=None) if A_C else None
        eps_hat_W = max((min(hamming(x, y) for y in A_W) for x in S_I), default=None) if A_W else None

        per_y = []
        for y in A_C:
            miss_count = sum(1 for x in M_C if hamming(x, y) <= rho)
            scores = rec["scores"][",".join(map(str, y))]
            per_y.append({
                "y": list(y), "miss_rho": miss_count,
                "has_missed_neighbor": int(miss_count > 0),
                **scores,
            })

        # cross-solver set quantities
        M_W_set, M_C_set = set(M_W), set(M_C)
        inter = M_W_set & M_C_set
        union = M_W_set | M_C_set
        jaccard = len(inter) / len(union) if union else None

        A_union = A_W_set | A_C_set
        eps_hat_union = max((min(hamming(x, y) for y in A_union) for x in S_I), default=None) if A_union else None

        out_records.append({
            "id": iid, "n": n, "alpha": inst["alpha"], "regime": inst["regime"], "split": split,
            "S_I_size": len(S_I),
            "A_C_size": len(A_C), "M_C_size": len(M_C), "coverage_C": len(A_C) / len(S_I) if S_I else None,
            "eps_hat_C": eps_hat_C,
            "A_W_size": len(A_W), "M_W_size": len(M_W), "coverage_W": len(A_W) / len(S_I) if S_I else None,
            "eps_hat_W": eps_hat_W,
            "M_W": [list(x) for x in M_W], "M_C": [list(x) for x in M_C],
            "S_I": [list(x) for x in S_I],
            "jaccard_MW_MC": jaccard,
            "M_W_size_check": len(M_W), "M_C_size_check": len(M_C),
            "intersection_size": len(inter), "union_size": len(union),
            "A_union_size": len(A_union), "coverage_union": len(A_union) / len(S_I) if S_I else None,
            "eps_hat_union": eps_hat_union,
            "rho_used": rho,
            "per_found_solution_C": per_y,
        })
        if (i + 1) % 100 == 0:
            print(f"  Stage B processed {i+1}/{len(cdcl_stage_a)} ({time.time()-t0:.1f}s)", flush=True)

    dt = time.time() - t0
    print(f"CDCL Stage B ({split}): processed {len(out_records)} instances in {dt:.1f}s")

    out_path = f"../data/cdcl_stage_b_results_{split}.json"
    with open(out_path, "w") as f:
        json.dump(out_records, f)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
