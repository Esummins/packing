# A125 — the local certificate around A122's S33 minimum (and S38), method notes

Read-only on every campaign and on A116 / A119 / A122; new files only, all under
`attempts/A125-s33-local-cert/` (plus `docs/proofs/local_certificate_s33.md`). ≤ 2 BLAS-pinned
processes at BelowNormal, `PYTHONDONTWRITEBYTECODE=1`, no deletes.

## 0. What was built and from what

| piece | source, unmodified | what A125 adds |
|---|---|---|
| Theorem LOCAL, Lemmas COVER / LEAF / RELAX / STAB | `docs/proofs/local_certificate.md` (A116) | nothing — the theory is used verbatim |
| bodies, interval census, relaxed rows, samplers, witness check, Trump canary | `attempts/A116-local-selection-tree/code/a116lib.py` | `build_bodies125`, the same object for two new class frames |
| tilt-cell sharing + dual inheritance tree, keyed rows, rational Farkas export | `attempts/A119-local-cert-lean/code/a119lib.py`, `exact119.py` | `run125.py`, `exact125.py` (same file format) |
| the INDEPENDENT checker | `attempts/A119-local-cert-lean/code/check_local.py` + `exactiv.py` | `check125.py` — imports `Checker` / `load` / `sha256_of` unmodified and only writes the report under A125 (A119's own `main` writes into A119's results, which this attempt is read-only on) |
| the minimum itself | `attempts/A122-s33-certify/results/{exact,polish,contacts,rigidity,a116_input}.json` | the 50-digit Lagrange configuration transcribed into `a125lib.S33_CFG` / `S38_CFG` |

## 1. The two minima, in their class frames

`a125lib.selfcheck` re-derives both as packings before anything else runs.

**S33min** — s\* = 3.9169308657139205630…, class **k6_07** (A53 `name_to_slots.json`), frame = the
**identity**: the six slot squares already sit on k6_07's cells
`BL(0,0) BL(0,1) BL(0,2) BL(1,0) BR(0,0) TR(0,0)`. Worst pair gap −3.3e-16, worst wall gap −4.4e-16.
Rank-14 contact system, first-order Fritz–John stationary (residual 8.3e-9), **all eleven squares
load-bearing, no rattler** (A122 §4), so

    L = { f0, f1, f2, f3, f4 }   (the full non-pin load-bearing set),   P = the six k6_07 cells.

|L| = 5 free bodies (10 centre + 5 tilt LP variables), |P| = 6 pin cores (12 variables), 28 LP
variables in all — against A116's 4 + 5 (S02) and 3 + 5 (S07). The keystone `f0` is **upright**
(tilt 0) and flush against the BL column's right face; `f1, f2` sit at 40.0005°, `f3` at 51.4485°,
`f4` at 47.0887°.

**S38min** — s\* = 3.9289146852229777, class **k6_21**, frame = the D4 element **`diag`**,
(x, y, t) ↦ (y, x, −t) applied at s\*. The image's six slot squares land exactly on k6_21's cells
`BL(0,0) BL(0,1) BL(1,0) TL(0,0) TL(1,0) TR(0,0)` (checked to 1e-9), and the five free squares all
carry the common tilt 90° − 41.754062677271° = **48.245937°** in the class frame. Worst pair gap
−3.3e-16, worst wall gap 0.

Anchoring is A116's: free squares dilated by s0/s\*, slot squares on their cells at s0, pins in
A57's δ-cores (h = δ/√2, δ = 1e-2), window `s ∈ [3.82, 3.897084]`.

## 2. No Trump cut is needed — the census says so

`a116lib.trump_in_N` at **every** point of the grid, for both shadows: **`inside = False`, ops = []**
— no D4 image of Trump's packing puts a square in every box of N *and* in every δ-core. This is
A122 §8 made rigorous inside the tree's own hypothesis: at S33min the keystone `f0` is upright while
Trump's nearest square is at 40.182°, so `f0`'s box excludes Trump on position alone out to
r = 0.2054 (and on tilt alone for any ρ < 40.18°); at S38min the tightest free box is 0.2947 from
any Trump square and `f1`'s is 0.6771. **So no tilt cut is applied anywhere in this attempt** —
unlike A116's S07, which needed `F_T(θ) > s0` from r ≥ 0.033 / ρ ≥ 4.82° onwards. The grid's
`cut = None` column is not an omission; it is the result.

## 3. The measured grid (`results/grid_S33*.jsonl`, `grid_S38.jsonl`; logs `logs/grid_*.log`)

Tree = A119's `RecTree` (one interval census per tilt cell shared by every leaf on it; the parent's
Farkas vector inherited into each child), `min_cell_deg = 0.05`, kill margin s0 + 1e-8, time cap
1800 s (5400 s for the ρ = 20° retries). Entries: verdict, certified minimum (the lowest closed
leaf's Farkas bound over the final cover), tree nodes, wall.

**S33, k6_07 frame, L = f0…f4, no cut** (near pairs 17–21 of 55; interval leaf counts 5·10²–1.6·10⁸):

| r \ ρ | 5° | 10° | 20° |
|---|---|---|---|
| 0.05 | DEAD 3.879029, 3 nodes, 0 s | DEAD 3.877104, 7 749 nodes, 26 s | DEAD 3.877086, 413 215 nodes, 1 233 s |
| 0.10 | DEAD 3.877765, 821 nodes, 12 s | DEAD 3.877085, 17 131 nodes, 36 s | (see §5) |
| 0.20 | DEAD 3.877130, 7 063 nodes, 25 s | **DEAD 3.877085, 420 899 nodes, 1 001 s** | (see §5) |

(the wall figures are the tree alone; the row's `seconds` in the jsonl includes the sampling and
SLSQP checks.)

**Largest certified: (r, ρ) = (0.2, 10°) and (0.05, 20°)** — the same two corners A116 certified for
S02, reached here with five free bodies instead of four and with **no cut**.

**S38, k6_21 frame, L = f0…f4, no cut**, the single requested point: **(0.1, 10°) DEAD**, certified
3.877093, 337 951 nodes, 1 400 s of tree.

**The measured minimum.** SLSQP inside N from 25–60 starts returns **3.916931 = s\* at every
certified S33 N** — the true minimum over N is the shadow minimum itself, so N contains no packing
below s\*, let alone below s0, and the gap between the certified bound (3.87709) and the truth
(3.91693) is the relaxation's, not the geometry's. (S38: 3.909294 at (0.1, 10°), i.e. the SLSQP
minimum leaves S38's own basin but still lands 0.032 above s0.)

## 4. Sampling (`code/sample125.py`, `results/sampling.json`)

A116's sampler is a Python loop at ~1·10⁴ draws/s and, with five free boxes, only 0.03 %–0.9 % of
draws have a pairwise-disjoint free block — so `sample125.py` is the same test vectorised with
numpy (2.3·10⁵ draws/s, cross-checked against `a116lib.sample_check` on equal populations:
72 vs 68 tested per 20 000 at S33 (0.05, 5°), 5 vs 6 at S38 (0.1, 10°)). Reported as
**drawn → tested → hits**: *drawn* = uniform poses in N (centres in the boxes, tilts in the
intervals, pin offsets in the δ-cores); *tested* = the draws whose free block is pairwise
interior-disjoint, each carried to 30 sides in [3.82, s0] and fully tested (all 55 pair selections
and all wall rows); *hits* = a draw that is a packing of L ∪ P at some side ≤ s0.

| N | drawn | tested | hits |
|---|---|---|---|
| S33 (0.2, 10°) | 1 325 000 | 10 146 | **0** |
| S33 (0.2, 5°) | 1 000 000 | 10 326 | **0** |
| S33 (0.1, 10°) | 2 600 000 | 10 815 | **0** |
| S33 (0.1, 5°) | 1 600 000 | 11 065 | **0** |
| S33 (0.05, 20°) | 14 600 000 | 10 088 | **0** |
| S33 (0.05, 10°) | 5 600 000 | 10 037 | **0** |
| S38 (0.1, 10°) | 30 000 000 | 10 013 | **0** |

## 5. The limiter

Not Trump (§2), not a rearrangement of L ∪ P (no witness and no unresolved leaf was found at any
grid point — A116's r = 0.3 limiter does not bite here because L is the WHOLE non-pin set, so there
are no dropped squares to un-block a rearrangement), but **the tilt-cell count at ρ = 20° with
r ≥ 0.1**: five tilt dimensions must be bisected to ≈ 1° before the McCormick term
((q-range) × cell width) is smaller than the margin, and the DFS does not empty its stack inside the
cap. Both ρ = 20° cells at r ≥ 0.1 are OPEN, not alive, and stay open when the cap is tripled to
5 400 s (`results/grid_S33_long.jsonl`):

| N | cap | nodes | closed leaves | certified min of the closed part | witnesses | unresolved |
|---|---|---|---|---|---|---|
| (0.1, 20°) | 1 800 s | 672 797 | 331 150 | 3.877093 | 0 | 0 |
| (0.1, 20°) | 5 400 s | 1 773 853 | 876 474 | 3.877088 | 0 | 0 |
| (0.2, 20°) | 1 800 s | 557 616 | 311 399 | 3.877087 | 0 | 0 |
| (0.2, 20°) | 5 400 s | 1 264 247 | 715 814 | 3.877087 | 0 | 0 |

This matters because A119 corrected three of A116's four "capped" ρ ≥ 20° cells to ALIVE (a checked
packing of L ∪ P below s0 inside N). Here the tree found **no witness at all** in 3 M nodes across
the two cells, which is what §1's "DROP is vacuous" predicts: A116's live witnesses were
rearrangements that the dropped squares would have forbidden, and here nothing is dropped.
`(0.05, 20°)` closes (413 215 nodes, 1 233 s), so the ρ = 20° frontier sits between r = 0.05 and
r = 0.1.

## 6. The exact certificates (`code/exact125.py`, `certs/`, checked by `code/check125.py`)

Same object and same file format as A119 T1, so A119's checker reads them unchanged: the recorded
proof tree (bisect / branch / imp / dead), and per dead leaf a **rational** Farkas vector (every
multiplier a multiple of 2⁻⁴⁰) re-verified by weak duality against the leaf's own relaxed rows
before it is written. Dual inheritance is left ON (a child is closed on the inherited vector only
when that vector certifies the bound on the CHILD's rows), which is what makes the 2·10⁵-leaf
certificates generable in 20 minutes rather than hours; the checker is the arbiter either way.

| certificate | dead leaves | multipliers | gz | generator | checker | verdict, min bound |
|---|---|---|---|---|---|---|
| **S33 (0.2, 10°)** | 215 904 | 4 385 025 | 34.3 MB | 1 228 s | 5 034 s | **VALID**, 3.877085097 |
| S33 (0.05, 20°) | 196 048 | 2 935 516 | 18.9 MB | 1 251 s | 4 078 s | **VALID**, 3.877086096 |
| **S38 (0.1, 10°)** | 174 160 | 3 022 417 | 21.5 MB | 1 085 s | 4 942 s | **VALID**, 3.877107298 |
| S33 (0.1, 10°) | 8 758 | 185 809 | 1.70 MB | 57 s | 245 s | **VALID**, 3.877084626 |
| S33 (0.2, 5°) | 3 804 | 81 532 | 0.69 MB | 25 s | 106 s | **VALID**, 3.877131332 |
| S33 (0.05, 10°) | 3 747 | 78 768 | 0.77 MB | 26 s | 90 s | **VALID**, 3.877114509 |
| **total** | **602 421** | **10 689 067** | 77.9 MB | 3 672 s | **14 497 s** | **6/6 VALID** |

## 7. Consumer (`code/consumer125.py`, `results/consumer.json`)

A116 §7(b)'s test, widened so a node of a SMALLER class can be tested against a bigger-class N: the
node's LP-support representative (A107 `extract.json` `cfg`, eleven poses at s0) is carried into the
class frame and matched INJECTIVELY against **all** the bodies of N — the |L| free boxes *and* the
|P| pin cores. Testing the pins is what makes a trump5 (A60) node admissible against a k6_07 N at
all: trump5's five cells are a subset of k6_07's six, so the sixth, `BL(0,2)`, has to be found in
the support; it is not free by the node's class. Both frames are reported: A107's own `struct_op`
(A116/A119's test) and the best of the eight D4 images (also sound as a kill — a packing at the node
whose image satisfies N is killed with its image).

Over all 1 421 alive nodes carrying a support (A57 963, A60/trump5 283, A61 14, plus A107's Part-II
k0 nodes; the other 42 of A107's 325 A60 nodes have no support representative in `extract.json`):

| N | inside (struct_op) | inside (any D4) | pin-eligible | of which A60/trump5 |
|---|---|---|---|---|
| S33/k6_07 (0.2, 10°) | **1** | **1** | 30 | 25 |
| S33/k6_07 (0.2, 5°), (0.1, 10°), (0.1, 5°), (0.05, 20°), (0.05, 10°) | 0 | 0 | 30 | 25 |
| S38/k6_21 (0.1, 10°) | 0 | 0 | 102 | 25 |

The one node inside is S33's own gallery node `c0_Y0335` (A60/trump5, level 1) at centre deviation
0.1044 and tilt deviation 8.699°, i.e. r ≥ 0.1047 and ρ ≥ 8.70°. **What blocks the rest is the
sixth pin, not the radius**: the body whose nearest support square is furthest outside its own
tolerance is `BL(0,2)` for 1 065 of 1 421 nodes (then `BL(1,0)` 199, `TR(0,0)` 94), and only 30
nodes have all six k6_07 cells fillable by distinct tilt-0 squares inside their δ-cores. S34's node
has `BL(0,2)` inside the core in position (0.0065 < h) but tilted 0.75°; S35's has it lifted by
0.0262 > h (cf. Trump's own 0.0326 lift); K19's node (Part II, A38 `node_053`) has `BL(1,0)` 0.1326
off its cell. The same phenomenon at S38 with k6_21's own distinguishing cell: `TL(1,0)` blocks
1 020 of 1 421, and S38's node `c0_Y0169` needs r ≥ 0.2703 at ρ = 40°.

Distance census (minimal centre radius for a full match, over the eight D4 images): for the k6_07 N,
1 node at r ≤ 0.2 for ρ ∈ {10°, 20°}; at ρ = 40°, 2 at r ≤ 0.2, 10 at r ≤ 0.3, 19 at r ≤ 1.0 (18 of
them A60/trump5). Nothing at ρ = 5°.

## 8. Files

```
code/a125lib.py        the two minima in their class frames; build_bodies125; selfcheck
code/probe125.py       census / root LP / Trump canary per grid point (no tree)
code/run125.py         the grid, largest first; sampling + SLSQP + Trump canary per DEAD verdict
code/sample125.py      the vectorised sampler (drawn -> tested -> hits)
code/exact125.py       the rational Farkas certificate (A119 T1 format)
code/check125.py       A119's check_local.Checker, unmodified, reporting under A125
code/export_boxes125.py  results/N_boxes.json in A119's format
code/consumer125.py    the consumer counts and the distance census
results/grid_S33*.jsonl grid_S38.jsonl probe.json sampling.json consumer.json N_boxes.json check_local.json
certs/*.cert.json.gz manifest.json
```
