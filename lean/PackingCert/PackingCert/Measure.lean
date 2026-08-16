/-!
# Lower-bound "measure certificate" checker (prototype, style A)

A *measure certificate* for the claim "no `n` pairwise-disjoint closed unit
squares fit inside `[0, side]²`" (hence `s(n) > side`) is a finite atomic
measure `μ = Σ wᵢ δ_{pᵢ}` with rational atoms `pᵢ` and rational weights
`wᵢ ≥ 0`, total mass `Σ wᵢ < n`, such that **every** closed unit square
`Q ⊂ [0, side]²` satisfies `μ(Q) ≥ 1`.  (If `n` disjoint squares fitted, the
total mass would be ≥ n.)

The universal statement over all squares is discharged by interval branch and
bound over the parameter space

  `(t, cx, cy) ∈ [0,1] × [0,side] × [0,side]`,  `t = tan(θ/2)`, `θ ∈ [0, π/2]`

(θ ∈ [0, π/2] covers all unit squares by the 4-fold symmetry of the square),
with `cos θ = (1−t²)/(1+t²)` (decreasing on [0,1]) and `sin θ = 2t/(1+t²)`
(increasing on [0,1]), so a `t`-interval gives *exact rational* enclosures of
cos and sin.  A box `[t0,t1]×[x0,x1]×[y0,y1]` is discharged if

* after clipping the centre ranges to the admissible region
  `w/2 ≤ c ≤ side − w/2` (`w = cos+sin` = bounding-box width, using the lower
  bound `wLo` of `w` over the box), the box is empty (no square with parameters
  in the box lies inside the container), or
* the total weight of atoms that lie inside `Q(t,cx,cy)` for **all** parameters
  of the (clipped) box — decided by rational interval arithmetic on
  `u = cos·(px−cx) + sin·(py−cy)`, `v = −sin·(px−cx) + cos·(py−cy)`,
  `|u| ≤ 1/2 ∧ |v| ≤ 1/2` — is ≥ 1;

otherwise it is bisected along its widest dimension, down to a depth `fuel`.

Certificate = (n, side, atoms, fuel): style (A), the Lean function does the
recursion itself.  Style (B) (explicit box list with witnesses) is not
implemented; see attempts/A06-lean-setup/notes.md.

Everything is over `Rat` (core Lean, no Mathlib), Bool-valued, so that
`native_decide` can evaluate it.  Sound in the direction we need: whenever
`checkMeasure c = true`, every admissible square has mass ≥ 1 (bridge lemma not
formalised — same status as the upper-bound checker).
-/

namespace PackingCert.Measure

structure Atom where
  px : Rat
  py : Rat
  w  : Rat
deriving Repr

/-- A measure certificate. -/
structure MCert where
  n     : Nat          -- claim: no `n` disjoint unit squares in `[0,side]²`
  side  : Rat
  atoms : List Atom
  fuel  : Nat          -- max bisection depth
deriving Repr

/-- Parameter box: `t ∈ [t0,t1]`, centre `(cx,cy) ∈ [x0,x1]×[y0,y1]`. -/
structure Box where
  t0 : Rat
  t1 : Rat
  x0 : Rat
  x1 : Rat
  y0 : Rat
  y1 : Rat
deriving Repr

/-- Closed rational interval `[lo, hi]`. -/
abbrev Ivl := Rat × Rat

def cosR (t : Rat) : Rat := (1 - t * t) / (1 + t * t)
def sinR (t : Rat) : Rat := (2 * t) / (1 + t * t)

def imul (a b : Ivl) : Ivl :=
  let p1 := a.1 * b.1
  let p2 := a.1 * b.2
  let p3 := a.2 * b.1
  let p4 := a.2 * b.2
  (min (min p1 p2) (min p3 p4), max (max p1 p2) (max p3 p4))

def iadd (a b : Ivl) : Ivl := (a.1 + b.1, a.2 + b.2)
def isub (a b : Ivl) : Ivl := (a.1 - b.2, a.2 - b.1)

/-- Enclosures of `cos θ`, `sin θ` for `t ∈ [t0,t1] ⊆ [0,1]`. -/
def cosIvl (b : Box) : Ivl := (cosR b.t1, cosR b.t0)
def sinIvl (b : Box) : Ivl := (sinR b.t0, sinR b.t1)

/-- Atom `a` lies in the closed unit square `Q(t,cx,cy)` for every parameter in the box. -/
def atomInside (c s : Ivl) (b : Box) (a : Atom) : Bool :=
  let dx : Ivl := (a.px - b.x1, a.px - b.x0)
  let dy : Ivl := (a.py - b.y1, a.py - b.y0)
  let u := iadd (imul c dx) (imul s dy)
  let v := isub (imul c dy) (imul s dx)
  let h : Rat := 1 / 2
  (-h ≤ u.1) && (u.2 ≤ h) && (-h ≤ v.1) && (v.2 ≤ h)

/-- Total weight of atoms provably inside `Q` for all parameters of the box. -/
def massInside (c s : Ivl) (b : Box) (atoms : List Atom) : Rat :=
  atoms.foldl (fun acc a => if atomInside c s b a then acc + a.w else acc) 0

/-- Clip the centre ranges to the admissible region `wLo/2 ≤ c ≤ side − wLo/2`.
Returns `none` if no square with parameters in `b` fits in the container. -/
def clipBox (side : Rat) (b : Box) : Option Box :=
  let c := cosIvl b
  let s := sinIvl b
  let wLo := c.1 + s.1
  let lo := wLo / 2
  let hi := side - wLo / 2
  let x0 := max b.x0 lo
  let x1 := min b.x1 hi
  let y0 := max b.y0 lo
  let y1 := min b.y1 hi
  if x0 ≤ x1 && y0 ≤ y1 then
    some { b with x0 := x0, x1 := x1, y0 := y0, y1 := y1 }
  else
    none

/-- Bisect along the widest dimension. -/
def split (b : Box) : Box × Box :=
  let wt := b.t1 - b.t0
  let wx := b.x1 - b.x0
  let wy := b.y1 - b.y0
  if wt ≥ wx && wt ≥ wy then
    let m := (b.t0 + b.t1) / 2
    ({ b with t1 := m }, { b with t0 := m })
  else if wx ≥ wy then
    let m := (b.x0 + b.x1) / 2
    ({ b with x1 := m }, { b with x0 := m })
  else
    let m := (b.y0 + b.y1) / 2
    ({ b with y1 := m }, { b with y0 := m })

/-- Discharge a (clipped) box: covered ⇒ true; else bisect if fuel remains. -/
def go (side : Rat) (atoms : List Atom) : Nat → Box → Bool
  | 0, b =>
    match clipBox side b with
    | none => true
    | some b' => massInside (cosIvl b') (sinIvl b') b' atoms ≥ 1
  | fuel + 1, b =>
    match clipBox side b with
    | none => true
    | some b' =>
      if massInside (cosIvl b') (sinIvl b') b' atoms ≥ 1 then true
      else
        let p := split b'
        go side atoms fuel p.1 && go side atoms fuel p.2

/-- The full check. -/
def checkMeasure (c : MCert) : Bool :=
  c.atoms.all (fun a => 0 ≤ a.w) &&
  (c.atoms.foldl (fun acc a => acc + a.w) 0 < (c.n : Rat)) &&
  go c.side c.atoms c.fuel ⟨0, 1, 0, c.side, 0, c.side⟩

/-! ## Instrumented variant: count boxes visited (for scaling experiments). -/

def goCount (side : Rat) (atoms : List Atom) : Nat → Box → Bool × Nat
  | 0, b =>
    match clipBox side b with
    | none => (true, 1)
    | some b' => (massInside (cosIvl b') (sinIvl b') b' atoms ≥ 1, 1)
  | fuel + 1, b =>
    match clipBox side b with
    | none => (true, 1)
    | some b' =>
      if massInside (cosIvl b') (sinIvl b') b' atoms ≥ 1 then (true, 1)
      else
        let p := split b'
        let r1 := goCount side atoms fuel p.1
        let r2 := goCount side atoms fuel p.2
        (r1.1 && r2.1, r1.2 + r2.2 + 1)

def checkMeasureCount (c : MCert) : Bool × Nat :=
  let ok0 := c.atoms.all (fun a => 0 ≤ a.w) &&
    (c.atoms.foldl (fun acc a => acc + a.w) 0 < (c.n : Rat))
  let r := goCount c.side c.atoms c.fuel ⟨0, 1, 0, c.side, 0, c.side⟩
  (ok0 && r.1, r.2)

end PackingCert.Measure
