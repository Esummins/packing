# A141 — the lane test with polygon cores: a corner reachable only by one conditioned square is a K0-FREE kill; certify s3_far first, then every corner of every open k0 cell (Opus)

Context (2026-09-07 evening). The PI, reading A140's page for `s3_far_BL389484_TR018470` (docs/shadows/k0v3/,
attempts/A140-k0-residue-gallery/results/{t1_polycore,lane140,gallery140}.json; four conditioned boxes h0..h3, h2 =
[3.0993, 3.2382] × [3.2382, 3.3771] × [14.25°, 28.07°] near the TR corner, h3 = [2.4049, 2.5438] × [2.2660, 2.4049]
× [0°, 7.13°]): "h3's polygon core comes within 1 of the right wall, so no square can sit flush against the right
wall beside it; from that line up to h2's core is less than 1, so nothing fits in that region; and the pinch between
the two cores stops any square from the upper left reaching the wedge — all of TR is unreachable except by h2."
Coordinator's sampled check (outer approximation of K′): K′(h3) right side → right wall 0.978; K′(h3) top → K′(h2)
bottom over the strip 0.072; pinch 0.181; K′(h2) right → wall 0.233; K′(h2) top → top wall 0.094. Consequence: every
unit square meeting the TR corner region (centre within √2/2 of the corner) overlaps K′(h2) unless it IS h2, so TR is
met by at most one square, and a k0 packing with a singly-met corner is K0-FREE (teleport, Lean: `teleport_packing`
/ `k0free_kill`) — the cell is DEAD, not merely coverable. A118's lane test (attempts/A118-lane-count) returned
UNDECIDED on TR for this cell because it ran with the axis-aligned cores; the polygon cores (A132's K′, certified
vertex-wise; A140 has the 40-vertex polygons for all twelve cells) recover the pinch. This is the lane leaf with K′
in place of K(a): LANE_K′(corner) = number of NON-conditioned squares that can meet the corner without meeting any
conditioned K′; M = number of conditioned squares that can meet it; LANE + M ≤ 1 ⇒ dead (A118's leaf, unchanged in
logic, stronger in geometry).

Read first: A118's BRIEF, notes and code (the lane test: its box cover, interval arithmetic, `cover ok + confirm
clean` discipline, the LANE + M ≤ 1 leaf and its Lean shape), A140's results (the certified K′ polygons; lane140.json's
stored vs fresh verdicts), A132's code/polycore.py (vertex certification), A135's PolyCoreT5.lean
(`shared_point_same_square`, `checkVertexInPBox_sound`), docs/proofs/k0_route.md (K0-FREE), the cell records A140
used, docs/known_results.md (teleport, T5).

## T1 — s3_far, exactly
With A140's certified K′(h2), K′(h3) (rational vertices): (a) the three PI distances exactly (right-wall gap of K′(h3),
the pocket height, the pinch) and the two K′(h2) wall gaps; (b) the lane statement for TR: prove, by a finite cover
of the TR corner-meeting poses (centre box [s0 − √2/2, s0]² × tilt [0°, 90°), bisected with interval SAT — A118's
mechanism), that every such pose's square meets int K′(h2) (a single witness point per cover cell suffices: A135's
set form), hence M ≤ 1 (h2 only; check that h0, h1, h3 cannot meet TR from their boxes) and LANE = 0; (c) emit the
kill certificate (cover cells + witness points, rational) and an independent checker; sample line drawn → tested →
hits (≥ 10⁴ corner-meeting poses, all overlapping K′(h2)); (d) the Lean shape: lane leaf with K′ = the composition
`corner met by ≤ 1 square → K0-FREE → k1 → dead on W` with the cover as a decidable check — name the existing
lemmas it uses and the one new obligation, if any.

## T2 — every corner of every open k0 cell
Run the K′ lane test on all four corners of the twelve converged-alive cells and of every other open k0 cell A115
lists (A140's pool), with M counted from the conditioned boxes' K′ (a conditioned square can meet the corner iff some
pose in its box does — interval test), and report the table: cell × corner → (LANE_K′ upper bound, M, verdict), the
kills (LANE + M ≤ 1), and for the near-misses (LANE + M = 2) which two squares. Each kill: certificate + checker +
sample line. Compare with A118's stored verdicts (which corners flip from UNDECIDED/LANE ≥ 2 to a kill and why —
expected: the pinch between two conditioned cores). Also the A57/A60 alive nodes IF the cell format allows the same
test cheaply (the pins are cores too: K′(pin) = the exact pin square less its box, A135's exact pin core) — report
the count only, no certificates there (a different campaign's fold-in).

## T3 — fold-in
`results/polycore_lane_kills.jsonl` in A115/A99's node-record format (cell id, corner, LANE, M, certificate path),
one line in A115's t6_report.md's hand-off list saying these cells are dead by the K′ lane leaf pending Lean, the
docs/budget.md k0 row (cells removed and CPU-h credited by A115's per-cell costs), residue_ledger §4 one sentence
(the PI's reading and the count), docs/shadows/k0v3/review_k0v3.csv `polycore_status` column updated.

Constraints: pure geometry, ≤ 2 processes BelowNormal (A136/A139/A140 running; the PI is using the machine); READ-
ONLY on every campaign and on A118/A132/A135/A140 files (new files only under attempts/A141-polycore-lane/; the docs
above append/edit only the named lines); NO recursive deletes; PYTHONDONTWRITEBYTECODE=1; git = fetch + plain merge +
push own paths with explicit pathspecs. Report ONCE: T1's exact distances and verdict first, T2's table second,
pointers last. No interim messages.
