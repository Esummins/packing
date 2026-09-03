"""A84: append the C.K4TIER note (owner chip A84 -> released at close), re-render depgraph.svg."""
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
P = os.path.join(ROOT, 'lean', 'depgraph.json')
d = json.load(open(P, encoding='utf-8'))
NOTE = (" || A84 (2026-09-02, docs/proofs/protected_trees.md): LEMMA P-TREE HOLDS [T] - an s0 zone-tree over the "
        "MONOTONE pin hypothesis (slack cores delta_pin) with (K) Lemma-B kills, (C) logic kills and (D) full "
        "localisations of the N = 11-k free squares near a compatible Trump image g.z-hat, composed with the "
        "contraction tube in the class's OWN direction (v = beta on the Trump-frame pin set I_g, c-hat/s-hat "
        "elsewhere; D4 commutes with dilation), excludes every packing containing S's pins at every side in "
        "[s-hat - delta_basin(S), s-hat) and makes every such packing at s-hat a Trump image. The exact-stratum "
        "hypothesis enters NOWHERE on the bound and only optionally at equality (Simp(g.z-hat) != S); H10-stuck "
        "(U-O2) is a corollary; Theorem U is not consumed (A83 4.3's T' ~ 3e-4 cap void). The tier = 14 trump5-like "
        "campaigns + 2 shadow trees (k4_05, corners4 have NO compatible Trump image, exact). LEMMA PD [T+M]: slack "
        "pin cores put a residue FLOOR = delta_pin under every ladder (k3_05: gap stalls at 0.0219, residue -> 3862); "
        "the drifted FULL pin square Sigma_p + (lambda-1)alpha_p with the two-endpoint convexity test restores A59's "
        "contraction (ratio 3.6-4.5, landing L24 with 59 boxes at 1.1427e-3 / 2.0102e-3 rad = A60's numbers, both "
        "pilot classes) - A60's delta_pin = 1e-2 re-emission needs it too. TUBE LAW [M, 19 directions, 42 certs]: "
        "T_max = 0.0457 (A60 landings) / 0.0574 (r = 6.5e-4, whole window) iff BL(0,1) is pinned (wall E3c2-7e3), "
        "else 0.1305 / 0.1680 (wall E7c2-9e3): whole-window seam for the BL(0,1)-pinned classes needs one more ladder "
        "level than A60 and delta_pin = 2.5e-2; the rest get the window x2.3 at A60 landings; regime-1 plain kills "
        "can be dropped. PILOT (k4_08, k3_05; A60 engine copied, both images' exact witnesses): census 752 / 984 "
        "attemptable at budget 6 / 7, 84 unkillable each (2 x 41), ladders land L24; P1 analogue PASS for both (eta -3): "
        "the interior zone is the whole cover; LP sample PARTIAL (6 GB commit gate behind A78 lean builds + a 12 GB "
        "foreign process): cover 2 PASS / 1 FAIL at eta ~ -0.8, ~700 s LP + 400-800 s cert per box (x3 / x15 A60); "
        "LADDER QUEUE 0/4 at L6-9 (tau = budget, one converged, no exact 6-family found on the grid) => the j = 0 "
        "queue is a deepen/conditioning queue, not a kill queue - the unmeasured price term (A60 never ran its ladder "
        "kills either). PRICE (sect 7): k4 image-bearing ~110-160 CPU-h each + the resister term; k3 ~200-300; "
        "k0_00 dominates (root eta = 0 at 3.833 per A82, no pins/logic kills, 8 images; >= 100 desktop-days plain, "
        "~25-30 with the stuck-only A58 corner seed); corners4: Lemma CC4 [T at s0] - every one of its 8 arm slot "
        "boxes is met by >= 2 non-pin squares (CC-2 teleport into k5_16 = its only k5 superclass, killed by A57) - "
        "plus an EXACT feasible square meeting 3 slot boxes (refutes the '<= 2 per square' count), so a finite case "
        "analysis is required (~2-10 desktop-days). Owner A84 closed; the tier is a compute campaign per class "
        "(obligation table sect 5) with two theory items still open: the ladder-resister law and corners4's cases.")
hit = 0
for n in d['nodes']:
    if n['id'] == 'C.K4TIER':
        n['note'] = n.get('note', '') + NOTE
        n['owner'] = None
        hit += 1
assert hit == 1, hit
with open(P, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=1, ensure_ascii=False)
print('C.K4TIER note appended, owner released')
r = subprocess.run([sys.executable, os.path.join(ROOT, 'lean', 'render_depgraph.py')], capture_output=True, text=True)
print(r.stdout[-600:], r.stderr[-600:])
