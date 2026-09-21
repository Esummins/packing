"""A260 adversary [M] for reading (R): maximise the PIERCE-by-O margin (room259.pierce_O: max over tilts of the largest
|(q-O).u|, |(q-O).v| over the exact centre set, minus 1/2) over the HYBRID family (geom260: 16 coordinates) at a fixed
side.  HARD feasibility: a proposal with hyb_margin < 0 is rejected, never penalised.  A value >= 0 is a free square of
a hybrid ring that MISSES the container centre; it is re-checked by exact SAT (free_margin) before it is reported.
Objectives:  --obj O : pierce_O;   --obj shiftO : pierce_O restricted to starts / moves with a forced open gap
(shift_k >= emin on wall 0) so that the search stays on genuinely locked walls.
    python adv260.py --side shat --adj 1 --restarts 8 --iters 400 --seed 1 [--emin 0.03] [--same 1]
Resumable: rows keyed in results/adv260.jsonl;  logs/STOP stops between restarts."""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom260 as H                                                   # noqa: E402
import room259 as R                                                   # noqa: E402
Z = H.Z


def feas(x, s, adj, emin, same):
    if same and max(abs(x[4 * k + 1] - x[4 * k + 3]) for k in range(4)) > 1e-12:
        return -1.0
    m = H.hyb_margin(x, s, bool(adj))
    if emin > 0:
        m = min(m, H.shift(x[0], x[1], x[2], x[3], s) - emin)
    return m


def start(rng, s, adj, emin, same):
    for _ in range(2000):
        xn = Z.sample_D(rng, s, 1, boxes=True, phimax=32.0)[0]
        x = H.from_normal(xn, s)
        if emin > 0:                                                  # open wall 0 by pulling s1 back
            x[0] -= emin + 1e-4
        if feas(x, s, adj, emin, same) >= 0:
            return x
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--side', default='shat')
    ap.add_argument('--adj', type=int, default=1)
    ap.add_argument('--same', type=int, default=0)
    ap.add_argument('--emin', type=float, default=0.0)
    ap.add_argument('--restarts', type=int, default=8)
    ap.add_argument('--iters', type=int, default=400)
    ap.add_argument('--seed', type=int, default=1)
    a = ap.parse_args()
    s = H.SHAT if a.side == 'shat' else float(a.side)
    out = os.path.join(HERE, '..', 'results', 'adv260.jsonl')
    stop = os.path.join(HERE, '..', 'logs', 'STOP')
    done = {json.loads(l)['key'] for l in open(out)} if os.path.exists(out) else set()
    scale = np.array([1, 2, 1, 2] * 4, float)
    for r in range(a.restarts):
        key = '%s|adj%d|same%d|emin%g|%d|%d' % (a.side, a.adj, a.same, a.emin, a.seed, r)
        if key in done:
            continue
        if os.path.exists(stop):
            return
        t0 = time.time()
        rng = np.random.default_rng(7000 * a.seed + r)
        x = start(rng, s, a.adj, a.emin, a.same)
        if x is None:
            continue
        f = R.pierce_O(None, s, 3.0, H.hyb_verts(x, s))[0]
        sig = 0.02
        for it in range(a.iters):
            d = sig * rng.normal(size=16) * scale
            if a.same:
                for k in range(4):
                    d[4 * k + 3] = d[4 * k + 1]
            y = x + d
            if feas(y, s, a.adj, a.emin, a.same) < 0:
                sig = max(sig * 0.97, 1e-4)
                continue
            g = R.pierce_O(None, s, 3.0, H.hyb_verts(y, s))[0]
            if g >= f:
                x, f, sig = y, g, min(sig * 1.3, 0.08)
            else:
                sig = max(sig * 0.93, 1e-4)
        Vs = H.hyb_verts(x, s)
        w, pose, nc = R.pierce_O(None, s, 0.5, Vs)
        row = {'key': key, 's': s, 'adj': a.adj, 'same': a.same, 'emin': a.emin, 'x': [float(v) for v in x],
               'shift': [H.shift(*x[4 * k:4 * k + 4], s) for k in range(4)],
               'tilts_deg': [[x[4 * k + 1] / Z.DEG, x[4 * k + 3] / Z.DEG] for k in range(4)],
               'hyb_margin': H.hyb_margin(x, s, bool(a.adj)), 'pierceO': w, 'pose': pose,
               'pose_margin': None if pose is None else R.free_margin(pose, Vs, s), 'ncomp': nc,
               'hole_one_slack': -(4 - s) / 2, 'sec': round(time.time() - t0, 1)}
        with open(out, 'a') as fh:
            fh.write(json.dumps(row) + '\n')
        print(key, 'pierceO %+.5f' % w, 'vs %+.5f' % row['hole_one_slack'], 'shift',
              [round(v, 4) for v in row['shift']], 'nc', nc, 'sec', row['sec'], flush=True)


Z.belownormal()
main()
