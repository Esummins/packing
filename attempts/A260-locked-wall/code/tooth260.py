"""A260 OPEN-TOOTH [T-computed check of the closed form, locked_wall.md s.2]: the least depth of the lowest vertex P of
a unit square of tilt psi (edge directions psi, psi + 90 deg, psi in [0, 90)) free of an OPEN PAIR of common tilt phi and
shift e (s1, W = s1 + (sec phi + e, 0)), with P over the notch span (between s1's top vertex and W's top vertex).
Closed form, c = cos phi, g = sin phi, d = psi - phi:
    psi <= phi :                          tau = c (1 + sin(phi - psi) - e g)                   (P on s1's edge line)
    psi >= phi :  tau = c + min(LIP, FAR)  (P = A + x u + t v in the notch frame; value c t + g x; s1 and W are quadrants)
        LIP (s1's top vertex on Q's left edge):  tan(phi) sin d <= e cos(psi) (P in the SLOT, W's vertex on Q's right edge):
                 sin(psi) (tan(phi) sin d - e cos(psi));          else (P on W's edge line): -e g c + g (tan(phi) + e g) tan d
        FAR (Q's far-left vertex on s1's edge line): sin d <= e c:  c (sin^2 d - e sin(psi)) / cos d + g sin d;
                 else: -e g c + g sin d
and for every psi:   tau >= c - (e/2) sin 2 psi >= c - e/2   (POKE form).   Exact value: room259.centre_set."""
import math
import os
import sys

import numpy as np
from shapely.geometry import box as sbox

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom260 as H                                                   # noqa: E402
import room259 as R                                                   # noqa: E402
Z = H.Z


def tau(phi, e, psi):
    c, g, t = math.cos(phi), math.sin(phi), math.tan(phi)
    d = psi - phi
    if d <= 0:
        return c * (1 + math.sin(-d) - e * g)
    ec, eg = e * c, e * g
    if t * math.sin(d) <= e * math.cos(psi):                          # lip + W's vertex (P in the slot)
        lip = c * (t * math.sin(d) ** 2 - e * math.sin(psi) * math.cos(d)) + g * (t * math.sin(d) * math.cos(d) + e * math.sin(psi) * math.sin(d))
    else:                                                             # lip + W's edge line
        lip = -eg * c + g * (t + eg) * math.tan(d)
    if math.sin(d) <= ec:                                             # far vertex on s1's edge line, P in the slot
        far = c * (math.sin(d) ** 2 - e * math.sin(psi)) / math.cos(d) + g * math.sin(d)
    else:
        far = -eg * c + g * math.sin(d)
    return c + min(lip, far)


def exact(phi, e, psi, a=3.0, s=9.0):
    Vs = [H.toucher(a, phi, s, 0), H.toucher(a + 1 / math.cos(phi) + e, phi, s, 0)]
    C = R.centre_set(Vs, s, psi)
    cp, sp = math.cos(psi), math.sin(psi)
    x0, x1 = a + math.cos(phi), a + 1 / math.cos(phi) + e + math.cos(phi)      # the two top vertices
    strip = sbox(x0 + (cp - sp) / 2, -1, x1 + (cp - sp) / 2, s + 1)
    best = 9.0
    for Pg in R.polys_of(C.intersection(strip)):
        best = min(best, float(np.array(Pg.exterior.coords)[:, 1].min()) - (cp + sp) / 2)
    return best


if __name__ == '__main__':
    worst, poke = 0.0, 9.0
    for phd in (2.0, 8.0, 14.545, 20.0, 28.0, 40.0):
        for e in (0.0, 0.02, 0.06, 0.13, 0.3):
            for psd in np.arange(0.0, 90.0, 2.5):
                phi, psi = phd * Z.DEG, psd * Z.DEG
                t, x = tau(phi, e, psi), exact(phi, e, psi)
                # beyond psi = phi + 45 the square's lowest vertex is no longer the one in the notch: compare there too
                worst = max(worst, abs(t - x)) if psd <= phd + 45 else worst
                poke = min(poke, x - (math.cos(phi) - 0.5 * e * math.sin(2 * psi)))
                if abs(t - x) > 1e-9 and psd <= phd + 45:
                    print('phi %5.2f e %.2f psi %5.1f  formula %.6f exact %.6f' % (phd, e, psd, t, x))
    print('max |formula - exact| (psi <= phi + 45 deg): %.2e;   min(exact - (c - e/2 sin 2psi)) = %+.4f' % (worst, poke))
