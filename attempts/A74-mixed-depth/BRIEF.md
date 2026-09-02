# A74 — mixed-depth emission: the corners4 certificate (Fable lead)

You are the THEORY lead (Fable). Successor to A73 (read attempts/A73-pair-v2/notes/findings.md +
docs/proofs/pair_kill.md §6.6 FIRST). State of play: the verification-throughput wall is broken
(clean-room Rust verify_pair2, C3 cross-validated, 131-323k nodes/s at --jobs 8); corners4's
remaining wall is EMISSION SHAPE — uniform-eta emission is dead (the fractional wall crosses the
threshold at eta* in (0.006, 0.05)), so every valid certificate is a mixed-depth measure, and
the measured cost driver is weight fragmentation (many small weights needing simultaneous
certainty), not margin. A73 priced the residue and left the machinery ready:
code/loop413.py (DEFICIENT-EARLY survey loop), hint trees, the deepening/consolidation pass
design, the 622-atom seed, and v2's analytic clauses.

Constraints unchanged: <= 2 LP slots (BLAS-pinned, headroom > 6 GB, wait out dips; run
sequentially if in doubt); A57/A60/A61 untouched; frozen verifiers untouched (v1 sha d9b7a24a;
verify_pair2.py + Rust binary now also frozen references — soundness bugs are headline findings,
fixed via versioned spec erratum + both implementations + corruption gates, never silently);
depgraph shared (owner chip C.K4TIER -> A74); Trump canary ledger per run.

## T1 — the mixed-depth emission loop for corners4 (beta=0, P0, stuckness-free)
Design the depth profile from Lemma W-prime's accounting: shallow atoms carry the bulk mass,
a small certified sub-eta stratum carries the V - threshold excess. Concretely: (a) run the
DEFICIENT-EARLY survey loop to convergence with mixed-depth column generation (consolidation
pass merging fragmented weights where the LP permits — fewer, fatter atoms is the explicit
objective, per the fragmentation finding); (b) emit; (c) certify with the Rust verifier
(--jobs 8; the compiled run is cheap now — use it inside the loop, not only at the end, per the
A39 discipline). Target: ONE exactly-verified corners4 emptiness certificate at a fixed window
side + the P0 consumption path into stratum_kill + the window pricing (slack-core slab, P-B
shell rules). If emission still fails, the failure must come out as Lemma W-double-prime: the
measured mixed-depth law (what profile is forced, what it costs) — walls with size laws are
successes.

## T2 — if corners4 lands: the critical tier with stuckness rows
Same machinery + docs/proofs/stuck_rows.md SR-1/SR-2 rows for k4_08/k4_11/k4_03 (margin -beta
classes; basin row P-B as reserve where its exact-stratum + shell hypotheses hold, k4_08 has
TWO images {id, diag}). Any one of them landing converts the tier's route from "architected"
to "demonstrated". If corners4 does NOT land, skip T2 and spend the time sharpening W-double-
prime instead.

## Deliverables
certs/ + Rust verification reports; docs/proofs updates (pair_kill.md §6.7 or W-double-prime);
per-run canary ledger; depgraph/registry/LOG; notes/findings.md; terse. Commit your work (pull/
merge first); push only if the tree is clean of campaign collisions, else say so.
