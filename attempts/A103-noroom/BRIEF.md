# A103 — NOROOM: no K0-BLOCKED packing below side 3.9, or the drain in the window, or the exact frame (Fable lead, theory)

Context (2026-09-06). k0_00 is the last unkilled class; its tree is priced at 9,300–21,700 CPU-h (A99, window-valid).
The PI's conjecture, in its useful range: **for every side m in the window W = [3.82, ŝ] (ŝ = 3.877083590…), every packing of
11 unit squares at side m with every corner cell met by ≥ 2 squares (K0-BLOCKED) has room to drain, i.e. a packing with
a simple square exists at the same side.** Above side 4 the question is vacuous (the 4×4 grid), so the theorem lives
strictly below 4, and the evidence says the truth is stronger than drain: no K0-BLOCKED packing has ever been found
below 3.985 (1,072 directed descents at four depth floors, k0dir2_87; 8 earlier A87 packings; strict85), the two found
below 4 (3.985, 3.9907) both drain to k = 7 by a single square with room, and the nearest one sits 0.108 above ŝ.

Deliverable, in order of preference — stop at the first that closes:
  (A) **Theorem NOROOM**: no K0-BLOCKED packing exists at side m ≤ 3.9 (or the largest m* ≥ ŝ you can prove).
  (B) **Theorem DRAIN(W)**: for m ∈ W, K0-BLOCKED at m ⇒ a k ≥ 1 packing at m (existence, not a motion).
  (C) the exact obstruction: a frame (contact structure + a realising configuration, or the exact reason none is
      excluded) drawn so the PI can look at it; state what single fact about it would finish the proof.
Composition: with (A) or (B), k0_00 = (window kills of k ≥ 1) + this theorem; no criticality, no selection, no tree;
hypotheses K0-O1-ALL (state the Lean shape against Composition.lean / Slide.lean conventions).

Read first, in this order: docs/residue_map.md §5 (the two sub-4 blocked packings, the PI's drain, A102 outcome, the grid
non-drainers and why they are irrelevant), docs/proofs/nocrit_k0_blocked.md (Theorem NOCRIT-SEL: at a Ψ-minimal
σ-minimiser every intruder is anchored in every cardinal retreat direction; residue RES(4) = the frame; Lemmas K, CLUSTER,
COL, PLATEAU), docs/proofs/frame_census.md §0–§2 (roles: a square is a home square of ≤ 1 corner, n_c ≤ 5, the nine
role patterns; Lemma F7: COL's ≥ 3 clause is vacuous at L1; W-GEN: with corner weights every rate-1 cluster is strictly
or wall-anchored, the only plateaus are tilted-D rate ties), docs/proofs/flood_lemma.md §1–§2 (SNAP destination form,
MULTI, SHELL grazer bound (1+√2)ε, CELL-INTERLOCK), docs/proofs/k0_blocked_side.md (SLIDE: d₂ ≥ ŝ − m; Theorem N),
docs/proofs/tilt_floor_k0.md (CEIL: min(d₁, d₂) ≤ 1 − 1/√2; TF-U, LOCK, MENU, JAM-0, ID), docs/proofs/wall_budget.md
(WALL-F, FLOAT), attempts/A102-rigidity-drain/notes/rigid102.md (the drain table; pins are square–square 32/33;
first-order freedom does NOT predict the drain — the rule is room), attempts/A87-drain-flow/code/pi_drain_3p9907.py.

## The three ingredients that were not on the table when RES(4) was priced — use all three
1. **Rotational retreat.** NOCRIT-SEL retreats by cardinal translation only. In the 3.9907 record the BR second meeter
   (square 3, 1.31° off axis, intrusion 1.02·10⁻³ = 0.5·sin θ minus its lift) is anchored against every translation
   (its upward cluster reaches the top wall through square 8) and still rotates out: all three contact torques about
   its centre have one sign. State and prove Lemma ROT: at the Ψ-minimal minimiser, every tilted intruder whose
   intrusion is tilt-borne is torque-locked (contacts with torques of both signs about its centre, or a contact at its
   intruding vertex); otherwise rotating toward axis decreases Ψ at the same side (first-order; handle the
   second-order/tangency cases by the selection, as W-GEN handles ties). This shrinks RES(4) to torque-locked frames.
2. **Chains are too long for the box.** A wall-to-wall anchoring chain of ≥ 3 squares spans ≥ 3 > m − 1, and 3 < m, so
   it cannot be flush at both walls; at a Ψ-minimal point with corner weights it is flush at the far wall (W-GEN), and
   then its near-end square intrudes its corner by ≥ 4 − m ≥ 0.123 (axis-aligned; more when tilted, since the width is
   cos θ + sin θ) and its far-end square occupies the far corner slot: if that square is flush to the adjacent wall it is
   SIMPLE and the packing is k ≥ 1 (done); if not, it is itself an intruder whose own holding chain runs back the other
   way, and the two chains share squares. Make this exact (Lemma CHAIN): for each corner pair (adjacent and opposite)
   and each axis, what a wall-anchored or corner-to-corner-anchored column of the RES(4) frame forces on the depths
   at its two ends, against SLIDE (d₂ ≥ ŝ − m) and CEIL (min(d₁, d₂) ≤ 0.293) at both corners.
3. **The corner regions are small and the free squares are few.** Home squares of a corner lie in [0, 1 + √2]² (F1);
   eight intruders sit in four such regions, and three free squares must supply all bracing between four regions in a
   box of side < 3.88 in BOTH axes (frame = columns in both axes through all four crowds). Count what the three free
   squares can touch (a unit square meets at most how many of the four corner regions? — the regions are ≥ m − 2 − 2√2
   … compute it) against what the frame needs, with Lemma CHAIN's forced depths as the load.

## What to expect and what to avoid
* The pure combinatorial count was measured (A91) and loses by 28 orders; do not re-run it. The geometry is where
  frames die: use the forced depths (ingredient 2) as inequalities, not the count of contacts.
* Trump is the canary for every lemma: it is K0-FREE (three corners singly met) with a rigid, torque-locked TL 2-crowd
  {4, 6} at depths 0.155/0.168, RES(1) realised, wall-anchored through the slot squares. Every lemma must be satisfied
  by Trump; the contradiction must use ≥ 2 blocked corners (A90 §5) and must fail at side 4 + ε (the grid).
* If (A) fails, try (B); if (B) fails, produce (C) as an exact object — a contact structure with a realising
  configuration if one exists (write it as poses so `docs/residue_map/gen_nondrainers.py`'s conventions can draw it,
  every square geometry-checked), or the exact family of frames left, with the one fact that would kill it. Do not
  hand back a census.
* Numerical experiments are allowed as chores (≤ 1 process, BLAS-pinned, pure geometry, seconds; the box is loaded:
  headroom > 6 GB commit and > 3 GB free physical) — e.g. directed search minimising side subject to K0-BLOCKED and
  full first-order anchoring of all eight intruders with rotation, to measure where rigid blocked frames first appear.
  A57/A60/A61/A96 untouched; frozen verifiers untouched; git = fetch + plain merge + push own paths (no rebase,
  autostash, reset).

Writes: attempts/A103-noroom/{notes,code,results,logs}, docs/proofs/noroom.md (the deliverable: theorem, lemmas ROT,
CHAIN, the count, proof or exact obstruction, Lean shape, obligations ledger with [T]/[S]/[M]/[F]/[C] labels),
depgraph K0.RESN chip (owner A103) with lean/depgraph.svg re-rendered, registry row, LOG.md. Report ONCE, tersely: which
of (A)/(B)/(C) closed and the side threshold first; the lemmas proved second; the obstruction (if any) third; pointers
last. No waiting-state messages.
