"""A262 geometry: the JAM RING -- a normal ring (A259's geom259, imported, never edited) whose wall-3 END square is
replaced by a FLOATER C (free pose) meeting the BL box; wall 3 keeps its START square X only.

Parameters p = (delta_0..3, phi_0..3, cx, cy, cth) + s.   Squares, in order:
    0 A  (floor START, meets BL)   1 A2 (floor END, meets BR)   2,3 right wall   4,5 ceiling
    6 X  (left wall START, meets TL; touches x = 0 ABOVE C)     7 C  (floater: touches nothing, meets BL)
margin(p, s) = min( containment, pair gaps, tilt range, box strictness: delta_k < 1 (k = 0..3), END of walls 0..2
               meets its box, C meets the open BL box (depth), C floats (both wall distances) )   -- HARD terms only.
jam_J(p, s): A261's inner sup J over wall-touching cells (jam261.J_of, imported) on (C, A, X);  J < 0 <=> no
wall-touching cell that meets C is free of A and X (the floater is JAMMED: P1 cannot land it).
"""
import math
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
for p in ('attempts/A259-normal-room/code', 'attempts/A261-box-meeters/code'):
    sys.path.insert(0, os.path.join(ROOT, p))
import geom259 as Z                                                   # noqa: E402

SHAT, DEG = Z.SHAT, Z.DEG
BOX = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], float)
NAMES = ['A', 'A2', 'R1', 'R2', 'T1', 'T2', 'X', 'C']


def verts(p, s):
    out = []
    for k in range(3):
        out += Z.row_verts(p[k], p[4 + k], s, k)
    out.append(Z.row_verts(p[3], p[7], s, 3)[0])
    out.append(Z.sq_verts(p[8], p[9], p[10]))
    return out


def depth_in_box(V, box=BOX):
    """signed depth of the intersection of the convex polygon V with the open box: > 0 <=> they meet (= -SAT gap)."""
    return -Z.poly_gap(V, box)


WALL = [0, 0, 1, 1, 2, 2, 3, None]                                     # the wall each square touches BY CONSTRUCTION


def contain_far(V, s, wall):
    """containment margin against the walls the square does NOT touch by construction (its own wall: exactly 0)."""
    m = [V[:, 1].min(), s - V[:, 0].max(), s - V[:, 1].max(), V[:, 0].min()]
    return float(min(v for k, v in enumerate(m) if k != wall))


def terms(p, s, need_float=True):
    Vs = verts(p, s)
    t = [contain_far(V, s, WALL[i]) for i, V in enumerate(Vs)]
    for i in range(8):
        for j in range(i):
            if not (i // 2 == j // 2 and i < 6):
                t.append(Z.poly_gap(Vs[i], Vs[j]))
    for k in range(4):
        t += [p[4 + k], 45 * DEG - p[4 + k], 1.0 - p[k]]
    for k in range(3):
        t.append(p[k] + Z.span(p[4 + k]) - (s - 1.0))
    C = Vs[7]
    t.append(depth_in_box(C))
    if need_float:
        t += [float(C[:, 0].min()), float(C[:, 1].min())]
    return t, Vs


def margin(p, s, need_float=True):
    return float(min(terms(p, s, need_float)[0]))


def jam_J(Vs):
    import jam261 as J                                                 # builds the cell grid at import (JAM_COARSE)
    return J.J_of([Vs[7], Vs[0], Vs[6]])[0]


def from_local(poseA, poseC, poseX, s, phi1=None, phi2=None):
    """embed A261's local witness (corner frame = BL frame): delta_0, phi_0 from A; delta_3, phi_3 from X."""
    a_th = poseA[2]
    d0 = poseA[0] - 0.5 * (math.cos(a_th) + math.sin(a_th))
    x_th = poseX[2]
    top = poseX[1] + 0.5 * (math.cos(x_th) + math.sin(x_th))
    d3 = s - top
    f1 = a_th if phi1 is None else phi1
    f2 = a_th if phi2 is None else phi2
    return np.array([d0, 0.8, 0.8, d3, a_th, f1, f2, x_th, poseC[0], poseC[1], poseC[2]], float)


def poses(p, s):
    return [Z.pose_of(V) for V in verts(p, s)]
