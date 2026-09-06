# A105 — Conjecture LOCK-FREE(< 4): the wall statement (Fable lead, theory)

Context (2026-09-06). A103 (docs/proofs/noroom.md) proved Lemma ROT: at the weighted-Ψ minimiser over K0-BLOCKED
packings at side m, every intruder is HELD (no single-square rigid motion, translation or rotation, strictly opens its
active rows and strictly decreases its corner depth; exact first order, Gordan form; the PI's one-signed-torque rule is
Corollary ROT-TORQUE). It reduced DRAIN(W) — and hence the whole k0_00 kill, with no tree — to:

  **Conjecture LOCK-FREE(< 4).** Every K0-BLOCKED packing of 11 unit squares at side m < 4 has an intruder that is not
  held.

Evidence: true 12/12 on the corpus (sides 3.985–4.107; the unheld square is always a second meeter); Trump (K0-FREE) is
held at all five of its intruders, so no proof can go through one blocked corner — it must use TWO blocked corners; it
must fail at 4 + ε, where the jammed 4×4 grid lives (A104 is measuring the exact failure point and the lowest side of a
fully-held blocked packing — read its report if it has landed: attempts/A104-grid-lock/notes/). The proof shape A103
named (noroom.md §7): the eight intruders' contact cones taken JOINTLY along one wall. A held second meeter needs a
far-side contact on the wall side of its argmin point (ROT-TORQUE's zero-torque case); a wall of length < 4 carries
three unit footprints (WALL-3, docs/proofs/wall_budget.md) and cannot supply that contact at both of its corners at
once; the grid escapes because its wall carries exactly four footprints.

Read first: docs/proofs/noroom.md (all; §2 Lemma ROT-GRAD/ROT, §7 the obstruction, §8 composition and Lean shape),
docs/proofs/wall_budget.md (WALL-F, FLOAT, WALL-3), docs/proofs/tilt_floor_k0.md (CEIL, JAM-0, LOCK, MENU, ID),
docs/proofs/nocrit_k0_blocked.md (Lemma K: an intruder is x-side, y-side or corner-type; CLUSTER; COL), docs/proofs/
k0_blocked_side.md (SLIDE: d₂ ≥ ŝ − m), docs/proofs/flood_lemma.md §1 (SHELL: a crowder of an η-disturbed square is a
grazer of depth ≤ (1+√2)ε), attempts/A103-noroom/results/lockmap103.svg + results/lock103.json (which intruders are
held, by which contacts), docs/residue_map.md §5 (the drained records, drawn), attempts/A102-rigidity-drain/notes/
rigid102.md §4 (pinned contact sets: 32/33 pins are square–square).

## The target
Prove LOCK-FREE(< 4), or LOCK-FREE(m) for the largest m ≥ ŝ you can (m ≥ ŝ suffices for the window: state exactly
which m). Route to try first, in this order:
1. **The wall lemma.** Fix a wall with both its corners blocked (two exist whenever ≥ 2 corners are blocked; with all
   four blocked every wall qualifies — use the best one). Along that wall, the two corner crowds' second meeters each
   need, to be held, a contact on the far side of the argmin point that pushes toward the corner (make this exact from
   ROT-GRAD: which contact directions can carry the corner-ward virtual push; separate the cases x-side / y-side /
   corner-type of Lemma K, and vertex-argmin vs edge-argmin). Then count along the wall: the pushers' footprints, the
   crowds' footprints (CEIL bounds their depths, JAM-0 their offsets, SHELL the grazers), WALL-3's three-footprint
   budget for a wall of length < 4. Show the two far-side pushers cannot both exist. Where the count needs a
   footprint width, use the tilted width cos θ + sin θ ≥ 1 and TF-U/LOCK for the tilts of wall-touching blockers.
2. If the wall lemma needs the pushers to be wall-touching and they need not be, use FLOAT (floating pushers priced)
   and CLUSTER (the pusher's own far-side cluster must be anchored — recurse once along the same wall).
3. If one wall does not close, use two adjacent walls sharing a blocked corner (the corner-type intruder is pushed in
   both axes; its two pushers occupy both walls' budgets).
Canaries, all mandatory: Trump satisfies every lemma (held 5/5, only TL blocked — your wall lemma must not fire on a
wall with one blocked corner); the 4×4 grid at 4 + ε (four footprints per wall) must NOT be excluded; the drained
records (3.985, 3.9907) must have the unheld intruder your proof predicts (check against lockmap103).

## Deliverable
docs/proofs/lockfree.md: theorem (with its exact m range), the wall lemma and its case split, proof or the exact
obstruction (the configuration of footprints along one wall that defeats the count, drawn as poses if realisable —
conventions of docs/residue_map/gen_nondrainers.py, geometry-checked), Lean shape against noroom.md §8, ledger with
[T]/[S]/[M]/[F]/[C]. Numerical chores allowed (≤ 1 process, BLAS-pinned, pure geometry, seconds; the box is loaded:
headroom > 6 GB commit and > 3 GB free physical). A57/A60/A61/A96/A104 untouched; frozen verifiers untouched; git =
fetch + plain merge + push own paths (no rebase/autostash/reset). Writes: attempts/A105-lockfree/{notes,code,results,
logs}, docs/proofs/lockfree.md, depgraph K0.RESN chip (owner A105) + lean/depgraph.svg re-rendered, registry row,
LOG.md. Report ONCE, tersely: the theorem and its m range first (or the obstruction), the wall lemma second, canaries
third, pointers last. No waiting-state messages.
