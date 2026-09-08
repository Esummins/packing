# A159 — the k0 near-miss corners, jointly: is A141's two-crowd real, and does the joint split close the rest? (Opus)

Context (2026-09-08). The PI, reading `docs/shadows/k0v4/l1_124.svg`: **"TR(0,0) cannot be doubly
met — two squares can each touch the corner cell but they are mutually exclusive."**

A141 (`attempts/A141-polycore-lane/`) recorded `l1_124` TR as **NEAR-MISS** (`LANE_K' <= 1`
certified, `M = 1`) and claims, in `results/t5_twocrowd.json`, a *realised* two-crowd: a free
square `(3.3649, 3.3683, 0.882)` and the conditioned square `H = (2.4734, 2.4885, 61.32°)` with
gap `0.018`, both meeting the **widened** TR box of Lemma K0-WIDEN (`a_w = 1.02551`, i.e.
`[s0 - a_w, s0]^2`). A realised pair is fatal to every lane leaf at that corner.

But A148 (`attempts/A148-gallery-v4/`, `864d314d`; its notes on the **corner-frame transport
bug** — A141/A157 poses are said to be in the cell's corner frame, corner at the origin, axes
inward, reflections negating the tilt) drew that witness and found `H` reaching **-0.026 to
-0.036** into the corner, i.e. `H` does *not* meet the corner in the witness; the coordinator's
hand check agrees (H's nearest edge passes below-left of `(2.85, 2.85)`). So A141's two-crowd
witness on `l1_124` may be bogus (frame or units), and the PI's mutual-exclusivity reading may be
a real kill.

## T1 — EXACT re-examination of every claimed two-crowd
All 44 k0 near-miss corners; the five converged-alive cells `l1_124`, `l1_153`, `l1_158`,
`l1_159`, `l2_p114_001` first. Transport each pose to the container frame *correctly* (read
`polylane.centre_window` / `cell_rect` and A148's transport code), **state the units**, and check
with exact SAT: the free square inside the container, interior-disjoint from `H`'s square, both
meeting the *interior* of the widened TR box, and `H`'s pose inside the cell's box `B`. Report
how many of the 28 claimed two-crowds survive.

## T2 — for every near-miss whose witness fails, the JOINT split, properly
`B_meet` = the sub-boxes of `B` whose `H` poses meet `int(widened corner box)`, certified by
intervals; `LANE_K'(corner | B_meet)` with `K'(B_meet)` as the obstacle (strictly larger than
`K'(B)`). `B_miss` = the rest, where `LANE_K'(B) <= 1` already gives *singly met*. If
`LANE(B_meet) = 0` the corner is singly met in every case ⇒ **K0-FREE** ⇒ the cell is dead
(conditional on K0-O1, as all lane kills are). Certificates in A141's formats
(`polycore_split_lane_v1` + witness points), an **independent** checker (extend `check141.py`;
share nothing with the emitter), and a sample line per cell (drawn → tested → hits: ≥ 10⁴ poses
of `H` in `B_meet`, no free square found disjoint from `H` meeting the box).

## T3 — THE CANARY
`l1_153` is a **Trump-image** cell; Trump images are doubly met at every corner in the widened
sense by construction (A143/A150), so **if the joint split kills `l1_153` the leaf is UNSOUND** —
run it there first and stop to report if it kills.

## T4 — fold-in
`results/joint_kills159.jsonl`; one line in `attempts/A115-k0-corner-rows/notes/t6_report.md`'s
hand-off list; the `docs/budget.md` k0 row clause (cells removed at A115's per-cell rates);
`docs/residue_ledger.md` §4 one sentence; `docs/shadows/k0v4/review_k0v4.csv` `polycore_status`
appended.

## Rules
Pure geometry. ≤ 2 processes at BelowNormal with affinity `0xFFFF` (the box is at its 16-process
ceiling — count and wait for a slot; never exceed). Cap 3 CPU-h. Read-only on every campaign and
prior attempt (new files only under this attempt plus the named appends). No recursive deletes.
`PYTHONDONTWRITEBYTECODE=1`. Git = fetch + plain merge + `git commit -- <pathspecs>` only.
Registry row and LOG entry. Report ONCE: the canary result first, the witness re-examination
table second, the joint-split kills third, pointers last; no interim messages.
