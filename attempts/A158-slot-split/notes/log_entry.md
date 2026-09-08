

## 2026-09-08 — A158-slot-split (Opus engineer) — done-mixed
- **Task**: the PI's tautologous YES/NO split on the near-simple slot box
  `S(r, tt) = {centre within r of the exact slot centre, tilt within tt of 0/90}` — **YES**: some
  square's pose is in `S`, killed by A141's lane leaf with `K'(S)` as an EXTRA obstacle; **NO**: no
  square's pose is in `S`, a `caselp` `NoFam(S)` plus an A135 exact-core LP re-solve — on
  `c0_Y0076 TL(0,0)` first, then over the alive A57/A60 nodes whose LP **dual support** puts weight
  ≥ 0.5 into some usable slot's `S` box. Five further cells were named by the coordinator mid-run:
  `c0_Y0787 BR(0,1)`, `c0_Y0959 TR(0,1)`, `k5_11_interior_Y0130 TR(0,0)`,
  `k5_11_interior_Y0147 TR(0,0)`, `k5_11_interior_Y1110 TR(0,0)`. READ-ONLY on every campaign and
  on A112/A118/A132/A135/A136/A141/A157; new files only under this attempt plus three named appends.
- **The leaf is right and it is cheap.** Once some square's pose is in `S`, the number of squares
  meeting `int C` is at most `1 + LANE_K'(C | S) + M(C | S)`: the `find_witness` discharge against
  `K'(S)` **identifies** the pose with the `S`-square (`PolyCoreT5.shared_point_same_square`)
  instead of contradicting it, so the extra core costs nothing and the kill rule is `LANE = M = 0`.
  Every piece is already deployed — `yes_or_no` with a ONE-element list (A120's clauses A2/A3 become
  vacuous), `noneIn_of_clamped` for the NO bridge, A136's `zone_sub_box` on the written rationals,
  the frozen `verify_case.py`, A141's cover and `M` machinery. One new named Lean obligation,
  `slot_singly_met_of_someIn` (`notes/leaf.md`).
- **Frames**: the leaf lives in the cell's corner frame at side `m`, the LP in the world frame at
  `s0`, so the NO zone is the **intersection** over `m ∈ [m_lo, s0]` of the pullbacks (inward — for
  A57 that costs up to 1.6e-3 per coordinate) while the YES cover uses the larger float box (also
  the sound direction, since `S' ⊆ S ⇒ K'(S) ⊆ K'(S')`). The corner clamp to `[1/2, s−1/2]` is a
  real bite: `c0_Y0076`'s nominal `[0.4, 0.6] × [3.277084, 3.477084]` clamps to a quarter of itself
  — and still kills. **`k6_23` verified**: FULL window `[191/50, 969271/250000]`, converted by A114.
- **The population**: **1,238 of the 1,693 alive A57/A60 records (73 %; 1,590 distinct nodes —
  k5_11 713, k5_16 552, trump5 325)** keep `τ ≥ budget` on a dual square sitting in some usable
  slot's `S(0.10, 10°)` box (A57 1,079 — k5_11 575, k5_16 504; A60 159; L1 962 / L2 243 / L3 19 /
  L4 14). Commonest: `k5_11 TR(0,0)` 420, `k5_11 BR(0,1)` 219, `k5_11 TL(1,0)` 205,
  `k5_16 BR(0,1)` 184, `k5_16 TL(1,0)` 166, `k5_16 BL(1,0)` 163.
- **`c0_Y0076 TL(0,0)` — the NO child is DEAD and the kill is the slot box's.** `NoFam(S(0.10,10°))`
  takes the node LP from `τ = 5.000000` to `τ = 4.000000`, `η = budget − τ = 1.000000` (20.6 s,
  converged); the **control** (identical exact-core re-solve, no `NoFam`) gives `τ = 5.000000`
  (3.0 s). Certificate `certs/no_c0_Y0076__TL0_0__r0.1_tt10.json` (4 atoms, total `103/25` = 4.12 <
  5), through A136's `narrow` (`ZONE ⊆ BOX` on the written rationals, max inward shift 7.40e-8),
  **PASS on the frozen `verify_case.py` (sha `521cb01f…`) in 1.0 s** — 7,262 boxes, 1,863 exempt
  (core 1,861, nofam 2), "node DEAD". So **`c0_Y0076` provably places a square within 0.10 of the
  exact `TL(0,0)` slot centre at tilt within 10° of axis-aligned.** (`verify_param.py` rejects the
  file as MALFORMED — it consumes the PARAMETRIC schema, not a fixed-side
  `case-measure-certificate-v1` — so the second-verifier cross-check is unavailable for this
  certificate kind, as in A136.)
- **The YES child does not exist: 0 of 141 measured cells.** 139 are refuted by a **realised** free
  second meeter — in the container, meeting `int C`, clear of every pin core, of `K'(H)` and of
  `K'(S)` — at 400,000 draws, at `tt = 10°` **already at `r = 0`** (5 s/cell, no cover). At `tt = 0`
  the largest closable radius is `2.9e-6 … 2.2e-3` per cell; three cells fail even at `r = 0,
  tt = 0`. On the two cells the screen did not refute, the certifying cover was bought and each
  closes exactly ONE half: `k5_11_interior_Y1110 TR(0,0)` certifies **`LANE_K'(C | S) = 0`** (the
  first time this cover has ever closed) with `M = 1`; `k5_16_interior_Y1014 TL(1,0)` certifies
  **`M(C | S) = 0`** with `LANE = 1`. Both give `1 + LANE + M = 2`.
- **Outcome over the split: BOTH-dead 0, NO-only 1, YES-only 0, NEITHER 140.** The other two A60 PI
  cells are NEITHER: `c0_Y0787 BR(0,1)` and `c0_Y0959 TR(0,1)` keep `τ = 5.000000` at
  `r = 0.10/0.05/0.02`, at `tt = 0.4°`, and even at `r = 0.20, tt = 20°` — the LP just moves the
  slot square outside the box. The sharpest near-miss is `k5_11_interior_Y0130 TR(0,0)`, where
  `NoFam(S)` eats the node's whole slack, `τ 5.500000 → 5.000000` exactly (A149's polycore arm
  reached the same value independently the same afternoon).
- **Why the halves cannot meet — arithmetic before geometry, and in the TILT alone.** `caselp` drops
  a row only if its centre is inside the zone by `EPS_ZONE = 2e-3` and its tilt inside a
  `t`-interval by `EPS_TH = 0.3°`; `S`'s intervals `[0, tt]`, `[90−tt, 90]` have empty margined
  forms for `tt ≤ 0.3°`. So **an `S` the YES child could close on exempts not one LP row** and the
  NO child is bit-for-bit the original LP. Measured on `c0_Y0076`: NO needs `r ∈ (0.02, 0.03]` at
  `tt = 10°` and `tt ∈ (1.5°, 2°]` at `r = 0.10`; the YES side was measured through the only
  remaining band, `tt = 0.31, 0.40, 0.49°`, and is refuted there too. Because the tilt bound does
  not involve `r`, no anisotropic box helps.
- **The PI's geometry is NOT refuted — the `K'`-based leaf is.** `pair158.py` looked for an explicit
  interior-disjoint pair (a pose IN `S` clearing every node core, and a free second meeter) on the
  six PI cells at `(r, tt) ∈ {0.10, 0.01} × {10°, 0.5°}`, 600,000 draws each: **none, max pair gap
  negative everywhere** (−6.1e-4 on `c0_Y0959`, −0.67 on `Y1110`). `K'(S)` is the intersection over
  the WHOLE box, so the intruder clears it while still overlapping every individual square with a
  pose in `S`. The repair — A141's `lane_corner_split` shape, partition `S` and run the leaf per
  piece — needs pieces `≤ 3.7e-4` in centre and `< 0.5°` in tilt, ≈ `1.5e6` pieces for
  `S(0.10, 10°)`, **≈ 400 CPU-h per cell**.
- **Every NO kill is quoted against a control**, because A135's exact cores are strictly larger than
  several stored ones and five of the top-20 records are `converged = false,
  dead_unconverged = true` (their stored `τ ≈ 4` was never a bound). 7 raw kills, **6 of them
  reproduced by the control with no `NoFam` at all** — artefacts of the exact-core re-solve, not of
  the slot box. One of the six is new information for A149's lane and is recorded only as an
  observation: `k5_16_interior_Y1039 BR(0,1)`, stored `τ = 4.999999999`, goes to `τ = 4.000000`
  (converged) on the exact-core re-solve alone. `k5_16_interior_Y1014`'s emitted certificate is true
  and verified but **not attributable** to the slot box for the same reason, and is not claimed as a
  split result.
- **Cost** ≈ 1.8 CPU-h of a 4 CPU-h cap (66 LP solves, 4,848 LP-seconds; 141 YES screens; 32
  crossover bisections; 24 pair hunts; the 1,693-record population scan in 31 s). **Exactly ONE**
  A158 python process on the box at any time, Normal priority, affinity `0xFFFF`, the other
  campaigns holding 14–15 (A149 4+4, A156 2+2, A136 2–3) — the launcher waits for a slot rather than
  exceeding 16, and its first pass recorded seven `SKIPPED: box already at 16` lines doing exactly
  that. Free physical never below 10.3 GB (gate 3 GB), free commit never below 75 GB (gate 6 GB);
  longest single LP 442 s against the 1,500 s wall, which never fired; no sentinel touched (A57's,
  A137's and A124's are all set and all scoped elsewhere), no shard launched, no recursive delete.
- Files: `attempts/A158-slot-split/` (code `slotlib158.py`, `probe158.py`, `pop158.py`,
  `xover158.py`, `yesscreen158.py`, `yescert158.py`, `no158.py`, `pair158.py`, `mktop158.py`,
  `mkcontrol158.py`, `sample158.py`, `sum158.py`, `run158{,b,c,d,e}.ps1`, `verify158.ps1`; results
  `pop158.{json,jsonl}`, `recs158.json`, `top158.jsonl`, `sample158.jsonl`, `xover158*.jsonl`,
  `yesscreen158.jsonl`, `yesscreen_pop158.jsonl`, `yescert158.jsonl`, `no158.jsonl`,
  `pair158.jsonl`, `summary158.json`; certs `no_c0_Y0076__TL0_0__r0.1_tt10.json` (+ report) and
  `no_k5_16_interior_Y1014__TL1_0__r0.1_tt10.json` (+ report); `BRIEF.md`, `notes/method.md`,
  `notes/leaf.md`), plus appends to `attempts/A57-shadow-trees/PAUSED.md`,
  `attempts/A60-trump5-campaign/notes/ledger.md` and `docs/residue_ledger.md` §1.
