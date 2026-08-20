#!/usr/bin/env python3
"""adversarial spot-check: random LEGAL placements must never meet a certified dead cell.
Independent of the certifier's interval logic (uses plain float SAT + point-in-square)."""
import json
import math
import sys
from fractions import Fraction as F

import numpy as np

sys.path.insert(0, '../../code')
from squares import corners as sq_corners, pair_separations  # noqa: E402

import table_wall  # noqa: E402
import pair_sliver  # noqa: E402


def check(tag, n_samples=400000, seed=7):
    r = json.load(open(f'results/{tag}.json'))
    meta = r['meta']
    if meta['kind'] == 'wall':
        placed, win, _ = table_wall.wall_config(meta['theta'], int(round(meta['d'] * 100)))
        s = float(table_wall.S)
    elif meta['kind'] == 'corner':
        placed, win, _ = table_wall.corner_config(meta['theta'])
        s = float(table_wall.S)
    else:
        placed, win, s_, _ = pair_sliver.config(meta['kind'])
        s = float(s_)
    cells = np.array([[float(F(v)) for v in c] for c in r['cells']])  # (m,4) x0,y0,x1,y1
    if not len(cells):
        print(tag, "no cells")
        return
    P = np.array([[float(p.cx), float(p.cy), 2 * math.atan(float(p.t))] for p in placed])
    rng = np.random.default_rng(seed)
    # sample placements with centres near the cells
    lo = cells[:, :2].min(0) - 0.75
    hi = cells[:, 2:].max(0) + 0.75
    worst = None
    n_legal = n_hit = 0
    for _ in range(n_samples):
        th = rng.uniform(0, math.pi / 2)
        c, sn = math.cos(th), math.sin(th)
        w2 = (c + sn) / 2
        cx = rng.uniform(max(lo[0], w2), min(hi[0], s - w2))
        cy = rng.uniform(max(lo[1], w2), min(hi[1], s - w2))
        X = np.vstack([P, [cx, cy, th]])
        import itertools
        n_all = len(placed) + 1
        idx = [k for k, (i, j) in enumerate(itertools.combinations(range(n_all), 2))
               if j == n_all - 1]
        if pair_separations(X)[idx].min() < 0:
            continue          # overlaps a placed square: not legal
        n_legal += 1
        # does Q meet any dead cell?  test cell corners + centre in Q, and Q corner in cell
        dx = np.array([cells[:, 0], cells[:, 2], cells[:, 0], cells[:, 2],
                       (cells[:, 0] + cells[:, 2]) / 2]).T - cx     # (m,5)
        dy = np.array([cells[:, 1], cells[:, 1], cells[:, 3], cells[:, 3],
                       (cells[:, 1] + cells[:, 3]) / 2]).T - cy
        u = c * dx + sn * dy
        v = -sn * dx + c * dy
        hit = ((np.abs(u) < 0.5 - 1e-9) & (np.abs(v) < 0.5 - 1e-9)).any()
        if not hit:
            qc = sq_corners(cx, cy, th)
            hit = ((qc[:, 0][None, :] > cells[:, 0][:, None] + 1e-9) &
                   (qc[:, 0][None, :] < cells[:, 2][:, None] - 1e-9) &
                   (qc[:, 1][None, :] > cells[:, 1][:, None] + 1e-9) &
                   (qc[:, 1][None, :] < cells[:, 3][:, None] - 1e-9)).any()
        if hit:
            n_hit += 1
            worst = (th, cx, cy)
    print(f"{tag}: {n_legal} legal samples, {n_hit} HITS on dead cells"
          + (f"  WORST {worst}" if worst else "  (OK)"))
    return n_hit


if __name__ == '__main__':
    bad = 0
    for tag in sys.argv[1:] or ['wall_th25_d0', 'corner_th30']:
        bad += check(tag) or 0
    sys.exit(1 if bad else 0)
