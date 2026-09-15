# A229 -- running a page's START NODES in PARALLEL (2026-09-15)

Read with `attempts/A211-coarse-tree/notes/coarse_tree.md` s.4 (Lemma INHERIT), whose notation this note keeps.

## 0. The observation that forced it  [M]

The lab sat idle from 01:06 to 08:59 on 2026-09-15 with three k5 pages alive.  Each page runs its start nodes
SEQUENTIALLY inside one 1800 s wall (`run211.run_starts`), so `k5_16_interior_Y1056` -- 3 start nodes, the first of
which ate the whole wall -- killed 0 of them while 7 of the lab's 10 process slots stood free.  The start nodes of one
page are independent hypotheses; nothing but the shared `certs/coarsetree211_<nid>.json` file made them sequential.

## 1. Lemma INHERIT applied FILE-WISE  [T]

Fix a page, a pad and the A203 start `s0`.  Recall (coarse_tree.md s.4) that a node of any campaign tree over
`(page, pad, s0)` is identified by its PATH KEY `P` -- the ordered conjunction of its branch steps -- and that

  (a) *kills are final*: if any certified run proved the node at `P` DEAD, then `P` is impossible, and so is every
      path extending `P`;
  (b) *branch lists are reusable*: a branch list recorded at `P` is an exhaustive disjunction under `P`;
  (c) walking the merged trie of all prior trees with (a) and (b) yields the DEAD branches and the START NODES, and
      the page is DEAD iff every start node is DEAD.

**Lemma PAR (A229).**  Let `F_1, ..., F_k` be certificates over the same `(page, pad, s0)` and let `T(F)` denote the
set of `(path key, record)` pairs a certificate contributes to the trie.  Then the merge of `T(F_1) u ... u T(F_k)`
by (c) is sound, and its verdict does not depend on which file contributed which record.

*Proof.*  (c) takes as input a SET of certified records keyed by path.  The hypotheses of (a) and (b) are statements
about the path key alone: "the node at `P` was proved DEAD by a certified rule", "the branch list `P.1, ..., P.m` was
certified exhaustive at `P`".  Neither mentions the file, the process, the wall, or the pose set the proving run
happened to hold -- coarse_tree.md s.4(a) makes this explicit ("the refutation does not depend on the pose set the
refuting run happened to hold: the hypothesis set is what died").  Two records with the same path key are therefore
records about the SAME hypothesis whichever file carries them, and the union is just the set (c) consumes.  Soundness
of the merge is (c).  Independence of the attribution: (a) is a disjunction over the sources ("closed by SOME
certificate"), which is symmetric in them, and (b) says every recorded branch list at `P` is exhaustive on its own, so
choosing any ONE of them is sound -- the choice changes only which labels the run prints, never which hypotheses are
left.  []

**Corollary (the parallel pass).**  Let `S = {s_1, ..., s_n}` be the start nodes of `(page, pad)` produced by (c) from
the certificates present at time `t_0`.  Partition `S` into `S_1, ..., S_k` and run one process per part, each
starting from the SAME merged state and each running only the start nodes of its own part (`run211.py --start`),
writing to its OWN file `certs/coarsetree211_<nid>__<TAG>.json` (`--cert-suffix`).  Then merging all `k` files with
the page certificate by Lemma PAR gives exactly the state one sequential run over all of `S` would have left.

*Proof.*  Each shard's tree under `s_i` is grown from `s_i`'s hypothesis alone (`startload211.load` loads `s_i` from
an ancestor snapshot on `s_i`'s OWN chain and replays `s_i`'s own steps; the tree below `s_i` never reads a sibling).
So the records a shard writes under `s_i` are the records the sequential run would have written under `s_i`, and the
union over the parts is the union over `S`.  Apply Lemma PAR.  []

**Why the shards never fight.**  Each writes one file no other process names (`__<TAG>`, `TAG` from the claim), and
the page certificate `coarsetree211_<nid>.json` is written by NO shard.  A start node that a shard leaves ALIVE stays
a start node of the next pass, because the merge finds no DEAD record and no branch list beyond what that shard
recorded.  A start node the FILTER skipped is recorded `SKIPPED (filter)` -- explicitly *not* `(wall)`: the run refused
it, the geometry did not, and `run211.wall_limited` therefore always allows the shard to be resumed.

**What a shard's pad verdict means.**  A shard is DEAD at a pad only if every start node the merge offered it was in
its own filter and every one of them died; otherwise it is ALIVE with the others `SKIPPED (filter)`.  So a shard row
can never claim a page kill that was not proved: `fold211` folds a `mode=page, pad=g1, verdict=DEAD` row, and such a
row from a shard means the shard really did close every remaining branch.

**The ordering rule inside the trie.**  `inherit211.trie` keeps, at a shared path, the branch list of the LAST source
of the highest rank.  All A211 files have rank 5, and `inherit211.a211_certs` returns them OLDEST FIRST by mtime, so
the newest A211 file's branch list wins.  By (b) any of them would do; taking the newest keeps the printed labels
closest to the most recent run.  DEAD is never subject to this tie-break: `g["dead"]` is set by the FIRST source that
closes the path and closure is checked in every source, so a kill in any file is final (that is (a)).

**What is NOT claimed.**  Nothing here lets two shards run the SAME start node and merge the two trees below it: they
would write different labels for the same hypotheses and the trie would keep only one branch list.  That is sound (by
(b) either list is exhaustive) but wasteful; `queue229.py` emits each start node exactly once and `worker229.sh`
claims it by `mkdir claims229/<nid>__<TAG>`.

## 2. What was built  [C]

* `attempts/A211-coarse-tree/code/run211.py` -- `--start LABEL[,LABEL...]` (the other start nodes recorded
  `SKIPPED (filter)`), `--cert-suffix TAG` (the run's certificate goes to `coarsetree211_<nid>__<TAG>.json`, implies
  `--no-fig`: a shard holds only part of the page), both carried on the results row (`shard`, `start_filter`,
  `cert_suffix`, `start_skipped`).  Without the flags the code path, the certificate and the row are unchanged.
* `attempts/A211-coarse-tree/code/inherit211.py` -- `a211_certs(nid)`: the page certificate AND every
  `coarsetree211_<nid>__*.json`, oldest first by mtime, all at rank 5.  The `__` separator keeps the A57 descendant
  pages (`coarsetree211_<nid>_D07.json`) out.  `A229_CERT_DIR` moves the A211 sources for an isolated test.
* `attempts/A229-start-parallel/code/queue229.py` -- the start-node queue, `<nid> <pad>:<label> <wall>`, longest-first
  by the wall each start node has already absorbed without closing (A225 `pstats211`), start nodes from
  `inherit211.merge` (the definition of what is left).  **Re-run it at launch time**: the certificates keep changing.
* `attempts/A229-start-parallel/code/worker229.sh` -- worker211's gates and post-run chores at start-node granularity.
* `attempts/A229-start-parallel/code/test_inherit_multi229.py`, `verify229.sh`, `results/verify229.md`.
