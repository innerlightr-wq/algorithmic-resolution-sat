"""
Phase 3, Part 14: verified extremal (sharpness) construction for the +2eps
constant in the asymmetric H0 correspondence theorem (Phase 2
PERSISTENCE_STABILITY.md Section 3 / Phase 3 FRAGMENTATION_THEOREM.md).

Construction, realized directly in the Hamming cube {0,1}^n, n=r+2*eps:
  p = 0^n
  q = first r coords set to 1 (rest 0)           [d(p,q) = r]
  a = p with an additional, DISJOINT block of eps coords flipped
  b = q with an additional, DISJOINT block of eps coords flipped (disjoint
      from q's own support AND from a's flip-block)
  S = {p,q,a,b},  A = {a,b}

Verifies: d(p,a)=d(q,b)=eps=eps_hat(A,S); a is p's UNIQUE nearest point in A
(and symmetrically for b,q); p,q are directly r-connected in S (single edge,
distance r); but a,b (their nearest-A images) are NOT connected in A at any
radius less than EXACTLY r+2*eps -- i.e. the guaranteed recovery radius
"r+2*eps" from the theorem is achieved with equality, not slack, on this
family. Hence the constant 2 cannot be replaced by any smaller universal
constant, in ARBITRARY metric spaces or specifically in the Hamming cube.
"""


def hamming(a, b):
    return sum(x != y for x, y in zip(a, b))


def build_extremal(r, eps):
    n = r + 2 * eps
    p = [0] * n
    q = [0] * n
    for i in range(r):
        q[i] = 1
    a = p.copy()
    for i in range(r, r + eps):
        a[i] = 1
    b = q.copy()
    for i in range(r + eps, r + 2 * eps):
        b[i] = 1
    return tuple(p), tuple(q), tuple(a), tuple(b), n


def verify(r, eps):
    p, q, a, b, n = build_extremal(r, eps)
    S = [p, q, a, b]
    A = [a, b]
    d_pa, d_qb = hamming(p, a), hamming(q, b)
    d_pq, d_ab = hamming(p, q), hamming(a, b)
    d_pb, d_qa = hamming(p, b), hamming(q, a)
    eps_hat = max(min(hamming(x, y) for y in A) for x in S)

    assert d_pa == eps and d_qb == eps
    assert d_pa < d_pb, "a must be strictly nearer to p than b"
    assert d_qb < d_qa, "b must be strictly nearer to q than a"
    assert d_ab == r + 2 * eps, f"sharpness mismatch: d(a,b)={d_ab}, expected {r+2*eps}"
    assert eps_hat == eps
    assert d_pq <= r  # p,q directly r-connected in S

    return {
        "r": r, "eps": eps, "n": n, "d_pq": d_pq, "d_pa": d_pa, "d_qb": d_qb,
        "d_ab": d_ab, "expected_r_plus_2eps": r + 2 * eps, "eps_hat": eps_hat,
        "sharp": d_ab == r + 2 * eps,
    }


if __name__ == "__main__":
    results = []
    for r, eps in [(1, 1), (2, 1), (3, 2), (4, 4), (5, 3), (10, 5), (1, 10)]:
        res = verify(r, eps)
        results.append(res)
        print(f"r={r:2d} eps={eps:2d} n={res['n']:3d}: d(p,q)={res['d_pq']} "
              f"d(a,b)={res['d_ab']} (=r+2eps={res['expected_r_plus_2eps']}) "
              f"eps_hat={res['eps_hat']}  SHARP={res['sharp']}")
    print(f"\nAll {len(results)} parameter combinations confirm exact equality "
          f"(no slack) -- the constant 2 is sharp, realized directly in the "
          f"Hamming cube for every tested (r,eps).")
