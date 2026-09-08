# A142 — the A57/A60 review gallery: the surviving alive nodes drawn in A140's format with exact pin cores and polygon cores, ranked by subtree cost, for the PI's second pass tonight (Opus, drawing only)

Context (2026-09-07 evening). The PI is reviewing drawings for geometric kills before any long run (today's reading
of two pages produced the pin-clip and the polygon core; a third produced the K′ lane kill on s3_far). The A57
LP-support figures that exist (docs/residue_map/a57_lp_support.svg, four nodes; A107's S-gallery by shadow family)
predate both levers and draw pins at their stock cores. A140 (`73eaf5e2`, attempts/A140-k0-residue-gallery/code/
gallery140.py, docs/shadows/k0v3/) is the current format: LEFT = LP dual support by weight, every conditioned square
as cyan H at box centre and mid-tilt with faint extremal outlines, K′ drawn inside each H, columns overlapping a
hypothesis square at every pose red-dashed with the overlap printed; RIGHT = the snapped near-packing with the
square names the PI labels from; below: box, τ/η/minmass, slot census, lane count, candidate cover.

Population: the A57 alive nodes that SURVIVE today's kills — start from the 414 ALIVE + 193 FAIL work-owing nodes
(A131's corpus, attempts/A131-pin-clip/results/corpus131.*), remove the 132 pin-clip kills (results/backlog_kills.jsonl),
the 64 polygon kills (attempts/A135-polycore-verifier/results/polycore_kills.jsonl), A135's 3 certified LP kills and
A124's 54 trim-empty nodes, and every descendant of a killed node (monotonicity) — print the arithmetic. Add A60's
alive nodes (A107's shadow_nodes.json, 283 with supports) as a second section. Rank by subtree cost: for A57 use
docs/budget.md §B's per-level costs times the node's live descendants (or 8^(levels remaining) with the measured
per-level alive fraction) — state the formula; draw the top 40 of A57 and the top 20 of A60.

Draw: pins as PINS only (zero-tilt-width cores) at their EXACT cores (A135's exactcore.py: half-side 1/2 − δ/√2,
certified), each pin's K′ = that exact square drawn as a thin inner outline; the conditioned square's K′ (A132's
polycore.py, certified vertices); the pin-clip result — the clipped centre box inside the original box (A131's
pinclip.py, per tilt sub-bin union); the lane count per corner and per wall slot with K′ (if A141 has landed, its
K′ lane results; else A118's stored verdicts, labelled as axis-core verdicts); red-dashed impossible columns
(against H's K′ AND against the exact pin cores — A132's attribution showed a quarter of the excluded weight is the
pins'). Under each page one line: "what to look for" = the corners/slots whose lane count is 1 (a second meeter
allowed) and the pockets between H's K′ and the nearest pin narrower than 1. Every drawn square geometry-checked;
every red-dashed column re-verified by independent SAT at 7³ poses.

Deliverables: docs/shadows/a57v3/<node>.svg (60 pages), docs/shadows/a57v3/README.md (the ranked table: node, class,
level, subtree cost, family, lane-1 corners, narrowest pocket, what to look for), docs/shadows/a57v3/review_a57v3.csv
(review.csv's columns + polycore_status, clip_kept, lane_1_corners, narrowest_pocket, empty PI columns), docs/
shadows.md Part IV (append only). Constraints: drawing and geometry only, no LP; ≤ 2 processes BelowNormal (A136/
A139/A140/A141 running; the PI is using the machine); READ-ONLY on every campaign and on A107/A118/A131/A132/A135/
A140/A141 files (new files only under attempts/A142-a57-review-gallery/ and docs/shadows/a57v3/); NO recursive
deletes; PYTHONDONTWRITEBYTECODE=1; git = fetch + plain merge + push own paths with explicit pathspecs; registry row,
LOG.md. Report ONCE: the population arithmetic and the top-10 table first, the list of pages second, pointers last.
No interim messages. Target: the first 20 pages pushed within 90 minutes (push them as a first commit, then the rest).
