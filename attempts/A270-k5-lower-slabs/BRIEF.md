# A270 -- THE k5 LOWER SLABS: what is certified for k5_11 / k5_16 (and trump5) on G2, G3, G4 = [3.82, 3.861637],
# what remains, and run the remainder with A268's levers.  (Coordinator's correction, 2026-09-23: the A211 pad
# 'g1' is A57's G1 SLAB (3.861637, s0], not the window; "k5 closed at the window pad" was wrong.)
Opus.  LAUNCH-AND-EXIT -- NEVER wait for a detached run.  Ops: short responses, files <= 250 lines, no monitors, no
interim messages, explicit-pathspec commits (fetch + plain merge only), PYTHONDONTWRITEBYTECODE=1, BLAS threads 1,
BelowNormal, affinity 0xFFFF, at most 4 worker python processes (RUNNING, never touch: the status loop, A262's
chain3, A263's chain, A269's trump5 re-emit + its loop and records), no recursive deletes, never edit a running
script in place (install by rename; flag-gate changes to the shared A211 chain), frozen verifiers byte-identical,
kill only your own python.exe by command line, detached launches by explicit Git Bash path.  Benchmark first.
Read first: docs/proofs/slot_crowds.md s.5 (the slab table: G1 = (3.861637, s0], G2 down to 3.847016, G3 to
3.832450, G4 to 3.82; "A57's four sides (now A96's parametric pass) remain the kill"; a G1 kill applies at s-hat
-> the uniqueness clause), attempts/A57*/notes/lemmas.md T23 (the four sides, delta_pin = 1e-2, Lemma B' slab),
attempts/A96* (the parametric pass), attempts/A211-coarse-tree/notes/coarse_tree.md (pads: zero = s0-only, g1 =
the G1 slab; S6: the pad enters through FC's slot pads and CC's lam; Lemma INHERIT (c), PAR), A229 shards,
A268 notes/terminal268.md + code (count268 / leaf268 / queue268 levers; the census after the fold: 300/303
DEAD at g1, 0 alive), A257 notes/window257.md (slab arithmetic; T_K(delta_pin): at 1e-2 a plain certificate's
width), A241 rows241.md (row sources: (A) parametric window certificate, (B) K1 climb -- k5_11 / k5_16 have
neither; the k5 classes with FULL-WINDOW rows got them from A56/A96's parametric layer).

## Task
1. STATUS, exactly: for k5_11, k5_16 and trump5, per slab G1-G4: what certificate closes the class on that slab
   (file, lemma, pad), or the alive residue (which A57/A96 tree nodes; how many).  Say which of A57's four sides
   were ever run for these classes, what A96's parametric pass certified, and whether the A211/A229 g1 kills
   (delta_pin 1e-2, slab B') transfer to any lower slab by any proved lemma (I expect not: INHERIT needs the
   child hypothesis inside the parent's; a lower pad is wider).  Correct docs/shadows/STATUS.md, A211's
   progress page and the ledger's k5 rows to say "dead on G1 (incl. s-hat)" instead of "closed at the window
   pad"; add a per-slab column.  Answer A268's question: a "class tree closed at g1" row source for rowcascade241
   is NOT a full-window row; if a per-slab row type is cheap and sound (row valid on the slab only), add it with
   its clause, else leave rows241 alone.
2. PADS g2, g3, g4 for the A211 chain: lam values (rationals) from the slab bounds, the FC slot pads and CC lam
   at those pads (cite S6), and the hypothesis each pad verdict covers.  Are the k5 frontier nodes' records
   (delta_pin 1e-2) valid hypotheses at those pads (A256 O1 arithmetic: T_K(1e-2) = 0.0257 covers depth 0.0154
   (G1) and 0.0300 (G2)? -- compute; G3 at 0.0446 and G4 at 0.0571 exceed it: then the records must be
   re-emitted at larger slack, as A269 does for trump5 -- say what slack each slab needs and price the
   re-emission).
3. RUN: benchmark 10 frontier roots of k5_16 at pad g2 with A268's levers ON (count268, leaf268, STALLED
   queue); price the 303-node frontier at g2 (and g3/g4 if the records allow); launch g2 detached if <= 150
   CPU-h (4 workers, 1800 s wall, per-shard commits, resume block, STOP files, progress page with a per-slab
   line), else report the price.  Deliverables: code/, results/ (+progress), certs/, notes/slabs270.md (the
   status table, the pad arithmetic, the price), registry row, LOG entry, ledger note, the STATUS/progress
   corrections.  Report once (<= 15 lines): the status table, the pads, the benchmark, what is launched.  EXIT.
