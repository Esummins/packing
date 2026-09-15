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

(filled in from `results/experiment221*.jsonl`; the `--profile` block is at the end of `logs/exp221_Y0402.log`)

<!--LANE_ALONE-->

## 4. Conclusion taken into the design

* the blocker is **not** the kernel (A213/A214 are active), **not** the bisection (3.7-9.3 s, exhausts) and **not**
  `lane_max_open` -- it is the lane's **root**: the meeting window instead of the pocket;
* the node's question at `m = 1` is *"is there a free centre in this pocket?"*, which the lane over-answers with
  *"does any free square meet this pocket?"*;
* so A221 replaces the lane on the pocket with the exact clip **rooted at the pocket** (Lemma POCKET-DEAD,
  `notes/lane221.md`), depth-first so the memory is the stack and the depth is not capped by a frontier;
* and, because every branch rule only shrinks a role's pose set, a child can run that cover on its **parent's**
  pockets without bisecting the container at all (Lemma POCKET-INHERIT).

The after-numbers are in `results/bench221.md`.
