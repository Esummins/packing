# A265 -- STRIP (the jammed sector's last lemma) and the OPEN corner layer of A263's P2 tree (add PLUG), plus the
# gap-count closure.  What A264 left of the k0 chain at n = 11.  (2026-09-22.)
Fable.  LAUNCH-AND-EXIT -- NEVER wait for a detached run.  Ops: short responses, files <= 250 lines, no monitors, no
interim messages, explicit-pathspec commits (fetch + plain merge only), PYTHONDONTWRITEBYTECODE=1, ONE heavy python
process at most (BelowNormal, affinity 0xFFFF; sub-minute helpers fine); detached launches call Git Bash by explicit
path.  RUNNING, never touch: the k5 pass loop, A256's loop256, A257's pilot257, the status loop, the chains of
A259-A263 (run259/260/261/262/263.sh) and their certs -- for task 2 write NEW cert files under attempts/A265-strip-plug/certs, never into A263's.
Read first: docs/proofs/three_lemmas.md (A264: NEAR-FLAT CUBE [T]; JAMMED SECTOR reduced to A262's pair3 at BL +
Lemma STRIP [C] (Lean strip_lemma, jam_sector_of_strip): replacing the floater C by its WALL drop T_u keeps both
BL sectors negative on 323/323 JAM rings and no sector square enters T_u minus C; NON-SERVING GAP: GAP-CELL (P1+),
BLOCKER-SIDE, STRIP-CHAIN [T], open: 1 + w - sec <= e < sec, unequal tilts, the count), docs/proofs/k0_route.md
s.13 (the 13-link chain), no_jam.md (A262), locked_wall.md (A260: Lemma PLUG -- a free square reaching within rho
of the corner contains the START square's lowest vertex (cos phi', a') when a' in (0.354 + rho, 1); with the plug
as a fifth obstacle A259's corner layer certified in 6 s), open_pairs.md + attempts/A263-open-pairs/code/cert263.py
(the P2 / WE / WS trees; the OPEN leaves), box_meeters.md (P1+, BLOCKER-SIDE), normal_room.md (PAIR, TOOTH).

## Task
1. Lemma STRIP [prove]: in the BL sector of a JAM ring, every free unit square that avoids the floater C also
   avoids the strip T_u minus C (T_u = C's wall drop), i.e. no free square enters the strip.  Candidates: the
   strip is bounded by A below (?), by X above and by the wall; its width is C's offset 0.72 minus ... -- compute
   the strip's exact shape from (A, C, X) and show it holds no unit-square vertex reachable from the pocket
   (PLUG-type: a square in the strip contains a named vertex of A or X), or find the sub-domain where it fails and
   draw it.  Test on the 323 JAM rings first (A264's data).  Then the sector is A262's pair3 with T_u as the END
   square: state jam_sector_of_strip's consequence with tags.
2. A263's P2 tree has OPEN cells 2,4 / 2,5 / 3,4 / 3,5 / 3,6 (index P2263_index.jsonl ok:false): the OPEN leaves
   sit at b >= 0.98 (e.g. box b in [0.9961, 1], phi_W 11.4 deg, a' 0.51, phi' 23.4 deg, box margin +0.016) -- the
   closed-corner layer that A260 closed for A259 by adding PLUG as a fifth obstacle (a' = 0.49-0.51 is inside the
   plug's range 0.354 + rho < a' < 1 for rho <= 1/8).  Re-run ONLY those five cells with the plug obstacle added
   to the box test (import cert263, wrap check_box; A260's plug code), certs under attempts/A265-strip-plug/certs
   with their own index + an own verifier (bisect-on-disagreement as A259's fixed verify259.py); the same for WE /
   WS cells that come out OPEN in A263's index when you look.  If a leaf stays OPEN with the plug, evaluate it by
   exact region search: a real miss is a counterexample to the independent-tilt room -- draw it.
3. Gap count: close "1 + w - sec <= e < sec" and unequal tilts for the non-serving gap, or state exactly what is
   left; the count "> 3 free squares" was the coordinator's guess -- derive the true count from GAP-CELL +
   STRIP-CHAIN + the unserved-slot square [T] and say whether it exceeds 3 on the window.
4. Update k0_route.md s.13's chain list with the new tags; say plainly which links are still [M] / [C] / waiting.
   Lean: Statements/Open/StripPlug.lean (build + audit 0 sorry, no "(no output)" rows; AUDIT.md rows; one import
   line after fetch + merge).  Deliverables: docs/proofs/strip_plug.md, the Lean file, code/, results/, certs/,
   pages in docs/residue_map/campaigns/A265-strip-plug/ (the strip with A, C, X; an OPEN leaf before / after the
   plug; geometry-checked, a note per panel saying what it IS, slivers with a 10x inset, undecided grey stipple
   never green), registry row, LOG entry, ledger s.4 note.  Report once (<= 20 lines).  EXIT.
