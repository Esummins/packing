#!/usr/bin/env python3
"""collect all results/*.json into a summary table + plots of the cell maps."""
import glob
import json
import os
from fractions import Fraction as F

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon as MplPoly


def plot_cells(tag, placed, s, r, out):
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.add_patch(Rectangle((0, 0), float(s), float(s), fill=False, lw=1.5, ec='k'))
    for (x0, y0, x1, y1) in r['cells']:
        x0, y0, x1, y1 = [float(F(v)) for v in (x0, y0, x1, y1)]
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc='#d66', ec='none'))
    for P in placed:
        ax.add_patch(MplPoly([(float(x), float(y)) for (x, y) in P.corners],
                             fc='#9ec5e8', ec='k', lw=0.8, alpha=0.85))
    ax.set_xlim(-0.05, float(s) + 0.05)
    ax.set_ylim(-0.05, float(s) + 0.05)
    ax.set_aspect('equal')
    ax.set_title(f"{tag}: certified dead area {r['area_float']:.4f}")
    plt.savefig(out, dpi=110, bbox_inches='tight')
    plt.close(fig)


if __name__ == '__main__':
    import table_wall
    import pair_sliver
    rows = []
    for path in sorted(glob.glob('results/*.json')):
        tag = os.path.basename(path)[:-5]
        if tag.endswith('_exact'):
            continue
        r = json.load(open(path))
        if 'n_pass' not in r:      # *_exact_target.json etc.
            continue
        meta = r.get('meta', {})
        ex = None
        if os.path.exists(f'results/{tag}_exact.json'):
            e = json.load(open(f'results/{tag}_exact.json'))
            ex = (e['area_float'], len(e['failed']))
        rows.append((tag, meta, r['area_float'], r['n_pass'], ex))
        try:
            if meta.get('kind') == 'wall':
                placed, _, _ = table_wall.wall_config(meta['theta'], int(round(meta['d'] * 100)))
                s = table_wall.S
            elif meta.get('kind') == 'corner':
                placed, _, _ = table_wall.corner_config(meta['theta'])
                s = table_wall.S
            else:
                placed, _, s, _ = pair_sliver.config(meta.get('kind', tag))
            plot_cells(tag, placed, s, r, f'plots/{tag}.png')
        except Exception as exn:
            print(f"(no plot for {tag}: {exn})")
    print(f"{'tag':24s} {'area':>9s} {'cells':>6s} {'exact':>16s}")
    for (tag, meta, a, n, ex) in rows:
        exs = f"{ex[0]:.4f} ({ex[1]} fail)" if ex else "-"
        print(f"{tag:24s} {a:9.4f} {n:6d} {exs:>16s}")
    json.dump({t: a for (t, m, a, n, e) in rows}, open('results/summary.json', 'w'), indent=1)
