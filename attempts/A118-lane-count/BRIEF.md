# A118 — the lane-count leaf: a slot that at most ONE non-pin square can reach is dead by teleport (Opus chore, geometry, resumable)

Context (2026-09-06, PI reading of K10/K01). Proved and in Lean: a corner cell met by ≤ 1 square teleports into k1
(K0-FREE / CC-2, docs/proofs/k0_route.md); a usable completable slot of a pinned class met by ≤ 1 non-pin square
teleports into the extension class, which is dead on the window (SLOT-CROWD, docs/proofs/slot_crowds.md §2; usable
slots per class listed there and in docs/residue_ledger.md §1a). What a tree node FIXES: the walls, the class pins,
and the conditioned square's core (its inscribed square over the box's pose range; A96's tight core `pinguard.tight_a`,
domain-asserted). The other squares are unlocalised. The LP's dual support is a witness, not a hypothesis (A115: no
weighted row can encode "singly met"; A112: k0 branching does not move τ). The sound leaf: **LANE-COUNT — for a node
and a usable cell C, compute the maximum number of interior-disjoint unit squares (any tilt) that can simultaneously
have open-interior intersection with C while avoiding the walls, the pins (at their δ = 10⁻² slack: use the pin's
slack core K_P, i.e. the pin anywhere in its slack box), and the conditioned core; if that maximum is ≤ 1, every
configuration satisfying the node's hypothesis has C met by ≤ 1 non-pin square, so the node is dead by teleport.**
Nothing about the free squares is assumed.

Read first: docs/proofs/k0_route.md (K0-FREE; what "meets" means — open interior), docs/proofs/slot_crowds.md
(SLOT-CROWD, usable slots, the extension classes and their window status — a slot is usable only where its
extension is certified: k6_07 is now full-window (A114), so BL(0,2) is usable for trump5 everywhere on W),
attempts/A101-flood-lemma/notes/a101_report.md (SNAP-T, the leaf that needed the cell EMPTY and fired nowhere — this
one needs ≤ 1 meeter), attempts/A85-k0-route/results/ (the corner "reach" work: at the k0 root without a conditioned
square reach never separates — say how this differs), attempts/A96-a57-parametric/code/pinguard.py (tight_a,
kill_core, the octagon test), attempts/A57-shadow-trees/results/tree/**/<node>.json + A60's and A38/A85/A99's node
jsons (hypotheses: hyp.cores; box; class), attempts/A107-shadow-gallery/results/{shadow_nodes,shadow_nodes_k0}.json,
docs/shadows/review.csv (the PI's readings will land here — K10: "only f3's core is close enough to intrude BR").

## T1 — the leaf, exactly
For cell C (a unit cell at a corner or a usable slot), the region R(C) = {poses of a unit square with open-interior
intersection with C, inside the container, interior-disjoint from every pin's slack core and from the conditioned
core}. LANE(C) = the maximum number of pairwise interior-disjoint squares with poses in R(C). Compute it soundly:
an UPPER bound suffices for the kill (LANE ≤ 1). Route: (a) if R(C) is empty, LANE = 0; (b) if every pose in R(C)
overlaps every other pose in R(C) (pairwise: for all p, q ∈ R(C), Q(p) ∩ Q(q) has nonempty interior), LANE ≤ 1 —
certify by interval arithmetic over a box cover of R(C) with the octagon/Minkowski test (as in T5″), or by a
convexity/width argument where R(C) is thin (e.g. C's approach is a lane narrower than 2 in the transverse direction,
so two unit squares cannot sit side by side in it — state the exact criterion and prove it); (c) otherwise LANE ≥ 2,
report the two witnesses. Every LANE ≤ 1 verdict confirmed by ≥ 10⁴ sampled pose pairs from R(C) (no two disjoint).
Trump canary: trump5's root and Trump's own cells must NOT fire on BL(0,2) (Trump's upright and sq7 both meet it)
nor on TL(0,0) (its 2-crowd); state which cells of which nodes are allowed to fire in trump5 (the slot must be usable
on the node's side range).

## T2 — yield
Run over: every open/alive node of A57 (both classes, all levels; the 1,536 open boxes + the alive-at-LP list), the
325 alive nodes of A60's trump5 cover in A107's input, and the 217 alive k0 cells (corners only; k0 has no pins, so
the only obstacles are the conditioned core and the walls — expect few fires: an open corner has two lanes). Report
per class and level: nodes with some usable cell at LANE ≤ 1 (kills), the cell, LANE = 0 vs 1, and the overlap with
T5′/T5″/A112 kills (attribute incrementally, per the lab law). Sample-confirm every kill.

## T3 — price and Lean shape
Wall per node; kills by level; the CPU-h removed from A57's 10–11-day schedule and from A60/A100's protected-tier
model (a lane-count kill skips LP and verification: ~850 s per node); the exact statement for the frozen chain (the
leaf's claim = "LANE(C) ≤ 1 for the node's hypothesis" — a finite interval computation, a new leaf kind whose Lean
shape is teleport_packing (Selection.lean) applied under a hypothesis proved by the octagon inequalities: write it
against the T5 pattern) and what the verifier needs to check. One line: "lane-count kills X of Y open A57 boxes and Z
of the trump5 alive nodes, worth D wall-days" or the failure mode (which lanes stay open).

Constraints: ≤ 2 processes, BLAS-pinned, pure geometry (no LP), headroom > 6 GB commit and > 3 GB free physical;
resumable per-node records; READ-ONLY on every campaign (A57/A96 paused, A61/A114/A115/A116/A117 running); frozen
verifiers untouched; NO recursive deletes, PYTHONDONTWRITEBYTECODE=1; tilt intervals normalised to [0, 90], core
half-sides asserted ≤ 1/2; git = fetch + plain merge + push own paths (no rebase/autostash/reset). Writes:
attempts/A118-lane-count/{code,results,notes,logs}, registry row, LOG.md, depgraph note on the A57 node. Report
ONCE: T3 line first, T2 table second, T1 criterion third, pointers last. No interim messages.
