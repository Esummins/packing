# A152 — the slot-lane leaf with a tolerance-shrunk / translated slot cell

## The brief (restated)

A141's slot-lane leaf (`attempts/A141-polycore-lane/`, `notes/method.md` §8.1, `code/t2_a5760.py`,
`code/t4_slots.py`, `code/check141.py`; 188 A57 + 56 A60 kills) counts a square as **MEETING** a
usable slot cell if its square intersects the unit cell **at all**.

On `k5_16_interior_Y1117` (the H box `x, y ∈ [2.3578, 2.4976]`, tilt `28.07°–41.11°`; pins =
corners4 + BL(0,1)) the PI reads `BR(0,1)` as **singly met**, while A141 returns `LANE ≥ 2`
because a second free square merely **GRAZES** the cell: the coordinator's sampled pair is
`A = (3.157, 1.732, 22.1°)` inside the slot (depth 0.853) and `B = (2.183, 0.934, 54.7°)` whose
corner enters the cell by 0.003; the two are interior-disjoint (gap 0.024) and both avoid the
exact pin cores and some pose of H.

**The proposed refinement.** The snap (SLOT-CROWD / usable-slot teleport, `docs/proofs/` and the
A94/A118 notes) only needs *some* admissible placement of the extension class's sixth simple
square to be free of all other squares, and that class allows its pins within the pin tolerance
`δ` of the slot (A57's G1 tree: `δ = 10⁻²`). So a square that meets the cell but misses the cell
**SHRUNK by the tolerance** (the slot's "core", the analogue of the exact pin core) does not block
the snap and must not count as a meeter.

## Tasks

1. **SOUNDNESS.** State the refined leaf exactly (meeter := intersects the tolerance-shrunk cell;
   the snapped square is placed at the admissible translate the grazers leave free — prove that
   such a translate exists whenever every other square misses the shrunk cell: the set of blocked
   translates is the union of the `(Q_i − cell)` intersections; give the argument and its Lean
   shape). **Check the prerequisite A118-O1 names**: are the k6 extension classes (k5_11:
   k6_18/20/23; k5_16: k6_23/27/28/29/30; trump5: k6_07/19/21–24) certified dead on the closed
   window **with the sixth pin allowed the same slack tolerance** (the slack-pin family), or only
   with exact pins? Read A56/A61/A114's certificate objects and Lemma B′ (A118 `notes/method.md`
   §2, A57 `notes/lemmas.md` T23) and answer precisely; if only exact pins, say what
   re-certification the slack form needs and price it (do the parametric certificates carry pin
   boxes?).

2. **RE-RUN** the slot-lane test with the shrunk cell over the current alive A57 population
   (A137's `PAUSED.md` v3 state, 406 work-owing; skip nodes already dead) and A60's alive nodes:
   Y1117 first, then all. Certificates in A141's format extended with the shrink (new kind
   `polycore_slot_lane_shrunk_v1`), checker extended, sample line per kill (drawn → meeting the
   shrunk cell → free), overlap with A141's kills, table by class / level / slot. Pure geometry,
   ≤ 2 BelowNormal processes, cap 3 CPU-h.

3. **FOLD-IN** lines (A137 `PAUSED.md` v3 addendum, A60 ledger) marked *"conditional on the
   slack-form extension kill"* if (1) finds the prerequisite unmet; one paragraph for
   `docs/residue_ledger.md` §1.

## Rules

Read-only on every campaign and prior attempt (new files only under this attempt plus the named
appends), no LP, no recursive deletes, `PYTHONDONTWRITEBYTECODE=1`, ≤ 16 python processes
(A149/A150/A151 run 2 each), git = fetch + plain merge + `git commit -- <pathspecs>` only.

## Layout

```
notes/soundness.md   task (1): the refined leaf, the counterexample, the sound repair, Lean shape
notes/prereq.md      task (1): the A118-O1 prerequisite, measured on the certificate objects
notes/results.md     task (2): Y1117, the sweep, the tables
code/lane152.py      the module: slack pin boxes, admissible translates, the three cell variants
code/t1_y1117.py     the focused study of k5_16_interior_Y1117 BR(0,1)
code/t2_sweep.py     the population sweep (resumable, sharded, budgeted)
code/check152.py     the checker for `polycore_slot_lane_shrunk_v1`
```
