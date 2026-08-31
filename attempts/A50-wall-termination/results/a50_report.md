# A50 — wall-termination instability + span-semigroup gaps: final report
(Fable lead + one Opus table worker, 2026-08-31)

Constants, exact throughout: s0 = 969271/250000 = 3.877084; live window
[191/50, s0] = [3.82, 3.877084]. Flush-free hypothesis throughout; per-certificate
FJ statements (D3' conventions). EXACT attempt: every table entry and key inequality
is a rational or a quadratic surd with integer-coefficient certificate; floats only
as readability labels. Checker corruption-gated (5/5). A29 untouched.

## 1. Question

A49 banked the empirical law: flush-free evasion breaks at the binding chain's WALL
TERMINATION (B-wall, 19/20 solo flush-acquisition events, simultaneous
10-13-contact collapse). A50 formalizes it: T1 = a certified Diophantine
tilt-exclusion table for wall-to-wall load chains (span-semigroup gaps); T2 = the
wall-termination instability lemma from presser-confinement (A48 C5b) x the span
table x the A49 map.

## 2. T1 — the span-semigroup gap program (notes/span_semigroup.md, code/, results/span_table.json)

Object: P-CHAINS — wall-to-wall load chains whose links are x-pinning (corner-corner,
corner-on-vertical-edge-of-class-0, wall-corner ends); exactly the geometry of the
A48/A49 evasion architecture, containing A47 T1's thin branch as the L2-forced
special case. Step ledger (Lemma S1): each tilted square advances by one of
{cos phi, sin phi, cos phi + sin phi, cos phi - sin phi}, each class-0 square by 1;
ends are tilted (class 0 at a wall is WF flush). Span quantization (Theorem S2):
equal-class chain span = a cos phi + b sin phi + c, index set A(6) (|A(6)| = 172,
|A(8)| = 375) from chain length L in [3,6] (H-L6CAP; L >= 3 certified, <= 6
conditional on presser-distinctness; L <= 8 robustness column shipped). Window gap
(Theorem S3): termination at side s forces f_abc(phi) = s EXACTLY (zero end
offsets, derived — wall corners pin x = 0 and x = s), so s in [191/50, s0] needs a
semigroup element in the window. Every island boundary is a root of the rational
quadratic (c-w-a)t^2 + 2bt + (a+c-w) in t = tan(phi/2): the table is computed
EXACTLY — no grid, no floats — as a finite union of intervals with quadratic-surd
endpoints.

**THE TILT-EXCLUSION TABLE (equal-class, monotone, L <= 6).** Eight exact gaps,
5.982138 deg of (0,45] excluded (13.3%); phi > 45 reads through the (a,b) swap:

| # | excluded phi (deg) | width |
|---|---|---|
| 1 | (0, 1.7347) = (0, theta*) | 1.735 |
| 2 | (4.949, 5.857) | 0.907 |
| 3 | (8.953, 9.777) | 0.823 |
| 4 | (10.712, 11.749) | 1.037 |
| 5 | (13.973, 14.075) | 0.103 |
| 6 | (26.232, 26.935) | 0.703 |
| 7 | (36.620, 37.208) | 0.588 |
| 8 | (40.254, 40.341) | 0.087 |

(Exact endpoint quadratics + enclosures < 1e-15 in results/span_table.json and
results/t1_table_report.md.) L <= 8 column: gaps 1, 2, 4, 6 are cap-independent;
3, 5, 7, 8 shrink. Meaning: for phi in a gap, NO equal-class flush-free P-chain of
that class terminates wall-to-wall at ANY live s — with L6, no binding chain of
that geometry exists at all.

**NEAR-FLUSH EXCLUSION (the headline; window-class variant V1, no equal-class
hypothesis).** theta* = root of 1969271 t^2 + 2000000 t - 30729 (i.e.
4(cos-sin) = s0), theta* = 1.7346504... deg. For EVERY chain with all tilt classes
in [0, v], v < theta* (classes free within the window, not equal), every reachable
span misses the live window — audited over ALL multisets (421 at L <= 6, 1236 at
L <= 8, plus the mixed-link extensions), exact. This is the programme's first
quantitative near-flush exclusion of delta_0 type — at CHAIN level, the only level
W1's refutation (A46 bridge) left possible: a flush-free binding chain cannot stay
within 1.73 deg of upright anywhere in the live window.

**Honest sharpness findings.**
- V2 (H-MONO dropped, signed steps): exclusion drops 5.982 -> 3.747 deg but does
  NOT collapse; gaps 6, 7 survive verbatim, the near-flush gap shrinks to
  (0, 1.166) deg.
- E1 (mixed-normal links allowed, m = 1, 2): ALL interior gaps dissolve; the
  admitted set becomes exactly [theta*, 45]. So the interior gaps are artifacts of
  full x-pinning (consumers must pin P-rigidity to use them), while the NEAR-FLUSH
  GAP IS ROBUST — it survives mixed links, the L <= 8 cap, and (shrunken) even
  dropping monotonicity.
- V1 sweep: sliding tilt-window classes of width >= 2 deg are never excluded away
  from near-flush; the table's power is over narrow tilt profiles — which is
  exactly what the A49 architectures are.

## 3. T2 — the wall-termination instability lemma (notes/wall_termination.md)

Status: PROVED IN BRANCHES, one named gap.

- **T2.1 (near-flush wall termination is dead) [T][X].** Under H-P + H-MONO +
  H-L6CAP: a flush-free wall termination of a binding chain with all classes
  < theta* does not exist at any live s (immediate from V1). Retro-explains A49's
  near-upright seeds: their binding chains could never terminate flush-free.
- **T2.2 (tilt pinning) [T][X].** At an FJ point at side s, an equal-class P-chain
  satisfies f_abc(theta) = s: theta lies in a finite algebraic set Theta(s) (at
  most two roots per triple). The chain tilt carries no continuous freedom;
  sigma-descent must rotate the whole class coherently at rate ds/f'(theta).
- **T2.3 (instability / overdetermination) [T, branch (i)].** Branch (i),
  CC-PINNED PRESSER (the A49 P-CONF architecture): the C5b torque balance
  u_geo(theta) = sin^2 theta is a second independent algebraic equation on top of
  f_abc(theta) = s. Unless identically satisfied (per-family exact divisibility
  check by cos^2+sin^2-1), the simultaneous system confines flush-free wall
  terminations to a FINITE set of side lengths per chain family; at every other s
  the closing rotation of the wall wedge is a strict first-order descent direction
  (W1.2 read backwards). The termination is a codim >= 1 coincidence — the formal
  content of "the evasion breaks at the wall".
  Branch (ii), FREE PRESSER = **GAP A50-G1** (below): C5b's evasion survives
  first-order analysis when the presser reaches the end square only through slides.
- **T2.4 (the A49 collapse mechanism, interpretation).** The wall termination is
  the unique contact whose flushing dissolves the global span constraint: WF
  acquisition converts the quantized (SPAN) equation into an interval condition,
  releasing every chain square's pinned tilt AT ONCE — the simultaneous
  10-13-contact collapse, B-wall solo dominance, and "presser never first" of the
  A49 map, in one mechanism. Not a theorem; the formalization target is exactly
  A50-G1 route (1).

## 4. Canaries — 4/4 PASS (results/canaries_a50.json; lead independent re-check in notes/verification_log.md)

- **C1 (s\* window):** at phi = 45 (exact Q[sqrt2]) the hitting set is exactly
  {a+b = 4, c = 1} (6 triples), span 2 sqrt2 + 1 = s\*; A47 Corollary T1a
  reproduced with the predicted non-thin splittings. (Note: (5,-1,1) appears via a
  zero-length antidiagonal step at exactly 45 — boundary of strict monotonicity;
  admission is unaffected, (2,2,1) alone carries it.)
- **C2 (Trump spines, machinery canary):** x-spine 0-1-8-2 and y-spine 2-8-7-9-5
  give ledger residual EXACTLY -5287/50000000000 (~1.06e-7, the certificate's
  uniform slack) against the A43 span identity — lead reproduced independently,
  same exact rational. Trump's spines carry flush links: outside the flush-free
  P-chain class, so the table claims nothing about them; the canary certifies the
  arithmetic.
- **C3 (the 2.6e-6 margin):** 191/50 - 5 cos theta_T = 42003301/15959754923050 > 0
  exactly (a float implementation would be inside noise). theta_T = 40.1819 deg is
  nevertheless ADMITTED — unique hitting triple (0,6,0), six sin-steps,
  f = 6 sin theta_T in the window; it sits 0.072 deg below gap 8. The brief's
  "Trump spines admitted at their exact tilts" holds in this precise sense.
- **C4 (theta\*):** exact sign checks bracket the root; the V1 audit covers every
  multiset, not only the binding families ((n2,n3) = (3,3) from below, n4 = 4 from
  above — theta* is SHARP: gap 1's upper endpoint is the same surd).

## 5. Verification map

Exact sweep in code/span_table.py (surd comparisons by exact-sign bisection +
rational-quadratic gcd for equality). Independent checker code/checker_span.py:
separate algebra path (own index-set enumeration, own root isolation, own surd
order), reconstructs the full labelled decomposition of (0,45] and re-verifies the
near-flush audits and V1 sweep; corruption gate 5/5 detected (endpoint widened
1e-9; deleted triple; sign flip; s0 off by one; relabelled interval) —
logs/checker_gate.log: PRISTINE PASS, GATE PASS. V2/E1 blocks are exact but
report-only EXCEPT the load-bearing E1 near-flush survival, which is gated.
Lead spot-checks (independent code): theta* quadratic + 1.7347 correction, C3
margin, s* squaring, Trump residuals, |A(6)| = 172 (notes/verification_log.md).

## 6. Gap list

- **A50-G1 (THE gap; T2 branch (ii)):** free presser / one-wall-anchored press
  chain — C5b's evasion when the torque-decisive presser reaches the end square
  only through slide DOFs. Its span is s - y_anchor with y_anchor free: nothing
  quantizes it. Routes, by expected cost: (1) SECOND-ORDER descent at the C5b
  balance (sign of the second variation of sigma along closing + slide relaxation;
  finite exact-rational curvature computation — recommended next-attempt target);
  (2) both-axes coupling (y-chain is itself table-bound; crossing argument;
  mono-axis branch stays open); (3) a new absolute-position certificate class
  (A45 fourth-face law says current tables cannot charge it; C6' says budget
  composition needs it anyway).
- A50-G2: H-MONO unproved for general H-paths (V2 quantifies the cost: near-flush
  gap shrinks to (0, 1.166 deg), interior gaps 6, 7 survive).
- A50-G3: H-L6CAP conditional (presser-distinctness); L <= 8 column shipped, gaps
  1, 2, 4, 6 cap-independent.
- A50-G4: interior gaps require full P-rigidity (E1 dissolves them); only the
  near-flush gap is hypothesis-robust. Consumers (census/case-tree nodes) must pin
  chain rigidity to use interior gaps — same consumption pattern as A48's
  escalation signatures.
- A50-G5: outside the model — multi-class chains beyond the window variant,
  L >= 9, adjacent-edge mixed traversals (H-OPP), degenerate dx = 0 steps,
  lambda0 = 0 branch (as always).
- A50-G6: T2.3's per-family objects (the identity check and the finite exceptional
  s-sets) are instantiation obligations — enumerable with the same machinery when
  a census node pins a family; not enumerated here.

## 7. Verdict

T1 DELIVERED: certified exact tilt-exclusion table (8 gaps, 5.98 deg at L <= 6;
robustness columns; all boundaries quadratic surds; corruption-gated checker;
canaries 4/4 incl. the s* window and both Trump spines). T2 CONDITIONAL-PROVED:
near-flush wall terminations excluded below theta* = 1.7347 deg (robust to every
relaxation tested); tilt pinning exact; instability proved on the CC-pinned-presser
branch as an overdetermination theorem; the free-presser branch is the single
remaining gap (A50-G1), with the second-order C5b computation named as the
cheapest route. The A49 collapse map now has a mechanism: the wall termination is
the chain's only span-releasing contact.
