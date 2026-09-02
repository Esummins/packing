# The pair-certificate soundness lemma (Lemma P) — A66, 2026-09-02

The certificate family `h10_stuck.md` §8 named as the cheapest formalism that can see what
single-square measures provably cannot: atoms price unordered PAIRS of placements, and the
stuckness revenue is the per-box 2-crowd of CC-2′. Format frozen in
`docs/specs/pair_certificate_v1.md`; this file carries the mathematics: the kill lemma at
drain-v3 rigor, the closed-vs-interior bridge clause for the pair rows, the exact form of the
stuckness hypothesis consumed, the β = 0 emptiness corollary, the death-witness criterion, and
the A34 non-applicability argument. Labels: [T] proved, [S] routine given cited items,
[M] measured exact.

Standing ingredients: Δ_λ dilation facts B.0(a)–(c) and Corollary B′'s margin bookkeeping
(`closed_disjoint_bridge.md`); the teleport-stuck selection chain (`unique_transfer.md` §2);
CC-2′ re-based on teleport-stuckness (A58 §2; re-base per `h10_stuck.md` standing-ingredients
paragraph); the unclipped-box census and its s-stability (A58 occupancy matrix; A53 L2(iv);
exact per-class lists `attempts/A65-low-k-closure/results/h10_boxspec.json`).

## 1 The certificate's claim (from the spec, restated)

A `pair-certificate-v1` PASS at side s″ for class S (k pins, N = 11 − k, m boxes) declares
axis slack cores K_1…K_k (half-side a = 1/2 − δ, δ > 0, centred at slots_S(s″)), widened
boxes B̃_1…B̃_m (closed axis squares, centre = the s″ slot-box centre, half-side 1/2 + ε_box),
β ≥ 0, and an atomic pair measure: atoms ((p_i, p′_i), w_i ≥ 0), W₂ = Σ w_i. It establishes:

> **(P1′)** W₂ < C(N,2) + β·m, and
> **(P2′)** every unordered pair {Q, Q′} of closed unit squares in [0, s″]², each meeting no
> core (closed intersection), with int Q ∩ int Q′ = ∅, satisfies
> μ₂{Q,Q′} := Σ{ w_i : one of p_i, p′_i lies in Q and the other in Q′ } ≥ 1 + β·m₂(Q,Q′),
> where m₂(Q,Q′) = #{ i : int Q ∩ int B̃_i ≠ ∅ and int Q′ ∩ int B̃_i ≠ ∅ }.

## 2 [T] Lemma P (pair kill, with the bridge built in)

**Lemma P.** Let C be a pair-certificate-v1 PASS at side s″ for class S as above, and let

  m̃ ∈ ( s″ / (1 + δ/A), s″ ),  A = 5/2  (the slack-core shell of B.4, OPEN at the bottom:
  at the endpoint the core containment margin degenerates to 0 and (H)-type interior
  containment fails), and
  ε_box ≥ 3·(s″/m̃ − 1)   (satisfied for the whole shell when ε_box ≥ 3·δ/(A − δ) ≥ 3(λ_max−1)).

Then no teleport-stuck packing at side m̃ has skeleton exactly S.

*Proof.* Suppose z* is such a packing: axis pins at slots_S(m̃), free squares q_1 … q_N (in
stratum S the non-pin squares are exactly the non-simple ones). Set λ = s″/m̃ > 1 and dilate.

1. *Bridge.* Δ_λ z* is a family of 11 closed unit squares in [0, s″]² (B.0(b)), pairwise
   disjoint **as closed sets** with SAT gap ≥ λ − 1 (B.0(a)).
2. *Cores are owned.* The dilated pin j is axis-aligned with centre within (λ−1)·A < δ = ρ
   per axis of the s″-slot (B.0(c)); the axis core of half-side 1/2 − δ centred at that slot
   therefore lies in the open interior of the dilated pin (Corollary B′'s computation with
   θ_c = 0). Hence each core is contained in its owner; every dilated free square Δq_a is
   disjoint from the dilated pins (step 1), so it meets no core: **core-free**.
3. *Incidences survive widening.* If x ∈ int q_a ∩ int B_i(m̃) then λx ∈ int Δq_a ∩
   int λB_i(m̃), and λB_i(m̃) ⊆ B̃_i: per coordinate the m̃-box centre is α + β_c·m̃ with
   |α| ≤ 5/2 (A56 P1 slot arithmetic), so |λ(α + β_c m̃) − (α + β_c s″)| = (λ−1)|α| ≤
   (λ−1)·5/2, while the half-width grows from 1/2 to λ/2 = 1/2 + (λ−1)/2; total excursion
   ≤ 1/2 + 3(λ−1) ≤ 1/2 + ε_box. ∎(step)
4. *Stuckness rows consumed.* z* teleport-stuck ⇒ by CC-2′ (re-based: derived from
   teleport-stuckness alone) every unclipped completable box B_i(m̃) of S — the census list is
   s-stable, so it is the s″ list read at m̃ — is met (open interiors) by ≥ 2 distinct free
   squares. **This is the entire stuckness input**: one unordered pair π_i per box, both
   members meeting int B_i(m̃); no CC-3/CC-4/corridor content is encoded. By step 3, both
   members of π_i meet int B̃_i after dilation, so Σ_{a<b} m₂(Δq_a, Δq_b) ≥
   Σ_i #{boxes whose chosen pair is {a,b}} summed = m.
5. *Rows apply.* Each unordered pair {Δq_a, Δq_b} (a < b) is admissible for (P2′): both in
   [0,s″]², core-free (step 2), interiors disjoint (step 1, strictly). Hence
   μ₂{Δq_a, Δq_b} ≥ 1 + β·m₂(Δq_a, Δq_b).
6. *Additivity.* Σ_{a<b} μ₂{Δq_a, Δq_b} ≤ W₂: an atom (p_i, p′_i) is collected by {a,b} only
   if p_i and p′_i lie in the two (distinct) squares; since the Δq are pairwise disjoint
   closed sets, p_i lies in at most one square and p′_i in at most one, so each atom is
   collected by at most one unordered pair.
7. *Chain.* W₂ ≥ Σ_{a<b} (1 + β·m₂) ≥ C(N,2) + β·m > W₂ by (P1′). Contradiction. ∎

Remarks. (i) λ > 1 is used exactly where Lemma B uses it: closed disjointness for atom
additivity (step 6) and owner disjointness (step 2); at m̃ = s″ the lemma is NOT asserted —
the shell is half-open, as everywhere in the composition. (ii) The row quantifier is
interior-disjoint pairs, a superset of the realised (strictly disjoint) pairs — conservative.
(iii) β = 0 needs no boxes and no stuckness; see §3. (iv) Window form: identical status to
every fixed-side kill — the slack-core grid (B.4) covers [3.82, s0] with ~37 sides at
δ = 1e-3, or a parametric re-emission; nothing pair-specific changes the bookkeeping, except
that consumers must carry ε_box ≥ 3(λ_max − 1) per grid slab.

## 3 [T] Corollary P0 (β = 0: EMPTINESS, no stuckness hypothesis)

If the certificate has β = 0 (boxes ignored) and W₂ < C(N,2), then no packing at side
m̃ ∈ (s″/(1+δ/A), s″) contains axis-aligned unit squares at all pins of S **at all** — not
merely no stuck one. *Proof.* Steps 1–2 and 5–7 with the N non-pin squares of an arbitrary
packing containing the pins; stuckness (step 4) is never used. ∎

This is the constructive residue route (a) of `corners4_empty.md` §6: the single-square
analogue is blocked by K1 aliveness (τ* ≥ N), but the pair analogue of aliveness is the
existence of a full N-family of pairwise-disjoint core-free squares — which for corners4 is
exactly what the A65 search could not find. A P0 PASS for corners4 would delete the class
outright on the certified shell(s).

## 4 [T/M] The decision criterion (both directions) and the canary theorem

**Death witness [T].** If N pairwise-disjoint (closed) core-free unit squares exist at s″
with Σ_{a<b} m₂ ≥ m, then every certificate satisfying (P2′) has W₂ ≥ C(N,2) + β·m — sum the
rows over the family's pairs (additivity as in step 6). The pair route is then dead for the
class at every β, decisively.

**Canary theorem [T+M].** Trump's packing supplies such a death witness for its own class:
on trump5 (N = 6, m = 6) his six non-simple squares realise every box with exactly 2 meeters
(A58 §5 canary, re-tallied in `h10_stuck.md` §2). His packing has contacts, so the witness is
its **dilated image**: for any certificate side s″ whose Lemma P shell contains ŝ — i.e.
exactly the certificates that would bind Trump — Δ_{s″/ŝ}(his six free squares) is pairwise
closed-disjoint, core-free (steps 1–2 of Lemma P), and keeps every box incidence (step 3), so
Σ_{a<b} m₂ ≥ 6 = m and every valid pair certificate at such an s″ has
W₂ ≥ C(6,2) + 6β = threshold: **no pair certificate whose shell reaches ŝ can kill trump5.** The design provably spares the canary — the pair threshold is saturated with
equality by the packing every argument must spare, exactly as H10-I is (load 2.00). The
formalism's power is confined to classes where the 2-crowds are NOT jointly realisable.

**Kill hope [M].** k4_08 (N = 7, m = 7): the best exactly-verified family realises
Σ_{a<b} m₂ = 6 < 7 (crowdfam box_coverage (2,2,2,2,2,2,1): six boxes with exactly one
realised pair, the TL(0,0) box deficient — `attempts/A65-low-k-closure/results/crowdfam.json`).
The integral obstruction is short by exactly one pair-incidence; the fractional pair-LP value
τ₂(β) against threshold C(7,2) + 7β = 21 + 7β is the pilot question
(`attempts/A66-corners4-pair/`). corners4 (N = 7, m = 8): no family exists at all; both the
β = 0 emptiness form (threshold 21) and the boosted form (21 + 8β) are structurally open to
certification.

## 5 [T] Why the A34 collapse theorem does NOT apply

The collapse theorem (A34 `notes/verdict.md` §1) caps any sparse moment/SOS relaxation whose
cliques carry ≤ m′ < n squares at s(m′): from an optimal m′-packing it builds locally
consistent clique measures — pair cliques collapse to s(2) = 2. Three reasons it has no grip
here, in decreasing order of importance:

1. **The pair certificate is a pricing dual, not a feasibility relaxation.** Its rows
   quantify over single realised pairs of a hypothetical 11-packing at the fixed side s″ with
   the class pins as cores; no consistency between rows is asserted, no marginal of any
   relaxation variable exists, and there is nothing to glue. The anti-correlated-triangle
   escape (marginal agreement without a global measure) needs a family of local measures
   asked to agree; the certificate asks no such question.
2. **Every row already carries global data.** A row's admissibility condition (containment in
   [0, s″]², core-freeness against all k pins) embeds the full container and skeleton — the
   "square support" of each constraint in A34's sense includes the pins, and the certified
   side is s″ ≈ 3.877, not s(2).
3. **The stuckness revenue couples to the global budget.** The kill compares W₂ against
   C(N,2) + β·m, a count over ALL pairs of the family at once; the additivity step consumes
   pairwise disjointness of the entire 11-square family (an n = 11 fact). No 2-square
   subconfiguration certifies or refutes Σ m₂ ≥ m — precisely the coupling whose absence
   collapses pair-clique relaxations. Conversely: what WOULD reintroduce the collapse is
   replacing the per-pair rows by pair-marginal consistency constraints on a relaxed packing
   measure; the spec's semantics (§1) forbids that reading.

In A34's vocabulary: pair STRUCTURE here means pairs are the priced test objects (the
analogue of single placements in `measure-certificate-v1`), not the support of relaxation
cliques. The certificate's strength lives in the row quantifier (checked by branch-and-bound,
co-NP side), not in any moment matrix.

## 6 [T] Lemma P-B: the basin-exclusion discount (PI's fat-mass row, drain-basin framing)

The ε-parking ghost's home — the Trump-image perturbation families that A65 found to be the
ONLY realisable death-witness material — is an open neighbourhood that the A36 basin deletes
QUANTITATIVELY for exact-form strata. Monetised at pair level it is a row DISCOUNT with a
threshold rebate, and the accounting favours the certificate 21 : 15.

**Setup.** Setting of Lemma P (class S, k pins, N = 11 − k free squares, certified side s″,
slack δ), plus: a rational γ ∈ [0, 1]; a declared set G_S of **compatible Trump images** —
D4 images g of ẑ whose five simple slots contain S's pin slots (any other image has a pin
coordinate ≥ the slot spacing 1 ≫ rBasin from its counterpart, so its basin box cannot meet
the stratum; the compatible set is a per-class pattern computation, e.g. crowdfam's
`trump-sym4` embedding for k4_08); and for each g ∈ G_S, N zone boxes Ẑ_{g,1} … Ẑ_{g,N} in
(c, t)-space at side s″ around the dilated poses of g·ẑ's N non-pin-matching squares (zone
radius r_z, with the mod-π/2 t-branch for near-upright squares as in `theorem_u.md` §3).

**Certificate claim.** (P2″) for every admissible interior-disjoint core-free pair:
μ₂{Q,Q′} ≥ 1 + β·m₂(Q,Q′) − γ·Σ_{g∈G_S} bz_g(Q,Q′), where bz_g = 1 iff Q and Q′ lie in two
distinct zones of g (two disjoint unit squares can never share a zone: zone diameter ≪ 1 ≤
centre distance). (P1″) W₂ < C(N,2) + β·m − γ·C(N−1,2)·|G_S|.

**Lemma P-B.** In addition to Lemma P's hypotheses, suppose

  m̃ ∈ [ŝ − ρ_B, ŝ]  with  r_z + √2·ρ_B + rounding slop ≤ 3/2000  and  ρ_B ≤ 3/2000
  (the pullback bookkeeping per Lemma B-NO/B.2″: a centre coordinate's zone, centred at the
  s″/ŝ-dilated pose but pulled back by λ = s″/m̃, drifts by |ĉ|·(ŝ − m̃)/ŝ ≤ √2·(ŝ − m̃) —
  the DOMINANT slop, an order above the slack-core shell width; t-coordinates do not scale
  under dilation, so tilt zones pull back undrifted. E.g. r_z = 5·10⁻⁴, ρ_B = 5·10⁻⁴ leaves
  ≥ 2.9·10⁻⁴ slack),

and that the stratum hypothesis is EXACT (skeleton exactly S). Then the conclusion of
Lemma P holds with the discounted claim (P1″)/(P2″).

*Proof.* As Lemma P, with one further count. Fix g ∈ G_S and suppose ALL N free squares of
the stuck packing z lie (after Δ_λ dilation) in distinct zones of g. Pull back: every free
square's (c, t) is within r_z + √2·(ŝ − m̃) + slop ≤ 3/2000 of the corresponding non-pin
square of g·ẑ. The pins: z's pins sit exactly at slots(m̃), g·ẑ's matching simple squares exactly at
slots(ŝ), so each pin coordinate deviates by β_c·(ŝ − m̃) ≤ 3/2000 (slot arithmetic; tilt
coordinates 0 = 0 exactly). Hence ALL 33 coordinates of z lie within 3/2000 of g·ẑ: z is in
the A36 basin box of g·ẑ (D4 × S₁₁-covariant). The basin theorem gives σ(z) ≥ ŝ; but
σ(z) ≤ m̃ ≤ ŝ, so σ(z) = ŝ = m̃ and the equality clause forces z = g·ẑ. Now g·ẑ has FIVE
simple squares (a trump5 image), so its skeleton is not exactly S (|S| = k ≤ 4) —
contradicting the exact-stratum hypothesis. Hence for every g at most N − 1 free squares are
in-zone, so Σ_{pairs} bz_g ≤ C(N−1,2), and the additivity chain reads
W₂ ≥ Σ_{a<b}(1 + βm₂ − γΣ_g bz_g) ≥ C(N,2) + βm − γ·C(N−1,2)·|G_S|, contradicting (P1″). ∎

**Where the monotone→exact bridge enters (stated per the PI's bookkeeping demand).** The
skeleton-contradiction step is the ONLY place, and it is load-bearing: a MONOTONE hypothesis
("z contains the pins of S") would NOT contradict z = g·ẑ — the compatible image g·ẑ
*contains* S's pins by definition of compatibility. The basin row is therefore UNSOUND for
monotone pin quantifiers and sound exactly for the InStratum-exact semantics
(`instratum_bridge.md`, H2/F11 definitional layer) that H10-stuck already uses (CC-2′'s "in
stratum S the non-pin squares are exactly the non-simple ones"). The other imported
equality is `basin`'s equality clause (= A36's certified theorem after the X.1/X.3
transfers), consumed exactly as in `theorem_u.md` §4 — none of A60's open D-node content.

**Shell caveat (why this is a near-ŝ weapon).** For m̃ below the ρ_B-shell the pins' own
slot drift (and the √2-weighted zone drift) exceeds the basin radius: z can sit outside the basin box on its PIN coordinates while all N
free squares are in-zone, the count Σbz ≤ C(N−1,2) loses its justification, and the row must
be DROPPED (γ = 0, plain Lemma P). The composition consumes basin-discounted certificates
only on [ŝ − 3/2000, ŝ] — which is exactly where the ghost lives (the attained side) and
where H10-stuck's consumers (the selection chain at the attained minimum, the uniqueness
chain at ŝ) need it. Deep-window kills stay plain.

**The naive accounting, and what the pilot measured [M].** Against a PURE ghost family (all
N free squares in one image's zones — e.g. the crowdfam k4_08 family, a trump-sym4
perturbation at ~10⁻⁷ ≪ r_z) the floor drops by γ·C(N,2) = 21γ while the threshold rebate
is only γ·C(N−1,2) = 15γ: a naive net gain of 6γ. Measured (A66 γ-pilot, k4_08, contained
adequate catalog with zone-perturbation columns at 3·10⁻⁴ (in-zone) and 3·10⁻³ (out),
all cells converged at Lmax = 1.000000, β = 1,
`attempts/A66-corners4-pair/results/pairlp_k4_08_basin_v2.json`):

  γ = 0: value 27.000 vs threshold 28.000 (margin −1.000, ghost-mass fraction 1.00);
  γ = 0.1: 25.100 vs 26.500 (margin −1.400, ghost fraction 0.70);
  γ = 0.3: 24.031 vs 23.500 (margin +0.531: REFUTED, ghost fraction 0.10).

**The mechanism is real but smaller and non-monotone: the discount gains ≈ 4γ near γ = 0
(0.4 at γ = 0.1), then the fractional dual dodges — it re-weights toward out-of-zone
variants displaced 3·10⁻³ that keep almost the full value (A58's meeter margins ~1.6·10⁻²
≫ the 1.5·10⁻³ basin), the value is convex in γ, and beyond γ ≈ 0.245 the unconditional
rebate wins and the certificate is refuted.** Usable window 0 < γ ≲ 0.245, optimum near
γ ≈ 0.1: the basin row widens k4_08's certifiable margin from β to ≈ β + 0.4 at β = 1 — a
reserve, not a lever; PI's dτ/dε ~ 10² is not observed (the ghost's value is robust to the
whole basin radius). Sound at every γ (Lemma P-B), profitable only in that window. What the
basin can still do beyond pricing is disjunctive conditioning (branch on which square
deviates — A60-style), which is not a row. Credit: PI idea (drain-basin/grain framing);
formulation, accounting and the measurement this file + the A66 pilot. (A first γ-run
reported a "+14γ law / dead at every β" — retracted: its perturbation columns had escaped
the containment filter; the exact audit is `results/containment_audit.json`.)

**Measured pair-tier verdicts (A66 pilot; adequacy criterion: the catalog's single-square
fractional packing reproduces the A65 value — k4_08 τ_f = 7.000000 exact; corners4 7.084 vs
7.2545 after 13 column-generation rounds, residual attributed to the δ = 0 core-free
filter; every catalog audited for exact containment).** k4_08: restricted τ₂(β) = 21 + 6β
EXACTLY at β ∈ {0, 1/4, 1} (integral optimum = the crowdfam ghost family; best exact
contained 7-family in any support has Σm₂ = 6, I = 13 — §4's kill-hope paragraph stands),
i.e. margin −β below the threshold 21 + 7β with ZERO fractional excess on the restricted
instance; product witness certifies τ₂(0) ≥ 21 (emptiness dead, as for every class with a
full N-family). **k4_08's boosted pair kill is LIVE at restricted strength** — the first
protected-class pricing object in the lab whose restricted value sits strictly below its
kill threshold — and the residue is the full-quantifier question (emission + exact
verification, or a richer dual). corners4: β = 0 value brackets τ₂(0) ∈ [14.89, 21.32]
(certified product witness; unconverged cutting-plane upper end, trend 22.20 → 21.53 → 21.32
toward 21), straddling 21 — OPEN; the solver (simplex time on a 17k × 10k LP), not the
formulation, is the binder. **Composed-family answer:** (i) corners4: β = 0 emptiness
(Corollary P0), no basin row (G_S = ∅: every trump5 image has a clear corner); (ii) k4_08
and, by the same ghost mechanism, k4_11 (floors one pair-incidence short): pair rows +
stuckness boost β (margin β) + basin discount γ ≈ 0.1 near ŝ (≈ +0.4); (iii) subcritical
classes (floors 2–3 short per crowdfam): plain pair + β with 2β–3β windows, untested.

## 6.5 [T+M] Lemma W (the margin wall) and the A71 emission verdict (2026-09-02)

A71 ran the emission oracle loop (BRIEF T1) against the frozen verifier. Verdict: **no
full-quantifier certificate emitted; the obstruction is a quantified verification wall**,
recorded here because it binds every future emission attempt in v1 semantics.

**Lemma W (margin wall).** Let η > 0 and let Q_1 … Q_K be unit squares in [0, s″]², each
core-free against class S's slack cores, whose η-cores (concentric squares of side 1 − 2η,
same orientation) are pairwise disjoint. Let D = the set of interior-disjoint pairs among
them and V = |D| + β·Σ_{D} m₂. For any atomic pair measure μ write μ₂^η for collection
counting only atoms whose endpoints are ≥ η deep in their squares. Then
Σ_{(i,j)∈D} μ₂^η{Q_i, Q_j} ≤ W₂ (an η-deep endpoint lies in the pairwise-disjoint η-cores,
so each atom serves at most one pair at margin η). Hence if V ≥ C(N,2) + βm, every
P1′-valid certificate carries ≥ V − W₂ units of its coverage of these rows on atoms less
than η deep — and any `verify_pair.py` run must refine the corresponding pair boxes to the
~η scale before COVERED can fire (certain membership over a box is depth against every
placement in it). *Proof: the two sentences above.* ∎

**Measured instantiation (k4_08, β = 1, s″ = s0, δ = 1/1000, ε_box = 1/833) [M exact].**
K = 11 mixed-tilt squares with pairwise-disjoint 0.15-cores, exact rationals, D = 35,
Σm₂ = 4: V = 39 ≥ 28 (`attempts/A71-pair-emission/results/wall_witness2_k4_08.json`,
pure-Fraction verification of every constraint). So every valid certificate rides ≥ 11
units of family coverage on sub-0.15-margin atoms. Fractional probes (η-shrunk membership
LPs) show the adversary value already ≥ 28-trending at η ≈ 0.03–0.10 but did not converge
in budget (`results/etaprobe_*.json`, honest per-η state). Companion negative: k4_08's
pins block the CHEAPEST wall families — an axis-aligned 4-row of shrunk cores needs the
empty y-band [2.499, 2.378] at s0 (`code/wallwit.py`) — the naive (4 − s″)/6 ≈ 0.02 wall
does not apply; the pins protect at the exploit level too.

**Fixed point and demonstration [M/F].** The A71 loop's empirical fixed point: with
adversarial continuum row-hunting + mock-witness feedback the covering LP climbs from the
restricted 27 to W₂ ≈ 30.0 ≥ 28 (P1′ violated) — the wall priced on the covering side; the
rescaled P1′-valid candidate was judged by the FROZEN verifier end to end: FAIL at depth 12
with concrete deficit witnesses (`attempts/A71-pair-emission/certs/pair_k4_08_s0_b1_v1s.report.json`).
corners4 carries the same wall in β = 0 form: exact witness K = 9, D = 22 ≥ 21 at η = 0.15
(`results/wall_witness2_k4_13.json`) — though with the smallest shortfall (1 unit), making
corners4 the natural v2 pilot. **A71 T3 broke the solver wall [M]**: inclusion-maximal
point reduction (265k raw → 1375 maximal patterns) + IPM-no-crossover + row purging turn
A66's stalled 17k×10k simplex into ~8-min converged cut loops; the support-catalog β = 0
value CONVERGED at 20.528144 (viol 0/0, Lmax = 1.000000037) with an exact certified lower
bound 4103377/200000 = 20.516885 (exact Lmax 62499/62500 on cell-representative points,
support exact-audited; completeness caveat recorded in
`attempts/A71-pair-emission/results/k4_13_cert_lower.json`). Dual pricing exposed the
A66 support catalog as NOT pair-adequate (40% of the 1.74M enriched pair columns
under-priced), so the run GROWS the catalog by pricing: grow-0 = 20.528144 converged,
grow-1 (304 placements / 20.4k pairs) = 20.542 at budget (Lmax 1.12), further grows in
flight at session close — every measurement ≥ 0.45 BELOW the line 21 and the value moves
by ~1e-2 per grow: A66's bracket [14.89, 21.32] is effectively [20.52, ~20.6], and the
Corollary P0 emptiness route for corners4 is OPEN at restricted strength (not refuted;
final adequacy-clean value = the A71 T3 artifact set, `results/pairlp_k4_13_a71cg.json`).

**Cost identity [M].** Frozen-verifier throughput at realistic atom counts (3000 atoms,
exact Fractions): 57 pair-boxes/s (17.5 ms/node; A71 `results/calib_verify.json`); the
A71 float mock replays the identical discharge rules at 72k nodes/s (1250×). Leaf-count
geometry ~0.8·((2.877/2r_c)²/(2r_t))²/2 at cell radii (r_c, r_t) ≈ (m/4, m/8) for margin m:
all-margins-0.15 (ruled out by Lemma W) ≈ 6e8 leaves ≈ 125 days single-core; 0.10 ≈ 7e9 ≈ 4 y;
0.05 ≈ 4.5e11 ≈ 250 y — v1 verification is decades-to-centuries at the actually-forced margins. The wall is the verifier's uniform
certain-membership COVERED discharge (spec §5's warning, now priced), NOT the certificate's
existence: restricted τ₂ = 27 < 28 with zero fractional excess on every audited catalog.

**Consequences.** (i) v1 emission for the k4-tier is CLOSED as infeasible-at-scale; the
constructive residue is a v2 design: margin-aware splitting, placement-dependent membership
accounting, a compiled second implementation (wanted for the TCB anyway), and/or an
analytic coverage clause — spec revision to be VERSIONED (pair-certificate-v2), never an
edit of v1. (ii) The measure-existence question (a proof that a W₂ < 28 measure exists,
not an atom list) is the open mathematical half [C]. (iii) Canary: Lemma W is
adversary-side (a lower bound on W₂) — it strengthens nothing against trump5; the A71
run-level canary re-verified the dilated 60-digit Trump family as an exact death witness
under the A71 parameters (min SAT gap = λ − 1 = 1.06e-7 exactly, Σm₂ = 6;
`results/canary_trump.json`).

## 6.6 [T+M] pair-certificate v2, Lemma W′, and the corners4 depth-profile wall (A73, 2026-09-02)

**v2 exists** (`docs/specs/pair_certificate_v2.md`, claim IDENTICAL to v1 — every
consumption path and the canary theorem carry over verbatim): free rational-cut
margin-aware splitting (Lemma S), EXACT quadratic-sign-test membership/exemption
predicates (Lemmas M/E/Q — iff, no interval slop), the analytic handoff clause
COVERED-F (Lemma F, failing-set form), VACUOUS-CONTAIN (the container-boundary sliver
the v1 clip provably cannot discharge), and DEFICIENT-EARLY (exact rational
counterexample rows). Two implementations from the spec: the A73 reference
(`attempts/A73-pair-v2/code/verify_pair2.py`; selftest 0 violations, toys + corruption
gates) and a clean-room compiled Rust build (`code/verify_pair2_rs/`, selftest-clean,
20k–440k nodes/s single-thread by regime, ≥100k with jobs) — checklist C3 for the pair
family. **The v1 THROUGHPUT wall is broken** [M]: the first full-quantifier
atom-bearing (P2′) PASSes exist — synthetic grid-pair certificates at s = 3 verified
end-to-end (5866 nodes at atom margin 0.146; 1098 nodes at margin 0.076; the SMALLER
margin cost FEWER nodes) — and the measured v2 cost law tracks the measure's FRONTIER
STRUCTURE (where coverage hands off between witnesses), not (1/margin)^6.

**Lemma W′ (fractional margin law; Lemma W's quantified successor).** Let z* be any
η-feasible adversary (load of η-deep collection ≤ 1 at every atom position), of value
V = Σ z*(1 + βm₂). Then every P1′-valid certificate satisfies
Σ_i w_i·S_i^η(z*) ≥ V − W₂ > V − (C(N,2) + βm), where S_i^η = the z*-mass of rows
collecting atom i sharply but not η-deep. *Proof:* V ≤ Σ z*μ₂ = Σ_i w_i L_i,
L_i ≤ 1 + S_i^η by η-feasibility at atom i's own position. ∎ The τ₂^η curve therefore
prices the DEPTH PROFILE of every valid certificate.

**Measured corners4 τ₂^η curve (catalog-restricted, A73 `pairlp413e.py` = A71 rig +
η-deep membership + η-shrunk arrangement; brackets = [feasible-scaled, relaxation]):**
sharp η→0: 20.528 CONVERGED (A71); η = 0.01: [18.01, 21.38] unconverged, still
descending ~0.008/round at the IPM wall (plausible asymptote 21.1–21.3, i.e. ABOVE the
line); η = 0.02: [17.77, 22.30]; η = 0.05: [18.31, 26.24]; η = 0.1: scaled ≥ ~34
(relaxation plateau 57.000) — DEAD decisively, and by Lemma W′ ≥ ~13 weighted units of
sub-0.1-margin service are FORCED in every valid corners4 certificate. **The fractional
wall crosses 21 at η* somewhere in (~0.006, ~0.05) — far below Lemma W's integral
0.12–0.15.** Uniform-η emission is dead on that whole range while sharp 20.528 stays
open: any valid corners4 certificate is a MIXED-DEPTH measure (deep coverage of generic
rows + the forced shallow units at the exploit families' own scale), and its
verification cost concentrates near the exploit manifolds — exactly what margin-aware
splitting + hint trees localize.

**The tangency trap [M].** LP-optimal covering primals put atoms ON the membership
boundaries of the squares they serve (arrangement-cell representatives; margins ~1e-6):
the A71 seed is emission-side anti-verifiable — v2's first corners4 survey measured
COVERED firing ZERO times on it. Emitters must solve at η-deep semantics or deepen
post-hoc; η-deep coverage implies true coverage (conservative).

**Status of the corners4 pilot (honest).** No corners4 certificate emitted: the residue
is no longer verifier throughput but the EMISSION problem — produce a mixed-depth,
weight-CONSOLIDATED measure (W₂ < 21 with the Lemma W′-forced shallow structure), for
which the uniform-η LP is only a sufficient-side probe (and its η-runs hit genuine IPM
scaling walls: η-shrunk arrangements yield ~2× denser rows, nnz 4–6M, rounds 30–900 s,
all runs at η ∈ {0.01, 0.02, 0.05} stopped unconverged straddling 21). Constructive
successor, priced: a deepening/consolidation pass on the sharp primal (move each atom to
maximize min serving depth subject to tight rows, consolidate onto a coarse net), the
survey loop (DEFICIENT-EARLY rows) against the compiled verifier, and hint-tree
emission. Canary [M]: the dilated Trump family re-verified SAFE under A73 parameters
(min pair SAT gap = λ − 1 = 1.06e-7 exactly, Σm₂ = 6); all η-probes are
adversary-side. P0 consumption path unchanged and restated in
`attempts/A73-pair-v2/notes/findings.md`.

## 6.7 [M+T] Mixed-depth emission: the first sub-threshold corners4 measures, hint trees, and Lemma W″ (A74, 2026-09-02)

**Machinery** (`attempts/A74-mixed-depth/code/`, emission-side only; the frozen v2
verifiers are untouched and every claim below about the continuum is theirs). The (P2′)
point-pattern rows are offered to the A71/A73 adversary LP at SEVERAL depth levels
η₁ > … > η_L at once (each level's own arrangement of the η-shrunk squares; row (c,d,l)
counts z_ij only when both endpoints are η_l-deep), priced into the adversary as
load ≤ rhs_l = 1 + μ·(η_max − η_l)/(η_max − η_min). By LP duality the row duals y then
minimise the depth-priced covering cost Σ y_r·rhs_r subject to Aᵀy ≥ 1 over EVERY catalog
pair (all pairs are columns, so any HiGHS-optimal dual is a restricted covering measure —
provided no column sits at its bound, which is checked), and the certificate gate is the
UNPRICED mass W₂ = Σ y ≤ priced value. Consolidation drops rows below a rising dual-weight
floor and re-solves, accepted while W₂ < guard. Dual seeding (the binding point pairs of
earlier runs re-membershipped at every level) replaces ~15 cut rounds; the loop solves are
IPM + crossover (exact duals each round; IPM-only iterates time out without a feasible
point above ~10 M nnz, and simplex cold-starts do not finish). Canary per emission SAFE
(`notes/ledger.md`: min gap = λ − 1 = 1.06e-7, Σm₂ = 6).

**[M] Sub-threshold measures exist (restricted).** On the 404-placement A71 colgen catalog
(+ control columns):

| run | menu η | μ | exact W₂ | atoms | mass at 0.05 / 0.02 / 0.008 / 0.002 / 0.0005 |
|---|---|---|---|---|---|
| md5 | 0.05, 0.02, 0.008, 0.002 | 0.01 | **20.98857** | 461 | 0.87 / 7.29 / 7.55 / 5.28 / — |
| md7 | + 0.0005 | 0.01 | **20.95955** | 353 | 0.59 / 6.98 / 7.41 / 5.10 / 0.87 |
| md8 | md7 menu, catalog grown by 65 exact-counterexample placements (469) | 0.01 | **20.95828** | 363 | 0.61 / 6.81 / 7.47 / 5.23 / 0.84 |

Every atom is ≥ its level's η deep in every square its row serves (the A73 tangency trap
is closed by construction; positions rounded to 1e-6 ≪ η). Certificates:
`attempts/A74-mixed-depth/certs/pair_k4_13_s0_b0_md{5,7,8}.json` (+ `_hinted`).

**Lemma W″ (the measured mixed-depth law, restricted form).** Let V(η_min, μ) be the
converged value of the depth-priced adversary LP on a catalog S with menu floor η_min.
By weak duality every covering of S's pairs whose atoms are all ≥ η_min-deep in the
squares they serve has W₂ ≥ V(η_min, μ)/(1 + μ); and the measured values pin the
restricted optimum to the threshold from below: slack 21 − W₂ = 0.011 at floor 0.002,
0.040 at floor 0.0005, against 0.47 at the sharp limit (A71: 20.528 converged). The
forced profile is not "bulk deep + thin shallow stratum": ~70 % of the mass sits at
0.008–0.02, ~25 % at 0.002, 3–4 % at 0.05 — the bulk lives just below the A73 bracket
η* ∈ (0.006, 0.05), as Lemma W′ predicts. Depth and consolidation compete for the same
slack: at μ = 0.3 the dual mass rises ABOVE 21 while rows are added (21.31 → 21.55, run
killed), and consolidation is accepted down to 470 rows (20.9886) and rejected at the
next floor (398 rows, 21.0026) for md5; 355 → 271 rows: 20.9595 → 21.0517 for md7.
Catalog growth by exact counterexample rows costs essentially nothing (md7 → md8:
−0.001 with 65 new placements), so the restricted optimum is not what blocks a
certificate; the verification residue is.

**[M] Verification residue and hint trees.** md5 unhinted (Rust verify_pair2 `--jobs 8`,
depth 34, 2 M nodes, survey): FAIL by cap only — 0 definitive rows, 300 cap witnesses at
depth 34 with certain mass median 0.845 (min 0.68), the verifier's own splitter having
driven factor A to widths 2e-4–7e-4 while factor B's tilt interval stayed UNSPLIT in all
300: the residue is tilt uncertainty in the un-split factor, not the atom margins.
`code/hinttree.py` (spec §4 hint trees: emitter-side float B&B, cut = max-min lookahead
over the six midpoint cuts, COVERED leaves where float-certain mass ≥ 1, empty nodes for
verifier fallback; verifier untouched, every leaf re-proved) changes the search shape:
30 nodes/root → cap witnesses at 99.8 % certain mass; 3000 nodes/root (237 k hint nodes,
5.9 k leaves) → COVERED 106.8 k vs 98.6 k, and DEFICIENT-EARLY fires 7317× — exact
rational counterexample pairs (collecting 0.948–0.992) exist in the continuum between
catalog placements, which the unhinted search never probed. Those rows are the survey
loop's row source (md8 is the first grown-catalog re-solve). No corners4 PASS yet: the
honest state is a working mixed-depth emission loop with exact holes being harvested,
not a certificate.

**P0 consumption and window pricing (unchanged in form, now priced per side).** A v2 PASS
of any of these certificates at s₀ with δ = 1/1000 slack cores consumes verbatim as in
§6.6 / A73 (`Corollary P0`; ε_box = 1/833 = 3δ/(5/2 − δ) exactly): emptiness of every
packing containing the corner pins on (s₀/(1 + δ/(5/2)), s₀), i.e. the corners4 leaf of
C.K4TIER on that shell; full-window coverage is the slack-core slab grid (~38 sides at
δ = 1e-3 over [3.82, s₀]). Measured per-side loop cost at this scale: LP 25–40 min
(IPM+crossover rounds, dual-seeded), hint build ~10 min, hinted 1–2 M-node survey
15–25 min — ≈ 1 h per loop iteration, iterations-to-convergence and the certification
run itself unpriced (not reached).

## 7 What remains open for a certified pair kill (the honest ledger)

* [M, pilot] the fractional pair-LP verdict per class — A66 measures k4_08 (boosted) and
  corners4 (β = 0 and boosted) at restricted-LP strength; a restricted value above threshold
  refutes the route for that class (restricted rows lower-bound every certificate's W₂).
  A71 (2026-09-02): k4_11 = 21 + 6β and k4_03 = 21 + 4β EXACTLY (margin −β, zero fractional
  excess, adequacy τ_f = 7.000000 per class) — the whole one-short critical tier shares the
  k4_08 signature; stuckness-row soundness now standalone in `stuck_rows.md` (SR-1/SR-2),
  with exact P-B image sets G_S = {id, diag}/{id}/{diag}/∅ for k4_08/k4_11/k4_03/corners4.
* [S] the verifier: `verify_pair.py` is NEW trusted code (C3-scale trust investment; the
  clean-room spec is `docs/specs/pair_certificate_v1.md` §3). Not in the TCB until a second
  implementation or a Lean port exists.
* [C] window form: the slack-core grid obligation, shared with every fixed-side kill (B.4),
  plus the ε_box widening per slab.
* [C] the k ≤ 3 tier: Lemma P applies verbatim (their boxes and censuses are in
  h10_boxspec.json); per-class LP verdicts not yet priced.
