#!/usr/bin/env python
"""Does A51-NEW-0 drain anywhere known?

A37's own attractor stress test (`a37_drain.deep_check`: re-descent from the
point plus 8 random restarts at each of four amplitudes, penalty continuation
+ polish + exact-feasibility repair).  If something deeper turns up it was
reached by CROSSING a barrier, so it is recorded as `deeper_basin`, never as a
correction -- the A37 convention.  Any deeper landing is rematched against the
atlas + A04 catalogue with `same_family`.

Also runs the strictly-monotone always-feasible `local_descent` from the point,
which is the honest drain: if that moves, the point is not an attractor.

Writes atlas_ext/drain_check.json.  [NUM] float64 -- taxonomy, no certificate.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ATT, 'A37-cp-atlas', 'code'))

import a37_pipeline as P                                    # noqa: E402
import a37_drain as D                                       # noqa: E402

HITS = json.load(open(os.path.join(HERE, 'hits_3.8853914.json')))
z = [float(v) for v in HITS[0]['z']]
x, _, s0 = D.repair(D.z_to_a04(z))
print('start s = %.16f' % s0)

out = {'s_start': s0, 'n_landings_in_cluster': len(HITS)}

# ---- 1. strictly monotone feasible descent (the honest drain)
xl = D.local_descent(x)
if isinstance(xl, tuple):
    xl = xl[0]
_, _, s_loc = D.repair(xl)
out['local_descent'] = {'s_end': s_loc, 'gain': s0 - s_loc,
                        'moved': bool(s_loc < s0 - 1e-12)}
print('local_descent (monotone, always feasible): s %.16f -> %.16f (moved %s)'
      % (s0, s_loc, out['local_descent']['moved']))

# ---- 2. deep check: barrier-crossing stress
dc = D.deep_check(z, s0)
out['deep_check'] = {k: v for k, v in dc.items() if k != 'deep_z'}
print('deep_check: s %.16f -> %.16f by %s (improved %s)'
      % (s0, dc['s_deep'], dc['by'], dc['improved']))

# ---- 3. rematch whatever we ended at
refs = []
atlas = json.load(open(os.path.join(ATT, 'A37-cp-atlas', 'results',
                                    'atlas_final.json')))
for e in atlas['entries']:
    cp = os.path.join(ATT, e['cert_path'])
    if not os.path.exists(cp):
        continue
    zc = json.load(open(cp)).get('z_center')
    if zc:
        zz = [float(P.Fraction(v)) for v in zc]
        refs.append(('atlas:%s' % e['family_id'], zz))
for fidx, fam in P.filtered_families():
    zz, _, _ = P.load_family(fidx)
    refs.append(('A04-cat[%d]' % fidx, [float(v) for v in zz]))

targets = [('self', z, s0), ('local_descent', D.a04_to_z(xl), s_loc)]
if dc.get('deep_z'):
    targets.append(('deep', dc['deep_z'], dc['s_deep']))
out['rematch'] = {}
for tag, zt, st in targets:
    hit = None
    near = []
    for name, zz in refs:
        ok, why, ds, da, g = D.same_family(zt, st, zz, zz[P.S_IDX])
        near.append((ds, g[0], name, why))
        if ok and hit is None:
            hit = {'ref': name, 'why': why}
    near.sort()
    out['rematch'][tag] = {'s': st, 'match': hit,
                           'nearest': [{'ref': n, 'ds': d, 'geom': gg}
                                       for d, gg, n, _ in near[:3]]}
    print('  rematch %-14s s %.12f -> %s (nearest %s ds %.2e)'
          % (tag, st, hit['ref'] if hit else 'NO KNOWN FAMILY',
             near[0][2], near[0][0]))

out['verdict'] = (
    'ATTRACTOR: the strictly-monotone feasible descent does not move and the '
    'barrier-crossing stress finds nothing deeper'
    if not out['local_descent']['moved'] and not dc['improved'] else
    ('drains/escapes: local %s, deep %s'
     % (out['local_descent']['moved'], dc['by'])))
print('=> %s' % out['verdict'])
with open(os.path.join(HERE, 'drain_check.json'), 'w') as f:
    json.dump(out, f, indent=1)
