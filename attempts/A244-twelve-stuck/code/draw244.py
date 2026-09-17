"""A244 minimal SVG page writer: panels on a grid, exact geometry, a per-panel geometry check."""
import math

import numpy as np

BLUE, ORANGE, GREY, RED, GREEN = '#2f6fb0', '#d97a20', '#888888', '#c02020', '#2f8f4f'
CELLFILL = {'00': '#ffe9c9', '01': '#dfeffd', '10': '#e6f7e3'}


def esc(t):
    return (t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


class Page(object):
    def __init__(self, w, h, title):
        self.w, self.h, self.title = w, h, title
        self.parts = []
        self.panels = {}

    def panel(self, key, x, y, w, h, side, pad=0.12):
        sc = min(w / (side + 2 * pad), h / (side + 2 * pad))
        self.panels[key] = (x + (w - sc * side) / 2, y + h - (h - sc * side) / 2, sc)
        return self.panels[key]

    def _t(self, key, p):
        x0, y0, sc = self.panels[key]
        return (x0 + sc * p[0], y0 - sc * p[1])

    def frame(self, key, side, label=None):
        a, b = self._t(key, (0, 0)), self._t(key, (side, side))
        self.parts.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="none" '
                          'stroke="#222" stroke-width="1.6"/>' % (a[0], b[1], b[0] - a[0], a[1] - b[1]))
        if label:
            self.text(a[0], b[1] - 6, label, 11, '#222')

    def rect(self, key, r, fill, stroke='#bbb', width=0.8, dash=None):
        x0, x1, y0, y1 = r
        a, b = self._t(key, (x0, y0)), self._t(key, (x1, y1))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        self.parts.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s" '
                          'stroke="%s" stroke-width="%.2f"%s/>' % (a[0], b[1], b[0] - a[0], a[1] - b[1],
                                                                   fill, stroke, width, d))

    def square(self, key, pose, fill, stroke, width=1.3, label=None, dash=None, op=0.85):
        cx, cy, th = pose
        co, si = math.cos(th), math.sin(th)
        pts = [(cx + co * a - si * b, cy + si * a + co * b)
               for a, b in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))]
        s = ' '.join('%.2f,%.2f' % self._t(key, p) for p in pts)
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        self.parts.append('<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" '
                          'stroke-width="%.2f"%s/>' % (s, fill, op, stroke, width, d))
        if label:
            p = self._t(key, (cx, cy))
            self.text(p[0], p[1] + 3, label, 8.5, '#111', anchor='middle')

    def dot(self, key, p, col=RED, r=2.0):
        q = self._t(key, p)
        self.parts.append('<circle cx="%.2f" cy="%.2f" r="%.1f" fill="%s"/>' % (q[0], q[1], r, col))

    def text(self, x, y, t, size=10, col='#111', anchor='start', mono=False, weight='normal'):
        fam = 'ui-monospace,Consolas,monospace' if mono else 'system-ui,Segoe UI,sans-serif'
        self.parts.append('<text x="%.2f" y="%.2f" font-size="%.1f" fill="%s" text-anchor="%s" '
                          'font-family="%s" font-weight="%s">%s</text>'
                          % (x, y, size, col, anchor, fam, weight, esc(t)))

    def note(self, x, y, lines, size=9.2, lead=11.5, mono=False):
        for k, l in enumerate(lines):
            self.text(x, y + k * lead, l, size, '#333', mono=mono)

    def polyline(self, pts, col, width=1.4, dash=None):
        s = ' '.join('%.2f,%.2f' % p for p in pts)
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        self.parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.2f"%s/>'
                          % (s, col, width, d))

    def line(self, x1, y1, x2, y2, col='#999', width=1.0, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        self.parts.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" '
                          'stroke-width="%.2f"%s/>' % (x1, y1, x2, y2, col, width, d))

    def save(self, path):
        head = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'
                '<rect width="100%%" height="100%%" fill="#ffffff"/>' % (self.w, self.h, self.w, self.h))
        with open(path, 'w', encoding='utf-8') as f:
            f.write(head + '\n' + '\n'.join(self.parts) + '\n</svg>\n')


def check(poses, side, tol=1e-9):
    """geometry check for a panel: containment and pairwise interior-disjointness, exactly as
    drawn.  Returns (ok, min wall gap, min pair gap)."""
    import fast244 as F
    z = np.zeros(F.NV)
    n = len(poses)
    for i, (x, y, t) in enumerate(poses):
        z[3 * i], z[3 * i + 1], z[3 * i + 2] = x, y, t
    for i in range(n, F.N):                       # park the unused slots far apart, outside
        z[3 * i] = side + 5 + 3 * i
        z[3 * i + 1] = side + 5 + 3 * i
    z[F.S_IDX] = side
    cx, cy, th, co, si, q, n2 = F.geom(z)
    gw = min(float(np.min(np.stack([q[i, :, 0], q[i, :, 1], side - q[i, :, 0], side - q[i, :, 1]])))
             for i in range(n))
    _, g1, _ = F.pair_table(q, n2, cx, cy)
    gp = min(max(g1[i, j], g1[j, i]) for i in range(n) for j in range(i + 1, n))
    return bool(gw >= -tol and gp >= -tol), float(gw), float(gp)
