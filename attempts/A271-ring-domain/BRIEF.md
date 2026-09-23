# A271 -- RING DOMAIN FROM HYPOTHESES: derive STRIP_2-IN-RING's domain (D1)-(D2), (U1)-(U9) from the family-stuck
# ring conditions themselves, so that STRIP needs no certificate off it.  (PI, 2026-09-23: "the ring domain is
# essentially required by the double-meeter requirement round the border plus the pinning requirement -- so what do
# we actually need to show?")
Fable.  LAUNCH-AND-EXIT -- NEVER wait for a detached run.  Ops: short responses, files <= 250 lines, no monitors, no
interim messages, explicit-pathspec commits (fetch + plain merge only), PYTHONDONTWRITEBYTECODE=1, ONE heavy python
process at most (BelowNormal, affinity 0xFFFF; sub-minute helpers fine); RUNNING, never touch: the status loop,
A262's chain3, A263's chain, A269's and A270's loops and their records / certs.
Read first: docs/proofs/strip_enclosure.md (A267: STRIP_2-IN-RING [T-prose] on the domain (D1) h_v < 1 < L_h,
g < 1; (D2) X's lowest point >= h_v; (U1) a1 < a*; (U2) b_X >= 0 on [a1, a2]; (U3) a2 - a* > w_max/2; (U4) rho(C_top)
< 1, rho(y0) < 1, ...; (U5) a_R - sin beta+ >= a*; (U6) h_u + c - cos phi < 1; (U8) X's top > C_top + 1/sqrt2; (U9)
T_u below X's far edge; s.3.5: what fails off the domain; s.6 item 5: "the JAM conditions alone do not give
(U1)-(U9); they are explicit ring-domain inequalities, [M] on 43/43 rings"; hyp267 margins: thinnest D1 0.0009,
D2/U2 0.0016, U5 0.041, the rest >= 0.19), docs/proofs/no_jam.md (the JAM corner and the JAM RING: X serves the
wall's other box -- it meets the TL box, so X's lowest point > 1 and X reaches height >= s - 1; the ring's walls
0-2 are rows of two / open pairs; C floats 0.25-0.72 off the wall meeting the BL box; HELD-JAM), box_meeters.md
(SAME-WALL, meeters_split, BLOCKER-SIDE), normal_ring.md (P1-P4; the RETREAT term P4: C is held), locked_wall.md
(LIFT), last_two.md s.1 (strip266: the 5-parameter tree priced ~5e3 CPU-h -- the thing this brief makes unnecessary),
family250.md (FAMILY-STUCK: every family of disjoint border cells over-met), ring_swap.md (CELLS).

## What we actually need to show
STRIP_2 is only ever applied at a JAM corner OF A FAMILY-STUCK NORMAL-FORM PACKING at side s <= s-hat.  So the
domain that matters is not the 5-parameter (h_u, h_v, theta_C, y_X, phi_X) box but its intersection with what
those hypotheses force.  Show that the ring hypotheses imply (D1)-(D2) and (U1)-(U9) -- or imply a smaller set of
inequalities under which A267's proof of s.3 still goes through -- with each step cited:
 H1 X meets the TL box (it is that box's wall meeter: BOX-MEETERS / the JAM row of no_jam.md), so X's lowest
    point > 1 (X misses the BL box: SAME-WALL / meeters_split) and X's top >= s - 1 >= 2.82; X is a wall toucher.
 H2 X holds C (int X meets int T_u: the definition of the JAM; else C drops by LIFT / P1).
 H3 C meets the open BL box; A is the floor toucher meeting it; C and A do not overlap.
 H4 s <= s-hat (window) and the packing is family-stuck (every border family over-met) and normal (P1-P4).
 H5 C is not pinned by the bare ring except through X (HELD-JAM [M]: the bare ring never blocks C's retreat) --
    use only if provable; otherwise do without.
For each of (D1), (D2), (U1)...(U9): derive it from H1-H5, or show it can fail under H1-H5 (a drawn configuration
satisfying H1-H5 that violates it -- then either A267's proof must be adapted for that case, or the violating
sub-domain is the ONLY place a certificate is needed: price it, it should be tiny).  The thinnest measured
margins (D1 0.0009: h_v < 1 -- C meets the box only by a sliver; D2/U2 0.0016) are the ones most likely to be
equalities in the limit rather than consequences: say what happens AT the limit (h_v -> 1: C leaves the box and
the corner is no longer JAM -- so the JAM domain is open there and STRIP is vacuous at the boundary?).
Then state STRIP_2-IN-RING with the derived domain as Theorem (or Theorem + one small certified sub-domain), and
record what NO-JAM(11) still lacks after it (pair3 from A262's chain3; 5d).

## Task
1. The derivations above (proofs first; every inequality tested on the 43 JAM rings + A262's adversary rows as
   a sanity check, never as a proof).  2. Where a condition is not implied: the drawn counter-configuration, the
   adapted proof or the residual sub-domain with a benchmark price (own verifier; launch only if <= 20 CPU-h).
3. docs/proofs/ring_domain.md; Statements/Open/RingDomain.lean (theorems where the set description suffices,
   documented axioms otherwise; the consequence: strip_two_in_ring's RingDomain replaced by the hypotheses; build
   + audit 0 sorry, no "(no output)" rows; AUDIT.md rows; one import line after fetch + merge); pages in
   docs/residue_map/campaigns/A271-ring-domain/ (a JAM corner with H1-H5 marked and each U-condition drawn as the
   geometric fact it is; any counter-configuration; geometry-checked, a note per panel saying what it IS, undecided
   grey stipple never green); registry row, LOG entry, ledger s.4 note, k0_route.md s.13 link 5b updated.
   Report once (<= 15 lines): which conditions are derived, which are not and what replaces them, the price of
   any residual certificate, what NO-JAM(11) still lacks, anything in the brief that was wrong.  EXIT.
