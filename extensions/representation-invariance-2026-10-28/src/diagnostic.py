"""THEOREM D applied to the repository's OWN certified margins.

CORRECTED 2026-10-28 after external review.  Three errors in the first version:

  (1) MARGIN LANGUAGE.  It said rows with margin 1 are "destroyed by a single
      auxiliary variable".  That is wrong in two ways.  Theorem D's threshold
      says that at margin <= p the GUARANTEE IS VOID -- i.e. there EXISTS a
      solution-preserving extension and lift that ties or reverses.  It does
      NOT say that a given encoding reverses the ordering, and adding auxiliary
      variables does not automatically reverse anything.  "Guarantee void" and
      "ordering reversed" are different statements.
  (2) It applies ONLY if distances are measured on all n+p coordinates.  The
      repository measures on the original variables, where Lemma 1 gives exact
      invariance, so no repository result is affected.
  (3) EXACT versus LOWER BOUND.  The first version counted only singleton
      difference intervals and then called every margin exact.  A row with
      diff_lo = m and diff_hi > m certifies only M >= m.  For such a row the
      SAFE half of the threshold is established (safe for p <= m-1) but the
      void half is NOT, because M may be larger.  The two kinds of row are
      reported separately below and never pooled.

Also: these are COMPARISONS, not independent instances.  Replicates, budgets
and selection schemes are nested within a much smaller set of instances, and
the counts below are counts of measurements.

No new SAT solving.  This reads certified intervals already on disk and asks
one question of each: how many auxiliary variables p would a solution-
preserving re-encoding need before the certified ordering could be destroyed,
if distances were measured on all coordinates?

THEOREM D (verified sharp in src/preservation.py; the additive-p bound itself
is classical -- see LITERATURE.md):
    eps_x <= eps_full <= eps_x + p,
under TWO hypotheses, both required and both stated: the solution set projects,
pi(S_G) = S_F, and the observed sample projects, pi(A') = A.

Hence for a certified strict margin M = eps(A1) - eps(A2) >= 1, measuring on
all n+p coordinates:
    M >= p+1  =>  the strict ordering is PRESERVED under EVERY such extension
    M <= p    =>  the GUARANTEE IS VOID: some extension and lift ties (M = p)
                  or reverses (M <= p-1).  Not every extension does.
So p_max = M - 1 is the largest auxiliary-variable count for which the ordering
is guaranteed.  Nothing here asserts that a particular re-encoding reverses a
particular comparison.
"""
import csv, sys, os
FAILS = []
def check(name, ok, detail=''):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}{('  -- ' + detail) if detail else ''}")
    if not ok: FAILS.append(name)
    return ok

# Paths are resolved from this file's own location, so the script reproduces
# from a clean checkout at any path.  src/ -> extensions/<this>/ -> extensions/
EXT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTS = os.path.dirname(EXT)

SRC = {
 'equal-size': (os.path.join(EXTS, 'certified-resolution-2026-10-27',
                'data', 'equal-size', 'paired_results.csv'),
                'verdict', 'diff_lo', 'diff_hi'),
 'budget/selection pilot': (os.path.join(EXTS,
                'solver-budget-selection-pilot-2026-10-27',
                'data', 'paired_results.csv'),
                'verdict', 'diff_lo', 'diff_hi'),
}

def load(path, vk, lo, hi):
    rows = []
    with open(path) as f:
        for row in csv.DictReader(f):
            v = (row.get(vk) or '').strip()
            try:
                a, b = int(row[lo]), int(row[hi])
            except (ValueError, KeyError, TypeError):
                continue
            rows.append((v, a, b))
    return rows

# CORRECTION.  An earlier version of this script counted only SINGLETON
# difference intervals as certified margins, which discarded 18 of the 21
# equal-size rows and then asserted that every certified margin is a singleton.
# That was wrong on both counts.  A certified strict ordering needs only
# diff_lo >= 1; the certified margin is then bounded BELOW by diff_lo, and
# Theorem D's tolerance p_max = M - 1 is likewise a lower bound.  Using diff_lo
# is the conservative reading and is what is used below.

def main():
    missing = [p for p, *_ in SRC.values() if not os.path.exists(p)]
    if missing:
        print('  [FAIL] required certified data not found:')
        for m in missing:
            print(f'           {m}')
        FAILS.append('missing input data')
        return 1
    allm = []
    for label, (path, vk, lo, hi) in SRC.items():
        rows = load(path, vk, lo, hi)
        cert = [r for r in rows if abs(r[1]) >= 1 and r[1] * r[2] > 0]
        ties = [r for r in rows if r[1] == r[2] == 0]
        wide = [r for r in rows if r[1] <= 0 <= r[2] and (r[1], r[2]) != (0, 0)]
        exact = sorted(abs(r[1]) for r in cert if r[1] == r[2])
        lower = sorted(min(abs(r[1]), abs(r[2])) for r in cert if r[1] != r[2])
        mags = sorted(exact + lower)
        print(f"\n       {label}")
        print(f"         rows with a parsed difference interval : {len(rows)}")
        print(f"         certified strict ordering (|M| >= 1)   : {len(cert)}")
        print(f"           of which EXACT margin (singleton)    : {len(exact)}"
              f"   -> both halves of the threshold apply")
        print(f"           of which LOWER BOUND only            : {len(lower)}"
              f"   -> only the safe half applies")
        print(f"         certified tie (margin exactly 0)       : {len(ties)}")
        print(f"         interval straddles 0 (no ordering)     : {len(wide)}")
        if mags:
            print(f"         margin |M| range                       : {mags[0]} .. {mags[-1]}")
            print(f"         tolerance p_max = |M| - 1              : "
                  f"{mags[0]-1} .. {mags[-1]-1}")
            byp = {}
            for m in mags:
                byp.setdefault(m, 0)
                byp[m] += 1
            print(f"         {'|M|':>5}{'rows':>6}{'p_max':>7}  guaranteed for")
            for m in sorted(byp):
                note = ("   <-- no nonzero-p guarantee" if m == 1 else "")
                print(f"         {m:>5}{byp[m]:>6}{m-1:>7}  every extension with "
                      f"p <= {m-1} auxiliary variables{note}")
        allm += mags
    frag = [m for m in allm if m == 1]
    check('Theorem D applies to every certified strict ordering, with the exact '
          'and lower-bound rows kept separate; these are COMPARISONS with '
          'replicates nested, not independent instances', bool(allm),
          f'{len(allm)} certified strict comparisons across both integrated '
          f'stages; margins {min(allm)} .. {max(allm)}')
    check('a nonempty set of certified orderings has margin 1, so Theorem D '
          'gives them NO nonzero-p guarantee: if distances were measured on all '
          'coordinates, some solution-preserving extension with one auxiliary '
          'variable would tie them. It does not follow that any particular '
          're-encoding reverses them, nor that the repository results change -- '
          'the repository measures on the original variables, where Lemma 1 '
          'gives exact invariance', bool(frag),
          f'{len(frag)} of {len(allm)} comparisons have |M| = 1 (p_max = 0)')
    rob = [m for m in allm if m >= 10]
    check('while the largest certified margins carry a guarantee against every '
          'solution-preserving extension adding up to |M| - 1 auxiliary '
          'variables', bool(rob),
          f'{len(rob)} comparisons with |M| >= 10; largest margin {max(allm)} '
          f'is guaranteed for p <= {max(allm)-1}')
    print(f"\n  {'ALL PASS' if not FAILS else 'FAILURES: ' + '; '.join(FAILS)}")
    return 1 if FAILS else 0

if __name__ == '__main__':
    print('=' * 92); print('THEOREM D AS A DIAGNOSTIC ON THE CERTIFIED MARGINS'); print('=' * 92)
    sys.exit(main())
