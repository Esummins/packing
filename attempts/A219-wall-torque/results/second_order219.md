# A219 addendum 2b — the second-order (buckling) test on every four-crowd witness, 2026-09-14

Rows `second219.jsonl` (per witness, per variant: stationarity, every accepted zero mode with v₂, its status, the squares it moves,
the curve check); code `code/second219.py` (158 s for 193 witnesses), `modes219.py` (selection, completion, v₂, curve),
`rows219.py` (analytic Hessians, checked against central differences to 2·10⁻¹⁰).  Theory: `docs/proofs/wall_torque.md` §5
(Lemma STRUT, Theorem SO).

## 1. The ring `rand_0_0569|t20` — the PI's mode, verified

| quantity | value |
|---|---|
| loads on square 6 (A217's multipliers) | from 4 at P4 = (2.0586, 0.9397), from 7 at P7 = (2.9983, 1.2817); floor row active, λ = 0 |
| F(4 → 6) | (0.5375, 0.1956); moment about P7 = −2.7·10⁻¹¹ (collinear: a two-force strut) |
| rotation about P7, clockwise, 1 mrad | floor gap +5.98·10⁻⁴ (rate 0.598 / rad); gap to 7 +2.5·10⁻⁷; gap to 4 −7.5·10⁻⁷ (quadratic); **gap to rattler 0: −6.4·10⁻⁴ (first order)** |
| counter-clockwise | floor −5.97·10⁻⁴ (blocked by the floor); 7-contact −5.0·10⁻⁴ |
| loaded core (rattler rows dropped), clockwise | first-order zero mode (2 rows open); **v₂ = +0.381 > 0**: the side INCREASES at second order |
| 11 squares (rattler rows kept) | completion LP infeasible: rattler 0 is caged by 4, 5 (edge-edge on two sides) and 6 (corner at the triple point P4) — **the mode is blocked** |
| other core modes of 6 | rotations about the line points of the 6–7 contact: v₂ = +0.004 … +0.013; about its floor vertex (whole ring bends): v₂ = −6.8·10⁻⁴, w at the box, curve check FAILS — not claimed |

So the PI's diagnosis is exact up to the rattler (6 is a strut, its rotation is a first-order free mode of the loaded structure, the
floor opens, 4 closes only at second order), but the conclusion "a mechanism at second order" is not: along the mode the side goes
UP at second order, and in the actual 11-square configuration the mode does not exist (the caged rattler).  Page:
`docs/residue_map/campaigns/A219-wall-torque/ring_mode_rand_0_0569_t20.svg`.

## 2. All witnesses

Variants: **bounded** = every active row (the bounded problem the witness is a local optimum of); **loaded_ext** = walls + pair rows +
the external rows that carry load; **core** = loaded_ext restricted to the loaded squares (rattlers' rows dropped: for a global
minimiser a rattler may be moved within its free region); **free** = walls + pairs.  Candidates per variant: the rotation of every
square about every one of its active contact points, both senses (STRUT-labelled when the square's loads are exactly two point
loads), plus the eigenvectors of negative eigenvalue of the reduced Hessian at the LP multiplier; the unloaded squares complete the
mode by an L1-minimal LP; per pair the separating axis with the best rate is selected (NLP(S) branch); v₂ from the LP of Theorem SO
with |w|∞ ≤ 10; every v₂ < 0 re-checked along the curve x(t) = z + t y + t² w/2 at t = 10⁻⁴, 3·10⁻⁴, 10⁻³.

| class | n | variant | stationary (λ₀ = 1) | ≥ 1 zero mode | strut mode present | 2nd-order saddle (v₂ < 0) | of which curve-verified | not KKT under the mode's selection (no self-stress either: not FJ) |
|---|---|---|---|---|---|---|---|---|
| HELD  | 8   | bounded    | 7   | 5   | 2  | 0  | 0 | 2 |
| HELD  | 8   | loaded_ext | 7   | 5   | 3  | 0  | 0 | 3 |
| HELD  | 8   | core       | 7   | 5   | 3  | 1 (the marginal ring mode, −6.8·10⁻⁴) | 0 | 3 |
| HELD  | 8   | free       | 0   | –   | –  | –  | – | – |
| CROWD | 185 | bounded    | 182 | 119 | 48 | 11 | 8 | 29 |
| CROWD | 185 | loaded_ext | 182 | 119 | 48 | 11 | 9 | 29 |
| CROWD | 185 | core       | 182 | 85  | 48 | 11 | 6 | 29 |
| CROWD | 185 | free       | 0   | –   | –  | –  | – | – |

Notes.  (a) One HELD and three CROWD witnesses have no λ₀ = 1 multiplier on their own bounded rows by HiGHS (A217 accepted them
by NNLS residual < 10⁻⁸): counted as not stationary.  (b) "Not KKT under the mode's selection": the selection that makes the mode
feasible (a different tied axis at a vertex–vertex contact) admits no λ₀ = 1 multiplier and no self-stress — the point is not
Fritz-John for that NLP(S), excluded at first order by D3′ (a minimiser is FJ for every consistent selection); SLSQP's own selection
was KKT.  (c) No strut mode is a saddle anywhere: on all 48 + 3 strut modes v₂ ≥ 0 — the strut mechanism is real but stiff.
(d) Saddles occur only on CROWD witnesses (artificial pulls), at sides 4.0–4.5; the free variant is never stationary (A217's
finding: the external multipliers are positive), so the second-order test never had to decide a genuine k0 FJ point.

## 3. What Theorem SO adds to the toolbox

A (C)-type minimiser-only leaf (`drain_flow_k0.md` Lemma F-LEAF): at a residue chain landing on an unknown structure that IS
first-order stationary, the LP of Theorem SO (34 variables, ~30 rows, milliseconds) can still exclude it when a zero mode with
v₂ < 0 exists; it is exact for the direction tested and conservative in the completion.  It does not close anything by itself:
the objects it would have to exclude for k0_00 — genuine k0 FJ points with rattler crowds — are not saddles by any mode found
(K0FREE / BOXK0 were not in scope of this run; their zero modes are rattler motions with v₂ = 0).
