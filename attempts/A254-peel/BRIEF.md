# A254 -- PEEL: the n-general form of ring + poker, and the onion inequality s >= 2 + s(n - 4(m-2))
# (PI, 2026-09-20: "I suspect in the general form ONLY-RING is true for all non-trivial side lengths, s < ceil sqrt n").
Fable. LAUNCH-AND-EXIT -- NEVER wait for a detached run.  Ops: short responses, files <= 250 lines, no monitors, no
interim messages, explicit-pathspec commits (fetch + plain merge only), PYTHONDONTWRITEBYTECODE=1, <= 1 python
process (BelowNormal, affinity 0xFFFF; the k5 pass loop and the status loop are running -- never touch them).
Pages to docs/residue_map/campaigns/A254-peel/.  Every lemma stated for general n, m = ceil(sqrt n), s in (m-1, m).
Read first: attempts/A253-min-tilt/notes/mintilt253.md (theta_min = 0; the tau -> 0 limit of the all-ADJ ring is the
four-corner-domino pinwheel; Lemma HOLE-ONE, NOTCH-NARROW: pocket = centre hole [1, s-1]^2 + four 1 x (s-3) notches
=> capacity 1 => 9 < 11; room measured constant across tilts; ONLY-RING [C]), docs/proofs/centre_disc.md (ring +
ribbon poker is the family-stuck structure; RING-POKER-RESIDUAL(11)), type_t_chase.md (A249: the ring, T-CELLS,
s.3.4 non-ring structures), attempts/A250-family-stuck/notes/family250.md (FAMILY-STUCK; theorem at s >= 4: needs
4 floor(s) - 3 > n squares; ILP minimum 9 below 4), ring_swap.md (CELLS, Lean cells_swap / teleport_of_swap),
ring_capacity.md (A236: NO-CLOSURE identity 4(m-2) + (m-2)^2 - 3 + 4 = m^2 - 3; Lemma TWO), one_flush.md + A226
results/survey226.* (the 21 records below ceil sqrt n, their flush corners), corner_chase.md (TWO-POKERS).

## The coordinator's observation (check it, do not trust it)
HOLE-ONE is the m = 4 case of a recursion.  The flush limit of the general ring is the pinwheel of four flush
1 x (m-2) wall blocks; the pocket is the centre hole of side s - 2 plus four notches of width s - (m-1) < 1 (they
hold no unit square: NOTCH-NARROW).  So all n - 4(m-2) non-ring squares lie in a square of side s - 2:
   PEEL (flush limit):   s >= 2 + s(n - 4(m-2)).
n = 11: s >= 2 + s(3) = 4 > s-hat (HOLE-ONE is s(2) = 2).  With n = m^2 - k the inner count is (m-2)^2 + 4 - k, so
by Nagamochi's s(j^2 - 1) = s(j^2 - 2) = j PEEL gives s >= m (contradiction) for every k <= 6; from memory of
Friedman's table it also beats the record at n = 5, 10, 17, 18, 19, 26, 27 (uses s(11)!), 28, 37, 38, 50, and is an
EQUALITY at n = 65 (2 + s(37) = 8.5987 = record) -- verify every number against the survey / the literature; PEEL
needs LOWER bounds on s(n'), so say for each n which are proved and which are only records.  If it holds, k0
exclusion at n becomes a corollary of lower bounds at n' = n - 4(m-2): the inductive tool for higher n.

## Task
1. DEFINE the border-cell system for general m (the flush slot chains from each corner; which cells overlap below
   m: left slot j meets right slots m-1-j and m-2-j in ribbons of width 1 - eps and eps, eps = m - s) and restate
   FAMILY-STUCK(n); recover A250's theorem at s >= m - ... as the general count.  State ONLY-RING(n) exactly: what
   "the ring" is for m >= 5 (m-2 tilted touchers per wall at a common handedness? are the mid-wall slots served?),
   how many pokers the families force (n = 11: one poker in one ribbon breaks all 16 eight-cell families -- check
   m = 3 and m = 5 by the ILP of count250 generalised), and what evidence exists for / against it (run A250's
   search250 generalised at n = 5 (m = 3), n = 10, 17 on a small budget, detached; report from what finished).
2. PROVE PEEL at the flush limit for general m [T], with the exact hypothesis (which structure, which limit), and
   NOTCH-NARROW general.  Then the honest gap: OFF the flush limit the pocket is not a square -- at n = 11 the room
   is measured constant (A253); for larger m the inner packing has freedom.  Is there a monotone statement
   (pocket at tilt tau is contained in a rotated / sheared copy of something of inner side <= s - 2 + f(tau) with
   the ring paying >= f(tau) elsewhere)?  State the strongest provable form; tag the rest [C] precisely.
3. TABLE: for every n <= 100 below ceil sqrt n: m, k, n', the best PROVED lower bound on s(n'), the record s(n),
   PEEL's verdict (excluded by theorem / excluded given records / equality / not excluded).  Draw the n = 17 and
   n = 65 cases (the pinwheel, the hole, the inner record packing inside it) -- geometry-checked SVGs, a note per
   panel saying what it IS, undecided regions grey stipple never green.
4. Say plainly what is proved, what is conditional on ONLY-RING(n), and what this does for n = 11 (does PEEL +
   continuity from the flush limit close RING-POKER-RESIDUAL(11) off the common-tilt slice?  If a short argument
   exists, give it; else the exact remaining case).
5. Deliverables: docs/proofs/peel.md, lean/.../Statements/Open/Peel.lean (PEEL flush-limit as a theorem if it
   formalises from HOLE-ONE's set description, else documented axiom; ONLY-RING(n) as a documented axiom; the
   consequence chain; build + audit, 0 sorry; AUDIT.md row), code/, results/peel254.md (+jsonl), pages, registry
   row, LOG entry, ledger s.4 note.  Commit after every piece; push.  Report once (<= 20 lines) and EXIT.
