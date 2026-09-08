# A139 (R4) — the certificates replayed: `localDead_s07_t` exists, and what stood in the way

**Read with `attempts/A138-certcover-plumbing/notes/lean.md` (which specified (R4)) and
`lean/PackingCertMathlib/PackingCertMathlib/LocalCertS07T.lean`.**

## The headline

```lean
theorem certOk_s07 : certOk s07Cert = true := by native_decide
theorem certCover_s07 :
    CertCover s07Cert.leaves s07Cert.M.boxes s07Cert.M.pins
      ((s07Cert.M.slo : ℚ) : ℝ) ((s07Cert.M.shi : ℚ) : ℝ)
theorem checkLeaf_s07 : s07Cert.leaves.all (checkLeaf (969271/250000)) = true := by native_decide
theorem localDead_s07_t : LocalDead s07Boxes s07Pins ((969271/250000 : ℚ) : ℝ)
```

with `s07Boxes = s07Cert.M.boxes` and `s07Pins = s07Cert.M.pins` — the neighbourhood is READ OFF
the same data the two checks run on, so there is no matching obligation between the certificate
and the statement.  Rosters (`scratch/A139Axioms.lean`, 16.6 s):

| theorem | axioms |
|---|---|
| `certOk_s07` | `propext, Classical.choice, Quot.sound` + its own `native_decide` axiom |
| `certCover_s07` | the same three + `certOk_s07`'s |
| `checkLeaf_s07` | the same three + its own |
| **`localDead_s07_t`** | the same three + **`check_3_82`'s** (through `lb_382`) + `certOk_s07`'s + `checkLeaf_s07`'s |

No `sorry`; `Local.sat_selection` does not appear (`SatInterior.sat_selection_thm` proves it).

## What (R4) actually was: not plumbing, an ENCLOSURE MISMATCH

A138 specified (R4) as "pure engineering — the certificates re-encoded as Lean data", on the
strength of a T2 audit that checked the row builder, the box walk and the envelope keys.  **That
audit did not check the one thing that fails.**  `LocalCertT3.treeOk` re-runs the certificate's
selection EXCLUSIONS — `selectionOk` at every branch, `gapHi < 0` at every `impsel` — and it
computes them with `LocalCertT2.gapHi`, whose support-width bound is

```lean
def wLoQ (a b : IQ) : ℚ :=
  max ((cosRelI a b).lo + (sinRelI a b).lo) ((cosRelI a b).lo - (sinRelI a b).hi)
```

— interval arithmetic on `cosRel` / `sinRel`.  A133's generator excludes with the SAME expression
but bounds `w` below by `a133lib.w_range_cell`: the EXACT range of `w = |cos Δ| + |sin Δ|` over the
cell product, obtained through the exact range of `u = tan(Δ/2)` and the monotone structure of
`w(|u|)`.  The true `w` is never below `1`; `wLoQ` can be, and at S07's root it is **−0.2397**.
The exclusion threshold therefore differs by up to `(1 − wLoQ)/2 ≈ 0.62`.

`code/diag_gap.py` replays both enclosures on every exclusion A134's `S07_trump5_r0.10_rho40`
records:

| | exclusions | not reproducible by `wLoQ` |
|---|---|---|
| `branch` (the excluded selections of a branch node) | 426 | **38 (8.9 %)**, at depths 0, 1, 2, 3, 5, 9, 10, 11, 13 |
| `imp_sel` (a fixed selection become impossible) | 246 | **246 (100 %)** |

100 % for `imp_sel` is not an accident: an `imp_sel` node fires the moment the generator's gap
crosses zero, so every one of them is a close call, and a bound loosened by ≥ 0.1 loses all of
them.  **A134's certificates cannot pass `certOk`, and no re-encoding of them can.**

Two further mismatches, both real and both cheap, surfaced in the same pass:

* **A133 fixes a selection with NO branch node** whenever the census leaves exactly one
  possibility (`TreeT._node`: `if pr not in fx and len(poss) == 1: fx[pr] = poss[0]`).  Lean's
  `fx` grows only through `sel1`, so those selections are simply absent from the walk's list while
  the leaf's rows use them.
* **For a pin–pin pair the generator drops the four swapped selections as duplicates**
  (`census`: `if bi.kind == "pin" and bj.kind == "pin" and o == 1: continue`).  `selectionOk`
  quantifies over all eight and does not know they are duplicates.

## The fix, in three pieces

**(1) Re-emit with the enclosure Lean re-runs** (`code/regen_t3.py`).  A133's `Geo` subclassed so
that the EXCLUSION half of the gap (`.hi`) uses `wLoQ`; the FAR half (`.lo`, which only decides
whether a pair may be dropped from the LP, and dropping rows is sound in either direction) keeps
the exact range.  Everything else — the LP, `RowsT`, the envelopes, `quantise_leaf`, A134's
`build_pcert` and `emit2` — is A133's and A134's code unchanged, and the bodies are byte-for-byte
A119's, so **the neighbourhood, and hence the statement, is unchanged**.

The search closes, and the price is small:

| | A134's cert | A139's re-emission |
|---|---|---|
| tree wall | 23.2 s | **23.4 s** |
| nodes / dead leaves | 4 675 / 2 140 (768 rays) | 5 479 / **2 923** (1 484 rays) |
| bisections / branches / `imp_sel` | 2 202 / 87 / 246 | 2 318 / 170 / **68** |
| rows | 25 377 | 27 287 |
| envelope entries h/S/w | 21 / 21 / 336 | 21 / 21 / 336 |
| unresolved | 0 | **0** |

**+37 % leaves, +7 % rows, no new envelope entries, and the cell floor `1/5000` is never
reached.**  The branches Lean's coarser enclosure cannot exclude are killed by the LP instead —
the relaxation carries a certified PLANE below `w`, which is sharper than the constant `wLoQ`, so
a branch that is geometrically impossible shows up as an infeasibility ray (rays go 768 → 1 484).

**(2) Re-encode the two structural differences** (`code/encode_t3.py`).  A selection A133 fixed
without a branch is re-encoded AT THE TERMINAL THAT NEEDS IT as `sel1 σ · (impx i j [σ])` — the
tautological split, closed by the exhaustiveness node, whose `selectionOk` obligation is exactly
"the other seven are excluded here" and holds on the terminal's (smaller) cell by monotonicity.
Each recorded pin–pin selection is emitted with its mirror: `gapHi (pb.swap) k e = gapHi pb k (−e)`
EXACTLY (both tilt cells are the point `0`, so `axI` is the same on both sides and `IQ.sub`
negates exactly), and the mirror builds the SAME affine rows (`wsOf` gives `[1]`, the owner's cell
is degenerate so `Us = [0]` and `corr = 0`, and `P` is invariant under swapping owner and sign),
so the mirror's branch is closed by the same leaf and an `impsel` under it simply names the mirror.

**(3) Emit, with A126's elaborator remedy.**  32 entries per `private def` and linear `++` for the
three envelope tables; the tree cut into a `private def` at every subtree of ≥ 64 nodes (241 defs);
the leaves as one string each, 2 000 per literal, decoded by a `parseLeafT` that takes the box and
the row denominators SEPARATELY (a leaf box is dyadic on `2^58`, its rows are on `10^12` — the
single-denominator `LocalCert.parseLeaf` cannot carry both without a 19+14-digit common
denominator).  Bisection children are computed, not recorded: 185 440 rational literals not
emitted.

`encode_t3.py` verifies, before writing a line, everything the Lean check will re-run — `layoutOk`,
`rootOk`, `splitOk` at every bisection, `pairBoxOf`/`pbOkB`/`selectionOk` at every `impx`,
`σ ∈ fx` and `gapHi < 0` at every `impsel`, `L.box == cur` at every leaf, every envelope key the
walk looks up, `checkLeaf` on ALL leaves exactly, and the Lean row builder on a sample.

## Cost

| step | wall |
|---|---|
| `regen_t3.py` (search + `pcert` + emit) | 23.4 s + 0.6 s |
| `encode_t3.py` (verify + emit 6.16 MB of Lean) | 5.8 s |
| `lake build PackingCertMathlib.LocalCertS07T` (BelowNormal, includes both `native_decide` runs) | **535.1 s** |
| `scratch/A139Axioms.lean` | 16.6 s |

The emitted file: 4 636 bisections, 4 566 `sel1`, 1 780 `impx` (1 442 of them terminal fixes),
136 `impsel`, 5 845 dead-leaf nodes over 2 923 distinct leaves.  The node counts are exactly twice
the re-emitted tree's because the one pin–pin branch pair — `BL(1,0)` / `BL(0,1)`, whose census is
CELL-INDEPENDENT and therefore branches at the root — duplicates the whole tree through its
mirror.  **The duplication costs tree text only** (leaves are shared, `dead li` is emitted twice),
and it would disappear entirely if `LocalCertT3` learned the one-line fact that for two squares of
tilt `0` the two orientations of a selection are the same statement.

## What this does NOT settle

The re-emission is A139's, so the S07/S02 certificates in `attempts/A134-certcover-close/certs/`
are now certificates that A133's checker accepts and Lean's `treeOk` does not.  Either the
generator adopts `wLoQ` for the exclusion test (the change is four lines and costs +37 % leaves),
or `LocalCertT2` acquires the exact `w` range as a decidable enclosure with its soundness proof
(then A134's certificates replay unchanged, and every future one is cheaper).  **The second is the
better buy** — the exact range is A133's `w_range` and its Lean proof is the one-variable statement
that `w(|u|)` increases to `√2 − 1` and decreases after, which `LocalCertT2` already has the
polynomial machinery for.
