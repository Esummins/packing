"""Append A118's one-line note to the depgraph C.A57 node (owner field untouched).
Usage: python depgraph_note118.py   (edits lean/depgraph.json in place, utf-8, nothing else)."""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P = os.path.join(ROOT, "lean", "depgraph.json")

NOTE = ("A118 (2026-09-06, measurement + one new leaf kind, attempts/A118-lane-count): "
        "LANE-COUNT -- for a usable cell C of the class, count the maximum number of pairwise "
        "interior-disjoint unit squares that can meet int C given the walls, the pins and the "
        "conditioned core (in C's CORNER FRAME, on the ORIGINAL packing, with the node's "
        "hypothesis pulled back over [m_lo, s0] -- every position affine in m); LANE + M <= 1 "
        "kills the node by teleport (SLOT-CROWD), with NO LP and NO certificate replay. "
        "Sweep over 3,580 A57/A60/k0 records (18,086 node-cell verdicts, 1.84 CPU-h, 0.37 s per "
        "cell): 62 nodes fire; box-matched against the campaign ledgers 25 of them REPRODUCE "
        "boxes A57/A60 already certified dead (positive control, 2,300x cheaper), 24 are "
        "dead-at-LP and 13 are NEW -- k5_11_interior_Y1080 (the one A57 box whose tree row is "
        "FAIL, with all eight children) and 12 of the 217 alive k0 cells, the latter conditional "
        "on k1_00. Fire rate 1.7 % => ~0.05 wall-days at 5 workers; deploy AT EMISSION as a "
        "1.85 s/node pre-screen, never as a re-solve. THE TRAP: the count is vacuous in the "
        "DILATED frame -- on the slab the licensed crowd pad is a_w = 1 exactly (SLOT-SLIDE's "
        "depth credit cancels Lemma B-YES-S's pad, A109 aw_check) and F_p(1) contains the "
        "grazing staircase, disjoint from everything in the cell, so LANE >= 2 at every node; "
        "the leaf only has teeth on the original packing. WHERE IT STOPS: corner cells dominate "
        "(TR(0,0) 27, BL(1,0) 15, TL(0,0) 9; BL(1,1) fires once in 3,580) and 1,323 cells sit at "
        "LANE <= 1 saved only by M = 1 (the node's own conditioned square may be the second "
        "meeter). A118-O1: a lane-count leaf excludes class-S images, not A57's whole delta=1e-2 "
        "slack family, so it must not be re-used for lemmas.md T23's broader slack statement. "
        "A109-O1 DISCHARGED and slot_crowds.md 1.2's usable-slot table superseded (A114 made "
        "k6_07/k6_21/k6_23/k6_27 FULL on the CLOSED window: k5_16 m_u 4->6, trump5 m_u 4->6). "
        "T4 (reversed leaf, branch on the two meeters): sound, free on the '<= 1 meeter' side, "
        "and unaffordable on the other -- 276-44,850 pair-children per cell, Lemma TC kills "
        "60.4 % and a new octagon PAIR test 8.3 %, 2 of 24 sampled children die and CERTIFY, so "
        "2-500 CPU-h to kill one node against 850 s for its own LP. Lean shape: teleport_packing "
        "under the T5 pattern; obligations O-COVER / O-PAIR / O-HULL, all interval arithmetic "
        "(notes/t3_lean.md). Canaries all PASS (exact Trump depths to <5e-7; trump5 ROOT LANE>=2 "
        "at all six usable cells incl. BL(0,2) and TL(0,0); Trump's TL pair-box survives).")


def main():
    d = json.load(io.open(P, encoding="utf-8"))
    hit = False
    for n in d["nodes"]:
        if n.get("id") == "C.A57":
            if "A118 (2026-09-06" in (n.get("note") or ""):
                print("already present, nothing done")
                return
            n["note"] = (n.get("note") or "").rstrip() + " || " + NOTE
            hit = True
    if not hit:
        raise SystemExit("C.A57 not found")
    with io.open(P, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    print("C.A57 note appended")


if __name__ == "__main__":
    main()
