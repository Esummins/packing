# cost281 part 4 -- F3 TORQUE [T-cond]: the load path of an F corner

**Conditionality, stated exactly.**  Force / torque facts are statements about Fritz-John points with the meeter in
question LOADED (positive multiplier on its contacts).  A233's LOCKED (no retreat at the Psi-minimal optimum) is a
KINEMATIC property and does not imply load: rattler crowds are locked-but-unloaded at 61 of 70 doubly-met corners of the
genuine k0 FJ points (`k0_count.md` s.5), and a caged rattler is locked.  So every line below is [T-cond] on (i) the
k >= 1 window rows (so that the optimum is k0 and locked) AND (ii) the named meeter carrying load.  Nothing here is
in the chain (s.8); it answers the brief's F3.

**F3.1 [T] The flat has no forced wall torque.**  A flat toucher meets its wall along an EDGE; the wall's normal pressure
is a distribution along that edge whose resultant W may act anywhere on the edge: the wall supplies any torque in
[-W/2, W/2] about the flat's centre.  (Lemma W's tau = W (sin th - cos th)/2 is the VERTEX-contact formula; at th = 0 it
is the extreme -W/2 of the edge range.)  So A is never torque-limited by its wall; its along-wall balance needs a
corner-ward pusher (HOLD) because its partner pushes it outward along the wall (PUSH (ii)): A's holder is the square
pressing its far edge along the floor (the floor chain's F_in), or A is unloaded.

**F3.2 [T] The poker needs two further loaded contacts (TWO-CONTACT).**  B is tilted; th = 45 deg (sin 45 = 0.707 <= d
is allowed) is TWO-CONTACT's listed exception (a single vertical load at T balances B, A217's torque-neutral diamond).
For th != 45 deg B's loaded contacts besides the wall are >= 2 among: (c1) its flat A, at A's corner (d, 1) on B's edge
V->R [force on A along (sin th, -cos th): down and AWAY from the wall, so A's holder is its floor neighbour]; (c2) the
wall neighbour above: a FLAT A_TL touching B's top vertex T vertically (only with A_TL's bottom = y_T, FLAT-ABOVE
tight), or a T-meeter B' on B's edge T->R (a vertex-edge contact at a FREE position along the edge); (c3) a free /
interior square on B's edge V->R (the notch square G) or on T->R; (c4) BR's floor meeter at B's right vertex R (only if
it reaches x = w(th) <= 1.414 at height y_R = y_V + sin th; not excluded, listed).

**F3.3 [T] GEAR and LEVER for the three-contact poker (A239 s.3).**  With exactly (wall, c1, a vertical load at T):
F_out = cot th . F_in, and torque balance forces d = sin th + cos^3 th, which is > 1 for th < 57.1 deg and >= 0.98 on
[57.1 deg, 90 deg).  Consequences on W:
 (a) [T-cond] BL's poker B on x = 0 with TL's FLAT above it (a (Pi_BL, Phi_TL) wall) is torque-balanced by {wall, A_BL,
     A_TL at T} only if d_BL >= 0.98.  If the floor is a (Phi_BL, Pi_BR) wall, SIDE(PhiPi) gives d_BL < s - 3 <= 0.877:
     contradiction.  So **in the all-F pinwheel every LOADED poker has a contact of type (c3)/(c4): an interior square
     (or the far floor meeter at R)** -- the PI's "pinned by an internal square", as a theorem for the pinwheel under
     LOAD.  If the floor is (Phi_BL, Phi_BR) or (Phi_BL, tau_BR), d_BL >= 0.98 is not excluded by side; the poker is
     then steep (th >= 57.1 deg), y_T >= 1 + psi(th) + sin th >= 2.13 and A_TL sits at [y_T, y_T + 1]: s >= 3.13 only.
 (b) [T-cond] A T-neighbour B' on B's edge T->R has a free lever arm: torque balance of B is then possible for every th
     (A239's [C] beyond the family); the load leaves along B' with a gain fixed by the contact position, not by cot th.
     So F3 closes NOTHING for Pi-tau walls: the chase reaches an interior square only where the poker's top load is a
     flat's (vertical) load, i.e. on Pi-Phi walls.
 (c) [T-cond] Loop gain.  A closed wall-to-wall load loop through F corners alone (every poker with a vertical top
     load) needs Prod cot th_c = 1 with every th_c >= 57.1 deg, every factor < 0.65: impossible.  So a loaded chain
     through F corners only cannot close on itself; by CHAIN it ends at far walls -- which says nothing about interior
     squares (Trump's TL crowd does exactly this).  RING (A219) is [M] 193/193 at s > 4 and measured on the 12 rings
     below 4 (A239 s.2), a theorem only in its CHAIN form; the interior contact an F corner "needs" is the one named
     in (a), under LOAD, on a Pi-Phi wall whose flat partner's wall is PhiPi.
**F3.4 Bottom line.**  Torque adds to the room count exactly one conditional statement, (a).  It duplicates what
FAMILY-STUCK already gives unconditionally for the same wall (H-F1: the poker's slot on a Pi-Phi wall needs a free
square), so it is not used in part 6's table; it is recorded because the brief asked what the load path looks like.
