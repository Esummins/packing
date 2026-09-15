# A218 -- LEMMA TORQUE in its surviving form: the k0 COUNT (PI torque intuition -> A217's finding; 2026-09-14 18:00).
Fable. LAUNCH-AND-EXIT (theory; write, prove, test, commit, report, exit; any long check detached with a resume block).

A217 (attempts/A217-torque-probe/notes/torque.md, results/torque217.md): on 3,555 FJ-feasible local optima no sign-rule
torque invariant survives (Lemma W is an identity; the signed sum fails at Trump's open TL corner), but NO FJ point has
four doubly-met open corners (0/883; forced four-crowds always need an external along-wall pull), and the surviving
statement is a COUNT: four doubly-met open corners need 8 distinct meeters + >= 4 along-wall holders = 12 > 11.
Gaps: G1 -- at a sigma-minimiser a meeter of a doubly-met open corner is pushed OUT along its wall by the other meeter
and must be held by a square along that wall (measured 639/639, not proved); G2 -- a holder serves at most two meeters
(the sharing bound).  If G1 and G2 hold, the k0 class is impossible for n = 11 by a lemma, and with K0-2 the k-maximal
minimiser has a settled corner: the whole k0_00 obligation (the compute-bound part of the proof) closes.

Ops: short responses, files <= 250 lines, no monitors, no waiting turns; explicit-pathspec commits; never touch the
running workers. Read first: A217's notes and results (the witnesses, the crowd search, Lemma W, C4/C5 statistics,
G1/G2 as stated), docs/proofs/k0_route.md (K0-FREE, K0-BLOCKED, teleport, K0-2), forced_corners.md (Theorem FC),
corner_seal.md (SEAL/WEDGE/NO-SECOND: how a meeter reaches around a corner), descent.md (Lemma CH), drain_lemma.md /
drain_flow_k0.md (the FJ stress, DF-K0), sideband.md (Lemma A1/A2, Theorem B), contact_census.md, A88's census.

## Task
1. STATE Lemma K0-COUNT precisely (any n, then n = 11): at a sigma-minimiser (or an FJ point) of n unit squares in a
   square container with every corner box doubly met and open (no settled corner), the loaded contact structure
   contains 8 distinct corner meeters and at least 4 further distinct squares each holding a meeter along its wall;
   hence n >= 12.  Make every term exact (doubly met = Theorem FC's meeting of the corner cell; "held along its wall"
   = a loaded contact whose force on the meeter has a component along the wall toward the corner; distinctness).
2. PROVE G1: from FJ force balance on a corner meeter (wall force + the other meeter's push + holders = 0) and the
   geometry of two squares both meeting the corner cell from the two walls (corner_seal.md, Lemma A1): show the other
   meeter's contact pushes it away from the corner along its wall, so a third square with an along-wall component
   toward the corner is loaded.  Handle the cases: meeter flush against its wall / tilted (Lemma W); both meeters
   touching each other or not (if not, what holds them?); a meeter that is itself another corner's meeter (adjacent
   corners share a wall -- can one square meet two corners? no: unit square, side > 3; state it).
3. PROVE G2: a holder pushes along the wall toward one corner; it can hold at most the two meeters ... (derive the
   true bound; the along-wall direction is toward a specific corner, and a square touching one wall can push toward
   both ends of it only ... ); or replace by a weaker sharing bound that still gives >= 12.
4. TEST every step numerically on A217's witnesses (the forced four-crowds: which square holds which meeter, along
   which wall) and on the settled optima (where the lemma's hypothesis fails and the count must NOT reach 12).
5. Deliverables: docs/proofs/k0_count.md (the lemma, proofs of G1/G2 or the precise remaining obligation, the n-general
   statement and its n = 11 corollary, what it implies for k0_00 via K0-2, the PI credited for the torque line of
   thought that found it), lean/PackingCertMathlib/PackingCertMathlib/Statements/Open/K0Count.lean (statement as an
   axiom with docstring and pointer, building), registry row, LOG entry, docs/residue_ledger.md section 4, a note in
   writeup/01_summary.md's lever table.  Report once (the lemma, the status of G1 and G2: proved / obligation, what
   closes) and EXIT.
