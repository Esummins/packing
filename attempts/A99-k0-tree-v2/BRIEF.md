# A99 — the k0_00 tree, next generation: measure the three reductions on A85's own nodes (Opus, engineering pilot)

PI target: ~10x on the k0_00 tree (A85 interior-first, 3,200-7,000 CPU-h at s0, notes/pilot_report.md + k0_route.md
s.8; 216 level-1 cells of T(s0) x [0,90), bisection b = 8, ~6,290 nodes at levels 2-4 under f2 = 0.85; per node ~1,000 s
LP + 630-860 s certification (+800-1,200 s per eps_geo round); the 3e3-3e4 spread is f2 = 0.33 measured vs 0.85 assumed).
Three reductions to MEASURE, not argue:

## R1 — failures certify instead of descending (target: f2 -> > 0.9)
A96 found A57's certification FAILs are sliver artefacts: 82/82 closed by re-verifying the SAME certificate on the
witness sub-windows (resolve96.py, median 4 s, no new LP). Apply resolve96's method to every FAILed / eps_geo A85 row
(results/a85_lp_samples.jsonl, results/nodes/k0_00/*, certs/k0_00/) at fixed side s0 (sub-boxes instead of sub-windows:
re-run verify_case.py restricted to the witness cells with depth raised) and report the fraction that close without a
new LP; then re-project the tree's node count with the measured effective f2 (levels 3-4 shrink by (1-f2) x 8 per level).

## R2 — corner-depth pattern at the root with exempt boxes (Lemma ID's consumer, never run in the tree)
Lemma ID (docs/proofs/tilt_floor_k0.md s.7; certificate attempts/A89-tilt-floor/certs/k0_00/R1_4shallow_d0.3.json,
window-valid): a corner all of whose intruders are shallower than delta has (0, 1-delta)^2 empty => an EXEMPT box
(A89-O3's exempt-family form, verify_case.py's nofam exemption; overlapping boxes, per A92's engine law). Branch the
ROOT on the shallow/deep pattern at delta = 0.3 (2^4 patterns mod D4 = 6; all-shallow dead by the certificate): for each
of A85's 12 stored level-1 rows (and the 3 undecided level-1 cells), re-run the node LP with the exempt boxes of 1, 2
and 3 shallow corners added (and, at deep corners, nothing new — or optionally the depth-capable pair census restricted
to depth >= 0.3 as a hypothesis with cores, A85's pair machinery) and report tau/eta/verdict per pattern vs the plain
row. Headline: how many of the 216 level-1 cells (sample >= 20 cells across the T(s0) partition) DECIDE (kill) at the
root under each pattern; the projected level count removed.

## R3 — per-node cost
(a) Certification with --jobs 4 vs 1 on 10 A85 certificates (wall and correctness identical); (b) LP warm start from
the parent/sibling column pool (A57's warm57 pattern) on 10 nodes vs cold; (c) parametric emission of 5 A85 level-1
kills with A96's to_param96 + verify_param.py over [3.82, s0]: wall vs fixed-side, window coverage — this prices the
WINDOW for the k0 tree (A85's numbers are s0-only). Report per-node cost under (a)+(b) and the window factor under (c).

## Verdict
Combine: projected k0_00 tree CPU-h with R1, R2, R3 separately and stacked, at s0 and window-valid; against 3,200-7,000
(s0) and 4x that (four sides); state the assumptions and what remains unmeasured (level-2 descent rate at delta_pin =
1e-2 — A96's 2.36x finding applies here too). Constraints: <= 2 processes of your own (the box is at its cap; A96 owns
A57's queue — coordinate by leaving a note in attempts/A96-a57-parametric/notes/ if you need a slot), BLAS-pinned, the
6144 MB commit gate, Start-Process-detached drivers, one terminal wait; A57/A60/A61/A96 untouched; frozen verifiers
copied byte-identical, never edited; writes under attempts/A99-k0-tree-v2/{code,results,notes}, registry row, LOG.md,
depgraph K0.TREE note (chip -> A99; fetch + plain merge + push own paths only). Report once, tersely: the stacked
projection first, then R1/R2/R3 each with its measured number.
