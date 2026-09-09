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
