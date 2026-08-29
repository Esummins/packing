# A46 — flush-mandatory via the balanced-wedge budget (Fable lead)

Goal: prove I-L17 (docs/ideas.md — read first): no critical structure at s0 is flush-free.
W1 AND W2 below. This is a NEW-MATHEMATICS attempt; the pilot-honesty rules still apply (label
every gap; a refutation of W1 with a concrete near-flush balanced critical mechanism would be a
major finding in its own right).

Context: A44 results/a44_report.md + notes/theory.md (why FJ+counting is closed — do NOT reuse that
route; the index identity and L-lemmas are available as ingredients), A45 results/a45_report.md +
notes/charging_lemma.md (why raw-contact charging is inert — Ceiling 2; the moat machinery and the
plane-mode lemmas ARE reusable), A23/A25 (the dead-region oracle + atlas + union disjointness — W2's
engine), A35 notes/theory.md (semantic cells, tie/endpoint machinery — W1's language),
docs/proofs/structure_lemmas.md + drain_lemma.md v3, A37 atlas (canaries).

## W1 (yours, the crux): small-angle exclusion
Statement to prove (or refute with a mechanism): there is delta_0 > 0 such that in any FJ-critical
configuration at s0 with NO flush contacts, every corner-on-edge contact has relative edge angle
delta >= delta_0. Candidate routes, in order: (a) the wedge-closing drain — show the relaxation
rotating toward flush is sigma-non-increasing when unblocked, so criticality forces blocking; then
show near-flush blocking (balance at small delta) forces either a flush contact elsewhere or a
contradiction (the blocking torque needs a lever the near-flush geometry cannot supply — quantify
via the force-balance rows); (b) stratum/limit argument: flush-free critical points at delta -> 0
converge to critical points OF the flush stratum with a broken selection — excluded by the A35
tie/endpoint analysis; (c) if both fail, find the counterexample mechanism and characterize it.
Care: sigma-non-increase of closing is NOT automatic (bounding-box coupling); the balance is
network-level (FJ rows), not local. Any delta_0, however small, suffices if W2's table reaches it.

## W2 (Opus under your direction): the balanced-wedge table + budget kill
(1) Certify w(delta): for a BALANCED corner-on-edge contact at relative angle delta (balance
pinning the neighbour geometry — extract the exact pinned data from the FJ row structure), the
certified dead area attributable to the pair, via the A23 oracle in exact Fractions, over a delta
grid from delta_0-candidates (1, 2, 5 deg) up to 45. (2) Disjointness: A25's rectangle-subtraction
scheme adapted to wedge regions; prove or certify the union bound for >= 2 wedges per square.
(3) The budget composition: min contacts in a flush-free 11-network (L1 + connectivity + L6 chain
=> derive the honest minimum, do not assume 17), times min w over the admitted range, vs 4.0318;
report the delta_0 threshold W2 actually needs, so W1 knows its target. Canaries: Trump (his CE
contacts are wall-type/unbalanced-toward-flush — structure must survive trivially); atlas valleys
at their own s.

## Compose
W1(delta_0) AND W2(delta_0) => flush-mandatory at s0. Report the theorem or the named gap; census
value (~x1e3, the legitimized N4-type column) measured via A43-H1 if proved. Gap list, registry,
LOG, PI-readable. Constraints: <= 4 heavy processes, ONE long-poll waiter per background run,
checkpoints, exact certification the arbiter, A29 untouched.
