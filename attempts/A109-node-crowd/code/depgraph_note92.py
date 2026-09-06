"""A92: chip K0.RES4 -> A92, append the A92 note to K0.RES4 / K0.TREE / K0.FREE, add the three new
nodes (K0.CEIL, K0.CROWD, K0.SLIDE) with edges, re-render depgraph.svg.  Run once at close-out
with the chore's numbers in RESULT below."""
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
P = os.path.join(ROOT, 'lean', 'depgraph.json')
d = json.load(open(P, encoding='utf-8'))

RESULT = os.environ.get("A92_RESULT", "[M] chore result: see attempts/A92-blocked-side/notes/crowd92_report.md")

NOTE_RES4 = (" || A92 (2026-09-03, docs/proofs/k0_blocked_side.md): the residue re-split by DEPTH instead of by frames. "
             "(S) substantive (every corner's 2nd intruder depth >= delta) is a WEIGHTED root measure certificate (Lemma CW: mu >= 1 everywhere, "
             "mu >= 1+e on the crowd family F_c(a_w), total < 11+8e; verified by TWO runs of the frozen verify_case.py on one measure) - the brief's "
             "'8-core K-leaf' does not exist (the depth-delta pose set has EMPTY core for delta < 0.134). Theorem CEIL [T]: max(mu_A, mu_B) >= "
             "1/(cos a + sin a) >= 1/sqrt2 for any two disjoint unit squares in a quadrant => per-corner min(d1,d2) <= 1 - 1/sqrt2 = 0.2929 "
             "(equality: the diagonal 45-deg pair); pair charge <= 1 so area alone (4 < E(s-hat) = 4.0318) never closes (S). "
             "(N) nicked: Lemma SLIDE [T, forall-packings, modulo K0-O1]: slide the shallow intruders' retreat clusters along the diagonal, grow the "
             "container, teleport => a K0-BLOCKED packing at side m < s-hat has d2(c) >= s-hat - m at EVERY corner. Composition (Theorem N): a crowd "
             "certificate C(delta, m_lo) (pad 0.4403 (s0 - m_lo) < delta) + SLIDE + K0-FREE kill every side in [m_lo, s-hat - delta]; a chain of "
             "certificates converges geometrically (ratio 0.4403) and gives s(11) >= s-hat - delta_inf, delta_inf = where the LP stops passing. "
             "EXACT RESIDUE RES-N(delta_inf): K0-BLOCKED packings at side m in (s-hat - delta_inf, s-hat) with some corner's 2nd intruder at depth in "
             "[s-hat - m, delta_inf) (+ nicked non-images at s-hat for uniqueness). " + RESULT)

NEW_NODES = [
    dict(id="K0.CEIL", title="Theorem CEIL: two disjoint unit squares in a quadrant have max(mu) >= 1/(cos a + sin a) >= 1/sqrt2 (per-corner min(d1,d2) <= 0.2929)",
         label="proved-prose", lean_axiom="stratum_kill (k0_00 piece; ceiling for (S))",
         note="A92 [T] Wedge Lemma (unit square in {y>=0, y<=(x-x0)tan a} has min x >= x0 + cos^2 a / sin a) + separating line; equality only at the diagonal 45-deg pair (the d2front87 motif, certified 0.292893 at side 4.357 = the maximum possible D2 at any side). Corollary: pair charge <= 1, route 2 (area) dead; float self-check results/ceil_check.json.",
         source="docs/proofs/k0_blocked_side.md sect 2.1-2.2, attempts/A92-blocked-side/code/ceil_check.py"),
    dict(id="K0.CROWD", title="(S) crowd-weighted root certificate C(delta, m_lo): no K0-BLOCKED packing at side in [m_lo, s0) with min_c d2 >= delta",
         label="open", lean_axiom="stratum_kill (k0_00 piece; the (S) half)",
         note="A92: Lemma B-YES (crowd hypothesis transfers to s0 with pad (lambda-1)(a + 1/sqrt2); a_w < 1 iff delta > 0.4403 (s0 - m_lo)), Lemma CW (two frozen-verifier runs on one measure: run A n = 11+8e plain; run B weights/(1+e) with the complement of the crowd family exempt). Canary: no Trump image realises the hypothesis for a_w < 1. " + RESULT,
         source="docs/proofs/k0_blocked_side.md sect 2.3-2.5, attempts/A92-blocked-side/notes/{chore_crowd_cert.md,crowd92_report.md}, certs/"),
    dict(id="K0.SLIDE", title="Lemma SLIDE: K0-BLOCKED at side m < s-hat forces d2(c) >= s-hat - m at every corner (nick floor); Theorem N composition",
         label="proved-prose", lean_axiom="stratum_kill (k0_00 piece; the (N) half)",
         note="A92 [T], forall-packings, no selection: slide the shallow intruders' u-retreat clusters (u = diagonal, depth rate exactly 1/sqrt2 per 1/sqrt2 of side) with the container growing at the far walls (Lemma CLUSTER affine feasibility, clusters only grow, <= 10 enlargements), then teleport (K0-FREE) => a k1 packing at side m + T; (k1-a) kills it for m + T < s-hat. Consumes K0-O1 exactly as K0-FREE. Theorem N: C(delta, m_lo) + SLIDE + K0-FREE kill all sides in [m_lo, s-hat - delta]; chain ratio 0.4403; residue RES-N(delta_inf) = the slab below s-hat.",
         source="docs/proofs/k0_blocked_side.md sect 3"),
]
NEW_EDGES = [
    dict(**{"from": "K0.RES4", "to": "K0.CROWD", "kind": "uses"}),
    dict(**{"from": "K0.RES4", "to": "K0.SLIDE", "kind": "uses"}),
    dict(**{"from": "K0.CROWD", "to": "K0.CEIL", "kind": "motivation"}),
    dict(**{"from": "K0.SLIDE", "to": "K0.FREE", "kind": "uses"}),
    dict(**{"from": "K0.CROWD", "to": "V.CASE", "kind": "uses"}),
]

ids = {n['id'] for n in d['nodes']}
for n in NEW_NODES:
    if n['id'] not in ids:
        d['nodes'].append(n)
for e in NEW_EDGES:
    if e['to'] in ids or e['to'] in {n['id'] for n in NEW_NODES}:
        if not any(x['from'] == e['from'] and x['to'] == e['to'] for x in d['edges']):
            d['edges'].append(e)
hit = 0
for n in d['nodes']:
    if n['id'] == 'K0.RES4':
        if 'A92 (2026-09-03' not in n.get('note', ''):
            n['note'] = n.get('note', '') + NOTE_RES4
        n['owner'] = 'A92'
        hit += 1
    if n['id'] == 'K0.TREE' and 'A92:' not in n.get('note', ''):
        n['note'] = n.get('note', '') + " || A92: the depth split (K0.CROWD + K0.SLIDE) is a tree-free alternative for everything below s-hat - delta_inf; the tree remains the fallback for the slab RES-N(delta_inf)."
assert hit == 1, hit
with open(P, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=1, ensure_ascii=False)
print('K0.RES4 chip -> A92; nodes', len(d['nodes']), 'edges', len(d['edges']))
r = subprocess.run([sys.executable, os.path.join(ROOT, 'lean', 'render_depgraph.py')], capture_output=True, text=True)
print(r.stdout[-400:], r.stderr[-400:])
