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

---

## 3. The stratification by simple squares and the class-frame reduction

### 3.1 The idea (PI, A53) and why it makes the continuum finite

A packing is a point of a 33-dimensional continuum, and no finite case list exists a priori. The skeleton of
§1.2 is a finite combinatorial label attached to every packing at every side in (3, 4): which corner slots are
occupied by squares sitting *exactly* on the grid, closed under the Young down-set condition. This label
splits the continuum into 163 D4-classes (`Census.lean`), and kills climb the containment lattice (K1): once
a class is killed on the window, every class whose skeleton contains its pins is dead there too. A class is
killed by a certificate that *pins* its skeleton squares as cores (hypotheses) and prices the remaining
budget n − k squares. The class containing ẑ (trump5) cannot be killed by definition; its sub-skeleton
classes cannot be killed by any single-square certificate (K1 applied to Trump's images, A55 sharpness) —
these 16 protected classes need trees whose leaves land in the basin (§3.6). The empty class k0_00 has no
pins and is the unstratified problem; it is handled by the teleport/crowding route of §7.

### 3.2 Exhaustiveness and the top-level composition

**Lemma (stratify) [L] (`TopLevel.stratify`, `exists_stratum`).** If the minimum is attained at m ∈ wnd then
some minimiser lies in some class; as stated the selection content is empty — every packing has a skeleton.
The uniqueness clause likewise reads a packing at ŝ into its class (`unique_transfer`, a theorem since A78).

**Composition (`TopLevel.s_eleven_ge`, `s_eleven_eq`, `s_eleven_unique`) [L from the three axioms].** Take
the attained minimiser at m ≤ ŝ; if its class is trump5, `trump_residual` + `basin` give m ≥ ŝ; otherwise
`stratum_kill` contradicts. At ŝ every packing is in some class; non-Trump classes are excluded by
`stratum_kill`, and Trump's class lands in the basin, whose equality clause gives ẑ up to the symmetry and
relabelling.

**Per-class form (A86, `Composition.lean`).** Define `ClassKilledAt i m` := every packing of class i at side m
has m ≥ ŝ, and at m = ŝ is a D4-image of ẑ. Then `s_eleven_ge_of_classes` and `s_eleven_unique_of_classes`
prove both halves from `∀ i m, ClassKilledAt i m` alone, without `stratum_kill`, `trump_residual` or `basin`
[L]. The old axioms imply the new hypothesis (`classKilledAt_of_stratum_kill`,
`classKilledAt_trump_of_residual`). A further re-split `StratumKillAll`/`StratumKillMin` (`s_eleven_ge_of_split`,
`s_eleven_unique_of_split`) [L] admits classes killed only for σ-*minimisers* (needed if selected-form leaves
such as K0-ROT are used; today MinForm = ∅).

### 3.3 The certificate kills, by tier (status 2026-09-09)

| tier | classes | result | status |
|---|---|---|---|
| k ≥ 7 | 1110 − (k ≤ 6) tuples | every k ≥ 7 tuple contains a killed k = 6 sub-tuple (A53 L5, combinatorial) | [L] via K1 once the k = 6 kills are on the window |
| k = 6 | 33 | all 33 killed (A53/A54) | [C] window: all full-window (A56/A61/A114) |
| k = 5 | 22 | 19 killed by single certificates; k5_11, k5_16 killed at s0 by A57's sub-stratification trees; trump5 = Trump's class | [C] for 19 (window); k5_11/k5_16 window trees running [P]; trump5 §3.6 |
| k = 4 | 14 | 8 killed; the sweep is exactly sharp: a k = 4 class is certifiably empty iff it is not a sub-skeleton of trump5 | [C]; 6 protected |
| k ≤ 3 | 11 | k3_00 killed; the other ten protected | [C] one; ten protected |
| window coverage | 52 scoreboard rows (the classes needing a window certificate) | **52/52 full-window** (A146 closed the last row, k5_13, 2026-09-07) | [C] |

The K61 corpus (61 s0 certificates) is replayed in Lean (A78 T5); the parametric certificate of k5_06 is
replayed over the whole window (`ParamK506.k5_06_param_kill`, 215 s); `WindowRows.k5_06_slab` instantiates
`SlabKill` for it [L]. The other 51 window rows are [C] with Lean replay priced but not run [P].

### 3.4 Window transfer: why s0-only certificates prove nothing on the window

A certificate is stated at one rational side. The composition needs every side m ∈ [3.82, ŝ]. Three facts
govern the transfer:

**Lemma B.0 [L] (`Dilation.lean`).** For a packing P at side m and λ > 1, Δ_λ P is a family of closed unit
squares pairwise disjoint *as closed sets* with separating-axis gap ≥ λ − 1 (`scaleC_disjoint`, proved by
A64's pull-back trick without any separation theorem), contained in [0, λm]² (`scaleC_subset`), and a pin at
slot α + βm dilates to distance exactly (λ − 1)|α| from the side-λm slot (`slot_tracking`).

**Lemma B (the bridge) [L] (`lemma_B`, `dilation_bridge`, `priced_dichotomy`, `hcert_of_priced`).** Let C be
a case-LP PASS at side s″ with cores K₁ … K_r and empty NO-families, budget b = 11 − r, Σw < b, and let P be
a packing at side m < s″ with r distinct squares whose dilates contain the cores. Then P does not exist.
*Proof.* The ≥ b non-owner dilates are admissible, meet no core (closed disjointness from the owners), are
not exempt, so each has μ-mass ≥ 1; the masses add over disjoint closed sets: μ(total) ≥ b > Σw. ∎ At
λ = 1 the lemma fails (touching squares can share an atom): this is the S4 trap, and it is why every kill in
the composition is applied at a certified side strictly above the packing's side.

**Corollary B′ (slot form) [L] (`bprime_containment`).** With the containment margin
ρ(C) := ½ − a(cos θ_c + sin θ_c) of a core against an axis-parallel pin and A = max |α| ≤ 5/2, the kill of
pin set S at s″ applies to every packing containing S at side m with (s″/m − 1)·A < ρ(C).

**The corpus number [M].** The library's ε-fat cores (a = 16383999967232/32768001953125) have
ρ ≈ 1.0000009·10⁻⁹ > 0 exactly, so an s0-only certificate reaches only sides within relative distance
4·10⁻¹⁰ below s0 — and (s0 − ŝ)/ŝ ≈ 1.06·10⁻⁷, so **an s0-only certificate with ε-fat cores instantiates
`stratum_kill` at no side of [3.82, ŝ] at all** (`docs/proofs/closed_disjoint_bridge.md` B.2). The window
quantifier is carried by (i) the parametric certificates (`checkParamI_kill` [L]: (P1)+(P2) at every real
side of [s_lo, s_hi] for s-affine atoms and cores; the s-axis is bisected together with the pose box), or
(ii) the **slack-core grid**: a certificate with cores of half-side ½ − δ covers a slab of relative width
δ/A below its side (A57's window grid uses four sides at δ = 10⁻²), or (iii) the tube for the top slab.

**Lemma B-NO [L] (`priced_dichotomy` with a nonempty `Exempt`).** With NO-families the bridged claim is
occupancy: some non-owner square of P has its dilated (centre, t) in some zone F_k, i.e. (c, t) ∈ λ⁻¹F_k.
Consumers must hypothesise the outward-widened zone F_k^{+ε}, ε = (λ_max − 1)·max coordinate — a real
widening (≈ 1.6·10⁻³) under the slack-core grid (B.2″).

**Cover invariance (A57's trees) [T] (`docs/proofs/cover_invariance.md`).** The interior zone
Z(s) = [11/10, s − 11/10]² with 12 × 12 columns × 8 t-intervals is a complete cover at every s ∈ W (CI-1,
Lean `grid_cover`); the frozen (a, tm) cores stay valid for every s ≤ s0 (CI-2, monotone in the box width);
no pin centre ever enters Z(s) (CI-3, `slot_outside_zone`); but the T5 logic kills are relative-position
facts that can flip across the window and must be re-checked per box (CI-4, obligation). The affine family is
exactly `verify_param`'s (α, β) form with β dyadic/12 for boxes and β ∈ {0,1} for pins.

**The slab-width law [M] (`docs/budget.md` §E).** A parametric slab passes iff
log₂(width/w_min) + d_pose ≤ 48; one probe slab prices a class; every earlier bulk FAIL of A56 was an
over-width slab, never node hardness; near a shadow at side s* the cost per unit side rises as
(s* − s) → (s* − s0) and diverges only if the class contains an actual minimum.

### 3.5 Zone trees and their leaves (the shape every campaign shares)

A **zone tree** at s0 for a class S is a finite rooted tree whose root hypothesis is `ContainsPins S`
(slack pin cores of half-side ½ − δ_pin) and whose branching at a node is a complete disjunction over a
closed cover {Bᵢ} of a zone Z × [0°, 90°]: the NO child (no square centred in Z; budget unchanged) and the
YES_i children (some square with (c, θ) ∈ Bᵢ; budget − 1), with the **pinguard** rules: a box containing a
pin's (slot ± δ_pin) × {0°, 90°} is "parent" (never budget-decremented); a box whose core meets a pin core or
another conditioned core without a shared witness is contradictory (T5, Lean `core_meet_same_square`);
refinement by a closed sub-cover keeps the budget (T11, `refine_cover`); zone-assignment collapse N1
(`centre_separation`, `zone_assign_bijective`: footprints of diameter < 1 hold at most one centre, so the
labelled and unlabelled hypotheses coincide). Leaves:

* **(K)** a case-LP PASS at s0 for the node — no family (Lemma B);
* **(C)** contradictory or vacuous by logic;
* **(D)** all free squares localised within the landing radii of a D4-image of ẑ — the tube (Lemma SEAM);
* **(D′)** all eleven squares inside an atlas value box with certified σ ≥ V ≥ s0 (Lemma K0-ATLAS,
  `atlas_dilated_kill_fold` [L]: no dilation bookkeeping since the dilate has strict wall margins);
* **(T)** a teleport leaf (§7.2): a corner box or a usable slot met by ≤ 1 square.

**Lemma P-TREE [T] (`docs/proofs/protected_trees.md` §2; Lean `ZoneTree.tree_kill`,
`Composition.classKilledAt_of_tree`).** For a protected class S with pin set P_S, a closed tree at s0 over
the *monotone* hypothesis whose leaves are (K)/(C)/(D), together with a tube certificate in each class
direction v_I (I = the Trump-frame indices of the image's pinned squares) at radius ≥ the landings, proves:
(a) no packing at any side m ∈ [ŝ − δ_basin(S), ŝ) contains S's pins; (b) every packing at ŝ containing
S's pins is a D4-image of ẑ; with δ_basin(S) = min(T_I, T_K(δ_pin)), T_K(δ) = ((δ/A_S)ŝ − (s0 − ŝ))/(1 +
δ/A_S). The exact-stratum hypothesis is used nowhere on the lower bound and only optionally at m = ŝ
(Simp(g·ẑ) = trump5 ≠ S). **Lemma PD [L] (`pd_convex`, `pd_rule`)**: with slack pins the residue ladder
stalls at δ_pin; the logic kills must use the drifted *full* pin square, tested at the two endpoints λ = 1
and λ_max (convexity of K − Σ_p). Below the tube's reach the class needs plain slab kills (`SlabKill`,
`classKilledAt_of_slabs` [L]).

### 3.6 The protected tier and the trump5 residual

Fourteen of the 16 protected classes have a compatible Trump image (G_S ≠ ∅) and are P-TREE campaigns;
**the tube law [M]**: T_max depends on the pin set only through square 3 = BL(0,1) — 0.0457 (landing radii)
/ 0.0574 (r = 6.5·10⁻⁴) when it is pinned, 0.1305 / 0.1680 when it is free — so the whole window is
covered by the tube alone for the corner-only classes and needs one more ladder level (r ≤ 6.5·10⁻⁴) for the
BL(0,1)-pinned ones. Pilot laws (A84 k4_08/k3_05, A100 k4_11/k3_02): the (D) geometry is class-independent
per image (landing level 24, residue 53–118 boxes, the same numbers as A60's square-1 ladder); the η law is
exact — η < 0 ⟺ a certificate exists, 54/54 cover nodes; price 3 500–4 200 CPU-h for the 15 classes
excluding k0_00 [P]. **k4_05 and corners4 have no Trump image**: their trees have no (D) leaves and must
close by (K)/(C) alone; corners4 emptiness is provably invisible to every single-square scheme (exact
7-point centre witnesses at every window side, `docs/proofs/corners4_empty.md`; the obstruction is
orientation coupling) and remains open [P]; the pair-certificate route was walled (Lemma W‴: complete
verification trees of 10⁹–10¹¹ nodes, A77).

**trump5** (Trump's own class) is the A60 residual tree: zone cover at s0 (kill rate 0.781 first pass),
residue ladders contracting at ratio ≈ 4.5 per level to level 24 (landings 1.4472·10⁻³ centre, 2.0102·10⁻³
rad), confinement of the outer squares by NO-families, (D) leaves into the tube. Status: paused; 218 alive
nodes re-solved with exact cores by A149 killed 87 (40.7 %), 131 alive; regime 1 (plain slack-core slabs below
ŝ − δ_basin) needs two certificates if they certify [P].

---

## 4. The case-measure LP leaf and its certificate

### 4.1 The certificate and its claim

A `case-lp-certificate-v1` (`docs/specs/case_lp_certificate_v1.md`) declares a side s, a count n (11), an
atomic measure μ = Σ wᵢ δ_{pᵢ} (D4-expanded), core squares K₁ … K_r (half-side a_j > 0, centre, tilt
tm_j), NO-families F₁ … F_m, and a budget b. A PASS establishes, as one theorem [L for the checker
`checkCaseI`, `CaseBridge.checkCaseI_kill`]:

> (P1) Σ wᵢ < b; (P2) every closed unit square Q ⊆ [0, s]² meeting no core (closed intersection) and not
> NO-exempt has μ(Q) ≥ 1.

The decision procedure is a branch-and-bound over boxes [t₀, t₁] × [x₀, x₁] × [y₀, y₁] with four discharge
rules — VACUOUS (no admissible placement: the container clip via the quasiconcavity of w), EXEMPT-core
(every pose of the box meets one core, by separating-axis overlap on all four edge normals with interval
enclosures — sufficiency is `sat_squares` [L]), EXEMPT-nofam (the box lies in a zone), COVERED (atoms
provably inside every pose of the box carry mass ≥ 1 + margin) — all in integer arithmetic on a common
grid; an undischarged box at the depth cap is a FAIL witness. Errata: the loader rejects a ≤ 0 ("bad core"),
contrary to the spec's original wording (A70). The parametric form (`verify_param.py`, V.PARAM [L]) replaces
each point by its s-interval and the container by its most permissive end.

### 4.2 The LP behind the certificate, and what "alive" means

The certificate is the dual of a covering LP: maximise the total weight of a fractional packing (placements
with density ≤ 1 at every atom) subject to the hypotheses; τ := its value; a certificate exists iff τ < b
with a margin the certifier can close (η := τ − b < 0). **Lemma A57-3 (alive gate) [L]
(`AliveChecker.lean`, `AliveBridge.lean`).** If a strictly disjoint family of ≥ b admissible squares
avoiding every core exists (an `alivewitness`), then τ ≥ b and no certificate of that budget passes
`checkCaseI`. Trump's dilated images are such witnesses for every node they reach: this is the **canary** —
an engine that certifies a node an image realises is wrong (engine assertion, exit 9). Measured laws [M]:
on A60/A100 cover nodes η < 0 ⟺ a certificate exists (54/54); on the k4 tier η ≤ −1 is geometrically
impossible at every side (exact 6-families, A82); certification at fractional η depends on the "eps_geo"
repair and the witness-feedback depth, an engineering constant (A85's f₂).

### 4.3 Budget, exemptions, and why exact cores are certifiable today

The budget is n − r: every core must be *owned* by a distinct square of the family (pinguard: distinct
witnesses, `Zones.lean` T5/T11). A core is a lower approximation of the hypothesis square; the larger the
certified core, the more placements are exempt and the cheaper the LP. **A135's finding [M, load-bearing]:**
both frozen verifiers take the core half-side a *verbatim* from the certificate and never recompute it from
the box (they check only 0 ≤ tm ≤ 1 and a > 0), so any half-side that is *sound* — certified inside every
pose of the box by an argument outside the verifier — is certifiable under the frozen chain with no verifier
change. For a pin box (tilt 0, half-width h = δ/√2, δ = 10⁻²) the exact core is ½ − h = 0.492928… against
the stock ½ − δ = 0.49: ×1.012 in area; for a tilted conditioned box the exact axis core is A135's `exact_a`
(corners certified per piece). **Measured effect [M]:** re-solving the alive A57 population with exact pin
cores kills 28.6 % (46/161, A137); on trump5 40.7 % (87/214, A149); FAIL-with-holes records convert at
62.5 % because their LP was already below budget and only the certificate's exemption annulus was short
(A149). **A170's audit [M]:** an emission bug (`caselp.make_certificate` reverting exact cores to stock)
touched only three attempts' lanes (A150/A165/A166); 698/698 certificates of the main lanes carry exact cores;
59 certificates recovered, 118 already-exact FAILs unchanged, so the rates above stand.

The **polygon core** K′(B) (§1.4) is strictly larger than any axis core (median area ratio 1.225, up to 1.53
at level 1); it excludes 22.3 % of the dual-support columns carrying 35.7 % of τ over 506 alive nodes [M,
A132]. Using it *inside* the certificate needs a new exemption clause (`verify_case_v3.py`'s `polycores`,
A135: rational polygon–square SAT in the exemption test; identical to the frozen verifier on 24/24
polycore-free certificates; independent sampled controls 0 unsound exemptions) [C, non-frozen] and one Lean
lemma, `PolyCoreT5.checkVertexInPBox_sound` [L] (the exemption soundness statement `PolycoreExemptSound` is
stated, not yet proved [P]). Its logic-level use needs no certificate at all (§5.2).

### 4.4 Rows the LP does not know, and the exact-zero law

The LP's dual support is a fractional object; its alive nodes are alive for reasons the LP cannot express
(§4.6). Two attempts to feed structural facts into the LP as rows both failed for measured reasons:
**SLOT-CROWD rows** (§7.3) re-price rather than forbid, because one placement can meet two or three slot
boxes at once and the incidence budget pays for it (A109: 0 of 18 alive nodes at any licensed depth);
**corner-incidence rows** (R6, A115/A154) go the wrong way — the widened corner boxes cover 28 % of the
container where a covering measure is cheapest, so c = dτ/de ≥ B in 23/23 runs. The **existential-filter
law** (A89–A101, `docs/proofs/exchange_lemma.md` §7): any leaf whose hypothesis is "no other square reaches
region R" is silent at the frontier, where the unlocalised free squares' shadows cover everything, and
free only at depth. Its complement, the **enumeration–certificate mismatch law** (A30–A52): counts quotient
placement away, certificates price placements; every count-based route to k0 (FJ census 10³⁶ structures,
frame census 10²⁸–10⁵⁹) lost on the count, not on the per-structure price.

### 4.5 Tree composition in Lean

`ZoneTree.ClosedTree s0 tc Root` is the abstract object: nodes carry `NodeHypC` (cores + NO-zones on the
dilated family), leaves are (K) `checkCaseI … = true`, (C), (D) the SEAM landing, (D′) `checkAtlas … = true`
with L ≥ s0, and `cover` is the complete-disjunction obligation the producer must supply; `tree_kill` is
Lemma P-TREE (a)+(b) [L]. The rule library (`zone_dichotomy`, `grid_cover`, `slot_outside_zone`,
`pd_convex`, `pd_rule`, `d4_dil_comm`) supplies the covers used by every campaign. What is missing [P]: the
tree-file → `cover` emitter, and the `ClosedTree` instances for trump5 / the protected classes / k0_00,
which await the campaigns' leaf corpora (`lean/lean_wave7_A86.md` §4).

### 4.6 What the alive nodes are: shadows

An alive node's dual support, drawn as squares at their centres and tilts with opacity by weight, is a
picture a person can read (the PI's rule, A107: draw the relaxation, not a packing). Over A57/A60's alive
population 53 shadow values explain 1 566 nodes (`docs/shadows/S01.svg` … ; `writeup/figures/shadow_S01.svg`,
`shadow_S02.svg`, `shadow_S07.svg`): **S01 "room at side 4.000"** (a slot left empty or singly met — dead by
teleport, which the LP does not know; ≈ 45 % of alive nodes), **S02 the k7 pinwheel** (seven slot squares +
three load-bearing squares at 48.435° + one strut; s* = 3.886746 = s0 + 0.0097, so the relaxed core cannot see
the slack; carries the deep tree), **S07** (the exact 45° packing above), S03–S53 small families, and a
fractional tail with no integral support. The k0 spectrum reproduces this (K01 = room, K06 = the pinwheel).
No open box contains a shadow (A106: 64 of 145 open level-2–4 boxes are empty by box-vs-pin geometry; the
shadow floor of both A57 classes is the pinwheel at +0.0097) — the boxes are alive because the relaxation,
not the geometry, has room. This is the reading that produced the geometric leaves of §5 and the local
certificates of §6.

---

## 5. Geometric leaves: kills that need no LP

Each leaf is stated for a node of a zone tree (any class, any n): pins P with certified cores, a conditioned
square H with parameter box B_H, the container [0, s0]², the family F of eleven closed pairwise-disjoint unit
squares (the dilate of §1.3 when the window is meant). Every leaf below has an exact rational certificate
and an independent checker; the Lean column says what is formalised. The order in which they are applied
matters and is a lemma of its own (§5.9): geometry to a fixed point first, LP only afterwards.

### 5.1 Pin-clip and the tilt trim (A131, A96)

**Lemma CLIP [T]+[C].** Let K be a certified core of another square (a pin's exact core, or the axis core of
another conditioned square). For a tilt sub-bin [t₀, t₁] of B_H, the set of centres c at which Q(c, θ) meets
int K *for every* θ in the sub-bin is convex and is decided exactly: each of the four separating-axis
conditions is a single sinusoid in θ (rational in t), whose extremum over the sub-bin is at an endpoint or
at one interior critical point (`P² + Q² < ¼`). Removing those centres from B_H is sound: a centre in the
dead set carries no square distinct from K's owner. The clip is four bisected slabs per obstacle, searched
in floats and certified in `Fraction`s, no epsilon. *Canary and controls [M]:* 674/674 existing logic kills
clip to EMPTY; 1.14·10⁶ sampled poses, 0 hits; the predicate matches a direct SAT grid on 40 000 cases.
**Yield [M]:** of A57's 607 unclosed nodes 132 clipped to EMPTY (112 of them by the deployed tilt trim
T5″, the box-wise octagon test that CLIP strictly dominates), 292 narrowed; on ten alive nodes the clipped
LP moved five from η ≈ 0 to η ≤ −0.5. **Caveat [T]:** the LP's `eps_geo` row-shrink must never be chained
after a clip — it re-imposes exactly the shell the clip removed. Lean: the T5 rule
`core_meet_same_square` [L]; the clip's sinusoid decision is [C] (A131 `pinclip.dead_q`, independent
checker 132/132).

### 5.2 The polygon core and the pair leaf (A132, A135, A141)

**Lemma K′ [T]+[L].** K′(B) := ⋂_{poses ∈ B} Q(pose) is convex; a rational point v lies in K′(B) iff for each
of the four corners (x, y) of the centre rectangle the polynomial conditions |proj_k(v − (x, y))| ≤ ½
hold for all t ∈ [t₀, t₁] on both edge axes (`PolyCoreT5.checkVertexInPBox_sound` [L]; decided by Bernstein
positivity after clearing 1 + t²). The certified polygon is the convex hull of certified vertices, built
by clipping on a θ-grid, shrinking by 10⁻⁶ and simplifying inward only.

**Leaf PAIR (shared point) [L] (`PolyCoreT5.shared_point_same_square`).** If two boxes B₁, B₂ have a common
rational point v ∈ K′(B₁) ∩ K′(B₂) then any two squares with poses in B₁ and B₂ share an interior point, so
they are the same square; a node hypothesising two *distinct* squares there is dead. This is the T5
contradictory rule with the polygon in place of the axis core (T5⁗): 64 logic kills on 506 alive nodes, 37
new [M]; on k0 it killed `s3_far` (A141: h0 and h1 share a certified point once h0's box is clipped to the
container) [C].

**Leaf OVL (always-overlap) [T] (A118 §1.2).** If every pose pair (p₁ ∈ B₁, p₂ ∈ B₂) overlaps then the
two boxes cannot hold distinct squares. (Octagon pair inequality: strictly stronger than Lemma TC below,
firing at centre distance < 1 rather than ≈ 0.7.)

### 5.3 Tilt coherence (PI, Lemma TC) and centre separation

**Lemma TC [T (support-function identity, verified to machine epsilon); leaf [C]] (`docs/known_results.md`
26c; `ParamNoFam.lean` `TCLeaf`).** Two interior-disjoint unit squares with centre distance c and tilt
difference D (mod 90°) satisfy (1 + cos D + sin D)/2 ≤ c; so centres within 1.05 force |D| ≤ 6.06°, within
1.10 force |D| ≤ 13.05°, within 1.207 force |D| ≤ 44°, with equality for edge-to-edge flush at D = 0. As a
leaf between two boxes (bins) it is frozen as a Lean `Prop` whose separating-axis step is [C] (A117: 170/170
stored fires reproduced, 1.7·10⁶ sampled pairs, 0 counterexamples). n-general and elementary. Measured: as a
kill test 4.8× weaker than the octagon interval test because it discards direction; it is the O(1)
pre-screen and the reason the pinwheel's three tilted squares share a tilt.

**Lemma CN (centre separation) [L] (`Zones.centre_separation`; A42 N1.0).** Distinct squares of a packing
have Euclidean centre distance ≥ 1 (each contains the open disc of radius ½ about its centre). Corollary:
a footprint of diameter < 1 holds at most one centre (`zone_assign_bijective`). **Leaf CN (cover number)
[T, zero kills M] (A153):** if the certified outer feasible-centre region of a node is covered by k pieces of
diameter < 1 then at most k more squares fit, so k < budget kills with no LP. Measured over 322 nodes: cover
number − budget has median +4, minimum 0, and on 322/322 the region already holds ≥ budget points pairwise
≥ 1 apart — a floor no refinement removes. Kept as a gallery assertion; priced at zero as a lever.

### 5.4 The teleport leaf, lanes and slot lanes (A58, A118, A141)

**Lemma CC-2 (teleport) [L] (`Selection.teleport_packing`).** If the open interior of a slot cell C ⊆ [0, m]²
meets the interior of at most one square Q of a packing at side m, replacing Q by the exact cell square C
gives a packing at side m (no corridor, no motion). Applied to a corner slot this is Lemma K0-FREE (§7.2).
Applied to a **usable slot** of a pinned class S — a completable, unclipped slot whose extension class
S ∪ {p} is certified dead on a window containing m — it gives:

**Lemma SLOT-CROWD [T, ∀-packings] (`docs/proofs/slot_crowds.md` §2).** In every packing at side m ∈ [3.82,
s0) containing S's pins, every usable slot is met (open interiors) by ≥ 2 non-pin squares. For k5_11 the
usable slots are BL(1,1), BR(0,1), TL(1,0) (extensions k6_18, k6_20, k6_20, full window) and TR(0,0) (k6_23);
for k5_16 BR(0,1), TR(0,1), TR(1,0) and BL(1,0); trump5's six unclipped completable slots are all doubly met
by Trump's own free squares (exact 60-digit canary: second depths 0.016 … 0.305).

**Leaf LANE [T]+[C] (A118 axis cores; A141 polygon cores).** LANE(C) := an upper bound on the number of
pairwise interior-disjoint unit squares that can meet int C while lying in the container and interior-disjoint
from every core (pins and K′(H)); M(C) := 1 if some pose of H meets int C, else 0 (decided exactly by
A161's `box_misses_cell_exact`, the full separating-axis test over B_H with the square's own normals — A141's
cell-normal test was incomplete). If LANE(C) + M(C) ≤ 1 the slot is singly met and the node is dead by
SLOT-CROWD. LANE is certified by a complete prefix-code cover of the meeter pose space with three discharge
rules (container, misses-cell, shared rational point) and a pair test on the open set; a realised disjoint
pair is a sound LANE ≥ 2 certificate that retires the cell forever (Lemma A159-1). **Yield [M]:** 188 A57
nodes + 56 trump5 nodes (A141; 294 certificates, independent checker); 47 k0 cells (A141). **Caveat (A118-O1,
A152) [T]:** the k6 extension classes are certified with *exact* pins (tolerance 3·10⁻⁸), so a slot-lane
kill is sound for the class-S composition with exact pins, and for A57's δ = 10⁻² slack-pin family only after
the twelve extension certificates are re-solved with a = ½ − h and re-verified over the window (1–15 / 2–30
CPU-h, four classes at τ = 4.60–4.72 at risk) [P]. **The shrunk-cell refinement is FALSE [F]** (A152): "every
other square misses the cell shrunk by δ ⟹ some translate of the cell is free" fails — four grazers entering
through the four faces block every translate; the sound fixed-translate form is vacuous at completable slots.
**The undecided cells are real two-crowds [M]** (A157: 86 of 179 realise a free pose at 4·10⁵ draws; the
covers close 0 of 93); a hairline grazer with clearance 10⁻² is invisible on a page — "met" is interior
intersection at any depth.

### 5.5 Chord rows, guard lines, and the chord-limited lane (A144, A161, A167)

**Lemma LINE [T] (A144 `chord_sum_le_side`).** For any line ℓ inside the container the chords int Q ∩ ℓ of
a packing's squares are disjoint open segments, so their lengths sum to ≤ s. For a parameter box B the
minimum chord `minchord(B, ℓ)` over all poses is five exact rational evaluations (the chord depends on the
tilt only through y = cos + sin; one factor is monotone, the other attains its interval minimum at an
endpoint). Splitting off the hypothesis squares turns the PI's reading "a line crossing four squares through
opposing sides forces side ≥ 4" into an LP column priced at rhs(ℓ) = s0 − Σ_pins minchord − minchord(H)
instead of s0. As an LP row it is narrow (active on 2 of 20 re-solves) and needs a v4 certificate clause
(`guardlines`, spec written, Lean shape two theorems + one checker, not built) [P]; offline it flags 86 of
448 survivors [M] (`writeup/figures/k5_11_interior_Y0147_guardline.svg`).

**Lemma CL (chord-limited lane) [T]+[C] (A161).** For a usable slot on a wall carrying two pins, the guard
line inside the slot's wall row caps at β := ⌊s0 − Σⱼ minchord(Bⱼ, ℓ)⌋ the number of free squares crossing
the line through opposite sides (chord ≥ 1, the band); A141's lane cover with an exact band prune
(max|v| ≤ (y + 1 − y²)/2) bounds the outside meeters by LANE_out; SLOT-CROWD's ≥ 2 is contradicted by
β + LANE_out + M ≤ 1. 98 certificates, all passing an independent checker; 27 genuinely new dead nodes
after de-duplication against the status collector (A161's own "90 new" was a population-snapshot error).
k5_11 contributes zero because its wall-adjacent usable slots sit on a wall with one pin chord (β = 2).
**Conditional form [T]+[C] (A167):** splitting B_H into pieces b with their own guard line, chord row
(minchord is monotone under box inclusion) and fattened core: n(b) = β(b) + LANE_out(b) if every pose of b
misses the cell, else min(β, LANE_band) + LANE_out + 1; n(b) ≤ 1 on every piece kills. 15 kills (11 new)
over 416 cells; 285 cells are no-go by an exact rational two-crowd witness (49 certified), which retires them
for every lane-type leaf.

### 5.6 The impossible-weight gate (A145)

Not a lemma: the share of a node's dual-support weight sitting on placements the hypothesis forbids (columns
meeting K′(H) or a pin's exact core) is a threshold *predictor* of an exact-core re-solve kill [M] (4 of 5
above 0.60 killed; monotone on ALIVE records 100/50/28/7 % by band; nearly flat on FAIL records). It orders
the exact-core chore; the kills it predicts are ordinary (K) leaves under the frozen verifier.

### 5.7 Wastage: Lemma ID and Leaf WASTE (A89, A164)

**Lemma ID [T] (`docs/proofs/tilt_floor_k0.md` §7).** If no square reaches depth ≥ δ at corner c then the
box [0, 1 − δ]² at c is wasted, so c_sh shallow corners strand c_sh(1 − δ)² of the wastage budget
E(m) := m² − 11 ≤ B₀ := s0² − 11 = 4.031780343056. Area alone never kills four shallow corners
(4 < 4.0318); **certified [C] (A89-O3):** no packing at any side of the window has all four corners
SHALLOW(0.3) — some square reaches within 0.7 of a corner point; three shallow corners is open.
**Leaf WASTE [T] (A164):** with U := the container points no admissible square can contain (admissible = in
the container, interior-disjoint from every certified core), |U| ≤ m² − 11; |U| > B₀ is an LP-free kill; the
window is covered by inflating the cover square only. **Measured: zero kills on all 71 alive gallery nodes
[M]** — |U|/B₀ median 18.6 %, maximum 47 %; the corner column is *empty* on every node, so Lemma ID's charged
region is empty on the alive population; 64–100 % of the certified waste sits in wall strips. "Only one
centre fits near the right wall" is false unconditionally (seven 1-separated centres fit in x ≥ s0 − ½).

### 5.8 Snap, exchange and flood (A98, A101) — leaves that are sound and silent

**Lemma SNAP-D [T].** A square Q of a packing can be replaced by the exact cell square C at the same side iff
no other square meets int C (= `teleport_packing`). **Lemma MULTI [T]:** a set of squares moves onto a set T
of pairwise interior-disjoint cells iff no *untouched* square meets any int C ∈ T — the movers may crowd each
other's targets, which is why one-at-a-time greedy stalls while the joint move certifies. **Lemma SHELL
[T]:** a crowder of an η-disturbed square's cell (tilt θ) is a grazer of SAT depth ≤ √2·ε,
ε = η + ½ − 1/(2(cos θ + sin θ)) ≤ η + θ/2 — the tangency law made a theorem. **Lemma FLOOD-D [T]:** a Young
diagram D at a corner with N(D) := #{squares meeting int D} ≤ |D| yields a packing at the same side with an
exact corner slot square, hence k ≥ 1; the excess X(D) = N(D) − |D| equals overhang minus free area
(Lemma X); at side < 4 every square meets the 3 × 3 corner block (Lemma CAP), so a win needs |D| ≤ 8.
**Lemma EXPOSE [T]:** a re-fit Q₀ after removing a two-intruder corner's pair is valid iff no untouched
square has an interior point in int Q₀ ∖ (A ∪ B). **Theorem EXCHANGE (every K0-BLOCKED packing on
[3.82, ŝ) converts to k ≥ 1 at the same side) is OPEN [C]**; its exact stall is INTERLOCK / CELL-INTERLOCK
(realised at two corners of the 3.9855 record and at Trump's TL, never at four corners). As node leaves these
are silent at the frontier (existential-filter law) — SNAP-T fired on 0 of A57's witness holes.

### 5.9 The multi-box invariant (A171, A172, A175) — the order of operations, as code

**Lemma INV [T].** In a node with several conditioned roles, (i) every piece is first clipped to the
container (the sound w_min rule; the strict w_max clip narrows the hypothesis and is a diagnostic only);
(ii) every piece of every role is clipped against every *other* role's core with Lemma CLIP, and the cores
are rebuilt after each pass, to a fixed point; (iii) **K′(role) is the exact rational intersection of the
per-piece polygon cores**, every vertex re-certified against every piece — a hull of the surviving pieces
forgets clips that remove different slabs in different tilt sub-bins and loses a quarter of the certified
core (A172: on one node kept fractions H 0.44 → 0.36, D 0.088 → 0.072); (iv) the invariant K-CONTAINER,
K-DISJOINT (exact polygon SAT), POSE-CONTAINER, CLIP-FIXPOINT is asserted before any row, cover, figure or LP;
a failing K-DISJOINT is the PAIR kill, not an error; an emptied role is the kill `EmptyBox`. **The obstacle
must be the polygon core, not the inscribed axis square** (A175's defect finding: with axis-core obstacles a
recorded node kept H 1.00/D 1.00/S 1.00/B 0.60 and was alive; with polygon obstacles H is emptied and the
node is dead). This is the rule two agents in a row broke and the PI caught by eye; it is now
`attempts/A171-multibox-invariant/code/multibox.py`, and `chord_rows`/`lane` refuse an un-normalised node.

---

## 6. Local certificates around the exact minima (S07, S02, S33, S38)

### 6.1 Theorem LOCAL (A116; `docs/proofs/local_certificate.md`) — n-general

Fix a known minimum z* with load-bearing squares L and the class pins P (slack h), a side window
W ∋ s0, radii (r, ρ) and an optional tilt cut. The **local hypothesis N**: s ∈ W; for each pin some square
is axis-aligned with centre in the slot's h-box; for each ℓ ∈ L some *other* square has pose in
F_ℓ = [c_ℓ ± r]² × ([θ_ℓ ± ρ] ∩ cut); all distinct. Dead(N, s0): no packing of n squares at side ≤ s0
satisfies N.

**Reduction DROP [T].** The |P| + |L| witnesses of N form a packing of |P| + |L| squares satisfying N, so
Dead_{L∪P}(N, s0) ⇒ Dead(N, s0): the other squares never appear (and §6.4 says what that costs).

**Lemma COVER [T] (Lean `cover_pair`, `SatInterior.cover_pair'`).** Over a tilt cell K, a pair is FAR if some
selection's interval enclosure is ⊆ [0, ∞), NEAR otherwise; a selection is POSSIBLE on K if its enclosure
reaches ≥ 0. Every packing of L ∪ P with tilts in K lies in the polyhedron P_λ(θ) of some **leaf** λ (one
possible selection per near pair) — a finite case split of ≤ 8^k cases by Lemma SAT.

**Lemma LEAF [T].** At fixed tilts, v_λ(θ) := min{s : (s, c, u) ∈ P_λ(θ)} is an LP whose dual y ≥ 0 gives
s ≥ Σ y_k d_k(θ) for every point of the leaf polyhedron; the support of y is a wall-to-wall load path and its
value is a chain formula in the tilts (Lemma GRAIN-LP).

**Theorem LOCAL [T].** Dead_{L∪P}(N, s0) ⟺ for every cell K of a finite cover of N's tilt box and every
possible leaf λ on K, inf_{θ ∈ K} v_λ(θ) > s0. (⇒ is the converse: an LP minimiser at side ≤ s0 is itself a
packing of L ∪ P satisfying N.)

**Lemma RELAX [T]+[L] (`LocalCertT2.relax_wall`, `relax_selection`).** Over a tilt cell each selection row
is replaced by affine rows in (s, c, u, t) implied by the true row: p cos φ + q sin φ ≤ p + |q| sin hw +
max(0, −p_lo)(1 − cos hw), the McCormick planes for q·φ, and affine lower bounds for the support width
w = |cos Δ| + |sin Δ| (in t the two smooth branches cos Δ ± sin Δ bound w below on the whole cell, so the
π/2 kink never appears: A133). The loss is second order in the cell width plus one McCormick term that
halves under a q-range split. A111's earlier leaf stopped at r < s* − s0 because it dropped ambiguous pairs
and lost first order per row; with every near pair case-split the certified minimum sits within 10 % of s*.

**Lemma STAB [T]+[M].** A contact's selection is forced on a box until its riding vertex reaches the end of
its edge (tangential slack ½ − |τ|) or the relative tilt crosses 90°; a flush contact costs one binary
split. The PI's stability-radius reading (the minimum's own contacts) matches the rigorous radii to ±0.02;
the single-leaf neighbourhood is ≈ 0.02 and stops at the short-slack contact (S07: f0's vertex 0.057 below
BL(0,1)'s corner — the Trump boundary; S02: f1's corner 0.085 over f3's), which the tree case-splits.

### 6.2 The certified neighbourhoods and the Trump boundary

| minimum, frame | L | largest certified (r, ρ) | cut | status |
|---|---|---|---|---|
| S02, k5_11 (pins BL(0,0) BL(0,1) BL(1,0) TL(0,0) BR(0,0)) | f1, f2, f3, BR(0,1) | (0.2, 10°), (0.05, 20°) | none | [C] A119 rational; [L] `localDead_s02_t` (0.2, 10°) |
| S07, trump5 | f0, f2, f4 | (0.1, 40°), (0.2, 10°) | F_T(θ) > s0, i.e. θ > θ_T + 6.1·10⁻⁵° (grid uses 41.565°) | [C]; [L] `localDead_s07_t` (0.1, 40°) |
| S33, k6_07 (six pins) | all five free squares | (0.2, 10°), (0.05, 20°) | none (Trump outside on position alone) | [C] A125 |
| S38, k6_21 | five free squares | (0.1, 10°) | none | [C] A125 |

**The dip, exactly [T] (`local_certificate.md` §4).** For S07 the pair f0–BL(0,1) has two selections once
δ > 0.024: the face (f0's vertex on x = 1) and the corner (BL(0,1)'s corner (1, 2) on f0's lower-left edge).
The corner leaf's support is the **gap chain** with value F_T(θ) = 2 + (2 + sin θ)/(cos θ + sin θ), increasing
on θ > 24.3°, equal to s0 at θ₀ = 40.181998° = θ_T + 6.1·10⁻⁵°: so N must be cut by θ > θ₀ — Trump's own
tilt, not the grain boundary 41.565° (where F_T = Λ = S02's value 3.886746 and the *formula* changes). Below
θ₀ the dip is real and unavoidable: Trump is a packing at ŝ < s0 satisfying trump5's pins, so no N containing
Trump's tilt can be dead — the cut is the canary (uncut runs at (0.05, 5°) and beyond go ALIVE with witnesses
at side F_T(40°) = 3.875871). For S02 the mirror dip D(θ) = F_T(90° − θ) < s0 at θ > 49.818° is an artefact of
the restriction to L ∪ P (Trump's three tilted squares under the diagonal reflection satisfy k5_11's pins with
nine squares) and does not materialise in the k5_11 frame because the pins BL(1,0), TL(0,0) leave no room.

**The radius limit [M].** At r = 0.3 both shadows admit a genuine rearrangement of the |L| + |P| squares
below s0 that the *dropped* squares would forbid (S02: BR(0,1) slides 0.3 left with f3 on top, 3.873; S07:
the ladder shears, 3.856); adding the blockers as boxes lifts the value but does not extend the radius
(A119 T3). **Correction to A116 [F]:** three of its four ρ ≥ 20° "capped" cells are ALIVE (checked packings
of L ∪ P below s0 inside N); the certified radii are unaffected. At S33 nothing is dropped, and the ρ = 20°,
r ≥ 0.1 cells are OPEN at the cap with no witness — the limiter is the tilt-cell count (five tilt dimensions
bisected to ≈ 1°), not geometry.

**Corollary TRUMP-GAP [T/M, 40 digits] (`docs/proofs/grain_flood.md` §2.4).** ŝ = 2 + (2 + sin θ_T)/(cos
θ_T + sin θ_T) at Trump's tilt: Trump, S07 and S02 are three kink minima of one menu of chain formulas in the
common tilt θ, with u = cos θ + sin θ — the ladder Λ(θ) = 2 + 4u/(u² + 1) (minimum 2 + 4√2/3 at 45°, = 4 at 0°
and 90°: the grid), the column chain Y, the diagonal chain D(θ) = 2 + (2 + cos θ)/u, and the gap chain
F_T = D(90° − θ). S07 = Λ meets Y at 45°; S02 = Λ meets D at sin θ cos θ = 2 sin θ − 1 (θ* = 48.43512°);
S07's boundary into Trump's grain is at sin θ cos θ = 2 cos θ − 1 (41.56488°), crest exactly S02's value.
**Theorem CONT [T]:** the fixed-tilt value function s_min(θ) is continuous in θ for every n (a finite union
of polyhedra with Slater points, Berge); **Lemma INHERIT [T]:** the formula survives every unloaded contact
change; only a change of the loaded basis can produce a kink, and only a crossing of two local branches can
turn s_min down. **GRAIN-FLOOD as a box kill is true and empty [T]** ("every local minimum ≤ s0 lies in
Trump's grain" is the class kill itself, `grain_flood.md` §4); the sound consumer is a conflict row on the
support's cells (GRAIN-ROW), which kills a support pattern, not a node.

### 6.3 The Lean closure: LocalDead from certificate data alone

`Local.lean` defines `LocalHyp Ls Ps s z` (boxes, pins) and `LocalDead Ls Ps s0`. The chain
`localDead_of_cert` (A126, a reflected weak-duality leaf checker `LocalCert.checkLeaf_sound` proved once
and run on every dead leaf by `native_decide`) needed one named hypothesis, `CertCover` — that the recorded
leaves cover the hypothesis. A133 re-emitted every certificate in **t = tan(θ/2)** (cos, sin rational: no
π, no Taylor series, no interval kernel anywhere; the certificates got *sharper*, S02 32 570 → 16 406
leaves). A134 proved the cover's three pieces (`selectionOk_sound`, `relax_wall`/`relax_selection`,
`localHyp_bodies`) with a decidable Bernstein positivity certificate `posCheck` on the certificate; A138
wrote the reflected plumbing (`treeOk_sound`, `wallOf_sound`, `selCtx_sound`, `rowImplies_sound` — the
600-line quantisation estimate collapses to one lemma because the emitted row is compared with the built
row through `minL`), ending in `certCover_of_check : certOk C = true → CertCover …` and
`localDead_of_certOk`. A139 closed the data: **`localDead_s07_t : LocalDead s07Boxes s07Pins 3.877084` and
`localDead_s02_t` are theorems [L]** with Ls, Ps read off the certificate's own `CMeta`, rosters
`[propext, Classical.choice, Quot.sound]` + the replays' `native_decide` axioms + `check_3_82`'s; build
571 s / 6 707 s. One catch [F→fixed]: Lean's support-width enclosure `wLoQ` is coarser than the
generator's exact w-range, so 246/246 of S07's selection closures were not reproducible until the
certificates were re-emitted with the Lean-side exclusion (+37 % leaves for S07); the permanent fix — the
exact w-range as a decidable enclosure in `LocalCertT2` — is [P]. The S33/S38 certificates are [C] under
A119's independent rational checker (six certificates, 602 421 dead leaves, 10.7·10⁶ multipliers) and not
yet in Lean [P].

### 6.4 YES/NO composition, F-COVER, basins as unions

**Lemma YES/NO [L] (`LocalCompose.node_dead_of_yes_no`, `classKilledAt_of_yes_no`).** For a tree node with
hypothesis H and a local neighbourhood N = (Ls, Ps): the YES child "a square in each box of Ls" is dead by
`LocalDead`; the NO children "no square in box Bᵢ" are ordinary case-LP nodes with NO-families; the
disjunction is a tautology (`yes_or_no`), so the node is dead when all NO certificates PASS. **F-COVER
[F→fixed, A136]:** the NO zones were written rounded *outward* (tilt to 2⁻²⁰, centre to 9 decimals), so
ZONE ⊆ BOX failed by ~10⁻⁷ and the tautology failed at file level; the fix rounds the zone inward and
checks `zone_sub_box` on the written rationals (one trap: a bound that is an exact geometric fact, ½ or
s0 − ½, must be written exactly). A120's 22 NO certificates re-certify 22/22; Y0230's four NO certificates
replay in Lean (`y0230_dead` [L]); the in-N board is 15 closed / 24 touched of 35 targets [C]. `Local.Box`
cannot carry a tilt cell leaving [0°, 90°] (the inside part is kept; sound, marked).

**Basins are unions, per frame [C] (A151, A160, A163).** Growing S02's neighbourhood coordinate by
coordinate: f1 certifies at 10× A116's cell volume (0 real packings found inside any grown N), but the
growth directions trade off — a **live-low witness** (nine squares at side 3.8693 < s0) refutes f2's
upward slice together with the grown f1 — so the certified basin is a *disjunction* of differently shaped
boxes (53 box sets + A151-B, 114 of 184 in-N nodes). f0 is an exact rattler with a one-parameter slide of
length 0.298419 at fixed tilt; f3 is the most load-bearing square. A basin is a statement about a
hypothesis in a class frame: transported to k5_16 (52/54 certified) and trump5 (42/54; 9 refusals are real
witnesses because trump5 does not pin TL(0,0)), all 94 objects re-emitted through A133's generator and
checked. **Consumer of the S33 basin [M]:** one node — the sixth pin BL(0,2), which k6_07 has and trump5
lacks, blocks 1 065 of 1 421 alive supports.

### 6.5 Coupled moves at the k0 residue (A128, A130) — box lemmas, not node kills

**Lemma BOX-MOVE [T] (`docs/proofs/drain_sel.md` §2.0).** A rigid screw of a cluster C ∋ Q, certified on a
pose box B by interval rows (every possibly-active pair axis of a member against an outsider has positive
derivative, every wall row likewise, Q's depth candidates decrease, no other depth increases), shows that B
contains no Ψ^(w)-minimiser at which Q intrudes its corner, for every positive weight vector w; its dual is
Lemma BOX-GORDAN (Motzkin form with interval coefficients). **Lemma EXCHANGE-BOX [T]:** Lemma EXPOSE on a
box, ∀-packings. **Measured [M]:** on the twelve converged-alive k0 near-packings, K01–K06, the two locked
boundary packings and Trump (canary held on every box), 35 exact certificates each re-sampled 10⁴ → 0 hits:
the cluster screw certifies nothing a single square does not; the exchange is the only coupled move that
works where every single-square move fails (nine corners); below 4 every hold is a flush re-fit with margin
≈ 0. The non-rigid field (A130, Lemma BOX-FIELD-W) certifies the 4.001525 lock at all eight intruders; the
three window holds are mode accumulations at the flush stratum (Lemma MODE), not locks, and are k ≥ 1
packings above ŝ, so they cost DRAIN-SEL(W) nothing. None of this is composed into a node kill.
