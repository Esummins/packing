r"""A279 page: docs/residue_map/campaigns/A279-nest-residual/nest_residual.svg -- two panels.
(a) A277's Y-poke FLOAT2 witness (true scale, BL corner) with the three separator ARCS drawn at their extreme angles
    (D->C alpha, Y->D eta, X->C xi; computed exactly by nest279.arc), the NEST inequality read off (it FAILS here:
    eta_+ > alpha_-, so SWEEP lands D), and the candidate cells of part 2.6: N_Y = Y - sec(a) e_x (Y's left normal
    cell) and N_X = X - sec(phi) e_y, each geometry-checked (inside the container? which squares meet it?).
(b) the (tan eta, tan alpha) plane: the region EXCLUDED by (Sigma) [T] with the offset bounds 2.62 / 1.21 (part 3.1)
    in dark hatch, the NEST-impossible half (eta >= alpha) in light grey, the rest GREY STIPPLE = undecided [C].
Every drawn claim is asserted here; numbers to results/page279_checks.json.   python page279.py  (< 10 s)"""
import json, math, os, sys
import numpy as np
from shapely.geometry import Polygon, box as sbox
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
import nest279 as N; L = N.L; G8 = N.G8                                   # noqa: E402
W = json.load(open(os.path.join(ROOT, 'attempts', 'A277-float2-room', 'results', 'float277_witness.json')))
S = W['side']; OUTDIR = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A279-nest-residual'); os.makedirs(OUTDIR, exist_ok=True)
V = {k: L.verts(W['poses'][k][0], W['poses'][k][1], math.radians(W['poses'][k][2])) for k in ('C', 'D', 'X')}
V['Y'] = np.array(W['Y_vertices']); P = [V['C'], V['D'], V['X'], V['Y']]
nm, arcs = N.nest(P)
assert arcs['alpha'] and arcs['eta'] and arcs['xi'] and nm < 0 and arcs['eta'][1] > arcs['alpha'][0]   # NEST fails on the witness
# candidate cells on the witness
a = math.radians(77.21); phi = math.radians(W['poses']['X'][2])
NY = V['Y'] - np.array([1 / math.cos(a), 0.0]); NX = V['X'] - np.array([0.0, 1 / math.cos(phi)])
def meets(T):
    return {k: float(max(0.0, G8.depth(V[k], T))) for k in V}
chk = dict(side=S, nest_margin=nm, arcs=arcs, N_Y=dict(x_min=float(NY[:, 0].min()), in_container=bool(NY.min() >= -1e-9), meets=meets(NY)),
           N_X=dict(y_min=float(NX[:, 1].min()), in_container=bool(NX.min() >= -1e-9), meets=meets(NX)))
assert not chk['N_Y']['in_container']                       # Y steep (77 deg): sec a = 4.5, N_Y is outside the container
assert chk['N_X']['in_container'] and chk['N_X']['meets']['C'] > 0
# (b) exclusion map
def excluded(te, ta):                                        # (Sigma) with the offset bounds, sec >= 1
    return 2.62 * te + 1.21 * max(ta - te, 0.0) <= math.sqrt(1 + ta * ta) + math.sqrt(1 + te * te) - 0.5 - 1 / math.sqrt(2)
grid = [(te, ta) for te in np.arange(0.0, 3.0, 0.05) for ta in np.arange(0.0, 3.0, 0.05) if te < ta]
exc = [(te, ta) for te, ta in grid if excluded(te, ta)]
chk['sigma_excluded'] = dict(fraction_of_nest_half=len(exc) / len(grid), max_tan_alpha_excluded_at_eta0=max([ta for te, ta in exc if te == 0.0]))
assert chk['sigma_excluded']['max_tan_alpha_excluded_at_eta0'] >= 0.3
json.dump(chk, open(os.path.join(HERE, '..', 'results', 'page279_checks.json'), 'w'), indent=1)
# ---- SVG
SC, PW, PH, M = 150, 620, 640, 40
def tr(p, ox): return ox + M + p[0] * SC, PH - M - p[1] * SC
def poly(pts, ox, style): return '<polygon points="%s" %s/>' % (' '.join('%.2f,%.2f' % tr(p, ox) for p in pts), style)
def text(x, y, s, ox, size=11): return '<text x="%.1f" y="%.1f" font-size="%d" font-family="sans-serif">%s</text>' % (ox + x, y, size, s)
def line_at(pt, ang_deg, ox, col, dash='5,4'):
    d = np.array([math.cos(math.radians(ang_deg)), math.sin(math.radians(ang_deg))]); A, B = np.array(pt) - 3 * d, np.array(pt) + 3 * d
    return '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.3" stroke-dasharray="%s"/>' % (*tr(A, ox), *tr(B, ox), col, dash)
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (2 * PW, PH + 76, 2 * PW, PH + 76),
       '<defs><pattern id="stip" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.1" fill="#888"/></pattern>'
       '<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse"><path d="M0,6 L6,0" stroke="#333" stroke-width="1.2"/></pattern></defs>',
       '<rect width="100%" height="100%" fill="white"/>']
BL, FL = 'fill="#9ecae1" fill-opacity="0.7" stroke="#08519c" stroke-width="1.2"', 'fill="#fdae6b" fill-opacity="0.7" stroke="#e6550d" stroke-width="1.2"'
ox = 0
svg.append('<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="#000"/>' % (ox + M, PH - M - 3.9 * SC, 3.9 * SC, 3.9 * SC))
svg.append('<rect x="%d" y="%d" width="%d" height="%d" fill="url(#stip)"/>' % (ox + M, PH - M - 2.6 * SC, 2.6 * SC, 2.6 * SC))
for k in ('C', 'D'): svg.append(poly(V[k], ox, BL))
for k in ('X', 'Y'): svg.append(poly(V[k], ox, FL))
svg.append(poly(NX, ox, 'fill="none" stroke="#08519c" stroke-width="2" stroke-dasharray="6,3"'))
svg.append(poly([(0, 0), (1, 0), (1, 1), (0, 1)], ox, 'fill="none" stroke="#000" stroke-width="0.6"'))
# separator lines through the contact-side vertices at the arc ends
cD, cC, cY, cX = V['D'].mean(0), V['C'].mean(0), V['Y'].mean(0), V['X'].mean(0)
svg.append(line_at(0.5 * (cD + cC), arcs['alpha'][0], ox, '#08519c')); svg.append(line_at(0.5 * (cD + cC), arcs['alpha'][1], ox, '#08519c', '2,3'))
svg.append(line_at(0.5 * (cD + cY), arcs['eta'][0], ox, '#e6550d')); svg.append(line_at(0.5 * (cD + cY), arcs['eta'][1], ox, '#e6550d', '2,3'))
svg.append(line_at(0.5 * (cC + cX), arcs['xi'][0], ox, '#31a354')); svg.append(line_at(0.5 * (cC + cX), arcs['xi'][1], ox, '#31a354', '2,3'))
svg.append(text(M, PH + 18, '(a) A277 witness, arcs: alpha [%.1f, %.1f], eta [%.1f, %.1f], xi [%.1f, %.1f] deg (lines through the pair midpoints, at the arc ends).' % (*arcs['alpha'], *arcs['eta'], *arcs['xi']), ox))
svg.append(text(M, PH + 34, 'NEST fails here (eta+ %.1f > alpha- %.1f): SWEEP lands D [T].  N_X = X - sec(phi) e_y (dashed) meets C by %.3f: a cell for C iff D, Y miss it (D: %.3f).' % (arcs['eta'][1], arcs['alpha'][0], chk['N_X']['meets']['C'], chk['N_X']['meets']['D']), ox))
svg.append(text(M, PH + 50, 'N_Y = Y - sec(a) e_x is OUTSIDE the container (x_min %.2f): Y is steep.  Grey stipple = the NEST sub-residual: UNDECIDED [C], no NEST quadruple found yet [M].' % chk['N_Y']['x_min'], ox))
svg.append(text(M, PH + 66, 'Geometry check: all arcs computed exactly (golden section + bisection on the support functions); every drawn cell tested by SAT against the four squares.', ox))
ox = PW; SB = 150.0                                        # (b): tan eta in [0,3] -> x, tan alpha in [0,3] -> y
def trb(te, ta): return ox + M + te * SB, PH - M - ta * SB
svg.append('<rect x="%d" y="%d" width="%d" height="%d" fill="url(#stip)"/>' % (ox + M, PH - M - 3 * SB, 3 * SB, 3 * SB))
svg.append('<polygon points="%s" fill="#ddd"/>' % ' '.join('%.1f,%.1f' % trb(*p) for p in [(0, 0), (3, 3), (3, 0)]))
for te, ta in exc:
    x, y = trb(te, ta); svg.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="url(#hatch)"/>' % (x, y - 0.05 * SB, 0.05 * SB, 0.05 * SB))
svg.append('<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="#000"/>' % (ox + M, PH - M - 3 * SB, 3 * SB, 3 * SB))
svg.append(text(M, PH + 18, '(b) the (tan eta, tan alpha) plane.  Light grey: eta >= alpha (no NEST).  Hatch: EXCLUDED by (Sigma) [T] with offsets <= 2.62 / 1.21 --', ox))
svg.append(text(M, PH + 34, 'shallow nests cannot exist (tan alpha <= %.2f impossible at eta = 0).  Grey stipple: UNDECIDED [C] -- (WEDGE) and FLAT-C bite at steep alpha, not yet closed.' % chk['sigma_excluded']['max_tan_alpha_excluded_at_eta0'], ox))
svg.append(text(M, PH + 50, 'Fraction of the NEST half excluded by (Sigma) alone: %.0f%%.  Axes: x = tan eta (0..3), y = tan alpha (0..3).' % (100 * chk['sigma_excluded']['fraction_of_nest_half']), ox))
svg.append('</svg>')
open(os.path.join(OUTDIR, 'nest_residual.svg'), 'w', encoding='utf-8').write('\n'.join(svg))
print(json.dumps(chk, indent=1))
