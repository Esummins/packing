"""A235 -- the COMPLETE first-order union test at a witness: enumerate every consistent selection (one separating
axis per touching pair that has two tied axes -- flush pairs and VV pairs; walls and external rows kept) and ask
whether the point is Fritz-John (lam0 = 1, or a self-stress) for NLP(S).  D3': a minimiser is a local minimum of
every NLP(S) whose feasible set contains it, so ONE failing selection excludes the point at first order (Gordan:
a strictly opening, strictly descending direction exists for that selection).  Attribution to the VV pair under
test: a failing selection whose VV-axis flip alone restores FJ.
    python select235.py [--cap 14]   -> results/select235.jsonl  (witnesses with a loadable tilted VV contact)
"""
import itertools
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vv235 as V             # noqa: E402
import stress234 as ST        # noqa: E402

OUT = os.path.join(V.ATT, 'results', 'select235.jsonl')
LOAD_TOL = 1e-6


def axes_of(rows):
    """{pair: {(owner, edge): [row indices]}} over the edge rows (line rows included: they belong to the axis)."""
    pairs = {}
    for k, r in enumerate(rows):
        if r['kind'] == 'edge':
            key = (min(r['i'], r['j']), max(r['i'], r['j']))
            pairs.setdefault(key, {}).setdefault((r['j'], r['edge']), []).append(k)
    return pairs


def selections(rows, cap, rng):
    """yield (choice dict pair -> axis, row index list); exhaustive when the number of 2-axis pairs <= cap,
    else 2^cap random samples."""
    pairs = axes_of(rows)
    single = [k for k, r in enumerate(rows) if r['kind'] != 'edge']
    multi = [(p, sorted(ax)) for p, ax in pairs.items() if len(ax) > 1]
    fixed = [k for p, ax in pairs.items() if len(ax) == 1 for k in list(ax.values())[0]]
    n_multi = len(multi)
    if n_multi <= cap:
        combos = itertools.product(*[range(len(ax)) for _, ax in multi])
        total = int(np.prod([len(ax) for _, ax in multi])) if multi else 1
    else:
        total = 2 ** cap
        combos = (tuple(rng.integers(len(ax)) for _, ax in multi) for _ in range(total))
    for c in combos:
        choice = {p: ax[c[a]] for a, (p, ax) in enumerate(multi)}
        idx = single + fixed + [k for a, (p, ax) in enumerate(multi) for k in pairs[p][ax[c[a]]]]
        yield choice, sorted(idx)
    return


def run_witness(w, vv_pairs, cap, rng):
    rows, A = w['rows'], w['A']
    pairs = axes_of(rows)
    n_multi = sum(1 for ax in pairs.values() if len(ax) > 1)
    out = {'name': w['name'], 'rid': w.get('rid'), 'cls': w['cls'], 's': float(w['z'][-1]), 'n_rows': len(rows),
           'n_pairs': len(pairs), 'n_two_axis_pairs': n_multi, 'exhaustive': n_multi <= cap}
    status = {}
    vv_rows = {k for e in vv_pairs for k in (e['rowA'], e['rowB'])}
    red, indep = [], 0
    for choice, idx in selections(rows, cap, rng):
        st, _ = V.fj_status(A[idx])
        status[tuple(sorted(choice.items()))] = st
        red.append(len(idx) - int(np.linalg.matrix_rank(A[idx], tol=1e-9)))
        for k in vv_rows & set(idx):                       # NO-VV-IND's hypothesis inside this selection
            if not V.in_span(A, k, [m for m in idx if m != k])[0]:
                indep += 1
    out['n_selections'] = len(status)
    out['rows_per_selection'] = [min(len(i) for _, i in selections(rows, cap, rng)), max(len(i) for _, i in selections(rows, cap, rng))]
    out['redundancy_min_max'] = [min(red), max(red)]
    out['rank_full'] = bool(min(len(i) for _, i in selections(rows, cap, rng)) - min(red) >= A.shape[1])
    out['n_vv_row_independent_in_a_selection'] = indep
    out['n_kkt'] = sum(v == 'KKT' for v in status.values())
    out['n_self_stress'] = sum(v == 'self-stress' for v in status.values())
    out['n_not_fj'] = sum(v == 'none' for v in status.values())
    out['excluded'] = out['n_not_fj'] > 0
    per = []
    for e in vv_pairs:
        p = tuple(e['pair'])
        axA = (p[0], next(r['edge'] for k, r in enumerate(rows) if k == e['rowA']))
        axB = (p[1], rows[e['rowB']]['edge'])
        attr = {'pair': list(p), 'fail_with_A': 0, 'fail_with_B': 0, 'fail_only_because_A': 0, 'fail_only_because_B': 0}
        for key, st in status.items():
            if st != 'none':
                continue
            d = dict(key)
            if d.get(p) == axA:
                attr['fail_with_A'] += 1
                d2 = dict(d)
                d2[p] = axB
                if status.get(tuple(sorted(d2.items()))) not in (None, 'none'):
                    attr['fail_only_because_A'] += 1
            elif d.get(p) == axB:
                attr['fail_with_B'] += 1
                d2 = dict(d)
                d2[p] = axA
                if status.get(tuple(sorted(d2.items()))) not in (None, 'none'):
                    attr['fail_only_because_B'] += 1
        per.append(attr)
    out['vv'] = per
    out['vv_attributable'] = any(a['fail_only_because_A'] + a['fail_only_because_B'] > 0 for a in per)
    return out


def main():
    ST.set_priority()
    cap = int(sys.argv[sys.argv.index('--cap') + 1]) if '--cap' in sys.argv else 14
    rng = np.random.default_rng(235)
    t0 = time.time()
    res = []
    with open(OUT, 'w', encoding='utf-8') as f:
        for l in open(ST.WIT, encoding='utf-8'):
            raw = json.loads(l)
            if raw['cls'] not in ('HELD', 'CROWD'):
                continue
            w = ST.from_w217(raw)
            w['rid'] = raw['rid']
            cen, _ = V.analyse(w)
            vv = [e for e in cen['vv'] if e['loadable']]
            if not vv:
                continue
            o = run_witness(w, vv, cap, rng)
            o['t_s'] = round(time.time() - t0, 1)
            res.append(o)
            f.write(json.dumps(o, default=float) + '\n')
            print('%s %s two-axis pairs %d selections %d | KKT %d self-stress %d NOT-FJ %d | VV-attributable %s | %s | rows %s redundancy %s VV-row independent in %d selections' % (
                o['name'], o['cls'], o['n_two_axis_pairs'], o['n_selections'], o['n_kkt'], o['n_self_stress'], o['n_not_fj'],
                o['vv_attributable'], [(a['pair'], a['fail_only_because_A'], a['fail_only_because_B']) for a in o['vv']],
                o['rows_per_selection'], o['redundancy_min_max'], o['n_vv_row_independent_in_a_selection']), flush=True)
    print('%d witnesses, %.0f s; excluded at first order by SOME consistent selection: %d (VV-attributable %d)' % (
        len(res), time.time() - t0, sum(o['excluded'] for o in res), sum(o['vv_attributable'] for o in res)))
    for cls in ('HELD', 'CROWD'):
        rs = [o for o in res if o['cls'] == cls]
        print('  %-5s %d witnesses, excluded %d, VV-attributable %d, exhaustive %d' % (
            cls, len(rs), sum(o['excluded'] for o in rs), sum(o['vv_attributable'] for o in rs), sum(o['exhaustive'] for o in rs)))


if __name__ == '__main__':
    main()
