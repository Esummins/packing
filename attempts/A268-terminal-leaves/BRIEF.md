# A268 -- TERMINAL LEAVES: the whole k1-5 compute residue is one object -- a start node that survives every wall
# with no new children.  Diagnose where its wall goes and build the lever.  (2026-09-23.)
Opus.  LAUNCH-AND-EXIT -- NEVER wait for a detached run.  Ops: short responses, files <= 250 lines, no monitors, no
interim messages, explicit-pathspec commits (fetch + plain merge only), PYTHONDONTWRITEBYTECODE=1, BLAS threads 1,
BelowNormal, affinity 0xFFFF, at most 4 python processes (the machine rebooted at 07:35 today; the only lab
processes now are the status loop, A262's chain3 and A263's chain -- never touch them), no recursive deletes,
never edit a running script in place, frozen verifiers byte-identical, kill only your own python.exe by command line,
detached launches by explicit Git Bash path.  Benchmark before estimating.
Read first: attempts/A211-coarse-tree/notes/coarse_tree.md (leaf rule order CC -> no-room -> basin -> NS -> ROLE-SPLIT
-> exact cascade; Lemmas CT / INHERIT / POCKET / ROLE-SPLIT), A220 (exact-first budgeted round, A220_NOROOM_INHERIT),
A221 (lane cover), A224 (SNAP), A229 (start-node shards / Lemma PAR / queue229), A230 (EPS all-candidates,
NS-at-wedge, taper -- flags A230_*, default OFF, benchmark never landed), A228 (guards), the A257 sibling table
(results/seam_table257.md: two FAR siblings ALIVE, leaf reason "every forced slot has two named meeters after the
exact cascade and the sharp round"), the A256 progress page (87 trump5 start nodes ALIVE at pad 0, depths like
R.4.3.2.p1.p1.2.2.2.2.2.2.2.x, 1800-2250 s each), the k5 pass loop's record: passes 14-40 (09-21 09:29 -> 09-22
22:10) re-ran the SAME 70 start nodes of 17 k5 pages with ZERO kills -- e.g. k5_16_interior_Y0384 g1
R.2.1.5.p2.p2.2.2.2: 31 rows, every one ALIVE with n_nodes 1, depth 0, no NS / pocket / role split, 0 exact rounds,
2800-5000 s (the 1800 s wall overrun) -- i.e. the start node's OWN cascade never finishes.

## Task
1. DIAGNOSE on three representatives (one k5 start node above, one trump5 survivor, one A257 far sibling): run
   with timing instrumentation (per stage: coarse cascade rounds, exact cascade, each leaf rule, the sharp round),
   wall 7200 s, and report where the time goes and WHAT THE NODE LOOKS LIKE (pieces per role: widths, tilt ranges;
   which slots are forced; pocket cover; which rule came closest and by how much).  Is it (a) the exact cascade
   too slow at this depth (then a budget / early-exit lever), (b) a genuine fixed point of every rule (then a new
   branching), or (c) the wall overrun itself (2800-5000 s in a 1800 s wall: the guard does not fire)?
2. THE LEVER, by what 1 shows: candidates -- (i) forced ROLE-SPLIT on the widest named role when the cascade
   stalls (bisect tilt or centre; sound by Lemma ROLE-SPLIT); (ii) A230's EPS all-candidates + NS-at-wedge switched
   ON (benchmark off/on on the three nodes); (iii) exact cascade with a per-round budget and inheritance of the
   coarse pieces (A220's round made resumable across passes: a pass that runs out of wall must leave the node
   STRICTLY smaller for the next pass, else the loop spins -- add that invariant as a check: a pass that returns
   the node unchanged is recorded 'STALLED' and the loop must not requeue it); (iv) a longer wall for terminal
   nodes only.  Implement the one(s) the diagnosis supports, flag-gated, in the A211 chain (install by rename,
   never edit a running script), with certificates + the existing verifier clauses (a new leaf gets its own).
3. BENCHMARK on the three, then on 10 k5 + 10 trump5 start nodes: kills, median time, price for the 70 + 87 + 2.
   If priced within ~100 CPU-h, launch the k5 remainder detached (4 workers, the STALLED invariant on, per-shard
   commits, resume block, STOP file) and report; else report the price and the geometry of the survivors (drawn:
   one page per representative, pieces and forced slots, geometry-checked, a note per panel saying what it IS).
4. Deliverables: code/, results/terminal268.md (+jsonl), notes/terminal268.md (the diagnosis, the lever's
   soundness with citations, the STALLED invariant), pages, registry row, LOG entry, ledger note.  Report once
   (<= 15 lines): the diagnosis per representative, the lever, the benchmark table, what is launched.  EXIT.
