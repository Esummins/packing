"""A261 SVG helpers: a corner-frame Panel and convex clipping (Sutherland-Hodgman) for overlap slivers."""
import html

import numpy as np

BLUE, RED, ORANGE, GREY, GREEN = '#2b6cb0', '#c53030', '#dd6b20', '#718096', '#2f855a'


def clip(S, Cp):
    """Sutherland-Hodgman: convex polygon S clipped by convex polygon Cp (both counter-clockwise)."""
    out = [tuple(p) for p in S]
    for i in range(len(Cp)):
        a, b = Cp[i], Cp[(i + 1) % len(Cp)]
        inp, out = out, []
        side = lambda p: (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
        for j in range(len(inp)):
            p, q = inp[j], inp[(j + 1) % len(inp)]
            sp, sq = side(p), side(q)
            if sp >= 0:
                out.append(p)
            if sp * sq < 0:
                t = sp / (sp - sq)
                out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
        if not out:
            return []
    return out


class Panel:
    def __init__(self, x0, y0, ext, sc, title, origin=(0.0, 0.0)):
        self.x0, self.y0, self.ext, self.sc, self.org, self.o = x0, y0, ext, sc, origin, []
        self.o.append('<text x="%.1f" y="%.1f" font-size="12" font-weight="bold">%s</text>' % (x0, y0 - 8, html.escape(title)))

    def pt(self, p):
        return self.x0 + (p[0] - self.org[0]) * self.sc, self.y0 + (self.ext - (p[1] - self.org[1])) * self.sc

    def poly(self, V, **kw):
        if len(V) < 3:
            return
        self.o.append('<polygon points="%s" %s/>' % (' '.join('%.2f,%.2f' % self.pt(p) for p in V), ' '.join(
            '%s="%s"' % (k.replace('_', '-'), v) for k, v in kw.items())))

    def sq(self, Q, col=BLUE, name=None, op='0.20', dash=None):
        kw = dict(fill=col, fill_opacity=op, stroke=col, stroke_width='1.4')
        if dash:
            kw.update(fill='none', stroke_dasharray=dash)
        self.poly(Q, **kw)
        if name:
            x, y = self.pt(np.asarray(Q).mean(0))
            self.o.append('<text x="%.1f" y="%.1f" font-size="11" fill="%s" text-anchor="middle">%s</text>' % (x, y + 4, col, name))

    def walls(self, box=True):
        e = self.ext
        o = self.org
        self.o.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="#1a202c" stroke-width="2.4"/>'
                      % (*self.pt((o[0], o[1] + e)), *self.pt(o), *self.pt((o[0] + e, o[1]))))
        if box:
            self.poly([(0, 0), (1, 0), (1, 1), (0, 1)], fill='#faf089', fill_opacity='0.35', stroke='#b7791f', stroke_width='0.8',
                      stroke_dasharray='4,3')

    def note(self, lines, dy=16):
        for i, s in enumerate(lines):
            self.o.append('<text x="%.1f" y="%.1f" font-size="10.5" fill="#2d3748">%s</text>' % (
                self.x0, self.y0 + self.ext * self.sc + dy + 13 * i, html.escape(s)))
