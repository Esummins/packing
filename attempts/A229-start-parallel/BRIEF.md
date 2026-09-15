# A229 -- run a page's start nodes in PARALLEL (2026-09-15 09:05).  The lab sat idle from 01:06 to 08:59 with three
# k5 pages alive; each page runs its start nodes sequentially inside one 1800 s wall, so one hard start node
# (Y1056: 3 start nodes, the first ate the whole wall, 0 killed) blocks the rest while 7 process slots are free.
Opus. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns, explicit-pathspec
commits per shard, PYTHONDONTWRITEBYTECODE=1, at most ONE test python of your own (BelowNormal, affinity 0xFFFF),
never touch the running pass-6 workers p6a/p6b/p6c (queue_pass6.txt: Y0402, Y0738, Y1056; flags
A220_NOROOM_INHERIT=1 A221_LANE=1 A224_SNAP=1) -- they must keep running; your change lands for the NEXT pass.
Never edit a running worker script in place (bash reads by byte offset): install by rename (A228).  A224 owns
nothing now; A230 (EPS all-candidates + NS-at-wedge) owns tree211.py / leaves211.py -- you own run211.py,
startload211.py, inherit211.py, worker211.sh, progress211.py/pstats211.py (coordinate: do not edit tree211/leaves211).
Read first: run211.py (CLI, the per-page cert coarsetree211_<page>.json, the runs loop over start nodes, SKIPPED
(wall)), inherit211.py + startload211.py (Lemma INHERIT: prior trees merged on the path key; dead branches final;
start nodes = alive leaves; the A211h nearest-sound-ancestor climb), worker211.sh (claims by mkdir per nid),
notes/coarse_tree.md s.4, A225's pstats211.py (start-node accounting).

## Task
1. run211.py: `--start LABEL[,LABEL...]` runs ONLY those start nodes of the page (the others SKIPPED (filter), not
   (wall)); `--cert-suffix TAG` writes the run's certificate to coarsetree211_<page>__<TAG>.json (the page cert
   untouched); the results row carries start/suffix.  Default behaviour byte-identical without the flags.
2. inherit211 / startload211: the loader merges EVERY coarsetree211_<page>*.json (page cert + suffixed certs) on
   the path key -- dead branches from any file are final (each carries its own certificate), alive leaves from the
   newest file per path; snapshots resolved across files; the A211h climb unchanged.  Prove in notes/parallel229.md
   that merging per-start certs is Lemma INHERIT applied file-wise (same hypothesis key => same node; a DEAD branch
   is a theorem about that hypothesis regardless of which run proved it).  Test: test_inherit_multi229.py -- a page
   run whole vs the same page run as two --start halves then loaded: identical dead set and identical next start
   nodes.
3. worker211.sh -> worker229.sh (new file, same gates): queue lines `NID START [WALL]`; claim dir
   claims/NID__START; after the run: fold211 / progress211 / refresh_current / commit as before.  A queue builder
   `queue229.py PAGE...` that lists the current start nodes of each page (pstats211's accounting, both pads) as one
   line each, longest-first, so N workers take N start nodes of the same page.
4. Verify on a CLOSED page (Y0500 g1, isolated dirs): whole-page run vs 3 parallel --start runs merged: same
   verdict, same dead set; report seconds.  Then write queue_pass7.txt = the start nodes of Y0402 / Y0738 / Y1056
   (both pads) for the coordinator to launch when pass 6 ends (do NOT launch; the pass-6 certs will change until
   then -- note that queue229.py must be re-run at launch time).
5. Deliverables: the patches, worker229.sh, queue229.py, test, notes/parallel229.md, results/verify229.md,
   registry row, LOG entry.  Report once (<= 12 lines) and EXIT.
