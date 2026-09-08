# A138 T3 — the closure statement

## What the local-certificate chain now asserts, from which data, under which axioms

`LocalCertT3.certCover_of_check` closes `LocalCert.CertCover`, the single named obligation A126
left open: **for a certificate `C` whose one decidable check `certOk C` passes, every packing
that satisfies the neighbourhood hypothesis `LocalHyp C.M.boxes C.M.pins` at any side in the
certificate's own window `[C.M.slo, C.M.shi]` has an LP variable vector inside one of the
recorded leaves' boxes, satisfying that leaf's rows.**  Composed with A126's Farkas half
(`LocalCert.localDead_of_cert`, `checkLeaf`), `localDead_of_certOk` gives
`LocalDead C.M.boxes C.M.pins s0` — no packing of side `≤ s0` satisfies the neighbourhood —
from **two decidable checks and nothing else**.  `certOk` bundles: A119's variable layout
(`layoutOk`), the root cell (`rootOk`), the three envelope tables with their Bernstein positivity
certificates (`hEnvOk`, `sEnvOk`, `wEnvOk`), and the whole reflected tree (`treeOk`, which at
every leaf rebuilds the node's true relaxed rows and checks that each emitted quantised row is
implied by one of them on the leaf's box).  The axiom roster of `certCover_of_check` and of every
lemma under it is `[propext, Classical.choice, Quot.sound]`; `localDead_of_certOk` adds only
`check_3_82`'s `native_decide` axiom, through `lb_382`, exactly where A126 needed it.  There is
no `sorry` and the project axiom `Local.sat_selection` is not used — `SatInterior.sat_selection_thm`
proves it.

**`localDead_s07_t` and `localDead_s02_t` are NOT yet instances of this**, because the S07/S02
certificates have not been re-encoded into the reflected shape as Lean data — (R4), the only
remaining piece, and pure engineering: `code/reencode_check.py` verifies that a
`local-cert-t-v2` certificate carries every field `certOk` reads, that the walk reproduces every
leaf's recorded box, and that **all 295 700 emitted rows of the three certificates are implied by
the rows the Lean builder constructs** (`notes/lean.md`).

## What `LocalCompose.node_dead_of_yes_no` needs in addition

`node_dead_of_yes_no` turns `LocalDead Ls Ps s0` into "the node is dead" — hence, through
`classKilledAt_of_yes_no`, into `ClassKilledAt` — from two further hypotheses, and
`localDead_of_certOk` supplies only the first argument `hD`:

* **`hyes`** — that a packing of the node's region with SOME square in every box of `L` satisfies
  `LocalHyp Ls Ps s z`.  This is where the class pins enter: it needs the node's own hypothesis
  `H` to force a square into each slack core of `P`, and the boxes of `L` to be pairwise
  distinct-square (`LocalHyp` quantifies over DISTINCT squares).  It is per-node data, not a
  certificate.
* **`hno`** — that for each `i` the NO branch `NoneIn (Ls.get i) z` is impossible, i.e. **A120's
  and A136's NO certificates, replayed**.  This is the live dependency: `noneIn_of_clamped` makes
  the clamp to `[1/2, s−1/2]` free (`centre_in_slab`), but the ROUNDING with which a NO zone
  reaches the certificate file is not free — finding F-COVER, measured by A133 at up to
  `1.1·10⁻⁷` OUTWARD in tilt on all four of A120's closed nodes, which is the direction that
  breaks the containment.  What is needed is the decidable **ZONE ⊆ BOX** guard run AT EMISSION
  against the written rationals (A133 `notes/fcover.md` specifies it; A136 is producing such
  certificates).

So the chain from A138 to `ClassKilledAt` is: `certOk` + `checkLeaf` (done, decidable) →
`LocalDead` (done) → `node_dead_of_yes_no` with (i) the per-node YES bridge and (ii) replayed NO
certificates carrying ZONE ⊆ BOX (A136) → `ClassKilledAt` → `Composition.lean`.  Nothing in that
chain now needs new mathematics on the LOCAL side.
