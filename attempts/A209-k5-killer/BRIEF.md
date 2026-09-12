# A209 -- THE k5 KILLER: one composed chain over every alive non-trump5 node (PI, 2026-09-12: "we had a system to kill
every remaining non trump5 node")

Model: Fable. Short responses, files in pieces <= 250 lines, no interim messages, commit after every batch
(`git add -- <paths>; git commit -- <paths>`; fetch + plain merge only; never pull --rebase / autostash / reset; no
recursive deletes; PYTHONDONTWRITEBYTECODE=1; up to 6 worker processes gated at 10 lab pythons EXCLUDING command lines
containing "Claude Extensions" (the k0 cascade keeps its 4 slots), BLAS pinned to 1 thread, affinity 0xFFFF, BelowNormal,
6144 MB gate; never touch other campaigns' files or processes (A207 basin clip is running in parallel: read its
results/basin207.jsonl when it lands and add the basin clip as a rule); frozen verifiers byte-identical. Agent
messaging is broken; report ONCE at the end (and a short interim table file every hour: results/progress.md).
Pages: docs/residue_map/campaigns/A209-k5killer/k5killer209_<nid>.svg (+ gallery) per docs/residue_map/README.md; set
CURRENT.json to A209 (A206, A205 as fallbacks) and run refresh_current.py per batch; kills to the status gallery
collector; once A209 is producing rows the coordinator stops A206's remaining worker.

## The chain (every stage proven in its own campaign; compose, do not reinvent; page after every stage)
 0. A202 stage 0 (closed form, <= 30 s per pad) + A203 CSP (piece-pair rule S, H-consistency, mutual clip, count).
 1. A204 polygon-clip cascade to the fixed point (per-piece K', lonely, forced meeters instantiated).
 2. A205 clip tree (Lemma CT, fresh-table proviso) with A206's Rule NS (sliver splits, MAX_FRAC 0.5), A205's bar-anon
    and sharp round, and at EVERY fully named leaf: (a) A208's NO-ROOM leaf with the pocket CN bound (k = 10: A189 full
    budget; k = 9: pockets recorded and BRANCHED on -- instantiate the 10th square in each pocket of diameter < 1, cascade,
    no-room again) -- attempts/A208-noroom-leaves/code/noroom208.py, results/noroom208.jsonl; (b) A207's BASIN clip when
    available (near-simple poses of FULL slots cut); (c) the pad-0 verdict printed beside the window verdict.
    Wall 3600 s per pad per page (g1 pad = the page's window; pad 0 second), depth cap 5, node cap 300.
 3. NOTHING slower (no LP) in this campaign; survivors listed with their leaves' state and next lever.

## Population and order
 a. The 22 alive k5 gallery pages (docs/shadows/STATUS.md: k5_11 Y0130, Y0202, Y0672, Y0738; k5_16 the 18 listed) --
    reuse A205/A206 certificates as starting states where they exist (load206), else from stage 0.
 b. Then the whole k5 frontier: every alive k5_11 / k5_16 record in A57's census (attempts/A57-shadow-trees/PAUSED.md:
    1,693 alive A57/A60 records, 1,590 distinct nodes, k5_11 713, k5_16 552; the records under
    attempts/A57-shadow-trees/results/tree/k5_1[16]_interior_*/), deepest-first within a tree (aliveness descends
    containment, Lemma K1: a dead node closes its subtree), skipping nodes already closed by the gallery pages' kills;
    write a loader for tree records (A198's FP.load_page reads review_a57v4.csv only -- extend it: same record format,
    G.class_of_record, forced_items).  Budget: measure the first 20 frontier nodes and write the price per node and
    the projected total into results/progress.md before running the rest; stop and report if the projection exceeds
    400 CPU-h.
 c. Fold every kill into the A57 tree records' closure (a node kill = its subtree; ClosedTree bookkeeping as A57 does),
    the status gallery, docs/residue_ledger.md section 4, docs/budget.md, registry row, LOG entry, PAUSED.md fold-in.
Every kill: [C: library clip trace (+ A189 Lemma 1 / Lemma CN / Lemma BASIN)] with its branch / clip / round, audited
by sampling (A206's audit206b with the cap-1 two-meeter criterion); no verifier clause yet -- say so everywhere.
