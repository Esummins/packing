# A166 — composition, the window transfer, and the price of the nearest-corner sub-tree

Companions: `notes/method.md` (the stages and Lemma A166-1), `notes/canary.md` (the soundness
correction the canary forced), `notes/certificate_bug.md` (the `make_certificate` exact-core reversion
and its consequences for other attempts), `notes/tables.md` (all generated tables),
`docs/proofs/k0_route.md` §§3, 4.1–4.2, `attempts/A143-corner-first-k0/notes/composition.md` §§1, 3,
6 and `attempts/A150-four-corner-product/notes/composition.md` §§1, 5, 6 (the numbers A166 is measured
against), `docs/budget.md` k0 row.

---

## 1. What A166 adds to the k0_00 route, stated as a rule

> **Rule NC (nearest-corner sub-tree).** Let `X` be a node of the interior-first k0_00 tree with
> conditioned box `B_H`, and let `c` be the corner nearest `B_H`'s centre (for every node of A38's
> tree, `c = TR`: the D4 fundamental triangle lies in the TR quadrant). Then `X` splits into
>
> * **branch (a)**, one child per unordered pair `(X_1, X_2)` of cells of A143's 216-cell corner
>   cover that survive A166's stages — hypothesis `[B_H, X_1^clip, X_2^clip]`, budget 8; and
> * **branch (b)**, one child per surviving cell `X_1` — hypothesis `[B_H^meet, X_1^clip]`,
>   budget 9 — which exists **iff** some pose of `B_H` meets `int B_c^w`.
>
> These two branches are a COVER of `X` (`code/pick166.py`'s docstring carries the proof), so `X` dies
> when all children of both branches die. Branch (b) is the part the brief's "3-box node at budget 8"
> omitted, and omitting it produces an unsound kill of `l1_153` (`notes/canary.md`).

The value of the rule is entirely in how much of branch (a) the geometry removes before any LP, and in
whether branch (b) exists at all.

## 2. The two measurements that decide it, over the WHOLE open k0 pool

`code/price166.py`, `results/price166_wmax.json`. Pool: A115's 166 open k0_00 records
(`cells140.open_pool`) minus the 47 killed by A141's `K'` lane leaf = **119 remaining open k0_00
cells**; 118 carry one hypothesis box, one carries two.

| quantity | measurement |
|---|---|
| nearest corner | **`TR` on 117 of 119**, `BL` on 2 (`s1cor_near_b178`, `s2_near_046_619`) |
| `d(z_H, corner)` | min 1.5715, Q1 1.9489, median 2.1216, Q3 2.3265, max 2.5943 |
| `H` can meet `int B_TR^w` (A161 exact) | yes on 53, **no on 66** |
| the crossover | `can_meet = True` only for `d ∈ [1.5715, 2.0573]`; `can_meet = False` only for `d ∈ [2.0127, 2.5943]` |

and, on the eleven plus a 41-cell sample of the pool, the size of branch (a) (`results/price166_wmax.json`
`sample`; the sampled stage omits `(P1s)`, `(MUT)` and `(DIST)`, so it is a 0–4 % over-estimate — it
gives 149 where the full stage gives 139 on `l1_104`):

| `d` band | cells in the sample | surviving pair cells |
|---|---|---|
| <= 1.93 | 14 | 0 - 66 |
| 1.93 - 2.05 | 16 | 4 - 129 |
| 2.05 - 2.20 | 6 | 55 - 197 |
| 2.20 - 2.60 | 5 | 69 - 355 |

Over the 41-cell sample: min 0, Q1 9, **median 25**, Q3 91, max 355, mean 70.5; **zero on 7 of 41, and ALL 7 of those have `can_meet = True`** (`s2_near_046_619`, `l1_159_sh3_warm`, `node_159`, `node_121`, `node_123`, `node_125`, `node_153`).

> **[F] A166's (C) leaf — "branch (a) empty AND branch (b) impossible", i.e. a kill by pure geometry
> with no LP and no certificate — is available on ZERO of the 119 remaining open k0_00 cells, and the
> reason is structural, not a matter of resolution.** Branch (a) empties only when `H` is close enough
> to the corner to crowd the whole corner-meeting zone — measured, **every one of the 11 + 41 cells
> with an empty branch (a) has `d ≤ 1.9319`**, and none above it does; branch (b) disappears only when
> `H` is far enough that no pose of `B_H` reaches the widened corner box, and **the smallest `d` with
> `can_meet = False` anywhere in the pool is 2.0127**. So the two conditions live on either side of
> the gap `d ∈ (1.9319, 2.0127)` and never coincide; the smallest `can_meet = False` cell (`l1_148`
> and its two aliases) already keeps 25 surviving pair cells. The overlap region `d ∈ [2.0127, 2.0573]`
> contains **exactly 5** `can_meet = False` cells — `l1_148_plain_warm`, `l1_148_sh3_warm`, `node_148`
> (the same box, `d = 2.0127`), `node_184` and `node_185` (`d = 2.0344`) — and **all five were staged
> directly and keep 25, 25, 25, 91 and 87 surviving pair cells**. The emptiness is therefore not
> "unmeasured on the boundary": every candidate in the pool is decided.

This is the same shape of obstruction A155 found from the other end (the 2-crowd space is thin, but a
box cover cannot see it) and A158 found in the tilt variable (the `S` narrow enough for the YES child
exempts no LP row): **the two conditions A166 needs are each individually cheap and jointly empty.**

## 2a. The PI's prediction, decided (and the coordinator's two additions)

The brief predicted: *for a Trump-like `H` whose nearest corner is SIMPLE in Trump, forcing that corner
doubly met contradicts the Trump-like packing and the LP dies at once; only the `H` adjacent to the
non-simple corner survives its sub-tree.* Measured (`notes/tables.md` §2, §3):

| `H`'s nearest corner in its matching Trump image | cells | Trump pose distance | `d(z_H, TR)` | budget-8 pair cells |
|---|---|---|---|---|
| **SIMPLE** | `l1_153`, `l1_159`, `l1_158`, `l1_124`, `l1_148`, `l1_104` | 0.0000, 0.0261, 0.0381, 0.2263, 0.2263, 0.1715 | 1.85 – 2.16 | **0, 0, 0, 0, 25, 139** |
| **NON-SIMPLE** | `l2_p114_001`, `l2_p74_001`, `l1_071`, `l2_p65_111`, `l2_p65_101` | 0.5596, 0.1886, 0.5596, 0.7263, 0.7263 | 2.04 – 2.39 | **16, 60, 371, 178, 237** |

So the prediction is **right in direction and wrong in consequence**. Right: the six cells whose nearest
corner is SIMPLE in Trump are exactly the six with the closest Trump matches and the smallest
`d(z_H, TR)`, and four of them have their budget-8 branch **annihilated** — forcing `TR` doubly met by
two squares OTHER than `H` is indeed contradictory there. Wrong: that is not a kill, because those same
four are precisely the cells where `H` itself can reach the widened corner box, so the degenerate branch
(one of the two meeters IS `H`) survives — and on `l1_153` it MUST, since Trump `g4` realises it. The
five NON-SIMPLE cells all survive the budget-8 branch with 16–371 pair cells, so "only the `H` adjacent
to the non-simple corner survives" is exactly backwards as a statement about which branch is empty.

**Coordinator's addition (1): which interior square, and simple or not.** All eleven match one of
Trump's three INTERIOR tilted squares `sq7`, `sq8`, `sq9` (the other two tilted squares, `sq6` and
`sq10`, are flush against a wall). `sq9` is the match for `l1_153` (exactly), `l1_159`, `l1_148`; `sq8`
for `l1_104`, `l1_124`, `l1_158`; `sq7` for the five NON-SIMPLE cells — and `sq7` is precisely the one
whose matches are POOR (pose distance 0.19–0.73), i.e. the third interior square is not what the hard
cells look like. The prediction "the third interior square is nearest the three-simple corner
`BL[2,1]` and should die fastest" does not survive: `sq7` in `g0`'s frame is nearest `TL` (2.554) with
`BL` a close second (2.586), and the cells that match it are the ones the geometry hits LEAST.

**Coordinator's addition (2): the quadrant census** (`notes/tables.md` §6, split at `s0/2`). Trump's own
census is `3/3/3/2` in every image — **never** `2` in the non-simple quadrant. The quadrant holding only
two centres is the one **diagonally opposite the THREE-SIMPLE corner**, in all eight images without
exception (`g0`: three-simple `BL`, sparse `TR`; `g4`: three-simple `BL`, sparse `TR`; and so on). So the
stated diagnostic — "the non-simple quadrant holds exactly the two meeter centres and nothing else, and a
third centre there is off Trump's pattern" — separates nothing: the non-simple quadrant always holds a
third centre, and that third centre is always one of the three interior tilted squares (for `g0`'s
non-simple `TL` it is `sq7`, the `TL`-adjacent interior square). The corrected signature is *one sparse
quadrant, diagonally opposite the three-simple corner*. On the eleven, the dual support's sparsest
quadrant is `TR` on 8 of 11 (`l1_071` and `l2_p65_101` have it at `BR`), i.e. thin exactly where `H` and
the forced corner crowd both live — consistent with the geometry above, but the support sizes (10–83
placements) are not comparable one-for-one with Trump's 11 squares, so this is a shape statement, not a
count.

## 3. What A166 does buy, and it is not nothing

1. **A factor 11 to ∞ on branch (a).** The generic corner-first pair root has 4 244 live pair cells
   (23 436 unordered pairs; A143's chain kills 82 %). Conditioning on `H` leaves 0 … 371 — a further
   cut of 91 % to 100 %, for 3–95 CPU-s per cell after a shared 100 CPU-s census. **74–182 of the 216
   cover cells (34–84 %) cannot hold a corner meeter distinct from `H` at all**, because a square
   there would have to overlap `H`'s own square. The cut is `H2`/`H1`; `DEAD_R` (A161's exact reach
   test) removes a further constant 16 cells at every node, and A143's `(P2)`/`(P1)`/`(P1s)` and
   A158's mutual clip (applied FIRST, per tilt sub-bin) remove only 0–26 pairs on top of the `H` stages.
2. **Four of the eleven now carry only a two-core hypothesis.** On `l1_124`, `l1_153`, `l1_158`,
   `l1_159` branch (a) is empty, so *if either of the two `TR` meeters is not `H`, the node is
   contradictory*: the node's remaining content is "`H` itself is one of the two `TR` meeters and the
   other is one of 3–20 named cover cells". That is a strictly stronger statement than A115's node and
   than A141/A159's near-miss reading, and it is the first time the five TR near-miss cells have been
   pinned from the K0-BLOCKED side rather than the lane side.
3. **A free 26 % cut of A143/A150/A155's own corner cover, `H`-independent.** A161's exact
   `box_misses_cell_exact` certifies that 16 of the 216 corner cover cells hold no corner-meeting pose
   at all (A155's reach clip cannot see them: it uses only the corner box's normals). That removes
   1 118 of the 4 244 alive pair cells at `w_max` and 970 of 3 646 at `w0` — read A143/A150/A155's
   censuses as 3 126 / 2 676. Cost: 0.
4. **A proof of `M = 0` where A141 had a sampled 0.** A141/A148 record `TR(0,0): M 0?` on six of the
   eleven (`docs/shadows/k0v4/review_k0v4.csv`, `lane_bounds` `M=0` with a question mark). A161's
   `box_misses_cell_exact` **certifies** it on exactly those six, and refutes it on the five near-miss
   cells. Over the pool that is 66 certified `M = 0` corners. This is a free strengthening of A141's
   lane ledger and it is what makes branch (b) decidable at all.
5. **An LP mechanism worth a unit of `η`** — see §4.

## 4. The LP, and where it sits between A143 and A150

See `notes/tables.md` §5 for the run. Read against the two reference points:

| conditioning | budget | `η` | converged kills |
|---|---|---|---|
| A115 / A38, the interior cell alone | 10 | `0.000` on all eleven (that is what "converged-alive" means) | 0 |
| A143, ONE square at BL, no `H` | 10 | −0.044 / −0.633 / −0.000 | 0 |
| A143, TWO squares at BL, no `H` | 9 | −0.083 / −0.077 | 0 |
| **A166, `H` + TWO squares at `TR`** | **8** | see `tables.md` §5 | see `tables.md` §5 |
| **A166, degenerate branch (`H` a meeter + one more)** | **9** | see `tables.md` §5 | see `tables.md` §5 |
| A150, FOUR squares, one per corner, no `H` | 7 | −6.0 … +1.08, median −1.0 | 7 of 13, **7** verifier PASS (4 as A150 recorded them; the other 3 recovered by §7.0's exact-core fix) |

> **The one converged budget-8 kill is CERTIFIED, and getting it certified uncovered a bug in shared
> machinery — see `notes/certificate_bug.md`.** `l2_p65_101_b8_005_512` converges at `τ = 7.000000`
> against budget 8 in 118–134 s, and the frozen verifier first reported 32 HOLES at every one of five
> separation rounds. The cause is not the LP: `caselp.make_certificate` rebuilds the hypothesis with
> `Hyp.from_json`, which reverts A135's EXACT cores to the STOCK ones, so the certificate exempts a
> smaller core than the LP was allowed to ignore. All 32 holes are the single placement
> `(3.35109, 1.49, 0°)`, at SAT depth **+0.0296 against the exact core** and **−0.000001 against the
> stock core**, with `exact_mass = 0`. Carrying the exact cores (sound: A135's `exact_a` certifies
> `K(B) ⊆ Q(p)` for every pose in `B`) gives **PASS on the frozen `verify_case.py` at every scale
> 1.005 … 1.14 and every denominator 1e6 / 1e9 / 1e12 — 15 of 15**. And the same substitution turns
> **5 of 5 of A150's previously-FAILing certificates into PASSes**, so A150's four-corner root is 7
> converged kills / **7 certified**, not 4.

The structural expectation, and it is what the run shows: A158b's **exact-1 accounting** (`addendum_b`
§1 — adding a square to the hypothesis removes exactly one unit of dual packing *and* exactly one unit
of budget, so the child returns to `τ = budget`) is the default, and the only thing that beats it is
cores that are SPREAD, which is what A150's four corners had and what A166's three (one interior, two
at the same corner) only partly have. The degenerate branch at budget 9 is the worst case of all: it
adds one core at the corner nearest `H`, i.e. exactly A143's "second core at the same corner" geometry,
and A143 measured that at `η ≈ −0.08`.

## 5. The window transfer, exactly

Every A166 statement above is made at the pad `w_max = (λ_max − 1)(1 + √2/2) = 0.0255100742`, so it is
a WINDOW statement and needs no parametric verifier. The chain, in full:

1. Let `P` be a k0_00 packing at side `m ∈ [3.82, ŝ]`, `λ = s0/m ∈ [1, λ_max]`, `F = Δ_λ P`. By
   Lemma B.0 (`closed_disjoint_bridge.md`) `F` is a strictly disjoint closed 11-family in `[0, s0]²`
   with positive margins at all four walls.
2. A38's interior-first cover is a cover of poses of `F` **at the fixed side `s0`**, so
   "some square `H` of `F` has pose in `B_H`" is a fixed-side statement (Lemma K0-D4 for the orbit
   quotient).
3. Lemma K0-FREE (`k0_route.md` §3): either some corner box `B_c(m)` of `P` is met by ≤ 1 square of
   `P` — a **(T)** leaf, `P` does not exist for `m < ŝ` and is a Trump image at `m = ŝ`, consuming
   k1_00's tree (obligation **K0-O1, still OPEN**, ~200–300 CPU-h, ∀-packings, paid once for the whole
   window) — or every corner box of `P` is met by **≥ 2 distinct** squares of `P`.
4. Lemma K0-WIDEN (`k0_route.md` §4.1) sends each meeter `Q` of `int B_c(m)` to a meeter `Δ_λ Q` of
   `int B_c^w(s0)` with `w = (λ − 1)(1 + √2/2) ≤ w_max`; `Δ_λ` is injective, so distinctness is
   preserved. Hence `F` has two distinct squares meeting `int B_c^{w_max}(s0)`, since
   `B_c^w ⊆ B_c^{w_max}`.
5. A166's cover is built on `Z(w_max)` and its reach clip is against `[0, a_{w_max}]²`, so it covers
   `R_c^{w}` for every `w ≤ w_max` (both the zone and the reach set are monotone in `w`); the
   `DEAD_R` verdicts are stated against `B_c^{w_max}`, the largest box, so a certified miss there is a
   certified miss at every smaller pad. **Every stage is therefore monotone in the safe direction.**
6. Consequently a `case-lp-certificate-v1` PASS on the FROZEN `verify_case.py`
   (sha256 `521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af`) at the fixed side `s0`,
   on the node `[B_H, X_1^clip, X_2^clip]` with budget 8, excludes `F`, hence excludes `P`, for
   **every** `m ∈ [3.82, ŝ)`. No `verify_param` emission is needed and A155 §5's list of missing
   machinery (parametric emission for corner-crowd nodes, a polygon-core parametric verifier, cover
   invariance for the corner cover) is **not consumed**: A166 uses ONE dilation slab, the whole window,
   which A155 §4 measured to be the cheapest member of the slab family anyway.
7. What remains at `m = ŝ`: K0-FREE's equality clause gives "`P` is a Trump image", discharged by the
   (D) leaf + scale-ray tube exactly as in A143 §4 (`k0_route.md` K0-O3, `T = 0.1279 ≥ ŝ − 3.82`). No
   A166 kill can fire on a node a Trump image realises — `notes/canary.md` verifies this on `l1_153`.

Until that chain is read and signed off in `k0_route.md` itself, every A166 kill is recorded in its
certificate as `scope: "s0_fixed_side"`, `window: "transfer pending (k0_route sec 4.1)"`. **The
pending item is a proof-reading task on two already-[T] lemmas (B.0 and K0-WIDEN), not a compute
task** — this is the difference between A166 and A155's slab-wise route, which needed machinery that
does not exist.

The pad-0 run (`results/subtree166_w0.jsonl`) is the s0-only control and is recorded as such: it is
2–16 % tighter on the pair census (3 646 vs 4 244 alive pairs; survivors 342/119/22/0/0/0/0/10/275/156/55
against 371/139/25/0/0/0/0/16/237/178/60) and buys nothing that matters, reproducing A155 §1's finding
that the pad is worth a few per cent.

## 6. Price

**Geometry.** A shared pair census of 100 CPU-s per pad, then 3–95 CPU-s per cell (median ≈ 12 s on the
17-cell pool sample, 24 s on the eleven; the cost scales with the number of surviving cover cells).
Over the 119 remaining open k0_00 cells: **≈ 0.5 CPU-h, once.** This is by far the cheapest per-node
geometry in the k0 lab, and it should be run on the whole pool regardless of what follows, because it
produces the 66 certified `M = 0` corners of §3.3 and the branch-(a) survivor count that every price
below depends on.

**LP, branch (a), the eleven.** Surviving pair cells 371 + 237 + 178 + 139 + 60 + 25 + 16 = **1 026
nodes** (four cells contribute 0). At the measured 240 s cap with certification that is
**70–95 CPU-h to decide the eleven at level 1** — and only if the LP decides at level 1, which
`tables.md` §5 says it does not on the sampled nodes.

**LP, branch (a), the pool.** A 41-cell sample of the 119 (`results/price166_wmax.json`) gives
survivors min 0, Q1 9, **median 25**, Q3 91, max 355, **mean 70.5**, zero on 7 — so the pool carries
**≈ 8 400 nodes, 560 CPU-h at level 1** (and ≈ 3 000 nodes / 200 CPU-h if only the median-and-below half
is run), one to two levels deeper if the LP behaves as A85's law says
(`τ` falls ≈ 0.5 per bisection level, decision at `η ≤ −1`), i.e. **6 000–8 000 CPU-h at depth 2**.
Against `docs/budget.md`'s k0 row (12 000 CPU-h, 9 400–10 900 after A141) that is **not a saving**: it
is the same order, for a tree that still owes branch (b) on 53 of the 119 cells and still owes the
interior tree's own depth below every surviving pair cell.

**LP, branch (b).** 53 of 119 cells have it; 3–20 partner cells each, budget 9, and A143 measured that
exact geometry at `η ≈ −0.08`. Priced at the same 240 s cap: **≈ 400 nodes, 25–30 CPU-h** — cheap, and
by A158b's exact-1 accounting guaranteed to return `τ = budget`: **all 12 degenerate nodes measured here
do exactly that** (`η` min −0.0097, median −0.0000, max 0.0000), so the money spent on branch (b) buys
nothing at all.

**Verdict on the price.** The sub-tree is worth running for its GEOMETRY (0.5 CPU-h for the whole pool,
a 91–100 % cut of the corner-first branching factor, the 26 % free cut of A143's own cover, 66 certified
`M = 0` corners, and four of the eleven reduced to a two-core hypothesis) and is **not** worth running as
an LP campaign: it prices at the interior tree's own 12 000 CPU-h without removing the interior tree's
obligations, and its one free lunch — the (C) leaf — is provably unavailable on every cell of the current
pool (§2). What the LP campaign WOULD deliver, now that the certificate path is fixed, is certified kills
at ~125 CPU-s each on the sub-population where three cores are spread enough (`l2_p65_101`'s kill is the
instance), which is the same mechanism A150 found at four corners — and the same conclusion: **the
mechanism is real and the branching factor spends it back.**

## 7. Three corrections to inherited machinery, for the record

0. **`caselp.make_certificate` reverts A135 exact cores to stock cores** — the big one, written up in
   `notes/certificate_bug.md`: it rebuilds the hypothesis with `Hyp.from_json`, whose `__init__` sets
   `cores = [b.core() for b in boxes]`, so the `cores` field the json carries is discarded. Every
   exact-core node's certificate therefore under-exempts, and the resulting verifier FAILs are
   artefacts. Fixed in A166's own emission path (`caselp.py` untouched); recovers A166's one converged
   kill and 5 of 5 of A150's FAILing certificates.


1. **`exactcore.cores_pairwise_disjoint` is not a sound disjointness test for TILTED cores.** It
   compares `max(|Δkx|, |Δky|) − (a_i + a_j) > 0`, which is the separating-axis test on the `x` and `y`
   axes with support radius `a`; a core at tilt `θ` has `x`-support radius `a(|cos θ| + |sin θ|) > a`.
   It is correct for the axis-aligned pin cores it was written for (`tm ≈ 0`). A166 therefore uses its
   own exact rational SAT over the four edge normals (`geo166.cores_disjoint_exact`) as the budget
   gate. A150's four-corner LP (four tilted cores) and A158b's seven-box gate both called the
   inherited function; neither conclusion is necessarily wrong (the test is conservative in one
   direction only — it can report DISJOINT for cores that overlap, i.e. it is unsound, so both should
   be re-checked).
2. **A141's `box_misses_cell` and A161's `box_misses_cell_exact` differ on exactly the population that
   matters here.** A141's separates only along the CELL's normals with the box's bounding half-width,
   so it cannot fire for a box whose square clears the corner box along one of its OWN edge normals —
   which is the situation of every `H` at `d ≈ 2.0–2.6`. A161's full test certifies `M = 0` on 66 of
   the 119. A159 §6c's `n_miss_pieces = 0` was measured with the weaker test.
