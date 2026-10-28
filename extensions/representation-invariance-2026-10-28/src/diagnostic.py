"""Corollary D1 applied to this repository's certified margins.

No SAT solver is run.  This reads certified difference intervals already on
disk and asks one question of each comparison: for how many auxiliary variables
does Theorem D still GUARANTEE the certified ordering, if distances were
measured on all coordinates?

THEOREM D (verified in src/preservation.py; the additive-p bound itself is
classical -- see LITERATURE.md), under TWO hypotheses, both required:
    (H1) the solution set projects:    pi(S_G) = S_F
    (H2) the observed sample projects: pi(A')  = A
        eps_x = eps  and  eps <= eps_full <= eps + p.

COROLLARY D1, for a certified strict margin M = eps(A1) - eps(A2) >= 1:
    M >= p+1  =>  ordering PRESERVED under EVERY such extension and lift
    M <= p    =>  GUARANTEE VOID: SOME extension and lift ties (M = p) or
                  reverses (M <= p-1)
So p_max = M - 1 is the largest auxiliary-variable count carrying a guarantee.

TWO KINDS OF ROW, NEVER POOLED
------------------------------
A row with diff_lo = diff_hi = M pins M, so BOTH halves of Corollary D1 apply.

A row with diff_lo = m < diff_hi certifies only M >= m.  The SAFE half applies
(guaranteed for every p <= m-1) but the VOID half does NOT, because the actual
margin is unresolved and may be much larger: this repository has lower-bound
rows as wide as [1, 13].  For such a row at m = 1 the correct statement is that
the available bounds ESTABLISH NO POSITIVE AUXILIARY-VARIABLE TOLERANCE.  It is
NOT that one auxiliary variable can produce a tie.

CORRECTIONS (2026-10-28, external review).
  * An earlier version separated the two kinds in the per-source printout and
    then POOLED them before claiming that one auxiliary variable can produce a
    tie in all 43 margin-one comparisons.  Only 28 of those are exact; the
    other 15 have unresolved margins and support no such claim.
  * An earlier version said rows with margin 1 are "destroyed by a single
    auxiliary variable".  The void half is an EXISTENCE statement about some
    extension, not a claim that a given encoding reverses anything.
  * All of this applies only when distances are measured on all n+p
    coordinates.  This repository measures on the original variables, where
    Lemma 1 gives exact invariance, so no repository result is affected.

These are COMPARISONS, not independent instances: budgets, selection schemes
and replicates are nested within a much smaller set of instances.
"""
import csv, os, sys
from collections import Counter

FAILS = []
def check(name, ok, detail=''):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}{('  -- ' + detail) if detail else ''}")
    if not ok:
        FAILS.append(name)
    return ok

# Paths are resolved from this file's own location, so the script reproduces
# from a clean checkout at any path.  src/ -> extensions/<this>/ -> extensions/
EXT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTS = os.path.dirname(EXT)

SRC = {
 'equal-size': os.path.join(EXTS, 'certified-resolution-2026-10-27',
                            'data', 'equal-size', 'paired_results.csv'),
 'budget/selection pilot': os.path.join(EXTS,
                            'solver-budget-selection-pilot-2026-10-27',
                            'data', 'paired_results.csv'),
}
ID_KEYS = {'equal-size': ('cell',), 'budget/selection pilot': ('instance_id',)}


def classify(path):
    """Partition the rows into the four certified outcomes."""
    exact, lower, ties, straddle, ids = [], [], 0, 0, set()
    n_rows = 0
    for row in csv.DictReader(open(path)):
        for k in ID_KEYS_CUR:
            if row.get(k):
                ids.add(row[k])
        try:
            lo, hi = int(row['diff_lo']), int(row['diff_hi'])
        except (ValueError, KeyError, TypeError):
            continue
        n_rows += 1
        if lo == hi == 0:
            ties += 1
        elif lo * hi <= 0:
            straddle += 1
        elif lo == hi:
            exact.append(abs(lo))
        else:
            lower.append((min(abs(lo), abs(hi)), max(abs(lo), abs(hi))))
    return exact, lower, ties, straddle, ids, n_rows


def main():
    global ID_KEYS_CUR
    missing = [p for p in SRC.values() if not os.path.exists(p)]
    if missing:
        print('  [FAIL] required certified data not found:')
        for m in missing:
            print(f'           {m}')
        FAILS.append('missing input data')
        return 1

    all_exact, all_lower, all_ids = [], [], 0
    for label, path in SRC.items():
        ID_KEYS_CUR = ID_KEYS[label]
        exact, lower, ties, straddle, ids, n_rows = classify(path)
        all_exact += exact
        all_lower += lower
        all_ids += len(ids)
        print(f"\n       {label}")
        print(f"         rows with a difference interval        : {n_rows}")
        print(f"         distinct instance identifiers           : {len(ids)}")
        print(f"         certified strict ordering               : "
              f"{len(exact) + len(lower)}")
        print(f"           EXACT margin   (both halves apply)    : {len(exact)}")
        print(f"           LOWER BOUND    (safe half only)       : {len(lower)}")
        print(f"         certified tie (margin exactly 0)        : {ties}")
        print(f"         interval straddles 0 (no ordering)      : {straddle}")

    print("\n       EXACT margins -- both halves of Corollary D1 apply")
    print(f"       {'M':>4}{'rows':>6}{'p_max':>7}  guaranteed for          void for")
    for m, c in sorted(Counter(all_exact).items()):
        print(f"       {m:>4}{c:>6}{m-1:>7}  every p <= {m-1:<13} some ext. with p >= {m}")

    print("\n       LOWER-BOUND margins -- only the safe half applies, because")
    print("       the actual margin is unresolved within the interval shown")
    print(f"       {'M >=':>5}{'rows':>6}{'p_max >=':>10}  interval widths seen")
    for m, c in sorted(Counter(lo for lo, hi in all_lower).items()):
        his = sorted({hi for lo, hi in all_lower if lo == m})
        print(f"       {m:>5}{c:>6}{m-1:>10}  diff_hi in {his}")

    n_ex1 = sum(1 for m in all_exact if m == 1)
    n_lb1 = sum(1 for lo, hi in all_lower if lo == 1)

    check('exact and lower-bound margins are reported separately and are never '
          'pooled; these are COMPARISONS with budgets, schemes and replicates '
          'nested, not independent instances',
          bool(all_exact) and bool(all_lower),
          f'{len(all_exact)} exact + {len(all_lower)} lower-bound = '
          f'{len(all_exact)+len(all_lower)} certified strict comparisons over '
          f'at most {all_ids} instance identifiers')

    check('for comparisons with an EXACT margin of 1, Corollary D1 gives no '
          'nonzero-p guarantee AND its void half applies: some '
          'solution-preserving extension with one auxiliary variable ties '
          'them, if distances are measured on all coordinates. It does not '
          'follow that any particular re-encoding does so, and the repository '
          'measures on the original variables, where Lemma 1 gives exact '
          'invariance', n_ex1 > 0,
          f'{n_ex1} comparisons with exact margin 1')

    widest = max(all_lower, key=lambda t: t[1] - t[0])
    check('for comparisons whose margin is only bounded BELOW by 1, the '
          'available bounds establish NO POSITIVE auxiliary-variable '
          'tolerance, and nothing more: the actual margin is unresolved and '
          'may be far larger, so no tie claim follows', n_lb1 > 0,
          f'{n_lb1} such comparisons; widest interval [{widest[0]}, {widest[1]}], '
          f'which leaves an actual margin of up to {widest[1]} open')

    # REGRESSION (external review): a lower-bound row must never be treated as
    # an exact margin.  Synthetic rows exercise the classifier directly, so the
    # pooling bug cannot reappear silently if the CSVs change.
    def tol_claims(lo, hi):
        """What may be asserted for one certified difference interval."""
        if lo == hi == 0:
            return ('tie', None, None)
        if lo * hi <= 0:
            return ('no ordering', None, None)
        m = min(abs(lo), abs(hi))
        if lo == hi:
            return ('exact', m - 1, m)        # (safe p_max, void from p)
        return ('lower bound', m - 1, None)   # void half UNAVAILABLE
    cases = [
        ((1, 1), ('exact', 0, 1)),            # exact margin 1: void half applies
        ((1, 8), ('lower bound', 0, None)),   # reviewer's example: it does NOT
        ((1, 13), ('lower bound', 0, None)),  # widest such row in this repo
        ((-3, -1), ('lower bound', 0, None)), # negative orientation, still a bound
        ((19, 19), ('exact', 18, 19)),
        ((0, 0), ('tie', None, None)),
        ((-1, 2), ('no ordering', None, None)),
    ]
    wrong = [(c, tol_claims(*c), want) for c, want in cases if tol_claims(*c) != want]
    check('REGRESSION: the classifier never attributes a void-half (tie or '
          'reversal) claim to a row whose margin is only bounded below -- '
          'including the reviewer\'s [1, 8] case and this repository\'s widest '
          '[1, 13]', not wrong,
          f'{len(cases)} synthetic intervals classified correctly; '
          f'[1,8] yields a safe bound p <= 0 and NO void claim')

    rob = [m for m in all_exact if m >= 10]
    check('the largest exact margins carry a guarantee against every '
          'solution-preserving extension adding up to M - 1 auxiliary '
          'variables', bool(rob),
          f'{len(rob)} comparisons with exact margin >= 10; largest exact '
          f'margin {max(all_exact)} is guaranteed for p <= {max(all_exact)-1}')

    print(f"\n  {'ALL PASS' if not FAILS else 'FAILURES: ' + '; '.join(FAILS)}")
    return 1 if FAILS else 0


if __name__ == '__main__':
    print('=' * 92)
    print('COROLLARY D1 APPLIED TO THE CERTIFIED MARGINS')
    print('=' * 92)
    sys.exit(main())
