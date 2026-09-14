# A211h -- load a start node from the nearest SOUND ancestor (2026-09-14 15:20). Opus. LAUNCH-AND-EXIT.
Y0202 is ALIVE on both pads only because four start nodes are refused by the loader:
  g1: R.3.2.2, R.3.2.3, R.3.3 -- the ancestor snapshots in attempts/A205-clip-tree/certs/extended/*_w3600*.json were
      written at the 300-piece cap while H had 415 / 475 pieces ("capped: cannot load soundly");
  pad 0: R.1.5.2 -- its ancestor R.1.5r1 (a refresh node) carries no snapshot.
Every tree node of the page is DEAD (40/40 pad 0, 10/10 g1).
Fix (startload211 / inherit211): when the chosen ancestor's snapshot is capped or absent, climb the path to the nearest
ancestor whose snapshot is COMPLETE (any campaign's certificate; else the page's A203 stage-0 root) and replay the
remaining branch steps from the path key (row / pair / NS / pocket / rsplit -- apply_step handles each); record which
ancestor was used and how many steps were replayed (`meta["loaded_from"]`).  Soundness: Lemma INHERIT -- same path key,
same hypothesis; replaying steps from a higher complete snapshot only enlarges the pose set (superset).
Regression: test_inherit211 --load over every page: 0 refusals for capped/missing snapshots (a genuinely unloadable
node -- no complete ancestor at all -- may still be refused: report the count).  Then re-run Y0202 pad 0 and g1 through
the normal path (run211 page k5_11_interior_Y0202 --pads zero,g1 --wall 1800, the real cert dir, with --no-fig off so
the page redraws) and report the verdicts.  Ops as A211g (workers untouched; explicit-pathspec commits; no monitors;
report once and EXIT).
