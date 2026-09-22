"""A265 exact region search on A263's OPEN P2 leaves (cells 2,4 / 2,5 / 3,4 / 3,5 / 3,6): for a sample of leaves
(the 40 largest box margins + 60 random per cell) the EXACT P2 margin (geo263.factor_margin, exact centre sets,
0.25-degree grid) at the leaf's midpoint, (a) at SMAX = 3.8771 where A263 tested it, (b) at the ADJ-consistent side
s_eff of cert265 -- and for the worst real miss at SMAX, the FULL corner (s1, W, S', W') over a grid of shifts
(e, e') and W'-tilts inside the non-ADJ domain: does any 4-square corner leave the missing square free?
    python miss265.py -> results/miss265.json"""
import json
import os
import random
import sys

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cert265 as M                                                   # noqa: E402
G = M.C.G
A263 = os.path.join(HERE, '..', '..', 'A263-open-pairs', 'certs')


def leaf_margins(r):
    mid = 0.5 * (np.array(r['lo']) + np.array(r['hi']))
    f, g = (mid[0], mid[1], 0.0, mid[1]), (mid[2], mid[3], 0.0, mid[3])
    s_e = M.s_eff(np.array(r['hi']))
    m1, p1 = G.factor_margin('P2', M.SMAX, f, g, step=0.25)
    m2, p2 = G.factor_margin('P2', s_e, f, g, step=0.25)
    return dict(mid=list(map(float, mid)), box_m=r['m'], s_eff=float(s_e), exact_smax=float(m1), pose_smax=p1,
                exact_seff=float(m2), pose_seff=p2)


def full_scan(mid, s):
    """FULL corner margin over (e, e', fW') with s1's tilt = fW and W' at tilt fW' in the non-ADJ domain."""
    best = (-9.0, None)
    for e in np.linspace(0.0, 1.2, 13):
        f = (mid[0], mid[1], float(e), mid[1])
        if G.floor_dom(f, s, adj=False) < 0:
            continue
        for e1 in np.linspace(0.0, 1.2, 13):
            for fw in np.arange(2.0, 45.0, 4.0) * G.DEG:
                g = (mid[2], mid[3], float(e1), float(fw))
                if G.right_dom(g, s, adj=False) < 0:
                    continue
                m, pose = G.factor_margin('FULL', s, f, g, step=1.0)
                if m > best[0]:
                    best = (float(m), dict(e=float(e), e1=float(e1), fW1=float(fw), pose=pose))
    return best


def main():
    random.seed(2)
    out, worst = {}, (-9.0, None)
    for cell in M.CELLS:
        i, j = cell.split(',')
        rows = [json.loads(l) for l in open(os.path.join(A263, 'P2263_cell_%s_%s.jsonl' % (i, j)))]
        op = sorted([r for r in rows if r['st'] == 'OPEN'], key=lambda r: -r['m'])
        pick = op[:40] + random.sample(op[40:], min(60, max(0, len(op) - 40)))
        recs = [leaf_margins(r) for r in pick]
        ex = np.array([q['exact_smax'] for q in recs])
        ef = np.array([q['exact_seff'] for q in recs])
        out[cell] = dict(n_open=len(op), n_sampled=len(recs), exact_smax_max=float(ex.max()),
                         exact_smax_pos=int((ex > 0).sum()), exact_seff_max=float(ef.max()),
                         exact_seff_pos=int((ef > 0).sum()), rows=recs)
        k = int(ex.argmax())
        if ex[k] > worst[0]:
            worst = (float(ex[k]), dict(cell=cell, **recs[k]))
        print(cell, len(op), 'exact@SMAX max', round(float(ex.max()), 4), 'pos', int((ex > 0).sum()),
              '| exact@s_eff max', round(float(ef.max()), 4), 'pos', int((ef > 0).sum()), flush=True)
    full = full_scan(np.array(worst[1]['mid']), M.SMAX) if worst[1] else None
    print('worst real P2 miss at SMAX', worst, 'FULL corner scan', full, flush=True)
    json.dump(dict(cells=out, worst=worst, full_scan=full),
              open(os.path.join(HERE, '..', 'results', 'miss265.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
