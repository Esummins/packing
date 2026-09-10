import PackingCertMathlib.WindowsCore

/-!
# The WINDOWS clause — rational pieces to integer boxes (A192)

`verify_case_v4.window_boxes`: a rational `(t, c)`-piece is rounded OUTWARD to the verifier's
integer grid (`t·2^K`, `x·D`, `y·D`) and clamped to the root box (`t ∈ [0, 2^K]`, centres in
`[D/2, SD − D/2]`); an empty clamped box is a vacuous piece.  `windowBox` is that rounding,
`roundBounds` the six inequalities an ADMISSIBLE pose of the rational piece satisfies against
it, `inBox_of_windowBox` its soundness, and `winSet_of_pieces` the lift to the window predicate
of `WindowsCheck.lean`: a certificate whose integer pieces are the `windowBox` images of its
rational pieces has (H1) for the RATIONAL windows.  No axiom is introduced.
-/

namespace PackingCert
namespace S11
namespace WindowsW

open Set MeasureI CaseI

/-- `window_boxes`: outward rounding to the grid, clamped to the root box. -/
def windowBox (ctx : Ctx) (P : PBox) : Option IBox :=
  if max 0 ⌊P.t0 * (ctx.TROOT : ℚ)⌋ ≤ min ctx.TROOT ⌈P.t1 * (ctx.TROOT : ℚ)⌉ ∧
      max (ctx.D / 2) ⌊P.x0 * (ctx.D : ℚ)⌋ ≤ min (ctx.SD - ctx.D / 2) ⌈P.x1 * (ctx.D : ℚ)⌉ ∧
      max (ctx.D / 2) ⌊P.y0 * (ctx.D : ℚ)⌋ ≤ min (ctx.SD - ctx.D / 2) ⌈P.y1 * (ctx.D : ℚ)⌉ then
    some ⟨max 0 ⌊P.t0 * (ctx.TROOT : ℚ)⌋, min ctx.TROOT ⌈P.t1 * (ctx.TROOT : ℚ)⌉,
      max (ctx.D / 2) ⌊P.x0 * (ctx.D : ℚ)⌋, min (ctx.SD - ctx.D / 2) ⌈P.x1 * (ctx.D : ℚ)⌉,
      max (ctx.D / 2) ⌊P.y0 * (ctx.D : ℚ)⌋, min (ctx.SD - ctx.D / 2) ⌈P.y1 * (ctx.D : ℚ)⌉⟩
  else none

/-- `⌊a·M⌋ ≤ b·M` for `a ≤ b`, `0 ≤ M` (casts to `ℝ`). -/
theorem floor_mul_le {a : ℚ} {b : ℝ} {M : ℤ} (hab : (a : ℝ) ≤ b) (hM : (0 : ℝ) ≤ (M : ℝ)) :
    ((⌊a * (M : ℚ)⌋ : ℤ) : ℝ) ≤ b * (M : ℝ) := by
  have h1 : ((⌊a * (M : ℚ)⌋ : ℤ) : ℚ) ≤ a * (M : ℚ) := Int.floor_le _
  have h2 : ((⌊a * (M : ℚ)⌋ : ℤ) : ℝ) ≤ (a : ℝ) * (M : ℝ) := by exact_mod_cast h1
  have h3 : (a : ℝ) * (M : ℝ) ≤ b * (M : ℝ) := mul_le_mul_of_nonneg_right hab hM
  linarith

/-- `b·M ≤ ⌈a·M⌉` for `b ≤ a`, `0 ≤ M`. -/
theorem le_ceil_mul {a : ℚ} {b : ℝ} {M : ℤ} (hba : b ≤ (a : ℝ)) (hM : (0 : ℝ) ≤ (M : ℝ)) :
    b * (M : ℝ) ≤ ((⌈a * (M : ℚ)⌉ : ℤ) : ℝ) := by
  have h1 : a * (M : ℚ) ≤ ((⌈a * (M : ℚ)⌉ : ℤ) : ℚ) := Int.le_ceil _
  have h2 : (a : ℝ) * (M : ℝ) ≤ ((⌈a * (M : ℚ)⌉ : ℤ) : ℝ) := by exact_mod_cast h1
  have h3 : b * (M : ℝ) ≤ (a : ℝ) * (M : ℝ) := mul_le_mul_of_nonneg_right hba hM
  linarith

/-- The six bounds of an admissible pose of the rational piece against the rounded box. -/
theorem roundBounds {c : CCertI} (hsd : 0 < c.sDen) {P : PBox} (q : PSq) (hq0 : 0 ≤ q.t)
    (hq1 : q.t ≤ 1) (hsub : q.set ⊆ container (caseSide c)) (hP : InPBox P q) :
    ((max 0 ⌊P.t0 * ((mkCtx (toMCert c)).TROOT : ℚ)⌋ : ℤ) : ℝ) ≤ q.t * ((mkCtx (toMCert c)).TROOT : ℝ) ∧
    q.t * ((mkCtx (toMCert c)).TROOT : ℝ) ≤ ((min (mkCtx (toMCert c)).TROOT ⌈P.t1 * ((mkCtx (toMCert c)).TROOT : ℚ)⌉ : ℤ) : ℝ) ∧
    ((max ((mkCtx (toMCert c)).D / 2) ⌊P.x0 * ((mkCtx (toMCert c)).D : ℚ)⌋ : ℤ) : ℝ) ≤ q.cx * ((mkCtx (toMCert c)).D : ℝ) ∧
    q.cx * ((mkCtx (toMCert c)).D : ℝ) ≤ ((min ((mkCtx (toMCert c)).SD - (mkCtx (toMCert c)).D / 2) ⌈P.x1 * ((mkCtx (toMCert c)).D : ℚ)⌉ : ℤ) : ℝ) ∧
    ((max ((mkCtx (toMCert c)).D / 2) ⌊P.y0 * ((mkCtx (toMCert c)).D : ℚ)⌋ : ℤ) : ℝ) ≤ q.cy * ((mkCtx (toMCert c)).D : ℝ) ∧
    q.cy * ((mkCtx (toMCert c)).D : ℝ) ≤ ((min ((mkCtx (toMCert c)).SD - (mkCtx (toMCert c)).D / 2) ⌈P.y1 * ((mkCtx (toMCert c)).D : ℚ)⌉ : ℤ) : ℝ) := by
  obtain ⟨r1, r2, r3, r4, r5, r6⟩ := inBox_root hsd q hq0 hq1 hsub
  obtain ⟨p1, p2, p3, p4, p5, p6⟩ := hP
  have hR : (0 : ℝ) ≤ ((mkCtx (toMCert c)).TROOT : ℝ) := by
    change (0 : ℝ) ≤ (((2 : Int) ^ (c.depth + 1) : Int) : ℝ)
    push_cast
    positivity
  have hDR : (0 : ℝ) ≤ ((mkCtx (toMCert c)).D : ℝ) := by
    change (0 : ℝ) ≤ ((c.sDen * (2 : Int) ^ (c.depth + 2) : Int) : ℝ)
    have : (0 : ℝ) < (c.sDen : ℝ) := by exact_mod_cast hsd
    push_cast
    positivity
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
  · rw [Int.cast_max]
    have h0 : ((0 : ℤ) : ℝ) ≤ q.t * ((mkCtx (toMCert c)).TROOT : ℝ) := r1
    exact max_le (by simpa using h0) (floor_mul_le p5 hR)
  · rw [Int.cast_min]
    exact le_min r2 (le_ceil_mul p6 hR)
  · rw [Int.cast_max]
    exact max_le r3 (floor_mul_le p1 hDR)
  · rw [Int.cast_min]
    exact le_min r4 (le_ceil_mul p2 hDR)
  · rw [Int.cast_max]
    exact max_le r5 (floor_mul_le p3 hDR)
  · rw [Int.cast_min]
    exact le_min r6 (le_ceil_mul p4 hDR)

/-- **Soundness of the rounding**: an admissible pose in the rational piece lies in its
integer box. -/
theorem inBox_of_windowBox {c : CCertI} (hsd : 0 < c.sDen) {P : PBox} {b : IBox}
    (hb : windowBox (mkCtx (toMCert c)) P = some b) (q : PSq) (hq0 : 0 ≤ q.t) (hq1 : q.t ≤ 1)
    (hsub : q.set ⊆ container (caseSide c)) (hP : InPBox P q) :
    inBox (mkCtx (toMCert c)) b q := by
  obtain ⟨b1, b2, b3, b4, b5, b6⟩ := roundBounds hsd q hq0 hq1 hsub hP
  unfold windowBox at hb
  split_ifs at hb with hc
  rw [Option.some.injEq] at hb
  subst hb
  exact ⟨b1, b2, b3, b4, b5, b6⟩

/-- A rational piece holding an admissible pose is not vacuous. -/
theorem windowBox_ne_none {c : CCertI} (hsd : 0 < c.sDen) {P : PBox}
    (q : PSq) (hq0 : 0 ≤ q.t) (hq1 : q.t ≤ 1)
    (hsub : q.set ⊆ container (caseSide c)) (hP : InPBox P q) :
    windowBox (mkCtx (toMCert c)) P ≠ none := by
  obtain ⟨b1, b2, b3, b4, b5, b6⟩ := roundBounds hsd q hq0 hq1 hsub hP
  intro hb
  unfold windowBox at hb
  split_ifs at hb with hc
  refine hc ⟨?_, ?_, ?_⟩
  · exact_mod_cast b1.trans b2
  · exact_mod_cast b3.trans b4
  · exact_mod_cast b5.trans b6

/-- (H1) for RATIONAL windows: a window whose integer pieces are the `windowBox` images of a
rational piece list `Ps` is satisfied (`WinSet`) by every admissible square with a
parametrisation in one of the rational pieces. -/
theorem winSet_of_pieces {c : CCertI} (hsd : 0 < c.sDen) {w : CWindow} {Ps : List PBox}
    (hw : w.pieces = Ps.filterMap (windowBox (mkCtx (toMCert c))))
    (q : PSq) (hq0 : 0 ≤ q.t) (hq1 : q.t ≤ 1) (hsub : q.set ⊆ container (caseSide c))
    (hP : ∃ P ∈ Ps, InPBox P q) : WinSet (mkCtx (toMCert c)) w q.set := by
  obtain ⟨P, hPs, hPq⟩ := hP
  refine ⟨q, ⟨hq0, hq1⟩, rfl, ?_⟩
  rcases hb : windowBox (mkCtx (toMCert c)) P with _ | b
  · exact absurd hb (windowBox_ne_none hsd q hq0 hq1 hsub hPq)
  · refine ⟨b, ?_, inBox_of_windowBox hsd hb q hq0 hq1 hsub hPq⟩
    rw [hw, List.mem_filterMap]
    exact ⟨P, hPs, hb⟩

end WindowsW
end S11
end PackingCert
