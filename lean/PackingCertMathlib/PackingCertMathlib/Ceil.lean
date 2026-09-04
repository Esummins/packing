import PackingCertMathlib.Crowd

/-!
# Theorem CEIL: two disjoint unit squares in a quadrant (A93 T3, depgraph K0.CEIL)

`docs/proofs/k0_blocked_side.md` §2.1.  For two closed unit squares `A`, `B` in the quadrant
(here: in a container `[0,s]²`, any `s`) with disjoint interiors,

    `max (μ_BL A) (μ_BL B) ≥ 1/√2`,   `μ_BL(Q) = min_{p ∈ Q} max(p_x, p_y)`  (`Crowd.muC`),

so at every corner of every packing `min(d₁, d₂) ≤ 1 − 1/√2 = 0.2929` (Corollary CEIL-1): a
substantive crowd at depth `> 0.2929` is impossible, and the certified frontier value
`0.292893` of `d2front87` is the theoretical maximum.

Proof, as in the prose: a separating line `{n·p = u}` (Hahn–Banach on the two open convex
interiors, `geometric_hahn_banach_open`, extended to the closed squares through the interior
combos `mem_interior_combo`), normalised to a unit normal.  If `n` has both components `≥ 0`
(or both `≤ 0`) the line cuts off the corner and one square has `μ ≥ 0.853`
(`ceil_corner_cut`); otherwise, say `n_x > 0 > n_y`, `B` lies in the wedge
`{y ≥ 0, n·p ≥ u}` and `A` in the mirrored wedge `{x ≥ 0, n·p ≤ u}`, and the **Wedge Lemma**
(`wedge_x`, `wedge_y`: a unit square in `{y ≥ 0} ∩ {n·p ≥ u}` has `min x ≥ (u + n_y²)/n_x`)
gives `L_A, L_B` with `n_x·L_B + (−n_y)·L_A = 1`, hence `max ≥ 1/(n_x − n_y) ≥ 1/√2`.  The
Wedge Lemma's two-branch/concavity step is the one algebraic inequality
`a² ≤ max(aC, a(C+S) − bC)` for `a² + b² = 1 = C² + S²` (`wedge_core`), proved by the exact
factorisation `(aS)² − (a² − (a−b)C)² = (a − C)·((a² + (a−b)²)C + a·b²)`.

Axioms: `propext, Classical.choice, Quot.sound`.
-/

namespace PackingCert
namespace S11

noncomputable section

open Set

/-! ## Convexity and interior combos of a square -/

/-- The combination `(1−θ)p + θ·centre`, `θ ∈ (0, 1]`, of a point of the square with its centre
lies in the interior (the `u/v` coordinates scale by `1 − θ < 1`). -/
theorem mem_interior_combo (q : PSq) {p : RP} (hp : p ∈ q.set) {θ : ℝ} (h0 : 0 < θ) (h1 : θ ≤ 1) :
    ((1 - θ) * p.1 + θ * q.cx, (1 - θ) * p.2 + θ * q.cy) ∈ interior q.set := by
  rw [mem_set_iff_uv] at hp
  obtain ⟨hu, hv⟩ := hp
  apply strict_uv_mem_interior
  · have e : rdot ((1 - θ) * p.1 + θ * q.cx - q.cx, (1 - θ) * p.2 + θ * q.cy - q.cy) (edir q)
        = (1 - θ) * rdot (p.1 - q.cx, p.2 - q.cy) (edir q) := by
      simp only [rdot]; ring
    rw [e, abs_mul, abs_of_nonneg (by linarith)]
    nlinarith [mul_le_mul_of_nonneg_left hu (by linarith : (0 : ℝ) ≤ 1 - θ)]
  · have e : rdot ((1 - θ) * p.1 + θ * q.cx - q.cx, (1 - θ) * p.2 + θ * q.cy - q.cy) (perpV (edir q))
        = (1 - θ) * rdot (p.1 - q.cx, p.2 - q.cy) (perpV (edir q)) := by
      simp only [rdot, perpV]; ring
    rw [e, abs_mul, abs_of_nonneg (by linarith)]
    nlinarith [mul_le_mul_of_nonneg_left hv (by linarith : (0 : ℝ) ≤ 1 - θ)]

theorem centre_mem_interior (q : PSq) : centre q ∈ interior q.set :=
  mem_interior_of_sqdist_lt q (by simp [sqdist, centre])

theorem psq_convex (q : PSq) : Convex ℝ q.set := by
  rw [convex_iff_forall_pos]
  intro x hx y hy a b ha hb hab
  have h := psq_set_convex q hx hy (θ := b) hb.le (by linarith)
  have hab' : a = 1 - b := by linarith
  subst hab'
  convert h using 1
  ext <;> simp

/-- A continuous linear functional on the plane is `p ↦ p.1·f(1,0) + p.2·f(0,1)`. -/
theorem clm_eval (f : ℝ × ℝ →L[ℝ] ℝ) (p : ℝ × ℝ) : f p = p.1 * f (1, 0) + p.2 * f (0, 1) := by
  have : p = p.1 • ((1 : ℝ), (0 : ℝ)) + p.2 • ((0 : ℝ), (1 : ℝ)) := by
    ext <;> simp
  conv_lhs => rw [this]
  rw [map_add, map_smul, map_smul]
  simp [smul_eq_mul]

/-! ## The separating line -/

/-- **Separation** of two interior-disjoint squares: a unit normal `n` and a level `u` with
`n·p ≤ u` on `A` and `n·p ≥ u` on `B`. -/
theorem exists_sep_line {qA qB : PSq} (hd : Disjoint (interior qA.set) (interior qB.set)) :
    ∃ n : RP, ∃ u : ℝ, n.1 ^ 2 + n.2 ^ 2 = 1 ∧
      (∀ p ∈ qA.set, n.1 * p.1 + n.2 * p.2 ≤ u) ∧ (∀ p ∈ qB.set, u ≤ n.1 * p.1 + n.2 * p.2) := by
  obtain ⟨f, u, hfA, hfB⟩ := geometric_hahn_banach_open (psq_convex qA).interior isOpen_interior
    (psq_convex qB).interior hd
  -- weak inequalities on the closed squares, through the interior combos
  have hcombo : ∀ (q : PSq) (p : RP) (θ : ℝ),
      f ((1 - θ) * p.1 + θ * q.cx, (1 - θ) * p.2 + θ * q.cy) = (1 - θ) * f p + θ * f (centre q) := by
    intro q p θ
    rw [clm_eval f, clm_eval f p, clm_eval f (centre q)]
    simp only [centre]
    ring
  have hA : ∀ p ∈ qA.set, f p ≤ u := by
    intro p hp
    by_contra hgt
    push Not at hgt
    have hc := hfA _ (centre_mem_interior qA)
    have hden : 0 < f p - f (centre qA) := by linarith
    have hne := hden.ne'
    obtain ⟨θ, hθ0, hθ1, hθu⟩ : ∃ θ : ℝ, 0 < θ ∧ θ ≤ 1 ∧ (1 - θ) * f p + θ * f (centre qA) = u :=
      ⟨(f p - u) / (f p - f (centre qA)), by positivity, by rw [div_le_one hden]; linarith,
        by field_simp; ring⟩
    have hmem := hfA _ (mem_interior_combo qA hp hθ0 hθ1)
    rw [hcombo, hθu] at hmem
    exact lt_irrefl _ hmem
  have hB : ∀ p ∈ qB.set, u ≤ f p := by
    intro p hp
    by_contra hlt
    push Not at hlt
    have hc := hfB _ (centre_mem_interior qB)
    -- a small `θ` keeps the combo below `u`
    have hD : 0 < f (centre qB) - f p := by linarith
    obtain ⟨θ, hθ0, hθ1, hθu⟩ : ∃ θ : ℝ, 0 < θ ∧ θ ≤ 1 ∧
        θ * (f (centre qB) - f p) ≤ (u - f p) / 2 :=
      ⟨min 1 ((u - f p) / (2 * (f (centre qB) - f p))), lt_min one_pos (by positivity),
        min_le_left _ _, by
          have h := min_le_right 1 ((u - f p) / (2 * (f (centre qB) - f p)))
          calc min 1 ((u - f p) / (2 * (f (centre qB) - f p))) * (f (centre qB) - f p)
              ≤ (u - f p) / (2 * (f (centre qB) - f p)) * (f (centre qB) - f p) :=
                mul_le_mul_of_nonneg_right h hD.le
            _ = (u - f p) / 2 := by field_simp⟩
    have hmem := hfB _ (mem_interior_combo qB hp hθ0 hθ1)
    rw [hcombo] at hmem
    nlinarith
  -- the functional is not zero
  set a := f (1, 0) with ha
  set b := f (0, 1) with hb
  have hne : 0 < a ^ 2 + b ^ 2 := by
    by_contra h0
    push Not at h0
    have ha0 : a = 0 := by nlinarith [sq_nonneg a, sq_nonneg b]
    have hb0 : b = 0 := by nlinarith [sq_nonneg a, sq_nonneg b]
    have h1 := hfA _ (centre_mem_interior qA)
    have h2 := hfB _ (centre_mem_interior qB)
    rw [clm_eval, ← ha, ← hb, ha0, hb0] at h1 h2
    linarith
  set N := Real.sqrt (a ^ 2 + b ^ 2) with hN
  have hNpos : 0 < N := Real.sqrt_pos.mpr hne
  have hN2 : N ^ 2 = a ^ 2 + b ^ 2 := Real.sq_sqrt hne.le
  refine ⟨(a / N, b / N), u / N, ?_, ?_, ?_⟩
  · field_simp
    linarith
  · intro p hp
    have := hA p hp
    rw [clm_eval, ← ha, ← hb] at this
    rw [div_mul_eq_mul_div, div_mul_eq_mul_div, ← add_div, div_le_div_iff_of_pos_right hNpos]
    linarith
  · intro p hp
    have := hB p hp
    rw [clm_eval, ← ha, ← hb] at this
    rw [div_mul_eq_mul_div, div_mul_eq_mul_div, ← add_div, div_le_div_iff_of_pos_right hNpos]
    linarith

/-! ## The Wedge Lemma -/

/-- The algebraic core of the Wedge Lemma (the two-branch / concavity step of the prose):
for `a, b > 0`, `a² + b² = 1`, `C, S ≥ 0`, `C² + S² = 1`:  `a² ≤ max(aC, a(C+S) − bC)`. -/
theorem wedge_core {a b C S : ℝ} (ha : 0 < a) (hb : 0 < b) (hab : a ^ 2 + b ^ 2 = 1)
    (hC : 0 ≤ C) (hS : 0 ≤ S) (hCS : C ^ 2 + S ^ 2 = 1) :
    a ^ 2 ≤ a * C ∨ a ^ 2 ≤ a * (C + S) - b * C := by
  rcases le_or_gt a C with haC | hCa
  · left
    nlinarith
  · right
    -- `a S ≥ a² − (a − b) C` by the exact factorisation
    have hR : a ^ 2 - (a - b) * C ≤ a * S := by
      rcases le_or_gt (a ^ 2 - (a - b) * C) 0 with h | h
      · nlinarith [mul_nonneg ha.le hS]
      · have hid : (a * S) ^ 2 - (a ^ 2 - (a - b) * C) ^ 2
            = (a - C) * ((a ^ 2 + (a - b) ^ 2) * C + a * b ^ 2) := by
          linear_combination (a ^ 2) * hCS - (a ^ 2) * hab
        have hnn : 0 ≤ (a - C) * ((a ^ 2 + (a - b) ^ 2) * C + a * b ^ 2) :=
          mul_nonneg (by linarith) (by positivity)
        have hsq : (a ^ 2 - (a - b) * C) ^ 2 ≤ (a * S) ^ 2 := by linarith
        exact (abs_le_of_sq_le_sq' hsq (mul_nonneg ha.le hS)).2
    nlinarith

/-- **Wedge Lemma, `x`-form.**  A unit square in `{y ≥ 0} ∩ {n_x x + n_y y ≥ u}` with
`n_x > 0 > n_y`, `|n| = 1`, has every point at `x ≥ (u + n_y²)/n_x` (i.e. `n_x·x ≥ u + n_y²`). -/
theorem wedge_x {q : PSq} (ht : q.t ∈ Icc (0 : ℝ) 1) {nx ny u : ℝ} (hnx : 0 < nx) (hny : ny < 0)
    (hn : nx ^ 2 + ny ^ 2 = 1) (hW : ∀ p ∈ q.set, 0 ≤ p.2 ∧ u ≤ nx * p.1 + ny * p.2) :
    ∀ p ∈ q.set, u + ny ^ 2 ≤ nx * p.1 := by
  have hC := cosT_nonneg ht.1 ht.2
  have hS := sinT_nonneg ht.1
  have hCS := cosT_sq_add_sinT_sq q.t
  -- the three vertices: `p0`, `p0 + e⊥` (minimal `x`), `p0 + e + e⊥`
  have hv0 : baseCorner q ∈ q.set := ⟨0, 0, le_rfl, zero_le_one, le_rfl, zero_le_one, by
    simp [aff]⟩
  have hv1 : aff (baseCorner q) (edir q) 0 1 ∈ q.set :=
    ⟨0, 1, le_rfl, zero_le_one, zero_le_one, le_rfl, rfl⟩
  have hv3 : aff (baseCorner q) (edir q) 1 1 ∈ q.set :=
    ⟨1, 1, zero_le_one, le_rfl, zero_le_one, le_rfl, rfl⟩
  obtain ⟨h0y, -⟩ := hW _ hv0
  obtain ⟨-, h1n⟩ := hW _ hv1
  obtain ⟨-, h3n⟩ := hW _ hv3
  simp only [aff, edir, zero_mul, one_mul, add_zero] at h1n h3n
  set m := -ny with hm
  have hm0 : 0 < m := by linarith
  have hnm : nx ^ 2 + m ^ 2 = 1 := by rw [hm]; linarith
  have key := wedge_core hm0 hnx (by linarith) hC hS hCS
  intro p hp
  obtain ⟨a, b, ha0, ha1, hb0, hb1, rfl⟩ := hp
  simp only [aff, edir]
  -- `x ≥ x* = p0.1 − S`
  have hx : (baseCorner q).1 - sinT q.t ≤ (baseCorner q).1 + a * cosT q.t - b * sinT q.t := by
    nlinarith [mul_nonneg ha0 hC, mul_le_mul_of_nonneg_right hb1 hS]
  have hy : cosT q.t ≤ (baseCorner q).2 + cosT q.t := by linarith
  rcases key with k | k
  · nlinarith [mul_le_mul_of_nonneg_left hy hm0.le]
  · nlinarith [mul_le_mul_of_nonneg_left hy hm0.le]

/-- **Wedge Lemma, `y`-form** (the mirror): a unit square in `{x ≥ 0} ∩ {n_x x + n_y y ≤ u}` with
`n_x > 0 > n_y`, `|n| = 1`, has every point at `y ≥ (n_x² − u)/(−n_y)` (i.e.
`(−n_y)·y ≥ n_x² − u`). -/
theorem wedge_y {q : PSq} (ht : q.t ∈ Icc (0 : ℝ) 1) {nx ny u : ℝ} (hnx : 0 < nx) (hny : ny < 0)
    (hn : nx ^ 2 + ny ^ 2 = 1) (hW : ∀ p ∈ q.set, 0 ≤ p.1 ∧ nx * p.1 + ny * p.2 ≤ u) :
    ∀ p ∈ q.set, nx ^ 2 - u ≤ (-ny) * p.2 := by
  have hC := cosT_nonneg ht.1 ht.2
  have hS := sinT_nonneg ht.1
  have hCS := cosT_sq_add_sinT_sq q.t
  -- the three vertices: `p0` (minimal `y`), `p0 + e`, `p0 + e⊥` (minimal `x`)
  have hv0 : baseCorner q ∈ q.set := ⟨0, 0, le_rfl, zero_le_one, le_rfl, zero_le_one, by
    simp [aff]⟩
  have hv1 : aff (baseCorner q) (edir q) 0 1 ∈ q.set :=
    ⟨0, 1, le_rfl, zero_le_one, zero_le_one, le_rfl, rfl⟩
  have hv2 : aff (baseCorner q) (edir q) 1 0 ∈ q.set :=
    ⟨1, 0, zero_le_one, le_rfl, le_rfl, zero_le_one, rfl⟩
  obtain ⟨-, h0n⟩ := hW _ hv0
  obtain ⟨h1x, -⟩ := hW _ hv1
  obtain ⟨-, h2n⟩ := hW _ hv2
  simp only [aff, edir, zero_mul, one_mul, add_zero, sub_zero] at h1x h2n
  set m := -ny with hm
  have hm0 : 0 < m := by linarith
  have hnm : nx ^ 2 + m ^ 2 = 1 := by rw [hm]; linarith
  have key := wedge_core hnx hm0 hnm hS hC (by linarith)
  intro p hp
  obtain ⟨a, b, ha0, ha1, hb0, hb1, rfl⟩ := hp
  simp only [aff, edir]
  -- `y ≥ y* = p0.2`
  have hy : (baseCorner q).2 ≤ (baseCorner q).2 + a * sinT q.t + b * cosT q.t := by
    nlinarith [mul_nonneg ha0 hS, mul_nonneg hb0 hC]
  have hx : sinT q.t ≤ (baseCorner q).1 := by linarith
  rcases key with k | k
  · nlinarith [mul_le_mul_of_nonneg_left hx hnx.le]
  · nlinarith [mul_le_mul_of_nonneg_left hx hnx.le]

/-! ## Theorem CEIL -/

theorem gcf_zero (s : ℝ) (p : RP) : gcf s 0 p = max p.1 p.2 := by
  simp [gcf, cframe, cornerR, cornerT]

theorem le_muC_of_forall {s : ℝ} {c : Fin 4} {q : PSq} {L : ℝ}
    (h : ∀ p ∈ q.set, L ≤ gcf s c p) : L ≤ muC s c q := by
  obtain ⟨⟨p, hp, hpv⟩, -⟩ := muC_spec s c q
  rw [← hpv]
  exact h p hp

theorem centre_ge_half {s : ℝ} {q : PSq} (ht : q.t ∈ Icc (0 : ℝ) 1) (hq : q.set ⊆ container s) :
    1 / 2 ≤ q.cx ∧ 1 / 2 ≤ q.cy := by
  obtain ⟨h1, -, h3, -⟩ := (set_subset_container_iff ht.1 ht.2 s).mp hq
  have := wT_ge_one ht.1 ht.2
  constructor <;> linarith

/-- The corner-cut case: `n` with both components `≥ 0`, `A ⊆ {n·p ≤ u}`, `B ⊆ {n·p ≥ u}` —
then `μ(B) ≥ 0.85 > 1/√2`: the far point `c_A + n/2` of `A` puts `u ≥ n·c_A + 1/2 ≥
(n_x + n_y)/2 + 1/2`, and `n·p ≤ (n_x + n_y)·max(p_x, p_y)` on `B`. -/
theorem ceil_corner_cut {s : ℝ} {qA qB : PSq} (htA : qA.t ∈ Icc (0 : ℝ) 1)
    (hA : qA.set ⊆ container s) {nx ny u : ℝ} (hnx : 0 ≤ nx) (hny : 0 ≤ ny)
    (hn : nx ^ 2 + ny ^ 2 = 1) (hsepA : ∀ p ∈ qA.set, nx * p.1 + ny * p.2 ≤ u)
    (hsepB : ∀ p ∈ qB.set, u ≤ nx * p.1 + ny * p.2) :
    71 / 100 ≤ muC s 0 qB := by
  obtain ⟨hcx, hcy⟩ := centre_ge_half htA hA
  have hfar : (qA.cx + nx / 2, qA.cy + ny / 2) ∈ qA.set := by
    apply mem_set_of_sqdist_le
    simp only [sqdist, centre]
    nlinarith
  have hu := hsepA _ hfar
  have hsum : nx + ny ≤ 14143 / 10000 := by
    have h2 : (nx + ny) ^ 2 ≤ (14143 / 10000 : ℝ) ^ 2 := by nlinarith [sq_nonneg (nx - ny)]
    exact (pow_le_pow_iff_left₀ (by linarith) (by norm_num) two_ne_zero).mp h2
  have hpos : 0 < nx + ny := by nlinarith
  refine le_muC_of_forall fun p hp => ?_
  rw [gcf_zero]
  have hb := hsepB p hp
  have h1 : nx * p.1 ≤ nx * max p.1 p.2 := mul_le_mul_of_nonneg_left (le_max_left _ _) hnx
  have h2 : ny * p.2 ≤ ny * max p.1 p.2 := mul_le_mul_of_nonneg_left (le_max_right _ _) hny
  by_contra hlt
  push Not at hlt
  nlinarith [mul_lt_mul_of_pos_left hlt hpos]

/-- The main case with a separating line `n_x > 0 > n_y`: the two wedge bounds `L_A`, `L_B`
satisfy `n_x·L_B + (−n_y)·L_A = 1`, so `max(L_A, L_B) ≥ 1/(n_x − n_y) ≥ 1/√2`. -/
theorem ceil_wedge_case {s : ℝ} {qA qB : PSq} (htA : qA.t ∈ Icc (0 : ℝ) 1) (htB : qB.t ∈ Icc (0 : ℝ) 1)
    (hA : qA.set ⊆ container s) (hB : qB.set ⊆ container s) {nx ny u : ℝ} (hnx : 0 < nx)
    (hny : ny < 0) (hn : nx ^ 2 + ny ^ 2 = 1) (hsepA : ∀ p ∈ qA.set, nx * p.1 + ny * p.2 ≤ u)
    (hsepB : ∀ p ∈ qB.set, u ≤ nx * p.1 + ny * p.2) :
    1 / Real.sqrt 2 ≤ max (muC s 0 qA) (muC s 0 qB) := by
  have hwB := wedge_x htB hnx hny hn fun p hp => ⟨(cframe_of_mem_container 0 (hB hp)).2.2.1, hsepB p hp⟩
  have hwA := wedge_y htA hnx hny hn fun p hp => ⟨(cframe_of_mem_container 0 (hA hp)).1, hsepA p hp⟩
  set m := -ny with hm
  have hm0 : 0 < m := by linarith
  -- `μ_B ≥ L_B := (u + n_y²)/n_x`, `μ_A ≥ L_A := (n_x² − u)/m`
  have hLB : (u + ny ^ 2) / nx ≤ muC s 0 qB := by
    refine le_muC_of_forall fun p hp => ?_
    rw [gcf_zero, div_le_iff₀ hnx]
    have := hwB p hp
    nlinarith [mul_le_mul_of_nonneg_left (le_max_left p.1 p.2) hnx.le]
  have hLA : (nx ^ 2 - u) / m ≤ muC s 0 qA := by
    refine le_muC_of_forall fun p hp => ?_
    rw [gcf_zero, div_le_iff₀ hm0]
    have := hwA p hp
    nlinarith [mul_le_mul_of_nonneg_left (le_max_right p.1 p.2) hm0.le]
  -- `n_x·L_B + m·L_A = 1`, so `max(L_A, L_B) ≥ 1/(n_x + m)`
  have hsum : nx * ((u + ny ^ 2) / nx) + m * ((nx ^ 2 - u) / m) = 1 := by
    field_simp
    linarith [hn]
  have hmax : 1 / (nx + m) ≤ max (muC s 0 qA) (muC s 0 qB) := by
    rw [div_le_iff₀ (by linarith)]
    have h1 := le_trans hLA (le_max_left (muC s 0 qA) (muC s 0 qB))
    have h2 := le_trans hLB (le_max_right (muC s 0 qA) (muC s 0 qB))
    nlinarith [mul_le_mul_of_nonneg_left h1 hm0.le, mul_le_mul_of_nonneg_left h2 hnx.le]
  -- `n_x + m ≤ √2`
  have hle : nx + m ≤ Real.sqrt 2 := by
    rw [Real.le_sqrt (by linarith) (by norm_num)]
    nlinarith [sq_nonneg (nx - m)]
  exact le_trans (one_div_le_one_div_of_le (by linarith) hle) hmax

/-- **Theorem CEIL** (`k0_blocked_side.md` §2.1): two closed unit squares in `[0,s]²` with
disjoint interiors satisfy `max(μ_BL(A), μ_BL(B)) ≥ 1/√2`. -/
theorem ceil {s : ℝ} {qA qB : PSq} (htA : qA.t ∈ Icc (0 : ℝ) 1) (htB : qB.t ∈ Icc (0 : ℝ) 1)
    (hA : qA.set ⊆ container s) (hB : qB.set ⊆ container s)
    (hd : Disjoint (interior qA.set) (interior qB.set)) :
    1 / Real.sqrt 2 ≤ max (muC s 0 qA) (muC s 0 qB) := by
  obtain ⟨n, u, hn, hsepA, hsepB⟩ := exists_sep_line hd
  have h071 : 1 / Real.sqrt 2 ≤ 71 / 100 := by
    have : (100 / 71 : ℝ) ≤ Real.sqrt 2 := by
      rw [Real.le_sqrt (by norm_num) (by norm_num)]; norm_num
    have := one_div_le_one_div_of_le (by norm_num) this
    linarith [show (1 : ℝ) / (100 / 71) = 71 / 100 by norm_num]
  rcases le_or_gt 0 n.1 with hx | hx <;> rcases le_or_gt 0 n.2 with hy | hy
  · -- both `≥ 0`: the corner cut, `B` far
    exact le_trans h071 (le_trans (ceil_corner_cut htA hA hx hy hn hsepA hsepB) (le_max_right _ _))
  · -- `n.1 ≥ 0 > n.2`: the wedge case when `n.1 > 0`, else the corner cut with `−n`
    rcases lt_or_eq_of_le hx with hx' | hx'
    · exact ceil_wedge_case htA htB hA hB hx' hy hn hsepA hsepB
    · have hsepA' : ∀ p ∈ qB.set, (-n.1) * p.1 + (-n.2) * p.2 ≤ -u := fun p hp => by
        linarith [hsepB p hp]
      have hsepB' : ∀ p ∈ qA.set, -u ≤ (-n.1) * p.1 + (-n.2) * p.2 := fun p hp => by
        linarith [hsepA p hp]
      exact le_trans h071 (le_trans (ceil_corner_cut htB hB (by linarith) (by linarith)
        (by nlinarith) hsepA' hsepB') (le_max_left _ _))
  · -- `n.1 < 0 ≤ n.2`: swap the roles (`−n`), then the wedge case or the corner cut
    have hsepA' : ∀ p ∈ qB.set, (-n.1) * p.1 + (-n.2) * p.2 ≤ -u := fun p hp => by
      linarith [hsepB p hp]
    have hsepB' : ∀ p ∈ qA.set, -u ≤ (-n.1) * p.1 + (-n.2) * p.2 := fun p hp => by
      linarith [hsepA p hp]
    rcases lt_or_eq_of_le hy with hy' | hy'
    · rw [max_comm]
      exact ceil_wedge_case htB htA hB hA (by linarith) (by linarith) (by nlinarith) hsepA' hsepB'
    · exact le_trans h071 (le_trans (ceil_corner_cut htB hB (by linarith) (by linarith)
        (by nlinarith) hsepA' hsepB') (le_max_left _ _))
  · -- both `< 0`: the corner cut with `−n`, `A` far
    have hsepA' : ∀ p ∈ qB.set, (-n.1) * p.1 + (-n.2) * p.2 ≤ -u := fun p hp => by
      linarith [hsepB p hp]
    have hsepB' : ∀ p ∈ qA.set, -u ≤ (-n.1) * p.1 + (-n.2) * p.2 := fun p hp => by
      linarith [hsepA p hp]
    exact le_trans h071 (le_trans (ceil_corner_cut htB hB (by linarith) (by linarith)
      (by nlinarith) hsepA' hsepB') (le_max_left _ _))

/-- **Corollary CEIL-1**: at every corner of every packing, the two deepest intruders cannot
both be at depth `> 1 − 1/√2 = 0.2929`: for two distinct squares `i ≠ j` of a packing at
side `s`, `max(μ_BL(z i), μ_BL(z j)) ≥ 1/√2` (and by D4 the same at every corner). -/
theorem ceil_packing {s : ℝ} {z : Cfg} (hz : CfgPacking s z) {i j : Fin 11} (hij : i ≠ j) :
    1 / Real.sqrt 2 ≤ max (muC s 0 (z i)) (muC s 0 (z j)) :=
  ceil (hz.1 i) (hz.1 j) (hz.2.contained i) (hz.2.contained j) (hz.2.interiorDisjoint i j hij)

end

end S11
end PackingCert
