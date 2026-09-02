import PackingCertMathlib.MeasureChecker

/-!
# The `verify_measure.py` driver as a Lean checker (`checkMeasurePy`) — A75, depgraph V.MEAS

Core Lean 4 only, no Mathlib.  `checkMeasureI` (`MeasureChecker.lean`, A64/A06) is the
integer decision core of `certs/verify_measure.py` and its soundness is A.F2
(`MeasureBridge.lean`).  The Python DRIVER (`Verifier.run` / `covered` / `root_boxes` /
`main`) is a GENERALISATION of `checkMeasureI`; this file models that driver exactly, so
that the soundness theorem of `MeasurePyBridge.lean` speaks about the Python program's
accept rule rather than about one instance of it:

* `--tscale T` (integer; default 2): the `t`-width weight in the split rule
  (`checkMeasureI` hard-codes 2);
* `--split k`: the root `[0,1] × [1/2, s−1/2]²` is first cut into a `4^k` grid in
  `(cx, cy)` (`root_boxes`), each cell starting at depth counter `2k` — so each root
  cell gets `depth − 2k` further bisections (`fuel`);
* `--strict-margin m`: the mass threshold is `NEED = ⌈(1 + m)·WD⌉` (a certificate
  parameter `need` here, gated `wd ≤ need`);
* the float shortlist (`float_candidates`) and its "float reject" early return: modelled
  by an ORACLE `pick : IBox → List IAtom → Int → IAtom → Bool` (any function of the
  clipped box, the not-yet-certified atoms and the certified mass).  Soundness holds for
  EVERY oracle; the Python run is one instance, `pick := fun _ _ _ _ => true` is
  `--no-float-prepass`;
* `covered` never DROPS atoms (`checkMeasureI.sift` drops `outsideAll` atoms): the
  `known` index tuple of certified atoms, inherited by the children, is carried here as
  its complement `rest` (the atoms not yet certified, heavy-first order) + `sure`;
* `main`'s `s < 1` early PASS ("no unit square fits") is the `vacuousPass` disjunct;
* `--scale-weights` and the D4 `symmetry` expansion are certificate preprocessing (the
  scaled/expanded atom list IS the certificate the checker sees; the `total < n` gate is
  applied after scaling in `main`); `--n` overrides the `n` field.

Not modelled (decision-neutral for PASS): witness construction/reporting, the
`--max-witnesses(-per-box)` early stops (they only shorten a FAIL), multiprocessing
(root cells are independent; PASS ⟺ every cell passes = `List.all`), statistics.

Per-box order (`Verifier.run`): clip (vacuous) → covered (on the clipped box) → depth
check → split.  Integer primitives (`clipI`, `boxTrig`, `projI`, `insideAll`, floor
midpoints) are the A64 definitions, byte-identical to the Python `clip_int`, `box_trig`,
`atom_inside_int`, `(X0 + X1) >> 1`.
-/

namespace PackingCert.MeasurePy

open PackingCert.MeasureI

/-- `Verifier.covered`: test the not-yet-certified atoms the oracle picks; certified
atoms add their weight to `sure`, the others are kept (nothing is dropped).  Early
stop at `NEED`.  Returns `(covered, sure', rest')`. -/
def siftPy (ctx : Ctx) (Clo Chi Slo Shi E : Int) (b : IBox) (pick : IAtom → Bool) :
    List IAtom → Int → List IAtom → Bool × Int × List IAtom
  | [], sure, acc => (sure ≥ ctx.NEED, sure, acc)
  | a :: as, sure, acc =>
    if sure ≥ ctx.NEED then (true, sure, acc)
    else
      let (u0, u1, v0, v1, lim) := projI ctx Clo Chi Slo Shi E b a
      if pick a && insideAll u0 u1 v0 v1 lim then
        siftPy ctx Clo Chi Slo Shi E b pick as (sure + a.w) acc
      else siftPy ctx Clo Chi Slo Shi E b pick as sure (a :: acc)

/-- `splitI` with the `t`-width weight `tscale` as a parameter. -/
def splitPy (ctx : Ctx) (ts : Int) (b : IBox) : IBox × IBox :=
  let wt := (b.T1 - b.T0) * ts * ctx.D
  let wx := (b.X1 - b.X0) * ctx.TROOT
  let wy := (b.Y1 - b.Y0) * ctx.TROOT
  if wx ≥ wy && wx ≥ wt then
    let m := (b.X0 + b.X1) / 2
    ({ b with X1 := m }, { b with X0 := m })
  else if wy ≥ wt then
    let m := (b.Y0 + b.Y1) / 2
    ({ b with Y1 := m }, { b with Y0 := m })
  else
    let m := (b.T0 + b.T1) / 2
    ({ b with T1 := m }, { b with T0 := m })

/-- `Verifier.run`, one stack frame (fuel = `depth − d`). -/
def goPy (ctx : Ctx) (ts : Int) (pick : IBox → List IAtom → Int → IAtom → Bool) :
    Nat → IBox → List IAtom → Int → Bool
  | 0, b, rest, sure =>
    match clipI ctx b with
    | none => true
    | some b' =>
      let (Clo, Chi, Slo, Shi, E) := boxTrig ctx b'.T0 b'.T1
      (siftPy ctx Clo Chi Slo Shi E b' (pick b' rest sure) rest sure []).1
  | fuel + 1, b, rest, sure =>
    match clipI ctx b with
    | none => true
    | some b' =>
      let (Clo, Chi, Slo, Shi, E) := boxTrig ctx b'.T0 b'.T1
      let (cov, sure', rest') := siftPy ctx Clo Chi Slo Shi E b' (pick b' rest sure) rest sure []
      if cov then true
      else
        let p := splitPy ctx ts b'
        goPy ctx ts pick fuel p.1 rest' sure' && goPy ctx ts pick fuel p.2 rest' sure'

/-- `Verifier.root_boxes k`: the root cut into `4^k` cells, `step = (hi − lo) >> k`. -/
def rootGrid (ctx : Ctx) (k : Nat) : List IBox :=
  let lo := ctx.D / 2
  let hi := ctx.SD - lo
  let m : Nat := 2 ^ k
  let step := (hi - lo) / (m : Int)
  (List.range m).flatMap fun (i : Nat) => (List.range m).map fun (j : Nat) =>
    ⟨0, ctx.TROOT, lo + step * (i : Int), lo + step * ((i : Int) + 1),
      lo + step * (j : Int), lo + step * ((j : Int) + 1)⟩

/-- `assert step << k == hi - lo`. -/
def gridOK (ctx : Ctx) (k : Nat) : Bool :=
  let lo := ctx.D / 2
  let hi := ctx.SD - lo
  let m : Nat := 2 ^ k
  ((hi - lo) / (m : Int)) * (m : Int) == hi - lo

/-- The structural gates of `main`/`load_certificate`: positive denominators, weights
≥ 0, total mass `< n` (after any scaling), `wd ≤ need` (margin ≥ 0). -/
def gatesPy (c : MCertI) (need : Int) : Bool :=
  0 < c.sDen && 0 < c.wd && c.wd ≤ need &&
  c.atoms.all (fun a => 0 < a.pd && 0 ≤ a.w) &&
  (c.atoms.foldl (fun acc a => acc + a.w) 0 < (c.n : Int) * c.wd)

/-- `main`'s `s < 1` shortcut: "no unit square fits; vacuous PASS". -/
def vacuousPass (c : MCertI) (need : Int) : Bool :=
  gatesPy c need && c.sNum < c.sDen

/-- **The Python verifier's accept rule**: gates, and either the `s < 1` shortcut or
the root-grid assertion + every root cell discharged with `fuel = depth − 2k`
(`NEED = need`). -/
def checkMeasurePy (c : MCertI) (need ts : Int) (k : Nat)
    (pick : IBox → List IAtom → Int → IAtom → Bool) : Bool :=
  let ctx : Ctx := { mkCtx c with NEED := need }
  vacuousPass c need ||
  (gatesPy c need && gridOK ctx k &&
    (rootGrid ctx k).all (fun b => goPy ctx ts pick (c.depth - 2 * k) b c.atoms 0))

/-- The `--no-float-prepass` oracle. -/
def pickAll : IBox → List IAtom → Int → IAtom → Bool := fun _ _ _ _ => true

end PackingCert.MeasurePy
