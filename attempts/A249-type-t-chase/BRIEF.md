# A249 -- the corner chase for TYPE-T corners (both meeters tilted): the case A248 did not reach (2026-09-17 09:00).
Fable. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns (checks detached
with a resume block and logs/STOP), explicit-pathspec commits, PYTHONDONTWRITEBYTECODE=1, <= 1 python process
(BelowNormal, affinity 0xFFFF; the k5 frontier, A238, A241, A244 lanes and A247 triples are running -- never touch
them).  Pages to docs/residue_map/campaigns/A249-type-t-chase/.
Read first: docs/proofs/corner_chase.md (A248: POKE's true form -- TILT-MIN, TOP-2 (a poker's top vertex is at
height >= 2), FLAT-ABOVE (no flat wall square with bottom < 2 coexists with a poker); NO-ROTATE [T] from A233 (the
flush-stack click is a retreat; blockers are always external, so pinning forces no interior square); Lemma
TWO-POKERS [T]: two type-F pokers on one wall need s >= s* = 3.9342370 > s-hat, so on the window every type-F
poker's slot needs an interior square, <= 1 type-F poker per wall, and four type-F corners need >= 4 > 3 free
squares (given SEPARATE-NOTCHES [M]); the type-T corner -- both meeters tilted, 2912 of 3056 corpus corners -- NOT
reached), perimeter_walk.md (PROJECTION, TWO-FAR, UPPER-END), snap_down.md (STACK's true form), wedged_seal.md
(a meeter on both walls is alone: in a type-T corner the two tilted meeters touch different walls, or one touches
no wall), k0_count.md (PUSH: the two meeters push each other out along their walls; HOLD), wall_torque.md
(TWO-CONTACT: a loaded tilted wall square needs >= 2 further loaded contacts), sideband.md (B0/B0': the geometry
of two squares both meeting the open corner box), pocket_waste.md (TILT-MIN, DEPTH-BUDGET), the corpus (A244's
764 twelve-stuck packings, A217's genuine FJ points with their 45 locked type-T corners: the test set), A248 code
(chase248, twopokers248, notches248, external248 -- reuse).

## The question
Type-T corner c: meeters A (touches the floor or no wall) and B (touches the wall or no wall), both tilted, both
meeting the open box; the 12-stuck hypothesis needs c01 and c10 doubly met too (WALL-SLOT); A233's Psi-minimality
locks both.  A248's route for type-F: the poker's slot cannot be flat-supplied, two pokers per wall need s >= s*,
so the slot's second meeter must be interior, and 3 interior squares cannot serve four corners.  Do the same for
type-T:
1. Lemma T-SLOTS [prove]: which squares can be the second meeter of c01 (and c10) when B is a tilted wall
   toucher: the adjacent corner's wall meeter (a tilted stack: STACK's resting types; the height budget h + h' <=
   s - delta - delta' with TOP-2-type bounds), A's own tip (when A is tilted its top vertex can rise into c01 --
   A248's TOP-2 is for the poker; derive A's reach into c01 from B0/B0'), or an interior square.  Give the exact
   inequalities in (theta_A, delta_A, theta_B, delta_B, s).
2. Lemma TWO-TILTED [prove or certify]: the analogue of TWO-POKERS -- two type-T corners on one wall with the wall
   slots served externally (by each other's wall meeters, or by the floor meeters' tips) need s >= s_T*: compute
   s_T* by the chord / height argument, certify the minimum over the parameter box (interval branch-and-bound as
   twopokers248), and compare with s-hat and 4.  If s_T* <= s-hat, the external ring of type-T corners is NOT
   excluded on the window by this route: say so, and find what else the lock (NO-ROTATE, TWO-CONTACT, RES-LOCK
   rows) forces on such a ring -- is its pinning consistent with external contacts only?
3. Mixed rings (type-F and type-T corners on the same wall) -- the inequalities pairwise; the count: with <= 1
   type-F poker per wall and the type-T bounds, how many corners can be served externally on the window, and does
   the shortfall exceed the 3 free squares (the SEPARATE-NOTCHES dependence made explicit or removed)?
4. TEST on the 45 locked type-T corners of the genuine FJ points (every inequality must hold there, at their own
   sides >= 3.897) and on the 764 twelve-stuck packings' type-T corners; report the tightest witness on the window
   side and which inequality binds.
5. Say plainly: if TWO-TILTED + T-SLOTS + the count close the type-T and mixed cases below s-hat, then with A248
   LOCKED-CROWD-FREE(11) is proved on the window and k0_00 closes via A233's theorems -- state it; else the exact
   remaining case with a drawn witness.  Lean: Statements/Open/TypeTChase.lean (theorems where prose formalises,
   documented axioms otherwise, the consequence chain; build + audit, 0 sorry).
6. Deliverables: docs/proofs/type_t_chase.md, the Lean file, code/, results/typet249.md (+jsonl, certificates),
   pages (a type-T corner's forced structure; the two-tilted bound; the tightest corpus witness), registry row,
   LOG entry, ledger s.4 note.  Report once (<= 20 lines) and EXIT.
