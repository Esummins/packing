"""draw130.py -- A130 T1: the flush geometry at K03, K06, cell_l1_124 and the 4.001525 control, drawn
(docs/residue_map conventions: 120 px per unit, dashed corner cells; every drawn square geometry-checked for
containment and pairwise separation).  Flush contacts (edge-on-edge, positive length) are drawn as thick green
segments with their length; the held intruders in red with their Gordan support; the exchange re-fit Q0 (blue
dashed) at every two-meeter corner with the flush blocker(s) marked; the certified moves (FIELD / EX2) in green.
Output: results/flush130.svg."""
import json, math, os, sys
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__)); A130 = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import geom130 as gm

S = 120
res = {}
for l in open(os.path.join(A130, 'results', 'moves130.jsonl'), encoding='utf-8'):
    if l.strip():
        o = json.loads(l); res[o['packing']] = o
a128 = {}
for l in open(os.path.join(gm.A128, 'results', 'moves128.jsonl'), encoding='utf-8'):
    if l.strip():
        o = json.loads(l); a128[o['packing']] = o
sample = {s['name']: s for s in gm.load_sample()}


def poly(pts, ox, oy, col, fill, dash=False, op=0.5, w=1.6):
    d = ' '.join('%.1f,%.1f' % (ox + p[0] * S, oy - p[1] * S) for p in pts)
    da = ' stroke-dasharray="5,3"' if dash else ''
    return '<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="%.1f"%s/>' % (d, fill, op, col, w, da)


def seg(p, q, ox, oy, col, w):
    return '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f" stroke-linecap="round"/>' % (ox + p[0] * S, oy - p[1] * S, ox + q[0] * S, oy - q[1] * S, col, w)


def text(x, y, s, size=11, col='#222', bold=False, anchor='start'):
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return '<text x="%.1f" y="%.1f" font-size="%d" fill="%s" text-anchor="%s"%s>%s</text>' % (x, y, size, col, anchor, ' font-weight="bold"' if bold else '', s)


def check_packing(polys, side, tol):
    for p in polys:
        assert all(-tol <= x <= side + tol and -tol <= y <= side + tol for x, y in p), 'outside'
    for i in range(len(polys)):
        for j in range(i + 1, len(polys)):
            assert gm.sep(polys[i], polys[j]) >= -tol, 'overlap %d %d %.2e' % (i, j, gm.sep(polys[i], polys[j]))


def panel(name, ox, oy, body, title):
    o = res[name]; s = sample[name]; m = o['side']
    poses = [(cx, cy, gm.snap_tilt(th)) for (cx, cy, th) in s['poses']]
    polys = [gm.verts(*p) for p in poses]
    check_packing(polys, m, 2e-6)
    body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#000" stroke-width="2.5"/>' % (ox, oy - m * S, m * S, m * S))
    for cx, cy in [(0, 0), (m - 1, 0), (0, m - 1), (m - 1, m - 1)]:
        body.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" fill="none" stroke="#666" stroke-width="1" stroke-dasharray="4,3"/>' % (ox + cx * S, oy - (cy + 1) * S, S, S))
    verdict = {}
    for cn, cr in o['corners'].items():
        for q, sr in cr['subjects'].items():
            verdict[int(q)] = (cn, sr)
    for i, p in enumerate(polys):
        if i in verdict:
            cn, sr = verdict[i]
            cert = sr['FIELD_box']['certified_radius'] is not None or sr['ROTW_box']['certified_radius'] is not None
            col, fill = ('#080', '#bde5bd') if cert else ('#b00', '#f4b6b6')
        else:
            col, fill = '#444', '#e6e6e6'
        body.append(poly(p, ox, oy, col, fill))
        cx, cy = poses[i][0], poses[i][1]
        body.append(text(ox + cx * S, oy - cy * S + 4, str(i), 12, col, True, 'middle'))
    # flush contacts
    for f in o['flush_contacts']:
        (p, q) = f['segment']
        body.append(seg(p, q, ox, oy, '#0a0', 4.0))
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        if not isinstance(f['pair'][1], str):
            body.append(text(ox + mx * S, oy - my * S - 5, 'L=%.3f' % f['length'], 8, '#060', False, 'middle'))
    # subject labels
    for i, (cn, sr) in verdict.items():
        cx, cy = poses[i][0], poses[i][1]
        fb, rw = sr['FIELD_box']['certified_radius'], sr['ROTW_box']['certified_radius']
        wc = sr['weak_cone']['max_depth_rate']
        tag = '%s d=%.3g ' % (cn, sr['depth_point']) + ('FIELD r=%g' % fb if fb else ('ROT-W r=%g' % rw if rw else 'held on every box')) + ' | point rate %.1e' % wc
        body.append(text(ox + cx * S, oy - cy * S + 16, tag, 7.5, '#000', False, 'middle'))
    # exchange re-fits and their flush blockers
    for cn, cr in o['corners'].items():
        ex = cr.get('EX2', {})
        e128 = (a128.get(name, {}).get('exchange', {}) or {}).get(cn, {})
        if not e128.get('Q0_frame'):
            continue
        u, v, phi = ex.get('Q0_frame', e128['Q0_frame'])
        Sq = gm.cell_pose(cn, m, 0, 0); Q0 = gm.frame_to_container(cn, m, u, v, phi)
        body.append(poly(gm.verts(*Sq), ox, oy, '#06c', 'none', True, 0.0, 2.0))
        body.append(poly(gm.verts(*Q0), ox, oy, '#06c', 'none', True, 0.0, 2.0))
        cert = ex.get('certified_radius')
        tried = ex.get('tried', [])
        F = tried[0]['flush_set'] if tried else []
        lab = 'EX2 %s r=%g' % (cn, cert) if cert else 'EX2 %s: flush vs %s' % (cn, F)
        body.append(text(ox + Q0[0] * S, oy - Q0[1] * S - 14, lab, 8, '#06c', True, 'middle'))
        for j in F:
            body.append(poly(polys[j], ox, oy, '#e60', 'none', False, 0.0, 2.6))
    body.append(text(ox, oy - m * S - 22, title, 12, '#000', True))
    body.append(text(ox, oy - m * S - 8, 'green thick = flush contact (edge-on-edge) with length; red = subject held on every box; green square = certified; blue dashed = slot square + re-fit Q0; orange outline = the flush blocker of Q0', 7.5, '#333'))
    return m


body = []
titles = {'K03': 'K03 (l2_p65_111), side 3.925149', 'K06': 'K06 (l1_159, the S02 pinwheel), side 3.886745',
          'cell_l1_124': 'cell_l1_124 (K02-type), side 3.942810', 'lock_4.001525': 'control: A104 lock 4.001525 (above 4)', 'TRUMP_canary': 'Trump (canary)'}
x = 20; y0 = 560; row = 0
for nm in ('K03', 'K06', 'cell_l1_124', 'lock_4.001525', 'TRUMP_canary'):
    if nm not in res:
        continue
    if x > 1500:
        x = 20; y0 += 600
    m = panel(nm, x, y0, body, titles[nm])
    x += m * S + 40
doc = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Segoe UI, sans-serif" style="background:#fff">' % (1560, y0 + 40)] + body + ['</svg>']
open(os.path.join(A130, 'results', 'flush130.svg'), 'w', encoding='utf-8').write('\n'.join(doc))
print('wrote flush130.svg')
