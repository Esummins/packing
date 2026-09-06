# A110 — method notes (grain sweeps, load paths, the T4 count)

Theory is in `docs/proofs/grain_flood.md`; this file records how the [M] items were produced.

## Discipline

* One BLAS-pinned Python process at a time (`OMP/MKL/OPENBLAS/NUMEXPR_NUM_THREADS = 1`, set before numpy is
  imported); two chores (`code/grain110.py` ≈ 16 min, `code/t4_110.py` ≈ 5 s); pure geometry (SLSQP + nnls).
  Headroom at start: 14.4 GB free physical, 86 GB commit — the A61 campaign (pids 45764/8652/43180) untouched.
* Nothing under `attempts/A57-*`, `A60-*`, `A61-*`, `A96-*`, `A109-*`, `lean/` or the frozen verifiers was written or
  imported for writing; A106 `shadow11`, A107 `shadowlib/minimise/analyse`, A108 `a108lib/exact` are imported as
  libraries (A108's import order pins BLAS). Node jsons of A57/A60 are read for their `hyp.boxes` only.
* Writes: `attempts/A110-grain-flood/{code,results,logs,notes}`, `docs/proofs/grain_flood.md`, registry row, LOG line,
  two depgraph notes (C.A57, K0.RESN) and one new depgraph node GRAIN (owner A110).

## The sweeps (`code/grain110.py`)

* **Problem.** All eleven squares free (34 variables, A107 order `[s, (x,y,θ)×11]`, A107's `make_cons((), 11)` =
  55 SAT gaps + 44 containment gaps), the common tilt of the load-bearing tilted squares PINNED (S07: f0 f1 f2 f4, the
  rattler f3's tilt free; S02: f1 f2 f3, the strut f0's tilt free; Trump branch: all five, as A108). SLSQP (maxiter 400,
  ftol 1e-14), three starts per tilt — warm from the previous tilt and two 0.02-jitters — the best kept. Every landing
  is rescaled to its exact side σ (`a108lib.sigma`: the smallest side at which the normalised shape is a packing),
  so the reported s is never a solver value.
* **Contacts.** Pairs and walls with gap < 1e-6 at the rescaled landing; incidence type (vertex-on-edge / flush /
  exactly-opposite = full flush) from A107's `analyse.incidences`, the incidence rows from `analyse.contact_rows`
  (exact analytic derivative of the vertex-to-supporting-line distance with the rotation lever), wall rows likewise.
* **Load path.** Fritz-John multipliers by `nnls(Jᵀ, e_s)` on the unit-normalised rows with the pinned tilt columns
  REMOVED (the pinned tilts are equalities with free-sign multipliers, so their columns do not constrain the cone);
  loaded = per-contact resultant > 1e-4; the residual is the KKT residual of the fixed-tilt problem and is ≤ 1e-8 at
  every reported point except the S07 point 42.0° (5e-7) and the Trump-branch point 41.6° (1e-7).
* **Events.** Between consecutive tilts: contacts that appear/disappear (`contact_events`) and loaded rows that
  appear/disappear (`load_events`). A change of the loaded set with the closed form unchanged is a change of dual basis
  within the same value (the ladder's two equivalent row pairs f0–f1/f0–f4 vs f1–f2/f2–f4 alternate on the y-chain
  side of S07: same formula Y, same value, nnls picks either) — reported but not a load-path change.
* **Grids.** S07: 45° → 38° at 0.1°, 45° → 62° at 0.25°; Trump branch 40.1819° → 46° at 0.1° and → 38°; S02: 48.4351°
  → 36° at 0.1°, → 62° at 0.25°. The S07 down-sweep's first point (45.000°) reports "no landing" because the exact
  configuration sits on the boundary of SLSQP's feasibility tolerance after the tilt-clip; the polish at 45° (a
  separate call, 3.885618088665 vs the exact 3.885618083164, +5.5e-9) and the up-sweep's 45° point cover it.
* **Closed forms** evaluated alongside: Λ(θ) = 2 + 2(c + s)/(1 + cs), Y(θ) = (1 + 3c + s + 2cs + 2s²)/(1 + cs), the
  S02 wedge A(θ), the gap chain F_T(θ) = 2 + (2 + s)/(c + s) (derived after the sweep from the 8-row loaded set on
  (40.45°, 41.56°)); symbolic checks (sympy, in the LOG of the session): Y − Λ = (s − c)(c + s − 1)/(1 + cs); F_T − Λ =
  s(cs − 2c + 1)/((c + s)(1 + cs)); A − Λ = −c²(cs − 2s + 1)/(s²(1 + cs)) modulo c² + s² = 1.

## The T4 count (`code/t4_110.py`)

* Inputs: A107's `shadow_nodes.json` (which alive nodes S07/S02 explain) and `extract.json` (each node's LP support as
  an 11-square representative configuration: hypothesis cores + integral placements, cells of pitch 0.19 — A107's
  tolerance 0.21), the two sweep files.
* Family = the (tilt, configuration) records of the shadow's branch inside [θ_lo, θ_hi] (S07: [41.6°, 53.75°] — the
  crest to the last tilt at which the loaded set is the y-chain; S02: [θ_lo, θ_hi] read off the S02 sweep, see the
  proof note §3.4).
* Per node: canonicalise the support into the shadow's frame (A107's `struct_op`, `minimise.canon_free`), keep the
  non-slot squares, and for every family tilt greedily match the family's load-bearing squares (S07: f0 f1 f2 f4;
  S02: f1 f2 f3) to distinct support squares by nearest centre; best tilt = least max centre distance; INSIDE iff
  max centre distance ≤ 0.21 and every matched tilt within 5° (one A57 tilt cell) of the family tilt. Separately, for
  each conditioned box of the node's hypothesis (mapped into the shadow frame): the nearest family square over the
  whole family, whether the box's tilt interval meets the family's tilt range, and whether the box CONTAINS a family
  square (centre in the box and tilt in the box's interval).
* The drawing `results/box_to_grain_110.svg`: the S07 family at 43.0° (containment and pairwise SAT checked, worst
  value printed in the title), node `A60/c0_Y0324`'s conditioned box and its LP support (dashed; overlaps of one cell
  pitch are the LP's, as in A107).
