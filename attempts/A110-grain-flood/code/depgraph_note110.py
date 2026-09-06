"""Append A110's notes to the depgraph (C.A57 and K0.RESN) and add the GRAIN node (owner A110).
Usage: python depgraph_note110.py  (edits lean/depgraph.json in place, utf-8, keeps everything else)."""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
P = os.path.join(ROOT, 'lean', 'depgraph.json')
g = json.load(open(P, encoding='utf-8'))
notes = json.load(open(os.path.join(ROOT, 'attempts', 'A110-grain-flood', 'results', 'depgraph_notes.json'), encoding='utf-8'))
byid = {n['id']: n for n in g['nodes']}
for nid in ('C.A57', 'K0.RESN'):
    byid[nid]['note'] = byid[nid].get('note', '') + ' || ' + notes[nid]
if 'GRAIN' not in byid:
    g['nodes'].append(dict(id='GRAIN', title='Grains: fixed-tilt polyhedra, chain formulas, the flood rule, and the box-to-grain obstruction',
                           label='proved-prose', lean_axiom=None, owner='A110',
                           source='docs/proofs/grain_flood.md; attempts/A110-grain-flood', note=notes['GRAIN']))
    g['edges'].append(dict({'from': 'C.A57', 'to': 'GRAIN', 'kind': 'motivation'}))
    g['edges'].append(dict({'from': 'K0.RESN', 'to': 'GRAIN', 'kind': 'motivation'}))
json.dump(g, open(P, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('depgraph updated: C.A57, K0.RESN notes; GRAIN node', 'added' if 'GRAIN' not in byid else 'present')
