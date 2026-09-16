"""A239 page 1: docs/residue_map/campaigns/A239-rings-below-4/wedged_seal.svg -- Lemma WEDGED-SEAL drawn exactly:
(a) the wedged square, the sealed triangle (hatched) and the two wedges; (b) the proof's objects: the strip, the
triangle Delta = L R R', the forbidden quadrant K at R (stipple), the extremal second square G along the leaning
edge (min u = 1/sin theta), the wedge line through R at angle alpha; (c) the wedge inequality f(alpha) >= 1;
(d) the consequence at a doubly-met corner (the window crowd at 20 deg with Lemma PUSH's normal).
"""
import math
import os
import sys
import time

import numpy as np
from shapely.geometry import Polygon, box as sbox

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import draw239 as DR                                                       # noqa: E402
import geom239 as GM                                                       # noqa: E402
import stress239 as SS                                                     # noqa: E402
import band236 as BD                                                       # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
PAGES = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A239-rings-below-4')
SIDE = 2.4


def walls(pg, k):
    x0, y0 = pg.P(k, 0, 0)
    x1, _ = pg.P(k, SIDE, 0)
    _, y1 = pg.P(k, 0, SIDE)
    pg.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#222" stroke-width="3.5"/>' % (x0, y0, x1, y0))
    pg.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#222" stroke-width="3.5"/>' % (x0, y0, x0, y1))
    pg.cell(k, (0, 1, 0, 1), label=None)


def panel_a(pg, k, th):
    t0 = time.time()
    Q = GM.wedged_square(th)
    tri, Tf, Tw = GM.wedge_regions(th)
    walls(pg, k)
    pg.poly(k, Tf, DR.WEDGE, '#c66', 0.8)
    pg.poly(k, Tw, DR.WEDGE, '#c66', 0.8)
    pg.poly(k, tri, 'url(#hatch)', '#555', 0.8)
    pg.square(k, Q, DR.ORANGE[0], DR.ORANGE[1], label='Q', width=2.0)
    b, l = math.cos(math.radians(th)), math.sin(math.radians(th))
    for (x, y), t in (((l, 0), 'L=(sin th, 0)'), ((0, b), 'W=(0, cos th)'), ((b + l, l), 'R=(cos+sin, sin)'), ((b, b + l), 'T=(cos, cos+sin)')):
        DR.dot(pg, k, x, y, '#222', 2.5)
        DR.label(pg, k, x + 0.02, y + 0.06, t, 9, '#222', 'start')
    DR.label(pg, k, 0.14, 0.12, 'sealed', 8, '#333')
    DR.label(pg, k, 0.86, 0.1, 'T_f', 9, '#a33')
    DR.label(pg, k, 0.1, 0.9, 'T_w', 9, '#a33')
    ok, gap, wall = pg.check_partial([Q], 100.0)
    t1 = time.time()
    found, worst = GM.second_meeter_search(th, 20000, seed=7)
    t2 = time.time()
    v = BD.verts(Q)
    pg.text(k, DR.wrap([
        '(a) WHAT IT IS: the WEDGED square Q (tilt theta = %g deg, centre (w/2, w/2), w = cos + sin = %.3f) with one vertex on the floor '
        'and one on the wall of a corner; the open corner box (0,1)^2 dashed red; the sealed triangle (area sin cos / 2 = %.3f) hatched; '
        'the two wedges T_f (apex angle theta) and T_w (apex angle 90 - theta) shaded: the only parts of the box Q leaves uncovered.'
        % (th, b + l, b * l / 2),
        'Lemma WEDGED-SEAL (= sideband.md Cor. B1): no unit square of the quadrant interior-disjoint from Q meets the box -- no square can '
        'put a point into T_f or T_w (docs/proofs/wedged_seal.md s.2).  Far vertices at x, y = cos + sin = %.3f >= 1.' % (b + l),
        'checks: Q in the quadrant (min coordinate %.1e), touches both walls (x_min %.1e, y_min %.1e), meets the box: %s; Monte-Carlo: '
        '20000 random unit squares of the quadrant meeting the box, interior-disjoint from Q: %d found (largest SAT gap %.3f < 0); '
        'draw %.2f s, search %.1f s.' % (v.min(), v[:, 0].min(), v[:, 1].min(), BD.meets_corner(Q, 100.0, 'BL'), found, worst, t1 - t0, t2 - t1)]))


def panel_b(pg, k, th, alpha):
    t0 = time.time()
    tr = math.radians(th)
    b, l = math.cos(tr), math.sin(tr)
    L, R = np.array([l, 0.0]), np.array([l + b, l])
    tv, nv = np.array([b, l]), np.array([-l, b])
    Rp = np.array([l + 1 / b, 0.0])
    Q = GM.wedged_square(th)
    walls(pg, k)
    K = Polygon([R, R + 3 * nv, R + 3 * nv - 3 * tv, R - 3 * tv]).intersection(sbox(0, 0, SIDE, SIDE))
    DR.shade(pg, k, K, 'url(#stip)', '#999', 0.5)
    pg.poly(k, [L, R, Rp], 'none', '#333', 1.0, dash='3,2')
    for P0, P1 in ((L - 2.5 * nv, L + 0.6 * nv), (R - 3 * nv, R + 2 * nv)):
        a0, a1 = pg.P(k, *P0), pg.P(k, *P1)
        pg.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#888" stroke-width="0.8" stroke-dasharray="2,3"/>' % (a0[0], a0[1], a1[0], a1[1]))
    pg.square(k, Q, DR.ORANGE[0], DR.ORANGE[1], label='Q', width=2.0)
    g0 = L + (b / l) * tv
    G = (g0[0] + (tv[0] - nv[0]) / 2, g0[1] + (tv[1] - nv[1]) / 2, tr)
    pg.square(k, G, DR.BLUE[0], DR.BLUE[1], label='G*', width=1.6)
    ar = math.radians(alpha)
    A0 = np.array([R[0] - R[1] / math.tan(ar), 0.0])
    P1 = A0 + 2.2 * np.array([math.cos(ar), math.sin(ar)])
    a0, a1 = pg.P(k, *A0), pg.P(k, *P1)
    pg.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#7b2cbf" stroke-width="1.2" stroke-dasharray="5,3"/>' % (a0[0], a0[1], a1[0], a1[1]))
    for (x, y), t in ((L, 'L'), (R, 'R'), (Rp, "R'"), (A0, 'A0')):
        DR.dot(pg, k, x, y, '#222', 2.5)
        DR.label(pg, k, x + 0.04, y + 0.05, t, 9, '#222', 'start')
    DR.label(pg, k, R[0] - 0.35, R[1] + 0.9, 'K (forbidden)', 9, '#666')
    ok, gap, wall = pg.check_partial([Q, G], 100.0)
    vG = BD.verts(G)
    pg.text(k, DR.wrap([
        '(b) WHAT IT IS: the objects of the proof at theta = %g deg.  Strip = between the two dotted lines perpendicular to the leaning '
        'edge L-R through L and R; Delta = the dashed triangle L R R\' (the part of the strip below the edge and above the floor); '
        'K = the open quadrant at R (stipple) that no second meeter G may enter (steps 1-4 of s.2).' % th,
        'G* (blue) is the EXTREMAL admissible square of the wedge case: its edge lies along L-R and its vertex on the floor; its least '
        'abscissa is 1/sin theta = %.3f > 1, so it misses the box.  Purple: the separating line through R at angle alpha = %g deg of '
        'step 5, meeting the floor at A0; every square below it and above the floor has min u >= f(alpha) = %.3f >= 1 (step 6).'
        % (1 / l, alpha, GM.f_alpha(th, alpha)),
        'checks: Q, G* in the quadrant (min coordinate %.1e), SAT gap Q-G* %.1e >= 0, G* min x = %.4f = 1/sin theta; draw %.2f s.'
        % (min(BD.verts(Q).min(), vG.min()), gap, vG[:, 0].min(), time.time() - t0)]))


def panel_c(pg, k):
    t0 = time.time()
    pl = DR.Plot(pg, k, (0.0, 90.0), (0.0, 0.5))
    ths = np.arange(0.5, 89.6, 0.5)
    g = [min(GM.f_alpha(t, a) for a in np.arange(t, 90.0, 0.05)) - 1 for t in ths]
    pl.line(ths, g, '#1f4e79', 2.0, lab='min_alpha f - 1')
    pl.line(ths, [0.75 * math.sin(math.radians(t)) + math.cos(math.radians(t)) - 1 for t in ths], '#b06a00', 1.2, '5,3', '(3/4) sin + cos - 1')
    pl.line(ths, [min(0.5, 1 / math.sin(math.radians(t)) - 1) for t in ths], '#2a9d8f', 1.2, '2,3', '1/sin - 1')
    pl.vline(math.degrees(math.atan(2.0)), '#888', 'tan th = 2')
    pl.axes('theta (deg)', 'f(alpha) - 1', [0, 15, 30, 45, 60, 75, 90], [0, 0.1, 0.2, 0.3, 0.4, 0.5])
    gm = min(g)
    pg.text(k, DR.wrap([
        '(c) WHAT IT IS: the wedge inequality of step 6, f(alpha) = sin th + cos th - sin th cot alpha + cos^2 alpha / sin alpha >= 1 for '
        'alpha in [theta, 90): blue = min over alpha of f - 1 (grid 0.05 deg), positive at every theta in [0.5, 89.5] (least %.1e at theta = %.1f deg, '
        '-> 0 only as theta -> 0 or 90); the two bounds of the proof: (3/4) sin + cos - 1 for tan theta <= 2 (dashed) and 1/sin - 1 for tan '
        'theta > 2 (dotted), both >= 0 on their ranges.' % (gm, ths[int(np.argmin(g))]),
        'Both sides vanish as theta -> 0 (the wedge T_w opens to a full quadrant: W -> (0, 1), a flush square beside Q just misses) and as '
        'theta -> 90; the inequality is strict inside.  Lemma B0* checked on a 0.25-deg grid (test239.py).  %.1f s.' % (time.time() - t0)]))


def panel_d(pg, k, th):
    t0 = time.time()
    A, B = GM.window_pair(th, math.sin(math.radians(th)) + 0.02, 0.0)
    walls(pg, k)
    pg.square(k, A, DR.ORANGE[0], DR.ORANGE[1], label='A', width=1.8)
    pg.square(k, B, DR.ORANGE[0], DR.ORANGE[1], label='B', width=1.8)
    pushes = SS.push_axes([A, B], SIDE, {'BL': [0, 1]})
    DR.push(pg, k, pushes, [A, B], SIDE)
    ok, gap, wall = pg.check_partial([A, B], SIDE)
    p = pushes['BL']
    pg.text(k, DR.wrap([
        '(d) WHAT IT IS: the consequence at a doubly-met open corner -- A237\'s window crowd at theta = %g deg: A flat on the floor at '
        'offset delta = sin theta + 0.02 = %.3f (touches the floor only), B tilted with a vertex on the wall and its lower edge through '
        'A\'s corner (touches the wall only).  Neither is wedged: by WEDGED-SEAL a wedged meeter would be ALONE (then K0-FREE teleports it).'
        % (th, math.sin(math.radians(th)) + 0.02),
        'Purple: Lemma PUSH\'s separating normal at the contact (A\'s corner on B\'s edge): into the pushed square %s it reads '
        '(n_u, n_v) = (%+.3f, %+.3f) -- positive along the floor A touches (PUSH (ii)), negative into the floor; the wedged square would '
        'need (+, +) into it and a positive component of (-n) at once: the contradiction of s.3.' % ('A' if p['pushed'] == 0 else 'B', p['n_frame'][0], p['n_frame'][1]),
        'checks: SAT gap A-B %.1e (contact), min wall coordinate %.1e; both meet the box: %s, %s; %.2f s.'
        % (gap, wall, BD.meets_corner(A, 100.0, 'BL'), BD.meets_corner(B, 100.0, 'BL'), time.time() - t0)]))


def page():
    os.makedirs(PAGES, exist_ok=True)
    pg = DR.page('A239 -- Lemma WEDGED-SEAL (= Cor. B1): a corner meeter touching both walls is alone. (a) the wedged square and its '
                 'wedges; (b) the proof objects; (c) the wedge inequality; (d) the consequence at a doubly-met corner', 2, 2, SIDE, note_h=210)
    panel_a(pg, 0, 30.0)
    panel_b(pg, 1, 30.0, 60.0)
    panel_c(pg, 2)
    panel_d(pg, 3, 20.0)
    return pg.write(os.path.join(PAGES, 'wedged_seal.svg'))


if __name__ == '__main__':
    print(page())
