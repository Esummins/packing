# A278 part 6 -- SWEEP on the witness, the separator arcs, and what the residual must satisfy  [T] + [T-computed]

**[T-computed] (page278.py, results/page278_checks.json).**  On A277's Y-poke witness the largest-gap SAT separators
are: D -> C along D's edge normal, slope angle 12.87 deg (gap 0.00227); Y -> D along Y's edge normal, slope angle
77.21 deg (gap 0.00055); X -> C along C's edge normal, 14.47 deg (gap 0.00393).  All three have positive slope
(FLOAT-SLOPE and BLOCKER-SIDE, as they must).  Since a Y -> D separator of angle 77.21 deg EXCEEDS the D -> C
separator's 12.87 deg, Lemma 2.3 SWEEP applies to D with any psi in [12.87, 77.21] deg: D - t (cos psi, sin psi)
stays on D's side of both lines, never meets C or Y, and lands on a wall; the landing cell is met by D alone unless
X (the only other square) meets it -- X lies in {y >= 2.03}, the landing cell in {y <= 2.4} near the corner: [T-computed]
for psi = 45 deg the landing cell misses X (not run here; the flat cell of part 3 already lands D).  So the witness
is landed TWICE: by the flat floor cell (shadow-certified) and by the diagonal slide.

**[T] The arcs.**  For two disjoint convex bodies the separating normals form an arc (part 2 (iii)).  Write
[alpha_-, alpha_+] for the slope angles of the D -> C separators, [eta_-, eta_+] for Y -> D, [xi_-, xi_+] for X -> C
(all inside (0, 90) deg).  Lemma 2.3 lands D unless  eta_+ < alpha_-  and lands C unless  alpha_+ < xi_-, when the
sweep meets no square outside {C, D, X, Y}.  Hence every point of the residual R (part 4) with the sweep free satisfies
      eta_+ < alpha_- <= alpha_+ < xi_-                                                     (NEST)
-- Y is separated from D ONLY by lines shallower than every C-D separator, X from C only by steeper ones.  Since Y
meets int T_v(D) (a point of Y lies straight below a point of D), a shallow separator of D and Y means Y is UNDER D,
not beside it: Y's top region lies under D's lower edges over a horizontal stretch, which for a floor toucher Y of
tilt alpha_Y puts D's lower vertex above Y's top vertex or its upper edges -- D then floats HIGH (h_v(D) of order Y's
height at that x, >= cos alpha_Y or so), the opposite end of the residual from the witness (h_v = 0.0047).  At that
end C, above-left of D with the C-D separator steeper than D-Y and C meeting B, is pushed toward the wall: this is
where the flat cell of part 3 is doubtful and where a certificate must work.  (NEST) is a cheap PRUNE for the tree
of part 4: compute the three arcs from the cores/hulls and discard boxes violating it -- every discarded box is
landed by SWEEP [T], provided the swept region is inside the container and meets no fifth square: the container is
fine near the corner; a fifth square in the swept region is again outside the shadow, so the sweep must be
combined with a shadow test on the swept region (the same disc test on D's translates), or the box is kept.

**Correction to part 2's closing remark.**  "xi_X > alpha > alpha_Y is the ONLY way both are jammed by the four
alone" is (NEST) with the arcs made explicit; the witness violates it (eta_+ = 77.2 > alpha_- = 12.9), which is
why A277's optimiser drove every such configuration to the boundary where a floater touches (sup 0 attained only
there): the jammed FLOAT2 corner needs a HIGH D over a Y that is under it, and then P1's cells are elsewhere.
