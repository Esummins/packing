# A43 lead verification log (Fable)

Independent checks performed by the lead (not by the compute workers):

1. Reference constants derived independently before dispatch and matched against worker output:
   span(F-F) = s0-1 = 2.877084 > 2 sqrt2 = 2.8284271 (k=3 F-F death; H2 unit check U3);
   span(C-C) floor = s0 - sqrt2 = 2.46287044 (U5/U6); per-wall along-wall gap
   sqrt(1-(sqrt2/2-1/2)^2) = 0.97831834, 3 gaps = 2.93495503 > s0-1 (H1 N1 hand-check matches to
   all printed digits); h(theta*) = 0.70460817; k=3 C-C per-step floor 1.04866 forcing FL-link
   tilt into [2.86, 87.14] deg (consistent with H2's k=3 window forcing [12,78]/[18,72] after
   coupling).
2. Trump spine structure extracted independently (check_trump.py + edge list): x-axis shortest
   chains k = 4 (e.g. 0-1-8-2), y-axis k = 5 (e.g. 2-8-7-9-5), shared squares {2, 8} — matches
   H2 canary counts (14 x-chains, 16 y-chains) and the double-spine sharing claim in the report.
3. H1 artifacts read directly: regression.json = EXACT MATCH at every k; b_trump_canary 20/20
   PASS with exact rationals (max coverage 1.137624852 vs thr 1.402957280); R12 = R11 at every k
   (N5/N6 inert) consistent with the mask-window m_low = 0 finding; k11 join fits recomputed
   ratios spot-checked (all-wall fractions 0.7/0.4656/0.2417/0.0956/0.0314 decay ~exp(-0.78k)).
4. H2 artifacts read directly: ablation tables per checkpoint; kill_audit.json = 0 witnesses over
   48 killed types (independent second implementation); canary_trump / canary_a37 = 30 + 163
   chains, 0 failures; unit checks U1-U7 pass, U2 reproduces a realized Trump CE step inside the
   certified branch union.
5. Provenance rulings made by the lead and enforced: flush-mandatory CONDITIONAL (ledger SOFT +
   A32-H1); N2/N3 existential (k=11 join only); N7 approx (canary-confirmed over-kill: Trump's
   graph contains a 4-cycle); A25 pair atlas excluded at s0; A39 resealed field required a
   present standalone PASS report before use (it was).
6. Formalization (spine definition, span identity, FL/CE/CC dx enclosures, crossing lemma sketch
   for the double-spine assessment) authored and re-derived by the lead; the CE degeneracy
   arguments (|th_d - psi| = 45 => flush; phi_a = phi_b => flush) checked by hand.
