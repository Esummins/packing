# charge85 — certified corner CHARGE of pinned intruder pairs (A85 chore)

Run: `attempts/A85-k0-route/code/charge85.py`
Outputs: `results/charge85.json`, `results/charge85.pairs.jsonl`, `logs/charge85.log`
One process, `OMP_NUM_THREADS=1`. No commit. Nothing outside `A85-k0-route/{code,results,notes,logs}` written.

## 1. What the number means

For a pair box `(K_i, K_j)` — two A85 BL-corner hypothesis boxes
`[t0,t1] x [x0,x1] x [y0,y1]` (t = tan(theta/2)) — the reported **charge** is a
rational `A` for which the following is machine-certified in exact `Fraction`
arithmetic:

> there is a set of pairwise interior-disjoint rational rectangles contained in
> the **BL quadrant** `[0, s0/2]^2`, of total area `A`, such that for EVERY
> placement pair `(P_i, P_j)` with parameters in `(K_i, K_j)` and EVERY closed
> unit square `Q` with `Q ⊂ [0,s0]^2`, `int Q ∩ int P_i = ∅`, `int Q ∩ int P_j = ∅`,
> the square `Q` meets none of those rectangles.

This is A25's box-uniform form (A23 `dead_region.PlacedBox` semantics: every
discharge — witness-point interiority, interval SAT separation — is taken over
the whole hypothesis box).  `s0 = 969271/250000 = 3.877084`,
`E(s0) = s0^2 - 11 = 4.0317804…`.

**Why the four charges add.** Every rectangle is clipped to the corner's own
quadrant, so the dead sets of the four corners are interior-disjoint by
construction and the A23 budget lemma (notes Lemma 2) gives

    charge(BL) + charge(BR) + charge(TR) + charge(TL) <= E(s)

for any packing of 11 unit squares in `[0,s]^2` realising the four corner
hypotheses.  A four-corner combination whose charge sum exceeds `E(s0)` is
therefore **dead by area** with no further work.

## 2. Method

1. **Windows.** A25 `wall_rects` for both cores + `between_rect`, clipped to the
   BL quadrant, snapped to a 1/8 grid and made pairwise disjoint.
2. **Float screen (not a proof).** `atlas_lib.map_windows(mode='float')` with
   `cell0 = 1/8`, `min_cell = 1/16`, `work_budget = 2500`.  This only *proposes*
   tiles; its negative filter (`quick_cover`) only ever drops tiles.
3. **Exact re-certification (the proof).** every proposed tile is re-run through
   `dead_region.Certifier(mode='exact', depth_max=30)`, `max_boxes = 200000`,
   at most 600 tiles.  Only tiles that pass are counted.
   Dropped / unvisited / capped / failed tiles simply do not count, so the
   reported number is always a certified **lower** bound.
4. **Hypothesis = the full A85 box** (not the atom hull).  A larger hypothesis
   can only lower the certified area, so this is the conservative choice.

## 3. Refinement (A25's cliff)

A25's floors collapse to 0 once a hypothesis half-width exceeds ~0.10–0.15.  The
A85 boxes are 0.1389 wide in x and y and up to 13.8° wide in tilt, so the cliff
is live.  When the level-0 charge is below `1/100` the pair hypothesis is
bisected in its widest dimension (tilt widths compared in `t` units scaled by
`3/2`, matching `dead_region`'s `tscale`) and the charge is taken as the
**minimum over the 2^L sub-boxes**, capped at `L = 2` (4 sub-boxes) and 120 s.

The minimum is the sound aggregator: every placement of the pair lies in some
sub-box and strands at least that sub-box's area, all inside the same quadrant.
`level` in the output records how many bisections were needed.

## 4. Sampling

Seeded (`random.Random(85)`) stratified sample of 200 of the 7 044 realisable
pair boxes: 40 JAM, 40 BLOCK, 40 WEDGE, and 20 from each of the four OTHER
offset bins.  The OTHER bin is the offset `g = max(x0, y0) - 1/2` of the pair's
axis-aligned member (box-level, i.e. a sound lower bound on that member's
offset); this is Trump's corner type.

## 5. Results (200 pair boxes, 2 231 s, one process)

### 5.1 Canaries

| canary | charge | note |
|---|---|---|
| Trump TL pair at its exact placement (1e-7 point box) | **251/256 = 0.98047** | 92 exact-certified cells, no refinement needed |
| flushest JAM pair (354, 368), g = 0 | **0** | still 0 after 2 bisections (4 sub-boxes) |

**Independent validation** (`charge85_post.py`): all 92 Trump-canary cells were
tested against the exact 11-square Trump packing mapped into the same BL frame.
**0 hits** — no Trump square meets any cell certified unreachable, as the
certificate demands (Trump's other nine squares are exactly legal unit squares
disjoint from the two intruders).

The Trump charge sits *above* A47's corner-table max of 0.85; A47's entries are
single-square charges, this is a pair.

### 5.2 Per-case charge table (certified lower bounds, at s0)

| stratum | n | min | p25 | median | max | refined |
|---|---|---|---|---|---|---|
| JAM | 40 | 0.0000 | 0.0586 | 0.2031 | 0.3438 | 8 at L2 |
| BLOCK | 40 | 0.0000 | 0.1953 | 0.5977 | 1.2344 | 1 at L2 |
| WEDGE | 40 | 0.0234 | 0.1289 | 0.4531 | 1.0508 | 0 |
| OTHER g∈[0.1,0.3) | 20 | 0.1211 | 0.2109 | 0.2930 | 0.4922 | 0 |
| OTHER g∈[0.3,0.5) | 20 | 0.3477 | 0.4531 | 0.6094 | 0.7461 | 0 |
| OTHER g∈[0.5,0.7) | 20 | 0.4492 | 0.6055 | 0.7070 | 1.0117 | 0 |
| OTHER g∈[0.7,1.0) | 20 | 0.0195 | 0.1602 | 0.6406 | 1.0625 | 0 |

Overall: min 0, median 0.3945, max 1.2344 (BLOCK pair (183,232)).

**Refinement was almost never needed** — 9 of 200 pairs (8 JAM + 1 BLOCK) fell
below the 1/100 cliff trigger, and all 9 were still 0 after two bisections, so
those are genuine zeros of the method, not cliff artefacts. The A85 box widths
(0.1389 in x/y, ≤ 13.8° in tilt) sit *under* A25's cliff for this pair
geometry: 191/200 pairs certified a positive charge at level 0.

### 5.3 The OTHER (Trump-type) trend, and the fan in the top bin

Median charge rises steeply with the axis member's offset g:
`0.293 → 0.609 → 0.707` across the first three bins.  The **top bin
g ∈ [0.7,1) does not continue the trend — it fans out** (min 0.0195, median
0.641, max 1.0625).  The discriminator is not g but whether the pair actually
pins the corner pocket: the high-charge top-bin boxes have the axis member
*flush to a wall* near the corner (e.g. (291,366): box 366 is x∈[0.50,0.64],
y∈[1.33,1.47], θ∈[0°,7.1°] — Trump's own box, charge 1.0625), while the
low-charge ones have it flush at large offset with the partner far away
(e.g. (56,473), charge 0.0195).  **Offset alone does not price a corner.**

### 5.4 Four-corner combinations dead by area

D4-orbits of 4-tuples drawn from the sampled charges, counted exactly by
Burnside over the corner action (verified against brute force):

| pool | > E(s0) = 4.0318 (dead by area) | > 3.5 (dead if interior wastes ≥ 0.53) |
|---|---|---|
| all 200 | 10 465 / 202 015 050 = **5.18e-5** | 466 084 / 202 015 050 = **2.31e-3** |
| non-JAM (160) | 10 460 / 82 953 640 = 1.26e-4 | 460 213 / 82 953 640 = 5.55e-3 |
| OTHER only (80) | 80 / 5 250 420 = 1.52e-5 | 11 288 / 5 250 420 = 2.15e-3 |
| OTHER, g ≥ 0.3 (60) | 80 / 1 675 365 = 4.78e-5 | 11 081 / 1 675 365 = 6.61e-3 |

A uniform four-corner kill needs **> 1.00795** per corner (E/4); only **8 of
200** sampled pairs clear that, and **16 of 200** clear 3.5/4 = 0.875.  The
largest four-corner sum reachable from the sample is 4 × 1.2344 = 4.9375.

### 5.5 The PI's cap: VACUOUS at area level

The cap asked for is the max g for which an OTHER corner plus three
minimum-charge non-JAM corners stays under budget.  The sampled **minimum
non-JAM charge is 0** (one BLOCK pair, certified 0 after two bisections), so the
head available to the OTHER corner is the whole budget 4.0318, and the largest
single-corner charge anywhere in the sample is 1.2344.

**There is no cap: every sampled offset, up to g = 0.972, stays under budget.**
80/80 OTHER pairs are admissible, 0 are excluded, in every bin, and the same
holds for the Trump pattern (one OTHER corner + three JAM corners, min JAM = 0).
Even three *median* non-JAM corners (3 × 0.5586 = 1.6758) leave a head of 2.356,
which no single corner in the sample approaches.

Only the all-OTHER-same-bin configurations get close: 4 × max is 4.047 for
g ∈ [0.5,0.7) and 4.25 for g ∈ [0.7,1) — i.e. *some* four-corner combinations in
the two high bins are dead by area, but no whole bin is.

**Reading for the PI**: the corner-charge budget is a real, certified
constraint, but on its own it kills ~5e-5 of four-corner combinations and
imposes no bound on the offset g.  It becomes useful only in combination — with
an interior-waste floor (2.3e-3 at 3.5) or with a lower bound on the *other*
three corners' charges, which is exactly what the JAM/zero-charge corners deny.

## 6. Caveats

* The charge is a **lower** bound; a coarser box or a tighter work budget only
  makes it smaller.  A "small" charge is never evidence that a corner is cheap.
* The minimum non-JAM charge used in the cap is the minimum over the **sample**,
  not over all 7 044 pairs; the true minimum can only be lower, which would
  *loosen* the cap.  A production cap needs the full sweep.
* Charges are measured at `s0`; the s-window `[3.82, s0]` is not swept.  A
  smaller side gives a smaller budget `E(s)` and (weakly) a larger charge, so
  `s0` is the conservative end for the *budget* comparison.
* The Trump canary uses a 1e-7 box around Trump's exact TL pair, mapped to the
  BL frame by `(x,y) -> (x, s-y)`, `theta -> 90 - theta (mod 90)`, and is
  measured inside the `s0` container (`s0 > s_hat` by 4e-10, which only helps
  the covering square, so the number is still a lower bound).
