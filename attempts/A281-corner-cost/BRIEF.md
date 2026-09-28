# A281 -- CORNER COST: the two corner classes (F: one flush meeter + one tilted; T: both tilted) and what each
# costs in SIDE BUDGET and in TORQUE PINNING; a counting exclusion on the window from those costs alone.
# (PI, 2026-09-28: "after symmetry there are basically two classes: one flush one not, or both not -- can we use
# them to make statements about the side budget and torque pinnings?")
Fable.  TINY STEPS: one tool call per turn, <= 60 lines per Write, derivations on disk in numbered pieces
(notes/cost281_partN.md) committed as you go, never a single response over ~10k tokens; first turn = commit a
20-line outline.  LAUNCH-AND-EXIT -- never wait for a detached run.  ONE heavy python at most; never touch other
campaigns' processes / code / certs (the k5 loop, A262/A263 chains, the status loop are running).
READ FIRST: docs/proofs/k0_knowledge.md s.0.5, then s.1 (definitions), s.2 (theorems: the force/torque group A218/
A219/A233/A239/A248 and the window-exclusion group A258/A261/A264), s.5 (FALSE), s.7 (DEAD); the coordinator's
reduced catalogue docs/residue_map/current/corner_catalogue_reduced.svg (+ .json): against the partner alone every
floater pair lands, leaving floor + wall pairs in two contact graphs; then corner_chase.md (A248: type F = flat +
poker; POKE, TOP-2, FLAT-ABOVE; TWO-POKERS: two type-F pokers on one wall need s >= 3.9342370; Lean
two_pokers_window), type_t_chase.md (A249: type T; T-SLOTS, T-CELLS; the all-ADJ ring; TWO-TILTED fails as a
bound), normal_ring.md + family258 (least side of the common-tilt ring 1 + sec + cos + sin + tan(phi/2); mixed
senses from 3.9298; a flat row 3.9347; rows of three 3.9814), three_lemmas.md s.3 (near-flat cube), wedged_seal.md
(REACH R(theta, delta), GEAR-RATIO, LEVER: a torque-balanced CONTACT ring needs s > 4), local_lock.md (A233: at the
Psi-minimal optimum every meeter is LOCKED; RADIAL / CHAIN), k0_count.md (PUSH, HOLD), wall_torque.md (Lemma W,
TWO-CONTACT, ONE-TILTED, CEIL), ring_swap.md (RING: walls + meeters never balance), handedness.md (A234: no global
torque sum separates), mintilt253.md (the ring settles unless HELD by a ribbon poker), peel.md (BAND-COUNT).
## Framing (state it exactly; it decides what torque may be used for)
Room arguments hold for ANY packing at side s.  Torque / lock arguments hold only for an OPTIMAL packing (A233:
the Psi-minimal optimum is locked); they apply to k0 in the value form through: if a k0 packing existed at some
s < s-hat then s(11) < s-hat and the optimum at s(11) is locked; if the k >= 1 classes are excluded on the whole
window (the trees' job), that optimum is k0 and locked -- so every torque statement below is conditional on the
k >= 1 window rows, and must be tagged so.  Room statements are unconditional.
## The two classes and their costs -- derive as lemmas, n-general where the geometry allows
Class F (one flush meeter, sense 0, + one tilted): the flush square occupies length 1 of its wall flush; the
tilted partner B is a poker (A248) whose slot needs an interior square or the adjacent wall's meeter.
 F1 SIDE: along-wall extent consumed by an F corner on each of its two walls (closed form in B's tilt and offset);
    two F corners on one wall: TWO-POKERS (>= 3.9342, [T]); an F corner and a T corner on one wall: derive the
    analogous bound (A249's mixed case) -- is it > s-hat?  A flat ROW (two flush squares) costs 3.9347 [M->T?].
 F2 HOLDERS: the poker's slot cannot be flat-supplied (FLAT-ABOVE) -> one interior holder per F corner on the
    window (A248), or the adjacent corner's wall meeter (then that corner is T with a specific sense: say which).
 F3 TORQUE (conditional): a flat toucher against a wall has no wall torque; the poker's torque balance needs
    TWO-CONTACT (>= 2 further loaded contacts) -- what does the load path of an F corner look like, and can it
    close without interior squares (RING theorem says no: name the interior contact it needs).
Class T (both tilted): the PAIR corner of the ring.
 T1 SIDE: the chord / reach along each wall (A239's R(theta, delta)); the ring's least side as a function of
    tilt (family258); mixed senses >= 3.9298 [M -> certified by A261 for tilts >= 0.703 deg + the cube [T]]; so on
    the window the four T corners are ONE-SENSE (cite) -- state SIDE(T, T) per wall in closed form.
 T2 HOLDERS: the one-sense ring SETTLES (A253: the bare ring is one exchange per wall from a longer row; A258 P2')
    unless HELD: one ribbon poker holds the WHOLE ring (A249/A253) -- so four T corners cost ONE holder in
    total, plus what the holder needs (A252/A259: the holder contains O -> capacity 1).
 T3 TORQUE (conditional): LEVER -- a torque-balanced contact ring needs s > 4; so below 4 the ring's load path
    must pass through interior squares (the holders): how many contacts, hence how many interior squares,
    does torque balance of a one-sense ring need?  (A239 s.3; A233 RADIAL/CHAIN.)  Compare with T2.
## The count
With f F-corners and 4 - f T-corners on the window: side budget per wall (F1 + T1) vs s <= s-hat, and holders
(F2 + T2, and T3 if conditional) vs the 3 free squares: derive the table f = 0..4 and say which f survive on
the window by SIDE alone, by HOLDERS alone, by both; where the surviving cases are exactly the ring + one poker
(f = 0) -- already excluded by room -- and whatever else remains (f = 1? the F corner's poker as the ring's
holder?).  If a case survives all three, draw it and say what closes it.  Tag every line [T] / [T-cond] /
[T-computed] / [M] / [C].
## Deliverables
docs/proofs/corner_cost.md (pieces), Statements/Open/CornerCost.lean (the count as a theorem from the cited
axioms where it formalises; build + audit 0 sorry via PYTHONIOENCODING=utf-8 python lean/audit.py; one import
line after fetch + merge), page docs/residue_map/campaigns/A281-corner-cost/ (the two classes with their along-
wall extents and holders marked; the f-table; geometry-checked; note per panel; undecided grey stipple never
green), registry row, LOG entry, ledger s.4 note, APPEND entries to k0_knowledge.md.  Report once (<= 12 lines).
