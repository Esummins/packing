# A66 — corners4 deletion + the pair-certificate family (Fable lead)

You are the THEORY lead (Fable). Successor to A65 per its ranked residue for H10-stuck
(docs/proofs/h10_stuck.md). Two tasks, cheapest-decisive first. Same constraints as A65: at most
2 light LP slots (BLAS-pinned, commit headroom > 6 GB before launching), never touch A57/A60/A61
state, new files only in certs/, frozen verifiers never modified. lean/depgraph.json is the live
scoreboard — update + re-render as you land things (A64 may also edit; pull/merge before push;
pushing is fine if the tree is clean of campaign write collisions — otherwise leave committed and
say so).

Read: docs/proofs/h10_stuck.md (the pricing, the H10-I incidence lemma, the channel observation),
docs/proofs/theorem_u.md + unique_transfer.md, attempts/A65-low-k-closure/results/
{crowdfam.json, boost_k4_13.json, clique_caps.json}, attempts/A58-clear-corner/notes/theory.md
(A58-G3 pair version), docs/specs/case_lp_certificate_v1.md (the spec pattern to imitate),
attempts/A34-sos-pilot/notes/verdict.md (the collapse theorem — pair-clique caps; know why pair
STRUCTURE differs from pair CLIQUES before designing anything).

## T1 — corners4 direct integral infeasibility (short, decisive; do first)
A65's route (2): with all four corner slots pinned, the channels between adjacent corner pins
have width s0 - 2 = 1.877084 < 2 = s(2), and the crowd-family search found the pins+7
configuration infeasible even without stuckness. Target: a PROOF that corners4 is EMPTY at every
s in [3.82, s0] — not merely stuck-excluded. Candidate argument: the four pins partition the
remaining region; channel width < s(2) forbids 2 squares abreast in any channel; count what the
7 free squares would need vs what the geometry admits (occupancy/N1 machinery, or a small exact
case-LP per channel at window-grade slack cores delta per the closed_disjoint_bridge rules).
Deliverable: docs/proofs/corners4_empty.md + any certificates exactly verified + depgraph note
on C.K4TIER (one of six k4 protected classes deleted outright if this lands). If the argument
fails, say exactly where the 1.877 channel admits the needed occupancy.

## T2 — the pair-certificate family (design + spec + pilot)
A65 proved single-square measure certificates CANNOT close H10-stuck (the forced 2-crowd's value
is pairwise; boosted-kill law refuted at every beta). Design the pair certificate: a measure/LP
object whose atoms price PAIRS (e.g. mu on ordered pairs of placements, or a single-square field
PLUS pairwise conflict rows with exact dual witnesses), such that a PASS proves no stuck packing
realises the class. Requirements: (a) exact rational verification with a small standalone
verifier in the TCB style (spec first: docs/specs/pair_certificate_v1.md, written for clean-room
reimplementation); (b) soundness lemma at drain-v3 rigor including the closed-vs-interior bridge
clause for the pair rows and the stuckness hypothesis's exact form (which teleport-blocked
constraints become rows); (c) the A34 collapse theorem must NOT apply — state explicitly why
this is not a pair-clique relaxation (the stuckness rows couple to the global budget). Then
PILOT on k4_08 (the load-2.00 class where mbar = 2.53 was measured): emit, solve, exactly verify
one pair certificate with your 2 slots. Trump's configuration must survive as the aliveness
witness in any class he inhabits — canary at every step. Honest NO-GO with the failure mechanism
named is a full success (it would be the ninth face and would redirect H10 to conditioning/FJ).

## Deliverables
docs/proofs/corners4_empty.md; docs/specs/pair_certificate_v1.md + verifier + pilot cert/report;
depgraph updates + re-render; notes/findings.md; registry row; LOG.md; terse traffic.
