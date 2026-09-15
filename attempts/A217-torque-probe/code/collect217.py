"""A217 collector: dedupe the search runs into results/witnesses217.jsonl (D4-quotiented), run the
Fritz-John stress at every witness (results/torque217.jsonl), tabulate the candidate invariants.
    python collect217.py [--cap 60]
Classes: K0FREE (free run, no slot square, FJ), SETTLED (free run, >= 1 slot square, FJ), HELD (tilt-boxed,
bound active), BOXK0 (tilt-boxed, bound inactive, FJ), CROWD0 (4 doubly-met corners, crowd rows inactive =
a genuine FJ point with four 2-crowds), CROWD (4 doubly-met corners held by crowd forces).
"""
import argparse
import glob
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom217 as G
import opt217 as O
import crowd217 as C
import stress217 as S

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
RES = os.path.join(ATT, 'results')


def jdefault(o):
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(repr(o))


def classify(r):
    if r.get('fj_res', 1) >= 1e-8 or r.get('min_pair_gap', -1) < -1e-6 or r.get('min_wall_gap', -1) < -1e-6:
        return None
    if 'crowd_delta' in r:
        n2 = sum(1 for c, m in r['meeters'].items() if len(m) >= 2)
        if n2 < 4 or not r['k0']:
            return None
        return 'CROWD0' if r['n_crowd_active'] == 0 else 'CROWD'
    if r['tmin_deg'] is None:
        return 'K0FREE' if r['k0'] else 'SETTLED'
    if not r['k0']:
        return None
    return 'HELD' if r['n_tiltbound_active'] > 0 else 'BOXK0'


def key_of(r):
    sig = r['sig']
    return (round(r['s'], 5), tuple(tuple(round(v, 2) for v in row) for row in sig))


def load_witnesses():
    seen = {}
    for f in sorted(glob.glob(os.path.join(RES, 'search217_*.jsonl'))):
        for line in open(f):
            try:
                r = json.loads(line)
            except Exception:
                continue
            cls = classify(r)
            if cls is None:
                continue
            k = (cls,) + key_of(r)
            if k in seen:
                continue
            r['cls'] = cls
            r['n2'] = sum(1 for c, m in r['meeters'].items() if r['settled'][c] is None and len(m) >= 2)
            seen[k] = r
    return list(seen.values())


def stress_record(r):
    z = np.array(r['z'])
    tmin = None if r.get('tmin_deg') is None else math.radians(r['tmin_deg'])
    extra = None
    if 'crowd_delta' in r:
        desq = r['designated']
        extra = C.active_crowd_fixed(z, desq, r['crowd_delta'])
    a = S.analyse(z, tmin=tmin, extra_active=extra)
    out = {'wid': r['wid'], 'cls': r['cls'], 's': r['s'], 'rid': r['rid'], 'fj': a['fj'], 'lam0': a['lam0'],
           'n_rows': a['n_rows'], 'fj_res': a['fj_res']}
    if a['fj'] == 'INFEASIBLE':
        return out, a
    out['total_wall_torque'] = a['total_wall_torque_about_centre']
    out['wall_pressure'] = {k: float(v) for k, v in a['wall_pressure'].items()}
    out['wall_moment'] = {k: float(v) for k, v in a['wall_moment'].items()}
    out['max_eq_torque'] = max(abs(p['eq_torque']) for p in a['squares'])
    out['max_eq_force'] = max(p['eq_force'] for p in a['squares'])
    out['pred_err'] = max(abs(p['tau_wall'] - p['tau_wall_pred']) for p in a['squares'] if p['tau_wall_pred'] is not None) if any(p['tau_wall_pred'] is not None for p in a['squares']) else 0.0
    out['squares'] = [{k: (float(v) if isinstance(v, (float, np.floating)) else v) for k, v in p.items() if k != 'contacts'} for p in a['squares']]
    cs = {}
    for cn, e in a['corners'].items():
        cs[cn] = {'settled': e['settled'], 'meeters': e['meeters'], 'det': e['det'],
                  'T': float(e['T_corner']), 'T_range': e['T_corner_range'],
                  'members': [{k: (float(v) if isinstance(v, (float, np.floating)) else v) for k, v in m.items()} for m in e['members']]}
    out['corners'] = cs
    out['arrows'] = a['arrows']
    return out, a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cap', type=int, default=60)
    a = ap.parse_args()
    ws = load_witnesses()
    by = {}
    for r in ws:
        by.setdefault(r['cls'], []).append(r)
    chosen = []
    for cls, lst in by.items():
        lst.sort(key=lambda r: r['s'])
        # keep the lowest sides and, for the k0 classes, everything with many doubly-met corners
        keep = lst[:a.cap] + [r for r in lst[a.cap:] if r.get('n2', 0) >= 3]
        chosen += keep
        print('%-8s distinct %4d kept %4d  sides %.5f .. %.5f  n2 counts %s' % (
            cls, len(lst), len(keep), lst[0]['s'], lst[-1]['s'],
            {k: sum(1 for r in lst if r['n2'] == k) for k in range(5)}), flush=True)
    chosen.sort(key=lambda r: (r['cls'], r['s']))
    with open(os.path.join(RES, 'witnesses217.jsonl'), 'w') as fw, open(os.path.join(RES, 'torque217.jsonl'), 'w') as ft:
        for k, r in enumerate(chosen):
            r['wid'] = 'w%03d_%s' % (k, r['cls'].lower())
            rec = {kk: r[kk] for kk in ('wid', 'cls', 'rid', 's', 'z', 'fj_res', 'n_rows', 'tilts_deg', 'settled', 'meeters', 'n2', 'k0')}
            rec['tmin_deg'] = r.get('tmin_deg')
            rec['crowd_delta'] = r.get('crowd_delta')
            rec['designated'] = r.get('designated')
            rec['n_tiltbound_active'] = r.get('n_tiltbound_active', 0)
            rec['n_crowd_active'] = r.get('n_crowd_active', 0)
            fw.write(json.dumps(rec, default=jdefault) + '\n')
            try:
                t, _ = stress_record(r)
            except Exception as e:                  # noqa
                t = {'wid': r['wid'], 'cls': r['cls'], 's': r['s'], 'error': repr(e)}
            ft.write(json.dumps(t, default=jdefault) + '\n')
    print('wrote', len(chosen), 'witnesses', flush=True)


if __name__ == '__main__':
    main()
