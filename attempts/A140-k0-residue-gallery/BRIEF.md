# A140 — the k0 residue gallery, v3: one page per converged-alive cell with the day's drawing rules, the polygon core measured on k0, and the candidate cover per cell for the PI's review (Opus)

Context (2026-09-07 evening). The k0_00 residue is exactly twelve converged-alive cells (A115 T6 `0d4c79fd`,
attempts/A115-k0-corner-rows/notes/t6_report.md, results/t6_summary.json; τ = budget, minmass 1, converged — no LP time
kills them): level-1 `l1_071, l1_104, l1_124, l1_148, l1_153 (a Trump image — must stay alive), l1_158, l1_159`;
level-2 `l2_p114_001, l2_p65_101, l2_p65_111, l2_p74_001`; A85 `s3_far_BL389484_TR018470`. The PI reviewed A107's
K-gallery (docs/shadows.md Part II, docs/shadows/K01..K30.svg, review.csv) BEFORE A115's last pass; three of the
twelve (`l1_124, l1_148, l1_158`) have no A107 shadow at all (A128 built near-packings from their supports). Since
that review the drawing rules changed (PI, 2026-09-07): the example hypothesis square at the CENTRE of the box and
the CENTRE of its tilt window (cyan H, tilt printed), faint outlines at the extremal tilts, pins drawn only as pins,
and — from docs/residue_map/gen_a57_lp.py `0fbbc165` — every dual-support column that overlaps a hypothesis square at
EVERY pose of its box outlined red-dashed with the overlap printed. Two new objects also exist that the gallery has
never shown: the polygon core K′(B) (A132 `7d5e9070`, attempts/A132-polygon-core/code/polycore.py; A135's
code/exactcore.py certifies half-sides) and the k0 cells' candidate covers (A113's re-branching rule: branch on the
slot the support keeps occupying; A118's lane count; A107 Part II's slot census). The polygon core was measured on
A57/A60 only — never on k0, where a level-2/3 cell carries TWO or THREE conditioned squares and the K′-vs-K′ test
between conditioned boxes, and K′ vs the container walls, is the only geometric kill available (k0 has no pins).

Read first: docs/shadows.md Part II and A107's code/{extract,svg,writeup_k0}.py (the K-gallery format the PI knows),
docs/residue_map/gen_a57_lp.py (the current drawing rules — reuse its panel code; for k0 there are no pins, so the
"feasible centre" rule is against the container and the OTHER conditioned boxes' K′), A115's t6 files and the cell
records (A99/A113 node jsons: `packing`, `hyp.cores` with boxes, `atoms_all` if stored), A113's notes (support slot
census, the re-branching rule), A128's results/nearpack128.json and A130's results/flush130.svg (the near-packings
and flush geometry of K03/K06/l1_124), docs/shadows/review.csv (the PI's shorthand: `r <sq> <cell>`, `ns`, `i`, `g`,
`st4`, `fl`, `?`).

## T1 — the polygon core on k0 (measurement, minutes)
For each of the twelve cells (and, cheaply, every open k0 cell A115 lists): K′ of every conditioned box (exact vertex
certification by A132's test); (i) support columns and full-pool columns excluded by K′ but passing K(a), with the
weight they carry vs the slack; (ii) K′ vs container: any conditioned box whose K′ leaves the container is dead (T5-
type); (iii) K′ vs K′ between conditioned boxes of the same cell (the pair kill of budget §D item 1): any pair whose
polygon cores meet is dead by `core_meet_same_square`'s set form (one witness point). Table by cell; sample line per
count (drawn → tested → hits). No LP unless (i) removes weight ≥ slack on a cell — then ONE in-vitro re-solve on that
cell (240 s, 2 processes BelowNormal, recorded as "LP-dead under polygon core, certificate pending" — the s0-only
kills are certifiable by exact cores under the frozen verifier per A135; say which).

## T2 — the gallery, v3
`docs/shadows/k0v3/<cell>.svg` for each of the twelve, in the reviewed two-panel form: LEFT = the LP dual support
drawn by weight (A107 v2 conventions) with the day's rules — every conditioned square as cyan H at box centre and
mid-tilt with faint extremal outlines, K′ drawn inside each H as a polygon, impossible columns red-dashed with the
overlap printed, the container; RIGHT = the snapped near-packing (A107's snap, or A128's near-packing where A107 has
none) with the same square names and orientation as the right panel of the old K-gallery (the PI labels from the
right panel). Under each: the cell's box(es), τ/η/minmass, the support's slot census (which slots are met, singly or
doubly, by which squares — A113's rule), the lane count (A118), and ONE candidate cover per cell in words and as a
third small panel: the re-branching split A113's rule proposes (the slot the support keeps occupying, drawn as the
box to branch on) or the two-meeter cover (A118 T4) — with what each would need to be a certified leaf. Also a fresh
review sheet `docs/shadows/k0v3/review_k0v3.csv` with the same columns as review.csv plus `polycore_status`,
`candidate_cover`, and empty PI columns. Every drawn square geometry-checked (containment, and every red-dashed
column's overlap re-verified by SAT at 7³ poses); the index page docs/shadows.md gets a Part III pointing here.

## T3 — the one-table summary for the PI
docs/shadows/k0v3/README.md: the twelve cells × (level, s* of the near-packing, shadow family if any, polycore
status from T1, candidate cover, what the PI's reading would decide). Plus the three cells that had no drawing
before, flagged.

Constraints: ≤ 2 processes, BLAS-pinned, BelowNormal (A136/A139 running; the PI is using the machine); READ-ONLY on
every campaign and on A107/A113/A115/A128/A130/A132/A135 files (new files only under attempts/A140-k0-residue-gallery/
and docs/shadows/k0v3/; docs/shadows.md append only); no LP beyond T1's clause; NO recursive deletes;
PYTHONDONTWRITEBYTECODE=1; git = fetch + plain merge + push own paths with explicit pathspecs. Report ONCE: T1's table
first, the list of SVGs with one line each second, pointers last. No interim messages.
