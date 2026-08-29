# A42 — pricing the occupancy chain + the PI's tightening sweep (Fable lead)

Goal: the decisive residual measurement for the far field. Price the OCCUPANCY certificate family
(the one that did NOT die) along the A41 cascade, prove Lemma N1, and test the PI's post-assignment
tightening schedule. Outputs plug directly into docs/proofs/seam_design.md's cost formula.

Context: docs/proofs/seam_design.md (the cascade, N1, the formula, S1a-d stalls), A39 results
(cheap-cert rule: attempt exact certification every round, gate on tau*1.005 < budget; exact cert
at L1 costs 0.6-16 s; the DEEP-CORE family's death mechanism — do not resurrect it), A38
(root_s0.json: k=0 occupancy certified 1.7 s slack 3.0; probe A: k=1 leaned right, tau 9.2,
unconverged under the OLD rule), A40 (basin h = 6.55e-3 certified, ceiling ~0.02), A37 atlas
(ball centers = Trump placements p_1..p_11).

## T1 (theory, yours): Lemma N1 — the zone-assignment collapse
11 pairwise-disjoint certified regions each containing >= 1 of the 11 centers => exactly one each,
assignment unique mod S11. Prove at Theorem-1 care (multiset/quotient framing per the lab's
symmetry discussion; disjointness hypothesis explicit; state what fails if two balls overlap).
Short — rated LOW difficulty in seam_design.md — but it is load-bearing for everything below.

## T2 (measurement): the coarse chain k = 0..3+
Conditional occupancy at s0 = 969271/250000, balls of radius r_occ = 0.06 at Trump placements
(D4-canonical frame): step k = given squares in balls 1..k (coarse conditioning, NOT deep cores),
certify "no square in ball k+1 => tau < budget". A39's cheap-cert rule from step one. Measure per
step: slack (budget - tau), wall time to certified kill, LP size. THE numbers: the slack-decay
curve (S1c) and cost growth. Go as deep as slack allows; if it dies at k = 3-5, that IS the result
— name the decay constant.

## T3 (measurement): the PI's tightening sweep (NEW — first-class)
After conditioning on ALL 11 balls at r = 0.06 (the post-N1 state): the placement domain collapses
to 11 islands. Now cycle: shrink ball 1 to r' < 0.06 ("no square in ball_1(r') minus nothing —
i.e. certify ball 1's square must be within r' of p_1"), certify, move to ball 2, sweep. Measure:
certificate cost + slack vs r' at r' = 0.03, 0.015, 0.0066 (= A40's basin, the rendezvous target).
Compare cost against the naive depth-first refinement model (seam_design.md d_sq term). Hypothesis
to test: post-assignment LPs are tiny (domain = 11 islands) and strong (field concentrates);
Gauss-Seidel sweeps may reach the basin radius at seconds-per-certificate. Also check: does the
sweep's SECOND pass (re-tightening ball 1 after balls 2-11 tightened) gain further, as the PI
conjectures? Honest failure = the slack dies at some r'; name it.

## T4: compose
Plug measured (chain cost, sweep cost, reachable r') into seam_design.md's formula with A40's h
and A39's L1 numbers -> desktop-days bracket for the full far field, dominant term named,
GO/NO-GO. List what N6 (ghost-manifold cells) still blocks regardless.

Constraints: Opus subagents for LP compute; <= 4 heavy processes; ONE long-poll waiter per
background run (lab rule); checkpoints; exact certification per lab standard (verifier is the
arbiter); A29 untouched. Terse traffic; PI-readable final report.
