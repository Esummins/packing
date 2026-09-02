# The U_k ladder: multi-square rigidity of ẑ as a COUNTING row on the exact strata — A80, 2026-09-02

Target (A80 BRIEF, PI idea): extend Theorem U (`theorem_u.md`: ten squares of ẑ force the
eleventh — 11 certificates, Σw = 0) upward to U_k (11 − k squares near their ẑ-slots force the
other k), and compose with the basin theorem into a counting exclusion on the exact protected
strata: "at most 10 − k squares within (r_c, r_t) of their Trump-slot poses" — a row for the
pair LP of `pair_kill.md`, one level above Lemma P-B (whose row is the k = 0 case: not all 11).
Labels: [T] proved, [S] routine given cited items, [M] measured/computed exact (interval) or
float LP (stated), [C] open. Code `attempts/A80-u-ladder/code/` (the A66 rig COPIED, the A65
emitter re-parametrised, the frozen `verify_case.py` byte-identical: sha256 521cb01f…bef7af).

**Headline (findings first).** (i) [T] The row is sound on the EXACT stratum only and its
soundness has exactly one new ingredient, Lemma U-C (a square within (r_c, r_t) of a slot
contains the slot's slack core once δ ≥ r_t + √2(r_c + ρ_B)); everything else is Lemma P-B's
proof with U_R in place of "all N in-zone". (ii) [T] In the pair LP the level-k row is the single
linear inequality Σ_{in-zone pairs} z ≤ C(6 − k, 2) per image, and by LP duality its multiplier
IS the discount γ of the certificate form (P2″) with rebate C(6 − k, 2)·γ — so the ladder is
measured by ONE constrained LP per rung with no γ sweep, and rung 0 reproduces P-B's optimum
over γ. (iii) [M] T1 — the reach of U_1: the pocket of a removed square at core slack δ is NOT
δ-sized: square 6 (the top tilted square, held by the top wall, the flush contact with 9 and the
point contact with 4) has a pocket of half-widths (5.6 δ, 5.8 δ) in (centre, t) — the hinge
amplification of `grain_discharge.md` §4 seen from inside — so the pocket lands in the basin
only for δ ≤ 5.6·10⁻⁴ (A40 radii) / 2.6·10⁻⁴ (Lean rBasin = 3/2000): **the reach collapses
below 10⁻³**, as the BRIEF's reserve clause anticipated. (iv) [M] T2 — the decisive number: see
§6 (filled from `attempts/A80-u-ladder/results/ladderlp_k4_08*.json`).

## 0 Setting and conventions

As `pair_kill.md` §6/§6.8: class S (k_S pins, N = 11 − k_S free squares; for k4_08 k_S = 4,
N = 7, m = 7 boxes, threshold C(7,2) + 7β = 28 at β = 1), certified side s″ (s0 for the pair
certificate), stuck packing z at side m̃ ∈ [ŝ − ρ_B, ŝ] with skeleton EXACTLY S, compatible
Trump images G_S (k4_08: {id, diag}, A71/A76; both pull back to the Trump-frame pin set
{0, 1, 3, 5}, free slots {2, 4, 6, 7, 8, 9, 10}). Configurations in (c, t)-coordinates, t =
tan(θ/2) (E.COORD); for the six upright slots "within r_t of t̂ = 0" means the equivalent tilt
mod π/2 (`theorem_u.md` §3: t ∈ [1 − h, 1] ⇔ |t′| ≤ h/(2 − h) + (h/(2−h))³). A **basin box**
B = (r_c^B, r_t^B): a theorem σ ≥ ŝ with equality iff ẑ on |c − ĉ|∞ ≤ r_c^B, |t − t̂|∞ ≤ r_t^B,
|s − ŝ| ≤ ρ_B — instantiated by the Lean `basin` axiom (3/2000, 3/2000), by A36 per coordinate
(37/10000, 37/20000) and by A40 per coordinate (5794/884563 ≈ 6.55·10⁻³, half of it in t), all
with the P-B(R) reading (side separately in the shell, no (1+√2) gate).

## 1 The U_R statements

For R ⊆ {0, …, 10} and radii r = (r_c, r_t) define the hypothesis on a packing z at side m̃:

  H_R(r): there is an injective assignment of squares of z to the slots j ∉ R with
          |c_q − ĉ_j|∞ ≤ r_c and |t_q − t̂_j| ≤ r_t (equivalent tilt) for the assigned square q.

**U_R(r; B)** := every packing z at side m̃ ∈ [ŝ − ρ_B, ŝ] with H_R(r) has ALL 33 coordinates in
the basin box B of ẑ, hence (basin equality clause, σ(z) ≤ m̃ ≤ ŝ) z = ẑ. Theorem U of A65 is
U_{{i}}(0; Lean basin) for each i. The ladder's level k is the family {U_R : |R| = k}; the
statement is D4 × S₁₁-covariant (apply g), and the two-images bookkeeping of P-B is inherited.

Two certificate forms deliver U_R, both `case-lp-certificate-v1` PASSes at s″ = 3877083591023/10¹²
(A65's realised side; λ = s″/m̃ ∈ (1, 1 + 2.6·10⁻¹⁰ + ρ_B/ŝ·(1 + …)]) with cores K_j (j ∉ R) =
the tight-certificate poses at half-side a = 1/2 − δ and zones F_i (i ∈ R) = (hw_c, hw_t)-boxes
around the tight poses:

* **C⁰_R** (Σw = 0, budget |R|): PASS ⇔ every admissible placement meeting no core lies in
  some F_i. Bridged (Lemma B-NO, `closed_disjoint_bridge.md` B.2″, applied |R| times — with
  Σw = 0 the pigeonhole prices ANY non-exempt non-owner, so all |R| non-owners are exempt):
  every non-owner square of Δ_λ z has (λc, t) in some F_i, and two disjoint unit squares cannot
  share a zone (zone diameter ≪ 1), so the non-owners occupy the |R| zones bijectively.
* **C¹_R** (0 < Σw < |R|, atoms in the merged pocket): PASS ⇒ at least one non-owner is exempt
  (if all |R| were priced, μ ≥ |R| > Σw). Weaker, needed exactly when the merged pocket of R
  has intermediate placements (a flush pair's 1 × 2 slab: a unit square slides from slot i to
  slot j meeting no core — C⁰ fails at those placements, one atom of weight 1 on the shared
  edge covers them all, Σw = 1 < 2).

**Lemma U-C (containment) [T].** Let q be a square of z with |c_q − ĉ_j|∞ ≤ r_c, |t_q − t̂_j| ≤ r_t
(equivalent tilt), z at side m̃ ≥ ŝ − ρ_B, λ = s″/m̃, and K_j the certificate core of slot j
(centre κ_j with |κ_j − (s″/ŝ)ĉ_j|∞ ≤ ε_κ, tilt t_r with |t_r − t̂_j| ≤ ε_t, half-side 1/2 − δ;
A65 ledger: ε_κ ≤ 2·10⁻¹⁴, ε_t ≤ 10⁻¹³). If

  δ ≥ (r_t + ε_t) + √2·(λ(r_c + ρ_B) + ε_κ)                                             (U-C)

then K_j lies in the open interior of Δ_λ q. *Proof.* In q's body frame the core's corners sit
at o + R(Δθ)·(1/2 − δ)(±1, ±1) with o = R(−θ_q)(λc_q − κ_j) and Δθ = θ_r − θ_q. |λc_q − κ_j|∞ ≤
λ r_c + |λ − s″/ŝ|·|ĉ_j|∞ + ε_κ ≤ λ(r_c + ρ_B) + ε_κ (|λ − s″/ŝ| = s″(ŝ − m̃)/(m̃ŝ) and
|ĉ_j| ≤ ŝ), so |o|∞ ≤ |o|₂ ≤ √2(λ(r_c + ρ_B) + ε_κ); |Δθ| ≤ 2(r_t + ε_t) (X.1 of
`theta_t_transfer.md`, both branches for uprights). A corner's body-frame ∞-norm is ≤
(1/2 − δ)(cos + sin)(Δθ) + |o|∞ ≤ (1/2 − δ)(1 + |Δθ|) + |o|∞ = 1/2 + (1/2)|Δθ| − δ(1 + |Δθ|) +
|o|∞ < 1/2 iff δ(1 + |Δθ|) > |Δθ|/2 + |o|∞, implied by (U-C). ∎

**Lemma U-R (from certificates to U_R) [T].** Fix r, ρ_B and a basin box B with r_c + √2ρ_B +
slop ≤ r_c^B, r_t ≤ r_t^B. (a) If C⁰_R PASSes at slack δ satisfying (U-C) for r, with zones
(hw_c, hw_t) whose pull-back satisfies hw_c + √2ρ_B + slop ≤ r_c^B and hw_t + hw_t³ ≤ r_t^B,
then U_R(r; B). (b) If C¹_R PASSes at slack δ satisfying (U-C) for r, with zones (hw_c, hw_t),
and U_{R∖{i}}(max(r, hw); B) holds for every i ∈ R, then U_R(r; B). *Proof.* (a) H_R(r) and
Lemma U-C give hypothesis (H) of Lemma B-NO for the |11 − R| cores with distinct owners; the
PASS + B-NO (Σw = 0 form) put every non-owner in a distinct zone; pulling back through λ the
zone deviations are ≤ hw_c + √2ρ_B + slop in centres (the P-B drift bookkeeping, dominant
term |ĉ|(ŝ − m̃)/ŝ ≤ √2 ρ_B... per coordinate ≤ ρ_B; the √2 is the conservative constant of
`pair_kill.md` §6) and ≤ hw_t (+ the cubic on the t ≈ 1 branch) in tilt; the assigned squares
deviate by ≤ r; so all 33 coordinates are in B. (b) As (a) up to "some non-owner q* is in some
F_i"; then the squares assigned to slots ∉ R together with q* at slot i satisfy
H_{R∖{i}}(max(r, hw)), and U_{R∖{i}} concludes. The case split over i ∈ R is finite. ∎

The peeling in (b) is where the ladder's reach is spent: each atom-bearing level costs a factor
≈ (√2 + 1)·(pocket amplification) in δ downward, because the zone of level k is the radius of
level k − 1. Since the row's LP value is insensitive to the zone radius (§6, and A76's
saturation law), the reach only has to stay above the B&B resolution — it does not have to be
large; what the ladder buys is the COUNT, not the radius.

## 2 [T] Lemma BR (bridging dichotomy — what the "connected-component shortcut" is)

For R and slack δ let free(R) be the set of admissible placements meeting no core K_j, j ∉ R.
Then free(R) ⊆ ⋃_{i∈R} free({i}) ∪ Bridge(R), where Bridge(R) = placements meeting no core
outside R and meeting ≥ 2 cores of R. *Proof.* A placement in free(R) meets at most the cores
of R; if it meets at most one of them, K_i say, it avoids all cores of {0..10}∖{i}. ∎
Consequently, given the level-1 PASSes (free({i}) ⊆ F_i, each Theorem-U certificate), C⁰_R
PASSes iff Bridge(R) ⊆ ⋃ F_i, and Bridge(R) is non-empty only when a unit square can touch two
cores of R at once while clearing the other nine (7 …): for a flush-contact pair it is the
whole sliding slab; for a point-contact or non-adjacent pair it is decided by the same B&B in
the same sub-second run. So the honest shortcut is not a lemma that saves certificates — every
C⁰_R is cheaper than the lemma it would replace — but the statement of WHICH R need atoms:
exactly those whose removed squares carry a flush contact of ẑ (edges (0,1), (0,3), (6,9),
(7,8), (7,9), (8,10), (9,10) of Trump's contact graph, `grain_discharge.md` §2); the seven
point contacts and the 41 non-adjacent pairs have Bridge(R) ⊆ ⋃F_i by the direct certificate
[M — the census for |R| = 2 is in `attempts/A80-u-ladder/results/`, §6, when T3 ran]. A
disconnected R = R₁ ⊔ R₂ (no contact between the parts) can still have a non-empty Bridge(R)
through Trump's sub-10⁻² gaps (7–4: 0.0126; strip gaps 0.0249), which is why the direct
certificate, not a separation lemma, is the sound route.

## 3 [T] Lemma U-ROW (the counting row, exact stratum only)

**Setting.** Lemma P-B(R)'s: certificate side s″ = s0, class S with pins, compatible images
G_S, zones Ẑ_{g,j} = (r_c, r_t)-boxes in (c, t) at s0 around the s0-dilated poses of the N
non-pin squares of g·ẑ, stuck packing z at m̃ ∈ [ŝ − ρ_B, ŝ] with skeleton EXACTLY S, and the
per-coordinate basin conditions r_c + √2ρ_B + slop ≤ r_c^B, r_t ≤ r_t^B, ρ_B ≤ ρ_B^B.

**Lemma U-ROW.** Suppose U_R(r; B) holds for every R ⊆ (free slots of g) with |R| = k (in
Trump's frame, after the pull-back by g), with r = (r_c + slop, r_t) (slop = the s0 ↔ s″
re-dilation drift ≤ (1 − s″/s0)·ŝ ≤ 4.1·10⁻⁷ and the 10⁻⁸ rounding of the LP's zone centres).
Then for every g ∈ G_S, at most N − 1 − k of the N free squares of Δ_λ z (λ = s0/m̃) lie in
zones of g. Equivalently, since the k_S pins are always in-zone (slot drift (λ − 1)·5/2 ≪ r_c,
B.0(c)): at most 10 − k of the 11 squares are within r of their g·ẑ poses.

*Proof.* Suppose N − k free squares of Δ_λ z lie in zones of g (distinct zones: two disjoint
unit squares cannot share one). Together with the k_S pins that is 11 − k squares; let R be the
k slots of g·ẑ not so occupied — R consists of free slots. Pull g back: the pulled-back
packing satisfies H_R(r) with r as stated (zone membership at s0 pulls back to |c − ĉ_j| ≤
r_c + ρ_B·|ĉ_j|/ŝ + rounding, |t − t̂_j| ≤ r_t; pins to |c − ĉ_j| ≤ (5/2)(ŝ − m̃)/m̃, tilt 0).
U_R(r; B) then gives z = g·ẑ. But g·ẑ has FIVE simple squares (a trump5 image), so its skeleton
is not exactly S (k_S ≤ 4) — contradicting the exact-stratum hypothesis. ∎

**Where the exact-stratum hypothesis enters (and the monotone trap).** Exactly once, in the
last sentence, and it is load-bearing: a MONOTONE hypothesis ("z contains the pins of S") is
satisfied by g·ẑ itself (compatibility of g), so the row would then assert something false of
Trump — the same trap as Lemma P-B's, one level up. Everything before that sentence is a
statement ABOUT Trump-near packings that Trump satisfies (he is the U_R conclusion, never
excluded). The row is a theorem of the InStratum-exact semantics (`instratum_bridge.md`) and
nothing else; it is not a valid row for the ∀-packings quantifier of `stratum_kill`, and it is
consumed only where H10-stuck's rows are (the teleport-stuck endpoint of the selection chain,
`unique_transfer.md` §2–3, side in the ρ_B-shell below ŝ).

**Certificate form and pricing [T].** For rung k and multipliers γ_g ≥ 0 the pair certificate
claims (P2‴) μ₂{Q, Q′} ≥ 1 + β m₂(Q, Q′) − Σ_g γ_g bz_g(Q, Q′) on every admissible interior-
disjoint core-free pair and (P1‴) W₂ < C(N, 2) + βm − Σ_g γ_g·C(N − 1 − k, 2). Kill: Lemma P's
chain with Σ_{a<b} bz_g ≤ C(N − 1 − k, 2) for every g by Lemma U-ROW. Sound for every choice of
γ_g ≥ 0 (a subset of G_S is allowed: fewer discounted pairs). In the restricted packing LP of
the A66 rig (max Σ z_ij(1 + βm₂) s.t. point loads ≤ 1) the rung is the HARD row
Σ_{ij: bz_g = 1} z_ij ≤ C(N − 1 − k, 2) per image — valid for every real family, hence for the
LP; by LP duality (one extra constraint with multiplier γ_g*) the constrained value V_k equals
min over γ of [Lagrangian value + γ·C(N−1−k, 2)], i.e. V_k < threshold ⇔ a restricted
certificate of the (P2‴)/(P1‴) form exists at γ = γ*. So margin_k := V_k/L_max − threshold is
the rung's restricted margin, rung 0 is Lemma P-B optimised over γ (A66 measured γ = 0.1 by
hand: −1.40), and the whole ladder is one LP per rung on a shared row store.

## 4 [S] Composition (what changes in the composed proof: nothing structural)

The row is an additional valid inequality on the death-witness side of Lemma P for the stuck
endpoint; its consumption path is Lemma P-B's verbatim (`pair_kill.md` §6, shell caveat
included: below the ρ_B-shell the pins' slot drift leaves the basin and the row is dropped).
Its own inputs are (i) the U_R certificates (case-LP PASSes at s″, `verify_case.py` frozen,
V.CASE lean-proved soundness) with the exact side-condition ledger (Lemma U-C margins, zone →
basin containment, the peeling slack chain), (ii) `basin` (equality clause only; A36/Lean or
A40 per coordinate — stated per ledger), (iii) InStratum-exact. No new axiom; Trump is never
excluded by any U_R (he is its unique solution) — the exclusion is the skeleton mismatch.

## 5 Canary

Every U_R certificate EXHIBITS ẑ: with all zones deleted (control form) the only holes are
Trump's own pockets, and the PASS says "the free space supports unit squares only there";
the composed conclusion is z = g·ẑ. The counting row asserts nothing that ẑ falsifies: ẑ has
11 squares in-zone and skeleton trump5, so it is outside the row's quantifier (exact k4_08).
The LP measurements are adversary-side. SAFE by construction; per-run ledger in
`attempts/A80-u-ladder/notes/findings.md`.

## 6 [M] Measurements

(filled by A80 T1/T2; see `attempts/A80-u-ladder/notes/findings.md` for the tables)
