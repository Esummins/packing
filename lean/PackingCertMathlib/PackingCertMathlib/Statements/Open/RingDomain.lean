import PackingCertMathlib.Statements.Open.StripEnclosure

/-!
# -- OPEN: RING DOMAIN — which of STRIP₂-IN-RING's domain conditions the JAM hypotheses force — A271

`docs/proofs/ring_domain.md`.  Corner frame: wall `x = 0`, floor `y = 0`; `C` the floater (lowest vertex
`(h_u + s, h_v)`, tilt `θ`, `c = cos θ, s = sin θ`, left vertex at height `L_h = h_v + c`); `X` the wall toucher
(lowest point `X_low`, tilt `φ`, `cφ, sφ`); `A` the floor toucher (tilt `α`); `s̄ ∈ [3.82, ŝ]` the side.

**What is a theorem here (the arithmetic cores of ring_domain.md §1–§2).**
* `low_core` [T] (Lemma LOW, §1 (F4)): `A` lies below a line `y = k + m x` of slope `m > 0` and `C` above it
  (Lemma SLOPE); `A`'s left vertex `(x_min, cos α)` gives `k ≥ cos α − m x_min`, `C`'s vertices `B = (u, h_v)` and
  `R = (u + c, h_v + s)` give `h_v ≥ k + m u` and `h_v + s ≥ k + m (u + c)`.  With `d = x_min − u > 0` and
  `c − d > 0`: `c h_v ≥ c cos α − s d` (split on `c m ≤ s`).
* `lh_gt_one` [T]: from `c h_v ≥ c cos α − s d`, `d < 1 − s`, `cos α ≥ 0.7071`, `c ≥ 0.7071`: `h_v + c > 1` — the
  floater's left vertex is above height 1 whenever a floor toucher shares its box ((D1)'s `L_h > 1`).
* `u1_core` [T] ((U1)): `c sφ + s · dy < 1` when `dy < s` (X meets int `T_u`, so `X_low − L_h < s`), `sφ ≤ c`.
* `u9_core` [T] ((U9), the top vertex of `T_u`): `sφ² − sφ c + cφ · dy < 1` when `dy < c + s + cφ + sφ − 1.82`
  (`C_top − X_low` under `X_top > s̄ − 1 ≥ 2.82`, `h_v < 1`), `cφ ≥ sφ ≥ 0`, `c ≥ 0.7071`, `c + s ≤ 1.4143`.
* `x_high` [T] ((F1), (D2)): `X_top > s̄ − 1`, `s̄ ≥ 3.82`, `X_top − X_low = cφ + sφ ≤ 1.4143` give `X_low > 1.4057`.
* `strip_two_in_ring_of_jam` [T from the axiom]: the BL sectors of a JAM corner reduce to `pair3` under
  `JamCorner ∧ RingIneq` — A267's `strip_in_ring_of_enclosure` with the domain replaced by the hypotheses.

**What is not.**
* `strip_two_in_jam` [T-prose] is A267's proof (strip_enclosure.md §1–§3) with (D1), (D2), (U1), (U2), (U9)
  supplied by ring_domain.md §1–§2; `JamCorner` (H1–H3 at a side in [3.82, ŝ]) and `RingIneq` ((U3)–(U6) + (U8))
  are opaque.  (U3)–(U6) are FALSE as consequences of H1–H5 (ring_domain.md §2, drawn); (U8) is [M] only.
-/

namespace PackingCert.S11.OpenLemmas.RingDomain

/-- **Lemma LOW, the core** [T]: `A` under the line, `C`'s vertices `B`, `R` over it, `d = x_min − u > 0`,
`c − d > 0`, `c > 0`, `s ≥ 0`, `m > 0`: `c h_v ≥ c cos α − s d`. -/
theorem low_core (c s m k ca xmin u hv : ℝ) (hc : 0 < c) (_hs : 0 ≤ s) (_hm : 0 < m)
    (hk : ca - m * xmin ≤ k) (hB : k + m * u ≤ hv) (hR : k + m * (u + c) ≤ hv + s)
    (hd : 0 < xmin - u) (hcd : 0 < c - (xmin - u)) :
    c * ca - s * (xmin - u) ≤ c * hv := by
  by_cases h : c * m ≤ s
  · nlinarith [mul_le_mul_of_nonneg_left (show ca - m * (xmin - u) ≤ hv by linarith) hc.le,
               mul_nonneg (sub_nonneg.2 h) hd.le]
  · push_neg at h
    nlinarith [mul_le_mul_of_nonneg_left (show ca - s + m * (c - (xmin - u)) ≤ hv by linarith) hc.le,
               mul_nonneg (sub_nonneg.2 h.le) hcd.le]

/-- **The left vertex is above height 1** [T]: `c h_v ≥ c cos α − s d`, `d < 1 − s`, `cos α ≥ 0.7071`,
`c ≥ 0.7071`, `s ≥ 0`, `c ≤ 1`: `h_v + c > 1`. -/
theorem lh_gt_one (c s d ca hv : ℝ) (h1 : c ^ 2 + s ^ 2 = 1) (hc : 7071 / 10000 ≤ c) (hs : 0 ≤ s)
    (hca : 7071 / 10000 ≤ ca) (hd : d < 1 - s) (h : c * ca - s * d ≤ c * hv) : 1 < hv + c := by
  have hc0 : (0:ℝ) ≤ c := by linarith
  have hs1 : s ≤ 7072 / 10000 := by nlinarith
  have hkey : 2929 / 10000 * c < 1 - s := by
    by_contra hcon
    push_neg at hcon
    nlinarith [mul_le_mul_of_nonneg_left hcon hc0, mul_le_mul_of_nonneg_left hcon hs]
  by_contra hcon
  push_neg at hcon
  nlinarith [mul_le_mul_of_nonneg_left hd.le hs, mul_le_mul_of_nonneg_left hca hc0,
             mul_le_mul_of_nonneg_left hcon hc0, mul_lt_mul_of_pos_left hkey (show (0:ℝ) < c by linarith)]

/-- **(U1), the core** [T]: `c sφ + s dy < 1` from `dy < s`, `0 < s`, `sφ ≤ c`, `c² + s² = 1`. -/
theorem u1_core (c s sphi dy : ℝ) (h1 : c ^ 2 + s ^ 2 = 1) (hc : 0 < c) (hs : 0 < s) (hsphi : sphi ≤ c)
    (hdy : dy < s) : c * sphi + s * dy < 1 := by
  nlinarith [mul_le_mul_of_nonneg_left hsphi hc.le, mul_lt_mul_of_pos_left hdy hs]

/-- **(U9), the top vertex of `T_u`** [T]: `σ = sφ² − sφ c + cφ dy < 1` when `dy < c + s + cφ + sφ − 1.82`,
`0 ≤ sφ ≤ cφ ≤ 1`, `cφ² + sφ² = 1`, `c ≥ 0.7071`, `c + s ≤ 1.4143`. -/
theorem u9_core (c s cphi sphi dy : ℝ) (hphi : cphi ^ 2 + sphi ^ 2 = 1) (hs0 : 0 ≤ sphi) (hsc : sphi ≤ cphi)
    (hc1 : cphi ≤ 1) (hc : 7071 / 10000 ≤ c) (hw : c + s ≤ 14143 / 10000)
    (hdy : dy < c + s + cphi + sphi - 182 / 100) :
    sphi ^ 2 - sphi * c + cphi * dy < 1 := by
  have hcpos : 0 < cphi := by nlinarith
  have hsphi_le : sphi ≤ 7072 / 10000 := by nlinarith
  have key : cphi * (sphi + (c + s) - 182 / 100) < sphi * c := by
    by_cases h : sphi ≤ 4057 / 10000
    · nlinarith [mul_le_mul_of_nonneg_left hw hcpos.le, mul_nonneg hs0 (show (0:ℝ) ≤ c by linarith)]
    · push_neg at h
      nlinarith [mul_le_mul_of_nonneg_left hw hcpos.le, mul_lt_mul_of_pos_left h (show (0:ℝ) < c by linarith)]
  nlinarith [mul_lt_mul_of_pos_left hdy hcpos]

/-- **(F1) X is high** [T]: `X_top > s̄ − 1`, `s̄ ≥ 3.82`, `X_top − X_low ≤ 1.4143`: `X_low > 1.4057 > 1 > h_v`. -/
theorem x_high (side xtop xlow : ℝ) (hside : 382 / 100 ≤ side) (htop : side - 1 < xtop)
    (hw : xtop - xlow ≤ 14143 / 10000) : 14057 / 10000 < xlow := by linarith

/-- H1–H3 at a side in `[3.82, ŝ]` (ring_domain.md, the hypotheses): opaque. -/
opaque JamCorner : Prop
/-- The ring inequalities (U3)–(U6) + (U8) of strip_enclosure.md §3.1 — NOT consequences of H1–H5
(ring_domain.md §2): opaque. -/
opaque RingIneq : Prop

/-- **STRIP₂-IN-JAM** [T-prose] (ring_domain.md §5 = strip_enclosure.md §1–§3 with (D1), (D2), (U1), (U2), (U9)
derived): under H1–H3 and the ring inequalities no unit square of the quadrant interior-disjoint from `C` and `X`
has an interior point in `T_u ∖ C`. -/
axiom strip_two_in_jam (hjam : JamCorner) (hring : RingIneq) (Q : Set RP)
    (h : PackingCert.S11.OpenLemmas.StripPlug.TwoFree Q) :
    ¬ PackingCert.S11.OpenLemmas.ThreeLemmas.InStrip Q

/-- **The BL sectors of a JAM corner reduce to `pair3`** [T from `strip_two_in_jam`]: A267's
`strip_in_ring_of_enclosure` with `RingDomain` replaced by `JamCorner ∧ RingIneq`. -/
theorem strip_two_in_ring_of_jam (hjam : JamCorner) (hring : RingIneq)
    (hsub : ∀ Q, PackingCert.S11.OpenLemmas.ThreeLemmas.JamSectorFree Q →
      PackingCert.S11.OpenLemmas.StripPlug.TwoFree Q)
    (hcover : ∀ Q, PackingCert.S11.OpenLemmas.ThreeLemmas.JamSectorFree Q →
      ¬ PackingCert.S11.OpenLemmas.ThreeLemmas.InStrip Q →
      PackingCert.S11.OpenLemmas.ThreeLemmas.Pair3Free Q)
    (hpair3 : ∀ Q, ¬ PackingCert.S11.OpenLemmas.ThreeLemmas.Pair3Free Q) (Q : Set RP) :
    ¬ PackingCert.S11.OpenLemmas.ThreeLemmas.JamSectorFree Q :=
  fun h => hpair3 Q (hcover Q h (strip_two_in_jam hjam hring Q (hsub Q h)))

#print axioms low_core
#print axioms lh_gt_one
#print axioms u1_core
#print axioms u9_core
#print axioms x_high
#print axioms strip_two_in_ring_of_jam

end PackingCert.S11.OpenLemmas.RingDomain
