#!/usr/bin/env python
"""Dedupe probe for the A51 side-find attractor at s = 3.8853914.

(1) confirms the 30 landings are ONE family under A37's own `same_family`
    (D4 x relabel x translation + s key);
(2) checks it against every entry of A37's atlas_final.json and every A04
    catalogue family below 3.95.
Writes atlas_ext/dedupe.json.  No A37 file is written.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ATT, 'A37-cp-atlas', 'code'))

import a37_pipeline as P                                    # noqa: E402
import a37_drain as D                                       # noqa: E402

S_IDX = P.S_IDX
hits = json.load(open(os.path.join(HERE, 'hits_3.8853914.json')))
Z = [[float(v) for v in h['z']] for h in hits]
S = [z[S_IDX] for z in Z]

out = {'n_hits': len(hits), 's_min': min(S), 's_max': max(S)}

# ---- (1) internal consistency
worst = None
for k in range(1, len(Z)):
    ok, why, ds, da, g = D.same_family(Z[0], S[0], Z[k], S[k])
    if not ok:
        print('  HIT %d does NOT match hit 0: %s' % (k, why))
    if worst is None or g[0] > worst[0]:
        worst = (g[0], k, g[1], da, ds)
nmatch = sum(1 for k in range(1, len(Z))
             if D.same_family(Z[0], S[0], Z[k], S[k])[0])
print('(1) internal: %d/%d landings match landing 0 under same_family'
      % (nmatch + 1, len(Z)))
print('    worst geometric distance %.3e (hit %d, %d/11 aligned, tilt %.2e '
      'deg, ds %.2e)' % worst)
out['internal'] = {'matched': nmatch + 1, 'of': len(Z),
                   'worst_geom': worst[0], 'worst_aligned': worst[2],
                   'worst_tilt_deg': worst[3], 'worst_ds': worst[4]}

# ---- (2) against the atlas
atlas = json.load(open(os.path.join(ATT, 'A37-cp-atlas', 'results',
                                    'atlas_final.json')))
cands = []
for e in atlas['entries']:
    # the REFINED centre lives in the certificate, not in the atlas entry
    cp = os.path.join(ATT, e['cert_path'])
    if not os.path.exists(cp):
        continue
    zc = json.load(open(cp)).get('z_center')
    if zc is None:
        continue
    zz = [float(P.Fraction(v)) if isinstance(v, str) else float(v)
          for v in zc]
    cands.append(('atlas:%s' % e['family_id'], zz, zz[S_IDX], e.get('class')))
for j, nf in enumerate(atlas['drain']['new_families']):
    zz = [float(P.Fraction(v)) if isinstance(v, str) else float(v)
          for v in nf['z']]
    cands.append(('drain:%s' % nf['id'], zz, zz[S_IDX], 'NEW'))
sub = P.filtered_families()
for fidx, fam in sub:
    zz, _, _ = P.load_family(fidx)
    zz = [float(v) for v in zz]
    cands.append(('A04-cat[%d]' % fidx, zz, zz[S_IDX], 'catalogue'))

res = []
for name, zz, sc, cl in cands:
    ok, why, ds, da, g = D.same_family(Z[0], S[0], zz, sc)
    res.append({'ref': name, 'class': cl, 'match': bool(ok), 'ds': ds,
                'tilt_deg': da, 'geom': g[0], 'aligned': g[1], 'why': why})
res.sort(key=lambda r: r['ds'])
matches = [r for r in res if r['match']]
print('\n(2) vs %d references (atlas entries + drain new families + A04 <3.95)'
      % len(res))
print('    MATCHES: %d' % len(matches))
for r in res[:5]:
    print('    %-16s %-12s ds %.3e  tilt %.3e deg  geom %.3e (%d/11)'
          % (r['ref'], r['class'], r['ds'], r['tilt_deg'], r['geom'],
             r['aligned']))
out['n_references'] = len(res)
out['references'] = [r['ref'] for r in res]
out['nearest'] = res[:5]
out['n_matches'] = len(matches)
out['matches'] = matches
out['verdict'] = ('DISTINCT: no atlas/catalogue reference matches'
                  if not matches else 'MERGES WITH %s' % matches[0]['ref'])
print('\n=> %s' % out['verdict'])
with open(os.path.join(HERE, 'dedupe.json'), 'w') as f:
    json.dump(out, f, indent=1)
