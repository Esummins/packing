# A101 — the Flood Lemma, second attempt: report (Fable lead, theory; 2026-09-05)

Deliverable: `docs/proofs/flood_lemma.md` (Lemma SNAP in destination form, SNAP-SWEEP, MULTI,
SHELL, SNAP-DICHOTOMY, SNAP-SIDE, Corollary OFFSET; Lemma FLOOD-T + NINE; CELL-INTERLOCK = the
exact stall of the static simultaneous move set; composition; Lean shapes). Two read-only chores,
one process each, OMP pinned, < 100 MB, 11 s and 4 s (free physical at launch 4.9 GB, python RSS
of the running campaigns 10.7 GB — no slot taken from A96).

## Chore 1 — `code/cellflood101.py` → `results/cellflood101.json`, `logs/cellflood101.log`

The static simultaneous move set (ALIGN, cell TELEPORT, TELEPORT_FREE, full WALL-SLIDE, static
Young flood, simultaneous combinations) is ONE multi-teleport onto a pairwise-disjoint cell set T
of any of the four corner lattices, feasible iff X(T) = N(T) − |T| ≤ 0 (Lemma FLOOD-T). The script
computes X_min(c) = min over T ∋ c(0,0) exactly (2¹¹ movable sets × max independent cell set),
"meets" = interval-certified SAT depth > tol on the exact rational poses (A87's certifier
re-implemented), tol 10⁻⁹ and 10⁻⁶, on the 8 exact K0-BLOCKED packings of A87 + Trump.

| packing | side | n_meet BL BR TR TL | X_min BL BR TR TL | note |
|---|---|---|---|---|
| record_s0115 (10⁻⁹) | 3.98548 | 2 2 2 2 | **1 1 0 0** | BL/BR: argmin T = the bare corner cell; TR: {TR(0,0), TR(0,1)} moving sq6, sq7; TL: {TL(0,0), TL(1,0)} moving sq4, sq5; no free cell in any lattice, no single-meeter cell |
| record_s0115 (10⁻⁶) | 3.98548 | 2 2 1 1 | 1 1 0 0 | TR(0,0), TR(0,1), TR(0,2), TL(0,0) singly met (strict85's K0-FREE) |
| polish/anchored ×7 | ≥ 4.0000001 | 2 2 2 2 | not computed | side ≥ 4: 16-cell lattices, static flood vacuous (A98 §6.1) |
| TRUMP (both) | ŝ | 1 1 1 2 | 0 0 0 1 | the three 0's are the identity on the exact slot squares; **over every nonempty set of NON-exact cells X_min = 1** (argmin BR(2,0), 2 meeters): Trump admits no multi-teleport — CANARY PASS |

SHELL numerical check (2·10⁵ random pairs, η ∈ {10⁻³ … 0.1}, θ₀ ∈ {0.5° … 10°}): max SAT depth /
(√2 ε) = 0.768 over 1 485 crowders; max corner-frame depth / ((1 + √2) ε) = 0.409 over the 532
crowders obeying CONT. Both bounds hold.

## Chore 2 — `code/snap_yield101.py` → `results/snap_yield101.json`, `logs/snap_yield101.log`

Read-only over 488 `*.witnesses.json` files under `attempts/A57-shadow-trees/certs/**` (13 688
boxes: 5 500 holes, 8 185 undecided, 3 tight). Per box: tilt range (θ = 2 atan t, mod 90°), L∞
distance of the WHOLE box to the nearest of the 36 lattice-cell centres at the node's side, the
flush distance (one coordinate only), and the cell's status for the class (pin / completable
usable / completable unusable / clipped / other).

η-ball (whole box within η of a cell centre, tilt ≤ θ₀), all groups → (pocket96 population = G1
trees + epsgeo):
* (0.01, 1°): 81 boxes, 73 holes, 31 at usable cells, 14 files → 53 holes, 16 usable;
* (0.02, 2°): 232 boxes, 184 holes, 72 usable, 26 files → 89 holes, 32 usable;
* cells: k5_16 BR(1,0) [k6_27 OPEN, unusable] 32, BL(1,0) [k6_23] 16–32, BL(1,1) [not completable
  for k5_16] 5–24; k5_11 TR(0,1), BL(1,2) [not completable] a handful. Matches pocket96's pocket
  population (32/46 at its tolerances; population differences: stale repairedPASS witness files,
  slack/D2/L1/zonescan groups, centre-based L∞).
* Flush pattern (ONE coordinate within 0.01 of a lattice coordinate, tilt ≤ 1°, NOT in the η-ball):
  k5_11 holes 160 against a pin row/column, 83 against a clipped cell, 79 other; k5_16 holes 64
  against pins, 97 against usable cells, 60 against unusable cells — pocket96's "near-flush against
  pin squares", displaced ALONG the pin.
* Distance percentiles (holes): min 0.0034, p01 0.0100, p05 0.030, p10 0.050, median 0.153; tilt
  ≤ 1° for 1 325 of 5 500 holes (24 %) — near-axis squares are common, near-CELL squares are ~1 %.

Leaf verdict: SNAP-T (destination form) needs every other non-pin shadow to miss int C; every A57
node has ≥ 4 unlocalised non-pin squares; **0 nodes flip** (as pocket96's exemption and A98's EX).

## Sweep (A87 `results/k0dir2_87.jsonl`, in flight, 585 rows at read time)

| floor δ | seeds | lowest σ_best_blocked | next |
|---|---|---|---|
| 10⁻⁶ | 300 | 4.0000016 | 4.0000030, 4.0000030, 4.0000067 |
| 10⁻⁴ | 291 | 4.000023 | 4.000053, 4.000087, 4.000141 |
| 10⁻³, 10⁻² | queued | | |

vs the exact record (δ ≤ 1.7·10⁻⁸) at 3.98548: m*(δ) is floor-dependent; every value ≥ ŝ + 0.108.

## Canary

Trump: no multi-teleport of any kind (X_min = 1 over all non-exact cell sets, both tolerances);
the one disturbed square (upright sq4, η = 0.0326 at BL(0,2)) is crowded by sq7 at 0.016 ≤
(1 + √2)·0.0326 = 0.079 (SHELL (b)), extension k6_07 open at ŝ — SNAP-SIDE vacuous. PASS.
