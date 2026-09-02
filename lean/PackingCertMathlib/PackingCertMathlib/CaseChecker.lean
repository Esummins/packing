import PackingCertMathlib.MeasureChecker

/-!
# Case-LP certificate checker (`checkCaseI`) — A70, depgraph node V.CASE

Core Lean 4 only, no Mathlib.  The decision core of `verify_case.py`
(canonical copy `attempts/A53-simple-strata/code/verify_case.py`, sha256 `521cb01f…`,
frozen spec `docs/specs/case_lp_certificate_v1.md`), on top of the measure checker
of `MeasureChecker.lean` (A64): the certificate additionally carries **cores** (closed
squares that hypothetical family members contain), **NO-families** (centre-box ×
t-interval exemption zones), and a **budget** `b = n − #cores`; a box may now also be
discharged **EXEMPT** — provably meeting a core for all its parameters (SAT
non-separation on all four edge-normal axes, `core_exempt_frac`), or provably inside a
NO-family zone (`nofam_exempt`).

Faithfulness notes (deviations from the Python driver, all decision-neutral):
* the float shortlist / float pre-filter layers are omitted (they only *shortlist*;
  every Python accept decision is re-derived exactly — spec §5).  Omitting the float
  core pre-filter can only grant *more* exemptions than the Python run (the exact test
  decides); omitting the mass shortlist can only certify *more* atoms.  Both exact
  tests here are the Python exact tests verbatim;
* the `4^k` initial grid split of the root box (a parallelisation feature of the
  driver) is not reproduced: `checkCaseI` bisects from the root box with
  `fuel = depth`.  The box *scales* (`D`, `K`) are those of the declared `depth`,
  identical to a `--depth <depth>` Python run;
* exact rational arithmetic uses core-Lean `Rat` where the Python uses
  `fractions.Fraction` (the exempt tests); the integer-scaled mass/clip/split layer is
  shared verbatim with `MeasureChecker.lean` (`sift`, `clipI`, `splitI`).

The per-box decision sequence is the Python `Verifier.run` order: clip (vacuous) →
exempt (on the clipped box) → covered → split / fail.

Soundness (`checkCaseI` PASS ⟹ claims (P1) + (P2) of the frozen spec ⟹ no strict
family satisfies the pin hypotheses at side `s`) is proved in `CaseBridge.lean`.
-/

namespace PackingCert.CaseI

open PackingCert.MeasureI

/-- A core square: centre `(kx, ky)`, orientation `tan(θ_m/2) = tm ∈ [0,1]`,
half-side `a > 0` (loader gate of `verify_case.py`; spec §2 text also mentions
`a = 0`, but the deployed loader rejects it — A70 finding). -/
structure CCore where
  kx : Rat
  ky : Rat
  tm : Rat
  a  : Rat
deriving Repr

/-- A NO-family zone: centre rectangle `[x0,x1]×[y0,y1]` with closed t-intervals. -/
structure CNoFam where
  x0 : Rat
  x1 : Rat
  y0 : Rat
  y1 : Rat
  tivs : List (Rat × Rat)
deriving Repr

/-- A case-LP certificate: measure data plus hypotheses.  The budget is
`n − cores.length` (loader-enforced in Python, definitional here). -/
structure CCertI where
  n     : Nat
  sNum  : Int
  sDen  : Int
  wd    : Int
  depth : Nat
  atoms : List IAtom
  cores : List CCore
  nofams : List CNoFam
deriving Repr

/-- `cos θ`, `sin θ` as exact rationals of `t = tan(θ/2)` (`cos_sin_t`). -/
@[inline] def ratCosSin (t : Rat) : Rat × Rat :=
  let tt := t * t
  ((1 - tt) / (1 + tt), 2 * t / (1 + tt))

@[inline] def rabs (x : Rat) : Rat := if x < 0 then -x else x

@[inline] def rmin (a b : Rat) : Rat := if a ≤ b then a else b

@[inline] def rmax (a b : Rat) : Rat := if a ≤ b then b else a

/-- Clamp at zero from below (the `Alo` clamp of `core_exempt_frac`). -/
@[inline] def rclamp0 (x : Rat) : Rat := if x < 0 then 0 else x

/-- The `Babs` combinator of `core_exempt_frac`: `0` when the enclosure `[blo, bhi]`
straddles `0`, else the smaller endpoint magnitude. -/
@[inline] def rbabs (blo bhi : Rat) : Rat :=
  if blo ≤ 0 && 0 ≤ bhi then 0 else rmin (rabs blo) (rabs bhi)

/-- Four-corner interval product, `Rat` endpoints (`imul4`). -/
@[inline] def rmul4 (a0 a1 b0 b1 : Rat) : Rat × Rat :=
  let p1 := a0 * b0
  let p2 := a0 * b1
  let p3 := a1 * b0
  let p4 := a1 * b1
  (rmin (rmin p1 p2) (rmin p3 p4), rmax (rmax p1 p2) (rmax p3 p4))

/-- The certified lower bound `g_inf ≤ g(t) = |cos(θ−θ_m)| + |sin(θ−θ_m)|` on the
t-interval (`core_exempt_frac` lines `Alo`/`Babs`): `A = cos(θ−θ_m) ≥ 0` is bounded
below by its monotone corner (clamped at 0), `B = sin(θ_m−θ)` by the min endpoint
magnitude of its enclosure when it does not straddle `0`. -/
def gInf (K : CCore) (t0 t1 : Rat) : Rat :=
  let (c1, s0) := ratCosSin t0       -- cos decreasing, sin increasing in t
  let (c0, s1) := ratCosSin t1
  let (cm, sm) := ratCosSin K.tm
  rclamp0 (c0 * cm + s0 * sm) + rbabs (-s1 * cm + c0 * sm) (-s0 * cm + c1 * sm)

/-- `core_exempt_frac`: `true` iff for EVERY `(t, cx, cy)` in the box the closed unit
square `Q(c, θ(t))` provably meets the core (SAT: projection overlap on all four
edge-normal axes, by outward rational interval arithmetic). -/
def coreExempt (K : CCore) (t0 t1 x0 x1 y0 y1 : Rat) : Bool :=
  let (c1, s0) := ratCosSin t0       -- cos decreasing, sin increasing in t
  let (c0, s1) := ratCosSin t1
  let (cm, sm) := ratCosSin K.tm
  let g := gInf K t0 t1
  let dxlo := x0 - K.kx
  let dxhi := x1 - K.kx
  let dylo := y0 - K.ky
  let dyhi := y1 - K.ky
  -- core axes e1 = (cm, sm), e2 = (−sm, cm): need sup |proj| ≤ a + g/2
  let lime := K.a + g / 2
  let lo1 := dxlo * cm + dylo * sm
  let hi1 := dxhi * cm + dyhi * sm
  rmax (rabs lo1) (rabs hi1) ≤ lime &&
  (let lo2 := -dxhi * sm + dylo * cm
   let hi2 := -dxlo * sm + dyhi * cm
   rmax (rabs lo2) (rabs hi2) ≤ lime &&
   -- Q axes f1 = (C, S), f2 = (−S, C): need sup |proj| ≤ 1/2 + a·g
   (let limf := (1 : Rat) / 2 + K.a * g
    let (a0, a1) := rmul4 c0 c1 dxlo dxhi
    let (b0, b1) := rmul4 s0 s1 dylo dyhi
    rmax (rabs (a0 + b0)) (rabs (a1 + b1)) ≤ limf &&
    (let (e0, e1) := rmul4 (-s1) (-s0) dxlo dxhi
     let (f0, f1) := rmul4 c0 c1 dylo dyhi
     rmax (rabs (e0 + f0)) (rabs (e1 + f1)) ≤ limf)))

/-- `nofam_exempt`: box centre rectangle inside the zone AND `[t0,t1]` inside one of
its closed t-intervals (exact comparisons). -/
def nofamExempt (f : CNoFam) (t0 t1 x0 x1 y0 y1 : Rat) : Bool :=
  f.x0 ≤ x0 && x1 ≤ f.x1 && f.y0 ≤ y0 && y1 ≤ f.y1 &&
  f.tivs.any (fun iv => iv.1 ≤ t0 && t1 ≤ iv.2)

/-- `Verifier.exempt`: NO-families first, then cores (Python order). The integer box
is converted to exact rationals (`t = T/2^K`, `x = X/D`). -/
def exemptB (ctx : Ctx) (cores : List CCore) (nofams : List CNoFam) (b : IBox) : Bool :=
  let t0 := (b.T0 : Rat) / (ctx.TROOT : Rat)
  let t1 := (b.T1 : Rat) / (ctx.TROOT : Rat)
  let x0 := (b.X0 : Rat) / (ctx.D : Rat)
  let x1 := (b.X1 : Rat) / (ctx.D : Rat)
  let y0 := (b.Y0 : Rat) / (ctx.D : Rat)
  let y1 := (b.Y1 : Rat) / (ctx.D : Rat)
  nofams.any (fun f => nofamExempt f t0 t1 x0 x1 y0 y1) ||
  cores.any (fun K => coreExempt K t0 t1 x0 x1 y0 y1)

/-- Discharge a box (fuel = remaining bisections): clip → exempt → covered → split.
Identical to `MeasureI.go` with the exemption test inserted after clipping
(`Verifier.run` order). -/
def goC (ctx : Ctx) (cores : List CCore) (nofams : List CNoFam) :
    Nat → IBox → List IAtom → Int → Bool
  | 0, b, atoms, sure =>
    match clipI ctx b with
    | none => true
    | some b' =>
      if exemptB ctx cores nofams b' then true
      else
        let (Clo, Chi, Slo, Shi, E) := boxTrig ctx b'.T0 b'.T1
        (sift ctx Clo Chi Slo Shi E b' atoms sure []).1
  | fuel + 1, b, atoms, sure =>
    match clipI ctx b with
    | none => true
    | some b' =>
      if exemptB ctx cores nofams b' then true
      else
        let (Clo, Chi, Slo, Shi, E) := boxTrig ctx b'.T0 b'.T1
        let (cov, sure', rest) := sift ctx Clo Chi Slo Shi E b' atoms sure []
        if cov then true
        else
          let p := splitI ctx b'
          goC ctx cores nofams fuel p.1 rest sure' &&
          goC ctx cores nofams fuel p.2 rest sure'

/-- Loader gates on a core: `0 ≤ tm ≤ 1` and `a > 0` (`verify_case.py` "bad core"). -/
def coreOK (K : CCore) : Bool := 0 ≤ K.tm && K.tm ≤ 1 && 0 < K.a

/-- The full check: structural gates (positive denominators, weights ≥ 0, valid
cores, budget arithmetic `Σw < (n − r)·wd`), then every box of the root discharged.
Mirrors `checkMeasureI` with the budget in place of `n`. -/
def checkCaseI (c : CCertI) : Bool :=
  let ctx := mkCtx { n := c.n, sNum := c.sNum, sDen := c.sDen, wd := c.wd,
                     depth := c.depth, atoms := c.atoms }
  0 < c.sDen && 0 < c.wd &&
  c.atoms.all (fun a => 0 < a.pd && 0 ≤ a.w) &&
  c.cores.all coreOK &&
  decide (c.cores.length ≤ c.n) &&
  (c.atoms.foldl (fun acc a => acc + a.w) 0
      < ((c.n : Int) - (c.cores.length : Int)) * c.wd) &&
  goC ctx c.cores c.nofams c.depth (rootBox ctx) c.atoms 0

end PackingCert.CaseI
