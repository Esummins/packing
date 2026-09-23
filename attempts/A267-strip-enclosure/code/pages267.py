"""A267 page: docs/residue_map/campaigns/A267-strip-enclosure/enclosure.svg -- the ENCLOSURE of the strip on two JAM
rings (wall, floor, the empty corner box, A, C, X, T_u dashed, S stippled, the C-X and A-C gaps with 10x insets, the
closest free square below C from approach267).  Every square is the ring's own (geom262.verts) and passes the exact
check written into the panel note (X, C interior-disjoint; X meets int T_u; C meets the open box; A's area in the
band [0, h_u] x [h_v - 0.6, h_v] = 0; the drawn square Q* is interior-disjoint from C and X, in the quadrant, and overlaps A -- said in the note).
    python pages267.py"""
import json
import math
import os
import sys

import numpy as np
from shapely.geometry import Polygon, box as sbox

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
import measure267 as M                                                # noqa: E402
Z = M.Z
OUT = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A267-strip-enclosure')
RES = os.path.join(HERE, '..', 'results')
IDS = ['jam261_polished|3.877084|0.95,26.0,0.95,6.0', 'jam261_polished|3.877084|0.95,26.0,0.55,26.0']
SC, H, PW = 150.0, 520.0, 560


def T(p, ox, oy=30, sc=SC, o=(0.0, 0.0)):
    return (ox + sc * (p[0] - o[0]), oy + H - sc * (p[1] - o[1]))


def poly(V, fill, stroke='#333', op=0.5, w=1.2, extra='', **kw):
    pts = ' '.join('%.2f,%.2f' % T(p, **kw) for p in V)
    return '<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="%.1f" %s/>' % (pts, fill, op, stroke, w, extra)


def shp(g, fill, **kw):
    out = []
    for Pg in getattr(g, 'geoms', [g]):
        if Pg.geom_type == 'Polygon' and Pg.area > 1e-12:
            out.append(poly(np.array(Pg.exterior.coords)[:-1], fill, op=1.0, w=0.6, stroke='#c80', **kw))
    return ''.join(out)


def text(x, y, s, size=11, extra=''):
    return '<text x="%.1f" y="%.1f" font-size="%d" font-family="sans-serif" %s>%s</text>' % (x, y, size, extra, s)


def inset(V_list, centre, ox, oy, size=150, mag=10.0, label=''):
    """10x inset around `centre` (data coords), clipped to a square of `size` px."""
    sc = SC * mag
    half = size / 2.0 / sc
    o = (centre[0] - half, centre[1] - half)
    cid = 'clip%d%d' % (int(ox), int(oy))
    g = ['<clipPath id="%s"><rect x="%d" y="%d" width="%d" height="%d"/></clipPath>' % (cid, ox, oy, size, size),
         '<g clip-path="url(#%s)">' % cid]
    for V, fill, stroke in V_list:
        pts = ' '.join('%.2f,%.2f' % (ox + sc * (p[0] - o[0]), oy + size - sc * (p[1] - o[1])) for p in V)
        g.append('<polygon points="%s" fill="%s" fill-opacity="0.35" stroke="%s" stroke-width="1.2"/>' % (pts, fill, stroke))
    g.append('</g><rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="#000"/>' % (ox, oy, size, size))
    g.append(text(ox + 3, oy + size + 13, label, 10))
    return ''.join(g)


def panel(rid, ox, tag):
    r = [q for q in M.rings() if q['id'] == rid][0]
    V = M.G.verts(r['p'], r['s'])
    A, X, C = V[0], V[6], V[7]
    row = [q for q in json.load(open(os.path.join(RES, 'measure267.json')))['rows'] if q['id'] == rid][0]
    ap = [q for q in json.load(open(os.path.join(RES, 'approach267.json')))['rows'] if q['id'] == rid][0]
    hu, hv, c, s = row['h_u'], row['h_v'], row['c'], row['sn']
    Tu = C - np.array([hu, 0.0])
    S = Polygon(Tu).difference(Polygon(C))
    Q = Z.sq_verts(ap['q'][0], ap['q'][1], ap['psi_deg'] * M.DEG)
    kw = dict(ox=ox)
    g = ['<rect x="%d" y="30" width="%d" height="%d" fill="#fff" stroke="#000" stroke-width="1.5"/>' % (ox, PW - 30, H)]
    g.append(text(ox, 20, '(%s) JAM ring %s -- the enclosure of the strip S' % (tag, rid.split('|')[0] + ' ' + rid.split('|')[2]), 12, 'font-weight="bold"'))
    # wall and floor are the panel's left and bottom edges
    g.append(poly(M.G.BOX, 'none', stroke='#c33', w=1.2, extra='stroke-dasharray="4,3"', **kw))
    g.append(poly(Tu, 'none', stroke='#36c', w=1.3, extra='stroke-dasharray="6,3"', **kw))
    g.append(shp(S, 'url(#stip)', **kw))
    g.append(poly(C, '#f3d0d0', stroke='#c33', op=0.9, w=1.8, **kw))
    g.append(poly(X, '#d0dcf3', stroke='#36c', op=0.9, w=1.8, **kw))
    g.append(poly(A, '#e4e4e4', stroke='#555', op=0.9, w=1.8, **kw))
    g.append(poly(Q, 'none', stroke='#060', w=1.6, extra='stroke-dasharray="2,2"', **kw))
    for P, lab in ((C, 'C'), (X, 'X'), (A, 'A')):
        m = T(P.mean(axis=0), **kw)
        g.append(text(m[0] - 5, m[1] + 4, lab, 14, 'font-weight="bold"'))
    m = T(np.array([hu / 2 + 0.05, hv + 0.55]), **kw)
    g.append(text(m[0] - 4, m[1], 'S', 13, 'fill="#c80" font-weight="bold"'))
    m = T(np.array([0.3, 0.45]), **kw)
    g.append(text(m[0], m[1], 'empty corner box', 10, 'fill="#c33"'))
    m = T(Q.mean(axis=0), **kw)
    g.append(text(m[0] - 30, m[1] + 4, 'Q* (free of C, X; d=%.3f)' % ap['dist'], 10, 'fill="#060"'))
    L = np.array([hu, hv + c])
    m = T(L, **kw)
    g.append('<circle cx="%.1f" cy="%.1f" r="9" fill="none" stroke="#000" stroke-width="0.8"/>' % m)
    ac = (Polygon(A).exterior.interpolate(Polygon(A).exterior.project(Polygon(C).centroid)))   # a point of A near C
    pa = np.array(Polygon(C).exterior.interpolate(Polygon(C).exterior.project(ac)).coords[0])
    m = T(pa, **kw)
    g.append('<circle cx="%.1f" cy="%.1f" r="9" fill="none" stroke="#000" stroke-width="0.8"/>' % m)
    # insets
    g.append(inset([(C, '#f3d0d0', '#c33'), (X, '#d0dcf3', '#36c'), (Tu, 'none', '#36c')], L, ox + PW - 200, 40,
                   label='10x: the C-X gap at L (SAT gap %.4f)' % row['gap_CX']))
    g.append(inset([(C, '#f3d0d0', '#c33'), (A, '#e4e4e4', '#555'), (Tu, 'none', '#36c')], pa, ox + PW - 200, 215,
                   label='10x: the A-C gap (SAT gap %.4f)' % row['gap_CA']))
    # geometry check
    Pa, Pc, Px, Pt = Polygon(A), Polygon(C), Polygon(X), Polygon(Tu)
    chk = dict(XC_disjoint=Z.poly_gap(X, C) >= -1e-12, X_meets_Tu=Px.intersection(Pt).area > 1e-9,
               C_meets_box=Pc.intersection(sbox(0, 0, 1, 1)).area > 0,
               A_band_zero=Pa.intersection(sbox(0, hv - 0.6, hu, hv)).area < 1e-12,
               Q_free_of_CX=min(Z.poly_gap(Q, C), Z.poly_gap(Q, X)) >= -1e-9 and Q.min() >= -1e-9,
               Q_overlaps_A=Z.poly_gap(Q, A) < 0,
               Q_misses_S=-Z.poly_gap(Q, Tu) <= 0)
    y0 = 30 + H + 16
    notes = ['IS: corner frame (wall x=0 = left edge, floor y=0 = bottom edge); red dashed = the open corner box (0,1)^2, EMPTY;',
             'C = the floater (h_u=%.3f, h_v=%.4f, tilt %.1f deg, meets the box by area %.1e); X = the wall toucher above C' % (hu, hv, row['theta_deg'], row['C_box_area']),
             '(tilt %.1f deg, lowest point %.3f, meets T_u by area %.3f); A = the floor START square (x_min %.3f > h_u: its area in' % (row['phi_X_deg'], row['X_low'], row['X_meets_Tu_area'], row['A_xmin']),
             'the band [0,h_u] x [h_v-0.6,h_v] is 0); T_u = C dropped onto the wall (blue dashed); stipple = the STRIP S = T_u minus C.',
             'Circles: the two gaps (C-X at L, width %.4f; A-C, width %.4f), 10x insets at the right.  Q* (green dashed) = the closest' % (row['gap_CX'], row['gap_CA']),
             'unit square free of C and X (the TWO-obstacle statement) in the quadrant to the strip (approach267, 1-deg tilts): distance %.3f,' % ap['dist'],
             'tilt %.0f deg, it touches %s -- and it OVERLAPS A (SAT gap %.2f): the ring itself fills case (iii) with A; without A the entry' % (ap['psi_deg'], '+'.join(ap['touches']), Z.poly_gap(Q, A)),
             'from the corner box is what Lemma WEDGE-FLOAT (strip_enclosure.md s.1) excludes, and it still misses S by 0.05-0.17.  Geometry check: ' + ', '.join('%s %s' % kv for kv in chk.items()),
             'check passed: %s' % all(chk.values())]
    for i, t in enumerate(notes):
        g.append(text(ox, y0 + 14 * i, t, 10))
    return ''.join(g), all(chk.values())


def main():
    os.makedirs(OUT, exist_ok=True)
    head = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="sans-serif">' % (2 * PW + 40, H + 175),
            '<defs><pattern id="stip" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="2.5" cy="2.5" r="1" fill="#c80"/></pattern></defs>']
    body, ok = [], True
    for k, rid in enumerate(IDS):
        gk, okk = panel(rid, 20 + k * (PW + 10), 'ab'[k])
        body.append(gk)
        ok = ok and okk
    open(os.path.join(OUT, 'enclosure.svg'), 'w').write('\n'.join(head + body + ['</svg>']))
    json.dump(dict(rings=IDS, check_passed=ok), open(os.path.join(RES, 'pages267.json'), 'w'), indent=1)
    print('enclosure.svg written; geometry check passed:', ok)


if __name__ == '__main__':
    main()
