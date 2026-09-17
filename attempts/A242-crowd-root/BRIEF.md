# A242 -- STUCK-4(11) by certificate: the k0 cascade from the CROWD ROOT with the new leaves (PI, 2026-09-16 15:00:
# "given those results, is there any way we can show that no stable k0 packing exists below the trivial side?").
Opus (soundness statements checked against the cited proofs; escalate a theory question to a note, do not guess).
LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns (the cascade runs detached,
per-cell commits, resume block), explicit-pathspec commits, PYTHONDONTWRITEBYTECODE=1, at most 2 python processes
(BelowNormal, affinity 0xFFFF; the k5 frontier workers / loop, A238's sweep and A241's parametric campaign are
running -- never touch them), frozen verifiers untouched (verify_case.py sha 521cb01f..., verify_case_v4.py; a new
leaf gets its own verifier clause), read-only libraries wrapped never edited.
Read first: k0_route.md s.4.2 (the CROWD ROOT H_B: the k0 hypothesis with the EIGHT corner meeters boxed -- A232
found |X| = 5 there and said the leaf belongs at that root, not at the 11 one-role cells), ring_swap.md +
swap_leaf.md (A232: swap_packing / cells_swap theorems, the SWAP leaf and its verifier), local_lock.md (A233: at the
Psi-minimal optimum every meeter of a doubly-met corner is LOCKED, so "stable" = loaded, rattlers excluded), A239's
notes/rings_below_4.md + docs/proofs/wedged_seal.md (reach inequality R(theta, delta) >= s - 2, GEAR-RATIO, LEVER:
a torque-balanced contact ring needs s > 4; every constructed ring below 4 is FJ-infeasible and its pocket holds
ONE square; WEDGED-SEAL: a meeter touching both walls is alone), pocket_waste.md (A237: pocket capacity decidable
per pocket in 0.1 s; PIERCE lemma in Lean), ring_capacity.md (A236: the count never closes -- the shape must),
noroom.md + A189 noroom189 (Lemma 1: DEAD iff sum of pocket LANE values < m free squares -- the m-square no-room,
here m = 3 = 11 - 8), A221 noroom221 / pocket221 (pocket-rooted clip, parent-pocket inheritance), A171 multibox
(pieces, per-piece cores K': the sound over-approximation of the free region is container minus the meeters' CORES,
never minus their reach sets -- direction matters), local_certificate.md (Theorem LOCAL, Lemma STAB: an LP / FJ
infeasibility certificate valid over a box), A188 line certificates, A185's cell format and verify_case_v4.

## The statement and the route
STUCK-4(11): no teleport-stuck (all four corner boxes doubly met) LOCKED packing of 11 unit squares has side < 4.
It covers the window [3.82, s-hat] and, with A233 (the Psi-minimal optimum is locked if it is a four-crowd) and
K0-FREE, it closes k0_00 for the value; "stable" = locked is the PI's word for it.  Route: a CASCADE rooted at H_B
(the 8 meeters boxed: each in its corner box, WEDGED-SEAL forbids touching both walls, PUSH's floor/wall split),
side s in [3.82, 4) as a parameter (or the window first, then extend), branching on the meeters' boxes (centre /
tilt bisection, the A211 coarse-tree machinery), with THREE leaves, each certified over the whole cell:
  L1 NO-ROOM(m = 3): the three non-meeter squares must fit in container minus the union of the 8 meeters' CORES
     over the cell; A189 Lemma 1 with A221's pocket cover: DEAD iff sum LANE(pocket) < 3.  (A239: capacity 1 on
     every constructed ring; the shape kill of A236/A237 made sound over a box.)
  L2 FJ-INFEASIBLE over the cell: the locked crowd's force / torque balance with walls + the 8 meeters + at most
     3 interior squares (whose poses are anonymous: use the sound relaxation -- any interior contact is a row with
     an unknown but bounded position; or restrict L2 to cells where L1 has shown capacity <= 1 so the interior is a
     single square, then enumerate its contact structure) -- Theorem LOCAL's certificate form; cite exactly what is
     proved about box-valid FJ certificates and use only that.
  L3 REACH / GEAR: A239's reach inequality and LEVER as box tests (a wall whose two crowds cannot span it in
     contact and whose gap admits no bridging interior square -- by L1's pocket -- leaves a corner meeter without
     its along-wall holder; state the exact soundness argument from HOLD + CHAIN, or drop L3).
Every kill = a certificate for the cell's hypothesis; the cascade's completeness = the union of cells covers H_B.

## Task
1. Build H_B as the root in A185's cell format (or A211's page format if the coarse tree loads it): 8 boxed roles
   with the crowd hypothesis (each corner box met by both of its meeters; one touches at most the floor, one at
   most the wall -- cite WEDGED-SEAL / PUSH), 3 anonymous squares, side parameter.  Say exactly which hypothesis
   the root covers and why it is all of "teleport-stuck k0 below 4" (D4 symmetry reduction allowed, cite).
2. Implement L1 (A189/A221 with m = 3 over the cell's cores), L2 (only in the form the local-certificate theorems
   license), L3 (only if sound); wire them into the cascade with the A211 branching; certificate + verifier clause
   per leaf; audit sampling.
3. RUN from the root, detached, wall 2 h per cell, shards as A229 if the tree fans out; report kills by leaf, cells
   alive at the wall (drawn: the cell's meeter boxes, the pocket, which leaf came closest), depth, CPU-h so far, and
   the PRICE to completion from the first 50 cells (benchmark before estimating).  If L1 alone closes most cells
   (expected below ~3.95), say so; if cells survive, say what geometry they show.
4. Deliverables: attempts/A242-crowd-root/{code,results/crowd242.md (+jsonl),certs,logs,notes/crowd242.md (the
   root hypothesis, the leaves' soundness with citations, the price)}, pages docs/residue_map/campaigns/
   A242-crowd-root/ (root, first kills, survivors), Statements/Open/Stuck4.lean (STUCK-4(11) as a documented axiom
   + the consequence chain to k0_00 via A233's theorems and K0-FREE; build + audit, 0 sorry), registry row, LOG
   entry, ledger s.4 note.  Report once (<= 15 lines) and EXIT.
