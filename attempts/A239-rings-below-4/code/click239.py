"""A239 Panel E: the CLICK / SWAP of one corner on A226's S = 3.90 crowd ring (A231's improvement).  The ring's
pocket holds ONE square (A222's placer), so the object is the 9-square packing ring + interior square.  Steps:
(1) CORNER-SWAP at BL (ring_swap.md s.2.1): the two meeters out, the slot square in, the leftover re-placed by the
region search (Lemma SWAP: same side); (2) the SHRINK (realign.md s.2.1): the fixed-tilt side LP of Lemma GRAIN-LP
with the slot pinned, axes re-selected (A231 geomn231.fixed_tilt_min, variant B); (3) the anchored move: the
remaining tilted squares rotate to alignment in 20 steps, the LP at every step (the side it reaches); and, for
comparison, the plain click of the unswapped ring.  Every step timed.
    python click239.py   -> results/click239.jsonl
"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A231-realign', 'code'))
import geom239 as GM                                                       # noqa: E402
import geomn231 as GN                                                      # noqa: E402
import region222 as RG                                                     # noqa: E402
import band236 as BD                                                       # noqa: E402

GM.set_priority()
ATT = os.path.abspath(os.path.join(HERE, '..'))
OUT = os.path.join(ATT, 'results', 'click239.jsonl')
STEPS = 20


def shrink(poses, S, pins, fixed=None):
    th = np.array([p[2] for p in poses])
    P, s, sel, k = GN.fixed_tilt_min(poses, th, fixed, pins, iters=12)
    return P, s, k


def anchored_move(poses, S, pins, steps=STEPS):
    """rotate every tilted square toward its alignment (tilts scaled to 0; the sense is the tilt's own sign), the
    side LP (free axes) at every step from the previous centres; returns the side sequence and the final poses."""
    th0 = np.array([p[2] for p in poses])
    cur, seq = list(poses), []
    for k in range(steps + 1):
        t = k / steps
        th = th0 * (1.0 - t)
        P, s, sel, _ = GN.fixed_tilt_min(cur, th, None, pins, iters=12)
        if P is None:
            seq.append(None)
            break
        cur = P
        seq.append(float(s))
    return seq, cur


def corner_swap(poses, S, corner='BL'):
    """the two meeters of `corner` out, the slot square in, the leftover placed by A222's greedy placer."""
    ms = BD.meeters(poses, S, corner)
    keep = [p for i, p in enumerate(poses) if i not in ms]
    ax, bx, ay, by = GN.slot_pin(corner)
    slot = (ax + bx * S, ay + by * S, 0.0)
    fixed = keep + [slot]
    got = RG.greedy(fixed, S, len(ms) - 1, GM.thetas(5.0), 3)
    if got is None:
        got = RG.greedy(fixed, S, len(ms) - 1, GM.thetas(1.0), 3)
    if got is None:
        return None, ms
    return fixed + got, ms


def main():
    t0 = time.time()
    S = 3.90
    ring = GM.ring226(S, 0.02)
    cap, inner = GM.capacity(ring, S, 3)
    P9 = ring + inner
    ok, gap, wall = BD.check_packing(P9, S)
    row = {'S': S, 'ring': [list(p) for p in ring], 'interior': [list(p) for p in inner], 'capacity': cap,
           'packing_ok': bool(ok), 'gap': float(gap), 'wall': float(wall), 'times': {'build': time.time() - t0}}
    print('ring + %d interior square(s): packing %s gap %.1e' % (cap, ok, gap), flush=True)
    # (1) the swap at every corner
    swaps = {}
    for cn in GM.CORNERS:
        t1 = time.time()
        P, ms = corner_swap(P9, S, cn)
        if P is None:
            swaps[cn] = {'ok': False, 'meeters': ms, 'secs': time.time() - t1}
            print(cn, 'swap: no room for the leftover', flush=True)
            continue
        ok2, g2, w2 = BD.check_packing(P, S)
        pins = {len(P) - 2: cn}                       # the slot square is the last of `fixed`, before the leftover
        t2 = time.time()
        P0, s0, k = shrink(P, S, pins)
        t3 = time.time()
        seq, Pend = anchored_move(P0 if P0 is not None else P, S, pins)
        t4 = time.time()
        swaps[cn] = {'ok': True, 'meeters': ms, 'swapped': [list(p) for p in P], 'swap_check': [bool(ok2), float(g2), float(w2)],
                     'shrink_side': s0, 'shrink_poses': [list(p) for p in P0] if P0 else None, 'lp_iters': k,
                     'move_sides': seq, 'move_end': [list(p) for p in Pend], 'move_end_side': seq[-1] if seq else None,
                     'secs': {'swap': t2 - t1, 'shrink': t3 - t2, 'move': t4 - t3}}
        print('%s swap ok (gap %.1e) -> shrink %.4f (%d LP rounds, %.1fs) -> anchored move to flush: %s (%.1fs)' % (
            cn, g2, s0 if s0 else float('nan'), k, t3 - t2, ['%.3f' % v if v else 'blocked' for v in seq[::5]], t4 - t3), flush=True)
    row['swaps'] = swaps
    # the plain click of the 9-square and the 8-square ring (no swap, no pin)
    for lab, P in (('click9', P9), ('click8', ring)):
        t1 = time.time()
        seq, Pend = anchored_move(P, S, {})
        row[lab] = {'sides': seq, 'end': [list(p) for p in Pend], 'secs': time.time() - t1}
        print(lab, 'sides', ['%.3f' % v if v else 'blocked' for v in seq[::5]], flush=True)
    row['times']['total'] = time.time() - t0
    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write(json.dumps(row) + '\n')
    print('wrote', OUT, 'in %.1f s' % (time.time() - t0))


if __name__ == '__main__':
    main()
