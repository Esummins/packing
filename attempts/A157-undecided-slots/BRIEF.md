# A157 — the UNDECIDED usable-slot cells of A141's A57/A60 sweep

## The brief (restated)

A141's slot-lane sweep over the alive A57/A60 population
(`attempts/A141-polycore-lane/results/t2_a5760_s{0,1}.jsonl`, produced by `code/t2_a5760.py`
via `polylane.lane_corner_generic`) left **1 655 (node, slot) cells UNDECIDED**. A sub-population
of those carries `lane_lb = 0` — the 8 000-pose sample found **no free pose meeting the slot cell
at all** — together with a certified `M <= 1`. Those are *probable kills*: `LANE_K'(p) = 0` with
`M(p) <= 1` means the usable slot `p` is met by at most one square of the family, which
contradicts Lemma SLOT-CROWD (>= 2 non-pin meeters), i.e. the single meeter snaps into the exact
slot and the packing lands in the certified-dead k6 extension class.

The PI's example: `c0_Y0076` (A60 trump5, level 1, alive) — `TL(0,0)` UNDECIDED `lane_lb 0 M 1`
and `BL(0,2)` UNDECIDED `lane_lb 0 M 1`. The PI reads `TL(0,0)` as singly met because the
hypothesis square's corners sit outside the unit corner and a second meeter would have to be a
corner intrusion that does not fit.

### Tasks

1. Enumerate every **alive**-node cell in the two sweep files with `verdict = UNDECIDED`,
   `lane_lb = 0`, `M <= 1`. Report the count by class and by slot (recompute; do not take the
   coordinator's quick count).
2. Run **A141's certifying cover** — the same machinery, the same exact pin cores and `K'(H)`,
   with `M` certified exactly by the interval test — on each, `c0_Y0076`'s `TL(0,0)` and
   `BL(0,2)` first. Emit `polycore_slot_lane_v1` certificates for every `LANE_K' = 0, M <= 1`
   outcome, checker 100 % pass, one sample line per kill (drawn -> meeting -> free). Report the
   kill count by class / level / slot, the near-misses (LANE 1, M 1), and the cells where the
   cover could not close (depth reached, open leaves).
3. Fold-in: `attempts/A157-undecided-slots/results/slot_kills157.jsonl` in A141's
   `polycore_lane_kills.jsonl` format (a NEW file under this attempt — appending to A141's own
   ledger is **not** allowed); one paragraph each appended to
   `attempts/A57-shadow-trees/PAUSED.md` and `attempts/A60-trump5-campaign/notes/ledger.md`,
   marked "exact-pin form, class-S composition, A118-O1 stands"; one sentence in
   `docs/residue_ledger.md` section 1.

### Rules

Pure geometry. <= 2 processes, affinity `0xFFFF`, BelowNormal, cap 3 CPU-h. <= 16 lab python
processes on the box (counted first: A149 4, A156 2, A136 2, A137 5, A154 1 = 14; A157 adds 2 =
16). READ-ONLY on every campaign and every prior attempt — new files only under this attempt plus
the three named appends. No recursive deletes. `PYTHONDONTWRITEBYTECODE=1`. Git = fetch + plain
merge + `git commit -- <pathspecs>` only. Registry row and LOG entry.

## Soundness (unchanged from A141 / A118)

* The leaf is A118 §1 / A141 §8.1 verbatim: `LANE_K'(p) + M(p) <= 1` at a USABLE slot contradicts
  SLOT-CROWD, so the node is dead. Pins are obstacles only and are never counted in `M`.
* The composition is the class-S one of `attempts/A118-lane-count/notes/method.md` §2.
* **Caveat A118-O1 stands**: a LANE kill excludes class-`S` packings with EXACT pins, not the
  `delta = 10^-2` slack family. The A152 caveats stand: exact-pin form only.

## What A141 actually did on these cells (a correction found here)

The sweep did **not** skip the covers on the UNDECIDED population — `skipped_covers` is set only
on the `LANE>=2` / `NEAR-MISS-OR-WORSE` rows (4 750 + 1 790). Every UNDECIDED row carries
`M_exact = true`, i.e. the `M` covers ran and closed. What failed is the **LANE** cover: with
`t2_a5760.py`'s budget (`--maxopen 1200`, `lane_depth0 = 20`, `rounds = 8`) `lane_cover` returned
`lane = None` with `reason = "open budget exhausted"` (which also zeroes the reported
`cover_open`, hence the misleading `cover_open = 0` on 188 of the 196 target rows). A157's job is
therefore purely a **budget** job: re-run the identical cover with a much larger `max_open` and a
deeper `depth0`, and certify what closes.
