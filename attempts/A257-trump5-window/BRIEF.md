# A257 -- TRUMP5 OVER THE WINDOW: slack-pin records (A256's O1) and the seam (O3) -- the real tube work.
Opus for the engineering; escalate any soundness question to a note, do not guess.  LAUNCH-AND-EXIT -- NEVER wait
for a detached run.  Ops: short responses, files <= 250 lines, no monitors, no interim messages, commit after every
shard with explicit pathspecs (fetch + plain merge only), PYTHONDONTWRITEBYTECODE=1, BLAS threads 1, BelowNormal,
affinity 0xFFFF, 3072 MB free-memory gate, no recursive deletes, never delete pidfiles, never edit a running script
in place, kill only your own python.exe by command line; detached launches must call Git Bash explicitly (plain
`bash` can resolve to WSL).  RUNNING, never touch: the k5 pass loop (6 workers), A256's loop256 (3 workers), the
status loop, A254 / A255 jobs.  Lab ceiling 12 python processes: you get ONE process until the coordinator says
otherwise; make the worker count an argument.  Frozen verifiers byte-identical.
Read first: attempts/A256-trump5-passes/notes/trump5_closure.md (the chain; O1: 146 of A60's 149 trump5 records carry
pin cores delta_pin = 3.08e-8 so T_K < 0 -- they reach NO side below s0; the k5 pages carry 1e-2; T_K(1e-2) = 0.0257
covers g1 (0.0154) but not the whole window (0.0571) -> two slabs; O3: delta_LP(trump5) never scanned -> the seam is
an obligation; ray gate ray256.py: class (b) EMPTY on today's records; Lemma TUBE-KILL on the slot ray, verifier
verify_tubekill256.py, OFF by default), docs/proofs/contraction_tube.md s.4 (Lemma SEAM, s.4.2-4.4 compute
obligations), attempts/A60-trump5-campaign (notes/ledger.md s.1, how records / cores are emitted, the ladder, the
(K) and (D) leaves), attempts/A57 (how the k5 records got delta_pin = 1e-2), A211 notes/coarse_tree.md S6 (the pad
never touches the pins), A82 (the crossover scans for k4_08 / k4_11), A212 notes s.3 (aligned split), A229 shards.

## The question
What is the cheapest SOUND way to a full-window trump5 row?  Two candidate routes -- price both by benchmark:
 R1 RE-EMIT: regenerate A60's trump5 records with slack pin cores (delta_pin = 1e-2 for the g1 slab; the second
    slab below it per contraction_tube s.4.2), then A256's loop at the window pads.  With slack pins the H boxes
    and the root hypothesis WIDEN: some nodes may now hold a ray image (class (b) non-empty) -- there TUBE-KILL
    (slot ray) is the leaf and the aligned split (A256 O4) must work on A211's current _expand.
 R2 RE-ROOT: skip A60's records; run the coarse tree from the trump5 CLASS ROOT (five slack pins at 1e-2, H free)
    at each slab with the current toolkit (kills now cost a median 30 s per start node on trump5, A256's
    benchmark), gate + aligned split + TUBE-KILL isolating the image.  Fewer inherited certificates, one uniform
    hypothesis, Lemma INHERIT unusable from A60 -- price it.
In both, the SEAM is where the tree must hand the near-Trump siblings to the tube: a sibling just outside the tube
radii must die by the ordinary rules.  A212 s.6 measured one such sibling (F1 0.12 deg off the image) NOT dying in
700 s under the old rules.  That is delta_LP vs delta_basin made concrete.

## Task
1. State exactly what a slab is for trump5 (side range, pin slack, which pad, which tube depth range) and prove the
   two-slab cover of [3.82, s-hat] from Lemma SEAM's numbers; or say how many slabs are really needed.  Note.
2. SEAM PILOT (the decisive measurement, do it before pricing either route): build the synthetic Trump-containing
   page as A212 s.6 did, with slack pins 1e-2, at g1; run the current chain with the gate, the aligned split
   (port it to the current _expand -- A256 O4) and TUBE-KILL ON; measure: aligned cuts to reach the tube, and for
   EACH near-Trump sibling whether it dies, by which rule, in what time (flags A220/A221/A224 on; try A230_EPS).
   Report the sibling table; the siblings that do not die in 1800 s are the seam gap -- draw the worst one (page
   in docs/residue_map/campaigns/A257-trump5-window/, geometry-checked, a note per panel saying what it IS).
   If a bigger tube (A83's (T, r) curve: smaller T per slab buys larger r) closes the gap, say which certificate
   to re-emit with verify_tube.py and do it if it is minutes.
3. PRICE R1 and R2 from benchmarks (10 nodes each), recommend one, and LAUNCH its first slab detached with one
   worker (resume block, STOP file, per-shard commits, progress page).  Do not launch a campaign priced over
   ~300 CPU-h; report the price instead.
4. Deliverables: notes/window257.md (slabs, the seam pilot, the prices, the recommendation; every claim tagged
   [T] / [T-computed] / [M] / [C]), code/, results/, certs/ (+ own verifier clauses), the page, registry row, LOG
   entry, ledger note, an update of A256's closure table rows O1 / O3 / O4.  Report once (<= 20 lines).  EXIT.
