# A66 — corners4 + pair certificates: findings (Fable lead, 2026-09-01/02)

Labels: [T] proved, [M] measured/computed exact, [F] float pilot evidence, [C] open.

## T1 — corners4 direct integral infeasibility: the counting route is REFUTED [T+M]

`docs/proofs/corners4_empty.md`. Lemmas E1 (centre relaxation: pairwise >= 1, pin clearance
>= 1/2, wall bands), E2 (centre region = two width-(s-3) bands + four inner-corner slivers),
E3 (diagonal-translation embedding C(s) into C(s')). EXACT 7-point witnesses: at s = 191/50
(denominator 1000; min pairwise d^2 = 1.06177, min pin clearance d^2 = 0.265613) and a
structured tight one at s0 (3 centres along one channel column at spacing (s0-1)/2 = 1.4385,
two pin-edge points (3/2, 1), (3/2, s0-1), two wall midpoints). By E3 the relaxation is
feasible at EVERY s in [3.82, s0]: the candidate counting proof cannot close anywhere in the
window. Rigidity exhibit: the s0 witness does not lift (wall and pin-edge positions force
theta = 0 exactly; axis pairs need L_inf >= 1 but the witness has L_inf = s0-3 = 0.877084) —
the obstruction is orientation coupling, invisible to occupancy measures; with A65's
fractional wall (tau(0) = 7.2545 > 7) corners4 emptiness is beyond ALL single-square
machinery. corners4 NOT deleted; C.K4TIER unchanged. Residue routes priced: (a) pair
certificate at beta = 0 (Corollary P0; pilot OPEN, below), (b) conditioned mini-tree over the
rigidity case split (tens of branches), (c) contact/FJ.

## T2 — pair certificates: designed, spec'd, soundness proved [T]; verifier built; pilots [F]

* `docs/proofs/pair_kill.md`: Lemma P (pair kill via Delta_lambda bridge: closed disjointness
  for atom additivity, slack-core ownership, box widening eps_box >= 3(lambda-1); stuckness
  input = CC-2' 2-crowds per unclipped box and NOTHING else); Corollary P0 (beta = 0
  emptiness, stuckness-free); death-witness criterion; CANARY THEOREM (dilated Trump
  saturates trump5's pair threshold C(6,2)+6 beta exactly — no pair certificate whose shell
  reaches s-hat can kill trump5); A34 non-applicability (pricing dual over realised pairs,
  no marginal gluing; rows carry container + pins; threshold couples all pairs through
  whole-family disjointness); Lemma P-B (PI's basin-exclusion discount: sound for EXACT
  strata only — a monotone reading would bind Trump, who contains k4_08's pins — and only in
  a ~5e-4 shell below s-hat because the pins' own slot drift and the sqrt2-weighted zone
  drift must fit inside the 3/2000 basin radius).
* `docs/specs/pair_certificate_v1.md`: clean-room normative spec; eleven ambiguities from
  the build folded in (unsound sqrt2 bound 181/128 replaced by 19601/13860 + exact t* bracket,
  body-frame sign pinned, g-floor, possibly-meets thresholds, depth/split/counter semantics,
  deficit definition, coincident-atom warning, report keys, mandatory selftest + reference
  sha256, pricing-pipeline cell-representative note).
* `code/verify_pair.py` (sha256 d9b7a24a...662d): pure-Fraction 6-D B&B, selftest 0/15000
  violations (it caught an unsound-PASS interval bug during build); toy PASS at s = 199/100
  (W2 = 0 < 1: "two unit squares need side 2" as a genuine pair-certificate PASS, 29.8 s at
  depth 40) and falsifier FAIL at s = 201/100 with exact confirmed witnesses (SAT gap 27/12800).
  NEW trusted code, NOT in the TCB.

## Pilot results [F] (restricted pair-LP, dual side; value = lower bound on any certificate W2)

Adequacy criterion (introduced after a false "15"): the catalog's SINGLE fractional packing
must reproduce the A65 value. Every catalog audited for exact containment
(`results/containment_audit.json`); all cited cells converged at fine Lmax = 1.000000.

* k4_08 (N = 7, m = 7, threshold 21 + 7 beta; tau_f_cat = 7.000000 exact): restricted
  tau_2(beta) = 21 + 6 beta EXACTLY at beta in {0, 1/4, 1} — integral optimum = the crowdfam
  ghost family (Sigma m2 = 6, I = 13; best exact contained family in every support has
  Sigma m2 = 6; a claimed Sigma m2 = 7 family was RETRACTED: two members were outside the
  container). Margin -beta with ZERO fractional excess on the restricted instance: **the
  boosted pair kill for k4_08 is LIVE at restricted strength** — first protected-class
  pricing object below its threshold. Emptiness (beta = 0) dead (product witness certifies
  tau_2(0) >= 21).
* k4_08 basin discount (beta = 1): gamma 0 / 0.1 / 0.3 -> margins -1.000 / -1.400 / +0.531,
  ghost fraction 1.00 / 0.70 / 0.10. Real but modest (~4 gamma near 0, then a convex dodge to
  out-of-zone variants at 3e-3 that keep the value); usable window 0 < gamma <~ 0.245,
  optimum ~0.1 (+0.4). Reserve, not lever.
* corners4 (N = 7, m = 8; tau_f_cat = 7.084 vs A65 7.2545): beta = 0 bracket
  tau_2(0) in [14.89, 21.32] (certified product witness; unconverged cutting-plane upper end,
  trend 22.20 -> 21.53 -> 21.32) — STRADDLES 21: OPEN. Binder = simplex time (17k x 10k LP),
  not the formulation. Emission NOT attempted (condition not met).
* Universality of the k4 tie: crowdfam floors are one pair-incidence short at every critical
  class (k4_08, k4_11: 6/7; k4_03: 4/5) and 2-3 short at subcritical ones (k3_02, k3_05,
  k1_00: 2; k0_00: 3); every death-witness family is a Trump image — the same
  Trump-saturation mechanism, one level up from H10-I.

## Verdicts

T1: NO-GO for the counting proof (exact witnesses); corners4 stays. T2: design + soundness
+ verifier DONE; pilot says the pair formalism is NOT the ninth face — k4_08's stuck kill is
kill-shaped at restricted strength (margin beta) and corners4's emptiness is undecided —
but no certificate was emitted/verified: the full-quantifier question (emission oracle loop
against verify_pair.py with a first-order LP solver) is the successor.

## Canary ledger

1. T1: point-set statements; Trump not in corners4 (TL clear). SAFE.
2. Lemma P/P0/P-B: canary theorem proves trump5 unkillable by the formalism; P-B's proof
   reaches z = g.z-hat and contradicts only the exact-k4 skeleton hypothesis. SAFE by theorem.
3. Pilots: dual-side measurements on k4_08/k4_13 strata; the k4_08 control reproduces his
   image family's value 21 + 6 beta. SAFE.
