# A143 — the corner-first k0_00 tree: the root lemma as used, the two-cover intersection rule, and the price

Companion files: `docs/proofs/k0_route.md` (Lemmas K0-FREE, K0-WIDEN, K0-BLOCKED, K0-D4, K0-ATLAS),
`attempts/A38-root-power/notes/{design.md, T0_composition.md}` (the interior-first cover this is
measured against), `attempts/A115-k0-corner-rows` (the warm re-solve path and record format),
`attempts/A118-lane-count/code/lane.py` (the K′ lane leaf, imported unchanged and read-only),
`attempts/A131-pin-clip` (walls as pins, the per-tilt-sub-bin clip), `attempts/A132-polygon-core`
(K′), `attempts/A135-polycore-verifier` (the exact rational axis core), `attempts/A140-…` (the
drawing format).

---

## 1. The root lemma as used

For a packing `P` at side `m ∈ [3.82, ŝ]` write `B_c(m)` for the closed unit box at corner `c` and
`F = Δ_λ P` for its dilate at `s0 = 969271/250000`, `λ = s0/m ≤ λ_max = 1.0149426`.

**(R1) The dichotomy** (`k0_route.md` §3, Lean `teleport_packing`; consumes k1_00's tree, obligation
K0-O1, still OPEN). Either some corner box `B_c(m)` is met by **≤ 1** square of `P` — then `P` does
not exist for `m < ŝ` and is a Trump image at `m = ŝ` (K0-FREE, a (T) leaf) — or **every** corner
box is met by ≥ 2 squares (K0-BLOCKED).

**(R2) The widening** (Lemma K0-WIDEN, `k0_route.md` §4.1). A meeter of `B_c(m)` in `P` dilates to a
meeter of the *widened* box `B_c^w(s0) = [0, a_w]²` at BL, with

    w = (λ_max − 1)(1 + 1/√2) = 0.02551014…,   a_w = 1 + w = 1.02551014…

so the corner-first **cover** must be stated with `a_w`, while the K0-FREE **kill** is run on the
UNWIDENED box (A118's `lane.run_cell` already uses `a_w = 1` for exactly this reason).

**(R3) The cover.** Under K0-BLOCKED the BL box is met, so some square `Q0` of `F` has a pose in

    R_BL = { (c, θ) : Q(c, θ) ⊆ [0, s0]²  and  int Q(c, θ) ∩ int[0, a_w]² ≠ ∅ }.

Admissibility gives `h(θ) ≤ c_i ≤ s0 − h(θ)` with `h(θ) = (cos θ + sin θ)/2 ∈ [1/2, √2/2]`, and
meeting gives `c_i < a_w + h(θ)`. Hence

    c ∈ [1/2, a_w + √2/2]² = [0.5, 1.7326162]²  =: Z_BL,     θ ∈ [0°, 90°)  (the θ ≡ θ+90° glue).

The level-1 cover is the 6 × 6 grid on `Z_BL` × 6 tilt windows of 15° = **216 closed cells**, each
clipped per tilt window against the two constraints above. Nothing is lost: the grid covers `Z_BL ×
[0°, 90°)` exactly. Sampled confirmation: **22 078 drawn admissible BL-meeting poses, 0 misses**
(`results/cover143.json`), i.e. every drawn pose lands in a non-empty cell whose CLIPPED box
contains it — so the clip discards no admissible pose.

**(R4) D4.** The stabiliser of BL in D4 is `{id, transpose}`; the transpose fixes BL, swaps `x, y`
and sends `θ ↦ 90° − θ`, and both K0-BLOCKED and "BL is met" are invariant. Lemma K0-D4 with
`X_n` = the level-1 cells (a `D4_BL`-set) gives the quotient: **126 canonical cells** (`x ≥ y`,
diagonal cells kept whole), against the interior tree's 216. Nothing new is needed in Lean beyond
the cell-cover check itself — the transport of (K)/(C)/(T)/(D)/(D′) verdicts is `k0_route.md` §2's
Lemma K0-D4 proof verbatim, with `D4_BL` in place of `D4`.

**(R5) The doubly-met root (T1b).** K0-BLOCKED gives TWO distinct meeters at BL. The pair cover is
the set of unordered pairs of level-1 cells (`A = B` allowed), quotiented by the transpose acting on
the unordered pair: 216·217/2 = 23 436 pairs → **11 772 canonical pair cells**, budget 9 = 11 − 2.
Sampled confirmation: **12 000 drawn, realised, interior-disjoint BL 2-crowds, 0 violations** — every
one lands in a pair cell that geometry did NOT kill.

## 1a. The tilt clause of the brief is NOT available — a correction

The brief and the extension both assume "k0 means no simple square, so the BL intruder is tilted,
`θ ∈ (δ_simple, 90° − δ_simple)`". **There is no such tolerance in the k0 root definition.** Lean's
`Skeleton.lean` defines `OccupiesSlot q c` as "the point set of `q` is exactly the unit box centred
at the slot centre `c`" — axis-aligned AND exactly on the slot. `skeleton = ∅` therefore removes,
from the `θ = 0` slice of `R_BL`, exactly the single pose `(1/2, 1/2, 0°)` (the BL(0,0) slot; the
neighbouring slot BL(1,0) at `(3/2, 1/2)` does not meet the OPEN unit box) and its `θ = 90°` twin —
a measure-zero set. Moreover `M_{k0_00}` is the monotone hypothesis with NO pins, true of every
packing, which is precisely why the k0_00 tree is a ∀-packings statement; a positive-measure tilt
exclusion would make it a statement about the exact stratum and would need an exactness bridge that
`k0_route.md` §3 explicitly avoids consuming. **The corner-first cover must therefore run over the
full tilt range**, and its level-1 cell count is not reduced by the k0 hypothesis at all.

## 2. The two-cover intersection rule

The corner-first tree is an INDEPENDENT cover of the SAME hypothesis (K0-BLOCKED at s0, ∀-packings).
Formally, for interior cells `X` (a conditioned square in the D4 fundamental triangle) and
corner-first cells `Y` (a conditioned BL meeter, or a pair of them):

> **Rule I (product node).** If `F` reaches interior cell `X` and corner-first cell `Y`, it reaches
> the product node `X ∧ Y` whose hypothesis is the union of the two hypothesis box lists, with
> budget `11 − |X| − |Y|` — provided the two conditioned squares are DISTINCT, which is forced
> whenever `cores_meet(K(X), K(Y))` fails and `X`'s box and `Y`'s box are core-disjoint; if they can
> be the same square the node is simply `X` with a narrower box (`X ∩ Y`).
>
> **Rule II (transport of death).** `X` dies if EVERY `Y` compatible with it is dead, and vice
> versa. Compatibility is decided by the same three geometric leaves used inside each tree
> (centre-distance, K′-vs-K′, container clip), so the intersection costs no LP.
>
> **Rule III (support cut, no new node).** If an interior cell's LP optimum has a support that
> cannot supply a K0-BLOCKED BL crowd — no two support placements meeting `[0, a_w]²` lie in a
> surviving pair cell — then the corner-crowd constraint cuts that optimum. This is not yet a kill
> (the LP may find another optimum), but it is the dual-guided re-branching lever `docs/budget.md`'s
> k0 row asks for, and it is *decidable from data already on disk*.

Measured (`results/intersect143.json`) on A115 T6's twelve converged-alive interior cells: every one
has 1–20 support placements meeting the widened BL box, in 1–8 distinct corner-first cells; **none**
has a BL meeter in a corner-first cell that died (there are none — see §3); **two of the twelve
(`l2_p74_001`, `s3_far_BL389484_TR018470`) have NO surviving BL pair at all in their support**, i.e.
Rule III fires on them today.

## 3. What the geometry is worth (the measurement)

| root | cells (canonical) | geometry kills | rate |
|---|---|---|---|
| single-intruder (budget 10) | 216 (126) | **0** | 0 % |
| doubly-met pair (budget 9) | 23 436 (11 772) | **9 638** = 7 919 P2 + 1 313 P1 + 406 P1s | **81.9 %** |

* **P2** = the maximum centre distance over the two clipped boxes is `< 1` (two interior-disjoint
  unit squares have centre distance ≥ 1, since any separating direction `n` gives
  `|d·n| ≥ h_1(n) + h_2(n) ≥ 1`).
* **P1** = `K′(A)` meets `K′(B)` (A132 polygon cores): every square realising `A` overlaps every
  square realising `B`, so the two-square hypothesis is contradictory — a (C) leaf.
* **P1s** = A131's per-tilt-sub-bin refinement of P1: subdivide each tilt window into 4, clip each
  sub-bin against the container, and require EVERY surviving sub-pair to be contradictory. It fires
  on 406 pair cells the whole-window test misses — **4.2 % of the geometry kills, and the only place
  in A143 where per-sub-bin clipping produces an outright kill.** (On the single root the sub-bin
  clip still tightens: 22 of the 216 cells lose 2 of their 8 tilt sub-bins outright — a free
  narrowing of the hypothesis available to the level-2 split, worth recording but not a kill.)

**Why the container clip empties nothing in the single root, and why that is not a bug.** Clipping
per tilt sub-bin can only beat the whole-window clip if two sub-bins are emptied for *different*
reasons. Emptiness of a sub-bin needs `x1 < h_min(sub) ≤ √2/2` or `x0 > a_w + h_max(sub) ≥ 1.5`, and
no cell can satisfy the first in one sub-bin and the second in another. So on a single conditioned
square the sub-bin clip is provably equal to the whole-window clip — the A131 mechanism only pays
once a SECOND object (here `K′(Q1)`) enters the clip, which is exactly the pair root.

**Why the K′ lane test kills nothing at level 1, in either root.** At BL, `M` (the conditioned
squares that can meet the cell) is 1 in the single root and 2 in the pair root, so the kill
`LANE + M ≤ 1` needs `LANE(BL) = 0` resp. is impossible. `LANE(BL) ≤ 1` was certified on 20 of 216
single cells and 158 of 1 322 tested pair cells, and `LANE(BL) = 0` on 6 pair cells — none of which
reaches the threshold. At BR / TR / TL the conditioned squares are all localised at BL, so the other
three corners are untouched and `LANE ≥ 2` is realised by an explicit disjoint witness pair on 214 /
216 / 212 single cells and on essentially every pair cell. **The lane leaf is a DEEP-node weapon on
this tree: it can only fire once the tree has conditioned squares at more than one corner.** This
reproduces, from the geometry side, A115's finding that corner-crowd ROWS on the interior tree
killed nothing.

Upgrading the leaf to A141's **polygon** cores — the upgrade that killed 26 further level-1 cells of
the interior tree — changes nothing here: `polylane.lane_corner` on 27 single cells (all four
corners, exact rational shared-point discharge) gives **0 kills**, with BL at 7 `LANE ≥ 2`, 16
`NEAR-MISS-OR-WORSE` (a second BL meeter realised by an explicit witness) and 4 UNDECIDED, and
BR/TR/TL at 27/27/27 `LANE ≥ 2`. The reason is structural, not a matter of core quality: on the
corner-first root the conditioned square *is* a meeter of the corner the leaf tests, so the leaf's
budget is spent before it starts.

## 4. Trump, and the terminal mechanism (the PI's prediction)

Measured on the exact A22/A65 data (`results/trump143.json`, `results/trump143_cells.json`), with
the family dilated to `s0`:

* **On the UNWIDENED box** (`a_w = 1`) every Trump image has exactly ONE doubly-met corner and three
  singly-met ones — e.g. `g0`: BL 1, BR 1, TR 1, **TL 2**. So *Trump is K0-FREE at three of its four
  corners*: the K0-FREE branch, not the tree, is what catches it. **The PI's identification of the
  single non-simple corner (TL in trump5's frame) is CONFIRMED**, and after the D4 reduction that
  corner is BL for images `g2` and `g6`.
* Its two meeters are the axis-aligned NON-slot square at `(0.5, 1.34453, 0°)` and the tilted square
  at `(1.53629, 0.70461, 49.818°)`. In the corner-first cover they are the pair cell
  **{(0,4,0), (5,0,3)}** (canonically `{(0,4,5),(5,0,3)}` under the `θ ≡ θ+90°` glue — an
  axis-aligned meeter sits on the boundary of tilt bins 0 and 5, which the tilt partition should
  treat as one bin).
* **But the K0-WIDEN pad breaks the "one lineage" prediction.** At `a_w = 1.0255` every corner of
  every image is met by ≥ 2 squares (the flush neighbours enter), and the Trump canary becomes
  **5 single cells** `{(0,0,0), (4,0,0), (4,3,2), (4,3,3), (5,0,3)}` and **9 pair cells**. All nine
  survive the geometry prunes, as they must — that is the canary, and it passed.
* **Descending the Trump pair lineage 3 levels (`results/descend143.json`) produces no kill, and no
  depth ever will.** At depth 0/1/2/3: `P1` and `P2` never fire; BR, TR, TL stay `LANE ≥ 2` with
  `M = 0`; BL has `M = 2`. The reason is a proof, not a budget: `Δ_λ ẑ` is a genuine 11-family that
  satisfies the node's hypothesis and has ≥ 2 widened meeters at every corner, so `LANE(c) + M(c) ≥ 2`
  at every corner at every depth. (At depth 3 the node does reach `LANE(BL) = 0`, i.e. it *forces*
  exactly two BL meeters — a tightening, not a kill.)

> **Therefore the predicted terminal mechanism does NOT hold, and cannot.** The Trump lineage of the
> corner-first tree is discharged exactly as in the interior-first tree: by a **(D) leaf** — all
> eleven squares localised within the landing radii `(1.6·10⁻³, 2.1·10⁻³)` of an image — followed by
> the scale-ray tube (`k0_route.md` K0-O3, `T = 0.1279 ≥ ŝ − 3.82`), which gives `m ≥ ŝ` with
> equality only at `P = g·ẑ`. No K0-FREE lane kill can ever fire on a node that a Trump image
> realises, because K0-FREE is FALSE of Trump at the corner the node conditions on. The corner-first
> canonicalisation does not change the (D) obligation; it only relocates it (5 single / 9 pair
> level-1 cells instead of A38's 3).

## 5. Price

Reference: the interior-first k0_00 tree is priced at **12 000 CPU-h** (`docs/budget.md` k0 row,
after A115's 22-of-216 level-1 pass), or 3 200–7 000 CPU-h in `k0_route.md` §8's optimistic row.

**Single-intruder corner-first root.** (Measured η in §6: −0.0442, −0.6328, −0.0000.) Level-1 cells
are 1.96× wider in position than the interior
tree's (half-width 0.1027 vs 0.0524) at the same 7.5° tilt half-width, because the corner-meeting
zone is 1.233 wide and the cell budget was matched to 216. The measured level-1 slack is therefore
WORSE than the interior root's (`η` in §6's table vs A85's `−0.12 … −0.34`), and the A38/A85 law
(`τ` falls ≈ 0.5 per bisection level, decision at `η ≤ −1`) puts the decision one to two levels
deeper: depth 3–4 instead of the interior tree's depth 2. Node counts `126 · 8^(d−1)` = 8 064 (d=3)
/ 64 512 (d=4); at A85's measured 0.47–1.1 CPU-h per decided node that is **3 800–8 900 CPU-h at
d = 3 and 30 000–71 000 at d = 4**. Conclusion: **the single-intruder corner-first root is not a
saving — at best it matches the interior tree, at worst it is 3–6× worse.** Its only structural
advantages are the `/2` from `D4_BL` (against the interior tree's `/8`, already spent) and free
(T) leaves.

**Doubly-met pair root.** Geometry removes 81.9 % of the 11 772 canonical pair cells for **90 CPU-s
of total compute** — the cheapest cut anywhere in the k0 route, and it is exact and certificate-free
(P2 is arithmetic; P1/P1s are A132's certified rational vertex tests). What it buys depends entirely
on the depth at which the budget-9 two-core LP decides:

| scenario | decides at | nodes | CPU-h at 0.47–1.1 h/node |
|---|---|---|---|
| level 1 (`η ≤ −1` on the 2 134 survivors) | d = 1 | 2 134 | **1 000–2 350** |
| level 2 | d = 2 | 17 072 | 8 000–18 800 |
| level 3 | d = 3 | 136 576 | 64 000–150 000 |

so the doubly-met root is a **5–12× cut on the interior tree if and only if the two-core budget-9 LP
decides at level 1**, and is worse than the interior tree from level 2 on. **§6 measures where it
actually sits: η ≈ −0.08 at level 1, i.e. NOT the level-1 row — the pair root prices at 8 000–18 800
CPU-h, no better than the interior tree.** Two further multipliers, both already priced elsewhere and both available here: the
`/2` of `D4_BL`, and Rule II above (a pair cell dies if every compatible interior cell is dead) —
the two covers are cheap to intersect because compatibility is a core test, not an LP.

**What would change the verdict.** (i) A finer tilt partition: the corner-first cells are wide in
`θ` exactly where `K′` is weakest, and `K′/K(a)` area ratio here is 1.18–1.60 (median 1.32), the
largest measured anywhere in the lab — 12 windows of 7.5° would roughly halve `w_θ` at 2× the node
count and should be measured before any campaign. (ii) A143's geometry cut applies to the corner
seed of `k0_route.md` §4.4 too: A85 measured `N_pair ≈ 3.4·10⁴` per corner from 644 reach boxes at
width 0.15 with a 7-bin tilt partition; A143's coarser 216-cell cover with the same three prunes
plus the sub-bin refinement leaves 2 134 — the difference is the box width and the `D4_BL` quotient,
and it does not rescue the four-corner product (`2 134⁴/8 ≈ 2.6·10¹²`).

## 6. The LP measurement, and what it settles

Hypothesis cores are A135's certified EXACT axis cores — a square at the box's own tilt, so the
FROZEN `verify_case.py` (sha256 `521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af`)
needs no change and a converged kill is certifiable as-is. `K′` is an audit column only: a kill that
needs the polygon core is "LP-dead under `K′`, certificate pending".

| root | n | τ | η | converged kills | certified |
|---|---|---|---|---|---|
| single-intruder, budget 10, 240 s | 3 | 9.9558 / 9.3672 / 10.0000 | −0.0442 / −0.6328 / −0.0000 | 0 | 0 |
| doubly-met pair, budget 9, 240 s | 2 | 8.9174 / 8.9231 | −0.0826 / −0.0769 | 0 | 0 |

**The comparison anchor** (`results/a115_l1_eta.json`, read-only from A115's `t4/t5_runs.jsonl`):
A115's warm re-solves of the INTERIOR level-1 root cells, `src = A38-l1`, n = 89, median LP wall
**286 s** — the same cap — give

    eta:  min −1.327   Q1 −1.000   median −0.729   Q3 −0.000   max +0.409;
          20 % at eta <= −1,  56 % at eta <= −0.5;  14 CERTIFIED DEAD of the 89 re-solved.

So at matched LP time the corner-first level-1 cells sit at the **upper (worst) quartile** of the
interior root's slack distribution, and the doubly-met pair cells sit above it: **conditioning a
SECOND square at the SAME corner buys essentially no LP slack** (η −0.077, −0.083 at budget 9 vs
−0.044, −0.633, −0.000 at budget 10), because the two cores overlap the same low-coverage corner
region and the node pays a whole unit of budget for the second one. That is the decisive negative
result of A143: the 81.9 % geometric cut of the pair root does NOT translate into an LP advantage,
so the "decides at level 1" row of §5's table is not the row we are on, and the pair root prices at
level 2 or worse (**8 000–18 800 CPU-h**), i.e. no better than the interior tree's 12 000.

Caveat of record: n = 3 and n = 2 (the 2 CPU-h cap, on a box carrying five other campaigns, bought
five 240 s nodes at ~275 CPU-s each plus 0.85 CPU-h of exact geometry). These are slack readings,
not a kill rate; the kill rate at this η is 0 by A115's own law and needs no further measurement.
The interior root's headline **22 of 216** required A115's 29.8 CPU-h of warm continuation over
every reachable open cell, and A85 measured **0 of 3** interior level-1 certifications at a 900 s
cap — so "0 of 5 at 240 s" is not evidence against the corner-first root by itself; **the η
distribution is**, and it is worse.
