"""Certified radius measurement for the pilot, at arbitrary n.

Uses the method fixed by PROTOCOL.md §7: the baseline sequential-counter
encoding with the DRUP proof taken from the same solve, checked by the pinned
drat-trim under its strict verdict rule, plus the improved query policy.

Certificate standard, unchanged:
  * a lower bound needs a SAT model re-checked on the ORIGINAL variables by
    direct Hamming distance (`verify.py` imports no SAT library, no encoder);
  * an upper bound needs a DRUP proof accepted by drat-trim;
  * UNKNOWN tightens nothing; an unchecked UNSAT is solver-reported only;
  * auxiliary variables never contribute to a distance.
"""
import os, sys, json, time, threading, resource

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pilotlib as P                       # sets sys.path to the sibling + repo
import store, dratcheck
from encode import encode_Q
from verify import check_witness, hamming
from eqlib import select_radius, decisive_radii, classify
from pysat.solvers import Glucose3

PER_INVOCATION = 60.0
CHECKER_CAP = 300.0
ENCODING = 'seqcounter'


def _cnf_text(cnf, nvars):
    lines = [f'p cnf {nvars} {len(cnf)}']
    lines += [' '.join(str(l) for l in c) + ' 0' for c in cnf]
    return '\n'.join(lines) + '\n'


def query(clauses, n, B, r, art_dir, tag, remaining):
    """One certified radius query.  Never raises."""
    q = dict(r=r, n=n, encoding=ENCODING, status=None, encode_s=0.0,
             solve_s=0.0, check_s=0.0, witness_verified=None, min_dist=None,
             proof_lines=0, proof_bytes=0, proof_verdict=None,
             cnf_sha256=None, proof_sha256=None, witness_sha256=None,
             total_clauses=0, total_vars=n, bytes_written=0)
    t0 = time.perf_counter()
    cnf, nvars, naux, kind = encode_Q(clauses, n, B, r, ENCODING)
    q['encode_s'] = time.perf_counter() - t0
    if kind == 'trivial_unsat':
        q.update(status='TRIVIAL_UNSAT', proof_verdict='arithmetic (r >= n)')
        return q
    q.update(total_clauses=len(cnf), total_vars=nvars)
    os.makedirs(art_dir, exist_ok=True)
    cp, ch, nb = store.store_artifact(art_dir, f'{tag}_r{r}.cnf',
                                      _cnf_text(cnf, nvars))
    q['cnf_sha256'] = ch
    q['bytes_written'] += nb

    s = Glucose3(bootstrap_with=cnf, with_proof=True)
    budget = min(PER_INVOCATION, max(0.0, remaining()))
    timer, t1 = None, time.perf_counter()
    try:
        if budget > 0:
            timer = threading.Timer(budget, lambda: s.interrupt())
            timer.start()
            res = s.solve_limited(expect_interrupt=True)
        else:
            res = None
    finally:
        if timer:
            timer.cancel()
    q['solve_s'] = time.perf_counter() - t1

    if res is None:
        s.delete()
        q.update(status='UNKNOWN',
                 proof_verdict=f'solver interrupted after {budget:.0f}s')
        return q
    if res:
        model = s.get_model()
        s.delete()
        pos = {l for l in model if l > 0}
        x = tuple(1 if (i + 1) in pos else 0 for i in range(n))
        wp, wh, nb2 = store.store_artifact(art_dir, f'{tag}_r{r}.witness',
                                           json.dumps(list(x)) + '\n')
        q['witness_sha256'] = wh
        q['bytes_written'] += nb2
        ok, msg = check_witness(clauses, n, B, r, x)
        q.update(status='SAT', witness_verified=ok, witness_msg=msg,
                 min_dist=min(hamming(x, b) for b in B))
        return q

    proof = s.get_proof() or []
    s.delete()
    q['proof_lines'] = len(proof)
    if not proof:
        q.update(status='UNSAT', proof_verdict='UNSAT but no proof emitted')
        return q
    pp, ph, nb3 = store.store_artifact(art_dir, f'{tag}_r{r}.drup',
                                       '\n'.join(proof) + '\n')
    q.update(proof_sha256=ph, proof_bytes=nb3)
    q['bytes_written'] += nb3
    cap = min(CHECKER_CAP, max(1.0, remaining()))
    cr = dratcheck.check(os.path.join(art_dir, f'{tag}_r{r}.cnf'),
                         os.path.join(art_dir, f'{tag}_r{r}.drup'), timeout_s=cap)
    q['check_s'] = cr['wall_s']
    q.update(status='UNSAT', proof_verdict=cr['verdict'],
             checker_detail=cr['detail'], checker_exit=cr['exit_code'])
    return q


class SetState:
    """Certified interval for one observed set, advanced in time slices."""

    def __init__(self, key, clauses, n, B, art_dir, journal, meta):
        self.key, self.clauses, self.n, self.B = key, clauses, n, B
        self.art_dir, self.journal, self.meta = art_dir, journal, meta
        self.lo, self.hi = 0, n
        self.exhausted = set()
        self.queries = 0
        self.n_sat = self.n_cert = self.n_unchecked = self.n_unknown = 0
        self.encode_s = self.solve_s = self.check_s = 0.0
        self.bytes_written = 0
        self.alarm = None
        self.max_proof_lines = 0

    @property
    def exact(self):
        return self.lo == self.hi

    def interval(self):
        return dict(lo=self.lo, hi=self.hi, exact=self.exact)

    def advance(self, slice_s, opponent=None, group_remaining=lambda: 1e9):
        """Spend up to `slice_s` on this set.  With an opponent interval, aim
        at the ordering (policy D) before falling back to policy P."""
        t0 = time.perf_counter()

        def remaining():
            return min(slice_s - (time.perf_counter() - t0), group_remaining())

        while True:
            if self.exact or self.alarm:
                return
            if remaining() <= 1.0:
                return
            r = None
            if opponent is not None:
                for cand in decisive_radii(self.lo, self.hi,
                                           opponent['lo'], opponent['hi']):
                    if cand not in self.exhausted:
                        r = cand
                        break
            if r is None:
                r = select_radius(self.lo, self.hi, self.exhausted)
            if r is None:
                return
            q = query(self.clauses, self.n, self.B, r, self.art_dir,
                      self.key, remaining)
            self.queries += 1
            self.encode_s += q['encode_s']
            self.solve_s += q['solve_s']
            self.check_s += q['check_s']
            self.bytes_written += q['bytes_written']
            self.max_proof_lines = max(self.max_proof_lines, q['proof_lines'])
            rec = dict(q)
            rec.update(kind='query', key=self.key, **self.meta)
            self.journal.append(rec)
            st = q['status']
            if st == 'SAT':
                if not q['witness_verified']:
                    self.alarm = f'witness rejected at r={r}: {q.get("witness_msg")}'
                    return
                self.n_sat += 1
                self.lo = max(self.lo, r + 1)
            elif st in ('UNSAT', 'TRIVIAL_UNSAT'):
                cert = (q['proof_verdict'] == 'VERIFIED'
                        or str(q['proof_verdict']).startswith('arithmetic'))
                if cert:
                    self.n_cert += 1
                    self.hi = min(self.hi, r)
                else:
                    self.n_unchecked += 1
                    self.exhausted.add(r)
            else:
                self.n_unknown += 1
                self.exhausted.add(r)
