# A266 -- the last two [C] links of the k0 chain at n = 11: STRIP_2 for tilted C (certify the 5-parameter box) and
# CAPACITY-2 on the non-serving gap.  (2026-09-22.)
Fable.  LAUNCH-AND-EXIT -- NEVER wait for a detached run.  Ops: short responses, files <= 250 lines, no monitors, no
interim messages, explicit-pathspec commits (fetch + plain merge only), PYTHONDONTWRITEBYTECODE=1, ONE heavy python
process at most (BelowNormal, affinity 0xFFFF; sub-minute helpers fine); detached launches call Git Bash by explicit
path.  RUNNING, never touch: the k5 pass loop, A256's loop256, A257's pilot257, the status loop, A259's verify
rerun, A262's chain, A263's chain, A265's lane (run265b.sh) and all their certs.
Read first: docs/proofs/strip_plug.md (A265: STRIP_2 -- two-square, s-free lemma on (h_u, h_v, theta_C; y_X, phi_X):
C, X and the wall seal the strip T_u minus C; [T] hand proof for flat C in standard orientation via the chord /
tip / column-collision argument; [C] tilted C and the mirrored orientations; Lean strip_two [C],
strip_of_two_obstacles [T]; the non-ADJ ROOM miss at s-hat (+0.025, e' = 0.6): a bare-ring witness, not a k0
counterexample; gap count = 2 free squares in the gap; the chain needs CAPACITY-2: two disjoint free squares both
missing O; Lean gap_needs_two_misses), three_lemmas.md (STRIP-CHAIN, GAP-CELL, BLOCKER-SIDE), open_pairs.md
(non-ADJ; P2 x WE x WS), normal_room.md (PAIR, HOLE-ONE tilt form, TOOTH), k0_route.md s.13 (the chain).

## Task
1. STRIP_2 general.  Extend the hand proof to tilted C (theta_C in (0, 45)) and the mirrored orientations if the
   same mechanism carries (chord < h_u => strip point in a tip; the tip argument with C's tilt); where it does
   not, certify the 5-parameter box by interval branch-and-bound (own verifier, bisect-on-disagreement; benchmark
   first; the agent priced it 1-3 CPU-h -- launch detached).  Result: STRIP_2 [T] / [T-computed] on the JAM
   domain => with A264's jam_sector_of_strip and A262's pair3 (check pair3's index: done? verified?) the BL sector
   closes => NO-JAM(11)'s sector part.  Then say what NO-JAM(11) still lacks (indirect jams, FLOAT2: read A262's
   chain3 outputs if landed).
2. CAPACITY-2 on the non-serving gap: two interior-disjoint free squares both missing O in a ring whose wall has
   an unserved slot (gap e up to 1.169).  A265's witness has ONE miss; show a second disjoint miss is impossible:
   the two misses would both sit on the centre line near that wall (the miss region is the notch), and two unit
   squares in the notch need width >= 2 > e; or the second miss is elsewhere and A263's P2 x WE x WS bound the
   other three walls' notches.  Prove it or certify it (the miss region's width as a closed form in e, tilts);
   test on A265's witness and A263's non-ADJ rows; draw the miss region.
3. Update k0_route.md s.13 with the new tags; list what remains [C] / [M] / waiting, and which running chains
   must land (A259 verify, A262 pair3 / chain3, A263 WE/WS + slab jobs, A265 lane) for the chain to be all
   [T] / [T-computed] on [3.82, s-hat].  Lean: Statements/Open/LastTwo.lean (build + audit 0 sorry, no "(no
   output)" rows; AUDIT.md rows; one import line after fetch + merge).  Deliverables: docs/proofs/last_two.md,
   the Lean file, code/, results/, certs/, pages in docs/residue_map/campaigns/A266-last-two/ (the tilted-C strip
   with the tip argument; the gap's miss region with the two-square impossibility; geometry-checked, a note per
   panel saying what it IS, undecided grey stipple never green), registry row, LOG entry, ledger s.4 note.
   Report once (<= 20 lines).  EXIT.
