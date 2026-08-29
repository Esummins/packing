# A43 — full-library re-census + the spine census: final report (Fable lead, 2026-08-28)

## 1. Question and verdict

I-L16 asked two measurement questions. H1: does the 2026 theorem library (occupancy at s-hat,
per-wall <= 3, flush-mandatory, A21 tilt windows, wastage motifs, tight-variety, pair sums),
applied soundly as bulk filters, collapse the A31 structure count? H2: is the L6 wall-to-wall
spine a small enough anchor alphabet to hang the far field on?

**VERDICT: NO on both, for the SAME structural reason at two different levels, and the reason is
the finding.** H1: the whole library buys a factor of ~2 on the k = 11 graph count (2.3e29-1.5e30
vs A31's 4.2e29-3.3e30); only per-wall <= 3 hard-prunes at all. H2: the spine census answers
"large", not "small" — the stack cuts 72% at k = 3 and < 0.4% at every k >= 4 (~2.1e6 spine
types at k = 11), and the per-spine completion estimate is 1e18+ desktop-days BEFORE the unpriced
transverse dimension. Both halves are canary-clean and verified (H1: exact regression to every
A31 number + 20/20 Trump checks; H2: 30/30 Trump chains + 163/163 A37 valley chains + an
independent no-witness audit of all 48 kills).

**THE LAW (the composed thesis result).** Name: the ENUMERATION-CERTIFICATE MISMATCH. Our
certificate families price PLACEMENTS — a guard field prices mu(Q(t,cx,cy)), the wastage atlas
prices (centre-box x tilt-box) cells, occupancy prices zones. Every object cheap enough to
enumerate — contact graph, decoration, spine type — is cheap precisely BECAUSE it quotients
placement away. So bulk enumeration and bulk certification cannot meet: each filter failed for
exactly the coordinate it forgets. N2/N3 are existential over the 11 squares (vacuous below the
k = 11 join — the witness may be a rattler); N5/N6 are positional and a graph carries no position
(certified m_low = 0.000000 on every wall-mask window, while the SAME field pointwise exempts
7.13% of placement cells — the power exists, the window is ~1e6x too coarse); a spine type
carries position in ONE axis only, so the placement filters (C3 field, C4 wastage) are certified
zero on every survivor — the wastage floor is literally 0 because y is free and deep-interior
dead area is genuinely 0 (A25). This is the third face of the finding/refuting asymmetry:
 (1) the ghost/Trump-consistency shield (A42 F4) — a sound weapon that does not read the
     distinguishing hypothesis cannot kill;
 (2) the c^33 metric cover (A30) — metric covers of semantic objects explode dimensionally;
 (3) the enumeration-certificate mismatch (A43) — combinatorial quotients forget the coordinates
     that certificates price.
Corollary, positive form: BITE IS PROPORTIONAL TO PINNED COORDINATES. The census's only real
cuts are exactly where coordinates got pinned: H1's wall-flush slabs (2 of 3 coordinates pinned
=> 36/2000 along-wall positions certified exempt, the census's single positional kill); H2's
k = 3 layer (span pins tilt => all 10 survivors forced C-C, tilt classes forced into [18,72] /
[12,78] deg). Any future bulk instrument must either pin coordinates before certifying or price
structure directly (interface charging, I-L13).

## 2. H1 — the re-census (results/h1/h1_report.json, verified)

Field: A39 resealed, eta_cert = 2518483/6250000 = 0.402957280 exactly (standalone PASS,
D4-closed, 1468 atoms); thresholds W1 = 1+eta, W2 = 2+eta as exact rationals.

Ablation (cumulative orbit counts; R0-R10 = A31 verbatim, EXACT regression PASS):

| k | R10 = A31 MAIN | R11 +N1 per-wall<=3 (EXACT) | R12 +N5+N6 (EXACT) | non-thin |
|---|---|---|---|---|
| 3 | 10 | 10 | 10 | 1 |
| 4 | 140 | 131 | 131 | 17 |
| 5 | 2275 | 2007 | 2007 | 245 |
| 6 | 41951 | 33967 | 33967 | 4001 |
| 7 | 842398 | 623194 | 623194 | 67130 |

Per-filter outcomes (full ledger with soundness classes in notes/formalization.md Part 1):
- **N1 per-wall <= 3 [EXACT]**: the only hard prune. Keep-factor 0.74 at k = 7 (x1.35).
- **N2 A38.1 occupancy [EXACT-EXISTENTIAL]**: legitimate only at k = 11 (all-wall cores die);
  the all-wall share decays as exp(-0.78 k) and extrapolates to 0.18% at k = 11. Bonus squeeze:
  under N1 the walls carry <= 12 incidences, so an all-wall k = 11 core has <= 1 corner square.
- **N3 A21 THM3 [EXACT-EXISTENTIAL]**: two thirds of decorations carry a zero-pinned tilt class
  (wall-flush => phi = 0 in [0,18], THM3 free); the potentially-biteable share is flat ~31% and
  needs a forcing condition the census cannot test. Not a bulk filter.
- **N4 flush-mandatory [CONDITIONAL — provenance corrected]**: NOT certified (structure_lemmas
  marks Maxwell m >= 3k+1 SOFT; A32-H1 ruled it unusable; the A43 brief listed it as certified
  in error). Measured anyway: at L0 it is implied by non-thinness; at L1 the flush share
  collapses to 6.3e-4 at k = 11. If ever proved it lands the composed count at ~2e25 = A31's
  best case — the single biggest lever in sight, and the one that is unproven.
- **N5/N6 tight-variety W1/W2 [EXACT]**: zero kills at graph windows (m_low = 0.000000 on all 9
  wall-mask boxes). One real cut at L1: wall-flush pinning (t = 0, wall distance exactly 1/2)
  gives m_low up to 1.437085 > 1.402957 — 36/2000 along-wall slabs certified exempt on every
  wall. The only positional bite in the census.
- **N7 wastage motifs [APPROX, canary-refuted as a filter]**: Trump's own contact graph contains
  a 4-cycle — the motif proxy would delete the optimum. A23/A25 kill certified CELLS, not
  motifs. Report-only forever.
- **N8 band count [EXACT, inert]**: no L0 handle; recorded so nobody re-spends.

Composed EXACT count MAIN' = MAIN & N1 (N5/N6 inert): k = 11 projection 2.30e29 / 1.51e30 /
1.09e30 (3 models); non-thin 2.7e28-3.5e28; CONDITIONAL with N4: 1.6e26-8.9e26, with
non-thinness ~2e25. A31's NO-GO verdict on enumerate-then-solve is unchanged.

## 3. H2 — the spine census (results/h2/h2_report.json, verified)

Object: SPINE = shortest wall-to-wall H-path guaranteed by L6 (lambda0 > 0 branch); type =
(k; end types F/C; link types FL/CEab/CEba/CC), up to reversal; formal definition, certified
span arithmetic (span identity x_k - x_1 = s0 - h(phi_1) - h(phi_k)), per-link dx enclosures and
the constraint stack C0-C6 in notes/formalization.md Part 2.

Ablation (canonical types; C0 span, C1 tilt coupling, C2 joint windows+capacity, C3 W1 field,
C4 A25 wastage):

| k | raw | C0 | +C1 | +C2 | +C3 | +C4 survivors |
|---|---|---|---|---|---|---|
| 3 | 36 | 18 | 14 | 10 | 10 | **10** |
| 4 | 136 | 136 | 132 | 132 | 132 | **132** |
| 5 | 528 | 528 | 523 | 523 | 523 | **523** |
| 6 | 2080 | 2080 | 2074 | 2074 | 2074 | **2074** |
| 7 | 8256 | 8256 | 8249 | 8249 | 8249 | **8249** |
| 8..11 (C0-C2 DP, upper bounds) | | | 32888 / 131319 / 524790 / **2098165** | | | |

Where it bites, and where it cannot:
- k = 3 is the only strong layer: every F-F and most F-C types die on span (2 sqrt2 = 2.8284 <
  s0 - 1 = 2.8771); all 10 survivors are C-C (both end squares tilted), and C-FL.FL-C forces its
  tilt class into [18, 72] deg. A real, certified structure theorem for 3-chains at s-hat.
- k >= 4: span is slack by a full link; the only kills are C1's two local rules (no CE link
  between two wall-flush zero classes; no wall-corner end inside a zero class — a nice reduction
  of A31's tilt feasibility to purely local conditions on paths, worth keeping).
- C3 and C4 are INERT: 0 kills, wastage floor exactly 0 for every survivor at every k, max
  certified min-coverage 0.000000 vs threshold 1.402957. Mechanism: a spine type is a projection
  that forgets the transverse coordinate; every square window spans the full y-range, whose
  minimum touches deep-interior cells that are genuinely worthless. H1's disease one level up.
- C5 (THM3 forcing) false for every survivor; C6 (band count) provably inert with y free.

Canaries — all clean:
- Trump at s0: 30 shortest wall-to-wall chains (14 x-axis at k = 4, 16 y-axis at k = 5); all 30
  pass every realized-point check and all 30 realized types are census survivors. The tilted
  strip enters as the y-spine F-CEab.FL.FL.FL-C (1 upright + 4 tilted, flush core) — the
  5 tilted squares' own flush 5-chain 6-9-7-8-10 is NOT wall-to-wall on a single axis; recorded
  honestly.
- A37 attractors: all 12 RIGID/VALLEY/VALLEY-MARGINAL entries pass at their OWN s (163 chains,
  0 failures). Information: every valley's realized spine type ALSO survives at s0 — the spine
  stack excludes none of the known attractors at s-hat.
- Independent kill audit: a second implementation (no bins, no cells, direct tilt grid)
  re-searched all 48 killed types for witnesses: none found. Kills are not binning artifacts.

Completion cost (DESIGN ESTIMATE, no runs): survivors' anchor counts total 10^20.3 over
k = 3..7; at A35's measured 10-30 desktop-min/anchor that is 1.3e18-3.9e18 desktop-days —
and the anchor pins NO y_i and NO rattler; at A35's semantic cliff R* = 0.00586 the free
y-interval is ~490 semantic cells per spine square (~490^k unpriced). Not affordable as posed;
no per-spine far-field program is written, per the brief's "honest either way".

## 4. Lever (a) assessed on paper: the DOUBLE SPINE (no compute spent)

Idea: when BOTH axes bind, L6/L7 give an x-spine AND a y-spine simultaneously; chain members get
both coordinates pinned where the webs meet, so the placement certificates finally have a handle.

Soundness frame first (three branches, all must be carried): {lambda0 = 0} OR {mono-axis: only
one axis binds — possible in principle (cf. n = 2), y-extent in [11/s0 = 2.8372, m); no y-spine
exists there, so the single-spine census is all we get} OR {both bind: double spine}. The lever
refines only the third branch.

Crossing lemma (new, provable at T-quality, L4-style drawing argument): the x-spine's union is a
connected set joining the left and right walls, so it separates bottom from top; the y-spine must
therefore either SHARE a square with it or contain a square-square CONTACT into it. So the joint
object is a connected 2-spine web, and its crossing square (or contact pair) has BOTH coordinates
pinned to cell scale. (Trump realizes it with TWO shared squares: x-spine 0-1-8-2 and y-spine
2-8-7-9-5 share {2, 8}.)

Honest joint-type count: |joint types| ~ |tau_x| x |tau_y| x (crossing placements ~ k_x k_y)
divided by symmetry (~x4): at k_x = k_y = 5 that is 523^2 x 25 / 4 ~ 1.7e6 types — the cross
product DOMINATES and no measured cross-constraint collapses it: C0 span is slack in each axis
at k >= 4 independently, and the coupling constraints (shared-square consistency, capacity
lemma across webs, |union| <= 11) are exactly the kind the k >= 4 layers already shrug off.
Joint-type count goes UP by ~3 orders, not down.

Per-joint-type handle strength, priced from measurements already in hand: the web pins BOTH
coordinates of the crossing square(s) ONLY. At crossing-cell scale (~0.06 x 0.06 x 3 deg) the
A39 field exempts ~7% of placement cells pointwise (H1 measurement) — but a type survives if ANY
reachable crossing cell is non-exempt, and the reachable set is many cells, so expected TYPE
kills ~0; the gain is anchor-level pruning of order a few percent. C4 wastage stays inert at the
crossing: crossings live mid-container where certified dead area is genuinely 0 (A25); the
near-wall cells where wastage is worth 0.3-1.5 are exactly where crossings are not. Every
non-crossing web square KEEPS one free transverse coordinate, so the unpriced completion factor
improves only from ~490^(k) to ~490^(k_x + k_y - 2 x shared) while type count and per-type
anchors multiply. Net arithmetic: strictly worse as a completion program, ~neutral-to-x2 as a
census cut.

**RECOMMENDATION: NO-GO on a double-spine probe.** The measured mechanism (bite proportional to
pinned coordinates; one-to-two pinned squares out of ~9) predicts a type-level cut of x1.1-2 for
~3 orders more types, with the mono-axis branch uncovered besides. If the lab ever wants the
crossing-square kill fraction as a datum, it is an hours-scale composition of the existing H2 DP
with a pre-registered gate (joint-type kill >= 50%, else stop) — but the prior from H1+H2 says
it fails the gate. The next lever is not more enumeration. Two candidates rank above it:
 (i) prove OR refute a Maxwell-type row bound for FJ-critical non-thin structures (N4): the one
     unproven statement measured here to be worth x10^4 alone (composed count -> ~2e25); the
     ledger's warning (degenerate jams with fewer rows) says target a weakened FJ-specific form;
 (ii) certificates that price STRUCTURE rather than placement — the I-L13 interface-charging
     functional is the only family in the repo whose unit of account (grain boundary length x
     misorientation) matches the enumerated object; A26 killed wall-charging, but square-square
     interface charging was never built.

## 5. Gap list

- A43-G1 (scope): the lambda0 = 0 branch is uncovered by BOTH halves (same residual as A31);
  the mono-axis branch is additionally uncovered by any double-spine refinement.
- A43-G2 (H1): all A31 gaps G1-G7 inherited; N2/N3 fold in only at the k = 11 join; all k >= 8
  numbers are 3-model extrapolations with a k = 7 holdout, not bounds.
- A43-G3 (H2 scope): census covers SHORTEST spines (complete for existence; completion arguments
  must be phrased "the shortest spine has type tau"); off-spine contacts are not modelled (sound
  relaxation: over-accepts); k = 8..11 counts are C0-C2-only upper bounds at coarser cells.
- A43-G4 (H2 numerics): outward-rounded floats (nextafter + 1e-9 slop); no kill within 1e-9 of a
  boundary; x-cell DP is arc-consistent (over-accepts); C-end bins include phi = 0 (over-accepts).
- A43-G5 (fields/atlas provenance): A39 resealed field (eta 0.402957) used everywhere at s0;
  A25 single atlas at s0 only (pair atlas is 3.84-only, 54/330 unrealisable — excluded); A37
  valley canaries have no field/atlas at their own s, so C3/C4 are null there (C0-C2 complete);
  family 27's coordinates are 6-decimal rounded (weaker canary evidence, flagged).
- A43-G6 (cost model): completion estimates use A35's per-anchor constant, which is valid only
  where an anchor pins a contact structure; the transverse debt (~490 R*-cells per free
  coordinate) is stated, not priced; A38's open-ended T_decide(s0) applies to any coverage-LP
  completion and A38-G7's 3600-s calibration node is still the cheapest missing datum.
- A43-G7 (provenance correction to the brief): flush-mandatory is NOT certified; it ran as a
  CONDITIONAL column only. The brief's claim is corrected, not followed.

## 6. Files

notes/formalization.md (spine-type definition, certified span arithmetic, filter soundness
ledger), notes/compose_draft.md, notes/verification_log.md (lead spot-checks), code/h1/,
code/h2/, results/h1/h1_report.json (+ level0_k*.json, regression.json, trump_canary.json,
l1_wallflush_n5.json, field_info.json), results/h2/h2_report.json (+ checkpoints/census_k*.json,
canary_trump.json, canary_a37.json, dp_counts.json, kill_audit.json, survivors_k*.txt), logs/.
