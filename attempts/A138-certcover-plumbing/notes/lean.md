# A138 T1/T2 — the reflected plumbing of `CertCover`: what `LocalCertT3.lean` proves

**Read with A134's `notes/lean.md` (which named the residue) and §§1–8 of
`lean/PackingCertMathlib/PackingCertMathlib/LocalCertT3.lean`.**

## Stated plainly

A134 proved every MATHEMATICAL step of `LocalCert.CertCover` — (C1) the tilt cover (A133), (C2)
the selection cover, (C3) Lemma RELAX for both row families, (C4) the geometric half of the
variable map — and named four kinds of bookkeeping that stood between them and
`localDead_s07_t`: **(R1)** the reflected tree walk, **(R2)** the reflected row builder with the
outward-quantisation step, **(R3)** the variable index map, **(R4)** the leaf data and the replay.

**(R1), (R2) and (R3) are now written and proved, and so is the glue.**  `LocalCertT3.lean`
(1 856 lines, 130 declarations, `lake build` 25 s, no `sorry`) ends in

```lean
theorem certCover_of_check {C : Cert} (hok : certOk C = true) :
    CertCover C.leaves C.M.boxes C.M.pins ((C.M.slo : ℚ) : ℝ) ((C.M.shi : ℚ) : ℝ)

theorem localDead_of_certOk {C : Cert} {s0 : ℚ} (hok : certOk C = true)
    (hlo : ((C.M.slo : ℚ) : ℝ) ≤ 191 / 50) (hhi : (s0 : ℝ) ≤ ((C.M.shi : ℚ) : ℝ))
    (hchk : C.leaves.all (checkLeaf s0) = true) :
    LocalDead C.M.boxes C.M.pins (s0 : ℝ)
```

— `LocalDead` for a neighbourhood from **two decidable checks on the certificate and nothing
else**: no geometric side condition, no numeric hypothesis, no unproved lemma.  `Ls` and `Ps`
are READ OFF the certificate (`CMeta.boxes` / `CMeta.pins`), so there is no matching obligation
between the certificate and the statement either.

**(R4) is NOT done**: no `certCover_s07`, no `localDead_s07_t`.  What is missing is exclusively
DATA — the S07/S02 certificates re-encoded into the reflected shape as Lean literals — and T2's
measurement below shows the data is already all there and already accepted by the check as
written.

## Axiom roster

`lean/PackingCertMathlib/scratch/A138Axioms.lean`:

| theorem | roster |
|---|---|
| `rowImplies_sound`, `layoutOk_get`, `geoHyp_of_localHyp`, `bodyIQ_mem`, `pairBoxOf_holds`, `wallOf_sound`, `usOf_sound`, `selRowsOfCtx_sound`, **`selCtx_sound`**, `allRows_sound`, **`treeOk_sound`**, `rootOk_sound`, **`certCover_of_check`** | `[propext, Classical.choice, Quot.sound]` |
| `localDead_of_certOk` | the same **+ `check_3_82`'s `native_decide` axiom** (through `lb_382`, exactly where A126 needed it) |
| `smoke_certOk`, `smoke_cover` | the same + that instance's own `native_decide` axiom |

`Local.sat_selection` — the project's one local axiom — does **not** appear anywhere:
`SatInterior.sat_selection_thm` proves it, and A134's `selectionOk_sound` consumes the theorem.

## The four residues, and what each turned out to be

**(R2), the part A134 priced at ≈ 600 lines, collapses to one lemma.**  A134 expected the
outward quantisation of `gen_local_t.quantise_leaf` (coefficients rounded to `1/10¹²`, the
constant lowered by the total rounding slack over the box) to be re-derived in Lean.  It does not
have to be.  Comparing the emitted row with the true row through `LocalCert.minL`,

```lean
def rowImplies (tc : List ℚ) (tk : ℚ) (box : List (ℚ × ℚ)) (r : CRow) : Bool :=
  match minL (addL tc (smulL (-1) r.co)) box with
  | none => false | some v => decide (r.k - tk ≤ v)
```

is exactly the invariant `quantise_leaf` establishes, and `rowImplies_sound` (12 lines, from
`minL_le`) says a true row that holds forces the emitted row to hold.  **Nothing about the
rounding is re-derived, and a generator that rounds differently — or not at all — is accepted by
the same check.**  What is left of (R2) is the ROW BUILDER proper: `wallOf` / `wallOf_sound` for
the wall family and `selCtx` / `selCtx_sound` for the selection family, the latter being the one
long proof in the file (≈ 220 lines) because it wires all five hypotheses of `relax_selection`
— `axis_decomp_t`, `one_sub_cosRel_le` + `corr_bound`, one of `relax_U_A/B1/B2`, `wrel_ge_plane`
— to the certificate's own recorded constants.

**(R1) becomes a plain structural induction once the branch is made BINARY.**  A133's emitted
`branch` node is n-ary (one child per possible selection), and a Lean inductive with a
`List CNode` field gives no usable induction hypothesis.  The fix costs nothing: a selection
branch re-encodes as a chain of binary `sel1` nodes, **each of which is the tautology
`SelHolds σ ∨ ¬ SelHolds σ` and carries no certificate at all**, closed by one `impx` node where
`selectionOk_sound` says the recorded selections are exhaustive and every one of them has already
been refuted along the chain.  The walk therefore carries two selection lists, the ones that HOLD
and the ones that DO NOT, and `treeOk_sound` is five cases with no auxiliary induction.

**(R3) is 40 lines, not 120.**  Writing A119's layout INTO the map (`certX`) rather than reading
`vi`/`ti` out of the certificate makes the five evaluation lemmas one `omega` each; `layoutOk`
then DECIDES that the emitted body records use that layout, so a generator that ever renumbers is
rejected rather than misread.

**One thing A134's list did not name, and it is real: the ROOT CELL.**  `CertCover` quantifies
over configurations, `treeOk_sound` over points of the root cell, and the bridge — "the
certificate's root cell is the neighbourhood's own box" — is 20 rational comparisons per
neighbourhood.  It is `rootOk` / `rootOk_sound` (§7), decidable, so `certCover_of_check` has no
side condition.

**A data-size finding worth carrying into (R4).**  A bisection node need not record its children's
cells: `cellLo` / `cellHi` compute them and `splitOk` still checks the split.  At 2 202
bisections over 20 coordinates that is **88 000 rational literals removed** from the S07 data
file — and A126's wall is the elaborator, not the kernel.

**Executability.**  `certOk` is over `ℚ`/`Bool`/`List` only.  Kernel `decide` gets STUCK on it
(§8; the `Decidable` instance does not reduce), `native_decide` runs it — which is the path A126
and A134 already use for the leaf and `pcert` replays, so this costs nothing new, but it means
(R4) must budget `native_decide`, not `decide`.

## T2 — does `local-cert-t-v2` carry every field the reflected shape reads?

**Yes.  No generator revision is needed; what (R4) needs is a pure RE-ENCODER.**
`code/reencode_check.py` builds the reflected shape from a v2 certificate and checks it field by
field, including a mirror of the Lean row builder written from the LEAN definitions (not from the
generator) and the Lean `affImplies` test:

| | S07 (0.1, 40°) | S02 (0.02, 2°) | S02 (0.2, 10°) |
|---|---|---|---|
| layout `vi=2i+1`, free first, `ti=2nb+1+i` | OK, `nv = 20` | OK, `nv = 23` | OK, `nv = 23` |
| root cell reconstructed from `meta` | OK | OK | OK |
| walk reproduces **every** leaf's box | 2 140/2 140 | 8/8 | 16 406/16 406 |
| bisect children = `cellLo`/`cellHi` | 2 202 nodes | 0 | 16 278 |
| n-ary branch → `sel1` chain + `impx` | 270 + 87 (87 branches) | 14 + 7 | 190 + 63 |
| `impsel` nodes | 246 | 0 | 0 |
| envelope keys needed / present (h, S, w) | 21/21, 21/21, 324/336 | 2/2, 2/2, 10/10 | 49/50, 49/50, 884/944 |
| missing keys | 0, 0, 0 | 0, 0, 0 | 0, 0, 0 |
| `S` entry fields | `K, c_hi, c_lo, corr, lo, s_hi, s_lo, tm, up` — all five chains and all three constants |
| `w` certificate modes | `xy` 252, `x` 42, `y` 42 | `xy` 4, `x` 4, `y` 2 | `xy` 830, `x` 100, `y` 14 |
| **emitted rows implied by a built row** | **25 377 / 25 377** | **124 / 124** | **270 199 / 270 199** |

**295 700 emitted rows across 18 554 leaves, and every one of them is implied, on its own leaf
box, by a row the Lean builder constructs.**  That is the whole of (R2)'s risk retired: the Lean
`wallOf` / `selCtx` formulas agree with `gen_local_t.RowsT` on every row of every leaf of all
three certificates, including the two degenerate paths (a pin's collapsed tilt cell, where
`S ≡ 0` and `C ≡ 1` and no `S` table entry is read at all; and a pin–pin pair, where `w = 1`).

The `w` table carries 12 (S07) and 60 (S02) entries the walk never asks for — the census evaluates
envelopes on cells that are later bisected away.  Harmless: `wEnvOk` checks them all, and an
entry that is never looked up costs only its own positivity check.

## [C] — missing library lemmas

**None.**  Every step of (R1), (R2), (R3) and the glue is a theorem in `LocalCertT3.lean` or one
it imports.  The one thing (R4) needs and does not have is a Lean DECODER for the re-encoded
certificate and the emitted data file — engineering, not mathematics.

## (R4), specified

1. `code/encode_t3.py`: walk a `local-cert-t-v2` certificate exactly as `reencode_check.py` does
   and emit (a) `CMeta` and the root cell as literals (8 bodies, 20 pairs — trivial); (b) the
   three envelope tables as literals (S07: 21 + 21 + 336 entries, the `w` grids being ~20
   rationals each ⇒ ≈ 7 000 literals, comfortably inside A126's 32-entries-per-`private def`
   budget); (c) the tree, `bisect`/`sel1`/`impx`/`impsel`/`dead` with NO child cells (S07: 4 945
   nodes after the sel1 expansion, each 2–5 small literals); (d) the leaves, string-encoded and
   decoded by A126's `LocalCert.parseLeaf` — but note that a leaf box mixes the row denominator
   `10¹²` with dyadic tilt endpoints of denominator up to `2^(24+depth)`, so `parseLeaf` must be
   called with the common denominator, or a two-denominator variant added.
2. `certOk_s07 : certOk s07Cert = true := by native_decide`, then `certCover_s07` by
   `certCover_of_check`, then `localDead_s07_t` by `localDead_of_certOk` with A126's
   `check_s07`-style leaf check re-emitted on the v2 leaves.
3. Budget: A134 measured the `pcert` replay at 36 s (S07) / 81 s (S02) and found the ELABORATOR,
   not the kernel, to be the wall (one 336-entry list literal times out at `isDefEq`; the remedy
   is 32 entries per `private def` and linear `++`).  The tree and the tables here are of the same
   order; the leaves are A126's own measurement.
