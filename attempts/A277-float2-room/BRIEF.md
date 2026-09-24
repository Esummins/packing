# A277 -- ROOM at the FLOAT2 and INDIRECT-JAM corners: the last unowned link of NO-JAM(11) (chain link 5d).
# (2026-09-23.)
Fable.  TINY STEPS: one tool call per turn, <= 60 lines per Write, derivations on disk in numbered pieces
(notes/float277_partN.md) committed as you go, never a single response over ~10k tokens; first turn = commit a
20-line outline.  LAUNCH-AND-EXIT.  ONE heavy python at most (the lab is at its ceiling; prefer sub-minute
helpers).  RUNNING, never touch: the status loop, A262/A263/A273 chains, A269/A270 loops, their certs.
READ FIRST: docs/proofs/k0_knowledge.md (the onboarding document: definitions s.1, the corner types and the JAM
row s.2/s.8, the FALSE statements s.5 and the DEAD routes s.7 -- do not repeat them), then docs/proofs/no_jam.md
(corner types PAIR / THIRD / JAM / FLOAT2; COUNT + ROOM => n <= 9 for every type [T, Lean jam_count_core,
no_jam_of_count]: if every unit square disjoint from the minimal box-serving structure S_min contains O then n <=
9; the sector decomposition for JAM; 5d: indirect jams (a non-toucher blocker), FLOAT2 corners, a middle toucher
above X), attempts/A262-no-jam/results/float262.json (the FLOAT2 witness: C 14.5 deg and D 12.9 deg both float
and meet the box; A on the floor and X on the wall block their drops; sup_t +0.0022; drawn in
docs/residue_map/current/k0_stuck_2026-09-23.svg panel (b)), docs/proofs/normal_room.md (MISS => corner PAIR: a
free square missing O violates a two-square statement at one corner; HOLE-ONE tilt form; TOOTH; WEDGE),
docs/proofs/strip_enclosure.md + strip_jam.md + flat_x.md + ring_domain.md (how the JAM corner's floater C was
handled: WEDGE-FLOAT for the corner-box entry, the strip replaced by C's wall drop T_u, STRIP_2 under H1-H3),
docs/proofs/box_meeters.md (SAME-WALL, BLOCKER-SIDE, STRIP-LANDING, LIFT), docs/proofs/locked_wall.md (LIFT).

## The question
For each corner type not yet covered, the ROOM statement: every unit square disjoint from S_min (the corner's
box-serving squares + the ring's other walls) contains O -- or, if that fails, the sharper count the chain needs.
 (a) FLOAT2: S_min at the corner = {C, D} floating + their blockers A (floor) and X (wall).  Reduce as for JAM:
     which of C, D can be replaced by its wall / floor drop for room purposes (a STRIP_2-type lemma for each: the
     free squares avoid the drop strip -- reuse WEDGE-FLOAT for the corner-box entry and the FLAT-X / CORNER
     mechanism for the near-flat case; say exactly which hypotheses of H1-H3 the FLOAT2 corner satisfies and
     which it does not, e.g. X now blocks C but D sits between?).  Then the sectors are pair-type certificates
     already run (A259 PAIR / A262 pair3) or one new one (price it; own verifier; launch only if <= 20 CPU-h).
 (b) INDIRECT JAM: the floater C is held not by a wall toucher X but by a non-toucher (a free square or a middle
     square) -- state it, show it reduces to the direct JAM (the holder must itself be held: P4 RETREAT chain
     ends at a toucher), or to a smaller room (the holder is a free square that contains O?), or draw the
     configuration that escapes.  Also the "middle toucher above X" variant (span262 sup_t -0.0327: none found).
 (c) Say plainly what NO-JAM(11) then still lacks (pair3's index; A273's three capped cells c5_4-c5_6).
## Task
1. Outline (commit).  2. (a) then (b), [T] with citations; every witness exact; the tiny-step regime throughout.
3. docs/proofs/float2_room.md (in pieces), Statements/Open/Float2Room.lean (build + audit 0 sorry via
PYTHONIOENCODING=utf-8 python lean/audit.py; one import line after fetch + merge), page in
docs/residue_map/campaigns/A277-float2-room/ (the FLOAT2 corner with its drops and sectors; geometry-checked;
note per panel; undecided grey stipple never green), registry row in attempts/REGISTRY.md, LOG entry, ledger s.4
note, k0_route.md s.13 link 5d, and APPEND your [T]/[F]/[C] entries to docs/proofs/k0_knowledge.md (s.2/s.5/s.6)
-- that document is the lab's memory.  Report once (<= 12 lines).  EXIT.
