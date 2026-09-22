"""A262 certificate trees (cert262 kernels).  Resumable per root cell (certs/<fam>262_index.jsonl); logs/STOP stops after
the current cell; --budget seconds stops the run (the cell in progress is NOT written: it restarts next time).
    --fam pair3 : root cells 9 x 9 in (phi, phi') of 5 deg, b, a' in [0, 1]                       (4 coordinates)
    --fam jam   : root cells 9 x 9 in (alpha, phiX) of 5 deg; d0 in [0,1], yX in [0.29, 2.88], cx, cy in [0.5, 1.71],
                  th in [0, 90 deg)                                                              (7 coordinates)
Leaves: CERT / PRUNE / OPEN (depth limit).  Adaptive bisection on the weighted widest coordinate.
    python tree262.py --fam pair3 [--only i,j] [--budget 36000] [--maxdepth 30]"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import cert262 as K2                                                  # noqa: E402
Z = K2.Z
DEG = Z.DEG
WEIGHT = {'pair3': np.array([1.0, 2.0, 1.0, 2.0]), 'jam': np.array([1.0, 2.0, 1.0, 2.0, 1.0, 1.0, 2.0])}
CHECK = {'pair3': K2.check_box_pair3, 'jam': K2.check_box}


def root(fam, i, j, step=5.0):
    if fam == 'pair3':
        return ([0.0, i * step * DEG, 0.0, j * step * DEG], [1.0, (i + 1) * step * DEG, 1.0, (j + 1) * step * DEG])
    return ([0.0, i * step * DEG, 1.0 - math.cos((j + 1) * step * DEG), j * step * DEG, 0.5, 0.5, 0.0],
            [1.0, (i + 1) * step * DEG, K2.SMAX - 1.0, (j + 1) * step * DEG, 0.5 + 0.5 * math.sqrt(2),
             0.5 + 0.5 * math.sqrt(2), math.pi / 2])


def tree(fam, lo, hi, depth, maxdepth, out, stats, deadline):
    if deadline and time.time() > deadline:
        raise TimeoutError
    st, m = CHECK[fam](lo, hi)
    stats[st] = stats.get(st, 0) + 1
    if st != 'FAIL':
        out.append({'lo': list(map(float, lo)), 'hi': list(map(float, hi)), 'st': st, 'm': m})
        return True
    if depth >= maxdepth:
        out.append({'lo': list(map(float, lo)), 'hi': list(map(float, hi)), 'st': 'OPEN', 'm': m})
        return False
    k = int(((np.array(hi) - np.array(lo)) * WEIGHT[fam]).argmax())
    mid = 0.5 * (lo[k] + hi[k])
    ok = True
    for a, b in ((lo[k], mid), (mid, hi[k])):
        l2, h2 = list(lo), list(hi)
        l2[k], h2[k] = a, b
        ok = tree(fam, l2, h2, depth + 1, maxdepth, out, stats, deadline) and ok
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fam', default='pair3')
    ap.add_argument('--cells', type=int, default=9)
    ap.add_argument('--maxdepth', type=int, default=30)
    ap.add_argument('--only', default='')
    ap.add_argument('--budget', type=float, default=0.0)
    ap.add_argument('--order', default='centre')
    ap.add_argument('--sub', type=int, default=0, help='split every root cell into 2^sub jobs (the first sub bisections)')
    a = ap.parse_args()
    Z.belownormal()
    certs = os.path.join(ATT, 'certs')
    os.makedirs(certs, exist_ok=True)
    stop = os.path.join(ATT, 'logs', 'STOP')
    idx = os.path.join(certs, '%s262_index.jsonl' % a.fam)
    done = {json.loads(l)['cell'] for l in open(idx)} if os.path.exists(idx) else set()
    step = 45.0 / a.cells
    deadline = time.time() + a.budget if a.budget else None
    cells = [(i, j) for i in range(a.cells) for j in range(a.cells)]
    if a.order == 'centre':                                            # the witness tilts (14-18 | 18-28 deg) first
        cells.sort(key=lambda c: abs(c[0] - 3) + abs(c[1] - 4))
    for i, j in cells:
        if a.only and a.only != '%d,%d' % (i, j):
            continue
        for q, (lo, hi) in enumerate(subcells(a.fam, root(a.fam, i, j, step), a.sub)):
            cell = '%d,%d' % (i, j) + (',%d' % q if a.sub else '')
            if cell in done:
                continue
            if os.path.exists(stop):
                return
            if not job(a, i, j, q, cell, lo, hi, certs, idx, deadline):
                return


def subcells(fam, box, sub):
    boxes = [box]
    for _ in range(sub):
        nxt = []
        for lo, hi in boxes:
            k = int(((np.array(hi) - np.array(lo)) * WEIGHT[fam]).argmax())
            mid = 0.5 * (lo[k] + hi[k])
            for x, y in ((lo[k], mid), (mid, hi[k])):
                l2, h2 = list(lo), list(hi)
                l2[k], h2[k] = x, y
                nxt.append((l2, h2))
        boxes = nxt
    return boxes


def job(a, i, j, q, cell, lo, hi, certs, idx, deadline):
    t0, out, stats = time.time(), [], {}
    try:
        ok = tree(a.fam, lo, hi, 0, a.maxdepth, out, stats, deadline)
    except TimeoutError:
        print(a.fam, cell, 'BUDGET reached: cell not written', stats, round(time.time() - t0, 1), flush=True)
        return False
    with open(os.path.join(certs, '%s262_cell_%s.jsonl' % (a.fam, cell.replace(',', '_'))), 'w') as fh:
        for row in out:
            fh.write(json.dumps(row) + '\n')
    with open(idx, 'a') as fh:
        fh.write(json.dumps({'cell': cell, 'ok': ok, 'stats': stats, 'leaves': len(out), 'sub': a.sub,
                             'sec': round(time.time() - t0, 1)}) + '\n')
    print(a.fam, cell, ok, stats, round(time.time() - t0, 1), flush=True)
    return True


if __name__ == '__main__':
    main()
