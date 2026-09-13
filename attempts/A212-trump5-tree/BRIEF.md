# A212 -- THE TRUMP5 TREE: the coarse tree with a Trump-containment gate and the tube leaf (PI, 2026-09-13 00:40).
Fable. LAUNCH-AND-EXIT.

PI: "eventually every node has to be killed in every direction that isn't trump. So for trump5, the current toolbox
should work, it just needs to check if the current node is a parent of trump, and if so, don't try to kill it, just go
straight to split. And then we use the leaf discharge rules + trump basin to clear out everything that isn't trump."

Ops (binding, as A211's BRIEF): short responses, files <= 250 lines, no monitors, no waiting turns; build, test on one
page, launch ONE detached launcher (workers commit per node, progress.md hourly), report, EXIT.  Explicit-pathspec
commits; fetch + plain merge; no pull --rebase / reset; no recursive deletes; PYTHONDONTWRITEBYTECODE=1; up to 3 workers
gated at 10 lab pythons excluding "Claude Extensions" and 3072 MB free (A211's 5 workers + A207 + the k0 cascade are
running: never touch them); BelowNormal via A210's working fix; BLAS pinned.  COPY A211's code (attempts/A211-coarse-tree/
code: coarse211, tree211, leaves211, rsplit211, inherit211, startload211, run211, fig211, worker211.sh, launch211.sh) into
code/ and extend the copies.  Pages docs/residue_map/campaigns/A212-trump5tree/; a collector block for kills.

## The three additions (state each in notes/trump5_tree.md before use)
1. GATE `contains_trump(node)`: the node's hypothesis (pins, H box, the forced slots' meeter requirements, instantiated
   roles' boxes, branch steps) is satisfied by SOME D4 image of the Trump packing z-hat (attempts/A03-upper-reconstruct/
   trump11_float.js* via A60's substrat.trump_realizes / completions.TRUMP5; docs/proofs/contraction_tube.md; k0_route.md
   section 4.2-4.3 (D)/(D') leaves; A163's refusing witnesses).  Exact rational check with the certified z-hat; a node
   that contains a Trump image is NEVER submitted to a kill rule (skipping is sound: it proves nothing); it is branched at
   once on the tightest slot / widest role (A211's rules, ROLE-SPLIT included), so the Trump image is isolated into one
   child per step.
2. TUBE LEAF (the "trump basin"): a node whose every role box (all 11 squares named: pins + H + instantiated + the
   remaining anonymous meeters localised by their rows) lies within the certified tube radius (r_c, r_theta) of one Trump
   image is the (D) leaf of k0_route.md: by Theorem T1 (contraction tube) every packing in it is that image at side
   s-hat -- uniqueness, not a kill.  Certificate: the image, the radii, the per-square containment (exact).  Use the
   tube certificates in certs/tube_*.json (verify_tube.py) -- if the certified radius is too small for the node's boxes,
   keep splitting (ROLE-SPLIT) until it fits; record the depth needed.
3. trump5 pages are c0 nodes at side s0, lambda = 1: NO PAD (pad 0 only; every leaf rule at its sharpest; no
   window-pending bookkeeping).  Non-Trump branches die by the leaf rules (CC, NO-ROOM + pockets, BASIN where a basin
   row exists for the class, NS, exact cascade last), inheriting A198/A199/A205/A206 certificates for these pages
   (Lemma INHERIT; A199's seal rows in attempts/A199-corner-seal/results/seal199.jsonl are kills too).

## Population, test, report
Test on c0_Y1033 (A182's STEP 34 no-room work exists; A189) at wall 900 s: report the gate decisions per node, the
kills per rule, and whether a tube leaf was reached.  Then the 13 alive trump5 gallery pages (c0_Y0169, c0_Y0171,
c0_Y0215, c0_Y0223, c0_Y0255, c0_Y0257, c0_Y0258, c0_Y0695, c0_Y0787, c0_Y0788, c0_Y1033, f1_L10_0003,
slack0.02_c0_Y0272), wall 1800 s, then A60's alive frontier (attempts/A60-trump5-campaign results; the census in A57's
PAUSED.md: trump5 325 records) deepest first with the price measured after 20 nodes and a STOP at 150 CPU-h.
results/trump5tree212.jsonl (page, verdict DEAD / TRUMP-TUBE / ALIVE, gate hits, tube depth, seconds), certs/, pages,
progress.md; registry row, LOG entry, docs/residue_ledger.md section 4, docs/budget.md item, PAUSED fold-in.  Report
once (the three additions as stated, the c0_Y1033 test, the launcher and where rows land, how to resume) and EXIT.
