"""gen_residue128.py -- draw the T3 sample's boundary packings with the menu's verdicts (docs/residue_map conventions:
120 px per unit, dashed corner cells, every drawn square checked for containment and pairwise separation).

Panels: the two A104 fully-held locks (4.000237, 4.001525) with intruders labelled by the menu verdict and the
certified EXCHANGE placements drawn (slot square + re-fit Q0), and Trump (canary).  Output results/residue128.svg."""
import json, math, os, sys
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__)); A128 = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import coupled128 as cm

S = 120
res = {json.loads(l)['packing']: json.loads(l) for l in open(os.path.join(A128, 'results', 'moves128.jsonl'), encoding='utf-8') if l.strip()}
sample = {s['name']: s for s in cm.load_sample()}


def poly(pts, ox, oy, col, fill, dash=False, op=0.5, w=1.6):
    d = ' '.join('%.1f,%.1f' % (ox + p[0] * S, oy - p[1] * S) for p in pts)
    da = ' stroke-dasharray="5,3"' if dash else ''
    return '<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="%.1f"%s/>' % (d, fill, op, col, w, da)


def text(x, y, s, size=11, col='#222', bold=False, anchor='start'):
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return '<text x="%.1f" y="%.1f" font-size="%d" fill="%s" text-anchor="%s"%s>%s</text>' % (x, y, size, col, anchor, ' font-weight="bold"' if bold else '', s)


def check_packing(polys, side, tol=1e-7):
    for p in polys:
        assert all(-tol <= x <= side + tol and -tol <= y <= side + tol for x, y in p), 'outside'
    for i in range(len(polys)):
        for j in range(i + 1, len(polys)):
            assert cm.sep(polys[i], polys[j]) >= -tol, 'overlap %d %d %.2e' % (i, j, cm.sep(polys[i], polys[j]))


def panel(name, ox, oy, body):
    o = res[name]; s = sample[name]; m = o['side']
    poses = [(cx, cy, cm.snap_tilt(th)) for (cx, cy, th) in s['poses']]
    polys = [cm.verts(*p) for p in poses]
    check_packing(polys, m, tol=2e-6 if name.startswith('K') else 1e-7)
    body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#000" stroke-width="2.5"/>' % (ox, oy - m * S, m * S, m * S))
    for cx, cy in [(0, 0), (m - 1, 0), (0, m - 1), (m - 1, m - 1)]:
        body.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" fill="none" stroke="#666" stroke-width="1" stroke-dasharray="4,3"/>' % (ox + cx * S, oy - (cy + 1) * S, S, S))
    verdict = {}
    for r in o['intruders']:
        rb, cb = r['ROT_box']['certified_radius'], r['CLUSTER_box']['certified_radius']
        verdict[r['square']] = (r['corner'], r['depth'], rb, cb, r['CLUSTER_box'].get('cluster'))
    for i, p in enumerate(polys):
        if i in verdict:
            cn, d, rb, cb, cl = verdict[i]
            col, fill = ('#b00', '#f4b6b6') if (rb is None and cb is None) else ('#080', '#bde5bd')
        else:
            col, fill = '#444', '#e6e6e6'
        body.append(poly(p, ox, oy, col, fill))
        cx, cy = poses[i][0], poses[i][1]
        body.append(text(ox + cx * S, oy - cy * S + 4, str(i), 12, col, True, 'middle'))
    for i, (cn, d, rb, cb, cl) in verdict.items():
        cx, cy = poses[i][0], poses[i][1]
        tag = '%s d=%.3g ' % (cn, d) + ('HELD on every box' if (rb is None and cb is None) else 'ROT r=%s' % rb if rb else 'CLUSTER %s r=%s' % (cl, cb))
        body.append(text(ox + cx * S, oy - cy * S + 16, tag, 8, '#000', False, 'middle'))
    # exchange placements
    for cn, e in o['exchange'].items():
        if e.get('certified_radius') is None:
            continue
        u, v, phi = e['Q0_frame']
        Sq = cm.cell_pose(cn, m, 0, 0); Q0 = cm.frame_to_container(cn, m, u, v, phi)
        body.append(poly(cm.verts(*Sq), ox, oy, '#06c', 'none', True, 0.0, 2.2))
        body.append(poly(cm.verts(*Q0), ox, oy, '#06c', 'none', True, 0.0, 2.2))
        A, Qi = e['possible_meeters_box']
        untouched = [cm.verts(*poses[j]) for j in range(11) if j not in (A, Qi)]
        for P in (cm.verts(*Sq), cm.verts(*Q0)):
            assert all(cm.sep(P, U) >= -1e-9 for U in untouched) and cm.wall_gap(P, m) >= -1e-9, 'exchange placement invalid'
        assert cm.sep(cm.verts(*Sq), cm.verts(*Q0)) >= -1e-9
        body.append(text(ox + Q0[0] * S, oy - Q0[1] * S - 14, 'EXCHANGE %s r=%g' % (cn, e['certified_radius']), 9, '#06c', True, 'middle'))
    return m


body = []
titles = {'lock_4.000237': 'A104 lock 4.000237 (held at all 8 under ROT on every box)', 'lock_4.001525': 'A104 lock 4.001525 (Gordan-certified at all 8)',
          'TRUMP_canary': 'Trump (canary): held under every move, no box certifies'}
x = 20
for nm in ('lock_4.000237', 'lock_4.001525', 'TRUMP_canary'):
    if nm not in res:
        continue
    m = panel(nm, x, 560, body)
    body.append(text(x, 60, titles[nm], 13, '#000', True))
    body.append(text(x, 76, 'red = intruder held under ROT and every CLUSTER on every box radius tried; green = certified retreat; blue dashed = certified EXCHANGE (slot square + re-fit Q0)', 8, '#333'))
    x += m * S + 40
doc = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="600" font-family="Segoe UI, sans-serif" style="background:#fff">' % max(x, 980)] + body + ['</svg>']
open(os.path.join(A128, 'results', 'residue128.svg'), 'w', encoding='utf-8').write('\n'.join(doc))
print('wrote residue128.svg')
