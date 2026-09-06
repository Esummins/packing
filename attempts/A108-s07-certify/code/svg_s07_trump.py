"""A108 T3 - Trump and S07 side by side, in the conventions of docs/residue_map/gen_pinwheel_k7_svg.py.

Same scale, same corner-cell guides, same colour code (tilted squares red, upright slot squares
blue), same green contact circles, same "every square containment- and overlap-checked before it is
drawn" rule.  The only additions are (i) the two panels share one scale so the 0.0085 side
difference is visible as a real offset, (ii) the squares Trump and S07 disagree on are outlined in
amber, and (iii) the barrier plot between them is drawn underneath.

Writes docs/residue_map/s07_vs_trump.svg.
"""
from __future__ import annotations

import json
import math
import os

import a108lib as A
from a108lib import L
import exact as EX

ROOT = A.ROOT
OUT = os.path.join(ROOT, 'docs', 'residue_map', 's07_vs_trump.svg')
S = 150.0                       # px per unit, as in gen_pinwheel_k7_svg.py (160) - 150 fits two panels
SHAT = A.SHAT


# ------------------------------------------------------------------ geometry + checks
def sq(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s_), cy + 0.5 * (dx * s_ + dy * c))
            for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def sep(p, q):
    axes = []
    for poly in (p, q):
        for i in range(4):
            a, b = poly[i], poly[(i + 1) % 4]
            ex, ey = b[0] - a[0], b[1] - a[1]
            n = math.hypot(ex, ey)
            axes.append((-ey / n, ex / n))
    best = -9.0
    for ax in axes:
        pp = [x * ax[0] + y * ax[1] for x, y in p]
        qq = [x * ax[0] + y * ax[1] for x, y in q]
        best = max(best, min(qq) - max(pp), min(pp) - max(qq))
    return best


def check(s, cfg, tol=1e-9):
    polys = [sq(*c) for c in cfg]
    for P in polys:
        for x, y in P:
            assert -tol <= x <= s + tol and -tol <= y <= s + tol, ('containment', x, y, s)
    m = min(sep(polys[i], polys[j]) for i in range(len(polys)) for j in range(i + 1, len(polys)))
    assert m >= -tol, ('overlap', m)
    return polys, m


def contact_points(polys, tol=1e-7):
    pts, pairs = [], []
    n = len(polys)
    for i in range(n):
        for j in range(i + 1, n):
            if sep(polys[i], polys[j]) < tol:
                pairs.append((i, j))
                best = (9.0, None)
                for AA, BB in ((polys[i], polys[j]), (polys[j], polys[i])):
                    for v in AA:
                        for k in range(4):
                            a, b = BB[k], BB[(k + 1) % 4]
                            ex, ey = b[0] - a[0], b[1] - a[1]
                            Lq = ex * ex + ey * ey
                            t = max(0.0, min(1.0, ((v[0] - a[0]) * ex + (v[1] - a[1]) * ey) / Lq))
                            f = (a[0] + t * ex, a[1] + t * ey)
                            dd = math.hypot(v[0] - f[0], v[1] - f[1])
                            if dd < best[0]:
                                best = (dd, f)
                pts.append(best[1])
    return pts, pairs


# ------------------------------------------------------------------ svg helpers
def esc(t):
    return str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def text(x, y, t, size=11, col='#222', bold=False, anchor='start', mono=False):
    b = ' font-weight="bold"' if bold else ''
    fam = ' font-family="Consolas, monospace"' if mono else ''
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{col}" '
            f'text-anchor="{anchor}"{b}{fam}>{esc(t)}</text>')


def panel(ox, oy_base, s, cfg, names, title, sub, moved, smax, rattlers=()):
    """One packing.  oy_base is the y pixel of the container's BOTTOM edge; both panels share it,
    so the taller container sticks up by exactly the side difference."""
    body = []
    polys, m = check(s, cfg)
    oy = oy_base
    body.append(text(ox, oy - smax * S - 40, title, 13.5, '#111', True))
    body.append(text(ox, oy - smax * S - 23, sub, 10, '#444'))
    # corner guide cells
    for (x0, y0) in ((0, 0), (s - 1, 0), (0, s - 1), (s - 1, s - 1)):
        body.append(f'<rect x="{ox + x0 * S:.1f}" y="{oy - (y0 + 1) * S:.1f}" width="{S:.1f}" '
                    f'height="{S:.1f}" fill="none" stroke="#ccc" stroke-width="1" '
                    f'stroke-dasharray="4,3"/>')
    body.append(f'<rect x="{ox:.1f}" y="{oy - s * S:.1f}" width="{s * S:.1f}" '
                f'height="{s * S:.1f}" fill="none" stroke="#000" stroke-width="2.2"/>')
    for i, P in enumerate(polys):
        a = math.degrees(cfg[i][2]) % 90.0
        tilted = min(a, 90.0 - a) > 1.0
        col, fill = ('#c62828', '#ef9a9a') if tilted else ('#1565c0', '#90caf9')
        pts = ' '.join(f'{ox + x * S:.1f},{oy - y * S:.1f}' for x, y in P)
        body.append(f'<polygon points="{pts}" fill="{fill}" fill-opacity="0.55" stroke="{col}" '
                    f'stroke-width="1.6"/>')
        if names[i] in moved:
            body.append(f'<polygon points="{pts}" fill="none" stroke="#ef6c00" '
                        f'stroke-width="2.6" stroke-dasharray="6,3"/>')
        cx, cy, th = cfg[i]
        body.append(text(ox + cx * S, oy - cy * S + 3, names[i], 9.5, '#000', True, 'middle'))
        if tilted:
            body.append(text(ox + cx * S, oy - cy * S + 14,
                             f'{math.degrees(th) % 90:.4f}°', 8, '#333', False, 'middle'))
        if names[i] in rattlers:
            body.append(text(ox + cx * S, oy - cy * S + 25, 'RATTLER', 7.5, '#6a1b9a', True,
                             'middle'))
    pts, pairs = contact_points(polys)
    for f in pts:
        body.append(f'<circle cx="{ox + f[0] * S:.1f}" cy="{oy - f[1] * S:.1f}" r="4.2" '
                    f'fill="none" stroke="#2e7d32" stroke-width="1.8"/>')
    walls = []
    for i, (cx, cy, th) in enumerate(cfg):
        g = L.wall_gaps(cx, cy, th, s)
        for nm, v in g.items():
            if v < 1e-7:
                walls.append(f'{names[i]}-{nm}')
    contacts = [f'{names[i]}-{names[j]}' for i, j in pairs]
    return body, m, contacts, walls


def main():
    s7, cfg7 = EX.exact_float()
    st, cfgt, _ = A.load_trump()
    names = list(A.NAMES)
    moved = {'BL(0,2)'}          # amber dashes: the square whose ROLE differs (the tilt
                                 # difference is written on every red square instead)

    smax = max(s7, st)
    W = int(2 * smax * S + 3 * 46 + 40)
    top = 78
    oy_base = top + smax * S
    body = []
    b1, m1, c1, w1 = panel(46, oy_base, st, cfgt, names,
                           f'TRUMP  (class trump5)   s-hat = {st:.12f}',
                           'the optimum: five squares at 40.1819°, BL(0,2) lifted 0.03256 off its slot '
                           '(the TL two-crowd); f3 is wedged on the right wall between f2 and f4',
                           moved, smax)
    b2, m2, c2, w2 = panel(46 + smax * S + 46, oy_base, s7, cfg7, names,
                           f'S07  (class k6_07)   s* = 2 + 4√2/3 = {s7:.12f}',
                           'BL(0,2) snapped INTO its slot, all five tilted squares at exactly 45°, '
                           'f3 drops out of the load path; s* - s-hat = +0.0085345',
                           moved, smax, rattlers={'f3'})
    body += b1 + b2

    y = oy_base + 24
    for label, val in (('worst pairwise SAT separation', f'Trump {m1:+.2e}   S07 {m2:+.2e}'),):
        body.append(text(46, y, f'{label}: {val}   (every square containment-checked against '
                                f'[0,s]^2 before drawing; no overlaps in either panel)', 9.5, '#444'))
        y += 15
    for tag, lst in (('Trump contacts', c1 + w1), ('S07 contacts', c2 + w2)):
        for r in range(0, len(lst), 13):
            body.append(text(46, y, (f'{tag}: ' if r == 0 else ' ' * (len(tag) + 2)) +
                             ', '.join(lst[r:r + 13]), 9, '#444', mono=(r > 0)))
            y += 13
        y += 4
    only1 = [c for c in c1 + w1 if c not in c2 + w2]
    only2 = [c for c in c2 + w2 if c not in c1 + w1]
    body.append(text(46, y, 'only in Trump: ' + ', '.join(only1) +
                     '        only in S07: ' + ', '.join(only2), 9.5, '#b71c1c'))
    y += 20

    # ---- the barrier plot
    doc = json.load(open(os.path.join(A.RES, 'trump_compare.json'), encoding='utf-8'))
    seg = doc['segment_normalised']
    fine = doc.get('relaxed_tilt_path_fine') or doc['relaxed_tilt_path']
    body.append(text(46, y, 'Are they one basin?  No - the side rises strictly between them.', 12,
                     '#111', True))
    y += 8
    PW, PH = 470.0, 150.0
    for k, (ttl, xs, ys, xlab) in enumerate((
            ('straight segment in pose space  (u = c/s, theta)',
             [p[0] for p in seg['samples']], [p[1] for p in seg['samples']],
             'S07  <- t ->  Trump'),
            ('relaxed path: five tilted squares pinned at a common tilt, all else re-minimised',
             [r['tilt_deg'] for r in fine], [r['s'] for r in fine], 'tilt (deg)'))):
        px = 46 + k * (PW + 90)
        py = y + 26
        xs2 = [v for v, w in zip(xs, ys) if w is not None]
        ys2 = [w for w in ys if w is not None]
        lo, hi = min(ys2), max(ys2)
        pad = 0.08 * (hi - lo) if hi > lo else 0.01
        lo, hi = lo - pad, hi + pad
        x0, x1 = min(xs2), max(xs2)
        body.append(text(px, py - 8, ttl, 9.5, '#333'))
        body.append(f'<rect x="{px}" y="{py}" width="{PW}" height="{PH}" fill="#fafafa" '
                    f'stroke="#bbb" stroke-width="1"/>')
        for val, col, lab in ((s7, '#c62828', 's* (S07)'), (SHAT, '#1565c0', 's-hat (Trump)')):
            yy = py + PH - PH * (val - lo) / (hi - lo)
            body.append(f'<line x1="{px}" y1="{yy:.1f}" x2="{px+PW}" y2="{yy:.1f}" '
                        f'stroke="{col}" stroke-width="1" stroke-dasharray="5,3"/>')
            body.append(text(px + PW - 3, yy - 3, lab, 8, col, False, 'end'))
        pl = ' '.join(f'{px + PW * (v - x0) / (x1 - x0):.1f},'
                      f'{py + PH - PH * (w - lo) / (hi - lo):.1f}'
                      for v, w in zip(xs2, ys2))
        body.append(f'<polyline points="{pl}" fill="none" stroke="#111" stroke-width="1.8"/>')
        kmax = max(range(len(ys2)), key=lambda i: ys2[i])
        mx = px + PW * (xs2[kmax] - x0) / (x1 - x0)
        my = py + PH - PH * (ys2[kmax] - lo) / (hi - lo)
        body.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="4" fill="none" stroke="#ef6c00" '
                    f'stroke-width="2"/>')
        body.append(text(mx + 7, my + 3, f'max {ys2[kmax]:.6f}', 8.5, '#ef6c00'))
        body.append(text(px, py + PH + 12, xlab, 8.5, '#666'))
        body.append(text(px, py + PH + 24,
                         f'range {min(ys2):.6f} .. {max(ys2):.6f}', 8.5, '#666'))
    y = y + 26 + PH + 40

    lines = [
        f"Straight segment: max side {seg['sigma_max']:.9f} at t = {seg['t_max']:.3f}, "
        f"+{seg['barrier_over_S07']:.6f} over S07 and +{seg['barrier_over_trump']:.6f} over Trump.",
        f"Relaxed common-tilt path (the most generous path measured): crest "
        f"{max(r['s'] for r in fine if r['s'] is not None):.9f}, "
        f"+{max(r['s'] for r in fine if r['s'] is not None) - s7:.6f} over S07.  A barrier above "
        f"BOTH ends = two separate local minima, not one basin.",
        "Skeleton: identical.  Six uprights BL(0,0) BL(0,1) BL(0,2) BL(1,0) BR(0,0) TR(0,0) and five "
        "equal-tilt squares in the same cyclic order.  The differences are the tilt (45° vs 40.1819°, "
        "4.818° apart) and Trump's BL(0,2), lifted 0.03256 off its slot.  L-inf pose distance 0.0841.",
        "S07 is the k6_07 packing: the class you land in when Trump's disturbed upright is aligned "
        "into BL(0,2).  Aligning it costs +0.0085345 of side - the exact price of Trump's TL two-crowd.",
    ]
    for t in lines:
        body.append(text(46, y, t, 10, '#333'))
        y += 15

    H = int(y + 12)
    svg = ([f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'font-family="Segoe UI, sans-serif" style="background:#fff">']
           + body + ['</svg>'])
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg))
    print('wrote', OUT)
    import xml.dom.minidom
    xml.dom.minidom.parse(OUT)
    print('xml ok;  Trump worst sep', m1, ' S07 worst sep', m2)
    print('Trump contacts:', c1 + w1)
    print('S07 contacts:', c2 + w2)


if __name__ == '__main__':
    main()
