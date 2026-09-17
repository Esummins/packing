# A250 -- FAMILY-STUCK: the right stuck hypothesis (Lemma CELLS on every family), its search, and its count
# (from the PI's reading of twelve_stuck_fail.svg, 2026-09-17 10:30: "the 6/9 pair serves both TL00 and TL10 --
# two meeters, two slots, so they can teleport down").
Opus (search + counts; a Fable note only if the count becomes a theorem).  LAUNCH-AND-EXIT. Ops: short responses,
files <= 250 lines, no monitors or waiting turns (the search runs detached, per-row commits, resume block,
logs/STOP), explicit-pathspec commits, PYTHONDONTWRITEBYTECODE=1, at most 2 python processes (BelowNormal, affinity
0xFFFF; the k5 frontier, A238, A241, A244's lanes, A247's triples and A249 are running -- never touch them).
Pages to docs/residue_map/campaigns/A250-family-stuck/.
Read first: ring_swap.md (Lemma CELLS [T, Lean cells_swap]: a family Pi of disjoint cells met by <= |Pi| squares
in total exchanges into the |Pi| slot squares at the same side), attempts/A244-twelve-stuck (the search code
search244 / verify244, the 488 certified twelve-stuck packings in results/twelve244.jsonl, the 4-stuck control),
perimeter_walk.md (A247: PROJECTION [T]: a unit square meets cells of ONE five-cell corner neighbourhood only;
MAX-FIVE; TWO-FAR; UPPER-END), construct_towards.md (NOT-SELF-SUFFICIENT [T]: a corner's two meeters cover <= 5 of
its 6 incidences; TYPE-F-OWN), corner_chase.md (A248), the coordinator's test (below).

## The fact
The coordinator tested the PAIR condition (every disjoint pair of border cells met by >= 3 distinct squares) on all
488 certified twelve-stuck packings and on A217's 486 valid witnesses: ZERO are pair-stuck.  In every twelve-stuck
packing some corner domino {c00, c01} or {c00, c10} is met by exactly 2 squares in total (BL00+BL01 237 times,
BL00+BL10 204, BR 29, TR 15, TL 3), so by CELLS the two squares exchange into the domino: a k2 packing at the same
side.  Twelve-stuck was the wrong hypothesis; FAMILY-STUCK -- every family of disjoint border cells Pi is met by
> |Pi| squares -- is the stuck notion the k0 obligation actually needs, and no witness of it exists in any data at
any side up to 4.5.

## Task
1. SEARCH (A244's optimiser with FAMILY rows): rows for every disjoint pair of border cells (>= 3 distinct meeters,
   depth > 0 each) and every disjoint triple (>= 4), on top of the 12 single-cell rows; minimise the side over 11
   poses, >= 2 000 restarts from random starts and from A244's certified packings as seeds; tilt floor off.  Verify
   every candidate exactly (verify244 extended with the family checks).  Report the least verified FAMILY-STUCK
   side, or the best residual per side over [3.82, 4.6] if none is found, with the effort.  Also the control: the
   same optimiser with only the 12 single-cell rows must reproduce ~4.00001.
2. COUNT: under family-stuck, each corner's three cells need >= 4 distinct squares and each domino >= 3; with
   PROJECTION (a square serves one corner neighbourhood), MAX-FIVE, NOT-SELF-SUFFICIENT and TYPE-F-OWN, derive the
   minimum number of squares a family-stuck packing needs at s <= s-hat, at s < 4, at s in [4, 3+sqrt2), and at
   s >= 3+sqrt2 (where ADJ supply dies): is it > 11 anywhere?  State the count as a lemma with its dependencies; if
   it exceeds 11 on the window, say so plainly -- with WALL-SLOT / CELLS / K0-FREE that is STUCK-EXIST(11) in the
   family form and closes k0_00 (no locks); write Statements/Open/FamilyStuck.lean (the count as a theorem if it
   formalises from the cited theorems, else a documented axiom + the consequence chain; build + audit, 0 sorry).
3. If the count does not exceed 11 but the search finds nothing, state the smallest family-stuck incidence
   structures the count allows (the walk under the family condition -- expect few) and hand them to a bounded
   rigorous search (interval branch-and-bound over their poses at s <= s-hat) as A247 did for pairs.
4. Deliverables: code (search250, verify250, count250), results/family250.md (+jsonl), notes/family250.md, the
   Lean file, pages (a twelve-stuck packing with its teleportable domino highlighted and the k2 packing after the
   exchange; the family-stuck count table), registry row, LOG entry, ledger s.4 note.  Report once (<= 15 lines)
   and EXIT.
