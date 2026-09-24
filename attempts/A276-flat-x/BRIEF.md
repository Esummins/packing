# A276 -- STRIP_2 with X near FLAT: the second-order corner (phi_X -> 0, theta_C <= 5 deg).  Route R2 only; R1 is dead.
# (2026-09-23.)
Fable.  TINY STEPS: one tool call per turn, <= 60 lines per Write, long derivations on disk in numbered pieces
(notes/flatx276_partN.md) committed as you go, never a single response over ~10k tokens (two agents died on the
64k cap on this very question); first turn = commit a 20-line outline.  LAUNCH-AND-EXIT.  ONE heavy python at
most; RUNNING, never touch: the status loop, A262/A263/A273 chains, A269/A270 loops, A275.
Read first: attempts/A274-flat-corner/results/r1_274.md (route R1 is DEAD: (U3), (U4), (U5), (U6) all fail inside
theta, phi <= 5 deg under H1-H3 -- exact witnesses drawn in r1_274.svg; only (U8) holds there, and it is a
theorem: 1.82 - w(theta) >= +0.03; STRIP_2's own margin: on the diagonal theta = phi it is FIRST order, ~0.5
theta; the zero-margin edge is phi = 0 (X flat) where it is ~0.25 theta^2 (0.0019 at 5 deg, 0.00031 at 2, 0.000078
at 1)), attempts/A273-disc-lemma/notes/disc273.md (the DROP LEMMA form; h_v-invariance; the box run's 81 cells
exclude the corner), docs/proofs/strip_jam.md (A272: what stops the intruder is X's right boundary + T_u's top
edge; the LEFT constraint; the case split by the centre's height; the worst intruder is FLAT with its bottom edge
on y = C_top and X FLAT), docs/proofs/strip_enclosure.md s.3, docs/proofs/ring_domain.md (H1-H3; Lemma LOW's
full-range form: only L_h > 1 is uniform), the geometry conventions in those notes.

## The question, narrowed
Fix X FLAT (phi = 0) first.  X's bottom edge is y = X_low on x in [0, 1]; C's top edge rises to the right at slope
tan theta; H2 (X overlaps T_u) and X disjoint from C force X_low into a window of width O(tan theta) above C's
top at x = 1 (the dip D is first order in theta).  Every square Q free of C and X with an interior point in S
must, by A272's LEFT constraint, sit right of X at X's heights and cross into S below X_low and above C's top
line -- a channel whose height is O(theta) -- or come from below (centre <= 1: WEDGE-FLOAT kills it).  Yet the
measured margin is only 0.25 theta^2: so the best intruder is NOT squeezing through the channel; find what it is
doing (A272: flat Q with its bottom edge on y = C_top, i.e. Q resting ON C's top line to the right of X, and its
interior point in S is ... where?  T_u's top edge is C's top edge shifted LEFT by h_u, which at a given x is
HIGHER than C's top by h_u tan theta -- so S has a thin sliver ABOVE C's top line, of height h_u tan theta, left
of C's right vertex?  Check: is that sliver where the intruder touches S, and is its clearance the 0.25 theta^2?).
Then the second-order proof: the sliver's height h_u tan theta vs the intruder's need to clear X's right edge
(x >= 1) and C's top edge simultaneously; an exact inequality in (h_u, theta, D) with the 0.25 theta^2 margin
reproduced.  Then phi small but nonzero: perturbation with an explicit constant (the diagonal margin 0.5 theta
says phi helps; show the margin is monotone in phi or bound the phi-derivative), covering [0, 5 deg]^2 minus
what A273's cells already certify (they exclude only the corner cell(s): read A273's index for which).
## Task
1. Outline (commit).  2. The X-flat lemma [T] with the mechanism identified.  3. The phi-perturbation [T].
4. docs/proofs/flat_x.md (in pieces), Statements/Open/FlatX.lean (build + audit 0 sorry; audit via lean/audit.py;
one import line after fetch + merge), page docs/residue_map/campaigns/A276-flat-x/ (the sliver and the resting
intruder at 5, 2, 0.5 deg; geometry-checked; note per panel), registry row, LOG entry, ledger s.4 note,
k0_route.md s.13 5b.  Report once (<= 12 lines): the mechanism, the statement proved and its domain, any
residual, anything in the brief that was wrong.  EXIT.
