# The upper bound AT ŝ: route decision and the attainment lemma (A63, 2026-09-01)

Target: A62 finding F2 / Lean axioms `zhat`, `trump_packs_at_shat` — the equality claim's UB
half. A62 named two routes: (a) A22's Krawczyk existence + feasibility; (b) closedness of
{s : Fits 11 s} plus a certified sequence of sides ↓ ŝ. This file executes the cheap half —
the attainment/closedness lemma and the EXACT check of what route (b) can and cannot deliver —
and reduces route (a) to one precisely-localised algebraic gap with two closure specs.
Labels: [T] proved, [M] computed exact, [F] finding, [C] open.

## 1 [T] Lemma A (the fits-ray): {s : Fits 11 s} is a closed ray [s(11), ∞), and the infimum
is attained

(i) *Monotone.* If 11 unit squares pack in [0, s]² and s ≤ s′ then the same squares pack in
[0, s′]² (container inclusion). So {s : Fits} is up-closed.

(ii) *Closed.* Let s_n → s∞ with Fits(s_n); WLOG s_n ≤ s∞ + 1 =: S. Represent each packing by
its configuration z_n ∈ K := ([0, S]² × [0, 1])¹¹ (centres, t = tan(θ/2); the `parametrize`
lemma — every unit square in the container is PSq.set of some (c, t), elementary). K is
compact; pass to a convergent subsequence z_n → z∞. Each defining condition survives the limit:
* containment: corner coordinates are continuous in (c, t) and closed inequalities pass to
  limits (s_n → s∞ on the right-hand side);
* pairwise interior-disjointness: overlapping interiors is an OPEN condition on configuration
  pairs (if int Q ∩ int Q′ ∋ x, then squares within ε of (Q, Q′) still overlap near x), so its
  complement is closed;
* unit size and squareness: built into the parametrisation.
So z∞ is a packing at side s∞: Fits(s∞). ∎

(iii) With (i)+(ii): {s : Fits} = [m, ∞) with m = min = sInf = s(11). This is D1 restated on
the set level; it also discharges the PROSE of the Lean axiom `attained` (formalisation of (ii)
is the known cost: closedness of `Fits` — A62 note on `attained` unchanged) and isolates
`parametrize` as its only geometric input.

**Consequence (the honest reduction).** s(11) ≤ s″ for every certified side s″; and
s(11) = the side of ANY feasible configuration that attains the minimum. The UB-at-ŝ question
is EXACTLY: "exhibit a packing at side ŝ" — no compactness argument can manufacture one from
sides > ŝ alone, because nothing forces the minimum DOWN to ŝ except an actual packing there
(the lower-bound machinery only forces it UP to ≥ ŝ).

## 2 [T/F] Route (b) checked exactly: REFUTED as a finite certificate route

* **Single certificate + scaling [F].** Scaling a packing changes the squares' side with the
  container: 11 unit squares in [0, σ]² ⟺ 11 λ-side squares in [0, λσ]². No λ ≠ 1 produces
  UNIT squares at a smaller side; the certified `trump11_tight` packing at
  s₁ = 3.877083591023 yields Fits(s) for s ≥ s₁ (Lemma A(i)) and NOTHING below s₁. The
  "scaling argument" the brief asked to check does not exist.
* **Any finite set of fixed-side certificates.** `checkPacking` requires strictly positive
  margins (A62 F2), so every certified side is a rational STRICTLY above ŝ; a finite set has a
  minimum s_min > ŝ and delivers only s(11) ≤ s_min. A sequence ↓ ŝ needs infinitely many
  certificates — not a finite proof object.
* **Parametric UB certificate (a rational curve of packings z(τ), σ(z(τ)) ↓ ŝ).** On each
  smooth piece σ(z(τ)) is a polynomial in τ with rational coefficients; its limit as τ → 0⁺ is
  its value at 0, a RATIONAL number ≠ ŝ (ŝ is a degree-8 algebraic irrational, T1 certificate).
  So no rational-data curve reaches ŝ in the limit; curve data in ℚ(ŝ) is exactly route (c)
  below, with the same algebraic cost. **Route (b) is closed off, not merely unexecuted.**

## 3 Route (a): what A22 already proves, and the ONE remaining gap

A22 (`attempts/A22-local-rigidity/`, certificate + standalone `recheck.py`) proves, modulo the
mpmath.iv trust item (TCB T3):

* existence + uniqueness of the contact solution ẑ in the box N = box(z0, 5e-4), with
  ‖ẑ − z0‖∞ ≤ 1e-50 (Krawczyk);
* **feasibility: ẑ IS a packing at its own side** (A22 §4 — exact flush/coincidence arguments
  plus interval SAT with min margins 0.0249/0.549);
* strict local optimality: every feasible z ∈ N has s(z) ≥ ŝ_A22 := s(ẑ), equality iff z = ẑ.

So **Fits(ŝ_A22) holds — the UB at the INTRINSIC value ŝ_A22 is already certified**, and with
Lemma A and the lower-bound axioms the composed equality is s(11) = ŝ_A22. What is NOT proved
is the statement-identity ŝ_A22 = ŝ_octic (the octic root the theorem names — A22 §7 gap 2:
PSLQ-found, enclosure-consistent, never derived).

**[M] How tightly the two are now tied** (using T1's isolation certificate):
* z0's s-coordinate = 3.87708359002281417730789706… lies in (a, b) = (3.877083, 3.877084)
  with ≥ 4.1e-7 clearance on both sides; ‖ŝ_A22 − z0_s‖ ≤ 1e-50, so ŝ_A22 ∈ (a, b).
* T1: the octic has exactly ONE root ŝ_octic in (a, b) (and exactly two real roots overall).
* A22 encloses octic(ŝ_A22) ∈ ±3.1e-45; T1's Taylor certificate gives octic′ ≥ 152.37 on
  [a, ∞); by the mean value theorem |ŝ_A22 − ŝ_octic| ≤ 3.1e-45 / 152.37 ≤ 2.1e-47.
* **Equality remains open [C]**: intervals can never prove it; it is an algebraic identity.

## 4 [C] Closure specs for the identification (choose either; both finite)

* **(c-alg) Exact number-field verification.** Verify that an exact algebraic point solves
  A22's 38-row curated system, with the side coordinate a root of the octic. Obstacle recorded
  by A53 L4: at least one coordinate of ẑ (the ε-off square's cy) has minimal polynomial of
  degree 7; since 7 ∤ 8, the coordinate field is NOT ℚ(ŝ_octic) — the verification field is a
  compositum of degree up to 56. Spec: a ~200-line exact checker doing arithmetic in
  ℚ[x]/(m(x)) for the compositum's primitive element (or componentwise in the two fields with
  resultant-certified compatibility), all sign gates via T1-style Sturm isolation + interval
  refinement — same TCB profile as `verify_sturm.py`, stdlib rationals only. Input data (the
  exact coordinates as polynomials in the primitive element) must first be RECOVERED (PSLQ/LLL
  from the 60-digit data, then verified exactly — recovery is untrusted search, verification is
  the certificate). This also upgrades A22 §7 gap 2 for good.
* **(a2-lean) t-reparametrised Krawczyk replay in Lean** (checklist F6, A28 §4) discharges the
  mpmath.iv trust item and formalises existence+feasibility, but does NOT by itself tie ŝ_A22
  to the octic; pair it with (c-alg) for the full statement, or with (S3-fallback) below.
* **(S3-fallback) Restate.** Publish with ŝ := ŝ_A22 (intrinsically defined by A22's
  certificate: "the side of the unique contact solution in N") and the octic as a certified
  remark ("agrees with the second root of […] to within 2.1e-47"). Checklist S3 explicitly
  sanctions this shape. Zero additional mathematics; the Lean `shat` would then be defined
  from the (replayed) Krawczyk certificate instead of the octic.

## 5 Verdict for the composition (state of `zhat` / `trump_packs_at_shat`)

* With ŝ read as ŝ_octic (current `TopLevel.lean`): the axioms remain OPEN; the discharge is
  (a2-lean) + (c-alg). Route (b) cannot discharge them and should be struck from the route
  list.
* With ŝ read as ŝ_A22 (fallback restatement): `trump_packs_at_shat` is certified TODAY
  (Python-interval TCB), and the honest composed theorem is s(11) = ŝ_A22 conditional on the
  lower-bound axioms, with |s(11) − ŝ_octic| ≤ 2.1e-47 unconditionally-on-the-same-axioms.
* Interval-only honest form (no A22 feasibility accepted): ŝ ≤ s(11) ≤ 3.877083591023,
  unchanged from A62.
