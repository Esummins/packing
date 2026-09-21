# A258 -- NORMAL-RING: what a family-stuck packing looks like AFTER normalisation (the structure half of the k0
# exclusion; PI, 2026-09-21: "focus today on a theoretical exclusion for k0").
Fable.  LAUNCH-AND-EXIT -- NEVER wait for a detached run.  Ops: short responses, files <= 250 lines, no monitors, no
interim messages, explicit-pathspec commits (fetch + plain merge only), PYTHONDONTWRITEBYTECODE=1, ONE heavy python
process at most (BelowNormal, affinity 0xFFFF; sub-minute helpers fine); detached launches call Git Bash by explicit
path.  RUNNING, never touch: the k5 pass loop, A256's loop256, A257's pilot257, the status loop.  A259 (NORMAL-ROOM)
runs in parallel on the ROOM half -- do not duplicate it; write your family's parametrisation early (notes/
family258.md, commit it first) so A259 can read it.  Every lemma n-general (m = ceil sqrt n, eps = m - s) where it
can be; n = 11 on the window [3.82, s-hat] is the deliverable, [3.82, 4) the stretch.
Read first: docs/proofs/common_sense.md (A255: VALUE-WLOG [T] -- any packing at the same side may be studied;
Lemma NORMAL-CELL [T] = CELLS on the tilted cell T = s1 +- sec(phi) e; ONE-STEP NORMALISATION [T, Lean
exists_rowNormal]: maximise a potential over ALL packings at side s -- either some packing is not family-stuck or
the maximiser is family-stuck and normal; s.2.3 last line: a LEXICOGRAPHIC maximiser normalises all rows at once;
s.2.4: on A249's rings the normal cell is met ONLY by the facing toucher W, so the ring is NOT row-normal -- W
exchanges onto T; type F is a second structure; N1-N5), ring_swap.md (CELLS for cells of ANY pose), family250.md,
peel.md (A254: 8m-20 cells, 4(m-2)+1, BAND-COUNT, POKE), type_t_chase.md (T-SLOTS, T-CELLS), corner_chase.md
(TWO-POKERS, TOP-2, FLAT-ABOVE), construct_towards.md (NOT-SELF-SUFFICIENT), wedged_seal.md, sideband.md (B0/B0'),
mintilt253.md, A255 results (ringsense255: 0 of 84 mixed-sense rings; local255 / blocked255 witnesses).

## The coordinator's reading (check it; it may be wrong)
VALUE-WLOG lets us choose ANY potential, lexicographically: e.g. (number of wall-touching squares, sorted row-length
vector, then sum of row offsets toward a corner, ...).  Every exchange lemma we can prove (CELLS on a well-chosen
cell of any pose) becomes a normal-form property of the maximiser.  After W exchanges onto T each wall of A249's ring
carries a ROW OF TWO adjacent common-tilt touchers (translate sec(phi) along the wall); a row of two started at
offset delta spans delta + sec + cos + sin ~ delta + 2.25 at 14.5 deg, so it meets BOTH corner boxes iff delta > s - 1
- (sec + cos + sin), and its end cell delta + 2 sec + cos + sin > s leaves the container: normal.  Rows of three fit a
wall (2 sec + cos + sin ~ 3.28 < s) but cannot pinwheel on four walls below 4.  So the conjectured NORMAL RING is a
pinwheel of four common-tilt PAIRS: parameters (delta_w, phi_w) per wall, 8 coordinates + s -- not 17 -- and further
potentials may cut it down (equal tilts?  rows pushed to a corner?).  That collapse is the point: A259 bounds the
room on THIS family.

## Task
1. NORMALISATIONS.  List every exchange / motion lemma available or provable (NORMAL-CELL; a TOUCH-NORMAL cell that
   brings a floating root meeter to its wall -- N1; corner-ward slides of a whole row; tilt-equalising?), state the
   lexicographic potential, and prove the normal-form theorem: properties (P1..Pk) of the maximiser.  Lean: extend
   CommonSense.lean's exists_max_potential pattern (theorems where the set description suffices, documented axioms
   for prose lemmas).
2. CLASSIFY the normal-form family-stuck structures at m = 4: by wall, the possible row-length vectors (l1..l4),
   which squares meet which of the 12 border cells, the family-stuck inequalities, where pokers / free squares must
   sit (ribbons), type-F corners in normal form (a flat wall square is a row of sense 0: what does NORMAL-CELL give
   for it?  does the normal form kill type F on the window outright, with TWO-POKERS?), mixed senses (the corner
   step N4: two rows meeting at a corner box with opposite senses -- B0/B0' geometry; ring-level: can a mixed-sense
   pinwheel of pairs close?  analytic first; if needed a <= 9-coordinate interval branch-and-bound, benchmarked,
   detached, <= 100 CPU-h).  Output: Theorem / Conjecture NORMAL-RING(11): every normal-form family-stuck packing
   on the window is the pinwheel of four common-tilt pairs of one sense plus free squares, with the EXACT parameter
   domain D (inequalities in delta_w, phi_w, s) -- notes/family258.md FIRST, for A259.
3. TEST on the corpus + searches: normalise A249/A251/A253 rings by the exchange (are the results in D?  still
   family-stuck with the poker?); run a family-stuck search restricted to normal form at s in {3.82, s-hat, 3.95,
   3.99} -- anything outside D is a counterexample: draw it.
4. General m: state NORMAL-RING(n) (rows of m-2, wall slack -- A254 found the flush limit keeps slack for m >= 5);
   what is proved for all m, what is m = 4 only.
5. Say plainly what is [T], [T-computed], [M], [C]; the chain to FAMILY-STUCK-EXIST(11) with A259's room; the exact
   remaining obligations.  Deliverables: docs/proofs/normal_ring.md, notes/family258.md, the Lean file
   (Statements/Open/NormalRing.lean; build + audit 0 sorry; AUDIT.md rows), code/, results/, pages in
   docs/residue_map/campaigns/A258-normal-ring/ (the exchange W -> T on the ring, before / after; the normal ring
   with its parameters; each excluded structure with the reason; geometry-checked, a note per panel saying what it
   IS, undecided grey stipple never green), registry row, LOG entry, ledger s.4 note.  Report once (<= 20 lines).
