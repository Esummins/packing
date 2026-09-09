# A169 derivations — the maths behind `docs/proofs/sideband.md`

Notation as in the proof document: unit square Q with centre z, tilt θ, e = (cos θ, sin θ),
e⊥ = (−sin θ, cos θ); w(φ) = |cos φ| + |sin φ| (period 90°, w = cos + sin on [0°, 90°],
w = √2 cos(φ − 45°) there, so w is concave on each quadrant; w ∈ [1, √2]); half-width
g_Q(n) = w(∠n − θ)/2; support h_Q(n) = n·z + g_Q(n).  Box (0, c)², c ∈ {1, 1 + w₀},
w₀ = 0.025509.  Tags [T]/[S]/[M]/[F]/[C] as in the document.

## A. Lemma A1 — why 1/√2 and why it is sharp

SAT gives an edge normal n of one square with n·Δ ≥ 1/2 + g_{Q′}(n) ≥ 1 (both half-widths are
≥ 1/2).  The ℓ∞ bound is |n·Δ| ≤ (|n₁| + |n₂|) ‖Δ‖∞ ≤ √2 ‖Δ‖∞.  Both inequalities are tight
simultaneously for two 45° diamonds separated along the axis n = (1, 1)/√2 with Δ = (1/√2, 1/√2):
n·Δ = 1 = 1/2 + 1/2 (each diamond has half-width 1/2 along its own edge normal n), and the
diamonds share an edge.  The Euclidean form used in Lean is |Δ|₂ ≥ 1 (Cauchy–Schwarz against the
unit selection axis), which gives ‖Δ‖∞ ≥ 1/√2 since ‖Δ‖₂² ≤ 2 ‖Δ‖∞².  The Euclidean bound is
also sharp (the same pair), so the two forms are equivalent in strength.

## B. Lemma A2 — the cell diameters

Meeter centre bounds.  Lower: Q ⊆ {x ≥ 0} means every point z + a e + b e⊥ has x ≥ 0; the
point with a = −1/2, b = +1/2 has x = z_x − (cos θ + sin θ)/2 = z_x − w(θ)/2 ≤ z_x − 1/2, so
z_x ≥ 1/2 (Lean `quad_centre_ge_half`, which uses t ∈ [0, 1], i.e. cos θ, sin θ ≥ 0).  Upper: a
point p ∈ Q with p_x < c and |p − z| ≤ 1/√2 gives z_x < c + 1/√2, and in the square-free form
used by Lean: if z_x ≥ c then 0 ≤ z_x − c < z_x − p_x so (z_x − c)² < (z_x − p_x)² ≤ 1/2.

Cells.  On the NE side each coordinate lies in [c, c + 1/√2), a half-open interval of length
1/√2, so two such coordinates differ by < 1/√2 strictly.  On the SW side each coordinate lies in
[1/2, c), of length c − 1/2, which is < 1/√2 iff c < 1/2 + 1/√2 = 1.20711.  Both c = 1 and
c = 1 + w₀ qualify, with room: the SW cell has ℓ∞-diameter 0.5 (unit) / 0.5255 (widened)
against the 0.7071 that Lemma A1 forbids.  That slack is why (a) holds with NO restriction on
c: only the NE cell is used, and its diameter is < 1/√2 for every c.

Why the constant cannot be improved below c, in words: put one diamond just left of x = c
(centre x = c − ε) and as high as a meeter can be (centre y just under c + 1/√2, so its lowest
vertex just enters the open box), and the mirror image; they are separated along the
anti-diagonal with room ε′ − ε.  Both centres exceed c − ε in both coordinates.  The atlas's
"both centres beyond 1" search never found this for the unit box because there it needs both
centres beyond 1 = c, which Lemma A2 forbids; the widened box has the 0.0255 of room.

## C. Theorem B — the support-inequality device

The two inequalities of §3 and the three of Cor. B1 all have the form
  Φ(φ) := Σ_i λ_i w(φ + φ_i) ≥ const,  λ_i > 0 (or one λ_i < 0 handled separately),
and w(· + φ_i) is concave on each interval between consecutive break points
{−φ_i + k·90°}.  A finite sum of functions concave on a common partition is concave on each
piece, so its minimum over a piece is at an endpoint; the minimum over all φ is therefore the
minimum over the finitely many break points, where each w is evaluated at a multiple of 90°
(value 1) or at a known shift.  Every instance below reduces to a one-line check at the break
points.  (Lean [C]: after fixing the signs of the four products cos·cos, sin·sin, … the absolute
values open and `nlinarith` closes each piece; there are ≤ 8 pieces per inequality.)

Lemma B0 (wedge).  f(φ) = w(φ) − a·w(ζ + φ), a = cos ζ − sin ζ, target T = 2 sin² ζ =
1 − cos 2ζ.  Break points on [0°, 90°]: 0, 90° − ζ, 90°.  Values: f(0) = f(90°) = 1 − a w(ζ) =
1 − (cos²ζ − sin²ζ) = T (exact, so equality is attained at φ ≡ 0);
f(90° − ζ) = w(90° − ζ) − a = w(ζ) − a.  For a ≤ 0 (ζ ≥ 45°) f is a positive combination and
the break-point check finishes with w(ζ) − a − T = (w(ζ) − 1)(1 + a) ≥ 0.  For a > 0 the
second term is convex on its pieces, so the endpoint argument does not apply directly; but on
each piece f is a single sinusoid A cos φ + B sin φ with A, B ≥ 0 (A = 1 − cos 2ζ, B = sin 2ζ
on the first piece; A = 1 + a², B = 1 − cos 2ζ on the second), and such a sinusoid is concave on
[0°, 90°], so the endpoint argument applies after all; f(90° − ζ) = 2 sin ζ ≥ 2 sin² ζ.

Lemma B0′ (triangle).  g(ψ) = b w(ψ) + w(ψ − γ), b = cos γ + sin γ ≥ 1 > 0: a positive
combination; break points 0, γ, 90°; g(0) = b + w(−γ) = 2b, g(90°) = 2b, g(γ) = b w(γ) + 1 =
b² + 1 = 2b + (b − 1)² ≥ 2b.  The geometric content: the largest square in the right triangle
{x, y ≥ 0, cos γ x + sin γ y ≤ L} has side L/(cos γ + sin γ), attained by the axis-aligned
corner square (ψ ≡ 0), which is the classical "largest inscribed square has a side on a side"
fact, here proved directly for the right-angled corner.

Where the (⇒) argument uses them.  With Q2 ⊆ {n·q ≥ β} for the SAT normal n and Q2 in the
quadrant with a point p below y = c (NW case): the lowest possible position of Q2's centre is
governed by x₂ ≥ g and y₂ < c + g with g = w(ψ)/2, and the separation needs n·z₂ ≥ β + w(ψ − ζ)/2.
Eliminating z₂ leaves β < c cos ζ − [w(ψ − ζ)/2 − (cos ζ − sin ζ) w(ψ)/2]; B0 with φ = ψ − ζ
says the bracket is ≥ sin² ζ, with equality exactly when Q2 has tilt ψ ≡ ζ, i.e. an edge of Q2
lies on the separating line — the witness of (⇐).  The SW case is the same with B0′ and gives
(P); the NE case needs no inequality at all (the point p itself bounds n·z₂).

## D. Cor. B1 — the pressed square is lonely (unit box)

Pressed Q1: centre (g, g), g = w(θ)/2; h(n) = g (n₁ + n₂) + w(∠n − θ)/2.

(NE) at angle α: (2 − w(θ)) w(α) > w(α − θ)?  D(α) := w(α − θ) − (2 − w(θ)) w(α).  On
[θ, 90°]: D = P sin α + N cos α with P = 2 cos(45° − θ) − √2 ≥ 0 and N = √2 (cos θ − 1) ≤ 0,
so D′ = P cos α − N sin α ≥ 0: D increases from D(θ).  On [0, θ]: D = P′ cos α + N′ sin α with
P′ = 2 sin(θ + 45°) − √2 ≥ 0, N′ = √2 (sin θ − 1) ≤ 0, so D decreases to D(θ).  And
D(θ) = 1/√2 − (2 − √2 u) u with u = sin(θ + 45°) ∈ [1/√2, 1], = √2 (u − 1/√2)² ≥ 0.  So (NE)
never holds; equality only at θ = 0 (u = 1/√2), where the pressed axis square touches the
partner [1, 2] × [0, 1] — a touching, not a meeting, of the OPEN box.

(W) at ζ: need w(θ)(cos ζ − sin ζ) + w(ζ − θ) < 2 cos ζ − 2 sin² ζ for some ζ.  As a function
of θ with ζ fixed and ζ < 45° it is a positive combination of shifted w's, minimal at θ ≡ 0
(value 2 cos ζ) or θ ≡ ζ (value w(ζ)(cos ζ − sin ζ) + 1 = cos 2ζ + 1); both exceed the right
side (2 cos ζ ≥ 2 cos ζ − 2 sin² ζ; 1 + cos 2ζ − 2 cos ζ + 2 sin² ζ = 2 − 2 cos ζ ≥ 0).  For
ζ ≥ 45° the coefficient of w(θ) is ≤ 0, and the crude bound w(θ) ≤ √2, w(ζ − θ) ≥ 1 gives
left ≥ 1 + √2 (cos ζ − sin ζ), which exceeds 2 cos ζ − 2 sin² ζ because
1 − √2 sin ζ + (√2 − 2) cos ζ + 2 sin² ζ ≥ 1 − √2 + (1 − √2) + 1 = 0.17 > 0 on [45°, 90°].
(S) is (W) after the diagonal reflection θ ↦ 90° − θ (the pressed square is symmetric).  (P)
is vacuous at c = 1.  Hence lonely at every tilt.  ∎  Numerically (`slide169.json`
`inequality_min_over_grid`) the three left-minus-right expressions have minimum −2·10⁻¹⁶ on a
720 × 2880 grid, i.e. 0 to rounding.

## E. Cor. B2 — the slide family and the mode-(a) partner

Q1 on the floor at tilt θ, slid δ: centre (g + δ, g), g = w(θ)/2.  Its upper-left edge is the
line {e⊥·q = h(e⊥)} with h(e⊥) = −sin θ (g + δ) + cos θ g + 1/2 = g (cos θ − sin θ) + 1/2 − δ sin θ
= (cos²θ − sin²θ)/2 + 1/2 − δ sin θ = cos²θ − δ sin θ.  Clause (W) at ζ = θ (the partner Q2 of
tilt θ with an edge on that line and its left vertex on the wall): cos²θ − δ sin θ <
c cos θ − sin²θ, i.e. 1 − δ sin θ < c cos θ.  For c = 1: δ sin θ > 1 − cos θ, δ > tan(θ/2).
Depth: Q2's lowest vertex is at height (β + sin²ζ)/cos ζ with β = h(e⊥), ζ = θ:
(cos²θ − δ sin θ + sin²θ)/cos θ = sec θ − δ tan θ; intrusion below y = 1 is 1 − sec θ + δ tan θ
= (δ − tan(θ/2)) tan θ because sec θ − 1 = tan(θ/2) tan θ.  In t = tan(θ/2): tan θ = 2t/(1 − t²),
sec θ = (1 + t²)/(1 − t²), so intrusion = 2t(δ − t)/(1 − t²) and the lowest point is at
(1 + t² − 2tδ)/(1 − t²).  The PI's "intrusion in csc θ" is not reproduced: the exact mode-(a) intrusion is (δ − t) tan θ,
≈ δθ for small θ, and the partner's left vertex sits on the wall at height y_v + cos θ;
the numbers in `check_b.json` `depth` (grid vs closed
form, grid ≤ closed form by 0.007–0.026 at pitch 0.04) are consistent with the closed form
being the exact optimum of mode (a) and the grid being coarse.

## F. Cor. B3 — tilt 0 exactly

Q1 = [a, 1 + a] × [b, 1 + b].  (W): h(n_W(ζ)) = max_{Q1}(−sin ζ x + cos ζ y) = −a sin ζ +
(1 + b) cos ζ < cos ζ − sin²ζ ⟺ b cos ζ < sin ζ (a − sin ζ).  Maximise s (a − s)/√(1 − s²) over
s = sin ζ ∈ (0, min(a, 1)): the derivative has the sign of a − 2s + s³, so the optimum is the
root u of u³ − 2u + a = 0, i.e. a = u (2 − u²), and the value is u (a − u)/√(1 − u²) =
u (u − u³)/√(1 − u²) = u² √(1 − u²) =: F(a).  Small a: u ≈ a/2, F ≈ a²/4.  At a = 1:
u³ − 2u + 1 = (u − 1)(u² + u − 1), u = (√5 − 1)/2 = 0.618, F = 0.382 · 0.786 = 0.300.  For a ≥ 1
the pose is not a meeter.  (NE): h(n_NE(α)) = (1 + a) cos α + (1 + b) sin α < cos α + sin α ⟺
a cos α + b sin α < 0: never.  (S) is the mirror.  `lonely_exact.json` `theta0_law`: the raster
agrees at u = 0.1 … 0.6 (below the curve non-lonely, above lonely).

## G. Cor. B4 — the exact slide threshold and the crossing mode

For the slide family (NE) and (S) fail at δ = 0 (B1) and their left sides are increasing in δ
(the coefficient of δ is cos α ≥ 0, resp. cos ζ > 0), so only (W) can open, and
  δ_min(θ) = inf_{ζ ∈ (0°, 90°)} R_θ(ζ)/sin ζ,
  R_θ(ζ) = g (cos ζ − sin ζ) + w(ζ − θ)/2 − c cos ζ + sin² ζ,  g = w(θ)/2.
At ζ = θ: R = cos²θ + 1/2 − 1/2 ... = 1 − c cos θ and the quotient is (1 − c cos θ)/sin θ, the
mode-(a) value.  For ζ ≠ θ the partner's edge is not on Q1's edge; the separating line touches
Q1 at a vertex (its upper vertex for ζ < θ), and Q2's edge rests on that vertex: the "crossing"
mode.  `slide169.json` (scan at 1/40°, bisection to 10⁻¹²): the minimiser is ζ = θ up to
θ* = 56.757° and moves to ζ* < θ beyond (47.3°, 41.5°, 36.2°, 30.8°, 24.7°, 17.2° at
60°…85°), where δ_min = 0.5727, 0.6118, 0.6335, 0.6302, 0.5887, 0.4778 against tan(θ/2) =
0.5774, 0.6371, 0.7002, 0.7673, 0.8391, 0.9163.  So the mode-(a) law is exact on
[0°, 56.76°] and an upper bound beyond.  At θ = 0 the infimum 0 is not attained: R_0(ζ)/sin ζ =
(cos ζ − sin ζ + cos ζ + sin ζ − 2cos ζ + 2 sin²ζ)/(2 sin ζ) = sin ζ → 0.

Widened box (c = 1 + w₀).  The same formula with c; but now the pressed square (δ = 0) is not
always lonely: clause (NE) at α = θ reads g w(θ) + 1/2 < c w(θ), i.e. w(θ)² − 2c w(θ) + 1 < 0,
i.e. w(θ) < c + √(c² − 1) = 1.2528, i.e. sin(θ + 45°) < 0.8858, θ < 17.35° (and θ > 72.65° by
the reflection).  This is the exact pressed-square condition [T]: the scan shows α = θ is the
best (NE) direction and no (W)/(S) direction opens earlier [M].  The mode-(a) partner (height
sec θ < c, θ < 12.81°) is only the second-best witness.  Widened δ_min: 0.1062, 0.1670,
0.2238, 0.2789, 0.3336, 0.3887, 0.4449, 0.5002, 0.5472, 0.5813, 0.5970 at 20°, 25°, …, 70°.

## H. The atlas thresholds are pitch artefacts

`gen_two_meeter*.py` (atlas v2) raised the first meeter's displacement in steps and searched a
coarse raster of Q2 poses; the recorded "d*" is the first step at which the search succeeded.
At θ = 0 the true threshold is 0 (any δ > 0 admits the partner of tilt ζ ≈ arcsin δ hugging
the wall, which a coarse tilt raster misses), and at 15°–45° the true tan(θ/2) is 0.13, 0.27,
0.41 against the atlas 0.34, 0.38, 0.56.  The atlas remains right about one thing: the pressed
square is lonely for the unit box (B1).

## I. The lonely set, as A168 consumes it

Theorem B is a decision procedure for a POSE; for a BOX of poses the sound test is the one in
the document §6 R3: each clause is "∃ angle: (linear form in x, y) + w(θ − angle)/2 < r(angle)",
and w ≥ 1 gives the box-wise sufficient condition for loneliness (every clause fails on the
whole box).  In T = tan(angle/2) the clause (W) reads, after clearing (1 + T²)²,
  (1 + T²) [y (1 − T²) − 2 T x] + (1 + T²)² /2 ≥ c (1 − T²)(1 + T²) − 4 T²  (box corners for x, y),
a quartic in T on [0, 1] — Bernstein positivity decides it.  The measured lonely fractions
(`lonely_exact.json`, widened 0.54–0.74) say the row deletes most of each corner reach cover
before any LP is solved; the pair census reduction (0.4)² is the [S] estimate in §6.
