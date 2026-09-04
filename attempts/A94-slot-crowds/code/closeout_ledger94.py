"""A94 close-out: append the REGISTRY row and the LOG entry (idempotent: skipped if the A94 row/entry
is already present)."""
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
REG = os.path.join(ROOT, "attempts", "REGISTRY.md")
LOG = os.path.join(ROOT, "LOG.md")

ROW = ("| A94-slot-crowds | theory lead (Fable) + 1 Opus chore, <= 2 processes | PI observation: generalise A92's "
       "K0-BLOCKED crowd machinery to the completable slots of the pinned classes so k5_11/k5_16 (then the protected "
       "tier) die on [3.82, s-hat - delta_inf] by one certificate chain instead of A57's 4-side grid | T1 Lemmas "
       "CONT/SLOT-CROWD/SWEEP/MOVE/SLOT-SLIDE/B-YES-S/CW-S + Theorem N-S + Lemma CEIL-T (docs/proofs/slot_crowds.md); "
       "exact census + exact-Trump canary (code/slots94.py, trumpcanary94.py, protected94.py); T2 Opus chore = A92 "
       "engine copy with slot families in slot frames, slack pin cores, incidence budget, (1+r_max)-run frozen "
       "certification (code/slotcrowd94.py etc.) | done-mixed | **THEORY LANDS, CERTIFICATES DO NOT.** SLOT-CROWD [T] "
       "forall-packings, unconditional for the pinned classes (teleport onto a usable unclipped completable slot lands "
       "in a k6 extension that A56/A61 kill on the window): k5_11 usable slots BL(1,1) (k6_18), BR(0,1)/TL(1,0) "
       "(k6_20), TR(0,0) (k6_23, to 3877/1000); k5_16 BR(0,1) (k6_29), TR(0,1) (k6_30), TR(1,0) (k6_28), BL(1,0) "
       "(k6_23); k5_16's BR(1,0)/TL(1,0) wait on k6_27 (A61). Census exact: 8 completable slots each, 4 resp. 6 "
       "unclipped, 4 usable each (m_u = 4). SLOT-SLIDE [T]: retreat along the slot-frame diagonal away from the backed "
       "sides, container grows at the far walls, PIN BLOCKS MOVE WITH THEIR ANCHORING WALLS (stay at their slots) and "
       "never obstruct (Lemma SWEEP: relative motions are always away from a Young down-set's walls) - the brief's "
       "(C)-contact case does not arise; d2 >= s-hat' - m at every usable slot. CORRECTION to A92 sect 3.1: the d2 form "
       "needs the JOINT translation of all shallow intruders (one cluster, cost exactly d2); the sequential proof gives "
       "only the sum bound - A93 T2 should formalise the joint form. Lemma CW-S [T]: pin cores slackened by rho >= "
       "(lambda-1)A_S (Lemma B'), slot families with pad (lambda-1)(a + 1/sqrt2 + max(i,j)) (pad ratio 0.698 vs A92's "
       "0.440), INCIDENCE budget N + 2 m_u e with r_max runs B_r (an axis-aligned square near (2.44,2.44) meets all "
       "four k5_11 boxes at s0). Theorem N-S: G2/G3/G4 unnecessary iff delta_inf <= 0.0154, G3/G4 iff <= 0.0300, G4 "
       "iff <= 0.0446. EXACT-TRUMP CANARY PASS (60-digit A03 data, Fractions): all 6 unclipped trump5 slots doubly "
       "met, second depths 0.016049/0.280083/0.252050/0.264033/0.305293/0.155475 (A58 reproduced exactly), "
       "containment lemma holds. Lemma CEIL-T: a class with a compatible Trump image is crowd-killable only below "
       "s-hat - max_g min_p d2(g,p) => k4_03/k4_06/k4_08 ceilings 3.72/3.72/3.61 < 3.82 (chain VOID on the window, "
       "they keep P-TREE), k4_11 3.861, trump5 3.72; k4_05/corners4 no image (eligible once k5_11/k5_16 are dead on "
       "the window); k <= 3 tier has no usable slot (extensions = protected k4 or s0-only A55 k4 kills). MEASURED "
       "(chore, 397 min, 23 LPs, 4 cert chains; canaries PASS incl. e=0 regression 5.874/5.960): on (s0, G2] both "
       "classes pass the LP only at delta >= 0.2 (k5_11 eta -0.80/-0.25, k5_16 -0.95/-0.58) and fail at delta <= 0.1 "
       "(k5_11 delta 0.1 e 1/8: tau 7.007 vs 7 - 0.007 short) => delta_inf >= 0.2 at the s0 side, the chain removes "
       "NO A57 side; on (G4, 3.82] k5_11 passes at delta 0.1/0.04/0.02 (eta -0.25/-0.22/-0.21), k5_16 at 0.1 (-0.16), "
       "but NO certificate closes: the converged delta 0.1 node (minmass 1.0000, 39 atoms; close-out run 1794 s) gives "
       "run A PASS, B1 PASS, B2-B4 FAIL with 30-32 exact HOLES - the incidence rows r >= 2 are not priced by the row "
       "oracle (A94-G4, engine gap, not a refutation; eps_geo cannot cure real holes). A certified delta = 0.1 there "
       "would not kill the slab anyway (SLIDE gives d2 >= 0.0438 only; the slab-killing delta is 0.04, whose LP pass "
       "is unconverged at minmass 0.88 and predicted to fail the same way). VERDICT: mechanism sound and LP-live at "
       "the low side, dead at the s0 side where it would have to bite; A57's sides (A96's parametric pass) remain "
       "the kill for k5_11/k5_16. m_u = 4 caveat folded into Theorem N-S (s-hat' = 3877/1000; sliver to G1). "
       "Discipline: <= 2 processes, BLAS pinned, 6144 MB commit gate, A57/A60/A61/A86/A92/A93 untouched, frozen "
       "verifiers untouched. | attempts/A94-slot-crowds |\n")

LOGE = """
## 2026-09-04 A94-slot-crowds (Fable lead + 1 Opus chore, <= 2 processes) -- closed done-mixed: theory lands, no certified PASS
- T [docs/proofs/slot_crowds.md]: SLOT-CROWD [T] forall-packings and UNCONDITIONAL for pinned classes - every usable unclipped completable slot of S is met by >= 2 non-pin
  squares, else teleport onto the slot lands in the k6 extension that A56/A61 kill on the window (k5_11: BL(1,1)->k6_18, BR(0,1)/TL(1,0)->k6_20, TR(0,0)->k6_23 to 3877/1000;
  k5_16: BR(0,1)->k6_29, TR(0,1)->k6_30, TR(1,0)->k6_28, BL(1,0)->k6_23; BR(1,0)/TL(1,0)->k6_27 OPEN). Exact census: 8 completable slots each, 4/6 unclipped, 4 usable each.
  SLOT-SLIDE [T]: retreat along the slot-frame diagonal away from the backed sides; pin blocks translate WITH their anchoring walls (stay at their slots in the grown container)
  and never obstruct (Lemma SWEEP: every relative motion is away from a Young down-set's walls) - no (C) contact; d2 >= s-hat' - m at every usable slot. CORRECTION to A92 3.1:
  the d2 form needs the JOINT translation of all shallow intruders (the sequential proof gives only the sum bound); A93 T2 should formalise the joint form.
  Lemma CW-S [T]: slack pin cores rho >= (lambda-1)A_S, slot pad (lambda-1)(a+1/sqrt2+max(i,j)) (ratio 0.698 vs 0.440), INCIDENCE budget N + 2 m_u e with r_max runs B_r.
  Theorem N-S: chain + A57 G1 shell; G2/G3/G4 retired iff delta_inf <= 0.0154, G3/G4 iff <= 0.0300, G4 iff <= 0.0446. Lemma CEIL-T (exact Trump): k4_03/k4_06/k4_08 crowd
  ceilings 3.72/3.72/3.61 < 3.82 - the chain is VOID for them on the window (P-TREE stays); k4_11 3.861; k4_05/corners4 eligible only after k5_11/k5_16 die on the window;
  k <= 3 tier blocked on k4 window kills. Exact-Trump canary PASS (all 6 unclipped trump5 slots doubly met; d2 = 0.016049 ... 0.305293; A58 reproduced exactly).
- M [chore, notes/slotcrowd94_report.md, 397 min, 23 LPs, 4 cert chains, canaries PASS incl. e=0 regression]: on (s0, G2] the LP passes only at delta >= 0.2 for both classes
  and fails at delta <= 0.1 (k5_11 delta 0.1 e 1/8: tau 7.007 vs budget 7) => delta_inf >= 0.2 at the s0 side: THE CHAIN REMOVES NO A57 SIDE. On (G4, 3.82] k5_11 passes at
  0.1/0.04/0.02 (eta -0.25/-0.22/-0.21), k5_16 at 0.1, but no certificate closes: close-out certification of the converged delta 0.1 node (minmass 1.0, 39 atoms, 1794 s) =
  run A PASS, B1 PASS, B2-B4 FAIL with 30-32 exact HOLES - the incidence (r >= 2) rows are not priced by the row oracle (A94-G4, engine gap; eps_geo cannot cure real holes).
  A certified delta 0.1 would not kill the slab anyway (needs delta <= 0.0438 = the unconverged 0.04 pass, minmass 0.88, predicted to fail identically); the slab is A96's job.
  m_u = 4 (incl. the k6_23 slot) folded into Theorem N-S honestly: s-hat' = 3877/1000, sliver to G1. Verdict: mechanism sound, LP-live at the low side, dead at the s0 side.
- Discipline: <= 2 processes (driver + one certify), BLAS pinned, 6144 MB commit gate x2 readings; A57/A60/A61/A86/A92/A93 untouched; frozen verifiers untouched; git: fetch +
  plain merge (already up to date) + push own paths. Files: docs/proofs/slot_crowds.md, attempts/A94-slot-crowds/{code,results,certs,logs,notes}, lean/depgraph.json+svg
  (C.A57 note + chip -> A96, C.K4TIER CEIL-T note, K0.SLIDE joint-translation note, K0.CW slot-form note), REGISTRY row.
"""


def main():
    reg = open(REG, encoding="utf-8").read()
    if "| A94-slot-crowds |" not in reg:
        with open(REG, "a", encoding="utf-8") as f:
            f.write(ROW if reg.endswith("\n") else "\n" + ROW)
        print("registry row appended")
    log = open(LOG, encoding="utf-8").read()
    if "A94-slot-crowds (Fable lead" not in log:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(LOGE)
        print("LOG entry appended")


if __name__ == "__main__":
    main()
