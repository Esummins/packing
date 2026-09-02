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

## 6 What remains open for a certified pair kill (the honest ledger)

* [M, pilot] the fractional pair-LP verdict per class — A66 measures k4_08 (boosted) and
  corners4 (β = 0 and boosted) at restricted-LP strength; a restricted value above threshold
  refutes the route for that class (restricted rows lower-bound every certificate's W₂).
* [S] the verifier: `verify_pair.py` is NEW trusted code (C3-scale trust investment; the
  clean-room spec is `docs/specs/pair_certificate_v1.md` §3). Not in the TCB until a second
  implementation or a Lean port exists.
* [C] window form: the slack-core grid obligation, shared with every fixed-side kill (B.4),
  plus the ε_box widening per slab.
* [C] the k ≤ 3 tier: Lemma P applies verbatim (their boxes and censuses are in
  h10_boxspec.json); per-class LP verdicts not yet priced.
