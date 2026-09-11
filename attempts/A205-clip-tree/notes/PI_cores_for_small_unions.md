# PI reading (2026-09-10 20:50): "shouldn't any of the yellow boxes with a diameter lower than 1 automatically get a
# clip core once the clip stage starts, and then all of them should cascade the clips against each other until stable?"

Status: a slot union of diameter < 1 has cap 1 (Lemma CN), so its anonymous meeter is INSTANTIATED as a role carried
as pieces and A204's fixed point clips every role against every other role's polygon K', rebuilt from the survivors
after every pass (Y0147 died so at round 2).  The closed-form core of a region of diameter d is the disc of radius
(1-d)/2 about its centre, and as an obstacle it gives exactly Lemma CN's bound (1 - d/2 from the region's centre):
nothing beyond stage 0; the gain is the exact polygon core, which is bigger than the disc.

For A205: (1) in every branch the chosen option row is a small region -> instantiate with its K' and run the cascade
to the fixed point BEFORE the count (the PI's "yellow box gets a core"); (2) PAIR-CORE lemma to state and prove before
use: two interior-disjoint unit squares with centres in a region U of diameter D in [1, 2) ... their union contains
the intersection over all admissible placements of the pair (a fixed central patch of U when D is small); use only
with a written proof and an exact computation of the patch; (3) cascade all instantiated cores against each other
until stable at every node, page after the fixed point.
