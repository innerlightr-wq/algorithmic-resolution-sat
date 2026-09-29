"""
Phase 4, Parts 5-13 data preparation. Builds per-found-solution datasets for
the cross-solver confound analysis, using ONLY already-frozen Phase 2/3 data
(phase2/data/stage_b_results_test.json, phase3/data/cdcl_stage_b_results_test.json)
-- no re-running of Stage A/B, no new solver calls. This is retrospective
diagnostic analysis on already-revealed data (explicitly sanctioned by the
task's Part 6 item 10: "cluster membership AFTER reveal as a diagnostic
only"), NOT a new prospective-prediction pipeline, so no anti-leakage guard
is needed here -- everything used was already legitimately revealed in
Phase 2/3's own Stage B.

Produces two per-solution tables:
  wc_dataset: rows = (instance, y) for y in A_W(I) [WalkSAT-found]
              features = WalkSAT-derived (basin, disc_flips, foundneighbor_W,
                         hamming_weight) + shared/instance covariates
              target   = label_C(y) = has y a M_C-neighbor within rho? (CDCL blindness)
  cw_dataset: rows = (instance, y) for y in A_C(I) [CDCL-found]
              features = CDCL-derived (recurrence, conflicts_to_discovery,
                         decisions_to_discovery, foundneighbor_C, hamming_weight)
              target   = label_W(y) = has y a M_W-neighbor within rho? (WalkSAT blindness)

Both tables also carry: instance id, n, alpha, regime, S_I_size, coverage_W,
coverage_C, eps_hat_W, eps_hat_C, dist_to_other_solver_set(y) (retrospective,
legitimate diagnostic), local_S_I_density(y) (retrospective, legitimate).
"""
import json
import numpy as np


def hamming(a, b):
    return sum(x != y for x, y in zip(a, b))


def main():
    with open("../../phase2/data/stage_b_results_test.json") as f:
        walksat_sb = json.load(f)
    with open("../../phase3/data/cdcl_stage_b_results_test.json") as f:
        cdcl_sb = json.load(f)
    cdcl_by_id = {r["id"]: r for r in cdcl_sb}

    wc_rows = []
    cw_rows = []

    for wrec in walksat_sb:
        iid = wrec["id"]
        crec = cdcl_by_id.get(iid)
        if crec is None:
            continue

        S_I = [tuple(x) for x in crec["S_I"]]
        M_W = [tuple(x) for x in crec["M_W"]]
        M_C = [tuple(x) for x in crec["M_C"]]
        A_C_points = [tuple(p["y"]) for p in crec["per_found_solution_C"]]
        rho = crec["rho_used"]

        shared = {
            "id": iid, "n": crec["n"], "alpha": crec["alpha"], "regime": crec["regime"],
            "S_I_size": crec["S_I_size"],
            "coverage_W": crec["coverage_W"], "coverage_C": crec["coverage_C"],
            "eps_hat_W": crec["eps_hat_W"], "eps_hat_C": crec["eps_hat_C"],
            "rho": rho,
        }

        # local S_I density (retrospective diagnostic): count of S_I points
        # within radius `rho` of y, INCLUDING y itself minus 1
        S_I_sample = S_I if len(S_I) <= 300 else S_I[:300]  # cap for cost; documented

        # wc_dataset: y in A_W(I), target = CDCL blindness
        for p in wrec["per_found_solution"]:
            y = tuple(p["y"])
            miss_c = sum(1 for x in M_C if hamming(x, y) <= rho)
            label_c = int(miss_c > 0)
            dist_to_C = min((hamming(y, z) for z in A_C_points), default=None)
            local_density = sum(1 for x in S_I_sample if x != y and hamming(x, y) <= rho)
            wc_rows.append({
                **shared, "y": list(y), "hamming_weight": p["hamming_weight"],
                "basin": p["basin"], "disc_flips": p["disc_flips"], "foundneighbor_W": p["foundneighbor"],
                "dist_to_other_solver_set": dist_to_C, "local_S_I_density": local_density,
                "miss_rho_target": miss_c, "label_target": label_c,
            })

        # cw_dataset: y in A_C(I), target = WalkSAT blindness
        A_W_points = [tuple(p["y"]) for p in wrec["per_found_solution"]]
        for p in crec["per_found_solution_C"]:
            y = tuple(p["y"])
            miss_w = sum(1 for x in M_W if hamming(x, y) <= rho)
            label_w = int(miss_w > 0)
            dist_to_W = min((hamming(y, z) for z in A_W_points), default=None)
            local_density = sum(1 for x in S_I_sample if x != y and hamming(x, y) <= rho)
            cw_rows.append({
                **shared, "y": list(y), "hamming_weight": p["hamming_weight"],
                "recurrence": p["recurrence"], "conflicts_to_discovery": p["conflicts_to_discovery"],
                "decisions_to_discovery": p["decisions_to_discovery"], "foundneighbor_C": p["foundneighbor"],
                "dist_to_other_solver_set": dist_to_W, "local_S_I_density": local_density,
                "miss_rho_target": miss_w, "label_target": label_w,
            })

    with open("../data/wc_dataset.json", "w") as f:
        json.dump(wc_rows, f)
    with open("../data/cw_dataset.json", "w") as f:
        json.dump(cw_rows, f)

    print(f"wc_dataset (y in A_W, predicting CDCL blindness): {len(wc_rows)} rows, "
          f"{len(set(r['id'] for r in wc_rows))} instances")
    print(f"cw_dataset (y in A_C, predicting WalkSAT blindness): {len(cw_rows)} rows, "
          f"{len(set(r['id'] for r in cw_rows))} instances")
    print("Wrote ../data/wc_dataset.json and ../data/cw_dataset.json")


if __name__ == "__main__":
    main()
