# A143 — the corner-first k0 tree, pilot: canonicalise on the BL corner intruder instead of an interior-zone square; level-1 kill rate with the day's leaves vs the interior root's 22 of 216 (Opus, ≤ 2 CPU-h)

Context (2026-09-07 evening). The PI: "any packing shows up in phase space once per labelling; a packing with a square
near bl00 must be covered by a tree whose conditioned core is near bl00, and that coverage reflects over the
symmetries." The existing k0 tree (A24 zone scheme, A38 `notes/design.md`, `notes/T0_composition.md`; A99 v2;
A115's warm re-solves) quotients D4 × S11 by an EXISTENTIAL interior hypothesis: every packing has a square with
centre in the D4-invariant interior zone Z; level 1 = the fundamental triangle T × 6 tilt windows of 15° = 216 cells,
kills transferred to the 7 D4 images by the machine-checked reduction. A113 found the tree "conditions on an
interior square, and Trump's interior squares are the tilted ones"; the un-killable cells' supports are mostly ROOM
at the corners (K01, 84 cells); A115's corner-crowd ROWS on that tree killed nothing. Today's leaves are strongest
against walls: the polygon core (A132/A135/A140), pin-clip (A131; here the walls play the pins' role), and the K′
lane kill (the PI's s3_far reading, A141: a corner reachable by only one square ⇒ K0-FREE ⇒ dead).

The corner-first canonical choice: condition on the square that meets the BL corner. Root lemma, already a theorem
for k0: a k0 packing is K0-FREE (some corner met by ≤ 1 square — dead by teleport, Lean `teleport_packing` /
`k0free_kill`) or K0-BLOCKED with every corner met by an intruder; k0 means no simple square, so the BL intruder is
tilted (θ ∈ (δ_simple, 90° − δ_simple) with the class's simple-square tolerance — read it from the k0 root definition)
and its centre lies in the corner-meeting zone (within √2/2 of the corner and inside the container). D4 reduces the
four corners to BL; S11 is quotiented by the existential. Level 1 = the corner zone (centre box) × tilt windows; the
tree is an INDEPENDENT cover of k0_00, so it composes with the interior tree (a cell must survive both) and with every
existing k0 kill.

Read first: A38's notes/design.md and T0_composition.md (the root lemma, the D4 reduction, the cell format, budget
10 = 11 − 1), A99's driver (how a k0 cell's LP is set up: hypothesis core, rows, the k0 case-LP), A115's code (the
warm re-solve path and the record format — reuse it), docs/proofs/k0_route.md (teleport / K0-FREE), A141's lane test
with K′ (if landed; else A118's), A135's exactcore.py, A132's polycore.py, A131's pinclip.py (walls as pins),
docs/budget.md §B and the k0 row.

## T1 — the cover (exact, minutes)
Define the level-1 cells: the BL corner-meeting zone for a tilted square (centre (x, y) with x, y ∈ [1/2·(cos θ +
sin θ) − margin…]: the set of poses whose square meets the corner CELL [0, c]² used by the teleport theorem — take the
definition from k0_route.md exactly) × tilt windows (start with 6 of 15°, as the interior tree; then 12 of 7.5° if
the LP asks). Prove the cover: every K0-BLOCKED packing's BL intruder has a pose in some cell (interval check +
sampled confirmation drawn → tested → hits ≥ 10⁴). Apply the geometric leaves BEFORE any LP: (a) container clip (the
walls as pins: the pose must keep the square inside the container — clip the centre box per tilt sub-bin, A131's
mechanism with the container's half-planes); (b) the K′ lane test on the OTHER three corners and on BL itself (M
counts the conditioned square; LANE + M ≤ 1 ⇒ dead) — note BL's own lane: if no OTHER square can meet BL past the
conditioned K′, BL is singly met ⇒ dead outright; (c) the polygon core against the walls. Report how many level-1
cells die by geometry alone.

## T2 — the level-1 LP (≤ 2 CPU-h total, 2 processes BelowNormal)
For the surviving cells: the k0 case-LP with the EXACT axis-aligned core (A135) in the hypothesis and the pool pruned
by K′ (A132; record which columns K′ removed beyond the exact core), 240 s, budget 10; certify converged kills through
the FROZEN verify_case with exact cores (certifiable today per A135); 900 s only at a knife edge. Table: cell ×
(geometry verdict, τ, η, minmass, converged, certified). Kill rate vs the interior root (22 of 216 after A115's
complete pass; 17 at the first pass). Also: which cells the interior tree's alive supports fall into (the twelve
converged-alive cells' supports have a BL intruder — locate it — so the two covers can be intersected: report, for
each of the twelve, whether its BL intruder's pose lies in a corner-first cell that DIED).

## T3 — composition and price
notes/composition.md: the root lemma as used (the K0-FREE / K0-BLOCKED dichotomy, the tilt exclusion from k0's
definition, the D4 reduction — say what is already in Lean and what is new: expected nothing new beyond the cell
cover check), the two-cover intersection rule, and the projected cost of finishing the corner-first tree from the
level-1 rate (A99's per-level model) against the interior tree's 12,000 CPU-h — plus the intersection: the cells of
the interior tree that die because their BL intruder lies in a dead corner-first cell.

Constraints: ≤ 2 processes, BLAS-pinned, BelowNormal, cap 2 CPU-h (the PI is using the machine; A136/A139/A140/A141/
A142 running — count the box, stay ≤ 16 python processes); READ-ONLY on every campaign and attempt (new files only
under attempts/A143-corner-first-k0/); frozen verifiers byte-identical; NO recursive deletes; PYTHONDONTWRITEBYTECODE=1;
git = fetch + plain merge + push own paths with explicit pathspecs. Drawings: one SVG of the level-1 cover (cells
coloured by verdict) and one page per certified kill in A140's format (three cores drawn, legend). Writes: the attempt
dir, registry row, LOG.md, docs/budget.md k0 row one clause, residue_ledger §4 one sentence. Report ONCE: T2's table
and the kill rate first, T1's geometry-only count second, T3 third, pointers last. No interim messages.
