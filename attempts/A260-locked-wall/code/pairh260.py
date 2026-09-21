"""A260 hybrid CORNER-PAIR, common tilt per wall (the open pair of family258 s.7 with f_W = f_1):
    p = (b, phi, a', phi', e, e')      corner BR of [0,s]^2
    floor:  W  = END toucher, end gap b, tilt phi;   s1 = W - (sec phi + e) along the wall   (e = 0: the row of A259)
    right:  S' = START toucher, offset a', tilt phi';  W' = S' + (sec phi' + e') along the wall.
PAIR^h(p; s): no unit square inside [0,s]^2, free of the four squares, has
    (i) (q-O).(-v) >= 1/2 and q_x >= s/2   or   (ii) (q-O).u >= 1/2 and q_y <= s/2          (pair259's two cases).
The corner frame is monotone in s exactly as in normal_room.md s.2.3 (the four squares are fixed in the BR frame).
PLUG [T] (locked_wall.md s.4): for a' in (0.354 + RHO, 1) no free unit square meets the corner box [s-RHO, s] x [0, RHO].
    python pairh260.py         (probe: margins for a few tilts / gaps, [M])"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom260 as H                                                   # noqa: E402
import pair259 as P                                                   # noqa: E402
Z = H.Z
RHO = 0.25


def pairh_verts(p, s):
    b, f, a1, f1, e, e1 = p
    dW = s - b - H.w_of(f)
    d1 = dW - 1.0 / math.cos(f) - e
    return [H.toucher(d1, f, s, 0), H.toucher(dW, f, s, 0),
            H.toucher(a1, f1, s, 1), H.toucher(a1 + 1.0 / math.cos(f1) + e1, f1, s, 1)]


def plug(s, rho=RHO):
    return np.array([(s - rho, 0.0), (s, 0.0), (s, rho), (s - rho, rho)])


def feas(p, s):
    Vs = pairh_verts(p, s)
    m = min(Z.contain_margin(V, s) for V in Vs)
    for i in (0, 1):
        for j in (2, 3):
            m = min(m, Z.poly_gap(Vs[i], Vs[j]))
    return m


def in_domain(p, s, adj=True):
    b, f, a1, f1, e, e1 = p
    a = s - b - e - Z.span(f)
    b1 = s - a1 - e1 - Z.span(f1)
    m = min(1 - b, 1 - a1, 1 - a, 1 - b1, a, b1, e, e1)
    if adj:
        m = min(m, a + H.w_of(f) - (s - 2), b + H.w_of(f) - (s - 2), a1 + H.w_of(f1) - (s - 2), b1 + H.w_of(f1) - (s - 2))
    return m


if __name__ == '__main__':
    s = H.SHAT
    rng = np.random.default_rng(3)
    for emax in (0.0, 0.1, 0.2, 0.35):
        worst, n, arg = -9, 0, None
        for _ in range(4000):
            f, f1 = rng.uniform(1, 35, 2) * Z.DEG
            p = (rng.uniform(0.6, 1), f, rng.uniform(0.6, 1), f1, rng.uniform(0.5, 1) * emax, 0.0)
            if in_domain(p, s) < 0 or feas(p, s) < 0:
                continue
            n += 1
            m, pose = P.pair_margin(0, 0, 0, 0, s, 3.0, pairh_verts(p, s))
            if m > worst:
                worst, arg = m, (p, pose)
            if n >= 60:
                break
        print('emax %.2f  n %d  worst pair margin %+.4f  (HOLE-ONE slack %+.4f)' % (emax, n, worst, -(4 - s) / 2),
              None if arg is None else [round(float(t), 4) for t in arg[0]], flush=True)
