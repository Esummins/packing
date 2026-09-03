# A88 D5 — `results/census88_sample.jsonl` format

One JSON object per line. Every record is a DECORATED support structure H on a loaded core of
**k = 11** squares plus the 4 wall nodes, at side s in the certified window
**[S_LO, S_HI] = [3.82, 3.877084]**. The pilot can build the algebraic system directly from the
`rows` field: it is already in the A30 `t3lib` row vocabulary.

## Provenance / sampling

* **Level 0** — uniform over LABELLED F0 survivors. The factorable superset (masks in the 9
  L5(b)-admissible masks, pairwise coexistence, touching window on every edge) is sampled
  EXACTLY (masks from the exact marginal, every touchable pair an independent fair coin), and
  the full F0 filter set is applied; every survivor found is an exactly uniform draw. Read as a
  sample of ORBITS it carries A59's orbit-weight caveat (here measured at **+3.3 %**: the exact
  Burnside orbit count is 1.0330 x labelled/(11! * 8)).
* **Level 1** — uniform among the tilt-feasible decorations of that structure that additionally
  satisfy **K0-1** and **K0-3**, by rejection from the raw gauge-fixed menu `20^Ess * 2^Esw`.
* `tag` = `"F0+K0-1+K0-3"` for the main block, `"F0+K0-3 (K0-1 dropped)"` for the 100 extra
  records in which the slot-exclusion filter K0-1 was NOT imposed.

## Gauge (state it once, do not re-derive)

A square carries no marking, so rotating its corner/edge labels by 90 deg is the same physical
square. The gauge fixes `phi_i = theta_i mod 90 deg` in **[0, 90)**, which fixes the labels.
With A30 `t3lib` conventions (`z[3i]=cx_i`, `z[3i+1]=cy_i`, `z[3i+2]=theta_i`, `z[33]=s`):

* corner `k` of square `i` sits at `c_i + R(theta_i) * HALF[k]`,
  `HALF = [(-1/2,-1/2), (1/2,-1/2), (1/2,1/2), (-1/2,1/2)]`;
* edge `e` of square `i` has outward normal `R(theta_i) * NHAT[e]`,
  `NHAT = [(0,-1), (1,0), (0,1), (-1,0)]`;
* hence **edge `e` joins corners `e` and `e+1 mod 4`**.

Wall dictionary in this gauge (wall bit b: 0=L `x=0`, 1=B `y=0`, 2=R `x=s`, 3=T `y=s`):

| wall | touching EDGE (wall-flush) | touching CORNER (corner-on-wall) |
|---|---|---|
| L `x=0` | 3 (corners 3, 0) | 3 |
| B `y=0` | 0 (corners 0, 1) | 0 |
| R `x=s` | 1 (corners 1, 2) | 1 |
| T `y=s` | 2 (corners 2, 3) | 2 |

## Decoration menu (A31 gauge-fixed, 20 per SS edge, 2 per SW edge)

* **flush(i,j)** — 4 types: which edge `e` of the OWNER (this file always takes the LARGER
  vertex index as the owner) is flush; the partner's edge is then forced to `e+2 mod 4`.
* **corner-on-edge** — 16 types: (owner in {i,j}) x (edge `e` of the owner) x (sign of the class
  inequality). Given the sign, the touching corner `c` of the partner is forced:
  `(e - c) mod 4 = 3` when `phi_partner > phi_owner`, `= 2` when `phi_partner < phi_owner`
  (the other two residues are geometrically impossible).
* **square-wall** — 2 types: wall-flush (pins `phi_i = 0`) or corner-on-wall (needs `phi_i != 0`).

The map decoration -> `rows` was verified INJECTIVE by exhaustive enumeration on six small
structures (`code/selftest88.py`, `results/selftest88.json`): the menu size is exactly
`20^Ess * 2^Esw` in every case, the tilt-feasible count agrees with the independent A31/A44
exact formula, and distinct decorations give distinct row sets.

## Fields

| field | meaning |
|---|---|
| `tag` | which filter set the record was drawn under |
| `k`, `loaded_core` | 11 and `[0..10]` — every square is loaded here |
| `wall_mask`, `wall_mask_names` | wall bitmask per square (bit b as above) and its letters |
| `ss_edges` | the square-square edges of H, as `[i,j]` with `i<j` |
| `rows` | THE ROW SET (see below) |
| `tilt_class` | class id per square; class **0 is the pinned (phi = 0) class when it exists** |
| `n_classes` | number of tilt classes |
| `class_order_strict` | list of `[lower_class, upper_class]` STRICT inequalities |
| `zero_class_pinned` | true iff some square is wall-flush, i.e. class 0 exists and is `phi = 0` |
| `Ess`, `Esw`, `E` | square-square edges, square-wall edges, `E = Ess + Esw` |
| `F` | number of FLUSH contacts (SS flush + wall-flush); each carries 2 rows |
| `m` | `E + F` = number of rows (A44 Fact 0 convention) |
| `chi` | `m - (3k+1)` = `m - 34`; `chi >= 0` is RIGID-POSSIBLE |
| `n_flush_ss`, `n_wall_flush` | the two parts of `F` |
| `rigid_possible` | `chi >= 0` |
| `slot_squares` | squares with two wall-flush contacts (empty iff K0-1 holds) |
| `K0_1`, `K0_2`, `K0_3` | slot exclusion / A58 crowding CSP / A45 Lemma-R ruler cap |

## `rows` — the A30 t3lib vocabulary

* `{"kind":"wall","i":sq,"corner":0..3,"wall":"x=0"|"y=0"|"x=s"|"y=s"}`
  = the row `q_corner(sq) . n_wall >= 0` (resp. `s - q >= 0`).
  A **corner-on-wall** contact emits ONE such row; a **wall-flush** contact emits TWO — the two
  corners `k`, `k+1` of the square's edge facing that wall (table above).
* `{"kind":"sep","o":owner_sq,"e":edge 0..3,"p":corner_sq,"kstar":corner 0..3}`
  = the separation row `n_e(theta_o) . (q_kstar(p) - c_o) - 1/2 >= 0`.
  A **corner-on-edge** contact emits ONE such row; a **flush** contact emits TWO — corner
  `kstar = e+2` of `p` and its neighbour `e+3` on that same edge of `p`.
  The associated t3lib DOMINANCE rows are NOT emitted: they are determined by `(o,e,p,kstar)`
  and the pilot rebuilds them with `t3lib.dom_row(o, e, p, kstar, m)` for `m != kstar`.

`len(rows) == m == E + F` in every record (asserted at emission and re-checked on Trump).

## Realisability

The row set is guaranteed to be self-consistent for SOME assignment of tilts respecting
`class_order_strict` (the tilt-feasibility test is exact for the tilt subsystem: equalities by
union-find, strict inequalities acyclic, nothing strictly below class 0). Positions are NOT
checked — the pilot's realisability LP decides that. No geometric pre-filtering beyond the
tilt test was applied.
