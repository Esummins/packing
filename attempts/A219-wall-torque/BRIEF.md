# A219 -- the PI's wall-torque limitations, made exact and tested (2026-09-14 19:10).
Fable. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors, no waiting turns, explicit-pathspec
commits, PYTHONDONTWRITEBYTECODE=1, <= 2 python processes, never touch running workers. Pages to
docs/residue_map/campaigns/A219-wall-torque/ (geometry-checked SVGs, notes on each panel saying what it IS, times).

Read first: attempts/A218-k0-count (k0_count.md, the ring page ring_loadpath_rand_0_0569_t20.svg, count218.md),
attempts/A217-torque-probe (torque.md: Lemma W, C4/C5, the HELD/CROWD classes, stress217.analyse), docs/proofs/
k0_route.md, drain_flow_k0.md, sideband.md (B0/B0'), corner_seal.md.

## The PI's three limitations (verbatim intent) and what to do with each
L1. WLOG S < ceil(sqrt(n)): a packing of side >= ceil(sqrt(n)) is beaten (or tied) by the simple packing.  For a
    minimiser at n = 11 we already have the stronger S <= s-hat = 3.877084 (certified upper bound).  State Lemma
    CEIL n-general with its proviso (s(n) < ceil(sqrt n)), and USE the stronger bound everywhere below.
L2. "Squares cannot load along a wall without a net torque."  Make it exact.  (a) Lemma TWO-CONTACT: a square
    touching one wall at a vertex (tilt not in {0, 45, 90} deg) with exactly one other loaded contact is not in
    force balance (two forces must be collinear; the wall force is normal through the touching vertex; no edge
    normal of the square is wall-normal and no other vertex lies on that line).  So a loaded tilted wall square
    needs >= 2 loaded square contacts.  (b) Lemma ONE-TILTED: of the two meeters of a doubly-met open corner at
    least one is tilted (two flat meeters overlap).  (c) Note honestly where L2 is FALSE as stated: a flat square in
    edge-to-edge contact carries along-wall compression with zero torque (the simple packing's rows), and in the
    ring witness squares 3, 5, 10 are torque-balanced by wall + two contacts.  L2's force is on the tilted meeters.
L3. "They require squares pushing out from the centre to keep them pinned; the holders have to meet in the middle
    in a way that still torque balances."  This is the conjecture to test: Lemma RING -- at n = 11, S <= s-hat, no
    loaded four-crowd (four doubly-met open corners, every meeter loaded) is force- AND torque-balanced by walls and
    meeters alone; some meeter needs a holder that is not a meeter (an interior square pushing it toward its wall);
    and the interior holders cannot themselves balance in the room left (< 1.9 x 1.9 inside the wall bands).

## Task
1. Prove CEIL, TWO-CONTACT, ONE-TILTED (docs/proofs/wall_torque.md, n-general, n = 11 corollaries); each gets a
   Statements/Open/ axiom file (build + lean/audit.py exit 0, no sorry).
2. TEST Lemma RING on A217's 8 HELD four-crowd witnesses and the 185 forced CROWD four-crowds: drop the tilt-floor /
   crowd rows, keep the contact structure (which rows are loaded), solve the free FJ multiplier LP (force + torque
   balance, multipliers >= 0, walls + listed contacts only).  Report per witness: feasible (a free torque-balanced
   ring exists -- then the PI's L3 is false; draw it) or infeasible with the torque residual per meeter and WHICH
   meeter needs the extra holder and in which direction (is it "out from the centre", toward its wall?).  Then add
   one interior holder square at the best pose (A217's search with the ring structure forced and the floor removed,
   S <= s-hat) and see whether 11 squares ever balance.  Pages: the ring with its torque residuals; the best
   11-square free attempt with its residual.
3. State the finite structure question exactly (contact structures of a loaded four-crowd: meeters x {wall,
   partner, <= 2 holders}, holders in {other meeter, interior square}), count the structures, and price the H-LOC
   certificate (fj_census_k0.md s.4, 0.78 s per structure) for deciding all of them at S <= s-hat -- that is the
   proof of RING if every structure is infeasible.  Say clearly what RING would and would not close: it excludes
   LOADED four-crowds; rattler crowds (61 of 70 doubly-met corners at genuine k0 FJ points have both meeters
   unloaded) need the teleport / drain route, say which lemma covers them and whether it is proved.
4. Deliverables: wall_torque.md, Open/ files, results/ring219.md (+ jsonl), pages, registry row, LOG entry,
   ledger s.4 note.  Report once (<= 25 lines: the three lemmas' status, RING feasible-or-not per witness class, the
   structure count and certificate price, what closes) and EXIT.

## Addendum 2b (PI, 19:30) -- the second-order test
On the ring witness square 6 is a two-force strut (loaded contacts 4 and 7 only, collinear through the two contact
vertices, floor contact unloaded, moment about the 7-contact -2.7e-11).  A clockwise rotation of 6 about its
7-contact is a FIRST-ORDER FREE MODE (1 mrad: floor +6e-4, 7 held, gap to 4 -5e-7, quadratic).  The ring is
stationary, not stable; the stress LP cannot see it.  (i) Decide whether the side decreases at second order along
that mode (a sigma-minimiser is a local minimum: an FJ point with a zero mode along which s decreases at second
order is excluded).  (ii) Lemma STRUT (any n): a square whose loaded contacts are exactly two collinear vertex
contacts has rotation about either contact as a first-order free mode; state the second-order exclusion (reduced
Hessian of the side on the first-order zero modes of the active set) and run it on every HELD and CROWD four-crowd
witness; count the saddles.  Deliverables: results/second_order219.md, a page for the ring's mode.
