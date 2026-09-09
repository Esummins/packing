# A171 — the MULTI-BOX INVARIANT: clipping as CODE, not as an instruction (Opus)

**Context.** Two agents in a row built multi-box case trees on the k0 cell `l1_104` and drew/solved
boxes that were not clipped:

* **A165 (Opus)** — its C2 panel drew the two TR meeter boxes as unclipped pose unions overlapping
  `H`'s core, which loses the whole forcing.
* **A168 (Fable)** — its S2 nodes carry boxes whose pose unions escape the container (a `s − 1/2`
  container bound applied to a box with a non-degenerate tilt bin) and whose poses meet another
  box's certified core.

The PI caught both by eye. **The clipping rule must become CODE that every multi-box construction
calls, not an instruction in a brief.**

**Deliverable.** A small pure-geometry library
`attempts/A171-multibox-invariant/code/multibox.py` that imports (read-only)

| import | from | what it gives |
|---|---|---|
| `pinclip.py` | A131 | per-tilt-sub-bin clip of a centre box against an obstacle (exact rational octagon predicate, bisection + exact certification) |
| `polycore.py` | A132 | `K'(B)` with exact rational vertex certification |
| `exactcore.py` | A135 | the exact maximal axis core of a box |
| `chordlane.py` | A161 | `box_misses_cell_exact`, exact `cs_max/cs_min`, the lane cover |
| `guardline.py` | A144 | `minchord_box`, `Line` (for `chord_rows`) |
| `polylane.py` | A141 | `build_cond`, `centre_window`, the lane cover machinery |

**API**

* `Node(boxes: dict name -> Box(x0,x1,y0,y1,th0,th1 or t-interval))`
* `node.normalise(s, nsub=4, max_iter=10)` — container clip of every box (all poses inside
  `[0,s]^2`, per tilt sub-bin) then mutual clip of every box against every other box's `K'` to a
  fixed point, recomputing `K'` and the exact axis core after each pass; returns the clipped Node
  with per-box kept fractions and clip traces, or raises `EmptyBox(name)` when a box loses every
  pose (the case is dead by the pair leaf).
* `node.assert_invariant()` — exact checks that every `K'` lies inside the container and every pair
  of `K'` is interior-disjoint (rational SAT), raising otherwise.
* `node.figure(path, s, extras)` — A148-style panel: container, every `K'` solid, pose unions as
  thin outlines, names, kept fractions, the invariant's result printed on the page.
* `node.chord_rows(lines)` — A144's guard-line chord row over the node's boxes (minchord per box).
* `node.lane(cell, ...)` — A141's lane cover with A161's exact miss test, restricted to the node's
  cores.

**Tests** (`tests/test_multibox.py`, all under 2 minutes):

  (a) two boxes whose `K'` overlap → mutual clip shrinks or empties them; invariant passes after.
  (b) a box straddling the container edge → container clip removes the outside poses.
  (c) A168's failing S2 node (`attempts/A168-cascade-fable/results/`, node `BR139/TRH-25`:
      `H`, `B1`, `D` as recorded) reproduced: before `normalise` the invariant FAILS (D outside the
      container, D and B1 meeting H); after `normalise` it PASSES, with kept fractions reported.
  (d) random nodes of 2–6 boxes: 10^4 sampled poses after `normalise` never violate.

**Also**: `notes/usage.md` (five lines: how a cascade/sub-tree must call it before any row, cover,
figure or LP); one line appended to `attempts/A57-shadow-trees/PAUSED.md` v4's resume block; one
line appended to `docs/residue_ledger.md` §6; registry row and LOG entry.

**Rules.** No LP. ≤ 2 processes at BelowNormal with affinity 0xFFFF. Read-only on every campaign and
prior attempt (new files only under this attempt, plus the two appends). No recursive deletes.
`PYTHONDONTWRITEBYTECODE=1`. Git = fetch + plain merge + `git commit -- <pathspecs>` only.
