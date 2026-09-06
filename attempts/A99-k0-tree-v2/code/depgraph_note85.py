"""A85: append the C.K4TIER note (owner chip A85 -> released at close), re-render depgraph.svg."""
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
P = os.path.join(ROOT, 'lean', 'depgraph.json')
d = json.load(open(P, encoding='utf-8'))
NOTE = (" || A85 (2026-09-02, docs/proofs/k0_route.md): the k0_00 instance re-examined - NO order-of-magnitude cut along the "
        "three cuts. [T] Lemma K0-FREE: a corner box met by <= 1 square teleports the packing into k1_00's MONOTONE hypothesis "
        "at the same side (teleport_packing); k1_00's P-TREE (tube 0.1305 >= the window) excludes it at every m < s-hat and "
        "Theorem U closes m = s-hat: FORALL-packings, A84's stuck-only caveat void, exact-class question moot (K1 climbs). "
        "[T] Lemma K0-D4: equivariant quotient /8 with mod-G transport of (K)/(C)/(T)/(D)/(D') verdicts (Theorem A38.1 + d4_wlog "
        "at the root; orbit representatives on the seed, canonical fraction measured 0.120). [T+M] Lemma K0-PAIR: NO finite "
        "case list for K0-BLOCKED - the corner 2-crowd space has interior and contains same-sense tilted pairs (32 % of 33 656 "
        "surviving pair boxes); the 'mixed-sign V' prune is unsound. [M] The seed as a cover is DEAD (644 reach boxes, 33 656 "
        "pairs per corner, 2.9e16 four-corner nodes). [T] K0-ATLAS: A37 boxes are (D') leaves with no dilation / window "
        "obligation; 12 k0 ghosts within 0.02 of s0 (atlas families 9/8/7/11, all outside the atlas) drained by 3S boxes centred "
        "at the ghosts (h = s_g - s0 >= 6x the landing radius, ~1 desktop-hour). [T+M] K0-ROT stated exactly (centre-height term; "
        "Trump D+-sigma = 3.877; ghosts within 2.2e-7); selected-form (C) rule, no price effect. [M] A38-G7 CLOSED with the A60 "
        "engine on A38's own cells: level 1 undecided (0/3, all eps_geo repairs fail), depth 2 decided (tau = budget - 1.0..1.27, "
        "3/3; first cold PASS of a no-pin node at s0, ~1 000 s LP + 630-860 s cert). PRICE: 3 200-7 000 CPU-h (45-100 "
        "desktop-days at 3 slots) if depth-2 certifications repair at ~85 %, else >= 3e4 CPU-h: 3-30x below A38's floor, not "
        "below A84's plain >= 100 desktop-days; the deciding constant is certification reliability at eta ~ -1. T4: the seed does "
        "not force the selected form; the stratum_kill_all/_min split is needed only for K0-ROT leaves (lean/k0_readiness_A85.md). "
        "Owner A85 closed.")
hit = 0
for n in d['nodes']:
    if n['id'] == 'C.K4TIER':
        if 'A85 (2026-09-02' not in n.get('note', ''):
            n['note'] = n.get('note', '') + NOTE
        n['owner'] = None
        hit += 1
assert hit == 1, hit
with open(P, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=1, ensure_ascii=False)
print('C.K4TIER note appended, owner released')
r = subprocess.run([sys.executable, os.path.join(ROOT, 'lean', 'render_depgraph.py')], capture_output=True, text=True)
print(r.stdout[-600:], r.stderr[-600:])
