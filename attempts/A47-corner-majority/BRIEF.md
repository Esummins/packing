# A47 — flush-free kill via corner primitives + majority composition (Fable lead)

Goal: docs/ideas.md I-L18-expanded (read first). Close the flush-free branch of flush-mandatory by
the PI's majority route with magnitude-scale primitives. Three legs:

(a) THIN BRANCH: run A46's designed rectangle lemmas (attempts/A46-balanced-wedge/results/
a46_report.md gap G3 + notes/w1_theory.md W1.6 — the [45,0,0,45] minimal structure and its finite
residue). Exact certification. If they pass: flush-free THIN critical structures are dead at s0,
a standalone theorem.

(b) I-L18 PRIMITIVES: certify multi-square/corner-region charges in exact Fractions via the A23
oracle: (i) tilted-or-corner-touching square in a container-corner zone (A23-4b's 0.34-0.61 —
recertify at s0 over the A21 corner-zone box with the wall-flush case EXCLUDED by hypothesis, bins
by tilt); (ii) wall-region variants (tilted square near mid-wall, from A23's tables, region-
disjoint per A25/A46 clip_util); (iii) assess pair-in-corner if cheap. Ownership: region-level
disjointness (corner regions are pairwise far; corner vs wall-wedge overlap handled by A46's
adjacent-wall deduction).

(c) MAJORITY COMPOSITION (yours): for a flush-free critical structure at s0 — A21 THM1 gives a
corner-zone square (cite; verify its hypothesis covers s0 <= 3.88); flush-freeness forbids
wall-flush => primitive (i) fires; L6/L7 give wall contacts => WC wedge charges (A46 w_WC table);
interior contacts => CE/CC wedges + the PI's majority counting (how many interiors CAN be
small-angle given the graph structure — use the torque toolkit W1.1-W1.4 and the bridge mechanism's
requirements to bound the small-angle population honestly, or charge them at the small bins and let
the majority carry). Target: sum > 4.0318 for every flush-free non-thin candidate profile. Report
the honest margin or the named shortfall; if it clears, flush-mandatory composes (thin from (a),
non-thin from (c)) — then measure the census factor via A43-H1.

Canaries: Trump + atlas at their own s (all have flush — must be UNTOUCHED by the composition,
verify vacuity); the A46 fire-zone bookkeeping conventions. Constraints: <= 4 heavy processes, ONE
long-poll waiter per background run, exact certification the arbiter, checkpoints, A29 untouched.
Registry, LOG, PI-readable report with the gap list.
