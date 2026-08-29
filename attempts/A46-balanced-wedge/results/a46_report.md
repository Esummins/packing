# A46 — flush-mandatory via the balanced-wedge budget: REFUTED twice over, with theorems banked
(Fable lead + Opus W2 agent, 2026-08-29)

## 1. Question and verdict

I-L17 asked for the pincer's second jaw: prove that no FJ-critical structure at s <= s0 is
flush-free, via W1 (balanced corners have mismatch delta >= delta_0) AND W2 (certified wedge
table w(delta) + disjointness + budget composition > B0 = 4.031780343056).

**VERDICT (three lines).**
1. **W1 is FALSE — refuted independently by theory and by measurement.** Theory: the BRIDGE
   mechanism (notes/w1_theory.md par.5, exact-Fraction verified) balances a loaded
   corner-on-edge contact at EVERY mismatch delta > 0 with generic neighbours and bounded
   multipliers — no local first-order argument can exclude it, and the stratum/limit route
   dies structurally (bounded multipliers, smooth limit onto the flush stratum). Measurement:
   genuine critical points USE near-flush loaded contacts — family A37-NEW-0 carries a
   FORCED CE row at delta = 1.029 deg, family 31 at 2.272 deg [float audit]. No usable
   delta_0 exists. Balance does NOT force large angles: the PI's dichotomy premise fails.
2. **W2's budget can never reach B0 anyway — a magnitude no-go on top.** Even at the fantasy
   threshold delta_0 = 45 (every contact maximally mismatched), the honest flush-free minima
   (derived from L1/L2/L6/L7/L11 only — the true thin minimum is 4 contacts, not 17) fall
   x2.0-x6.9 short of 4.0318; and if the interior contacts are CE the ceiling is
   table-independent: max conceivable = 2.817 = 0.699 B0 — a CE-only flush-free structure is
   unkillable by ANY per-contact dead-area certificate (A45's Ceiling-2 law, one level up,
   ~10x less severe, still binding). The fire zone is exactly FIVE points of the count
   lattice (n_WC >= 11 at tilt (40,45] AND >= 20 sharp-wedge CC interiors) — the genuine
   atlas maxes at 3 wall contacts and 1 CC (aligned, worth 0). Nothing real is near it.
3. **What survives is substantial.** A genuine structure theorem — flush-free thin load
   chains QUANTIZE to exactly 45/0 tilts and 3-chains are impossible at s0 — plus the
   strongest certified charge table the lab has (w_WC, 11/11 bins exact, 280x A45's
   per-contact charges, Trump capture 12% vs A45's 0.04%), the torque dichotomy toolkit,
   a CC convention correction (sharp free-wedge angle governs; 19x between same-mismatch
   bins), and the named successor primitive (multi-square corner hypotheses) that is the
   one direction that could move the numbers.

Honest refutation = success, again: I-L17 is now settled as a route (dead, with the failure
mechanism named at both ends), and the flush-mandatory statement itself survives only as an
atlas-consistent conjecture that no wedge-budget argument can reach.

## 2. W1 theory (notes/w1_theory.md; exact cross-checks code/w1_checks.py, ALL PASS)

Proved at T-quality:
- **W1.0 (alignment taxonomy).** An interior corner-on-edge contact at mismatch 0 mod 90 IS
  a flush contact — there is no "T-contact" loophole; CE always has delta in (0,45]
  strictly; WC tilt likewise; the only zero-charge flush-free square-square type is the
  ALIGNED corner-corner (both free wedges exactly 90). [Confirmed by W2: all 7 atlas CC
  contacts are aligned, certified charge exactly 0.]
- **W1.1/W1.2 (torque dichotomy).** dg_k = omega * cross(p_k - q, n_k) for every row type
  under rotation about the contact corner q; hence at any FJ point a LOADED corner contact
  forces on its corner square either a force pencil through q or loaded blockers AND loaded
  closers (two-signed torques). This subsumes the brief's "sigma-non-increase of closing"
  and is immune to the bounding-box coupling worry.
- **W1.3 (pencil reduction).** The pencil branch collapses to a codim >= 2 double-brace
  signature: an aligned-CC brace at BOTH far corners (or an exact-45 far-corner contact).
  The D3' tie-menu attack on it provably fails (loadedness of CC-braced contacts is
  selection-dependent) — recorded so nobody repeats it. Exclusion open [W1-G1].
- **W1.4 (blocker taxonomy + wall-lever collapse).** At small delta the only blockers are
  right-edge CE, the bridge corner, the far corner, and (confined within 2 tan delta of the
  wedge ends) the bottom edge; a WALL can block only through the near-flush corner itself
  with torque arm sin delta — wall-blocked families need lambda ~ 1/sin delta and die in the
  limit. The resistant blockers are square-square.
- **W1.6 (45/0 quantization — the keeper).** In a flush-free configuration every degree-2
  loaded square is L2-thin, and a thin wall-to-wall chain forces: contact normals all +-e1
  on one line, corner-OWNING squares at tilt EXACTLY 45, receiving squares at EXACTLY class
  0, chain ends owners (receiver at a wall = WF flush), adjacent receivers linked only by
  aligned CC. Span arithmetic: 2 sqrt2 + 1 = 3.8284 < s0 exactly, so 3-chains are
  IMPOSSIBLE; the minimal flush-free thin structure is [45, 0, 0, 45] with 2 WC(45) +
  2 CE(45) + 1 aligned CC. The near-flush escape is CLOSED on the thin branch with no
  delta_0 — thin structures charge at the LARGEST bins by theorem. Its completion question
  reduces to finite rectangle-packing lemmas (7 squares in the complement strips) [W1-G3].
Refuted [MECH]: the uniform delta_0 — the bridge (a's far bottom corner resting on a
support edge sloping g >= delta, presser above, exact multipliers lam_b = sin(g-d)/sin g > 0
etc., verified in rational trig down to d = 0.057 deg).

## 3. W2 measurement: the empirical W1 verdict (results/atlas_mismatch_audit.json, FLOAT)

All 12 genuine A37 entries + Trump, contacts re-extracted and classified, loadability from
A44's FJ LP. Global minima: **loaded CE mismatch 1.029 deg (A37-NEW-0, forced row), 2.272
(fam 31), 7.106 (A37-NEW-3); any CE 0.196 deg (fam 01, unloadable); loaded WC tilt 33.9
deg; CC always aligned = charge 0.** Genuine critical points live at the near-flush end W1
needed to exclude. (Float-only — the atlas stores radians; this is a measurement, not a
theorem.)

## 4. The certified tables (results/w_wc_table.json, w_ce_cc_pilot.json)

- **w_WC(phi), 11 bins over (0.5,45] deg: ALL EXACT** (869/869 tiles recertified in pure
  Fractions, 0 failures; A45 WC frame, PlacedBox nsub=4 bin-uniform, Lemma-P' wall mode,
  Lemma-K slab keeper measured to cost ZERO in this window). Range: 0 at (0.5,1] (true area
  ~sin(phi)/2 below the 1/64 resolution floor) up to **453/2048 = 0.2212 at (40,45]**. Full
  exact radial profiles shipped (every entry inside sup-radius 1 of the contact point) —
  the disjointification input. This is ~280x A45's best per-contact charge (0.221 vs
  6.26e-4): the moat/ownership discipline, not the geometry, was A45's cost.
- **CE pilot: <= 29/4096 = 0.00708 (exact at (39,42])**, 0 below 5 deg — interiors are 31x
  weaker than wall wedges, confirming the lead's estimate.
- **CC pilot + convention correction: the governing parameter is the SHARP FREE-WEDGE
  angle, not mismatch mod 90** — bins of identical mismatch differ 19x (0.0037 vs 0.0706);
  max 289/4096 = 0.0706 (exact) at wedge (20,30]; ALIGNED CC certifies exactly 0.
- **Disjointness** (code/clip_util.py, exact): along-wall Voronoi truncation (inert to r=3
  per wall, saturating at 0.9317/wall), opposite-wall slabs disjoint (2 x 5/4 < s0),
  adjacent-wall corner handled by deduction/diagonal-split (implemented; 0 in every
  evaluated profile).

## 5. The composition: no delta_0 exists, and none could (results/composition_report.md)

Honest minimum contact counts from L1/L2/L6/L7/L11 + planarity only (17 was never honest):
thin minimum **4 contacts** (2 WC + 2 interior), non-thin minimum **6** (3 WC + 3 interior,
k_H = 3), all-loaded k_H = 11 gives 20. Pricing every profile at its most favourable bins:

| profile | sum at delta_0 = 45 (fantasy best) | shortfall vs B0 |
|---|---|---|
| THIN 1-axis (4 contacts) | 0.583 | x6.9 |
| NONTHIN k_H = 3..5 | 0.875-0.936 | x4.3-4.6 |
| THIN 2-axes / nonthin 2-axes | 1.026-1.096 | x3.7-3.9 |
| k_H = 11 all loaded (20 contacts) | 2.014 | x2.0 |

Table-independent ceiling: with CE interiors, max conceivable (12 wall incidences at the
maximal bin + 23 interiors) = **2.817 = 0.699 B0 — inert forever**. Only sharp-wedge-CC
interiors can conceivably fire, and the fire zone is exactly 5 count-lattice points
(n_WC >= 11, all at (40,45], plus >= 20 sharp CC) — no genuine structure is within a factor
of 4 of it (atlas max: 3 wall contacts, 1 CC, aligned). **Answer to the brief: there is no
delta_0; the composed theorem does not close at n = 11.** The mechanism is the fifth face
of the enumeration-certificate mismatch: balance pins ANGLES, but wedge area is quadratic
in nothing — it is the COUNT that is short, and criticality honestly forces only 4-6
contacts, not 17.

## 6. Canaries (results/canaries.json) — ALL PASS

Trump (exact extraction): 25 contacts, charge sum 0.4849 <= 4.0318 (capture 12.0%; A45
captured 0.04%). All 12 atlas families at their own s: PASS, max capture 14.0%. The table
is sound and 7-100x too weak on real structures — the loss is in the count, not the
certificate.

## 7. Keepers (banked) and the successor direction

1. **Theorem W1.6 (45/0 quantization + 3-chain impossibility)** — the first structural
   theorem about flush-free critical configurations beyond the L-lemmas; census-usable as a
   hard prune on thin flush-free branches (they are a measure-zero, explicitly enumerable
   family), and its residue is reduced to finite rectangle-packing lemmas.
2. **The w_WC table** — the strongest certified per-contact charge table in the lab (280x
   A45); future uses: wall-ledger arguments (A26 revival at mid-tilt), per-wall occupancy
   caps, seam/corner analyses, and any argument needing "a tilted wall contact strands
   >= w_WC(phi)". Radial profiles make it composition-ready.
3. **The torque-dichotomy toolkit (W1.1-W1.4)** — per-contact FJ structure extraction
   (blocker taxonomy, wall-lever collapse, pencil reduction), reusable wherever criticality
   must be converted to local geometry.
4. **CC sharp-wedge convention** — any future contact-pricing must index CC by free-wedge
   angle (19x within a mismatch class), and aligned CC is exactly zero (proved + certified).
5. **Successor primitive (I-L18 candidate, recorded, NOT pursued): multi-square corner
   hypotheses.** A23-4b certified 0.34-0.54 for ONE square in a container corner (2.4x the
   single-wall wedge); W2's gap list item 21 identifies interface+wall / multi-square
   hypotheses as the one direction that moves numbers — the charge unit would be the
   BALANCED JUNCTION (pair + pinned blocker geometry from the W1.4 taxonomy), pricing the
   b|d chimney under a bridge rather than the pair sliver. Expected gain: one order of
   magnitude on interiors; still needs a count argument to close any budget.

## 8. Gap list

- **A46-G1** (= W1-G1): the codim >= 2 pencil/double-brace tower is reduced, not excluded
  (first-order per-selection FJ provably cannot; second-order or completion needed).
- **A46-G2** (= W1-G2): bridge GLOBAL realizability at sigma <= s0 was probed only via the
  atlas (which answers: yes, near-flush loaded rows occur in genuine valleys at 1-2 deg);
  no certified flush-free critical point was constructed — flush-mandatory itself remains
  an open, atlas-consistent conjecture (every genuine entry has F >= 3 flush edges, A44 B6').
- **A46-G3** (= W1-G3): the [45,0,0,45] thin residue reduces to "7 unit squares in the
  complement strips" rectangle lemmas — designed, not run.
- **A46-G4** (= W1-G4): the neighbourhood form of the limit argument (near-flush criticals
  lie within h(delta) of the flush stratum) is stated, not quantified.
- **A46-W2-1..4** (composition_report.md sect. 7): CE/CC far-field outside conv(a cup b)
  dropped (weakens only the fire zone); per-wall Voronoi saturation is an empirical max over
  one family (not load-bearing at N1 <= 12); adjacent-wall deduction implemented but
  unexercised; the lambda_0 = 0 branch has no wall contacts and the composition is vacuous
  there (inherited ledger branch).
- **Float scope**: the entire atlas audit (radians in the atlas), 5 of 8 pilot CE/CC bins,
  atlas canary rows. Everything load-bearing in the tables and the verdict is exact
  Fractions (869 + 20 + 44 + 58 tiles, 0 failures).
- N1 <= 12 and 3k+2 = 35 quoted from A45/A31, not re-derived.

## 9. Files

notes/w1_theory.md (W1.0-W1.6, bridge, route-b obituary), code/w1_checks.py (exact
cross-checks, ALL PASS), code/ (W2: a46_lib, task1-6, clip_util + A45 harness verbatim),
results/ (atlas_mismatch_audit.json, w_wc_table.json, w_ce_cc_pilot.json, composition.json,
composition_report.md, canaries.json, this report), logs/, LOG.md. A29 untouched; no prior
attempt modified. Compute ~35 min total, <= 3 concurrent processes, all long runs
checkpointed.
