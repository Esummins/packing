# A121 — how the readings are checked, mapped and priced

Read-only on every campaign and attempt except `attempts/A121-reading-validator/**` (plus the
registry row and `LOG.md`).  One process, BLAS pinned to one thread (`blas1` imported before
numpy in both entry points), `PYTHONDONTWRITEBYTECODE=1`, pure geometry: **no LP, no solver, no
sampler of my own** — the only lane verdicts used are A118's frozen ones.

## 0. What is read

| what | from |
|---|---|
| readings | `docs/shadows/review.csv`, column `PI_reading` |
| the minimised packing (right panel) | `A107/results/shadows_k0.json` (`slots`, `free`, `s`), `shadows.json` for Part I |
| the nodes an entry explains | `A107/results/shadow_nodes_k0.json`, `shadow_nodes.json` |
| the map back to a node's frame | `A107/results/extract_k0.json` (`struct_op`), `extract.json` |
| the lane test | `A118/results/lane_s0.jsonl`, `lane_s1.jsonl` (verdict, `lane_ub`, `ncond_pot` = M) |
| the usable cells + extension classes | `A118/code/corpus.py` `CLASSES` |
| geometry primitives | `A118/code/lanelib.py` (`frame`, `cell_centre`, `mu_many`, `gap_pose_vs_core`, `cont_frames`) |
| the `i` queue | `A115/results/t4/*.json`, `t4_summary.json` |
| already-booked kills | `A118/results/report118.json` (`kills`) |

## 1. The minimised packing, reconstructed

Slot squares sit at their cell centres with tilt 0 (`minimise.py` fixes them as affine functions
of `s`); free squares are `free[k]` as `f0..fn`.  A cell name `BL(i,j)` is `[i,i+1]x[j,j+1]`
measured from its corner (`lanelib.frame`), so a cell is the same object at every side.

* **meets the OPEN cell**: SAT gap to the unit cell `< -1e-7`.
* **grazes**: `|gap| <= 1e-7` — A107's own contact threshold.  Grazers are reported but are NOT
  meeters; this is the difference between a room reading and a crowd reading in six of the rows.
* **depth**: `d = max(0, 1 - mu_p)` (`slot_crowds.md` §1.3).  `mu_p` is the SLOT depth only where
  Lemma CONT holds (Q misses `R_p`), so each meeter carries a `cont` flag and the report quotes
  the SAT penetration `-gap` alongside; Lemma SHELL's `(1+sqrt2)eps` bound is quoted only at a
  corner cell, since k0_00 has no pins and CONT is unavailable at a non-corner cell.
* **near-snapped**: L-inf distance of the pose centre to the cell centre and the tilt mod 90
  (folded to the nearest axis), against A107's own snap window `0.05 / 3 deg`.

## 2. The frame map (canary C1)

`extract.py` stores `struct_op` = the D4 element `f` applied to the NODE's `cfg` to reach the
canonical structure the shadow was minimised in.  So

    shadow frame  =  f(node frame),        node cell  =  f^{-1}(shadow cell).

D4 acts on cell NAMES combinatorially (`r90`: `BL(i,j) -> BR(j,i)`, …), independently of the
side.  **C1** re-derives this on all 161 K-entry nodes: applying `f` to the node's `cfg` and
re-running A107's snap-based split reproduces the node's stored canonical `struct` — 161/161, no
mismatches.  **C2** checks `cell_map` is a D4 action on names and permutes the four corner cells.
**C3** checks the entry's drawn packing is its primary structure's (max-`nnodes`) minimum.
**C4** reproduces every contact A107 books for the K entries with this module's SAT gap:
235 contacts, max |difference| **0.0**.

## 3. Reading -> cut

| reading | cut in the node's frame |
|---|---|
| `r` / `ns` at a CORNER cell, k0_00 | **(a)** K0-FREE teleport into a corner cell -> `k1_00` (OPEN: every k0 verdict is conditional on `k1_00`'s tree, `k0_route.md` §3) |
| `r` / `ns` at a usable slot of a pinned class | **(b)** SLOT-CROWD teleport, extension named from `corpus.CLASSES` |
| `ns` with `*` | **(c)** SNAP of the node's own hypothesis square (none in this batch) |
| `i` | **(d)** A115 warm re-solve status |
| any other cell of k0_00 | **none** — k0_00 has no pins, so only the four corner cells have an extension class at all; a teleport/SNAP into `BL(1,0)`, `BL(1,1)`, `BR(0,1)`, `TR(0,1)`, `TR(1,0)`, `BR(1,0)`, `TL(1,0)`, `BL(0,2)` is licensed by no lemma |

The cut becomes a **node kill** exactly when A118's leaf fires at the mapped cell:
`LANE(C) + M(C) <= 1`, i.e. `lane_ub + ncond_pot <= 1` in the lane record.  Verdicts are read,
never recomputed — same corner frame, same `a_w = 1`, same `rho = 0`.

## 4. Incremental

`results/state.json` holds `sha1(PI_reading)` per row.  A bare run processes only the rows whose
reading text changed; `--since <commit>` diffs the CSV cell against `git show <commit>:...`
instead; `--all` and `--only K01,K02` force.  `readings.jsonl` and `cuts.jsonl` are merged by
entry id, so re-processing one row rewrites only that row's records.

## 5. What A121 does NOT claim

* The shadow is not inside the node's box (A106: 0 of 62 landed boxes contain a shadow).  A
  reading is therefore a **pointer to a cell**, never a fact about every configuration of the
  node; the lane test is what turns it into a statement about the node.
* The drawn packing is the entry's PRIMARY structure's minimum.  Nodes of an entry's secondary
  structures share only the value `s*`; `cuts.jsonl` carries `in_primary_struct` per node.
* Every k0 kill is conditional on `k1_00` (A118-O2).

## 6. Batch 2: the pinned classes (S rows)

An S entry's nodes do not share a class (S01 spans k5_11, k5_16, trump5, four A61 stragglers and
two k6 classes), and usability is a property of the cell **in the node's own frame**, where the
class pins live.  So the cut kind is decided per NODE, not per entry:

1. `node_class(nd)` = A118's own `cls` where it has a lane record; else the nid prefix (A61's
   window stragglers are named by their class, `.stageA` being a run stage, not a class); else
   the campaign default.
2. the cell is mapped to the node frame through `struct_op^{-1}` FIRST, and only then tested
   against that class's usable set (`corpus.CLASSES`, A118 `notes/method.md` §3).
3. a class with no usable-slot table (k5_05, k5_10, k5_12, k5_17, k6_20, k6_21, k6_29 - A61's
   stragglers) yields `cut_kind = none`: no certified extension, so no teleport lemma.

The table used is A118's own `corpus.CLASSES`, which for **k5_16 has six usable cells including
`BL(1,0)` (extension k6_23)**; a five-cell version of that list omitting `BL(1,0)` is in
circulation.  Sensitivity: 50 cut rows depend on `BL(1,0)` being usable and **none of them is a
node kill**, so nothing in this report turns on the discrepancy.

Two more shorthand tokens are handled: `g` swallows the REST of the string (a grain description
is prose and may contain `;`), and `-` is an explicit "no reading of this kind" that yields no
cut and no flag.  A `g` row now also carries the entry's tilt clusters (0.5 deg linkage) and its
flush-on-wall lists, so a description that names no squares ("a common-tilt grain", "4 stacked on
the left") can still be checked; and for S02/S07 it carries A116's stability radii.

Two thresholds were re-set on batch-2 evidence: the Fritz-John closure test is `kkt_residual >
1e-3` (1e-6 flagged nnls noise - S07 1.3e-4 at full rank 7 of 7), and the "flush" verdict uses
A101's own 0.01.

**A merge bug found and fixed here:** `merge()` derived the set of entries to replace from the
NEW rows, so an entry whose cuts fell to zero (S11's `-`) kept its stale rows forever.  The
touched set is now `todo` - the entries actually re-processed.

## 7. Batch 3: `st4`, `fl`, the `-` scan, cross-entry claims, and panel provenance

**`st4`.** Four axis-aligned unit squares flush against ONE wall all span that wall's unit strip,
so they are pairwise disjoint in the perpendicular coordinate, each occupies a unit interval of
it, and the side is `>= 4`. The four need not be consecutive: S50's top square sits `2.7e-5`
above the third, which is exactly `s* - 4`. `wall_stacks()` therefore COUNTS flush axis-aligned
squares per wall rather than looking for a run of unit steps. The cut is a NODE cut only when
every one of the four is a PIN of the node's class or one of its CONDITIONED squares (then the
node's own hypothesis forces `side >= 4 > s0` and the node is dead); otherwise the stack kills
the drawn CONFIGURATION and says nothing about the node.

**`fl <sq> <cell>`.** Flush-along-wall: the square shares ONE coordinate with the cell centre
(residual `<= 0.01`, A101's threshold) and is displaced along that wall. It is NOT a snap
candidate -- Lemma SNAP-D needs the square inside the cell's eta-ball -- so the only cut it can
carry is the ROOM condition on the cell.

**The `-` rows** are answered by `usable_scan()`: for every node, every USABLE cell of its class
(named in the NODE's frame) is pulled into the shadow frame through `struct_op` and its occupancy
read off the drawn packing. SLOT-CROWD / K0-FREE demand `>= 2` NON-PIN squares in the open cell,
so a usable cell met by `<= 1` non-pin square is a candidate cut the reading did not have to
name; A118's lane verdict at that cell is what converts it. Pins are identified by mapping the
class's census pin slots into the shadow frame (`pin_cells`).

**Cross-entry claims.** A `g` description naming another entry (`S07-type`, `same minimum as
S33`, `same as S05`) is a checkable claim: `compare_packings` aligns the two minimised packings
over the full D4 with a Hungarian matching on centre + tilt. `same` in the text makes it an
IDENTITY claim (a failure is a `?`); anything else is a family claim and only gets the
measurement. Where **A122** has re-minimised both with all eleven squares free, A122's pairwise
numbers are the authority on whether two entries are the same MINIMUM, and the gallery landings
can still differ -- that distinction is what settles S34.

**Panel provenance (`seed_distance`).** Each entry's drawn minimum is matched over D4 against the
snapped dual support of the primary structure's own seed node -- the packing the minimiser was
started from. `snap` = max centre move `<= 0.05` AND max tilt move `<= 3 deg`; `tilt-only` =
positions held, tilts moved; `rearrangement` = some square moved more than 0.05.

**The meet/graze boundary moved to 1e-6.** At 1e-7, S44's `f0` (SAT gap `-1.24e-7`, corner-frame
depth `9.2e-8`) counted as a second meeter and made a correct `r` reading look like a crowd. Over
all 83 entries only 4 meeters sit between 1e-7 and 1e-4 and every one is a converged tangency, so
the boundary is drawn at 1e-6 -- five orders below the LP pitch 0.192. Grazers are never silently
dropped: every one is listed against its cell.

**Cross-check against A107 gallery v2.** The v2 re-render adopted A121's slot/free finding and
reports "47 such squares in 33 entries" at its own thresholds (1e-3 in position, 0.05 deg in
tilt). This module reproduces exactly **47 in 33** at those thresholds, and **41 in 29** at its
own stricter (1e-5, 1e-3 deg). A107's results JSONs are unchanged by v2, so the audit still
reports against the stored splits.
