import Mathlib.Data.Real.Basic
import Mathlib.Data.Set.Prod
import Mathlib.Order.Interval.Set.Basic
import Mathlib.Order.ConditionallyCompleteLattice.Basic
import Mathlib.Topology.Instances.Real.Lemmas
import Mathlib.Tactic
import PackingCertMathlib.Bridge
import PackingCertMathlib.Parametrize
import PackingCertMathlib.Measure382
import PackingCertMathlib.Attain
import PackingCertMathlib.ThetaT

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
its status as of 2026-09-02 (A64).  Discharging an axiom = replacing it by a
definition/theorem without changing any statement that mentions it.  Discharged so far:
`shat`/`shat_spec` and `rBasin` (A63); `parametrize` (A64, `Parametrize.lean`) and
`lb_382` (A64, `MeasureBridge.lean` + `Measure382.lean` — the measure bridge formalised,
so `s(11) ≥ 3.82` is an end-to-end Lean theorem whose only extra axiom is
the `native_decide` evaluation axiom); `trump_packs_at_shat` (A64) is now a theorem
from the finer split `shatA22` + `trump_packs_at_shatA22` (certified) +
`shatA22_eq_shat` (the open identity); `attained` (A68, `Attain.lean` — drain lemma D1,
compactness in coordinates).  12 named axioms remain, but only
`shatA22_eq_shat` and the genuinely-open leaf families carry open mathematics.

The point of the file (per `docs/publication_checklist.md` F3) is to force the definition of
"packing", the quantifier order, and the exact form of each leaf obligation.  Every ambiguity
this forced is recorded in `attempts/A62-trust-ledger/notes/findings.md` (F-numbered) and the
load-bearing ones are repeated in the docstrings below.

## Definitional debt (opaque layers, declared as axioms)

* `StratumIdx / trumpStratum / InStratum` — the Young-form skeleton census (A53) is not yet a
  formal definition; the stratum predicate is opaque here.  NOTE the intended semantics is
  "the selected minimiser's skeleton is EXACTLY this class" (see `stratum_kill` docstring for
  why the certificate-native "contains these pins" reading would make the axiom false).
* `shat` — DISCHARGED (A63): a definition (unique octic root in the isolating interval),
  with `shat_spec` a theorem; certificate `certs/octic_root_isolation.json` +
  `certs/verify_sturm.py` (checklist S3).
* `zhat` — the exact Trump configuration; formal target: definable from A22's Krawczyk
  existence certificate once replayed in the `t = tan(θ/2)` parametrisation (A28 §4, F6);
  route decision and the ŝ_A22 = ŝ identification gap: `docs/proofs/attainment_ub.md`.
* `rBasin` — DISCHARGED (A63): a definition, 3/2000, justified by the exact θ↔t transfer
  constants (`docs/proofs/theta_t_transfer.md`).
-/

namespace PackingCert
namespace S11

noncomputable section

open Set

/-! ## The packing problem, set level

`container`, `IsPacking` and `Fits` live in `PackingCertMathlib/Parametrize.lean` since A64
(moved there unchanged, same namespace, so the measure bridge can consume them). -/

/-- `s(n)`, as an infimum (checklist S2).  `attained` below is the statement that the
infimum is a minimum (drain lemma D1). -/
def sPack (n : ℕ) : ℝ := sInf {s : ℝ | Fits n s}

/-! ## The packing problem, configuration level (tan-half parametrisation)

The configuration layer (`cosT`, `sinT`, `PSq`, `edir`, `baseCorner`, `PSq.set`)
lives in `PackingCertMathlib/Parametrize.lean` since A64 (moved there unchanged,
same namespace, so that the parametrisation lemma and the measure bridge can use
it without importing this statement file). -/

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

/-- The Taylor expansion of the octic at `a = 3877083/1000000`: every coefficient above
degree 0 is POSITIVE (certificate `certs/octic_root_isolation.json`, checker
`certs/verify_sturm.py`), so the octic is strictly increasing on `[a, ∞)` by pure algebra —
no calculus enters the uniqueness argument. -/
private lemma trumpOctic_taylor (x : ℝ) :
    trumpOctic x =
      -(89907663116138493411101284007125861208828959 /
          1000000000000000000000000000000000000000000000000)
        + (19047448354002451638684536547366689841780627 /
            125000000000000000000000000000000000000000)
            * (x - 3877083 / 1000000)
        + (165507240204079365683276620593074875583 / 250000000000000000000000000000000000)
            * (x - 3877083 / 1000000) ^ 2
        + (140531576756507493150247963879501 / 125000000000000000000000000000)
            * (x - 3877083 / 1000000) ^ 3
        + (75650550884558810753780247 / 100000000000000000000000)
            * (x - 3877083 / 1000000) ^ 4
        + (31128529333060215509 / 125000000000000000)
            * (x - 3877083 / 1000000) ^ 5
        + (14024503122223 / 250000000000)
            * (x - 3877083 / 1000000) ^ 6
        + (1377083 / 125000)
            * (x - 3877083 / 1000000) ^ 7
        + (x - 3877083 / 1000000) ^ 8 := by
  unfold trumpOctic; ring

/-- The octic strictly increases to the right of `a = 3877083/1000000`. -/
private lemma trumpOctic_strictMono {x y : ℝ}
    (hx : (3877083 / 1000000 : ℝ) ≤ x) (hxy : x < y) : trumpOctic x < trumpOctic y := by
  rw [trumpOctic_taylor x, trumpOctic_taylor y]
  set u := x - 3877083 / 1000000 with hu_def
  set v := y - 3877083 / 1000000 with hv_def
  have hu : (0 : ℝ) ≤ u := by simp only [hu_def]; linarith
  have huv : u < v := by simp only [hu_def, hv_def]; linarith
  have huv' : u ≤ v := le_of_lt huv
  have h2 : u ^ 2 ≤ v ^ 2 := pow_le_pow_left₀ hu huv' 2
  have h3 : u ^ 3 ≤ v ^ 3 := pow_le_pow_left₀ hu huv' 3
  have h4 : u ^ 4 ≤ v ^ 4 := pow_le_pow_left₀ hu huv' 4
  have h5 : u ^ 5 ≤ v ^ 5 := pow_le_pow_left₀ hu huv' 5
  have h6 : u ^ 6 ≤ v ^ 6 := pow_le_pow_left₀ hu huv' 6
  have h7 : u ^ 7 ≤ v ^ 7 := pow_le_pow_left₀ hu huv' 7
  have h8 : u ^ 8 ≤ v ^ 8 := pow_le_pow_left₀ hu huv' 8
  linarith

private lemma trumpOctic_continuous : Continuous trumpOctic := by
  unfold trumpOctic; fun_prop

/-- **[S3 — root isolation, existence half]** sign change on the isolating interval. -/
private lemma trumpOctic_exists_root :
    ∃ x ∈ Icc (3877083 / 1000000 : ℝ) (3877084 / 1000000), trumpOctic x = 0 := by
  have hab : (3877083 / 1000000 : ℝ) ≤ 3877084 / 1000000 := by norm_num
  have hivt := intermediate_value_Icc hab trumpOctic_continuous.continuousOn
  have h0 : (0 : ℝ) ∈ Icc (trumpOctic (3877083 / 1000000)) (trumpOctic (3877084 / 1000000)) := by
    have ha : trumpOctic (3877083 / 1000000 : ℝ) < 0 := by unfold trumpOctic; norm_num
    have hb : 0 < trumpOctic (3877084 / 1000000 : ℝ) := by unfold trumpOctic; norm_num
    exact ⟨le_of_lt ha, le_of_lt hb⟩
  exact hivt h0

/-- **[S3 — root isolation]** the octic has exactly one root in `[3.877083, 3.877084]`.
Certificate: `certs/octic_root_isolation.json` (Sturm; the octic has exactly TWO real
roots, the other in `(-2, -1)`, so this root is the SECOND real root, as the theorem
statement requires), checker `certs/verify_sturm.py` (exact rational arithmetic, stdlib
only).  The Lean proof is certificate-free: IVT for existence, the all-positive Taylor
shift for uniqueness. -/
theorem trumpOctic_existsUnique :
    ∃! x : ℝ, x ∈ Icc (3877083 / 1000000 : ℝ) (3877084 / 1000000) ∧ trumpOctic x = 0 := by
  obtain ⟨x, hx, hfx⟩ := trumpOctic_exists_root
  refine ⟨x, ⟨hx, hfx⟩, ?_⟩
  rintro y ⟨hy, hfy⟩
  by_contra hne
  rcases lt_or_gt_of_ne hne with h | h
  · have := trumpOctic_strictMono hy.1 h
    rw [hfy, hfx] at this
    exact lt_irrefl 0 this
  · have := trumpOctic_strictMono hx.1 h
    rw [hfx, hfy] at this
    exact lt_irrefl 0 this

/-- **ŝ = 3.877083590022813…**, the value of `s(11)`: the unique (and second real) root of
the octic in `[3.877083, 3.877084]`.  A DEFINITION since A63 (was an axiom); tied to the
octic by the theorem `shat_spec` below. -/
noncomputable def shat : ℝ := trumpOctic_existsUnique.choose

/-- **[S3 — root isolation]** ŝ is the unique root of the octic in `[3.877083, 3.877084]`.
DISCHARGED (A63): was an axiom; now proved from `trumpOctic_existsUnique`
(certificate `certs/octic_root_isolation.json` + `certs/verify_sturm.py` document the
Sturm count and the second-root index; the Lean proof itself needs neither).
Findings F7 closed. -/
theorem shat_spec :
    trumpOctic shat = 0 ∧ shat ∈ Icc (3877083 / 1000000 : ℝ) (3877084 / 1000000) ∧
      ∀ x ∈ Icc (3877083 / 1000000 : ℝ) (3877084 / 1000000), trumpOctic x = 0 → x = shat := by
  obtain ⟨⟨hmem, hroot⟩, huniq⟩ := trumpOctic_existsUnique.choose_spec
  exact ⟨hroot, hmem, fun x hx hfx => huniq x ⟨hx, hfx⟩⟩

/-- The window on which every per-stratum obligation is stated: `[3.82, ŝ]`.
The lower end is Theorem 1 (`lb_382`); certificates are produced on the rational
superset `[191/50, 969271/250000]` (A56's window), which contains this one. -/
def wnd : Set ℝ := Icc (191 / 50 : ℝ) shat

/-! ## The named hypotheses (the leaf families of the proof plan) -/

/-- **[D1 — attainment]** `{s | Fits 11 s}` has a least element.  DISCHARGED (A68): was an
axiom; now the theorem `attained_thm` of `PackingCertMathlib/Attain.lean`
(`docs/proofs/drain_lemma.md` D1).  No Hausdorff limits: the coordinate feasible region
(33 square coordinates + the side, cut out by `t ∈ [0,1]`, the `set_subset_container_iff`
containment inequalities and pairwise non-overlap) is closed and bounded, the side
projection continuous; non-overlap is closed because the interior of a parametrised
square is EXACTLY the open `u/v` box (`mem_interior_iff_uv`).  Axioms: `propext,
Classical.choice, Quot.sound` only. -/
theorem attained : ∃ m, IsLeast {s : ℝ | Fits 11 s} m := attained_thm

/-!
**[parametrisation]** — every set-level packing is represented by a configuration
(`parametrize`).  DISCHARGED (A64): was an axiom here; now a THEOREM in
`PackingCertMathlib/Parametrize.lean` (the square's own 90° symmetry `sqSet_rot` brings the
edge vector into the closed first quadrant, then the half-angle substitution
`t = e₂/(1+e₁) ∈ [0,1]` is exact algebra — no transcendental functions).
Prose: `docs/proofs/parametrization.md`.
-/

/-- **[Theorem 1 — s(11) ≥ 3.82]** DISCHARGED (A64): was an axiom; now the end-to-end
theorem `s_eleven_ge_382` (`Measure382.lean`): the `native_decide` evaluation of
`checkMeasureI` on `certs/measure_certificate_3.82.json` composed with the FORMALISED
measure bridge (`MeasureBridge.lean` — checker soundness: interval arithmetic, grid
trigonometry, clip/sift/split/branch-and-bound, coverage, and the scaling/counting
argument; was the A28 §7 item 4 prose, checklist F2).  Axioms: `propext,
Classical.choice, Quot.sound, Lean.ofReduceBool`. -/
theorem lb_382 : ∀ s : ℝ, Fits 11 s → (191 / 50 : ℝ) ≤ s := s_eleven_ge_382

/-- **[UB at ŝ exactly]** Trump's configuration.  STATUS: OPEN as a whole, but SPLIT by
A64 into its certified and open parts (the A63 route decision, executed Lean-side):
route (a) — A22 Krawczyk existence + FEASIBILITY — certifies `Fits ŝ_A22` for the
INTRINSIC side `shatA22` of the contact solution (Python-interval TCB;
`trump_packs_at_shatA22` below); the whole algebraically-open residue is the single
identity axiom `shatA22_eq_shat`.  Route (b) remains REFUTED as a finite route
(`docs/proofs/attainment_ub.md` §2). -/
axiom zhat : Cfg

/-- **[UB at ŝ — intrinsic side]** The side of A22's unique contact solution ẑ in the
Krawczyk box `N = box(z0, 5e-4)`: `‖ẑ − z0‖∞ ≤ 1e-50`, and ẑ IS a packing at its own
side (A22 §4 feasibility).  Certified TODAY modulo the mpmath.iv trust item (TCB T3);
Lean replay = the t-reparametrised Krawczyk checker (A28 §4 / checklist F6). -/
axiom shatA22 : ℝ

/-- See `shatA22`: A22 feasibility, i.e. `Fits 11 shatA22` in configuration form.
Certified (Python-interval TCB; exact flush/coincidence arguments + interval SAT with
min margins 0.0249/0.549). -/
axiom trump_packs_at_shatA22 : CfgPacking shatA22 zhat

/-- **[UB at ŝ — the algebraic identity, now CERTIFICATE-BACKED]** `ŝ_A22 = ŝ_octic`.
CLOSED at the Python-certificate tier by A69 (`docs/proofs/attainment_ub.md` §7): the
(c-idl) saturated ideal-membership certificate `certs/cidl_identity.json`, checker
`certs/verify_cidl.py` (stdlib rationals; PASS 0.7 s; corruption gates fail loudly):

    e(t)·Δ(t)⁸·octic(S) = Σ_j q_j(t,S)·G_j

over the 13 reduced A22 contact rows on the certified exact-structure slice, with the
sign gate "e·Δ has no root in [3/10, 2/5] ∋ t̂" (exact Sturm).  Evaluating at the A22
point gives `octic ŝ_A22 = 0`; with A22's 1e-50 enclosure (`ŝ_A22 ∈ Icc 3.877083
3.877084`) and `shat_spec`'s uniqueness this yields `shatA22 = shat` (the octic's
SECOND real root; the other lies in `(-2,-1)`).  En route the tan-half minimal
polynomial `5t⁸−10t⁷−2t⁶+14t⁵+12t⁴−6t³+2t²+2t−1` is DERIVED (upgrading A22 §7 gap 2),
and A53 L4's "degree-7 coordinate / compositum 56" obstacle is VOID (spurious A03
minpoly annotations; every ẑ-coordinate lies in ℚ(t̂), degree 8).
* Still an AXIOM pending the named obligation CIDL-LEAN (attainment_ub.md §7.5):
  (i) `native_decide` replay of the identity + Sturm gates (Measure382Check isolation
  pattern), (ii) refined A22-interface axioms carrying "the generators vanish at ẑ,
  t̂ ∈ [3/10,2/5], ŝ_A22 ∈ Icc 3.877083 3.877084" in place of the opaque `shatA22` —
  then this becomes a theorem via `shat_spec`.  No new mathematics remains.
* S3-fallback: WITHOUT this axiom the remaining axioms still support the restated
  theorem `s(11) = ŝ_A22` (attainment_ub.md §5) — this decomposition is the Lean-side
  preparation for that restatement, keeping `shat`/`shat_spec` (A63) intact. -/
axiom shatA22_eq_shat : shatA22 = shat

/-- The composed upper-bound-at-ŝ statement — a THEOREM from the split (A64); its
`#print axioms` separates the certified feasibility from the open identity. -/
theorem trump_packs_at_shat : CfgPacking shat zhat :=
  shatA22_eq_shat ▸ trump_packs_at_shatA22

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
interior-disjoint packings (contacts allowed — the minimiser has them).
A63 STATUS UPDATE:
* (F9/S4) the λ-dilation bridge is now WRITTEN and proved:
  `docs/proofs/closed_disjoint_bridge.md` Lemma B + Corollary B′ (centre dilation to a
  certified rational side strictly above the packing's side; corpus containment margin
  ρ ≈ 1.0000009e-9, exactly positive, uniform across all 68 kill certificates).
* (F4) the monotone→exact bridge is written: `docs/proofs/instratum_bridge.md` (K1 +
  Lemma M→E); it covers exactly the certified classes, and records that the K1-protected
  tier is H10's business, in the target form H10-stuck (`unique_transfer.md` §3).
* (F6, SHARPENED) via Lemma B an s₀-only certificate reaches only sides within relative
  distance ~4e-10 below s₀ — i.e. NO side of `[3.82, ŝ]` at all (the gap to ŝ is
  ~1.06e-7 relative).  The window quantifier of this axiom is carried by parametric
  coverage + B′ for the 38(+A61) full-window classes; the A57 k5_11/k5_16 trees and any
  s₀-only stragglers instantiate NOTHING here until re-emitted (parametric form, or the
  slack-core fixed-side grid of `closed_disjoint_bridge.md` B.4).
* QUANTIFIER CAVEAT (A63, from `unique_transfer.md` §1): as stated this axiom quantifies
  over ALL packings.  For the K1-protected classes at `s = ŝ` that strength is equivalent
  to (a piece of) the uniqueness theorem and can never come from certificates; the
  non-circular discharge routes the uniqueness composition through teleport-stuck
  packings (H10-stuck) + Theorem U — see `unique_transfer.md`.  At sides `< ŝ` the
  low-k instances are needed only for the `stratify`-selected minimiser. -/
axiom stratum_kill : ∀ i : StratumIdx, i ≠ trumpStratum → ∀ s ∈ wnd, ∀ z : Cfg,
    CfgPacking s z → ¬InStratum i s z

/-- The basin radius (∞-norm, in `(cx, cy, t)` coordinates): **3/2000 = 1.5e-3**.
A DEFINITION since A63 (was an opaque axiom, findings F5).  Derivation
(`docs/proofs/theta_t_transfer.md` X.3): A36 certifies the basin at radius 37/10000 in
`(c, θ, s)`; a t-deviation ≤ 3/2000 gives a θ-deviation ≤ 3/1000 ≤ 37/10000 (X.1,
`|Δθ| ≤ 2|Δt|`), and the corner-perturbation bound `r·(1+√2) < 37/10000` (X.2) closes the
`∀ s` slab so that every case of the `basin` axiom below lands inside A36's certified
34-dim box.  The A60 residual tree's landing radius 4.45e-4 sits at 0.30 × this value. -/
noncomputable def rBasin : ℝ := 3 / 2000

/-- **X.3(a), machine-checked (A68)**: the tilt-transfer gate `2·rBasin ≤ h_A36`.
With `theta_lipschitz` (`ThetaT.lean`), a `t`-deviation ≤ `rBasin` is a θ-deviation
≤ `2·rBasin ≤ 37/10000`, inside A36's box radius. -/
theorem rBasin_gate_tilt : 2 * rBasin ≤ 37 / 10000 := gate_tilt

/-- **X.3(b), machine-checked (A68)**: the slab gate `rBasin·(1+√2) < h_A36` (the binding
condition of `docs/proofs/theta_t_transfer.md` X.3).  With `corner_perturb`
(`ThetaT.lean`, sharp constant `r_c + √2·r_t`), every corner coordinate of a
configuration inside the `rBasin` box moves by `< 37/10000`, which closes the `∀ s` slab
of the `basin` axiom against A36's certified box. -/
theorem rBasin_gate_slab : rBasin * (1 + Real.sqrt 2) < 37 / 10000 := gate_slab

/-- `z` lies in the certified rigidity box around Trump's configuration. -/
def InBasin (z : Cfg) : Prop := ∀ i,
  |(z i).cx - (zhat i).cx| ≤ rBasin ∧ |(z i).cy - (zhat i).cy| ≤ rBasin ∧
    |(z i).t - (zhat i).t| ≤ rBasin

/-- **[trump5 residual — A59/A60]** Every packing in the Trump stratum at side
`s ∈ [3.82, ŝ]` is, after a container symmetry and a relabelling, a packing landing inside
the rigidity basin.  STATUS: A60 campaign running (zone cover + residue ladders +
confinement, every kill an exact certificate); the low-`s` slab (H7/G-A59-7) and the
s-parametric form of the (K) leaves are open — as stated the axiom quantifies over the
whole window, which is exactly that open obligation.  A63 sharpening
(`closed_disjoint_bridge.md` B.2/B.4): the tree's s₀ kill certificates, with the library's
ε-fat pin cores (margin ~1e-9), instantiate at NO side of the window via the dilation
bridge; the named upgrade paths are parametric re-emission or the slack-core fixed-side
grid (pricing HELD pending A60's δ-re-emission test — its measured law is η ≤ −1, stricter
than A56's slack gate).  The confinement leaves (nonempty `nofams`, the only route for the
outer triple) transfer via Lemma B-NO (B.2″) as occupancy with the zone contracted by 1/λ —
downstream consumers must hypothesise the outward-widened zone.  Dilation transfers KILLS only, never this axiom's containment conclusion (the
pulled-back basin box misses `InBasin` by ~(λ−1)·|ĉ| ≫ rBasin) — D.SLAB stands.  The
`InBasin` target is now concrete: all 33 coordinates within 3/2000, mod G (A60's landing
radius 4.45e-4 = 0.30 × rBasin).  The symmetry/relabelling is produced by the D4 reduction
inside the tree (H12; machine-checked at 3.84, re-proof at s₀ listed as mechanical). -/
axiom trump_residual : ∀ s ∈ wnd, ∀ z : Cfg, CfgPacking s z → InStratum trumpStratum s z →
    ∃ (z' : Cfg) (f : RP → RP) (e : Equiv.Perm (Fin 11)),
      IsCtrSym s f ∧ CfgPacking s z' ∧ InBasin z' ∧ ∀ j, (z (e j)).set = f '' (z' j).set

/-- **[A22/A36 — local rigidity at Trump]** Inside the basin box: every packing side is
≥ ŝ, and a packing at side exactly ŝ inside the box IS Trump's configuration.  STATUS:
certified by Python interval arithmetic (mpmath.iv Krawczyk + Farkas, standalone
re-checker, corruption gates); Lean replay blocked on interval trigonometry until the
certificate is re-emitted in `t` (A28 §4 / checklist F6).  The coordinate-box caveat is
RESOLVED (A63): with `rBasin = 3/2000` this axiom asserts exactly A36's certified theorem
after the θ↔t transfer, including the `∀ s` slab (`docs/proofs/theta_t_transfer.md` X.3;
the transfer constants are exact, the underlying intervals remain Python-certified). -/
axiom basin : ∀ z : Cfg, InBasin z →
    (∀ s : ℝ, CfgPacking s z → shat ≤ s) ∧ (CfgPacking shat z → z = zhat)

/-- **[uniqueness transfer]** EVERY packing at side ŝ has, after a container symmetry and
a relabelling, a representative that lies in some stratum.  STATUS RE-DIAGNOSED by A63
(`docs/proofs/unique_transfer.md`): AS STATED this axiom follows from census
exhaustiveness (A53 L3 — every packing has exactly one Young skeleton; take the D4
normalisation).  The F3 hole did not close, it MOVED: `s_eleven_unique` then feeds an
arbitrary packing to `stratum_kill`, whose ∀-packing strength at the K1-protected classes
is not what H10's machinery will prove (see the quantifier caveat on `stratum_kill`).
The full uniqueness architecture is now on file at drain-lemma rigor: selection CHAIN of
CC-2 teleports to a teleport-stuck packing (degenerate H1 cases resolved — teleports need
no corridor), stuck-packing kills (H10-stuck), residual+basin at the endpoint, and the
COLLAPSE back along the chain via Theorem U (one-square rigidity of ẑ), the single new
leaf, with an executable 11-certificate spec (re-insertion certificates at a rational
side in T1's isolating interval, budget 1, `nofams` zone inside the basin box).
Obligations ledger: U-O1..U-O4 in `unique_transfer.md` §5.  Kept as an axiom until the
prose is independently verified. -/
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
