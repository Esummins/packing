# A233 -- an ANALYTIC reason for one simple square, any n (PI, 2026-09-15 17:50: "I'd still love an analytical
# reason for at least one simple square, since that would generalise up and allow us to ignore k0 for higher n
# without re-searching").
Fable. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns, explicit-pathspec
commits, PYTHONDONTWRITEBYTECODE=1, <= 1 python process (BelowNormal, affinity 0xFFFF; the lab runs 6 k5 workers +
A232), never touch running workers.  Pages to docs/residue_map/campaigns/A233-local-lock/.
Read first (the week's results, all in docs/proofs/): one_flush.md (ONE-FLUSH <=> UNCROWD; CROWD-ABOVE: crowds exist
at O(eps) above every record, so NO local charge -- area, chord, side -- can prove it; the statement is about the
OPTIMUM), ring_swap.md (SWAP, CELLS, RAISE), realign.md (A231: after a corner swap the fixed-tilt shrink is strictly
side-lowering on 783/792 witnesses and never blocked; STEP + k1-a excludes four-crowds at n = 11 in Lean; the
obligation is STEP: a corner swap exists), two_grains.md, wall_torque.md (RING holds on 193/193: no loaded
four-crowd balances by walls + meeters alone; the deficit is an along-wall force toward the corner), k0_count.md
(PUSH, HOLD proved; the 12 > 11 count refuted by the 9-square ring), torque.md (rattler crowds: 61/70 doubly-met
corners at genuine k0 FJ points have both meeters unloaded), k0_route.md + drain_flow_k0.md + theorem_u.md + drain_sel.md
(the lab's extremal route: the k-MAXIMAL sigma-minimiser, teleport-stuck; NOCRIT-SEL, Lemma ROT, RES-LOCK: at that
minimiser every intruder of a doubly-met corner is LOCKED -- 3.3 square-square rows + 1 wall row per intruder --
and the ledger's own analytic candidate: LOCK-FREE+(< 4), "a supply count: the crowd arms cannot furnish three
square rows to all eight corner members at side < 4", 0 counterexamples in every corpus), lockfree.md, h10_stuck.md.

## What an n-general proof must look like (from this week's eliminations)
Every local charge fails (crowds are O(eps)-cheap); rotation of the container is stable; the count is n = 11-only;
the click's monotonicity fails near 45 deg.  What has NOT failed: (i) the EXTREMAL choice -- among the minimisers
take the k-maximal one (Theorem U), so the packing is teleport-stuck and (RES-LOCK) every corner meeter is locked
by loaded rows; (ii) the LOCAL structure of a lock in a CONVEX corner -- PUSH (the two meeters push each other out
along their walls), HOLD (a pressed meeter has a holder toward the corner along its wall), RING (walls + meeters
alone never balance), the PI's gear rule (a holder must itself be held; the chain along a wall ends only at a wall
row, a flush square, or the next corner's crowd -- a ring); (iii) LOCALITY: every row partner of a meeter touches
it, so lies within distance sqrt2 of its centre: the lock of corner c is decided inside the corner ARM
A_c = [0, 1 + sqrt2 + 1]^2 (n-independent), and the four arms are disjoint once s > 2(2 + sqrt2) ~ 6.83, i.e. for
n >= 47 the corner locks are INDEPENDENT local problems; below that the finitely many n are the survey's cases.
Target: Theorem LOCAL-LOCK (any n): at a k-maximal sigma-minimiser below ceil(sqrt n) no corner box is doubly met
by locked meeters -- because the rows a locked pair needs cannot all be supplied from inside the arm by squares
that are themselves in balance (a supply / torque count in the convex corner, the PI's gear rule made exact), and
the only way to supply them from outside the arm is a wall chain to the next corner, i.e. a ring, which RING (to be
proved in the local form) forbids.  Hence a K0-FREE corner exists and teleports: ONE-FLUSH(n) for all n.

## Task
1. Make the extremal route exact for general n: state Theorem U / k-maximal minimiser / RES-LOCK in n-general form
   (which of them are proved n-general already, which are n = 11 in their present form -- read the docs and say).
2. Prove the LOCALITY lemma (row partners within sqrt2; the arm; independence of the four arms for large s) and
   state the local lock problem exactly: a finite list of contact structures inside one arm (meeters x {wall,
   partner, holders in the arm}, with the arm's squares in balance) -- this is A219's structure census but LOCAL
   (arm-sized, not 2.6e11): count it.
3. Attempt the supply / torque count in the arm with the PI's gear rule: a holder chain along a wall inside a convex
   corner must end at a wall row or leave the arm; leaving the arm = a wall chain to the next corner (ring) --
   prove RING in the local form (walls + meeters + arm holders cannot balance the two meeters of an open corner
   without an along-wall force from outside the arm) or find the exact obstruction; test every step on A217's
   witnesses restricted to the arms (the 193 four-crowds, the 883 genuine FJ points' corners).
4. Deliverables: docs/proofs/local_lock.md (the theorem or the exact remaining local obligation, n-general, with
   the n = 11 corollary and the finite-n caveat for s < 6.83), Statements/Open/LocalLock.lean (documented axiom +
   the consequence ONE-FLUSH(n) as a theorem from it and the extremal route's hypotheses; build + audit, 0 sorry),
   pages (an arm with its structures; the ring witness's arm), registry row, LOG entry, ledger s.4 note.  Report
   once (<= 20 lines: what is proved, what the local obligation is, whether it is finite, what closes) and EXIT.
