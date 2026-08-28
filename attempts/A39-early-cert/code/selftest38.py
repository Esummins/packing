#!/usr/bin/env python3
"""
A38 self-test (design.md W1 CANARY + soundness audits + one smoke node).

  (a) TRUMP CANARY (mandatory).  The 11 placements of atlas entry 0 (the Trump/Stromquist packing)
      and all their D4 images must be NON-exempt at thr_cert AND at thr_float.  A single exempt
      Trump placement would mean the field cut prunes the true optimum -- an instant STOP.
      The canary also reports the raw float coverage mu(Q) of each placement (Lemma A33.1 says
      the SUM over the 11 is <= 11 + eta, so individually they sit at or below ~1 + eta).
  (b) mlow_box MONOTONICITY on 20 random nested box pairs: a bigger box must give a smaller bound.
  (c) EXACT CROSS-CHECK of 30 random grid cells: the stored float m_low against a per-atom
      exact-Fraction recomputation (mapper.mlow_exact semantics) on the SAME box, plus the
      slop-free exact m_low (the true bound) to confirm the float value never exceeds truth.
  (d) SMOKE NODE: one level-1 node (the triangle cell nearest the container centre, theta window
      [30,45]) at time_limit 60 with W1 OFF then ON.

  python selftest38.py [--time_limit 60] [--skip_smoke]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import sys
import time
from fractions import Fraction as F

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import fieldcut as fc                                  # noqa: E402
import node38                                          # noqa: E402
import cover38                                         # noqa: E402
from caselp import Box                                 # noqa: E402
from lpbox import Sym                                  # noqa: E402

REPO = fc.REPO
ATLAS = os.path.join(REPO, "attempts", "A37-cp-atlas", "results", "atlas_final.json")
RESULTS = os.path.join(HERE, "..", "results")
LOGS = os.path.join(HERE, "..", "logs")


# --------------------------------------------------------------------------- convention check
def trump_placements():
    """atlas entry 0's canonical_sig, with the (cx, cy, third) convention CONFIRMED geometrically:
    both readings (third = theta in radians, third = t = tan(theta/2)) are scored by the minimum
    pairwise SAT gap of the 11 unit squares and by containment in [0, s0]^2; the valid packing wins."""
    d = json.load(open(ATLAS))
    sig = d["entries"][0]["canonical_sig"]
    s = fc.S0F

    def corners(cx, cy, th):
        c, sn = math.cos(th), math.sin(th)
        e1 = np.array([c, sn]); e2 = np.array([-sn, c]); k = np.array([cx, cy])
        return np.array([k + 0.5 * (i * e1 + j * e2) for i, j in ((-1, -1), (1, -1), (1, 1), (-1, 1))])

    def gap(A, B):
        best = -1e18
        for P, Q in ((A, B), (B, A)):
            for i in range(4):
                e = P[(i + 1) % 4] - P[i]
                n = np.array([-e[1], e[0]]); n = n / np.linalg.norm(n)
                a, b = P @ n, Q @ n
                best = max(best, max(b.min() - a.max(), a.min() - b.max()))
        return best

    scores = {}
    for name, f in (("theta_radians", lambda u: u),
                    ("t_tan_half_theta", lambda u: 2 * math.atan(u))):
        sq = [corners(cx, cy, f(u)) for cx, cy, u in sig]
        mind = min(gap(sq[i], sq[j]) for i in range(11) for j in range(i + 1, 11))
        allp = np.vstack(sq)
        scores[name] = dict(min_pairwise_sat_gap=float(mind),
                            bbox=[float(allp.min()), float(allp.max())],
                            inside_container=bool(allp.min() >= -1e-6 and allp.max() <= s + 1e-6),
                            thetas_deg=sorted(set(round(math.degrees(f(u)) % 90, 4) for _, _, u in sig)))
    verdict = max(scores, key=lambda k: scores[k]["min_pairwise_sat_gap"])
    conv = (lambda u: u) if verdict == "theta_radians" else (lambda u: 2 * math.atan(u))
    P = [(cx, cy, conv(u)) for cx, cy, u in sig]
    return P, dict(verdict=verdict, scores=scores)


# --------------------------------------------------------------------------------- (a) canary
def canary(mk, P):
    s = fc.S0F
    sym = Sym("D4", s)
    rows = []
    worst = dict(thr_cert=None, thr_float=None)
    n_exempt = {"thr_cert": 0, "thr_float": 0}
    for pi, (cx, cy, th) in enumerate(P):
        for (a, b, t) in sym.placement_images(cx, cy, th):
            thd = math.degrees(t) % 90.0
            cov = fc.coverage_at(math.tan(math.radians(thd) / 2.0), a, b)
            e1 = mk.exempt(thd, a, b, fc.THR_CERT_F)
            e2 = mk.exempt(thd, a, b, fc.THR_FLOAT)
            # the eroded-cell m_low actually seen by the filter
            i, j, k, bad = mk._idx(np.array([thd]), np.array([[a, b]]))
            ml = float(mk.ero[i[0], j[0], k[0]]) if not bad[0] else None
            rows.append(dict(square=pi, cx=a, cy=b, theta_deg=thd, coverage=cov,
                             eroded_mlow=ml, exempt_cert=bool(e1), exempt_float=bool(e2),
                             in_grid=bool(not bad[0])))
            n_exempt["thr_cert"] += int(e1)
            n_exempt["thr_float"] += int(e2)
            if ml is not None:
                for key, thr in (("thr_cert", fc.THR_CERT_F), ("thr_float", fc.THR_FLOAT)):
                    slackm = thr - ml            # margin: > 0 means safely non-exempt
                    if worst[key] is None or slackm < worst[key]["margin"]:
                        worst[key] = dict(margin=slackm, square=pi, cx=a, cy=b, theta_deg=thd,
                                          eroded_mlow=ml)
    cov = [r["coverage"] for r in rows]
    return dict(n_placements=len(rows), n_exempt=n_exempt,
                PASS=bool(n_exempt["thr_cert"] == 0 and n_exempt["thr_float"] == 0),
                coverage_min=min(cov), coverage_max=max(cov),
                coverage_sum_one_orbit=sum(r["coverage"] for r in rows if abs(r["cx"] - P[r["square"]][0]) < 1e-12
                                           and abs(r["cy"] - P[r["square"]][1]) < 1e-12),
                worst_margin=worst, placements=rows)


# ------------------------------------------------------------------------- (b) monotonicity
def monotonicity(n=20, seed=38):
    rng = np.random.default_rng(seed)
    lo, hi = 0.5, fc.S0F - 0.5
    out, bad = [], 0
    for _ in range(n):
        t0 = float(rng.uniform(0, 0.95)); t1 = t0 + float(rng.uniform(1e-3, 0.05))
        x0 = float(rng.uniform(lo, hi - 0.2)); x1 = x0 + float(rng.uniform(1e-3, 0.1))
        y0 = float(rng.uniform(lo, hi - 0.2)); y1 = y0 + float(rng.uniform(1e-3, 0.1))
        small = (t0, min(1.0, t1), x0, x1, y0, y1)
        gt = float(rng.uniform(1e-3, 0.03)); gc = float(rng.uniform(1e-3, 0.05))
        big = (max(0.0, t0 - gt), min(1.0, t1 + gt), x0 - gc, x1 + gc, y0 - gc, y1 + gc)
        ms, mb = fc.mlow_box(*small), fc.mlow_box(*big)
        ok = mb <= ms + 1e-12
        bad += (not ok)
        out.append(dict(small=list(small), big=list(big), mlow_small=ms, mlow_big=mb, ok=bool(ok)))
    return dict(n=n, violations=bad, PASS=bool(bad == 0), samples=out)


# ------------------------------------------------------------------------ (c) exact cross-check
def exact_crosscheck(mk, n=30, seed=3838):
    """Compare the stored float m_low of random grid cells with the exact-Fraction recomputation
    on the SAME (bit-identical) box.  Fraction(float) is exact, so the two differ only by float
    arithmetic; the slop-free exact value is the TRUE m_low and must dominate the float bound."""
    rng = np.random.default_rng(seed)
    NT, NC = mk.NT, mk.NC
    ht, hc, clo = mk.ht, mk.hc, mk.clo
    rows, bad_sound, bad_close = [], 0, 0
    for _ in range(n):
        i = int(rng.integers(0, NT)); j = int(rng.integers(0, NC)); k = int(rng.integers(0, NC))
        t0f, t1f = i * ht, (i + 1) * ht
        x0f, x1f = clo + hc * j, clo + hc * (j + 1)
        y0f, y1f = clo + hc * k, clo + hc * (k + 1)
        grid_v = float(mk.mlow[i, j, k])
        float_v = fc.mlow_box(t0f, t1f, x0f, x1f, y0f, y1f)
        args = (F(t0f), F(min(1.0, t1f)), F(x0f), F(x1f), F(y0f), F(y1f))
        ex_v = fc.mlow_box_exact(*args)                      # same SLOP = 1e-6
        tr_v = fc.mlow_box_exact(*args, slop=F(0))           # slop-free: the TRUE m_low
        sound = float_v <= float(tr_v) + 1e-12
        close = abs(float_v - float(ex_v)) <= 0.05
        bad_sound += (not sound)
        bad_close += (not close)
        rows.append(dict(cell=[i, j, k], grid=grid_v, float=float_v,
                         exact=str(ex_v), exact_f=float(ex_v),
                         true_mlow=str(tr_v), true_f=float(tr_v),
                         grid_eq_float=bool(abs(grid_v - float_v) < 1e-12),
                         sound=bool(sound), within_0p05=bool(close)))
    return dict(n=n, unsound=bad_sound, not_within_0p05=bad_close,
                grid_matches_float=all(r["grid_eq_float"] for r in rows),
                max_abs_float_minus_exact=max(abs(r["float"] - r["exact_f"]) for r in rows),
                max_true_minus_float=max(r["true_f"] - r["float"] for r in rows),
                PASS=bool(bad_sound == 0), samples=rows)


# ------------------------------------------------------------------------- (e) the W2 row path
def w2_path(mk, n=20000, seed=1138):
    """W2 is inert wherever the cores are loose (c_j < 1), which is the level-1 regime; this
    exercises and validates the W2 attribution anyway.  Over the 216 level-1 cells, take the one
    with the LARGEST c_j, form thr_node = 1 + eta - max(0, c_j - 1) < thr_cert, and check on random
    admissible placements that (i) exempt@thr_node is a strict SUPERSET of exempt@thr_cert and
    (ii) FieldFilter attributes exactly the difference to rows_dropped_w2."""
    cs, _ = cover38.cells()
    scan = [(fc.core_mlow(cover38.to_box(c), mk.meta), c) for c in cs]
    cj, cell = max(scan, key=lambda p: p[0])
    tn = fc.thr_node([cj])
    rng = np.random.default_rng(seed)
    lo, hi = 0.5, fc.S0F - 0.5
    C = rng.uniform(lo, hi, size=(n, 2))
    th = rng.uniform(0.0, 90.0)
    e1 = mk.exempt_many(th, C, fc.THR_CERT_F)
    e2 = mk.exempt_many(th, C, tn)
    filt = node38.FieldFilter(mk, fc.THR_CERT_F, tn)
    keep = np.ones(n, dtype=bool)
    ex = filt(th, C, keep)
    c = filt.counts()
    return dict(cell=dict(i=cell['i'], j=cell['j'], k=cell['k'], idx=cell['idx']),
                c_j=cj, thr_cert=fc.THR_CERT_F, thr_node=tn,
                n_cells_with_cj_gt_1=sum(1 for m, _ in scan if m > 1.0), n_cells=len(scan),
                cj_min=min(m for m, _ in scan), cj_max=cj,
                theta_deg=th, n_samples=n,
                n_exempt_cert=int(e1.sum()), n_exempt_node=int(e2.sum()),
                superset=bool((e1 & ~e2).sum() == 0), strictly_more=bool(e2.sum() > e1.sum()),
                counts=c,
                attribution_ok=bool(c['rows_dropped_w1'] == int(e1.sum())
                                    and c['rows_dropped_w2'] == int((e2 & ~e1).sum())
                                    and bool((ex == e2).all())),
                PASS=bool((e1 & ~e2).sum() == 0 and e2.sum() > e1.sum()
                          and c['rows_dropped_w1'] == int(e1.sum())
                          and c['rows_dropped_w2'] == int((e2 & ~e1).sum())))


# ---------------------------------------------------------------------------- (d) smoke node
def smoke(time_limit=60.0, i=0, j=0, k=2):
    cs, geo = cover38.cells()
    cell = next(c for c in cs if (c['i'], c['j'], c['k']) == (i, j, k))
    B = cover38.to_box(cell)
    os.makedirs(LOGS, exist_ok=True)
    os.makedirs(os.path.join(RESULTS, 'selftest'), exist_ok=True)
    out = []
    for w1 in (False, True):
        tag = 'w1on' if w1 else 'w1off'
        lp = os.path.join(LOGS, 'smoke_%s.log' % tag)
        open(lp, 'w').close()

        def log(*a, _lp=lp):
            with open(_lp, 'a') as f:
                f.write(' '.join(str(x) for x in a) + '\n')
        t0 = time.time()
        rec = node38.solve_a38_node(
            fc.S0F, [B], cover38.BUDGET, w1=w1, w2=w1, time_limit=time_limit, log=log,
            out=os.path.join(RESULTS, 'selftest', 'smoke_%s.json' % tag))
        rec['wall'] = time.time() - t0
        rec['tag'] = tag
        rec['log'] = os.path.relpath(lp, REPO).replace('\\', '/')
        out.append(rec)
    off, on = out
    return dict(cell=dict(i=i, j=j, k=k, idx=cell['idx'], box=B.to_json(),
                          exact={kk: str(cell[kk]) for kk in ('x0', 'x1', 'y0', 'y1', 'th0', 'th1')}),
                budget=cover38.BUDGET, time_limit=time_limit,
                w1_off=off, w1_on=on,
                delta_tau=(on.get('tau') or 0) - (off.get('tau') or 0),
                rows_dropped_w1=(on.get('filter') or {}).get('rows_dropped_w1'),
                rows_dropped_w2=(on.get('filter') or {}).get('rows_dropped_w2'))


# ---------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--time_limit', type=float, default=60.0)
    ap.add_argument('--skip_smoke', action='store_true')
    ap.add_argument('--grid', default=fc.GRID_PATH)
    ap.add_argument('--out', default=os.path.join(RESULTS, 'selftest38.json'))
    a = ap.parse_args()
    os.makedirs(RESULTS, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    t00 = time.time()

    if not os.path.exists(a.grid):
        print('building grid ...', flush=True)
        fc.build_grid(path=a.grid)
    mk = node38.mask(a.grid)
    f = fc.field()

    P, conv = trump_placements()
    print('convention: %s  (%s)' % (conv['verdict'], json.dumps(conv['scores'][conv['verdict']])), flush=True)

    R = dict(when=time.strftime('%Y-%m-%dT%H:%M:%S'), host=platform.node(),
             python=sys.version.split()[0], numpy=np.__version__,
             s=str(fc.S0), eta_cert=str(fc.ETA_CERT), thr_cert=str(fc.THR_CERT),
             thr_cert_float=fc.THR_CERT_F, thr_float_NUM=fc.THR_FLOAT,
             cert=os.path.relpath(f.path, REPO).replace('\\', '/'),
             n_atoms=f.n, d4_closed=f.d4_closed,
             grid=dict(mk.meta), convention=conv)

    R['a_canary'] = canary(mk, P)
    print('(a) canary PASS=%s  exempt@cert=%d exempt@float=%d  worst margin cert=%.6f float=%.6f'
          % (R['a_canary']['PASS'], R['a_canary']['n_exempt']['thr_cert'],
             R['a_canary']['n_exempt']['thr_float'],
             R['a_canary']['worst_margin']['thr_cert']['margin'],
             R['a_canary']['worst_margin']['thr_float']['margin']), flush=True)

    R['b_monotonicity'] = monotonicity()
    print('(b) monotonicity PASS=%s (%d violations / 20)'
          % (R['b_monotonicity']['PASS'], R['b_monotonicity']['violations']), flush=True)

    R['c_exact_crosscheck'] = exact_crosscheck(mk)
    c = R['c_exact_crosscheck']
    print('(c) exact cross-check PASS=%s  grid==float:%s  max|float-exact|=%.3e  '
          'not-within-0.05: %d/30' % (c['PASS'], c['grid_matches_float'],
                                      c['max_abs_float_minus_exact'], c['not_within_0p05']), flush=True)

    R['e_w2_path'] = w2_path(mk)
    e = R['e_w2_path']
    print('(e) W2 path PASS=%s  worst-case level-1 c_j=%.6f -> thr_node=%.6f (%d/%d cells have '
          'c_j > 1); exempt %d -> %d of %d samples'
          % (e['PASS'], e['c_j'], e['thr_node'], e['n_cells_with_cj_gt_1'], e['n_cells'],
             e['n_exempt_cert'], e['n_exempt_node'], e['n_samples']), flush=True)

    R['field_stats'] = [mk.frac_exempt(fc.THR_CERT_F), mk.frac_exempt(fc.THR_FLOAT)]
    print('(*) exempt cell fraction: ' + json.dumps(R['field_stats']), flush=True)

    if not a.skip_smoke:
        R['d_smoke'] = smoke(a.time_limit)
        d = R['d_smoke']
        for tag in ('w1_off', 'w1_on'):
            r = d[tag]
            print('(d) %-7s status=%-12s tau=%.6f minmass=%s maxcov=%s rows=%s %.1fs'
                  % (tag, r.get('status'), r.get('tau', float('nan')), r.get('minmass'),
                     r.get('maxcov'), r.get('n_rows'), r.get('wall', 0)), flush=True)
        print('(d) rows_dropped_w1=%s rows_dropped_w2=%s  delta_tau=%+.6f  core_mlow=%s'
              % (d['rows_dropped_w1'], d['rows_dropped_w2'], d['delta_tau'],
                 d['w1_on'].get('field', {}).get('core_mlow')), flush=True)

    R['PASS'] = bool(R['a_canary']['PASS'] and R['b_monotonicity']['PASS']
                     and R['c_exact_crosscheck']['PASS'] and R['e_w2_path']['PASS'])
    R['wall_s'] = time.time() - t00
    json.dump(R, open(a.out, 'w'), indent=1)
    print('SELFTEST %s -> %s (%.0fs)' % ('PASS' if R['PASS'] else 'FAIL', a.out, R['wall_s']),
          flush=True)
    return 0 if R['PASS'] else 1


if __name__ == '__main__':
    sys.exit(main())
