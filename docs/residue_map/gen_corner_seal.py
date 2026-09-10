"""docs/residue_map/corner_seal.svg -- the PI's corner seal on k5_16_interior_Y0491's BR corner (A199), in the drawing
rules of gen_a57_lp.py: hypothesis squares only at ADMISSIBLE poses (checked: inside the container, clear of every pin
core and of H's box at every pose sampled), one note per panel saying what it IS, times printed.
Left: the page's BR corner at s0 with F at a pose of the certified reach region, the leaning edge L_F, the sealed chord,
the sliver, the wedge, and a would-be H dipping into the sliver (its left edge enters F: Lemma WEDGE case A).
Right: the reach region and the SEAL statistics from results/seal199.jsonl.  Reads the jsonl; no geometry engine."""
import json, math, os, sys
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
S0 = 969271 / 250000
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'k5_16_interior_Y0491'
rows = [json.loads(l) for l in open(os.path.join(R, 'attempts', 'A199-corner-seal', 'results', 'seal199.jsonl'), encoding='utf-8') if l.strip()]
row = [d for d in rows if d.get('page') == PAGE and abs(d.get('lam', 1) - 1) < 1e-12][-1]
run = [r for r in row['runs'] if r['verdict'] == 'DEAD'][0] if row['verdict'] == 'DEAD' else row['runs'][0]
leaf = run['leaf_result']
reach = dict(n_pieces=leaf['n_sealed'] + leaf['n_residue'], vol_frac=leaf['vol_sealed'] + leaf['vol_residue'], n_tests=leaf['n_tests'],
             hull=leaf['sealed_hull'] or leaf['residue_hull'], H_misses_B='n/a', seconds=leaf['seconds'])
rec = json.load(open(os.path.join(R, row['record']), encoding='utf-8'))
pins = [(0.5 * (b['x0'] + b['x1']), 0.5 * (b['y0'] + b['y1'])) for b in rec['hyp']['boxes'] if abs(b['th1'] - b['th0']) < 1e-9]
hbox = [b for b in rec['hyp']['boxes'] if abs(b['th1'] - b['th0']) > 1e-9][0]

def sq(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s_), cy + 0.5 * (dx * s_ + dy * c)) for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]
def sat(p, q):
    best = -9
    for poly_ in (p, q):
        for i in range(4):
            a, b = poly_[i], poly_[(i + 1) % 4]; ex, ey = b[0] - a[0], b[1] - a[1]; n = math.hypot(ex, ey); ax = (-ey / n, ex / n)
            pp = [x * ax[0] + y * ax[1] for x, y in p]; qq = [x * ax[0] + y * ax[1] for x, y in q]
            best = max(best, min(qq) - max(pp), min(pp) - max(qq))
    return best
def admissible(P):
    if not all(0 <= x <= S0 and 0 <= y <= S0 for x, y in P): return False
    if any(sat(P, sq(px, py, 0.0)) < -1e-9 for px, py in pins): return False
    for i in range(5):
        for j in range(5):
            for k in range(5):
                hx = hbox['x0'] + (hbox['x1'] - hbox['x0']) * i / 4; hy = hbox['y0'] + (hbox['y1'] - hbox['y0']) * j / 4
                ht = math.radians(hbox['th0'] + (hbox['th1'] - hbox['th0']) * k / 4)
                if sat(P, sq(hx, hy, ht)) < -1e-9: return False
    return True
# an admissible F pose from the certified reach hull (the hull's centre, mid tilt; search nearby if the centre is infeasible)
hx0, hx1, hy0, hy1, ht0, ht1 = reach['hull']
F = None
for i in range(9):
    for j in range(9):
        for k in range(5):
            cx = hx0 + (hx1 - hx0) * i / 8; cy = hy0 + (hy1 - hy0) * j / 8; th = math.radians(ht0 + (ht1 - ht0) * k / 4)
            P = sq(cx, cy, th)
            if admissible(P) and (F is None or abs(cx - 0.5 * (hx0 + hx1)) + abs(cy - 0.5 * (hy0 + hy1)) < F[3]):
                F = (cx, cy, th, abs(cx - 0.5 * (hx0 + hx1)) + abs(cy - 0.5 * (hy0 + hy1)))
cx, cy, th, _ = F; PF = sq(cx, cy, th)
q = max(PF, key=lambda p: p[0]); b = min(PF, key=lambda p: p[1]); phi = math.atan2(q[0] - b[0], q[1] - b[1])
c = (S0 - 1.0, 1.0)                                  # the pin's free corner
xr = q[0] - (q[1] - c[1]) * math.tan(phi)            # where L_F crosses y = 1
xl = xr - 1 / math.cos(phi)
# a would-be H: a unit square whose lowest vertex dips into the sliver (x_r, s0-1) x {1} -- drawn to show WHY it fails
psi = math.radians(70.0); d = 0.06; vx = xr + 0.55 * (c[0] - xr); v = (vx, c[1] - d)
Hw = [v, (v[0] + math.sin(psi), v[1] + math.cos(psi)), (v[0] + math.sin(psi) - math.cos(psi), v[1] + math.cos(psi) + math.sin(psi)), (v[0] - math.cos(psi), v[1] + math.sin(psi))]
gap_ok = sat(Hw, PF) >= -1e-9
# ---- drawing
SC = 300; OX, OY = 40, 40; x_lo, y_hi = S0 - 2.3, 2.3
X = lambda x: OX + (x - x_lo) * SC; Y = lambda y: OY + (y_hi - y) * SC
pts = lambda P: ' '.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in P)
def esc(t): return str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def text(x, y, t, size=10, col='#222', bold=False, anchor='start'):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{col}" text-anchor="{anchor}"{" font-weight=\"bold\"" if bold else ""}>{esc(t)}</text>'
out = ['<svg xmlns="http://www.w3.org/2000/svg" width="1240" height="800" font-family="Segoe UI, sans-serif" style="background:#fff">',
       text(OX, 22, f'{PAGE}: the corner seal at BR (A199; docs/proofs/corner_seal.md).  F = a free meeter of BR(0,1) at a pose of the CERTIFIED reach region (exact); it reaches around the pin\'s corner, is rotated (phi = {math.degrees(phi):.1f} deg), seals BR(1,0)\'s top edge; verdict {row["verdict"]} in {row.get("seconds", 0):.0f} s (SEAL leaf)', 11, bold=True),
       text(OX, 36, 'blue = pins (k5_16, exact at s0); black rect = H\'s box; green = F (admissible: inside, clear of every pin and of H at 125 sampled poses); dashed = the unit slot boxes BR(0,1), BR(1,0) (pad 0); orange = F\'s chord on y = 1 (the seal); hatched = the wedge between L_F and the pin\'s side; red dashed = a would-be H dipping into the sliver -- its left edge enters F (Lemma WEDGE, case A)', 8.5, '#444')]
# clip region: the corner
out.append(f'<rect x="{X(x_lo)}" y="{Y(y_hi)}" width="{(S0 - x_lo) * SC:.1f}" height="{(y_hi + 0.0) * SC:.1f}" fill="none" stroke="#000" stroke-width="2"/>')
for (px, py) in pins:
    if px > x_lo and py < y_hi: out.append(f'<polygon points="{pts(sq(px, py, 0))}" fill="#90caf9" fill-opacity="0.6" stroke="#1565c0" stroke-width="1.5"/>')
for (x0, x1, y0, y1, nm) in ((S0 - 1, S0, 1, 2, 'BR(0,1)'), (S0 - 2, S0 - 1, 0, 1, 'BR(1,0)')):
    out.append(f'<rect x="{X(x0)}" y="{Y(y1)}" width="{(x1 - x0) * SC}" height="{(y1 - y0) * SC}" fill="none" stroke="#000" stroke-width="1" stroke-dasharray="5,3"/>' + text(X(x0) + 4, Y(y1) + 12, nm, 9))
out.append(f'<rect x="{X(hbox["x0"])}" y="{Y(hbox["y1"])}" width="{(hbox["x1"] - hbox["x0"]) * SC:.1f}" height="{(hbox["y1"] - hbox["y0"]) * SC:.1f}" fill="none" stroke="#000" stroke-width="2"/>' + text(X(hbox['x0']), Y(hbox['y1']) - 3, f'H box (tilt {hbox["th0"]:.1f}-{hbox["th1"]:.1f} deg)', 8))
# the wedge (between L_F and the pin's side, below y = 1) hatched
wy = b[1]; wx = xr + (wy - c[1]) * math.tan(phi)
out.append('<defs><pattern id="hat" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="#e65100" stroke-width="1"/></pattern></defs>')
out.append(f'<polygon points="{pts([(xr, c[1]), (c[0], c[1]), (c[0], wy), (wx, wy)])}" fill="url(#hat)" stroke="none"/>')
out.append(f'<polygon points="{pts(PF)}" fill="#2e7d32" fill-opacity="0.25" stroke="#2e7d32" stroke-width="2"/>' + text(X(cx) - 4, Y(cy) + 4, 'F', 12, '#2e7d32', True))
# L_F extended, chord, sliver
out.append(f'<line x1="{X(xr + (0.0 - c[1]) * math.tan(phi))}" y1="{Y(0.0)}" x2="{X(xr + (q[1] + 0.3 - c[1]) * math.tan(phi))}" y2="{Y(q[1] + 0.3)}" stroke="#2e7d32" stroke-width="0.8" stroke-dasharray="3,3"/>' + text(X(q[0]) + 6, Y(q[1]) - 4, f'q = ({q[0]:.3f}, {q[1]:.3f}); L_F', 8, '#2e7d32'))
out.append(f'<line x1="{X(max(xl, S0 - 2))}" y1="{Y(1.0)}" x2="{X(xr)}" y2="{Y(1.0)}" stroke="#e65100" stroke-width="4"/>' + text(X(S0 - 1.9), Y(1.0) - 6, f'F\'s chord on y = 1: [{xl:.3f}, {xr:.3f}] (length 1/cos phi = {1 / math.cos(phi):.3f}); sliver ({xr:.3f}, {S0 - 1:.3f}) of width {S0 - 1 - xr:.3f} < sin phi = {math.sin(phi):.3f}', 8, '#e65100'))
out.append(f'<polygon points="{pts(Hw)}" fill="none" stroke="#c62828" stroke-width="1.6" stroke-dasharray="6,3"/>' + text(X(Hw[2][0]), Y(Hw[2][1]) - 4, f'would-be H vertex in the sliver (depth {d}, psi 70 deg): {"overlaps F by " + format(-sat(Hw, PF), ".3f") if not gap_ok else "clear of F (?)"}', 8, '#c62828'))
out.append(text(X(c[0]) + 3, Y(c[1]) + 10, 'pin corner c', 8))
# right panel: the statistics
tx, ty = 760, 70
lines = ['Certified region of BR(0,1)'s free meeters (exact bisection of the meeter window against the pins' K', H's K', the container; A161 miss test on BR(0,1)):',
         f'  {leaf["n_sealed"]} SEALED pieces (vol {leaf["vol_sealed"]:.5f} of the window), {leaf["n_residue"]} residue, {leaf["dropped"]} dropped, {leaf["n_tests"]} exact tests, {leaf["seconds"]} s',
         f'  sealed hull: x [{hx0:.3f}, {hx1:.3f}]  y [{hy0:.3f}, {hy1:.3f}]  tilt [{ht0:.1f}, {ht1:.1f}] deg  (phi = 90 - tilt in [{90 - ht1:.1f}, {90 - ht0:.1f}] deg)',
         'Lemma NO-SECOND per sealed piece (exact rationals in t = tan(theta/2), worst ends): deep regime q_y < cos phi - sin phi,',
         '  l_x < -1, y_bl < 0, and min over psi' of cos psi' + c tan psi' > 1 + l_y  (c = -1 - l_x, h = 1 + y_bl):',
         f'  smallest margin over the sealed pieces {leaf["sealed_margin_min"]:.2e} > 0',
         (f'The near-upright sliver (residue at the depth cap): a second meeter would have its rightmost vertex within h/2 = {leaf["gbox"]["h"]/2:.3f} of BR(1,0)'s left side,'
          f' so its centre in the box x [{leaf["gbox"]["box"][0]:.2f}, {leaf["gbox"]["box"][1]:.2f}] y [{leaf["gbox"]["box"][2]:.2f}, {leaf["gbox"]["box"][3]:.2f}]: exact reach test EMPTY ({leaf["gbox"]["n_tests"]} tests)' if leaf.get('gbox') else 'no residue'),
         f'Verdict: {row["verdict"]} -- {run.get("leaf")}',
         f'Total {row.get("seconds", 0):.0f} s at s0 (pad 0; lam = 1); certificate = attempts/A199-corner-seal/results/seal199.jsonl (every test listed).',
         'Reading (corner_seal.md): SEAL gives the rotation and the seal (chord 1/cos phi > 1 covers the top edge of BR(1,0) except the sliver);',
         'WEDGE: no second meeter of BR(1,0) on the wedge side of L_F; NO-SECOND: none under F or across the left side either -- BR(1,0)'s only',
         'non-pin meeter is F, against Theorem FC.  H is not needed except as the obstacle that confines F's region.',
         'What the pair test could not see: the exact multibox chain {pins, H, F-sub-box, G} leaves G ALIVE in every sub-box (F's K' is far smaller than any actual F).']
for k, l in enumerate(lines):
    out.append(text(tx, ty + 14 * k, l, 8.5 if not l.startswith('  ') else 8, '#222' if not l.startswith('  ') else '#333', not l.startswith('  ') and not l.startswith('Reading') and not l.startswith('BR')))
out.append('</svg>')
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'corner_seal.svg')
open(p, 'w', encoding='utf-8').write('\n'.join(out)); print('wrote', p, 'F pose', (round(cx, 3), round(cy, 3), round(math.degrees(th), 1)), 'phi', round(math.degrees(phi), 2), 'H-vertex overlap', round(-sat(Hw, PF), 4))
import xml.dom.minidom; xml.dom.minidom.parse(p); print('xml ok')
