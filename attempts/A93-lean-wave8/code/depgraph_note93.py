"""A93: note-only updates on the K0.* nodes (chips stay with A92): 'Lean: ...' lines on
K0.CW / K0.SLIDE / K0.CEIL / K0.RESN / K0.FREE, plus the V.CASE consumer note; re-render svg.
Run once at close-out; idempotent (skips nodes that already carry the A93 note)."""
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
P = os.path.join(ROOT, 'lean', 'depgraph.json')
d = json.load(open(P, encoding='utf-8'))

CEIL = os.environ.get("A93_CEIL", "Lean (A93, 2026-09-04, Ceil.lean): THEOREM ceil / ceil_packing - two closed unit squares in [0,s]^2 with disjoint interiors have max(mu_BL A, mu_BL B) >= 1/sqrt2 (mu = Crowd.muC, the attained min of max(x,y)); separating line from geometric_hahn_banach_open on the open convex interiors + interior combos (exists_sep_line, unit normal), corner-cut case ceil_corner_cut (mu >= 0.853 > 0.71 >= 1/sqrt2), wedge case wedge_x / wedge_y with n_x L_B + (-n_y) L_A = 1; the Wedge Lemma's concavity step is the exact factorisation (aS)^2 - (a^2-(a-b)C)^2 = (a-C)((a^2+(a-b)^2)C + a b^2) (wedge_core). Axioms propext/Choice/Quot.sound.")

NOTES = {
    "K0.CW": ("Lean (A93, 2026-09-04, lean/PackingCertMathlib/PackingCertMathlib/{Crowd,CrowdZone}.lean): Lemma B-YES = scaleC_meets_cornerBox "
              "(pad (lambda-1)*r for any r >= wT/2; r = 7072/10000 via wT_le_bound); Lemma CW = crowd_sound (weight arithmetic: 8 crowd members "
              "priced >= (1+e) wd by run B, 3 by run A, total < n wd <= (11+8e) wd; 8 distinct members from not_meets_two_corners, (s0-2a_w)^2 > 2); "
              "Theorem S(delta) window form = crowd_cert_kill; the 'one measure' and 'E disjoint from F_c(a_w)' clauses are DECIDABLE checkers "
              "sameMeasure / crowdZones (separating-axis tests with ratCosSin/rmul4 enclosures, bisection) with soundness theorems; "
              "crowdKill_of_files packages two checkCaseI PASSes + sameMeasure + crowdZones + rational side conditions into CrowdKill delta m_lo s0. "
              "Axioms propext/Choice/Quot.sound. Replay generator lean/gen_crowd_lean.py (isolated Corpus/Crowd/Check_<tag>.lean, native_decide); "
              "no certificate delivered by the chore yet, so no replay module exists. A94 correction absorbed: crowd_sound_incidence = Lemma CW-S (one atom list, 1 + r_max runs B_r with the exact complement of the r-fold family exempt, budget n <= 11 + 2 m_u e, pin cores, incidence double count sum_p #meeters >= 2 m_u); corner boxes = the case m_u = 4, r_max = 1."),
    "K0.SLIDE": ("Lean (A93, 2026-09-04, Slide.lean): slide_crowd is a THEOREM (forall packings, modulo K0-O1 = K0O1 : forall c, SlabKill {corner slot c} 3.82 s-hat): "
                 "every packing at side m in [3.82, s-hat) has at every corner two distinct squares meeting the closed box [0, 1-(s-hat-m)]^2. "
                 "PROOF SIMPLIFICATION: no clusters, no Lemma CLUSTER, no enlargement rounds - translate the WHOLE packing away from the corner "
                 "(shiftCfg; container grows at the far walls), a rigid motion is a packing at side m+tau outright and mu_c rises by exactly tau "
                 "(cframe_shift); attained minima (exists_min_gcf) give the tau < s-hat - m; K0-FREE (k0free_kill = teleport_packing + K0-O1) closes. "
                 "Note: the prose's sequential Step 2 only yields sum_{i>=1} d_i >= s-hat - m; the stated d_2 >= s-hat - m needs the simultaneous "
                 "motion (all shallow intruders at once), which the whole-packing translation is. A94 addendum (PinnedSlide.lean): Lemma SWEEP = sweep_core (floor argument on a Young down-set; an interior point landing in an open cell after a move away from the walls was in a closed cell of the block before) + sweep_packing; Lemma MOVE cluster-free = pinnedShift_packing (non-pins shift by shiftVec c tau, each pin block by pinVec c' tau = its anchoring walls' displacement; packing at side m+tau containing the same pins for EVERY tau >= 0). Remaining for SLOT-SLIDE: the teleport composition with the clip census (Lemma CONT) - named obligation slot_slide. Axioms propext/Choice/Quot.sound."),
    "K0.CEIL": CEIL,
    "K0.RESN": ("Lean (A93, 2026-09-04, Composition.lean): named hypothesis ShellKill i delta_inf (below: no packing of class i at m in (s-hat - delta_inf, s-hat) "
                "with CrowdBox m (1-(s-hat-m)) and not CrowdBox m (1-delta_inf); at_shat: non-crowded packings of class i at s-hat are Trump images); "
                "classKilledAt_of_chain: K0-O1 + chain + ShellKill i => ClassKilledAt i m on the whole window, for EVERY class i (k0_00's stratum_kill piece). "
                "Below s-hat - delta_K the chain is class-blind: no_packing_of_chain / s_eleven_ge_of_chain (s(11) >= s-hat - delta_K) / classKilledAt_below_of_chain."),
    "K0.FREE": ("Lean (A93, 2026-09-04, Slide.lean): k0free_kill - a corner whose open unit box is interior-met by <= 1 square: teleport_packing into the slot "
                "+ K0-O1 (SlabKill of the corner slot); the corner box is cornerBox m 1 c = slotBox (slotCentre m (c,0,0)) (cornerBox_one_eq_slotBox)."),
    "V.CASE": ("A93 consumer: the crowd certificate consumes checkCaseI_price twice (run A: cores=[] nofams=[]; run B: cores=[] with the exemption clause) "
               "and checkCaseI_facts for the total; see Crowd.crowd_sound."),
}

hit = 0
for n in d['nodes']:
    if n['id'] in NOTES and 'A93, 2026-09-04' not in n.get('note', '') and 'A93 consumer' not in n.get('note', ''):
        n['note'] = n.get('note', '') + " || " + NOTES[n['id']]
        if n['id'] in ("K0.SLIDE", "K0.FREE", "K0.CEIL"):
            n['label'] = 'lean-proved'  # K0.SLIDE/K0.FREE: modulo K0-O1 (in the note)
        hit += 1
with open(P, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=1, ensure_ascii=False)
print('A93 notes appended:', hit, '; nodes', len(d['nodes']), 'edges', len(d['edges']))
r = subprocess.run([sys.executable, os.path.join(ROOT, 'lean', 'render_depgraph.py')], capture_output=True, text=True)
print(r.stdout[-400:], r.stderr[-400:])
