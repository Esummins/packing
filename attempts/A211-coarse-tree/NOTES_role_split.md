# A211c -- ROLE-SPLIT at "fully named but wide" leaves (PI, 2026-09-12 19:40). Opus. LAUNCH-AND-EXIT.
PI on Y0202 pad-0 leaf R.1.4.2.2s: "Why does this case list 'next lever' as lp on the node instead of no-room? it's got
5 pins and 5 named nodes that cover a huge chunk of the box."
Diagnosis: (1) tree211 skipped no-room by the once-per-k rule -- backwards (smaller boxes = larger cores); patched by the
coordinator to run at every fully named leaf (node-level flag).  (2) On this leaf no-room on the boxes is UNDECIDED
anyway: F4's box spans 0.9 in y with tilt 0-90 and F1's 0.4 x 0.35 with tilt 3-66, so their CORES (intersection over the
box) are empty -- the ten squares cover the container in the UNION sense only.
Lever: ROLE-SPLIT.  At a fully named leaf where no-room is UNDECIDED, pick the named role whose box is widest (position
extent > 0.25 or tilt range > 30 deg; prefer the role whose core is empty), bisect its box (the widest dimension; tilt
split at the midpoint), and recurse into the two children (each child: the coarse round, then the leaf rules incl.
no-room again); depth cap 4 splits per role; each split is an exhaustive disjunction (sound), recorded as a branch step
in the path key (Lemma INHERIT).  Stop splitting a role once every child's no-room decides or the child dies.
Implement in tree211.py next to pocket_branches (same branch mechanics), state it in notes/coarse_tree.md (Lemma
ROLE-SPLIT), test on Y0202 pad 0 from the inherited state (report: splits, no-room verdicts per child, seconds), commit,
and let the running workers pick the code up on their next node (they spawn a fresh python per node) -- do NOT restart
the workers.  Report once and EXIT.
