"""Scan all results for s below the exact octic root; exact-verify anything that qualifies."""
import json, glob, sys
import numpy as np
from verify_exact import verify_claim
import mpmath as mp

mp.mp.dps = 30
ROOT = float(mp.findroot(lambda s: mp.polyval([1, -20, 178, -842, 1923, -496, -6754, 12420, -6865], s), 3.877))
print('exact octic root (Trump/G-R record):', repr(ROOT))
recs = []
for f in glob.glob('res_*.jsonl'):
    for l in open(f):
        try:
            recs.append(json.loads(l))
        except Exception:
            pass
recs.sort(key=lambda r: r['s'])
print('n records', len(recs), 'best strict s', recs[0]['s'], 'diff to root', recs[0]['s'] - ROOT)
below = [r for r in recs if r['s'] < ROOT - 1e-9]
print('records with strict s < root - 1e-9:', len(below))
for r in below[:5]:
    ok, m, msg = verify_claim(np.array(r['x']), r['s'])
    print('  s=%.10f verify=%s margin=%.2e %s' % (r['s'], ok, m, msg))
    if ok:
        json.dump(r, open('CANDIDATE_RECORD.json', 'w'), indent=1)
        print('  !!!! CANDIDATE_RECORD.json written')
# also: rediscoveries of the record (within 1e-6) and exact verification of the best one
hits = [r for r in recs if abs(r['s'] - ROOT) < 1e-6]
print('rediscoveries of the record within 1e-6:', len(hits))
if hits:
    r = hits[0]
    ok, m, msg = verify_claim(np.array(r['x']), r['s'] + 1e-9)
    print('exact verification of best rediscovery at s_claim = s+1e-9:', ok, m, msg)
