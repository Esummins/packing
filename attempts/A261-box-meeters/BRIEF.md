# A261 -- BOX-MEETERS: the structure obligations left after A258 -- the two meeters of every corner box are wall
# touchers on its two walls (O1, O2), and the window exclusions as certificates (O3).  (PI theory day, 2026-09-21.)
Fable.  LAUNCH-AND-EXIT -- NEVER wait for a detached run.  Ops: short responses, files <= 250 lines, no monitors, no
interim messages, explicit-pathspec commits (fetch + plain merge only), PYTHONDONTWRITEBYTECODE=1, ONE heavy python
process at most (BelowNormal, affinity 0xFFFF; sub-minute helpers fine); detached launches call Git Bash by explicit
path.  RUNNING, never touch: the k5 pass loop, A256's loop256, A257's pilot257, the status loop, A258's run258.sh
side, A259's run259.sh chain.  A260 runs in parallel on the ROOM obligations (locked wall, corner notch).
Read first: docs/proofs/normal_ring.md + attempts/A258-normal-ring/notes/family258.md VERSION 2 (the normal-form
theorem: lexicographic potential Phi1 #wall touchers, Phi2 row vector, Phi4 RETREAT, Phi3 slide; properties P1-P4;
the family D / D' / D^h; [M] least sides: mixed senses + + + - from 3.9298, + - + - 3.9484, + + - - 3.9767; type F
(flat row) >= 3.9347; row of three >= 3.9814; single toucher never meets both end boxes [T]; obligations O1
TOUCH-NORMAL, O2 the two meeters of a box lie on its two walls, O3 certificates for the [M] least sides),
common_sense.md (VALUE-WLOG; NORMAL-CELL; the corpus: 520 doubly-met corners with NO wall toucher, all at s >= 4),
sideband.md (B0/B0': every way two squares both meet the open corner box), wedged_seal.md (a meeter touching both
walls is alone), construct_towards.md (NOT-SELF-SUFFICIENT), k0_count.md (PUSH), family250.md, peel.md
(BAND-COUNT: at most 4(m-2) squares in the unit band; the 8m-20 cells), ring_swap.md (CELLS, cells of any pose).

## The statement to reach
BOX-MEETERS(11): in a maximiser of the lexicographic potential that is family-stuck at s in [3.82, s-hat], every
corner box is met by exactly two squares, both wall touchers, one on each of the box's walls, and the eight are
distinct -- so the eight form four wall pairs and A258's classification (rows of two of one sense on the window)
applies.  With A259 / A260's room (every free square contains O => capacity 1) this gives FAMILY-STUCK-EXIST(11).

## Task
1. O1 TOUCH-NORMAL.  A box meeter C that touches no wall: find the exchange or motion that brings a meeter to the
   wall without losing the side -- candidates: CELLS on a wall-touching cell T' of C's tilt under C (met only by C
   and what?); a straight slide of C toward the wall (what blocks it must itself be a lower box meeter -> take
   that one); Phi1 already maximises the number of wall touchers, so state exactly what P1 gives and what is
   missing.  Below 4 the corpus has NO doubly-met corner without a wall toucher -- find out why (BAND-COUNT?  the
   band under a floating meeter is too thin for anything but a toucher?) and prove it on [3.82, 4) or the window.
2. O2 TWO WALLS.  Both meeters on the SAME wall of the box (a row start and a second-layer square, A255's
   rand_0_0441 pattern; or two floor touchers) -- show it is not family-stuck or reduces (the box's other wall
   slot c01 then needs meeters: count them with NOT-SELF-SUFFICIENT / the family condition), or find the witness.
   A THIRD box meeter: what does the family condition say (|M| counts help, so it is allowed) -- does it break
   the classification?  A258 found none on the C4 slice; settle it on the window.
3. O3 CERTIFICATES for the window exclusions.  A258's least sides come from an exact LP in (a_w, s) per tilt
   vector on an 11^4 grid: make it box-valid (interval tilt boxes, LP dual certificate valid over the box, outward
   rounding; own verifier) and certify: no mixed-sense ring of pairs, no flat row, no row of three at side <=
   3.8771 (margin 0.053 in the side -- coarse boxes should do).  Benchmark 100 boxes, then launch detached if
   <= 50 CPU-h.
4. General m: which of 1-3 are m-free (the corner geometry is), which are m = 4 only.
5. Say plainly what is [T] / [T-computed] / [M] / [C]; the chain to ONLY-RING(11) in value form; the exact
   remaining obligations; every counterexample drawn.  Deliverables: docs/proofs/box_meeters.md,
   Statements/Open/BoxMeeters.lean (build + audit 0 sorry; AUDIT.md rows), code/, results/, certs/ (+ verifier),
   pages in docs/residue_map/campaigns/A261-box-meeters/ (a floating meeter and the move that lands it; the
   same-wall pair and why it fails; the certified exclusion map over the tilt grid; geometry-checked, a note per
   panel saying what it IS, slivers with a 10x inset, undecided grey stipple never green), registry row, LOG
   entry, ledger s.4 note.  Report once (<= 20 lines).  EXIT.
