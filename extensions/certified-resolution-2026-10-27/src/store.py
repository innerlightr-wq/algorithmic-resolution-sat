# ---------------------------------------------------------------------------
# VENDORED, UNMODIFIED, from the certified-resolution research workspace.
# Origin   : continuation src/store.py (hashing, atomic writes, append-only journal)
# sha256   : 686d4713367b7a45d2c14184043cd4de06154a008f4bdc6985cf9cc39ab6bf31
# Vendored : 2026-10-27.  Only this provenance header was prepended; the code
#            below is byte-identical to the origin file.
# ---------------------------------------------------------------------------
"""Restart-safe persistence: atomic writes, hashed artifacts, append-only journal.

Ordering discipline (this is the whole point of the module)
----------------------------------------------------------
An artifact is fsync'd to its final path BEFORE any journal record mentions it.
A journal record is therefore either absent, or present and backed by a file
whose hash it states.  A record never promises a file that is not there.

Journal records are one JSON object per line, appended and fsync'd.  A process
killed mid-append can leave a torn final line; `read_journal` drops exactly that
line and reports it, rather than failing to load or silently accepting it.

Query states are kept distinct, because conflating them is how an unchecked
UNSAT becomes a "certified" bound:

    SOLVED_SAT          solver said SAT, witness stored, not yet re-verified
    WITNESS_VERIFIED    witness re-checked against original clauses + distances
    SOLVED_UNSAT        solver said UNSAT, proof stored, checking PENDING
    PROOF_VERIFIED      proof independently accepted by the compiled checker
    PROOF_REJECTED      proof independently rejected  (a real alarm)
    PROOF_UNRESOLVED    checker timed out / crashed / no proof   (not a pass)
    TRIVIAL_UNSAT       r >= n, unsatisfiable by arithmetic, no solver involved
    UNKNOWN             solver interrupted; NEVER treated as UNSAT
"""
import os, json, hashlib, tempfile, time

SOLVED_SAT = 'SOLVED_SAT'
WITNESS_VERIFIED = 'WITNESS_VERIFIED'
SOLVED_UNSAT = 'SOLVED_UNSAT'
PROOF_VERIFIED = 'PROOF_VERIFIED'
PROOF_REJECTED = 'PROOF_REJECTED'
PROOF_UNRESOLVED = 'PROOF_UNRESOLVED'
TRIVIAL_UNSAT = 'TRIVIAL_UNSAT'
UNKNOWN = 'UNKNOWN'


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for blk in iter(lambda: f.read(1 << 20), b''):
            h.update(blk)
    return h.hexdigest()


def hash_clauses(repo_clauses):
    """Canonical hash of the ORIGINAL formula, independent of clause order."""
    canon = sorted(tuple(sorted((int(v), int(s)) for (v, s) in c)) for c in repo_clauses)
    return sha256_bytes(json.dumps(canon, separators=(',', ':')).encode())


def hash_A(A):
    """Canonical hash of a frozen observed set (order-independent)."""
    canon = sorted(tuple(int(b) for b in a) for a in A)
    return sha256_bytes(json.dumps(canon, separators=(',', ':')).encode())


def atomic_write_text(path, text):
    """Write + fsync to a temp file in the same directory, then rename.

    The rename is atomic on the same filesystem, and the directory entry is
    fsync'd too, so a crash leaves either the old file or the complete new one.
    """
    d = os.path.dirname(os.path.abspath(path)) or '.'
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix='.tmp-', suffix='.part')
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(d, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return path


def store_artifact(dirpath, name, text):
    """Durably store one artifact; return (path, sha256, bytes)."""
    path = os.path.join(dirpath, name)
    atomic_write_text(path, text)
    return path, sha256_file(path), os.path.getsize(path)


class Journal:
    """Append-only JSONL journal, fsync'd per record."""

    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(os.path.abspath(path)) or '.', exist_ok=True)

    def append(self, rec):
        rec = dict(rec)
        rec.setdefault('ts', time.time())
        line = json.dumps(rec, separators=(',', ':'), sort_keys=True, default=str) + '\n'
        with open(self.path, 'a') as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())
        return rec

    def read(self):
        return read_journal(self.path)


def read_journal(path):
    """Return (records, problems).  A torn final line is dropped and reported."""
    recs, problems = [], []
    if not os.path.exists(path):
        return recs, problems
    with open(path) as f:
        raw = f.readlines()
    for i, line in enumerate(raw):
        s = line.strip()
        if not s:
            continue
        try:
            recs.append(json.loads(s))
        except json.JSONDecodeError as e:
            if i == len(raw) - 1:
                problems.append(f'dropped incomplete final journal record '
                                f'(line {i + 1}, {len(s)} bytes): {e}')
            else:
                problems.append(f'CORRUPT journal record at line {i + 1} '
                                f'(not the last line): {e}')
    return recs, problems


def resumable_queries(records, formula_hash, A_hash):
    """Completed queries that may be reused, keyed by radius.

    A query is reusable ONLY if it was recorded against the same original
    formula AND the same frozen observed set.  A matching instance id or seed is
    deliberately not sufficient: a solver-produced observed set is not
    guaranteed to be reproduced bit-for-bit, and reusing a query across a
    different A would measure a different object.
    """
    out = {}
    for r in records:
        if r.get('kind') != 'query':
            continue
        if r.get('formula_hash') != formula_hash or r.get('A_hash') != A_hash:
            continue
        st = r.get('state')
        if st in (WITNESS_VERIFIED, PROOF_VERIFIED, TRIVIAL_UNSAT,
                  SOLVED_UNSAT, PROOF_UNRESOLVED, PROOF_REJECTED, SOLVED_SAT):
            prev = out.get(r['r'])
            # prefer the strongest record for a radius
            rank = {PROOF_REJECTED: 5, PROOF_VERIFIED: 4, WITNESS_VERIFIED: 4,
                    TRIVIAL_UNSAT: 4, SOLVED_UNSAT: 2, PROOF_UNRESOLVED: 2,
                    SOLVED_SAT: 1}
            if prev is None or rank.get(st, 0) >= rank.get(prev.get('state'), 0):
                out[r['r']] = r
    return out
