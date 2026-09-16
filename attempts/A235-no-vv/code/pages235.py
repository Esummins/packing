"""A235 page (docs/residue_map/campaigns/A235-no-vv/ring_vv_4_6.svg): the ring's lean 4|6 -- the tilted
vertex-on-vertex contact at the triple point P (4's corner = 6's corner = rattler 0's corner), the two separating
edge lines, the physical force cone at P, the rolling directions (rotation of 6 and of 4 about P) with the rows that
block each sense at first order, the inverted-pendulum curvatures of the two VV rows, and (inset) the reflex
feasible cone of the pair's relative translation: {g_A >= 0} u {g_B >= 0}.  Geometry-checked (draw219.Page.check:
arrow feet on the boundary, no pair overlap, no wall crossing) with a note per panel.
    python pages235.py
"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vv235 as V             # noqa: E402
import roll235 as RL          # noqa: E402
import stress234 as ST        # noqa: E402
import rows219 as R           # noqa: E402
import draw219 as D           # noqa: E402
import geom217 as G           # noqa: E402

PAGES = os.path.join(V.ATT, '..', '..', 'docs', 'residue_map', 'campaigns', 'A235-no-vv')
os.makedirs(PAGES, exist_ok=True)
RID = 'rand_0_0569|t20'
ORANGE, BLUE, GREY = ('#fde9c9', '#b06a00'), ('#dbe9f6', '#1f4e79'), ('#eeeeee', '#888')


def blocking_rows(z, rows, A, i, P, lam):
    out = {}
    for om, name in ((1.0, 'ccw'), (-1.0, 'cw')):
        y = RL.rot_mode(z, i, P) * om
        rates = A @ y
        out[name] = [(k, rows[k], float(rates[k]), float(lam[k])) for k in range(len(rows)) if rates[k] < -1e-9]
    return out


def row_label(r):
    if r['kind'] == 'wall':
        return 'wall %s of %d' % (r['wall'], r['i'])
    if r['kind'] == 'edge':
        return "%d's corner on %d's edge%s" % (r['i'], r['j'], '' if r.get('on_segment', True) else ' (line row)')
    if r['kind'] == 'tiltbound':
        return 'tilt bound of %d' % r['i']
    return r['kind']


def main():
    t0 = time.time()
    raw = [json.loads(l) for l in open(ST.WIT, encoding='utf-8') if RID in l][0]
    w = ST.from_w217(raw)
    z, rows, A, lam = w['z'], w['rows'], w['A'], w['lam']
    cen, cts = V.analyse(w)
    e = next(x for x in cen['vv'] if x['pair'] == [4, 6])
    P = np.array(e['P'])
    terms = RL.contact_terms(z, rows, e['rowA'], e['rowB'], P, 4, 6)
    nrm = G.normals(z)
    n_e = nrm[rows[e['rowA']]['j'], rows[e['rowA']]['edge']]      # 4's separating edge normal (force on 6 along +n_e)
    n_f = nrm[rows[e['rowB']]['j'], rows[e['rowB']]['edge']]      # 6's separating edge normal (force on 6 along -n_f)
    roll = [json.loads(l) for l in open(os.path.join(V.ATT, 'results', 'novv235.jsonl'), encoding='utf-8')
            if l.startswith('{"wid": "%s"' % raw['wid'])]
    ro = next(o for o in roll if o['pair'] == [4, 6])

    pg = D.Page(z, width_notes=520, height_extra=300)
    pg.frame()
    pg.squares({4: ORANGE, 6: ORANGE, 0: BLUE, 7: GREY, 5: GREY})
    q = G.corners(z)
    # the two separating edge lines through P (dashed), the force cone at P on square 6
    for owner, edge, col in ((rows[e['rowA']]['j'], rows[e['rowA']]['edge'], '#b06a00'), (rows[e['rowB']]['j'], rows[e['rowB']]['edge'], '#1f4e79')):
        a, b = q[owner, edge], q[owner, (edge + 1) % 4]
        d = (b - a) / np.linalg.norm(b - a)
        p0, p1 = pg.P(*(P - 0.9 * d)), pg.P(*(P + 0.9 * d))
        pg.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.2" stroke-dasharray="5,4"/>' % (p0[0], p0[1], p1[0], p1[1], col))
    pg.arrow(P, n_e, '#b06a00', length=0.5, on_square=6)
    pg.arrow(P, -n_f, '#1f4e79', length=0.5, on_square=6)
    # rolling: velocity of 6's and 4's far corners under rotation about P (ccw), drawn as short arrows
    for i, col in ((6, '#d62728'), (4, '#2ca02c')):
        for k in range(4):
            v = R.jrot(q[i, k] - P)
            if np.linalg.norm(v) > 1e-9:
                pg.arrow(q[i, k], v, col, width=1.2, length=0.22, on_square=i)
    pg.dot(P, '#d62728', r=5, label='P')
    blk = {i: blocking_rows(z, rows, A, i, P, lam) for i in (4, 6)}
    pg.line('A235 -- the ring (%s, s = %.4f): the lean 4|6 is a tilted VERTEX-ON-VERTEX contact' % (RID, z[R.S_IDX]), bold=True)
    pg.line('tilts 4: %.0f deg, 6: %.0f deg (gap 40 deg); P = (%.4f, %.4f) = corner of 4 = corner of 6 = corner of rattler 0' % (
        math.degrees(z[14]), math.degrees(z[20]), P[0], P[1]))
    pg.line('dashed: the two separating edge lines through P (orange: 4\'s edge e, blue: 6\'s edge f); the pair is')
    pg.line('interior-disjoint near P iff  g_A >= 0  OR  g_B >= 0  (a UNION of half-spaces; inset below).')
    pg.line('arrows at P: the physical force cone on 6, between n_e (orange, selection S_A) and -n_f (blue, S_B).')
    pg.line('load of the 4|6 rows over the FJ polytope: [%.3f, %.3f]; 0|6 rows: [%.3f, %.3f] -- the 0.572 crosses the' % (
        e['load_range'][0], e['load_range'][1], *next(x for x in cen['vv'] if x['pair'] == [0, 6])['load_range']))
    pg.line('triple point through 4|6 or through 0|6: the rows are DEPENDENT (grad g_A in the span of the others).')
    pg.line('two-selection test: S_A %s, S_B %s (both KKT: no first-order exclusion at this pair).' % (e['sel_A'], e['sel_B']))
    pg.line('')
    pg.line('The rolling plane at P (rotations of 6 (red) and of 4 (green) about P; both VV rows exactly zero):', bold=True)
    for i in (6, 4):
        for sense in ('ccw', 'cw'):
            rs = blk[i][sense]
            pg.line('  %d %s: blocked at first order by %s' % (i, sense, '; '.join('%s (rate %.2f, lam %.2f)' % (row_label(r), rt, lm) for _, r, rt, lm in rs[:3])
                                                              + (' ...' if len(rs) > 3 else '')), size=11)
    pg.line('  every direction of the plane is blocked with all rows kept (%d / 72 feasible for S_A, S_B, S_AB): no second-order' % ro['S_A'].get('n_feasible', 0), size=11)
    pg.line('  test applies here -- the contact is torque-locked by 7 (ccw) and by the floor + the tilt bound (cw) on 6,', size=11)
    pg.line('  by the wall + tilt bound (ccw) and by 0, 5 (cw) on 4.  A219\'s strut mode is a rotation of 6 about the', size=11)
    pg.line('  7-contact, NOT about P: v2 = +0.381 there, and P then leaves 4 at second order.', size=11)
    pg.line('')
    pg.line('Curvature of the VV rows along the rolling (the inverted-pendulum terms, Theorem SO):', bold=True)
    pg.line('  rot 6 about P: y^T H_A y = h_B = n_e.(c_6 - P) = %.4f, y^T H_B y = 1/2;  rot 4: y^T H_B y = h_A = %.4f, y^T H_A y = 1/2' % (
        terms['h_B'], terms['h_A']), size=11)
    pg.line('  contribution to y^T Hess(L) y: -lam_A h_B - lam_B / 2 < 0 whenever loaded -- a knife-edge IF the rolling were feasible.', size=11)
    # ---- inset: the reflex cone of relative translation u of 6's vertex (frame: n_e up)
    x0, y0, rr = D.M + 130, D.M + D.S * pg.s + 150, 95
    pg.o.append('<text x="%d" y="%d" font-size="12" fill="#222" font-weight="bold">inset: feasible relative translations u of 6\'s vertex at P</text>' % (D.M, y0 - rr - 30))
    pg.o.append('<text x="%d" y="%d" font-size="11" fill="#222">feasible iff n_e.u &gt;= 0 (orange half-plane) or n_f.u &lt;= 0 (blue); the excluded wedge (hatched) is</text>' % (D.M, y0 - rr - 14))
    ang_e = math.atan2(n_e[1], n_e[0])
    ang_f = math.atan2(-n_f[1], -n_f[0])
    # half-planes as arcs of radius rr: H_A = {angle in [ang_e - 90, ang_e + 90]}, H_B = {angle in [ang_f - 90, ang_f + 90]}
    def arc(a0, a1, col, op):
        pts = ['%.1f,%.1f' % (x0, y0)] + ['%.1f,%.1f' % (x0 + rr * math.cos(a0 + (a1 - a0) * k / 60), y0 - rr * math.sin(a0 + (a1 - a0) * k / 60)) for k in range(61)]
        pg.o.append('<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="none"/>' % (' '.join(pts), col, op))
    arc(ang_e - math.pi / 2, ang_e + math.pi / 2, '#fde9c9', 0.9)
    arc(ang_f - math.pi / 2, ang_f + math.pi / 2, '#dbe9f6', 0.7)
    # the excluded wedge = complement of the union: from ang_e + 90 to ang_f - 90 (mod 2pi), going the short way
    dd = ((ang_f - ang_e + math.pi) % (2 * math.pi)) - math.pi          # signed angle from n_e to -n_f
    if dd >= 0:
        lo, hi = ang_f + math.pi / 2, ang_e - math.pi / 2 + 2 * math.pi
    else:
        lo, hi = ang_e + math.pi / 2, ang_f - math.pi / 2 + 2 * math.pi
    excl = math.degrees(hi - lo)
    arc(lo, hi, 'url(#stip)', 1.0)
    for ang, col, lab in ((ang_e, '#b06a00', 'n_e'), (ang_f, '#1f4e79', '-n_f')):
        pg.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2" marker-end="url(#ah)"/>' % (
            x0, y0, x0 + 0.8 * rr * math.cos(ang), y0 - 0.8 * rr * math.sin(ang), col))
        pg.o.append('<text x="%.1f" y="%.1f" font-size="11" fill="%s">%s</text>' % (x0 + 0.9 * rr * math.cos(ang), y0 - 0.9 * rr * math.sin(ang), col, lab))
    pg.o.append('<circle cx="%.1f" cy="%.1f" r="%d" fill="none" stroke="#333"/>' % (x0, y0, rr))
    cone_deg = 360.0 - excl
    pg.o.append('<text x="%d" y="%d" font-size="11" fill="#222">the overlap directions (4\'s wedge and the reflected wedge of 6): %.0f deg; the feasible cone is REFLEX, %.0f deg</text>' % (D.M, y0 + rr + 20, excl, cone_deg))
    pg.o.append('<text x="%d" y="%d" font-size="11" fill="#222">(&gt; 180: it contains the lines through P along e and along f, so the first-order condition is KKT for S_A AND for S_B).</text>' % (D.M, y0 + rr + 36))
    # geometry check of the inset: the excluded wedge equals 180 - angle(n_e, -n_f), the wedges are disjoint
    ang_between = math.degrees(math.acos(max(-1.0, min(1.0, float(n_e @ (-n_f))))))
    assert abs(excl - (180.0 - ang_between)) < 1e-6, (excl, ang_between)
    pg.o.append('<text x="%d" y="%d" font-size="10" fill="#666">inset geometry checked: excluded wedge %.4f deg = 180 - angle(n_e, -n_f) = 180 - %.4f.</text>' % (D.M, y0 + rr + 52, excl, ang_between))
    path = pg.write(os.path.join(PAGES, 'ring_vv_4_6.svg'), t0)
    print('wrote', path, 'excluded wedge %.2f deg' % excl)


if __name__ == '__main__':
    ST.set_priority()
    main()
