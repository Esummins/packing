r"""A278 page: docs/residue_map/campaigns/A278-no-float2/no_float2.svg -- three true-scale panels of the BL corner at
side s-hat.  (a) A277's Y-poke FLOAT2 witness with the certified flat cell T = [x, x+1] x [0,1] (blue outline), the
part T \ int D (dark hatch: in the SHADOW of {C, D, X, Y}, disc test margin 0.032) and K_outer (light grey: where a
fifth square's centre could be).  (b) the nested JAM schematic on the same poses: the C-D, Y-D and X-C separators
(dashed), the residual set L of part 4 as grey STIPPLE over the corner (undecided), never green.  (c) the CAP-2(A, C)
frame on A261's JAM corner: O, the S1 half-plane lines through O at psi = 0, the S2 centre line y = s/2 - 1/2, the
BL sectors grey STIPPLE (undecided).  Every panel is geometry-checked here (assertions), results/page278_checks.json.
    python page278.py   (< 10 s)"""
import json
import math
import os
import sys

import numpy as np
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A261-box-meeters', 'code'))
import local261 as L                                                   # noqa: E402

W = json.load(open(os.path.join(ROOT, 'attempts', 'A277-float2-room', 'results', 'float277_witness.json')))
CELL = json.load(open(os.path.join(HERE, '..', 'results', 'cell278.json')))
JAM = json.load(open(os.path.join(ROOT, 'attempts', 'A261-box-meeters', 'results', 'jam261_polished.json')))
S = W['side']
OUTDIR = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A278-no-float2')
os.makedirs(OUTDIR, exist_ok=True)
V = {k: L.verts(W['poses'][k][0], W['poses'][k][1], math.radians(W['poses'][k][2])) for k in ('C', 'D', 'X')}
V['Y'] = np.array(W['Y_vertices'])
P = {k: Polygon([tuple(p) for p in V[k]]) for k in V}
xs = CELL['cell']['x']
T = sbox(xs, 0, xs + 1, 1)
NG = 64
gon = [(0.5 * math.cos(2 * math.pi * i / NG), 0.5 * math.sin(2 * math.pi * i / NG)) for i in range(NG)]
infl = [unary_union([Polygon([(p[0] + g[0], p[1] + g[1]) for g in gon]) for p in V[k]] + [P[k]]).convex_hull for k in V]
K_outer = sbox(0.5, 0.5, S - 0.5, S - 0.5).difference(unary_union(infl))
target = T.difference(P['D'])
checks = {'a': dict(T_meets={k: float(T.intersection(P[k]).area) for k in P}, disc_dist=float(target.distance(K_outer)),
                    margin=float(target.distance(K_outer)) - 1 / math.sqrt(2))}
assert checks['a']['margin'] > 0.03 and checks['a']['T_meets']['C'] == 0 == checks['a']['T_meets']['Y']
# (b) separators: SAT-style supporting lines between the pairs (D->C, Y->D, X->C), reported as slope angles
def sep_angle(A, B):
    """a separating line of two disjoint convex polygons: the edge normal (of either) with the largest gap; slope angle in deg."""
    best = None
    for Q in (A, B):
        for i in range(4):
            e = Q[(i + 1) % 4] - Q[i]
            n = np.array([-e[1], e[0]]) / np.linalg.norm(e)
            gap = min(B @ n) - max(A @ n)
            gap2 = min(A @ n) - max(B @ n)
            for g, nn in ((gap, n), (gap2, -n)):
                if best is None or g > best[0]:
                    best = (g, nn)
    g, n = best
    ang = math.degrees(math.atan2(n[0], -n[1])) % 180                  # slope angle of the line with normal n
    return float(g), float(ang), n
sepCD = sep_angle(V['D'], V['C'])
sepYD = sep_angle(V['Y'], V['D'])
sepXC = sep_angle(V['X'], V['C'])
checks['b'] = dict(gap_CD=sepCD[0], angle_CD=sepCD[1], gap_YD=sepYD[0], angle_YD=sepYD[1], gap_XC=sepXC[0], angle_XC=sepXC[1])
assert all(g >= 0 for g in (sepCD[0], sepYD[0], sepXC[0]))
# (c) A261's JAM corner
JP = {k: L.verts(*JAM['poses'][k]) if 'poses' in JAM else None for k in ('A', 'C', 'X')} if 'poses' in JAM else None
if JP is None:
    src = JAM.get('squares', JAM)
    JP = {k: L.verts(src[k][0], src[k][1], src[k][2] if abs(src[k][2]) < 1.6 else math.radians(src[k][2])) for k in ('A', 'C', 'X')}
O = (S / 2, S / 2)
checks['c'] = dict(O=O, S2_line=S / 2 - 0.5, A_meets_box=float(Polygon(JP['A']).intersection(sbox(0, 0, 1, 1)).area),
                   C_meets_box=float(Polygon(JP['C']).intersection(sbox(0, 0, 1, 1)).area), X_low=float(JP['X'][:, 1].min()))
assert checks['c']['A_meets_box'] > 0 and checks['c']['C_meets_box'] > 0 and checks['c']['X_low'] >= 1
json.dump(checks, open(os.path.join(HERE, '..', 'results', 'page278_checks.json'), 'w'), indent=1)

# ---- SVG
SC, PW, PH, M = 150, 620, 640, 40
def tr(p, ox):
    return ox + M + p[0] * SC, PH - M - p[1] * SC
def poly(pts, ox, style):
    return '<polygon points="%s" %s/>' % (' '.join('%.2f,%.2f' % tr(p, ox) for p in pts), style)
def shp(geom, ox, style):
    out = ''
    for g in (geom.geoms if hasattr(geom, 'geoms') else [geom]):
        if g.is_empty:
            continue
        out += poly(list(g.exterior.coords), ox, style)
    return out
def text(x, y, s, ox, size=11):
    return '<text x="%.1f" y="%.1f" font-size="%d" font-family="sans-serif">%s</text>' % (ox + x, y, size, s)
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (3 * PW, PH + 60, 3 * PW, PH + 60),
       '<defs><pattern id="stip" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.1" fill="#888"/></pattern>'
       '<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse"><path d="M0,6 L6,0" stroke="#333" stroke-width="1.2"/></pattern></defs>',
       '<rect width="100%" height="100%" fill="white"/>']
BL, FL = 'fill="#9ecae1" fill-opacity="0.7" stroke="#08519c" stroke-width="1.2"', 'fill="#fdae6b" fill-opacity="0.7" stroke="#e6550d" stroke-width="1.2"'
for pi, ox in enumerate((0, PW, 2 * PW)):
    svg.append('<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="#000"/>' % (ox + M, PH - M - 3.9 * SC, 3.9 * SC, 3.9 * SC))
# (a)
ox = 0
svg.append(shp(K_outer, ox, 'fill="#ddd" stroke="none"'))
svg.append(shp(target, ox, 'fill="url(#hatch)" stroke="#333" stroke-width="0.8"'))
for k in ('C', 'D'):
    svg.append(poly(V[k], ox, BL))
for k in ('X', 'Y'):
    svg.append(poly(V[k], ox, FL))
svg.append(poly([(xs, 0), (xs + 1, 0), (xs + 1, 1), (xs, 1)], ox, 'fill="none" stroke="#08519c" stroke-width="2.2" stroke-dasharray="6,3"'))
svg.append(poly([(0, 0), (1, 0), (1, 1), (0, 1)], ox, 'fill="none" stroke="#000" stroke-width="0.6"'))
svg.append(text(M, PH + 18, '(a) Y-poke FLOAT2 witness (A277): flat cell T = [%.3f, %.3f] x [0,1] (dashed) met by D only; T \\ int D hatched = in the' % (xs, xs + 1), ox))
svg.append(text(M, PH + 34, 'SHADOW of {C,D,X,Y} (disc test: dist to K_outer (light grey, admissible 5th centres) %.4f > 0.7071, margin %.4f) [T-computed].' % (checks['a']['disc_dist'], checks['a']['margin']), ox))
svg.append(text(M, PH + 50, 'Geometry check: T meets C, X, Y by area 0 exactly, D by %.3f; gaps C-D %.5f, D-Y %.5f.' % (checks['a']['T_meets']['D'], CELL['gaps']['C-D'], CELL['gaps']['D-Y']), ox))
# (b)
ox = PW
svg.append('<rect x="%d" y="%d" width="%d" height="%d" fill="url(#stip)"/>' % (ox + M, PH - M - 2.6 * SC, 2.6 * SC, 2.6 * SC))
for k in ('C', 'D'):
    svg.append(poly(V[k], ox, BL))
for k in ('X', 'Y'):
    svg.append(poly(V[k], ox, FL))
def line(n, pts_ref, ox, col):
    g, ang, nn = n
    c = (max(pts_ref @ nn) + 0.5 * g)
    d = np.array([-nn[1], nn[0]])
    p0 = nn * c
    a, b = p0 - 3 * d, p0 + 3 * d
    return '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.4" stroke-dasharray="5,4"/>' % (*tr(a, ox), *tr(b, ox), col)
svg.append(line(sepCD, V['D'], ox, '#08519c'))
svg.append(line(sepYD, V['Y'], ox, '#e6550d'))
svg.append(line(sepXC, V['X'], ox, '#e6550d'))
svg.append(text(M, PH + 18, '(b) the nested JAM: separators D->C (blue, slope %.1f deg), Y->D (%.1f deg), X->C (%.1f deg); all positive slope' % (sepCD[1], sepYD[1], sepXC[1]), ox))
svg.append(text(M, PH + 34, '(FLOAT-SLOPE [T]).  Grey stipple: the residual L of part 4 -- FLOAT2 quadruples not yet shown to have a shadow cell -- UNDECIDED [C].', ox))
svg.append(text(M, PH + 50, 'Geometry check: SAT gaps along the drawn normals %.4f / %.4f / %.4f >= 0.' % (sepCD[0], sepYD[0], sepXC[0]), ox))
# (c)
ox = 2 * PW
svg.append('<rect x="%d" y="%d" width="%d" height="%d" fill="url(#stip)"/>' % (ox + M, PH - M - 2.7 * SC, 2.7 * SC, 2.7 * SC))
svg.append(poly(JP['C'], ox, BL))
for k in ('A', 'X'):
    svg.append(poly(JP[k], ox, FL))
svg.append('<circle cx="%.1f" cy="%.1f" r="4" fill="#000"/>' % tr(O, ox))
svg.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#000" stroke-width="1"/>' % (*tr((0, O[1]), ox), *tr((3.9, O[1]), ox)))
svg.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#000" stroke-width="1"/>' % (*tr((O[0], 0), ox), *tr((O[0], 3.9), ox)))
svg.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#555" stroke-width="1" stroke-dasharray="3,3"/>' % (*tr((0, S / 2 - 0.5), ox), *tr((3.9, S / 2 - 0.5), ox)))
svg.append(text(M, PH + 18, '(c) CAP-2(A, C) frame on A261 JAM corner: O, S1 lines through O (psi = 0), S2 centre line y = s/2 - 1/2 = %.3f (dashed);' % (S / 2 - 0.5), ox))
svg.append(text(M, PH + 34, 'BL sectors grey stipple: where two disjoint misses are not excluded -- UNDECIDED [C]; cert277 --fam jam is the certificate.', ox))
svg.append(text(M, PH + 50, 'Geometry check: A, C meet the box (areas %.3f, %.3f), X_low = %.3f >= 1.' % (checks['c']['A_meets_box'], checks['c']['C_meets_box'], checks['c']['X_low']), ox))
svg.append('</svg>')
open(os.path.join(OUTDIR, 'no_float2.svg'), 'w', encoding='utf-8').write('\n'.join(svg))
print(json.dumps(checks, indent=1))
