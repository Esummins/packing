# A42 verification log (Fable lead, 2026-08-28)

Every exact claim in the A42 report traces to an entry here. Arbiter throughout: verify_case.py
(exact rationals) for certificates; Fraction arithmetic for geometry.

## V1 — Lemma N1 hypothesis (H1), exact (T1)
`code/n1_check.py` (Fraction over exact float values), run 2026-08-28, exit 0:
- min pairwise centre distance^2 of the 11 Trump e-frame placements = 1 EXACTLY (sharp;
  consistent with Lemma N1.0's bound ||c-c'|| >= 1);
- 11 footprints R_j = clip(p_j +- 0.06, [1/2, s0-1/2]^2) pairwise disjoint, min sup-gap
  = 34675803100911181/56294995342131200 ~ 0.615966;
- max footprint diam^2 = 18/625 = 0.0288 < 1 (diam ~ 0.16971).
Covers every sweep radius r' <= 0.06 (shrinking only helps). Lemma: docs/proofs/occupancy_collapse.md.

## V2 — chain (T2): zero kills; artifacts checked by the lead
results/chain.json inspected directly (lead, 2026-08-28): k=1..10 all converged=True,
minmass=1.0, tau integer-exact (11-k for k<=5, 12-k for k>=6; max deviation 3.2e-11) — true LP
optima, no certificates possible (auto_scale correctly refuses at tau >= budget). Control
cond_k rows (target nofam removed) match chain tau to <=1.2e-12 — F3. Union variant converged
tau 10.000 (A38 probe-A slack was a relaxation artifact). Pipeline validated end-to-end by the
cw_root re-run: certified total 206/25 < 11, standalone verify_case PASS depth 39, 1.1 s
(results/spotverify.json).

## V3 — sweep (T3): budget-1 vacuity; the 11 free assignment certificates
results/sweep.json inspected directly (lead): 111 records, every tightening node alive(LP)
with tau = 1.000000 exactly (F1); liveness scan shows collision-based emptiness unreachable at
any core quality; dying radius = R_j itself; second-pass gain = 0 (ball 6: tau 1.0 both under
others-at-0.06 and others-at-0.03). POSITIVE: 11/11 occupancy/assignment certificates PASS by
verifier-only emptiness (measure total 1e-6), 0.9-8.6 s each, 38.1 s total — F5. Complement
cover soundness assert ran inside sweep42.py per node.

## V4 — tighten probe (T2 addendum)
results/tighten_probe.json: k=2 target shrink rho'=0.045, 0.03, ...: tau = 9.000000000032
unchanged, alive(LP), converged — F6. No certificate exists at any (k, rho') in the
0.06-family.

## V5 — zone-size probe (zoneprobe42): volume scaling refuted
results/zoneprobe.json inspected directly (lead): P1 (k=0, w=0.35, budget 11) tau =
10.999999999996 (= 11 to 4e-12), 29 cert attempts, ALL FAIL — the best certificate fails on
COVERAGE (14 holes), not value; P3 w=0.25: tau 10.929 unconverged and rising, 24 attempts;
w=0.15: tau 11.087, 5 attempts; P2 (k=1, w=0.35 core): the core consumes 1.0 of budget and
buys 0.145 of tau — net -0.855, strongly alive. Headroom does NOT scale with exempted volume
(w=0.35 zone has ~34x a ball's volume and zero headroom); the central-window root remains the
unique certifying member of the occupancy family. N1 (H1) for w=0.35 zones: diag^2 = 0.98 < 1,
min pairwise gap 0.035966 (pair 3-6) — checked by the lead in float arithmetic on the exact
placement values (adequate for interpreting a NEGATIVE probe; would need the n1_check exact
form only if this design point were ever used affirmatively).
