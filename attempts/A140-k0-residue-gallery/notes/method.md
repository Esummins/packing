# A140 method — what was measured, what was drawn, and what each step is worth

## The corpus: which record is the cell

A115 T6 hands off **twelve converged-alive k0_00 cells**.  A cell has several LP records — the one
A38/A85/A99 first produced, sometimes an A99 `plain_warm` re-solve, and A115's own T4/T5
continuation.  Only the last is converged (`converged = True`, `minmass = 1.000`, `tau = budget`
exactly), and only the last is the record whose dual support means "the LP has reached its optimum
and it is not below budget".  Every page in `docs/shadows/k0v3/` is drawn from

    attempts/A115-k0-corner-rows/results/nodes/<nid>.t{4,5}.lp.json

with the mapping fixed in `code/cells140.py` and cross-checked against T6's `converged_alive` map.
This matters for the gallery: A107's K-gallery was built from the *earlier* records, so where a
cell appears in Part II it appears through an alias whose dual support is a different object.

## k0_00 has no pins

A57/A60 nodes carry 5 class pins plus 1 conditioned square, and T5's kill is "the conditioned
box's core meets a pin's core".  A k0 node's `hyp.cores` are **all** conditioned squares — the
class has no pins at all — so:

* the "feasible centre" rule of `gen_a57_lp.py` (draw H at the feasible centre nearest the box
  centre) runs against the **container** and the **other conditioned boxes' K'**, not against pins;
* the T5-polygon kill has no analogue for a single-box cell.  It only has content where a cell
  carries more than one conditioned square, which among the twelve is exactly
  `s3_far_BL389484_TR018470` (four boxes, budget 7 = 11 − 4).

The brief expected level-2/3 cells to carry two or three conditioned squares.  They do not: in
A38's k0 tree a level-2 cell is a **refinement of the same box** (`l2_p65_101` = parent 65,
sub-box 101), so it has one conditioned square with a narrower window — tilt width 7.5° instead of
15°, which is why its K' is proportionally larger.

## T1 (i): what "excluded by K' but passing K(a)" proves

The node LP counts the `budget` squares OTHER than the conditioned ones, and its row filter drops a
placement only when it penetrates some axis core `K(a)` by more than `EPS_CORE = 2e-3`.  K(a) is
the largest *square of the box's own pose* inside every `Q(c, θ)`, `(c, θ) ∈ B`; the polygon core

    K'(B) = ⋂ over (c, θ) ∈ B of Q(c, θ)

is the whole intersection and is strictly bigger.  A placement whose square meets K'(B) meets
`Q0` at **every** pose of B, so it cannot be one of the other squares — the LP is charging dual
weight to a column its own hypothesis forbids.  On k0 the effect is large because the boxes are
wide in tilt: K' has 1.09×–1.47× the area of K(a) on the twelve, and the exact axis core (A135)
recovers 1.02×–1.25× of that **inside the frozen certificate schema** (it is still a square at the
box's own tilt, so `verify_case` needs no change).

Slack is `tau − budget`, which on a converged-alive cell is 0 to within 4e-12.  Any excluded
positive weight therefore exceeds the slack, which is why the brief's clause fires on all twelve
and why the in-vitro re-solve is the only way to tell a real kill from a column the LP can replace.

## The control arm

A132's in-vitro driver runs two arms (axis, poly) so that a drop is attributable to the core and
not to the re-solve.  Here the **axis arm already exists and is stronger than a fresh 240 s solve**:
A115's stored record is the axis arm run to convergence at `tau = budget`.  So `invitro140.py`
runs one arm per cell — the brief's "ONE in-vitro re-solve on that cell".

## Red-dashed columns: two different objects, both drawn

`gen_a57_lp.py`'s rule is "overlaps the hypothesis square at EVERY pose of the box", sampled on a
7³ pose grid.  That is a *sampled* statement.  "Meets K'" is the certified statement and is
strictly stronger (meeting the intersection implies meeting every pose).  Both are drawn: the red
dash marks the 7³ rule, and the label says `[K' certified]` when the certified test also fires.
The counts differ on three cells (`l2_p65_101` 42 vs 39, `l2_p65_111` 28 vs 24, `l2_p74_001` 3 vs
2): those columns overlap at every *sampled* pose without meeting the intersection, and they carry
no weight in T1's kill arithmetic.

## Geometry checks

`code/verify140.py` re-derives, with implementations that share no code with the drawing path:

1. containment of every square in both panels;
2. the 7³ always-overlap statement, recomputed with A107's `shadowlib.sat_gap` (a different
   formula from the polygon SAT used to draw it);
3. for each K'-certified column, an **exact** witness where one exists: a rational point that
   `polycore.vertex_ok` certifies to lie in `Q(c, θ)` for every pose of the box AND that lies
   strictly inside the column's own square.  One such point is a floating-point-free proof that
   the two squares share an interior point at every pose.  Where the search finds none, the
   K' ∩ column sliver is thinner than the 1e-9 rational grid — a "not proved", never a false kill.
