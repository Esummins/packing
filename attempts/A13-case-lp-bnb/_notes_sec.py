# -*- coding: utf-8 -*-
import io
notes = io.open('notes.md', encoding='utf-8').read()
s3 = u'''## 3. Sanity checks (Task 1)

(i) Root at s = 3.80 (H = ∅): D4 LP warm-started from A07's `v2_s3.80_rowonly.json`: τ = 10.44–10.47 (300 s, joint row/col
    generation oscillating as in A07); C1 LP (no symmetry, whole square, same warm start): τ = 10.495 (240 s, unconverged
    upper bound), consistent with A07's 10.42–10.49 and with the certified bound (dead at the root: 10.5 < 11).
(ii) A12 contrast at s = 3.86, Θ_B = [0,2]∪[32,36], corners fixed as (degenerate) core boxes = the four unit squares
    [0,1]²+images, budget 7: C1 LP τ = 7.000 (converged, 166 s) = A12's 7.000. Corners fixed AND the four side zones
    [0.5,0.75]×[1.2,s−1.2] excluded: **τ = 5.000 (converged, minmass 1.0, maxcov 1.0, 139 s; μ = 5 atoms of weight 1)** =
    A12's 5.000. This check FOUND A BUG in the first version of the NO-family filter (θ-margin also applied at the closed
    ends θ = 0/90 and centre margin at the domain boundary cx = 0.5, so upright rows / wall-touching rows were never
    dropped and the first two B&B runs' NO-branches were void — `NO(all corners)` came out alive with τ = 11.04; after the
    fix (margins only at interior ends) it is dead with τ = 9.41). Runs 1–2 (`results/t384_run{1,2}_aborted/`) are kept
    for the record but their NO-nodes are meaningless; run 3 (`results/t384c/`) is the reported one.
    A second lesson from (ii): from a cold start the C1 LP needs MASSIVE column generation to find the τ = 5 measure
    (with ≤ 200 columns/iteration and ≤ 80 column iterations it stalls at 6.9–7.0 for 12 min; with 1500 columns/iteration
    it converges in 2 min) — see §5 on LP convergence.

## 4. Run at s = 3.84 (Task 2) — `results/t384c/` (run 3), 8 workers, 300 s per node LP

Root (D4, warm from A07 `v2_s3.84.json`): τ = 11.033 (367 s; minmass 0.97, maxcov 1.04) — alive by 0.033. Fractional packing
zone weights: each corner zone 0.972, each side zone 1.000, interior 3.147 (the 4+4+3 structure of A07/A12).
Level 1 (branch on the corner family, D4-symmetric): 13 children:
* `NO(all corners)` (D4 LP): **τ = 9.41 < 11, dead by 1.59** (rows 0.98-converged): every packing at s ≤ 3.84 has a square
  with centre in a corner zone [0.5,1.1]² (up to symmetry: in corner 0).
* 12 YES boxes = corner zone [0.5,1.1]² split 2×2 in the centre × 3 in θ ([0,30],[30,60],[60,90]), budget 10, C1 LP:
  the 9 boxes NOT containing the corner-square placement (0.5,0.5,0°) (centre boxes [0.5,0.8]×[0.8,1.1] and
  [0.8,1.1]×[0.5,0.8], all θ, and [0.8,1.1]²×[30,60]; the two other [0.8,1.1]² boxes are vacuous) are DEAD by
  0.23–0.69 (τ = 9.31–9.77; several with unconverged rows, "dead??", but the margins are large);
  the 3 boxes [0.5,0.8]²×{[0,30],[30,60],[60,90]} (they contain the corner square) are ALIVE with slack +0.036, +0.064,
  +0.096 at 300–590 s — but with rows AND columns far from converged (minmass 0.45–0.49, maxcov 1.5–1.75).
  Long re-solves (`_long_node.py`, 900–1500 s, 400 columns/iteration): box [0,30]: τ → 10.07, 10.03, 10.00, 9.98, 9.96
  (rows converged, maxcov 1.07 and still falling), i.e. **at/below the budget 10** — the standard corner box appears to be
  DEAD at 3.84 by ≈ 0.04, but (a) that run predates the shell-row fix of §5 (missing rows ⇒ τ underestimated), and the
  shell-including re-solves of the three boxes were at 10.18–10.24 after 360 s (unconverged, maxcov 1.4–1.5); (b) 0.04 is
  within the LP noise (mirror-image nodes differ by up to 0.1 at 300 s). NOT decided within the pilot.
Level 2 (children of the alive corner boxes: corner 1/2/3 families, 13 children each): 11 solved: 7 dead by 0.23–0.7
  (the off-corner boxes again), `NO corner1` dead??, the on-corner boxes alive with slack +0.17…+0.45 (unconverged).
Level 3: 2 alive so far. Growth: per corner level ≈ 3 survivors (the three θ-thirds of the on-corner centre box) out of
13 ⇒ 3⁴ ≈ 80 nodes with all corners fixed at depth 4 if nothing changes, then 4 side levels (19 children each) ⇒ 10⁴–10⁵
leaves — UNLESS the deeper nodes die (slack should shrink by ≈ 0.03 per fixed corner: root 0.033 − 4×(1−0.972) ≈ −0.08 at
depth 4 with converged LPs; the pilot's LPs are too noisy to see it). Node LP cost 340–670 s each (8 workers ⇒ ≈ 55 LPs/h).
Final counts of the run: see the table appended in §4b (from `python summarize.py results/t384c/tree.json`).
(3.85/3.86 not run: 3.84 did not close.)

## 5. Rigour: certificates and the LP-convergence problem (Task 4)

Pipeline: `certify.py node.json --s_rat p/q [--eps_geo 0.003]` = certificate (weights ×1.03, atoms 1/10⁶, hypotheses
rational) → `verify_case.py` (exact) → witnesses fed back as rows → re-solve → repeat.
* Verifier: `verify_case.py --selftest` PASS (3000 random boxes, int vs Fraction). Exempt tests implemented exactly (§1).
* **Certified (PASS)**: `certs_wip/smoke_node1_eps.json` — s = 96/25, budget 11, one D4-symmetric NO-family (no square
  centred in the interior zone [1.1,2.74]²), 220 atoms, total 10.467 < 11, verified in 2.6 s at max depth 27, 506 boxes
  exempt (nofam). Claim: no packing at side ≤ 3.84 has all centres outside the interior zone. (Weak but the pipeline
  works end to end: NO-family exemption path.) The plain (eps_geo = 1e-4) certificate of the same node FAILED with
  0.96–0.99 sliver holes that moved around under 4 rounds of witness feedback (τ ≪ budget, LP degenerate); the robust
  variant (LP re-solved with rows shrunk by EPS_GEO = 3·10⁻³, so every closed placement contains a nearby row's shrunk
  square) passed at once. Recommendation: certification runs use EPS_GEO ≈ 2–3·10⁻³ (costs ≈ 0.1–0.9 in τ here).
* Core path: `results/core380_node.json` (s = 3.80, one core box [0.5,0.8]²×[0,30], budget 10): converged LP τ = 9.605
  (462 s). Certificate ×1.03 (total 9.893 < 10): verifier FAILED with 37 holes of mass ≈ 0.80–0.82 at placements
  TOUCHING the core (SAT depth 5·10⁻⁶ ∈ (0, EPS_CORE]): the LP keeps these rows (conservative) but its row oracle never
  proposed them — the arrangement-cell sample points near the core all lie in the exempt part (depth > 2·10⁻³) and the
  2·10⁻³-thin kept shell is invisible to cell sampling. FIX (implemented, `Hyp.shell_points`): the oracle adds, per core,
  240 centres on the octagons {c : depth(Q(c,θ),K) = 10⁻⁵} and {= 10⁻³} and, per NO-family, points 10⁻³ inside the zone
  edges; EPS_TH raised to 0.3° (> fine θ step 0.25°) so the θ-margin strips always contain oracle samples. Re-solve of the
  core380 node with shells (`results/core380_node_b.json`): τ = 9.84 at 530 s (maxcov 1.17, not converged) — the shell
  rows are NOT free; whether the +0.24 is convergence or a real cost of covering the touching squares is open (a real
  cost would be an artefact of the exempt-margin scheme; the alternative is a zero-gap scheme with tangencies handled by
  the 3% margin, or exempting in the verifier w.r.t. the core and in the LP w.r.t. a core SHRUNK by 10⁻³ — which is
  what the present margins amount to). Certification of a core node was therefore NOT completed in the pilot; the run-3
  tree (built before the shell fix) has slightly optimistic τ at core nodes.
* LP convergence is the dominant practical problem: a C1 node LP with 8k–12k rows and 2–5k atoms takes 15–80 s per
  iteration (8 workers, BLAS threads pinned to 1), needs 30–100 iterations for ±0.02 accuracy; at 300 s the values are
  ±0.1 (mirror-image nodes 2 vs 4 in run 2: 9.93 vs 10.11). Deaths by ≥ 0.2 are robust; the on-corner nodes at slack
  ±0.05 are undecided by 300-s LPs.

## 6. Files

`lpbox.py` (LP engine, C1 + hyp hook), `caselp.py` (hypotheses, node LP, certificate), `bnb.py` (driver), `summarize.py`,
`certify.py`, `verify_case.py` (exact verifier with exempt tests), `_sanity2.py`, `_core380.py`, `_long_node.py`,
`_patch_*.py` (how lpbox/verify_case were derived from A12/A08 files), `geom.py` (A12 copy, unused).
Results: `results/t384c/` (run 3: `tree.json`, `bnb.log`, `node_<id>.json/.log`), `results/t384_run{1,2}_aborted/`,
`results/smoke384/`, `results/sanity2_*.json`, `results/core380_node*.json`, `results/long_node*.json`,
`results/test_root_380_*.json`; `certs_wip/smoke_node1_eps.json` (+ .report.json, PASS), `certs_wip/core380_node.json`
(FAIL, witnesses); `logs/`.
Reproduce: `python bnb.py --s 3.84 --tag t384c --workers 8 --node_budget 300 --time_limit 300 --root_warm ../A07-lp-dual/results/v2_s3.84.json`;
`python summarize.py results/t384c/tree.json [x]`; `python certify.py results/smoke384/node_1.json --s_rat 96/25 --eps_geo 0.003 --jobs 4`;
`python _sanity2.py noside`.

## 7. Verdict for the PI

1. The machinery exists and is sound in design (§1 bridge; exact verifier with NO-family and core exemption; A12's
   conditional LP reproduced exactly: corners fixed 7.000, + sides empty 5.000). One node certificate PASSED end to end.
2. At s = 3.84 the tree did NOT close within the pilot (≈ 40 LPs of 300–600 s each in ~1 h on 8 workers). What we saw:
   NO(all corners) dies by 1.6; 9 of 12 corner boxes die by 0.2–0.7; the 3 boxes containing the corner square sit at
   slack ≈ 0 (+0.04…+0.10 at 300 s; ≈ −0.04 after 25 min without shell rows; +0.2 with shell rows unconverged) — the
   whole question at 3.84 is decided in the second decimal, i.e. by LP convergence, not by tree size. If the on-corner
   boxes are dead the tree at 3.84 has 13 leaves; if alive, the observed branching (3 survivors per corner level, 19
   children per side level) gives 3⁴·(≈5)⁴ ≈ 10⁴–10⁵ leaves unless slack accumulation kills them earlier.
3. Viability for 3.85/3.86/3.87 on this machine: NOT with the present node LP. Cost model: 300–900 s per C1 node for
   ±0.05, and the deaths needed at 3.85 (root slack 0.06) / 3.86 (0.10) require ±0.01 accuracy ⇒ ≥ 30 min per node;
   with 10³–10⁵ nodes ⇒ weeks–years. Two things must change first: (a) the C1 node LP must converge 10× faster (warm-
   started dual simplex is fine — the bottleneck is column generation: use ≥ 1000 columns/iteration and keep all rows;
   from a cold start 1500 col/it converged the τ = 5 sanity LP in 2 min while 200 col/it stalled at 6.9 for 12 min) and
   (b) the corner/side "families" should be the placements NEAR the fractional packing's support (small boxes with big
   cores) rather than zone partitions — 9 of 12 corner boxes were dead by ≥ 0.2 at once, so coarse boxes are cheap to
   kill, but the surviving on-corner boxes need refinement to grow the core from side 0.45 to ≈ 0.9 to gain the missing
   ≈ 0.05–0.1; each refinement halves a box (2 LPs) so ~4–6 levels ⇒ 16–64 LPs per corner ⇒ 10³ LPs for the corner
   stage alone. Branching heuristic that worked: wall-first (corners, then sides), NO-child + coarse YES boxes, best-first
   by slack; symmetric root branch (WLOG corner 0) — 4× saving at level 1 only.
4. Concrete next step (cheap, decisive for 3.84): converge the three on-corner box LPs at 3.84 with shell rows to
   ±0.01 (≈ 30 min each with 1000+ columns/iteration; refine only if needed), then certify the 13 leaves with
   `certify.py --eps_geo 0.003` ⇒ **s(11) ≥ 3.84** would follow from a 13-node tree. If they are alive, run the
   corner-refinement stage (≈ 10³ LPs) before deciding about 3.85.
'''
start = notes.index(u'## 3. Sanity checks (Task 1)')
notes = notes[:start] + s3
io.open('notes.md', 'w', encoding='utf-8').write(notes)
print('ok')
