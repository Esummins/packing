---
name: square-packing-n11-lab
description: "State of the s(11) square-packing lab repo (C:\\Users\\esumm\\code\\packing) â€” new lower bound 3.80 via measure/LP certificates, method ceiling ~3.83, next step case-LP"
metadata: 
  node_type: memory
  type: project
  originSessionId: 8b20e315-017a-445b-9327-302e5359887a
  modified: 2026-08-19T05:54:15.698Z
---

Repo C:\Users\esumm\code\packing is a multi-agent "lab" on s(11) (11 unit squares in the smallest square).
As of 2026-08-18: proven bounds were 3.788854 (Stromquist 2003) â‰¤ s(11) â‰¤ 3.877083590022814 (Trump 1979).
Lab result: **s(11) â‰¥ 3.82** via "measure certificates" (Î¼ = weighted atoms, total < 11, every closed
unit square in [0,s]Â² has mass â‰¥ 1; Theorem 1 in docs/results.md), certs/measure_certificate_3.80/3.81/3.82.json,
verified by two independent exact verifiers (certs/verify_measure.py) and Lean theorems s11_ge_3_80/81/82
(native_decide, lean/PackingCert, targets PackingCertSlow*). Pure-LP ceiling â‰ˆ 3.83 (Ï„*(3.83)=11.000).
Upper-bound checker has an axiom-free kernel proof. Mathlib not installed (disk). A09: angle-lattice MILP
(CP-SAT) finds Trump's packing ab initio in <1 min from Î˜={0,Î¸*} but cannot certify (bound stuck at âˆš11).

**Why:** the user's goal is to close the gap or find an ab-initio method; the repo tracks all attempts
(attempts/REGISTRY.md, LOG.md, docs/ideas.md) so failed ideas are not repeated.
**How to apply:** if resuming, read LOG.md + attempts/REGISTRY.md first; next planned step is I-L6
"case-LP" (LP-based branch and bound with Stromquist-style wall case splits) to pass 3.83, and the
Lean bridge lemmas. Session limits / OAuth expiry killed subagents repeatedly â€” resume them via
SendMessage with pointers to their on-disk partial work.

Update 2026-08-19 (A13/A14): case-LP B&B at 3.84 does not close (fixing corners never kills; 10âµâ€“10â¶ node LPs);
certified lemma: every 11-packing at side â‰¤ 3.84 has a corner-zone square. A11 sweep of open n â‰¤ 100: matches n=11,18,
no beats. Proposed next: I-L9 LovÃ¡sz Ï‘â€² kernel SDP (pilot: discretised Ï‘â€² vs LP at 3.85). Row-oracle bugs fixed in A14.
Update 2026-08-18 (A10/A12): orientation-restricted box LP is tight near Trump's angles but boxes "uprights + tilt in
[20Â°,36Â°]" stay at Ï„ = 11.000 via a 4+4+3 fractional packing (corners 1, side zones 4Ã—Â¼, interior 8 tilted Â¼ + 4 upright Â¼).
A12 showed region-rank cuts (I-L8) cannot kill it: integer loads on all symmetric regions, every macroscopic region
realisable, LP-certified k(R) never violated (lemma), fine combinatorial cuts escaped by sliding. What kills it: conditional
LPs (corners fixed + side zones empty â‡’ Ï„ = 5 < 7) â‡’ next = case-LP I-L6 with fix-a-square (shadow) branches, C1 row oracle.

Update 2026-08-18 (A13/A14, case-LP I-L6 at 3.84): the tree does NOT close. A14 found+fixed three blind spots in the exact
row oracle (A10â†’A13) at hypothesis nodes (cap before hypothesis filter; domain-boundary cells; cap exhaustion) â€” every A10â€“A13
LP value at a hypothesis node is an under-estimate. On-corner boxes are alive (Ï„ â‰ˆ 10.1â€“10.2, budget 10); one corner fixed
exactly: Ï„ = 10.000 with dual coverage 1.000; four corners: 7.000 (Â¼-structure) â‡’ corner refinement never kills; only empty
side zones kill (4 corners + NO side0: 6.36; root + NO all sides: 8.28). Certified leaves (exact verifier PASS): every packing
at side â‰¤ 3.84 has a square centred in a corner zone [0.5,1.1]Â²; no square in [0.8,1.1]Â²Ã—[60Â°,90Â°]. Closing needs 10âµâ€“10â¶ LPs
â‡’ case-LP campaign stopped. Certification margins (3e-3 shrink + 3%) cost 0.1â€“0.25 per node.

Update 2026-08-19 (A15, Ï‘â€² pilot, attempts/A15-theta-pilot): on one discretised placement graph (Nâ‰ˆ2200â€“3750, A12 Â¼-structure
injected) Ï‘â€² â‰ˆ 10.38 (3.84) / 10.43â€“10.48 (3.85, also mid-tilt graph, also refined grid) / [10.45,10.64] (3.87) vs LP 11.000 vs Î± 10;
â‰ˆ half the LP gap removed, gap stable under refinement. Machinery: D4 block-diagonalised SDP in SCS with dual-certificate
brackets (SCS needs â‰³3e4 iterations at Nâ‰ˆ2200; tight values from ~500-node support sub-SDPs). Verdict: continuous kernel
certificate (I-L9) worth building, kernel class must include LP coverage-indicator features (the LP certificate IS such a kernel).
Next: Ï‘â€² on an un-seeded fine grid; Ï‘â€² as node relaxation in the case tree (4 corners fixed: LP = 7 = budget).

Update 2026-08-19 (A16, attempts/A16-theta-casetree): Ï‘â€² kills every node type that stalls the LP case tree, on the same
grids where LP = budget exactly â€” N2 (4 corners fixed): Ï‘â€² â‰¤ 6.6 vs budget 7; N1: â‰¤ 9.44 vs 10; A14's alive boxes: slack
âˆ’0.24â€¦âˆ’0.48; N4 integral. Universal pattern Î± = budgetâˆ’1, LP = budget, Ï‘â€² â‰ˆ Î±+0.4â€“0.6 â‡’ tree = ~14 nodes, maybe 1.
Next running: A17-kernel-root = continuum Ï‘â€² kernel at the root (LP-atom indicator features + smooth D4 terms, cutting
planes, float phase; target Î» < 11 at 3.84), then A18 = exact/rational phase + Lean. Dual certificates are cheap (SCS
res_dual 1e-8 at ~2k iterations) even when primals are useless.

Update 2026-08-19 (A17, attempts/A17-kernel-root, done-negative on the Î»<11 target, float phase): the 1181-atom
normalised-indicator kernel class (Ï† = (1, 1[pâˆˆQ]/m(x)), A07's 3.84 LP atoms) does NOT reach Î» < 11 at 3.84 â€” cutting-plane
loop stalls at Î»_sdp â‰ˆ 11.05â€“11.13 (rows are valid â‡’ class optimum â‰ˆ 11.0â€“11.2), diagonal LP-shaped (corr 0.99 with Ï„/m(x),
binding = continuum of coverage-1 cells), pair oracle finds a non-converging stream of interior mid-tilt (29â€“68Â°) violations
(K â‰ˆ âˆ’0.7â€¦âˆ’0.86 vs âˆ’1). Class penalty vs discrete Ï‘â€² (10.38) â‰ˆ +0.7 â‡’ A16 risk R2 (feature class) binds before R1. Kernel
beats LP-form by 1.25 on same atoms. Calibration at 3.80 PASS (pair = âˆ’1 exactly, min cov 1.0297 vs advisor 1.0300).
TWO STRUCTURAL DISCOVERIES: (1) condition (ii) is needed only for disjoint CLOSED squares (touching pairs EXEMPT and must be:
shared boundary atoms force K > âˆ’1); (2) the subclass M = LP-form + C, C â‰¤ 0 off-diag, satisfies (ii) UNIVERSALLY by algebra
(disjoint closed squares share no atom) â‡’ NO 6-D pair verification at all; on the A15 c384 graph dropping the 20% of edges
that share no atom leaves Î± = 10 â‡’ recommended A18 = restricted class + atoms inside mid-tilt sliver-overlap regions +
smooth features interpolating the discrete duals' ~40 dominant eigenvectors. Solver note: sparse-conic SCS impossible
(patterns dense, 71â€“277 atoms/square); per-block Burerâ€“Monteiro + L-BFGS hingeÂ² works (validated vs Clarabel).

Update 2026-08-19 (A18, attempts/A18-restricted-kernel, done-negative with THEOREM): the restricted (automatic-(ii))
kernel class COLLAPSES TO THE LP â€” proved, not just measured. With Ï† = (1, a/m(x)) and border = normalisation weights,
K(x,x) = aáµ€Sa/mÂ² where S = D âˆ’ wwáµ€ is a PSD Z-matrix with margin (S_pq â‰¤ âˆ’w_pw_q); M-matrix/dominance theory â‡’ the class
optimum has C â‰¡ 0 (two-measure LP-form kernel K_u = (Î£w_qu_q)(Î£_{pâˆˆx}w_p/u_p)/mÂ² âˆ’ 1) and Cauchyâ€“Schwarz gives
Î» â‰¥ Î£Î½/inf Î½(x) â‰¥ Ï„*(s) for Î½ = wâˆ˜u. So Î» < 11 at 3.84 impossible (Ï„*(3.84) = 11.02); pair-free kernel ceiling = LP
ceiling â‰ˆ 3.83; ALL no-pair-verification variants blocked (Ïƒ<1, free border/normalisation with Ïâ‰¥1, wall-atom caps â€”
the last only if atoms sit exactly on âˆ‚ container, none do). Everything the full kernel gains over the LP lives in
POSITIVE off-diag entries on overlapping non-sharing mid-tilt pairs. Machine-validated: SDP == two-measure GP to 4e-5
(96 atoms; u_Îµ = (S*+ÎµI)â»Â¹1 realises the collapse constructively); float runs: Î»(u=1)â†’Î»(u*) = 10.618â†’10.506 (3.80),
10.749â†’10.725 (3.82), 11.376â†’11.179 (3.84), all â‰¥ Ï„* as forced. By-product: LP-form kernels have a one-vector rational
PSD certificate (M Z-matrix, M(W,u)áµ€ = 0 â€” no LDLáµ€). Binding cells at 3.80/3.82 are admissible-boundary WALL cells
(coverage 1.017/1.022 â€” every prior float min-coverage number was an attack under-estimate). Recommended A19: HYBRID
kernel â€” Z-sign globally, D_pq > 0 only for atom pairs in the mid-tilt sliver region, 6-D cell-pair verification
restricted to pairs of squares both meeting that region (orders of magnitude smaller than A17's full pair space).
Convex machinery: fixed-w class optimum = geometric program in log u (softmax + L-BFGS, per D4 orbit valid only on
canon-deduped/D4-closed row sets).

Update 2026-08-19 (A17â€“A20, kernel programme CONCLUDED negative): indicator kernel stalls ~11.0â€“11.2 at 3.84 (A17);
collapse theorem: automatic-pair classes â‰¥ Ï„* (A18); Ï„*(3.84) â‰¥ 11 PROVED exactly (A19 lp_floor_384.json, exact B&B);
hybrid/localised classes buy â‰¤0.06 and re-pin from the 6-D pair continuum even at k=480 D4-blocks with verified convex
solves (A20; also found+fixed a silent Clarabel stall in A19's h380). R1 (gridâ†’continuum) is real. Untested: smooth
features that change the pair oracle (piecewise-smooth pair bounds). Certified bounds stand: 3.82 â‰¤ s(11) â‰¤ 3.877084.

Update 2026-08-19 (A22, attempts/A22-local-rigidity, commit 96eb0b7): STRICT LOCAL OPTIMALITY OF TRUMP'S PACKING
CERTIFIED (first ever, 46-yr open): in the box ||zâˆ’z0||âˆž â‰¤ 5e-4 (34 coords) the contact system has a unique solution
(Krawczyk, enclosure 1e-50), it is feasible, every feasible config in N has s â‰¥ Å with equality iff Trump; stability
s â‰¤ Å+Î´ â‡’ ||zâˆ’áº‘|| â‰¤ 155.7Î´. Min multiplier 0.0175 (strict complementarity after drop-set; one pinwheel self-stress),
min inactive margin 0.019. All-rational certificate + standalone recheck.py (mpmath.iv+fractions, 8 checks PASS,
corruption gates FAIL). Remaining: mpmath.iv trust, symbolic octic identification, relabelling reduction, Lean port.
Optimality now = global half only (exclude packings outside N at s â‰¤ Å).

Update 2026-08-19/20 (A23 wastage oracle, commit fdd28cb â€” PI's idea VINDICATED): sound dead-region certifier
(witness-point overlap test â€” SAT-projection test rejected as unsound; float-guarded + pure-Fraction modes; PlacedBox
= core-box-uniform certificates composing with verify_case). Ledger bites in the mid-tilt band: adjacent 33Â° pinwheel
pair strands 1.88 (48% of budget) at depth 2; full 4-cycle strands 6.55 > budget (killed depth 4); EXACT THEOREM at s':
the scaled 4-cycle has dead area 2816/625 = 4.5056 > s'Â²âˆ’11 = 4.0318 (176 cells, pure Fractions) â‡’ no 11-packing at s'
contains it. Single squares strand â‰¤ 0.6 (not a root killer); corner squares strand 0. Next: composed pilot on A14
node-3 pinwheel children, NO-zone discharge, PlacedBox sweeps (~1 CPU-day/corner box).
Also A21 (partial, still writing): certified at 3.88 â€” corner occupancy (10.561 < 11) and side-zone occupancy;
per-corner version NOT certifiable at 3.88; generic-tilt window blocked.

Update 2026-08-20 (A21 consolidated by advisor after spend-limit kill; commit 1357396): CERTIFIED at 3.88 â€” THM1
corner occupancy (10.5611<11) and THM2 side-zone occupancy (8.7453, margin 2.25); NOT certifiable: per-corner
(LP~10.7 above ceiling), per-side (FAIL 10.937), orientation windows (alive via ~43Â° near-packings / Trump itself).
ROADMAP COMPLETE: local optimality certified (A22), structure at 3.88 (A21), wastage killer for mid-tilt (A23,
exact kill at s'). Open: the global stage (exclude packings outside the A22 box at s â‰¤ s'); next experiment =
composed killer (coverage LP + wastage) on A14 node-3 pinwheel children. docs/results.md has the full programme.

Update 2026-08-20 (A25 wastage atlas, commit 6676916): continuum dead-area atlas built (query.py: D4-aware lookup over
(centre-box, tilt-box) -> certified rational lower bound + disjoint_regions() for the budget lemma). MIN k = 3: three
mid-tilt squares in [1.275,1.35]^2 x [15,20] deg + its 90-deg rotations strand 4.7930 > budget 3.7456 at 3.84, and
4.2070 > 4.0318 AT s' (exact Fractions). k=2 impossible (best 3.1953). Cost 2.9 s/cell (A23 exhaustive was ~1 CPU-day,
~2000x). CRITICAL: certified value is a THRESHOLD in centre-box size (point 1.74 / 0.15-box 0.32 / 0.075-box 1.49) â€”
branch centres to 0.075 before querying; tilt width nearly free. Strongest single-square wastage = square ~1.2 from a
CORNER (L-moat 1.40-1.60), not flush-to-wall. Coverage 35-43% of mid-tilt cells >= 0.3, deep interior genuinely 0.
Corrections: D4 fundamental domain = QUADRANT x theta<=45 (not octant); pair cells need realisability flag (54/330 not
realisable). Atlas is s-independent on [3.84,3.88]. A24 (composed tree at 3.84, LP + wastage kills) still running.

Update 2026-08-20 (A24 composed tree, commits f64d8ae/fc6d425): s(11) >= 3.84 NOT certified; record stays 3.82.
T1/T2 split: 30 kills ALL by coverage LP, wastage fired at ZERO tree nodes â€” it needs >=3 cores of centre half-width
<=0.075 (cliff to 0 at 0.10) and T1 already wins by that depth. NEW CERTIFIED: A24.1 every 11-packing at side <= 3.84
has a square centred in [11/10,137/50]^2 (margin 2.76, largest at 3.84); A24.W the 4-core pinwheel node killed BOTH by
area (2416/625 > 2341/625) and by coverage (103/25 < 7) â€” first doubly-killed node. Interior-first branching beats
A14's wall-first (interior core half-side >=0.35 gives slack -0.7..-2.0). Root + one exhaustive D4 level: 26 converged
deaths, 15/15 attempted leaves certified, 3 alive; closing 3.84 estimated 100-300 CPU-hours (vs A14's 10^4-10^5).
Open frontier = those 3 alive boxes.

Update 2026-08-20 (A26 wall-strip ledger, commits b6c0c8d/ddee7f4 â€” PI's propagation idea, done-negative + 3 theorems):
COUNTING WORKS: Lemma B0 (band-avoiders are a packing one level down: m(w) = max{n : s(n) <= s-2w}); THM A26.1 if
(2B-1)^2 < 8 then <=1 square fits in side B, so >=10 of 11 squares meet the width-1 band at 3.84 AND at s' (holds for
all s < 3.9142); THM A26.2 >=7 squares have centre within 1.34711 of a wall. CHARGING CANNOT: the functional has an
EXACT ZERO (flush near-upright wall square strands 0 â€” 6 of Trump's 11 are exactly that), min total charge 0.0000 vs
budget 3.7456. TILT FORCING HAS A HARD CEILING: 10 squares with tilts <= 23.36 deg fit in 3.84 (advisor re-verified:
margins +2.3e-4 / +9.0e-5), so at most ~1-2 squares can ever be forced mid-tilt vs the ~7 needed. THM A26.3: A19's
value-11 fractional packing satisfies every band/tilt/zone rank cut => tau_cut(3.84) >= 11, closing the I-L8 line;
general principle: LP-certified rank bounds can never be violated by a feasible fractional packing, only combinatorial
bounds strictly below tau_B can cut. Next cheap items: free tree pruning via A26.1; Lean-formalise B0+A26.1 (~1 CPU-h);
only surviving charging direction is CORNER occupancy at depth ~1.2 (3 squares there exceed budget).

Update 2026-08-21: A28 (Opus) formalised the UB REAL-PLANE THEOREM in Lean+Mathlib: eleven_unit_squares_in_3877084
(exists 11 disjoint unit squares in [0,3.877084]^2 as sets in R^2; axioms propext/choice/Quot.sound only, underlying
checker kernel-checked axiom-free) â€” s(11) <= 3.877084 is now a machine-checked statement about R^2. Mathlib install
~10GB, torn down after (11GB free; rebuild = one `lake exe cache get`). A26.1 formalised in weakened form; left open
inequality A28.â˜…, which the advisor PROVED by hand (docs/proofs/a28star.md: two branches, both collapse to
(1-sin)(1-cos) >= 0) â‡’ SHARP band lemma: â‰¤1 square avoids the width-w band for any w > (s-2)/2, all s < 4.
A22 Krawczyk Lean replay blocked on cert being angle- not t-parametrised (fix: re-emit in t, then 1-2 day port).
A27 (close 3.84 tree) still running. I-L11 (critical-point/flow reduction) recorded; drain+stress lemmas = advisor lane.

Update 2026-08-22 (A27 done, commit e0ba5d6): 3.84 tree NOT yet closed but 123/216 level-1 cells discharged with exact
certs (verify_tree2.py: 0 failures); THE 3 LIVE BOXES ARE CERTIFIED DEAD (95/101 at one refinement; 89 at two â€” its
children 89_010/89_111 are provably LP-unkillable at their size, Ï„=10.000 maxcov=1.000, but all 24 grandchildren
certify; 84 = Ïƒ(89) via 29 machine-checked rational symmetry transfers). SOUNDNESS GAP in A24's verify_tree found+fixed:
the core-containment bridge was float â€” verify_tree2 does it in exact rational intervals, tree re-parametrised by
t=tan(Î¸/2) (Ï€-free), Ïƒ(t)=(1âˆ’t)/(1+t). New rigorous class alive(LP) (Ï„_LP â‰¥ budget, column oracle exhausted â‡’ only
refinement kills). A26/A28.â˜… pre-filter provably inert on 1-core trees. Cost to finish ~340 CPU-h, no new math;
A29-finish-384 (Opus) dispatched with refine-alive-first + warm-start-cert speedups.

Update 2026-08-26 (PIVOT: A29 paused, T3 is the critical path): PI asked whether finishing 3.84 was
necessary for the endgame (s(11) = s*); advisor answer NO (a container-side LB prunes no configuration
cells of the exclusion program) and PI decided: **A29 PAUSED as fallback** (179 verified certs on disk,
74 open level-1 cells; resume `python finish.py` in attempts/A29-finish-384 at â‰¤6 workers â€” 9 workers
OOM-crashed the machine). A29 had two bugs, both fixed (fb9272a): no-FAIL-marker (restart re-ran 32
deterministic failures; now param-stamped leaf_<n>.attempt.json markers) and provisional-certificate
counting (leaf json written before verification; 6 unverified files wrongly skipped â€” soundness-relevant).
**drain_lemma.md v2**: D3 (KKT+CQ, taxonomy TODO) replaced by D3â€² (Fritz John per smooth selection â€”
containment needs no selection; selected separation + dominance rows give S-feasible â‡’ disjoint and
menu completeness; ties covered by multiple selections). FJ needs no constraint qualification â‡’
degenerate taxonomy DISCHARGED; only residue is Î»â‚€=0 branch (cost, not soundness). T3 sound on
D1+D2+D3â€². **A30-t3-pilot dispatched** (Opus): P1 reproduce A22 root isolation, P2 offset-cell
exclusion, P3 generic-cell menu size + per-selection Krawczyk cost + full-cover extrapolation at s*.
docs/plain_language_guide.md written for the PI (explains everything in mech-E terms).

Update 2026-08-26 (A30+A31 pilots, both decisive negatives with validated machinery): A30 killed
T3-as-coordinate-cover (discharge ratio câ‰ˆ1.86 scale-invariant â‡’ c^33â‰ˆ8e8 cell shell around every
critical point; floor 1e5-5e7 CPU-h) but validated the FJ engine (isolates Trump at hâ‰¤2.4e-4, 0.2s;
Gordan/Farkas test = exact first-order test, 2ms/selection) and found 3 blocking errors in drain_lemma
v2 (fixed in v3: FJ sign, D2 vacuousâ†’centroid-shrink repair, separation row). A31 killed naive
enumerate-then-solve over contact structures (4e29-3e30 projected at k=11; non-thin graphs ~17^k;
all factorial growth in the L2 degree-2 thin branch) but validated the filters (metric x50,
planarity x3.3, L6; tilt propagation kills 79-98%, rotation-system 91% more). structure_lemmas.md
L1-L7 proved (L6 = stress lemma core in 3 lines: wall-to-wall loaded chain via component force
balance). Free lemma: â‰¤3 squares/wall (tight at Trump 3/3/3/2). Flush contacts mandatory for
rigidity (planarity caps |E|â‰¤3k+2 < Maxwell 3k+1 without 2-row flush edges). CURRENT DESIGN: the
endgame campaign = branch-and-bound over PARTIAL structures (subgraph-closed kills, metric/LP/
Farkas/FJ at partial nodes, contact type algebraic in the per-graph solve); go/no-go = frontier
size, unmeasured (candidate pilot A32). A29 (3.84) still paused as fallback, machine idle.

Update 2026-08-26 (A32 NO-GO â€” the wall is mapped from all three sides): structure-B&B frontier >=
leaves (all-monotone kills => every survivor is a visited leaf); frontier ratios linear in k =>
5.6e12-1.4e14 graph nodes / ~1e30 decorated leaves at k=11; B&B only 2.7x better than A31 flat and
3x slower in wall clock; Farkas/case-LP/FJ fire ZERO times at structure level (contacts fixed but
selection rows not => FJ ill-posed above decoration layer); L2 strut-DFS kills 43% of thin graphs
(the one crack). VERDICT across A30/A31/A32: any complete search over the current lemma set's
survivors is dead by 7-24 orders; endgame s(11)=s* needs family-kill mathematics (space-collapsing
theorem), not better search. Advisor recommendation pending PI: resume A29 (3.84 = main line, ~2
days), advisor works L2 hard-closure + family-kill ideas, consider consolidating corpus for
write-up. All pilots' engines validated and banked; ~minutes of compute each.

Update 2026-08-27 (A33+A34 closed â€” endgame survey complete, new records banked): A34 sparse-SOS
NO-GO with COLLAPSE THEOREM (advisor-verified): any sparse relaxation with cliques of â‰¤ m < n
squares caps at s(m) forever (injective-assignment exchangeability); even 10-cliques cap below
Stromquist; full-clique level 3 = 16215-block unreachable; trust chain validated (exact rational
SOS cert for s(2), independent checker PASS). A33: equality-pigeonhole Lemma A33.1 formalized;
eta(s) gate [0.19,0.43] at s-hat, ~0.05 float at 3.84 (certified 0.3229, tangency cluster blocks
tighter); single-square variety pinning weak (one blob, wall bands), multi-field stacking dead
(shared tight set), THE WIN = k-subset TIGHT-SUM CUTS (51% of disjoint pairs violate pair budget)
deployable in the A29 tree; PI's grain conjecture REFUTED in measured range (eta RISES with n;
n=11 = method's best non-trivial case; eta(m^2)=0 exact; eta=0 iff LP settles s(n)); NEW CERTIFIED
THEOREMS s(12) >= 3.877084 and s(12) >= 39/10 = 3.90 (published record was 3.7889); tau*=12 crossing
~3.95-3.97 = 99% of n=12 record 4.0 => n=12 campaign may nearly close s(12)=4 â€” natural sequel.
Five endgame approaches now measured dead-or-weak at s-hat (cover, enumeration, structure-B&B,
sparse SOS, variety pinning). Live equity: tight-sum cuts at 3.84-3.85, the n=12 target, corpus
write-up. A29 still PAUSED (resume needs PI word; 6 workers max).

Update 2026-08-27 (A35 closed â€” PI's escape-complex idea: GO as tool, NO-GO as basin closer): I-L15
(semantic contact-change cells, not metric balls) VALIDATED â€” Trump's jam neighbourhood covered by
~10^2 IV-certified certificates in minutes (vs A30's 8e8-cell shell / 1e5+ CPU-h: that assassin is
DEAD). Jam has zero escape routes (all break sets empty/load-refuted/wedged; universal stratum-
independent certificate covers all 2^42 break sets, 0 true survivors, 553 s). Found+repaired: A22
basis missed the exact (1,3) corner-corner contact + used dist surrogates for two flush pairs
(A22's theorem survives); multiple enumeration/soundness bugs caught by independent checkers.
Composed v2 theorem reaches only 0.25 r_N (currently subsumed by A22 in reach; levers L1
endpoint-row lemma + L2 omega-scale; per-stratum form reaches 1.6-3.1 r_N). Assassins: semantic
cliff R* ~ 0.006 (method's language expires at the basin boundary); global far-field wall
untouched. Steady-state ~10-30 min per critical point; all 36 A04 optima ~ 1 desktop-day. Flush
contacts = the recurring villain (A30 union-Farkas, A31 mandatory-flush, A35 first-order blindness).
Endgame arithmetic after A35: per-CP factor removed; remaining walls = far field (LP ceiling 3.83,
1e30 structures) + cliff handoff. PENDING PI DECISIONS: resume A29 (3.84, ~2 days, 6 workers),
n=12 campaign (may fully close s(12)=4), corpus write-up.

Update 2026-08-27 (A36 closed â€” DOMINANCE): composed escape-complex theorem now STRICTLY DOMINATES
A22: sigma >= s-hat with equality iff z-hat on box(z-hat, 3.7e-3) [certified max 3.779e-3 = 7.56
r_N, ~10^29x A22's volume], stratum-blind, both FJ branches, 17 IV certs + corruption-gated
re-checker, 12 min compute. Decisive lever = max-form pinning (kappa_eff 19.3 vs 784, x11.4),
discovered not ordered; L1 over-estimate lemma (+2.4%) discharges the endpoint caveat. Next
ceilings: A22 old-row tangential margins 5.2e-3, semantic cliff ~0.006, then far field (untouched).
A35+A36 = the methods centerpiece for the write-up. PENDING PI: resume A29 (3.84), n=12 campaign,
write-up.

Update 2026-08-27 (A37 closed â€” certified CP atlas): 32 A04 families below 3.95 = 10 real attractor
structures: Trump (only rigid CP) + 9 valleys ({1~2}, 6, {13~14}, 27 marginal, 31, A37-NEW-0..3 at
3.9027-3.9255 â€” four attractors A04 MISSED, found by draining its fixed-angle artifacts; catalog
provably incomplete => BDBFS discovery loop is load-bearing). 24 NOT-CP entries constructively
refuted (explicit smaller-s packings). atlas_final.json: 36 entries, each a certified discharge box
sigma >= V >= 3.877084 within h (3.76e-3..6e-2); 37 certs, 2018 checks, gates bite; generic
pipeline reproduces A22+A36 (trust-chain regression). <2 desktop-hours. NEXT: A38 root-power pilot
at s-hat (last unmeasured factor: conditioned LP-tree + tight-sum cuts + wastage + atlas discharge
=> does the far field close at desktop node counts?). Also still pending: A29 resume, n=12, write-up.

Update 2026-08-28 (A38 closed â€” far-field NO-GO; endgame parked at a mapped frontier): assassin =
per-node LP DECISION COST at s0 (cost wall, not geometry): the identical rule that decides 3.84
nodes in 150-500s decided 0/60 depth-2/3 nodes at s-hat (eta 0.24 vs 0.046 => 5x richer near-tight
placement family for the oracle); b_eff 8.00 flat; weapons silent until depth 5-7; floor 70-700
desktop-days OPEN-ENDED ABOVE. All 4 pre-registered GO criteria fail. BANKED: Theorem A38.1
(certified: every 11-packing at side <= 3.877084 has an interior-zone square, margin 0.9994); T0
composed soundness statement (8 seams; S1 = unpriced full-pinning cascade); trust-chain finding
(2/8 float kills at s0 evaporate under exact certification â€” 3.84 results NOT contaminated, every
3.84 leaf was individually certified; NEW LAB RULE: certification-in-the-loop, float = measurement
only); the 5 alive(LP) cells sit at tau/maxcov = 10.000000/1.000000 EXACTLY (the 1/4-ghost equality
manifold = the true-wall geography). REOPENING LEVERS: L1 reseal s-hat field (~5x on W1, ~2 depths
= 64x frontier), L2 decide-without-full-convergence (witness-feedback at solve time), L3 warm
starts; cheapest datum = one 3600s calibration node (G7). CONSEQUENCE: s(11) = s-hat NOT currently
composable (D1 + atlas + A36 stand; far field does not). Unaffected: A29 3.84 fallback (still
paused, resume 6 workers), n=12 campaign (ceiling 99.2%), corpus write-up (arc complete: 2 records,
local optimality, A35-A37 methods, 6 quantified walls).

Update 2026-08-28 (A39/A40/A41 all closed â€” the vice measured from both jaws): A40 grew Trump's
certified basin to h = 6.55e-3 (1.77x A36, past the cliff; 2930 certs verified; saturates at a
certificate-cost wall, rate exactly 1/kappa_eff; ceiling ~0.02 via G-A40-2/3 recentred anchors).
A39: early certification adopted at LEVEL 1 (exact cert costs 0.6-16 s there â€” A38's 2/8 failure
finding REFUTED, artifact of certify.py pre-resolve; f1 = 0.351, b_eff 5.19, G1 debt closed 38/38)
but DEPTH-2 WALL IS REAL: witness feedback raises tau into budget (median +0.115) closing cert
headroom, and depth-2 cores exempt 8x less â€” 1/49 decided; reseal capped at eta >= 0.335 (got
0.403), W1 first-kill depth 5 unchanged (A38's 64x lever estimate wrong). A41 seam design:
N1 zone-assignment collapse (16^10 -> 10 additive certs, LOW difficulty), parametrized cost formula
(dominant = refinement-window term), N6 ghost-manifold discharge = HARD/OPEN residual wall.
COMPOSED STATE: the deep-core LP family is dead at depth >= 2 (mechanism understood), but A41's
cascade uses OCCUPANCY-type certificates (A38's root: 1.7 s at s0) â€” the one unmeasured family.
Decisive next measurement if pursued: A42 = price occupancy-chain certificates at s0 (k = 1..3)
under A39's cheap-cert rule + prove N1. Also open: N6 (candidate idea: two-field simultaneous
budgets vs the equality manifold). PI decision pending: A42 vs 3.84 resume vs n=12 vs write-up.

Update 2026-08-28 (A42 closed â€” the s-hat far-field survey is COMPLETE, A30-A42): the occupancy
cascade does not exist as a certificate route: tau = budget INTEGER-EXACT at every conditioning
(k=1..10), every radius (d-tau/d-rho' = 0 identically), every zone size (w=0.35 = 34x volume: still
tau = 11.000000; medium cores ANTI-economical, -0.855 net), both tightening schedules (budget-1
identity F1; mid-chain zero). The 1/4-ghost saturates every conditional budget at s0 exactly â€” N6
(ghost equality manifold) is the GENERIC far-field mode, not five corner cells. F4 shield: any
nofam-blind weapon can never force occupancy (Trump realizes the rest of the hypothesis). BANKED:
Lemma N1 PROVED (centers >= 1 apart => diameter-<1 zones hold <=1 center; assignment collapse;
docs/proofs/occupancy_collapse.md), free verifier-only assignment step (11 balls, 38 s, no LP),
root Theorem A38.1, ghost-mass conjecture (occupancy power = ghost mass displaced, not volume;
profiling = cheap diagnostic, unrun). VERDICT: s(11) = s-hat requires an N6-class weapon vs the
ghost's equality manifold (candidates: two-field budgets [A33 shared-support caveat], nofam-aware
FJ/Farkas, theta'-rows [A17-A20 caveat]) â€” no known family works, each closed by an exact
mechanism. Actionable now: A29 resume (3.84), n=12 campaign, corpus write-up.

Update 2026-08-28 (A43 closed): PI's bulk-kill thesis measured NEGATIVE at both levels â€” graph
census: full 2026 library worth ~x2 (N1 the only hard prune; existential theorems vacuous below
k=11; positional filters get m_low = 0 on position-free objects; flush-mandatory NOT certified,
worth x1e4 IF proved; motif filters unsound â€” Trump's graph has a 4-cycle); spine census: LARGE
(~2.1e6 types at k=11, <0.4% cut at k>=4 â€” spine types forget y, wastage floor exactly 0).
THE LAW (third face of finding/refuting asymmetry): ENUMERATION-CERTIFICATE MISMATCH â€” our
certificates price placements; every object cheap enough to enumerate quotients placement away.
Double-spine lever: NO-GO on paper (crossing lemma pins 1-2 squares, x1e3 cost for x1.1-2 cut).
Banked: k=3 spine structure theorem at s-hat (all 3-chains corner-ended, tilt forced [18,72]);
wall-flush slab cut (1.8% positional); A31 counts regression-verified. RANKED OPEN LEVERS:
(1) FJ-specific Maxwell row bound (prove flush-mandatory for critical structures => x1e4 census);
(2) I-L13 INTERFACE CHARGING â€” the only certificate family whose unit of account (contacts/edges)
matches the enumerated object; per-contact-type certified wastage from atlas data would give a
graph-summable bulk filter. Endgame survey now spans A30-A43. Pending PI: pursue levers vs A29
resume vs n=12 vs write-up.

Update 2026-08-29 (A44+A45 closed â€” both census levers resolved): A44: FJ-Maxwell REFUTED
unconditionally (family 31 valley: m = 3k, all squares loaded; support-level bounds die even at
Trump); rigid-branch bound + index identity (m = 3k+1+sigma-d) + lambda0=0-needs-self-stress
PROVED; C* (m >= 3k) survives atlas, tight at 27/31, but PROVEN unreachable by FJ+counting
(curvature-blocked valleys) â€” conjecture only, x354 if ever proved; flex branch = 99.94% of census.
A45: charging lemma PROVED + fully exact table, but INERT at n=11 as a THEOREM (Ceiling 2: charge
<= rho_min^2 x (3k+2) contacts = 2.19 < budget 4.03 â€” can never fire; Ceiling 1: no ownership
scheme beats it, plane-dead pair area ~0.05/contact caps everything). FOURTH FACE of the mismatch
law: interfaces pin relative coordinates; relative-coordinate certificates price only sliver
wastage; the budget lives in the far field. Bite ~ pinned coordinates, again. LIVE GAINS: PI's
Lemma R (ruler cap, Trump 5-strip extremal, margin 0.4636) + Lemma Q (quantization kill) proved +
census-measured (x1.09 at L1, odd-cycle parity mechanism); k>=10 zero-charge class DEAD exactly
(tilt propagation + A26 2.503-degree cap); Ceiling 2 = permanent screening test for per-contact
certificate proposals. Open small computation: sharp m(theta) B&B (closes zero-charge Z1).
The census axis is now exhaustively priced (A43-A45). Standing: A29 resume, n=12, write-up.

Update 2026-08-29 (A46 closed â€” balanced-wedge flush-mandatory route dead, twice): W1 refuted by
THEORY (bridge mechanism: loaded corner contact balanced at EVERY mismatch delta > 0, rational-
exact to 0.057 deg) and by MEASUREMENT (genuine CPs carry loaded CE rows at 1.03/2.27/7.1 deg â€” the
near-flush end is INHABITED); W2: even fantasy delta_0 = 45 falls x2-6.9 short, CE-only interiors
capped at 0.699*B0 table-independently. FIFTH face of the mismatch law: balance pins angles but the
COUNT is short. Flush-mandatory stays an atlas-consistent conjecture (F >= 3 empirically) with
FOUR closed proof routes (counting/charging/wedge-budget/stratum-limit). BANKED: Theorem W1.6
(flush-free thin chains quantize to exactly 45/0 tilts; flush-free 3-chains impossible at s0 â€”
2sqrt2+1 < s0 exact; minimal flush-free structure = explicit [45,0,0,45]); the w_WC table (280x
A45's charges, Trump capture 12% â€” strongest certified charge table in the lab; A45's cost was the
moat, not the geometry); torque-dichotomy toolkit; CC sharp-free-wedge convention (19x). I-L18
recorded NOT pursued: multi-square corner hypotheses (A23-4b 0.34-0.54, 2.4x single wedge).
THEORY SPRINT COMPLETE (A30-A46): every known route priced or refuted with exact mechanisms.
Standing deliverables: A29 resume (s(11) >= 3.84), n=12 campaign, corpus write-up.

Update 2026-08-29 (A47 closed, done-mixed â€” first positive theorem about unknown CPs): **THEOREM
(thin branch)**: flush-free thin load chains span exactly o*sqrt2 + r (diamonds exactly 45, uprights
exactly 0; dismissal lemmas close mixed cases); unique window value s* = 2sqrt2+1 = 3.82843, and
its [45,0,45] structure admits NO 11-packing completion (new certificate class: obstacle-aware A08
coverage at rational relaxation, 50/50 boxes, exact coverage audit, independently re-verified) =>
no flush-free critical structure at any s in [3.82, s-hat] contains a thin chain, NO exceptions.
Also banked: 54-entry exact corner primitive table (max 0.8523 = 4x best wall wedge; feasibility
law: tilt > 40 deg infeasible within 0.7 of a wall); near-flush corner cell = exact 0 (Trump-
confirmed). Composition: packing-level FORCED sum exactly 0 (epsilon-parking evasion), grant-all
x1.35-2.27 short â€” SIXTH face, PI-SCOPED: kills only the packing-level statement, which never used
criticality; the parking witness drains. **I-L19 = the open route (PI formulation): bridge-cascade
descent â€” flush-free all-near-flush balance needs bridge structures whose blocker-slope/loaded-
blocker-recursion/wall-lever (1/sin d) requirements may be globally self-defeating.** A44's closure
was order-conditions only; budgets never used criticality; I-L19 untouched by all six faces.

Update 2026-08-29 (A48 closed â€” I-L19 cascade local theory settled, composition provably does not
follow): R1 PROVED corrected (blocker SUPPORT-EDGE slope escalates strictly, g > d iff loaded;
naive contact-mismatch monotonicity FALSE); R2 PROVED (menu complete, no cycling via height
functional <= 9 composite steps, C4: flush-free branches universally NON-THIN with A47 T1);
R3 REFUTED exact (wall-lever 1/sin collapse was an axis-parallel-frame artifact â€” lever arm is
sin(absolute tilt); bounded-multiplier single-presser balance at u = sin^2 d exists; salvage =
O(d^2) PRESSER-CONFINEMENT LEMMA, first criticality-derived position-forcing fact); R4 NO-GO a
priori (C6': grant-all ceiling of ALL certified tables = 0.9416*B0 < B0 â€” screening theorem for
every future criticality-aware charging proposal). NAMED GAP A48-G1: flush-free structures can
route all rotational demand through B1 overhang-press chains + confined pressers, never forced
mid-tilt â€” only GLOBAL REALIZABILITY at s <= s0 can kill it. I-L19 downgraded to a global-
realizability conjecture. DECISIVE NEXT EXPERIMENT (named, cheap): drain-style numerical hunt for
a flush-free critical point seeded on the two evasion branches â€” finds one (= discovery) or adds
evidence + basin data. Banked case-tree teeth: escalation rows as node LP inequalities, near-CC
confinement split, universal non-thinness, C6' screener. Atlas pencil branch = flush artifact
(none below 22.4 deg).

Update 2026-08-31 (A49 closed by advisor after lead hit usage limit; PI PAPER VISION recorded):
A49 OUTCOME B â€” 252/252 evasion drains acquire flush, 0 candidates, 72/72 stratum minimisers
blocked-by-flush-boundary (0/324 interior), evasion breaks at CHAIN WALL TERMINATIONS never the
presser (banked map = the formalization target); I-L19 = strongly corroborated global-realizability
conjecture; mid-tilt non-thin flush-free basins unsampled; a37_drain.repair lam_hi bug fixed.
**PI PAPER VISION (standing directive): write the paper only WHEN a full optimality proof of s(11)
exists.** The paper must include: (1) appendices for EVERY off-critical-path investigation
(negative results as first-class publishable output â€” requires knowing what ended up on the
critical path); (2) a methods section on the human+Fable+Opus complementary division of labour;
(3) a checking/validation/human-simplification section (requires the final result first). Field
note given to PI: this is discrete/combinatorial geometry (packing) + computational real algebraic
geometry + rigidity theory, not algebraic geometry proper. IMPLICATION: keep REGISTRY/LOG/certs
paper-ready; write-up deferred; interim deliverables (3.84 record, n=12) remain valuable as future
paper components or standalone notes.

Update 2026-08-31 (A50 closed done-mixed â€” the span-semigroup program DELIVERED): **NEAR-FLUSH
EXCLUSION THEOREM**: theta* = 1.73465 deg (exact root of 1969271t^2 + 2000000t - 30729; = where
4(cos-sin) = s0): any wall-to-wall load chain with ALL tilt classes below theta* cannot span at any
s in [3.82, s0] â€” robust to mixed-normal links, L <= 8, near-monotonicity-free (1.166 deg). The
program's first quantitative delta0-type theorem, at chain level (the only level A46's bridge left
open); retro-explains A49. Also: exact tilt-exclusion table (8 gaps, 5.98 deg of (0,45], all
endpoints quadratic surds); TILT PINNING (span equation => chain tilts are a finite algebraic menu
per s â€” no continuous freedom); T2.3(i) proved (CC-pinned pressers confined to finitely many s;
elsewhere wall-wedge closing is strict descent); T2.4 mechanism (wall termination = the chain's
only span-releasing contact â€” flushing it releases all pinned tilts at once = A49's simultaneous
collapse). GAP A50-G1: the free-presser branch â€” cheapest route = second-order descent at the C5b
balance (exact-rational curvature). A52: Prop 1 (duality collapse) CONFIRMED 21/21 â€” the equality
manifold REGENERATES against any certified field pair (replacement ghosts always exist, all atoms
at capacity exactly 1); two-field N6 route closed. FLUSH-MANDATORY status: near-upright chains
dead (A50 T2.1), thin dead (A47), CC-pinned pressers nearly dead (T2.3i finite-s + per-family
obligations), REMAINING = free presser (G1) + mid-tilt world (A51 running) + composition.

Update 2026-08-31 (A51 closed done-negative â€” and it FALSIFIED a banked law): 0 flush-free
candidates in the mid-tilt world (399 descents; 113/113 local-stratum minimizers
BLOCKED-BY-FLUSH-BOUNDARY at s_min = s0 + 0.00133 â€” far tighter than A49's 4.0; 15 runs land ON
Trump exactly). A49's wall-termination law INVERTS in the pure mid-tilt world (6% wall / 94%
interior-pair solo events); REPLACEMENT LAW (0/149 counterexamples): flush is acquired WITHIN a
tilt regime â€” uprights flush with walls/uprights, tilted with tilted, never cross-regime. A50's
T2 wall-termination theorems stand (they are about near-upright chains) but the universal-breaking
interpretation is re-scoped (gap G-A51-1). SIDE FIND: new non-catalogue attractor s = 3.8853914
(30 hits, VALLEY rank 33/34) â€” certification dispatched (A51-NEW-0, A37 pipeline, atlas append).
Flush-mandatory: corroboration now includes the mid-tilt world; I-L19 stays a global-realizability
conjecture; open = A50-G1 free presser (second-order route) + composition.

Update 2026-09-01 (A53 closed done-success â€” THE TOP OF THE STRATIFICATION COLLAPSED, first
decomposition where this ever happened): PI's I-L20 simple-square stratification (Young-diagram
form, census 1110 tuples / 163 D4 classes, k <= 9, s-stable). TIER 1 CLOSED: all k >= 7 strata
certifiably empty (L5 subset cap, 0 exceptions); 32/33 k=6 classes certified dead â€” tau typically
4.000000 EXACTLY vs budget 5 with INTEGRAL blocking packings (the 1/4-ghost is a full-box-symmetry
creature; residual regions kill it outright); 18/21 non-Trump k=5 certified dead (F4-shield-free
leverage real). OPEN STRAGGLERS (4, all corner-dominated/Trump-adjacent â€” matching I-L20's
oxygen prediction): k6_23 Trump+TL (4.9337), k5_11 (5.905), k5_13 (5.677 FAIL), k5_16 corners4+1
(5.98951 ~ genuinely at budget). Trump canary: skeleton ((2,1),(1),(1),empty) k=5; 6th upright
eps-off-grid with eps = 0.03255831... (degree-7 minpoly â€” at NO slot); its completing slide
BLOCKED by tilted sq7's corner (intrusion 0.0135) â€” the A46/A48 bridge geometry measured inside
Trump's own packing; k6_07 (slide completed) certified dead. Trump-residual localization FAILS at
pilot quality (tight variety 5.1%, uncovered core = the pinwheel center). Theory: partition
exhaustiveness [T], 33-node cap [T], slide-stuck minimizer exists [S] but slide-stuck =/=> high k
(Trump's blocked slide = the counterexample mechanism; blockedness LP-invisible). NAMED GAPS:
G-A53-1 s-parametric transfer (kills at s0 only; needed for any s(11) > s0' use); G-A53-2
blocked-slide pricing = the composition point with I-L19/A48 cascade. NEXT MOVES RANKED: 4
stragglers (Trump toolbox not longer LPs), k=4 sweep (14 classes, cheap), s-parametric certs,
low-k = the remaining deep work (flush-poor + blocked-slide bridge).

Update 2026-09-01 (A54 closed â€” the k >= 6 tier is UNCONDITIONALLY EMPTY): k6_23 (the last open
k=6 class) and k5_13 killed with exact certificates (independently re-verified) â€” all 33 k=6 Young
classes certified + L5 cap => every stratum with k >= 6 empty, no conditions. Tier 2 = 19/21
non-Trump k=5 dead. The two survivors (k5_11: 0.35% short of certification; k5_16: at budget) are
CHARACTERIZED: their LP optima ARE Trump's ghost with re-decorated boundaries â€” the survivors are
Trump's basin minus the eps-off square (5 of his 6 free squares within 0.05-0.26 of their tight
sets). LEVERS BANKED: merged warm start (union of all prior rows/atoms, pruning OFF) + lifted
scale cap (budget/tau, not 1.03) â€” both necessary; row-pruning starvation diagnosed (prune COLUMNS
only for kills); tau_LP bounds tau* in NEITHER direction on restricted LPs. Rung 3 priced for the
satellites: ~612-6000 children, A24's 100-300 CPU-h regime. Rung 4 dead a priori (straggler pins
are zero-wastage configs). MISSING TOOL (A54-2): no ALIVE-side verifier exists (rigorous
tau* >= budget needs an integral-witness polisher or a coverage-<=1 dual verifier â€” the mirror of
verify_case). STRATIFICATION SCOREBOARD: k>=6 empty / k=5 dead except Trump + 2 satellites /
k<=4 unswept. Next menu: k=4 sweep (cheap), satellite rung-3 trees (~2 desktop-days), s-parametric
transfer (G-A53-1), low-k slide-stuck design, ALIVE verifier build.

Update 2026-09-01 (A55 closed done-success â€” THE PROBLEM LOCALIZES): 8/14 k=4 classes killed
exactly, and the sweep is EXACTLY SHARP â€” a k=4 class is certifiably empty iff contained in no
open k=5 class (zero exceptions). K1 (new lemma): aliveness propagates DOWNWARD (adjoin the pin to
the witness family) â€” kills climb containment, aliveness descends; dual of L5. K2: the four
Trump-sub-skeleton k=4 classes are PROVABLY uncertifiable (a kill would refute Trump's
feasibility). K3 (pre-registered): k4_05 = the unique class whose kill closes BOTH k5_11 and
k5_16 â€” survived as predicted (K1-hard). corners4 converges to 7.200 not 7.000 (interior block ->
3 from above; the 0.2 excess is entirely interior). CONSEQUENCE: the ENTIRE remaining
stratification problem localizes onto THREE k=5 classes â€” trump5 (provably alive, is Trump) +
k5_11 + k5_16 (his two shadows, the ghost mimicking his zone profile); all k<=4 aliveness is
K1-inherited from these; one unprotected low class k3_00 (killable profile, quick job dispatched).
A56 running: 26/52 kills transferred to the full window so far, ZERO holes anywhere, k6_23 partial
to within an 8.4e-5 sliver; corrected depth law (fast FAILs = witness-cap aborts); recipes =
sub-window bisection + margin re-solves. NEXT DECISION after A56: the two shadows (rung-3 trees ~2
desktop-days each, or new localization ideas) â€” killing them + s-transfer = the stratification's
upper structure complete, leaving low-k slide-stuck design as the final frontier.

Update 2026-09-01 (k3_00 dead â€” THE PIN-LP ROUTE IS COMPLETE): 61 certified pin-sets (1 k=3 + 8
k=4 + 19 k=5 + 33 k=6); verified class-by-class over all D4 images: EVERY remaining open Young
class at every k <= 4 is contained in one of exactly THREE k=5 classes â€” trump5 (provably alive =
Trump), k5_11, k5_16 â€” no exceptions, and by K1 none can ever carry a certificate. The entire
stratification problem = those three classes. LEVERS BANKED: checkpoint-folding into merged_warm
(interrupted passes lose nothing â€” k3_00 passed at ROUND 0 after folding a killed pass's 2951
orbits; eta was never the progress variable, accumulated atoms are); detached Start-Process
pattern for >55min jobs (harness reaps backgrounded ones). A56 final sweep running (30/52 -> 22
mechanical resolves).

Update 2026-09-01 (A58 + A59 closed â€” the three-front endgame is converging on every front):
A58 (done-success): the TELEPORT LEMMA CC-2 (10 lines, subsumes slide-stuck: k-maximal minimizers
have every completable slot box met by >= 2 non-simple squares) => Theorem A58-1 (k<=3 clear
corners are doubly crowded; k=0 => >= 8/11 corner-tied); Trump teleport-extremal (8/8 boxes
exactly 2 meeters, zero margin); area route provably void for k<=3 (0.9715 B0); residue = the
bridge geometry Trump's TL realizes; successors named (pair primitive, CC-4 -> FJ rows, extension
to k=4/trump5). A59 (done-success, GO): trump5 finite program P0-P7 PRICED AT SINGLE-DIGIT
DESKTOP-DAYS at 5 procs (~1e4-1e5 certs) â€” r_kill = 4.55*hw exactly, annulus closes at +2.19
levels (hw <= 8.13e-4) into the A36 basin (genuine discharge leaves, no wedge work); upward trap
certified via SIX completions (8 naive - 2 overlap-dead), all with PASS kills; Trump-adjacent
sibling kills IMPOSSIBLE (ALIVE-certified) but residue contracts ~34 boxes/level, 41->18->7->0
into the basin at level 24; tau* = k conjecture (17/18); engine changes: alive-gate (1 ms) +
zero-atom vacuity arbiter (0.79 s, no LP) â€” fold into tree57; Lemma A59-P1 (interior occupancy at
trump5). Honest conditions: A56 parametric overhead on (K) leaves unpriced; depth-2/3 ladders
extrapolated (first falsifier); census 4.4e10 = map only. A57 shadow trees: 44+ kills, 0
unresolved-that-resisted (at-budget children die on bisection), 3 failure modes characterized, no
cert ever failed exact verification. A56: 15/22 mechanical resolves. THE COMPOSED PICTURE: shadow
trees (hours) + trump5 program (days) + k<=3 residue (A58's bridge-geometry successors) + s-window
transfer = the full s(11) = s-hat proof outline, with only the k<=3 bridge residue lacking a
priced route.

Update 2026-09-01 (A56 closed done-success): the stratum-kill library is now WINDOW-GRADE â€” 38/52
proof-grade over all s in [3.82, s0] (4 M1-theorem + 21 original + 13 eps_geo-re-solved), 2
partials (k6_23 open only on an 8.4e-5 sliver; k6_07 a 0.050 band), 12 s0-only with the successor
recipe (A57 atom-enrichment to slack >= 0.5, then eps_geo + 4D). Soundness stack P0-P7: census
stable on the closed window; monotone transfer REFUTED as a route (tilted chains defeat both
embeddings; M1 saves single-corner sets); adaptive interval-s 4D verification on the UNMODIFIED
audited core; certificate-fungibility ledger rule. Measured laws: t_4D ~ 261us x s-splits;
repairability gate budget - tau0 >= 0.5 (eps_geo is the lever, weight scale inert; d-tau/d-eps ~
1.4e2); two witness-cap artifacts corrected. ZERO holes in any run. Cost 9.6 h. Cap status:
k(P) <= 5 window-uniform modulo 6 named k=6 residues.

Update 2026-09-01 (trust chain / publication): PI ran an OUTSIDE AUDIT agent -> docs/publication_checklist.md
(54 items, codes S/H/C/F/R/W/P; go/no-go strip for any optimality claim) + PR #1 (root Lean CI, .github/workflows/lean.yml;
fast+Mathlib green; 3.82 cert re-verified on a 3rd machine, box count identical). PI STANDING DIRECTIVE: no "trust me"
steps — every compute step an exact certificate, ALL logic/theory in Lean. Publication plan: NOT the classic checklist
route; AI-forward writeup (human+Fable+Opus process) and talk to Anthropic contacts about publishing/mathematician review.
A62-trust-ledger dispatched (Fable): F3 formal Lean statement w/ leaves as hypotheses, H13+H11 dependency graph +
load-bearing-conjecture sweep, C1 TCB + C2 frozen cert specs, C9 hash manifest. Post-tree-closure wave (not started):
H9 prune -> formalize only used lemmas; C3 second impls of verify_case/verify_param from frozen specs (clean-context
agents); C8 corpus-wide cold re-verify; C4 consolidated corruption suite; R3/R4 adversarial agents vs the kills; F6
interval-trig blocker on A22 Lean replay (tan-half likely cures). A57 speedup declined: not critical path (A60 is);
~1 min/child x ~2060 left / 3 shards ~= 2 days, acceptable per PI.

Update 2026-09-01 (A62 closed, done-success): TopLevel.lean = formal statement, s_eleven_ge/eq/unique from exactly
13 named axioms, builds clean. 3 HIGH holes: F2 no UB route AT s-hat (Lean UB is s-hat+8.8e-10, checkPacking needs
strict margins -> equality needs A22 Krawczyk replay in t-coords or Fits-closedness); uniqueness follows from no
written lemma (selection yields a DIFFERENT minimiser; axiom unique_transfer isolated; PI decision whether to claim);
F9 interior-disjoint vs closed-disjoint bridge gap at every kill (lambda-scaling repair implicit, written nowhere,
ties to F6 window-density). F6: window transfer must be FUSED into kill axioms (transfer principle would axiomatise
A56's refuted claim). H11: ZERO load-bearing conjectures; 14 open nodes; G-A59-10 extrapolation flag vindicated by
A60 falsifier. TCB gap: no standalone end-to-end verifier for tree compositions (A57/A59/A60 layer = where A54 gap
lived); mpmath.iv in rigidity decision path. Artifacts: depgraph.json/svg (41 nodes), docs/specs/* (4 frozen cert
specs + tcb.md), manifest_3.8x.md. Pushed 7fed015. Next wave candidates: F7 Sturm cert (10 min), F9/S4 lemma,
unique_transfer, F2 route.

Update 2026-09-01 (A63 closed, done-success; pushed f088981): T1 Sturm CLOSED — shat is a Lean DEFINITION,
shat_spec a THEOREM (calculus-free, octic strictly increasing right of left endpoint), axioms 16->13. T2 bridge
CLOSED + HEADLINE: lambda-dilation Lemma B proved; corpus scan (68 certs, cores eps-fat, margin ~1e-9>0) =>
parametric certs fully instantiate stratum_kill, BUT s0-only certs bind only a 4e-10-relative shell below s0 —
A57 tree leaves + A60 zone leaves instantiate NOTHING on [3.82,s-hat] as emitted. Repairs: verify_param
re-emission post-pass (no LP redo) or slack-core grid (~37 sides). Relayed to A57/A60/A61; awaiting A57 cost
assessment; A61's 12 conversions now load-bearing. T3 unique_transfer HALF: axiom follows from census
exhaustiveness; real hole moved to stratum_kill forall-quantifier at K1-protected classes; architecture =
CC-2 chain -> H10-stuck (re-base A58 on stuckness) -> basin -> Theorem U (one-square rigidity of z-hat, THE new
leaf; 11 re-insertion certs spec'd). Obligations U-O1..U-O4. T4 UB-at-shat HALF: route (b) REFUTED as finite
route; attainment lemma written (discharges `attained`); residue = algebraic identity shat_A22 = shat_octic
pinned to <= 2.1e-47; closure via number-field verification (deg-7 coordinate obstacle, compositum <= 56) or
restate shat := shat_A22. T5 CLOSED: InStratum bridge (K1 homed, M->E lemma); theta-t exact |dt|<=|dtheta|<=2|dt|;
rBasin = 3/2000 Lean definition; A60 landing radius = 0.30 x rBasin. Open nodes 14->13 (+A.THMU). Machine:
pagefile F: 25/100 GB, commit constraint gone; A57 5 workers, A60 4 shards, resumes verified exact post-restart.

Update 2026-09-02 (window strategy DECIDED + executing): cover-invariance lemma HOLDS (docs/proofs/
cover_invariance.md; affine form exact vs corpus; 601 logic kills need per-box C-check). Pure-parametric route
rejected by measurement: naive anchoring FAILs at window bottom (0 holes, T14 signature) => per-leaf anchoring
search x2300 + steep atom-count scaling (4 atoms 14s, 159 atoms >340s). DECISION: hybrid — A57 grid backbone
delta=1e-2 (V9/E4 gate CLEAN), 4 sides {3.877084, 3.862404, 3.847780, 3.833212} with 95%-overlap slabs covering
to 3.81794, tag G1 (delta=0 logic kills NOT valid at delta=1e-2 — 13/344 flip; old tag quarantined), parametric
to_param.py --beta-mid one-shot on <=30-atom leaves as skip-list only. Estimate 6.4 desktop-days no-skip, 4-5
with. Side 1 not free: ~300 delta=0 children re-emitted. A60: per-campaign delta differs (basin widening eats
85% rBasin at 1e-3 => A60 wants delta~1e-4); Lemma B-NO covers its 4 confinement leaves (consumer widens
outward); sq2-3 basin landings at 1.04x margin — landings + dilation must be budgeted TOGETHER (open); A60
delta-test re-emission pending. rBasin coordinate bug caught+fixed in tree60 (theta-radians vs t-world).

STANDING PRACTICE (PI request 2026-09-02): lean/depgraph.json + lean/depgraph.svg are the LIVE monitoring copy
of the lemma dependency graph (promoted from A63; A62/A63 results/ copies frozen provenance). The ADVISOR updates
labels/notes as milestones land and re-renders via `python lean/render_depgraph.py` (stdlib-only; legend shows
live counts; nodes missing from LAYERS auto-drop into a catch-all row). Update at close-out commits.

Update 2026-09-02 (A65 closed done-success, pushed 56a69a0): THEOREM U CERTIFIED — U-O1 discharged, 11
re-insertion certs PASS cold depth 60 with Sigma w = 0 (ten slack cores geometry suffices), at rational side
s'' = 3877083591023/1e12 inside the Sturm interval; falsifier control holes ONLY at Trump's pocket; A.THMU ->
certificate+verifier; uniqueness residue now U-O2 (=H10-stuck) + U-O3 (A57 G1) + U-O4. H10-stuck PRICED:
Trump SATURATES his own class at exactly load 2.00 (why the tier is hard); routes (a) decoupled counting +
(c) absorption dead [T]; boosted-kill LP refuted at every beta (law tau(beta) = tau(0)(1+mbar*beta), mbar
3.00/2.53 > needed 2.29/2.00) => single-square measure certs PROVABLY cannot close H10 (forced 2-crowd value
is pairwise); no protected class has a crowd-saturated family (exact D=1e8, short by 1-3; corners4 EMPTY at
s0, load 2.29 supercritical unique). Residue ranked: (1) pair certificates (A58-G3), (2) corners4 channel
infeasibility (s0-2 = 1.877 < s(2) = 2), (3) conditioning/FJ. A66-corners4-pair DISPATCHED (Fable): T1
corners4 empty at every window s via channel argument; T2 pair-certificate family design+spec+pilot on k4_08
(collapse-theorem distinction required; NO-GO would be the ninth face). A64 (Lean wave) still running:
Parametrize.lean + MeasureBridge.lean visible in tree.

Update 2026-09-02 (A64 closed done-success, pushed 7c6cdac): s(11) >= 3.82 is an END-TO-END LEAN THEOREM
(s_eleven_ge_382; MeasureBridge.lean ~950 lines full checker soundness, native_decide isolated in
Measure382Check.lean [2380s — NEVER re-run casually]; axioms propext/Choice/Quot.sound + ofReduceBool).
parametrize DISCHARGED (Parametrize.lean; square own 90deg symmetry + half-angle, pure algebra). UB-at-shat:
sign/interval route REFUTED (needs height bound, doubly-exp); axiom SPLIT — entire residue = ONE axiom
shatA22_eq_shat; new (c-idl) closure spec = saturated ideal-membership cofactor cert (rational poly identities
+ one sign gate, no number fields; search = bounded Groebner/Macaulay). KEY TOOLCHAIN LESSON (findings):
cross-toolchain elaboration is the bottleneck, not the math — checker compiled sans Mathlib carries core
OfNat/Decidable instances so rw/simp fail on its ites; recipe = hypothesis copy + split at + dsimp only +
exact_mod_cast; applies to future A22 Krawczyk replay. Depgraph: gold tier live; open nodes 13 -> 12; owner
chips convention (dark badge = attempt working the node; blocked_only dashed outline = own work done).
DISPATCHED: A68-lean-wave3 (green->gold: A.D1 attainment, A.SBRIDGE dilation bridge, B.K1, E.COORD theta-t;
priority order, honest partials OK) + A69-cidl-identity (execute (c-idl) search, elimination along contact
chain, measured wall = success; S3-fallback restatement is the safety net). Circuit-style depgraph renderer:
bus trunks per source->row, ports, global crossing dedup, zero overlapping segments verified.

Update 2026-09-02 (A67 + A69 closed done-success): A67 — D.D4 machine-checked at s0 (harness ported via 2
rebound constants, R1-R8 PASS incl census D4-equivariance; WLOG conditional on s0 root occupancy = D.TREE;
t-bins side-independent). A69 — shatA22_eq_shat CERTIFICATE FOUND+VERIFIED (certs/cidl_identity.json +
verify_cidl.py): A22 structure collapses to 13 generators LINEAR over Q[t] => Cramer/adjugate cert, ~2 min
compute; identity e*Delta^8*octic = sum q_j G_j + Sturm sign gate; s_A22 = octic 2nd root. A53 L4 deg-7
coordinate was PHANTOM (A03 findpoly junk annotations) — all z-hat coords in Q(t-hat) deg 8; tan-half minpoly
now DERIVED not PSLQ. Lean residue = CIDL-LEAN engineering obligation (attainment_ub.md 7.5) + A.UNIQ prose
derivation — both queued for next Lean wave. A.UBshat -> certificate+verifier; frame row zero solid reds;
remaining solid reds all compute-gated (A60 x4, A61) or active theory (C.K4TIER/A66). Depgraph conventions
added: owner chips; blocked_only dashed outline colored by own_tier (TOP gold-dashed, A.UNIQ green-dashed).
A69 ops incident: wrong-PID force-kill during OOM triage (campaign worker, requeued; mains verified alive).

Update 2026-09-02 (A66 closed done-mixed, f524970; A71 dispatched): corners4 counting route REFUTED
theorem-grade (exact 7-point occupancy witnesses at every window side; obstruction is ORIENTATION COUPLING,
invisible to single-square machinery) — class not deleted. Pair family: Lemma P/P0 sound (stuckness input =
CC-2-prime 2-crowds; box widening 3(lambda-1)); CANARY THEOREM (dilated Trump saturates trump5 pair threshold
C(6,2)+6beta exactly => no sound pair cert kills him — standing guardrail); A34 collapse inapplicable (pricing
dual over realized pairs, no gluing); Lemma P-B (PI basin row) sound ONLY for exact strata + ~5e-4 shell below
s-hat (monotone reading would bind Trump). Pilot verdicts: k4_08 KILL-SHAPED (tau2 = 21+6beta vs 21+7beta,
margin beta; false death-witness retracted via containment audit — chore's exact checks missed containment,
lesson recorded); basin discount = RESERVE (window gamma<0.245, gain ~0.4 at 0.1; naive gamma-rebate dodged);
corners4 OPEN (tau2(0) in [14.89, 21.32], simplex-time bound ~17k rows). Standing gates: D1 catalog adequacy +
containment audit on every pair-LP number. verify_pair.py = new pure-Fraction 6-D B&B verifier (not TCB yet).
A71 (Fable): T1 emission oracle loop k4_08 (A39 discipline, verify_pair as oracle); T2 stuckness rows ->
k4_11/k4_03; T3 corners4 first-order solve + exact dual rounding. A70 (V.CASE then A22/A36 replay) resumed
post-usage-limit; CaseHyp compiles, bridge layer in progress.

Update 2026-09-02 (A70 closed done-success, 34b57af; A72 dispatched): V.CASE LEAN-PROVED — case-LP verifier
soundness formal (CaseChecker/CaseSat/CaseHyp/CaseBridge.lean; checkCaseI_price = spec claim P2 feeding A68
Dilation pigeonhole; checkCaseI_kill = lemma_B hcert producer per PASS file) + END-TO-END pilot replay
(k5_06.lo kill cert, native_decide seconds, Python cross-check identical tree). Real math found: SAT
sufficiency had NO prose lemma anywhere — now sat_squares (geometric Hahn-Banach + 4-cone bound; clamp
shortcut FALSE w/ counterexample). Spec erratum: "a=0 point core legal" wrong both ways. Rigidity rung (a)
LANDED: a36_check_exact.py (17 basin certs, 339/339, 10.8s) + a22_recheck_exact.py (full Krawczyk chain,
1.5s) — exact rational, stdlib only, dyadic intervals + alternating-Taylor cos/sin => mpmath.iv OUT of
rigidity decision path at Python tier (F6/E.IV neutralized); theta-frame Taylor route needed NO t-reparam
(t-frame reopens at Lean rungs (b)/(c), open+named). Engineering recipe: name every checker subcomputation
as top-level def; core Rat crosses Mathlib boundary friction-free. Named residues: corpus-wide case replay
(price separately), B.2-prime prose, V.PARAM, census hface, rigidity Lean rungs (b)/(c), CIDL-LEAN, A.UNIQ
derivation. A72-census-cleanroom dispatched (Opus): H2 independent re-enumeration from the written Young
definition, sha256 frozen before peeking, diff vs A53; closes census hface computational content on MATCH.

Update 2026-09-02 (A71 closed, 3d7e5c9; A73 dispatched): k4_08 v1 emission = VERIFICATION WALL (Lemma W,
pair_kill.md 6.5): certificates exist (tau2 = 21+6beta stands) but every P1-prime-valid cert carries >= 11
coverage units on atoms < 0.15 deep; frozen verify_pair at 57 nodes/s => 125 days-to-centuries. Whole critical
tier unified: k4_11 = 21+6beta, k4_03 = 21+4beta EXACT (margin -beta, kill-shaped). P-B image sets corrected
(k4_08 has TWO Trump images: {id, diag}). stuck_rows.md SR-1/SR-2 written [T]. corners4 SOLVE WALL BROKEN
(inclusion-maximal point reduction 265k->1375 + IPM-no-crossover): certified exact lower 20.516885, bracket
[20.528, 20.542], ALL >= 0.457 below threshold 21 => P0 emptiness route OPEN, corners4 least-walled (1-unit
shortfall), natural v2 pilot; 622-atom seed dumped. A66 support catalog NOT pair-adequate (40.4% underpriced)
— adequacy gate vindicated again. A73 (Fable): spec v2 (margin-aware splitting + analytic coverage clause w/
per-clause lemmas), compiled clean-room verifier (Rust/C, exact rationals, >= 100k nodes/s target, doubles as
C3 for pair family), pilot corners4 emptiness cert. Canary ledger discipline continues (dilated Trump family
re-verified as exact death witness per run).

Update 2026-09-03 (A73 closed done-mixed, a5addca; A74 dispatched): THROUGHPUT WALL BROKEN — clean-room Rust
verify_pair2 (spec-only build, C3 cross-val ALL AGREE, i128+BigInt exact, 300k nodes/s geometry / 131-323k
--jobs 8; scoop rust-gnu 1.98 installed user-level; target/ gitignored) + spec v2 (Lemmas S/Q/M/E/F exact-iff
membership via corner reduction, VACUOUS-CONTAIN found by clean-room review, DEFICIENT-EARLY, hint trees) +
FIRST full-quantifier atom-bearing P2-prime PASSes (s=3 anchors; cost tracks measure frontier, NOT
(1/margin)^6). corners4 wall MOVED to emission shape: tangency trap (LP-optimal atoms sit ON membership
boundaries, COVERED fires 0x); Lemma W-prime [T]; measured eta* crosses threshold in (0.006, 0.05) =>
uniform-eta emission DEAD, certificates must be MIXED-DEPTH measures; cost driver = weight fragmentation
(mean w ~ 0.05, ~15 atoms certain at once), not margin. A74 (Fable): mixed-depth emission loop (loop413.py
ready, consolidation pass = fewer fatter atoms, Rust certify-in-loop), corners4 first, then critical tier
w/ stuck rows if it lands; else Lemma W-double-prime. Canary ledger discipline standing.

Update 2026-09-03 (PI bottom-up direction; A76 dispatched on Fable 5.1): PI reframed the k-tier stall as
top-down asymptotic difficulty AT Trump (same shape that started the project) and proposed extending the
BOTTOM-UP side: enumerate the narrow contact-graph/grain space of the remaining protected strata near Trump
and discharge grains directly, moving the floor up. Advisor analysis: far-field explosion (A31/A32 1e30) does
NOT apply in the near-Trump annulus (A65: every feasible family is a Trump-image perturbation); rigidity
certs get EASIER near Trump (inverted difficulty vs LP); COUPLING = Lemma P-B's exclusion power scales with
the discharged radius R (currently a 5e-4 shell from rBasin=3/2000) => bottom-up grows R, top-down pair-LP
consumes P-B(R); they meet in the middle. Risks designed around: completeness BY CONSTRUCTION (A37/A51 atlas
was incomplete by search); flexible grains need drain v3 / FJ (t3lib) — different cert family, own TCB; A44
index identity classifies rigid vs flexible. A76 brief: T1 Lemma G-R local completeness + per-class
|G_S(R)|; T2 discharge (Krawczyk exact / drain / FJ) + composition lemma; T3 P-B(R) addendum, hand R to A74.
A74 keeps the C.K4TIER owner chip; A76 is the complementary front. Also this session: advisor's own
process-attribution false alarm on A60 (relative-path trap, 5th instance) — use A57 whose.py for sweeps;
an empty check result is not a negative result.

Update 2026-09-03 (A75 + A74 closed; A77 dispatched): A75 (Fable 5.1) — V.MEAS + V.PARAM LEAN-PROVED
(verify_measure DRIVER incl. float shortlist as arbitrary oracle; 4-D param checker w/ kill at EVERY real side;
pilot k5_06.param full-window native_decide 215s); D.N1/C.M1/C.T5T11 gold; B.SEL/C.CC2 partial on census
interface hinc (=F11/H2); board 14 gold / 12 blue / 3 green / 8 open; verifier_lean now on C.K61/C.A57/C.WIN/
D.TRAP/D.P1/A.THMU; corpus-wide param replay priced ~3 h serial. A74 (done-mixed): FIRST SUB-THRESHOLD
restricted pair measures for corners4 — md5 20.98857 / md7 20.95955 / md8 20.95828 < 21, P1-prime-valid,
tangency trap closed by construction (every atom >= its level eta); Lemma W-double-prime (slack 0.011-0.040
vs 0.47 sharp; forced profile ~70% mass at 0.008-0.02, 25% at 0.002; depth pricing + consolidation both spend
slack; catalog growth by exact holes ~free); verification residue CAPS ONLY (0 holes; hint trees -> 99.8%
certain mass; loop converges ~4x/iter, ~1 h/iter, holes 220->57); NO PASS yet. Rig lessons: read HiGHS duals
BEFORE deleteRows; IPM-no-crossover no feasible iterate >10M nnz; bound-saturated columns break dual covering.
A77 (Fable 5.1): iterate to PASS (N=8 budget) or Lemma W-triple-prime; add A76's P-B(R) row if delivered.
A76 (bottom-up grains) running in parallel.

Update 2026-09-03 (owner sweep; A78 + A79 dispatched on Fable 5.1): PI rule — EVERY non-gold node must have a
clear owner. Assignments: A78 (Lean wave 6) = Census.lean F11 pinning A72's 8 binding choices + Lean-computed
census (B.CENSUS, B.SEL, B.EXACT, C.CC2 via hface/hinc), CIDL-LEAN (A.UBshat), alivewitness + D4 checker
soundness (D.ALIVE, D.D4), unique_transfer derivation (A.UNIQ own-tier), fixed-corpus Lean replays C8 for
C.K61/D.TRAP/D.P1/A.THMU (prices A57/A60 replays). A79 = rigidity rungs (b) E.A22 Krawczyk + (c) E.A36 basin
in Lean (theta-frame per A70; rBasin fixed). C.WIN owner A61 (replay gated on stragglers + G1). Non-attempt
owners: TOP = "auto", X.* + D.TAUK = "off-tree" (gray chips = no work). PI confirmed the gold-dashed
"proven assuming dependencies" affordance reads well — keep it. Renderer: chips gray for non-attempt owners.

Update 2026-09-03 (A76 closed done-mixed, 78ec0ec7): BOTTOM-UP FRONT WALLED — grains adjacent to Trump on
the protected strata cannot extend R beyond A22/A36/A40: the hard family is always HINGE grains (strip flush
pair degraded to single-corner contact; 7-8-10-9 ring worst) = A40's saturation face omega_b = 1/kappa_eff
seen from below; k4_08 has 1.7e7 grains, 13,702 hard at (1e-2, 2e-3), ratio ->47.8; continuation residue ~1e7
Krawczyk steps, priced not started. LP measurement: basin row gains ~0.1 margin per DECADE of radius =>
"the two fronts do not meet" — P-B(R) is a reserve, never a lever. USEFUL BY-PRODUCTS: (1) A40's 2930 basin
certs EXACT-rechecked (a40_check_exact.py, 168,774 checks, 0 fail) => per-coordinate radius (6.55e-3 -
sqrt2*rho_B, 3.27e-3); rBasin raisable to 27/10000 — would fix A60's D.S6 4.9% overshoot with no extra
bisection (relayed to A60 to confirm same object; A79 told to hold 3/2000 until A60 adopts); (2) trivial
radii: corners4 d_min 0.8445, k4_05 0.4365 — exact class empty near every Trump image (corners4's wall is
emission shape, not ghost saturation; A77 told not to wait for P-B); (3) Lemmas G-R (local completeness by
construction, exact cert), K, DF (drain-flex), D2-double-prime; K/DF dichotomy exhaustive on Trump rows,
no positive dependency at z-hat; (4) t-native exact Krawczyk enclosure of z-hat (no Taylor) = E.COORD rung at
Python tier. Canary safe.

Update 2026-09-03 (PI idea: U_k ladder; A80 dispatched on Fable 5.1): extend Theorem U upward — U_2 on the 14
contact-graph edges (only CONNECTED removed sets need joint certs; non-adjacent pairs = U_1 + separation lemma
or cheap direct cert — PI shortcut, repaired: U_1 pins all ten others so it doesn't literally apply twice) —
composed with the basin into a COUNTING exclusion on exact strata: "at most 10-k squares within slack delta
of Trump slots." Advisor analysis: differs from P-B (one coordinate off by 1.5e-3, measured 0.1/decade) by
forcing (k+1) WHOLE squares off by delta ~1e-2 (A76 rigid-grain radius w/ pins) ~ (k+1) budget units via
dtau/deps ~1e2 — first exclusion shaped like the ghost itself. Named risk: A12 region-rank lesson (fractional
loads satisfy integer counting rows) — but A66 measured the near-Trump pair-LP optimum INTEGRAL at Trump's
witness, so test not argue. A80 order: T1 re-emit U_1 at delta in {1e-3,3e-3,1e-2} (A65 used ~1e-4) -> T2
counting row k=1 ("<= 9 within delta") on k4_08 pair-LP (copy of A66 rig), margin vs -1.40 baseline / -1.51
P-B; lever iff >= +1 -> T3 climb (U_2 edges, connected triples). Exact-stratum-only soundness (monotone
reading binds Trump). Also: A60 resolved D.S6 budget WITHOUT rBasin change (per-coordinate A36 radii fit w/
57% spare; overshoot was the uniform-collapse s-slab gate artefact; one more bisection level; relief is
s0-only — window form D.SLAB still open); A79 stays on A36 @ 3/2000.

Update 2026-09-03 (A78 closed done-success, d0ce2e77): TOPLEVEL AXIOM ROSTER 12 -> 7. Census.lean = the
Young-form definition as a Lean DEFINITION (all 8 A72 choices pinned; B1/B3/B6 theorems; B2 predicate
decided combinatorially, proved equal to real one on (3,4)); L3 exhaustiveness = skeleton_mem_census
(theorem about packings); CensusCheck native_decide = 1110/163 + D4 closure + EXACT equality w/ A72 tuple
set + orbit partition. hface was REFLEXIVITY; hinc = card_lt_teleport; M->E = class_kill. stratify and
unique_transfer are THEOREMS; s_eleven_unique rests on exactly {basin, stratum_kill, trump_residual, zhat}.
CIDL-LEAN discharged (shatA22_eq_shat theorem; new axiom a22_exact_structure = A22 certified content only,
i.e. E.A22/A79's job). A.UNIQ own tier gold (UniqueChain.lean strong induction on 11-k). D.D4 verifier_lean
(d4_wlog conditional on root occupancy); D.ALIVE verifier_lean (alive_sound, completeness-side arbiter).
D.P1 + A.THMU corpus_replayed; K61 26/61 + TRAP runner continuing (T5 engineer finalizes). LOUD FINDING:
attempts/A57-shadow-trees/results/alive/k5_16_m5.json = FALSE LP-UNKILLABLE claim (m=5 < budget 6) — A57
told to quarantine; trump5_strict.json is the only sound witness. Lean replay cost 25-100x Python wall
(k6_08 747s / 343k boxes) => A57/A60 corpora replays are multi-day desktop jobs. NO green nodes left. Board:
19 gold / 10 blue / 8 open / 6 off-tree / 1 resolved-cited.

Update 2026-09-03 (A79 closed done-success): RIGIDITY CHAIN LEAN-PROVED. E.A22 (checkA22 theta-frame port,
native_decide; krawczyk_sound Banach+Neumann+Matrix.mulVec_injective_iff_isUnit; zhatV_feas; a22_optimal) and
E.A36 (a36_basin second-order Taylor along segment, interval Hessian mass, quadratic dichotomy; 17 certs
replayed, RigidityCheck builds 140s; ONLY G3_UNIVERSAL radius 3689e-6 is load-bearing — slab gate 3.6213e-3
closes against it; 16 variants' L1-axis-disjunction soundness = sole named residue). zhat/shatA22 =
DEFINITIONS; trump_packs_at_shatA22/basin = THEOREMS. TOPLEVEL ROSTER = 3 AXIOMS: stratum_kill, trump_residual,
a22_exact_structure. Findings: A22 [F] recheck NOT self-contained (needs exact-structure derivation: mate
walls => theta=0, parallel-normal corner-on-edge pairs => equal tilts, affine known-centre for flush-upright
block); eps0/g_max/eps_w must be over box(z0,r0) not at z0 (harmless); theta frame beats t at Lean tier
(Real.hasSum_cos + alternating bounds); deep-embedded row language w/ symbolic D gives value/grad/Hessian
soundness in one induction. E.IV now absent at both tiers.

Update 2026-09-03 (A77 closed done-mixed, ad800bc9): NO corners4 PASS. A74's "holes 220->57 convergence" was a
--nodes HARD-STOP ARTIFACT (283k-393k undischarged leaves behind sampled caps). Lemma W-triple-prime [M]:
complete hint trees have per-level frontier retention r(d) = 0.75-0.86 FLAT from depth 8 to 25 on every root
=> complete verification tree ~1e9-1e11 nodes; binding resource = TREE SIZE (eta-fine boundaries of a
necessarily tight measure), not holes, not LP. Loop: holes fall ~6x/iter but hole placements consume the
slack (md9 W2 = 20.99646, slack 0.0035; next iteration crosses 21). PAIR-CERTIFICATE ROUTE CLOSED in this
certificate form for corners4 (the least-walled class). C3 gap found: ref roots() ix-major vs Rust iy-major
(spec silent) — hint keys not portable; with --root_order rust both impls fire rule-for-rule identically
(VACUOUS-CONTAIN 0 in both); spec erratum owed. K-TIER STATUS: top-down pair route walled (W-triple-prime),
bottom-up grain route walled (hinge grains, A76), U-ladder verdict pending (A80; dodge witness staged).
Likely next: A65 route (3) = A60-style CONDITIONING trees on the exact-k4 residual (cover + ladders +
confinement into basin, exact-stratum hypothesis as extra constraint; 21-dim vs trump5's 18) — branching
avoids the single-global-measure tightness wall. Roster still 3 axioms.

Update 2026-09-03 (A80 closed done-mixed b4be7d4e; docs/known_results.md = R5 ledger e941d61d; A81 dispatched):
U-LADDER VERDICT = RESERVE-PLUS: rung-1 row (<= 9 squares within delta of Trump slots; sound on EXACT stratum
only, Lemma U-ROW) moves k4_08 adversary 27 -> 26.000 exactly (margin -2.000; +1.00 vs plain, +0.59 vs P-B);
ladder LINEAR ~0.55/rung (rungs 2-5 -> -2.56/-3.12/-3.72/-4.49), whole ladder ~3.5 units, NOT (k+1). Dodge
witness = A12 mechanism quantified (fractional adversary thins zones w/ 3e-3-displaced variants keeping box
incidences). T1: U_1 certifies at delta up to 1e-2 BUT square 6's hinge pocket scales (5.6, 5.8)*delta so
basin landing binds at delta <= 2.6e-4 (Lean rBasin) / 3.2e-4 (A36) / 5.7e-4 (A40); zone radius irrelevant to
margin (saturation law). Lemma BR: the component shortcut is a census not a lemma (direct C0 certs cheaper
than separation; Trump's sub-1e-2 gaps defeat distance separation); rung-2 census 41/55 pairs pass directly,
14 merged pockets need atoms+peeling (~hours/rung). Canary safe. SYNTHESIS -> A81 (Fable 5.1): A77's W''' wall
= tightness (slack 0.04 => eta-fine boundaries => r(d) 0.75-0.86); rung-1 gives k4_08 ~2 units slack => emit
NON-tight cert w/ consolidation, measure r(d); if << 0.75 -> Rust PASS = first protected-class kill (then
k4_11/k4_03); if ~0.8 -> Lemma W'''' (retention intrinsic) and tier redirects to A60-style conditioning trees.
PI corrections logged in known_results.md F: axis-aligned square NOT proven (k0 open), flush contact NOT
proven (I-L19 conjecture), NO wall-flush minimum theorem (only >= 2 wall contacts on opposite walls, L6/L7).

Update 2026-09-03 (PI s0 question -> A82 side scan; A81 baseline correction): s0 = 969271/250000 = s-hat + 4.1e-7
(rational just above s-hat; shell contributes ~4e-5 in tau — moving s0 1000x closer buys nothing: Trump fits at
s-hat so every side >= s-hat has the full ghost). LEVER = BELOW s-hat: protection is an s >= s-hat phenomenon
(aliveness witness = Trump's own family, fits only at >= s-hat); at m < s-hat slack ~ dtau/ds x (s-hat - m),
plausibly a full unit by ~s-hat - 0.01. Tier strategy hypothesis: plain kills on [3.82, s-hat - 0.01] +
conditioning trees (A60 machinery) with Theorem-U leaves in the thin slab [s-hat - 0.01, s-hat] (exact-stratum
hypothesis kills the near-Trump residue; A63 architecture). A82 (Opus) dispatched: tau(m) scan over 6 protected
classes x 12 sides w/ alive-gate, crossover m* where eta <= -1, one verified cert. A81 correction: k4_08 plain
pair value = 28.000 = threshold with Lemma-B-widened boxes (A66/A80's 27 = unit-box artifact) — the whole
tier saturates exactly; U-row must buy slack from 28. D.SLAB explained to PI: (K) leaves = emptiness, robust
under dilation; (D) leaves = "sigma >= s-hat here", trivially satisfied by the dilated packing (side ~ s0) and
undilated displacement (lambda-1)|c| ~ 0.03 at m=3.85 >> rBasin; shell handled by dilation, deeper slabs need
KILLS that get easier with depth (Trump no longer fits).

Update 2026-09-03 (proof SEAM articulated to PI; A82 partial data; A83 dispatched): THE SEAM = how "s >= s-hat -
delta" becomes "s = s-hat". Regime 1 (below seam): plain kills at sides m <= s-hat - delta_LP — protected classes
+ trump5 become killable below s-hat because Trump (the aliveness witness) stops fitting; A82 on-disk: k4_08
eta 0 / -0.027 / -0.050 at s0 / s-hat-6e-7 / s-hat-8.4e-5 (dtau/ds ~600), k4_11 ~200; all LPs UNCONVERGED (600s
cap => eta optimistic; k4_11 s0 row -0.0125 where truth is 0 = the tell); extrapolated crossover (eta <= -1)
~2e-3 (k4_08) / ~5e-3 (k4_11); one cert attempt at s-hat-8.4e-5 (slack 0.05) FAILED depth 56 as expected. Regime
2 (above seam): s0 residual tree + Lemma-B dilation + BASIN — dilation is pure centre scaling, so the covered
configs lie on the CONTRACTION RAY z-hat - t*c-hat/s-hat; basin reaches down delta_basin = few e-4 (uniform
rBasin) / ~3.7e-3 (A36 per-coord) / ~6.5e-3 (A40). Proof closes iff delta_basin >= delta_LP (= D.SLAB made
quantitative). A83 (Fable 5.1, PI idea): anisotropic CONTRACTION TUBE basin Tube(T,r) along the ray in (t,w)
coords — contraction compresses all contacts (no hinge breaks, Farkas multipliers all favourable) so T should
certify far beyond isotropic radius; target T >= 1e-2; + Lemma SEAM w/ exact m -> t map + Lean-readiness note
for RigidBasin. Uniqueness at s-hat: basin equality clause + Theorem U at protected (D) leaves. A81: rung-1
U-row DODGED exactly with two images (28.000 again); rungs 2/3/5 = 27.667/26.962/25.045 (slack ~3 at rung 5);
emission at rung 5 running to measure r(d) under slack.

Update 2026-09-03 (PI floor question; decision: BOTTOM-UP window sweep = free record floors): A higher proven
floor (e.g. s-hat - 0.01) does NOT shorten the s-hat push — slab density is ~1/eta(m), so cost concentrates in
the last few e-3 below s-hat + the seam; the stratification-free measure ceiling is 3.83 (theorem), so any
floor above it IS the stratified window coverage restricted to a sub-window (circular as a shortcut). What a
floor buys: a RECORD LOWER BOUND theorem (s(11) >= 3.86 beats Stromquist 3.789 and our 3.82) = Track A-prime
hedge + decoupling. Free version: A57 G1 sides now ordered BOTTOM-UP (4: 3.833212, 3: 3.847780, 2: 3.862404
after side 1) and A82 extended to EMIT verified kills for all 16 protected classes + trump5 at those three
side values with dilation-shell-covering slack cores (Trump doesn't fit below s-hat => plain kills, large
slack) => each completed side = s(11) >= 3.833 / 3.848 / 3.862 theorem, zero extra cost. Headline trigger: any
protected class not killing at 3.833 (eta > -1).

Update 2026-09-03 (A83 closed done-success, 3c039c98): CONTRACTION TUBE WORKS. Tube(T, r) along the SLOT ray
(pins ride slot lines — the exact (D)-leaf pull-back; scale ray is wrong for pinned classes) certified: T = 0.0457
at A60's landing radii (r_c 1.6e-3, r_theta 2.1e-3), T = 0.0571 = WHOLE WINDOW at r = 6.5e-4, T = 0.062 at 2e-4;
binding contact = tangential validity of A22 pin row E3c2-7e3 (pin square 3 corner on free square 7 left edge),
beta never binds, pinning reserve 10-50x. Compression lemma: all 38 rows strictly compressed on the ray (min
gamma 0.129), Farkas identity; canary safe. Lemma SEAM: delta_basin(trump5) = min(T_tube, T_K(delta_pin)) =
0.0257 at delta_pin = 1e-2 (K-slack bound T_K = (2/3)*delta_pin*s-hat; 0.0457 at delta_pin >= 1.8e-2); exact
map t = s-hat - m, pins w = 0, free squares w <= r_land + 3.6e-7; NO B.2'' widening (D.S6 4.9% overshoot VOID in
tube route). Finding 1: hull-box interval-dependency artifact walled T at 0.02; pair-relative enclosures
(translation-invariant rows) sound (Opus clean-room 3-way) and doubled T. ACTION: A60's (K) leaves must carry
delta_pin = 1e-2 (planned 1e-4 caps tube route at 2.5e-4) — relayed. GAP REMAINING: protected classes NOT rescued
by the tube via s0-Theorem-U leaves (pin drift x 5.8 pocket caps T' ~ 3e-4) vs A82 LP crossovers ~2e-3-5e-3 (and
deeper when converged) => protected slab (s-hat - ~2e-3, s-hat - 3e-4) uncovered; resolution = A60-style
residual trees for the exact protected classes with TUBE discharge leaves (stratum-blind below s-hat; Theorem U
only needed AT s-hat for uniqueness) — to design after A81 closes (A81 interim: r(d) 0.84-0.87 on the coarse
rung-5 measure = identical to corners4 => retention intrinsic, pair route closed in any form). Lean delta for the
tube written: lean/tube_obligation_A83.md (~400 lines on A79's RigidBasin).

Update 2026-09-03 (A81 closed done-mixed a07a7aaf; A84 dispatched): LEMMA W'''' — slack does NOT buy
verifiability: coarse rung-5 k4_08 measure (slack 1.0, 63% mass at eta >= 0.05) has r(d) 0.84-0.87, identical
to tight corners4; retention set by frontier structure (atom handoff loci + box-meeting boundaries), tree
1e9-3e10 nodes; worse at beta > 0 (U-bonus layer). Corollary S-08 [T, exact]: Trump's k4_08 images have Sigma
m2 = 7 against ANY positively widened box => plain boosted value = 28 = threshold at every beta — closes the
plain boosted route for the whole one-short tier; both-image rows mandatory. Widened two-image ladder: 28 / 28
/ 27.667 / 26.962 / ~26.06 / 25.045 (gains accelerating 0, .33, .70, .9, 1.0); U-row slack is ultra-shallow
(inside 1e-4 zones, adversary at 3e-4): mixed-depth emission at rung 5 gives W2 = 27.000 exactly, rung 3 -> 28.
ALL GLOBAL-MEASURE ROUTES FOR THE PROTECTED TIER NOW CLOSED WITH NAMED LAWS. A84 (Fable 5.1): Lemma P-TREE —
the K1 protection only blocks single-certificate kills; an A60-style tree with (K) kills (Lemma B, delta_pin
2e-2) + (D) basin discharges (contraction tube, stratum-blind) proves the LOWER BOUND with NO exact-stratum
hypothesis (basin: sigma >= s-hat on (D) boxes; Trump has sigma = s-hat, not <); exact hypothesis only at
equality (uniqueness, already composed by A78 UniqueChain + Theorem U) => protected tier = 16 trump5-like
campaigns = a COMPUTE question. Pilot k4_08 (4 pins, budget 7) + one k<=3 (clear-corner crowding as cover
seed, A58); price the tier. A60: qualifying delta_pin 1e-2 AND 2e-2 (T_K crosses T_tube at 0.0179);
re-emission of ~599 cover (K) leaves priced ~25 CPU-h, runs behind deepen. A57: --side added (tree57 could
only certify at s0 before!), queue G1 -> G4 -> G3 -> G2 confirmed, cross-validated 273/695 at side 4.

Update 2026-09-03 (A60 delta_pin qualification): delta_pin = 1e-2 qualifies 2/2 but is NOT cost-neutral (6.8x
LP+cert; cert 5s -> 540s on one leaf) — re-emission of ~599 cover (K) leaves ~172 CPU-h ~ 1.8 desktop-days
(n=2, order of magnitude; 30-leaf batch to price). ETA LAW RETRACTED (A60's second overfit, n=16): corpus n=735:
eta <= -0.7 -> 494/494 PASS; (-0.7, -0.05] -> 78 PASS / 11 FAIL (33 PASS at exactly -0.5); eta ~ 0 -> 0 PASS. Only
safe reading: eta ~ 0 never certifies (tau >= budget refusal already handles). Policy: certify everything not
refused. DECISION: target delta_pin = 2e-2 (tube binds, delta_basin 0.0457; A84 measured same T law across all
protected pin sets containing BL(0,1)); price the 30-leaf batch at 2e-2; fall back to 1e-2 (0.0257) if much
worse; not-yet-emitted deepen/ladder/confinement leaves set to the chosen delta for free; cover re-emission runs
behind deepen. Shard 3 tail (141/191) queried: route cap-hitting children to deepen rather than serialize.

Update 2026-09-03 (A82 closed done-mixed): FIRST PROTECTED-CLASS KILLS — k4_08 + k4_11 cold-verified (frozen
verify_case.py depth 60, 4/4 gates) at side 3.833212, eta ~ -0.35 (certs/a82/). F0 [T exact]: aliveness cliff =
step of exactly one AT s-hat (m_fam 7 -> 6 when Trump stops fitting; s_fit = s-hat to 3e-8; corners4 never
alive). F1: eta <= -1 GEOMETRICALLY IMPOSSIBLE on the k4 tier at every side (exact 6-families => tau* >= budget-1)
— never price a k<=4 window campaign off eta <= -1 (A60's law is a zone-tree property, not a fixed-side one).
F3 [M]: operative gate = eps_geo affordability: certifies iff budget - tau >~ 0.21 (A56's 0.5 re-measured at
0.21 for k<=4); eta -0.05 FAILED (positional holes ~1.5e-3), eta -0.377 PASSED. F6: dtau/ds ~ 7.3-8 on k4 =>
plain kills reach up to ~s-hat - 0.025; tube reaches down to s-hat - 0.0457 (delta_pin 2e-2) => SEAM OVERLAPS
for Trump-image k4 classes. F5 hygiene: |eta| < 0.02 = noise, eta <~ -0.2 = evidence, certificate = proof; the
unconverged LP read 6.9875 where tau* = 7 exactly. F7: A82 certs use degenerate pins (shell ~1e-8) — delta 1e-2
re-emission needed for slabs, headroom ~0.17 after eps_geo (unmeasured; scan82.py --delta 0.01 ready). HEADLINE
NON-KILLS at 3.833212: k0_00 eta = 0.000 (root LP has no slack above the 3.83 pure-LP ceiling — k0_00 IS the
unstratified problem) and corners4 eta = +0.011 => NO record floor s(11) >= 3.833 from grid sides without
closing k0_00 (my "free floors" claim retracted; A57's bottom-up order kept, floor claim gated on k0_00). Tier's
genuinely hard classes = k0_00 (needs A58 clear-corner seed: all 4 corners clear => >= 8/11 corner-tied, + A71
stuck rows) and corners4 (non-Trump-centred; orientation coupling) — relayed to A84 for pricing. Scope: full
17 classes x 3 sides with delta-core certs ~50-100 h at 2 slots; emitchain82 (k4_03/06/05) + chain B (trump5 +
five k3) left running, resumable.

Update 2026-09-03 (A84 closed done-mixed, ef64aacc): LEMMA P-TREE HOLDS [T] — a zone-tree at s0 over the
MONOTONE pin hypothesis with (K) Lemma-B kills, (C) logic kills, (D) full localisations near a compatible Trump
image, composed with the contraction tube in the class's OWN direction (v = beta on the pin set, c-hat/s-hat
elsewhere; D4 commutes with dilation) excludes every packing containing S's pins on [s-hat - delta_basin(S),
s-hat) and makes every such packing AT s-hat a Trump image; the exact-stratum hypothesis is used NOWHERE on
the bound (only optionally at equality); H10-stuck = corollary; Theorem U NOT consumed (A83's T' ~ 3e-4 cap
void). LEMMA PD (pin-drift logic kill) [T+M]: slack pin cores give every ladder a residue floor = delta_pin
(k3_05 stalled at 0.0219, residue 96 -> 3862) unless "core meets the FULL drifted pin square at lambda=1 and
lambda_max" is a (C) leaf; with PD both pilots contract like A60 (ratio 3.6-4.5, land L24, same containment
numbers). A60's 2e-2 re-emission needs PD (relayed). Tube law tier-wide (19 pin sets, 42 certs cold 1008/0):
T = 0.0457/0.0574 iff BL(0,1) pinned else 0.1305/0.1680; anisotropic (6.5e-4, 2.1e-3) -> 0.0525 needs tilt
landing ~L29; whole-window trees at A_S=3/2 need delta_pin 2.5e-2. Pilot: k4_08 752 attemptable @ budget 6, 84
unkillable (2x41), P1 analogue PASS eta -3, contraction median 3.85, lands L24; k3_05 identical box-for-box
((D) geometry is class-independent per image). Cost ~3x (LP) / ~15x (cert) A60 per box; ladder kill queue is a
deepen queue (0/4, tau* = budget converged; unmeasured price term). TIER PRICE (§7): k4 image-bearing ~110-160
CPU-h each (+resister term), k3 ~200-300 CPU-h; k4_05 + corners4 have NO compatible image (shadow trees);
K0_00 DOMINATES: >= 100 desktop-days plain, ~25-30 with the stuck-only A58 corner seed (forces a
stratum_kill_selected re-split); CORNERS4: Lemma CC4 [T at s0] holds (each of 8 arm slot boxes met by >= 2
non-pin squares; only k5 superclass k5_16, killed) BUT an exact feasible square can meet 3 slot boxes via the
middle strip, so ">= 4 straddlers" does not close — finite case analysis ~2-10 desktop-days. Rough tier total
~50-60 desktop-days sequential on this machine; decision point for the PI (parallel/cloud vs sequential; k0_00
route worth more design before spending 25-30 days).

Update 2026-09-03 (PI pushback on k0_00 price; A85 dispatched on Fable 5.1): k0_00 = the unstratified root
problem — every kill is pin-conditioned so nothing transfers except stratum-blind tools (basin, tube, A58
crowding, teleport). A84's 25-30 desktop-days is a first quote missing three cuts: C1 D4 QUOTIENT (empty pin
set => full D4 symmetry; 8 images = 1 residue on a fundamental domain, ~/8; A67 R8 machine-checked); C2
TELEPORT REDUCTION (CC-2: a k0 packing with a FREE corner slot teleports into k1_00 => covered by k1_00's tree;
k0_00's own tree owes only K0-BLOCKED = all 4 corner slots non-free => A58: >= 2 non-simple squares per corner
box => 8 squares localised to 4 corner regions, 3 free); C3 the doubly-blocked seed as a COVER / possibly a
finite case list (corner-blocker pair geometry ~ corners4 straddlers). A85 = design + pilot + re-price; T4 =
the stratum_kill_selected re-split note. A60 status: Lemma PD adopted (recovers exactly the 46 logic kills the
2e-2 slack pocket costs; canary clean); 30-leaf batch 12/30: multiplier 4.5x, re-cert success 0.833 (17% fall
to deepen at eta ~ 0) => re-emission ~43 CPU-h + deepen for the 17%; anisotropic tube NOT reachable (centre
needs L39-40) => stay isotropic T = 0.0457 (seam already overlaps); sixth check-failed-read-as-negative
incident (errored Get-Process read as "finished") — rule: file-based wait conditions, verify a check produced
output before believing it.

Note 2026-09-03 (k0_00 nature + PI rotation idea): k0_00 is NOT an empty class — a rigid rotation of Trump by
~1e-7 rad is a k0_00 packing at side <= s0 (rotation kills all simplicity); target is strictly "no k0_00
packing BELOW s-hat"; the rotational ghost family near each image lies in the basin/tube. ROTATION
STATIONARITY (PI idea -> Lemma K0-ROT, relayed to A85): global rigid rotation is always feasible, so at a
minimiser the extremal wall-contact squares cannot all be tilted in the same rotational sense (extent
cos+sin decreases toward alignment) — mixed-sign or axis-aligned; a consequence of FJ (rigid-motion
direction). Uses: free (C) logic kill on boxes with same-signed extremal tilt intervals; prunes the
corner-blocker-pair case list (a clear corner crowded by two squares must be a mixed-sign "V"). Does NOT force
a corner square (Trump's own TL corner is a clear, doubly-crowded corner).

Note 2026-09-03 (PI: "derivative of s positive under small perturbations"): = the basin theorem at Trump
(Lean) and the A37 ATLAS (37 + A51-NEW-0 certified boxes, sigma >= s0 each) at other CPs. Atlas boxes are
valid DISCHARGE LEAVES (D') for any tree (incompleteness irrelevant; V >= s0 covers the whole window with no
dilation). Relayed to A85 with: run A04's optimiser restricted to the octagon family (k=0, D4-symmetric,
V-crowder seeds) FIRST — best k0 critical point's side sets k0_00's regime (>> s-hat => trivial LP slack;
near s-hat => a new CP needing its own Krawczyk/basin certificate). Stratification already handles all
corner-aligned constructions via pins; the octagon family is the only place an uncovered CP could hide.

Update 2026-09-03 (k0_00 status + drains directive): A85 CP search: NO k0 critical point below s-hat; best k0
optimum 3.887213 = s-hat + 0.0101 (ghost of A04 family #9, s_min 3.8874; one square 1e-3 off a corner slot);
V-crowder/octagon family DEAD at >= 3.95 (min k0 4.00); strictly flush-free >= 3.9057; all k0 landings
under-contacted (median 6 pair contacts vs Trump 14 — shallow valleys); rotated Trump drains back to k>0;
atlas covers 0/262 k0 optima (nearest miss 0.0047). A38 = the pre-stratification pin-free interior-first
tree pilot at s0 — k0_00 IS A38's tree; A85 re-running its cells on the A60 engine: level 1 0/3 (eta -0.12..
-0.34, unconverged, cert + eps_geo FAIL — matches A38), depth 2 (A38 oracle eta ~ -1.4) decides the price.
DIRECTIVE to A85: bake NEW CP discharge boxes (A36/A37 second-order FJ + interval Hessian, theta-coords, A37
format; trivial Lipschitz won't reach) around k>=1 families whose k0 ghosts sit near s0 (family #9 first) as
(D') leaves; rule: depth-2 LP kill if eta hits the ~0.21 gate, else drain at the nearest family, deepen only
where neither applies; window coverage of a drain is free (sigma >= s0 on the box). Remaining k0_00 space =
near-Trump ghosts (basin/tube) + ghosts of k>=1 families just above s0 (drains / depth-2 kills) + loose
valleys (cheap kills).

Update 2026-09-03 (A86 Lean wave 7 dispatched): the six non-gold on-tree nodes (C.K4TIER, C.A61, D.TREE,
D.LADDER, D.SLAB, D.S6) are compute-gated but need three campaign-INDEPENDENT Lean deliverables for gold:
(1) contraction-tube checker (A83's ~400-line obligation on RigidBasin; tube_sound; replay 42 tube certs),
(2) atlas-value box checker (A37 boxes + A85 drains; sigma >= V >= s0 => window-free discharge), (3) the
ZONE-TREE COMPOSITION THEOREM (cover invariance CI-1/2/3 formal; leaves K/C incl. PD/D/D-prime/N; mod-G;
ladder-localisation clause; Lemma P-TREE) discharging trump_residual + the tier piece of stratum_kill DOWN TO
leaf-certificate hypotheses; (4) window composition for C.A61 rows. After A86, the only remaining obligation
on those nodes = certificate replay (priced multi-day). A85 §4.6: 12 k0 ghosts within 0.02 of s0 (families 9,
8, 7, 11), drains centred at the GHOSTS (A37 3S-soft, trivial reach h = s_g - s0 = 0.010-0.012 >= 6x landing
radius, ~3 min/box, ~1 desktop-hour for all 12); family-centred basins unnecessary.

Update 2026-09-03 (A85 closed done-mixed, f7b1314a): k0_00 PRICE DOES NOT DROP AN ORDER OF MAGNITUDE.
Interior-first k0_00 tree at s0 (216-cell D4-quotiented root via Theorem A38.1 + d4_wlog, A60 engine,
(D')/drain leaves): ~3,200-7,000 CPU-h = 45-100 desktop-days at 3 slots IF depth-2 certs repair at ~85%;
>= 3e4 CPU-h if only first-pass certs count (measured f2 = 1/3). Cuts: C1 D4 = real /8 (already in);
C2 teleport = sound (K0-FREE [T]: corner box met by <= 1 square teleports into k1_00's MONOTONE hypothesis,
killed window-wide by k1_00's P-TREE) but ~0 on the frontier (coarse cells satisfy ">= 2 per corner"
trivially; free (T) leaves only, ~-10% on the (D) side); C3 corner seed as cover = DEAD (644 reach boxes, 33,656
pair boxes/corner, 2.9e16 four-corner nodes after prunes and /8). K0-PAIR: NO finite case list (same-sense
floating 2-crowds exist, 32% of pair boxes) — the advisor's "mixed-sign V" prune is UNSOUND locally; K0-ROT
needs the centre-height term (one-line form only for single same-height contacts), usable only as a
selected-form deep-node rule. Drains: 12 ghost-centred boxes ~1 desktop-hour. Pilot: level 1 0/3 (A38-G7
closed negative at depth 1), depth 2 3/3 decide (eta -1.0..-1.27; first cold PASS of a no-pin node at s0:
certs/k0_00/s1int_l2_l2_p114_010; two FAIL on 2-8 coverage holes, totals 9.977 < 10) at ~1000 s LP + 630-860
s cert per node. DECIDING CONSTANT = certification reliability at eta ~ -1 (coverage holes) — engineering.
WHOLE-PROOF COMPUTE ESTIMATE: k0 3.2-7k + tier 2-4k + A57/A60 1-2k ~ 7-13k CPU-h total; on this 20-core box
with commit now 130 GB, raising slot caps from 3-4 to ~12-15 cuts wall-clock ~4x; cloud spot ~$500-1500 for
everything, k0_00 alone ~$160-350 (216 root cells trivially sharded). Decision pending with PI.

Update 2026-09-03 (PI redirect on k0_00 -> A87 drain-flow, dispatched 5a7f1c97): PI rejected the volume-tree
frame ("remainder must have exploitable structure"). Structure: A85 CP search = NO k0 critical point below
s-hat (lowest 3.887213) and every k0 optimum UNDER-CONTACTED (flat directions => critical MANIFOLDS, all at
s >= s-hat + 0.01) => {s < s-hat} n k0 has no critical points. Argument DF-K0: drain lemma v3 as a FLOW —
non-critical k0 config has an s-nonincreasing feasible motion; no CP below s-hat to stop at => flow EXITS k0
(a square becomes simple) at s' <= s < s-hat into a k>=1 stratum, already killed => downward induction on
11-k, no tree. Obligations: (a) QUANTITATIVE drain (definite s drop or contact within bounded motion; D2
centroid-shrink; asymptote = the break point), (b) exit well-foundedness (drain only increases k; s' <= s),
(c) selection compatibility (stuck-but-non-critical impossible). SOLE HARD OBLIGATION H1: certify globally
"no k0 FJ critical point with s < s-hat" = A22 Krawczyk exclusion made global over the measure-zero critical
variety (branch-and-prune; most boxes excluded by a nonzero feasible s-gradient with no FJ solve; rank-
deficient FJ boxes = the >= s-hat+0.01 manifolds). Risk: H1 could be its own expensive tree — PILOT its
per-box cost vs A85's 45-100 days. If DF-K0 wins, the k<=3 protected classes (few pins) may inherit it.
Whole-proof compute estimate stands at ~1e4 CPU-h (dominated by k0 under the tree frame); cloud spot
~$500-1500; raising this box's slot caps (commit now 130 GB) cuts wall-clock ~4x — PI decision pending.

Update 2026-09-03 (A87 closed done-success, 48530f63): DF-K0 HOLDS in MinForm — with stratum_kill split
(A85 §9, A86 Composition.lean StratumKillMin) k0_00's obligation = "no global sigma-minimiser lies in
k0_00"; a minimiser exists (D1) and is FJ for every consistent selection (D3') => H1(s-hat) (no k0 FJ point
with sigma <= s-hat) kills k0_00 DIRECTLY: no induction on 11-k, no selection, whole window at once
(obligations (a) unneeded, (b)/(c) VOID: k>=1 strata are codim 3, drains never reach them; teleport induction
serves uniqueness only). Lemma F-LEAF: minimiser-only leaves ((F) Farkas, (B) D2, (R) K0-ROT, (S) stuck rows)
admissible in the k0 zone-tree under StratumKillMin. BUT H1 AS A COVER IS DEAD: 1,448 cells over the 262
optima + rotated Trump: ALL exclusions were sigma_min(cell) > s0 (trivial side bound); Gordan/Farkas/(a)/(b)/
(c1) fired 0 times on 74 sigma-feasible cells at ANY h; 114k per-selection Farkas tests, 0 kills; h* = Delta/
2.15 (pure s-clip law); rotational ghost alive to h = 1e-8; 10^62.7 cells at h = 1e-2. ADVISOR ERROR: "most
boxes exclude immediately by nonzero gradient" confused "forall z exists descent direction" with "exists one
direction feasible on all of B" — Gordan is exact for the gradient hull, fires only at the slack scale (zero at
s*); the critical set's MEASURE is the wrong complexity measure. FINDING: 13 of 14 k0 "optima" below 3.9 (and
rotated Trump) have NO feasible FJ multipliers — optimiser artefacts, under-contacted BECAUSE non-critical; the
"critical manifolds at s >= s-hat + 0.0101" premise is unsupported; genuine k0 FJ points UNKNOWN — FJ-polished
CP re-run ~1 desktop-hour [C]. H1 must be stated at sigma <= s-hat (algebraic), not s0 (rotational ghosts are
genuine k0 packings at s0, 2e-7 from z-hat). ROUTE: k0_00 STAYS ON A85's TREE (45-100 desktop-days at f2 ~
0.85), consumed in MinForm, optionally with F-LEAF leaves. A86 chore: all 54 tube certs replay clean in Lean
(~26 s each, 23 min corpus, ~16x Python).

Update 2026-09-03 (PI flush-free question -> A88 dispatched): flush-free program landed as A47 (thin branch
quantised to 2sqrt2+1, killed) + A50 (near-flush exclusion, rulers <= 5) THEOREMS; global flush-mandatory
I-L19 = conjecture, off-tree; superseded by stratification for k >= 1 (pins ARE flush contacts); residue =
k0. PI suspicion "ghosts walk uphill; relaxing lands on simple squares / octagon family at 4+" = DF-K0
(A87, proved) + measured (rotated Trump -> Trump or k=2 @ 3.886; V-crowders -> 4.00/4.24; 13/14 k0 optima
non-critical). Remaining obligation H1 (no k0 FJ point <= s-hat): cover route dead; PI's contact-graph
route = A88: count k0 FJ-SUPPORTING contact structures (A44 m >= m_min(d) floor; A31 filters; k0
structural filters: no corner-flush, L6 chain, per-wall <= 3, A58 crowding, A50 tilt rules) mod D4 x S11
with rigorous bracket; per-structure Krawczyk (rigid) / Farkas (flexible) exclusion cost from a 20-structure
pilot; H1-by-structure wins if census <= ~1e6 (A31 global was 1e30; A44 priced but never ran the FJ-restricted
census; A87 called it unpriced). FJ-polished CP re-run chore (Opus) running in parallel.

Update 2026-09-03: T5 fixed-corpus Lean replays COMPLETE 73/73 (K61 61, TRAP 6, P1 1, THMU 11; 9.79 h wall; axiom audit clean; zero Python disagreements) -> C.K61/D.TRAP/D.P1/A.THMU corpus_replayed=true (commit c25ff809). Replay pricing law: box count alone does not price a replay (10^14-denominator rationals cost 158 s for 424 boxes); median 32x Python wall. A88 census: k0 FJ-supporting structures ~1e11 graphs / ~1e36 decorated (rigorous >= 1e12) -> contact-graph route LOSES to the tree; k0 filters buy x1.011 only; findings: ruler cap (K0-3) window-dependent; A31 type menu omits corner-corner kisses (planarity false on ACTIVE graph with point kisses; support-graph counts stand). k0_00 route = A85 tree; compute-scale decision pending with PI.

Update 2026-09-03 (A89 dispatched): PI asked for ANY math lever to cut K0-BLOCKED; my ranked list: (1) tilt-floor
lemma for corner blockers at a k0 FJ point (A50 dichotomy tilt=0 or >=theta_0, extended using criticality from
DF-K0; deletes the near-flush ghost zone where LP kills fail) -> A89 (Fable 5.1); (2) criticality node test
(Krawczyk/Gordan) at 4-corner-deep tree nodes; (3) exact 3-square geometric oracle at leaves; (4) SOS/Lasserre
node certs (low probability). Rejected: Voronoi/cell wastage (exact zeros persist), Morse/degree counting,
projection/integral-geometry bounds, further symmetry (D4 used; measure certs label-free). PI wastage argument
(k1 -> k0 epsilon move raises wastage) = teleport K0-FREE where a corner slot is free; fails in K0-BLOCKED
(>= 2 squares per corner, "other 10 unchanged" unavailable); global version = DF-K0 with H1.

Update 2026-09-03 (PI diagnosis, confirmed): the 167 "certified k0 FJ points" (A87) are ALL K0-FREE by teleport
(0/167 genuinely K0-BLOCKED; o012 at 3.8972 = atlas fam13/14 (k1) lifted 4e-4 with a rattler whose removal frees
the TR slot); second-order test: 0 strict local minima, 166 flat strata (Hessian identically 0 on flexes; rows
linear in centres), 1 saddle; plateau ends reach k>=1 or K0-FREE for all 167. Corner occupancy in critical
configs is thin (633/668 corners one blocker, 21 two, 0 three). Lesson: the "k0" label by exact simple-square
count is NOT the proof's residue; always filter by K0-BLOCKED (teleport test, k0blocked87.py). Open structural
question (PI): does ANY FJ point exist inside K0-BLOCKED at any side? Directed CP search seeded in K0-BLOCKED
dispatched (k0dir87). Trump's TL corner is a genuine doubly-intruded critical corner (depths 0.168/0.155), so one
blocked corner CAN be critical; four at once is the question. Axis-aligned pairs cannot both intrude a slot.
A89: TF loaded floor = GAP (near-flush jam is loaded-consistent); TF-U proved (Phi-minimal selection: unlocked
squares have tilt exactly 0); JAM-0, MENU, ID proved; 4 shallow corners NOT dead by area alone (needs root cert);
self-jammed pairs 1.9%, jammed reach 2.386 ~ max; depth prune: no pair with both blockers intruding >= 0.5.

Update 2026-09-03 (A90 dispatched): directed CP search seeded INSIDE K0-BLOCKED (520 seeds): 0 FJ points at any
side; all flows exit by a blocker sliding away; infimum over each K0-BLOCKED basin attained only on the boundary
(corner becomes K0-FREE), sigma = 4.000 for 17/18, one basin 3.985. => Theorem NOCRIT target (A90, Fable): no FJ
point inside K0-BLOCKED; if proved, k0_00 dies with NO tree (DF-K0 + NOCRIT + K0-FREE + k>=1 kills). Boundary
case: Trump's TL corner is a locked 2-crowd (so single blocked corners CAN be critical; theorem must use all four).
A88 blocked-graph census: localisation inert at graph level (1.03e11), graph-fixed Krawczyk closes 0/20 (work moves
into the contact-type menu; Gordan never fires) — every count-based route to H1 is dead. A89-O3: certified NO
packing in [3.82, s-hat] has all four corners shallow at depth 0.3 (exact total 10.976 < 11); 3-shallow failed on
LP budget only (C1 symmetry, needs lp_time >= 5000).

Update 2026-09-03 (A90 verdict, A91 dispatched): NOCRIT in FJ form is the WRONG statement (Lemma BLIND: FJ
certificates ignore unloaded squares). Proved NOCRIT-SEL: at the Psi-minimal (least total corner intrusion)
sigma-minimiser every intruder's retreat cluster is anchored (far wall or another corner's deepening intruder);
constraints affine in centres => cluster translation is an exact packing (Lemma CLUSTER); wall-anchoring
columns >= 3 squares above 1+2sqrt2 (Lemma COL). Exact residue RES(4) = a FRAME: wall-to-wall monotone contact
columns of >= 3 squares in both axes through all four corner crowds (Trump's skeleton with slot squares replaced
by tilted 2-crowds); Trump's TL satisfies RES(1), so refutation needs >= 2 corners jointly (PI's "can't all
reach" argument, now at the right level). A91 (Fable): frame census — exact finite object, realisability in
[1+2sqrt2, s-hat], per-frame price; if small+cheap, k0_00 closes with NO tree. Paper outline drafted at
docs/paper/outline.md (process paper; PI/AI attribution; AI tendencies; hardware i7-12700K/20 threads/32 GB).

Update 2026-09-03 (A91 closed): frame census DEAD (L1 = 5.7e28 orbits exact; realisable ~1e38; 1.3e32 CPU-h; mismatch law 4th
face). CORRECTION: the Trump archetype is WALL-anchored under A90's full cluster (the "(I)-anchored" claim was a minimal-chain
artefact) => Lemma PLATEAU is NOT load-bearing (W-GEN proved with Q-independent corner weights). Residue not-RES(4) =
wall-anchored frames, killed only by geometry => k0_00 route = A85 tree (3,200-7,000 CPU-h), with (C-sel) anchoring rows as
optional per-node prunes (expected silent at the frontier). Depgraph has a k0 residue row (K0.* nodes). Compute-scale decision
remains with the PI; paper outline at docs/paper/outline.md awaiting PI notes.

Update 2026-09-03 (k0 pricing settled): the priced k0_00 route (3,200-7,000 CPU-h) is A85's INTERIOR-FIRST tree
(216 level-1 cells of T(s0) x [0,90], bisection b=8 on one conditioned interior square); it never branches on corner
pairs, so corner structure (K0-BLOCKED, realisability 33,656 -> 7,044 pairs, d2 cut, anchoring) changes it by <= 15
CPU-h. Its cost = 6,290 single-square LP+cert nodes (~0.5-1.1 CPU-h each); the 3e3-3e4 spread is the certified-kill
fraction f2 (0.33 measured first pass vs 0.85 assumed) = eps_geo/oracle engineering. Corner-first (C3) is the only
consumer of corner cuts: 2.9e16 -> 3.9e13 (realisability) -> 1.6e12 (d2 hypothesis) combos, still dead. Empirical:
anchored d2 frontier collapses to the floor (PI conjecture holds on the residue), packing barrier for K0-BLOCKED at
side 4.000002 (heuristic; "K0-BLOCKED => side >= 4" would kill k0_00 with 0.12 margin, unproved). Two axis-aligned
squares cannot both intrude one slot; per-corner min(d1,d2) <= 1-1/sqrt2 (argued). Lesson: measure which tree a
price refers to before claiming an idea lowers it.

Update 2026-09-03 (A92 dispatched, PI target): prove K0-BLOCKED => side >= s-hat. TRAP: K0-BLOCKED is an open condition;
exact K0-BLOCKED packing exists at 3.985 (s0115) with 1e-8 nicks, so the universal statement is no easier than s(11) >= s-hat.
Split: (S) substantive crowding (every corner's second intruder depth >= delta) => side >= f(delta), empirical f > 4 for
delta > ~0.02; routes: wall-strip counting, pair wastage at substantive depth, ROOT MEASURE CERTIFICATE with eight
depth-capable cores (budget 3) — cheapest if it fires; (N) nicked corners by Psi-minimal selection / Lemma PD pin slack /
JAM-0. Retracted: "barrier at exactly 4" (the A85-seeded search's 4.000002 is contradicted by the free-space record 3.985).

Update 2026-09-03 (A92 theory + A93 dispatched): k0_00 plan RE-BASED: K0-FREE + crowd-weighted certificate chain
C(delta, m_lo) (Lemma CW: one measure, mu >= 1+e on squares meeting widened corner boxes, total < 11+8e, checked by
TWO frozen verify_case.py runs; B-YES transport; chain ratio 0.4403) + Lemma SLIDE (forall-packings, modulo k1_00:
a nick costs its depth in side => at side m < s-hat every corner has d2 >= s-hat - m) => s(11) >= s-hat - delta_inf;
residue = shell RES-N of width delta_inf (K0-BLOCKED with a second intruder at depth in [s-hat-m, delta_inf)).
Theorem CEIL proved (min(d1,d2) <= 1-1/sqrt2 per corner; pair charge <= 1 so area can't close). The 4.000002
"barrier" = 1e-4 nick-floor artefact. LP sweep delta in {0.3,0.2,0.1,0.05} running (A92 chore, self-gated on 6 GB).
Depgraph: K0.CEIL/K0.SLIDE proved-prose, K0.CW/K0.RESN open (A92), RES4 superseded, TREE = shell fallback.
A93 (Fable) = Lean wave 8: CW soundness, SLIDE, CEIL, Theorem N composition + roster. Campaign snapshot: A57 G1 side
~30% of nodes done for k5_11/k5_16 (6 shards x ~192 nodes each, ~20-25 h/shard), cert_fail 10-15% -> L2;
A60 at isotropic tube 0.0457 (L26 landings), cover completion/deepen ongoing; A61 6 rows converted, rest in flight.

Update 2026-09-04 (A94/A95 dispatched): PI: "the empty corner should kill k5_11 quickly" => SLOT-CROWD generalisation:
in class S every COMPLETABLE slot (Young-extension slot) must be doubly intruded (CC-2 teleport + extension kills),
so A92's SLIDE + CW chain applies to every pinned class with budget 11-k: A94 (Fable) proves it and runs slot-crowd
certificates for k5_11/k5_16 (8 slots, 6 free) then the protected tier; if delta_inf < 0.0155, A57's sides G2-G4 are
unnecessary (only the G1 shell tree remains). A95 (Opus): parametric node certificates vs 4 fixed sides; k5_11
diagonal-reflection reduction; A57 time split. Monotonicity in s FAILS for class kills (R-anchored pins move with s);
it holds only via Lemma B dilation with slack (slab ~0.0155 at delta=1e-2) — that is why the 4-side grid exists.
A60 state: cover j0 done (1,557 rows; ~430 pass, ~43 fail), deepen + delta_pin re-emission + ladder remain (~1-2 wk).
A92 crowd LP: delta=0.3 PASS (eta -2.55), 0.2 running. PI will add LP slots once "in the home stretch".

Update 2026-09-04 (A93 closed, A94 theory): Lean wave 8 ALL FOUR theorems: crowd_sound (+ incidence form CW-S, r_max+1
runs), slide_crowd (SLIDE is two lines in Lean: translate the WHOLE packing away from the corner with the container
growing — no clusters; d2 form under K0-O1), CEIL, Theorem N (s_eleven_ge_of_chain: s(11) >= s-hat - delta_K is
CLASS-BLIND: needs only K0-O1 (k1_00's slab kill) + a chain of crowd certificates). stratum_kill now reduces to (i)
K0-O1 = the ONE tree the route needs, (ii) chain replays, (iii) ShellKill per class on (s-hat - delta_K, s-hat].
A94: SLOT-CROWD proved unconditionally for k5_11/k5_16 (4 usable slots each, k6 extension kills exist); counting says
nothing; multi-run certificates; A57 sides G2-G4 unnecessary iff delta_inf <= 0.0154 (G3/G4 iff <= 0.030; G4 iff <=
0.045). Protected tier: k4_03/06/08 crowd-void on the window (Trump's own crowds too shallow, CEIL-T ceilings
3.61-3.72); k4_11 chainable to 3.861; k4_05/corners4 need k5_11/16 first; k<=3 no usable slot. Lean waves 7+8 committed.

Update 2026-09-04 (A95 pilot -> A96): PARAMETRIC node certificates (A56 verify_param.py, 4-D window) cost 0.062 of four
fixed sides (0.024 on eps_geo-repaired leaves); 7/15 A57 leaves cover the full window in one pass; FAILs cover 99.2-99.9%
with slivers at two FIXED sides ([3.82,3.820056], [3.82708,3.827135]) = boundary degeneracy, curable per side. k5_11 has
the diagonal reflection unused (tree57 C1): sigma-symmetric nth=10 ladder removes 1,177 LP children over 4 sides.
A57 true remaining = 15.4 wall-days @5 workers (25.7 @3): level 2 (~16,400 children) is the larger half; eps_geo tail =
49% of wall for 8% of rows. A96 (Opus): freeze sides 4/3/2, parametric pass over all nodes + level 2, slivers, sigma
ladder. Crowd chains (A92 k0: delta 0.3/0.2 pass, 0.1 refused; A94 pinned: delta 0.05 misses by 1.2% of budget,
dtau/de ~10 vs break-even 8): true theorems with boundary above s0, NO window shortcut; k0 falls back to the interior-first
tree; salvage = crowd rows as sound per-node hypotheses at A57's lower sides.

Update 2026-09-04 (A96 leg 1): A57 converted to parametric certificates: measured 0.199 of ONE fixed side per node
(0.05 of four); k5_11 G1 class coverage 0.984 after 25 nodes; slivers were an s-resolution artefact of the single
global pass (one s-cell each) — re-running the SAME certificate on the sliver sub-window closes them in 0.6-3 s
(resolve96.py); A.LB382 does NOT close [3.82, 3.8200557] (monotonicity runs the other way). Sides G4/G3/G2 FROZEN
(A57 code/FREEZE_TAGS.txt; launch.ps1 gate binding). Sigma ladder built and C-checked (2650/2650 orbits), not yet
deployed. Re-projection: A57 remaining 12.9 wall-days @3 workers / 7.7 @5 (baseline 25.7/15.4); with sigma ladder
12.0/7.2. Level 2 emitted once (parametric), rate re-measure from a delta=1e-2 deepen shard pending. to_param96 widens
core_affine to the (P-aff) family (A57's to_param raised on every level-2 child). Launch drivers Start-Process-detached.

Ops law (2026-09-04, A92 incident): NEVER `git pull --rebase` / `--autostash` / `reset` on the shared working tree while
campaigns run — an autostash reset clobbered 48 live campaign files for ~2 min (restored from the autostash commit).
Agents commit their own paths, `git fetch` + plain merge/push only; the coordinator alone reconciles.

Update 2026-09-04 (A92 closed): (S) certified ONLY at delta = 0.3 (two-run crowd certificate, 0 holes) — but CEIL gives
d2 <= 0.2929 always, so the certified hypothesis is met only in a thin band (near-diagonal 45-deg crowds); delta = 0.2
FAILED certification (65/65 holes inside the family), 0.1/0.05 refused (at 0.05 tau = 11(1+e) exactly: all eleven
squares fit the dilated family fractionally). Net: the k0 crowd chain has ~no content on the window; residue RES-N(0.3)
= all K0-BLOCKED packings in (s-hat - 0.3, s-hat) with some d2 < 0.3 = everything => k0_00 stays on the interior-first
tree. Engine law: NO-family covers must use OVERLAPPING boxes (abutting seams are un-exemptable holes). Git incident
(autostash reset clobbered 48 live files, restored) -> rule: no rebase/autostash/reset on the shared tree.

Update 2026-09-04 (A94 closed, done-mixed): slot-crowd chain: NO certified PASS for k5_11/k5_16 (delta_inf >= 0.2 at the
s0 side; close-out cert at (G4,3.82] delta=0.1: runs A/B1 pass, B2-B4 FAIL with 31/32 exact holes — incidence rows
r >= 2 are unpriced by the row oracle: engine gap A94-G4). A57 sides no longer needed: NONE; A96 parametric pass is
the kill. Theory banked: SLOT-CROWD (unconditional for pinned classes), SLOT-SLIDE + SWEEP, CW-S, Theorem N-S, CEIL-T
(protected tier: k4_03/06/08 and trump5 crowd-void on the window; k4_11 to 3.861; k4_05/corners4 need k5_11/16 first).
Lesson: the crowd-certificate mechanism is sound and the LP nearly passes everywhere, but certification needs a row
oracle that prices multi-crowd incidence; without it the chain is theory only.

Update 2026-09-04 (PI corner-case work): corner-pair taxonomy for K0-BLOCKED = JAM (slot square + near-flush nick; 68/7,044
boxes; d1 = 1), BLOCK (same-grain edge-to-edge), WEDGE (both tilted 15-45; CEIL pair), OFFSET-UPRIGHT (axis-aligned at
offset g > 0.1 + tilted partner = TRUMP'S OWN TL corner type, 28.5% of pairs — was "OTHER"). Reach NEVER separates crowds
at box level (min pair reach_ub 2.001 > s0/2) — touchability vacuous; only the free-square (locker) budget bites at
pattern level (jams isolated => lockers must be free squares: 1-2 each measured, not proved). PI composite argument:
AREA budget (sum of corner charges <= s^2 - 11 <= 4.03; Trump spends it in one corner) x LOCKER budget (jams area-cheap
but locker-expensive) => cap on offset g in k0. Measuring exact pair charges (A25 dead-region machinery; cliff at
half-width 0.1-0.15) on 200 stratified pair boxes (charge85). One-corner-pinned crowd pilot (pin1crowd92) running;
verifier needs integer budget so crowd bonus counts in whole units (e >= 1/4). Astroid: the never-covered corner region
under all tilts >= theta0 is x^(2/3)+y^(2/3)=1 (area 3pi/32) — exemptable ONLY with a tilt floor (blocked by the jam).

Update 2026-09-04 (A97 dispatched): PI's WALL-LENGTH BUDGET: jams (slot square + nick) are area-free but need an on-wall
pusher (upright, width 1) => two flush unit widths on a 3.877 wall (per-wall <= 3 touching) => two jams cannot share a
wall; adjacent crowds squeezed toward compact near-corner types (A47's 0.85 cell / wedges) where the wastage lands.
A47's corner-majority composition was vacuous only because of the near-flush zero cell (= the jam); denying it via the
wall budget makes it a real inequality => offset cap for OFFSET-UPRIGHT corners in k0. A97 (Fable): Lemma WALL + the
composition + Trump canary per wall. Running chores: charge85 (pair charges by case), pin1crowd92 (one-corner-pinned
crowd certificate pilot; verifier integer budget => e >= 1/4).

Update 2026-09-04 (charge85 + A97): exact pair charges (A25 machinery, no cliff): Trump TL pair 0.98; JAM 0-0.34; BLOCK 0-1.23
(zeros exist); WEDGE 0.02-1.05; OFFSET-UPRIGHT rises with g then fans out (discriminator = wall-flushness near the corner);
4-corner area kill 5e-5; offset cap VACUOUS on area alone. A97 (done-mixed): Lemma WALL-F THEOREM = chord budget on the
line at 1/sqrt2 from a wall (toucher chord = 1/cos tilt; <= 3 touchers; tilt slack < 0.877; projection widths cos+sin are
NOT a budget); two jams nicked on one wall impossible; j <= 3 unconditional; j <= 2 only under P-ON (pusher on wall),
REFUTED by corpus (pushers float at 0.76-0.94: zero chord); SLIDE confines jams to m >= s-hat - 0.01; no offset cap
(floor 0.27 on neighbours); Trump passes WALL-F on all walls (left wall tight at 3). Composition NOT dead by area.
PI follow-up: Lemma FLOAT — a floating pusher strands the wall-adjacent strip beneath it (no unit square fits height
< 1) or forces a third wall toucher: couples the area and wall budgets (sent to A97). Pagefile init raised to 100 GB
(commit limit 132 GB, applied without reboot); A57 at 4 shards + A96 2 verifiers; LPs commit 3-6 GB but touch 0.8-2.2 GB.

Update 2026-09-04 (A97 closed + FLOAT): Lemma FLOAT [T] (via SHADOW): a jam's floating pusher strands >= 0.7071(1-L) area in
the strip beside the slot square (L = wall chord spent there) — every jam pays 0.71 area or wall length; sharp on the
corpus (3 jams strand 0.7071/0.7071/0.7064). Composition still NOT dead by area (jams <= 2.12 total; other corners can
charge ~0: BLOCK 0, WEDGE 0.023, OFFSET 0.121); max jams 3 (2 under P-ON); offset FLOORS not caps. One-corner-pinned
crowd pilot: crowd weights price at PAR (lift/budget ~1) — crowd weighting dead in all forms. Pocket exemption (k6
slot pockets exempt in k5 certificates; PI lunch idea = Lemma PD downward) being measured on A57 witness holes (pocket96).

Update 2026-09-04 (pocket96): slot-pocket exemption yield ~0 (0.3-0.6% of A57 holes; 0 FAIL nodes flip): A57's holes are
near-flush against PIN squares / neighbouring witnesses, not at empty Young slots. FACT: the k6 window rows were emitted
with pin tolerance 3.1e-8 (degenerate cores, tm 1/2^25) — no slack at k6; any downward pocket use needs re-emission.
Guard: pocket exemption must be stated as class membership (Trump's TR square sits exactly on k5_11's TR(0,0) cell).

Ops law (2026-09-04, A96): the A57 scaler was deadlocked by HANDLE INHERITANCE: `& powershell -File launch.ps1 | Out-Null`
keeps the pipeline open until every handle on the child's stdout closes, and the spawned tree57.py inherits it, so the
scaler blocked until the SHARD exited (one launch per wake-up; "launched" logged unconditionally). Fix: Start-Process with
file redirection, WaitForExit(90 s), read back the pidfile and verify a live tree57.py before logging success; log
launcher stdout/stderr on failure. A57Count counts sweepfails + deepen, not just tree shards (cap 6 = 4 shards). A96 now
owns A57's scaler. Exchange-and-relax measurement (exchange87) running: remove both intruders, place the slot square,
greedily relax the other 9 at fixed side to grow the void, test a unit-square fit exactly; Trump TL is the canary (must
fail).

Update 2026-09-04 (EXCHANGE): PI's non-rigid drain measured (exchange87): remove a corner's two intruders, place the slot
square, re-fit one square at the SAME side — succeeds at >= 1 corner for EVERY one of the 8 exact K0-BLOCKED packings
(21/33 corners), exactly verified; relaxation not needed (void-area relaxation hurts); no third meeter ever; margins
~1e-8 at side 4.0000 (grid infimum) => the lemma is TIGHT; Trump fails (largest inscribable 0.9823, rigid). A98 (Fable):
Theorem EXCHANGE per corner case (JAM: re-fit the nick partner shifted by its depth / into FLOAT's stranded strip; WEDGE/
BLOCK: the arm argument, B shifted outward by its intrusion depth; OFFSET-UPRIGHT: role swap) or the exact failure
configuration; exchange as an exact box-level leaf; if forall-packings, k0_00 = EXCHANGE + k>=1 kills (no H1, no
selection, no tree). A96 contention: none detectable at 4 shards (+5 others); throughput 16 -> 41 rows/h; level-2 cost
at delta=1e-2 trending 2.76x (n=14, 2 parents) — re-price at 30 rows / 4 parents; resolve96 clearing 85 partials.

Update 2026-09-04 (PI: Young FLOOD): recursive exchange = flood a Young diagram from a corner: each placed slot square exposes
2 completable cells; free cell -> place a removed square (deficit removed-placed drops 1); else grab the cell with fewest
intruders (remove them, place); bonus: untouched squares that can slide/rotate rigidly into a cell = free placement; WIN
when deficit = 0 (a k>=1 packing at the SAME side); obstructions: Young diagram at side < 4 holds <= 9 cells, far squares
never freed; Trump must fail. Measurement flood87 (Opus) running on the 8 K0-BLOCKED packings + Trump; A98 (Fable) told
the lemma's real form is the flood (potential-function route: perfect Young packing vs displaced squares' accumulated
grain-termination waste, A26). If proved forall-packings: k0_00 = FLOOD + k>=1 kills.

Update 2026-09-04 (PI: pinning graph): flood termination = induction on the PINNING GRAPH (= NOCRIT-SEL anchoring: P -> Q
when P presses Q outward; chains end at walls by W-GEN): removing an intruder releases every square anchored through it
(it retreats AWAY from the corner, emptying its cell = the flood's free-cell event). One lemma needed: RELEASE (removing
the deepest intruder of the least-intruded cell releases >= 1 square) unless the packing is a FRAME (chains route to walls
around all intruders) — Trump is the stall archetype. Never enumerate pinning graphs (A91: 1e28); induct. Sent to A98.

Update 2026-09-04 (A98 closed, done-mixed): EXCHANGE/FLOOD not proved, not refuted; framework exact and forall-packings:
Lemma TWO (a corner with exactly two intruders always exists), FLOOD-D (Young diagram D with N(D) <= |D| => k>=1 at the
same side), X(D) = N(D) - |D| (K0-BLOCKED <=> X(slot) >= 1), CAP (side < 4: every square meets the 3x3 block, X = 2, win
needs <= 8 cells), EXPOSE, FLUSH-JAM (jam stall = interlocked wall column propagating to the corner above), CROSS (wedge/
block: B + (d,d) has mu = 1 exactly), RELEASE-CL (release iff retreat cluster not wall-anchored). Corpus successes = nick
corners (B re-placed in its own footprint, exposure 0.0016); substantive corners stall. Residue RES-X = INTERLOCK (wall-
anchored frames + removal budget), realised at 2 corners of s0115 and Trump's TL; no four-corner stall known. RELEASE as
stated is the DEFINITION of the stall, not a smaller residue. Exchange leaf: 0% yield, silent at the frontier. If it held:
plain StratumKill modulo K0-O1-ALL. Bottom line: every route lands on the same object — substantive mid-band crowds /
interlocked frames; whether any exist below s-hat far from Trump is THE question, and only geometry (the tree) answers it.

Update 2026-09-04 (flood87 final via A98): recursive Young flood: 30/33 (packing, corner) cases convert at the same side, exactly
verified; 9 rescued at depth 2-3 (all at side >= 4); the only stalls = the 3.9855 record's BL/BR (interlock through the
4-m arm-cell overlap) and Trump's TL (deficit 2 = CAP). A96: resolver closed 82/82 partials to full window (median 4 s);
k5_11 0.982 / k5_16 0.995 coverage; level-2 cost drifting 1.5x -> 2.8x -> 2.4x, gate at 4 parents; projection 10.9/6.5
wall-days @3/5 workers.

Update 2026-09-04 (A96 re-price): level-2 child cost at delta=1e-2 = 2.36x A95's delta=0 figure (511 s/child over 3 complete
parents; per-parent spread 197/351/841 s; logic-kill fraction 19%); LEVEL 2 = 76% of A57's remaining wall; schedule 9.6
wall-days @5 workers (16.0 @3) vs baseline 15.4/25.7; sigma ladder now worth only 0.47 d unless applied to the D2 cover;
least-supported term = level-2 parametric verify wall (measured on level-1 nodes) — being measured on 20 real level-2
children; re-project at 6 parents. Resolver: 82/82 partials closed (median 4 s).

Update 2026-09-04 (supply85): the pin-supply gate is VACUOUS: every required lock/anchor zone of every intruder has an
intruder supplier (same-corner partner reaches it); free squares never needed; ~1e6 viable assignments per 4-corner box
combination; point poses kill 6%. So "3 free squares must satisfy all pins" does NOT constrain at the first-link level;
the only scarce structure is COL's >= 3-square wall-to-wall monotone columns coexisting across corners = frame
realisability = geometry = the tree. Structural probing of k0 is exhausted at every level tried (criticality, crowding,
reach, area, wall length, exchange/flood, pin supply); the tree (A85 interior-first; A96-style parametric emission)
answers the existence question.

Update 2026-09-04 (A99 dispatched): PI wants ~10x on the k0_00 tree. Anatomy: 216 level-1 cells (never decide), ~6,290
nodes at levels 2-4 under f2 = 0.85 (0.33 measured), ~1 CPU-h/node (LP ~1000 s + cert 630-860 s), priced at s0 only
(window: 4x fixed or 0.8x parametric). Three reductions being MEASURED: R1 failures certify by sub-box re-verification
(A96: 82/82 A57 partials closed in seconds) => f2 > 0.9 => levels 3-4 collapse (2-3x); R2 corner shallow/deep pattern
at the root with Lemma ID exempt boxes (6 patterns mod D4; 4-shallow dead) => level-1 cells decide? (2x+); R3 per-node:
cert --jobs 4, warm starts, GPU (2-3x). Product ~10x if all land.

Update 2026-09-04 (budget): PI target for ALL remaining local layers (Lean replay excluded, can run after announce) = ~400
CPU-h (~3 days at 6 slots). Ledger: A57 ~1,150 (-> 500-700 with sigma ladder on D2 + resolver on level-2 fails), A60/A61
300-500 (running), protected tier 1,500-2,500 (MODEL only, never piloted with the new pipeline — A100 pilot: k4_11 + a
k<=3 class end to end), k0 3,200-7,000 (-> 400-700 if A99's R1-R3 land). Engineering alone lands ~2,000-3,000 CPU-h
(~2 weeks at 6 slots); 400 needs a layer-deleting theorem (degeneration/flood) or the protected tier pricing far lower.

Update 2026-09-04 (residue map): docs/residue_map.md (+ docs/residue_map/gen.py, geometry-checked SVGs: trump, record_3985,
corner_cases, depth_axis, tree_root, flood) = the PI-facing map of what is left: blocks/prices table, Trump + protected
tier, the k0 reduction chain with each week's result's effect, the four corner cases + depth axis, the 3.985 interlock,
the tree anatomy, pending measurements (A96 level-2 verify; A99 k0 reductions; A100 tier pricing), and four candidate
theorems (interlock exclusion; protected-tier degeneration; two-corner interlock lemma with delta*; interior grain
rigidity). PI is looking for 8-10x via 1-3 theorems; wants ~400 CPU-h all layers. Update the doc as measurements land.

Update 2026-09-04 evening (A96 final terms): A57 = 80 CPU-days (~1,925 CPU-h): level 1 11.6, level 2 44.4, level 3 24.3
(1-proc days); 16 wall-days @5 workers (four fixed sides: 136 CPU-days, 27 wall-days) — parametric still wins 1.7x.
Measured: level-2 verify 506 s/child (2.5x level-1 mean; n=15, censored), level-2 LP 1.55x (70 children, 8 parents;
the 2.76x was one outlier parent), level-3 descent 6.8% (was an unstated 0). Levers on the dominant level-2 verify term:
sigma ladder on the D2 cover (k5_11 halves), resolver closure of level-2 partials (9 FAILs at 0.988-0.999 coverage).
The PI's 400 CPU-h all-layers target is ~5x below A57 alone as measured.

Update 2026-09-04 night (A96 follow-ups): A57 honest range 14-16 wall-days @5 workers. Verify tail = ONE 88-atom level-2
child (23% of level-2 verify wall); law: a completed FAIL (0.988-0.999 coverage + witness cells) resolves in seconds, a
TIMEOUT yields nothing => RAISE the cap for high-atom children, never lower it. Level-2 partials close via resolver
(3-11 s). Sigma ladder propagates to level 2 (k5_11 halves) = +2 wall-days net but needs a coverage reset of the live
class: recorded, NOT deployed. Machine at ~18 heavy procs / 82% CPU / 5.4 GB free phys is fine.

Update 2026-09-04 night (A100 interim): protected tier from real runs: k3_02 ~225 CPU-h (cert rate 0.75, resolver 9/9,
ladder lands level 24 in the tube, 59 (D) leaves; bottom of A84's model); k4_11 ~390 CPU-h = 2.4-3.5x model because
first-pass certification is 0.26: tau pins EXACTLY to the budget on 74% of level-1 cells at s0 (image fits at s0, A82's
aliveness cliff). Tier ~4,500 CPU-h (interim); all layers ~10,000 CPU-h (~70 days @6 slots) vs the 400 target.
LEVER 5 (non-theorem): the protected tier's cost is the seam (s-hat - 0.025, s-hat); 0.025 = certifier eps_geo
affordability gate (~0.21 slack) / (dtau/ds ~ 8); a certifier that verifies at eta = -0.05 shrinks the tier ~4x.
Ladder-node certificates do NOT emit through A96's parametric emitter (box centres outside the P-aff family) —
(D)-side stays fixed-side. A84's engine asserted 2 Trump images for k4_11; it has 1 (patched by A100).

Update 2026-09-05 (A100 closed): protected tier from real runs: k4_11 203 CPU-h (4.4% of cells run; cert 0.385),
k3_02 290 (cert 0.75); tier 3,500-4,200 CPU-h (band 2,900-6,300), ~2x A84's model; ALL LAYERS 5,900-13,700 CPU-h vs
the 400 target (15-34x over). ETA LAW EXACT (54 nodes): eta < 0 => certificate 25/25; eta = 0 (tau = budget exactly)
=> resister 29/29 => eta-gating is a free oracle (skip certification + eps_geo on eta = 0: 25-40% of cover legs).
The resister branch does NOT close: level-2 at delta_pin 1e-2 kills 1/16 children, tau stays pinned at the budget
(image feasible in the cell / fractional shadow at s0). Parametric route carries to protected (K) cover nodes (28/28
emit; resolver 20/20) but NOT to ladder/residue/NO-family nodes. Bug: resolve96 keys done on bare id (fixed in
resolve100 as (cls,id)); A84's class84 asserted |G_S| = 2 for k4_11 (it has 1). What removes the eta = 0 cells is a
theorem (the top slab (s-hat - 0.03, s-hat) of image-bearing classes), not compute.

Correction 2026-09-05 (A96): the eta law is one-sided: eta = 0 => resister holds (15/15 on A57), but eta < 0 => certificate
FAILS on A57 (576/730 = 79%); A100's 25/25 was 54 k4_11 nodes. A57's tree57 already refuses certification at tau >=
budget, so eta-gating saves 0 on A57; it applies only to A84's P-TREE engine (protected tier). resolve96 (cls,id) fix
ported; A57 ids embed the stratum name so no collision occurred. Cross-campaign rules from one corpus must be re-tested.

Update 2026-09-05 (PI shower correction): the 3.985 "interlock" record degenerates at the SAME side into k5_10 (BL[2,1]+TL[2]
canonical; A61 converted to full window, PASS margin 0.016; no Trump image => its min side is in (s-hat, 3.985]): align 4,5,6
(1e-4 moves; 6's TR "nick" is a 1e-8 TANGENCY, not a block), slide 10 into the cell below TL (0.38) and 7 into the TR corner
(0.39). Lessons: tangency != block (gap >= 0 bar); the degeneration move set needs wall-slides into cells freed by aligning
a tangent neighbour (K0-FREE at the cell level); corner-local flood stalls are NOT global stalls. k5 shapes table:
A53 name_to_shapes.json (rows along the wall; [1,1] = column). Note: importing docs/residue_map/gen.py re-runs figure
generation (side effect).

Update 2026-09-05 (degen87): global degeneration with the wider move set (tangency bar 1e-6; SIMULTANEOUS align + cell-level
teleport + wall-slides + exchange): 6/8 exact K0-BLOCKED packings reach a DEAD class at the same side; all 8 degenerate
(k 0 -> 6..11); the 3.985 record -> k=7 (TR[1,1,1]+TL[2,1,1], dead; sub-tuple k5_10); Trump: zero moves (canary). The two
failures (side 4.0000) stop at BL[2]+BR[2]+TR[1,1], not realisable at s0. Laws: greedy must be SIMULTANEOUS (one-at-a-time
stalls at move zero: aligning sq4 alone overlaps sq5); tangency bar 1e-6 (1e-4 loses moves). Thickness picture: uncrowded
cells = K0-FREE (unbounded, Lean); near-slot in crowded cells = PD slack (0.01-0.02) or SLIDE (side cost); substantive
crowds = the exchange conjecture. Every intruder test in exchange87/flood87/d2front/cases85 should be re-run at the strict
convention; the K0-BLOCKED corpus likely shrinks further.

Update 2026-09-05 (strict85): under the strict convention (intruder depth > 1e-6; equivalent to int(Q) meeting the open
(1-tol)-cell) the 3.985 record and polish12 are K0-FREE; the 6 remaining K0-BLOCKED packings are all at sigma >= 4.0000041
and sit at k0dir87's EPS_KEEP floor 1e-4 (artefact). NO K0-BLOCKED packing below side 4.000004 is known. 167 FJ points
unchanged. Pair census invariant at the strict bar (min pair depth 3.8e-5); SLIDE floors cut the corner-first frontier
35x (to 1.1e12 at G4) — corner-first still dead; the interior-first tree is unaffected. Trump canary passes.

Update 2026-09-05 (A101 dispatched): second Fable attempt on the flood: Lemma SNAP first = the eta-disturbance drain (PI theme:
the lab keeps meeting eta-disturbed simple squares — near-flush ghosts, nicks, tangencies — panicking, then finding they
drain): a near-axis square within eta of a completable cell snaps into it at the same side unless the cell is strictly
crowded ("snap or crowded" dichotomy); snaps must be SIMULTANEOUS; box-level (T) leaf for A57's near-flush-against-pin
holes (pocket96 tested empty slots, not stacked cells). Then Theorem FLOOD under the strict convention + simultaneous
moves (empirical boundary side 4; k0dir2_87 floor sweep pending). Machine was half idle (CPU 47%): A96 told to run 6
A57 shards + 3 verifiers under the 3 GB RAM gate.

Update 2026-09-05 (certfail census -> docs/cert_failures.md + docs/cert_failures/gen.py): 1,072 failed nodes / 9,910 witness
boxes / 246.9 h wall across 9 sources, 8 categories with one exact figure each. MID-TILT (15-45 deg) = 58% of boxes:
interior (D, 38%, 31.5% wall) + wall-adjacent-not-corner (H sub-band, 1,880 boxes) + corner poses (C) ~ 55% of wall — no
drain. ETA = 0 refusals (E): 479 nodes (A57 292, A60 148, A100 38), 23% wall, never reach certification — missing
class-level drain. F (ladder sliver) + G (timeouts) = 17%, plugged. A+B near-lattice = 1%, close ZERO nodes (SNAP's
box-level yield on certificates is bounded by this). The 15-30x must come from two holes: mid-tilt near walls/pins, and
eta = 0. 75% of failed nodes are single-category.

Update 2026-09-05 (A101 closed): SNAP PROVED in destination form: a square within eta of a cell snaps at the same side IFF no
other square meets int C (= teleport_packing at the cell; the swept region is irrelevant to soundness); MULTI (simultaneous
snaps valid iff target cells pairwise disjoint and no untouched square meets a target — movers may crowd each other's
cells, which is why one-at-a-time stalls); SHELL: any crowder of a disturbed square's cell is a GRAZER (depth <= (1+sqrt2)
eps); SNAP-SIDE. Leaf yield on A57 = 0 (holes are FLUSH AGAINST PIN ROWS displaced along the pin; >= 4 unlocalised squares
at every node so the destination condition never certifies). FLOOD not proved: exact stall = CELL-INTERLOCK (X(T) >= 1 for
every disjoint cell set containing a corner cell, any of the 4 lattices; |T| <= 9 below side 4); record cell-interlocked at
BL/BR; Trump admits no move. Floor sweep (partial): lowest strictly K0-BLOCKED side 4.0000016 at floor 1e-6, 4.000023 at
1e-4 (none below 4). Dynamic moves outside the census (A101-G2).

Update 2026-09-05 (holes chore): the mid-tilt hole = 564 distinct placements (5,695 boxes are clusters of 8-24 terminal
boxes): motifs pin-flush 163 (square resting on a PIN CORE, inside the drawn pin by exactly the slack 0.014 = 0.01*sqrt2),
free-floating 183, wall-flush 132, cond-flush 86. NO fractional-pinwheel signature (4/164 nodes) — the LP's holes are
single LEANING squares, not 2x2 blocks. ETA = 0 = the PIN-CONTACT stratum: eta = 0 rate 42-100% when the conditioned
box touches a pin (gap < 0.02), ~0% far from pins; concentrates on Trump images where the class has one; propagates
(32% of children again eta = 0). UNIFICATION: both holes = a tilted square in contact with an axis-aligned pin / wall /
the other localised square; slack cores make it cheap for the adversary; local charges tiny (A45). Drain target = the
leaning square. 12 motif figures added (docs/cert_failures/fig_D_16-19, fig_E_20-27). Block-first pilot (block96)
running on 20 failed k5_11 nodes.

Update 2026-09-05 (A96 six-shard read): level-2 LP cost SETTLED at 1.11x A95's figure (529 children / 53 parents) — the
2.76x / 2.36x / 1.55x readings were small-sample noise (law: do not headline a per-child cost below ~50 parents);
level-2 verify 545 s/child (n=26, 2.06x level-1 mean); level-2 descent 11.3% => expansion factor 0.91/level (level 1:
1.44) — level 3 = 41% of A57's wall; level-3 descent is the highest-value unknown (depth-3 deepen probe requested).
6 shards: +14% throughput for +50% shards (busy=17 median +20%) — hold at 6. Schedule 92 CPU-days = 18.5 wall-days @5
(fixed sides 125 CPU-days; parametric wins 1.35x). Pass: 458 nodes, k5_11 0.978 / k5_16 0.994.

Update 2026-09-05 (A101 + floor sweep): A101 DONE — SNAP proved in destination form (= teleport at the cell; MULTI,
SHELL grazer bound (1+sqrt2)eps, SNAP-SIDE, OFFSET); SNAP leaf yield on A57 = 0 (holes are flush ALONG pin rows, >=4
unlocalised squares per node; existential-filter law again). FLOOD OPEN: exact stall = CELL-INTERLOCK (no disjoint
cell set with overhang <= free area, all 4 lattices, <= 9 cells below 4). RETRACTED: "no strictly K0-BLOCKED packing
below 4.000004" — k0dir2_87 floor 1e-3 found strictly blocked packings at 3.9907 (0.8% of seeds; 3 of 4 second meeters
at exactly floor depth => grazer-blocked eta-disturbance of a K0-FREE packing). m*(delta) is floor-dependent; every
value found >= s-hat + 0.11. Law: a search floor bounds what the search can SEE, not what exists — lower floors miss
grazer-blocked packings (1e-6 floor with 300 seeds never found the 3.9907 basin).
A99 supervisor chain apparently died after R2 (no process, no FINAL_DONE); R2 pattern screen: shallow-pattern level-1
cells die (eta -1..-2) but the all-deep branch keeps A85's whole tree — branching costs x15 in cells, cannot beat A85's price.

Update 2026-09-06 (A99 landed, commit 99985b76): k0_00 tree v2 pilot. R1 (resolver on A85 FAILs): 0/12 close — deeper
uniform bisection RAISES hole counts; A85's FAILs are LP row-generation failures, not verifier artefacts; f2 = 2/3 with
eps_geo (A85's published 0.85 was optimistic). R2 (shallow/deep branching): exact x15 in level-1 cells (D4 stabiliser
count), tau drops ~1.06 but minmass halves => LESS converged LP, not deader nodes; zero kills claimed. R3c (parametric
emission of A85's interior cells): works — 1 node PASSes the frozen 4-D verifier over [3.82, s0] in 123 s (+5-7% per
node vs x4 for a side grid); corner-crowd nodes (t-grid cores) cannot be emitted; cover-invariance transport to the A38
cover is an open obligation. STACKED window-valid k0_00 projection: 9,300-21,700 CPU-h (2.9-3.1x WORSE than A85's
published 3,200-7,000 because f2 measured 2/3 not 0.85). With R2: 138k-323k. All-layers total now ~15k-35k CPU-h vs the
400 target. Lesson: the "10x from stacking three reductions" was never there; only the parametric window (3.8x vs sides)
is real.

Update 2026-09-06 (PI drain of the 3.9907 record — VERIFIED EXACTLY): PI read the figure and saw square 3's three
contacts (sq 2 below, right wall, sq 8 upper-left) all permit a CCW rotation; rotating 3 by 1.31 deg about its centre to
axis-aligned is collision-free (2000-step SAT sweep), lifts its vertex out of BR, BR drops to ONE meeter (K0-FREE), and
simultaneous snaps of 1,2,3,5,6,7,9 give a VALID packing at the same side with k = 7 (BR staircase [3,1] + TR row [3]).
So the "first strictly K0-BLOCKED packing below 4" is a k7 packing wearing a 1.3-degree tilt on one square. Lesson (again):
strict K0-BLOCKED with floor-depth second meeters is a ROTATION eta-disturbance, not just translation — SNAP's
destination form covers it (rotation about centre to axis then teleport). Third time the PI's spatial read beat the
census (3.985 record, interlock, now 3.9907). Files: attempts/A87-drain-flow/{code/pi_drain_3p9907.py,
results/pi_drain_3p9907.json}, docs/residue_map/strict_3p9907_drain.svg.

Update 2026-09-06 (block96 landed): block-first (pin the 2x2 grain as one rigid object) on 20 k5_11 nodes closes 0/20;
tau integral in every LP (0 kills / 1-2 survivors) — the LP degenerates to "does an 11th square fit"; survivors are the
eta=0 stratum near-axis (0-5, 85-90 deg); NO pinwheel signature (de-duplicated 2/14 nodes have same-tilt pairs, no
triple); mid-tilt 2x2 blocks do not fit beside k5_11 pins. Cheap (+12-40%) and worthless; no-block branch uncovered.
Law: de-duplicate witness placements before reading a signature (verify_case emits one witness per refined sub-box; raw
count gave 93% "block-shaped", de-duplicated 14%).

Update 2026-09-06 (A102 landed, 3e4929db): rigidity drain on all 12 strictly K0-BLOCKED packings + Trump. 10/12 drain
to k>=2 at the same side (both sub-4 ones -> k=7; largest d2 drained 1.02e-2); non-drainers floor-1e-4 (4.0000044) and
polish12 (4.0000001) are first-order screw-FREE yet jam after ~1e-4 deg on a square whose gap is just above the contact
bar (1.4e-6, 3.1e-5). Trump rigid (canary PASS). LAW: the contact-torque SIGN test is NOT the rule — 21/31 floor-depth
second meeters are pinned and first-order freedom does not predict the drain; the rule is all-or-nothing ROOM
(retraction fraction 1.000 or ~0). Obstruction for theory: contact set at a fixed tolerance does not determine finite
motion -> need a finite-motion / room criterion, not a torque filter on the contact graph (this also undercuts the
"fold torque-lock into the frame census" idea unless near-contacts at ~1e-4 are counted as contacts). Pins are
square-square (32/33). Empirical threshold for PI's "blocked+rigid impossible" conjecture: rigid blocked packings exist
at 4.0000001; none below 4 (n=2).

2026-09-06: A103 (Fable, NOROOM) dispatched on PI's go — target: no K0-BLOCKED packing at m <= 3.9, else DRAIN(W)
(existence of a k>=1 packing at the same side, not a motion), else exact drawable obstruction. Ingredients: Lemma ROT
(rotational retreat), Lemma CHAIN (wall-to-wall chain of 3 spans 3 < m, flush far end => near end intrudes >= 4-m, far
end sits in the slot => simple or an intruder), corner regions [0,1+sqrt2]^2 vs 3 free squares. PI framing that fixed
my confusion: above side 4 the question is vacuous (grid), so the A102 non-drainers at 4+eps are irrelevant; the
theorem is an EXISTENCE statement on the window only.

Update 2026-09-06 (A103 landed, f7730e98, done-mixed): NOROOM at 3.9 OPEN; DRAIN(W) reduced EXACTLY to Conjecture
LOCK-FREE(<4): every K0-BLOCKED packing at side < 4 has an intruder that is not HELD (held = no single-square rigid
motion, translation or rotation, opens its active rows and decreases its corner depth; exact first order, Gordan form).
Lemma ROT [T]: at the weighted-Psi minimiser every intruder is held (PI's one-signed-torque rule is its corollary).
With LOCK-FREE: k0_00 = window kills + one leaf, no tree. Corpus: 0/12 blocked packings held at all 8 intruders; every
one has an unheld SECOND meeter; Trump held 5/5 (canary) => proof must use >= 2 blocked corners and fail at 4+eps.
Proof shape named: eight contact cones jointly along one wall of length < 4 with WALL-3. Negatives: CHAIN-AX exact only
for axis-aligned edge-to-edge columns (Trump's column has tilted middles, third case) ; corner-region count vacuous
below 4.83 (Trump's sq7 braces all four corners); NOROOM-LOCAL near Trump proved but eps unquantified/circular.

Update 2026-09-06 (A96 depth-3 probe final, c7155224): level-3 descent 4/42 = 9.5%, f3 = 0.76 (interims drifted 0 ->
0.30 -> 0.67 -> 0.76 as parents landed — never headline an interim rate), per-child 292 s (no escalation). Descent is
CLUSTERED (4 of 6 parents 0/8, one parent 3/8): a branching process with rare fertile nodes, not uniform geometric.
Tail fitted: A57 = 23-26 wall-days @5 (rho 0.63-0.86), 34 if rho=1; terminates in every case (no 10x divergence).
Dominant unknown = fertility persistence; fertility probe (deepen the 4 alive level-3 children) approved and running.

2026-09-06 PI insight (banked as a project law): A57's FERTILE nodes are fertile because their box contains a SHADOW
(a local side-minimum just above s0, or Trump itself in protected classes); B&B closes around it taking smaller bites
and children without the shadow die — that is the asymptote the PI warned of; termination needs a finite certified
volume (Morse/basin certificate, A63's tube machinery: rBasin=3/2000 for Trump) around each shadow, after which the
tree covers only the complement. Dispatched: A104 (Opus: grid closure + m_lock search), A105 (Fable: LOCK-FREE(<4)
wall lemma), A106 (Opus, read-only: alive-box diameters vs shadow slack; basin-vs-tree verdict).

2026-09-06 PI read the A57 LP support and named the shadow: k7 packing = BL L-shape 3 + BR stacked 2 + TL 1 + TR 1 +
4-square PINWHEEL at one tilt (48.435 deg); direct SLSQP gives s* = 3.886746 = s-hat + 0.0097 (docs/residue_map/
pinwheel_k7_shadow.svg, gen_pinwheel_k7.py). A57's fertile lineage Y0036 is this shadow (LP dual support integral,
5 placements at weight 1, worst overlap -0.015 vs a pin under shrunken cores). k7 is killed AS A CLASS (exact slot
squares), but k5_11 packings NEAR the k7 minimiser (TR and BR(0,1) squares slightly off-slot) are in k5_11 with side
~3.8867 > s0 — the tree must resolve the 0.0097 slack; the bottom-up fix is a basin certificate around the k7
minimiser. Symmetry transport (mirror a dead box across the class's diagonal symmetry) covers 0 alive boxes: the
residue is itself mirror-symmetric (two mirrored shadows), so no free halving. The LP dual support IS the shadow
(PI: "grab the phase-space point near the dead end of the LP search") — draw it directly, not the hole witnesses.

Update 2026-09-06 (A105 landed, 6ff1d3a9, done-mixed): the ONE-WALL lemma is FALSE — record_s0115's bottom wall
(3.985) and floor-1e-3's left wall (3.9907) have both corners blocked with all four intruders held; at 4.08-4.11 two
adjacent walls are fully locked. Stands: Conjecture LOCK-FREE+(<4) (some intruder not LOCKED = held AND wall-held) =
what RES-LOCK = empty needs. Proved: ROT-W, LINE, PUSH-LINE (held-and-pushed <=> contacts' resultant = corner-ward force
along a line through the argmin set). HOOK family: wall-hugging nick + tilted carrier through its inner corner, kinds
alpha/beta; Trump's TL crowd is a beta-hook. Theorems HOOK-alpha/beta: two same-kind hooks on one wall need m > 4
(tilted-grid shell side 2(1+s)(1+c)/(s+c) >= 4). Prop HOOK-beta-alpha: the MIXED pair fits at m = 2+(2-s)/c+tan(theta/2)
< 4 for theta in (0,30 deg) — reproduces the 3.985 record's side to 6 decimals; needs a third contact (HOOK-W).
Residue: the four-corner PUSH-LINE count. Generalises: HOOK theorems are one-wall statements with 4 = the grid side
(-> ceil(sqrt n) for general n).

Update 2026-09-06 (A106 landed, 66c62e1e): basin switch does NOT apply to A57 — none of the 145 open L2-L4 boxes
contains a local minimum (box-constrained min on the boundary; released flow leaves; median distance to a shadow
square 0.32 = 9 r_basin; best attainable side in an alive box s0+0.013, median s0+0.061). Boxes are alive because the
LP relaxation (inscribed cores a=0.36-0.48, pin slack 1e-2) cannot see the slack, NOT because they hold near-solutions.
Shadow floor = PI's k7 pinwheel 3.886746 (certified endpoint), r_basin 0.035. LEVER: pinguard tests inscribed cores, not
unit squares — direct pin-separability test kills 122/516 open boxes (23.6%, all 4 open L4) at 0.6 s each (~9-13 CPU-days
of tail); A96 asked to make it sound (interval over whole box + pin slack core) and price it as a leaf. Law: an
"alive" box in a core-relaxed LP tree need not contain anything — check what the box CAN reach before building
basins around what it cannot.

Update 2026-09-06 (A96 fertility probe, 5fd0e287): 0/4 parents fertile, 0/30 alive at level 4 — fertility NOT
heritable (3 of 4 parents were siblings of the one fertile L3 node; all died). Termination mechanism: logic-kill share
rises with depth (32% L2 -> 60% L4) as smaller boxes clash with pins; cost flat ~290 s/child. Factors 1.44 -> 0.91 ->
0.76 -> 0. A57 schedule ~20 wall-days @5 (27 at 95% upper bound); tree terminates by measurement.
A106's pin-clash prune is UNSOUND as written (sampled minimum of overlap = upper bound on the true min; a positive
sample does not prove emptiness) — 122/516 is an upper bound on yield. Approved route B: tighter common-inscribed core
inside the existing KILL-BY-LOGIC leaf (no new Lean), positive control on the 601 known logic kills first, then
pre-filter on new children only. Law: a search that fails to find a separating pose proves nothing; emptiness needs
an interval/exact bound over the whole box.

Update 2026-09-06 (A96 route B, 761513f5, DEPLOYED as pre-filter on new children): tight common-inscribed core
a = (1/2 - h*M_c)/M_t (old bound assumed 45 deg in every tilt range) enlarges cores 0.7-10.9%, contains the old core
by construction; positive control 583/583 (corpus has 583 known logic kills, not 601). Yield: 70 new kills on 1,536
open boxes — 1.8% L1, 8.2% L2, 17.9% L3, 11/12 L4. A57 schedule 19.6 -> 13.3 wall-days @5 (-32%, lower bound); 72% of
the benefit at level 4. Law: the logic leaf's core bound was the loose part of the relaxation — check the constants
of a sound leaf before adding a new leaf.

Update 2026-09-06 (A104 landed, af6456e1): below side 4 the closing iteration (step to first collision, pin new rows,
re-polish, repeat = follow the contact manifold) ALWAYS frees a corner: 443 endpoints + 12 corpus, zero fully-held
blocked packings below 4. Fully-held ones first appear at m_lock = 4.000237 (4.001525 with full Gordan certs). EVEN
THE GRID IS LOCK-FREE: the exact 4x4 grid has one meeter per corner; the eps-grid is blocked only by an O(eps) poke
that Lemma ROT's step removes; A103's "jams on a near-contact" was a STRAIGHT-LINE artefact (following the manifold
the square rolls past; polish12's nick retracts 100%). Lock anatomy: 3.3 square-square + 1 wall row per intruder —
locks are held by SQUARES, so a wall-length budget alone cannot prove LOCK-FREE; missing step = at side < 4 the crowd
arms cannot supply 3+ square rows to all eight corner members. Law: test motions along the contact manifold, not
straight lines; near-contacts that block a straight step are rolled past.

Update 2026-09-06 (A107 landed, 2faaa1a1): docs/shadows.md — 53 distinct shadows explain 1,260 of 1,566 alive-at-LP
nodes (A57+A60+A61); 306 fractional/unexplained. S01 = side exactly 4.000 (620 nodes; "has room", not nearly
feasible); S02 = PI's pinwheel 3.886746 (267 nodes, carries the deep tree; f1-top wall binding; idle strut blocked
at 2nd order only); S07 = NEW 3.885618 = s-hat+0.0085 on trump5's skeleton (Trump's six slot squares + five free at
44.88 deg) — numerically only; A108 dispatched to certify exactly and compare with Trump (basin or separate min).
Laws: a shadow is a VALUE of s*, not a point; LP rows are configuration cells (pitch 0.19) so integral-component
disjointness test is >= -0.21; draw the LP support directly at every fertile node (PI's rule) — it worked.

2026-09-06 PI read the gallery: S07 = Trump with f0's corner no longer poking into the gap between BL(0,2) and BL(0,1)
(snapped Trump); S01 has a FREE CORNER -> already killed by the teleport lemma into a higher-k class; S03's free
squares essentially simple (SNAP); S04's f0 teleports to BR(0,1); S05 = S07's pinwheel upside down; S06 = the optimal
n=5 packing (2+1/sqrt2) with a unit band = the s(10) optimum 3+1/sqrt2 (a 10-square shadow). PI DIAGNOSIS (banked as
the next lever): "the issue is turning teleport-lemma kills into kills in phase space" — the node LP does not know
SLOT-CROWD; A94's crowd certificate (CW-S, 1+r_max verifier runs) exists but was only tried at the ROOT (failed at the
s0 side); A109 dispatched to test SLOT-CROWD rows at the NODE level on the S01/S03/S04 alive nodes.

2026-09-06 00:37 PAUSE (PI directive): all long-running LP campaigns paused to free compute while A108 (S07 certify)
and A109 (node-level SLOT-CROWD rows) run. A61 stopped by me (resumable; attempts/A61-window-stragglers/PAUSED.md);
A57/A96 (6 shards, 2 deepens, param96 x2, resolver, sweepfails, verifier children) being stopped by A96 with a
PAUSED.md + resume recipe. Do NOT restart anything until the PI lifts the pause.

2026-09-06 00:45 A57/A96 paused by A96 (e4d87b39, attempts/A57-shadow-trees/PAUSED.md): 18 processes stopped, scaler
FIRST (it relaunches shards). Ops laws: (1) a pause that wants to keep in-flight results needs a SENTINEL FILE the
driver checks between launches, not a kill — param96 writes a node's row only after reaping its child, so killing the
driver discards a clean verifier exit; (2) nothing reaps certify children whose tree57 parent died — an orphan burned
11.3 h; check for orphans after every restart. Resume = copy-paste block in PAUSED.md (launch.ps1 for shards; re-run
select96.py before the A96 drivers; tight core on by default). State: scoreboard k5_11 0.978, k5_16 0.991.

Update 2026-09-06 (A108 landed, 310849f9): S07 CERTIFIED EXACTLY — an 11-square packing of side s* = 2 + 4*sqrt2/3 =
(6+4sqrt2)/3 = 3.885618083 (= s-hat + 0.0085345), all coordinates in Q(sqrt2), all five tilted squares at EXACTLY 45 deg;
class k6_07 = trump5 + BL(0,2) (Trump's disturbed upright put into its slot). Separate local minimum from Trump:
straight-segment barrier +0.032, best common-tilt path crests at 41.60 deg, +0.0011 over S07. Not first-order rigid
(f3 rattler, 3 flexes); Fritz-John fails at first order STRUCTURALLY: a 45-deg square touching a wall has zero
first-order torque (half-width maximal at 45) — local minimality is second order. Second-best known packing of 11.
Traps: perturb-and-re-minimise WITHOUT a trust region walks out of the basin to s-hat (SLSQP repairs infeasibility by
leaving); A107's numbers for S07 (44.88 deg, 8 flexes) were drift artefacts. Covering kill: k6_07 PASS at s0
(A53/A54); S07 sits 0.0085 above the window so it is irrelevant to the proof, relevant to the paper (and to n=12+:
the 45-degree grain is a closed-form family).

2026-09-06 ~01:00: A61 RESUMED on PI directive (campaign61 pid 45764, 8 strata: k5_02/03/05/12/13/14, k6_21/27; heavy 2,
jobs 3); A57/A96 STAY PAUSED. Window status (A56 scoreboard): k6 29/32 full, k6_21+k6_27 open whole window, k6_07 open
band (3.827, s0], k6_23 sliver 8.4e-5; k5 (excl. A57's k5_11/k5_16) 12/19 full, 7 open (k5_10 converted by A61 but
scoreboard not yet updated). Stragglers are certificate-MARGIN failures (tau 4.6-4.7 vs budget 5; k5_02 margin 0.0005),
not geometry.

2026-09-06 02:00: docs/residue_ledger.md = the exhaustive "what is left" list by node family with SVGs (A57 S01 room /
S02 pinwheel / S03-S06 / fractional tail; 8 window stragglers + 2 fragments; protected tier; k0_00 LOCK-FREE+; 3 Lean
axioms). PI's bottom-up idea banked and dispatched as A110 (Fable, GRAIN-FLOOD): a shadow kill should be the GRAIN
(all configurations sharing the load-bearing contact graph; side = chain length as a function of tilts, closed form)
not a 0.004 ball; s_min is continuous across contact changes that keep the load path, so kills FLOOD along the grain
adjacency graph and only Trump's grain is alive; the gap is the box-to-grain map (Morse: box minimum = a grain or the
boundary where the flow leaves).

Update 2026-09-06 (A110 landed, 411cc79d): GRAIN-FLOOD as a box kill is CIRCULAR (a packing at side <= s0 is itself
a local min <= s0, so the hypothesis = the class kill); box-to-grain map has no sound certificate short of the class
kill (monotone quantity = the side = the node's own bound; reachable grains = the selection census ~8^45 — existential
filter law). Proved: GRAIN-LP (side min at fixed tilts/selection is an LP with dual = load path), INHERIT, CONT
(s_min continuous in tilts; PI's dichotomy is about LOADED rows), GRAIN-ROW (conflict row; kills support patterns not
nodes). THE CHAIN MENU (paper-grade): Lambda = 2+4u/(u^2+1), Y, D = 2+(2+cos)/u, F_T = 2+(2+sin)/u with u = cos+sin;
Trump, S07, S02 are kink minima of it; TRUMP-GAP: s-hat = 2+(2+sin theta_T)/(cos theta_T+sin theta_T) to 40 digits;
S07's Trump boundary at 41.565 deg, crest = S02's value exactly. T4: S07 family 0/19 supports, S02 family 56/267 (none
deep). Law: bottom-up grain kills need the tree's localisation; the right consumer is a row in the node LP.

Update 2026-09-06 (A109 landed, 7daabe6f): node-level SLOT-CROWD rows kill 0/18 genuinely-alive A57 nodes at every
LICENSED depth (on a window ending at s, SLOT-SLIDE's margin and the dilation pad cancel EXACTLY -> only "meet" (delta
0) is licensed; k5_11's 4th slot carries no hypothesis above 3.877), 18/18 at unlicensed delta 0.3, certify 0/10
(B_r runs fail on exact holes at r=1 — small boxes make A94-G4 worse). 94% of supports violate SLOT-CROWD but rows
RE-PRICE rather than forbid: slot boxes 0.877 apart vs a 45-deg square's 1.414 span -> one placement meets 2-3 slots,
incidence budget pays (c 6.2 vs B 4.4). Depth breaks multiplicity; prize if depth 0.3 were licensed = the whole A57
remainder (+12.7 wall-days). Crowd rows are fixed-s0-only today (verify_param lacks nofams for B_r). SIDE FINDING:
28/46 sampled "alive-at-LP" nodes were NOT genuinely alive (tau < budget, unconverged at time limit) -> re-run
unconverged alive nodes with longer LP time when A57 resumes. Law: crowding needs certified depth; depth needs the
extension classes dead ABOVE the target side.

2026-09-06 08:00: A61 pass 5 results: CONVERTED k5_05 (margin 0.70), k5_14 (0.016), k6_21 (0.014); k5_02/k5_03 gate-fail
with ZERO margin (budget - tau = 0.000); k5_12 gate-fail by a hair (0.0265 < 0.03 gate -> lower gate to 0.02, cheapest
item); k6_27 fixed-s re-certification failed (no base cert); k5_13 running. k6+: only k6_27 whole-window + k6_07 band +
k6_23 sliver remain. Scoreboard update pending (update_scoreboard61.py).
PI refined the grain idea (not global): read the load path off the exact regional minimum and pin the load-path
squares in LP space WITH SLACK — YES side (squares in all load-path boxes) dies by the chain (side >= chain min > s0,
exact, no measure certificate; Lambda >= 2+4sqrt2/3 for ALL tilts so the tilt radius is unlimited and the position
radius is set by separating-axis selection stability), NO side = A57's existing NO-family hypothesis removing exactly
the support the LP used. Dispatched A111 (Opus) to measure the YES radius and whether NO children die or re-price.

2026-09-06 PI observation (box_to_grain_110.svg): a conditioned box beside a pin admits at high tilts NO position
clearing the pin -> those tilts are dead by logic; TILT TRIMMING (shrink the bin to the surviving sub-range) is a sound
refinement (node = trimmed child + dead part) that also ENLARGES the tight core (a larger inscribed square over a
narrower bin) -> stronger LP hypothesis. Facts: LP rows carry (cx, cy, theta) and are pre-filtered against pin cores;
the conditioned square enters the LP only as its core over the whole tilt bin. A96 asked to measure offline (surviving
bin fraction by level, boxes emptied, a_tight enlargement, LP tau change on >= 30 alive nodes, leaf shape vs T5/T5').

2026-09-06 PI: Lemma TC (tilt coherence, exact, verified): two disjoint unit squares with centre distance c and tilt
difference D (mod 90) satisfy (1+cos D+sin D)/2 <= c -> c<=1.05 forces |D|<=6.06 deg, c<=1.10 -> 13 deg, c<=1.207 ->
44 deg. Grain members must share a tilt (forced, not incidental); LP rows near the conditioned box with incoherent
tilt overlap EVERY pose -> stronger row filter than the inscribed core; mid-tilt box within 1.2 of a pin dead outside
D(c) (tilt trimming closed form). known_results 26c. A96 measuring rows removed / tau change / leaf shape (verifier
admissibility clause would change from 'disjoint from every core' to 'not overlapping all poses' -> new frozen clause
+ Lean parallel to T5).

Update 2026-09-06 (A96 155a3c5b, tilt trimming measured): per tilt sub-interval, dead iff the whole centre box lies
inside one pin's OCTAGON (Minkowski sum pin core (+) -Q(theta)) for every theta in it = T5 with a tilt-range parameter
(no new verifier/Lean beyond the range parameter). 2,222 boxes: 159 empty surviving bins = NEW KILLS (2.3x T5'):
51 L1 / 86 L2 / 10 L3 / 12 of 14 L4; 155 partially trimmed; control 618/618. Value = outright kills, NOT core
enlargement (median a gain 1.000). Lemma TC exact to 2e-16 (support-function identity, Lean-able as equality) but as a
kill test 4.8x weaker than the octagon interval test (33 vs 159) — direction matters; keep TC as O(1) pre-screen.
Row-dropping by all-poses test would widen the verifier's admissibility clause -> shelved with route (A). LP re-solves
on trimmed bins + schedule effect pending; not deployed.

Correction (A96 e68d8dbc): the 159 trimming kills = 70 (exactly T5' — trimming subsumes the tight core) + 89
incremental (31 L1 / 54 L2 / 3 L3 / 1 of 3 L4). A57 schedule 13.3 -> 10-11 wall-days @5 (credible saving at L2-L3;
L4 rate rests on 3 boxes; subtree removal of ALIVE kills not counted -> 10-11 is a conservative upper bound).
Deployment shape T5'' = trimmed child + k excluded tilt intervals; not deployed. Law: decompose a new leaf's kills
against the leaves already in place before quoting a multiplier.

2026-09-06 PI directive: brief A112 as soon as A111 lands. A112 = a second, region-specific LP tree with DUAL-GUIDED
branching (condition on the load-path squares first — rank the dual support's weight-1 placements by Fritz-John
multiplier: for S02 the top-wall square f1, then the mirror pair f0/f2 — YES/NO boxes sized by A111's selection-
stability radius; YES-YES-YES leaves killed by the chain formula or a 3-core LP; NO leaves by LP with the region
removed), run on the region where A57 stalls (S02 lineage; root = class pins + the stalled box, or the class alone);
kills transfer to old boxes by containment (a tree is a cover; the Lean composition takes unions). Yardstick = the
old tree's projected cost for the same region. Insight behind it: A57's deep S02 boxes condition on the RATTLER f3's
pocket, so no structural fact about the minimum can reach the LP through that square.

A112 addendum (PI): compare THREE branching orders on the same region — (1) load path by Fritz-John multiplier;
(2) STRANDED SPACE: score each dual-support placement by the LP row mass its YES core would strike out + the support
mass its NO-family would remove (strong branching measured in rows, no LP solve needed; a wastage/unusable-area
variant as a second column); (3) hybrid = the load-path member that strands the most. Yardstick: nodes to
termination and LP count vs the old tree's projection for the region.

2026-09-06 12:00 A111 interim: S02's LOAD PATH IS TRUMP'S (diag reflection; 0.018 / 1.4 deg from Trump's squares
8,9,10) — boxes on the three load-path squares alone cannot be a sound kill; the class pins must carry it. T1 YES
radius: 0 certified kills at r 0.02-0.1 with a LIPSCHITZ bound + capped bnb (direction-blind, like TC) though the
direct minimum stays 3.8867 (regions dead in truth); T2 NO side: tau 5.0 -> 4.75-4.80 in every child but
dead-UNCONVERGED at the LP cap (1/4 converged dead in one node). Sent A111 a scoped addition: octagon interval test
(pairs + pins) as the YES bounding step, trimmed bins + 900 s cap on 6 NO children (convergence vs re-pricing), pair
logic kills (core-core, TC). Law: A111's T1 negative was an artefact of a direction-blind bound until re-measured.

2026-09-06 12:30 docs/budget.md is THE fixed home of the total estimate (rule: every landed measurement updates its
row + provenance + date; nothing else quotes a total). As of now: A57 1,250 CPU-h (10-11 wall-days @5), stragglers
30, protected tier 3,800 (2,900-6,300; week's levers untested there), k0_00 0 (theorem) or 15,000 (tree). Theorem
route ~5,100 CPU-h (~42 wall-days), tree route ~20,000. Node anatomy: logic kill ~0 s; PASS ~850 s of which ~half is
VERIFICATION (100 s exact + 545 s 4-D at L2) not LP (240 s); ALIVE = LP + 8 children = the expensive object.

2026-09-06 PI: use the exact local minimum to estimate the box granularity needed to kill around it. Analysis: a box
near a shadow with slack Delta = s* - s0 is guaranteed ALIVE until the relaxation error (conditioned-core shrink
0.143/0.076/0.039/0.020 at L1-L4 + pin slack 0.01 + row grid pitch) < Delta; for S02 (0.0097) that is level 4, as
measured. But PRE-SPLITTING does not pay: alive LPs are only ~200 x 300 s = 17 CPU-h of 1,250; the cost is the PASS
children (LP + ~650 s verification), which pre-splitting multiplies. Where the granularity estimate pays: per-node
VERIFY CAP from Delta (timeouts), per-node LP CAP (A109's 28/46 unconverged: predicted-dead get more time,
predicted-alive get split), and skipping guaranteed-alive LPs. -> a scheduling rule in the driver using A107's
shadow-to-node map; to be folded into the A112 brief.

2026-09-06 PI: shadow-guided speedups are what "hand me the exact minima by SVG" was for; asked what else to give ->
gallery readings S08-S53 (room / near-simple / teleport / genuine grain + load path), drains of blocked packings,
protected-tier alive-node readings, the k5_12 gate decision. k0_00: evidence (every minimum found near s-hat is k>=5)
can GUIDE the k0 tree (coarse boxes far from the k>=1 manifold where the LP kills cheaply; near the manifold the
region is the K0-BLOCKED residue = teleport/drain territory, so the tree should END IN DRAIN LEAVES, not bisect
toward the manifold; adaptive box SIZE, never hypothesis shape — A99 R2's x15 warning). Cheap measurement queued
behind A112: correlate A85's level-1 k0 alive cells with distance to the nearest lattice cell; if alive = near-manifold
only, the whole k0 cost is the residue LOCK-FREE+ would delete.

Update 2026-09-06 (A113 landed, 6409396b): k0 tree cost vs manifold. On the CELL's own box only 1.4/4.6/18% of the
projected cost is within eta 0.05/0.1/0.2 of the k>=1 manifold, and Trump's cells sit at eta 0.366 (the tree
conditions on an INTERIOR square = Trump's tilted ones) — wrong object. On the LP SUPPORT the PI's hypothesis holds:
LP-killed cells' supports have <=1 simple placement (match S01 room); un-killable cells (0/26 with d_pos<=0.05 ever
killed; six most resistant, tau up to 10.5, at d_pos<=0.02; tau climbs under row generation -> un-killable by more
LP time) have supports = 2-6-slot partial skeletons of near-critical shadows (S38 exact, S07 Jaccard 0.83). Position
distance predicts tau (Spearman -0.44), tilt distance nothing; LP wall flat in eta. => k0 RE-BRANCHING rule: branch a
cell on the slot its support keeps occupying (readable after the LP) = k0 face of A112; YES side via K0-FREE/teleport
+ crowd rows (licensed at depth 0 at fixed s0, all k>=1 dead there); NO side LP without the support. k0 tree has
ZERO logic kills today (never branches on corners). A107 glob bug: 264 k0 LP jsons exist (A38 l1/l2/l3_nodes, A85,
A99 results/nodes/k0_00/) — fix adds ~146 alive k0 nodes to the gallery.

Update 2026-09-06 (A96 d016209b, READY TO RESUME, not launched): T5'' trimming at emission wired (trim57.py, TRIM
flag, 618/618 control vs deployed module; suffixed ids Y0007a/b for bins surviving in pieces); shadow_sched.py (off:
564 predicted-dead / 8 alive / 619 unknown; LP cap x3.75 + verify depth +8 for predicted-dead); recheck96.py (900 s
re-check, resumable, --trimmed); pausegate.py (PAUSE sentinel checked between nodes + --reap orphans). CAUTION: trimmed
re-solves at 240 s: 29/32 solved, only 2 converged, 4 eta<-1e-6, 19 knife-edge (|eta|<=1e-6), 6 alive — trimming
moves the LP but does not decide it at 240 s; take no kill count before the 900 s re-check. TC ROW SCREEN removes a
median 43.8% of warm rows (13k of 30k) — strongest case for row-dropping (route A: verifier admissibility clause
'disjoint from every core' -> 'disjoint from some pose of the box' = new frozen verifier + Lean parallel to T5).
Asked A96 to measure dropped-row LP kills at 900 s and write the clause/Lean spec.

Update 2026-09-06 (A111 landed, 4c6ace6e): load-path branching sound on 146/286 shadow-explained nodes; ~35 kills at a
2/3 certify rate (n=3) = ~+1 wall-day; 2 nodes killed end to end. Chain (Farkas) YES kill certifies only for
r < s*-s0 (0.0097 / 0.0085) = level-4 widths (grid_lb = s* - r exactly). Octagon/TC kill NOTHING between load-path
boxes at s0 (genuine room; side-blind rules cannot make a side statement) but the FREE PAIR KILL (core_meet +
tilt_coupling between the node's own bin and a load-path box) fires 113/264 (L1) -> 200/264 (L4) on S02 nodes, 19/19
S07 from L2; verified by 57,840 sampled pairs. NO side = convergence-time problem (dead-unconverged at 80 s -> DEAD at
900 s); 8/22 nodes all-NO-children dead; certs 14 PASS / 4 FAIL (eta <= -0.5 always passes); verify_param lacks
nofams -> NO certs fixed-side (x4 for the window). S07 branch UNSOUND at L1 (Trump inside the YES region at A57's L1
tilt half-width 4.87 deg > 4.82 needed), usable from L2. BUGS caught only by sampling: containment rows used the max
half-width; tight_a fed a negative (reflected) tilt interval returned a core half-side 0.784 > 1/2 (!) — asked A96 to
assert the domain and scan the deployed corpus. STANDING RULE: no LP-free geometric count before >= 1e4 sampled pairs
confirm it. A112 dispatched (region tree, three orderings, S02 L2-3 nodes + k0 cells).

2026-09-06 PI asked about lowering the LP cap: the trade is ASYMMETRIC — an LP costs 240-400 s, a false ALIVE (cap
hit unconverged; A109 28/46, A96 27/29 at 240 s) costs 8 children x ~850 s = ~6,800 s -> RAISE the LP cap for
borderline nodes (900 s re-check built), LOWER the verify cap (completed FAIL + resolver beats a 1,500 s timeout;
atom-dependent cap in). Pin WASTAGE (stranded pocket area a candidate box creates against pins/walls/other boxes)
added to A112 as a fourth full branching order.

Update 2026-09-06 (A107 Part II, 87ed93bb): 217 alive k0 cells (A38 153, A99 53, A85 11); 30 K-shadows explain 161;
K01 = room at side 4.000 explains 84 (the k0 twin of S01); K06 = the pinwheel 3.886745 reached from k0; 56
unexplained. CORRECTION to A113: slot-set Jaccard != packing match (A113's "S38 exact" cell minimises to 3.914 = K04;
its "S07" cell to 4.000 = K01) -> un-killable k0 cells are mostly ROOM. K0-FREE (teleport, Lean) kills room
configurations by theorem; the k0 LP doesn't know it. Corner cells are far apart (a square meets at most one) so
corner-crowd rows (A92's Lemma CW) have NO multiplicity re-pricing, unlike A94's slot rows -> A115 dispatched: CW
corner rows at the k0 NODE level on the K01 cells (delta 0/0.05/0.1, 900 s, two-run certification, Trump-image canary).

LAB LAW (2026-09-06, PI question "more nodes at low timeout or fewer at high?"): fewer at the converging cap, with the
TWO-STAGE PROTOCOL for every lever test: stage 1 LP at 240 s -> any node with eta <= -1e-3 goes straight to the frozen
certifier (the certificate is the verdict; ~100-150 s; A111: every child with eta <= -0.5 passed); stage 2 = only
knife-edge nodes (|eta| < 1e-6) get 900 s, and only those still on the edge count as alive. Report kills as CERTIFIED
passes, never LP verdicts. Unconverged 240 s LPs measure the cap, not the lever (2/29 converged, 19 knife-edge).
Sent to A112 and A115.

Update 2026-09-06 (A114 landed, 9ef80bfa): k6_23 (resolver, 0.17 h), k6_07 (16-slab grid, 2.3 h — BL(0,2)/S07 slot
now a full-window kill), k6_27 (14 slabs, 0.55 h) CLOSED -> k6 and up all full-window; scoreboard 48/52. k5_03
partial (5.9%), k5_02 partial (0.4%): resolver closes every recorded witness cell but BULK slabs fail (thin); k5_12
still open (gate irrelevant; certify FAILs at depth 56, tau driven to budget by witness feedback; no certifiable
measure at eps_geo 0.003). A114 continuing slab sweeps k5_03 -> k5_02 -> k5_12 under a 15 CPU-h cap. Method laws: GRID a
band, never bisect from the top (one-slab timeout 1800 s vs 16 pieces at 190 s each); A56 witness files are truncated
(diagnostic only) — closures rest on complete slab PASSes; slab cost per 1e-3 side @ depth 48: 11-340 s by class.

SLAB-WIDTH LAW (2026-09-06, from A114's k6_07 log): the 4-D verifier needs a fixed leaf s-cell width w_min (k6_07:
2.3e-5; set by certificate margin vs dilation sensitivity) and a fixed pose depth d_pose (~39); a slab passes iff
log2(width/w_min) + d_pose <= depth cap 48. Passing 0.0029 slabs: s-depth 7, max depth 46, 167-215 s (rising gently
toward s0, more admissible area); failing 0.0235 halves: s-depth 10, depth cap hit, 8 undecided boxes, 0 holes, 1,500 s
each. Predictor: ONE narrow probe slab gives w_min and d_pose -> width_max = w_min * 2^(48 - d_pose) (k6_07: 0.0118 ->
5 pieces suffice); total cost ~linear in band width once slabs fit, so over-split freely, never under-split.

2026-09-06 slab law banked in docs/budget.md sE. Near-solution corollary (PI suspicion confirmed): w_min/d_pose are set
by the certificate's slack, which for a class carrying a shadow at s* is ~(s* - s) at side s -> cost per 1e-3 of side
is flat far below the shadow and rises steeply toward s0; k5_02 (margin 0.0006) and k5_03 (bulk slabs fail near s0,
cheap at 3.82) both sit on the S02 pinwheel (A107 lists them under S02). Fix: anchor a FRESH certificate at each
slab's top side (slack s* - s_top) instead of reusing the s0 certificate — sent to A114 with a request for the cost
profile along s (first direct measurement of verification cost vs distance to a shadow). Diverges only for classes
containing an actual minimum (Trump's) = the basin/tube domain.

2026-09-06 PI: near-solution scaling is THE exponential; invest in the bottom-up local method. Diagnosis of why
A111's Farkas leaf certified only r < s*-s0: (i) AMBIGUOUS selection pairs were DROPPED instead of case-split (losing
the rows that carry the chain when a contact is near opening); (ii) boxes anchored at the shadow's coordinates at side
s* while the node sits at s0 -> frame slack 0.0097 absorbed by the radius (anchor at s0 instead); (iii) O3 chord
relaxation loose over big tilt cells. None structural. A116 (Fable) dispatched: Theorem LOCAL = selection tree over the
near pairs of the load path; leaves = chain formulas (min side at fixed selection, GRAIN-LP); N dead iff every live
leaf's chain min > s0; the only dip is the gap chain inside Trump's range (cut at 41.565 deg); measure radius on
S02/S07 at r up to 0.3, rho up to 40 deg; consumer = A112's YES leaf.

2026-09-06 PI sharpening (sent to A116 as primary route): enumerate realisable contact graphs within per-square
perturbation delta from the exact minimum's own contact graph via PER-PAIR CONTACT-TYPE STABILITY RADII — a contact's
type (edge-on-vertex etc.) changes only if the riding vertex reaches its edge's end (distance readable from the
minimum) or a rotation brings another edge into play (forbidden by Lemma TC within contact distance); non-contacting
near pairs get a no-contact radius. Then N = min pair radius, ONE live leaf (the minimum's graph with contacts closed
or open; open contacts only lengthen the chain), kill = one chain formula over the tilt box cut at the Trump boundary.
PI's example: S07's f4 bottom-right edge can only meet BR(0,0)'s corner within radius ~0.25. Deliverable = per-pair
radius table for S07/S02 (the object the PI wants to read).

Update 2026-09-06 (A115 landed, f37487d3): corner-crowd rows at the k0 NODE level do not kill — 36 cells x 3 delta,
1 attributable certified kill (L3), 0 genuinely alive cells. NEW failure mode: the K01 "room" supports have EVERY
corner met by a single DEEP meeter (>= 0.30 in 296/486 incidences), never empty — the K0-FREE teleport hypothesis
exactly; crowd rows charge the SECOND meeter, which does not exist. At delta 0 every Trump image realises 9 corner
incidences vs guaranteed budget 8 (tangent squares count) -> the root crowd LP can never pass at delta 0; at 0.05/0.1
c >= B in 100/101 runs (tau convex in e -> no e kills). Incidental: a plain warm re-solve certified an A99-open cell
-> warm re-solve pass over A99's open k0 cells fired (cap 5 CPU-h). Law: the k0 room needs the TELEPORT hypothesis as
a node cut (re-branch on the singly-met corner = A112's k0 face), not a weighted row.

Update 2026-09-06 (A112 landed, e6690215): region tree on 17 stalled S02 L2/L3 nodes: 77 nodes / 56 LPs / 51 min vs
old tree 671 nodes / 54 h projected; kills 9/17 but 6 were already T5'' trim kills -> own score 3/11 non-trivial (1
free by TC bin-vs-pin, 2 by certified 3-node trees at 27-54x less wall). Branching ORDER is a tie-break (all four
within 73-77 nodes, same kills). Two-stage protocol 2.26x cheaper than flat 900 s. All 10 free pair kills are Lemma
TC (none core-core), 4 between boxes the tree introduced; the chain kill never fired at tree depth (r <= 0.0125). k0
cells: 0 kills, every LP at eta = 0 EXACTLY (removing a support placement does not move tau). Corrections: eta does
NOT predict certification (PASS in [-1,-0.25], FAIL in [-0.71,-0.16]); the k0 YES shortcut "square in a slot box =>
k>=1" is UNSOUND as box containment (A53 stratifies by grid-locked squares). Emission is NONDETERMINISTIC
(certify.py --loop_cols re-solves under a time limit; atom set wall-clock dependent) -> reproduce kills by REPLAYING
certificates. Dispatched A117: verify_param_v2 with NO-families (~100 lines + Lean lemma) + Lemma TC as a certified
leaf; asked A96 to wire --region-tree fall-through (off by default).

2026-09-06 PI (reading K10/K01): "anywhere a corner can only be reached by ONE square is dead by teleport". Sound
form = LANE-COUNT leaf (A118 dispatched): for a node and a usable cell C, upper-bound the number of interior-disjoint
unit squares that can simultaneously meet C given what the node FIXES (walls, pin slack cores, the conditioned core);
LANE <= 1 => dead by teleport (K0-FREE / SLOT-CROWD, Lean), quantifying over all configurations. The LP's dual
support is a WITNESS not a hypothesis — a reading of it ("only f3 can reach BR") kills the configuration, not the
node. Differs from A101's SNAP-T (needed the cell EMPTY; 0 fires) — this needs <= 1 meeter. Expect fires where pins +
conditioned core close a lane (pinned classes), few in k0 (an open corner has two lanes). Review CSV columns clarified:
reading / load path (grain only) / binding contact (grain only) / drain-or-kill (the node cut: "tele f1 BR00",
"snap f0 f2 BL11", "chain", "same as S07").

2026-09-06 PI generalisation: "sign kill certs directly in phase space — any box with only one (x_i, y_i) near a
corner is dead by teleport, no LP". Sound in FULL phase space; our trees localise ONE square (the LP handles the
rest by measure), so a node cannot see how many squares are near a corner — the architectural reason every
"singly met" row failed. Use it BACKWARDS: branch on the TWO meeters (a box-pair cover of the corner-meeting region
R(C) x R(C) for two non-pin squares); the complement "<= 1 square meets C" is dead by teleport for FREE; the YES side
gives the LP two extra cores at the corner (pair kills, TC, octagon fire between them). Differs from A99's R2 (depth
PATTERN branching, x15, no kills). Added to A118 as T4: pair-box counts, logic kills, two-core LP kill rate and price
on >= 20 pair-boxes; Trump's TL two-crowd must survive its pair-box.

Update 2026-09-07 (A115 T4, 71a5b20b): a plain 240 s WARM RE-SOLVE (no rows) from each k0 cell's stored rows/atoms
certifies 10/55 open cells reached (7 of A99's plain L1 cells, 2 never run) for 5.1 CPU-h -> 300-700 CPU-h removed
from A99's frontier (59-138x return). Stored node results were row-generation-INCOMPLETE. 4 cells CONVERGED-alive
(tau = budget, minmass 1, converged) -> no LP time kills them; candidates for A118's two-meeter cover. Continuation
fired (900 s + witness feedback on the 36 kill-candidates; plain pass over the 82+41 never-run cells; cap 10 CPU-h).
LAW: before any new mechanism, re-run the cheap control (warm continuation + ordinary certificate) on the open set.

Update 2026-09-07 (A116 landed, 74a34f96, done-success): THEOREM LOCAL proved (COVER/LEAF/DROP/RELAX/STAB) and the
local certificate certified at (r, rho) = (0.2, 10 deg) for S02 (k5_11 frame, L = f1 f2 f3 BR(0,1)) and (0.1, 40 deg) /
(0.2, 10 deg) for S07 (trump5 frame, cut F_T(theta) > s0) — 20x A111's radius; 1e4 samples, Trump outside. A111's
r < s*-s0 was the DROPPED ambiguous rows. PI's stability-radius route confirmed pair by pair (f4-BR(0,0) = 0.254 at
fixed tilt; limiter f0-BL(0,1), the Trump boundary). Limiter at r = 0.3 = genuine rearrangement that the dropped
squares would block -> add blockers as boxes (A119). Consumer: 72/184 k5_11 + 23/68 k5_16 S02-explained alive nodes
have supports inside a certified N; 4-445 s per N shared. Dispatched A119 (rational Farkas certs + Local.lean +
blocking boxes + tilt-cell sharing); asked A96 to make the certified N the YES region in regionopt96.

Update 2026-09-07 (A96 ef646f0f): region-tree option now uses A116's certified N as the YES region (tagged 'pending
A119'); replay of A112's 17 stalled nodes: only 4 inside a certified N, 2 close outright (0.5 s, no LP). The 72/184
headline is the corpus fraction, not the stall-set overlap. Targeting decision taken: run the region tree offline on
ALL ~70 in-N alive A57 nodes (cap 12 CPU-h, two-stage protocol, NO certs s0-only pending A117). LAW: a lever's
headline fraction must be intersected with the population it will actually be applied to before quoting a saving.

2026-09-07: A96 STOPPED (correctly) before running the region tree with A116's N as the YES region: A116 states N as
6-D PAIR-POSE boxes with forced selections, not as (centre, tilt) boxes per load-path square in the node's frame; the
conversion is a soundness step (a wrong N would be certified downstream without any failure signal). A119 asked to
export each certified N as node-frame boxes per L square + the cut with a covering note (results/N_boxes.json) and a
1e4-sample check; A96 to verify the check independently then run the 35 in-N ALIVE nodes (not ~70: 39 of the 74 are
already decided) at 900 s two-stage, cap 15 CPU-h. LAW: an agent that stops on a soundness step it cannot verify is
doing the right thing — never tell it to improvise a frame change.

Update 2026-09-07 (A96 37eae961): ROW-DROPPING is NEGATIVE — three arms at 900 s on the trimmed alive nodes: arm C
(all-poses row filter, median 53% of rows removed) 3 strict kills vs arm B 4, none new; it only buys convergence
(7/26 vs 4/30) on nodes that end knife-edge/alive anyway. A speedup with no kill yield does not justify a
soundness-relevant verifier clause change -> route (A) shelved, spec on file. 900 s cap confirmed (2/29 converged at
240 s vs 4/30, 7/26 at 900 s). A96 waiting on A119's N_boxes.json for the 35-node in-N run.

LAB LAW (2026-09-07, A96 f1f8f7ac): an acceptance-filtered sampled check must report how many samples SURVIVED the
filter, not how many were drawn — A96's first check of A119's N boxes rejected 99.97% of draws (strict containment
vs pin slack) and "20,000 samples, 0 hits" tested ~30 configurations. Corrected: pins clamped into the container,
containment applied to load-path squares only; S02 k5_11 r0.2/rho10: 73,642 draws, 10,500 tested, 0 hits. Apply to
A116's and A119's quoted 1e4-sample confirmations too. A96 now writing the NO-side runner (N boxes -> caselp
NO-family children) with an A112 replay control before the 35-node run.

2026-09-07: A96 (the A57/A96 owner agent) is OUT OF WORKING ROOM — it declined to write the NO-side runner in a
hurry and handed off a settled spec (its last report; PAUSED.md current: T5'/T5'' on at resume, shadow scheduling and
region-tree/A116 options off, recheck96 available, row filter shelved). A120 (fresh Opus) dispatched with that spec:
runner + controls (A112 replay byte-identical; covering check with survivor counts) + the 35 in-N alive nodes at 15
CPU-h. Any future A57 resume needs a FRESH owner agent briefed from PAUSED.md + lemmas.md, not A96.

Update 2026-09-07 (A117 landed, 6f160858): verify_param_v2 (NEW file; sha 153029ba...; v1 0c58485c... and verify_case
521cb01f... untouched) adds NO-families to the 4-D verifier: 30/30 byte-identical to v1 without nofams; Lean
ParamNoFam.lean nofamExemptIV_sound PROVED, lake build clean, axioms unchanged. NO-side re-verification: 16/48
window-valid kills gained, 0 fixed-side PASS became a window FAIL, but 4-D wall = 10x the four fixed sides (a NO cert
is tiny at fixed side because the nofam exempts most of the container) -> v2 buys VALIDITY not wall. New blocker on
the YES side: a branch box as a core is refused by core_affine (not slot / not in Q_dy) -> certificate-based
region-tree kills stay s0-only; the only window-valid region-tree claim today = the free TC kill of Y0041_D02.
TC leaf: 170/170 fires reproduced, 1.7M sampled pairs, 0 counterexamples; Lean statement frozen as Prop, SAT step [C].
Process laws: only select certificates with a stored report or always pass a cap; comparison caps by BOX COUNT not
wall; a verification cap may only abort (CAP), never decide.

Update 2026-09-07 (A118 landed, 405b6522): LANE-COUNT leaf sound (0.37 s/cell, 18,086 cells): reproduces 25 kills the
trees paid ~850 s for; 13 NEW (1 A57 box Y1080, 12 k0 cells conditional on k1_00) = 0.05 wall-days. Failure mode:
1,323 cells at LANE <= 1 are saved only by M = 1 — the node's own conditioned square may be the second meeter. Corner
cells dominate fires; BL(1,1) fires 1/3,580. Deploy at emission as pre-screen (~1.7% of LPs), never as a re-solve.
REVERSED LEAF (two-meeter cover) sound but non-terminating: 26-14,099 pair-children/node, 9% per-child kill rate,
2-500 CPU-h per node kill = k0_route C3 at pinned classes; its value is the free branch. The octagon PAIR inequality
(no separating axis for any pose pair) is strictly stronger than Lemma TC (fires at centre distance < 1 vs ~0.7) and
subsumes the TC-leaf obligation. Usable-slot table updated (k5_16 + BR(1,0), TL(1,0); trump5 + BR(0,1), BL(0,2));
A109-O1 discharged. Count must run on the ORIGINAL packing (a_w = 1 exactly on the slab; the grazing staircase makes
LANE >= 2 vacuously on the dilated family) — pull cores back to side m and hull over the slab.

Update 2026-09-07 (A121 batch 1, 199000f4): PI's `r` readings 3/3 EXACTLY right (singly met corners, depths
0.67/0.67/0.97). But for k0 (K rows) only the FOUR CORNERS carry a teleport lemma (no pins => no completable
non-corner slot): 16/23 `ns` items name cells k0 cannot teleport into; 11/23 name squares already EXACTLY on their
cell (the gallery's slot/free split under-counts slots in 11/21 entries — the minimiser slides free squares onto
cells and nothing re-snaps them); 9 are far off (L-inf 0.1-0.9: the minimiser REARRANGED, not snapped); 2 are crowd
cases. Node kills from the batch: 6, all already A118's. K18's shared-tilt grain confirmed (6 squares within 5.5e-4
deg) but its Fritz-John decomposition does not close (rank 19/21). 14 A38 `i` nodes never in A115's queue -> added.
LAW for the CSV: K rows -> annotate corners only; S rows -> usable slots too; a right-panel square far from its
left-panel pose is a rearrangement (flag ?), not a snap.

Update 2026-09-07 (A121 batch 2, 4c6e01fa): 45 rows, 138 items, 1,453 (node,cut) rows, 9 node kills, 0 NEW (all
A118's). All 12 `r` items exactly right. Of 60 `ns` items only 5 are genuine uncrowded near-snaps; 22 already exactly
on the cell (gallery slot/free under-count now 23/45 entries); 26 of 30 "far" items are FLUSH in one axis, displaced
ALONG the wall (A101's flush population) -> new token `fl <sq> <cell> <along>`; cell names are NOT offset (identity is
the argmin over 784 relabellings). 736/1,453 cut rows are `none` because usability is per node class (S entries mix
classes; TL(0,0) usable for trump5 but not k5_11/k5_16). Validator found 5 corner singly-met candidates the readings
missed (none node kills). g rows: K18/S13 tilt clusters exact; K18 and K30 Fritz-John do not close (rank deficient).
CONCLUSION: the readings validate the gallery but node kills are bottlenecked by M = 1 (the tree's own conditioned
square may be the second meeter), not by identification — PI's time is best spent on `g` rows, `?` rows, and pinned
S rows; `ns` on K rows yields nothing.

2026-09-07 PI callout: S33/S34/S35 (trump5 nodes, k11 6 slot + 5 free, s* 3.9169-3.9174, 0-1 flexes; K19 = S33
exact) minimise to almost the same contact graph and look FULLY LOADED (no rattler/room/rotation) — a candidate
third exact minimum on trump5's skeleton after Trump and S07. A122 dispatched (A108-style: polish with trust region,
exact endpoint, contact graph, rigidity, Trump/S07 comparison, drawing, local-certificate applicability).

2026-09-07 PI on S38 (trump5 boundary, 5 common-tilt squares, s* 3.9289): its tilt-sweep curve shows a local
minimum next to Trump's global minimum with a HILL between. Reading: the hill = the crest where two menu chains
cross (as S07's family crosses into Trump's gap chain at 41.565 deg); S38's local certificate is cut at the crest;
and the crests along the common-tilt families are points on TRUMP'S BASIN BOUNDARY — far larger than the 0.0015
Hessian ball in those directions; collect them (S07's, S38's, ...) to shape the tube around Trump. Added to A122.

2026-09-07: PI's first pass over ALL 83 gallery entries complete (docs/shadows/review.csv, 2473d98d). New PI token
`st4` (S50/S52/S53): a vertical stack of four simple squares on one side forces side >= 4 -> dead (configuration
kill; node kill only if the four are pins/hypotheses). S21 read as S07-type (near-Trump, f0's corner out of the gap);
S33/34/35 "fully loaded"; S30/S31/S16/S24/S29/S13/K18 same-tilt grains; `-` rows (S22, S37-S43, S46, S47, S49, S51)
= blue snaps carry the row. A121 running batch 3 + cumulative.

2026-09-07 00:40 PI granted the machine for ~8-9 h (asleep; token reset). Dispatched A123 (Opus, night-shift A57
OWNER): resume A57 from PAUSED.md with T5'/T5'' LIVE at emission (first live test), shadow scheduling + region-tree
OFF, recheck96 --trimmed at 1 process; box <= 16 python processes, > 3 GB free physical; PAUSE sentinel at 08:00,
drain, PAUSED.md v2 with the night's kill table (live T5'' fire rate vs the 89-box projection). Other chores still
running at <= 2 procs: A61 (k5_13), A114 (k5 stragglers), A115 (k0 warm re-solves), A119, A120, A121 (batch 3), A122.

2026-09-07 01:00 A123 correctly REFUSED the full A57 resume: the box already held 17-20 python processes (8 workers
pinned at 100%, ~69% CPU) from A53/A61/A96-arm-C/A112/A114/A119/A120/A121; the resume block needs >= 17 more ->
3x oversubscription would convert other campaigns' wall-capped nodes into spurious TIMEOUTs and depress the night's
T5'' measurement. Discrepancies found: launch.ps1 has NO pidfile gate (the gate is in scaleup.ps1; calling launch
twice double-launches); all 21 A57 pidfiles stale; pausegate.py lives under A57/code not A96; A96's arms96 --arm C
(pid 26228) still running 11.8 h after A96 reported the arms finished (a STRAY). Re-scoped: kill the stray, 3 shards
(k5_11 s0/s1, k5_16 s0) + recheck96 at 1 proc, no deepens/drivers/select96; emission-time T5/T5'/T5'' fire rates are
geometry (contention-independent) = the clean deliverable; LP/certify walls reported as CONTENDED. LAW: a campaign
resume needs a process budget counted against the live box first; chores at "<= 2 each" add up.

Update 2026-09-07 (A121 cumulative, 4a3b0078): 83 rows validated: 9 node kills, 0 NEW (all A118's); all 18 `r`
exactly right; `st4` sound (four flush squares on a wall => side >= 4; need not be consecutive) but configuration
kills only; S34 = S33 (ds 6e-15), S35 != S33 (6.9 deg), S09 != S05, S21 = related near-Trump, not S07; 7 g rows have
FJ residual > 1e-3 (nnls fits). KEY FACT: 81/83 gallery right panels are REARRANGEMENTS of the node's support (only
S02/S07 tilt-only) => a reading is a pointer to a cell, never a node fact; node kills need the lane test and the
node's own conditioned square blocks it in every close case (6 misses). Meet/graze threshold now 1e-6. The gallery
review's value = the exact minima (S02, S07, S33 family) feeding the local certificate, not per-node cuts.

Update 2026-09-07 (A114 continuation, ee0c18d5): k5_03, k5_02, k5_12 ALL CLOSED full-window with the ORIGINAL s0
certificates once slabs were sized by the slab-width law (12.5 CPU-h); scoreboard 51/52 — only k5_13 (A61) open.
My per-slab-certificate premise was REFUTED: every earlier bulk FAIL was an over-width slab (k5_02's 4x), never node
hardness; make_param hard-codes S0 anyway. L7 cost profile (224 runs): bulk trend mild (+38-59% across the window);
blow-up confined to the last 1e-4..5e-4 below s0 (k5_12 129 -> 4,181 s per 1e-3; k6_27 d_pose 39 -> 43) = the S02
shadow in the arithmetic. width_max: k6_27 0.014, k6_07 0.012, k5_02/03 0.0018, k5_12 0.0010 -> 0.0005 at the top.
Driver bug: verify_param's integer grid D = 250000 << (depth+2) refuses s endpoints whose denominator is not 2^a 5^b
(b <= 6) -> "FAIL in 0.3 s" = a crash recorded as a verdict; close114 now validates endpoints and persists banked
ranges after every slab. LAW: a FAIL that returns in under a second is a crash, not a verdict.

2026-09-07 ~02:00 A123 night shift LIVE: 3 shards (k5_11 s0/s1, k5_16 s0) + recheck96 --trimmed (383 ALIVE queued);
box 20-21 python, 13.7 GB free; TRIM/TIGHT_CORE on, shadow_sched off. A123 DECLINED my order to kill arms96 C: it
is on its 32nd/last node (31 rows, no 'done' line) and 5 nodes landed after A96's n=26 report — one of them (Y1135)
is the report's own open caveat; a C-only kill among them would flip the row-filter gate. Leave it (frees itself
within the hour). T5'' LEDGER GAP: trim_excluded / trim_from are built in build_children but never persisted (not in
rec/jsonl/node json) — not a soundness issue (sub-boxes; 618/618 control) but MUST-FIX before the next resume; T5''
full kills identifiable by pin_info == "trim", partial trims by the a/b id suffix. LAW (again): don't kill a process
on a premise the log contradicts; the agent that checks is right.

2026-09-07 ~02:30 night shift: 4 shards + recheck96 live, box 21/~24. arms96 C finished (32/32): ZERO C-only kills on
complete data; row-filter gate definitively NOT met; verifier-v2 row-filter stays shelved. T5'' persistence gap is
WORSE than reported: the commonest outcome (a single surviving trimmed piece, e.g. Y0376 theta [0, 3.51] vs canonical
7.63 band) leaves NO marker in any persisted field (pin=ok, no a/b suffix, no trim fields); the live fire rate is
recoverable only by comparing emitted theta widths against the pre-T5'' canonical bands — A123's analyzer does that.
MUST-FIX before the next resume: persist trim_excluded/trim_from + original bin extent on every child.

Update 2026-09-07 (A119 landed, e07f8808/71d18eba): five local certificates EXACT (S02 (0.2,10),(0.1,10),(0.05,20);
S07 (0.2,10),(0.1,40)): 53,094 dead leaves, 769,440 rational multipliers, all VALID under an independent dyadic-
interval checker (no numpy; rebuilds every RELAX row); Local.lean builds, 0 sorries, ONE axiom sat_selection
(Lemma SAT for INTERIORS; closed form already in CaseSat). Corrections to A116: 3 of its 4 "capped" rho>=20 cells are
ALIVE (witness packings of L u P below s0 inside N: S07 (0.2,20) 3.8734 ladder shears at 65 deg; S07 (0.2,40) 3.8696;
S02 (0.2,40) 3.8767) — A116's own witness files had it under a 'capped' label (F5); blocking boxes do NOT widen the
radius (6 free bodies -> 16-23 near pairs; only S02 (0.1,5) closes). Consumer unchanged 95/252. Findings F1-F4:
q-splits don't survive tilt bisection; close on the Farkas vector; infeasible cells need an exported ray; checker
must match generator sharpness. LAW: a 'capped' verdict is not 'open' — check the witness file.

Update 2026-09-07 (A122 landed, 4e8eecc8): S33 = S34 = K19 is ONE exact minimum, 3.916930865713920563 (endpoint cert
eps 1e-9); S35 is a DISTINCT second minimum 3.917417657814610628 (+4.9e-4, one square 6.9 deg off); S38 = 3.928914685
with an algebraic side of DEGREE 9 (explicit minimal polynomial). S33/S35 are SMOOTH interior critical points (16
active rows, rank 14/15 -> 2-/1-parameter family; FJ closes at first order, unlike S07's kink); no closed form by PSLQ
at 170 digits. All 11 squares load-bearing, no rattler (PI's "fully loaded" confirmed); 2 flexes blocked at 2nd
order. Same k6_07 skeleton as Trump/S07, differs from S07 in ONE square (f0 upright, flush on the BL column at x=3/2);
third separate minimum (crests +0.038 toward Trump and S07 vs S07-Trump +0.0011). S38's grain = two chain formulas NOT
in A110's menu (C2/C3, crossing polynomial G(theta)); its crest is on the FAR side (42.794 deg, 3.934378); no
descent via F_T (k6_21 lacks BL(0,2)); it contributes NO wall to Trump's basin; S07's wall = 41.5649 deg / 3.886746.
A116's local certificate applies to S33/S38 with NO Trump cut out to r = 0.205 / 0.677. Trap (path form of A108's):
a tilt-pinned relaxed sweep WITHOUT a continuation tube reports 3.9023 at S38's tilt, 0.027 BELOW s*.

Update 2026-09-07 (A115 T5, e7a53299): warm re-solves certify 17/216 k0 level-1 root cells (16 new) + 6 L2 + 1 L3 +
4 A85 for 15.4 CPU-h total -> 770-1,780 CPU-h off A99's frontier (48-111x). The PI's 14 `i` gallery readings: 14/14
certified (7 were never-queued A38 undecided L1 cells) — the readings DID produce kills, via the incomplete-support
pointer. 7 converged-alive cells (tau = budget, minmass 1, converged; l1_153 is a Trump-image cell) -> two-meeter cover
candidates, no LP time helps. 32 persistent cert-FAIL candidates. Continuation fired (34 never-run L1 + open L2/3,
cap 15 CPU-h). k0 tree route now ~13,500 CPU-h central.

Update 2026-09-07 (A120 landed, 9fa13dfe): local certificate as the YES leaf on the 35 in-N alive A57 nodes: 9
processed at the 15 CPU-h cap, 4 CLOSED outright (all L1; 83 descendants = ~0.05 wall-days), 5 with 17 open NO
children (2 structures). FINDING: certifier shortfall, not survivors — 31/36 NO children clearly below budget at the
LP but at a 0.3% certificate margin only ROUNDS-6 certification passes (690-2,470 s); A112's --rounds 1 default was
the limiter; "waiting for column generation buys nothing" holds only when eta is deeply below budget. Timeout protocol
2.74x on the LP. Controls all green (A112 replay byte-identical; covering 3 x 1e5 tested 0 hits; same-boxes-same-frame
asserted 35/35). Laws: CAP is never a verdict (kill the whole subprocess tree); two processes must never write the
same node record. Continuation fired on the 26 remaining (rounds 6 from the start, cap 15 CPU-h).

Update 2026-09-07 08:15 (A123 night shift paused cleanly, ad55f884): 296 new L1 children on 3 shards: PASS 149, logic
90, ALIVE 45, FAIL 9, T5'' full kills 3 (1.0%), trimmed bins 16 (5.4%). T5'' LIVE: touch rate 6.4% matches offline
6.6%, but full-empty rate 1.0% vs the projected 3.7% -> the offline "159" likely mixed TOUCHED with EMPTIED; 15/16
trimmed bins still ALIVE; trims bite at tilt extremes -> T5'' buys LP tractability, NOT kills; the 10-11 wall-day
figure is unsafe (budget row now 11-13 pending A124's control). THE NIGHT'S REAL RESULT: recheck96 --trimmed certified
11/23 previously-ALIVE nodes (48%) in 7.3 CPU-h — better per budget than the shards; 360 remain. k5_16 s0 hangs
deterministically on Y0381 (2 h single-thread spin after the LP cap; reproduced) — needs debugging before that shard
resumes. Soundness clean (max core 0.398; bins in [0,90]). Dispatched A124 (day shift): re-check at 2 BelowNormal
procs cap 20 CPU-h, touched-vs-emptied control + schedule re-derivation, Y0381 hang diagnosis. LAW: a lever's
projection must separate "touched" from "emptied"; on a contended box, re-check alive nodes before opening shards.

Update 2026-09-07 (A120 continuation, 5d0069a5): stopped by A123's A57 PAUSE sentinel (pausegate checks BOTH bases) —
correct behaviour; 11/35 processed, still 4 closed, 7 open, 24 not run; 11/44 NO children are genuine survivors
(converged, eta = 0; one with eta > 0) concentrated in 4 nodes — not closable by this cover at s0 at any certifier
budget; survivor count does NOT track distance from the S02 minimum (dmax). CERTIFIER DEFAULT for the next owner:
--rounds 6, hard wall 2600 s, --time_limit 420 (passes came at rounds 0-5, max 2470 s; rounds 1 would have taken 52%
of passes, rounds 3 81%). Ledger a120_closures.jsonl is append-with-revision (reader takes the last row per id).
A124 asked to define a sentinel-scoping mechanism so chores run under the A57 shard pause; then A120 resumes.

2026-09-07 morning: PI asked for a basin around S33 -> A125 dispatched (A116/A119 machinery on S33min with L = all
11 load-bearing squares, r up to 0.2, rho up to 20 deg, rational leaves + A119 checker, no Trump cut needed since
Trump is excluded on position alone to r = 0.205; consumer = A60's trump5 alive nodes; S38 at (0.1,10) as a second
point). Value: the protected tier's residual tree must end in certified basins around every minimum on Trump's
skeleton; each certified N is a region trump5's tree never bisects.

2026-09-07 EXTERNAL REVIEW (another model, via the PI): (1) finish the Lean LocalDead checker + YES/NO composition
before expanding A116-A120 -> A126 dispatched (replay a concrete N in the kernel; discharge sat_selection by
shrink-and-limit; Composition.lean step; instantiate on A120's Y0230); (2) small reusable incompatibility
certificates on 2-4 squares with ASYMMETRIC per-coordinate widths chosen by what the contradiction depends on
(uniform enlargement fails: real partial packings appear) -> A125's follow-up on S33/S02 from A116's pair radii;
(3) k0: target the SELECTED minimiser on W only (DRAIN-SEL(W)), not LOCK-FREE+(<4) for all packings; keep uniqueness
separate (Trump basin); (4) COUPLED moves (cluster screw, exchange, two-wall coupling, supply count) with EXACT
inequalities on neighbourhoods — single-square tests miss coordinated escapes -> A128 (Fable) dispatched with the
reviewer's success criterion (exact inequalities on neighbourhoods; trajectories count as nothing) on the sample:
7 converged-alive k0 supports, K01-K06, the two fully-held boundary packings, Trump as canary.

2026-09-07 A115 T6 done (0d4c79fd): warm re-solves complete over every reachable open k0 cell: 22/216 L1 + 13 L2 +
2 L3 + 10 A85/A99 nodes certified for 29.8 CPU-h = 1,023-2,372 CPU-h off the k0 tree (34-80x). 71 stage-A kill
candidates still lack the 900 s continuation (5 of the last 27 closed that way) -> a cheap follow-up chore.
12 converged-alive cells (tau = budget, minmass 1) are the true k0 residue sample -> handed to A128. budget.md k0
row: tree route 13,500 -> 12,000; total tree route ~18,500.

2026-09-07 reviewer note 5: Burns-Massaccesi (Aug 2026) net-orientation + shrunk-square exact verifier -> A129
dispatched as a bounded benchmark (12 CPU-h). Lab framing: sigma(delta) = 1/(cos d + sin d) inclusion = our CORE
lemma; margin cost ~ s*delta (1 deg cell at s0 costs 0.068 > the whole window 0.057), so it lives or dies on how
fine the net must be at tilt-coupled leaves. Payoff if it works: replay verification is HALF of an 850 s PASS node.
Not a route past A19's measure-method obstruction (reviewer and lab agree).

2026-09-07 A128 (c91ce1a4, docs/proofs/drain_sel.md): DRAIN-SEL(W) stated (selected minimiser, W only, a MENU of
moves; uniqueness untouched). Box-lemmas [T]: BOX-MOVE, BOX-GORDAN, CLUSTER-ROT, EXCHANGE-BOX (for-all-packings on
a box). RESULT: the cluster screw certifies NOTHING beyond single-square ROT at any r >= 1e-5; the EXCHANGE is the
only coupled move that works where every single-square move fails (9 corners). TWO-WALL trivial on a box; SUPPLY
vacuous by planarity. Residue held under the whole menu: lock 4.001525 (above 4), K03, K06 (= S02 pinwheel support),
l1_124, Trump (canary OK) -> below 4 every failure is a FLUSH re-fit (margin ~0): the flush population from the
box side. Named missing move: non-rigid column-straightening + row-slide field at the 4.001525-type frame, or a
depth-2 exchange with margin. Not composed; k0 budget row unchanged.

2026-09-07 PI reading of Y0036 (k5_11) vs pin bl10: most drawn tilts are geometrically impossible at most centres.
Checked exactly: lower half of the L1 box blocked at every tilt (tree logic-killed it); alive D2 bins feasible only
in a top sliver (y >= 1.491 upright, >= 1.505..1.521 at 82.4 deg) under the CW lean over bl10's corner (2,1); the
mirror lean is impossible for the whole D02/D06 bin. T5'' cannot empty it (box corner survives) = A123's live
finding. Lever PIN-CLIP (T5'''): shrink the centre box to the pin-feasible region per tilt sub-bin before the LP
(exact octagon intersections; frozen verifiers unchanged) -> A131 dispatched (offline corpus measurement + in-vitro
LP test on Y0036's children; no shard launch).

2026-09-07 PI reading of Y0186_D00_D00 (LP support figure): a support column intrudes into every hypothesis pose.
Checked exactly on the 4 alive L3 nodes: in EVERY node 2 of the 5-8 weight-1 support columns overlap the
hypothesis square at every pose (SAT gap -0.005..-0.029) yet clear the AXIS-ALIGNED core K(a) by +0.003..+0.045;
the tilted square protrudes ~0.21 beyond K(a) along the diagonals. Lever POLYGON CORE K'(B) = intersection of the
hypothesis square over all poses in the box (convex polygon; certified vertex-wise by pinguard's interval formula):
column pruning + certificate hypothesis + T5-polygon logic kill (K' meets pin core). Needs a v3 verifier clause
(v2 pattern) + Lean lemma polycore_meet_same_square. A132 dispatched (measure over 383 alive nodes; in-vitro LP on
10; spec). Composes with A131's pin-clip (clip the box, then K' of the clipped box).

2026-09-07 A130 (cd87ec6d): the non-rigid FIELD (BOX-FIELD-W) is the coupled move A128 named — kills the 4.001525
lock at all 8 intruders on the 1e-4 box. The 3 window holds (K03, K06, l1_124) survive every move: exact slide at
slot-like+flush corners = mode accumulation (Lemma MODE), blockers = wedged interior grains. Trump first-order
ISOLATED. Costs DRAIN-SEL(W) nothing (holds are k>=1 packings above s-hat; SLOT-GRAZER confines flush corners to a
thin slab below s-hat); costs the TREE a semi-algebraic leaf at flush stacks. k0 budget unchanged (12,000 / 0).

2026-09-07 A126 done: sat_selection axiom -> theorem; LocalDead S07/S02 in the kernel (reflected checker +
native_decide, 19 s / 67 s); LocalCompose.node_dead_of_yes_no + classKilledAt_of_yes_no proved; Y0230's 4 NO certs
replayed (11x frozen verifier). Remaining: CertCover hypothesis needs a rational cos/sin interval kernel -> cheaper
to RE-EMIT certificates in t = tan(theta/2) (rational cos/sin) — generator change (A119 code). BUG F-COVER: A120's
NO-certificate files round the zone OUTWARD -> ZONE not inside BOX by ~1e-7 on all 22 PASSing NO certs; fix = one
rounding direction + re-certify (queue with the A120 resume). E2: check_local.Checker.dead early-returns before its
capture hook (a generator trusting it emits incomplete covers). Elaborator, not kernel, is the Lean wall at 1e6 coeffs.

2026-09-07 A129 (f8ad68fc): net-orientation verifier (Burns-Massaccesi = two Aug-2026 BLOG posts on n=17, not
arXiv; same certificate object as ours, an atomic measure; their novelty = verifier: 181 orientations in t, B=0.9973,
per-orientation translation sweep, no LP/Farkas). Verdict: CROSS-CHECK only. s(11)>=3.82 and s(12)>=3.90 both PASS
an independent decision procedure (2148 s / 802 s; 3.5x the frozen verifier). As replay verifier REJECTED (median
15x slower; blow-up, never margin: 0/60). Lemma N3: exempt hypotheses on the UNIT square over the net cell; shrink
only the mass. budget.md D.6 + publication_checklist W7 written.

2026-09-07 A131 pin-clip (32d63560): exact clip (4 sinusoids in theta, rational in t, no epsilon) strictly
dominates T5'/T5'' (+21 two-pin empties). 132 of the 607 unclosed A57 nodes clip to EMPTY (112 by the deployed
trim) — a backlog because T5'/T5'' only run at emission; sweep running (A131 continued). LP on clipped boxes:
5/10 alive nodes to eta <= -0.5, 2 CERTIFIED (Y0036_D02, Y0186_D00_D00), 3 cert-FAIL holes. CAVEAT: recheck96
kills are LP verdicts (never certifies) -> the re-check's 11/23 are not certificates; A124 told to certify.
Deploy shape: after T5'', before LP; persist clip_* fields. Lesson (with A132's polygon core): use the exact pose
set, not its axis-aligned shadow.

2026-09-07 A131 backlog sweep (43da8a3f): 132 pin-clip kill certificates (t-parametrised replayable traces),
independent checker 132/132, 1.58M samples 0 hits; 20 need the two-pin joint clip. Clip vs T5'' contain each
other only on this corpus (Y0360_D06: T5'' empties by different single pins per sub-interval). RULE: never chain
eps_geo after a pin-clip (row-shrink pushes tau back to budget) -> resolver or depth. A57 owner folds the 132 in
at resume (PAUSED.md line). Git: shared index race — agents committing concurrently can swallow each other's
staged files; A131 soft-reset and re-committed own paths.

2026-09-07 A133 (4a7e5821): all 10 local certificates re-emitted in t = tan(theta/2): SHARPER (S07 2302->2140
leaves, S02 32570->16406; certified min 3.877108 vs 3.877092), independent checker 569k rows; LocalCertT.lean: 12
theorems (monotone cos/sin bounds = exact endpoint enclosures; w-bound lemmas retire the pi kernel; Bernstein
positivity posCheck_sound; C1 coverOk_sound). Remaining C2 selection cover, C3 RELAX, C4 variable map (~1,050 lines
reflection over Q, no transcendentals) -> A134 dispatched. Key insight: A119's LP tilt variable is the ANGLE,
Local.Box's is t -> arctan step unavoidable in theta; in t it is the identity. F-COVER outward rounding lives in
A112's caselp.py make_certificate (nofams clause, TDEN 2^24 +-1 unit, XDEN 1e9 nearest), not A120's runner; fix =
round the NO zone inward; the ZONE-in-BOX test must run at emission on the WRITTEN rationals.

2026-09-07 A132 polygon core (7d5e9070): over 506 alive nodes 22.3% of support columns (0.357 tau) and 20.5% of
pools are K'-only excluded; T5'''' logic kill fires on 64 (37 new). In vitro all 3 converged LP pairs KILL
(5.0 -> 4.0/4.5/4.0). ATTRIBUTION: 1/4 of excluded weight is the PINS' — stored pin core a = 0.49 (tight_a +
TIGHT_EPS) vs exact 0.49293; Y1038's kill lives entirely in that pin-core slop (A96's earlier all-poses filter
was on the conditioned box only -> 0 kills). Lean: core_meet_same_square takes arbitrary sets -> T5'''' kill = one
rational witness point + two vertex checks, no verifier change; LP-column exclusion needs a v3 polycores clause
(4-6 days). A135 dispatched: does the frozen verifier accept exact pin cores? certify the 3 kills.

2026-09-07 A125 (395549fe; agent did not push — coordinator pushed): S33 basin certified (0.2,10 deg) and
(0.05,20 deg), no Trump cut needed; S38 (0.1,10). Limiter = tilt-cell count at rho 20. Consumer = 1 node
(c0_Y0335): the SIXTH PIN BL(0,2) (k6_07 has it, trump5 lacks it) binds 1,065/1,421 alive supports -> lever =
promote BL(0,2) from pin to free box (mirror of A116-G2) or rho = 40. Protected-tier row unchanged. Agents may
refuse to push citing "publish" — the lab's standing rule is push at every milestone; the coordinator pushes.

2026-09-07 A124 (97aa4e9c): T5'' offline projection was RIGHT (159 emptied = 9.1%, 9.5% trimmed); A123's §4
mislabelled it; live L1 consistent (Fisher p 0.35). Schedule full-kills-only 13.3 -> 10.5 (10.6-11.7); rests on
the L2 rate 13.7% (untested live). The 900 s RE-CHECK IS NOT A LEVER: by the campaign's rule (eta < -0.005 tau)
night 11 -> 1 strict kill, day 21 -> 2 (already known); rest knife-edge |eta| <= 1e-9 => alive nodes are genuinely
alive-at-LP. recheck96 never certified and never wrote node jsons. Y0381: LPModel sets no time_limit -> h.run()
spins; guard = per-node process wall (a kTimeLimit exit must be CAP-not-a-verdict). Scoped sentinel:
pausegate.paused(base=OWN_BASE) (PAUSED.md §7a); "A57 PAUSE set" no longer implies nothing runs.

2026-09-07 A135 (b65073e7): FROZEN VERIFIERS TAKE THE CORE HALF-SIDE a VERBATIM (never see the box; only check
0<=tm<=1, a>0) -> soundness of a is the EMITTER's obligation -> exact cores certifiable today. Exact pin core
0.49293 (vs 0.49 stock: Box.core() bounds by the circumscribed disc). Conditioned core: tight_a within 0.3% of
exact; polygon adds another x1.05-1.14 (half of A132's 1.225 recoverable inside the frozen schema). 3/3 in-vitro
kills CERTIFIED: Y0871 + Y0281_D03 under frozen verify_case with exact cores; Y1038 needs verify_case_v3.py
(polycores clause, imports the frozen class, regression 24/24, --replay byte-identical). PolyCoreT5.lean clean,
checkVertexInPBox_sound proved. NEXT CHORE: re-emit the ALIVE population with exact pin cores (414 x 240 s ~ 28
CPU-h), no verifier/Lean change. Shared git index race hit again (A134's staged files swept, repaired).

2026-09-07 A134 (99bbdd66): C2 selection cover, C3 RELAX (both row families), C4 variable map (geometric half) all
THEOREMS in LocalCertT2.lean (36 theorems, 3 standard axioms; no missing library lemma). In t, axis_decomp is an
algebraic identity (linear_combination vs cos^2+sin^2=1). Residue = ~1,000 lines of reflected plumbing (tree walk,
row builder rowsOf + outward quantisation, index map vi=2i+1, leaf replay) -> A138 dispatched. Traps: posCheck
compares lists (trailing-zero shape); elaborator wall (32 entries per private def). Bernstein depth 0 suffices for
every envelope -> identical trees to A133's. Extra fields S_lo/S_hi/K now emitted with positivity certificates.

2026-09-07 A138 (aed1f864): LocalCertT3.lean (1,858 lines, no sorry): localDead_of_certOk — LocalDead of a
neighbourhood from TWO decidable checks (certOk + leaf check) and nothing else; roster standard + check_3_82's
native_decide via lb_382. Structural: the n-ary selection branch must be binary sel1 nodes (List field gives no IH);
bisection nodes need not store children's cells; A134's 600-line R2 collapsed to one lemma via minL. R4 (data as
Lean literals + native_decide; kernel decide gets stuck on certOk) -> A139 dispatched. To turn A120/A136 closures
into ClassKilledAt: per-node YES bridge hyes (node data) + replayed NO certs with ZONE-in-BOX (A136).

2026-09-07 PI reading of A140's s3_far page: K'(h3) within 1 of the right wall (0.978), pocket to K'(h2) 0.07,
pinch 0.18 -> TR corner reachable only by the conditioned h2 -> singly met -> K0-FREE -> the cell is DEAD. A118's
lane test said UNDECIDED because it used axis-aligned cores; with POLYGON cores the pinch appears. Lever: lane test
with K' (LANE + M <= 1) on every corner of every open k0 cell -> A141 dispatched. (Note: my sampled K' is an OUTER
approximation — the intersection over fewer poses is larger — so wall gaps need the certified polygons.)

2026-09-07 A140 (73eaf5e2): k0 gallery v3 (docs/shadows/k0v3/, 12 pages, review_k0v3.csv, README). Polygon core on
k0: column exclusion fires on ALL 12 (K'/K(a) area up to 1.47 on 15-deg windows); K' vs container: nothing; K' vs K':
only s3_far has >1 box (k0 L2 cells REFINE the same box — one square), pairs disjoint. In vitro under K': 8/12 drop
below budget, s3_far CONVERGED at 6/7 (LP-dead under K'); exact axis core recovers 50-100% of K's excluded weight on
9/12 -> exact-core arm dispatched (certifiable under the frozen verifier). Lane: 5/12 carry a two-meeter cover on
TR(0,0) (3 never measured by A118). The two levers cover the residue exactly: no cell in neither.

2026-09-07 PI symmetry point: the k0 tree already quotients D4 x S11 via an EXISTENTIAL interior-zone hypothesis
(A24/A38: fundamental triangle x 6 tilt windows = 216 cells, D4 transfer machine-checked). The PI's alternative
canonical choice = condition on the BL CORNER INTRUDER (root lemma free for k0: K0-FREE dead by teleport, else every
corner met by a tilted intruder; D4 -> one corner). Wall-strong leaves (polygon core, clip, K' lane) bite hardest
there; the two covers compose (a cell must survive both). A143 pilot dispatched (level-1 kill rate vs 22/216, 2 CPU-h).

2026-09-07 PI refinement: corner-first root + DOUBLY-MET corner = condition on BOTH BL meeters (Q1 intruder, Q2
second tilted meeter disjoint from K'(Q1), both in the corner cell) -> pair cells nearly all geometry-killed (hook
pairs); LP with two conditioned squares, budget 9. Folded into A143 as T1b/T2b.

2026-09-07 PI prediction for the corner-first doubly-met k0 tree: ONE deep lineage = Trump's shadow entering via
its single non-simple corner (TL in trump5's frame; -> BL after D4); all other pair cells die (hook pairs only
survive). The lineage ends NOT by a basin (Trump is not in k0) but by the K' LANE kill: as the pair cell shrinks
toward Trump's TL pair, the other corners are forced to single simple meeters -> K0-FREE -> dead. A143 told to
track the Trump pair cell and the depth at which the far corners' lane counts close.

2026-09-07 A142 (d6c2f5f4): A57/A60 review gallery docs/shadows/a57v3/ (60 pages, README, review_a57v3.csv).
Population after today's kills: 607 work-owing -> 465 survivors (lists overlap heavily: 253 entries = 142 nodes).
FREE KILL: running A131's clip with the EXACT pin core (0.49293 instead of 0.49) empties 17 more A57 survivors and
narrows 272 of 465; A60 had NEVER been clipped (exact pins, a_pin = 1/2): 34 of 283 nodes clip EMPTY, 143 narrow.
376 of 1,240 impossible columns on the pages are against exact PIN cores (the pins' share). Trap: a hypothesis box
is a pin only when th1 == th0 (A60 depth-2 nodes carry a tilted previously-conditioned square in the pin slots).

2026-09-07 A142 follow-up (f5f2f1c1): 51 exact-clip kill certificates (17 A57 + 34 A60), checker 51/51, 612k
samples 0 hits; A57 survivors 448 (323 ALIVE + 125 FAIL); 14 of A60's 34 are T5'' alone (never applied to A60).
Appended to A57 PAUSED.md and A60 ledger.md for fold-in.

2026-09-07 A139 (414507cc): localDead_s07_t / localDead_s02_t are LEAN THEOREMS (LocalDead of S07 (0.1,40) and S02
(0.2,10) at s0 from certificate data; roster standard + native_decide + check_3_82; builds 571 s / 6,707 s). Catch:
A134's certs used the exact w-range for selection exclusion, Lean's wLoQ enclosure is coarser -> re-emitted with
the Lean-side exclusion (+37% leaves S07); permanent fix = exact w-range as a decidable enclosure in LocalCertT2.
Reviewer item 1 (finish the Lean checker + composition) is now closed except per-node NO replays (A136).

2026-09-07 A143 corner-first k0 pilot (2d594e0d/123ea093): DONE-MIXED. Sound root; pair geometry kills 82% of
11,772 pair cells in 90 CPU-s; BUT the LP in survivors has ~no slack (single root eta 0..-0.63; pair root eta
-0.08 at budget 9: a second conditioned square at the same corner buys no slack for a unit of budget); priced
3,800-8,900 (single) / 8,000-18,800 (pair) vs 12,000 interior -> not cheaper. K' lane leaf cannot fire at the
conditioned corner (M = 1). Trump: non-simple corner = TL CONFIRMED (singly met at BL/BR/TR on the plain box) but
K0-WIDEN's pad (a_w = 1.0255) makes every Trump image doubly met at all corners -> the lineage can NEVER die by
K0-FREE; terminal mechanism = landing + scale tube as in the interior tree. Correction: the k0 root has NO simple-
square tolerance (Lean OccupiesSlot exact). Two of the twelve alive cells (l2_p74_001, s3_far) have NO surviving
BL pair in their supports.

2026-09-07 PI reading of Y0147 (a57v3): a horizontal line 0.99 below the top crosses opposite sides of FOUR
squares -> side >= 4. Lever GUARD-LINE ROWS: for any line, chords of a packing's squares sum to <= s (disjoint
intervals); row over placements with pins' exact chords (=1 through the pin core's height range) and the
hypothesis square's MIN chord over its box (>= chord of K'); the LP today treats H as its 0.93-wide core and packs
three unit chords beside it. Needs a v3 verifier clause + Lean chord_sum_le_side / minchord_of_box. n-general:
kills "stack of ceil(sqrt n)" configurations. A144 dispatched (Y0147 control, offline violations over 448, 20 LPs).

2026-09-07 A140 exact-core arm (476f9108): s3_far CERTIFIED DEAD under the FROZEN verify_case with exact cores
(tau 6/7 converged, cert 6.983 < 7, PASS 4 s) -> k0 converged-alive residue 12 -> 11; kill candidates l1_148,
l2_p65_101, l2_p65_111 (below budget, unconverged). Pages regenerated: 3 cores per H, panel-3 bins as outlines,
census partition fixed; 117/139 impossible columns dropped by the exact core alone, 22 only by K'.

2026-09-07 PI reading of Y0241 (a57v3): pockets below/bottom-right of H hold no unit square. Confirmed: 4 of 5
support columns overlap H at every pose (already red-dashed); feasible-centre map: nothing fits below/right of H
(bl10-top to H-bottom <= 0.69; H-right to wall <= 0.7; floor gap bl10..BR = 0.877). The certifiable form = A135's
v3 box exemption (every placement in a box meets K' or a pin core). Systematic version: rank survivors by the
support weight impossible under H, re-solve with exact cores + K' in that order -> A145 dispatched (2 CPU-h).

2026-09-07 PI reading of k5_16 Y0460: smeared 56-column fractional support = the measure relaxation spreading a
square's mass over neighbouring grid cells (not a solver bug); ~0.5 weight axis-aligned in slot BR(0,1). A second
BR(0,1) meeter needs a CW-leaning square below H's right side, excluded by K'(H) -> BR(0,1) singly met -> snap the
near-simple meeter to the exact slot -> k6 extension class (all dead on W) -> node dead. = the K' LANE test on
USABLE SLOTS (not only corners). A141 told to extend to slots over the A57/A60 populations, Y0460 first.

2026-09-07 22:05 A61's k5_13 resolver (resolve61.py) had HUNG inside an LP since 09-06 05:54 — 40 CPU-h on one
spinning thread, no output — the lpbox no-time-limit bug (A124/Y0381) hits campaigns too; killed by the
coordinator; A146 restarts k5_13 under a per-LP process wall (1,500 s, CAP never a verdict). RULE: every LP call in
every driver needs an external wall until lpbox sets time_limit; check long-running processes' log mtime vs CPU.

2026-09-07 PI reading of l2_p114_001: the corner nearest H (TR) can never be doubly met. A141's K' lane gave
NEAR-MISS (LANE 1, M 1). New leaf CONDITIONAL LANE: split B into B_meet (H meets the corner cell) / B_miss; in
B_miss LANE <= 1 => singly met => K0-FREE; in B_meet recompute LANE with K'(B_meet) (bigger near the corner) -> 0
=> H alone meets => dead. Both cases geometry only. A141 told to run it on every NEAR-MISS corner/slot.

2026-09-07 22:40 PI to bed; machine released until 07:30 2026-09-08. Night: A137 (A57 owner: fold-in of all
kill lists, exact-pin-core re-emission first, new hooks, deepen for the L2 rate, pause 07:00), A148 (gallery v4:
GEOMETRY panel = feasible-centre region shaded + pockets + guard lines + lane tags; SUPPORT panel from the exact-
core re-solve; NEAREST panel with s0 overlay; WHAT-TO-LOOK-FOR line; k0v4 now, a57v4 at 06:00). PI's gallery
brief: less busy, impossible overlaps should not appear at all, notes on what each plot IS; the question is
"is there a shortcut that geo-kills the node without more LP", esp. for k0. Morning digest owed: ledger update,
night kill table, the two galleries.

2026-09-07 A141 (1f9de0ef): K' LANE on k0: 47 kill cells (27 L1, 9 L2, 3 L3) + s3_far by a PAIR leaf (h0,h1
share a rational point at every pose -> same square -> contradictory hypothesis; unconditional (C) leaf); 1,130-
2,620 CPU-h credited to the k0 row. TRAP: M counts squares that can REACH the corner, and a conditioned square
reaches far beyond its core (s3_far: h3 reaches TR too -> M=2). 44 near-misses: 28 have REALISED 2-crowds (free +
conditioned both meeting the widened cell) -> no refinement can kill them; l2_p114_001 is one (gap 0.0145) -> the
PI's reading there is refuted; the joint split is implemented but never fires on this corpus. A57/A60 SLOT LANE:
155 (node,slot) kills on 145 distinct A57 nodes in the first 1,050/1,693 records (LANE_K'=0, M=1), 135 certified;
Y0460 itself NOT a kill (34k free poses). Sweep shards were killed by the PI at 22:10 (I misattributed to A144);
A141 told to resume + certify + measure overlap with clip kills. Lean: two new obligations LaneCoverSound, K0Widen.

2026-09-07 A145 (b250191b): Y0241 CERTIFIED DEAD (tau 5.0 -> 3.25, v3; frozen fails w/ 32 holes). 18 re-solves:
10 LP kills, 9 certs (3 frozen). The impossible-weight fraction is a THRESHOLD gate: >= 0.60 -> 4/5 kill; < 0.45
-> 0/7 move. Queue: 98 survivors >= 0.60 (~9 CPU-h). A137 told to order the exact-core re-emission by it.
Shared-index race again (A148's commit swept A145's files; content intact).

2026-09-08 ~00:30 A146 (5d207001): k5_13 CLOSED on the original A56 parametric certificate with 58 slabs of 1e-3
(58/58 PASS, 2.8 CPU-h) -> WINDOW SCOREBOARD 52/52: THE WINDOW LAYER IS DONE. The row was never hard: A56's FAIL
was a 28x over-width slab (law: w_min 1.56e-5, d_pose 41 -> width_max 0.002). RULE: a parametric FAIL with 0
holes and a depth-limited worst witness is a slab price, not a certificate price — one 75 s probe settles it. The
A61 re-solve route was dead for a measured reason (dtau/deps 119-132 vs 57-90 on converted rows). Hang mitigation:
the two-stage protocol itself; supervise146.py wall (silence AND no live descendant) as backstop.

2026-09-08 A144 guard lines (093cc105): 86/448 survivors violate a guard line offline (Y0147 +0.128: pin + H
(minchord exactly 1) + two LP free columns = 4.0055). As an LP row active on 2/20 (Y0147 eta -0.12; Y0101);
UNEMITTABLE under the frozen chain (certify.py rebuilds from atoms) -> v4 clause needed (spec + Lean shape, 0 new
axioms). BY-PRODUCT: exact cores alone kill 15/20 (selected) vs deployed cores 0/6 -> the exact-core re-emission
is the lever. Read z (row activity), not delta-tau.

2026-09-08 A141 final (c0578941): SLOT-LANE kills 188 A57 nodes (96 k5_11 + 92 k5_16) + 56 trump5, 243/244 new
beyond clip kills (disjoint leaves); 294 certs. A118-O1 is NOT a blocker for the composition (only the broader
slack-pin reuse is excluded). A57 survivors before the night: 448 - 187 = ~261. The A141 sweep shards were in fact
NOT killed at 22:10 (my process listing was wrong); they finished.

2026-09-08 A136 (7bc5965c): F-COVER fixed (NO zone inward, YES box inward — shrinking the YES box strengthens the
hypothesis; one trivial Lean obligation: LocalDead antitone in the box list); 22/22 re-certified; 15/35 in-N nodes
CLOSED (was 4); certifier at rounds 6 no longer binding (54 PASS, 6 CAP, 0 FAIL). TRAP: a bound that is an exact
geometric fact (1/2, s0-1/2) must be written exactly, never rounded (rounding it failed all 7 BR(0,1) certs).
closures136.jsonl = filled-in LocalCompose instantiations (Lean replay away).

2026-09-08 06:50 A148 gallery v4 pushed: docs/shadows/k0v4/ (11 pages) and docs/shadows/a57v4/ (60 pages), each
with the GEOMETRY panel (certified inner/outer feasible-centre region, pitch 0.02, Lipschitz margin), pockets,
guard lines, lane tags; new LP-free DISK BOUND (each square contains a disk of radius 1/2 -> cap on how many fit
in green+undecided) — does not bite yet (k0 17-18 vs 10; A57 7-11 vs 4-5); loose because of the undecided band
(finer grid / interval tilt sweep would tighten). No node killed by the drawing. Uniform k0 shape: 10/11 have
K'(H) within 1 of the right wall; 5 leave TR a NEAR-MISS. Bookkeeping hole: A142's A60 clip kills exist only as
certs/a60/*.clipkill.json (no jsonl) -> ~150 ids missing from jsonl-built kill lists; RULE: *.clipkill.json = kill
record; *__exall.json is not.

2026-09-08 07:00 A137 night shift 2 (b91a2813, PAUSED.md v3): fold-in 492 A57 rows (NEW closures: clip backlog
111, exact-clip 12, slot-lane only 7 — A141's 187 were mostly already-PASS nodes; A145 7; A135 6). Fresh children
3,034: 26.3% dead by geometry (L2: 27.5% vs the 13.7% assumed; L1 LP kills 78.8% of decided). Exact-core re-
emission: 46/161 CERTIFIED under the frozen verifier (28.6%; A145's frac gate: >=0.6 37.9%, 0.30-0.45 still 23.8%
-> keep in queue). Work-owing 632 -> 406. TRAP: an id is not a node — L1 (eps-fat pins) and G1 (delta 1e-2) trees
share ids; kills transfer only downward in the pin core (2 of A142's 17 don't transfer to G1). T5'''' fired 0 on
A57. Queue: 142 ALIVE un-re-solved + 2,184 LP jobs (queue_bc.json). Schedule re-derivation owed (A149).

2026-09-08 PI: corner tree v2 = condition on ALL FOUR corner intruders at once (K0-BLOCKED means all four met);
each corner's band is narrow (far enough for a second meeter — A143's surviving pair cells; close enough that the
other 10 fit in the L-shaped remainder — A148's disk bound); branch as a PRODUCT of band cells (D4 / 8) and kill
combinations by geometry (adjacent-intruder overlap, guard lines along walls, disk bound with 4 cores removed and
7 squares to place, K' lane per corner). A150 pilot dispatched (survivor counts per stage; LP with 4 conditioned
squares at budget 7: does it buy slack where one corner did not?).

2026-09-08 PI asks for a basin around the S02 pinwheel that rejects LP snaps = the local certificate + YES/NO
split (exists; 15/35 in-N closed). Limits: radius (real packings beyond ~0.2), consumer count (35/252), NO cost.
A151 dispatched: exact-core kill rates BY FAMILY from the night (is the pinwheel's 0.0097 slack now LP-visible?),
asymmetric N grown per coordinate until the first real packing (reviewer item 2), consumer count and price.

2026-09-08 PI reading of Y1117 (BR(0,1) singly met): A141 said LANE >= 2 because a 55-deg square grazes the cell by
0.003. Refinement: the snap only needs SOME admissible placement of the 6th simple square (pin tolerance delta)
free of others -> a grazer shallower than the tolerance does not block -> meeter := intersects the TOLERANCE-SHRUNK
cell (slot analogue of the exact pin core). Prerequisite (A118-O1): the k6 extension classes must be dead in
SLACK-pin form. A152 dispatched: soundness + prerequisite check + re-run on the alive population.

2026-09-08 PI on Y1117: the LP drops H + 3 into one pinwheel grain; wants a cheap grain pricing. Lever
COVER-NUMBER leaf: disjoint unit squares have centres >= 1 apart (each contains the radius-1/2 disk) -> if the
certified outer feasible-centre region F (A148's green + undecided) is covered by k pieces of diameter < 1 and
k < budget, the node is dead, LP-free (exact version of A148's disk bound; same-tilt refinement: L-inf >= 1 in the
rotated frame, conditional on Lemma TC's common tilt). A153 dispatched over the alive population + k0's eleven.

2026-09-08 A150 four-corner product (d993979b): the band is NOT narrow (206/216 cells; whole zone); product
geometry cuts 15.6% of 1.5e9 tuples; guard/disk/separation bounds kill 0. BUT four corners DO buy LP slack:
median eta -1.0, 7/13 converged kills, 4 certified (vs 0 for one/two squares at one corner); Trump canary alive.
Product priced out (>= 4e5 CPU-h). Mechanism to consume: (R6) widened corner boxes 1.83 > sqrt2 apart -> no
square meets two -> K0-BLOCKED forces >= 8 of 11 squares to meet a corner box -> ONE counting row valid for every
packing (A154 testing on the k0 eleven + trump5's non-simple corners). A150 wrote no registry/LOG rows (A154 adds).

Depth lemmas on file (PI asked 2026-09-08): Lemma ID (A89, tilt_floor_k0.md s7): depth < delta at a corner strands
(1-delta)^2 of E(m) = m^2 - 11 < 4.0318; CERTIFIED on W: no packing has all four corners SHALLOW(0.3) (>= 1 corner
has a square within 0.7 of the corner point); 3-shallow open. SLOT-GRAZER (A130): at m <= s-hat - delta no corner
intruder has mu_c <= delta/(1+sqrt2) (vanishes near s-hat). JAM-0 (A89): axis-aligned blocker at offset g pins its
partner's tilt (sin <= g) and depth. None bounds the SECOND meeter's depth. Use: root corner = deepest corner (by
rotation) -> band restricted to depth >= 0.3; shallow corners are NO-families in the case-LP.

2026-09-08 THE K0 PAD EXPLAINED (k0_route.md s4.1, Lemma K0-WIDEN): the k0 tree at s0 covers the window by
DILATION (lambda = s0/m); a square meeting the exact corner box at side m meets only the box widened by
w = (lambda-1)(1+sqrt2/2) at s0 (w_max 0.0255). At a fixed side w = 0; on a 1e-3 slab w ~ 5e-4. The PI is right
that at a fixed side the corner-root tree needs only TWO TRUE INTRUDERS per corner (exact cell: singly met ->
teleport -> k>=1 -> pin trees, trump5 included). => SLAB-WISE corner-first trees with near-exact cells; A150's
fat band (206/216) was measured at the full pad. A155 dispatched: band vs pad, product survivors, LP at budget 7,
slab-wise price.

2026-09-08 ~10:00 PI at work (remote desktop only): machine released except ~3 threads (~20 total) -> total
python processes <= 17. A149 scaled to 4 LP workers (cap 30 CPU-h, FAIL population next); A156 day shift runs
A57's queue_bc.json (2,184 LP jobs) + deepen at 5 workers until 23:00 or the PI's word, then PAUSED.md v4.

2026-09-08 BOX RULE (PI): lab work confined to the 16 P-core threads = logical CPUs 0-15 (affinity mask 0xFFFF);
E-cores 16-19 are the PI's (remote desktop, VS Code). Every launched worker/subprocess gets ProcessorAffinity
0xFFFF; ceiling 16 lab python processes. i7-12700K: 8P+4E = 20 threads, 31.7 GB RAM; ~6 usable LP slots
(memory-bound).

2026-09-08 A151 (6c56a342/882d5b93): exact-core re-solve kill rate BY FAMILY: S02 36.8% (best on the stubborn set,
but marginal: median tau 4.75, 30% LOST/TOO-TIGHT), S01 25.5%, all 25.9%; T5'''' fired 0 on A57; A137's
"exact-core" lane mixed fresh children (tag corrected). S02 alive: 99 (36 already failed the re-solve). Asymmetric
N for S02 certified: f1 +-0.40/+-0.25/+-40 deg (10x volume) DEAD, no real packing found inside any grown N — the
limit is COMPUTE (wall caps), not geometry; consumers 96 (42 alive) vs 72 (32). Symmetric N still OWES 26 closures
never run (25 CPU-h) -> A136 resumed on the 26 + 10 (asymmetric). Rule: re-solve first (0.39 CPU-h/kill), split
the survivors (1.39 CPU-h/closure).

2026-09-08 A153 cover-number leaf (a7d20381): ZERO kills on 322 nodes (60 a57v4 + 11 k0 + 251 alive A57):
cover number median budget+4; the obstruction is a FLOOR (F_outer always holds >= budget points pairwise >= 1
apart), so no piece shape / grid refinement can help; Lemma TC (common tilt) 0 sound kills (Y0083 needs 4 only at
exactly t = 0). k0: cover 18-22 vs 10 — never bites with one conditioned square. Priced at zero as a lever; kept
as a free gallery assertion (2-4 pieces tighter than the disk bound). Lemma CN + Lean shape written, 0 new axioms.

2026-09-08 A155 (4712cb37): the K0-WIDEN pad is a 2% effect on the corner band (202 vs 206 of 216 cells at pad 0)
and 4.2% on the product; the PI's geometry is right at POSE level (2-crowd occupancy median 0.0125 at pad 0 vs
0.16 at full pad; 90/216 cells hold no witnessed 2-crowd) but a level-1 box cover cannot see it, and refining
explodes the product (x105, x1300). Slab-wise corner trees pay the whole-window cost PER SLAB -> >= 5e6 CPU-h,
priced out. A08's 3.82 measure certificate kills only the single side 3.82. Corner-first k0 TREE is dead as a
tree; what remains is the R6 counting row (A154) and four-corner conditioning as LP slack.

2026-09-08 A152 (c0a71bbb): (1) the k6 extension classes are certified with EXACT pins only (tolerance 3e-8, no
pin boxes) -> A118-O1 unrelieved; slack-form re-certification would cost A60 1-15 / A57 2-30 CPU-h (4 classes
near budget may not re-solve). (2) MY shrunk-cell argument was FALSE: four grazers through four faces block every
admissible translate; the sound fixed-translate form is structurally vacuous (completable slots are wall/pin-
backed). (3) Y1117's BR(0,1) is a GENUINE 2-crowd (pairs with gap 0.24-0.33) — the PI's eye was wrong there.
(4) In the delta = 1e-2 family the exact snap t = 0 is inadmissible at 14/16 usable slots; A141's kills remain
sound for the class-S composition only (A118 s2). Zero gained; 6% of A141's cells fail in the slack regime.

2026-09-08 PI reading of c0_Y0076 (trump5): TL(0,0) singly met. A141's sweep had it UNDECIDED with lane_lb 0
(no free meeter sampled) and M 1 — the certifying cover was SKIPPED for speed. Backlog: 196 such cells on 174
distinct alive A57/A60 nodes (k5_16 BL(1,0) 40, TL(1,0) 27; k5_11 BL(1,1) 23; trump5 BR(0,1) 22 ...). A157
dispatched to certify them (c0_Y0076's TL(0,0) and BL(0,2) first).

2026-09-08 A154 R6 row (4743d13a/6b734d1b): (R6) IS A115's d0 row verbatim (already measured: 1 attributable
kill); 0 kills on the eleven, the near-misses, random L1 cells, and trump5's TL row; eta goes UP under it
(c >= B in 23/23 runs: the widened corner boxes cover 28% of the container where a covering measure is cheapest
anyway). Lemma ID's row adds nothing (vacuous at 4 corners; joint runs +3.8 eta). Row licensed nowhere in the
protected tier (k5_16/k4_13 have zero non-simple corners; k<=4 classes' corner extensions are protected classes).
Deepest-corner root: factor 0.53 on ONE corner (A150's product 5.3e6 -> 2.8e6 CPU-h). THE CORNER-FIRST LINE IS
CLOSED. A150's "four corners buy slack" came from four conditioned squares as CORES (budget 7), not the row.

2026-09-08 A157 (54efe66c): the 196 UNDECIDED slot cells are NOT kills: 86/179 realise a free pose at 400k draws
(c0_Y0076 TL(0,0): a free square at 29.4 deg clears K'(H) by 1.1e-2); covers on the 93 survivors: 0 kills, 1
near-miss, 24 unclosed (frontier doubles per depth). Correction: the covers were not "skipped" — the LANE cover
returned None on open-budget exhaustion and reported cover_open = 0 misleadingly. Lever: sampling decides a cell
in 2 s; cover depth costs 35+ s and decided none. Reading trap: a free tilted square can reach a slot past H
while clearing it by 1e-2 — invisible on a page.

2026-09-08 PI diagnosis of c0_Y0076: the LP is alive only because it puts mass on the near-simple TL SLOT square
AND counts H (+ the tilted square above-right of H) as meeters — no single packing does both. Leaf = YES/NO split
on the slot box S (near-simple poses): YES -> conditional lane with K'(S) as obstacle -> singly met -> teleport;
NO -> NoFam(S) exclusion (A112 nofams via A136's wrapper) -> re-solve -> the forced pair strands the left region.
A158 dispatched (c0_Y0076 first; then top 20 alive nodes by support weight in a usable slot's S box).

2026-09-08 PI on c0_Y0215 ("should snap into BL(1,1)"): H IS the BL(1,1) near-simple square (box centre 1.45,
tilt 82-90) sitting 0.12 down-left of the slot; the snap fails because H pushed to its cell's bottom-left leaves
top/right strips where the LP's grazer columns (1.6,2.34) and (2.33,1.61) rest — a legitimate 2-crowd (A141
witnessed it). Node alive-at-LP at tau 5.5/5. Tool: exact-core re-solve (A60 pins are exact; H's stock core 0.42
vs K' nearly the full square at 8 deg). A60 was never re-emitted -> added to A149's queue (c0_Y0215 first).

2026-09-08 PI on c0_Y0787 (trump5; H at (2.22-2.36, 1.38-1.52) tilt 41-53, tau exactly 5/5): forcing BR(0,1)
doubly met strands the space right of H. A141: BR(0,1) NEAR-MISS (LANE 1, M 1). Added to A158's slot-split set.
Pattern: NEAR-MISS slots with H adjacent are the slot-split candidates (YES: slot square sole meeter; NO:
NoFam(slot box) forces the H + second-meeter configuration).

2026-09-08 PI on c0_Y0959 (TR(0,1) "singly met"): H reaches into TR(0,1) by 0.12 and two disjoint grazers from
below also meet it -> LANE >= 2; the reading fails on the touch definition again. RULE for readings: "met" =
interior intersection, any depth; grazers from an adjacent region count. The slot SPLIT (A158) is the tool for
"the LP drops a full square into the slot" nodes. c0_Y0959 added to A158's set.

2026-09-08 PI on k5_11_interior_Y0130: LP placements inside the polygon core (7/10 columns K'-impossible, w 3.5)
+ TR(0,0) NEAR-MISS -> "strict polygon exclusion leaves TR(0,0) singly met". Pulled to the front of A149's exact-
core queue and added to A158's slot-split set (TR(0,0)).

2026-09-08 PI on k5_11_interior_Y0147: H as a TR(0,0) meeter forces a second meeter that strands most of TR(0,0)
-> slot split (A158 set now: c0_Y0076, c0_Y0787, c0_Y0959, k5_11 Y0130, k5_11 Y0147 + top 20 by slot weight).
A141: TR(0,0) and TL(1,0) NEAR-MISS (LANE 1, M 1) on Y0147 — the near-miss-with-H-adjacent profile every time.

2026-09-08 PI on k5_11_interior_Y1110 (H central at 41-53 deg; TR(0,0) UNDECIDED lane 1 M 1): doubly-met TR(0,0)
strands most of a unit square in the upper right -> A158 slot split (sixth node). Y0275: the PI's "quadrilateral
pocket with all sides < 1 and one FIRM side (H's polygon edge) holds no square centre" — being tested numerically
(background job) against A148's green cells left of H.

2026-09-08 PI on k5_11_interior_Y0275: "a whole unit of LP weight left of H" = column (1.374, 2.428, 73.5 deg),
IMPOSSIBLE under H at every pose AND overlapping bl01's exact pin core — kept by the stock-core pruning; 3 of 5
weight-1 columns impossible (frac 0.6). The pocket left of H at H's height is dead by the per-centre all-tilt
map; the only feasible centres left of H are the strip y 1.49-1.63 (parallel nesting under H, clearance 0.036).
General lemma "quadrilateral with sides < 1 and one hard side holds no square centre" is FALSE (diamond in a
0.99-square at (0.25, 0.495) crosses 3 sides, misses the 4th, touches no vertex). Y0275 pulled forward in A149.

2026-09-08 A148 regeneration (864d314d): undecided now grey stipple (it was overstating the free set by ~1/5);
witnessed free meeters drawn per slot/corner (10 on A57/A60, all on cells A141 had as lane_lb 0 — including two
DISJOINT PAIRS: Y0865 BR(1,0), slack0.02_c0_Y0272 BL(0,2)); red-dashed columns now say if they also overlap an
exact pin core (356/966 on A57/A60). BUGS FOUND: A141/A157 poses are in the CELL'S CORNER FRAME (transport by the
corner's D4 map; reflections negate the tilt) — my earlier reading of their witness coordinates as container
coordinates was wrong; A141's t2_a5760 rows are per NODE with a nested cells list (per-cell reads yield nothing —
why the lane tags read n/a before). Box at the 16-process ceiling (A137/A156 shards x6+2, A149 x4, A136 x3).

2026-09-08 PI on l1_124 TR(0,0): two squares can touch the corner but are mutually exclusive -> singly met.
A141's t5_twocrowd claims a realised pair (free (3.365,3.368,0.88) + H (2.473,2.489,61.3 deg), gap 0.018) but
A148's transport shows H reaching -0.026 (NOT meeting) and my hand check agrees — A141's two-crowd witnesses may
be bogus (corner-frame / units). A159 dispatched: exact re-examination of all 28 claimed two-crowds, the joint
split with K'(B_meet) on failures, canary l1_153 first (must survive).

2026-09-08 A158 slot split (033c48b9): c0_Y0076's NO child (NoFam(S), S = slot box (0.10, 10 deg)) is DEAD
(tau 5 -> 4, certified frozen) — the PI's diagnosis half-confirmed: the node provably places a near-simple square
in TL(0,0). The YES child via the K'(S) lane leaf is REFUTED on all six (a free meeter clears K'(S) = the
intersection over the whole S box while overlapping every individual pose — 0 realised pairs in 600k draws); per-
piece repair ~400 CPU-h/cell. Population: 1,238 of 1,693 alive records keep tau >= budget on a dual square inside
some usable slot's S(0.10,10) — huge. Top-20 split: NO-only 1, neither 140 (6 raw NO kills were exact-core
artefacts). NEXT (sent): the YES child as an LP NODE with two boxes (H + S), budget 4, exact cores + K' pruning.
Correction: A141's NEAR-MISS-OR-WORSE = early-exit branch (covers skipped), not certified NEAR-MISS.

2026-09-08 PI on the YES child (H + slot box S as two conditioned bodies): clip each box against the other's
exact core (A131's pin-clip with the other core as the pin) BEFORE the LP -> smaller H box -> larger K'(H) on
H's lower-right -> pinches the LP's 4-square load path on the right. Sent to A158. General rule: in any multi-box
node, mutual clipping of boxes against each other's cores precedes the LP.

2026-09-08 PI on c0_Y0076's YES child (an S02 pinwheel shadow, LP would stall): with a square in TL(0,0), clip
H -> K'(H_clipped) grows -> the tilted meeter above-right of H can no longer reach TL(0,0) -> LANE = 0 -> the slot
square is the sole meeter -> teleport up in k -> dead by geometry. Sent to A158: lane leaf on the mutually clipped
cores BEFORE the LP. Pattern: CLIP-THEN-LANE on the YES child of a slot split.

2026-09-08 A158b (5e7edfab): the YES child as an LP node is STRUCTURALLY NEUTRAL — the slot square removes one
unit of dual packing AND one unit of budget (all 12 sub-cases converge at tau = 4 = budget; dual weight in S is
exactly 1 on 730/1,238 records) -> the population split is not worth buying. Mutual clip works as the PI
predicted (Y0787: H kept 0.50, K'(H) x1.13) but the LP framing's CLAMP of S to [1/2, s0-1/2] moved the lane test
more. Y1110: LANE_K'(C | S, H_clipped) = 0 CERTIFIED (first empty conditional cover) but the M half cannot
discharge for INTERIOR H (no prune fires). Gate added: pairwise-disjoint cores over ALL boxes (A135's ExactHyp
checks only cores[:n-1]). Slot-split lever closed except c0_Y0076's NO-only certificate.

2026-09-08 A159 (446ed81f/5b5f8097): canary l1_153 CLEAN. A141's 28 two-crowd witnesses are CORRECT and
container-frame (my "bogus witness" suspicion was wrong): the -0.026 on A148's page was the K0-WIDEN pad (A148
measures against the plain unit cell; the leaf uses the widened box; they differ by W0 = 0.02551). The PI's
reading is RIGHT at the UNWIDENED cell: 0 of 28 witnesses have both squares meeting the plain TR(0,0); 35/44
near-miss corners have no unwidened 2-crowd (16 EXACTLY tangent) — but the leaf must use the widened box for
the window, so 0 kills; a pad-free leaf would be s0-only. Lemma A159-1: one exact 2-crowd witness retires a corner
from every lane leaf forever (0.1 s) — screen before any cover budget; C8 guard added to check159. The k0 two-
crowd is a PAD phenomenon (A155's result from the other side). Eleven cells stay eleven. A148's LOG over-
attributed the corner-frame bug to A141 (it was A157's).

2026-09-08 PI on S02's f0: the basin should be grown along f0's whole SLIDING SLOT (several contact graphs; a box
hypothesis over poses does not care). A151 grew f1 (compute-limited, no real packing found) but never f0 (forced-
radius ordering). A160 dispatched: trace f0's slide, grow N along it with A151's ladder, consumer count, hand to
A136's YES leaf.

2026-09-08 PI: S02's second basin axis = the COMMON TILT of the grain f1/f2/f3 (A106's pinwheel tilt curve, min
3.886746 at 48.435 deg, rising both sides) -> cover it as a CHAIN of certified boxes along the curve (tilt steps
~2.5 deg, centres moving with the tilt), f0's slide inside each; union in N_boxes list format for A136. Claim to
test: f0 slide + common tilt cover the vast majority of the pinwheel+7 residues. Sent to A160.

2026-09-08 PI on k5_16 Y0842 (BL(1,0) UNDECIDED lane 1 M 1): "only one core fits in the bottom slot by chord
sum, and nothing outside the slot can reach BL(1,0)" -> new leaf CHORD-LIMITED LANE = A144's guard-line chord
budget on the wall band (<= 1 band square) + A141's lane cover restricted to OUTSIDE poses (LANE(outside) = 0) +
M -> singly met -> snap -> dead. A161 dispatched (Y0842 first, then all wall-adjacent undecided/near-miss slots;
A159's two-crowd screen first).

2026-09-08 A160 (f2453a24): S02 exact structure: f0 IS a rattler (slide length 0.298 along its body axis e2,
tilt fixed, three contact graphs = the PI's diagonal slot); at s0 nothing slides; f3 is the MOST load-bearing
square (not a rattler); BR(0,0) is a second rattler (slide 0.536); load path = {f1,f2,f3,BL(0,1),BR(0,1)}; f0 was
never in A116's N ("the strut"). Adding f0 as a body: net LOSS of consumers (96/42 -> 15/8) and caps. COMMON-TILT
CHAIN: 24/25 links (h 1.25 deg) over 60 deg, ~7 s/link — but a link's consumer ceiling is the support's tilt
SPREAD (f2/f3 tilts bind independently); independent axis SLICES certify (8/8). UNION A151-B + chain + slices:
114/50 consumers (vs 96/42). FIRST WITNESSES in the A116/A151/A160 line: compounding growth directions is refuted
by live-low partial packings (9 of 11 squares at side 3.8693 < s0) -> the basin is a UNION of boxes, not a
growable box. N_boxes160.json (53 sets, disjunction) handed to A136.

2026-09-08 GAP found via the PI's Y1110 (k5_16, family S02): every S02 basin certificate is in k5_11's FRAME;
the pinwheel's 7 slots contain both classes' pin sets, so k5_16's 68 and trump5's 12 S02 nodes never had a basin
or a consumer count. A163 dispatched: map A160's 53-box union into the k5_16 and trump5 frames, re-emit with
A133's generator, consumer counts, hand to A136. RULE: a basin certificate is per (minimum, class frame) — build
it in every class frame the shadow appears in.

2026-09-08 A161 CHORD-LIMITED LANE (27477e08): k5_16 Y0842 BL(1,0) KILLED exactly as the PI read (beta = 1 band
square by the wall chord row, LANE_out = 0 by an exact cover, M = 0). Population: 98 kills on 96 nodes, 90 NEW
(66 k5_16 + 24 trump5); 68 of them beta = 0 (H itself is the one square allowed in the wall lane). STRUCTURAL
GATE: the leaf needs TWO pins on the slot's wall (k5_11's wall slots have one -> 0 kills). Fixed A141's M budget
failure with box_misses_cell_exact (full SAT with the square's own normals). Lemma CL, checker 98/98, 0 new
axioms. Re-run targets: 126 UNDECIDED pairs (10 s budget), lift A141's lane_ub budget with the exact test.

2026-09-08 PI on c0_Y0169 (trump5, H at (1.24-1.38, 2.36-2.50) tilt 14-28): TL(0,0) reachable by one square at a
time (gap above H < 1; H not meeting the corner at the drawn pose). A141 NEAR-MISS (lane 1, M 1); A161 NO-LINE
(beta + M >= 2). The CONDITIONAL chord-limited lane: B_miss -> beta(1) + LANE_out = 0 -> singly met; B_meet -> H
meets TL, the band square must avoid H's corner in the cell (< 1 width left) -> LANE_band = 0 -> H sole meeter.
Sent to A161 (c0_Y0169 first, then all NO-LINE/UNDECIDED cells with M = 1).

2026-09-08 PI on l1_104: a WASTAGE argument (not lane): only one centre fits near the right wall below H, the
upper-right pocket is too short, so the right-wall strip is uncovered wherever that square goes. Leaf =
UNCOVERABLE AREA U (points no admissible square can contain, given pins' exact cores, K'(H), walls); |U| > s0^2 -
11 = 4.0318 => dead, LP-free (Lemma ID generalised from corners to the whole container). Never computed before.
A164 dispatched (l1_104 first, then the eleven + the 60 a57v4 pages).

2026-09-08 PI's CASCADE reading of l1_104: TR doubly met forces D (deep, up-right of H) + S (shallow, up-left) ->
two centres in the top strip -> top-wall chord row leaves one more, which must poke into TL(0,0) with a min depth
-> TL's second meeter forced along the left wall -> bottom-left band holds one -> six squares in narrow forced
boxes, large wastage, the other five cannot fit. = A150's mechanism (many conditioned boxes buy LP slack) with the
boxes FORCED by geometry instead of enumerated. A165 dispatched: explicit case tree with certified forcing steps,
multi-box LP at the leaves, canary l1_153.

2026-09-08 22:20 A156 day shift (9a18b867, PAUSED.md v4): 339 kills (269 frozen-certified + 70 geometry) for 28
CPU-h at only 2-3 workers (the 16-process ceiling was eaten by the geometry chores: sequence lanes if 5 workers
are wanted). LEVEL 2 LP kills 89% of decided in 122 s vs L1 72% / 236 s -> 2.4x kills per CPU-h -> queue level 2
FIRST. The geometry rate is a FRONTIER property (41.6% on children of alive L2/L3; 0.6% on children of fresh LP
survivors) -> never price the tree at a per-level geometry rate. T5'''' 0/342 on A57 (run it on A60 only).
Corpus hygiene: 139 ids stored twice, 26 pairs disagree -> take the strongest verdict (state156.py). Open work
423 after ledgers. 1 frozen FAIL-with-holes (Y0785) awaits v3.

2026-09-08 A149 RE-PRICE of A57 (08:10, reprice149.json): frontier counted id by id = 2,052 nodes owing work +
4,683 L1 "ok" children on sides 2-4 of the delta grid; CENTRAL ~1,800 CPU-h / ~15 wall-days (9.6-26), UP from
~800 because the old figure had no descent term (one ok child costs 3.76 nodes). Node cheaper (283 s). The single
unmeasured input was D_2 (share of L2 outcomes owing a split): A156 measured ~0.11 on 93 jobs -> A96's 0.113
stands. Free bookkeeping cuts: 563 of 1,995 queued jobs already dead (mkqueue ignored ancestry, ~90 CPU-h);
emit137's done-set read one shard file (573/849 night children were re-screens). Corrected new-id rates: L1
geometry 22.5%, LP kill 76.5%.

2026-09-08 PI: hybrid tree = keep the interior root; for the HARD nodes (H near one of Trump's three interior
squares) open a SUB-TREE rooted on the corner NEAREST to H, conditioning on H + that corner's two meeters (3-box
node, budget 8), pair cover clipped against K'(H). Prediction: a Trump-like H whose nearest corner is simple in
Trump dies at once (forcing it doubly met contradicts Trump); only the TL-adjacent H survives and its LP prices
the worst component. = A150's slack mechanism with the corner FORCED by H. A166 dispatched on the eleven k0 cells
(canary l1_153 must survive).

2026-09-08 PI signatures of Trump: chord signature (3,3,3,2) on the four walls; QUADRANT CENSUS: the non-simple
quadrant holds exactly the two TL-meeter centres and nothing else; Trump's third interior square is nearest the
three-simple corner (dies fastest under a forced pair). Both added to A166's per-cell table as diagnostics; worth
printing on every gallery page (chord signature + quadrant census vs Trump's).

2026-09-08 A163 (a175ee1d): S02 basin in k5_16's frame: 52/54 box sets certified (Y1110 in-N via A151-B and the
h=10 chain link; its f3 at 47.12 deg sits 0.065 deg below every 1.25-deg window — tilt binds again); 21 alive
consumers. trump5's frame: 42 certified, 9 refused by REAL witnesses (trump5 does not pin TL(0,0)); 3 alive
consumers. All 94 objects re-emitted + checked (A133 chain). Correction: A160's N_boxes160.json lacked A151-B.
Handed to A136 (24 more consumers). Box memory pressure killed three helpers (all resumable).

2026-09-08 A161 cont. (a491c1d0): CORRECTION — A161's "90 new" were 27 genuinely new (23 trump5 + 4 k5_16);
its population came from A141's t2 snapshot and 62 were already dead in A57's tree jsonl (A149/A156 since).
RULE: build populations from the STATUS collector (status_gallery.py), never from a campaign snapshot. +13 kills
from the 126 undecided (the GUARD LINE choice decides, not the budget: try the top 6 offsets). A141's leaf with
the exact SAT: 105 M-flips, 0 kills — the chord row does the killing. c0_Y0169: half certified (LANE_out = 0),
the band cover did not close -> not dead. Population pass over NO-LINE/M=1 not run (cap spent); cost order:
trump5 BR(0,1) 82 cells, k5_16 BL(1,0) 94, BR(1,0) 84, TL(1,0) 81.

2026-09-08 A164 uncoverable-area leaf (6d0ae26d): 0 kills on 71 nodes; l1_104's certified |U| = 0.129 (3.2% of
B0 = 4.0318), all in the wedge between K'(H) and the east wall; population median 18.6%, max 47% (A60 7-box
node); |U| scales with box count (0.13 at 1 box, 0.79 at 6, 1.70 at 7) -> first fire at 9-10 boxes where the LP
is already cheap. CORNER column is 0.000 on all 71 -> Lemma ID's charged region is EMPTY on the alive population;
64-100% of certified waste is in wall strips. The PI's "one centre near the right wall" is false unconditionally
(7 one-separated centres fit in x >= s0 - 1/2). A counted wastage row needs lane counts, not an area budget.
Lean shape: 4 obligations (W3 raster soundness = the Lipschitz fact A148's pages already lean on).

2026-09-08 PI caught A165 drawing unclipped pair boxes (TRa/TRb pose unions overlapping H's core). RULE (again,
now hard): in every multi-box node, clip every box against every other core BEFORE drawing / rows / covers / LP;
a box all of whose poses meet another core is empty (case dies); draw K' as the core, pose unions as thin
outlines only. Sent to A165 as a stop-and-fix.

2026-09-09 00:35 A165 (Opus cascade) KILLED at the PI's request (unclipped pair boxes; low faith in execution);
redone as A168 (FABLE): case tree with mutual clipping mandatory, every step a certified leaf, cover checked,
canary l1_153 first. RULE (PI): complex case-tree constructions go to Fable, not Opus.

2026-09-09 PI on the l1_104 cascade: A165 omitted the forced square along the RIGHT wall under H that meets BR
(only one centre fits in that band; it locks a lot of wastage along the east wall — probably critical to a full
kill). Sent to A168 as a required forced box (BR doubly met + right-wall band count), clipped against K'(H).

2026-09-09 PI's branching ORDER for the l1_104 cascade: (1) the right-wall square under H meeting BR (one centre
fits), (2) the TR pair (deep D up-right of H, shallow S along the top), (3) the top square the chord row leaves
room for (the 2->3 branch expected very narrow), then TL's second meeter and the bottom-left band; LP / |U| at
the leaves. Sent to A168.

2026-09-09 PI's LEMMA SIDEBAND (conjecture): a doubly-met corner box has at least one meeter with centre within
1 of an adjacent wall (x <= 1 or y <= 1 at BL) and the other outside that band. Numeric: no disjoint pair of
meeters with both centres beyond 1 (best gap -0.146 unit / -0.092 widened, anti-diagonal ~45-deg pairs). A169
(Fable) proving it + Sideband.lean; A168 uses it as a [C] step (band meeter priced by the wall chord row; outside
meeter bounded by the corner reach).

2026-09-09 A166 (bc8b5dd5): nearest-corner sub-tree — NO cell dead. Canary corrected the construction: a corner
meeter can BE H (Trump image g4's sq9 = H is a TR meeter) -> two branches: budget 8 (both meeters != H) and
budget 9 (one meeter is H, exists iff some pose of B_H meets int B_TR^w). The nearest corner is TR for all eleven
and 117/119 open cells (A38's fundamental triangle) -> ONE sub-tree. PI's predictions: direction right,
consequence wrong (the simple-corner cells are exactly those where H reaches the corner -> branch (b) survives);
"third square dies fastest" fails; quadrant census corrected: Trump is 3/3/3/2 with the sparse quadrant OPPOSITE
the three-simple corner, never the non-simple one. LP price ~560 CPU-h at L1 = no saving. CERTIFICATE BUG:
caselp.make_certificate reverts exact cores to stock via Hyp.from_json -> cert-FAIL/TOO-TIGHT/LOST-KILL outcomes
under exact-core LPs may be spurious; carrying exact cores: PASS 15/15, A150 4 -> 7 certified; 127 open k0
records are free-certification candidates -> A170 dispatched (audit all lanes + re-certify + wrapper fix).

2026-09-09 TWO-MEETER ATLAS (docs/residue_map/gen_two_meeter{,_v2}.py): a first meeter PRESSED into the corner
(touching both walls) admits NO second meeter of the unit corner box at any tilt (widened box: pad grazers only
near axis-aligned). Displacement thresholds d*(theta) for a second meeter to exist: slide along a wall 0.18 (0
deg), 0.34 (15), 0.38 (30), 0.56 (45), 0.64 (60), 0.72 (75); pull along the diagonal ~1.04-1.18 (none <= 1.2 at
0/90). => the deep meeter of a doubly-met corner is displaced from the pressed pose by >= d*(theta): the
"requirement" constant for k0 (A169 formalising; closed forms pending).

2026-09-09 A167 conditional chord-lane pass (1523a8f6): 416 cells / 258 alive nodes -> 15 KILLs (11 distinct
NEW: 7 trump5 + 4 k5_16, L1), 285 no-go by witness (49 EXACT rational two-crowd certificates retiring cells),
116 undecided. c0_Y0169 NEGATIVE: a band square DOES fit beside H on part of H's box (sampled free poses on every
offset) — the PI's second half false; A161's open cover had nothing to prove. Scheduling: a closing cover closes
in ~1 s; breadth over guard-line offsets (2 s slices + one retry) beats any long budget; the viability screen
(0.3 s/piece) makes depth-5 splits affordable. Checker fix: witness leaves citing the conditioned index verify
against the PIECE's box.

2026-09-09 PI's closed-form construction for the second meeter given a wall gap delta of the deep meeter: deepest
intrusion = a square flush with the side wall resting on the deep square, rotated by theta to fit the gap ->
intrusion in csc(theta), valid while sin(theta) <= delta; shallowest = cores whose corner just touches the top of
the gap. Expected: the allowable region is wildly small for flush deep squares and conservative delta. Sent to
A169 (derive, check vs atlas v2 thresholds, Lean shape in t).

2026-09-09 PI caught A168 (Fable) at S2: D's core escapes the container and overlaps H's core; B1 clips H; S
(the second TR meeter) not placed before moving to TL. Sent a stop-and-fix with a hard INVARIANT: at every node,
container clip + mutual clip to a fixed point, then the checker ASSERTS every K' inside the container and
pairwise disjoint before any figure/row/LP; both pair meeters placed before the next step. Second agent to
break the clipping rule — the invariant must be code, not instruction.

2026-09-09 PI REVISED cascade order (supersedes): (1) the TR corner square D first; (2) the second TR meeter S,
limited by D, presses H down-right (re-clip H vs K'(S), K'(D)) which kills much of the space for the right-wall
square B under H; (3) BR's second meeter, greatly limited; (4) the two left corners last, if needed. Sent to A168.

2026-09-09 cascade order (final, PI): (1) TR corner square D; (2) second TR meeter S (re-clip H vs D,S);
(3) B = the right-wall square under H, BR's deep meeter, as its own step; (4) BR's second meeter; (5) left
corners last if needed.

2026-09-09 ~01:30 PI to bed. Cascade logic (PI): a corner's first meeter's region = the poses ADMITTING a second
meeter (coexistence, mutually clipped), not the bare corner-meeting region: D's region cut by the existence of an
S; B1's region cut by the existence of a second BR meeter that (because of the small gap above B1 below H) cannot
come from above or above-left. Sent to A168. Morning digest owed: A168/A169/A170/A171/A136/A149 + status board +
gallery regeneration (chord signature + quadrant census on pages).

2026-09-09 ~02:30 A171 (multibox invariant library) closed: attempts/A171-multibox-invariant/code/multibox.py â€”
Node.normalise (container clip per tilt sub-bin + mutual K' clip to fixed point, refine bisection) and
assert_invariant (exact rational; K-CONTAINER, K-DISJOINT, POSE-CONTAINER(-STRICT), CLIP-FIXPOINT); chord_rows/lane
raise on un-normalised nodes. On A168's S2 node it found 5 violations; sound clip keeps H 0.44 / B1 0.94 / D 0.088
(91% of D's box was never possible). CAVEAT: strict_container=True drops centres feasible at only some tilts of a
sub-bin (recorded sliver) â€” not sound for a kill unless the sliver is covered; use strict_container=False or split.
Rule (PI): every multi-box node asserts the invariant before any row/cover/figure/LP. A169 relaunched (first run hit
the 64k output cap).

2026-09-09 ~03:00 A149 CLOSED: 180 certified kills (93 A57 ALIVE+FAIL drained at 38.8%, 87 A60 alive trump5 drained
at 40.7%), 0 error; Y0275 CERTIFIED DEAD (tau 5 -> 4); Y0130 alive under both exact square and K' cores (needs a
different leaf); c0_Y0215 unmoved. Rules learned: run exact-core chores FAIL-FIRST (62.5% kills at 0.22 CPU-h/kill
vs 16% ALIVE at 0.69); key the corpus by (tag,id) (third id-collision: 19 G1 nodes masked by dead L1 rows -> 14
kills); wall-cap must kill the process TREE (orphan verifier burned 2,914 CPU-s). A57 re-price ~1,800 CPU-h /
~15 wall-days (subtree term; 1,721 with A149's kills; joint re-derivation with A156's 339 kills owed). A166's cert
bug never on A57's path (137/137 certs exact; re-verify of 55 non-PASS recovered 0).

2026-09-09 ~03:30 A170 CLOSED (commit 2b7172c3): the caselp.make_certificate stock-core reversion touched ONLY
A150/A165/A166 (every other lane goes through emit135.make_cert, born exact). 59 recovered PASSes over 409 (2.35
CPU-h, 0 LPs): 25 repairs incl. 3 NEW â€” A165's l1_104_spread00/02/03 (leaf now 4 of 4) â€” and 34 free vacuity
upgrades (A59 ladder 8-14% cheaper, envelope unchanged). 118 already-exact FAILs unchanged; all 128 k0 open-pool
FAIL candidates give 0 PASS. Galleries unchanged (k0v4 11/0, a57v4 53/7). Wrapper: attempts/A170-certfix/code/
certwrap170.py make_certificate_exact (cores only enlarged, vertex test guarded). Lever noted: FAILs with 0 holes
"undecided at this depth" -> depth-64..72 frozen replay costs seconds.

2026-09-09 ~02:20 the machine REBOOTED: killed A168 (cascade, mid S2/S3), A169 (sideband lemma; sideband.md
249 lines + Sideband.lean 5 theorems on disk, unreported/uncommitted), A136 (24/54 closures), the affinity
watchdog and the 07:13 digest cron. 10:05 relaunched all three as resume briefs (A168 told to consume A171
multibox, A170 certwrap, A169 section 6 + cell form); watchdog restarted. A169 verdicts (from disk): SIDEBAND (a)
[T] sharp with constant c = box side (widened: x<1+w; "within 1" FALSE for the widened box); (b) FALSE as stated,
TRUE as "centres in different cells of the 2x2 grid at c" (l-inf distance >= 1/sqrt2, needs c < 1.2071);
REQUIREMENT Theorem B exact: slide threshold t = tan(theta/2), intrusion (delta-t) tan theta; pressed square admits
no unit-box partner, but a widened-box partner for theta < 12.8 deg; atlas d*(theta) values are pitch artefacts
(true 0/0.13/0.27/0.41/0.57/0.63). Lesson: after any reboot, relaunch from disk state; agents' partial files survive.

2026-09-09 ~10:40 PI finding on A171: clipping a box's pose space must GROW its K' on the far side (intersection
over fewer poses), and that growth is what propagates the cascade (D grows -> clips H harder -> clips B1). A171's
rebuild() formed K' from the UNION HULL of the surviving pieces, losing most of it: measured on the S2 node,
per-piece-intersection K' is 7.8% (H) / 4.6% (D) larger and one more pass cuts kept poses H 0.44->0.38, D 0.088
->0.073. A172 (Opus) dispatched to rebuild K' as the exact intersection of per-piece K' (vertices re-certified per
piece). A168's roles168 already intersects per piece. Rule: any clip/normalise loop must recompute cores from the
PIECES, never from a hull.

2026-09-09 ~12:00 A172 CLOSED (79999887): multibox K' = certified exact intersection of per-piece K' (vertices
re-certified per piece; kmode="union" restores old). S2 node fixed point: kept H 0.441->0.358, D 0.088->0.072,
B1 unchanged; 6x wall on that node. Drawing docs/residue_map/kprime_pieces_S2.svg (+gen). A169 CLOSED (69699879,
8c9c0c82): SIDEBAND (a) [T] sharp constant c; cell form Lemma A2 (l-inf >= 1/sqrt2, c < 1.207); Theorem B [T]
(four clauses NE/W/S/P, both directions); slide threshold = tan(theta/2) up to theta* = 56.76 deg then (W)-mode
crossing; widened-box pressed partner iff theta < 17.35 or > 72.65 deg (NOT 12.8); lonely fraction 54-74%
widened. Lean Sideband.lean 345 lines: sideband_a, distinct_cells, linf_sep proved; Theorem B stated [C] with
clause (P) proved. Rows for A168 in sideband.md section 6 (R1 cell prune, R2 band/outside split, R3 LONELY
NO-family). PI: B1 (right-wall deep meeter under H) -> partner only from the (left, floor) cell; A168 step 4.

2026-09-09 ~12:30 DEFECT found by the PI reading A174's S3 page (H outlines crossing S and B cores while kept H = 1.00):
roles168.normalise clips against the other roles AXIS CORES only, never their K' polygons -> no upstream propagation.
Node l1_104 root/D0/S1/B0: A168 kept H/D/S/B 1/1/1/0.60 ALIVE; multibox poly obstacles -> EmptyBox(H) = DEAD (pair leaf).
A174 stopped; A175 (Fable) relaunched: polygon-obstacle clip via multibox at every node, re-normalise every recorded
node, lonely clip at all four corners, geometry to fixed point before LP. Batch cross-check running from scratch
(clipcheck.py -> clipcheck.jsonl). RULE: multi-box clips must use K' polygons (mode=poly), and pages must print
kept fractions so a non-propagating clip is visible.
