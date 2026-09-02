# Lean-readiness note: the contraction tube on A79's RigidBasin machinery (A83, 2026-09-03)

Notes file only (no `.lean` edits by A83).  Theory and certificates:
`docs/proofs/contraction_tube.md`, `certs/tube_*.json`, checker `certs/verify_tube.py`.
The tube theorem is A36's `(V')` chain in new coordinates; everything below is stated as a
delta against `RigidKernel.lean` (`checkA36`) and `RigidBasinMain.lean` (`a36_basin`), so
the next rigidity wave can formalise it without redesign.

## 0. What is being certified

`Tube v T r = { ẑ − t•v + w : 0 ≤ t ≤ T, ∀ i, |w i| ≤ r i }` in the 34-dim θ-frame
(`Vec = Fin 34 → ℝ`), `v` a CENTRE-ONLY direction (`v (3i+2) = 0`, `v 33 = 1`, `v ≥ 0`;
two named instances: `scale` = `z0_i / z0_33` on every centre, `slot` = the trump5 pins ride
their slot lines with `v = β ∈ {0,1}`, free squares scale).  Theorem `tube_basin`:

    checkTube c a = true → InTube v T r z → Feas z → sZ ẑ ≤ sZ z ∧ (sZ z = sZ ẑ → z = ẑ)

exactly `a36_basin`'s conclusion with `InBoxZ ẑ h` replaced by `InTube`.  With `T = 0` and
`r i = h` for all `i` the checker and the theorem specialise to `checkA36`/`a36_basin`
(the Python checker reproduces `G3_UNIVERSAL`'s constants at `T = 0`, see the doc §1.5).

## 1. The certificate structure (delta on `A36Cert`)

    structure TubeCert extends A36Cert where
      T      : Rat            -- depth along the ray
      rC rT rS : Rat          -- perturbation radii on centres / tilts / s
      v      : Array Rat      -- 34 entries, the direction (checked: v_theta = 0, v_s = 1, v ≥ 0)
      strictRows : Array Nat  -- rows declared strictly compressed (informational, see §4)

`omega`, `P`, `universal := true` as in the universal A36 certificate (`ω` supported on rows
0..35 and 44, 45 only; no branch rows, no L1 disjunction — the tube is branch-free by
construction, §4).

## 2. The box (what changes in `radBox`)

    def tubeBox (z0 : Array Rat) (v : Array Rat) (T : Rat) (rad : Array Rat) (r0 : Rat) : Box :=
      Box.ofArray (Array.ofFn fun i => IV.mkR (z0[i] - T * max (v[i]) 0 - rad[i] - r0)
                                             (z0[i] + T * max (-v[i]) 0 + rad[i] + r0))

asymmetric per coordinate (contraction only moves coordinates DOWN when `v ≥ 0`).  The
membership lemma replacing `inBoxR_of_inBoxZ`/`memBox_of_inBoxR`:

    theorem inTube_memBox : InTube v T rad z → MemBox (tubeBox c.z0 v T rad c.r0) z
      -- from zhatV_inBoxR (|ẑ − z0| ≤ r0) and |z_i − ẑ_i| = |−t v_i + w_i|, t ∈ [0,T]

and `seg_memBox` (already in `RigidExpr.lean`) puts the whole segment `[ẑ, z]` in the box
(the box is convex and contains both endpoints), which is all `Wfun_taylor` and `mvt_box`
need.  Every enclosure lemma of `RigidBasin.lean` (`mem_omegaGrad`, `mem_omegaHess`,
`mem_pinJ`, `mem_Mrow_pin`, `abs_W_le_eps0`, `sum_abs_grad_le_epsW`, `abs_pin_le_gmax`,
`loaded_row_nonneg`) is stated for an arbitrary `Array IV` box and is reused verbatim with
`b := tubeBox …` (Hessian, β, validity) or `radBox c.z0 c.r0` (ε₀, ε_w, g_max — the point
quantities, as A79 already does).

## 3. The Taylor remainder (the one genuinely new inequality)

`a36_basin` bounds `|Σ_ij Whess η i j d_i d_j| ≤ 2 H̄ x²` with `H̄ = ½ Σ_ij mag(H_ij)`.
The tube writes `d = −t•v + w` and bounds the four pieces separately:

    d^T H d = t² (v^T H v) − t (v^T H) · w − t w · (H v) + w^T H w

    |d^T H d| ≤ t² q_vv + t Σ_b |(v^T H)_b| |w_b| + t Σ_a |(H v)_a| |w_a| + Σ_ab |H_ab| |w_a| |w_b|

with the checker quantities (all over the tube box):

    q_vv    = mag (Σ_ab v_a v_b H_ab)          -- interval SUM first, then magnitude
    HvCol b = mag (Σ_a v_a H_ab),  HvRow a = mag (Σ_b H_ab v_b)
    Hmag ab = mag H_ab

No symmetry of the interval Hessian is assumed (column and row sums are both computed); the
pure-algebra identity is `ring`, the enclosures are `mem_omegaHess` + `mem_mag`, and
`Finset.abs_sum_le_sum_abs` as in `hhessterm`.  The reason the tube is cheap is visible
here: wall and edge rows are LINEAR in the centre coordinates and in `s`, so
`H_ab = 0` whenever both `a, b` are centre/s coordinates except for the two dist rows —
`q_vv` is ~0.02 (scale) or exactly 0 (slot), i.e. the ray is a straight line for every
contact row.  The per-coordinate bounds fed in are

    t ≤ tb x := min T (x + rS)                         -- from |w_s| ≤ rS, d_s = −t + w_s
    |w_i| ≤ wb x i := min (rad i) (x + tb x * |v_i|)   -- from w = d + t v
    x := ‖d‖_∞  (dist d 0 as in a36_basin)

and `E x := ε₀ + ε_w x + ½ (tb x)² q_vv + (tb x) Σ_i ½(HvCol i + HvRow i) (wb x i)
          + ½ Σ_ab Hmag ab (wb x a) (wb x b)`.
Lemma to state: `hT1_tube : Wfun c a z − E x ≤ sZ z − sZ ẑ` (replaces `hT1`).

## 4. Validity of the loaded rows: nothing changes, and why (the compression lemma's role)

`loaded_row_nonneg` needs, on the tube box: walls/dists globally (`wall_valid`,
`dist_valid` — need only `SmallTilt`), edge rows via `edge_valid` with the [V] margins
(tangential `< 1/2`, depth `> −1/2`) checked by `loadedValidOK` on the tube box.  The tube
certificate loads the same universal rows as `G3_UNIVERSAL`; the checker verifies the
margins on the (much larger) tube box, and they hold up to `T ≈ 4·10⁻²` (binding row
`E4c1-7e2`, the same row that bounds A36's isotropic reach — see the doc §3).  The
COMPRESSION LEMMA (doc §2: every loaded row has `γ_k = ∇g_k(ẑ)·v ≥ 0`, `Σ ω_k γ_k = 1 ± ε_w`,
and the rows go strictly negative along the ray) is NOT load-bearing for `tube_basin`: it
is what guarantees that no contact BREAKS along the ray, hence that the branch-free row set
stays valid and no L1 disjunction is needed, and it is the canary (`ẑ − T v` violates a wall
row, so the ray is never a packing).  Formalising it is optional: `γ_k` is an
`evalIV`/`gradDense` enclosure at the point box, and the identity `Σ ω γ = (Aᵀω)·v = e_s·v + ρ·v`
is `sum_abs_grad_le_epsW` applied to `v`.

## 5. The dichotomy: `quad_pin` is replaced by a monotone-iteration lemma

`E` above is monotone non-decreasing in `x` but NOT a convex quadratic (piecewise, through
the `min`s), so `quad_pin` does not apply.  Case 2 still yields `x ≤ ψ x` with
`ψ x := (κ_eff E x + κ g_max)/(1 − β)` (`hxbound` unchanged: β is `betaA36` on the tube box).
The replacement is trivial:

    theorem iter_pin {ψ : ℝ → ℝ} (hmono : Monotone ψ) {x X : ℝ} (hx : x ≤ ψ x) (hX : x ≤ X) :
        ∀ n, x ≤ ψ^[n] X            -- induction: x ≤ ψ x ≤ ψ (ψ^[n] X)

plus `rup_mono` (the checker's upward-rounded iterate dominates the true one, by
monotonicity of `ψ` and `x ≤ rup x`), and the checker's exit condition
`x_n + r0 ≤ r_N` hands over to `a22_optimal'` exactly as `hzN` does now.  `X := X_max =
max_i (T |v_i| + rad i + 2 r0)` bounds `‖d‖_∞` on the tube (`inTube_dist_le`).  Monotonicity
of `E`: every coefficient is ≥ 0 and `tb`, `wb` are non-decreasing in `x` (`min` of
non-decreasing functions).  Note the iteration does not need `ψ(X_max) < X_max`
explicitly; if it fails the iterate never drops below `r_N` and the checker rejects.

## 6. The consumer-facing statement (TopLevel-side, for D.SLAB)

The `basin` theorem of `Rigidity.lean` is `t`-frame with the slab gate
`rBasin(1+√2) < 3689/10⁶`.  Its tube analogue is a statement about packings at sides
`m ∈ [ŝ − T, ŝ]` (doc §4, Lemma SEAM): with `t := ŝ − m` and the `slot` direction,

    theorem basin_tube (hm : ŝ − T ≤ m) (hm' : m ≤ ŝ) (hP : CfgPacking m P)
        (hnear : ∀ i, |c_i(P) − (ẑ_i − t v_i)| ≤ rC ∧ |t_i(P) − t̂_i| ≤ rT_t) :
        m = ŝ ∧ P = ẑ

(the `m < ŝ` case is refuted, since `z := (P, m)` is a feasible point of the tube with
`z_s = m < ŝ`).  The θ↔t transfer for the tilt radius is `ThetaT.lean`'s
`theta_lipschitz` (`|Δθ| ≤ 2|Δt|`) globally, or the sharp local factor `2/(1+t_lo²) ≤ 1.771`
on `t ∈ [0.36, 0.37]` for A60's landing boxes; centres and `s` transfer with factor 1.  No
s-slab gate is needed: the side `m` is a coordinate of the tube point (`w_s = 0`).

## 7. Obligation list (in order)

1. `tubeBox`, `InTube`, `inTube_memBox`, `inTube_dist_le`  (box parametrisation).
2. `hT1_tube` (the split remainder bound, §3) — new lemma, pure algebra + existing enclosures.
3. `iter_pin`, `rup_mono` (§5) and the checker's `iterOK` (`Nat.iterate` of the rounded map,
   exit at `x_n + r0 ≤ r_N`).
4. `checkTube` = `checkA36` with the box swapped and `pinningOK` replaced by `iterOK`; the
   [C]/[CANARY] checks may be carried as `Bool` fields without soundness content.
5. `tube_basin` = `a36_basin` with steps 1–3 substituted; `basin_tube` (§6) as the
   D.SLAB-facing corollary.  Data modules: generate from `certs/tube_*.json` with the
   `gen_rigidity_lean.py` pattern (ω is `G3_UNIVERSAL`'s, so `RigidData36.lean` already has it).
Estimated size: ~400 lines on top of A79's files; no new analysis (no Clairaut, no convexity).
