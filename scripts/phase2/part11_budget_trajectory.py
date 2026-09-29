"""
Part 11: budget trajectory. For a handful of representative instances chosen
from Part 10's fragmentation events (one from solution_rich, one from
intermediate -- near_threshold instances have too few solutions for a
meaningful trajectory), rerun WalkSAT with INCREASING restart budgets
T1<T2<...<Tk (reusing the same underlying random stream, so A_{T_i}(I) is
monotonically increasing in T_i -- a genuine anytime trajectory, not
independent resamples) and track, at each budget:
  - |A_T(I)|, coverage
  - eps_hat(T)
  - C_{A_T}(r) at the fixed r where fragmentation was observed in Part 10
  - C_S(r) for reference (constant, ground truth)
This produces the "budget trajectory showing fragmentation resolving as
budget increases" the task requested as a candidate V2 figure.
"""
import json
import numpy as np

from sat_common import clauses_from_jsonable
from exhaustive_only import solve_all_exhaustive
from walksat_solver import walksat_single_run
from topology_utils import pairwise_hamming_matrix, cluster_count_from_dist_matrix, eps_hat_from_points

SELECTED_INSTANCES = [537, 619]  # solution_rich, intermediate -- from Part 10's top fragmentation events
BUDGETS = [5, 10, 20, 40, 80, 150, 300, 600]
MAX_FLIPS = 3000
P_NOISE = 0.5
SEED = 20260928 + 555


def run_trajectory(inst_id, instances_by_id, r_fixed):
    inst = instances_by_id[inst_id]
    n = inst["n"]
    clauses = clauses_from_jsonable(inst["clauses"])
    S_I = solve_all_exhaustive(clauses, n)
    D_S = pairwise_hamming_matrix(np.array(S_I, dtype=np.int8))
    C_S_r = cluster_count_from_dist_matrix(D_S, r_fixed)

    rng = np.random.default_rng(SEED + inst_id)
    max_budget = max(BUDGETS)
    all_runs = []
    for _ in range(max_budget):
        found, assignment, flips = walksat_single_run(clauses, n, MAX_FLIPS, P_NOISE, rng)
        all_runs.append((found, assignment, flips))

    trajectory = []
    for T in BUDGETS:
        found_so_far = sorted(set(a for (f, a, fl) in all_runs[:T] if f))
        if len(found_so_far) == 0:
            trajectory.append({"T": T, "A_T_size": 0, "coverage": 0.0,
                                "eps_hat": n, "C_A_r": None})
            continue
        A_arr = np.array(found_so_far, dtype=np.int8)
        eh = eps_hat_from_points(np.array(S_I, dtype=np.int8), A_arr)
        D_A = pairwise_hamming_matrix(A_arr) if len(A_arr) > 1 else np.zeros((1, 1), dtype=np.int64)
        c_a_r = cluster_count_from_dist_matrix(D_A, r_fixed) if len(A_arr) > 1 else 1
        trajectory.append({
            "T": T, "A_T_size": len(found_so_far),
            "coverage": len(found_so_far) / len(S_I),
            "eps_hat": eh, "C_A_r": c_a_r,
        })

    return {
        "id": inst_id, "n": n, "alpha": inst["alpha"], "regime": inst["regime"],
        "S_I_size": len(S_I), "r_fixed": r_fixed, "C_S_r_fixed": C_S_r,
        "trajectory": trajectory,
    }


def main():
    with open("../data/instances_test.json") as f:
        instances = json.load(f)
    instances_by_id = {r["id"]: r for r in instances}

    with open("../data/part10_results.json") as f:
        part10 = json.load(f)
    frag_by_id = {e["id"]: e for e in part10["fragmentation_events"]}

    results = []
    for iid in SELECTED_INSTANCES:
        r_fixed = frag_by_id[iid]["at_r"]
        traj = run_trajectory(iid, instances_by_id, r_fixed)
        results.append(traj)
        print(f"\n=== Instance {iid} (n={traj['n']}, alpha={traj['alpha']}, "
              f"regime={traj['regime']}, |S_I|={traj['S_I_size']}, r_fixed={r_fixed}, "
              f"C_S({r_fixed})={traj['C_S_r_fixed']}) ===")
        print(f"{'T':>6} {'|A_T|':>7} {'coverage':>10} {'eps_hat':>8} {'C_A(r)':>8} {'C_S(r)':>8} {'fragmented?':>12}")
        for row in traj["trajectory"]:
            frag = (row["C_A_r"] is not None and row["C_A_r"] > traj["C_S_r_fixed"])
            print(f"{row['T']:6d} {row['A_T_size']:7d} {row['coverage']:10.4f} "
                  f"{row['eps_hat']:8d} {str(row['C_A_r']):>8} {traj['C_S_r_fixed']:8d} {str(frag):>12}")

    with open("../data/part11_budget_trajectory.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nWrote ../data/part11_budget_trajectory.json")


if __name__ == "__main__":
    main()
