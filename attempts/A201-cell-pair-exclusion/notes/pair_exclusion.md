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

## 3. Results

(filled in below from `results/pairexcl201.jsonl` and `certs/pe201_*.json`)
