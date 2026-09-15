# A221 step 1 -- where the no-room 120 s actually goes (measured before any design)

Harness `code/exp221.py` (+ `code/nodeload221.py`, which rebuilds a recorded no-room node from a certificate: the
node record's `roles` field carries only the NON-pin roles, the five pins come from the node's `snapshot`, and the
merge is exactly the `pg.roles` dict `tree209.noroom_at` hands to A189).  One detached BelowNormal python per page,
affinity 0xFFFF, `PYTHONDONTWRITEBYTECODE=1`.  A213 integer core + A214 C kernel **installed and active** on every
run below (`{"installed": true, "flag": true, "flag_clip": true, "ckernel": true}` -- so the kernels are already
under the lane's exact tests; they are not the missing lever).

Raw records: `results/experiment221.jsonl`, `results/experiment221_Y0738.jsonl`; logs in `logs/`.

## 1. The 120 s cap, split by phase

The recorded run is reproduced exactly (same verdict, same pockets, same order of magnitude in seconds).

| node | k | m | build s | bisect s | bisect stop | open pieces | pockets | **lane s** | verdict |
|---|---|---|---|---|---|---|---|---|---|
| Y0402 zero_page R.2.1 | 10 | 1 | 3.0 | 9.3 | exhausted | 10272 | 2 | **109.1** | UNDECIDED |
| Y0738 zero_page R.1.1.3.3 | 10 | 1 | 3.0 | 3.7 | exhausted | 2368 | 1 | **114.8** | UNDECIDED |

`bisect stop = exhausted` means A189's bisection stopped at its OWN depth cap (13), not at the deadline: the
bisection is cheap and finishes.  **91 % and 96 % of the cap is the lane, and the lane returns `None`.**

## 2. Why the lane cannot finish -- it is answering a bigger question

`chordlane.lane_out(cell, ...)` roots its cover at `polylane.centre_window(cell, s)`: the centres of unit squares
**meeting** `int(cell)`, i.e. the pocket grown by `1/sqrt(2)` on every side.

| node | pocket | pocket area | lane root (meeting window) | root area | blow-up |
|---|---|---|---|---|---|
| Y0402 R.2.1 | `[1.4375, 2.0917] x [3.1396, 3.4396]` | 0.196 | `[0.730, 2.799] x [2.432, 3.377]` | 1.954 | **10x** |
| Y0402 R.2.1 | `[3.2571, 3.4396] x [1.5013, 1.8972]` | 0.072 | `[2.550, 3.377] x [0.794, 2.604]` | 1.497 | **21x** |
| Y0738 R.1.1.3.3 | `[2.4435, 2.8794] x [2.2066, 2.6488]` | 0.193 | `[1.736, 3.377] x [1.499, 3.356]` | 3.046 | **16x** |

The node's roles are what created the pocket; the collar the lane must additionally discharge is 10-21x the pocket
and sits away from those roles, so no budget setting reaches `LANE = 0` there.  See s.3.

## 3. The lane ALONE on the recorded pockets, 600 s and `lane_max_open = 1e6`

Budget: `deadline = 600 s`, `lane_max_open = 1e6`, `lane_depth = 48` -- 5x the time and 10x the open budget of the
node's whole cap.  (`n_open = 0` in the table is A161's `PAIR_CAP = 4000` short-circuit: the cover gave up with more
than 4000 undischarged boxes and reports none of them.)

| node | pocket | lane | s | depth | leaves discharged (by test) |
|---|---|---|---|---|---|
| Y0402 R.2.1 | `[1.4375, 2.0917] x [3.1398, 3.4396]` | **None** | 604 | 48 | 2947: witness 2251, container 694, misses_cell 2 |
| Y0402 R.2.1 | `[3.2575, 3.4396] x [1.5013, 1.8427]` | **0** | **160** | 34 | 12033: witness 6208, container 5783, misses_cell 42 |
| Y0738 R.1.1.3.3 | `[2.4433, 2.8773] x [2.2065, 2.6479]` | **None** | 601 | 48 | 1526: witness 1526 |

Two facts, and they are the whole design:

1. **the lane never reaches 0 on the pockets that matter**: 600 s and a 10x open budget change nothing on two of the
   three pockets.  The reason is not budget -- see s.3b;
2. **on the pocket it CAN discharge it needs 160 s**, i.e. more than the node's entire 120 s cap.  A221's pocket
   cover kills that same pocket in **0.0 s** (`results/bench221.jsonl`, tag `four`: `dropped_fraction = 1.0` at
   depth 1).

### 3a. `cProfile` of a 120 s lane run (Y0402 R.2.1, pocket 1; full block at the end of `logs/exp221_Y0402.log`)

```
  1200680   20.913 tottime  polylane.py:135(_gmax)
   300170   13.589          polylane.py:147(point_margin_many)
   345680    3.275          numpy.asarray
    45390    2.951 (cum 44.4)  polylane.py:161(best_shared_point)
   254810    2.800          numpy linspace
   254660    2.438          numpy _broadcast_to
   127330    1.102          numpy meshgrid
   820179    0.844          fractions.Fraction.__new__
```

**~98 % of the lane is the float WITNESS SEARCH** -- `best_shared_point`'s 7-round 9x9 grid refinement and the
`point_margin_many` / `_gmax` it calls -- not the exact rational tests.  So A213's integer core and A214's C kernel,
both active, are irrelevant here (`Fraction.__new__` is 0.8 s of 45 s), and routing "the lane's exact tests" through
them would buy nothing.  This is what ruled that lever out.

### 3b. Is the surviving pocket a budget limit or the truth?  (the deep probe, tag `deep`)

Y0402 R.2.1 pocket 1 through A221's own cover at `pk_depth = 48`, `pk_max_open = 4e5`, 245 s:

| | dropped fraction of the pocket's (centre x tilt) volume | open pieces | depth |
|---|---|---|---|
| pocket 1 `[1.4375, 2.0917] x [3.1398, 3.4396]` | **0.119** | 196504 | 48 |
| pocket 2 `[3.2575, 3.4396] x [1.5013, 1.8427]` | **1.000** | 0 | 1 |

**88 % of pocket 1 is still open after 48 halvings**: the pocket genuinely holds free poses, so NO no-room leaf --
A189's lane, A221's cover, or anything else -- can ever kill R.2.1.  A189 was spending 109 s of its 120 s cap on a
question with no favourable answer, and paying 160 s for the one pocket that does die.  The right measure of A221 on
such a node is therefore *how fast it returns the same UNDECIDED, and how tight a residue it hands back* -- and on
the nodes where every pocket IS dead, whether it kills them (s. `results/bench221.md`).

## 4. Conclusion taken into the design

* the blocker is **not** the kernel (A213/A214 are active and the lane is 98 % float witness search), **not** the
  bisection (3.7-9.3 s, exhausts) and **not** `lane_max_open` (600 s / 1e6 changes nothing) -- it is the lane's
  **root**: the meeting window instead of the pocket, and the float witness search over it;
* the node's question at `m = 1` is *"is there a free centre in this pocket?"*, which the lane over-answers with
  *"does any free square meet this pocket?"*;
* so A221 replaces the lane on the pocket with the exact clip **rooted at the pocket** (Lemma POCKET-DEAD,
  `notes/lane221.md`), depth-first so the memory is the stack and the depth is not capped by a frontier;
* and, because every branch rule only shrinks a role's pose set, a child can run that cover on its **parent's**
  pockets without bisecting the container at all (Lemma POCKET-INHERIT).

The after-numbers are in `results/bench221.md`.
