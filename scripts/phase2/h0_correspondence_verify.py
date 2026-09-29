"""
Phase 2, Part 3: brute-force verification of the elementary H_0-specific
correspondence claims (derived in PERSISTENCE_STABILITY.md), for RANDOM
subsets of the Hamming cube (this is a pure metric-space fact, not specific
to SAT solution structure, so synthetic random point sets are a legitimate
and simpler test bed than full SAT instances).

Claims to verify, for S subset of {0,1}^n, A subset of S (nonempty), and
eps_hat = max_{x in S} min_{y in A} d(x,y):

(1) NO FALSE MERGE (exact, no slack): for all r >= 0, every A-r-cluster is
    contained in a single S-r-cluster. Equivalently: if x,y in A are
    r-connected within A (chain of steps <= r using only points of A), then
    x,y are r-connected within S (trivially true: same chain works, since
    A subset S). This direction needs NO epsilon slack.

(2) GUARANTEED RE-MERGE (with 2*eps_hat slack): for all r >= 0, the
    nearest-neighbor map phi: S -> A (phi(x) = argmin_{y in A} d(x,y), ties
    broken arbitrarily) sends every S-r-cluster into a SINGLE
    A-(r+2*eps_hat)-cluster. Equivalently: if x,y in S are r-connected
    within S, then phi(x), phi(y) are (r+2*eps_hat)-connected within A.
    Consequence: C_A(r + 2*eps_hat) <= C_S(r) for all r.
"""
import itertools
import random
import networkx as nx

random.seed(20260928)

def hamming(a, b):
    return sum(x != y for x, y in zip(a, b))

def cluster_partition(points, r):
    """Return list of frozensets: connected components of the r-threshold graph."""
    G = nx.Graph()
    G.add_nodes_from(points)
    pts = list(points)
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if hamming(pts[i], pts[j]) <= r:
                G.add_edge(pts[i], pts[j])
    return [frozenset(c) for c in nx.connected_components(G)]

def cluster_count(points, r):
    return len(cluster_partition(points, r))

def nearest(x, A):
    return min(A, key=lambda y: hamming(x, y))

def eps_hat(S, A):
    return max(min(hamming(x, y) for y in A) for x in S)

def check_instance(n, S, A, r_values, log):
    A = list(A)
    S = list(S)
    eh = eps_hat(S, A)

    # Claim (1): no false merge -- A-r-partition refines S-r-partition (restricted to A)
    for r in r_values:
        part_A = cluster_partition(A, r)
        part_S = cluster_partition(S, r)
        # map each point of A to its S-r-cluster id
        s_cluster_of = {}
        for idx, comp in enumerate(part_S):
            for p in comp:
                s_cluster_of[p] = idx
        for comp_A in part_A:
            s_ids = {s_cluster_of[p] for p in comp_A}
            if len(s_ids) != 1:
                log['claim1_failures'].append((n, r, "A-cluster spans multiple S-clusters", comp_A))

    # Claim (2): re-merge with 2*eps_hat slack
    for r in r_values:
        part_S = cluster_partition(S, r)
        r2 = r + 2 * eh
        part_A_r2 = cluster_partition(A, r2)
        a_cluster_of = {}
        for idx, comp in enumerate(part_A_r2):
            for p in comp:
                a_cluster_of[p] = idx
        for comp_S in part_S:
            images = set()
            for x in comp_S:
                y = nearest(x, A)
                images.add(a_cluster_of[y])
            if len(images) != 1:
                log['claim2_failures'].append((n, r, eh, "S-cluster's phi-images span multiple A-(r+2eh)-clusters", comp_S))
        # consequence check: C_A(r+2eh) <= C_S(r)
        if len(part_A_r2) > len(part_S):
            log['consequence_failures'].append((n, r, eh, len(part_A_r2), len(part_S)))

    return eh

def random_subset(n, size):
    all_pts = list(itertools.product([0, 1], repeat=n))
    return random.sample(all_pts, min(size, len(all_pts)))

def main():
    log = {'claim1_failures': [], 'claim2_failures': [], 'consequence_failures': []}
    total_instances = 0
    for n in [4, 5, 6, 7, 8]:
        for trial in range(20):
            S_size = random.randint(4, min(40, 2**n))
            S = random_subset(n, S_size)
            A_size = random.randint(1, len(S))
            A = random.sample(S, A_size)
            if len(A) == 0:
                continue
            r_values = list(range(0, n + 1))
            eh = check_instance(n, S, A, r_values, log)
            total_instances += 1

    print(f"Total (n, random S, random A) instances checked: {total_instances}")
    print(f"Claim 1 (no false merge, exact) failures: {len(log['claim1_failures'])}")
    for f in log['claim1_failures'][:10]:
        print("  ", f)
    print(f"Claim 2 (guaranteed re-merge at r+2*eps_hat) failures: {len(log['claim2_failures'])}")
    for f in log['claim2_failures'][:10]:
        print("  ", f)
    print(f"Consequence (C_A(r+2eh) <= C_S(r)) failures: {len(log['consequence_failures'])}")
    for f in log['consequence_failures'][:10]:
        print("  ", f)

    # Also explicitly check: is C_A(r+2eh) <= C_S(r) actually TIGHT sometimes
    # (i.e. does the bound get achieved with equality, not just hold with slack)?
    # Demonstrate one constructed tight-ish example.
    print("\n--- Tightness check on a hand example ---")
    n = 4
    S = [(0,0,0,0), (1,1,0,0), (1,1,1,1)]  # 3 points, spread out
    A = [(0,0,0,0), (1,1,1,1)]  # miss the middle point
    eh = eps_hat(S, A)
    print(f"S={S}")
    print(f"A={A}, eps_hat={eh}")
    for r in range(0, 5):
        cs = cluster_count(S, r)
        ca = cluster_count(A, r)
        ca_shift = cluster_count(A, r + 2*eh)
        print(f"  r={r}: C_S(r)={cs}  C_A(r)={ca}  C_A(r+2eh={r+2*eh})={ca_shift}  "
              f"(claim: C_A(r+2eh) <= C_S(r) -> {ca_shift <= cs})")

if __name__ == "__main__":
    main()
