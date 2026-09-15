# PI (2026-09-14 17:10): the precise conjecture to test
"If we can say that a corner singly met (or not met) is an opportunity to teleport a square in there, and thus the
'actual' solution is k1+, that puts very explicit constraints on the squares in/around the corners, and I suspect
that those constraints require a net torque from the container, which isn't possible from a convex container."

Skeleton:
 (1) TELEPORT (k0_route.md K0-FREE / K0-BLOCKED, Theorem FC): a corner met by at most one square lets a square be
     teleported into it at no cost in side, so a k0 optimum has EVERY corner doubly met, both meeters held.
 (2) EQUILIBRIUM (Fritz-John stress): each corner meeter's wall forces are balanced by its holders; the walls are the
     only external forces, so the TOTAL force and TOTAL torque of the walls on the packing vanish.
 (3) CLAIM: the doubly-met-and-held configuration at a corner forces the wall forces there to contribute torque (about
     some fixed point) of a definite sign, the same at all four corners under the rotations relating them, so the
     total cannot vanish -- contradiction -- hence some corner is at most singly met and (1) gives k1+.

Coordinator's caveat for the probe: about the container CENTRE the two walls of one corner give torques of opposite
signs (an upward force at (x, y) below-left of the centre has torque (x - c) f < 0; a rightward force there has
torque -(y - c) f > 0), so a per-corner sign is NOT automatic -- test (a) the moment of each corner's wall forces
about the CORNER POINT itself, (b) about the centre, (c) the chirality pattern of the two meeters (corner_seal.md) and
whether it is forced uniformly by "both meeters reach the corner cell from the two walls", (d) the holders' torques.
Report which of these, if any, carries the definite sign; if none, say so with the witness.  Also confirm (1) on the
witnesses: does every all-four-unsettled local optimum have every corner doubly met?

## PI (2026-09-14 17:25): the GEAR RULE -- sign propagation along holder chains
"a square meeting the wall with some torque sign can only be pinned by another square operating against it, which has
to have the same torque sign (like meshing gears), so pins can only be held by squares of the same torque, but in a
convex container, you can't have a non-zero torque, so you can't have a consistent pin direction against all squares.
Non-convex containers provide an opportunity to pin squares with different torques though, so the logic breaks."
Testable form: a frictionless point contact between squares A and B at point p with force F on A: torque on A is
(p - a) x F, on B is (p - b) x (-F); when p lies between the centres these have the SAME sign (gear rule); when p is
outside the centre segment (a pocket contact: pushed from the far side) the signs can differ.
Probe items (in order): (a) for every loaded contact in every witness's stress network, the two-body torque signs and
whether p lies between the centres -- how often equal, and where not, is it a pocket contact?  (b) for every corner
meeter, the wall torque sign vs the sign carried by its holders; (c) whether the holder chains around the boundary of
an all-four-unsettled witness are single-signed and closed, versus broken by a pocket contact in the settled-corner
optima and in Trump.  If (a),(b) hold and (c) separates, Lemma TORQUE is a PARITY statement on the contact graph:
proof route = gear rule + total wall torque zero.
