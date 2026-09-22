# A264 -- THE THREE REMAINING LEMMAS of the k0 exclusion at n = 11: the JAMMED SECTOR, the NON-SERVING GAP, and the
# NEAR-FLAT CUBE.  (PI, 2026-09-22: "brief the three remaining lemmas".)
Fable.  LAUNCH-AND-EXIT -- NEVER wait for a detached run.  Ops: short responses, files <= 250 lines, no monitors, no
interim messages, explicit-pathspec commits (fetch + plain merge only), PYTHONDONTWRITEBYTECODE=1, ONE heavy python
process at most (BelowNormal, affinity 0xFFFF; sub-minute helpers fine); detached launches call Git Bash by explicit
path.  RUNNING, never touch: the k5 pass loop, A256's loop256, A257's pilot257, the status loop, the certificate
chains of A259-A263 and their certs (A259's verifier is being re-run by its own agent -- do not edit A259).
Read first (in this order): docs/proofs/no_jam.md (A262: corner types PAIR / THIRD / JAM / FLOAT2; the count kills
nothing, ROOM(S_min) <= 1 => n <= 9 [T]; JAM rings exist on the whole window, every free square contains O [M];
sectors BR/TR = A259's PAIR, TL = pair3 (launched), BL = the 7-parameter `jam` kernel priced 15-500 CPU-h -> pilot
only; HELD-JAM retreat cone; obligations N1-N9), docs/proofs/open_pairs.md (A263: the miss-O test factors P2 x WE x
WS with the PRINCIPAL-NORMAL clip; (c) non-ADJ: a non-ADJ wall carries a free square in its unserved slot [T, Lean
nonadj_free_meeter] but ROOM <= 1 is [F] as a bare-ring statement when the gap e reaches 1.169 -- a flat unit cell
fits between s1 and W (nonadj_gap.svg); (d) the slab: mixed-sense margin ∝ eps only in the all-near-flat cube,
minimiser = the domino pinwheel b_w = 1, a_w = s - 3; the first-order lemma "a near-flat mixed corner forces b >= 1
+ eps(1 - a) - O(eps^2)": mechanism [T], constants [C]), box_meeters.md (A261: P1+ -- in a Phi1-maximiser a family
of disjoint WALL-TOUCHING cells of any pose with |M(Pi)| <= |Pi| is met by touchers only; SAME-WALL; JAM witness;
[T] no closed-LP certificate reaches a flat wall), normal_room.md (A259: MISS => corner PAIR; HOLE-ONE tilt form;
TOOTH; WEDGE), locked_wall.md (A260: PLUG -- a square reaching the corner box swallows the START square's lowest
vertex; OPEN-TOOTH; LIFT), normal_ring.md (P1-P4), common_sense.md s.2 (VALUE-WLOG; NORMAL-CELL), ring_swap.md
(CELLS on cells of any pose), peel.md (BAND-COUNT, POKE).

## Lemma 1 -- JAMMED SECTOR (A262's N1).  The BL sector of a ring with one JAM corner: obstacles A (floor toucher,
tilt phi), C (the floater, same-ish tilt, 0.72 off the wall), X (the wall square above C, the next box's meeter).
The 7-parameter box tree is too expensive; find the analytic statement.  Candidates: (i) C's far vertex reaches
~1.94 toward O, so C is a BIGGER obstacle than a toucher -- the region left for a free square between C and the
opposite rows is contained in A259's PAIR region for a fictitious toucher at C's outer edge (monotonicity of the
obstacle: a free square avoiding C avoids anything inside C); state and prove the comparison, then the sector is
A259's certificate again with C's outer edge as the "END square"; (ii) PLUG-type: any free square dipping into
the sector below height 1 contains a named vertex of A, C or X.  Test on A262's 34 JAM rings (results/) and its
adversary rows before proving.  Also settle N3 (indirect jams: a non-toucher blocker), N5 (FLOAT2: two floaters
at one box -- by SAME-WALL + P1+ on the wall-touching cells under them?), N6 (adjacent j = 2: none found -- prove
or certify with the comparison), so that NO-JAM(11) becomes [T] / [T-computed] on [3.82, s-hat].

## Lemma 2 -- NON-SERVING GAP (A263's O3).  A wall whose facing toucher W does not serve s1's slot (non-ADJ): the
gap e between s1 and W can reach 1.169 and a flat unit cell fits in it.  Room cannot close it; STRUCTURE must:
the gap cells are WALL-TOUCHING cells of any pose (flat, or at s1's tilt), so P1+ applies -- a family of them met
by <= |Pi| squares is met by touchers only -- and NORMAL-CELL / CELLS exchange a free square onto a gap cell,
raising Phi1 (a new wall toucher) or Phi2 (a longer row).  State Lemma NO-GAP: in a Phi-maximiser, every wall gap
between two touchers admitting a unit cell is met by >= 2 squares that are not the two touchers, and derive the
count: the free square in the unserved slot [T] + the gap's >= 2 meeters + ... > 3 free squares, or the gap
closes to e < 1 - (the TOOTH regime where A263's certificates hold).  Test on A263's non-ADJ rows and the
corner-feasible example in nonadj_gap.svg (does the exchange apply to it?).

## Lemma 3 -- NEAR-FLAT CUBE (A263's O4 / A261's slab).  All four walls at tilts < 0.703 deg and mixed senses:
the LP relaxation degenerates because the domino pinwheel (b_w = 1, a_w = s - 3) is closed-feasible at every side.
Make the first-order lemma exact: for tilts eps_w in [0, eps0], a mixed-sense corner forces b >= 1 + eps(1 - a) -
K eps^2 with an explicit K (Taylor with remainder on the corner constraint E(a, alpha, b, beta) from A258's
closed forms), hence the ring needs side >= 3.9347 - K' eps0^2 ... > s-hat for eps0 = 0.703 deg = 0.01227 rad;
state the exact inequality, prove it, and certify the constants by interval arithmetic on the cube (one small
box; own verifier).  Also the all-one-sense near-flat cube: A261 says the one-sense family reaches 0.7-1.4 deg
on one wall at s-hat -- confirm that A259/A263's room certificates cover it (their tilt cells start at 0).

## Task
Do Lemmas 1-3: proofs first, tests on the existing corpus / adversary rows, certificates (own verifier, benchmark,
detached if <= 30 CPU-h total) only where the analysis stops.  Say plainly for each: [T] / [T-computed] / [C] and
on which side range; then the FULL CHAIN for k0 at n = 11 on [3.82, s-hat] as a numbered list of statements with
their tags and files (normal form -> meeters split -> NO-JAM -> one sense / rows of two / no flat row (+ slab) ->
locks and open pairs -> room -> FAMILY-STUCK-EXIST(11) -> k0_00 via CELLS / K0-FREE), marking every link that is
still [M] or [C] or waiting on a running chain -- this list is what the PI reads next.  Deliverables:
docs/proofs/three_lemmas.md (or one file per lemma), Statements/Open/ThreeLemmas.lean (build + audit 0 sorry, no
"(no output)" rows; AUDIT.md rows; one import line in Statements.lean after fetch + merge), code/, results/,
certs/, pages in docs/residue_map/campaigns/A264-three-lemmas/ (the jammed sector with the comparison obstacle;
the non-serving gap with the exchange; the near-flat cube's corner; geometry-checked, a note per panel saying
what it IS, slivers with a 10x inset, undecided grey stipple never green), registry row, LOG entry, ledger s.4
note; update docs/proofs/k0_route.md (or the ledger's k0_00 row) with the chain list.  Report once (<= 25 lines).
