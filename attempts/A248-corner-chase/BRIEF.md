# A248 -- the CORNER CHASE: teleport-stuck + directionality + torque pinning, followed around the perimeter, with no
# internal square allowed to pin (PI, 2026-09-17 00:30).
Fable. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns (checks detached
with a resume block and logs/STOP), explicit-pathspec commits, PYTHONDONTWRITEBYTECODE=1, <= 1 python process
(BelowNormal, affinity 0xFFFF; the k5 frontier, A238, A241, A244's lanes and A247's triples are running -- never
touch them).  Pages to docs/residue_map/campaigns/A248-corner-chase/.
Read first: ring_swap.md (SWAP / CELLS: a family of disjoint cells met by <= |family| squares exchanges into the
slot squares -- the PAIR teleport of BL00 + BL01), local_lock.md (A233: at the Psi-minimal optimum nothing RETREATS
-- every meeter of a doubly-met corner is LOCKED; RES-LOCK: 3.3 square-square rows + 1 wall row per intruder;
RADIAL / CHAIN), snap_down.md (A245: STACK's true form -- a mutual wall pair below 4 is ordered, both meet both
slots, resting contact types; WALL-CLICK under H-ROOM lowers the side; directionality enters only through Lemma W),
cross.md (A240: PARTNER-TORQUE; locked corners are same-handed 215:11), wall_torque.md (Lemma W; TWO-CONTACT),
k0_count.md (PUSH, HOLD), wedged_seal.md, construct_towards.md (A246: NOT-SELF-SUFFICIENT [T], TYPE-F-OWN [T]: a
flat floor meeter serves exactly BL00 + BL10, never BL01), perimeter_walk.md (A247: PROJECTION, TWO-FAR, UPPER-END;
the UNLOCKED walks number ~1e10 -- incidence alone is loose; the 764 twelve-stuck packings, NONE locked), A244.

## The PI's chain (verbatim in substance)
"k0 implies there is no set of squares that can be teleported to simple.  BL: if the close meeter A is flush with
the floor, it has to slide far enough from the wall to allow a second meeter B from above; B is tilted so a corner
pokes down into BL00 -- the tilt has to be CCW for the poking corner to be at the wall side; then BL01 needs a
second meeter so the PAIR (A, B) cannot be teleported to the domino; with B's tilt CCW the only way to get it is a
same-tilt square B' above B or a centre square.  Take B': with s < 4 there is little room to fit TL00's second
meeter.  For the two left-wall squares not to just ROTATE out of the way (freeing BL00 for teleport), B' has to be
torque-pinned, which constrains where TL00's second meeter sits.  Follow the non-internal pinning options around
the outside: I think we run into a contradiction -- everything cannot be pinned without an internal square."
This adds to A247's incidence walk the two constraints it lacked: DIRECTIONALITY (which tilt sense a poking meeter
must have, hence which side its stack / notch is on) and PINNING (A233: at the Psi-minimal optimum every retreat --
including the joint rotation of a wall pair that would free a corner -- is excluded, so the structure is locked;
RES-LOCK counts the rows a lock needs).  A247's 1e10 unlocked walks should collapse under these.

## Task
1. Lemma POKE (any n) [prove]: a square meeting the open corner box from above the flat floor meeter, touching the
   left wall, must have its lowest vertex on the wall side, hence tilt sense CCW (in the corner's frame); its
   highest vertex is then on the far side, so the notch for a second meeter of BL01 is on the wall side above it:
   the second meeter of BL01 is a wall square above B (same-tilt stack, A245's STACK types) or an interior square
   through the notch -- and A (flat) never serves BL01 (TYPE-F-OWN).  Cover the case A tilted too.
2. Lemma NO-ROTATE [prove from A233]: at the Psi-minimal optimum the wall pair (B, B') cannot be rotated jointly
   toward flush (that is a retreat freeing BL00), so the pair is locked: state exactly which rows must be loaded
   (RES-LOCK / HOLD / TWO-CONTACT) and who can supply them without an interior square: A, the TL corner's meeters,
   the walls.  Derive the constraint on TL00's second meeter.
3. The CHASE: continue around TL, TR, BR with the same two lemmas, keeping every pinner EXTERNAL (walls + the 8
   meeters + wall stacks), and either reach the contradiction (state the closed-form inequality that fails for
   s < 4) or exhibit the consistent external chase (then an interior square is not needed and the argument
   fails -- draw it).  Then allow interior pinners: how many are needed, and can 3 free squares that fit (Lemma
   TWO: the centre holds one) supply them?
4. TEST on the 764 twelve-stuck packings (none is locked -- they must FAIL the chase somewhere: report where) and
   on A217's genuine FJ points' doubly-met corners (locked ones: which step of the chase they satisfy).
5. Say plainly what is proved [T], what the chase needs [C], and whether POKE + NO-ROTATE + the chase gives
   LOCKED-CROWD-FREE(11) below 4 (then k0_00 closes via A233's theorems).  Lean: Statements/Open/CornerChase.lean
   (POKE as a theorem if it formalises from the square's set description; NO-ROTATE / the chase as documented
   axioms + the consequence chain; build + audit, 0 sorry).
6. Deliverables: docs/proofs/corner_chase.md, the Lean file, code/, results/chase248.md (+jsonl), pages (BL's
   forced structure step by step; the chase around the perimeter; the failing step on a twelve-stuck packing),
   registry row, LOG entry, ledger s.4 note.  Report once (<= 20 lines) and EXIT.
