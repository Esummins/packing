# A33 running notes (theory lead: Fable advisor)

2026-08-26/27. Companion files: lemma.md (formal statements), grain_theory.md (T3 framework +
measured P2), records_wastage.txt, t1/ t2/ t3b/ (compute), docs/literature.md section F (T3a).

## T1 verdict (the gate) — MEASURED, verified

eta(s) = tau*(s) - 11, A07 double-cutting-plane rebuilt in t1/run_s.py, every LP solve
a-posteriori verified against independently rebuilt matrices. Float table (t1/results/eta_table.json):

| s        | tau_LP    | eta_float | exact frac-pack LB | certified feasible eta |
|----------|-----------|-----------|--------------------|------------------------|
| 3.84     | 11.045665 | 0.0457    | 0.0040             | (T2 sealing)           |
| 3.85     | 11.092788 | 0.0928    | 0.0527             | 0.448864 (PASS)        |
| 3.86     | 11.147532 | 0.1475    | 0.1138             | —                      |
| 3.87     | 11.197056 | 0.1971    | 0.1379             | —                      |
| 3.877084 | 11.242867 | 0.2429    | 0.1931             | 0.425400 (PASS, re-verified by lead: 6,154,892 boxes, identical tree) |

- eta(s) is ~linear on [3.84, s'], slope ~5.3 per unit s. Honest bracket at s' = 3.877084:
  eta in [0.193, 0.425], best estimate 0.24-0.40 (row oracle under-reports deficits by 1.4-2.9%
  via ~1-deg-wide moving sub-grid pockets; no tangency witnesses, so not the Goebel mode —
  eta_float is optimistic by that much; the sealed certificates are immune, being exact B&B).
- Forcing power at s': every square of any 11-packing at side < 3.877084 covers guard mass in
  [1, 1.4254] certified ([1, ~1.24] float-optimal), escape <= 0.4254 certified. Moderate.
- Forcing power at 3.84: eta_float 0.0457 — every square covers in [1, ~1.05], escape <= ~0.05.
  STRONG pinning; feeds the paused A29 tree as a new global constraint family (tight-sum cuts,
  grain_theory.md section 5).
- rho(11) at s' (forcing efficiency, grain_theory section 3): eta/(s'^2-11) = 0.2429/4.0318 =
  0.0602 float / 0.1055 certified — the LP sees ~94% of the geometric wastage. For comparison
  rho(10) = 0 exactly at s(10). The n-trend is T3b's measurement.

## By-product (lead, 2026-08-27): s(12) >= 3.877084, certified

The sealed T1 cert has exact total 11.4254 < 12 and certified coverage >= 1 everywhere, so by
Theorem 1 with n = 12: s(12) >= 3.877084 (lemma.md Corollary A33.4). Previous recorded bound:
3.7889 (Stromquist 2003 + monotonicity). +0.088 improvement, machine-checked today, Lean-portable
with the existing checkMeasureI infrastructure (same certificate format as the 3.80/3.82 certs).
T3b is locating the ceiling (tau* crossing 12) — extrapolated slope puts it near or above s = 4,
the conjectured s(12); but tau* must steepen near s = 4 (16-square grid at s = 4 forces
tau*(4) >= 16), so the crossing location is genuinely informative about how far the pure measure
method can push s(12).

## T3a (literature) — landed, docs/literature.md section F

W(x) = O(x^{3/5}) current UB, but Chung-Graham 2020's proof is FLAWED (Arslanov-Bui erratum, W5
term); correct proofs only Bui arXiv:2508.04603 and McClenagan arXiv:2602.01484 (2025-26). LB
still Roth-Vaughan Omega(x^{1/2}); 1/2-vs-3/5 fully open ($1000 bounty). NO LP/fractional/SDP
treatment of wastage asymptotics exists — eta(n) is virgin territory. Bui arXiv:2504.09489:
W = Theta(W*) with all tilts <= 1e-10 — near-upright grains asymptotically optimal up to
constants = rigorous one-sided crystallization, supports P3 (see grain_theory.md section 2).

## P2 measured from records (lead, in-context)

Peak envelope of c_n = W_n/(4 s_n) FLAT at 0.267-0.273 across n in [5,100]; c(m^2) = 0,
W(m^2-1) = 1 exactly, W(m^2+1) ~ 1.1 m. Records through n = 100 are Trump-like bicrystals
(bulk grid + one tilted grain); E-G sublinear regime not yet visible. grain_theory.md 5b.

## T2 verdict (maps, t2/results/summary.json) — landed 2026-08-27

- SINGLE-SQUARE PINNING IS WEAK at s'. Float-optimal fields exclude 48% of the admissible
  placement volume (thr 1+0.243); the sealed certified field (thr 1+0.425) excludes only 18%.
  The surviving set is ONE giant component (99.9% of surviving volume): wall bands survive at
  99.2%, interior at 78%, mid-tilt t-deciles dip to ~0.71. No thin sheets, no isolated islands.
  Localized exceptions exist (slice cx=0.9645 on the wall-mid line: only 3.5% of t survives).
- MULTI-FIELD STACKING FAILS (Lemma A33.3 empirically dead at s'): 6-field intersection = 50.2%
  of admissible vs best single 52.6% — 4.6% relative gain; independence would have predicted 7%
  absolute. Explanation (lead): complementary slackness — every near-optimal field is tight on
  the support of the near-unique optimal fractional packing, so all tight varieties share that
  core; field diversity cannot remove it. A33.3 is not wrong, it is toothless among NEAR-OPTIMAL
  fields; deliberately SUBOPTIMAL fields with disjoint tight sets would each have larger eta —
  the trade goes the wrong way.
- THE WIN — JOINT SUBFAMILY CONSTRAINTS (Lemma A33.1(i), k=2): of random disjoint pairs drawn
  from T x T, 51.5% violate cov(x)+cov(y) <= 2+eta (mean pair sum 2.4389 vs threshold 2.4254,
  max 2.787). The pigeonhole's bite is in k-subset joint rows, not single-square pinning.
  Usable form: "tight-sum cuts" as case-tree side constraints (grain_theory.md section 5).
- Canary PASS: all 11 lambda-scaled Trump placements survive every map with coverages in bounds.
- 3.84 certificate (t2/certs/A33_measure_feasible_3.84.json, PASS): eta_cert = 0.37756128 at a
  3% seal scale — NOT the ~1% hoped, because T1's 3.84 LP field is genuinely ~1.5% infeasible on
  closed squares (depth-64 witness, unscaled mass 0.98490; the row oracle's sub-grid pockets).
  Verifier-in-the-loop refinement (t2/refine_384.py): CAUTION — the loop's per-iteration
  "eta_cert ~ 0.046" printouts are NOT full verifications; the lead's independent depth-50 runs
  FAIL (28 -> 7 exact holes across iterations at scale 1; holes persist even at scale 1.01, i.e.
  real ~1% pockets remain and MOVE between cuts — the same phenomenon T1's oracle showed).
  A deepened run (depth-50 harvest, 800 witnesses, prior-witness preload, 5 iterations, then seal
  probes at scales 1..1.03) is in flight; the honest certified value at 3.84 as of now is
  eta_cert = 0.37756128 (the 3% seal, PASS). Same oracle caveat applies to the 3.85 (0.4489) and
  s' (0.4254) seals: their certified etas carry ~0.18-0.36 of margin cost that the same
  refinement could reclaim (recorded as gap).

## T3b verdict (t3b/results/eta_n_table.json, eta_n_meta.json) — landed 2026-08-27

- **GRAIN CONJECTURE REFUTED in the measured range n <= 26.** eta(n) at record sides:
  0 / 0 / 0 / ~0 / 0.243 / ~0 / 1.275 / 1.568 at n = 4, 5, 9, 10, 11, 16, 18, 26.
  rho(n): 0 (n=5), 0 (n=10), 0.060 (n=11), 0.242 (n=18, unconverged; rigorous dual bracket
  rho(18) >= 0.115 — already conclusively above rho(11) <= 0.060), 0.280 (n=26, unconverged).
  eta and rho RISE with n; n = 11 is the method's BEST non-trivial case, not its worst.
  Caveats carried: n=18/26 unconverged (bracketed), n=41/66 not run, all values at RECORD sides
  (the operationally relevant side — the method must bite at the target side).
- Crystal dips are TOTAL: eta(m^2) = 0 exactly (tau_eps(m) = m^2; near-uniform measure feasible).
  Free corollary: rho(n) = 1 whenever n's record side is a crystal side (n = 2,3; 6,7,8; 12..15) —
  the plain LP is maximally uninformative exactly there.
- Clean characterization for the writeup: **eta(n) = 0 iff the measure/LP method alone settles
  s(n)** — eta IS the method's failure margin at the record side; it is 0 exactly at the two
  proven-optimal swept n (5, 10) and at crystals.
- Calibration anchors PASS: tau*(3.7071) = 10.000000000003 (row violation 1e-13).
- Two corrections to grain_theory.md folded in (P1 paragraph): tau_eps(m) = m^2 (my
  lattice-vertex argument only killed the naive atomic field), and the closed-square tau* is
  degenerate at commensurate sides (remark (d) tangency); all etas use eps-shrunk tau, which is
  safe for every pigeonhole statement.
- **NEW CERTIFIED THEOREM: s(12) >= 39/10 = 3.90** (t3b/certs/A33_s12_3.90_v2.json, exact total
  184752/15625 = 11.8241 < 12, closed-square coverage PASS; independently re-verified by the
  lead, 3,258,450 boxes, 75 s). Beats the published s(12) >= 3.7889 by +0.111. tau* = 12
  crossing located at ~3.951-3.967 = 98.8-99.2% of the n=12 record side 4.0 — n = 12 may be
  nearly closable by the LP + case-tree family; flagged as a candidate future campaign.

## 3.84 refinement endgame (lead, 2026-08-27) — CLOSED at eta_cert = 0.3229

Eight verifier-in-the-loop iterations total (t2/refine_384.py, depth-50 harvests, witness
preload): eta_float(3.84) settles at 0.0463 (the original 0.0457 was oracle-optimistic by ~1.3%,
confirming T1's anomaly quantitatively). Full-depth sealing kept failing on real ~1% pockets that
MOVE between cuts; after it4 the last blocker is a SINGLE tangency/near-hole cluster at
(cx, cy, t) ~ (1.2132, 1.4645, 0.43798) (theta ~ 47.2 deg, float interior mass ~1.012 under
scale 1.02) that resists certification between scales 1.020 and 1.025 and is jitter-robust.
Sealed artifact: **t2/certs/A33_measure_feasible_3.84_v2.json, exact total 113229249/10^7 =
11.3229249, eta_cert(3.84) = 0.3229249, standalone PASS at depth 58** (improves the 3% seal's
0.3776; the remaining 0.277 of margin cost is dominated by that one cluster — a targeted
row+jitter iteration there is the documented route to eta_cert ~ 0.06-0.08, left as gap).
By Corollary A33.4 this certificate also independently re-proves s(12) >= 3.84 (superseded by
the 3.90 result).

## Status: COMPLETE. All four tasks landed; final report delivered to the PI.
