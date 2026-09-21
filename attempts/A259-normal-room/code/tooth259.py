"""A259 check of Lemma TOOTH [T] against exact centre sets: one floor row in a tall container; the least height of the
lowest vertex of a free square of tilt psi whose lowest vertex lies over the tooth span [T1.x, T2.x], against
tau = c(1 + sin(phi - psi)) (psi <= phi),  c + z tan(phi) tan(psi - phi) (psi >= phi, tan phi <= cos(psi - phi)),
c + z sin(psi - phi) otherwise."""
import math, sys, os
import numpy as np
from shapely.geometry import box as sbox
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import geom259 as Z, room259 as R

def tau(phi, psi):
    c, z = math.cos(phi), math.sin(phi)
    if psi <= phi: return c * (1 + math.sin(phi - psi))
    if math.tan(phi) <= math.cos(psi - phi): return c + z * math.tan(phi) * math.tan(psi - phi)
    return c + z * math.sin(psi - phi)

worst = 0.0
for fd in (3, 10, 14.545, 25, 33, 40, 44):
    phi = fd * Z.DEG; s = 6.0; a = 1.5
    Vs = Z.row_verts(a, phi, s, 0); c, z = math.cos(phi), math.sin(phi)
    for pd in range(0, 90, 3):
        psi = pd * Z.DEG; C_, S_ = math.cos(psi), math.sin(psi); h = (C_ + S_) / 2
        Cs = R.centre_set(Vs, s, psi)                                  # lowest vertex = q + ((S-C)/2, -(C+S)/2)
        lo, hi = a + c - (S_ - C_) / 2, a + c + 1 / c - (S_ - C_) / 2
        G = Cs.intersection(sbox(lo, 0, hi, 3.0))
        m = min(np.array(Pg.exterior.coords)[:, 1].min() for Pg in R.polys_of(G)) - h
        t = min(tau(phi, psi), c + z)                                  # never above the tips
        worst = max(worst, abs(m - t)) if m < c + z - 1e-9 else worst
        if abs(m - t) > 1e-6 and m < c + z - 1e-9: print('phi', fd, 'psi', pd, 'exact', round(m, 5), 'tau', round(t, 5))
print('max |exact - tau| where the square enters the tooth:', worst)
