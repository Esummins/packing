# A161 — the CHORD-LIMITED LANE: one band square by chord sum, nothing outside the band reaches the slot

Owner: Opus engineer. Started 2026-09-08. Attempt dir: `attempts/A161-chord-lane/`.
Everything outside this directory is READ-ONLY except the three named fold-in appends.

## Context (restated from the assignment)

The PI reads `docs/shadows/a57v4/k5_16_interior_Y0842.svg` (k5_16: pins = corners4 + BL(0,1);
recorded ALIVE at LP, `tau` exactly 5 / budget 5; A141's lane pass returned BL(1,0) UNDECIDED with
`lane_lb = 1`, `M = 1`; A144's offline sweep found max guard-line violation 0.1016) and says:

> "you can only put one core in the bottom slot by chord sum, and no cores outside that slot can
> reach BL(1,0)."

That sentence is the conjunction of two already-proved pieces:

* **A144's guard-line lemma** (`attempts/A144-guard-lines/notes/spec.md`, `code/guardline.py`):
  LINE-1 — the chords of an interior-disjoint family of unit squares on an axis-parallel line inside
  `[0,s]^2` sum to at most `s`; LINE-2 — the hypothesis squares' chords come off the right-hand side
  via `minchord(B, l)`, the exact five-point minimum of the chord over a parameter box (pins, whose
  tilt bin has zero width, contribute an *exact* chord of 1 whenever the line runs inside their core's
  height range).
* **A141's lane leaf** (`attempts/A141-polycore-lane/`, `code/polylane.py`, `t4_slots.py`,
  `check141.py`): at a USABLE slot cell `C` of a pinned class, SLOT-CROWD forces `>= 2` NON-PIN
  squares to meet `int C`; so `LANE_K'(C) + M(C) <= 1` is a contradiction and the node is DEAD (the
  meeter snaps into the exact slot and the packing lands in a certified-dead k6 extension class).
  Exact-pin form; A118-O1 stands. A159's C8 guard: one exact two-crowd witness retires a cell.

## The leaf this attempt states and runs

**CHORD-LIMITED LANE.** Partition the poses that meet the wall-adjacent slot cell `C` by their chord
on the *wall guard line* `l` (`y = y_L` for a bottom-row cell, `x = x_L` for a left-column cell):

* BAND poses — chord on `l` is `>= 1` (the square crosses `l` through two *opposite* sides);
* OUTSIDE poses — chord on `l` is `< 1`.

The chord row on `l` charges every band square a full unit against the budget
`rhs(l) = s - SUM_j minchord(B_j, l)` left after the hypothesis squares (the two wall-row pins give
1 each; `H` gives its own `minchord` if its box crosses `l`). Hence

    #band <= floor(rhs(l))  =:  beta ,

and the meeters of `C` are at most `beta + LANE_out + M`, where `LANE_out` is a certified upper bound
on the number of pairwise interior-disjoint FREE squares whose pose is an OUTSIDE pose meeting `C` and
avoiding every hypothesis core, and `M` counts the conditioned squares that can reach `C`.
`beta + LANE_out + M <= 1` contradicts SLOT-CROWD: the node is DEAD.

The PI's sentence is exactly `beta = 1`, `LANE_out = 0`, `M = 0`, total `1 <= 1`.

## Tasks

1. The leaf stated exactly with its soundness argument (chord lemma + lane cover + SLOT-CROWD); the
   certificate format (guard line + `minchord(H)` + the outside-lane cover + witness points); an
   independent checker extending `check141`/A144's; the Lean shape (`chord_sum_le_side` +
   `minchord_of_box` from A144's spec, the lane leaf from A141/A135, one new glue obligation).
2. `k5_16_interior_Y0842` first: `y_L`, `y_b`, the chord budget, `LANE(outside)`, `M`, verdict,
   certificate, sample line (`>= 10^4` outside poses meeting `C`, none free; `>= 10^4` band poses,
   chord `>= 1` on `y_L`).
3. Every alive A57/A60 node with a wall-adjacent usable slot — BL(1,0), BR(1,0), TL(1,0), TR(1,0),
   BL(0,1), BR(0,1), TR(0,1), TL(0,0), BL(0,2), each with its wall line and band — whose A141 verdict
   is UNDECIDED or NEAR-MISS with `lane_lb <= 1`: screen with A159's two-crowd witness rule first,
   then the chord-limited lane. Table by class/slot/level, kills with certificates, overlap with
   A141/A142/A131's kills (distinct new nodes).

## Rules (as given)

Pure geometry, no LP. `<= 2` processes at BelowNormal with affinity `0xFFFF`; box ceiling 16 lab
processes (A149/A156/A136/A137 were running at 16 when this started — counted and waited). Cap 3
CPU-h. Read-only on every campaign and prior attempt; new files only under this attempt, plus
fold-in appends to `attempts/A57-shadow-trees/PAUSED.md`, `attempts/A60-trump5-campaign/notes/ledger.md`
and one sentence in `docs/residue_ledger.md` section 1. No recursive deletes.
`PYTHONDONTWRITEBYTECODE=1`. git = fetch + plain merge + `git commit -- <pathspecs>` only. Registry
row and LOG entry. Report ONCE.
