# A280 -- the DROP LEMMA at steep C: A273's OPEN layer (theta >= 25 deg) was a MISSING PRUNE, not a weak drop test and not a miss (2026-09-24)

Tags: [T] proved, [T-prose] proved in prose, [T-computed] finite computation with its own independent check, [M]
measured, [C] conjecture, [F] false.  Code `attempts/A280-drop-steep/code/`, results `results/`, certificates
`certs/`, page `docs/residue_map/campaigns/A280-drop-steep/drop_steep.svg`.  A273's code imported, never edited.

## 0. Verdict

* **DIAGNOSIS: weak relaxation -- in PRUNE, not in the drop test.**  A273's `drop4273.prune4` checks the h_v window
  and "X hits int C" but NOT the first half of H2 (int X meets int T_u).  Every A273 OPEN leaf examined lies OUTSIDE
  H1-H3: X sits wholly above T_u (exact area X n T_u = 0), with the dip D in [0, 0.0002] (c6_2) / [0, 0.004] (c7_6,
  c8_3) against the (D-low) bound (c - sin phi) tan(min(theta, phi)) = 0.150 / 0.184 / 0.136 (strip_jam.md s.2, [T]).
  Counts (`diag280`, results/diag280_<cell>.json): c6_2 (theta 30-35, phi 10-15; not capped, 10 OPEN leaves at WMIN):
  10 / 10 pruned by DLOW; c7_6 (35-40 x 30-35): 191 729 of 191 732 OPEN leaves pruned by DLOW, the 3 others are the
  big never-explored boxes left by the 400k cap; c8_3 (40-45 x 15-20): 189 943 of 189 949, 6 big boxes left.
* **Exact slack at the open-leaf centres** [M] (slack273: exact support-function gap, grid + Nelder-Mead): NEGATIVE
  everywhere -- -0.00013 .. -0.00015 (c6_2), -0.00006 (c7_6), -0.00018 .. -0.00020 (c8_3) on the DLOW slivers
  (the drop lemma holds there but with margin -> 0 as D -> 0: X's bottom edge descends onto C's top line from above,
  a zero-margin limit OUTSIDE H1-H3), -0.017 .. -0.324 at the centres of the big capped boxes.  **No positive
  slack: no counterexample to the DROP LEMMA at steep C**; STRIP_2 needs nothing new.
* **The second zero-margin spot** (found by the strengthened tree's first benchmark, c7_6 before LOWF): h_u -> 1 on
  the (D-low) boundary.  [M] slack -0.049 (h_u 0.9), -0.005 (0.99), -0.0012 / -0.0008 (0.9999, D = D-low + 10^-3 /
  10^-4), theta 40, phi 32.88: q = (1/2, L_h) at the wall, D(q, 1/2) touching the wall, C's left vertex (h_u, L_h)
  and X's bottom vertex -- the axis-parallel unit square between the wall and C (page (c)).  It is outside H1-H3 by
  **Lemma LOW** (ring_domain.md (F4)): L_h >= 1.173 at theta 40 gives h_v >= 0.407 while the open box (A266) needs
  h_v < (c + s - sc - h_u c)/s < 0.235 at h_u = 1: h_u <= 0.854.  A273 had dropped LOW on purpose (its Lean core
  then covered alpha <= 45 deg only); A271's follow-up (F4) covers every tilt of A, so it is used here.
* **The strengthened test** = A273's box test unchanged + three sound prunes (`prune280`): DLOW, SEP (separating
  axis between X and T_u over the box), LOWF (Lemma LOW, full range).  **Benchmark** (5 cells, all CERT, tree280):
  c6_2 179 boxes 0.5 s, c7_6 69 boxes 0.2 s, c8_6 (40-45 x 30-35, not yet run by A273) 223 boxes 0.7 s, c8_3 327
  boxes 1.0 s, c5_4 51 boxes 0.2 s -- against A273's 400 000 boxes / 1 100-2 500 s per cell, OPEN.  verify280 PASS on
  all five (coverage replayed, bisections 0 / 0 / 8 / 8 / 0, 0 disagreements).  [T-computed] for these five cells,
  as `_bench` files (the run re-does them under the plain names).
* **Ring route: not needed** (the steep cells close on H1-H3 directly); (U3)-(U6), (U8) were not checked at steep C.
* **Launched** (gated, detached): `run280.sh` waits for A273's chain to end (no tree273 / verify273 / pages273
  python, no run273.sh bash, three checks 120 s apart), then tree280 + verify280 over the 29 steep cells not CERT in
  index273 (24 OPEN-LAYER + c8_4..c8_8 if A273 leaves them open), one commit per cell, page at the end.  Price
  [M, from the bench]: < 1 s tree + ~10 s verify per cell, ~0.1-0.3 CPU-h in all.

## 1. Why the brief's strengthening would not have helped

* The **LEFT constraint** is already the drop test's Gamma: strip_jam.md (P1) LEFT is exactly "int Q n int Gamma =
  0", Gamma = {h_v <= y <= C_top, x >= l_C(y)} -- drop273 carries it (K2, K5 against Gamma's core).
* The **height case split** adds nothing to the bad-centre set: Q is centrally symmetric about q, so the horizontal
  chord through q is centred at q with half-length >= 1/2; the chord conditions of cases A1 / A2 / M (centre chord
  right of X, left of C, inside the quadrant) are implied by dist(q, Xi or Xi') >= 1/2, dist(q, Gamma) >= 1/2 and
  q_x >= 1/2, which the test already uses; case C-left is dead by Lemma CL and never enters part R / L; A1-left's
  pocket bound X_low - q_y >= (1 - sin phi)/2 uses Q's corners (not only the disc) and was not needed [M: the
  cells closed on the prunes].
* A real strengthening of the test, if ever needed: Q is invariant under the quarter-turn about q, so p's four
  images under it lie in int Q and the drop can be replaced by conv(D(q, 1/2) u {p, p', p'', p'''}) [T] (sound,
  not implemented -- the prunes closed the cells).

## 2. The prunes (sound; tree prune280, verifier verify280)

* **DLOW** [T] (strip_jam.md s.2 (D-low)): int X n int T_u != 0 forces D >= (c - sin phi) tan theta (phi >= theta)
  and D > (c - sin phi) tan phi (phi < theta); pointwise D >= (c - sin phi) tan(min(theta, phi)); box pruned when
  D_hi < (cos th_hi - sin ph_hi) tan(min(th_lo, ph_lo)) (outward-rounded, margin 10^-12).
* **SEP** [T]: an edge normal of T_u'' or X'' with n.(x_i - t_j) of one strict sign for all 16 vertex pairs over
  the box (interval arithmetic) separates X from T_u for every parameter: H2 fails.
* **LOWF** [T-prose + T-computed]: Lemma LOW (F4): (a), (b) L_h >= 1/sqrt2 + tan(45 - theta/2) (Lean `low_core`,
  `lh_gt_one`); (c) L_h > G(alpha, theta) = cos alpha + c - s + (c + s - 1) tan alpha (prose (F4)(c); Lean
  `lh_gt_one_steep` proves only G > 1) -- minimised over alpha in [45, 90) by 1-deg interval pieces + the tail
  (cos alpha > 0): LOWB(theta) = 1.344 / 1.284 / 1.228 / 1.173 / 1.109 at theta 25 / 30 / 35 / 40 / 45 deg.
  h_v >= LOWB - c against h_v < 1, X_top <= s^, the open box: no h_v -> pruned.
* The **verifier** (verify280) re-types all three in mpmath.iv (80 bits), imports none of prune280 / geom273 /
  drop4273, reuses A273's independent verifier (verify273) for the h_v window and the q-cells (inscribed 128-gon
  penumbras, h down to 1/8192) and for the coverage replay; a CERT or PRUNE leaf it cannot re-derive is bisected
  (depth <= 6); still open -> DISAGREE (FAIL, never green).

## 3. What the brief had wrong

1. The weakness was not in the bad-centre set: LEFT is already Gamma and the height split is implied (s.1).  The
   missing pieces were H2's "X meets int T_u" and Lemma LOW in PRUNE.
2. "OPEN-LAYER for every theta in [25, 45] at all phi": c5_0..c5_3, c6_0, c6_1, c7_0 were CERT; 24 of the 67 cells
   indexed at the time were open (c6_2 uncapped, 10 OPEN leaves at the width floor).
3. The brief's second example cell (40-45 x 30-35 = c8_6) had not been run by A273; it was benchmarked directly and
   c7_6 / c8_3 (capped OPEN cells) were diagnosed instead.
4. The ring-domain route is unnecessary at steep C.

## 4. Flags for the next agent

* Both zero-margin spots of the drop lemma found here are OUTSIDE H1-H3 (X above T_u; h_u -> 1 with h_v below LOW):
  any future drop-type tree must carry H2 and LOW in its prune or it will grind there.
* The steep-C certificate now leans on LOW's case (c) intermediate inequality L_h > G(alpha, theta), which is prose
  in ring_domain.md (F4) -- a Lean core for it (`lh_gt_G`) would make LOWF's input [T] in Lean too.
