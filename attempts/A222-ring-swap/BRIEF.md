# A222 -- RING SWAP: teleport-decompose a loaded ring at once (PI, 2026-09-14 22:10: "if the load path is a ring,
# then the entire ring can be teleport-decomposed at once").
Fable. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns (long searches
detached, per-row commits, resume block), explicit-pathspec commits, PYTHONDONTWRITEBYTECODE=1, <= 2 python
processes (BelowNormal, affinity 0xFFFF), never touch running workers.  Pages to docs/residue_map/campaigns/
A222-ring-swap/ (geometry-checked, notes on each panel, times).  Read first: docs/proofs/k0_route.md s.3 (Lemma
K0-FREE, the discrete teleport: a corner box met by <= 1 square is exchanged for the settled corner square at the
SAME side; Lean Selection.lean teleport_packing), wall_torque.md (A219: Lemma RING holds on 193/193; the ring's
strut mode has v2 = +0.381 so LOCAL drains fail at second order), k0_count.md s.5 (the ring rand_0_0569|t20 and
its load path page attempts/A218-k0-count ring_loadpath), torque.md (C4/C5), A219's rows219 / modes219 code.

## The idea, in the lab's terms
Local motions of a loaded ring do not lower the side (A219).  The PI proposes a DISCRETE, non-local move: since
the ring's meeters hold only each other (and the walls), exchange the whole ring at once.
Lemma SWAP (generalised teleport, any n, trivially sound): if X is a set of squares of a packing P at side m and
X' is a packing of |X| unit squares inside  U(X) := (union of the squares of X) union Free(P), interior-disjoint
from P \ X, then (P \ X) union X' is a packing at side m.  teleport_packing is the case |X| = 1 (the <= 1 meeter
of a corner box exchanged for the settled corner square).
Conjecture RING-SWAP (n = 11, S <= s-hat): for a loaded four-crowd whose meeters form a ring, X = the eight
meeters (plus holders if needed) admits X' with a SETTLED CORNER; then the packing is teleported into k1_00 at the
same side, which is the K0-FREE contradiction (k0_00 closed for loaded rings without any force argument).
Local version (Lemma CORNER-SWAP, 2-for-2): the two meeters A, B of an open corner box met by exactly A and B can be
exchanged for the settled corner square S = [0,1]^2 (S lies in A u B u Free since nothing else meets the box) plus
ONE unit square inside (A u B u Free) \ S.  Area is fine ((A u B) \ S has area >= 1); shape may fail.  The PI's
point: around a RING the four remainders merge along each wall into a band, and the four leftover squares go into
the four bands -- "decomposed at once" where one corner alone might not swap.

## Task
1. STATE Lemma SWAP exactly and add Statements/Open/RingSwap.lean (SWAP as a theorem if it follows from the
   existing packing predicate in a few lines -- try; else an axiom with docstring) + the RING-SWAP conjecture as a
   documented axiom; build + audit (0 sorry).
2. TEST on the witnesses: for the ring rand_0_0569|t20 and every HELD / CROWD four-crowd of A217 (193), search for
   X' = 8 unit squares inside U(X) with the four corners settled (then the four leftovers in the wall bands), and
   the weaker: X' with >= 1 settled corner.  Region-constrained packing search (A217's optimiser with the
   containment constraint square subset of U(X) as a polygon-containment penalty; exact check of the found X' with
   the frozen predicates).  Also the 2-for-2 CORNER-SWAP per corner (which corners of which witnesses admit it).
   Report counts: all-four / >= 1 corner / none, and for failures WHAT blocks (a holder or rattler intruding into a
   band, a remainder too thin), with the ring drawn: X, U(X), X'.
3. PROVE what the witnesses support: e.g. CORNER-SWAP under a geometric condition (tilts, positions of A, B), or
   the band lemma (along a wall between two settled corners the remainders of two adjacent corners' meeters plus
   the free space contain a unit square when S - 2 >= 1 and no non-ring square enters the band [1, S-1] x [0, 1]).
   State everything n-general; say exactly what remains [C] and whether rattler crowds (unloaded meeters) are
   covered too -- SWAP does not care about loads, so if the geometry holds for ANY four-crowd, the rattler gap of
   A218/A219 closes as well.  That is the prize: say plainly whether RING-SWAP needs "loaded" at all.
4. Deliverables: docs/proofs/ring_swap.md, the Lean files, code/, results/swap222.md (+jsonl), pages, registry row,
   LOG entry, ledger s.4 note.  Report once (<= 20 lines: SWAP status, witness counts, what is proved, what remains,
   whether loads are needed, commits) and EXIT.

## Addendum 0 (PI, 22:30) -- the perimeter SWEEP is the proof route, and it needs no loads
Pick up one corner meeter A; the corner box now has one meeter B; pick B up and settle A in the corner (1-for-1
teleport: the box lies in A u B u Free).  The cell next to the settled square along the wall must be doubly met
(Theorem FC) -- one meeter is the next ring pin; place the square in hand there, pick up the next pin; repeat
around the perimeter.  The outside holds at most 4 floor(sqrt n) - 4 simple squares (corners double-counted; n = 11: 8; at S < 4, 3 per
wall), and the sweep uncovers that many, so at every step the SECOND meeter must be a centre square: no ring is
self-supporting under teleport-freeness.  Obligations: (i) Lemma STEP -- each exchange valid at the same side (the
target cell met only by the squares in hand and the next pin; check step by step on the 193 witnesses, name the
intruder where it fails); (ii) FC applies to cells exposed mid-sweep (pins = squares settled so far); (iii) the
exact count of exposed cells vs n - |ring| interior squares and how many exposed cells one interior square can
meet (A1 / CN).  Do this first (ring_swap.md s.1 + a sweep page on the ring witness); say whether it covers rattler
crowds and what geometric obligation remains.

## Addendum 0b (PI, 22:50) -- "if that count holds in general, k0 AND k1 are both trivially empty"
Run the sweep from a k1 start too and state the general theorem: every teleport-stuck packing at side <
ceil(sqrt n) exchanges at the SAME side into one with >= k* settled squares (k* exact at n = 11 if the count
closes; exact bookkeeping of the sweep, nothing left in hand -- or the corrected form: each exposed cell met only
by the next pin is a K0-FREE teleport on its own).  Separate VALUE (exchanges preserve the side: lower classes
reduce to higher ones) from UNIQUENESS (a k0/k1 packing at s-hat exchanges into Trump, so it is Trump with a subset
re-packed inside its union u Free: the finite obligation SWAP-RIGIDITY of Trump; test it on Trump if cheap).

## Addendum 0c (PI, 23:00) -- RAISE: k0 -> k2, start the search at k2
Target: from any teleport-stuck packing at side < ceil(sqrt n) at least TWO cells settle by exchange, so k0
raises to k2 and the stratified search starts at k2; the same count holds above k0 because for k > 0 the container
minus the settled squares is non-convex (FC's forced cells).  State Lemma RAISE(k -> k+2) or the honest RAISE(k ->
k+1) with exact hypotheses, from k = 0 and k = 1; simultaneous (independent teleports commute when cells and
meeters are distinct) vs sequential; what the certified k1-k4 trees give.  Consequence if it holds: the k0 cascade
is not needed for the VALUE; uniqueness reduces to SWAP-RIGIDITY of Trump.  Test RAISE on all A217 k0 witnesses
(two simultaneous teleports / one / none; draw a failing case).
