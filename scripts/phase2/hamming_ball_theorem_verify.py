"""
Phase 2, Part 1: exhaustive + representative brute-force verification of the
exact Hamming-ball-intersection theorem, for OPEN and CLOSED balls.

Central combinatorial lemma (derived independently, see HAMMING_BALL_THEOREM.md):
  min_{z in {0,1}^n} max(d(x,z), d(y,z)) = ceil(D/2),  where D = d(x,y).

Consequences to verify:
  OPEN balls:   B_eps(x) ∩ B_eps(y) = ∅  <=>  eps <= ceil(D/2)
  CLOSED balls: Bbar_eps(x) ∩ Bbar_eps(y) = ∅  <=>  eps <  ceil(D/2)

Also verifies the hypercube distance-transitivity assumption used to justify
testing one representative pair per (n, D) instead of literally every pair:
for FIXED n and D, the ball-intersection outcome at every tested eps is
checked to be IDENTICAL across many different pairs at that same D (not
merely asserted).

Exhaustiveness:
  n = 1..6: EVERY pair x,y (all C(2^n,2) pairs) checked exactly.
  n = 7..10: for each achievable D=1..n, a representative pair plus several
             additional randomly chosen pairs at the same D are checked
             (transitivity spot-check), rather than literally all pairs
             (infeasible: e.g. n=10 has ~524,000 pairs; distances only span
             1..n so the representative-plus-spot-check design already gives
             far more coverage than needed to catch any transitivity failure).

Epsilon grid per (n,D): integers 0..n, half-integers k+0.5 for k=0..n, AND
values immediately above/below every critical threshold (ceil(D/2)-0.01,
ceil(D/2), ceil(D/2)+0.01, D/2-0.01, D/2, D/2+0.01) to nail down strict vs
non-strict behavior exactly.
"""
import itertools
import math
import random

random.seed(20260928)

def hamming(a, b):
    return sum(x != y for x, y in zip(a, b))

def ball_intersect_empty(x, y, eps, n, closed):
    for z in itertools.product([0, 1], repeat=n):
        dz_x = hamming(x, z)
        dz_y = hamming(y, z)
        if closed:
            in_x = dz_x <= eps
            in_y = dz_y <= eps
        else:
            in_x = dz_x < eps
            in_y = dz_y < eps
        if in_x and in_y:
            return False
    return True

def eps_grid(n, D):
    vals = set()
    for k in range(0, 2 * n + 1):
        vals.add(k / 2)  # integers and half-integers 0, 0.5, 1, 1.5, ..., n
    c = math.ceil(D / 2)
    for base in [c, D / 2]:
        for delta in [-0.01, 0.0, 0.01]:
            v = base + delta
            if v > 0:
                vals.add(v)
    return sorted(vals)

def predict_open(D, eps):
    return eps <= math.ceil(D / 2)   # predicted: balls disjoint

def predict_closed(D, eps):
    return eps < math.ceil(D / 2)    # predicted: balls disjoint

def check_pair(x, y, n, results, D=None):
    D_actual = hamming(x, y)
    if D is not None:
        assert D_actual == D
    for eps in eps_grid(n, D_actual):
        actual_open = ball_intersect_empty(x, y, eps, n, closed=False)
        actual_closed = ball_intersect_empty(x, y, eps, n, closed=True)
        pred_open = predict_open(D_actual, eps)
        pred_closed = predict_closed(D_actual, eps)
        results['open_total'] += 1
        results['closed_total'] += 1
        if actual_open == pred_open:
            results['open_match'] += 1
        else:
            results['open_mismatches'].append((n, D_actual, eps, actual_open, pred_open))
        if actual_closed == pred_closed:
            results['closed_match'] += 1
        else:
            results['closed_mismatches'].append((n, D_actual, eps, actual_closed, pred_closed))
    return D_actual

def main():
    results = {
        'open_total': 0, 'open_match': 0, 'open_mismatches': [],
        'closed_total': 0, 'closed_match': 0, 'closed_mismatches': [],
    }
    transitivity_failures = []

    # n = 1..6: exhaustive over ALL pairs
    for n in range(1, 7):
        points = list(itertools.product([0, 1], repeat=n))
        by_D_outcomes = {}  # D -> list of (open_pattern, closed_pattern) per pair, for transitivity check
        for x, y in itertools.combinations(points, 2):
            D = hamming(x, y)
            # record a signature (tuple of open/closed outcomes across the eps grid) per pair
            sig_open = []
            sig_closed = []
            for eps in eps_grid(n, D):
                sig_open.append(ball_intersect_empty(x, y, eps, n, closed=False))
                sig_closed.append(ball_intersect_empty(x, y, eps, n, closed=True))
            by_D_outcomes.setdefault(D, []).append((tuple(sig_open), tuple(sig_closed)))
            check_pair(x, y, n, results, D=D)
        # transitivity check: all pairs at the same D should give the same signature
        for D, sigs in by_D_outcomes.items():
            first = sigs[0]
            for s in sigs[1:]:
                if s != first:
                    transitivity_failures.append((n, D, 'exhaustive-mismatch'))
                    break
        print(f"n={n} (exhaustive, {len(points)*(len(points)-1)//2} pairs): "
              f"open running match={results['open_match']}/{results['open_total']}, "
              f"closed running match={results['closed_match']}/{results['closed_total']}")

    # n = 7..10: representative pair per D + random spot-checks, with transitivity check
    for n in range(7, 11):
        for D in range(1, n + 1):
            x = tuple([0] * n)
            y = tuple([1] * D + [0] * (n - D))
            sigs = []
            sig_open = []
            sig_closed = []
            for eps in eps_grid(n, D):
                sig_open.append(ball_intersect_empty(x, y, eps, n, closed=False))
                sig_closed.append(ball_intersect_empty(x, y, eps, n, closed=True))
            sigs.append((tuple(sig_open), tuple(sig_closed)))
            check_pair(x, y, n, results, D=D)

            # 5 additional random pairs at the same D
            for _ in range(5):
                x2 = tuple(random.randint(0, 1) for _ in range(n))
                diff_positions = random.sample(range(n), D)
                y2 = list(x2)
                for p in diff_positions:
                    y2[p] = 1 - y2[p]
                y2 = tuple(y2)
                assert hamming(x2, y2) == D
                sig_open2 = []
                sig_closed2 = []
                for eps in eps_grid(n, D):
                    sig_open2.append(ball_intersect_empty(x2, y2, eps, n, closed=False))
                    sig_closed2.append(ball_intersect_empty(x2, y2, eps, n, closed=True))
                sigs.append((tuple(sig_open2), tuple(sig_closed2)))
                check_pair(x2, y2, n, results, D=D)

            first = sigs[0]
            for s in sigs[1:]:
                if s != first:
                    transitivity_failures.append((n, D, 'spotcheck-mismatch'))
                    break
        print(f"n={n} (representative+spotcheck, D=1..{n}, 6 pairs/D): "
              f"open running match={results['open_match']}/{results['open_total']}, "
              f"closed running match={results['closed_match']}/{results['closed_total']}")

    print("\n=== FINAL RESULTS ===")
    print(f"OPEN balls:   {results['open_match']}/{results['open_total']} match "
          f"({100*results['open_match']/results['open_total']:.4f}%)")
    print(f"CLOSED balls: {results['closed_match']}/{results['closed_total']} match "
          f"({100*results['closed_match']/results['closed_total']:.4f}%)")
    print(f"Transitivity failures (same n,D, different pair -> different outcome): "
          f"{len(transitivity_failures)}")
    if transitivity_failures:
        print("  ", transitivity_failures[:10])

    print(f"\nOpen-ball mismatches (formula: disjoint iff eps<=ceil(D/2)): "
          f"{len(results['open_mismatches'])}")
    for m in results['open_mismatches'][:15]:
        print("  ", m)
    print(f"\nClosed-ball mismatches (formula: disjoint iff eps<ceil(D/2)): "
          f"{len(results['closed_mismatches'])}")
    for m in results['closed_mismatches'][:15]:
        print("  ", m)

    # Explicit boundary demonstrations for the write-up
    print("\n=== EXPLICIT BOUNDARY EXAMPLES FOR WRITE-UP ===")
    def demo(n, x, y, eps, closed):
        D = hamming(x, y)
        empty = ball_intersect_empty(x, y, eps, n, closed)
        kind = "CLOSED" if closed else "OPEN"
        print(f"n={n} x={x} y={y} D={D} eps={eps} [{kind}]  "
              f"balls disjoint(empty)={empty}  ceil(D/2)={math.ceil(D/2)}")

    demo(2, (0,0), (1,1), 1.0, closed=False)     # D=2 even, eps=D/2=ceil(D/2)=1 boundary, open
    demo(2, (0,0), (1,1), 1.0, closed=True)      # same point, closed
    demo(3, (0,0,0), (1,0,0), 1.0, closed=False) # D=1 odd, eps=1=ceil(1/2), open -> should be disjoint(True)
    demo(3, (0,0,0), (1,0,0), 0.5, closed=False) # D=1 odd, eps=D/2=0.5 (paper's own claimed threshold)
    demo(4, (0,0,0,0), (1,1,1,0), 1.0, closed=False)  # D=3 odd, ceil(3/2)=2; eps=1<2 -> disjoint
    demo(4, (0,0,0,0), (1,1,1,0), 2.0, closed=False)  # D=3 odd, eps=2=ceil(D/2) -> disjoint (open)
    demo(4, (0,0,0,0), (1,1,1,0), 2.0, closed=True)   # same, closed -> should intersect (eps=ceil(D/2), closed)
    demo(4, (0,0,0,0), (1,1,1,0), 2.01, closed=False) # eps>ceil(D/2) -> intersect

if __name__ == "__main__":
    main()
