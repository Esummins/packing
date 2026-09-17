"""A251 task 1: the ALL-ADJ RING FAMILY, parametrised exactly, and its parameter BOXES.

Parameters (A249 twotilted249, mode 'ring'): per corner c in (BL, BR, TR, TL) the wall meeter's
(theta_B, delta_B) and the floor / side meeter's (theta_A, delta_A) in that corner's frame, plus the
side s -- 17 coordinates.  Constraints (the all-ADJ type-T ring of `type_t_chase.md` s.2.3):

    0 < theta < pi/2,  delta > 0                       (tilted, not wedged: WEDGED-SEAL)
    delta_B < 1, delta_A < 1                           (T-CELLS: both meeters meet their corner box)
    delta_B + w(theta_B) > s - 2                       (B reaches the far slot of its wall: all-ADJ)
    delta_A + w(theta_A) > s - 2                       (mirror)
    the eight squares pairwise interior-disjoint and inside [0, s]^2
    s in [3.82, 4)

so delta in (max(0, s - 2 - w(theta)), 1) and, since w <= sqrt2, delta > s - 2 - sqrt2 >= 0.406 on
the window: **a bounded box in 17 coordinates**, [0, pi/2]^8 x [0.40, 1]^8 x [3.82, 4].

[T] Lemma GAP (any n, s < 4).  The two touchers of one wall have wall extents [a0, a0 + wA] from
one end and [b0, b0 + wB] from the other, both reaching past s - 2; so their extents leave a gap of
length < 4 - s (0.18 on the window) or overlap: (delta + w) + (delta' + w') > 2s - 4 gives
gap = s - (delta + w) - (delta' + w') < 4 - s.  The wall is uncovered only on [0, delta] and
[s - delta', s] with delta, delta' < 1 -- the two corner notches -- plus that middle gap.

D4: the family and the capacity of its pocket are invariant under the eight symmetries of the
square (they permute the corners and swap the roles A <-> B), so a fundamental domain divides the
box count by at most 8 -- irrelevant against the product law (cert251).
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A249-type-t-chase', 'code'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A248-corner-chase', 'code'))
sys.path.insert(0, HERE)
import twotilted249 as W                                              # noqa: E402
import geom248 as G                                                   # noqa: E402
import geom251 as C251                                                # noqa: E402

HALF = math.pi / 2
CORNERS = ('BL', 'BR', 'TR', 'TL')
KAPPA = {'BL': 0.0, 'BR': 1.0, 'TR': math.sqrt(2.0), 'TL': 1.0}       # |d placement / d s|
NPAIR, NCONT, NTILT, NDELTA = 28, 8, 8, 8                             # term blocks of ring_margin
DELTA_LO = 3.82 - 2.0 - math.sqrt(2.0)


def bounds(s_lo=3.82, s_hi=4.0):
    """the 17 coordinate ranges (theta, delta interleaved per corner, then s)."""
    b = []
    for _ in CORNERS:
        b += [(0.0, HALF), (max(0.0, DELTA_LO), 1.0), (0.0, HALF), (max(0.0, DELTA_LO), 1.0)]
    return b + [(s_lo, s_hi)]


def poses_of(x, s):
    """the eight (cx, cy, theta) poses and their names, and the per-member kappa."""
    polys, names, _ = W.ring_polys(list(x), s, False)
    return [tuple(map(float, G.pose_of(V))) for V in polys], names, \
        [KAPPA[n.split('_')[1]] for n in names]


def deviations(rad):
    """(rho_i, dtheta_i) for the eight members from the box half-widths rad (17 numbers).
    rho <= LIP_C_THETA * dtheta + ddelta + kappa * ds  (centre displacement, Euclidean);
    dtheta is the parameter's own half-width."""
    ds = rad[16]
    rhos, dths = [], []
    for k, c in enumerate(CORNERS):
        for j in (0, 2):                                              # B then A of this corner
            dth, dde = rad[4 * k + j], rad[4 * k + j + 1]
            rhos.append(C251.LIP_C_THETA * dth + dde + KAPPA[c] * ds)
            dths.append(dth)
    # ring_polys orders the members B_BL, A_BL, B_BR, A_BR, ... -- matches the (0, 2) loop above
    return rhos, dths


def max_vertex_disp(rad):
    ds = rad[16]
    out = 0.0
    for k, c in enumerate(CORNERS):
        for j in (0, 2):
            out = max(out, C251.LIP_V_THETA * rad[4 * k + j] + rad[4 * k + j + 1] + KAPPA[c] * ds)
    return out


def local_vertex_disp(rad):
    """vertex displacement in the corner's OWN frame (no placement, so no kappa)."""
    return max(C251.LIP_V_THETA * rad[4 * k + j] + rad[4 * k + j + 1]
               for k in range(4) for j in (0, 2))


def margin_terms(x, s):
    return W.ring_margin(list(x), s, False, True)


def margin(x, s):
    return W.ring_margin(list(x), s, False)


def margin_ub(xc, rad):
    """a SOUND upper bound on the ring family's feasibility margin over the box centred at
    (xc, s = xc[16]) with half-widths rad: per term class, min term + its Lipschitz bump.
    margin_ub < 0 proves the box holds NO ring of the family (it may be discarded)."""
    s = xc[16]
    t = margin_terms(xc[:16], s)
    dv, dl, ds = max_vertex_disp(rad), local_vertex_disp(rad), rad[16]
    i = 0
    ub = min(t[i:i + NPAIR]) + 2.0 * dv
    i += NPAIR
    ub = min(ub, min(t[i:i + NCONT]) + 10.0 * (dv + ds))
    i += NCONT
    ub = min(ub, min(t[i:i + NTILT]) + max(rad[4 * k + j] for k in range(4) for j in (0, 2)))
    i += NTILT
    ub = min(ub, min(t[i:i + NDELTA]) + max(rad[4 * k + j] for k in range(4) for j in (1, 3)))
    i += NDELTA
    ub = min(ub, min(t[i:]) + dl + ds)
    return float(ub)


def sample_rings(s, restarts=40, seed=251, maxiter=20000, sym_seed=None):
    """feasible rings at side s: Nelder-Mead sup-margin restarts, every local optimum with
    margin > 0 kept (deduplicated by the pose multiset)."""
    rng = np.random.default_rng(seed)
    out = []
    for k in range(restarts):
        if sym_seed is not None and k == 0:
            x0 = list(sym_seed[:4]) + list(sym_seed[4:8]) + list(sym_seed[:4]) + list(sym_seed[4:8])
        else:
            x0 = W.random_start(rng, 4, k % 3)
        from scipy.optimize import minimize
        r = minimize(lambda z: -margin(z, s), x0, method='Nelder-Mead',
                     options={'xatol': 1e-10, 'fatol': 1e-12, 'maxiter': maxiter, 'adaptive': True})
        x = W.polish(lambda z, ss, t=False: W.ring_margin(z, ss, False, t), r.x, s)
        m = margin(x, s)
        if m > 0:
            key = tuple(sorted(round(v, 3) for v in poses_of(x, s)[0][0]))
            if all(abs(m - o['margin']) > 1e-6 or key != o['key'] for o in out):
                out.append({'margin': float(m), 'x': [float(v) for v in x], 'key': key})
    out.sort(key=lambda r: -r['margin'])
    return out


def gap_lemma(x, s):
    """[T] Lemma GAP, measured: per wall the two touchers' extents and the gap (< 4 - s)."""
    rows = []
    for k, c in enumerate(CORNERS):
        tB, dB, tA, dA = x[4 * k:4 * k + 4]
        rows.append({'corner': c, 'wall_B': [dB, dB + G.w(tB)], 'floor_A': [dA, dA + G.w(tA)],
                     'reach_B': dB + G.w(tB) - (s - 2), 'reach_A': dA + G.w(tA) - (s - 2)})
    walls = []
    pairs = {'x=0': ('BL', 'B', 'TL', 'B'), 'y=0': ('BL', 'A', 'BR', 'A'),
             'x=s': ('BR', 'B', 'TR', 'B'), 'y=s': ('TL', 'A', 'TR', 'A')}
    for wname, (c1, r1, c2, r2) in pairs.items():
        i1, i2 = CORNERS.index(c1), CORNERS.index(c2)
        e1 = x[4 * i1 + (0 if r1 == 'B' else 2)], x[4 * i1 + (1 if r1 == 'B' else 3)]
        e2 = x[4 * i2 + (0 if r2 == 'B' else 2)], x[4 * i2 + (1 if r2 == 'B' else 3)]
        a, b = e1[1] + G.w(e1[0]), e2[1] + G.w(e2[0])
        walls.append({'wall': wname, 'gap': float(s - a - b), 'bound': float(4.0 - s),
                      'ok': bool(s - a - b < 4.0 - s + 1e-9)})
    return {'corners': rows, 'walls': walls}


if __name__ == '__main__':
    s = 3.877084
    seed = [0.254, 0.891, 0.254, 0.695, 1.317, 0.695, 1.317, 0.891]
    x = list(seed[:4]) + list(seed[4:8]) + list(seed[:4]) + list(seed[4:8])
    print('seed margin %+.5f' % margin(x, s))
    rad = [0.0] * 17
    print('margin_ub at radius 0: %+.5f' % margin_ub(x + [s], rad))
    for r in (0.001, 0.01, 0.05):
        print('  radius %.3f -> ub %+.5f' % (r, margin_ub(x + [s], [r] * 17)))
    print(gap_lemma(x, s)['walls'])
