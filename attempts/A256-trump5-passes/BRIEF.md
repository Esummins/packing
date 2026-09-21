# A256 -- TRUMP5 PASSES: close A212's 84 alive trump5 nodes with the k5 toolkit (start-node shards, the A220 / A221 /
# A224 levers, the window pad), and write the trump5 CLOSURE ACCOUNT (PI, 2026-09-21: "start building the trump5
# tube leaf" -- the coordinator's check below shows the leaf exists; the missing piece is the pass loop + window).
Opus.  LAUNCH-AND-EXIT -- NEVER wait for a detached run.  Ops: short responses, files <= 250 lines, no monitors, no
interim messages, commit after every shard with explicit pathspecs (fetch + plain merge only; no pull --rebase, no
autostash, no reset), PYTHONDONTWRITEBYTECODE=1, BLAS threads 1, BelowNormal, affinity 0xFFFF, 3072 MB free-memory
gate per worker, no recursive deletes (rmdir single claim dirs), never delete pidfiles, never edit a running script
in place (install by rename), kill only your own python.exe matched by command line.  RUNNING, never touch: the k5
pass loop (frontier_loop.sh / loop_passes.sh / worker229.sh / run211.py, 6 workers), docs/shadows/status_loop.sh,
A254's search254, A255's runs.  Lab ceiling 12 python processes: you get at most 3 workers now; write the loop so
the count is an argument (the coordinator raises it when the k5 loop ends).  Frozen verifiers byte-identical
(verify_case.py sha 521cb01f..., verify_case_v4.py).

## What the coordinator found (verify, then build on it)
* The TUBE exists: docs/proofs/contraction_tube.md (A83 Theorem T1, 12 exact certificates, scale-ray T = 0.0571 >=
  s-hat - 3.82 at r_c = 1/625, r_theta = 21/10000; slot-ray T = 0.045 at the A60 landing radii; Lemma SEAM).
* The TUBE LEAF exists: attempts/A212-trump5-tree/notes/trump5_tree.md s.1-3 (GATE contains_trump, Lemma TUBE-LEAF,
  the aligned split; code trump212.py / tree212.py / run212.py over a frozen copy of A211's chain at b06a8203).
* results/trump5tree212.jsonl: 149 nodes (13 gallery + 136 of A60's alive frontier), PAD 0 ONLY (lam = 1, s0-only),
  ONE 1800 s wall each, 2026-09-14/15 -- BEFORE A220_NOROOM_INHERIT, A221_LANE (5x on no-room), A224_SNAP, A228's
  segfault guards, A229's --start / --cert-suffix shards and Lemma PAR.  Verdicts: 65 DEAD, 84 ALIVE, and on ALL
  149 gate_root = False, gate_hits = 0, tube leaves 0: NO alive node holds a D4 image of z-hat.  They are ordinary
  survivors of one wall (kills by EmptyBox / NOROOM / FC / CC / REACH), exactly what the k5 pages looked like before
  passes 4-13 closed 286 / 303 of them (median kill 246 s).  notes s.6: a Trump-containing page needs ~36 aligned
  cuts and its near-Trump siblings do not die in 700 s -- "where A60 / A83 discharged the real Trump residue".

## Task
1. PORT the pass machinery to the trump5 tree: run212.py must accept A229's --start / --cert-suffix (Lemma PAR,
   Lemma INHERIT from the pass-1 certificates in attempts/A212-trump5-tree/certs), honour the env flags
   A220_NOROOM_INHERIT / A221_LANE / A224_SNAP (A212's chain is a frozen COPY of A211 at b06a8203 -- either rebase
   Tree212 onto the current attempts/A211-coarse-tree/code/tree209.py chain, or port the three diffs; say which and
   why; the gate / tube leaf / aligned split stay as they are), and A228's guards + worker rc rows.  queue / worker
   / loop scripts as A229's (queue229.py, worker229.sh, loop_passes.sh) under attempts/A256-trump5-passes/code/
   with their own claims dir and STOP file; never share A211's claims or logs.
2. THE WINDOW PAD.  A212 ran pad 0 only.  The k5 pages are closed at pad g1 (the window pad) -- a g1 DEAD is the
   full-window statement, a pad-0 DEAD is s0-only / WINDOW-PENDING.  For trump5: (a) on nodes whose g1-padded boxes
   hold no contracted Trump image (gate false along Tube_scale / Tube_slot over t in [0, s-hat - 3.82] -- extend
   contains_trump to the ray: the image at depth t, exact rationals) run g1 exactly as k5 does; (b) on nodes whose
   padded boxes DO hold a ray image, the kill rules cannot work near t = 0 -- there the (D) leaf is the TUBE
   THEOREM used as a KILL for m < s-hat (no feasible point of the tube other than z-hat): state the exact lemma
   (TUBE-KILL: hypotheses = the node's pieces inside Tube_v(T, r) for every side in the pad; conclusion = no packing
   at side < s-hat, and only z-hat at s-hat -- uniqueness), cite contraction_tube.md for every step, and implement
   it as the leaf with a certificate row + verifier clause (own verifier file; the frozen ones untouched).  Report
   how many of the 84 + 65 fall under (a) and (b) BEFORE running.
3. BENCHMARK first (10 alive nodes, pass 2 with the flags, pad 0 and g1, 1800 s wall): kills, median time, price
   to completion.  Then launch the loop detached on the 84 (and the 65 pad-0 DEAD nodes at g1 -- WINDOW-PENDING
   otherwise), per-shard commits, resume block, progress page (A225's pstats block) at
   attempts/A256-trump5-passes/results/progress.md.
4. THE CLOSURE ACCOUNT (notes/trump5_closure.md, <= 150 lines): the complete chain that makes trump5 a full-window
   row: A60's tree (which c0 / ladder nodes, which certificates, s0 or window), where the Trump-containing residue
   was discharged (A36 basin, A83 tube, Lemma SEAM: delta_basin = 0.0257 at delta_pin = 1e-2 vs the crossover --
   is the seam CLOSED or still an obligation?  contraction_tube.md s.4.2 says trump5's own crossover is unmeasured),
   A212's 149, and what remains after A256.  Every link tagged [T] / [T-computed] / [M] / [C] with its file.  If a
   link is missing (e.g. the seam), say so plainly -- that is the real "tube leaf" work and the coordinator will
   brief it next.
5. Deliverables: code/, results/ (jsonl + progress.md), certs/, notes/trump5_closure.md, a page
   docs/residue_map/campaigns/A256-trump5-passes/ (the class's closure chain as a diagram: which region of the
   trump5 hypothesis each certificate family covers, undecided grey stipple never green), registry row, LOG entry,
   ledger note, docs/shadows status hook if the board reads trump5 verdicts.  Report once (<= 20 lines): (a)/(b)
   counts, the benchmark table, what is launched and how to stop it, the closure account's open links.  EXIT.
