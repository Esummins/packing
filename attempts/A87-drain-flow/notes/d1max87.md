# A87 chore `d1max87` — do LOCKED DEEP JAMS occur in anchored configurations?

PI target: a lemma bounding the DEEPER intruder's depth `d1` at a corner from ABOVE.  Mechanism =
Lemma JAM-0 (`docs/proofs/tilt_floor_k0.md` §5.1) read backwards.  For an axis-aligned deeper
intruder `Q = [a,a+1] x [b,b+1]`, `depth(Q) = 1 - g` exactly with `g = max(a,b)`, so

    d1 > 1 - g*   <=>   g < g*   ==>   sin(tilt of partner N) <= g,  depth(N) <= g^2/sqrt(1-g^2).

A deep intruder therefore CONFINES its partner to a `g*`-sliver and forces it near-flush; by
A89-G1 / §5.2 such a near-flush partner is flush-LOCKED only in the `K > 0` branch, which needs
a **presser within `r <= eps` of the partner's top vertex `u`** PLUS a **side pusher** on its far
edge.  Code: `code/d1max87.py`.  Results: `results/d1max87.{json,jsonl,census.json,canary.json,log}`.

Canary (`results/d1max87.canary.json`): **PASS** — Trump's TL corner comes out at
`d1 = 0.16832099` (sq 6, tilt 40.18°), `d2 = 0.15547472` (sq 4, flush), corner ANCHORED, **not**
a deep jam.  TL is Trump's only corner with >= 2 intruders.

## Part A — the corner census

Corpora (187 configurations, 98 corners with >= 2 intruders, 0 errors):

| corpus | configs | corners >= 2 intruders |
| --- | ---: | ---: |
| `d2front87.json` candidates (anchored arm + raw arm) | 15 | 60 |
| `k0dir87.polish.jsonl` rows carrying an exact-K0-BLOCKED `z` | 4 | 16 |
| `cp87_fj_polished.jsonl` `survivor_tight` (the certified 167) | 167 | 21 |
| Trump exact | 1 | 1 |

`k0dir87.deep.jsonl` persists **no configuration vector** (only per-row scalars), so only the 4
polished exact-K0-BLOCKED `z`s from that arm could be measured.

**Anchoring is applied PER CORNER** (the 167 FJ points are K0-FREE, so `d2front87`'s global
`ANCHORED` predicate — which demands 8 intruders — cannot fire on them):

    corner_anchored := neither intruder is A90-RETREATABLE (t3_90.analyse_square, verbatim)
                       AND the shallower has no constant-side rotation toward flush that
                       reduces its depth (d2front87.rot_toward_flush_free, verbatim).

22 of the 98 corners are anchored (17 d2front87, 4 k0dir87.polish, 1 Trump; **0 of the 21 FJ
two-intruder corners** — every FJ crowd has a retreatable member or a free flush-ward rotation).
Only 2 configurations are globally ANCHORED in `d2front87`'s sense, both from its anchored arm.

### Joint distribution of `(d1, partner tilt)` over the 22 ANCHORED corners

| `d1` \\ partner tilt | flush (0) | (1e-7, 0.1°) | [0.1°, 1°) | [1°, 6°) | [6°, 15°) | [15°, 45°] |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| [0, 0.1) | | 2 | | | | |
| [0.1, 0.2) | 1 | | | | | |
| [0.2, 0.3) | | | | | 1 | 6 |
| [0.3, 0.5) | | | | 1 | 1 | 4 |
| [0.5, 0.7) | | 3 | | | 1 | |
| [0.9, 0.99) | | 1 | 1 | | | |

The distribution is **bimodal and exactly as JAM-0 predicts**: mid-depth corners (`d1` 0.2–0.5)
carry strongly tilted partners (15–45°), and every corner with `d1 >= 0.5` has a partner at tilt
< 0.15°.  Not one anchored corner has both `d1 >= 0.5` and a partner above 0.15° tilt.
JAM-0's bound is never violated in the whole corpus: 93/98 rows satisfy the tilt clause at
`g = 1 - d1`, 98/98 the depth clause, and of the 9 rows whose deeper intruder is literally
axis-aligned (so JAM-0 applies as stated) **0 violate it**.

### Headline — the maximum anchored `d1` with a near-flush partner

Qualifying corner := anchored + deeper intruder NOT retreatable + partner tilt < 6°.
**9 such corners in 6 configurations.**

| source / tag | corner | sigma | d1 | d2 | tilt D | tilt P | presser? | side pusher? | external sq |
| --- | --- | ---: | ---: | ---: | ---: | ---: | :--- | :--- | :--- |
| `k0dir87.polish` s0076 | BR | 4.000004 | **0.947723** | 1.00e-04 | 0.1161° | 0.1161° | no | yes | 8, 10 |
| `k0dir87.polish` s0380 | BR | 4.000000 | **0.943224** | 1.98e-05 | 0.0202° | 0.0202° | no | yes | 9, 10 |
| `d2front87` anchored own-side | BR | 4.107107 | 0.590790 | 1.00e-04 | ~0 | 0.0140° | no | yes | 8 |
| `d2front87` anchored cap 4.6 | TL | 4.083735 | 0.581110 | 1.00e-04 | ~0 | 0.0137° | no | yes | 8 |
| `d2front87` anchored cap 4.6 | TL | 4.083736 | 0.581109 | 1.00e-04 | ~0 | 0.0138° | no | yes | 8 |
| `d2front87` raw cap 4.05 | BR | 4.037928 | 0.440246 | 3.72e-02 | 0 (AA) | 4.4041° | no | yes | 9, 10 |
| Trump | TL | 3.877084 | 0.168321 | 1.55e-01 | 40.18° | ~0 | no | yes | 7, 9 |
| `k0dir87.polish` s0380 | TL | 4.000007 | 0.000445 | 1.00e-04 | 0.0054° | 0.0057° | no | yes | 7, 8 |
| `k0dir87.polish` s0380 | TL | 4.000000 | 0.000352 | 2.98e-05 | 0.0202° | ~0 | no | yes | 1, 8 |

**max anchored `d1` with a retreat-blocked deeper and a near-flush partner = 0.9477231905**
(`k0dir87.polish` s0076, BR corner, sigma 4.000004060).  Second: 0.9432 (s0380, BR, sigma
4.0000001).  Max over ALL 98 rows (anchoring ignored) = 0.9757; max over anchored rows = 0.9477.

**Every one of the 9 sits at sigma >= 4.0000** except Trump's TL at `d1 = 0.168`.  The only
qualifying corner at `sigma <= s_hat` is Trump's, and it is not a deep jam.  Both `d1 > 0.9`
corners sit at `sigma = 4.0000001 / 4.000004` — on the packing barrier `d2front87` already
identified, above `s_hat = 3.877084` by 0.123.

### The §5.2 flush-lock menu is NEVER realised

`FLUSH_LOCK_MENU` := a pair contact on the partner within `eps = 0.05` of its top vertex `u`
with a pressing component > 0.1 (the §5.2 presser), AND a pair contact pushing the partner into
the wall it hugs (the §5.2 side pusher `K > 0`).

**0 of the 9 qualifying corners (and 0 of all 98 rows) satisfy it.**  Every qualifying corner has
the side pusher; **none has the presser**.  4 of the 9 have no pressing pair contact on the
partner at all; the closest a pressing contact ever comes to `u` is **0.1138** (`d2front87`
anchored own-side, BR) — more than twice `eps` — and in the two `d1 > 0.9` cases the partner's
only press is a flush kiss whose contact points are its own far-edge vertices at distance 1.000
and 1.414 from `u`.  Suppliers are uniformly `free_square` (a middle square that is not an
intruder at any corner and touches no container wall); one Trump/one k0dir row additionally uses
the corner's own deeper intruder.  **No `pin` and no `other_corner_intruder` ever supplies a
presser or side pusher.**

**Cost.** A qualifying corner consumes **1–2 external squares** (mean 1.67, max 2) — counting
distinct non-`{D,P}` squares that either supply the press/push or block the deeper intruder's
cardinal retreat clusters.

**Two such corners in one configuration: YES.**  2 configurations have >= 2 qualifying corners —
`d2front87/anchored_cap_4.600000` (2 corners, TL twice at `d1 = 0.581`) and
`k0dir87.polish/s0380` (**3 corners**: BR at `d1 = 0.943`, TL twice).  So multi-corner deep jams
do occur, but only at sigma ~ 4.0.

### A sharper test (`STRICT_3dof`) — and a gap in `d2front87`'s anchoring filter

`d2front87`'s anchoring tests (i) A90 cardinal CLUSTER translations and (ii) a pure rotation of
the shallower toward flush about one of its contacts.  Neither covers §5.2's own escape motion
(rotation about `u` COMBINED with a slide along the wall).  `d1max87` adds a superset: a 730-
direction probe over the full 3-dof rigid motion `(dx, dy, dtheta)` of the single square at three
step sizes, accepting any constant-side motion that strictly reduces the intruder's depth with
the whole packing feasible.

* The **deeper** intruder is 3-dof stuck in **all 9** qualifying corners.
* The **partner** is 3-dof FREE in **2** of them — both `d2front87` anchored cap-4.6 TL rows at
  `d1 = 0.581`.  Those two are ghosts that `d2front87`'s filter passed; the strict count of
  qualifying corners is **7**, and 16 (not 22) corners are anchored under the strict test.
* Both `d1 > 0.9` jams survive the strict test: at s0076/BR and s0380/BR the deeper AND the
  partner are locally immobile.  **The deep jam at sigma ~ 4.0 is real, not a ghost.**

### Reading for the PI

A lemma "`d1 <= 1 - g*` at the selected minimiser" cannot be had at `g* = 0.1` from the corpus:
two exact K0-BLOCKED anchored configurations realise `d1 = 0.9477` and `d1 = 0.9432` and survive
every retreat/lock/3-dof test applied here.  What the corpus DOES support is a much weaker,
side-dependent statement — every deep jam observed sits at `sigma >= 4.0000`, none below the
packing barrier and none in the window `[3.82, s_hat]` — which is exactly the same shape as
tilt_floor_k0's own remark that "all near-flush jams observed sit at sigma >= 4.0", i.e. still
GAP A89-G1 and not a local lemma.  The one genuinely new local fact is negative for the §5.2
worry: **the presser-within-eps-of-`u` half of the flush-lock menu is absent everywhere in the
corpus**, so if a lemma "a flush-locked near-flush corner blocker needs a presser within `eps` of
its top vertex" could be proved, it would kill every deep jam here — the side pusher alone is
always present and is never the binding half.

**Caveat.** `d2 = 1.0e-04` in most k0dir/d2front rows is the artificial depth floor `EPS_KEEP`
that `k0dir87`'s confined flow presses against, not a geometric optimum; the partner depths are
floor-limited, so `d2` in those rows should be read as "as shallow as the flow was allowed", and
the partner tilts (0.01–0.12°) as "as flush as the flow drove them".

## Part B — the pair census (`results/d1max87.census.json`)

A85's realisable surviving pairs: **7044** pairs over the **644** sound BL cover boxes
(`realise85.pairs.json` indexes the `sigma_closed_7` sound rows of `a85_reach_BL.json`).
Hypothesis under test: `d1 <= 0.9`, so `g* = 0.1`, JAM-0 tilt bound `arcsin(0.1) = 5.7391705°`,
JAM-0 depth bound `0.01005038`.

| depth bound used | boxes that can host `d1 >= 0.9` | pairs with a deep-capable member | pairs whose partner box lies ENTIRELY in JAM-0's tilt band |
| --- | ---: | ---: | ---: |
| A85 `depth_ub_wall` (wall-aware, sound) | 4 / 644 (0.62%) | 501 / 7044 (**7.11%**) | **0 (0.00%)** |
| A89 `t2b_depth` plain `depth_ub` | 10 / 644 (1.55%) | 704 / 7044 (9.99%) | **0 (0.00%)** |
| box depth LOWER bound (box FORCED to `d1 >= 0.9`) | 0 / 644 | 0 | 0 |

**The literal criterion answers 0.00%, and it is 0 for a granularity reason, not a geometric
one.** The cover's finest theta cell is `[0°, 7.125°]` (and its mirror `[82.875°, 90°]`), width
**7.1250°**, WIDER than JAM-0's 5.7392° band, so **no cell can lie entirely inside the band**:
`n_boxes_theta_range_entirely_within_jam0_tilt = 0` out of 644, while 128 boxes meet the band.
One bisection of those two extreme cells would make the clause able to bite.

The informative numbers at the current resolution:

* **JAM-0 alone already kills 393 of the 501** deep-capable pairs (**5.58% of the census**) —
  those whose partner cell misses the 5.74° band entirely and so cannot host the confined partner.
  (Plain bound: 556 of 704, 7.89%.)
* The remaining **108 pairs (1.53%)** survive with their partner cell merely SHAVED to the band.
* Total theta-measure removed from partner cells = **414.0 pair-equivalents = 5.88% of the
  census** (plain bound: 584.8 = 8.30%).
* JAM-0's DEPTH clause kills **0** additional pairs: no partner box of a deep-capable member is
  forced deeper than 0.01005.
* No box is FORCED to `d1 >= 0.9` (max box depth lower bound over the cover = 0.8090), so a
  `d1 <= 0.9` lemma can never delete a BOX outright — only shave it.

So: **a "`d1 <= 0.9` at the selected minimiser" lemma would delete 0.00% of A85's realisable pair
census as stated, and at most 5.6–5.9% of it once JAM-0's own tilt clause is charged to it** —
and only if the cover's two extreme theta cells are bisected first.  It is not a census-shrinking
lemma; its value would have to be structural (killing the deep-jam branch outright), and Part A
says the branch is non-empty above sigma 4.0.

## Provenance

* JAM-0 / §5.2: `docs/proofs/tilt_floor_k0.md` §5.1, §5.2, GAP A89-G1.
* RETREATABLE / clusters / LOCK / MENU: `attempts/A90-nocrit-blocked/code/t3_90.py`, verbatim.
* Anchoring filter (`rot_toward_flush_free`, `anchored_report`):
  `attempts/A87-drain-flow/code/d2front87.py`, verbatim.
* Box census: `attempts/A89-tilt-floor/code/t2b_reach.py` `load_boxes`,
  `attempts/A85-k0-route/results/realise85.{pairs,boxes}.json`.
* One process, `OMP_NUM_THREADS=1`, whole run 17 s.
