import Mathlib.Data.Real.Basic
import Mathlib.Data.Set.Prod
import Mathlib.Order.Interval.Set.Basic
import Mathlib.Order.ConditionallyCompleteLattice.Basic
import Mathlib.Topology.Instances.Real.Lemmas
import Mathlib.Tactic
import PackingCertMathlib.Bridge

/-!
# The composed optimality theorem for s(11) — formal STATEMENT (A62, checklist item F3)

This file states the top-level theorem of the optimality programme —

  `s(11) = ŝ`, the second real root of
  `x⁸ − 20x⁷ + 178x⁶ − 842x⁵ + 1923x⁴ − 496x³ − 6754x² + 12420x − 6865`,
  with equality attained, up to a symmetry of the container and a relabelling,
  only by Trump's configuration —

with every leaf family of the current proof plan as a NAMED `axiom`.  Nothing beyond the
composition glue is proved here; `#print axioms` on the three theorems at the bottom lists
exactly the declared hypotheses (plus `propext, Classical.choice, Quot.sound` from Mathlib).
Each axiom carries, in its docstring, the lab artefact that is supposed to discharge it and
its status as of 2026-09-01.  Discharging an axiom = replacing it by a definition/theorem
without changing any statement that mentions it.

The point of the file (per `docs/publication_checklist.md` F3) is to force the definition of
"packing", the quantifier order, and the exact form of each leaf obligation.  Every ambiguity
this forced is recorded in `attempts/A62-trust-ledger/notes/findings.md` (F-numbered) and the
load-bearing ones are repeated in the docstrings below.

## Definitional debt (opaque layers, declared as axioms)

* `StratumIdx / trumpStratum / InStratum` — the Young-form skeleton census (A53) is not yet a
  formal definition; the stratum predicate is opaque here.  NOTE the intended semantics is
  "the selected minimiser's skeleton is EXACTLY this class" (see `stratum_kill` docstring for
  why the certificate-native "contains these pins" reading would make the axiom false).
* `shat` — tied to the octic only through `shat_spec` (checklist S3: no root-isolation
  certificate in `certs/` yet).
* `zhat` — the exact Trump configuration; formal target: definable from A22's Krawczyk
  existence certificate once replayed in the `t = tan(θ/2)` parametrisation (A28 §4, F6).
* `rBasin` — the basin radius.  A22/A36 certify 3.7e-3 in `(c, θ)` coordinates; this file's
  configuration space is `(c, t)`, and no certified radius exists in `t` coordinates yet
  (findings F5).
-/

namespace PackingCert
namespace S11

noncomputable section

open Set

/-! ## The packing problem, set level -/

/-- The closed container `[0,s]²`. -/
def container (s : ℝ) : Set RP := Icc (0 : ℝ) s ×ˢ Icc (0 : ℝ) s

/-- A **packing** of `n` unit squares at side `s`: `n` closed unit squares (`IsUnitSquare`,
from `Bridge.lean`: congruent copies of `[0,1]²`), each contained in the closed container,
with pairwise disjoint **interiors** (contacts allowed — Trump's packing has 56 of them;
`Disjoint (Q i) (Q j)` on the closed sets, as in the A28 upper-bound theorem, would be the
WRONG notion here: it is strictly stronger and does not admit the extremal packing).
Findings F1. -/
structure IsPacking (n : ℕ) (s : ℝ) (Q : Fin n → Set RP) : Prop where
  unit : ∀ i, IsUnitSquare (Q i)
  contained : ∀ i, Q i ⊆ container s
  interiorDisjoint : ∀ i j, i ≠ j → Disjoint (interior (Q i)) (interior (Q j))

/-- `n` unit squares fit in `[0,s]²`. Monotone in `s` by construction of `container`. -/
def Fits (n : ℕ) (s : ℝ) : Prop := ∃ Q : Fin n → Set RP, IsPacking n s Q

/-- `s(n)`, as an infimum (checklist S2).  `attained` below is the statement that the
infimum is a minimum (drain lemma D1). -/
def sPack (n : ℕ) : ℝ := sInf {s : ℝ | Fits n s}

/-! ## The packing problem, configuration level (tan-half parametrisation) -/

/-- `cos θ` as a rational function of `t = tan(θ/2)`. -/
def cosT (t : ℝ) : ℝ := (1 - t ^ 2) / (1 + t ^ 2)

/-- `sin θ` as a rational function of `t = tan(θ/2)`. -/
def sinT (t : ℝ) : ℝ := 2 * t / (1 + t ^ 2)

/-- A parametrised square: centre `(cx, cy)`, orientation `t = tan(θ/2) ∈ [0,1]`
(`θ ∈ [0°, 90°]`; `t = 0` and `t = 1` denote the same square set — findings F8). -/
structure PSq where
  cx : ℝ
  cy : ℝ
  t : ℝ

/-- The unit edge vector `(cos θ, sin θ)` of a parametrised square. -/
def edir (q : PSq) : RP := (cosT q.t, sinT q.t)

/-- The base corner: centre minus `(e + e⊥)/2`. -/
def baseCorner (q : PSq) : RP :=
  (q.cx - (cosT q.t - sinT q.t) / 2, q.cy - (cosT q.t + sinT q.t) / 2)

/-- The closed unit square denoted by a parametrised square (via `Bridge.sqSet`). -/
def PSq.set (q : PSq) : Set RP := sqSet (baseCorner q) (edir q)

/-- A configuration: 11 parametrised squares — the 33 coordinates
`(cxᵢ, cyᵢ, tᵢ)` every certificate family speaks about. -/
abbrev Cfg := Fin 11 → PSq

/-- A configuration is a packing at side `s`. -/
def CfgPacking (s : ℝ) (z : Cfg) : Prop :=
  (∀ i, (z i).t ∈ Icc (0 : ℝ) 1) ∧ IsPacking 11 s fun i => (z i).set

/-! ## Symmetries of the container -/

/-- A symmetry of the container `[0,s]²`: a plane map that preserves squared Euclidean
distance and maps the container onto itself.  For `s > 0` these are exactly the 8 elements
of the dihedral group D₄, but the composition below never needs that classification. -/
structure IsCtrSym (s : ℝ) (f : RP → RP) : Prop where
  isometry : ∀ p q, sqdist (f p) (f q) = sqdist p q
  maps : f '' container s = container s

theorem IsCtrSym.comp {s : ℝ} {f g : RP → RP} (hf : IsCtrSym s f) (hg : IsCtrSym s g) :
    IsCtrSym s (f ∘ g) where
  isometry p q := by
    simp only [Function.comp_apply, hf.isometry, hg.isometry]
  maps := by rw [Set.image_comp, hg.maps, hf.maps]

/-! ## The algebraic value -/

/-- Trump's octic (A03; Ellsworth 2023). -/
def trumpOctic (x : ℝ) : ℝ :=
  x ^ 8 - 20 * x ^ 7 + 178 * x ^ 6 - 842 * x ^ 5 + 1923 * x ^ 4 - 496 * x ^ 3
    - 6754 * x ^ 2 + 12420 * x - 6865

/-- **ŝ = 3.877083590022813…**, the conjectured value of `s(11)`. Opaque; specified only
through `shat_spec`. -/
axiom shat : ℝ

/-- **[S3 — root isolation]** ŝ is the unique root of the octic in
`[3.877083, 3.877084]`.  STATUS: the octic and a 60-digit solution exist (A03); no exact
isolation certificate (Sturm sequence / sign changes at rational points) is in `certs/`.
Once one exists this axiom becomes a theorem and `shat` a definition.  Findings F7. -/
axiom shat_spec :
    trumpOctic shat = 0 ∧ shat ∈ Icc (3877083 / 1000000 : ℝ) (3877084 / 1000000) ∧
      ∀ x ∈ Icc (3877083 / 1000000 : ℝ) (3877084 / 1000000), trumpOctic x = 0 → x = shat

/-- The window on which every per-stratum obligation is stated: `[3.82, ŝ]`.
The lower end is Theorem 1 (`lb_382`); certificates are produced on the rational
superset `[191/50, 969271/250000]` (A56's window), which contains this one. -/
def wnd : Set ℝ := Icc (191 / 50 : ℝ) shat

/-! ## The named hypotheses (the leaf families of the proof plan) -/

/-- **[D1 — attainment]** `{s | Fits 11 s}` has a least element.  STATUS: PROVED in prose
(`docs/proofs/drain_lemma.md` D1, compactness); not yet formalised (needs `Fits` closed:
Hausdorff-limit argument on the configuration representation). -/
axiom attained : ∃ m, IsLeast {s : ℝ | Fits 11 s} m

/-- **[parametrisation]** Every set-level packing is represented by a configuration: each
unit square is `PSq.set` of some `(cx, cy, t)` with `t ∈ [0,1]`.  Elementary (every unit
square is a rotation of an axis-parallel one; `θ ∈ [0°,90°]` suffices; `tan(θ/2)`
surjects onto `[0,1]`), but load-bearing for every certificate family — it is the same
lemma the measure-bridge (F2) needs, stated once.  STATUS: unproved prose. -/
axiom parametrize : ∀ {n : ℕ} {s : ℝ} (Q : Fin n → Set RP), IsPacking n s Q →
    ∃ z : Fin n → PSq, (∀ i, (z i).t ∈ Icc (0 : ℝ) 1) ∧ ∀ i, Q i = (z i).set

/-- **[Theorem 1 — s(11) ≥ 3.82]** STATUS: certificate
`certs/measure_certificate_3.82.json` + two independent exact verifiers; Lean proves the
checker returns `true` (`s11_ge_3_82`, `native_decide`); the bridge "checker = true ⇒ every
unit square has mass ≥ 1 ⇒ no 11-packing" is prose (checklist F2, A28 §7 item 4). -/
axiom lb_382 : ∀ s : ℝ, Fits 11 s → (191 / 50 : ℝ) ≤ s

/-- **[UB at ŝ exactly]** Trump's configuration and the fact that it is a packing at side
ŝ.  STATUS: OPEN as a certificate — the strongest Lean-checked upper bound is
`s(11) ≤ 3.877083591023 > ŝ` (`trump11_tight_ok`), and `checkPacking` requires strictly
positive separation margins, so no certificate of the current UB family can EVER certify
the contact-closed packing at ŝ itself.  Intended discharge: A22's Krawczyk existence
certificate (exact contact solution, feasible), replayed in `t`-parametrisation (F6) —
or a closedness argument (`Fits` closed + rational certificates at sides ↓ ŝ).
Findings F2 — this obligation was previously implicit. -/
axiom zhat : Cfg

/-- See `zhat`. -/
axiom trump_packs_at_shat : CfgPacking shat zhat

/-- **[census — definitional debt]** Index type of the stratification (intended: the 163
D4 classes of the A53 Young-form census; kept opaque until the census definition is
formalised — checklist H2's independent re-enumeration then gets a formal target). -/
axiom StratumIdx : Type

/-- The distinguished stratum: Trump's `k = 5` skeleton class (`trump5`). -/
axiom trumpStratum : StratumIdx

/-- `InStratum i s z`: the configuration `z`, as a packing at side `s`, has skeleton
EXACTLY of class `i`.  The side parameter is essential: skeleton pins are anchored to the
walls of `[0,s]²`, so the predicate is a different subset of configuration space at every
`s` — this is what makes window transfer (H6) a per-certificate obligation rather than a
bookkeeping step.  Findings F4/F6. -/
axiom InStratum : StratumIdx → ℝ → Cfg → Prop

/-- **[H1 + H2 — selection + exhaustiveness]** If the minimum is attained at
`m ∈ [3.82, ŝ]`, then SOME minimiser (the k-maximal slide-stuck selected one) lies in some
stratum.  Note the quantifier: this produces an existential witness, NOT a statement about
every minimiser — the uniqueness clause therefore needs the separate, strictly stronger
`unique_transfer` below (findings F3, the largest hole this file forced).  STATUS: L6/CC-2
selection lemma in attempt notes (A53/A58), census exact but single-implementation;
degenerate slide cases (H1) unwritten. -/
axiom stratify : ∀ m : ℝ, IsLeast {s : ℝ | Fits 11 s} m → m ∈ wnd →
    ∃ (z : Cfg) (i : StratumIdx), CfgPacking m z ∧ InStratum i m z

/-- **[per-stratum kills, window form]** No packing at any side `s ∈ [3.82, ŝ]` has
skeleton exactly of a non-Trump class.  This single axiom fuses THREE obligations that are
separate artefacts in the lab, and the fusion is forced (A56 refuted "kill at s₀ + transfer
principle" as a factorisation — a general transfer axiom would be FALSE):
(1) the certificate kills — 61 exact pin-set certificates (k=3:1, k=4:8, k=5:19+2 via A57
    sub-trees, k=6:33) + K1 upward cap for k ≥ 7;
(2) window coverage — A56/A61 parametric 4-D certificates; 12 strata + the A57 sub-tree
    kills + 2 sliver bands are s₀-only as of this commit;
(3) the k ≤ 4 tier — the K1-protected classes ({k4_03, k4_05, k4_06, k4_08, k4_11,
    corners4} and the ten k ≤ 3 classes) can NEVER be killed by the pin-certificate route
    (A55 sharpness); their exclusion must come from the "exactly" in `InStratum` (skeleton
    maximality: A58 clear-corner/exchange route, checklist H10 — OPEN).
Certificates natively prove the monotone form "no packing whose skeleton CONTAINS these
pins"; the composition needs the exact-skeleton form; the bridge is K1 + the census
containment lattice and must become a written lemma (findings F4).
FOURTH fused obligation (findings F9, checklist S4): a `verify_case` PASS speaks about
families of pairwise-DISJOINT closed squares, while this axiom quantifies over
interior-disjoint packings (contacts allowed — the minimiser has them).  The bridge is a
λ-scaling-with-pin-slack argument (scale to a nearby rational side inside the window,
where the scaled packing is strictly disjoint and, for point/small cores, still contains
the pins); it is applied implicitly at EVERY use of a kill and is written nowhere. -/
axiom stratum_kill : ∀ i : StratumIdx, i ≠ trumpStratum → ∀ s ∈ wnd, ∀ z : Cfg,
    CfgPacking s z → ¬InStratum i s z

/-- The basin radius (∞-norm, in `(cx, cy, t)` coordinates).  A22/A36 certify 3.7e-3 in
`(c, θ)` coordinates; `dθ/dt = 2/(1+t²) ≠ 1`, so the certified radius does NOT transfer
numerically to this coordinate system — the residual tree and the basin certificate must
be re-expressed in the SAME box (findings F5).  Opaque until then. -/
axiom rBasin : ℝ

/-- `z` lies in the certified rigidity box around Trump's configuration. -/
def InBasin (z : Cfg) : Prop := ∀ i,
  |(z i).cx - (zhat i).cx| ≤ rBasin ∧ |(z i).cy - (zhat i).cy| ≤ rBasin ∧
    |(z i).t - (zhat i).t| ≤ rBasin

/-- **[trump5 residual — A59/A60]** Every packing in the Trump stratum at side
`s ∈ [3.82, ŝ]` is, after a container symmetry and a relabelling, a packing landing inside
the rigidity basin.  STATUS: A60 campaign running (zone cover + residue ladders +
confinement, every kill an exact certificate); the low-`s` slab (H7/G-A59-7) and the
s-parametric form of the (K) leaves are open — as stated the axiom quantifies over the
whole window, which is exactly that open obligation.  The symmetry/relabelling is produced
by the D4 reduction inside the tree (H12; machine-checked at 3.84, re-proof at s₀ listed
as mechanical). -/
axiom trump_residual : ∀ s ∈ wnd, ∀ z : Cfg, CfgPacking s z → InStratum trumpStratum s z →
    ∃ (z' : Cfg) (f : RP → RP) (e : Equiv.Perm (Fin 11)),
      IsCtrSym s f ∧ CfgPacking s z' ∧ InBasin z' ∧ ∀ j, (z (e j)).set = f '' (z' j).set

/-- **[A22/A36 — local rigidity at Trump]** Inside the basin box: every packing side is
≥ ŝ, and a packing at side exactly ŝ inside the box IS Trump's configuration.  STATUS:
certified by Python interval arithmetic (mpmath.iv Krawczyk + Farkas, standalone
re-checker, corruption gates); Lean replay blocked on interval trigonometry until the
certificate is re-emitted in `t` (A28 §4 / checklist F6); coordinate-box caveat as in
`rBasin`. -/
axiom basin : ∀ z : Cfg, InBasin z →
    (∀ s : ℝ, CfgPacking s z → shat ≤ s) ∧ (CfgPacking shat z → z = zhat)

/-- **[uniqueness transfer]** EVERY packing at side ŝ has, after a container symmetry and
a relabelling, a representative that lies in some stratum.  STATUS: OPEN, and — finding F3
— NOT implied by any written lemma: the selection lemma (L6/CC-2) produces a DIFFERENT
minimiser (slides move squares), so it proves the bound but not uniqueness for the
original packing.  Candidate route: slides at the optimal side move through packings at
side ŝ; once the slid representative is known to be `zhat`, the basin equality clause
applied along the (continuous) slide path forces the path constant.  Until this (or an
equivalent) is written, the uniqueness half of S1 has no proof sketch on file. -/
axiom unique_transfer : ∀ z : Cfg, CfgPacking shat z →
    ∃ (z' : Cfg) (f : RP → RP) (e : Equiv.Perm (Fin 11)) (i : StratumIdx),
      IsCtrSym shat f ∧ CfgPacking shat z' ∧ InStratum i shat z' ∧
        ∀ j, (z (e j)).set = f '' (z' j).set

/-! ## Composition glue (the only proofs in this file) -/

theorem shat_ge_382 : (191 / 50 : ℝ) ≤ shat := by
  have h := shat_spec.2.1.1
  norm_num at h ⊢
  linarith

theorem shat_mem_wnd : shat ∈ wnd := ⟨shat_ge_382, le_refl _⟩

theorem fits_shat : Fits 11 shat := ⟨fun i => (zhat i).set, trump_packs_at_shat.2⟩

/-- **The lower bound, operative form**: no 11-packing at any side below ŝ. -/
theorem s_eleven_ge : ∀ s : ℝ, Fits 11 s → shat ≤ s := by
  intro s hs
  obtain ⟨m, hm⟩ := attained
  have hms : m ≤ s := hm.2 hs
  have h382 : (191 / 50 : ℝ) ≤ m := lb_382 m hm.1
  have hmshat : m ≤ shat := hm.2 fits_shat
  have hwin : m ∈ wnd := ⟨h382, hmshat⟩
  obtain ⟨z, i, hz, hstr⟩ := stratify m hm hwin
  have hshatm : shat ≤ m := by
    by_cases hi : i = trumpStratum
    · subst hi
      obtain ⟨z', f, e, hsym, hz', hbasin, hrel⟩ := trump_residual m hwin z hz hstr
      exact (basin z' hbasin).1 m hz'
    · exact absurd hstr (stratum_kill i hi m hwin z hz)
  linarith

/-- **The composed optimality theorem**: `s(11) = ŝ`. -/
theorem s_eleven_eq : sPack 11 = shat := by
  obtain ⟨m, hm⟩ := attained
  have h1 : sPack 11 = m := hm.csInf_eq
  have h2 : shat ≤ m := s_eleven_ge m hm.1
  have h3 : m ≤ shat := hm.2 fits_shat
  rw [h1]
  linarith

/-- **The uniqueness clause**: every packing at side ŝ is, up to a symmetry of the
container and a relabelling, Trump's packing. -/
theorem s_eleven_unique : ∀ Q : Fin 11 → Set RP, IsPacking 11 shat Q →
    ∃ (f : RP → RP) (e : Equiv.Perm (Fin 11)),
      IsCtrSym shat f ∧ ∀ i, Q i = f '' (zhat (e i)).set := by
  intro Q hQ
  obtain ⟨z, hzt, hzQ⟩ := parametrize Q hQ
  have hz : CfgPacking shat z := by
    refine ⟨hzt, ?_⟩
    have hfun : (fun i => (z i).set) = Q := funext fun i => (hzQ i).symm
    rw [hfun]
    exact hQ
  obtain ⟨z', f1, e1, i, hsym1, hz', hstr, hrel1⟩ := unique_transfer z hz
  have hi : i = trumpStratum := by
    by_contra hi
    exact stratum_kill i hi shat shat_mem_wnd z' hz' hstr
  subst hi
  obtain ⟨z'', f2, e2, hsym2, hz'', hbasin, hrel2⟩ :=
    trump_residual shat shat_mem_wnd z' hz' hstr
  have hzz : z'' = zhat := (basin z'' hbasin).2 hz''
  refine ⟨f1 ∘ f2, (e2.trans e1).symm, hsym1.comp hsym2, fun j => ?_⟩
  have key : ∀ k, (z ((e2.trans e1) k)).set = (f1 ∘ f2) '' (zhat k).set := by
    intro k
    have h1 := hrel1 (e2 k)
    have h2 := hrel2 k
    rw [hzz] at h2
    rw [Equiv.trans_apply, h1, h2, Set.image_comp]
  have hk := key ((e2.trans e1).symm j)
  rw [Equiv.apply_symm_apply] at hk
  rw [hzQ j, hk]

end

end S11
end PackingCert
