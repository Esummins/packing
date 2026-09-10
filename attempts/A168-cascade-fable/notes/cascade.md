# A168 — the l1_104 cascade, done as a case tree of geometry-forced boxes (Fable lead, 2026-09-09)

Labels: [T] proved, [S] routine given cited items, [M] measured / computed exact, [F] finding, [C] open.
Record: `results/tree_<cell>.json` (the whole tree, every node with its pieces, cores, invariant, rows,
verdict), `results/cascade168.jsonl` (one line per node), `results/lp_<cell>.jsonl`,
`results/screens_<cell>.jsonl`, `results/check168_<cell>.json`; figures `figs/cascade_<cell>.svg`
(one page per step: before / the region + the forcing / after, then the coexistence pages, then the
tree); certificates under `certs/`.  Canary: §2 — read it first.  Results: §3 (canary), §4 (l1_104),
§5 (what generalises), §6 (files, discipline, obligations).

---

## 0. The objects and where each is proved

| tag | statement | source |
|---|---|---|
| (R1) | K0-FREE / K0-BLOCKED: for a packing P at side m ∈ [3.82, ŝ) not a Trump image, F = Δ_λ P has ≥ 2 distinct squares meeting int B_c^w(s0) at every corner c; the K0-FREE branch is the (T) teleport leaf, dead once `k1_00` closes (obligation K0-O1) | `docs/proofs/k0_route.md` §3, §4.1–4.2 |
| (R2) | K0-WIDEN pad w = (λ_max − 1)(1 + 1/√2) = 0.02551007… (rational form used in every exact test) | `k0_route.md` §4.1 |
| (R6) | s0 − 2(1 + w) − √2 = +0.41185 > 0: no square meets two widened corner boxes; the four crowds are disjoint sets of squares | A150 `notes/composition.md` §1; re-derived in `check168.c1` |
| (M0) | M(c) = 0 (H cannot meet int B_c^w): A161 `box_misses_cell_exact`, full SAT over H's box, exact | A161; re-derived in `check168.c1` with 5·10⁴ sampled poses |
| (K′) | K′(B) = ∩_{poses ∈ B} Q(pose), certified vertex-wise (`vertex_ok` = Lean `checkVertexInPBox`) | A132 / A135 `PolyCoreT5.lean` |
| (CLIP) | A131's per-tilt-sub-bin pin-clip with another square's certified axis core in the pin's role (A158's rule): a centre whose square meets that core at EVERY tilt of the sub-bin carries no square distinct from that role | A131 `pinclip.dead_q` (exact), A158 `notes/leaf.md` |
| (PAIR) | a rational point in every pose of two boxes ⇒ the two witnesses are the same square | Lean `PolyCoreT5.shared_point_same_square` |
| (OVL) | every pose pair of two boxes overlaps ⇒ not two distinct squares | A118 §1.2(ii) `lanelib.pair_always_overlap` |
| (ROW) | chords of an interior-disjoint family on an axis line inside the container sum to ≤ s0; a box contributes ≥ minchord(B, l) (exact five-point rule); β = ⌊s0 − Σ minchord⌋ caps the FREE squares with chord ≥ 1 | A144 LINE-1/2 `guardline.minchord_box`; A161 Lemma CL (band half) |
| (LANE) | A141's complete prefix-code cover with container / misses-cell / witness discharges; the pair test on the open set certifies LANE ≤ 1 | A141 `polylane`, A161 `chordlane.cover` |
| (SIDEBAND-a) | [T] A169 Lemma A2 / Cor. A3: two interior-disjoint meeters of the OPEN widened box (0, c)², c = 1 + w, have centres in DIFFERENT cells of the 2×2 grid {x < c, x ≥ c} × {y < c, y ≥ c} (corner-local coordinates); in particular one centre has x < c or y < c — the band constant is c = 1 + w = 1.025510, NOT 1 ("within 1 of a wall" is [F] for the widened box, A169 §0). Lemma A1: any two interior-disjoint unit squares have centres at ℓ∞-distance ≥ 1/√2 | `docs/proofs/sideband.md` §2; consumed here as row **R1** (`resume168.cells_dead`, [T] on the two centre rectangles, exact up to a 10⁻⁹ float guard) |
| (SIDEBAND-b) | [F] as first stated ("the other centre lies outside the band") — A169's counterexample: (0.6, 0.5) and (0.5244, 1.5220) at 0° / 2.866°, both x < 1; the TRUE form is the cell statement above | A169 §0 |
| (REQ) | [T] A169 Theorem B: a first meeter Q₁ (quadrant, meeting (0, c)²) admits a second meeter iff one of (NE), (W), (S) holds — and for c > 1 also (P) = the pressed square [0,1]² itself is a second meeter; a pose with all clauses failing is LONELY; in a K0-BLOCKED family no square is in a lonely pose at any corner (K0-WIDEN + K0-FREE) | `sideband.md` §3, §6 row R3; consumed here as row **R3** (`resume168.lonely_box`): the three one-parameter clauses on the box's centre rectangle with g(n) minimised over the box's tilt range, decided on a 2001-point grid with the Lipschitz margin [S], clause (P) by A131's exact clip against the pressed square shrunk by 10⁻⁶ [T per sub-bin]; validated against A169's Cor. B2 (slide threshold t = tan(θ/2): 0.33 lonely / 0.42 not at 45°), conservative below 20° |
| (INV) | [T] A171 `multibox.Node.normalise` + `assert_invariant`: the container clip (sound w_min rule; the STRICT w_max clip narrows the hypothesis and is used only as a diagnostic) then the mutual clip against every other K′ to a fixed point, K-CONTAINER / K-DISJOINT / POSE-CONTAINER / CLIP-FIXPOINT asserted exactly; `EmptyBox` = the pair-leaf kill | `attempts/A171-multibox-invariant/code/multibox.py`; re-verification of every alive node here: `code/a171check.py` (normalise with `strict_container=False`, assert with `strict=False`) |
| (LP) | the multi-box case-LP at budget 11 − #boxes on A135 exact cores, the certificate carrying the SAME exact cores (A166's finding), checked by the frozen `verify_case.py` (sha 521cb01f…) | A150 `lp150` pattern, A166 `certfix166` |
| (WASTE), (CN) | A164 |U| ≤ m² − 11 and A153's cover number, as free screens | A164 `geo164`, A153 `cover153` |

## 1. The construction rules (coordinator, 2026-09-09) and how they are met

**A node is a list of named ROLES.**  A role is a square of F whose pose is known to lie in the union of
its PIECES — one `caselp.Box` per tilt sub-bin (nsub = 4; the pieces partition the tilt range and a
union box is never re-formed).  Its certified objects (`roles168.Role`): K′(piece) for each piece
(A132); **K′(role) = the exact rational intersection of the pieces' K′** — a convex polygon inside every
pose of every piece, every vertex re-certified with `vertex_ok` against every piece; the **axis core** =
the largest axis square about K′(role)'s centroid inside it, its corners certified against every piece
(the 'pin' A131's clip consumes).

**NORMALISE, at every node, before anything else (`roles168.make_node`):**
(i) container clip of every piece with A131's w_min rule (a centre outside [w_min/2, s0 − w_min/2] for
every tilt of the sub-bin carries no admissible pose; the per-piece residual (w_max − w_min)/2 is
recorded as `slack`, ≤ 0.024 at nsub = 4, and every drawn or sampled pose union is restricted to
admissible poses);
(ii) mutual clip of every piece of every role against every OTHER role's axis core (A131's exact
predicate per sub-bin), K′ and axis cores recomputed after each pass, **iterated to a fixed point**
(≤ 8 passes; 2–4 in practice);
(iii) the recomputed K′(role) and axis cores are what every row, cover, figure and LP consumes;
(iv) **the INVARIANT is asserted**: every K′(role) inside [0, s0]² (every vertex, exact) and every pair
of K′(role)s interior-disjoint (exact SAT over both polygons' edge normals in ℚ).  A failing pair is not
an error: a rational point of the intersection lies in every pose of both roles, so the two witnesses are
the same square — the node is DEAD (C) with that point as the certificate (PAIR).  A node whose invariant
did not pass carries no row, cover, figure or LP.  (A171 `multibox.py` is being built for the same
purpose; this is the attempt-local implementation of the same statement.)

**Every box is a superset hypothesis for a DISTINCT square.**  K0-BLOCKED pairs are distinct by
definition; the four corner crowds are disjoint by (R6); H is distinct from every meeter wherever
M(c) = 0 is certified; in the M(TR) = 1 mixed case ("S = H") H is the second meeter itself, restricted
to the sub-boxes of its own box not certified to miss the corner (A159's B_meet with A161's exact test),
and the free meeter is distinct by construction.  Hence every clip is a plain discard.

**The tree is a COVER.**  Every branching is over a complete prefix-code cover (A141's deterministic
split, Kraft sum 1, replayed by the checker) of the pose window of the new square, with every discharged
leaf carrying its reason (container / misses-cell exact / band-or-out exact / role-aware witness:
a rational point in every pose of the box AND of every piece of the named role); the second meeter of a
corner is labelled by a tautology (larger centre x at TR, larger centre y at TL, smaller centre x at BL)
and the boxes entirely on the wrong side of the first meeter are PRUNED by that labelling; the mixed
child is added wherever M(c) = 1; the complement of a band step is kept as an OPEN node and counted.

**The COEXISTENCE cut (PI, night note).**  The first meeter's box at a corner is a valid hypothesis only
if some second meeter at that corner — distinct from every role, interior-disjoint from all of them,
inside the container — exists: for each first-meeter box, the second-meeter cover is built with the
roles as obstacles and its open boxes normalised one by one; the first survivor is a certificate of
coexistence (early exit); if none survives the first-meeter box DIES.  The region of the first meeter is
reported BEFORE and AFTER the cut (`tree.coex[step]`, figure pages "coexistence").


**The A169 leaves (resume, 2026-09-09).**  At every corner cover (`cascade168.corner_step`) each open box is
tested FIRST by R3 (lonely ⇒ dead for any role, no normalisation needed) and, for the second meeter of a
corner (S2/S4/S6/S8), by R1 against the first meeter's pieces (same cell ⇒ dead; ℓ∞ < 1/√2 everywhere ⇒
dead); the coexistence cut applies R3 to the FIRST meeter (a lonely first meeter dies without a cover) and
R3 + R1 to every candidate before it is normalised.  `cascade168 lonely` applies both post hoc to every
recorded ALIVE node (idempotent; verdict `DEAD(C, R3 lonely …)` / `DEAD(C, R1 …)` with the clause detail).
The old S3-complement reading ("LANE(OUT) ≤ 1 certified ⇒ a band meeter exists") stands on its own local
lane certificate [S]; A169's sharp constant makes the same statement with bands of width 1 + w and no cover.

**Resume bookkeeping.**  Steps and the coexistence cut run in SHARDS (`--shard k/n`): a shard writes only
the nodes it touched to `results/shards/tree_<cell>__<STEP>_s<k>of<n>.json`; `cascade168 merge --step S`
folds them (and the `coexS` shards) into the main tree and re-locates the canary.  Every node runs under
the 1,500 s wall (`resume168.NodeWall`: the node is listed in `results/wallcap_<cell>.json`, kept in its
prior state — CAP is never a verdict — and the process TREE is killed with `taskkill /T /F`); wall-capped
parents are skipped on resume.  Any LP waits for > 3 GB free physical and > 6,144 MB commit headroom
(`resume168.memory_gate`).  Certificates go through A170's `make_certificate_exact` (the exact cores the
row filter used; a FAIL with 0 holes is replayed at depth 64/72 before any re-solve).

**Sampling lines.**  Every geometric count is confirmed drawn → tested → hits: the checker's clip
falsification (admissible poses in a clipped-away region must overlap another role's core), the OVL
re-decisions (sampled pose pairs must overlap), the M(c) samples, the canary's real squares.

---

---

## 5. What generalises (every lemma n-general; each example → the lemma that generalises it)

**The cascade as a procedure.**  Input: a hard interior square H (a k0 cell: one conditioned box, τ = budget),
side s, pad w = (λ_max − 1)(1 + 1/√2).  Loop over the corners in the PI's order (the corner H blocks first):
(i) K0-BLOCKED gives two DISTINCT meeters of the widened box; (ii) cover the meeter window with the roles
as obstacles (container / misses-cell / witness leaves), and at every open box apply, in this order,
R3 (lonely ⇒ dead), R1 (same cell as the first meeter, or ℓ∞ < 1/√2 ⇒ dead), then NORMALISE (container
+ mutual clip to a fixed point) and ASSERT the invariant (K′ inside, pairwise disjoint; a failure is the
PAIR leaf), then OVL and the chord rows; (iii) before leaving a corner, the COEXISTENCE cut: a first meeter
with no admissible second meeter dies; (iv) at the end, the case-LP at budget n − #roles on the exact cores
(A170's wrapper), the uncoverable area and the cover number as free screens.  Nothing in the loop uses
n = 11 except the budget arithmetic and the fixed side s.

| statement used | n-general form | where it is proved |
|---|---|---|
| K0-BLOCKED / K0-WIDEN | for any n, any side window [m₀, s): a packing not a Trump image has ≥ 2 distinct squares at every widened corner box of its dilate, or is killed by the K0-FREE leaf | `k0_route.md` §3–4 |
| (R6) crowds disjoint | s − 2(1 + w) − √2 > 0 ⇒ no unit square meets two widened corner boxes; holds for every s > 2(1 + w) + √2 = 3.465 | A150 `composition.md` §1 |
| CLIP / PAIR / OVL | statements about two boxes of DISTINCT unit squares in any packing, no n | A131, A141 §3 (Lean), A118 §1.2 |
| ROW (chord rows) | chords of interior-disjoint squares on a line inside [0, s]² sum to ≤ s; β = ⌊s − Σ minchord⌋ free band squares, any n | A144, A161 Lemma CL |
| R1 (cells, ℓ∞) | Lemma A1 needs no container and no n; Lemma A2 needs c < 1/2 + 1/√2, i.e. every pad w < 0.2071 | A169 §2 |
| R3 (lonely poses) | Theorem B is a statement about ONE unit square in a quadrant and a box (0, c)², c ≥ 1; the K0 consequence (no square of a K0-BLOCKED family is lonely at any corner) is n-free | A169 §3, §6 |
| coexistence cut | "a hypothesis box for the first meeter is valid only if some admissible second meeter exists" is the constructive form of K0-BLOCKED at that corner; its cover + normalisation is the same code at every n | this attempt, §1 |
| LEAF LP | the case-LP with k conditioned boxes at budget n − k, certificate on the exact cores, frozen verifier | A150, A166/A170 |

**Examples → lemmas.**  A pressed TR meeter at 45° (centre 0.707 from both walls) is lonely (R3, Cor. B1);
a first meeter slid δ < tan(θ/2) along a wall is lonely (Cor. B2); two candidate meeters both in the NE
cell of a corner are the same square or overlap (R1, Lemma A2); the canary's real TR pair {D = square 5,
S = H itself (M(TR) = 1)} lands in distinct cells at c = 1 + w and at ℓ∞ ≥ 1/√2, as Lemma A2 says it must.

---

## A174 takeover (Fable lead, 2026-09-09 11:00 -> ) — the same tree, continued

A168's agent was stopped at 10:35 with its three S3 shards (`s3 --cell l1_104 --parents all --shard k/3`)
and the canary's S3 coexistence pass in flight; A174 (`attempts/A174-cascade-takeover/BRIEF.md`) is its
successor and works here.  Nothing of A168's record is re-derived; what is added is listed below with
its file, and every figure of a step is regenerated the moment that step's results land
(`code/fig174.py`, `figs/steps_<cell>_<STEP>.svg`, stable names; shard files are overlaid read-only so a
page exists while the shards run).

**A174.1  The coexistence cut at PIECE granularity (`code/coex174.py`, applied by `coex174b.py`).**
[T] A first meeter X at corner c′ (D at TR, B at BR) is a valid hypothesis only on the poses that admit
a second meeter of the widened box (K0-BLOCKED).  Per ALIVE node of S1 / S3 every piece of X is bisected
(`--bisect 1`: the longer centre side halved, tilt sub-bin kept) and each sub-piece sp is tested:
(i) the sub-node {other roles, X ∈ sp} is normalised (container + mutual clip to a fixed point,
invariant, OVL) — a dead sub-node has no configuration with X ∈ sp; (ii) the partner window (the
corner's meeter window) is covered ONCE PER PARENT with the parent's roles as obstacles (complete
prefix-code cover, A141's discharges; fewer obstacles ⇒ a superset of every child's and sub-piece's
partner poses, so the reuse is sound); (iii) every open box passes R3 (lonely ⇒ dead), R1 against sp
(Lemma A2 cells, Lemma A1 ℓ∞), then is normalised with {roles, X ∈ sp}: the first survivor is a
coexistence certificate (early exit), none ⇒ sp is dropped; in the M(TR) = 1 canary H itself
(restricted to B_meet) is tried as the partner.  X is replaced by the union of its surviving,
re-normalised sub-pieces, the node re-normalised, and the cut propagated to every descendant by
intersecting the same role's pieces (the descendant's hypothesis is contained in the ancestor's)
[T].  The cells of the parent's partner cover at c = 1 + w are RECORDED (corner-local x/y, `lo` =
within c of the wall) so the PI's reading — B's partner comes from the (left, floor) cell — is
measured, not assumed; those boxes are tried first.

**A174.2  The lonely clip (`code/lonely174.py`, consuming A173's `multibox.lonely_clip`).**  [T] R3 is a
NO-family in pose space (a lonely pose at corner c′ admits no second meeter of the widened box, so no
square of a K0-BLOCKED family is in one), and A168 consumed it only as a whole-role kill.  A173 makes it
a per-piece CLIP inside A171's library: centre slabs and tilt halves certified lonely are removed
(the box test is a sufficient condition, monotone under shrinking, so every removal is sound).  Here it
is applied to every corner-meeter role of every alive node (D, S at TR; B, B′ at BR; T at TL; L at
BL; `refine 1`): the clipped pieces are intersected with the piece they came from, the role rebuilt
(K′ from the survivors — larger, so the mutual clip bites harder), the invariant re-asserted, the
fixed point re-run at levels ≤ 2, and the clip propagated to the same role in every descendant.
Consumed only once A173 is registered done (until then A168's whole-role kill is what the tree has).

**A174.3  Figures (`code/fig174.py`).**  Per step and cell, `figs/steps_<cell>_<STEP>.svg`: an
AGGREGATE page (every touched parent's roles as thin outlines and ALL of the step's cover boxes,
stipple = alive, faint = dead; the same boxes coloured by the coexistence status; the union of the
alive children's new-role pieces = the region left after the step), then the per-chain pages of
fig168b (canary chain first) — regenerated whenever a shard file lands (overlay, read-only) and at
every merge / coexistence pass, and committed.  `figs/partner_<cell>_<STEP>.svg`: for a node after
the piece cut, the partner family drawn BY GEOMETRY (centres admitting some tilt inside the
container, clear of every K′, meeting the corner cell) with the certified witnesses, and the first
meeter's sub-pieces kept / dropped with the 2×2 grid at c = 1 + w drawn.

---

## A175 takeover (Fable lead, 2026-09-09 11:55 ->) -- the same tree under the POLYGON clip

**The defect [F, coordinator; reproduced here M].**  `roles168.normalise` clipped every piece only against
the other roles' AXIS CORES (`Role.axis`, the largest axis square inside K'(role)); K'(role) itself -- the
certified polygon, several times the area of its inscribed axis square -- was never an obstacle, so a
role's growth never reached the others and the cascade barely propagated upstream.  Two symptoms in the
record: (i) on `root/D0/S1/B0` (S3 shard `s1of3`) A168 kept H 1.00 / D 1.00 / S 1.00 / B 0.60, ALIVE;
the polygon clip empties H at pass 1 after two refinement levels (H 0.0027 kept, then EmptyBox(H): every
pose of H meets another role's K' at every tilt of its sub-bin -- the pair leaf) [M, `code/polyclip175.py`
on the shard record]; (ii) every reloaded role printed kept 1.00 because `Role.from_json` lost `area0`
(fixed: kept is now relative to the role's SOURCE box).

**A175.1  The polygon clip (`code/polyclip175.py`).**  A171/A172/A173's primitives (`multibox.py`, read-only,
IMPORTED not copied) are driven on roles168's PIECES: each piece (caselp.Box, its own tilt sub-bin) becomes an
A171 piece Bin(t_lo, t_hi) x the exact rational rect of its float coordinates (a superset [T]); then, in
order, the SOUND container clip (w_min, `strict_container=False`), A173's LONELY CLIP on every corner role
(D, S at TR; B, Bp at BR; T1, T2 at TL; L1, L2 at BL; c = 1 + w exactly `resume168.C_RAT` = `multibox.C_WIDEN`,
asserted equal) BEFORE anything reads K', `refine = 2` levels of tautologous bisection interleaved with the
clip against the POLYGON obstacles (`MBox.obstacle("poly")` = A172's per-piece K', every vertex certified
by `polycore.vertex_ok` against every piece), then lonely + mutual clip to a fixed point with K' rebuilt
from the survivors after every pass.  `EmptyBox` = the pair-leaf kill; the emptied box's replayable slab
trace (every `slab` step re-checkable by four corner `dead_poly` calls + convexity of the dead set, A171)
and every role's pieces at death are the certificate, recorded per node.  Survivors go back to roles168:
each piece rounded OUTWARD (`piece_box`) and intersected with the piece it came from (the unique old
piece whose t-range contains the survivor's sub-bin -- splits are nested), the Role rebuilt (roles168's
own per-piece K', exact intersection, vertex_ok-certified, axis core) as the CROSS-CHECK of A171's K'
(both areas recorded: `k_area` vs `k_area_mb`), then roles168's invariant (K' inside the container, every
pair interior-disjoint, exact SAT) and OVL asserted as before.  `cascade175.py` routes every
`roles168.make_node` call of cascade168 / coex174 (steps, coexistence cut, piece cut) to it.

**A175.2  Re-normalisation of the record (`code/renorm175.py`).**  Top-down over every ALIVE node with roles
(both trees; the S3 shard files overlaid read-only so the nodes the detached shards were still producing
are covered before the merge): a node's roles are first intersected with the SAME roles' clipped pieces at
its parent (the child's hypothesis is contained in the parent's, so a pose the parent's clip removed is
impossible for the child [T]; an emptied role = DEAD(propagation)), a node under a DEAD parent is
DEAD(ancestor) without computation, the rest run `polyclip175.make_node` under the 1,500 s wall.  Side files
`results/polyclip175_<cell>_s<k>of<n>.jsonl` (one line per node: verdict, leaf, certificate, new roles with
grown K', kept, rows on the step's walls), shards by S1 subtree, resumable; `apply` folds them into the tree
(the A168 record kept under `node.a168`), `fig174` overlays them so every page's kept: line shows the polygon
clip while the runs are in flight.

---

## A176 takeover (Fable lead, 2026-09-09 12:33 ->) -- the same tree on the FIXED library

**Why.**  A173 found a LIVE unsoundness in A171's library (`multibox.py`, fixed in 0c5e6d30 / 13f23204):
`Bin.radii` cached exact radius bounds keyed on `id(obstacle)`; `normalise` frees each pass's obstacles,
CPython recycles the address, and a surviving `Bin` could answer a NEW obstacle with the OLD one's bounds --
wrong in either direction inside the exact dead test.  Obstacles now carry a monotone `uid` and
`MBox.obstacle` caches by the exact content of K'.  A175's `renorm175` shards ran while the fix was
landing: their side files `results/polyclip175_l1_104_s*of4.jsonl` are NOT the record (kept read-only, a
comparison only; `fig174` no longer overlays them); the round-1 relaunches and their launcher loops were
killed at 12:33 [M].  A168's S3 shards (36268/37312/32084) and A174's coex174 processes do not use
multibox and were left running.

**A176.1  The library check [M].**  `multibox.py` on disk = 13f23204 (`Obstacle.__slots__` has `uid`;
`renorm176` asserts it at import).  `tests/test_multibox.py` post-fix: ALL PASS, 70.7 s (budget 120 s),
record `attempts/A176-cascade-fixedlib/results/test_multibox_postfix.json`.  A171's demo171 and A172's
report172 replayed on the fixed library into A176's own results (`code/rederive176.py`,
`results/rederive176.json`): NO cited number changed on BR139/TRH-25 (kept H 0.358392 / B1 0.942803 /
D 0.072175 at the A172 fixed point; union hull 0.440792 / 0.942803 / 0.088172; K' areas 0.658/0.740 hull
vs 0.709/0.774 same-pieces vs 0.731/0.799/0.794 fixed point; rows top beta 2 / right beta 1; lane 0) --
on that node the recycled-address alias never occurred; the writeup owes no correction
(`attempts/A176-cascade-fixedlib/notes/writeup_corrections.md`).  With the lonely clip on D at TR the same
node keeps D 0.057384 (new number).

**A176.2  Re-normalisation of the record (`code/renorm176.py`, `code/launch176.ps1`).**  renorm175's
top-down discipline (parent-intersection propagation [T], DEAD(ancestor) without computation, every other
node through `polyclip175.make_node` = `Node.normalise(nsub=4, refine=2, mode="poly", kmode="pieces",
strict_container=False, corners={D,S: TR; B,Bp: BR; T1,T2: TL; L1,L2: BL}, c = 1 + w)` driven on the
recorded PIECES, then roles168's invariant (strict=False) + OVL, under the 1,500 s wall) with FRESH side
files `results/renorm176_<cell>_s<k>of<n>.jsonl`; shards by a depth-d subtree key assigned greedily by size
(l1_104: depth 2, 3738 + 3732 nodes with the three S3 shard files overlaid; l1_153: depth 5, 348 + 344),
a node whose ancestor sits in another shard is retried after the side files are re-read.  Every record
carries the absolute pose volume per role before / after (`vol0`, `vol1`) and the role bounding boxes, so
`renorm176 xcheck` compares node by node with the coordinator's `clipcheck.jsonl` (fixed library, no lonely
clip, roles re-split from their bounding boxes): weaker here = they killed a node we kept, or a kept
volume here exceeds theirs.  Launched 12:52 (four processes, BelowNormal, affinity 0xFFFF).

**A176.3  Every NEW node on the fixed polygon + lonely clip.**  `roles168.make_node` now delegates to
`polyclip175.make_node` by default (the axis-core rule survives as `make_node_legacy` behind
`A168_LEGACY_CLIP=1`), so cascade168's steps, the coexistence cut and coex174's piece cut build every new
node on the library's clip without the cascade175 router.  Smoke: the l1_153 root through the new default,
kept H 1.000, 6.5 s [M].

## A183 takeover (Fable lead, 2026-09-09 15:56 ->) -- A181 resumed after the 15:46 crash

**State at the crash [M].**  Bugcheck 0xD1 (driver fault) at ~15:46, reboot 15:53; every process
died, A181's agent with them, and A181 wrote no notes section (this one covers both).  A181 had
landed: `renorm181` (parent-SEEDED top-down re-normalisation: child pieces = record ∩ parent's
fixed-point pieces per role and tilt sub-bin, no bounding-box re-merge, DEAD by inheritance when the
seeding empties a role; 49917cdf), the sliver fix in `polyclip175.mbox_to_pieces` (only the HOST
intersection of a survivor is kept; the sliver-era records set aside as `results/slivers_renorm181_*`;
c262d09c), and the l1_104 S1 figure (e4578050).  Records on disk: l1_104 78 (root, 28/28 S1 ALIVE,
S2 49 of 111 done: 27 ALIVE / 22 DEAD = 6 EmptyBox + 14 ancestor + 2 inheritance; 2,401 S3 nodes
already DEAD by closure), l1_153 24 (root, 6/6 S1, 1/1 S2, 16 of 119 S3 done, all ALIVE); `vol1 >
parent` on 0 nodes in both cells (`renorm181b report`, `logs/a183_report_*_pre.log`).  l1_104's S3
shards were merged into the tree at 14:47 (19,506 S3 nodes in `tree_l1_104.json`; the overlay adds
nothing), so no merge was needed.  A168's untracked core files and the AD-state sliver file were
committed first (da8a1ea2, 396737bf).

**A183.1  The refinement lever (`code/renorm183.py`, `code/launch183.ps1`).**  The coordinator measured
on l1_104 root/D0/S1/B5: nsub/refine 4/2 keeps H 0.745, 8/3 keeps 0.639 at 3.6x the time, 16/3 no
better.  Rule: every node that SURVIVES the 4/2 pass is re-clipped at nsub 8 / refine 3 SEEDED FROM ITS
OWN 4/2 FIXED POINT -- each surviving piece's tilt sub-bin is bisected once more (`MB.sub_bins(.., 2)`,
tautologous: the two halves cover the piece exactly), then three levels of `split_piece` bisection and
the polygon + lonely clip to the fixed point; the result is a subset of the 4/2 fixed point, so the
pass is sound and never weaker [T].  Children are seeded from the parent's FINAL (8/3) pieces.  The
record carries `setting` ("nsub 8 / refine 3 (after 4/2)"), `kept_42` / `vol1_42` and the final
`kept` / `vol1`; every figure page prints the setting.  Resumable on A181's side files: a node is done
when its last record is DEAD or ALIVE at the 8/3 setting; A181's 4/2-ALIVE records are UPGRADED in
place (recorded roles re-seeded by the parent's current pieces, then the 8/3 pass only).  A node
wall-capped (1,500 s, process tree killed) is retried at 4/2 only, then 4/1, then 4/0 (renorm181's
cap rule).  Box ceiling today 12 lab pythons (`launch183.ps1`), <= 4 of mine.

**A183.2  The figure rule.**  The PI read an extremal-tilt outline crossing S's K' on the "after S3"
page as a missed clip.  `fig168b.draw_role_full` now draws the hypothesis square only at an
ADMISSIBLE pose: the centre is the bbox centre if a surviving piece contains it (else the largest
piece's centre), the solid square at the mid-tilt of the largest piece containing that centre, and
the dashed extremal outlines at the th0 / th1 of THOSE pieces only -- never an excluded pose.

**A183.3  Launch [M].**  16:1x: l1_104 shards 0/2 and 1/2 (depth-2 keys; 6,278 + 6,221 nodes to do
including the whole S3) and l1_153 as ONE shard 0/1 (depth 5; ~700 nodes, S1..S8) -- two l1_153
half-shards ran for two minutes first and were killed so that a fourth slot stays free for the
figure, report and LP processes under the <= 4 rule (their records stay in
`renorm181_l1_153_s{0,1}of2.jsonl`; every side file of a cell is read).  Launchers relaunch a
wall-capped shard; the run is resumable at every record.

**A183.4  The LP and the pieces (settled; `code/lp183.py`).**  The frozen verifier reads ONE
rational square per hypothesised packed square (`hypotheses.cores = [{kx, ky, tm, a}]`, exemption
"Q meets a core", bridge "some packed square CONTAINS the core") and ignores the box a core carries;
a LIST of boxes per square is not expressible, and an exemption "Q meets some K_i of a list" would be
UNSOUND for the bridge (a packed square other than Q0 may meet a K_i it does not contain).  What v1
consumes from the pieces is any rational square K ⊆ K'(role) = the certified intersection of the
per-piece cores (A172): every surviving pose contains its piece's core ⊇ K'(role) ⊇ K [T].  lp168 /
cascade168 `stage_nodes` fed the exact core of the UNION BOX of the pieces (the clip's exclusions
re-admitted; the core shrinks).  `lp183.PiecesHyp` feeds `Role.axis` -- the largest axis square about
K'(role)'s centroid inside K'(role), every corner `vertex_ok`-certified against every surviving piece
(`roles168.axis_core_in_poly`) -- as the live `Hyp.cores`; `certwrap170.carry_exact_cores` carries a
live core verbatim (never shrinks one), so the certificate under the frozen verifier states exactly
that core.  The polygon K' itself would need a v4 clause `hypotheses.poly_cores = [{vertices}]` with
the exemption "Q meets the closed convex polygon" by exact SAT over Q's two axes and the polygon's
edge normals, the bridge unchanged.  Demo: l1_104 root/D0/S1 (S2, b = 8) -- see A183.5.

**A183.5  The pieces-LP demo [M] (`results/lp183_l1_104.jsonl`, `logs/lp183_104_D0_S1.log`).**  l1_104
root/D0/S1 (S2 at nsub 8 / refine 3: H 0.637 / D 0.299 / S 0.228 kept; b = 8).  Core half-sides a --
stock 0.3715 / 0.2779 / 0.3350; union-box A135 exact 0.3804 / 0.3043 / 0.3742; GROWN inside K' of the
pieces 0.3804 / 0.3069 / 0.3843 (+0 % / +0.9 % / +2.7 %; the union box's core at its own tilt is
already nearly maximal inside the polygon).  LP: tau = 7.999999999999936, CONVERGED, ALIVE(LP), 98 s
(the axis-square variant: tau 8.0000000001 unconverged, 295 s).  So at this node the pieces buy the LP
almost nothing and the LP cannot kill; the geometry (the clip's kills at S2/S3) is the lever.  The
mechanism is settled: v1 consumes the pieces through one grown square core per role; the polygon
itself needs the v4 clause of A183.4.

**A183.6  Alive before / after per step (running tally; [M] from the side files).**
*S1.*  l1_104: 28 ALIVE before (A168) -> 28 ALIVE after (A181 4/2) -> 28 ALIVE after (A183 8/3); the
lever's gain is in the pose volume, not the count: mean kept H 0.549 -> 0.511, D 0.153 -> 0.125, total
vol1 H 2.534 -> 2.358 (-7 %), D 2.292 -> 1.873 (-18 %); 54 s per node for the 8/3 pass on the 4/2
fixed point (root/D0: D 0.448 -> 0.332; root/D1: D 0.086 -> 0.059).  l1_153: 6 -> 6 -> 6 ALIVE; mean
kept H 0.390 -> 0.340, D 0.055 -> 0.033, vol1 H 0.386 -> 0.336 (-13 %), D 0.176 -> 0.107 (-39 %)
(root/D0: D 0.171 -> 0.112; root/D1: 0.021 -> 0.008; root/D2: 0.021 -> 0.007).  Figures
`figs/steps_l1_104_S1.svg`, `figs/steps_l1_153_S1.svg` (before panel = root's seeded fixed point at
8/3; the kept: line prints the setting and the 4/2 numbers).
*S2.*  l1_104: 111 ALIVE before (A168) -> 64 ALIVE / 47 DEAD after (A181/A183): leaves ancestor 20
(a DEAD S1 of the A168 record: R3 lonely), EmptyBox 23 (the pair leaf on the library's polygon +
lonely clip; 4 of them -- root/D0/S14, root/D53/S7, root/D58/S13, root/D58/S14 -- survive 4/2 and die
ONLY at 8/3), inheritance 4 (the seeding empties a role: no pose of the child's record inside the
parent's fixed point).  On the 64 survivors: mean kept H 0.403 -> 0.338, D 0.096 -> 0.077, S 0.157 ->
0.130; total vol1 H 4.251 -> 3.566 (-16 %), D 3.292 -> 2.625 (-20 %), S 5.373 -> 4.461 (-17 %); 102 s
per node; vol1 <= parent on every node.  The PI's two chains: root/D0/S0 seeded H 0.827 / D 0.448 /
S 0.888 -> 4/2 H 0.306 / D 0.254 / S 0.155 -> 8/3 H 0.293 / D 0.204 / S 0.111 (A176 had let its
children settle at D 0.298); root/D1/S0 seeded 0.996 / 0.086 / 0.887 -> 0.674 / 0.034 / 0.129 -> 0.620 /
0.027 / 0.109.  l1_153: 1 -> 1 -> 1 ALIVE (root/D25/S=H: H 0.897 -> 0.873, D 0.070 -> 0.059; the
sliver-era wall cap was stale: 299 s at the full setting).  Figures `figs/steps_<cell>_S2.svg`.
*Bookkeeping [M].*  A181's shard assignment differed from A183's, so a node's 4/2 record in one shard
file was masking its 8/3 upgrade in another under name-order last-wins; `renorm181.load_side` now
keeps the STRONGEST record per node (DEAD > ALIVE at 8/3 > ALIVE at 4/2 > SKIPPED marker) -- the
counts above are on that rule.  The shards themselves were unaffected (a node and its children share
the shard key; the owner's in-memory record is the upgraded one).
