# A32 — joint structure-B&B frontier pilot (Opus)

Goal: the go/no-go measurement for the structure-first endgame. Run a branch-and-bound over PARTIAL
contact structures with the kill cascade applied at every node, and measure the FRONTIER: surviving
partial structures per depth, kill shares per test, cost per node, and the growth trend toward
k = 11. NOT a proof; an instrumented search. Read first: docs/proofs/structure_lemmas.md (Soundness
ledger), docs/proofs/drain_lemma.md v3, attempts/A31-structure-count/results/count_report.json
(+ its code/lib0.py — reuse the validated filters), attempts/A30-t3-pilot/t3lib.py (Farkas test).

## Node semantics (soundness of partial-node kills)
A node = a partial structure (loaded squares, contact edges, optional decorations) meant to
represent ALL completions (more edges/squares/decorations may be added up to k ≤ 11 and the caps).
 - MONOTONE tests (kill valid at any node — constraints only accumulate under extension): tilt
   propagation, rotation-system/embedding consistency, metric interval feasibility (STRENGTHEN
   A31's: add triangle closure, tilt-class data, and the L2 collinearity equations for degree-2
   squares COMMITTED as struts — that codim-1 equation is what should make the thin branch die
   fast), non-planarity, L5 caps, per-wall ≤ 3 (promote it: the proof in A31's report is sound).
 - STRUCTURAL requirements (L1 degree ≥ 2, L6 wall-to-wall chain, flush-mandatory): NOT monotone.
   Apply as EXTENSIBILITY checks — kill only if no completion within the remaining square/edge/cap
   budget can satisfy them (e.g. remaining squares cannot bridge the walls). Otherwise defer.
 - Branch moves: add an edge (canonical-extension discipline — orderly generation so no duplicate
   subtree is explored twice; reuse A31's canonical forms), add a square, commit a decoration class
   (flush vs corner-on-edge; tilt class), or CLOSE the node (no more edges ⇒ structural checks fire).

## Seeding
Grow from the mandatory skeleton, not from empty: L7/L6 anchor a loaded square on each of two
opposite walls; A21 structure theorems (corner-zone and side-zone squares exist at ≤ 3.88 — cite,
don't re-prove) may seed wall contacts. State the seeding assumptions explicitly in the report.

## Kill cascade (cheap → expensive; instrument each)
 1. tilt propagation fixpoint  2. rotation-system consistency  3. metric interval feasibility
 (strengthened as above)  4. Farkas first-order test on the wide cell via t3lib (sample-based is
 fine; measure cost/benefit)  5. case-LP (A27 machinery) — STUB or sample only, measure cost on ~10
 nodes, do not integrate fully  6. FJ solve — leaves only, sample ~10, measure cost.
The pilot's product is the MEASUREMENT, not exhaustive kills: where full soundness is deferred,
count the node as SURVIVING and log the deferral.

## Report (results/frontier_report.json, findings block; terse REPORT)
Frontier size vs depth (edges, squares) with and without each cascade stage (ablation on samples if
full reruns are dear); kill shares per stage; sec/node per stage; the growth trend and an honest
extrapolation: does the frontier at k = 11 project to 1e4-1e6 solvable nodes (GO) or explode (NO-GO)?
Compare directly against A31's flat counts at matching k (the early-kill collapse factor). Trump's
structure must SURVIVE the search to its leaf (soundness canary — assert it). Gap list as usual.

## Constraints
Budget ≤ 4 h wall, ≤ 6 workers, RAM guard, checkpoint per depth, resumable. Do not touch A29/A30/
A31 state (read-only reuse). Terse traffic.
