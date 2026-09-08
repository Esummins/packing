import PackingCertMathlib.LocalCertT2

/-!
# The reflected plumbing of `CertCover`: the walk, the row builder, the index map — A138 T1

`LocalCertT.lean` (A133) discharged **(C1)** the tilt cover and `LocalCertT2.lean` (A134)
discharged **(C2)** the selection cover, **(C3)** Lemma RELAX and the geometric half of **(C4)**.
A134's §9 named the residue exactly, all of it bookkeeping:

* **(R1)** the reflected tree walk over `bisect` / `branch` / `imp` / `imp_sel` / `dead`,
  consuming `LocalCertT.coverOk_sound` and `LocalCertT2.selectionOk_sound`;
* **(R2)** the reflected row builder `rowsOf` with the OUTWARD quantisation step;
* **(R3)** the variable index map (A119's layout `vi = 2i+1`, tilts last);
* **(R4)** the leaf data and the replay.

This file writes (R1)–(R3).  Its organising idea is that all of A134's §9 (R2) — the ≈ 600 lines
of "affine-form arithmetic plus outward quantisation" — collapses to ONE lemma, `rowImplies_sound`
(§2), once the true row and the emitted row are compared through `LocalCert.minL`:

    minL (true.co − emitted.co) box ≥ emitted.k − true.k   ⟹   emitted ≤ true  on the box,

which is exactly the invariant `gen_local_t.quantise_leaf` establishes (coefficients rounded to
`1/10¹²`, the constant lowered by the total rounding slack over the box).  So the row BUILDER only
has to produce the true rows and their justifications; nothing about the rounding is ever
re-derived.

* **§1** affine forms from unit vectors — `uvec`, and `evalL` through `addL` / `smulL`.
* **§2** the outward-quantisation lemma `rowImplies` / `rowImplies_sound`.
* **§3** the reflected certificate data (`CBody`, `CMeta`) and **(R3)** the index map `certX`,
  with `layoutOk` deciding that the emitted body records use A119's layout.
* **§4** the geometric bundle `GeoHyp` — one square per body, its centre and tilt read off `certX`
  — and the per-body interval and affine forms (`cenIQ`, `cenAff`, `tiltIQ`) with their
  soundness, from which `PairBox.holds` follows for every pair.
* **§5** **(R2)** the row builder: the wall family and the selection family, each with the
  soundness lemma that `LocalCertT2.relax_wall` / `relax_selection` supplies.
* **§6** **(R1)** the reflected tree and `walk_sound`.
* **§7** the glue `certCover_of_check`.
-/

namespace PackingCert
namespace S11
namespace LocalCertT3

open Set
open PackingCert.S11.LocalCert
open PackingCert.S11.LocalCertT
open PackingCert.S11.LocalCertT2

/-! ## 1. Affine forms built from unit vectors

`LocalCert.evalL` reads a POSITIONAL coefficient list.  A row of the certificate is sparse — at
most six of the twenty variables — so it is built here by `addL`ing unit vectors, and `evalL`
distributes over the construction by `LocalCert.evalL_addL` / `evalL_smulL`, which are theorems.
An affine FORM is a pair `(co, k)`, read as `Σ_j co_j x_j + k`. -/

/-- The coefficient list of `a · x_i`. -/
def uvec (i : Nat) (a : ℚ) : List ℚ := List.replicate i 0 ++ [a]

theorem evalL_replicate_append (n : Nat) (p : List ℚ) (x : Nat → ℝ) (i : Nat) :
    evalL (List.replicate n 0 ++ p) x i = evalL p x (i + n) := by
  induction n generalizing i with
  | zero => simp [evalL]
  | succ n ih =>
    have e : List.replicate (n + 1) (0 : ℚ) ++ p = 0 :: (List.replicate n 0 ++ p) := rfl
    rw [e]
    simp only [evalL, Rat.cast_zero, zero_mul, zero_add, ih]
    congr 1
    omega

theorem evalL_uvec (i : Nat) (a : ℚ) (x : Nat → ℝ) : evalL (uvec i a) x 0 = (a : ℝ) * x i := by
  rw [uvec, evalL_replicate_append]
  simp only [Nat.zero_add, evalL]
  ring

/-- An affine form over the LP variables. -/
abbrev Aff := List ℚ × ℚ

def aZero : Aff := ([], 0)
def aConst (c : ℚ) : Aff := ([], c)
def aVar (i : Nat) (a : ℚ) : Aff := (uvec i a, 0)
def aAdd (u v : Aff) : Aff := (addL u.1 v.1, u.2 + v.2)
def aSmul (c : ℚ) (u : Aff) : Aff := (smulL c u.1, c * u.2)
def aSub (u v : Aff) : Aff := aAdd u (aSmul (-1) v)

/-- The real value of an affine form at a variable vector. -/
noncomputable def aVal (u : Aff) (x : Nat → ℝ) : ℝ := evalL u.1 x 0 + (u.2 : ℝ)

theorem aVal_zero (x : Nat → ℝ) : aVal aZero x = 0 := by simp [aVal, aZero, evalL]

theorem aVal_const (c : ℚ) (x : Nat → ℝ) : aVal (aConst c) x = (c : ℝ) := by
  simp [aVal, aConst, evalL]

theorem aVal_var (i : Nat) (a : ℚ) (x : Nat → ℝ) : aVal (aVar i a) x = (a : ℝ) * x i := by
  simp [aVal, aVar, evalL_uvec]

theorem aVal_add (u v : Aff) (x : Nat → ℝ) : aVal (aAdd u v) x = aVal u x + aVal v x := by
  simp only [aVal, aAdd, evalL_addL]
  push_cast
  ring

theorem aVal_smul (c : ℚ) (u : Aff) (x : Nat → ℝ) : aVal (aSmul c u) x = (c : ℝ) * aVal u x := by
  simp only [aVal, aSmul, evalL_smulL]
  push_cast
  ring

theorem aVal_sub (u v : Aff) (x : Nat → ℝ) : aVal (aSub u v) x = aVal u x - aVal v x := by
  simp only [aSub, aVal_add, aVal_smul]
  push_cast
  ring

/-! ## 2. (R2), the quantisation half: one lemma

`gen_local_t.quantise_leaf` rounds each coefficient of a true relaxed row to the nearest multiple
of `1/10¹²` and LOWERS the constant by the total rounding slack over the leaf's box, so that the
emitted row is implied by the true row AT EVERY POINT OF THE BOX.  Reflected, that invariant is a
single `minL` comparison, and its soundness is `LocalCert.minL_le`: nothing about the rounding
itself is re-derived here, and a generator that rounds differently — or not at all — is accepted
by exactly the same check. -/

/-- **The outward-quantisation check.**  The emitted row `r` is implied on `box` by the true row
`Σ tc_j x_j + tk ≤ 0`. -/
def rowImplies (tc : List ℚ) (tk : ℚ) (box : List (ℚ × ℚ)) (r : CRow) : Bool :=
  match minL (addL tc (smulL (-1) r.co)) box with
  | none => false
  | some v => decide (r.k - tk ≤ v)

/-- **Soundness of the outward quantisation.**  On the box, a true row that holds forces the
emitted row that passes the check to hold. -/
theorem rowImplies_sound {tc : List ℚ} {tk : ℚ} {box : List (ℚ × ℚ)} {r : CRow} {x : Nat → ℝ}
    (hchk : rowImplies tc tk box r = true) (hb : InBox box x 0)
    (htrue : evalL tc x 0 + (tk : ℝ) ≤ 0) : evalL r.co x 0 + (r.k : ℝ) ≤ 0 := by
  revert hchk
  cases hmin : minL (addL tc (smulL (-1) r.co)) box with
  | none => intro h; simp [rowImplies, hmin] at h
  | some v =>
    intro h
    simp only [rowImplies, hmin, decide_eq_true_eq] at h
    have hlow : (v : ℝ) ≤ evalL (addL tc (smulL (-1) r.co)) x 0 := minL_le _ _ _ _ _ hmin hb
    rw [evalL_addL, evalL_smulL] at hlow
    have hcast : ((r.k - tk : ℚ) : ℝ) ≤ (v : ℝ) := by exact_mod_cast h
    push_cast at hcast hlow
    linarith

/-- The same check against an affine FORM, which is how the row builder produces its rows. -/
def affImplies (u : Aff) (box : List (ℚ × ℚ)) (r : CRow) : Bool := rowImplies u.1 u.2 box r

theorem affImplies_sound {u : Aff} {box : List (ℚ × ℚ)} {r : CRow} {x : Nat → ℝ}
    (hchk : affImplies u box r = true) (hb : InBox box x 0) (htrue : aVal u x ≤ 0) :
    evalL r.co x 0 + (r.k : ℝ) ≤ 0 :=
  rowImplies_sound hchk hb htrue

/-! ## 3. The reflected certificate, and (R3) the variable index map

A119's numbering, inherited by A133 and A134: the side is variable `0`, body `i` owns the two
centre variables `2i+1` (`cx`) and `2i+2` (`cy`) IN THE CERTIFICATE'S BODY ORDER (the boxes of `L`
first, then the slack cores of `P`), and the tilts of the `|L|` free bodies follow all the
centres, at `2·|bodies| + 1 + i`.  So `nv = 2(|L| + |P|) + 1 + |L|`.  A PIN's centre variable is
the OFFSET from its nominal centre `(α + β s)`, which is why the map below subtracts it; a pin
has no tilt variable at all, its tilt being exactly `0`.

Verified on `S07_trump5_r0.10_rho40`: `nv = 20`, three free bodies with `vi = 1, 3, 5` and
`ti = 17, 18, 19`, five pins with `vi = 7, 9, 11, 13, 15`. -/

/-- One body of the certificate.  A free body carries its centre box and its ROOT tilt cell; a
pin carries its affine centre and the half-width of its slack core.  All rational: the `Box` /
`Pin` of the Lean statement are read OFF these (`boxOfCB` / `pinOfCB`), so no matching obligation
between the certificate and the statement is left over. -/
structure CBody where
  free : Bool
  vi : Nat
  ti : Nat
  x0 : ℚ
  x1 : ℚ
  y0 : ℚ
  y1 : ℚ
  t0 : ℚ
  t1 : ℚ
  ax0 : ℚ
  ax1 : ℚ
  ay0 : ℚ
  ay1 : ℚ
  hh : ℚ
deriving Inhabited, Repr, DecidableEq

/-- The certificate's header: the bodies in their own order, the number of FREE ones, and the
side window. -/
structure CMeta where
  bs : List CBody
  nL : Nat
  slo : ℚ
  shi : ℚ
deriving Inhabited, Repr, DecidableEq

noncomputable def boxOfCB (b : CBody) : Box := ⟨b.x0, b.x1, b.y0, b.y1, b.t0, b.t1⟩
noncomputable def pinOfCB (b : CBody) : Pin := ⟨b.ax0, b.ax1, b.ay0, b.ay1, b.hh⟩

/-- The neighbourhood's `L`. -/
noncomputable def CMeta.boxes (M : CMeta) : List Box :=
  (List.range M.nL).map fun i => boxOfCB (M.bs.getD i default)

/-- The neighbourhood's `P`. -/
noncomputable def CMeta.pins (M : CMeta) : List Pin :=
  (List.range (M.bs.length - M.nL)).map fun j => pinOfCB (M.bs.getD (M.nL + j) default)

theorem boxes_length (M : CMeta) : M.boxes.length = M.nL := by simp [CMeta.boxes]

theorem pins_length (M : CMeta) : M.pins.length = M.bs.length - M.nL := by simp [CMeta.pins]

theorem getD_of_getElem? {M : CMeta} {i : Nat} {b : CBody} (hb : M.bs[i]? = some b) :
    M.bs.getD i default = b := by
  rw [List.getD_eq_getElem?_getD, hb]
  rfl

/-- **The layout check.**  Body `i` has `vi = 2i+1`; a free body's tilt is at `2·nb + 1 + i`, the
free bodies come first, and every root tilt cell lies in the fundamental domain `[0, 1]`.  A
decidable statement about the EMITTED body records, so a certificate whose generator ever changes
the numbering is rejected rather than misread. -/
def layoutOk (M : CMeta) : Bool :=
  (M.nL ≤ M.bs.length) &&
  (List.range M.bs.length).all fun i =>
    match M.bs[i]? with
    | none => false
    | some b => (b.vi == 2 * i + 1) && (b.free == decide (i < M.nL)) &&
        (!b.free || ((b.ti == 2 * M.bs.length + 1 + i) && (0 ≤ b.t0) && (b.t1 ≤ 1)))

theorem layoutOk_le {M : CMeta} (h : layoutOk M = true) : M.nL ≤ M.bs.length := by
  rw [layoutOk, Bool.and_eq_true, decide_eq_true_eq] at h
  exact h.1

theorem layoutOk_get {M : CMeta} {i : Nat} {b : CBody} (h : layoutOk M = true)
    (hb : M.bs[i]? = some b) :
    b.vi = 2 * i + 1 ∧ (b.free = true ↔ i < M.nL) ∧
      (b.free = true → b.ti = 2 * M.bs.length + 1 + i ∧ 0 ≤ b.t0 ∧ b.t1 ≤ 1) := by
  have hi : i < M.bs.length := by
    by_contra hc
    rw [List.getElem?_eq_none (by omega)] at hb
    simp at hb
  rw [layoutOk, Bool.and_eq_true, List.all_eq_true] at h
  have hmem : i ∈ List.range M.bs.length := List.mem_range.mpr hi
  have h2 := h.2 i hmem
  rw [hb] at h2
  simp only [Bool.and_eq_true, beq_iff_eq, Bool.or_eq_true, Bool.not_eq_true',
    decide_eq_true_eq] at h2
  obtain ⟨⟨hv, hfr⟩, hti⟩ := h2
  refine ⟨hv, ?_, ?_⟩
  · rw [hfr]; simp
  · intro hf
    rcases hti with hc | hc
    · rw [hf] at hc; exact absurd hc (by simp)
    · exact ⟨hc.1.1, hc.1.2, hc.2⟩

theorem bs_lt_of_getElem {M : CMeta} {i : Nat} {b : CBody} (hb : M.bs[i]? = some b) :
    i < M.bs.length := by
  by_contra hc
  rw [List.getElem?_eq_none (by omega)] at hb
  simp at hb

/-- **(R3) the variable index map.**  The LP variable vector of a configuration: the side, then
each body's centre (a pin's, relative to its nominal centre), then each free body's tilt. -/
noncomputable def certX (M : CMeta) (q : Nat → PSq) (s : ℝ) : Nat → ℝ :=
  fun j =>
    if j = 0 then s
    else if 2 * M.bs.length + 1 ≤ j then (q (j - (2 * M.bs.length + 1))).t
    else
      match M.bs[(j - 1) / 2]? with
      | none => 0
      | some b =>
          if (j - 1) % 2 = 0 then
            (q ((j - 1) / 2)).cx - (if b.free then 0 else (b.ax0 : ℝ) + (b.ax1 : ℝ) * s)
          else
            (q ((j - 1) / 2)).cy - (if b.free then 0 else (b.ay0 : ℝ) + (b.ay1 : ℝ) * s)

theorem certX_zero (M : CMeta) (q : Nat → PSq) (s : ℝ) : certX M q s 0 = s := by simp [certX]

theorem certX_tilt (M : CMeta) (q : Nat → PSq) (s : ℝ) (f : Nat) :
    certX M q s (2 * M.bs.length + 1 + f) = (q f).t := by
  have h1 : ¬ (2 * M.bs.length + 1 + f = 0) := by omega
  have h2 : 2 * M.bs.length + 1 ≤ 2 * M.bs.length + 1 + f := by omega
  have h3 : 2 * M.bs.length + 1 + f - (2 * M.bs.length + 1) = f := by omega
  simp only [certX, if_neg h1, if_pos h2, h3]

theorem certX_cx {M : CMeta} {q : Nat → PSq} {s : ℝ} {i : Nat} {b : CBody}
    (hb : M.bs[i]? = some b) :
    certX M q s (2 * i + 1) =
      (q i).cx - (if b.free then 0 else (b.ax0 : ℝ) + (b.ax1 : ℝ) * s) := by
  have hi : i < M.bs.length := bs_lt_of_getElem hb
  have h1 : ¬ (2 * i + 1 = 0) := by omega
  have h2 : ¬ (2 * M.bs.length + 1 ≤ 2 * i + 1) := by omega
  have h3 : (2 * i + 1 - 1) % 2 = 0 := by omega
  have h4 : (2 * i + 1 - 1) / 2 = i := by omega
  simp only [certX, if_neg h1, if_neg h2, h4, hb, h3]
  simp

theorem certX_cy {M : CMeta} {q : Nat → PSq} {s : ℝ} {i : Nat} {b : CBody}
    (hb : M.bs[i]? = some b) :
    certX M q s (2 * i + 2) =
      (q i).cy - (if b.free then 0 else (b.ay0 : ℝ) + (b.ay1 : ℝ) * s) := by
  have hi : i < M.bs.length := bs_lt_of_getElem hb
  have h1 : ¬ (2 * i + 2 = 0) := by omega
  have h2 : ¬ (2 * M.bs.length + 1 ≤ 2 * i + 2) := by omega
  have h3 : ¬ ((2 * i + 2 - 1) % 2 = 0) := by omega
  have h4 : (2 * i + 2 - 1) / 2 = i := by omega
  simp only [certX, if_neg h1, if_neg h2, h4, hb, if_neg h3]

/-! ## 4. The geometric bundle, and the per-body forms and enclosures

`LocalCertT2.localHyp_bodies` (C4's geometric half) hands one square per body in the
certificate's own order.  `GeoHyp` packages exactly what the row builder and the enclosures read
off it, and `geoHyp_of_localHyp` produces it. -/

/-- Everything the row builder and the selection enclosures consume from a configuration. -/
structure GeoHyp (M : CMeta) (q : Nat → PSq) (s : ℝ) : Prop where
  hbox : ∀ (i : Nat) (b : CBody), M.bs[i]? = some b → b.free = true → (boxOfCB b).mem (q i)
  hpin : ∀ (i : Nat) (b : CBody), M.bs[i]? = some b → b.free = false → (pinOfCB b).mem s (q i)
  hcont : ∀ i : Nat, i < M.bs.length → (q i).set ⊆ container s
  htilt : ∀ i : Nat, i < M.bs.length → 0 ≤ (q i).t ∧ (q i).t ≤ 1
  hdisj : ∀ i j : Nat, i < M.bs.length → j < M.bs.length → i ≠ j →
            Disjoint (interior (q i).set) (interior (q j).set)

theorem geoHyp_of_localHyp {M : CMeta} {s : ℝ} {z : Cfg} (hlay : layoutOk M = true)
    (hz : CfgPacking s z) (h : LocalHyp M.boxes M.pins s z) :
    ∃ q : Nat → PSq, GeoHyp M q s := by
  obtain ⟨q, hL, hP, hrest, hdis⟩ := localHyp_bodies hz h
  have hnL : M.nL ≤ M.bs.length := layoutOk_le hlay
  have hlen : M.boxes.length = M.nL := boxes_length M
  have hlenP : M.pins.length = M.bs.length - M.nL := pins_length M
  refine ⟨q, ?_, ?_, ?_, ?_, ?_⟩
  · intro i b hb hfree
    have hi : i < M.bs.length := bs_lt_of_getElem hb
    have hiL : i < M.nL := ((layoutOk_get hlay hb).2.1).mp hfree
    have hiB : i < M.boxes.length := by omega
    have hget : M.boxes.get ⟨i, hiB⟩ = boxOfCB b := by
      show M.boxes[i] = boxOfCB b
      have e : M.boxes[i] = boxOfCB (M.bs.getD i default) := by
        simp only [CMeta.boxes, List.getElem_map, List.getElem_range]
      rw [getD_of_getElem? hb] at e
      exact e
    rw [← hget]
    exact hL i hiB
  · intro i b hb hfree
    have hi : i < M.bs.length := bs_lt_of_getElem hb
    have hiL : ¬ i < M.nL := by
      intro hc
      have := ((layoutOk_get hlay hb).2.1).mpr hc
      rw [hfree] at this
      exact Bool.noConfusion this
    have hj : i - M.nL < M.pins.length := by omega
    have hget : M.pins.get ⟨i - M.nL, hj⟩ = pinOfCB b := by
      show M.pins[i - M.nL] = pinOfCB b
      have e : M.pins[i - M.nL] = pinOfCB (M.bs.getD (M.nL + (i - M.nL)) default) := by
        simp only [CMeta.pins, List.getElem_map, List.getElem_range]
      rw [show M.nL + (i - M.nL) = i by omega, getD_of_getElem? hb] at e
      exact e
    have hmem := hP (i - M.nL) hj
    rw [hget] at hmem
    rwa [show M.boxes.length + (i - M.nL) = i by omega] at hmem
  · intro i hi
    exact (hrest i (by omega)).2
  · intro i hi
    exact (hrest i (by omega)).1
  · intro i j hi hj hij
    exact hdis i j (by omega) (by omega) hij

/-! ### 4.1 The affine form of a body's centre and tilt

`certX` is a definition, so each of these is a two-line computation; they are the bridge between
`evalL` over the certificate's coefficient lists and the real quantities `relax_wall` and
`relax_selection` speak about. -/

/-- The affine form of body `i`'s centre abscissa.  For a pin the LP variable is the OFFSET, so
the nominal centre `α + β s` is added back. -/
def cenAffX (M : CMeta) (i : Nat) : Aff :=
  match M.bs[i]? with
  | none => aZero
  | some b => if b.free then aVar (2 * i + 1) 1
              else aAdd (aVar (2 * i + 1) 1) (aAdd (aVar 0 b.ax1) (aConst b.ax0))

/-- The affine form of body `i`'s centre ordinate. -/
def cenAffY (M : CMeta) (i : Nat) : Aff :=
  match M.bs[i]? with
  | none => aZero
  | some b => if b.free then aVar (2 * i + 2) 1
              else aAdd (aVar (2 * i + 2) 1) (aAdd (aVar 0 b.ay1) (aConst b.ay0))

/-- The affine form of body `i`'s tilt: its own variable if free, the constant `0` if a pin. -/
def tiltAff (M : CMeta) (i : Nat) : Aff :=
  match M.bs[i]? with
  | none => aZero
  | some b => if b.free then aVar (2 * M.bs.length + 1 + i) 1 else aZero

theorem cenAffX_val {M : CMeta} {q : Nat → PSq} {s : ℝ} {i : Nat} {b : CBody}
    (hb : M.bs[i]? = some b) : aVal (cenAffX M i) (certX M q s) = (q i).cx := by
  have hx := certX_cx (q := q) (s := s) hb
  cases hf : b.free with
  | true =>
    simp only [cenAffX, hb, hf, if_pos, aVal_var]
    rw [hf] at hx
    simp only [if_pos] at hx
    push_cast
    rw [hx]
    ring
  | false =>
    simp only [cenAffX, hb, hf, Bool.false_eq_true, if_false, aVal_add, aVal_var, aVal_const]
    rw [hf] at hx
    simp only [Bool.false_eq_true, if_false] at hx
    rw [hx, certX_zero]
    push_cast
    ring

theorem cenAffY_val {M : CMeta} {q : Nat → PSq} {s : ℝ} {i : Nat} {b : CBody}
    (hb : M.bs[i]? = some b) : aVal (cenAffY M i) (certX M q s) = (q i).cy := by
  have hx := certX_cy (q := q) (s := s) hb
  cases hf : b.free with
  | true =>
    simp only [cenAffY, hb, hf, if_pos, aVal_var]
    rw [hf] at hx
    simp only [if_pos] at hx
    push_cast
    rw [hx]
    ring
  | false =>
    simp only [cenAffY, hb, hf, Bool.false_eq_true, if_false, aVal_add, aVal_var, aVal_const]
    rw [hf] at hx
    simp only [Bool.false_eq_true, if_false] at hx
    rw [hx, certX_zero]
    push_cast
    ring

theorem tiltAff_val {M : CMeta} {q : Nat → PSq} {s : ℝ} {i : Nat} {b : CBody}
    (hg : GeoHyp M q s) (hb : M.bs[i]? = some b) :
    aVal (tiltAff M i) (certX M q s) = (q i).t := by
  cases hf : b.free with
  | true =>
    simp only [tiltAff, hb, hf, if_pos, aVal_var]
    rw [certX_tilt]
    push_cast
    ring
  | false =>
    have := (hg.hpin i b hb hf).2.2
    simp only [tiltAff, hb, hf, Bool.false_eq_true, if_false, aVal_zero]
    exact this.symm

/-! ### 4.2 Reading the current cell

The certificate's cells are `LocalCert.InBox`-shaped lists of rational bounds over ALL the LP
variables — the tree bisects only tilt coordinates, so the centre and side coordinates keep the
root's bounds — and `inBox_get` is the coordinatewise reader. -/

theorem inBox_get : ∀ (box : List (ℚ × ℚ)) (x : Nat → ℝ) (i j : Nat) (p : ℚ × ℚ),
    InBox box x i → box[j]? = some p → (p.1 : ℝ) ≤ x (i + j) ∧ x (i + j) ≤ (p.2 : ℝ) := by
  intro box
  induction box with
  | nil => intro x i j p _ h; simp at h
  | cons c t ih =>
    intro x i j p hb h
    obtain ⟨hlo, hhi, hrest⟩ := hb
    cases j with
    | zero =>
      simp only [List.getElem?_cons_zero, Option.some.injEq] at h
      subst h
      simpa using ⟨hlo, hhi⟩
    | succ n =>
      simp only [List.getElem?_cons_succ] at h
      have := ih x (i + 1) n p hrest h
      rwa [show i + 1 + n = i + (n + 1) by omega] at this

/-- The interval of the current cell at one coordinate. -/
def cellIQ (cur : List (ℚ × ℚ)) (j : Nat) : Option IQ :=
  match cur[j]? with
  | none => none
  | some p => some ⟨p.1, p.2⟩

theorem cellIQ_mem {cur : List (ℚ × ℚ)} {x : Nat → ℝ} {j : Nat} {I : IQ}
    (hb : InBox cur x 0) (h : cellIQ cur j = some I) : I.mem (x j) := by
  revert h
  cases hp : cur[j]? with
  | none => intro h; simp [cellIQ, hp] at h
  | some p =>
    intro h
    simp only [cellIQ, hp, Option.some.injEq] at h
    subst h
    have := inBox_get cur x 0 j p hb hp
    simpa [IQ.mem] using this

/-- Body `i`'s centre and tilt enclosures over the current cell: for a pin the centre interval is
the OFFSET interval shifted by `α + β s` with `s` ranging over the cell's side interval, and the
tilt cell is the single point `0`. -/
def bodyIQ (M : CMeta) (cur : List (ℚ × ℚ)) (i : Nat) : Option (IQ × IQ × IQ) :=
  match M.bs[i]?, cellIQ cur 0, cellIQ cur (2 * i + 1), cellIQ cur (2 * i + 2) with
  | some b, some sI, some cx, some cy =>
      if b.free then
        match cellIQ cur (2 * M.bs.length + 1 + i) with
        | none => none
        | some tI => some (cx, cy, tI)
      else
        some (IQ.add cx (IQ.add (IQ.mul (IQ.const b.ax1) sI) (IQ.const b.ax0)),
              IQ.add cy (IQ.add (IQ.mul (IQ.const b.ay1) sI) (IQ.const b.ay0)),
              ⟨0, 0⟩)
  | _, _, _, _ => none

theorem bodyIQ_mem {M : CMeta} {cur : List (ℚ × ℚ)} {i : Nat} {q : Nat → PSq} {s : ℝ}
    {X Y T : IQ} (hg : GeoHyp M q s) (hbox : InBox cur (certX M q s) 0)
    (h : bodyIQ M cur i = some (X, Y, T)) :
    X.mem (q i).cx ∧ Y.mem (q i).cy ∧ T.mem (q i).t := by
  revert h
  cases hb : M.bs[i]? with
  | none => intro h; simp [bodyIQ, hb] at h
  | some b =>
    cases hs : cellIQ cur 0 with
    | none => intro h; simp [bodyIQ, hb, hs] at h
    | some sI =>
      cases hcx : cellIQ cur (2 * i + 1) with
      | none => intro h; simp [bodyIQ, hb, hs, hcx] at h
      | some cx =>
        cases hcy : cellIQ cur (2 * i + 2) with
        | none => intro h; simp [bodyIQ, hb, hs, hcx, hcy] at h
        | some cy =>
          have hmx : cx.mem (certX M q s (2 * i + 1)) := cellIQ_mem hbox hcx
          have hmy : cy.mem (certX M q s (2 * i + 2)) := cellIQ_mem hbox hcy
          have hms : sI.mem (certX M q s 0) := cellIQ_mem hbox hs
          rw [certX_zero] at hms
          cases hf : b.free with
          | true =>
            cases ht : cellIQ cur (2 * M.bs.length + 1 + i) with
            | none => intro h; simp [bodyIQ, hb, hs, hcx, hcy, hf, ht] at h
            | some tI =>
              intro h
              simp only [bodyIQ, hb, hs, hcx, hcy, hf, ht, if_pos,
                Option.some.injEq, Prod.mk.injEq] at h
              obtain ⟨e1, e2, e3⟩ := h
              subst e1; subst e2; subst e3
              rw [certX_cx hb, hf] at hmx
              rw [certX_cy hb, hf] at hmy
              simp only [if_pos, sub_zero] at hmx hmy
              refine ⟨hmx, hmy, ?_⟩
              have := cellIQ_mem hbox ht
              rwa [certX_tilt] at this
          | false =>
            intro h
            simp only [bodyIQ, hb, hs, hcx, hcy, hf, Bool.false_eq_true, if_false,
              Option.some.injEq, Prod.mk.injEq] at h
            obtain ⟨e1, e2, e3⟩ := h
            subst e1; subst e2; subst e3
            rw [certX_cx hb, hf] at hmx
            rw [certX_cy hb, hf] at hmy
            simp only [Bool.false_eq_true, if_false] at hmx hmy
            have hpin := hg.hpin i b hb hf
            refine ⟨?_, ?_, ?_⟩
            · have hv := IQ.add_mem hmx
                (IQ.add_mem (IQ.mul_mem (IQ.const_mem b.ax1) hms) (IQ.const_mem b.ax0))
              have e : (q i).cx - ((b.ax0 : ℝ) + (b.ax1 : ℝ) * s)
                  + ((b.ax1 : ℝ) * s + (b.ax0 : ℝ)) = (q i).cx := by ring
              rwa [e] at hv
            · have hv := IQ.add_mem hmy
                (IQ.add_mem (IQ.mul_mem (IQ.const_mem b.ay1) hms) (IQ.const_mem b.ay0))
              have e : (q i).cy - ((b.ay0 : ℝ) + (b.ay1 : ℝ) * s)
                  + ((b.ay1 : ℝ) * s + (b.ay0 : ℝ)) = (q i).cy := by ring
              rwa [e] at hv
            · rw [hpin.2.2]
              exact ⟨by norm_num, by norm_num⟩

/-- The `PairBox` of two bodies over the current cell. -/
def pairBoxOf (M : CMeta) (cur : List (ℚ × ℚ)) (i j : Nat) : Option PairBox :=
  match bodyIQ M cur i, bodyIQ M cur j with
  | some (xw, yw, tw), some (xo, yo, tb) => some ⟨xw, yw, tw, xo, yo, tb⟩
  | _, _ => none

theorem pairBoxOf_holds {M : CMeta} {cur : List (ℚ × ℚ)} {i j : Nat} {q : Nat → PSq} {s : ℝ}
    {pb : PairBox} (hg : GeoHyp M q s) (hbox : InBox cur (certX M q s) 0)
    (h : pairBoxOf M cur i j = some pb) : pb.holds (q i) (q j) := by
  revert h
  cases h1 : bodyIQ M cur i with
  | none => intro h; simp [pairBoxOf, h1] at h
  | some w =>
    cases h2 : bodyIQ M cur j with
    | none => intro h; simp [pairBoxOf, h1, h2] at h
    | some o =>
      intro h
      obtain ⟨xw, yw, tw⟩ := w
      obtain ⟨xo, yo, tb⟩ := o
      simp only [pairBoxOf, h1, h2, Option.some.injEq] at h
      subst h
      obtain ⟨a1, a2, a3⟩ := bodyIQ_mem hg hbox h1
      obtain ⟨b1, b2, b3⟩ := bodyIQ_mem hg hbox h2
      exact ⟨a1, a2, a3, b1, b2, b3⟩

/-- The decidable half of `PairBox.ok`: both tilt cells lie in the fundamental domain. -/
def pbOkB (pb : PairBox) : Bool :=
  (0 ≤ pb.tw.lo) && (pb.tw.hi ≤ 1) && (0 ≤ pb.tb.lo) && (pb.tb.hi ≤ 1)

theorem pbOkB_sound {pb : PairBox} (h : pbOkB pb = true) : pb.ok := by
  simp only [pbOkB, Bool.and_eq_true, decide_eq_true_eq] at h
  exact ⟨h.1.1.1, h.1.1.2, h.1.2, h.2⟩

/-! ## 5. (R2) The reflected row builder

The certificate records, once per distinct cell, the affine ENVELOPE each row family consumes
together with the positivity certificate that proves it (`gen_local_t2.build_pcert`).  §5.1
reflects those three tables and checks them; §5.2 and §5.3 build the two row families and prove
each built row holds on the cell.  The emitted (quantised) rows are then matched against these by
`affImplies` — §2 — and nothing about the rounding is re-derived. -/

/-! ### 5.1 The three envelope tables

Each is a list of entries keyed by the CELL the envelope is stated on, and each is checked once,
by the positivity machinery of `LocalCertT` / `LocalCertT2`, before any row is built. -/

/-- The wall-chord table: the tilt cell, the chord `(m, c)`, its positivity chain. -/
abbrev HEnv := List ((ℚ × ℚ) × (ℚ × ℚ) × List (ℚ × ℚ × Poly))

def hEnvOk : HEnv → Bool
  | [] => true
  | e :: t => posChain (hPoly e.2.1.1 e.2.1.2) e.2.2 e.1.1 e.1.2 && hEnvOk t

def hLookup : HEnv → (ℚ × ℚ) → Option (ℚ × ℚ)
  | [], _ => none
  | e :: t, cell => if e.1 = cell then some e.2.1 else hLookup t cell

theorem hLookup_sound : ∀ (E : HEnv) (cell : ℚ × ℚ) (mc : ℚ × ℚ) (t : ℝ),
    hEnvOk E = true → hLookup E cell = some mc →
    ((cell.1 : ℚ) : ℝ) ≤ t → t ≤ ((cell.2 : ℚ) : ℝ) →
    (mc.1 : ℝ) * t + (mc.2 : ℝ) ≤ wT t / 2 := by
  intro E
  induction E with
  | nil => intro cell mc t _ h _ _; simp [hLookup] at h
  | cons e T ih =>
    intro cell mc t hok h h1 h2
    rw [hEnvOk, Bool.and_eq_true] at hok
    by_cases hc : e.1 = cell
    · rw [hLookup, if_pos hc, Option.some.injEq] at h
      subst h
      subst hc
      exact wT_ge_aff hok.1 h1 h2
    · rw [hLookup, if_neg hc] at h
      exact ih cell mc t hok.2 h h1 h2

/-- One entry of the `S` table: the owner's tilt cell, the affine envelope of
`S(t) = sin(θ(t) − θ(t*))`, its two CONSTANT corners and the correction constant `K`, each with
its own positivity chain.  `t* = (a+b)/2` is the cell midpoint, computed rather than recorded, so
that the certificate cannot disagree with the polynomial the check compares against. -/
structure SEntry where
  cell : ℚ × ℚ
  alpha : ℚ
  bup : ℚ
  blo : ℚ
  slo : ℚ
  shi : ℚ
  kk : ℚ
  cUp : List (ℚ × ℚ × Poly)
  cLo : List (ℚ × ℚ × Poly)
  cHi : List (ℚ × ℚ × Poly)
  cLoC : List (ℚ × ℚ × Poly)
  cCorr : List (ℚ × ℚ × Poly)
deriving Inhabited, Repr

/-- The cell midpoint `t*`, and the rational `cos θ*`, `sin θ*` it determines. -/
def SEntry.tm (e : SEntry) : ℚ := (e.cell.1 + e.cell.2) / 2

def sEntryOk (e : SEntry) : Bool :=
  posChain (sUpPoly (cosTQ e.tm) (sinTQ e.tm) e.alpha e.bup) e.cUp e.cell.1 e.cell.2 &&
  posChain (sLoPoly (cosTQ e.tm) (sinTQ e.tm) e.alpha e.blo) e.cLo e.cell.1 e.cell.2 &&
  posChain (sUpPoly (cosTQ e.tm) (sinTQ e.tm) 0 e.shi) e.cHi e.cell.1 e.cell.2 &&
  posChain (sLoPoly (cosTQ e.tm) (sinTQ e.tm) 0 e.slo) e.cLoC e.cell.1 e.cell.2 &&
  posChain (cPoly (cosTQ e.tm) (sinTQ e.tm) e.kk) e.cCorr e.cell.1 e.cell.2 &&
  (0 ≤ e.kk)

abbrev SEnv := List SEntry

def sEnvOk : SEnv → Bool
  | [] => true
  | e :: t => sEntryOk e && sEnvOk t

def sLookup : SEnv → (ℚ × ℚ) → Option SEntry
  | [], _ => none
  | e :: t, cell => if e.cell = cell then some e else sLookup t cell

theorem sLookup_ok : ∀ (E : SEnv) (cell : ℚ × ℚ) (e : SEntry),
    sEnvOk E = true → sLookup E cell = some e → sEntryOk e = true ∧ e.cell = cell := by
  intro E
  induction E with
  | nil => intro cell e _ h; simp [sLookup] at h
  | cons f T ih =>
    intro cell e hok h
    rw [sEnvOk, Bool.and_eq_true] at hok
    by_cases hc : f.cell = cell
    · rw [sLookup, if_pos hc, Option.some.injEq] at h
      subst h
      exact ⟨hok.1, hc⟩
    · rw [sLookup, if_neg hc] at h
      exact ih cell e hok.2 h

/-- The positivity certificate of one `w` envelope.  A pin's tilt cell is the single point
`t = 0`, so the bivariate test degenerates on one side and is replaced by the substituted
univariate one (`LocalCertT2.substY0` / `substX0`). -/
inductive WCert where
  | xy (g : List (ℚ × ℚ × List (ℚ × ℚ × List Poly)))
  | subY (pcs : List (ℚ × ℚ × Poly))
  | subX (pcs : List (ℚ × ℚ × Poly))
deriving Inhabited, Repr

/-- One entry of the `w` table: the branch sign, the two tilt cells, the plane and its
certificate. -/
structure WEntry where
  eps : ℚ
  cw : ℚ × ℚ
  cb : ℚ × ℚ
  mw : ℚ
  mo : ℚ
  cc : ℚ
  cert : WCert
deriving Inhabited, Repr

def wEntryOk (e : WEntry) : Bool :=
  ((e.eps == 1) || (e.eps == -1)) &&
  (match e.cert with
   | .xy g => posGrid (wPolyT e.eps e.mw e.mo e.cc) g e.cw.1 e.cw.2 e.cb.1 e.cb.2
   | .subY pcs => (e.cb.1 == 0) && (e.cb.2 == 0) &&
       posChain (padZ 5 (substY0 (wPolyT e.eps e.mw e.mo e.cc))) pcs e.cw.1 e.cw.2
   | .subX pcs => (e.cw.1 == 0) && (e.cw.2 == 0) &&
       posChain (substX0 (wPolyT e.eps e.mw e.mo e.cc)) pcs e.cb.1 e.cb.2)

/-- **The `w` envelope, as the row builder consumes it.**  A checked entry gives a certified
plane below `w` on the cell product, by `LocalCertT2.wrel_ge_plane`. -/
theorem wEntry_sound {e : WEntry} {qw qo : PSq} (hok : wEntryOk e = true)
    (h1 : ((e.cw.1 : ℚ) : ℝ) ≤ qw.t) (h2 : qw.t ≤ ((e.cw.2 : ℚ) : ℝ))
    (h3 : ((e.cb.1 : ℚ) : ℝ) ≤ qo.t) (h4 : qo.t ≤ ((e.cb.2 : ℚ) : ℝ)) :
    (e.mw : ℝ) * qw.t + (e.mo : ℝ) * qo.t + (e.cc : ℝ) ≤ wrel qw qo := by
  rw [wEntryOk, Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq, beq_iff_eq] at hok
  obtain ⟨heps, hcert⟩ := hok
  refine wrel_ge_plane heps qw qo ?_
  cases hc : e.cert with
  | xy g =>
    rw [hc] at hcert
    exact posGrid_sound g e.cw.1 e.cw.2 e.cb.1 e.cb.2 qw.t qo.t hcert h1 h2 h3 h4
  | subY pcs =>
    rw [hc] at hcert
    simp only [Bool.and_eq_true, beq_iff_eq] at hcert
    obtain ⟨⟨hz1, hz2⟩, hch⟩ := hcert
    have hzero : qo.t = 0 := by
      rw [hz1] at h3; rw [hz2] at h4
      push_cast at h3 h4
      linarith
    have := posChain_sound pcs e.cw.1 e.cw.2 qw.t hch h1 h2
    rw [peval_padZ, peval_substY0] at this
    rw [hzero]
    exact this
  | subX pcs =>
    rw [hc] at hcert
    simp only [Bool.and_eq_true, beq_iff_eq] at hcert
    obtain ⟨⟨hz1, hz2⟩, hch⟩ := hcert
    have hzero : qw.t = 0 := by
      rw [hz1] at h1; rw [hz2] at h2
      push_cast at h1 h2
      linarith
    have := posChain_sound pcs e.cb.1 e.cb.2 qo.t hch h3 h4
    rw [peval_substX0] at this
    rw [hzero]
    exact this

abbrev WEnv := List WEntry

def wEnvOk : WEnv → Bool
  | [] => true
  | e :: t => wEntryOk e && wEnvOk t

def wLookup : WEnv → ℚ → (ℚ × ℚ) → (ℚ × ℚ) → Option WEntry
  | [], _, _, _ => none
  | e :: t, eps, cw, cb =>
      if e.eps = eps ∧ e.cw = cw ∧ e.cb = cb then some e else wLookup t eps cw cb

theorem wLookup_ok : ∀ (E : WEnv) (eps : ℚ) (cw cb : ℚ × ℚ) (e : WEntry),
    wEnvOk E = true → wLookup E eps cw cb = some e →
    wEntryOk e = true ∧ e.cw = cw ∧ e.cb = cb := by
  intro E
  induction E with
  | nil => intro eps cw cb e _ h; simp [wLookup] at h
  | cons f T ih =>
    intro eps cw cb e hok h
    rw [wEnvOk, Bool.and_eq_true] at hok
    by_cases hc : f.eps = eps ∧ f.cw = cw ∧ f.cb = cb
    · rw [wLookup, if_pos hc, Option.some.injEq] at h
      subst h
      exact ⟨hok.1, hc.2.1, hc.2.2⟩
    · rw [wLookup, if_neg hc] at h
      exact ih eps cw cb e hok.2 h

/-! ### 5.2 The wall family

`Parametrize.set_subset_container_iff` — `Q ⊆ [0,s]² ⟺ w_T(t)/2 ≤ c ≤ s − w_T(t)/2` in each
coordinate — plus a certified chord below `w_T(t)/2` gives the four rows of one body. -/

/-- The wall rows from a chord, with no certificate hypothesis: the pin case (`t = 0`, the exact
chord `1/2`) and the free case go through the same statement. -/
theorem wall_of_chord {q : PSq} {s m c : ℝ} (hch : m * q.t + c ≤ wT q.t / 2)
    (h0 : 0 ≤ q.t) (h1 : q.t ≤ 1) (hsub : q.set ⊆ container s) :
    (-q.cx + (m * q.t + c) ≤ 0 ∧ q.cx - s + (m * q.t + c) ≤ 0) ∧
    (-q.cy + (m * q.t + c) ≤ 0 ∧ q.cy - s + (m * q.t + c) ≤ 0) := by
  obtain ⟨hx0, hx1, hy0, hy1⟩ := (set_subset_container_iff h0 h1 s).mp hsub
  exact ⟨⟨by linarith, by linarith⟩, ⟨by linarith, by linarith⟩⟩

/-- `w_T(0) = 1`: a pin's exact chord is the constant `1/2`. -/
theorem wT_zero : wT 0 = 1 := by
  unfold wT cosT sinT
  norm_num

/-- The four wall rows of body `i` for the chord `m t + c`. -/
def wallRows (M : CMeta) (i : Nat) (m c : ℚ) : List Aff :=
  let hb := aAdd (aSmul m (tiltAff M i)) (aConst c)
  let X := cenAffX M i
  let Y := cenAffY M i
  [aAdd (aSmul (-1) X) hb, aAdd (aAdd X (aVar 0 (-1))) hb,
   aAdd (aSmul (-1) Y) hb, aAdd (aAdd Y (aVar 0 (-1))) hb]

/-- The wall rows of body `i` over the current cell, with the chord read from the table. -/
def wallOf (M : CMeta) (E : HEnv) (cur : List (ℚ × ℚ)) (i : Nat) : Option (List Aff) :=
  match M.bs[i]? with
  | none => none
  | some b =>
      if b.free then
        match cur[2 * M.bs.length + 1 + i]? with
        | none => none
        | some cell => (hLookup E cell).map fun mc => wallRows M i mc.1 mc.2
      else some (wallRows M i 0 (1 / 2))

/-- **The wall family of Lemma RELAX, reflected.**  Every row `wallOf` builds holds at the
configuration's variable vector. -/
theorem wallOf_sound {M : CMeta} {E : HEnv} {cur : List (ℚ × ℚ)} {i : Nat} {q : Nat → PSq}
    {s : ℝ} {rs : List Aff} (hg : GeoHyp M q s) (hok : hEnvOk E = true)
    (hbox : InBox cur (certX M q s) 0) (h : wallOf M E cur i = some rs) :
    ∀ r ∈ rs, aVal r (certX M q s) ≤ 0 := by
  revert h
  cases hb : M.bs[i]? with
  | none => intro h; simp [wallOf, hb] at h
  | some b =>
    have hi : i < M.bs.length := bs_lt_of_getElem hb
    have ht01 := hg.htilt i hi
    have hcont := hg.hcont i hi
    have hcx := cenAffX_val (q := q) (s := s) hb
    have hcy := cenAffY_val (q := q) (s := s) hb
    have htv := tiltAff_val (q := q) (s := s) hg hb
    -- one common tail: from a chord bound to the four rows
    have key : ∀ m c : ℚ, ((m : ℝ) * (q i).t + (c : ℝ) ≤ wT (q i).t / 2) →
        ∀ r ∈ wallRows M i m c, aVal r (certX M q s) ≤ 0 := by
      intro m c hch r hr
      obtain ⟨⟨w1, w2⟩, w3, w4⟩ := wall_of_chord hch ht01.1 ht01.2 hcont
      have hx0 : certX M q s 0 = s := certX_zero M q s
      simp only [wallRows, List.mem_cons, List.not_mem_nil, or_false] at hr
      rcases hr with rfl | rfl | rfl | rfl
      · simp only [aVal_add, aVal_smul, aVal_const, hcx, htv]
        push_cast
        linarith
      · simp only [aVal_add, aVal_smul, aVal_const, aVal_var, hcx, htv, hx0]
        push_cast
        linarith
      · simp only [aVal_add, aVal_smul, aVal_const, hcy, htv]
        push_cast
        linarith
      · simp only [aVal_add, aVal_smul, aVal_const, aVal_var, hcy, htv, hx0]
        push_cast
        linarith
    cases hf : b.free with
    | false =>
      intro h
      simp only [wallOf, hb, hf, Bool.false_eq_true, if_false, Option.some.injEq] at h
      subst h
      refine key 0 (1 / 2) ?_
      have hz : (q i).t = 0 := (hg.hpin i b hb hf).2.2
      rw [hz, wT_zero]
      norm_num
    | true =>
      cases hc : cur[2 * M.bs.length + 1 + i]? with
      | none => intro h; simp [wallOf, hb, hf, hc] at h
      | some cell =>
        cases hl : hLookup E cell with
        | none => intro h; simp [wallOf, hb, hf, hc, hl] at h
        | some mc =>
          intro h
          simp only [wallOf, hb, hf, hc, hl, if_pos, Option.map_some,
            Option.some.injEq] at h
          subst h
          refine key mc.1 mc.2 ?_
          have hmem := inBox_get cur (certX M q s) 0 (2 * M.bs.length + 1 + i) cell hbox hc
          rw [Nat.zero_add, certX_tilt] at hmem
          exact hLookup_sound E cell mc (q i).t hok hl hmem.1 hmem.2

/-! ### 5.3 The selection family

`LocalCertT2.relax_selection` is the whole of Lemma RELAX for this family: given the selection's
own row `g_σ ≥ 0`, the exact axis decomposition, the correction bound, ONE of the three `Q·S`
envelopes and a certified plane below `w`, the emitted row holds.  What is written here is the
assembly of the affine forms `P`, `Q`, `U`, `W_lb` those five hypotheses speak about, and the
proof that the certificate's own recorded constants supply them. -/

/-- The exact minimum of an affine form over a box. -/
def affMin (u : Aff) (box : List (ℚ × ℚ)) : Option ℚ := (minL u.1 box).map fun v => v + u.2

/-- The exact maximum. -/
def affMax (u : Aff) (box : List (ℚ × ℚ)) : Option ℚ :=
  (minL (smulL (-1) u.1) box).map fun v => -v + u.2

theorem affMin_le {u : Aff} {box : List (ℚ × ℚ)} {v : ℚ} {x : Nat → ℝ}
    (h : affMin u box = some v) (hb : InBox box x 0) : (v : ℝ) ≤ aVal u x := by
  revert h
  cases hm : minL u.1 box with
  | none => intro h; simp [affMin, hm] at h
  | some w =>
    intro h
    simp only [affMin, hm, Option.map_some, Option.some.injEq] at h
    subst h
    have := minL_le _ _ _ x 0 hm hb
    simp only [aVal]
    push_cast
    linarith

theorem le_affMax {u : Aff} {box : List (ℚ × ℚ)} {v : ℚ} {x : Nat → ℝ}
    (h : affMax u box = some v) (hb : InBox box x 0) : aVal u x ≤ (v : ℝ) := by
  revert h
  cases hm : minL (smulL (-1) u.1) box with
  | none => intro h; simp [affMax, hm] at h
  | some w =>
    intro h
    simp only [affMax, hm, Option.map_some, Option.some.injEq] at h
    subst h
    have := minL_le _ _ _ x 0 hm hb
    rw [evalL_smulL] at this
    simp only [aVal]
    push_cast at this ⊢
    linarith

/-- The tilt cell of a body over the current cell: its own cell if free, the point `0` if a
pin. -/
def tcellOf (M : CMeta) (cur : List (ℚ × ℚ)) (i : Nat) : Option (ℚ × ℚ) :=
  match M.bs[i]? with
  | none => none
  | some b => if b.free then cur[2 * M.bs.length + 1 + i]? else some (0, 0)

theorem tcellOf_mem {M : CMeta} {cur : List (ℚ × ℚ)} {i : Nat} {q : Nat → PSq} {s : ℝ}
    {cell : ℚ × ℚ} (hg : GeoHyp M q s) (hbox : InBox cur (certX M q s) 0)
    (h : tcellOf M cur i = some cell) :
    ((cell.1 : ℚ) : ℝ) ≤ (q i).t ∧ (q i).t ≤ ((cell.2 : ℚ) : ℝ) := by
  revert h
  cases hb : M.bs[i]? with
  | none => intro h; simp [tcellOf, hb] at h
  | some b =>
    cases hf : b.free with
    | false =>
      intro h
      simp only [tcellOf, hb, hf, Bool.false_eq_true, if_false, Option.some.injEq] at h
      subst h
      have := (hg.hpin i b hb hf).2.2
      rw [this]
      norm_num
    | true =>
      cases hc : cur[2 * M.bs.length + 1 + i]? with
      | none => intro h; simp [tcellOf, hb, hf, hc] at h
      | some p =>
        intro h
        simp only [tcellOf, hb, hf, if_pos, hc, Option.some.injEq] at h
        subst h
        have := inBox_get cur (certX M q s) 0 (2 * M.bs.length + 1 + i) p hbox hc
        rwa [Nat.zero_add, certX_tilt] at this

theorem cosRel_self (t : ℝ) : cosRel t t = 1 := by
  have := cosT_sq_add_sinT_sq t
  unfold cosRel
  nlinarith [this]

theorem sRel_self (t : ℝ) : sRel (cosT t) (sinT t) t = 0 := by
  unfold sRel
  ring

/-- Two squares with tilt `0` have `w = 1`; only `1 ≤ w` is needed. -/
theorem wrel_ge_one_of_zero {qw qo : PSq} (h1 : qw.t = 0) (h2 : qo.t = 0) : 1 ≤ wrel qw qo := by
  have hs := wrel_ge_sub qw qo
  have hc : cosRel qw.t qo.t = 1 := by rw [h1, h2]; unfold cosRel cosT sinT; norm_num
  have hn : sinRel qw.t qo.t = 0 := by rw [h1, h2]; unfold sinRel cosT sinT; norm_num
  rw [hc, hn] at hs
  linarith

/-! #### The pieces of one selection's rows -/

/-- The two centre differences `c_o − c_w` as affine forms. -/
def dAffX (M : CMeta) (iw io : Nat) : Aff := aSub (cenAffX M io) (cenAffX M iw)
def dAffY (M : CMeta) (iw io : Nat) : Aff := aSub (cenAffY M io) (cenAffY M iw)

/-- The owner's axis at the cell MIDPOINT, exactly, as a pair of rationals. -/
def axQ (tm : ℚ) (k : Bool) : ℚ × ℚ :=
  if k then (-(sinTQ tm), cosTQ tm) else (cosTQ tm, sinTQ tm)

theorem axQ_cast (tm : ℚ) (k : Bool) :
    (((axQ tm k).1 : ℚ) : ℝ) = (axk ⟨0, 0, ((tm : ℚ) : ℝ)⟩ k).1 ∧
    (((axQ tm k).2 : ℚ) : ℝ) = (axk ⟨0, 0, ((tm : ℚ) : ℝ)⟩ k).2 := by
  cases k
  · simp only [axQ, axk, Bool.false_eq_true, if_false]
    exact ⟨cosTQ_cast tm, sinTQ_cast tm⟩
  · simp only [axQ, axk, if_pos]
    refine ⟨?_, cosTQ_cast tm⟩
    push_cast
    rw [sinTQ_cast tm]

/-- `P = ε d·a_k(θ*)`. -/
def selP (M : CMeta) (iw io : Nat) (tm : ℚ) (k : Bool) (eps : ℚ) : Aff :=
  aSmul eps (aAdd (aSmul (axQ tm k).1 (dAffX M iw io)) (aSmul (axQ tm k).2 (dAffY M iw io)))

/-- `Q = ε d·a_k(θ* + 90°)`. -/
def selQ (M : CMeta) (iw io : Nat) (tm : ℚ) (k : Bool) (eps : ℚ) : Aff :=
  aSmul eps (aAdd (aSmul (-(axQ tm k).2) (dAffX M iw io)) (aSmul (axQ tm k).1 (dAffY M iw io)))

/-- One certified plane below `w`, as an affine form in the two tilt variables. -/
def wAff (M : CMeta) (iw io : Nat) (mw mo c : ℚ) : Aff :=
  aAdd (aSmul mw (tiltAff M iw)) (aAdd (aSmul mo (tiltAff M io)) (aConst c))

/-- The three `Q·S` envelopes of Lemma RELAX: the chord of `|Q|` times the chord scale of `S`,
and the two McCormick planes with `S` replaced by the affine envelope the multiplier's sign
selects. -/
def usOf (Q Sup Sdn : Aff) (qlo qhi slo shi : ℚ) : List Aff :=
  let mq : ℚ := if 0 ≤ qlo then 1 else if qhi ≤ 0 then -1 else (qhi + qlo) / (qhi - qlo)
  let cq : ℚ := if 0 ≤ qlo then 0 else if qhi ≤ 0 then 0 else -2 * qlo * qhi / (qhi - qlo)
  [aSmul (max |slo| |shi|) (aAdd (aSmul mq Q) (aConst cq)),
   aAdd (aSmul qhi (if 0 ≤ qhi then Sup else Sdn)) (aAdd (aSmul slo Q) (aConst (-(qhi * slo)))),
   aAdd (aSmul qlo (if 0 ≤ qlo then Sup else Sdn)) (aAdd (aSmul shi Q) (aConst (-(qlo * shi))))]

theorem usOf_sound {Q Sup Sdn : Aff} {qlo qhi slo shi : ℚ} {x : Nat → ℝ} {Sv : ℝ}
    (hql : (qlo : ℝ) ≤ aVal Q x) (hqh : aVal Q x ≤ (qhi : ℝ))
    (hsl : (slo : ℝ) ≤ Sv) (hsh : Sv ≤ (shi : ℝ))
    (hup : Sv ≤ aVal Sup x) (hdn : aVal Sdn x ≤ Sv) :
    ∀ U ∈ usOf Q Sup Sdn qlo qhi slo shi, aVal Q x * Sv ≤ aVal U x := by
  intro U hU
  have habs : |Sv| ≤ ((max |slo| |shi| : ℚ) : ℝ) := by
    push_cast
    refine abs_le.mpr ⟨?_, ?_⟩
    · have h1 : -|(slo : ℝ)| ≤ (slo : ℝ) := neg_abs_le _
      have h2 : -max |(slo : ℝ)| |(shi : ℝ)| ≤ -|(slo : ℝ)| := by
        simp only [neg_le_neg_iff]
        exact le_max_left _ _
      linarith
    · have h1 : (shi : ℝ) ≤ |(shi : ℝ)| := le_abs_self _
      have h2 : |(shi : ℝ)| ≤ max |(slo : ℝ)| |(shi : ℝ)| := le_max_right _ _
      linarith
  simp only [usOf, List.mem_cons, List.not_mem_nil, or_false] at hU
  rcases hU with rfl | rfl | rfl
  · -- envelope (A)
    have hchord : |aVal Q x| ≤
        ((if 0 ≤ qlo then (1 : ℚ) else if qhi ≤ 0 then -1 else (qhi + qlo) / (qhi - qlo) : ℚ) : ℝ)
          * aVal Q x
        + ((if 0 ≤ qlo then (0 : ℚ) else if qhi ≤ 0 then 0 else
              -2 * qlo * qhi / (qhi - qlo) : ℚ) : ℝ) := by
      by_cases h1 : (0 : ℚ) ≤ qlo
      · have h1' : (0 : ℝ) ≤ (qlo : ℝ) := by exact_mod_cast h1
        rw [if_pos h1, if_pos h1]
        rw [abs_of_nonneg (by linarith)]
        push_cast
        linarith
      · by_cases h2 : qhi ≤ (0 : ℚ)
        · have h2' : (qhi : ℝ) ≤ 0 := by exact_mod_cast h2
          rw [if_neg h1, if_pos h2, if_neg h1, if_pos h2]
          rw [abs_of_nonpos (by linarith)]
          push_cast
          linarith
        · have hl : (qlo : ℝ) < 0 := by
            have : ¬ (0 : ℚ) ≤ qlo := h1
            push_cast
            exact_mod_cast lt_of_not_ge this
          have hh : (0 : ℝ) < (qhi : ℝ) := by
            have : ¬ qhi ≤ (0 : ℚ) := h2
            exact_mod_cast lt_of_not_ge this
          rw [if_neg h1, if_neg h2, if_neg h1, if_neg h2]
          have := absQ_chord hql hqh hl hh
          push_cast
          exact this
    have := relax_U_A (Qv := aVal Q x) (Sv := Sv) habs hchord
    simp only [aVal_smul, aVal_add, aVal_const]
    push_cast at this ⊢
    linarith
  · -- envelope (B1)
    by_cases h : (0 : ℚ) ≤ qhi
    · have h' : (0 : ℝ) ≤ (qhi : ℝ) := by exact_mod_cast h
      have := relax_U_B1 (Qv := aVal Q x) (Sv := Sv) (qh := (qhi : ℝ)) (Slo := (slo : ℝ))
        (Senv := aVal Sup x) hqh hsl (by rw [if_pos h']; exact hup)
      simp only [if_pos h, aVal_add, aVal_smul, aVal_const]
      push_cast at this ⊢
      linarith
    · have h' : ¬ (0 : ℝ) ≤ (qhi : ℝ) := by
        intro hc; exact h (by exact_mod_cast hc)
      have := relax_U_B1 (Qv := aVal Q x) (Sv := Sv) (qh := (qhi : ℝ)) (Slo := (slo : ℝ))
        (Senv := aVal Sdn x) hqh hsl (by rw [if_neg h']; exact hdn)
      simp only [if_neg h, aVal_add, aVal_smul, aVal_const]
      push_cast at this ⊢
      linarith
  · -- envelope (B2)
    by_cases h : (0 : ℚ) ≤ qlo
    · have h' : (0 : ℝ) ≤ (qlo : ℝ) := by exact_mod_cast h
      have := relax_U_B2 (Qv := aVal Q x) (Sv := Sv) (ql := (qlo : ℝ)) (Shi := (shi : ℝ))
        (Senv := aVal Sup x) hql hsh (by rw [if_pos h']; exact hup)
      simp only [if_pos h, aVal_add, aVal_smul, aVal_const]
      push_cast at this ⊢
      linarith
    · have h' : ¬ (0 : ℝ) ≤ (qlo : ℝ) := by
        intro hc; exact h (by exact_mod_cast hc)
      have := relax_U_B2 (Qv := aVal Q x) (Sv := Sv) (ql := (qlo : ℝ)) (Shi := (shi : ℝ))
        (Senv := aVal Sdn x) hql hsh (by rw [if_neg h']; exact hdn)
      simp only [if_neg h, aVal_add, aVal_smul, aVal_const]
      push_cast at this ⊢
      linarith

/-! #### The assembled context and its rows -/

/-- Everything one fixed selection contributes: the two affine forms of the decomposition, the
correction constant, the `Q·S` envelopes and the certified planes below `w`. -/
structure SelCtx where
  P : Aff
  Q : Aff
  corr : ℚ
  Us : List Aff
  Ws : List Aff

/-- The rows: one per (`w` branch, `U` envelope) pair, exactly `gen_local_t.RowsT._selection`. -/
def selRowsOfCtx (c : SelCtx) : List Aff :=
  c.Ws.flatMap fun W =>
    c.Us.map fun U =>
      aSub (aSub (aAdd (aSmul (1 / 2) W) (aConst (1 / 2 - c.corr))) c.P) U

/-- **(C3) assembled.**  With the five hypotheses `relax_selection` consumes, every row of the
selection family holds. -/
theorem selRowsOfCtx_sound {c : SelCtx} {x : Nat → ℝ} {qw qo : PSq} {k : Bool} {eps Cv Sv : ℝ}
    (hgs : 0 ≤ gsel qw qo k eps)
    (hdec : aVal c.P x * Cv + aVal c.Q x * Sv
      = eps * ((qo.cx - qw.cx) * (axk qw k).1 + (qo.cy - qw.cy) * (axk qw k).2))
    (hcor : aVal c.P x * Cv ≤ aVal c.P x + (c.corr : ℝ))
    (hU : ∀ U ∈ c.Us, aVal c.Q x * Sv ≤ aVal U x)
    (hW : ∀ W ∈ c.Ws, aVal W x ≤ wrel qw qo) :
    ∀ r ∈ selRowsOfCtx c, aVal r x ≤ 0 := by
  intro r hr
  simp only [selRowsOfCtx, List.mem_flatMap, List.mem_map] at hr
  obtain ⟨W, hWm, U, hUm, rfl⟩ := hr
  have key := relax_selection (qw := qw) (qo := qo) (k := k) (eps := eps)
    (Pv := aVal c.P x) (Qv := aVal c.Q x) (Cv := Cv) (Sv := Sv) (corr := (c.corr : ℝ))
    (Wlb := aVal W x) (Uv := aVal U x) hgs hdec hcor (hU U hUm) (hW W hWm)
  simp only [aVal_sub, aVal_add, aVal_smul, aVal_const]
  push_cast
  linarith

/-- The `w` branches: the constant `1` when both bodies are pins (`w(0) = 1`), otherwise the two
certified planes, one per branch sign. -/
def wsOf (M : CMeta) (WE : WEnv) (iw io : Nat) (bothPin : Bool) (cw cb : ℚ × ℚ) :
    Option (List Aff) :=
  if bothPin then some [aConst 1]
  else
    match wLookup WE 1 cw cb, wLookup WE (-1) cw cb with
    | some e1, some e2 =>
        some [wAff M iw io e1.mw e1.mo e1.cc, wAff M iw io e2.mw e2.mo e2.cc]
    | _, _ => none

/-- The `Q·S` envelopes and the correction constant, from the `S` table; the DEGENERATE case
(the owner's tilt cell is a point, in particular whenever the owner is a pin) has `S ≡ 0` and
`C ≡ 1`, so it needs no table entry at all. -/
def selUs (M : CMeta) (SE : SEnv) (iw : Nat) (Q : Aff) (cw : ℚ × ℚ) (qlo qhi plo : ℚ) :
    Option (List Aff × ℚ) :=
  if cw.1 = cw.2 then some ([aZero], 0)
  else
    match sLookup SE cw with
    | none => none
    | some se =>
        some (usOf Q (aAdd (aSmul se.alpha (tiltAff M iw)) (aConst se.bup))
                     (aAdd (aSmul se.alpha (tiltAff M iw)) (aConst se.blo))
                     qlo qhi se.slo se.shi,
              max 0 (-plo) * se.kk)

/-- **The selection context of one fixed selection over the current cell.** -/
def selCtx (M : CMeta) (SE : SEnv) (WE : WEnv) (cur : List (ℚ × ℚ)) (iw io : Nat) (k : Bool)
    (eps : ℚ) : Option SelCtx :=
  match M.bs[iw]?, M.bs[io]?, tcellOf M cur iw, tcellOf M cur io with
  | some bw, some bo, some cw, some cb =>
      match affMin (selP M iw io ((cw.1 + cw.2) / 2) k eps) cur,
            affMin (selQ M iw io ((cw.1 + cw.2) / 2) k eps) cur,
            affMax (selQ M iw io ((cw.1 + cw.2) / 2) k eps) cur,
            wsOf M WE iw io (!bw.free && !bo.free) cw cb with
      | some plo, some qlo, some qhi, some Ws =>
          match selUs M SE iw (selQ M iw io ((cw.1 + cw.2) / 2) k eps) cw qlo qhi plo with
          | none => none
          | some (Us, corr) =>
              some ⟨selP M iw io ((cw.1 + cw.2) / 2) k eps,
                    selQ M iw io ((cw.1 + cw.2) / 2) k eps, corr, Us, Ws⟩
      | _, _, _, _ => none
  | _, _, _, _ => none

/-- **(C3) Lemma RELAX for the selection family, reflected and assembled.**  Every row the
builder produces from a fixed selection holds at the configuration's variable vector.  The five
hypotheses of `LocalCertT2.relax_selection` are supplied here: the axis decomposition by
`axis_decomp_t` (an algebraic identity in `t`), the correction bound by `one_sub_cosRel_le` and
`corr_bound`, the `Q·S` envelope by `usOf_sound`, and the plane below `w` by `wEntry_sound`. -/
theorem selCtx_sound {M : CMeta} {SE : SEnv} {WE : WEnv} {cur : List (ℚ × ℚ)}
    {iw io : Nat} {k : Bool} {eps : ℚ} {q : Nat → PSq} {s : ℝ} {c : SelCtx}
    (hg : GeoHyp M q s) (hsok : sEnvOk SE = true) (hwok : wEnvOk WE = true)
    (hbox : InBox cur (certX M q s) 0)
    (hgs : 0 ≤ gsel (q iw) (q io) k ((eps : ℚ) : ℝ))
    (h : selCtx M SE WE cur iw io k eps = some c) :
    ∀ r ∈ selRowsOfCtx c, aVal r (certX M q s) ≤ 0 := by
  revert h
  cases hbw : M.bs[iw]? with
  | none => intro h; simp [selCtx, hbw] at h
  | some bw =>
  cases hbo : M.bs[io]? with
  | none => intro h; simp [selCtx, hbw, hbo] at h
  | some bo =>
  cases hcw : tcellOf M cur iw with
  | none => intro h; simp [selCtx, hbw, hbo, hcw] at h
  | some cw =>
  cases hcb : tcellOf M cur io with
  | none => intro h; simp [selCtx, hbw, hbo, hcw, hcb] at h
  | some cb =>
  set tm : ℚ := (cw.1 + cw.2) / 2 with htmdef
  set P : Aff := selP M iw io tm k eps with hPdef
  set Q : Aff := selQ M iw io tm k eps with hQdef
  cases hplo : affMin P cur with
  | none => intro h; simp [selCtx, hbw, hbo, hcw, hcb, hplo, ← hPdef, ← htmdef] at h
  | some plo =>
  cases hqlo : affMin Q cur with
  | none => intro h; simp [selCtx, hbw, hbo, hcw, hcb, hplo, hqlo, ← hPdef, ← hQdef, ← htmdef] at h
  | some qlo =>
  cases hqhi : affMax Q cur with
  | none =>
    intro h
    simp [selCtx, hbw, hbo, hcw, hcb, hplo, hqlo, hqhi, ← hPdef, ← hQdef, ← htmdef] at h
  | some qhi =>
  cases hws : wsOf M WE iw io (!bw.free && !bo.free) cw cb with
  | none =>
    intro h
    simp [selCtx, hbw, hbo, hcw, hcb, hplo, hqlo, hqhi, hws, ← hPdef, ← hQdef, ← htmdef] at h
  | some Ws =>
  cases hus : selUs M SE iw Q cw qlo qhi plo with
  | none =>
    intro h
    simp [selCtx, hbw, hbo, hcw, hcb, hplo, hqlo, hqhi, hws, hus,
      ← hPdef, ← hQdef, ← htmdef] at h
  | some p =>
  obtain ⟨Us, corr⟩ := p
  intro h
  simp only [selCtx, hbw, hbo, hcw, hcb, hplo, hqlo, hqhi, hws, hus,
    ← hPdef, ← hQdef, ← htmdef, Option.some.injEq] at h
  subst h
  -- the geometry read off the cell
  have hiw : iw < M.bs.length := bs_lt_of_getElem hbw
  have hio : io < M.bs.length := bs_lt_of_getElem hbo
  have htw := tcellOf_mem hg hbox hcw
  have htb := tcellOf_mem hg hbox hcb
  have hdxv : aVal (dAffX M iw io) (certX M q s) = (q io).cx - (q iw).cx := by
    simp only [dAffX, aVal_sub, cenAffX_val hbo, cenAffX_val hbw]
  have hdyv : aVal (dAffY M iw io) (certX M q s) = (q io).cy - (q iw).cy := by
    simp only [dAffY, aVal_sub, cenAffY_val hbo, cenAffY_val hbw]
  obtain ⟨hA1, hA2⟩ := axQ_cast tm k
  set tmR : ℝ := ((tm : ℚ) : ℝ) with htmR
  set Cv : ℝ := cosRel (q iw).t tmR with hCvdef
  set Sv : ℝ := sRel (cosT tmR) (sinT tmR) (q iw).t with hSvdef
  have hPv : aVal P (certX M q s)
      = ((eps : ℚ) : ℝ) * (((q io).cx - (q iw).cx) * (axk ⟨0, 0, tmR⟩ k).1
          + ((q io).cy - (q iw).cy) * (axk ⟨0, 0, tmR⟩ k).2) := by
    simp only [hPdef, selP, aVal_smul, aVal_add, hdxv, hdyv]
    rw [← hA1, ← hA2]
    ring
  have hQv : aVal Q (certX M q s)
      = ((eps : ℚ) : ℝ) * (-(((q io).cx - (q iw).cx) * (axk ⟨0, 0, tmR⟩ k).2)
          + ((q io).cy - (q iw).cy) * (axk ⟨0, 0, tmR⟩ k).1) := by
    simp only [hQdef, selQ, aVal_smul, aVal_add, hdxv, hdyv]
    rw [← hA1, ← hA2]
    push_cast
    ring
  have hdec : aVal P (certX M q s) * Cv + aVal Q (certX M q s) * Sv
      = ((eps : ℚ) : ℝ) * (((q io).cx - (q iw).cx) * (axk (q iw) k).1
          + ((q io).cy - (q iw).cy) * (axk (q iw) k).2) := by
    rw [hPv, hQv, hCvdef, hSvdef]
    exact axis_decomp_t (q iw) (q io) tmR k ((eps : ℚ) : ℝ)
      ((q io).cx - (q iw).cx) ((q io).cy - (q iw).cy) rfl rfl
  -- the `w` branches
  have hW : ∀ W ∈ Ws, aVal W (certX M q s) ≤ wrel (q iw) (q io) := by
    revert hws
    cases hbp : (!bw.free && !bo.free) with
    | true =>
      intro hws
      simp only [wsOf, hbp, if_pos, Option.some.injEq] at hws
      subst hws
      intro W hWm
      simp only [List.mem_cons, List.not_mem_nil, or_false] at hWm
      subst hWm
      simp only [Bool.and_eq_true, Bool.not_eq_true'] at hbp
      have hzw : (q iw).t = 0 := (hg.hpin iw bw hbw hbp.1).2.2
      have hzo : (q io).t = 0 := (hg.hpin io bo hbo hbp.2).2.2
      rw [aVal_const]
      have := wrel_ge_one_of_zero hzw hzo
      push_cast
      linarith
    | false =>
      cases he1 : wLookup WE 1 cw cb with
      | none => intro hws; simp [wsOf, hbp, he1] at hws
      | some e1 =>
        cases he2 : wLookup WE (-1) cw cb with
        | none => intro hws; simp [wsOf, hbp, he1, he2] at hws
        | some e2 =>
          intro hws
          simp only [wsOf, hbp, Bool.false_eq_true, if_false, he1, he2,
            Option.some.injEq] at hws
          subst hws
          have hone : ∀ e : WEntry, wEntryOk e = true → e.cw = cw → e.cb = cb →
              aVal (wAff M iw io e.mw e.mo e.cc) (certX M q s) ≤ wrel (q iw) (q io) := by
            intro e hok hc1 hc2
            have hb1 : ((e.cw.1 : ℚ) : ℝ) ≤ (q iw).t := by rw [hc1]; exact htw.1
            have hb2 : (q iw).t ≤ ((e.cw.2 : ℚ) : ℝ) := by rw [hc1]; exact htw.2
            have hb3 : ((e.cb.1 : ℚ) : ℝ) ≤ (q io).t := by rw [hc2]; exact htb.1
            have hb4 : (q io).t ≤ ((e.cb.2 : ℚ) : ℝ) := by rw [hc2]; exact htb.2
            have := wEntry_sound hok hb1 hb2 hb3 hb4
            simp only [wAff, aVal_add, aVal_smul, aVal_const,
              tiltAff_val hg hbw, tiltAff_val hg hbo]
            linarith
          obtain ⟨hk1, hc11, hc12⟩ := wLookup_ok WE 1 cw cb e1 hwok he1
          obtain ⟨hk2, hc21, hc22⟩ := wLookup_ok WE (-1) cw cb e2 hwok he2
          intro W hWm
          simp only [List.mem_cons, List.not_mem_nil, or_false] at hWm
          rcases hWm with rfl | rfl
          · exact hone e1 hk1 hc11 hc12
          · exact hone e2 hk2 hc21 hc22
  -- the correction constant and the `Q·S` envelopes
  have hPlo : ((plo : ℚ) : ℝ) ≤ aVal P (certX M q s) := affMin_le hplo hbox
  have hQlo : ((qlo : ℚ) : ℝ) ≤ aVal Q (certX M q s) := affMin_le hqlo hbox
  have hQhi : aVal Q (certX M q s) ≤ ((qhi : ℚ) : ℝ) := le_affMax hqhi hbox
  have hcorU : aVal P (certX M q s) * Cv ≤ aVal P (certX M q s) + ((corr : ℚ) : ℝ) ∧
      ∀ U ∈ Us, aVal Q (certX M q s) * Sv ≤ aVal U (certX M q s) := by
    revert hus
    by_cases hdeg : cw.1 = cw.2
    · intro hus
      simp only [selUs, if_pos hdeg, Option.some.injEq, Prod.mk.injEq] at hus
      obtain ⟨hUs, hcorr⟩ := hus
      subst hUs; subst hcorr
      have hteq : (q iw).t = tmR := by
        have h1 := htw.1
        have h2 := htw.2
        rw [← hdeg] at h2
        have : (q iw).t = ((cw.1 : ℚ) : ℝ) := le_antisymm h2 h1
        rw [this, htmR, htmdef, ← hdeg]
        push_cast
        ring
      constructor
      · rw [hCvdef, hteq, cosRel_self]
        push_cast
        linarith
      · intro U hU
        simp only [List.mem_cons, List.not_mem_nil, or_false] at hU
        subst hU
        rw [hSvdef, hteq, sRel_self, aVal_zero]
        linarith
    · intro hus
      revert hus
      cases hse : sLookup SE cw with
      | none => intro hus; simp [selUs, hdeg, hse] at hus
      | some se =>
        intro hus
        simp only [selUs, if_neg hdeg, hse, Option.some.injEq, Prod.mk.injEq] at hus
        obtain ⟨hUs, hcorr⟩ := hus
        subst hUs; subst hcorr
        obtain ⟨hseok, hsecell⟩ := sLookup_ok SE cw se hsok hse
        have htmeq : se.tm = tm := by rw [SEntry.tm, hsecell, htmdef]
        have hc1 : ((se.cell.1 : ℚ) : ℝ) ≤ (q iw).t := by rw [hsecell]; exact htw.1
        have hc2 : (q iw).t ≤ ((se.cell.2 : ℚ) : ℝ) := by rw [hsecell]; exact htw.2
        rw [sEntryOk, Bool.and_eq_true, Bool.and_eq_true, Bool.and_eq_true, Bool.and_eq_true,
          Bool.and_eq_true, decide_eq_true_eq] at hseok
        obtain ⟨⟨⟨⟨⟨hpUp, hpLo⟩, hpHi⟩, hpLoC⟩, hpCorr⟩, hK0⟩ := hseok
        rw [htmeq] at hpUp hpLo hpHi hpLoC hpCorr
        have hcm : ((cosTQ tm : ℚ) : ℝ) = cosT tmR := cosTQ_cast tm
        have hsm : ((sinTQ tm : ℚ) : ℝ) = sinT tmR := sinTQ_cast tm
        have hSvalt : Sv = sRel ((cosTQ tm : ℚ) : ℝ) ((sinTQ tm : ℚ) : ℝ) (q iw).t := by
          rw [hSvdef, hcm, hsm]
        have hup : Sv ≤ ((se.alpha : ℚ) : ℝ) * (q iw).t + ((se.bup : ℚ) : ℝ) := by
          rw [hSvalt]; exact sRel_le_aff hpUp hc1 hc2
        have hdn : ((se.alpha : ℚ) : ℝ) * (q iw).t + ((se.blo : ℚ) : ℝ) ≤ Sv := by
          rw [hSvalt]; exact sRel_ge_aff hpLo hc1 hc2
        have hsh : Sv ≤ ((se.shi : ℚ) : ℝ) := by
          have := sRel_le_aff hpHi hc1 hc2
          rw [← hSvalt] at this
          push_cast at this
          linarith
        have hsl : ((se.slo : ℚ) : ℝ) ≤ Sv := by
          have := sRel_ge_aff hpLoC hc1 hc2
          rw [← hSvalt] at this
          push_cast at this
          linarith
        have hCK : 1 - Cv ≤ ((se.kk : ℚ) : ℝ) := by
          rw [hCvdef]
          exact one_sub_cosRel_le hcm hsm hpCorr hc1 hc2
        have hK0' : (0 : ℝ) ≤ ((se.kk : ℚ) : ℝ) := by exact_mod_cast hK0
        constructor
        · have := corr_bound (Pv := aVal P (certX M q s)) (Plo := ((plo : ℚ) : ℝ)) (Cv := Cv)
            (K := ((se.kk : ℚ) : ℝ)) hPlo (by rw [hCvdef]; exact cosRel_le_one _ _) hCK hK0'
          push_cast
          linarith
        · refine usOf_sound (Sv := Sv) hQlo hQhi hsl hsh ?_ ?_
          · simp only [aVal_add, aVal_smul, aVal_const, tiltAff_val hg hbw]
            exact hup
          · simp only [aVal_add, aVal_smul, aVal_const, tiltAff_val hg hbw]
            exact hdn
  exact selRowsOfCtx_sound (qw := q iw) (qo := q io) (k := k) (eps := ((eps : ℚ) : ℝ))
    (Cv := Cv) (Sv := Sv) hgs hdec hcorU.1 hcorU.2 hW

/-! ### 5.4 All the rows of one node

The rows a node's LP sees are the four wall rows of every body plus the six rows of every FIXED
selection.  `allRows` assembles them and `allRows_sound` says every one of them holds. -/

def optList : List (Option (List Aff)) → Option (List Aff)
  | [] => some []
  | none :: _ => none
  | some a :: t => (optList t).map fun r => a ++ r

theorem optList_mem : ∀ (l : List (Option (List Aff))) (rs : List Aff),
    optList l = some rs → ∀ r ∈ rs, ∃ a, some a ∈ l ∧ r ∈ a := by
  intro l
  induction l with
  | nil => intro rs h r hr; rw [optList, Option.some.injEq] at h; subst h; simp at hr
  | cons hd t ih =>
    intro rs h r hr
    cases hd with
    | none => rw [optList] at h; exact absurd h (by simp)
    | some a =>
      rw [optList, Option.map_eq_some_iff] at h
      obtain ⟨r', hr', rfl⟩ := h
      rcases List.mem_append.mp hr with hm | hm
      · exact ⟨a, List.mem_cons_self .., hm⟩
      · obtain ⟨b, hb, hrb⟩ := ih r' hr' r hm
        exact ⟨b, List.mem_cons_of_mem _ hb, hrb⟩

/-- One recorded selection of the tree: the pair, the owner flag, the axis and the sign. -/
structure CSel where
  i : Nat
  j : Nat
  o : Bool
  k : Bool
  e : ℚ
deriving Inhabited, Repr, DecidableEq

def CSel.owner (σ : CSel) : Nat := if σ.o then σ.j else σ.i
def CSel.other (σ : CSel) : Nat := if σ.o then σ.i else σ.j

/-- The selection's own separating-axis row, `g_σ ≥ 0`. -/
def SelHolds (σ : CSel) (q : Nat → PSq) : Prop :=
  0 ≤ gsel (q σ.owner) (q σ.other) σ.k ((σ.e : ℚ) : ℝ)

/-- Every row of a node: the wall family of every body, the selection family of every fixed
selection. -/
def allRows (M : CMeta) (SE : SEnv) (WE : WEnv) (HE : HEnv) (cur : List (ℚ × ℚ))
    (fx : List CSel) : Option (List Aff) :=
  optList (((List.range M.bs.length).map fun i => wallOf M HE cur i) ++
           fx.map fun σ => (selCtx M SE WE cur σ.owner σ.other σ.k σ.e).map selRowsOfCtx)

theorem allRows_sound {M : CMeta} {SE : SEnv} {WE : WEnv} {HE : HEnv} {cur : List (ℚ × ℚ)}
    {fx : List CSel} {q : Nat → PSq} {s : ℝ} {rs : List Aff}
    (hg : GeoHyp M q s) (hh : hEnvOk HE = true) (hsok : sEnvOk SE = true)
    (hwok : wEnvOk WE = true) (hbox : InBox cur (certX M q s) 0)
    (hfx : ∀ σ ∈ fx, SelHolds σ q) (h : allRows M SE WE HE cur fx = some rs) :
    ∀ r ∈ rs, aVal r (certX M q s) ≤ 0 := by
  intro r hr
  obtain ⟨a, hain, hra⟩ := optList_mem _ rs h r hr
  rcases List.mem_append.mp hain with hm | hm
  · obtain ⟨i, _, hw⟩ := List.mem_map.mp hm
    exact wallOf_sound hg hh hbox hw r hra
  · obtain ⟨σ, hσ, he⟩ := List.mem_map.mp hm
    rw [Option.map_eq_some_iff] at he
    obtain ⟨c, hc, rfl⟩ := he
    exact selCtx_sound hg hsok hwok hbox (hfx σ hσ) hc r hra

/-- The leaf's emitted (quantised) rows are all implied by the node's true rows. -/
def leafRowsOk (M : CMeta) (SE : SEnv) (WE : WEnv) (HE : HEnv) (cur : List (ℚ × ℚ))
    (fx : List CSel) (L : CLeaf) : Bool :=
  match allRows M SE WE HE cur fx with
  | none => false
  | some rs => L.rows.all fun r => rs.any fun u => affImplies u L.box r

/-! ## 6. (R1) The reflected certificate tree

A133's emitted `root` has five kinds of node.  Two are case SPLITS — a tilt bisection and a
selection branch — and three CLOSE a node: a pair with no possible selection, a fixed selection
that has become impossible on the smaller cell, and a dead leaf.

The selection branch is reflected here as a chain of BINARY splits (`sel1`), each of which is the
tautology `SelHolds σ ∨ ¬ SelHolds σ` and needs no certificate at all; what the certificate has
to supply is the closing node at the end of the chain (`impx`), where the recorded selections are
exhaustive by `LocalCertT2.selectionOk_sound` and every one of them has already been refuted
along the chain.  Binary nodes make the tree a plain structural inductive, so `treeOk_sound` is a
plain structural induction. -/

/-- The two halves of the current cell at a bisection, COMPUTED rather than recorded: at 2 202
bisections a 20-coordinate certificate would otherwise carry 88 000 rational literals for data
the walk already holds. -/
def cellLo (cur : List (ℚ × ℚ)) (jv : Nat) (m : ℚ) : List (ℚ × ℚ) :=
  cur.set jv ((cur.getD jv (0, 0)).1, m)

def cellHi (cur : List (ℚ × ℚ)) (jv : Nat) (m : ℚ) : List (ℚ × ℚ) :=
  cur.set jv (m, (cur.getD jv (0, 0)).2)

inductive CNode where
  /-- bisect the cell at coordinate `jv`, split point `m`; the children's cells are computed. -/
  | bisect (jv : Nat) (m : ℚ) (l r : CNode) : CNode
  /-- case split on one selection: it holds (`hd`) or it does not (`tl`). -/
  | sel1 (σ : CSel) (hd tl : CNode) : CNode
  /-- the pair `(i, j)` is interior-disjoint, so one of `sels` holds — and all of them have been
  refuted on this branch, so the node is vacuous. -/
  | impx (i j : Nat) (sels : List (Bool × Bool × ℚ)) : CNode
  /-- a fixed selection is impossible on this cell. -/
  | impsel (σ : CSel) : CNode
  /-- a dead leaf of the certificate. -/
  | dead (li : Nat) : CNode
deriving Inhabited

/-- The decidable well-formedness of the whole tree. -/
def treeOk (M : CMeta) (SE : SEnv) (WE : WEnv) (HE : HEnv) (leaves : List CLeaf) :
    CNode → List (ℚ × ℚ) → List CSel → List CSel → Bool
  | .bisect jv m l r, cur, fx, ng =>
      splitOk cur (cellLo cur jv m) (cellHi cur jv m) jv m &&
        treeOk M SE WE HE leaves l (cellLo cur jv m) fx ng &&
        treeOk M SE WE HE leaves r (cellHi cur jv m) fx ng
  | .sel1 σ hd tl, cur, fx, ng =>
      treeOk M SE WE HE leaves hd cur (σ :: fx) ng &&
        treeOk M SE WE HE leaves tl cur fx (σ :: ng)
  | .impx i j sels, cur, _, ng =>
      (i != j) && (i < M.bs.length) && (j < M.bs.length) &&
      (match pairBoxOf M cur i j with
       | none => false
       | some pb => pbOkB pb && selectionOk pb sels) &&
      sels.all fun p => decide ((⟨i, j, p.1, p.2.1, p.2.2⟩ : CSel) ∈ ng)
  | .impsel σ, cur, fx, _ =>
      decide (σ ∈ fx) &&
      (match pairBoxOf M cur σ.i σ.j with
       | none => false
       | some pb => pbOkB pb && decide (gapHi (if σ.o then pb.swap else pb) σ.k σ.e < 0))
  | .dead li, cur, fx, _ =>
      match leaves[li]? with
      | none => false
      | some L => (L.box == cur) && leafRowsOk M SE WE HE cur fx L

/-- **(R1) the reflected tree walk, sound.**  Every configuration whose variable vector lies in
the root cell reaches a recorded leaf whose box contains it and whose rows hold there. -/
theorem treeOk_sound {M : CMeta} {SE : SEnv} {WE : WEnv} {HE : HEnv} {leaves : List CLeaf}
    {q : Nat → PSq} {s : ℝ} (hg : GeoHyp M q s) (hh : hEnvOk HE = true)
    (hsok : sEnvOk SE = true) (hwok : wEnvOk WE = true) :
    ∀ (T : CNode) (cur : List (ℚ × ℚ)) (fx ng : List CSel),
      treeOk M SE WE HE leaves T cur fx ng = true →
      InBox cur (certX M q s) 0 →
      (∀ σ ∈ fx, SelHolds σ q) → (∀ σ ∈ ng, ¬ SelHolds σ q) →
      ∃ L ∈ leaves, LeafHolds L (certX M q s) := by
  intro T
  induction T with
  | bisect jv m l r ihl ihr =>
    intro cur fx ng hchk hbox hfx hng
    rw [treeOk, Bool.and_eq_true, Bool.and_eq_true] at hchk
    obtain ⟨⟨hs, hl⟩, hr⟩ := hchk
    rcases splitOk_sound cur (cellLo cur jv m) (cellHi cur jv m) jv m (certX M q s) 0 hs hbox
      with h1 | h2
    · exact ihl (cellLo cur jv m) fx ng hl h1 hfx hng
    · exact ihr (cellHi cur jv m) fx ng hr h2 hfx hng
  | sel1 σ hd tl ihh iht =>
    intro cur fx ng hchk hbox hfx hng
    rw [treeOk, Bool.and_eq_true] at hchk
    by_cases hs : SelHolds σ q
    · refine ihh cur (σ :: fx) ng hchk.1 hbox ?_ hng
      intro τ hτ
      rcases List.mem_cons.mp hτ with rfl | hm
      · exact hs
      · exact hfx τ hm
    · refine iht cur fx (σ :: ng) hchk.2 hbox hfx ?_
      intro τ hτ
      rcases List.mem_cons.mp hτ with rfl | hm
      · exact hs
      · exact hng τ hm
  | impx i j sels =>
    intro cur fx ng hchk hbox hfx hng
    exfalso
    rw [treeOk, Bool.and_eq_true, Bool.and_eq_true] at hchk
    obtain ⟨⟨hidx, hpb⟩, hall⟩ := hchk
    rw [Bool.and_eq_true, Bool.and_eq_true, bne_iff_ne, decide_eq_true_eq,
      decide_eq_true_eq] at hidx
    obtain ⟨⟨hne, hi⟩, hj⟩ := hidx
    revert hpb
    cases hp : pairBoxOf M cur i j with
    | none => intro hpb; simp at hpb
    | some pb =>
      intro hpb
      rw [Bool.and_eq_true] at hpb
      have hholds := pairBoxOf_holds hg hbox hp
      have hdis := hg.hdisj i j hi hj hne
      obtain ⟨p, hpm, hgp⟩ :=
        selectionOk_sound (pbOkB_sound hpb.1) hholds hdis hpb.2
      rw [List.all_eq_true] at hall
      have hin := hall p hpm
      rw [decide_eq_true_eq] at hin
      refine hng _ hin ?_
      simp only [SelHolds, CSel.owner, CSel.other]
      cases hb : p.1
      · rw [hb] at hgp
        simpa using hgp
      · rw [hb] at hgp
        simpa using hgp
  | impsel σ =>
    intro cur fx ng hchk hbox hfx hng
    exfalso
    rw [treeOk, Bool.and_eq_true, decide_eq_true_eq] at hchk
    obtain ⟨hmem, hpb⟩ := hchk
    revert hpb
    cases hp : pairBoxOf M cur σ.i σ.j with
    | none => intro hpb; simp at hpb
    | some pb =>
      intro hpb
      rw [Bool.and_eq_true, decide_eq_true_eq] at hpb
      have hok := pbOkB_sound hpb.1
      have hholds := pairBoxOf_holds hg hbox hp
      have hgs := hfx σ hmem
      simp only [SelHolds, CSel.owner, CSel.other] at hgs
      have hlt : ((gapHi (if σ.o then pb.swap else pb) σ.k σ.e : ℚ) : ℝ) < 0 := by
        exact_mod_cast hpb.2
      cases hb : σ.o
      · rw [hb] at hgs hlt
        simp only [Bool.false_eq_true, if_false] at hgs hlt
        have := gsel_le_gapHi (pb := pb) (qw := q σ.i) (qo := q σ.j) hok hholds σ.k σ.e
        linarith
      · rw [hb] at hgs hlt
        simp only [if_pos] at hgs hlt
        have := gsel_le_gapHi (pb := pb.swap) (qw := q σ.j) (qo := q σ.i)
          (PairBox.swap_ok hok) (PairBox.swap_holds hholds) σ.k σ.e
        linarith
  | dead li =>
    intro cur fx ng hchk hbox hfx hng
    revert hchk
    cases hl : leaves[li]? with
    | none => intro hchk; simp [treeOk, hl] at hchk
    | some L =>
      intro hchk
      simp only [treeOk, hl, Bool.and_eq_true, beq_iff_eq] at hchk
      obtain ⟨hbeq, hrows⟩ := hchk
      refine ⟨L, List.mem_of_getElem? hl, ?_⟩
      have hLbox : InBox L.box (certX M q s) 0 := by rw [hbeq]; exact hbox
      refine ⟨hLbox, ?_⟩
      revert hrows
      cases hall : allRows M SE WE HE cur fx with
      | none => intro hrows; simp [leafRowsOk, hall] at hrows
      | some rs =>
        intro hrows
        simp only [leafRowsOk, hall, List.all_eq_true] at hrows
        intro rw' hrw
        have hu := hrows rw' hrw
        rw [List.any_eq_true] at hu
        obtain ⟨u, hum, himp⟩ := hu
        exact affImplies_sound himp hLbox
          (allRows_sound hg hh hsok hwok hbox hfx hall u hum)

/-! ## 7. The root cell, and the glue

The last piece is that the certificate's ROOT cell is the neighbourhood's own box: side in the
certificate's window, each free body's centre in its `Box` and each pin's OFFSET in `[−h, h]`,
each free body's tilt in its root cell.  `rootOk` decides it and `rootOk_sound` proves it, so
`certCover_of_check` has no numeric side condition left. -/

theorem inBox_of_forall : ∀ (box : List (ℚ × ℚ)) (x : Nat → ℝ) (i : Nat),
    (∀ (j : Nat) (p : ℚ × ℚ), box[j]? = some p →
      ((p.1 : ℚ) : ℝ) ≤ x (i + j) ∧ x (i + j) ≤ ((p.2 : ℚ) : ℝ)) → InBox box x i := by
  intro box
  induction box with
  | nil => intro x i _; trivial
  | cons c t ih =>
    intro x i h
    have h0 := h 0 c (by simp)
    rw [Nat.add_zero] at h0
    refine ⟨h0.1, h0.2, ih x (i + 1) ?_⟩
    intro j p hj
    have := h (j + 1) p (by simpa using hj)
    rwa [show i + (j + 1) = i + 1 + j by omega] at this

/-- **The root-cell check.** -/
def rootOk (M : CMeta) (cell : List (ℚ × ℚ)) : Bool :=
  (cell.length == 2 * M.bs.length + 1 + M.nL) &&
  (cell[0]? == some (M.slo, M.shi)) &&
  (List.range M.bs.length).all fun i =>
    match M.bs[i]? with
    | none => false
    | some b =>
        if b.free then
          (cell[2 * i + 1]? == some (b.x0, b.x1)) && (cell[2 * i + 2]? == some (b.y0, b.y1)) &&
            (cell[2 * M.bs.length + 1 + i]? == some (b.t0, b.t1))
        else
          (cell[2 * i + 1]? == some (-b.hh, b.hh)) && (cell[2 * i + 2]? == some (-b.hh, b.hh))

theorem rootOk_sound {M : CMeta} {cell : List (ℚ × ℚ)} {q : Nat → PSq} {s : ℝ}
    (hlay : layoutOk M = true) (hok : rootOk M cell = true) (hg : GeoHyp M q s)
    (hlo : ((M.slo : ℚ) : ℝ) ≤ s) (hhi : s ≤ ((M.shi : ℚ) : ℝ)) :
    InBox cell (certX M q s) 0 := by
  rw [rootOk, Bool.and_eq_true, Bool.and_eq_true, List.all_eq_true, beq_iff_eq,
    beq_iff_eq] at hok
  obtain ⟨⟨hlen, h0⟩, hall⟩ := hok
  have hnL : M.nL ≤ M.bs.length := layoutOk_le hlay
  refine inBox_of_forall cell (certX M q s) 0 ?_
  intro j p hj
  rw [Nat.zero_add]
  have hjlt : j < cell.length := by
    by_contra hc
    rw [List.getElem?_eq_none (by omega)] at hj
    simp at hj
  rw [hlen] at hjlt
  by_cases hj0 : j = 0
  · subst hj0
    rw [h0, Option.some.injEq] at hj
    subst hj
    rw [certX_zero]
    exact ⟨hlo, hhi⟩
  · by_cases hjt : 2 * M.bs.length + 1 ≤ j
    · -- a tilt coordinate
      set f := j - (2 * M.bs.length + 1) with hf
      have hfL : f < M.nL := by omega
      have hfb : f < M.bs.length := by omega
      have hjf : j = 2 * M.bs.length + 1 + f := by omega
      have hb := hall f (List.mem_range.mpr hfb)
      revert hb
      cases hbs : M.bs[f]? with
      | none => intro hb; simp at hb
      | some b =>
        intro hb
        dsimp only at hb
        have hfree : b.free = true := ((layoutOk_get hlay hbs).2.1).mpr hfL
        rw [hfree] at hb
        simp only [if_pos, Bool.and_eq_true, beq_iff_eq] at hb
        rw [hjf, hb.2, Option.some.injEq] at hj
        subst hj
        rw [hjf, certX_tilt]
        have := (hg.hbox f b hbs hfree).2.2
        exact ⟨this.1, this.2⟩
    · -- a centre coordinate
      set i := (j - 1) / 2 with hi
      have hib : i < M.bs.length := by omega
      have hb := hall i (List.mem_range.mpr hib)
      revert hb
      cases hbs : M.bs[i]? with
      | none => intro hb; simp at hb
      | some b =>
        intro hb
        dsimp only at hb
        by_cases hpar : (j - 1) % 2 = 0
        · have hji : j = 2 * i + 1 := by omega
          cases hfree : b.free with
          | true =>
            rw [hfree] at hb
            simp only [if_pos, Bool.and_eq_true, beq_iff_eq] at hb
            rw [hji, hb.1.1, Option.some.injEq] at hj
            subst hj
            rw [hji, certX_cx hbs, hfree]
            have := (hg.hbox i b hbs hfree).1
            simpa using ⟨this.1, this.2⟩
          | false =>
            rw [hfree] at hb
            simp only [Bool.false_eq_true, if_false, Bool.and_eq_true, beq_iff_eq] at hb
            rw [hji, hb.1, Option.some.injEq] at hj
            subst hj
            rw [hji, certX_cx hbs, hfree]
            have := (hg.hpin i b hbs hfree).1
            rw [abs_le] at this
            simp only [Bool.false_eq_true, if_false, pinOfCB] at this ⊢
            push_cast
            constructor <;> linarith [this.1, this.2]
        · have hji : j = 2 * i + 2 := by omega
          cases hfree : b.free with
          | true =>
            rw [hfree] at hb
            simp only [if_pos, Bool.and_eq_true, beq_iff_eq] at hb
            rw [hji, hb.1.2, Option.some.injEq] at hj
            subst hj
            rw [hji, certX_cy hbs, hfree]
            have := (hg.hbox i b hbs hfree).2.1
            simpa using ⟨this.1, this.2⟩
          | false =>
            rw [hfree] at hb
            simp only [Bool.false_eq_true, if_false, Bool.and_eq_true, beq_iff_eq] at hb
            rw [hji, hb.2, Option.some.injEq] at hj
            subst hj
            rw [hji, certX_cy hbs, hfree]
            have := (hg.hpin i b hbs hfree).2.1
            rw [abs_le] at this
            simp only [Bool.false_eq_true, if_false, pinOfCB] at this ⊢
            push_cast
            constructor <;> linarith [this.1, this.2]

/-- **The reflected certificate.** -/
structure Cert where
  M : CMeta
  HE : HEnv
  SE : SEnv
  WE : WEnv
  cell : List (ℚ × ℚ)
  root : CNode
  leaves : List CLeaf

/-- **The one decidable check.**  The layout, the root cell, the three envelope tables and the
whole tree. -/
def certOk (C : Cert) : Bool :=
  layoutOk C.M && rootOk C.M C.cell && hEnvOk C.HE && sEnvOk C.SE && wEnvOk C.WE &&
    treeOk C.M C.SE C.WE C.HE C.leaves C.root C.cell [] []

/-- **`CertCover` from the check** — (C1)–(C4) and (R1)–(R3) assembled.  This is the obligation
`LocalCert.localDead_of_cert` leaves open, and it is now decided by exact rational arithmetic on
the certificate's own data. -/
theorem certCover_of_check {C : Cert} (hok : certOk C = true) :
    CertCover C.leaves C.M.boxes C.M.pins ((C.M.slo : ℚ) : ℝ) ((C.M.shi : ℚ) : ℝ) := by
  rw [certOk, Bool.and_eq_true, Bool.and_eq_true, Bool.and_eq_true, Bool.and_eq_true,
    Bool.and_eq_true] at hok
  obtain ⟨⟨⟨⟨⟨hlay, hroot⟩, hh⟩, hsok⟩, hwok⟩, htree⟩ := hok
  intro s z hlo hhi hz hN
  obtain ⟨q, hg⟩ := geoHyp_of_localHyp hlay hz hN
  refine ⟨certX C.M q s, certX_zero C.M q s, ?_⟩
  exact treeOk_sound hg hh hsok hwok C.root C.cell [] [] htree
    (rootOk_sound hlay hroot hg hlo hhi) (by simp) (by simp)

/-- **Theorem LOCAL from two decidable checks.**  `LocalDead` for the certificate's own
neighbourhood: `hchk` is `LocalCert.checkLeaf` on every recorded leaf (the Farkas half) and
`certOk` is the cover half.  Nothing else is assumed. -/
theorem localDead_of_certOk {C : Cert} {s0 : ℚ} (hok : certOk C = true)
    (hlo : ((C.M.slo : ℚ) : ℝ) ≤ 191 / 50) (hhi : (s0 : ℝ) ≤ ((C.M.shi : ℚ) : ℝ))
    (hchk : C.leaves.all (checkLeaf s0) = true) :
    LocalDead C.M.boxes C.M.pins (s0 : ℝ) :=
  localDead_of_cert hlo hhi hchk (certCover_of_check hok)

/-! ## 8. Executability: the whole check runs in the kernel

Every function `certOk` calls is over `ℚ`, `Bool` and `List` — no `ℝ` and no `Classical` — so it
is `decide`-able (and `native_decide`-able on real certificate data).  The instance below is
DEGENERATE (no bodies, one leaf, a window ABOVE `s0`): its point is not the mathematics but that
the pipeline `certOk → certCover_of_check → CertCover` reduces and composes, which is the
property (R4) will exercise on `S07_trump5_r0.10_rho40` with the same code path. -/

/-- A degenerate certificate: no bodies, a window `[3.9, 5]`, one dead leaf with no rows. -/
def smokeCert : Cert where
  M := ⟨[], 0, 39 / 10, 5⟩
  HE := []
  SE := []
  WE := []
  cell := [(39 / 10, 5)]
  root := .dead 0
  leaves := [⟨false, [(39 / 10, 5)], []⟩]

/-- The reflected check reduces. -/
theorem smoke_certOk : certOk smokeCert = true := by native_decide

/-- So does the Farkas half. -/
theorem smoke_leafOk : smokeCert.leaves.all (checkLeaf (969271 / 250000)) = true := by
  native_decide

/-- And the two compose into a genuine `CertCover`. -/
theorem smoke_cover :
    CertCover smokeCert.leaves smokeCert.M.boxes smokeCert.M.pins
      ((39 / 10 : ℚ) : ℝ) ((5 : ℚ) : ℝ) :=
  certCover_of_check smoke_certOk

end LocalCertT3
end S11
end PackingCert

-- A138: end of file
