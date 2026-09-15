"""A217 pages: docs/residue_map/campaigns/A217-torque/torque217_<wid>.svg -- the packing with the Fritz-John
contact forces drawn as arrows (wall forces blue, square-square forces black, external crowd / tilt-bound
forces red), the per-corner signed torques annotated, and a gallery of the drawn witnesses.
    python fig217.py [--max-per-class 8]
"""
import argparse
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom217 as G

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
RES = os.path.join(ATT, 'results')
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
OUT = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A217-torque')
SC = 110.0
PAD = 70.0


def P(x, y, s):
    return PAD + SC * x, PAD + SC * (s - y)


def arrow(x0, y0, x1, y1, col, w=1.6):
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f" marker-end="url(#ah_%s)"/>'
            % (x0, y0, x1, y1, col, w, col.strip('#')))


def page(w, t):
    z = np.array(w['z'])
    s = z[33]
    q = G.corners(z)
    Wd = int(2 * PAD + SC * s)
    H = Wd + 150
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (Wd, H, Wd, H)]
    o.append('<defs>' + ''.join('<marker id="ah_%s" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#%s"/></marker>' % (c, c) for c in ('1f77b4', '000000', 'd62728', 'ff7f0e')) + '</defs>')
    o.append('<rect width="100%%" height="100%%" fill="white"/>')
    x0, y0 = P(0, s, s)
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#f7f7f7" stroke="#333" stroke-width="2"/>' % (x0, y0, SC * s, SC * s))
    # corner boxes
    for cn in G.CORNER_NAMES:
        M, tt, det = G.corner_frame(cn, s)
        Minv = np.linalg.inv(M)
        pts = [Minv @ (np.array(p) - tt) for p in ((0, 0), (1, 0), (1, 1), (0, 1))]
        o.append('<polygon points="%s" fill="none" stroke="#999" stroke-dasharray="4,3"/>' % ' '.join('%.1f,%.1f' % P(p[0], p[1], s) for p in pts))
    corners = t.get('corners', {})
    tilts = w['tilts_deg']
    for i in range(G.N):
        settled_here = any(e['settled'] == i for e in corners.values()) or any(v == i for v in w['settled'].values())
        meeter = any(i in e['meeters'] for e in corners.values())
        fill = '#c7e9c0' if settled_here else ('#fdd0a2' if meeter else '#dadaeb')
        o.append('<polygon points="%s" fill="%s" stroke="#444" stroke-width="1"/>' % (' '.join('%.1f,%.1f' % P(q[i, k, 0], q[i, k, 1], s) for k in range(4)), fill))
        cx, cy = P(z[3 * i], z[3 * i + 1], s)
        o.append('<text x="%.1f" y="%.1f" font-size="11" text-anchor="middle" font-family="sans-serif">%d (%.1f&#176;)</text>' % (cx, cy + 4, i, tilts[i] % 90))
    lam_max = max([a['lam'] for a in t.get('arrows', [])] + [1e-9])
    for a in t.get('arrows', []):
        f = np.array(a['f'])
        L = 0.55 * (np.linalg.norm(f) / lam_max) ** 0.5 + 0.08
        d = f / (np.linalg.norm(f) + 1e-15)
        p = np.array(a['p'])
        col = {'wall': '#1f77b4', 'edge': '#000000', 'crowd': '#d62728', 'tiltbound': '#ff7f0e'}[a['kind']]
        x1, y1 = P(p[0] - L * d[0], p[1] - L * d[1], s)
        x2, y2 = P(p[0], p[1], s)
        o.append(arrow(x1, y1, x2, y2, col, 1.2 + 2.0 * np.linalg.norm(f) / lam_max))
    # corner torque labels
    for cn, e in corners.items():
        M, tt, det = G.corner_frame(cn, s)
        anchor = np.linalg.inv(M) @ (np.array([0.5, 0.5]) - tt)
        ax, ay = P(anchor[0], anchor[1], s)
        lab = '%s: %s T=%+.3f' % (cn, 'settled' if e['settled'] is not None else '%d meeter%s' % (len(e['meeters']), '' if len(e['meeters']) == 1 else 's'), e['T'])
        o.append('<text x="%.1f" y="%.1f" font-size="10" font-family="sans-serif" fill="#a00" text-anchor="middle">%s</text>' % (ax, ay - 14, lab))
        for m in e['members']:
            if m['chi'] != 0 and m['W'] > 1e-9:
                o.append('<text x="%.1f" y="%.1f" font-size="9" font-family="sans-serif" fill="#a00" text-anchor="middle">sq%d chi=%+d tw=%+.3f th=%+.3f tb=%+.3f</text>' % (ax, ay + 24 + 10 * m['i'] % 20, m['i'], m['chi'], m['tau_wall_frame'], m['tau_hold_frame'], m['tau_bound_frame']))
    # note
    y = Wd + 16
    lines = ['A217 %s  class %s  side %.6f (s-hat 3.877084)  FJ %s  rows %d  res %.1e' % (w['wid'], w['cls'], w['s'], t.get('fj', '?'), t.get('n_rows', 0), t.get('fj_res', 1)),
             'WHAT THIS IS: a %s of the side of 11 unit squares; arrows = Fritz-John contact forces (blue wall, black square-square, red external crowd / orange tilt-bound row)' % ('local optimum' if w['cls'] in ('K0FREE', 'SETTLED', 'BOXK0') else 'held local optimum (NOT an FJ point of the free problem)'),
             'corner frame torques: tw = from the walls, th = from the holders, tb = external; chi = +1 if the tilt in the corner frame is < 45 deg.  T = sum over the meeters of tw.',
             'settled corners %d, doubly-met corners %d, tilt bounds active %d, crowd rows active %d; total wall torque about the centre %.2e; pressures %s' % (
                 sum(v is not None for v in w['settled'].values()), w['n2'], w.get('n_tiltbound_active', 0), w.get('n_crowd_active', 0),
                 t.get('total_wall_torque', float('nan')), {k: round(v, 3) for k, v in t.get('wall_pressure', {}).items()}),
             'verifier: A217 stress217.analyse (HiGHS LP on the active rows, NNLS residual); drawn by fig217.py; run id %s' % w['rid']]
    for ln in lines:
        o.append('<text x="10" y="%d" font-size="10" font-family="sans-serif">%s</text>' % (y, ln.replace('&', '&amp;').replace('<', '&lt;')))
        y += 14
    o.append('</svg>')
    return '\n'.join(o)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--max-per-class', type=int, default=8)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    W = [json.loads(l) for l in open(os.path.join(RES, 'witnesses217.jsonl'))]
    T = {json.loads(l)['wid']: json.loads(l) for l in open(os.path.join(RES, 'torque217.jsonl'))}
    per = {}
    drawn = []
    for w in sorted(W, key=lambda w: (w['cls'], w['s'])):
        c = per.get(w['cls'], 0)
        if c >= a.max_per_class and not (w['cls'] == 'HELD' and w['n2'] == 4) and not (w['cls'] == 'K0FREE' and w['n2'] >= 3) and w['rid'] != 'atlas_trump_raw|free':
            continue
        per[w['cls']] = c + 1
        t = T.get(w['wid'], {})
        open(os.path.join(OUT, 'torque217_%s.svg' % w['wid']), 'w').write(page(w, t))
        drawn.append((w, t))
    # gallery: one row per drawn witness
    rows = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="%d" viewBox="0 0 1100 %d">' % (30 + 16 * (len(drawn) + 3), 30 + 16 * (len(drawn) + 3)),
            '<rect width="100%" height="100%" fill="white"/>',
            '<text x="10" y="18" font-size="12" font-family="sans-serif">A217 torque probe gallery: wid | class | side | doubly-met corners | settled | external rows | per-corner T (BL,BR,TR,TL) -- pages torque217_&lt;wid&gt;.svg</text>']
    y = 40
    for w, t in drawn:
        Ts = ' '.join('%+.3f' % t['corners'][cn]['T'] if 'corners' in t else '?' for cn in G.CORNER_NAMES)
        rows.append('<text x="10" y="%d" font-size="10" font-family="monospace">%-14s %-8s %.6f n2=%d settled=%d ext=%d  T=[%s]</text>' % (
            y, w['wid'], w['cls'], w['s'], w['n2'], sum(v is not None for v in w['settled'].values()), w.get('n_tiltbound_active', 0) + w.get('n_crowd_active', 0), Ts))
        y += 16
    rows.append('</svg>')
    open(os.path.join(OUT, 'torque217_gallery.svg'), 'w').write('\n'.join(rows))
    print('drew', len(drawn), 'pages to', OUT)


if __name__ == '__main__':
    main()
