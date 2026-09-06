# A102 — the rigidity drain: contact-torque test on floor-depth second meeters (Opus chore, measurement)

Context (2026-09-06). k0dir2_87 produced the first strictly K0-BLOCKED packing below side 4 (certified 3.990748514985,
`attempts/A87-drain-flow/results/k0dir2_87.records.json`, floor 1e-3). The PI drained it by eye and the drain verifies
exactly (`attempts/A87-drain-flow/code/pi_drain_3p9907.py`, figure `docs/residue_map/strict_3p9907_drain.svg`): the
floor-depth second meeter (square 3, tilted 1.31 deg off axis) has three contacts (square 2, the right wall, square 8's
25-degree edge) whose torques about its centre all have the same sign (CCW: +0.46, +0.49, +0.23), so the rotation to
axis-aligned is unopposed; it is collision-free (2000-step SAT sweep), lifts the vertex out of the BR cell, BR drops to
one meeter (K0-FREE), and simultaneous snaps of seven squares give a valid k = 7 packing at the same side. The census
measured DEPTH and called the corner blocked; the mechanical test (are all contact torques on the intruder one-signed?)
decided it in one look. Make that test a tool and run it on every strictly K0-BLOCKED packing the lab owns.

Read first: `attempts/A87-drain-flow/code/pi_drain_3p9907.py` (the exact check to generalise: contact detection at the
certification tolerance 5e-9, contact normal = outward normal of the touched EDGE — not the centre-to-contact direction,
which gave the wrong sign on square 8 — torque about the intruder's centre, rotation sweep, simultaneous snap search by
exhaustive assignment over lattice cells within 0.7, Young-closure count of simple squares), `notes/degen87.md` and
`results/degen87.jsonl` (the earlier simultaneous move set and its stalls), `docs/proofs/flood_lemma.md` s.1 (SNAP
destination form, MULTI, SHELL) and s.2 (CELL-INTERLOCK), `docs/residue_map.md` s.5, `attempts/A85-k0-route/results/strict85.json`.

## Inputs — every strictly K0-BLOCKED packing on disk
(a) the four floor records in `k0dir2_87.records.json` (1e-6, 1e-4, 1e-3, 1e-2); (b) the eight A87 K0-BLOCKED packings
(degen87 inputs, incl. record_s0115 at 3.98548) and the strict85 set; (c) every confined-descent endpoint in
`k0dir2_87.jsonl` / `k0dir2_87.deep.jsonl` with `blocked_at_best` true and side < 4.01, if poses are recoverable (ask
A87's code, do not re-run descents). Trump as the canary (its TL crowd {4, 6} at depth 0.155/0.168 must NOT drain).

## T1 — the rigidity test (per packing, per corner, per second meeter)
For each corner cell met by >= 2 squares, for each meeter Q of depth d2 (start with the shallower one): list Q's contacts
(squares and walls, gap < 1e-7), the contact point, the edge normal, and the torque about Q's centre. Classify Q:
FREE-ROT if all torques have one sign (or there are <= 1 contacts), and test the CCW/CW rotation about the centre to
the nearest axis-aligned angle by a SAT sweep (>= 2000 steps, tol 5e-9); FREE-TRANS if the contact normals leave an open
half-plane of translations (the normals' cone is not the whole plane) and test the translation that exits the corner
cell; PINNED otherwise (record the opposing contacts). Also test rotation about each contact vertex of Q. Output per
meeter: class, the unopposed motion, whether it is collision-free, and the corner meeter counts after it.

## T2 — the drain
When T1 frees a corner (drops it to one meeter): apply K0-FREE / SNAP destination form — the exhaustive simultaneous
snap search of pi_drain_3p9907.py (all near-axis squares, lattice cells within 0.7, keep valid packings, maximise the
Young-closed count) — and report the resulting class (Young diagram per corner, k). Iterate: after the snaps, re-run T1
on the remaining crowded corners (the freed cells change the contacts). Stop when no corner frees or k >= 1 is reached.
Report per packing: initial (side, n_meet, d2 per corner), the sequence of moves, final k and class, and — for the ones
that do NOT drain — the exact PINNED contact set of every second meeter (this is the residue that a theorem has to
handle). Distinguish "pinned by a wall + one square" from "pinned by two or more squares".

## T3 — the statement to hand to theory
From the results, state the empirical rule in one line: e.g. "every floor-depth (d2 <= 1e-2) second meeter in the
corpus is FREE-ROT or FREE-TRANS", or the exact exception. If all sub-4 strictly blocked packings drain to k >= 1 at the
same side, say so and give the largest d2 that drained; if any does not, give its figure data (poses, side, pinned
contacts) so it can be drawn. Do not attempt the proof; name the obstruction.

Constraints: <= 1 process, BLAS-pinned (OMP/MKL/OPENBLAS 1), pure geometry (no LP; seconds per packing), headroom
> 6 GB commit and > 3 GB free physical; A57/A60/A61/A96 untouched; frozen verifiers untouched; no rebase/autostash/reset
(fetch + plain merge + push own paths). Writes: `attempts/A102-rigidity-drain/{code,results,notes,logs}`, registry row,
LOG.md, a one-line chip on depgraph K0.RESN (owner A102). Terminal events only: one report when the table is complete,
ordered T3 rule first, T2 drain table second, T1 detail third, pointers last. Use the drawing conventions of
`docs/residue_map/gen_strict_drain.py` if you produce figures (every square geometry-checked).
