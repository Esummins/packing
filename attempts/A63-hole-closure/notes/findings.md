# A63 findings — the hole-closure pass over A62's F-list (2026-09-01)

Executed against the A62 axiom roster at commit `c9980bf`+. Numbered N1–N7; severity tags as
in A62 (HIGH/MED/LOW). Artefact pointers at the end of each item.

## N1 — shat_spec DISCHARGED; the octic is unusually kind. [closes F7/S3]
The Trump octic has exactly TWO real roots (Sturm, exact; the other in (−2, −1)), so the root
in [3.877083, 3.877084] is "the second real root" with no further bookkeeping. Better: every
Taylor coefficient of the octic at a = 3877083/1000000 above degree 0 is POSITIVE, so the
octic is strictly increasing on [a, ∞) by pure algebra — the Lean uniqueness proof needs no
calculus, no Sturm chain, and no interval arithmetic (IVT + `pow_le_pow_left₀`). `shat` is now
a Lean DEFINITION and `shat_spec` a theorem depending only on `propext, Classical.choice,
Quot.sound`. Certificate `certs/octic_root_isolation.json`; checker `certs/verify_sturm.py`
(stdlib fractions only; 5 corruption gates fail loudly).

## N2 [HIGH, headline] — Lemma B closes S4/F9, and its corpus margin SHARPENS F6: an s₀-only
certificate instantiates the kill axiom at NO side of the window.
The λ-dilation bridge (centres ×λ, sizes fixed) makes an interior-disjoint packing strictly
disjoint (SAT gap ≥ λ−1) while pin squares track their slots to within (λ−1)·5/2 — Lemma B +
Corollary B′ in `docs/proofs/closed_disjoint_bridge.md`. BUT the deployed kill certificates
all use ε-fat cores (a = 16383999967232/32768001953125 ≈ 1/2 − 3.1e-8, tm = 2⁻²⁵), whose
exact containment margin is ρ ≈ 1.0000009e-9. So a kill certified at side s″ binds packings
only at sides m ∈ [s″/(1 + ρ/(5/2)), s″) — a 4e-10-relative shell. Consequences:
* parametric (window) certificates + dense rationals ⇒ `stratum_kill` instances at EVERY
  m ∈ [3.82, ŝ] for the covered classes — the S4 repair is now a written lemma, not folklore;
* an s₀-only certificate (A57 k5_11/k5_16 trees, A60 zone-tree leaves, A61 stragglers until
  their parametric forms land) reaches NOTHING in [3.82, ŝ] (the ŝ→s₀ gap is 1.06e-7
  relative ≫ 4e-10). "s₀-only" in the ledgers overstates usability.
* A56's refutation of monotone transfer stands; Lemma B is its quantified boundary.
* NEW ROUTE (B.4, the slack-core grid): re-emitting certificates with core half-side
  1/2 − 1e-3 widens the shell to ~4e-4 relative, so ~37 fixed-side certificates cover the
  whole window — an alternative to 4-D parametric verification, and the only visible window
  route for the A57/A60 tree compositions short of re-architecting them.

## N3 [HIGH] — F3 re-diagnosed: `unique_transfer` as stated is a corollary of census
exhaustiveness; the uniqueness load actually sits in `stratum_kill`'s quantifier. [T3]
A53 L3 gives every packing a unique Young skeleton, so every packing at ŝ IS in a stratum
(D4-normalise; f = g, e induced). The gap A62 saw is real but lives downstream:
`s_eleven_unique` feeds an ARBITRARY packing to `stratum_kill`, whose ∀-packings strength at
the K1-protected classes cannot come from certificates (K1) and will not come from A58's
K*-maximal machinery. Non-circular architecture, on file at drain-lemma rigor
(`docs/proofs/unique_transfer.md`): CC-2 teleport chain (no corridors ⇒ the H1 degenerate
slide cases evaporate) to a teleport-stuck packing → stuck-kills (H10 re-based to
**H10-stuck**, which A58's mechanism already supports) → residual + basin → **collapse back
via Theorem U (one-square rigidity of ẑ)** — the ONE new leaf, with an executable
11-certificate spec (re-insertion certificates: rational side in T1's isolating interval,
10 shrunk cores, budget 1, `nofams` zone inside the basin box; the only load-bearing use of
`nofams` in the composition). Obligations: U-O1 (the 11 certs), U-O2 (= H10-stuck),
U-O3 (k5_11/16 window instantiation), U-O4 (existing D/E nodes).

## N4 [HIGH] — F2 route decided: (b) is refuted, not merely unexecuted; (a)'s residue is one
algebraic identity, now pinned to 2.1e-47. [T4]
Scaling cannot produce unit squares at a smaller side; finite certificate sets have minimum
side > ŝ; rational parametric curves have rational σ-limits ≠ ŝ (ŝ is a degree-8 irrational —
T1). So the Fits-closedness route delivers only the attainment lemma (written:
`attainment_ub.md` §1, also the prose discharge of `attained`). A22's certificate ALREADY
proves Fits(ŝ_A22) for the intrinsic contact-solution side; the whole remaining F2 content is
ŝ_A22 = ŝ_octic. Using T1's Taylor bound (octic′ ≥ 152.37 on [a, ∞)) against A22's octic
enclosure (±3.1e-45): |ŝ_A22 − ŝ_octic| ≤ 2.1e-47. Closure specs: exact number-field
verification — NOTE the obstacle: A53 L4 records a coordinate with a degree-7 minimal
polynomial, and 7 ∤ 8, so the verification field is a compositum of degree up to 56, not
ℚ(ŝ) — or the S3-fallback restatement (ŝ := ŝ_A22, octic as a certified remark).

## N5 [MED] — rBasin = 3/2000, and the binding constraint is NOT the tilt transfer. [T5/F5]
The naive transfer h/2 = 1.85e-3 is unsound for the `basin` axiom as stated: its ∀-s clause
covers sides below A36's s-slab, and closing it needs the corner-perturbation bound
r(1+√2) ≤ h — which binds first. rBasin = 3/2000 satisfies both exactly
((3/2000)(24143/10000) = 3.62145e-3 < 37/10000). Now a Lean definition; A60's landing radius
4.45e-4 = 0.30 × rBasin. `docs/proofs/theta_t_transfer.md`.

## N6 [MED] — the monotone→exact bridge and K1 now have a proofs home. [T5/F4]
`docs/proofs/instratum_bridge.md`: K1 both directions (E.1), Lemma M→E (E.2 — reflexivity +
D4 bookkeeping + Lemma B), exact coverage table (E.3). The K1-protected residue is H10 by
design, not a missing lemma.

## N7 [LOW] — lb_382's own S4 gap closed in passing.
The measure-certificate bridge also quantifies over disjoint families; a packing at m < 3.82
dilates (any λ) to a strictly-disjoint family at 191/50 with no cores to track (Lemma B,
r = 0 case). One line, previously unwritten (`closed_disjoint_bridge.md` B.2 last bullet).

## Ledger effect
Axioms: 16 declared → 13 (`shat`, `shat_spec`, `rBasin` discharged); `#print axioms` on all
three theorems clean (no sorryAx; shat_spec = propext/choice/Quot.sound only). Depgraph
(A63 copy at `results/depgraph.json`): A.S3 → certificate+verifier; B.EXACT, E.COORD →
proved-prose; +A.SBRIDGE (proved-prose), +A.THMU (open); open nodes 14 → 13, with A.UBshat
and A.UNIQ still open but route-decided with named residues.

## N8 [MED] — A60 feedback round: Lemma B-NO (nofams-aware clause) added; grid pricing held.
A60's ledger (notes/ledger.md) surfaced that its four confinement PASSes — the only viable
route for trump5's outer triple — carry a NO-family, which Lemma B as first written excluded.
Added B.2″ **Lemma B-NO**: with nonempty nofams the bridged claim is occupancy, and it
transfers to side m = s″/λ as "some non-owner square has (c, t) ∈ λ⁻¹F_k" — no side condition
on core owners (the pricing dichotomy never touches them); the zone contracts toward the
origin, so downstream consumers must hypothesise the OUTWARD widening F^{+ε},
ε = (λ_max−1)·max-coordinate (1.6e-9 in the fat-pin shell; ≈1.6e-3 under the slack-core
grid). Also B.2′: the general owner-frame (H) criterion ((λ−1)|c_o|₂ < ρ_j), codifying A60's
recorded false alarm (B′'s axis-parallel width formula misapplied to tilted cores gives
ρ ≈ −0.204; the correct margin is 1/2 − a > 0). Confirmations banked: ρ = 1.0000009e-9
independently reproduced on A60's 49 leaves; the T5 θ↔t lemma caught A60's basin-discharge
test (θ-radians vs wrong radius → corrected to contain_t vs 3/2000, square-1 ladder passes at
1.24× — thin; squares 2–3 to be re-checked). B.4's ×37 grid price is HELD: A60's measured law
is η ≤ −1 (the 0.5-slack regime failed on trump5); one δ = 1e-3 re-emission test is running.
