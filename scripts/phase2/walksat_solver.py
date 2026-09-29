"""
Instrumented WalkSAT-style stochastic local search solver.

Standard WalkSAT: repeat `max_flips` times: if assignment satisfies all
clauses, stop (success). Else pick a random UNSATISFIED clause; with
probability `p_noise` flip a random variable in that clause (random walk
move), else flip the variable in that clause that minimizes the number of
newly-violated clauses (greedy move, ties broken randomly).

Instrumentation (Stage-A-legitimate: uses only the CNF formula and the
solver's own search trajectory, never S_I):
  - per restart: whether it converged, to which assignment, and how many
    flips it took.
This is enough to compute the `basin(y)`, `disc_flips(y)` prospective risk
scores from ACCESSIBILITY_FRAMEWORK.md Section 4. Full per-step trajectories
are NOT retained (memory/runtime cost was judged not worth it for the
`visitdensity` feature, which is deprioritized -- documented in
EXPERIMENT_PROTOCOL.md).
"""
import numpy as np

from sat_common import eval_assignment, count_violated_clauses


def walksat_single_run(clauses, n, max_flips, p_noise, rng):
    """
    One WalkSAT restart. Returns (found: bool, assignment: tuple or None,
    flips_used: int).
    """
    assignment = rng.integers(0, 2, size=n)

    # precompute clause membership per variable for speed
    for flip_count in range(1, max_flips + 1):
        violated = []
        for ci, clause in enumerate(clauses):
            sat = False
            for (var, sign) in clause:
                val = assignment[var]
                if (val == 1) if sign == 1 else (val == 0):
                    sat = True
                    break
            if not sat:
                violated.append(clause)
        if not violated:
            return True, tuple(int(b) for b in assignment), flip_count - 1

        clause = violated[rng.integers(0, len(violated))]
        vars_in_clause = [v for (v, s) in clause]

        if rng.random() < p_noise:
            chosen_var = vars_in_clause[rng.integers(0, len(vars_in_clause))]
        else:
            best_var = None
            best_break = None
            for v in vars_in_clause:
                trial = assignment.copy()
                trial[v] = 1 - trial[v]
                nviol = count_violated_clauses(trial, clauses)
                if best_break is None or nviol < best_break:
                    best_break = nviol
                    best_var = [v]
                elif nviol == best_break:
                    best_var.append(v)
            chosen_var = best_var[rng.integers(0, len(best_var))]

        assignment[chosen_var] = 1 - assignment[chosen_var]

    # did not converge within max_flips
    sat_now = eval_assignment(assignment, clauses)
    if sat_now:
        return True, tuple(int(b) for b in assignment), max_flips
    return False, None, max_flips


def walksat_multi_restart(clauses, n, K, max_flips, p_noise, rng):
    """
    Run K independent WalkSAT restarts. Returns a list of dicts:
      {"found": bool, "assignment": tuple or None, "flips": int}
    This is the raw Stage-A trajectory log; predictor features are derived
    from this list downstream (run_stage_a.py), never from S_I.
    """
    runs = []
    for _ in range(K):
        found, assignment, flips = walksat_single_run(clauses, n, max_flips, p_noise, rng)
        runs.append({"found": found, "assignment": assignment, "flips": flips})
    return runs
