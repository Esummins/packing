# A87 — k0_00 by drain-flow, not by tree: the "no critical point below s-hat" route (Fable lead)

You are the THEORY lead (Fable). PI insight: A85 priced k0_00 as a VOLUME tree (45-100 desktop-days)
but its own CP search shows k0 has NO critical point below s-hat (lowest 3.887213 = s-hat + 0.0101)
and every k0 optimum is UNDER-CONTACTED (median 6 contacts vs Trump 14) => the s-critical set of k0
is a union of positive-dimensional critical MANIFOLDS all at s >= s-hat + 0.01, and {s < s-hat} ∩ k0
contains no critical points. A tree covers volume; the content is a measure-zero critical set. Replace
the tree with a DRAIN-FLOW / downward-induction argument. This attempt: make it rigorous or find
exactly where it breaks.

Read first: docs/proofs/drain_lemma.md v3 (D1 attainment, D2 centroid-shrink, the FJ selection
formalism, Gordan/Farkas test), docs/proofs/structure_lemmas.md (L6 slide-stuck, wall-to-wall chain),
attempts/A30-t3-pilot/t3lib.py (the FJ/Farkas exclusion engine + its exact duals), attempts/A22-local-
rigidity (Krawczyk LOCAL FJ exclusion around Trump — the template for the GLOBAL version),
attempts/A85-k0-route/results/cp85_k0_search.json (262 k0 optima, none below s-hat, all under-
contacted), docs/proofs/k0_route.md (A85's tree route + K0-FREE teleport-to-k1), docs/known_results.md.

## T1 — the drain-flow theorem (the reframe; state at drain-v3 rigor)
Theorem DF-K0: IF (H1) no k0 configuration with s < s-hat is a Fritz-John critical point of the
enclosing-side function subject to the packing constraints, THEN every selected k0 minimiser has
s >= s-hat, GIVEN that every k>=1 stratum is excluded below s-hat. Proof obligations to nail:
 (a) DRAIN STEP: a non-critical k0 config has a feasible s-nonincreasing motion that either forms a
     new contact or makes a square simple (drain lemma v3 gives the direction; you must show it
     reaches a stratum boundary, not just moves — the QUANTITATIVE drain: s drops by a definite
     amount OR a contact forms within bounded motion; use D2 centroid-shrink; if it can asymptote,
     that is the break point — say so).
 (b) EXIT well-foundedness: the boundary of k0 reached by draining is a HIGHER stratum (a square
     became simple => k increases) at side s' <= s; induction on 11 - k, base = the killed strata.
     State the exact map "drain exit -> which stratum" and that s' <= s (draining never increases s).
 (c) SELECTION compatibility: reconcile with L6 (a selected minimiser is already slide-stuck) — a
     slide-stuck k0 config with no simple square and s < s-hat is EITHER critical (excluded by H1)
     OR the selection would have moved it (contradiction). Make the "stuck but non-critical" case
     impossible or route it.
Deliverable: docs/proofs/drain_flow_k0.md with DF-K0, the three obligations discharged or the exact
gap named. If DF-K0 holds, k0_00's whole cost = the H1 certificate (T2), not a tree.

## T2 — H1: the global FJ-exclusion certificate (the hard obligation; pilot it)
Certify "no k0 FJ critical point with s < s-hat over the configuration box." This is A22's Krawczyk
exclusion made GLOBAL: branch-and-prune over configuration space, at each box test that the FJ system
(stationarity of s + complementarity on active contacts + the k0 hypothesis "no square simple") has
NO solution with s < s-hat (interval-Newton/Krawczyk non-existence, exact rational; t3lib for the
Farkas/FJ duals). KEY QUESTIONS to measure on a pilot (a few configuration boxes + the neighbourhoods
of the 262 known optima): (i) is the exclusion test per box much cheaper than an LP kill (determined
system vs optimisation)? (ii) does the branch tree over the CRITICAL variety stay far smaller than
A85's volume tree (the critical set is measure-zero + all known components are above s-hat, so most
boxes should exclude immediately by an s-gradient-nonzero argument — a config where dS/dmotion != 0
in a feasible direction is not critical, killed with no FJ solve)? (iii) the under-contacted manifolds:
a critical manifold has a flat direction => the FJ system is degenerate there; handle rank-deficient
FJ boxes (they are exactly the s >= s-hat+0.01 optima, provably above the target). Report the pilot's
per-box cost, tree-size projection, and the price of H1 vs A85's 45-100 desktop-days.

## T3 — verdict
Compose: k0_00 price under the drain-flow route (H1 cost + DF-K0, both window-transferred: DF-K0 is
side-generic; H1 must exclude at every s in [3.82, s-hat] — note the exclusion gets EASIER as s falls
below the lowest CP, so the binding side is just-below-s-hat, same as everywhere). Compare to the
tree. If drain-flow wins, this becomes k0_00's route and the tier's k<=3 classes may inherit it
(they also have few pins). If it loses or H1 is intractable, say why and fall back to A85's tree.

Constraints: <= 2 slots, BLAS-pinned, headroom > 6 GB; A57/A60/A61/A85/A86 untouched; frozen verifiers
untouched; certs/ new files only; depgraph C.K4TIER note (chip -> A87). Honest partial (drain-flow
handles the bulk, small residue to the tree) is a full success. This is a design+pilot attempt: the
deliverable is DF-K0 with its obligations resolved and H1's measured price.
