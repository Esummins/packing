# A40 lead verification log (Fable)

## Theory verification (in-context, pre-run)
- S1 pointwise [V]: proved from scratch (corner strictly interior to owner forces interior
  overlap through any neighbourhood of a corner of p); matches A37 amendment A1, now with a
  written proof rather than a rule.
- S2 over-estimate: re-proof one line (owner support along own edge normal exact).  Same as
  A36 L1.1.
- S5 anchor chain re-derived by hand twice (once when the cut ledger was single-cut, once for
  the multi-cut + signed-diagonal form).  Sign conventions checked on the face cut
  (c(z-hat) = -h_in exact) and both tie-cut sides (anchor side -tau, cost side +tau; the two
  closed sides cover).
- S5' emptiness: checked that no e_s constraint is needed and that loaded cuts must be
  EXCLUDED from the upper bound (sup of a cut over the box is positive); the implementation
  loads rows only.  Verified in code review of empty_lp/certify_empty.
- S7 floors: trivially sound (interval lower bound); the value premium is the whole cost.
- Signed-diagonal Hessian refinement: upper bound of d^T H d needs off-diagonal magnitudes
  and positive parts of diagonals only.  Checked against the naive triangle bound on the
  binding branch (10.63 -> 8.04, 24 %): the accumulated-interval + signed form is what both
  producer and checker compute.

## Measurement verification
- M1 per-row [V]-margins cross-checked against A36's aggregate margin (min over rows at
  h = 3.779e-3: A36 reported 0.005809; A40's per-row bisection puts the first row death at
  h_V = 0.00522 (row 16), consistent (0.5 - |t| margins decrease ~4.0/unit h).
- M4 growth-rate LP: the face anchor rate for sq6.t- (0.0518) equals min_r omega_r/|Y_r|
  intuition from A36's kappa_eff = 19.3 (1/19.3 = 0.0518) -- two independent derivations of
  the same number; noted as a satisfying consistency check.

## Producer/checker independence
- a40_check.py: no producer libs (mpmath.iv + fractions + stdlib only); jets transcribed from
  a36_check.py (A35 lineage); rows rebuilt from the constraint dicts stored in each
  certificate; kills, [V]/safe/forced/branch/floor claims, margins, ring chain, and the
  per-face covering split tree re-verified from scratch.
- Corruption gates: omega-sign, h-big, drop-anchor, floor-raise, drop-sibling (coverage).

## Final-run verification
- Store census (lead): 2930 certificates in ring_00..ring_06 = 2564 anchors + 42 wall-empty
  + 324 leaf-empty; loaded-row validity modes: wall 31469, V 20103, branch 14532, aux 2698,
  floor 1149, relfloor 14, forced 9; 16 certificates carry a tie cut; min anchor margin over
  the whole store 2.43e-07 > 0.
- Hand verification (lead) of ring_00/sq6_t-.json: omega_b = 47638489687/920169064943 =
  0.051771, gain omega_b*h_in = 1.9155e-4; V0_sup 3.7e-60, eps_w*h_out ~ 4e-18, Hbar =
  8.0360, quad = 8.0360*(0.0045315)^2 = 1.6501e-4; margin = 2.654e-5 = the claimed value;
  cut ledger -1762624118419/9201690649430000 = -omega_b*h_in exactly.  PASS.
- The chain tiles [37/10000, 5794/884563]: ring h_in/h_out continuity is part of the
  standalone checker ([CHAIN]); coverage trees re-verified per (ring, face) ([COV]).
- Independent Opus verification run (results/check_report.json): a40_check.py standalone
  re-checker over the full store: 2930 certificates, 168,774 checks, 0 failures (reproduced
  twice).  Corruption gates: omega-sign, h-big, drop-anchor, floor-raise, drop-sibling --
  all 5 FAIL as required.  VERDICT: PASS.
