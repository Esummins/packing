"""A263 geometry of the FACTORISED miss-O test (docs/proofs/open_pairs.md s.1-2).  A258 / A259 / A260 code imported,
never edited.  Corner BR of [0,s]^2; floor = wall k-1 (open pair s1, W), right wall = wall k (open pair S', W').
    floor  f = (b, fW, e, f1):  W  = toucher(s - b - w(fW), fW),  s1 = toucher(delta_W - e - sec f1, f1)      (wall 0)
    right  g = (a', f1', e', fW'):  S' = toucher(a', f1'),  W' = toucher(a' + sec f1' + e', fW')              (wall 1)
    e = the SHIFT delta_W - (a + sec f1) >= 0 (any tilts);  gamma = e + (cos fW - cos f1) tan f1 = the horizontal gap
    from W's left vertex A_W to s1's right-edge line.
REGIONS of the wall-nearest vertex P of a free square Q, per wall (wall frame, A_W = W's left vertex, T1 = s1's top):
    RIGHT: (P - A_W).uW >= 0      LEFT: (P - T1).u1 <= 0      NOTCH: the rest           (uW, u1 = the edge directions)
FACTORS (each <= 4 parameters + s, s eliminated by the corner-frame monotonicity of normal_room.md s.2.3):
    P2  corner pair, TWO squares W, S':   (i) miss to the floor, q_x >= s/2, P in RIGHT(floor)
                                          (ii) miss to the right wall, q_y <= s/2, P' in LEFT(right wall)
    WE  one wall (floor), s1, W:          (i) with P NOT in RIGHT(floor)                  END half
    WS  one wall (right), S', W':         (ii) with P' NOT in LEFT(right wall)            START half
PRINCIPAL NORMAL [T]: take n = the normal of Q with the LARGEST (q-O).n; then (i) carries (q-O).(-v) >= (q-O).u and
(ii) carries (q-O).u >= (q-O).(-v).  In the corner frame these clips relax as s grows for psi >= 0 resp. psi <= 0, and
only there are they imposed.  Without them P2 is FALSE (a 44-degree square hugging the right wall above S', where the
dropped W' stood, misses O 'to the floor' by +0.03: results/fact263_rows_v0.jsonl).
[T] (i) or (ii) at corner BR  =>  P2 or WE or WS  (dropping squares only enlarges the free set; the regions cover).
"""
import math
import os
import sys

import numpy as np
from shapely.geometry import Polygon, box as sbox

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A260-locked-wall', 'code'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A259-normal-room', 'code'))
import geom260 as H                                                   # noqa: E402
import room259 as R                                                   # noqa: E402
Z = H.Z
DEG, SHAT = Z.DEG, Z.SHAT
BIG = 9.0


def sec(f):
    return 1.0 / math.cos(f)


def floor_sq(f, s):
    b, fW, e, f1 = f
    dW = s - b - H.w_of(fW)
    return [H.toucher(dW - e - sec(f1), f1, s, 0), H.toucher(dW, fW, s, 0)]            # s1, W


def right_sq(g, s):
    a1, f1, e1, fW = g
    return [H.toucher(a1, f1, s, 1), H.toucher(a1 + sec(f1) + e1, fW, s, 1)]           # S', W'


def floor_dom(f, s, adj=True):
    """>= 0: b < 1, a in (0,1), e >= 0, tilts in (0,45], s1 / W interior-disjoint, (adj) both reach the far slot."""
    b, fW, e, f1 = f
    dW = s - b - H.w_of(fW)
    a = dW - e - sec(f1)
    V = floor_sq(f, s)
    m = min(1 - b, b, 1 - a, a, e, fW, f1, 45 * DEG - fW, 45 * DEG - f1, Z.poly_gap(V[0], V[1]))
    if adj:
        m = min(m, 2.0 - dW, a + H.w_of(f1) - (s - 2.0))
    return m


def right_dom(g, s, adj=True):
    a1, f1, e1, fW = g
    dW = a1 + sec(f1) + e1
    b1 = s - dW - H.w_of(fW)
    V = right_sq(g, s)
    m = min(1 - a1, a1, 1 - b1, b1, e1, fW, f1, 45 * DEG - fW, 45 * DEG - f1, Z.poly_gap(V[0], V[1]))
    if adj:
        m = min(m, 2.0 - dW, a1 + H.w_of(f1) - (s - 2.0))
    return m


def halfplane(p0, n):
    """the polygon {x : (x - p0).n >= 0} inside a big box."""
    n = np.array(n, float) / np.linalg.norm(n)
    t = np.array([-n[1], n[0]])
    p0 = np.array(p0, float)
    return Polygon([p0 - BIG * t, p0 + BIG * t, p0 + BIG * t + 2 * BIG * n, p0 - BIG * t + 2 * BIG * n])


def frames(s, f=None, g=None):
    """(A_W, uW) of the floor's W and (T1', u1') of the right wall's S' in container coordinates."""
    out = {}
    if f is not None:
        b, fW, e, f1 = f
        out['AW'] = np.array([s - b - H.w_of(fW), math.cos(fW)])
        out['uW'] = np.array([math.cos(fW), math.sin(fW)])
    if g is not None:
        a1, f1, e1, fW = g
        out['T1'] = np.array([s - H.w_of(f1), a1 + math.cos(f1)])         # wall frame (a' + c, w) -> (s - d, t)
        out['u1'] = np.array([-math.sin(f1), math.cos(f1)])               # wall frame (c, z) -> (-z, c)
    return out


def near_offset(psi, wall):
    """P - q for the vertex of Q (tilt psi in [-45, 45) deg) nearest the floor (wall 0) / the right wall (wall 1)."""
    u = np.array([math.cos(psi), math.sin(psi)])
    v = np.array([-math.sin(psi), math.cos(psi)])
    if wall == 0:
        return -(u + v) / 2 if psi >= 0 else (u - v) / 2
    return (u - v) / 2 if psi >= 0 else (u + v) / 2


def factor_margin(kind, s, f=None, g=None, step=1.0, psis=None, half=0.5, Vs=None, extra=()):
    """max over psi of the miss-O margin of factor `kind` in {'P2', 'WE', 'WS', 'FULL'} (< 0: the factor holds)."""
    fr = frames(s, f, g)
    if Vs is None:
        Vs = {'P2': lambda: [floor_sq(f, s)[1], right_sq(g, s)[0]], 'WE': lambda: floor_sq(f, s),
              'WS': lambda: right_sq(g, s), 'FULL': lambda: floor_sq(f, s) + right_sq(g, s)}[kind]()
    Vs = list(Vs) + list(extra)
    O = np.array([s / 2, s / 2])
    right, lower = sbox(s / 2, -1, s + 1, s + 1), sbox(-1, -1, s + 1, s / 2)
    worst, pose = -9.0, None
    psis = np.arange(-45.0, 45.0 - 1e-9, step) if psis is None else psis
    for pd in psis:
        psi = pd * DEG
        C = R.centre_set(Vs, s, psi, half)
        if C.is_empty:
            continue
        u = np.array([math.cos(psi), math.sin(psi)])
        v = np.array([-math.sin(psi), math.cos(psi)])
        cases = []
        if kind in ('P2', 'WE', 'FULL'):
            G = C.intersection(right)
            if kind == 'P2':
                G = G.intersection(halfplane(fr['AW'] - near_offset(psi, 0), fr['uW']))
            elif kind == 'WE':
                G = G.intersection(halfplane(fr['AW'] - near_offset(psi, 0), -fr['uW']))
            if psi >= 0:                                              # PRINCIPAL-NORMAL clip [T, s-monotone for psi >= 0]
                G = G.intersection(halfplane(O, -v - u))
            cases.append((G, -v, 'i'))
        if kind in ('P2', 'WS', 'FULL'):
            G = C.intersection(lower)
            if kind == 'P2':
                G = G.intersection(halfplane(fr['T1'] - near_offset(psi, 1), -fr['u1']))
            elif kind == 'WS':
                G = G.intersection(halfplane(fr['T1'] - near_offset(psi, 1), fr['u1']))
            if psi <= 0:                                              # PRINCIPAL-NORMAL clip [T, s-monotone for psi <= 0]
                G = G.intersection(halfplane(O, u + v))
            cases.append((G, u, 'ii'))
        for G, n, tag in cases:
            for Pg in R.polys_of(G):
                A = np.array(Pg.exterior.coords)[:-1]
                val = (A - O) @ n
                i = int(val.argmax())
                if val[i] - 0.5 > worst:
                    worst, pose = float(val[i] - 0.5), (float(A[i, 0]), float(A[i, 1]), psi, tag)
    return worst, pose


def corner_of_ring(x, s, k):
    """hybrid ring x (geom260: (a, f1, b, fW) per wall): the corner between wall k (as floor) and wall k+1 (right)."""
    a, f1, b, fW = x[4 * k:4 * k + 4]
    k1 = (k + 1) % 4
    a1, g1, b1, gW = x[4 * k1:4 * k1 + 4]
    return (b, fW, H.shift(a, f1, b, fW, s), f1), (a1, g1, H.shift(a1, g1, b1, gW, s), gW)


def gamma_of(e, f1, fW):
    return e + (math.cos(fW) - math.cos(f1)) * math.tan(f1)


if __name__ == '__main__':
    s = SHAT
    f = (0.85, 14 * DEG, 0.05, 10 * DEG)
    g = (0.8, 16 * DEG, 0.03, 12 * DEG)
    print('dom', floor_dom(f, s), right_dom(g, s))
    for kind in ('FULL', 'P2', 'WE', 'WS'):
        print(kind, factor_margin(kind, s, f, g, 3.0))
