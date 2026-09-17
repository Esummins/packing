"""A249: n-general geometry of a TYPE-T corner (both meeters tilted) seen from one of its walls.

Corner frame (A248 geom248): the shared wall is u = 0, the corner c at the origin, the floor v = 0;
cells c00 = (0,1)^2, c01 = (0,1)x(1,2) up the wall, c10 = (1,2)x(0,1) along the floor; c' = (0, s).
WALL square B (touching the wall, tilt theta_B = angle of its edge leaving the wall vertex L,
measured from the horizontal, in (0, 90 deg)): L = (0, delta_B + cos t), V = (sin t, delta_B)
(lowest vertex, delta_B = its height above the floor), R = V + (cos t, sin t), T = L + (cos t, sin t).
FLOOR square A (touching the floor, tilt theta_A = angle of the edge leaving its lowest vertex V_A
to the right): V_A = (delta_A + sin t, 0), W_A = (delta_A, cos t) (leftmost, delta_A = its offset
from the wall), R_A = V_A + (cos t, sin t), T_A = W_A + (cos t, sin t).
The mirror u <-> v maps (theta_B, delta_B) to (90 deg - theta_A, delta_A).
Off-wall versions: xi (B's distance from the wall), eta (A's height above the floor).
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A248-corner-chase', 'code'))
import geom248 as G                                                   # noqa: E402

TOL = 1e-9
CELLS_C = {'c00': (0, 1, 0, 1), 'c01': (0, 1, 1, 2), 'c10': (1, 2, 0, 1)}


# ---------------------------------------------------------------- the two squares
def wall_square(theta, delta_B, xi=0.0):
    """B: wall vertex L = (xi, delta_B + cos theta), lowest vertex V = L + (sin, -cos)."""
    si, co = math.sin(theta), math.cos(theta)
    L = np.array([xi, delta_B + co])
    V = L + (si, -co)
    return np.array([V, V + (co, si), V + (co - si, si + co), L])      # V, R, T, L


def floor_square(theta, delta_A, eta=0.0):
    """A: lowest vertex V_A = (delta_A + sin theta, eta), leftmost W_A = (delta_A, eta + cos theta)."""
    si, co = math.sin(theta), math.cos(theta)
    V = np.array([delta_A + si, eta])
    return np.array([V, V + (co, si), V + (co - si, si + co), V + (-si, co)])   # V, R, T, W


# ---------------------------------------------------------------- the closed-form cell predicates
def B_meets_c00(theta, delta_B):
    return delta_B < 1


def B_meets_c01(theta, delta_B):
    """the top vertex T = (cos t, delta_B + sin t + cos t) is above height 1 (always for delta_B > 0)."""
    return delta_B + math.sin(theta) + math.cos(theta) > 1


def B_meets_c10(theta, delta_B):
    """B's lower edge V->R crosses u = 1 below height 1."""
    return delta_B + (1 - math.sin(theta)) * math.tan(theta) < 1


def A_meets_c00(theta, delta_A):
    return delta_A < 1


def A_meets_c10(theta, delta_A):
    return delta_A + math.sin(theta) + math.cos(theta) > 1


def A_meets_c01(theta, delta_A):
    """A's left edge W->T crosses height 1 left of u = 1: u_A(1) = delta_A + (1 - cos t) cot t < 1."""
    return u_A_at_1(theta, delta_A) < 1


def u_A_at_1(theta, delta_A):
    return delta_A + (1 - math.cos(theta)) / math.tan(theta)


def u_B_at_1(theta, delta_B):
    """abscissa where B's lower edge V->R crosses height 1 (B's cap lies left of it)."""
    return math.sin(theta) + (1 - delta_B) / math.tan(theta)


def wall_range(theta, delta_B):
    """B's extent along the wall: [delta_B, delta_B + w(theta)]."""
    return delta_B, delta_B + G.w(theta)


def floor_range(theta, delta_A):
    return delta_A, delta_A + G.w(theta)


# ---------------------------------------------------------------- reading a corner view
def frame_params(P, kind):
    """(theta, offset, gap) of a square P (vertex array in the corner frame) read as a wall
    square (kind 'B': theta = frame tilt of the edge leaving the leftmost vertex upward, offset =
    height of the lowest vertex, gap = distance of the leftmost vertex from the wall) or as a
    floor square ('A': theta = angle of the edge leaving the lowest vertex to the right, offset =
    abscissa of the leftmost vertex, gap = height of the lowest vertex)."""
    if kind == 'A':
        th, V = G.frame_tilt(P)
        W = P[int(np.argmin(P[:, 0]))]
        return th, float(W[0]), float(V[1])
    # B: mirror the square (u <-> v) and read it as an A
    Q = np.stack([P[:, 1], P[:, 0]], axis=1)
    th, delta, gap = frame_params(Q, 'A')
    return math.pi / 2 - th, delta, gap


def cell_touch(V, s, tol=1e-7):
    return {'floor': G.touches(V, 'v', s, tol), 'wall': G.touches(V, 'u', s, tol)}


def centre_cell(V):
    c = V.mean(axis=0)
    return ('S' if c[1] < 1 else 'N') + ('W' if c[0] < 1 else 'E')


def role_of_pair(P, Q, s):
    """assign the roles (A = floor side, B = wall side) to two tilted meeters of c00: a wall
    toucher is B, a floor toucher is A; otherwise by the centre cells (NW -> B, SE -> A), then
    by which is nearer its wall.  Returns (A, B, how)."""
    tP, tQ = cell_touch(P, s), cell_touch(Q, s)
    if tP['wall'] and not tQ['wall']:
        return Q, P, 'touch'
    if tQ['wall'] and not tP['wall']:
        return P, Q, 'touch'
    if tP['floor'] and not tQ['floor']:
        return P, Q, 'touch'
    if tQ['floor'] and not tP['floor']:
        return Q, P, 'touch'
    cP, cQ = centre_cell(P), centre_cell(Q)
    if cP == 'NW' or cQ == 'SE':
        return Q, P, 'cell'
    if cQ == 'NW' or cP == 'SE':
        return P, Q, 'cell'
    # both untouching, cells {SW, NE} or alike: the one nearer the wall is B
    return (P, Q, 'near') if P[:, 0].min() > Q[:, 0].min() else (Q, P, 'near')


def type_t_record(A, B, s):
    """the type-T corner's parameters and its predicted / measured cells."""
    tA, dA, eA = frame_params(A, 'A')
    tB, dB, xB = frame_params(B, 'B')
    rec = {'theta_A': math.degrees(tA), 'delta_A': dA, 'eta_A': eA,
           'theta_B': math.degrees(tB), 'delta_B': dB, 'xi_B': xB,
           'A_touch': cell_touch(A, s), 'B_touch': cell_touch(B, s),
           'A_cell': centre_cell(A), 'B_cell': centre_cell(B),
           'gap_AB': float(G.poly_gap(A, B)),
           'd_A': G.depth_corner(A), 'd_B': G.depth_corner(B),
           'cells_A': {k: float(G.depth_rect(A, r)) for k, r in CELLS_C.items()},
           'cells_B': {k: float(G.depth_rect(B, r)) for k, r in CELLS_C.items()}}
    if rec['B_touch']['wall'] and not rec['B_touch']['floor']:
        rec['pred_B'] = {'c00': B_meets_c00(tB, dB), 'c01': B_meets_c01(tB, dB), 'c10': B_meets_c10(tB, dB)}
        rec['uB1'] = u_B_at_1(tB, dB) if dB < 1 else None
    if rec['A_touch']['floor'] and not rec['A_touch']['wall']:
        rec['pred_A'] = {'c00': A_meets_c00(tA, dA), 'c01': A_meets_c01(tA, dA), 'c10': A_meets_c10(tA, dA)}
        rec['uA1'] = u_A_at_1(tA, dA)
    rec['A_reach'] = float(A[:, 0].max())          # along the floor
    rec['B_reach'] = float(B[:, 1].max())          # along the wall
    return rec


def exact_check(A, B, s, tol=TOL):
    """(disjoint, in container) of two vertex arrays."""
    inside = min(A.min(), B.min()) >= -tol and max(A.max(), B.max()) <= s + tol
    return G.poly_gap(A, B) >= -tol, inside


if __name__ == '__main__':
    B = wall_square(math.radians(30), 0.6)
    A = floor_square(math.radians(40), 0.7)
    print(type_t_record(A, B, 3.85))
