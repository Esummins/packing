# A206 -- the NAMED-OR-ANONYMOUS split at the clip tree's "fully named" leaves (PI reading, 2026-09-11 12:20)

Model: Fable. Short responses, files in pieces <= 250 lines, no interim messages, commit after every page batch
(`git add -- <paths>; git commit -- <paths>`; fetch + plain merge only; never pull --rebase / autostash / reset; no
recursive deletes; PYTHONDONTWRITEBYTECODE=1; <= 3 processes, BLAS pinned to 1 thread, affinity 0xFFFF, BelowNormal;
6144 MB gate; lab ceiling 12 python processes EXCLUDING command lines containing "Claude Extensions"; COPY A205's code
(attempts/A205-clip-tree/code at the current commit) into your code/ and extend the copy; never touch A205's files or
its running extended pass (run205_ext.sh; the coordinator stops it when you produce rows). Agent messaging is broken;
report ONCE at the end.  Pages: docs/residue_map/campaigns/A206-namedsplit/namedsplit206_<nid>.svg (+ gallery) per
docs/residue_map/README.md; set docs/residue_map/CURRENT.json to A206 (A205, A203 patterns as fallbacks) and run
docs/residue_map/refresh_current.py after every batch.

## The PI's reading (credit by name): k5_11 Y0672, leaf R.2.3.1 of A205's tree
"how is this node still alive? I don't see how the TR00 meeter box (the one with no core built) is placeable? With
how close the H and F1 cores are to the possible centers, it seems like there _should_ be an F4 core, and once that
tries to cascade the clip, it will probably die."
Coordinator's check: H's box there is [2.358,2.389]x[2.381,2.466], tilt 0-12 deg; TR(0,0)'s widened box starts at
2.85 in x and y; H's top-right corner reaches (2.87, 2.92) upright, so H is "not provably missing" TR(0,0) by 0.02 and
A205's rule (named = H-if-not-provably-missing + instantiated roles; |named| >= 2 -> no branch) counted H + F1 and
stopped ("every forced slot has two named meeters").  The count's own witness placed the second meeter in the anonymous
cell 24 instead.  The disjunction must be SPLIT, not counted.

## Rule NS (state and prove it in notes/named_split.md before use, any n)
At a node where every forced slot has |named_p| >= 2 (A205's stop), for each slot p whose named set contains a role r
whose MEETING fraction of p is small (r's pieces that meet p's widened box are a sliver -- threshold: kept fraction of
the meeting pieces < 0.5, or simply every slot with a non-empty anonymous row set), branch exhaustively:
  [r meets p]: clip r to its pieces meeting p (exact reach clip, A161), keep the other roles, run A204's cascade + A205's
              clips to the fixed point, then A205's rule (branch further or stop);
  [r misses p]: r is clipped to its pieces provably missing p (the complement -- sound: the two branches cover r's
              pieces), so p needs an anonymous meeter: instantiate the row(s) (singly if one other named remains, pairs
              if none), F_k with its K', cascade, recurse.
This is A182's H-meets / two-free split at the leaf, applied to every named role whose reach is coarse.  DEAD iff every
branch DEAD; undecided = ALIVE; every kill [C: library clip trace] with branch/clip/round.  A205's soundness proviso
(refresh the table with one cascade round before any branching) is inherited; audits (A205's scratch/audit205.py,
audit_roles205.py, with the cap-1 two-meeter criterion) on every kill.

## Runs and report
1. Y0672 R.2.3.1 first (load the node from attempts/A205-clip-tree/certs/cliptree205_k5_11_interior_Y0672.json, g1
   pad) -- the page after the split, both branches, times; then every "fully named" ALIVE leaf in A205's certs
   (results/cliptree205.jsonl, certs/, certs/extended/*_w3600*.json as the extended pass lands them) grouped by page,
   wall 3600 s per page; then the pages whose 900 s trees were wall-cut, running the whole tree with rule NS.
2. results/namedsplit206.jsonl, certs/, pages; notes/named_split.md (Rule NS, the PI credited, per-page table: leaves
   split, branches, kills by clip, seconds); registry row, LOG entry, docs/residue_ledger.md section 4, docs/budget.md
   item, status gallery collector block for kills; PAUSED.md fold-in for what survives, with the next lever named.
