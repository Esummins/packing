import Mathlib.Tactic
import PackingCertMathlib.Parametrize
import PackingCertMathlib.LocalCertT
import PackingCertMathlib.Zones

/-!
# T5‴ — the shared-witness logic kill, and the `polycores` exemption clause (A135, from A132's spec)

A132 (`attempts/A132-polygon-core/notes/spec.md`) found that `Zones.core_meet_same_square` is
already stated for arbitrary SETS `K`, `K'` — no squareness anywhere — so the polygon core buys a
logic kill with **no new consumer theorem**.  Its §4.1 collapse goes one step further: the kill's
`hne` hypothesis needs only ONE point in both cores, and the implementation already produces and
certifies that point (`polycore.overlap_witness`, 64/64 on the firing nodes, each verified exactly
against BOTH boxes).  So for the LOGIC KILL Lean never sees a polygon: the certificate is **one
rational point plus two vertex checks**, and `polycore.py`'s clipping, simplification and hull are
the (untrusted) way that point is found.

This file supplies exactly that.

* `PBox` / `InPBox` — a rational parameter box carrying its TILT RANGE (`t = tan(θ/2)`), i.e. the
  certificate's `box` field with `t0/t1` rather than only `tm`.
* `cornerPolys` — the four rational quadratics of A132 spec §1 at one corner of the centre
  rectangle: with `d = v − c` and `(u, w) = (dx, dy)` then `(dy, −dx)`,
  `(½ − u) − 2w·t + (½ + u)·t² ≥ 0` and `(½ + u) + 2w·t + (½ − u)·t² ≥ 0` on `[t0, t1]`.
* `checkVertexInPBox` — the DECIDABLE check: those sixteen quadratics (four corners × two edge
  normals × two signs), each with a Bernstein positivity certificate, discharged by
  `LocalCertT.posCheck`.  Rational data only; `decide` / `native_decide` friendly, and it reuses
  the positivity machinery A126/A133 already built rather than introducing a new one.
* `checkVertexInPBox_sound` — **proved**: a passing check gives `v ∈ q.set` for EVERY pose `q` in
  the box.  Two ingredients: `abs_proj_le_half` (the quadratics are the projection bounds after
  clearing the positive denominator `1 + t²` of the half-angle parametrisation) and
  `biaffine_bound` (`c` enters the projections affinely, so the four corners of the centre
  rectangle suffice — the step `polycore.vertex_ok` states in a comment and takes for granted).
* `shared_point_same_square` — **T5‴**, the deployable leaf, proved: one rational point in the
  interior of both boxes' poses forces the two witnesses to be the same square.  Three lines,
  because `core_meet_same_square` does the work.

## The one gap, and it is not new

`core_meet_same_square` consumes `K ⊆ interior (Q i)`, while the vertex check certifies the CLOSED
square.  `StrictlyInside` names the interior form and `InteriorFromMargin` states the step that
supplies it from a strictly positive margin in the same quadratics — the emitter's `1e-6` inward
shrink is what pays for it (A132 spec §1, "Shrink and interiors").  This is the same
closed-vs-interior bridge A62 recorded as a HIGH hole "at every kill" and A63 closed for the
square core; nothing about the polygon makes it worse.

## Route (2)/(3): the `polycores` exemption clause

`PolySetSubsetPose` and `PolycoreExemptSound` state, in `ParamNoFam.lean`'s `[C]` style, the two
obligations the `polycores` clause of `attempts/A135-polycore-verifier/code/verify_case_v3.py`
rests on.  No axiom is introduced by this file.
-/

namespace PackingCert
namespace S11

open Set
open PackingCert.S11.LocalCertT

noncomputable section

/-! ## 1. The rational parameter box -/

/-- A parameter box, rational, carrying its TILT RANGE (the certificate's `box` field). -/
structure PBox where
  x0 : ℚ
  x1 : ℚ
  y0 : ℚ
  y1 : ℚ
  t0 : ℚ
  t1 : ℚ

/-- A pose lies in the box. -/
def InPBox (B : PBox) (q : PSq) : Prop :=
  (B.x0 : ℝ) ≤ q.cx ∧ q.cx ≤ (B.x1 : ℝ) ∧ (B.y0 : ℝ) ≤ q.cy ∧ q.cy ≤ (B.y1 : ℝ) ∧
  (B.t0 : ℝ) ≤ q.t ∧ q.t ≤ (B.t1 : ℝ)

/-! ## 2. Two elementary lemmas -/

/-- A function affine in one variable is nonnegative on `[a, b]` as soon as it is nonnegative at
both endpoints. -/
theorem affine_nonneg_of_endpoints {a b x p q : ℝ} (hax : a ≤ x) (hxb : x ≤ b)
    (ha : 0 ≤ p + q * a) (hb : 0 ≤ p + q * b) : 0 ≤ p + q * x := by
  by_cases hab : a < b
  · nlinarith [mul_nonneg (sub_nonneg.mpr hxb) ha, mul_nonneg (sub_nonneg.mpr hax) hb]
  · have hba : b ≤ a := not_lt.mp hab
    have hxa : x = a := le_antisymm (hxb.trans hba) hax
    rw [hxa]; exact ha

/-- An affine function of `(cx, cy)` nonnegative at the four corners of a rectangle is
nonnegative on the rectangle. -/
theorem biaffine_nonneg {x0 x1 y0 y1 cx cy P A B : ℝ}
    (hx0 : x0 ≤ cx) (hx1 : cx ≤ x1) (hy0 : y0 ≤ cy) (hy1 : cy ≤ y1)
    (h00 : 0 ≤ P + A * x0 + B * y0) (h01 : 0 ≤ P + A * x0 + B * y1)
    (h10 : 0 ≤ P + A * x1 + B * y0) (h11 : 0 ≤ P + A * x1 + B * y1) :
    0 ≤ P + A * cx + B * cy := by
  have h0 : 0 ≤ (P + A * x0) + B * cy :=
    affine_nonneg_of_endpoints hy0 hy1 (by linarith) (by linarith)
  have h1 : 0 ≤ (P + A * x1) + B * cy :=
    affine_nonneg_of_endpoints hy0 hy1 (by linarith) (by linarith)
  have h2 : 0 ≤ (P + B * cy) + A * cx :=
    affine_nonneg_of_endpoints hx0 hx1 (by linarith) (by linarith)
  linarith

/-- **The corner reduction, in the shape the projections have.**  `K − A·cx − B·cy` is the generic
affine form of a projection of `v − c` on a fixed direction; a bound at the four corners is a
bound on the whole rectangle.  This is `polycore.vertex_ok`'s "`c` enters affinely, so its max over
the rectangle is at a corner", made a theorem. -/
theorem biaffine_bound {x0 x1 y0 y1 cx cy K A B : ℝ}
    (hx0 : x0 ≤ cx) (hx1 : cx ≤ x1) (hy0 : y0 ≤ cy) (hy1 : cy ≤ y1)
    (h00 : |K - A * x0 - B * y0| ≤ 1 / 2) (h01 : |K - A * x0 - B * y1| ≤ 1 / 2)
    (h10 : |K - A * x1 - B * y0| ≤ 1 / 2) (h11 : |K - A * x1 - B * y1| ≤ 1 / 2) :
    |K - A * cx - B * cy| ≤ 1 / 2 := by
  rw [abs_le] at h00 h01 h10 h11 ⊢
  constructor
  · have := biaffine_nonneg (P := 1 / 2 + K) (A := -A) (B := -B) hx0 hx1 hy0 hy1
      (by linarith [h00.1]) (by linarith [h01.1]) (by linarith [h10.1]) (by linarith [h11.1])
    linarith
  · have := biaffine_nonneg (P := 1 / 2 - K) (A := A) (B := B) hx0 hx1 hy0 hy1
      (by linarith [h00.2]) (by linarith [h01.2]) (by linarith [h10.2]) (by linarith [h11.2])
    linarith

/-- **The half-angle clearing.**  The two rational quadratics of A132 spec §1 are exactly
`|u cos θ + w sin θ| ≤ 1/2` after multiplying by the positive denominator `1 + t²`. -/
theorem abs_proj_le_half {u w t : ℝ}
    (h1 : 0 ≤ (1 / 2 - u) + (-2 * w) * t + (1 / 2 + u) * t ^ 2)
    (h2 : 0 ≤ (1 / 2 + u) + (2 * w) * t + (1 / 2 - u) * t ^ 2) :
    |u * cosT t + w * sinT t| ≤ 1 / 2 := by
  have hD : (0 : ℝ) < 1 + t ^ 2 := by positivity
  have e1 : (u * cosT t + w * sinT t - 1 / 2) * (1 + t ^ 2)
      = -((1 / 2 - u) + (-2 * w) * t + (1 / 2 + u) * t ^ 2) := by
    unfold cosT sinT
    field_simp
    ring
  have e2 : (u * cosT t + w * sinT t + 1 / 2) * (1 + t ^ 2)
      = (1 / 2 + u) + (2 * w) * t + (1 / 2 - u) * t ^ 2 := by
    unfold cosT sinT
    field_simp
    ring
  rw [abs_le]
  constructor
  · nlinarith [e2, hD, h2]
  · nlinarith [e1, hD, h1]

/-! ## 3. The decidable vertex check -/

/-- The four quadratics of ONE corner `c` of the centre rectangle, for the point `v`:
`(u, w) = (dx, dy)` and `(dy, −dx)` with `d = v − c`, each with both signs. -/
def cornerPolys (v c : ℚ × ℚ) : List Poly :=
  [ [1 / 2 - (v.1 - c.1), -2 * (v.2 - c.2), 1 / 2 + (v.1 - c.1)],
    [1 / 2 + (v.1 - c.1),  2 * (v.2 - c.2), 1 / 2 - (v.1 - c.1)],
    [1 / 2 - (v.2 - c.2),  2 * (v.1 - c.1), 1 / 2 + (v.2 - c.2)],
    [1 / 2 + (v.2 - c.2), -2 * (v.1 - c.1), 1 / 2 - (v.2 - c.2)] ]

/-- `posCheck` down two parallel lists: the polynomials and their positivity certificates. -/
def allPos : List Poly → List Poly → ℚ → ℚ → Bool
  | [], [], _, _ => true
  | p :: ps, c :: cs, a, b => posCheck p c a b && allPos ps cs a b
  | _, _, _, _ => false

theorem allPos_sound : ∀ (ps cs : List Poly) (a b : ℚ), allPos ps cs a b = true →
    ∀ p ∈ ps, ∀ x : ℝ, (a : ℝ) ≤ x → x ≤ (b : ℝ) → 0 ≤ peval p x := by
  intro ps
  induction ps with
  | nil => intro cs a b _ p hp; simp at hp
  | cons p ps ih =>
    intro cs a b h
    cases cs with
    | nil => simp [allPos] at h
    | cons c cs =>
      rw [allPos, Bool.and_eq_true] at h
      intro r hr x h1 h2
      rcases List.mem_cons.mp hr with rfl | hr'
      · exact posCheck_sound h.1 h1 h2
      · exact ih cs a b h.2 r hr' x h1 h2

/-- The check at one corner. -/
def checkCorner (t0 t1 : ℚ) (v c : ℚ × ℚ) (cs : List Poly) : Bool :=
  allPos (cornerPolys v c) cs t0 t1

/-- **The vertex check.**  Decidable, rational: the two quadratics of A132 spec §1 evaluated over
`[t0, t1]` with a Bernstein positivity certificate, at the four corners of the centre rectangle
and for the two edge normals. -/
def checkVertexInPBox (B : PBox) (v : ℚ × ℚ) (cs : List (List Poly)) : Bool :=
  match cs with
  | [c0, c1, c2, c3] =>
      checkCorner B.t0 B.t1 v (B.x0, B.y0) c0 &&
      checkCorner B.t0 B.t1 v (B.x1, B.y0) c1 &&
      checkCorner B.t0 B.t1 v (B.x1, B.y1) c2 &&
      checkCorner B.t0 B.t1 v (B.x0, B.y1) c3
  | _ => false

/-- One corner's four quadratics give the two projection bounds at that corner. -/
theorem corner_proj {v c : ℚ × ℚ} {t0 t1 : ℚ} {cs : List Poly}
    (h : checkCorner t0 t1 v c cs = true) {t : ℝ} (ht0 : (t0 : ℝ) ≤ t) (ht1 : t ≤ (t1 : ℝ)) :
    |((v.1 : ℝ) - (c.1 : ℝ)) * cosT t + ((v.2 : ℝ) - (c.2 : ℝ)) * sinT t| ≤ 1 / 2 ∧
    |((v.2 : ℝ) - (c.2 : ℝ)) * cosT t + (-((v.1 : ℝ) - (c.1 : ℝ))) * sinT t| ≤ 1 / 2 := by
  have H := allPos_sound (cornerPolys v c) cs t0 t1 h
  have h0 : (0 : ℝ) ≤ peval [1 / 2 - (v.1 - c.1), -2 * (v.2 - c.2), 1 / 2 + (v.1 - c.1)] t :=
    H _ (by simp [cornerPolys]) t ht0 ht1
  have h1 : (0 : ℝ) ≤ peval [1 / 2 + (v.1 - c.1), 2 * (v.2 - c.2), 1 / 2 - (v.1 - c.1)] t :=
    H _ (by simp [cornerPolys]) t ht0 ht1
  have h2 : (0 : ℝ) ≤ peval [1 / 2 - (v.2 - c.2), 2 * (v.1 - c.1), 1 / 2 + (v.2 - c.2)] t :=
    H _ (by simp [cornerPolys]) t ht0 ht1
  have h3 : (0 : ℝ) ≤ peval [1 / 2 + (v.2 - c.2), -2 * (v.1 - c.1), 1 / 2 - (v.2 - c.2)] t :=
    H _ (by simp [cornerPolys]) t ht0 ht1
  simp only [peval] at h0 h1 h2 h3
  push_cast at h0 h1 h2 h3
  refine ⟨abs_proj_le_half ?_ ?_, abs_proj_le_half ?_ ?_⟩
  · linarith [h0]
  · linarith [h1]
  · linarith [h2]
  · linarith [h3]

/-- **Soundness of the vertex check.**  A passing check proves that the rational point lies in the
closed unit square of EVERY pose in the box. -/
theorem checkVertexInPBox_sound {B : PBox} {v : ℚ × ℚ} {cs : List (List Poly)}
    (h : checkVertexInPBox B v cs = true) :
    ∀ q : PSq, InPBox B q → ((v.1 : ℝ), (v.2 : ℝ)) ∈ q.set := by
  match cs, h with
  | [c0, c1, c2, c3], h =>
    rw [checkVertexInPBox, Bool.and_eq_true, Bool.and_eq_true, Bool.and_eq_true] at h
    obtain ⟨⟨⟨k00, k10⟩, k11⟩, k01⟩ := h
    rintro q ⟨hx0, hx1, hy0, hy1, ht0, ht1⟩
    obtain ⟨a00, b00⟩ := corner_proj k00 ht0 ht1
    obtain ⟨a10, b10⟩ := corner_proj k10 ht0 ht1
    obtain ⟨a11, b11⟩ := corner_proj k11 ht0 ht1
    obtain ⟨a01, b01⟩ := corner_proj k01 ht0 ht1
    set C := cosT q.t with hCdef
    set S := sinT q.t with hSdef
    have eu : ∀ cx cy : ℝ, ((v.1 : ℝ) - cx) * C + ((v.2 : ℝ) - cy) * S
        = ((v.1 : ℝ) * C + (v.2 : ℝ) * S) - C * cx - S * cy := by intro cx cy; ring
    have ev : ∀ cx cy : ℝ, ((v.2 : ℝ) - cy) * C + (-((v.1 : ℝ) - cx)) * S
        = ((v.2 : ℝ) * C - (v.1 : ℝ) * S) - (-S) * cx - C * cy := by intro cx cy; ring
    rw [eu] at a00 a10 a11 a01
    rw [ev] at b00 b10 b11 b01
    have hu : |((v.1 : ℝ) * C + (v.2 : ℝ) * S) - C * q.cx - S * q.cy| ≤ 1 / 2 :=
      biaffine_bound hx0 hx1 hy0 hy1 a00 a01 a10 a11
    have hv : |((v.2 : ℝ) * C - (v.1 : ℝ) * S) - (-S) * q.cx - C * q.cy| ≤ 1 / 2 :=
      biaffine_bound hx0 hx1 hy0 hy1 b00 b01 b10 b11
    rw [mem_set_iff_uv]
    simp only [rdot, edir, perpV, ← hCdef, ← hSdef]
    constructor
    · calc |((v.1 : ℝ) - q.cx) * C + ((v.2 : ℝ) - q.cy) * S|
          = |((v.1 : ℝ) * C + (v.2 : ℝ) * S) - C * q.cx - S * q.cy| := by rw [eu]
        _ ≤ 1 / 2 := hu
    · calc |((v.1 : ℝ) - q.cx) * -S + ((v.2 : ℝ) - q.cy) * C|
          = |((v.2 : ℝ) * C - (v.1 : ℝ) * S) - (-S) * q.cx - C * q.cy| := by ring_nf
        _ ≤ 1 / 2 := hv

/-! ## 4. T5‴ — the deployable leaf -/

/-- A rational point in the OPEN square of every pose of a box. -/
def StrictlyInside (B : PBox) (v : ℚ × ℚ) : Prop :=
  ∀ q : PSq, InPBox B q → ((v.1 : ℝ), (v.2 : ℝ)) ∈ interior q.set

/-- **The margin step.**  Running the SAME sixteen quadratics with a strictly positive right-hand
side (`≥ m > 0` instead of `≥ 0`) puts the point in the OPEN square of every pose.  This is what
the emitter's `1e-6` inward shrink pays for (A132 spec §1).  `[C]`: statement frozen, proof not
written; it is the closed-vs-interior bridge A62 recorded as a HIGH hole at every kill and A63
closed for the square core — the polygon does not make it worse or different. -/
def InteriorFromMargin : Prop :=
  ∀ (B : PBox) (v : ℚ × ℚ) (m : ℚ), 0 < m →
    (∀ q : PSq, InPBox B q →
      |((v.1 : ℝ) - q.cx) * cosT q.t + ((v.2 : ℝ) - q.cy) * sinT q.t| ≤ 1 / 2 - (m : ℝ) ∧
      |((v.1 : ℝ) - q.cx) * (-sinT q.t) + ((v.2 : ℝ) - q.cy) * cosT q.t| ≤ 1 / 2 - (m : ℝ)) →
    StrictlyInside B v

/-- **T5‴, the deployable form.**  One rational point certified for BOTH boxes: the two witnesses
are the same square, so a child requiring them distinct is empty by logic.  A specialisation of
`Zones.core_meet_same_square`, not a new argument — the polygon has disappeared entirely. -/
theorem shared_point_same_square {n : ℕ} {s : ℝ} {Q : Fin n → Set RP} (hP : IsPacking n s Q)
    {i j : Fin n} {B B' : PBox} {w : ℚ × ℚ}
    (hw : StrictlyInside B w) (hw' : StrictlyInside B' w)
    (hi : ∃ q : PSq, InPBox B q ∧ Q i = q.set)
    (hj : ∃ q : PSq, InPBox B' q ∧ Q j = q.set) : i = j := by
  obtain ⟨q, hq, hqi⟩ := hi
  obtain ⟨q', hq', hqj⟩ := hj
  refine core_meet_same_square hP (K := {((w.1 : ℝ), (w.2 : ℝ))})
    (K' := {((w.1 : ℝ), (w.2 : ℝ))}) ?_ ?_ ⟨_, rfl, rfl⟩
  · rw [hqi]; exact Set.singleton_subset_iff.mpr (hw q hq)
  · rw [hqj]; exact Set.singleton_subset_iff.mpr (hw' q' hq')

/-! ## 5. Route (2)/(3): the `polycores` exemption clause of `verify_case_v3.py` -/

/-- The polygon core denoted by a rational vertex list: its convex hull. -/
def polySet (V : List (ℚ × ℚ)) : Set RP :=
  convexHull ℝ {p : RP | ∃ v ∈ V, p = ((v.1 : ℝ), (v.2 : ℝ))}

/-- **Every vertex inside every pose ⇒ the hull is inside every pose.**  `[C]`: the only missing
ingredient is `Convex ℝ (PSq.set q)`, which via `mem_set_iff_uv` is `Convex.inter` of two
`convex_halfspace`-style sets; `checkVertexInPBox_sound` supplies the generators and
`convexHull_min` finishes. -/
def PolySetSubsetPose : Prop :=
  ∀ (B : PBox) (V : List (ℚ × ℚ)),
    (∀ v ∈ V, ∀ q : PSq, InPBox B q → ((v.1 : ℝ), (v.2 : ℝ)) ∈ q.set) →
    ∀ q : PSq, InPBox B q → polySet V ⊆ q.set

/-- **The v3 exemption lemma.**  A placement whose square meets the polygon core of a hypothesis
box is not one of the `n − #cores` squares the budget accounts for: it meets that box's witness at
EVERY pose, so it either IS that witness or contradicts interior-disjointness.  This is the exact
analogue of the frozen core clause with the square core replaced by the polygon, and it is what
`verify_case_v3.polycore_exempt_frac` decides.

`[C]`: statement frozen, proof not written.  What remains, in order: (a) `PolySetSubsetPose`
(convexity of `PSq.set`); (b) the vertex-in-all-poses step, which is `checkVertexInPBox_sound`
and IS proved in §3 above — the monotone `cosT`/`sinT` bounds it would otherwise need are
`LocalCertT.cosT_anti` / `sinT_mono` / `cosT_mem` / `sinT_mem`; (c) the separating-axis step
"no separating axis ⇒ the convex polygon and the square meet", which is the ONLY genuinely new
obligation and is the same one `ParamNoFam.TCLeaf` and `Band.lean` are blocked on. -/
def PolycoreExemptSound : Prop :=
  ∀ (n : ℕ) (s : ℝ) (Q : Fin n → Set RP) (i j : Fin n) (B : PBox) (V : List (ℚ × ℚ)) (qj : PSq),
    IsPacking n s Q →
    (∀ v ∈ V, StrictlyInside B v) →
    (∃ q : PSq, InPBox B q ∧ Q i = q.set) →
    Q j = qj.set → (interior qj.set ∩ polySet V).Nonempty →
    i = j

end

end S11
end PackingCert
