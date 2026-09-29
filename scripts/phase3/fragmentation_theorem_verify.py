"""
Phase 3, Part 15: verification for FRAGMENTATION_THEOREM.md.

1. Explicit example of under-representation causing C_A(r) < C_S(r) at r < eps.
2. 200-trial random check that r >= eps guarantees C_A(r) >= C_S(r) (the
   Proposition in FRAGMENTATION_THEOREM.md), with zero tolerated violations.
"""
import itertools
import random
import networkx as nx


def hamming(a, b):
    return sum(x != y for x, y in zip(a, b))


def components(points, r):
    G = nx.Graph()
    G.add_nodes_from(points)
    pts = list(points)
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if hamming(pts[i], pts[j]) <= r:
                G.add_edge(pts[i], pts[j])
    return [frozenset(c) for c in nx.connected_components(G)]


def main():
    print("=== Example: under-representation causing C_A(r) < C_S(r) ===")
    p1 = tuple([0] * 10)
    p2 = tuple([1] + [0] * 9)
    q = tuple([1] * 10)
    S = [p1, p2, q]
    A = [p1]
    eps = max(min(hamming(x, y) for y in A) for x in S)
    print("S =", S)
    print("A =", A)
    print("eps =", eps)
    for r in [1, 5, 9, 10, 11]:
        CS = len(components(S, r))
        CA = len(components(A, r))
        print(f"r={r}: C_S(r)={CS} C_A(r)={CA}  C_A<C_S? {CA<CS}  (r>=eps? {r>=eps})")

    print("\n=== Verify Proposition: r>=eps implies C_A(r)>=C_S(r), 200 random trials ===")
    random.seed(42)
    violations = 0
    n_checks = 0
    for trial in range(200):
        n = random.randint(4, 7)
        allpts = list(itertools.product([0, 1], repeat=n))
        S = random.sample(allpts, random.randint(3, min(15, len(allpts))))
        A = random.sample(S, random.randint(1, len(S)))
        eps = max(min(hamming(x, y) for y in A) for x in S)
        for r in range(eps, n + 1):
            n_checks += 1
            CS = len(components(S, r))
            CA = len(components(A, r))
            if CA < CS:
                violations += 1
                print(f"VIOLATION: n={n} r={r} eps={eps} C_S={CS} C_A={CA}")
    print(f"Total (trial,r) checks with r>=eps: {n_checks}")
    print(f"Violations of 'r>=eps => C_A(r)>=C_S(r)': {violations} (should be 0)")


if __name__ == "__main__":
    main()
