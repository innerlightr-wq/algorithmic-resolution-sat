"""Regenerate every reported table from the source data.

No figure in the consolidation note is typed by hand: this script reads
data/stage1.json, data/stage2.json and data/pairing.json and emits both LaTeX
and Markdown.  Ratios are computed from UNROUNDED seconds.

Usage:  python3 src/maketables.py [--latex | --markdown]  > tables.tex
"""
import json, sys, os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda n: json.load(open(os.path.join(HERE, 'data', n)))


def load():
    s1, s2 = D('stage1.json'), D('stage2.json')
    pr = D('pairing.json') if os.path.exists(
        os.path.join(HERE, 'data', 'pairing.json')) else {}
    by = {}
    for r in s2['rows']:
        by.setdefault(r['tag'], {})[r['method']] = r
    return s1, s2, pr, by


def agg(by, tags, m, k):
    return sum(by[t][m][k] for t in tags)


def partition(by, pr=None):
    res = [t for t, v in by.items() if v['S']['exact'] and v['L']['exact']]
    unres = [t for t in by if t not in res]
    paired = (pr or {}).get('paired', [])
    return res, unres, [t for t in res if t in paired]


def fmt(x, nd=1):
    return f'{x:.{nd}f}'


def tables(latex=True):
    s1, s2, pr, by = load()
    res, unres, paired = partition(by, pr)
    L, out = latex, []
    def row(*c):
        out.append((' & '.join(str(x) for x in c) + r' \\') if L
                   else ('| ' + ' | '.join(str(x) for x in c) + ' |'))
    def rule():
        out.append(r'\midrule' if L else None)
    CAPS = []
    _pending = {}
    def head(cols, align, caption=None, label=None):
        if L:
            if caption:
                out.append(r'\begin{table}[htbp]'); out.append(r'\centering')
                _pending['c'], _pending['l'] = caption, label
            out.append(r'\begin{tabular}{' + align + '}'); out.append(r'\toprule')
            out.append(' & '.join(cols) + r' \\'); out.append(r'\midrule')
        else:
            out.append('| ' + ' | '.join(cols) + ' |')
            out.append('|' + '|'.join(['---'] * len(cols)) + '|')
    def end(caption=None, label=None):
        caption = caption or _pending.pop('c', None)
        label = label or _pending.pop('l', None)
        if L:
            out.append(r'\bottomrule'); out.append(r'\end{tabular}')
            if caption:
                out.append(r'\caption{' + caption + '}')
                out.append(r'\label{tab:' + label + '}')
                out.append(r'\end{table}')
        out.append('')

    # ---- Table 1: stage 1 witness replay
    out.append('% TABLE 1 -- Stage 1 witness replay' if L else '### Table 1')
    head(['source', 'witnesses', 'loose', 'max gain', 'mean gain'],
         'lrrrr', caption='Stage 1: stored witnesses replayed against their recorded samples. A witness is \\emph{loose} when its actual distance exceeds the threshold that was requested.', label='stage1')
    for key, lab in (('opt', 'optimization (n=64 units)'),
                     ('pilot', 'budget/selection pilot')):
        d = s1[key]
        row(lab, d['n'], d['loose'], d['max_gain'], fmt(d['mean_gain'], 3))
    rule()
    tot = s1['opt']['n'] + s1['pilot']['n']
    lo = s1['opt']['loose'] + s1['pilot']['loose']
    mg = max(s1['opt']['max_gain'], s1['pilot']['max_gain'])
    mean = (s1['opt']['n'] * s1['opt']['mean_gain']
            + s1['pilot']['n'] * s1['pilot']['mean_gain']) / tot
    row(r'\textbf{total}' if L else '**total**', tot, lo, mg, fmt(mean, 3))
    end()

    # ---- Table 2: stage 1 aggregation
    out.append('% TABLE 2 -- Stage 1 effect on reported quantities' if L
               else '### Table 2')
    head(['quantity', 'optimization', 'pilot'], 'lrr', caption='Stage 1: effect on the quantity the reported intervals use. No reconstructed measurement gains a better certified lower bound.', label='stage1agg')
    row('measurements reconstructed', s1['opt_measurements'],
        s1['pilot_measurements'])
    row('with an improved certified lower bound', s1['opt_improved'],
        s1['pilot_improved'])
    end()

    # ---- Table 3: per-unit stage 2
    out.append('% TABLE 3 -- Stage 2 per unit' if L else '### Table 3')
    head(['unit', '$|A|$', 'S total (s)', 'L total (s)', 'ratio',
          'S width', 'L width', 'L constraints'], 'lrrrrrrl', caption='Stage 2, per unit. The first four rows are the units exact under both methods; the remaining five did not resolve. Ratios are computed from unrounded seconds.', label='perunit')
    for t in res + unres:
        S, Lz = by[t]['S'], by[t]['L']
        row((t.replace('_', r'\_') if L else '`' + t + '`'), S['A_size'],
            fmt(S['total_s']), fmt(Lz['total_s']),
            fmt(S['total_s'] / Lz['total_s'], 2),
            S['final_width'], Lz['final_width'],
            f"{Lz['constraints_min']}--{Lz['constraints_max']}")
        if t == res[-1]:
            rule()
    end()

    # ---- Table 4: paired totals
    out.append('% TABLE 4 -- paired totals' if L else '### Table 4')
    head(['group', 'metric', 'S', 'L', 'ratio'], 'llrrr', caption="Stage 2 paired totals. ``Verified paired'' are the units whose radius sequences and per-query outcomes were confirmed identical (Table~\\ref{tab:pairing}). The all-units row mixes different amounts of completed work and is not offered as a headline.", label='totals')
    groups = [(f'verified paired ({len(paired)})', paired),
              (f'exact under both ({len(res)})', res),
              (f'unresolved ({len(unres)})', unres),
              (f'all {len(by)} units', list(by))]
    for name, tags in groups:
        if not tags:
            continue
        first = True
        for k, lab in (('total_s', 'total s'), ('solve_s', 'solve s'),
                       ('check_s', 'check s'), ('encode_s', 'encode s')):
            a, b = agg(by, tags, 'S', k), agg(by, tags, 'L', k)
            row(name if first else '', lab, fmt(a), fmt(b),
                fmt(a / b, 2) if b else '--')
            first = False
        row('', 'queries', agg(by, tags, 'S', 'queries'),
            agg(by, tags, 'L', 'queries'), '--')
        row('', 'summed width', agg(by, tags, 'S', 'final_width'),
            agg(by, tags, 'L', 'final_width'), '--')
        rule()
    end()

    # ---- Table 5: certification integrity
    out.append('% TABLE 5 -- certification integrity' if L else '### Table 5')
    head(['outcome', 'S', 'L'], 'lrr', caption='Stage 2 certification integrity across all 18 measurements.', label='integrity')
    for k, lab in (('n_cert', 'certified UNSAT upper bounds'),
                   ('n_sat', 'verified SAT witnesses'),
                   ('n_unchecked', 'unchecked UNSAT (moves no bound)'),
                   ('n_unknown', 'UNKNOWN'),
                   ('n_trivial', 'trivial UNSAT (arithmetic)')):
        row(lab, agg(by, list(by), 'S', k), agg(by, list(by), 'L', k))
    al = [r['alarm'] for r in s2['rows'] if r['alarm']]
    row('alarms', len(al), len(al))
    end()

    # ---- Table 6: pairing verification
    if pr:
        out.append('% TABLE 6 -- paired-per-query verification' if L
                   else '### Table 6')
        head(['unit', 'hashes', 'S radii', 'L radii', 'identical', 'stop'],
             'llllll', caption='Paired-per-query verification. One unit fails: its static ladder hit the budget, the sequences differ, and its exact answer did not reproduce.', label='pairing')
        for t, v in sorted(pr.get('units', {}).items()):
            if 'S' not in v:
                row((t.replace('_', r'\_') if L else t), 'MISMATCH',
                    '--', '--', '--', '--')
                continue
            row((t.replace('_', r'\_') if L else '`' + t + '`'),
                'ok' if v['hashes_ok'] else 'MISMATCH',
                ','.join(map(str, v['S']['radii'])),
                ','.join(map(str, v['L']['radii'])),
                ('yes' if (v['same_radii'] and v['same_outcomes']
                           and v.get('agrees_with_stage2')) else 'NO'),
                v['S']['stop'] + '/' + v['L']['stop'])
        end()
    return '\n'.join(x for x in out if x is not None)


if __name__ == '__main__':
    print(tables(latex=('--markdown' not in sys.argv)))
