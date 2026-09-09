# A167 — the CONDITIONAL chord-limited lane: the per-piece form, its levers, its checker

Written 2026-09-08 (A167, Opus). Status as A161's leaf: a GEOMETRIC leaf on the A57/A60 node tree
with a kill certificate and an independent checker, pending Lean. Nothing is deployed into a frozen
verifier. A118-O1 (exact-pin caveat) is inherited verbatim from A161 `notes/leaf.md` sec 5b.

---

## 1. The leaf

Setting as A161 sec 1: a node `N` of a pinned class `S` (five pins plus `L` conditioned squares) at
side window `[m_lo, s0]`, `s0 = 969271/250000`; `C = [i, i+1] x [j, j+1]` a USABLE, WALL-ADJACENT
slot cell in the cell's corner frame (A118 `lane.cframe_boxes`, hulled over `m`); `B_H` the box of
the single conditioned square (`L = 1`, which is the whole population here).

Let `B_1, ..., B_N` be a COMPLETE binary subdivision of `B_H` under A141's deterministic
`split_box` (widest of `x`, `y`, `theta/60`), so the true pose of `H` lies in exactly one piece.
For a piece `b`, with `K'(b) ⊇ K'(B_H)` its own — strictly fatter — polygon core as the obstacle,
and with ONE wall guard line `l(b)` chosen for that piece:

    beta(b)      = floor( s0 - minchord(b, l) - SUM_{j != H} minchord(B_j, l) )    [A144 LINE-1/2]
    m(b)         = 0 if EVERY pose of b misses int C (exact SAT), else 1
    LANE_out(b)  = max # of pairwise interior-disjoint FREE squares whose pose meets int C, avoids
                   every core, and has chord < 1 on l          [cover with the `band` prune]
    LANE_band(b) = the same with chord >= 1 on l               [cover with the `not_band` prune,
                                                                run over the BAND SLAB only]
    n(b)         = beta(b) + LANE_out(b)                              if m(b) = 0
                 = min(beta(b), LANE_band(b)) + LANE_out(b) + 1       if m(b) = 1

**LEMMA CCL.** If `n(b) <= 1` for EVERY piece `b`, then at most one non-pin square meets `int C` in
every realisation, contradicting SLOT-CROWD (A94/A109: at a usable slot at least TWO non-pin squares
meet `int C`, else the single meeter snaps into the slot and the packing lands in the certified-dead
extension class). The node is DEAD.

*Proof.* The pieces tile `B_H`, so fix the piece `b` containing `H`'s pose and run A161's LEMMA CL
count with `K'(b)` in place of `K'(B_H)` and `l(b)` in place of `l`: the non-pin meeters of `int C`
split into `H` itself (contributing `m(b)`, since a piece with `m(b) = 0` has no pose meeting
`int C`), the free BAND meeters, and the free OUTSIDE meeters. The band half is capped BOTH by the
chord row (`beta(b)`) and by the band cover (`LANE_band(b)`), so by their minimum; the outside half
by `LANE_out(b)`. ∎

Three differences from A161's unconditional form, each sound on its own:

1. **Per-piece line.** The band/outside partition, `beta`, and both covers all use the SAME line on
   a given piece; different pieces may use different lines because a realisation is scored only by
   its own piece. (A161 T8 used one global line.)
2. **Per-piece `beta`.** `minchord` is monotone under box inclusion, so putting the PIECE's box in
   the guard row instead of `B_H` is a sound tightening — `H`'s true pose really is in `b`. This is
   what turns `beta = 1` into `beta = 0` on pieces where `H` sits deep in the wall lane, and then
   `min(beta, LANE_band) = 0` with NO band cover at all.
3. **Band-slab root.** `chord >= 1 <=> |v| <= f(y) = (y + 1 - y^2)/2` with `y = |cos| + |sin| in
   [1, sqrt2]` and `f` DECREASING there, so every band pose has `|v| <= f(1) = 1/2`. Hence the
   `LANE_band` cover may be run over `centre_window(C) n { |off - c_perp| <= 1/2 }`: the poses
   dropped are all OUTSIDE poses, which `LANE_out` counts. (Emitted `SLAB_EPS = 1e-9` wide so the
   checker's exact containment test passes.)

## 2. What the measurement says (the operational lever)

A161 found "which guard line, not how long". A167's diagnostics
(`logs/diag_y0169_d3.log`, `d4`, `d5`) sharpen that to something schedulable:

* a cover that CLOSES closes in **0.6–1.2 s**; a cover that does not grinds for as long as it is
  given (measured to 40,000 boxes in A161). So each offset gets a SHORT hard slice (`--offs 2 s`)
  and BREADTH over offsets buys the kills; one phase-2 long slice (`--longs 12 s`) is spent on the
  offset that got closest (fewest boxes left open).
* **the viability screen is the big win.** A sampled FREE pose meeting `int C` (free = avoiding every
  `K'`, the fattened piece core included) is a realisation of the lane quantity it belongs to, i.e.
  a hard lower bound — A159's C8 witness rule. An offset whose sample already forces `n(b) >= 2`
  (`outside_free > 0`, or `band_free > 0` with `beta >= 1`, or `beta >= 2`) can NEVER produce a kill,
  so no cover is run on it. That screen costs one pose pool per piece (~0.3 s) and removes
  50–100 of the ~106 swept offsets on the hard pieces; without it those pieces burned 20–30 s each.
* consequently the split can start DEEP: `--predepth 3` (8 pieces) with `--splitdepth 5`, and the
  no-go pieces are recognised in ~0.3 s.

## 3. Verdicts (and what each one is a statement about)

| verdict | statement |
|---|---|
| `KILL` | every piece closed: `n(b) <= 1` on all of `B_H`. The node is DEAD (certificate). |
| `NO-GO-witness` | on some piece, EVERY swept offset is screened out by a sampled free meeter. This is a statement about the LEAF, not the node: the leaf's own counters are `>= 2` there at the split depth reached, so this cell cannot kill this node by this route. |
| `UNDECIDED-time` | the 60 s cell budget expired with covers unresolved. |

A `NO-GO-witness` cell can be escalated to a RETIREMENT of the cell for the whole lane family by an
EXACT two-crowd witness (`code/witness167.py`, certificate `nogo_two_crowd_v1`): two unit squares,
rationalised onto a `1/10^6` grid so every vertex is an exact rational, with

    (W1) both inside [0, s0]^2      (W2) both meeting int C       (W3) interiors DISJOINT
    (W4) each clear of all five class pins        (W5) one of them a legal pose of `H` (in `B_H`)

all five decided by the separating-axis test over the two polygons' edge normals, which is COMPLETE
for convex polygons. Such a pair makes SLOT-CROWD's `>= 2` satisfiable within the constraints any
lane-family counter is built from, so no leaf of the family can fire at that cell — A159's C8 rule
in exact arithmetic. Note the difference from `NO-GO-witness`: the screen's free pose need only avoid
the CORES, so it forces the leaf's counter up without exhibiting an interior-disjoint pair.

## 4. The certificate `conditional_chord_limited_lane_v1`

`certs/cond_<nid>__<slot>.json`, SHA-256 in the result rows. Fields as A161's
`chord_limited_lane_v1` (`s`, `nid/src/cls/level`, `slot/corner/ij/cell`, `cell_kind`, `extension` +
`extension_window`, `frame`, `m_lo`, `n_pins`, `cond_index`, `hyp_boxes`, `split_rule`), plus

* `split_root` — `B_H`, the root of the tautologous subdivision;
* `pieces[]` — one entry per piece: `path`, `box`, `m` (+ `misses_detail.axis`), `line`
  (`orient`, `off` as an exact rational), `beta`, `rhs`, `minchords`, `total`, and the two covers
  `out_cover` / `band_cover` as `{value, root, leaves[], open[]}` with A141's leaf `why` codes plus
  `not_band`;
* `band_rule`, `slab_eps`, `sample_lines[]` (per piece: drawn -> meeting -> band/outside -> free).

## 5. The independent checker `code/checkcond167.py`

Extends A161's `checkcl.py` (imported, and delegated to verbatim for a `chord_limited_lane_v1`
certificate); `checkcl` itself shares with the emitter ONLY A132's trusted `polycore.vertex_ok` and
A57's `caselp.Box/t_lo/t_hi`. Checks, in order:

    E1  leaf name, `s`, usable slot + declared extension + FULL window, every hyp box holds a
        container-admissible pose, frame boxes re-derived from the node record (checkcl D1);
    E2  `split_root == hyp_boxes[cond_index]`, and the pieces' paths are a COMPLETE PREFIX CODE
        over it with every stored box equal to the box the split rule recomputes -- the pieces TILE
        `B_H`, so no realisation escapes;
    E3  each piece's guard line: an exact rational in (0, 1) with the cell's wall orientation;
    E4  each piece's `beta` RE-DERIVED by the five-point `minchord` from the other hypothesis boxes
        plus THE PIECE'S OWN box; the re-derived value is the one used in the arithmetic;
    E5  a piece declaring `m = 0` carries an exact separating axis for its own box vs the cell;
    E6  the `LANE_out` root CONTAINS `[X0 - sqrt2/2, X1 + sqrt2/2] n [1/2, s - 1/2] x [0, 90]`;
        leaves discharged only by `container` / `band` / `misses_cell` / `witness`;
    E7  the `LANE_band` root contains that window INTERSECTED with the slab `|off - c_perp| <= 1/2`;
        leaves discharged only by `container` / `not_band` / `misses_cell` / `witness`
        (`band` is illegal there, `not_band` illegal in `LANE_out`);
    E8  open sets: value 0 needs an EMPTY open list, value 1 needs every pair (diagonal included)
        certified always-overlapping;
    E9  per piece: `m = 0` => `beta + LANE_out <= 1`; `m = 1` => `LANE_out = 0` AND
        `min(beta, LANE_band) = 0`; a `chord-contradiction` piece is re-derived as
        `s - SUM minchord < 0` (that piece is EMPTY of realisations).

`not_band_holds` is re-implemented in the checker from the spec (`min |v| > f(cs_min)`, `f`
decreasing so `cs_min` gives the largest threshold and a LOWER bound of `cs_min` is safe).
The window containment tests allow `1e-12` for the emitter's float window arithmetic, the same slack
A141's own prunes use.

## 6. Lean shape (delta over A161 sec 5)

A161's roster stands (2 `Bool` checkers `checkBandBox` / `checkBoxMissesRect` with soundness, 1 glue
theorem `chord_limited_slot_crowd`, 3 supporting lemmas, 0 new axioms). A167 adds:

* `checkNotBandBox` + soundness (`min |v| > f(cs_min)` => every pose has chord `< 1`) — the mirror
  of `checkBandBox`, same route (`chordLen_eq` + `f` antitone + `y_range_of_tilt`);
* `band_subset_slab`: `1 <= chordLen a c θ l -> |off - c_perp| <= 1/2` — one line from
  `f(y) <= f(1) = 1/2`; this is what licenses the slab root;
* `minchord_mono`: `B' ⊆ B -> minchordVal B ≤ minchordVal B'` — the per-piece guard row (immediate
  from the definition as an infimum over the box);
* `cond_split_slot_crowd`: the glue over a complete subdivision — `∀ b ∈ pieces, n(b) ≤ 1` plus
  `pieces` tiling `B_H` gives `False`. Its proof is a case split on which piece contains `H`'s pose,
  then A161's `chord_limited_slot_crowd` on that piece with `m(b)` folded in.

Roster delta: 1 new `Bool` checker, 1 soundness theorem, 3 small lemmas, 1 glue theorem, 0 axioms.

## 7. n-general form

Unchanged from A161 sec 6, with one addition that is the actual content of this attempt: *the
conditioned squares' own parameter box is a legitimate case-split axis for the wall lane, and the
split pays twice — the piece's core is fatter (so it blocks the lane) AND the piece's chord in the
guard row is longer (so the wall lane is cheaper). For any `n` and any class with a wall row of
pins, the conditional wall-lane bound is therefore never worse than the unconditional one, and the
cost of using it is one pose-pool sample per piece.*
