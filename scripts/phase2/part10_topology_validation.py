"""
Part 10: empirical validation of the H0 stability theorem (PERSISTENCE_STABILITY.md
Section 3) on REAL SAT solution spaces (test split, 360 instances), plus
coverage vs eps_hat vs topological-distortion relationships.

For each test instance with A(I) != empty:
  - recompute S_I (exhaustive_only, Stage-B-only module -- this script is a
    Stage-B/post-hoc analysis script, never used for prediction)
  - compute eps_hat, C_S(r), C_A(r) for all r = 0..n
  - verify: C_A(r + 2*eps_hat) <= C_S(r) for ALL r (the PROVED theorem)
  - verify: no false merge (every A-r-cluster is contained in a single S-r-cluster)
  - measure fragmentation: does C_A(r) > C_S(r) for some r (same radius)?
    if so, by how much, and at what r relative to eps_hat?
"""
import json
import time
import numpy as np

from sat_common import clauses_from_jsonable
from exhaustive_only import solve_all_exhaustive
from topology_utils import pairwise_hamming_matrix, cluster_count_from_dist_matrix

def main():
    with open("../data/instances_test.json") as f:
        instances = json.load(f)
    instances_by_id = {r["id"]: r for r in instances}

    with open("../data/stage_a_predictions_test.json") as f:
        stage_a = json.load(f)

    theorem_violations = []
    false_merge_violations = []
    fragmentation_events = []
    per_instance_summary = []

    t0 = time.time()
    n_processed = 0
    for rec in stage_a:
        iid = rec["id"]
        A_I = [tuple(y) for y in rec["A_I"]]
        if len(A_I) == 0:
            continue
        inst = instances_by_id[iid]
        n = inst["n"]
        clauses = clauses_from_jsonable(inst["clauses"])
        S_I = solve_all_exhaustive(clauses, n)
        if len(S_I) < 2:
            continue

        S_arr = np.array(S_I, dtype=np.int8)
        A_arr = np.array(A_I, dtype=np.int8)

        D_S = pairwise_hamming_matrix(S_arr)
        D_A = pairwise_hamming_matrix(A_arr) if len(A_arr) > 1 else np.zeros((1, 1), dtype=np.int64)

        # eps_hat via cross distances
        G = S_arr.astype(np.float64) @ A_arr.astype(np.float64).T
        s_norm = (S_arr.astype(np.float64) ** 2).sum(axis=1)
        a_norm = (A_arr.astype(np.float64) ** 2).sum(axis=1)
        D_SA = np.rint(s_norm[:, None] + a_norm[None, :] - 2 * G).astype(np.int64)
        eps_hat = int(D_SA.min(axis=1).max())

        r_values = list(range(0, n + 1))
        C_S = {r: cluster_count_from_dist_matrix(D_S, r) for r in r_values}
        C_A = {r: cluster_count_from_dist_matrix(D_A, r) if len(A_arr) > 1 else 1 for r in r_values}

        # THEOREM CHECK: C_A(r + 2*eps_hat) <= C_S(r) for all r
        for r in r_values:
            r_shift = r + 2 * eps_hat
            if r_shift <= n:
                ca_shift = cluster_count_from_dist_matrix(D_A, r_shift) if len(A_arr) > 1 else 1
            else:
                ca_shift = 1  # beyond diameter, everything merges (or trivially <=1 component)
            if ca_shift > C_S[r]:
                theorem_violations.append({"id": iid, "r": r, "eps_hat": eps_hat,
                                            "C_A_shift": ca_shift, "C_S_r": C_S[r]})

        # NO-FALSE-MERGE CHECK: every A-r-cluster within a single S-r-cluster
        # (label S-clusters via connected components on D_S, check A points'
        # labels agree within each A-cluster)
        from scipy.sparse import csr_matrix
        from scipy.sparse.csgraph import connected_components
        for r in [0, max(1, n // 4), max(1, n // 2), n]:
            adj_S = (D_S <= r).astype(np.int8)
            np.fill_diagonal(adj_S, 0)
            _, labels_S = connected_components(csr_matrix(adj_S), directed=False)
            s_label_of = {S_I[i]: labels_S[i] for i in range(len(S_I))}

            adj_A = (D_A <= r).astype(np.int8) if len(A_arr) > 1 else np.zeros((1, 1))
            np.fill_diagonal(adj_A, 0)
            if len(A_arr) > 1:
                _, labels_A = connected_components(csr_matrix(adj_A), directed=False)
            else:
                labels_A = np.array([0])
            a_cluster_members = {}
            for i, lab in enumerate(labels_A):
                a_cluster_members.setdefault(lab, []).append(A_I[i])
            for lab, members in a_cluster_members.items():
                s_labels = {s_label_of[m] for m in members}
                if len(s_labels) != 1:
                    false_merge_violations.append({"id": iid, "r": r, "n_s_labels_spanned": len(s_labels)})

        # FRAGMENTATION: does C_A(r) > C_S(r) at the SAME r for any r?
        max_excess = 0
        frag_r = None
        for r in r_values:
            excess = C_A[r] - C_S[r]
            if excess > max_excess:
                max_excess = excess
                frag_r = r
        is_fragmented = max_excess > 0
        if is_fragmented:
            fragmentation_events.append({
                "id": iid, "n": n, "alpha": inst["alpha"], "regime": inst["regime"],
                "eps_hat": eps_hat, "max_excess_components": max_excess, "at_r": frag_r,
                "S_I_size": len(S_I), "A_I_size": len(A_I),
            })

        per_instance_summary.append({
            "id": iid, "n": n, "alpha": inst["alpha"], "regime": inst["regime"],
            "S_I_size": len(S_I), "A_I_size": len(A_I), "eps_hat": eps_hat,
            "is_fragmented": is_fragmented, "max_excess_components": max_excess,
        })

        n_processed += 1
        if n_processed % 50 == 0:
            print(f"  processed {n_processed} ({time.time()-t0:.1f}s)", flush=True)

    dt = time.time() - t0
    print(f"\nProcessed {n_processed} test instances with |A(I)|>=1, |S_I|>=2, in {dt:.1f}s")
    print(f"\n=== THEOREM CHECK: C_A(r+2*eps_hat) <= C_S(r) ===")
    print(f"Violations: {len(theorem_violations)}")
    for v in theorem_violations[:10]:
        print("  ", v)

    print(f"\n=== NO-FALSE-MERGE CHECK ===")
    print(f"Violations: {len(false_merge_violations)}")
    for v in false_merge_violations[:10]:
        print("  ", v)

    print(f"\n=== FRAGMENTATION FREQUENCY ===")
    print(f"Fragmented instances (C_A(r)>C_S(r) for some r): {len(fragmentation_events)}/{n_processed} "
          f"({100*len(fragmentation_events)/n_processed:.1f}%)")
    by_regime = {}
    for e in fragmentation_events:
        by_regime.setdefault(e["regime"], 0)
        by_regime[e["regime"]] += 1
    total_by_regime = {}
    for s in per_instance_summary:
        total_by_regime.setdefault(s["regime"], 0)
        total_by_regime[s["regime"]] += 1
    for regime, count in by_regime.items():
        print(f"  {regime}: {count}/{total_by_regime[regime]} "
              f"({100*count/total_by_regime[regime]:.1f}%)")

    eps_hats_frag = [e["eps_hat"] for e in fragmentation_events]
    eps_hats_all = [s["eps_hat"] for s in per_instance_summary]
    print(f"\nMean eps_hat (fragmented instances): "
          f"{np.mean(eps_hats_frag) if eps_hats_frag else None}")
    print(f"Mean eps_hat (all instances): {np.mean(eps_hats_all):.3f}")

    with open("../data/part10_results.json", "w") as f:
        json.dump({
            "theorem_violations": theorem_violations,
            "false_merge_violations": false_merge_violations,
            "fragmentation_events": fragmentation_events,
            "per_instance_summary": per_instance_summary,
            "n_processed": n_processed,
        }, f, indent=2)
    print("\nWrote ../data/part10_results.json")


if __name__ == "__main__":
    main()
