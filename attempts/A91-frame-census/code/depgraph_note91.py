"""A91: append the C.K4TIER note (chip left with its current owner), re-render depgraph.svg."""
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
P = os.path.join(ROOT, 'lean', 'depgraph.json')
d = json.load(open(P, encoding='utf-8'))
NOTE = (" || A91 (2026-09-03, docs/proofs/frame_census.md): A90's residue RES(4) enumerated as an exact finite object (frames: roles/types/masks/"
        "anchoring columns, levels L0-L3, Lemmas F1-F8 incl. the chord lemma => per wall <= 3 / <= 1 free per wall, COL vacuous at L1, the rate row). "
        "COUNT [EXACT/MC]: L1 = 5.7e28 frames mod G (MC 1.3e29), L2 ~1e37 orbits, L3 <= 1.6e59; combinatorics buy x3.3 (L0) / x2.9e4 (L1); box LP "
        "realisability kills 99.7 % at 3.8 ms => realisable ~1.2e38 at L2; PRICE ~1.3e32 CPU-h vs A85's 3 200-7 000: the frame-census route LOSES by "
        "~28 orders, and its 0.3 % survivors (the Trump-with-2-crowds archetype among them) never close at box level. Canaries 3/3 PASS. [T] the "
        "archetype's clusters are all WALL-anchored; Lemma W-GEN: corner-weighted Psi^(w) (Q-independent weights) makes every rate-1 cluster strictly "
        "anchored (no X-X plateaus); A91-G1 [C] = slide-iteration termination for tilted-D rate ties (not load-bearing). VERDICT: k0_00 stays on A85's "
        "tree with not-RES(4) as a SelForm (C) leaf (A90 sect 6(i)); (C-sel) per-node anchoring test designed (sect 9), pricing chore named (1 h), not run.")
hit = 0
for n in d['nodes']:
    if n['id'] == 'C.K4TIER':
        if 'A91 (2026-09-03' not in n.get('note', ''):
            n['note'] = n.get('note', '') + NOTE
        hit += 1
assert hit == 1, hit
with open(P, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=1, ensure_ascii=False)
print('C.K4TIER note appended; owner left as',
      [n.get('owner') for n in d['nodes'] if n['id'] == 'C.K4TIER'])
r = subprocess.run([sys.executable, os.path.join(ROOT, 'lean', 'render_depgraph.py')],
                   capture_output=True, text=True)
print(r.stdout[-400:], r.stderr[-400:])
