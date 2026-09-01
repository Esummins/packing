# A56 verification log

## V1 (T1, Fable) — census stability on the CLOSED window [191/50, s0]
A53 L2(iv) endpoint predicates re-checked at s = 191/50 and s = 969271/250000 by hand
(soundness.md P0): s not integer; frac in (3/4,1) (41/50, 219271/250000); s < 4; cross-family
conflict set {2,3} unchanged (41/50 < 1, 9/50 < 1, 91/50 > 1). Census constant on all of W. PASS.

## V2 (T1, Fable) — library inventory
results/library_inventory.json: 52 PASS certificates (A53 certs_wip: 32 k=6 + 18 k=5; A54:
k6_23, k5_13 — these supersede A53's non-PASS files of the same name). All nofams empty. Max
atom coordinate over the whole library = 1776997/500000 = 3.553994 < 3.82 (atoms admissible on
all of W under any anchor beta in [0,1]). Thinnest margins: k5_02 +0.00055 (total-margin,
s-free), k6_23@A54 +0.0146, k5_13@A54 +0.0374, k5_15/k5_10 +0.077, k6_27 +0.079, k6_20 +0.107.

## V3 (T1, Fable) — M1 single-corner transfer tags
anchor test on name_to_slots: exactly 4 of 52 classes are single-corner — k5_00, k5_01, k6_00,
k6_01. These transfer to every s <= s0 by M1 (soundness.md P2) with NO computation: identity
embedding of [0,s]^2 into [0,s0]^2 flush at the anchor corner; kill hypotheses are
containment-priced (A53 L5), so the s0 certificate applies verbatim. 48 multi-corner classes
(31 k=6, 17 k=5) go to the parametric verifier.

## V4 (T1, Fable) — refutation of the general monotone-transfer routes
Recorded in soundness.md P2/M2: rigid embedding impossible (four-corner anchoring); corner-wise
translation reduces to a contact-graph feasibility system that monotone fields solve only for
axis-separated pairs — tilted contacts allow (Delta v).u >= -2*delta violations, and the
slot-arithmetic exclusion (4 - s < 1) blocks only DIRECT pin-square-pin squeezes, not tilted
chains (the A46/A48 bridge geometry, present in Trump's packing). tau*-monotonicity: constraint
families at different s are incomparable (moving exemption zones); no inclusion argument; A54 S0
forbids measured refutation via tau_LP. Verdict: conjecture, unproved, NOT used by A56.

## V5 (T2, Opus) — parametric verifier gates, first pass (2026-09-01)
verify_param.py imports the A53 integer core UNMODIFIED (imul4/trig_int/box_trig/vacuous_int/
clip_int/core_exempt_frac...); the only new exact predicates are point-to-interval widenings
(atom_inside_int_iv, core_exempt_frac_iv). Gates: selftest 1500 random boxes clean (interval
predicates vs pointwise Fraction evaluation at samples); degenerate run [s0,s0] reproduces
verify_case.py stat-for-stat; C2 cross-checks (old verifier at s = 191/50, midpoint, s0 per
PASS) 63/63 PASS. First-pass scoreboard: 4 M1 + 21 TRANSFERRED = 25/52 closed over the whole
window; 26 OPEN + 1 TIMEOUT (k6_04), ALL open rows depth-limited undecided with ZERO holes;
stage 0: all 48 multi-corner certs PASS at the far endpoint s = 191/50 (gap anchoring). Cost
law and corrections banked in soundness.md P6. Cumulative verifier time 8916 s.

## V6 (T2, Opus) — completion pass: the depth route refuted, k6_23 sub-window closed
Depth lifting converted 0/5 (k6_32, k5_19 at depth 56 AND 60, k5_20 at 60 — all TIMEOUT at
600–900 s; implied blowups ≥ 33×–1300×): the "+8 depth ≈ 2.5×" law was an artifact of
witness-cap aborts (soundness.md P6 (iii)). The budget went to k6_23 instead: depth-56 PASS on
the sub-window [191/50, 3877/1000] (2888 s, full C2) — the hardest certificate now covers all
but the width-8.4e-5 sliver below s0, and A54's fixed-s certificate covers s = s0 itself; open
= the OPEN interval (3877/1000, 969271/250000). Scoreboard after pass: 26/52 (25 full + 1
partial), still zero holes.

## V7 (T2, Opus) — repair recipes validated and priced, then the final sweep
Sub-window bisection: 2/8 successes (k6_23 as above; k6_07 PASS on [191/50, 956767/250000],
173 s) — works only when the witness set is complete (soundness.md P6 (iv), artifact 2).
Re-solve-with-margin: VALIDATED 3/4 on the sample (k6_08 12 s, k6_28 97 s, k6_32 677 s;
k5_02 infeasible at eps_geo = 0.003 — τ hit the budget exactly), with the lever identified as
eps_geo row-shrink, weight scale inert, and witness feedback measured INERT in the sample (the
witness glob matched 0 files — fixed in resolve_margin.py; the conversions are eps_geo alone).
Final mechanical sweep over the remaining rows: 13/21 converted (13/16 above the eps_geo ≥
0.0015 threshold, 0/5 below — the budget-slack rule budget − τ0 ≥ ~0.5, soundness.md P6 (v));
every conversion re-verified by the 4D verifier at depth 48 over the whole window + full C2
against the unmodified A53 verify_case.py. Certificate substitution per the P7 ledger rule
(advisor ruling), both certs kept with provenance in every substituted row.

## V8 — closure (2026-09-01)
Final scoreboard (results/scoreboard.json): 52 rows = 38 FULL-WINDOW (4 M1 + 21 original-cert
parametric + 13 re-solved-cert parametric; k6 27/33, k5 11/19) + 2 PARTIAL (k6_23 open only on
(3877/1000, s0), width 8.4e-5; k6_07 certified [191/50, 956767/250000] and at s0, open on
(956767/250000, s0), width 0.050016) + 12 s0-ONLY (k5_02/03/05/10/12/13/14/17,
k6_20/21/27/29 — their original s0 kills stand untouched). ZERO coverage holes in any A56 run.
Cumulative verifier time 34584 s ≈ 9.6 h. Canaries: C1 endpoint identity by construction +
re-verified; C2 63/63 first pass and per-row thereafter (old verifier, independent code path);
C3 window predicates (V1); C4 trump5/k5_11/k5_16 never touched; C5 A29 untouched, ≤ 3 heavy
processes throughout (A55 concurrent).
