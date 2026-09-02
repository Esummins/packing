# A83 adversarial review (R3/R4) — verify_tube.py + tube certificates

Reviewer: Opus, read-only audit, 2026-09-02.

**Moving target warning.** `certs/verify_tube.py` was edited **twice** during this review.
Everything below is against the final version audited:

    certs/verify_tube.py    885 lines
                            sha256 9cc21a5adc4527418fb5a2f305fb928f10e97902869e5b873ca774453de436f7
    certs/tube_slot_T1e-2_landing.json   sha256 dfe7b4c2401b186cd8384b9732fee66aa28d54704274aac6f5fe4440849568c6
    certs/tube_scale_T1e-2_landing.json  sha256 09b1093f2b9f3365d9ae5330725ecbcd7d2720c40a05e6903bffb1f9d4cfa662

The two mid-review changes were (1) `[H]`: `|Hv|_i` went from the one-sided
`mag(sum_a v_a H_ab)` to the symmetrized `(|(v^T H)_i| + |(H v)_i|)/2`; (2) PAIR-RELATIVE
EVALUATION of edge/dist rows plus a strengthened `[CANARY]`. Both are audited below; both
are sound. `certs/` grew from 2 to 11 tube certificates over the same window.

---

## (i) VERDICT

**SOUND.** Every inequality the checker gates on is a valid bound for the corresponding
quantity in T1, over the correct set (the tube, resp. the r0-widened hull box `B`), for
every feasible `z` in the tube. No unsound line found, in either the pre- or the
post-`pair_box` version. All six declared corruption gates fail as required, and the
A36 regression reproduces `beta 0.4353 / Hbar 7.908 / kappa_eff 19.316 / psi/h 0.9978`
exactly.

Findings are hygiene / trust-boundary / documentation, not soundness. The three that
matter: **`a22_sha256` is silently optional** (a cert without it passes, 20 checks instead
of 21); **the `claims` blocks of the two named certificates are now stale by up to 48%**
and the checker computes that deviation and never prints it; and **`pair_box`'s
correctness rests on an unasserted coupling** between `row_box`'s `kind` test and
`row_jet`'s expressions.

### Chain audit, point by point

**(a) `tb`, `wb` — VALID at every feasible point of the tube.**
`v_s = 1` is gated, so `d_s = -t + w_s`, hence `t = w_s - d_s <= |w_s| + |d_s| <= r_s + x`;
with `t <= T`, `t <= tb = min(T, x + r_s)`. And `w_i = d_i + t v_i` gives
`|w_i| <= x + t|v_i| <= x + tb|v_i|`, while `|w_i| <= r_i` by definition of the tube;
hence `|w_i| <= wb_i`. Both hold pointwise at the **actual** `x = |d|_inf` of that `z`,
which is exactly what the dichotomy consumes. Sound.

**(b) `q_vv`, `|Hv|`, the cross term — VALID; symmetry is not assumed.**
`q_vv = mag( sum_{a,b} v_a v_b [H_ab] )` — interval sum THEN magnitude — encloses
`v^T H(xi) v` for a single `xi`, since each `[H_ab]` encloses `H_ab(xi)`. With
`d = -t v + w`,

    (1/2)|d^T H d| <= (1/2)t^2 |v^T H v| + (t/2)(|v^T H w| + |w^T H v|) + (1/2)|w^T H w|

and `|v^T H w| <= sum_i |(v^T H)_i| |w_i|`, `|w^T H v| <= sum_i |(H v)_i| |w_i|`. So
`Hv_mag[i] = (|Hv_col[i]| + |Hv_row[i]|)/2` with coefficient **`tb`, not `2 tb`**, is
exactly right: the factor 2 of the cross term is cancelled by the 1/2 of the Taylor
remainder. No symmetry of the accumulated interval Hessian is needed.
Measured: the accumulated interval Hessian is in fact **exactly** symmetric
(max `|Hd[a,b] - Hd[b,a]| = 0`, no missing transposes), so the change is belt-and-braces.
The pre-change one-sided form was *also* sound, because every `Hd` entry encloses the
**true** (symmetric) `H_ab`. `B` (resp. the pair box) is convex and contains both `z-hat`
and `z`, so the Lagrange form of Taylor along `[z-hat, z]` is legitimate.

**(c) Monotonicity of `psi` — HOLDS.**
`tb(x) = min(T, x + r_s)` nondecreasing; `wb_i(x) = min(r_i, x + tb(x)|v_i|)` nondecreasing;
`e0, ew, q_vv, |Hv|_i, |H_ij|` are nonnegative constants; so `E_of` is monotone
nondecreasing, and `psi = (keff E + kappa g_max)/(1-beta)` is too (`keff >= 0`,
`1 - beta > 0`). Base case `x <= X_max = max_i(T|v_i| + r_i + 2 r0)` holds since
`|d_i| <= T v_i + r_i` (the `2 r0` is unneeded but outward). The induction
`x <= psi(x) <= psi(x_n) = x_{n+1}` is correct, and the stagnation break
(`if x >= prev: break`) leaves `reached = False`, i.e. fails safe.

**(d) `[V]` — applied to every loaded edge row.**
The loop is `for k in range(36)` filtered to `kind == 'edge'`. Measured: the loaded set is
**exactly** `{0..35} u {44,45}` = 20 wall + 16 edge + 2 dist, and `omega = 0 off the
universal rows` is gated, so every loaded edge row is covered (unloaded ones too —
conservative). Wall rows (containment) and dist rows (separating-hyperplane / half-width)
are globally valid for feasible `z` by A22 notes section 1; the code correctly does not
re-verify those lemmas — but it also never asserts the row-kind layout it depends on
(suggestion 2).

**(e) `[N]`, `[C]`, `[CANARY]`, `direction_spec` — gating but NOT load-bearing for T1.**
The dichotomy never uses `gamma_k >= 0`, the Farkas identity, the strict-compression list,
the canary, or the `1e-40` activity tolerance (`eps_0` and `g_max` are recomputed exactly
regardless). They are structural / "this ray really contracts" claims. The `[CANARY]`
strengthening (require `gam[k].lo > 0` **and** `gcon[k].hi < 0`) is a real improvement —
without it a `gamma = 0` wall row could satisfy the canary off `z0`'s ~1e-60 residual.
It fires non-vacuously: 4 wall rows on the slot cert (`W4c0[x=0]`, `W4c3[x=0]`,
`W6c2[y=s]`, `W10c1[x=s]`), 20 on the scale cert. Two residual nits:
  * `gcon` is still evaluated at the **point** `z0 - T v`, not over `box(z0 - T v, r0)`,
    so "`g_k(z-hat - T v) < 0`" is off by `r0 = 1e-50`. Since wall rows are exactly affine
    along the ray (`v_theta = 0`), the rigorous version is free from already-computed
    quantities: `g(z-hat - T v) = g(z-hat) - T gamma <= 1e-40 - T gamma_lo < 0`.
  * the Farkas tolerance `|sum omega gamma - 1| <= eps_w + 1e-30` implicitly assumes
    `|v|_inf <= 1` (the true bound is `||rho||_1 |v|_inf`). `|v|_inf = 1` in the shipped
    certs and the `1e-30` pad swamps `eps_w ~ 8e-45`; a large `v_i` would give a false
    alarm, never a false accept.

**(f) Rounding — outward everywhere.**
`IV.__init__` applies `rdown`/`rup` after every operation; `mag()` is an upper bound;
`e0, ew, g_max, q_vv, |Hv|, |H_ij|, beta, kappa, kappa_eff` are exact-rational upper
bounds; `E_of` and `psi` use unrounded `Fraction` arithmetic; the iterate is
`rup(psi(prev))`, i.e. rounded **up** — the sound direction for a monotone map. No float
enters any decision: `frac()` explicitly raises on JSON floats.

**(g) A22 handover — correct; `r_N` is around `z0`, not `z-hat`.**
A22's Krawczyk box is centred at `c = z0` (notes section 3: `K(B) = -Y F(c) + ...`,
`r_N = 5e-4` "the theorem box"). So `|z - z0|_inf <= |z - z-hat|_inf + |z-hat - z0|_inf
<= x_n + r0 <= r_N` — and the `+ r0` in the gate exists for exactly that reason. Correct.

**(h) `slot` direction detection — not a soundness gate.**
Soundness needs only `v >= 0`, `v_s = 1`, `v_theta = 0`, all gated. `direction_spec` is
documentation / anti-hand-edit. The `1e-30` R-slot threshold against 60-digit `z0` and
`r0 = 1e-50` is comfortable. But it duplicates `emit_tube.direction()` formula-for-formula,
so it catches JSON edits, not emitter bugs; and a pinned coordinate matching neither an
R-slot nor an L-slot silently gets `v_i = 0` with no diagnostic. Harmless for T1; it means
"the tube covers the configurations at side m" is entirely the emitter's obligation.

**(i) Kernel vs `a36_check_exact.py` — verbatim modulo two intentional differences.**
`IV`, `J`, `row_vars`, `row_jet`, `build_constraints`, `axis_corner_positions`, `_cos_pt`,
`_sin_pt`, `sin_iv`, `rdown`, `rup` are byte-identical modulo comments. Differences:
`cos_iv`'s `if/else` rewritten as a ternary (semantically identical); `frac` widened to
accept ints/decimal strings and **hardened** to raise on JSON floats. `edge_td` is a
refactor of a36_check_exact's inline `[V]` loop with identical arithmetic.

### (j) PAIR-RELATIVE EVALUATION — SOUND (audited three ways)

The claim: edge and dist rows are translation invariant in the centres, so they may be
enclosed on a box where square `i`'s two centre slots carry the interval of `c_i - c_j`
and square `j`'s carry the point `0`, instead of on the hull box `B` where the two centres
vary independently.

**Algebraic argument — holds.** Three things must be true and all three are:
1. *The row expressions depend on the centres only through `c_i - c_j`, literally.*
   In `row_jet`, the edge row is `nx*(qx - cjx) + ny*(qy - cjy) - 1/2` with
   `qx = cix + (ci*hx - si*hy)`, so `qx - cjx = (cix - cjx) + rot`; the dist row is
   `(V0-V2)^2 + (V1-V3)^2 - 1`. In `edge_td`, `wx = qx - box[3j]` likewise. Nothing in
   either normal `n(theta_j)` or corner offset `R(theta_i)h` carries an absolute centre.
   Because value and **all** partial derivatives of `f(c_i - c_j, theta)` depend on the
   centres only through the difference, the same holds for gradients and Hessians —
   including `d/dc_j = -d/du`, which the jet gets right since `c_j` remains a *variable*
   (of value 0), not a constant.
2. *The interval covers the tube's `c_i - c_j` range.* For `z = z-hat - t v + w`,
   `(c_i - c_j)_ax = (zhat_a - zhat_b) - t(v_a - v_b) + (w_a - w_b)` with
   `zhat_a - zhat_b in z0_a - z0_b +- 2 r0`, `-t*dv in [-T max(dv,0), T max(-dv,0)]`, and
   `|w_a - w_b| <= r_a + r_b`. That is **exactly** `pair_box`'s `lo`/`hi`, correctly
   signed for either sign of `dv` (it does not even need `v >= 0`).
3. *Every mean-value / Taylor point lies in the tube.* The tube is
   `z-hat + ([-T,0] v) (+) Box(r)` — a Minkowski sum of a point, a segment and a box,
   hence convex, and it contains `z-hat`. So `[z-hat, z]` is inside it for every tube `z`,
   and `[V]`'s validity condition is pointwise at `z` anyway. Wall rows correctly keep
   `B` (they carry absolute `c_i` and `s`); tilt slots keep `B`, which is the exact tube
   range since `v_theta = 0`. Decorrelation across rows is harmless: each row's box
   encloses that row's quantities at the *same* `xi`, so the omega-weighted sums enclose
   `H(xi)` and `A_P(xi_r)`.

**Empirical check 1 — translation invariance is exact.** Evaluating every loaded edge/dist
row at a random tube point in the absolute frame vs the translated frame
`(c_i - c_j, 0, theta)` agrees on value, all gradient entries and all Hessian entries to
within **2 dyadic grid units** (max abs diff 9.14e-100 vs grid `2^-330` = 4.57e-100) —
i.e. pure outward rounding, no semantic difference.

**Empirical check 2 — the enclosure is real.** 432 sampled relative-centre coordinates over
random tube points *and* random segment points `z-hat + s(z - z-hat)`, with `z-hat` itself
randomized inside `box(z0, r0)`: **0 uncovered**. And the pair-box jet **encloses** the
true value / gradient / Hessian at every one of those points: **0 violations**.

**Empirical check 3 — it is a genuine tightening.** Max relative-centre interval width
0.012653 (pair) vs 0.023168 (hull), pair `<=` hull on every slot.

**Effect.** At `T = 1e-2` on the slot cert: `beta 0.3206 -> 0.2480`, min tangential
`0.00878 -> 0.01302`, `x* 2.08e-04 -> 1.54e-04`. Reach: the certified `T` grew from
`2.99e-2` (pre-change ceiling) to `6.2e-2` (slot) and `1.3e-1` (scale). At `T = 0` the pair
box and the hull difference have the *same* width (`2 r_c + 2 r0`), so the A36 regression
is bit-for-bit unchanged — a useful invariant.

**Residual risk (not unsoundness).** `pair_box`'s correctness is an **unasserted coupling**
between `row_box`'s `kind in ('edge','dist')` test and `row_jet`/`edge_td`'s expressions.
If a row kind were added, a row mislabelled, or an absolute-position term introduced into
an edge row, `pair_box` would become unsound **silently**. See suggestion 1.

**Trusted inputs not re-verified** (appropriate delegations, but they belong in the
"WHAT IS CHECKED" list as *assumed*): `krawczyk_cert.json`'s `r_0`
(`|z-hat - z0|_inf <= 1e-50`), `r_N`, `Y`, `S`, `constraints`; A22 strict local optimality
on `box(z0, r_N)`; the wall / dist global validity lemmas and the edge validity lemma.

---

## (ii) Gates and adversarial edits — outcomes

### Cold runs, current checker (exit 0)

    verify_tube: 2 certificate(s), A22 cert krawczyk_cert.json (sha256 f82689e754a1...), PREC 330, EXACT
      [ok] slot_T1e-2_landing     T=1/100      rc=1/625     rt=21/10000  beta=0.2480 Hbar=7.881 q_vv=0.000e+00 Hv1(tilt)=0.100 keff=19.316 psi/X=0.0669 x*=1.54e-04 n=2 tan=0.01302 (E4c1-7e2) 0.9s
      [ok] scale_T1e-2_landing    T=1/100      rc=1/625     rt=21/10000  beta=0.2502 Hbar=7.881 q_vv=2.199e-02 Hv1(tilt)=0.039 keff=19.316 psi/X=0.0818 x*=1.98e-04 n=2 tan=0.01302 (E4c1-7e2) 0.7s
      2 certificates, 42 checks, 0 failures, 1.6 s
    => ALL CHECKS PASS

All 11 certificates now in `certs/` pass (231 checks, 0 failures, 8.7 s). `[V]` remains the
binding limit on `T`: min tangential 0.01302 (T=1e-2) -> 0.00121 (T=4.2e-2) -> 0.00011
(T=6.2e-2) -> 0.00006 (scale T=1.3e-1), while `beta <= 0.55` and `psi/X <= 0.22`. So the
tube length is limited by A22 edge-row validity, not by the contraction.

### The six declared corruption gates — ALL FAIL AS REQUIRED (exit 0)

    ### omega-sign  corruption omega-sign: checker FAILED as required => PASS
        [FAIL] slot_T1e-2_landing omega >= 0
        [FAIL] slot_T1e-2_landing omega > 0 on every pin
        [FAIL] slot_T1e-2_landing [P] monotone iteration reaches x_n + r0 <= r_N (A22 handover) stopped at x = 4.7052e-02 after 1 steps (r_N = 5.0e-04)
    ### drop-pin    corruption drop-pin: checker FAILED as required => PASS
        [FAIL] slot_T1e-2_landing omega > 0 on every pin
        [FAIL] slot_T1e-2_landing well-formed KeyError(4)
    ### T-big       corruption T-big: checker FAILED as required => PASS
        [FAIL] slot_T1e-2_landing [V] A22 edge rows valid on the tube box tangential -0.372991 (E3c2-7e3), depth+1/2 0.297237
        [FAIL] slot_T1e-2_landing [K] beta(B) < 1 beta = 2.527239
        [FAIL] slot_T1e-2_landing [P] monotone iteration reaches x_n + r0 <= r_N (A22 handover) stopped at x = 1.0116e+00 after 0 steps (r_N = 5.0e-04)
    ### r-big       corruption r-big: checker FAILED as required => PASS
        [FAIL] slot_T1e-2_landing [V] A22 edge rows valid on the tube box tangential -0.039225 (E7c2-9e3), depth+1/2 0.936616
        [FAIL] slot_T1e-2_landing [K] beta(B) < 1 beta = 1.829467
        [FAIL] slot_T1e-2_landing [P] monotone iteration reaches x_n + r0 <= r_N (A22 handover) stopped at x = 2.2800e-02 after 0 steps (r_N = 5.0e-04)
    ### drop-aux    corruption drop-aux: checker FAILED as required => PASS
        [FAIL] slot_T1e-2_landing omega > 0 on every pin
        [FAIL] slot_T1e-2_landing well-formed KeyError(44)
    ### wrong-ray   corruption wrong-ray: checker FAILED as required => PASS
        [FAIL] slot_T1e-2_landing direction v >= 0
        [FAIL] slot_T1e-2_landing direction matches spec slot(pins=[0, 1, 2, 3, 5])
        [FAIL] slot_T1e-2_landing [C] gamma_k >= 0 on every loaded row min lo -6.895e-01
        [FAIL] slot_T1e-2_landing [C] declared strictly compressed rows have gamma > 0 bad: [6, 11, 13, 15, 16, 17]
        [FAIL] slot_T1e-2_landing [C] strictly compressed rows negative at z-hat - T v max hi 6.895e-03

`wrong-ray` on the scale cert also fails (same five checks: `min lo -5.159e-01`,
`bad: [0,1,2,3,4,5]`, `max hi 5.165e-03`).

Note: `drop-pin` and `drop-aux` fail **partly by crashing** — the `KeyError` comes from
`gmax = max(gz[k].mag() for k in P)` where `gz` is keyed only by loaded rows, caught by the
blanket `except (KeyError, ValueError, AssertionError)` and reported as "well-formed". The
designed check `omega > 0 on every pin` does also fire, so the gate is real, but the crash
path is fragile.

### A36 regression (T = 0, r_c = r_theta = r_s = 3689/1000000) — REPRODUCES A36 EXACTLY

      [ok] A36regress  T=0/1  rc=3689/1000000 rt=3689/1000000 beta=0.4353 Hbar=7.908
           q_vv=0.000e+00 Hv1(tilt)=0.105 keff=19.316 psi/X=0.9978 x*=3.91e-04 n=10
           tan=0.00617 (E4c1-7e2) 1.0s
      1 certificates, 21 checks, 0 failures  =>  ALL CHECKS PASS

Target beta 0.4353, Hbar 7.908, kappa_eff 19.316, psi/h 0.9978 — **exact match on all
four**, both before and after the `pair_box` change (`psi/X` here is `psi(X_max)/X_max`
with `X_max = h + 2 r0`, i.e. A36's `psi(h)/h`).

### Adversarial edits (scratchpad copies only — nothing under `certs/` was touched)

| # | edit | outcome | rejected by |
|---|------|---------|-------------|
| 1 | `r_s = 1/1`, `T = 0` (r_s huge) | **PASS** (exit 0), psi/X 0.0007, x* 9.65e-05 | — SOUND, see note |
| 2 | negate `omega` on a **non-pin** loaded row (row 1) | FAIL (1) | `omega >= 0`; `[P]` psi/X 2.36 |
| 3 | `direction_v[2] = 1/1000` (nonzero tilt) | FAIL (1) | `direction centre-only`; `direction_spec`; `[C] gamma >= 0` (min lo -5.0e-04) |
| 4 | add row 0 (gamma = 0) to `strictly_compressed_rows` | FAIL (1) | `[C] declared strictly compressed rows have gamma > 0  bad: [0]` |
| 5 | remove `a22_sha256` | **PASS** (exit 0), 20 checks instead of 21 | — **SHOULD NOT PASS SILENTLY** |
| 6 | `T = 1e-9` with A36-size `r_c = r_theta = 3689/1000000` | **PASS** (exit 0), psi/X 0.9978, x* 3.92e-04, n=10 | — correct; the A36 box does survive a tiny `T > 0`, but only barely (psi/X is already 0.9978 at T=0) |
| 7 | `T = 0`, landing radii | PASS, beta 0.2254, psi/X 0.3337 | — sanity: `T = 0` disables `[C]`/`[CANARY]` by design |
| 8 | `direction_v[0] = 2/1` on the scale cert (`|v|_inf > 1`) | FAIL (1) | `direction_spec`; `[C] gamma >= 0` (min lo -3.23). **No soundness gate fired**; the Farkas check still passed |
| 9 | `v = e_s` only (freeze centres, shrink only `s`) | FAIL (1) | `direction_spec` **only** — every soundness gate passed |
| 10 | `r_s = T = 1/100` (tb saturates at T) | PASS, psi/X 0.0388, x* 1.95e-04 | — correct |
| 11 | truncate `direction_v` to 30 entries | exit 1 via **uncaught IndexError traceback** | — contract says malformed => exit 2 |
| 12 | all `omega` halved (grad W = e_s/2) | FAIL (1) | `[P]` (eps_w -> 0.5, psi/X 25.8). Farkas passed *at the boundary* (0.5 >= 1 - 0.5) |

**Nothing PASSES that should not on soundness grounds.** Three PASSes need a note:

* **#1 (`r_s` huge) is SOUND.** `W` is *exactly affine in `s`* — verified: **not one nonzero
  Hessian entry touches index 33** (wall rows `x=s`/`y=s` are `s - q_x`, linear in `s`; no
  other row involves `s`). `Hbar` is bit-identical to the `r_s = 0` case (7.881 both) and
  `beta` is unchanged. The certified statement is the *stronger* true claim: "any feasible
  `z` whose centres/tilts are within `(r_c, r_theta)` of `z-hat`, with `s` anywhere in
  `s-hat +- 1`, has `|z - z-hat|_inf <= 9.65e-05`, hence lies in A22's box". Consequence:
  **a large `r_s` is not evidence of reach.** The reach levers are `T`, `r_c`, `r_theta`.
* **#9 (`v = e_s`) is SOUND but vacuous.** T1 is true for that tube; only `direction_spec`
  rejects it. Confirms that "the tube covers the configurations at side `m`" is the
  emitter's / campaign's obligation, not the checker's.
* **#5 (no sha) should not pass** — see finding 1 below.

### Extra finding: the shipped certificates' `claims` are STALE and it is never printed

`check_cert` computes `claims_max_rel_dev` and stores it only in the `--report` JSON; it is
never printed and never gated. Both named certificates were emitted under the
pre-`pair_box` checker, so:

    slot_T1e-2_landing    beta  claim 0.320577  recomputed 0.248039  dev 22.6%
                          x_star claim 2.0758e-4 recomputed 1.5369e-4 dev 26.0%
                          psi_over_Xmax claim 0.074121 recomputed 0.066915 dev  9.7%
                          min_tangential claim 0.008778 recomputed 0.013018 dev 48.3%
    scale_T1e-2_landing   beta  claim 0.336823  recomputed 0.250207  dev 25.7%
                          x_star claim 2.8304e-4 recomputed 1.9788e-4 dev 30.1%
                          min_tangential claim 0.008778 recomputed 0.013018 dev 48.3%

Every deviation is in the conservative direction (recomputed is *better*), so there is no
soundness issue — the checker gates on its own values, as documented. But a reader of the
JSON is being handed numbers up to 48% off, and a cold run gives no hint. Re-emit, or print
the deviation.

---

## (iii) Gaps between the docstring's theorem and what the code checks

1. **`a22_sha256` is optional.** `if cert.get('a22_sha256') and not corrupt:` — a certificate
   omitting the field passes with one fewer check and no warning (edit #5). With `--a22 PATH`
   free-form, nothing then binds a certificate to a particular A22 input. Not documented.
2. **The docstring's `[F]` says "T, r rational, T >= 0, r > 0"**; the code (and its own gate
   string) accepts `r_s >= 0`, and every shipped certificate has `r_s = 0`.
3. **`[C]` / `[CANARY]` are listed among the load-bearing checks** with no indication that
   the T1 proof does not use them. They gate the exit code, so a false alarm there blocks a
   sound certificate, and a reader will over-read their significance.
4. **The canary / strict-compression are evaluated at a point**, `z0 - T v`, not over
   `box(z0 - T v, r0)`, so the docstring's blanket "every quantity below is an exact
   rational interval enclosure over the tube box B" and "[C] ... `g_k(z-hat - T v) < 0`"
   are both stronger than what runs.
5. **The Farkas tolerance assumes `|v|_inf <= 1`**, neither stated nor gated.
6. **The `PAIR-RELATIVE EVALUATION` docstring paragraph understates the widths** by a factor
   two on the `w` part: it says half-width "`T|v_i - v_j|/2 + r_c`" (pair) and
   "`T(v_i + v_j)/2 + r_c`" (hull), but the code correctly uses `rad[a] + rad[b] = 2 r_c`
   plus `2 r0`. Code right, comment wrong. The justification sentence also cites only
   convexity; the load-bearing half is translation invariance of the *derivatives*, which
   only the inline comment mentions.
7. **Trusted-but-unchecked inputs are not listed**: `r_0`, `r_N`, `Y`, `S`, `constraints`
   from `krawczyk_cert.json`; A22 optimality on `box(z0, r_N)`; the three validity lemmas.
   "WHAT IS CHECKED" reads as if a PASS were self-contained.
8. **The claimed A36 regression is not executable from the file.** The docstring says
   "the checker reproduces a36_check_exact's constants on G3_UNIVERSAL (regression)" —
   true (I reproduced it by hand-editing a copy), but nothing in the repo runs it.
9. **`claims_max_rel_dev` is computed and never surfaced** on the console (only in the
   `--report` JSON) — see the stale-claims finding above.
10. **The code never asserts the row-kind layout** it relies on: nothing checks that
    `cons[0..35]` are only `wall`/`edge` and that 44/45 are `dist`. True today (20 + 16 + 2),
    but it is exactly the assumption that makes `[V]`'s restriction to `range(36)`
    sufficient — and, since `pair_box`, also the assumption that decides which rows get the
    relative box.
11. **Emitter (`emit_tube.py`).** Certification-in-the-loop is honest: `evaluate()` runs the
    real `check_cert`, a file is written only on PASS, and `strictly_compressed_rows`
    computed by the emitter is re-verified by the checker, so there is no circularity.
    Two nits: (a) `direction()` is a verbatim copy of the checker's `slot`/`scale` formula,
    so the `direction_spec` gate is a tautology w.r.t. emitter bugs (it catches only
    hand-edits to the JSON); (b) the written file is never re-verified from disk after the
    JSON round-trip, and `claims` are attached *after* the evaluation that produced them —
    which is how the stale-claims situation above arose when the checker changed.

---

## (iv) Suggestions, ranked

1. **Pin the `pair_box` invariant with a runtime self-test.** For each edge/dist row, at a
   fixed pseudo-random point, assert that `row_jet` in the absolute frame and in the
   translated frame `(c_i - c_j, 0, theta)` agree on value, gradient and Hessian to within a
   few grid units (I measured 2 units, 9.14e-100). Cost < 0.1 s. This converts the currently
   *implicit* coupling between `row_box`'s `kind` test and `row_jet`'s expressions into a
   checked invariant, and is the single highest-value addition given how much reach now
   rests on `pair_box`.
2. **Make `a22_sha256` mandatory** (fail when absent, not only when mismatched), and add
   `no-sha` / `swap-a22` corruption gates. It is the only binding between a certificate and
   its A22 input, and it is currently opt-in.
3. **Assert the row-kind layout** at load: `cons[k]['kind'] in ('wall','edge')` for `k < 36`,
   `== 'dist'` for `k in (44,45)`, no loaded row outside `{0..35, 44, 45}`. This is what makes
   "walls/dists globally valid, edges by `[V]`" — and now also "which rows get `pair_box`" —
   a theorem rather than an observation about today's `krawczyk_cert.json`.
4. **Re-emit the certificates and print `claims_max_rel_dev`** on the `[ok]` line, with a
   loud warning above ~1e-6. The two named certs are currently up to 48% stale.
5. **Remove the crash paths from the gates.** Compute `gz` over `loaded | set(P)` (or gate
   `om[k] > 0` before indexing) so `drop-pin`/`drop-aux` fail by a designed check rather than
   `KeyError`; add `IndexError`/`TypeError` to the `except` tuple so a malformed certificate
   returns 2 instead of a traceback (edit #11); validate `len(direction_v) == 34` and
   `len(omega_rational) == 70` *before* they are used.
6. **Make `[CANARY]` rigorous for free.** Wall rows are exactly affine along the ray
   (`v_theta = 0`), so `g(z-hat - T v) = g(z-hat) - T gamma <= eps_N - T gamma_lo`; gate on
   that instead of evaluating at the point `z0 - T v`. Same for the strict-compression
   negativity check. Also gate `|v|_inf <= 1` (or use `eps_w * |v|_inf` in the Farkas
   tolerance).
7. **Mark load-bearing vs structural checks in the docstring.** Load-bearing for T1: `[F]`
   (v shape only), `[S]`, `[V]`, `[Z]`, `[G]`, `[H]`, `[K]`, `[E]`, `[P]`, plus the
   pair-relative invariant. Structural / informational: `[N]`, `[C]`, `[CANARY]`,
   `direction_spec`, `claims`. Add the trusted-input list (item iii.7) and fix the
   factor-two width statement (iii.6).
8. **Add a built-in `--a36-regress` self-test** running the `T = 0, r = 3689/1000000`
   configuration and asserting `beta 0.4353 / Hbar 7.908 / kappa_eff 19.316 / psi/X 0.9978`.
   It is a strong invariant precisely because `pair_box` collapses to the hull evaluation at
   `T = 0`, so it would catch an accidental change to the relative-box widths.
9. **Widen the corruption suite** to what is currently unprobed: negate a *non-pin* omega
   (edit #2 — caught only by `omega >= 0`), inject a nonzero `v_theta` (#3), declare a false
   strict row (#4), perturb `pair_box`'s sign convention (`max(dv,0)` <-> `max(-dv,0)`), and
   blow up `r_s` alone (#1 — document that it legitimately passes).
10. **Document the two structural facts a reader will otherwise mis-weigh**: `W` is affine in
    `s`, so `r_s` is free and is not a reach lever; and `[V]`'s min tangential margin (down to
    6e-05 at the current `T` ceiling) is the binding limit on tube length, not `beta` or
    `psi/X`.
11. **Emitter:** re-verify the written certificate from disk after `json.dump` (this is what
    would have caught the stale `claims`), and consider verifying `direction_spec` in the
    checker from a *different* formulation (check `v` against the slot lines' defining
    equations rather than recomputing the same expression) so the gate catches emitter bugs
    and not just hand-edits.
