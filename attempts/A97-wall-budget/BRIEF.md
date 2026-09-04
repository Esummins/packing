# A97 — the wall-length budget for K0-BLOCKED (Fable lead, theory; PI mechanism)

PI mechanism (2026-09-04): a near-zero-wastage corner is a JAM (slot square flush on both walls at
offset g < 0.1 plus a near-flush nick partner: 68 of the 7,044 realisable pair boxes, cases85). A jam is
locked only from its far side (Lemma MENU, docs/proofs/tilt_floor_k0.md): an on-wall pusher against
its outer edge, or a downward contact at its outer top vertex; the corpus (d1max87) shows the on-wall
pusher + a flush kiss in every deep jam, never a vertex presser. A zero-wastage pusher is an upright
flush on the same wall, width 1, so a wall carrying a jam plus pusher has two flush unit widths and
only 1.877 left; the adjacent corner's crowd (doubly intruding its own slot, reach up to 2.1-2.4) must
put its wall member in the remaining length (per-wall <= 3 squares touch a wall, structure_lemmas L6/
A31; flush rulers <= 5, A50) or intrude from the other wall's side, in which case the pusher (to x = 2.1)
collides with the crowd's reach region (from x = s - 2.1 = 1.78). Two jams on one wall are impossible
outright (four flush widths > s and > 3). So jams are area-free but wall-length-expensive, and they
squeeze both neighbours toward compact near-corner types — the 0.85 cell of A47's corner table
(centre [.9,1.1]^2, near-upright) or wedges — which is where the wastage lands. Reach arithmetic alone
does NOT separate crowds (cases85: min pair reach_ub 2.001 > s0/2), so the wall budget must be argued
as a 1-D packing of wall-touching squares, A50-ruler style, not as a reach bound.

Read first: docs/proofs/tilt_floor_k0.md (JAM-0, LOCK, MENU, TF-U), docs/proofs/structure_lemmas.md
(per-wall <= 3, L6 wall-to-wall chain), attempts/A50-wall-termination (ruler quantisation, tilt table),
docs/proofs/nocrit_k0_blocked.md (anchoring columns >= 3 squares, W-GEN), attempts/A85-k0-route/results/
cases85.json (per-case reach/depth tables; the four-case taxonomy JAM / BLOCK / WEDGE / OFFSET-UPRIGHT
= Trump's TL corner type), attempts/A87-drain-flow/notes/d1max87.md (locks in the corpus: flush kiss +
side pusher, 1-2 free squares per jam), attempts/A47-corner-majority/results/primitives_report.md (the
54-entry exact corner charge table; the near-flush zero cell; feasibility law: tilt > 40 deg cannot sit
within 0.7 of a wall), attempts/A85-k0-route/results/charge85.* when it lands (pair charges by case),
docs/known_results.md 16a.

## T1 — Lemma WALL (the 1-D budget)
For each wall w of a K0-BLOCKED packing at side m in [3.82, s-hat): enumerate what can touch w and with
what width along w: the two corner crowds' wall members (a slot-adjacent upright: width 1; a tilted
member: width cos t + sin t in (1, 1.414]; possibly none touching), a jam's on-wall pusher (width 1 if
upright; tilted pushers — say whether MENU allows them and what they cost), and free squares. With
per-wall <= 3 and total width + gaps <= m < 3.877, prove: (a) two jam corners cannot share a wall; (b) a
wall carrying a jam + on-wall pusher leaves the adjacent crowd's wall member at most 0.877 of gap
(state the exact inequality in the member's tilt), and if the crowd has no wall member on w, its
intrusion of its own slot must come from the perpendicular wall's side and its reach along w is bounded
by the pusher's far edge — quantify; (c) the maximum number of jam corners (with on-wall pushers)
in a K0-BLOCKED packing (expected <= 2, on opposite walls), and the free-square count they consume;
(d) the above-wall lock alternative (vertex presser at the jam square's outer top vertex): what wall
length it consumes (its own wall contact, if any) and whether it evades the budget — if it does, state
the residue precisely (the corpus never shows it). Canary: Trump (k3) has three slot corners and one
OFFSET-UPRIGHT corner (upright at offset 0.8445 flush on the left wall, partner at 40.18 deg touching
the top wall?) — check every wall of Trump against Lemma WALL's inequalities exactly (60-digit
certificate); the lemma must not exclude it and should show which of its walls are tight.

## T2 — the squeeze, composed with the corner charges
For the non-jam corners adjacent to a jam, derive the forced type and position bounds (near-corner
upright within x of the corner, or a wedge with tilt in a range) and look them up in A47's corner
table and in charge85's pair charges: the forced minimum charge per squeezed corner. Then the k0
composition: with j jam corners (j <= the T1 maximum) and 4 - j charged corners, the sum of corner
charges must be <= m^2 - 11 <= 4.0318; report for j = 0, 1, 2 whether the forced sum exceeds the
budget (dead by area), and if not, the offset cap: the largest offset g at which an OFFSET-UPRIGHT
corner can coexist with three non-simple, non-jam corners. This is A47's corner-majority composition
rerun with the zero cell denied by the wall budget — say exactly which cells remain available to the
adversary.

## T3 — verdict and consumers
If T1+T2 kill a set of the 21 four-corner patterns (cases85) or cap g, state the surviving patterns and
the census fraction they contain (cases85 has the box counts), and how the A85 tree / a corner-first
tree consumes the lemma (as (C) leaves: wall-touching counts and widths are exact box-level tests). If
the budget does not close, name the exact escape (above-wall locks; tilted pushers; crowds not touching
walls) and its measured frequency in the corpus.

Constraints: <= 2 processes total with the running chores (charge85, pin1crowd92); BLAS-pinned; headroom
> 6 GB; A57/A60/A61/A96 untouched; frozen verifiers untouched; writes in attempts/A97-wall-budget/,
docs/proofs/wall_budget.md, depgraph K0.RESN note (chip -> A97; pull/merge; no rebase/autostash/reset),
registry row, LOG.md. Report tersely: max jam count and the two-jams-per-wall verdict first, the
composition verdict (dead by area for which j / the offset cap) second, the escape list third, pointers.
