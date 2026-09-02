# A68 — Lean wave 3: green -> gold on the load-bearing prose lemmas (Fable lead)

You are the THEORY lead (Fable). Successor to A64 (read attempts/A64-lean-wave/notes/findings.md
FIRST — especially the cross-toolchain elaboration recipe; it cost A64 most of its time and you
will hit the same walls). PI end-state: every node lean-proved or certificate+verifier.
lean/depgraph.json is the live scoreboard (update labels + re-render as you land; others may
edit — pull/merge before push). Do the mathematics and Lean yourself; Opus for chores. Do NOT
touch A57/A60/A61 campaigns; light CPU (lake builds fine; do NOT re-run the 2380s native_decide
module — A64 isolated it in Measure382Check.lean precisely so edits never trigger it).

Targets, in priority order (all currently proved-prose; formalize statement AND proof, discharge
or replace the matching TopLevel axiom where one exists, axioms audit clean after each):

## T1 — A.D1: attainment (`attained`)
docs/proofs/drain_lemma.md D1. Compactness: configuration space closed+bounded, side function
continuous, interior-disjointness closed. A64's Parametrize.lean has the config-space defs.
Mathlib has IsCompact machinery — this is the one where Mathlib genuinely helps.

## T2 — A.SBRIDGE: the lambda-dilation bridge (Lemma B / B' / B.2' / B-NO)
docs/proofs/closed_disjoint_bridge.md. Pure algebra + elementary geometry (dilation, strict
gaps, pin tracking, the nofams occupancy clause). Feeds every stratum_kill application, so its
Lean form should be stated the way stratum_kill consumes it.

## T3 — B.K1: kills climb containment, aliveness descends
docs/proofs/instratum_bridge.md E.1 (+ Lemma M->E, E.2). Finite combinatorics over skeleton
tuples; no analysis.

## T4 — E.COORD: the theta<->t transfer
docs/proofs/theta_t_transfer.md — |dt| <= |dtheta| <= 2|dt| exact on the range, rBasin
justification including the forall-s slab bound r(1+sqrt2) <= h. Monotone rational bounds, no
transcendentals (A64's t-grid trig lemmas in MeasureBridge.lean may be reusable).

Do them in order; a wave that lands T1+T2 clean beats all four rushed. For each: if the prose
proof has a gap, that is a FINDING (fix the prose too, or flag load-bearing severity). Honest
partials with the remaining obligation named beat claimed closes.

## Deliverables
Lean files compiling, CI green, audit clean; depgraph labels gold as landed (+ remove/retarget
owner chips you resolve); prose docs updated where Lean exposed gaps; notes/findings.md;
registry row; LOG.md; terse.
