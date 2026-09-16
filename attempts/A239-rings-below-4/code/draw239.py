"""A239 drawing helpers on top of A222's Page (docs/residue_map rules: exact squares, hatched sealed regions, the
pocket shaded, forces as arrows -- blue wall, black square-square, RED external deficit -- torque senses as arcs,
grey stipple for undecided / schematic squares, a note per panel with the geometry check and the time per step)."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A222-ring-swap', 'code'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A217-torque-probe', 'code'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A237-pocket-waste', 'code'))
import draw222 as D            # noqa: E402
import geom237 as G237         # noqa: E402

ORANGE, BLUE, GREY, RED = D.ORANGE, D.BLUE, D.GREY, D.RED
POCKET = '#e8f1fb'
WEDGE = '#fbe3e3'
MARKER = ('<defs><marker id="ah" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">'
          '<path d="M0,0 L7,3.5 L0,7 z" fill="context-stroke"/></marker>'
          '<marker id="ahr" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">'
          '<path d="M0,0 L7,3.5 L0,7 z" fill="#d62728"/></marker></defs>')


def page(title, cols, rows, side, note_h=230, panel_w=None):
    pg = D.Page(title, cols, rows, side, panel_w=panel_w, note_h=note_h)
    pg.o.insert(2, MARKER)
    return pg


def wrap(lines, width=112):
    out = []
    for t in lines:
        while len(t) > width:
            cut = t.rfind(' ', 0, width)
            cut = width if cut < 40 else cut
            out.append(t[:cut])
            t = '   ' + t[cut:].lstrip()
        out.append(t)
    return out


def shade(pg, k, geom, fill='url(#hatch)', stroke='#555', width=0.8):
    for poly in G237.polys_of(geom):
        pg.poly(k, list(poly.exterior.coords)[:-1], fill, stroke, width=width)
        for ring in poly.interiors:
            pg.poly(k, list(ring.coords)[:-1], 'white', stroke, width=width)


def pocket(pg, k, members, s):
    """the pocket polygon (container minus the members) shaded light blue; returns it."""
    P = G237.pocket(list(members), s)
    shade(pg, k, P, POCKET, '#9ab', 0.6)
    return P


def dot(pg, k, x, y, col=RED, r=3.5):
    px, py = pg.P(k, x, y)
    pg.o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (px, py, r, col))


def label(pg, k, x, y, text, size=10, col='#222', anchor='middle'):
    px, py = pg.P(k, x, y)
    pg.o.append('<text x="%.1f" y="%.1f" font-size="%d" fill="%s" text-anchor="%s">%s</text>' % (px, py, size, col, anchor, D.esc(text)))


def arrow(pg, k, p, f, col, length, width=1.6, dash=None, red=False):
    """an arrow at the point p in the direction f (unit vector times `length` in packing units)."""
    fn = math.hypot(f[0], f[1])
    if fn < 1e-12 or length <= 0:
        return
    ux, uy = f[0] / fn, f[1] / fn
    a0, a1 = pg.P(k, *p), pg.P(k, p[0] + length * ux, p[1] + length * uy)
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    pg.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f"%s marker-end="url(#%s)"/>'
                % (a0[0], a0[1], a1[0], a1[1], col, width, d, 'ahr' if red else 'ah'))
    pg.o.append('<circle cx="%.1f" cy="%.1f" r="2.2" fill="%s"/>' % (a0[0], a0[1], col))


def arc(pg, k, c, sense, col, r_px=20, dash=None, width=2.4, text=None):
    """a torque arc about the centre c: sense +1 = counter-clockwise (y up), -1 = clockwise."""
    cx, cy = pg.P(k, *c)
    angs = [math.radians(200 + 140 * j / 30.0) for j in range(31)] if sense > 0 else [math.radians(340 - 140 * j / 30.0) for j in range(31)]
    pts = ' '.join('%.1f,%.1f' % (cx + r_px * math.cos(t), cy - r_px * math.sin(t)) for t in angs)
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    pg.o.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s marker-end="url(#%s)"/>'
                % (pts, col, width, d, 'ahr' if col == RED else 'ah'))
    if text:
        pg.o.append('<text x="%.1f" y="%.1f" font-size="9" fill="%s" text-anchor="middle">%s</text>' % (cx, cy + r_px + 11, col, D.esc(text)))


def forces(pg, k, arrows, scale=0.45, lam_max=None):
    """FJ force arrows: blue wall normals, black pair forces on the first square with a grey reaction."""
    if not arrows:
        return
    lam_max = lam_max or max(a['lam'] for a in arrows)
    for a in arrows:
        L = scale * (0.25 + 0.75 * a['lam'] / lam_max)
        w = 1.2 + 2.5 * a['lam'] / lam_max
        if a['kind'] == 'wall':
            arrow(pg, k, a['p'], a['f'], '#1f77b4', L, w)
        else:
            arrow(pg, k, a['p'], a['f'], '#000', L, w)
            arrow(pg, k, a['p'], [-a['f'][0], -a['f'][1]], '#666', L, w)


def deficit(pg, k, per_square, poses, scale=1.2):
    """the external loads of the minimal closing load in RED: forces at the centre, torques as arcs."""
    for i, d in per_square.items():
        i = int(i)
        F = d['F']
        c = (poses[i][0], poses[i][1])
        fn = math.hypot(*F)
        if fn > 1e-6:
            arrow(pg, k, c, F, RED, min(0.6, scale * fn), 2.2, red=True)
        if abs(d['tau']) > 1e-6:
            arc(pg, k, c, 1 if d['tau'] > 0 else -1, RED, r_px=18, text='ext %+.3f' % d['tau'])


def lemma_w(pg, k, squares, poses, s_tol=1e-6):
    """Lemma W: the aligning sense of every tilted wall square as an orange arc (solid when the wall force is
    loaded, dashed when it is 0)."""
    for q in squares:
        if not q['tilted']:
            continue
        c = (poses[q['i']][0], poses[q['i']][1])
        if q['W'] > s_tol:
            arc(pg, k, c, q['aligning_sense'], '#ff7f0e', r_px=26, text='W %.2f tau %+.3f' % (q['W'], q['tau_wall']))
        else:
            arc(pg, k, c, q['aligning_sense'], '#ff7f0e', r_px=26, dash='4,3', width=1.4, text='W = 0')


def push(pg, k, pushes, poses, s):
    """Lemma PUSH at every doubly-met corner: the separating normal into the pushed meeter at the contact point
    (solid when touching, dashed when the pair has a gap), with (n_u, n_v) in the corner frame."""
    for cn, p in pushes.items():
        n, pt = p['n'], p['contact']
        dash = None if p['touching'] else '5,3'
        arrow(pg, k, pt, n, '#7b2cbf', 0.35, 1.8, dash)
        arrow(pg, k, pt, [-n[0], -n[1]], '#7b2cbf', 0.35, 1.8, dash)
        label(pg, k, pt[0], pt[1] - 0.14, '%s n=(%+.2f,%+.2f)%s' % (cn, p['n_frame'][0], p['n_frame'][1], '' if p['touching'] else ' gap %.3f' % p['gap']), 8, '#7b2cbf')


class Plot:
    """a small x-y plot inside panel k of a Page (data box -> the panel's square)."""

    def __init__(self, pg, k, xr, yr, margin=0.22):
        self.pg, self.k, self.xr, self.yr, self.m = pg, k, xr, yr, margin
        s = pg.side

        def P(x, y):
            u = margin + (s - 2 * margin) * (x - xr[0]) / (xr[1] - xr[0])
            v = margin + (s - 2 * margin) * (y - yr[0]) / (yr[1] - yr[0])
            return pg.P(k, u, v)
        self.P = P
        ox, oy = pg.origin(k)
        pg.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="white" stroke="#333" stroke-width="1.2"/>'
                    % (P(xr[0], yr[1])[0], P(xr[0], yr[1])[1], P(xr[1], yr[0])[0] - P(xr[0], yr[1])[0], P(xr[1], yr[0])[1] - P(xr[0], yr[1])[1]))

    def line(self, xs, ys, col, width=1.6, dash=None, lab=None):
        pts = ' '.join('%.1f,%.1f' % self.P(x, y) for x, y in zip(xs, ys) if self.yr[0] <= y <= self.yr[1])
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        self.pg.o.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (pts, col, width, d))
        if lab:
            x, y = xs[-1], min(max(ys[-1], self.yr[0]), self.yr[1])
            px, py = self.P(x, y)
            self.pg.o.append('<text x="%.1f" y="%.1f" font-size="9" fill="%s">%s</text>' % (px + 3, py + 3, col, D.esc(lab)))

    def hline(self, y, col, lab, dash='4,3'):
        self.line([self.xr[0], self.xr[1]], [y, y], col, 1.0, dash)
        px, py = self.P(self.xr[0], y)
        self.pg.o.append('<text x="%.1f" y="%.1f" font-size="9" fill="%s">%s</text>' % (px + 3, py - 3, col, D.esc(lab)))

    def vline(self, x, col, lab):
        self.line([x, x], [self.yr[0], self.yr[1]], col, 1.0, '2,3')
        px, py = self.P(x, self.yr[0])
        self.pg.o.append('<text x="%.1f" y="%.1f" font-size="9" fill="%s" text-anchor="middle">%s</text>' % (px, py + 12, col, D.esc(lab)))

    def axes(self, xlab, ylab, xticks, yticks):
        for x in xticks:
            px, py = self.P(x, self.yr[0])
            self.pg.o.append('<text x="%.1f" y="%.1f" font-size="9" fill="#444" text-anchor="middle">%g</text>' % (px, py + 22, x))
        for y in yticks:
            px, py = self.P(self.xr[0], y)
            self.pg.o.append('<text x="%.1f" y="%.1f" font-size="9" fill="#444" text-anchor="end">%g</text>' % (px - 4, py + 3, y))
        px, py = self.P(0.5 * (self.xr[0] + self.xr[1]), self.yr[0])
        self.pg.o.append('<text x="%.1f" y="%.1f" font-size="10" fill="#222" text-anchor="middle">%s</text>' % (px, py + 36, D.esc(xlab)))
        px, py = self.P(self.xr[0], self.yr[1])
        self.pg.o.append('<text x="%.1f" y="%.1f" font-size="10" fill="#222">%s</text>' % (px, py - 8, D.esc(ylab)))
