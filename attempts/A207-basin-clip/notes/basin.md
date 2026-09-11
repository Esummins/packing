# NEAR-SIMPLE IS SIMPLE: Lemma BASIN, the basin certificates of the FULL extension classes, and the basin clip — A207, 2026-09-11

The PI's reading (2026-09-11 14:40, Y0881 leaf R.2.3s): "it's basically just setting F1 directly in a simple slot, and then
using the fact that the pads grow around corners to claim the simple square totally isn't simple" — and the lever the PI
named with it: the BASIN of the extension certificate around the simple pose (the descent idea of `docs/proofs/descent.md`
Theorem D2 applied to the library's own kills).  Credit for "near-simple is simple" and for the basin/descent idea: the PI.
Labels: [T] proved here, [S] routine given the cited items, [M] measured (`results/basin207.jsonl`, `results/basinclip207.jsonl`,
`results/s0basin207.jsonl`, `certs/`, `logs/`), [F] false / did not happen, [C] obligation.  Conventions: `forced_corners.md`
(Theorem FC, the pad π_i, the dilation Δ_λ), `k0_route.md` §4.1 (K0-WIDEN), `slot_crowds.md` (Lemma SLOT-CROWD), A53
`notes/lemmas.md` L5 and A56 `notes/soundness.md` P3 (what a case-measure / parametric certificate kills), A57's page frame
(a page = a node about F = Δ_λ P at s0, λ ∈ [1, λ_1]; λ_1 − 1 = 0.0040 on the G1 slab, 0.0149 on the whole window).
n-general throughout: n unit squares, any class S, any Young-completable unclipped non-pin cell p, any side window.

## 0. Verdict

> **[T] Lemma BASIN.**  The kill of the extension class T = S ∪ {p} does not stop at the simple pose of p: re-solving T's
> case LP with p's exact pin replaced by the BOXED square |c − c_p|_∞ ≤ r_c, |tan(θ/2)| ≤ t_r (its core the axis-aligned
> square [c_p ± a]², a = 1/(2(cos + sin)(t_r)) − r_c) gives a certificate of the same kind that kills every packing of the
> window containing the pins of S and ANY square within (r_c, t_r) of the simple pose of p.  Transported to a page's frame
> (F = Δ_λ P, λ unknown in [1, λ_1]) the dead set is the box B_F(p) = ∩_λ [λ(c_p ± r_c)] × {|tan(θ/2)| ≤ t_r} — the
> basin around EVERY point of the dilation drift segment of the simple pose — and it may be cut from every role's pieces
> and from every anonymous option row of the page (§2).  **[M] The library's own certificates have basin ≈ 0** (the poses
> beside a pin were exempt, so no atom covers them: k6_28's certificate fails at r_c = 0.03 with mass 0.53 at (2.394,
> 2.379), §3.0); the basin is a property of a RE-SOLVED certificate, priced per (class, slot) in §3.

## 1. Setting

A class S with pin set P_S: axis-aligned unit squares at census slots, slot centre coordinates α + βm on a container of
side m (β ∈ {0, 1}: anchored to the wall at 0 or at m).  A cell p = (c, i, j) of the census (corner c, offsets i, j) has
slot centre c_p(m) with coordinate u_p := i + 1/2 measured from the corner's vertical wall and v_p := j + 1/2 from its
horizontal wall; in container coordinates x = u_p on an UNREFLECTED axis (corner at x = 0) and x = m − u_p on a
REFLECTED one (corner at x = m).  T = S ∪ {p}.  A case-measure certificate (A13/A53, `verify_case.py`; parametric over a
side window [m_lo, m_hi] by A56 `verify_param.py`) declares cores K_q = [k_q ± a_q]² (tilted by t_q) and an atomic
measure μ_m with μ_m(total) < n − #cores, and a PASS certifies: every admissible closed unit square Q ⊂ [0, m]² meeting
no core has μ_m(Q) ≥ 1, for every m of the window.  Its kill (A53 L5, A56 P3 — exactly the reading under which the
scoreboard's FULL rows are consumed by Theorem FC): no packing of n unit squares in [0, m]², m ∈ [m_lo, m_hi], has a
square containing each core.  For the library's k6 certificates the cores are the six pins' (half-side 0.4999999692,
tilt 2⁻²⁵ in t-units), and an axis-aligned pin at its slot contains its core [S: a(cos + sin)(tm) = 0.49999999899 ≤ 1/2,
checked in rationals].

**The basin core.**  For rationals r_c ≥ 0 and t_r ≥ 0 (t = tan(θ/2)) put w(t) = cos θ + sin θ = (1 + 2t − t²)/(1 + t²)
and a(r_c, t_r) := ⌊(1/(2 w(t_r)) − r_c)·10⁹⌋/10⁹, so that (a + r_c) w(t_r) ≤ 1/2 exactly.  The BASIN CERTIFICATE C_r of
(T, p) is a certificate as above whose cores are T's library cores for q ∈ P_S and, for p, the axis-aligned core
K_p(m) = [c_p(m) ± a]² (tilt 0), verified over its window [m_lo, m_hi] ⊆ [191/50, s0] by the frozen `verify_param.py`
(sha 0c58485c…) and cross-checked at m_lo, (m_lo + m_hi)/2, m_hi by the frozen `verify_case.py` (sha 521cb01f…) on the
specialisations (A56's canary C2).  `code/basin207.py` builds it: A53 `caselp.solve_node` with the modified hypothesis
(the LP's row filter exempts exactly the poses meeting K_p), A54's certify loop at s0, A56 `make_param` (gap anchoring),
`verify_param`, C2; every number in the certificate is a rational.

## 2. [T] Lemma BASIN

**(i) Containment.**  Let Q be a closed unit square with centre c and tilt θ folded into (−45°, 45°], |c − c_p(m)|_∞ ≤ r_c
and |tan(θ/2)| ≤ t_r.  Then K_p(m) ⊆ Q.
*Proof.*  For x ∈ K_p(m) write x − c = (x − c_p) − (c − c_p) = v − d with |v|_∞ ≤ a, |d|_∞ ≤ r_c.  Q = {c + R_θ y : |y|_∞ ≤
1/2}, so x ∈ Q iff |R_{−θ}(v − d)|_∞ ≤ 1/2.  Each component of R_{−θ}(v − d) is cos θ·z₁ ± sin θ·z₂ with |z_i| ≤ a + r_c,
hence bounded by (a + r_c)(|cos θ| + |sin θ|) = (a + r_c) w(|θ|) ≤ (a + r_c) w(t_r) ≤ 1/2, because w is increasing in |θ|
on [0°, 45°] and (a + r_c) w(t_r) ≤ 1/2 by the construction of a.  ∎

**(ii) The P-frame kill.**  Let C_r PASS on [m_lo, m_hi].  Then no packing of n unit squares in [0, m]², m ∈ [m_lo, m_hi],
contains the pins of S together with a square Q as in (i) (Q of any index; it is automatically a non-pin: a pin of S is
axis-aligned at another slot, at ℓ∞-distance ≥ 1 > r_c from c_p).
*Proof.*  Such a packing has a square containing every core of C_r: each pin of S contains its library core (§1) and Q ⊇
K_p(m) by (i).  This is the hypothesis C_r's PASS forbids at side m (A53 L5 / A56 P3).  Nothing about Q's alignment or
about a slot is used — the certificate prices core containment only.  ∎

**(iii) The F-frame clip.**  A page at s0 is a node about F = Δ_λ P: P a packing at side m = s0/λ containing the pins of
S, λ ∈ [1, λ_1] unknown (the G1 slab: λ_1 = s0/3.861637; the whole window: λ_1 = s0/3.82; pad 0: λ_1 = 1), and
s0/λ_1 ≥ m_lo.  Define, per axis, with u the slot coordinate (u_p or v_p) and
    I(u) := [λ_1 (u − r_c), u + r_c]   on an unreflected axis,   I(u) := [s0 − u − r_c, s0 − λ_1 (u − r_c)]   on a reflected one,
    B_F(p) := I(u_p) × I(v_p),   T_B := {θ : |tan(θ/2)| ≤ t_r}  (as tilts in [0, 90): [0, r_t] ∪ [90° − r_t, 90)).
Then no square Q′ of F has centre in B_F(p) and tilt in T_B.  Consequently every piece (centre rect × tilt bin) of every
role of the page — H, an instantiated meeter, an anonymous option row's reach — may be replaced by piece ∖ (B_F(p) × T_B).
*Proof.*  Q′ = Δ_λ Q for a square Q of P with centre c and the same tilt (`closed_disjoint_bridge.md` Lemma B.0: dilation
moves centres by λ and leaves sizes and tilts alone), c′ = λc.  On an unreflected axis the P-coordinate of the slot is u
and c′ ∈ I(u) ⊆ [λ(u − r_c), λ(u + r_c)] for the true λ (λ ≤ λ_1 and u − r_c > 0 give λ(u − r_c) ≤ λ_1(u − r_c);
λ(u + r_c) ≥ u + r_c), i.e. |c − u| = |c′/λ − u| ≤ r_c.  On a reflected axis the P-coordinate is x = m − u_P with u_P the
distance from the far wall and x′ = λx = s0 − λu_P; c′ ∈ I(u) ⊆ [s0 − λ(u + r_c), s0 − λ(u − r_c)] (λ(u + r_c) ≥ u + r_c and
λ_1(u − r_c) ≥ λ(u − r_c)) gives |u_P − u| ≤ r_c.  So Q is within (r_c, t_r) of the simple pose of p at side m ∈ [s0/λ_1, s0]
⊆ [m_lo, m_hi], and (ii) says P does not exist — contradicting the node's hypothesis.  The clip is the tautologous
decomposition of a rect minus a closed box into ≤ 4 rects (`clip207.rect_minus`) on the tilt sub-bins inside T_B
(`clip207.tilt_parts`: the bin is split at t_r and at t(90° − r_t) = (1 − t_r)/(1 + t_r)); every dropped pose lies in
B_F(p) × T_B, every kept pose is kept whole.  ∎

*What "within the basin" means in F's frame.*  The simple pose of p is not one point of the page: over the page's λ range
its dilate sweeps the segment {λ c_p(m) : λ ∈ [1, λ_1]} = {(s0 − λ(i + 1/2), s0 − λ(j + 1/2))} at a TR-anchored slot (length
0.006 × 0.002 on the G1 slab for TR(1,0)).  Because λ is unknown, a pose is excluded only if it lies in the basin of
EVERY point of the segment — the intersection of the boxes, which is what I(u) is (the box is shrunk by the drift on the
side the segment moves towards, and grown by λ r_c − r_c ≥ 0 on the other).  On pad 0 (λ_1 = 1) B_F(p) is the plain box
[c_p ± r_c]²; on the G1 slab it is the box [c_p − r_c, c_p − 0.006 + λ_1 r_c] (x) × [c_p − r_c, c_p − 0.002 + λ_1 r_c] (y)
for TR(1,0).

*Soundness grade.*  (i) and (iii) are elementary and exact in rationals; (ii) inherits the certificate semantics of the
library (A53 L5 / A56 P3, [S] there; the same reading Theorem FC uses for the FULL rows).  A kill that uses the clip is
therefore [C: extension certificate + Lemma BASIN + library clip trace] with the basin certificate's path, r_c, r_t and
window named in the leaf string.  **What the lemma does NOT say [F]:** nothing about a second meeter, nothing about the
pads — the pad-only survivor is killed because its near-simple square is impossible outright, not because its partner is.

## 3. [M] The basins — see §3.1 for the table (filled by `run_basin207.py`, rows in `results/basin207.jsonl`)

### 3.0 The library certificates have no basin [M]
k6_28's re-solved certificate (`attempts/A56-sparametric/certs/resolved/k6_28.json`, 9 atoms, margin 0.23) with its
TR(1,0) core shrunk to (r_c, r_t) = (0.03, 2.5°) FAILS at s0 in 8 s: 5 holes, worst at θ = 2.18°, centre (2.3937, 2.3786),
exact mass 53/100 — an upright square just below the pin whose top edge (2.879) no longer reaches the shrunken core
(bottom at 2.928).  The poses beside a pin were EXEMPT when the LP was solved, so no atom was ever placed for them: the
basin of an as-solved certificate is the eps_core margin (0.002) and nothing more.  The basin is bought by re-solving.

### 3.1 The per-slot basin table
(see the report / `results/basin207.jsonl`; filled below at the end of the campaign)

## 4. [M] The clip — Y0881's leaf, the alive leaves of A206 / A205, the stage-0 pass

(filled at the end of the campaign; rows in `results/basinclip207.jsonl`, `results/s0basin207.jsonl`)

## 5. What the basin could not do

(filled at the end of the campaign)
