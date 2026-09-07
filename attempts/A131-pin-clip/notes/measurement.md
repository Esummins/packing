# A131 T1 + T2 — the pin-clip, confirmed and measured

Code: `code/pinclip.py` (the clipper), `code/t1_check.py` (sampling + controls),
`code/corpus131.py` (the corpus sweep), `code/gen_pinclip_fig.py` (the figure).
Results: `results/t1_check.json`, `results/corpus131.json`, `results/corpus131.jsonl`.
Figure: `notes/pinclip_Y0036.svg`.

## T1 — the clipper

`pinclip.clip_node(box, slots, nsub)` replaces the centre box, per tilt sub-bin, by the
axis-aligned rectangle left after removing every centre at which the conditioned square meets a
pin core at EVERY tilt of the sub-bin (or leaves the container at every tilt). Arithmetic is
**exact rational throughout**: tilts are carried as `t = tan(θ/2)`, which is how A57's cover is
built (lemmas.md T2), so `cos θ = (1−t²)/(1+t²)` and `sin θ = 2t/(1+t²)` are exact rationals at
every sub-bin endpoint and there is no epsilon anywhere in the decision. Floats appear only in the
*search* for a slab boundary (a bisection); every boundary the search proposes is then certified by
the exact predicate and walked back until it certifies.

**The intersection over tilts is exact, not a sub-bin worst case.** The first version used
trim57's envelope — `A`, `B` at `w_min` against `max_θ |d·n|` — which is sound but loses badly on
wide bins. Rewriting the four SAT conditions as

    |d_x| < w_min/2 + a_P,   |d_y| < w_min/2 + a_P,
    max_θ [ (±d_x − a_P) cos θ + (±d_y − a_P) sin θ ] < 1/2      (u-axis, two sign branches)
    max_θ [ (±d_y − a_P) cos θ + (∓d_x − a_P) sin θ ] < 1/2      (v-axis, two sign branches)

turns each rotating-axis condition into a SINGLE sinusoid in θ whose maximum over the sub-bin is at
an endpoint or at the interior critical point (value `√(P²+Q²)`, compared as `P²+Q² < 1/4`). That
is the exact `⋂_θ Octagon(θ)`. The difference is not cosmetic: at `nsub = 1` the envelope version
fails to empty **34 of the 674** boxes the tree kills by "core meets pin core"; the exact version
empties **674 of 674**.

### Sampled confirmation — `drawn → tested → hits`

12 nodes (Y0036 and its four depth-2 children, plus 7 drawn at random from the open set),
`nsub = 8`, 40,000 draws in each region per node:

* **discarded region: 480,000 drawn → 287,017 tested → 0 hits.** A "hit" is a draw in the removed
  region that is nevertheless pin-free and inside the container, i.e. a counterexample. Per-node
  the tested counts run 22,319 – 40,000, so the ≥ 10⁴ bar is met **by each node relied on**, not
  only in aggregate (lemmas.md's rule).
  The six extra T3 nodes were sampled separately at `nsub = 1`
  (`results/t3_node_samples.json`): **240,000 drawn → 190,303 tested → 0 hits**, per-node tested
  23,236 – 36,704. **Grand total across all three sampled sets** (T1's twelve, T3's ten, and the
  21 incremental kills): **1,140,000 drawn → 897,320 tested → 0 hits**.
* kept region: 480,000 drawn → 415,075 tested → 352,898 feasible (85.0 %). This is not required to
  be 100 %: the clip removes only the four axis-aligned dead slabs, so a dead region strictly
  inside the box survives in the bounding rectangle. The worst node of the twelve is
  `k5_16_interior_Y0279` (19 % feasible in the kept box), the best are the untouched ones (100 %).

### Positive control A — the tree's own logic kills

**674 of 674** boxes carrying `KILL-BY-LOGIC (core meets pin core)` clip to EMPTY at `nsub = 1`.
That is the required domination: `K_B` lies inside every admissible square, so if `K_B` meets a pin
core then every centre of the box is dead at every tilt, and the clipper must see it.

### Control C — the predicate against a direct SAT computation

`dead_q` is not only sound, it is **exact**. Cross-checked against an independent, direct
separating-axis computation on a 2,001-point tilt grid: 40,000 random (offset `d`, tilt sub-bin)
pairs, sub-bin widths 0.5° – 90°, `dead_q` true on 29,008 of them —
**0 cases where `dead_q` says dead but a grid tilt separates** (unsoundness), and
**0 cases where every grid tilt overlaps but `dead_q` says alive** (a missed kill). The two
implementations share no code: the check evaluates `|cos| + |sin|` and the four SAT axes in floats
at each grid tilt, where `dead_q` works from the closed-form sinusoid maxima in exact rationals.

### Positive control B — the stored LP support atoms

The solved-node records (`attempts/A57-shadow-trees/results/tree/<key>/<id>.json`, field
`packing` = the placements with positive dual weight) give **99,991 support columns over 1,745
solved nodes**. Two checks:

* every column is pin-free at its own tilt, up to the LP's own row-filter slack: 9,788 columns
  penetrate a pin core, **maximum depth 2.0000·10⁻³**, and **0 exceed `caselp.EPS_CORE = 2·10⁻³`**
  — the LP drops a row only when it penetrates a core by more than `EPS_CORE` on every axis, so
  shallow penetration is the documented conservatism of the filter, not a violation of the octagon
  geometry. (Note for anyone repeating this: `lpbox` stores row tilts in **radians**, not degrees.
  Reading them as degrees produces 31,316 spurious "violations" up to depth 0.146.)
* **0 of the 99,991 columns lie inside their own node's conditioned box**, hence none can fall
  outside the clip. That is not an accident and it is worth recording: an admissible LP row must be
  disjoint from every core including `K_B`, and a placement in `B` contains `K_B`, so the "support
  atoms inside the clipped box" test is vacuous by construction. The non-vacuous version is the
  pin-freeness check above.

## T2 — the corpus

The corpus is rebuilt by A96's own selection rule (`trim96.rows()`, re-implemented in
`code/t1_check.py` so A96 stays read-only). It has **grown since A96's snapshot**: 2,418 boxes now
(674 logic kills + 1,744 open) against A96's 2,222, because the A123 night shift added 296
children. **A96's frozen 1,604-row open set is a subset and is tracked separately** — the check
that the reconstruction is right is that T5″ recomputed here empties exactly **159** of those 1,604
rows, reproducing A96's headline number.

### Kept fraction, empties and free levels, by level

`EMPTIED` = clipped EMPTY at every sub-bin (a logic kill, no LP, no certificate). `touched` =
narrowed but alive. `free levels` = ½·log₂(1/kept), quoted over the *touched* population only
(it is 0 by definition on the untouched and ∞ on the emptied).

**nsub = 1** (one clip per node — the recommended default: one child, one certificate)

| | n | EMPTIED | touched | untouched | mean kept | free levels med / mean / max |
|---|---|---|---|---|---|---|
| L1 | 1266 | 67 (5.29 %) | 221 (17.5 %) | 978 | 0.840 | 0.88 / 1.14 / 8.07 |
| L2 | 425 | 90 (21.18 %) | 113 (26.6 %) | 222 | 0.642 | 0.63 / 1.03 / 7.46 |
| L3 | 39 | 10 (25.64 %) | 13 (33.3 %) | 16 | 0.620 | 0.24 / 0.42 / 1.72 |
| L4 | 14 | 12 (85.71 %) | 2 (14.3 %) | 0 | 0.024 | 3.92 / 2.36 / 3.92 |
| **all** | **1744** | **179 (10.26 %)** | **349 (20.0 %)** | **1216** | **0.780** | **0.63 / 1.09 / 8.07** |

**nsub = 8**

| | n | EMPTIED | touched | untouched | mean kept | free levels med / mean / max |
|---|---|---|---|---|---|---|
| L1 | 1266 | 68 (5.37 %) | 313 (24.7 %) | 885 | 0.808 | 0.66 / 1.22 / 9.57 |
| L2 | 425 | 90 (21.18 %) | 127 (29.9 %) | 208 | 0.601 | 0.98 / 1.38 / 8.96 |
| L3 | 39 | 10 (25.64 %) | 13 (33.3 %) | 16 | 0.600 | 0.31 / 0.58 / 2.78 |
| L4 | 14 | 12 (85.71 %) | 2 (14.3 %) | 0 | 0.010 | 5.42 / 3.42 / 5.42 |
| **all** | **1744** | **180 (10.32 %)** | **455 (26.1 %)** | **1109** | **0.747** | **0.71 / 1.26 / 9.57** |

Intermediate resolutions: `nsub = 2` → 179 emptied / 428 touched / mean kept 0.762;
`nsub = 4` → 180 / 447 / 0.752. **Refining the sub-bin buys touch, not kills**: from 1 to 8
sub-bins the empty count moves 179 → 180 while the touched count moves 349 → 455. That is a direct
consequence of the exact intersection: at `nsub = 1` the rule is already as strong as it can be
against a *single* pin over the whole bin, and only the multi-pin/partial-overlap cases improve.

### By class

| | n | EMPTIED | touched | mean kept (nsub 8) |
|---|---|---|---|---|
| k5_11 | 939 | 127 (13.53 %) | 254 (27.1 %) | 0.700 |
| k5_16 | 805 | 53 (6.58 %) | 201 (25.0 %) | 0.801 |

k5_11 is clipped twice as hard as k5_16, and the reason is visible in the slot lists: k5_11 pins
`(1.5, 0.5)` — an **interior-adjacent** pin, the `bl10` of the PI's reading — where k5_16 pins the
far corner `(3.377084, 3.377084)` instead. An interior pin casts a much larger shadow over the
interior zone `[1.1, 2.777]²` that both trees condition on.

### Overlap with T5′ and T5″

* **T5′** (the tree's own `KILL-BY-LOGIC`, 674 boxes): dominated completely — 674/674 clip to EMPTY
  (control A).
* **T5″** (trim57 at `nsub = 256`, recomputed on the same rows): T5″ empties 159 open boxes and
  touches 166 more. **The clip empties all 159 — none is lost — and 21 more**
  (17 at L1, 4 at L2; 15 in k5_11, 6 in k5_16). So

  > pin-clip ⊇ T5″ on this corpus, with a 13 % larger kill set and a 2.7× larger touched set
  > (455 vs 166).

  The 21 incremental full kills are the honest "new kills" figure, and — unlike the offline
  159 that A123's live shift found to be conflating *touched* with *emptied* — this count is
  computed with the two categories separated from the start.

  **Each of the 21 is sample-confirmed on its own** (`results/incremental_kills.json`):
  20,000 draws in the full box × tilt bin per node, **420,000 drawn → 420,000 tested → 0 hits**,
  every node clearing 10⁴ tested by itself. 17 are level 1, 4 level 2; 15 in k5_11, 6 in k5_16.
  Their T5″ surviving fractions run from 0.055 to 1.000 — i.e. several of them T5″ does not touch
  at all, so they are not near-misses of the trim, they are a different mechanism (multiple pins
  clipping different sides of the same box until nothing is left).

### The clipped box's own core

The clipped box has a smaller half-diagonal, so `caselp.Box.core()` on it is bigger: over the 349
touched boxes at `nsub = 1`, `a_new/a_old` runs 1.0007 – 1.2453, **median 1.0449** — the same shape
as A96's `a_tight_gain_on_trimmed_bin` for T5″. But re-running `pinguard.classify` with the tight
core on those enlarged cores gives **0 additional logic kills**. The clip already extracts
everything the pin geometry has to give on those boxes; there is no second harvest.

### A cheap independent read on the schedule assumption

The 900 s ALIVE re-check (A96 `recheck96` + A124 `recheck124`) has now processed **63** nodes
with a verdict, 27 of them certified dead, on the ORIGINAL boxes. Crossing that with the clip:

| clip outcome | n | certified dead at 900 s |
|---|---|---|
| EMPTY (the clip kills it for free) | 8 | 1 (12.5 %) |
| kept < 0.25 | 21 | 12 (57.1 %) |
| kept 0.25 – 0.5 | 3 | 2 (66.7 %) |
| kept 0.5 – 1.0 | 8 | 3 (37.5 %) |
| untouched (kept = 1) | 23 | 9 (39.1 %) |

Read carefully: this says **"clippable" correlates with "killable"** (57 % vs 39 % at the
extremes), not that clipping *causes* the kill — the LP here ran on the unclipped box. With
n = 21 vs 23 the difference is not significant. It is, however, the free half of the T3 question,
and it points the same way. Note also the single most expensive kill in the whole re-check —
`k5_11_interior_Y0546`, 2,179 s — is one the clip empties for nothing.

### The number that actually decides anything: the UNCLOSED population

Of the 1,744 open boxes, 1,137 already carry a certified PASS. The 607 that do **not** — 414
`ALIVE-at-LP` and 193 `FAIL` — are the campaign's real residue, and the clip bites on them far
harder than on the corpus as a whole:

| | n | share of the 607 |
|---|---|---|
| clipped EMPTY (logic kill, no LP, no certificate) | **132** | **21.8 %** |
| — of which T5″ alone would also empty | 112 | 18.5 % |
| — of which the clip is the only rule that empties | **20** | 3.3 % |
| narrowed and still alive | **292** | 48.1 % |
| untouched | 183 | 30.1 % |

The 132 split 74 `ALIVE` / 58 `FAIL`, and 63 / 57 / 6 / 6 by level 1–4. **They are open today only
because both T5′ and T5″ are pre-filters on newly emitted children** — lemmas.md T5′ is explicit
that "existing verdicts are not recomputed or overwritten", and A96's
`superseded_by_tight_core.jsonl` is the ledger of the same effect for the tight core. So there is a
**backlog**: a one-pass geometric sweep over the recorded open set closes 132 of 607 unclosed nodes
at zero LP cost, and 112 of those need only the trim that is already deployed. Against the 900 s
re-check's 27 certified kills for 8.11 CPU-h, this is 132 kills for minutes of pure geometry, and
the two sets barely overlap (1 node).

That sweep is the cheapest item this attempt found and it needs no deployment decision at all — it
is a *re-classification of recorded rows*, not a change to emission. It does need the same care
A96 took: write the superseding verdicts to a ledger with the prior verdict retained, do not
overwrite the tree files.

**The list is written out**: `results/backlog131.jsonl` (+ `backlog131.json`), one row per node with
its prior verdict, τ/η, box, the witness pins and whether T5″ alone would have sufficed. It
supersedes nothing — landing it is the campaign owner's call. 132 rows: 93 k5_11 / 39 k5_16,
63/57/6/6 by level, prior verdict 74 ALIVE / 58 FAIL. **111 are emptied by a SINGLE pin, 21 need
two pins jointly** — and that is precisely where the clip beats T5″, which only ever tests
single-pin domination of the whole box (20 of the 21 are clip-only; the odd one out is emptied by
T5″ using *different* pins on different tilt sub-intervals, which is the one thing T5″ can do that
a single-pin clip cannot, and another reason to keep both).

### The schedule consequence, and the assumption it rests on

> **Assumption (stated, per the brief).** The LP's kill rate on a clipped box equals the tree's
> measured kill rate at the corresponding *smaller* level: a box whose centre area has shrunk by
> `2^(−2f)` is priced as a node `f` levels deeper. This is the survivor-count rule's caveat —
> it is a projection, not a measurement, and T3 is the beginning of testing it.

Taking budget.md §B's KILL-BY-LOGIC share by level (29 % at L1 rising to 60 % at L4, interpolated
linearly at 10.33 points per level and capped at 60 %) and promoting each surviving box by its own
free levels:

| | outright EMPTIED | expected extra logic kills among survivors | total |
|---|---|---|---|
| nsub = 1 | 179 (10.26 %) | 31.9 (1.83 %) | **12.10 %** of open nodes |
| nsub = 8 | 180 (10.32 %) | 46.0 (2.64 %) | **12.96 %** of open nodes |

**What that does to the 11–13 wall-days.** budget.md §B prices a non-logic node at ~850 s (LP
240–400 s + exact verify 100 s + 4-D window verify 545 s at level 2) and a logic kill at ~0 s, so
converting a fraction `q` of nodes to logic kills removes `q` of the *node* cost outright, and the
alive ones among them remove their eight children too. On the A57 row (1,300 CPU-h central,
11–13 wall-days at 5 workers):

* the **incremental** part over what is already deployed is what matters. T5′ and T5″ are both ON
  (`pinguard.TIGHT_CORE = True`, `trim57.TRIM = True`), so of the 12.96 % only
  **21/1,744 = 1.20 % is new outright killing** plus the 2.64 % of *modelled* promotion. Call it
  **3.8 % of nodes**, i.e. ≈ 50 CPU-h, ≈ **0.4 wall-days** off 11–13. That is the honest headline
  and it is small.
* the number that is *not* small is the **26 % touched**: those nodes keep a box a median 0.71
  levels smaller for free, which under the assumption is worth another ~1 % of nodes but, more to
  the point, is the LP-tractability effect A123 measured for T5″ ("trimming buys LP tractability,
  not kills") and A124's re-check converted into kills at a 900 s cap (11 of 23, 47.8 %). **If the
  clip behaves like the trim, its value is realised through the re-check, not through emission** —
  and that is exactly what T3 measures.
* the L4 row is the one to watch for termination: 12 of 14 level-4 boxes clip to EMPTY, and the
  two survivors keep 1 % of their area (5.4 free levels). budget.md's tail measurement
  ("level-4 descent 0 of 30") is reinforced, not changed.

**Caveat carried forward from A123/A124.** The offline projection for T5″ was 3.70 % incremental
and the live fire rate was 1.01 %. Nothing here is immune to the same gap: this is an offline sweep
over boxes that already exist, and a deployed clip acts on children as they are emitted, whose
population is not identical. The one thing that *is* directly comparable is the domination result
(clip ⊇ T5″, 0 lost), which is geometry and does not depend on the population.
