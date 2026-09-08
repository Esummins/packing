"""A155 -- vectorised float geometry for the corner band (unit squares only).

Three primitives, all on numpy arrays of poses (cx, cy, th_deg):

    fmm(cx, cy, th)            min over Q(c, th) of max(x, y).  Q meets the OPEN box [0, a)^2
                               iff fmm < a.  (A143 `cells143.f_min_max` in floats; the exact
                               rational version is used as a cross-check on a sample.)
    in_container(cx, cy, th)   Q(c, th) subset [0, s0]^2.
    sat_gap(p, q)              max over the four edge normals of (|dc.n| - h_p(n) - h_q(n)).
                               > 0  <=>  the two unit squares have disjoint interiors with a
                               positive separating gap (A148 `geo148.sat_gap` convention).

Floats are used only where a float answer is a WITNESS (a drawn 2-crowd) or a diagnostic
(occupancy sampling); every SOUND kill in A155 goes through A132's exact polygon cores, exactly
as in A143/A150.
"""
import numpy as np

SQ2H = float(np.sqrt(0.5))


def _verts(cx, cy, th):
    """(..., 4, 2) vertices of the unit square at (cx, cy) tilted th degrees."""
    t = np.radians(th)
    co, si = np.cos(t), np.sin(t)
    e1 = np.stack([0.5 * co, 0.5 * si], -1)
    e2 = np.stack([-0.5 * si, 0.5 * co], -1)
    c = np.stack([cx, cy], -1)
    return np.stack([c + e1 + e2, c + e1 - e2, c - e1 - e2, c - e1 + e2], -2)


def fmm(cx, cy, th):
    """min over the square of max(x, y) -- float version of cells155.f_min_max."""
    V = _verts(cx, cy, th)
    best = np.max(V, axis=-1).min(-1)
    for i in range(4):
        p = V[..., i, :]
        q = V[..., (i + 1) % 4, :]
        d = q - p
        den = d[..., 0] - d[..., 1]
        with np.errstate(divide="ignore", invalid="ignore"):
            s = (p[..., 1] - p[..., 0]) / den
        val = p[..., 0] + s * d[..., 0]
        ok = np.isfinite(s) & (s >= 0.0) & (s <= 1.0)
        best = np.where(ok, np.minimum(best, val), best)
    return best


def half_extent(th):
    t = np.radians(th)
    return 0.5 * (np.abs(np.cos(t)) + np.abs(np.sin(t)))


def in_container(cx, cy, th, s):
    h = half_extent(th)
    return (cx >= h) & (cx <= s - h) & (cy >= h) & (cy <= s - h)


def sat_gap(c1, t1, c2, t2):
    """c1, c2 : (..., 2) centres; t1, t2 : (...) tilts in degrees.  Returns the SAT gap."""
    d = c2 - c1
    best = None
    for (t, k) in ((t1, 0), (t1, 1), (t2, 0), (t2, 1)):
        a = np.radians(t) + (0.5 * np.pi if k else 0.0)
        n = np.stack([np.cos(a), np.sin(a)], -1)
        proj = np.abs((d * n).sum(-1))
        # half-width of a unit square at tilt u projected on the axis at angle a
        h1 = 0.5 * (np.abs(np.cos(np.radians(t1) - a)) + np.abs(np.sin(np.radians(t1) - a)))
        h2 = 0.5 * (np.abs(np.cos(np.radians(t2) - a)) + np.abs(np.sin(np.radians(t2) - a)))
        g = proj - h1 - h2
        best = g if best is None else np.maximum(best, g)
    return best
