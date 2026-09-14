# A211g -- two resume bugs (2026-09-14 14:05). Opus. LAUNCH-AND-EXIT.
1. A211 pass 2: pages after the first "finish" in 4-6 s with every loaded start node "undecided (wall) at the fully
   named leaf" (logs/coarsetree211_k5_16_interior_Y0660.log, worker_p2a.out 12:04-12:05): the loaded start node's
   Trace / elapsed timer (pg.T) comes from the snapshot or the previous run, so out_of_time() is true at once.  Fix: a
   fresh Trace per run with the run's wall (startload211 / run211), keeping the snapshot's `t` only as provenance.
   Regression: load any start node and assert pg.T.left() == wall.  Then clear the gallery claims (rmdir each of
   code/queue_gallery_pass2.txt's pages under logs/claims/) and relaunch `worker211.sh p2a 1800 <queue>` and p2b.
2. A212 frontier: every A60 frontier node fails in load211.synth_record with KeyError '<nid>_interior_G1'
   (logs/trump5tree212_f1_L02_0007.log): the loader knows only A57's k5 tree files.  Extend attempts/A212-trump5-tree/
   code/load211.py (A212's copy) to A60's records (attempts/A60-trump5-campaign/results/ -- find the alive frontier
   records the census counts; A60's tree60.py / substrat.py show the record format), regression-load all 136 nodes of
   code/queue_frontier.txt with 0 errors, clear their claims (rmdir), relaunch `bash code/launch212.sh 3 1800`.
Ops as before: workers f1/f2 (k5 frontier) untouched; explicit-pathspec commits; no monitors; report once and EXIT.
