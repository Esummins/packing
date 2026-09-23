"""A272 page: docs/residue_map/campaigns/A272-strip-jam/strip_jam.svg -- six panels, one per violator of A267's ring
inequalities (adv271's U3, U4, U5, U6, the U8-minimiser) plus the H1-H3 point where the LEFT-constrained UPPER-case
sup is attained (left272 joint, X flat).  Each panel: the corner (box, T_u dashed, S stipple = the strip, UNDECIDED
here: STRIP_2 is [M] on these points), C / X / A, the best UPPER-case square Q (centre above L_h, LEFT-constrained:
left272) with the terms that stop it, and the DISC-LEMMA sets: Xi+D(1/2) (blue hatch: centres whose inscribed disc
meets X's side), Gam+D(1/2) (red hatch: ... C's side), and the target (P'+D(1/sqrt2)) n {y >= C_top} (thick grey
outline): every centre of a free strip square would have to lie in the target outside both hatched sets -- the
panel's exact check is that this bad-centre set is EMPTY (shapely area < 1e-9).        python pages272.py"""
import json
import math
import os
import sys

import numpy as np
from shapely.geometry import Polygon, box as sbox

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import upper272 as U                                                  # noqa: E402
import left272 as LF                                                  # noqa: E402
import disc272 as DC                                                  # noqa: E402

R, PR = U.R, U.PR
OUT = os.path.join(R.ROOT, 'docs', 'residue_map', 'campaigns', 'A272-strip-jam')
RES = U.RES
SC, H, PW = 130.0, 440.0, 500


def T(p, ox, oy=30):
    return (ox + SC * p[0], oy + H - SC * p[1])


def poly(V, fill, ox, stroke='#333', op=0.6, w=1.2, extra=''):
    pts = ' '.join('%.2f,%.2f' % T(p, ox) for p in V)
    return '<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="%.1f" %s/>' % (pts, fill, op, stroke, w, extra)


def shp(g, fill, ox, stroke='#888', w=0.6, op=1.0):
    return ''.join(poly(np.array(P.exterior.coords)[:-1], fill, ox, op=op, w=w, stroke=stroke)
                   for P in getattr(g, 'geoms', [g]) if P.geom_type == 'Polygon' and P.area > 1e-12)


def text(x, y, s, size=10, extra=''):
    return '<text x="%.1f" y="%.1f" font-size="%d" %s>%s</text>' % (x, y, size, extra, s)


def line(p, q, ox, stroke, extra=''):
    a, b = T(p, ox), T(q, ox)
    return '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1" %s/>' % (a[0], a[1], b[0], b[1], stroke, extra)


def bad_centre_set(q):
    Xi, Gam, P, Ctop = DC.sets(q)
    win = sbox(0, Ctop, 6, 6)
    target = P.buffer(0.5 ** 0.5, 64).intersection(win) if not P.is_empty else P
    bad = target.difference(Xi.buffer(0.5, 64)).difference(Gam.buffer(0.5, 64))
    return Xi, Gam, P, Ctop, target, bad


def panel(q, Qp, tag, title, ox, notes_extra):
    q = np.array(q, float)
    hu, hv, th, xlow, phi, ax, al, side = q
    C, X, A, Tu = R.squares(q)
    S = Polygon(Tu).difference(Polygon(C))
    cond, cons = R.conditions(q), R.constraints(q)
    Xi, Gam, P, Ctop, target, bad = bad_centre_set(q)
    win = sbox(0, 0, 3.5, 3.3)
    g = ['<rect x="%d" y="30" width="%d" height="%d" fill="#fff" stroke="#000" stroke-width="1.5"/>' % (ox, PW - 20, H)]
    g.append(text(ox, 20, '(%s) %s' % (tag, title), 12, 'font-weight="bold"'))
    g.append(shp(Xi.buffer(0.5, 32).intersection(win), 'url(#hb)', ox, stroke='#69c', w=0.8))
    g.append(shp(Gam.buffer(0.5, 32).intersection(win), 'url(#hr)', ox, stroke='#c66', w=0.8))
    g.append(poly(R.BOX, 'none', ox, stroke='#c33', w=1.1, extra='stroke-dasharray="4,3"'))
    g.append(poly(Tu, 'none', ox, stroke='#36c', w=1.2, extra='stroke-dasharray="6,3"'))
    g.append(shp(S, 'url(#stip)', ox))
    g.append(poly(C, '#f3d0d0', ox, stroke='#c33', op=0.9, w=1.6))
    g.append(poly(X, '#d0dcf3', ox, stroke='#36c', op=0.9, w=1.6))
    g.append(poly(A, '#e4e4e4', ox, stroke='#555', op=0.9, w=1.6))
    if not target.is_empty:
        g.append(shp(target, 'none', ox, stroke='#444', w=2.0, op=0.0))
    g.append(line((0, Ctop), (3.4, Ctop), ox, '#999', 'stroke-dasharray="2,3"'))
    g.append(text(*T((2.75, Ctop + 0.03), ox), 'y = C_top', 9, 'fill="#999"'))
    tv = LF.terms_of(q, Qp)
    Q = PR.q_square(Qp)
    g.append(poly(Q, 'none', ox, stroke='#060', w=1.4, extra='stroke-dasharray="2,2"'))
    m = T(Q.mean(axis=0), ox)
    g.append(text(m[0] - 10, m[1] + 4, 'Q', 12, 'fill="#060" font-weight="bold"'))
    for Pp, lab in ((C, 'C'), (X, 'X'), (A, 'A')):
        m = T(Pp.mean(axis=0), ox)
        g.append(text(m[0] - 5, m[1] + 4, lab, 14, 'font-weight="bold"'))
    act = [LF.TERMS[i] for i, v in enumerate(tv) if v - min(tv) <= 2e-3]
    chk = dict(H1_H3_ok=bool(cons.min() >= -1e-9), bad_centre_area=float(bad.area), bad_empty=bool(bad.area < 1e-9),
               t_left=round(float(min(tv)), 5))
    y0 = 30 + H + 14
    notes = ['IS: corner frame; C floater (h_u %.3f, h_v %.3f, %.1f deg), X wall toucher (X_low %.3f, %.1f deg), A floor toucher, side %.3f;' % (hu, hv, th / R.DEG, xlow, phi / R.DEG, side),
             'T_u blue dashed, stipple = S (UNDECIDED: STRIP_2 [M] here); beta = phi - theta = %+.1f deg; margins U3 %+.3f U4 %+.3f U5 %+.3f U6 %+.3f U8 %+.3f.' % (cond['beta_deg'], cond['U3'], cond['U4'], cond['U5'], cond['U6'], cond['U8']),
             'Q (green dashed) = best UPPER-case square (centre above L_h, LEFT-constrained): t = %+.4f < 0, stopped by %s.' % (min(tv), ', '.join(act)),
             'Blue hatch = Xi+D(1/2), red hatch = Gam+D(1/2), thick grey = (P\'+D(1/sqrt2)) above C_top: bad-centre set EMPTY (area %.1e).' % bad.area,
             'Exact checks: H1-H3 (20 SAT/containment terms >= -1e-9): %s; bad-centre set empty: %s.' % (chk['H1_H3_ok'], chk['bad_empty'])] + notes_extra
    for i, t in enumerate(notes):
        g.append(text(ox, y0 + 13 * i, t, 9))
    return ''.join(g), chk


def main():
    os.makedirs(OUT, exist_ok=True)
    adv = json.load(open(os.path.join(U.A271, '..', 'results', 'adv271.json')))['results']
    lf = {r['start']: r for r in json.load(open(os.path.join(RES, 'left272_fixed.json')))['rows']}
    lj = json.load(open(os.path.join(RES, 'left272_joint.json')))
    top = max((r for r in lj['rows'] if r.get('t_left', -9) > -9), key=lambda r: r['t_left'])
    panels = [(adv['U3']['q'], lf['U3']['Q'], 'a', 'violates (U3): X flat over a 34.5-deg C', ['X\'s flat bottom passes 0.001 under C\'s top vertex; the exposed strip is the sliver right of X\'s right edge x = 1.']),
              (adv['U4']['q'], lf['U4']['Q'], 'b', 'violates (U4): room right of X at C_top = 1.30', ['Q must clear X\'s lower-right edge up to its left vertex; that pushes its bottom right of T_u\'s top.']),
              (adv['U5']['q'], lf['U5']['Q'], 'c', 'violates (U5): X at 45 deg over a 2-deg C', ['Same mechanism: the 45-deg edge of X shadows T_u\'s top from every square right of it.']),
              (adv['U6']['q'], lf['U6']['Q'], 'd', 'violates (U6): h_u + cos theta - cos phi = 1.18', ['(U4) fails too (-0.60); Q is still 0.17 short of T_u.']),
              (adv['U8']['q'], lf['U8']['Q'], 'e', '(U8)-minimiser: X_top - C_top = 0.80, a_R < a*', ['T_u\'s top vertex is INSIDE X; the exposed part of S is the tiny triangle right of x = 1 (FAR-SIDE, tau > 1).']),
              (top['q'], top['Q'], 'f', 'sup of the UPPER case under H1-H3 (left272 joint): t = %+.4f' % top['t_left'], ['The worst point of the whole H1-H3 set: X flat, C at 15 deg; the flat Q\'s bottom edge sits ON y = C_top right of x = 1.'])]
    head = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="sans-serif">' % (2 * PW + 40, 3 * (H + 130) + 40),
            '<defs><pattern id="stip" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="2.5" cy="2.5" r="1" fill="#999"/></pattern>',
            '<pattern id="hb" width="6" height="6" patternUnits="userSpaceOnUse"><path d="M0,6 l6,-6" stroke="#69c" stroke-width="0.7"/></pattern>',
            '<pattern id="hr" width="6" height="6" patternUnits="userSpaceOnUse"><path d="M0,0 l6,6" stroke="#c66" stroke-width="0.7"/></pattern></defs>']
    body, checks, ok = [], [], True
    for k, (q, Qp, tag, title, extra) in enumerate(panels):
        ox, oy = 20 + (k % 2) * (PW + 10), (k // 2) * (H + 130)
        gk, chk = panel(q, Qp, tag, title, ox, extra)
        body.append('<g transform="translate(0,%d)">%s</g>' % (oy, gk))
        checks.append(dict(panel=tag, title=title, **chk))
        ok = ok and chk['H1_H3_ok'] and chk['bad_empty']
    open(os.path.join(OUT, 'strip_jam.svg'), 'w').write('\n'.join(head + body + ['</svg>']))
    json.dump(dict(check_passed=ok, panels=checks), open(os.path.join(RES, 'pages272.json'), 'w'), indent=1)
    print('strip_jam.svg written; every panel passes the exact checks:', ok)
    for c in checks:
        print(c)


if __name__ == '__main__':
    main()
