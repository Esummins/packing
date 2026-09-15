"""A217 checks quoted in torque217.md: (a) interior tilted squares get holder torques of both signs;
(b) the crowd-torque exceptions; (c) holder-vs-wall sign counts at crowd-forced meeters (final data)."""
import json, os, sys, math, collections, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom217 as G, stress217 as S, crowd217 as C
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
W = [json.loads(l) for l in open(os.path.join(RES, 'witnesses217.jsonl'))]
T = {json.loads(l)['wid']: json.loads(l) for l in open(os.path.join(RES, 'torque217.jsonl'))}
# (a)
both = one = none = 0
for w in W:
    if w['cls'] not in ('SETTLED', 'K0FREE', 'BOXK0'): continue
    z = np.array(w['z']); a = S.analyse(z)
    if a['fj'] == 'INFEASIBLE': continue
    for p in a['squares']:
        if p['W'] > 1e-9 or not p['tilted']: continue
        sg = set(np.sign(t) for _, t in p['contacts'] if abs(t) > 1e-9)
        if len(sg) == 2: both += 1
        elif len(sg) == 1: one += 1
        else: none += 1
print('(a) interior tilted loaded-by-contacts squares at genuine FJ points: holder torques of both signs %d, one sign %d, all zero %d' % (both, one, none))
# (b), (c)
exc = []; hold = collections.Counter(); n_ok = n_bad = 0
for w in W:
    if w['cls'] != 'CROWD': continue
    t = T[w['wid']]
    if 'arrows' not in t: continue
    for a in [a for a in t['arrows'] if a['kind'] == 'crowd']:
        e = t['corners'][a['corner']]; m = [mm for mm in e['members'] if mm['i'] == a['i']][0]
        if m['chi'] == 0: continue
        tb = m['tau_bound_frame']
        if tb * m['chi'] > 0: n_ok += 1
        else:
            n_bad += 1; exc.append((w['wid'], a['corner'], a['i'], m['walls'], round(m['tilt_frame_deg'], 2), round(a['lam'], 4), round(tb, 5)))
        h = m['tau_hold_frame']
        hold['hold*chi=%+d' % (1 if h * m['chi'] > 1e-9 else (-1 if h * m['chi'] < -1e-9 else 0))] += 1
print('(b) crowd torque sign == chi: %d, != chi: %d; exceptions (wid, corner, sq, walls, tilt_frame, lam, tau):' % (n_ok, n_bad))
for x in exc: print('    ', x)
print('(c) holder torque sign vs chi at crowd-forced tilted meeters:', dict(hold))
