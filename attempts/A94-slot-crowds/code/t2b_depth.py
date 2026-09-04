"""A89 / T2 ADDENDUM add-on: INTRUSION DEPTH of corner blockers.

  depth(Q) := 1 - inf { max(p_x, p_y) : p in int(Q) cap (0,1)^2 }   (corner frame)
            = 1 - f_min_max(Q)   whenever f_min_max(Q) < 1
  (f_min_max = min over Q of max(x, y), corner85.f_min_max; the identity holds
   because the infimum over the intersection is attained where max(x,y) is
   minimal over Q, and that value is < 1 exactly when Q meets the open slot.)
  Sanity: axis-aligned [a,a+1] x [b,b+1] -> depth = 1 - max(a, b);
  a 45-deg diamond with lowest vertex (v_x, v_y) in the slot -> 1 - max(v_x, v_y);
  the slot square itself -> depth 1.

  DEPTH(corner) := max over that corner's blockers.

(1) 644 sound BL cover boxes: SOUND max of depth over each box.
    f_min_max is nondecreasing in c_x and in c_y separately (max(c+q) is
    pointwise nondecreasing, hence so is its min over q), so the minimum over
    the centre box is at (x0, y0) EXACTLY -- no slack needed in x, y.  In theta
    it is scanned on a fine grid and slacked outward by the Lipschitz constant
    sqrt(2)/2 per radian times half the grid spacing.  So
        depth_ub(box) = 1 - min_th f_min_max(x0, y0, th) + slack.
(2) depth added to every blocker row already emitted (A87 167 points, atlas,
    Trump), with per-corner DEPTH distributions.
(3) A87 corners with DEPTH < 0.3: how many of their blockers are axis-aligned.

Usage: python t2b_depth.py
"""
from __future__ import annotations

import os
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ.setdefault(_v, '1')

import json
import math
import re
import sys
import time
from decimal import Decimal, getcontext

import numpy as np

import a89lib as L
import t2b_reach as TB

OUT = os.path.join(L.RESULTS, 't2b_depth.json')
DELTAS = (0.05, 0.1, 0.2, 0.3, 0.5)
DEPTH_BINS = [('<0 (box cannot reach the slot)', -1e9, 0.0),
              ('[0,0.05)', 0.0, 0.05), ('[0.05,0.1)', 0.05, 0.1),
              ('[0.1,0.2)', 0.1, 0.2), ('[0.2,0.3)', 0.2, 0.3),
              ('[0.3,0.5)', 0.3, 0.5), ('[0.5,1)', 0.5, 1.0 - 1e-12),
              ('>=1 (slot square attainable)', 1.0 - 1e-12, 1e9)]
NTH = 2001                   # theta scan per box
LIP = math.sqrt(2.0) / 2.0   # |d f_min_max / d theta| <= circumradius


def dbin(v):
    for nm, a, b in DEPTH_BINS:
        if a <= v < b:
            return nm
    return DEPTH_BINS[-1][0]


def empty_dbins():
    return {nm: 0 for nm, _, _ in DEPTH_BINS}


# ------------------------------------------------------------------- (1) boxes
def box_depth_ub(b):
    th = np.linspace(math.radians(b.th0), math.radians(b.th1), NTH)
    cx = np.full(NTH, b.x0)
    cy = np.full(NTH, b.y0)
    f = TB.f_minmax_np(TB.verts_np(cx, cy, th))
    slack = LIP * (th[1] - th[0]) / 2.0 if NTH > 1 else 0.0
    return 1.0 - (float(f.min()) - slack), float(f.min()), slack


def part1():
    R, V, rows, boxes = TB.load_boxes()
    pairs = TB.stream_pairs(os.path.join(TB.RES85, 'a85_pairs_BL.json'))
    ub, fmin, slack = [], [], None
    for b in boxes:
        d, fm, sl = box_depth_ub(b)
        ub.append(d)
        fmin.append(fm)
        slack = sl
    ub = np.array(ub)
    out = {'n_sound_boxes': len(boxes), 'n_pairs': len(pairs),
           'theta_scan_points': NTH, 'lipschitz_slack_deg_equiv': slack,
           'method': 'depth_ub(box) = 1 - min_theta f_min_max(x0, y0, theta) '
                     '+ Lipschitz slack; exact in (c_x, c_y) by monotonicity',
           'depth_ub': {'max': float(ub.max()), 'min': float(ub.min()),
                        'mean': float(ub.mean())},
           'depth_ub_hist': {nm: int(((ub >= a) & (ub < b)).sum())
                             for nm, a, b in DEPTH_BINS},
           'per_delta': {}}
    for dl in DELTAS:
        deep = np.where(ub >= dl)[0]
        ds = set(int(k) for k in deep)
        one = sum(1 for (i, j, _si, _sj) in pairs if i in ds or j in ds)
        both = sum(1 for (i, j, _si, _sj) in pairs if i in ds and j in ds)
        out['per_delta']['%g' % dl] = {
            'n_deep_capable_boxes': len(deep),
            'frac_deep_capable_boxes': len(deep) / len(boxes),
            'n_pairs_with_a_deep_capable_member': one,
            'frac_pairs_with_a_deep_capable_member': one / len(pairs),
            'n_pairs_with_both_deep_capable': both,
            'frac_pairs_with_both_deep_capable': both / len(pairs)}
    out['deepest_boxes'] = [
        {'k': int(k), 'depth_ub': float(ub[k]), 'box': boxes[k].to_json()}
        for k in np.argsort(-ub)[:10]]
    return out


# ------------------------------------------------------------- (2) blocker rows
def corner_frame_quad(V, corner, x0, y0, sig):
    x1, y1 = x0 + sig, y0 + sig
    if corner == 'BL':
        return [(p[0] - x0, p[1] - y0) for p in V]
    if corner == 'BR':
        return [(x1 - p[0], p[1] - y0) for p in V]
    if corner == 'TL':
        return [(p[0] - x0, y1 - p[1]) for p in V]
    return [(x1 - p[0], y1 - p[1]) for p in V]


def f_minmax_quad(Q):
    best = min(max(x, y) for x, y in Q)
    for k in range(4):
        px, py = Q[k]
        qx, qy = Q[(k + 1) % 4]
        dx, dy = qx - px, qy - py
        if dx == dy:
            continue
        s = (py - px) / (dx - dy)
        if 0.0 <= s <= 1.0:
            best = min(best, px + s * dx)
    return best


def annotate(path):
    """add a `depth` field to every blocker row of a t2 jsonl, in place."""
    rows = [json.loads(x) for x in open(path) if x.strip()]
    # group by point tag so the origin / sigma is computed once
    by = {}
    for r in rows:
        by.setdefault(r['tag'], []).append(r)
    for tag, rs in by.items():
        sig = rs[0]['sigma']
        # every row of a tag shares the same configuration; recover the origin
        # from the stored centre + the corner-frame centre of any BL/BR row
        x0 = y0 = None
        for r in rs:
            cf = r['centre_corner_frame']
            c = r['centre']
            if r['corner'] == 'BL':
                x0, y0 = c[0] - cf[0], c[1] - cf[1]
                break
            if r['corner'] == 'BR':
                x0, y0 = c[0] + cf[0] - sig, c[1] - cf[1]
                break
            if r['corner'] == 'TL':
                x0, y0 = c[0] - cf[0], c[1] + cf[1] - sig
                break
            if r['corner'] == 'TR':
                x0, y0 = c[0] + cf[0] - sig, c[1] + cf[1] - sig
                break
        for r in rs:
            cx, cy = r['centre']
            th = math.radians(r['theta_deg'])
            V = L.verts(cx, cy, th)
            Q = corner_frame_quad(V, r['corner'], x0, y0, sig)
            f = f_minmax_quad(Q)
            r['f_minmax_corner_frame'] = f
            r['depth'] = 1.0 - f
    with open(path, 'w') as fo:
        for r in rows:
            fo.write(json.dumps(r, default=str) + '\n')
    return rows


def per_corner_depth(rows, source):
    per = {}
    for r in rows:
        per.setdefault((r['tag'], r['corner']), []).append(r)
    corner_depth = {k: max(x['depth'] for x in v) for k, v in per.items()}
    bins = empty_dbins()
    for v in corner_depth.values():
        bins[dbin(v)] += 1
    bl = empty_dbins()
    for r in rows:
        bl[dbin(r['depth'])] += 1
    by_c = {}
    for c in L.CORNERS:
        vals = [v for (t, cc), v in corner_depth.items() if cc == c]
        by_c[c] = {'n_corners': len(vals),
                   'max': (max(vals) if vals else None),
                   'min': (min(vals) if vals else None),
                   'mean': (sum(vals) / len(vals) if vals else None),
                   'hist': {}}
        b = empty_dbins()
        for v in vals:
            b[dbin(v)] += 1
        by_c[c]['hist'] = b
    dvals = [r['depth'] for r in rows]
    return {'source': source, 'n_blockers': len(rows),
            'n_corners_with_a_blocker': len(corner_depth),
            'blocker_depth': {'max': max(dvals), 'min': min(dvals),
                              'mean': sum(dvals) / len(dvals)},
            'blocker_depth_hist': bl,
            'corner_DEPTH_hist': bins,
            'corner_DEPTH_by_corner': by_c,
            'n_negative_depth_rows': sum(1 for v in dvals if v <= 0.0)}


# -------------------------------------------------------------- (3) shallow A87
def part3(rows):
    per = {}
    for r in rows:
        per.setdefault((r['tag'], r['corner']), []).append(r)
    shallow = {k: v for k, v in per.items()
               if max(x['depth'] for x in v) < 0.3}
    nb = sum(len(v) for v in shallow.values())
    aa = sum(1 for v in shallow.values() for x in v if x['tilt_deg'] < L.TILT_POS)
    aa_exact = sum(1 for v in shallow.values() for x in v
                   if x.get('tilt_exact_zero'))
    loaded = sum(1 for v in shallow.values() for x in v if x['loaded_loadable'])
    ratt = sum(1 for v in shallow.values() for x in v if x['is_rattler'])
    allper = len(per)
    shb, bhb = empty_dbins(), empty_dbins()
    tb = L.empty_bins()
    for v in shallow.values():
        shb[dbin(max(x['depth'] for x in v))] += 1
        for x in v:
            bhb[dbin(x['depth'])] += 1
            tb[L.tilt_bin(x['tilt_deg'])] += 1
    return {'criterion': 'corners (point, corner) whose DEPTH = max blocker depth '
                         'is < 0.3',
            'n_corners_total': allper,
            'n_corners_shallow': len(shallow),
            'frac_corners_shallow': len(shallow) / allper if allper else None,
            'n_blockers_at_shallow_corners': nb,
            'n_axis_aligned_tilt_lt_1e-7': aa,
            'frac_axis_aligned': aa / nb if nb else None,
            'n_axis_aligned_theta_exactly_zero': aa_exact,
            'n_loaded_loadable_at_shallow_corners': loaded,
            'n_rattlers_at_shallow_corners': ratt,
            'DEPTH_hist_at_shallow_corners': shb,
            'blocker_depth_hist_at_shallow_corners': bhb,
            'tilt_hist_of_blockers_at_shallow_corners': tb}


# ------------------------------------------------------------- Trump exactly
def trump_exact_depth():
    getcontext().prec = 300
    p = os.path.join(L.ATT, 'A03-upper-reconstruct', 'trump11_exact.json')
    d = json.load(open(p))
    s = Decimal(d['s'])
    co = Decimal(d['cos_theta'])
    si = Decimal(d['sin_theta'])
    half = Decimal(1) / 2

    def quad(cx, cy, c, sn):
        return [(cx + c * u - sn * v, cy + sn * u + c * v)
                for (u, v) in ((-half, -half), (half, -half), (half, half),
                               (-half, half))]

    def fmm(Q):
        best = min(max(x, y) for x, y in Q)
        for k in range(4):
            px, py = Q[k]
            qx, qy = Q[(k + 1) % 4]
            dx, dy = qx - px, qy - py
            if dx == dy:
                continue
            t = (py - px) / (dx - dy)
            if 0 <= t <= 1:
                best = min(best, px + t * dx)
        return best

    out = []
    for i in (4, 6):
        sq = d['squares'][i]
        cx, cy = Decimal(sq['cx']), Decimal(sq['cy'])
        if i == 4:                       # upright: theta = O(1e-109), cos=1, sin=0
            c, sn = Decimal(1), Decimal(sq['theta'])
        else:
            c, sn = co, si
        Q = quad(cx, cy, c, sn)
        # TL corner frame: (x, s - y)
        QT = [(x, s - y) for (x, y) in Q]
        f = fmm(QT)
        out.append({'square': i, 'f_minmax_TL_frame': str(f)[:60],
                    'depth': str(1 - f)[:60], 'depth_float': float(1 - f)})
    return {'corner': 'TL', 'blockers': out,
            'DEPTH_TL_exact': max(out, key=lambda r: r['depth_float'])['depth'],
            'DEPTH_TL_float': max(r['depth_float'] for r in out),
            'note': 'Decimal at 300 dps from the certificate; the upright sq4 uses '
                    'cos = 1, sin = theta = O(1e-109) (exact to the certificate).'}


def main():
    t0 = time.time()
    print('free commit %.0f MB' % L.free_commit_mb(), flush=True)
    out = {'attempt': 'A89 / T2 addendum add-on: intrusion depth',
           'definition': 'depth(Q) = 1 - inf{max(p_x,p_y) : p in int(Q) cap '
                         '(0,1)^2} = 1 - f_min_max(Q) in the corner frame; '
                         'DEPTH(corner) = max over its blockers',
           'depth_bins': [b[0] for b in DEPTH_BINS]}
    print('(1) box census ...', flush=True)
    out['part1_BL_cover_boxes'] = part1()
    print('(2) blocker rows ...', flush=True)
    ra = annotate(os.path.join(L.RESULTS, 't2_blockers_a87.jsonl'))
    rb = annotate(os.path.join(L.RESULTS, 't2_blockers_atlas.jsonl'))
    rc = annotate(os.path.join(L.RESULTS, 't2_blockers_trump.jsonl'))
    out['part2_A87_167'] = per_corner_depth(ra, 'A87 167 certified k0 FJ points')
    out['part2_atlas_12'] = per_corner_depth(rb, 'A46 12 atlas families')
    out['part2_trump'] = per_corner_depth(rc, 'Trump exact certificate')
    out['part2_trump_rows'] = [
        {'corner': r['corner'], 'square': r['square'], 'tilt_deg': r['tilt_deg'],
         'depth': r['depth'], 'f_minmax': r['f_minmax_corner_frame']} for r in rc]
    out['part2_trump_TL_exact'] = trump_exact_depth()
    print('(3) shallow corners ...', flush=True)
    out['part3_A87_shallow_corners'] = part3(ra)
    out['secs'] = time.time() - t0
    json.dump(out, open(OUT, 'w'), indent=1, default=str)
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ('part1_BL_cover_boxes',)}, indent=1,
                     default=str), flush=True)
    print('\npart1:', json.dumps({k: v for k, v in out['part1_BL_cover_boxes'].items()
                                  if k != 'deepest_boxes'}, indent=1, default=str),
          flush=True)
    print('-> %s  (%.1f s)' % (OUT, time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
