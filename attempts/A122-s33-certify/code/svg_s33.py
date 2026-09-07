"""A122 T4 - draw S33min beside A108's S07 and Trump, with the conventions of
docs/residue_map/gen_pinwheel_k7_svg.py: S = 160 px per unit, free squares red / slot squares blue,
green circles on every contact point, every square containment- AND overlap-checked before it is
written, and the finished file re-parsed as XML.

Writes docs/residue_map/s33_vs_s07_trump.svg.
"""
from __future__ import annotations

import json
import math
import os
import xml.dom.minidom

import a122lib as A

SHAT = A.SHAT
S = 118                       # px per unit (three panels side by side)
PAD = 34


def sq(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s_), cy + 0.5 * (dx * s_ + dy * c))
            for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def sep(p, q):
    axes = []
    for poly_ in (p, q):
        for i in range(4):
            a, b = poly_[i], poly_[(i + 1) % 4]
            ex, ey = b[0] - a[0], b[1] - a[1]
            n = math.hypot(ex, ey)
            axes.append((-ey / n, ex / n))
    best = -9.0
    for ax in axes:
        pp = [x * ax[0] + y * ax[1] for x, y in p]
        qq = [x * ax[0] + y * ax[1] for x, y in q]
        best = max(best, min(qq) - max(pp), min(pp) - max(qq))
    return best


def esc(t):
    return str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def text(x, y, t, size=11, col='#222', bold=False, anchor='start'):
    b = ' font-weight="bold"' if bold else ''
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{col}" '
            f'text-anchor="{anchor}"{b}>{esc(t)}</text>')


def contact_point(P, Q):
    best = (9.0, None)
    for AA, BB in ((P, Q), (Q, P)):
        for v in AA:
            for k in range(4):
                a, b = BB[k], BB[(k + 1) % 4]
                ex, ey = b[0] - a[0], b[1] - a[1]
                Ln = ex * ex + ey * ey
                t = max(0.0, min(1.0, ((v[0] - a[0]) * ex + (v[1] - a[1]) * ey) / Ln))
                f = (a[0] + t * ex, a[1] + t * ey)
                dd = math.hypot(v[0] - f[0], v[1] - f[1])
                if dd < best[0]:
                    best = (dd, f)
    return best[1]


def panel(ox, oy, s, cfg, names, nfree, title, sub, body):
    """One packing.  (ox, oy) = pixel of the container's LOWER-LEFT corner."""
    polys = [sq(*c) for c in cfg]
    # containment and overlap checks, exactly as the pinwheel generator does them
    for P in polys:
        for x, y in P:
            assert -1e-9 <= x <= s + 1e-9 and -1e-9 <= y <= s + 1e-9, (title, x, y, s)
    m = min(sep(polys[i], polys[j]) for i in range(11) for j in range(i + 1, 11))
    assert m >= -1e-9, (title, m)

    body.append(text(ox, oy - s * S - 26, title, 12.5, bold=True))
    body.append(text(ox, oy - s * S - 11, sub, 9.5, '#444'))
    body.append(f'<rect x="{ox}" y="{oy-s*S:.1f}" width="{s*S:.1f}" height="{s*S:.1f}" '
                f'fill="none" stroke="#000" stroke-width="2.2"/>')
    for (x0, y0) in ((0, 0), (s - 1, 0), (0, s - 1), (s - 1, s - 1)):
        body.append(f'<rect x="{ox+x0*S:.1f}" y="{oy-(y0+1)*S:.1f}" width="{S}" height="{S}" '
                    f'fill="none" stroke="#bbb" stroke-width="1" stroke-dasharray="4,3"/>')
    for i, P in enumerate(polys):
        col, fill = ('#c62828', '#ef9a9a') if i < nfree else ('#1565c0', '#90caf9')
        pts = ' '.join(f'{ox+x*S:.1f},{oy-y*S:.1f}' for x, y in P)
        body.append(f'<polygon points="{pts}" fill="{fill}" fill-opacity="0.6" stroke="{col}" '
                    f'stroke-width="1.5"/>')
        cx, cy, th = cfg[i]
        body.append(text(ox + cx * S, oy - cy * S + 3, names[i], 9, '#000', True, 'middle'))
        body.append(text(ox + cx * S, oy - cy * S + 13, f'{A.tmod(th):.2f}°', 7.5, '#333',
                         False, 'middle'))
    contacts = []
    for i in range(11):
        for j in range(i + 1, 11):
            if sep(polys[i], polys[j]) < 1e-7:
                contacts.append(f'{names[i]}–{names[j]}')
                f = contact_point(polys[i], polys[j])
                body.append(f'<circle cx="{ox+f[0]*S:.1f}" cy="{oy-f[1]*S:.1f}" r="4" fill="none" '
                            f'stroke="#2e7d32" stroke-width="1.8"/>')
    walls = []
    for i, (cx, cy, th) in enumerate(cfg):
        w = (abs(math.cos(th)) + abs(math.sin(th))) / 2
        for nmw, g in (('left', cx - w), ('right', s - w - cx),
                       ('bottom', cy - w), ('top', s - w - cy)):
            if g < 1e-7:
                walls.append(f'{names[i]}–{nmw}')
    return m, contacts, walls


def main():
    d = json.load(open(os.path.join(A.RES, 'polish.json'), encoding='utf-8'))
    b = d['entries']['S33']['best']
    s33, cfg33 = b['sigma'], [tuple(c) for c in b['cfg']]
    n33 = A.names_for('S33')
    s07, cfg07 = A.load_s07_exact()
    st, cfgt = A.load_trump()
    # Trump in the same reading order: the five tilted squares first
    order = sorted(range(11), key=lambda i: (A.tmod(cfgt[i][2]) < 1e-6, i))
    cfgt = [cfgt[i] for i in order]
    nt = [f'f{k}' if A.tmod(cfgt[k][2]) > 1e-6 else f'u{k}' for k in range(11)]

    body = []
    y0 = 104
    W1 = s33 * S + PAD
    oxs = [PAD, PAD + W1 + 26, PAD + 2 * (W1 + 26)]
    oy = y0 + max(s33, s07, st) * S

    res = {}
    res['S33'] = panel(oxs[0], oy, s33, cfg33, n33, 5,
                       f'S33 = S34 = K19  (A122)   s* = {s33:.9f}',
                       f's* − s0 = +{s33-A.S0:.6f},  s* − s-hat = +{s33-SHAT:.6f};  '
                       f'k6_07 skeleton, 5 free', body)
    res['S07'] = panel(oxs[1], oy, s07, cfg07,
                       list(A.FREE) + list(A.SLOTS), 5,
                       f'S07  (A108)   s* = 2 + 4√2/3 = {s07:.9f}',
                       f's* − s0 = +{s07-A.S0:.6f};  same k6_07 skeleton, every tilt 45°',
                       body)
    res['Trump'] = panel(oxs[2], oy, st, cfgt, nt, 5,
                         f'Trump   s-hat = {st:.9f}',
                         's-hat − s0 = −0.00000041;  the global minimum, '
                         'five squares at 40.182°, column lifted', body)

    def wrap(items, per):
        return [', '.join(items[i:i + per]) for i in range(0, len(items), per)]

    yy = oy + 22
    ymax = yy
    for k, ox in zip(('S33', 'S07', 'Trump'), oxs):
        m, contacts, walls = res[k]
        y = yy
        body.append(text(ox, y, f'{k}: min pairwise SAT separation {m:+.1e}', 9, '#444'))
        y += 13
        for n, line in enumerate(wrap(contacts, 5)):
            body.append(text(ox, y, ('contacts: ' if n == 0 else '   ') + line, 8, '#333'))
            y += 10
        for n, line in enumerate(wrap(walls, 5)):
            body.append(text(ox, y, ('walls: ' if n == 0 else '   ') + line, 8, '#333'))
            y += 10
        ymax = max(ymax, y)
    yy = ymax

    hdr = ('A122 - S33 (= S34 = K19) certified against A108\'s S07 and Trump.  All three sit on '
           'the SAME six-cell k6_07 slot skeleton (BL column of three, BL(1,0), BR(0,0), TR(0,0)); '
           'they are three distinct local minima of the side.')
    hdr2 = ('S07 is the 45° point (every tilt equal, side in Q(√2)); S33 has FOUR different '
            'tilts (0°, 40.00° twice, 51.45°, 47.09°) and its f0 is UPRIGHT, flush against the '
            'column\'s right face x = 1; Trump lifts BL(0,2) off the column.  Green circles = contact points.')
    body.insert(0, text(PAD, 24, hdr, 12.5, '#000', True))
    body.insert(1, text(PAD, 42, hdr2, 10, '#444'))

    Wpx = int(oxs[-1] + st * S + PAD)
    Hpx = int(yy + 16)
    doc = ([f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wpx}" height="{Hpx}" '
            f'font-family="Segoe UI, sans-serif" style="background:#fff">'] + body + ['</svg>'])
    out = os.path.join(A.ROOT, 'docs', 'residue_map', 's33_vs_s07_trump.svg')
    open(out, 'w', encoding='utf-8').write('\n'.join(doc))
    xml.dom.minidom.parse(out)
    print('wrote', out, '- xml ok')
    for k in res:
        m, c, w = res[k]
        print(f'  {k}: min SAT sep {m:+.2e}, {len(c)} pair contacts, {len(w)} wall contacts')
    json.dump({k: dict(min_sat=res[k][0], contacts=res[k][1], walls=res[k][2]) for k in res},
              open(os.path.join(A.RES, 'svg.json'), 'w', encoding='utf-8'), indent=1)


if __name__ == '__main__':
    main()
