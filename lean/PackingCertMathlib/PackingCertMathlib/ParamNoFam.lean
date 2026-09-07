import Mathlib.Data.Real.Basic
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Inverse
import Mathlib.Tactic
import PackingCertMathlib.Parametrize
import PackingCertMathlib.CaseChecker
import PackingCertMathlib.CaseHyp
import PackingCertMathlib.ParamChecker

/-!
# NO-families in the parametric (window) checker — A117 T1, depgraph node V.PARAM

The Lean shape of the one clause `verify_param_v2.py` adds to the frozen 4-D verifier
(`attempts/A96-a57-parametric/code/verify_param_v2.py`, rule (N)), stated and proved
PARALLEL to the existing core-exemption clause `CaseHyp.nofamExempt_sound` /
`ParamChecker.coreExemptIV`:

* `PNoFam` — a NO-family whose zone edges are AFFINE in the side `s`
  (`Z(s) = [ax0 + bx0·s, ax1 + bx1·s] × [ay0 + by0·s, ay1 + by1·s]`, plus a finite list
  of closed `t`-intervals).  Every certificate A111/A112 emits has `b* = 0`: the branch
  box is the node's own `s`-independent support box, and the YES/NO split
  "some square has its pose in `F`, or none does" is a tautology at EVERY side for the
  SAME `F`.  The affine form is carried anyway, because it costs nothing and covers the
  wall-anchored case `x1(s) = s − 1/2`.
* `cellNoFam` — the WORST-CASE zone on an s-cell `[sa, sb]`: the INTERSECTION of `Z(s)`
  over the cell, i.e. `[max(x0(sa), x0(sb)), min(x1(sa), x1(sb))] × …`.  Each edge is
  affine, so its extremes on the cell are at the endpoints.  This is `SCell.nofams_iv`.
* `nofamExemptIV` — `CaseI.nofamExempt` on the shrunken zone.  It is LITERALLY the frozen
  fixed-side predicate applied to a smaller rectangle: no new geometry enters the TCB.
* `nofamExemptIV_sound` — the parallel of `nofamExempt_sound`: a passing test proves that
  for EVERY side `s` in the s-cell and EVERY pose in the box, the placement lies in the
  NO-family zone at that side.  Direction: the shrunken zone exempts LESS than the true
  zone at any single side, never more.

`exemptPN` is `PVerifier.exempt` of v2: the NO-family loop, then the core loop, in the
Python order.  `exemptPN_eq_exemptP_of_nil` is the equivalence with v1 measured on 30
certificates in `attempts/A117-verifier-v2/results/equivalence.json`.

## Lemma TC (tilt coherence) — A117 T2(b), `known_results.md` 26c

`tcWidth D = |cos D| + |sin D|` is the support half-width of a unit square in the
direction of an edge normal at relative tilt `D`.  `tc_centre_dist` states Lemma TC:
two interior-disjoint unit squares at tilt difference `D` have centres at least
`(1 + cos D + sin D)/2` apart.  `tc_leaf` is the leaf that consumes it, in the shape of
`Zones.core_meet_same_square` with the width function in place of the core.  Both carry
a `[C]` obligation: the statement is frozen here, the proof is not yet written (the
exact check and its 10⁴-samples-per-fire control are
`attempts/A117-verifier-v2/code/tcleaf.py`).
-/

namespace PackingCert
namespace S11

open Set MeasureI CaseI ParamI

/-! ## The NO-family with an s-affine zone -/

/-- A NO-family of the PARAMETRIC checker: zone edges affine in `s`, `t`-intervals
`s`-free.  With every `b* = 0` this is `CaseI.CNoFam`. -/
structure PNoFam where
  ax0 : Rat
  bx0 : Rat
  ax1 : Rat
  bx1 : Rat
  ay0 : Rat
  by0 : Rat
  ay1 : Rat
  by1 : Rat
  tivs : List (Rat × Rat)
deriving Repr

/-- `SCell.nofams_iv`: the worst-case (smallest) zone on the s-cell `[sa, sb]` — the
intersection of `Z(s)` over the cell.  Each edge is affine, so its extremes are at the
endpoints. -/
def cellNoFam (f : PNoFam) (sa sb : Rat) : Rat × Rat × Rat × Rat :=
  (rmax (f.ax0 + f.bx0 * sa) (f.ax0 + f.bx0 * sb),
   rmin (f.ax1 + f.bx1 * sa) (f.ax1 + f.bx1 * sb),
   rmax (f.ay0 + f.by0 * sa) (f.ay0 + f.by0 * sb),
   rmin (f.ay1 + f.by1 * sa) (f.ay1 + f.by1 * sb))

/-- `nofam_exempt_frac_iv`: the frozen fixed-side predicate `CaseI.nofamExempt` on the
shrunken zone. -/
def nofamExemptIV (f : PNoFam) (sa sb t0 t1 x0 x1 y0 y1 : Rat) : Bool :=
  let (zx0, zx1, zy0, zy1) := cellNoFam f sa sb
  nofamExempt ⟨zx0, zx1, zy0, zy1, f.tivs⟩ t0 t1 x0 x1 y0 y1

/-- `PVerifier.exempt` of v2: NO-families first, then cores (the Python order, which is
also `CaseI.exemptB`'s). -/
def exemptPN (ctx : Ctx) (cores : List PCore) (nofams : List PNoFam) (sa sb : Rat)
    (b : IBox) : Bool :=
  let t0 := (b.T0 : Rat) / (ctx.TROOT : Rat)
  let t1 := (b.T1 : Rat) / (ctx.TROOT : Rat)
  let x0 := (b.X0 : Rat) / (ctx.D : Rat)
  let x1 := (b.X1 : Rat) / (ctx.D : Rat)
  let y0 := (b.Y0 : Rat) / (ctx.D : Rat)
  let y1 := (b.Y1 : Rat) / (ctx.D : Rat)
  nofams.any (fun f => nofamExemptIV f sa sb t0 t1 x0 x1 y0 y1) ||
  exemptP ctx cores sa sb b

/-- **v2 = v1 when there are no NO-families.**  The Lean form of the A117 T1
equivalence claim: with `nofams = []` the v2 dispatcher IS the frozen v1 dispatcher, so
no certificate emitted before A117 can change verdict. -/
theorem exemptPN_nil (ctx : Ctx) (cores : List PCore) (sa sb : Rat) (b : IBox) :
    exemptPN ctx cores [] sa sb b = exemptP ctx cores sa sb b := by
  simp [exemptPN]

/-- The real meaning of "the pose lies in the NO-family at side `s`". -/
def InZoneP (f : PNoFam) (s : ℝ) (q : PSq) : Prop :=
  (f.ax0 : ℝ) + (f.bx0 : ℝ) * s ≤ q.cx ∧ q.cx ≤ (f.ax1 : ℝ) + (f.bx1 : ℝ) * s ∧
  (f.ay0 : ℝ) + (f.by0 : ℝ) * s ≤ q.cy ∧ q.cy ≤ (f.ay1 : ℝ) + (f.by1 : ℝ) * s ∧
  ∃ iv ∈ f.tivs, (iv.1 : ℝ) ≤ q.t ∧ q.t ≤ (iv.2 : ℝ)

/-! ### The one new inequality: an affine function on a cell is between its endpoints -/

theorem affine_le_max {α β sa sb s : ℝ} (h1 : sa ≤ s) (h2 : s ≤ sb) :
    α + β * s ≤ max (α + β * sa) (α + β * sb) := by
  rcases le_total (0 : ℝ) β with hb | hb
  · exact le_max_of_le_right (by nlinarith)
  · exact le_max_of_le_left (by nlinarith)

theorem min_le_affine {α β sa sb s : ℝ} (h1 : sa ≤ s) (h2 : s ≤ sb) :
    min (α + β * sa) (α + β * sb) ≤ α + β * s := by
  rcases le_total (0 : ℝ) β with hb | hb
  · exact le_trans (min_le_left _ _) (by nlinarith)
  · exact le_trans (min_le_right _ _) (by nlinarith)

/-- **The NO-family exemption clause of the parametric checker is sound.**  Exactly
`CaseHyp.nofamExempt_sound` with the zone taken at its s-cell worst case: a passing
`nofamExemptIV` proves that for EVERY side `s` in the cell, EVERY placement of the box
has its `(centre, t)` in the family's zone at that side. -/
theorem nofamExemptIV_sound {f : PNoFam} {sa sb : ℚ} {s : ℝ}
    (hsa : (sa : ℝ) ≤ s) (hsb : s ≤ (sb : ℝ))
    {t0 t1 x0 x1 y0 y1 : ℚ} {q : PSq}
    (hqt0 : (t0 : ℝ) ≤ q.t) (hqt1 : q.t ≤ (t1 : ℝ))
    (hx0 : (x0 : ℝ) ≤ q.cx) (hx1 : q.cx ≤ (x1 : ℝ))
    (hy0 : (y0 : ℝ) ≤ q.cy) (hy1 : q.cy ≤ (y1 : ℝ))
    (h : nofamExemptIV f sa sb t0 t1 x0 x1 y0 y1 = true) : InZoneP f s q := by
  simp only [nofamExemptIV, cellNoFam, nofamExempt, Bool.and_eq_true, decide_eq_true_eq,
    List.any_eq_true] at h
  obtain ⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, iv, hiv, h5⟩ := h
  replace h1 := of_decide_eq_true h1
  replace h2 := of_decide_eq_true h2
  replace h3 := of_decide_eq_true h3
  replace h4 := of_decide_eq_true h4
  refine ⟨?_, ?_, ?_, ?_, iv, hiv, ?_, ?_⟩
  · have hm : (f.ax0 : ℝ) + (f.bx0 : ℝ) * s
        ≤ max ((f.ax0 : ℝ) + (f.bx0 : ℝ) * (sa : ℝ))
              ((f.ax0 : ℝ) + (f.bx0 : ℝ) * (sb : ℝ)) := affine_le_max hsa hsb
    have hc : ((rmax (f.ax0 + f.bx0 * sa) (f.ax0 + f.bx0 * sb) : ℚ) : ℝ)
        = max ((f.ax0 : ℝ) + (f.bx0 : ℝ) * (sa : ℝ))
              ((f.ax0 : ℝ) + (f.bx0 : ℝ) * (sb : ℝ)) := by
      rw [rmax_cast]; push_cast; ring_nf
    have : max ((f.ax0 : ℝ) + (f.bx0 : ℝ) * (sa : ℝ))
               ((f.ax0 : ℝ) + (f.bx0 : ℝ) * (sb : ℝ)) ≤ (x0 : ℝ) := by
      rw [← hc]; exact_mod_cast h1
    linarith
  · have hm : (f.ax1 : ℝ) + (f.bx1 : ℝ) * s
        ≥ min ((f.ax1 : ℝ) + (f.bx1 : ℝ) * (sa : ℝ))
              ((f.ax1 : ℝ) + (f.bx1 : ℝ) * (sb : ℝ)) := min_le_affine hsa hsb
    have hc : ((rmin (f.ax1 + f.bx1 * sa) (f.ax1 + f.bx1 * sb) : ℚ) : ℝ)
        = min ((f.ax1 : ℝ) + (f.bx1 : ℝ) * (sa : ℝ))
              ((f.ax1 : ℝ) + (f.bx1 : ℝ) * (sb : ℝ)) := by
      rw [rmin_cast]; push_cast; ring_nf
    have : (x1 : ℝ) ≤ min ((f.ax1 : ℝ) + (f.bx1 : ℝ) * (sa : ℝ))
                          ((f.ax1 : ℝ) + (f.bx1 : ℝ) * (sb : ℝ)) := by
      rw [← hc]; exact_mod_cast h2
    linarith
  · have hm : (f.ay0 : ℝ) + (f.by0 : ℝ) * s
        ≤ max ((f.ay0 : ℝ) + (f.by0 : ℝ) * (sa : ℝ))
              ((f.ay0 : ℝ) + (f.by0 : ℝ) * (sb : ℝ)) := affine_le_max hsa hsb
    have hc : ((rmax (f.ay0 + f.by0 * sa) (f.ay0 + f.by0 * sb) : ℚ) : ℝ)
        = max ((f.ay0 : ℝ) + (f.by0 : ℝ) * (sa : ℝ))
              ((f.ay0 : ℝ) + (f.by0 : ℝ) * (sb : ℝ)) := by
      rw [rmax_cast]; push_cast; ring_nf
    have : max ((f.ay0 : ℝ) + (f.by0 : ℝ) * (sa : ℝ))
               ((f.ay0 : ℝ) + (f.by0 : ℝ) * (sb : ℝ)) ≤ (y0 : ℝ) := by
      rw [← hc]; exact_mod_cast h3
    linarith
  · have hm : (f.ay1 : ℝ) + (f.by1 : ℝ) * s
        ≥ min ((f.ay1 : ℝ) + (f.by1 : ℝ) * (sa : ℝ))
              ((f.ay1 : ℝ) + (f.by1 : ℝ) * (sb : ℝ)) := min_le_affine hsa hsb
    have hc : ((rmin (f.ay1 + f.by1 * sa) (f.ay1 + f.by1 * sb) : ℚ) : ℝ)
        = min ((f.ay1 : ℝ) + (f.by1 : ℝ) * (sa : ℝ))
              ((f.ay1 : ℝ) + (f.by1 : ℝ) * (sb : ℝ)) := by
      rw [rmin_cast]; push_cast; ring_nf
    have : (y1 : ℝ) ≤ min ((f.ay1 : ℝ) + (f.by1 : ℝ) * (sa : ℝ))
                          ((f.ay1 : ℝ) + (f.by1 : ℝ) * (sb : ℝ)) := by
      rw [← hc]; exact_mod_cast h4
    linarith
  · calc (iv.1 : ℝ) ≤ (t0 : ℝ) := by exact_mod_cast h5.1
      _ ≤ q.t := hqt0
  · calc q.t ≤ (t1 : ℝ) := hqt1
      _ ≤ (iv.2 : ℝ) := by exact_mod_cast h5.2

/-! ## Lemma TC (tilt coherence) — A117 T2(b) -/

/-- `w(D) = |cos D| + |sin D|`: the support half-width of a unit square in the direction
of an edge normal at relative tilt `D` (the sum of the two half-widths of the square's
own axes projected on that normal). -/
noncomputable def tcWidth (D : ℝ) : ℝ := |Real.cos D| + |Real.sin D|

/-- `θ` is the tilt of the parametrised square `q` (`t = tan(θ/2)`, via the checker's own
half-angle functions — no `arctan` needed). -/
def TiltOf (q : PSq) (θ : ℝ) : Prop := Real.cos θ = cosT q.t ∧ Real.sin θ = sinT q.t

/-- `D` is the REDUCED tilt difference of two tilts: `|θ₁ − θ₂|` folded mod `π/2` into
`[0, π/4]`.  Folding mod `π/2` and then into `[0, π/4]` is exactly "take the larger of
`|cos d|`, `|sin d|` as the cosine and the smaller as the sine", which is what
`octagon.tilt_dev_min` / `tcleaf.tilt_dev_min` compute in degrees — and it needs no
`arctan`. -/
def IsReducedTilt (θ₁ θ₂ D : ℝ) : Prop :=
  0 ≤ D ∧ D ≤ Real.pi / 4 ∧
  Real.cos D = max |Real.cos (θ₁ - θ₂)| |Real.sin (θ₁ - θ₂)| ∧
  Real.sin D = min |Real.cos (θ₁ - θ₂)| |Real.sin (θ₁ - θ₂)|

/-- **Lemma TC, support-function form** (`known_results.md` 26c).  For `D ∈ [0, π/2]`
the minimum over directions of the sum of the two half-widths of two unit squares at
relative tilt `D` is `(1 + cos D + sin D)/2`, attained on an edge normal (the
face-to-face placement).

`[C]` — the STATEMENT is frozen here as a `Prop`; the proof is not written, and no
axiom is introduced, so the project's axiom count is unchanged.  Verified to `2·10⁻¹⁶`
numerically (`known_results.md` 26c) and, on every deployed fire, by `≥ 10⁴` sampled
pose pairs (`attempts/A117-verifier-v2/results/tc_replay.json`).  The missing Lean step
is the separating-axis theorem for two interior-disjoint convex polygons, which
`Band.lean` records as not formalised in this development. -/
def TCSupportMin : Prop :=
  ∀ D : ℝ, 0 ≤ D → D ≤ Real.pi / 2 →
    (1 + tcWidth D) / 2 = (1 + Real.cos D + Real.sin D) / 2

/-- **Lemma TC.**  Two interior-disjoint closed unit squares whose tilts differ by `D`
(reduced mod `π/2` into `[0, π/4]`) have centres at least `(1 + cos D + sin D)/2` apart.
`[C]`, statement only — this is the named leaf that A112's 10 free kills and A111's free
pair kills rest on. -/
def TCCentreDist : Prop :=
  ∀ (q₁ q₂ : PSq) (θ₁ θ₂ D : ℝ), TiltOf q₁ θ₁ → TiltOf q₂ θ₂ → IsReducedTilt θ₁ θ₂ D →
    Disjoint (interior q₁.set) (interior q₂.set) →
    (1 + Real.cos D + Real.sin D) / 2
      ≤ Real.sqrt ((q₁.cx - q₂.cx) ^ 2 + (q₁.cy - q₂.cy) ^ 2)

/-- **The TC leaf**, in the shape of `Zones.core_meet_same_square` with the width
function in place of the core: two conditioned bins whose maximum centre distance is
strictly below `(1 + cos D_min + sin D_min)/2` for the MINIMUM tilt difference `D_min`
over the bins hold no two DISTINCT squares of a packing.  `[C]`, statement only; the
exact decision procedure is `attempts/A117-verifier-v2/code/tcleaf.py` (`tc_fires`),
which computes `cmax` and `D_min` in exact rational arithmetic with the tilt intervals
normalised to `[0, 90°]`. -/
def TCLeaf : Prop :=
  ∀ (n : ℕ) (s : ℝ) (Q : Fin n → Set RP) (i j : Fin n) (q₁ q₂ : PSq)
    (θ₁ θ₂ D cmax Dmin : ℝ),
    IsPacking n s Q → i ≠ j → Q i = q₁.set → Q j = q₂.set →
    TiltOf q₁ θ₁ → TiltOf q₂ θ₂ → IsReducedTilt θ₁ θ₂ D →
    Real.sqrt ((q₁.cx - q₂.cx) ^ 2 + (q₁.cy - q₂.cy) ^ 2) ≤ cmax →
    0 ≤ Dmin → Dmin ≤ D →
    cmax < (1 + Real.cos Dmin + Real.sin Dmin) / 2 → False

/-- The leaf follows from Lemma TC by monotonicity of `D ↦ (1 + cos D + sin D)/2` on
`[0, π/4]` — the only step between the two, and the reason `D_min` (a minimum, never a
maximum) is the right quantity to compute over the bins.  `[C]`, stated with its
premise. -/
def TCLeaf_of_TCCentreDist : Prop := TCCentreDist → TCLeaf

end S11
end PackingCert
