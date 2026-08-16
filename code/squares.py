"""
squares.py -- shared geometry for the unit-square packing lab.

A unit square is described by (cx, cy, theta): centre and rotation angle (radians,
counter-clockwise).  Its corners are  c + R(theta) * (+-1/2, +-1/2).

Functions
---------
corners(cx, cy, theta)                 -> (4,2) array of corner coordinates
all_corners(X)                         -> (n,4,2) for X of shape (n,3)
axes(theta)                            -> (2,2) unit edge normals of a square (rows)
sat_separation(A, B, thA, thB)         -> signed separation between two squares:
                                          > 0 : squares are disjoint, value = largest gap
                                                over the 4 candidate separating axes
                                          < 0 : squares overlap, |value| = penetration depth
                                                (min over axes of the projection overlap)
                                          also returns the axis (as unit vector) realising it
pair_separations(X)                    -> vector of signed separations for all pairs i<j
containment_margin(X, s)               -> (n,) smallest distance of any corner of each square
                                          to the boundary of [0,s]^2 (negative if outside)
wall_gaps(X, s)                        -> (n,4) gaps of each square to walls x=0, y=0, x=s, y=s
is_valid(X, s, tol=0.0)                -> True iff all separations and margins >= tol
plot_packing(X, s, ax=None, ...)       -> matplotlib drawing (labels, optional contacts)

Conventions: X is an (n,3) float array with rows (cx, cy, theta).  Everything here is
floating point and intended for search / diagnostics.  Exact verification is done by
certs/verify_certificate.py (Fractions).

Author: A03-upper-reconstruct.  Free for other attempts to import:
    import sys; sys.path.insert(0, 'code'); from squares import *
"""
from __future__ import annotations

import itertools
import math

import numpy as np

_HALF = np.array([[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]])


def corners(cx: float, cy: float, theta: float) -> np.ndarray:
    """Corners of the unit square centred at (cx,cy) rotated by theta (CCW order,
    starting at the corner that is (-1/2,-1/2) in the square's own frame)."""
    c, s = math.cos(theta), math.sin(theta)
    R = np.array([[c, -s], [s, c]])
    return np.array([cx, cy]) + _HALF @ R.T


def all_corners(X: np.ndarray) -> np.ndarray:
    """(n,3) -> (n,4,2) corner array (vectorised)."""
    X = np.asarray(X, dtype=float)
    c, s = np.cos(X[:, 2]), np.sin(X[:, 2])
    R = np.empty((len(X), 2, 2))
    R[:, 0, 0] = c
    R[:, 0, 1] = -s
    R[:, 1, 0] = s
    R[:, 1, 1] = c
    return X[:, None, :2] + np.einsum('kj,nij->nki', _HALF, R)


def axes(theta: float) -> np.ndarray:
    """The two unit edge normals (cos t, sin t) and (-sin t, cos t) as rows."""
    c, s = math.cos(theta), math.sin(theta)
    return np.array([[c, s], [-s, c]])


def sat_separation(A: np.ndarray, B: np.ndarray, thA: float, thB: float):
    """Signed separation of two convex quadrilaterals given by corner arrays A,B (4,2)
    using the 4 candidate axes (edge normals of both squares).

    Returns (sep, axis).  sep > 0 means the projections onto `axis` are disjoint with gap
    `sep` (hence the squares are disjoint); sep < 0 means every axis shows overlap and
    -sep is the minimum overlap (a penetration depth).  Squares touching have sep == 0.
    """
    best = -np.inf
    best_axis = None
    for ax in np.vstack([axes(thA), axes(thB)]):
        pa = A @ ax
        pb = B @ ax
        gap = max(pb.min() - pa.max(), pa.min() - pb.max())
        if gap > best:
            best, best_axis = gap, ax
    return best, best_axis


def _pair_index(n: int):
    return np.array(list(itertools.combinations(range(n), 2)))


def pair_separations(X: np.ndarray) -> np.ndarray:
    """Signed SAT separations for all pairs i<j (order of itertools.combinations)."""
    X = np.asarray(X, dtype=float)
    n = len(X)
    C = all_corners(X)                       # (n,4,2)
    c, s = np.cos(X[:, 2]), np.sin(X[:, 2])
    N = np.stack([np.stack([c, s], -1), np.stack([-s, c], -1)], 1)   # (n,2,2) normals
    P = _pair_index(n)
    i, j = P[:, 0], P[:, 1]
    # axes: 4 per pair
    AX = np.concatenate([N[i], N[j]], axis=1)          # (m,4,2)
    pi = np.einsum('mkd,mad->mak', C[i], AX)           # (m,4axes,4corners)
    pj = np.einsum('mkd,mad->mak', C[j], AX)
    gap = np.maximum(pj.min(2) - pi.max(2), pi.min(2) - pj.max(2))   # (m,4)
    return gap.max(1)


def containment_margin(X: np.ndarray, s: float) -> np.ndarray:
    """For each square, min over its corners of the distance to the boundary of [0,s]^2
    (negative if a corner sticks out)."""
    C = all_corners(X)
    m = np.minimum(np.minimum(C[..., 0], C[..., 1]),
                   np.minimum(s - C[..., 0], s - C[..., 1]))
    return m.min(1)


def wall_gaps(X: np.ndarray, s: float) -> np.ndarray:
    """(n,4) array: distance of each square to the walls x=0, y=0, x=s, y=s."""
    C = all_corners(X)
    return np.stack([C[..., 0].min(1), C[..., 1].min(1),
                     s - C[..., 0].max(1), s - C[..., 1].max(1)], 1)


def is_valid(X: np.ndarray, s: float, tol: float = 0.0) -> bool:
    """True iff every pair separation and every containment margin is >= tol."""
    return bool(pair_separations(X).min() >= tol and containment_margin(X, s).min() >= tol)


def normalise_angles(X: np.ndarray) -> np.ndarray:
    """Return a copy with every angle reduced to [0, pi/2) (square symmetry)."""
    Y = np.array(X, dtype=float)
    Y[:, 2] = np.mod(Y[:, 2], math.pi / 2)
    return Y


def plot_packing(X, s, ax=None, labels=True, contacts=None, title=None, colors=None):
    """Draw the packing.  `contacts` (optional): iterable of (x,y) points to mark.
    Returns the matplotlib Axes."""
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon, Rectangle
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 7))
    X = np.asarray(X, dtype=float)
    ax.add_patch(Rectangle((0, 0), s, s, fill=False, lw=2, ec='black'))
    for k, (cx, cy, th) in enumerate(X):
        upright = abs(math.sin(2 * th)) < 1e-6
        col = (colors[k] if colors is not None else ('#e8d3a0' if upright else '#9ec5e8'))
        ax.add_patch(Polygon(corners(cx, cy, th), closed=True, fc=col, ec='k', lw=1))
        if labels:
            ax.text(cx, cy, str(k), ha='center', va='center', fontsize=11)
    if contacts is not None:
        for (px, py) in contacts:
            ax.plot(px, py, 'o', color='red', ms=4)
    ax.set_xlim(-0.05 * s, 1.05 * s)
    ax.set_ylim(-0.05 * s, 1.05 * s)
    ax.set_aspect('equal')
    if title:
        ax.set_title(title)
    return ax
