# STRIP₂ IN JAM under H1–H3 alone — what stops the square on every violator of the ring inequalities is X's right boundary casting a shadow over T_u's top (not the C–X wedge); the free-strip-square problem reduces [T] to a statement about a POINT and three CONVEX SETS (the DISC LEMMA), which is [M] true on the whole H1–H3 set with sup slack −0.005 (−0.017 for the square itself) and NOT proved; the case split is on the CENTRE's height, not on X's tilt — A272, 2026-09-23

The brief (A272 BRIEF): STRIP₂ under H1–H3 only — A267's proof needs the ring inequalities (U3)–(U6), (U8), which
A271 showed are FALSE as consequences of H1–H3 while STRIP₂ itself survives every violator; draw where the
square's best attempt sits on each violator and what stops it, then find the proof by cases (the brief's
candidate: on |φ − θ|).  Tags [T] proved, [T-prose] proved in prose with the arithmetic cores in Lean,
[T-computed] finite computation with its own check, [M] measured, [C] conjecture, [F] false.  Code
`attempts/A272-strip-jam/code/` (`upper272` the UPPER-case probe, `left272` the same with the LEFT constraint —
the probe that isolates the mechanism —, `disc272` / `disc272b` the disc-lemma tests, `pages272`); results beside
it; page `docs/residue_map/campaigns/A272-strip-jam/strip_jam.svg` (six panels, exact checks each); Lean
`Statements/Open/StripJam.lean`.  Notation as A267 / A271: corner frame, C the floater (h_u, h_v, θ; c, s;
L = (h_u, L_h), T = (h_u + c, C_top)), T_u = C − h_u e_x, S = T_u ∖ C, X the wall toucher (φ; B_X = (sin φ, X_low),
R_X = (w_φ, Y_R := X_low + sin φ), wall vertex W = (0, Y_W := X_low + cos φ), top X_top), r_X(y) / ℓ_C(y) X's right
and C's left boundary at height y, D := C_top − X_low (X's dip below C's top), Q the free square (centre q,
tilt ψ) with p ∈ int Q ∩ S.  The point T' := (c, C_top) is T_u's top vertex.

## 0. Verdict

> **[M] The mechanism on every violator (§1, page (a)–(f)).**  Restricting the probe to squares that could contain a
> strip point (centre above L_h by WEDGE-FLOAT, and LEFT: the part below C_top left of C), the best square on
> every violator is stopped by **X and T_u only** — active terms `gap_X` + `depth_Tu` (+ the LEFT constraint), C's
> gap NEVER active: sup t = −0.080 (U3), −0.179 (U4), −0.170 (U5), −0.175 (U6), −0.031 (U8-minimiser).  Q comes
> from the right, above C_top; to be right of X at every height of X it must clear X's lower-right edge up to its
> own left vertex, and that pushes its bottom right of T_u's top: **X's right boundary casts a shadow over T_u's
> top corner**, the C–X wedge that A267 trapped the chords in plays no part, and neither does A.  Without LEFT
> (`upper272`) the probe's sup is 0 — at h_u → 0, where Q sits RIGHT of C touching T_u's right edge from outside:
> a vacuous boundary (S has width h_u), not a mechanism.  Over the whole H1–H3 set (joint search, `left272`):
> **sup t = −0.0168**, at X FLAT (φ = 0), θ = 15°, h_u = 0.42, with Q flat, its bottom edge ON y = C_top right of
> X's right edge x = 1 (page (f)).  So the worst points are not "X tilted far from C" but X flat over a 15–35°
> C with X's flat bottom just under C's top — every one a (U3)+(U4) violator with (U5) tight.
> **[T] The reduction (§2–§4).**  Every free strip square has centre q above L_h (A267 §1–2); its horizontal
> chords at heights in [X_low, X_top] lie on ONE side of X (NO-LEFT + IVT); its part below C_top is left of C
> (LEFT).  Hence its inscribed disc D(q, ½) misses the two CONVEX sets Ξ := {X_low ≤ y ≤ X_top, x ≤ r_X(y)} (Q
> right of X; Ξ′ := {…, x ≥ X's left boundary} when Q is left of X) and Γ := {h_v ≤ y ≤ C_top, x ≥ ℓ_C(y)}, and
> its strip point p lies within 1/√2 of q outside Ξ ∪ Γ (a DROP conv(D(q, ½) ∪ {p}) ⊂ Q).  The case "q above X_top
> with Q LEFT of X" is dead outright by **Lemma CL** [T]: (D − cos φ) cot φ ≤ c, so the pocket left of X's
> upper-left edge above W misses T_u (Lean `cl_core_i`, `cl_core_ii`).  The other cases (q ∈ (L_h, X_low) with
> Q left of X, q ∈ (L_h, X_low) or [X_low, C_top] or above C_top with Q right of X) all reduce to
> **the DISC LEMMA: no point q with q_y > L_h, dist(q, Ξ) ≥ ½ (resp. Ξ′), dist(q, Γ) ≥ ½ lies within 1/√2 of
> P := S ∖ (Ξ ∪ Γ)** — a statement about a point and three convex sets in the five parameters (h_u, h_v, θ, X_low, φ),
> tilt-free.  Lean `centre_right_core`: Q's a-range crosses T_u's top edge, so only a poke reaches the strip.
> **[M] The DISC LEMMA holds on the H1–H3 set** (§5, `disc272`: centres above C_top, sup slack −0.005, attained
> only with h_v → 1.0000 — the open boundary where C leaves the box — and X flat; −0.047 on the 43 rings and the
> four violators; `disc272b`: centres in (L_h, C_top], right and left of X — see §5 for the numbers).  It is
> **NOT PROVED**: the hand proof by cases did not close, the disc lemma IS the residual, and its price (§6) is a
> box tree over the five parameters with a 2-D convex-geometry test per box, ~10² CPU-h on the H1–H3 set, ~20 on
> the (U3)–(U6)+(U8)-violating part — not launched (no verified kernel exists; A266's tilt-binned `strip266` at
> ~10³ CPU-h is the wrong tool).
> **Statement (§7): STRIP₂-IN-JAM ⟸ H1–H3 + DISC LEMMA** [T-prose]; Lean `strip_two_in_jam_of_disc` (axiom),
> `strip_two_in_ring_of_disc` (the pair3 bridge), cores `d_low_core`, `cl_core_i`, `cl_core_ii`,
> `centre_right_core`; A271's `strip_two_in_jam` under `RingIneq` untouched.  (U8) is FOLDED: the case
> q_y > X_top is Case C of §2, handled by the same reduction — (U8) is not a hypothesis anywhere.
> **What the brief had wrong (§8):** the case split is not on |φ − θ| — the violators' mechanism is uniform and
> the worst points have X FLAT; the C–X wedge ("tall but narrow") is not what stops Q; C is never the active
> obstacle; A267's argument does not survive for small |β| either (its (U3), (U5) can fail at β = 0).

## 1. The violators: where Q's best attempt sits and what stops it  [M, exact geometry check per panel]

`upper272` maximises t = min(gap(Q, C), gap(Q, X), Q_xmin, Q_ymin, depth(Q, T_u), q_y − L_h) over Q (centre, tilt;
grid 11 × 9 × 8 then Nelder–Mead) on adv271's violators and the 43 rings; `left272` adds the LEFT term
−max{x − ℓ_C(y) : (x, y) a vertex of Q clipped to the bands [h_v, L_h], [L_h, C_top]} (ℓ_C is affine on each band,
so the max is at a vertex).  Every Q reported passes the exact SAT check; every panel's configuration passes the
exact H1–H3 check (20 terms ≥ −10⁻⁹).

| violator | β = φ − θ | best Q without LEFT (`upper272`) | best Q with LEFT (`left272`) | active terms | what stops it |
|---|---|---|---|---|---|
| (U3) h_u .39, θ 34.5°, φ 0 | −34.5° | −0.061, ψ 0°, touching X, C, T_u | **−0.080**, ψ 0° | gap_X, depth_Tu, LEFT | X's right edge x = 1; T_u's top is 0.18 left of it |
| (U4) h_u .82, θ 10.4°, φ 28.7° | +18.3° | −0.139, ψ 72° | **−0.179**, ψ 83° | gap_X, depth_Tu | X's lower-right edge up to Q's left vertex |
| (U5) h_u .63, θ 2°, φ 45° | +43° | −0.102, ψ 71° | **−0.170**, ψ 82° | gap_X, depth_Tu | the 45° edge of X |
| (U6) h_u .90, θ 5.7°, φ 45° | +39° | −0.126, ψ 74° | **−0.175**, ψ 81° | gap_X, depth_Tu | the same |
| (U8)-min h_u .59, θ 20.8°, φ 0 | −20.8° | −0.027, ψ 0° | **−0.031**, ψ 0° | gap_X, depth_Tu, LEFT | x = 1; T_u's top vertex is INSIDE X; the exposed sliver is right of x = 1 |
| sup point (`left272` joint) h_u .42, θ 15°, φ 0, h_v .995 | −15° | — | **−0.0168**, ψ 0° | gap_X, depth_Tu | Q flat, bottom edge on y = C_top, left edge on x = 1 |

Without LEFT the near-misses are on the WRONG side of C (b < 0 at a > 1, below C_top: they contain no strip point
and say nothing); with LEFT the picture is uniform: **C's gap is never active**.  The obstacle is X's right
boundary — for φ > 0 its lower-right edge (Q's left vertex must be right of it, and the edge rises at cot φ per
unit height: the higher Q's left vertex, the further right Q's bottom), for φ = 0 its right edge x = 1 — together
with the requirement to reach T_u ∩ {y < C_top}, whose top vertex T' = (c, C_top) is at most w(θ) < 1.415 from the
wall.  On the rings (A267's domain, U3–U6 ≥ 0.04) the LEFT-constrained sup is −0.12 to −0.15: the ring domain
buys margin, not the mechanism.  The joint sup over H1–H3 (58 starts, 55 feasible ends) is −0.0168 at X flat:
STRIP₂ under H1–H3 alone is [M] true with that margin, away from the open boundaries (h_v → 1, h_u → 0, X's
depth in T_u → 0 — all three are where the JAM domain is open and the statement vacuous).
