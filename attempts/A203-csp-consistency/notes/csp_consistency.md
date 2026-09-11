# A203 -- H-consistency and piece-level pair compatibility in the fast count: the lemmas, for any n

The layer is the PI's.  Two readings of 2026-09-10 fixed it: on `fast30_k5_16_interior_Y0839.svg` (18:20) --
*"looking at how tight the BR and TR meeter options are, it seems like clipping H on both of those (and settling the
mutual clip) should basically kill all the options there ... Is there any way we bake something into the fast step to
help kill these super small slots?"* -- and on `fast30_k5_16_interior_Y0191.svg` (17:40) -- the TL(1,0) meeter pair
passes the hull tests (CN 1.056) but no pair of MEETING poses is disjoint: *"Is the geo pre-check ensuring that there
are options with enough distance between them?"* (`attempts/A202-fast30/notes/PI_pair_table_pieces.md`).  The
coordinator's grid check on Y0839 (`y0839_csp_gridcheck.py`) made the first reading exact: the count's witness option
in cell 10 has 78 admissible meeting poses and NOT ONE is disjoint from ANY admissible H pose, which the pairwise hull
table (A1 / CN / MK) cannot see.  So the fast count is made a small CSP on PIECES: every option must be compatible
with H (H exists), H must be compatible with some option of every slot a free square must meet, and a cover must
admit a COMMON H piece.  Every rule below is a SOUND necessary condition; an undecided pair is compatible; the
verdicts are `[C: closed-form trace]` -- no verifier clause exists yet (the certificate is the JSON trace).

Setting and notation = A202's `notes/fast30.md` s.0 (pieces = closed centre rect x closed tilt sub-bin; w(a) =
|cos a| + |sin a| the axis-parallel width of a unit square tilted by a; pins with certified cores; H = the conditioned
square with its record box x tilt window; forced slots p with widened open boxes B_p+, Theorem FC).  Code:
`code/csp203.py` (rule S, the node trees, the cached compatibility), `satbatch203.py` (rule S vectorised),
`csp203b.py` (units, option piece sets, the feedback), `csp203c.py` (masks, settle, the mutual clip), `count203.py`
(the count with the H-mask), the copies of A202's `fast30.py` / `fast30b.py` / `rules202.py` / `fig202.py`
(modified only here), `fig203b.py` (the page), `run203.py` / `run203.sh`.

## 1. Lemma PC (piece compatibility, rule S)  [T]

Let F, G be interior-disjoint unit squares with centres c_F, c_G and tilts t_F, t_G.  Then for some axis direction
phi in {t_F, t_F + 90} or {t_G, t_G + 90} (the square whose axis it is called A, the other B):

    |(c_G - c_F) . (cos phi, sin phi)|  >=  1/2 + w(t_B - phi)/2.

*Proof.*  Two convex polygons with disjoint interiors have a separating line parallel to an edge of one of them
(the separating-axis theorem); the projections of A and B on that edge's normal have disjoint interiors, so the
distance between the projected centres is at least the sum of the projected half-widths: 1/2 for A on its own axis,
w(t_B - phi)/2 for B (the projection of a unit square on a direction at angle a to its axes has half-width
(|cos a| + |sin a|)/2).  []

**Rule S (the piece-pair test).**  For pieces P_1 = R_1 x [a_1, b_1] and P_2 = R_2 x [a_2, b_2] let D = R_2 - R_1
(a closed rect: the centre differences d), with corners (r_k, alpha_k) in polar form.  For a tilt sub-interval
[p_0, p_1] of piece i's bin the projection distance on piece i's axes is bounded by

    max_{d in D, phi in [p_0, p_1]} |d . a(phi)|  <=  max_k  r_k cos( dist([p_0 - alpha_k, p_1 - alpha_k], 90 Z) )

(|d . a| is linear in d, so maximal at a corner of D; on the two axes phi, phi + 90 together |cos| v |sin| =
cos(dist to the nearest multiple of 90)), and the other square's half-width is at least 1/2 + w_min([a_j - p_1,
b_j - p_0])/2 (w is 90-periodic and concave between multiples of 90, so its minimum over an interval is at an
endpoint, or 1 when the interval contains a multiple of 90).  If the bound is < the half-width for every
sub-interval of BOTH bins (sub-intervals of width <= `step` = 4 deg; every comparison with the margin EPS = 1e-9 on
floats of outward-rounded rects), Lemma PC has no axis: NO pose pair of the two pieces is interior-disjoint -- the
pair is EXCLUDED.  Lemma CN is the special case "every corner of D has r_k < 1"; rule S exceeds CN only through the
tilt coupling (up to 1/2 + 1/sqrt2 = 1.207); beyond that distance no pair can be excluded (the fast pre-filter).
`csp203.sat_dead` (scalar), `satbatch203.sat_dead_batch` (numpy over a block of pairs; the sub-interval count is the
block's maximum -- finer, still sound).  Fuzz (`scratch/fuzz203.py`, 6000 random pairs at centre distance 0.85-1.25,
bins <= 20 deg): 2872 pairs declared dead, 300 random pose pairs + the 64 corner/endpoint pose pairs each: **0
refutations** (2026-09-10).

**Hierarchy.**  A node = (hull rect, list of tilt intervals, children); the test on a node pair is rule S over every
interval pair (a superset of the pieces: sound); a node pair is COMPATIBLE when some leaf pair under it is not
excluded, evaluated top-down with the first compatible leaf pair stopping the search, and cached per node pair and
per leaf block (`csp203.Compat`).

## 2. The variables (any n)

* **H's units.**  A202's alive H pieces (its box split nsub_h x nsub_h, tilt window in nbins_h bins, refined 2
  levels under P / W / the meet clip) grouped by their depth-`ud` ancestor (ud = 1: at most 8 x 8 x 8 = 512 units);
  a unit is a node whose leaves are its alive fine pieces.  H's units never grow; a unit dies with all its pieces.
* **An option row's pieces.**  A202's row (g, S) (cell g, slot set S) gets the piece set  P(g, S) = the intersection
  over p in S of the surviving pieces of slot p in cell g  (dyadic pieces: the intersection of two lists is the
  finer piece wherever one contains the other, `csp203b.inter_pieces`).  *Sound:* a pose of a free square with
  centre in g meeting every B_p+ (p in S) lies in a surviving piece of every slot p in S (each slot's rules are
  necessary conditions on a meeter of p), hence in P(g, S).  A row with P(g, S) empty is dropped.  The row's node:
  hull -> coarse groups (sub-rect x coarse tilt bin) -> the pieces as leaves.

## 3. Lemma HC (H-consistency)  [T]

In every packing of the page H exists, so a free square realising the row (g, S) has a pose in P(g, S) that is
interior-disjoint from H's pose, which lies in some alive H piece.  Hence: **if no piece of P(g, S) is compatible
(rule S) with any alive H piece, the row (g, S) is dead** -- and with it every row (g, S') with S' a superset of S
(its poses meet every slot of S too).  For a SINGLETON row (g, {p}) this kills every surviving piece of slot p in
cell g (each such piece IS the row's piece set), which feeds A202's unions, caps and Theorem FC.  Letter **H** on
the page (rule "H" in the certificate).

## 4. Lemma MC (the mutual clip)  [T]

Let p be a forced slot (Theorem FC: two distinct non-pin meeters of B_p+) such that no conditioned square other
than H may meet B_p+ (A161's miss test on the other roles' boxes, `roles_reach`).  Then at least one FREE square
meets B_p+ (Corollary FC-count: the non-pin squares are H and the free squares, and two distinct meeters are
needed), i.e. some row (g, S) with p in S is realised by a free square interior-disjoint from H.  Hence: **an H
unit compatible with no alive row containing p is dead** ("MC:p").  Iterating Lemma HC and Lemma MC (rows die ->
units lose their cover -> units die -> rows lose their partners -> ...) reaches a fixed point in milliseconds; H's
surviving pieces are the alive units' pieces, H's box is their hull (never grown), and A202's H-dependent rules
(C, M, L) re-run on the shrunken H in the next round (the fixed point with the option build).  If every unit dies
the page is DEAD (no pose of H is compatible with the free meeter some slot must have).

## 5. The SETTLE refinement (the PI's "settling the mutual clip")  [T]

For a row whose compatible leaf pairs (option piece, H piece) are few (<= 400), each pair is refined: the option
piece is split 2 x 2 x 2 (centre quadrants x tilt halves) up to 3 levels, every child re-tested by A202's rules
(P pins, W walls, C / M against H's hull and groups, L chord rows; R reach for every slot of S; A161's exact miss X
for every slot of S) and by rule S against the H piece; a child failing any test holds no pose realising the row
disjoint from that H piece (each test is a necessary condition; a child's poses are a subset of the parent's, and
the inherited chord bounds are lower bounds for the child).  A pair all of whose children die at some level is
EXCLUDED; when every pair of a (row, unit) dies the unit's bit leaves the row's mask; a row whose mask empties is
dead -- letter **F**.  Budgets: fan-out <= 64 surviving children (else the pair stays compatible), 2 s per row,
6 s per round; results cached per (piece, H piece, S).  Undecided = compatible (sound).

## 6. Theorem COUNT-CSP (the count with the H-mask)  [T]

Theorem COUNT (A198) / COUNT-PAIR (A201) with two more necessary conditions on a cover: (i) the chosen H row
(g_H, S_H) names the units of H that may sit in g_H and meet every slot of S_H (A202's `role_options` clip; the
mask m_H), and every chosen free row (g, S) has its compatibility mask m(g, S) = the alive units with a compatible
piece; a cover needs  m_H AND m(g_1, S_1) AND ... AND m(g_k, S_k) != 0  (H's actual pose is ONE piece, compatible
with every chosen free square) -- the search ANDs along the branch and prunes on empty; (ii) two chosen free rows
must be compatible on their PIECE sets (rule S hierarchically; Lemma A1 on the hulls kept), so a slot's demand-2
pair is tested over the MEETING pieces of the two rows, never over cell hulls (the PI's Y0191 reading).  If the
capped exact search finds no cover, the page is DEAD (`count203.count_search`; prunes counted per rule).  The
bar-H counts (H forced at p when no cover without H at p exists) run with the same masks.

## 7. Soundness checks and the audit

* Fuzz of rule S: s.1.  A202's rules P / W / C / M / L / R / X / meet: A202's fuzz (`fast30.md` s.4).
* Audit of the kills by sampling (`scratch/audit203.py`): for every dead row (H / F) sample admissible poses
  (container, pin cores) on a grid over the row's hull x its tilt intervals that meet every slot of S, and every
  admissible H pose on a grid over H's RECORD box x window; a sampled disjoint pair would refute the kill.  Y0839
  g1: 6 dead rows, 216 / 11 meeting admissible poses each, 2975 H poses, **0 refutations**; Y0191 g1: see the log
  (`logs/audit_Y0191_g1.log`).
* Kept rule (A202): a stage-0 kill of a page that the exact tests leave alive is a bug until proved otherwise; the
  CSP adds constraints the exact table never had (H-consistency), so its kills are audited by sampling first.

## 8. Y0839 (both pads)

The witness option of A202's count -- cell 10 serving BL(1,0) + BR(0,1) + BR(1,0), hull [2.190, 2.226] x
[0.698, 0.770], 11 pieces (all at tilt 62-71 deg: the only poses that reach BR(0,1)'s box) -- survives the
node-level rule S against 11 of H's 512 units (nearest at max centre distance 1.0025: two poses at tilt 64.01 in
opposite corners of the two pieces are separated along the common axis by 1.0005 -- but the option's corner pose
does not meet BR(0,1)); the SETTLE refines its 133 compatible leaf pairs, all die (R / X / S on the children), and
the row is DEAD by **F** in 315 ms (g1) -- the coordinator's grid conclusion, reproduced in closed form.  The
singleton (10, BR(0,1)) dies the same way (15 pieces killed), and cell 7's BR(1,0) rows (330 pairs).  The mutual
clip kills 87 of H's 512 units (MC:BR(0,1)).  The count then finds another cover (cell 15 for the triple), and the
bar-H count forces H at BR(0,1) (A202 forced nothing).  Verdict ALIVE at both pads: 28.2 s / 25.5 s (A202's stage
0 is 16-17 s of it; the CSP round 1 is 7.7 s: build 0.5 s, masks 2.9 s = 84,714 node tests + 1.86 M leaf pairs in
numpy blocks, settle 4.2 s; round 2 cached, 2 s).

## 9. The table over the pages A202 left alive at stage 0

(filled by `code/report203.py` from `results/csp203.jsonl` at the end of the population run -- see s.10)
