# Eleven unit squares in a square: the mathematics of s(11) = ŝ

*Living document, edited in place; written 2026-09-09 from the repository's proof notes, ledgers and Lean
sources. Every claim carries a status tag: **[T]** proved in the notes (`docs/proofs/*.md`), **[L]** checked
in Lean 4 + Mathlib (`lean/PackingCertMathlib/`, theorem names given verbatim), **[C]** backed by an exact
certificate checked by a frozen verifier, **[P]** pending compute or pending formalisation, **[S]** supported
(numerically or by a sketch) but not proved, **[M]** measured. Where the record marks a statement FALSE, the
false statement and its true replacement are both given. Attempt identifiers `A###` refer to
`attempts/REGISTRY.md` and `LOG.md`.*

---

## 0. The theorem, its present status, and the certificate contract

### 0.1 Statement

Let s(n) be the side of the smallest square into which n closed unit squares can be placed with pairwise
disjoint interiors (rotations allowed). Let ŝ be the second real root of

    x⁸ − 20x⁷ + 178x⁶ − 842x⁵ + 1923x⁴ − 496x³ − 6754x² + 12420x − 6865,

the unique root in [3.877083, 3.877084]; ŝ = 3.877083590022814… (Trump 1979; the octic is Ellsworth 2023's).
Let ẑ be Trump's packing: six axis-parallel squares — the corner slot squares BL(0,0), BL(1,0), BL(0,1),
BR(0,0), TR(0,0) at their slots and one upright at (½, y₄) on the left wall — and five squares at one common
tilt θ_T = 40.181937…°.

**Theorem (target).** s(11) = ŝ, and every packing of eleven unit squares in [0, ŝ]² is, up to a symmetry of
the container and a relabelling of the squares, ẑ.

**Status.** The theorem is *stated* in Lean (`PackingCert.S11.s_eleven_eq`, `s_eleven_unique`,
`lean/PackingCertMathlib/PackingCertMathlib/TopLevel.lean`) and *proved there from exactly three named axioms*
(plus `propext`, `Classical.choice`, `Quot.sound` and the `native_decide` evaluation axiom for certificate
replays):

| axiom | content | what discharges it | status |
|---|---|---|---|
| `stratum_kill` | no packing at any side of the window [3.82, ŝ] has skeleton exactly of a non-Trump class | one `ClassKilledAt i m` obligation per class (§8): window certificates for 52 classes, the A57 trees for k5_11/k5_16, P-TREE trees for the 16 protected classes, the k0 route | [C] for 52 classes; [P] for the rest |
| `trump_residual` | every packing of Trump's class at any side of the window lands, mod D4 × S₁₁, in the rigidity basin | A60's residual zone-tree + the contraction tube (Lemma SEAM) | [P] |
| `a22_exact_structure` | three facts about ẑ read off A22's certified Krawczyk enclosure (tilt in [3/10, 2/5] in t; side in the octic's isolating interval; the 13 reduced contact rows vanish) | A22's certificate + A70's exact re-check; Lean replay of the witness lemmas | [C]; Lean [P] |

What is established unconditionally is recorded in §2: **3.82 ≤ s(11) ≤ 3.877084** with both ends Lean
theorems, Trump's packing is a packing at its own intrinsic side ŝ_A22 (a Lean theorem), ŝ_A22 = ŝ modulo the
third axiom, and ẑ is a strict local minimiser with a certified basin and a certified contraction tube.

The honest one-line status (2026-09-09, `writeup/01_summary.md`, `docs/residue_ledger.md` §0): every class but
k0_00 is either closed on the whole window or reduced to a priced tree campaign that has already run in part;
k0_00 is reduced to eleven converged-alive cells of hypothesis space, and **no k0 cell has yet been killed by
the cascade built for it** (§7.8).

### 0.2 What a reader must check, and with what

The proof is a composition of (i) prose lemmas, (ii) Lean theorems, and (iii) exact certificates. A reader who
accepts (i) and the Lean kernel need only (a) run the frozen verifiers on the certificate corpus and (b) replay
the Lean modules. Nothing that *finds* a certificate (LP solvers, annealers, tree builders, the agents) is in
the trusted base (`docs/specs/tcb.md`).

**Frozen verifiers** (Python 3, stdlib `fractions` on every accept path; floats only in shortlists and FAIL
witnesses — a float can cause a spurious FAIL, never a spurious PASS):

| verifier | sha256 (prefix) | certificate format | claim of a PASS |
|---|---|---|---|
| `attempts/A53-simple-strata/code/verify_case.py` (canonical; 16 byte-identical copies) | `521cb01f…` | `case-lp-certificate-v1` (`docs/specs/case_lp_certificate_v1.md`) | (P1) Σw < budget b and (P2) every closed unit square in [0,s]² meeting no core and not NO-exempt has μ-mass ≥ 1 |
| `attempts/A56-sparametric/code/verify_param.py` | `0c58485c…` | `parametric-kill-certificate-v1` (`docs/specs/parametric_kill_certificate_v1.md`) | (P1)+(P2) at **every** side s ∈ [s_lo, s_hi] for s-affine atoms and cores |
| `verify_param_v2.py` (A117; v1 never edited) | `153029ba…` | v1 + NO-families with s-affine zone edges | as v1, with exemption decided on the s-cell worst-case zone |
| `certs/verify_measure.py` | — | `measure-certificate-v1` | μ(Q) ≥ 1 for every closed unit square Q ⊆ [0,s]², Σw < n ⇒ s(n) ≥ s |
| `certs/verify_certificate.py` | — | packing certificate | n pairwise-disjoint closed unit squares in [0, side]² exist ⇒ s(n) ≤ side |
| `certs/verify_tube.py` | — | `contraction-tube-certificate-v1` | Theorem T1: every feasible point of the tube has side ≥ ŝ, equality only at ẑ |
| `certs/verify_sturm.py`, `certs/verify_cidl.py` | — | root isolation; ideal membership | the octic's two real roots; ŝ_A22 satisfies the octic |
| `attempts/A22-local-rigidity/recheck.py`, `attempts/A36-levels/code/a36_check.py` | — | Krawczyk / basin | superseded in the trusted base by the Lean replays `checkA22`, `checkA36` (A79) |

Non-frozen verifiers that decide *new* leaves have their own independent checkers and are cited where used
(pin-clip, polygon core `verify_case_v3.py`, lane covers, chord rows, the local certificate's
`check_local_t.py`); none of these has a Lean bridge except the polygon core's vertex test (§5.2) and the local
certificate (§6.3).

**Lean.** `lean/PackingCertMathlib/` (Lean 4.34.0-rc1 + Mathlib). The checkers of the case, parametric,
measure, tube, atlas, Krawczyk and basin certificates are Lean functions with machine-checked soundness
theorems (`checkCaseI_kill`, `checkParamI_kill`, `checkMeasureI_no_packing`, `tube_basin`,
`atlas_dilated_kill_fold`, `krawczyk_sound`, `a36_basin`), and a certificate is *replayed* by evaluating the
checker on the certificate's data with `native_decide` in an isolated module. Replayed so far (A78 T5, A79,
A86, A139): the 3.82 measure certificate, Theorem U's 11 certificates, P1, the K61 corpus (61 class kills at
s0), TRAP (6), the k5_06 parametric certificate over the whole window, A22/A36, 54 tube certificates, 49 atlas
boxes, and the two local certificates S07 (0.1, 40°) and S02 (0.2, 10°). The A57/A60 corpora (thousands of
certificates) are priced multi-day and **not yet replayed** [P].

**Composition glue the reader must accept as prose or Lean.** The bridge from "no family of pairwise-disjoint
*closed* squares" (what a PASS says) to "no packing" (interior-disjoint, contacts allowed) is Lemma B (§3.5,
Lean `lemma_B`); the bridge from monotone pin-set kills to exact-class emptiness is Lemma M→E (Lean
`class_kill`); the assembly of a zone-tree's leaves into a class kill is `ZoneTree.tree_kill` and
`Composition.classKilledAt_of_tree`. **One piece of glue has no standalone verifier and no Lean instance
yet**: the tree files themselves — that the emitted children of every node form a complete cover of the parent
(`ClosedTree.cover`), audited in-attempt by exact cover checks (A54/A57 `substrat`, `pinguard`) but not by an
end-to-end `verify_tree_s0.py` (`docs/specs/tcb.md`, TCB debt item 1) [P].

### 0.3 Conventions

Throughout, s0 := 969271/250000 = 3.877084 = ŝ + 4.0998·10⁻⁷ (the rational side at which every fixed-side
certificate is stated), and the **window** is W = [3.82, s0] (the Lean window `wnd` is [191/50, ŝ] ⊂ W). A
**kill** of a hypothesis is a certificate that no configuration satisfies it; **alive** means the LP value
τ reaches the budget so no certificate of that shape can exist (Lemma A57-3, `AliveBridge.lean`). Every kill
engine carries a **canary**: Trump's packing (and its D4 images, dilated to s0) must survive every leaf;
several lemmas below are stated with their canary because the canary is what fixed their form.

Figures are copied into `writeup/figures/`; the drawing conventions (hypothesis square at its box centre and
mid-tilt, extremal-tilt outlines, polygon cores solid, undecided region stippled, witnessed meeters drawn) are
those of `docs/shadows/a57v4/README.md`.

---

## 1. Definitions

### 1.1 Packings, sides, the parametrisation

A **closed unit square** is `sqSet p₀ e = {p₀ + a·e + b·e⊥ : (a, b) ∈ [0,1]²}` for a unit vector e
(`Bridge.lean`, `IsUnitSquare`). A **packing at side s** is a family Q₁, …, Q_n of closed unit squares
contained in the container [0, s]² with pairwise disjoint interiors (contacts allowed — every minimiser has
them). `Fits n s` says such a family exists; s(n) := inf{s : Fits n s} (`TopLevel.lean`, `sPack`).

**Lemma A.PARAM (parametrisation) [L] (`Parametrize.lean`, `parametrize`; prose
`docs/proofs/parametrization.md`).** Every closed unit square is `PSq.set (cx, cy, t)`: centre (cx, cy), edge
direction (cos θ, sin θ) with **t = tan(θ/2) ∈ [0, 1]**, where

    cos θ = (1 − t²)/(1 + t²),   sin θ = 2t/(1 + t²)    (`cosT`, `sinT`; cosT² + sinT² = 1 identically).

*Proof idea.* The square's own 90° symmetry (`sqSet_rot`) brings e into the closed first quadrant; then
t := e₂/(1 + e₁) is exact algebra. No trigonometry enters; t = 0 and t = 1 denote the same axis-parallel
square (findings F8), so the representation is a cover, not a bijection. ∎

Consequences used everywhere: w(t) := cosT t + sinT t ∈ [1, √2] is twice the axis-parallel half-width of a
square at tilt t (`wT_ge_one`; quasiconcave on [0,1]: `wT_ge_min`); Q ⊆ [0, s]² iff w/2 ≤ cx, cy ≤ s − w/2
(`set_subset_container_iff`); the interior of a parametrised square is exactly the open (u, v)-box
(`mem_interior_iff_uv`, `Attain.lean`), which is what makes interior-disjointness a closed condition on the
coordinates. A **configuration** z is the 33-vector (cxᵢ, cyᵢ, tᵢ), i < 11 (`Cfg`); `CfgPacking s z` is the
configuration-level packing predicate. The θ-frame (radians) is used by the rigidity certificates; the
transfer constants are exact: |Δt| ≤ |Δθ| ≤ 2|Δt| on [0,1] (`ThetaT.lean`, `theta_lipschitz`,
`sub_le_theta`) and a corner moves by at most r_c + √2·r_t (`corner_perturb`; the sharp constant is
load-bearing for the basin gate, `docs/proofs/theta_t_transfer.md` X.3).

The container symmetry group is D4 acting about (s/2, s/2) (`Census.lean`, `d4Apply`, `d4Sq`: rotations keep
t, reflections send t to (1 − t)/(1 + t)); `d4_packing` says the image of a packing is a packing at the same
side, `skeleton_d4` that the skeleton (below) is equivariant.

### 1.2 Slots, skeletons, classes

Fix s ∈ (3, 4). For a corner c of the container and cell offsets (i, j) ∈ {0,1,2}², the **slot** (c, i, j) is
the axis-parallel unit cell at offsets i, j along c's two walls; its centre is affine in the side,
**slotCentre = α + β·s** per coordinate with β ∈ {0, 1} and α ∈ {±½, ±3/2, ±5/2} (A56 P1; Lean
`slotCentre_affine`). A square **occupies** a slot when its set equals the slot cell exactly
(`OccupiesSlot`; axis-parallel, centre exactly at the slot centre — no tolerance). A slot is a **skeleton
cell** when its whole down-set {(i′, j′) : i′ ≤ i, j′ ≤ j} at that corner is occupied (`IsSkelCell`); the
**skeleton** of a packing is the set of its skeleton cells — a Young diagram at each corner
(`skeleton s z`, A53's Young-form definition, the PI's). Squares occupying skeleton cells are the packing's
**simple squares**; k := |skeleton|.

**Lemma (census) [L] (`Census.lean`, `CensusCheck.lean`).** At every side s ∈ (3, 4) the skeleton of a
packing is one of exactly **1110** four-tuples of Young diagrams (`skeleton_mem_census`), forming **163**
D4-orbits (`classCodes_length`); two independent enumerations (A53, A72 clean-room) agree exactly. The
**class** of a packing is the D4-orbit of its skeleton (`InStratum i s z`, exact membership). Classes are
named k{k}_{index}; the ones this document names:

| class | pins (BL frame, D4-representative) | role |
|---|---|---|
| trump5 | BL(0,0), BL(1,0), BL(0,1), BR(0,0), TR(0,0) — Trump's five slot squares | the class containing ẑ (k = 5; Trump's sixth upright at (½, y₄) is not on a slot) |
| k5_11 | BL(0,0), BL(0,1), BL(1,0), TL(0,0), BR(0,0) | A57 shadow tree |
| k5_16 | BL(0,0), BL(0,1), BR(0,0), TL(0,0), TR(0,0) = corners4 + BL(0,1) | A57 shadow tree |
| corners4 = k4_13 | the four corner slots | protected, no Trump image |
| k1_00 | BL(0,0) | the dependency K0-O1 of every k0 statement |
| k0_00 | ∅ | the empty class: no square is exactly a corner slot square |

**Monotone vs exact.** Certificates natively prove the **monotone** form "no packing whose skeleton
*contains* pin set S" (`ContainsPins S s z`: an injective assignment of squares occupying the slots of S);
the composition needs the **exact** form. **Lemma K1 [L] (`containsPins_mono`, `kill_mono`):** kills climb
containment (S ⊆ S′ and S killed implies S′ killed); dually aliveness descends (a strictly disjoint witness
family for S′ is one for S — `alivewitness`, `AliveBridge.lean`). **Lemma M→E [L] (`class_kill`,
`docs/proofs/instratum_bridge.md`):** a monotone kill of some S ⊆ g·T (g ∈ D4) at side s empties the exact
class of T at s. Because of K1, no single-square certificate can ever kill a class whose pin set is contained
in that of a class containing a packing — the 16 **protected** classes (the sub-skeletons of trump5:
k4_03, k4_05, k4_06, k4_08, k4_11, corners4, and the ten k ≤ 3 classes) are exactly those (A55 sharpness
[C] + K1 [L], `docs/known_results.md` item 15).

### 1.3 Corner boxes, K0-FREE / K0-BLOCKED / K0-WIDEN

For a corner c and a packing at side m, B_c(m) is the closed unit box at c; a square **meets** B_c when
int Q ∩ int B_c ≠ ∅ (A58's convention). In the **corner frame** (the D4 map sending c to the origin, container
in the positive quadrant) μ_c(Q) := min_{p ∈ Q} max(p_x, p_y) and the **intrusion depth**
d_c(Q) := max(0, 1 − μ_c(Q)); Q meets the open box iff d_c(Q) > 0 (`Crowd.lean`, `muC`,
`meets_cornerBox_iff_muC_le`). Two corner boxes are m − 2 > √2 apart, so a square meets at most one corner
box (CC-1(ii)).

* **K0-FREE**: some corner box is met by at most one square. **K0-BLOCKED**: every corner box is met by
  at least two distinct squares.
* **K0-WIDEN** (`docs/proofs/k0_route.md` §4.1): for a packing P at side m < s0 and λ := s0/m, the
  **dilate** F := Δ_λ P (centres scaled by λ about the origin, tilts and sizes unchanged) is a family of
  eleven pairwise *disjoint closed* unit squares in [0, s0]² (Lemma B.0, §3.5). If Q ∈ P meets B_c(m) then
  Δ_λ Q meets the **widened** box B_c^w(s0) = B_c(s0) grown by w into the container, with
  w = (λ − 1)(1 + 1/√2) ≤ w_max = (s0/3.82 − 1)(1 + 1/√2) = 0.025510 (Lean `scaleC_meets_cornerBox`);
  conversely a square of F meeting the unwidened B_c(s0) comes from a square of P meeting B_c(m). The k0
  trees are stated at s0 on F with the widened boxes; teleport leaves use the unwidened ones.

### 1.4 Cores, boxes, pieces

A **parameter box** B = [x₀, x₁] × [y₀, y₁] × [t₀, t₁] is a hypothesis "some square of the family has
(cx, cy, t) ∈ B". Its **axis core** K(a) is the axis-parallel square of half-side a about the box centre
certified to lie inside every pose of B (`caselp.Box.core`; for a pin box of tilt 0 and centre half-width h
the stock construction gives ½ − h√2 while the **exact** core is ½ − h, A135). Its **polygon core**
K′(B) := ⋂_{(c,θ) ∈ B} Q(c, θ) is the exact intersection of all poses — a convex polygon, certified
vertex-by-vertex (A132; Lean `PolyCoreT5.checkVertexInPBox_sound`): a rational point v lies in every pose of B
iff four polynomial inequalities in t hold on [t₀, t₁] at the four corners of the centre rectangle, decided by
Bernstein positivity. K(a) ⊆ K′(B) ⊆ every pose; a smaller box has a larger core.

A **NO-family** is the complementary hypothesis "no square has (cx, cy, t) in the zone F" (a centre rectangle ×
a list of closed t-intervals). A **node** of a tree carries pin cores, conditioned boxes B₁ … B_j (each with
its core), NO-families, and a **budget** b = n − #cores. A **piece** is a sub-box (tilt sub-bin × centre
rectangle); a **multi-box node** carries several named roles, each a union of pieces, and must satisfy the
invariant of §5.9 before any row, cover, figure or LP is derived from it.

### 1.5 Selections, rows, load paths

For two squares (owner o, other) and a signed **selection** σ = (owner, axis k ∈ {1, 2}, sign ε) the
**separating-axis row** is g_σ := ε (c_other − c_o)·a_k(θ_o) − ½ − w(θ_o − θ_other)/2 ≥ 0.
**Lemma SAT [L] (`CaseSat.sat_squares`; interior form `SatInterior.sat_selection_thm`, A126):** two unit
squares are interior-disjoint iff g_σ ≥ 0 for one of their eight signed selections. At fixed tilts every row
(walls, selections) is affine in the centres (Fact A, `docs/proofs/nocrit_k0_blocked.md` §1), so the packings
at fixed tilts with a fixed selection per pair form a polyhedron in (centres, s); the side minimum over it is
an LP whose dual is a balanced system of contact forces with unit load on the far walls — a **load path**
(Lemma GRAIN-LP, `docs/proofs/grain_flood.md` §1). A **grain** is the set of configurations sharing a
load-bearing contact structure; inside a grain the side is a closed-form function of the tilts.

---

## 2. The certified bounds 3.82 ≤ s(11) ≤ 3.877084, and the packing at ŝ

### 2.1 The lower bound: the guard-field measure certificate

**Theorem 1 (measure certificate) [L] (`Measure382.lean`, `s_eleven_ge_382`: ∀ s, Fits 11 s → 191/50 ≤ s).**
Let μ = Σᵢ wᵢ δ_{pᵢ} be a finite nonnegative atomic measure on [0, s]². If μ(Q) ≥ 1 for every closed unit
square Q ⊆ [0, s]² and μ([0, s]²) < n, then no n pairwise-disjoint closed unit squares fit in [0, s]²;
hence (by the dilation bridge below) no packing of n squares exists at any side m < s, i.e. s(n) ≥ s.

*Proof.* n pairwise-disjoint closed squares carry disjoint atom sets, so Σ μ(Qᵢ) ≤ μ(total) < n ≤ Σ μ(Qᵢ). The
bridge from interior-disjoint packings at m < s to disjoint closed families at s is Lemma B with r = 0 cores
(§3.5). ∎

The certificate `certs/measure_certificate_3.82.json` (A07/A08) is checked by `verify_measure.py` and by the
Lean checker `checkMeasureI` (integer interval arithmetic, rational grid trigonometry, clip via the
quasiconcavity of w, branch-and-bound to a fixed depth, coverage), whose soundness bridge is
`MeasureBridge.checkMeasureI_no_packing` [L] (A64) and whose driver model `checkMeasurePy_no_packing` [L]
(A75) covers the Python driver's root split, `--tscale` and margin for every float shortlist oracle. The pure
guard-field method tops out near 3.83 [M] (τ*(3.83) = 11.000; τ*(3.84) ≥ 11 exactly, A19), which is why the
rest of the proof is a case analysis. A structurally independent verifier (Burns–Massaccesi's net of
orientations, A129) re-checks the same certificate: PASS in 2 148 s against the frozen verifier's 587 s; it
is a cross-check, not a replacement [M]. The same machinery gives **s(12) ≥ 3.90** [C] (A33).

### 2.2 The upper bound and the exact packing

**Theorem 2 [L] (`Trump11.lean`, `eleven_unit_squares_in_3877084`, kernel `decide`, no `native_decide`).**
Eleven pairwise-disjoint closed unit squares fit in [0, 969271/250000]²; hence s(11) ≤ 3.877084.

The certificate is a rational rounding of ẑ (`certs/trump11_certificate.json`; the tight form at
s″ = 3877083591023/10¹² is `trump11_certificate_tight.json`, A65). This gives s(11) ≤ s0, not s(11) ≤ ŝ:
`checkPacking` needs strictly positive margins and ŝ is irrational, so **no finite set of fixed-side packing
certificates proves Fits(ŝ)** (`docs/proofs/attainment_ub.md` §2, route (b) refuted). Fits(ŝ) is obtained
instead from the rigidity certificate:

**Theorem 3 (Trump's contact solution) [L] (`Rigidity.lean`).** A22's curated 34-row contact system has
exactly one zero ẑ in the box ‖z − z0‖∞ ≤ 5·10⁻⁴ about the rational centre z0, with ‖ẑ − z0‖∞ ≤ 10⁻⁵⁰
(`Rigid.krawczyk_sound`, Banach on the true box); ẑ is a packing at its own side ŝ_A22 := ẑ₃₃
(`Rigid.zhatCfg_packing`, `TopLevel.trump_packs_at_shatA22`); and every feasible configuration in the box has
side ≥ ŝ_A22 with equality iff ẑ (`a22_optimal`, A22 §5's Farkas argument). The Lean replay
(`RigidityCheck.lean`, `checkA22`, 140 s) uses a dyadic 2⁻³³⁰ interval kernel with alternating-Taylor
cos/sin certified from Mathlib's series; the earlier `mpmath.iv` trust item is gone from the decision path.

**Theorem 4 (ŝ_A22 = ŝ) [L modulo `a22_exact_structure`] (`TopLevel.shatA22_eq_shat`).** Substituting ẑ's
exact structure (six uprights at their slots, five squares at one tilt t̂) into the 38 rows and clearing
(1 + t²)ᵏ leaves 13 generators G₀…G₁₂ ∈ ℚ[t, y₄, x₆…y₁₀, S], linear in the 12 non-t variables. Exact linear
elimination (A69) yields the saturated ideal-membership identity

    e(t)·Δ(t)⁸·octic(S) = Σⱼ qⱼ(t, S)·Gⱼ,   e, Δ root-free on t ∈ [3/10, 2/5]  (Sturm),

so octic(ŝ_A22) = 0, and root isolation (`shat_spec`: exactly one root in [3.877083, 3.877084], proved by the
IVT plus an all-positive Taylor shift, no calculus) gives ŝ_A22 = ŝ. Replayed in Lean over ℚ
(`CidlCheck.lean`, `CidlBridge.octic_zero_of_generators`; certificate `certs/cidl_identity.json`,
`verify_cidl.py`). By-product: the tan-half minimal polynomial 5t⁸ − 10t⁷ − 2t⁶ + 14t⁵ + 12t⁴ − 6t³ + 2t² + 2t
− 1 of t̂ is *derived*, and every coordinate of ẑ lies in ℚ(t̂), degree 8 (A03's "degree-7 coordinate"
annotations were spurious; `docs/known_results.md` item 4). The octic has exactly two real roots, the other
in (−2, −1) [C].

**Corollary.** Fits(ŝ) (`fits_shat`), so s(11) ≤ ŝ, and with Theorem 1 the certified state is
3.82 ≤ s(11) ≤ ŝ ≤ 3.877084.

**Lemma D1 (attainment) [L] (`Attain.attained_thm`; prose `docs/proofs/drain_lemma.md`).** {s : Fits 11 s}
has a least element: the coordinate feasible region (33 coordinates and the side) is closed and bounded and
the side projection is continuous; non-overlap is closed by `mem_interior_iff_uv`. No Hausdorff-limit
argument is needed. Hence s(11) is a minimum and the theorem's lower half reads "no packing at any side
m ∈ [3.82, ŝ)"; the uniqueness half reads "every packing at ŝ is an image of ẑ".

### 2.3 Rigidity and the basin

**Theorem 5 (basin) [L] (`TopLevel.basin`; `Rigid.a36_basin`, `basin_tframe`).** With rBasin := 3/2000
(t-coordinates), every configuration z with |z − ẑ|∞ ≤ rBasin in all 33 coordinates (`InBasin`) satisfies:
every side s with CfgPacking s z has s ≥ ŝ, and CfgPacking ŝ z implies z = ẑ. The Lean proof composes A36's
universal certificate `G3_UNIVERSAL` (σ ≥ ŝ on the 34-dimensional ∞-box of radius 3689/10⁶ in (c, θ, s),
second-order Taylor with the interval Hessian, max-form pinning, hand-over to `a22_optimal` at radius 1/2000)
with the two transfer gates `rBasin_gate_tilt` (2·rBasin ≤ 37/10000) and `rBasin_gate_slab`
(rBasin·(1 + √2) < 37/10000 — equivalent to √2 < 22/15; the naive per-component estimate 3r does *not* close,
`docs/proofs/theta_t_transfer.md` X.3½). "Close enough to Trump is Trump", stratum-blind.

**Theorem U (one-square rigidity) [C] + [L replay] (`docs/proofs/theorem_u.md`, A65; corpus A.THMU
replayed A78).** A packing at side ŝ consisting of ten squares of ẑ and one further unit square is ẑ. Proof:
eleven case-LP certificates at s″ = 3877083591023/10¹² with the ten dilated squares as cores of half-side
4999/10000, budget 1, Σw = 0, and one NO-family zone of half-width 10⁻³ around the missing square; Lemma B-NO
(§3.5) forces the eleventh square into the zone, whose pull-back lies inside the basin box, and Theorem 5's
equality clause finishes. The falsifier control (zone deleted) fails exactly at Trump's own pocket. The
multi-square ladder U_k (A80) is sound on exact strata but its reach collapses below 10⁻³ through the
hinge pocket of square 6 (half-widths 5.6δ, 5.8δ) [M]; it is not on the critical path.

**Theorem T1 (contraction tube) [L] (`RigidTube.tube_basin`, `TubeSeam.tube_tframe`; prose
`docs/proofs/contraction_tube.md`, A83).** For a centre-only direction v (v_θ = 0, v_s = 1) and radii
r = (r_c, r_θ), Tube_v(T, r) := {ẑ − t·v + w : 0 ≤ t ≤ T, |wᵢ| ≤ rᵢ}. If the checker `checkTube` passes
(pair-relative interval boxes for the edge/dist rows — the hull box is an interval-dependency artefact that
walls the tube at T ≈ 0.02 —, split Taylor remainder, monotone pinning iteration), every feasible point of
the tube has side ≥ ŝ with equality only at ẑ. Certified (`certs/tube_*.json`, 54 files replayed): on the
**slot ray** (trump5's pins riding their slot lines, free squares scaled) T = 0.045 at the A60 landing radii
(1.6·10⁻³, 2.1·10⁻³ rad) and T = 0.0571 ≥ ŝ − 3.82 (the whole window) at r = 6.5·10⁻⁴; on the pure **scale
ray** T = 0.1305 at the landing radii. The wall is the validity of one pin row (`E3c2-7e3`, a corner sliding
along an edge at 0.39 per unit depth) — a named geometric wall, not a numerical one. The compression lemma
(every loaded row is compressed along the ray, `docs/proofs/contraction_tube.md` §2) is why no L1-style axis
disjunction is needed.

**Lemma SEAM [T] (`contraction_tube.md` §4; Lean `TubeSeam.seam_inTube`).** A packing at side m = ŝ − t with
its pins exactly at slots(m) and its dilate's free squares within r_land of the λ₀-dilated ẑ-poses lies in
Tube_slot(t, (r_land + 3.6·10⁻⁷, r_land,θ, 0)); hence m ≥ ŝ with equality only at ẑ. This is how a (D) leaf
of a residual tree (all free squares localised near an image) discharges: δ_basin(trump5) = min(T_tube,
T_K(δ_pin)) = 0.0257 at pin slack δ_pin = 10⁻² and 0.0457 at δ_pin ≥ 1.8·10⁻² [M].

### 2.4 Other exact minima on Trump's skeleton (context for §6)

Four further local minima have exact endpoint certificates [C] (`docs/known_results.md` 26a, 26d;
`writeup/figures/s07_vs_trump.svg`, `s33_vs_s07_trump.svg`): **S07** at s* = 2 + 4√2/3 = 3.885618083…, every
coordinate in ℚ(√2), all five tilted squares at exactly 45°, class k6_07 = trump5 + BL(0,2), a separate basin
(barrier +0.032 on the straight segment; common-tilt crest +0.0011 at 41.60°); **S02**, the k7 pinwheel, at
3.886746029 (θ* = 48.43512°); **S33 = S34 = K19** at 3.916930865713920563… (smooth interior critical point,
no closed form found by PSLQ at 170 digits); **S35** at 3.917417657814610628…; **S38** (class k6_21) at
3.928914685222977527…, algebraic of degree 9. None lies in the window; they organise the alive population of
the trees (§4.6) and are the anchors of the local certificates (§6).
