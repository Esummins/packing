"""A246: SLOT-MET(eta) by interval branch-and-bound (docs/proofs/construct_towards.md s.3).

Claim SLOT-MET (A243, [S]): two interior-disjoint unit squares A, B in the closed quadrant, both
meeting the open corner box (0,1)^2, cannot both avoid the open wall slot (0,1) x (1,2).
Lemma CAP-REDUCTION [T] (the note, s.3.2) puts a counterexample in the form: each square has
exactly its LEFTMOST vertex W = (1 - a, v) strictly left of u = 1, 0 < a <= min(sin th, cos th),
v >= cos th (the lowest vertex above the floor), v cos th + a sin th <= cos th (the cap's top
chord end at or below v = 1), and WLOG v_A >= v_B.  The pose is c = W + ((cos+sin)/2, (sin-cos)/2).
This search certifies: for every such pair with BOTH box depths >= eta the two squares overlap
(SAT depth > 0).  Every discard uses an interval enclosure with the guard GUARD = 1e-9.

    python slotmet246.py --eta 1e-2 [--hmin 1e-4] [--budget-min 240]
resume: the same command (queue checkpoint logs/slotmet_<eta>.npz); stop: touch logs/STOP.
Output: results/slotmet246_<eta>.json  (status CERTIFIED / UNDECIDED / STOPPED, counts, timing).
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import interval246 as IV                      # noqa: E402

G = IV.GUARD
BOX = (0.0, 1.0, 0.0, 1.0)
DIMS = ('thA', 'aA', 'vA', 'thB', 'aB', 'vB')
INIT = np.array([[0.0, np.pi / 2], [0.0, 0.70711], [0.0, 1.0]] * 2)     # (6, 2)


def pose(box, off):
    """(cx, cy, th) intervals of the square parametrised by dims off (th), off+1 (a), off+2 (v)."""
    th = (box[:, 0, off], box[:, 1, off])
    a = (box[:, 0, off + 1], box[:, 1, off + 1])
    v = (box[:, 0, off + 2], box[:, 1, off + 2])
    c, s = IV.cos_i(th), IV.sin_i(th)
    cx = IV.add(IV.sub(IV.I(np.ones_like(a[0])), a), IV.scale(IV.add(c, s), 0.5))
    cy = IV.add(v, IV.scale(IV.sub(s, c), 0.5))
    return (cx, cy, th), (th, a, v, c, s)


def single_alive(par, eta):
    """False where the single-square constraints fail for EVERY parameter of the box."""
    th, a, v, c, s = par
    mn = IV.imin(c, s)
    ok = a[0] <= mn[1] + G                                  # a <= min(sin, cos)
    ok &= v[1] >= c[0] - G                                  # v >= cos
    top = IV.sub(IV.add(IV.mul(v, c), IV.mul(a, s)), c)      # v cos + a sin - cos <= 0
    ok &= top[0] <= G
    return ok


def alive(box, eta):
    pa, parA = pose(box, 0)
    pb, parB = pose(box, 3)
    ok = single_alive(parA, eta) & single_alive(parB, eta)
    ok &= parA[2][1] >= parB[2][0] - G                     # WLOG v_A >= v_B
    dA = IV.depth_rect(pa, BOX)
    dB = IV.depth_rect(pb, BOX)
    ok &= (dA[1] >= eta - G) & (dB[1] >= eta - G)           # both depths >= eta somewhere in the box
    dp = IV.depth_pair(pa, pb)
    ok &= dp[0] <= G                                        # disjoint somewhere in the box
    return ok, dp


def widest(box):
    wd = (box[:, 1, :] - box[:, 0, :]) / (INIT[:, 1] - INIT[:, 0])
    return np.argmax(wd, axis=1), wd.max(axis=1)


def run(eta, hmin, budget_min, batch, log):
    ck = os.path.join(ATT, 'logs', 'slotmet_%g.npz' % eta)
    stop = os.path.join(ATT, 'logs', 'STOP')
    if os.path.exists(ck):
        d = np.load(ck)
        queue, stats = d['queue'], json.loads(str(d['stats']))
        log('resume: %d boxes in the queue, %s' % (len(queue), stats))
    else:
        queue = INIT.T[None, :, :].copy()                   # (1, 2, 6)
        stats = {'processed': 0, 'discarded': 0, 'undecided': 0, 'seconds': 0.0,
                 'min_pair_depth_lo': None, 'undecided_boxes': []}
    t0 = time.time()
    last_ck = t0
    status = 'RUNNING'
    while len(queue):
        if os.path.exists(stop):
            status = 'STOPPED'
            break
        if (time.time() - t0) / 60.0 > budget_min:
            status = 'BUDGET'
            break
        cur, queue = queue[-batch:], queue[:-batch]
        ok, dp = alive(cur, eta)
        stats['processed'] += len(cur)
        stats['discarded'] += int((~ok).sum())
        cur = cur[ok]
        if len(cur):
            k, wd = widest(cur)
            small = wd < hmin
            if small.any():
                stats['undecided'] += int(small.sum())
                for b in cur[small][:20]:
                    if len(stats['undecided_boxes']) < 200:
                        stats['undecided_boxes'].append(b.tolist())
                lo = float(dp[0][ok][small].min())
                stats['min_pair_depth_lo'] = lo if stats['min_pair_depth_lo'] is None else min(lo, stats['min_pair_depth_lo'])
            big = cur[~small]
            if len(big):
                kk = k[~small]
                parts = []
                for kd in np.unique(kk):
                    parts.append(IV.box_split(big[kk == kd], int(kd)))
                queue = np.concatenate([queue] + parts) if len(queue) else np.concatenate(parts)
        if time.time() - last_ck > 60:
            stats['seconds'] += time.time() - t0
            t0 = time.time()
            np.savez(ck, queue=queue, stats=json.dumps(stats))
            last_ck = time.time()
            log('  processed %d, queue %d, discarded %d, undecided %d, %.0f s' % (
                stats['processed'], len(queue), stats['discarded'], stats['undecided'], stats['seconds']))
    stats['seconds'] += time.time() - t0
    if status == 'RUNNING':
        status = 'CERTIFIED' if stats['undecided'] == 0 else 'UNDECIDED'
        if os.path.exists(ck):
            os.remove(ck)
    else:
        np.savez(ck, queue=queue, stats=json.dumps(stats))
    stats.update(status=status, eta=eta, hmin=hmin, guard=G, queue_left=int(len(queue)))
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--eta', type=float, default=1e-2)
    ap.add_argument('--hmin', type=float, default=1e-4, help='relative box width below which a box is UNDECIDED')
    ap.add_argument('--budget-min', type=float, default=240.0)
    ap.add_argument('--batch', type=int, default=20000)
    a = ap.parse_args()
    try:
        sys.path.insert(0, os.path.join(ATT, '..', 'A244-twelve-stuck', 'code'))
        from search244 import belownormal
        belownormal()
    except Exception:
        pass
    os.makedirs(os.path.join(ATT, 'logs'), exist_ok=True)
    os.makedirs(os.path.join(ATT, 'results'), exist_ok=True)
    lf = open(os.path.join(ATT, 'logs', 'slotmet_%g.log' % a.eta), 'a')

    def log(t):
        lf.write(time.strftime('%H:%M:%S ') + t + '\n')
        lf.flush()
        print(t, flush=True)

    log('SLOT-MET(eta = %g) interval B&B, hmin %g, budget %.0f min' % (a.eta, a.hmin, a.budget_min))
    st = run(a.eta, a.hmin, a.budget_min, a.batch, log)
    log('%s: processed %d, discarded %d, undecided %d, queue left %d, %.0f s' % (
        st['status'], st['processed'], st['discarded'], st['undecided'], st['queue_left'], st['seconds']))
    with open(os.path.join(ATT, 'results', 'slotmet246_%g.json' % a.eta), 'w') as f:
        json.dump(st, f, indent=1)


if __name__ == '__main__':
    main()
