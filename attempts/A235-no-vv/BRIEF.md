# A235 -- Lemma NO-VV: a minimiser has no loaded vertex-on-vertex contact between non-parallel squares (PI,
# 2026-09-15 20:20: "if you epsilon-perturb ALL the dimensions and let it relax, the point-on-point configuration
# won't survive; point-on-side is absolutely valid -- the expected way torque is applied to stabilise rotation").
Fable. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns, explicit-pathspec
commits, PYTHONDONTWRITEBYTECODE=1, <= 1 python process (BelowNormal, affinity 0xFFFF), never touch running workers.
Pages to docs/residue_map/campaigns/A235-no-vv/.  Read first: wall_torque.md (A219: Theorem SO, the second-order
exclusion in selection form; the ring's strut mode v2 = +0.381 -- ONE mode only, which is the PI's objection: "you
walked a line in that space that is technically still balanced"), local_certificate.md (Theorem LOCAL, Lemma
STAB), drain_sel.md / A128 (cluster screw, Gordan dual), contact_census.md (contact types: vertex-on-edge, flush,
exactly-opposite), A217's witnesses + stress tables, the coordinator's probe below.

## The measured fact (coordinator, 2026-09-15 20:30, attempts/A217 witnesses)
A LOADED vertex-on-vertex contact between two squares that are not parallel (mod 90 deg) occurs in NO genuine FJ
point: SETTLED 0 / 40 witnesses, K0FREE 0 / 41, BOXK0 0 / 36 (0 of ~700 loaded contacts), while the HELD
configurations have 26 / 174 with one and the CROWD four-crowds 6 / 182; the ring's lean 4|6 (70 deg on 20 deg) is
one.  At genuine optima the loaded contacts are vertex-on-edge (165 at SETTLED), flush edge-edge (166), and lattice
coincidences of flush / parallel squares (83).  So the PI's claim holds on everything we have.

## Task
1. STATE Lemma NO-VV exactly (any n): at a local minimiser of the side (or: at a Fritz-John point that is a strict
   local minimiser), no loaded contact is vertex-on-vertex between non-parallel squares.  Say what "loaded" means
   (positive multiplier on one of the two rows active at the point contact) and treat the parallel case
   separately (two same-tilt squares meeting corner to corner is a flush-lattice coincidence and can be loaded).
2. PROVE it or find the exact obstruction.  The feasible set near a VV contact is the CORNER of two smooth
   constraints (A's vertex vs B's edge line, B's vertex vs A's edge line); LP-style minimisers CAN sit at corners,
   so genericity alone is not a proof.  The route: the two rows' gradients at a VV contact are linearly dependent
   with the rotations (a rolling direction: rotate A about the common point, or slide the vertices past each other,
   changes both gaps at second order only), so the feasible cone at the corner contains a direction along which
   the side is flat to first order (the multipliers give no descent block) and the second-order term is decided by
   the curvature of the two edges at the vertex -- a knife-edge: show the reduced Hessian on that direction is
   indefinite or negative when the contact is loaded (Theorem SO's v2 < 0), so the configuration is not a strict
   local minimiser and relaxes to a vertex-on-edge contact.  This is the PI's full-dimensional perturbation, done
   as a second-order argument in the 2-dimensional rolling subspace rather than along one mode.  Test the reduced
   Hessian on every loaded tilted VV contact of the HELD / CROWD witnesses (32 of them) and on the ring's 4|6.
3. CONSEQUENCES, honestly: (a) for the k5 / k0 trees -- a VV row pair can be dropped from the option table at a
   minimiser (a small prune; price it on one page); (b) for four-crowds -- only 7 of 189 four-crowd witnesses have a
   loaded tilted VV, so NO-VV does not exclude crowds; say so.  (c) n-general statement about the contact graph of
   optimal packings (vertex-on-edge and flush only): is it consistent with all 21 survey records (check).
4. Deliverables: docs/proofs/no_vv.md, Statements/Open/NoVV.lean (theorem if it follows from Theorem SO's Lean form,
   else a documented axiom; build + audit, 0 sorry), code/, results/novv235.md (+jsonl), one page (the ring's lean
   with the rolling direction and its second-order side change), registry row, LOG entry.  Report once (<= 15
   lines) and EXIT.
