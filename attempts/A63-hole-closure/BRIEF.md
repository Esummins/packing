# A63 — close the A62 holes (Fable lead)

You are the THEORY lead (Fable). PI decision: the UNIQUENESS CLAIM STAYS in the theorem. Your job:
close or decisively route every hole A62 found, hardest-first where blocking, cheapest-first where
free. Do the mathematics yourself; Opus subagents only for mechanical compute/Lean-build chores.
Do NOT touch the running campaigns (A57/A60/A61) or their processes; light CPU only.

Read first: attempts/A62-trust-ledger/notes/findings.md (F1-F12, the work order),
lean/PackingCertMathlib/PackingCertMathlib/TopLevel.lean (the 13 axioms — your targets),
attempts/A62-trust-ledger/results/depgraph.json, docs/publication_checklist.md (S4, F2, F6, H8),
attempts/A22-local-rigidity/ (+recheck.py), attempts/A36-levers/, attempts/A56-param-transfer/
(M1 + the refuted monotone transfer), docs/proofs/drain_lemma.md, docs/specs/*.

## T1 — F7: Sturm isolation certificate (do first; ~10 min of math, unblocks shat_spec)
Exact rational isolating interval for the second real root of the octic
s^8-20s^7+178s^6-842s^5+1923s^4-496s^3-6754s^2+12420s-6865, by Sturm sequence or exact sign
changes, as a certificate file in certs/ + a checker (exact integer arithmetic; TCB-small) +
wire shat_spec in Lean so it appears in #print axioms of s_eleven_eq discharged, not assumed.

## T2 — F9/S4: the closed-vs-interior-disjoint bridge lemma
Write THE lemma (docs/proofs/): a minimiser's squares are interior-disjoint; the verifier prices
pairwise-disjoint CLOSED squares; the lambda-scaling-with-pin-slack repair, stated with exact
hypotheses per kill application (which lambda, which slack, where window-density is required).
Make explicit the F6 interaction: a kill valid at s0 only cannot use the rescaling escape. Then
state per certificate family (case-LP, parametric, atlas) the exact verifier-checkable hypothesis
that instantiates the lemma — this is the H4 obligation made concrete. Flag any kill family for
which the repair does NOT go through as a headline finding.

## T3 — unique_transfer: the uniqueness lemma (PI-confirmed in scope)
The selection argument (L6 slides / CC-2 teleports) proves the bound via a MODIFIED minimiser.
Prove the transfer back: any original minimiser at side s-hat connects to the selected one by
slide/teleport paths along which sigma is constant, and basin rigidity (A22/A36) propagates
uniqueness-up-to-D4 back along the path. Handle the degenerate cases H1 lists (slide creating a
new contact mid-path, ties, normalization changes). Deliverable: docs/proofs/unique_transfer.md
at drain-lemma-v3 rigor + the axiom in TopLevel.lean annotated with its proof obligations (keep
it an axiom until the prose is verified — do not claim it formalized).

## T4 — F2: the upper bound AT s-hat (route design + execute the cheap half)
Routes named by A62: (a) A22 Krawczyk existence+feasibility replayed in t-coordinates (rational
trig — the F6-blocker cure), (b) closedness of {s : an 11-packing fits} + the certified sequence
s-hat + 8.8e-10. Assess both; (b) looks cheap — a compactness argument (D1 machinery) shows the
fits-set is closed, so the infimum is attained and s(11) <= s-hat follows from the certified
sequence IF a certified sequence approaching s-hat exists (does one? the single UB cert may
suffice with a scaling argument — check exactly). Execute whichever route is provable this
attempt; design the other as a spec. Success = the honest theorem upgrades from
s(11) in [s-hat, s-hat+9e-10] to s(11) = s-hat conditional only on the lower-bound axioms.

## T5 — F4 + F5: the two medium bridges
F4: write the monotone->exact InStratum bridge (A55 cap-logic: a minimiser whose skeleton
CONTAINS a class tuple lies in an enumerated EXACT class — two paragraphs, but load-bearing).
F5: the theta-to-t coordinate transfer for box radii (A22/A36/A37 radii are theta-world;
TopLevel's rBasin is t-world); exact Lipschitz constants of t = tan(theta/2) on the relevant
ranges, stated as a lemma, and rBasin given a concrete value.

## Deliverables
certs/ Sturm certificate + checker; docs/proofs/{closed_disjoint_bridge.md, unique_transfer.md,
attainment_ub.md, instratum_bridge.md, theta_t_transfer.md}; TopLevel.lean updated (axioms
discharged where proved, obligations annotated where not; builds clean, axiom audit updated);
updated depgraph.json labels; notes/findings.md for anything new; registry row; LOG.md; terse.
Honest partials welcome: a hole half-closed with the remaining obligation named beats a claimed close.
