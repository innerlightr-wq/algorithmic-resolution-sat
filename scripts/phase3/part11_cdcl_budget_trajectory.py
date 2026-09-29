"""
Phase 3, Part 11: CDCL budget trajectories on the SAME two instances Phase 2
used for its WalkSAT trajectory (id 537 solution_rich, id 619 intermediate --
phase2/data/part11_budget_trajectory.json), for a direct paired comparison,
pre-specified (not cherry-picked post-hoc for this phase).

Budget knob: R fixed at 5 permuted runs; T (solutions enumerated per run)
swept over {1,2,4,8,16,32,64} -- increasing T is the direct CDCL analogue of
WalkSAT's increasing restart count (more search effort per instance).
"""
import json
import sys
import numpy as np
import random

sys.path.insert(0, "../../phase2/scripts")
from exhaustive_only import solve_all_exhaustive
from sat_common import clauses_from_jsonable as phase2_clauses_from_jsonable
from topology_utils import pairwise_hamming_matrix, cluster_count_from_dist_matrix, eps_hat_from_points

sys.path.insert(0, ".")
from pysat_common import clauses_from_phase2_jsonable, permute_clauses, random_phases, unpermute_model
from pysat.solvers import Glucose3

SELECTED_INSTANCES = [537, 619]
T_VALUES = [1, 2, 4, 8, 16, 32, 64]
R_RUNS = 5
BASE_SEED = 20260928 + 9999


def run_cdcl_union_at_budget(clauses, n, R, T, base_seed):
    found = set()
    for run_idx in range(R):
        rng = random.Random(base_seed + run_idx)
        pclauses, perm = permute_clauses(clauses, n, rng)
        phases = random_phases(n, rng)
        g = Glucose3(bootstrap_with=pclauses)
        g.set_phases(phases)
        cnt = 0
        for model in g.enum_models():
            cnt += 1
            y = unpermute_model(model, perm, n)
            found.add(y)
            if cnt >= T:
                break
        g.delete()
    return found


def main():
    with open("../../phase2/data/instances_test.json") as f:
        instances = json.load(f)
    instances_by_id = {r["id"]: r for r in instances}

    with open("../../phase2/data/part11_budget_trajectory.json") as f:
        walksat_traj = json.load(f)
    walksat_by_id = {r["id"]: r for r in walksat_traj}

    results = []
    for iid in SELECTED_INSTANCES:
        inst = instances_by_id[iid]
        n = inst["n"]
        clauses_p2 = phase2_clauses_from_jsonable(inst["clauses"])  # phase2 tuple format, for exhaustive solve
        clauses = clauses_from_phase2_jsonable(inst["clauses"])  # pysat int format, for CDCL
        S_I = solve_all_exhaustive(clauses_p2, n)
        S_arr = np.array(S_I, dtype=np.int8)
        D_S = pairwise_hamming_matrix(S_arr)

        r_fixed = walksat_by_id[iid]["r_fixed"]
        C_S_r = cluster_count_from_dist_matrix(D_S, r_fixed)

        traj = []
        for T in T_VALUES:
            found = run_cdcl_union_at_budget(clauses, n, R_RUNS, T, BASE_SEED + iid)
            if not found:
                traj.append({"T": T, "A_size": 0, "coverage": 0.0, "eps_hat": n, "C_A_r": None})
                continue
            A_arr = np.array(sorted(found), dtype=np.int8)
            eh = eps_hat_from_points(S_arr, A_arr)
            D_A = pairwise_hamming_matrix(A_arr) if len(A_arr) > 1 else np.zeros((1, 1), dtype=np.int64)
            c_a_r = cluster_count_from_dist_matrix(D_A, r_fixed) if len(A_arr) > 1 else 1
            traj.append({"T": T, "A_size": len(found), "coverage": len(found) / len(S_I),
                         "eps_hat": eh, "C_A_r": c_a_r})

        results.append({
            "id": iid, "n": n, "alpha": inst["alpha"], "regime": inst["regime"],
            "S_I_size": len(S_I), "r_fixed": r_fixed, "C_S_r_fixed": C_S_r,
            "trajectory": traj,
        })

        print(f"\n=== Instance {iid} (n={n}, alpha={inst['alpha']}, regime={inst['regime']}, "
              f"|S_I|={len(S_I)}, r_fixed={r_fixed}, C_S({r_fixed})={C_S_r}) [CDCL, R={R_RUNS}] ===")
        print(f"{'T(sols/run)':>12} {'|A_T|':>7} {'coverage':>10} {'eps_hat':>8} {'C_A(r)':>8} {'C_S(r)':>8}")
        for row in traj:
            print(f"{row['T']:12d} {row['A_size']:7d} {row['coverage']:10.4f} {row['eps_hat']:8} "
                  f"{str(row['C_A_r']):>8} {C_S_r:8d}")

        print(f"\n  --- WalkSAT trajectory on same instance (from Phase 2, for comparison) ---")
        print(f"  {'T(restarts)':>12} {'|A_T|':>7} {'coverage':>10} {'eps_hat':>8} {'C_A(r)':>8}")
        for row in walksat_by_id[iid]["trajectory"]:
            print(f"  {row['T']:12d} {row['A_T_size']:7d} {row['coverage']:10.4f} {row['eps_hat']:8} {str(row['C_A_r']):>8}")

    with open("../data/part11_cdcl_budget_trajectory.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nWrote ../data/part11_cdcl_budget_trajectory.json")


if __name__ == "__main__":
    main()
