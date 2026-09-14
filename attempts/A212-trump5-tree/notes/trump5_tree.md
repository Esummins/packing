# A212 -- the TRUMP5 TREE: A211's coarse tree with a Trump-containment gate, the tube leaf, lambda = 1 (2026-09-14)

The PI (2026-09-13 00:40): *"eventually every node has to be killed in every direction that isn't trump ... check if
the current node is a parent of trump, and if so, don't try to kill it, just go straight to split ... then the leaf
discharge rules + trump basin clear out everything that isn't trump."*  Code: `code/trump212.py` (the image, the
gate, the tube check, the aligned split), `tree212.py` (Tree212 over A211's Tree211), `run212.py`; A211's chain copied
UNCHANGED at b06a8203 into `code/` (coarse211, tree211, leaves211, rsplit211, inherit211, startload211, fig211, the
A204-A210 modules).  Everything of A211 `notes/coarse_tree.md` (S1-S7, Lemmas CT, INHERIT, POCKET, ROLE-SPLIT) is kept
verbatim; the three additions below are stated BEFORE use.  Labels: [T] proved, [S] supported, [M] measured, [C] open.

## 0. The frame  [T]

A trump5 page is a c0 node of A60's tree at side s0 = 969271/250000 with the class pins {BL(0,0), BL(1,0), BL(0,1),
BR(0,0), TR(0,0)} = Trump's squares 0, 1, 3, 2, 5 and the H box (A60's YES box); f1_L10_0003 carries a sixth pin
(Trump's square 7).  The pages are run at PAD 0 ONLY: lam = 1, F = P, every hypothesis about a packing P at side s0
itself (A209's rule: an s0-only statement; the window instantiation of a pad-0 verdict stays pending as for every
pad-0 verdict of A209 / A211, and no window-pending bookkeeping is carried here).  The Trump packing z-hat (A22's jam,
side s-hat = 3.8770835900... < s0; the exact algebraic squares in `attempts/A03-upper-reconstruct/trump11_exact.json`,
60 digits, rational centre z0 with |z-hat - z0| <= 1e-50) is EMBEDDED at s0 as A53 / A60 `substrat.trump_realizes` do:
squares 2 and 5 (the R-family pins) moved outward onto their slots (s0 - 1/2, 1/2) and (s0 - 1/2, s0 - 1/2), the
other nine unchanged.  Moving 2 and 5 away from every neighbour by s0 - s-hat = 4.1e-7 keeps interiors disjoint, so
z-hat_emb is a packing at side s0 with the five class pins exactly on their slots; its D4 images g.z-hat_emb
(the container's symmetries at side s0, tilt theta -> theta under a rotation, theta -> 90 deg - theta under a
reflection) are packings at s0 too.  Tilt convention: a page piece (rect x [t0, t1]) is the unit square rotated by
theta = 2 atan t counter-clockwise (multibox `_pose_outlines`), A22's theta; tilts are read modulo 90 deg.

## 1. GATE `contains_trump(N)`  [T for what it claims; a heuristic for where it is applied]

**Definition.**  N contains the image g.z-hat_emb when there is an injective assignment of its named squares to
the image's eleven squares such that (i) every pin box holds the centre of an upright square of the image (exact
rationals, tolerance 1e-6 outward: the R-family shift and the 1e-50 rounding); (ii) H and every instantiated role F_i
are assigned distinct squares whose (centre, t) lies in one of the role's CURRENT pieces (rect and t-bin, 1e-9
outward); (iii) every slot the node names the role at (`forced_H`, `role_slots`) is met by the assigned square --
the closed unit square meets the open widened slot box `wb(p)`, exact separating-axis test on the four axes, a
1e-9 margin in favour of "meets"; (iv) every Rule-NS miss hypothesis (`pg.miss`) holds for the assigned square, with
the margin in favour of "misses".  The gate returns the FIRST g in D4 order with such an assignment (pins force
g = id on the trump5 pages: the pin set is not D4-symmetric).  Row steps, pocket steps and role splits are carried by
the pieces (`apply_branch` / `apply_pocket` / `apply_rsplit` write them into the pieces), so (ii) covers them.

**What it is used for.**  A node the gate accepts is NEVER submitted to a kill rule (rule CC, NO-ROOM's verdict, the
basin clip, S-PAIR): it is branched at once -- A211's row / pair rule, Rule NS, Lemma POCKET (no-room is run ONLY for
its pocket cover, never for its verdict) and the aligned split of s.3 -- so that the image is isolated into one
child per step.  Skipping a kill rule proves nothing and cannot make a DEAD claim: sound.  A coarse / exact cascade
round IS run on such a node (its clips are sound necessary conditions; on a node that truly contains a packing they
only shrink the pieces towards it), and if a cascade or a rule ever returns DEAD on a gated node the tree records
`gate_conflict` and leaves the node ALIVE (a discrepancy between the gate's arithmetic and a rule: never a kill).
Every node record carries `trump_gate` = dict(contains, g, assignment, checks, seconds); the page row carries the
gate hits.  A false negative of the gate costs only wasted kill attempts (every rule stays sound); a false positive
costs only a skipped kill.  Soundness of the tree does not depend on the gate.

## 2. TUBE LEAF (D)  [T]

**Lemma TUBE-LEAF.**  Let N be a pad-0 node whose eleven squares are all named (5 or 6 pins, H, the instantiated
roles; no anonymous square left), let g in D4 and an assignment as in s.1, and suppose every piece of every named
role lies inside the box of half-widths (r_c', r_theta) about its assigned square of g.z-hat_emb: centre rect inside
[c_x - r_c', c_x + r_c'] x [c_y - r_c', c_y + r_c'] and the t-bin's theta-interval [2 atan t0, 2 atan t1] (mod 90
deg, under the reflection rule) inside [theta_i - r_theta, theta_i + r_theta], with r_c' = r_c - 2 (s0 - s-hat)
(exact rationals; the 1e-50 rounding of z0 absorbed by a 1e-9 margin).  Then (a) every packing P at side s0
satisfying N has each square within (r_c', r_theta) of g.z-hat_emb -- a LOCALISATION, the (D) leaf of
`docs/proofs/k0_route.md` s.4.2; (b) for every m in [s-hat - T, s-hat] and every packing P' at side m whose dilate
Delta_{s0/m} P' satisfies N's pieces, P' = g.z-hat at m = s-hat and no P' exists at m < s-hat, by Theorem T1
(`docs/proofs/contraction_tube.md`) on the SCALE-ray tube certificate `certs/tube_scale_T5.71e-2_window.json`
(T = 571/10000 >= s-hat - 3.82, r_c = 1/625, r_theta = 21/10000, r_s = 0; `certs/verify_tube.py`).
*Proof.*  (a) P's squares are its named roles' poses, each in some piece.  (b) Let F = Delta_{s0/m} P' satisfy N and
c_F its centres; c_{P'} = (m/s0) c_F.  With c_F = c_emb + w, |w| <= r_c': c_{P'} - (m/s-hat) c-hat =
m c-hat (1/s0 - 1/s-hat) + (m/s0)(c_emb - c-hat) + (m/s0) w, and |c-hat| <= s0, |c_emb - c-hat| <= s0 - s-hat give
|.| <= r_c' + 2 (s0 - s-hat) = r_c.  Tilts are unchanged by the dilation.  So g^{-1} P' = z-hat - t v_scale + w' with
t = s-hat - m in [0, T], |w'_c| <= r_c, |w'_theta| <= r_theta, w'_s = 0: a feasible point of Tube_scale(T, r) at side
m <= s-hat, and T1 gives m >= s-hat, i.e. m = s-hat and g^{-1} P' = z-hat.  []
The leaf is recorded `TRUMP-TUBE` -- NOT a kill (the node holds the image): a page verdict `TRUMP-TUBE` means every
branch is DEAD or a tube leaf, i.e. the page's residue at s0 is the Trump image's basin and nothing else.  The
certificate `certs/trump5tree212_<nid>.json` carries, per tube leaf, g, the assignment, the radii, and per role the
exact containment margins.  The uniqueness clause of (b) is what `unique_transfer.md` s.3 needs from trump5.

## 3. Reaching the tube: the ALIGNED split  [T]

At a gated node with all eleven squares named whose pieces do not yet fit the tube box, Lemma ROLE-SPLIT (A211 s.5)
is applied with the cut CHOSEN AT THE TUBE WALL: for the role r and coordinate u with the largest excess of its hull
over the box, m = c_u + r_c' (when the hull exceeds the box above) or m = c_u - r_c' (below); for the tilt
coordinate m = tan((theta_i +- r_theta)/2) rounded outward to a rational.  Lemma ROLE-SPLIT allows any m inside the
hull, so the two children are exhaustive and sound; the child containing the image is the one the gate accepts, the
other child is a non-Trump node and goes through the leaf rules from the top.  Two cuts per coordinate, six per role,
at most 36 aligned cuts on a page (`TRUMP_SPLIT_CAP`; counted apart from RSPLIT's per-role cap of 4 and not charged
to the depth cap, as in A211).  The depth (number of aligned cuts) at which the tube leaf is reached is recorded
(`tube_depth`).  Where anonymous squares remain and no pocket cover exists (k < 9), the gated node is left ALIVE with
the reason recorded: the tube is unreachable without a lever that names the last squares.

## 4. lambda = 1, no pad  [T]

Every page runs pad 0 only (`--pads zero`): the leaf rules at their sharpest (rule CC with lam = 1, Theorem FC's
slot boxes unpadded, the basin rows of the class where they exist), no G1 run, no window-pending label in the row --
the row's verdict is DEAD / TRUMP-TUBE / ALIVE and is an s0-only statement by construction (s.0).  Lemma INHERIT is
kept (A205 / A206 / A209 / A211 certificates are merged when they exist; for the c0 pages none exist, and A199's
seal rows -- `attempts/A199-corner-seal/results/seal199.jsonl` -- name no trump5 page, so the pages start from the
plain root); A185's and A189's c0 artefacts are not path-keyed and are not inherited.

## 5. [M] Gate at the roots (before the test)

Of the 13 alive trump5 gallery pages only `f1_L10_0003` (H box [1.687, 1.689] x [1.959, 1.960] x [40.09, 40.25] deg,
the ladder node pinning Trump's square 7) contains a Trump image at the root; the 12 c0_* pages' H boxes hold no
square of any D4 image (A60's `trump_realized` = False on every alive record agrees), so on them the gate is false
at every node and the tree is A211's pad-0 tree with the sharper rules.  The test of s.6 measures both.

## 6. [M] c0_Y1033 at wall 900 s -- filled after the test (see results/progress.md and the report)
