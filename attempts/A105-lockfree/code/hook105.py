r"""hook105.py -- A105: the hook geometry (docs/proofs/lockfree.md s.3-4).

A HOOK at a corner (BL frame): an axis-aligned square N = [0,1] x [1-eps, 2-eps] hugging the side wall and
nicking the corner box by eps > 0 from above, and a tilted square T (tilt theta, ccw, lowest vertex on the
floor at (v_x, 0)) carrying N's inner bottom corner (1, 1-eps) on T's upper-left edge.  Exact: with
s = sin theta, c = cos theta, the corner lies on the edge at parameter s_par = (1 - eps - c)/s in [0, 1] and
    v_x = g(theta, eps) := 1 + s - c (1 - eps - c)/s = 1 + tan(theta/2) + (c/s) eps  ( = h(theta) + (c/s) eps ).
T's right vertex is at (v_x + c, s).  Two hooks at the two corners of one wall with tilted squares T1, T2 on
the floor need  m >= g(theta1, eps1) + g(theta2, eps2) + D(theta1, theta2),  D = the least horizontal
distance between the lowest vertices of two floor squares (T1 ccw theta1, T2 cw theta2) with disjoint
interiors.  Checks here (pure geometry, seconds):
  (1) D(theta1, theta2) by SAT bisection against the breakpoint formula
      D = max(c1 + s1 c2/s2, c1 + c2 - (s2 - s1) s1/c1)  (s1 <= s2);
  (2) Phi(theta1, theta2) := tan(theta1/2) + tan(theta2/2) + D(theta1, theta2) >= 2 on a fine grid of
      [0, 45 deg]^2 (the inequality behind Theorem HOOK-4: four hooks with stacked wall uprights need m >= 4);
  (3) the equal-tilt four-hook shell at its exact minimal side m(theta) = 2(1+s)(1+c)/(s+c): built as poses,
      geometry-checked (containment, pairwise SAT), corner meet counts (the nicks are eps = (4-m)/2 <= 0: NOT
      K0-BLOCKED), drawn;
  (4) the two exact one-wall counterexamples to the one-wall lemma (record_s0115's bottom wall, the
      floor-1e-3 record's left wall), drawn with their hooks, from A87's exact poses (A103's loader).
Writes attempts/A105-lockfree/results/hook105.json and hookwall105.svg only.
"""
from __future__ import annotations
import os, sys, json, math
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"): os.environ[_v] = "1"
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import lockw105 as L
RES = L.RES

def sq_floor(vx, theta, ccw=True):
    """unit square with lowest vertex (vx, 0), tilt theta ccw (or cw): returns (cx, cy, th) pose."""
    c, s = math.cos(theta), math.sin(theta)
    if ccw: cx, cy, th = vx + (c - s) / 2.0, (c + s) / 2.0, theta
    else: cx, cy, th = vx - (c - s) / 2.0, (c + s) / 2.0, -theta
    return (cx, cy, th)

def D_num(t1, t2):
    """least horizontal distance between the lowest vertices of T1 (ccw t1) and T2 (cw t2), both on the floor."""
    P1 = L.verts(*sq_floor(0.0, t1, True))
    lo, hi = 0.0, 3.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        P2 = L.verts(*sq_floor(mid, t2, False))
        if L.sep(P1, P2) >= 0: hi = mid
        else: lo = mid
    return hi
def D_formula(t1, t2):
    if t1 > t2: t1, t2 = t2, t1
    s1, c1, s2, c2 = math.sin(t1), math.cos(t1), math.sin(t2), math.cos(t2)
    b1 = c1 + (s1 * c2 / s2 if s2 > 0 else c1 * 0.0 + 1.0 * (1.0 if s1 == 0 else 0.0))
    if s2 == 0: b1 = c1 + 1.0 if s1 == 0 else c1
    b2 = c1 + c2 - (s2 - s1) * s1 / c1
    return max(b1, b2)
def g(theta, eps):
    s, c = math.sin(theta), math.cos(theta)
    return 1 + s - c * (1 - eps - c) / s

def check_D_and_Phi(n=91):
    worst = 0.0; phimin = (9.0, None); rows = []
    ths = [math.radians(45.0 * k / (n - 1)) for k in range(n)]
    for i, t1 in enumerate(ths):
        for t2 in ths[i:]:
            if t1 == 0 and t2 == 0: dn = 2.0      # two uprights side by side
            else: dn = D_num(t1, t2)
            df = D_formula(max(t1, 1e-9), max(t2, 1e-9)) if (t1 > 0 or t2 > 0) else 2.0
            worst = max(worst, abs(dn - df))
            phi = math.tan(t1 / 2) + math.tan(t2 / 2) + dn
            if phi < phimin[0]: phimin = (phi, (math.degrees(t1), math.degrees(t2)))
    return worst, phimin

def shell(theta):
    """equal-tilt four-hook shell at its minimal side; returns (m, eps, poses, checks)."""
    s, c = math.sin(theta), math.cos(theta)
    m = 2 * (1 + s) * (1 + c) / (s + c); eps = (4 - m) / 2.0
    vx = g(theta, eps)
    T1 = sq_floor(vx, theta, True); T2 = sq_floor(m - vx, theta, False)
    def refl_y(p): return (p[0], m - p[1], -p[2])
    T4, T3 = refl_y(T1), refl_y(T2)
    N1 = (0.5, 1.5 - eps, 0.0); N2 = (0.5, 2.5 - eps, 0.0); N3 = (m - 0.5, 1.5 - eps, 0.0); N4 = (m - 0.5, 2.5 - eps, 0.0)
    poses = [T1, T2, T3, T4, N1, N2, N3, N4]
    P = [L.verts(*q) for q in poses]
    cont = min(L.wall_gap(p, m) for p in P)
    pair = min(L.sep(P[i], P[j]) for i in range(8) for j in range(i + 1, 8))
    meets = {cn: [(i, round(L.corner_depth(q, cn, m), 9)) for i, q in enumerate(poses) if L.corner_depth(q, cn, m) > 1e-9] for cn in L.CORNERS}
    return m, eps, poses, {'containment_min': cont, 'pair_sep_min': pair, 'meets': meets, 'vx': vx, 'R1x': vx + c}

# ---------------------------------------------------------------- drawing
S = 120
def esc(t): return str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def text(x, y, t, size=10.5, col='#222', bold=False, anchor='start'):
    return '<text x="%.1f" y="%.1f" font-size="%s" fill="%s" text-anchor="%s"%s>%s</text>' % (x, y, size, col, anchor, ' font-weight="bold"' if bold else '', esc(t))
def panel(ox, oy, title, s, poses, hi_red, hi_blue, notes, contacts=None):
    out = [text(ox, oy - s * S - 26, title, 12, bold=True)]
    out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#000" stroke-width="2"/>' % (ox, oy - s * S, s * S, s * S))
    for (x0, y0) in ((0, 0), (s - 1, 0), (s - 1, s - 1), (0, s - 1)):
        out.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" fill="none" stroke="#999" stroke-width="1" stroke-dasharray="4,3"/>' % (ox + x0 * S, oy - (y0 + 1) * S, S, S))
    for i, q in enumerate(poses):
        p = L.verts(*q)
        col, fill = ('#c62828', '#ef9a9a') if i in hi_red else ('#1565c0', '#90caf9') if i in hi_blue else ('#555', '#e0e0e0')
        out.append('<polygon points="%s" fill="%s" fill-opacity="0.6" stroke="%s" stroke-width="1.5"/>' % (' '.join('%.1f,%.1f' % (ox + x * S, oy - y * S) for x, y in p), fill, col))
        t = math.degrees(q[2]) % 90; t = min(t, 90 - t)
        out.append(text(ox + q[0] * S, oy - q[1] * S + 4, str(i), 10.5, '#000', True, 'middle'))
        out.append(text(ox + q[0] * S, oy - q[1] * S + 14, '%.2f°' % t, 7.5, '#333', False, 'middle'))
    for (x, y) in (contacts or []):
        out.append('<circle cx="%.1f" cy="%.1f" r="3.5" fill="none" stroke="#b71c1c" stroke-width="1.4"/>' % (ox + x * S, oy - y * S))
    y = oy + 16
    for ln in notes:
        out.append(text(ox, y, ln, 9, '#333')); y += 12
    return out, y

def main():
    out = {}
    worst, phimin = check_D_and_Phi(91)
    out['D_formula_vs_SAT_max_abs_err'] = worst; out['Phi_min_on_grid'] = {'value': phimin[0], 'at_deg': phimin[1]}
    L.log('D formula vs SAT bisection: max |err| = %.2e over 91x91 grid; min Phi = %.6f at %s deg' % (worst, phimin[0], phimin[1]))
    # the shell at three tilts
    shells = {}
    for deg in (18.93, 5.0, 40.0, 45.0):
        m, eps, poses, ch = shell(math.radians(deg))
        shells['%.2f' % deg] = {'m': m, 'eps': eps, 'poses': poses, 'checks': ch}
        L.log('shell theta=%.2f: m=%.6f eps=%.6f containment %.2e pair %.2e meets %s' % (deg, m, eps, ch['containment_min'], ch['pair_sep_min'], {k: len(v) for k, v in ch['meets'].items()}))
    out['shells'] = shells
    # the corpus records
    C = {c['name']: c for c in L.load_corpus()}
    rec = C['record_s0115']; flo = C['floor_1e-03_d1em03_s0050']
    # the (beta, alpha) flush hook pair of the record's bottom wall against the exact formulas of s.3:
    #   beta carrier (steep edge carries the corner): v_x = 1 + (1-s)/c + (s/c) eps, depth (s/c)(1 - s - eps)
    #   alpha carrier (shallow edge):                 v_x = 1 + tan(t/2) + (c/s) eps
    #   flush pair: horizontal offset of the lowest vertices = 1/c;  m = v_beta + 1/c + v_alpha.
    s_, P_ = rec['side'], rec['poses']
    th = math.radians(90.0 - (math.degrees(P_[1][2]) % 90.0)); s, c = math.sin(th), math.cos(th)
    eps_BL = L.corner_depth(P_[0], 'BL', s_); eps_BR = L.corner_depth(P_[3], 'BR', s_)
    v_beta = 1 + (1 - s) / c + (s / c) * eps_BL; v_alpha = 1 + math.tan(th / 2) + (c / s) * eps_BR
    m_pred = v_beta + 1 / c + v_alpha
    v1 = min(L.verts(*P_[1]), key=lambda p: p[1]); v2 = min(L.verts(*P_[2]), key=lambda p: p[1])
    out['record_bottom_wall'] = {'theta_deg': math.degrees(th), 'eps_BL': eps_BL, 'eps_BR': eps_BR,
                                 'v_beta_formula': v_beta, 'v_beta_actual': v1[0], 'v_alpha_formula_from_right': v_alpha, 'v_alpha_actual_from_right': s_ - v2[0],
                                 'depth_beta_formula': (s / c) * (1 - s - eps_BL), 'depth_beta_actual': L.corner_depth(P_[1], 'BL', s_),
                                 'm_formula': m_pred, 'm_actual': s_, 'f_theta': (2 - s) / c + math.tan(th / 2)}
    L.log('record bottom wall (beta,alpha) hooks: theta %.4f deg, eps %.5f/%.5f; v_beta %.5f (actual %.5f), v_alpha %.5f (actual %.5f), depth_beta %.5f (actual %.5f); m formula %.6f vs %.6f' % (
        math.degrees(th), eps_BL, eps_BR, v_beta, v1[0], v_alpha, s_ - v2[0], (s / c) * (1 - s - eps_BL), L.corner_depth(P_[1], 'BL', s_), m_pred, s_))
    fmin = min((((2 - math.sin(x)) / math.cos(x) + math.tan(x / 2)), math.degrees(x)) for x in [math.radians(0.05 * k) for k in range(1, 901)])
    out['f_beta_alpha_min'] = {'value': fmin[0], 'at_deg': fmin[1]}; L.log('min over theta of (2-s)/c + tan(theta/2) = %.6f at %.2f deg (a flush (beta,alpha) pair fits below 4 iff this + eps terms < 2)' % fmin)
    body = []; ymax = 0
    # panel 1: record bottom wall
    s, P = rec['side'], rec['poses']
    cont = [tuple(c['point']) for i in (0, 1, 2, 3) for c in L.contacts_of(P, i, s)]
    notes = ['bottom wall (BL, BR both blocked): all four intruders HELD (Lemma ROT) -- the one-wall lemma is FALSE here.',
             'hooks: sq0 = [0,1]x[0.9853,1.9853] nicks BL by 0.0147 from above, carried by sq1 (tilt 18.93 deg, floats 2.7e-5) at (1, 0.9853);',
             '       sq3 = [2.9855,3.9855]x[0.9855,1.9855] nicks BR by 0.0145, carried by sq2 (on the floor) at (2.9855, 0.9855).',
             'sq1 and sq2 are flush edge-to-edge (same tilt sense): sq1 is WEDGED (self-stress, lambda = 0) and fails (W): it slides',
             'along sq2 at zero row rate and leaves BL -- LOCKED fails at sq1; sq0, sq2, sq3 are PUSHED (cone certificates in lockw105).',
             'TL sq4 (nick 7e-9) unheld by translation (A103); TR sq7 wedged between sq6 and the top wall, unpressed from the left (fails W).']
    o1, y1 = panel(30, 60 + 4.1 * S, 'record_s0115: side 3.9854837, K0-BLOCKED', s, P, {0, 3}, {1, 2}, notes, cont); body += o1; ymax = max(ymax, y1)
    # panel 2: floor-1e-3 left wall
    s2, P2 = flo['side'], flo['poses']
    cont2 = [tuple(c['point']) for i in (0, 1, 4, 5) for c in L.contacts_of(P2, i, s2)]
    notes2 = ['left wall (BL, TL both blocked): all four intruders HELD and W-held: LOCKED -- the one-wall lemma is FALSE here too.',
              'sq0 / sq4: two 16.41-deg squares stacked flush on the left wall (an edge-to-edge tilted column); sq1 (upright at',
              'offset 0.923 on the floor, X-type) pressed by sq9 low on its right edge; sq5 (upright on the top wall at offset 0.990)',
              'pressed by sq6.  Unlocked: BR sq3 (rotation, 1.31 deg) and TR sq6 (screw) -- the right wall, as lockmap103 says.']
    o2, y2 = panel(30 + 4.1 * S + 70, 60 + 4.1 * S, 'floor-1e-3 record: side 3.9907485, K0-BLOCKED(1e-3)', s2, P2, {1, 5}, {0, 4}, notes2, cont2); body += o2; ymax = max(ymax, y2)
    # panel 3: the shell
    m, eps, poses, ch = shell(math.radians(18.93))
    notes3 = ['the equal-tilt FOUR-HOOK SHELL (the grid tilted by 18.93 deg): four wall uprights stacked in pairs on the side walls,',
              'four floor/ceiling squares carrying their inner corners, neighbours touching vertex-to-vertex along each wall.',
              'Its side is EXACTLY m = 2(1+sin t)(1+cos t)/(sin t + cos t) = %.6f >= 4 (Theorem HOOK-4), so the nicks are' % m,
              'eps = (4 - m)/2 = %.4f < 0: every corner box is met by ONE square -- the shell is never K0-BLOCKED; at t -> 0 it is the 4x4 grid.' % eps,
              'checks: containment %.1e, min pairwise SAT %.1e; corner meeters BL:%d BR:%d TR:%d TL:%d.' % (ch['containment_min'], ch['pair_sep_min'], *[len(ch['meets'][k]) for k in L.CORNERS])]
    o3, y3 = panel(30 + 2 * (4.1 * S + 70), 60 + 4.1 * S, 'four-hook shell, tilt 18.93 deg, minimal side %.4f' % m, m, poses, set(), {4, 5, 6, 7}, notes3); body += o3; ymax = max(ymax, y3)
    body.append(text(30, ymax + 14, 'red = the hook uprights (wall-hugging axis-aligned nicks), blue = the tilted carriers / the shell uprights; circles = contacts at gap < 1e-7 on the highlighted squares (A102 conventions).', 9.5, '#444'))
    body.append(text(30, ymax + 27, 'A105 (2026-09-06): a wall of length < 4 CAN carry two blocked corners with every intruder held (two exact instances); what it cannot carry is four hooks with stacked uprights (HOOK-4: m >= 4, equality = the grid).', 9.5, '#444'))
    W = int(3 * (4.1 * S + 70) + 60); H = int(ymax + 42)
    doc = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Segoe UI, sans-serif" style="background:#fff">' % (W, H)] + body + ['</svg>']
    outp = os.path.join(RES, 'hookwall105.svg'); open(outp, 'w', encoding='utf-8').write('\n'.join(doc))
    import xml.dom.minidom; xml.dom.minidom.parse(outp)
    json.dump(out, open(os.path.join(RES, 'hook105.json'), 'w'), indent=1)
    L.log('wrote', outp, W, H)

if __name__ == '__main__':
    main()
