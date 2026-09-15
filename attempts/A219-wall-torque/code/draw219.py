"""A219 SVG helpers: exact squares, force arrows at contact points, torque arcs, note column; every page
is geometry-checked (arrow feet on the boundary of the square they act on, no pair overlap, no wall
crossing) before it is written."""
import math

import numpy as np

import geom217 as G

S = 150.0
M = 60


class Page:
    def __init__(self, z, width_notes=360, height_extra=200):
        self.z = np.asarray(z, float)
        self.s = float(self.z[G.S_IDX])
        self.n = G.N
        self.H = int(S * self.s) + 2 * M
        self.W = self.H + width_notes
        self.o = []
        self.notes = []
        self.foot_err = 0.0
        self.extra = height_extra
        self.tx = M + S * self.s + 25
        self.ty = M + 10

    # ---- geometry
    def verts(self, i):
        return G.corners(self.z)[i]

    def P(self, x, y):
        return (M + S * x, M + S * (self.s - y))

    def dist_to_boundary(self, i, p):
        cx, cy, th = self.z[3 * i], self.z[3 * i + 1], self.z[3 * i + 2]
        c, d = math.cos(th), math.sin(th)
        u = c * (p[0] - cx) + d * (p[1] - cy)
        v = -d * (p[0] - cx) + c * (p[1] - cy)
        return max(abs(u), abs(v)) - 0.5

    def check(self):
        gap = min(G.pair_gaps(self.z).values())
        wall = float(G.wall_rows(self.z)[0].min())
        assert self.foot_err < 1e-6 and gap > -1e-6 and wall > -1e-6, (self.foot_err, gap, wall)
        return gap, wall

    # ---- drawing
    def frame(self):
        self.o.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Helvetica,Arial,sans-serif">'
                      % (self.W, self.H + self.extra))
        self.o.append('<defs><marker id="ah" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">'
                      '<path d="M0,0 L8,4 L0,8 z" fill="context-stroke"/></marker>'
                      '<pattern id="stip" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1" fill="#999"/></pattern></defs>')
        self.o.append('<rect width="%d" height="%d" fill="white"/>' % (self.W, self.H + self.extra))
        x0, y0 = self.P(0, self.s)
        self.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#333" stroke-width="2"/>'
                      % (x0, y0, S * self.s, S * self.s))

    def squares(self, styles, dashed=()):
        """styles: i -> (fill, stroke); default grey stipple (a square with no loaded contact)."""
        for i in range(self.n):
            pts = ' '.join('%.1f,%.1f' % self.P(*v) for v in self.verts(i))
            fill, stroke = styles.get(i, ('url(#stip)', '#777'))
            dash = ' stroke-dasharray="6,4"' if i in dashed else ''
            self.o.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.5"%s/>' % (pts, fill, stroke, dash))
            cx, cy = self.P(self.z[3 * i], self.z[3 * i + 1])
            self.o.append('<text x="%.1f" y="%.1f" font-size="15" text-anchor="middle" fill="#222">%d</text>' % (cx, cy + 5, i))

    def outline(self, verts, col='#d62728', dash='7,4', label=None):
        pts = ' '.join('%.1f,%.1f' % self.P(*v) for v in verts)
        self.o.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="%s"/>' % (pts, col, dash))
        if label:
            cx, cy = self.P(*np.mean(verts, axis=0))
            self.o.append('<text x="%.1f" y="%.1f" font-size="11" fill="%s" text-anchor="middle">%s</text>' % (cx, cy - 12, col, label))

    def arrow(self, p, f, col, width=2.0, length=0.45, on_square=None):
        fn = math.hypot(*f)
        if fn < 1e-12:
            return
        if on_square is not None:
            self.foot_err = max(self.foot_err, abs(self.dist_to_boundary(on_square, p)))
        ux, uy = f[0] / fn, f[1] / fn
        a0 = self.P(*p)
        a1 = self.P(p[0] + length * ux, p[1] + length * uy)
        self.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f" marker-end="url(#ah)"/>'
                      % (a0[0], a0[1], a1[0], a1[1], col, width))
        self.o.append('<circle cx="%.1f" cy="%.1f" r="3" fill="%s"/>' % (a0[0], a0[1], col))

    def arc(self, i, tau, col='#ff7f0e', label=None, r=30):
        """torque arc about square i's centre; + = counter-clockwise in the packing (screen y is down)."""
        cx, cy = self.P(self.z[3 * i], self.z[3 * i + 1])
        angs = [math.radians(200 + 140 * k / 40.0) for k in range(41)] if tau > 0 else [math.radians(340 - 140 * k / 40.0) for k in range(41)]
        pts = ' '.join('%.1f,%.1f' % (cx + r * math.cos(t), cy - r * math.sin(t)) for t in angs)
        self.o.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" marker-end="url(#ah)"/>' % (pts, col))
        if label:
            self.o.append('<text x="%.1f" y="%.1f" font-size="11" fill="%s" text-anchor="middle">%s</text>' % (cx, cy + r + 13, col, label))

    def dot(self, p, col='#d62728', r=5, label=None):
        a = self.P(*p)
        self.o.append('<circle cx="%.1f" cy="%.1f" r="%d" fill="%s"/>' % (a[0], a[1], r, col))
        if label:
            self.o.append('<text x="%.1f" y="%.1f" font-size="11" fill="%s">%s</text>' % (a[0] + 7, a[1] - 5, col, label))

    def line(self, t, dy=16, size=12, col='#222', bold=False, x=None, y=None):
        if x is not None:
            self.tx = x
        if y is not None:
            self.ty = y
        t = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        self.o.append('<text x="%d" y="%d" font-size="%d" fill="%s"%s>%s</text>'
                      % (self.tx, self.ty, size, col, ' font-weight="bold"' if bold else '', t))
        self.ty += dy

    def write(self, path, t0=None):
        import time
        gap, wall = self.check()
        if t0 is not None:
            self.line('', dy=8)
            self.line('renderer %.2f s; geometry checked: arrow feet on the boundary (%.0e), min pair gap %.0e, min wall gap %.0e'
                      % (time.time() - t0, self.foot_err, gap, wall), size=10, col='#666')
        self.o.append('</svg>')
        open(path, 'w', encoding='utf-8').write('\n'.join(self.o))
        return path
