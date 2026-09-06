# A113 — where does the k0_00 tree's cost sit relative to the k ≥ 1 manifold? (Opus chore, read-only, pure geometry)

Context (2026-09-06). Every local minimum of the side found near ŝ has simple squares (Trump k5 at ŝ; S07 k6 at
2 + 4√2/3; the pinwheel k7 at 3.886746; every entry of docs/shadows.md down to 3.94 is k ≥ 5). The PI's proposal for
k0_00: guide the k0 tree by that evidence — coarse boxes far from the k ≥ 1 manifold (where the LP kills cheaply),
and near the manifold no LP at all, because that region is the K0-BLOCKED residue (teleport/K0-FREE proved; the
blocked remainder is Conjecture LOCK-FREE⁺(< 4), docs/proofs/{noroom,lockfree}.md). Guidance only affects branching,
never soundness. The measurement that decides whether it is worth building: is the k0 tree's alive/expensive
population concentrated near the manifold?

Read first: attempts/A85-k0-route/ (the k0_00 tree: root = 216 D4-quotiented depth-2 cells of T(s0) × [0, 90°) for the
first conditioned square; results/, notes/, the level-1 cell verdicts: PASS / KILL / FAIL / ALIVE, LP τ, η, times),
attempts/A99-k0-tree-v2/notes/report99.md + results/ (R1/R2/R3 measurements, the 12 FAIL certificates, the r1 ladder,
the stacked projection 9,300–21,700 CPU-h), docs/proofs/k0_route.md (K0-FREE/CC-2, teleport), docs/proofs/
k0_blocked_side.md (SLIDE, Theorem N), docs/residue_map.md §3–§6 (the k0 reduction chain and tree anatomy), docs/
budget.md (the k0 row), attempts/A107-shadow-gallery/notes/method.md (A85/A99 had no LP jsons in A107's format —
say what LP data the k0 cells do have on disk).

## T1 — distance to the manifold, per cell
For every level-1 k0 cell (and level-2 children where they exist): the conditioned square's box; its distance to the
k ≥ 1 manifold = the L∞ distance from the box to the nearest lattice cell centre of any corner lattice at s0 (position)
and the tilt distance to 0 mod 90 (report both, and a combined "η-ball" measure: the smallest η such that some pose in
the box is within η in position and tilt of a simple placement). Tabulate verdict (PASS / logic / FAIL / ALIVE) and
LP cost against that distance. The question: are the ALIVE and FAIL cells (the expensive ones) the near-manifold
cells, and are the far cells cheap PASSes?

## T2 — what the near-manifold cells' supports are
For the ALIVE/FAIL cells with LP data on disk: draw the dual support (docs/residue_map/gen_a57_lp.py conventions,
adapted to k0's hypotheses — no pins, one conditioned core) and classify by A107's method: which shadow (Trump image?
S07? S02? room?) the support is, and how many simple/near-simple placements it contains (a k0 support with a
near-simple placement is a configuration the teleport/SNAP lemmas cover if the cell is otherwise free). Count.

## T3 — the projection
Split A99's 9,300–21,700 CPU-h projection into the part spent within η of the manifold and the part spent farther,
for η ∈ {0.05, 0.1, 0.2}, using the measured per-cell costs and A85's §8.3 branching model. One line: "X% of the k0
tree's projected cost is within η = … of the k ≥ 1 manifold" — that is the amount LOCK-FREE⁺ (or any drain leaf) would
delete even if the tree runs, and the amount an adaptive-box-size tree could skip LPs on. Also: does any far cell
(η > 0.2) stay ALIVE at the LP? If none, the far region is already cheap and the whole k0 problem is the residue.
Canary: the eight Trump images must sit inside the near-manifold set at every η (they are k5 packings, distance 0).

Constraints: READ-ONLY on A85/A99/A57/A60/A61/A96/A111 files and processes; ≤ 1 process, BLAS-pinned, pure geometry
(no LP), headroom > 6 GB commit and > 3 GB free physical; frozen verifiers untouched; git = fetch + plain merge +
push own paths (no rebase/autostash/reset). Writes: attempts/A113-k0-manifold-distance/{code,results,notes,logs},
registry row, LOG.md, one-line note on depgraph K0.TREE (owner field untouched). Report ONCE: T3 line first, T1
table second, T2 counts third, pointers last. No interim messages.
