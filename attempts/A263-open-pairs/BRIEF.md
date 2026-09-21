# A263 -- OPEN PAIRS: force common tilt on an open wall (LOCK-TILT), close the non-ADJ hybrids and the near-flat
# slab -- the ROOM / certificate leftovers of the k0 exclusion.  (PI theory day on k0, 2026-09-21/22.)
Fable.  LAUNCH-AND-EXIT -- NEVER wait for a detached run.  Ops: short responses, files <= 250 lines, no monitors, no
interim messages, explicit-pathspec commits (fetch + plain merge only), PYTHONDONTWRITEBYTECODE=1, ONE heavy python
process at most (BelowNormal, affinity 0xFFFF; sub-minute helpers fine); detached launches call Git Bash by explicit
path.  RUNNING, never touch: the k5 pass loop, A256's loop256, A257's pilot257, the status loop, A259's / A260's /
A261's certificate chains and their certs.  A262 runs in parallel on NO-JAM.
Read first: docs/proofs/locked_wall.md (A260: UNLOCK = P2'; LIFT; OPEN-TOOTH closed form, least notch depth
cos(phi)(1 - e sin phi) at the row's tilt; hybrid PAIR certificates for open pairs of COMMON tilt; [M] adversary
over the 16-coordinate hybrid family with independent tilts: sup miss-margin -0.0654 at s-hat; still [C]:
LOCK-TILT -- an open wall whose s1 and W have different tilts, ~50 CPU-h for one open wall per corner, beyond
budget for two; non-ADJ hybrids), normal_room.md (A259: MISS => corner PAIR, 4 parameters (b, phi; a', phi'), s
eliminated), normal_ring.md + family258.md v2 (P1-P4; the hybrid family D^h), box_meeters.md (A261: admissible
axes [T]; the box-valid LP certificate; [T] no closed-LP certificate reaches a flat wall -- the slab of tilts
(0, 0.703 deg) stays [M]; an exactly flat row costs 3.9347), common_sense.md (NORMAL-CELL: CELLS on a cell of any
pose; VALUE-WLOG).

## The coordinator's readings (check them)
(a) WHY DOES THE PAIR NEED phi_1 AT ALL?  A259's corner PAIR sees wall w's END square W (b, phi_W) and wall w+1's
    START square (a', phi').  The notch between s1 and W on wall w is a different place: a free square missing O
    through the notch is bounded by OPEN-TOOTH.  With unequal tilts the notch is a wedge between s1's right edge
    (tilt phi_1) and W's left edge (tilt phi_W): give OPEN-TOOTH for the wedge in closed form (depth as a function
    of e, phi_1, phi_W, psi) -- it is a 3-parameter one-wall lemma, NOT a corner lemma, so the certificate should
    factor: corner PAIRs (4 parameters, done by A259) x wall NOTCHES (3 parameters).  If the miss-O test really
    couples the notch to a corner, say exactly how, and find the factorisation that keeps every piece <= 5
    parameters.
(b) FORCE COMMON TILT by an exchange: the cell T_e = s1 + (sec phi_1 + e') e_wall re-posed where W stands, at
    s1's tilt: met by W, perhaps by the locker F and by wall w+1's start square.  When is |M(T_e)| <= 1 (then W
    exchanges onto it and a potential term "open pairs of common tilt" rises), and what does the other case force?
(c) NON-ADJ hybrids: a wall slot served by a free square instead of the facing toucher.  If every free square
    contains O (the PAIR bound does not care about ADJ), at most one free square exists; how many wall slots can
    one square containing O serve (it is >= 1 - ... from every wall: can it reach depth < 1 on any wall?  TOOTH
    says only through a notch).  Count => non-ADJ dies or is the locked wall again.
(d) THE SLAB (0, 0.703 deg): near-flat walls.  The LP relaxation degenerates at tilt 0; replace it there by the
    analytic statement (a row of tilt phi -> 0 is a flat row up to O(phi): its cost 3.9347 - C phi > s-hat for phi
    <= 0.703 deg with an explicit Lipschitz constant C), [T] with the constant certified.

## Task
Do (a)-(d): proofs first; certificates (own verifier; benchmark; detached if <= 50 CPU-h total) where analysis
stops; tests against A260's adversary rows and the 46 corpus rings.  Say plainly what ROOM and the window
exclusions now are, on which families, [T] / [T-computed] / [M] / [C]; the exact remaining obligations.
Deliverables: docs/proofs/open_pairs.md, Statements/Open/OpenPairs.lean (build + audit 0 sorry, no "(no output)"
rows; AUDIT.md rows; one import line in Statements.lean after fetch + merge), code/, results/, certs/, pages in
docs/residue_map/campaigns/A263-open-pairs/ (the wedge notch with the deepest free square; the factorised
certificate map; the near-flat row; geometry-checked, a note per panel saying what it IS, slivers with a 10x
inset, undecided grey stipple never green), registry row, LOG entry, ledger s.4 note.  Report once (<= 20 lines).
