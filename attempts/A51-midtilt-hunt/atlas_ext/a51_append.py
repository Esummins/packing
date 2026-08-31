#!/usr/bin/env python
"""Append the A51-NEW-0 entry to A37's atlas_final.json.

Additive only: existing entries are byte-identical afterwards (asserted), the
existing meta keys are untouched, and one new meta key `extensions` records
the provenance of the appended entry.  A timestamped backup of the atlas is
written next to it before anything is changed.
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..', '..'))
ATLAS = os.path.join(ATT, 'A37-cp-atlas', 'results', 'atlas_final.json')

work = json.load(open(os.path.join(HERE, 'atlas_a51.json')))
entry = dict(work['entries'][0])
stageA = entry.pop('stage_a')
dedupe = json.load(open(os.path.join(HERE, 'dedupe.json')))
drain = None
dp = os.path.join(HERE, 'drain_check.json')
if os.path.exists(dp):
    drain = json.load(open(dp))

entry['family_id'] = 'A51-NEW-0'
entry['catalogue_index'] = -1
entry['discovered_by'] = (
    'A51 mid-tilt flush-free hunt (attempts/A51-midtilt-hunt/results/'
    'a51_report.md section 8): 30 independent free-descent landings (26 census '
    '+ 4 negative-control) converge here; absent from the A04 catalogue, from '
    'atlas_final.json and from the A37 drain new-family list.')
entry['dedupe_probe'] = {
    'producer': 'attempts/A51-midtilt-hunt/atlas_ext/a51_dedupe.py',
    'metric': "a37_drain.same_family (D4 x relabel x translation, s_tol 1e-8, "
              "g_tol 1e-6)",
    'internal': dedupe['internal'],
    'n_references': dedupe['n_references'],
    'n_matches': dedupe['n_matches'],
    'nearest': dedupe['nearest'][:3],
    'verdict': dedupe['verdict'],
}
entry['cp_audit'] = stageA
if drain is not None:
    entry['attractor_stress'] = {
        'producer': 'attempts/A51-midtilt-hunt/atlas_ext/a51_drain_check.py',
        'local_descent': drain['local_descent'],
        'deep_check': drain['deep_check'],
        'rematch': drain['rematch'],
        'verdict': drain['verdict'],
    }

atlas = json.load(open(ATLAS))
before = json.dumps(atlas['entries'], sort_keys=True)
ids = [e['family_id'] for e in atlas['entries']]
if 'A51-NEW-0' in ids:
    print('A51-NEW-0 already present -- replacing it in place (idempotent)')
    atlas['entries'] = [e for e in atlas['entries']
                        if e['family_id'] != 'A51-NEW-0']
    before = json.dumps(atlas['entries'], sort_keys=True)

bak = ATLAS + '.bak-%s' % time.strftime('%Y%m%dT%H%M%S')
shutil.copy2(ATLAS, bak)
print('backup -> %s' % bak)

atlas['entries'].append(entry)


def key(e):
    k = e['family_id']
    return (0, k, '') if isinstance(k, int) else (1, 0, k)


atlas['entries'].sort(key=key)
after = json.dumps([e for e in atlas['entries']
                    if e['family_id'] != 'A51-NEW-0'], sort_keys=True)
assert after == before, 'EXISTING ENTRIES CHANGED -- aborting'

ext = atlas['meta'].setdefault('extensions', [])
ext.append({
    'entry': 'A51-NEW-0',
    'appended': time.strftime('%Y-%m-%d'),
    'by': 'A51 (computation postdoc), attempts/A51-midtilt-hunt/atlas_ext/',
    'note': 'non-catalogue attractor at s = 3.8853914 found as a side product '
            'of the A51 mid-tilt flush-free hunt; certified by the A37 '
            'pipeline (step 3S soft path) with the standalone A37 re-checker '
            'and all five corruption gates re-run over the new certificate. '
            'The pre-existing entries and meta fields are unchanged; the '
            'meta counts ("10 distinct attractor structures", "4 families '
            'missing") predate this entry and now read one low.',
    'producers': ['attempts/A51-midtilt-hunt/atlas_ext/a51_certify.py',
                  'attempts/A51-midtilt-hunt/atlas_ext/a51_dedupe.py',
                  'attempts/A51-midtilt-hunt/atlas_ext/a51_drain_check.py'],
})

with open(ATLAS, 'w') as f:
    json.dump(atlas, f, indent=1)
print('atlas_final.json: %d entries (was %d)'
      % (len(atlas['entries']), len(atlas['entries']) - 1))
print('  %-12s %-8s h=%s  V@1e-3=%.15f'
      % (entry['family_id'], entry['class'], entry['h_certified'],
         entry['value']['V_soft_at_1e-3']))
