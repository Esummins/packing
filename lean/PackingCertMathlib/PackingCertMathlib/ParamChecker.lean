import PackingCertMathlib.CaseChecker

/-!
# Parametric (window) kill-certificate checker (`checkParamI`) — A75, depgraph node V.PARAM

Core Lean 4 only, no Mathlib.  The decision core of `verify_param.py`
(`attempts/A56-sparametric/code/verify_param.py`, A56 T2(C); soundness statement P3
of `attempts/A56-sparametric/notes/soundness.md`), the 4-D `(t, cx, cy, s)` branch-and-bound
that certifies a pin-set kill for EVERY side `s` of a window `[s_lo, s_hi]` at once.

The certificate declares, for each side `s`, the atomic measure `μ_s = Σ wᵢ δ_{pᵢ(s)}`
with AFFINE atom positions `pᵢ(s) = (αxᵢ + βxᵢ·s, αyᵢ + βyᵢ·s)` and cores (closed squares
that hypothetical family members contain) with affine centres
`(akxⱼ + bkxⱼ·s, akyⱼ + bkyⱼ·s)`, half-side `aⱼ`, tilt `tmⱼ`.  A PASS certifies

    for every `s ∈ [s_lo, s_hi]` and every closed unit square `Q ⊆ [0,s]²` that meets
    no core `Kⱼ(s)`:   `μ_s(Q) ≥ 1` (scaled: `≥ need/wd`, `need ≥ wd`),

plus the `s`-free budget inequality `Σ wᵢ < n − #cores`.

## What is reused verbatim from the audited fixed-side checkers

* `imul4`, `trig`, `boxTrig`, `clipI`, `insideAll` (`MeasureChecker.lean`, A64 = the
  Python `imul4 / trig_int / box_trig / clip_int / atom_inside_int` predicates, which
  `verify_param.py` IMPORTS unmodified from A53's `verify_case.py`);
* `coreExempt` (`CaseChecker.lean`, A70 = `core_exempt_frac`).

## The new predicates (each = the A53 one with a POINT replaced by an INTERVAL)

* `projIV` / `cellAtom`: `atom_inside_int_iv` — the atom's `x`/`y` are the exact
  rational intervals `[α + β·s_a, α + β·s_b]` (sorted) of the s-cell, brought to a
  common denominator `pd` exactly as `SCell.__init__` does (lcm of the four
  denominators); the `dx`/`dy` enclosures are wider, so the test is at least as strict;
* `coreExemptIV` / `cellCore`: `core_exempt_frac_iv` — `kx, ky` widened to their exact
  s-intervals (`CoreP.at`): `dxlo = x0 − kx1`, `dxhi = x1 − kx0`, etc.  Literally
  `coreExempt` with a centre-`0` core on the box shifted by the centre interval.

## Discharge rules on a 4-D box `B = [T0,T1] × [X0,X1] × [Y0,Y1] × [SA,SB]` (P3)

(V)+(CL) clip with the wall at `s = SB/D` (the largest container of the cell, via
`clipI` with `SD := SB`) → (E) exempt on the clipped box (`exemptP`) → (C) covered
(`siftP`: certified mass of the atoms whose whole s-interval box lies in `Q` for every
`(t, c)` of the box reaches `need`) → split the widest of `t` (× `tscale`), `x`, `y`,
`s` (× `sscale`; never when the s-cell is a point or its midpoint is not an integer:
`sWidth`), ties in the order `x, y, t, s` (Python's stable sort) → a box undischarged at depth
`depth` is a FAIL.

## Faithfulness notes (deviations from the Python driver, all decision-neutral)

* the float shortlist (`float_candidates`) and the float core pre-filter
  (`core_exempt_float_iv`) are modelled by an ORACLE `pick : PBox → List PAtom → Int →
  PAtom → Bool` (any function of the box, the not-yet-certified atoms and the certified
  mass — enough to encode the Python shortlist together with its "float reject" early
  return); the soundness theorem (`ParamBridge.lean`) holds for EVERY oracle, and the
  Python run is one instance.  Omitting the float core pre-filter can only grant MORE
  exemptions than the Python run (the exact test decides).  `pick := fun _ _ _ _ => true`
  is the `--no-float-prepass` run;
* Python's `known` index tuple (atoms certified for an ancestor box, inherited by the
  children — including across s-splits) is carried as the complement: the list `rest` of
  atoms NOT yet certified, in the same heavy-first order; certified mass is `sure`;
* `tscale`/`sscale` are modelled as integers (Python accepts rationals; the campaign used
  the defaults 2 and 8);
* the root grid (`--split k`: `4^k` boxes, depth counter starting at `2k`) IS
  reproduced (`rootGridP`, `fuel = depth − 2k`), including the divisibility assertion
  (`gridOK`);
* the grid denominator `S_DEN = 250000` is a certificate field `sDen` here (the
  generator emits 250000); `s_lo = saNum/sDen`, `s_hi = sbNum/sDen` (Python asserts that
  the endpoints lie on the grid);
* the census-window canary C3 (`[s_lo, s_hi] ⊆ [191/50, 969271/250000]`) is a loader
  gate in Python (`ValueError` → exit 2) and a Bool gate here (`windowOK`); it is NOT
  used by the soundness proof (which is about the declared cores), only recorded;
* `nofams` are unsupported by `verify_param.py` (loader rejects them) and absent here.

The per-box decision sequence is the Python `PVerifier.run` order.  Soundness
(`checkParamI` PASS ⟹ for every `s` in the window, no strict family of `n` closed unit
squares at side `s` has designated owners containing the cores `Kⱼ(s)`) is proved in
`ParamBridge.lean`.
-/

namespace PackingCert.ParamI

open PackingCert.MeasureI PackingCert.CaseI

/-- An atom with an affine position `(αx + βx·s, αy + βy·s)` and integer weight
numerator `w` (over the certificate's `wd`). -/
structure PAtom where
  alphaX : Rat
  betaX  : Rat
  alphaY : Rat
  betaY  : Rat
  w      : Int
deriving Repr

/-- A core with an affine centre `(akx + bkx·s, aky + bky·s)`, tilt `tm`, half-side `a`. -/
structure PCore where
  akx : Rat
  bkx : Rat
  aky : Rat
  bky : Rat
  tm  : Rat
  a   : Rat
deriving Repr

/-- A parametric kill certificate.  `s_lo = saNum/sDen`, `s_hi = sbNum/sDen` (`sDen` is
the unified grid denominator, 250000 in the campaign); `need = ⌈(1 + margin)·wd⌉`
(`PVerifier.NEED`; `wd ≤ need` is a gate). -/
structure PCertI where
  n     : Nat
  sDen  : Int
  saNum : Int
  sbNum : Int
  wd    : Int
  need  : Int
  depth : Nat
  atoms : List PAtom
  cores : List PCore
deriving Repr

/-- A 4-D box: the 3-D box of `MeasureChecker.lean` plus the s-cell `[SA, SB]/D`. -/
structure PBox where
  T0 : Int
  T1 : Int
  X0 : Int
  X1 : Int
  Y0 : Int
  Y1 : Int
  SA : Int
  SB : Int
deriving Repr

def PBox.toIBox (p : PBox) : IBox := ⟨p.T0, p.T1, p.X0, p.X1, p.Y0, p.Y1⟩

def PBox.withIBox (p : PBox) (b : IBox) : PBox :=
  ⟨b.T0, b.T1, b.X0, b.X1, b.Y0, b.Y1, p.SA, p.SB⟩

/-- An atom widened to its s-cell: `x ∈ [pxlo, pxhi]/pd`, `y ∈ [pylo, pyhi]/pd`
(`SCell.PXlo/PXhi/PYlo/PYhi/PD`). -/
structure IAtomIV where
  pxlo : Int
  pxhi : Int
  pylo : Int
  pyhi : Int
  pd   : Int
  w    : Int
deriving Repr

/-- Sorted pair (`if x0 > x1: swap`). -/
@[inline] def rminmax (u v : Rat) : Rat × Rat := if u ≤ v then (u, v) else (v, u)

/-- Numerator of `r` over the common denominator `pd` (a multiple of `r.den`):
`r.num * (pd // r.den)`. -/
@[inline] def numOver (r : Rat) (pd : Nat) : Int := r.num * ((pd : Int) / (r.den : Int))

/-- The exact `x`-interval of an atom over the s-cell (sorted). -/
def cellX (a : PAtom) (sa sb : Rat) : Rat × Rat :=
  rminmax (a.alphaX + a.betaX * sa) (a.alphaX + a.betaX * sb)

/-- The exact `y`-interval of an atom over the s-cell (sorted). -/
def cellY (a : PAtom) (sa sb : Rat) : Rat × Rat :=
  rminmax (a.alphaY + a.betaY * sa) (a.alphaY + a.betaY * sb)

/-- The common denominator of the four interval endpoints (`SCell`'s lcm loop). -/
def cellPd (a : PAtom) (sa sb : Rat) : Nat :=
  Nat.lcm (Nat.lcm (cellX a sa sb).1.den (cellX a sa sb).2.den)
    (Nat.lcm (cellY a sa sb).1.den (cellY a sa sb).2.den)

/-- `SCell.__init__` for one atom: exact s-interval endpoints, lcm denominator. -/
def cellAtom (a : PAtom) (sa sb : Rat) : IAtomIV :=
  let (x0, x1) := cellX a sa sb
  let (y0, y1) := cellY a sa sb
  let pd := cellPd a sa sb
  ⟨numOver x0 pd, numOver x1 pd, numOver y0 pd, numOver y1 pd, (pd : Int), a.w⟩

/-- `atom_inside_int_iv`'s enclosures: `projI` with the atom point replaced by its
interval box (`dxlo = PXlo·D − X1·PD`, `dxhi = PXhi·D − X0·PD`, …). -/
@[inline] def projIV (ctx : Ctx) (Clo Chi Slo Shi E : Int) (b : IBox) (a : IAtomIV) :
    Int × Int × Int × Int × Int :=
  let dxlo := a.pxlo * ctx.D - b.X1 * a.pd
  let dxhi := a.pxhi * ctx.D - b.X0 * a.pd
  let dylo := a.pylo * ctx.D - b.Y1 * a.pd
  let dyhi := a.pyhi * ctx.D - b.Y0 * a.pd
  let lim := E * a.pd * ctx.D
  let (a0, a1) := imul4 Clo Chi dxlo dxhi
  let (b0, b1) := imul4 Slo Shi dylo dyhi
  let (c0, c1) := imul4 (-Shi) (-Slo) dxlo dxhi
  let (d0, d1) := imul4 Clo Chi dylo dyhi
  (2 * (a0 + b0), 2 * (a1 + b1), 2 * (c0 + d0), 2 * (c1 + d1), lim)

/-- The exact `kx`-interval of a core over the s-cell (sorted). -/
def cellKx (K : PCore) (sa sb : Rat) : Rat × Rat :=
  rminmax (K.akx + K.bkx * sa) (K.akx + K.bkx * sb)

/-- The exact `ky`-interval of a core over the s-cell (sorted). -/
def cellKy (K : PCore) (sa sb : Rat) : Rat × Rat :=
  rminmax (K.aky + K.bky * sa) (K.aky + K.bky * sb)

/-- `CoreP.at`: the exact centre intervals of a core over the s-cell. -/
def cellCore (K : PCore) (sa sb : Rat) : Rat × Rat × Rat × Rat :=
  let (kx0, kx1) := cellKx K sa sb
  let (ky0, ky1) := cellKy K sa sb
  (kx0, kx1, ky0, ky1)

/-- `core_exempt_frac_iv`: `core_exempt_frac` with `dx ∈ [x0 − kx1, x1 − kx0]`,
`dy ∈ [y0 − ky1, y1 − ky0]` — i.e. `coreExempt` for the centre-`0` core on the shifted
box. -/
def coreExemptIV (K : PCore) (kx0 kx1 ky0 ky1 t0 t1 x0 x1 y0 y1 : Rat) : Bool :=
  coreExempt ⟨0, 0, K.tm, K.a⟩ t0 t1 (x0 - kx1) (x1 - kx0) (y0 - ky1) (y1 - ky0)

/-- `PVerifier.exempt`: some core is provably met for every `(t, c, s)` of the box. -/
def exemptP (ctx : Ctx) (cores : List PCore) (sa sb : Rat) (b : IBox) : Bool :=
  let t0 := (b.T0 : Rat) / (ctx.TROOT : Rat)
  let t1 := (b.T1 : Rat) / (ctx.TROOT : Rat)
  let x0 := (b.X0 : Rat) / (ctx.D : Rat)
  let x1 := (b.X1 : Rat) / (ctx.D : Rat)
  let y0 := (b.Y0 : Rat) / (ctx.D : Rat)
  let y1 := (b.Y1 : Rat) / (ctx.D : Rat)
  cores.any (fun K =>
    let (kx0, kx1, ky0, ky1) := cellCore K sa sb
    coreExemptIV K kx0 kx1 ky0 ky1 t0 t1 x0 x1 y0 y1)

/-- `PVerifier.covered`: walk the not-yet-certified atoms (heavy first); an atom the
oracle picks whose whole s-interval box is inside `Q` for the whole box is certified
(its weight added to `sure`); the others are kept.  Stops once `sure ≥ NEED`.
Returns `(covered, sure', rest')`. -/
def siftP (ctx : Ctx) (Clo Chi Slo Shi E : Int) (b : IBox) (sa sb : Rat)
    (pick : PAtom → Bool) :
    List PAtom → Int → List PAtom → Bool × Int × List PAtom
  | [], sure, acc => (sure ≥ ctx.NEED, sure, acc)
  | a :: as, sure, acc =>
    if sure ≥ ctx.NEED then (true, sure, acc)
    else
      let (u0, u1, v0, v1, lim) := projIV ctx Clo Chi Slo Shi E b (cellAtom a sa sb)
      if pick a && insideAll u0 u1 v0 v1 lim then
        siftP ctx Clo Chi Slo Shi E b sa sb pick as (sure + a.w) acc
      else siftP ctx Clo Chi Slo Shi E b sa sb pick as sure (a :: acc)

/-- The 4-axis split rule of `PVerifier.run`: widths `wt = (T1−T0)·tscale·D`,
`wx = (X1−X0)·2^K`, `wy = (Y1−Y0)·2^K`, `ws = (SB−SA)·sscale·2^K` (`−1` when the s-cell
is a point or `SA + SB` is odd); the widest wins, ties in the order `x, y, t, s`;
floor midpoints. -/
def sWidth (ctx : Ctx) (ss : Int) (p : PBox) : Int :=
  if p.SB - p.SA == 0 || (p.SA + p.SB) % 2 != 0 then -1
  else (p.SB - p.SA) * ss * ctx.TROOT

def splitP (ctx : Ctx) (ts ss : Int) (p : PBox) : PBox × PBox :=
  let wt := (p.T1 - p.T0) * ts * ctx.D
  let wx := (p.X1 - p.X0) * ctx.TROOT
  let wy := (p.Y1 - p.Y0) * ctx.TROOT
  let ws := sWidth ctx ss p
  if wx ≥ wy && wx ≥ wt && wx ≥ ws then
    let m := (p.X0 + p.X1) / 2
    ({ p with X1 := m }, { p with X0 := m })
  else if wy ≥ wt && wy ≥ ws then
    let m := (p.Y0 + p.Y1) / 2
    ({ p with Y1 := m }, { p with Y0 := m })
  else if wt ≥ ws then
    let m := (p.T0 + p.T1) / 2
    ({ p with T1 := m }, { p with T0 := m })
  else
    let m := (p.SA + p.SB) / 2
    ({ p with SA := m }, { p with SB := m })

/-- The context with the wall at the cell's upper side (`clip_int(SB, …)`). -/
@[inline] def ctxAt (ctx : Ctx) (SB : Int) : Ctx := { ctx with SD := SB }

/-- Discharge a 4-D box (fuel = remaining bisections): clip (wall at `SB`) → exempt →
covered → split / fail.  `PVerifier.run`, one stack frame. -/
def goP (ctx : Ctx) (ts ss : Int) (cores : List PCore)
    (pick : PBox → List PAtom → Int → PAtom → Bool) :
    Nat → PBox → List PAtom → Int → Bool
  | 0, p, rest, sure =>
    match clipI (ctxAt ctx p.SB) p.toIBox with
    | none => true
    | some b' =>
      let sa := (p.SA : Rat) / (ctx.D : Rat)
      let sb := (p.SB : Rat) / (ctx.D : Rat)
      if exemptP ctx cores sa sb b' then true
      else
        let (Clo, Chi, Slo, Shi, E) := boxTrig ctx b'.T0 b'.T1
        (siftP ctx Clo Chi Slo Shi E b' sa sb (pick (p.withIBox b') rest sure) rest sure []).1
  | fuel + 1, p, rest, sure =>
    match clipI (ctxAt ctx p.SB) p.toIBox with
    | none => true
    | some b' =>
      let sa := (p.SA : Rat) / (ctx.D : Rat)
      let sb := (p.SB : Rat) / (ctx.D : Rat)
      if exemptP ctx cores sa sb b' then true
      else
        let (Clo, Chi, Slo, Shi, E) := boxTrig ctx b'.T0 b'.T1
        let (cov, sure', rest') :=
          siftP ctx Clo Chi Slo Shi E b' sa sb (pick (p.withIBox b') rest sure) rest sure []
        if cov then true
        else
          let q := splitP ctx ts ss (p.withIBox b')
          goP ctx ts ss cores pick fuel q.1 rest' sure' &&
          goP ctx ts ss cores pick fuel q.2 rest' sure'

/-- `PVerifier.root_boxes`: the root `[0, 2^K] × [D/2, SB − D/2]² × [SA, SB]` split into
`4^k` boxes in `(cx, cy)`, `step = (hi − lo) / 2^k`. -/
def rootGridP (ctx : Ctx) (SA SB : Int) (k : Nat) : List PBox :=
  let lo := ctx.D / 2
  let hi := SB - lo
  let m : Nat := 2 ^ k
  let step := (hi - lo) / (m : Int)
  (List.range m).flatMap fun (i : Nat) => (List.range m).map fun (j : Nat) =>
    ⟨0, ctx.TROOT, lo + step * (i : Int), lo + step * ((i : Int) + 1),
      lo + step * (j : Int), lo + step * ((j : Int) + 1), SA, SB⟩

/-- The root-grid divisibility assertion (`assert step << k == span`). -/
def gridOK (ctx : Ctx) (SB : Int) (k : Nat) : Bool :=
  let lo := ctx.D / 2
  let hi := SB - lo
  let m : Nat := 2 ^ k
  ((hi - lo) / (m : Int)) * (m : Int) == hi - lo

/-- Scale constants (`PVerifier.__init__`): `K = depth + 1`, `D = sDen·2^(depth+2)`;
`SD` is the wall at `s_hi` (root clip), `NEED = need`. -/
def mkCtxP (c : PCertI) : Ctx :=
  let K := c.depth + 1
  { K := K
    TROOT := (2 : Int) ^ K
    P4 := (4 : Int) ^ K
    D := c.sDen * (2 : Int) ^ (c.depth + 2)
    SD := c.sbNum * (2 : Int) ^ (c.depth + 2)
    NEED := c.need }

def saRoot (c : PCertI) : Int := c.saNum * (2 : Int) ^ (c.depth + 2)
def sbRoot (c : PCertI) : Int := c.sbNum * (2 : Int) ^ (c.depth + 2)

/-- Loader gates on a core (`load_param`: `0 ≤ tm ≤ 1`, `a > 0`). -/
def coreOKP (K : PCore) : Bool := 0 ≤ K.tm && K.tm ≤ 1 && 0 < K.a

/-- Canary C3: the window lies inside the census window `[191/50, 969271/250000]`. -/
def windowOK (c : PCertI) : Bool :=
  (191 : Rat) / 50 ≤ (c.saNum : Rat) / (c.sDen : Rat) &&
  (c.sbNum : Rat) / (c.sDen : Rat) ≤ (969271 : Rat) / 250000

/-- The full check: structural gates (positive denominators, `wd ≤ need`, weights ≥ 0,
valid cores, budget arithmetic `Σw < (n − r)·wd`, window order + canary, root-grid
divisibility), then every root box discharged with `fuel = depth − 2k`. -/
def checkParamI (c : PCertI) (ts ss : Int) (k : Nat)
    (pick : PBox → List PAtom → Int → PAtom → Bool) : Bool :=
  let ctx := mkCtxP c
  0 < c.sDen && 0 < c.wd && c.wd ≤ c.need &&
  c.atoms.all (fun a => 0 ≤ a.w) &&
  c.cores.all coreOKP &&
  decide (c.cores.length ≤ c.n) &&
  (c.atoms.foldl (fun acc a => acc + a.w) 0
      < ((c.n : Int) - (c.cores.length : Int)) * c.wd) &&
  c.saNum ≤ c.sbNum &&
  windowOK c &&
  gridOK ctx (sbRoot c) k &&
  (rootGridP ctx (saRoot c) (sbRoot c) k).all
    (fun p => goP ctx ts ss c.cores pick (c.depth - 2 * k) p c.atoms 0)

/-- The `--no-float-prepass` oracle: test every atom exactly. -/
def pickAll : PBox → List PAtom → Int → PAtom → Bool := fun _ _ _ _ => true

end PackingCert.ParamI
