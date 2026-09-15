"""A222 SVG helpers: multi-panel pages of exact squares, census cells, settled slot squares, X' outlines at
admissible (checked) poses, grey stipple for undecided regions, a note block per panel.  Every panel that
shows a configuration is geometry-checked (SAT gaps and wall rows of the drawn 11-square configuration
>= -1e-6) before the page is written; the check result is printed in the panel's note."""
import math

import numpy as np

import geom217 as G

S = 95.0          # pixels per unit
PAD = 30


def sq_verts(cx, cy, th):
    c, d = math.cos(th), math.sin(th)
    return [(cx + c * x - d * y, cy + d * x + c * y) for x, y in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))]


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


class Page:
    def __init__(self, title, cols, rows, side, panel_w=None, note_h=120, width_extra=0):
        self.side = side
        self.pw = panel_w or int(S * side) + 2 * PAD
        self.ph = int(S * side) + 2 * PAD + note_h
        self.cols, self.rows = cols, rows
        self.W = cols * self.pw + width_extra
        self.H = rows * self.ph + 40
        self.o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Helvetica,Arial,sans-serif">'
                  % (self.W, self.H),
                  '<defs><pattern id="stip" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.1" fill="#888"/></pattern>'
                  '<pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="7" stroke="#555" stroke-width="1.2"/></pattern></defs>',
                  '<rect width="%d" height="%d" fill="white"/>' % (self.W, self.H),
                  '<text x="12" y="24" font-size="15" font-weight="bold" fill="#222">%s</text>' % esc(title)]
        self.checks = []

    def origin(self, k):
        r, c = divmod(k, self.cols)
        return c * self.pw + PAD, 40 + r * self.ph + PAD

    def P(self, k, x, y):
        ox, oy = self.origin(k)
        return ox + S * x, oy + S * (self.side - y)

    def frame(self, k, s=None):
        s = s or self.side
        x0, y0 = self.P(k, 0, s)
        self.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#333" stroke-width="1.6"/>'
                      % (x0, y0, S * s, S * s))

    def poly(self, k, verts, fill, stroke, width=1.3, dash=None, label=None, lcol='#222'):
        pts = ' '.join('%.1f,%.1f' % self.P(k, *v) for v in verts)
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        self.o.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (pts, fill, stroke, width, d))
        if label is not None:
            cx, cy = self.P(k, *np.mean(verts, axis=0))
            self.o.append('<text x="%.1f" y="%.1f" font-size="12" text-anchor="middle" fill="%s">%s</text>' % (cx, cy + 4, lcol, esc(str(label))))

    def square(self, k, pose, fill, stroke, label=None, dash=None, width=1.3):
        self.poly(k, sq_verts(*pose), fill, stroke, width, dash, label)

    def cell(self, k, box, stroke='#d62728', fill='none', dash='5,3', label=None, width=1.6):
        x0, x1, y0, y1 = box
        self.poly(k, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], fill, stroke, width, dash, label, lcol=stroke)

    def text(self, k, lines, size=10.5, col='#222', dy=13):
        ox, oy = self.origin(k)
        y = oy + S * self.side + 16
        for t in lines:
            self.o.append('<text x="%d" y="%.1f" font-size="%.1f" fill="%s">%s</text>' % (ox, y, size, col, esc(t)))
            y += dy

    def check(self, poses, s, tol=1e-6):
        """geometry check of a full 11-square configuration; returns (ok, min pair gap, min wall)."""
        z = np.zeros(G.NV)
        for i, p in enumerate(poses):
            z[3 * i:3 * i + 3] = p
        z[G.S_IDX] = s
        gap = min(G.pair_gaps(z).values())
        wall = float(G.wall_rows(z)[0].min())
        ok = gap >= -tol and wall >= -tol
        self.checks.append(ok)
        return ok, gap, wall

    def check_partial(self, poses, s, tol=1e-6):
        """pairwise SAT gaps and wall rows of an arbitrary number of squares (partial packings of the sweep)."""
        worst_gap, worst_wall = 1e9, 1e9
        for i, p in enumerate(poses):
            v = np.array(sq_verts(*p))
            worst_wall = min(worst_wall, v[:, 0].min(), v[:, 1].min(), s - v[:, 0].max(), s - v[:, 1].max())
        for i in range(len(poses)):
            for j in range(i + 1, len(poses)):
                worst_gap = min(worst_gap, sep(poses[i], poses[j]))
        ok = worst_gap >= -tol and worst_wall >= -tol
        self.checks.append(ok)
        return ok, worst_gap, worst_wall

    def write(self, path):
        assert all(self.checks), self.checks
        self.o.append('</svg>')
        open(path, 'w', encoding='utf-8').write('\n'.join(self.o))
        return path


def sep(p, q):
    """separating-axis gap of two unit squares (>= 0: interior-disjoint)."""
    vp, vq = sq_verts(*p), sq_verts(*q)
    best = -1e9
    for th in (p[2], q[2]):
        for ax in ((math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th))):
            a = [ax[0] * x + ax[1] * y for x, y in vp]
            b = [ax[0] * x + ax[1] * y for x, y in vq]
            best = max(best, min(a) - max(b), min(b) - max(a))
    return best


ORANGE = ('#fde9c9', '#b06a00')
BLUE = ('#dbe9f6', '#1f4e79')
GREY = ('#eeeeee', '#888888')
DARK = ('url(#hatch)', '#444444')
STIP = ('url(#stip)', '#777777')
RED = '#d62728'
