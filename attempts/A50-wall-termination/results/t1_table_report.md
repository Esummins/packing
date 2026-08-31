# A50 T1 — span-semigroup tilt-exclusion table (compute report)

Spec: `notes/span_semigroup.md` (Theorem S2/S3, variants V1/V2/E1, canaries C1–C4).
Code: `code/span_table.py` (table), `code/canary_span.py` (C1–C4),
`code/checker_span.py` (independent checker + corruption gate).
Data: `results/span_table.json`, `results/canaries_a50.json`, `logs/checker_gate.log`.

All certified entries are exact: `fractions.Fraction`, or an integer-coefficient
quadratic + root index + a rational enclosure of width < 1e-15 obtained by
exact-sign bisection.  Floats appear only in `_float*` fields (readability).

Constants: `s0 = 969271/250000`, `lo = 191/50`.  Parametrisation `t = tan(phi/2)`,
`cos = (1-t^2)/(1+t^2)`, `sin = 2t/(1+t^2)`; domain `phi in (0,45]`, i.e.
`t in (0, sqrt2-1]`, right end = root #1 of `t^2 + 2t - 1`.
Boundary of `f_{abc} = a cos + b sin + c = w`: `(c-w-a) t^2 + 2 b t + (a+c-w) = 0`.

Index sets (Theorem S2): **|A(6)| = 172** (spec value, asserted), |A(8)| = 375;
421 multisets at L<=6, 1236 at L<=8.

## 1. Equal-class MONOTONE table, column L <= 6

Excluded = for EVERY (a,b,c) in A(6), f_{abc}(phi) lies outside [lo, s0].
All eight gaps are open intervals; their endpoints are admitted points (some f
equals lo or s0 there exactly).  "(a,b,c)@w" = the boundary whose root the
endpoint is.

| # | excluded phi (deg) | width | lo endpoint (exact) | hi endpoint (exact) |
|---|---|---|---|---|
| 1 | (0.000, 1.735) | 1.735 | t = 0 (domain end) | root1 `1969271t^2+2000000t-30729` = (4,-4,0)@s0 = **theta\*** |
| 2 | (4.949, 5.857) | 0.907 | root1 `191t^2+200t-9` = (2,-2,2)@lo | root1 `1969271t^2+500000t-30729` = (4,-1,0)@s0 |
| 3 | (8.953, 9.777) | 0.823 | root1 `191t^2+100t-9` = (2,-1,2)@lo | root0 `241t^2-500t+41` = (2,5,1)@lo |
| 4 | (10.712, 11.749) | 1.037 | root0 `1719271t^2-2500000t+219271` = (3,5,0)@s0 | root1 `2219271t^2+2500000t-280729` = (5,-5,0)@s0 |
| 5 | (13.973, 14.075) | 0.103 | root0 `1719271t^2-2000000t+219271` = (3,4,0)@s0 | root1 `2219271t^2+2000000t-280729` = (5,-4,0)@s0 |
| 6 | (26.232, 26.935) | 0.703 | root1 `291t^2+400t-109` = (4,-4,2)@lo | root1 `719271t^2+1000000t-280729` = (2,-2,3)@s0 |
| 7 | (36.620, 37.208) | 0.588 | root1 `391t^2+200t-109` = (5,-2,1)@lo | root0 `241t^2-500t+141` = (1,5,0)@lo |
| 8 | (40.254, 40.341) | 0.087 | root0 `969271t^2-3000000t+969271` = (0,6,0)@s0 | root1 `719271t^2+500000t-280729` = (2,-1,3)@s0 |

Excluded measure **5.982138 deg** of (0,45]; admitted 39.017862 deg (86.7%).
This reproduces the lead's float recon to <= 1e-3 deg on every endpoint.

## 2. Equal-class MONOTONE table, column L <= 8 (robustness)

Eight gaps again, all subsets of / adjacent to the L<=6 gaps; total excluded
**5.426659 deg** (admitted 39.573341).

| # | excluded phi (deg) | lo endpoint | hi endpoint |
|---|---|---|---|
| 1 | (0.000, 1.735) | t = 0 | root1 `1969271t^2+2000000t-30729` = (4,-4,0)@s0 |
| 2 | (4.949, 5.857) | root1 `191t^2+200t-9` = (2,-2,2)@lo | root1 `1969271t^2+500000t-30729` = (4,-1,0)@s0 |
| 3 | (8.953, 9.439) | root1 `191t^2+100t-9` = (2,-1,2)@lo | root0 `41t^2-500t+41` = (0,5,3)@lo |
| 4 | (10.712, 11.749) | root0 `1719271t^2-2500000t+219271` = (3,5,0)@s0 | root1 `2219271t^2+2500000t-280729` = (5,-5,0)@s0 |
| 5 | (14.009, 14.075) | root0 `1469271t^2-4000000t+469271` = (2,8,0)@s0 | root1 `2219271t^2+2000000t-280729` = (5,-4,0)@s0 |
| 6 | (26.232, 26.935) | root1 `291t^2+400t-109` = (4,-4,2)@lo | root1 `719271t^2+1000000t-280729` = (2,-2,3)@s0 |
| 7 | (36.719, 37.208) | root1 `391t^2+500t-209` = (6,-5,2)@lo | root0 `241t^2-500t+141` = (1,5,0)@lo |
| 8 | (40.254, 40.257) | root0 `969271t^2-3000000t+969271` = (0,6,0)@s0 | root1 `1719271t^2+1500000t-780729` = (5,-3,2)@s0 |

Only gaps 3, 5, 7, 8 shrink when the length cap is relaxed to 8; gaps 1, 2, 4, 6
are cap-independent in [6,8].

## 3. NEAR-FLUSH exclusion (V1 window class), exact

theta\* = root #1 of the primitive quadratic **1969271 t^2 + 2000000 t - 30729**
(= `(4+s0)t^2 + 8t - (4-s0)` cleared), i.e. 4(cos - sin) = s0.
Enclosure `t* in [128043594488893/8457954541961216, 256087188977787/16915909083922432]`,
**theta\* = 1.7346504143603858 deg** (float, readability).

Verified EXACTLY at `v` = the rational lower end of that enclosure (`v < theta*`,
`4(cos v - sin v) > s0`): for the window class [0, v] EVERY multiset's reachable
span interval `[sum of per-step minima, sum of per-step maxima]` misses [lo, s0].

| audit | multisets | max < lo | min > s0 | hits window |
|---|---|---|---|---|
| L <= 6 | 421 | 134 | 287 | **0** |
| L <= 8 | 1236 | 204 | 1032 | **0** |
| L <= 6, E1 m=1 mixed link | 226 | 54 | 172 | **0** |
| L <= 6, E1 m=2 mixed links | 105 | 14 | 91 | **0** |

Binding families (exact, at `v`): tightest from below is (n2,n3) = (3,3),
max span 3.180249626 < lo; tightest from above is n4 = 4, min span
4(cos v - sin v) = s0 + O(1e-16) > s0 — i.e. **theta\* is the sharp threshold**,
and gap #1 of the L<=6 table ends exactly at theta\* (its hi endpoint is the
(4,-4,0)@s0 boundary root).  The near-flush exclusion survives E1 (m = 1, 2).

## 4. V1 sliding-window sweep (window class, monotone, L <= 6)

u steps by 1/4 deg over (0,45]; window [u, u+w] clipped at 45; grid marks are
exact rationals whose float degree is within 1e-6 of the mark.

| w (deg) | windows | EXCLUDED | excluded windows (deg) |
|---|---|---|---|
| 1/2 | 179 | 7 | [0.25,0.75] [0.5,1.0] [0.75,1.25] [1.0,1.5] [10.75,11.25] [11.0,11.5] [26.25,26.75] |
| 1 | 179 | 2 | [0.25,1.25] [0.5,1.5] |
| 2 | 179 | 0 | — |

Window classes wider than ~1 deg are never excluded away from the near-flush
region: the exclusion is a statement about narrow tilt profiles.

## 5. V2 SIGNED variant (H-MONO dropped, equal class, L <= 6)

721 signed triples.  Admitted **41.253294 of 45 deg (91.7%)**; excluded 3.747 deg
in five gaps: (0, 1.166), (5.164, 5.657), (10.952, 11.749), (26.232, 26.935),
(36.620, 37.208).  Honest reading: dropping monotonicity costs 2.23 deg of
exclusion (5.98 -> 3.75) but does NOT collapse the table — two gaps (#6, #7)
survive verbatim, and a near-flush gap survives in shrunken form (0, 1.166).

## 6. E1 MIXED-NORMAL extension (equal class, monotone, L <= 6 incl. mixed slots)

m = 1: 108 triples; m = 2: 60 triples.  Admitted set for m = 1, for m = 2, and for
the union over m in {0,1,2} is **exactly [theta\*, 45]** (43.265350 deg): a single
mixed-normal link dissolves every interior gap, and the ONLY surviving exclusion
is the near-flush one, whose boundary is again theta\*.  Sharpness statement: the
interior gaps are artefacts of full x-pinning (P-chain rigidity); the near-flush
gap is not.

## 7. Canaries (`results/canaries_a50.json`) — 4/4 PASS

* **C1** (phi = 45, exact Q[sqrt2]): hitting set is exactly
  {(0,4,1),(1,3,1),(2,2,1),(3,1,1),(4,0,1),(5,-1,1)} = {a+b=4, c=1} (6 triples),
  span 2 sqrt2 + 1; membership proved by exact squaring: 8 - (lo-1)^2 = 119/2500 > 0
  and (s0-1)^2 - 8 = 17350771441/62500000000 > 0.  A47 Corollary T1a reproduced,
  with the non-thin splittings included as predicted.
* **C2** (Trump spines, machinery canary): x-spine 0-1-8-2 and y-spine 2-8-7-9-5,
  ledger residual `(c_last - c_first) - (s0 - h(phi_first) - h(phi_last))` =
  **-5287/50000000000 ~ -1.0574e-7** for both spines (identical because both spines
  run between the same two class-0 corner squares' coordinates), well inside the
  1/100000 bound.  Both spines carry flush links, so the exclusion table claims
  nothing about them; only the ledger arithmetic is being tested.
* **C3** (the margin): theta_T = 2 atan(194075/530594) = 40.181937290 deg;
  cos theta_T = 243864887211/319195098461; **191/50 - 5 cos theta_T =
  42003301/15959754923050 ~ +2.6318e-6**, so 5 cos theta_T < lo strictly (the
  (5,0,0) chain misses the window).  BUT theta_T is **ADMITTED** in the L<=6
  table: the unique hitting triple is (0,6,0) (six sin-steps, f = 6 sin theta_T).
  theta_T sits in the admitted interval (37.208, 40.254) deg, 0.072 deg below the
  nearest exclusion gap (40.254, 40.341).
* **C4** (theta\* enclosure): 4(cos - sin) > s0 at the rational below theta\* and
  < s0 at the rational above (exact); the V1 audit covers all 421 (resp. 1236)
  multisets, not just the binding families.

## 8. Checker + corruption gate (`logs/checker_gate.log`) — GATE PASS

`code/checker_span.py` re-verifies `span_table.json` from the JSON alone with a
separate algebra path (own index-set enumeration by realisability search, own
Cauchy-bracket root isolation, own surd order, own Q[sqrt2] evaluation at 45 deg).
It reconstructs the labelled decomposition of (0,45] independently — the root set
of all boundary quadratics cuts the domain into cells of constant hit-set; every
interior breakpoint is an admitted point (f = lo or s0 there); each open cell is
labelled by exact evaluation at a rational witness — and requires the JSON's
intervals to match run-for-run (endpoints as algebraic objects, closure flags,
labels, per-triple exclusion sides, no boundary root inside any excluded
interval).  It also re-verifies the near-flush audits and every V1 sweep row.

| corruption | detected by |
|---|---|
| 1. exclusion endpoint enclosure widened by 1e-9 | enclosure width 2.0e-9 not < 1e-15 |
| 2. triple #100 deleted from A(6) | \|A(6)\| != 172 / index-set mismatch |
| 3. sign flip of a stored quadratic coefficient B | enclosure does not bracket a root |
| 4. s0 numerator off by one | constant s0 differs from 969271/250000 |
| 5. an excluded interval relabelled admitted | label mismatch at 10.712 deg |

PRISTINE: PASS (16 intervals L<=6, 16 intervals L<=8); 5/5 corruptions detected.
Runtime: table 2 s, canaries < 1 s, checker + gate 3 s.

## 9. Scope, caveats, deviations from the brief

* The table is a NECESSARY-condition sieve (spec section 5): excluded class =>
  no equal-class flush-free wall-to-wall P-chain at any live s; admission
  constructs nothing.
* Hypotheses carried: H-MONO (column 1/2), H-L6CAP (L<=6 primary, L<=8 robustness
  column), P-chain rigidity (E1 measures the cost of relaxing it), H-OPP inside E1.
* **Deviation**: the task prompt's sanity figure theta\* ~ 1.7457 deg is wrong;
  the exact root is **1.7346504 deg** (lead confirmed mid-run and corrected the
  spec).  Nothing else in the prompt's expected landscape changed — all eight
  recon intervals reproduce.
* **Honest report on V2**: admission is high (91.7%) but NOT near-total; five
  gaps survive dropping H-MONO.
* Checker scope: the L<=6 / L<=8 columns, the near-flush audits and the V1 sweep
  are fully re-verified and corruption-gated.  The V2 and E1 blocks are
  report-only union measures (their admitted intervals are exact, but the checker
  does not re-derive them); their load-bearing claim — E1 near-flush survival —
  IS gated, via the mixed-link audits.
* Degenerate class-0 steps (dx = 0) and non-P (mixed-normal beyond m=2, L>=9,
  multi-class beyond the window variant) branches remain outside the table, as
  the spec states.
