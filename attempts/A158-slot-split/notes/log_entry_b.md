

## 2026-09-08 — A158b-slot-split addendum (Opus engineer) — the YES child as an LP node, and the mutual clip
- **Two coordinator/PI corrections, both run.** (i) The YES child is an ordinary LP node, not a lane
  leaf: `pins + H + the slot box S`, `budget = 11 − #cores = 4`, A135 exact cores on all 7 boxes,
  `S` an ordinary second core in the frozen `case-measure-certificate-v1` schema. (ii) Before it,
  the two conditioned boxes are mutually clipped with A131's pin-clip, each box's own core in the
  pin's role, then `K'` rebuilt and the lane test re-run on the clipped cores.
- **Extra soundness gate**: A135's `ExactHyp` only checks `cores[:n−1]` pairwise disjoint; with `S`
  appended `K(S)` would go unchecked and, if it met `K(H)`, the two hypotheses could be witnessed by
  the SAME square and the budget would be 5, not 4. `cores_pairwise_disjoint` is re-run over all 7
  (min gap 0.0000 on A60's exact pins, 0.0141 on A57's `δ = 10⁻²` pins).
- **The YES-child LP lands exactly back on the knife edge: 12 of 12 sub-cases (6 cells × 2 tilt
  pieces), all converged, `τ = 4.000000 = budget`, `η = 0`** (3.4–80.4 s each). This is the general
  obstruction stated exactly: adding the slot square removes **exactly one** unit of dual packing
  *and* **exactly one** unit of budget, so the YES child returns to `τ = budget` — the same 1 the NO
  child removes from `τ` alone. The dual weight in `S` is exactly 1 on **730 of the 1,238** selected
  records, so on that whole sub-population **the split is structurally neutral** and no amount of
  compute changes it.
- **The mutual clip bites, and the PI's prediction about `K'(H)` is confirmed.** At `S(0.10, 10°)`:
  `H`'s box keeps 0.5003 of its area on `c0_Y0787` (0.4714 by volume at `nsub = 4`), 0.6273 on
  `Y0147`, 0.8865 on `c0_Y0076`, 1.0000 on `Y0130`/`Y1110`; `K'(H)` grows ×1.126 on `c0_Y0787`
  (0.590298 → 0.664416), ×1.066 on `Y0147`, ×1.027 on `c0_Y0076`; `S`'s box keeps 0.7439/0.7265 on
  `c0_Y0959`/`Y0147` with **two empty tilt sub-bins** at `nsub = 4`. (The core handed to A131 is the
  largest axis-aligned square inscribed in `K'`, strictly smaller than `K'`, so the clip removes less
  than the truth — sound, and A131 is imported unchanged.)
- **What actually changed the lane test was the CLAMP, not the clip.** The LP framing writes `S` in
  the world frame clamped to `[1/2, s0 − 1/2]`, which for a corner slot halves the centre box
  (`c0_Y0076`: `0.2 × 0.2 → 0.1 × 0.1`) and fattens `K'(S)` from 0.566 to 0.736. With that core the
  400,000-pose screen stops refuting on two cells.
- **`k5_11_interior_Y1110 TR(0,0)`: `LANE_K'(C | S, H_clipped) = 0` is CERTIFIED on BOTH tilt pieces**
  — 36 and 35 leaves, **0 open**, 36 s and 37 s. First empty conditional lane cover ever obtained.
  The kill then needs `M(C | S, H_clipped) = 0`, and that is where it stops: the screen finds no
  meeting pose of the clipped `H` box clear of the other cores in 100,000 draws, but
  `cond_can_meet`'s cover discharges **ZERO** leaves — `(max_depth 40, max_open 5,000)` → 0 leaves /
  5,001 open / 21.8 s; `(42, 40,000)` → 0 leaves / 40,001 open / 183.8 s. The reason is structural,
  not budgetary: `H_clipped` sits at frame `[1.374, 1.519]²` with `hmax ≈ 0.686`, so
  `box_misses_cell` needs `x0 ≥ 1.686` and can never fire, the container prune never fires on an
  interior box, and the shared-point discharge finds nothing — the DFS fills its open budget in one
  corner. A third rung was stopped at 674 s rather than bought.
- **`c0_Y0076` is NOT dead by the split, on either route.** YES-by-LP `τ = 4 = budget` on both
  pieces; YES-by-lane blocked with the open set GROWING with depth (159 → 270 → 646 at
  `(22, 8k) → (24, 30k) → (26, 60k)`), and piece 1 has `M_lb = 1` outright. Its NO child stands
  certified (frozen `verify_case` PASS), so no `A136 closures` record is written — there is no
  closure. `c0_Y0787` and `c0_Y0959` are refuted on the lane side even after the clip (free meeter
  realised at clearance 4.37·10⁻² and 1.23·10⁻¹); `Y0130`/`Y0147` have `lane_lb = M_lb = 1`.
- **Verdict on the population**: do not run the split over the 1,238 records. The YES-child LP costs
  4–80 s per sub-case and always returns `τ = budget` for the accounting reason above; the geometric
  route needs an `M` cover whose prune set is empty by construction whenever `H` is interior.
- **Cost** ≈ 0.7 CPU-h of the +2 CPU-h extension (12 YES-child LPs, 24 clip LPs, 12 clip+lane
  screens at 400,000 poses, 7 lane-cover rungs, 2 M-cover rungs + 1 stopped). One A158 python at a
  time throughout; the launcher waited for a slot (the box sat at 16 from the other campaigns for
  much of the window and one launch was refused outright).
- Files added under `attempts/A158-slot-split/`: code `yeslp158.py`, `clip158.py`,
  `lanedeep158.py`, `mdeep158.py`, `run158g.ps1`; results `yeslp158.jsonl`, `clip158.jsonl`,
  `lanedeep158.jsonl`, `mdeep158.jsonl`, `{y0076,y1110,five,deep}_job*.jsonl`;
  `notes/addendum_b.md`. No certificate was emitted by either route.
