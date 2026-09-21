"""A262 task 2 [M]: rings with j = 1..4 JAM corners -- do they exist, and what is the ROOM of their pocket?

jam sets: (3,) one JAM corner;  (3,1) two OPPOSITE;  (3,0) two ADJACENT;  (3,0,1) three;  (0,1,2,3) four.
Stage 1 (exist): Nelder-Mead x 2 on t = multi262.objective (HARD terms + the jam sup J of every JAM corner) from
    A261's witness triples copied into every JAM corner (+ seeded perturbations).  t > 0 <=> a j-JAM ring (8 squares).
Stage 2 (room adversary): (1+1)-ES maximising the PIERCE margin (room259: max over free squares of the miss of O,
    3-degree grid while searching, 1 degree for the reported value) with every proposal REJECTED unless t >= 0.
    pierce < 0: every free square contains O (room <= 1);  pierce = -1.5: NO free square at all (room 0).
Per reported ring: capacity259.best_set (disjoint free squares, exact SAT) and the 12-cell all-families test.
    python adv262.py [--seeds 4] [--es 1500]    -> results/adv262.jsonl   (resumable by key; logs/STOP)
"""
import argparse
import json
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize

sys.dont_write_bytecode = True
os.environ.setdefault('JAM_COARSE', '1')
HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import multi262 as M                                                  # noqa: E402
import ring262 as RR                                                  # noqa: E402
import fam262 as F                                                    # noqa: E402
import room259 as R                                                   # noqa: E402
import capacity259 as CAP                                             # noqa: E402
Z = M.Z
OUT = os.path.join(ATT, 'results', 'adv262.jsonl')
STOP = os.path.join(ATT, 'logs', 'STOP')
JAMS = [(3,), (3, 1), (3, 0), (3, 0, 1), (0, 1, 2, 3)]
SIDES = [Z.SHAT, 3.82, 3.95, 3.99]


def pierce(p, s, jam, step):
    Vs = M.verts(p, s, jam)[0]
    return R.pierce_O(None, s, step, Vs=Vs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seeds', type=int, default=4)
    ap.add_argument('--es', type=int, default=1500)
    ap.add_argument('--iters', type=int, default=2000)
    a = ap.parse_args()
    Z.belownormal()
    done = {json.loads(l)['key'] for l in open(OUT)} if os.path.exists(OUT) else set()
    for jam in JAMS:
        for s in SIDES:
            for wi, (name, pA, pC, pX) in enumerate(RR.witnesses()):
                for seed in range(a.seeds):
                    key = '%s|%.6f|W%d|%d' % (''.join(map(str, jam)), s, wi, seed)
                    if key in done:
                        continue
                    if os.path.exists(STOP):
                        return
                    t0 = time.time()
                    rng = np.random.default_rng(262000 + 97 * seed + wi)
                    p0 = M.start_from_witness(pA, pC, pX, s, jam)
                    if seed:
                        p0 = p0 + rng.normal(size=len(p0)) * 0.01 * seed
                    f = lambda p: -M.objective(p, s, jam)
                    opt = dict(maxiter=a.iters, xatol=1e-7, fatol=1e-9, adaptive=True)
                    r = minimize(f, p0, method='Nelder-Mead', options=opt)
                    r = minimize(f, r.x, method='Nelder-Mead', options=opt)
                    p, t = r.x, -r.fun
                    row = dict(key=key, jam=list(jam), s=s, t=float(t), p=[float(v) for v in p])
                    if t > 1e-6:
                        row['pierce_at_maxt'] = float(pierce(p, s, jam, 1.0)[0])
                        x, fx, sig = p.copy(), pierce(p, s, jam, 3.0)[0], 0.01
                        for _ in range(a.es):
                            y = x + sig * rng.normal(size=len(x))
                            if M.objective(y, s, jam) < 0:
                                sig = max(sig * 0.97, 1e-5)
                                continue
                            g = pierce(y, s, jam, 3.0)[0]
                            if g >= fx:
                                x, fx, sig = y, g, min(sig * 1.3, 0.05)
                            else:
                                sig = max(sig * 0.93, 1e-5)
                        Vs = M.verts(x, s, jam)[0]
                        pm, pose, nc = R.pierce_O(None, s, 1.0, Vs=Vs)
                        W, _ = CAP.best_set(Vs, s, kmax=3)
                        rep = F.report(Vs + [Z.sq_verts(*w) for w in W], s)
                        row.update(adv_p=[float(v) for v in x], adv_t=float(M.objective(x, s, jam)), pierce=float(pm),
                                   pierce_pose=pose, comps=nc, capacity_lb=len(W), free=[list(map(float, w)) for w in W],
                                   n_squares=8 + len(W), family_stuck=rep['family_stuck'], min_excess=rep['min_excess'],
                                   hole_one_slack=-(4 - s) / 2)
                        if pose is not None:
                            row['pierce_pose_free_margin'] = float(R.free_margin(pose, Vs, s))
                    row['seconds'] = round(time.time() - t0, 1)
                    with open(OUT, 'a') as fh:
                        fh.write(json.dumps(row) + '\n')
                    print(key, 't=%.5f' % t, 'pierce=%s cap=%s' % (row.get('pierce'), row.get('capacity_lb')),
                          row['seconds'], 's', flush=True)


if __name__ == '__main__':
    main()
