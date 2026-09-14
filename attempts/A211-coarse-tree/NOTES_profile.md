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
