# Lemma WALL-SLOT and the 12-cell hypothesis: the PI's slot pair BL00 / BL01 made a lemma, what it strengthens, and what it does not close — A243 addendum, 2026-09-16 18:00

The PI (18:00, at `reach_domain.svg`): *"look at the pair of slots BL00 and BL01: how can we possibly get a second
meeter for BL01?  If we cannot, both A and B teleport to those two slots."*  This note states the swap as a lemma
(n-general, any side ≥ 2), proves it, isolates the one geometric fact it needs to bite (SLOT-MET, [S] with a
133 000-pair search and a proof route), draws the consequence for STUCK-4 / LOCKED-CROWD-FREE(11) — the hypothesis
may assume all TWELVE border cells doubly met — examines the PI's three suppliers of a second meeter as a leaf on
the reach summary, and answers the question asked: **(i)–(iii) do not cover the summary domain analytically; the
exact remaining case is stated in §4.**  Tags as in `reach243.md`.  Code `code/wallslot243.py`, results
`results/wallslot243.md`; sources `k0_route.md` §3 (K0-FREE, `swap_packing`, `teleport_packing`), `sideband.md`
(A1, A2), `wedged_seal.md` (Cor. B1), `pocket_waste.md` (Lemma TWO, JAGGED, PIERCE), `rings_below_4.md` §2.4.

## 1. Lemma WALL-SLOT [T]

**Setting.**  Container [0, s]², s ≥ 2; corner c with frame (u, v); the corner box c00 = [0,1]², the WALL SLOTS
c01 = [0,1] × [1,2] (up c's wall) and c10 = [1,2] × [0,1] (along c's floor).  Twelve cells in all; for s < 4 the
four cells of each wall (c00, c01, c′10, c′00 for the adjacent corner c′) overlap and **cover the wall's strip
[0, s] × [0, 1]**, so the twelve cells cover the border strip {dist(x, ∂[0,s]²) ≤ 1} (`test243.test_wall_slot`:
the difference has area 0 at 3.82, ŝ, 3.99).  A square MEETS a cell iff its interior meets the open cell.

**Lemma WALL-SLOT.**  Let P be a packing of n unit squares in [0, s]² and Z one of the eight wall slots.  (a) If at
most one square of P meets Z, there is a packing P′ of n squares at the same side that contains the slot square Z
and agrees with P off that one square (off nothing if Z is unmet, after dropping any one square of P ∪ {Z}).
(b) If moreover the unique meeter Q of Z is a meeter of the adjacent corner box c00 and c00 is doubly met in P,
then c00 is singly met in P′, and K0-FREE (`teleport_packing`) gives a packing P″ at the same side containing the
CORNER DOMINO {[0,1]², [0,1] × [1,2]} (resp. {[0,1]², [1,2] × [0,1]}).
*Proof.*  (a) Every square of P other than Q has interior disjoint from int Z, so Z is interior-disjoint from
P ∖ {Q}; Z ⊆ [0, s]² since s ≥ 2.  This is `swap_packing` with X = {Q} (or X = ∅ and one square dropped).  (b) Z's
interior is {v > 1} in the frame, the open box is {v < 1}: Z does not meet c00, and the only meeter of c00 removed
is Q, so exactly one meeter remains; K0-FREE exchanges it for the corner square [0,1]², whose interior {v < 1,
u < 1} is disjoint from int Z.  ∎  (Nothing about locks or forces is used; the lemma is as elementary as K0-FREE.)

**Corollary (12-STUCK).**  At every side m at which (k1-a) holds — every packing containing a corner slot square is
killed (the window [3.82, ŝ]; Lean `kill` in `Stuck4.lean`) — a teleport-stuck packing in which some wall slot's
unique meeter is a meeter of its corner does not exist.  Hence, given SLOT-MET (§2), **STUCK-4(11) and
LOCKED-CROWD-FREE(11) may assume all twelve cells doubly met** ("12-stuck"), and A242's root H_B and A243's summary
root may add that hypothesis to every cell.

## 2. SLOT-MET — the fact that makes the corollary unconditional [S]+[M]

**Claim SLOT-MET.**  Two interior-disjoint unit squares A, B in the closed quadrant, both meeting the open corner
box (0,1)², cannot both avoid the open wall slot (0,1) × (1,2) (nor, by symmetry, both avoid (1,2) × (0,1)).  So
each wall slot of a doubly-met corner is met by a meeter of that corner, and WALL-SLOT (b) applies whenever (a)
does.  **Status: [S] — the proof route below is complete except for one inequality; [M] two runs of the search (133 242 and
66 634 pairs tested) over the whole parameter range: no interior-disjoint pair, least overlap 0.073.**
*Route.*  (1) A convex body disjoint from the open quadrant {u < 1, v > 1} lies in a half-plane
{a u − b v ≥ a − b}, a, b ≥ 0, and a point of the open box forces b > 0: the body lies BELOW a line of slope
m ≥ 0 through (1, 1).  Its part left of u = 1 is therefore inside [0,1]².  (2) A square inside [0,1]² is the flush
square, lonely by WEDGED-SEAL / Cor. B1; so each of A, B crosses u = 1, and its part left of u = 1 is a CAP cut off
by the line u = 1.  For a tilted square (tilt θ ∈ (0°, 90°), leftmost vertex L = (1 − λ, v_L)) the cap is the
right-angled triangle at L iff λ < min(sin θ, cos θ); the top vertex T is right of u = 1 (else v_T ≤ 1 and the
square is flat), and the bottom vertex V is right of u = 1 too: u_V ≤ 1 would need sin θ ≤ λ ≤ cos θ with
cos θ + λ tan θ ≤ 1, i.e. sin² θ ≤ (1 − cos θ) cos θ, false for θ > 0.  (3) The two caps' chords on u = 1 are
interior-disjoint segments of [0, 1]; take A's above B's.  Right of u = 1, A's lower boundary DESCENDS from its
chord bottom (edge L→V, slope −cot θ_A) and B's upper boundary ASCENDS from its chord top (edge L→T, slope
tan θ_B) — the two regions open toward each other.  (4) [C] the remaining inequality: the two boundaries cross
before either edge ends, or else cross on the next edges (A's V→R rising, B's T→R falling) — the search finds the
least overlap 0.073 at (θ_A, θ_B) = (86°, 4.5°), the extreme case where B's chord top is lowest.  Obligation
O-SLOT-MET.  (Flat squares: a flat meeter has chord [0,1] and leaves no room for the other's chord.)

## 3. The PI's three suppliers of a second meeter, as a leaf on the reach summary

Under 12-STUCK the wall slot c01 is met by a meeter of c (SLOT-MET, say B) and by a SECOND square X.  Which squares
can be X?  Far corners are out (a BR / TR square has u ≥ s − 1 − √2 ≥ 1.41 > 1).  The candidates are exactly the
PI's: **(a)** the adjacent corner c′'s meeter (either of its two: any c′ meeter has centre v ≥ s − 1.707 and body
v ≥ s − 2.414 ≥ 1.41 < 2, so both can reach down); **(b)** the corner's own other meeter A (its tip in the notch
between B's slanted edge and u = 1: A must have a point with u < 1, 1 < v < 2); **(c)** a free square.

* **(a) in the summary [T].**  A c′ meeter meets c01 only if it has a point with u < 1 and v < 2, hence only if c′'s
  crowd reaches beyond s − 2 along the shared wall: **r_wall(c′) > s − 2** (necessary, not sufficient: the reach ignores u) (r_wall the summary's reach coordinate along
  that wall, measured from c′).  The mutual (wall-grain) supply of both slots of one wall needs r_wall(c) > s − 2 AND
  r_wall(c′) > s − 2 (`wallslot243.wall_grain_possible`).  The PI's inequality h + h′ ≤ s − δ − δ′ is the
  wall-hugging model (both meeters with points at every height of their projections near the wall); in general the
  two wall meeters may interleave, separated by a slanted line, and the condition is the reach pair above with
  interior-disjointness — feasible below 4 and, contrary to "tight at 4", also at and above 4 (at s = 4 the
  projections [< 1, > 2] and [< 2, > 3] can be disjoint).  On the ring `rand_0_0569|t20` (4.11) the coordinator's
  reading (5 and 2 meet BL01) is this case.
* **(b), (c) are not read by the summary.**  Whether A's tip enters c01 is a pose fact (A's max v > 1 with u < 1)
  that the reaches and depths do not determine, and a free square is anonymous: it can meet c01 unless the cell's
  CORES leave it no room — the same fibre-core obstruction as R3 (`reach243.md` §3.3).  So the leaf reads, on a
  cell: MUTUAL-POSSIBLE or MUTUAL-IMPOSSIBLE (`wall_slot_leaf`), and **neither verdict kills**: MUTUAL-IMPOSSIBLE
  only says the second meeter is A's tip or a free square.

**[M] On the window ring at ŝ** (`results/wallslot243.md` §1): at every corner the tilted partner's slot (BL01,
BR10, TR01, TL10) is met by that partner ALONE — the flat meeter of the adjacent corner sits at v ≥ s − 1 − δ ≥
2.5 and never reaches it — while the flat meeter's slot is met by the flat meeter and the adjacent partner (the
wall grain).  So WALL-SLOT kills the whole window family and A226's rattler rings outright, before any pocket
argument: they are not 12-stuck.  (Consistent with A237/A239: those rings had capacity 1 and were killed by room;
WALL-SLOT kills them by teleport, which is cheaper and needs no pocket.)

## 4. Do (i)–(iii) close the summary domain analytically?  No — and the exact remaining case

* **(ii), the mutual case.**  What is proved: the twelve cells cover the border strip, so every free square either
  lies in the centre [1, s−1]² — at most ONE does (Lemma TWO: side s − 2 < 2) — or meets a border cell that is
  already doubly met.  What is NOT proved: that the pocket of a wall-grain four-crowd holds ≤ 2 squares.  That is
  Theorem POCKET-CAP's hypothesis capacity < 3 = POCKET(11) on the wall-grain family, which A237 §3.2 (iii) showed
  has no analytic form without a tilt floor, and the mutual condition supplies none: r_wall(c) > s − 2 forces the
  wall meeter's extent w(θ) > s − 2 − v_min only, and v_min may be close to 1 (a wall meeter floating high, meeting
  the box in a sliver), leaving every tilt admissible.  The notches are not "at most one more" by any lemma here: a
  third wall member beside a tilted meeter's slanted edge is a unit square in the border strip, not in the centre.
* **(iii), the jutting third member / an interior vertex through the notch.**  A239 §2.4's "the jut empties the
  pocket" is a measurement on the 45°-jut family at s = 3.95 (capacity 0 in every bin), not a lemma; there is no
  statement for a jut of arbitrary tilt at arbitrary position.
* **The exact remaining case** for STUCK-4(11) below 4 after WALL-SLOT: a 12-stuck locked four-crowd in which every
  wall slot's second meeter is (a) the adjacent corner's meeter, (b) its own corner's other meeter, or (c) one of
  the three free squares, with the pocket (container minus the eight bodies) holding the three free squares — a
  pose-level room statement.  Sub-case all-(a) is the wall-grain ring with POCKET(11) unproved; a free square can
  serve BOTH slots of one wall (it spans v from < 2 to > s − 2 inside the strip), so three free squares can supply
  three walls and no count closes.  **It is not the proof of POCKET(11); it is POCKET(11) with a new, cheaper
  hypothesis (12-stuck) and the window family removed by teleport.**

## 5. What is new, and the obligations

* Lemma WALL-SLOT [T] and the 12-STUCK corollary (given SLOT-MET) — a hypothesis strengthening for every k0 root:
  A242's `H_B` may require each of the eight slots to be met by ≥ 2 roles / free squares; that is a NEW PRUNE for
  A242's cascade (a cell whose eight role boxes' reach sets leave some slot unmeetable by any role is not dead by
  it — the free squares may still meet it — so it prunes only cells where the slot is also unreachable by a free
  square, i.e. again a room statement; recorded, not run).
* SLOT-MET [S]/[M], obligation O-SLOT-MET (the crossing inequality of §2 (4)); O-WALL-SLOT in Lean: the same swap
  as `swap_packing` with the slot cell in place of the corner cell (routine, not done — no leaf consumes it here).
* The leaf `wall_slot_leaf` on the summary: MUTUAL-POSSIBLE / MUTUAL-IMPOSSIBLE, no kill.  The price of the
  summary root is unchanged (`reach243.md` §4).
