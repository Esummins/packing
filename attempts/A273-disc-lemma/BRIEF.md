# A273 -- THE DISC LEMMA, certified: the last piece of STRIP_2 under the corner hypotheses alone.  (2026-09-23.)
Opus (a certificate chore; a Fable note only if a hand proof falls out).  LAUNCH-AND-EXIT -- NEVER wait for a
detached run.  Ops: short responses, no interim messages, files in pieces <= 120 lines per Write, never a single
response over ~15k tokens, explicit-pathspec commits after every piece (fetch + plain merge only),
PYTHONDONTWRITEBYTECODE=1, BLAS threads 1, BelowNormal, affinity 0xFFFF, ONE python process (the lab is at its
ceiling: A269's and A270's loops (4 workers each), A262's chain3, A263's chain, the status loop -- never touch
them).  Benchmark before estimating.  Own verifier, at least as strong as the tree at every bin or bisect on
disagreement (A259's lesson); a certificate's parameters must be consistent with the box's own hypotheses (A265's).
Read first: docs/proofs/strip_jam.md (A272: STRIP_2-IN-JAM <= H1-H3 + DISC LEMMA [T]; the DISC LEMMA: no point q
with q_y > L_h, dist(q, Xi) >= 1/2 and dist(q, Gamma) >= 1/2 lies within 1/sqrt2 of the strip S -- Xi = X's side,
Gamma = C's side, both convex; tilt-free, 5 parameters (h_u, h_v, theta_C, y_X, phi_X); [M] sup slack -0.005 on
H1-H3 (disc272, attained only as h_v -> 1 with X flat), -0.047 on rings + violators; price ~1e2 CPU-h on H1-H3,
~20 CPU-h on A271's residual R as a 5-parameter tree with a 2-D convex bad-centre test; Lean StripJam.lean:
DiscLemma opaque, axiom strip_two_in_jam_of_disc), docs/proofs/ring_domain.md (A271: H1-H3, the five derived
conditions, the residual R = H1-H3 minus the ring inequalities, mc271: R ~ 18% of the H1-H3 set; on the ring
domain A267's proof already gives STRIP), docs/proofs/strip_enclosure.md s.3, attempts/A272-strip-jam/code
(disc272: the joint search; the convex sets Xi, Gamma in closed form), attempts/A271-ring-domain/code (ringdom271:
the H1-H3 hard constraints; adv271; mc271).

## Task
1. The box-valid test: over a parameter box B of (h_u, h_v, theta_C, y_X, phi_X) inside H1-H3, the bad set is
   {q : q_y > L_h(B) lower bound, dist(q, Xi_core(B)) >= 1/2, dist(q, Gamma_core(B)) >= 1/2, dist(q, S_outer(B))
   <= 1/sqrt2} -- with cores INSIDE the true sets and outers OUTSIDE (sound direction: the true bad set is inside
   the test set).  2-D convex geometry per box (the sets are polygons / offset polygons); CERT iff the test set is
   empty (area <= 1e-10 with outward rounding), else bisect; PRUNE iff B misses H1-H3 entirely.  Benchmark 200
   boxes.
2. Run over R first (A271's residual, ~20 CPU-h priced), then over all of H1-H3 if the price allows (<= 100 CPU-h)
   -- the H1-H3 run makes A271's ring inequalities unnecessary altogether.  Detached, resumable per cell, STOP
   file, certs + index + verify273 (independent re-derivation from a dump, bisect-on-disagreement), commit per cell.
   Where the slack -> 0 (h_v -> 1, X flat): the box test will not close at the boundary -- handle it by the vacuous
   boundary argument (at h_v = 1 C leaves the box: cite ring_domain.md) as a PLUG-type layer with an explicit
   margin, or report the exact open layer.
3. If while building the test a hand proof of the disc lemma appears (a point at distance >= 1/2 from two convex
   sets that together with the wall enclose the strip: the disc of radius 1/2 about q misses both; the strip point
   within 1/sqrt2 ...), write it in the note tagged [T] with the geometry -- but do not spend more than an hour on it.
4. Deliverables: code/, certs/ (+ index, verify273 output), results/disc273.md, notes/disc273.md (the test's
   soundness with citations, the price, the boundary layer), pages in docs/residue_map/campaigns/A273-disc-lemma/
   (the bad-centre test on one box: q, Xi, Gamma, S and the disc; the certified map over (theta_C, phi_X);
   geometry-checked, notes per panel, undecided grey stipple never green), Lean: replace the DiscLemma axiom's
   status in AUDIT.md by the certificate reference when verify273 passes (no new sorry), registry row, LOG entry,
   ledger s.4 note, k0_route.md s.13 5b.  Report once (<= 15 lines).  EXIT.
