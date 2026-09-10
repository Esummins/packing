import PackingCertMathlib.WindowsCheck
import PackingCertMathlib.PolyCoreT5

/-!
# The WINDOWS clause — (V3), an attached core inside every pose of its window (A192)

`boxed_windows.md` §5, `coreInPiece_sound`: the verifier re-derives (V3) by A135's exact
`point_in_all_poses` on the FOUR CORNERS of the attached core against every piece of its
window.  Here:

* `coreCorners` — the four corners of a v1 core `K = (kx, ky, tm, a)`;
* `coreSet_sub_of_corners` — the four corners in a square ⇒ the whole core in the square
  (the core is the biaffine image of `[−a, a]²`, `PolyCoreT5.biaffine_bound`);
* `toPBox` / `inPBox_of_inBox` — an integer box of the verifier's grid as A135's rational
  parameter box (`t = T / 2^K`, `x = X / D`);
* `checkCoreInBox` — the decidable check: `PolyCoreT5.checkVertexInPBox` on the four corners,
  each with its Bernstein positivity certificates;
* `checkCoreInBox_sound` — a PASS gives `coreSet K ⊆ q.set` for EVERY pose `q` in the box;
* `checkWindowsI_kill_of_check` — Theorem W's end form with (V3) discharged by the check.

No axiom is introduced.
-/

namespace PackingCert
namespace S11
namespace WindowsW

open Set MeasureI CaseI
open PackingCert.S11.LocalCertT

noncomputable section

/-! ## 1. The four corners of a core -/

/-- The four corners `centre + a·(±e₁ ± e₂)`, `e₁ = (cos θ_m, sin θ_m)`, `e₂ = (−sin θ_m, cos θ_m)`. -/
def coreCorners (K : CCore) : List (ℚ × ℚ) :=
  [ (K.kx + K.a * ((ratCosSin K.tm).1 - (ratCosSin K.tm).2),
      K.ky + K.a * ((ratCosSin K.tm).2 + (ratCosSin K.tm).1)),
    (K.kx + K.a * ((ratCosSin K.tm).1 + (ratCosSin K.tm).2),
      K.ky + K.a * ((ratCosSin K.tm).2 - (ratCosSin K.tm).1)),
    (K.kx + K.a * (-(ratCosSin K.tm).1 + (ratCosSin K.tm).2),
      K.ky + K.a * (-(ratCosSin K.tm).2 - (ratCosSin K.tm).1)),
    (K.kx + K.a * (-(ratCosSin K.tm).1 - (ratCosSin K.tm).2),
      K.ky + K.a * (-(ratCosSin K.tm).2 + (ratCosSin K.tm).1)) ]

/-- The corners, as real points, in the `(i, j) ∈ {±1}²` form. -/
theorem corner_mem {K : CCore} {q : PSq}
    (hc : ∀ v ∈ coreCorners K, ((v.1 : ℝ), (v.2 : ℝ)) ∈ q.set)
    (i j : ℝ) (hi : i = 1 ∨ i = -1) (hj : j = 1 ∨ j = -1) :
    ((K.kx : ℝ) + (K.a : ℝ) * (i * cosT (K.tm : ℝ) - j * sinT (K.tm : ℝ)),
      (K.ky : ℝ) + (K.a : ℝ) * (i * sinT (K.tm : ℝ) + j * cosT (K.tm : ℝ))) ∈ q.set := by
  rcases hi with rfl | rfl <;> rcases hj with rfl | rfl
  · have h := hc _ (List.mem_cons_self)
    convert h using 2 <;> push_cast <;> rw [ratCosSin_fst, ratCosSin_snd] <;> ring
  · have h := hc _ (List.mem_cons_of_mem _ (List.mem_cons_self))
    convert h using 2 <;> push_cast <;> rw [ratCosSin_fst, ratCosSin_snd] <;> ring
  · have h := hc _ (List.mem_cons_of_mem _ (List.mem_cons_of_mem _
      (List.mem_cons_of_mem _ (List.mem_cons_self))))
    convert h using 2 <;> push_cast <;> rw [ratCosSin_fst, ratCosSin_snd] <;> ring
  · have h := hc _ (List.mem_cons_of_mem _ (List.mem_cons_of_mem _ (List.mem_cons_self)))
    convert h using 2 <;> push_cast <;> rw [ratCosSin_fst, ratCosSin_snd] <;> ring

/-- **The core is inside the square once its four corners are.** -/
theorem coreSet_sub_of_corners {K : CCore} {q : PSq}
    (hc : ∀ v ∈ coreCorners K, ((v.1 : ℝ), (v.2 : ℝ)) ∈ q.set) : coreSet K ⊆ q.set := by
  intro p hp
  obtain ⟨h1, h2⟩ := hp
  have hcs : cosT (K.tm : ℝ) ^ 2 + sinT (K.tm : ℝ) ^ 2 = 1 := cosT_sq_add_sinT_sq _
  obtain ⟨u, hu⟩ : ∃ u : ℝ, u = (p.1 - (K.kx : ℝ)) * cosT (K.tm : ℝ) + (p.2 - (K.ky : ℝ)) * sinT (K.tm : ℝ) := ⟨_, rfl⟩
  obtain ⟨v, hv⟩ : ∃ v : ℝ, v = (-(p.1 - (K.kx : ℝ))) * sinT (K.tm : ℝ) + (p.2 - (K.ky : ℝ)) * cosT (K.tm : ℝ) := ⟨_, rfl⟩
  have hua : |u| ≤ (K.a : ℝ) := by rw [hu]; exact h1
  have hva : |v| ≤ (K.a : ℝ) := by rw [hv]; exact h2
  have hu0 : -(K.a : ℝ) ≤ u := (abs_le.mp hua).1
  have hu1 : u ≤ (K.a : ℝ) := (abs_le.mp hua).2
  have hv0 : -(K.a : ℝ) ≤ v := (abs_le.mp hva).1
  have hv1 : v ≤ (K.a : ℝ) := (abs_le.mp hva).2
  have ex : p.1 = (K.kx : ℝ) + u * cosT (K.tm : ℝ) - v * sinT (K.tm : ℝ) := by
    rw [hu, hv]; linear_combination (-(p.1 - (K.kx : ℝ))) * hcs
  have ey : p.2 = (K.ky : ℝ) + u * sinT (K.tm : ℝ) + v * cosT (K.tm : ℝ) := by
    rw [hu, hv]; linear_combination (-(p.2 - (K.ky : ℝ))) * hcs
  have hproj : ∀ i j : ℝ, (i = 1 ∨ i = -1) → (j = 1 ∨ j = -1) →
      |((K.kx : ℝ) + (K.a : ℝ) * (i * cosT (K.tm : ℝ) - j * sinT (K.tm : ℝ)) - q.cx) * cosT q.t + ((K.ky : ℝ) + (K.a : ℝ) * (i * sinT (K.tm : ℝ) + j * cosT (K.tm : ℝ)) - q.cy) * sinT q.t| ≤ 1 / 2 ∧
      |((K.kx : ℝ) + (K.a : ℝ) * (i * cosT (K.tm : ℝ) - j * sinT (K.tm : ℝ)) - q.cx) * (-sinT q.t) + ((K.ky : ℝ) + (K.a : ℝ) * (i * sinT (K.tm : ℝ) + j * cosT (K.tm : ℝ)) - q.cy) * cosT q.t| ≤ 1 / 2 := by
    intro i j hi hj
    have h := (mem_set_iff_uv q _).mp (corner_mem hc i j hi hj)
    simpa only [rdot, edir, perpV] using h
  have h1_pp : |(((K.kx : ℝ) - q.cx) * cosT q.t + ((K.ky : ℝ) - q.cy) * sinT q.t) - (-(cosT (K.tm : ℝ) * cosT q.t + sinT (K.tm : ℝ) * sinT q.t)) * (K.a : ℝ) - (-(-sinT (K.tm : ℝ) * cosT q.t + cosT (K.tm : ℝ) * sinT q.t)) * (K.a : ℝ)| ≤ 1 / 2 := by
    have e : (((K.kx : ℝ) - q.cx) * cosT q.t + ((K.ky : ℝ) - q.cy) * sinT q.t) - (-(cosT (K.tm : ℝ) * cosT q.t + sinT (K.tm : ℝ) * sinT q.t)) * (K.a : ℝ) - (-(-sinT (K.tm : ℝ) * cosT q.t + cosT (K.tm : ℝ) * sinT q.t)) * (K.a : ℝ) = ((K.kx : ℝ) + (K.a : ℝ) * ((1 : ℝ) * cosT (K.tm : ℝ) - (1 : ℝ) * sinT (K.tm : ℝ)) - q.cx) * cosT q.t + ((K.ky : ℝ) + (K.a : ℝ) * ((1 : ℝ) * sinT (K.tm : ℝ) + (1 : ℝ) * cosT (K.tm : ℝ)) - q.cy) * sinT q.t := by ring
    rw [e]
    exact (hproj (1 : ℝ) (1 : ℝ) (Or.inl rfl) (Or.inl rfl)).1
  have h1_pm : |(((K.kx : ℝ) - q.cx) * cosT q.t + ((K.ky : ℝ) - q.cy) * sinT q.t) - (-(cosT (K.tm : ℝ) * cosT q.t + sinT (K.tm : ℝ) * sinT q.t)) * (K.a : ℝ) - (-(-sinT (K.tm : ℝ) * cosT q.t + cosT (K.tm : ℝ) * sinT q.t)) * (-(K.a : ℝ))| ≤ 1 / 2 := by
    have e : (((K.kx : ℝ) - q.cx) * cosT q.t + ((K.ky : ℝ) - q.cy) * sinT q.t) - (-(cosT (K.tm : ℝ) * cosT q.t + sinT (K.tm : ℝ) * sinT q.t)) * (K.a : ℝ) - (-(-sinT (K.tm : ℝ) * cosT q.t + cosT (K.tm : ℝ) * sinT q.t)) * (-(K.a : ℝ)) = ((K.kx : ℝ) + (K.a : ℝ) * ((1 : ℝ) * cosT (K.tm : ℝ) - (-1 : ℝ) * sinT (K.tm : ℝ)) - q.cx) * cosT q.t + ((K.ky : ℝ) + (K.a : ℝ) * ((1 : ℝ) * sinT (K.tm : ℝ) + (-1 : ℝ) * cosT (K.tm : ℝ)) - q.cy) * sinT q.t := by ring
    rw [e]
    exact (hproj (1 : ℝ) (-1 : ℝ) (Or.inl rfl) (Or.inr rfl)).1
  have h1_mp : |(((K.kx : ℝ) - q.cx) * cosT q.t + ((K.ky : ℝ) - q.cy) * sinT q.t) - (-(cosT (K.tm : ℝ) * cosT q.t + sinT (K.tm : ℝ) * sinT q.t)) * (-(K.a : ℝ)) - (-(-sinT (K.tm : ℝ) * cosT q.t + cosT (K.tm : ℝ) * sinT q.t)) * (K.a : ℝ)| ≤ 1 / 2 := by
    have e : (((K.kx : ℝ) - q.cx) * cosT q.t + ((K.ky : ℝ) - q.cy) * sinT q.t) - (-(cosT (K.tm : ℝ) * cosT q.t + sinT (K.tm : ℝ) * sinT q.t)) * (-(K.a : ℝ)) - (-(-sinT (K.tm : ℝ) * cosT q.t + cosT (K.tm : ℝ) * sinT q.t)) * (K.a : ℝ) = ((K.kx : ℝ) + (K.a : ℝ) * ((-1 : ℝ) * cosT (K.tm : ℝ) - (1 : ℝ) * sinT (K.tm : ℝ)) - q.cx) * cosT q.t + ((K.ky : ℝ) + (K.a : ℝ) * ((-1 : ℝ) * sinT (K.tm : ℝ) + (1 : ℝ) * cosT (K.tm : ℝ)) - q.cy) * sinT q.t := by ring
    rw [e]
    exact (hproj (-1 : ℝ) (1 : ℝ) (Or.inr rfl) (Or.inl rfl)).1
  have h1_mm : |(((K.kx : ℝ) - q.cx) * cosT q.t + ((K.ky : ℝ) - q.cy) * sinT q.t) - (-(cosT (K.tm : ℝ) * cosT q.t + sinT (K.tm : ℝ) * sinT q.t)) * (-(K.a : ℝ)) - (-(-sinT (K.tm : ℝ) * cosT q.t + cosT (K.tm : ℝ) * sinT q.t)) * (-(K.a : ℝ))| ≤ 1 / 2 := by
    have e : (((K.kx : ℝ) - q.cx) * cosT q.t + ((K.ky : ℝ) - q.cy) * sinT q.t) - (-(cosT (K.tm : ℝ) * cosT q.t + sinT (K.tm : ℝ) * sinT q.t)) * (-(K.a : ℝ)) - (-(-sinT (K.tm : ℝ) * cosT q.t + cosT (K.tm : ℝ) * sinT q.t)) * (-(K.a : ℝ)) = ((K.kx : ℝ) + (K.a : ℝ) * ((-1 : ℝ) * cosT (K.tm : ℝ) - (-1 : ℝ) * sinT (K.tm : ℝ)) - q.cx) * cosT q.t + ((K.ky : ℝ) + (K.a : ℝ) * ((-1 : ℝ) * sinT (K.tm : ℝ) + (-1 : ℝ) * cosT (K.tm : ℝ)) - q.cy) * sinT q.t := by ring
    rw [e]
    exact (hproj (-1 : ℝ) (-1 : ℝ) (Or.inr rfl) (Or.inr rfl)).1
  have h2_pp : |(((K.kx : ℝ) - q.cx) * (-sinT q.t) + ((K.ky : ℝ) - q.cy) * cosT q.t) - (-(cosT (K.tm : ℝ) * (-sinT q.t) + sinT (K.tm : ℝ) * cosT q.t)) * (K.a : ℝ) - (-(-sinT (K.tm : ℝ) * (-sinT q.t) + cosT (K.tm : ℝ) * cosT q.t)) * (K.a : ℝ)| ≤ 1 / 2 := by
    have e : (((K.kx : ℝ) - q.cx) * (-sinT q.t) + ((K.ky : ℝ) - q.cy) * cosT q.t) - (-(cosT (K.tm : ℝ) * (-sinT q.t) + sinT (K.tm : ℝ) * cosT q.t)) * (K.a : ℝ) - (-(-sinT (K.tm : ℝ) * (-sinT q.t) + cosT (K.tm : ℝ) * cosT q.t)) * (K.a : ℝ) = ((K.kx : ℝ) + (K.a : ℝ) * ((1 : ℝ) * cosT (K.tm : ℝ) - (1 : ℝ) * sinT (K.tm : ℝ)) - q.cx) * (-sinT q.t) + ((K.ky : ℝ) + (K.a : ℝ) * ((1 : ℝ) * sinT (K.tm : ℝ) + (1 : ℝ) * cosT (K.tm : ℝ)) - q.cy) * cosT q.t := by ring
    rw [e]
    exact (hproj (1 : ℝ) (1 : ℝ) (Or.inl rfl) (Or.inl rfl)).2
  have h2_pm : |(((K.kx : ℝ) - q.cx) * (-sinT q.t) + ((K.ky : ℝ) - q.cy) * cosT q.t) - (-(cosT (K.tm : ℝ) * (-sinT q.t) + sinT (K.tm : ℝ) * cosT q.t)) * (K.a : ℝ) - (-(-sinT (K.tm : ℝ) * (-sinT q.t) + cosT (K.tm : ℝ) * cosT q.t)) * (-(K.a : ℝ))| ≤ 1 / 2 := by
    have e : (((K.kx : ℝ) - q.cx) * (-sinT q.t) + ((K.ky : ℝ) - q.cy) * cosT q.t) - (-(cosT (K.tm : ℝ) * (-sinT q.t) + sinT (K.tm : ℝ) * cosT q.t)) * (K.a : ℝ) - (-(-sinT (K.tm : ℝ) * (-sinT q.t) + cosT (K.tm : ℝ) * cosT q.t)) * (-(K.a : ℝ)) = ((K.kx : ℝ) + (K.a : ℝ) * ((1 : ℝ) * cosT (K.tm : ℝ) - (-1 : ℝ) * sinT (K.tm : ℝ)) - q.cx) * (-sinT q.t) + ((K.ky : ℝ) + (K.a : ℝ) * ((1 : ℝ) * sinT (K.tm : ℝ) + (-1 : ℝ) * cosT (K.tm : ℝ)) - q.cy) * cosT q.t := by ring
    rw [e]
    exact (hproj (1 : ℝ) (-1 : ℝ) (Or.inl rfl) (Or.inr rfl)).2
  have h2_mp : |(((K.kx : ℝ) - q.cx) * (-sinT q.t) + ((K.ky : ℝ) - q.cy) * cosT q.t) - (-(cosT (K.tm : ℝ) * (-sinT q.t) + sinT (K.tm : ℝ) * cosT q.t)) * (-(K.a : ℝ)) - (-(-sinT (K.tm : ℝ) * (-sinT q.t) + cosT (K.tm : ℝ) * cosT q.t)) * (K.a : ℝ)| ≤ 1 / 2 := by
    have e : (((K.kx : ℝ) - q.cx) * (-sinT q.t) + ((K.ky : ℝ) - q.cy) * cosT q.t) - (-(cosT (K.tm : ℝ) * (-sinT q.t) + sinT (K.tm : ℝ) * cosT q.t)) * (-(K.a : ℝ)) - (-(-sinT (K.tm : ℝ) * (-sinT q.t) + cosT (K.tm : ℝ) * cosT q.t)) * (K.a : ℝ) = ((K.kx : ℝ) + (K.a : ℝ) * ((-1 : ℝ) * cosT (K.tm : ℝ) - (1 : ℝ) * sinT (K.tm : ℝ)) - q.cx) * (-sinT q.t) + ((K.ky : ℝ) + (K.a : ℝ) * ((-1 : ℝ) * sinT (K.tm : ℝ) + (1 : ℝ) * cosT (K.tm : ℝ)) - q.cy) * cosT q.t := by ring
    rw [e]
    exact (hproj (-1 : ℝ) (1 : ℝ) (Or.inr rfl) (Or.inl rfl)).2
  have h2_mm : |(((K.kx : ℝ) - q.cx) * (-sinT q.t) + ((K.ky : ℝ) - q.cy) * cosT q.t) - (-(cosT (K.tm : ℝ) * (-sinT q.t) + sinT (K.tm : ℝ) * cosT q.t)) * (-(K.a : ℝ)) - (-(-sinT (K.tm : ℝ) * (-sinT q.t) + cosT (K.tm : ℝ) * cosT q.t)) * (-(K.a : ℝ))| ≤ 1 / 2 := by
    have e : (((K.kx : ℝ) - q.cx) * (-sinT q.t) + ((K.ky : ℝ) - q.cy) * cosT q.t) - (-(cosT (K.tm : ℝ) * (-sinT q.t) + sinT (K.tm : ℝ) * cosT q.t)) * (-(K.a : ℝ)) - (-(-sinT (K.tm : ℝ) * (-sinT q.t) + cosT (K.tm : ℝ) * cosT q.t)) * (-(K.a : ℝ)) = ((K.kx : ℝ) + (K.a : ℝ) * ((-1 : ℝ) * cosT (K.tm : ℝ) - (-1 : ℝ) * sinT (K.tm : ℝ)) - q.cx) * (-sinT q.t) + ((K.ky : ℝ) + (K.a : ℝ) * ((-1 : ℝ) * sinT (K.tm : ℝ) + (-1 : ℝ) * cosT (K.tm : ℝ)) - q.cy) * cosT q.t := by ring
    rw [e]
    exact (hproj (-1 : ℝ) (-1 : ℝ) (Or.inr rfl) (Or.inr rfl)).2
  rw [mem_set_iff_uv]
  simp only [rdot, edir, perpV]
  rw [ex, ey]
  constructor
  · have e : ((K.kx : ℝ) + u * cosT (K.tm : ℝ) - v * sinT (K.tm : ℝ) - q.cx) * cosT q.t + ((K.ky : ℝ) + u * sinT (K.tm : ℝ) + v * cosT (K.tm : ℝ) - q.cy) * sinT q.t
        = (((K.kx : ℝ) - q.cx) * cosT q.t + ((K.ky : ℝ) - q.cy) * sinT q.t) - (-(cosT (K.tm : ℝ) * cosT q.t + sinT (K.tm : ℝ) * sinT q.t)) * u - (-(-sinT (K.tm : ℝ) * cosT q.t + cosT (K.tm : ℝ) * sinT q.t)) * v := by ring
    rw [e]
    exact biaffine_bound hu0 hu1 hv0 hv1 h1_mm h1_mp h1_pm h1_pp
  · have e : ((K.kx : ℝ) + u * cosT (K.tm : ℝ) - v * sinT (K.tm : ℝ) - q.cx) * (-sinT q.t) + ((K.ky : ℝ) + u * sinT (K.tm : ℝ) + v * cosT (K.tm : ℝ) - q.cy) * cosT q.t
        = (((K.kx : ℝ) - q.cx) * (-sinT q.t) + ((K.ky : ℝ) - q.cy) * cosT q.t) - (-(cosT (K.tm : ℝ) * (-sinT q.t) + sinT (K.tm : ℝ) * cosT q.t)) * u - (-(-sinT (K.tm : ℝ) * (-sinT q.t) + cosT (K.tm : ℝ) * cosT q.t)) * v := by ring
    rw [e]
    exact biaffine_bound hu0 hu1 hv0 hv1 h2_mm h2_mp h2_pm h2_pp


/-! ## 2. Integer boxes as rational parameter boxes -/

/-- The verifier's integer box as A135's rational parameter box. -/
def toPBox (ctx : Ctx) (b : IBox) : PBox :=
  ⟨(b.X0 : ℚ) / ctx.D, (b.X1 : ℚ) / ctx.D, (b.Y0 : ℚ) / ctx.D, (b.Y1 : ℚ) / ctx.D,
    (b.T0 : ℚ) / ctx.TROOT, (b.T1 : ℚ) / ctx.TROOT⟩

theorem inPBox_of_inBox {ctx : Ctx} (hD : 0 < ctx.D) (hR : 0 < ctx.TROOT) {b : IBox} {q : PSq}
    (h : inBox ctx b q) : InPBox (toPBox ctx b) q := by
  obtain ⟨h1, h2, h3, h4, h5, h6⟩ := h
  have hDR : (0 : ℝ) < (ctx.D : ℝ) := by exact_mod_cast hD
  have hRR : (0 : ℝ) < (ctx.TROOT : ℝ) := by exact_mod_cast hR
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
  · show (((b.X0 : ℚ) / ctx.D : ℚ) : ℝ) ≤ q.cx
    push_cast
    rw [div_le_iff₀ hDR]
    exact h3
  · show q.cx ≤ (((b.X1 : ℚ) / ctx.D : ℚ) : ℝ)
    push_cast
    rw [le_div_iff₀ hDR]
    exact h4
  · show (((b.Y0 : ℚ) / ctx.D : ℚ) : ℝ) ≤ q.cy
    push_cast
    rw [div_le_iff₀ hDR]
    exact h5
  · show q.cy ≤ (((b.Y1 : ℚ) / ctx.D : ℚ) : ℝ)
    push_cast
    rw [le_div_iff₀ hDR]
    exact h6
  · show (((b.T0 : ℚ) / ctx.TROOT : ℚ) : ℝ) ≤ q.t
    push_cast
    rw [div_le_iff₀ hRR]
    exact h1
  · show q.t ≤ (((b.T1 : ℚ) / ctx.TROOT : ℚ) : ℝ)
    push_cast
    rw [le_div_iff₀ hRR]
    exact h2

/-! ## 3. The decidable (V3) check and its soundness -/

/-- `checkVertexInPBox` on the four corners of `K` against the box `b`, each corner with its
own list of four Bernstein certificate lists (A135's data shape). -/
def checkCoreInBox (ctx : Ctx) (K : CCore) (b : IBox) (cs : List (List (List Poly))) : Bool :=
  match cs, coreCorners K with
  | [c0, c1, c2, c3], [v0, v1, v2, v3] =>
      checkVertexInPBox (toPBox ctx b) v0 c0 && checkVertexInPBox (toPBox ctx b) v1 c1 &&
      checkVertexInPBox (toPBox ctx b) v2 c2 && checkVertexInPBox (toPBox ctx b) v3 c3
  | _, _ => false

/-- **(V3) from the check**: a PASS puts the whole core inside every pose of the box. -/
theorem checkCoreInBox_sound {ctx : Ctx} (hD : 0 < ctx.D) (hR : 0 < ctx.TROOT) {K : CCore}
    {b : IBox} {cs : List (List (List Poly))} (h : checkCoreInBox ctx K b cs = true) :
    ∀ q : PSq, inBox ctx b q → coreSet K ⊆ q.set := by
  intro q hq
  have hB := inPBox_of_inBox hD hR hq
  refine coreSet_sub_of_corners ?_
  match cs, h with
  | [c0, c1, c2, c3], h =>
    simp only [checkCoreInBox, coreCorners, Bool.and_eq_true] at h
    obtain ⟨⟨⟨k0, k1⟩, k2⟩, k3⟩ := h
    intro v hv
    simp only [coreCorners, List.mem_cons, List.not_mem_nil, or_false] at hv
    rcases hv with rfl | rfl | rfl | rfl
    · exact checkVertexInPBox_sound k0 q hB
    · exact checkVertexInPBox_sound k1 q hB
    · exact checkVertexInPBox_sound k2 q hB
    · exact checkVertexInPBox_sound k3 q hB

/-- **Theorem W for a PASS, with (V3) discharged by `checkCoreInBox`** on every piece of every
window that carries a core (`certs` are the Bernstein certificates, per window and piece). -/
theorem checkWindowsI_kill_of_check {C : CCertW} (h : checkWindowsI C = true)
    (certs : Fin C.windows.length → IBox → List (List (List Poly)))
    (hV3 : ∀ i (j : Fin C.c.cores.length), (C.windows.get i).core = some (j : ℕ) →
      ∀ b ∈ (C.windows.get i).pieces,
        checkCoreInBox (mkCtx (toMCert C.c)) (C.c.cores.get j) b (certs i b) = true)
    {Q : Fin C.c.n → Set RP} (hQ : IsStrictFamily C.c.n (caseSide C.c) Q)
    (σ : Fin C.windows.length → Fin C.c.n) (hσ : Function.Injective σ)
    (hH1 : ∀ i, WinSet (mkCtx (toMCert C.c)) (C.windows.get i) (Q (σ i)))
    (own : Fin C.c.cores.length → Fin C.c.n)
    (hH2 : ∀ j : Fin C.c.cores.length, (∀ i, (C.windows.get i).core ≠ some (j : ℕ)) →
      coreSet (C.c.cores.get j) ⊆ Q (own j))
    (hH3 : ∀ k, ¬ CaseExempt C.c (Q k)) : False := by
  obtain ⟨hsd, -, -, -, -, -, -, -, -⟩ := checkWindowsI_facts h
  have hD : 0 < (mkCtx (toMCert C.c)).D := by
    change 0 < C.c.sDen * (2 : Int) ^ (C.c.depth + 2)
    positivity
  have hR : 0 < (mkCtx (toMCert C.c)).TROOT := by
    change 0 < (2 : Int) ^ (C.c.depth + 1)
    positivity
  refine checkWindowsI_kill h hQ σ hσ hH1 own hH2 hH3 ?_
  intro i j hj q hq
  obtain ⟨b, hb, hbq⟩ := hq
  exact checkCoreInBox_sound hD hR (hV3 i j hj b hb) q hbq

end

end WindowsW
end S11
end PackingCert
