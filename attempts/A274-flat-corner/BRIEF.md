# A274 -- THE NEAR-FLAT CORNER of STRIP_2: theta_C <= 5 deg and phi_X <= 5 deg, where the strip's margin goes to
# zero like 0.15 theta^2 and no box tree can close it.  Hand proof.  (2026-09-23.)
Fable.  LAUNCH-AND-EXIT -- NEVER wait for a detached run.  Ops: short responses, no interim messages, files in
pieces <= 120 lines per Write, never a single response over ~15k tokens, explicit-pathspec commits after every
piece (fetch + plain merge only), PYTHONDONTWRITEBYTECODE=1, ONE heavy python process at most (BelowNormal,
affinity 0xFFFF; the lab is at its ceiling -- prefer sub-minute helpers).  RUNNING, never touch: the status loop,
A262's chain3, A263's chain, A269's / A270's loops, A273's run273 and their certs.
Read first: attempts/A273-disc-lemma/notes/disc273.md + docs/proofs/strip_jam.md s.0/s.5 corrections (A273: the
DISC LEMMA is false -- exact counterexample theta 8.01 deg, X flat; the DROP LEMMA replaces it: the whole cone
conv(D(q, 1/2) U {p}) misses Xi and Gamma; h_v-invariant, 4 parameters (h_u, theta, D = C_top - X_low, phi); the
box run over 81 (theta, phi) cells is running; the OPEN LAYER: theta, phi <= 5 deg, STRIP_2's own margin ~ 0.15
theta^2 -> 0: at theta = phi = 0 X's bottom edge and C's top edge are collinear and the channel between them has
zero width -- these configurations satisfy H1-H3, so the layer is real), docs/proofs/strip_enclosure.md s.3
(A267's proof under the ring inequalities: on the ring domain STRIP holds -- does the near-flat corner lie inside
the ring domain?  If (U3)-(U6), (U8) follow from H1-H3 when theta, phi <= 5 deg, A267's proof closes the layer
with no new argument), docs/proofs/ring_domain.md (A271: the five derived conditions; the violators of U3-U6 had
X tilted 13-43 deg from C -- so near-flat X and near-flat C may be inside the ring domain automatically),
docs/proofs/three_lemmas.md s.3 (A264's NEAR-FLAT CUBE: the pattern for a first-order lemma with exact constants
-- the mixed-sense margin ∝ eps in the cube; here the margin is ∝ theta^2, so the argument must be second order),
docs/proofs/box_meeters.md (BLOCKER-SIDE), no_jam.md.

## The question
In the corner theta_C, phi_X in [0, 5 deg] under H1-H3: show no unit square Q disjoint from C and X (quadrant)
has an interior point in S = T_u minus C.  Routes, in order of cheapness:
 R1 RING-DOMAIN RESTRICTED: derive (U3)-(U6), (U8) from H1-H3 + theta, phi <= 5 deg (small angles make X's
    lower-right edge nearly flat, the wedge nearly a horizontal slot of height D; the conditions may become
    trivial).  Then A267's theorem applies verbatim.  Check each condition's derivation at small angles first.
 R2 DIRECT: at small angles the channel between C's top edge (tilt theta) and X's bottom edge (tilt phi) is a
    near-horizontal slot of width D + O(theta + phi) at the wall side and narrower toward C; a unit square with
    an interior point in S must enter the slot from the right with a vertex (POKE) -- its depth is bounded by the
    slot's width, and S lies further in than that.  Second-order care where the margin is 0.15 theta^2: the exact
    limit theta = phi = 0 has a zero-width channel (nothing enters), and the first-order terms must be shown to
    open the channel slower than they move S away.  Exact constants; tests against A273's margin curve
    (-0.0003 at 2 deg, -0.00008 at 1 deg) as sanity checks.
 R3 If neither closes on all of [0, 5]^2: the exact residual (drawn) and whether A273's box test can take it
    from a smaller angle (e.g. the layer [0, 1 deg]^2 by R2 and [1, 5]^2 by the tree -- price it).
Also say whether the near-flat corner can occur in a JAM RING at all (C's tilt <= 5 deg with the ring's rows
tilted 10-26 deg?  A262's rings have theta_C 8-25 deg) -- if a ring-level fact excludes it cheaply, record it as
the alternative, but the corner-local proof is the deliverable.

## Task
1. R1, then R2 (or R3); every step [T] with citations; margins tested numerically as sanity checks only.
2. docs/proofs/flat_corner.md; Statements/Open/FlatCorner.lean (theorems where the set description suffices,
   documented axioms otherwise; the consequence: STRIP_2-IN-JAM on [0,5]^2 x the rest; build + audit 0 sorry, no
   "(no output)" rows; AUDIT rows via lean/audit.py; one import line after fetch + merge); page in
   docs/residue_map/campaigns/A274-flat-corner/ (the near-flat channel at 5, 2, 0.5 deg with S and the best
   intruder; geometry-checked, a note per panel, undecided grey stipple never green); registry row, LOG entry,
   ledger s.4 note, k0_route.md s.13 5b.  Report once (<= 15 lines): which route closed, the statement, the
   residual if any, whether the corner occurs in rings, anything in the brief that was wrong.  EXIT.
