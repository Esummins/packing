---
name: geometry-before-lp
description: "PI directive (2026-09-09): on k0 nodes, force geometry to a fixed point before any LP; geometry cost pays off massively in LP-tree size"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8b20e315-017a-445b-9327-302e5359887a
  modified: 2026-09-09T17:56:48.642Z
---

On k0 (and any multi-box) nodes, run EVERY geometric forcing to a fixed point before any LP, and use the LP
only as a leaf where the geometry runs out. Forcing order: per-piece K' + container clip to the fixed point
(A171/A172), lonely clip (A169 Theorem B, A173), piece-level coexistence cuts (D vs S; B1 vs a partner from
the (left, floor) cell only), all four corners at once (not "left corners last"), partner cores as pins,
chord rows / lanes re-emitted from the grown cores; then exact-core LP.

**Why:** the PI's reading of the cascade (2026-09-09): "doing more of this forcing geometry before LP is going
to be necessary to getting it to complete in a reasonable amount of time... it cuts down on the LP tree enough
that it pays off massively on the backend." Evidence: D step killed 54/82 cover boxes by geometry; lonely rule
71/309 alive nodes in one pass at zero LP cost; per-piece K' cut surviving poses of H and D by ~20% more;
LP side costs ~0.7 CPU-h per ALIVE kill (A149).

**How to apply:** every cascade / case-tree brief states the forcing order above and forbids LP at a node
whose geometry has not reached a fixed point; clips propagate (a clipped box's K' must be rebuilt from the
PIECES so it grows on the far side and clips neighbours harder — see [[square-packing-n11-lab]]); figures
emitted per step as results land. Related: [[feedback-priority-order]], [[present-problems-spatially]].
