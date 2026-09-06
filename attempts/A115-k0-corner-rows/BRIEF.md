# A115 — corner-crowd rows at the k0 NODE level: do the K01 "room" cells die? (Opus chore, ≤ 2 CPU-h, resumable)

Context (2026-09-06). A107 Part II (`87ed93bb`, docs/shadows.md) drew the LP dual supports of the 217 alive k0_00 cells
(A38 root, A99, A85): 30 shadow values explain 161; **K01 — the support minimises to side exactly 4.000 (a corner or
slot left empty or singly met, "room") — explains 84 of them**, exactly as S01 does for A57. A k0 packing with a
corner cell met by ≤ 1 square is K0-FREE and teleports into k1 (Lean, CC-2), so those supports describe configurations
that are already dead by theorem; the k0 tree's LP does not carry that hypothesis. A92 built the crowd certificate
for k0 (docs/proofs/k0_blocked_side.md §2.4, Lemma CW: incidence rows "every corner cell is met by ≥ 2 non-conditioned
squares", verified by two frozen runs; attempts/A92-blocked-side/{code,certs}) and found the ROOT LP refuses at depth
δ ≤ 0.1 and passes only at δ = 0.3, which CEIL makes vacuous. Unlike A94's slot rows (A109: multiplicity — one
placement meets two or three slot boxes at once), the four CORNER cells are ≥ m − 2 apart, so a unit square meets at
most one of them: the incidence budget is exact and re-pricing by multiplicity cannot happen. The open question is
whether, at the NODE level (a conditioned box), depth-0 or shallow-depth corner rows kill the K01 cells or the LP
re-prices to a different room configuration.

Read first: docs/proofs/k0_blocked_side.md (Lemma CW §2.4, the two-run verification, the δ sweep), attempts/A92-
blocked-side/{notes,code} (reuse the row builder verbatim), docs/proofs/k0_route.md (K0-FREE/CC-2; what "met" means
at depth 0 vs the strict convention), attempts/A107-shadow-gallery/results/shadow_nodes_k0.json (the 84 K01 cells and
which corner their support leaves singly met), attempts/A38-root-power/results/l1_nodes/*.json (the cell LPs: hyp,
packing, rows_all, tau, budget), attempts/A113-k0-manifold-distance/results/t2_supports.jsonl, attempts/A109-node-
crowd/notes/report.md (the failure mode to compare against).

## T1 — which corner, how deep
For each of the 84 K01 cells: which corner cell(s) the dual support leaves empty or singly met, and at what depth the
existing meeters sit (the support's placements vs the four corner cells at s0). Table by corner and depth.

## T2 — node-level corner rows
On ≥ 30 of them (stratified over the four corners and levels 1–3), add Lemma CW's corner incidence rows to the node
LP at δ ∈ {0 (meet, licensed everywhere at s0), 0.05, 0.1} (own copies; the conditioned square is exempt from the
rows, as in A109's budget bookkeeping), re-solve with a 900 s cap (A111: the NO/row side is a convergence-time
problem), and report per node and δ: τ, η, converged, dead; and whether the new support is another K-shadow (A107's
dedup) or a re-priced room configuration. For the LP-dead ones certify a sample (≥ 6) with the frozen verifier in
A92's two-run form; report PASS/FAIL and hole counts. Trump canary: the three Trump-image cells (A38 idx 21/152/153)
must survive at every δ ≤ 0.155 (Trump's TL crowd depths 0.155/0.168; Lemma CEIL-T).

## T3 — verdict
One line: "corner rows at δ = … kill X of Y K01 cells at the node level and certify Z of Z" or the failure mode; the
price per cell; what it removes from the k0 tree projection (A99's 9,300–21,700 CPU-h; A113's per-cell costs) if
deployed at the root level of A85's tree (the rows are part of the node hypothesis; a certified node is the ordinary
A92 two-run certificate — say what the Lean shape is against k0_blocked_side.md §2.4).

Constraints: ≤ 2 processes, BLAS-pinned, commit gate 6144 MB and > 3 GB free physical before every LP; resumable
per-cell record files; READ-ONLY on A38/A85/A92/A99/A107/A113 and every running campaign (A61, A112, A114, A96);
frozen verifiers byte-identical; git = fetch + plain merge + push own paths. Writes: attempts/A115-k0-corner-rows/
{code,results,notes,logs}, registry row, LOG.md, one-line note on depgraph K0.CW. Report ONCE: T3 first, T2 table
second, T1 third, pointers last. No interim messages.
