# lean/ — Lean 4 certificates for the square-packing lab

Two independent, no-Mathlib, decidable checkers plus certificate data:

| what | file | theorem | proof method |
|---|---|---|---|
| **Upper bound** `s(11) ≤ 3.877084` (11 unit squares fit in `[0, 969271/250000]²`) | `PackingCert/Main.lean`, `Kernel.lean` | `PackingCert.trump11_ok : checkPacking Data.trump11 = true` | `native_decide` **and** kernel `decide` (axiom-free) |
| Upper bound `s(11) ≤ 3.877083591023` (tight variant) | same | `PackingCert.trump11_tight_ok` | same |
| **Lower bound** `s(11) ≥ 3.741594` (A05's 10-point unavoidable set as a measure certificate) | `PackingCert/MeasureMain.lean` | `PackingCert.Measure.s11_ge_37416 : checkMeasure Data.a05_10pt = true` | `native_decide` only |
| Lower bound `s(5) > 2.6` (perturbed Göbel 4-point measure, prototype) | same | `PackingCert.Measure.s5_gt_26` | `native_decide` |

Both checkers are `Bool`-valued functions; Lean proves *that the checker returns `true` on the
data*.  The elementary "bridge lemmas" that connect `= true` to the geometric statements over ℝ²
are **not** formalised (they need Mathlib; see "What is assumed" and
`attempts/A06-lean-setup/notes.md`).

## Toolchain / build

* elan 4.2.3, Lean **4.33.0** (`stable`), Lake 5.0.0 — pinned in `PackingCert/lean-toolchain`.
* Install elan (Windows): `elan-init.exe` from https://github.com/leanprover/elan/releases, then
  `elan default stable`. Put `%USERPROFILE%\.elan\bin` on PATH.
* Build:
  ```
  cd lean/PackingCert
  lake build            # ≈ 5 s for the packing checker; + several minutes for the measure theorem
  lake build measure_bench && .lake/build/bin/measure_bench data 40   # native timing of the measure checker
  ```
* Check axioms: `lake env lean scratch/Axioms.lean` prints
  `trump11_ok_kernel` → *no axioms*; `trump11_ok` → `native_decide` axiom (`Lean.ofReduceBool`).

## Project layout (`lean/PackingCert/`)

```
PackingCert/Geometry.lean      Pt (Int×Int), add/sub/dot/perp, Square (4 corners), edges
PackingCert/Checker.lean       Cert, checkPacking : Cert → Bool                       (upper bound)
PackingCert/Example.lean       hand-made 4-square example (+ 3 negative tests)      decide/native_decide
PackingCert/Data.lean          GENERATED from certs/trump11_certificate_int.json
PackingCert/DataTight.lean     GENERATED from certs/trump11_certificate_tight_int.json
PackingCert/Main.lean          trump11_ok, trump11_tight_ok (native_decide)
PackingCert/Kernel.lean        trump11_ok_kernel, trump11_tight_ok_kernel (decide, axiom-free)
PackingCert/Measure.lean       MCert, checkMeasure : MCert → Bool                    (lower bound)
PackingCert/MeasureExample.lean perturbed Göbel example
PackingCert/MeasureData.lean   GENERATED from attempts/A08-measure-verify/tests/a05_10pt.json
PackingCert/MeasureMain.lean   s5_gt_26, s11_ge_37416 (native_decide)
MeasureBench.lean              `lake exe measure_bench` — native timing / box counts
scratch/                       ad-hoc files (Axioms.lean etc.), not part of the library
```

## Upper-bound checker: `checkPacking`

Certificate `Cert = {denom, sideNum, sideDen, squares}`; every coordinate is an integer meaning
`coord/denom`; container `[0, sideNum/sideDen]²`. `checkPacking c = true` iff

1. `0 < denom`, `0 < sideDen`;
2. each square is a genuine unit square: `e = p1−p0`, `n = (−e.y, e.x)`, `e·e = denom²`,
   `p2 = p1 ± n`, `p3 = p0 ± n` (same sign);
3. each corner is strictly inside: `0 < x`, `x·sideDen < sideNum·denom` (same for `y`);
4. each of the 55 pairs is strictly separated by one of the 8 edge vectors `n` of the two squares:
   all corners of one project strictly below all corners of the other (`a·n < b·n`).

**Bridge lemma (assumed, elementary):** `checkPacking c = true` ⇒ the 11 closed unit squares
`conv{corners/denom}` are contained in `[0, side]²` and pairwise disjoint (any linear functional
that strictly separates two finite point sets separates their convex hulls; the choice of axes
only affects completeness, never soundness). Hence `s(11) ≤ side`.

## Lower-bound checker: `checkMeasure`

Certificate `MCert = {n, side, atoms : List ⟨px, py, w⟩, fuel}` (all `Rat`).
`checkMeasure c = true` iff all `w ≥ 0`, `Σ w < n`, and the branch-and-bound over
`(t, cx, cy) ∈ [0,1] × [0,side]²` (`t = tan(θ/2)`, `θ ∈ [0, π/2]`) discharges every box within
depth `fuel`, where a box `[t0,t1]×[x0,x1]×[y0,y1]` is discharged if
* after clipping the centre ranges to `wLo/2 ≤ c ≤ side − wLo/2`
  (`wLo = min(w(t0), w(t1))`, `w = cos θ + sin θ` unimodal in `t`) it is empty, or
* the atoms provably inside `Q(t,cx,cy)` for **all** parameters of the box (rational interval
  arithmetic on `u = cos·(px−cx)+sin·(py−cy)`, `v = −sin·(px−cx)+cos·(py−cy)`, `|u|,|v| ≤ ½`,
  with `cos ∈ [cos t1, cos t0]`, `sin ∈ [sin t0, sin t1]` exact rationals) have total weight ≥ 1;
* otherwise it is bisected along the widest dimension (`t`-width counted ×2), children inherit the
  mass already certified and drop atoms provably outside.

**Bridge lemma (assumed, elementary):** `checkMeasure c = true` ⇒ every closed unit square
`Q ⊂ [0, side]²` has `μ(Q) ≥ 1` (all such squares are covered by the box tree; interval arithmetic
over-approximates; `θ ∈ [0, π/2]` suffices by symmetry) ⇒ no `n` pairwise-disjoint closed unit
squares fit in `[0, side]²` ⇒ `s(n) ≥ side`.  Semantics match `certs/verify_measure.py` (A08).

**Caveat:** certificates must have positive margin — an atom exactly on the boundary of some
admissible square (e.g. Göbel's `(1,1)` and the wall-flush upright square `[0,1]²`) can never be
certified by boxes.  Kernel `decide` does not work for this checker (`Rat` normalisation uses
well-founded recursion); only `native_decide`.

## Regenerating the data (reproducible pipeline)

```
# upper bound: certs/*.json (A03) → Data.lean / DataTight.lean
python lean/gen_cert_lean.py certs/trump11_certificate_int.json       --name trump11
python lean/gen_cert_lean.py certs/trump11_certificate_tight_int.json --name trump11_tight -o lean/PackingCert/PackingCert/DataTight.lean
# lower bound: A08-format measure JSON → MeasureData.lean (fuel = max bisection depth)
python lean/gen_measure_lean.py attempts/A08-measure-verify/tests/a05_10pt.json --fuel 40 --name a05_10pt
cd lean/PackingCert && lake build
```
`gen_cert_lean.py` accepts integer corners over a common denominator, rational corners, or
centre + `t = tan(θ/2)`; it re-checks the certificate in exact `Fraction` arithmetic before
writing Lean, so a failing `lake build` means "Lean disagrees", never "bad input".
`gen_measure_lean.py` accepts the `verify_measure.py` JSON format (incl. `"symmetry": "D4"`).

How the certificates were generated: see `certs/` (A03: exact 60-digit solution of Trump's contact
system, scaled by `s_c/s*` and rounded to rationals; A05/A08: optimised 10-point unavoidable set).

## `lean/PackingCertMathlib`

Template Mathlib project for the bridge lemmas.  **Not built**: `lake exe cache get` needs
≈ 5 GB + a second 3 GB toolchain and ran this machine's disk out of space (see notes.md).
`BridgeSketch.lean` there is an unbuilt sketch of the intended statements.
