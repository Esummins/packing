# FAMILY-STUCK — the stuck hypothesis Lemma CELLS actually needs, its count and its search — A250, 2026-09-17

The PI (10:30), reading A248's `twelve_stuck_fail.svg`: *"the 6/9 pair serves both TL00 and TL10 — two meeters, two
slots, so they can teleport down."*  This note (i) states FAMILY-STUCK and shows it is the hypothesis the k0 route
needs, not A244's TWELVE-STUCK (§1); (ii) proves the COUNT — family-stuck needs `n ≥ 4⌊s⌋ − 3`, so 13 squares at every
side ≥ 4 and only 9 below 4 — exactly, by integer programming over the PROJECTION catalogue (§2); (iii) reports the
search (§3) and the corpus (§4); (iv) says what is left (§5).  Tags: [T] proved, [T-computed] certified by an exact
finite computation, [M] measured, [C] obligation, [F] fails.  Code `attempts/A250-family-stuck/code/`
(`fam250`, `fast250`, `search250`, `verify250`, `count250`, `pages250`, `summarise250`, `test250`, `run250.sh`),
results `results/family250.md` (+ `count250.json`, `fam250_*.jsonl`), pages
`docs/residue_map/campaigns/A250-family-stuck/{domino_exchange,count}.svg`, Lean
`Statements/Open/FamilyStuck.lean`.  Sources: `ring_swap.md` (Lemma CELLS, the perimeter count),
`construct_towards.md` (A246), `perimeter_walk.md` (A247), A244 `twelve244.md`, A248 `corner_chase.md`.

## 0. Verdict

> **[T] FAMILY-STUCK is the right hypothesis.**  Lemma CELLS (`ring_swap.md` §1.3, Lean `cells_swap`) exchanges a
> packing, at the same side, into any family `Π` of pairwise interior-disjoint unit cells with `|M(Π)| ≤ |Π|`.  So the
> hypothesis that blocks every exchange is FAMILY-STUCK — `|M(Π)| > |Π|` for EVERY disjoint family of border cells —
> of which A244's TWELVE-STUCK is only the rows `|Π| = 1`.  The gap is real and it is where every corpus packing
> lives: a corner DOMINO `{c00, c01}` met by exactly two squares in total is a legal `Π` with `|M(Π)| = |Π| = 2`.
>
> **[M]/[T-computed] Nothing in the corpus is family-stuck.**  0 of A244's 488 certified twelve-stuck packings and 0
> of A217's 486 witnesses are even PAIR-stuck; every one has a corner domino met by exactly two squares (the exchange
> drawn and geometry-checked in `domino_exchange.svg`: nine squares kept, the two meeters replaced by the two cell
> squares — a k2 packing at the same side).
>
> **[T]/[T-computed] The count** (§2).  At a side `s ≥ 4` the twelve border cells are PAIRWISE DISJOINT, so the whole
> twelve is a legal family and family-stuck needs 13 squares: **no packing of eleven unit squares at any side ≥ 4 is
> family-stuck** (Lean `no_family_stuck_ge_four`) — where A244 certifies 488 twelve-stuck ones from 4.000010 to 4.5
> and A247's UPPER-END only reaches down to `4 + √2`.  The family hypothesis has no window above 4 at all.  Below 4
> the two facing slots of each wall overlap, the largest family is 8 cells, and the exact minimum over all incidence
> structures (ILP over the PROJECTION catalogue with NOT-SELF-SUFFICIENT and TWO-FAR; SLOT-MET and A247's 62 certified
> pair kills add nothing) is **9 ≤ 11**.  **The count does not close the window**: k0_00 unchanged.
>
> **[M] The search** (§3): A244's optimiser with the family rows (every disjoint pair ≥ 3 meeters, every disjoint
> triple ≥ 4, on top of the twelve single-cell rows), exact verification of every candidate: no FAMILY-STUCK packing
> anywhere on `[3.82, 4.6]`; the least side at which even the `|Π| ≤ 3` rows are met is ≈ 4.0017, and the full
> condition fails there by the count.  Control (`|Π| ≤ 1` only): 4.0005 — A244's 4.000010 reproduced.
>
> **What A250 buys**: the obligation on `[3.82, ŝ]` is now FAMILY-STUCK-EXIST(11) — strictly weaker than
> STUCK-EXIST(11) (Lean `family_stuck_of_stuck_exist`: family-stuck implies twelve-stuck), so it is a smaller thing to
> kill; and the whole region `s ≥ 4`, which carried every known twelve-stuck packing, is dead for it by counting.

## 1. The hypothesis

**1.1 Setting.**  Container `[0, s]²`, `s > 3`; the twelve BORDER CELLS of A244 `cells244`: per corner `c` the box
`c00` and the wall slots `c01` (up `c`'s wall) and `c10` (along its floor).  `M(Π)` := the squares whose interiors
meet a cell of `Π`.  A family is ADMISSIBLE when its cells are pairwise interior-disjoint.

> **Definition (n-general).**  A packing is **FAMILY-STUCK** when `|M(Π)| > |Π|` for every admissible family `Π` of
> border cells.  `|Π| = 1` is TWELVE-STUCK; `|Π| = 2` on `{c00, c01}` is PAIR-STUCK.

**1.2 Why this and not TWELVE-STUCK [T].**  Lemma CELLS is a Hall-type deficiency criterion: `|M(Π)| ≤ |Π|` alone
licenses the exchange `X := M(Π) ∪ (any |Π| − |M(Π)| others) → X' := Π`.  A twelve-stuck packing may still have a
domino with two meeters in total — and then the exchange puts down BOTH cells of the domino at once (RAISE(0 → 2), a
k2 packing).  The twelve-cell condition asks 24 incidences of a set that may be supplied by as few as 8 squares
(§2); the family condition asks, per corner, FOUR distinct squares on `{c00, c01, c10}` — i.e. a corner with two
meeters needs TWO distinct outside suppliers, not one square covering both slots.  That one square is exactly what
every corpus packing uses.

**1.3 Which cells are disjoint [T].**  Along one wall the cells' intervals are `(0,1)`, `(1,2)`, `(s−2, s−1)`,
`(s−1, s)`; the only pair that can overlap is the facing pair `(1,2)`, `(s−2, s−1)`, and it is interior-disjoint iff
`s ≥ 4`.  Cells of different walls differ by more than 1 in a coordinate for `s ≥ 3`.  So the conflict graph of the
twelve cells is a **perfect matching on the eight slots below 4** (four conflicting pairs, one per wall: max family 8,
1295 admissible families) and **empty at `s ≥ 4`** (max family 12, 4095 families).  `fam250.conflicts` computes
exactly these; `test250` checks it.

## 2. The count

**2.1 The perimeter form [T] (n-general).**  A packing of `n` unit squares that is family-stuck at side `s` has
`n ≥ 4⌊s⌋ − 3`.  *Proof.*  The perimeter carries `4⌊s⌋ − 4` pairwise disjoint cells (`ring_swap.md` §1.4); family-
stuck needs more meeters than cells, and the meeters are squares.  ∎  For `n = 11`: `s < 4`.  At `n = 11`, `s ≥ 4` the
twelve border cells themselves are the family — **Corollary (Lean `no_family_stuck_ge_four`, `family_stuck_side_lt`):
no eleven-square configuration at a side ≥ 4 is family-stuck.**  The same count read forwards is `ring_swap.md`'s
remark that RAISE is trivial above 4, now a theorem: `raise_of_ge_four` (every eleven-square packing at `s ≥ 4`
exchanges into one containing a corner square, no hypothesis at all).

**2.2 The exact count below 4 [T-computed]** (`count250.py`).  A square's cell-set is, by PROJECTION [T, A247], a
subset of ONE five-cell corner neighbourhood `N_c = {c00, c01, c10, c′10, c″01}`, and every subset is realisable below
4 with an exact rational witness (A247 §2.1) — 112 types.  Minimise `Σ x_t` over non-negative integers subject to:
every admissible family `Π` has `Σ_{t ∩ Π ≠ ∅} x_t ≥ |Π| + 1`; `Σ_{t ⊇ {c00,c01,c10}} x_t ≤ 1` (NOT-SELF-SUFFICIENT
[T, A246]); `Σ_{t ⊇ {c00, g}} x_t ≤ 1` for each far slot `g` (TWO-FAR [T, A247]).  Any family-stuck packing is a
feasible point, so the optimum is a valid lower bound on `n` for every `n`.  Exact optima (HiGHS):

| level | `s ∈ [3,4)` (1295 families) | `s ≥ 4` (4095 families) |
| --- | --- | --- |
| `|Π| ≤ 1` (TWELVE-STUCK) | 8 | 8 |
| `|Π| ≤ 2` (dominoes) | 8 | 8 |
| `|Π| ≤ 3` | 8 | 8 |
| `|Π| ≤ 4` | 8 | 10 |
| every family (FAMILY-STUCK) | **9** | **13** |
| every family containing a corner cell (what RAISE needs) | 9 | 13 |
| + SLOT-MET [T-computed, A246] | 9 | — |
| + A247's 62 certified pair kills (436 D4 images, level (0.05, 0.07)) | 9 | — |
| + both | 9 | — |

**9 ≤ 11: the count does not close the window.**  Every extra proved layer available (SLOT-MET, the certified pair
table, the restriction to families containing a corner cell) leaves it at 9.  This is the same wall as A246 §3 and
A247 §3: the rules are local and the obstruction below 4 is global.

**2.3 The smallest structures the count allows [T-computed]** (`count250.structure`; the brief's task 3).  With the
total fixed at `n`, the exact min/max of each functional over all structures:

| n | free squares | 5-cell squares | meeters of one corner | cross-corner squares | ADJ suppliers |
| --- | --- | --- | --- | --- | --- |
| 9 | 0 … 1 | 0 … 4 | 2 … 3 | 5 … 9 | 4 … 8 |
| 10 | 0 … 2 | 0 … 4 | 2 … 4 | 4 … 10 | 2 … 8 |
| 11 | 0 … 3 | 0 … 4 | 2 … 5 | 3 … 11 | 0 … 8 |

So a MINIMAL (n = 9) family-stuck structure is rigid: at most one free square, at least five squares whose cell-set
spans two corners and **at least four ADJ suppliers** (a box meeter reaching the adjacent corner's far slot — by
ADJ-REACH [T, A246] each needs extent > s − 3 along its wall, and by TYPE-F-OWN a type-F corner emits at most one).
At `n = 11` every one of those minima collapses (ADJ suppliers may be 0), so the eleven-square list is **not few**:
it is A247's walk count again with four extra demands, and a per-walk bounded search over 11 poses + s is out of
reach by A247 §4.3's factor.  The bounded rigorous search can only be handed the `n = 9` skeletons, which are not
what `n = 11` must realise — recorded, not run.

## 3. The search [M]

`search250.py` = A244's optimiser (`feas244` phase A/B) driven by FAMILY rows: for every admissible family with
`|Π| ≤ kmax` the `(|Π|+1)`-th largest overlap depth over the eleven squares must be ≥ δ.  `kmax = 1` reproduces
A244's penalty bit for bit (`test250`), which is the control.  Rows are taken from the `s < 4` conflict graph, a
NECESSARY condition at every side in `[3, 5)`.  Every candidate that meets its rows is verified exactly
(`verify250`, mpmath intervals, 40 digits): containment, pairwise interior-disjointness, and the family condition
over EVERY admissible family at the certified side — with the SURE meeters (depth interval entirely > 0) for a PASS
and the MAYBE meeters plus provably disjoint cells for a certified failure.  Live numbers, lanes resumable
(`run250.sh laneA|laneB`, `logs/STOP`): `results/family250.md`.

## 4. The corpus [T-computed]

| corpus | n | sides | twelve-stuck | pair-stuck | family-stuck |
| --- | --- | --- | --- | --- | --- |
| A244 `twelve244.jsonl` | 489 | 4.000010 … 4.5 | 488 | **0** | **0** |
| A217 `witnesses217.jsonl` | 486 | 3.886746 … 5.001260 | 43 | **0** | **0** |

Every one of the 488 certified twelve-stuck packings has at least one corner domino met by exactly two squares
(counting every occurrence: `{BR00,BR01}` 346, `{TL00,TL10}` 317, `{BL00,BL01}` 237, `{TR00,TR01}` 215,
`{TR00,TR10}` 211, `{BL00,BL10}` 205, `{TL00,TL01}` 111, `{BR00,BR10}` 90), and the exchange is a packing: the page
`domino_exchange.svg` draws the lowest-sided one (s = 4.000012), its two meeters and the k2 packing after the
exchange, with the geometry check on both panels.

## 5. What is left

* **[C] FAMILY-STUCK-EXIST(11)** on `[3.82, 4)`: no packing of eleven unit squares below side 4 is family-stuck.
  Lean `family_stuck_exist_eleven`; implied by STUCK-EXIST(11) (`family_stuck_of_stuck_exist`), so this is the
  weaker obligation — but the count reaches only 9 and the search finds nothing.
* **[T] dead above 4**: `no_family_stuck_ge_four`, and with it RAISE at every side ≥ 4 (`raise_of_ge_four`).
* k0_00's row is **unchanged**: the route is sound and load-free, its obligation is geometric, and the family form
  does not make it a counting consequence.
