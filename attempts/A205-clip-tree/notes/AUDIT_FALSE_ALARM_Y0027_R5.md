# Audit false alarm (coordinator, 2026-09-11 01:10): Y0027 / g1 / leaf R.5

audit_batch.sh reported R.5 "REFUTED" by exhibiting ONE admissible square G meeting BL(1,0) disjoint from H, F1 and
the pins.  The leaf's kill is FC with "anonymous cap 1 by CN (union diameter 0.9955 < 1)": it claims BL(1,0) has at
most ONE anonymous meeter (and H misses, no role reaches), so ONE exhibited meeter is not a refutation -- a refutation
needs TWO disjoint admissible meeters of BL(1,0) coexisting with some H and F1 pose.  audit205.py's criterion is right
only for cap-0 kills (R.1 here) and must require two meeters for cap 1.

Coordinator's two-meeter sample (scratch/y0027_r5_twomeeters.py): 6,000 admissible meeters of BL(1,0); 3,242 disjoint
meeter PAIRS ignoring H / F1; 0 of them coexist with any of 50 H poses in R.5's box and any of the 10 admissible F1
poses.  => the kill stands on the sample; Y0027 g1 DEAD is NOT withdrawn.  Successor: fix audit205.py (two meeters
for cap 1; the pair must also respect the roles), re-run the audits, and keep the leaf labels as they are.
