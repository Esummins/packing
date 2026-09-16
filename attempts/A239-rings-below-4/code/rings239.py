"""A239 rings strictly below side 4 and the gear lemma: build the rings (A226's crowd rings at S = 3.90 / 3.99; the
window ring in wall-to-wall CONTACT at the tilt theta* where the reach closes (k = 0); the JUTTING 3 2 3 2 ring at
S = 3.95), run the free FJ multiplier LP with the contact structure fixed (stress239.analyse: feasibility, the
minimal external load = the deficit rows, PUSH axes, Lemma W torques, the loaded component), the pocket (A222's
greedy placer capacity, A237's PIERCE(1) at the centre, which members the one interior square could touch), and
the reach table of s.1.  Every step timed; one jsonl row per ring.
    python rings239.py   -> results/rings239.jsonl, results/reach239.jsonl
"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom239 as GM                                                       # noqa: E402
import stress239 as SS                                                     # noqa: E402
import band236 as BD                                                       # noqa: E402
import geom237 as G237                                                     # noqa: E402

GM.set_priority()
ATT = os.path.abspath(os.path.join(HERE, '..'))
OUT = os.path.join(ATT, 'results', 'rings239.jsonl')
REACH = os.path.join(ATT, 'results', 'reach239.jsonl')


def theta_contact(S, margin=0.02, eta=0.0):
    """the tilt at which the least-offset window ring closes its walls (gap = 0): reach(theta, sin theta + margin) =
    S - 2 - eta, by bisection on [0, 89] deg (reach is increasing there for the offsets used)."""
    lo, hi = 0.01, 89.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if GM.reach(mid, math.sin(mid * GM.DEG) + margin) < S - 2 - eta:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def timed(fn, *a, **k):
    t0 = time.time()
    r = fn(*a, **k)
    return r, time.time() - t0


def study(label, poses, S, extra=None):
    t_all = time.time()
    row = {'label': label, 'S': S, 'n': len(poses), 'poses': [list(map(float, p)) for p in poses], 'times': {}}
    (ok, gap, wall), row['times']['check'] = timed(BD.check_packing, poses, S)
    row.update({'packing_ok': bool(ok), 'min_gap': float(gap), 'min_wall': float(wall)})
    res, row['times']['lp'] = timed(SS.analyse, poses, S)
    row.update({'pattern': res['pattern'], 'meeters': res['meeters'], 'n_rows': res['n_rows'], 'rows': res['rows'],
                'free_lp': res['free_lp'], 'push': res['push'], 'torque_only': res['torque_only']})
    if 'lam' in res:
        row.update({'lam': res['lam'], 'arrows': res['arrows'], 'squares': res['squares']})
    row['deficit'], row['loaded_deficit'], row['partner_rows'] = res['deficit'], res['loaded_deficit'], res['partner_rows']
    (cap, cap_poses), row['times']['capacity'] = timed(GM.capacity, poses, S, 3)
    row.update({'capacity_greedy': cap, 'interior': [list(map(float, p)) for p in cap_poses]})
    W, row['times']['waste'] = timed(G237.waste, list(poses), S, 1.0)
    row.update({'pocket_area': W['area'], 'coverable': W['coverable_area'], 'waste': W['waste']})
    p1, row['times']['pierce'] = timed(G237.pierce, list(poses), S, [(S / 2, S / 2)], 1.0, W['free'])
    row['pierce1_centre'] = float(p1)
    need = sorted((res.get('loaded_deficit') or res.get('deficit') or {}).get('per_square', {}).keys())
    tt = {}
    t0 = time.time()
    for i in range(len(poses)):
        tt[i] = GM.touchable(poses, S, i, 2.0)
    row['times']['touchable'] = time.time() - t0
    row['touchable'] = {i: {'can': bool(v[0]), 'dist': v[1], 'tilt': v[2]} for i, v in tt.items()}
    row['deficit_squares'] = need
    if extra:
        row.update(extra)
    row['times']['total'] = time.time() - t_all
    d, ld = row.get('deficit'), row.get('loaded_deficit')
    print('%-22s S %.3f n %2d pattern %s packing %s (gap %.1e wall %.1e) rows %d LP %s deficit %s loaded(rho=0.1) %s '
          'torque-only %s capacity %d pierce1 %.1e touchable %s  %.1fs' % (
              label, S, len(poses), row['pattern'], ok, gap, wall, res['n_rows'], res['free_lp'],
              '%.3f' % d['objective'] if d else '-', '%.3f' % ld['objective'] if ld else '-',
              '%.3f' % res['torque_only']['objective'] if res['torque_only'] else '-',
              cap, p1, [i for i in tt if tt[i][0]], row['times']['total']), flush=True)
    if ld:
        for i, dd in ld['per_square'].items():
            print('     ext on %d: F (%+.3f, %+.3f) %s tau %+.3f %s' % (i, dd['F'][0], dd['F'][1], dd.get('direction', ''), dd['tau'], dd.get('torque', '')))
    return row


def reach_table():
    rows = []
    for th in np.arange(0.5, 89.6, 0.5):
        d0 = math.sin(th * GM.DEG) + 0.02
        rows.append({'theta': float(th), 'w': GM.w_of(th * GM.DEG), 'chord': 1.0 / max(math.cos(th * GM.DEG), math.sin(th * GM.DEG)),
                     'reach_least': GM.reach(th, min(d0, 0.999)), 'reach_deep': GM.reach(th, 0.98),
                     'delta_least': min(d0, 0.999)})
    thr, curves = {}, {}
    for S in (3.88, 3.90, 3.95, 3.99, 4.0, 4.11):
        thr[str(S)] = {'least': GM.theta_star(S), 'deep': GM.theta_star(S, lambda t: 0.98)}
    for S in (3.88, 3.95, 3.99):                     # the contact curve delta(theta): R(theta, delta) = S - 2, its waste
        cur = []
        for th in np.arange(1.0, 44.6, 1.0):
            t = th * GM.DEG
            d = (S - 2 - GM.w_of(t) - math.sin(t) * math.tan(t)) / (1 - math.tan(t))
            if math.sin(t) + 0.02 <= d < 1.0:
                A, B = GM.window_pair(th, d, 0.0)
                Wc = G237.waste([A, B], 6.0, 1.0)
                near = [c for c in G237.components(Wc['uncov']) if c['cx'] < 3.0 and c['cy'] < 3.0]
                cur.append({'theta': float(th), 'delta': float(d), 'waste': float(sum(c['area'] for c in near))})
        curves[str(S)] = cur
    with open(REACH, 'w', encoding='utf-8') as fh:
        fh.write(json.dumps({'thresholds': thr, 'contact_curves': curves}) + '\n')
        for r in rows:
            fh.write(json.dumps(r) + '\n')
    print('reach thresholds theta* (least offset / deep offset 0.98):', thr, flush=True)
    return thr


def main():
    t0 = time.time()
    thr = reach_table()
    rows = []
    # Panels B, C: A226's crowd rings (rattler crowds)
    for S in (3.90, 3.99):
        rows.append(study('ring226_S%.2f_eps0.02' % S, GM.ring226(S, 0.02), S, {'kind': 'ring226', 'eps': 0.02}))
    # the window ring in CONTACT (k = 0) at S = 3.95 and at s-hat: theta* from the reach equation
    for S in (3.877, 3.95):
        th = theta_contact(S)
        R, delta = GM.window_ring(S, th, None, 0.0)
        rows.append(study('contact_S%.3f_th%.2f' % (S, th), R, S, {'kind': 'contact', 'theta': th, 'delta': delta,
                                                                    'reach': GM.reach(th, delta)}))
    # the balanced family ABOVE 4 (torque balance of B needs delta = sin th + cos^3 th; loop gain cot^4 th): a check
    for thb in (45.0, 70.0):
        t = thb * GM.DEG
        d = min(math.sin(t) + math.cos(t) ** 3, 0.999)
        Sb = 2 + GM.reach(thb, d)
        Rb, _ = GM.window_ring(Sb, thb, d, 0.0)
        rows.append(study('balanced_th%.0f_S%.3f' % (thb, Sb), Rb, Sb, {'kind': 'balanced', 'theta': thb, 'delta': d}))
    # Panel D: the jutting 3 2 3 2 rings at S = 3.95
    for th, phi in ((5.0, 45.0), (10.0, 45.0), (15.0, 45.0), (20.0, 45.0), (10.0, 30.0), (10.0, 60.0)):
        R, info = GM.jutting_ring(3.95, th, phi, 0.0)
        info.update({'kind': 'jutting', 'theta': th, 'phi': phi})
        rows.append(study('jut_S3.95_th%.0f_phi%.0f' % (th, phi), R, 3.95, info))
    with open(OUT, 'w', encoding='utf-8') as fh:
        for r in rows:
            fh.write(json.dumps(r) + '\n')
    print('wrote', OUT, 'in %.1f s' % (time.time() - t0))


if __name__ == '__main__':
    main()
