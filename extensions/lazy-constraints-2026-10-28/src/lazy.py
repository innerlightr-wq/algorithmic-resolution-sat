"""STAGE 2 -- do fewer distance constraints suffice to certify the same answer?

Methods, both re-run here on this machine, interleaved per unit:

  S (static)  Q_r^A encoded from scratch with a distance constraint for EVERY
              observed solution -- the baseline, as methods.static_query.
  L (lazy)    abstraction refinement: encode Q_r^S for a subset S of A, solve,
              check the candidate against the WHOLE of A, and on failure add
              the nearest violated a in A and re-solve.

EXACTNESS (stated in PROTOCOL.md before measuring, repeated here).
  sat(Q_r^A) subset-of sat(Q_r^S) for S subset-of A, because Q_r^S is a
  conjunction over a sub-family.  Hence:
    * Q_r^S UNSAT  ==>  Q_r^A UNSAT, so a CHECKED UNSAT proof for the subset
      certifies the full query's upper bound.  The proof is checked against the
      subset CNF that produced it, which is what drat-trim is given.
    * a candidate x with F(x) and min_{a in A} d_H(x,a) >= r+1 is a valid
      witness for Q_r^A whatever S produced it.  Verification is ALWAYS against
      the full A, via the stage's own check_witness.
  Refinement adds the argmin a, which x violates, so no candidate recurs.

Both methods use the same radius policy (methods.select_radius), the same
encoder, the same solver, the same checker and the same budget.
"""
import os, sys, json, time, threading, hashlib

OPT = os.path.expanduser('~/scratch/sat-resolution-oracle-audit-2026-10-26/'
                         'optimization-2026-10-27')
sys.path.insert(0, os.path.join(OPT, 'src'))
import units                                      # sets up sys.path for the rest
import store, dratcheck
from encode import encode_Q
from verify import check_witness, hamming
from methods import select_radius, _cnf_text, _solve_with_limit, N
from pysat.solvers import Glucose3

PER_INVOCATION = 60.0
MEASUREMENT_BUDGET = 120.0            # PROTOCOL.md: reduced from 240 s
CHECKER_CAP = 120.0
ENCODING = 'seqcounter'
S0 = 4                                # PROTOCOL.md: initial subset size
REFINE_CAP = 60                       # PROTOCOL.md: refinement cap per query
ART = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'artifacts')


def greedy_farthest(A, k):
    """k observed solutions, greedily pairwise far apart.  Deterministic."""
    idx = [0]
    while len(idx) < min(k, len(A)):
        best, bd = None, -1
        for j in range(len(A)):
            if j in idx:
                continue
            d = min(hamming(A[j], A[i]) for i in idx)
            if d > bd:
                best, bd = j, d
        idx.append(best)
    return list(idx)


def _solve_and_certify(cnf, nvars, A_full, clauses, r, tag, remaining):
    """Solve one CNF; on SAT return the model, on UNSAT certify the proof."""
    out = dict(status=None, solve_s=0.0, check_s=0.0, proof_lines=0,
               proof_verdict=None, model=None, total_clauses=len(cnf),
               total_vars=nvars)
    s = Glucose3(bootstrap_with=cnf, with_proof=True)
    budget = min(PER_INVOCATION, max(0.0, remaining()))
    res, secs = _solve_with_limit(s, budget)
    out['solve_s'] = secs
    if res is None:
        s.delete()
        out.update(status='UNKNOWN',
                   proof_verdict=f'solver interrupted after {budget:.0f}s')
        return out
    if res:
        out['model'] = s.get_model()
        s.delete()
        out['status'] = 'SAT'
        return out
    proof = s.get_proof() or []
    s.delete()
    out['proof_lines'] = len(proof)
    if not proof:
        out.update(status='UNSAT', proof_verdict='UNSAT without a proof')
        return out
    os.makedirs(ART, exist_ok=True)
    cp, _, _ = store.store_artifact(ART, f'{tag}.cnf', _cnf_text(cnf, nvars))
    pp, _, _ = store.store_artifact(ART, f'{tag}.drup', '\n'.join(proof) + '\n')
    cap = min(CHECKER_CAP, max(1.0, remaining()))
    t0 = time.perf_counter()
    cr = dratcheck.check(cp, pp, timeout_s=cap)
    out['check_s'] = time.perf_counter() - t0
    out.update(status='UNSAT', proof_verdict=cr['verdict'])
    return out


def query_static(clauses, A, r, tag, remaining):
    t0 = time.perf_counter()
    cnf, nvars, naux, kind = encode_Q(clauses, N, A, r, ENCODING)
    enc = time.perf_counter() - t0
    if kind == 'trivial_unsat':
        return dict(status='TRIVIAL_UNSAT', proof_verdict='arithmetic (r >= n)',
                    encode_s=enc, solve_s=0.0, check_s=0.0, iters=0,
                    constraints_used=len(A), min_dist=None, total_clauses=0)
    q = _solve_and_certify(cnf, nvars, A, clauses, r, tag, remaining)
    q['encode_s'] = enc
    q['iters'] = 1
    q['constraints_used'] = len(A)
    q['min_dist'] = None
    if q['status'] == 'SAT':
        pos = {l for l in q.pop('model') if l > 0}
        x = tuple(1 if (i + 1) in pos else 0 for i in range(N))
        ok, msg = check_witness(clauses, N, A, r, x)
        q.update(witness_verified=ok, witness_msg=msg,
                 min_dist=min(hamming(x, a) for a in A))
    q.pop('model', None)
    return q


def query_lazy(clauses, A, r, tag, remaining):
    """Abstraction refinement over the distance constraints."""
    sub = greedy_farthest(A, S0)
    enc = 0.0
    agg = dict(solve_s=0.0, check_s=0.0, proof_lines=0, total_clauses=0)
    for it in range(1, REFINE_CAP + 1):
        Asub = [A[i] for i in sub]
        t0 = time.perf_counter()
        cnf, nvars, naux, kind = encode_Q(clauses, N, Asub, r, ENCODING)
        enc += time.perf_counter() - t0
        if kind == 'trivial_unsat':
            return dict(status='TRIVIAL_UNSAT',
                        proof_verdict='arithmetic (r >= n)', encode_s=enc,
                        solve_s=0.0, check_s=0.0, iters=it,
                        constraints_used=len(sub), min_dist=None,
                        total_clauses=0)
        q = _solve_and_certify(cnf, nvars, A, clauses, r,
                               f'{tag}_it{it}', remaining)
        agg['solve_s'] += q['solve_s']
        agg['check_s'] += q['check_s']
        agg['proof_lines'] = max(agg['proof_lines'], q['proof_lines'])
        agg['total_clauses'] = max(agg['total_clauses'], q['total_clauses'])
        if q['status'] == 'UNKNOWN':
            return dict(status='UNKNOWN', proof_verdict=q['proof_verdict'],
                        encode_s=enc, iters=it, constraints_used=len(sub),
                        min_dist=None, **agg)
        if q['status'] == 'UNSAT':
            # sat(Q_r^A) subset-of sat(Q_r^sub), so UNSAT here settles the full
            # query.  The proof was checked against the subset CNF.
            return dict(status='UNSAT', proof_verdict=q['proof_verdict'],
                        encode_s=enc, iters=it, constraints_used=len(sub),
                        min_dist=None, **agg)
        # SAT on the abstraction: check the candidate against the FULL A
        pos = {l for l in q['model'] if l > 0}
        x = tuple(1 if (i + 1) in pos else 0 for i in range(N))
        d = min(hamming(x, a) for a in A)
        if d >= r + 1:
            ok, msg = check_witness(clauses, N, A, r, x)
            return dict(status='SAT', witness_verified=ok, witness_msg=msg,
                        min_dist=d, proof_verdict=None, encode_s=enc, iters=it,
                        constraints_used=len(sub), **agg)
        # spurious: add the nearest violated observed solution
        j = min(range(len(A)), key=lambda i: hamming(x, A[i]))
        if j in sub:                      # cannot happen, but never loop
            return dict(status='REFINE_STUCK', proof_verdict='argmin already in S',
                        encode_s=enc, iters=it, constraints_used=len(sub),
                        min_dist=d, **agg)
        sub.append(j)
    return dict(status='REFINE_CAP', proof_verdict=f'hit {REFINE_CAP} iterations',
                encode_s=enc, iters=REFINE_CAP, constraints_used=len(sub),
                min_dist=None, **agg)


def measure(unit, clauses, A, method):
    """One measurement: the radius ladder under one method."""
    tag = unit['tag']
    lo, hi = unit['start_lo'], unit['start_hi']
    exhausted = set()
    t_start = time.perf_counter()

    def remaining():
        return MEASUREMENT_BUDGET - (time.perf_counter() - t_start)

    rec = dict(tag=tag, group=unit['group'], role=unit['role'], method=method,
               A_size=len(A), start_lo=lo, start_hi=hi,
               start_width=hi - lo, queries=0, n_sat=0, n_cert=0,
               n_unchecked=0, n_unknown=0, n_trivial=0, encode_s=0.0,
               solve_s=0.0, check_s=0.0, iters_total=0,
               constraints_max=0, constraints_min=None, min_dist_max=None,
               stop_reason=None, alarm=None,
               historical_exact=unit.get('historical_exact'))
    while True:
        if remaining() <= 1.0:
            rec['stop_reason'] = 'budget'
            break
        r = select_radius(lo, hi, exhausted)
        if r is None:
            rec['stop_reason'] = 'exhausted' if lo < hi else 'exact'
            break
        fn = query_static if method == 'S' else query_lazy
        q = fn(clauses, A, r, f'{tag}_{method}_r{r}', remaining)
        rec['queries'] += 1
        rec['encode_s'] += q['encode_s']
        rec['solve_s'] += q['solve_s']
        rec['check_s'] += q['check_s']
        rec['iters_total'] += q.get('iters', 1)
        cu = q.get('constraints_used')
        if cu is not None:
            rec['constraints_max'] = max(rec['constraints_max'], cu)
            rec['constraints_min'] = cu if rec['constraints_min'] is None \
                else min(rec['constraints_min'], cu)
        st = q['status']
        if st == 'SAT':
            if not q.get('witness_verified'):
                rec['alarm'] = f'witness rejected at r={r}: {q.get("witness_msg")}'
                rec['stop_reason'] = 'alarm'
                break
            rec['n_sat'] += 1
            lo = max(lo, r + 1)                 # baseline rule, both methods
            if q.get('min_dist') is not None:
                rec['min_dist_max'] = max(rec['min_dist_max'] or 0, q['min_dist'])
        elif st in ('UNSAT', 'TRIVIAL_UNSAT'):
            cert = (q['proof_verdict'] == 'VERIFIED'
                    or str(q['proof_verdict']).startswith('arithmetic'))
            if st == 'TRIVIAL_UNSAT':
                rec['n_trivial'] += 1
            if cert:
                rec['n_cert'] += 1
                hi = min(hi, r)
            else:
                rec['n_unchecked'] += 1
                exhausted.add(r)
        else:
            rec['n_unknown'] += 1
            exhausted.add(r)
    rec.update(final_lo=lo, final_hi=hi, final_width=hi - lo,
               exact=(lo == hi), total_s=time.perf_counter() - t_start)
    return rec


if __name__ == '__main__':
    print('=' * 100)
    print('STAGE 2 -- LAZY DISTANCE CONSTRAINTS versus the STATIC baseline')
    print('=' * 100)
    T0 = time.perf_counter()
    HARD_CAP = 75 * 60
    rows, excluded = [], []
    base = json.load(open(os.path.join(OPT, 'data', 'baseline.json')))
    for u in base:
        cl, A, meta = units.recover(u['tag'], u['obs_seed_id'])
        fh, ah = store.hash_clauses(cl), store.hash_A(A)
        if fh != u['formula_hash'] or ah != u['A_hash']:
            excluded.append((u['tag'], 'hash mismatch'))
            continue
        for method in ('S', 'L'):                       # interleaved, S first
            if time.perf_counter() - T0 > HARD_CAP:
                excluded.append((u['tag'] + '/' + method, 'total cap reached'))
                continue
            r = measure(u, cl, A, method)
            rows.append(r)
            print(f"  {r['tag']:<18} {method}  [{r['start_lo']},{r['start_hi']}]"
                  f" -> [{r['final_lo']},{r['final_hi']}]  w={r['final_width']:<3}"
                  f" exact={str(r['exact']):<5} q={r['queries']:<2}"
                  f" it={r['iters_total']:<3}"
                  f" cons={r['constraints_min']}..{r['constraints_max']}"
                  f"/{r['A_size']:<4} t={r['total_s']:6.1f}s"
                  f" (enc {r['encode_s']:.1f} solve {r['solve_s']:.1f}"
                  f" chk {r['check_s']:.1f}) {r['stop_reason']}"
                  + (f"  ALARM {r['alarm']}" if r['alarm'] else ''))
    json.dump(dict(protocol_sha=open(os.path.join(
                      os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      'data', 'PROTOCOL_SHA.txt')).read().strip(),
                   measurement_budget_s=MEASUREMENT_BUDGET,
                   per_invocation_s=PER_INVOCATION, checker_cap_s=CHECKER_CAP,
                   initial_subset=S0, refine_cap=REFINE_CAP,
                   total_s=time.perf_counter() - T0,
                   excluded=excluded, rows=rows),
              open(os.path.join(os.path.dirname(os.path.dirname(
                  os.path.abspath(__file__))), 'data', 'stage2.json'), 'w'),
              indent=1)
    print(f"\n  total {time.perf_counter()-T0:.1f}s against a {HARD_CAP}s cap; "
          f"excluded {excluded}")
