# A217 torque probe -- results table (snapshot 2026-09-14 evening; `collect217.py` re-generates it from the search files)

Witness files: `witnesses217.jsonl` (486 kept of 3,555 distinct FJ-feasible local optima, D4-quotiented; the 40 lowest
per class plus every witness with >= 3 doubly-met corners), `torque217.jsonl` (the Fritz-John stress at each: HiGHS LP
on the active rows, NNLS residual, forces, per-square and per-corner torques, LP ranges over the multiplier polytope),
`hunt217.txt` (the class-wise ranges printed by `hunt217.py` / `hunt217b.py`), pages
`docs/residue_map/campaigns/A217-torque/torque217_<wid>.svg` + `torque217_gallery.svg` (39 drawn).

## 1. Witness classes (all local optima of the side by SLSQP on the selected SAT rows, outer axis re-selection,
active-set FJ residual < 1e-8 by NNLS; s-hat = 3.877084)

| class | meaning | distinct | lowest side | doubly-met open corners n2 = 0/1/2/3/4 |
|---|---|---|---|---|
| SETTLED | free run, >= 1 slot square (the settled-corner reference set; Trump = family 0, family 6 = 3.886746 ...) | 430 | 3.886746 | 376 / 51 / 3 / 0 / **0** |
| K0FREE | free run, NO slot square (k0), a genuine FJ point | 417 | 3.897231 (near-slot upright 4e-4 off; first tilted-corner one 3.966513, two 44 deg corner diamonds) | 351 / 62 / 3 / 1 / **0** |
| BOXK0 | tilt box on the corner squares (theta in [t, 90-t], t = 3/10/20 deg), bound INACTIVE: genuine k0 FJ point | 36 | 4.000000 | 32 / 3 / 0 / 1 / **0** |
| HELD | tilt box ACTIVE: a k0 local optimum of the BOUNDED problem, not an FJ point of the free one; the bound multiplier = the missing torque | 2487 | 3.907159 | 798 / 963 / 582 / 136 / **8** |
| CROWD | every corner box met by two designated squares with margin delta (0.05 / 0.02), crowd rows ACTIVE: held by external forces | 185 | 4.001364 | 0 / 0 / 0 / 0 / **185** |
| CROWD0 | as CROWD with every crowd row inactive = a genuine FJ point with four 2-crowds | **0** | -- | -- |

Sources: A85's 262 k0 optima (all four variants each: 1,048 runs), 600 random starts x 4 variants (2,400 runs), 168+
crowd starts (the crowd search was still running at the snapshot; `search217_crowd0.jsonl` grows). The A37 atlas entry
with no slot square (family 11, s = 3.888014, NOT-CP) drains to family 6 (3.886746, three slot squares) -- it is not a
k0 FJ point; A163's witnesses all carry pins (settled corners) and do not qualify. **Every one of A85's 14 k0 "optima"
below 3.9 drains to a settled-corner optimum** (3.886746 family 6 / 3.897231) under the SAT-row SLSQP -- A87 s.5.4's
finding ("not Fritz-John points") reproduced constructively.

## 2. Identities (checked on every FJ-feasible witness; the numbers are max |error| over the class)

| identity | SETTLED | K0FREE | BOXK0 | HELD | CROWD |
|---|---|---|---|---|---|
| total wall torque about the container centre = 0 (internal contact torques cancel pairwise) | 4e-9 | 7e-9 | 1e-8 | not 0 (external rows carry torque: up to 0.94) | not 0 (up to 15) |
| tilted square touching walls with total wall force W: tau_wall = W (sin theta - cos theta)/2, EVERY wall the same sign (the wall torques a tilted square toward its nearest axis alignment) | 2e-16 | 2e-16 | 4e-16 | 3e-16 | 2e-15 |
| per-square force and torque closure | 3e-8 | 5e-8 | 1e-8 | 2e-9 | 5e-8 |
| lam0 = 0 (pure self-stress) witnesses | 0 | 0 | 0 | 0 | 0 |

## 3. The candidate invariants and their fate

| # | candidate | fate |
|---|---|---|
| C1 | "The sum over corners of the signed corner torques T_c (corner frame, det-corrected) vanishes / has a fixed sign at every FJ point." | FAILS on SETTLED already: T_c at Trump's open TL corner = +0.035 (unique), at other settled optima T_c ranges over [-0.30, +0.20] with both signs; no identity beyond the global one of s.2 (which involves ALL wall squares, not the corner meeters). |
| C2 | "An open corner's meeters receive net wall torque of sign chi(corner)" (chi = +1 if the meeter's tilt in the corner frame is < 45 deg). | An IDENTITY per tilted meeter, not a constraint: tau_wall = W (sin - cos)/2 has sign -chi always (s.2), so sum_m chi_m tau_wall_m <= 0 on every class (max +0.0 everywhere). Carries no information about k0. |
| C3 | "A tilted wall-loaded meeter receives holder torque of sign chi (anti-aligning)." | Identity at a free FJ point (holder = -wall); it becomes a CONSTRAINT only where the holders cannot supply it: at CROWD witnesses the interior holders torque the meeter TOWARD alignment in 368 of 551 cases (they push it flat too) and the external crowd force supplies the whole anti-aligning torque; 532 of 551 crowd torques on tilted meeters have sign chi (the 19 exceptions are near-upright meeters, tilt <= 9 deg from an axis, multipliers <= 0.14; `verify217.py`). At HELD witnesses the bound torque has sign chi in 494 of 494 cases. |
| C4 | "No FJ point has four doubly-met open corners" (the PI's conjecture in packing terms). | **SURVIVES on every witness**: 0 of 883 genuine FJ points (SETTLED + K0FREE + BOXK0) have n2 = 4; forcing n2 = 4 (CROWD, 185 distinct) ALWAYS leaves >= 1 crowd row loaded (1 / 2 / 3 / 4 corners in 3 / 67 / 61 / 51 witnesses); the pull is along the meeter's wall toward the corner in 569 of 639 rows (the meeter wants to retreat along its wall) and acts at a wall-touching square in 639 of 639. Not a torque identity: a first-order statement about the direction of retreat. |
| C5 | "At a k0 FJ point every wall-loaded meeter of a doubly-met corner is torque-neutral (upright-flush or tilted exactly 45 deg), i.e. T_c = 0 at every doubly-met open corner." | SURVIVES on the k0 classes: all 14 doubly-met open corners of K0FREE / BOXK0 have |T_c| < 4e-16 and their loaded meeters are 45-deg diamonds or flush uprights; FAILS (as it should) on SETTLED: Trump TL (square 6 at 40.18 deg, tw = +0.016; the flush square 4, tw = +0.019). Sample is thin (14 corners, all at s >= 4.0). |
| C6 | "Parity / winding of the wall-torque signs along the boundary chain." | Not testable as stated: the chain of wall squares is broken at every open corner met by two squares that do not touch each other (most CROWD corners), and the sign of tau_wall is the tilt side (identity C2), so the winding count is the count of tilt-side changes around the boundary -- free. Dropped. |

## 4. The interior grains (the PI's remark)

Trump's five tilted grains (40.18 deg): squares 6 and 10 touch a wall (W = 0.271, 0.321) and carry tau_wall = -0.016,
-0.019 (toward alignment), closed by their holders (+0.016, +0.019); squares 7, 8, 9 touch no wall (W = 0), their
holder torques sum to zero with contacts on BOTH sides of their centres (the non-convex pocket). At the 883 genuine FJ points every wall-free tilted square with loaded contacts (254 of them) receives holder torques of BOTH signs on the same square (`verify217.py` (a): 254 both / 0 one-signed); no sign constraint appears -- the constraint appears exactly on the wall-touching squares (one wall: the
identity of s.2 with W the single wall's force; two walls: the same identity with W the sum, both walls torque the same
way), as the PI's remark predicts.
