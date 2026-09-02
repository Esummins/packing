# A73 — pair-certificate v2 + corners4 pilot: findings (Fable lead, 2026-09-02)

Labels: [T] proved, [M] measured/computed exact, [F] float evidence, [C] open.
Successor to A71 (Lemma W / verification wall). BRIEF: attempts/A73-pair-v2/BRIEF.md.
STATUS: IN PROGRESS — updated as runs land.

## T1 — spec v2 [T]

docs/specs/pair_certificate_v2.md written (versioned; v1 untouched, sha d9b7a24a stays
frozen). The claim (P1')/(P2') is IDENTICAL to v1 — every consumption path (P0
emptiness -> stratum_kill; boosted stuckness kills) applies to a v2 PASS unchanged, and
the canary theorem binds v2 identically (v2 strengthens the verifier's reach, not the
row semantics). New decision machinery, each clause with its own lemma at drain-v3
rigor:

* Lemma S (exhaustive disjunction): splitting is free — any of the 6 dims, any rational
  interior cut, emitter hints allowed; soundness independent of the heuristic.
* Lemma Q (exact quadratic sign test on an interval) — the arithmetic workhorse.
* Lemma M (exact membership, IFF): certain membership of a point over a factor box
  reduces to 4 pinned quadratic tests (corner reduction via sign-fixedness of C, S,
  1-t^2, t on t in [0,1]). Kills the v1 outward-interval slop (~2.5x/dim): COVERED now
  fires at the atom's TRUE worst-case margin.
* Lemma E (exact core exemption, IFF): 8 pinned quadratics, same machinery.
* Lemma F (COVERED-F handoff): the analytic one-step discharge — two witnesses each
  certain but for ONE designated constraint; if the pinned slack SUM is >= 0 over the
  box (corner-enumerated, exact), every point satisfies one of them: min(w_i,w_j)
  collected across the frontier without splitting to dust. MEM/EXC mixed pairs allowed
  (exempt points owe nothing). This is the monotone/quasiconcave one-step discharge of
  the BRIEF (A64 wT_ge_min style; closed-form quadratics instead of A70
  alternating-Taylor).
* DEFICIENT-EARLY (optional): exact rational probe pair (admissible, core-free,
  interior-disjoint — all decidable exactly at rational t) with exactly-computed
  collected mass < 1 + beta*m2 refutes the certificate on the spot (kind "definitive").
  Only accelerates FAIL; the emission loop's row source.

## T2 — implementations

* Reference attempts/A73-pair-v2/code/verify_pair2.py (Fable, from the spec): selftest
  0 violations (Q/M/E/NONDISJOINT fuzz, 2500 draws each); toy corpus verdicts MATCH v1
  (s199 PASS depth 40; s201 FAIL; smoke FAIL at depth 26); corruption gates OK
  (float-literal exit 2, bad total exit 2, P1' violation exit 2, atom-delete stays
  FAIL, negative weight exit 2). Throughput ~1.3-6.5k nodes/s (float fail-fast
  pre-screen + exact confirmation; 20-100x the frozen v1's 57/s before compilation).
  One implementation bug caught by the toy corpus: the VACUOUS clip must be re-applied
  at every CHILD construction (v1 sect 3.1 "applied at box construction"), not only at
  roots — the s199 PASS is unreachable without it. Spec wording already correct.
* Compiled (Opus chore, clean-room from spec + v1 spec + toy corpus only): Rust
  toolchain was absent on this machine (no rustc, no MSVC, no gcc) — installed scoop
  rust-gnu 1.98.0 (user-level). Build in flight; the chore's pre-implementation spec
  review found no soundness errors, two wording ambiguities resolved (Lemma M pinning
  prose, COVERED-F same-factor corner-sum reading — spec updated in place).

## T3 — corners4 pilot [in progress]

* Canary per run: dilated 60-digit Trump family re-verified SAFE under A73 parameters
  (delta = 1/1000, eps_box = 1/833): min pair SAT gap = lambda - 1 = 1.06e-7 exactly,
  sum m2 = 6 (results/canary_trump.json).
* Seed certificate assembled (certs/pair_k4_13_s0_b0_seed.json): 622 atoms,
  W2 = 10264259/500000 = 20.5285 < 21, 4 corner slack cores (a = 499/1000), m = 0.
* FINDING (the tangency trap) [M]: the A71 seed is emission-side anti-verifiable — its
  atoms are arrangement-cell REPRESENTATIVES of the support squares, i.e. they sit ON
  the membership boundaries of the squares they serve (margins ~1e-6 by the LP's own
  optimality: load is tight where squares touch atoms). First v2 survey (60k nodes,
  depth 26): COVERED fired ZERO times, zero definitive rows, 400 cap witnesses — not
  the verification wall, the SEED's margins. Any emission pipeline that dumps LP duals
  at arrangement points produces uncertifiable certificates; the emitter must solve at
  eta-deep membership semantics (atoms forced eta-deep into the squares they serve;
  conservative for (P2'): eta-deep coverage implies true coverage).
* Machinery: code/pairlp413e.py = A71 pairlp413 with --eta (membership h = 1/2 - eta;
  arrangement points from the eta-SHRUNK squares); code/loop413.py = the emission loop
  (LP -> emit+canary -> v2 survey -> definitive rows grow the catalog -> re-solve).
* The pivotal curve: tau_2^eta(k4_13, beta=0) vs eta — the fractional-wall law that
  Lemma W quantifies integrally (corners4 integral witnesses: V(0.12) = 14 < 21 <=
  22 = V(0.15)). Measurements below.

(continued as runs land)

## Anchors: the first full-quantifier atom-bearing PASSes + the v2 cost law [M]

Synthetic grid-pair certificates (s = 3, k = 0, all grid-point pairs at weight 1;
a unit square at any admissible placement contains a pitch-g grid point at depth
>= 1/2 - g*sqrt(2)/2):

| anchor | pitch | atom margin | verdict | nodes | max depth | clause mix |
|---|---|---|---|---|---|---|
| certs/anchor_grid05_s3.json | 1/2 | >= 0.146 | **PASS (full B&B)** | 5866 | 8 | 2152 COV, 661 COV-F, 188 ND |
| certs/anchor_grid06_s3.json | 3/5 | >= 0.076 | **PASS (full B&B)** | 1098 | 8 | 347 COV, 213 COV-F, 57 ND |

The 0.5-grid anchor is the FIRST exactly-verified full-(P2') atom-bearing pair
certificate in the program (toy geometry, but end to end through the v2 B&B:
Python-exact 39.7 s). COVERED-F fires organically (661 handoffs; the near-axis
failing-set degeneracy measured and the spec's Lemma F generalized to failing sets
because of it).

Reference-implementation bugs caught by the corpus/anchors (both fixed, both
spec-conformant readings):
1. the VACUOUS clip must be re-applied at every child construction (v1/v2 wording
   already says "at box construction"; toy s199 PASS unreachable without it);
2. the margin-aware split heuristic must target atoms possibly collectable in BOTH
   factors (else it thrashes toward one-sided atoms and never reaches COVERED — a
   40-depth dive measured on the anchor before the fix). The spec's soundness is
   unaffected (Lemma S: heuristic-independent); §6 guidance matches the fix.

**Cost-law finding [M]**: the fine anchor (HALF the margin) verified in FEWER nodes
(1098 vs 5866). With exact membership + COVERED-F, the leaf scale is set by the
FRONTIER STRUCTURE of the measure (where coverage responsibility changes witness �
~ the atom pitch), not by the atom margin, whenever single atoms carry the threshold
weight. The v1 (1/margin)^4-6 law is a consequence of interval slop + uniform
splitting, both gone in v2. The corners4-specific residue: an LP measure fragments
the threshold over ~15+ small-weight atoms per box (mean w ~ 0.07), so the binding
scale reverts to ~min margin of the NEEDED SET (~eta) wherever no single-witness
handoff exists; emission should therefore CONSOLIDATE weight (snapped coarse atom
net, sparsity-priced columns, deeper-than-eta placements) � cost then tracks the
consolidated pitch, not eta.

## The P0 consumption path (stated; binds any corners4 v2-PASS)

A corners4 (k4_13) beta=0 v2 PASS at side s0 with delta = 1/1000 slack cores at the four
corner pins consumes EXACTLY as a v1 PASS would (the v2 claim is verbatim v1):
by Corollary P0 (docs/proofs/pair_kill.md; bridge side conditions eps_box >= 3*delta/
(5/2-delta), checked by the composition), it kills every packing CONTAINING the corner
pins — emptiness, stuckness unused, G_S = {} (no basin row needed for corners4) — at
every side m-tilde in (s0/(1 + delta/(5/2)), s0). That discharges the corners4 leaf of
C.K4TIER's stratum_kill obligation on that shell; full-window coverage = the slack-core
slab grid per the Lemma P shell rules (A71 pricing: ~38 sides at delta = 1e-3 over
[3.82, s0], each side one emission + verification).

## Lemma W' (fractional margin law — Lemma W's quantified successor) [T]

Let z* be ANY eta-feasible adversary (finitely many admissible core-free
interior-disjoint pairs with weights z >= 0 such that for every point pair position,
the z-mass of pairs that would collect it with BOTH endpoints eta-deep is <= 1), of
value V = sum z*(1 + beta*m2). Then for every P1'-valid certificate (true-semantics
coverage) with atom weights w_i:

    sum_i w_i * S_i^eta(z*)  >=  V - W2  >  V - (C(N,2) + beta*m),

where S_i^eta(z*) = the z*-mass of rows that collect atom i sharply but with some
endpoint LESS than eta deep. Proof: V <= sum_rows z* mu2(row) (validity) =
sum_i w_i L_i (sharp loads); L_i = L_i^eta + S_i^eta with L_i^eta <= 1 by
eta-feasibility at the atom's own position; sum. QED.

Consequence: the tau_2^eta curve prices the DEPTH PROFILE every valid certificate
must have — weighted shallow-service against the optimal eta-adversary is at least
tau_2^eta - threshold. Measured (catalog-restricted, feasible-scaled, so honest
lower bounds on tau_2^eta):
  eta = 0.1:  scaled value ~34 (plateau 57 unconverged) => >= ~13 weighted units of
              sub-0.1-margin service FORCED in every corners4 beta=0 certificate;
  eta = 0.05: scaled 18.31 (unconverged, bracket [18.31, 26.24]) — not yet forcing;
  eta = 0.02: run in flight.

## Cost-model survey (the eta=0.01 primal as a structural stand-in) [M]

certs/costmodel_k4_13_eta001.json = the eta=0.01 primal (435 atoms, W2 = 21.3795 —
NOT P1'-valid, n relabeled 11->12 to pass the gate; labeled cost-model, NOT a
certificate). Reference survey, depth 26 / 30k-node budget: 1948 nodes examined,
COVERED-F fired 104x (the handoff clause works on a real LP measure), EXEMPT 65,
NONDISJOINT 548, ZERO definitive rows (no coverage hole exhibited at this budget —
the measure is continuum-tight near its rows), but 250 cap witnesses at depth 26 and
plain COVERED 0: threshold-1 coverage on a fragmented measure (mean w ~ 0.05) needs
~15+ atoms simultaneously certain, so the binding leaf scale is ~the needed set's min
margin, well below the depth-26 box scale. Weight CONSOLIDATION is the emission-side
lever (see the cost-law finding above); with it, anchor-like node counts are expected.
