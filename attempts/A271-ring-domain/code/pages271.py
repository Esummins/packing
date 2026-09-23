"""A271 page: docs/residue_map/campaigns/A271-ring-domain/ring_domain.svg -- four panels: (a) a JAM ring's corner with
H1-H3 marked and the DERIVED conditions drawn (L above height 1 by Lemma LOW, X's bottom above 1.4 by (F1), X above
C's upper-left line by (F5) = (U2), a_1 < a* (U1), T_u under X's far edge (U9)); (b)-(d) adv271's exact violators of
(U3), (U4), (U5)/(U6): configurations satisfying H1-H3 on which A267's ring inequalities FAIL -- with the probe's
closest free square (grey stipple = the strip S, undecided there: STRIP_2 is [M] only).  Every panel passes the exact
H1-H3 check written into its note.        python pages271.py"""
import json
import math
import os
import sys

import numpy as np
from shapely.geometry import Polygon, box as sbox

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ringdom271 as R                                                # noqa: E402
import probe271 as PR                                                 # noqa: E402

Z = R.Z
OUT = os.path.join(R.ROOT, 'docs', 'residue_map', 'campaigns', 'A271-ring-domain')
RES = os.path.join(HERE, '..', 'results')
SC, H, PW = 140.0, 470.0, 500


def T(p, ox, oy=30):
    return (ox + SC * p[0], oy + H - SC * p[1])


def poly(V, fill, ox, stroke='#333', op=0.6, w=1.2, extra=''):
    pts = ' '.join('%.2f,%.2f' % T(p, ox) for p in V)
    return '<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="%.1f" %s/>' % (pts, fill, op, stroke, w, extra)


def shp(g, fill, ox):
    return ''.join(poly(np.array(P.exterior.coords)[:-1], fill, ox, op=1.0, w=0.6, stroke='#888')
                   for P in getattr(g, 'geoms', [g]) if P.geom_type == 'Polygon' and P.area > 1e-12)


def text(x, y, s, size=10, extra=''):
    return '<text x="%.1f" y="%.1f" font-size="%d" %s>%s</text>' % (x, y, size, extra, s)


def line(p, q, ox, stroke, extra=''):
    a, b = T(p, ox), T(q, ox)
    return '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1" %s/>' % (a[0], a[1], b[0], b[1], stroke, extra)


def panel(q, Qp, tag, title, ox, notes_extra):
    q = np.array(q, float)
    hu, hv, th, xlow, phi, ax, al, side = q
    C, X, A, Tu = R.squares(q)
    S = Polygon(Tu).difference(Polygon(C))
    cond, cons = R.conditions(q), R.constraints(q)
    g = ['<rect x="%d" y="30" width="%d" height="%d" fill="#fff" stroke="#000" stroke-width="1.5"/>' % (ox, PW - 20, H)]
    g.append(text(ox, 20, '(%s) %s' % (tag, title), 12, 'font-weight="bold"'))
    g.append(poly(R.BOX, 'none', ox, stroke='#c33', w=1.1, extra='stroke-dasharray="4,3"'))
    g.append(poly(Tu, 'none', ox, stroke='#36c', w=1.2, extra='stroke-dasharray="6,3"'))
    g.append(shp(S, 'url(#stip)', ox))
    g.append(poly(C, '#f3d0d0', ox, stroke='#c33', op=0.9, w=1.6))
    g.append(poly(X, '#d0dcf3', ox, stroke='#36c', op=0.9, w=1.6))
    g.append(poly(A, '#e4e4e4', ox, stroke='#555', op=0.9, w=1.6))
    g.append(line((0, 1), (3.3, 1), ox, '#999', 'stroke-dasharray="2,3"'))
    g.append(text(*T((3.0, 1.03), ox), 'y = 1', 9, 'fill="#999"'))
    g.append(line((0, 1.4057), (3.3, 1.4057), ox, '#69c', 'stroke-dasharray="2,3"'))
    g.append(text(*T((2.55, 1.43), ox), 'y = 1.406 <= X_low (F1)', 9, 'fill="#69c"'))
    if Qp is not None:
        Q = PR.q_square(Qp)
        g.append(poly(Q, 'none', ox, stroke='#060', w=1.4, extra='stroke-dasharray="2,2"'))
        m = T(Q.mean(axis=0), ox)
        g.append(text(m[0] - 40, m[1] + 4, 'Q: closest free square', 9, 'fill="#060"'))
    for P, lab in ((C, 'C'), (X, 'X'), (A, 'A')):
        m = T(P.mean(axis=0), ox)
        g.append(text(m[0] - 5, m[1] + 4, lab, 14, 'font-weight="bold"'))
    L = np.array([hu, hv + math.cos(th)])
    m = T(L, ox)
    g.append('<circle cx="%.1f" cy="%.1f" r="6" fill="none" stroke="#000"/>' % m)
    g.append(text(m[0] + 8, m[1] + 3, 'L: L_h = %.3f (LOW: >= 1.121)' % L[1], 9))
    chk = dict(H1_H3_all_ok=bool(cons.min() >= -1e-9), min_term=round(float(cons.min()), 6))
    y0 = 30 + H + 14
    notes = ['IS: corner frame (wall = left edge, floor = bottom edge); red dashed = the open box; C floater (h_u %.3f, h_v %.3f, %.1f deg),' % (hu, hv, th / R.DEG),
             'X wall toucher (X_low %.3f, %.1f deg), A floor toucher (a_x %.3f, %.1f deg), side %.3f; T_u blue dashed; stipple = S (UNDECIDED here' % (xlow, phi / R.DEG, ax, al / R.DEG, side),
             'unless (U3)-(U6)+(U8) hold: grey, never green).  Margins: D1 %+.4f D2 %+.4f U1 %+.3f U2 %+.4f U3 %+.3f U4 %+.3f U5 %+.3f U6 %+.3f U8 %+.3f U9 %+.3f' % tuple(cond[k] for k in R.COND),
             'beta = phi - theta = %+.1f deg.  Exact H1-H3 check (20 SAT / containment terms): %s' % (cond['beta_deg'], chk)] + notes_extra
    for i, t in enumerate(notes):
        g.append(text(ox, y0 + 13 * i, t, 9))
    return ''.join(g), chk['H1_H3_all_ok']


def main():
    os.makedirs(OUT, exist_ok=True)
    adv = json.load(open(os.path.join(RES, 'adv271.json')))['results']
    chk = json.load(open(os.path.join(RES, 'check271.json')))['rows']
    ring = [r for r in chk if r['id'].startswith('jam261_polished|3.877084|0.95,26.0,0.95')][0]
    probe = {r['start']: r for r in json.load(open(os.path.join(RES, 'probe271_two.json')))['rows']}
    panels = [(ring['q'], None, 'a', 'JAM ring %s: H1-H3 and the five DERIVED conditions' % ring['id'].split('|')[2],
               ['DERIVED [T]: L above y = 1 (Lemma LOW), X_low > 1.406 (F1), X above C\'s upper-left line = (U2) (BLOCKER-SIDE mirror), a_1 < a* (U1), T_u under X\'s far edge (U9).']),
              (adv['U3']['q'], probe['U3']['Q'] if 'U3' in probe else None, 'b', 'violates (U3): X flat, C at 34.5 deg -- a wedge 0.69 wide at L',
               ['NOT DERIVED: (U3) a_2 - a* = %.3f < w_max/2 = %.3f.  probe271: best free square t = %+.4f < 0 -- no free strip square (STRIP_2 [M] true here).' % (adv['U3']['q'] and R.conditions(adv['U3']['q'])['a_R'] * 0 + (min(R.conditions(adv['U3']['q'])['a_R'], 1) - R.conditions(adv['U3']['q'])['a_star']), R.conditions(adv['U3']['q'])['w_max'] / 2, probe['U3']['t_fixed'])]),
              (adv['U4']['q'], probe['U4']['Q'] if 'U4' in probe else None, 'c', 'violates (U4): room right of X at C\'s top = 1.30 (h_u 0.82, beta 18 deg)',
               ['NOT DERIVED: (U4) fails by 0.300 (rho(C_top) = 1.30 >= 1).  probe271: t = %+.4f (h_v = 0.998: the box square touches T_u from below, the OPEN boundary).' % probe['U4']['t_fixed']]),
              (adv['U5']['q'], probe['U5']['Q'] if 'U5' in probe else None, 'd', 'violates (U5): X at 45 deg over a 2-deg C -- S\'s top corner exposed beyond X',
               ['NOT DERIVED: (U5) a_R - sin beta - a* = %.3f; (U6) violator (h_u 0.90, phi 45) is the same picture with C further out.  probe271: t = %+.4f.' % (adv['U5']['margin'], probe['U5']['t_fixed'])])]
    head = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="sans-serif">' % (2 * PW + 40, 2 * (H + 130) + 40),
            '<defs><pattern id="stip" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="2.5" cy="2.5" r="1" fill="#999"/></pattern></defs>']
    body, ok = [], True
    for k, (q, Qp, tag, title, extra) in enumerate(panels):
        ox, oy = 20 + (k % 2) * (PW + 10), (k // 2) * (H + 130)
        gk, okk = panel(q, Qp, tag, title, ox, extra)
        body.append('<g transform="translate(0,%d)">%s</g>' % (oy, gk))
        ok = ok and okk
    open(os.path.join(OUT, 'ring_domain.svg'), 'w').write('\n'.join(head + body + ['</svg>']))
    json.dump(dict(panels=[p[3] for p in panels], check_passed=ok), open(os.path.join(RES, 'pages271.json'), 'w'), indent=1)
    print('ring_domain.svg written; exact H1-H3 check passed on every panel:', ok)


if __name__ == '__main__':
    main()
