# supply85 — A91 §9's supply gate, run at the sound level (A85 chore)

`code/supply85.py` → `results/supply85.json`, `results/supply85.zones.jsonl`.
One process, `OMP_NUM_THREADS=1`, 97 s wall.

## Headline

**0 / 128 (0.000) of the attemptable four-corner combinations have ZERO viable
supply assignment.** The exact gate, run soundly, kills nothing: A85's
attemptable fraction stays 0.128 (the sound gate sample — 128 attemptable, 5
unkillable, 867 contradictory, reproduced bit-for-bit from `realise85.py`'s
`stage_gate` seed 20260903 and asserted in the run).

The reason is sharper than "no kill": **not one required zone in any of the 128
nodes fails to be reachable by another intruder** (`zones_without_intruder
_supplier.total = 0`). The three free squares were never needed; the free-square
placement machinery (container + core-disjointness) never became load-bearing.
101 / 128 nodes have some zone with exactly one intruder supplier, so the gate is
*close* to a per-zone bottleneck, but never at one.

## Viable-assignment counts (the 128 feasible nodes)

Counted as: ordered triples of pairwise-disjoint free-square blocks × independent
intruder choices for the rest (subset convolution over the ≤ 16 zones).

| decade | 1e4 | 1e5 | 1e6 | 1e7 | 1e8 | 1e9 |
|---|---|---|---|---|---|---|
| nodes | 4 | 40 | 55 | 26 | 2 | 1 |

min 6.4e4, max 2.49e9, median 10^6.28. Zones per node: 8 (23), 9 (47), 10 (41),
11 (14), 12 (2), 13 (1) — i.e. most nodes have 1–5 corner-type (D) intruders
needing both cardinals, the rest a single cardinal.

## Why it is vacuous, and what would not be

Lemma K types are *ambiguous at A85's box resolution* (0.15 in x, y; 7–14° θ
bins): of the 1024 intruder slots, 149 are forced X, 151 forced Y, 184 forced D,
and 540 admit two or three types. Because a single-cardinal type is a strict
weakening of D's requirement, every ambiguous intruder gets the cheaper option,
and 84 / 128 nodes carry ≥ 2 option tuples.

The dominant effect is the zone width. Per pose, the +e-facing zone is half the
square's bbox; over a pose box (subdivided 4×4×4 here) it swells to ≈ 1.4 across,
and the supplier reach test is `dist(centre box, zone) ≤ √2/2`. Two intruders at
the same corner have centres within ≈ 1.77, so the partner almost always reaches
both of the other's zones.

Sensitivity (**diagnostic only, not sound**: pose boxes shrunk by λ about their
centres, so λ < 1 is not a cover):

| λ | 1.00 | 0.50 | 0.25 | 0.00 |
|---|---|---|---|---|
| nodes with an intruder-unsuppliable zone | 0 | 5 | 6 | 8 |

So even at point poses only 6.25 % of nodes have a zone no intruder can reach —
and those would still have to be shown unreachable by a free square. **Refining
the A85 census does not make this gate bite**: the first-link "someone presses me
from the far side" condition is simply not scarce with 10 candidate suppliers.
What is scarce is Lemma COL's ≥ 3-square wall-to-wall chain and the requirement
that the chains at all four corners coexist (`nocrit_k0_blocked.md` §4.4) — the
gate as specified in A91 §9 tests only the first link of each chain and therefore
cannot see the counting obstruction. A useful successor gate must carry the whole
column (monotone contact chain to the far wall, ≥ 3 squares, shared members
across the four corners' columns), not the contact zone alone.

## Conservatism (never reject an assignment that could exist)

* zone = union over a 4×4×4 pose subdivision of the per-pose far-side bbox
  (over-approximates the true union of far-side boundary sets);
* supplier reach = circumradius √2/2 disk against the whole centre box;
* possible Lemma K types over-approximated by interval evaluation (incl. the
  θ = 0 / θ = 90 degenerate faces where the extreme face is an edge, not a
  vertex), and a node is killed only if EVERY option tuple fails;
* free-square centres over-set `[1/2, s0 − 1/2]²`; a core excludes a centre only
  inside `a + 1/2` of its inscribed disk (under-approximated core ⇒ minimal
  exclusion); grid test relaxed by the grid half-diagonal;
* interior-disjointness between suppliers and between suppliers and the intruder
  they press is NOT imposed (doubtful contact counts as possible).

## Canary — Trump's TL 2-crowd: PASS

Exact A03 poses. In the TL frame sq4 = (0.5, 2.5325)→(0.5, 1.3445), tilt 0 →
Lemma K type **Y** (required e_y); sq6 → tilt 49.818°, type **X** (required e_x).
Both agree with A90 `t3_trump.json` (`cardinals` = `["e_y"]` and `["e_x"]`).
Suppliers found: sq4's e_y zone ← {3, 6, 7}; sq6's e_x zone ← {7, 9}. A90's
clusters name 7 as sq4's blocking presser and 9 as sq6's; squares 3 and 7 of the
brief's expected {3, 7, 8} are present. ≥ 1 assignment at both zones — the gate
does not fire on Trump. The run asserts this before touching the census.
