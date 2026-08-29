# A45 — interface charging: final report (Fable lead, 2026-08-29)

## 1. Question and verdict

I-L13 asked for the graph-native certificate: per-contact-type wastage charges that
SUM over a contact graph, evading the enumeration-certificate mismatch because the
unit of account (the interface) IS the enumerated object.

**VERDICT: the calculus exists, is sound, and is fully exact-certified — and it is a
magnitude NO-GO at n = 11, by a table-independent theorem, with the mechanism named.
The attempt's live bite came entirely from the PI's two flush-ruler laws (Lemmas
R and Q), which are new EXACT census filters and close most of the zero-charge class.**
All canaries pass (Trump charge sum 0.00174 <= 4.0318; his 5-strip survives Lemma R
with margin 0.4636 exactly; his 6 uprights charge 0; ruler filter leaves 1632 feasible
assignments on his graph; A31/A43 regression EXACT).

## 2. The charging lemma (notes/charging_lemma.md — the theory deliverable)

Proved at T-quality: plane-mode position-freeness (Lemma P/P': certify with the pair
centred in a 20-container and the certificate is position-free — the A23 certifier
applies verbatim); the MOAT-VORONOI ownership scheme (Lemma M: a certified moat box
around a contact point excludes every other packing square, because the A23 dead
definition is closed-contact exclusion; Lemma M': charged contact points are >= min
moat apart; Lemma O: sup-norm Voronoi ownership is free at radius rho_min/2); and

> **Theorem A45.1 (interface charging lemma).** For any 11-packing at s <= s0 and any
> set I of charged contacts realized in table bins: sum of charge(K_i) <= s^2 - 11.

Exact zeros proved structural: FL and WF charge 0 (reentrant-notch argument — the
slid flush pair is NOT convex, the proof needed repair); CC is UNCHARGEABLE (one free
wedge at a corner-corner contact is always >= 90 deg, so no moat exists at any
radius). One degenerate leak found and patched (a corner on two walls = one uncharged
WCC interface). Lead audit trail: notes/verification_log.md V1-V6.

## 3. The certified table (agent A, results/charge_table.json) — and why it is small

75 bins swept (WC 15, CE 60), 50 dropped (no moat at 1/16 — most CE bins), 25 kept,
**all 25 exact-Fraction re-certified (270/270 tiles, 25/25 moats, 0 failures,
unmodified-A23 cross-check bit-exact)**. rho_min = 1/16, charge radius 1/32.
Best entries: WC mid-tilt 0.0069 (full plane-dead wedge 0.0537, so the ownership
discipline keeps ~1/8); CE mid-mismatch 0.00046 (full 0.0037). Trump's 25 contacts
(9 WF + 2 WC + 7 FL + 1 CC + 6 CE) sum to 57/32768 = 0.00174: capture fraction
4.3e-4 of budget, ~500x below even A26's uncharged per-square calibration 0.8672.

## 4. The NO-GO, as theorems (the finding)

**Ceiling 2 (table-independent; agent B).** charge <= rho_min^2 per contact and a
MAIN structure has <= 3k+2 contacts (A31 L4a), with rho_min <= 1/4 forced by geometry:
max conceivable charge sum at k = 11 is **(3.11+2)/16 = 2.1875 < 4.0318 — the charge
filter can NEVER fire at n = 11**, whatever the table (1.84x short at the ladder
maximum; firing needs rho_min >= 0.3394, off the ladder — no legal square within a
third of a unit of a contact point). With the ACTUAL certified table (rho_min = 1/16,
largest entry 41/65536 = 6.26e-4): max sum 0.0219, short by **184x**. Agent B ran the
census twice — stub table, then certified table — identical verdicts, which is the
point.

**Ceiling 1 (kills every alternative ownership scheme — the on-paper assessment).**
The binding constraint is not even the moat quadratic: ANY per-contact scheme is
capped by the maximal plane-dead area of the pair, measured at 0.0537 (best WC bin) /
0.0037 (CE) / 0.0232 (CC). A magic multiplicity-1 overlap-accounting scheme with
full-wedge capture sums to ~0.9 at k = 11 (~2x short even doubling for window
truncation). Bonferroni-style non-exclusive charging divides full wedges by overlap
multiplicity m ~ 6-12 — no better than the 8x the moats cost. **No ownership scheme
beats the plane-dead ceiling; refinement is pointless.**

**Ceiling 3.** Census min-over-realizations semantics zero almost every contact
anyway (CC realization loophole, WCC, dropped bins) — A43-N5/N6's disease one level up.

**Mechanism, named — the fourth face of the enumeration-certificate mismatch:**
an interface pins RELATIVE coordinates only, and relative-coordinate certificates
price only relative-coordinate wastage: the contact sliver, ~10^-2. The budget
s0^2 - 11 = 4.03 lives in the far field (A25's 0.3-1.5 corner-moats at d ~ 1.2),
priceable only with absolute coordinates. A26 = per-square charging dies on an exact
zero; A45 = per-interface charging dies on quadratic smallness; both instances of
"bite proportional to pinned coordinates" (A43) — the interface pins exactly the two
coordinates that carry the least wastage.

## 5. The live bite: the PI's quantization laws (Lemmas R + Q) [EXACT, certified]

> **Lemma R (flush-ruler cap, sharp).** A ruler of k same-class squares joined by
> k-1 same-normal series flush links has k <= s(|cos psi| + |sin psi|). At s0:
> upright rulers cap at 3 squares; 5-rulers force tilt in [20.77, 69.23] deg;
> 6-rulers are impossible. Trump's tilted 5-strip is the extremal object
> (capacity 5.4636, margin 0.4636).

> **Lemma Q (quantization).** Wall-flush anchoring pins class 0 and the anchored
> coordinate exactly; opposite-wall WF anchors at flush-graph distance <= 2 cannot
> span s - 1 in [2.80, 2.877]; spanning same-normal series force s integer: dead.

Census measurement (agent B, results/census_report.json; regression duty a full
RE-RUN, exact match to every A31/A43 number, 510-graph L1 sample 0 mismatches): at
Level 0 both new filters are PROVABLY inert (an orbit dies only if every decoration
dies, and the all-corner decoration — no flush component, charge 0 — always exists:
same law again). At Level 1: **RULER cuts ~5-7% of decoration weight per k (keep
0.948/0.942/0.939/0.938/0.928 at k = 3..7; extrapolated 0.894-0.928 at k = 11,
3-model with k = 7 holdout)**; CHARGE keep = 1.0 everywhere (Ceiling 2 realized).
**Composed k = 11 projection: A43's 2.30e29 -> 2.06-2.14e29 — RULER is worth x1.09
and nothing else moves.** The refined-gauge form is the real find: A31's factor 4
per flush edge IS the CSP's (family, sign) pair, so counting feasible assignments is
strictly stronger than the kill column at the same soundness class. Kill audit:
411/411 killed component signatures are zero-pinned (wall-anchored), fully
classified — M1 Lemma-Q path bound (392), M2 odd-cycle parity (16, a NEW mechanism:
a same-wall pin set equalises one family, forcing every link into the other, and an
odd cycle of +-1 cannot close), M3 Lemma-Q integrality (3). **Lemma R's pure length
cap contributes ZERO kills** — a decoration fixes neither normal family nor sign, so
no ruler is ever forced long: the bite is gauge multiplicity, and only where a wall
pins a coordinate. A43's law, one level down.

## 6. The zero-charge composition (Theorem A45.2) — mostly CLOSED

Zero-charge class share of decorations: 3.8% (k=3) -> 5e-6 (k=7), all components
wall-anchored (L3 forbids floating components: residue (e) EMPTY in this census).
Split:
- **k >= 10: the whole class is DEAD, exactly** — every zero-charge core is all
  class-0; A26 caps squares within 2.503 deg of upright at 9. UNIVERSAL (about the
  packing, not existential): needs no k = 11 join. The composed statement the brief
  asked for, proved.
- k <= 9: RULER kills 60-78% of the class per k; the remainder is consistent with
  9 uprights + rattlers — residue (f), quantified, stands.
- Single-grain common-tilt residue: m_ub(theta) certified table — 9 on [0,3) deg
  (residue dies there, and A26 already had that bin), 12 on [3,18), 14 on [18,45):
  **GAP-A45-Z1 stands on 14 of 15 bins** (the sharp m(theta) B&B is designed, not
  run — the one open computation of the composition). Note the eroded region is a
  rotated SQUARE, not the octagon the notes guessed (erosion of a square by a
  square); counted on the exact region.

Spot check on A43-H2's 10 k = 3 spine survivors: 0 ruler kills, 0 charge kills
(killing needs 2.02/contact vs ownership ceiling 0.0625); RULER does not even trim
a gauge assignment there — C-C ends mean no WF anchor, no pin, and every tilt
window contains 45 deg so the extent cap is slack. The 3-chain structure theorem
does not tighten.

## 7. Gap list

- G-A45-1 (= agent B G1): CHARGE inert at k <= 11 by Ceiling 2 — permanent, not a
  refinement gap.
- G-A45-2: min-over-realizations collapse (CC/WCC/dropped-bin loopholes) — any
  future contact-pricing scheme must first force realization types, not just graphs.
- G-A45-Z1: single-grain common-tilt residue at theta >= 3 deg (m_ub >= 12); the
  sharp m(theta) certified B&B is the one open computation of the composition.
- G-A45-Z2: rattler joins for zero-charge cores k <= 9 (residue (f)).
- Windows: full plane-dead maps measured to R = 1/2 (Ceiling 1 estimate has a <= 2x
  window caveat, absorbed in the stated margin).
- Agent A vs B classify one Trump ss-contact differently at the 1e-6 SAT tolerance
  (FL vs CC — both price it 0; harmless, recorded).

## 8. Files

notes/charging_lemma.md (theory + §9 verdict); notes/verification_log.md (lead
checks V1-V9); results/charge_table.json, pilot.json, canary_trump.json (agent A);
results/census_report.json, regression_b.json, canary_b.json, ruler_kill_audit.json,
spot_h2_k3.json, census_l1.json (agent B); code/ (charge certifier, plane-mode
harness), code/census/ (ruler/charge columns, m_ub); logs/. A29 untouched;
compute ~2 h total, process caps respected (A <= 2, B <= 1).
