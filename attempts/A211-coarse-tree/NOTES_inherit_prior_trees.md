# A211b -- INHERIT the prior trees (PI, 2026-09-12 19:10: "your new run ignored the prior y0202 work and started the
# node over"). Opus. LAUNCH-AND-EXIT. Same directory, same launcher; code change + relaunch.

Ops as in BRIEF.md (launch-and-exit, no monitors; explicit-pathspec commits; never touch A207 / the k0 cascade).
A211's workers were stopped at 19:10 (STOP file, 3 claims: Y0130, Y0202, Y0672 -- clear them when relaunching).

## What to build: the start state of a page = the UNION of every prior certificate for it
Sources, all audited kills with certificates (dead branches are FINAL; never redo them):
  attempts/A205-clip-tree/certs/cliptree205_<nid>.json (+ certs/extended/*_w3600v4.json), the 900 s / 3600 s trees;
  attempts/A206-named-split/certs/namedsplit206_<nid>.json (runs keyed leaf label: Rule NS subtrees under A205 leaves);
  attempts/A209-k5-killer/certs/k5killer209_<nid>.json (both pads; the composed chain's trees, 3600 s);
  attempts/A210-corner-cover/results/cornercover210_leaves.jsonl (CC kills of A209 nodes: node, slot, pad);
  attempts/A208-noroom-leaves/results/noroom208.jsonl (no-room kills of A205/A206 leaves);
  attempts/A207-basin-clip/results/basinclip207.jsonl (basin + NS kills of leaves).
Build per (page, pad) the merged tree: the branching structure of the most recent tree (A209's), with every branch
that ANY prior certificate closed marked DEAD (carry the certificate path and the rule), every leaf killed by A208 /
A210 / A207 marked DEAD likewise, and the remaining ALIVE / undecided nodes as the coarse tree's START NODES (load
their role pieces / boxes with load206 / load209 semantics -- pieces padded outward when loading: a superset).
Soundness: a branch closed under one sound rule set stays closed under another (its hypothesis set is what died); the
coarse tree only refines the open nodes.  Write this as a lemma (INHERIT) in notes/coarse_tree.md before use.
Then run the coarse tree from those start nodes only (pad 0 first), and the page verdict = DEAD iff every inherited
branch and every new branch is DEAD.  The page shows inherited dead branches in grey with their source campaign.
Results: results/coarsetree211.jsonl rows carry inherited_dead / inherited_alive counts and the source certs.
Test on Y0202 pad 0 (report: how many branches inherited dead, how many start nodes, seconds), relaunch
`bash code/launch211.sh 4 1800` with the claims cleared, report once, EXIT.
