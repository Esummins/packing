"""A37 final atlas merge (lead). Idempotent: rerun after drain.json lands.

Merges atlas.json (pilot: 0,1,4,6) + atlas_batchA.json (2..17) + atlas_batchB.json (18..31,
fam31 superseded by atlas_fam31_ext.json) + drain.json (if present) into atlas_final.json,
applying the lead's decisions:
  - fam 27 reclassified VALLEY-MARGINAL (batch B evidence: critical to 7.3e-8, min free-sign
    multiplier +2.06e-2, descent -1.2e-7; binary equality-LP cannot resolve).
  - stratum merges: {1,2} and {13,14} are single mechanisms (valleys); entries kept, tagged.
  - 3.903x cluster (19..24): six geometrically distinct configs (>=6.7e-2 apart) — explicit
    non-merge note so nobody merges by s-value.
  - taxonomy meta: NOT-CP class describes dynamical role; value certificates sound regardless.
"""
import json, os

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')


def load(name):
    p = os.path.join(R, name)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


def entries(a):
    if a is None:
        return []
    return a['entries'] if isinstance(a, dict) and 'entries' in a else list(a.values()) if isinstance(a, dict) else a


ents = {}
for src in ('atlas.json', 'atlas_batchA.json', 'atlas_batchB.json'):
    for e in entries(load(src)):
        ents[int(e['family_id'])] = e
ext = load('atlas_fam31_ext.json')
if ext:
    for e in entries(ext):
        if int(e['family_id']) == 31:
            e['notes'] = (e.get('notes', '') +
                          ' | lead: h ceiling raised 1/20 -> 1/10 (pipeline --hmax patch); '
                          'h now bound by V >= incumbent (trivial-bound regime).')
            ents[31] = e

# fam 27 reclassification
if 27 in ents:
    e = ents[27]
    e['class_pipeline'] = e.get('class')
    e['class'] = 'VALLEY-MARGINAL'
    e['notes'] = (e.get('notes', '') +
                  ' | lead reclassification per batch B: critical to 7.3e-8, min free-sign '
                  'multiplier +2.06e-2, descent rate only -1.2e-7; the binary equality-LP '
                  'cannot resolve 7e-8 vs 1.4e-2. Genuine attractor. Certificate unaffected '
                  '(value bounds are class-independent).')

# stratum merges
for a, b in ((1, 2), (13, 14)):
    for x, y in ((a, b), (b, a)):
        if x in ents:
            ents[x]['stratum_merge'] = ('single mechanism with family %d (batch A: one '
                                        'valley, 6-dim); counted once in the CP tally' % y)

# NEW families from the drain probe (pipeline run with fidx 1000+j)
newatlas = load('atlas_new.json')
if newatlas:
    for e in entries(newatlas):
        j = int(e['family_id']) - 1000
        e['family_id'] = 'A37-NEW-%d' % j
        e['discovered_by'] = 'A37 drain probe (results/drain.json); absent from A04 catalogue'
        if j == 1:
            e['class_pipeline'] = e.get('class')
            e['class'] = 'VALLEY-MARGINAL'
            e['notes'] = (e.get('notes', '') +
                          ' | lead: pipeline binary equality-LP flags e_s infeasible, but the '
                          'drain deep re-descent (mu-continuation + 32 restarts to 3e-2) found '
                          'NO smaller-s witness; per the residual-scaled policy NOT-CP requires '
                          'a constructive witness, so classified VALLEY-MARGINAL (fam-27 '
                          'pattern).')
        if j == 3:
            e['notes'] = (e.get('notes', '') +
                          ' | shallow attractor: a 1e-2 perturbation escapes to family 6 '
                          '(drain report); certificate unaffected.')
        ents[e['family_id']] = e

drain = load('drain.json')
meta = {
    'attempt': 'A37-cp-atlas',
    'claim_semantics': 'each entry certifies: every feasible 11-square packing configuration z '
                       'with ||z - z_center||_inf <= h_certified has sigma(z) >= V (exact '
                       'rational V; interval-verified certificate in cert_path; standalone '
                       're-checker code/a37_check.py).',
    'taxonomy_note': 'class RIGID/VALLEY/VALLEY-MARGINAL/NOT-CP describes the point\'s '
                     'dynamical role under the compression flow. NOT-CP = local minimum of s '
                     'only at A04\'s fixed lattice angles (descent exists under free rotation; '
                     'constructively witnessed for 12 of them, see drain block). Value '
                     'certificates are sound REGARDLESS of class: sigma >= V on the box needs '
                     'no criticality.',
    'dedupe_key': 's at tol 1e-8 as the primary key + partial geometric alignment as '
                  'corroboration (drain worker): rattlers translate AND rotate freely, so '
                  'pure-coordinate metrics false-negative on rattler-bearing families; full '
                  'D4 x relabel x translation alignment < 1e-6 is a sufficient shortcut, '
                  'never a necessary one. s-value alone is NOT a key: '
                  'families 19..24 share s ~ 3.903 but are six geometrically distinct '
                  'configurations (pairwise >= 6.7e-2 apart). Stratum merges: {1,2}, {13,14}.',
    'catalogue_completeness': 'A04 catalogue is NOT complete as a free-angle attractor list: '
                              '4 families missing (found by draining its own NOT-CP points). '
                              'Benign for the bound (smallest new attractor 3.9027 = 0.0256 '
                              'above the incumbent) but the BDBFS discovery loop is '
                              'load-bearing for the far-field campaign: certificates can only '
                              'discharge neighbourhoods of CPs someone has FOUND.',
    'far_field_guidance': 'for s_min >= ~3.887 the trivial Lipschitz bound sigma >= s(z)-h '
                          'beats the barrier out to the [V]-margin radius; consume '
                          'trivial-bound boxes for high-value CPs, barrier boxes for the '
                          'low-s families (barrier buys ~1.4-2x there).',
    'material_critical_structure': '10 distinct attractor structures: Trump (RIGID) + 9 valley '
                                   'mechanisms {1~2}, 6, {13~14}, 27 (marginal), 31, A37-NEW-0, '
                                   'A37-NEW-1 (marginal), A37-NEW-2, A37-NEW-3 (shallow); all '
                                   'other atlas entries are fixed-angle shadows (NOT-CP) that '
                                   'drain into these (24/24 constructively)' + (' + drain additions, see drain block'
                                           if drain else ' (drain worker pending at merge time)'),
}
key = lambda k: (0, k, '') if isinstance(k, int) else (1, 0, k)
out = {'meta': meta, 'drain': drain, 'entries': [ents[k] for k in sorted(ents, key=key)]}
with open(os.path.join(R, 'atlas_final.json'), 'w') as f:
    json.dump(out, f, indent=1)
print('atlas_final.json: %d entries; drain block: %s' % (len(ents), 'present' if drain else 'MISSING'))
for k in sorted(ents, key=key):
    e = ents[k]
    print('%-10s %-15s h=%-18s' % (k, e.get('class'), str(e.get('h_certified'))[:18]))
