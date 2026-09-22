"""A265 re-run of A263's OPEN P2 cells (2,4 / 2,5 / 3,4 / 3,5 / 3,6) with two SOUND strengthenings of the box test,
cert263.check_box wrapped (never edited; its module globals SMAX / PLUG_A / RHO_PLUG are set per box and restored):
 (1) ADJ-CONSISTENT SIDE.  A263 checks every box at SMAX = 3.8771 but imposes ADJ (W and S' reach their far slots,
     b + w(fW) >= s - 2, a' + w(f1') >= s - 2) only at SMIN = 3.82.  The all-ADJ ring of a box exists only for
     s <= s_eff := min(SMAX, hi_b + w(hi_fW) + 2, hi_a' + w(hi_f1') + 2); the corner-frame monotonicity
     (open_pairs.md s.2.2, Lean corner_frame_mono / clip_mono) makes the certificate at s_eff valid for every s <= s_eff,
     which is every side at which a parameter of the box is in the family.  A263's OPEN leaves are exactly the boxes
     whose ring is ADJ only near 3.82 while P2 is FALSE at 3.8771 (strip_plug.md s.2: exact margin +0.020 at 3.8771,
     -0.061 at 3.82 on the worst leaf).
 (2) GRADED PLUG (locked_wall.md s.4, Lemma PLUG: a' in (0.354 + rho, 1) => no free square meets [0, rho]^2 at the
     corner): rho = 1/4 for lo_a' > 0.604 (A263's), 1/8 for lo_a' > 0.48, 1/16 for lo_a' > 0.417.
    python cert265.py --cells 2,4;2,5;3,4;3,5;3,6 [--maxdepth 26]  ->  certs/P2265_cell_i_j.jsonl + P2265_index.jsonl"""
import argparse
import json
import os
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A263-open-pairs', 'code'))
import cert263 as C                                                   # noqa: E402

K = C.K
SMAX, SMIN = K.SMAX, K.SMIN
PLUGS = ((0.604, 0.25), (0.48, 0.125), (0.417, 0.0625))               # (least a' of the box, rho): a' > 0.3536 + rho
CELLS = ['2,4', '2,5', '3,4', '3,5', '3,6']


def s_eff(hi):
    return min(SMAX, hi[0] + K.w_of(hi[1]) + 2.0, hi[2] + K.w_of(hi[3]) + 2.0)


def plug_of(lo):
    for a_min, rho in PLUGS:
        if lo[2] > a_min:
            return a_min, rho
    return 9.0, 0.0


def check_box(lo, hi, bins=K.BINS):
    """cert263.check_box('P2', ...) at the ADJ-consistent side with the graded plug; returns (status, margin, s_used)."""
    lo, hi = np.array(lo, float), np.array(hi, float)
    if C.outside_domain('P2', lo, hi, True):
        return 'PRUNE', None, SMAX
    s = s_eff(hi)
    if s < SMIN:
        return 'PRUNE', None, s
    a_min, rho = plug_of(lo)
    saved = (C.SMAX, C.PLUG_A, C.RHO_PLUG)
    C.SMAX, C.PLUG_A, C.RHO_PLUG = s, a_min, rho
    try:
        st, m = C.check_box('P2', lo, hi, bins, adj=True)
    finally:
        C.SMAX, C.PLUG_A, C.RHO_PLUG = saved
    return st, m, s


def tree(lo, hi, depth, maxdepth, out, stats):
    st, m, s = check_box(lo, hi)
    stats[st] = stats.get(st, 0) + 1
    row = {'lo': list(map(float, lo)), 'hi': list(map(float, hi)), 'st': st, 'm': m, 's': round(float(s), 6)}
    if st != 'FAIL':
        out.append(row)
        return True
    if depth >= maxdepth:
        row['st'] = 'OPEN'
        out.append(row)
        return False
    k = int(((np.array(hi) - np.array(lo)) * C.WEIGHT['P2']).argmax())
    mid = 0.5 * (lo[k] + hi[k])
    ok = True
    for a, b in ((lo[k], mid), (mid, hi[k])):
        l2, h2 = list(lo), list(hi)
        l2[k], h2[k] = a, b
        ok = tree(l2, h2, depth + 1, maxdepth, out, stats) and ok
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cells', default=';'.join(CELLS))
    ap.add_argument('--maxdepth', type=int, default=26)
    a = ap.parse_args()
    C.Z.belownormal()
    certs = os.path.join(HERE, '..', 'certs')
    os.makedirs(certs, exist_ok=True)
    stop = os.path.join(HERE, '..', 'logs', 'STOP')
    idx = os.path.join(certs, 'P2265_index.jsonl')
    done = {json.loads(l)['cell'] for l in open(idx)} if os.path.exists(idx) else set()
    for cell in a.cells.split(';'):
        if cell in done or os.path.exists(stop):
            continue
        i, j = map(int, cell.split(','))
        t0, out, stats = time.time(), [], {}
        lo, hi = C.root('P2', i, j, 5.0)
        ok = tree(lo, hi, 0, a.maxdepth, out, stats)
        with open(os.path.join(certs, 'P2265_cell_%d_%d.jsonl' % (i, j)), 'w') as fh:
            for row in out:
                fh.write(json.dumps(row) + '\n')
        rec = {'cell': cell, 'ok': ok, 'stats': stats, 'leaves': len(out), 'sec': round(time.time() - t0, 1),
               'plug': [list(p) for p in PLUGS], 's_rule': 'min(SMAX, hi_b+w(hi_fW)+2, hi_a+w(hi_f1)+2)'}
        with open(idx, 'a') as fh:
            fh.write(json.dumps(rec) + '\n')
        print('P2265', cell, ok, stats, round(time.time() - t0, 1), flush=True)


if __name__ == '__main__':
    main()
