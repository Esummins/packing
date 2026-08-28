# A38 extrapolation frame (fixed BEFORE the data lands — Fable)

Anchor at 3.84 (A24/A27, same cover, same LP): level-1 216 nodes, final state 117 certified dead
/ 20 alive(LP) / rest undecided-at-limit; tau quartiles 9.00 / 9.00 / 9.56, max 10.25, budget 10;
median node cost 655 s (l1_summary snapshot: 65 dead at moderate limits). Refinement anchor: the
3 A24-live boxes closed at depth 2 (16/16 children) except one needing depth 3 (5/8 at depth 2);
measured remaining cost to close 3.84: ~340 CPU-h over ~1200 nodes.

## Quantities the pilot must produce

Per depth d in {1,2,3} and weapon w in {W1-node, W5, W1-marginal, W2-marginal}:
  k_d(w) = kills attributable to w; f_d = total kill fraction among nodes processed at depth d;
  b_d = 8 * (1 - f_d) = effective branching of survivors; cost_d = median node wall seconds;
  stall_d = count of alive(LP) nodes all of whose children are alive(LP) with zero W1/W2 drops.
Census at depth 3: n_trump (Trump-consistent survivors), n_atlas (other-attractor-consistent),
n_unexplained; distances to nearest atlas placement sets.
Seam: b2 = surviving children of the second-square occupancy branch at a near-Trump leaf;
occupancy-LP verdict (does tau < budget fire at all at leaf scale).

## The bracket

Witness-coordinate closure depth: D_w = depth at which the witness box fits atlas scale
(0.05241 / 2^(D_w-1) <= 3.7e-3 => D_w ~ 5; theta similar). Survivor count at depth D_w:
  optimistic: N_1 * prod_{d<=3} (8(1-f_d)) * (8(1-f_3))^(D_w-3), with f beyond 3 held at f_3
    (justified only if f_d is non-decreasing in d in the measured range — check);
  pessimistic: same with f_d replaced by its lower binomial 95% CI and undecided counted alive.
Full-configuration cost per surviving witness leaf (the S1 cascade): squares 2..11 each need
occupancy + cover at ~b2 branching to atlas scale => multiply by b2^10 (optimistic: b_eff drops
with each added core because budget tightens by 1 and W2 thresholds tighten — measure the 2-core
b vs 1-core b and use the RATIO to schedule the decay; pessimistic: b2 constant).
Node cost: cost_d trend (W1 should shrink LPs; deeper = smaller boxes = fewer rows... but higher
tau; measure).
Desktop-days = total nodes x median cost / (6 workers x 86400 s).

## GO/NO-GO criteria (pre-registered)

GO requires ALL of:
 (1) f_d reaches > 7/8 by depth 3 (b_eff < 1), or survivors demonstrably localize to atlas
     neighbourhoods with count shrinking in absolute terms;
 (2) zero structural stalls (stall_d = 0), or every stall is atlas-consistent (dischargeable by
     K2/K3 at depth);
 (3) the seam probe fires (second-square occupancy kills at leaf scale) with b2 <= ~24, and the
     2-core branching shows decay vs 1-core;
 (4) the composed bracket's PESSIMISTIC end <= ~1000 desktop-days and optimistic end <= ~100.
NO-GO names the assassin = the first criterion violated, quantified (e.g. "b_eff = 2.3 at depth 3
and flat", "stalled cells at wall-distance X with no weapon", "b2 = 200: the S1 cascade is the
wall", "median node cost 40 min at depth 3 => bracket floor 10^4 desktop-days").

## Honesty rules

Undecided-at-limit counts as survivor everywhere. Sampled depths get binomial CIs and the frame
carries them through. eta_float (1.243) columns are [NUM] and never enter the GO bracket — they
bound what A33's G5 seal-tightening could buy. Kill matrix distinguishes kill(LP) from
kill(certified); the GO verdict must state the certification debt explicitly.
