"""A259 adversary: maximise the PIERCE-by-O margin  max_theta G(theta) - 1/2  over the normal-ring domain D at a fixed
side (HARD feasibility: a proposal outside D is rejected, never penalised).  A positive value = a free square that
misses the container centre: then the witness is re-checked by exact SAT and a second / third square is looked for.
(1+1)-ES with step adaptation, coarse tilt grid while searching, 0.5-degree grid for the reported value.
    python adv259.py --side shat --restarts 6 --iters 250 --seed 1 [--boxes 0] [--phimax 45]
Resumable: rows keyed (side, boxes, seed, restart) in results/adv259.jsonl; logs/STOP stops between restarts."""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom259 as Z                                                   # noqa: E402
import room259 as R                                                   # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--side', default='shat')
    ap.add_argument('--restarts', type=int, default=6)
    ap.add_argument('--iters', type=int, default=250)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--boxes', type=int, default=1)
    ap.add_argument('--phimax', type=float, default=45.0)
    ap.add_argument('--out', default=os.path.join(HERE, '..', 'results', 'adv259.jsonl'))
    a = ap.parse_args()
    s = Z.SHAT if a.side == 'shat' else float(a.side)
    stop = os.path.join(HERE, '..', 'logs', 'STOP')
    done = set()
    if os.path.exists(a.out):
        done = {json.loads(l)['key'] for l in open(a.out) if l.strip()}
    for r in range(a.restarts):
        key = '%s|%d|%d|%g|%d' % (a.side, a.boxes, a.seed, a.phimax, r)
        if key in done:
            continue
        if os.path.exists(stop):
            return
        t0 = time.time()
        rng = np.random.default_rng(1000 * a.seed + r)
        x = Z.sample_D(rng, s, 1, boxes=bool(a.boxes), phimax=a.phimax)[0]
        f = R.pierce_O(x, s, 3.0)[0]
        sig = 0.03
        for it in range(a.iters):
            y = x + sig * rng.normal(size=8) * np.array([1, 1, 1, 1, 2, 2, 2, 2.0])
            if Z.ring_margin(y, s, bool(a.boxes)) < 0:
                sig = max(sig * 0.97, 1e-4)
                continue
            g = R.pierce_O(y, s, 3.0)[0]
            if g >= f:
                x, f, sig = y, g, min(sig * 1.3, 0.1)
            else:
                sig = max(sig * 0.93, 1e-4)
        Vs = Z.ring_verts(x, s)
        w, pose, nc = R.pierce_O(x, s, 0.5, Vs)
        row = {'key': key, 's': s, 'boxes': a.boxes, 'x': [float(v) for v in x],
               'phi_deg': [float(v / Z.DEG) for v in x[4:]], 'ring_margin': Z.ring_margin(x, s, bool(a.boxes)),
               'pierceO': w, 'pose': pose, 'pose_margin': None if pose is None else R.free_margin(pose, Vs, s),
               'ncomp': nc, 'hole_one_slack': -(4 - s) / 2, 'sec': round(time.time() - t0, 1)}
        with open(a.out, 'a') as fh:
            fh.write(json.dumps(row) + '\n')
        print(key, 'pierceO %+.5f' % w, 'phi', [round(v, 2) for v in row['phi_deg']],
              'd', [round(float(v), 4) for v in x[:4]], 'nc', nc, flush=True)


Z.belownormal()
main()
