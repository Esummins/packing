# A139 (R4) — the closure statement

## What is now a theorem

`LocalCertT3.S07T.localDead_s07_t : LocalDead s07Boxes s07Pins ((969271/250000 : ℚ) : ℝ)` —
**no packing of side ≤ 3.877084 satisfies the neighbourhood hypothesis of
`S07_trump5_r0.10_rho40`** — from two `native_decide` checks on emitted rational data and nothing
else: `certOk_s07` (the cover half: A119's variable layout, the root cell, the three envelope
tables with their Bernstein positivity certificates, and the whole tree, which at every leaf
rebuilds the node's true relaxed rows and matches each emitted quantised row against them) and
`checkLeaf_s07` (the Farkas half).  `certCover_s07` is `LocalCert.CertCover` for this
neighbourhood, the obligation A126 opened and A138 closed in the abstract, now INSTANTIATED.  `Ls`
and `Ps` are `C.M.boxes` / `C.M.pins`, read off the same certificate, so nothing is assumed about
the correspondence between the data and the statement.  Axioms: `propext`, `Classical.choice`,
`Quot.sound`, the two `native_decide` axioms of the replays, and `check_3_82`'s through `lb_382`.
No `sorry`; the project axiom `Local.sat_selection` is not used.

## The one thing A138's specification of (R4) got wrong

(R4) was specified as data plumbing.  It is not: `treeOk` re-runs the certificate's selection
EXCLUSIONS with `LocalCertT2.gapHi`, whose `w`-bound `wLoQ` is interval arithmetic, while A133's
generator excludes with the EXACT range of `w` over the cell product.  On A134's S07 certificate
**246/246 `imp_sel` closures and 38/426 branch exclusions are not reproducible in Lean**
(`code/diag_gap.py`), so that certificate cannot pass `certOk` under any re-encoding.  A139
therefore re-emits the certificate with the exclusion test computed the LEAN way (`regen_t3.py`,
A133's search with one overridden method; LP, envelopes, rounding, `pcert` all unchanged; bodies
byte-for-byte A119's, so the STATEMENT is unchanged) and pays +37 % leaves and +7 % rows for it.
Details, and the two smaller re-encodings (A133's branch-free singleton fixes; the pin–pin
mirror selections `selectionOk` demands and the generator drops as duplicates), in `notes/lean.md`.

## What this unblocks, and what it does not

`LocalCompose.node_dead_of_yes_no` turns `LocalDead Ls Ps s0` into "the node is dead" from two
further hypotheses, and A139 supplies only the first argument `hD` — now concretely, for a real
neighbourhood.  Unchanged from A138's status: **`hyes`** (a packing of the node's region with a
square in every box of `L` satisfies `LocalHyp`) is per-node data, not a certificate; **`hno`**
(each NO branch impossible) is A120's/A136's NO certificates replayed, and needs the decidable
ZONE ⊆ BOX guard at emission that A133 `notes/fcover.md` specifies and A136 is producing.

The certificates in `attempts/A134-certcover-close/certs/` remain valid under A133's checker and
remain unreplayable in Lean.  Two ways to close that permanently, both outside A139's scope:
adopt `wLoQ` in the generator's exclusion test (four lines, +37 % leaves, all future certificates
replay), or give `LocalCertT2` the exact `w` range as a decidable enclosure with its soundness
proof (A133's `w_range`: `w(|u|)` increases to `√2 − 1` and decreases after — one-variable, and
the polynomial machinery is already there).  **The second is the better buy**: it makes every
existing certificate replayable and every future one cheaper.
