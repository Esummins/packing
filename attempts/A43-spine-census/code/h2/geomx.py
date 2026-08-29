#!/usr/bin/env python3
"""A43-H2: realized-configuration geometry -- contact extraction, wall masks,
shortest wall-to-wall path enumeration, and spine typing of a REALIZED packing.

Used only by the canaries (Trump, A37 valleys).  Float geometry with an explicit
tolerance TOL; every realized configuration here is a numerically exact solution
of its own contact system, so TOL = 1e-6 is far above the residual (Trump's
certificate is exact to 1e-11, A37's z_center to ~1e-12) and far below the
smallest genuine gap (A35 measured the min non-contact gap of Trump at 0.024875).
"""
from __future__ import annotations

import math

TOL = 1e-6
# corner order matches A37/A31: k=0..3 -> (+,+), (-,+), (-,-), (+,-) half-offsets
HALF = [(0.5, 0.5), (-0.5, 0.5), (-0.5, -0.5), (0.5, -0.5)]


class Config:
    """A realized packing: squares (cx, cy, theta_rad) inside [0, s]^2."""

    def __init__(self, sq, s, name='', tol=TOL, eps_phi=1e-7, eps_pos=1e-6):
        self.s = float(s)
        self.name = name
        self.tol = float(tol)
        self.eps_phi = float(eps_phi)
        self.eps_pos = float(eps_pos)
        self.sq = [(float(a), float(b), float(c)) for a, b, c in sq]
        self.n = len(self.sq)
        self.pts = []
        for cx, cy, th in self.sq:
            c, sn = math.cos(th), math.sin(th)
            self.pts.append([(cx + a * c - b * sn, cy + a * sn + b * c)
                             for a, b in HALF])

    def swap_axes(self):
        """Reflect (x, y) -> (y, x); theta -> -theta.  Turns the y-axis spine
        problem into the x-axis one.  (A packing of the same container.)"""
        sq = [(cy, cx, -th) for cx, cy, th in self.sq]
        return Config(sq, self.s, self.name + '|swap', self.tol,
                      self.eps_phi, self.eps_pos)

    def phi(self, i):
        d = math.degrees(self.sq[i][2]) % 90.0
        if d > 90.0 - self.eps_phi:
            d -= 90.0
        if abs(d) < self.eps_phi:
            d = 0.0
        return d if d >= 0 else d + 90.0

    # ------------------------------------------------------------- contacts
    def wall_corners(self, i):
        """{wall: [corner indices touching it]}, walls 'L','B','R','T'."""
        out = {'L': [], 'B': [], 'R': [], 'T': []}
        T = self.tol
        for c, (x, y) in enumerate(self.pts[i]):
            if x < T:
                out['L'].append(c)
            if y < T:
                out['B'].append(c)
            if x > self.s - T:
                out['R'].append(c)
            if y > self.s - T:
                out['T'].append(c)
        return out

    def pair_contact(self, i, j):
        """Classify the contact between squares i and j.

        Returns None (no contact) or a dict with
            kind: 'FL' | 'CE' | 'CC'
            for CE: owner (edge holder) and other (corner holder).
        Incidences are corner-on-edge hits: corner c of square p lies on edge e of
        square q iff its normal coordinate d == 1/2 and |t| <= 1/2 (tolerance)."""
        T = self.tol
        if _sat_gap(self.pts[i], self.pts[j]) > T:
            return None
        inc = []
        for (p, q) in ((i, j), (j, i)):
            cx, cy, th = self.sq[q]
            for e in range(4):
                ang = th + math.radians(90.0 * e)
                nx, ny = math.cos(ang), math.sin(ang)
                for c, (px, py) in enumerate(self.pts[p]):
                    wx, wy = px - cx, py - cy
                    d = nx * wx + ny * wy
                    t = -ny * wx + nx * wy
                    if abs(d - 0.5) < T and abs(t) < 0.5 + T:
                        inc.append(dict(owner=q, other=p, edge=e, corner=c,
                                        t=t, corner_end=abs(abs(t) - 0.5) < TOL))
        if not inc:
            return None
        # Fact 0 (structure_lemmas): the contact set of two interior-disjoint
        # convex bodies is a point or a segment.  Collect the DISTINCT contact
        # points; >= 2 of them means a segment, i.e. a FLUSH contact (this is the
        # only correct test -- a flush pair at tangential offset in (0,1) puts one
        # segment endpoint on each square, so "two corners on one edge" misses it).
        pts = []
        for x in inc:
            p = self.pts[x['other']][x['corner']]
            if not any(math.hypot(p[0] - q[0], p[1] - q[1]) < T for q in pts):
                pts.append(p)
        if len(pts) >= 2:
            return dict(kind='FL', inc=inc, npts=len(pts))
        # single contact point: corner-corner if it is a corner of BOTH squares
        cc = False
        for a in self.pts[i]:
            for b in self.pts[j]:
                if math.hypot(a[0] - b[0], a[1] - b[1]) < T:
                    cc = True
        if cc:
            return dict(kind='CC', inc=inc, npts=1)
        x = inc[0]
        return dict(kind='CE', owner=x['owner'], other=x['other'], inc=inc,
                    npts=1)

    def graph(self):
        """(adjacency over squares, pair-contact dict, wall corner map)."""
        adj = {i: set() for i in range(self.n)}
        pc = {}
        for i in range(self.n):
            for j in range(i + 1, self.n):
                r = self.pair_contact(i, j)
                if r is not None:
                    adj[i].add(j)
                    adj[j].add(i)
                    pc[(i, j)] = r
        wc = [self.wall_corners(i) for i in range(self.n)]
        return adj, pc, wc


def _sat_gap(P, Q):
    best = -1e9
    for poly in (P, Q):
        n = len(poly)
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % n]
            ax, ay = -(y2 - y1), (x2 - x1)
            nn = math.hypot(ax, ay)
            ax, ay = ax / nn, ay / nn
            p = [x * ax + y * ay for x, y in P]
            q = [x * ax + y * ay for x, y in Q]
            best = max(best, max(min(q) - max(p), min(p) - max(q)))
    return best


# --------------------------------------------------- shortest wall-to-wall
def shortest_paths(cfg, wall_a='L', wall_b='R', cap=20000):
    """All shortest square-node paths from wall_a to wall_b in the active-contact
    graph.  Returns (list of tuples of square indices, distance)."""
    adj, pc, wc = cfg.graph()
    src = [i for i in range(cfg.n) if wc[i][wall_a]]
    dst = set(i for i in range(cfg.n) if wc[i][wall_b])
    if not src or not dst:
        return [], None, (adj, pc, wc)
    INF = 10 ** 9
    dist = {i: INF for i in range(cfg.n)}
    order = []
    frontier = list(src)
    for i in src:
        dist[i] = 1
    while frontier:
        order.append(list(frontier))
        nxt = []
        for u in frontier:
            for v in adj[u]:
                if dist[v] > dist[u] + 1:
                    dist[v] = dist[u] + 1
                    nxt.append(v)
        frontier = nxt
    best = min((dist[i] for i in dst), default=INF)
    if best >= INF:
        return [], None, (adj, pc, wc)
    out = []

    def back(v, acc):
        if len(out) >= cap:
            return
        if dist[v] == 1 and v in set(src):
            out.append(tuple([v] + acc))
            if dist[v] != 1:
                return
        if dist[v] == 1:
            return
        for u in adj[v]:
            if dist[u] == dist[v] - 1:
                back(u, [v] + acc)

    for t in dst:
        if dist[t] == best:
            back(t, [])
    return out, best, (adj, pc, wc)
