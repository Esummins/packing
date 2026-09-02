/-!
# Lower-bound measure checker (verbatim copy of `lean/PackingCert/PackingCert/MeasureInt.lean`)

Core Lean 4 only, no Mathlib.  Duplicated here (A64) because the `PackingCert` project is pinned
to Lean 4.33.0 while this project uses the Mathlib toolchain; keeping a byte-identical copy of the
definitions is what makes the bridge theorem of `MeasureBridge.lean` a statement *about the same
checker*.  Everything from the original header onwards is unmodified:

# Lower-bound "measure certificate" checker — all-integer version (`checkMeasureI`)

Same mathematics as `PackingCert/Measure.lean` (the `Rat` prototype), but with the fixed
integer scaling of `certs/verify_measure.py` (attempt A08, "INTEGER ARITHMETIC" block), so
that the box tree and every decision are literally the same computation as the independent
Python verifier, and only `Int`/`Nat` `+ * ≤ <` are used (GMP-fast, no gcds, and in
principle kernel-`decide`-able).

## The claim being certified (identical to the header of certs/verify_measure.py)

Let `μ = Σᵢ wᵢ δ_{pᵢ}` be a finite atomic measure on the plane with rational atoms `pᵢ` and
rational weights `wᵢ ≥ 0`, total mass `Σ wᵢ < n`.  Suppose

    (H)  every CLOSED unit square `Q` (any orientation) with `Q ⊆ [0,s]²` has `μ(Q) ≥ 1`.

Then no `n` pairwise-disjoint closed unit squares fit in `[0,s]²` (each would carry mass ≥ 1,
total ≥ n > Σ wᵢ), and — since a packing of side `s' < s` can be scaled up by `s/s'` and its
squares shrunk back to unit size, making them pairwise disjoint and closed inside `[0,s]²` —
`s(n) ≥ s`.

`checkMeasureI c = true` decides (H) by branch and bound; the checker itself is `Bool`-valued
and proven `= true` by evaluation.  **Bridge lemma (assumed, NOT formalised in Lean):**
`checkMeasureI c = true ⇒ (H) ∧ Σ wᵢ < n ∧ all wᵢ ≥ 0`, whose proof uses only:

* θ ∈ [0, π/2] covers all orientations (a square is invariant under rotation by π/2), and
  `t = tan(θ/2) ∈ [0,1]` parametrises it with `cos θ = (1−t²)/(1+t²)` (decreasing on [0,1]) and
  `sin θ = 2t/(1+t²)` (increasing on [0,1]) — so `[cos t1, cos t0]`, `[sin t0, sin t1]` are
  exact enclosures over `t ∈ [t0,t1]`;
* `Q(c,θ) ⊆ [0,s]²  ⟺  w/2 ≤ cx ≤ s − w/2 ∧ w/2 ≤ cy ≤ s − w/2` with `w = cos θ + sin θ` (≥ 1),
  and `w` is unimodal in `t` so `min(w(t0), w(t1)) ≤ w(t)` on `[t0,t1]`; hence every admissible
  centre lies in `[1/2, s−1/2]²` (the root box) and in the clipped sub-boxes;
* `p ∈ Q(c,θ)  ⟺  |u| ≤ 1/2 ∧ |v| ≤ 1/2`, `u = cos θ (px−cx) + sin θ (py−cy)`,
  `v = −sin θ (px−cx) + cos θ (py−cy)`; interval arithmetic over-approximates `u, v`, so
  "inside for the whole box" and "outside for the whole box" are sound; atoms inside for a box
  stay inside for its sub-boxes (mass is inherited), atoms outside can be dropped (only lowers
  the computed mass);
* the two halves of a bisection cover the box, so the leaves cover the admissible set; the
  outward-rounded clipping keeps every admissible placement.

## Integer scaling (as in verify_measure.py)

`K = depth + 1`; `t = T / 2^K`, `T ∈ [0, 2^K]`; `cos = (4^K − T²)/(4^K + T²)`,
`sin = 2T·2^K/(4^K + T²)`.  Lengths are scaled by `D = den(s)·2^(depth+2)`: `cx = X/D`,
`s = SD/D` with `SD = num(s)·2^(depth+2)`.  Atoms keep their own denominator `PD`
(`px = PXn/PD`).  Weights are integers over a common denominator `WD`; the mass test
`Σ ≥ 1` becomes `Σ WI ≥ WD`.  All comparisons are cross-multiplied.
-/

namespace PackingCert.MeasureI

structure IAtom where
  px : Int      -- numerator of x over pd
  py : Int      -- numerator of y over pd
  pd : Int      -- denominator (> 0)
  w  : Int      -- weight numerator over the certificate's wd (≥ 0)
deriving Repr

structure MCertI where
  n     : Nat
  sNum  : Int
  sDen  : Int
  wd    : Int          -- common weight denominator (> 0)
  depth : Nat          -- max bisection depth (= fuel); fixes the integer scale
  atoms : List IAtom
deriving Repr

structure IBox where
  T0 : Int
  T1 : Int
  X0 : Int
  X1 : Int
  Y0 : Int
  Y1 : Int
deriving Repr

/-- Scale constants derived from the certificate. -/
structure Ctx where
  K     : Nat
  TROOT : Int   -- 2^K
  P4    : Int   -- 4^K
  D     : Int   -- den(s) * 2^(depth+2)
  SD    : Int   -- num(s) * 2^(depth+2)
  NEED  : Int   -- = wd  (mass ≥ 1  ⟺  Σ WI ≥ wd)

def mkCtx (c : MCertI) : Ctx :=
  let K := c.depth + 1
  { K := K
    TROOT := (2 : Int) ^ K
    P4 := (4 : Int) ^ K
    D := c.sDen * (2 : Int) ^ (c.depth + 2)
    SD := c.sNum * (2 : Int) ^ (c.depth + 2)
    NEED := c.wd }

/-- `(cn, sn, dn)` with `cos = cn/dn`, `sin = sn/dn` at `t = T/2^K`. -/
@[inline] def trig (ctx : Ctx) (T : Int) : Int × Int × Int :=
  let TT := T * T
  (ctx.P4 - TT, 2 * T * ctx.TROOT, ctx.P4 + TT)

/-- Enclosure `(Clo, Chi, Slo, Shi, E)`: `cos ∈ [Clo,Chi]/E`, `sin ∈ [Slo,Shi]/E` on `[T0,T1]`. -/
def boxTrig (ctx : Ctx) (T0 T1 : Int) : Int × Int × Int × Int × Int :=
  let (cn0, sn0, dn0) := trig ctx T0
  let (cn1, sn1, dn1) := trig ctx T1
  (cn1 * dn0, cn0 * dn1, sn0 * dn1, sn1 * dn0, dn0 * dn1)

@[inline] def imul4 (a0 a1 b0 b1 : Int) : Int × Int :=
  let p1 := a0 * b0
  let p2 := a0 * b1
  let p3 := a1 * b0
  let p4 := a1 * b1
  (min (min p1 p2) (min p3 p4), max (max p1 p2) (max p3 p4))

/-- Interval enclosures of `2u·(E·PD·D)` and `2v·(E·PD·D)`, and the bound `lim = E·PD·D`. -/
@[inline] def projI (ctx : Ctx) (Clo Chi Slo Shi E : Int) (b : IBox) (a : IAtom) :
    Int × Int × Int × Int × Int :=
  let dxlo := a.px * ctx.D - b.X1 * a.pd
  let dxhi := a.px * ctx.D - b.X0 * a.pd
  let dylo := a.py * ctx.D - b.Y1 * a.pd
  let dyhi := a.py * ctx.D - b.Y0 * a.pd
  let lim := E * a.pd * ctx.D
  let (a0, a1) := imul4 Clo Chi dxlo dxhi
  let (b0, b1) := imul4 Slo Shi dylo dyhi
  let (c0, c1) := imul4 (-Shi) (-Slo) dxlo dxhi
  let (d0, d1) := imul4 Clo Chi dylo dyhi
  (2 * (a0 + b0), 2 * (a1 + b1), 2 * (c0 + d0), 2 * (c1 + d1), lim)

/-- Atom inside `Q` for every parameter of the box: `|u| ≤ 1/2 ∧ |v| ≤ 1/2`. -/
@[inline] def insideAll (u0 u1 v0 v1 lim : Int) : Bool :=
  u1 ≤ lim && -lim ≤ u0 && v1 ≤ lim && -lim ≤ v0

/-- Atom outside `Q` for every parameter of the box: `u > 1/2 ∨ u < −1/2 ∨ v > 1/2 ∨ v < −1/2`. -/
@[inline] def outsideAll (u0 u1 v0 v1 lim : Int) : Bool :=
  lim < u0 || u1 < -lim || lim < v0 || v1 < -lim

/-- Sift the undecided atoms of a box: add the weight of atoms inside-for-all to `sure`,
drop atoms outside-for-all, keep the rest.  Stops early once `sure ≥ NEED`.
Returns `(covered, sure', undecided')`. -/
def sift (ctx : Ctx) (Clo Chi Slo Shi E : Int) (b : IBox) :
    List IAtom → Int → List IAtom → Bool × Int × List IAtom
  | [], sure, acc => (sure ≥ ctx.NEED, sure, acc)
  | a :: as, sure, acc =>
    if sure ≥ ctx.NEED then (true, sure, acc)
    else
      let (u0, u1, v0, v1, lim) := projI ctx Clo Chi Slo Shi E b a
      if insideAll u0 u1 v0 v1 lim then sift ctx Clo Chi Slo Shi E b as (sure + a.w) acc
      else if outsideAll u0 u1 v0 v1 lim then sift ctx Clo Chi Slo Shi E b as sure acc
      else sift ctx Clo Chi Slo Shi E b as sure (a :: acc)

/-- Clip the centre ranges to `wLo/2 ≤ c ≤ s − wLo/2`, `wLo = min(w(t0), w(t1))`, rounded
OUTWARD (floor / ceil; `Int./` is floor for positive divisors).  `none` if vacuous. -/
def clipI (ctx : Ctx) (b : IBox) : Option IBox :=
  let (cn0, sn0, dn0) := trig ctx b.T0
  let (cn1, sn1, dn1) := trig ctx b.T1
  let wn0 := cn0 + sn0
  let wn1 := cn1 + sn1
  let (wn, wd) := if wn0 * dn1 ≤ wn1 * dn0 then (wn0, dn0) else (wn1, dn1)
  let lo := (wn * ctx.D) / (2 * wd)
  let hi := -((-(2 * ctx.SD * wd - wn * ctx.D)) / (2 * wd))
  let X0 := max b.X0 lo
  let X1 := min b.X1 hi
  let Y0 := max b.Y0 lo
  let Y1 := min b.Y1 hi
  if X0 ≤ X1 && Y0 ≤ Y1 then some { b with X0 := X0, X1 := X1, Y0 := Y0, Y1 := Y1 } else none

/-- Bisect the widest dimension (`t`-width counted ×2 = `tscale`), floor midpoints. -/
def splitI (ctx : Ctx) (b : IBox) : IBox × IBox :=
  let wt := (b.T1 - b.T0) * 2 * ctx.D
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

/-- Discharge a box (fuel = remaining bisections). -/
def go (ctx : Ctx) : Nat → IBox → List IAtom → Int → Bool
  | 0, b, atoms, sure =>
    match clipI ctx b with
    | none => true
    | some b' =>
      let (Clo, Chi, Slo, Shi, E) := boxTrig ctx b'.T0 b'.T1
      (sift ctx Clo Chi Slo Shi E b' atoms sure []).1
  | fuel + 1, b, atoms, sure =>
    match clipI ctx b with
    | none => true
    | some b' =>
      let (Clo, Chi, Slo, Shi, E) := boxTrig ctx b'.T0 b'.T1
      let (cov, sure', rest) := sift ctx Clo Chi Slo Shi E b' atoms sure []
      if cov then true
      else
        let p := splitI ctx b'
        go ctx fuel p.1 rest sure' && go ctx fuel p.2 rest sure'

/-- Root box: `T ∈ [0, 2^K]`, centres in `[1/2, s − 1/2]²` (every admissible centre is there
because `w ≥ 1`). -/
def rootBox (ctx : Ctx) : IBox :=
  let lo := ctx.D / 2
  ⟨0, ctx.TROOT, lo, ctx.SD - lo, lo, ctx.SD - lo⟩

/-- The full check: positive denominators, weights ≥ 0, total mass < n, and every box discharged. -/
def checkMeasureI (c : MCertI) : Bool :=
  let ctx := mkCtx c
  0 < c.sDen && 0 < c.wd &&
  c.atoms.all (fun a => 0 < a.pd && 0 ≤ a.w) &&
  (c.atoms.foldl (fun acc a => acc + a.w) 0 < (c.n : Int) * c.wd) &&
  go ctx c.depth (rootBox ctx) c.atoms 0

/-! ## Instrumented variant (box count) for benchmarking. -/

def goCount (ctx : Ctx) : Nat → IBox → List IAtom → Int → Bool × Nat
  | 0, b, atoms, sure =>
    match clipI ctx b with
    | none => (true, 1)
    | some b' =>
      let (Clo, Chi, Slo, Shi, E) := boxTrig ctx b'.T0 b'.T1
      ((sift ctx Clo Chi Slo Shi E b' atoms sure []).1, 1)
  | fuel + 1, b, atoms, sure =>
    match clipI ctx b with
    | none => (true, 1)
    | some b' =>
      let (Clo, Chi, Slo, Shi, E) := boxTrig ctx b'.T0 b'.T1
      let (cov, sure', rest) := sift ctx Clo Chi Slo Shi E b' atoms sure []
      if cov then (true, 1)
      else
        let p := splitI ctx b'
        let r1 := goCount ctx fuel p.1 rest sure'
        if !r1.1 then (false, r1.2 + 1) else
        let r2 := goCount ctx fuel p.2 rest sure'
        (r2.1, r1.2 + r2.2 + 1)

def checkMeasureICount (c : MCertI) : Bool × Nat :=
  let ctx := mkCtx c
  let ok0 := 0 < c.sDen && 0 < c.wd &&
    c.atoms.all (fun a => 0 < a.pd && 0 ≤ a.w) &&
    (c.atoms.foldl (fun acc a => acc + a.w) 0 < (c.n : Int) * c.wd)
  let r := goCount ctx c.depth (rootBox ctx) c.atoms 0
  (ok0 && r.1, r.2)

end PackingCert.MeasureI
