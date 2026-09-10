# A201 -- cell-pair mutual exclusion in the assignment count (the PI's reading, 2026-09-10)

Credit: **"cell-pair mutual exclusion"** is the PI's reading of `quick200_fast_k5_16_interior_Y0044.svg`
(2026-09-10 15:20): *"because of the chord limitation on the right wall, sections 21/22/23 can only have one
centre TOTAL, which means 21/22 isn't a valid centre pair for BR(0,1), and similar logic applies to TR(0,1).
That type of mutual exclusion kills a lot of the possible configurations."*  A198/A200's count treated two
option rows as compatible whenever Lemma A1 allowed it; this note states the rule that the count now enforces,
for any n, and reports what it killed.

## 1. The lemma (any n)

Setting = A198's `notes/fastprop.md` (Theorem COUNT): a page node at side s with pins P_1..P_k (axis-aligned
stock boxes), fixed roles R (the conditioned square H, instantiated meeters F_j) with certified K'(R), and
n - k - |R| anonymous free squares; forced cells p_1..p_m (Theorem FC, `docs/proofs/forced_corners.md`) each
needing TWO distinct non-pin meeters of its widened open box B_p+.  A grid of closed cells g of side < 1/sqrt2
covers the centre range; Reach(g, S) is the set of (centre rect x tilt sub-bin) pieces of cell g not proved
dead by the container clip, the exact dead test against every K'(R) and the pins, the MISS test for every
p in S and (at corner slots) the lonely clip -- a superset of the poses of any anonymous square with centre in
g meeting every B_p+, p in S.  Option rows: (g, S) with Reach(g, S) non-empty; a fixed role's rows (R, g, S)
likewise on its normalised pieces.

**[T] Theorem COUNT-PAIR.**  Let X_1 = (who_1, g_1, S_1) and X_2 = (who_2, g_2, S_2) be two rows of the option
table with piece sets P_1, P_2 (X_i's own surviving pieces) and centre hulls h_1 = hull(P_1), h_2 = hull(P_2).
In every packing of the page in which two DISTINCT squares realise X_1 and X_2, their poses z_1 in P_1 and
z_2 in P_2 satisfy

  (a) ||c(z_1) - c(z_2)||_inf >= 1/sqrt2  (Lemma A1, `sideband.md` s.2, Lean `linf_sep`);
  (b) ||c(z_1) - c(z_2)||_2   >= 1        (Lemma CN, A153, `residue_ledger.md` s.1: the open inscribed discs of
                                           radius 1/2 of interior-disjoint unit squares are disjoint);
  (c) z_1 is not in the dead set of P_1 against K'(P_2), where K'(P) = the intersection over z in P of the closed
      unit square at z (A171/A172: `MBox.rebuild(kmode="pieces")`, certified), and symmetrically -- because a
      square at z_1 meeting int K'(P_2) meets the interior of the square at z_2 (K'(P_2) is a subset of the
      square at z_2), contradicting interior-disjointness.  Iterating the clip (z_1 survives against K' of the
      survivors of P_2, and so on) keeps z_1, z_2 at every pass.

Hence the pair (X_1, X_2) is EXCLUDED from every cover of the count -- i.e. no assignment of Theorem COUNT may
use both rows for two distinct squares -- as soon as ONE of the following is PROVED:
  (a') max over the hulls of the l-inf centre distance < 1/sqrt2 (A198's `a1_compatible`, unchanged);
  (b') max over the hulls of the Euclidean centre distance < 1 (attained at hull corners: sqrt(dx_max^2 +
       dy_max^2) with dx_max = max(x1_1 - x0_2, x1_2 - x0_1), exact in Fractions);
  (c') the seeded two-box mutual clip (`code/pairclip201.py`) empties one side: every piece of P_1 is dead
       against K'(P_2') for the current survivors P_2' (or symmetrically), at some pass.
Theorem COUNT with (a')-(c') as the pairwise test in place of (a') alone is Theorem COUNT-PAIR: **if the exact
search over the option table finds no assignment satisfying COUNT's (b)-(d) with every chosen pair
COMPATIBLE, the page is DEAD.**  Sound direction only: an exclusion needs a proof, compatibility needs none;
an untested pair (time budget) is compatible.  Same-cell pairs: the count never places two squares in one
closed cell (A1); the cells' Euclidean diameter (0.814 on k5_16's 0.575 grid) is < 1, so CN says the same.
The K' of (c') is built on COARSENED pieces (one hull piece per initial tilt quarter): a hull piece contains
its fine pieces, so its K' is a subset of theirs and the intersection is a sound, slightly smaller K'.  The
pieces P_i are the reach survivors, so the container, the pins' stock boxes and every role's K' are already
in them; the clip adds only the pair's own mutual exclusion, which is exactly what was missing.

The three rules nest as tests of the same statement: (a') and (b') read the hulls only (milliseconds); (c')
reads the pieces with their tilts (0.3-3 s per pair on Y0044).  (c') is tried on the CELL pair first (the
union over slots of the two cells' anonymous survivors: one exclusion covers every option pair of the two
cells, the PI's "21/22/23 can only have one centre total"), then on the option pair.

## 2. What was implemented (`code/`)

* `pairtab201.py` -- `PairTable`: the per-round table, lazy, cached per unordered pair; `compatible(k1, k2)`
  runs (a') -> (b') -> (c') and records every exclusion with its rule and numbers (hulls + max l-inf / max
  Euclidean distance; the clip's pass trace, kept fractions, seconds); `hits` = the exclusions the current
  search USED; `check_pairs` runs a prior witness cover (A200's) through the table.
* `pairclip201.py` -- `pair_clip(P1, P2)`: the seeded mutual clip (A171 primitives read-only:
  `MBox.rebuild`, `obstacle("poly")`, `_clip_rect_obstacle`); `far_apart` skips hulls >= sqrt2 apart.
* `count201.py` -- A200's `count_search` with `table.compatible` as the pairwise test (one line changed).
* `quick201.py` -- `QPage201(quick200.QPage)`: A200's round with the table wired into every count (no-chord,
  chord, bar-H per slot); certificates keep A200's fields and add `pair_excl` (+ `witness_check` per round).
* `run201.py` / `run201.sh` -- the chain (g1 pad, then pad 0), ops rules (BLAS pinned, BelowNormal, affinity
  0xFFFF, lab ceiling 12 counted before every page, commit per page); `fig201.py` -- the page
  `docs/residue_map/pairexcl201_<nid>.svg` from the certificates (live200's drawing rules + the excluded
  witness pairs in red); `exp201.py` -- the pricing experiment.

## 3. Pricing rule (c) (`exp201.py`, `logs/exp201_y0044.log`, Y0044 at the g1 pad, 40 pairs the count reaches)

* The FULL multibox node {pins, H, hull(X1), hull(X2)} normalised at nsub 2 / refine 1 (the brief's first
  reading of (c)): **0 exclusions in 118 s** (2.9 s a pair) -- the box hulls forget the piece structure, and K'
  of a hull box is too small to clip anything.
* The SEEDED two-box clip on the rows' own pieces (`pairclip201`): **17 exclusions in 30 s** (0.75 s a pair;
  0.3-0.5 s on the PI's column pairs), among them EVERY 21|23 pair of the right-wall column the PI named --
  `(21, BR(0,1)) | (23, BR(0,1))`, `(21, BR(1,0)) | (23, TR(0,1))`, ... (16 of 16 tested): a centre in cell 21
  sits at y >= 1.5 (P3's stock box), one in cell 23 at y <= 2.377 (P4's), and every square of the first meets
  K' of the second -- Lemma CN alone says 1.049 >= 1 and cannot decide it.  21|22 and 22|23 are Lemma CN
  (max distance 0.927 / 0.9 < 1).  So the PI's "one centre total in 21/22/23" is exactly the three pairwise
  exclusions, two by CN and one by the exact clip.
* Where the budget goes: a lazy (c) inside the DFS (every pair the search touches, in search order) spent 180 s
  on 211 option pairs, excluded 11, and left 350 pairs undecided -- and the count then walked through an
  undecided pair.  The deployed design spends (c) on the CELL pairs first (80 near pairs of Y0044's 25 alive
  cells, 74 s, 15-22 excluded) and then ONLY on the pairs of the covers the count proposes (the
  witness-refutation loop): 7 covers refuted in 43 s, the 8th verified pair by pair, 0 pairs undecided.

## 4. Y0044 (k5_16_interior_Y0044): the witness cover dies, the page does not

| pad | A200 fast steps | A201 steps (s) | A200's witness cover | page |
|---|---|---|---|---|
| g1 | 210 s, ALIVE | normalise 3.4 > options 80 > union 0.3 > pair-cells 74 (80 pairs, 15 excl) > count 43 (7 covers refuted, 8th VERIFIED) > normalise 4.4 > options 74 > union 0.3 > pair-cells 65 (54 pairs, 12 excl) > count 51 (8 refuted, 9th VERIFIED); 401 s | **DEAD**: 16\|17 by **CN** (max centre distance 0.836 < 1: the coordinator's number), 17\|18 by **EXACT** (option pair, X2 empties in pass 1), 18\|14 by **EXACT** | **ALIVE** -- a verified cover exists |
| 0 | 210 s, ALIVE | the same steps; 444 s | **DEAD**: the same three pairs | **ALIVE** -- a verified cover exists |

The verified cover at the g1 pad (every pair passes (a) (b) (c)): H at cell 11 -> BL(1,0); F1 at cell 5 ->
BL(1,0)+BR(1,0); anonymous squares at cell 16 -> BR(0,1)+BR(1,0), cell 18 -> BR(0,1)+TR(0,1), cell 8 ->
TL(1,0)+TR(1,0), cell 14 -> TL(1,0)+TR(0,1)+TR(1,0).  Exclusions found per round: A1 124 / CN 85 / EXACT 10
(round 1), A1 36 / CN 42 / EXACT 12 (round 2); the count used 218 of them (round 1).  "Verified" means no
rule excludes any of its 15 pairs -- not that a packing realises it (the test is one-sided).

## 5. The table over A200's fast-phase certificates

(`code/report201.py`; every A200 certificate ALIVE at the g1 pad, run through the chain g1 -> pad 0)
