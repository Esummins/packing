# A232 -- prove STEP on the WINDOW by certificates: the SWAP leaf for the k0 cells (PI, 2026-09-15 17:30: "can we
# prove STEP against the window? we only need it true <= s-hat for the search to ignore k0 entirely").
Opus. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns (cell runs detached,
per-cell commits, resume block), explicit-pathspec commits, PYTHONDONTWRITEBYTECODE=1, at most 2 python processes
(BelowNormal, affinity 0xFFFF; the lab runs 6 k5 workers), never touch running workers or the A57/A211 state;
frozen verifiers untouched (verify_case.py sha 521cb01f..., verify_case_v4.py) -- the new leaf gets its OWN verifier
clause, byte-identical old paths.  Read first: ring_swap.md + lean/.../Statements/Open/RingSwap.lean (swap_packing
and cells_swap are PROVED theorems: replacing a set X of squares by squares that lie in the container and are
interior-disjoint from every square NOT in X gives a packing at the same side), realign.md s.8 (Lean
fourcrowd_dead_of_step_kill: at n = 11, STEP + k1-a excludes four-crowds), k0_route.md s.3 (K0-FREE, k1-a = the k1_00
tree's certified kill: any packing in W with a settled corner is dead / Trump), the k0 lane: docs/shadows/k0v4/
(the 11 converged-alive k0_00 cells l1_071 ...), attempts/A185-boxed-windows-clause/code/{run185,winlp185,
verify_case_v4}.py (the boxed-windows clause: a cell = role boxes over the window W; how cells are loaded, split,
certified), A183-cascade-resume, A171/A172 multibox (reach sets: union of Q over a role box; exact miss tests
chordlane.box_misses_cell_exact), A213/A214 kernels.

## The leaf (sound by swap_packing + k1-a; no LP, no load, rattlers included)
At a k0 cell (11 role boxes over W, every corner box doubly met by hypothesis), pick a corner c and its slot square
S = the settled unit square at c.  Let X = the set of roles whose REACH SET (union of poses over the role's box)
meets int(S) -- these are the squares that could be in S's way.  If there are placements P_1..P_{|X|-1} of unit
squares (fixed poses, inside the container at every side of W -- use the window's smallest side for containment and
the largest for nothing: the exchanged squares stay put, so fixed poses inside [0, s_min]^2 are inside every
container of W) such that S, P_1, ..., P_{|X|-1} are pairwise interior-disjoint and each misses the reach set of
every role NOT in X, then EVERY packing in the cell exchanges (swap_packing with X) into a packing at the same side
with the corner c settled, which k1-a kills (side >= s-hat, and = s-hat only for Trump, which is not k0).  So the
cell is DEAD by SWAP-LEAF.  Certificate: c, X, the poses of S and the P_i (rationals), the pairwise disjointness,
containment, and one exact miss certificate per (P or S, role not in X); verifier clause = these checks + the k1-a
citation.  |X| = 2 with X = the two corner meeters is the PI's STEP; |X| = 1 is K0-FREE; larger X is allowed (the
leftovers may go anywhere free).  The leftover search: candidate poses on a grid of centres x tilts inside the
cell's free region (the complement of the non-X roles' reach sets), verified exactly; prefer axis-aligned P.

## Task
1. Implement swapleaf232.py against A185's cell format: for a cell, for each corner c (4) and the induced X: search
   the placements, verify exactly, emit the certificate; also try X = the two meeters only.  Verifier clause in a
   NEW verifier file (verify_swap232.py, stdlib + exact rationals), never edit the frozen ones.
2. Run it on the 11 k0_00 cells (both the cell as recorded and, where it fails, one round of A185's own split with
   the leaf re-tried on the children -- bounded: <= 64 children per cell, wall 600 s per cell).  Report per cell:
   DEAD by SWAP-LEAF (which corner, |X|, seconds) / undecided (which corner came closest: the reach-set overlap that
   blocked the leftover, drawn).  Pages docs/residue_map/campaigns/A232-swap-leaf/<cell>.svg: the cell's role boxes,
   S and the P_i, the reach sets of the non-X roles (grey), per the lab's drawing rules.
3. Lean: Statements/SwapLeaf.lean -- the leaf's soundness as a THEOREM from swap_packing (fixed poses, disjointness
   hypotheses as stated) and the k1-a hypothesis; build + audit exit 0, no sorry.
4. Say plainly what closes: if all 11 cells die, k0_00 is closed by certificates and the k0 obligation is
   discharged for the window (STEP proved on W cell-wise, not analytically); if some survive, what geometric fact
   blocks them and whether A185's finer split or a larger X would reach them (price it).
5. Deliverables: code, results/swapleaf232.md (+jsonl, certs), the Lean file, pages, docs/proofs/swap_leaf.md
   (the leaf, its soundness, the results), registry row, LOG entry, ledger s.4 note.  Report once (<= 15 lines)
   and EXIT.
