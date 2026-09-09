# The two doc lines A164 appends

## `docs/residue_ledger.md` §6 (new subsection 6.3)

### 6.3 Leaf WASTE — the uncoverable area, Lemma ID with the corner box removed (A164, 2026-09-08)

A89's Lemma ID charges a SHALLOW corner (1 − δ)² against the wastage budget E(m) = m² − 11 ≤ B₀ =
s₀² − 11 = 4.031780343056 and dies there ("area alone never kills four shallow corners"). A164
removed the corner from the statement. For a node whose hypothesis boxes carry cores K_j ⊆ every
pose of the box (A135 exact for a pin, A132 polycore K′ for a conditioned square), let U be the set
of container points that NO admissible square can contain — admissible for a FREE square = inside
the container and interior-disjoint from every core, while a hypothesis square's own cover is the
union of its poses over its box. Then **Leaf WASTE [T]: |U| ≤ m² − 11, so |U| > m² − 11 is an
LP-free kill** (one line: each of the eleven squares lies in its own coverable set and the interiors
are disjoint, so 11 ≤ m² − |U|; `attempts/A164-wastage-area/notes/leaf.md` §1). Lemma ID is exactly
the case where U is certified by a HYPOTHESIS (shallowness) instead of by GEOMETRY, and the charged
region need no longer be a corner box or even connected — areas of subsets of U simply add. The
window is covered by inflating only the COVER square to λ_max = s₀/3.81794 while admissibility stays
at side 1 (a λ-admissible square contains the concentric unit one), so one s₀-frame raster kills the
whole slab. **[M] Measured on all 71 alive gallery nodes (11 pin-free k0v4 cells + 60 a57v4 pages),
pitch 0.01 × 36 tilt bins with margin-guarded Lipschitz certificates: NO KILL, and not close** —
|U|/B₀ has min 0.00 %, median 18.56 %, max 42.18 %; means 3.18 % (k0, 0 pins), 19.47 % (A57, 5
pins), 21.20 % (A60); refined at pitch 0.005 × 90 bins the two extremes reach 47.05 % of B₀
(`f1_L10_0003`, |U| = 1.8969, window-sound 1.8084) and 35.37 % (`k5_11_interior_Y0738`, 1.4261).
Controls: 7.1 M poses drawn, 1 223 887 certified admissible by an independent SAT pass, 976 134
carried through the containment test, 0 hits; an independent checker (own SAT, own dense sweep, no
code shared with the dilation) confirmed five masks cell by cell, 4.6–7.1 M meeting poses each, 0
admissible meeters. **[F] The corner column is ZERO on every one of the 71 nodes**: no corner unit
box is ever certified unreachable, so **Lemma ID's charged region is empty on the whole alive
population — not small, empty**, and 64–100 % of the certified waste sits in the four WALL STRIPS.
**[F] On the PI's cell `l1_104` all 0.129 units of waste lie in the EAST strip — the wedge between
K′(H) and x = s₀ that A148 already flags as the node's one sub-unit pocket (H → wall x = s, 0.828):
the LOCATION of the reading is right, the COUNT is not.** "Only one square's centre can sit near the
right wall" is false unconditionally — the outer admissible-centre mask admits seven 1-separated
centres in x ≥ s₀ − ½ and eight in x ≥ s₀ − 1 — and the counting hypothesis that would give it,
K0-FREE′ (every corner doubly met, eight squares corner-committed), is vacuous as an AREA row: a
corner-committed square's centre is within √2/2 of its box and covers √2/2 further, so the four
corner reach-envelopes already leave only 0.0166 of the container uncovered on `l1_104` (max 0.248
over the eleven cells) against the 2 + B₀ = 6.03 the row needs. Wastage is therefore a LOCATION
diagnostic, not a kill: the counted version needs A141's lane counts / A153's cover number, because
B₀ = 4.03 out of 15.03 is too large a fraction of the container for a 1–2 unit sliver to reach. |U|
scales with the box count (0.128 at 1 box, 0.793 at 6, 1.701 at 7), which puts the first fire at
9–10 boxes — a node with 1–2 free squares left, where the LP is cheap anyway.

## `docs/budget.md` §D (append to item 1, "Geometric kills that skip both LP and verification")

*A164 (`PENDING`, 2026-09-08):* Leaf WASTE (the uncoverable area |U| against the wastage budget
m² − 11 — A89's Lemma ID with the corner box replaced by any certified-uncoverable region) is the
CHEAPEST screen in the toolbox — 8–18 s per node for the whole certificate (raster + Lipschitz
margins + 10⁵ sampled poses), no certifier round at all, against ~850 s for an LP node — and it
**fires on nothing at the current frontier**: over all 71 alive gallery nodes the best node reaches
42.2 % of B₀ = 4.0318 at pitch 0.01 (47.1 % at pitch 0.005: `f1_L10_0003`, |U| = 1.8969), the median
18.6 %, and the eleven pin-free k0 cells 0–8.3 %; the four corner boxes are coverable on every
single node, so Lemma ID's own shallow-corner row has no consumer either. **0 CPU-h are at stake
from deploying it on today's alive set.** The right disposition is a 15-s pre-screen inside the
EMITTER at 7+ hypothesis boxes, where |U| scales with the box count (mean 0.128 at 1 box, 0.793 at
6, 1.701 at 7) and the leaf's own extrapolation puts the first fire at 9–10 boxes. The transferable
asset is W3, the Lipschitz-raster soundness obligation
(`attempts/A164-wastage-area/notes/leaf.md` §3): A148's gallery pages and A164's leaf lean on the
same two facts — clearance is 1-Lipschitz in the centre and (√2/2)-Lipschitz in the tilt — so
writing W3 once in Lean pays for both, and Leaf WASTE then costs 0 new axioms.
