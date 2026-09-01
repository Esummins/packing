# A59 leg (b) — Level-0 grain census of the trump5 residual polygon

Worker run 2026-09-01. Code: `attempts/A59-trump-residual/code/{geomlib,graphlib0,count_exact,canary,census,completions,lower_bound}.py`.
Spec: `notes/theory.md` §0 and T4 (authoritative). Window `I = [3.82, s0]`, `s0 = 969271/250000`.

---

## HEADLINE

**The Level-0 grain census does not terminate as a list: it is ~4.4 x 10^10 grains.**

| quantity | value | status |
|---|---|---|
| grains, point estimate | **4.4364 x 10^10** (+- 4.3 x 10^8, 1 sigma) | Monte Carlo (caps + full planarity) |
| grains, rigorous UPPER bound | **822 380 205 647** (8.2238 x 10^11) | EXACT (Burnside, filters 1-4 + interleave) |
| grains, rigorous LOWER bound | **2 290 359** | EXACT (proved sub-family, all filters verified) |
| admissible anchor masks | **91** | exact |
| canary (Trump's residual grain) | **PASS** on every hard filter | exact |
| runtime | 193 s (single process, no pools) | |

Consequences, stated plainly:

* The census exceeds the 3 x 10^5 emission threshold by five orders of magnitude, so
  `grains.jsonl` was NOT written; `grains_sample.jsonl` carries 1000 stratified samples.
* It exceeds the 3 x 10^7 stop threshold by three orders of magnitude. **No DFS was run to
  exhaustion** — instead the pairwise part of the filter set was counted EXACTLY (it factors
  over vertex pairs, so Burnside over S6 closes it in seconds), and only the two filters that
  do not factor (capacity caps, full planarity) were estimated by unbiased Monte Carlo.
  This gives an honest number rather than an honest abort.
* **T5's per-grain certificate program is not viable at Level 0 as specified.** At 1 second of
  certificate work per grain the exclusion leg would take 1.4 x 10^3 years. The composition
  theorem needs its enumerated unit coarsened (see §11).

---

## 0. What was enumerated

A grain is `(mu_1..mu_6; E)`: `mu_i` a subset of the 16 anchor elements `{A0..A11, C1..C4}`
touched by free square `i`, `E` the touching graph on the six free squares, counted up to S6
relabelling only (the pin set has trivial D4 stabiliser). Free squares may have empty masks
(rattlers are legitimate here — theory.md G-A59-5) and `E` is unconstrained a priori.

Raw space: 156 S6-classes of graphs x 91^6 mask tuples. Equivalently 2^15 x 91^6 labelled
structures = 1.861 x 10^16, of which 2.611 x 10^13 S6-orbits.

**Why the count factors.** Every hard filter except the capacity caps and full planarity is a
condition on a PAIR of free squares, and which condition applies depends only on whether the
pair is an edge of E:

* non-edge `(i,j)`: masks must coexist and not interleave — predicate `N(a,b)`;
* edge `(i,j)`: additionally the boxes must be able to touch — predicate `T(a,b)`, and
  `T ⊆ N`.

So the number of labelled structures is `Z = sum_m prod_{i<j} w(m_i,m_j)` with
`w = [N] + [T] ∈ {0,1,2}`, and the orbit count is Burnside over S6; for a permutation with
cycles `C_1..C_c` all pairs in one pair-orbit join the same two cycles, so
`Z_p = sum_{a in M^c} prod_{orbits} w(a_u, a_v)`. Every intermediate is an integer below 2^53,
so the float64/BLAS evaluation is exact and the outer accumulation is done in Python ints.
The counter is validated three ways (§10.7).

---

## 1. Admissible anchor masks — 91

| `|mu|` | 0 | 1 | 2 | 3 | 4 | 5 | 6+ |
|---|---|---|---|---|---|---|---|
| count | 1 | 16 | 35 | 27 | 10 | 2 | 0 |

Well inside the "tens-to-hundreds" expectation, so the box construction was not tightened
further. Pair-table densities over the 91 x 91 grid: coexistence 0.8233, touch 0.8657,
interleave 0.1807.

Measured: **max over admissible mask-box pairs of the minimum box distance = 2.786403**, and
`2*sqrt2 = 2.828427`. Hence the hop bound `|c_i-c_j| <= sqrt2 * hops` is **vacuous for
hops >= 2** and coincides with the touching window at hops = 1 (see §2, level 4).

---

## 2. Ablation table (cumulative, in the order of the brief)

| # | filter added | grains (S6-orbits) | x previous | status |
|---|---|---|---|---|
| 1 | per-square anchor-mask admissibility | 26 113 311 517 020 | — | EXACT |
| 2 | + pairwise mask coexistence (BAD table) | 4 617 417 645 080 | 0.1768 | EXACT |
| 3 | + touching window on edges | 1 707 953 952 209 | 0.3699 | EXACT |
| 4 | + hop bound | 1 707 953 952 209 | 1.0000 | EXACT, **vacuous** |
| 5 | + per-element capacity caps | ~1.3537 x 10^12 | 0.7926 | MC (+-0.0006) |
| 6 | + planarity (full, cycle + apex) | **~4.4364 x 10^10** | 0.03278 | MC (+-0.0003) |

Exact side-count on the same chain: applying only the *interleave* consequence of planarity
(the pairwise part, which does factor) to level 4 gives **822 380 205 647** exactly. Since full
planarity implies interleaving-freeness and the caps only remove structures, this number is a
**rigorous upper bound for row 6**.

Reading: coexistence and the touching window each remove roughly a factor 3-6; the caps remove
only 21%; **full planarity is by far the strongest filter** — it removes 96.7% of the
cap-surviving structures, and its cheap pairwise shadow (interleave) accounts for only about
half of that. Planarity also strongly prefers sparse contact graphs: the mean `|E|` over
pairwise-admissible structures is 7.5, over surviving grains 4.83.

---

## 3. Per-prefix growth curve (exact, labelled)

Number of valid `k`-prefixes `(m_0..m_{k-1})` weighted by the number of admissible edge
statuses among them — i.e. the exact node count at depth `k` of the DFS that was not run:

| depth k | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| filters 1-4 | 91 | 12 524 | 2 890 264 | 1 177 982 744 | 8.7535 x 10^11 | 1.2118 x 10^15 |
| filters 1-4 + interleave | 91 | 11 200 | 2 236 252 | 779 338 728 | 4.9330 x 10^11 | 5.8141 x 10^14 |

Branching factor per level (filters 1-4 + interleave): 123, 200, 348, 633, 1179. The branching
factor *grows* with depth (each new square is compared against an already-consistent prefix, so
the surviving mask population per level does not shrink) — this is why prefix pruning cannot
rescue the enumeration.

---

## 4. Breakdown

### 4.1 By number of anchored squares (nonempty mask) — EXACT

Computed by giving the empty mask a formal weight `z`, running the Burnside count at
`z = 0..6`, and interpolating the degree-6 polynomial over Fractions (level: filters 1-4 +
interleave; total 822 380 205 647).

| #anchored | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| grains | 156 | 48 960 | 5 402 800 | 287 031 520 | 8 097 411 096 | 116 943 783 264 | 697 046 527 851 |
| share | 2e-10 | 6e-8 | 7e-6 | 3.5e-4 | 0.0098 | 0.1422 | **0.8476** |

**The explosion is not rattler-driven.** 84.8% of grains have all six squares anchored, 99.0%
have at least five. Forbidding rattlers outright would buy a factor 1.18, nothing more.
(Empty-mask count = 6 - #anchored; the all-rattler grain count 156 is the number of graph
classes on 6 vertices with all pairs mutually touch-compatible for the empty mask, as expected.)

### 4.2 By number of SS edges — Monte Carlo (10 390 surviving samples)

| `|E|` | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | >=12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| share % | 0.16 | 1.51 | 5.53 | 12.84 | 21.84 | 24.54 | 18.88 | 9.76 | 3.88 | 0.87 | 0.14 | 0.04 | 0 |

Mean `|E|` = 4.83, mean `sum |mu_i|` = 9.92 over surviving grains. No surviving sample had
`|E| >= 12`; planarity + the touching window cut the dense end hard.

### 4.3 Joint (anchored, edges) — Monte Carlo

The joint table is in `census_summary.json` (`joint_mc`, 40 occupied cells). Modal cell is
(6 anchored, 5 edges) at 16.6% of survivors; (6,4) 15.9%, (6,3) 10.1%, (5,5) 6.9%.

---

## 5. Per-element usage (Monte-Carlo, over surviving grains)

`grain_frac` = share of grains in which the element is touched at least once;
`mean_mult` = mean number of squares touching it.

| elem | A0 | A1 | A2 | A3 | A4 | A5 | A6 | A7 |
|---|---|---|---|---|---|---|---|---|
| frac | 0.299 | 0.204 | 0.497 | 0.374 | 0.417 | 0.566 | 0.646 | 0.359 |
| mult | 0.339 | 0.229 | 0.607 | 0.445 | 0.483 | 0.711 | 0.848 | 0.414 |

| elem | A8 | A9 | A10 | A11 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|---|---|---|
| frac | 0.375 | 0.546 | 0.459 | 0.441 | 0.633 | 0.740 | 0.691 | 0.617 |
| mult | 0.435 | 0.632 | 0.534 | 0.510 | 0.850 | 1.094 | 0.969 | 0.821 |

The four exposed pin corners C1-C4 are the busiest elements (frac 0.62-0.74) — reflex corners
of R(s) are cheap to touch from three sides and have the loosest centre box (a full
`sqrt2 x sqrt2` square rather than a thin slab). Rarest: A1, the exposed stretch of the bottom
wall, length `s-3 = 0.877` (cap 2), and A0.

---

## 6. Capacity caps actually used (all PROVED, see §10.5)

Segment caps from `1 + floor(span / 0.9783183)` where `span` is the tangential extent of the
element's own certified centre box after intersection with the admissible core, maximised over
the eight s-sub-intervals; `0.9783183 = sqrt(1 - (sqrt2/2 - 1/2)^2)`.

| A0 | A1 | A2 | A3 | A4 | A5 | A6 | A7 | A8 | A9 | A10 | A11 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 2 | 3 | 3 | 2 | 3 | 3 | 2 | 2 | 2 | 2 | 2 | 3 | 3 | 3 | 3 |

These are **tighter than the brief's suggested formula** (`span = seglen + sqrt2`) in two ways,
both proved in §10.5: the tangential reach of a centre from its contact point is `1/2`, not
`sqrt2/2`; and the centre box is clipped to the admissible core `[1/2, s0-1/2]^2`. theory.md's
hand-computed values are reproduced (A1 cap 2, corner cap 3) and A0, A4, A7-A11 come out at 2
rather than 3.

**Corner cap is 3, not 4** — the clean proof exists (§10.5b) and uses the pin: two centres on a
corner element are at angular separation >= 90 degrees about the corner, and every admissible
centre lies in the closed 180-degree arc facing away from the pin.

---

## 7. Canary — PASS

Derived BY CODE from `A03-upper-reconstruct/trump11_float.json` (contacts at tol 1e-9;
free squares 4, 6, 7, 8, 9, 10; contacts exactly at a pin corner attributed to the corner
element only, implemented by pulling each corner-adjacent segment end back by 1e-7):

| square | centre | derived mu |
|---|---|---|
| sq4 | (0.500000, 2.532558) | {A0} |
| sq6 | (1.536287, 3.172475) | {A3} |
| sq7 | (1.688559, 1.959613) | {C1} |
| sq8 | (2.424525, 1.272254) | {C2, C3} |
| sq9 | (2.436509, 2.623834) | {C4} |
| sq10 | (3.172475, 1.936475) | {A2} |

`E = {(4,6), (4,7), (6,9), (7,8), (7,9), (8,10), (9,10)}`.

**The derived grain is identical to the one asserted in theory.md T4** — masks and all seven
edges. Verified: every mask is in the 91-mask admissible list; every mask box contains the
actual Trump centre (tightest: sq6's `c_y = 3.172475` against the A3 lower bound
`s_lo - sqrt2/2 = 3.169974`, margin 2.5e-3); all 15 pairs coexist and none interleave; all
seven edges satisfy the touching window; caps hold (every element used at most once);
the full planarity test passes.

---

## 8. Side task — the eight one-cell Young completions of trump5

`results/completions.json`. Exact Fraction arithmetic at `s = s0 = 969271/250000`; matching
against A53's 33 D4-classes of `k = 6` Young 4-tuples (`skeletons_young.json` classes cross-
checked index-by-index against `name_to_slots.json`).

| completion | added slot | k6 class | D4 op |
|---|---|---|---|
| BL+(2,0) | (5/2, 1/2) | **none — infeasible** | — |
| BL+(1,1) | (3/2, 3/2) | k6_19 | refl_d |
| BL+(0,2) | (1/2, 5/2) | k6_07 | id |
| BR+(1,0) | (s-3/2, 1/2) | **none — infeasible** | — |
| BR+(0,1) | (s-1/2, 3/2) | k6_21 | refl_d |
| TR+(1,0) | (s-3/2, s-1/2) | k6_24 | refl_d |
| TR+(0,1) | (s-1/2, s-3/2) | k6_22 | refl_d |
| TL+(0,0) | (1/2, s-1/2) | k6_23 | id |

**TL+(0,0) -> k6_23 reproduces theory.md T2.1's own annotation exactly** (independent check of
the matcher).

**FINDING — T2.1 over-counts: there are SIX completions, not eight.**
`BL+(2,0)` puts a slot square at `(5/2, 1/2)` while BR already occupies `(s-1/2, 1/2)`; the
x-gap is `s - 3 ∈ [0.820, 0.877084] < 1` and the y-gap is 0, so the two unit squares overlap
for **every** `s` in the window. `BR+(1,0)` at `(s-3/2, 1/2)` overlaps BL's `(3/2, 1/2)` by the
same `s - 3 < 1`. Neither is a Young 4-tuple with pairwise interior-disjoint slot squares, so
neither appears among A53's 1110 tuples and no packing can realize it — they are vacuously
killed. (This is exactly A53 L2(iii): column offsets `i + j = 2 ∈ {2,3}`.)

T2.1's theorem survives unchanged: a maximal chain from trump5 up to any strictly larger Young
tuple `S` has its first step inside `S`, hence pairwise disjoint, hence one of the six feasible
completions.

**Actionable for G-A59-1 / A56:** the s-parametric transfer is needed for **six** k = 6 classes,
not eight — `{k6_07, k6_19, k6_21, k6_22, k6_23, k6_24}`. Five carry A53 PASS certificates at
s0; `k6_23` is the class A53 left open and A54 W1 closed. That is the priority list to request.

---

## 9. Level-1 decoration fan-out per grain (arithmetic only)

A31's gauge-fixed menu (verified against `A31/results/level1.json`: the row `Ess=0, Esw=6` has
`gauge_menu = 64 = 2^6`, the row `Ess=1, Esw=4` has `gauge_menu = 320 = 20 * 2^4`):

    decorations(grain) = 20^|E| * 2^(sum_i |mu_i|)

Over the surviving grains (`|E|` mean 4.83, `sum |mu_i|` mean 9.92), `log10` of the menu size:

| statistic | median | mean | p95 |
|---|---|---|---|
| log10 decorations/grain | 9.21 | 9.28 | 12.72 |

So a typical grain carries ~1.6 x 10^9 Level-1 decorations, and by Jensen the Level-1 object
count is at least `4.44e10 * 10^9.28 = 8.4 x 10^19` (the tail at p95 = 10^12.7 pushes the true
expectation higher). A31 measured tilt-propagation survival of 2-14% at k = 4, falling with
`|E|`; applying that optimistically still leaves **~10^18-10^19 Level-1 objects**.

Two honest caveats on this arithmetic:

* the "2 per square-anchor contact" gauge is A31's WALL menu (flush / corner-on-wall). A contact
  at an exposed pin corner `C_j` has its own menu (square vertex AT the corner, or square edge
  THROUGH the corner: 4 + 4 raw), and pin corners carry roughly 3.7 of the mean 9.92 anchor
  contacts, so 2 is a lower estimate there;
* a corner contact also leaves a continuous parameter (where along the square's edge the pin
  corner sits). That is cell geometry, not a discrete decoration, and is not counted above — it
  feeds the A43 cell-subdivision multiplier that theory.md's T4 remark warns about.

---

## 10. Filter soundness

Every filter below is a NECESSARY condition on any point of `F` with `s` in `I`, so pruning on
it cannot remove a realizable grain. Nothing else was pruned; all occupancy / loadedness /
Maxwell statistics are SOFT and reported only (10.10), per theory.md T4 and A43.

**10.1 Certified centre boxes (filter 1).**

*Segment element.* A unit square touching the element lies on its free side with a contact point
`q` on the element; the distance from the centre to the element's line is the square's half-width
in the normal direction, hence in `[1/2, sqrt2/2]`; `q` lies in the square so `|c-q| <= sqrt2/2`,
and since the normal part is at least `1/2` the tangential part is at most
`sqrt(1/2 - 1/4) = 1/2`.

*Corner element.* Interiors are disjoint, so the pin corner `C` lies on the free square's
boundary; every boundary point of a unit square is at distance in `[1/2, sqrt2/2]` from its
centre, giving an annulus, relaxed to its bounding box.

*Admissible core.* The square lies in `[0,s]^2` with `s <= s0`, so `c` is in
`[1/2, s-1/2]^2`, a subset of `[1/2, s0-1/2]^2`.

*Pin separation.* Two interior-disjoint unit squares have `|c - p| >= 1` (each contains the open
disc of radius 1/2 about its centre; those discs are disjoint). A mask is pruned only when the
whole widened box violates this for EVERY admissible position of some pin — for the moving pins
P4, P5 the max over `s` of `|c - P(s)|` is attained at an endpoint of the sub-interval (it is
convex in `s`), so testing the two endpoint positions is exact for the test used.

*Two elements in one mask.* Both contact points lie in one closed unit square, of diameter
`sqrt2`, so the two elements' point sets come within `sqrt2` of each other.

*s-window.* Every element position is AFFINE in `s`, so the union of a box over a sub-interval
is the interval hull of its two endpoint values. The window is split into 8 sub-intervals and a
mask is kept if it is feasible in at least one — the realized `s` lies in one of them, and there
the widened box contains the true box. Contacts exactly at a pin corner are attributed to the
corner element only; the segment boxes are nevertheless taken over the CLOSED segment, which is
a superset, hence sound.

**10.2 Pairwise coexistence (filter 2).** Two interior-disjoint unit squares have
`|c_i - c_j| >= 1`; if the maximum distance between the two centre boxes is below 1, no pair of
points in them can be 1 apart. NECESSARY.

**10.3 Touching window (filter 3).** If squares `i, j` touch, a common boundary point lies in
both, each within `sqrt2/2` of its centre, so `|c_i - c_j| <= sqrt2` (and at least 1 by 10.2).
If the minimum distance between the boxes exceeds `sqrt2` the edge is impossible. NECESSARY.
The below-1 cases (overlapping boxes) are recorded, never pruned: 2485 of the 8281 ordered mask
pairs have minimum box distance 0.

**10.4 Hop bound (filter 4).** Along a chain of `d` contacts the triangle inequality gives
`|c_i - c_j| <= sqrt2 * d`. NECESSARY, but MEASURED VACUOUS on R(s): the largest minimum
distance between any two admissible mask boxes is 2.786403, below `2*sqrt2 = 2.828427`, so the
bound never bites at `hops >= 2`, and at `hops = 1` it IS filter 3. Level 4 of the ablation is
therefore identical to level 3 — a proved statement about R(s), not a coding shortcut.

**10.5a Segment capacity caps (filter 5).** Two squares touching the same segment element have
normal coordinates inside an interval of length `sqrt2/2 - 1/2 = 0.207107`, and centres at least
1 apart, so their tangential coordinates differ by at least
`sqrt(1 - 0.207107^2) = 0.9783183`. All such centres lie in the element's certified centre box
(10.1), whose tangential extent after clipping to the admissible core is `span`. Hence at most
`1 + floor(span / 0.9783183)` squares touch the element. NECESSARY. Values in section 6.

**10.5b Corner capacity cap = 3 (filter 5).** Let `C` be an exposed pin corner and `p` the
centre of its pin, so `|C - p| = sqrt2/2`. Write an admissible centre as
`C + rho*(cos phi, sin phi)` with `phi` measured from the direction `C` to `p`, and
`rho` in `[1/2, sqrt2/2]` by 10.1.

  (i) *Pairwise 90 degrees.* For two centres,
  `|c1-c2|^2 = rho1^2 + rho2^2 - 2*rho1*rho2*cos(a)` is convex in each `rho_i`, so its maximum
  over `[0, sqrt2/2]^2` is attained at a vertex of that square and equals `max(1/2, 1 - cos a)`;
  if `a < 90` degrees this is below 1, contradicting `|c1-c2| >= 1`. So the angular separation
  about `C` of any two such centres is at least 90 degrees.

  (ii) *180-degree admissible arc.* `|c - p| >= 1` reads
  `rho^2 + 1/2 - sqrt2*rho*cos(phi) >= 1`, i.e. `cos(phi) <= (rho^2 - 1/2)/(sqrt2*rho) <= 0`
  since `rho <= sqrt2/2`. So every admissible centre has `phi` in the CLOSED 180-degree arc
  `[90, 270]` degrees.

Three points in a closed 180-degree arc with pairwise gaps of at least 90 degrees is the
maximum (four would need three gaps totalling at least 270 > 180). Cap = **3**. NECESSARY.
The brief allowed falling back to 4; the pin makes 3 provable.

**10.6 Planarity (filter 6).** `R(s)` is a simply connected polygon (all three pin blocks are
corner-attached to the container boundary) whose boundary walk visits the 16 anchor elements in
the cyclic order of theory.md section 0. In the actual configuration, draw for each free square
the straight segments from its centre to its contact points; these lie inside that square, the
squares have pairwise disjoint interiors, and each square-square contact segment lies in the
union of the two squares. Together with the boundary curve of `R(s)` this is a plane graph.
Contract each of the 16 boundary arcs to a single vertex: contracting connected subgraphs of a
plane graph yields a MINOR, hence a planar graph, and the 16 contracted vertices remain on the
outer face in the boundary cyclic order. Adding an apex vertex in the outer face joined to all
16 keeps it planar. So `G(grain) + 16-cycle + apex` is planar. NECESSARY. This is strictly
stronger than abstract planarity of `G(grain) + 16-cycle`, and it is the version the geometry
actually gives.

*Cheap pairwise shadow used in the tables (interleave).* If `mu_i` and `mu_j` contain four
distinct elements appearing in cyclic order `a, b, c, d` with `a, c` in `mu_i` and `b, d` in
`mu_j`, then in the disc bounded by the cycle the path `a - i - c` separates `b` from `d`, and
square `j` cannot reach both. NECESSARY. (Contract `i` into the edge `a-c` and `j` into `b-d`:
`K4` on `{a,b,c,d}` plus the apex is a `K5` minor.)

**10.7 Validation of the counter.**

  (a) With all weights equal to 1 the Burnside routine returns the number of 6-multisets of
  masks, `C(n+5,6)`; checked for `n = 5` and `n = 7`.
  (b) Against a brute-force orbit enumeration (all labelled graphs x mask tuples, canonical form
  over all of `S_k`) on random `{0,1,2}` weight matrices for `k = 3` and `k = 4`, three trials
  each: exact agreement (51/51, 284/284, 82/82, 281/281, 49/49, 287/287).
  (c) The fast symmetric identity path agrees with the generic path on a random 9-mask matrix.
  (d) Independently, the Monte-Carlo interleave pass rate 0.479658 matches the exact LABELLED
  ratio `Z_id(interleave)/Z_id(level 4) = 581412051461424 / 1211807015741424 = 0.479789`
  to 0.17 sigma.
  (e) A first version of the interleave predicate was not symmetric (cycle positions were listed
  in element-index order rather than sorted); the Burnside divisibility assertion
  (`sum_p Z_p` divisible by 720) caught it immediately.
  (f) Planarity spot checks: empty masks with `K6` and with `K5` -> non-planar; with `K4` ->
  planar; an interleaving mask pair with no edges -> non-planar; a nested pair -> planar.

**10.8 Rigorous lower bound.** Counted exactly: grains with `E` empty whose six masks are
pairwise element-disjoint, pairwise coexistent and pairwise non-crossing. On that family the two
non-factoring filters hold automatically — caps because every element is touched at most once
while every computed cap is at least 2; planarity because with no square-square edges the six
supports form a pairwise disjoint, pairwise non-crossing (laminar) family of stars, realizable
by pairwise disjoint trees inside the disc. Count: **2 290 359**. Every member survives every
hard filter, so the census is at least that. This bound is very lossy — it exists only to make
"larger than the 3e5 emission threshold" a theorem rather than an estimate.

**10.9 What is ESTIMATED, not proved.** Rows 5 and 6 of the ablation and the headline
`4.4364e10`. The estimator is rejection sampling: `m` uniform on `M^6`, accepted with
probability `w(m)/2^15`, then an edge set drawn uniformly among the admissible ones — exactly
uniform on LABELLED level-4 structures. 400 000 accepted samples out of 6 200 000 raw draws.
The reported number multiplies the exact ORBIT count at level 4 by the labelled pass rate;
because 98.5% of orbits have trivial stabiliser (`orbits * 720 / Z_id = 1.0148` at level 4 and
`1.0184` at level 6a) this substitution costs well under 1%, below the precision claimed.
Binomial 1 sigma on the pass rate is 0.00025 (about 1% relative).

**10.10 SOFT statistics (reported, never pruned).** Fraction of surviving grains with all six
squares anchored AND the square-square graph connected: 0.195. Fraction with every square
"loaded" in the Maxwell sense `deg_E(i) + |mu_i| >= 2`: 0.638. Empty-mask counts: section 4.1.
None of these was used to prune (A31: Maxwell counts are met by zero survivors; A43: existential
filters are vacuous — not repeated here).

---

## 11. Findings the PI should act on

**11.1 The Level-0 grain is the wrong certificate unit — by 10 orders of magnitude.** T5's
composition theorem asks for one X1-X5 certificate per grain. At ~4.4e10 grains that is
infeasible for any per-grain cost, and A43's law reappears exactly as theory.md's T4 remark
predicted (cell subdivision then multiplies on top). The census is not the bottleneck; the
per-grain obligation is.

**11.2 Where the count actually lives — and what does NOT help.**

  * Rattlers are not the problem: 84.8% of grains have all six squares anchored (exact,
    section 4.1). Banning empty masks buys a factor 1.18.
  * Loadedness does not help much either: 63.8% of grains already have every square at
    Maxwell degree >= 2, and it is a SOFT condition anyway.
  * Connectivity is the one cheap structural restriction with real bite: only 19.5% of grains
    have a connected square-square graph with all squares anchored — a factor 5. Still not
    enough, and still not a proved necessary condition.
  * The genuinely strong filter is PLANARITY (factor 30 beyond the caps), and its exact
    pairwise shadow captures only half of that. If more of full planarity could be pushed into
    a factorable (pairwise or triple-wise) predicate, the exact count would tighten, but the
    order of magnitude would not move.

**11.3 What would move the order of magnitude.** The fan-out driver is `91^6`: 91 masks per
square with 16 anchor elements and near-free pairing. Options, in decreasing attractiveness:

  * *Coarsen the grain.* Group anchor elements into a few classes (e.g. wall / staircase /
    BR-block / TR-block / corner) and certify per coarse grain with the fine structure handled
    inside one certificate region. This is the A35-anchored regime the T4 remark argues for and
    it is exactly what makes the residual problem "certify in minutes" per object.
  * *Use FJ/criticality at Level 0.* Every filter used here is a CONTAINMENT filter — precisely
    the F4 lesson of A45-A47 and A53 L6(ii). A Fritz-John-necessary condition applied at the
    grain level (e.g. a per-grain Farkas direction refuting the whole grain at once, the (W')
    form) would prune on criticality rather than metric feasibility, which is where the mass is.
  * *Do not* invest in tighter centre boxes: the 91 masks are already close to minimal (all 16
    singletons and 35 of the 120 pairs survive) and halving the mask count only divides the
    census by `2^6 = 64`.

**11.4 The completion list is 6, not 8** (section 8) — a direct, immediate reduction of the
G-A59-1 / A56 dependency. Priority list for the s-parametric transfer:
`k6_07, k6_19, k6_21, k6_22, k6_23, k6_24`.

**11.5 Trump's grain is unremarkable in the census.** It has 6 anchored squares, 7 edges,
`sum |mu_i| = 7`. The MC-estimated share of the (6 anchored, 7 edges) cell is 4.7% of grains,
i.e. roughly 2 x 10^9 grains share Trump's coarse profile. There is no Level-0 signature that
singles it out — consistent with theory.md G-A59-3's warning that the discriminating work all
lives at the geometric level, not the combinatorial one.

---

## 12. Files and reproduction

    code/geomlib.py       R(s), 16 anchor elements, centre boxes, caps, interleave predicate
    code/graphlib0.py     S_k graph representatives with Aut (A31 lib0 pattern, copied)
    code/count_exact.py   exact Burnside orbit counting for the factorable filter set
    code/canary.py        derives Trump's residual grain from A03 float data
    code/census.py        driver (masks, canary, exact ablation, MC, samples, outputs)
    code/completions.py   the 8 one-cell completions -> A53 k6 classes (exact Fractions)
    code/lower_bound.py   standalone rigorous lower bound (also inlined in census.py)

    results/census_report.md     this file
    results/census_summary.json  machine-readable
    results/grains_sample.jsonl  1000 stratified sample grains, canonical (lex-min over S6)
    results/completions.json     side task
    results/lower_bound.json     rigorous lower bound
    logs/census.log              progress

`python census.py` (single process, no pools, ~193 s: 12 s per exact Burnside run x 12 runs,
~50 s Monte Carlo). `python completions.py` is instant. `grains.jsonl` was NOT written: the
census exceeds the 3e5 emission threshold (rigorously, by 10.8).
