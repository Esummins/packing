# A134 T2 — what `LocalCertT2.lean` proves, and the exact residue in front of `localDead_s07_t`

**Read with `attempts/A133-tan-half-emission/notes/lean.md` (which priced this work) and §9 of
`LocalCertT2.lean` (the same statement, in the file).**

## Stated plainly

The brief asked for `localDead_s07_t` / `localDead_s02_t` with no hypothesis beyond the
certificate data.  **That is NOT achieved.**  What is achieved is that **all three of A133's
remaining pieces (C2), (C3), (C4) are discharged as named theorems**, with the full axiom roster
`[propext, Classical.choice, Quot.sound]` and no `sorry`; what remains between them and
`certCover_s07` is assembly and data, of four named kinds, and **no missing library lemma**.

| A133's pricing | A134's outcome |
|---|---|
| (C2) the selection cover, ≈ 250 lines | `selectionOk` / `selectionOk_sound` — DONE |
| (C3) Lemma RELAX, ≈ 600 lines | the row-family soundness — `relax_wall`, `relax_selection` and its five ingredients — DONE; the reflected ROW BUILDER (`rowsOf`) and the quantisation step NOT written |
| (C4) the variable map, ≈ 120 lines | the geometric half (`localHyp_bodies`) DONE; the variable-INDEX map NOT written |
| assembly, ≈ 80 lines | NOT written |
| generator: emit the positivity certificates | DONE (T1), and one further gap found and closed |

A133's pricing was accurate about the mathematics and low about the plumbing: (C3)'s 600 lines
are the row BUILDER (a Lean twin of a 100-line Python class over ~20 LP variables, plus the
outward-quantisation bookkeeping), not the row justification, which is the part that had the
mathematical content and is now ~200 lines of proved lemmas.

## What each piece turned out to need

**(C2).**  The enclosure of `g_σ` over a cell.  In `t` every ingredient is exact, so the whole
computation is one rational interval evaluation:

* `cosI` / `sinI` are the ENDPOINT values (`LocalCertT.cosT_mem` / `sinT_mem`), zero enclosure
  error;
* the only widening is `IQ.mul`, the four corner products;
* the support width is bounded BELOW by `w = max(cos Δ + sin Δ, cos Δ − sin Δ)` — the two smooth
  branches, each bounded by interval arithmetic on `cosRel` / `sinRel`.  **This is where A119
  needed a rigorous `π`** (to locate the `π/2` kink of `w`); here `wrel_ge_add` / `wrel_ge_sub`
  are already theorems and the bound is sharp up to the interval widths, because the maximum of
  the two branches IS `w`.

Then `selection_cover` is `SatInterior.sat_selection_thm` plus a decidable membership test: the
selection Lemma SAT provides has `g_σ ≥ 0`, so it is not one of the excluded ones, so it is one of
the recorded ones.  `selectionOk` checks all eight, in both owner orientations (`PairBox.swap`).

**(C3).**  The selection row is `W_lb/2 + 1/2 − corr − P − U ≤ 0`, and the proof is one chain:

    1/2 + W_lb/2  ≤  1/2 + w/2  ≤  Proj  =  P·C + Q·S  ≤  (P + corr) + U.

`relax_selection` is that chain (`linarith` from five hypotheses).  Its ingredients:

* `axis_decomp_t` — `P·C + Q·S = ε d·a_k(θ_w)` with `C = cosRel(t_w, t*)` and
  `S = sRel(cos θ*, sin θ*)(t_w)`.  In the angle this is `Local.axis_decomp`, an addition
  formula; in `t` it is an ALGEBRAIC IDENTITY, one `linear_combination` against
  `cos² + sin² = 1`.  **No `arctan`, no angle, nowhere.**
* `one_sub_cosRel_le` + `corr_bound` — `P·C ≤ P + max(0, −P_lo)·K` from a certified
  `1 − C ≤ K` (the new `cPoly` certificate) and `C ≤ 1` (`cosRel_le_one`).
* `relax_U_A` / `relax_U_B1` / `relax_U_B2` — the three `Q·S` envelopes; (A) uses `absQ_chord`,
  which is `Local.abs_chord` with the denominator cleared, and (B1)/(B2) are McCormick with `S`
  replaced by the affine envelope on the side the multiplier's sign selects.
* `wrel_ge_plane` — `W_ε ≥ mw t_w + mo t_o + c` from the bivariate positivity certificate, plus
  `wrel_ge_sub` (`ε = +1`) or `wrel_ge_add` (`ε = −1`).

The wall rows are `relax_wall`, from `Parametrize.set_subset_container_iff` (`Q ⊆ [0,s]² ⟺
w_T(t)/2 ≤ c ≤ s − w_T(t)/2`) and the certified chord `wT_ge_aff`.

**(C4).**  `localHyp_bodies`: from `LocalHyp` + `CfgPacking`, one square per body indexed
`0 … |L|+|P|−1` in the certificate's body order, with box membership, slack-core membership,
`t ∈ [0,1]`, containment in `[0,s]²` and **pairwise interior-disjointness** — the last being what
the selection cover consumes and the only part with any content (the injection `w` assembled from
`wL`, `wP` and the disjointness of their images).

## The residue, named exactly

**(R1) the reflected certificate tree** (≈ 300 lines, no new mathematics).  An inductive mirroring
the emitted `root` — `bisect`, `branch`, `imp` / `imp_sel`, `dead` — with a decidable `treeOk`
applying `LocalCertT.splitOk` at a bisection, `selectionOk` at a branch and at an `imp`, and
matching a `dead` node against the recorded leaf.  Consumes `LocalCertT.coverOk_sound` (C1) and
`selectionOk_sound` (C2), both theorems.

**(R2) the reflected row builder** (≈ 600 lines).  `rowsOf : Cell → Selections → List CRow`, the
Lean twin of `gen_local_t.RowsT`, with `rowsOf_sound` from §7.  Two parts, both bookkeeping:
the affine-form arithmetic that identifies `evalL row.co x 0 + row.k` with the real quantities
`P`, `Q`, `W_lb`, `c_x`, `c_y`; and the OUTWARD quantisation of `gen_local_t.quantise_leaf`
(coefficients rounded to `1/10¹²`, the constant lowered by the total rounding slack over the box,
so `emitted ≤ true ≤ 0`), for which `LocalCert.minL_le` is the tool.

**(R3) the variable INDEX map** (≈ 120 lines).  §8 supplies the squares; what remains is
`x (2i+1) = (q i).cx`, `x (2i+2) = (q i).cy − (α + β s)` for a pin and
`x (2·|B|+1+f) = (q i).t`, from a decidable check that the certificate's layout is that one.  It
is: A119's numbering is `vi = 2i+1` in body order and the tilts follow all the centres, and A133
inherits it — verified on `S07_trump5_r0.10_rho40` (`nv = 20`, three free bodies at `1,3,5`, five
pins at `7,9,11,13,15`, tilts at `17,18,19`).

**(R4) the data and the replay.**  `LocalCertT2S07Data` / `…S02Data` for the `t`-certificates
(2 140 and 16 406 leaves) plus the `pcert` entries, and the `native_decide` replay.  T3 measured
the `pcert` half of exactly this and it is cheap (36 s and 81 s including overhead, with A126's
batching); the leaf half is A126's measurement.

## [C] — missing library lemmas

**None.**  Every mathematical step of (C2), (C3) and (C4) is a theorem in `LocalCertT2.lean`,
`LocalCertT.lean`, `Local.lean`, `SatInterior.lean` or `Parametrize.lean`.  The one thing that was
missing was on the CERTIFICATE side, not the library side, and is stated here for the record:

> **[C] (closed by T1)** The certificate must record, per `S` envelope cell, the constant
> enclosure `S_lo ≤ sin(θ(t) − θ(t*)) ≤ S_hi` and the correction constant
> `K ≥ max_cell (1 − cos(θ(t) − θ(t*)))`, each with a positivity certificate.  Lemma RELAX's
> envelopes (A), (B1), (B2) and the `corr` term consume these three numbers, and A133's checker
> recomputed them from the cell rather than reading them, which Lean cannot do.
> `gen_local_t2.py` now emits them (`pcert.S[…].s_lo/s_hi/K`, chains `c_lo`, `c_hi`, `corr`), and
> `sRel_le_aff` / `sRel_ge_aff` (at `alpha = 0`) and `one_sub_cosRel_le` are the consumers.

One further observation worth recording, because it is invisible until one writes the Lean:
**`posCheck` compares LISTS**, so a positivity certificate is only accepted if it reproduces the
polynomial with the exact trailing-zero shape `posAux` produces.  That is a real constraint on the
generator (`code/leanpoly.py` mirrors the recursions; every envelope polynomial is defined through
`padZ` on both sides) and it is the kind of thing that fails at the very end of an assembly if it
is not settled first.
