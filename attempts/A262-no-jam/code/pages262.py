"""A262 pages (geometry-checked; a note per panel saying what it IS; slivers with a 10x inset; undecided = grey stipple,
never green).   python pages262.py  ->  docs/residue_map/campaigns/A262-no-jam/
  jam_ring.svg   (a) a RING with ONE JAM corner at s-hat (8 squares, exact check) and the worst free square of its
                 pocket (it contains O);  (b) 10x inset: the floater's sliver in the box;  (c) the RETREAT cone (HELD-JAM)
  jam_two.svg    (a) two OPPOSITE JAM corners at s-hat: the pocket admits NO free square [M, 1 deg];  (b) two ADJACENT
                 JAM corners: the best ring found (a packing if t > 0, otherwise drawn as NOT a packing, overlap red)
"""
import html
import json
import math
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
os.environ.setdefault('JAM_COARSE', '1')
HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import geom262 as G                                                   # noqa: E402
import multi262 as M                                                  # noqa: E402
import fam262 as F                                                    # noqa: E402
import room259 as R                                                   # noqa: E402
from svg261 import BLUE, GREY, ORANGE, RED, Panel, clip              # noqa: E402
Z = G.Z
PAGES = os.path.join(G.ROOT, 'docs', 'residue_map', 'campaigns', 'A262-no-jam')
PURPLE = '#6b46c1'
STIP = ('<defs><pattern id="stip" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" '
        'r="0.9" fill="#a0aec0"/></pattern></defs>')


def container(pn, s):
    pn.poly([(0, 0), (s, 0), (s, s), (0, s)], fill='none', stroke='#1a202c', stroke_width='2.4')
    for bx, by in ((0, 0), (s - 1, 0), (s - 1, s - 1), (0, s - 1)):
        pn.poly([(bx, by), (bx + 1, by), (bx + 1, by + 1), (bx, by + 1)], fill='#faf089', fill_opacity='0.35',
                stroke='#b7791f', stroke_width='0.8', stroke_dasharray='4,3')
    x, y = pn.pt((s / 2, s / 2))
    pn.o.append('<circle cx="%.1f" cy="%.1f" r="3" fill="%s"/><text x="%.1f" y="%.1f" font-size="11">O</text>' % (x, y, RED, x + 5, y - 5))


def draw_ring(pn, Vs, names, s, floaters):
    ok = F.packing_margin(Vs, s) >= -1e-9
    for V, nm in zip(Vs, names):
        pn.sq(V, ORANGE if nm in floaters else BLUE, nm)
    if not ok:
        for i in range(len(Vs)):
            for j in range(i):
                if Z.poly_gap(Vs[i], Vs[j]) < -1e-9:
                    pn.poly(clip(list(map(tuple, Vs[i])), list(map(tuple, Vs[j]))), fill=RED, fill_opacity='0.8', stroke=RED)
    return ok


def best_ring(side):
    rows = [json.loads(l) for l in open(os.path.join(ATT, 'results', 'ring262.jsonl'))]
    rows = [r for r in rows if abs(r['s'] - side) < 1e-9 and r['t'] > 1e-6 and r.get('pierce', -9) > -1.0]
    return max(rows, key=lambda r: r['t'])


def page_ring():
    s = G.SHAT
    r = best_ring(s)
    p = np.array(r['p'])
    Vs = G.verts(p, s)
    assert G.margin(p, s) > 0 and F.packing_margin(Vs, s) >= -1e-9 and G.jam_J(Vs) < 0
    pm, pose, nc = R.pierce_O(None, s, 1.0, Vs=Vs)
    assert pm < 0 and R.free_margin(pose, Vs, s) >= -1e-9 and R.contains_O(pose, s) > 0
    out = [STIP]
    a = Panel(30, 40, s, 95, '(a) a RING with ONE JAM corner, s = s-hat [M, exact check]')
    container(a, s)
    draw_ring(a, Vs, G.NAMES, s, {'C'})
    Cs = R.centre_set(Vs, s, pose[2])
    for Pg in R.polys_of(Cs):
        a.poly(list(Pg.exterior.coords)[:-1], fill=PURPLE, fill_opacity='0.35', stroke=PURPLE, stroke_width='0.8')
    a.sq(Z.sq_verts(*pose), GREY, 'Q', dash='5,3')
    C = Vs[7]
    a.note(['IS: floor row A, A2; right and top rows; left wall carries X ONLY; C FLOATS (%.3f off the wall) and meets the BL box' % C[:, 0].min(),
            'by a sliver (depth %.4f).  JAM margin t = %.4f, J = %.4f (no wall cell receives C).  Purple: exact centre set of' % (G.depth_in_box(C), r['t'], r['J']),
            'free squares at the worst tilt (%.0f deg); Q = the free square of largest miss: pierce margin %.4f < 0, it CONTAINS O.' % (math.degrees(pose[2]), pm),
            'Count: 8 outer + at most 1 (all free squares contain O) = 9 < 11.  [M] on a 1-degree tilt grid -- not a certificate.'])
    P = C[np.argmin(C[:, 1])]
    wx, wy = P[0] - 0.06, P[1] - 0.07
    b = Panel(30 + s * 95 + 40, 40, 0.12, 2400, "(b) 20x inset at C's lowest vertex: the sliver in the box", origin=(wx, wy))
    win = [(wx, wy), (wx + 0.12, wy), (wx + 0.12, wy + 0.12), (wx, wy + 0.12)]
    b.poly(clip(win, [(0, 0), (1, 0), (1, 1), (0, 1)]), fill='#faf089', fill_opacity='0.45', stroke='#b7791f', stroke_width='0.8')
    for V, col in ((Vs[0], BLUE), (C, ORANGE)):
        b.poly(clip(win, list(map(tuple, V))), fill=col, fill_opacity='0.25', stroke=col, stroke_width='1.2')
    b.note(['IS: a 0.12 x 0.12 window.  Yellow = the box (y < 1).  Orange = C: lowest vertex (%.4f, %.4f),' % (P[0], P[1]),
            'inside the box by %.4f.  Blue = A (gap C-A %.4f).  Retreat of length' % (G.depth_in_box(C), Z.poly_gap(C, Vs[0])),
            '<= (1 - %.4f)/sin(tilt) = %.4f takes C off the box: P4 (RETREAT) => C is HELD.' % (P[1], (1 - P[1]) / math.sin(p[10] % (math.pi / 2)))])
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="sans-serif">%s</svg>' % (
        30 + s * 95 + 40 + 420, 40 + s * 95 + 90, ''.join(out + a.o + b.o))
    open(os.path.join(PAGES, 'jam_ring.svg'), 'w', encoding='utf-8').write(svg)
    return dict(t=r['t'], pierce=pm, depth_C=G.depth_in_box(C))


def best_multi(jam, side):
    path = os.path.join(ATT, 'results', 'adv262.jsonl')
    rows = [json.loads(l) for l in open(path)] if os.path.exists(path) else []
    rows = [r for r in rows if tuple(r['jam']) == jam and abs(r['s'] - side) < 1e-9]
    q = json.load(open(os.path.join(ATT, 'results', 'quick_j2.json')))
    if str(jam) in q:
        rows.append(dict(jam=list(jam), s=side, t=q[str(jam)]['t'], p=q[str(jam)]['p']))
    return max(rows, key=lambda r: r['t'])


def page_two():
    s = G.SHAT
    out, body, info = [STIP], [], {}
    for k, (jam, ttl) in enumerate((((3, 1), 'two OPPOSITE JAM corners'), ((3, 0), 'two ADJACENT JAM corners'))):
        r = best_multi(jam, s)
        p = np.array(r['p'])
        Vs, wall, role = M.verts(p, s, jam)
        pn = Panel(30 + k * (s * 95 + 40), 40, s, 95, '(%s) %s, s = s-hat: t = %+.4f' % ('ab'[k], ttl, r['t']))
        container(pn, s)
        ok = draw_ring(pn, Vs, role, s, {x for x in role if x[0] == 'C'})
        if r['t'] > 0:
            assert ok and M.objective(p, s, jam) > 0
            pm, pose, nc = R.pierce_O(None, s, 1.0, Vs=Vs)
            txt = ('NO free square: centre set EMPTY at all 90 tilts: 8 + 0 < 11' if pose is None else
                   'worst free square: pierce margin %.4f (< 0: it contains O): 8 + 1 < 11' % pm)
            if pose is not None:
                pn.sq(Z.sq_verts(*pose), GREY, 'Q', dash='5,3')
            pn.note(['IS: a packing of 8 [M, exact check]: each JAM wall = its START square + a floater.',
                     txt, '[M] 1-degree tilt grid; not a certificate.'])
            info[str(jam)] = dict(t=r['t'], pierce=pm)
        else:
            pn.note(['IS: NOT a packing -- the best structured start after Nelder-Mead; overlaps in red.',
                     'least term t = %.4f < 0: no such ring found at s-hat [M] (adv262.jsonl).' % r['t']])
            info[str(jam)] = dict(t=r['t'])
        body += pn.o
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="sans-serif">%s</svg>' % (
        30 + 2 * (s * 95 + 40), 40 + s * 95 + 80, ''.join(out + body))
    open(os.path.join(PAGES, 'jam_two.svg'), 'w', encoding='utf-8').write(svg)
    return info


if __name__ == '__main__':
    os.makedirs(PAGES, exist_ok=True)
    res = dict(jam_ring=page_ring(), jam_two=page_two())
    json.dump(res, open(os.path.join(ATT, 'results', 'pages262.json'), 'w'), indent=1)
    print(json.dumps(res, indent=1))
