# A86 — Lean wave 7: the last theorems the compute nodes need (Fable lead)

You are the THEORY lead (Fable). Six depgraph nodes remain non-gold (C.K4TIER, C.A61, D.TREE, D.LADDER,
D.SLAB, D.S6); all are compute-gated, but their GOLD needs three Lean deliverables that do NOT depend on
campaign data. Build them now so that when A57/A60/A61/A85 finish, the only remaining step is
certificate replay. Read attempts/{A64,A68,A70,A75,A78,A79}-*/notes/findings.md (toolchain recipes),
lean/tube_obligation_A83.md, lean/k0_readiness_A85.md, docs/proofs/{contraction_tube, protected_trees,
k0_route, closed_disjoint_bridge, cover_invariance, theta_t_transfer}.md, lean/PackingCertMathlib/
PackingCertMathlib/{RigidBasin*,RigidA36,Dilation,ThetaT,TopLevel}.lean. Standing constraints: light CPU;
isolated native_decide modules cache-hit only; never touch A57/A60/A61/A85 state; depgraph shared
(pull/merge; owner chips A86 on the six nodes' Lean sub-obligations via note, chips stay with the
campaigns).

## T1 — the contraction-tube checker (A83's obligation)
Port Tube(T, r) to Lean on A79's RigidBasin machinery per lean/tube_obligation_A83.md: tubeBox/InTube,
the compression lemma (all rows strictly compressed on the slot ray), the split remainder, iter_pin;
soundness theorem `tube_sound`: PASS => every packing in Tube(T, r) has sigma >= shat, equality only at
zhat. Replay A83's certs/tube_* (42 certificates; isolate the native_decide module). Lemma SEAM's map
(t = shat - m, pins w = 0, free squares w <= r_land) as a theorem consumed by T3.

## T2 — the atlas-value box checker (for A85's drains and A37's boxes)
Spec docs/specs/atlas_value_certificate_v1.md: a box in theta-coords with sigma >= V certified (A37's
"trivial Lipschitz" and 3S-soft forms; A85 §4.6 uses the trivial-reach form h = s_g - s0). Lean checker +
soundness `atlas_sound`: PASS => every packing in the box has sigma >= V; with V >= s0 this discharges the
box at EVERY window side with no dilation (state that corollary). Replay A37's 37 (+A51-NEW-0) boxes and
A85's drains as they land (isolated module).

## T3 — the zone-tree composition theorem
The generic statement the campaigns instantiate: given a stratum hypothesis (pins with slack delta_pin),
a cover (complete disjunction, per cover_invariance.md — formalise CI-1/2/3), and leaves of types
(K) case-LP kill (V.CASE, checkCaseI_kill + Lemma B at delta_pin), (C) logic kill incl. Lemma PD
(pin-drift: core meets the full drifted pin square at lambda=1 and lambda_max), (D) basin discharge
(box inside the basin => tube below shat) , (D') atlas discharge, (N) confinement/nofams leaf (Lemma
B-NO, Dilation.lean) — conclude: no packing containing the pins has sigma < shat at any side in
[shat - delta_basin, s0], and at shat only Trump images (Lemma P-TREE, protected_trees.md §2). Include
the mod-G bookkeeping of D.S6 (trump5 trivial stabiliser; D4 for k0_00 per K0-D4) and the ladder-
localisation clause (a (D) leaf is a full localisation of the free squares). Discharge `trump_residual`
and the protected-tier piece of `stratum_kill` DOWN TO leaf-certificate hypotheses (i.e. the axioms
become "these certificate files PASS" — the replay obligation, priced separately). Also A85's
stratum_kill_selected re-split if k0_00's route uses the corner seed (lean/k0_readiness_A85.md).

## T4 — window composition for C.A61
The 52-row scoreboard's full-window rows are parametric certificates (V.PARAM checkParamI_kill, Lean)
plus M1 transfers (Zones.lean) plus slack-core slabs (Lemma B). State the window-coverage theorem for a
stratum as a disjunction over its row's certificates and instantiate it for the rows that are done;
leave the 9 converting rows as named hypotheses.

Deliverables: Lean files + CI green + axiom audit; TopLevel roster note (what each remaining axiom now
reduces to); replay-cost table (per-certificate wall for tube/atlas/case/param) so the final replay wave
is priced; lean/README.md; depgraph notes on the six nodes ("Lean composition done; awaiting replay");
registry row; LOG.md; findings. Honest partials with named obligations beat claimed closes; T1+T3 landing
clean is a full success.
