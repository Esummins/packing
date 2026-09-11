# A204 -- the polygon-clip cascade to a fixed point on the survivors of the closed-form layers

The campaign is the PI's (2026-09-10 19:50): *"a bunch of them are going to die once we move from the geo kills to the
clipping/polygon kills. I doubt any of these (maybe one) will survive through to LP"* -- and the rule it runs under is the
PI's too (memory: geometry-before-LP): force the geometry to a fixed point before any LP, every clip re-run on the
PIECES so that K' grows on the far side and clips the neighbours harder.  Input: the 35 pages A203 left alive at the
g1 pad (`survivors_from_A203.txt`), each started from A203's certificate (its clipped H box, its forced slots, its alive
H units).  NO LP, NO branched tree; a page after every round.  Labels: [T] proved, [S] supported, [M] measured, [C] open.

## 1. The node and the round (any n)

**The node.**  Pins (A57's slack pin boxes, delta_pin = 0.01) + H (the conditioned square) + the instantiated forced
meeters F_k, every role carried as PIECES (rational centre rect x tilt sub-bin, A171's representation), SEEDED and
never re-merged into a box (A181's rule):

* H starts from A203's alive UNITS -- its box split 8 x 8 in x / y and 8 bins uniform in t = tan(th/2), minus the units
  A203's mutual clip killed (Lemma MC: an H unit compatible with no option row of a slot a free square must meet) --
  each reconstructed EXACTLY from its index and padded outward by 1e-9 (`poly204.unit_pieces`): a superset of the
  exact unit, so every A203 kill is consumed and nothing else [T];
* a forced meeter F (Theorem FC, `forced_corners.md`: avail_p = H_p + |R_p| + cap_p = 2 with cap_p = 1, A200's
  semantics) is seeded with the per-tilt-bin HULLS of its union's surviving reach pieces (<= 8 pieces; a piece
  contributes to every bin it overlaps: a superset of the union, sound) [T];
* every role's pieces are carried from round to round; the round's clips only ever remove poses.

**The fixed point (`poly204.fixpoint`).**  A171's `Node.normalise` (mode "poly", kmode "pieces", strict_container
False) driven on the node's CURRENT pieces: the sound container clip (w_min), A173's LONELY clip on every role at a
forced CORNER (an instantiated corner meeter, and H when H is forced at that corner -- Corollary FC-corner: both
meeters are non-lonely poses; the constant is the K0-WIDEN c = 1 + w at every pad, since a pose lonely at the larger
box is lonely at the pad's smaller box [T]), two levels of tautologous bisection interleaved with the clip against every
other role's POLYGON K' (A172: the certified intersection of the per-piece K'), then lonely + mutual clip to a fixed
point with K' rebuilt from the survivors after every pass.  Obstacles farther than 1/sqrt2 from a piece are skipped
(A198's `obstacle_near`: skipping a clip only keeps more).  `EmptyBox` = the pair leaf (A135 `shared_point_same_square`).

**The round (`poly204b.propagate_round`).**  A200's option table on the node -- every grid cell (side 0.70 < 1/sqrt2,
Lemma A1) x forced slot bisected with the exact dead test against every role's K', A161's exact miss and the lonely
clip at corners; SEEDED from the previous round's survivors and re-clipped in place (K' only grows, so the new survivors
are a subset: sound) -- the union caps (CN / A1-U / CHORD-U), Theorem FC's forcing (avail < 2 DEAD; avail = 2: H
clipped, a role clipped, the unique anonymous meeter INSTANTIATED), the count with caps (Theorem COUNT) and the bar-H
forcing (A180/A182's unit propagation without branching).  Then the APPLY on the pieces: H and every instantiated
role are re-clipped by the exact reach against ALL their forced slots every round (unit resolution: clipped in place;
few pieces: two more levels), and the round is `changed` iff a role was added, a forced set grew, or a pose volume
fell.  The loop stops at the first round where neither the fixed point nor the apply moved (or on a kill, or at the
900 s wall); the survivors then get A189's no-room leaf at >= 9 boxed roles.

**What A204 adds to A203 [T].**  (i) K'(H) from A203's alive units (up to 512 pieces) instead of the box's 16 pieces:
the intersection over fewer poses is larger and clips the meeter cells harder; (ii) the lonely clip on H at a forced
corner (k5_11's TR(0,0)); (iii) the K'-growth cascade through the instantiated meeters (a forced meeter's K' clips H,
H's K' clips the cells, ...) to a fixed point; (iv) the exact reach clips on the pieces every round.  The count itself
is A200's (hull pairs by Lemma A1) -- weaker than A203's H-mask count -- so every kill here is geometric: the pair
leaf (EmptyBox), an FC availability < 2 after a clip, or a role with no pose meeting its forced slots.

## 2. Soundness and the audit

Every rule is one of the lab's certified primitives (A171/A172/A173 library >= 13f23204, A161 `box_misses_cell_exact`,
A198/A200 caps and FC, A189 no-room); what is new is the DRIVER (seeding, carry, fixed point), so the kept rule of
A202/A203 applies: **a kill the exact tests left alive is a bug until audited by sampling**.  `scratch/audit204.py`:
for a killed (page, pad), H poses are sampled over A203's alive units (random + the unit corners at both tilt ends),
kept when admissible (container, pin cores of half-side 0.49) and meeting every slot H was forced at; at a forced
CORNER the sample is restricted to NON-LONELY poses witnessed INDEPENDENTLY of Theorem B's clauses by a partner G on a
0.02 / 2-degree grid (admissible, meeting the K0-WIDEN box, interior-disjoint from H); the killing slot's meeter poses
are taken on the same grid over the WHOLE window (not the alive cells); a disjoint admissible (H, F) pair would refute
the kill, and the F poses disjoint from some hypothesis H pose are listed per grid cell against the certificate's alive
cells.  Verdicts are `[C: library clip trace]` (no verifier clause; the certificate is the JSON trace of every exact
test and every round's pieces); a pad-0 kill is s0-only, WINDOW-PENDING.

## 3. What died, and by which clip  [M]

(filled from `results/report204.md` at the end of the campaign; see section 4 for the table)

## 4. The table, the survivors' state, the next lever  [M]

(filled at the end of the campaign)
