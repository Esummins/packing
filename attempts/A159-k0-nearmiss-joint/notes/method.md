# A159 — method: what was checked, in what frame, at what width, and what each result is worth

## 0. The question, restated

The PI, on `docs/shadows/k0v4/l1_124.svg`: *"TR(0,0) cannot be doubly met — two squares can each
touch the corner cell but they are mutually exclusive."*

A141 recorded `l1_124` TR as NEAR-MISS (`LANE_K' <= 1` certified, `M = 1`) and, in
`results/t5_twocrowd.json`, claimed a *realised* two-crowd there. A148 drew that witness and
measured `H` reaching **-0.026 to -0.036** into the corner — i.e. not reaching it — and A148's LOG
entry attributed the discrepancy to a **corner-frame transport bug** ("A141 and A157 run the lane
test IN THE CELL'S CORNER FRAME"). Three things had to be separated: the frame, the width, and
the leaf.

## 1. The frame: A141 is container-frame, and A148's LOG generalises A157's bug too far

`polylane.corner_cell(c, s, w)` returns

    TR  =  (s - 1 - w,  s,  s - 1 - w,  s)   =   [2.8515739257860595, 3.877084]^2

in **container** coordinates, and `polylane.centre_window` is built from that rectangle, not from
`cell_rect(i, j) = [i, i+1] x [j, j+1]`. Every `cell` field stored in
`A141/results/t2_cells_s*.jsonl` carries those container numbers. The poses in
`t5_twocrowd.json` are therefore container-frame, in container units (side `s0 = 969271/250000`,
unit squares, **tilt in degrees**, 90-periodic) — and A159 T1 confirms it from the records
themselves rather than from prose: for all 28 witnesses `H`'s pose lies inside the cell's own box
`B`, which is stated in container coordinates (e.g. `l1_124` has `B = [2.46263075, 2.5674485]^2 x
[60°, 75°]` and `H = (2.4734, 2.4885, 61.32°)`). Under any of the seven other D4 maps `H` would
leave `B`.

A148's own `data148.py` gets this right in code (`_witness_poses`: *"A141's two-crowd poses come
from a different code path that already works in the container frame and are left alone"*). The
corner-frame bug is **A157's**, and the LOG entry's "A141 and A157" over-attributes it. Nothing in
A141's records needs re-framing.

## 2. The width: the discrepancy is the K0-WIDEN pad, and it is the whole story

A148's page measures `depth_into_cell` against `data148.cell_rect`, i.e. the **plain unit corner
cell** `TR(0,0) = [s0 - 1, s0]^2`. The lane leaf is stated over the **widened** box of Lemma
K0-WIDEN, `[s0 - 1 - W0, s0]^2` with

    W0 = (lambda_max - 1)(1 + 1/sqrt2),   lambda_max = s0/3.82,   W0 = 0.0255100742139405.

`-0.026 to -0.036` against the unit cell is `+0.0255 - (0.026 … 0.036)`, i.e. **a hair either side
of zero** against the widened box. So the two measurements were never in conflict; they were
taken against two different rectangles that differ by 0.0255.

`code/xwitness159.py` decides which side of zero, exactly. Poses are read as exact binary
rationals; the geometry is done in `mpmath.iv` interval arithmetic at 60 dps (raised to 240 if any
enclosure straddles 0, which never happened); SAT over the union of edge normals is **complete**
for convex polygons, so a strictly negative gap is a *proof* that the interiors meet and a
strictly positive one a proof that they do not. Seven quantities per witness: `H` and free square
inside the container, each against the widened box, each against the unwidened cell, and the
square-square separation.

**Result: 28 of 28 witnesses are exact and real.** `H` penetrates the widened box by between
`1.84e-5` (`l1_124`, the PI's own page) and `1.87e-1`; the free square penetrates by `8.6e-4` to
`1.02`; the pairs are separated by `1.8e-3` to `9.7e-2`; every `H` is inside its `B`; every square
is inside the container. A141's claimed gaps reproduce to 9 digits.

**And the PI is right about the unit cell.** In **0 of the 28** witnesses do *both* squares meet
the unwidened cell `TR(0,0)`: in 25 the conditioned square `H` misses it (by `+0.0083` to
`+0.0360`) and in the other 3 the *free* square misses it (by `+0.0138` to `+0.0246`). Every
recorded two-crowd lives entirely on the 0.0255-wide widening annulus. The reading and the record
are both correct, about different rectangles.

## 3. What that costs the lane leaf — Lemma A159-1

> **Lemma A159-1.** Let `C` be the cell, `B_j` the conditioned box, and suppose there are poses
> `H* in B_j` and `F` (a unit square in the container) with `int Q(H*) ∩ int Q(F) = ∅` and both
> `int Q(H*)` and `int Q(F)` meeting `int C`. Then `lane_corner_split(C, ·, j)` cannot close, at
> any depth or piece budget.
>
> *Proof.* Let `B_k` be the piece of the partition containing `H*` (the partition is complete, so
> exactly one does). `K'(B_k) = ∩_{p in B_k} Q(p) ⊆ Q(H*)`, so `int Q(F)` misses `K'(B_k)`; the
> 28 cells carry exactly one conditioned box, so `F` misses **every** core and is a free meeter,
> whence any sound `lane_ub` on `B_k` is `>= 1`. And `H* in B_k` meets `int C`, so
> `box_misses_cell(B_k)` is false and `m_k = 1`. Then `lane_ub + M_other + m_j >= 2 > 1` and the
> piece cannot be discharged. ∎

So the joint split is provably dead on all 28 corners with a surviving witness, and the only
near-misses on which it can be run at all are the **16 with no witness**. This is not a budget
statement; it is a theorem about those 16 being the entire target set.

## 4. THE CANARY — `l1_153`

`l1_153` is a Trump-image cell: a Trump image is doubly met at every corner in the widened sense
by construction (A143/A150; `residue_ledger` §4 records that Trump's lineage "can never die by
K0-FREE — Δ_λẑ has ≥ 2 widened meeters at every corner"), and A154 already used it as the canary
for the (R6) row. A159 T1 sharpens this from "by construction" to an **exact witness**: `H =
(2.6264, 2.3827, 48.21°) in B`, free `= (3.3490, 3.3617, 1.397°)`, penetrations `3.32e-4` and
`1.01`, separation `4.74e-3`, all certified at 60 dps.

The joint split was therefore run on `l1_153` TR **first**, at a budget (192 pieces, depth 10)
larger than A141's own T5 default. By Lemma A159-1 it must not close; if it had, the leaf would
have been proved unsound and everything else in this attempt withdrawn.

## 5. What the leaf is stated over, and why `w = 0` is not a substitute

`code/unwiden159.py` re-runs A141's ordinary leaf at `w = 0` on all 44 near-misses, to test the
PI's reading in its own rectangle. It kills **0 of 44**: `LANE_K' <= 1` with `M = 1` at the
unwidened cell too. The reading is not a `LANE + M` statement — it is the *joint* statement, which
the separate counts cannot express at either width.

Note also that a `w = 0` kill would have been an **s0-only** result. `W0` is exactly the slack
that makes one fixed corner box serve every side in `W = [3.82, s0]`; a kill at the unwidened cell
certifies "singly met" at the fixed side `s0` and does not transport to the window. Every
`unwiden159` record carries `scope: "s0_only"` and `cell_kind: "k0_corner_unwidened"` so nothing
downstream can bank it as a window kill.

## 6. The joint statement, tested directly

`code/twocrowd159.py` asks the PI's question as an optimisation rather than a count:

    maximise  J(H, F) = min( depth(Q_H, C), depth(Q_F, C), gap(Q_F, Q_H),
                             slack(Q_H, container), slack(Q_F, container) )
    over      H in B,  F a free unit square

`J > 0` **is** a realised two-crowd. Multistart Nelder-Mead, run at both widths on all 44
near-misses; every positive hit is re-verified exactly by `xwitness159.check_one` at 60 dps. A
search that fails is reported as `best_J` with the restart count and is **evidence, not a kill** —
the file says so in its own docstring, and no certificate is emitted from a negative search.

## 6b. What the direct search found

| | widened box (`w = W0`) | unwidened cell (`w = 0`) |
|---|---|---|
| realised two-crowd (exact) | **30 of 44** | **8 of 44** |
| of those, new (A141 had no witness) | 2 (`node_117` TR, `s2_near_046_619` BL) | — |
| no two-crowd found | 14 | 36 |
| of those, joint optimum exactly tangent (`|J| < 10⁻⁹`) | — | **17** |

The eight corners where the PI's reading is **false** even at `TR(0,0)`: `l1_192_plain_warm`,
`node_150`, `node_187`, `node_192`, `node_193`, `node_194`, `node_195` (TR) and
`s2_near_046_619` (BL) — each with an exactly re-verified pair, `J` from `6.9·10⁻⁴` to
`7.4·10⁻²`. On the other 36 the sup of `J` is `≤ 0`, and on 17 of them it is 0 to `10⁻⁹`: the two
squares can reach the plain corner cell only in a mutually tangent, measure-zero configuration.
That is the PI's reading, quantified — and tight.

Two corners have **no pose of the conditioned square reaching `TR(0,0)` at all**
(`deepest_H < 0`): `node_117` (`−1.20·10⁻²`) and `s3_far` (`−1.96`). `node_117` was therefore
re-run at `w = 0` with a 6× cover budget (`depth0 24, max_depth 40, max_open 9,000,
max_leaves 400,000`, `results/unwiden159_deep.jsonl`) to try to certify `M = 0` and close it as an
s0-only kill: the LANE cover still returns `None` (open budget exhausted) and `cond_can_meet`
still fails to *prove* the exclusion, so no certificate. `M = 1` in those records means "not
proved excluded", not "can meet".

## 6c. The joint split: 0 of 9, and it is geometry, not budget

| cell (box class) | pieces | closed (all `B_meet`, `lane_ub = 0`) | open | why open |
|---|---|---|---|---|
| `l1_158` (depth 9) | 38 | 23 | 15 | all `lane_ub ≥ 1`, all depth-capped |
| `l1_158` (depth 15) | 495 | 146 | **349** | same |
| `l1_159` (= `l1_159_plain_warm`, `l1_159_sh3_warm`, `node_159`) | 110 | 39 | 71 | same |
| `l2_p114_011` | 229 | 62 | 167 | same |
| `l3_pp114_001_000` | 308 | 63 | 245 | same |
| `node_120` | 50 | 31 | 19 | same |
| `node_125` | 57 | 28 | 29 | same |
| `node_151` | 93 | 46 | 47 | same |
| `node_160` | 94 | 41 | 53 | same |

Two facts make this a closed question rather than a budget one:

* `open_reasons.no_lane_bound = 0` on every run — no open piece is open because the LANE cover ran
  out of budget. Each carries a **certified** `lane_ub ≥ 1`: a free meeter provably survives
  `K'(piece)` there. With `m_j = 1` on the same piece (it is a `B_meet` piece) the total is `≥ 2`
  by certification, not by failure to decide.
* refining does not help: `l1_158` goes from 15 open pieces at depth 9 to **349** at depth 15
  while the closed count only rises 23 → 146. The frontier roughly doubles per level, the same
  divergence A157 measured on the A57 slot covers.

`B_miss` is empty on every class (`n_miss_pieces = 0`): no sub-box of `B` can be certified to miss
the widened corner box at all, so the split never gets the cheap half of its dichotomy.

## 7. Provenance and discipline

Read-only on every campaign and every prior attempt. `polylane` / `polycore` / `emit141` /
`caselp` are imported from A141/A132/A57 and never written. New files live only under
`attempts/A159-k0-nearmiss-joint/`; the only edits outside it are the four named appends.
`check159.py` is A141's `check141.py` (an attempt-local copy — A141 is read-only) extended with
C7 (the B_meet/B_miss ledger and the burden each side carries), C8 (the contradiction guard: a
kill at a corner with a proved realised two-crowd is failed loudly) and C9 (an independent sample
line with its own from-scratch SAT). It imports nothing from the emitter.
