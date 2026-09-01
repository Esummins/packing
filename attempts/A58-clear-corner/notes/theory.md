# A58 — the clear-corner composition for the k <= 3 strata (Fable lead, 2026-09-01)

Constants, exact: s0 = 969271/250000 = 3.877084; B0 = s0^2 - 11 = 251986271441/62500000000 =
4.031780343056; certified live window of sides [191/50, s0] = [3.82, 3.877084]. Young-form
stratification and all census facts from A53 notes/lemmas.md (L1-L6); ledger and emptiness map
from A55 + A55/k3_ext (E4: 61 certified pin-sets; open classes k <= 4 all K1-protected).
Branch labels: [T] proved theorem, [M] measured/computed exact, [F] float-verified with margins,
[C] conjecture / named gap.

Convention. "Q meets B" means the OPEN interiors intersect; packings are interior-disjoint
families of 11 closed unit squares. Slot values per axis: L = {1/2, 3/2, 5/2},
R = {s0-1/2, s0-3/2, s0-5/2} (at side m in the window: same with m for s0; the census is
m-stable, A53 L2(iv)). B_p = the closed unit axis-aligned box centred at slot p (the "slot box").
Cell (i,j) of corner c = slot at offset i along the wall-normal-x axis, j along y, from c.

## 0. Scope: what is left below k = 5, and why no LP can touch it

A55/k3_ext E4 [M]: every Young class at k >= 6 and 19 of 22 at k = 5 are certifiably empty; open
are {k5_11, trump5, k5_16} at k = 5, {k4_03, k4_05, k4_06, k4_08, k4_11, k4_13} at k = 4, and at
k <= 3 the ten classes k0_00, k1_00, k2_00-02, k3_01-05 (k3_00, the wall column, is killed).
Every open class is a sub-tuple of an open k = 5 class, so by K1 (aliveness descends) NO pin-LP
certificate can ever exist for any of them. The k <= 3 STRATA (skeleton exactly S) are therefore
invisible to the whole certificate machinery of A53-A55: this attempt supplies the missing
mechanism. The PI's observation is the pigeonhole: a k <= 3 skeleton has at most 3 nonempty
corner diagrams, so at least one container corner is CLEAR (empty diagram); every nonempty
diagram contains its corner cell (Young closure), so #occupied corners = #nonempty diagrams <= k.

## 1. CC-1 [T] — the zone/slot separation layer (exact arithmetic, code/a58_analysis.py)

(i) The only slot value in the A21 corner-zone interval [49/100, 11/10] is 1/2 (exact compare:
3/2, 5/2 > 11/10; s0-5/2 = 344271/250000 = 1.377 > 11/10). Hence a SIMPLE square has its centre
in the (s0-frame, A47-enlarged) corner zone [49/100,11/10]^2 of corner c iff it IS the corner
square of c; a clear corner's zone contains no simple centre.
(ii) Corner-root boxes are pairwise unreachable by one square: adjacent roots are s0-2 =
1.877084 apart along an axis and (s0-2)^2 - 2 = 95215271441/62500000000 > 0, i.e. s0-2 > sqrt2 =
the diameter of a unit square; same for every s >= 3.82 ((s-2)^2 >= 3.3124 > 2). No unit square
meets two distinct corner-root boxes anywhere in the window.
(iii) Simple-clip census [M, exact]: the complete list of slot squares whose interior meets a
corner-root box interior is the 12 offset-2 cells — cell (2,0) clips the root box of the corner
adjacent along its horizontal wall (overlap width exactly 4 - s0 = 30729/250000 = 0.122916),
cell (0,2) the corner adjacent along its vertical wall, cell (2,2) the diagonal corner's root.
An offset-2 cell needs its two predecessors, i.e. a straight 3-arm: with k <= 3 the only class
containing one is k3_00 (killed). **Hence in every OPEN k <= 3 class, no simple square meets any
clear corner's root box.** (Deeper completable-slot boxes can be simple-clipped; the per-class
instances are enumerated exactly in results/occupancy_matrix.json — they occur first at k = 3:
k3_01's BL(0,2) and TL(0,1) boxes are clipped by the opposite-anchored wall squares.)

## 2. CC-2 [T] — the exchange (teleport) selection lemma

Setting: D1 attainment (docs/proofs/drain_lemma.md): M = argmin sigma over D0 is nonempty,
m = min sigma. For a minimizer P and a choice F of enclosing square of side m (an "embedding"),
k(P,F) = |Simp(P)| in the frame F normalised to [0,m]^2. K* = max over (P,F) of k(P,F) is
attained (integers 0..11, nonempty set). Fix (P*, F*) attaining it; normalise F* = [0,m]^2.

**Lemma CC-2 (empty completable boxes are impossible).** Let S = Simp(P*), k = |S| <= 10, and let
p be a completable slot of S (Young-ready cell, offsets <= 2) whose box B_p is interior-disjoint
from the slot squares of S. Then some square of P* meets B_p.

Proof. Suppose none does. P* has 11 - k >= 1 non-simple squares; let Q be one. P' := P* with Q
moved to B_p (placed axis-aligned at p). Interiors: no square of P* \ {Q} meets int(B_p), so P'
is a packing; B_p subset [0,m]^2, so sigma(P') <= m, and sigma(P') >= m by minimality: P' is a
minimizer embedded in the SAME frame [0,m]^2. Simplicity is monotone in the occupied-slot
pattern and Q was non-simple, so Simp(P') >= S u {square at p}: the p-cell's predecessors are
occupied (completability) and the enlarged diagram is Young, hence k(P',F*) >= k + 1 > K*.
Contradiction. QED

**Refinement CC-2' (single non-simple meeters are impossible).** In the same setting, if exactly
one square Q meets B_p and Q is non-simple, move Q itself to p: after its removal B_p is free,
and the same exchange gives k+1. Contradiction. Hence every completable slot box B_p (disjoint
from S's slot squares) satisfies exactly one of:
  (R1) some SIMPLE square meets B_p  [possible only in the CC-1(iii) clip geometry], or
  (R2) at least TWO non-simple squares of P* meet B_p.
With CC-1(iii): **for every open k <= 3 class, every clear corner's root box of the selected
minimizer carries >= 2 non-simple meeters** — and by CC-1(ii) the crowds at distinct corners are
disjoint sets of squares. At k = 0 that is >= 8 distinct non-simple squares tied to the corners.

Remarks. (a) No corridor, no slide, no blocking geometry enters: the exchange is a teleport, so
CC-2 strictly subsumes the grid-completing-slide selection A53 L6(a)-(c) (a completing slide
would also raise k in M, contradicting K*-maximality; k-max minimizers are slide-stuck AND
teleport-stuck). The PI's "blocked slide" dichotomy is resolved on the strong side: the blocked
branch is not one option, it is FORCED, and the "intruder" is upgraded from corridor-intruder to
box-meeter. (b) Valid at the true m anywhere in the window — no s-transfer, no certificate, no
LP. (c) The lemma is vacuous only at k = 11 (no square to move).

## 3. CC-3 [T at s = s0] — certificates transfer to occupancy theorems for ALL packings

**Lemma CC-3.** Let S be a pin-set and p a slot with B_p interior-disjoint from the pins, and
suppose S u {p} carries a PASSing kill certificate at s0 (A53 L5 semantics). Then EVERY packing
of 11 unit squares in [0,s0]^2 containing axis-aligned squares at all pins of S has a square
meeting B_p; moreover either a pin meets B_p (excluded when disjointness holds — so not here) or
>= 2 non-pin squares meet B_p (single non-pin meeter: move it to p, producing a packing
containing S u {p}, contradicting the certificate; empty box: move any of the >= 11 - |S| - ...
>= 1 non-pin squares).

This holds for ALL packings at s0, with no minimizer selection — but ONLY at s0 (the pins and
the certificate live in the s0 frame; transfer across the window is exactly A56's subject,
G-A53-1). The certificate route and the exchange route are complementary: CC-2 needs no
certificate but only binds the selected minimizer; CC-3 binds every packing but needs the kill.

**Where CC-3 applies (the occupancy matrix, [M] exact, results/occupancy_matrix.json).** For
each open class and completable slot p, the class of S u {p} was computed and looked up in the
ledger. Findings:
(a) At clear-corner ROOTS of open k <= 3 classes the superset class is OPEN in EVERY case
    (k0_00->k1_00; k1_00->k2_01/02; k2_xx->k3_01/03/04/05; k3_xx->k4_03/05/06/08/11/13): the
    open low-k classes are closed under adjoining clear-corner roots, so by K1 a certificate for
    S+root can NEVER exist — **the exchange lemma is not merely convenient, it is the only
    possible mechanism for clear-corner-root occupancy.**
(b) At DEEPER completable slots, 11 rows land on certified-empty classes and become
    unconditional s0 occupancy theorems, e.g.: every packing at s0 containing the BL 2-column
    {(1/2,1/2),(1/2,3/2)} has >= 2 further squares meeting [0,1]x[2,3] (wit k3_00); every
    packing containing k3_03 has crowds at BL(0,2) [wit k3_00-image], BR(0,1) [k4_10] and
    BR(1,0) [k4_04]; similarly k3_01 (TL(1,0), wit k4_04), k3_02 (three rows), k3_04 (three
    rows). The corner-scattered classes (k1_00, k2_01, k2_02, k3_05, k4_13) get NO cert-backed
    rows — every superset is open. Pattern: cert-backed occupancy exists exactly where the class
    has a 2-arm pointing at a killable extension.

## 4. CC-4 [T] — persistence: the crowd cannot be dissolved by free motion

Let P* be as in CC-2 and let Z be any sigma-preserving deformation of P* moving only NON-simple
squares (continuous or not; only the endpoint matters) with endpoint P'' in [0,m]^2. Then P'' is
again a minimizer in the same frame with the SAME skeleton-lower-bound (Simp(P'') >= S, and
k(P'') <= K* forces the R1/R2 alternative again at every completable slot box). In particular:
no motion of the crowd members that is available at the minimizer (rattler play, slide, rotation)
can bring a completable box's non-simple meeter count below 2 without a simple square taking
over. Consequences: (i) a crowd member with an escape direction (a motion taking it out of B_p,
all other squares fixed, disjointness kept) must be REPLACED in the box before it exits — but
the count constraint is on the endpoint, so what is actually forced is: in every minimizer
reachable by such motions, >= 2 non-simple squares meet B_p. (ii) Generic consequence [C, the
honest gap]: crowd members are blocked against box-exiting motions by walls, pins or other
squares — converting this into contact/FJ rows (the cascade feed, A48 C1/C3, A50 T2) requires
the motion analysis that is exactly A50-G1's frontier; NOT done here.

## 5. The composed statement (T1), branch-labelled

**Theorem A58-1 (clear-corner occupancy for low-k minimizers).** [T; ingredients: D1, A53 L1-L3,
CC-1, CC-2'] Let m = s(11) (attained), and let P* be a (K*-maximal) minimizer as in Sec. 2, with
skeleton S, k = |S|. Suppose k <= 3. Then S is one of the eleven k <= 3 Young classes; at
least 4 - k >= 1 corners are clear, and:
 (i)  [roots] for every clear corner c, at least two non-simple squares of P* meet the interior
      of the corner box B_c (the 1x1 box at c); crowds at distinct corners are disjoint; if
      k = 0, at least 8 of the 11 squares are corner-crowd members.
 (ii) [all completable slots] every completable slot box of S is either simple-clipped (only in
      the exact CC-1(iii)/matrix geometry; impossible at clear-corner roots of open classes) or
      carries >= 2 non-simple meeters.
 (iii)[s0 rows, all packings] at s = s0 the 11 cert-backed matrix rows of Sec. 3(b) hold for
      every packing containing the class pins, minimizer or not. [T at s0; window: A56 pending]
 (iv) [centres] independently, by A21 THM1/THM2 (certified at 3.88 >= window): some square's
      centre lies in some corner zone and some square's centre lies in some side zone. The
      witness corner cannot be directed to a clear corner (see Sec. 6); if S occupies no corner
      (k = 0), the THM1 witness corner is automatically clear and its zone occupant is
      non-simple by CC-1(i).
If k(S) of every minimizer is <= 3 is false — i.e. some minimizer has k >= 4 — the k <= 3 strata
are irrelevant to s(11) and the problem moves up to the open k = 4/5 classes, where the same
machinery applies at every clear corner (all open k = 4 classes except k4_13 = corners4 have
one; trump5 has TL clear). The pigeonhole exhausts exactly at corners4/k5_16.

**Canary [F, margins > 1.6e-2; independent Opus re-verification (own SAT + polygon-clip
areas, max deviation 5e-5)].** Trump's own packing (s_T, A03 data), skeleton trump5, has ALL
EIGHT completable slot boxes carrying EXACTLY 2 meeters (open-interior convention):
six boxes with 2 non-simple meeters, two boxes (BL(2,0), BR(1,0)) simple-clipped by the
adjacent corner squares at overlap exactly 4 - s_T = 0.122916 plus one tilted meeter. The
decisive TL-root box is met by the eps-off upright (margin +0.1555) and tilted sq6 (+0.1683) —
the composition's residue at the top of the stratification is literally Trump's own TL crowd,
and Trump is teleport-extremal (every box at the minimum count). A53 L4's measured corridor
intruder (sq7 at depth 0.0136 in the BL(0,2) corridor) reappears as the second meeter of the
BL(0,2) box (margin +0.0160): the blocked-slide measurement and the exchange lemma agree.
Sharp nuance found by the verification: on 7 of the 8 boxes a THIRD square sits in exact flush
contact with the box boundary (SAT margin 0 within 2e-15, interiors disjoint; only TL(0,0) has
a genuinely clear third square, at -0.645). The exactly-2 count is therefore knife-edge, not
robust: an arbitrarily small motion of the flush neighbours creates a third meeter. All A58
statements use only open-interior meeting at the exact configuration and are unaffected; but no
downstream argument may assume a positive margin between the crowd and the rest.

## 6. The quantifier, resolved honestly

A21 THM1 is existential over corners; for any skeleton occupying >= 1 corner its witness can be
the corner square itself, and the brief asked whether per-corner occupancy could be re-examined.
Answer: (a) the CENTRE-level per-corner statement is not available and is evaded by real
geometry — A21 measured NO(corner0) at tau ~10.7-10.86 unconverged (above the certifiability
ceiling, blocking mass on the other corners), and at Trump the TL-zone [49/100,11/10]^2 x
[s-11/10, s-49/100] contains NO square centre at all (both TL crowd members sit with centres
OUTSIDE the zone: the eps-off upright at corner-frame y' = 1.344, sq6 at x' = 1.536) — so a
per-corner centre-occupancy theorem is FALSE at the only known near-optimal packing's clear
corner, and no heavy LP run on it is warranted. (b) The correct per-corner statement is
INTERIOR-MEETING at the root box, and it is a theorem (CC-2') at the selected minimizer — the
existential quantifier of THM1 is not directed but REPLACED: every completable slot, every
clear corner, at once. The A21 zone statements remain useful only as centre-level extras (iv).

## 7. Honest gaps

* A58-G1: CC-3 rows at s0 only (= G-A53-1/A56; CC-2 rows are window-free).
* A58-G2: CC-4's "blocked => contact rows" conversion (the cascade feed G-A53-2) not formalised;
  the known hard node is A50-G1 (free-presser second-order descent).
* A58-G3: the crowd is not chargeable by existing tables (T2 screening, see report): a certified
  "meets-B_c" primitive (position-free, tilt-binned, pair version) does not exist; building one
  at useful strength is the named successor compute.
* A58-G4: K*-maximal selection commits the minimizer; statements (i)-(ii) are per-selection
  (exactly like L6), not for every minimizer. All downstream uses must keep the selection.
* A58-G5: Trump canary rows are float (A03 float file, meeter margins >= 1.6e-2, tolerance
  1e-9; the two exact-looking margins 0.122916 = 4 - s_T confirmed exactly); the combinatorial
  layer (census, matrix, class statuses) is exact Fractions. Verification found 7 of 8 boxes
  have a third square in exact FLUSH contact with the box boundary (margin 0 within float
  noise) — the 2-meeter counts are open-interior facts at the exact configuration only, with
  no perturbation margin; any robust ("third square stays 0.01 clear") reading is FALSE.
