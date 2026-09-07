import PackingCertMathlib.Local
import PackingCertMathlib.Attain

/-!
# Lemma SAT for open interiors — A126 T2

`Local.lean` (A119) states Lemma SAT for INTERIORS as its one project axiom
`LocalCert.sat_selection`: two unit squares with disjoint interiors admit one of the eight
signed separating-axis rows `g_σ ≥ 0`.  `CaseSat.sat_squares` proves the CLOSED-square form
(the four projection overlaps ⇒ the squares MEET).  This file closes the gap: `sat_selection_thm`
is a THEOREM with the axiom's exact statement, and `cover_pair'` is the axiom-free
re-derivation of the one lemma of `Local.lean` that consumes the axiom.

## The argument (`docs/proofs/local_certificate.md` §1, made finite)

Contrapositive.  If all eight `g_σ < 0` then, in the owner's frame, the four projection
overlaps hold STRICTLY, with the SAME right-hand side

    `B = 1/2 + (|C| + |S|)/2`,   `C = cos Δ`, `S = sin Δ`, `Δ = θ_o − θ_w`

(`octagon_strict`'s hypotheses).  Put `M` = the max of the four left-hand sides (`M < B`) and
`λ = (M/B + 1)/2 ∈ (M/B, 1)`.  Then `sat_squares` applies verbatim to the picture scaled by
`1/λ` (`a = 1/2`, centre offset `d/λ`), and its conclusion `d/λ = μ + b₁u + b₂u^⊥` with
`|μᵢ|, |bᵢ| ≤ 1/2` scales back to

    `d = λμ + (λb₁)u + (λb₂)u^⊥`,  `|λμᵢ|, |λbᵢ| ≤ λ/2 < 1/2`,

i.e. all four coordinates are STRICTLY inside — and `Attain.mem_interior_iff_uv` (the interior
of a parametrised square is exactly the open `u/v` box) turns that into an interior point of
BOTH squares, contradicting the disjointness hypothesis.

No limit and no subsequence is needed: `λ` is written down (`octagon_strict_core`), which is
why the whole argument is one file with no new axiom.  The rotation that `sat_squares` does not
cover (`c = cos Δ < 0`) is handled by replacing the other square's edge direction `u` by `−u` —
the same point set, and the conjunction `|u-coord| < 1/2 ∧ |u^⊥-coord| < 1/2` is invariant.
-/

namespace PackingCert
namespace S11
namespace LocalCert

open Set

noncomputable section

/-! ## 1. The support width is symmetric -/

/-- `w(θ_w − θ_o) = w(θ_o − θ_w)`: the support width of the OTHER square in the owner's frame
does not depend on which of the two is called the owner. -/
theorem wrel_comm (qw qo : PSq) : wrel qo qw = wrel qw qo := by
  unfold wrel
  rw [show cosT qo.t * cosT qw.t + sinT qo.t * sinT qw.t
        = cosT qw.t * cosT qo.t + sinT qw.t * sinT qo.t from by ring,
    show cosT qo.t * sinT qw.t - sinT qo.t * cosT qw.t
        = -(cosT qw.t * sinT qo.t - sinT qw.t * cosT qo.t) from by ring, abs_neg]

/-! ## 2. The strict octagon lemma -/

/-- `sat_squares` at `a = 1/2` with all four overlaps STRICT, for `cos Δ ≥ 0`: the offset `d`
decomposes with all four coefficients strictly inside their intervals.  The scale
`λ = (M/B + 1)/2` is explicit — this is the shrink of `local_certificate.md` §1. -/
private theorem octagon_strict_core {C S d1 d2 : ℝ} (hC : 0 ≤ C) (hCS : C ^ 2 + S ^ 2 = 1)
    (h1 : |d1| < 1 / 2 + (C + |S|) / 2) (h2 : |d2| < 1 / 2 + (C + |S|) / 2)
    (h3 : |C * d1 + S * d2| < 1 / 2 + (C + |S|) / 2)
    (h4 : |(-S) * d1 + C * d2| < 1 / 2 + (C + |S|) / 2) :
    ∃ m1 m2 b1 b2 : ℝ, |m1| < 1 / 2 ∧ |m2| < 1 / 2 ∧ |b1| < 1 / 2 ∧ |b2| < 1 / 2 ∧
      d1 = m1 + b1 * C - b2 * S ∧ d2 = m2 + b1 * S + b2 * C := by
  have hSabs : 0 ≤ |S| := abs_nonneg S
  set B : ℝ := 1 / 2 + (C + |S|) / 2 with hBdef
  have hBpos : 0 < B := by rw [hBdef]; linarith
  set M : ℝ := max (max |d1| |d2|) (max |C * d1 + S * d2| |(-S) * d1 + C * d2|) with hMdef
  have hM0 : 0 ≤ M :=
    le_trans (abs_nonneg d1) (le_trans (le_max_left _ _) (le_max_left _ _))
  have hMB : M < B := max_lt (max_lt h1 h2) (max_lt h3 h4)
  have hMBlt : M / B < 1 := (div_lt_one hBpos).mpr hMB
  have hMB0 : 0 ≤ M / B := div_nonneg hM0 hBpos.le
  set lam : ℝ := (M / B + 1) / 2 with hlamdef
  have hlam1 : lam < 1 := by rw [hlamdef]; linarith
  have hlam0 : 0 < lam := by rw [hlamdef]; linarith
  have hMlam : M ≤ lam * B := by
    have hkey : M / B * B = M := div_mul_cancel₀ M hBpos.ne'
    have hlb : lam * B = (M / B * B + B) / 2 := by rw [hlamdef]; ring
    rw [hlb, hkey]
    linarith
  have hscale : ∀ x : ℝ, |x| ≤ M → |x / lam| ≤ B := by
    intro x hx
    rw [abs_div, abs_of_pos hlam0, div_le_iff₀ hlam0]
    calc |x| ≤ M := hx
      _ ≤ lam * B := hMlam
      _ = B * lam := by ring
  have e1 : |d1 / lam| ≤ 1 / 2 + (C + |S|) / 2 :=
    hscale d1 (le_trans (le_max_left _ _) (le_max_left _ _))
  have e2 : |d2 / lam| ≤ 1 / 2 + (C + |S|) / 2 :=
    hscale d2 (le_trans (le_max_right _ _) (le_max_left _ _))
  have e3 : |C * (d1 / lam) + S * (d2 / lam)| ≤ 1 / 2 + 1 / 2 * (C + |S|) := by
    rw [show C * (d1 / lam) + S * (d2 / lam) = (C * d1 + S * d2) / lam from by ring]
    have hx := hscale (C * d1 + S * d2) (le_trans (le_max_left _ _) (le_max_right _ _))
    rw [hBdef] at hx
    linarith
  have e4 : |(-S) * (d1 / lam) + C * (d2 / lam)| ≤ 1 / 2 + 1 / 2 * (C + |S|) := by
    rw [show (-S) * (d1 / lam) + C * (d2 / lam) = ((-S) * d1 + C * d2) / lam from by ring]
    have hx := hscale ((-S) * d1 + C * d2) (le_trans (le_max_right _ _) (le_max_right _ _))
    rw [hBdef] at hx
    linarith
  obtain ⟨m1, m2, b1, b2, hm1, hm2, hb1, hb2, hd1, hd2⟩ :=
    sat_squares (c := C) (s := S) (a := 1 / 2) (d1 := d1 / lam) (d2 := d2 / lam)
      hC hCS (by norm_num) e1 e2 e3 e4
  have hhalf : ∀ x : ℝ, |x| ≤ 1 / 2 → |lam * x| < 1 / 2 := by
    intro x hx
    rw [abs_mul, abs_of_pos hlam0]
    nlinarith [abs_nonneg x]
  refine ⟨lam * m1, lam * m2, lam * b1, lam * b2, hhalf _ hm1, hhalf _ hm2,
    hhalf _ hb1, hhalf _ hb2, ?_, ?_⟩
  · have hb : lam * (d1 / lam) = d1 := by field_simp
    rw [← hb, hd1]; ring
  · have hb : lam * (d2 / lam) = d2 := by field_simp
    rw [← hb, hd2]; ring

/-- The strict octagon lemma without the sign restriction on `C = cos Δ`: replacing the other
square's edge direction `u` by `−u` describes the SAME square and flips `(C, S)` to
`(−C, −S)`. -/
private theorem octagon_strict {C S d1 d2 : ℝ} (hCS : C ^ 2 + S ^ 2 = 1)
    (h1 : |d1| < 1 / 2 + (|C| + |S|) / 2) (h2 : |d2| < 1 / 2 + (|C| + |S|) / 2)
    (h3 : |C * d1 + S * d2| < 1 / 2 + (|C| + |S|) / 2)
    (h4 : |(-S) * d1 + C * d2| < 1 / 2 + (|C| + |S|) / 2) :
    ∃ m1 m2 b1 b2 : ℝ, |m1| < 1 / 2 ∧ |m2| < 1 / 2 ∧ |b1| < 1 / 2 ∧ |b2| < 1 / 2 ∧
      d1 = m1 + b1 * C - b2 * S ∧ d2 = m2 + b1 * S + b2 * C := by
  have habsS : |(-S)| = |S| := abs_neg S
  rcases le_total 0 C with hc | hc
  · rw [abs_of_nonneg hc] at h1 h2 h3 h4
    exact octagon_strict_core hc hCS h1 h2 h3 h4
  · have hc' : 0 ≤ -C := by linarith
    rw [abs_of_nonpos hc] at h1 h2 h3 h4
    have g1 : |d1| < 1 / 2 + ((-C) + |(-S)|) / 2 := by rw [habsS]; exact h1
    have g2 : |d2| < 1 / 2 + ((-C) + |(-S)|) / 2 := by rw [habsS]; exact h2
    have g3 : |(-C) * d1 + (-S) * d2| < 1 / 2 + ((-C) + |(-S)|) / 2 := by
      rw [habsS, show (-C) * d1 + (-S) * d2 = -(C * d1 + S * d2) from by ring, abs_neg]
      exact h3
    have g4 : |(-(-S)) * d1 + (-C) * d2| < 1 / 2 + ((-C) + |(-S)|) / 2 := by
      rw [habsS, show (-(-S)) * d1 + (-C) * d2 = -((-S) * d1 + C * d2) from by ring, abs_neg]
      exact h4
    obtain ⟨m1, m2, b1, b2, hm1, hm2, hb1, hb2, hd1, hd2⟩ :=
      octagon_strict_core hc' (by linear_combination hCS) g1 g2 g3 g4
    refine ⟨m1, m2, -b1, -b2, hm1, hm2, by rwa [abs_neg], by rwa [abs_neg], ?_, ?_⟩
    · rw [hd1]; ring
    · rw [hd2]; ring

/-! ## 3. The common interior point -/

/-- The geometric core, in raw coordinates: four strict projection overlaps produce a point
`(m1, m2)` in the owner's frame and `(−n1, −n2)` in the other square's frame, all four
coordinates of absolute value `< 1/2`. -/
private theorem common_point {cw sw co so dx dy : ℝ}
    (hpw : cw ^ 2 + sw ^ 2 = 1) (hpo : co ^ 2 + so ^ 2 = 1)
    (b1 : |dx * cw + dy * sw| < 1 / 2 + (|cw * co + sw * so| + |cw * so - sw * co|) / 2)
    (b2 : |dx * -sw + dy * cw| < 1 / 2 + (|cw * co + sw * so| + |cw * so - sw * co|) / 2)
    (b3 : |dx * co + dy * so| < 1 / 2 + (|cw * co + sw * so| + |cw * so - sw * co|) / 2)
    (b4 : |dx * -so + dy * co| < 1 / 2 + (|cw * co + sw * so| + |cw * so - sw * co|) / 2) :
    ∃ m1 m2 n1 n2 : ℝ, |m1| < 1 / 2 ∧ |m2| < 1 / 2 ∧ |n1| < 1 / 2 ∧ |n2| < 1 / 2 ∧
      m1 * cw - m2 * sw - dx = -(n1 * co - n2 * so) ∧
      m1 * sw + m2 * cw - dy = -(n1 * so + n2 * co) := by
  have hCS : (cw * co + sw * so) ^ 2 + (cw * so - sw * co) ^ 2 = 1 := by
    have hp : (cw * co + sw * so) ^ 2 + (cw * so - sw * co) ^ 2
        = (cw ^ 2 + sw ^ 2) * (co ^ 2 + so ^ 2) := by ring
    rw [hp, hpw, hpo]; norm_num
  have h3 : |(cw * co + sw * so) * (dx * cw + dy * sw)
      + (cw * so - sw * co) * (dx * -sw + dy * cw)|
      < 1 / 2 + (|cw * co + sw * so| + |cw * so - sw * co|) / 2 := by
    rw [show (cw * co + sw * so) * (dx * cw + dy * sw)
        + (cw * so - sw * co) * (dx * -sw + dy * cw) = dx * co + dy * so from by
      linear_combination (dx * co + dy * so) * hpw]
    exact b3
  have h4 : |(-(cw * so - sw * co)) * (dx * cw + dy * sw)
      + (cw * co + sw * so) * (dx * -sw + dy * cw)|
      < 1 / 2 + (|cw * co + sw * so| + |cw * so - sw * co|) / 2 := by
    rw [show (-(cw * so - sw * co)) * (dx * cw + dy * sw)
        + (cw * co + sw * so) * (dx * -sw + dy * cw) = dx * -so + dy * co from by
      linear_combination (dy * co - dx * so) * hpw]
    exact b4
  obtain ⟨m1, m2, n1, n2, hm1, hm2, hn1, hn2, hd1, hd2⟩ :=
    octagon_strict hCS b1 b2 h3 h4
  refine ⟨m1, m2, n1, n2, hm1, hm2, hn1, hn2, ?_, ?_⟩
  · linear_combination (-cw) * hd1 + sw * hd2 + (dx - n1 * co + n2 * so) * hpw
  · linear_combination (-sw) * hd1 + (-cw) * hd2 + (dy - n1 * so - n2 * co) * hpw

/-- A point written in a square's own frame with both centred coordinates strictly inside
`(−1/2, 1/2)` is an INTERIOR point of the square (`Attain.mem_interior_iff_uv`). -/
private theorem mem_interior_of_coords (q : PSq) (a b : ℝ) (ha : |a| < 1 / 2)
    (hb : |b| < 1 / 2) :
    ((q.cx + a * cosT q.t - b * sinT q.t, q.cy + a * sinT q.t + b * cosT q.t) : RP)
      ∈ interior q.set := by
  have hp := cosT_sq_add_sinT_sq q.t
  rw [mem_interior_iff_uv]
  constructor
  · have e : rdot (((q.cx + a * cosT q.t - b * sinT q.t,
        q.cy + a * sinT q.t + b * cosT q.t) : RP).1 - q.cx,
        ((q.cx + a * cosT q.t - b * sinT q.t,
        q.cy + a * sinT q.t + b * cosT q.t) : RP).2 - q.cy) (edir q) = a := by
      simp only [rdot, edir]
      linear_combination a * hp
    rw [e]; exact ha
  · have e : rdot (((q.cx + a * cosT q.t - b * sinT q.t,
        q.cy + a * sinT q.t + b * cosT q.t) : RP).1 - q.cx,
        ((q.cx + a * cosT q.t - b * sinT q.t,
        q.cy + a * sinT q.t + b * cosT q.t) : RP).2 - q.cy) (perpV (edir q)) = b := by
      simp only [rdot, edir, perpV]
      linear_combination b * hp
    rw [e]; exact hb

/-! ## 4. Lemma SAT for interiors -/

/-- **Lemma SAT for INTERIORS, as a theorem** (`local_certificate.md` §1).  Exactly the
statement of `Local.lean`'s project axiom `sat_selection`, proved from `CaseSat.sat_squares`
(the closed-square form) by the explicit shrink of `octagon_strict_core` and
`Attain.mem_interior_iff_uv` (the interior of a parametrised square is the open `u/v` box). -/
theorem sat_selection_thm (qw qo : PSq)
    (h : Disjoint (interior qw.set) (interior qo.set)) :
    (∃ k : Bool, ∃ eps : ℝ, (eps = 1 ∨ eps = -1) ∧ 0 ≤ gsel qw qo k eps) ∨
    (∃ k : Bool, ∃ eps : ℝ, (eps = 1 ∨ eps = -1) ∧ 0 ≤ gsel qo qw k eps) := by
  by_contra hno
  push Not at hno
  obtain ⟨hnw, hnoo⟩ := hno
  have hax_f : ∀ q : PSq, axk q false = (cosT q.t, sinT q.t) := by intro q; simp [axk]
  have hax_t : ∀ q : PSq, axk q true = (-(sinT q.t), cosT q.t) := by intro q; simp [axk]
  have hwq : wrel qw qo
      = |cosT qw.t * cosT qo.t + sinT qw.t * sinT qo.t|
        + |cosT qw.t * sinT qo.t - sinT qw.t * cosT qo.t| := rfl
  have hwq' : wrel qo qw
      = |cosT qw.t * cosT qo.t + sinT qw.t * sinT qo.t|
        + |cosT qw.t * sinT qo.t - sinT qw.t * cosT qo.t| := by rw [wrel_comm, hwq]
  have hpw : cosT qw.t ^ 2 + sinT qw.t ^ 2 = 1 := cosT_sq_add_sinT_sq qw.t
  have hpo : cosT qo.t ^ 2 + sinT qo.t ^ 2 = 1 := cosT_sq_add_sinT_sq qo.t
  -- the eight strict gaps, folded into four two-sided bounds
  have g1p := hnw false 1 (Or.inl rfl)
  have g1m := hnw false (-1) (Or.inr rfl)
  have g2p := hnw true 1 (Or.inl rfl)
  have g2m := hnw true (-1) (Or.inr rfl)
  have g3p := hnoo false 1 (Or.inl rfl)
  have g3m := hnoo false (-1) (Or.inr rfl)
  have g4p := hnoo true 1 (Or.inl rfl)
  have g4m := hnoo true (-1) (Or.inr rfl)
  simp only [gsel, hax_f, hax_t, hwq, hwq'] at g1p g1m g2p g2m g3p g3m g4p g4m
  have b1 : |(qo.cx - qw.cx) * cosT qw.t + (qo.cy - qw.cy) * sinT qw.t|
      < 1 / 2 + (|cosT qw.t * cosT qo.t + sinT qw.t * sinT qo.t|
        + |cosT qw.t * sinT qo.t - sinT qw.t * cosT qo.t|) / 2 := by
    rw [abs_lt]; constructor <;> linarith
  have b2 : |(qo.cx - qw.cx) * -sinT qw.t + (qo.cy - qw.cy) * cosT qw.t|
      < 1 / 2 + (|cosT qw.t * cosT qo.t + sinT qw.t * sinT qo.t|
        + |cosT qw.t * sinT qo.t - sinT qw.t * cosT qo.t|) / 2 := by
    rw [abs_lt]; constructor <;> linarith
  have b3 : |(qo.cx - qw.cx) * cosT qo.t + (qo.cy - qw.cy) * sinT qo.t|
      < 1 / 2 + (|cosT qw.t * cosT qo.t + sinT qw.t * sinT qo.t|
        + |cosT qw.t * sinT qo.t - sinT qw.t * cosT qo.t|) / 2 := by
    rw [abs_lt]; constructor <;> linarith
  have b4 : |(qo.cx - qw.cx) * -sinT qo.t + (qo.cy - qw.cy) * cosT qo.t|
      < 1 / 2 + (|cosT qw.t * cosT qo.t + sinT qw.t * sinT qo.t|
        + |cosT qw.t * sinT qo.t - sinT qw.t * cosT qo.t|) / 2 := by
    rw [abs_lt]; constructor <;> linarith
  obtain ⟨m1, m2, n1, n2, hm1, hm2, hn1, hn2, G1, G2⟩ :=
    common_point hpw hpo b1 b2 b3 b4
  -- the common interior point, written in each square's own frame
  have hin1 : ((qw.cx + m1 * cosT qw.t - m2 * sinT qw.t,
      qw.cy + m1 * sinT qw.t + m2 * cosT qw.t) : RP) ∈ interior qw.set :=
    mem_interior_of_coords qw m1 m2 hm1 hm2
  have hpt : ((qw.cx + m1 * cosT qw.t - m2 * sinT qw.t,
      qw.cy + m1 * sinT qw.t + m2 * cosT qw.t) : RP)
      = (qo.cx + (-n1) * cosT qo.t - (-n2) * sinT qo.t,
         qo.cy + (-n1) * sinT qo.t + (-n2) * cosT qo.t) := by
    simp only [Prod.mk.injEq]
    exact ⟨by linear_combination G1, by linear_combination G2⟩
  have hin2 : ((qw.cx + m1 * cosT qw.t - m2 * sinT qw.t,
      qw.cy + m1 * sinT qw.t + m2 * cosT qw.t) : RP) ∈ interior qo.set := by
    rw [hpt]
    exact mem_interior_of_coords qo (-n1) (-n2) (by rwa [abs_neg]) (by rwa [abs_neg])
  exact Set.disjoint_left.mp h hin1 hin2

/-! ## 5. The consumer, axiom-free -/

/-- **Lemma COVER, one pair** — `Local.lean`'s `cover_pair` with the axiom replaced by
`sat_selection_thm`.  Same statement, standard axioms only. -/
theorem cover_pair' (qw qo : PSq) (h : Disjoint (interior qw.set) (interior qo.set))
    (hexc : ∀ (k : Bool) (eps : ℝ), (eps = 1 ∨ eps = -1) → gsel qw qo k eps < 0) :
    ∃ k : Bool, ∃ eps : ℝ, (eps = 1 ∨ eps = -1) ∧ 0 ≤ gsel qo qw k eps := by
  rcases sat_selection_thm qw qo h with ⟨k, e, he, hg⟩ | h2
  · exact absurd hg (not_le.mpr (hexc k e he))
  · exact h2

end

end LocalCert
end S11
end PackingCert
