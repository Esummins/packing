# realise85 — the A85 blocker-pair census made SOUND about REALISABILITY (chore, 2026-09-03)

A87 `notes/d2front87.md` §"The barrier is upstream of packing": A85's level-2 pair prune
(`code/{tree85,corner85,gate85}.py`, `results/a85_pairs_BL.json`) never checked that a pair is
REALISABLE.  This run replaces the grid verdict (a LOWER bound on realisability) with an EXACT
necessary condition (an UPPER bound), so the two now bracket the truth.

Code `code/realise85.py`; results `results/realise85.{json,boxes.json,pairs.json}`.
One process, `OMP_NUM_THREADS=1`, free commit 13.2 GB at start, 31.8 s wall.  Nothing committed;
no A57/A60/A61 file or process touched.

## Definition made exact

A placement of a BL corner blocker is REALISABLE at side `s` in the window `[3.82, s0]`,
`s0 = 969271/250000`, iff

* **(R1) container.**  `Q ⊂ [0,s]²`, i.e. `c_x ≥ h(θ)`, `c_y ≥ h(θ)` (near walls) and
  `c_x + h ≤ s`, `c_y + h ≤ s` (far walls), `h(θ) = (cos θ + sin θ)/2`.
* **(R2) K0-BLOCKED.**  `Q` meets the OPEN slot `(0,1)²` with certified depth
  `1 − f_min_max(Q) > 1e-9` (a tangency is not a block).  `f_min_max` = A89's
  `t2b_depth` / `corner85.f_min_max`.
* **(R3)** the two blockers of a pair are interior-disjoint.

**The far walls never bind on this cover:** `max_b (x1 + h_max(b)) = 2.4571068 < 3.82`, so (R1)
reduces to the quadrant constraint on the whole window; nothing here depends on where in
`[3.82, s0]` the side sits.

## (1) Box test — 560 of 644 survive

Per θ-cell (0.01°), all bounds outward-rounded, a box is dropped only if provably no placement
in it is realisable:

* `f_min_max` is nondecreasing in `c_x` and `c_y` separately (A89 part-1 lemma), so over a cell
  the minimum sits at the WALL-AWARE lower-left corner `X_lb = max(x0, min_cell h)`,
  `Y_lb = max(y0, min_cell h)` — not at `(x0, y0)`;
* `f_min_max` is `√2/2`-Lipschitz in θ at fixed centre → cell slack `√2/2 · Δθ/2`;
* **exact per-cell reach cap** (the constraint A85 never had): `f_min_max(c_x,c_y,θ) < v` iff some
  `p ∈ Q(0, c_y, θ)` has `p_x + c_x < v` and `p_y < v`, hence
  `c_x < v − min{p_x : p ∈ Q(0,Y_lb,θ_mid), p_y ≤ v}` with the min over the polygon clipped by
  `y ≤ v`, `v = 1 − 1e-9 + slack`.  Exact, O(1) per cell.  Same for `c_y`.

| | boxes |
|---|---|
| A85 sound reach-cover boxes (`sigma_closed_7`) | 644 |
| **realisable (surviving)** | **560** |
| dropped | 84 |

The dropped set is exactly A89 `t2b_depth`'s `depth_ub < 0` bucket (84 boxes) — **the container
constraint drops no box beyond the slot test alone**, and the dropped set is σ-closed.  It does
tighten the depth ceiling on the survivors: wall-aware `depth_ub` vs A89's wall-free value,
mean tightening 0.00599, max 0.1077, 173 of 560 boxes tightened (residual +3.8e-5 excess on some
boxes is only this run's coarser θ cell, 0.01° vs A89's ~0.007°).

Wall-aware `depth_ub` over the 560: min 0.000038, mean 0.337007, max 1.000018;
≥ 0.05: 519, ≥ 0.10: 449, ≥ 0.20: 374, ≥ 0.292893: 288.

## (2) Pair test — 7 044 of 33 656 survive

Each surviving box is split into ≤ 28 θ-ATOMS (0.5°), each carrying the realisability-reduced
centre interval `[min_cell X_lb, min(x1, max_cell cap_x)] × [ … y … ]` — atoms cover every
realisable placement of the box.  For each atom pair a sound UPPER bound of the 4-axis SAT gap

  `gap = max(|D·e1A|,|D·e2A|,|D·e1B|,|D·e2B|) − 1/2 − r`,  `r = (|cos d| + |sin d|)/2`

is computed by interval arithmetic (`r` lower-bounded exactly on the `d`-interval).  A pair is
DROPPED iff every atom pair has `gap_ub < 0`, i.e. every placement pair in the two boxes
overlaps or violates (R1)/(R2).  This subsumes A85's `maxdist < 1` prune.

| | pairs |
|---|---|
| A85 surviving level-2 pairs | 33 656 |
| … with both boxes realisable | 18 787 |
| **… surviving the pair test** | **7 044**  (0.2093) |
| A89 grid witnesses, exact, OPEN slot (LOWER bound) | 4 365  (0.1297) |

So the realisable count is bracketed **[4 365, 7 044]** — the grid verdict A87 reported
(856/6000 subsample ⇒ ≥ 0.1427) and this exact upper bound are within 1.6× of each other.
σ-closure of the new surviving set: 7 017/7 044 = 0.9962 (A85's was 0.9891; same rational-core
cause, sound either way).

## (3) Four-corner frontier — A85's exact contradiction gate on top

`gate85`'s own machinery verbatim (D4 corner maps, per-box drop masks, `pinguard.cores_meet`
cross-corner contradiction, fast alive verdict at budget 3), 1 000 sampled 4-corner
combinations drawn from the surviving pair set, seed 20260903.

| sample source | attemptable | unkillable | contradictory | D4-canonical |
|---|---|---|---|---|
| A85 (all 33 656 pairs) | 179 (0.179) | 2 (0.002) | 819 (0.819) | 120 (0.120) |
| **realisable pairs (7 044)** | **128 (0.128)** | 5 (0.005) | 867 (0.867) | 125 (0.125) |
| + `d2 ≥ 0.10` pairs (2 441) | 362 (0.362) | 32 (0.032) | 606 (0.606) | 140 (0.140) |

The `/8` of Lemma K0-D4 stays exact on the realisable seed (0.125, orbit size 8).

D4-canonical 4-corner combinations: `7 044⁴ / 8 = 3.077·10¹⁴`; **attemptable frontier
`3.94·10¹³` nodes** (A85: `33 656⁴ · 0.179 / 8 = 2.87·10¹⁶`).

## (4) Re-price

Per-node cost, A85 measured (`notes/pilot_report.md` R4 table, `results/pilot_summary85.json`,
`docs/proofs/k0_route.md` §7.3/§8.3): ≈ 1 000 s LP + 630–860 s certification = **0.47 CPU-h**
first-pass PASS, **1.1 CPU-h** with two eps_geo repairs (the 1 700 s/attempt figure §7.2 uses).
S5 (4-corner, 8 cores, budget 3) was never run in the pilot — the 3 h LP cap was consumed by
S1 — so the 4-corner per-node cost is A85's own extrapolation, not a measurement.

| route | pairs/corner | attemptable frac | frontier nodes | CPU-h (0.47 – 1.1) | vs 3 200–7 000 CPU-h |
|---|---|---|---|---|---|
| A85 as published | 33 656 | 0.179 | 2.87·10¹⁶ | 1.35·10¹⁶ – 3.16·10¹⁶ | 4.2·10¹² × |
| **realisability-sound** | **7 044** | **0.128** | **3.94·10¹³** | **1.85·10¹³ – 4.33·10¹³** | **5.8·10⁹ ×** |
| + `d2 ≥ 0.10` at all 4 corners (HYPOTHESIS, price only) | 2 441 | 0.362 | 1.61·10¹² | 7.6·10¹¹ – 1.8·10¹² | 2.4·10⁸ × |

Realisability is worth **729×** on the frontier (4.8× per corner on the pair count, ×0.72 on the
attemptable fraction).  The d2 < 0.10 cut, if it ever becomes a theorem, is worth a further
**24×** (2.9× per corner on the pair count, offset by the attemptable fraction RISING to 0.362 —
deep-capable boxes hug the slot and contradict each other across corners less often).

**Verdict unchanged: C3 stays DEAD.**  Stacked, the two cuts move the corner-seed cover from
`10¹⁶` to `10¹²`–`10¹³` nodes, i.e. `10¹¹`–`10¹³` CPU-h — still 8–10 orders of magnitude above
the interior-first tree's 3 200–7 000 CPU-h (`k0_route.md` §8.3).  Nothing available at the pair
level closes that gap; it would take a cut of ≈ 10⁹ on the frontier, i.e. ≈ 180× per corner on
the pair count beyond what realisability + d2 already give (7 044 → ≈ 40 pairs per corner).
The sound residue of C3 is unchanged (Lemma K0-REUSE, the (C) prunes at fine boxes).

## Canaries

* **Trump's TL 2-crowd (squares 4 and 6) in the BL frame — must be REALISABLE: PASS.**
  Exact (300 dps, `A03-upper-reconstruct/trump11_exact.json`, reflected `y → s − y`):
  sq4 at `(0.5, 1.34452528)`, θ = 0°, depth 0.155474724; sq6 at `(1.53628718, 0.70460817)`,
  θ = 49.818063°, depth 0.168320990 (both match `d2front87`'s references to 1e-9); both in the
  quadrant (`min_x ≥ 0`, `min_y ≥ 0`), SAT gap `+2.2e-16` (interior-disjoint).  Located uniquely
  in cover boxes 366 (sq4) and 275 (sq6); **both boxes survive (1), and the census pair
  (275, 366) survives (2)**.  The tiny-box test on the poses themselves also returns realisable.
* **Two axis-aligned blockers at one corner — must be DROPPED: PASS.**  Degenerate θ = 0 boxes
  over the whole cover rect: a single such square IS realisable (`depth_ub` 1.0), but the exact
  reach cap gives `c_x, c_y ∈ [0.5, 1.499999999]`, so `max|ΔC| ≤ 1 − 1e-9` and the interval SAT
  bound is `gap_ub = −9.98e-10 < 0` — every placement pair overlaps.  Pair dropped.
* **Soundness against A89's witnesses: PASS.**  All 4 365 pairs that `t2b_pairs.jsonl` witnesses
  EXACTLY against the open slot (disjoint + both meet the slot + both in the quadrant) survive
  both (1) and (2); 0 box violations, 0 pair violations.

## Caveats

* (1) and (2) are NECESSARY conditions only: 7 044 is an upper bound on the realisable pairs
  (4 365 is the matching lower bound).  Every prune is outward-rounded; a pair is dropped only
  when provably no placement pair qualifies.
* The 4-corner gate is A85's own (`gate85`) applied on top; the cross-corner test is
  `cores_meet` on the ORIGINAL boxes' rational cores, not on the realisability-reduced atoms.
  Re-running the contradiction test on the reduced atoms would only prune further — unmeasured.
* `d2 ≥ 0.10` is a HYPOTHESIS (A87's PI conjecture), not a theorem; the third row is a price, not
  a result.  `d2_ub(i,j) = min(depth_ub(i), depth_ub(j))` uses the wall-aware `depth_ub`.
* The 4-corner per-node cost is extrapolated (S5 never ran); the frontier, not the constant, is
  what decides the verdict here.
