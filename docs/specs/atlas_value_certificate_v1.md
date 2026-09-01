# atlas-value-certificate-v1 (A37 3R / 3S) — frozen spec (A62, checklist C2)

**Verifier:** `attempts/A37-cp-atlas/code/a37_check.py` (719 lines, sha256 `f3f48cfe…`),
standalone: imports only `mpmath.iv + fractions + json + math + glob + os + sys`; uses **no
producer library**. The order-2 interval jets and row language are transcribed (with
attribution) from A36's `a36_check.py`, which transcribes A35's `m2_check_inflation.py`.
**Index:** `attempts/A37-cp-atlas/results/atlas_final.json` (36 catalogue entries + the
A51-NEW-0 extension); per-family certificates `results/certs/fam*_3R.json` / `fam*_3S.json`.
**Status:** written from behaviour + code at commit `c9980bf` (2026-09-01) by A62.

**Role in the composition (H11 note):** the atlas is presently **off the critical path** of
the live A53–A60 proof plan — only Trump's own basin certificate (A22/A36 lineage, see
`rigidity_krawczyk_certificate_v1.md`) is composed. Atlas entries serve as the map of the
critical-point landscape and as canaries. This spec freezes them because fam00 (Trump, 3R)
is the same certificate class as A36's composed theorem, produced by the generic pipeline.

## 1. The mathematical claim a PASS establishes

For an entry with centre configuration `z_center` (the 33 configuration coordinates + the
side coordinate; **orientations are raw angles θ, not t** — see coordinate caveat below),
box radius `h` (∞-norm) and value `V`:

> every **feasible** packing configuration z (11 unit squares, pairwise disjoint interiors,
> normalised container) with ‖z − z_center‖_∞ ≤ h has enclosing side σ(z) ≥ V,

with V ≥ 3.877084 for every entry except Trump's own (fam00), whose claim is the A22/A36
statement σ ≥ ŝ with equality iff ẑ. The claim is **stratum-blind**: no assumption about
which contacts are active, both Fritz-John branches covered (max-form pinning).

* **Mode 3R (hard):** rational multiplier vector ω over the rebuilt row set; the checker
  re-derives the barrier quantities and verifies the value inequality V ≤ v_lo − x* with
  second-order control Hbar·h²-type terms (claims: `W0, r_res, eps_0, eps_w, g_max, kappa,
  kappa_eff, beta, Hbar, psi, v_lo, v_hi, x_star, wd, wt`).
* **Mode 3S (soft):** no exact pin basis; per-variant tables (`variants`, `branched` pairs
  with no [V]-safe row are branched over live axes) with `V_max ≤ V_target` on `h_table`;
  used for valleys/rattler cores and for pure trivial-Lipschitz boxes (e.g. A51-NEW-0).

## 2. Certificate fields

Common: `family_id`, `catalogue_index`, `class` (RIGID / VALLEY / …), `mode` ("3R"/"3S"),
`z_center` (rational strings), `contact_table` (the ONLY structural input the checker
trusts — everything else is re-derived), `claim_text`, `active_tol`, `s_min_float`
(informational), `claims{…}` as above.
3R adds: `P` (pin basis), `Y` (dual data), `omega_rational`, `h`, `r_N`.
3S adds: `variants[]`, `branched[]`, `h_table`, `h_probe`, `kill_margin`, `s_center`.

## 3. What the checker verifies (normative check list)

From the contact table alone it: **[R]** rebuilds every row and compares with the implied
row order; **[C]** re-verifies every row ACTIVE at z_center; **[S]** recomputes each
separation row's [V]-safety flag from the tangential coordinate (an endpoint row marked
"safe" fails); **[B]** recomputes branch structure — for every pair with a non-[V]-safe row
it re-runs the kill test on box(z_center, h_probe) and requires the certificate's live-axis
set to contain every axis it cannot kill, with the full product of live axes enumerated;
**[O]** sign discipline on ω; **[W]/[G]/[H]/[V]** recompute W0, the residual
‖A(z_center)ᵀω − e_s‖₁, the Hessian bound Hbar(h), and every loaded row's tangential/depth
margins over box(h); then the final value inequality. All interval arithmetic is
`mpmath.iv` outward-rounded, with `nextafter` guards on every float conversion.

**Trust base:** `mpmath.iv` (cited third-party; same trust item as the A22/A36 chain —
checklist F6). Corruption gates (ω-sign, h-big, drop-branch, value-inflate, drop-aux where
applicable) must FAIL; the A37/A51 runs record them.

## 4. Settings that MUST appear in a PASS record (C7)

`active_tol`, `h` (3R) or `h_table`/`h_probe` (3S), dps of the interval context, and the
per-check PASS counts. The lab records these in the attempt's `final_report.json`; a bare
"PASS" without the box radius and tolerance is not citable.

## 5. Coordinate caveat (findings F5)

Atlas boxes, like the A22/A36 boxes they generalise, live in (c, θ) coordinates while every
case/parametric certificate and the formal statement (`TopLevel.lean`) use (c, t),
t = tan(θ/2). dθ/dt = 2/(1+t²) ≠ 1: radii do not transfer verbatim between the two systems.
Any composition that hands a (c,t)-box to an atlas entry must convert with outward rounding
— or the certificates must be re-emitted in t (A28's recommendation).
