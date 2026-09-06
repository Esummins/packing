"""A104 drawing: (a) the two jammed-grid packings and the intruder Lemma ROT's closing step walks out of
its corner cell (T1: the grid is LOCK-FREE too), (b) the lowest fully-held K0-BLOCKED packing found
(T2: side m_lock), with every intruder's contact points and its Gordan multipliers.

Conventions of docs/residue_map/gen_nondrainers.py (unit cells dashed, first meeters blue, second meeters
red, everything geometry-checked: containment and pairwise SAT gap >= -5e-9).  Writes
attempts/A104-grid-lock/results/lock104.svg.
"""
from __future__ import annotations

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
A104 = os.path.dirname(HERE)
RES = os.path.join(A104, 'results')

S = 118


def sq(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s_), cy + 0.5 * (dx * s_ + dy * c))
            for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]


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


def cell_depth(p, x0, y0):
    xs = [x for x, y in p]
    ys = [y for x, y in p]
    dx = min(max(xs), x0 + 1) - max(min(xs), x0)
    dy = min(max(ys), y0 + 1) - max(min(ys), y0)
    return min(dx, dy) if dx > 1e-12 and dy > 1e-12 else 0.0


def esc(t):
    return str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def text(x, y, t, size=11, col='#222', bold=False, anchor='start'):
    b = ' font-weight="bold"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-size="%s" fill="%s" text-anchor="%s"%s>%s</text>'
            % (x, y, size, col, anchor, b, esc(t)))


RED = ('#c62828', '#ef9a9a')
BLUE = ('#1565c0', '#90caf9')
GREY = ('#555', '#e0e0e0')
GREEN = ('#2e7d32', '#a5d6a7')


def panel(ox, oy, title, sub, s, P, mark=None, contacts=None, held=False):
    polys = [sq(*q) for q in P]
    assert all(-5e-9 <= x <= s + 5e-9 and -5e-9 <= y <= s + 5e-9
               for p in polys for x, y in p), 'containment ' + title
    m = min(sep(polys[i], polys[j]) for i in range(11) for j in range(i + 1, 11))
    assert m >= -5e-9, (title, m)
    corners = {'BL': (0, 0), 'BR': (s - 1, 0), 'TR': (s - 1, s - 1), 'TL': (0, s - 1)}
    meet = {cn: sorted([(cell_depth(p, *c), i) for i, p in enumerate(polys)
                        if cell_depth(p, *c) > 1e-9], reverse=True)
            for cn, c in corners.items()}
    first = {ds[0][1] for ds in meet.values() if ds}
    second = {d[1] for ds in meet.values() for d in ds[1:]}
    out = [text(ox, oy - s * S - 30, title, 12.5, bold=True),
           text(ox, oy - s * S - 15, sub, 10, '#444')]
    out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#000" '
               'stroke-width="2.2"/>' % (ox, oy - s * S, s * S, s * S))
    for cn, (x0, y0) in corners.items():
        out.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" fill="none" stroke="#999" '
                   'stroke-width="1" stroke-dasharray="4,3"/>'
                   % (ox + x0 * S, oy - (y0 + 1) * S, S, S))
        out.append(text(ox + (x0 + 0.5) * S, oy - (y0 + 0.5) * S - 26,
                        '%s: %d' % (cn, len(meet[cn])), 9,
                        '#2e7d32' if len(meet[cn]) < 2 else '#777', True, 'middle'))
    for i, p in enumerate(polys):
        col, fill = (GREEN if (held and (i in first or i in second))
                     else RED if i in second else BLUE if i in first else GREY)
        if mark is not None and i == mark:
            col, fill = ('#6a1b9a', '#ce93d8')
        pts = ' '.join('%.1f,%.1f' % (ox + x * S, oy - y * S) for x, y in p)
        out.append('<polygon points="%s" fill="%s" fill-opacity="0.6" stroke="%s" '
                   'stroke-width="1.6"/>' % (pts, fill, col))
        t = math.degrees(P[i][2]) % 90
        t = min(t, 90 - t)
        out.append(text(ox + P[i][0] * S, oy - P[i][1] * S + 4, str(i), 10.5, '#000', True, 'middle'))
        out.append(text(ox + P[i][0] * S, oy - P[i][1] * S + 14, '%.2f' % t + '°', 7.5,
                        '#333', False, 'middle'))
    for c in (contacts or []):
        x, y = c
        out.append('<circle cx="%.1f" cy="%.1f" r="3.4" fill="none" stroke="#c62828" '
                   'stroke-width="1.4"/>' % (ox + x * S, oy - y * S))
    return out


def main():
    import sys
    sys.dont_write_bytecode = True
    sys.path.insert(0, os.path.join(A104, '..', 'A87-drain-flow', 'code'))
    sys.path.insert(0, os.path.join(A104, '..', 'A103-noroom', 'code'))
    import lock103 as L

    C = {c['name']: c for c in L.load_corpus()}
    t1 = {json.loads(l)['tag']: json.loads(l)
          for l in open(os.path.join(RES, 't1_close.jsonl'), encoding='utf-8')}
    summ = json.load(open(os.path.join(RES, 'a104_summary.json'), encoding='utf-8'))

    W, Hh = 2000, 1180
    body = ['<text x="26" y="34" font-size="17" font-weight="bold" fill="#111">'
            'A104 - the closing iteration of Lemma ROT: the jammed grid drains too, and fully-held '
            'K0-BLOCKED packings start above 4</text>',
            '<text x="26" y="54" font-size="11" fill="#444">Dashed = the four unit corner cells. '
            'Blue = first meeter, red = second meeter, purple = the intruder the closing step walks '
            'OUT of its cell, green = held (Gordan certificate). Per-corner meeter count printed '
            'above each cell; green count = the corner that freed.</text>']

    # (a) the two grid packings, before and after the closing
    x = 40
    for name, lbl in (('polish12_s0380', 'polish12'), ('floor_1e-04_d1em04_s0202', 'floor 1e-4')):
        r = t1[name]
        ex = [m for rd in r['rounds'] for m in rd['moves'] if m['why'] == 'exited' or m['exits_cell']]
        e = ex[0] if ex else None
        c = C[name]
        body += panel(x, 620, '%s  (before)' % lbl,
                      'side %.7f, strictly K0-BLOCKED' % c['side'], c['side'], c['poses'],
                      mark=(e['square'] if e else None))
        after = [tuple(p) for p in r['poses']]
        mc = r['final']['meet_counts']
        freed = [k for k in ('BL', 'BR', 'TR', 'TL') if mc[k] < 2]
        body += panel(x, 1130, '%s  (after: corner %s free)' % (lbl, ','.join(freed)),
                      'side %.7f; %s sq%d leaves after travel %.1e (%s)'
                      % (r['side_end'], e['corner'], e['square'], e['travel'], e['free_by'])
                      if e else 'side %.7f' % r['side_end'],
                      r['side_end'], after, mark=(e['square'] if e else None))
        x += int(c['side'] * S) + 90

    # (b) the m_lock packing
    rec = summ.get('m_lock_certified_record') or summ.get('m_lock_record')
    if rec:
        pts = [tuple(cc['point']) for it in rec['intruders'] for cc in it['contacts']]
        body += panel(x + 20, 620, 'm_lock = %.7f  (fully held)' % rec['side'],
                      'every one of the 8 intruders HELD (Gordan multipliers certified); '
                      'contact points circled', rec['side'], [tuple(p) for p in rec['poses']],
                      contacts=pts, held=True)
        yy = 700
        body.append(text(x + 20, yy, 'per-intruder Gordan certificate', 12, '#111', True))
        yy += 18
        for it in rec['intruders']:
            b = it['branches'][0]['cert']
            body.append(text(x + 20, yy,
                             '%s sq%-2d  d=%.3e  tilt %.3f deg  contacts %d (%d square / %d wall)  '
                             'lambda_tot=%.4f' % (it['corner'], it['square'], it['depth'],
                                                  it['tilt_deg'], it['n_contacts'],
                                                  it['n_sq_contacts'], it['n_wall_contacts'],
                                                  (b or {}).get('lam_total', float('nan'))), 10))
            yy += 15

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
           'font-family="DejaVu Sans, Arial, sans-serif"><rect width="%d" height="%d" fill="#fff"/>'
           % (W, Hh, W, Hh, W, Hh)) + '\n'.join(body) + '</svg>'
    p = os.path.join(RES, 'lock104.svg')
    open(p, 'w', encoding='utf-8').write(svg)
    print('wrote', p, len(svg), 'bytes')


if __name__ == '__main__':
    main()
