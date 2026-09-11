# A205 -- the CLIP TREE: branch on a forced slot's remaining meeter options, instantiate, cascade, recurse
(PI 2026-09-10 20:35: "k5_11 Y0202 looks like it'll die if/when clip cascades try to run on the BR01 meeters.")

Model: Fable. Short responses, files in pieces <= 250 lines, no interim messages, commit after every page batch
(`git add -- <paths>; git commit -- <paths>`; fetch + plain merge only; never pull --rebase / autostash / reset; no
recursive deletes; PYTHONDONTWRITEBYTECODE=1; <= 2 processes, BLAS pinned to 1 thread, affinity 0xFFFF, BelowNormal;
6144 MB gate; lab ceiling 12 python processes EXCLUDING command lines containing "Claude Extensions"; never touch other
campaigns' files or processes -- COPY A204's code (attempts/A204-polyclip-cascade/code at the current commit) into
your code/ and extend the copy). Agent messaging is broken; report ONCE at the end.
Pages: docs/residue_map/campaigns/A205-cliptree/cliptree205_<nid>.svg (+ gallery) per docs/residue_map/README.md; set
docs/residue_map/CURRENT.json to A205 (A204's then A203's patterns as fallbacks) and run refresh_current.py per batch.

## Why
A204's cascade runs the polygon + lonely clip to a FIXED POINT but only instantiates FORCED meeters (cap 1).  On
k5_11 Y0202 (g1 pad) nothing is forced: one round, H kept 0.996, no role instantiated, ALIVE in 214 s -- the BR(0,1)
meeters were never clipped against anything.  The PI's clip tree: BRANCH on the slot's remaining meeter options
(A203's option rows: BR(0,1) has 4 alive cells), instantiate the meeter as a role in each branch, run A204's cascade
to the fixed point (K' grows, clips H and the other meeters), apply the count with A203's pair table + H-mask, then
branch on the next tightest slot; a branch dies by EmptyBox / FC / no-room / count; the page dies when every branch
does.  This is A180/A182's assignment tree with unit propagation, with A204's cascade at every node -- NOT an LP tree.

## Rules
1. Order: at each node pick the slot with the fewest alive option rows (ties: the one H reaches); branch over its
   rows (both meeters when H does not reach it: pairs of rows, piece-compatible by A203's rule S); unit-propagate
   (a slot with one row left is instantiated without branching); coarse settings (nsub 4 / refine 2); the cascade at
   every node; depth cap 4, node cap 200, wall 900 s per pad per page; an undecided branch (cap/wall) stays ALIVE.
2. Every kill carries its trace (which branch, which clip, which round) [C: library clip trace]; a page after the
   root cascade and after every closed branch (the tree drawn as a small panel row: branch -> verdict -> seconds).
3. Start on k5_11 Y0202 (g1 then pad 0), then k5_16 Y0839, then A204's survivors in the order A204 finishes them
   (results/polyclip204.jsonl; ALIVE rows only); once you are producing rows, the coordinator stops A204.
4. Deliverables: results/cliptree205.jsonl (nid, pad, verdict, tree size, depth, seconds, killing leaves), certs/,
   pages, notes/clip_tree.md (the procedure as a lemma for any n, the PI credited, the table), registry row, LOG entry,
   docs/residue_ledger.md section 4, docs/budget.md item, status gallery collector block for kills, PAUSED.md fold-in
   for survivors with the next lever named.
