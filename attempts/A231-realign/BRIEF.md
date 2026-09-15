# A231 -- REALIGN: how a grain re-aligns once one of its corners is settled (PI, 2026-09-15 09:50: "any actual
# assertion would require us to make some statement about how the grain re-aligns -- the grain that's now corner
# settled").
Fable. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns (long runs detached,
per-row commits, resume block), explicit-pathspec commits, PYTHONDONTWRITEBYTECODE=1, <= 1 python process
(BelowNormal, affinity 0xFFFF), never touch running workers (pass-6 p6a/p6b/p6c; A229/A230 benchmarks).  Pages to
docs/residue_map/campaigns/A231-realign/.  Read first: two_grains.md (A223: the click is real on the ring -- joint
grain rotation 70->90 / 20->0, side 4.11 -> 4.00 monotone -- but the chain formula is NOT monotone toward alignment:
Lambda rises 3.886 at 45 deg -> 4 at alignment; FOUR-WALL <=> STUCK-4), grain_flood.md (chain menu Lambda, Y, D, F_T;
kink minima theta* = 48.435 deg, theta_c = 41.565 deg; Trump's own side is a chain formula; Theorem CONT; INHERIT),
descent.md D3 + descent_grains.md s.6 (common-tilt / slide moves), ring_swap.md (CORNER-SWAP at >= 1 corner holds on
26/26 tested four-crowds; the swap leaves a settled corner square + one leftover), one_flush.md (A226: ONE-FLUSH <=>
UNCROWD, the improvement statement; CROWD-ABOVE crowds exist arbitrarily close to any record), A223 code
(click223 / the chain-formula fit), A222 code (the corner swap), A217 witnesses.

## The assertion to make exact
Rotation of the container is stable and the teleport is blocked, so the only exclusion of a four-crowd is an
IMPROVEMENT: settle one corner (CORNER-SWAP: the two meeters -> the settled square S + one leftover), then the GRAIN
that now contains S re-aligns (its members in contact with S rotate toward S's alignment along the chain, Theorem
D3's common-tilt move anchored by S) and the side drops below the start -- so the four-crowd was not optimal.
Lemma REALIGN (candidate, n-general): let G be a grain in contact with a settled corner square S along a wall.
(a) FLUSH SIDE: if G's tilt is on the flush side of its chain formula's minimum (theta below theta_c for the
    families where the formula decreases toward alignment), the anchored common-tilt move of G toward alignment is
    feasible (lean contacts slide, Lemma LEAN-SLIDE) and side-non-increasing, and ends flush: the packing's side is
    >= its flush side (Lemma FLUSH gives >= ceil(sqrt n) if the whole configuration goes flush; otherwise the
    chain formula of the remaining tilted part).
(b) KINK SIDE: if G's tilt is at or beyond the minimum, G re-aligns to the kink (Trump's 40.18 deg seam, S07's 45):
    the endpoint is a packing with a settled corner and a diagonal seam -- a member of the k >= 1 classes whose
    trees are certified, so the k0 packing's side is >= that class's minimum.
Together: every four-crowd drains to a k >= 1 packing at no larger side -> ONE-FLUSH at that n.  The gaps to find:
does the swap's leftover square fit (STEP) and stay out of the re-alignment's way; is the anchored move feasible
against the OTHER grains (the opposite-handed one meets G at the lean); is the side monotone along the anchored
move (this is where A223's non-monotonicity must be reconciled: the anchor changes the chain -- S is flush, so the
chain through S has a flush segment and the formula's minimum moves).

## Task
1. TEST first: for the ring rand_0_0569|t20 and all 193 four-crowds (A217 HELD/CROWD) and, importantly, the 40
   window-shaped CROWD-ABOVE crowds A226 built near records (they are the ones that look like the k0 window):
   corner-swap one corner (A222's routine, each corner in turn), then run the ANCHORED re-alignment (A223's click
   code with S fixed flush, G = the squares in contact-chain with S, common tilt toward S's alignment, side
   minimised over centres at each step with contacts kept) and record: feasible or blocked (by what), the side
   trajectory, the endpoint (flush / kink angle / blocked), and whether the endpoint side is < the start side.
   Table + pages (three frames for the ring; the worst case).
2. STATE Lemma REALIGN with the dichotomy made exact from the chain menu (which families decrease toward alignment
   over which tilt ranges; the anchored chain formula with a flush segment), prove what can be proved (feasibility
   of the anchored move at a lean; monotonicity where the formula is monotone), tag the rest [C] precisely.
3. Say what closes: if REALIGN holds, ONE-FLUSH(n) for every n where the swap's leftover fits; at n = 11 the k0_00
   obligation reduces to the (a)/(b) endpoints, both certified classes.  Lean: Statements/Open/Realign.lean (the
   candidate as a documented axiom + the consequence theorem), build + audit, 0 sorry.
4. Deliverables: docs/proofs/realign.md, the Lean file, code/, results/realign231.md (+jsonl), pages, registry row,
   LOG entry, ledger s.4 note.  Report once (<= 20 lines) and EXIT.
