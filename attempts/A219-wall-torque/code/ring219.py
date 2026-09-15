"""A219 Lemma RING test: at every four-crowd witness (A217's 8 HELD + 185 CROWD, n2 = 4) drop the tilt-floor /
crowd rows, keep the contact structure, and ask the free FJ multiplier LP (force + torque balance of every
square by walls + listed contacts, multipliers >= 0) whether a balanced ring exists.  When it does not: the
minimal external load that closes the balance (torques only; forces + torques), per square, and the direction
of the external force on each meeter (toward its wall / along its wall toward the corner / radially outward).
    python ring219.py            -> results/ring219.jsonl (one line per witness), prints a summary
"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rows219 as R                       # noqa: E402
import geom217 as G                       # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
WIT = os.path.join(ATT, '..', 'A217-torque-probe', 'results', 'witnesses217.jsonl')
OUT = os.path.join(ATT, 'results', 'ring219.jsonl')
WALL_IN = {'x=0': (1.0, 0.0), 'y=0': (0.0, 1.0), 'x=s': (-1.0, 0.0), 'y=s': (0.0, -1.0)}
LOAD_TOL = 1e-6


def four_crowds():
    out = []
    for l in open(WIT, encoding='utf-8'):
        w = json.loads(l)
        if w['n2'] == 4 and w['cls'] in ('HELD', 'CROWD'):
            out.append(w)
    return out


def meeter_info(w, z, rows):
    """per meeter: corner, touched corner walls (active wall rows), the three reference directions."""
    cx, cy, th, s = G.unpack(z)
    info = {}
    for cn, ms in w['meeters'].items():
        M, t, det = G.corner_frame(cn, s)
        for i in ms:
            walls = sorted({r['wall'] for r in rows if r['kind'] == 'wall' and r['i'] == i})
            d_wall = [(-np.array(WALL_IN[wl])) for wl in walls]                  # into the wall
            d_along = []
            for wl in walls:
                # frame coordinate that the wall fixes: u for the corner's u-wall, v for its v-wall
                nfr = M @ np.array(WALL_IN[wl])
                a = int(np.argmax(np.abs(nfr)))                                  # 0: u-wall, 1: v-wall
                dfr = np.zeros(2)
                dfr[1 - a] = -1.0                                                # along the wall, toward the corner
                d_along.append(M.T @ dfr)
            rad = np.array([cx[i] - s / 2, cy[i] - s / 2])
            rad = rad / np.linalg.norm(rad)
            info[i] = {'corner': cn, 'walls': walls, 'd_wall': d_wall, 'd_along': d_along, 'd_rad': rad,
                       'tilt_frame_deg': math.degrees((th[i] if det == 1 else -th[i]) % (math.pi / 2))}
    return info


def analyse(w):
    rows_all, z = R.witness_rows(w)
    cx, cy, th, s = G.unpack(z)
    vals, A_all, _ = R.system(z, rows_all)
    lam_b, lam0_b = R.feasible(A_all)                     # the bounded stress (A217's)
    ext_rows = [k for k, r in enumerate(rows_all) if r['kind'] in ('tiltbound', 'crowd')]
    free_idx = [k for k, r in enumerate(rows_all) if r['kind'] in ('wall', 'edge')]
    rows = [rows_all[k] for k in free_idx]
    A = A_all[free_idx]
    out = {'wid': w['wid'], 'cls': w['cls'], 'rid': w['rid'], 's': float(s), 'meeters': w['meeters'],
           'n_rows': {k: sum(r['kind'] == k for r in rows_all) for k in ('wall', 'edge', 'tiltbound', 'crowd')},
           'bounded_lam0': lam0_b,
           'bounded_external_load': float(sum(lam_b[k] for k in ext_rows)) if lam_b is not None else None}
    # (a) free LP on ALL active free rows; (b) on the rows LOADED in the bounded stress only
    lam, lam0 = R.feasible(A)
    out['free_all'] = 'lam0=1' if lam0 == 1.0 else ('self-stress' if lam0 == 0.0 else 'INFEASIBLE')
    if lam_b is not None:
        loaded = [k for k in free_idx if lam_b[k] > LOAD_TOL]
        lamL, lam0L = R.feasible(A_all[loaded]) if loaded else (None, None)
        out['free_loaded'] = 'lam0=1' if lam0L == 1.0 else ('self-stress' if lam0L == 0.0 else 'INFEASIBLE')
        out['n_loaded_free_rows'] = len(loaded)
    # minimal external loads
    tcoords = [3 * i + 2 for i in range(G.N)]
    fcoords = [3 * i + a for i in range(G.N) for a in range(3)]
    mi = meeter_info(w, z, rows)
    r_t = R.min_external(A, tcoords)
    out['torque_only'] = None
    if r_t is not None:
        lamT, mu, obj = r_t
        out['torque_only'] = {'objective': obj, 'tau': {i: float(mu[i]) for i in range(G.N) if abs(mu[i]) > 1e-7}}
    r_f = R.min_external(A, fcoords)
    lamF, muF, objF = r_f
    per = {}
    for i in range(G.N):
        F = muF[3 * i:3 * i + 2]
        tau = float(muF[3 * i + 2])
        if np.linalg.norm(F) < 1e-7 and abs(tau) < 1e-7:
            continue
        d = {'F': [float(F[0]), float(F[1])], 'tau': tau, 'meeter': i in mi}
        if i in mi and np.linalg.norm(F) > 1e-7:
            u = F / np.linalg.norm(F)
            m = mi[i]
            d['corner'] = m['corner']
            d['walls'] = m['walls']
            d['cos_toward_wall'] = max([float(u @ v) for v in m['d_wall']], default=None)
            d['cos_along_wall_to_corner'] = max([float(u @ v) for v in m['d_along']], default=None)
            d['cos_radial_out'] = float(u @ m['d_rad'])
            cands = {'toward_wall': d['cos_toward_wall'], 'along_wall_to_corner': d['cos_along_wall_to_corner'],
                     'radial_out': d['cos_radial_out']}
            cands = {k: v for k, v in cands.items() if v is not None}
            d['direction'] = max(cands, key=cands.get)
        per[i] = d
    out['force_torque'] = {'objective': objF, 'per_square': per,
                           'n_meeters_loaded_externally': sum(1 for i in per if per[i]['meeter']),
                           'n_non_meeters_loaded_externally': sum(1 for i in per if not per[i]['meeter'])}
    # wall-torque sign check on the meeters: external torque vs the wall torque (Lemma W: aligning)
    signs = []
    if r_t is not None:
        _, A_w, _ = R.system(z, rows)
        q = G.corners(z)
        for i in mi:
            tw = 0.0
            for k, r in enumerate(rows):
                if r['kind'] == 'wall' and r['i'] == i and lamT[k] > 1e-9:
                    p = q[i, r['corner']]
                    f = lamT[k] * np.array(WALL_IN[r['wall']])
                    tw += (p[0] - cx[i]) * f[1] - (p[1] - cy[i]) * f[0]
            tau = out['torque_only']['tau'].get(i, 0.0)
            if abs(tau) > 1e-7 and abs(tw) > 1e-9:
                signs.append(int(np.sign(tau * tw)))
    out['ext_torque_vs_wall_torque_signs'] = signs
    return out


def main():
    t0 = time.time()
    ws = four_crowds()
    res = []
    with open(OUT, 'w', encoding='utf-8') as f:
        for w in ws:
            o = analyse(w)
            o['t_s'] = round(time.time() - t0, 2)
            res.append(o)
            f.write(json.dumps(o) + '\n')
    print('%d witnesses in %.1f s' % (len(res), time.time() - t0))
    for cls in ('HELD', 'CROWD'):
        rs = [o for o in res if o['cls'] == cls]
        fa = [o['free_all'] for o in rs]
        print(cls, len(rs), 'free LP on all active rows:', {k: fa.count(k) for k in set(fa)},
              '| loaded rows only:', {k: [o.get('free_loaded') for o in rs].count(k) for k in set(o.get('free_loaded') for o in rs)})
        tq = [o for o in rs if o['torque_only'] is not None]
        print('   torque-only external closes the balance:', len(tq), 'of', len(rs),
              '| objective min/med/max', np.round(np.percentile([o['torque_only']['objective'] for o in tq], [0, 50, 100]), 4) if tq else '-')
        dirs = [d['direction'] for o in rs for d in o['force_torque']['per_square'].values() if d.get('direction')]
        print('   force+torque objective min/med/max', np.round(np.percentile([o['force_torque']['objective'] for o in rs], [0, 50, 100]), 4),
              '| external force directions on meeters:', {k: dirs.count(k) for k in set(dirs)},
              '| non-meeters loaded externally:', sum(o['force_torque']['n_non_meeters_loaded_externally'] for o in rs))
        sg = [x for o in rs for x in o['ext_torque_vs_wall_torque_signs']]
        print('   sign(ext torque * wall torque): -1 (anti-aligning) %d, +1 %d' % (sg.count(-1), sg.count(1)))


if __name__ == '__main__':
    main()
