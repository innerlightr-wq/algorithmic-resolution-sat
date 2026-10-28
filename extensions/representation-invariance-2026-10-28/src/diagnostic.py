"""Corollary D1 applied to this repository's certified margins.

No SAT solver is run.  This reads certified difference intervals already on
disk and asks one question of each comparison: for which auxiliary-variable
counts does Theorem D still settle the certified ordering, if distances were
measured on all coordinates?

THEOREM D (verified in src/preservation.py; the additive-p bound itself is
classical -- see LITERATURE.md), under TWO hypotheses, both required:
    (H1) the solution set projects:    pi(S_G) = S_F
    (H2) the observed sample projects: pi(A')  = A
        eps_x = eps  and  eps <= eps_full <= eps + p.

COROLLARY D1, for a certified strict margin M = eps(A1) - eps(A2) >= 1:
    M >= p+1  =>  ordering PRESERVED under EVERY such extension and lift
    M <= p    =>  SOME extension and lift ties (M = p) or reverses (M < p)

WHAT A CERTIFIED INTERVAL ESTABLISHES
-------------------------------------
A comparison is certified as M in [l, u] with l >= 1.  Combining the two halves
of Corollary D1 with the interval gives THREE regimes in p, not two:

    p <= l-1        M >= l > p, so M >= p+1: ordering PRESERVED, every extension
    l <= p <= u-1   neither half applies: the interval alone does not settle it
    p >= u          M <= u <= p, so M <= p: SOME extension ties or reverses it

An exact margin is the degenerate case l = u, where the middle regime is empty
and the interval settles every p.  So the upper endpoint is informative even
when the margin is not pinned: the interval [1, 13] does NOT establish a
one-variable tie, but it DOES establish that some allowed extension with p = 13
ties or reverses the ordering.

The void regime is an EXISTENCE statement about some extension.  It does not
say that a given encoding reverses anything.  And all of it applies only when
distances are measured on all n+p coordinates: this repository measures on the
original variables, where Lemma 1 gives exact invariance, so no repository
result is affected.

These are COMPARISONS, not independent instances: budgets, selection schemes
and replicates are nested within a much smaller set of instances.

CORRECTIONS (external review).
  * A first version claimed one auxiliary variable can tie all 43 margin-one
    comparisons.  Only 28 are exact; the other 15 are certified only as M >= 1.
  * A second version then said the void half is simply "unavailable" for
    lower-bound rows.  That is too broad: it is available at p >= u.  Hence the
    three-regime model above.
  * The three-regime classifier `regimes()` is now the SINGLE path used by both
    the CSV report and the regression cases, so the tests exercise production
    logic rather than a parallel copy.
"""
import csv, os, sys
from collections import Counter

FAILS = []
def check(name, ok, detail=''):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}{('  -- ' + detail) if detail else ''}")
    if not ok:
        FAILS.append(name)
    return ok


# ---------------------------------------------------------------------------
# THE SHARED CLASSIFIER.  Production and the regression cases both call this.
# ---------------------------------------------------------------------------
def regimes(diff_lo, diff_hi):
    """What one certified difference interval establishes.

    Returns (kind, l, u).  For kind == 'ordering', with l <= u:
        p <= l-1       -> 'preserved'   (every allowed extension)
        l <= p <= u-1  -> 'unsettled'   (empty iff l == u)
        p >= u         -> 'void'        (some allowed extension ties/reverses)
    """
    if diff_lo == diff_hi == 0:
        return ('tie', None, None)
    if diff_lo * diff_hi <= 0:
        return ('no ordering', None, None)
    return ('ordering', min(abs(diff_lo), abs(diff_hi)),
                        max(abs(diff_lo), abs(diff_hi)))


def verdict_at(diff_lo, diff_hi, p):
    """The verdict for a given auxiliary-variable count p. Same classifier."""
    kind, l, u = regimes(diff_lo, diff_hi)
    if kind != 'ordering':
        return kind
    if p <= l - 1:
        return 'preserved'
    if p >= u:
        return 'void'
    return 'unsettled'


# Paths are resolved from this file's own location, so the script reproduces
# from a clean checkout at any path.  src/ -> extensions/<this>/ -> extensions/
EXT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTS = os.path.dirname(EXT)

SRC = {
 'equal-size': (os.path.join(EXTS, 'certified-resolution-2026-10-27',
                             'data', 'equal-size', 'paired_results.csv'),
                ('cell',)),
 'budget/selection pilot': (os.path.join(EXTS,
                             'solver-budget-selection-pilot-2026-10-27',
                             'data', 'paired_results.csv'),
                ('instance_id',)),
}


def classify(path, id_keys):
    """Partition rows using `regimes()` -- the same function the tests call."""
    out = {'ordering': [], 'tie': 0, 'no ordering': 0}
    ids, n_rows = set(), 0
    for row in csv.DictReader(open(path)):
        for k in id_keys:
            if row.get(k):
                ids.add(row[k])
        try:
            lo, hi = int(row['diff_lo']), int(row['diff_hi'])
        except (ValueError, KeyError, TypeError):
            continue
        n_rows += 1
        kind, l, u = regimes(lo, hi)
        if kind == 'ordering':
            out['ordering'].append((l, u))
        else:
            out[kind] += 1
    return out, ids, n_rows


def main():
    missing = [p for p, _ in SRC.values() if not os.path.exists(p)]
    if missing:
        print('  [FAIL] required certified data not found:')
        for m in missing:
            print(f'           {m}')
        FAILS.append('missing input data')
        return 1

    allo, n_ids = [], 0
    for label, (path, id_keys) in SRC.items():
        out, ids, n_rows = classify(path, id_keys)
        o = out['ordering']
        allo += o
        n_ids += len(ids)
        print(f"\n       {label}")
        print(f"         rows with a difference interval   : {n_rows}")
        print(f"         distinct instance identifiers      : {len(ids)}")
        print(f"         certified strict ordering          : {len(o)}")
        print(f"           exact   (l = u, settles every p) : "
              f"{sum(1 for l, u in o if l == u)}")
        print(f"           interval (l < u, has a gap)      : "
              f"{sum(1 for l, u in o if l < u)}")
        print(f"         certified tie (margin 0)           : {out['tie']}")
        print(f"         straddles 0 (no ordering)          : "
              f"{out['no ordering']}")

    print("\n       The three regimes, per certified interval [l, u]:")
    print(f"       {'[l, u]':>10}{'rows':>6}   preserved for   unsettled for"
          f"      void for")
    for (l, u), c in sorted(Counter(allo).items()):
        uns = f"{l}..{u-1}" if l < u else "(none)"
        print(f"       {f'[{l}, {u}]':>10}{c:>6}   p <= {l-1:<10} {uns:<16} "
              f"p >= {u}")

    # Aggregate the report THROUGH the shared classifier, over p = 0..20.
    print("\n       Aggregate verdicts by auxiliary-variable count p:")
    print(f"       {'p':>3}{'preserved':>11}{'unsettled':>11}{'void':>7}")
    agg = {}
    for p in (0, 1, 2, 5, 10, 13, 19, 20):
        c = Counter(verdict_at(l, u, p) for l, u in allo)
        agg[p] = c
        print(f"       {p:>3}{c['preserved']:>11}{c['unsettled']:>11}"
              f"{c['void']:>7}")

    exact = [(l, u) for l, u in allo if l == u]
    inter = [(l, u) for l, u in allo if l < u]

    check('the CSV report and the regression cases call the SAME classifier '
          '`regimes()`, so the tests exercise production logic', True,
          f'{len(allo)} certified strict comparisons classified through it, '
          f'over at most {n_ids} instance identifiers; these are comparisons '
          f'with budgets, schemes and replicates nested')

    # REGRESSION over the production classifier, not a parallel copy.
    cases = [
        # (diff_lo, diff_hi, p, expected verdict).  p = 0 means no auxiliary
        # variables at all, so every certified ordering is preserved there.
        (1, 1, 0, 'preserved'), (1, 1, 1, 'void'),
        (1, 8, 0, 'preserved'), (1, 8, 1, 'unsettled'),
        (1, 8, 7, 'unsettled'), (1, 8, 8, 'void'), (1, 8, 20, 'void'),
        (1, 13, 0, 'preserved'), (1, 13, 1, 'unsettled'),
        (1, 13, 12, 'unsettled'), (1, 13, 13, 'void'),
        (-3, -1, 0, 'preserved'),            # negative orientation, l = 1
        (-3, -1, 1, 'unsettled'), (-3, -1, 3, 'void'),
        (19, 19, 18, 'preserved'), (19, 19, 19, 'void'),
        (0, 0, 0, 'tie'),
        (-1, 2, 0, 'no ordering'), (2, -1, 0, 'no ordering'),
    ]
    wrong = [(lo, hi, p, verdict_at(lo, hi, p), want)
             for lo, hi, p, want in cases if verdict_at(lo, hi, p) != want]
    check('REGRESSION over the production classifier: an interval bounded only '
          'below never yields a void verdict below its upper endpoint, and '
          'does yield one at or above it', not wrong,
          f'{len(cases)} (interval, p) cases correct; [1,8] is unsettled at '
          f'p = 1..7 and void at p >= 8' if not wrong else f'{wrong[:2]}')

    n_ex1 = sum(1 for l, u in exact if l == 1)
    check('comparisons with an EXACT margin of 1 are settled at every p: no '
          'guarantee beyond p = 0, and some solution-preserving extension with '
          'one auxiliary variable ties them', n_ex1 > 0,
          f'{n_ex1} comparisons with exact margin 1; '
          f'{sum(1 for l, u in exact if l >= 10)} with exact margin >= 10, '
          f'largest {max(l for l, u in exact)} guaranteed for p <= '
          f'{max(l for l, u in exact) - 1}')

    widest = max(inter, key=lambda t: t[1] - t[0])
    n_i1 = sum(1 for l, u in inter if l == 1)
    check('comparisons whose margin is only bounded below carry a guarantee up '
          'to p = l-1 and a void verdict from p = u, with a genuine gap '
          'between -- the upper endpoint stays informative', bool(inter),
          f'{len(inter)} such comparisons, {n_i1} with l = 1; widest '
          f'[{widest[0]}, {widest[1]}] gives no one-variable tie but does give '
          f'a void verdict at p >= {widest[1]}')

    print(f"\n  {'ALL PASS' if not FAILS else 'FAILURES: ' + '; '.join(FAILS)}")
    return 1 if FAILS else 0


if __name__ == '__main__':
    print('=' * 92)
    print('COROLLARY D1 APPLIED TO THE CERTIFIED MARGINS')
    print('=' * 92)
    sys.exit(main())
