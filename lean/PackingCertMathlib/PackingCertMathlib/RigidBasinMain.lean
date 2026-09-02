import PackingCertMathlib.RigidBasin

/-!
# `a36_basin`: the basin theorem (A79, rung (c))
-/

namespace PackingCert.Rigid

open PackingCert PackingCert.S11 Set Finset

section

variable {c : A22Cert} {a : A36Cert}

theorem stats_e0 (c : A22Cert) (a : A36Cert) : (a36Stats c a).e0 = eps0 c a (radBox c.z0 c.r0) := rfl
theorem stats_ew (c : A22Cert) (a : A36Cert) : (a36Stats c a).ew = epsW c a (radBox c.z0 c.r0) := rfl
theorem stats_hb (c : A22Cert) (a : A36Cert) :
    (a36Stats c a).hb = hbar c a (radBox c.z0 (a.h + c.r0)) := rfl
theorem stats_beta (c : A22Cert) (a : A36Cert) :
    (a36Stats c a).beta = betaA36 c a (radBox c.z0 (a.h + c.r0)) := rfl
theorem stats_kap (c : A22Cert) (a : A36Cert) : (a36Stats c a).kap = kappa c := rfl
theorem stats_keff (c : A22Cert) (a : A36Cert) : (a36Stats c a).keff = kappaEff c a := rfl
theorem stats_gm (c : A22Cert) (a : A36Cert) : (a36Stats c a).gm = gmax c a (radBox c.z0 c.r0) := rfl

theorem pinsOK_size (h : pinsOK c a = true) (hS : c.S.size = NV) : a.P.size = NV := by
  simp only [pinsOK, beq_iff_eq] at h
  rw [h]; simp [hS]

theorem hbar_nonneg (c : A22Cert) (a : A36Cert) (bx : Box) : (0 : ℚ) ≤ hbar c a bx := by
  rw [hbar_eq]
  exact div_nonneg (Finset.sum_nonneg fun i _ => Finset.sum_nonneg fun j _ => mag_nonneg _) (by norm_num)

theorem kappaEff_nonneg (c : A22Cert) (a : A36Cert) : (0 : ℚ) ≤ kappaEff c a := by
  unfold kappaEff
  rw [rng_eq]
  exact le_trans le_rfl (foldl_rmax_ge _ _ _)

set_option maxHeartbeats 2000000 in
-- one long assembly proof (Taylor + pinning + handover); split would only add plumbing
/-- **The basin theorem (universal certificate).** -/
theorem a36_basin (hc : checkA22 c = true) (ha : checkA36 c a = true) (hu : a.universal = true)
    {z : Vec} (hz : InBoxZ (zhatV c hc) a.h z) (hf : Feas z) :
    sZ (zhatV c hc) ≤ sZ z ∧ (sZ z = sZ (zhatV c hc) → z = zhatV c hc) := by
  obtain ⟨hh, hr, hpins, ho, hpin, hlv, hrange, hang, -⟩ := checkA36_parts ha
  have hlv' := hlv hu
  obtain ⟨hsh, -, -, -, -, -⟩ := checkA22_parts hc
  obtain ⟨hz0, hS, hr0, hr0N, -⟩ := shapeOK_parts hsh
  have hP : a.P.size = NV := pinsOK_size hpins hS
  have hpos : pinsPositive a = true := by
    simp only [omegaOK, Bool.and_eq_true] at ho
    exact ho.1.2
  have hltP : ∀ k ∈ a.P, k < NEXT3 := by
    simp only [pinsRangeOK, Bool.and_eq_true, decide_eq_true_eq, Array.all_eq_true_iff_forall_mem] at hrange
    exact hrange.1
  -- boxes
  set zh := zhatV c hc with hzh
  set hb : ℚ := a.h + c.r0 with hhb
  have hzA : MemBox (boxArr c hb) z := memBox_of_inBoxR hz0 (inBoxR_of_inBoxZ hc hz)
  have hzhA : MemBox (boxArr c hb) zh :=
    memBox_of_inBoxR hz0 (inBoxR_mono (by linarith) (zhatV_inBoxR hc))
  have hsm : SmallTilt z := smallTilt_of_anglesSmall (by rw [← radBox_eq]; exact hang) hzA
  have hsmh : SmallTilt zh := zhatV_smallTilt hc
  -- the difference vector and its norm
  set d : Vec := fun k => z k - zh k with hd
  set x : ℝ := dist d 0 with hx
  have hx0 : 0 ≤ x := dist_nonneg
  have hxh : x ≤ (a.h : ℝ) := by
    rw [hx, dist_pi_le_iff (by exact_mod_cast hh.le)]
    intro k
    rw [Real.dist_eq, Pi.zero_apply, sub_zero]
    exact hz k
  have hdk : ∀ k, |d k| ≤ x := fun k => by
    have := dist_le_pi_dist d 0 k
    rw [Real.dist_eq, Pi.zero_apply, sub_zero] at this
    exact this
  -- W ≥ 0 at z
  have hW0 : 0 ≤ Wfun c a z := W_nonneg hr hu ho hlv' hzA hsm hf
  -- the constants
  set e0 : ℝ := ((eps0 c a (radBox c.z0 c.r0) : ℚ) : ℝ) with he0
  set ew : ℝ := ((epsW c a (radBox c.z0 c.r0) : ℚ) : ℝ) with hew
  set hbR : ℝ := ((hbar c a (radBox c.z0 hb) : ℚ) : ℝ) with hhbR
  set beta : ℝ := ((betaA36 c a (radBox c.z0 hb) : ℚ) : ℝ) with hbeta
  set kap : ℝ := ((kappa c : ℚ) : ℝ) with hkap
  set keff : ℝ := ((kappaEff c a : ℚ) : ℝ) with hkeff
  set gm : ℝ := ((gmax c a (radBox c.z0 c.r0) : ℚ) : ℝ) with hgm
  set xs : ℝ := (((a36Stats c a).xstar : ℚ) : ℝ) with hxs
  -- the pinning checks, cast to ℝ
  simp only [pinningOK, Bool.and_eq_true, decide_eq_true_eq] at hpin
  simp only [stats_e0, stats_ew, stats_hb, stats_beta, stats_kap, stats_keff, stats_gm] at hpin
  obtain ⟨⟨⟨⟨hb1, hψh⟩, hxs0⟩, hψxs⟩, hxsN⟩ := hpin
  have hb1' : beta < 1 := by rw [hbeta]; exact_mod_cast hb1
  have hxs0' : 0 ≤ xs := by rw [hxs]; exact_mod_cast hxs0
  have hpsi : ∀ q : ℚ, ((psi (kappaEff c a) (eps0 c a (radBox c.z0 c.r0)) (epsW c a (radBox c.z0 c.r0))
      (hbar c a (radBox c.z0 hb)) (kappa c) (gmax c a (radBox c.z0 c.r0)) (betaA36 c a (radBox c.z0 hb)) q : ℚ) : ℝ)
      = (keff * (e0 + ew * q + hbR * q * q) + kap * gm) / (1 - beta) := by
    intro q; unfold psi; push_cast; rfl
  have hψh' : (keff * (e0 + ew * a.h + hbR * a.h * a.h) + kap * gm) / (1 - beta) < (a.h : ℝ) := by
    rw [← hpsi]; exact_mod_cast hψh
  have hψxs' : (keff * (e0 + ew * xs + hbR * xs * xs) + kap * gm) / (1 - beta) ≤ xs := by
    rw [← hpsi, hxs]; exact_mod_cast hψxs
  have hxsN' : xs + (c.r0 : ℝ) ≤ (c.rN : ℝ) := by rw [hxs]; exact_mod_cast hxsN
  have hkeff0 : 0 ≤ keff := by rw [hkeff]; exact_mod_cast kappaEff_nonneg c a
  have hhb0 : 0 ≤ hbR := by rw [hhbR]; exact_mod_cast hbar_nonneg c a _
  have hbeta0 : 0 ≤ beta := by
    rw [hbeta]
    have : (0 : ℚ) ≤ betaA36 c a (radBox c.z0 hb) := by
      unfold betaA36; rw [rng_eq]; exact foldl_rmax_ge _ _ _
    exact_mod_cast this
  have hkap0 : 0 ≤ kap := by
    rw [hkap]
    have : (0 : ℚ) ≤ kappa c := by
      unfold kappa; rw [rng_eq]; exact foldl_rmax_ge _ _ _
    exact_mod_cast this
  have hgm0 : 0 ≤ gm := by
    rw [hgm]
    have : (0 : ℚ) ≤ gmax c a (radBox c.z0 c.r0) := by
      unfold gmax; rw [← Array.foldl_toList]; exact foldl_rmax_ge _ _ _
    exact_mod_cast this
  have h1b : 0 < 1 - beta := by linarith
  -- Taylor: s(z) − s(ẑ) ≥ W(z) − E(x)
  have hzh0 : MemBox (boxArr c c.r0) zh := zhatV_memBox_r0 hc
  obtain ⟨η, hη, htay⟩ := Wfun_taylor (c := c) (a := a) hzhA hzA
  have hWzh : |Wfun c a zh| ≤ e0 := by rw [he0, radBox_eq]; exact abs_W_le_eps0 hzh0
  have hgrad : ∑ j : Fin NV, |Wgrad c a zh j - (if (j : ℕ) = S_IDX then 1 else 0)| ≤ ew := by
    rw [hew, radBox_eq]; exact sum_abs_grad_le_epsW hr hzh0
  have hhess : ∑ i : Fin NV, ∑ j : Fin NV, |Whess c a η i j| ≤ 2 * hbR := by
    rw [hhbR, radBox_eq]; exact sum_abs_hess_le hr hη
  have hds : sZ z - sZ zh = d sIdx := by
    simp only [hd]; rw [sZ_eq, sZ_eq]
  -- the gradient term
  have hgradterm : |∑ j : Fin NV, (Wgrad c a zh j - (if (j : ℕ) = S_IDX then 1 else 0)) * d j| ≤ ew * x := by
    calc |∑ j : Fin NV, (Wgrad c a zh j - (if (j : ℕ) = S_IDX then 1 else 0)) * d j|
        ≤ ∑ j : Fin NV, |Wgrad c a zh j - (if (j : ℕ) = S_IDX then 1 else 0)| * |d j| := by
          refine (Finset.abs_sum_le_sum_abs _ _).trans ?_
          exact sum_le_sum fun j _ => by rw [abs_mul]
      _ ≤ ∑ j : Fin NV, |Wgrad c a zh j - (if (j : ℕ) = S_IDX then 1 else 0)| * x :=
          sum_le_sum fun j _ => mul_le_mul_of_nonneg_left (hdk j) (abs_nonneg _)
      _ = (∑ j : Fin NV, |Wgrad c a zh j - (if (j : ℕ) = S_IDX then 1 else 0)|) * x := by
          rw [Finset.sum_mul]
      _ ≤ ew * x := mul_le_mul_of_nonneg_right hgrad hx0
  have hsumgrad : ∑ j : Fin NV, Wgrad c a zh j * d j
      = ∑ j : Fin NV, (Wgrad c a zh j - (if (j : ℕ) = S_IDX then 1 else 0)) * d j + d sIdx := by
    have : ∑ j : Fin NV, (if (j : ℕ) = S_IDX then (1 : ℝ) else 0) * d j = d sIdx := by
      rw [sum_ite_S]; ring
    rw [← this, ← Finset.sum_add_distrib]
    exact Finset.sum_congr rfl fun j _ => by ring
  -- the Hessian term
  have hhessterm : |∑ j : Fin NV, ∑ i : Fin NV, Whess c a η i j * d i * d j| ≤ 2 * hbR * x ^ 2 := by
    calc |∑ j : Fin NV, ∑ i : Fin NV, Whess c a η i j * d i * d j|
        ≤ ∑ j : Fin NV, ∑ i : Fin NV, |Whess c a η i j| * (x * x) := by
          refine (Finset.abs_sum_le_sum_abs _ _).trans ?_
          refine sum_le_sum fun j _ => ?_
          refine (Finset.abs_sum_le_sum_abs _ _).trans ?_
          refine sum_le_sum fun i _ => ?_
          rw [abs_mul, abs_mul, mul_assoc]
          refine mul_le_mul_of_nonneg_left ?_ (abs_nonneg _)
          exact mul_le_mul (hdk i) (hdk j) (abs_nonneg _) hx0
      _ = (∑ i : Fin NV, ∑ j : Fin NV, |Whess c a η i j|) * x ^ 2 := by
          rw [Finset.sum_comm]
          simp only [← Finset.sum_mul, sq]
      _ ≤ 2 * hbR * x ^ 2 := mul_le_mul_of_nonneg_right hhess (sq_nonneg x)
  have hT1 : Wfun c a z - e0 - ew * x - hbR * x ^ 2 ≤ sZ z - sZ zh := by
    rw [hds]
    have h1 := abs_le.mp hWzh
    have h2 := abs_le.mp hgradterm
    have h3 := abs_le.mp hhessterm
    rw [htay, hsumgrad]
    simp only [hd] at h2 h3 ⊢
    nlinarith [h1.1, h1.2, h2.1, h2.2, h3.1, h3.2]
  -- dichotomy
  by_cases hcase : e0 + ew * x + hbR * x ^ 2 < Wfun c a z
  · -- case 1: strict
    have : sZ zh < sZ z := by linarith
    exact ⟨this.le, fun h => absurd h this.ne'⟩
  · push_neg at hcase
    -- pinning: `x ≤ ψ(x)`
    choose ξ hξ hmvt using fun rr : Fin NV => mvt_box hzhA hzA (e70 c (pinPos a rr))
    -- `d_i = Σ_j m_ij d_j + Σ_r Y_ir (g_r(z) − g_r(ẑ))`
    have hdi : ∀ i : Fin NV, d i
        = ∑ j : Fin NV, ((if i = j then (1 : ℝ) else 0)
            - ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval (ξ rr) ((e70 c (pinPos a rr)).D j)) * d j
          + ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ)
            * (eval z (e70 c (pinPos a rr)) - eval zh (e70 c (pinPos a rr))) := by
      intro i
      have e1 : ∑ j : Fin NV, (if i = j then (1 : ℝ) else 0) * d j = d i := by
        simp [ite_mul, Finset.sum_ite_eq]
      have e2 : ∑ j : Fin NV, (∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ)
            * eval (ξ rr) ((e70 c (pinPos a rr)).D j)) * d j
          = ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ)
            * (eval z (e70 c (pinPos a rr)) - eval zh (e70 c (pinPos a rr))) := by
        simp only [hmvt, Finset.mul_sum, Finset.sum_mul]
        rw [Finset.sum_comm]
        refine sum_congr rfl fun rr _ => sum_congr rfl fun j _ => by simp only [hd]; ring
      rw [← e1, ← e2]
      simp only [sub_mul, Finset.sum_sub_distrib]
      ring
    -- the three bounds
    have hrowsum : ∀ i : Fin NV, ∑ j : Fin NV, |(if i = j then (1 : ℝ) else 0)
        - ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval (ξ rr) ((e70 c (pinPos a rr)).D j)| ≤ beta := by
      intro i
      have h1 := sum_abs_le_betaRow (M := Mrow c.Y (pinJ c a (radBox c.z0 hb)) i)
        (m := fun j => (if i = j then (1 : ℝ) else 0)
          - ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval (ξ rr) ((e70 c (pinPos a rr)).D j))
        (fun j => by rw [radBox_eq]; exact mem_Mrow_pin hr hP hltP hξ i j)
      refine h1.trans ?_
      rw [hbeta]
      exact_mod_cast betaRow_le_betaA36 (radBox c.z0 hb) i
    have hpinz : ∀ rr : Fin NV, 0 ≤ eval z (e70 c (pinPos a rr)) := by
      intro rr
      have hr' : (rr : ℕ) < a.P.size := by rw [hP]; exact rr.isLt
      refine loaded_row_nonneg hr hu hlv' hzA hsm hf (mem_loaded a ?_ ?_)
      · unfold pinPos; rw [getD_of_lt _ hr']; exact hltP _ (Array.getElem_mem hr')
      · simp only [pinsPositive, Bool.and_eq_true, decide_eq_true_eq, Array.all_eq_true] at hpos
        unfold pinPos; rw [getD_of_lt _ hr']; exact (hpos.2 rr hr').ne'
    have hYz : ∀ i : Fin NV, |∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval z (e70 c (pinPos a rr))|
        ≤ keff * Wfun c a z := by
      intro i
      calc |∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval z (e70 c (pinPos a rr))|
          ≤ ∑ rr : Fin NV, |((Ymat c.Y i rr : ℚ) : ℝ)| * eval z (e70 c (pinPos a rr)) := by
            refine (Finset.abs_sum_le_sum_abs
              (fun rr : Fin NV => ((Ymat c.Y i rr : ℚ) : ℝ) * eval z (e70 c (pinPos a rr)))
              Finset.univ).trans ?_
            refine sum_le_sum fun rr _ => ?_
            rw [abs_mul, abs_of_nonneg (hpinz rr)]
        _ ≤ ∑ rr : Fin NV, keff * (ωR a (pinPos a rr) * eval z (e70 c (pinPos a rr))) := by
            refine sum_le_sum fun rr _ => ?_
            rw [← mul_assoc]
            refine mul_le_mul_of_nonneg_right ?_ (hpinz rr)
            exact (abs_Y_le_cvec i rr).trans (cvec_le_keff hpos rr)
        _ = keff * ∑ rr : Fin NV, ωR a (pinPos a rr) * eval z (e70 c (pinPos a rr)) := by
            rw [Finset.mul_sum]
        _ ≤ keff * Wfun c a z :=
            mul_le_mul_of_nonneg_left (pin_sum_le_W hr hu ho hlv' hpos hrange hzA hsm hf) hkeff0
    have hYzh : ∀ i : Fin NV, |∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval zh (e70 c (pinPos a rr))|
        ≤ kap * gm := by
      intro i
      calc |∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval zh (e70 c (pinPos a rr))|
          ≤ ∑ rr : Fin NV, |((Ymat c.Y i rr : ℚ) : ℝ)| * gm := by
            refine (Finset.abs_sum_le_sum_abs
              (fun rr : Fin NV => ((Ymat c.Y i rr : ℚ) : ℝ) * eval zh (e70 c (pinPos a rr)))
              Finset.univ).trans ?_
            refine sum_le_sum fun rr _ => ?_
            rw [abs_mul]
            refine mul_le_mul_of_nonneg_left ?_ (abs_nonneg _)
            rw [hgm, radBox_eq]
            exact abs_pin_le_gmax hP hzh0 rr
        _ = (∑ rr : Fin NV, |((Ymat c.Y i rr : ℚ) : ℝ)|) * gm := by rw [Finset.sum_mul]
        _ ≤ kap * gm := by
            refine mul_le_mul_of_nonneg_right ?_ ?_
            · rw [hkap]; exact sum_abs_Y_le_kappa i
            · rw [hgm]
              have : (0 : ℚ) ≤ gmax c a (radBox c.z0 c.r0) := by
                unfold gmax; rw [← Array.foldl_toList]; exact foldl_rmax_ge _ _ _
              exact_mod_cast this
    -- `x ≤ β x + κ_eff W(z) + κ g_max`
    have hnn : 0 ≤ beta * x + keff * Wfun c a z + kap * gm := by
      have := mul_nonneg hbeta0 hx0
      have := mul_nonneg hkeff0 hW0
      have := mul_nonneg hkap0 hgm0
      linarith
    have hxbound : x ≤ beta * x + keff * Wfun c a z + kap * gm := by
      rw [hx, dist_pi_le_iff hnn]
      intro i
      rw [Real.dist_eq, Pi.zero_apply, sub_zero, hdi i]
      have h1 := abs_le_of_rowsum (hrowsum) d i
      have h2 := hYz i
      have h3 := hYzh i
      have hsplit : ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ)
            * (eval z (e70 c (pinPos a rr)) - eval zh (e70 c (pinPos a rr)))
          = ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval z (e70 c (pinPos a rr))
            - ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval zh (e70 c (pinPos a rr)) := by
        rw [← Finset.sum_sub_distrib]; exact sum_congr rfl fun rr _ => by ring
      rw [hsplit]
      set A := ∑ j : Fin NV, ((if i = j then (1 : ℝ) else 0)
        - ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval (ξ rr) ((e70 c (pinPos a rr)).D j)) * d j
        with hA
      set Bz := ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval z (e70 c (pinPos a rr)) with hBz
      set Bh := ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval zh (e70 c (pinPos a rr)) with hBh
      calc |A + (Bz - Bh)| ≤ |A| + |Bz - Bh| := abs_add_le _ _
        _ ≤ |A| + (|Bz| + |Bh|) := add_le_add le_rfl (abs_sub Bz Bh)
        _ ≤ beta * x + (keff * Wfun c a z + kap * gm) := add_le_add h1 (add_le_add h2 h3)
        _ = beta * x + keff * Wfun c a z + kap * gm := by ring
    -- hence `x ≤ ψ(x)`, i.e. the quadratic is `≥ 0` at `x`
    have hq : 0 ≤ (keff * hbR) * x ^ 2 + (keff * ew - (1 - beta)) * x + (keff * e0 + kap * gm) := by
      have h5 := mul_le_mul_of_nonneg_left hcase hkeff0
      have h6 : (keff * hbR) * x ^ 2 + (keff * ew - (1 - beta)) * x + (keff * e0 + kap * gm)
          = (beta * x + keff * (e0 + ew * x + hbR * x ^ 2) + kap * gm) - x := by ring
      rw [h6]; linarith
    have hqs : (keff * hbR) * xs ^ 2 + (keff * ew - (1 - beta)) * xs + (keff * e0 + kap * gm) ≤ 0 := by
      rw [div_le_iff₀ h1b] at hψxs'
      have h6 : (keff * hbR) * xs ^ 2 + (keff * ew - (1 - beta)) * xs + (keff * e0 + kap * gm)
          = (keff * (e0 + ew * xs + hbR * xs * xs) + kap * gm) - xs * (1 - beta) := by ring
      rw [h6]; linarith
    have hqh : (keff * hbR) * (a.h : ℝ) ^ 2 + (keff * ew - (1 - beta)) * a.h
        + (keff * e0 + kap * gm) < 0 := by
      rw [div_lt_iff₀ h1b] at hψh'
      have h6 : (keff * hbR) * (a.h : ℝ) ^ 2 + (keff * ew - (1 - beta)) * a.h + (keff * e0 + kap * gm)
          = (keff * (e0 + ew * a.h + hbR * a.h * a.h) + kap * gm) - a.h * (1 - beta) := by ring
      rw [h6]; linarith
    have hxxs : x ≤ xs := quad_pin (mul_nonneg hkeff0 hhb0) hxh hq hqs hqh
    -- hand over to A22
    have hzN : MemBox (boxArr c c.rN) z := by
      refine memBox_of_inBoxR hz0 fun k => ?_
      have h1 := hdk k
      have h2 := zhatV_inBoxR hc k
      calc |z k - z0R c k| = |d k + (zh k - z0R c k)| := by simp only [hd]; ring_nf
        _ ≤ |d k| + |zh k - z0R c k| := abs_add_le _ _
        _ ≤ xs + (c.r0 : ℝ) := add_le_add (h1.trans hxxs) h2
        _ ≤ (c.rN : ℝ) := hxsN'
    exact a22_optimal' hc hzN hsm hf

end

end PackingCert.Rigid
