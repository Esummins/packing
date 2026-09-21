# A255 -- COMMON-SENSE: the local lemma behind ONLY-RING -- chase the second-meeter requirement out of a corner and
# show the wall meeters it forces share a tilt sense (or the structure reduces by CELLS)  (PI, 2026-09-20).
Fable (the statement + soundness first; the search second).  LAUNCH-AND-EXIT -- NEVER wait for a detached run.
Ops: short responses, files <= 250 lines, no monitors, no interim messages, explicit-pathspec commits (fetch + plain
merge only), PYTHONDONTWRITEBYTECODE=1, at most 2 python processes (BelowNormal, affinity 0xFFFF; the k5 pass loop,
the status loop and A254's search are running -- never touch them; kill only your own python.exe by command line).
Pages to docs/residue_map/campaigns/A255-common-sense/.  Lemmas stated n-general (m = ceil sqrt n, eps = m - s).

## The PI's argument (verbatim in substance)
"Assume a corner non-simple.  Its root (the unit box flush in the corner) has two meeters.  Pick up both: if either
adjacent unit box becomes free, put the two down in root + that box -- now simple.  By recursion the second-meeter
requirement is chased around the outside, through the other three corners.  Because of HOW two meeters can meet the
root, for the chain to keep failing to simplify we need common-tilt squares along the sides, which force the other
corners into similar common-tilt corner packings.  For the FULL set not to simplify we need a common-tilt ring AND a
poker that pins the ring so it cannot settle its tilt to zero."  The lemma to prove is the middle sentence.  "Place
two squares that touch the root, then check how the second tile out can be met; I suspect the meeters further out
end up common tilt along the wall (or reducible to that)."

## What exists (read first)
ring_swap.md (CELLS [T, Lean cells_swap]: the pick-up-and-put-down move IS CELLS on the domino {c00, c01}: met by
<= 2 squares => exchange), family250.md + A254 docs/proofs/peel.md (FAMILY-STUCK(n), the 8m-20 cell system, ribbons
eps / 1-eps, ring + narrow-ribbon poker attains 4(m-2)+1), construct_towards.md (NOT-SELF-SUFFICIENT [T]: a corner's
two meeters cover <= 5 of its 6 incidences; TYPE-F-OWN), sideband.md (B0/B0': all ways two squares both meet the
open corner box), wedged_seal.md, corner_chase.md (A248: type-F corner = flat + poker; TOP-2, FLAT-ABOVE,
TWO-POKERS s* = 3.9342370; the coordinator's CW-poker witness cw_poker_witness.svg: a poker's tilt sense is NOT
forced locally -- the lemma must survive this), type_t_chase.md (A249: T-SLOTS -- the exact list of possible second
meeters of c01; T-CELLS; the all-ADJ ring; s.3.4 non-ring / mixed structures), perimeter_walk.md + A247 code
(triples247: interval branch-and-bound over pose triples per walk; PROJECTION, TWO-FAR; it sought INFEASIBILITY and
mostly got FEASIBLE/BUDGET -- A255 changes the question to CLASSIFICATION), mintilt253.md (tilt window (0, tau_max);
the bare ring settles continuously to the flush pinwheel at fixed side; the poker's ribbon closes as tau -> 0),
A244 twelve244.jsonl (488 certified twelve-stuck), A217 witnesses, A251 joint251.json rings.

## Task
1. STATE the chase as lemmas with exact hypotheses.  Tilt SENSE of a wall toucher: tilt mod 90 in (0,45) vs
   (45,90) measured the same way round the perimeter (so a pinwheel has one sense); flat = sense 0.  Candidate:
   Lemma COMMON-SENSE (local): in a FAMILY-STUCK packing at s in (m-1, m), along any wall the squares meeting the
   wall cells c00, c01, ... of one corner, other than squares shown to be pokers/interior by T-SLOTS, are wall
   touchers of ONE sense, and the corner's other wall carries the SAME sense (the pinwheel propagation); else some
   family Pi has |M(Pi)| <= |Pi|.  "Reducible" may ONLY mean a CELLS exchange (or a move already a theorem:
   NO-ROTATE / A233 retreats in the value form -- say which form each use needs); tilt settling is not a reduction
   unless proved side-non-increasing with contacts kept.  Decide what the poker's role is in this language (the
   incidence that breaks the 16 families; and the obstruction to the ring's settling) and how type-F corners
   (the CW-poker witness) enter: excluded by TWO-POKERS + interior count, or a genuine second structure?
2. TEST FIRST on the corpus (cheap, before any tree): for every corner of the 488 + 486 + ring witnesses, the
   senses of its wall-cell meeters, per wall and across the corner; tabulate violations of COMMON-SENSE and, for
   each violation, the family Pi that CELLS reduces it by (the coordinator's family test: all families of pairwise
   disjoint border cells, |M(Pi)| <= |Pi|).  If a violation is family-stuck-locally (no reducing family inside the
   corner's five-cell neighbourhood), draw it -- that is the counterexample or the missing hypothesis.
3. THE EXHAUSTIVE LOCAL SEARCH (the PI's): root meeters A, B by B0/B0' type (floor toucher / wall toucher / free;
   WEDGED-SEAL), then the third square C meeting c01 (T-SLOTS types), then D for c10: interval branch-and-bound on
   the COUNTER-hypothesis "opposite senses (or flat + tilted) AND every family inside the neighbourhood over-met"
   at s in [3.82, 4): certify infeasible per type, or return the feasible boxes drawn.  Reuse triples247's engine;
   benchmark 20 boxes before estimating; stop at the price if > ~200 CPU-h.  Run detached with a resume block and
   logs/STOP, per-type commits.  Then say what changes for m >= 5 (the chain c01, c02, ... is not overlapped by the
   facing corner until the mid-wall: is the local lemma the same statement with eps general?).
4. Say plainly: COMMON-SENSE proved / certified per type / false (witness), and the chain COMMON-SENSE =>
   ONLY-RING(11) (what else is needed: closing the pinwheel round four corners; the poker count) => with A253/A254
   room => FAMILY-STUCK-EXIST(11).  Lean: Statements/Open/CommonSense.lean (documented axioms for prose lemmas,
   theorems where the set description suffices, the consequence chain to only_ring in Peel.lean; build + audit,
   0 sorry, AUDIT.md row).  Deliverables: docs/proofs/common_sense.md, the Lean file, code/, results/sense255.md
   (+jsonl), pages (the chase drawn corner by corner: root meeters, the blocked adjacent box, its blocker, the sense
   arrows; every violating corpus corner class with its reducing family; geometry-checked, a note per panel saying
   what it IS, undecided grey stipple never green), registry row, LOG entry, ledger s.4 note.  Report once
   (<= 20 lines) and EXIT.
