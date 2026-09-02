# A81 — does U-ladder slack escape the tightness wall? k4_08 pair certificate at slack 2 (Fable lead)

You are the THEORY lead (Fable). The synthesis of A77 + A80: A77's Lemma W''' says a corners4 pair
certificate is NECESSARILY TIGHT (slack 0.004-0.04) and a tight measure has eta-fine boundaries
=> verification tree ~1e9-1e11 nodes (frontier retention 0.75-0.86 per level, flat). A80's U-ladder
row (sound on the EXACT stratum, Lemma U-ROW) moves k4_08's restricted adversary from 27 to 26.000
at rung 1 (margin -2.000 vs threshold 28; rungs 2-5 add ~0.55 each, whole ladder ~3.5 units). So
on k4_08 the certificate no longer has to be tight — it has ~2 units of slack at rung 1. The
question this attempt answers: DOES SLACK BUY VERIFIABILITY? I.e. does a k4_08 pair certificate
emitted under the rung-1 row at slack ~2 have a frontier retention r(d) well below 0.75 (coarse
boundaries -> tree 1e5-1e7 nodes -> Rust PASS in hours), or is r(d) intrinsic to the pair geometry?
This is the decisive experiment for the whole protected tier; corners4 is NOT the target here (no
Trump image within 0.84 — the U-row is irrelevant there).

Read first: docs/proofs/u_ladder.md (Lemma U-ROW, the rung table, dodge witness, T1 reach
collapse: the sound row zone delta <= ~3e-4 because of square 6's hinge pocket; zone radius is
irrelevant to the margin), docs/proofs/pair_kill.md §6.7-6.9 (W'', W''', the emission loop,
hint trees, frontier-retention measurement), attempts/A77-corners4-close/code/{hintbatch,iter77,
hintcheck}.py + notes, attempts/A80-u-ladder/code + results, attempts/A73-pair-v2 (Rust verifier
verify_pair2_rs, --root_order rust per A77's C3 finding), attempts/A74-mixed-depth/code.

Constraints: <= 2 slots, one LP at a time, BLAS-pinned, headroom > 6 GB; A57/A60/A61 untouched;
frozen verifiers untouched (the U-row enters the EMISSION LP as a constraint and the certificate
as spec-side data per Lemma U-ROW — if verify_pair2 cannot express the row, that is a versioned
spec addition v2.1 with its soundness lemma, both implementations, gates — NOT a silent edit);
certs/ new files; depgraph C.K4TIER chip -> A81; Trump canary per run (the U-row must never bind
Trump: he is excluded only by the exact-stratum hypothesis).

## T1 — the measurement (decisive; do first)
Emit a k4_08 pair certificate (beta = 1, fixed side s0, both Trump images {id, diag}) under the
rung-1 U-row at slack target ~1.5-2.0 using A74/A77's mixed-depth emission (consolidation ON —
fewer fatter atoms is the objective; slack is now abundant, spend it on coarseness). Build the
complete hint tree (A77 hintbatch.py) and measure r(d) per level to depth 25 on all roots.
Compare against corners4's 0.75-0.86. Report the tree-size law under slack. If r(d) <= ~0.5 the
complete tree is ~1e5-1e7: proceed to T2. If r(d) stays ~0.8: the wall is intrinsic to pair
geometry, not tightness — deliver Lemma W'''' (retention vs slack), and the tier redirects to
conditioning trees (A65 route 3 / A60-style) — say so plainly.

## T2 — PASS (only if T1 says yes)
Run the Rust verifier (--jobs 8, --root_order rust, hints) to a full-quantifier PASS; cross-
check with verify_pair2.py on a root prefix with per-rule firing counts diffed; corruption gates;
canary ledger; both-verifier reports. State the composed kill: Lemma U-ROW (rung 1, U_1 at
delta <= 3e-4 with the basin landing) + Lemma P + P0 consumption into stratum_kill for the EXACT
k4_08 stratum; note the window obligation (slack-core slabs, P-B shell rules) separately. If it
lands: the first protected-class kill — independently re-verify before claiming, then k4_11/k4_03
(same rung-1 row, their own images per A71) are the immediate successors.

## Deliverables
r(d) table + tree-size law; certs/ + reports; docs/proofs/pair_kill.md §6.10 (or W''''); depgraph;
registry row; LOG.md; notes/findings.md (if the harness blocks that path, put findings in the proof
doc as A80 did); terse. Walls with measured laws are successes.
