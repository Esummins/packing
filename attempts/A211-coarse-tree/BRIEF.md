# A211 -- THE COARSE TREE: reach the leaf kills as fast as possible (PI, 2026-09-12 18:20: "the more coarse we can get
away with the better, since we want to reach the leaf kills asap"). Fable. LAUNCH-AND-EXIT.

Ops (binding): short responses, files in pieces <= 250 lines, no interim messages, NO monitors, NO waiting turns: build,
test on one page, launch ONE detached launcher (workers commit per node with explicit pathspecs, write results/progress.md
hourly), report and EXIT with a resume block (memory rule agents-launch-and-exit).  `git add -- <paths>; git commit --
<paths>`; fetch + plain merge only; no pull --rebase / reset; no recursive deletes; PYTHONDONTWRITEBYTECODE=1; up to 6
workers gated at 10 lab pythons excluding "Claude Extensions" command lines and at 3072 MB free physical; BLAS pinned;
priority BelowNormal set the WORKING way (A210's fix: c_void_p(-1) + argtypes -- the old snippet silently no-ops);
affinity 0xFFFF; never touch other campaigns' files or processes (A207's basin queue and the k0 cascade are running);
COPY code from A209 (attempts/A209-k5-killer/code, the composed chain) and A210 (rule CC) into code/ and modify the
copies.  Pages: docs/residue_map/campaigns/A211-coarsetree/ per docs/residue_map/README.md; CURRENT.json -> A211.

## Why
A209's trees are WALL-limited, not rule-limited: every gallery page sits ALIVE at the 3,600 s wall on both pads with
undecided branches, because the exact cascade fixed point at a 5-role node costs ~400 s and the tree spends its hour
on 10-20 internal nodes.  The leaf rules (A210 Lemma CORNER-COVER, A208 NO-ROOM + pocket CN bound, A207 Lemma BASIN,
A206 Rule NS) kill in milliseconds to seconds once a fully named leaf is reached.  So: make internal nodes CHEAP and
get to named leaves first; spend exactness only where a kill is claimed.

## The design (state each soundness point in notes/coarse_tree.md before use)
1. INTERNAL nodes: the coarsest sound propagation -- stage-0 rules on cell rectangles + A203's piece-pair table at
   coarse bins (16 sub-rects x 6 tilt bins, no refinement), ONE cascade round with hull boxes (nsub 2 / refine 1, or
   the box-only K' if the library allows), no lonely clip, no sharp round, no SEAL; branch immediately on the tightest
   slot (fewest rows; pairs when no named meeter; unit propagation); depth cap 6, node cap 600; per-node target <= 20 s.
   A coarse node is a SUPERSET (never kills wrongly): a coarse DEAD is still a DEAD (every test is a sound necessary
   condition) but coarse ALIVE means "branch further".
2. LEAVES (every forced slot with two hard-named meeters, or all option rows exhausted): the leaf rules in this order,
   cheapest first, each closed-form/exact and certified: (a) Lemma CORNER-COVER (A210 rule CC, P-frame corollary CC');
   (b) NO-ROOM with the pocket CN bound on the leaf's role boxes (k = 10: full; k = 9: branch into the pockets of
   diameter < 1 as the 10th role and recurse); (c) Lemma BASIN clip (A207's results/basin207.jsonl radii; only the
   slots with a BASIN row); (d) Rule NS split of any soft name (slivers only); (e) ONLY THEN the exact cascade at the
   leaf (nsub 4 / refine 2, lonely clip, sharp round) to a fixed point; (f) the pad-0 verdict printed beside the window
   verdict.  A leaf is DEAD iff one rule proves it; the page is DEAD iff every branch is.
3. PAD 0 FIRST on every node (pad ghosts get their instant s0 verdict), then the G1 pad; wall 1,800 s per pad per page
   at first -- measure how many pages reach leaves; raise only if the measured node cost allows.
4. Every kill [C: closed-form / library clip trace + the leaf lemma] with branch / rule / seconds, audited by sampling
   (A206's audit206b, cap-1 two-meeter criterion); pages after the root and after every closed branch, the tree table
   on the page with seconds per node.

## Population and report
The 19 alive k5 gallery pages (A210's results/pages210.txt) pad 0 then g1; then A209's frontier census (321 alive
nodes, deepest first; a node kill closes its subtree, Lemma K1) with the price measured after 20 nodes and written to
results/progress.md; stop at a 200 CPU-h projection.  Results results/coarsetree211.jsonl; certs/; the status gallery
collector block; registry row, LOG entry, docs/residue_ledger.md section 4, docs/budget.md item; PAUSED fold-in.
Report once (the design's soundness points, the one-page test with per-node seconds and where the leaves were reached,
the launcher command / pid / where rows land / how to resume) and EXIT.
