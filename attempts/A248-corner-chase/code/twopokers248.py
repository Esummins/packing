"""A248: Lemma TWO-POKERS -- two wall-touching pokers on one wall (B beside the flat floor meeter of
the lower corner, B' beside the flat ceiling meeter of the upper corner, offsets <= 1) need
    s >= 2 + F(theta, theta_f),   F = psi(t) + psi(t_f) + sin t_f + max(cos t_f tan t, sin t - (cos t - cos t_f) cot t_f)
(theta <= theta_f WLOG; psi(t) = (1 - sin t)/cos t = tan(45 deg - t/2)), corner_chase.md s.3.2.
(i) a CERTIFIED lower bound of min F over the triangle by adaptive bisection with monotone
    enclosures (every term is a product / difference of monotone functions on a box);
(ii) the line theta + theta_f = 90 deg, where F = h(theta) = tan(45 - t/2) + tan(t/2) + sec t, minimised;
(iii) the SAT feasibility sup-margin of the pair (wall-touching or floating) over a ladder of sides.
    python twopokers248.py   -> results/twopokers248.json
"""
import json
import math
import os
import sys

import numpy as np
from scipy.optimize import minimize, minimize_scalar

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import geom248 as G                                                   # noqa: E402

GUARD = 1e-9


def psi(t):
    return (1.0 - math.sin(t)) / math.cos(t)


def F(t, tf):
    a, b = math.cos(tf), math.cos(t)
    return psi(t) + psi(tf) + math.sin(tf) + max(a * math.tan(t), math.sin(t) - (b - a) / math.tan(tf))


def lower_bound(t0, t1, f0, f1):
    """F >= this on the box [t0,t1] x [f0,f1] with t1 <= f1 (theta <= theta_f): psi decreasing,
    sin increasing, cos decreasing, tan increasing, cot decreasing."""
    base = psi(t1) + psi(f1) + math.sin(f0)
    lb1 = math.cos(f1) * math.tan(t0)                                  # both factors >= 0
    lb2 = math.sin(t0) - max(0.0, math.cos(t0) - math.cos(f1)) / math.tan(f0)
    return base + max(lb1, lb2) - GUARD


def certify(target, eps=1e-4, hi=math.pi / 2 - 1e-9, max_boxes=4_000_000):
    """bisect the triangle {eps <= t <= tf <= hi} until every box has lower bound >= target or is
    smaller than 1e-7; returns (certified, boxes, worst box)."""
    stack = [(eps, hi, eps, hi)]
    boxes = 0
    worst = None
    while stack:
        t0, t1, f0, f1 = stack.pop()
        if t0 > f1:
            continue
        boxes += 1
        if boxes > max_boxes:
            return False, boxes, (t0, t1, f0, f1)
        lb = lower_bound(t0, min(t1, f1), max(f0, t0), f1)
        if lb >= target:
            continue
        if max(t1 - t0, f1 - f0) < 1e-7:
            return False, boxes, (t0, t1, f0, f1, lb)
        if t1 - t0 >= f1 - f0:
            m = 0.5 * (t0 + t1)
            stack += [(t0, m, f0, f1), (m, t1, f0, f1)]
        else:
            m = 0.5 * (f0 + f1)
            stack += [(t0, t1, f0, m), (t0, t1, m, f1)]
        worst = (t0, t1, f0, f1, lb)
    return True, boxes, worst


def h(t):
    return math.tan(math.pi / 4 - t / 2) + math.tan(t / 2) + 1.0 / math.cos(t)


def sat_margin(x, s):
    th, xv, d, thf, xvf, df = x
    if not (0 < th < math.pi / 2 and 0 < thf < math.pi / 2):
        return -1.0
    B = G.poker(th, d, x_v=xv)
    Bp = G.flip_up(G.poker(thf, df, x_v=xvf), s)
    return min(G.poly_gap(B, Bp), d, df, xv - math.sin(th), xvf - math.sin(thf),
               (1 - xv) * math.tan(th) - d, (1 - xvf) * math.tan(thf) - df, s - Bp[:, 1].max())


def sup_margin(s, restarts=120, seed=0):
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(restarts):
        th, thf = rng.uniform(0.01, 1.55, 2)
        x0 = [th, math.sin(th) + rng.uniform(0, 0.3), rng.uniform(0, 0.3),
              thf, math.sin(thf) + rng.uniform(0, 0.3), rng.uniform(0, 0.3)]
        r = minimize(lambda x: -sat_margin(x, s), x0, method='Nelder-Mead',
                     options={'xatol': 1e-10, 'fatol': 1e-12, 'maxiter': 4000})
        if best is None or r.fun < best.fun:
            best = r
    return -best.fun, [float(v) for v in best.x]


def main():
    out = {}
    r = minimize_scalar(h, bounds=(0.01, 1.2), method='bounded', options={'xatol': 1e-12})
    out['line'] = {'theta_deg': math.degrees(r.x), 'min_h': r.fun, 's_star': 2 + r.fun}
    print('on theta + theta_f = 90: min h = %.10f at theta = %.6f deg -> s* = %.10f' % (r.fun, math.degrees(r.x), 2 + r.fun))
    # a fine grid over the triangle for the numerical minimum of F
    best = (9.0, None)
    for t in np.linspace(0.001, 1.57, 800):
        for tf in np.linspace(t, 1.57, 400):
            v = F(t, tf)
            if v < best[0]:
                best = (v, (math.degrees(t), math.degrees(tf)))
    out['grid_min'] = {'F': best[0], 'at_deg': best[1]}
    print('grid min F = %.8f at %s' % best)
    target = r.fun - 1e-6
    ok, boxes, worst = certify(target)
    out['certified'] = {'target': target, 'ok': ok, 'boxes': boxes, 'worst': worst,
                        's_lower_bound': 2 + target if ok else None}
    print('certified min F >= %.8f over the triangle: %s (%d boxes)' % (target, ok, boxes))
    ladder = {}
    for s in (3.82, 3.877084, 3.90, 3.93, 3.934, 3.936, 3.94, 3.95, 3.97, 4.0):
        m, x = sup_margin(s)
        ladder['%.6f' % s] = {'sup_margin': m, 'x': x}
        print('s = %.6f  sup SAT margin %+.5f  (theta %.2f, theta_f %.2f deg)' % (s, m, math.degrees(x[0]), math.degrees(x[3])))
    out['sat_ladder'] = ladder
    json.dump(out, open(os.path.join(ATT, 'results', 'twopokers248.json'), 'w', encoding='utf-8'), indent=1)


if __name__ == '__main__':
    main()
