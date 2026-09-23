# A272 -- STRIP_2 UNDER H1-H3 ALONE: the statement holds on every violator of A267's ring inequalities (A271 [M]);
# find the proof that does not need them.  (2026-09-23.)
Fable.  LAUNCH-AND-EXIT -- NEVER wait for a detached run.  Ops: short responses, no interim messages, files in
pieces <= 120 lines per Write call, one file per call, never a single response over ~15,000 tokens (A271 was cut
off by the 64k output cap), explicit-pathspec commits after every piece (fetch + plain merge only),
PYTHONDONTWRITEBYTECODE=1, ONE heavy python process at most (BelowNormal, affinity 0xFFFF).  RUNNING, never touch:
the status loop, A262's chain3, A263's chain, A269's and A270's loops, records and certs.
Read first: docs/proofs/ring_domain.md (A271: (D1), (D2), (U1), (U2), (U9) are THEOREMS from the JAM corner
hypotheses H1-H3 -- Lemma SLOPE (the A-C separator has positive slope), Lemma LOW (L_h >= cos alpha + tan(45 -
theta/2) >= 1.121, h_v >= 0.414), X_low > 1.406; (U3)-(U6) and (U8) are FALSE as consequences: exact violators with
X tilted 13-43 deg away from C and meeting T_u by a sliver (margins -0.18 to -0.30); yet STRIP_2 itself SURVIVES
every violator [M] (probe271: sup t = -0.00000, attained only as h_v -> 1, the vacuous boundary); residual ~18% of
the H1-H3 set, ~1e3 CPU-h as a box tree -- not launched; the statement now: STRIP_2-IN-JAM = H1-H3 + (U3)-(U6) +
(U8) => no {C, X}-free square meets S), docs/proofs/strip_enclosure.md s.3 (A267's proof: the UPPER case in C's
frame, chord trapping under X's lower-right edge, the tent chord function; where each U-condition enters),
last_two.md s.1 (the LEFT-SHADOW box test; the SAT case list), no_jam.md, box_meeters.md (BLOCKER-SIDE, SAME-WALL).

## The question
STRIP_2 under H1-H3 only: C meets the open box (h_v < 1, its left vertex above 1 by LOW), A the floor toucher
meeting the box (SLOPE), X a wall toucher with lowest point > 1.406 overlapping T_u (H1-H2), side in [3.82, s-hat].
Claim: no unit square Q disjoint from C and X (in the quadrant) has an interior point in S = T_u minus C.
A267's proof needs (U3)-(U6), (U8) because it traps Q's chords under X's lower-right edge; on the violators X is
tilted far from C, so that wedge is wide -- but Q still does not fit, by probe271.  Find WHY on the violators:
where does Q's best attempt sit (draw the sup-t configuration of probe271 for each violator: Q, C, X, T_u, S), and
which obstacle stops it -- C's upper-left edge? X's lower edge? the wall? T_u's own top edge (Q must have an interior
point in S, so it must reach below T_u's top)?  Then a proof by cases on X's tilt relative to C: |phi - theta| small
= A267's argument; |phi - theta| large = the new argument (candidate: with X tilted far from C, X's lower-right
edge is steep, the wedge under it is tall but NARROW at the strip's height -- a unit square in it has width >= 1
> the wedge's width there; or POKE through the wedge mouth bounded by the mouth width).  If a genuinely new
sub-case resists, state the exact residual (parameters, size) and price a box tree over ONLY it (benchmark; launch
if <= 30 CPU-h with own verifier).
Also (U8) for theta > 6.5 deg: derive or fold into the case split.

## Task
1. The violator gallery (probe271's sup-t configurations, geometry-checked, one panel each, a note saying what
   stops Q).  2. The proof by cases, [T] where it closes; every step cited; the residual (if any) drawn and priced.
3. docs/proofs/strip_jam.md; Statements/Open/StripJam.lean (theorems where the set description suffices, documented
   axioms otherwise; strip_two_in_jam's RingIneq hypothesis discharged or reduced; build + audit 0 sorry, no "(no
   output)" rows; AUDIT.md rows; one import line after fetch + merge); pages in
   docs/residue_map/campaigns/A272-strip-jam/; registry row, LOG entry, ledger s.4 note, k0_route.md s.13 link 5b.
   Report once (<= 15 lines): the mechanism on the violators, the case split, what is [T] / residual, the price,
   what NO-JAM(11) still lacks, anything in the brief that was wrong.  EXIT.
