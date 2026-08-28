# Lab notebook (append-only, newest at bottom)

## 2026-08-16 — advisor — project start
- Repo initialised. Only prior artefact: `chat_history.txt` (a previous Claude session that derived
  the exact algebraic description of the Trump/Gensane–Ryckelynck 11-square packing and produced a rational
  certificate; those files were not saved, only the transcript).
- Environment: Python 3.14 (numpy/scipy/mpmath/sympy/matplotlib/shapely installed), 20 CPUs, no Lean yet.
- Wrote README, docs/known_results.md (seeded, unverified), docs/ideas.md, attempts/REGISTRY.md.
- Dispatching A01–A07 in parallel (see REGISTRY).

## 2026-08-16 — A01-literature (lit agent) — done
- Sweep of Friedman DS7 (2009), Stromquist 2003 (+1984 memos), Gensane–Ryckelynck 2005, Nagamochi 2005,
  Kearney–Shiu 2002, Bentz 2010/2016, Montanher–Neumaier–Markót–Domes–Schichl 2019, Ellsworth's "Squares in
  Squares" (to Feb 2026), Wikipedia/MathWorld/OEIS, arXiv API, Semantic Scholar forward citations.
- Outcome: bounds confirmed — 2+2·sqrt(4/5) = 3.788854 (Stromquist 2003, Thm 2; nothing newer exists) ≤ s(11)
  ≤ 3.877083590022814 (Trump 1979; exact octic s⁸−20s⁷+178s⁶−842s⁵+1923s⁴−496s³−6754s²+12420s−6865 published by
  Ellsworth 2023, agrees with G–R 2005's angle polynomial and with chat_history.txt). Attribution corrected: G–R
  did not improve Trump's packing, only its digits. s(12) is also open. "Vienna" interval B&B = JOGO 2019 paper
  (3 unit squares in a circle). No LP/SDP bounds and no Lean/Isabelle/Coq formalisations exist for this problem.
- Files: docs/literature.md (new), docs/known_results.md (rewritten, [verified] tags), docs/papers/ (11 PDFs +
  txt extractions + Ellsworth pages + n=11 SVG with exact parameters), attempts/A01-literature/notes.md, REGISTRY.

## 2026-08-16 — advisor — session-limit interruption
- All six computational/analysis agents (A02–A07) were killed mid-run by an API session limit; partial code and
  data survived on disk. Resumed each agent from its transcript with pointers to its partial work.
- Correction broadcast to A04: its "CANDIDATE" files (s ≈ 3.87708359224) are re-discoveries of Trump's packing,
  2.2e-9 ABOVE the exact record 3.877083590022814 (the threshold had been my rounded 3.877084).

## 2026-08-16 — advisor — second interruption (OAuth expiry) and re-dispatch
- All agents died again (401). Partial results on disk before death: A07 LP logs show τ*(3.7071)=10.000 for the
  n=10 calibration (LP method reproduces Stromquist's exact s(10)), and for n=11 τ*(3.65)≈9.37, τ*(3.80)≈10.43,
  τ*(3.85)≈11.07 (grid LP, row generation, not yet rigorous). A05: best pure 10-point unavoidable set s0≈3.751
  (< 3.7889) ⇒ point method alone cannot beat Stromquist. A04: Trump packing rediscovered repeatedly, nothing below.
- Re-dispatched A02–A07; spawned A08-measure-verify (independent exact-rational verifier for measure certificates)
  and asked A06 to prototype the Lean checker for measure certificates (I-C2). Critical path: A07 → A08 → A06.

## 2026-08-16 — A04-upper-search (search agent) — done-negative
- Fixed-s basin hopping (fsbh.py: minimise overlap penalty at target s, kick, relax with free s when feasible,
  shrink s) is the only method that leaves the upright/4x4 basin; free-s penalty BH (driver.py) stays at s=4.
- 2488 recorded local optima (results.jsonl); Trump's packing (s* = 3.877083590022814) rediscovered 276 times,
  by 7 of 8 chains, typically within 5–20 min; best strict s = s* + 3.9e-12; ZERO records below s* − 1e-9
  (check_candidates.py, exact-root threshold). Earlier CANDIDATE_* files (s ≈ s*+2.2e-9) renamed REDISCOVERY_*.
- Catalogue: local_optima.json (702 s-distinct), families_catalogue.json (102 structural families; 32 with
  s < 3.95, listed in notes.md with angles/counts/coordinates), best_optima.png. Runner-up structures: 5 squares
  at 45° (3.885618), 4 at 41.6° + 7 upright (3.886746, largest basin), 3.887045. Nothing between s* and 3.8856
  except slack variants of Trump's structure. Assessment: unstructured search saturates on Trump within minutes;
  a continuation should seed structurally different topologies (two tilted groups, tilts 20–30°, ≥6 tilted).

## 2026-08-16 — A03-upper-reconstruct (UB agent) — done-success
- Reconstructed Trump's 11-square packing: multi-start penalty/SLSQP optimiser (`attempts/A03-upper-reconstruct/optimize.py`,
  analytic SAT Jacobians, kicks to escape the nonsmooth 45° trap) gives s = 3.8770835900228136 (double, 1.4e-15 from the octic root).
- Contact graph (56 corner-on-line equations, rigid: rank 33/33 in positions) → mpmath Gauss–Newton at 70 dps →
  60-digit coordinates in `trump11_exact.json`. Verified: octic in s (residual −3.6e-66, also recovered by PSLQ),
  p(t)=5t⁸+10t⁷−2t⁶−14t⁵+12t⁴+6t³+2t²−2t−1 at t = −tan(θ/2) (1.8e-71; sign convention!), cos θ minimal polynomial,
  Ellsworth's s = 2+(2+sinθ)/(cosθ+sinθ) (1.9e-60), equal strip gaps 0.0248745350255969539804755… .
- Certificates: `certs/trump11_certificate.json` (s_c = 3877084/10⁶, margins 5.3e-8 wall / 1.06e-7 pair),
  `_tight` (3877083591023/10¹², margins 1.3e-10 / 2.6e-10), `_38771` (38771/10⁴), plus all-integer `_int.json` /
  `_tight_int.json` for Lean (D = 23 / 28 digits); `certs/verify_certificate.py` (stdlib Fraction/int, both formats) passes
  them and rejects 4 corrupted variants; A06's gen_cert_lean.py pre-check accepts the int file.
- Shared code: `code/squares.py`. Catalogue: `local_optima.json` (36 distinct s, 34 < 4; runner-ups 3.885618 = 2+2√(8/9),
  3.886746 with 4 squares at 41.565°). Nothing better than 3.877084 found. Notes: `attempts/A03-upper-reconstruct/notes.md`.

## 2026-08-16 — A02 (Stromquist analysis) — done
- Downloaded Stromquist 2003 to docs/papers/stromquist2003.pdf; full reconstruction of Lemmas 1-8, Theorems 1-3 in
  attempts/A02-stromquist-analysis/notes.md (+ check_stromquist.py grid checker, figure renders).
- Theorem 2 (s(11) >= 3.7889) = two-stage case argument: 10-point 3-4-3 lattice P1 unavoidable except in 4 edge
  rectangles (unit legs are the binding constraint), exceptional wall-hugging box forced (Lemmas 4, 6) to contain 3
  points of a 12-point set P2, count 1+9 < 11. Not expressible as one measure (P2 is adapted per rectangle).
- Errata: paper's f(sqrt(4/5)) table entry uses a spurious root (true .9145 @31.5deg, still fine); literal Fig.14
  point G=(.8,1.85) leaves a 1e-4 escape (Lemma 4 needs f(.95)>=.8, but f(.95)=.798); G'=(.78,1.845) repairs it.
- Assessment: pure 10-point sets ~3.74 max (heuristic); best route = A07 LP + Stromquist-style case splits at the
  walls ("case-LP"), plus clique inequalities; certification = three (x,y,theta) coverage checks, no lemmas needed.

## 2026-08-16 — A05 (LB agent, postdoc) — optimised unavoidable point sets (I-L1): done-negative
- Code: `attempts/A05-unavoidable-opt/unavoid.py` (vectorised coverage evaluator + wall grids, symmetric
  parametrisations, SLP/LP minimax optimiser with trust region + kick heuristic, continuation in s0),
  `run_opt.py`, `holes.py`, `make_cert.py`; verifier `certs/verify_unavoidable.py` (exact `Fraction`
  interval B&B with t = tan(theta/2) rationalisation; `--float` = IEEE-double outward-rounded mode, 50x faster).
- Sanity: n=5 blind -> 2.70712 (Goebel set rediscovered, exact set gives max d = 0 at 2+1/sqrt2);
  9 points reach only ~3.414 (=2+sqrt2), so Stromquist's s(10) is not a pure 9-point argument;
  Stromquist's Fig.13 10-point set at 3.7889: max uncoveredness +0.0233, 4 wall-adjacent holes = his two rectangles.
- Result: max s0 for a pure 10-point unavoidable set ~ 3.7505 (numerical, all families converge to the 3-4-3
  column pattern = Stromquist Fig.13 rotated). Robust set (margin 2e-3) at s0 = 3.741594 certified PASS by the
  exact-rational verifier (863 953 boxes, 270 s CPU) and by the float mode (1.15M boxes, 46 s):
  `certs/unavoidable_10pt_3.7416.json` — sanity artefact only, below 3.788854.
- Obstruction: interior Lemma-2 triangles (26/64 deg squares) vs 45 deg squares slipping along the walls between
  wall-adjacent points. Holes of the minimax-optimal set at 3.7889 / 3.80: depth +0.0078 / +0.0099, uncovered
  fraction of (c,theta)-space 2.3e-3 / 3.3e-3, mostly interior. If squares whose centre is within 0.05 (0.1) of
  the boundary of the centre domain are exempt, 10 points reach s0 ~ 3.85 (3.94): the entire deficit sits at
  the walls/corners -> the way to use point sets is Stromquist's wall case-argument (cf. A02/A07 "case-LP").
  With corners pinned at (1,1) (Lemma 1) and the 0.05 wall layer exempt, 10 points reach only s0 = 3.807:
  the headroom of "10 points + wall case-argument" above 3.7889 is at most ~0.02.
- Files: notes.md, plots best10_s3.751.png, holes_best10_s3.789/3.800.png, wall_holes_s*.png,
  pinned_holes_s*.png, JSON: holes_best10.json, wall_holes.json, pinned_delta0.05.json, stromquist_fig13_eval.json.

## 2026-08-16 — advisor — status after A02/A03/A04 completion
- A03 done-success: Trump packing reconstructed to 60 digits, rigid (Jacobian rank 33/33), certificates in certs/
  (s_c = 3877084/10^6 and s*+1e-9) PASS the stdlib-Fraction verifier; integer versions ready for Lean.
- A04 done-negative: 2488 records, Trump basin hit 416×, nothing below s*; runner-ups 3.885618 (45° family) and
  3.886746; families_catalogue.json for future structured seeding.
- A02 done: Stromquist proof fully reconstructed; two errata found (table value f(√(4/5)); Fig. 14 point G leaves
  a 1e-4 hole at centre (0.6427,1.3750), tilt 69.67° — repaired by G'=(.78,1.845)); theorem unaffected. Recommends
  "case-LP": LP for the bulk + Stromquist-style wall case splits, to push beyond the pure-LP ceiling.

## 2026-08-16 — A06 (lean agent) — Lean 4 toolchain + checkers: done-success
- Toolchain: elan 4.2.3, Lean 4.33.0 stable, Lake 5.0.0 (`~/.elan/bin`, 82 s install). Mathlib NOT installed:
  `lake exe cache get` (v4.34.0-rc1, 8691 files, 9 min) filled the disk (31 GB → 1.6 GB free) and was rolled back;
  bridge lemmas therefore remain on paper (sketch in lean/PackingCertMathlib/BridgeSketch.lean, unbuilt).
- lean/PackingCert (core Lean only), `lake build` 4.7 s + 97 s for the measure theorem:
  * UB: `checkPacking : Cert → Bool` (Int arithmetic; unit-square shape, strict containment, strict SAT
    separation over the 8 edge vectors). `trump11_ok : checkPacking Data.trump11 = true` (side 969271/250000)
    and `trump11_tight_ok` (side 3877083591023/10^12) by native_decide AND by axiom-free kernel `decide`
    (1.3 s). Data generated from certs/trump11_certificate_int.json / _tight_int.json by lean/gen_cert_lean.py
    (which re-checks in Fraction arithmetic first).
  * LB: `checkMeasure : MCert → Bool` (Rat interval branch-and-bound over (t=tan θ/2, cx, cy), semantics aligned
    with certs/verify_measure.py). `s11_ge_37416 : checkMeasure Data.a05_10pt = true` — A05's 10-point set at
    s = 3.741594 (571k boxes, 93 s native / 97 s native_decide); `s5_gt_26` (perturbed Göbel). Kernel `decide`
    does not work for Rat. Finding: unperturbed Göbel-type sets have zero margin (atom on the edge of wall-flush
    squares) and are unverifiable by any box method — certificates must be backed off.
- Files: lean/README.md, lean/gen_cert_lean.py, lean/gen_measure_lean.py, lean/PackingCert/MeasureBench.lean
  (native timing exe), attempts/A06-lean-setup/notes.md (versions, timings, exact statements, gap analysis).

## 2026-08-16 — A07-lp-dual (LP agent) — INTERIM (14:35): measure certificate for s(11) >= 3.80 on disk
- Method: covering LP for tau*(s) = min total mass of a measure with mu(Q) >= 1 for every closed unit
  square Q in [0,s]^2, solved by simultaneous row generation (placements) AND column generation (atoms
  placed where the dual fractional packing over-covers). Grid-atom version (v1) is useless: its dual
  exploits sliver overlaps between grid points (tau_grid(3.80) = 11.000 exactly, true coverage 1.5).
- Numbers so far (free atoms, v2): tau*(3.65) = 9.364, tau*(3.7071) = 10.000 exactly (LP tight at s(10)),
  tau*(3.80) = 10.4865 (row-converged, 137 atom orbits), tau*(3.82) ~ 10.65, tau*(3.84) ~ 11.01,
  tau*(3.85) ~ 11.06  => crossing of 11 near s ~ 3.835-3.84.
- certs/measure_certificate_3.80.json (format measure-certificate-v1, 1069 atoms, exact rationals,
  weights x1.03 rounded up, total 10.801639 < 11).  A07's float-interval B&B (outward rounding 1e-12,
  min box width 1e-5, 12.2M boxes) PASSES an earlier iterate; the official file is being re-verified by
  A07's verifier and by A08's exact-integer certs/verify_measure.py (running).  If both pass:
  s(11) >= 3.80 > 2+2sqrt(4/5) = 3.788854 (Stromquist).  Details: attempts/A07-lp-dual/notes.md.

## 2026-08-16 — A08-measure-verify (verify agent) — done-success
- Deliverable `certs/verify_measure.py` (+ `certs/README.md` describing all certificate formats/verifiers): independent,
  exact-integer interval branch-and-bound over (t = tan θ/2, cx, cy) with admissible-region clipping, inherited certified
  atoms, numpy float shortlist (accept decisions always exact), witnesses with EXACT masses (kinds hole/tight/undecided),
  `--jobs`, `--strict-margin`, `--scale-weights`, `--report`, `--selftest` (int core vs Fraction core, 0 mismatches).
- Tests: centre-atom s<2 PASS / s>2 FAIL; Göbel's literal 4-point set is a *tangency* (atom (1,1) on the edge of the
  wall-flush corner square, at every s) — unverifiable by any box method (A06 found the same); backed off by 4e-4 it
  PASSES at 2.70610678 (51k boxes, 1.7 s) and FAILS at 2.72 (holes at θ≈34°, c≈(1.36,1.36)); A05's 10-point set at
  3.741594 independently PASSES (568k boxes, 15 s). A07's raw LP files FAIL as expected: v1 grid atoms on wall-square
  edges (tight); v2test has 39 genuine holes (θ=0.0017°, c=(0.50004,1.49988), exact mass 0.9678: eps_geo=1e-4 shrink is
  smaller than the row spacing) — witnesses in attempts/A08-measure-verify/witnesses_*.json.
- **A07's frozen `certs/measure_certificate_3.80.json` (1069 atoms, total 10.801639 < 11) PASSES**: 5 836 650 boxes,
  max depth 45, 62.9 s on 4 processes (`--depth 48 --jobs 4`). Re-verified with two other box trees (tscale 1 / 4:
  PASS), float-free exact runs on sub-boxes (identical trees), 300k random float placements (min mass 1.0300),
  `--strict-margin 0.04` (rigorous holes at mass 1.0288 ⇒ the certificate's slack is exactly A07's ×1.03).
  ⇒ **s(11) ≥ 19/5 = 3.80** (beats Stromquist's 3.788854), pending A07's own verifier and A06's Lean re-check
  (regenerate MeasureData.lean from the certificate, fuel ≥ 48).
- Cost model for the future: leaves ~ (tight volume)/δ³ with δ = certificate robustness margin; δ = 1e-4 was
  affordable here (6M boxes) because tight regions are thin; a larger eps_geo would make Lean re-checks cheaper.
- Files: attempts/A08-measure-verify/{notes.md, make_tests.py, convert_a07.py, tests/, a07/, witnesses_*.json,
  report_*.json}; Lean-port design (integer scheme enabling kernel `decide`) in notes.md §6.
- 14:50 UPDATE: certs/measure_certificate_3.80.json PASSES BOTH verifiers: A07 float-interval B&B
  (12.0M boxes, min width 1e-5, outward rounding) and A08's independent EXACT integer B&B
  certs/verify_measure.py (5.84M boxes, max depth 45, 115 s):
  "PASS: every closed unit square in [0,19/5]^2 has mass >= 1; total 10801639/1000000 < 11 ==> s(11) >= 19/5".
  ==> NEW LOWER BOUND s(11) >= 3.80 (previous: 2+2sqrt(4/5) = 3.788854, Stromquist 2003).
  Certificate: 1069 atoms (137 D4-orbits), exact rationals, total mass 10.801639.  Now pushing to 3.82.

## 2026-08-16 — advisor — NEW LOWER BOUND s(11) ≥ 3.80 (computer-verified)
- certs/measure_certificate_3.80.json (A07: 1069 atoms, s = 19/5, total 10.801639, weights ×1.03 robustness)
  PASSES certs/verify_measure.py (A08, independent exact-integer interval B&B: 5,836,650 boxes, depth ≤ 45,
  51 s), reproduced by the advisor; advisor's own float spot-check: 200k random + adversarial placements,
  min mass 1.0300. Bridge argument (scale + shrink) is two lines. This beats Stromquist's 3.788854.
- Next: A07 pushing s to 3.82/3.84; A06 asked to Lean-check the certificate.

## 2026-08-18 — A06 (lean agent) — Lean theorem for the new lower bound s(11) ≥ 3.80
- New all-integer measure checker `lean/PackingCert/PackingCert/MeasureInt.lean` (`checkMeasureI`), same integer
  scaling and box rules as certs/verify_measure.py (A08); header states the certified claim and the bridge lemma in
  words. ~10× faster than the Rat prototype (no gcds); kernel `decide` works on toys (Göbel, 795 boxes, 30 s, no axioms).
- `PackingCert.MeasureI.s11_ge_3_80 : checkMeasureI Data.cert_3_80 = true` (certs/measure_certificate_3.80.json,
  1069 atoms, mass 10.801639 < 11, s = 19/5) by native_decide in the separate target `lake build PackingCertSlow`:
  654 s wall (precompileModules on; 1509 s interpreted); compiled exe 5 837 883 boxes in 536 s (A08 Python:
  5 836 650 boxes). Axioms: native_decide only. Default `lake build` clean ≈ 76 s (UB theorems + A05 measure
  theorems `a05_10pt_int_ok` 13 s / `s11_ge_37416` 71 s).
- certs/measure_certificate_3.82.json is REJECTED by the Lean checker (false after 103 534 boxes, 12 s), consistent
  with A08 (17 holes, min mass 0.988). No theorem for it; data kept (`MeasureIntData382.lean`, bench mode int_3_82).
- Docs: lean/README.md (theorem table, axioms per theorem, build commands), attempts/A06-lean-setup/notes.md §8.

## 2026-08-18 — A07-lp-dual — s(11) >= 3.81 certified; 3.82 in the rigorous separation loop
- certs/measure_certificate_3.81.json (980 atoms, s = 381/100, weights x1.04, total 27463/2500 = 10.9852 < 11)
  PASSES A08's exact verifier: "PASS: every closed unit square in [0,381/100]^2 has mass >= 1 ; total
  27463/2500 < 11 ==> s(11) >= 381/100", 5,116,306 boxes, max depth 42, 82 s (3 jobs).  ==> s(11) >= 3.81.
- 3.82: row-converged tau = 10.7163 (x1.025 = 10.985); A08 + A07 verifiers found oracle-missed pockets
  (unscaled mass 0.963-0.975 at theta ~ 39-45 deg); witnesses fed back as LP rows (rigorous separation
  loop, results/v2_s3.82_fix*.json); second round running.
- 13:10 FINAL: certs/measure_certificate_3.82.json (1769 atoms, s = 191/50, weights x1.025, total
  5492737/500000 = 10.985474 < 11; two rounds of "verifier witnesses -> LP rows -> re-solve") PASSES A08 exact
  verifier ("PASS ... ==> s(11) >= 191/50", 7,639,758 boxes, depth 43, 107 s) and A07 float B&B (14.8M boxes).
  ==> s(11) >= 3.82.  Ceiling of the pure LP/measure method: tau*(3.83) = 11.000, so 3.82 is (essentially) the
  end of the road for I-L2; blocking fractional packing at 3.83-3.85 does not exploit small cliques (max
  pinwheel weight sum 0.31, heaviest overlapping pair 0.93) => next: case-LP (I-L6), not clique cuts.
  A07 done-success; full write-up attempts/A07-lp-dual/notes.md, plot plots/tau_vs_s.png.

## 2026-08-18 — advisor — s(11) ≥ 3.82 certified; Lean theorems
- A07 shipped certs/measure_certificate_3.81.json and _3.82.json (rigorous separation loop: verifier witnesses
  → LP rows, two rounds for 3.82). Both PASS A08's exact verifier and the advisor's re-runs
  (3.81: 5.12M boxes 47 s; 3.82: 7.64M boxes). Pure-LP ceiling: τ*(3.83) = 11.000. Blocking fractional
  packing is Trump-like and does NOT exploit pinwheels ⇒ next step is I-L6 case-LP branching, not clique cuts.
- Lean: advisor added targets PackingCertSlow381/382; `s11_ge_3_81` built (12 min, native_decide axiom only);
  `s11_ge_3_82` building. docs/results.md and README updated.
- Lean `s11_ge_3_82` built (26.5 min, native_decide axiom only). Final certified chain: s(11) ≥ 3.82.

## 2026-08-18 — A09-angle-lattice-milp — angle-lattice MILP: ab-initio finder yes, certifier no
- `attempts/A09-angle-lattice-milp/milp_pack.py`: fixed-angle-lattice packing MILP (SAT-axis disjunctions, per-axis
  big-M, symmetry breaking, HiGHS or CP-SAT back-end, fixed-structure LP polish); `make_cert.py` -> rational
  certificate + exact verification.
- Calibration reproduced exactly (polished LP): {0}: n=5,10,11 -> 3,4,4; {0,45}: n=5 2.7071067812, n=10 3.7071067812
  (CP-SAT proves optimality, 535 s), n=11 3.8856180832 (= 2+4sqrt2/3, Stromquist Thm 3; found in ~1 min, not proven).
- AB INITIO: Theta={0,theta*} -> Trump's packing s=3.8770835900228 (diff 4e-16, 6 uprights + 5 tilted, no contact
  graph given) in 23-39 s; coarse lattice {0,30,35,40,45} -> Trump structure at 40 deg, s=3.87764 (rational cert
  PASSES). Solver dual bound never leaves sqrt(11): LP relaxation void; feasibility at 3.87707 with counts fixed:
  UNKNOWN in 900 s. HiGHS unusable beyond n=10 uprights. n=12 {0,45},{0,40,45}: nothing < 4 in 600 s.
- Assessment (notes.md sec. 4): interval angle-box B&B with a MILP oracle is hopeless (per-box oracle already fails on
  a point box); the viable box killer is Theorem 1 restricted to orientations in the box (Stromquist's 0/45 result is
  the two-point case) -> recommended follow-up: A07 LP with theta restricted to [theta*-delta, theta*+delta] u {0}.

## 2026-08-18 — advisor — dispatched A10 (angle-box LP sizing) and A11 (ab-initio sweep over open n ≤ 100)

## 2026-08-18 — A11-abinitio-sweep — angle-lattice MILP sweep over open n ≤ 100: 2 exact rediscoveries, no beat
- `attempts/A11-abinitio-sweep/`: records n ≤ 100 parsed from Ellsworth's triangular table (`records.json`); tilt
  angles of the record packings read from his SVG sources (17: 39.805/53.376, 18: 24.295/65.705, 28: 30.291,
  29: 5 angles, 37: 45+42.09/47.91, 39, 41, 50 = atan(3/4), 53); A09's CP-SAT + LP-polish + rational-cert
  pipeline run as a 4-slot queue (39 runs, 600–900 s each, `results.jsonl`, `notes.md` §4).
- MATCHES (ab initio, no contact graph, certificates PASS `certs/verify_certificate.py`): n=11 Trump 3.8770835900228
  (43 s) and n=18 Hämäläinen 7/2+√7/2 = 4.822875655532295 (14 uprights + 2×2 block tilted 24.295°, < 600 s).
- NO BEAT for any n. n=17 stalls at 4.7071 (16+1) on all lattices/seeds, n=19 at 4.9428 (16+3); feasibility at
  record−1e-4 UNKNOWN (12, 17, 18, 19, 20, 21); n ≥ 26 stays near the grid in 900 s (26–29, 37–41, 50, 52, 65).
  Curiosities: n=18 at 4.8385 with 13+5 at Trump's angle; n=50 at 7+5/7 with one 3-4-5 tilted square.
- Verdict (notes.md §5–6): finder competitive only for n ≲ 20 with |Θ| ≤ 3, the record tilt on the lattice and a
  small tilted cluster; larger n needs seeding with the record structure + fix-s at record−ε, angle refinement near
  the record tilt, in-search LP polish, more workers/longer runs. Bugs: fix-s off the 1e-5 grid ⇒ MODEL_INVALID
  (fixed in A11's milp_pack.py); `--counts` silently ignored by the CP-SAT back-end (A09's counts run was unconstrained).

## 2026-08-18 — A10-angle-box-lp — orientation-restricted measure LP: Trump box tight, mid-tilt band not; angle B&B sizing
- `attempts/A10-angle-box-lp/lp_measure_box.py` (A07's lp_measure2 with θ-restricted rows, C4/D4 symmetry chosen by
  reflection-closure, EXACT per-θ arrangement row oracle — the c-grid oracle missed sliver holes and gave τ=10.76 at
  {0,45}/3.89 where ν≥11 — and non-binding row pruning: LP 60 s → 1 s), `verify_measure_restricted.py` (A08 copy +
  `--theta-range`), `make_cert_box.py`, `run_batch.py`, `summarize.py`; results/*.json, notes.md.
- Sanity: {0°} → crossing exactly at s=4 (9→16); {0°,45°} → (3.885, 3.886] = Stromquist's 2+4√2/3.
- Trump box [0,δ]∪[θ*±δ]: τ*_B ≈ 10.3–10.8 then jumps to 11 exactly (weight-11 fractional packing appears):
  s_B(10°)≤3.84, s_B(5°)∈(3.84,3.85), s_B(2°)∈(3.86,3.865), s_B(1°)∈(3.87,3.874], s_B(≤0.5°)≤3.876 (EPS_GEO floor 8e-4)
  ⇒ s*−s_B(δ) ≈ 0.006·δ: the restricted LP is tight at Trump as δ→0. Rigorous restricted certificate
  (certs_wip/box_cert_3.85_d2.json, PASS): no packing with all orientations in [0,2°]∪[38.18,42.18°] has side ≤ 3.85.
- Negative: boxes "uprights + one tilt in ≈[20°,36°]" ([0,10]∪[20,30], [0,2]∪[32,36], [0,1]∪[34.5,35.5], [0,1]∪[31,33],
  [0,5]∪[25,35]∪[38,43]) are ALIVE at 3.85 and 3.87 with τ=11.000 exactly via 4-fold ¼/½-weight fractional structures
  (no packing known there < 3.89), down to half-width 0.5°; class weights/counts do not help (τ(α) convex, min at α=1);
  [0,10] alone: 9.33 (3.85), 10.5 (3.87), 11.0 (3.90). Far boxes without uprights or with tilts ≥ 38° die easily.
- Verdict: pure angle-box B&B not viable at 3.85–3.87 (mid-tilt band never dies; ≥10⁶–10⁹ multisets meet it; per-box
  LP 1–15 min); the box LP is a good first-level killer inside a case-LP (I-L6) tree with clique/region cuts against
  the ¼-weight 4-fold structures. Trump neighbourhood alone would be ~10³ LPs.

## 2026-08-18 — A12-region-rank-pilot — region-rank cuts (I-L8) do NOT close the mid-tilt integrality gap (done-negative)
- `attempts/A12-region-rank-pilot/`: `lp_region.py` (A10 box LP + region dual variables λ_R with cost k(R); row oracle on
  μ + Λ with cell/shell sampling), `make_regions.py` (k(R) ≤ α(G_robust) for unions of small (c,θ)-boxes, robust pairwise
  overlap by interval witness points), `analyze.py`/`geom.py` (support dissection, exact SAT overlaps, CP-SAT MIS,
  rank-inequality violation search, realised lower bounds k_lb(R)), `iterate.py`, `depth_profile.py`, `lp_fixed.py`
  (conditional LP: fixed squares / excluded zones, budget n−1); notes.md, results/, plots/, logs/.
- Box [0,2]∪[32,36] reproduced: τ = 11.000 (3.86: conv 96 s; 3.87: conv 33 s). Fractional packing = 4 corners (1) + 4 side
  zones (4×¼ each) + interior 3 (8 tilted ¼ pinwheel at 32–33° + 4 upright ¼); Σx(frac) = 7 vs α = 6, support 11 vs α = 10,
  max rank violation 1.5. ALL orbit weights are integers ⇒ integer load on every C4-symmetric region; every macroscopic
  region tried (discs 0.6–1.0, annulus, side/corner zones, tilted blobs, corners+disc, sides+disc, …) is realised
  (x*(R) ≤ k_lb(R)) — 4+4+1, 4+2+3, 8+1 all packable, only the global 4+4+3 fails.
- Lemma: with k(R) certified by the sub-LP (I-L8 recursion) a cut is never violated when x*(R) ∈ ℤ (x*|_R is dual-feasible
  for the sub-LP, τ_R ≥ x*(R)). Combinatorially certified fine cuts (28 boxes, ρ ≤ 0.05, θ±1°, k = 6 vs 7; ρ ≥ 0.08 ⇒ α ≥ 8)
  added to the LP: τ = 11.000000, λ = 0 in 10+9 rounds at 3.86, 3 at 3.85, 3 at 3.87; support slides 0.06–0.33 per round
  (continuum escape); even an uncertified ρ = 0.3, k = 6 region is escaped. Per round 10–100 s.
- Contrast: conditional LP "four corner squares fixed" τ = 7.000 = budget (alive); "corners fixed + no square centred in
  side zones" τ = 5.000 < 7 (DEAD, 12 s) ⇒ the 8+3 structure needs conditional counts (case-LP I-L6, fix-a-square branches).
- Verdict: region cuts don't kill the mid-tilt band; "angle boxes × region cuts" campaign stays 10⁶+ LPs. Recommend a pilot of
  an asymmetric (C1) conditional LP with box-of-fixed-square "shadow" rows (est. 10³–10⁴ LPs per angle box).

## 2026-08-18 — A13-case-lp-bnb (case-LP branch-and-bound pilot, I-L6)
Implemented the rigorous case-LP B&B (hypotheses = core boxes with rational inner squares + NO-families; C1 node LP; exact verifier with exempt tests; certify loop). Sanity: A12's conditional LP reproduced exactly (7.000 / 5.000). At s = 3.84: NO(all corners) dead by 1.59, 9/12 corner boxes dead by ≥ 0.23, the 3 corner-square boxes at slack ≈ 0 (undecided by 300-s LPs); tree not closed in ~40 LPs; one node certificate verified end to end; core-node certification exposed a row-oracle blind spot (touching shell) — fixed, not re-certified. Verdict: LP convergence (column generation) is the bottleneck; 3.84 hinges on three LPs; 3.85+ not viable yet. See attempts/A13-case-lp-bnb/notes.md.

## 2026-08-18 — A14-close-tree-384 — close A13's case tree at 3.84? NO: the tree cannot close (done-negative)
- `attempts/A14-close-tree-384/`: A14 copies of A13's `lpbox/caselp/certify/verify_case` + `run_node.py` (one node, warm),
  `branch_node.py` (one wall-first level with a process pool), `level1_385.py`, `verify_casetree.py` (exact tree-logic checker:
  box cover of the corner zone in rationals, core lemma re-derived with rational tangent bounds, NO-family set = C4-orbit,
  leaf re-verification), `summarize_a14.py`; notes.md (§1 D4 WLOG + budget check confirmed; §3b–§5b bugs; §6 verdict).
- Engineering: vectorised column incidence (A13 spent 0.2 s per column in a Python loop); alternating row/column iterations
  (dual/primal simplex stay warm; mixed additions took 340 s per HiGHS solve at 8k×5k) with row pruning (6 strikes) and
  column pruning (zero weight, positive reduced cost, 2 strikes): 2–30 s per iteration; HiGHS status check.
- BUG (A10→A13 `RowOracle.exact_theta`, all hypothesis nodes): the max_cand cut of the lowest-mass arrangement cells was
  applied before the hypothesis filter ⇒ exempt cells (mass 0.2–0.5) exhausted it ⇒ "minmass = 1" with genuine holes
  (verifier: 0.958 at θ = 8.27°). Two further blind spots (cells straddling the admissible-domain boundary are clipped into
  neighbours ⇒ wall-touching placements never proposed; the cap exhausted at unconverged nodes) — all three fixed (v1–v3).
  Every A13 τ at a hypothesis node is an under-estimate; A13's "9 of 12 corner boxes dead by 0.2–0.7" was an artefact
  (A14: −0.13…+0.04, and 0.00 with the 3e-3 certification shrink). A13's node 13 was never solved (pending in tree.json).
- Results at 3.84 (fixed oracle): NO(all corners) 9.59 (dead −1.4) — **certified, exact verifier PASS: every packing at side
  ≤ 3.84 has a square centred in a corner zone [0.5,1.1]²**; far box 13 ([0.8,1.1]²×[60,90]°, −0.40) also certified (total
  9.9755 < 10); on-corner boxes 2/3/4 alive +0.11…+0.19; exact corner square
  fixed: τ = 10.000 with dual coverage 1.000 ⇒ τ* ≥ 10 for every box containing it (no refinement can kill); four exact
  corners fixed: 7.000 = budget (the ¼-weight structure survives all corner fixing); killing power only in NO-side zones
  (4 corners + NO side0: 6.36 < 7; + NO all sides 4.25; root + NO all sides 8.28). One more corner level under 2/3/4:
  NO child −0.26…−0.30, diagonal-off boxes −0.2, 9/12 YES boxes alive by +0.13…+0.54 (growth ×9, slack grows with depth).
  Certification overhead 0.1–0.25 per node. 3.85 level 1: root 11.07, NO corners 9.56, on-corner boxes 0.00…+0.11.
- Verdict: 3.84 not certifiable by this tree; closing needs ≥ 2 empty side zones per leaf ⇒ 10⁵–10⁶ node LPs (10⁴–10⁵ CPU-h);
  recommend stopping the case-LP campaign; the machine-checked yield of I-L6 is the corner-zone lemma + the structural facts.

## 2026-08-19 — A15-theta-pilot — ϑ′ (Lovász–Schrijver) vs the point-clique LP on one discretised placement graph (I-L9 pilot, done)
- `attempts/A15-theta-pilot/`: `graph.py` (D4-invariant grid of placements + injected A12 ¼-structure / A07 dual placements, exact SAT
  adjacency), `lp_point.py` (point-LP, row generation), `theta_sdp.py` (ϑ′ with the D4 symmetry block-diagonalised via isotypic projectors,
  one constraint per pair orbit, SCS direct; dual-certificate upper bound and primal-feasible lower bound), `support_sdp.py` (exact ϑ′ on the
  support subgraph ⇒ tight lower bound), `continue_sdp.py`, `alpha.py` (CP-SAT), `run_pilot.py`, `analyze.py`, `post_dual.py`, `table.py`;
  `results/*.json` (+ graphs, B, LP x, SCS duals), `logs/`; notes.md.
- Table (same graph for all three numbers; N ≈ 2150–2340, h = 0.2, Δθ = 10° or mid-tilt {0}∪[30,36]; f385: N = 3750, Δθ = 5°):
  s=3.80: LP 10.000, ϑ′ 10.000, α 10 | s=3.84: LP 11.000, ϑ′ ∈ [10.376, 10.392], α 10 | s=3.85: LP 11.000, ϑ′ ∈ [10.43, 10.48]
  (mid-tilt graph [10.41, 10.48]; N=3750: [10.40, 10.74]), α 10 | s=3.87: LP 11.000 (row generation not converged, ≥ 10.97),
  ϑ′ ∈ [10.45, 10.64], α 10.  On the A12 ¼-structure support alone (52–80 nodes): LP 10.5–10.9, ϑ′ = α = 10 (9 at 3.87).
- Verdict: ϑ′ − LP ≈ −0.55…−0.6 at 3.84/3.85 on the same placement graph (≈ half of the LP's integrality gap; ϑ′ is still ≈ 0.4 above α,
  B has rank ≈ 150 with corners 0.93, side uprights 8 × 0.37, interior 2.5); continuous kernel version worth building: YES — with the
  kernel class containing coverage-indicator features (the LP certificate is itself such a kernel, notes §4).  NOT a bound on s(11)
  (finite induced subgraph; the grid LP is 11 only because the ¼-structure was injected).
- Numerics: SCS on the symmetry-reduced SDP (0.3–0.9 M pair-orbit rows, PSD blocks ≈ N/8…N/4) is 0.25–0.6 s/iteration and needs ≳ 3·10⁴
  iterations; 25–55-min runs give reliable dual upper bounds only; tight values from 400–520-node support sub-SDPs (15 min).

## 2026-08-19 — A16-theta-casetree — ϑ′ as the node certificate of the A13/A14 case tree (decisive comparison test, done)
- `attempts/A16-theta-casetree/`: `nodes.py` (node catalogue with A14's exact hypothesis/exemption semantics via caselp.Hyp:
  root, one/four corners fixed exactly, A14's depth-1 on-corner and off-corner boxes, corners + NO side zone, NO corner zones;
  seeds = the node's own A14 LP fractional packing + A12 ¼-structures; LP initial points = A14's atoms), `theta_sdp.py`
  (A15's ϑ′ SDP generalised to any subgroup H ≤ D4 — the stabiliser of the admissible set is computed and used: D4/Z2/C1;
  validated against full-matrix cvxpy), `graph.py` (near-duplicate merge, subgroup-closed seeding), `lp_point.py`
  (incremental HiGHS), `run_node.py`, `table.py`; results/*.json (+ table.md), logs/, notes.md.
- Per node: one seeded placement graph (h = 0.2, Δθ = 10°, N = 970–3150), the LP ν*_H, ϑ′ bracket (certified dual-certificate
  upper bound + tight support-sub-SDP lower bound), α (CP-SAT).  NOT a bound on s(11).  Un-seeded grids (h down to 0.1) are
  integral (LP = α = 10): uninformative.
- **Results (certified ub / tight, s = 3.84 | 3.85 | 3.87): four corners fixed exactly (the node that stalls the tree,
  LP = 7.000 = budget): ϑ′ ≤ 6.62 | 6.59 | 6.51 (tight 6.25–6.46), α = 6 — dead by ≥ 0.38–0.49, stable under grid refinement
  (N 2177→3152) ; one corner exact (LP = 10.000 = budget): ϑ′ ≤ 9.44 | 9.49 | 9.48 (tight 9.38–9.45) — dead by ≥ 0.5 ;
  A14's three alive on-corner boxes (LP grid 10.03–10.05, continuum 10.11–10.19): ϑ′ ≤ 9.61–9.67 | 9.52–9.64 (tight 9.44–9.50),
  dead by ≥ 0.24–0.48 even with richer seeding ; A14's uncertifiable off-corner boxes: ϑ′ ≤ 9.41 / 9.14 (dead 0.59 / 0.86) ;
  corners + NO side0: ϑ′ = α = 6.000 exactly (integral) vs LP 6.25.  Everywhere α = budget − 1 and ϑ′ ≈ α + 0.4–0.6.**
- Consequence: the ϑ′ tree at 3.84/3.85 is root + 13 leaves (A14 estimated 10⁵–10⁶ LP nodes); the root alone (A15: ϑ′ < 11
  up to 3.87 on seeded grids) may suffice.  Cost 40–60 min per node (SCS: dual certificate accurate after ≈ 2000 iterations;
  C1 nodes are eigendecomposition-bound at 1.3–1.5 s/it — dual-side/cutting-plane or Burer–Monteiro needed to scale).
  Caveat: grid ϑ′ only lower-bounds the continuum ϑ′ (no upward drift seen under refinement/seeding, but only the continuum
  kernel certificate settles it).  Rigorous plan (notes §3(e)): per-node kernel K ⪰ 0, K(x,x) ≤ λ−1 on non-exempt placements,
  K(x,y) ≤ −1 on disjoint non-exempt pairs (verify_case.py exemption semantics), LP-atom indicator features + cross terms
  (node duals have 30–45 eigenvalues > 1 %), verification by cell B&B + pairwise cell table, rational LDLᵀ; ≈ 4–6 weeks to a
  first certified node.  Recommendation: build the I-L9 continuum kernel at the ROOT first (λ < 11 at 3.84), tree as fallback.

## 2026-08-19 — A17-kernel-root — continuum ϑ′-kernel certificate at the root (float phase, done-negative + two structural discoveries)
- `attempts/A17-kernel-root/`: `features.py` (normalised coverage-indicator features φ(x) = (1, 1[p∈Q(x)]/m(x)) over
  A07's 1181 LP atoms at 3.84; D4 action on atoms/features; isotypic basis reusing A16 theta_sdp; LP-form kernel;
  D4-canonical pattern keys), `sdp.py` (kernel SDP min λ s.t. K(x,x) ≤ λ−1, K(x,y) ≤ −1−δ on rows, M ⪰ 0 D4-invariant:
  per-block Burer–Monteiro X = YᵀY + L-BFGS hinge² feasibility + λ-descent — the sparse-conic SCS form was built and
  abandoned because the patterns are DENSE (71–277 atoms per square, ~2·10⁵ nnz per row); validated vs cvxpy/Clarabel),
  `oracle_diag.py` (scans + admissible-boundary sweeps + A07-style rotated-frame prefix-sum coverage scan + pattern-search
  polish), `oracle_pair.py` (strict SAT-disjointness geometry, tangent-pair sampler by contact-distance bisection,
  node-set K scans, alternating polish with re-contact), `calibrate.py`, `loop.py` (cutting-plane driver, crash-resumable),
  `check_feas.py`, `export_cert.py`; results/ (calibration_380.json, k384.json history, kernel_k384.json + _M.npy), notes.md.
- **Calibration at 3.80 PASS**: the LP certificate IS a kernel in this class; pair oracle max = −1.000000000 exactly,
  diag oracle min coverage 1.029676 (advisor's independent spot check 1.0300 — ours slightly sharper) ⇒ λ = τ/m_min = 10.49
  (= τ exactly for the min-mass-1 unscaled measure, as the theory says).
- **Bridge bookkeeping discovery**: condition (ii) must be stated for pairs of disjoint CLOSED squares (touching EXEMPT):
  a touching pair can share a boundary atom, forcing K > −1 there (seen live in calibration, K = −0.706 on a touching grid
  pair); the scale-shrink step of Theorem 1 produces closed-disjoint squares, so the exemption is sound — and necessary for
  ANY closed-indicator feature class.  No fixed positive gap can be assumed (gaps → 0 as s′ → s).
- **At 3.84 the 1181-atom indicator class does NOT reach λ < 11 (done-negative on the target)**: 13 cutting-plane
  iterations, 8044 rows; λ_sdp stalls at 11.05–11.13; the optimised diagonal is LP-shaped (corr(K(x,x), τ/m(x)) = 0.99,
  binding cells = a continuum of coverage-1.000 cells: corners, walls, interior tilts); the pair oracle finds a
  NON-CONVERGING stream of violations K ≈ −0.72…−0.86 (need ≤ −1), all interior mid-tilt (29–68°) barely-disjoint pairs —
  the ¼-structure region again.  Strongest float attack: maxdiag 10.4282 (at the min-coverage cell, m = 0.9687),
  maxpair −0.7163 ⇒ scaled fully-certified-in-float λ = 15.56 (worthless); honest class estimate ≈ 11.0–11.2 vs discrete
  ϑ′ 10.38 ⇒ the feature class (A16 risk R2), not the grid→continuum gap (R1), binds first, costing ≈ +0.7.  The kernel
  beats the LP form on the same atoms by ≈ 1.25 (λ_LP-form = 1 + τ/m_min = 12.38) — cross terms are worth a unit; the
  basis is too short by ~0.15.
- **A18-structure discovery (removes the 6-D pair verification!)**: in the subclass M = [[1, −wᵀ],[−w, τ·diag(w) + C]]
  with C ≤ 0 off-diagonal (diagonal free), K(x,y) = −1 + a(x)ᵀCa(y)/(m m′) ≤ −1 holds for EVERY pattern-disjoint pair by
  algebra, and strictly disjoint closed squares never share an atom ⇒ (ii) is UNIVERSAL, no pair oracle/verifier at all;
  the rigorous certificate reduces to rational LDLᵀ (M is a Gram matrix by construction here) + ONE verify_measure-style
  3-D cell B&B with a quadratic form.  Viability evidence: on the A15 c384 graph 80.15 % of the 1.11M edges share an atom,
  and dropping the 220,820 non-sharing edges leaves α = 10 unchanged (CP-SAT OPTIMAL).  Recommended A18: restricted class
  + atoms placed INSIDE the mid-tilt sliver-overlap regions (the non-sharing edges say where) + ~40 smooth D4 features
  interpolating the discrete duals' dominant eigenvectors (the indicator basis is constant on cells; the discrete Z varies
  within the tight-cell continuum — that is the missing 0.15).
- 3.85/3.86 not run (λ < 11 already fails at 3.84 in this class).

## 2026-08-19 — A18-restricted-kernel — the automatic-(ii) kernel class collapses to the LP: λ ≥ τ*(s), goal provably unreachable (done-negative, with THEOREM)

- **Task**: push A17's discovery D2 (M = [[1, −wᵀ],[−w, τdiag(w)+C]], C ≤ 0 off-diagonal ⇒ condition (ii) automatic for
  every pair of strictly disjoint closed squares — no 6-D pair verification) to λ < 11 at s = 3.84 by optimising atoms, w, C.
- **Main result — collapse theorem (proved in notes.md §3, machine-validated §4)**: with φ = (1, a(x)/m(x)) and the border
  tied to the normalisation weights, M ⪰ 0 ⟺ S := D − wwᵀ ⪰ 0 and K(x,x) = a(x)ᵀSa(x)/m(x)²; the class constraint makes S a
  PSD **Z-matrix** with entrywise margin (S_pq ≤ −w_pw_q). Every PSD Z-matrix is a limit of scaled-diagonally-dominant ones
  (u_ε = (S+εI)⁻¹1 > 0), and the dominance decomposition is pointwise monotone on 0/1 patterns ⇒ the class optimum sits on
  the boundary family S_u with **C ≡ 0** and D = diag(w_p(Σw_qu_q)/u_p): a TWO-MEASURE LP-form kernel,
  K_u(x,x) = (Σ_q w_qu_q)·(Σ_{p∈x} w_p/u_p)/m(x)² − 1. Cauchy–Schwarz with ν := w∘u then gives
  **λ = 1 + sup K ≥ Σν/inf_x ν(Q(x)) ≥ τ*(s)** — the plain Theorem-1 LP value, with equality at w = LP measure, u = 1.
  τ*(3.84) = 11.02 ⇒ **λ < 11 at 3.84 is impossible in the restricted class**; the automatic-(ii) kernel ceiling IS the LP
  ceiling ≈ 3.83. All no-pair-verification generalisations are blocked too: border σ < 1 (λ ≥ σ−1+τ*/σ, min at σ=1), free
  border/normalisation with pointwise ρ ≥ 1 (same C–S chain), positive entries on "inseparable" atom pairs (exist only for
  atoms exactly ON the container boundary — cap(p) = inward unit segment — and a closure/measure-zero argument restores the
  bound; no atom set in use has boundary atoms). Corollary: everything A17's full kernel gained over the LP (11.13 vs 11.38)
  is carried by POSITIVE off-diagonal mass on overlapping non-sharing (interior mid-tilt, ¼-structure) pairs — exactly the
  entries the restricted class deletes. The pair-free shortcut does not exist, at the root or at any case-tree node.
- **Machine validation**: tiny (28 atoms): identities to 7e-15, (ii)-automatic exact (K = −1.000000000 on 2460 disjoint
  pairs for diagonal D), monotonicity, SDP = u-family to 1.3e-4, SDP = row-LP τ* to 2e-6 at w = ν_LP. Medium (96 atoms,
  220 rows, cvxpy/Clarabel vs full-θ convex GP): **17.057096 vs 17.057133 (4e-5)**, and the SDP's own dominance vector
  u_ε = (S*+εI)⁻¹1 plugged into the two-measure formula reproduces the SDP value in the ε→0 limit (17.057097) — the
  collapse realised constructively. Two solver pitfalls documented (cvxpy fancy-index sign constraints; orbit-constant u
  is only WLOG on D4-closed/canon-deduped row sets).
- **Full-scale numerics** (convex GP over log u per D4 orbit + A17 diag oracle + two-measure ratio scan; no pair side
  exists at all): calibration PASS (LP-form identity λ = τ/m_min; at 3.84 the u=1 supremum independently reproduces A17's
  continuum min-coverage cell 0.968742). λ(u=1) → λ(u*): 3.80: 10.618 → **10.506** (τ* = 10.42); 3.82: 10.749 → **10.725**
  (τ* = 10.62–10.72); 3.84: 11.376 → **11.179** (τ* = 11.02). Optimising C (≡ u) strictly reduces λ everywhere — the
  dispatch's hoped-for datum exists — but the gain is precisely the certificate-margin slack and can never cross the LP
  floor. Binding cells at 3.80/3.82 are admissible-boundary WALL cells (coverage 1.0173/1.0220, sharper than A17's
  calibration attack found; A08's exact ≥ 1 untouched); at 3.84 interior mid-tilt cells (24–28°, 45°) — the ¼ region.
- **By-product**: every class member (including the plain LP certificates read as kernels) has a one-vector rational PSD
  certificate — M is a Z-matrix with M·(W, u)ᵀ = 0 — no rational LDLᵀ needed, ever, for LP-form kernels.
- **Consequence for the programme**: the only kernel-shaped route to λ < 11 at 3.84 is a HYBRID: Z-sign structure globally,
  D_pq > 0 permitted only for atom pairs inside the mid-tilt sliver-overlap region (A17 §6.1's 220k non-sharing edges,
  median depth 0.094), with the 6-D cell-pair verification restricted to pairs of squares both meeting that region — a
  pair table orders of magnitude smaller than A17's full pair space. That is the recommended A19; the 14-node ϑ′ tree
  faces the same theorem at every node (node LPs sit AT the budget), so it, too, needs genuine pair verification.

## 2026-08-19 — A19-hybrid-kernel — hybrid kernel (free R-block) buys ≈ nothing at reachable sizes (done-negative); **τ*(3.84) ≥ 11 PROVED by exact rational certificate**

- **Task**: the only kernel route A18's collapse theorem leaves open — Z-sign structure globally, D_pq unrestricted only
  for atom pairs inside a designated region R, so that (ii)-verification localises to R-meeting pairs; target λ < 11 at
  3.84; plus make τ*(3.84) ≥ 11 rigorous.
- **Class algebra (notes §1, machine-validated to 9e-15)**: D = diag(g) + F with supp F ⊆ R×R gives K(x,y) = −1 EXACTLY
  on every disjoint closed pair unless both squares cover an R-atom (automaticity), K(x,x) linear in (g,F), and
  M ⪰ 0 ⟺ one (k+1)×(k+1) cone by Schur (k = |R-atoms|) + per-atom scalar terms — a convex SDP at FULL 1181-atom
  resolution. F = 0 recovers A18's two-measure family exactly (gate (a) PASS on A18's own rows: 11.14406 vs their
  11.1438 at 3.84; 10.50617 vs 10.50627 at 3.80). The diag+R form equals the D4-invariant full hybrid (pair-orbit SDP)
  to 3e-5. NEW PITFALL for the lab list: with canon-deduped representative rows, a NON-D4-invariant matrix variable
  under-estimates massively (10.55 vs the true 14.47 on a tiny instance) — every SDP variable must be tied to the
  invariant subspace.
- **Result (same-rows F-on/F-off, Clarabel, the decisive comparisons)**: 3.84 (R = 148 central mid-tilt atoms from the
  binding-placement inventory): hybrid 11.14579 vs F=0 11.14406 — F buys −0.0017 = exactly the δ_p pair-margin cost;
  3.80 (gate (b), R = wall bands): 10.50369 vs 10.50615 — +0.0025 of the 0.086 needed to reach τ*(3.80) = 10.42.
  **Gate (b) FAILS; λ < 11 at 3.84 is not approached.** The optimal F is genuinely active (≈ half its entries positive,
  |F|max 0.36–0.55): the mechanism exists but the localised pair constraints price it at exactly its diagonal benefit.
  Mechanism (observed live): the automatic optimum's tight set is a coverage-1 continuum spanning the whole container;
  relieving the R-patch re-pins the supremum outside R (binding cell moved to a wall cell at it 1). Covering the whole
  tight structure needs k ~ 600+, beyond the convex (k+1)-cone form on this hardware (Clarabel memory death at cone
  ≳ 250–300, measured 6–9 GB alloc failures with silent exit; SCS at eps 3e-5 produced non-monotone junk λ — measured,
  rejected). Burden had it worked: 9.9 % of disjoint pairs are R-meeting (centres within 1.163 of centre).
- **Exact-graph diagnostic** (BM + EXACT finite pair oracle on the A15 c384 graph, ϑ′ = 10.38, LP = 11.000): the
  1181-atom pattern class stays feasible at λ = 10.35 through 33k exact pair rows; at 34.8k rows the value settles at
  **λ ≈ 10.4300** (diag clean, max pair violation −0.58 and closing; results/gclass384.json) — the indicator basis is NOT intrinsically
  ≥ 11 on the graph; the continuum tight-cell continuum plus solver scaling are what bind, not the basis.
- **τ*(3.84) ≥ 11, fully rigorous** (attempts/A19-hybrid-kernel/lp_floor_384.json + results/lp_floor_verify.json):
  18 closed unit squares — 4 corner squares (weight 1) + 10 upright ½-slide placements + the interior 61.5° pinwheel
  (4 × ½) — with rational centres (den 2^20), exactly-rational unit directions, weights summing to EXACTLY 11, and
  Σᵢ wᵢ·1[p ∈ Qᵢ] ≤ 1 verified for EVERY point by an exact Fraction quadtree B&B (10,009 boxes, depth 15, 0 undecided);
  weak duality then gives τ*(3.84) ≥ 11. Combined with A18's collapse theorem, **λ ≥ 11 at 3.84 for every
  automatic-(ii) kernel is now a fully rigorous statement**. (Two soundness traps found en route: the raw ¼-structure
  violates CLOSED-cover at touching lines — cover 1.125 — and coarse coordinate snapping creates 1.5-cover coincidence
  lines invisible to float scans; the pipeline handles both: η-inflated LP + edge-line probes + exact-B&B feedback.)
- **Programme consequence**: a small sliver-localised unrestricted block does NOT turn the automatic class into a
  sub-11 certificate — the ¼-cheat's kernel-killing cross terms live wherever the LP's tight structure lives, i.e.
  everywhere. Remaining kernel-shaped moves, in order: (1) D4-block-diagonalise the R-cone (isotypic blocks ~k/8 —
  pushes the convex form to k ~ 600; pure engineering); (2) A17-style Burer–Monteiro on the full hybrid with sign
  hinges (k = m = 1181, loses convexity guarantees); (3) leave the indicator class: smooth features interpolating the
  discrete duals' dominant eigenvectors (A17 §6.3-2, still untested).

## 2026-08-19 (late) — A20-scaled-hybrid: block-diagonalised R-cone; gates fail; the re-pinning is the continuum, not the solver
- **Step-1 engineering delivered**: the hybrid (k+1)-cone Schur block is now solved in D4-isotypic blocks
  (BlockHybridSDP; sparse per-irrep affine maps built from A16's projectors; blocks ≈ k/8, E ≈ k/4). Exactness
  validated two ways (random-member eigenvalue match 2e-14; A19's h384 values reproduced on identical rows to
  3.5e-5). Practical envelope on 32 GB: k = 480 with ~10k rows OK (10–25 min/solve); k = 597 (22.5k F-orbit
  variables) dies on memory. Every headline solve is verified feasible a posteriori from (g, F) — residuals
  ≤ 2e-7 — because Clarabel returns "optimal_inaccurate" throughout (the values are nonetheless real).
- **A19 correction**: A19's h380 hybrid number (10.5037, "F buys +0.0025 at 3.80") was a SILENT full-cone
  Clarabel stall. On A19's own h380 rows the class reaches ≤ 10.344876 (verified feasible member) — below
  τ*(3.80) = 10.42. The k ≤ 150 hybrid was never the bottleneck A19 measured at 3.80.
- **But the gates still fail, now for the right reason.** Low fixed-row values are properties of unconverged row
  sets: under a working solver+oracle loop with container-spanning R the value climbs monotonically back to the
  automatic class. 3.80 (k = 308): 10.4914 → 10.5052 vs F=0 10.5061 — F buys ≤ 0.001 of the 0.086 needed to
  reach τ*(3.80); gate (b) FAILS. 3.84 (k = 480, R inventory includes the exact LP-floor tight structure):
  8.5683 → 11.0860 over 5 iterations, oracle violations still +0.4/+0.8 at stop; same-rows comparison
  hybrid 11.085959 vs F=0 11.144051 (F buys +0.058 — 34× the k=148 gain, yet already above 11 and rising;
  A17's full-class BM equilibrated at 11.05–11.13, the same band).
- **Programme consequence**: the "solver couldn't reach big R" explanation of A19 is now eliminated along with
  the localisation hypothesis itself — what re-pins the hybrid class is the 6-D pair CONTINUUM (grid→continuum
  risk R1 in its sharpest observed form): every finite pair-row set leaves neighbouring near-tangent mid-tilt
  cells open, the convex optimum exploits them, the oracle closes them, λ climbs. The graph diagnostic
  (≈ 10.4 feasible on the c384 graph) stands — on GRAPHS; the continuum eats the difference. Remaining
  kernel-shaped move: leave the piecewise-constant indicator class (smooth features, A17 §6.3-2) — untested
  here per protocol (the 3.80 gate failed below the 0.02 threshold), and any such attempt must now expect the
  same continuum pricing unless the features change what the pair oracle can find (see A20 notes §3.4).

## 2026-08-19 — advisor — optimality roadmap dispatched (per PI)
- Pivot from fixed-s ladders to the optimality frame (PI's observation: 3.84-lemmas are vacuous if Trump is optimal;
  proofs must live at s' = 3.877083590… / s'+δ). Three parallel legs: A21 structure theorems at 3.88 (non-vacuous,
  constrain all near-optimal packings), A22 rigorous local optimality at Trump (Krawczyk + KKT — the s→s'⁻ endgame),
  A23 wastage/dead-area oracle (PI's integral constraint; the one killer whose strength may survive at s' in the
  mid-tilt band).

## 2026-08-20 — A22-local-rigidity — strict local optimality of Trump's packing CERTIFIED
- **The s -> s'^- endgame theorem is done**: in the explicit box N = {||z - z0||_inf <= 5e-4}
  around the 60-digit Trump configuration (34 coordinates: 11 centres + 11 angles + s), every
  feasible 11-square configuration has s >= s-hat, with equality exactly at the unique contact
  solution z-hat (Krawczyk-enclosed to 1e-50, itself a feasible packing, s-hat = octic root to
  1e-50).  Quantitative version: s <= s-hat + delta forces ||z - z-hat||_inf <= 155.7 delta.
- Method: curated smooth active set (degenerate flush/corner-corner contacts replaced by
  centre-distance rows ||c_i-c_j||^2 >= 1, valid by the support-function argument; corner-on-edge
  rows valid by an interval-checked corner-in-interior lemma); unique strictly positive KKT
  multipliers (min 0.01754) on a rank-34 subsystem chosen from the 4-dim multiplier freedom
  (3 wall redundancies + 1 pinwheel self-stress — one flush-pair row must always be dropped);
  68 closed-form rational positive-spanning certificates; an interval-MVT argument that needs
  no Hessian bounds (beta = 0.634 < 1 at r = 5e-4).  A second Krawczyk system with angle-equality
  rows proves z-hat's exact structure (uprights exactly cornered, all five tilts equal), which
  in turn makes z-hat's feasibility and the dropped rows' vanishing exact.
- Verification: standalone recheck.py (mpmath.iv + fractions only) re-verifies every interval
  claim from results/krawczyk_cert.json in ~40 s; corruption gates (z0 by 1e-3 and 1e-8, mu
  sign flip, edge-index tamper) all fail loudly.
- Remaining gaps to full formality: mpmath.iv trusted; symbolic identification s-hat = octic
  root (Q(t) bridge) not re-proved; D4 x S11 relabelling reduction stated, not formalised; not
  in Lean (the JSON was designed integer-interval-replayable for a future A06-style port).
- Programme consequence: the optimality frame now needs only the GLOBAL half — exclude
  s <= s-hat outside N/(D4 x S11).  Any future bound s(11) >= s-hat - delta localises all
  near-optimal packings to 156 delta of Trump inside N.

## 2026-08-20 — A23-wastage-oracle (geometry postdoc) — the PI's area ledger BITES: the integral pinwheel is dead, at 3.86 and at s'
- Built the dead-region certifier (`attempts/A23-wastage-oracle/dead_region.py`): D is DEAD for a partial
  configuration H if no unit square Q ⊂ [0,s]² with int(Q) ∩ int(P_i) = ∅ meets int(D).  3-D (t,cx,cy)
  interval B&B, exact-Fractions and float-guard modes; sound discharges only (admissibility clip;
  separating-axis disjointness with exact cos/sin enclosures; overlap by WITNESS POINT p ∈ int(P) exact +
  p ∈ Q over the whole box — the tempting "SAT projections overlap on all axes" test is necessary-not-
  sufficient and was rejected).  Budget lemma: interior-disjoint dead regions satisfy Σ area ≤ s² − 11 in
  any 11-packing extending H (one-line proof in notes §1); deadness is monotone under adding squares, so
  certificates persist down a branch tree.  Validated on hand cases incl. a genuinely instructive negative
  (a 0.9-wide channel is NOT dead where 45–60° corners can dip through the slot; certifier found the
  escape).  Exact rechecks: every float-mapped cell list tested so far re-verifies in pure Fractions with
  0 failures; independent random-legal-placement adversarial tests: 0 hits.
- Wastage tables (s = 3.85): one mid-tilt square near a wall strands 0.19–0.47 of certified dead area
  (θ ∈ {20..35}°, d ∈ {0..0.2}, monotone in both); in a container corner 0.34–0.61.  Core-box-UNIFORM
  version (PlacedBox: certificates hold for EVERY placement of an A14-style core [0.72,0.74]²×[39,41]°)
  0.5285, all 410 cells exact-PASS — the object that composes into A14's verify_case semantics.
- Ledger on the real obstruction (s = 3.86, budget 3.8996): four flush corner squares strand 0.0000
  (why A14's corner stage was barren).  But A12's interior ¼-pinwheel, taken INTEGRALLY: the adjacent
  33° pair (exactly disjoint at the raw support rationals) strands 1.8834 — 48 % of the budget at depth
  2 — via a wall-shadow mechanism the coverage LP never sees; the full 4-cycle strands **6.5488 > budget:
  killed at depth 4, margin 2.65; EXACT-Fraction subset 4.4032 > 3.8996, 0 cell failures** (Lemma 2: any packing containing it has ≤ 8 squares; sharp — pinwheel
  + 4 corner squares is legal and meets 0 dead cells).  A 10-square A12-style realisation leaves no legal
  placement anywhere (entire free region certified dead, 4.80).
- **At s' = 3.8770836 (budget 4.03178): the scaled 4-cycle strands 6.5758 (float), and the kill is
  EXACT — a 176-cell subset re-certifies in pure Fractions to 4.5056 = 2816/625 > s'² − 11 (0 failures):
  machine-checked theorem, no packing of 11 (indeed ≥ 11) unit squares in [0,s']² contains it.**
  A continuum PlacedBox-pair version (cores centres ±0.01, θ ±0.9°) still strands 1.3837 uniformly.  First argument in the programme that kills a
  mid-tilt structure at the optimality side.  Role going forward: an independent, cheap (minutes/node,
  parallel) kill test inside the case tree whose strength GROWS with depth, complementary to the node LP
  whose slack shrinks; not a root-stage killer (single squares strand ≤ 0.6).  Recommended: composed
  pilot on A14's node-3 pinwheel children; NO-zone discharge; PlacedBox sweep to lift realisation kills
  to continuum statements.

## 2026-08-20 — A21-structure-388 (consolidated by advisor; agent hit spend limit mid-write-up)
- CERTIFIED at s = 97/25 = 3.88 > s' (non-vacuous — constrains all near-optimal packings incl. Trump's):
  THM1 corner occupancy (total 10.5611 < 11, exact verifier PASS) and THM2 side-zone occupancy (total 8.7453,
  margin 2.25, PASS). Zones: corners [0.5,1.1]² + images; sides 0.6-bands on the mid-walls.
- NOT certifiable at 3.88: per-corner (LP ~10.7, above certifiability ceiling), per-side (verifier FAIL at 10.937),
  orientation windows (FAIL ~10.96–10.98; the [0,5]∪[40,50] window is alive via Trump itself; [0,5]∪[43,47]∪[85,90]
  alive via ~43° near-packings at ≈3.880). All verdicts from certs_wip/*.report.json on disk.
- Roadmap status: optimality = certified local theorem (A22) + structure scaffolding at 3.88 (A21, this) +
  wastage killer for the mid-tilt band (A23). Global stage remains the open problem; next composed pilot =
  wastage + coverage on A14 pinwheel children.

## 2026-08-20 — advisor — A21 late certification landed (thm3_orientation_pm18: PASS)
- Detached certify run finished after the agent was killed: every 11-packing at side <= 3.88 has a square oriented in
  [0,18] u [27,63] u [72,90] deg (total 10.9748 < 11, 292228 boxes, 0 witnesses). I.e. the pure narrow-tilt family
  (all squares between 18 and 27 deg) is DEAD at 3.88. Recorded in REGISTRY + docs/results.md.

## 2026-08-20 — advisor — campaign launched (PI raised spend limit)
- A24-composed-tree: the headline attempt — case tree at s = 96/25 = 3.84 with TWO independent node-kill tests
  (T1 coverage LP, T2 wastage ledger vs budget 2341/625 = 3.7456). Target: certified s(11) >= 3.84, which the pure
  measure LP provably cannot reach (A07 ceiling 3.83; A19's exact value-11 fractional packing at 3.84 makes the
  impossibility rigorous). Fallback target 3.83 (still a record over the lab's 3.82).
- A25-wastage-atlas: certified continuum dead-area atlas over (centre-box x tilt-box) cells + pair atlas in the
  mid-tilt band, with a query API for A24. Key efficiency idea: certified LOWER bounds only, capped candidate
  regions, early exit.
- Both agents instructed for token frugality (detached compute, single blocking wait, one final report).

## 2026-08-20 — A25-wastage-atlas — continuum wastage atlas delivered (done-success)
- **A23's dead-region oracle is now a lookup table over hypothesis BOXES.** `attempts/A25-wastage-atlas/query.py`
  is A24's import surface: `Atlas.lookup(cx_box, cy_box, theta_box) -> (certified rational lower bound on the
  stranded/dead area, list of realising rectangles in the query frame)`, D4-aware, 0 when uncovered.
  `disjoint_regions()` checks the cross-square interior-disjointness side condition of A23's budget lemma.
- Atlases shipped: coarse single at s = 96/25 and at s' = 3.877084 (1310 cells each, theta 0-45 in 3 deg bins,
  centre boxes 0.15); FINE single at 3.84 (centre 0.075, 5 deg bins, mid-tilt, 1839 cells); pair atlas (330 pairs,
  mid-tilt, box-centre separation 1.00-1.25, realisability-flagged). Cost **2.9-8.9 s per cell** vs A23's ~1 CPU-day
  estimate: capped candidate windows (wall/corner shadow strips, made pairwise disjoint by rectangle subtraction),
  coarse 1/8 -> 1/16 tiling visited in level order with a work budget, and a midpoint-realisation negative filter.
  Every cap only drops tiles, so the numbers stay certified LOWER bounds.
- **Headline: min k = 3.** Any node fixing three mid-tilt squares in [1.275,1.35]^2 x [15,20] deg and its two
  90 deg rotations has certified dead area 4.7930 > 3.7456 = s^2-11 at 3.84; the coarse-cell version gives
  4.2070 > 4.0318 **at s'**. k = 2 is out of reach (best two-square value 3.1953). Both witness families are inside
  the exact-Fraction re-certified set (58 entries / 5083 tiles, **0 failures**), so the statement is exact.
  Compare A23: k = 4, and only for four exactly fixed placements.
- **Two findings A24 must act on.** (i) The certified value is a THRESHOLD in core-box size: same centre, mid tilt,
  point 1.74 / 0.15-box 0.32 / 0.075-box 1.49 / 0.01-box 1.65 — while tilt width is nearly free (3 deg -> 1 deg buys
  2 %). Branch the CENTRE to 0.075 before querying. (ii) The strongest single-square wastage is not the flush-to-wall
  square of A23 but the square parked ~1.2 from a corner, which strands an L-moat of 1.40-1.60 — over a third of the
  whole budget from ONE square.
- Coverage/limits: 35 % (coarse) / 43 % (fine) of mid-tilt cells carry a useful value >= 0.3, but the median cell is
  only 0.20/0.29 (typical-case k ~ 19/13) — the ledger is decisive in the near-corner band and useless generically.
  Deep-interior cells are genuinely 0 (verified, not assumed). The atlas is essentially s-independent on [3.84,3.88];
  only the budget moves.
- Corrections to the dispatch: the D4 fundamental domain is quadrant x theta<=45 (NOT octant x theta<=45, which
  double counts, |D4| = 8 = 4 x 2); and 54/330 pair cells are NOT realisable — max centre distance >= 1 is necessary
  but not sufficient for two tilted squares — so they are flagged and excluded, a pair atlas without that flag
  manufactures vacuously-true kills.


## A24-composed-tree — the two-kill-test case tree at 3.84 (done-negative, two new certified theorems)

Composed A14's coverage LP (T1) with A23/A25's wastage ledger (T2) into one tree at s = 96/25 = 3.84
(budget for T2: s^2 - 11 = 2341/625 = 3.7456). **3.84 is NOT certified; the record stays 3.82.** But the
attempt produced two certified theorems, the first YES-branch kills in the I-L6 line, and the first
affordable cost estimate for closing 3.84.

- **Composition + validation.** `kill_tests.py` maps an A14 `Hyp` to A23 certifier data: YES boxes become
  `PlacedBox` cores with OUTWARD rounding (so the certificate is uniform over the whole box), and NO-families
  become a **new discharge rule** in the dead-region B&B (A23 listed this as future work) — under the node
  hypothesis every packing square avoids the family, so a parameter box inside it holds no legal placement.
  Interior-disjointness of the dead regions is structural (one quadtree, one window) and audited exactly.
  Reproduces A23 to the digit: corners4 0.0000, corner_box 0.5285, plus new NO-zone unit tests.

- **THEOREM A24.1 (certified, exact `verify_case.py` PASS).** Every packing of 11 unit squares in a square of
  side <= 3.84 has a square whose centre lies in the closed **interior** zone [11/10, 137/50]^2. Measure total
  1030019/125000 = 8.240152 < 11, **margin 2.76** — the largest case-LP margin at 3.84 (A14's corner lemma:
  0.88). The zone ladder is sharp: cw = 0.8 gives tau = 10.21 (not certifiable), cw = 1.0 gives tau = 11.000
  with maxcov = 1.000 (the quarter-structure re-appears).

- **THEOREM A24.W (certified, pure Fractions, 0 cell failures).** No such packing has four squares in the four
  core boxes (c_i +- 0.03) x [30 deg, 36 deg] on the rigidly translated A12 pinwheel: certified dead area
  **2416/625 = 3.8656 > 2341/625**. The SAME node is independently killed by T1 with an exact coverage
  certificate (total 103/25 < 7) — the first node in the programme killed by a coverage certificate AND by an
  area certificate.

- **Wastage scaling law at 3.84** (`sweep.py`), k translated-pinwheel cores of centre half-width d:
  k=1 0.92 (exact) / 0.68 (d=0.01); k=2 2.60 / 2.05 / 1.42 (d=.03) / 0.98 (d=.06); k=3 **4.36 exact = DEAD**;
  k=4 6.60 / 5.72 / **4.45 (d=.03) = DEAD** / 3.47 (d=.06). Strongly super-additive — and there is a **cliff**:
  at d = 0.10 the certified area collapses to exactly **0** (independent confirmation of A25's 0.075-vs-0.15
  threshold). Cross-validation with A25's atlas on a level-1 box: A24 1.1196 (cells 1/8) -> 1.2260 (1/32) vs
  atlas 1.2812 — two independent certifiers agreeing.

- **The first YES-branch kills.** A14's blocker (a corner square fixed EXACTLY still leaves tau* = 10 = budget,
  so the corner stage can never close) does not carry over to the interior. T1's power at an interior node is
  governed by the rational core half-side a = (1/2 - d sqrt2)/(1 + dt): a >= 0.35 kills (slack -0.7 ... -2.0),
  a ~ 0.31 is marginal, a <= 0.28 is alive — i.e. centre half-width <= 0.05 and tilt window <= 15 deg.

- **T1/T2 split: 30 kills, ALL of them T1; T2 fired at ZERO tree nodes.** The ledger needs k >= 3 cores of
  centre width <= 0.075, and by that depth T1 has already won. T2's role remains A23's: killing *realised*
  mid-tilt structures whose quarter-weight fractional versions hold tau* = 11 and are invisible to every LP.

- **Frontier and cost.** Root lemma + ONE D4-reduced exhaustive level (216 boxes of 0.1025^2 x 15 deg over the
  fundamental triangle {1.92 <= y <= x <= 2.74}; cover verified exactly in rationals). 106/216 solved at a
  150 s LP: 26 converged deaths (slack -1.0 ... -2.0), 4 robust deaths, 76 undecided of which **3 genuinely
  alive (tau up to 10.018)**; **15/15 attempted leaves certified** by the exact verifier. Closing needs
  converged LPs (~36 CPU-h) + leaf certification (~15 CPU-h) + one refinement level under the survivors:
  **100-300 CPU-hours**, two orders of magnitude below A14's 10^4-10^5 estimate for the wall-first tree. That
  is the first affordable route to 3.84 this programme has had — but the three alive boxes mean termination is
  not guaranteed, so it is a gamble, not a plan.

- Package `attempts/A24-composed-tree/certs/casetree_3.84/` with `manifest.json` and `verify_tree.py`
  (re-verifies the root, the cover logic in rationals, every leaf, and the T2 certificate; OVERALL PASS,
  CLOSURE 15/216 — the verifier reports honestly that the tree is open).
- D4 note (after A25's correction): A24 reduces the CENTRE to an octant and keeps ALL theta (relative size
  1/8) — equivalent to A25's quadrant x theta <= 45, and not the unsound octant x theta <= 45.


## 2026-08-21 — A26-wall-ledger — the GLOBAL boundary ledger: counting works, charging has an exact zero (done-negative, three theorems)

- **The PI's reformulation, tested.** A tilted lattice of unit squares tiles the plane with zero waste, so waste is
  produced only where a same-tilt block TERMINATES (wall wedge / inter-block sliver): evaluate a boundary functional
  GLOBALLY on all 11 squares instead of summing A23/A25's local pockets. Counting half: success. Charging half: dies
  on a zero. Net: **no kill at 3.84, 0 of A24's 3 live level-1 boxes, 0 at the root** — but the failure is now exact.
- **Lemma B0 (the right formulation).** A unit square avoids the width-w boundary band iff its centre is
  >= w + h(theta) from every wall, h = (cos+sin)/2, i.e. iff the square lies in the CONCENTRIC square of side
  B = s-2w. So the band-avoiders are a packing one level down and
  **m(w) = max{ n : s(n) <= s-2w }** — exact wherever the small-n constants s(n) are known (n <= 9), and
  unavailable exactly when B >= 3 because it then needs the OPEN s(10). Pleasing self-similarity.
- **Theorem A26.1 (elementary, exact, self-contained; four-line proof).** If (2B-1)^2 < 8 then at most ONE unit
  square fits in a square of side B. [SAT: |u.(c1-c2)| >= 1/2 + h(psi) >= 1 for an edge normal u of Q1, while
  |u.(c1-c2)| <= (B-h1-h2)(|cos|+|sin|) = 2 h1 (B-h1-h2) <= (B-1/2)^2/2.] At s = 96/25, w = 1: (2B-1)^2 =
  4489/625 = 7.1824 < 8. **=> at most one of the 11 squares avoids the width-1 band, i.e. >= 10 MEET it** —
  stronger than the dispatch's pigeonhole target (>= 9), and it also holds at s' (7.5854 < 8) and at every
  s < 3.914213. Side effect: re-proves s(2) >= 1/2 + sqrt2 from scratch.
- **Theorem A26.2 + the R-profile.** With R := dist(centre, nearest wall) - h(theta): #{R >= w} <= m(w). At 3.84
  that is <=1 above 0.93, <=4 above 0.5665 (s(5) = 2+1/sqrt2), <=5 above 0.42. Hence **>= 7 of the 11 squares have
  centre within 0.64 + sqrt2/2 = 1.34711 of a wall.** TIGHT against Trump: his R-profile is
  (0.9840, 0.5676, 0.5486, 0 x 8), and the E1 threshold at s' is 0.98144 — exactly one square above it. ZERO Trump
  squares avoid the width-1 band, as the dispatch predicted.
- **The charged wall functional (charge.py)** does unions properly: A25 atlas cells + exact rational cross-square
  rectangle-disjointness (max-weight independent set, bitmask-exact), validated against every published A23/A25
  number (L-moat 1.4648, fine 1.5977, d=0.45 head 0.5078, deep interior 0, flush corner 0, D4 round trip).
- **The killer fact: the functional has an EXACT ZERO.** Over the 1070 admissible band cells the minimum certified
  charge is 0.0000 (16 cells at d = 0.45, theta in [0,6] deg) and the smallest positive value is 0.0039. A flush
  near-upright wall square strands NOTHING — an axis-parallel block terminating on an axis-parallel wall makes no
  wedge. Verified to be a computed zero, not an atlas gap (the same (i,j) cells carry 0.004-0.027 at theta 6-15 deg).
  That configuration is 6 of Trump's own 11 squares. **min-over-profiles total charge = 0.0000 vs budget 3.7456.**
  Best certified per-square charge with tilt AND depth floors: 0.1602; the requirement is 0.5351 (n = 7 forced by
  counting) or 0.9364 (n = 4, one per wall). Short by 3.3x-5.8x, from a base of 0.
- **Reality check:** the certified wall charge of Trump's ACTUAL packing is 0.8672 = 21.5 % of his budget 4.0318 —
  the calibration any ledger of this type has to beat in the WORST case, not the best.
- **Theorem A26.3 (decisive negative, and the cheap by-product).** The band lemma is a family of region-rank cuts
  (I-L8): sum_{R(p) >= w} y_p <= m(w), plus tilt cuts, band x tilt cuts, A21 zone ranks. Evaluated on A19's EXACT
  rational value-11 fractional packing at 3.84: **0 violations**, and several cuts are TIGHT (weight 1 = m(w) in the
  deep interior; weight 9 = the near-upright cap; weight 1 = each corner-zone rank). So that y stays feasible for the
  cut-strengthened LP: **tau_cut(3.84) >= 11 and the boundary-band/tilt/zone rank-cut family cannot break the pure-LP
  ceiling.** The I-L8 boundary-band instantiation is closed.
- **The weak link, quantified AND CLOSED (as the PI predicted, but worse).** Elementary tilt forcing: two squares
  with tilt within eps of axis-parallel have ||Dc||_inf >= 1/(cos eps + sin eps), centres in a square of side s-1, so
  an NxN pigeonhole gives at most N^2 whenever (s-1)(cos eps + sin eps) < N: at most 9 within **3.326 deg** at 3.84
  (2.503 deg at s'), then the bound jumps uselessly to 16. But A24's own LP probe already does better and IS a valid
  rank bound (the tilt-<=-eps squares of any packing are themselves a packing in that class, so their number is
  <= floor(tau_B)): "NO square with theta in [10,80]" gives tau = 9.358 => **at most 9 within 10 deg**. And
  tiltmax.py (numerical, witness confirmed by exact float SAT) finds **TEN unit squares of tilt <= 15 deg that DO
  fit in [0,3.84]^2**, with the 9-vs-10 threshold at **eps* ~ 12 deg**. So the provable ceiling (10 deg) is within
  2 deg of the truth (12 deg): **tilt forcing is maxed out, the best obtainable statement is "at least 2 squares have
  tilt >= 10 deg", and the ledger's requirement of ~7 charged squares is unreachable IN PRINCIPLE.** Conjecture
  A26.T ("at most 9 within 28.5 deg" - the cheapest cut that would have cut off A19's solution) is REFUTED by a
  10-square witness of max tilt 23.36 deg; only the cap-10 version survives, and that is a restricted form of the
  main conjecture. General reason, worth recording: **LP-certified rank bounds tau_B(R) can never be violated by a
  feasible fractional packing** (restrict y to R), so only a COMBINATORIAL bound strictly below tau_B can cut.
- Independent numerical validation of the cited constants (same searcher): 2 squares in 1.84 / 1.95 no; 4 in 2.00
  tangential; 5 in 2.56 no; 5 in 2.71 tangential; 6 in 2.99 no - s(2)=2, s(4)=2, s(5)=2+1/sqrt2, s(6)=3 reproduced.
- **Next (ranked).** (a) FREE, today: use the R-profile as an LP-less pruning rule in A24's interior-first tree -
  "two squares both with R >= 0.93" is dead by Thm A26.1, "five with R >= 0.5665" by Thm A26.2; (b) ~1 CPU-hour:
  formalise Lemma B0 + E1 in Lean - four lines of rational geometry, no certificate file, and it yields a real
  structure theorem at 3.84 AND at s'; (c) the only surviving ledger direction is a CORNER-occupancy statement
  ("how many squares must sit at depth 0.9-1.35 near a corner?", where the charge is 1.40-1.60 and 3 suffice) - an
  LP question, not a counting one; (d) do NOT refine the wall atlas and do NOT chase tilt forcing past 12 deg.

## 2026-08-24 — A28-lean-batch: Mathlib installed; **the upper-bound bridge lemma is a theorem over ℝ²**

- **The headline.** `lean/PackingCert` only ever proved `checkPacking Data.trump11 = true` — a `Bool`
  computation, with the geometric meaning left as an assumed "bridge lemma" (A06 §5). That gap is closed:
  ```
  PackingCert.eleven_unit_squares_in_3877084 :
    ∃ Q : List (Set (ℝ × ℝ)), Q.length = 11 ∧ (∀ q ∈ Q, IsUnitSquare q)
      ∧ (∀ q ∈ Q, q ⊆ Set.Icc (0:ℝ) (969271/250000) ×ˢ Set.Icc (0:ℝ) (969271/250000))
      ∧ Q.Pairwise Disjoint
  ```
  **Axioms: `[propext, Classical.choice, Quot.sound]` — no `native_decide`.** The certificate is evaluated
  by kernel `decide` (`trump11_ccw_ok_kernel`, axiom-free, `maxRecDepth 10000`, 18 s), so the entire chain
  from the 75-bit integer data to the real-plane statement is kernel-checked. `s(11) ≤ 3.877084` is now a
  statement about ℝ², not about a Boolean.
- **Mathlib finally installed.** `lake exe cache get` succeeded: 8691 `.ltar` files in 6 min 15 s;
  6.52 GB `.lake` + 0.41 GB download cache + 3.02 GB toolchain v4.34.0-rc1. Our modules then compile in
  seconds (Bridge 15 s, Band 22 s, Trump11 18 s). **All of it was deleted at the end** — free space on this
  machine hit **0.29 GB** mid-run (A27's output; Lean's own incremental builds cost ~10 MB) — returning
  ~10 GB. The `.lean` sources are committed and one `lake exe cache get` rebuilds everything.
- **How the bridge is proved, and why it is short.** Following A06's own suggestion, a square is
  `sqSet p0 e = {p0 + a·e + b·e⊥ : a,b ∈ [0,1]}` rather than a `convexHull` — this needs **no** convexity
  API at all. Two lemmas carry everything: the algebraic identity
  `rdot (aff p0 e a b) n = (1−a)(1−b)d₀ + a(1−b)d₁ + ab·d₂ + (1−a)b·d₃` (a convex combination of the four
  corner projections, pure `ring`), and `aff_sqdist` (the parametrisation is a Euclidean isometry, so the
  set really IS a congruent copy of `[0,1]²` — proved, not asserted). Then
  **`disjoint_of_strictlyBelow`**: if along ANY vector `n` all four corners of one square project strictly
  below all four of the other, the two CLOSED squares are `Disjoint`. No unit-length, no edge-direction
  hypothesis — which is the precise sense in which the checker's choice of candidate axes affects only
  completeness, never soundness. Containment is the same machinery with `n = (1,0), (0,1)`; the 55 pairs
  lift to `List.Pairwise Disjoint` through `allPairs_pairwise`.
  One concession: `checkPackingCCW` (the `+n` orientation branch of `isUnitSquare`), with
  `checkPackingCCW_imp` back to the original checker; all 11 squares of the certificate are CCW.
- **A26.1: formalised, but with the constant lost — and a better constant found in the process.** Mathlib's
  separating-hyperplane theorem hands you *a* direction; A26's E1 needs an **edge normal** of one of the
  squares, which requires the H-representation of the Minkowski sum of two squares (an octagon). Not
  attempted. Running the same chain with an arbitrary direction gives
  `two_unit_squares_side_ge : 1 + √2/2 ≤ B` (**1.7071** vs A26's **1.9142**), hence `band_96_25`: at
  s = 96/25, at most one square avoids the width-**1.08** band (A26: width 1).
  **But** — running A26's chain WITHOUT its final relaxation `2h₁(B−½−h₁) ≤ (B−½)²/2`, and minimising over
  the separating direction α and both tilts, gives **exactly 2.0000** (grid 361×361×721, minimiser
  θ₁ = 0°, θ₂ = 90°). So even the WEAK form of SAT already implies `B ≥ 2`, which is **sharp** (= s(2)) and
  strictly stronger than E1. It decouples completely into one two-vector inequality:
  **(A28.★)  `|u·e| + |u·e⊥| + ‖u‖₁·‖e‖₁ ≥ 2‖u‖₁` for unit `u, e ∈ ℝ²`** (verified numerically to −4.4e−16,
  equality at θ ∈ {0°, 90°}). It is NOT formalised: 6-fold sign split with two quadratic constraints, and
  the tight branches need their own factorisations (`e₁+e₂−1 = 2e₁e₂/(e₁+e₂+1)`, `1−e₁ = e₂²/(1+e₁)`) —
  one `nlinarith` does not do it. **Payoff for whoever does: A26.1 with band width (s−2)/2 — 0.92 at 3.84
  instead of 1 — and valid for every s < 4 rather than s < 3.9142.** Cheapest high-value item in the Lean
  queue.
- **A22's Krawczyk certificate cannot be replayed in Lean as it stands, and the fix is on A22's side.**
  `krawczyk_cert.json` stores the 11 tilts as raw rational ANGLES, and all 36 wall/edge rows evaluate
  `c_i + R(θ_i)(±½,±½)`; a decidable checker would therefore need certified rational enclosures of cos/sin
  (Taylor with rigorous remainder) built from scratch — a bigger project than the checker itself. Re-emit
  the certificate in `t = tan(θ/2)`, the parametrisation `certs/`, `gen_cert_lean.py` and `MeasureInt.lean`
  already use, and every constraint row becomes a rational function: a `checkKrawczyk` in the existing
  all-`Int` MeasureInt style is then a direct 1–2 day port of `recheck.py`'s [K]/[E]/[B] gates.
- **Still assumed after A28** (in decreasing value): (A28.★); the Hahn–Banach step that would turn
  `Band.lean`'s separation hypotheses into "interior-disjoint" (needs `Convex (sqSet p0 e)` — easy — plus
  `geometric_hahn_banach_open` and a Riesz identification); the **lower-bound** measure bridge lemma
  (`checkMeasureI c = true ⇒ μ(Q) ≥ 1 for every unit square in [0,s]²`), still A06's 3–5 day estimate; the
  A22 replay. Notes: `attempts/A28-lean-batch/notes.md`; theorem/axiom table: `lean/README.md`.

## 2026-08-25 — A27-close-384 (rigorous-computation postdoc) — done-negative, but the tree moved a long way

- **Verdict: s(11) >= 3.84 is still NOT certified.** A24's interior-first case tree went from **15/216** to
  **123/216** discharged level-1 cells, with **162 exact leaf certificates** (`verify_tree2.py`: root PASS,
  cover exact, 162 PASS / 0 FAIL). 93 cells remain open.
- **All 216 level-1 node LPs solved** (A24 had 106, each at a 150 s limit): 65 converged deaths, 20 proved
  `alive(LP)`, 131 undecided at the 700 s limit — but **117 cells are certified dead by the exact verifier**,
  because an unconverged LP can still yield a certifiable measure after the EPS_GEO = 3e-3 re-solve and the
  witness-feedback rounds. The exact verifier, not the LP status, is the arbiter.
- **New rigorous negative, `alive(LP)`:** tau >= budget AND the column oracle exhausted (maxcov <= 1+1e-3) means
  the fractional packing is dual-feasible for the whole atom space, so tau_LP(box) >= budget: such a node can
  NEVER be killed by the coverage LP at that box size. 20 level-1 cells are in this class. A24's "alive" label
  conflated this with "LP not converged"; the two are now separated.
- **The three boxes A24 left alive are dead.** Cells 95 and 101 close at level 2 (8/8 children certified,
  tau 8.61-9.00). Cell 89 needs level 3: two of its children (89_010, 89_111 — the near-axis-parallel tilts at
  centre ~(2.38,2.38)) sit at tau = 10.000000 with maxcov = 1.000000, i.e. provably LP-unkillable at
  0.05125 x 0.05125 x 7.5 deg; a third (89_101, slack only -0.325) fails certification. All 24 grandchildren
  have tau in [7.03, 9.00] and all 24 certify. Cell 84 = sigma(cell 89) is discharged for free.
- **Soundness gap in A24's verify_tree.py, found and closed.** `verify_case.py` proves a statement about the
  rational CORE square; the step "every unit square with (centre, theta) in the box contains that core" was
  float arithmetic inside the certificate builder and was never machine-checked. `verify_tree2.py` now checks
  it in exact rational interval arithmetic (worst projection 0.468-0.489 against the bound 0.5, i.e. the
  construction has 2-6 % slack). It also re-parametrises the tree by t = tan(theta/2), so every cut, every
  8-way tiling and the diagonal symmetry sigma(t) = (1-t)/(1+t) are RATIONAL — pi never enters the verification.
- **Diagonal symmetry machine-checked and used:** 31 exact transfers (29 of them discharging the entire
  sub-tree under cell 84 from cell 89's). The naive transfer fails by ~7e-8 because the t-endpoints are
  outward-rounded to denominator 2^24; checking the mirror's core against the sigma-IMAGE box instead of the
  mirror's own box makes it exact.
- **The free A26 band pre-filter is provably inert on this tree** (0 CPU, 0 kills): A26.1/A26.2 and the
  sharpened A28.* threshold w* = 0.92 all cap the number of squares with band clearance >= w at >= 1, and every
  node of an interior-first tree fixes exactly ONE square. It would only pay in a tree with 2+ cores per node.
  T2 (the wastage ledger) skipped per node for A24's measured reason (a single core strands <= 1.2812 of the
  3.7456 budget); A24's 4-core pinwheel certificates are still carried and re-checked.
- **Measured cost to finish:** ~340 CPU-hours over ~1200 more nodes (branching 1 -> 8 -> ~0.5 surviving
  grandchildren), no new mathematics. Certification, not the node LP, dominates at the margin; the two cheap
  wins available are (i) stop grinding cells that the `alive(LP)` test already condemns and refine immediately,
  (ii) warm-start each child's certificate from the parent's converged dual.
- Machine was powered off mid-run; everything is checkpointed and the full exact re-verification after restart
  passed with 0 failures.

## 2026-08-26 — pivot: A29 paused, T3 pilot dispatched (A30), drain lemma v2
- PI question: is finishing 3.84 necessary for the endgame (s(11) = s*)? Advisor answer: NO — a
  container-side lower bound prunes no configuration cells of the exclusion program; the tree's only
  transferable value (exact bridge, cell machinery, Krawczyk toolkit) is already banked. 3.84 is a
  standalone record + insurance, ~2 days of compute. PI decision: pause A29 (fully resumable, 179
  certs on disk), pivot compute to the T3 pilot. Resume at <=6 workers if T3 stalls (9 workers OOM'd
  the machine).
- drain_lemma.md v2: D3 (KKT + degenerate taxonomy TODO) REPLACED by D3′ (Fritz John per selection):
  smooth selection NLP = containment (no selection needed) + selected separation with dominance rows
  (S-feasible => disjoint; every z in D0 is S-feasible for some menu selection; ties covered by
  membership in several selections). FJ needs NO constraint qualification, so the corner-corner /
  flush taxonomy obligation is discharged entirely; the only residue is the lambda0 = 0 branch, a
  COST issue (split the cell), not soundness. T3 now sound on D1 + D2 + D3′ with no outstanding
  proof debt.
- A30-t3-pilot dispatched (Opus): P1 reproduce A22's root isolation inside the new harness, P2
  exclusion on an offset cell, P3 menu-size + per-selection cost on a generic cell; report
  extrapolated full-cover cost at s0 = s* and every heuristic shortcut taken.
- Also this session: docs/plain_language_guide.md written for the PI; A29 resume bug (FAIL markers)
  and a provisional-certificate soundness bug found and fixed (fb9272a) after the PI caught the
  retry behaviour in the logs.

## 2026-08-26 — A30 pilot verdict: engine works, coordinate cover dies; structure-first reformulation
- A30 (5.5 min wall!): per-branch FJ machinery validated against A22 (rows to 2.6e-30, min-lambda
  0.017542 vs 0.01754; isolates Trump at h <= 2.4e-4). Three corrections to drain_lemma v2 found and
  advisor-verified -> v3: C1 FJ sign (v2 unsatisfiable everywhere - blocking), C2 D2 vacuous
  (centroid-shrink repair), C3 separation-row form. New preferred test (c1): Gordan/Farkas direction
  certificate, exactly first-order-complete, ~2 ms/selection, lambda0=0 covered free.
- Decisive negative: discharge-radius/cell-width ratio c ~ 1.86 is SCALE-INVARIANT => ~c^33 ~ 8e8
  surviving cells around EVERY critical point at every refinement depth; >= 1e5-5e7 CPU-h floor for
  Trump's shell alone; D2 reach at s* is zero. T3-as-coordinate-cover rejected: the blow-up is
  dimensional, not algorithmic.
- Reformulation (validates the PI's earlier contact-graph proposal): branch on selection/contact
  STRUCTURE at the top (finite combinatorial menu, pruned by counting lemmas + the stress lemma, now
  load-bearing), solve each structure's FJ system GLOBALLY as a polynomial system in t = tan(theta/2)
  (homotopy/Groebner + certified root isolation), coordinate cells only at the last level inside
  structure-reduced boxes, composed with A22's neighbourhood at Trump. Next advisor task: stress
  lemma + a bound on the pruned structure-graph count (the go/no-go number for the campaign).

## 2026-08-26 — structure lemmas L1-L7 written; A31 counting pilot dispatched
- docs/proofs/structure_lemmas.md v1 (advisor): L1 loaded degree >= 2 (single contact cannot
  balance); L2 degree-2 collinearity (thin branch); L3 floating components are rattlers OR carry a
  compression self-stress (A_K^T lambda_K = 0 — never silently dropped); L4 planarity of the contact
  graph (contact sets of disjoint convex bodies are convex => simple graph; edges drawn through
  contact points cannot cross); L5 metric caps; **L6 = the stress lemma's core, PROVED in 3 lines**:
  lambda0 > 0 forces load on the far wall; summing x-stationarity over that load's H-component,
  internal forces cancel in Newton pairs and y-wall normals have no x-component, so the component
  must also press the near wall — a wall-to-wall loaded chain (>= 3 squares at s*; Trump's strip has
  5). lambda0 = 0 branch = global self-stress, kept as its own excludable system. L7 binding-axis
  walls. Soundness ledger separates HARD prunes / THIN branches / SOFT report-only filters (Maxwell
  count is NOT a theorem — soft only).
- A31 dispatched (Opus): Level-0 ablation counts k=3..6, Level-1 decoration fan-out under tilt
  propagation, Level-2 projection to k=11. Completeness over speed. PI approved this test.

## 2026-08-26 — A31 verdict: naive enumerate-then-solve dead (4e29); joint structure-B&B is the shape
- Level-0 exhaustive k=3..7 with per-filter ablation (validated: OEIS match, independent brute force
  at k<=4 exact agreement, Burnside cross-check, Trump's own graph passes every hard filter).
  Dominant filters: metric realizability (x50 at k=7), wall-cycle planarity (x3.3), L6 wall-to-wall.
  Non-thin MAIN series is a clean exponential (~17^k -> ~7e9 at k=11); ALL super-exponential growth
  lives in the L2 degree-2 thin branch (89% of survivors at k=7).
- Decoration fan-out: tilt propagation (exact for the tilt subsystem) kills 79-98% but leaves
  ~4e10/graph at k=7; planar rotation-system consistency (added, Level 1b) kills up to 91% more and
  strengthens with k. Composed projection at k=11: 4e29-3e30 structures (best case with every
  promotion ~2.5e25). Even the undecorated graph layer alone is ~1e4 CPU-days. NAIVE
  ENUMERATE-THEN-SOLVE IS NOT VIABLE.
- Free lemma found (tight at Trump 3/3/3/2): at most 3 squares touch any one wall (gap 0.97832 vs
  range s-1 <= 2.8771). Maxwell: planarity caps |E| <= 3k+2, survivors max 3k-1 < 3k+1 => FLUSH
  CONTACTS (2 rows/edge) ARE MANDATORY for rigidity — |E| >= 3k+1 must never be used as a prune.
- Design consequence (agent + advisor concur): never materialise a level. The campaign must be a
  BRANCH-AND-BOUND OVER PARTIAL STRUCTURES (subgraph-closed kills: an infeasible partial structure
  kills all completions), with the metric/LP/Farkas/FJ tests applied at partial nodes and contact
  TYPE resolved algebraically inside the per-graph solve. The go/no-go number is now the B&B
  FRONTIER size, not the leaf count — unmeasured (next pilot candidate A32).

## 2026-08-26 — A32 verdict: NO-GO. The structure-B&B frontier cannot beat flat enumeration
- Canary PASS (Trump survives to leaf, real decoration survives mode-D). Engine reproduces A31
  exactly (9/9 cross-checks). ~1h20m wall.
- Decisive structural fact: with all-monotone kills every surviving structure is a leaf that must be
  visited, so nodes >= leaves; measured overhead 80-122x and GROWING with k. Frontier ratios linear
  in k (factorial x exponential): 5.6e12-1.4e14 graph nodes at k=11, ~1e30 decorated leaves — 7-24
  orders above the GO target. B&B collapse vs A31 flat: only 2.7x, and 3x SLOWER in wall clock.
- Stages 4-6 (Farkas / case-LP / FJ) fire ZERO times at the structure level: a structure fixes
  contacts but not selection rows (~500 possible vs ~35 needed), so the FJ system is not well-posed
  above the decoration layer. The exclusion tests only bite below a decoration+geometry resolution
  the search cannot afford to reach.
- One real win: exact strut-DFS (L2) kills ~43% of THIN graphs wholesale (0% of non-thin) — factor
  1.6, not the 10x a hard L2 prune would need, and even 10x is noise against 24 orders.
- CONCLUSION (three pilots, three sides of the same wall): coordinate cover c^33 (A30), flat
  structure enumeration 4e29 (A31), structure-B&B frontier >= leaves ~1e30 (A32). Any COMPLETE
  search that visits survivors of the current lemma set is dead. The endgame s(11) = s* needs a
  family-kill mathematics that collapses the space itself (O(1) core-shape theorem or equivalent) —
  not better search. All engines validated along the way are banked (FJ/Krawczyk, Farkas, filters,
  tilt/embedding propagation, drain v3 + structure lemmas L1-L7).
- Advisor recommendation to PI: resume A29 (s(11) >= 3.84 becomes the main line again, ~2 days at 6
  workers); advisor pursues L2 hard-closure (a real lemma regardless) and family-kill ideas in
  background; consider consolidating the corpus for write-up.

## 2026-08-26 — I-L13/I-L14 dispatched as Fable-led attempts A33/A34 (PI directive: Fable for theory)
- PI refined I-L13 with the grain conjecture: large-n optima are crystal-like (grains + boundary-
  confined wastage, interface cost -> constant), so eta should FALL with n and n=11 is near the
  method's worst case — A33 tests eta(n) across n and the high-n forcing question, alongside the
  eta(s) gate table and tight-variety maps at s-hat.
- A34 pilots sparse SOS on the lifted POP: validation on solved s(2)/s(3)/s(5), then the decision
  number — does sparse level 2 beat the proven pure-LP ceiling 3.83 at n=11?
- Both leads run on Fable (PI: Opus hopeless at theoretical math; Opus/Sonnet subagents for coding
  only). Machine shared 3+3 heavy processes; A29 remains paused (PI has not asked to resume).
- Idea 3 (structure ladder at s >= s-hat) shelved by PI for now — on the board, not active.

## 2026-08-27 — A34 closed: NO-GO with a new collapse theorem (advisor-reviewed: PASS)
- COLLAPSE THEOREM (A34, Fable lead; advisor verified the proof): any sparse moment relaxation of
  the lifted POP whose every clique carries <= m < n squares is feasible at s(m) at EVERY level with
  EVERY cut valid for m-square sub-packings — construction: uniform INJECTIVE assignment of each
  clique's squares to an optimal m-packing's placements; marginals agree, measures never glue (RIP
  failure as a hard ceiling, the anti-correlated-triangle phenomenon). 7 machine confirmations
  (Tier A n-independent in two cut settings x three levels). Consequences: pair cliques cap at
  s(2)=2; even 10-square cliques cap at s(10)=3.7071 < Stromquist 3.7889 — NO intermediate design
  can beat known results; the full 44-var clique is mandatory, and there level 3 = 16215-block
  (unreachable), while affordable level 2 is distance-geometry strength (projected 2.3-2.9 at n=11).
  Retro-explains A17-A20's wall. Reusable no-go criterion for all future sparse-relaxation ideas.
- Trust chain VALIDATED end-to-end: exact rational SOS certificate s(2) >= 1.7070435822
  (461253418188326279/270206000000000000), independent exact checker PASS (53 PSD blocks, LDL^T
  over Q, 4 corruption gates); Grams provably singular at the optimum — adaptive-shift rounding
  recipe recorded. If a strong relaxation ever exists, its certificates are Lean-portable.
- I-L14 closed on the idea board; registry row final. A33 (I-L13 tight variety + grain) still
  running: eta(s) gate in flight, T2/T3b queued.

## 2026-08-27 — A33 closed: grain conjecture refuted in range; tight-sum cuts + s(12) >= 3.90 banked
- Lemma A33.1 (equality pigeonhole) formalized: field total 11+eta => every subfamily I of any
  11-packing has coverage sum in [|I|, |I|+eta], escape <= eta; eta < 0 recovers Theorem 1; A33.4:
  eta < 1 excludes 12-packings.
- eta(s) gate: 0.046 (3.84, float; certified 0.3229 — tangency cluster blocks a tighter seal, G5)
  -> 0.243 (s-hat, float; bracket [0.193, 0.4254 certified]). Linear, slope ~5.3.
- T2 verdict: single-square variety pinning weak at s-hat (48% excluded, one blob, wall bands
  alive); multi-field stacking structurally dead (near-optimal fields share the tight set of the
  essentially unique optimal fractional packing). THE WIN: k-subset TIGHT-SUM CUTS — 51.5% of
  disjoint pairs in TxT violate cov(x)+cov(y) <= 2+eta; deployable as side rows in the A29 tree and
  I-L12 cells. Trump canary PASS everywhere.
- T3 verdict: PI's grain conjecture REFUTED in measured range — eta/rho RISE with n (n=11 is the
  method's best non-trivial case); crystal dips exact (eta(m^2) = 0); characterization eta(n) = 0
  iff LP alone settles s(n). PI's constant-wastage-per-perimeter is real (flat 0.26-0.27 in records
  to n=100) but the LP gap grows regardless. Literature section F added (CG-2020 flaw; Bui/
  McClenagan repairs; Bui's near-upright crystallization theorem; no prior LP treatment).
- NEW CERTIFIED THEOREMS: s(12) >= 3.877084 and s(12) >= 39/10 = 3.90 (vs published 3.7889), exact
  verifier PASS, independently re-verified, Lean-portable. tau*=12 crossing at ~3.95-3.97 = 99% of
  the n=12 record side 4.0 => an n=12 campaign (LP + tight-sum-cut tree) may NEARLY CLOSE s(12)=4 —
  the natural sequel.
- Endgame scoreboard after A30-A34: five approaches measured (coordinate cover, flat enumeration,
  structure B&B, sparse SOS, tight-variety pinning) — all dead or weak AT s-hat; the live equity is
  tight-sum cuts at 3.84-3.85 (fallback tree), the n=12 target, and the corpus write-up.

## 2026-08-27 — I-L15 (PI): escape-complex inflation; A35 dispatched (Fable lead)
- PI diagnosis of the A30 wall: the 1.86^33 shell is an artifact of metric boxes over a semantic
  object; the basin should be a cell complex cut along contact-change hypersurfaces — per stratum a
  FIXED smooth system where ONE dual certificate covers the whole cell to its combinatorial
  boundary. Escape strata of Trump's 38 contacts, codim-graded; loose regime handed to D2 + LP
  far-field; PI's bidirectional gap protocol (minimizer -> new certified CP or death) patrols the
  seam. Evades A30 (no boxes) and A31/A32 (one known graph's perturbations, not all graphs).
- Risks to measure: truncation K (codim beyond which slack kills) and cascade branching (new
  contacts subdividing routes). A35 measures both + certificate reach + stratum counts; deliverable
  = desktop-days estimate for certifying Trump's full basin boundary at s-hat.

## 2026-08-27 — A35 closed: GO as a tool, NO-GO as a basin closer. A30's per-CP assassin is dead
- PI's I-L15 (semantic cells, not metric balls) VALIDATED: Trump's jam neighbourhood covered by
  ~10^2 exactly re-checkable certificates in MINUTES on the desktop, vs A30's c^33 ~ 8e8-cell shell
  (1e5-5e7 CPU-h). The jam has NO escape routes: every break set empty, load-refuted, or wedged
  (min wedge strength 0.577); cascade trivial; zero sigma dips in ~4,700 followed segments.
- Modeling bugs found & repaired en route (M4/M1b/M3b/M2b, each caught by independent checkers):
  A22's basis misses the exact (1,3) corner-corner contact and used dist surrogates for two flush
  contacts (A22's own theorem survives — superset optimality); m1b minimal-dead enumeration missed
  4 triples (20,700 sets would have been silently uncovered); a positive-omega-on-dominance-rows
  soundness bug self-caught. Lessons recorded: surrogate rows = valid aux inequalities, never
  stratification coordinates; minimal-dead searches must run past size 2.
- The v2 25,050-stratum explosion proven an ARTIFACT: aux dist rows restored as valid inequalities
  kill both flat seeds at first order and yield a UNIVERSAL stratum-independent certificate — 64
  certs cover all 2^42 break sets, TRUE SURVIVORS 0, 553 s (vs 12.8 CPU-days per-stratum).
- Composed theorem: sigma >= s-hat, equality iff z-hat, all break sets, both FJ branches, on
  box(z-hat, 0.25 r_N) — currently SUBSUMED IN REACH by A22 (structure/cost vastly better, radius
  worse), conditional on an endpoint-row lemma. Two bounded levers to beat A22's reach: L1 the
  endpoint-row lemma, L2 omega-scale normalization (per-stratum form already reaches 1.6-3.1 r_N).
- Assassins named: semantic cliff R* ~ 0.006 (gained contacts revive 82% of sets; the ridge sits AT
  the cliff — the full basin boundary is where the method's language expires); the GLOBAL wall
  (A31/A32 1e30, LP ceiling 3.83) untouched — A35 removes the per-critical-point factor only.
- Cost: ~1 desktop-hour for the whole pilot; ~10-30 min per critical point steady-state; all 36 A04
  optima ~ 1 desktop-day (each needs its own contact audit first).

## 2026-08-27 — A36 dispatched: chase A35's levers L1 (endpoint-row lemma) + L2 (omega scale)
- PI directive. Target: composed escape-complex theorem on a box strictly larger than A22's r_N —
  turning "method validated" into "method dominates A22." A35 lead resumed with context.

## 2026-08-27 — A36 closed: composed theorem STRICTLY DOMINATES A22 — 7.56x radius
- THEOREM (A36, quoted at safety radius): every feasible 11-square configuration z with
  ||z - z-hat||_inf <= 3.7e-3 (certified max 3.779e-3 = 7.56 r_N) has sigma(z) >= s-hat, equality
  iff z = z-hat. Stratum-blind (all 2^44 break sets, both FJ branches, stationarity never used).
  17 IV certificates, standalone re-checker (339 checks, independently re-run by the lead), 5/5
  corruption gates. ~12 min of compute. Volume vs A22's box: ~7.56^33 ~ 10^29 x larger.
- Honest attribution: the L1 endpoint lemma (over-estimate principle: any-corner separation rows
  over-estimate the axis gap, so barriers never need dominance rows) is sound, discharges M2b-a for
  good, but bought +2.4%. The decisive lever was DISCOVERED, not ordered: MAX-FORM PINNING —
  kappa_eff = max_r(|Y_ir|/omega_r) = 19.3 vs kappa/alpha = 784 => x11.4 radius. Branch-free
  certificate on A22's own rows + 2 aux dist rows already reaches 7.38 r_N on the minimal trust
  chain.
- Standing limits: local theorem; ridge handoff G1 + semantic cliff R* ~ 0.006 unchanged (current
  radius = ~60% of the cliff; next ceiling = A22 old-row tangential margins at 5.2e-3); global
  far-field wall untouched. Binding constant kappa_eff*Hbar*h/(1-beta).

## 2026-08-27 — campaign architecture settled; A37 (CP atlas) dispatched
- PI's composed architecture confirmed with the value-discharge subtlety: far-field exclusion tests
  STRUCTURALLY FAIL near any CP (a critical point is genuinely there, value > s-hat) — the per-CP
  A35/A36 value certificate is the only discharge for those holes. CP list completeness NOT assumed:
  BDBFS protocol (survivor -> minimizer probe -> new CP audited+certified, or death) keeps it sound.
- Campaign map: Trump box DONE (7.56 r_N); A37 = CP atlas (~1 desktop-day, mechanical + audits);
  A38 = root-power pilot at s-hat (THE last unmeasured factor: can the conditioned LP-tree with
  tight-sum cuts/wastage/occupancy shrink the far field to the CP boxes at tractable node count);
  seam = G1 cliff handoff. s(11) = s-hat exactly composes from D1 + far field + atlas + A36
  uniqueness, IF A38's number is finite-and-desktop.

## 2026-08-27 — A37 closed: the certified critical-point atlas. 32 catalog families -> 10 attractors
- HEADLINE COLLAPSE: below 3.95 the material structure is Trump (the only RIGID CP) + 9 valley
  mechanisms ({1~2}, 6, {13~14}, 27 marginal, 31, A37-NEW-0..3 at s = 3.9027-3.9255 — four
  attractors A04 MISSED, found by draining its own fixed-angle artifacts). The other 24 catalog
  entries are NOT-CP tilt-lattice shadows, each CONSTRUCTIVELY refuted (explicit smaller-s packing)
  and drained 24/24, 0 stuck, into the 10.
- Atlas (results/atlas_final.json, 36 entries): every entry carries a certified discharge box
  sigma >= V >= 3.877084 (exact rationals) within radius h (3.76e-3 Trump barrier regime ... 6.0e-2
  high-s trivial regime). 37 certificates, 2018 checks PASS, corruption gates bite (with the
  applicability honesty fix). Trump through the GENERIC pipeline reproduces A22 + A36 from scratch.
- Lessons banked for A38: discovery loop is LOAD-BEARING (catalog provably incomplete); CP
  classification needs residual scales + constructive witnesses (two false NOT-CPs caught at 1e-7);
  trivial Lipschitz beats barrier for s_min >= ~3.887; dedupe s-primary at 1e-8, never s-alone.
- Cost: < 2 desktop-hours vs 1-day budget. Gaps G-A37-1..5 recorded (float-rationalized NEW
  centers, marginal classes, [NUM] drain taxonomy, completeness-beyond-today = the global wall).

## 2026-08-27 — A38 dispatched: the far-field root-power measurement at s-hat
- The last unmeasured factor in the s(11) = s-hat composition. Weapons composed into the tree for
  the first time: tight-sum domain cut (placements with coverage > 1+eta pruned everywhere), pair
  cut (joint coverage > 2+eta => conflict rows), atlas discharge (36 certified boxes as termination),
  Farkas/FJ for near-jammed nodes, the A27 case-LP arsenal. Measures kill matrix by depth x weapon,
  survivor census, the G1 seam (tree-leaf scale vs box scale), extrapolation bracket, GO/NO-GO.

## 2026-08-28 — A38 closed: NO-GO — the far-field cost wall at s-hat is named; root theorem banked
- THE MEASUREMENT the s(11) = s-hat composition was waiting for, and it is honest and negative:
  the conditioned interior-first tree at s0 = 3.877084 CANNOT reach the atlas boxes with today's
  engine. Assassin = per-node LP DECISION COST at s0 (cost wall, not geometry wall): 0/60
  depth-2/3 nodes decided at 180-485 s — tau sits 0.5-1.5 BELOW budget (kills plausibly exist)
  but the row-generation LP never stabilizes (minmass 0-0.5); the same rule decides in 150-500 s
  at 3.84. Driver: eta(s0) ~ 0.24 vs eta(3.84) ~ 0.046. b_eff = 8.00 flat, every weapon silent
  until W1's onset at depth 5-7 => frontier floor 70-700 desktop-days, bracket open-ended above
  (no decision constant exists in the data; cheapest closer = one 3600 s calibration node, G7).
- BANKED: THEOREM A38.1 (certified) — every 11-packing at side <= 3.877084 has a square centred
  in the interior zone [1.1, 2.777084]^2; margin 0.9994 (vs 2.76 at 3.84): the interior-first
  entry point survives AT the endgame side, barely.
- TRUST-CHAIN FINDING: exact-certification sample failed 2/8 at level 1 — the float row oracle
  leaves coverage holes on nodes that PASS A27's converged/minmass/added_rows rule at s0; both
  repaired to tau = budget. A27/A29's 3.84 results are NOT contaminated (their leaves were each
  exact-certified). Rule for all future sweeps: certification-in-the-loop, float classification
  is measurement-only.
- Weapons ledger: W1-as-row-filter dead shallow (oracle already hunts the tight variety) but its
  bite GROWS with depth (row-drop x16 by 2-core scale; c_core median 0.658 -> 1.21 by depth 3);
  A33's sealing margin (G5) quantified as a ~5x multiplier on W1 => reseal is lever L1, worth ~2
  depths (~64x frontier). W2 strictly post-refinement (pair bound collapses over wide cores).
  W3/W4 structural zeros at pilot depths (need all 11 squares pinned) — the G1 seam probe leaned
  right (occupancy tau 9.2 < 10) but could not converge: seam OPEN, cost-blocked at step one.
- Census clean: Trump's 3 witness cells survive (a sound tree must not kill them); the 5
  alive(LP) cells sit at tau = 10.000000 / maxcov = 1.000000 exactly — the equality-manifold
  knife edge (A33's essentially-unique optimal fractional packing showing through), the true-wall
  geography to watch if the cost wall ever falls.
- Endgame consequence: s(11) = s-hat is NOT currently composable — D1 + atlas + A36 uniqueness
  stand, the far field does not. Live equity: L1 (reseal eta at s-hat), L2 (decide-without-
  convergence: witness-feedback in the solve loop), L3 (warm-started children); the 3.84-3.85
  fallback tree and the n = 12 campaign (A33) are unaffected and remain the affordable targets.
  T0 composition note (seams S1-S8) in attempts/A38-root-power/notes/T0_composition.md; full
  report attempts/A38-root-power/results/rootpower_report.md; registry row final.

## 2026-08-28 — PI verdict on A38: a win (assassin named, levers actionable). A39/A40/A41 dispatched in parallel
- PI reframing: compute is down to reasonable numbers with a clear plan to kill the pure-guard-LP
  asymptotics. Two PI options (bottom-up basin growth crossing only limiting boundaries; better
  top-down deletion) + advisor's third (early certification — the root certified from an
  UNCONVERGED LP in 1.7s; A27's rule gated certification on convergence, so depth nodes never
  tried). All three fired in parallel: A39 (Opus: cert-in-the-loop calibration + field reseal),
  A40 (Fable: surgery-lemma basin growth to h ~ 0.03 — the cliff is the enumeration's limit, not
  the barrier's; tangential margins bind and they're per-row), A41 (Fable: S1 seam design with the
  parametrized cost formula). Decision point after all three report.

## 2026-08-28 — A40 closed: surgery-lemma basin growth — Trump's certified box grown 3.7e-3 -> 6.55e-3 (13.1 r_N); honest saturation named
- THEORY (T1, banked in attempts/A40-basin-surgery/notes/theory.md): the SURGERY LEMMA set —
  S1 pointwise [V]-validity (A37's rule, now proved); S2 over-estimate (A36 L1.1); S3 axis
  disjunction with kills on a region; S4 safe/forced axes (gained-contact rows valid WITHOUT
  dominance); S5 multi-cut ANCHOR certificate (face cut + tie cuts as valid affine rows; the
  negative-at-z-hat cut value is the anchor; accumulated-interval Hessian with signed-diagonal
  refinement, ~25% below the triangle bound); S5' leaf-emptiness (Taylor bound drives a valid
  combination negative on the sub-box); S7 floor-shifted rows; S7' RELATIVE floors (same-axis
  corner rows differ by an exact 1-D trig of the relative angle — endpoint/couple rows priced
  at sin(tau) under a tie cut); S6 composition (rings x faces x branch trees, strict margins
  preserve "equality only at z-hat" on top of A36's theorem).
- RESULT (T2): certified growth 37/10000 -> 5794/884563 = 6.5501e-3 = 13.10 r_N = 1.77x A36,
  in 7 rings, 2930 certificates (2564 anchors, 42 wall-empties, 324 leaf-empties), 45 min
  wall, seconds-per-certificate. Chain, coverage trees, kills, [V]/floor/relfloor claims and
  margins re-verified by the standalone corruption-gated checker (a40_check.py, no producer
  libs): 168,774 checks, 0 failures, reproduced twice; 5/5 gates fail as required.
- BINDING SEQUENCE: (i) h < 4.5e-3 anchor-only (61 faces, wall-empties); (ii) 4.5-5.4e-3 the
  |t|=0.475-0.479 [V]-deaths force surgery on (3,7),(4,7) then all 10 flush/corner pairs;
  (iii) 5.4-6.5e-3 deep branch trees (up to ~10 pairs/leaf) + leaf-empties carry the load;
  (iv) SATURATION at h = 6.55e-3, face sq6.theta-, all-near leaf with (6,9) in its switched
  selection: the worst-leaf growth rate omega_b = 0.0518 = 1/kappa_eff(A22) (the A36 pin
  constant reappearing as a rate) vs quadratic cost 2*Hbar*h with Hbar ~ 8 => hard ceiling
  h ~ 0.0065 for this certificate form. NOT a geometry wall: a cost-of-certificate wall,
  named quantitatively.
- Levers left on the table (gap list, attempts/A40-basin-surgery/): G-A40-1 signed quadratic
  remainder beyond diagonal (the |H|-mass Taylor bound is the assassin's other half);
  G-A40-2 recentred anchors inside the slivers; G-A40-3 full-near-cone rate 0.164 => ceiling
  ~0.02 if the switched-selection slivers are closed; G-A40-4 tie-cut search is budgeted DFS
  (facesearch 90s) — saturation declared at budget on the known wall, deep probe confirms the
  rate wall at 240s+; G-A40-5 h=0.01/0.03 checkpoints NOT reached — brief's goal partially
  met, honest NO recorded with the constraint named.
- A29 untouched; 1 background process throughout; Opus subagent used for the verification run.
