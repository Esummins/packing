r"""exchange87_refine.py -- high-resolution re-decision of the BORDERLINE fits.

The main scan decides the fit test on a 1/200 centre grid x 1 deg tilt grid plus
a local refinement from the single best cell.  Several (packing, corner) cases
land within 1e-3 of lambda = 1, where that is not enough to decide.  This pass
rebuilds the PRE-RELAXATION 10-square configuration of a case exactly (9 kept
squares + the exact corner slot square -- reproducible from the packing and the
corner alone), scans tilts at 1 deg keeping the best centre per tilt, then runs a
pattern search in (cx, cy, theta) from the best cell of each of the top tilts.

Any lambda >= 1 found is verified exactly: rational coordinates, interval SAT
gaps > 0 against all 10 squares and container clearance >= 0.

Usage: python exchange87_refine.py
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import json
import math
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exchange87 as X                                        # noqa: E402

RESULTS = X.RESULTS
OUT = os.path.join(RESULTS, 'exchange87.refine.json')
BORDER_LO = 0.99


def per_tilt_scan(sqs, m, tilts_deg, h=X.H_FIT):
    """best (lambda, cx, cy) for each tilt."""
    N = int(math.ceil(m / h))
    xs = (np.arange(N) + 0.5) * h
    pre = []
    for (cx, cy, th) in sqs:
        DX = xs[None, :] - cx
        DY = xs[:, None] - cy
        ct, st = math.cos(th), math.sin(th)
        pre.append((DX, DY, np.abs(DX * ct + DY * st),
                    np.abs(-DX * st + DY * ct), th))
    dedge = np.minimum(xs, m - xs)
    CB = 2.0 * np.minimum(dedge[None, :], dedge[:, None])
    out = []
    for td in tilts_deg:
        th = math.radians(td)
        ct, st = math.cos(th), math.sin(th)
        L = CB / (abs(ct) + abs(st))
        for (DX, DY, A1, A2, thj) in pre:
            d = th - thj
            w = abs(math.cos(d)) + abs(math.sin(d))
            lj = np.maximum((A1 - 0.5) / (0.5 * w), (A2 - 0.5) / (0.5 * w))
            np.maximum(lj, 2.0 * np.abs(DX * ct + DY * st) - w, out=lj)
            np.maximum(lj, 2.0 * np.abs(-DX * st + DY * ct) - w, out=lj)
            np.minimum(L, lj, out=L)
        k = int(np.argmax(L))
        iy, ix = divmod(k, N)
        out.append((float(L.flat[k]), td, float(xs[ix]), float(xs[iy])))
    return out


def pattern_search(sqs, m, lam, td, px, py, iters=90):
    """(cx, cy, theta) pattern search on the exact lambda formula."""
    th = math.radians(td)
    sp, stt = X.H_FIT, math.radians(1.0)
    for _ in range(iters):
        moved = False
        for dth in (-stt, 0.0, stt):
            for dx in (-sp, 0.0, sp):
                for dy in (-sp, 0.0, sp):
                    if dth == 0.0 and dx == 0.0 and dy == 0.0:
                        continue
                    v = X.lam_at(sqs, m, px + dx, py + dy, th + dth)
                    if v > lam + 1e-15:
                        lam, px, py, th = v, px + dx, py + dy, th + dth
                        moved = True
        if not moved:
            sp *= 0.5
            stt *= 0.5
            if sp < 1e-15:
                break
    return lam, th, px, py


def build_case(pk, cn):
    """rebuild the pre-relaxation 10-square configuration of (pk, cn)."""
    sqsQ, m = X.z_to_sqs(pk['z'])
    mf = float(m)
    sf = [(float(a), float(b), float(c)) for a, b, c in sqsQ]
    dep = [X.depth_at_corner(s, cn, mf) for s in sf]
    intr = sorted([i for i in range(11) if dep[i] > X.TOL_BLOCK],
                  key=lambda i: -dep[i])
    if len(intr) < 2:
        return None
    keep = [i for i in range(11) if i not in (intr[0], intr[1])]
    slot = X.slot_square(cn, m)
    sqs10 = [sf[i] for i in keep] + [(float(slot[0]), float(slot[1]), 0.0)]
    sqsQ10 = [sqsQ[i] for i in keep] + [slot]
    return sqs10, sqsQ10, m, mf


def main():
    rows = []
    for f in ('exchange87.jsonl', 'exchange87.anchored.jsonl'):
        p = os.path.join(RESULTS, f)
        if os.path.exists(p):
            rows += [json.loads(l) for l in open(p)]
    pk_by_name = {}
    for p in X.load_packings() + [X.load_trump()] + X.load_anchored():
        pk_by_name[p['name']] = p

    todo = [r for r in rows
            if r.get('largest_inscribable_side') is not None
            and r['largest_inscribable_side'] >= BORDER_LO
            and not r.get('slot_blocked')]
    X.log('refine: %d borderline/successful cases (lambda >= %.2f) of %d'
          % (len(todo), BORDER_LO, len(rows)))
    out = []
    for r in todo:
        t0 = time.time()
        pk = pk_by_name.get(r['packing'])
        if pk is None:
            continue
        b = build_case(pk, r['corner'])
        if b is None:
            continue
        sqs10, sqsQ10, m, mf = b
        scan = per_tilt_scan(sqs10, mf, list(range(0, 90)))
        scan.sort(key=lambda t: -t[0])
        best = (-1e30, 0.0, 0.0, 0.0)
        for lam, td, px, py in scan[:6]:
            v = pattern_search(sqs10, mf, lam, td, px, py)
            if v[0] > best[0]:
                best = v
        lam, th, px, py = best
        rec = {'packing': r['packing'], 'corner': r['corner'],
               'sigma': r['sigma'],
               'lambda_coarse_main_run': r['largest_inscribable_side'],
               'lambda_refined_pre_relax': lam,
               'theta_deg': math.degrees(th), 'cx': px, 'cy': py,
               'secs': time.time() - t0}
        if lam >= 1.0:
            rec['placement'] = X.verify_placement(sqsQ10, m, px, py, th)
            rec['EXCHANGE_SUCCESS'] = bool(rec['placement']['VERIFIED'])
            rec['host_cert'] = X.certify_config(sqsQ10, m)
        else:
            rec['EXCHANGE_SUCCESS'] = False
        out.append(rec)
        X.log('  %-18s %-3s  lambda %.9f -> %.9f  %s  (%.0fs)'
              % (r['packing'], r['corner'], r['largest_inscribable_side'],
                 lam, 'SUCCESS' if rec['EXCHANGE_SUCCESS'] else 'fail',
                 rec['secs']))
    json.dump({'border_lo': BORDER_LO, 'n_refined': len(out),
               'n_success': sum(1 for r in out if r['EXCHANGE_SUCCESS']),
               'rows': out}, open(OUT, 'w'), indent=1)
    X.log('refine done: %d/%d succeed after refinement'
          % (sum(1 for r in out if r['EXCHANGE_SUCCESS']), len(out)))


if __name__ == '__main__':
    main()
