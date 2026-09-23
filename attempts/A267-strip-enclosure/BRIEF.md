# A267 -- STRIP_2 by ENCLOSURE: the PI's route (keep A and X as obstacles; the strip is walled in; the only entries
# are two narrow gaps and the open corner below).  Hand proof first.  (2026-09-23.)
Fable.  LAUNCH-AND-EXIT -- NEVER wait for a detached run.  Ops: short responses, files <= 250 lines, no monitors, no
interim messages, explicit-pathspec commits (fetch + plain merge only), PYTHONDONTWRITEBYTECODE=1, ONE heavy python
process at most (BelowNormal, affinity 0xFFFF; sub-minute helpers fine); detached launches call Git Bash by explicit
path.  RUNNING, never touch: the k5 pass loop, A256's loop256, A257's pilot257, the status loop, the chains of
A262 / A263 / A265 / A266 and their certs.
Read first: docs/proofs/last_two.md s.1 (A266: STRIP_2 restated -- domain: C meets the open corner box (0,1)^2,
h_u in (0,1), tilt in [0, 45]; X leftmost vertex on the wall, lowest point >= C's, disjoint from C, overlapping
T_u; claim: no unit square disjoint from C and X in the quadrant has an interior point in S = T_u minus C; [T] flat
C (A265 s.1.3), [M] 60/60 + 323 rings, the 5-parameter tree ~5e3 CPU-h -> hand proof; s.1.4 the SAT case list),
docs/proofs/strip_plug.md s.1 (A265: why A was dropped -- exact region search on the JAM rings with {C, X} alone
finds no square entering S, so the two-obstacle form holds and is stronger), docs/proofs/no_jam.md s.2 (the JAM
corner; C meets the box by a sliver 0.003-0.010 deep; HELD-JAM: the bare ring never pins C), docs/proofs/peel.md
(POKE: a square enters a gap of width g by one vertex to depth <= g/2), box_meeters.md (SAME-WALL: two touchers of
one wall cannot both meet the open box; meeters_split), the coordinator's page
docs/residue_map/campaigns/A266-last-two/strip_clean.svg (panel (b) = an in-domain point; panel (a) = A266's
out-of-domain witness), attempts/A262-no-jam/results/ring262.jsonl + code/geom262.py (verts: squares 0 = A,
6 = X, 7 = C on the 43 JAM rings with t > 0).

## The coordinator's measurements on the 43 JAM rings (2026-09-23; reproduce first)
C hovers at the box's top: h_v (C's lowest point) = 0.988-0.999 on every ring, h_u = 0.38-0.72, C meets the box by
area <= 3e-4.  C touches NEITHER A (gap 0.0009-0.0106) NOR X (gap 0.0016-0.042).  A lies entirely RIGHT of x = h_u
(A's area in the band [0, h_u] x [h_v - 0.6, h_v] is 0 on every ring), so A does NOT close the strip from below:
below S = T_u minus C (a band along the wall from height ~1 to ~2.2, width h_u) lies the EMPTY corner box.

## The PI's route (state it exactly, then prove it)
With A and X kept as obstacles, S is enclosed: wall on the left, C on the right, X above, and below it the corner
box.  A free square Q with an interior point in S must enter through (i) the C-X gap (width g_CX, POKE depth
<= g_CX / 2 -- show a poke there does not reach an interior point of S, or bound it), (ii) the A-C gap (same), or
(iii) from BELOW through the corner box -- then Q meets the open box, so Q is a THIRD meeter of the corner: by
SAME-WALL and meeters_split Q is a wall toucher (the wall has none meeting the box) or a second floater; in either
case say what happens: the corner is no longer a JAM of type (1,0,1) -- it is (1,1,1) with C a pocket square
(A262's THIRD row: covered by the PAIR ring, C in its pocket), or FLOAT2 (A262's float262: jammed FLOAT2 exists,
margin 0.0022 -- its room is a separate obligation N5; say whether the enclosure argument applies to it too).
So STRIP_2 in the JAM ring reduces to: pokes through two gaps of width < 0.05 cannot reach S -- a closed-form
inequality in (h_u, h_v, theta_C, y_X, phi_X, g) -- plus the case split (iii).  Prove it on the JAM domain; if the
gap widths must be bounded, get them from the JAM conditions (C meets the box, X overlaps T_u, C not pinned by the
ring) or from the maximiser (P4 / held: is C in contact with its holder G?).  General-m: everything here is
corner-local and s-free -- say so.

## Task
1. Reproduce the measurements; draw the enclosure on two JAM rings (wall, A, C, X, T_u dashed, S stippled, the
   two gaps with a 10x inset, the empty corner box) -- geometry-checked, a note per panel saying what it IS.
2. Prove STRIP_2-IN-RING by the enclosure route ([T]), or the exact sub-case that resists, drawn; the POKE bound
   for each gap in closed form; case (iii) resolved by the corner-type table.
3. Consequence: with jam_sector_of_strip and pair3 (A262's chain3 -- read its index if landed), NO-JAM(11)'s BL
   sector; list what NO-JAM(11) still lacks.  Lean: Statements/Open/StripEnclosure.lean (build + audit 0 sorry,
   no "(no output)" rows; AUDIT.md rows; one import line after fetch + merge).  Deliverables:
   docs/proofs/strip_enclosure.md, the Lean file, code/, results/, pages in
   docs/residue_map/campaigns/A267-strip-enclosure/, registry row, LOG entry, ledger s.4 note, k0_route.md s.13
   link 5b updated.  Report once (<= 15 lines).  EXIT.
