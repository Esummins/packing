# A281 corner cost -- outline (Fable, 2026-09-28)
Framing: room = unconditional [T]; torque/lock = conditional on k>=1 window rows [T-cond].
Pieces (<= 60 lines each, committed as written):
 part1  definitions recap: corner classes F / T, sense, poker, holder, window [s-hat, 3.877084]; cite k0_knowledge s.1/s.2
 part2  F1 SIDE: along-wall extent of an F corner per wall (closed form in tilt t, offset); F+F on a wall = TWO-POKERS
        (>= 3.9342370 [T]); F+T mixed bound; flat row 3.9347
 part3  F2 HOLDERS: FLAT-ABOVE => one interior holder per F corner, or adjacent wall meeter (that corner then T, sense fixed)
 part4  F3 TORQUE [T-cond]: flat toucher has no wall torque; poker needs TWO-CONTACT; RING => interior contact named
 part5  T1 SIDE: reach R(theta,delta); ring least side 1+sec+cos+sin+tan(phi/2); mixed senses >= 3.9298 => one-sense on window
 part6  T2 HOLDERS: bare ring settles (A253/A258 P2') unless HELD by one ribbon poker; holder contains O => capacity 1
 part7  T3 TORQUE [T-cond]: LEVER => contact ring needs s>4; below 4 load path through interior; count contacts
 part8  THE COUNT: f = 0..4 table, side / holders / both; survivors; drawing of any survivor; what closes it
 part9  corrections to the brief; Lean statement plan; page plan
Deliverables: docs/proofs/corner_cost.md (assembled from parts), lean Statements/Open/CornerCost.lean, page
 docs/residue_map/campaigns/A281-corner-cost/, registry row, LOG, ledger s.4, k0_knowledge APPEND.
