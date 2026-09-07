# A126 — method (what the code does, and the two engineering findings)

## Discipline

* READ-ONLY on every campaign and on A116/A119/A120.  A119's `check_local.py` and `exactiv.py`
  are IMPORTED (never copied, never edited) and A119's certificates and A120's certificates and
  records are READ.  All new files live under `attempts/A126-localdead-lean/` and under
  `lean/PackingCertMathlib/PackingCertMathlib/{SatInterior, LocalCert, LocalCertS07(Data),
  LocalCertS02(Data), LocalCompose, LocalCertY0230(Data)}.lean` plus
  `lean/PackingCertMathlib/scratch/A126Axioms.lean`.  `Local.lean` is NOT edited: the axiom it
  states is discharged by a theorem of the same statement in a new file, and the one lemma that
  consumed it is re-derived there (`cover_pair'`).
* One `lake build` at a time, through A119's `lakeb.py` route (repo-wide lock, BELOW-NORMAL
  priority); at most two Python processes; `PYTHONDONTWRITEBYTECODE=1`; nothing deleted
  recursively.
* Every number that reaches Lean is re-verified in exact rational arithmetic on the way out
  (`extract126.py`) and again after encoding (`gen_lean126.py`'s round trip), by code that does
  not share the generator's arithmetic.

## The pieces

| file | what it is |
|---|---|
| `code/extract126.py` | T1: subclasses A119's `Checker` so that EVERY accepted dead leaf is recorded (the parent records only the feasible ones — infeasibility rays return before its capture hook), rounds rows / boxes / multipliers onto one denominator `10⁻⁹`, and re-evaluates every Farkas bound exactly |
| `code/gen_lean126.py` | T1: emits `LocalCert<TAG>Data.lean` (one string per leaf) and `LocalCert<TAG>.lean` (the `native_decide`, the boxes and pins of `N`, the theorem), with a Python round trip through the emitted text first |
| `lean/…/SatInterior.lean` | T2: Lemma SAT for interiors, a theorem |
| `lean/…/LocalCert.lean` | T1: the reflected leaf checker, its soundness, the decoder, `CertCover`, `localDead_of_cert` |
| `lean/…/LocalCompose.lean` | T3: the YES/NO split, `localHyp_of_yes`, `node_dead_of_yes_no`, the clamp lemmas |
| `lean/…/LocalCertY0230(Data).lean` | T3: A120's four NO certificates for `k5_11_interior_Y0230`, converted by `lean/gen_case_lean.py` and replayed by `native_decide` |

## Finding E1 — the data has to be a STRING, not a list literal

`S07 (0.1, 40°)` has 2 302 dead leaves, 27 363 rows and 101 629 nonzero rational coefficients;
`S02 (0.2, 10°)` has 32 570 / 504 404 / 1 977 332.  Emitted as nested `List Rat` literals in the
A78/A93 style that is ~10⁵ (resp. 2·10⁶) numeric literals for the ELABORATOR, which is where a
generated file of this size dies — not in the kernel, and not in `native_decide`.  Emitting one
STRING per leaf costs one token per leaf and moves the decoding into the same compiled
evaluation that runs the check (`LocalCert.parseLeaf`).  Measured on `S07 (0.1, 40°)`: data file
2.70 MB, elaboration 22 s; check file including the `native_decide` over all 2 302 leaves, 20 s.

This is safe by construction, not by inspection of the decoder: `localDead_of_cert` quantifies
BOTH the check and the cover obligation over the DECODED leaves, so a wrong decode makes the
obligation harder to discharge and can never make the conclusion cheaper.

## Finding E2 — a quarter of the dead leaves are invisible to A119's capture hook

`check_local.Checker.dead` validates an infeasibility ray and RETURNS before the block that
records the leaf, so `gen_local_lean.py`'s `capture` list contains only the leaves whose Farkas
bound is a finite side bound.  On `S07 (0.1, 40°)` that is 1 556 of 2 302 (**746 rays, 32 %**);
on `S02 (0.2, 10°)` it is 26 788 of 32 570 (5 782 rays, 18 %).  A generator that trusts the hook
therefore silently emits an INCOMPLETE cover.  `extract126.CapChecker` overrides `dead`, calls
the parent first (so the parent's verdict stays authoritative and nothing is recorded that it
rejected), and rebuilds the ray's rows with A119's own `LeafRows`.

## Finding E3 — `Box` cannot carry a tilt cell that leaves `θ ∈ [0°, 90°]`

`Local.Box` holds ONE interval in the Lean tilt parameter `t = tan(θ/2)`, and a packing's poses
are normalised to `t ∈ [0, 1]`, i.e. `θ ∈ [0°, 90°]` (`isUnitSquare_exists_psq`).  A116/A119's
cells are stated in the ANGLE `θ` and are allowed to leave that domain: `S02 (0.2, 10°)`'s
`BR(0,1)` cell is `θ ∈ [−10°, +10°]`.  Folded into the fundamental domain by the square's own
90° symmetry that cell is `t ∈ [0, tan 5°] ∪ [tan 40°, 1]` — the union of TWO intervals, which
no single `Box` can express.

The emitted box keeps the INSIDE part (`t ∈ [0, tan 5°]`), which makes `N` smaller, `LocalHyp`
harder to satisfy and `LocalDead` a weaker statement — the sound direction, and the generator
now prints the count and marks the box in the file's docstring.  Of the certificates handled
here: `S07 (0.1, 40°)` has NO straddling box (all four cells are inside `[41.6°, 85°]`), so its
`N` is the certificate's exactly; `S02 (0.2, 10°)` has ONE of four (`BR(0,1)`).

The honest fix is a `Box` whose tilt field is a LIST of `t`-intervals, exactly as
`CaseChecker.CNoFam.tivs` and `ParamNoFam.PNoFam.tivs` already are — a change to `Local.lean`,
which this attempt is not allowed to edit, and which `LocalHyp`'s consumers would have to follow.

## The rounding, and why it cannot make a false leaf pass

Everything reaching Lean sits on one denominator `D = 10⁻⁹`:

* **row coefficients** are rounded to the nearest multiple of `1/D` and the row's constant is
  LOWERED by the total rounding slack over the leaf's box, so the emitted row is IMPLIED by the
  true relaxed row (A119's `gen_local_lean.py` discipline, there at `10⁻¹⁵`);
* **box bounds** are rounded OUTWARD, so the emitted box CONTAINS the true one, which can only
  lower the minimum;
* **multipliers** are rounded to the nearest multiple of `1/D` and clamped at `0`.

Each of the three can turn a true leaf into a failing one and none can do the reverse, so the
Farkas bound is re-evaluated from the emitted integers and required to exceed `s0` (a ray: `0`).
Worst margins over all leaves: `S07 (0.1, 40°)` **1.358·10⁻⁵**, `S02 (0.2, 10°)`
**9.086·10⁻⁸** — the latter is tight because that certificate's own certified minimum is only
9.8·10⁻⁸ above `s0`, and the rounding costs about 7·10⁻⁹ of it.  `10⁻⁹` is therefore the right
denominator for this corpus: `10⁻⁸` would not clear `S02 (0.2, 10°)`, `10⁻¹⁵` triples the text.
