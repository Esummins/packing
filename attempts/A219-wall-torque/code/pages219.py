"""A219 pages (docs/residue_map/campaigns/A219-wall-torque/):
  ring_residual_rand_0_0569_t20.svg  -- the nine-square ring with the torque residual per meeter (the minimal
                                        external torques that close the free balance) and the force+torque
                                        minimal external load;
  ring_mode_rand_0_0569_t20.svg      -- the strut mode of square 6 (addendum 2b): contact points, the
                                        collinear force, the rotation, the floor gap, the caged rattler;
  best_attempt_<wid>.svg             -- the best 11-square attempt (holder219 drain with the smallest crowd
                                        residual) with its external pulls.
    python pages219.py
"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rows219 as R                 # noqa: E402
import ring219 as RING              # noqa: E402
import modes219 as MO               # noqa: E402
import second219 as S2              # noqa: E402
import draw219 as D                 # noqa: E402
import geom217 as G                 # noqa: E402
import opt217 as O                  # noqa: E402
import crowd217 as C                # noqa: E402
import stress217 as ST              # noqa: E402

PAGES = os.path.join(RING.ATT, '..', '..', 'docs', 'residue_map', 'campaigns', 'A219-wall-torque')
os.makedirs(PAGES, exist_ok=True)
RID = 'rand_0_0569|t20'
ORANGE, BLUE, RED = ('#fde9c9', '#b06a00'), ('#dbe9f6', '#1f4e79'), ('#f9d5d3', '#a11')


def load_ring():
    w = [x for x in RING.four_crowds() if x['rid'] == RID][0]
    rr = [json.loads(l) for l in open(RING.OUT, encoding='utf-8')]
    rr = [o for o in rr if o['rid'] == RID][0]
    return w, rr


def page_residual():
    t0 = time.time()
    w, rr = load_ring()
    z = np.array(w['z'])
    pg = D.Page(z, width_notes=380, height_extra=230)
    pg.frame()
    meeters = sorted(sum(w['meeters'].values(), []))
    pg.squares({**{i: ORANGE for i in meeters}, 9: BLUE})
    tq = rr['torque_only']['tau']
    tmax = max(abs(v) for v in tq.values())
    for i, tau in tq.items():
        pg.arc(int(i), tau, label='%+.3f' % tau, r=22 + 30 * abs(tau) / tmax)
    per = rr['force_torque']['per_square']
    for i, d in per.items():
        F = np.array(d['F'])
        if np.linalg.norm(F) > 1e-6:
            c = z[3 * int(i):3 * int(i) + 2]
            pg.arrow(c, F, '#d62728', width=2.5, length=0.35 + 0.4 * np.linalg.norm(F))
    pg.line('WHAT THIS IS', size=13, bold=True)
    for t in ['Lemma RING test on the nine-square ring rand_0_0569|t20', '(HELD, side %.4f): tilt floor dropped, contact structure kept,' % z[-1],
              'free FJ LP (walls + the active pair rows, lam >= 0): INFEASIBLE.', '',
              'orange = the 8 corner meeters, blue = holder 9, stipple = rattlers.', '',
              'ORANGE ARCS = the minimal external TORQUES that close the free', 'balance (L1-minimal over all squares): every one is on a meeter,',
              'sign anti-aligning (the wall torques them flat, Lemma W); total', '%.3f (the tilt floor supplied %.3f).' % (rr['torque_only']['objective'], rr['bounded_external_load']),
              '', 'RED ARROWS = the external FORCES of the L1-minimal force+torque', 'load (%.3f): at the centres of the squares that carry them.' % rr['force_torque']['objective'],
              '', 'Reading: the ring is force-balanced but not torque-balanced by', 'walls and meeters alone; what is missing is a torque of sign',
              'chi on four tilted meeters (2, 4, 7, 8) -- a holder pushing', 'each toward alignment.  The PI\'s L3 holds on this witness',
              '(and on all 193: ring219.md).']:
        pg.line(t)
    pg.ty = pg.H + 20
    pg.tx = D.M
    pg.line('Per-meeter torque residual (torque-only LP), tilt (deg), wall force W:', dy=18, size=11, bold=True)
    rows, _ = R.witness_rows(w)
    for i in meeters:
        pg.line('%2d: tau_ext = %+.4f   tilt %5.1f' % (i, tq.get(str(i), 0.0), math.degrees(z[3 * i + 2] % (math.pi / 2))), dy=15, size=11)
    return pg.write(os.path.join(PAGES, 'ring_residual_rand_0_0569_t20.svg'), t0)


def page_mode():
    t0 = time.time()
    w, rr = load_ring()
    rows_all, z = R.witness_rows(w)
    _, A_all, _ = R.system(z, rows_all)
    lam_all, _ = R.feasible(A_all)
    chk = S2.verify_ring(w)
    P4, P7 = np.array(chk['P4']), np.array(chk['P7'])
    F4 = np.array(chk['F4_on_6'])
    idx = S2.variant_rows(rows_all, lam_all, 'core')
    rows = [rows_all[k] for k in idx]
    _, A, Hs = R.system(z, rows)
    groups = MO.group_rows(rows)
    m = MO.make_mode(A, Hs, groups, S2.rotation_mode(z, 6, P7, -1.0), [18, 19, 20])
    idx2 = S2.variant_rows(rows_all, lam_all, 'loaded_ext')
    rows2 = [rows_all[k] for k in idx2]
    _, A2, Hs2 = R.system(z, rows2)
    m2 = MO.make_mode(A2, Hs2, MO.group_rows(rows2), S2.rotation_mode(z, 6, P7, -1.0), [18, 19, 20])
    pg = D.Page(z, width_notes=400, height_extra=150)
    pg.frame()
    meeters = sorted(sum(w['meeters'].values(), []))
    pg.squares({**{i: ORANGE for i in meeters}, 6: ('#ffd27f', '#b06a00'), 9: BLUE, 0: RED})
    pg.arrow(P4, F4, '#000', width=3, length=0.6, on_square=6)
    pg.arrow(P7, -F4, '#000', width=3, length=0.6, on_square=6)
    pg.dot(P4, label='P4')
    pg.dot(P7, label='P7')
    # exaggerated rotation of 6 about P7 by -0.05 rad (dashed outline)
    ang = -0.05
    c6 = z[18:20]
    Rm = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
    verts = [P7 + Rm @ (v - P7) for v in pg.verts(6)]
    pg.outline(verts, label='6 rotated -0.05 rad about P7')
    pg.arc(6, -1.0, col='#d62728', label='cw about P7', r=26)
    pg.line('WHAT THIS IS', size=13, bold=True)
    cw = chk['rot_1mrad_cw']
    for t in ['Addendum 2b: the STRUT MODE of square 6 on the ring', 'rand_0_0569|t20 (side %.4f).' % z[-1], '',
              'Square 6 (dark orange) carries exactly two loads: from 4 at P4', 'and from 7 at P7 (black arrows, equal and opposite, collinear:',
              'moment of F4 about P7 = %.1e); its floor row is active but' % chk['moment_of_F4_about_P7'], 'UNLOADED (lam = %.1f).' % chk['floor_lam_6'], '',
              'Rotating 6 about P7 clockwise by 1 mrad (dashed: x50):', '  floor gap  %+.2e  (opens, rate %.3f per rad)' % (cw['floor_gap'], cw['floor_gap'] / 1e-3),
              '  gap to 7   %+.2e  (holds: quadratic)' % cw['gap_to_7'], '  gap to 4   %+.2e  (closes at SECOND order only)' % cw['gap_to_4'],
              '  gap to 0   %+.2e  (the rattler 0, red, is hit at FIRST order)' % cw['gap_to_0'], '',
              'Lemma STRUT: a two-force strut has the rotation about either', 'contact as a first-order zero mode of the loaded structure.', '',
              'Second order (Theorem SO, wall_torque.md s.5), loaded core', '(rattler rows dropped): v2 = max over the multiplier polytope of',
              'y^T Hess(L) y = %+.4f > 0: the side INCREASES at second order' % (m['v2'] if m else float('nan')),
              'along the mode -- the ring is NOT a saddle here.', '',
              'With the rattler rows kept (11 squares) the mode is BLOCKED:', 'rattler 0 is caged by 4, 5 and 6 (edge-edge contacts) and cannot',
              'yield at first order (completion LP infeasible: %s).' % ('blocked' if m2 is None else 'free'), '',
              'The dashed outline penetrates 4 by %.1e and 0 by %.1e at' % (0.5 * 0.05 ** 2 * cw['gap_to_4'] / 0.5e-6, 0.05 * cw['gap_to_0'] / 1e-3),
              '0.05 rad: an annotation of the first-order mode, not a packing.']:
        pg.line(t, dy=15, size=11)
    return pg.write(os.path.join(PAGES, 'ring_mode_rand_0_0569_t20.svg'), t0)


def page_best_attempt():
    t0 = time.time()
    path = os.path.join(RING.ATT, 'results', 'holder219.jsonl')
    if not os.path.exists(path):
        return None
    best = None
    for l in open(path, encoding='utf-8'):
        o = json.loads(l)
        d = o.get('drain_crowd')
        if d and d['min_pair_gap'] > -1e-6 and d['min_wall_gap'] > -1e-6 and d['n2'] == 4:
            if best is None or d['crowd_lam_sum'] < best[1]['crowd_lam_sum']:
                best = (o, d)
    if best is None:
        return None
    o, d = best
    z = np.array(d['z'])
    w = [x for x in RING.four_crowds() if x['wid'] == o['wid']][0]
    desq = {cn: [int(i) for i in w['designated'][cn]] for cn in G.CORNER_NAMES} if w.get('designated') else C.designate_fixed(z)
    delta = w.get('crowd_delta') or 0.02
    labels, Jc = C.active_crowd_fixed(z, desq, delta)
    T = ST.analyse(z, extra_active=(labels, Jc))
    pg = D.Page(z, width_notes=380, height_extra=120)
    pg.frame()
    meeters = sorted(sum(d['meeters'].values(), []))
    holder = o.get('best_pose', {}).get('holder')
    pg.squares({**{i: ORANGE for i in meeters}, **({holder: BLUE} if holder is not None else {})})
    lam_max = max(a['lam'] for a in T.get('arrows', [{'lam': 1}]))
    for a in T.get('arrows', []):
        if a['lam'] < 1e-6:
            continue
        col = {'wall': '#1f77b4', 'edge': '#000', 'crowd': '#d62728'}[a['kind']]
        pg.arrow(a['p'], a['f'], col, width=1.2 + 3 * a['lam'] / lam_max, length=0.15 + 0.5 * a['lam'] / lam_max, on_square=a['i'])
    pg.line('WHAT THIS IS', size=13, bold=True)
    for t in ['The best 11-square attempt at a balanced four-crowd:', 'witness %s (%s), one square (blue, %s) placed as a' % (o['wid'], o['cls'], holder),
              'holder at the best pose, then A217\'s optimiser with the four', 'corner crowds FORCED (crowd rows, delta %.2f); side %.4f.' % (delta, z[-1]), '',
              'blue arrows = wall forces, black = square-square forces,', 'RED = the crowd rows\' external pulls still needed:',
              'sum of crowd multipliers %.3f (free FJ residual %.2e).' % (d['crowd_lam_sum'], d['fj_res_free']),
              'No 11-square four-crowd balances without them (ring219.md).', '',
              'The free run from the same start drains to side %.4f' % o.get('drain_free', {}).get('s', float('nan')),
              'with %d doubly-met open corners.' % o.get('drain_free', {}).get('n2', -1)]:
        pg.line(t, dy=15, size=11)
    return pg.write(os.path.join(PAGES, 'best_attempt_%s.svg' % o['wid']), t0)


if __name__ == '__main__':
    for f in (page_residual, page_mode, page_best_attempt):
        print(f.__name__, '->', f())
