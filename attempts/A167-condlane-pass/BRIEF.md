# A167 — the CONDITIONAL chord-limited lane, POPULATION PASS (A161's queued levers)

Owner: Opus engineer. Started 2026-09-08. Attempt dir: `attempts/A167-condlane-pass/`.
Everything outside this directory is READ-ONLY except the three named fold-in appends.

## Context (restated from the assignment)

A161 (`attempts/A161-chord-lane/`, commits `27477e08` / `a491c1d0`; `code/chordlane.py`,
`code/condlane.py`, `code/checkcl.py`; `notes/leaf.md`) built

* the CHORD-LIMITED SLOT LANE — band squares are priced by the wall chord row
  (`beta = floor(s0 - SUM_j minchord(B_j, l))`), plus the `LANE_out` cover of the outside poses,
  plus `M`; and
* its CONDITIONAL form — split `H`'s box `B_H` into a complete binary subdivision, and per piece
  `b` take `n(b) = beta + LANE_out(b)` when the piece misses the cell, else
  `n(b) = min(beta, LANE_band(b)) + LANE_out(b) + 1`, with the two covers carrying the
  complementary exact prunes (`band` / `not_band`).

A161 certified 27 genuinely new kills (T3/T5) plus 13 more from the undecided pairs, and found that
the **GUARD-LINE OFFSET choice decides closure** (40,000 boxes at one offset vs 163 leaves at
another) while budget alone does not. **The population pass of the conditional form was never run**
(the cap was spent by T5/T6 and three T8 runs).

## Tasks

1. **Build the population FROM THE COLLECTOR, not a snapshot.** Run
   `docs/shadows/status_gallery.py --json` for the current dead set (44 sources) and take the ALIVE
   A57/A60 nodes' `NO-LINE` and `UNDECIDED` cells with `M = 1` out of A161's t3 tables
   (`results/t3.jsonl`, `results/t3_dedup.jsonl`), in A161's cost order: trump5 BR(0,1) (82 cells),
   k5_16 BL(1,0) (94), BR(1,0) (84), TL(1,0) (81), then the rest.
2. **Run the conditional leaf with A161's queued levers**: (i) rank the offsets for the BAND cover
   by the sampled `band_free` count under `K'(piece)`; (ii) split `B_H` shallowly with a per-piece
   line; (iii) restrict the band cover's root to the slab `|v| <= 1/2`. 60 s per cell, top-6
   offsets; certificates (`chord_limited_lane_v1` / its conditional kind), `checkcl.py` 100 %,
   sample line per kill (drawn -> meeting -> band/outside -> free). **`c0_Y0169 TL(0,0)` first**
   (A161 certified `LANE_out = 0` there; the band cover is what remained open).
3. **Table by class/slot**: kills, no-go by exact witness (retired), still undecided; overlap with
   the collector's dead set (distinct NEW nodes ONLY); fold-in lines (`A57/PAUSED.md` v4 addendum,
   A60 ledger) and one sentence in `docs/residue_ledger.md` section 1, all with collector-checked
   counts.

## Rules (as given)

Pure geometry. `<= 2` processes at BelowNormal with affinity `0xFFFF`; box ceiling 16 lab processes
(count; wait). Cap 4 CPU-h. Read-only on every campaign and prior attempt (new files only under
this attempt, plus the named appends). No recursive deletes. `PYTHONDONTWRITEBYTECODE=1`.
git = fetch + plain merge + `git commit -- <pathspecs>` only. Registry row and LOG entry.
Report ONCE.
