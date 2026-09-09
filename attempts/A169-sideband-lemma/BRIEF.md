# A169 — the sideband lemma and the doubly-met-corner requirement (Fable lead)

Context (2026-09-09). A previous run of this attempt died on an output-size limit before writing
anything. Discipline for this run: every message short; files written in pieces of <= ~250 lines;
no large proof inline in a message; ONE final report under 1,500 words.

**Task.** Two lemmas about doubly-met corner boxes, stated for any n, needed by A168's k0 cascade.

(A) SIDEBAND. C = corner box of [0,s]^2 at BL: the closed unit box [0,1]^2, or the K0-WIDEN box
[0, 1+w]^2, w = 0.025509 on the window (docs/proofs/k0_route.md sec 3-4). Q1, Q2 interior-disjoint
unit squares inside the container, both meeting int C. Claim: at least one centre lies within 1 of
one of C's two walls (x <= 1 or y <= 1) and the other lies OUTSIDE that band. Settle the exact form,
the sharp constant as a function of w, and the precise meaning of "the other lies outside".
Coordinator's evidence: no disjoint pair with both centres beyond 1 in x and y (65k/81k samples,
best overlaps -0.146 unit / -0.092 widened, anti-diagonal ~45 deg pairs); two 45-deg diamonds at
(0.99,1.70)/(1.70,0.99) are disjoint and both meet the unit box, so threshold 1 may be tight.

(B) REQUIREMENT. What a doubly-met corner requires. Atlas evidence (docs/residue_map/gen_two_meeter*.py):
a PRESSED first meeter admits no second meeter of the unit box; slide thresholds d*(theta) =
0.18/0.34/0.38/0.56/0.64/0.72 at theta = 0/15/30/45/60/75; diagonal pull ~1.04-1.18. PI's closed
form: deep meeter Q1 slid delta from a wall; deepest second meeter = unit square flush with the side
wall resting on Q1, rotated theta to fit the gap, intrusion in csc(theta), valid while sin(theta) <=
delta; shallowest = core just touching the top of the gap with a corner. Derive depth_max(delta,
theta) + validity; the shallow curve; admissible region + area A(delta); delta_min(theta_1) vs d*;
widened versions; general (slide + pull) displacement region per tilt; the k0 consequence as a
NO-family / box / chord row the k0 case-LP can consume (say which, exactly).

(C) LEAN. docs/proofs/sideband.md (both lemmas [T], exact constants, proofs) and
lean/PackingCertMathlib/PackingCertMathlib/Sideband.lean in project style (PolyCoreT5.lean,
Local.lean; available: CaseSat.sat_squares, SatInterior.sat_selection_thm,
PolyCoreT5.shared_point_same_square); lakeb.py at BelowNormal, one build at a time, no sorry, roster
reported; algebraic forms in t = tan(theta/2) where possible.

(D) CONSUMPTION by A168's cascade: the corner step splits into a BAND meeter (priced by A144's chord
row on that wall) and an OUTSIDE meeter bounded by the corner reach; exact regions for BL with H
absent and with a conditioned square present. If a claim is FALSE: exact counterexample + strongest
true replacement.

**Rules.** Theory + light computation; <= 2 processes BelowNormal affinity 0xFFFF; box ceiling 16
(count and wait); read-only on every campaign and prior attempt (new files only under this attempt,
docs/proofs/sideband.md, the Lean file); no recursive deletes; PYTHONDONTWRITEBYTECODE=1; git =
fetch + plain merge + `git commit -- <pathspecs>`; registry row, LOG entry, known_results line.
Every claim [T]/[S]/[M]/[F]/[C].

**Files.** notes/derivation.md (the maths, in pieces), code/*.py (numeric checks), results/*.json,
docs/proofs/sideband.md, lean/.../Sideband.lean.
