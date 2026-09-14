# A211d -- INSTRUMENTED NODE KILL and an optimisation pass (PI, 2026-09-14 08:20). Opus. LAUNCH-AND-EXIT.
PI: "have you taken a general optimization pass to minimize time costs? Have you run an instrumented node kill to see
which parts are eating the time budget?"  Answer so far: no.  Do it now.

1. PROFILE: run one page from its inherited state under cProfile (python -m cProfile -o ... code/run211.py page
   k5_11_interior_Y0202 --pads zero --wall 900 with an isolated --cert-dir / --results / --no-fig so the workers'
   files are untouched), plus the tree's own per-node step_seconds / test_seconds.  Report a breakdown BY STAGE (load /
   inherit, coarse cascade round, reach tests, pair table, count, no-room, CC, basin, NS, role-split, exact cascade,
   figures, JSON I/O) and BY FUNCTION (top 25 cumulative), with the share of the 900 s each takes.
2. OPTIMISE only what keeps the certificates IDENTICAL on the test page (same verdicts, same kills, same node labels):
   caching (pieces, K', reach results across children), avoiding repeated JSON loads / re-normalisation, cheaper
   coarse bins where the rule is monotone, skipping tests whose result is implied, vectorising the SAT loops, not
   drawing figures on internal nodes.  No change to any rule's semantics; no new lemma.  Re-run the profile after the
   changes and report the per-stage gain.  Commit with explicit pathspecs; the running pass-2 workers (worker211.sh
   p2a/p2b) spawn a fresh python per node and will pick the code up -- do NOT restart them.
3. Report once: the two breakdowns (before / after), the changes, pointers (profile files under logs/profile/), commits.

## RESULT (A211d, 2026-09-14 09:10) -- profile of k5_11_interior_Y0202, pad 0, wall 900, isolated cert / results / --no-fig

Profiles: `logs/profile/{before,after}_k5_11_interior_Y0202_zero.{prof,log}` (cProfile, one process, BelowNormal,
BLAS pinned); the self-check run `logs/profile/verify_k5_11_interior_Y0202_zero.log` (A211_CLIP_VERIFY=1).

BY STAGE (before, 1755.9 s): normalise = the fixed point 1168.9 (66.6%); no-room leaf 380.3 (21.7%); option table
161.9 (9.2%, of which ROLE-REACH 155.2); count + bar-H 1.6; union caps 0.8; s-clip / HC rows / rebin 1.3; stage 0 +
INHERIT + start load + JSON I/O + the rest 41.1 (2.3%).  BY FUNCTION the whole page is ONE primitive pair:
`MBox.rebuild` (the per-piece K', A171/A172) 1160.4 s = 66.1% -- `pieces_poly` 996.4, `polycore.vertex_ok` 550.4,
`PC.build` 479.8 -- and `_clip_rect_obstacle` 532.8 s = 30.3% (bisect_region 149.7, the fixed points' clip_all 191.2,
no-room's bisect_free 143.0, the library normalise 49.2); below them it is all exact Fraction arithmetic
(math.gcd 144.9 s, Fraction._mul 131.3, forward 126.5).  JSON I/O 0.4 s; a figure render 0.10 s and a save 0.05 s per
node (measured separately) -- NOT worth skipping on internal nodes.

CHANGES (code/fastclip211.py, wired in coarse211.install / coarse211.role_reach): three PURE caches -- (0) `MBox.rebuild`
memoised on its pieces + build parameters; (1) `_clip_rect_obstacle` memoised on (obstacle, bin, rect) with the stats
deltas replayed; (2) the depth-0 role reach split into the S-independent prefix (container + obstacles, shared across
the role's slot sets at the node) and the A161 MISS tail.  No rule, no bound, no lemma touched; the trace's exact-test
counts are reproduced exactly.  Verified call-by-call against the library (13833 clip hits + 160 K' hits re-computed
and compared, no mismatch), and the two certificates agree field by field on every node both runs ran (kept, n_pieces,
K', forced_H, role_slots, alive_cells, miss, s-clip, HC rows, rebin, snapshot roles) -- only `seconds` / `t` differ.

GAIN on the three nodes both runs ran in full: 917.3 -> 747.1 s (-18.6%); option table 68.7 -> 18.8 (-72.6%,
ROLE-REACH -81%), no-room 380.3 -> 310.9 (-18.2%), the fixed point 436.7 -> 402.2 (-7.9%).  The time bought a KILL:
inside the same 900 s wall the after-run reached R.1.4.2.2.1.1 with enough budget left for A189's no-room to finish,
and that branch is DEAD by NOROOM where the before-run left it undecided at the wall.

NEXT LEVERS (not taken): the exact leaf cascade runs even when the wall is already spent (leaf_rules checks the wall
only at entry) -- 837.9 s of the before-run; the exact-mode role reach could share the same depth-0 prefix (91.5 s,
5%); everything else is exact rational arithmetic inside the read-only A171/A132 libraries.
