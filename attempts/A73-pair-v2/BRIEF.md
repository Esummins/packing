# A73 — pair-certificate v2: break the verification wall, pilot corners4 (Fable lead)

You are the THEORY lead (Fable). Successor to A71 (read attempts/A71-pair-emission/notes/
findings.md + docs/proofs/pair_kill.md §6.5 Lemma W + notes/t3_solver.md FIRST). A71 proved the
v1 wall is VERIFICATION COMPLEXITY, not certificate non-existence: every P1'-valid k4-tier
certificate must carry >= 11 coverage units on atoms < 0.15 deep, and the frozen pure-Fraction
verifier at 57 nodes/s prices that at months-to-centuries. corners4 is the least-walled class
(1-unit shortfall, certified bracket ~[20.517, 20.542] vs threshold 21) and is the pilot.

Constraints: <= 2 LP slots (BLAS-pinned, headroom > 6 GB, wait out dips); A57/A60/A61 and all
frozen verifiers untouched; verify_pair.py v1 stays frozen (sha d9b7a24a); spec changes are a
VERSIONED docs/specs/pair_certificate_v2.md, never silent edits; depgraph shared (pull/merge;
owner chip C.K4TIER -> A73). Trump canary theorem = standing guardrail, check per run.

## T1 — spec v2 + the two verifier upgrades
(a) MARGIN-AWARE SPLITTING: A66/A71 both measured that COVERED needs very tight boxes under
uniform bisection; design the split rule that spends depth only where enclosure margins are
thin (the T16 headroom idea applied to the 6-D pair B&B), with the soundness argument that the
rule preserves the exhaustive-disjunction invariant. (b) ANALYTIC COVERAGE CLAUSE: where a pair
box's coverage is decided by a monotone/quasiconcave bound (A64's w-quasiconcavity machinery,
A70's alternating-Taylor enclosures are the toolkit), let the verifier accept an analytic
one-step discharge instead of subdividing to dust — each such clause needs its own lemma at
drain-v3 rigor in the spec. Write v2 for clean-room reimplementation.

## T2 — the compiled second implementation (TCB-wanted; Opus chore under your spec review)
A compiled verifier (Rust preferred; C acceptable; exact rational arithmetic via i128/bigint —
NO floats in decisions) implementing v2 from the SPEC (the chore must not read verify_pair.py's
internals beyond the spec + its selftest corpus). Cross-validate: both verifiers must agree on
the v1 toy corpus (PASS s=199/100, FAIL s=201/100, smoke paths) and on corruption gates. Target
throughput >= 100k nodes/s (A71's float mock hit 72k/s in Python; compiled exact should beat
it). This doubles as checklist C3 for the pair family.

## T3 — pilot: corners4 emptiness certificate
With v2 + compiled verifier: emission oracle loop for the corners4 beta=0 (P0, stuckness-free)
certificate at a fixed window side. A71 left a 622-atom covering seed and the pricing-driven
catalog machinery; the D1 adequacy + containment audits are standing gates. Success = ONE
exactly-verified corners4 emptiness certificate + the P0 consumption path into stratum_kill
stated; then price the window (slack-core slab per the P-B shell rules). If the wall persists
even for corners4 at v2 speeds, measure it precisely (nodes needed vs nodes/s) — Lemma W's
quantified successor, and the k4-tier redirects fully to stuckness + basin + A60-style
conditioning.

## Deliverables
docs/specs/pair_certificate_v2.md; the compiled verifier + cross-validation log; certs/ new
files; per-run canary ledger; depgraph/registry/LOG; notes/findings.md; terse. Honest walls
with measured size laws remain successes.
