# A107 — method notes (Opus chore, read-only on every campaign)

## Discipline

* One BLAS-pinned Python process at a time (`OMP/MKL/OPENBLAS/NUMEXPR_NUM_THREADS=1`); the only
  long run is the structure minimisation (`logs/minimise.log`).
* **Nothing** under `attempts/A57-shadow-trees/`, `attempts/A60-trump5-campaign/`,
  `attempts/A61-window-stragglers/`, `attempts/A85-k0-route/`, `attempts/A96-a57-parametric/`,
  `attempts/A99-k0-tree-v2/`, `attempts/A104-*`, `attempts/A105-*`, `attempts/A106-*` or `lean/`
  was written; no campaign process was started, stopped or re-niced (the one `taskkill` in this
  attempt targeted A107's own PID and no other).
* Frozen verifiers untouched.  Writes confined to `attempts/A107-shadow-gallery/**`,
  `docs/shadows.md`, `docs/shadows/*.svg`, plus the registry row, `LOG.md` and one note field on
  the depgraph's `C.A57` node.
* Every drawn square is containment-checked; the minimised panels are additionally
  overlap-checked (`svg.panel_pack` asserts both and prints the min pairwise SAT separation).
  Overlaps appear only in the raw LP panel and are reported as numbers there.

## Pipeline

| step | file | what it does |
|---|---|---|
| 1 | `code/shadowlib.py` | geometry (SAT gaps scalar + vectorised, corners, wall gaps), D4 on `[0,s]^2`, the class stabiliser, slot-cell naming and snapping, tolerant shadow matching |
| 2 | `code/extract.py` | loads every ALIVE-at-LP node (`dead == False`) of A57/A60/A61 (A85/A99 have no LP nodes in this format), builds the shadow = hypothesis cores + integral support, splits fractional supports into integral components, groups by structure (slot set + free count) modulo the class stabiliser |
| 3 | `code/minimise.py` | the direct side minimisation per structure: slot squares affine in `s`, free squares `(cx, cy, theta)` and `s` variable, SLSQP; generalises `docs/residue_map/gen_pinwheel_k7.py` |
| 4 | `code/gallery.py` | de-duplicates the MINIMISED configurations into distinct shadows, re-confirms each with >= 100 restarts, runs the analysis |
| 5 | `code/analyse.py` | contact graph, Fritz-John contact forces, exact incidence Jacobian, flat directions + second-order test, rattler/load-bearing subgraph, common-tilt sweep |
| 6 | `code/svg.py`, `code/writeup.py` | the drawings and `docs/shadows.md` |

## Two things that had to be got right

**The LP rows are cells, not points.**  A node's `packing` entries are representatives of
configuration-space cells of pitch 0.1918 in `x`/`y` and 5 deg in tilt.  The integral supports in
this corpus — genuine LP integral solutions, so realisably disjoint — have worst pairwise SAT gap
**-0.2045**, i.e. exactly one cell pitch of overlap between representatives.  Testing
"pairwise disjoint" at gap >= 0 would have declared every shadow an overlap and every fractional
support componentless; the honest test is gap >= -0.21.  This is why the PI's instruction was
"draw it, overlaps and all".

**Flex counts need incidence Jacobians, not SAT derivatives.**  `analyse.contact_rows` builds one
row per incident vertex as the exact analytic derivative of `g = n_E . (V - P)` — the distance
from the incident vertex to the supporting *line* of the other square's edge — including the
lever term `(n_perp . (V - P)) * dtheta` from the edge owner's rotation, and the `dc/ds` term for
slot squares.  A finite difference of the SAT gap is wrong at flush contacts (the max over axes
is not differentiable there) and wrong at exactly-opposite vertex-vertex contacts (the normal is
a whole cone).  Exactly-opposite contacts are detected and flagged: their two vertex rows are
near-parallel, so their individual Fritz-John multipliers blow up while the *resultant*
`||sum_r lambda_r n_r||` stays finite — the resultant is what the gallery reports.  Every flat
direction of the fixed-`s` Jacobian is then probed at `|t| = 1e-3, 3e-3, 1e-2` against the exact
gaps; a genuine flex leaves them unchanged to `O(t^3)`, a second-order block shows the clean
`9` and `100` ratios of a quadratic.

## Cross-checks

* The PI's k7 pinwheel shadow is reproduced exactly: `s* = 3.886745977 = s-hat + 0.009662`, four
  free squares at one tilt 48.4352 deg, binding contact `f1`-top wall, `f0`-`f1` an
  exactly-opposite pair, one flat direction blocked at second order with curvature ~1e-5.
* The whole `s*` spectrum agrees with A106's independent census (§2.1 of
  `attempts/A106-shadow-diameter/notes/measurements.md`) to 6-7 digits.
* A106's finding that **no** open A57 box contains a shadow is reused, not re-derived: "explains"
  in this gallery means the node's dual support flows to that shadow, not that its box holds it.

## The one value below A106's census floor

A107 finds a k11 shadow at **s\* = 3.8856180554 = s-hat + 0.008534**, *below* the k7 pinwheel's
3.886746, on the trump5 (A60) skeleton with the slot set
`BL(0,0) BL(0,1) BL(0,2) BL(1,0) BR(0,0) TR(0,0)` (a BL column of three, BL(1,0), BR and TR) and
five free squares at a common tilt of 44.88 deg.  It explains 19 alive nodes.  Checks done:

* containment exact (min coordinate 0.0, max coordinate = s to 1e-15);
* worst pairwise SAT separation at the SLSQP point −9.5e-8, i.e. inside the solver's own
  feasibility tolerance;
* **feasibility restoration** at `s = s* + 1e-7` with `s` fixed: a configuration exists at which
  every non-degenerate constraint is `>= 0` (the reported minimum is exactly 0 because the
  slot-slot gaps inside one corner stack are identically zero).  So this is a genuine 11-square
  packing to numerical precision.

What has **not** been done: an exact interval endpoint certificate in A106's style (mpmath iv,
250-bit).  Until that is produced, treat 3.885618 as a numerically verified local minimum, not a
certified one.  It does not touch any bound — it is above s-hat — but it means A106's census
floor for these classes was not the true floor.
