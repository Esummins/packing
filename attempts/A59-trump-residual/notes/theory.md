# A59 — the trump5 stratum as an 18-d anchored grain problem (Fable, 2026-09-01)

Everything at s0 = 969271/250000 = 3.877084 unless stated; window I = (382/100, s0].
Inherits: A53 lemmas.md (L1–L6, Young-form definition, census L3, cap L5), A54 notes (S0 kill
semantics, k>=6 tier closed 33/33), A35 notes/theory.md (certificate forms (E)/(V)/(A)/(W')/(C)/(F),
T1-b' sign collapse), A36 composed theorem (box radius 3.7e-3, stratum-blind), drain_lemma v3 (D1).
Branch labels: [T] proved, [S] proved selection/soundness statement, [C] conjecture/named gap.

## 0. Setting and notation

Pins. trump5 = the k = 5 skeleton class ((2,1),(1),(1),()) with slot squares, at container side s:

    P1 = (1/2, 1/2), P2 = (3/2, 1/2), P3 = (1/2, 3/2)          (BL staircase — fixed)
    P4 = (s - 1/2, 1/2)                                          (BR corner — moves with s)
    P5 = (s - 1/2, s - 1/2)                                      (TR corner — moves with s)

Residual polygon R(s) = [0,s]^2 minus the five open pinned squares; area s^2 - 5 (= 10.0318 at s0).
Its boundary decomposes into 16 labelled anchor elements — 12 maximal segments + 4 exposed pin
corners — in boundary-cycle order:

    A0  L-wall   x = 0,      y in [2, s]         A1  B-wall   y = 0,     x in [2, s-1]
    A2  R-wall   x = s,      y in [1, s-1]       A3  T-wall   y = s,     x in [0, s-1]
    A4  stair-top-hi   y = 2, x in [0, 1]        A5  stair-right-hi  x = 1, y in [1, 2]
    A6  stair-top-lo   y = 1, x in [1, 2]        A7  stair-right-lo  x = 2, y in [0, 1]
    A8  BR-left  x = s-1,  y in [0, 1]           A9  BR-top   y = 1,    x in [s-1, s]
    A10 TR-left  x = s-1,  y in [s-1, s]         A11 TR-bottom y = s-1, x in [s-1, s]
    C1 = (1, 2)   C2 = (2, 1)   C3 = (s-1, 1)   C4 = (s-1, s-1)     (exposed pin corners)

    cycle: A0 A3 A10 C4 A11 A2 A9 C3 A8 A1 A7 C2 A6 A5 C1 A4  (back to A0).

The pin set has NO symmetry: the x<->y reflection fixes the BL staircase (lambda = (2,1) is
self-conjugate) but maps BR to TL (empty) — stabiliser of the pin set in D4 is trivial. All
residual objects are therefore counted up to S6 (relabelling of the free squares) only.

The 19-variable NLP. Variables zeta = (c_i, theta_i)_{i=1..6} in R^18 and s. Constraint rows:
  (w) wall rows — each free square inside [0,s]^2 (right/top rows involve s);
  (p) pin rows — SAT separation of each free square from each pinned square (P4, P5 rows
      involve s through the pin position; selection menus per D3' exactly as in A35);
  (q) pair rows — SAT separation between free squares.
Objective: min s. Feasible set F = { (zeta, s) : the 6 free squares are admissible in R(s),
pairwise interior-disjoint }. Each point of F IS an 11-square packing in [0,s]^2 (the pins are
part of the constraint set), with bounding box exactly [0,s]^2 — see T1(b).

## T1 [T] — the stratum is the NLP feasible set; normalization is free

Let Sigma(s') = { packings P of 11 unit squares, sigma(P) = s' <= s0, Simp(P) = trump5(s') },
Sigma = union over s' in I.

(a) Every P in Sigma corresponds to a point of F with s = sigma(P), and conversely every point of
F whose skeleton is exactly trump5 lies in Sigma. Proof: the pins at slots(s) have the Young
property, so trump5 subseteq Simp always holds on F; the skeleton of a point of F can only EXCEED
trump5 (see T2). Conversely a packing with Simp = trump5 has its five simple squares exactly at
the five slots by definition L1/L2. QED

(b) Normalization is rigid: the pinned skeleton touches all four container walls (L and B by the
staircase, B and R by P4, R and T by P5), so the bounding box of any point of F is exactly
[0,s]^2 — the translation/normalization freedom of drain_lemma v3 is spent by the pins. L6(iv)'s
caveat (box sides not necessarily touched by axis-aligned squares) is DISCHARGED inside this
stratum: all four sides are touched by pinned squares. QED

## T2 [T] — upward emptiness: the drain cannot escape up (the certified composition)

**Lemma T2.1 (completion slots — SIX, corrected by the census worker 2026-09-01).** The Young
4-tuples strictly containing trump5 with one added cell and pairwise interior-disjoint slot
squares are exactly SIX one-cell completions: BL + (1,1) -> slot (3/2, 3/2) [class k6_19];
BL + (0,2) -> (1/2, 5/2) [k6_07]; BR + (0,1) -> (s - 1/2, 3/2) [k6_21]; TR + (1,0) ->
(s - 3/2, s - 1/2) [k6_24]; TR + (0,1) -> (s - 1/2, s - 3/2) [k6_22]; TL + (0,0) ->
(1/2, s - 1/2) [k6_23, killed by A54 W1]. The two remaining addable cells, BL + (2,0) ->
(5/2, 1/2) and BR + (1,0) -> (s - 3/2, 1/2), give slot squares overlapping the BR resp. BL pins
for EVERY s in the window (x-gap s - 3 < 1, y-gap 0 — exactly A53 L2(iii), i + j = 2), are not
Young 4-tuples of the census, and are vacuously unrealizable — no kill needed. Class matching:
results/completions.json (exact Fractions, D4 ops recorded). Every Young 4-tuple S with trump5
as a strict subset contains at least one FEASIBLE T_j: take any maximal chain of Young tuples
from trump5 to S; its first step adds an addable cell, and if that step were one of the two
overlapping cells, S itself would contain overlapping slot squares — contradiction. So the
first step is one of the six. QED

**Lemma T2.2 (the certified kill transfers to the completions).** Each T_j is a 6-cell Young
4-tuple, hence lies in one of the 33 D4 classes of A53's k = 6 layer (L3 exhaustiveness), all of
which carry PASS exact certificates (A53 32/33 + A54 W1). By A53 L5 (kill semantics price
CONTAINMENT only), the certificate for the class of T_j proves: **no packing of 11 unit squares
in [0, s0]^2 contains axis-aligned unit squares at all six pins of T_j.** D4 transfer of a kill
is the usual action on certificates. QED

**Theorem T2.3 (upward emptiness at s0) [T].** No point of F with s = s0 has a free square
axis-aligned and centred exactly at a completion slot of any T_j. Consequently every point of F
at s = s0 has skeleton EXACTLY trump5, and the closure of Sigma(s0) inside the space of
11-packings at side s0 is Sigma(s0) itself together with points already in Sigma(s0) — the
stratum's upward boundary is empty, not merely unvisited. Proof: such a point of F would be an
11-packing in [0,s0]^2 containing all six pins of T_j, contradicting T2.2. QED

**Corollary T2.4 (window form) [C -> A56].** The same statement for every s in I requires the
kill certificates of the SIX classes {k6_07, k6_19, k6_21, k6_22, k6_23, k6_24} to be valid at
side s, i.e. exactly G-A53-1 / the A56 s-parametric transfer now in flight — that six-class list
(results/completions.json) is the priority order to hand A56. Everything below is stated
unconditionally at s = s0 and conditionally-on-A56 on the window. The upward trap uses ONLY
these six; but note the zone-tree children of T5' inherit their own, separate s-parametric
obligation (G-A59-7).

## T3 [T] — the stratum-restricted drain

**Theorem (restricted drain).** Assume T2 on the window (unconditional statement at the s0
endpoint below). Let m = inf { s : (zeta, s) in F, s in I }. Then:
 (i)  [attainment] The inf is attained: F cap {s <= s0} is compact (closed and bounded: contacts
      and containment are closed conditions; theta compactified mod pi/2), and it is nonempty —
      Trump's configuration zhat_res = (sq4, sq6..sq10 of A03, s = s_T) lies in it. So m <= s_T.
 (ii) [no upward escape] Every minimizer (zeta*, s* = m) has skeleton exactly trump5 (T2.3/T2.4);
      the minimizer stays interior to the stratum — the drain terminates INSIDE trump5.
 (iii) [automatic slide-stuckness] No point of F at s <= s0 admits a grid-completing slide at all
      (the slide's endpoint would violate T2.3), so — strictly stronger than A53 L6, which selects
      SOME slide-stuck minimizer — EVERY point of the stratum is slide-stuck. The L6 selection
      argument is not needed inside trump5.
 (iv) [FJ necessity] Every minimizer is a Fritz-John point of the 19-variable NLP: there exist
      lambda_0 >= 0 and multipliers on its ACTIVE rows (its actual contacts: wall, pin, pair, per
      selection menu), not all zero, with lambda_0 * e_s = sum lambda_r grad g_r, lambda_r >= 0.
      No constraint qualification is assumed (FJ, not KKT); the lambda_0 = 0 branch (a nonnegative
      self-stress on the active rows) is part of the obligation, exactly as in A35 (F).
 (v)  [floor] m > 382/100: a minimizer at s <= 3.82 would be an 11-packing in [0, 3.82]^2,
      contradicting the certified measure bound (A07/A08/Lean). So all critical objects live in
      the open window (3.82, s0].
Proof: (i) compactness + T1; (ii) T2; (iii) as stated; (iv) standard FJ for min s over finitely
many smooth-selection inequality rows, per selection with D3' menu completeness at ties (A35
convention, verbatim — the menus now include pin-corner ties, see G-A59-4); (v) as stated. QED

**What must be excluded, exactly.** "trump5 contains only Trump" = the statement m = s_T with
the minimum attained only at zhat_res. By T3 it suffices to exclude, for every possible active
contact structure ("grain"), every FJ point of the 19-var NLP with s in (3.82, s_T) — and at
s = s_T every FJ point other than zhat_res itself. Trump's own grain at zhat_res is a genuine FJ
point (it must survive; it is the canary), discharged not by exclusion but by the A36 basin
certificate (T5) plus cell coverage (the priced residue).

## T4 [T/S] — grains, the census contract, and why anchoring changes the regime

**Definition (grain).** The Level-0 grain of a point of F: the support structure
(mu_1..mu_6; E) where mu_i subseteq {A0..A11, C1..C4} is the set of anchor elements square i
touches (closed contact; a contact exactly at a segment endpoint that is a pin corner is recorded
on the corner element C_j, and on C_j alone), and E is the touching graph on the six free squares.
Counted up to S6. (Level-1 decorations — flush vs corner type, selection branch — refine a grain;
the census counts Level 0 and reports the measured decoration fan-out separately.)

**Census contract [S].** The census (leg b) must emit a finite list G of grains together with,
for every filter used, either (a) a proof that the filter is a NECESSARY condition satisfied by
every point of F with s in I (hard filter — may prune), or (b) the label SOFT (reported, never
pruned). Soundness obligations specific to R(s), re-proved rather than inherited from A31:
 - centre boxes per anchor element: a unit square touching a segment/corner element has its
   centre at distance [1/2, sqrt2/2] from the touched point, on the free side; boxes take the
   union over the element and are widened over s in I (the s-moving elements A2, A3, A8..A11,
   C3, C4 get interval positions). All boxes intersected with the admissible core
   { c : c in [1/2, s0 - 1/2]^2, |c - p|_2 >= 1 for every pin centre p (BL pins fixed; BR/TR
   evaluated at the s-extremes) } — |c - p|_2 >= 1 is exact for two interior-disjoint unit
   squares (incircle argument, tight at flush).
 - pairwise tables: BAD (two mask boxes cannot hold two interior-disjoint unit squares) and
   touching windows (edge in E forces centre distance in [1, sqrt2]) — A31 L5(a) verbatim on the
   new boxes; hop bound |c_i - c_j| <= sqrt2 * hops stays valid (a chain of touching squares is a
   Euclidean statement, pins do not enter).
 - per-element capacity caps: two squares touching the same segment have centres >= 1 apart
   with normal distances in [1/2, sqrt2/2] (normal spread <= sqrt2/2 - 1/2 = 0.2071), hence
   tangential separation >= sqrt(1 - 0.2071^2) = 0.97832 — recompute A31's bound per segment with its
   actual length (the exposed B-wall A1 has length s - 3 = 0.877084: cap 2; the corner elements:
   centres in a radius-sqrt2/2 disk pairwise >= 1 apart: cap 3). Caps are hard only where the
   supporting lemma is written out in the census report.
 - planarity: the contact structure drawn with the 16 anchor elements in their boundary-cycle
   order (section 0) plus the cycle edges must be planar — the A31 L4 wall-cycle argument with
   the polygon's cycle replacing the wall 4-cycle (same proof: contacts are realized by disjoint
   arcs in the closed region).
 - NO occupancy/loadedness/Maxwell filter is hard (A31: Maxwell counts are met by zero survivors;
   A43: existential filters are vacuous — do not repeat).
**Canary (hard gate):** Trump's residual grain,
   mu(sq4) = {A0}, mu(sq6) = {A3}, mu(sq7) = {C1}, mu(sq8) = {C2, C3}, mu(sq9) = {C4},
   mu(sq10) = {A2};  E = {46, 47, 69, 78, 79, 8-10, 9-10}   (A03 exact contact list),
must pass every hard filter. Any census run in which it does not is discarded.

**Why this is the anchored regime [S].** Of the row types, (w) and (p)-with-fixed-pins have
gradients with CONSTANT sign pattern in the free coordinates over any region where the selection
is constant (an anchor is a wall: it never moves, so its row's gradient never rotates); only the
15 pair rows (q) rotate with the configuration. A35's semantic cliff (R* ~ gap/L) was set by
moving-cluster diameter L ~ 4.24; inside R(s) every free square is within 1.44 of the boundary
and the moving cluster is at most the six residual squares (L <= 2.9), with 8 of Trump's 15
residual contacts anchored. This is precisely the regime where A35's machinery certified in
minutes (anchored strata) rather than dissolving at the cliff. The pilot (leg c) measures whether
that transfers from Trump's neighbourhood to foreign grains.

**The A43 mismatch check [S].** A43's law — certificates price placements, enumerable objects
quotient placement away — is answered here BY DESIGN: the per-grain certificate unit (T4/T5's FJ
exclusion over the grain's cell) is attached to exactly the enumerated object (the grain), and
the pins have already spent the placement quotient (no D4, no translation, slots exact). The law
can still reappear as CELL SUBDIVISION (one grain needing many boxes); the pilot's
cells-per-grain measurement is the honest test, and the composed cost in leg (d) must carry it
as a multiplier, not a footnote.

## T5 [T] — per-grain exclusion semantics and the composition theorem

**Per-grain obligation.** For a grain g with cell Cell(g) = { (zeta, s) in F : the contact
structure of zeta refines g }, an EXCLUSION certificate is any of (soundness inherited from the
cited forms):
 (X1) emptiness: interval/exact proof that Cell(g) = emptyset (metric refutation — refined L5(a)
      boxes, theta subdivision; A39-style cheap certificates);
 (X2) sign collapse: T1-b' coordinate sign cascade over a region containing Cell(g), with the
      gained-contact menu of the region included — kills BOTH FJ branches (A35 T1-b', proved);
 (X3) cone/Farkas: a region Farkas direction y with grad g_r . y > 0 for all rows active-capable
      on the region (A35 (W')/T1-a + the lambda_0 = 0 lemma) — no FJ point, either branch;
 (X4) value: a (V)-form certificate sigma >= s0 on the region (then the grain concerns the drain
      only at s >= s0 — out of the window; equality-at-s0 points are handed to the s0 endpoint
      analysis);
 (X5) isolation + value: Krawczyk isolation of a rigid solved point with certified s* > s0 (or a
      certified enclosure of s* outside (3.82, s0)); if a genuine FJ point with s* in the window
      appears and survives verification, that is not a certificate failure but a DISCOVERY (a new
      critical point of the stratum) and must be raised to the PI immediately — the composed
      program is then false as targeted.
**Trump's grain.** By A36 (stratum-blind over ALL of box(zhat, 3.7e-3) in the 34-var space):
every feasible configuration within 3.7e-3 of zhat has sigma >= s_T with equality iff zhat. The
slice { pins at slots(s) } of that box contains the neighbourhood { |zeta - zhat_res|_inf <=
3.7e-3, |s - s_T| <= 3.7e-3 } of zhat_res in F (a slice of a certified box theorem is certified:
the statement is universally quantified over the box). So Trump's grain is discharged on the A36
box; Cell(trump grain) minus that box carries the same X2-X4 obligations as any foreign grain —
this is the priced residue G-A59-3, NOT assumed small.

**Composition Theorem [T] (the finite program).** Suppose:
 (1) [census] G is emitted under the T4 contract (hard filters proved necessary);
 (2) [exclusion] every grain in G except Trump's carries an X1-X5 certificate covering its cell
     for s in (3.82, s0];
 (3) [Trump] Trump's grain carries the A36-box discharge plus X-certificates on the rest of its
     cell, concluding: sigma >= s_T on Cell, equality only at zhat_res;
 (4) [upward] T2.3 (s0) resp. T2.4 (window, A56).
Then min sigma over the closure of Sigma is s_T, attained only at Trump's packing — **the trump5
stratum contains only Trump**. Proof: T3 gives a minimizer which is an FJ point of the NLP with
s in (3.82, s0]; its grain is in G by (1); (2) forbids every grain but Trump's; (3) pins the
value and the uniqueness. QED

Remark (what this composes INTO): together with A53/A54/A55's kill library (k >= 6 and all
non-Trump k = 5 except k5_11/k5_16), A57 (k5_11, k5_16, in flight) and A58 + the low-k program
(k <= 4), statement (*) is the Trump-stratum leg of s(11) = s_T. A59 does not claim the others.

## T4a [M] — CENSUS VERDICT (2026-09-01): the Level-0 grain is the wrong certificate unit

The leg-(b) census (results/census_report.md) is honest and decisive: ~4.4364e10 Level-0 grains
(MC +-1%), rigorously bracketed [2 290 359, 822 380 205 647] (exact lower-bound family; exact
Burnside upper bound), 91 admissible masks, canary PASS, corner-cap-3 proved, runtime 193 s.
The explosion is NOT rattler-driven (84.8% of grains have all six squares anchored, exact) and
Trump's grain has no Level-0 signature (~2e9 grains share its coarse profile). Diagnosis =
the F4 lesson at Level 0: every census filter is a CONTAINMENT filter, and A43's
enumeration-certificate mismatch reappears exactly as T4's closing remark warned. T5's per-grain
program is therefore NOT the finite program — at 1 s/grain it is 1.4e3 years. The census is
kept as (i) the Level-0 map (mask list, usage stats, planarity dominance), (ii) the banked
lemmas: corner capacity 3 (proved via the pin), the 6-completion correction (T2.1), the
interleave/planarity pairwise shadow, the strict-gap canary data. T5 remains TRUE (each X-form
is sound) — it is the UNIT that is wrong; T5' below re-partitions the same obligation into
zone-tree cells, of which A57 measures the per-cell cost at seconds, not the grain count.

## T5' [T/S] — the RESIDUAL ZONE-TREE: the finite program, re-based (the pivot)

The certificate unit is now the A24/A54/A57 zone-tree cell INSIDE the 18-d residual, not the
grain. Machinery: A57's tree57/pinguard/deepen/alivewitness stack on the trump5 node,
unmodified semantics (A54 S0: the sole kill arbiter is an exact certificate through
verify_case.py; A57 T5 pinguard classes; A57 T2 t-uniform covers; A57 T11 depth-refinement
keeps the budget).

**T5'.1 [T] Branch soundness (inherited).** For a zone Z and a closed cover {B_i} of
Z x [0, 90], (NO: no square centred in Z) OR (YES_i: some square with (centre, theta) in B_i)
is a complete disjunction (A57 T1); refining any B_i by a closed sub-cover preserves budget
(A57 T11); a YES child's budget decrement is sound iff the witness is distinct from the pins
and from previously conditioned cores (A57 T5 pinguard + the distinct-witness check for
multi-core nodes: two cores admit a shared witness only if one (c, theta) lies in both boxes —
check box disjointness in (c, theta), with the theta = 0/90 identification). Sequential
conditioning of up to six cores is sound by induction on the same argument.

**T5'.2 [T] What the tree must deliver (the trump5 twist).** Unlike A57's strata, trump5 is
LP-unkillable — tau*(trump5) >= 6 = budget with a STRICT exact gap of 1.0574e-7 (A57 T8 /
Lemma A57-3 disjoint-family bound; artefact attempts/A57-shadow-trees/results/alive/
trump5_strict.json: Trump's free six scaled about the container centre by lambda = s0/s_T, exact
rational gap — this also repairs A53 V6's exact-touch soundness gap and is the rigorous form of
the nonemptiness used in T3(i)). Trump lives there. So the tree's target is not emptiness but
CONFINEMENT, and along the Trump-containing chain the SAME checker (alivewitness --placements,
with the scaled six restricted to the child's hypotheses) certifies ALIVE verdicts: a
Trump-containing child with r cores and budget m = 6 - r is rigorously LP-unkillable whenever
the scaled witnesses realize its cores and the remaining m witnesses are strictly disjoint from
all cores — those children are the (D)-chain, to be refined and discharged, never killed:

  THEOREM (zone-tree composition). Suppose a finite tree of the above branches, rooted at the
  trump5 node, is built such that every leaf is either
   (K) exact-certified empty (kill certificate, s-parametric per G-A59-7), or
   (C) contradictory/vacuous (pinguard logic or box-cover audit — no certificate needed), or
   (D) a DISCHARGE leaf: six cores conditioned, each core box B_j within the A36 basin slice —
       i.e. B_j contained in the sup-norm box of radius h = 3.7e-3 around Trump's j-th free
       square in (cx, cy, theta)-coordinates (theta in A22's coordinate units), with distinct
       witnesses forced (T5'.1) — AND the leaf's s-range within [s_T - h, s0].
  Then every 11-packing with skeleton trump5 and sigma in (3.82, s0] lies in a (D) leaf's cell;
  by the A36 composed theorem (restricted to the slice as in T5) sigma >= s_T with equality iff
  it IS Trump's packing. With T2 (upward) and T3 (drain) this proves: the trump5 stratum
  contains only Trump. QED (each leaf type: K empties, C empties, D discharges; the disjunction
  tree covers the node by construction.)

  The s-range clause: a packing in a (D) leaf has its 6 free squares within h of Trump's and its
  pins at slots(sigma); for the A36 box membership it needs |sigma - s_T| <= h as well. The
  upper side is free (sigma <= s0 = s_T + 4.1e-7); the LOWER side (sigma >= s_T - h) must be
  delivered by the tree: the (K) leaves must kill the s-slab (3.82, s_T - h) entirely — i.e.
  the near-Trump cells at sigma below s_T - h are kill obligations, not discharge candidates.
  [S] Plausible-but-not-free: a packing with all six free squares h-close to Trump's placements
  but bounding box 3.7e-3 SMALLER would be an eps-improved Trump — precisely what A36 refutes
  NEAR z-hat and what the kill certificates must refute at the slab boundary. The pilot measures
  whether the guard LP sees this slab (G-A59-8).

**T5'.3 [S] Depth arithmetic — SUPERSEDED IN PART by the pilot (2026-09-01).** The pilot
(results/pilot_report.md sections 1-4b) REFUTED the sibling-kill arithmetic below as written:
every Trump-adjacent sibling YES child at every depth and every half-width is ALIVE-CERTIFIED
unkillable by Lemma A57-3 (its budget-many surviving Trump witnesses are a strictly disjoint
family), so "~35 sibling kills per square" describes kills that cannot exist. The tree closes
anyway, by the RESIDUE-LADDER model: refine only the unkillable boxes (T11 bisection, alive-gate
re-run per sub-box); the unkillable residue stays bounded (21-52 boxes over 24 measured levels,
mean 34) and contracts onto Trump at gap ~ 4.6 x box radius until every residue box lies inside
the A36 basin slice (measured at level 24 for the first square). r_kill = 4.55 x hw exactly
(sup-norm, stable over 1.5 decades), so the annulus of G-A59-9 closes at hw <= h/4.55 = 8.13e-4
= 2.19 extra bisection levels — genuine (D) leaves exist, no A40/(W') work needed. Nested
branching collapses: unkillable counts 41 -> 18 -> 7 -> 0 -> 0 as squares are conditioned at
basin radius; free logic kills reach 93-100% from j = 1 on. The paragraph below is kept for the
record of what was conjectured before measurement; use the pilot's model.
CONJECTURE (tau* = k, new): on trump5 nodes, tau*(N) = k(N) = the number of surviving
strictly-separated Trump witnesses (17/18 converged solves agree; documented exception
conf_j4_hw0.02_a0.075 where tau = 2 > k = 1 — a disjoint pair NOT a sub-family of Trump's six).
Only the sound direction tau* >= k (Lemma A57-3) is used by the program (the never-attempt
gate); proving the converse on this stratum would make the tree a combinatorial computation
with the LP reduced to certificate construction.

[historical, refuted as written] Depth arithmetic (the c^18 ledger — to be MEASURED, not assumed). A (D) leaf needs
six cores of half-width <= h = 3.7e-3 in 3 coordinates each. A single square's confinement chain
from a zone-cover box (A57 interior resolution: half-widths ~0.075 in c, ~0.06 in t) to h is
~log2(0.075/0.0037) ~ 4-5 bisection levels x (2^3 - 1) sibling kills = ~35 sibling kills per
square, ~210 for six, PLUS the zone-level siblings (A57: ~1150 cover boxes per zone, of which
~25% contradictory-free and the rest die at 1-290 s each). The UNKNOWN that decides GO/NO-GO is
not the count but the KILL MARGIN PROFILE: sibling boxes at placement-distance d from zhat_res
lie inside the measured tight variety for d <~ 0.02 (A53/A54 tight maps: eta <= 0.02 within
0.007-0.026 of Trump's free squares), so their guard-LP margins shrink as d -> h. Define
r_kill = the smallest d at which sibling kills still exact-certify. GO requires r_kill <= h
(no annulus gap between the killable region and the basin); if r_kill > h the annulus
[h, r_kill] falls to neither tool and needs A40-style basin growth or (W')-wedge work — priced
separately or NO-GO. The pilot's single most important measurement is r_kill and the cost curve
c(d) of kills approaching it, at BOTH the first conditioning level (5 pins + 1 core) and the
last (5 pins + 5 cores + sibling for the sixth) — the last level is the Trump-adjacent regime
where A54's k5_11 experience (0.35% short) warns the margins die.

**T5'.4 [S] The tilt-menu lever (A50/A48 composition, optional levels).** Inside the residual
the 5-strip (the tilted quintet's flush ruler) is the maximal flush structure; the cascade
tilt-quantization (A48 C1-C6', A47 T1 span quantization) pins the admissible tilt of any
flush-coupled chain to a finite algebraic menu. Used as tree LEVELS (branch on menu membership
vs NoFam windows), this conditions theta at zero LP cost where it applies. Kept optional: menu
soundness inside R(s) must be re-derived (the cascade lemmas assume container-wall termination;
pin edges are walls for this purpose only where the A50 wall-termination analysis says so — in
flight). Not load-bearing for the composition theorem; a cost reducer.

## Gap list (A59 theory-side, honest)

G-A59-1  T2.4 window form = A56 dependency (8 completion classes; unconditional at s0).
G-A59-2  census filter soundness on R(s): each hard filter needs its lemma re-proved for the
         residual polygon (T4 contract); A31 proofs are for the empty container and do not
         transfer verbatim (different wall set, reflex corners).
G-A59-3  Trump's grain beyond the A36 box: the basin certificate covers radius 3.7e-3; the rest
         of the cell (the tight-variety mid-tilt core measured by A53/A54 tight maps: 5.1% of
         placement space, 675 clusters) is the single largest exclusion obligation. The A54
         tight-map profile says the ghost mass lives exactly here — expect the hardest work, and
         price it separately in leg (d).
G-A59-4  selection menus at pin corners: a free edge in contact with an exposed pin corner C_j
         has dominance ties when the contact point crosses the corner (the two adjacent segments
         swap the separating axis). D3' menu completeness must include these; the A36 L1
         branch-disjunction lemma is the template (over-estimate principle applies verbatim to a
         FIXED corner — easier than A35's moving endpoints, since the corner never moves).
G-A59-5  rattler coordinates: grains with a square of empty mask and no pair contact leave 3 free
         coordinates; FJ is unaffected (its multipliers vanish on absent rows) but X2/X3 regions
         must cover the rattler's whole admissible box — cheap (no active rows to rotate), but it
         must be stated in each certificate's region description.
G-A59-6  the k-th free square exactly at a NON-completing slot (e.g. axis-aligned at (1/2, 5/2)
         requires (1/2,3/2)+(1/2,5/2) predecessors — those ARE complete; the actual
         non-completing slots at trump5 are the R-family ones whose predecessors are absent,
         e.g. (s-3/2, 3/2)): such a point is interior to the stratum (skeleton unchanged, A53
         L1(i)), needs no special handling — recorded so nobody "fixes" it into a bug later.
G-A59-7  s-parametric form of the zone-tree kill certificates (T5'): every (K) leaf is certified
         at s0 only until run through A56's parametric recipe — the composed cost model must
         carry A56's measured overhead multiplier, and the count of certificates needing it is
         the tree's (K)-leaf count, not six. NOW SUBSUMES G-A59-8: the pilot's M4 diagnostic
         shows the low-s slab is structurally invisible at any fixed-s node (a packing at
         sigma < s_T - h has its BR/TR pins displaced by up to 5.7e-2, outside the node's
         hypothesis class) — the slab is exactly the s-parametric obligation, nothing separate.
G-A59-8  [MERGED into G-A59-7 per pilot M4 — kept as a pointer only.]
G-A59-9  discharge-radius ratio r_kill / h — MEASURED (pilot §2): r_kill = 4.55 x hw exactly;
         at hw = h the annulus exists (width 1.31e-2) and CLOSES by over-refinement at
         hw <= 8.13e-4 (+2.19 bisection levels per coordinate). Not the binding constraint;
         genuine (D) leaves exist. CLOSED as a question, kept as the number.
G-A59-10 nested six-square branching — measured favourable at level 1 (41 -> 18 -> 7 -> 0
         unkillable as squares are conditioned at basin radius; 93-100% free kills from j = 1).
         Residual obligation: run the full refinement ladders at conditioning depths 2 and 3
         (the pilot ran the ladder only at depth 0) to turn the composed 1e4-1e5-certificate
         estimate into a measurement.
G-A59-11 engine changes required before any A59 tree launch (both pure wins, pilot-validated):
         (i) fold alive59.k(N) into tree57.py as a pre-LP gate — never launch an LP on a node
         with k >= budget (Lemma A57-3 makes it provably uncertifiable; the pilot burnt 64% of
         its LP time re-discovering 1-ms facts); (ii) vac59 zero-atom vacuity certificates as
         the budget-1 arbiter (no LP, no EPS_CORE/EPS_ZONE floor — the LP-gated route cannot
         even see the discharge regime, its 2e-3 epsilons are the same scale as h).
G-A59-12 the tau* = k conjecture (T5'.3): prove or refute tau* <= k on trump5 nodes; only
         tau* >= k (proved, A57-3) is load-bearing in the program.
