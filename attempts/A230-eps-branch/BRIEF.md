# A230 -- Rule EPS: check ALL candidates, then BRANCH the surviving blocker at the wedge (PI, 2026-09-15 09:00:
# "F1 (BL10) should trigger EPS before F2 does (BR01), so there may need to be something to make sure it checks all
# candidates").
Opus. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns, explicit-pathspec
commits per shard, PYTHONDONTWRITEBYTECODE=1, at most ONE benchmark python (BelowNormal, affinity 0xFFFF), never
touch the running pass-6 workers (p6a/p6b/p6c on Y0402 / Y0738 / Y1056) -- your change lands for the next pass.
You own tree211.py / leaves211.py (apply A227's integration227.diff first, flag A227_EPS default OFF) and
eps227.py's successor eps230.py; A229 owns run211/startload211/inherit211/worker scripts -- do not edit those.
Read first: docs/proofs/lemma_eps.md (EPS-1..6, GATE, Rule EPS), attempts/A227-lemma-eps/{code/eps227.py,
results/eps227.md (71 pages: 294 candidate nodes, 0 kills, 284 nodes lose >= 1 meeter; the survivor is H, reaching
a wedge at every candidate; Y0865: H's edge crosses x = 2 at y = 0.9916 inside the right wedge target), the
integration diff}, tree211 Rule NS (N6.ns_candidates / ns_branches: the meets / misses split of a soft name at a
slot; MAX_FRAC), notes/coarse_tree.md.

## Task
1. ALL CANDIDATES: at a node, evaluate EVERY near-simple role (all roles whose box passes the candidate test, both
   cells a role could be near-simple in), in a deterministic order (the role with the smallest box first); a kill if
   ANY candidate's cell is left with < 2 distinct non-pin meeters; record per candidate what was struck and who
   survived.  Re-run the 71-cert scan (epsscan) with this: report candidates per node (was it 1.1 before because
   the candidate test excluded F1 / F2, or because the scan stopped at the first?) and kills.
2. NS-AT-WEDGE: when exactly one blocker survives at a candidate (H in 107 of 173 pairs), branch it with Rule NS at
   the WEDGE polygon instead of the whole cell: the MISSES child is DEAD at once by FC+EPS (record the kill with the
   wedge certificate + the miss certificate); the MEETS child carries "H meets the wedge W" as a row (its box
   clipped to the poses reaching W -- the exact clip of H's box against W, A213/A214 kernels), then the coarse round
   and the leaf rules as usual.  Depth-cap accounting as for NS; fresh-table proviso (refresh the option table after
   the clip before any further branching).
3. TAPER: replace the wedge's bounding rectangle in the strike test by the exact wedge polygon (polygon SAT, A161's
   exact miss test against the polygon) -- A227 s.7 [C]; count how many strikes it adds on the scan.
4. BENCHMARK (one process, isolated cert dirs, --no-fig, wall 900): Y0865 g1 from its A203 root with --no-inherit
   under flags {pass-6 set} vs {pass-6 set + A227_EPS=1}: nodes, dead leaves, FC+EPS kills, NS-at-wedge branches
   and their outcomes, time to first kill; verdict agreement on Y0500 g1.  If the wedge branch kills where the
   whole-cell NS did not, say where (the PI's F1/F4/H configuration).
5. Deliverables: patches (flag-gated; flag off = pass-6 behaviour), eps230.py, results/bench230.md (+jsonl, the
   re-scan table), notes/eps230.md, registry row, LOG entry; queue_pass7 flag recommendation.  Report once
   (<= 12 lines) and EXIT.
