#!/usr/bin/env python3
"""clip_util.py -- A46 task 5: exact tile clipping + the wall disjointification.

The task-2 tiles of a WC entry live in the contact frame with the contact point
at p = (10, 0) on the bottom wall and the wall along y = 0.  In a real packing
a WC contact at along-wall coordinate X is the isometric image of that frame
(Lemma P: the certificate transports).  So the contact's dead region occupies
the along-wall interval [X - 13/8, X + 13/8] intersected with its Lemma-K slab,
and the height interval [0, 5/4].

DISJOINTIFICATION USED (task 5):

  (a) SAME WALL.  Order the WC contact points along the wall, X_1 < ... < X_r.
      Truncate contact i's region to its along-wall VORONOI interval
      [ (X_{i-1}+X_i)/2 , (X_i+X_{i+1})/2 ]  (half-gaps; unbounded at the ends,
      clipped to the wall).  Voronoi cells are pairwise disjoint, so the
      truncated regions are pairwise interior-disjoint.  Truncation only
      removes area, so the sum stays a certified lower bound.
      `clip_x(cells, x_lo, x_hi)` computes the truncated area exactly, in the
      frame (x_lo, x_hi are offsets from p, i.e. relative coordinates).

  (b) DIFFERENT WALLS.  Every kept tile of a WC entry lies within height
      5/4 of its own wall (window cap) -- in fact within min(cos+sin) <= sqrt2.
      Two OPPOSITE walls: their slabs are disjoint because 2*(5/4) = 5/2 < s0.
      Two ADJACENT walls: the slabs intersect exactly in the corner square of
      side 5/4.  Handled by the CORNER DEDUCTION: subtract, once per container
      corner, the area of the smaller of the two regions restricted to that
      corner box.  `corner_overlap(cells, ...)` computes it exactly.  A cruder
      but simpler sound option, also implemented, is to truncate each region to
      its own wall's half of the corner box (the diagonal split), which makes
      adjacent-wall regions exactly disjoint with no deduction.

All arithmetic is exact Fractions.
"""
from __future__ import annotations

from fractions import Fraction as F


def clip_rect(cells, x0, y0, x1, y1):
    """(exact area, clipped tiles) of `cells` inside [x0,x1] x [y0,y1]."""
    a = F(0)
    out = []
    for (u0, v0, u1, v1) in cells:
        p0, p1 = max(u0, x0), min(u1, x1)
        q0, q1 = max(v0, y0), min(v1, y1)
        if p1 > p0 and q1 > q0:
            a += (p1 - p0) * (q1 - q0)
            out.append((p0, q0, p1, q1))
    return a, out


def clip_x(cells, px, x_lo, x_hi):
    """exact area of `cells` whose along-wall offset from px lies in
    [x_lo, x_hi] (x_lo may be -inf via a very negative Fraction)."""
    a = F(0)
    for (u0, v0, u1, v1) in cells:
        p0, p1 = max(u0, px + x_lo), min(u1, px + x_hi)
        if p1 > p0:
            a += (p1 - p0) * (v1 - v0)
    return a


def voronoi_intervals(xs, wall_lo, wall_hi):
    """half-gap Voronoi intervals of sorted along-wall positions xs."""
    xs = sorted(xs)
    out = []
    for i, x in enumerate(xs):
        lo = wall_lo if i == 0 else (xs[i - 1] + x) / 2
        hi = wall_hi if i == len(xs) - 1 else (x + xs[i + 1]) / 2
        out.append((lo, hi))
    return out


def wall_profile_sum(cells, px, xs, wall_lo, wall_hi):
    """Total certified dead area of r WC contacts on ONE wall at along-wall
    positions xs, after Voronoi truncation.  `cells` is the frame tile list
    (all contacts assumed to use the same phi-bin entry; pass a list of tile
    lists for mixed bins)."""
    if not isinstance(cells, list) or (cells and isinstance(cells[0], tuple)):
        cells = [cells] * len(xs)
    iv = voronoi_intervals(xs, wall_lo, wall_hi)
    tot = F(0)
    per = []
    for cl, x, (lo, hi) in zip(cells, sorted(xs), iv):
        a = clip_x(cl, px, lo - x, hi - x)
        per.append(a)
        tot += a
    return tot, per


def corner_overlap(cells_a, px_a, cells_b, px_b, side=F(5, 4)):
    """Area each region can put inside a shared container-corner box of side
    `side` (the two adjacent slabs' intersection).  Returns (a_in, b_in); the
    sound deduction is min(a_in, b_in)."""
    a, _ = clip_rect(cells_a, px_a - side, F(0), px_a + side, side)
    b, _ = clip_rect(cells_b, px_b - side, F(0), px_b + side, side)
    return a, b


def diagonal_split_area(cells, px, corner_x, side=F(5, 4)):
    """Sound alternative to a deduction: keep only the part of the region on
    its OWN side of the corner box's diagonal.  Implemented tile-wise and
    conservatively: a tile is kept whole iff it lies entirely outside the
    corner box or entirely on the own-wall side of the diagonal y <= |x - cx|;
    otherwise it is dropped.  Lower bound, exact."""
    a = F(0)
    for (u0, v0, u1, v1) in cells:
        # corner box = [corner_x - side, corner_x + side] x [0, side] but only
        # the half nearest the corner matters; the diagonal through the corner
        # is y = |x - corner_x|.
        far = min(abs(u0 - corner_x), abs(u1 - corner_x)) if \
            (u0 - corner_x) * (u1 - corner_x) > 0 else F(0)
        if v1 <= far:                       # entirely below the diagonal
            a += (u1 - u0) * (v1 - v0)
        elif min(abs(u0 - corner_x), abs(u1 - corner_x)) >= side:
            a += (u1 - u0) * (v1 - v0)      # entirely outside the corner box
    return a
