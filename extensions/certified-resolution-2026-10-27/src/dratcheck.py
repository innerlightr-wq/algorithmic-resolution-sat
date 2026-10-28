# ---------------------------------------------------------------------------
# VENDORED, UNMODIFIED, from the certified-resolution research workspace.
# Origin   : continuation src/dratcheck.py (drat-trim wrapper, strict verdict rule)
# sha256   : d8ab2ec177b3106d6f8817dba22c2052407587a15ea762756ef7fc3a6b4d7a35
# Vendored : 2026-10-27.  Only this provenance header was prepended; the code
#            below is byte-identical to the origin file.
# ---------------------------------------------------------------------------
"""Compiled-checker front end for DRUP/DRAT proofs (drat-trim).

Why the verdict is parsed and the exit code is NOT trusted
----------------------------------------------------------
Read from drat-trim.c @ 2e3b2dc (lines 905, 1479-1483, 1500) and then confirmed
by experiment on this machine:

  * success             -> prints a line `s VERIFIED`,                 exit 0
  * refutation rejected -> prints a line `s NOT VERIFIED`,             exit 1
  * time limit hit      -> prints a line `s TIMEOUT` and exit(0)       exit 0  (!)
  * parse-level trivial UNSAT (e.g. the CNF contains the empty clause)
                        -> prints `c trivial UNSAT` and `s VERIFIED`,  exit 1  (!)
  * memory failure      -> prints `s MEMORY ALLOCATION ERROR`
  * `-S` mode success   -> prints `c VERIFIED derivation: ...`

So the exit code is wrong in BOTH directions, and two distinct output lines
contain the substring "VERIFIED" while meaning "not verified" ("s NOT VERIFIED")
or "a different question was answered" ("c VERIFIED derivation").  Verdict lines
are additionally prefixed with a carriage return, so a naive `^s ` anchor misses
them entirely.

The acceptance rule implemented here is therefore:

    ACCEPT iff, after splitting on both \\n and \\r and stripping each piece,
    some line is EXACTLY "s VERIFIED", and no line is exactly "s TIMEOUT",
    "s NOT VERIFIED", "s DERIVATION" or "s MEMORY ALLOCATION ERROR".

Anything else -- crash, signal, wall-clock kill, missing proof file, empty
output, unparsable output -- is UNRESOLVED, never a pass and never a refutation.
"""
import os, subprocess, time, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
DRAT_TRIM = os.path.normpath(os.path.join(HERE, '..', 'tools', 'drat-trim', 'drat-trim'))

VERDICT_VERIFIED = 'VERIFIED'
VERDICT_NOT_VERIFIED = 'NOT_VERIFIED'
VERDICT_TIMEOUT = 'TIMEOUT'
VERDICT_UNRESOLVED = 'UNRESOLVED'

_FAIL_LINES = {
    's NOT VERIFIED': VERDICT_NOT_VERIFIED,
    's TIMEOUT': VERDICT_TIMEOUT,
    's DERIVATION': VERDICT_UNRESOLVED,
    's MEMORY ALLOCATION ERROR': VERDICT_UNRESOLVED,
}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for blk in iter(lambda: f.read(1 << 20), b''):
            h.update(blk)
    return h.hexdigest()


def binary_provenance(binary=DRAT_TRIM):
    """Identify the exact checker binary in use."""
    out = {'path': binary, 'exists': os.path.exists(binary)}
    if out['exists']:
        out['sha256'] = sha256_file(binary)
        out['size'] = os.path.getsize(binary)
    src = os.path.join(os.path.dirname(binary), 'drat-trim.c')
    if os.path.exists(src):
        out['source_sha256'] = sha256_file(src)
    try:
        g = subprocess.run(['git', '-C', os.path.dirname(binary), 'rev-parse', 'HEAD'],
                           capture_output=True, text=True, timeout=10)
        out['commit'] = g.stdout.strip() or None
        d = subprocess.run(['git', '-C', os.path.dirname(binary), 'status', '--porcelain',
                            '--', 'drat-trim.c'], capture_output=True, text=True, timeout=10)
        out['source_modified'] = bool(d.stdout.strip())
    except Exception as e:                                     # pragma: no cover
        out['commit'] = f'unavailable: {e}'
    return out


def parse_verdict(stdout):
    """Strict verdict extraction.  Returns (verdict, matched_lines)."""
    lines = []
    for chunk in stdout.replace('\r', '\n').split('\n'):
        s = chunk.strip()
        if s:
            lines.append(s)
    hits = [l for l in lines if l.startswith('s ')]
    for l in lines:
        if l in _FAIL_LINES:
            return _FAIL_LINES[l], hits
    if any(l == 's VERIFIED' for l in lines):
        return VERDICT_VERIFIED, hits
    return VERDICT_UNRESOLVED, hits


def check(cnf_path, proof_path, timeout_s=300, binary=DRAT_TRIM, extra_args=()):
    """Check `proof_path` against `cnf_path`.  Never raises; never guesses."""
    rec = dict(checker='drat-trim', cnf_path=cnf_path, proof_path=proof_path,
               verdict=VERDICT_UNRESOLVED, detail=None, exit_code=None,
               wall_s=0.0, timeout_s=timeout_s, verdict_lines=[])
    for p, what in ((binary, 'checker binary'), (cnf_path, 'CNF'), (proof_path, 'proof')):
        if not os.path.exists(p):
            rec['detail'] = f'missing {what}: {p}'
            return rec
    if os.path.getsize(proof_path) == 0:
        rec['detail'] = 'proof file is empty'
        return rec
    # drat-trim's own -t limit is a soft, in-loop check; the hard subprocess kill
    # below is the real bound.  Both are recorded.
    cmd = [binary, cnf_path, proof_path, '-t', str(int(max(1, timeout_s)))] + list(extra_args)
    t0 = time.perf_counter()
    try:
        pr = subprocess.run(cmd, capture_output=True, text=True,
                            timeout=timeout_s + 30)
        rec['wall_s'] = time.perf_counter() - t0
        rec['exit_code'] = pr.returncode
        v, hits = parse_verdict(pr.stdout)
        rec['verdict'], rec['verdict_lines'] = v, hits
        if pr.returncode < 0:
            rec['verdict'] = VERDICT_UNRESOLVED
            rec['detail'] = f'checker killed by signal {-pr.returncode}'
        elif v == VERDICT_UNRESOLVED and not hits:
            rec['detail'] = ('no verdict line in checker output; stderr=' +
                             (pr.stderr or '')[-200:])
        else:
            rec['detail'] = '; '.join(hits) or None
    except subprocess.TimeoutExpired:
        rec['wall_s'] = time.perf_counter() - t0
        rec['verdict'] = VERDICT_TIMEOUT
        rec['detail'] = f'checker exceeded the hard {timeout_s + 30}s subprocess limit'
    except Exception as e:                                     # pragma: no cover
        rec['wall_s'] = time.perf_counter() - t0
        rec['detail'] = f'checker invocation failed: {e!r}'
    return rec


def verified(rec):
    """The ONLY place a pass is decided.  No substring matching anywhere."""
    return rec.get('verdict') == VERDICT_VERIFIED
