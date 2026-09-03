# A89 — the tilt-floor lemma for corner blockers at a k0 Fritz-John point (Fable lead, theory + measurement)

Context. DF-K0 (docs/proofs/drain_flow_k0.md, A87) reduces k0_00 to H1: no k0 Fritz-John point of the
enclosing-side function at side <= s-hat. So on k0_00 we may assume CRITICALITY, a hypothesis the A85
tree does not use. The tree's cost is concentrated in the near-flush ghost zone: corner blockers with
tilt in (0, theta_0) jammed epsilon off the corner, where LP kills fail (eps_geo exhausted) and local
wastage charges are exactly 0 (A47 near-flush cell). A50 proved, for members of a spanning wall-to-wall
chain, the dichotomy tilt = 0 exactly OR tilt >= 1.73 deg. Every certified FJ point we hold (A87's 167 at
tol 1e-6, results/cp87_fj_polished.jsonl; the 12 atlas families, A46 audit) has loaded wall-corner tilts
>= 33.9 deg. PI direction: prove the dichotomy for corner blockers at a k0 FJ point, delete (0, theta_0)
from every blocker box in the tree.

Read first: docs/proofs/drain_flow_k0.md (H1's exact statement, the FJ system, the drain step), A50's
near-flush exclusion (attempts/A50-*, its theorem + proof mechanism: which motion it uses and why it is
s-nonincreasing and feasible), docs/proofs/structure_lemmas.md (L1 degree >= 2, L6 slide-stuck, per-wall
<= 3), A58 corner crowding (K0-BLOCKED: each corner box met by >= 2 non-simple squares), A47
results/a47_report.md (feasibility law: tilt > 40 deg cannot sit within 0.7 of a wall; near-flush cell = 0),
A46 composition_report.md §1 (loaded vs loadable contacts, lambda LP), attempts/A85-k0-route/notes/
pilot_report.md (blocker boxes, which LP rows FAIL and at what tilts), docs/known_results.md item 16a
(active-graph planarity caveat; ruler cap side-dependent).

## T1 — the lemma (state at drain-v3 rigor; name every obligation)
Theorem TF (tilt floor). Let z be a k0 FJ point at side s <= s-hat (selected per B.SEL / L6 if you need
it — say exactly which selection clause you use). Let Q be a square meeting a corner box [0,1]^2 (a corner
blocker, A58). Then tilt(Q) = 0 exactly, or tilt(Q) >= theta_0, with theta_0 explicit (target >= 1 deg;
report whatever you can prove). Route to try first: a near-flush wall-touching or corner-touching square
admits a feasible s-nonincreasing motion (rotation about its wall contact toward flush, or the A50
motion) unless a neighbour blocks it; enumerate what can block it (L1 degree, the second blocker of the
same corner, a free square) and show each blocking configuration is either impossible below s-hat or
itself non-critical. Cases you must treat explicitly: (i) Q loaded (positive multiplier) vs Q a rattler
(unloaded — criticality says nothing; use the drain/selection to move it, or show a rattler blocker can
be rotated to flush without changing s and the result is still k0 or teleports to k1); (ii) the second
blocker jammed against Q (the two-square corner jam: axis-aligned Q offset epsilon along the wall, tilted
partner dipping a vertex below y = 1 — write out why this is non-critical or impossible); (iii) tilt
exactly 0 but offset from the corner (allowed in k0 — the lemma must not claim it is excluded).
If the lemma is false, produce the counterexample configuration explicitly (a jammed near-flush blocker
at a genuine FJ point) — that is a full success too, and it tells the tree where the cost is real.

## T2 — empirical check (Opus chore; exact where possible)
On A87's 167 certified k0 FJ points and the 12 atlas families: for every square meeting a corner box,
record tilt, loaded/rattler status (lambda LP), and the blocking contacts; confirm no loaded corner
blocker has tilt in (0, theta_0). Then on A85's LP rows (results/a85_lp_samples.jsonl, nodes/k0_00/):
the fraction of FAILED nodes whose blocker box lies in (0, theta_0) entirely or partly, and the fraction
of the blocker-box tilt volume the lemma deletes. Canary: Trump's three corner squares have tilt exactly 0
(the lemma's exact-0 branch) — it must not be excluded.

## T3 — impact and consumers
State how the tree consumes TF: the blocker box census (A85 tree85/corner85) restricted to tilt in {0}
union [theta_0, 90 - theta_0] union {90} (D4), the K1/aliveness bookkeeping (a box with tilt exactly 0 is
a k0 box only if offset from the corner), and the Lean-readiness note (which TopLevel axiom the lemma
feeds, what hypothesis it adds — criticality via DF-K0). Re-price the tree with the deletion: use A85's
measured per-node costs, not the headline. Report: theta_0, the lemma status (proved / gap named /
counterexample), the deleted fraction, and the re-price.

Constraints: <= 2 processes, BLAS-pinned, headroom > 6 GB; A57/A60/A61/A86 untouched; frozen verifiers
untouched; writes in attempts/A89-tilt-floor/, docs/proofs/tilt_floor_k0.md, depgraph C.K4TIER note (chip
-> A89; pull/merge before push), registry row, LOG.md. Report tersely: theta_0 and lemma status first.
