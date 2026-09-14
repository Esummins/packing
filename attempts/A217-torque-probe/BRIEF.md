# A217 -- THE TORQUE PROBE on k0 witnesses (PI, 2026-09-14 17:40). Fable. LAUNCH-AND-EXIT (numerics detached; write-up
from disk when they land -- if that needs a second session, leave a resume block and EXIT rather than wait).

PI: "We have the teleport lemma and the two meeter lemma, and the fact that both meeters have to be pinned to prevent
them from exiting the box they're meeting, there's something knocking around in my brain about torque being an
invariant that prevents all four corners from being pinned like that?"  Goal: find out, by computation on real k0
configurations, whether a SIGNED equilibrium condition at unsettled corners obstructs all four corners being unsettled
at once -- i.e. whether "every optimal packing has a settled corner" has a torque proof for all n.

Ops: short responses, files <= 250 lines, no monitors, no waiting turns; 1-2 processes, BLAS pinned, BelowNormal via
A210's fix, PYTHONDONTWRITEBYTECODE=1; explicit-pathspec commits; never touch the running workers or the k0 cascade.
Read first: docs/proofs/drain_flow_k0.md and drain_lemma.md (the FJ / Fritz-John formulation NLP(S), the stress
network, DF-K0), docs/proofs/fj_census_k0.md and attempts/A88-fj-census (census, a88lib: contact structures and
multiplier solving), attempts/A44-fj-maxwell (Maxwell counting, eval_atlas), docs/proofs/corner_seal.md (SEAL/WEDGE:
the chirality of a corner meeter), docs/proofs/forced_corners.md (Theorem FC), docs/proofs/descent.md (Lemma CH corner
hurt), docs/proofs/k0_route.md sections 3-4 (K0-FREE / K0-BLOCKED / teleport), attempts/A37-cp-atlas (37 local optima
z_c with radii -- which are k0?), attempts/A163-s02-other-frames (refusing witnesses), attempts/A168-cascade-fable
results (l1_104 LP supports: NOT packings).

## The probe
1. WITNESSES: build a set of jammed k0 configurations numerically: (a) every A37 atlas entry / A163 witness whose four
   corner cells are each unsettled (no axis-aligned square filling the corner cell); (b) NEW local optima from a
   nonlinear side-minimisation of 11 unit squares (tan-half parametrisation, exact interior-disjointness as smooth
   constraints, SLSQP / IPOPT-style or the lab's own optimiser if one exists) started from many random k0
   configurations and from k5-class configurations with the corners perturbed, KEEPING the constraint that no corner
   is settled (both corner-adjacent squares tilted or offset), to local optimality (KKT residual < 1e-8).  Record
   side, contacts, tilts.  Aim for >= 30 distinct k0 local optima (D4-quotiented); report the sides found vs s-hat.
2. STRESS: at each witness solve the Fritz-John multipliers on the active contacts (a88lib / A44) -- a nonnegative
   force network in equilibrium; for each corner, compute the wall forces on its meeters, the torque each meeter
   receives from the walls about its centre, its chirality (CW / CCW per corner_seal.md), and the torque it receives
   from its holders; also the global quantities: total wall torque about the container centre (must be 0 -- check),
   the per-wall pressure moments, and the sum over corners of the signed corner torques.
3. INVARIANT HUNT: tabulate, over all witnesses, the signed corner quantities and look for a relation that (i) holds
   at every witness with a settled corner (the known optimal families: Trump images, the n = 5, 10, 13 optima if
   easy) and (ii) FAILS at every all-four-unsettled witness -- e.g. a sign rule "an unsettled corner's meeters
   receive net wall torque of sign chi(corner) and the D4-corrected sum over corners must vanish", or a parity /
   winding count along the chain of holders around the boundary.  State every candidate as an inequality or
   identity, test it, report which survive.  If a candidate survives on all witnesses, write it as Lemma TORQUE
   (conjecture, any n) with the proof route (force balance on each meeter + the wall geometry) and what is missing;
   if none survives, say so with the counterexample witness drawn.
4. Pages: docs/residue_map/campaigns/A217-torque/torque217_<witness>.svg (the packing with contact forces drawn as
   arrows, corner torques annotated, the stress network) and a summary table page; results/witnesses217.jsonl,
   results/torque217.md; notes/torque.md (the setting, the candidates, the verdict, the PI credited); registry row,
   LOG entry.  Report once (witness count and sides, the candidate invariants and their fate, the drawn
   counterexample or the conjecture) and EXIT.

## PI's remark (17:45) -- what the invariant should and should not forbid
"I think it's actually consistent with trump and higher n having non-simple middle grains, since the space those
grains occupy are non-convex."  Read: an interior tilted square (Trump's middle grains, and the tilted grains of the
best-known packings at higher n) sits in a NON-CONVEX pocket formed by its neighbours, so it can be held on all sides
and its wall-free torque balance closes without any sign constraint; a CORNER meeter sits in a CONVEX region bounded by
two walls, so its holders can only act from the interior side and the sign of the torque it can receive is
constrained.  The candidate invariant must therefore be a statement about wall-bounded (convex) positions only --
test that the interior grains of Trump and of the atlas optima carry no such constraint, and that the constraint
appears exactly at the corners (and possibly along the walls: a square touching one wall is a half-constrained case
worth tabulating too).
