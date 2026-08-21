#!/usr/bin/env python3
"""
adversarial.py -- independent spot-check of A25 atlas entries.

Completely independent of the certifier's interval logic: for an atlas entry we
sample RANDOM REALISATIONS of its core box(es) (actual unit squares with centres
and tilts drawn from the box, kept only if they are inside the container and
pairwise interior-disjoint), then sample many random unit-square placements that
are LEGAL for that realisation (plain float SAT), and check that none of them
meets a certified dead tile.  A hit would refute the certificate.

  python adversarial.py --tag s384 --s 96/25 --top 40
  python adversarial.py --config results/headline_3.84.json --s 96/25   # the min-k set
"""
import argparse
import itertools
import json
import math
import os
from fractions import Fraction as F

import numpy as np

from atlas_lib import clip_box


def sq_corners(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    return np.array([[cx + c * u - s * v, cy + s * u + c * v]
                     for (u, v) in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))])


def sat_gap(A, ca, sa, B, cb, sb):
    best = -1e18
    for (ax, ay) in ((ca, sa), (-sa, ca), (cb, sb), (-sb, cb)):
        pa = A[:, 0] * ax + A[:, 1] * ay
        pb = B[:, 0] * ax + B[:, 1] * ay
        g = max(pb.min() - pa.max(), pa.min() - pb.max())
        best = max(best, g)
    return best


def check(boxes, cells, s, n_real=120, n_place=3000, seed=11, margin=1e-9):
    """boxes: list of (t0,t1,x0,x1,y0,y1) floats; cells: (m,4) x0,y0,x1,y1."""
    rng = np.random.default_rng(seed)
    lo = cells[:, :2].min(0) - 0.75
    hi = cells[:, 2:].max(0) + 0.75
    n_real_ok = n_legal = n_hit = 0
    worst = None
    for _ in range(n_real):
        P = []
        for (t0, t1, x0, x1, y0, y1) in boxes:
            t = rng.uniform(t0, t1)
            th = 2 * math.atan(t)
            w2 = (math.cos(th) + math.sin(th)) / 2
            cx = rng.uniform(max(x0, w2), min(x1, s - w2))
            cy = rng.uniform(max(y0, w2), min(y1, s - w2))
            if cx > min(x1, s - w2) or cy > min(y1, s - w2):
                P = None
                break
            P.append((cx, cy, th))
        if P is None:
            continue
        ok = True
        for (i, j) in itertools.combinations(range(len(P)), 2):
            a, b = P[i], P[j]
            if sat_gap(sq_corners(*a), math.cos(a[2]), math.sin(a[2]),
                       sq_corners(*b), math.cos(b[2]), math.sin(b[2])) < 0:
                ok = False
                break
        if not ok:
            continue                      # not a realisable hypothesis instance
        n_real_ok += 1
        PC = [(sq_corners(*p), math.cos(p[2]), math.sin(p[2])) for p in P]
        th = rng.uniform(0, math.pi / 2, n_place)
        cth, sth = np.cos(th), np.sin(th)
        w2 = (cth + sth) / 2
        cx = rng.uniform(lo[0], hi[0], n_place)
        cy = rng.uniform(lo[1], hi[1], n_place)
        adm = (cx >= w2) & (cx <= s - w2) & (cy >= w2) & (cy <= s - w2)
        legal = adm.copy()
        QX = cx[:, None] + (cth[:, None] * np.array([-.5, .5, .5, -.5])[None, :]
                            - sth[:, None] * np.array([-.5, -.5, .5, .5])[None, :])
        QY = cy[:, None] + (sth[:, None] * np.array([-.5, .5, .5, -.5])[None, :]
                            + cth[:, None] * np.array([-.5, -.5, .5, .5])[None, :])
        for (B, cb, sb) in PC:
            gap = np.full(n_place, -1e18)
            for k in range(n_place and 1):
                pass
            for (axv, ayv) in ((cth, sth), (-sth, cth)):
                pa = QX * axv[:, None] + QY * ayv[:, None]
                pb = B[:, 0][None, :] * axv[:, None] + B[:, 1][None, :] * ayv[:, None]
                gap = np.maximum(gap, np.maximum(pb.min(1) - pa.max(1),
                                                 pa.min(1) - pb.max(1)))
            for (axv, ayv) in ((cb, sb), (-sb, cb)):
                pa = QX * axv + QY * ayv
                pb = B[:, 0] * axv + B[:, 1] * ayv
                gap = np.maximum(gap, np.maximum(pb.min() - pa.max(1),
                                                 pa.min(1) - pb.max()))
            legal &= gap > margin
        idx = np.nonzero(legal)[0]
        n_legal += len(idx)
        if not len(idx):
            continue
        # does a legal Q meet a dead tile?  (tile corners/centre inside Q, or a Q
        # corner inside a tile -- for two convex sets one of these must happen if
        # the intersection has interior)
        for i in idx:
            c_, s_ = cth[i], sth[i]
            px = np.concatenate([cells[:, 0], cells[:, 2], cells[:, 0], cells[:, 2],
                                 (cells[:, 0] + cells[:, 2]) / 2]) - cx[i]
            py = np.concatenate([cells[:, 1], cells[:, 1], cells[:, 3], cells[:, 3],
                                 (cells[:, 1] + cells[:, 3]) / 2]) - cy[i]
            u = c_ * px + s_ * py
            v = -s_ * px + c_ * py
            hit = ((np.abs(u) < .5 - 1e-9) & (np.abs(v) < .5 - 1e-9)).any()
            if not hit:
                qc = np.stack([QX[i], QY[i]], 1)
                hit = ((qc[:, 0][None, :] > cells[:, 0][:, None] + 1e-9) &
                       (qc[:, 0][None, :] < cells[:, 2][:, None] - 1e-9) &
                       (qc[:, 1][None, :] > cells[:, 1][:, None] + 1e-9) &
                       (qc[:, 1][None, :] < cells[:, 3][:, None] - 1e-9)).any()
            if hit:
                n_hit += 1
                worst = (float(th[i]), float(cx[i]), float(cy[i]))
                break
        if worst:
            break
    return n_real_ok, n_legal, n_hit, worst


def boxes_from_row(row, S):
    subs = [row] if 'cx' in row else [row['A'], row['B']]
    out = []
    for sub in subs:
        t0, t1 = F(sub['t'][0]), F(sub['t'][1])
        cl = clip_box(t0, t1, F(sub['cx'][0]), F(sub['cx'][1]),
                      F(sub['cy'][0]), F(sub['cy'][1]), S)
        out.append((float(t0), float(t1)) + tuple(float(v) for v in cl))
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', default=None)
    ap.add_argument('--s', required=True)
    ap.add_argument('--top', type=int, default=40)
    ap.add_argument('--n_real', type=int, default=120)
    ap.add_argument('--n_place', type=int, default=3000)
    a = ap.parse_args()
    S = F(a.s)
    rows = []
    with open(os.path.join('work', a.tag + '.jsonl')) as f:
        for line in f:
            line = line.strip()
            if line:
                r = json.loads(line)
                if r.get('cells'):
                    rows.append(r)
    rows.sort(key=lambda r: -r['dead_lb_float'])
    bad = 0
    for r in rows[:a.top]:
        cells = np.array([[float(F(v)) for v in c] for c in r['cells']])
        boxes = boxes_from_row(r, S)
        nr, nl, nh, w = check(boxes, cells, float(S), a.n_real, a.n_place)
        bad += nh
        print(f"{r['id']:16s} dead={r['dead_lb_float']:.4f} tiles={len(cells)} "
              f"realisations={nr} legal={nl} HITS={nh}" + (f"  {w}" if w else "  OK"),
              flush=True)
    print("TOTAL HITS:", bad)
