# A139 (R4) — results

`s0 = 969271/250000 = 3.877084`.  Everything below is on the certificates A139 re-emitted
(`certs/`, `code/regen_t3.py`); the neighbourhoods (`meta.bodies`) are byte-for-byte A119's, so
the theorems are about the same `N` A126/A133/A134 have been carrying.

## T0 — why A134's certificates cannot be replayed (`code/diag_gap.py`)

`LocalCertT3.treeOk` re-runs the certificate's selection EXCLUSIONS with `LocalCertT2.gapHi`,
whose support-width bound `wLoQ` is interval arithmetic on `cosRel`/`sinRel`.  A133's generator
excludes with the same expression but with `a133lib.w_range_cell`, the EXACT range of
`w = |cos Δ| + |sin Δ|` over the cell product.  `w ≥ 1` always; `wLoQ` can be negative.

| certificate | branch exclusions | not reproducible | `imp_sel` closures | not reproducible |
|---|---|---|---|---|
| `S07_trump5_r0.10_rho40` (A134) | 426 | **38 (8.9 %)** | 246 | **246 (100 %)** |
| `S02_k5_11_r0.20_rho10` (A134) | 314 | **44 (14.0 %)** | 0 | — |

Worst cases: S07 at the root, `wLoQ = −0.2397` against the true `w ≥ 1` (Lean's `gapHi` `+0.478`
where the generator has `−0.142`); S02 at depth 2, `wLoQ = 0.9917` against `1.3555`
(`+0.167` against `−0.015`).  One failure is enough to make `certOk` false, so neither
certificate can be replayed under any re-encoding.

## T1 — the re-emission with the Lean-faithful exclusion test (`code/regen_t3.py`)

A133's `Geo.gap` subclassed: the `.hi` (exclusion) half uses `wLoQ`, the `.lo` (far, i.e. "this
pair may be dropped") half keeps the exact range — dropping a pair only removes rows from the LP.
The LP, `RowsT`, the envelopes, `quantise_leaf`, A134's `build_pcert` / `emit2` are unchanged.

| `N` | leaves (A134 → A139) | rays | rows | branches | `imp_sel` | unresolved | tree wall | file |
|---|---|---|---|---|---|---|---|---|
| S07 (0.1, 40°) | 2 140 → **2 923** (+37 %) | 768 → 1 484 | 25 377 → 27 287 | 87 → 170 | 246 → **68** | **0** | 23.4 s | 1.43 MB |
| S02 (0.2, 10°) | 16 406 → **16 732** (+2 %) | 1 950 → 2 276 | 270 199 → 271 170 | 63 → 113 | 0 → **0** | **0** | 185.3 s | 13.53 MB |

Envelope tables are unchanged in size (21/21/336 and 50/50/946), the Bernstein depth stays 0, and
the cell floor `1/5000` is never reached.  The branches Lean's coarser enclosure cannot exclude
are killed by the LP instead — the relaxation carries a certified PLANE below `w`, sharper than
the constant `wLoQ`, so a geometrically impossible branch shows up as an infeasibility ray.

## T2 — the re-encoding and the emitted Lean (`code/encode_t3.py`)

Verified in Python before a line is written, on ALL nodes and ALL leaves: `layoutOk`, `rootOk`,
`splitOk` at every bisection, `pairBoxOf` + `pbOkB` + `selectionOk` at every `impx`, `σ ∈ fx` and
`gapHi < 0` at every `impsel`, `L.box == cur` at every leaf, every envelope key the walk looks up
present in both `env` and `pcert`, and `checkLeaf` exactly at `s0`.  The Lean row builder
(`wallOf` / `selCtx` / `selRowsOfCtx`, mirrored from the Lean definitions) is replayed on a
sample of leaves with the WALK's selection list: S07 60 leaves / 528 rows, S02 40 / 659, zero not
implied.

| | S07 | S02 |
|---|---|---|
| `bisect` / `sel1` / `impx` / `impsel` / `dead` | 2 318 / 2 286 / 891 / 68 / 2 923 | 16 278 / 26 968 / 13 312 / 0 / 16 732 |
| of the `impx`, terminal singleton fixes | 721 | 13 199 |
| tree cut into `private def`s (≥ 64 nodes) | 121 | 1 106 |
| emitted Lean | **5.79 MB** | **43.66 MB** |
| encode wall | 5.5 s | 44.2 s |

Two re-encodings, both forced by the difference between what A133 records and what `treeOk`
reads, and both invisible to the statement:

* **A133 fixes a selection with no branch node** when the census leaves one possibility.  Lean's
  `fx` grows only through `sel1`, so each such fix is re-encoded at the terminal that needs it as
  `sel1 σ · (impx i j [σ])`; the `impx` obligation is "the other seven are excluded here", which
  holds on the terminal's (smaller) cell.
* **A pin–pin pair's four swapped selections** are duplicates the generator drops and
  `selectionOk` does not.  `gapHi (pb.swap) k e = gapHi pb k (−e)` EXACTLY, and the mirror builds
  the SAME affine rows, so the mirror's branch reuses the recorded one's subtree verbatim — and
  because a pin–pin enclosure is CELL-INDEPENDENT (both tilt cells are the point `0`, neither
  centre interval is ever bisected) no `impsel` inside can name that pair, so the sharing is
  sound and the emitter emits one `private def` for both.  Without the sharing S02's four pin–pin
  branch pairs would have multiplied the tree text by 2⁴.

## T3 — the Lean walls

| step | wall |
|---|---|
| `lake build PackingCertMathlib.LocalCertS07T` (first cut, 6.16 MB, before subtree sharing) | 535.1 s |
| `lake build ...S07T ...S02T` together, BelowNormal (both `native_decide` runs each) | **6 712.3 s** |
| — `Built PackingCertMathlib.LocalCertS07T` (the two modules build in parallel) | **571 s** |
| — `Built PackingCertMathlib.LocalCertS02T` | **6 707 s** (112 min, steady 1.8 GB) |
| `scratch/A139Axioms.lean` (8 `#print axioms`) | 180.5 s |

`Build completed successfully (3210 jobs)`, no `error`, only style linter warnings (long lines,
`native_decide`, `show`).  The oleans are 39.6 MB (S07) and 186.1 MB (S02).

## T3 — the axiom rosters

| theorem | axioms |
|---|---|
| `certOk_s07`, `certOk_s02` | `propext, Classical.choice, Quot.sound` + own `native_decide` |
| `certCover_s07`, `certCover_s02` | the same three + the corresponding `certOk`'s |
| `checkLeaf_s07`, `checkLeaf_s02` | the same three + own `native_decide` |
| **`localDead_s07_t`, `localDead_s02_t`** | the same three + **`check_3_82`'s** (through `lb_382`) + `certOk`'s + `checkLeaf`'s |

No `sorry`; `Local.sat_selection` appears in none of them.
