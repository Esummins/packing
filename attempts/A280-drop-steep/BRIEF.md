# A280 -- THE DROP LEMMA AT STEEP C: A273's box test comes out OPEN on every cell with theta_C >= 25 deg (24 of
# 67 cells at the 400k box cap); strengthen the test or close the region another way.  (2026-09-24.)
Opus.  LAUNCH-AND-EXIT -- NEVER wait for a detached run.  Ops: short responses, files <= 120 lines per Write, never a
single response over ~15k tokens, explicit-pathspec commits (fetch + plain merge only), PYTHONDONTWRITEBYTECODE=1,
BLAS threads 1, BelowNormal, affinity 0xFFFF, ONE python process (the lab is at its ceiling; do not start a run
while A273's run273.sh is still alive -- check by command line 'tree273.py'; if it is, prepare + benchmark on <= 5
cells only and leave the launch line in the report).  Own verifier at least as strong as the tree at every bin or
bisect on disagreement; parameters consistent with the box's hypotheses; cores inside / outers outside.
Read first: docs/proofs/k0_knowledge.md s.0.5 then s.2.3 / s.5 / s.7; attempts/A273-disc-lemma/notes/disc273.md +
code (tree273 / verify273: the DROP LEMMA -- the cone conv(D(q, 1/2) U {p}) misses Xi and Gamma; 4 parameters
(h_u, theta, D, phi); index273.jsonl: CERT for theta < 25 deg, OPEN-LAYER for every theta in [25, 45] at all phi),
docs/proofs/strip_jam.md (A272: what stops the intruder is X's RIGHT boundary + T_u's top edge; the LEFT constraint:
a square holding a strip point is left of C below C_top; the case split by the centre's height), flat_x.md (A276:
FLAT-X / CORNER, the mechanism at X flat), ring_domain.md (A271: H1-H3; on JAM RINGS theta_C <= 25.8 deg [M] --
the ring never produces the steep-C region; Lemma LOW's full-range form), strip_enclosure.md s.3 (A267's proof on
the ring domain, which covers steep C IF the ring inequalities hold there).
## Task
1. DIAGNOSE on two OPEN cells (e.g. theta [30,35] x phi [10,15] and [40,45] x [30,35]): what the open leaves look
   like (the bad-centre test set's shape; is it a genuine near-miss or a weak relaxation?); evaluate the exact
   drop-lemma slack at their centres by exact geometry (A272's disc272 / probe).  If the exact slack is positive
   somewhere, that is a counterexample to the DROP LEMMA at steep C: draw it, and say what STRIP_2 needs instead
   (A272's reduction had other cases).
2. STRENGTHEN the box test where the relaxation is weak: add the LEFT constraint (A272) and the height case split
   to the bad-centre set; use the outer/inner sets' exact polygons; benchmark on the two cells (target: CERT at
   the 400k cap).  If still OPEN: the ring-domain route -- do the ring inequalities (U3)-(U6), (U8) hold on the
   steep-C part of H1-H3 (A274b's adversary code restricted to theta >= 25)?  If yes [M], A267's proof covers it
   and the certificate is only needed for the ring inequalities themselves (state that); if no, the exact
   residual.
3. RUN the strengthened test over the OPEN cells (after A273's chain ends), detached, own verifier, index,
   commit per cell; report the price and what is launched.
4. Deliverables: code/, certs/, results/drop280.md, notes/drop280.md, page in
   docs/residue_map/campaigns/A280-drop-steep/ (an open leaf's test set before / after; geometry-checked; note
   per panel; undecided grey stipple), registry row, LOG entry, ledger s.4 note, k0_route.md s.13 5b, APPEND
   entries to k0_knowledge.md.  Report once (<= 12 lines).  EXIT.
