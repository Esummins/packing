# A34 T1 — the lifted packing POP, correctness, sparsity, symmetry, size estimates

Fable (theory lead), 2026-08-26. Status: T1 deliverable. Conventions: docs/results.md; idea I-L14.

## 1. The POP

Fix n. Variables (the "circle form" — see §1.1 for why not t = tan(θ/2)):

- per square i = 1..n:  z_i = (x_i, y_i, γ_i, σ_i)   (centre, cos θ_i, sin θ_i)
- per unordered pair i < j:  u_ij ∈ R²  (separating direction)
- s (container side) — present in the min-s form; a constant in the fixed-s feasibility form.

Constraints (ALL of degree ≤ 2):

  (C1) circle:        γ_i² + σ_i² = 1,  γ_i ≥ 0, σ_i ≥ 0            [n equalities]
  (C2) containment:   x_i − (γ_i+σ_i)/2 ≥ 0,  s − x_i − (γ_i+σ_i)/2 ≥ 0, same in y   [4n rows, linear]
  (C3) separation:    u_ij · (p_a(z_i) − q_b(z_j)) ≥ 0  for all 16 corner pairs (a,b)  [16 rows/pair, bilinear]
  (C4) normalization: ‖u_ij‖² = 1                                    [1 equality/pair]
  (C5) box bounds:    x_i, y_i ∈ [1/2, s−1/2]; γ_i, σ_i ∈ [0,1]; u components ∈ [−1,1]; s ∈ [√n, 4] (min-s form, n=11)

where the corners are LINEAR in z_i:
  p_{σ1σ2}(z_i) = (x_i, y_i) + (σ1/2)(γ_i, σ_i) + (σ2/2)(−σ_i, γ_i),  σ1, σ2 ∈ {±1}.

Redundant valid cuts (degree ≤ 2; provable on the lifted set, NOT derivable by low-level SOS —
these are the load-bearing strengtheners, cf. A15's θ′ vs LP):

  (R1) u_ij · (c_i − c_j) ≥ 1        (proof in §2.3)
  (R2) ‖c_i − c_j‖² ≥ 1              (inscribed-disk argument, or R1 + Cauchy–Schwarz)
  (R3) 1 ≤ γ_i + σ_i ≤ √2           (from C1; use rational √2 upper enclosure 1.4142136)

Objective: min s (min-s form), or fixed s ∈ {3.83, 3.84, 3.85} feasibility (T3 decision form).

### 1.1 Why the circle form and not t = tan(θ/2)

The brief's t-form clears (1+t²) denominators: containment rows become degree 3, separation rows
degree 4 (with a shared β lift var) or degree 6 (β-free), forcing Lasserre level ≥ 2–3 just for
representability and inflating the monomial basis. The circle form is degree ≤ 2 throughout: level 1
(Shor) is already well-defined and level 2 is the first "real" level. Nothing is lost for exact
certificates: rational points are dense on {γ²+σ²=1} via γ = (1−t²)/(1+t²), σ = 2t/(1+t²), and any
SOS certificate in (γ,σ) is a polynomial identity that can be checked in Q[z,u]/(ideal) exactly;
at extraction time substitute the t-parametrisation if a denominator-free rational witness is wanted
(A28's Lean-side preference for t is unaffected: the CERTIFICATE is rational either way).

The β variant (8 rows/pair: u·p_a ≥ β, β ≥ u·q_b; 3 lift vars) is equivalent; the 16-row β-free
form was chosen because it keeps pair cliques at 10 vars and all rows homogeneous in structure.
Row count enters the SDP only through 11×11 (order-1) localizing blocks — cheap either way.

## 2. Correctness: projection of the lift = exactly the packings

Let F ⊂ R^{4n + 2·C(n,2)} (+1 for s) be the set defined by (C1)–(C5), and π the projection onto
(z, s). Let P_s = { z : the n closed unit squares Q(c_i, θ_i) lie in [0,s]² with pairwise disjoint
interiors }, where (γ_i, σ_i) = (cos θ_i, sin θ_i), θ_i ∈ [0, π/2].

**Claim: π(F) = { (z, s) : z ∈ P_s, bounds (C5) }, and min_F s = s(n) for n = 11.**

(a) *(C1)+(C5) ⇔ angles.* γ, σ ≥ 0 with γ²+σ²=1 iff (γ,σ) = (cos θ, sin θ) for a unique
θ ∈ [0, π/2]. Orientations of a square have period π/2, so this parametrises all placements, with a
benign double cover only at θ ∈ {0, π/2} (harmless: sets, not counts). No spurious points.

(b) *(C2) ⇔ containment.* For θ ∈ [0,π/2] the corner x-offsets are (σ1γ − σ2σ)/2 with maximum
absolute value (γ+σ)/2 (both γ,σ ≥ 0), same in y; so all four corners lie in [0,s]² iff (C2). ∎

(c) *(C3)+(C4) ⇒ disjoint interiors.* Suppose the 16 rows hold with ‖u‖ = 1. Since Q_i = conv{p_a},
min_{x∈Q_i} u·x = min_a u·p_a ≥ max_b u·q_b = max_{x∈Q_j} u·x =: β. So Q_i ⊂ {u·x ≥ β},
Q_j ⊂ {u·x ≤ β}. If p ∈ int(Q_i) had u·p = β then p − εu ∈ Q_i with u·(p−εu) < β, contradiction;
hence int(Q_i) ⊂ {u·x > β} and symmetrically int(Q_j) ⊂ {u·x < β}: interiors disjoint. ∎

(d) *Every packing admits the lift.* Let Q_i, Q_j be closed unit squares with disjoint interiors.
First, int(Q_i) ∩ Q_j = ∅: if q ∈ Q_j ∩ int(Q_i), pick q' ∈ int(Q_j); then (q, q'] ⊂ int(Q_j), and
points of the segment near q lie in the open set int(Q_i) — so int(Q_i) ∩ int(Q_j) ≠ ∅,
contradiction. Now separate the disjoint nonempty convex sets int(Q_i) and Q_j (separating
hyperplane theorem, no closedness needed): ∃ u ≠ 0, β with u·p ≥ β on int(Q_i) and u·q ≤ β on Q_j;
by continuity u·p ≥ β on Q_i = cl(int Q_i). Rescale ‖u‖ = 1. Then u·(p_a − q_b) ≥ 0 for all corner
pairs, (C3)+(C4) hold. Touching pairs are covered (weak inequalities). ∎

(e) *min attained and = s(n) (n = 11).* F is closed (polynomial (in)equalities) and bounded by
(C5), hence compact; s is continuous, min attained. By (a)–(d), values of s with a lift = values of
s with a packing, s ∈ [√11, 4]. Since s(11) ≤ 3.877084 < 4 (certified, A03) and s(11) ≥ √11 (area),
the artificial cap s ≤ 4 does not bind: min_F s = s(11). ∎ (Same argument for n = 2, 3, 5 with the
cap 4 replaced by any certified upper bound, e.g. 2.001, 2.001, 2.708.)

### 2.3 Validity of the cuts

(R1): from the 16 rows, u·c_i − u·c_j ≥ (|u·e_i| + |u·e_i⊥|)/2 + (|u·e_j| + |u·e_j⊥|)/2 where
e_i = (γ_i, σ_i) (because min_a u·p_a = u·c_i − (|u·e_i|+|u·e_i⊥|)/2 and symmetrically for j).
For any unit u and unit e: |u·e| + |u·e⊥| ≥ √((u·e)² + (u·e⊥)²) = ‖u‖ = 1. Hence
u·(c_i − c_j) ≥ ½ + ½ = 1. ∎
(R2): each unit square contains the closed disk of radius ½ about its centre; disjoint interiors of
the squares force disjoint interiors of the disks, so ‖c_i − c_j‖ ≥ 1. ∎
These are valid on F but their derivation uses |·| case analysis / Cauchy–Schwarz, exactly the kind
of reasoning low Lasserre levels emulate only with the cut present in the basis. They are the
continuum analogue of the d ≥ 1 fact A31 used, localised to the pair clique.

## 3. Correlative sparsity

Constraint-variable incidence: (C1),(R3) touch {γ_i,σ_i}; (C2) touch {x_i or y_i, γ_i, σ_i, s};
(C3),(C4),(R1),(R2) touch V_ij := z_i ∪ z_j ∪ {u_ij} (10 vars) (+s never).

Two decompositions:

**Tier A (pair cliques only, NOT RIP).** Cliques K_ij = V_ij ∪ {s}, 55 of them (11 vars; 10 in the
fixed-s form). Covers every constraint and the objective. The running-intersection property FAILS
(K_12, K_13, then K_23 ∩ (K_12 ∪ K_13) = z_2 ∪ z_3 ∪ {s} sits in no single earlier clique) —
because the square-interaction graph is K_n. Consequence: the sparse relaxation is still a VALID
lower bound at every level (the Dirac measure at any lifted packing point restricts to consistent
clique moments satisfying every block constraint), but the Lasserre convergence theorem does not
apply — the level-∞ limit of Tier A may sit strictly below s(n). Tier A is the continuum analogue
of A15's θ′ (pairwise-consistent SDP), which beat the LP by ~0.6 on the discretised graph; that is
the reason to hope Tier A level 2 > 3.83.

**Tier B (RIP-valid, convergent).** Add the configuration clique K_0 = {all z_i} ∪ {s}
(4n+1 = 45 vars at n = 11). Clique tree = star with centre K_0, leaves K_ij; each
K_ij ∩ K_0 = z_i ∪ z_j ∪ {s}: RIP holds. All separation content stays on the leaves; K_0 carries
only (C1), (C2), (R2), (R3) and box bounds. Sparse-Lasserre convergence (Lasserre/Waki–Kim–Kojima
+ Grimm–Netzer–Schweighofer; the quadratic-module on each clique is Archimedean by the explicit
box bounds) ⇒ Tier B level r → s(n).

## 4. Symmetry

G = D4 × S_n. Centre coordinates at the container centre (fixed-s form) to make D4 linear:
r90: c ↦ Rc, (γ,σ) fixed (orientation mod π/2 invariant), u_ij ↦ R u_ij; reflection:
c ↦ (x, −y), (γ,σ) ↦ (σ,γ), u ↦ (u1, −u2). S_n permutes square blocks and maps u_ij ↦ −u_ji when
the order flips. The POP is G-invariant, so moments may be averaged over G:

- S_n collapses the 55 pair cliques to ONE orbit: one 66×66 (fixed-s) / 78×78 moment block type
  plus consistency rows, ~55× reduction — the flag-algebra-style 2-point reduction.
- D4 block-diagonalises within cliques (A16's projectors reusable), ~4–8× on the big clique.

TSSOS does not do group averaging natively; SumOfSquares.jl + SymbolicWedderburn does. Pilot plan:
run CS(+TS) unsymmetrised first (sizes below are already small at Tier A); reach for symmetry only
if Tier B's K_0 block is the wall.

## 5. Size estimates (level r moment blocks; C(k+r, r) = monomials of deg ≤ r in k vars)

Fixed-s feasibility form at n = 11 (min-s adds +1 var to every clique):

| object | vars | level-1 blk | level-2 blk | count | level-2 total PSD vars |
|---|---|---|---|---|---|
| dense (no CS) | 154 | 155 | 12 090 | 1 | ~7·10⁷ — DEAD |
| Tier A pair clique | 10 | 11 | 66 | 55 | 55·C(14,4)≈55 k moments; 66×66×55 blocks — EASY |
| Tier A localizers (deg-2 rows) | — | scalar | 11×11 | ~19/pair ≈ 1045 | small |
| Tier B K_0 (n=11) | 44 | 45 | 1 035 | 1 | ~C(48,4) ≈ 1.9·10⁵ moments; one 1035×1035 block — HEAVY but plausibly Mosek-feasible (≈8–30 GB, hours); with D4×S_n averaging ≈ 130–260 per isotypic — comfortable |
| Tier B K_0 (n=5) | 20 | 21 | 231 | 1 | trivial |
| Tier B K_0 (n=3) | 12 | 13 | 91 | 1 | trivial |

Term sparsity (TSSOS TS on top of CS): the constraint support graph within a pair clique is dense
(corners mix all of z_i), so TS should trim constants, not orders; measure, don't assume.

Level 3 Tier A: C(13,3) = 286 per pair block ×55 — feasible if level 2 is inconclusive but close.

## 6. Validation protocol (T2) — what the numbers must show

Targets s(2) = 2, s(3) = 2, s(5) = 2 + 1/√2 = 2.7071067811…, min-s form.
Per target: level-1 bound (expect weak — the Shor relaxation of big-M-free disjunctions was void
in A09's MILP LP analogue; measure it), Tier A level-2 bound, Tier B level-2 bound, with and
without cuts (R1)–(R3) (ablation: the cuts are my main structural bet), SDP sizes, wall times.
Success criterion: some level-2 configuration certifies s(2), s(3) ≥ 2 − 10⁻⁶ and pushes s(5)
meaningfully above the trivial 2 (ideally to 2.7071 − 10⁻⁴). Then extract ONE dual (SOS)
certificate for n = 2 or 3, round to rationals (Peyrl–Parrilo projection onto the identity
subspace), and verify: (i) each Gram matrix PSD by exact LDLᵀ over Q, (ii) the polynomial identity
s − λ = σ_0 + Σ σ_k g_k + Σ φ_l h_l in exact arithmetic (σ SOS from the Gram forms, h the
equalities). That validates the whole trust chain end-to-end.

## 7. The n = 11 question (T3) and the endgame exclusion encoding (design only)

T3: Tier A level 2 (then Tier B if A is affordable-and-weak) at fixed s = 3.83 / 3.84 / 3.85:
report the moment-relaxation status (infeasible = kill at that s) or the min-s bound vs the proven
pure-LP ceiling τ*(3.83) = 11.000 (A07/A19). If nothing runs at n = 11, the deliverable is the
measured wall: largest n′ with Tier A/B level 2 feasible + block-size scaling law.

Endgame form (to run only if T3 is a GO): certify min s ≥ ŝ − ε OUTSIDE A22's certified box
(‖z − z₀‖_∞ ≤ 5·10⁻⁴ around Trump, which handles the inside). Two sound encodings:

(i) **66-branch disjunction** (recommended): WLOG symmetry-breaking rows first (fix the D4 frame
and an S_11 canonical labeling — e.g. lexicographic order of (x_i, y_i); every packing has an orbit
representative satisfying them, and each row is linear inside a pair clique, so sparsity survives).
Then the complement of the box is the union over the 66 coordinates (33 config coords × 2 sides;
u-coords excluded — the box is in configuration space) of half-spaces {z_k ≥ z⁰_k + 5·10⁻⁴} /
{z_k ≤ z⁰_k − 5·10⁻⁴}. 66 SDPs, each = base SDP + ONE linear row in one square's clique;
warm-startable; certificates independent and individually rational-verifiable.

(ii) **single ball cut**: ‖z − z₀‖₂² ≥ (5·10⁻⁴)² is implied by ‖z − z₀‖_∞ ≥ 5·10⁻⁴, so certifying
on F ∩ {ball cut} covers the box complement. One degree-2 row, but it couples ALL configuration
variables — lives only on Tier B's K_0, and breaks S_11 averaging unless the labeling is already
fixed by (i)-style rows. Use only if the 66-fold cost is the binding constraint.

Caveat recorded: ε > 0 is structural — the SDP certifies a strict bound on the closed complement;
matching A22's interior statement at ŝ exactly needs the standard ε → 0 / compactness stitch at
the box boundary (the boundary shell is INSIDE A22's certified region, so any ε < A22's local gap
5·10⁻⁴/155.7 ≈ 3.2·10⁻⁶ · δ-margin suffices; quantify when run).

## 8. Honest risks

- Tier A's limit may be < s(11) (no RIP): the pilot cannot distinguish "level 2 too weak" from
  "Tier A ceiling" without Tier B runs.
- The 6-D pair continuum killed A17–A20's kernels via cutting-plane escape; here the pair
  constraints are IMPOSED exactly (16 polynomial rows), not separated — that failure mode does not
  transfer. The transferred risk is plain relaxation weakness at low level.
- Solver: Mosek license vs open (COSMO/Clarabel/SDPA); Clarabel stalls at big cones (A19/A20
  lesson) — a-posteriori feasibility check on every headline solve is mandatory lab practice.
