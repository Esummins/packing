# A77 — run the corners4 loop to a verified PASS (Fable lead)

You are the THEORY lead (Fable). Successor to A74 (read attempts/A74-mixed-depth/notes/
{findings,ledger}.md + docs/proofs/pair_kill.md §6.7 FIRST). State: A74 produced the FIRST
sub-threshold restricted pair measures for corners4 (md8: W2 = 20.95828 < 21, P1'-valid, every
atom >= its level's eta — tangency trap closed by construction) and a converging verification
loop: with spec-§4 hint trees the Rust verifier's residue is CAPS ONLY (0 holes; 99.8% certain
mass), the harvest -> catalog-growth -> re-solve loop converges ~4x per iteration (holes 220 ->
57 at equal budget), ~1 h/iteration. Certification to a full PASS was left unpriced. Your job:
turn the crank to a verified PASS, or measure exactly where it stops.

Constraints: <= 2 slots (BLAS-pinned, headroom > 6 GB, wait out dips; 1 LP at a time as A74
did); A57/A60/A61/A76 untouched (A76 is the bottom-up front — if it delivers a certified
radius R and the P-B(R) row via the advisor, ADD the row: it widens your slack, which is the
scarce resource at 0.04); frozen verifiers untouched (verify_pair v1/v2 Python + Rust); hint
trees are spec-§4 side data, not verifier edits. depgraph: owner chip C.K4TIER -> A77.

## T1 — iterate to PASS
Run the A74 loop (code/loop413m.py + hinttree.py + harvest) from md8 with a budget of N
iterations (start N = 8; each ~1 h). Per iteration record: W2, slack, holes, cap certain-mass,
node budget, wall. Manage the two slack consumers deliberately (A74's W″: depth pricing and
consolidation both spend the 21 − W2 slack; catalog growth by exact holes is ~free — prefer it).
Success = ONE full-quantifier PASS from the Rust verifier on a corners4 beta=0 certificate at
the fixed side, cross-checked by verify_pair2.py (both implementations, per-rule firing counts
diffed — the VACUOUS-CONTAIN agreement caveat), corruption gates run, canary ledger entry.
Then state the P0 consumption path into stratum_kill and commit the certificate.

## T2 — if it stalls
If holes/caps stop shrinking before PASS, deliver Lemma W‴: the measured convergence law
(holes vs iteration vs node budget), the binding resource, and the certification cost at the
asymptote. A measured stall with the law is a success.

## T3 — window pricing (only if T1 lands)
Price the ~38 slack-core slabs given the measured per-side iteration count; if A76's R row
lands, re-price with it.

Deliverables: certs/ + Rust and Python reports + firing-count diff; per-iteration table;
docs/proofs/pair_kill.md §6.8; canary ledger; depgraph (C.K4TIER: if PASS, note "corners4
KILLED — first protected-class certificate"); registry row; LOG.md; notes/findings.md; terse.
Commit your work; push if the tree is clean of campaign collisions.
