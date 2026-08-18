# lean/ — Lean 4 certificates for the square-packing lab

Two independent, no-Mathlib, decidable checkers plus certificate data:

| what | file | theorem | proof method |
|---|---|---|---|
| **Upper bound** `s(11) ≤ 3.877084` (11 unit squares fit in `[0, 969271/250000]²`) | `PackingCert/Main.lean`, `Kernel.lean` | `PackingCert.trump11_ok : checkPacking Data.trump11 = true` | `native_decide` **and** kernel `decide` (axiom-free) |
| Upper bound `s(11) ≤ 3.877083591023` (tight variant) | same | `PackingCert.trump11_tight_ok` | same |
| **Lower bound `s(11) ≥ 3.80`** — NEW (published bound 3.7889): A07's LP measure certificate `certs/measure_certificate_3.80.json` (1069 atoms, mass 10.801639 < 11) | `PackingCertSlow.lean` (**separate target**: `lake build PackingCertSlow`, 654 s) | `PackingCert.MeasureI.s11_ge_3_80 : checkMeasureI Data.cert_3_80 = true` | `native_decide` (integer checker), 5 837 883 boxes |
| Lower bound `s(11) ≥ 3.741594` (A05's 10-point unavoidable set) | `PackingCert/MeasureIntMain.lean`, `MeasureMain.lean` | `PackingCert.MeasureI.a05_10pt_int_ok : checkMeasureI Data.a05_10pt_int = true` (Int checker, 571k boxes, 9 s) and `PackingCert.Measure.s11_ge_37416 : checkMeasure Data.a05_10pt = true` (Rat checker, 97 s) | `native_decide` |
| Lower bound `s(5) > 2.6` (perturbed Göbel 4-point measure, prototype) | same | `PackingCert.MeasureI.goebel26_int_ok`, `PackingCert.Measure.s5_gt_26`; kernel `decide` also works for the Int version (`scratch/IntKernel.lean`, 30 s, no axioms) | `native_decide` / `decide` |

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
  lake build                    # default target: ≈ 80 s clean (UB theorems 5 s; A05 measure theorems 71 s + 13 s; C/dynlib compilation)
  lake build PackingCertSlow    # the s(11) ≥ 3.80 theorem: 654 s ≈ 11 min (5 837 883 boxes)  [25 min without precompileModules]
  lake build measure_bench && .lake/build/bin/measure_bench int_3_80 48   # native timing / box count (≈ 9 min)
  ```
* Axioms (`lake env lean scratch/Axioms.lean`, `scratch/IntKernel.lean`):
  `trump11_ok_kernel`, `trump11_tight_ok_kernel`, `goebel26_int_kernel` → **no axioms**;
  `trump11_ok`, `a05_10pt_int_ok`, `s11_ge_3_80` → the `native_decide` axiom only (`Lean.ofReduceBool`);
  the `Rat` checker theorems (`s11_ge_37416`, `s5_gt_26`) additionally carry `propext, Classical.choice, Quot.sound` (from `Rat`'s definitions).

## Project layout (`lean/PackingCert/`)

```
PackingCert/Geometry.lean      Pt (Int×Int), add/sub/dot/perp, Square (4 corners), edges
PackingCert/Checker.lean       Cert, checkPacking : Cert → Bool                       (upper bound)
PackingCert/Example.lean       hand-made 4-square example (+ 3 negative tests)      decide/native_decide
PackingCert/Data.lean          GENERATED from certs/trump11_certificate_int.json
PackingCert/DataTight.lean     GENERATED from certs/trump11_certificate_tight_int.json
PackingCert/Main.lean          trump11_ok, trump11_tight_ok (native_decide)
PackingCert/Kernel.lean        trump11_ok_kernel, trump11_tight_ok_kernel (decide, axiom-free)
PackingCert/Measure.lean       MCert, checkMeasure : MCert → Bool        (lower bound, Rat prototype)
PackingCert/MeasureExample.lean perturbed Göbel example
PackingCert/MeasureData.lean   GENERATED from attempts/A08-measure-verify/tests/a05_10pt.json
PackingCert/MeasureMain.lean   s5_gt_26, s11_ge_37416 (native_decide, Rat checker)
PackingCert/MeasureInt.lean    MCertI, checkMeasureI : MCertI → Bool     (lower bound, all-Int, = verify_measure.py scaling)
PackingCert/MeasureIntData*.lean GENERATED (--int): 3.80 cert, 3.82 cert (fails), A05 set, Göbel
PackingCert/MeasureIntMain.lean a05_10pt_int_ok, goebel26_int_ok (native_decide)
PackingCertSlow.lean           s11_ge_3_80  — separate lib target `PackingCertSlow`
MeasureBench.lean              `lake exe measure_bench` — native timing / box counts (modes: goebel, grid, data, int_a05, int_3_80, int_3_82)
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

## Lower-bound checkers: `checkMeasureI` (Int, used for the real theorems) and `checkMeasure` (Rat prototype)

Both implement the claim in the header of `certs/verify_measure.py`: for μ = Σ wᵢ δ_{pᵢ}, wᵢ ≥ 0,
Σ wᵢ < n, **every closed unit square Q ⊆ [0,s]² has μ(Q) ≥ 1**, with θ ∈ [0,π/2] via t = tan(θ/2) ∈ [0,1],
`Q ⊆ [0,s]² ⟺ w/2 ≤ cx,cy ≤ s−w/2` (w = cos θ + sin θ), and `p ∈ Q ⟺ |u| ≤ ½ ∧ |v| ≤ ½`.
`checkMeasureI` uses exactly A08's integer scaling (t = T/2^K, K = depth+1; lengths × den(s)·2^(depth+2);
atoms over their own PD; weights over WD; NEED = WD; floor midpoints; tscale 2; outward-rounded clipping),
so its box tree coincides with the Python verifier's up to the root partition (5 837 883 vs 5 836 650 boxes on
the 3.80 certificate; 570 941 vs 570 943 Rat-vs-Int on the A05 set; 795 = 795 on Göbel). It is ~10× faster than
the Rat version (no gcds) and kernel-`decide`-able (demonstrated on the Göbel example only; millions of boxes
are far beyond kernel evaluation).

Rat prototype: certificate `MCert = {n, side, atoms : List ⟨px, py, w⟩, fuel}` (all `Rat`).
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

**Bridge lemma (assumed, elementary; stated in words in the header of `PackingCert/MeasureInt.lean`):**
`checkMeasure(I) c = true` ⇒ every closed unit square
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
# lower bound: A08-format measure JSON → Lean data (fuel = max bisection depth; --int for the Int checker)
python lean/gen_measure_lean.py certs/measure_certificate_3.80.json --fuel 48 --int --name cert_3_80 -o lean/PackingCert/PackingCert/MeasureIntData.lean
python lean/gen_measure_lean.py attempts/A08-measure-verify/tests/a05_10pt.json --fuel 40 --int --name a05_10pt_int -o lean/PackingCert/PackingCert/MeasureIntDataA05.lean
python lean/gen_measure_lean.py attempts/A08-measure-verify/tests/a05_10pt.json --fuel 40 --name a05_10pt   # Rat version
cd lean/PackingCert && lake build && lake build PackingCertSlow
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

### Added by the advisor (2026-08-18)
| theorem | target | build | axioms |
|---|---|---|---|
| `PackingCert.MeasureI.s11_ge_3_81 : checkMeasureI Data.cert_3_81 = true` (certs/measure_certificate_3.81.json, 980 atoms, mass 10.9852) | `lake build PackingCertSlow381` | 12 min | native_decide only |
| `PackingCert.MeasureI.s11_ge_3_82 : checkMeasureI Data.cert_3_82 = true` (certs/measure_certificate_3.82.json, 1769 atoms, mass 10.985474) | `lake build PackingCertSlow382` | 26.5 min | native_decide only |
Data files generated with `python lean/gen_measure_lean.py certs/measure_certificate_3.8X.json --fuel 48 --int --name cert_3_8X -o lean/PackingCert/PackingCert/MeasureIntData38X.lean`.
