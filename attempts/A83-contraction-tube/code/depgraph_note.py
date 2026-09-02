"""append A83 notes to lean/depgraph.json nodes D.SLAB and E.A36 (owners unchanged), then re-render."""
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
P = os.path.join(ROOT, 'lean', 'depgraph.json')
d = json.load(open(P, encoding='utf-8'))
NOTES = {
    'D.SLAB': (" || A83 (2026-09-03, docs/proofs/contraction_tube.md): CONTRACTION TUBE CERTIFIED "
               "(certs/tube_*.json + verify_tube.py, exact, 11 certs, 6 gates) - Theorem T1: every packing in "
               "Tube_v(T, r) = {z-hat - t v + w : t in [0,T], |w_i| <= r_i} has sigma >= s-hat, equality only "
               "at z-hat; slot-consistent ray (trump5 pins on their slot lines, free squares scaled = the exact "
               "pull-back of a (D) leaf) reaches T = 0.045 at A60's landing radii (1.6e-3, 2.1e-3 rad) and "
               "T = 0.0571 = the whole window at r = 6.5e-4; pure scaling ray T = 0.13. Wall = validity of pin "
               "row E3c2-7e3 (slot) / E7c2-9e3 (scale). Lemma SEAM: t = s-hat - m exactly, pins w = 0, free "
               "squares w <= r_land + 3.6e-7, NO B.2'' widening anywhere (tree logic applied to the dilated "
               "family at s0); delta_basin(trump5) = min(T_tube, T_K(delta_pin)) with T_K = (2/3) delta ŝ "
               "(A = 3/2): 0.0257 at delta_pin = 1e-2 -> A60's (K) leaves must be RE-EMITTED at delta_pin = 1e-2 "
               "(the 1e-4 plan reaches 2.5e-4 only). Protected classes: s0-Theorem-U caps T' ~ 3e-4 (pin drift "
               "through U's cores x 5.8 pocket) -> U-slab obligation (A80 owner). delta_LP(trump5) unscanned; "
               "A82's deep k4_08 point (eta -0.38 at s-hat - 0.044, unconverged) says protected crossovers "
               "lie deeper than the near-s-hat extrapolations."),
    'E.A36': (" || A83 (2026-09-03): the basin theorem has an ANISOTROPIC extension along the contraction ray "
              "(docs/proofs/contraction_tube.md T1): same (V') chain, same omega/P/Y (G3_UNIVERSAL, A22), "
              "tube box + pair-relative enclosures + split Taylor remainder + monotone iteration in place of "
              "quad_pin; checker certs/verify_tube.py reproduces checkA36's constants at T = 0 and hands over "
              "to A22 directly. Lean obligation written: lean/tube_obligation_A83.md (~400 lines on A79's "
              "files, no new analysis). Not yet Lean; owner unchanged."),
}
hit = 0
for n in d['nodes']:
    if n['id'] in NOTES:
        n['note'] = n.get('note', '') + NOTES[n['id']]
        hit += 1
assert hit == 2, hit
with open(P, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=1, ensure_ascii=False)
print('notes appended to D.SLAB, E.A36')
r = subprocess.run([sys.executable, os.path.join(ROOT, 'lean', 'render_depgraph.py')], capture_output=True, text=True)
print(r.stdout[-800:], r.stderr[-800:])
