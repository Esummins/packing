# A84 — the protected tier as residual trees: pilot k4_08 (+ one k<=3), price the tier (Fable lead)

You are the THEORY lead (Fable). After A65/A66/A71/A73/A74/A77/A80/A81, EVERY global-measure route
for the 16 protected classes is closed with a named law (single-square: K1 sharpness; pair: W'''/W''''
retention intrinsic; boosted: Corollary S-08; basin row / U-ladder: reserve-plus, ultra-shallow;
bottom-up grains: hinge wall). The route that remains — and that A83 just made SOUND — is the
A60 machinery: a residual zone-tree per exact protected class whose leaves are (K) kills (transfer
to lower sides by Lemma B with pin slack delta_pin = 2e-2) and (D) basin discharges (transfer to
lower sides by the CONTRACTION TUBE, docs/proofs/contraction_tube.md, T = 0.0457 at A60's landing
radii — stratum-blind), plus A82's plain kills below the crossover. KEY REFRAME (verify it as
Lemma P-TREE, at drain-v3 rigor, FIRST): the K1 "protection" only blocks single-certificate kills
because the s0 residue contains Trump; a tree with (D) leaves handles that exactly as trump5's does —
for the LOWER BOUND no exact-stratum hypothesis is needed at all (basin: sigma >= s-hat on the
discharge box, so nothing there beats s-hat; Trump himself has sigma = s-hat, not <); the exact
hypothesis enters only at equality (basin: equality only at z-hat; z-hat is not in the exact
class), i.e. uniqueness, which A78's UniqueChain already composes with Theorem U certified. If
this lemma holds, the "protected tier" is just "16 more trump5-like campaigns" — a COMPUTE
question, and this attempt prices it.

Read first: attempts/A60-trump5-campaign/{notes/resume_plan.md, notes/ledger.md, code/tree60.py,
confine60.py, launch.ps1} (the engine; COPY, never run against A60's state), attempts/A59-trump-
residual/results/a59_report.md (the pilot program P0-P7 + pricing law r_kill = 4.55 hw), A55's k4
pin sets + A65's clique_caps/crowdfam.json (per-class images), A58 notes/theory.md (clear-corner
crowding: every clear corner of a k<=3 minimiser has >= 2 non-simple squares meeting its corner box
— the cover SEED for k<=3 classes that have too few pins), docs/proofs/{contraction_tube, u_ladder,
pair_kill §6.10, closed_disjoint_bridge, unique_transfer}.md, A82 results (crossovers per class).

## T1 — Lemma P-TREE (the soundness reframe)
State and prove: for an exact protected class S with pin set P, a zone-tree over the monotone
hypothesis "P simple" whose leaves are (K) kills at s0 and (D) boxes contained in the basin (mod G,
per D.S6's bookkeeping) proves: no packing in class S has sigma < s-hat at side s0, and (with Lemma
B at delta_pin and the tube) at every side in [s-hat - delta_basin, s0]. Say exactly where the
exact-stratum hypothesis is and is not used. Cross-check against A63's H10-stuck architecture and
A78's UniqueChain (what, if anything, they still need beyond this).

## T2 — pilot k4_08 with the A60 engine (Opus compute, your design)
Budget 7 (4 pins). Interior-square cover per A59-P1's analogue (prove or measure which square is
forced into which zone with 4 pins — if no P1-analogue holds, the cover is over the whole free region;
say so and price it), pin slack delta_pin = 2e-2 from the start (A60 is qualifying 2e-2 now — reuse
its verdict), cover kill rate, resister count, one deepen round, and the ladder contraction ratio on
the residue (is it ~4.55 hw like trump5?). Canary: every Trump image of k4_08 ({id, diag}) must
survive to a (D) leaf and never be killed. Then the SAME on one k<=3 class (k3_05 or k2_01: fewer
pins, seed the cover from A58's clear-corner crowding) to measure how cost scales with free
dimension. <= 3 LP slots total (A60 is at 4, A57 at 6, A82 at 2 — check commit headroom > 6 GB and
wait out dips; BLAS-pinned).

## T3 — price the tier + composition
From the pilot laws: certificates and desktop-days per class, for the 6 k4 and the 10 k<=3 classes,
with the seam per class (A82 crossover vs delta_basin = 0.0457 at delta_pin = 2e-2). Write the
composition as the obligation table for the last stratum_kill axiom pieces. If the k<=3 classes
explode (no P1-analogue, residue not contracting), say so with the size law — that is the finding.

Constraints: A57/A60/A61/A82 untouched (copy code, own results dirs); frozen verifiers untouched;
certs/ new files only; depgraph C.K4TIER chip -> A84 (note the redirect); registry row; LOG.md;
notes/findings.md (fallback: the proof doc §6). Report tersely: Lemma P-TREE verdict, pilot laws,
tier price, findings, pointers.
