"""A217 invariant hunt over results/torque217.jsonl: class-wise ranges of the candidate quantities."""
import json, os, sys, math, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..', 'results')
T = [json.loads(l) for l in open(os.path.join(RES, 'torque217.jsonl'))]
W = {json.loads(l)['wid']: json.loads(l) for l in open(os.path.join(RES, 'witnesses217.jsonl'))}
def rng(vals):
    vals = [v for v in vals if v is not None and not (isinstance(v, float) and math.isnan(v))]
    return ('n=%d min %+.3e max %+.3e' % (len(vals), min(vals), max(vals))) if vals else 'n=0'
by = collections.defaultdict(list)
for t in T:
    by[t['cls']].append(t)
print('== identities (all witnesses): total wall torque about centre, tau_wall = W(sin-cos)/2 on tilted squares, equilibrium closure')
for cls, L in by.items():
    ok = [t for t in L if 'error' not in t and t['fj'] != 'INFEASIBLE']
    print('%-8s %3d/%3d FJ-feasible  |tot wall torque| %s  pred_err %s  eq_torque %s  eq_force %s  lam0=0: %d' % (
        cls, len(ok), len(L), rng([abs(t['total_wall_torque']) for t in ok]), rng([t['pred_err'] for t in ok]),
        rng([t['max_eq_torque'] for t in ok]), rng([t['max_eq_force'] for t in ok]), sum(1 for t in ok if t['lam0'] == 0)))
print('\n== per-corner signed torque T_c (corner frame) at UNSETTLED corners, by number of meeters; LP range over the polytope')
for cls, L in by.items():
    for nm in (1, 2, 3):
        Ts, lo, hi, chi_sum = [], [], [], []
        for t in L:
            if 'corners' not in t: continue
            for cn, e in t['corners'].items():
                if e['settled'] is not None or len(e['meeters']) != nm: continue
                Ts.append(e['T']); lo.append(e['T_range'][0]); hi.append(e['T_range'][1])
                chi_sum.append(sum(m['chi'] * m['tau_wall_frame'] for m in e['members']))
        if Ts:
            print('%-8s meeters=%d  T_c %s   T_min %s   T_max %s   sum chi*tau_wall %s' % (cls, nm, rng(Ts), rng(lo), rng(hi), rng(chi_sum)))
print('\n== per meeter (unsettled corners): tilted loaded meeters: chi vs sign of holder torque (frame)')
for cls, L in by.items():
    agree = disagree = upright_loaded = 0
    for t in L:
        if 'corners' not in t: continue
        for cn, e in t['corners'].items():
            if e['settled'] is not None: continue
            for m in e['members']:
                if m['W'] <= 1e-9: continue
                if m['chi'] == 0: upright_loaded += 1; continue
                h = m['tau_hold_frame'] + m['tau_bound_frame']
                if h * m['chi'] > 0: agree += 1
                else: disagree += 1
    print('%-8s tilted loaded meeters: holder torque sign == chi: %d, != chi: %d; upright loaded meeters %d' % (cls, agree, disagree, upright_loaded))
print('\n== CROWD witnesses: where the crowd force is needed')
cnt = collections.Counter(); mags = []
for t in by.get('CROWD', []):
    if 'arrows' not in t: continue
    w = W[t['wid']]
    cr = [a for a in t['arrows'] if a['kind'] == 'crowd']
    corners = sorted(set(a['corner'] for a in cr))
    cnt[len(corners)] += 1
    for a in cr:
        cn = a['corner']; e = t['corners'][cn]
        m = [mm for mm in e['members'] if mm['i'] == a['i']]
        walls = m[0]['walls'] if m else '?'
        mags.append((round(a['lam'], 4), cn, a['i'], walls, round(m[0]['tilt_frame_deg'], 1) if m else None))
print('number of corners with an active crowd force per witness:', dict(cnt))
print('crowd forces (lam, corner, square, walls touched, tilt in frame) sample:', sorted(mags, reverse=True)[:12])
print('crowd force on a square touching NO wall:', sum(1 for m in mags if m[3] == []), 'of', len(mags))
print('\n== doubly-met unsettled corners: are both meeters wall-loaded? (cls: both / one / none)')
for cls, L in by.items():
    c = collections.Counter()
    for t in L:
        if 'corners' not in t: continue
        for cn, e in t['corners'].items():
            if e['settled'] is not None or len(e['meeters']) < 2: continue
            nl = sum(1 for m in e['members'] if m['W'] > 1e-9)
            c[nl] += 1
    print('%-8s %s' % (cls, dict(c)))
