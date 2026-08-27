# A36 lead verification log (Fable)

## Pre-dispatch analysis (lead, in-context)
- L1 over-estimate principle proved (one line: owner support along its own edge normal =
  n.c_o + 1/2 exactly; any corner row >= axis gap). Float sanity of the disjunction premises:
  killed-axis overlap margins ~1.01, centre orders exactly 1.0, support identity residual 0.
- L1 branch structure designed: 2+2+4 branches, 16 variants, basis v3 = +2 rows.
- L2 posed as h-bisection with inner LP over the multiplier polytope + pin-basis search.

## Subagent run (2026-08-27) — VERIFIED
- code/a36_check.py run independently by the lead: 17 certificates, 339 checks, ALL PASS
  (per-variant h = 3.779e-3, psi/h = 0.9979, x* = 6.11e-58; UNIVERSAL branch-free 3.689e-3;
  min A22 tangential margin 0.005809; min L1 kill margin 0.98862; alpha-form comparison line
  psi/h = 40.5 confirms the max-form is load-bearing).
- Corruption gates spot-run by the lead: drop-branch (x* = inf, FAIL as required) and h-big
  (tangential -0.110, beta = 3.59, FAIL as required); agent reports 5/5 gates fail.
- Attribution accepted as honest: the decisive lever was the max-form pinning (x11.4), not L1
  (x1.024) — the branch-free UNIVERSAL certificate at 7.38 x r_N is the minimal trust-chain
  form; the 16-variant family squeezes +2.4% and makes the branch machinery falsifiable.
- Quoted radius decision (lead): headline theorem at h = 3.7e-3 (psi/h = 0.9607 re-derived;
  also implied by the h* certificate + monotonicity of the quadratic term), certified maximum
  3.779e-3. Rationale: h* sits 0.2% from its own cliff (gap A36-c).
- Deviations accepted: omega denominators 1e45 on pin rows (deliberate, A36-b); pin basis =
  A22's own S and Y (4.8% radius declined for trust-chain hygiene, A36-d).

## Consolidated A35+A36 gap list (final)
1. G1 ridge handoff: the theorem is local (box, inf-norm); nothing at s0 = s-hat absorbs the
   collar; basin-boundary certification still blocked by the semantic cliff R* ~ 0.006.
2. h_L1_max = 5.22e-3: next reach ceiling = A22's old-row tangential margins (h_valid); beyond
   it the 36-row description itself must be re-selected.
3. Binding constant kappa_eff*Hbar*h/(1-beta): further reach needs Hessian-mass rebalancing or
   a sharper pin (4.8% local-search head-room recorded, declined).
4. {35}/thin-certificate and M1b-erratum objects persist in A35 but are off the critical path
   (the (V') barrier is stratum-blind).
5. L1 relies on separating-axis completeness (as D3' does) — cited, not re-proved.
6. [NUM] layers (LP counts, kernels) remain uncertified; nothing load-bearing rests on them.
7. Global wall unchanged (A31/A32 1e30 structures; LP ceiling 3.83): A35/A36 remove the
   per-critical-point cost only.
