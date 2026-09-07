# A126 — what is now a Lean theorem, and exactly what is left

Companion to `notes/method.md`.  Every name below is in
`lean/PackingCertMathlib/PackingCertMathlib/`; the axiom audit is
`lean/PackingCertMathlib/scratch/A126Axioms.lean`.

## 1. Discharged

| was | now |
|---|---|
| `Local.sat_selection` — Lemma SAT for INTERIORS, A119's ONE project axiom | `SatInterior.sat_selection_thm`, a THEOREM (propext / Classical.choice / Quot.sound only) |
| `Local.cover_pair` (used the axiom) | `SatInterior.cover_pair'`, same statement, axiom-free |
| 2 302 (resp. 32 570) `linarith` calls, one per closed leaf, none of which A119 could afford to emit | ONE `native_decide` on `LocalCert.checkLeaf`, proved sound once (`LocalCert.checkLeaf_sound`) |

`sat_selection_thm` needs no limit and no subsequence.  With all eight gaps `< 0` the four
projection overlaps of `CaseSat.sat_squares` hold STRICTLY with the same right-hand side
`B = 1/2 + (|cos Δ| + |sin Δ|)/2`; put `M` = the max of the four left-hand sides and
`λ = (M/B + 1)/2 ∈ (M/B, 1)`, apply `sat_squares` to the picture scaled by `1/λ`, and scale the
conclusion back: every coordinate of the common point is `≤ λ/2 < 1/2` in absolute value, i.e.
strictly inside, and `Attain.mem_interior_iff_uv` turns that into a common INTERIOR point.  The
`cos Δ < 0` case is the `u ↦ −u` representation of the same square.

## 2. The one obligation of T1 — `LocalCert.CertCover`

```lean
def CertCover (leaves : List CLeaf) (Ls : List Box) (Ps : List Pin) (s0 : ℝ) : Prop :=
  ∀ s : ℝ, ∀ z : Cfg, s ≤ s0 → CfgPacking s z → LocalHyp Ls Ps s z →
    ∃ x : Nat → ℝ, x 0 = s ∧ ∃ L ∈ leaves, LeafHolds L x
```

"every packing that satisfies `N` at a side `≤ s0` has an LP variable vector that lies in the
box of ONE recorded leaf and satisfies that leaf's rows".  Given it, `localDead_of_cert` is four
lines.  It factors into four pieces; the first is proved, the fourth is bookkeeping, and the two
in the middle share ONE missing primitive.

**(C1) the tilt cover — PROVED in shape.**  A `bisect` node splits one body's tilt interval at a
recorded interior point and its two children carry `[lo, mid]`, `[mid, hi]`; their union is the
parent by `Local.cover_bisect` (`le_total`).  The tree's structural well-formedness (the
recorded `lo`/`mid`/`hi` really are the parent cell and `lo ≤ mid ≤ hi`) is a decidable check on
rational data.  S07 (0.1, 40°): 2 410 bisections, no `qsplit` node anywhere in any of A119's
seven certificates.

**(C2) the selection cover — needs one enclosure.**  A `branch` node on a near pair keeps a
sublist of the eight signed selections and asserts that every OTHER one is impossible on the
cell.  The logical step is now a theorem: `SatInterior.sat_selection_thm` says an
interior-disjoint pair HAS a selection with `g_σ ≥ 0`, and `Local.cover_selection` removes the
excluded ones.  What is missing is the arithmetic content of "excluded": that
`sup_cell g_σ < 0`, which A119's checker gets from
`gap_enclosure` = an interval enclosure of `ε (c_o − c_w)·a_k(θ_w) − 1/2 − w(θ_w − θ_o)/2` over
the cell.  Counts for S07 (0.1, 40°): 2 969 excluded selections at 87 branch nodes, 292
`imp_sel` leaves, 761 forced selections at dead leaves.

**(C3) Lemma RELAX — needs the same enclosure.**  Each recorded row is an affine relaxation of a
selection row over the tilt cell.  The pieces are already THEOREMS in `Local.lean`
(`axis_decomp`, `mccormick_hi/lo`, `abs_chord`, `chord_of_concave`, `abs_sin_le_sin`,
`cos_ge_of_abs_le`); what is missing is that the RATIONAL constants the generator put in the row
(the midpoint axis `a_k(θ*)`, the correction `(1 − cos h_w)`, the `sin h_w` factor, the chord of
`w = |cos| + |sin|` over the cell with its `π/2`-kink) really do bound the corresponding real
quantities.

**(C4) the variable map — bookkeeping.**  `LocalHyp` gives injections `wL`, `wP`; the variable
vector is `x 0 = s`, `x_{vi} = ` the centre of the free body / the pin's offset from
`(α + β s)`, `x_{ti} = ` the free body's tilt ANGLE.  Nothing mathematical, but it is the step
where the certificate's own body numbering has to be written down.

### The missing primitive, named

**A certified rational-interval kernel for `cos`, `sin` and `π` — A119's `code/exactiv.py`
(`Fx`, dyadic integers at scale `2⁻⁹⁶`, exact `cos_iv` / `sin_iv` / `w_iv` ranges over a
rational angle interval), in Lean.**  Both (C2) and (C3) reduce to it, and nothing else in the
certificate does.  Mathlib supplies `Real.pi_gt_3141592` / `Real.pi_lt_3141593` and the
low-order `Real.cos_bound` / `Real.sin_bound`; the 10⁻⁹-level accuracy the certificates use
needs higher-order Taylor bounds with explicit remainders, plus the argument reduction and the
`π/2`-kink location that `exactiv.kink_in` performs.  A119's finding F4 is the warning: the
kernel must reproduce the generator's SHARPNESS, not merely be sound, or a `branch` node whose
root cell is 80° wide is rejected.

### The cheaper route, and it is a generator change, not a Lean one

The certificate's tilt variables are ANGLES `θ`.  Lean's own parametrisation is
`t = tan(θ/2)`, in which

    cos θ = (1 − t²)/(1 + t²),   sin θ = 2t/(1 + t²)

are RATIONAL functions with no transcendental content at all: `Parametrize.cosT` / `sinT`, and
`cosT_sq_add_sinT_sq` is proved for EVERY real `t`.  A certificate emitted in `t` would make
every enclosure in (C2) exact rational arithmetic and every constant in (C3) a rational number,
and the trig kernel would leave the trusted base entirely.  The cost is on the generator side:
the relaxation would have to be redone in `t` (the axis components are no longer affine in the
cell parameter, so `axis_decomp` + McCormick would be replaced by a rational-function
relaxation), and every LP re-solved.  This is the recommended next step for anyone who wants
`LocalDead` for a concrete `N` with NO named obligation.

## 3. T3 — what remains between "dead in the ledger" and "dead in Lean"

`LocalCompose.y0230_dead` is A120's closure of `k5_11_interior_Y0230` as a Lean statement.  Its
hypotheses, and their status:

| hypothesis | content | status |
|---|---|---|
| `hD` | `LocalDead` for `N = S02_k5_11_r0.20_rho10` | `LocalCertS02.localDead_s02`, modulo `CertCover` (§2) |
| `hdisj` | A120 **A2**: the four mapped boxes are pairwise pose-disjoint | a finite rational interval test; `decide`-able, not yet written |
| `hsep` | A120 **A3**: each mapped box is pose-disjoint from every pin | same |
| `hpins` | the node's own class hypothesis: the five pins are occupied by five distinct squares, in the node frame (A120 **A1** + **A4**, the `D4` map and its exact inverse) | not written; this is `ContainsPins` transported through `d4Cfg`, the same step `Composition.classKilledAt_of_tree` already performs for the tree route.  **A1 itself checks out exactly**: the six cores of every `Y0230` NO certificate are, as EXACT rationals at `s0`, `(1/2, 1/2)`, `(1/2, 3/2)`, `(1/2, 844271/250000)`, `(3/2, 1/2)`, `(844271/250000, 1/2)` — A119's five pins `BL(0,0)`, `BL(0,1)`, `TL(0,0)`, `BL(1,0)`, `BR(0,0)` — plus `(3737327/2000000, 3178299/2000000)` at tilt half-width `13/16`, the node's own conditioned square.  Core half-side `16056319934464/32768001953125 ≈ 0.48999 < 1/2 − δ/√2 = 0.49293`, so a square whose centre is inside the slack core does contain the core, which is `checkCaseI_no_family`'s `hown` |
| `hno` | the four NO children are empty | see below |

The NO side, in detail.  A120's four PASSing certificates for `Y0230` are `NO0`, `NO1_r6`,
`NO2`, `NO3` (`NO1` itself FAILs and was re-priced); each is a
`case-measure-certificate-v1` at `s = 969271/250000`, depth 56, with **6 cores** (the node's five
class pins plus its own conditioned square) and **one NO-family zone** (the corresponding box of
`N`, mapped into the node frame and clamped to the wall slab).  `lean/gen_case_lean.py` converts
them and `LocalCertY0230.check_y0230_no{0,1,2,3}` replays all four by `native_decide` — the A78
route, and the harness exists.  Two steps still separate that from `hno`:

1. **`checkCaseI_no_family`, not `checkCaseI_kill`.**  The zone list is NONEMPTY, so the PASS
   proves "SOME non-owner square of the family lies in the zone", which is exactly the negation
   of the NO child — but it is stated for an `IsStrictFamily` (pairwise disjoint CLOSED squares)
   whereas `CfgPacking` gives interior-disjointness.  `Dilation.lean`'s Lemma B (the
   `λ`-dilation at a slightly smaller side) is the existing bridge and has to be applied.
2. **pose vs. set.**  `CaseExempt` says some `q` with `q.set = Q i` is in the zone; `NoneIn`
   speaks of the pose `z k`.  `q.set = (z k).set` does not force `q = z k` (`t = 0` and `t = 1`
   denote the same square — Parametrize's findings F8), so the last step needs the pose
   normalisation that `Census.mem_interior_d4Sq_set_iff` and `exists_nonneg_dir` already carry.

`LocalCompose.centre_in_slab` and `LocalCompose.noneIn_of_clamped` close the third gap A120
worried about: a NO child certified against the CLAMPED zone kills the branch of the UNCLAMPED
box, because a packed square's centre is at least `1/2` from every wall
(`wT_ge_one` + `set_subset_container_iff`).  So the CLAMP costs nothing.

Both remaining NO-side steps are pre-existing properties of the frozen fixed-side route
(every `checkCaseI` consumer in the repo has them), not new debts of this attempt.

## 4. Finding F-COVER — the emitted NO zone is the YES box rounded the WRONG WAY

`code/zonecheck126.py`, run on **all four of A120's CLOSED nodes and all 17 of their PASSing NO
certificates** (`results/zonecheck.txt`).

The split `H = YES ∪ ⋃_i NO_i` is a tautology **iff `ZONE_i ⊆ BOX_i` as pose sets**: a
configuration that fails the YES side fails it because NO square is in `BOX_i`, and to land in
`NO_i` it must then have no square in `ZONE_i` either.  A120's runner builds the zone EXACTLY
and records it at full precision in `results/nodes/<child>.json` (`hyp.nofams`, with the box's
own θ-interval in degrees) — its `box_identical_to_yes` guard checks precisely that.  The
rounding happens when the `case-measure-certificate-v1` file is written, and it is OUTWARD.
Comparing the CERTIFICATE against A120's own RECORD isolates exactly that step and is
independent of the node's `D4` frame map:

| | outside the recorded box by |
|---|---|
| tilt ends (`t = tan(θ/2)`, rounded out to `2⁻²⁰` / `2⁻²³`) | `9.0·10⁻⁸` … `1.10·10⁻⁷`, on EVERY one of the 17 |
| upper centre bounds (9 decimals, NEAREST) | up to `4.71·10⁻¹⁰`, on 13 of the 17 |
| lower centre bounds | never (nearest rounding happens to move them inward) |

`NO0`'s tilt is the clearest instance: `2924103/8388608 = 0.348580241` against
`tan(38.4351°/2) = 0.348580331`.  Outward is the right direction for the VERIFIER — a wider NO
zone exempts more boxes, and that is justified because the hypothesis it is proved under is
correspondingly stronger — and it is the wrong direction for the COVER.

Consequence, stated exactly and no more: the split is **not a tautology as certified**.  A
configuration whose only square near `F_i` sits in `ZONE_i \ BOX_i` satisfies neither the YES
side nor `NO_i`, and the argument places it in no branch — it might still happen to fail some
other `A_j^ZONE`, but nothing shows it does.  The sliver is `≤ 1.10·10⁻⁷` wide in tilt and
`≤ 4.71·10⁻¹⁰` in the upper centre coordinates, on every one of A120's four closed nodes.
Whether any packing actually lives there is a separate question and is not checked here; what is
established is that the COVER argument has a hole of that size.  Nothing in A120's LP or measure
work is wrong; the tautology is.

**The fix is one rounding direction, and it is cheap.**  Emit the NO zone INWARD (lower bounds
up, upper bounds down, tilt interval narrowed).  That makes the NO hypothesis WEAKER, so the
children have to be re-certified — but by `10⁻⁷` in tilt, orders of magnitude below the
resolution at which those certificates pass, so a re-run should be a formality.  Widening the
YES box instead is NOT an option: the YES kill is A119's certificate for `N`, and `N`'s boxes
are what they are.

`NO3` also confirms that A120 handles finding E3 correctly on its side: its zone carries TWO
`t`-intervals, `[tan 40°, 1]` and `[0, tan 5°]`, i.e. the `θ ∈ [−10°, +10°]` cell folded into
the fundamental domain.  It is `Local.Box`, with its single interval, that cannot say this.
