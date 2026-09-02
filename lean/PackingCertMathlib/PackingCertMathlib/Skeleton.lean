import Mathlib.Data.Real.Basic
import Mathlib.Data.Finset.Basic
import Mathlib.Tactic
import PackingCertMathlib.Parametrize
import PackingCertMathlib.Dilation

/-!
# K1 and the monotone→exact bridge: the combinatorial spine (A68, depgraph nodes
B.K1 / B.EXACT)

`docs/proofs/instratum_bridge.md` E.1(i) and E.2, formalised as far as today's formal
census reaches.  The Young-form census itself (A53: 1110 slot-sets / 163 D4 classes) is
NOT yet a Lean definition — `InStratum` stays opaque in `TopLevel.lean` (checklist
F11/H2) — so this file provides:

* the slot model: a `Slot` is a container corner + a Young cell; `slotCentre` places it at
  side `s` (affine, `α + β·s` with `β ∈ {0,1}`, matching A56 P1);
* `OccupiesSlot` — a parametrised square sits axis-aligned exactly on a slot;
* `ContainsPins` — the certificate-native monotone predicate "the packing's skeleton
  CONTAINS pin-set `S`" (injective slot assignment);
* **K1(i)** (`containsPins_mono` / `kill_mono`): kills climb containment — a kill of `S`
  in monotone form empties the monotone class of every `T ⊇ S`.  In this indexed slot
  model the prose step "sub-diagram cells keep their `(i, j)` offsets, so
  `slots_S(s) ⊆ slots_T(s)`" is the inclusion `S ⊆ T` itself, and K1(i) is the
  restriction of the assignment;
* **M→E** (`monotone_to_exact`): the bridge from a monotone kill to an exact-class
  emptiness statement, with the census interface as an explicit hypothesis `hface`
  ("membership in the exact class implies containing the class tuple, after the D4
  normalisation").  When the census lands formally (F11/H2), `hface` is discharged per
  class by reflexivity of `≤` plus the D4 bookkeeping of E.2 (equivariance of the slot
  map, machine-checked computationally by A67 R8), and this theorem converts each
  certificate PASS + Lemma B (`Dilation.lean`) into a `stratum_kill` instance.

NOT formalisable yet, and recorded as the obligation: the census definition itself
(`Simp`, the skeleton-of-a-packing function) — without it `hface` cannot be a theorem;
and K1(ii) ("aliveness descends") is a statement about LP values τ*, i.e. about what
certificates CAN exist — completeness, not soundness — and has no place in the trusted
composition.
-/

namespace PackingCert
namespace S11

noncomputable section

open Set

/-- A pin slot: a container corner (`0` = bottom-left, `1` = bottom-right, `2` =
top-right, `3` = top-left) and a Young cell `(cellx, celly)` counted inward from that
corner. -/
structure Slot where
  corner : Fin 4
  cellx : ℕ
  celly : ℕ
deriving DecidableEq

/-- The slot's centre at container side `s` — affine in `s`, `α + β·s` with `β ∈ {0,1}`
and `α = ±(cell + 1/2)` (A56 P1; `|α| ≤ 5/2` on the census, where cells are `< 3`). -/
def slotCentre (s : ℝ) (a : Slot) : RP :=
  match a.corner with
  | 0 => ((a.cellx : ℝ) + 1 / 2, (a.celly : ℝ) + 1 / 2)
  | 1 => (s - ((a.cellx : ℝ) + 1 / 2), (a.celly : ℝ) + 1 / 2)
  | 2 => (s - ((a.cellx : ℝ) + 1 / 2), s - ((a.celly : ℝ) + 1 / 2))
  | 3 => ((a.cellx : ℝ) + 1 / 2, s - ((a.celly : ℝ) + 1 / 2))

/-- A pin-set: a finite set of slots.  A Young 4-tuple is such a set whose cells form a
Young diagram at each corner; nothing in K1(i) needs the diagram condition, so the lemma
is stated for arbitrary pin-sets (it is strictly stronger). -/
abbrev PinSet : Type := Finset Slot

/-- The square `q` occupies the slot centred at `c`: its point set is exactly the
axis-aligned unit square there.  (By `set_of_t_zero` / `set_of_t_one`, a parametrised
square with `t ∈ {0, 1}` centred at `c` occupies it.) -/
def OccupiesSlot (q : PSq) (c : RP) : Prop :=
  q.set = Icc (c.1 - 1 / 2) (c.1 + 1 / 2) ×ˢ Icc (c.2 - 1 / 2) (c.2 + 1 / 2)

/-- The certificate-native monotone skeleton predicate: the configuration `z` CONTAINS
pin-set `S` at side `s` — an injective assignment of distinct squares to the slots of
`S`, each occupying its slot. -/
def ContainsPins (S : PinSet) (s : ℝ) (z : Fin 11 → PSq) : Prop :=
  ∃ f : Slot → Fin 11, Set.InjOn f ↑S ∧ ∀ a ∈ S, OccupiesSlot (z (f a)) (slotCentre s a)

/-! ## K1(i): kills climb containment -/

/-- **Lemma K1(i), aliveness half** (`instratum_bridge.md` E.1(i)): containment is
monotone — a packing whose skeleton contains `T` contains every `S ⊆ T`.  Restriction of
the slot assignment. -/
theorem containsPins_mono {S T : PinSet} (hST : S ⊆ T) {s : ℝ} {z : Fin 11 → PSq}
    (h : ContainsPins T s z) : ContainsPins S s z := by
  obtain ⟨f, hinj, hocc⟩ := h
  exact ⟨f, hinj.mono (Finset.coe_subset.mpr hST), fun a ha => hocc a (hST ha)⟩

/-- **Lemma K1(i), kill half**: a monotone kill of `S` empties the monotone class of
every `T ⊇ S`. -/
theorem kill_mono {S T : PinSet} (hST : S ⊆ T) {s : ℝ} {P : (Fin 11 → PSq) → Prop}
    (kill : ∀ z, P z → ¬ContainsPins S s z) :
    ∀ z, P z → ¬ContainsPins T s z :=
  fun z hz hT => kill z hz (containsPins_mono hST hT)

/-! ## M→E: the monotone→exact bridge, census interface explicit -/

/-- **Lemma M→E** (`instratum_bridge.md` E.2), with the census interface as the
hypothesis `hface`: if membership in the exact skeleton class `Exact` implies containing
the (D4-normalised) class tuple `T`, and some `S ⊆ T` carries a monotone kill, then the
exact class is empty.  `hface` is the not-yet-formal part (census definition, F11/H2 +
E.2's D4 bookkeeping, cross-checked computationally by A67 R8); everything else is K1(i).
-/
theorem monotone_to_exact {S T : PinSet} (hST : S ⊆ T) {s : ℝ}
    {P Exact : (Fin 11 → PSq) → Prop}
    (hface : ∀ z, P z → Exact z → ContainsPins T s z)
    (kill : ∀ z, P z → ¬ContainsPins S s z) :
    ∀ z, P z → ¬Exact z :=
  fun z hz hex => kill_mono hST kill z hz (hface z hz hex)

/-- A parametrised square with `t = 0` or `t = 1` centred on a slot occupies it. -/
theorem occupiesSlot_of_axis {q : PSq} {c : RP} (ht : q.t = 0 ∨ q.t = 1)
    (hcx : q.cx = c.1) (hcy : q.cy = c.2) : OccupiesSlot q c := by
  rcases ht with h | h
  · rw [OccupiesSlot, set_of_t_zero h, hcx, hcy]
  · rw [OccupiesSlot, set_of_t_one h, hcx, hcy]

end

end S11
end PackingCert
