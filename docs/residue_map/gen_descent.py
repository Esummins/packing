"""A194: docs/residue_map/descent.svg -- the corner-hurt region and one grain move, in the drawing rules of gen.py
(S px per unit, black container/quadrant, dashed corner cells, every drawn configuration containment- and
overlap-checked before drawing).  Three panels:

  (1) CORNER HURT at Trump's TL corner, corner frame (u, v) = distances from the two walls, the WIDENED box
      (0, 1+w)^2 in blue, the 2x2 cell grid at c_b dashed, the LONELY region of Theorem B for a first meeter of
      sq6's tilt (grey stipple = centres whose square admits NO second meeter; green = non-lonely), Trump's two
      meeters sq6/sq4 in cyan with their depths, the SEALED box (0, c_b - d1)^2 hatched (met by no square), and
      the conversion: the box translated by d2 along the diagonal (dashed) -- one meeter left, teleport.
  (2) DESCENT KILL on a real object: A163's trump5 witness 053 (9 squares of L u P at side 3.8739, dilated to s0):
      f1 is the ONLY TL meeter and is LONELY -- in a trump5 packing TL(0,0) must be doubly met (Theorem FC), so the
      witness dies (Theorem D2(b)).
  (3) ONE GRAIN MOVE: the pinwheel S02 at s* = 3.886746 with f0's exact slide (A160: length 0.298 at fixed tilt,
      rails BL(1,0)/f3, stops BR(0,1)/f1) and the common-tilt spine s*(theta) > s0 everywhere.
Read-only on every attempt; imports A169's geometry and Theorem B criterion."""
import json, math, os, sys
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A169-sideband-lemma', 'code'))
from geo169 import verts, sat_gap, in_quadrant, meets_open_box, S0, W0   # noqa: E402
from crit169 import criterion                                            # noqa: E402
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A194-descent', 'code'))
from hurt194 import to_frame, mu                                         # noqa: E402

S = 120
CB = 1 + W0
OUT = os.path.join(HERE, 'descent.svg')


def esc(t):
    return str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def text(x, y, t, size=11, col='#222', bold=False, anchor='start'):
    b = ' font-weight="bold"' if bold else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{col}" text-anchor="{anchor}"{b}>{esc(t)}</text>'


def poly(pts, X, Y, col, fill, op=0.55, w=1.6, dash=False):
    d = ' '.join(f'{X(p[0]):.1f},{Y(p[1]):.1f}' for p in pts)
    da = ' stroke-dasharray="5,3"' if dash else ''
    return f'<polygon points="{d}" fill="{fill}" fill-opacity="{op}" stroke="{col}" stroke-width="{w}"{da}/>'


def check_packing(polys, side):
    for p in polys:
        assert all(-1e-7 <= x <= side + 1e-7 and -1e-7 <= y <= side + 1e-7 for x, y in p), 'outside'
    for i in range(len(polys)):
        for j in range(i + 1, len(polys)):
            assert sat_gap(polys[i], polys[j]) >= -1e-6, f'overlap {i},{j}'


def trump():
    T = json.load(open(os.path.join(ROOT, 'certs', 'trump11_certificate.json')))
    sT = float(Fraction(T['container_side'])); lam = S0 / sT
    return [verts(float(Fraction(q['cx'])) * lam, float(Fraction(q['cy'])) * lam, 2 * math.atan(float(Fraction(q['t']))))
            for q in T['squares']]


def panel_hurt(ox, oy):
    """corner frame of Trump's TL corner, quadrant [0, 2.4]^2."""
    Q = 2.4
    X = lambda u: ox + u * S; Y = lambda v: oy - v * S
    TP = trump(); check_packing(TP, S0 + 1e-6)
    F = [to_frame(P, 'TL', S0) for P in TP]
    meet = [(i, F[i]) for i in range(11) if meets_open_box(F[i], CB)]
    dep = sorted([(CB - mu(P), i, P) for i, P in meet], reverse=True)
    d1, d2 = dep[0][0], dep[1][0]
    # tilt of the deep meeter in the frame
    (ax, ay), (bx, by) = dep[0][2][0], dep[0][2][1]; th = math.atan2(by - ay, bx - ax) % (math.pi / 2)
    out = [text(ox, oy - Q * S - 30, '(1) CORNER HURT — Trump\'s TL corner in its corner frame (Lemma CH)', 13, bold=True),
           text(ox, oy - Q * S - 16, f'grey stipple = LONELY centres at tilt {math.degrees(th):.1f}° (Theorem B: no second meeter of the widened box exists); green = non-lonely', 9.5, '#444'),
           text(ox, oy - Q * S - 4, f'cyan = Trump\'s meeters sq6 / sq4 at depths d1 = {d1:.3f}, d2 = {d2:.3f}; hatched = the sealed box (0, c_b - d1)^2, area {(CB - d1) ** 2:.3f}; dashed box = after the d2-conversion', 9.5, '#444')]
    # lonely raster
    pitch = 0.04; n = int(Q / pitch)
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * pitch, (j + 0.5) * pitch
            P = verts(cx, cy, th)
            if not in_quadrant(P) or not meets_open_box(P, CB):
                continue
            ok, _, _ = criterion(cx, cy, th, CB, steps=180)
            col = '#a5d6a7' if ok else '#9e9e9e'
            out.append(f'<rect x="{X(cx - pitch / 2):.1f}" y="{Y(cy + pitch / 2):.1f}" width="{pitch * S:.1f}" height="{pitch * S:.1f}" fill="{col}" fill-opacity="{0.8 if ok else 0.55}"/>')
    # quadrant, box, grid
    out.append(f'<rect x="{X(0)}" y="{Y(Q)}" width="{Q * S}" height="{Q * S}" fill="none" stroke="#000" stroke-width="2.5"/>')
    out.append(f'<rect x="{X(0)}" y="{Y(CB)}" width="{CB * S:.1f}" height="{CB * S:.1f}" fill="none" stroke="#1565c0" stroke-width="1.4"/>')
    out.append(f'<rect x="{X(0)}" y="{Y(1)}" width="{S}" height="{S}" fill="none" stroke="#666" stroke-width="1" stroke-dasharray="4,3"/>')
    for g in (CB,):
        out.append(f'<line x1="{X(g)}" y1="{Y(0)}" x2="{X(g)}" y2="{Y(Q)}" stroke="#d81b60" stroke-width="0.9" stroke-dasharray="5,3"/>')
        out.append(f'<line x1="{X(0)}" y1="{Y(g)}" x2="{X(Q)}" y2="{Y(g)}" stroke="#d81b60" stroke-width="0.9" stroke-dasharray="5,3"/>')
    # sealed box
    sb = CB - d1
    out.append(f'<rect x="{X(0)}" y="{Y(sb)}" width="{sb * S:.1f}" height="{sb * S:.1f}" fill="url(#hatch)" stroke="#e65100" stroke-width="1.2"/>')
    # meeters and the other squares in the frame (clipped view: draw all that intersect the quadrant window)
    for i, P in enumerate(F):
        if max(p[0] for p in P) < 0 or max(p[1] for p in P) < 0 or min(p[0] for p in P) > Q or min(p[1] for p in P) > Q:
            continue
        is_meet = any(i == k for k, _ in meet)
        out.append(poly(P, X, Y, '#000', '#00e5ff' if is_meet else '#eee', 0.45 if is_meet else 0.6, 1.8 if is_meet else 1.0))
        cx = sum(p[0] for p in P) / 4; cy = sum(p[1] for p in P) / 4
        if 0 < cx < Q and 0 < cy < Q:
            out.append(text(X(cx), Y(cy) + 4, f'sq{i}', 10, '#000', True, 'middle'))
    # conversion: box shifted by d2 along the diagonal
    out.append(f'<rect x="{X(d2)}" y="{Y(CB + d2)}" width="{CB * S:.1f}" height="{CB * S:.1f}" fill="none" stroke="#1565c0" stroke-width="1.2" stroke-dasharray="6,3"/>')
    out.append(f'<line x1="{X(0)}" y1="{Y(0)}" x2="{X(d2)}" y2="{Y(d2)}" stroke="#1565c0" stroke-width="2"/>')
    out.append(text(X(1.3), Y(2.2), 'cells at c_b = 1 + w (Lemma A2: one centre per cell)', 9, '#d81b60'))
    out.append(text(X(0.05), Y(sb + 0.05), 'sealed', 9, '#e65100'))
    return out


def panel_witness(ox, oy):
    W = json.load(open(os.path.join(ROOT, 'attempts', 'A163-s02-other-frames', 'results', 'witnesses163.json')))
    w = [x for x in W['witnesses'] if x['key'].startswith('053')][0]
    s = w['side']; lam = S0 / s; cfg = w['cfg']
    names = list(cfg); polys = [verts(cfg[n][0] * lam, cfg[n][1] * lam, math.radians(cfg[n][2])) for n in names]
    check_packing(polys, S0 + 1e-6)
    X = lambda x: ox + x * S; Y = lambda y: oy - y * S
    out = [text(ox, oy - S0 * S - 30, '(2) DESCENT KILL — A163 trump5 witness 053 (9 squares, side 3.8739 < s0, TL(0,0) dropped), dilated to s0', 13, bold=True),
           text(ox, oy - S0 * S - 16, 'f1 (red) is the ONLY square meeting the widened TL box and its pose is LONELY (Theorem B, margin -0.13):', 9.5, '#444'),
           text(ox, oy - S0 * S - 4, 'a trump5 packing must meet TL(0,0) twice (k6_23 dead on the window, Theorem FC) — Theorem D2(b) kills the witness by a clip, no tree', 9.5, '#444'),
           f'<rect x="{X(0)}" y="{Y(S0)}" width="{S0 * S:.1f}" height="{S0 * S:.1f}" fill="none" stroke="#000" stroke-width="2.5"/>']
    for cx, cy in [(0, 0), (S0 - 1, 0), (0, S0 - 1), (S0 - 1, S0 - 1)]:
        out.append(f'<rect x="{X(cx)}" y="{Y(cy + 1)}" width="{S}" height="{S}" fill="none" stroke="#666" stroke-width="1" stroke-dasharray="4,3"/>')
    out.append(f'<rect x="{X(0)}" y="{Y(S0)}" width="{CB * S:.1f}" height="{CB * S:.1f}" fill="none" stroke="#1565c0" stroke-width="1.4"/>')
    for n, P in zip(names, polys):
        pin = n[0] in 'BT' and '(' in n
        col = '#e53935' if n == 'f1' else ('#90caf9' if pin else '#ffe082')
        out.append(poly(P, X, Y, '#000', col, 0.6, 1.4))
        cx = sum(p[0] for p in P) / 4; cy = sum(p[1] for p in P) / 4
        out.append(text(X(cx), Y(cy) + 4, n, 9, '#000', n == 'f1', 'middle'))
    F = to_frame(polys[names.index('f1')], 'TL', S0)
    out.append(text(ox, oy + 14, f'f1 depth at the widened TL box: {CB - mu(F):.3f}; partner search 0 of 200,000 draws; the same holds on all nine A163 witnesses (descent_examples.md §7.2)', 9, '#333'))
    return out


def panel_grain(ox, oy):
    P = json.load(open(os.path.join(ROOT, 'attempts', 'A160-s02-f0-slide', 'results', 'polish160.json')))
    E = P['eleven']; s = E['s']; poses = E['poses']
    names = list(poses); polys = [verts(*poses[n][:2], math.radians(poses[n][2])) for n in names]
    check_packing(polys, s + 1e-6)
    SL = json.load(open(os.path.join(ROOT, 'attempts', 'A160-s02-f0-slide', 'results', 'slide_exact.json')))
    X = lambda x: ox + x * S; Y = lambda y: oy - y * S
    out = [text(ox, oy - s * S - 30, f'(3) ONE GRAIN MOVE — the pinwheel 4-grain (S02) at s* = {s:.6f}, common tilt {E["tilt_deg"]:.4f}°', 13, bold=True),
           text(ox, oy - s * S - 16, 'f0 is a strut: its exact freedom is a SLIDE of length 0.298 at fixed tilt (orange segment; rails BL(1,0)/f3, stops BR(0,1)/f1) — no slot at either end', 9.5, '#444'),
           text(ox, oy - s * S - 4, 'the load path f1 f2 f3 BL(0,1) BR(0,1) moves by the common tilt: s*(θ) = 3.997 / 3.911 / 3.887 / 3.902 / 3.974 at 3.4° / 28.4° / 48.4° / 68.4° / 88.4° — above s0 everywhere', 9.5, '#444'),
           f'<rect x="{X(0)}" y="{Y(s)}" width="{s * S:.1f}" height="{s * S:.1f}" fill="none" stroke="#000" stroke-width="2.5"/>',
           f'<rect x="{X(0)}" y="{Y(S0)}" width="{S0 * S:.1f}" height="{S0 * S:.1f}" fill="none" stroke="#1565c0" stroke-width="1" stroke-dasharray="6,3"/>']
    for cx, cy in [(0, 0), (s - 1, 0), (0, s - 1), (s - 1, s - 1)]:
        out.append(f'<rect x="{X(cx)}" y="{Y(cy + 1)}" width="{S}" height="{S}" fill="none" stroke="#666" stroke-width="1" stroke-dasharray="4,3"/>')
    load = {'f1', 'f2', 'f3', 'BL(0,1)', 'BR(0,1)'}
    for n, P in zip(names, polys):
        col = '#ffb300' if n in load else ('#90caf9' if '(' in n else '#eeeeee')
        out.append(poly(P, X, Y, '#000', col, 0.6, 1.4))
        cx = sum(p[0] for p in P) / 4; cy = sum(p[1] for p in P) / 4
        out.append(text(X(cx), Y(cy) + 4, n, 9, '#000', n in load, 'middle'))
    # f0's slide: try the recorded ends, else fall back to the direction/length in the file
    A = SL.get('end_lo', (2.180910, 1.507845)); B = SL.get('end_hi', (1.957631, 1.705836))
    out.append(f'<line x1="{X(A[0])}" y1="{Y(A[1])}" x2="{X(B[0])}" y2="{Y(B[1])}" stroke="#e65100" stroke-width="3"/>')
    for p, lab in ((A, 'end A: stop BR(0,1)'), (B, 'end B: stop f1')):
        out.append(f'<circle cx="{X(p[0])}" cy="{Y(p[1])}" r="4" fill="#e65100"/>')
        out.append(text(X(p[0]) + 6, Y(p[1]) - 6, lab, 8.5, '#e65100'))
    out.append(text(ox, oy + 14, 'amber = the load path (the grain); blue = the slots it leans on; dashed = s0. Kills are constant along moves inside a certified box (descent_grains.md §6.2); the move is the coordinate, not the mechanism.', 9, '#333'))
    return out


def main():
    PW = int(S0 * S) + 60
    body = ['<defs><pattern id="hatch" width="6" height="6" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">'
            '<line x1="0" y1="0" x2="0" y2="6" stroke="#e65100" stroke-width="1.4"/></pattern></defs>',
            text(20, 24, 'DESCENT (A194): the corner-hurt region, a descent kill on a real witness, and one grain move', 15, bold=True),
            text(20, 42, 'docs/proofs/descent.md — Lemma CH, Theorems D1–D3; descent_grains.md; descent_examples.md.  Every drawn configuration is containment- and overlap-checked.', 10, '#444')]
    top = 110 + int(S0 * S)
    body += panel_hurt(30, top)
    body += panel_witness(30 + PW, top)
    body += panel_grain(30 + 2 * PW, top)
    W = 3 * PW + 60; H = top + 40
    doc = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Segoe UI, sans-serif" style="background:#fff">'] + body + ['</svg>']
    open(OUT, 'w', encoding='utf-8').write('\n'.join(doc))
    import xml.dom.minidom; xml.dom.minidom.parse(OUT)
    print('wrote', OUT, 'xml ok')


if __name__ == '__main__':
    main()
