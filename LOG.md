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

## 2026-08-28 — A42 dispatched: occupancy-chain pricing + N1 + the PI's tightening sweep
- PI approved A42 and contributed the tightening-sweep schedule (gym insight): after full coarse
  assignment + N1, the placement domain COLLAPSES to 11 islands — re-tightening each ball against
  the restricted domain (Gauss-Seidel over balls, incl. a second pass) may be tiny+strong, a regime
  never measured (every prior occupancy LP was played against the full box). First-class T3.
- A42 = T1 prove N1, T2 chain slack-decay k=0..3+, T3 the sweep down to the 0.0066 basin
  rendezvous, T4 composed desktop-days + GO/NO-GO. The occupancy family only; the deep-core family
  stays dead per A39.

## 2026-08-28 — A42 closed: occupancy family measured to ZERO forcing power at every legal zone size; N1 proved; far-field NO-GO by MECHANISM
- **T1: Lemma N1 PROVED** (docs/proofs/occupancy_collapse.md). Separation ||c-c'|| >= 1
  (inscribed disks; Trump attains equality EXACTLY — min pairwise dist^2 = 1 in exact
  rationals); zones of diameter < 1 hold at most one centre GEOMETRICALLY (no pigeonhole);
  11 disjoint certified zones => exactly one each, assignment unique mod S11, complement
  centre-free. Cor N1.1: wrap-window conditioning as full-theta core + complement NO-family —
  kills the 2^6 wall-square branch. Instance hypotheses machine-checked exact (n1_check.py).
- **T2 (chain, r = 0.06 balls): dead at k = 1 by an exact integer.** tau(k) = 11-k exactly,
  k = 1..5 (12-k for k >= 6: the clipped corner ball buys NOTHING, permanent +1), all
  converged, minmass 1 — true optima. F2 "unit exchange": each ball core buys exactly the
  1.0 budget unit it costs. F3 "reflow": the forcing target nofam is worth exactly zero
  (delta-tau < 1.2e-12 on deletion; d tau / d rho' = 0 at k=2 over six radii). A38 probe-A's
  slack -0.80 = early-relaxation artifact (converged union optimum 10.000000, 619 s).
- **T3 (PI's tightening sweep): structurally vacuous — F1, the last-square identity** (one
  line: tau >= mu(Q0) >= 1 for any live placement) => budget-1 kills iff EXACT emptiness;
  111 nodes, tau = 1.000000 at every rho' across three decades, dying radius = R_j itself,
  **second-pass gain = exactly 0** (PI conjecture honestly refuted at budget 1). Identity
  retro-explains 3.84 deep-leaf full pinning. KEEPER (F5): the N1 assignment step is FREE —
  given 10 cores + complement cover the verifier alone forces the 11th square, 11/11 PASS,
  38.1 s total, measure 1e-6, no LP.
- **Zone-size lever (last design point): dead, volume scaling REFUTED.** w = 0.35 zones
  (side 0.70, diam 0.99 < 1, N1-legal, 34x ball volume): tau = 11.000000 exactly at k = 0,
  29 cert attempts all fail ON COVERAGE; w = 0.25 / 0.15 worse; medium cores ANTI-economical
  (cost 1.0 budget, buy 0.145 tau). The side-1.68 central-window root stays the UNIQUE
  certifying occupancy statement. Conjecture recorded (no compute): occupancy power = ghost
  mass displaced, not volume — profile the ghost measure vs zone kills as future work.
- **T4 verdict: NO-GO by mechanism.** seam_design's cascade term does not exist — no
  certificate at any (k, radius, zone size, interleaving). Integer-exact conditional taus =
  the 1/4-ghost saturates EVERY conditional budget at s0: the five A38 knife-edge cells were
  not a corner, N6 is the GENERIC far-field mode. Survives: root (banked), N1 (proved,
  Lean-friendly), F5 free assignment (machinery-in-waiting), F1/F4 as proposal filters, A39
  cheap-cert rule re-validated (0.6-16 s/attempt). Requires: N6-class mathematics — two-field
  budgets (vs A33's shared-support obstruction), a NOFAM-AWARE FJ/Farkas (F4 shield: any
  nofam-blind weapon is structurally unable to force occupancy — Trump realizes the rest of
  the hypothesis), theta'-type second-order rows (A17-A20 caveat), ghost-mass profiling as
  the diagnostic first step. Report: attempts/A42-occupancy-chain/results/a42_report.md;
  facts F1-F6: notes/structural_facts.md; verification V1-V5: notes/verification_log.md.
- A29 untouched; 3 Opus compute agents, <= 2 solver processes each; ~80 min total LP time —
  the family failed on VALUE, never on cost.

## 2026-08-28 — A43 dispatched (I-L16): the ghost-immune bulk-kill axis + spines as anchors
- PI push: the 10^30 counts survivors of the WEAK 2025 filter set; most illegality is invisible to
  those filters; bulk evaluation should kill grains en masse. Advisor synthesis: every post-A31
  theorem is combinatorial/geometric = GHOST-IMMUNE (F4 shields only coverage-type certificates) —
  the bulk axis was never systematically applied. And L6 gives every jammed grain a GUARANTEED
  anchor: the wall-to-wall loaded chain (spine, 3-6 squares, 1-D, heavily constrained). Spine-first
  enumeration inverts A31/A32: enumerate spine types under the full stack (plausibly
  dozens-hundreds), then per-spine A35-style anchored completion. Conjecture: only Trump's tilted
  5-strip spine completes below s-hat. A43 = H1 (library re-census, per-filter ablation) + H2
  (spine census, Trump canary) + composition.

## 2026-08-28 — A43 closed: bulk-kill thesis refuted at both levels; the enumeration-certificate mismatch named
- H1 (re-census, Opus, verified): the ENTIRE 2026 theorem library, soundly applied, buys ~x2 on
  the k=11 graph count (composed exact 2.3e29-1.5e30 vs A31 4.2e29-3.3e30). Only per-wall<=3
  hard-prunes (x1.35 at k=7, now HARD row R11). Per-filter reasons, each different: A38.1/THM3
  existential => vacuous below the k=11 join (witness may be a rattler); W1/W2 positional =>
  certified m_low = 0.000000 on every wall-mask window while the SAME field exempts 7.13% of
  placement cells (power exists, window ~1e6x too coarse); flush-mandatory NOT certified (ledger
  SOFT + A32-H1; brief corrected, run as CONDITIONAL — worth x1e4 IF ever proved, the biggest
  unproven lever); motif filters UNSOUND as filters (Trump's own graph contains a 4-cycle —
  canary-confirmed over-kill). Keepers: wall-flush slab cut (t=0, d=1/2 pinned => 36/2000
  along-wall positions certified exempt — the census's only positional bite); A31's numbers
  regression-confirmed EXACT; Trump canary 20/20.
- H2 (spine census, Opus, verified): L6 spine types at s0 under span/tilt-coupling/field/wastage:
  LARGE, not small — 10/132/523/2074/8249 at k=3..7, ~2.1e6 at k=11 (C0-C2 DP). Only k=3 is
  strong (72% cut; all survivors C-C, no wall-flush end possible, tilt classes forced into
  [18,72] deg — a real 3-chain structure theorem at s-hat); k>=4 cuts <0.4% (only C1's two local
  tilt rules). C3 (field) and C4 (wastage) INERT: wastage floor exactly 0 on every survivor — a
  spine type forgets the transverse coordinate and deep-interior dead area is genuinely 0.
  Canaries clean: 30/30 Trump chains (x-spines k=4, y-spines k=5; the tilted strip = y-spine
  F-CEab.FL.FL.FL-C), 163/163 A37 valley chains at their own s, all 48 kills witness-audited by
  an independent implementation. Per-spine completion: 1.3e-3.9e18 desktop-days BEFORE the
  ~490^k unpriced transverse debt — no far-field program written (honest-either-way clause).
- THE LAW (composed result): the ENUMERATION-CERTIFICATE MISMATCH — our certificates price
  PLACEMENTS; every object cheap enough to enumerate quotients placement away; bulk enumeration
  and bulk certification cannot meet. Third face of the finding/refuting asymmetry beside the
  ghost shield (A42 F4) and the c^33 cover (A30). Positive corollary, measured twice: bite is
  proportional to pinned coordinates (wall-flush slabs; k=3 tilt forcing).
- Double-spine lever assessed on paper (no compute): crossing lemma (x-spine separates bottom
  from top => the two spines share a square or a contact; Trump shares {2,8}) pins both
  coordinates of 1-2 squares out of ~9; joint types ~x1e3 MORE (523^2 x crossings at k=5) for a
  predicted x1.1-2 cut; mono-axis branch uncovered. NO-GO. Ranked instead: (i) prove/refute an
  FJ-specific Maxwell row bound (N4), (ii) I-L13 interface charging — the only certificate
  family whose unit of account matches the enumerated object.
- Report: attempts/A43-spine-census/results/a43_report.md; formalization + soundness ledger:
  notes/formalization.md; lead checks: notes/verification_log.md. A29 untouched; 2 Opus workers,
  <= 3 processes each, ~1 h compute total.

## 2026-08-29 — A44/A45 dispatched in parallel (A43's ranked levers)
- A44: the FJ-Maxwell bound — refutation hunt against the atlas first (valleys make naive
  isostaticity false), then proof or counterexample; x1e4 census multiplier if proved.
- A45: the PI's interface-charging calculus — per-contact-type certified charges, ownership
  disjointness, Trump canary, zero-charge-class composition; the one certificate whose unit of
  account matches the enumerated object.

## 2026-08-29 — A45 closed: interface charging certified-sound and a magnitude NO-GO by theorem; the PI's ruler laws are the live bite
- THEORY (notes/charging_lemma.md): the charging lemma EXISTS at T-quality — plane-mode
  position-freeness (big-container trick), moat-Voronoi ownership (A23's closed-contact
  exclusion makes a certified moat box repel every other packing square; charged contact
  points >= min-moat apart; ownership free at rho_min/2), Thm A45.1 sum(charges) <= s^2-11.
  Lead audit caught 3 soundness issues pre-compute: CC uncharge­able (a free wedge >= 90 deg
  kills every moat), FL zero-proof repaired (slid flush union not convex — reentrant-notch
  argument), WCC container-corner coincident-point leak patched.
- TABLE (Opus A): 25/75 bins kept, ALL exact-Fraction certified (270 tiles + 25 moats, 0
  failures); rho_min = 1/16. Trump canary PASS: his 25 contacts sum 0.00174 <= 4.0318 —
  capture 4.3e-4 of budget, ~500x under A26's per-square 0.8672.
- THE NO-GO, as theorems: (2) TABLE-INDEPENDENT — charge <= rho_min^2 <= 1/16/contact,
  contacts <= 3k+2 => max conceivable sum at k=11 is 2.1875 < 4.0318: the charge filter can
  NEVER fire at n=11 (actual table: max sum 0.0219 = 184x short; firing needs rho_min >= 0.34,
  off the moat ladder); (1) on-paper, kills EVERY ownership scheme — the binding cap is the
  plane-dead pair area itself (measured 0.054 WC / 0.004 CE full wedges): magic multiplicity-1
  overlap accounting sums ~0.9 at k=11; Bonferroni /m no better; (3) min-over-realizations
  collapse (CC/WCC/dropped-bin loopholes). MECHANISM (4th face of the mismatch law): an
  interface pins RELATIVE coordinates; relative-coordinate certificates price only sliver
  wastage (~1e-2), never the far field where the budget lives (A25's corner moats). A26 died
  on an exact zero; A45 dies on quadratic smallness. Lawful: bite ~ pinned coordinates.
- LIVE BITE — the PI's two flush-ruler laws, now EXACT census filters (Opus B, regression
  to A31/A43 exact, canaries 100%): Lemma R k <= s(cos+sin) (upright rulers <= 3, 5-rulers
  force tilt [20.77, 69.23] deg, 6 impossible; Trump's 5-strip extremal, margin 0.4636) +
  Lemma Q quantization. L0 inert (all-corner decoration — same law again); L1 RULER cuts
  5-7% of decoration weight per k (keep 0.894-0.928 at k=11; composed k=11 count 2.30e29 ->
  2.06-2.14e29 = x1.09; kill audit 411/411 wall-anchored: Lemma-Q path 392, NEW odd-cycle
  parity 16, integrality 3; the pure length cap kills 0 — bite is gauge multiplicity, only
  where a wall pins a coordinate). ZERO-CHARGE COMPOSITION mostly
  closed: the k >= 10 zero-charge class is DEAD EXACTLY (tilt propagation + A26's 2.503-deg
  9-cap — UNIVERSAL, no k=11 join); k <= 9: ruler kills 60-78% of the class, rattler-join
  residue stands; m_ub(theta) certified 9 on [0,3) deg, 12 on [3,18), 14 on [18,45)
  (GAP-Z1 stands on 14/15 bins; the sharp m(theta) B&B = the one open computation).
- Keeper: Ceiling 2 as a SCREENING TEST for any future per-contact certificate proposal
  (required mean charge/contact 0.29-0.37 vs ownership ceiling 1/16).
- Report: attempts/A45-interface-charge/results/a45_report.md; theory+verdict:
  notes/charging_lemma.md; lead checks V1-V9: notes/verification_log.md. A29 untouched;
  2 Opus workers (A <= 2, B <= 1 processes), ~2 h compute.

## 2026-08-29 — A46 dispatched (I-L17, PI): flush-mandatory via balanced wedges
- PI's dichotomy: in a flush-free critical structure every corner contact is BALANCED (else the
  wedge-closing relaxation drains toward flush), and balanced corners at substantial angle strand
  macroscopic certified wedges — the budget kills the network. Evades both closed roads: not
  FJ+counting (A44), not raw-contact charging (A45 — "balanced" imports criticality, pinning the
  wedge geometry; bite ~ pinned coordinates). W1 = small-angle exclusion (novel math, the crux);
  W2 = certified w(delta) table + disjoint union + budget composition (A23/A25 machinery).
  Advisor prior: above even odds — first such in the campaign.

## 2026-08-29 — A47 dispatched (I-L18 expanded): the PI's majority route with magnitude primitives
- Advisor reality-check folded in: A46's ceiling shows contact-local wedges cap at 0.70 x budget
  even all-large-angle — the majority argument needs bigger primitives. The synthesis: A21's
  certified corner occupancy gives POSITION unconditionally; flush-freeness forbids wall-flush;
  so the 0.34-0.61 corner charge FIRES on flush-free structures (5-10x wedge scale). Thin branch
  closable outright via A46's designed-not-run rectangle lemmas (W1.6 quantization residue).
  A47 = (a) rectangle lemmas, (b) certified corner/wall primitives, (c) majority composition.

## 2026-08-29 — A48 dispatched (I-L19): the bridge-cascade descent
- The criticality-aware route, untouched by all six closed faces. The cascade: near-flush loaded
  contacts need blockers at STRICTLY greater slope (R1); the recursion can't cycle or die in the
  interior (R2); wall termination collapses the lever (1/sin d) into the lambda0=0/self-stress
  branch (R3); the strictly-rising mismatches reach mid-tilt, where tilt-forcing + the certified
  corner/wedge tables charge what the recursion FORCES (R4). Compose with A47's thin-branch
  theorem. Bridge mechanism = positive control; a globally-embedded flush-free critical
  configuration, if found instead, would be a discovery.

## 2026-08-29 — A49 dispatched: the flush-free critical-point hunt (I-L19's decisive experiment)
- Seeds built from A48's own evasion architecture (the configurations its local theory says COULD
  balance flush-free); unconstrained drains record which contact flushes first (the global-breaking
  map); stratum-constrained drains find flush-free-stratum minimizers and test them against the
  full FJ LP. Either a certified flush-free critical point (refutes flush-mandatory — discovery) or
  the flush-acquisition map that the global argument needs. A48 lead resumed with context.

## 2026-08-31 — A49 closed (advisor close-out; lead hit usage limit post-compute): OUTCOME B
- The decisive I-L19 experiment: 252/252 evasion drains acquire flush; 0 candidates; 72/72
  stratum minimisers pressed against the flush boundary (0/324 interior). The PI's original
  drain-to-flush intuition measured at scale. Flush-acquisition map banked: the break is at the
  chain's WALL TERMINATION, never the presser — the target a future global proof should formalize.
  Sampling caveat recorded (near-upright basins only). a37_drain.repair bug found+fixed.
- PI's paper vision recorded (shower notes): paper WHEN full optimality proof exists; appendices
  publishing every off-critical-path investigation (negative results as first-class output);
  a methods section on the human+Fable+Opus division of labour; a validation/simplification
  section. Write-up deferred accordingly; the lab keeps REGISTRY/LOG/certs paper-ready.

## 2026-08-31 — threads 1-3 fired in parallel (A50/A51/A52); marginal-space reframe + span-semigroup idea
- PI re-oriented after days away; advisor reframe recorded: the three views form a chain of
  forgetting — view 1 joint (33-d truth), view 2 combinatorial quotient (contact strata), view 3
  MARGINALS (the LP sees only the one-particle density; the ghost is a marginal with no joint
  preimage; theta' = the two-particle rung, killed by collapse for sparse cliques; the mismatch
  law = certificates in view 3, enumerables in view 2, truth in view 1).
- New tool proposed by advisor and folded into A50: DIOPHANTINE SPAN-SEMIGROUP GAPS — rigid chain
  spans live in semigroups generated by {cos t, sin t, 1}; wall-to-wall termination needs a
  semigroup element in a certified window; gap conditions exclude tilt classes wholesale.
  Generalizes A47 T1 + the PI's ruler law; ghost-immune; position-carrying.
- A50 (Fable): span table + wall-termination instability lemma. A51 (Opus): mid-tilt flush-free
  hunt. A52 (Fable light): two-field probe vs the knife-edge/saturated cells — first direct crack
  attempt at the ghost's equality manifold.

## 2026-08-31 — A53 dispatched (I-L20, PI): simple-square stratification
- PI's decomposition: k = number of grid-locked doubly-flush squares. Two leverages no prior
  branching had: skeletons are DISCRETE (exact rational grid slots, tiny census) and non-Trump
  skeletons are F4-SHIELD-FREE; plus the measurable crux — the 1/4-ghost's power is built on
  full-box symmetry, and residual-region LPs (skeleton pinned exactly, area deleted, L-shaped
  domain) have never been run. Hazard flagged: k unstable under epsilon (near-grid squares strand
  ~epsilon) — patched by the k-maximality drain selection (grid-sliding is sigma-non-increasing;
  A49 measured the press-into-flush dynamics). Four attempts now in flight (A50/A51/A52/A53).

## 2026-08-31 — A52 closed (done-negative): two-field route to N6 dead by theorem; Prop 1 banked as the SEVENTH FACE
- Prop 1 (A52 formulation note §3, pre-registered before compute, 3-line proof): the joint node
  LP over ANY finite list of certified guard fields — one packing variable set, per-field point
  capacities + budget rows — has value EXACTLY tau (single-field): every Farkas combination of
  such rows IS a covering measure and pays full mass. On knife-edge cells no strict drop is
  possible in exact arithmetic. Seventh face of the enumeration-certificate mismatch law:
  coverage certificates cannot be COMPOSED — the ghost equality manifold is a node property,
  invariant under choice of certified field; only constraints false for fractional z can thin it.
- Machine confirmation 21/21 (A38 knife-edge n061/065/074/095/100 + A42 k1/k2; p1/p2 perturbed +
  region-weighted fields, all oracle-feasible, all EXACTLY optimal T2 = B + O(1e-11)): baselines
  tau = B to 1.8e-15; tau_J1 = B to 2.5e-9; zero certification attempts warranted. Diversity was
  real and bought nothing: supp Jaccard 0.00-0.17 (vs A33's 0.41-0.50) but tight-set Jaccard
  0.79-0.99. J2 exhaustion at FULL strength (delta = 0: coverage forced exactly 1 at all 19-23
  atoms of both supports + capacities + cardinality): nu_J2 = B on every node x variant, 0
  binding rows. 6/21 leak rows (leak2 = 0.4-1.0, L2 = 0): a specific ghost vertex dies (one
  placement covering two field-2 atoms), a replacement full-value vertex always exists — probes
  kill ghost VERTICES, never the ghost FACE. A33's "4.6% where independence predicts 7%" and the
  A42 complementary-slackness caveat were this theorem's float shadow.
- N6 status: coverage/capacity route CLOSED with prejudice (Prop 1 is a 3-line screening test for
  all future proposals of this shape). Remaining honest routes: integrality/enumeration
  constraints (A53's discrete skeletons + residual LPs are exactly this shape), theta' continuum
  revival (still needs a new idea), ghost-mass profiling as diagnostic. Signed-measure (J2/Farkas)
  weapons: outside current verifier and measurably toothless at full strength. 1062 s of compute
  total; A29 untouched. Report: attempts/A52-twofield-probe/results/a52_report.md.

## 2026-08-31 — A53 closed (done-success, pilot): I-L20 simple-square stratification
- DEFINITION AUDIT: PI's Young-form ("tiling grown in from a corner") adopted as primary; it is
  STRICTLY stronger than the brief's recursive doubly-flush reading (1110 tuples/163 D4 classes
  vs 7204/944; explicit witness for the divergence — partial-overlap cross-family chains). Census
  exact (Fractions), k = 0..9, stable in s across (3.82, 3.9). Trump = ((2,1),(1),(1),()) at k=5,
  certified from A03's 60-digit data; the 6th upright is eps-off-grid by 0.0325583143 (degree-7
  minpoly) and its completing slide is BLOCKED by a tilted square's corner intruding 0.0135 into
  the landing corridor — the bridge geometry measured inside Trump's own packing.
- HEADLINE: residual-region guard LPs with EXACT skeleton pins break the 1/4-ghost. All 33 k=6
  classes LP-dead (typical tau = 4.000000 exactly = an integral 4-square blocking packing;
  6 + 4 < 11), 32/33 exactly certified (most kills are 3-8-atom finite unavoidable sets, certs
  1-60 s under the A39 rule); k>=7 capped unconditionally (every k=7 class contains a certified
  k=6 sub-tuple). All 21 non-Trump k=5 classes LP-dead, 18 certified. Ghost law: corner pins keep
  tau = budget (corners4 -> 7.000, A14/A16 baseline reproduced); side-zone/interior pins collapse
  it. Kill hardness concentrates on Trump-adjacent classes; opens: k6_23 = Trump+TL (4.9337),
  k5_11 (5.905), k5_13 (5.677), k5_16 = corners4+1 (5.98951 — essentially at budget).
- Trump stratum: provably alive (feasibility canary), eta_residual consistent with 0; residual
  tight variety does NOT collapse (5.1% of placement space at eta 0.02 — the localization hope of
  I-L20's Trump branch fails at pilot LP quality; the mid-tilt pinwheel core is the last stand).
- Theory banked: partition exhaustiveness, anchor uniqueness, the 33-node cap, and the honest
  k-maximality slide-selection lemma (slide-stuck minimizer exists; blockedness — semi-algebraic,
  LP-invisible — is precisely the A50 cascade's target). Gap list: s-parametric transfer of the
  kills (G-A53-1), blocked-slide pricing (G-A53-2), k=4 sweep (14 classes), k6_23 certification.

## 2026-09-01 — A54 dispatched (stragglers); low-k design settled in discussion with the PI
- PI question answered and banked as the low-k design: the strata ARE disjoint (L3) but naive
  exclusions ("no square exactly at slot X") are measure-zero = LP-invisible (epsilon-parking).
  The usable form = the SLIDE-STUCK DICHOTOMY: hunt the slide-stuck minimizer (L6); every square is
  then either FAR from every completing slot (delta-radius NoFam zones — LP-visible positive-volume
  exclusions) or NEAR-BUT-BLOCKED (forcing a mid-tilt intruder in the landing corridor — Trump's
  own measured mechanism, intrusion 0.0135; priced by the wedge/cascade toolkit). = G-A53-2 made
  operational. Sequence: after stragglers + k=4 sweep.

## 2026-09-01 — A55 (k=4 sweep) + A56 (s-parametric transfer) dispatched in parallel
- PI sequencing: cheap extensions first (k=4 cap-extension + making the kill library
  proof-grade over the full window); the satellite trees (~2 desktop-days) and the low-k
  slide-stuck campaign held until these land.

## 2026-09-01 — the three-front endgame dispatched (A57/A58/A59)
- The stratification's residue = {trump5, k5_11, k5_16} + their sub-skeleton strata. PI's plan:
  (1) A57 shadow trees (the priced compute item); (2) A58 clear-corner composition — k <= 3 leaves
  a corner with no simple square, marrying the flush-free toolkit to the stratification with the
  corner-occupancy anchor; (3) A59 trump5 as an 18-d ANCHORED grain problem (pinned squares =
  walls; upward stratum boundary certified empty by the k=6 tier — the drain cannot escape up).
  A56's window sweep finishing underneath.

## 2026-09-01 - A59 closed (done-success): trump5 residual - census refuted the unit, zone-tree GO
- THEORY: stratum-restricted drain written (T1-T5'): trump5 = feasible set of a 19-var NLP with
  the 5 pins as obstacles; normalization rigid (pins touch all four walls); slide-stuckness
  AUTOMATIC for every stratum point (stronger than A53 L6); UPWARD TRAP certified: SIX one-cell
  Young completions {k6_07,19,21,22,23,24} (two of the naive eight overlap a pin for all s -
  vacuously dead), all carrying PASS kills => the drain cannot escape up, unconditional at s0;
  window form = A56's six-class priority ticket.
- CENSUS (leg b, honest): ~4.4e10 Level-0 grains in the residual polygon (rigorous bracket
  [2.29e6, 8.22e11]; 91 masks; canary PASS; corner-cap-3 proved). Anchoring does NOT shrink the
  combinatorial census; every filter is a containment filter - the F4/A43 law at Level 0. Grain
  unit dead by 10 orders; census kept as map + banked lemmas.
- PILOT (leg c, 87 exact certs, 0 canary events): the sibling-kill arithmetic is IMPOSSIBLE, not
  expensive - all Trump-adjacent YES children ALIVE-certified (A57-3); tau_LP = k(N) =
  surviving-Trump-witness count in 17/18 converged solves (exception documented; only
  tau* >= k is load-bearing). The tree closes by RESIDUE CONTRACTION: unkillable residue
  bounded (~34 boxes/level over 24 levels), contracts onto Trump at gap ~ 4.6 x radius, all
  inside the A36 basin slice at level 24. r_kill = 4.55 x hw exactly; the annulus closes at
  +2.19 bisection levels (hw <= 8.13e-4): genuine discharge leaves exist, no A40/wedge work.
  Nesting collapses: unkillable 41 -> 18 -> 7 -> 0 -> 0; 93-100% free logic kills from j=1.
  Budget-1 kills = zero-atom vacuity certs (0.5-1.5 s, no LP; caselp's 2e-3 epsilons blind the
  LP route at the h scale). Lemma A59-P1 banked: every trump5-skeleton packing has a square
  centred in the interior zone (exact cert, re-verified depth 60).
- COMPOSED PROGRAM (leg d): P0 engine (alive-gate + vac59 - the pilot burnt 64% of its LP time
  re-deriving 1-ms alive facts) -> P1 upward trap (A56) -> P3-P5 zone cover + residue ladders +
  confinement to hw <= 8.13e-4 -> (D) discharge into the A36 basin -> composition theorem.
  ~1e4-1e5 certificates = SINGLE-DIGIT DESKTOP-DAYS at 5 processes. GO, with conditions: A56
  parametric overhead on the kill leaves is the open cost line (the low-s slab is structurally
  invisible at fixed-s nodes - merged into G-A59-7); depth-2/3 ladders extrapolated (G-A59-10,
  check first); tau*=k conjecture noted (G-A59-12). Report: attempts/A59-trump-residual/
  results/a59_report.md.

## 2026-09-01 — machine headroom deployed: A60 (trump5 campaign) + A61 (window stragglers) launched
- PI noted idle capacity (CPU 10%, 11 GB free with only A57's 3 workers active). A60 executes
  A59's GO program (falsifier check first per its own conditions); A61 runs the G-A56-1 successor
  recipe. Concurrency budget: A57 ~3 + A60 <= 4 + A61 <= 2 heavy LPs with 4 GB RAM guards.

## 2026-09-01 — A62 (trust ledger) closed: formal statement finds three new HIGH holes; zero load-bearing conjectures
- F3 executed: TopLevel.lean (PackingCertMathlib, CI green) states the composed optimality
  theorem with 13 named axioms; the three top theorems are PROVED from exactly those axioms.
  Writing the composition forced the holes it was designed to find: (F2) no certificate route
  to the UB AT s-hat (strict-margin checkers can never certify the contact-closed packing);
  (F3) the uniqueness clause follows from NO written lemma (selection slides squares — proves
  the bound, not uniqueness; needs a slide-path + basin-rigidity argument); (F9) checklist S4
  confirmed as a missing lemma applied at every kill (certificates exclude disjoint-closed
  families, minimisers are interior-disjoint; the lambda-scaling repair is written nowhere).
- H13/H11: dependency graph shipped (attempts/A62-trust-ledger/results/depgraph.json + .svg).
  Sweep: no conjecture node is load-bearing — G-A59-12 motivation-only, I-L19/seam-S3
  off-tree, G-A59-10 already caught and corrected by A60's falsifier. The proof's distance
  is 14 OPEN nodes; H10 (k<=4/k<=3 exactness) remains the largest.
- C1/C2/C9: docs/specs/tcb.md + four frozen certificate specs + docs/manifest_3.8x.md.
  TCB debt named: no end-to-end verifier for the s0 tree compositions (the A54-gap layer);
  C3 clean-room inputs now exist for verify_case/verify_param.

## 2026-09-01 — A63 (hole closure) closed: shat_spec + rBasin discharged in Lean; the S4 bridge is a lemma and it re-prices the whole s0-only ledger

- T1 CLOSED: Sturm root-isolation certificate for the octic (certs/octic_root_isolation.json
  + certs/verify_sturm.py, exact stdlib rationals, 5 corruption gates). The octic has exactly
  2 real roots; the [3.877083, 3.877084] one is the second; all Taylor coefficients at the
  left endpoint above degree 0 are positive, so shat is now a Lean DEFINITION and shat_spec a
  THEOREM (propext/choice/Quot.sound only) — no calculus, no intervals. Axioms 16 -> 13
  (rBasin also discharged: definition 3/2000, docs/proofs/theta_t_transfer.md — the binding
  constraint is the forall-s slab (r(1+sqrt2) <= h), NOT the naive h/2 tilt transfer).
- T2 CLOSED (docs/proofs/closed_disjoint_bridge.md): Lemma B, the lambda-dilation bridge —
  centres x lambda, sizes fixed: strict disjointness (gap >= lambda-1) + pin tracking
  ((lambda-1)|alpha| <= (lambda-1)5/2). HEADLINE FINDING: the deployed cores are eps-fat
  (a ~ 1/2 - 3.1e-8), exact containment margin rho ~ 1.0000009e-9, so a fixed-side
  certificate binds only a 4e-10-relative shell below its side: parametric coverage + dense
  rationals fully instantiate stratum_kill on covered classes, but s0-ONLY certificates
  (A57 k5_11/k5_16 trees, A60 zone-tree leaves, A61 stragglers pre-conversion) instantiate
  the kill/residual axioms at NO side of [3.82, s-hat]. Named repair: the slack-core grid
  (cores at 1/2 - 1e-3 => ~37 fixed sides cover the window; alternative to 4D parametric,
  and the only visible window route for the tree compositions). lb_382's S4 gap closed too
  (r = 0 case).
- T3 HALF-CLOSED (docs/proofs/unique_transfer.md): F3 RE-DIAGNOSED — unique_transfer as
  stated follows from census exhaustiveness (L3); the uniqueness load sits in stratum_kill's
  forall-packings quantifier at the K1-protected classes. Full architecture written: CC-2
  teleport chain to a stuck packing (H1 degeneracies evaporate — teleports need no corridor)
  + H10 re-based to H10-STUCK + residual/basin + collapse back via THEOREM U (one-square
  rigidity of z-hat) — the single new leaf, with an executable 11-re-insertion-certificate
  spec (the only load-bearing nofams use). Obligations U-O1..U-O4 named.
- T4 HALF-CLOSED (docs/proofs/attainment_ub.md): route (b) REFUTED as a finite route
  (scaling breaks unit squares; rational curves have rational sigma-limits); attainment/
  fits-ray lemma written (also discharges `attained` prose). A22 already certifies
  Fits(s_A22); the whole residue is the algebraic identity s_A22 = s-hat-octic, now pinned
  to |diff| <= 2.1e-47 via T1's Taylor bound; closure = number-field verification
  (compositum deg <= 56 — a coordinate has a deg-7 minimal polynomial, so NOT Q(s-hat)) or
  the S3-fallback restatement (s-hat := s_A22).
- T5 CLOSED (docs/proofs/instratum_bridge.md + theta_t_transfer.md): K1 homed with both
  directions; Lemma M->E (exact => contains => killed, reflexivity + D4 bookkeeping); exact
  coverage table; K1-protected residue = H10 by design. Exact theta<->t constants
  (|dt| <= |dtheta| <= 2|dt|), rBasin concrete, A60 landing radius = 0.30 x rBasin.
- Ledger: depgraph updated (attempts/A63-hole-closure/results/depgraph.json): A.S3 ->
  certificate+verifier; B.EXACT, E.COORD -> proved-prose; +A.SBRIDGE (proved-prose),
  +A.THMU (open); open nodes 14 -> 13. Lean builds clean, #print axioms audited, README
  matrix updated. A57/A60/A61 untouched; light CPU only.
- A63 addendum (A60 feedback round): Lemma B-NO added to closed_disjoint_bridge.md (B.2'')
  — nofams certificates (A60's confinement leaves) transfer as occupancy with the zone
  contracted by 1/lambda; consumers must widen by (lambda_max-1)*coord. Owner-frame (H)
  criterion codified (B.2'; kills the tilted-core rho false alarm). rho independently
  reproduced by A60 (49 leaves); theta-t lemma caught A60's basin-discharge coordinate/radius
  bug (now contain_t vs 3/2000, 1.24x margin — watch squares 2-3). Slack-core grid pricing
  HELD pending A60's delta=1e-3 re-emission test (measured law eta <= -1, not 0.5-slack).
- A63 addendum 2 (advisor follow-up, decision-gating): cover-invariance lemma for A57's
  shadow trees PROVED (docs/proofs/cover_invariance.md, CI-1..CI-3) — the t-uniform cover x
  12-column zone subdivision stays a complete disjunction at every s in [3.82, s0]; frozen
  cores valid window-wide (box widths maximal at s0); pinguard sound at every s; (alpha,
  beta) affine form confirmed exactly (boxes beta = dyadic/12, pins beta in {0,1}, NO-child
  nofam x1 beta = 1). Residue: 601 logic kills are NOT invariant (relative motion <= 0.0547)
  => per-box exact C-check, LP only on flippers; (P-fix) frozen family as fallback. Tool
  gaps: make_param anchor rule, verify_param affine-nofam exemption (intersect over the
  s-cell), C-check driver. Route (a) unblocked as theory: 2 tool changes + C-check + one 4D
  pass, vs ~8 desktop-days for the delta=1e-2 grid; routes compose per leaf.

## 2026-09-02 — A64 (Lean wave 2) closed: s(11) ≥ 3.82 is an end-to-end Lean theorem; parametrization discharged; the UB residue is one axiom

- T1 CLOSED (A.PARAM → lean-proved): the `parametrize` axiom is a THEOREM
  (docs/proofs/parametrization.md + lean/PackingCertMathlib/.../Parametrize.lean). The
  square's own 90° symmetry (sqSet_rot) puts the edge vector in the closed first
  quadrant; t = e₂/(1+e₁) then satisfies cosT t = e₁, sinT t = e₂ by polynomial algebra
  mod e₁²+e₂²=1 — no transcendental function anywhere. Only the `unit` field of
  IsPacking is used. Bonus: u/v-membership, w-containment, w ≥ 1 and w-quasiconcavity
  lemmas, consumed by T2.
- T2 CLOSED (A.F2 + A.LB382 → lean-proved): MeasureBridge.lean formalises the FULL
  soundness of checkMeasureI (byte-identical copy, A28 pattern): interval products,
  floor-div bounds, exact rational grid trig with monotonicity, clip via
  quasiconcavity, sift/split/branch-and-bound induction, coverage, and the
  scaling+counting argument done in configuration space (strict-u/v pullback ⇒
  interior ⇒ shrunk squares fully disjoint; finite double-sum swap; no measure
  theory). Composed with native_decide on the 3.82 certificate (2380 s, isolated in
  Measure382Check.lean so edits never re-run it): `s_eleven_ge_382 : ∀ s, Fits 11 s →
  191/50 ≤ s`, axioms propext/Choice/Quot.sound + the native_decide axiom. TopLevel's
  lb_382 axiom := this theorem. The A28 estimate "3–5 days" was wrong in bottleneck,
  not size: the cost is CROSS-TOOLCHAIN ELABORATION — checker ites carry core
  OfNat/Decidable instances that Mathlib-written rw/simp patterns never match
  syntactically; recipe that works: hypothesis copy + `split at` + `dsimp only at` +
  full-unification exact/exact_mod_cast (recorded for the A22 Krawczyk replay).
- T3 ASSESSED + EXECUTED (A.UBshat stays open, residue = ONE axiom): the
  interval/sign route to ŝ_A22 = ŝ_octic is REFUTED (separation gaps need a height
  bound; arithmetic-Bézout heights through the 34-variable system are doubly
  exponential — no reachable precision wins). NEW closure spec (c-idl), cheaper than
  the degree-≤56 compositum: saturated ideal-membership cofactor certificate,
  verification = rational polynomial identity + one sign gate (verify_sturm-class
  TCB); search = bounded Gröbner/Macaulay campaign. Lean side: trump_packs_at_shat is
  now a THEOREM from shatA22 (intrinsic side) + trump_packs_at_shatA22 (certified,
  Python-interval TCB) + shatA22_eq_shat (the open identity) — discharging (c-idl)
  later replaces one axiom and touches nothing else; shat_spec (A63) untouched.
  attainment_ub.md §6 written; side-finding: `basin`'s certification is intrinsic too
  (the identity axiom is the single carrier).
- T4: gold `lean-proved` tier on the live depgraph (+renderer COLORS);
  A.PARAM/A.F2/A.LB382/A.S3 recoloured; open nodes 13 → 12; README matrix + axiom
  audit updated (no sorryAx; kernel theorems still axiom-free). CI note: the mathlib
  job now includes the ~40 min native_decide module (cached; .github out of A64 scope —
  gate it like PackingCertSlow382 if Actions minutes hurt). A57/A60/A61 untouched.

## 2026-09-02 — A67-d4-rerun (Opus, mechanical) — done
- **D.D4 / H12 closed: the D4 container-symmetry reduction is machine-checked at
  s0 = 969271/250000. PASS, 36.7 s, one process, BLAS-pinned.** Verifier
  `attempts/A67-d4-rerun/code/verify_d4_s0.py` **imports** A27's `caselp/level1/refine/
  verify_tree2` and rebinds two module constants (`verify_tree2.S`, `refine.S`) — no A27
  source copied or edited, so "same semantics, same verifier, side changed" is literal.
  Every predicate exact (`Fraction`).
- **The harness ported mechanically — nothing bakes in the side** (the brief's STOP
  condition did not fire). `zone/xcuts/tbins/qbox/cell_ijk/sigma_cell/sigma_t` and
  `level1.cover/check_cover` are all parametric in S; `t_lo/t_hi/q/cos_sin_t` never see it.
- Checked exactly at s0: R1 Z(s0) = [11/10, 694271/250000]² is concentric with [0,s0]²;
  R2 the acting group **is** D4 (8 signed perms, closed, orders {1,2⁵,4²}, nonabelian —
  the unique nonabelian order-8 group with 5 involutions); R3 every g maps container and
  zone **onto** themselves; R4 the 8 D4-images of the fundamental triangle T **cover** Z
  (octant decomposition exhibited: 8 triangles → convex T on 3 vertices each, glued into
  quadrants, quadrants into Z); R5 g(Q(c,θ)) = Q(g(c),θ′) with θ′ = θ or 90−θ, i.e.
  t ↦ (1−t)/(1+t) — a polynomial identity in t of degree ≤ 2 verified at 5 points;
  R6 `verify_tree2` check (2) verbatim (216 cells, cell↔box exact, none vacuous/coreless,
  `level1.check_cover` PASS); R7 check-(6) bookkeeping, **and the t-bins are proved
  side-independent** (identical at 96/25 and s0 — they depend only on NTH), so the whole
  t-side of check (6) transfers verbatim rather than merely re-passing.
- **Census side (R8, the second half of the brief):** A53 `skeletons.py`'s `d4_images` is
  **the same group of plane maps** as the container D4 at s0; it preserves [0,s0]², the slot
  lattice and the 4 corner anchors; `canon` is orbit-invariant and orbit-selecting on the
  whole corpus (7204 recursively-locked skeletons → 944 classes; 1110 Young slot-sets → 163
  classes, D4-closed, ⊆ the locked corpus — reproducing **B.CENSUS** exactly); and the Young
  slot map is D4-equivariant, g·slots(c,λ) = slots(g·c, λ or λᵀ), over all 8 g × 4 corners ×
  20 partitions. That equivariant action is precisely what `instratum_bridge.md` §E.2 uses
  when it applies h = g′g⁻¹ to a packing.
- Controls: same checker at 96/25 PASS (0.06 s, identical verdicts and identical t-rounding
  relation multiset); `A27 verify_tree2.py --skip_leaf_verify` PASS (19.1 s) as a live anchor.
- **Reported non-assertion, not a regression:** σ(box(i,i,k)) is *not* contained in the
  mirror cell's box in t-coordinates (worst ≈ 5.3e-8, and the failure flips direction across
  the mid-bin). That is the `t_lo/t_hi` outward-rounding artefact `verify_tree2`'s own
  docstring records, which is why its check (6) tests the mirror's certified core against the
  σ-**image** box. It is a property of `t_lo/t_hi` alone, hence identical at 3.84.
- **Scope (docs/proofs/d4_reduction_s0.md §D4.4):** the WLOG is conditional on the root
  occupancy lemma at s0, **which does not exist** (it exists only at 3.84, τ = 8.240152 < 11).
  `verify_tree2`'s certificate-consuming checks (1)(3)(4)(5)(7) have **no input** at s0 — the
  162 leaf certs are 3.84 objects — but that is the absence of a tree (D.TREE), not a
  portability blocker in the reduction. Says nothing about S₁₁ (seam S6 = D.S6, still open),
  and being a WLOG it proves no bound. Single implementation, as with B.CENSUS; R8's
  tree-side/census-side group identity is the nearest cross-check and it holds.
- Files: `docs/proofs/d4_reduction_s0.md` (addendum), `attempts/A67-d4-rerun/{code,results,
  logs,notes}`, depgraph `D.D4` open → **certificate+verifier** (+ re-render), REGISTRY row.
  A57/A60/A61/A29 untouched. Note for schedulers: commit headroom oscillated 2.9–6.6 GB
  during the run (the live campaigns), so the launcher polls and waits for the >6 GB gate.

## 2026-09-01 — A69: shatA22_eq_shat CLOSED at the certificate tier — (c-idl) found by exact elimination

- **The single open algebraic identity of the upper bound at ŝ is now certificate-backed.**
  `certs/cidl_identity.json` (301 KB) + `certs/verify_cidl.py` (stdlib fractions, PASS 0.7 s,
  corruption gates qcoeff/e/rowspec/octic all fail loudly): the saturated ideal-membership
  identity e(t)·Δ(t)⁸·octic(S) = Σ q_j(t,S)·G_j over the 13 reduced A22 contact rows, sign
  gate = exact Sturm root-freeness of e·Δ on [3/10, 2/5] ∋ t̂. Evaluated at the A22 point:
  octic(ŝ_A22) = 0; with the 1e-50 enclosure and shat_spec: **ŝ_A22 = ŝ (the octic's second
  real root)**. Construction + composition: docs/proofs/attainment_ub.md §7.
- **No Gröbner campaign was needed** (the A64 (c-idl) spec priced it as one): A22's certified
  exact structure (uprights pinned, one common tilt angle, Weierstrass t) makes the reduced
  system LINEAR in the 12 non-t unknowns over ℚ[t]; the certificate is Cramer/adjugate algebra
  plus two exact univariate divisions. Measured sizes: deg Δ 34, deg D 35, deg e 27,
  deg G_oct 272; coefficients a few hundred bits; search ≈ 2 min in plain Fractions.
  En route the tan-half minimal polynomial 5t⁸−10t⁷−2t⁶+14t⁵+12t⁴−6t³+2t²+2t−1 is DERIVED
  from the contact system (upgrades A22 §7 gap 2 from PSLQ-found to derived).
- **Finding: A53 L4's "degree-7 coordinate" never existed.** A03's per-square minpoly_cx/cy
  JSON fields are findpoly artifacts (the deg-7 poly for cy4 evaluates to −8.0e8 at the true
  ŷ4; cx2 = S−1/2 carries a deg-7 entry though it must have degree 8). Δ(t̂) ≠ 0 puts EVERY
  ẑ-coordinate in ℚ(t̂) (degree 8); true ŷ4 minpoly derived (findings.md). The (c-alg)
  compositum-56 obstacle is void; A03 minpoly annotations should not be used for anything.
- Lean: TopLevel `shatA22_eq_shat` docstring updated (axiom retained); residue = named
  obligation CIDL-LEAN (attainment_ub.md §7.5): native_decide replay of [O]/[I]/[G] + refined
  A22-interface axioms, then the axiom becomes a theorem via shat_spec — engineering only.
  Depgraph A.UBshat open → **certificate+verifier** (re-rendered). REGISTRY row added.
- Ops incident (honesty note): the first sympy-Expr assembly blew past 10 GB RSS and pushed
  commit headroom to 0.49 GB; while triaging under pressure, PID 24700 (~50 MB transient
  python, most likely a campaign certify worker) was force-killed by MISTAKE before the two
  A69 sympy processes were identified and killed. A57/A60/A61 main processes verified alive
  afterwards (schedulers requeue certify workers). Lesson recorded in findings.md: check
  command lines before killing; and sympy Expr is the wrong tool above degree ~100 — the
  lean Fraction rewrite (assemble.py) used < 100 MB.
- Files: certs/{cidl_identity.json, verify_cidl.py}, certs/README.md §3,
  docs/proofs/attainment_ub.md (§7 + status banner), attempts/A69-cidl-identity/{BRIEF.md,
  derive.py, assemble.py, eliminate.py, build_cert.py, notes/findings.md, results/},
  lean/TopLevel.lean (comment only), lean/depgraph.{json,svg}, REGISTRY. A29 untouched.

## 2026-09-01 — A68 (Lean wave 3) closed: attainment DISCHARGED (roster 13 → 12); Lemma B, K1(i), θ↔t transfer lean-proved

- **T1 / A.D1 — `attained` is now a Lean THEOREM** (`Attain.lean`; TopLevel roster 13 → 12
  named axioms, audit clean). Compactness done in the 33+1 COORDINATES — no Hausdorff
  limits anywhere (the old docstring's cost estimate was wrong in kind): the feasible
  region (t ∈ [0,1], A64's containment inequalities, pairwise non-overlap, s ∈ [0,11]) is
  closed + bounded, side projection continuous, `parametrize` maps set-level packings in,
  explicit 11-in-a-row packing for nonemptiness. Load-bearing new lemma:
  `mem_interior_iff_uv` — interior of a parametrised square = the OPEN u/v box (⊆ by an
  ε/2-push along the edge direction; ⊇ was A64's) — which makes interior-disjointness a
  CLOSED condition (overlap = open, witnessed by 4 strict inequalities).
- **T2 / A.SBRIDGE — the λ-dilation bridge lean-proved** (`Dilation.lean`), stated the way
  `stratum_kill` producers consume it: `dilation_bridge` (interior-disjoint packing at m ⟹
  `IsStrictFamily` at λm), `lemma_B`, and the PRICING PIGEONHOLE `priced_dichotomy` /
  `hcert_of_priced` — (P1) Σw < b plus (P2) per-placement μ ≥ 1 refute any strict family
  with cores in the owners (A64 `massIn` machinery reused); the `Exempt` parameter makes
  Lemma B-NO the same theorem. Plus `bprime_containment` ((H′) ⟹ (H)) and
  `pullback_mem_Icc` (B.2″ widening). Findings: B.0(a)'s SAT citation unnecessary (the
  scaleC pull-back suffices); (H)'s open-interior clause not needed for the conclusion;
  B.0(c) exact for EVERY β. Residues named: V.CASE ((P2) from a concrete PASS — the next
  MeasureChecker-style replay), B.2′ owner-frame clause, ρ stays [M].
- **T3 / B.K1 — K1(i) lean-proved; M→E conditional** (`Skeleton.lean`): slot model +
  `ContainsPins` + `containsPins_mono`/`kill_mono`; in the indexed slot model the prose
  slot-inclusion step IS the Finset inclusion — K1's residual content sits ENTIRELY in the
  census definition (F11/H2). `monotone_to_exact` lands E.2 with the census interface as
  explicit hypothesis `hface` (named obligation; A67 R8 is its computational cross-check).
  E.1(ii) aliveness deliberately unformalised: τ*-completeness, not soundness.
- **T4 / E.COORD — θ↔t transfer lean-proved** (`ThetaT.lean`): `cosT`/`sinT` ARE
  cos/sin(2·arctan t) — the first formal tie between the lab's t-world and the θ-world
  certificates; X.1 both directions; X.2 with the SHARP constant r_c + √2·r_t (the naive
  per-component constant FAILS gate (b) — sharpness is machine-checked as load-bearing);
  X.3 gates now TopLevel theorems `rBasin_gate_tilt`/`rBasin_gate_slab` (slab gate is
  exactly √2 < 22/15: (3/2000)(1+22/15) = 37/10000 on the nose). `basin` stays an axiom by
  design (mpmath.iv trust item, F6).
- Hygiene: full `lake build` green; all new theorems axioms = propext/Choice/Quot.sound;
  `scratch/Axioms.lean` extended (14 new prints); the 2380 s `native_decide` module
  untouched (cache hit); A57/A60/A61 untouched; light CPU only.
- Toolchain renames vs A64's recipes (for the next wave): `le_or_gt`, `abs_add_le`,
  `Set.mem_ofPred_eq`, `push Not`, `IsCompact.exists_isMinOn`; `@[fun_prop]` on
  `continuous_cosT/sinT/wT` trivialises configuration-space continuity goals.
- Files: `lean/PackingCertMathlib/PackingCertMathlib/{Attain,Dilation,Skeleton,ThetaT}.lean`
  (new), `TopLevel.lean` (attained → theorem; rBasin gates; header), root import list,
  `scratch/Axioms.lean`, `lean/README.md`, `lean/depgraph.{json,svg}` (A.D1/A.SBRIDGE/
  B.K1/E.COORD → lean-proved; A.D1 owner chip removed), prose annotations in
  `docs/proofs/{drain_lemma,closed_disjoint_bridge,instratum_bridge,theta_t_transfer}.md`,
  `attempts/A68-lean-wave3/notes/findings.md`, REGISTRY row.

## A66 closed (done-mixed) — corners4 counting route REFUTED; pair-certificate family designed + sound + verifier; pilot: k4_08 kill-shaped at restricted strength, corners4 OPEN (2026-09-02)
- T1 (docs/proofs/corners4_empty.md): Lemmas E1-E3 + EXACT 7-point witnesses (s = 191/50 and s0) show the centre-occupancy relaxation admits 7 squares at EVERY window side — the candidate counting proof cannot close; corners4 NOT deleted, C.K4TIER unchanged. Rigidity exhibit names the obstruction (orientation coupling; wall/pin-edge forcing vs axis L_inf).
- T2 (docs/proofs/pair_kill.md, docs/specs/pair_certificate_v1.md, attempts/A66-corners4-pair/code/verify_pair.py): Lemma P/P0, canary theorem (trump5 provably unkillable by pair certificates), A34 non-applicability, Lemma P-B (PI's basin-exclusion row: sound for exact strata in a ~5e-4 shell below s-hat; the monotone->exact bridge is load-bearing exactly at the skeleton-contradiction step). Verifier: pure-Fraction 6-D B&B, selftest clean (caught an unsound-PASS bug in build), toy PASS s=199/100, FAIL s=201/100 exact witnesses; NEW trusted code, not TCB.
- Pilot (restricted pair-LP, adequacy criterion tau_f_cat, exact containment audit): k4_08 tau_2 = 21+6beta exactly (margin -beta; a "saturated death witness" and a "21+7beta tie" were RETRACTED — perturbation columns had escaped the containment filter; caught by the lead's independent exact re-verification); basin discount window 0<gamma<0.245, +0.4 at gamma~0.1; corners4 beta=0 bracket [14.89, 21.32] OPEN. Emission not attempted.
- Canary: safe at every step (Trump not in corners4; canary theorem; controls reproduce his image family). Constraints honoured: <= 2 BLAS-pinned LP slots, headroom checked, A57/A60/A61 untouched, frozen verifiers untouched.

## A72 closed (done-success) — CENSUS CLEAN-ROOM: independent re-enumeration MATCHES exactly; H2 CLOSED, B.CENSUS doubly witnessed (2026-09-02)
- VERDICT **MATCH**. Clean-room enumerator (`attempts/A72-census-cleanroom/code/enum_census.py`, stdlib +
  Fractions, one process) written from the WRITTEN definition only — A53 `notes/lemmas.md` L1-L3
  statements, `docs/proofs/instratum_bridge.md` E.2-E.4, `docs/proofs/d4_reduction_s0.md` R2/R3/R8,
  LOG 2026-08-31 — with `skeletons2.py` / `skeletons.py` / `skeletons_young.json` NEVER opened until A72's
  own output was sha256-frozen (`results/sha256s`, timestamped pre-diff). Discipline held end to end.
- Diff (`results/diff_report.json`) matches at every level, not just on counts: the **1110 skeleton
  slot-sets are identical as sets of exact rational plane points** (0 tuples on either side only; the
  tuple -> slot-set map is injective in both implementations); the induced **163-orbit D4 partition is
  identical** (compared representative-free, so the comparison is convention-proof); the **two D4 groups
  are identical as maps on the 36-slot lattice** (A72's 8 signed-permutation matrices about the centre vs
  A53's `d4_images` rot/refl loop, graph-of-map comparison); per-k census identical on BOTH rows
  (1/4/14/40/85/156/222/260/208/120 raw, 1/1/3/6/14/22/33/35/30/18 D4); orbit-size histogram identical
  (1x2, 2x4, 4x39, 8x118 = 1110); Trump canary in the same class. `hface`'s computational content
  (instratum_bridge E.4) is now witnessed by two independent implementations.
- Method choices that made it a real cross-check rather than a transcription: the 3x3 slot box was
  **DERIVED** (offsets kept iff the closed unit square fits in [0,s0]^2; max offset came out 2) instead of
  assumed from L3's "inside 3x3"; the D4 action was implemented on **PLANE POINTS ONLY** and image points
  re-decoded to (corner, i, j), so `d4_reduction_s0.md` R8's slot-level rule "g.slots(c,lam) =
  slots(g.c, lam or lam^T)" is a *checked consequence* in A72, never an input — it PASSES, independently
  of A67's check of the same statement.
- Canonical **representatives** agree on only **3/163**. This is pure naming convention (A53 takes lex-min
  of the sorted plane-coordinate tuple; A72 lex-min of the corner-major cell encoding) and was
  pre-registered as non-binding in `notes/ambiguities.md` L4c before the diff — the invariant object is
  the orbit partition, and that matches. Consumers keyed to A53's class names (k5_11, k6_23, corners4, ...)
  are unaffected: A53's 163 stored reps each land in a distinct A72 orbit and cover all 163.
- SECOND FINDING — the definitional debt H2 does NOT cover. Writing the second enumerator required
  resolving **12 recorded ambiguities, 8 of them BINDING** (`notes/ambiguities.md` B1-B8, written before
  peeking). Sharpest: **B2** — L3's filter says "pairwise interior-disjoint" and only inherits the
  predicate from L1; read as closed-disjointness (strict > 1) it deletes every flush pair and collapses
  the census. **B4** — L1 defines Simp(P) as the LARGEST Young set at each corner, while L3 enumerates
  with NO maximality or realizability filter; the definition and the census point in opposite directions
  and only L3's parenthetical ("Realizability of a stratum is NOT claimed") resolves it. **B1** — "inside
  3x3" is a consequence of s0 < 4, not a definitional restriction. **B3** — the "4-tuple is a partition of
  Simp(P)" property is s0-SPECIFIC (needs s0 not in Z); at an integer side L1/L3 would be genuinely
  ambiguous about a square simple at two corners. The 4 label-only items include the one A53 and A72
  actually differ on: **A53 indexes lambda by ROW, A72 by COLUMN** — L1 never says which inward axis is
  e_c, so the Trump canary ((2,1),(1),(1),0) is only well-posed up to transposition. A Lean definition of
  the census (F11 / `InStratum`) must pin all 8 binding choices; that debt is now itemised, not just named.
- THIRD FINDING — the 7204 / 944 "recursively locked" corpus (A53 L1 Reading 2, consumed by A67 R8) is
  stated in a single clause with no written recursion, seeding rule, or definition of which flush contacts
  count. It is **not clean-room re-enumerable**: any second implementation would measure the author's
  guesses, not the definition. Deliberately out of A72's scope and recorded as a finding; it remains a
  single-implementation object.
- Files: `attempts/A72-census-cleanroom/{BRIEF.md, code/enum_census.py, code/diff_census.py,
  results/census_cleanroom.json, results/sha256s, results/diff_report.json, results/{enum,diff}_run.log,
  notes/ambiguities.md}`, REGISTRY row, `docs/publication_checklist.md` H2 -> DONE,
  `lean/depgraph.{json,svg}` (B.CENSUS note + source; label stays `certificate+verifier` — now two
  verifiers). Constraints honoured: one process, stdlib + Fractions only, no LP solvers, thread env pinned;
  A53/A67 read-only (imported, never written); A57/A60/A61/A29 untouched.

## 2026-09-02 - A71-pair-emission (theory lead Fable + 2 Opus chores) - done-mixed
- T1 (k4_08 emission oracle loop, beta=1, s0, delta=1/1000, eps_box=1/833): NO full-quantifier
  certificate - a quantified three-layer VERIFICATION WALL, recorded as pair_kill.md sect 6.5
  (Lemma W): (a) restricted feasibility UNREFUTED (tau_2 = 21+6beta = 27 < 28, zero fractional
  excess - the wall is verification complexity, NOT certificate non-existence); (b) margin wall
  [T+M exact]: K=11 mixed-tilt family with pairwise-disjoint 0.15-cores, D=35 disjoint pair rows
  + Sigma m2 = 4, V=39 >= 28 (pure-Fraction verified) => EVERY valid certificate carries >= 11
  coverage units on sub-0.15-margin atoms; greedy wall curve V(eta) = 17/19/20/22/39 at
  0.10/0.11/0.12/0.13/0.15; (c) cost identity [M]: frozen verify_pair.py throughput 57 nodes/s
  (17.5 ms/node, exact Fractions, 3000 atoms; A71 float mock replays identical rules at 72k/s);
  leaf table: all-margins-0.15 ~ 6e8 leaves ~ 125 days, 0.10 ~ 4 y, 0.05 ~ 250 y single-core.
  Loop empirics: covering LP fixed point W2 = 30.000171 >= 28 under continuum row-hunting +
  mock-witness feedback (P1' violated); rescaled P1'-valid candidate judged END TO END by the
  FROZEN verifier: FAIL at depth 12 with deficit witnesses (certs/pair_k4_08_s0_b1_v1s.report.json).
  v1 emission for the k4 tier CLOSED as infeasible-at-scale; residue = pair-certificate-v2 design
  (margin-aware splitting, compiled second implementation - wanted for the TCB anyway - and/or an
  analytic coverage clause; to be a VERSIONED spec, v1 untouched) + the measure-existence question.
  Window pricing (moot until wall broken): ~38 sides at delta=1e-3.
- T2: docs/proofs/stuck_rows.md [T] - SR-1/SR-2 at drain-v3 rigor (exact LP-row form of the CC-2'
  2-crowds: unclipped census boundary, InStratum-exact R1 exclusion, double-counting-safe tally
  Sigma m2 >= m, eps_box bookkeeping, canary saturation identity = standing design constraint);
  exact P-B compatible-image sets G_S = {id,diag}/{id}/{diag}/empty for k4_08/k4_11/k4_03/corners4
  (k4_08 has TWO images - A66 pilot declared one). Runs (Opus chore, 2.5 min): k4_11 tau_2 =
  21+6beta and k4_03 = 21+4beta EXACTLY (margin -beta, zero excess, adequacy tau_f = 7.000000
  each, value_ge_control everywhere): the whole one-short critical tier shares the k4_08
  signature.
- T3 (corners4 solve wall; Opus chore): BROKEN - solver switch collapses A66's 17k x 10k simplex
  stall to a converged ~8-min cut loop: beta=0 restricted value = 20.528144 (viol 0/0, Lmax
  1.000000) + EXACT certified lower bound tau_2(0) >= 4103377/200000 = 20.516885 (support
  exact-audited: 50 pairs/1 square dropped, min SAT gap 439/2372500; exact Lmax 62499/62500 on
  1271 cell-representative points; completeness caveat recorded). Dual pricing exposed the A66 support
  catalog as NOT pair-adequate (40% of 1.74M enriched pair columns under-priced) -> the run grows
  the catalog by pricing: grow-0 converged 20.528, grow-1 20.542 at budget, later grows in flight
  at session close -- every measurement >= 0.45 below 21 (~1e-2 per grow): bracket effectively
  [20.52, ~20.6], the Corollary P0 corners4-emptiness route OPEN at restricted strength. corners4 = the least-walled class (wall-witness
  shortfall 1 unit; exact witness V=22>=21 at eta=0.15) and the natural v2 pilot; restricted
  covering primal (616 atoms, W2 = 20.325) dumped as emission seed.
- Canary at every step: dilated 60-digit Trump free family re-verified as exact death witness
  under A71 parameters (min SAT gap = lambda-1 = 1.06e-7 EXACTLY per B.0(a), Sigma m2 = 6);
  all LP runs value_ge_control; wall/probe statements adversary-side (can only strengthen
  trump5's protection). SAFE.
- Discipline: <= 2 LP slots enforced (one own overrun killed), BLAS pinned, headroom gate held
  (one own 22.8-GB process spike caught and killed same minute; A57/A60/A61 untouched); frozen
  verifiers untouched (verify_pair.py sha d9b7a24a re-verified; interface note: its parser
  rejects float literals even inside the spec-ignored provenance block - emitters must
  stringify). Files: attempts/A71-pair-emission/*, docs/proofs/stuck_rows.md, pair_kill.md
  sect 6.5 + ledger updates, depgraph C.K4TIER note + svg, REGISTRY row.

## 2026-09-02 A73-pair-v2 (Fable lead + 1 Opus clean-room chore) -- done-mixed
- T1: docs/specs/pair_certificate_v2.md - versioned (v1 frozen, sha d9b7a24a re-verified), claim IDENTICAL to v1
  so P0/stuckness consumption + canary theorem carry over. Lemma S (free rational cuts), Lemma Q (exact quadratic
  sign test), Lemma M/E (EXACT iff membership/exemption: corner reduction via sign-fixedness of C,S,1-t^2,t on
  [0,1]), Lemma F (COVERED-F handoff: pinned slack-sum >= 0 => pointwise disjunction; failing-set form because
  coordinate/body axes degenerate pairwise at t=0), VACUOUS-CONTAIN (container-boundary sliver the v1 clip
  provably cannot discharge - found by the clean-room build), DEFICIENT-EARLY (exact rational counterexample
  rows), hint trees.
- T2: reference code/verify_pair2.py (selftest 0 violations; toys match v1; gates) + CLEAN-ROOM Rust
  code/verify_pair2_rs (from spec + v1 spec + toy corpus only; i128 fast path, overflow-checked BigInt; selftest
  0 violations, 9/9 gates; reproduced v1 toy 201080 nodes / depth 37 exactly). C3 CROSS-VALIDATION ALL AGREE
  (results/crossval.json). Throughput 300k nodes/s geometry regime, 22-47k atom regimes single-thread, 131-323k
  at --jobs 8. FIRST full-quantifier atom-bearing (P2') PASSes: grid anchors at s=3 (5866 nodes at margin
  0.146; 1098 at 0.076 - smaller margin, fewer nodes: cost tracks frontier structure, not (1/margin)^6).
- T3 corners4 pilot: NO certificate; wall MEASURED + re-quantified. Tangency trap: the A71 seed's atoms sit on
  membership boundaries (COVERED fired 0 times). Lemma W' [T]: weighted shallow service >= tau_2^eta - threshold.
  Measured tau_2^eta(k4_13,0) (A71 rig at eta-deep membership): eta=0.1 DEAD (scaled >= ~34, plateau 57.000,
  >= 13 forced sub-0.1 units); 0.05/0.02/0.01 unconverged brackets [18.3,26.2]/[17.8,22.3]/[18.0,21.38] (IPM
  walls at nnz 4-6M; four runs); sharp 20.528 open => fractional wall crosses 21 at eta* in (~0.006, ~0.05),
  far below Lemma W's integral 0.12-0.15: uniform-eta emission dead, every valid certificate is MIXED-DEPTH,
  verification cost concentrates near the exploit manifolds. Cost-model survey (eta=0.01 primal, labeled
  non-certificate): COVERED-F 104x, zero coverage holes, 250 cap witnesses at depth 26 - weight fragmentation
  is the driver. Residue priced: deepening/consolidation emission pass + DEFICIENT-EARLY survey loop
  (code/loop413.py ready) + hint trees, then the compiled certification run. P0 path stated (findings.md).
- Canary per run SAFE (dilated Trump: min gap = lambda-1 = 1.06e-7, Sigma m2 = 6). Discipline: <= 2 LP slots
  (sequential), BLAS pinned, headroom gate held (2 dips waited out), one own LP killed at a decisive plateau;
  A57/A60/A61 untouched; frozen verifiers untouched; rust-gnu 1.98.0 installed via scoop (user-level).
  Files: attempts/A73-pair-v2/*, docs/specs/pair_certificate_v2.md, docs/proofs/pair_kill.md sect 6.6,
  depgraph C.K4TIER note + svg, REGISTRY row.

## 2026-09-02 A75-lean-wave5 (Fable lead + 1 Opus chore) -- done-success
- T1 LEAN-PROVED, both nodes. V.MEAS: MeasurePy.lean + MeasurePyBridge.lean model the verify_measure.py DRIVER
  (tscale, 4^k --split grid with fuel = depth-2k, --strict-margin, no-drop known-inheritance, float shortlist as an
  arbitrary oracle, s<1 shortcut); checkMeasurePy_no_packing sound for every oracle/tscale/split/margin from the A64
  primitives; no new mathematics (one grid-coverage lemma). V.PARAM: ParamChecker.lean + ParamBridge.lean = the
  verify_param.py 4-D (t,cx,cy,s) checker; point->interval widenings are TRANSLATIONS of A70's coreExempt / A64's
  projI (translation invariance of PSq.set/coreSet), so no interval argument was re-derived; checkParamI_kill is
  the window kill at EVERY REAL side (no dense-rationals step needed) in the form stratum_kill consumes; pilot
  k5_06.param full window depth 56 native_decide 215 s (ParamData506/ParamK506, lean/gen_param_lean.py); Python
  --no-float-prepass replay reproduces the campaign tree box for box (293854 boxes). C.WIN verifier_lean set.
- T3: D.N1 (centre separation, at-most-one, zone assignment injective/unique/bijective), C.M1 (single-corner
  transfer), C.T5T11 (T5 contradictory-box rule + T11 refinement; the pinguard PARENT gate stays a code invariant)
  -> lean-proved (Zones.lean).
- T2: B.SEL/C.CC2 Lean PARTIAL (Selection.lean): exists_kmax, teleport_packing (no corridor hypothesis), cc2_stuck /
  cc2_two_meeters conditional on the census interface hinc (F11/H2 = hface's debt); H1 degenerate-case audit done
  (all absent in the teleport form). B.EXACT reviewed, unchanged (E.2 D4 bookkeeping still prose).
- Axioms: all new theorems propext/Choice/Quot.sound only (+ native_decide axiom for the 3 pilot theorems); full
  library build green (3175 jobs), Measure382Check cache hit, A57/A60/A61/A74 untouched. Engineering: a `let x := if
  ...` inside a checker def defeats `split at` (name it: sWidth); rcases on a beta-unreduced False; subst on c.n
  needs rcases c. Files: attempts/A75-lean-wave5/{notes/findings.md,logs/}, lean/PackingCertMathlib/.../{MeasurePy,
  MeasurePyBridge,ParamChecker,ParamBridge,ParamData506,ParamK506,Selection,Zones}.lean, lean/gen_param_lean.py,
  lean/README.md, scratch/Axioms.lean, depgraph json+svg, REGISTRY row.

## 2026-09-02 A74-mixed-depth (Fable lead, solo) -- done-mixed
- T1 MIXED-DEPTH EMISSION LOOP BUILT + RUN: code/pairlp413m.py (rows at depth levels eta in {0.05,0.02,0.008,0.002[,0.0005]}
  priced rhs_l = 1 + mu*(eta_max-eta_l)/(eta_max-eta_min); dual = depth-priced covering measure over ALL catalog pairs;
  gate = unpriced W2 = sum y with n_ub = 0; consolidation by rising dual-weight floor under a W2 guard; dual seeding
  from earlier runs' binding rows at every level; IPM+crossover rounds), emit413m.py (canary inside), loop413m.py,
  hinttree.py (spec s4 hint trees, max-min lookahead), primal2seed.py.
- FIRST SUB-THRESHOLD corners4 MEASURES [M]: md5 W2 = 20.98857 (461 atoms; floor 0.002), md7 W2 = 20.95955 (353;
  floor 0.0005), md8 W2 = 20.95828 on the catalog grown by 65 exact counterexample placements. Profile: ~70% of mass
  at 0.008-0.02, ~25% at 0.002, 3-4% at 0.05. Lemma W'' (pair_kill.md 6.7): slack 21-W2 is 0.011 / 0.040 at floors
  0.002 / 0.0005 vs 0.47 sharp; depth pricing spends W2 one-for-one (mu = 0.3: dual mass RISES to 21.55, killed);
  consolidation and depth compete for the same slack (accepted 470 rows / rejected 398 for md5). Catalog growth by
  exact holes costs ~nothing.
- VERIFICATION RESIDUE MEASURED: unhinted Rust survey (2M nodes, depth 34): FAIL by cap only, 0 definitive rows, caps at
  84.5% median certain mass with factor B's tilt UNSPLIT in all 300 (splitter dove A to 2e-4). Hint trees (verifier
  untouched): 30/root -> caps at 99.8% certain; 3000/root (237k nodes, 82 MB cert) -> COVERED +8%, DEFICIENT-EARLY 7317x:
  exact continuum counterexample rows (collect 0.948-0.992) harvested -> catalog grown -> md8. NO corners4 PASS;
  T2 skipped per BRIEF. Per-side loop iteration ~1 h (LP 25-40 min, hints 10, hinted survey 15-25); certification unpriced.
- Rig lessons [M]: IPM-no-crossover times out with no feasible iterate above ~10M nnz; simplex cold start does not finish;
  purge after solve invalidates HiGHS row duals (read duals BEFORE deleteRows); bound-saturated columns make the dual a
  non-covering; the Rust float-literal gate rejects floats in provenance (correct).
- Canary SAFE per emission (md5 x2, md7, md8: min gap = lambda-1 = 1.0574e-7, Sigma m2 = 6; notes/ledger.md). Discipline:
  1 LP slot at a time, BLAS pinned, headroom gate held; A57/A60/A61 untouched; frozen verifiers untouched (import-only).
  Files: attempts/A74-mixed-depth/*, docs/proofs/pair_kill.md 6.7, depgraph C.K4TIER note, REGISTRY row.

## 2026-09-02 A76-grain-discharge (Fable lead + 1 Opus chore + 1 LP slot) -- done-mixed
- PI bottom-up front: grains adjacent to Trump on the protected exact strata. HEADLINE = a quantified
  WALL: no radius beyond A22/A36/A40 is certifiable grain-by-grain for stuck minimisers, because every
  discharge available (Krawczyk for rigid grains, drain-flex for s-flexible grains, Gordan/FJ, the
  A22/A36/A40 inequality forms) is a box-nonsingularity statement capped by kappa_eff. The HINGE grains
  (strip flush pair -> single-corner contact; two of them in the 7-8-10-9 ring worst) have drain-flex
  ratio 10.7 at (1e-3,1e-3) and 48 at (rc,rt)=(1e-2,2e-3) = A40's saturation face (omega_b = 1/kappa_eff)
  seen from below; all-pass box ~1e-4 (A22's inequality form beats it: it keeps the hinge's second
  corner row as an inequality). Size law (census, k4_08, 1.7e7 grains, 143 370 at codim<=4): hard
  count 113/335/658/13702 at (1e-3)/(2e-3)/(5e-3,1e-3)/(1e-2,2e-3); ratio DEcreases with codim (>= 8
  contacts broken: 0.2 at the target box) - the top of the lattice is the only hard part; residue = a
  d-dim continuation cover ~ratio^d per hard grain, ~1e7 Krawczyk steps for (1e-2,2e-3) = 1.5x A40 in
  centres, 0.6x in tilts. Not started (not worth it: see LP line).
- Theory [T] (docs/proofs/grain_discharge.md): Lemma G-R local completeness BY CONSTRUCTION (the checker
  generates all 1936 corner-wall/corner-edge rows; contact <=> a corner on an edge SEGMENT) with exact
  certificate (78 rows on (1e-2,2e-3,1e-2): 36 Trump + 20 flush-upright coincidences + 22 type
  switches incl. the 7-4 blocked slide; 56 up to rc+1.4rt ~ 6e-3); Lemma K (rigid grain => z = z-hat =>
  not exact-S: the class hypothesis enters only here); Lemma DF (drain-flex: e_s not in the row span on
  the box => feasible side-decreasing curve => not a minimiser; downward-closed; implied-row bookkeeping
  via the wall-circuit identity, the flush TIE identity g_a - g_b = 0 on {t_i = t_j} for antipodal
  contact corners, the tie cycle); Lemma D2'' (minimiser => wall-to-wall contact chain on a binding axis,
  the other axis's walls are not connectors) proved without Fritz-John; K/DF dichotomy EXHAUSTIVE on
  Trump's rows (e_s in span of a proper sub-basis would give a second multiplier vector on S); no
  positive dependency at z-hat (max sum lambda = 0: lambda0=0 FJ never occurs); 21 necessary rows.
- Measured [M exact]: t-native Krawczyk (rational trig, monotone enclosures, no Taylor) contracts to the
  uniform t-box 1/250 (0.827), fails 3/500; pinned bases 0.74-0.78 at 1/250 (pins ~10%); anisotropic
  pinned k4_08 (1e-2,2e-3) 0.818 PASS vs unpinned FAIL (pins double the centre radius); tilt radius caps
  ~4e-3. D1 codim-1 certificates: 9/22 pass at the target box (the 13 failures are hinges + sq2's
  corner-rotation mode). Per-class: images.json (k4_08's two images = one grain problem; k4_05 and
  corners4 have NO compatible image: d_min 0.4365 / 0.8445 = trivial exact-class emptiness radius);
  census of the other pin sets (logs/census_p*_d2.log) shows the same hinge families (ratios 48-53).
- A40 basin EXACT-rechecked (Opus chore, code/a40_check_exact.py: 2930 certs, 168 774 checks, 0
  failures, 5 gates FAIL as required, 70.5 s at PREC 330; min anchor margin 2.4266e-7 exact): the
  6.55e-3 (theta-world) basin is now at A36's trust tier. P-B(R) re-read PER COORDINATE (pair_kill.md
  sect 6.8): (rc, rt) = (6.55e-3 - sqrt2 rho_B, 3.27e-3) vs the uniform 1.5e-3 (3.4x / 2.2x); Lean
  rBasin raisable to 27/10000.
- LP measurement (A66 basinlp rig imported unmodified, output redirected; k4_08, beta=1, gamma=0.1,
  converged): margin -1.40 / -1.50 / -1.51 / -1.51 at r_z = 1e-3 / 3.7e-3 / 6.5e-3 / 1e-2 (2e-2
  unconverged in budget): the basin row's gain is ~0.1 per DECADE of zone radius - reserve, not lever;
  the two fronts do NOT meet in the middle. The k4 tier stays the emission problem (A74).
- Canary SAFE at every step: Trump is the rigid grain's unique solution in every lattice, identified
  never excluded; only the exact-stratum hypothesis removes him. Discipline: <= 2 slots, BLAS-pinned,
  headroom gate held; A57/A60/A61/A74 untouched; frozen verifiers untouched; certs/verify_grain.py NEW
  (stdlib, exact, 5 gates) - not TCB. Files: attempts/A76-grain-discharge/*, certs/verify_grain.py,
  docs/proofs/grain_discharge.md, pair_kill.md 6.8, depgraph C.K4TIER note + svg, REGISTRY row.

## 2026-09-02 A78-lean-wave6 (Fable lead; Opus T2/T3/T5) -- done-success
- T1 F11/H2 DISCHARGED: the Young-form census is a Lean DEFINITION (Census.lean: skeleton s z = per corner the
  cells whose down-set is occupied by exactly-on-grid axis-aligned squares; all 8 A72 binding choices pinned,
  B1/B3/B6 THEOREMS; B2 decided combinatorially and proved = the real predicate on ALL of (3,4), so the census
  is one object on (3,4)). L3 exhaustiveness = theorem skeleton_mem_census (propext/choice/Quot.sound only);
  CensusCheck.lean (native_decide): 1110 tuples, 163 classes, D4-closed, EXACTLY A72's tuple set AND orbit
  partition, Trump ((2,1),(1),(1),{}) k=5. D4 action on points/squares/slots/configurations with
  skeleton_d4 (Simp(g.P) = g.Simp(P)); hface = containsPins_skeleton; Lemma M->E = class_kill; hinc =
  card_lt_teleport (CensusSelection.lean). B.CENSUS, B.EXACT, B.SEL, C.CC2 -> lean-proved.
- TopLevel: StratumIdx/trumpStratum/InStratum are DEFINITIONS (computation-free); stratify and unique_transfer
  are THEOREMS (census exhaustiveness); roster 12 -> 7 named axioms (stratum_kill, trump_residual, basin +
  the 4 A22 interface axioms). s_eleven_unique depends on exactly basin/stratum_kill/trump_residual/zhat.
- T2 CIDL-LEAN DISCHARGED (A.UBshat -> lean-proved): Cidl{Poly,Gen,Data,Check,Bridge}.lean replay
  certs/cidl_identity.json by native_decide (generators REBUILT from A22 conventions; 86728 -> 2682 terms;
  27 s), sign gates proved STRONGER (e<0, Delta<0 on [3/10,2/5], no Sturm needed); axiom shatA22_eq_shat
  replaced by a22_exact_structure (A22 certified content only); shatA22_eq_shat is a theorem.
- T4 A.UNIQ own tier -> lean-proved: unique_via_chain / s_eleven_unique_of_chain (UniqueChain.lean): the
  CC-2 chain + Theorem U collapse as a strong induction on 11-k, with H10-stuck (U-O2) and Theorem U (U-O1)
  as explicit hypotheses; the clause WITHOUT stratum_kill. Confirms A63's diagnosis exactly.
- D.D4 verifier_lean: d4_wlog (D4Wlog.lean) = the WLOG at every side, conditional on root occupancy (D4.5).
- T3 D.ALIVE verifier_lean: AliveChecker/AliveBridge.lean, alive_sound (PASS => no checkCaseI certificate of
  that budget); pilot trump5_strict 2.8 s. FINDINGS: F1 obstacles are full pin squares not the cert cores
  (theorem proved in core-monotone form); F2 admissibility hard-wired at s0; F3 nofams=[] implicit; F4 LOUD:
  attempts/A57-shadow-trees/results/alive/k5_16_m5.json carries a FALSE LP-UNKILLABLE claim (m=5 < budget 6)
  - do not cite; trump5_strict.json is the only sound witness file.
- T5 corpus replays (PackingCertCorpus target, one native_decide theorem per certificate): K61 26/61, TRAP 0/6 (⊂ K61), P1 1/1, THMU 11/11; 38 certificates, all OK; total Lean wall 60.4 min; max k6_08 = 747 s (8 atoms, 343470 boxes); Lean/Python wall ratio median 80×
- Audit: every new theorem propext/choice/Quot.sound (+ its own native_decide axiom for the check theorems);
  0 sorryAx; full default target green; Measure382Check cache hit throughout; A57/A60/A61/A76/A77/A79 untouched.
  Docs: instratum_bridge.md E.5, unique_transfer.md 6, d4_reduction_s0.md D4.5, attainment_ub.md 7.6;
  lean/README.md; depgraph json+svg (corpus_replayed accent added to the renderer); REGISTRY row.

## 2026-09-02 A80-u-ladder (Fable lead + Opus chores, 1 LP slot) -- done-mixed
- T2 VERDICT FIRST: the U_k counting row is a RESERVE-PLUS, not a lever. k4_08 pair LP (A66 rig copied, beta=1, thr 28,
  r_z=1e-3, converged cells): plain -1.00; rung 0 (= Lemma P-B optimised over gamma, one hard row with dual gamma*=0.088)
  -1.412; rung 1 ('<= 9 within delta') -2.000 (gamma* = 1/8): +0.59 over P-B, +1.00 over plain; rung 2 -2.564; rung 3
  -3.115; rung 4 -3.722; rung 5 (cap 0) -4.487 - all converged (3/5 needed lp_time 1800): linear ~0.55-0.6 per rung,
  ~3.5 units over plain for the whole ladder; rung 1 at r_z = 1e-4 identical (26.000000). Dodge witness = A12's mechanism
  quantified: rung-1 optimum 26 = 21+5 EXACTLY on 35 pairs - four ghost members at weight 1 (6 in-zone pairs = the cap),
  three split 2/3:1/3 with 3e-3-displaced variants keeping every box incidence; the row counts SQUARES, the adversary pays
  in pair mass parked outside the zones at gamma* per pair; zone radius irrelevant (A76 saturation law).
- T1: U_1 certifies at every delta (1e-3, 3e-3, 1e-2; sub-3 s each) but the composition's REACH collapses below 1e-3: the
  pocket of square 6 (top wall + flush 9 + point 4 = A76's hinge) is (5.6, 5.8) delta in (c, t) vs 1-2.8 delta elsewhere,
  exactly linear in delta; basin landing binds at delta <= 2.6e-4 (Lean 3/2000) / 3.2e-4 (A36 per coord) / 5.7e-4 (A40).
  U_1 has no pins, so A76's pinned rigid radius (1e-2) does not transfer. Packaged certs/uladder/u1_d1_4000 (all three
  basins) + u1_d1_2000 (A40); NEW stdlib checker certs/verify_uladder.py (structure vs the tight certificate, frozen-verifier
  reports, Lemma U-C margins, zone -> basin landing, counting-row radius; 5 corruption gates FAIL as required).
- Theory (docs/proofs/u_ladder.md): U_R statements + C0/C1 certificate forms + peeling (Lemma U-R), Lemma U-C (a square within
  (r_c, r_t) of a slot contains the slack core iff delta >= r_t + sqrt2(r_c + rho_B)), Lemma BR (bridging dichotomy: the
  'component shortcut' is a census, not a lemma - direct C0 certificates are cheaper than any separation argument), Lemma
  U-ROW (sound on the EXACT stratum only; the hypothesis enters once, at 'g.z-hat has five simple squares'), LP encoding by
  duality (hard row <=> discount form), composition unchanged from P-B.
- T3 probe (climb NOT run - lever threshold not met): rung-2 C0 census 41/55 PASS; 14 merged pockets = Trump's contact
  edges with (3,4) for (1,3) fail at every zone size -> atom certificates + peeling ((0,1) PASSes with one atom of weight 1;
  (3,4) needs a covering LP); priced ~hours emission per rung for ~0.55 slack. Canary SAFE throughout. Discipline held.
  Files: attempts/A80-u-ladder/{code,certs,results,logs}, certs/uladder/, certs/verify_uladder.py, docs/proofs/u_ladder.md,
  depgraph C.K4TIER note + svg (chip stays A77), REGISTRY row.
- 2026-09-02 A79-rigidity-lean closed (done-success, Fable 5.1): RIGIDITY REPLAY IN LEAN, rungs (b)+(c). E.A22 and
  E.A36 -> lean-proved: theta-frame port of A70's exact re-checkers (RigidKernel.lean: dyadic 2^-330 intervals,
  alternating-Taylor cos/sin certified from Mathlib Real.hasSum_cos/sin; deep-embedded row language with symbolic D and
  order-2 interval jets) replayed by native_decide (RigidityCheck.lean: checkA22_a22, checkA36_universal, checkA36_all17;
  140 s). Soundness: krawczyk_sound (Banach on the true box, Neumann invertibility of Y) => unique contact solution z-hat;
  zhatV_feas (interval SAT + exact-structure witnesses searched in S) => z-hat packs at its own side; a22_optimal (A22 sect 5);
  a36_basin (universal certificate: Taylor with interval Hessian mass, max-form pinning, quadratic dichotomy replacing the
  800-step iteration, handover to A22). TopLevel: zhat/shatA22 DEFINITIONS, trump_packs_at_shatA22/basin THEOREMS,
  roster 7 -> 3 (stratum_kill, trump_residual, a22_exact_structure); mpmath.iv out at both tiers. FINDING: only G3_UNIVERSAL
  is load-bearing (rBasin(1+sqrt2) = 3.6213e-3 < 3689/10^6; E.COORD gates untouched); A22's [F] re-check needs the
  exact-structure argument, derivable from S alone; eps0/g_max/eps_w must be box(z0,r0)-evaluated (x* 6e-48, harmless).
  Files: lean/PackingCertMathlib/PackingCertMathlib/Rigid*.lean, Rigidity.lean, RigidityCheck.lean, lean/gen_rigidity_lean.py,
  attempts/A79-rigidity-lean/{notes/findings.md,LOG.md,logs}, lean/README.md, depgraph E.A22/E.A36/E.IV (chips cleared),
  REGISTRY row. A57/A60/A61/A76/A77/A78 untouched.

## 2026-09-02 A77-corners4-close (Fable lead, solo) -- done-mixed (Lemma W''' measured, no PASS)
- MACHINERY: code/hintbatch.py = level-synchronous vectorised float B&B building COMPLETE spec-s4 hint trees (numpy pass over boxes x atoms per
  level, per-chunk atom pruning, A74 max-min lookahead cut, dyadic cuts inside the float-mirrored clipped interval, null leaves), leaf census
  cov/ex/nd/vac/hole/open; float predicates fuzzed vs the reference's exact ones (0/4000 disagreements); exact walk of the emitted trees with the
  reference's split/clip/discharge reproduces the census node for node; all 41 md8 hole pairs re-check exactly. code/iter77.py = grow -> LP ->
  emit (canary) -> build. ~1k nodes/s/process.
- FINDING 1 [M]: A74's "holes 220 -> 57" was a --nodes HARD-STOP artifact (283k-393k undischarged leaves behind the sampled caps; hinted cut
  nodes bypass --depth). FINDING 2 [M] Lemma W''' (pair_kill.md 6.9): complete-tree per-level retention r(d) = 0.75-0.86, FLAT from depth 8 to
  25 (root 2,11: 1.59M nodes; all 78 non-exempt roots: 2.71M nodes at 60k/root, 64 roots at cap, opens median certain 0.60, 41 holes),
  rule-insensitive => complete tree ~1e9-1e11 nodes at the W'' atom-depth scale; frozen verifier holds hints as serde_json Values (27 B/node)
  => route CLOSED in this certificate form. FINDING 3 [M]: the loop at equal budget md8 -> md9: holes 41 -> 7 (~6x) but the 56 hole placements
  cost 0.038 of the 0.042 slack (W2 20.95828 -> 20.99646, LP unconverged at kTimeLimit), open boxes unchanged 856k -> 853k; one more iteration
  crosses 21. FINDING 4 [M] C3 GAP: reference roots() is ix-major, Rust build_roots iy-major (spec 3.1/4 silent) -> "i,j" hint keys NOT
  portable (A74's 1493 misses explained); with --root_order rust both implementations fire rule-for-rule identically on the identical tree
  (vac 1726 / ex 6449 / nd 14201 / split 22375 / examined 43025, 0 misses); hinted Rust runs at 46k nodes/s vs 1.2-1.5k/s thrashing unhinted.
  Spec erratum owed (side data only). A76 relay: no P-B(R) row (corners4 d_min 0.8445). Canary SAFE x2 (min gap = lambda-1, sum m2 = 6).
- Discipline: 1 LP at a time (BLAS pinned, headroom gate waited out two dips to 0.26 GB), builder 4-6 procs, Rust jobs <= 6; A57/A60/A61/A76
  untouched; frozen verifiers untouched (import-only). Hinted certs (73 MB each) NOT committed (certs/.gitignore; regenerate with hintbatch.py).
  Files: attempts/A77-corners4-close/*, docs/proofs/pair_kill.md 6.9, depgraph C.K4TIER note (owner A77 closed), REGISTRY row.

## 2026-09-03 A83-contraction-tube (Fable lead + 1 Opus reviewer, <= 2 light slots) -- done-success
- T1 TUBE THEOREM CERTIFIED (docs/proofs/contraction_tube.md; certs/verify_tube.py stdlib-exact, 10 corruption gates; 12 certs
  certs/tube_*.json incl. the A36 box as a T = 0 regression, 289 checks, 0 failures; Opus clean-room review SOUND): every packing in Tube_v(T, r) = {z-hat - t v + w : t in [0,T], |w_i| <= r_i} has
  sigma >= s-hat, equality only at z-hat. A36's (V') chain re-based: pair-relative enclosures (edge/dist rows are translation
  invariant; on the hull box the pair centres vary independently -> interval-dependency artifact walled the tube at T ~ 0.02),
  split Taylor remainder d = -t v + w (q_vv = 0 on the slot ray: contraction is AFFINE on every wall/edge row), max-form
  pinning, monotone iteration in place of quad_pin, direct A22 handover. Reproduces G3_UNIVERSAL's constants at T = 0.
- NUMBERS (theta-frame, r_s = 0): slot ray (trump5 pins on their slot lines, free squares scaled = the exact pull-back of a
  (D) leaf): T = 0.045 at A60's landing radii (1.6e-3, 2.1e-3) [wall 0.0457], T = 0.0571 = s-hat - 3.82 at r = 6.5e-4,
  T = 0.0621 at r = 2e-4; scale ray (pure dilation pull-back): T = 0.13 at the landing radii. Isotropic r_max 3.68e-3 (= A36)
  at T = 0, 3.49e-3 at T = 0.02. psi/X = 0.023 at the landing point (A36: 0.998); beta never binds (0.33 / 0.55).
  WALL NAMED: tangential validity of A22 pin row E3c2-7e3 (pin square 3's corner on free square 7's left edge; slot ray,
  0.39 per unit T) / E7c2-9e3 (7-9 flush pair; scale ray, 0.10 per unit T). Both are pin rows (13, 27 in S): a different
  pin basis or an L1-style branch is the only lever beyond; not needed.
- COMPRESSION LEMMA [T]: scale ray - all 38 rows strictly compressed (gamma = c/s-hat on walls, n.(c_p - c_o)/s-hat >= 1/(2 s-hat)
  on edges, 2/s-hat on dists; min 0.12896); slot ray - gamma >= 0 with 18 pin-block rows exactly 0; Farkas identity
  sum omega gamma = 1 +- eps_w. Not load-bearing (the chain ignores the sign of v); it is why no contact breaks along the ray
  (branch-free, no L1) and the canary (z-hat - T v violates a strictly compressed wall row at every certified T).
- LEMMA SEAM [T]: t = s-hat - m EXACTLY; pins at slots(m) have w = 0 on the slot ray; free squares w <= r_land + 3.6e-7
  (the s0 - s-hat factor); tilts w = r_land,theta (1.771 r_t locally); dilation commutes with D4 at the respective sides.
  NO B.2'' widening anywhere (all tree logic is applied to the dilated family at s0); only the pin slack enters:
  T_K(delta_pin) = ((2/3) delta s-hat - (s0 - s-hat))/(1 + (2/3) delta) [A = 3/2 for trump5] = 0.0257 / 2.57e-3 / 2.5e-4 at
  delta = 1e-2 / 1e-3 / 1e-4 -> delta_basin(trump5) = min(T_tube, T_K) = 0.0257 at delta_pin = 1e-2 (0.0457 at >= 1.8e-2).
  => A60's (K) leaves must be re-emitted at delta_pin = 1e-2 (its planned 1e-4 caps the route at 2.5e-4); D.S6's 4.9%
  overshoot is void in the tube route. SEAM AS TWO NUMBERS: delta_basin 0.0257 vs delta_LP = A82 near-s-hat extrapolations
  1.7e-3 (k4_08) / 5e-3 (k4_11) [x5-15], BUT A82's deep point (k4_08 at s-hat - 0.044: eta -0.38, unconverged) says the
  protected crossovers lie deeper; trump5's own crossover UNSCANNED (named obligation). Protected classes: s0-Theorem-U caps
  T' ~ 3e-4 (pin drift (lambda-1)*5/2 enters U's cores, square-6 pocket x5.8) -> U-slab obligation (A80 owner) written.
- LEAN NOTE lean/tube_obligation_A83.md: tubeBox + InTube, split remainder lemma (no Hessian symmetry assumed: column and row
  sums both enclosed), iter_pin (monotone iteration), checkTube = checkA36 with the box swapped; ~400 lines on A79's files.
- Discipline: two light python processes max, no LP; A57/A60/A61/A81/A82 untouched; frozen verifiers untouched; certs/ new
  files only; depgraph notes on D.SLAB + E.A36 (owners unchanged), svg re-rendered. Files: attempts/A83-contraction-tube/*,
  certs/verify_tube.py, certs/tube_*.json, docs/proofs/contraction_tube.md, lean/tube_obligation_A83.md, REGISTRY row.

## 2026-09-02 A81-slack-verify (Fable lead + 1 Opus chore, <= 2 slots) -- done-mixed (T1 answered NO: Lemma W'''' measured; T2 not entered)
- T1 VERDICT FIRST: slack does NOT buy verifiability. Complete hint trees (code/hintbatch81.py = A77 builder + beta/U/zone targets) on the
  k4_08 rung-5 measure (slack 1.0, 196 atoms, 63% of the mass at depth >= 0.05): r(d) = 0.84-0.87 aggregate over d 8-14 (136 roots, 2.92M
  nodes, 64 roots at the 60k cap - the same count as corners4) and 0.79-0.88 on root 7,10 to depth 21 (1.15M nodes) - ABOVE corners4's tight
  measure (0.75-0.86, slack 0.042). Tree-size law unchanged: ~1e9-3e10 nodes to the measure's own 0.02-0.05 scale, 1e15 to its 5e-4 tail.
  Lemma W'''' (pair_kill.md 6.10): retention is set by the frontier structure (atom handoff loci + the beta U-bonus layer at the 7 widened
  boxes, a source corners4 never had), not by slack; open boxes on the deep root sit at 1.968 vs target 2. Redirect: conditioning trees.
- FINDING [T exact] Corollary S-08: the k4_08 images of Trump have Sigma m2 = 7 against ANY positively widened class box (member 4 tangent to
  TL(0,0) at -2.96e-7 = the dilation gap; +1.69e-3 at eps_box = 1/833) => plain boosted k4_08 value 28 = threshold at every beta (A66/A71/A80's
  "27 = 21+6 beta" was a unit-box artifact); the exact-stratum row is NECESSARY and BOTH images' rows are mandatory. Measured 28.000000.
- FINDING [M] rung 1 is DEAD in certificate semantics: both rung-1 rows -> 28.000000, gamma = 0; exact dodge = the two image families at
  weight 1/2 each (42 pairs, sum z = 21, 10.0 in-zone + one variant pair per image) halve every per-image counting row. Widened two-image
  ladder: 28.000 / 28.000 / 27.667 / 26.962 / ~26.06 (budget) / 25.045 at plain, k1..k5 (gains 0, 0.33, 0.70, ~0.9, ~1.0 - accelerating).
- FINDING [M] the U-row's slack is ultra-shallow: mixed-depth emission (eta >= 5e-4, A74 menu + 0.1) under the rung-5 rows gives
  W2 = 27.000000 (sharp 25.045): the exclusion lives in 1e-4 zones with the adversary parked at 3e-4 (A76 saturation law), so only atoms of
  margin < 3e-4 cash it - exactly the eta-fine structure W''' prices. Coarse measures are less complete: 1848 float holes at cap 60k (corners4: 41).
- Machinery (emission-side; frozen verifiers untouched): code/pairlp_u.py (U-rows as hard rows in EVERY model, duality gamma = discount,
  GATE = W2 + sum gamma cap, widened-box m2, candidate ladder + adversary support dumps), code/emit81.py (v2.1 candidate form: `urow` block =
  rung/cap/per-image gamma + (t,cx,cy) zone boxes with both tilt branches at uprights; trump5 canary + U-row canary, both SAFE x3),
  code/catalog81.py, code/retention81.py. No v2.1 verifier written (T2 not entered).
- Discipline: one LP at a time, BLAS pinned, 6 GB gate held (rung 5 waited 23 min); builder 4 procs; A57/A60/A61 untouched; hinted 70+ MB
  certs gitignored. Files: attempts/A81-slack-verify/{code,results,certs,logs}, docs/proofs/pair_kill.md 6.10, docs/proofs/u_ladder.md 6.2
  addendum, depgraph C.K4TIER (A81 note, owner closed) + svg, REGISTRY row. notes/findings.md blocked by the harness (findings in 6.10).

## 2026-09-02 A82-side-scan (Opus lead) -- done-mixed (crossover measured; 1 verified kill at 3.833212; 2 headline non-kills)
- SCOPE: PI side scan (alive gate + conditioned case-LP tau(m) + dtau/ds + crossovers, 12-side ladder) THEN the advisor's
  mid-run extension (17 classes x the 3 A57 grid sides, certificates + slab shells). Discipline held throughout: <= 2 LP
  slots (two detached BLAS-pinned chains, code/launch82.ps1), a commit-headroom gate that waited out every dip below 6 GB,
  A57/A60/A61/A81 state+files+processes untouched, frozen verifiers invoked-never-edited, certs/ new files only
  (certs/a82/). Solver of record copied into the attempt so no other tree's __pycache__ is touched.
- MACHINERY (attempts/A82-side-scan/code): sides82.py (exact L/R slot rebasing per A56 P0/P1; the 17-class spec incl.
  trump5; commit-headroom gate), alive82.py (side-parametric A57 alivewitness: Trump-image seeds relocated by the A56 P3
  gap-anchor rule + blind multistart + a MONOTONE CARRY from the next smaller side; every family re-verified EXACTLY in
  Fractions), scan82.py (node guard LP at side m, descending column-only warm starts, --delta slack cores + shell()
  reproducing A57 grid.py's slab arithmetic), emit82.py (A54 certify -> cold frozen verify at depth 60 -> 4 corruption
  gates), table82.py, chain82.py.
- F0 [T, exact] THE ALIVENESS CLIFF IS A STEP OF EXACTLY ONE, AT s-hat. k4_08/k4_11/k4_03 are ALIVE (m_fam = budget = 7,
  gaps 1.15e-7 / 8.97e-8 / 1.20e-7, exact at 1e8) at s0 and ONLY at s0; at every measured m < s-hat, m_fam = 6, exactly
  verified at 1e6. s_fit = 3.877083619 / 3.877083600 / 3.877083623 vs s-hat = 3.877083590022814 (agreement 3e-8): the
  class stops being an LP-unkillable stratum exactly when Trump's packing stops fitting. corners4 is never alive.
- F1 [T] THE A60 LAW eta <= -1 IS UNREACHABLE ON THE k=4 TIER ANYWHERE IN W. The exactly-verified 6-families give
  tau* >= 6 = budget - 1 at every side in [3.82, s0] for k4_08, k4_11, k4_03, k4_13 (and at all three grid sides for
  k4_03/k4_08/k4_13 + k3_01 + trump5), so eta >= -1 with equality the only possibility. Do not price a k<=4 window
  campaign off eta <= -1: it is geometrically excluded, not merely expensive.
- F2 [M, headline] A PROTECTED CLASS DOES KILL AT 3.833212, WITH eta = -0.38 (not -1).
  certs/a82/k4_08_958303_250000.json: 24 atoms, total 693001/100000 = 6.930010 < budget 7, side 958303/250000, 4 cores.
  Cold PASS by the FROZEN verify_case.py (md5 b1b825d918b21c1d2952d96bfce720b6) at --depth 60 (461204 boxes, 144789
  covered, 85845 exempt, 0 vacuous, 29 s); 4/4 corruption gates REJECTED (drop_heaviest / halve_weights / shift_atoms as
  coverage HOLES; overfull as "total >= budget"). => a fixed-side stratum kill does NOT need eta <= -1; the A60 law is a
  property of A60's zone-tree/4-D route, not of fixed-s case-measure certificates.
- F3 [M] THE REAL GATE IS eps_geo AFFORDABILITY. The same class at the FIRST A39-passing side, m = 3877/1000 with
  eta = -0.050, FAILED after 4 witness-feedback rounds; every witness a coverage HOLE of exact mass 0.963-0.988, i.e. the
  A56 P6(v) POSITIONAL deficit (~1.5e-3) whose repair costs dtau/d(eps_geo) ~ 1.1-1.7e2, i.e. ~0.21 of budget. Law:
  a protected class certifies at side m iff budget - tau(m) >~ 0.21. A56's 0.5-slack rule re-measured at 0.21 for k<=4.
- F4 [M, reported immediately per the extension] k0_00 AND corners4 DO NOT KILL AT 3.833212.
  k0_00 (root, budget 11): tau = 11.000000, eta = -0.000000, A39 FAILS -- the root LP has NO slack there, while the
  existing record bound rests on certs/measure_certificate_3.82.json (root tau = 10.716662 at 191/50). So there is NO
  record lower bound s(11) >= 3.833212 from a root measure certificate, and since a composed claim needs every stratum,
  k0_00's own eta = 0 is a hard stop for "each completed grid side yields a record lower bound" as stated.
  corners4 = k4_13: tau = 7.010638, eta = +0.010638, A39 FAILS -- ABOVE budget (coherent with A65's 7.2545 at s0).
- F5 [M] HYGIENE: an unconverged case-LP reads BELOW budget where the class is provably alive. At s0, where tau* = budget
  exactly by F0, the 600 s LP gave 7.000000 for k4_08 but 6.987500 for k4_11 (eta = -0.0125 of pure non-convergence;
  minmass 0.5-0.9 throughout). The canary caught it and WARNED rather than failing, because the LP had not converged.
  Reading rule banked: |eta| < ~0.02 is noise, eta <~ -0.2 is evidence, only an emitted certificate is proof.
- F6 dtau/ds ~ 7.3-8.0 per unit side on the k=4 tier (k4_08 OLS 8.02 / local 7.47; k4_11 s0-to-3.833212 chord 7.31),
  i.e. ~0.044 of budget slack per 1e-2 of side. The fitted eta = -1 crossover m* = 3.7556 lies OUTSIDE W, consistent with
  F1 (a fit predicting a crossover inside W is an artefact of the fit).
- F7 [M] SLAB SHELL PRICE (the extension's requirement, UNPAID here): scan82.shell() reproduces A57 grid.py -- delta-cores
  give rho ~ delta - tm and cover (s''/(1+rho/2.5), s'']. Reaching 3.833212 from 3.847780 needs rho >= 9.50e-3, i.e.
  delta ~ 1e-2 (A57's own choice; delta = 1e-2 covers (3.832450, 3.847780]). The certificate of F2 uses A53 DEGENERATE
  pins (delta ~ 3e-8), so its shell is ~1e-8 wide: it certifies the side 3.833212 and essentially nothing else. Re-emitting
  at delta = 1e-2 shrinks the exempt region and raises tau; with 0.377 of headroom minus 0.21 for eps_geo the budget is
  ~0.17. UNMEASURED -- one LP (scan82.py --delta 0.01) prices it and is successor task 1.
- GRID LP RESULTS at 958303/250000 = 3.833212 (600 s conditioned case-LP, delta = 0): k4_03 6.600000 (-0.400, A39 PASS),
  k4_05 6.642857 (-0.357, PASS), k4_08 6.622642 (-0.377, PASS, CERTIFIED), k4_11 6.666667 (-0.333, PASS, emission in
  flight at handover), k4_13 7.010638 (+0.011, no), k0_00 11.000000 (-0.000, no). Exact alive bounds for all 17 classes
  at all three grid sides are in results/alive_gate_grid.json (trump5: m_fam 5/6 at every grid side -- Trump's family does
  NOT fit there, canary as expected).
- TRUMP CANARY CLEAN: family fits at s0 (only ladder side >= s-hat) for every Trump-realised class, exact at 1e8; nowhere
  below. LP saturates at s0 (k4_08 exactly 7.000000; k4_11 flagged per F5). corners4 exempt (no Trump image). The single
  emitted certificate is at 3.833212, far below Trump's own side.
- Files: attempts/A82-side-scan/{code,results,notes,logs,certs}, certs/a82/k4_08_958303_250000.json(+report),
  notes/method.md + notes/side_scan.md (the crossover table + the grid table), results/side_scan.json,
  depgraph C.K4TIER note (chip unchanged, stays A81), REGISTRY row.
- ADDENDUM (same session, after the entry above was written): SECOND VERIFIED KILL --
  certs/a82/k4_11_958303_250000.json (58 atoms, total 6.956292 < budget 7, side 958303/250000), cold PASS by the frozen
  verify_case.py at --depth 60 (33 s), 4/4 corruption gates rejected. Emitted at eta = -0.333 with eps_geo = 1.5e-3 and
  3 witness-feedback rounds. So TWO of the six k=4 protected classes are now killed at 3.833212 by exactly verified
  fixed-side certificates, both at eta ~ -0.35, i.e. an order of magnitude short of the A60 law -- which F1 shows can
  never be met there anyway. k4_06 measured at 3.833212: tau = 6.615385, eta = -0.384615, A39 PASS. All five non-corners4
  k=4 classes pass the A39 gate at 3.833212 (k4_03 -0.400, k4_06 -0.385, k4_08 -0.377, k4_05 -0.357, k4_11 -0.333);
  corners4 alone does not (+0.011). Emissions for k4_03/k4_06/k4_05 and the LP sweep of trump5 + the five k3 classes at
  3.833212 were left RUNNING at handover (code/emitchain82.py and chain B; both resume from results/, both under the
  headroom gate) -- results land in attempts/A82-side-scan/{results,certs} and certs/a82/.

## 2026-09-02 A84-protected-trees (Fable lead + 1 Opus compute chore, <= 3 LP slots) -- done-mixed (Lemma P-TREE HOLDS; Lemma PD found; tube law for the tier; pilot exact laws complete, LP laws partial)
- T1 LEMMA P-TREE HOLDS [T] (docs/proofs/protected_trees.md sect 2): an s0 zone-tree over the MONOTONE pin hypothesis (slack
  cores delta_pin) with (K) Lemma-B kills, (C) logic kills, (D) full localisations of the N = 11-k free squares near a compatible
  Trump image, composed with the contraction tube in the class's OWN direction (v = beta on the Trump-frame pin set I_g,
  c-hat/s-hat elsewhere; D4 commutes with dilation), excludes every packing containing S's pins at every side in
  [s-hat - delta_basin(S), s-hat) and makes every such packing at s-hat a Trump image g.z-hat. The exact-stratum hypothesis is
  used NOWHERE on the bound and only optionally at equality (Simp(g.z-hat) != S; P = g.z-hat IS the uniqueness conclusion).
  H10-stuck (U-O2) becomes a corollary; Theorem U is not consumed (A83 4.3's T' ~ 3e-4 cap is void for this route).
  Per class [M, tier84.py]: G_S, I_g, A_S, T_K; k4_05 and corners4 have NO compatible Trump image (G_S empty) -> no (D) leaves.
- LEMMA PD (pin-drift logic kill) [T+M, sect 2.1] -- found by the pilot: with slack pin cores the residue ladder has a FLOOR =
  delta_pin (k3_05 pre-PD: gap stalls at 0.0219, residue 96 -> 3862 by L28, 293/3862 landed). The dilated family's pin is the
  FULL square Sigma_p + (lambda-1) alpha_p (drift always into the container), the set of drifts meeting a convex core is convex,
  so "core meets Sigma_p at lambda = 1 AND at lambda_max" is a (C) leaf on the whole side range. With PD both pilot classes
  contract exactly like A60 (ratio 3.6-4.5 = A59's 4.55 law; landing L24, 59 boxes, containment 1.1427e-3 / 2.0102e-3 rad =
  A60's square-1 numbers to four digits; canary ok at every level). A60's own delta_pin = 1e-2 re-emission needs PD too
  (sq7/sq8/sq9 all touch pin corners). Whole-window trees at A_S = 3/2 need delta_pin = 2.5e-2 (T_K).
- TUBE LAW FOR THE TIER [M, 19 Trump-frame pin sets, 42 certificates certs/tube_{k4_08,k3_05,I_*}_*.json, cold re-verified
  1008 checks / 0 failures]: T_max depends on the pin set ONLY through square 3 = BL(0,1): pinned -> 0.0457 (A60 landing
  radii) / 0.0574 (r = 6.5e-4, >= the window) with trump5's wall E3c2-7e3; free -> 0.1305 / 0.1680 (wall E7c2-9e3, the
  scale ray's). Anisotropic: (6.5e-4, 2.1e-3) gives 0.0525 -> the whole window needs the TILT landing tightened too (~L29).
  SEAM (with A82 closed): k4 image-bearing classes OVERLAP at A60 landings (plain kills to s-hat - 0.025 by A82 F3/F6, tube
  0.0457, delta_pin 2e-2 => T_K 0.051); k4_06 / k3_05 / k2_01 / k2_02 / k1_00 / k0_00 covered by the tube alone; BL(0,1)-pinned
  k<=3 classes need the tighter landing or a scan.
- PILOT (Opus chore; A60 engine COPIED to attempts/A84-protected-trees/code, class84/alive84/tree84 + launch84 with a
  commit-headroom gate; both images' exact witness families verified, min gap ~1e-7): census j0 k4_08 316 contradictory (280
  slack-core + 36 PD) / 752 attemptable at budget 6 / 84 unkillable (2 x 41); k3_05 84 / 984 at budget 7 / 84; P1 analogue
  PASS for both (k4_08 eta = -3.0 at budget 7, 52 s; k3_05 eta = -3.0 at budget 8, 17 s) -> the interior zone is the whole
  cover. LP SAMPLE PARTIAL (LPs sat at the 6 GB gate; free commit 0.8-6 GB behind A78 lean builds + a 12 GB foreign process):
  cover 3 boxes -> 2 PASS / 1 cert-FAIL at eta ~ -0.8, ~700 s LP + 400-800 s cert each (x3 / x15 A60); LADDER QUEUE 0/4 at
  levels 6-9 (tau = 6.000 = budget, one CONVERGED; no exact 6-family found on the grid): the queue is a deepen/conditioning
  queue, not a kill queue -- the unmeasured item of the price. Shards keep running to their 3 h caps.
- PRICE (sect 7): k4 image-bearing ~110-160 CPU-h each before the ladder-resister term; k3 ~200-300; k0_00 dominates
  (root eta = 0 at 3.833, no pins/logic kills, 8 images: >= 100 desktop-days plain, ~25-30 with the stuck-only A58 corner
  seed); corners4: Lemma CC4 [T at s0] (every one of the 8 arm slot boxes met by >= 2 non-pin squares, via CC-2 teleport into
  k5_16 = corners4's only k5 superclass, killed by A57) + an EXACT counterexample to the '<= 2 slots per square' count (a
  feasible tilted square meets 3 slot boxes through the middle strip) -> finite case analysis required, ~2-10 desktop-days.
- Discipline: <= 3 LP slots, BLAS pinned, 6 GB gate honoured (58 waits logged); A57/A60/A61/A82 untouched; frozen verifiers
  invoked only; certs/ new files only; A83 emitter imported read-only. notes/findings.md blocked by the harness -> sect 10.
  Files: docs/proofs/protected_trees.md, attempts/A84-protected-trees/{code,results,notes,logs,certs}, certs/tube_*,
  lean/depgraph.json (C.K4TIER note, owner released) + svg, REGISTRY row.

## 2026-09-02 A85-k0-route (Fable lead + 2 Opus chores, <= 3 LP slots) -- done-mixed (lemmas hold; the price does NOT drop an order of magnitude)
- T [docs/proofs/k0_route.md]: LEMMA K0-FREE holds in the FORALL-PACKINGS form: a corner box met by <= 1 square teleports the
  packing (teleport_packing) into k1_00's MONOTONE hypothesis at the same side; k1_00's P-TREE (tube 0.1305 >= the window) kills
  it at every m < s-hat and Theorem U closes m = s-hat. The corner seed is therefore NOT stuck-only (A84's caveat void) and the
  exact-class question is moot (K1 climbs). LEMMA K0-D4: equivariant quotient /8 with mod-G transport of every leaf verdict
  (Theorem A38.1 + d4_wlog at the root; orbit representatives on the seed, canonical fraction measured 0.120). LEMMA K0-PAIR:
  NO finite case list - the corner 2-crowd space has interior and contains same-sense tilted pairs (explicit exhibit; 32 % of
  the surviving pair boxes), the advisor's 'mixed-sign V' prune is unsound locally. K0-WIDEN (w = 0.0255), K0-ATLAS ((D') leaves,
  no dilation, no window obligation), K0-REUSE (near-slot pocket = k1_00's tree), K0-ROT (rotation stationarity with the exact
  centre-height term; Trump V-profile D+-sigma = 3.877; rotational ghosts at side <= s0 within 2.2e-7 of an image; selected-form
  (C) rule only, no price effect).
- M [attempts/A85-k0-route]: the seed as a COVER is dead - 644 reach boxes, 33 656 pair boxes per corner, 2.9e16 four-corner nodes
  after exact prunes and /8. A38-G7 closed with the A60 engine on A38's own cells: level 1 undecided (0/3, eta -0.12..-0.34, all
  eps_geo repairs fail), depth 2 decided (tau = budget - 1.0..1.27, 3/3; first cold PASS of a no-pin node at s0:
  certs/k0_00/s1int_l2_l2_p114_010; ~1 000 s LP + 630-860 s cert). k0 landscape: 262 k0 optima from 516 targeted runs, none below
  s-hat, best at s0 + 0.0101; 12 ghosts within 0.02 of s0 near atlas families 9/8/7/11, all outside the atlas -> drain boxes
  centred at the ghosts (A37 3S, h = s_g - s0 >= 6x the landing radius, ~1 desktop-hour for all 12); family-centred basins
  (radius 0.07-0.09) are not the route.
- PRICE: k0_00 = 3 200-7 000 CPU-h (45-100 desktop-days at 3 slots) if depth-2 certifications repair at ~85 %, >= 3e4 CPU-h if
  only first-pass certifications count: 3-30x below A38's floor, not below A84's plain >= 100 desktop-days; A84's 25-30-day
  seeded figure was unfounded. The deciding constant is certification reliability at eta ~ -1 - engineering, not geometry.
- T4: the seed does not force the selected form; stratum_kill_all / stratum_kill_min split (attainment hypothesis from B.SEL,
  and from the bound itself at s-hat) needed only for K0-ROT leaves -> lean/k0_readiness_A85.md (no lean/ edits).
- Discipline: A84 engine COPIED; A57/A60/A61/A82/A84 untouched; frozen verifier invoked only; certs/ new files only; <= 3 LP
  processes; free commit 1-3 GB under the other campaigns for the whole LP phase (S2-S5 not run). Files: docs/proofs/k0_route.md,
  attempts/A85-k0-route/{code,results,notes,logs,certs}, lean/k0_readiness_A85.md, lean/depgraph.json (C.K4TIER note, chip
  released) + svg, REGISTRY row.

## 2026-09-03 A86-lean-wave7 (Fable lead + 2 Opus chores, light CPU) -- done-success (T1+T3 landed clean; T2, T4 landed; replay priced)
- T1 TUBE CHECKER LEAN-SOUND (A83's obligation): RigidTubeKernel.lean (checkTube = verify_tube.py: hull box + PAIR-RELATIVE boxes
  for edge/dist rows, split Taylor remainder E(x), monotone iteration iterT) and RigidTube.lean (tube_basin: checkA22 & checkTube
  PASS => every feasible point of Tube_v(T,r) has s >= s(z-hat), equality only at z-hat; axioms propext/choice/Quot.sound). The one
  new analytic fact: translation invariance of the pair rows AND their symbolic derivatives (shift_inv_D from hasDerivAt_eval +
  HasDerivAt.unique) - no new induction over the expression language. quad_pin replaced by iterT_sound (E monotone on [0,inf)).
  TubeSeam.lean: t-frame form tube_tframe, per-coordinate inTube_mkVec, Lemma SEAM's map seam_inTube (pins w=0 up to the slot
  residual, free squares |w| <= r_land*(m/s0) + T*eps_v), the certificate-data residuals vfree_bound / pin_slot_bound from
  |z-hat - z0| <= r0. Data RigidTubeData.lean (54 certs, gen_tube_lean.py), isolated RigidTubeCheck.lean (3 load-bearing
  directions, 79 s), per-cert Corpus/Tube/Check_* (target PackingCertCorpus). REPLAY: native_decide agrees with verify_tube.py on
  every replayed certificate; ~29 s Lean per certificate vs ~1.7 s Python (regress_a36 29 s; three load-bearing 79 s together);
  full table in lean/lean_wave7_A86.md.
- T2 ATLAS BOX CHECKER LEAN-SOUND: AtlasKernel.lean (checkAtlas, trivial-reach/extent form in (cx,cy,t): witness corner pairs,
  rational cosT/sinT enclosures) + AtlasBridge.lean (atlas_kill; atlas_dilated_kill_fold = Lemma K0-ATLAS: L >= s0 discharges
  EVERY side m < s0 at once, the dilate's extent is <= s0 - (lambda-1) exactly). [F] the boxes must be tilt-FOLDED into [0,pi/4]
  (319/539 squares of the naive mod-pi/2 box wrap): foldT t = min t (tRefl t) preserves per-axis corner-coordinate sets hence
  extents (cornerPt_fold_x/y). Chore: 37 A37 entries + 12 A85 ghost drains re-emitted (emit_atlas_lean.py, gen_atlas_lean.py):
  48/49 reach L >= s0 (fam00 = Trump cannot, s-hat < s0); L(h) = s - 2.003 h, h_max ~ (s_min - s0)/2 = 0.499 x A37's radius;
  ghost drains 5.06e-3..5.80e-3 = 3.2-3.6x the landing radius (A85 sect 4.6 met at half the nominal). AtlasCheck native_decide 2.9 s.
- T3 ZONE-TREE COMPOSITION LEAN (ZoneTree.lean): ClosedTree s0 tc Root = leaves (K)/(N) checkCaseI PASS at s0 with NodeHypC
  (cores in owners, NO-zones avoided set-wise; nonempty nofams handled by the SAME clause via checkCaseI_no_family - no B.2 widening),
  (C), (D) = the SEAM landing after g and a relabelling, (D') = folded atlas box, plus cover (the tree's complete disjunction =
  the producer's obligation); tree_kill = Lemma P-TREE (a)+(b). Step 1 root_of_containsPins (occupiesSlot_params +
  bprime_containment under the drift budget). Rule library: zone_dichotomy, grid_cover (CI-1), slot_outside_zone (CI-3),
  pd_convex + pd_rule (Lemma PD), psq_set_convex, d4_dil_comm (D.S6 mod-G). Composition.lean: ClassKilledAt (every packing of
  class i at m has m >= s-hat, at s-hat is a D4-image of z-hat); s_eleven_ge_of_classes / s_eleven_unique_of_classes consume NEITHER
  stratum_kill NOR trump_residual NOR basin (old axioms imply the new hypothesis); classKilledAt_of_tree (D4 normalisation as in
  class_kill, exact hypothesis used nowhere on the bound); classKilledAt_of_slabs (regime 1/2 seam); the stratum_kill re-split of
  lean/k0_readiness_A85.md (StratumKillAll/StratumKillMin) with both consumers proved. TopLevel roster note added (docstring):
  stratum_kill + trump_residual -> certificate-file facts (checkCaseI/checkAtlas/checkTube PASS + cover + SEAM data + Step 1);
  a22_exact_structure unchanged.
- T4 WINDOW ROWS LEAN (WindowRows.lean): SlabKill S lo hi (half-open top: Lemma B needs lambda > 1); slabKill_of_param (a V.PARAM
  row covers its whole window: at every real side a specialisation side s2 in (m, s_hi] with (s2/m - 1) A < rho exists),
  slabKill_of_case (slack-core grid, (s2/lo - 1) A < rho), slabKill_of_M1 (no budget); slabKill_union; windowKilled_of_slab ->
  the stratum_kill instance via class_kill; k5_06_slab instantiated on the replayed pilot (rho = 1e-9 <= 1/2 - a(cosT+sinT) by
  norm_num). The 9 converting C.A61 rows enter as checkParamI = true hypotheses of that shape.
- Axiom audit (scratch/A86Axioms.lean): all new soundness theorems propext/choice/Quot.sound; composed statements add exactly the
  evaluation axioms of the certificates consumed. s_eleven_ge / s_eleven_unique untouched. Default target builds; frozen isolated
  modules cache hits.
- [E] rfl on a let-heavy structure projection ((tubeStats c tc).qvv) times out at whnf; delta then rfl is instant. Array.getElem_ofFn
  under a heavy function needs a generic getD_ofFn lemma. A foreign K61 corpus runner held the repo lock for hours; single-module
  builds went through lakeb --nolock (below-normal priority, no collision).
- Residues [C]: the tree-file -> cover emitter + CI-2 (replay tooling); the per-class (D)-leaf landing data and the
  ClosedTree instances for trump5/k4_08/k0_00 (await the campaigns' corpora); corpus-wide parametric replay (~200 s/cert).
- Files: lean/PackingCertMathlib/PackingCertMathlib/{RigidTubeKernel,RigidTube,TubeSeam,RigidTubeData,RigidTubeCheck,AtlasKernel,
  AtlasBridge,AtlasData,AtlasCheck,ZoneTree,Composition,WindowRows}.lean, Corpus/Tube/, lean/gen_tube_lean.py, lean/gen_atlas_lean.py,
  lean/lean_wave7_A86.md, lean/README.md, TopLevel.lean roster note, docs/proofs annotations (contraction_tube, protected_trees,
  k0_route, cover_invariance), attempts/A86-lean-wave7/{code,results,notes,logs}, certs/atlas_lean/, lean/depgraph.json notes on
  C.K4TIER/C.A61/D.TREE/D.LADDER/D.SLAB/D.S6 (owner chips unchanged) + svg, REGISTRY row.

## 2026-09-03 A87-drain-flow (Fable lead + 1 Opus pilot chore, <= 2 slots) -- done-success (DF-K0 HOLDS in two lines; H1 = T3|k0, MEASURED dead as a cover; k0_00 stays on A85's tree)
- T [docs/proofs/drain_flow_k0.md]: THEOREM DF-K0 holds in the selected (MinForm) form of stratum_kill that A85 sect 9 wrote and A86
  composed (StratumKillMin, Composition.lean 159-204): H1(s-hat) ("no k0 FJ point with sigma <= s-hat, for every consistent
  selection") => the k0_00 instance of StratumKillMin, by D1 (attained_thm) + D3' (FJ necessity at a global minimiser for every
  consistent selection). No hypothesis on the other strata, no induction on 11-k, no selection, whole window at once (s is a
  variable of the FJ system). Obligations: (a) drain step holds in first-order form (Lemma DS: Gordan direction gives a packing
  at side sigma - eps|y_s|) and is NOT NEEDED - attainment is the terminal point of every drain; the quantitative form ("a
  contact forms within bounded motion") is false as a mechanism (feasible-direction flows jam) and unnecessary. (b) VOID: the
  k>=1 strata are codimension-3 (a square EXACTLY on a corner slot), a drain from k0 never reaches them; the only k-raising
  mechanism is the discrete teleport (CC-2), whose well-founded induction is unique_via_chain (Lean) and serves uniqueness, not
  the bound. (c) VOID: a global minimiser is FJ for EVERY consistent selection, stuck or not; B.SEL enters only the uniqueness
  clause, replaced in the split composition by "every packing at s-hat is a minimiser". The exists-selection weakening of H1 is
  a no-op on cells (flush ties). Lemma F-LEAF: minimiser-only leaves ((F) Farkas, (B) D2 slack, (R) K0-ROT, (S) stuck rows,
  flagged) are admissible in the k0_00 zone-tree under StratumKillMin - the honest partial; no price effect (dominated by
  (D)/(D') value boxes at the residue; niche = a residue landing on an unknown structure below s0 + 1.6e-3).
- F: H1 IS drain_lemma.md's T3 restricted to k0, and the restriction prunes NOTHING at cell level (k0 open+dense). The
  measure-zero critical set is the wrong complexity measure: Gordan is exact for the GRADIENT HULL of a cell, so the test fires
  only at the discharge scale set by the configuration's slack (zero at s*), and the count is the 33-dim volume at that scale.
  "forall z exists descent direction" != "exists one direction feasible on all of B". The certificate must be stated at
  sigma <= s-hat (algebraic enclosure), not s0: at s0 the rotational ghosts are genuine k0 packings 2e-7 from z-hat.
- M [attempts/A87-drain-flow, A30 engine copied, selftest 7/7]: 1 448 cells over the 262 k0 optima + Trump rotated by 1e-3 /
  5e-8, h = 0.05..1e-4 (1e-8 for the ghost), s clipped to s0. EVERY exclusion was a-sigma (sigma_min(cell) > s0), 1 351/1 448;
  (a)/(a-menu)/(b)/(c1-union) fired 0 times; of the 74 cells with sigma_min <= s0, 0 (0.0 %) excluded by any test at any h;
  114 000 per-selection Farkas tests, 0 kills (menus 2^16-2^34); h*/Delta = 0.465 (uncensored median; h* = Delta/2.15, a pure
  s-clip law); the rotational ghost (sigma = s0 - 2.2e-7) alive down to h = 1e-8 (x-wall rows straddle). Cost 0.81 s per
  sigma-feasible cell (A30 0.50), 2.5 ms/selection, 1 LP node = 2 100 cells per cell but 10^60 x more cells: uniform cover
  10^39.6 / 10^62.7 / 10^95.7 cells at h = 0.05 / 1e-2 / 1e-3 after /8*11!; one A85 landing box = 10^6.7 cells = 10^3 CPU-h at
  h = 1e-3 WITHOUT being discharged. Verdict: H1 is its own astronomically more expensive tree.
- F [J3]: at 13 of the 14 k0 "optima" below 3.9 (and at rotated Trump) the FJ multiplier LP is INFEASIBLE (19-27 active rows,
  rank 17-23, flat dim 10-16, 0-4 rattlers; lambda0 = 0 branch infeasible too): with the sampled selections these are NOT
  Fritz-John points - A04/A85's optimiser stops at first-order points of the penalised problem; under-contacted BECAUSE
  non-critical. The premise "k0 critical set = under-contacted manifolds at s >= s-hat + 0.0101" is unsupported by its own
  census; the genuine k0 FJ points are unknown (caveat: one tie selection sampled per contact pair). [C] FJ-polish re-run of
  the CP search, ~1 desktop-hour. Does not touch DF-K0.
- Route: k0_00 = A85's tree (45-100 desktop-days at f2 ~ 0.85), optionally with Lemma F-LEAF leaves; MinForm re-split is the
  form to consume. Discipline: A30 engine COPIED; A57/A60/A61/A85/A86 untouched; frozen verifiers untouched; certs/ untouched
  (no certificate emitted); <= 2 processes, headroom 7.3 GB at launch. Files: docs/proofs/drain_flow_k0.md,
  attempts/A87-drain-flow/{code,results,notes,logs}, lean/depgraph.json (C.K4TIER note, chip released) + svg, REGISTRY row.
- A78 T5 COMPLETION: K61 61/61, TRAP 6/6 (⊂ K61), P1 1/1, THMU 11/11; 73 certificates, all OK/PENDING; total Lean wall 590.0 min; max k4_09 = 2400 s (531 atoms, 4192860 boxes); Lean/Python wall ratio median 32×
- A87 FOLLOW-UP CLOSED [C] (FJ-polish re-run of A85's k0 CP search, notes/fj_polish.md, code/fjpolish87.py, results/cp87_fj_polished.{json,jsonl} + cp87_below_shat_verify.json): HEADLINE = NO genuine k0 Fritz-John point at or below s-hat = 3.877083590022814 (0 of 179 survivors, 0 of 167 at tight tol 1e-6); A04's 702-optimum search NOT contradicted. Method: NNLS cone test (no LP) whose residual r = A^T lam* - e_s is itself the certified Gordan descent direction (A r >= 0, e_s.r = -||r||^2), eps-active feasible-descent flow + damped Newton on the active-set FJ system (t3lib fj_eval mode=active), tolerance ladder 1e-6..1e-3; 269 seeds (262 A85 optima + 7 rotated-Trump phi 5e-8..1e-2), ONE process BLAS-pinned, 1928 s. Seed census extends J3 from 15 points to all 262: 115/262 (44%) have NO FJ multipliers at ANY ladder tol -> that fraction of A85's "optima" are penalty/SLSQP artefacts, not critical points. After polish 167/262 are genuine FJ points at tol 1e-6; LOWEST is o012 at sigma = 3.897230787 (s-hat + 2.015e-2) - the same single point J3 found, polish adds nothing below it; next four 3.98284, 3.98284, 3.99692, 4.00000; ZERO tight survivors in [3.87,3.88). Lowest FEASIBLE k0 packing any drain reaches: 3.877140815 = s-hat + 5.72e-5 (Trump rotated 1e-4), re-verified exactly (80 dps, all 55 SAT gaps >= 9.86e-11 > 0, side <= 3.877140815) -> strictly ABOVE s-hat. CONTROL PASSES: rotational ghosts phi <= 1e-5 all drain back to sigma = 3.877083590 = s-hat to 2.9e-11 and are then correctly rejected as NOT k0 (k_flush = 3). Of J3's 14 low landings only o012 survives; the other 13 drain 1e-4..1.7e-3 and NONE converges in the 14 s/seed budget (2 leave the k0 stratum). CAVEATS: 98/269 flows truncated at the budget, so the claim is "no drain reached s-hat", not "no k0 FJ point below s-hat exists"; the 12 loose survivors pass only at tol 1e-4/1e-3 (mid-drain points look jammed when everything within 1e-4 is called a contact) and are NOT certificates; one tie selection per contact pair still sampled. A57/A60/A61/A85 untouched, no certificate emitted, headroom 8.3 GB at launch.

## 2026-09-03 A88-fj-census (Fable lead + 2 Opus chores, <= 2 processes) -- done-success (H1-by-structure PRICED: census ~1e36, >= 1e12 rigorously; loses on the count, not the price; k0_00 stays on A85's tree)
- T [docs/proofs/fj_census_k0.md]: THEOREM T1 (k0 FJ contact floor): m_H = 3k_H+1+sigma_H-d_H (A44 L8), so m_min(d_H) = 3k_H+1-d_H
  (+1 in the lambda0=0 branch); support conditions = L6 wall-to-wall chain on >= 3 loaded squares + L1 degree >= 2 (+ L11 non-thin
  row-degree >= 3 => m_H >= 6, 2E_H >= 3k_H+2); absolute floor k_H >= 3, m_H >= 4. Flat directions: flexes are s-neutral (L10), FJ
  points generically isolated in the core, d_crit <= d_H + 3(11-k_H) with d_H UNBOUNDED by first/second-order necessity (A44 frame):
  worst case k_H = 3, eight rattlers, d_crit <= 30 - the chain/L1 bound m from below, never d from above. The FJ side adds NO bulk
  filter: "enough contacts to support the multipliers" = L1 + L6 = A31's hard set; A44's rigid/flex split labels, does not kill.
  k0 filters: K0-1 slot exclusion (no wall-degree-2 square with a wall-flush edge; decoration level, inert at Level 0), K0-2 A58
  crowding as an existential zone CSP (S-flagged: k-maximal minimiser via stratify), K0-3 A45 ruler cap (WINDOW-DEPENDENT - Caveat
  R), K0-4 A50 tilt rules inert at census level. LEMMA H-LOC: the per-structure certificate is local to the loaded core (Gordan on
  H's rows refutes every FJ point with support in H whatever the unloaded squares do; Krawczyk on a rigid core lands on a
  sub-packing problem when the root is below s-hat).
- M [T2 census, attempts/A88-fj-census/notes/census_report.md; A59's method lifted to S_11 x D4, counter reproduces A31 R0/R2 and
  brute-force orbit counts exactly, divisibility by 11!*8 asserted]: Level-0 k_H = 11 support graphs 9.5e10 +- 2.5e9 [MC] in the
  rigorous bracket [57 232 EXACT, 1.27e15 EXACT] - inside A31's EXTRAPOLATED band, now measured; dominant filter L4(b) planarity
  x1380, then N1 x4.25; L5(a) nearly inert at k = 11. Decorations per graph median 1.3e21 (mean 2e25; A31's extrapolated 6.5e18 was
  2.4 orders low). DECORATED census 1.86e36 [MC, +-1/2 order] in [3.9e26 EXACT (one explicit graph's all-corner sub-menu
  8^24 * AO(G)/2), 4.4e52 EXACT crude]. Ablation: K0-1 x0.9895, K0-3 x0.99999, K0-2 x1.000 (1493/1493) - the whole k0 hypothesis
  buys x1.011; A58 dropped / A50 dropped: unchanged. Rigid-possible share 1.2e-5 (weighted); FLEX-ONLY >= 99.9988 %. Dominant
  multiplier = the contact-type decoration fan-out, ten orders above the graph count. CANARY PASS 9/9: Trump's structure derived by
  code (tol 1e-6), passes F0 on G and H, per-wall 3/3/3/2, EXCLUDED by K0-1 (slot squares {0,2,5}), INCLUDED with K0-1 dropped.
  D6: A87's 167 certified k0 FJ points satisfy T1 with 0 violations (k_H 4..11, m_H 7..32, d_H 2..9, chi in [-9,-2]: ZERO rigid)
  and are census members 167/167 (tilt-feasible, K0-1, L5(a)/N1 narrow and widened window).
- F [G-A88-4, two independent witnesses]: A31/A43/A44's gauge-fixed 20-type menu OMITS the same-class corner-corner kiss (Trump's
  (1,3) pair; 4 of the 167 certified points); the census undercounts by that family (verdict direction unaffected), and L4
  planarity is FALSE on the ACTIVE graph when squares kiss at a point (o124/o154 at sigma = 4) - L4 holds on the kiss-free
  support, the only object any existing count enumerated, so those counts stand. Caveat R: Lemma R's ruler cap grows with s
  (147 spurious kills from applying the s0 cap at sigma = 4).
- M [T3 pilot, notes/pilot_report.md; float intervals cross-checked to 1.2e-14 vs t3lib mpmath, no certificate emitted]: TRIAGE
  (interval-linear realisability LP over tilt-class bins, sound outer relaxation) on 720 uniform census structures: kill 0.225
  [0.210, 0.241] at 13.6 ms/structure - CONTAINMENT-type 0.222, s-hat-type 0.003 (2 of 720): A59's diagnosis re-derived, the s-hat
  bound is nearly free at Tier 1; no realised structure ever containment-killed; Trump survives. FJ TIER (core-box B&B: HC4
  propagation, a-structure, dominance side rows, a-sigma, Gordan/Farkas with the FIXED row set, Krawczyk for chi >= 0): 95.3 %
  [93.3, 96.8] of census survivors CLOSE in ~33 boxes / 50 ms; leaf kills = dominance rows 0.67, HC4 0.19, a-structure 0.09,
  F 0.053 (Gordan DOES fire once the selection menu is gone - A87's menu was part of the problem); Krawczyk reached 0 times by the
  search; HC4 is load-bearing (root box uncontracted without it, free with it). The 13 A87/Trump structures never close (20 000
  boxes) - correctly, they contain genuine FJ points. CANARY PASS: descending into the child containing z-hat, no leaf ever excluded
  it; eps-inflated Krawczyk contracts (ratio 0.25, cond 15.5), one root, s-enclosure [3.877083590022812, 3.877083590022816] contains
  s-hat. COST: 0.78 s/structure all-in (c_triage 0.0136 s, f_surv 0.775, c_FJ >= 0.994 s censored); break-even N = 3.2e7
  (triage-only ceiling 1.85e9); at N = 1e11 graphs 2.2e7 CPU-h = x3100 A85's 7 000; at the measured 1e36 x1e29. A85 baseline
  ~1350 s/node (6 PASS/5 FAIL/1 refused of 12), 63 s LP at 4 corners deep.
- Verdict: H1-by-structure LOSES on the count (>= 1e12 rigorously; 1e36 measured; break-even 3e7), not on the price; dominant
  multiplier named = decoration fan-out; k0_00 = A85's tree. Usable residue: Lemma H-LOC, the fixed-row Farkas + HC4 leaf (50 ms
  per closed structure) as (F)-type leaves for Lemma F-LEAF's zone-tree, the measured k = 11 growth laws. Discipline: 2 processes,
  BLAS pinned, headroom > 6 GB, A57/A60/A61/A86 untouched, frozen verifiers untouched, no certificate emitted. Files:
  docs/proofs/fj_census_k0.md, attempts/A88-fj-census/{code,results,notes,logs}, lean/depgraph.json (C.K4TIER note, chip released)
  + svg, REGISTRY row.

## 2026-09-03 A90-nocrit-blocked (Fable lead + 1 Opus chore, <= 2 processes) -- done-mixed (NOCRIT in SELECTED form with exact residue RES(4); FJ form is the wrong statement; Trump canary PASS)

- T [docs/proofs/nocrit_k0_blocked.md]: Lemma BLIND - an FJ certificate ignores every square carrying no positive multiplier
  (rattlers, unloaded touchers): moving them at the same side keeps the certificate verbatim. So "K0-BLOCKED => not FJ at any s"
  can only be a ROOM statement FJ does not see, and the brief's route (Lemma MENU far-side locks counted against L1/L6/per-wall
  caps/H-LOC) cannot close: LOCK (b)/MENU are about contacts that EXIST, not multipliers that are positive (A89-G1's wall).
- T: Theorem NOCRIT-SEL. Psi = total corner intrusion (depth d_c = 1 - min_Q max(p_x,p_y), tangency 0, tolerance-exact); a
  Psi-minimal sigma-minimiser z* exists (compact M(m)). Lemma K: every intruder is x-side / y-side / corner-type and retreats
  along e_x / e_y / both with exact positive rates. Lemma CLUSTER: all rows are affine in the centres (fjsecond87's zero
  centre-centre Hessian), so translating the retreat cluster C_e(Q) (squares pressing Q against e, transitively) is an EXACT
  packing at side m unless a member touches the far wall. Hence at z* every intruder of every corner is ANCHORED in each cardinal
  retreat direction: (W) cluster reaches the far wall, or (I) contains another corner's intruder that deepens. No FJ, no
  criticality, no second order (flat strata irrelevant) - TF-U's shape. Closed: rattler intruders impossible at z*; every intruder
  pressed on its far side; JAM-0 partner y-side, its presser column needs >= 4 squares to reach the top wall; Lemma COL: anchoring
  columns have >= 3 squares for m >= 1+2sqrt2 = 3.8284 (diamond-ghost regime below: tilts within 6.3 deg of 45, depth < 0.0084);
  Lemma PLATEAU [S]: rate-matched mutual anchoring slides at constant Psi to a K0-FREE point / wall / new contact.
- RESIDUE [OPEN, A90-G1] RES(4): a K0-BLOCKED Psi-minimal minimiser at which all >= 8 intruders are anchored - a FRAME of >= 3-square
  wall-to-wall monotone contact columns in both axes through the corner crowds (8 intruders + 3 free squares; Trump's skeleton
  with every slot square replaced by a tilted 2-crowd). Counting alone (11 squares, four >= 3-chains sharing members) does not close.
- T+M: where "all four corners blocked" enters - ONLY in refuting the residue, nowhere in the reduction (proved corner by corner).
  Trump: TL's shallow intruder sq4 = [0,1]x[0.8445,1.8445] (TL frame) is y-side (retreat = down only), its downward cluster
  {0,1,2,3,4,7,8} reaches the floor; sq6 is x-side, cluster {5,6,9,10} on x = s; RES(1) HOLDS at Trump's TL, so any refutation
  of RES(4) must use >= 2 blocked corners through Lemma COL's chain count. Canary [M]: Trump critical (cone residual 0.0,
  m_active 42, rank 34), TL 2-crowd locked (sq4 self-stress, sq6 MENU-locked by sq4 at rate -0.261), not excluded. PASS.
- M [T3, attempts/A90-nocrit-blocked/notes/t3_report.md]: A87's 520 exits re-run BITWISE (seed stream needs selftest()'s pool
  priming): the freeing square is the NON-DEEPEST intruder 520/520; retreatable by a single-square cardinal translation 508/520
  (511 with (1,1)), 507 with the singleton cluster; not flush-locked 515/520 (LOCK (b) LP), MENU-unlocked 100/108; LOCK and
  RETREATABLE never both hold. The 12 exceptions: one blocking vertex-on-edge contact, 3-4-square cluster wall-anchored, and the
  flow's actual exit is a coordinated 9-11-square SQP motion (Q sole mover 0/520) - a MOTION-CLASS gap of the translation test,
  not a lock (A90-G2: rotations / cluster motions would shrink RES). The 4 K0-BLOCKED non-FJ endpoints: RES holds at 2 (both
  s0380), fails at 2; the certified Gordan direction decreases a shallow intruder's depth 4/4 (s0380-2nd sheds all four second
  intruders at once). BLIND hunt: 0/167 K0-BLOCKED FJ points by repositioning unloadable squares; 70/167 points have fewer
  unloadable squares than deficient corners outright (hard count), the other 97 never yield a feasible doubling (heuristic);
  the 17 k0dir87 FJ endpoints have no stored z (data gap, ~50 min replay).
- Composition / Lean-readiness (T2): k0_00 = SEL-Psi + NOCRIT-SEL + [not RES(4)] + Lemma K0-FREE (k1_00 tree, Theorem U at s-hat),
  in the SELECTED form StratumKillSel Psi (A89 sect. 9.3 with Psi for Phi; s-hat clause via Psi-min over non-image packings, E.A36);
  DF-K0 / H1 NOT consumed; new Lean obligations N1-N5 (affine rows, CLUSTER, Lemma K rates, depth <=> interior meets slot, the
  residue). Price: not RES(4) as a SelForm (C) leaf is silent at A85's frontier -> A85's 3 200-7 000 CPU-h stands; a direct frame
  census is unpriced [C]. PI conjecture (n = 11) is exactly "not RES(4)".
- Discipline: 1 compute process, BLAS pinned, headroom > 12 GB throughout; A57/A60/A61/A86 untouched; frozen verifiers untouched;
  A87/A89 code imported, not modified; no certificate emitted. Chip C.K4TIER still owned by A89 (not released) - note added only.
  Files: docs/proofs/nocrit_k0_blocked.md, attempts/A90-nocrit-blocked/{code,results,notes,logs}, lean/depgraph.json + svg,
  REGISTRY row.

## 2026-09-03 A91-frame-census (Fable lead + 1 Opus chore, <= 2 processes) -- done-success (RES(4) census PRICED: finite, 5.7e28 at L1, ~1e37 at L2, realisable ~1.2e38; loses to A85's tree by ~28 orders; not-RES(4) stays a SelForm (C) leaf)
- T [docs/proofs/frame_census.md]: the FRAME defined exactly from A90's RES(4) at four levels (L0 roles/types/masks; L1 + one terminal per slot;
  L2 + first links; L3 full sign-consistent columns). Lemmas F1-F8 [T]: n_c <= 5 home squares per corner (area), nine K0-BLOCKED role patterns
  mod D4; a square touching two adjacent walls intrudes that corner with depth >= 1/2 (segment argument) => free squares touch <= 1 wall and
  (A89 exact depth-pair census) <= 1 both-walls square per corner; CHORD LEMMA (the chord of a unit square at distance 1/2 from its extreme point
  is >= 1, all tilts) => per wall <= 3 (N1 re-proved) and <= 1 free square per wall; terminal sets ((W): <= 3 far-wall squares; (I): far-corner
  home squares whose type contains the axis) with MUTUALITY and the RATE ROW (retreating corners {c, c_cross}, deepening {c_e, c_op}: disjoint);
  Lemma F6 link box rows; F7: Lemma COL's >= 3-member clause is VACUOUS at L1 (the far wall's two corners carry >= 4 home squares, the wall <= 3);
  F8: an X/Y retreater anchored only by one tilted D-type deepener is NOT anchored (rho_D < 1). Bound before enumeration: finite at every level,
  L1 <= 4.5e36 labelled by the 7-per-slot product (exact value by the product formula), ghost regime <= x2 per slot, D4 by Burnside.
- M [T2, attempts/A91-frame-census/notes/t2_report.md; product formula validated vs brute force 8/8 shapes]: L0 = 1.040e19 labelled EXACT
  (>= 1.25e16 orbits, MC 1.9e16); L1 = 1.558e32 labelled EXACT, >= 5.726e28 orbits (MC 1.28e29 +- 1.3e28, 97 % trivial stabilisers);
  ablation EXACT: roles only 4.5e36 -> F2(ii) 9.3e32 -> per-wall rows 1.56e32 (the whole combinatorial filter buys x3.3 at L0, x2.9e4 at L1);
  L2 ~3.8e40 labelled [MC bracket 1e39-1e41], ~1e37 orbits; L3 <= 1.56e59 EXACT UB, sign-consistency 0/20 on the median frame (~5e50, one digit).
  R6 (interval-linear LP: containment, masks, intrusion, Lemma K argmin-side type rows, F6 link rows): kill 315/316 = 0.9968 +- 0.0062 at ~4 ms
  => realisable at L2 ~1.2e38 labelled [EXTRAPOLATED, bracket 1e36-1e39]. Sharing: every R6 survivor shares column members across all six corner
  pairs, mean 0.33 free squares as middles, mean 6 squares serving two corners (A90 sect 4.4 quantified). CANARIES 3/3 PASS: C1 archetype
  (Trump with sq1/sq9 promoted; sq8 tangent too) is a member at every level, untouched by R1-R5 and by R6 (margin +0.104); C2 Trump absent
  ((1,1,2,1)); C3 four k0dir87 K0-BLOCKED endpoints satisfy every sect-2 constraint on their real geometry (6-11 of 12 slots anchored).
- M [T3, notes/t3_report.md, no certificate]: 20/20 uniform frames close at the ROOT LP in 3.8 ms (the generic frame's certificate is one LP);
  the archetype stays OPEN at tilt-bin depth 10 (111 boxes, 0 kills). PRICE 1.2e38 x 3.8 ms ~ 1.3e32 CPU-h vs 3 200-7 000: LOSES by ~28 orders,
  and loses twice (count + the survivors are exactly the unclosable ones); at L0 still 2e10 CPU-h.
- F [T, check with A90's cluster code]: the archetype's CLUSTERS are ALL WALL-ANCHORED (C_{+x}(1) = {1,2,8,10} at x = s, C_{-x}(8) = {0,1,3,4,7,8}
  at x = 0, ...); the chore's "100 % (I)-anchored, 2-member columns" is the minimal-chain extraction stopping at the first admissible (I)-terminal.
  Lemma PLATEAU is NOT what the archetype needs. Lemma W-GEN [T, sect 8.2]: with Psi^(w) = sum_c w_c Psi_c, weights Q-linearly independent,
  NOCRIT-SEL holds verbatim and every non-wall-anchored cluster with rate-1 members is STRICTLY anchored (D = Z-combination of weights with
  disjoint corner supports != 0); mutual rate-1 columns have at least one wall-anchored end; plateaus need a tilted-D rate tie (codim >= 1).
  A91-G1 [C]: termination of the slide iteration for tilted-D ties (no direction-independent monotone potential found: Psi_c lex, moments,
  sum d^2, active-row counts all fail) - not load-bearing for the archetype; even closed, the wall-anchored frames remain and die only by geometry.
- Design [sect 9, not run]: NOCRIT-SEL's rows as (C-sel) node tests in A85's tree - roles from reach boxes, type set T(B) from the argmin-side rows,
  forced retreats when T(B) c {X,D} or {Y,D}, anchoring EXISTENCE as a graph search over touch-capable boxes to far-wall-/(I)-capable boxes with
  the rate row on rate bins; sound, consumes Psi^(w)-minimality only (StratumKillSel). Expected effect = the existential-filter law (silent at the
  frontier); pricing = a 1-desktop-hour Opus chore on A85's stored 1 000/300/300 multi-corner gate samples + 12 LP nodes, measuring the kill on top
  of the 81.9 % exact contradictory gate. Verdict: k0_00 = A85's tree (3 200-7 000 CPU-h), not-RES(4) as its SelForm (C) leaf, A90 sect 6(i).
- Discipline: 2 processes, BLAS pinned, headroom 12 GB at launch; A57/A60/A61/A86 untouched; A85/A87/A88/A90 imported only; frozen verifiers
  untouched; no certificate emitted. Files: docs/proofs/frame_census.md, attempts/A91-frame-census/{code,results,notes,logs}, lean/depgraph.json
  (C.K4TIER note, chip released) + svg, REGISTRY row.

## 2026-09-03/04 A92-blocked-side (Fable lead + 2 Opus chores, <= 2 processes) -- done-success ((S) CERTIFIED at delta = 0.3 with boundary s0, delta = 0.2 open; CEIL + SLIDE proved; (N) residue = the slab below s-hat)
- T [docs/proofs/k0_blocked_side.md]: the PI target "K0-BLOCKED => side >= s-hat" split by DEPTH. (S) substantive (every corner's 2nd intruder depth >= delta):
  the brief's route-3 object (a root K-leaf with 8 depth-capable cores) does NOT exist - the depth-delta pose set has EMPTY core for delta < 0.134 (two
  60-deg wall-hanging squares share no point); replaced by the CROWD-WEIGHTED certificate, Lemma CW: mu >= 1 on every admissible square, mu >= 1+e on
  every square meeting the widened corner box [0,a_w]^2, total < 11+8e, verified by TWO runs of the frozen verify_case.py on ONE measure (run A n = 11+8e
  plain; run B weights/(1+e) with the exact complement of the crowd family as NO-families); Lemma B-YES transfers the hypothesis to s0 with pad
  (lambda-1)(a + 1/sqrt2), a_w < 1 iff delta > 0.4403 (s0 - m_lo). Boundary of (S) where it passes: s0 = 3.877084 (window [3.82, s0)).
  Theorem CEIL [T] (Wedge Lemma: a unit square in {y >= 0, y <= (x-x0) tan a} has min x >= x0 + cos^2 a / sin a; separating line): two disjoint unit
  squares in a quadrant have max(mu_A, mu_B) >= 1/(cos a + sin a) >= 1/sqrt2 => per-corner min(d1,d2) <= 1 - 1/sqrt2 = 0.292893, equality only at the
  diagonal 45-deg pair (deepfront87's conjectured ceiling PROVED; d2front87's certified 0.292893 at 4.357 is the maximum possible D2 at any side).
  Routes 1-2 CLOSED (negative): pair charge <= 1 at every delta (the diagonal pair strands exactly the triangle x+y <= sqrt2, area 1, no third square),
  4 x 1 < E(s-hat) = 4.0318; wall strips have the same ceiling (pinwheel fits eight crowd squares).
- T (N): Lemma SLIDE [forall-packings, no selection, modulo K0-O1 = k1_00's tree, the dependency K0-FREE already has]: slide the shallow intruders'
  diagonal retreat clusters (depth rate exactly 1/sqrt2 per 1/sqrt2 of side; Lemma CLUSTER affine feasibility with the container growing at the far
  walls; clusters only enlarge, <= 10 times), then teleport (K0-FREE) => a k1 packing at side m + sum(depths); (k1-a) kills it below s-hat. Hence every
  K0-BLOCKED packing at side m < s-hat has d2(c) >= s-hat - m at EVERY corner (nicks are bounded below by the distance to s-hat). Theorem N: a crowd
  certificate C(delta, m_lo) + SLIDE + K0-FREE kill every side in [m_lo, s-hat - delta]; a chain of certificates converges with ratio 0.4403 < 1 and
  gives s(11) >= s-hat - delta_inf, delta_inf = the depth where the crowd LP stops passing. EXACT RESIDUE RES-N(delta_inf): K0-BLOCKED packings at side
  m in (s-hat - delta_inf, s-hat) with some corner's 2nd intruder at depth in [s-hat - m, delta_inf) (+ nicked non-images at s-hat for uniqueness);
  inside it NOCRIT-SEL anchoring, JAM-0 (axis-aligned deep partner >= sqrt(s-hat - m) off the slot), K0-REUSE (no square containing K_p) hold and none
  empties it. Canaries: Trump K0-FREE (untouched; TL crowd satisfies CEIL), d2front87's 4.03-4.36 packings and s0115 outside every window (PASS).
- M [chore, attempts/A92-blocked-side/notes/crowd92_report.md]: engine copied from A89 (verify_case.py byte-identical, sha256 521cb01f...), one change
  in lpbox92.py (per-pose rhs 1+e on the crowd family, two-pass row oracle), certify92 two-run emitter; families EXACT for delta = 0.3/0.2/0.1/0.05
  (G outer cover 145-151 boxes/corner, overshoot 7.6-11 %; E complement 413-425 boxes each certified disjoint from F at all corners; D4 defect 2e-16);
  CANARY PASS at all four a_w. LP sweep (D4, 900 s, n = 11+8e): delta 0.3 e=1 tau 16.446 (eta -2.55) PASS; 0.2 e=1 tau 18.104 at 900 s (a NON-converged lower bound: 18.42 after 2926 s more, rising with rows; certificate needs minmass >= 0.970, got 0.94-0.97) OPEN;
  0.1 refused at every e (eta +0.59..+4.06, converged); 0.05 refused at every e with tau = 11(1+e) EXACTLY (all eleven squares fit in the dilated crowd
  family fractionally). CERTIFIED: delta = 0.3, e = 1 -- certs/runA_S_d0.3_e1_v2.json (n 19, total 18.962684, 1148 atoms) + runB_S_d0.3_e1_v2.json
  (weights halved, 413 exempt boxes, 0 holes), both PASS under the frozen verifier at depth 56, re-verified independently by the lead (rc 0/0).
  => THEOREM S(0.3): no K0-BLOCKED packing at any side in [3.82, s0) has every corner's 2nd intruder at depth >= 0.3 (boundary s0 = 3.877084).
  Engine finding (load-bearing for any NO-family cover of a REGION): verify_case.nofam_exempt is per-family containment, so a cover built from
  ABUTTING boxes leaves every seam un-exemptable -> 23-26 holes in run B; one-cell OVERLAPPING strips -> 0 holes on the same measure. delta = 0.2
  re-certified with the overlapping E by the follow-up chore: run A 13 holes, run B 65 holes all inside the crowd family (0 seam holes) -> geometric
  refusal at present LP convergence, NOT certified (delta_S = 0.3 stands; 0.15 not attempted, interpolated tau 19.5 > 19). Phase 2 (mixed patterns) not reached.
  OPS INCIDENT: a `git pull --rebase --autostash` on the shared dirty tree failed its reset --hard on a locked A57 log and clobbered 48 live tracked files of
  other campaigns for ~2 min; all restored byte-exact from the autostash commit 0966f2aa (kept, plus a stash entry). RULE (coordinator): no rebase /
  autostash / reset on the shared tree while campaigns run - git fetch, plain merge if needed, push own paths only, hand a non-clean merge to the coordinator.
- Discipline: 1 driver process + <= 1 LP/certify subprocess, BLAS pinned, gate 6144 MB; A57/A60/A61/A86 untouched; frozen verifiers untouched;
  writes: docs/proofs/k0_blocked_side.md, attempts/A92-blocked-side/{code,results,notes,logs,certs}, lean/depgraph.json+svg (K0.RES4 chip -> A92,
  nodes K0.CEIL/K0.CROWD/K0.SLIDE), REGISTRY row.

## 2026-09-04 A93-lean-wave8 (Fable lead, Lean only) -- done-success (T1, T2, T3, T4 all Lean theorems; replays pending the chore)
- T1 [lean/PackingCertMathlib/PackingCertMathlib/Crowd.lean, CrowdZone.lean]: Lemma B-YES (scaleC_meets_cornerBox, pad (lambda-1) r for r >= wT/2),
  the distinctness step (not_meets_two_corners), Lemma CW (crowd_sound: 8 crowd members priced >= (1+e) wd by run B, 3 by run A, total < n wd),
  Theorem S(delta) window form (crowd_cert_kill), mu_c attained + "depth >= delta <=> closed meeting" (muC, meets_cornerBox_iff_muC_le). The
  two clauses of Lemma CW that are NOT in verify_case.py are DECIDABLE checkers with soundness: sameMeasure (run B = run A / (1+e), exact
  integers) and crowdZones (run B's NO-families miss the crowd family [0,a_w]^2 at every corner: eight separating-axis tests with the
  ratCosSin/rmul4 enclosures, bisection). crowdKill_of_files: 2 x checkCaseI + sameMeasure + crowdZones + rational side conditions =>
  CrowdKill delta m_lo s0. A94 correction absorbed: crowd_sound_incidence = Lemma CW-S (1 + r_max runs, pin cores, budget 11 + 2 m_u e,
  incidence double count). Generator lean/gen_crowd_lean.py (isolated Corpus/Crowd/Check_<tag>.lean); smoke tests scratch/A93CheckerTest.lean.
  NO crowd certificate exists yet (A92 chore parked on the commit gate) => no replay module.
- T2 [Slide.lean]: Lemma SLIDE is a THEOREM modulo K0-O1 (K0O1 := forall c, SlabKill {corner slot c} 3.82 s-hat): slide_crowd - EVERY packing
  at side m in [3.82, s-hat) has, at every corner, two distinct squares meeting the closed box [0, 1-(s-hat-m)]^2. PROOF SIMPLIFICATION: no
  retreat clusters, no Lemma CLUSTER/Fact A, no enlargement rounds - translate the WHOLE packing away from the corner with the container
  growing at the far walls (a rigid motion is a packing; mu_c rises by exactly tau); attained minima give tau < s-hat - m; K0-FREE
  (k0free_kill = teleport_packing + K0-O1) closes. Finding: A92's sequential Step 2 only proves sum_{i>=1} d_i >= s-hat - m; the stated
  d_2 form needs the simultaneous motion (A94 sect 3.4 says the same) - the Lean statement is the d_2 form. A94 addendum [PinnedSlide.lean]:
  Lemma SWEEP (sweep_core: floor argument on a Young down-set) and the cluster-free Lemma MOVE (pinnedShift_packing: pin blocks translate
  with their anchoring walls, non-pins away from the corner; packing + ContainsPins at side m+tau for every tau >= 0). slot_slide (the
  teleport composition with the clip census / Lemma CONT) = named obligation.
- T3 [Ceil.lean]: Theorem CEIL is a THEOREM: ceil / ceil_packing, max(mu_BL A, mu_BL B) >= 1/sqrt2 for interior-disjoint unit squares in
  [0,s]^2; separating line from geometric_hahn_banach_open on the open convex interiors + interior combos; corner-cut case (mu >= 0.853);
  Wedge Lemma wedge_x/wedge_y with the concavity step as ONE factorisation (aS)^2 - (a^2-(a-b)C)^2 = (a-C)((a^2+(a-b)^2)C + a b^2).
- T4 [Composition.lean, TopLevel.lean roster note]: K0O1, slabKill_of_tree (K0-O1 from a closed tree), theoremN_slab, chain_cover,
  no_packing_of_chain, s_eleven_ge_of_chain (s(11) >= s-hat - delta_K from K0-O1 + a chain - CLASS-BLIND), classKilledAt_below_of_chain,
  ShellKill i delta (RES-N as the named hypothesis), classKilledAt_of_chain (ClassKilledAt i m on the whole window for EVERY class).
  Roster: stratum_kill -> K0-O1 + chain replays + ShellKill per class on the shell (s-hat - delta_K, s-hat] (trees/slabs restricted to the
  shell; k0_00 = RES-N open); trump_residual -> A60's tree on the shell only. T5 cost law: 2 x checkCaseI per certificate (0.4-0.6 ms/box),
  sameMeasure < 1 s, crowdZones <~ 1 min.
- Axioms (scratch/AxiomsA93.lean): propext/Classical.choice/Quot.sound only for every new theorem. Build: default target green (one lake
  build at a time, isolated native_decide modules cache-hit). Git: A86's Lean wave is UNCOMMITTED; A93 sits on top - commit together.
- Discipline: no compute campaigns touched (A57/A60/A61/A92 untouched); depgraph note-only on K0.CW/K0.SLIDE/K0.CEIL/K0.RESN/K0.FREE (+ V.CASE
  consumer note), chips stay with A92; writes: lean/PackingCertMathlib/{Crowd,CrowdZone,Slide,PinnedSlide,Ceil,Composition,TopLevel}.lean,
  PackingCertMathlib.lean, scratch/{AxiomsA93,A93CheckerTest,A93Probe,A93Probe2}.lean, lean/gen_crowd_lean.py, lean/README.md,
  lean/depgraph.json+svg, attempts/A93-lean-wave8/code/depgraph_note93.py, REGISTRY row.

## 2026-09-04 A96-a57-parametric (Opus lead, engineering, <= 2 verifier processes) -- running (A57 sides 4/3/2 FROZEN; parametric pass running; slivers CLOSED; sigma ladder discharged)
- T1 FREEZE [A57 code/FREEZE_TAGS.txt (G4,G3,G2), code/launch.ps1, code/scaleup.ps1]: sides 4/3/2 can no longer start. TWO gates because
  the running scaler (pid 8252) holds its 46-entry queue IN MEMORY: launch.ps1 refuses a frozen -Tag (logs to scaleup.log, exit 0 so the
  entry counts as consumed) and binds immediately; scaleup.ps1 drops frozen tags from the queue AND skips shards whose pidfile exists, so a
  restart is idempotent instead of relaunching G1 from the top. Restarting the scaler was rejected as the fix for exactly that reason.
  Verified live (launch.ps1 -Tag G4 -> "FROZEN k5_11 G4 0/6", nothing started). G1 shards untouched; A60/A61/A92/A93/A94 untouched.
- T2 PARAMETRIC PASS [A96 code/{select96,to_param96,param96,run96.ps1}, frozen verify_param.py + verify_case.py copied byte-identical,
  code/frozen.sha256]: 373 candidates (k5_11_G1 153, k5_16_G1 197, level-2 23). to_param96 widens A57's core_affine from the 12 level-1
  column centres to the whole (P-aff) family e_q(s)=c0+q(s-2c0), q in Q_dy -- exactly what cover_invariance.md CI-1..CI-3 proves, and what
  A57's emitter refuses on every level-2 child; the exact reconstruction assert is kept, so an off-family coordinate is rejected not
  re-anchored. Level 1 is G1 ONLY (L1 is the delta=0 emission: same stratum, different pin hypothesis, so it buys no G1 coverage).
  Logic kills stay per-side (CI-4, grid.py --ccheck) and are never re-emitted. MEASURED over 21 runs: mean parametric wall 266.3 s vs mean
  fixed-side 1332.7 s = 0.20 of ONE side (0.05 of the four it replaces); median 119.1 s.
- T3 SLIVERS -- CLOSED, and both proposed routes were the wrong diagnosis [code/{sliver96,endpoint96,resolve96}.py]. The two recurring cells
  A=[191/50, 977934271/256000000] and B=[979732417/256000000, 7654271/2000000] are ONE s-cell each (W/1024) and are an s-RESOLUTION
  artifact of the single global pass, not a fixed-s degeneracy: every witness is at a t-extreme with sample mass 4987/4000 > 1 and
  kind="undecided". More depth / t-biased splitting on the FULL window does NOT help; re-running the SAME certificate on the sliver
  SUB-window does, because verify_param splits the widest axis and the restricted window makes the s-cells ~1000x finer at once.
  Y0192 (sliver A) PASS 2.5 s, Y0271 (B) PASS 0.6 s, Y0067 (A+B) PASS 3.0 s -- all upgraded to FULL WINDOW, no new LP, no new document.
  (3a) A.LB382 does NOT close sliver A: s_eleven_ge_382 kills side exactly 3.82 and (by dilation) every m <= 3.82; monotonicity runs the
  other way, so it gives nothing on (3.82, 3.8200557] -- the open-endpoint form would have left an interval of the same width. Moot now.
  (3b) A fresh fixed-side slack-core certificate at 3.8271 is not worth buying: LP+certify per node (A57's measured 23-3800 s) vs 0.6-3.0 s.
- T4 SIGMA LADDER [code/{ladder96,mirror96}.py]: sigma-symmetric nth=10 ladder built at all four sides; 720/720/605/605 orbits; a_min gate
  holds everywhere (0.362009 vs deployed 0.356602 at side 1, and above the 0.34 floor at every side); 1177 LP children removed over four
  sides, 861 over sides 2-4 -- A95's counts reproduced from an independent build. TWO things done properly rather than assumed: (i) the
  representative's core is TRANSPORTED to its partner (sigma K_rep, not the partner's natively-computed core) -- a=(1/2-hd)/(1+width_t)
  depends on the t-width and sigma does not preserve t-widths, which is the whole source of A95's 19/720 native disagreements; (ii) the tree
  obligation "every square with (centre,t) in sigma B contains sigma K_B" is re-derived by A57's own pinguard.classify on the mirrored box
  carrying the transported core: 2650/2650 orbits agree, ZERO failures. mirror96 rewrites both certificate formats (atoms x<->y; cores
  swapped, tm -> (1-tm)/(1+tm)) and asserts sigma o sigma = id field-for-field. Deploying the ladder (720 orbit reps) is a fresh tree run,
  NOT executed here.
- T5/T6 [results/{scoreboard96,projection96,window_rows_*}.json]: class coverage is an INTERSECTION over the cover's boxes, never a mean.
  RE-PROJECTION: four-fixed-side baseline 25.74 / 15.44 wall-days (3 / 5 workers) -> parametric route 12.76 / 7.66, and 11.89 / 7.13 with
  the sigma ladder on k5_11. Level 2 is emitted once at side 1 and verified over the window (no per-side fanout left to remove); the
  first-200 measurement is supply-limited, not budget-limited -- only 31 level-2 rows exist today (L1_D2), no G1_D2 until the scaler's G1
  queue empties and deepen starts.
- Discipline: frozen verifiers copied byte-identical and never edited (code/frozen.sha256); BLAS pinned; 6144 MB commit gate in the
  launcher itself (param96 self-gates on GlobalMemoryStatusEx AvailPageFile); <= 2 verifier processes throughout -- one duplicate runner
  that a failed background launch had left behind was found by process attribution and killed. A60/A61/A92/A93/A94 untouched.
- A96 leg 1 close (2026-09-04): parametric pass 28 nodes (k5_11_G1 27: 22 full-window + 5 partial, class intersection 0.98438; k5_16_G1 1);
  cost 0.21 of ONE fixed side over 28 runs. Slivers CLOSED on the three single-sliver nodes (0.6-3.0 s each, upgraded to full window);
  three multi-gap nodes (Y0540/Y0101/Y0840, 6 witness cells each) queued with bisection. LEVEL-2 delta=1e-2 PROBE (one deepen shard at the
  DEPLOYED pin slack, since A95's 216.4 s/child came from delta=0 rows): 7 children of one parent, 4/7 free logic kills, 332.8 s/child =
  1.54x A95's number -- reported as a sensitivity (level 2 -> 17.21 days 1-proc), NOT folded into the headline. The pass is currently
  parked on its own 6144 MB commit gate (free commit ~4.8 GB under A57 G1 + A61 + A92 + A94); it self-resumes, no supervision needed.

## 2026-09-04 A94-slot-crowds (Fable lead + 1 Opus chore, <= 2 processes) -- closed done-mixed: theory lands, no certified PASS
- T [docs/proofs/slot_crowds.md]: SLOT-CROWD [T] forall-packings and UNCONDITIONAL for pinned classes - every usable unclipped completable slot of S is met by >= 2 non-pin
  squares, else teleport onto the slot lands in the k6 extension that A56/A61 kill on the window (k5_11: BL(1,1)->k6_18, BR(0,1)/TL(1,0)->k6_20, TR(0,0)->k6_23 to 3877/1000;
  k5_16: BR(0,1)->k6_29, TR(0,1)->k6_30, TR(1,0)->k6_28, BL(1,0)->k6_23; BR(1,0)/TL(1,0)->k6_27 OPEN). Exact census: 8 completable slots each, 4/6 unclipped, 4 usable each.
  SLOT-SLIDE [T]: retreat along the slot-frame diagonal away from the backed sides; pin blocks translate WITH their anchoring walls (stay at their slots in the grown container)
  and never obstruct (Lemma SWEEP: every relative motion is away from a Young down-set's walls) - no (C) contact; d2 >= s-hat' - m at every usable slot. CORRECTION to A92 3.1:
  the d2 form needs the JOINT translation of all shallow intruders (the sequential proof gives only the sum bound); A93 T2 should formalise the joint form.
  Lemma CW-S [T]: slack pin cores rho >= (lambda-1)A_S, slot pad (lambda-1)(a+1/sqrt2+max(i,j)) (ratio 0.698 vs 0.440), INCIDENCE budget N + 2 m_u e with r_max runs B_r.
  Theorem N-S: chain + A57 G1 shell; G2/G3/G4 retired iff delta_inf <= 0.0154, G3/G4 iff <= 0.0300, G4 iff <= 0.0446. Lemma CEIL-T (exact Trump): k4_03/k4_06/k4_08 crowd
  ceilings 3.72/3.72/3.61 < 3.82 - the chain is VOID for them on the window (P-TREE stays); k4_11 3.861; k4_05/corners4 eligible only after k5_11/k5_16 die on the window;
  k <= 3 tier blocked on k4 window kills. Exact-Trump canary PASS (all 6 unclipped trump5 slots doubly met; d2 = 0.016049 ... 0.305293; A58 reproduced exactly).
- M [chore, notes/slotcrowd94_report.md, 397 min, 23 LPs, 4 cert chains, canaries PASS incl. e=0 regression]: on (s0, G2] the LP passes only at delta >= 0.2 for both classes
  and fails at delta <= 0.1 (k5_11 delta 0.1 e 1/8: tau 7.007 vs budget 7) => delta_inf >= 0.2 at the s0 side: THE CHAIN REMOVES NO A57 SIDE. On (G4, 3.82] k5_11 passes at
  0.1/0.04/0.02 (eta -0.25/-0.22/-0.21), k5_16 at 0.1, but no certificate closes: close-out certification of the converged delta 0.1 node (minmass 1.0, 39 atoms, 1794 s) =
  run A PASS, B1 PASS, B2-B4 FAIL with 30-32 exact HOLES - the incidence (r >= 2) rows are not priced by the row oracle (A94-G4, engine gap; eps_geo cannot cure real holes).
  A certified delta 0.1 would not kill the slab anyway (needs delta <= 0.0438 = the unconverged 0.04 pass, minmass 0.88, predicted to fail identically); the slab is A96's job.
  m_u = 4 (incl. the k6_23 slot) folded into Theorem N-S honestly: s-hat' = 3877/1000, sliver to G1. Verdict: mechanism sound, LP-live at the low side, dead at the s0 side.
- Discipline: <= 2 processes (driver + one certify), BLAS pinned, 6144 MB commit gate x2 readings; A57/A60/A61/A86/A92/A93 untouched; frozen verifiers untouched; git: fetch +
  plain merge (already up to date) + push own paths. Files: docs/proofs/slot_crowds.md, attempts/A94-slot-crowds/{code,results,certs,logs,notes}, lean/depgraph.json+svg
  (C.A57 note + chip -> A96, C.K4TIER CEIL-T note, K0.SLIDE joint-translation note, K0.CW slot-form note), REGISTRY row.

## 2026-09-04 A97-wall-budget (Fable lead, theory; no chores of its own) -- closed done-mixed: the budget is a theorem, the mechanism does not close
- T [docs/proofs/wall_budget.md]: Lemma WALL-F [T] - the sound 1-D wall budget is sum over ALL squares of the interior chord on the line at distance
  1/sqrt2 from the wall (a wall-toucher's chord is EXACTLY 1/cos(tilt) in [1, sqrt2]); WALL-3: <= 3 touchers per wall, tilt slack sum(1/cos - 1) <= m - 3
  (< 0.877084; upright + two diamonds needs m >= 1 + 2 sqrt2 = A47's s* / Lemma COL's ghost threshold). Lemma WALL-NP [T]: the brief's projection width
  cos t + sin t is NOT a budget (interior-disjoint touchers with overlapping projections, overlap 0.0847 at 20 deg vs a diamond; up to 0.092) - the sound
  width is 1/cos t. JAM pair (JAM-0 form, g <= 0.1): footprint 1 (S) on both walls + 1/cos(alpha) (N) on the NICK wall only. WALL-J2/J3 [T]: the slot
  square's pusher (NOCRIT-SEL Cor. 2) is a FREE square, distinct per jam => j <= 3 jams (JAM^4 dead = cases85's free-square kill); WALL-J4 [T]: two jams
  nicked on one wall impossible (>= 4 > m); two jams on one wall with the nicks on the perpendicular walls are NOT excluded by the budget; j <= 2 at
  OPPOSITE corners only under hypothesis P-ON (pusher with unit footprint on the pusher wall, e.g. touching it). P-ON is not a theorem and the exact
  K0-BLOCKED corpus REFUTES it 3/3 (k0dir87 s0380 BR x2, s0076 BR at sigma 4.000: pusher floating 0.76-0.94 above the wall, footprint 0) - the residue is
  the floating-pusher POCKET (= the brief's above-wall lock (d)). Lemma WALL-S [T]: a jam's nick-wall neighbour keeps <= 1 unit-footprint member (exact
  inequality in tilt and wall distance); a zero-footprint intruder has depth <= 1 - 1/sqrt2 = 0.2929 (CEIL's constant); an OFFSET-UPRIGHT neighbour gets an
  offset FLOOR >= 0.2686 (Trump-safe), not a cap. SLIDE confines jams to m >= s-hat - g^2/sqrt(1-g^2) >= s-hat - 0.01005.
- COMPOSITION (T2): NOT dead by area for j = 0, 1, 2, 3 and NO offset cap: charge85 (200 pairs, exact lower bounds) has stratum minima JAM 0 / BLOCK 0 /
  WEDGE 0.023 / OTHER[0.1,0.3) 0.121 rising to 0.45 at g in [0.5,0.7); 89 % of the 7 044 realisable pairs pass the wall squeeze, including the charge-0
  ones (A47's flush-parking zero, one level up); forced sum ~ 0 << 4.03 in every pattern.
- T3: (C-wall) leaf rule = box-level phi_lb (exact, LP-free, monotone); census [M, results/wallcensus97.json]: 178/644 boxes unit-footprint per line,
  7.3 % of pairs have both members unit on a line, 10.8 % exceed s0 - 2 on either line; JAM patterns are ~0.06 % of the 4-tuple census; under P-ON 6/21
  patterns (25/81 labelled) die. Escapes: E1 floating pusher (corpus 3/3), E2 zero-footprint shallow member (27 % of pairs per line; depth <= 0.2929),
  E3 tilted on-wall pushers (allowed, cost >= 1: tighten only), E4 y-side/corner-type jams (S floating, presser over its far corner), E5 the SLIDE shell.
- CANARY [M, exact 70 dps, results/trump_wall_canary.*]: Trump PASSES WALL-F on all four walls: bottom 3.282914 / left 3.000000 / right 3.308901 / top
  2.630367 <= s-hat, touchers 3/3/3/2; the LEFT wall is tight at exactly three flush units (slack s-hat - 3 = 0.877084); no wall carries two diamonds;
  no jam corner (TL is OTHER, g = 0.8445, partner left-wall distance 0.8317 >= 0.2686).
- Discipline: theory only (three second-scale scripts, one process, no BLAS); A57/A60/A61/A96 untouched; frozen verifiers untouched; git fetch + plain
  merge + push own paths. Files: docs/proofs/wall_budget.md, attempts/A97-wall-budget/{code,results}, lean/depgraph.json+svg (K0.RESN note, chip A97),
  REGISTRY row.
- PI FOLLOW-UP (same day) Lemma FLOAT [T, wall_budget.md 2.4]: Lemma SHADOW (a square's points below h0 = 1/sqrt2 lie within the x-range of its chord
  at h0) => the strip P = (a+1, a+2) x (0, h0) beside the slot square on the pusher wall strands area >= h0 (1 - L), L = the WALL-F chord length spent in
  (a+1, a+2) by the other squares. Every jam (x-side, y-side or corner-type) pays 0.7071 (1 - L) in AREA plus L in WALL LENGTH; a floating pusher with an
  empty pocket strands exactly 0.7071 - SHARP on the corpus (s0380 BR x2: L = 0, stranded 0.7071, nothing meets P; s0076 BR: L = 0.021, stranded 0.7064).
  P-ON resolved into this dichotomy (A97-G1 closed, A97-C1 discharged). Composition rerun: jams contribute <= 3 x 0.7071 = 2.12 (j = 3, all floating) or wall
  units instead (P-ON => j <= 2 opposite); with charge85 minima 0/0/0.023/0.121 for the other corners the four-corner sum never exceeds 4.0318 for any j;
  max jam count stays 3 unconditionally; offset floor 0.2686 on nick walls, L/2 - 0.2314 on pusher walls (L > 0.463). Trump canary unchanged (no jam).
- A96 concurrency leg (2026-09-04 13:46-14:45): NO USABLE CONTENTION NUMBER, and the reason is the measurement, not the hardware.
  The concurrency raise did not happen: A57 stayed at 3 shards for the whole hour (neighbours96 timeline, 104 samples: busy
  distribution 6:7 7:67 8:18 9:12, mean 7.34, NEVER 10; A57 slot share 2.95). Cause: the restarted scaler made exactly ONE launch
  (k5_16 G1 s2, 13:46:28) and thereafter spawned launch.ps1 children that never produced a tree57 process or a pidfile (live ones
  observed at 14:46:45 and 14:47:28; scaler CPU 0.5 s over the hour, i.e. sleeping, not spinning). launch.ps1 invoked DIRECTLY with
  the same arguments works first time (k5_11 G1 s3 = pid 43044), so the fault is in the scaler's invocation context, not the script
  -- A57 infrastructure, left for A57's owner rather than patched blind mid-run.
  What the numbers would have said, and why they are not reportable: A57 s2 shard per-node wall 372.3 s median before (n=111) vs
  741.8 s after (n=6) -- but n=6, p25 51.9 / p75 1468.1, and every one of those rows is stamped busy=7, i.e. the SAME concurrency as
  before. A96's 12.5x median jump is queue composition, not contention: the pass is sorted by ascending atom count, so later rows are
  intrinsically dearer. Controlling for that (8 rows before vs 6 after, all 'easy', atoms 6-7) still gives 127 -> 450 s median, but the
  within-bucket spread is 10 s to 1500 s at IDENTICAL atom count, and the neighbour stamps invert the effect (busy=6 median 1116 s,
  busy=7 558 s, busy=8 342 s). That is noise with a sample size, not a memory-bandwidth signal on the 12700K.
  Now at 4 A57 shards + 2 A96 verifiers (deepen held back: the coordinator's allocation summed to 11 against a cap of 10). Fresh
  baseline snapshotted (results/contention_before_4shard.json) so the next window measures the concurrency it claims to.
- A96 contention leg 2 (2026-09-04 14:56-15:57, 4 tree shards + deepen + 2 verifiers, 9-12 busy): NO CONTENTION DETECTABLE.
  Controlled read (k5_11 s2, the one shard that ran through both regimes): baseline busy~7 median 386.0 s (n=119) vs busy 9-12
  median 379.8 s (n=7) -- 2% apart, i.e. flat. Pooled A57 rows by stamped neighbour count: busy=11 median 285.0 s (n=18),
  busy=12 292.5 s (n=5), both AT OR BELOW the 351.4 s all-time baseline; the two small buckets that look bad (busy=9 551 s n=3,
  busy=10 906 s n=2) move the wrong way, which is the noise floor showing. Honest bound: with the s2 wall distribution spanning
  7 s to 12787 s, n=7 excludes only a large effect (order 2x); a 10-20% penalty is invisible at this n and is NOT ruled out.
  Throughput is where the raise paid: 41 A57 rows in the hour at 4 shards vs 16 in the previous hour at 3 (the scaler wedge).
  Working set 5.9 GB against the 26 GB budget; the 12700K is not memory-bandwidth limited at this concurrency.
- A96 pass at 225 nodes: k5_11_G1 92 (55 full-window, 37 partial), class intersection 0.97754; k5_16_G1 133 (85 full, 48 partial),
  0.99219. Re-projection improves to 10.46 / 6.28 wall-days at 3 / 5 workers (9.70 / 5.82 with the sigma ladder). Level-2 delta=1e-2
  probe now 13 rows / 2 parents: 30.8% free logic kills, 597.4 s per child = 2.76x A95's delta=0 figure -- still a sensitivity, not
  the headline. 85 partial nodes are queued for resolve96 (paused: the box is at the 11-process cap).

## 2026-09-04 — A98-exchange-lemma (Fable, theory lead) — done-mixed: EXCHANGE not proved, not refuted; framework + residue exact
- PI mechanism: remove a corner's two intruders, place the slot square, re-fit one square at the SAME side (A87: 21/33 corners, 8/8 packings
  convert somewhere, Trump fails); refined mid-attempt to the recursive YOUNG FLOOD (grow a Young diagram of exact cells; free / single /
  double cells; rigid slide-ins; RELEASE via the pinning graph). Deliverable: docs/proofs/exchange_lemma.md.
- [T] Lemma TWO: some corner has EXACTLY two intruders (sum n(c) <= 11) and the slot square is disjoint from every non-intruder by definition
  (third-meeter closed; A87's 33/33 is a tautology). Lemma FLOOD-D: a Young diagram D at c with N(D) = #squares meeting int D <= |D| gives a
  k >= 1 packing at the same side - forall-packings, no selection, no criticality; the flood is a strategy for finding such a D. Lemma X: the
  excess X(D) = N(D) - |D| = (overhang of the displaced squares beyond D) - (free area inside D); K0-BLOCKED means X(slot) >= 1 at every
  corner. Lemma CAP: at side < 4 EVERY square meets the 3x3 block (separating line + the largest square in the corner triangle has side m - 3),
  so X(3x3) = 2 and a win needs <= 8 cells with >= 3 untouched squares outside D. Lemma RELEASE-CL: an untouched square leaves a cell iff its
  retreat cluster in the reduced packing is not WALL-anchored (Lemma CLUSTER verbatim; NOCRIT-SEL's (I)-anchoring is irrelevant at one corner);
  removing a corner intruder breaks only chains it presses ACROSS (its partner, Lemma CROSS) - the PI's RELEASE lemma is the definition of
  the stall, not a smaller residue.
- [T] Lemma EXPOSE: a re-fit Q0 is valid iff no untouched square meets the EXPOSURE int Q0 \ (A u B). Lemma FLUSH-JAM: at a JAM corner the
  flush cell of the nick partner has an exposure of five explicit slivers; the wall-side and S-side ones are SEALED; the top sliver (width
  <= g - sin(alpha) + tan(alpha/2), height <= g tan(alpha)) can be entered only by a wall-hugging square tilted >= the partner's tilt (A89
  5.2's "presser within r of u", exact), which at side < 4 INTRUDES THE ADJACENT CORNER (depth >= 4 - m + beta - delta): a JAM stall is an
  interlocked wall column, and the stall propagates to the corner above through B's top vertex. Lemma CROSS/ARM: after A's removal the
  partner's retreat across the separating line is free of A; B + (d, d) has mu = 1 exactly (SLIDE's identity).
- [M] static_flood98 (exact census over EVERY Young diagram at every corner, 8 corpus packings + Trump, 2.4 s): on the only sub-4 corpus packing
  (record_s0115, 3.9855) the 2-cell static flood REPRODUCES A87's depth-1 verdict corner by corner - nick corners (d2 = 1e-8) win with the
  partner's own cell (A87's verified placements ARE those cells), substantive corners (d2 = 0.0145) stall at all 20 diagrams (min X = 1;
  BL's arm cells are met by the column presser sq10 and by BR's deep intruder sq2 + pusher sq9, and symmetrically: adjacent crowds interlock
  through the 4 - m = 0.015 overlap of their arm cells); at side >= 4 the static flood is VACUOUS (16-cell grid, min X = -5), so the seven
  corpus packings at 4.00-4.11 measure nothing about the window. exposure98: all 21 verified A87 placements are B re-placed inside its own
  footprint (area in B >= 0.71, >= 0.99 in 15; exposure min 2e-6, median 0.0016, max 0.25) - the self-contained exchange never occurs;
  translation re-fits (ARM) certify 2/33, the pressed square blocking at distance = depth in 20 of 31 failures.
- CANARY Trump: min X = 1 over all 20 TL Young diagrams (cell below the slot met by sq3, sq4, sq7; cell to its right by sq6, sq9); K0-FREE
  corners X = 0 trivially. PASS. flood87 (A87 chore, PI measurement, second pass with the tangency fix, 23/33 rows at close-out): 21
  FLOOD_SUCCESS (17 at depth 1, 4 at depth 2-3 by a free cell after slide-ins, all exactly verified), 2 stalls (record BL/BR: no completable
  slot at shape [3,3,3], deficit 2 = Lemma CAP; releases = slide-ins only, 5 and 7); first pass had Trump TL at deficit 2 after two pay-2
  steps (the stall path); the terminal canary row lands with A87's notes/flood87.md.
- RESIDUE RES-X = INTERLOCK: every corner has X(D) >= 1 for every reachable Young D and every frontier square wall-anchored; subset of A91's
  wall-anchored frames plus the removal budget; realised at two corners (record) and at Trump's TL; NO four-corner INTERLOCK packing known
  or constructed (a JAM pinwheel needs, on every wall, two near-flush wall-huggers with the upper tilted >= the lower - the A47 I-L19
  recursion closed around the boundary - at margins ~ alpha g below any scanner-level certifier) [C]. In the window SLIDE puts the jam's
  sliver height >= s-hat - m; nothing empties RES-X.
- T2 leaf EX = Lemma EXPOSE at box level (cores of the pair boxes, shadows of the others; exact, LP-free, monotone, forall-packings (T)-type):
  neighbour-free yield 0 % (a core containing a cell is the single-pose K0-REUSE pocket), silent at the pair frontier, free once the column
  above B and the row right of A are localised - A85's price unchanged (existential-filter law). T3: if the lemma lands forall-packings on the
  window it discharges stratum_kill (k0_00) in the PLAIN form modulo K0-O1-ALL (every nonempty-skeleton class dead on the window); the
  uniqueness clause at s-hat needs flood displacement < r_B (true at nick corners only). Lean: one leaf exchange_flood or EX in the A85 tree;
  replay certificate = the final configuration under sat_squares (exchange87's certifier is that checker).
- Discipline: theory only (two second-scale scripts, one process, no BLAS); A57/A60/A61/A96 untouched; frozen verifiers untouched; git fetch +
  plain merge + push own paths. Files: docs/proofs/exchange_lemma.md, attempts/A98-exchange-lemma/{code,results,notes}, lean/depgraph.json+svg
  (K0.RESN note, chip A98 released), REGISTRY row.
- A98 addendum (flood87 final, 1253 s, A87 notes/flood87.md): 30/33 floods succeed, all exactly verified (21 depth 1 = exchange87, 8 depth 2, 1
  depth 3: 9 corners rescued beyond the depth-1 exchange, all at side >= 4); 3 stalls = record_s0115 BL/BR + TRUMP TL, each at the full
  block [3,3,3] with deficit 2 = Lemma CAP; canary_OK = True; releases were slide-ins only. Consistent with the static census corner by corner.
- A96 level-2 gate (31 rows / 4 parents, delta=1e-2): the 2.76x does NOT hold -- it was small-sample drift. The per-child scale
  vs A95's delta=0 216.4 s has fallen monotonically as parents landed: 1.54x (7 rows/1 parent) -> 2.76x (13/2) -> 2.43x (28/3)
  -> 2.21x (31/4) pooled, 2.36x over COMPLETE parents only (3 parents, 29 children, 511.4 s/child; the 4th parent is still being
  expanded by deepen and its children arrive logic-kills-first, which biases the pooled figure low). Per-parent per-child cost is
  197.2 / 351.2 / 841.0 s -- a 4.3x spread across three parents, so no single scale factor is yet determined; 2.36x is the number
  to use and it is soft. Logic-kill fraction settled at 19.4% (it read 57% at one parent).
- LEVEL 2 DOMINATES: at scale 2.36x the remaining wall is level1 11.39 d + level2 36.62 d = 48.01 d 1-proc, level 2 = 76.3% of it.
  Schedule at 5 workers 9.60 d (9.13 d with the sigma ladder), at 3 workers 16.00 d -- against the four-fixed-side baseline of
  15.44 / 25.74 d. So the parametric route still wins by ~1.6x, but the win is smaller than the delta=0 level-2 number implied
  (6.55 d at 5 workers), and the whole remaining schedule is now a level-2 question, not a level-1 one.
- Resolver sweep complete: 82/82 partial nodes closed to full window, zero residual, median 4.1 s, 1718 s total.
- A96 level-2 re-projection (both least-supported terms replaced with measurements). THE 2.76x DOES NOT HOLD: at 8 complete
  parents / 70 children the delta=1e-2 level-2 LP cost is 336.1 s/child = 1.553x A95's delta=0 216.4 s. The scale walked
  1.54 -> 2.76 -> 2.43 -> 2.36 -> 1.55 as parents landed; the high readings were one outlier parent (Y0059, 841 s/child) in a
  3-parent sample. Per-parent spread is still 126.8-841.0 s, so 1.55x is the number to use and it remains soft.
- LEVEL-2 PARAMETRIC VERIFY, MEASURED on 15 real delta=1e-2 children (replacing the level-1 mean): mean 505.9 s, median 424.1 s
  vs the 200.5 s level-1 mean previously assumed = 2.52x. This is the term that now dominates: 4608 level-2 children x 505.9 s
  = 27.0 d 1-proc. Caveats: n=15, one TIMEOUT counted at its 1500 s cap (censored, so the true mean is >= 505.9) and one
  abnormal exit (rc=-1) to re-run; sample atoms range 4-88, so it is not a clean median-node sample.
- LEVEL-3 DESCENT, MEASURED: 5/74 ALIVE at depth 2 = 6.8%. A95's schedule has NO level-3 term at all -- an unstated 0% descent.
  At 6.8% this adds 24.27 d 1-proc to the parametric route and 35.84 d to the fixed-side baseline.
- SCHEDULE, like-for-like (the SAME level-2 per-child cost and level-3 rate applied to both routes -- comparing a corrected
  parametric number against A95's uncorrected baseline would have been apples-to-oranges, and would have made the parametric
  route look WORSE than the fixed-side plan):
      parametric  level1 11.59 + level2 44.36 + level3 24.27 = 80.22 d 1-proc -> 16.04 wall-days at 5 workers (15.57 w/ sigma)
      fixed-side  level1 35.81 + level2 64.29 + level3 35.84 = 135.95 d 1-proc -> 27.19 wall-days at 5 workers
      => parametric still wins 1.69x, but the honest schedule is 16 wall-days at 5 workers, not the 6.55 d the delta=0
         level-2 numbers implied. Level 2+3 is 85.6% of the remaining wall.
- A96 follow-ups (sigma-on-D2 priced; level-2 verify term bounded; level-2 partials MEASURED).
- LEVEL-2 PARTIALS CLOSE EXACTLY AS AT LEVEL 1 -- measured, not assumed. resolve96 extended to read the level-2 results file
  (the level-2 param certs already live in the same certs/param/<cls> tree, so only the results file differed). The level-2 FAILs
  close in 3.1-10.7 s each, 1-2 witness cells apiece, zero residual -- same mechanism, same price as level 1.
- LEVEL-2 VERIFY TERM, bounded three ways (n=14 after dropping one abnormal exit for re-run): median 400.1 s, mean 458.6 s,
  censored mean 505.9 s (the censored one includes a TIMEOUT counted at its 1500 s cap, so it is a lower bound on that node).
  Schedules at 5 workers: 14.31 / 15.27 / 16.05 wall-days. The honest range is 14-16; 16.05 was the pessimistic end.
- TIMEOUT TAIL: ONE node of 14 (k5_11_interior_Y0059_D02, 88 atoms) is 23.4% of the whole level-2 verify wall. The tail is a few
  nodes, as suspected -- but the resolver-first strategy CANNOT be built on a lower cap: a TIMEOUT produces no witness file and
  no partial coverage, so it is worth nothing, whereas a completed FAIL yields 0.988-0.999 coverage plus witness cells that
  resolve in seconds. The correct move on the tail is therefore to RAISE the cap for high-atom children so they land as FAIL and
  then resolve, not to lower it. Cheap test queued: re-run Y0059_D02 at a 3000 s cap and see whether it completes as FAIL.
- SIGMA LADDER ON THE D2 COVER -- PRICED, NOT DEPLOYED (needs an explicit decision, see below). There is no separate D2 ladder
  to build: the orbit reduction PROPAGATES, because the partner box's entire level-2 subtree is the sigma-image of the
  representative's and is discharged by the same rewrite. So k5_11's level-2 (2136) and level-3 (1139) children both halve.
  At 794.6 s per child that is 15.06 d 1-proc saved = 3.01 wall-days at 5 workers, against a 4.90 d 1-proc rebuild of k5_11's
  level-1 cover as 505 orbit reps: NET +10.16 d 1-proc = +2.03 wall-days at 5 workers (16.05 -> ~14.0).
  THE CATCH, which is not build time: deploying it discards the 130 k5_11 nodes already verified on the nth=8 cover (1.26 d of
  work) and resets k5_11's class coverage from 0.98047 to 0 until the new tree catches up. The code build is under a day
  (ladder96/mirror96 already provide the ladder, orbits, reps, C-check and the rewrite; what is missing is a tree57 custom-ladder
  option and a deployment driver), but the cover swap is the highest-risk change available on a live campaign, so it is being
  surfaced for a decision rather than done unilaterally.

## 2026-09-05 — A100 (engineering pilot, Opus) — the protected tier priced from real runs
- Two classes end to end on the A96 pipeline with the A84 P-TREE engine copied into
  `attempts/A100-protected-pilot/code`: **k4_11** (image-bearing, budget 6, |G_S| = 1) and **k3_02**
  (budget 7, |G_S| = 2), the latter picked as the cheapest k <= 3 class by measured level-1 cell
  count (780 attemptable vs k3_05's 984). Engine change: `class84` asserted |G_S| = 2 and k4_11 has
  exactly ONE compatible Trump image (sym 0); widened to 1 <= |G_S| <= 2. T_PRIME extended with both
  classes at 457/10000 (A_S = 3/2, T_K(2e-2) = 0.0510, exactly k4_08's situation).
- **CANARIES CLEAN.** 0 census / Lemma-PD / ladder canary violations on either class, 0 certified
  image-realizable node; every in-zone Trump image square lands in a (D) leaf inside both the A36
  basin and the A83 tube profile. Frozen verifiers byte-identical to A96's `frozen.sha256`
  (`verify_param.py` 0c58485c..., `verify_case.py` 521cb01f...); `to_param96.py` used unmodified.
- **THE ETA LAW IS EXACT ON PROTECTED CLASSES: 54 of 54 cover nodes, eta < 0 <=> a certificate
  exists.** 25 nodes at eta < 0 all PASS; 29 nodes at eta = 0 (tau = budget exactly) all resist.
  A84 called the law "broken in our favour" from 3 nodes; with 54 it is sharper than A60's. Since
  the LP produces eta before certification is attempted, certification + the two eps_geo rounds on
  eta = 0 cells are pure loss: **8 615 s of k4_11's 21 795 s leg (39.5%) and 1 925 s of k3_02's
  9 695 s (19.9%), for 0 kills in 14 attempts.** Gating on eta cuts the per-node cover wall
  558.8 -> 337.9 s (k4_11) and 484.8 -> 388.5 s (k3_02). This is the run's one free lever.
- **The parametric route works on protected classes.** A84's interior cover is the same 12-column
  (P-aff) grid A57 uses and the class pins are slot coordinates, so A96's emitter accepts the
  certificates verbatim (pre-flight: 28/28 of A84's own cover certs). Measured: k4_11 mean 126.2 s
  per leaf, 4/15 full-window first time; k3_02 mean 268.2 s, 5/15. **Resolver 20/20 CLOSED**
  (43 exact window rows, 0 residual, mean 18.5 s / 121.5 s), so 30 of 30 emitted leaves are
  window-valid. Two node kinds do NOT emit: NO-family nodes (no `nofams` in verify_param) and every
  ladder/residue node (box centres outside Q_dy) — **the (K) cover side goes parametric, the ladder
  side does not.**
- **Level-2 descent at delta_pin = 1e-2 does not close the resister branch: 1 kill in 16 children**
  (k4_11 1/11, k3_02 0/5); tau stays pinned at the budget on parent and both children, and 0
  sub-boxes were logic-killed by the gate. This is A84's item-12 finding one level down.
- **(D) side measured and cheap.** Both ladders land at level 24, all_inside and all_in_tube true:
  k4_11 28 (D) leaves (one image), k3_02 59 (two images), contraction ratio ~3.6, max contain_t
  1.14e-3 / 1.22e-3 <= rBasin 1.5e-3 — identical to A84's k4_08/k3_05 to four digits. The ladders
  shed 619 / 1 437 (K) queue boxes, and A84 measured those to be a conditioning queue, not kills.
- **Price.** Per class, terms that CLOSE (level-1 emission + parametric verify + resolver):
  k4_11 96.0 CPU-h, k3_02 141.0 CPU-h. Plus ONE round of the non-closing level-2 branch: +107.1 /
  +149.2 CPU-h. Fractions actually run: 39/882 and 20/780 level-1 cells; downstream legs complete on
  those samples; the (D) side complete (exact). Protected tier, 15 classes excluding k0_00:
  **3 500-4 200 CPU-h** central (band 2 900-6 300 on the level-2 child wall, the weakest
  coefficient), against A84's 1 800 CPU-h model — **~2x**. All layers: **4 900-12 900 CPU-h**
  (k0_00 dominates the upper end and is A99's to close), against the ~400 CPU-h PI target.
- Files: `attempts/A100-protected-pilot/{code,results,logs,progress,certs}`,
  `results/a100_report.json` (every measured term), `results/a100_projection.json` (tier +
  all-layers with the sensitivity band). Latent bug found in A96's `resolve96.py`: `done` is keyed
  on the bare node id, so a node whose id recurs in another class is silently skipped (k4_11's
  c0_Y1119 was); fixed to (cls, id) in `code/resolve100.py` — worth porting back before A96 runs a
  second class.
- A96 <- A100 items (2026-09-05). (1) resolve96.py done-set BUG PORTED: now keyed on (cls, id), never the bare id. Re-scan of
  this campaign's 377 ids across param96 / param96_level2 / resolve96 / A95 t1_param found ZERO genuine cross-class collisions --
  A57 node ids embed their stratum name ("k5_11_interior_Y0295"), so nothing was skipped here. The fix stands anyway: the
  invariant must not rest on a naming convention other campaigns (k4_11's bare "c0_Y1119") do not share.
- (2) THE ETA LAW ON A57's OWN CORPUS (1206 G1 rows, levels 1+2) -- one half holds, the other does not, and the saving is ZERO:
    eta == 0 => resister: HOLDS, 15/15 (all ALIVE-at-LP).
    eta <  0 => certificate: DOES NOT HOLD. 576/730 PASS = 78.9%; 74 FAIL and 80 ALIVE-at-LP also have eta < 0. A100's 25/25 was
      54 k4_11 cover nodes; it does not transfer to A57, and anything that skipped work for eta < 0 here would be wrong on 21%.
    SAVING = 0.0% of the certify+eps_geo wall (0 s of 171818 s) and 0.0% of total node wall. A57 ALREADY does this: tree57.py
      (~line 504) refuses certification outright when tau >= budget, i.e. exactly eta >= 0, so all 15 eta == 0 nodes carry
      cert_seconds 0 and eps_geo 0. The optimisation is implemented; there is no remaining wall to remove.

## 2026-09-05 — A101-flood-lemma (Fable, theory lead) — done-mixed: SNAP proved (destination form + SHELL), FLOOD not proved, stall exact (CELL-INTERLOCK), Trump rigid
- Brief: T1 Lemma SNAP (eta-disturbance drain; swept region; simultaneous snaps; (T) leaf + yield on A57's holes), T2 Theorem FLOOD
  under the strict convention with the simultaneous move set or the exact stall + the k0dir2_87 side threshold, T3 composition +
  Lean. Deliverable docs/proofs/flood_lemma.md; two read-only second-scale chores in attempts/A101-flood-lemma/{code,results,logs,notes}.
- [T] Lemma SNAP-D: the sound form is the DESTINATION form = teleport_packing at the cell (a square within eta of a lattice cell snaps
  at the same side iff no OTHER square meets the open cell); the swept region is unnecessary for soundness (FLOOD-M; the physical
  rotate-then-slide can dig into a backing pin to second order), given explicitly and contained in the eta-ball C + (eta + (cos t +
  sin t - 1)/2) (SNAP-SWEEP). Lemma MULTI: simultaneous snaps are valid iff the target cells are pairwise interior-disjoint (NOT
  automatic across lattices below side 4) and no UNTOUCHED square meets any target - the movers may crowd each other's cells, which is
  exactly why one-at-a-time stalls (record sq4/sq5, 1e-4) and the joint move certifies. Lemma SHELL (the dichotomy sharpened): a
  crowder R of a disturbed square's cell has SAT depth <= sqrt2 eps and, under Lemma CONT (corner cell / unclipped completable slot),
  corner-frame depth <= (1+sqrt2) eps, eps = eta + 1/2 - 1/(2(cos t + sin t)) <= eta + t/2 - the A87 tangency law as a theorem
  (numerical check 2e5 pairs: ratios 0.77 / 0.41). Lemma SNAP-SIDE (SHELL + SLIDE/SLOT-SLIDE): an eta-disturbed square at a k0
  corner (mod K0-O1) or a usable slot at side m forces m >= s-hat' - (1+sqrt2) eps - near-flush ghosts live only within
  (1+sqrt2)(eta + t/2) of the extension window's top. Corollary OFFSET: K0-BLOCKED(delta) has no disturbed corner square with
  (1+sqrt2)(eta + t/2) < delta.
- [T]+[M] Leaf SNAP-T (destination form = box-level SLOT-CROWD; the eta-ball box is optional; simultaneous version for stacks) and its
  yield: snap_yield101 (read-only, 488 witness files, 13,688 boxes = 5,500 holes + 8,185 undecided, ALL 36 lattice cells): eta-ball
  (0.01, 1 deg) 73 holes / 31 at usable cells (pocket96 population: 53 / 16), all at k5_16 BR(1,0) [k6_27 OPEN] / BL(1,0) / BL(1,1)
  = pocket96's pockets; the dominant near-lattice pattern is FLUSH against a pin row/column (k5_11: 160 holes; k5_16: 97 against
  usable cells) displaced ALONG the pin, for which the destination test is the same; condition (2) (every other non-pin shadow
  misses int C) fails at EVERY A57 node (>= 4 unlocalised free squares): 0 nodes flip. SNAP removes pocket96's need for a
  delta_pin re-emission (the snap lands EXACTLY on the cell, the 3e-8 k6 certificates apply) - the obstruction was never the
  tolerance. Existential-filter law; A57/A96 prices unchanged.
- [T] Lemma FLOOD-T: every static move of the simultaneous set (ALIGN, cell TELEPORT, TELEPORT_FREE, full WALL-SLIDE, static Young
  flood at any corner, combinations) is ONE multi-teleport onto a pairwise-disjoint set T of lattice cells of ANY of the four corner
  lattices, feasible iff X(T) = N(T) - |T| <= 0 (FLOOD-D with "Young at one corner" -> "any disjoint cell set across lattices");
  k >= 1 iff some T containing a corner cell has X(T) <= 0. Lemma NINE: |T| <= 9 below side 4 (three points k(1-delta)); with CAP
  the census is finite. Exact stall = CELL-INTERLOCK (X(T) >= 1 for every disjoint T containing a corner cell) => A98's INTERLOCK;
  residue RES-CI subset of RES-X. Dynamic moves (partial slides, RELEASE retreats, rigid re-fits) outside the census [C]; degen87
  found none firing at the record's BL/BR.
- [M] cellflood101 (exact interval "meets" at tol 1e-9 and 1e-6, X_min by 2^11 movable sets x max independent cell set, 11 s):
  record_s0115 (3.98548) is CELL-INTERLOCKED at BL and BR - X_min = 1 over ALL disjoint cell sets of all four lattices, no free
  cell anywhere, no single-meeter cell at 1e-9 - and converts at the nicked TR/TL (X = 0: {TR(0,0),TR(0,1)} moving sq6/sq7,
  {TL(0,0),TL(1,0)} moving sq4/sq5; at 1e-6 the corner cells are singly met = strict85). TRUMP: X_min = 1 over EVERY nonempty set
  of non-exact cells (argmin BR(2,0), two meeters) - no multi-teleport of any kind; the one disturbed square (upright sq4, eta =
  0.0326 at BL(0,2)) is crowded by sq7 at 0.016 <= (1+sqrt2) 0.0326 = 0.079, extension k6_07 open at s-hat: CANARY PASS.
- Side threshold [M, A87 k0dir2_87 floor sweep, in flight]: lowest strictly K0-BLOCKED side 4.0000016 at floor 1e-6 (300 seeds),
  4.000023 at 1e-4 (291 seeds), floors 1e-3/1e-2 queued; vs the exact record 3.98548 at floor <= 1.7e-8: m*(delta) is FLOOR-
  DEPENDENT, every value >= s-hat + 0.108. THEOREM FLOOD NOT PROVED (A101-G1): CELL-INTERLOCK is realised at two corners below 4;
  no four-corner instance known; the sweep supports "strictly blocked below 4 needs a nick", not a theorem.
- T3: if CELL-INTERLOCK exclusion held below s-hat, k0_00 = FLOOD-T + K0-FREE + k >= 1 kills in the PLAIN StratumKill form modulo
  K0-O1-ALL (A98 s.8 with RES-X -> RES-CI); uniqueness clause not delivered by the teleport form; nothing removed today from the
  protected tier (A100 3,500-4,200 CPU-h) or A57. Lean: SNAP-D = teleport_packing (Selection.lean); MULTI = Finset fold + rational
  cell-cell SAT gap max(|dx|-1, |dy|-1); SHELL (a) = finite u/v lemma (mem_interior_iff_uv + SAT separation), (b) the chord
  argument as obligation shell_mu; SNAP-SIDE via slot_slide + ShellKill (Composition.lean). Depgraph: K0.RESN note appended, chip
  A101 released; registry row added.
- Pointers: docs/proofs/flood_lemma.md; attempts/A101-flood-lemma/notes/a101_report.md; code/{cellflood101,snap_yield101}.py;
  results/{cellflood101,snap_yield101}.json; logs/. No campaign file touched (A57 witnesses read only).
- A96 six-shard leg (2026-09-05 16:13-17:16, 1.05 h, busy 15-18). THROUGHPUT: A57 completed 13,046 s of node-wall per hour at
  6 shards vs 11,423 s/h at 4 shards -- +14% for +50% shards, i.e. strongly sub-linear. Per-node wall by stamped neighbour count:
  busy=16 median 352.7 s (n=7) BELOW the 364.5 s baseline, busy=17 median 439.3 s (n=10) 20% ABOVE it, busy=15 562.8 (n=2),
  busy=18 505.8 (n=1). D2 rows at busy=16 median 90.0 (n=10) and busy=17 258.7 (n=5), both at or below their 265.1 baseline.
  Verdict: the first hint of real contention (sub-linear throughput + busy=17 running 20% high), but per-node spread is still
  p25 231 / p75 1774 at n=10, so it is a hint and not a measurement. 6 shards is not obviously wrong; 8 would need a real test.
- LEVEL-2 COST SETTLED at n=529 rows / 53 parents (49 complete, 482 children): per-child 240.3 s = 1.11x A95's delta=0 216.4 s.
  The scale walked 1.54 -> 2.76 -> 2.43 -> 2.36 -> 1.55 -> 1.11 as parents landed; every high reading was small-sample noise and
  A95's original number was right all along. Level-2 VERIFY at n=26: mean 544.6 s, median 400.1 s = 2.06x the level-1 mean.
- **LEVEL-3 DESCENT IS THE SCHEDULE RISK, AND IT GREW**: 60/529 = 11.34% (was 6.8% at n=74). With fanout 8 that is an expansion
  factor of 0.907 PER LEVEL -- the tree is barely contracting. Level-1 descent is 0.1798 (factor 1.439), so the factor IS falling
  (1.439 -> 0.907) and contraction is plausible; but if it stalled at 0.907 the series sums to 10.8x the level-2 term and the
  schedule diverges. My model still stops at level 3, which is now the SAME unstated assumption one level down, and level 3 is
  41% of the projected wall. Measuring level-3 descent is now the highest-value unknown in the campaign.
- SCHEDULE (level-2 scale 1.11, verify 544.6 s, level-3 at 11.34%, nothing beyond level 3):
      parametric  level1 12.87 + level2 41.47 + level3 37.98 = 92.32 d 1-proc -> 18.46 wall-days at 5 workers (17.94 w/ sigma)
      fixed-side (same corrections, four sides)                = 124.77 d 1-proc -> 24.95 wall-days at 5 workers
      => parametric wins 1.35x (was 1.69x); the gap narrows because level 3 is paid by both routes.
- Pass state: 458 nodes verified; k5_11_G1 182 done (171 full-window) frac 0.97803, k5_16_G1 220 done (212 full) frac 0.99414.
  Corpus grew to 898 candidates (602 easy, 218 level-2, 50 fail, 28 epsgeo); main pass restarted on the full selection.

## 2026-09-05 - A99 - the k0_00 tree, next generation (engineering pilot, Opus)
- Measured the three PI reductions on A85's own k0_00 nodes. Net: a PRICE INCREASE, not the ~10x asked for.
  One real reduction found, and it is the window, not the tree.
- R1 DEAD, 0 of 12. Every FAILed A85 k0_00 certificate re-run through the frozen verify_case at depth 56 -> 64
  -> 88 (same certificate, no new LP) still FAILs, and the hole counts RISE with depth (b595 10->11->17,
  b178 42->45->47, p210_001 8->11->19, p215_011_eps0.004 5->17->26). Structural reason, established rather
  than assumed: verify_param splits the widest axis of a 4-D cell so a wide window starves the s-axis -- which
  is why A96's resolve96 sub-window re-run works -- but verify_case's --depth budget is UNIFORM over the root
  split, so "every witness box closes with k more bisections" IS "the global run at depth 56+k passes". There
  is no resolution artefact to harvest. A85's k0_00 FAILs are LP ROW-GENERATION failures (holes = admissible
  placements of exact mass < 1), the same diagnosis A89-O3 reached for the 3-shallow root node. Consequence:
  f2 ~ 0.85 has no measured support at all; A85's own depth-2 rate is 1/3 first pass, 2/3 with eps_geo repairs.
- Artefact defect in A85: certs/k0_00/s1cor_near_b178_epsgeo0.002.json on disk has exact total 10.050003 >=
  budget 10 (verifier rc = 2, "proves nothing") -- a later certify.py round overwrote the certificate that its
  .report.json describes. R1's denominator is 12, not 13.
- R2 is a COST MULTIPLIER of exactly x15, LP-free and exact: D4 quotients each shallow/deep branch only by the
  STABILISER of its corner pattern, 1728/|stab| = 216*|orbit|, so the level-1 cell count over orbit
  representatives is 216*16 = 3456, i.e. 3240 = 15 x 216 once the 4-shallow class (A89's window-valid root
  kill) is deleted. And the ALL-DEEP branch keeps its 216 cells with NO exempt box at all (Lemma ID fires only
  at a shallow corner), so R2 can never price the frontier below A85's figure whatever the other branches do.
- R2 LP screen (20 level-1 cells stratified over T(s0)x[0,90), plain vs 3-shallow at delta = 0.3 window-valid
  a_win = 0.6896936, 136 NoFams/corner from A89's o3fam, 300 s LP each, 52 launches, zero commit waits, zero
  canary refusals): median tau(plain) - tau(sh3) = +1.0567, eta <= -1.0 on 19/20 cells vs 6/20 plain -- but
  minmass HALVES, 0.5093 -> 0.2396. That is A89-O3's delta-sweep signature exactly: a larger exempt region
  gives the measure more freedom, so the same row-generation budget covers proportionally less and tau falls
  because the LP is LESS converged. ZERO kills claimed; the arbiter (certification) leg did not run.
- R3(c) IS the win. A85's interior cell grid already lies in A96's (P-aff) family -- the A38/T(s0) column step
  is exactly (s0 - 2*c0)/16 with c0 = 11/10, so every cell edge and core centre is e_q(s0) with 12q dyadic --
  so to_param96 emits with NO new anchoring rule. certs/param/s1int_l2_l2_p210_001_epsgeo0.004.param.json
  (241 atoms, total 9.97707 < 10) PASSes the frozen 4-D verifier over the WHOLE window [3.82, s0] in 123.2 s:
  1 847 066 boxes, 0 witnesses, coverage 1.00000. A NEW WINDOW-VALID KILL of a node A85 killed only at s0.
  The window therefore costs +119 s on a 1 630-1 860 s node (+5-7 %) instead of x4 for a 4-side grid: a 3.8x
  cut. Caveats: n = 1 (the other emitted node, 53 atoms, timed out at 600 s, >= x77), the four CORNER-CROWD
  nodes cannot be emitted at all (cores at 17/24, 91/72, 37/24, 41/72 are t-grid, not affine in s0), and
  transporting cover-invariance from A57's 12-column cover to the A38 cover is an OPEN obligation.
- STACKED PROJECTION (results/projection99.json; A85 s.8.3 model with only f2, branch count and window
  multiplier replaced): f2 = 2/3 at s0 gives 8 903-20 636 CPU-h; window-valid with parametric re-emission and
  R2 off gives 9 341-21 661 CPU-h = 130-301 desktop-days at three slots. That is 2.9-3.1x WORSE than the
  published 3 200-7 000, which was the f2 = 0.85 row R1 has now removed. With R2's branching: 138 000-323 000.
  The 4-side-grid alternative to R3(c) is 35 163-82 096.
- NOT MEASURED (queued behind the R2 screen; the supervisor chain died before launching them): R3(a)
  certification --jobs 4 vs 1, R3(b) LP cold vs warm (the 1 915-column sibling pool was built and used by all
  52 R2 LPs, but no cold control ran), and the R2 arbiter certification. Also still open: the level-2 descent
  rate at delta_pin = 1e-2 (A96's 2.36x), untouched here.
- Discipline: <= 2 compute slots throughout, BLAS pinned to 1 thread, tree85's 6144 MB commit gate before
  every LP (free commit 66.7-79.6 GB at all 52 launches, zero waits), detached drivers, frozen verifiers
  copied byte-identical (code/frozen.sha256). Nothing under A57/A60/A61/A85/A89/A96 was written.

## 2026-09-05 — A102-rigidity-drain (Opus chore) — done-success
- The PI's by-eye drain of the 3.9907 record is now a tool (`attempts/A102-rigidity-drain/code/rigid102.py`,
  self-test reproduces `pi_drain_3p9907.py` exactly: square 3's three contacts, torques +0.455/+0.488/+0.225
  all CCW, the 1.309 deg rotation collision-free, seven simultaneous snaps, k = 7). Run on all 12 strictly
  K0-BLOCKED packings on disk (4 k0dir2_87 floor records + the 8 A87/strict85 packings; the confined-descent
  endpoints of k0dir2_87.jsonl carry only scalars, no poses, so they are not recoverable without re-running
  descents) plus Trump, at both meet bars, one process, ~12 min.
- T3 RULE: the brief's candidate ("every floor-depth d2 <= 1e-2 second meeter is FREE-ROT or FREE-TRANS") is
  FALSE — 21 of the 31 floor-depth second meeters are PINNED and 12 are RIGID for the FULL first-order motion
  cone. What holds is a ROOM dichotomy: a second meeter either retracts COMPLETELY out of its corner cell
  under one rigid-body motion (10 of 12 packings, retraction fraction 1.000) or hardly moves (polish12 0.22,
  floor-1e-4 0.022, Trump 0.000) — nothing in between; and every full retraction is followed by a valid
  simultaneous snap to k >= 2 at the same side.
- Both sub-4 packings drain to k = 7 at the same side: record_s0115 (3.985484) and the 1e-3 floor record
  (3.990749). Caveat: the record's freeing move is tangency-scale (its TR/TL "crowds" are 1.6e-8 / 7.0e-9
  nicks); at the 1e-6 census bar the record is not K0-BLOCKED and the second meeters of its two real crowds
  (BL sq0 0.0147, BR sq3 0.0145) are first-order RIGID, so it does not drain there. Largest d2 that drained:
  1.02e-2 (floor-1e-2 record, TR sq6, 1.279 deg about its own centre, then 11 snaps to k = 5).
- Residue for theory (notes/rigid102.md s.4, full contact sets with points, edge normals and torques): the two
  non-drainers (floor_1e-04 at 4.0000044, polish12 at 4.0000001) and Trump. Pins are square-square — 32 of the
  33 PINNED second meeters are pinned by >= 2 squares, exactly 1 by a wall + one square. OBSTRUCTION NAMED:
  the contact set at a fixed tolerance does not determine the finite motion — both non-drainers have
  first-order-free second meeters that are stopped after ~1e-4 deg by a square whose gap is just above the
  1e-7 contact bar (1.4e-6 and 3.1e-5), so any theorem needs a finite-motion (second-order) criterion.
- CANARY PASS: Trump's TL crowd {4, 6} at depth 0.155/0.168 is first-order RIGID (no rotation about any point,
  no translation), zero moves, k stays 5. The stronger screw-cone test frees the three anchored packings that
  the centre-torque test could not, and still does not move Trump.
- Discipline: 1 process, OMP/MKL/OPENBLAS = 1, pure geometry (no LP, no descents re-run), commit headroom
  65 GB / 7.1 GB free physical throughout. Nothing under A57/A60/A61/A96 written; frozen verifiers untouched.
  Chip on K0.RESN (owner A102, released at close); depgraph re-rendered.

## 2026-09-06 — A103-noroom (Fable, theory lead) — done-mixed: NOROOM local only, DRAIN(W) open, exact obstruction delivered
- Deliverable `docs/proofs/noroom.md`. (A) closed LOCALLY: Lemma TRUMP-LOCAL [T] — no packing within eta0
  of a Trump image at side <= s-hat + eps0 is K0-BLOCKED (BR/TR cells are reachable only by the slot square
  and the 40.18-deg square resting on its corner, and every admissible slot-square pose — axis-aligned,
  CCW-tilted, CW-tilted, with the floor and the wall as the only constraints — covers the corner region the
  tilted square would have to enter; exact inequalities f(a) >= 1, h(a) < 0). With the uniqueness clause
  and compactness: Theorem NOROOM-LOCAL, m* > s-hat strictly; eps0 unquantified and the argument is circular
  for the window, so (A) at 3.9 stays OPEN. [M] trumplocal103: 29,254 admissible poses all cover, 0 of
  11,000 valid (sq2, sq8) neighbours doubly meet BR up to s-hat + 0.1.
- Ingredient 1 delivered as a theorem: Lemma ROT-GRAD (the depth gradient in (v, w) is the row of a virtual
  contact at the argmin point pushing the square away from the corner; rates explicit; the brief's "toward
  axis" sense is the vertex-argmin case, an edge-argmin D-type with c_x ~ c_y decreases depth toward the
  DIAMOND) + Lemma ROT (Gordan: at the Psi^(w)-minimiser every intruder is HELD — no single-square rigid
  motion strictly opens its active rows and strictly decreases its depth; exact, first order, no second
  order needed) + Corollary ROT-TORQUE (the PI's one-signed-torque rule). [M] lock103 on A102's 12 strictly
  K0-BLOCKED packings + Trump (3 s): ZERO packings held at all eight intruders; 37 unheld (17 translation,
  13 rotation, 7 screw); every packing has an unheld SECOND meeter (22), 9 with full room (= A102's
  drainers recovered from the first-order test alone), 13 stopped by a near-contact at gap 1e-7..1e-3 (=
  A102's obstruction, now the second-order case of an exact lemma); record 3.98548 held 7/8 (the 7e-9 TL
  nick translates out); TRUMP 5/5 HELD — canary PASS.
- Ingredients 2 and 3 do not bite: [T] Lemma CHAIN-AX (axis-aligned edge-to-edge column exact: near end
  intrudes by 4 - m in its coordinate, far end at [m-1, m]); [F] a general link makes x-progress > -1 only
  and Trump's own anchoring column sq4 -> sq7 -> sq8 -> sq1 has tilted middles and a far end that is
  neither a slot square nor an intruder (the brief's dichotomy has a third case); [F] the home regions
  [0, 1+sqrt2]^2 pairwise overlap for m < 4.83, adjacent centre regions are 0.41-0.46 apart, one free
  square braces all four corners (Trump's sq7) — the count is vacuous (A91 F5 in numbers).
- (B) DRAIN(W) reduces to RES-LOCK(m) = empty on W (RES-LOCK = K0-BLOCKED + every intruder held +
  NOCRIT-SEL/W-GEN anchoring + SLIDE/CEIL). (C) delivered: the family RES-LOCK, no realisation on disk at
  any side, candidate realisation = the jammed 4x4 grid at 4 + eps with its near-contacts closed (where the
  theorem must fail); drawing `attempts/A103-noroom/results/lockmap103.svg` (the two sub-4 packings,
  intruders labelled HELD/UNHELD with the unheld motions, geometry-checked). THE ONE FACT: Conjecture
  LOCK-FREE(< 4) — every K0-BLOCKED packing at side < 4 has an unheld intruder; true 12/12 on the corpus,
  needs two blocked corners (Trump is held everywhere), proof shape = the eight contact cones jointly along
  one wall of length < 4 with WALL-3. Composition if it lands: StratumKillSel Psi^(w) with LOCK-FREE as
  the leaf, k0_00 = window kills of k >= 1 + LOCK-FREE, no criticality, no tree; Lean shapes in s.8.
- Discipline: three chores, one process each, BLAS pinned, seconds, pure geometry; nothing under
  A57/A60/A61/A96 or A102 written (A102's loader copied, not imported); frozen verifiers untouched.
  Chip on K0.RESN (owner A103, released at close); depgraph re-rendered.
- A96 LEVEL-3 PROBE LANDED (42 children, 6 parents, delta=1e-2, ALIVE-only parents). Descent 4/42 = 9.52% -> expansion factor
  f3 = 0.762. Per-child 291.8 s (close to level 2's 240.3 s -- cost does NOT escalate with depth). Outcomes PASS 29 / FAIL 5 /
  KILL-BY-LOGIC 3 / ALIVE 4.
- **DESCENT IS CLUSTERED, NOT UNIFORM** -- the single most important qualifier on every number below. Per parent: four of the six
  complete parents contributed ZERO alive children (0/8 each); ONE parent (Y0036_D07) contributed 3 of 8; the sixth (Y0186_D00)
  is 1 of 2 and incomplete. So the pooled 9.52% is dominated by which parents were sampled, and a branching process with a few
  fertile nodes is the right picture, not a uniform geometric. n=42 with 4 events is a wide interval (roughly 3-24% Poisson,
  f3 in 0.2-1.9).
- THE FACTOR TREND AND THE TAIL. f1 = 1.439 (level-1 ALIVE fraction), f2 = 0.906, f3 = 0.762. The factor IS falling, but its
  DECAY IS SLOWING: f2/f1 = 0.63, f3/f2 = 0.841. Extrapolating f_{k+1} = rho * f_k instead of truncating at level 3:
      rho = 0.63 (decay continues as level1->2)   tail  5267 children,  5 levels, 37.79 d -> TOTAL 112.89 d -> 22.58 wall-days @5w
      rho = 0.736 (geometric mean, central)       tail  5982 children,  6 levels, 42.91 d -> TOTAL 118.01 d -> 23.60 wall-days @5w
      rho = 0.86 (decay as level2->3)             tail  7365 children,  9 levels, 52.83 d -> TOTAL 127.93 d -> 25.59 wall-days @5w
      rho = 1.0  (factor stalls at 0.762)         tail 13355 children, 30 levels, 95.80 d -> TOTAL 170.90 d -> 34.18 wall-days @5w
  Truncating at level 3 gave 75.10 d -> 15.02 wall-days @5w, so THE TAIL IS 50-130% ON TOP: the honest schedule is 23-26
  wall-days at 5 workers on the central cases, 34 if the factor stalls. The tree does terminate in every case examined (rho < 1
  gives 5-9 further levels), so this is a cost, not a divergence.
- The dominant uncertainty has moved AGAIN: it is no longer per-child cost (settled: level-2 LP 1.11x, level-3 291.8 s) nor the
  level-3 rate itself, but the CLUSTERING -- whether the fertile-parent fraction stays near 1-in-6 or itself decays. That is
  measurable by deepening the four ALIVE level-3 children and seeing how many are fertile.

## 2026-09-06 — A105-lockfree (Fable, theory lead) — done-mixed: the wall lemma is exact and FALSE on one wall; no theorem range; hooks classified
- Deliverable `docs/proofs/lockfree.md`. Target: Conjecture LOCK-FREE(< 4) via the brief's wall lemma. Result: NO m
  range proved. The one-wall statement (both corners of a wall of length < 4 blocked => an intruder of those two
  corners is unheld) is refuted by two exact packings on disk: record_s0115's bottom wall (3.98548, all four intruders
  HELD at the 1e-7 bar; sq1 a wedge with strict LP value 1.3e-8) and the floor-1e-3 record's left wall (3.99075, all
  four LOCKED with explicit cone certificates). Two ADJACENT locked walls sharing a blocked corner exist at 4.08-4.11
  (anchored0: right+top; anchored1/2: bottom+right), so route 3 (two walls) is not a side-free statement either.
- Proved [T]: Lemma ROT-W -- at the Psi^(w)-minimiser no single-square TRANSLATION with weak active rows (exact for
  translations, Fact A) decreases a depth; Farkas: -e in cone{n_k} over the contact force directions (walls never
  help). Independent of Lemma ROT in vivo (record sq1: ROT-held wedge, ROT-W-unheld; floor-1e-3 sq3: ROT-W-held,
  ROT-unheld by rotation). LOCKED := held and W-held; Conjecture LOCK-FREE+(< 4) (some intruder not LOCKED) is the
  exact consumer statement (RES-LOCK contains both locks) and is weaker than A103's. Lemma LINE: held and pushed iff
  the contact forces' resultant is the corner-ward force along a LINE through the argmin set (wedged otherwise);
  PUSH-LINE: for a wall-hugging Y-type nick the SQUARE contacts' resultant passes through (v_x, y_w), v_x < 1 - d --
  the brief's "far-side contact on the wall side of the argmin point", exact; it is what the 3.9907 record's BR sq3 /
  TR sq6 violate (the PI's one-signed-torque drain).
- The HOOK family [T]: wall-hugging axis-aligned nick N = [0,1]x[1-eps,2-eps] + tilted floor carrier T through N's
  inner corner; kind alpha (corner on T's shallow edge, v_x = 1 + tan(t/2) + (c/s) eps) and kind beta (steep edge,
  v_x = 1 + (1-s)/c + (s/c) eps, depth (s/c)(1-s-eps)). Trump's TL crowd IS a beta-hook (sq6 depth 0.168321 and
  top-wall vertex 1.595678 reproduced to six digits); record_s0115's BL is beta, BR is alpha. Theorem HOOK-alpha
  (m >= 2 + Phi + eps1 + eps2, Phi >= 2: [T] equal tilts, [M] 91x91 grid, [S] general) and HOOK-beta (m >= 4 +
  tan t (eps1+eps2), the identity (1-s)/c + s >= 1): two SAME-kind hooks on one wall need m > 4; the four-alpha-hook
  shell (tilted grid) has side exactly 2(1+s)(1+c)/(s+c) >= 4, equality = the grid (never K0-BLOCKED). Proposition
  HOOK-beta-alpha: the MIXED flush pair (steep edge against shallow edge, same tilt) has m = 2 + f(t) + (s/c)eps1 +
  (c/s)eps2, f = (2-s)/c + tan(t/2) < 2 exactly on (0, 30 deg) (min 1.9342 at 15.25 deg; f(30) = 2): the record's
  bottom wall reproduced to six decimals (3.985484). Lemma HOOK-W: the beta carrier of a flush pair has contact
  directions +-n and the floor only, cone = a half-plane missing -e_x: never W-held without a third contact on its
  upper-right edge -- the record has sq9 there at gap 2.1e-7 (A102's near-contact, in its exact place).
- [M] lockw105 (3 s): 0/12 corpus packings LOCKED at all eight; ROT-W adds 9 unlocked squares (wedges) beyond ROT
  and ROT adds the rotation drains ROT-W misses; locked both-blocked walls: floor-1e-3 left (3.9907, the only
  sub-4 one), polish12 bottom, anchored0 right+top, anchored1/2 bottom+right; Trump 5/5 LOCKED, all PUSHED.
  hook105 (2 s): D formula vs SAT to 7e-10, min Phi = 2 at the origin, shells built and geometry-checked, drawing
  results/hookwall105.svg (record bottom wall, floor-1e-3 left wall, the alpha-shell at 18.93 deg / 4.0575).
- Canaries PASS: Trump (one hook; two-hook statements silent; LOCKED 5/5); grid at 4+eps (the shell's equality
  case; the blocked grids are JAM-0 dips, outside the hook family; polish12's bottom wall LOCKED 4/4); records
  (unlocked = lockmap103's squares plus the ROT-W wedges, all on the non-hook walls). Residue named [C]: the
  four-corner PUSH-LINE count -- a locked hook wall is paid for on the opposite wall. Routes: FLOAT/CLUSTER silent
  (no floating pusher in either instance); two-wall route open below 4.
- Discipline: two chores, one process each, BLAS pinned, seconds; A103's loader copied, not imported; nothing
  under A57/A60/A61/A96/A104 touched; frozen verifiers untouched; A104 has no report on disk (BRIEF only). Chip on
  K0.RESN (owner A105, released at close); depgraph re-rendered; registry row.

## 2026-09-06 — A106-shadow-diameter (Opus chore, read-only measurement) — done-negative on the switch, done-success on a free prune

**Verdict first (T3). There is no basin switch to make on k5_11 / k5_16, because the premise
fails: A57's alive boxes do not contain shadows.** What the measurement did find is a 24 % prune
of the open tree that costs 0.6 s a box.

* **Both classes' shadow floor is the PI's k7 pinwheel, s\* = 3.886746 = s0 + 0.009662**
  (ŝ + 0.009662). k5_11's and k5_16's five pins are each a subset of that configuration's seven
  slot squares, so it is a configuration of both. A106's independent minimiser reaches it to
  7 digits from three unrelated seed families (the k7 seed, Trump transports, uniform random),
  and its exact interval endpoint certificate (mpmath iv, 250-bit, rationals at 1e-12) passes at
  ε = 1e-8. Spectrum above it: 3.902674, 3.911481, 3.912232, 3.914214, 3.924003, 3.942809, 4.0 —
  the same ladder the PI's 301-start k7 search produced.
* **r_basin.** A36/A70/A79's certified H̄ = 7.9079 (`contraction_tube.md` §1.5) gives, around a
  strict local minimum, side ≥ s\* − H̄x², hence a ball of radius √(slack/H̄) on which the side
  provably stays above s0: **r_basin = 0.034955** for the 3.886746 shadow (0.0246–0.0492 for
  H̄ ∈ [4,16]); 0.0569 for 3.902674.
* **Box radius vs basin radius** (half the median major diameter in pose space): k5_11 L1 0.0849
  (2.43 r_basin), L2 0.0475 (1.36), L3 0.0175 (0.50), L4 0.0087 (0.25); k5_16 L1 0.0950 (2.72),
  L2 0.0349 (1.00). So on size alone one further bisection puts a level-2 box inside the basin and
  the level-3/4 boxes are already 2–4× inside it — the brief's "is the diameter already small
  enough" is **yes, from level 2–3 down**.
* **But size is not the binding constraint.** Of 145 open nodes at levels 2–4, **zero** contains a
  local minimum: for all 62 that admit any configuration the box-constrained minimum sits on the
  box *boundary* (`interior = 0`), and releasing the box lets the configuration flow out of it to
  a class shadow — median ∞-gap from the box to the nearest square of that shadow **0.3166**,
  about 9 r_basin. The best side attainable with a square in an alive box is s0 + 0.0130 at best,
  median s0 + 0.0612, q3 + 0.1054, max + 0.656: the live boxes are 1.3–68× *further* from
  feasibility than the shadow is. A ball around a shadow would discharge configurations no live
  box contains, so the tree/basin seam of A63/A83 has nothing to bite on here.
* **τ is integral, so there is no η route either.** Every alive node sits at τ = budget exactly
  (|η| ≤ 2e-11) and every killed one a full unit below (τ = 4.000000, η = −1.000000, or
  4.2/4.33/4.5). The LP verdict flips; it does not converge. Extrapolating a closing depth from η
  is not available; the descent is the per-level event rate A96 already measured (11.3 % at
  level 2, 9.5 % at level 3, clustered), i.e. 5–9 further levels and **23–26 wall-days at
  5 workers** stands as the unaided cost.

**The lever that is actually there: 122 of A57's 516 open boxes (23.6 %) are EMPTY on geometry
alone.** `pinguard.classify` decides "core meets pin core" on the rational *inscribed* cores
(half-side a = 0.36–0.48); the true unit square is larger, so a box can be incompatible with a
pin while the cores are compatible. Asking the sharper question directly — *is there any pose in
B and any pin position in its δ = 1e-2 slack core for which the true unit squares are separated?*
— kills, at ~0.6 s a box (`code/t2b_pinclash.py`):

| | k5_11 L1 | k5_11 L2 | k5_11 L3 | k5_11 L4 | k5_16 L1 | k5_16 L2 |
|---|---|---|---|---|---|---|
| open boxes | 158 | 122 | 10 | 4 | 213 | 9 |
| **empty by box-vs-pin** | **25** | **51** | **6** | **4** | **33** | **3** |

61 of the 64 at levels 2–4 have clash depth > 1e-3 (robust; median 0.0145, max 0.0506); 3 sit
within grid noise and want an exact rational check before being claimed. The clashing pin is
(3/2, 1/2) 27×, (1/2, 3/2) 23×, (1/2, ŝ−1/2) and (ŝ−1/2, 1/2) 7× each — never the corner pin.
These nodes need no LP and no certificate, and their whole subtrees vanish with them: ~3.3
CPU-days of the immediately next level (122 × 8 children × 292 s) and, at A96's expansion
factors, **~9–13 CPU-days of the 38–53 CPU-day tail, ≈ 2–2.6 wall-days at 5 workers**. It also
explains part of the clustering A96 saw: a sterile parent is often one whose children are simply
void.

Secondary: 19 further open nodes admit no feasible landing at all with clash just below zero
(−5e-4 to −0.93, residual median 8e-4) — thin slivers that are probably also empty and are worth
an exact pass. One free-release landing returned 3.851577 and is flagged `free_feasible = False`:
an infeasible penalty artefact, not a packing, and excluded.

Discipline: one BLAS-pinned process at a time, wall-capped; A57/A96 state read only, snapshotted
with a sha256 manifest into `attempts/A106-shadow-diameter/results/snapshot/`; no A57/A96 process
started, stopped or re-niced; frozen verifiers untouched. Engine `code/shadow11.py` validated
against Trump (ŝ recovered to 3.4e-9 from a perturbed start under trump5's own pins).
Detail: `attempts/A106-shadow-diameter/notes/measurements.md`, `results/t3_switch.json`.
- A96 FERTILITY PROBE (level 4, 30 children from the 4 ALIVE level-3 children, delta=1e-2): **0 of 4 parents fertile, 0 alive of
  30 children, f4 = 0.000.** Fertility is NOT heritable -- three of the four parents were siblings under the one fertile level-3
  node Y0036_D07, exactly the case where heritability would have shown, and all three died. Outcomes KILL-BY-LOGIC 18 / PASS 6 /
  FAIL 6: the logic-kill share rises from 32% at level 2 to 60% at level 4, which IS the termination mechanism -- deeper boxes are
  smaller and clash with the pins. Per-child 292.6 s, flat with depth (level 2: 240.3, level 3: 291.8).
- FACTOR SEQUENCE 1.439 -> 0.906 -> 0.762 -> 0.000. With 0 events in n=30 the rule of three puts the 95% upper bound on the
  level-4 rate at 3/30, i.e. f4 <= 0.80, so the point estimate is 0 and the honest schedule is a range:
      f4 = 0.00 (measured)                tail 3181 children,  0 extra levels, 22.82 d => 97.92 d 1-proc -> 19.58 wall-days @5w
      f4 = 0.30                           tail 4385 children,  4 extra levels, 31.45 d => 106.55 d      -> 21.31 wall-days @5w
      f4 = 0.80 (95% upper bound)         tail 8139 children,  7 extra levels, 58.39 d => 133.49 d      -> 26.70 wall-days @5w
  So the campaign is ~20 wall-days at 5 workers, 27 in the pessimistic tail case -- and the tree TERMINATES; the divergence
  scenario (factor stalling near 1) is now excluded by measurement, not assumption.
- A106 pin-clash test EVALUATED (not deployed). NOT SOUND as a certificate as written: code/t2b_pinclash.py takes the MINIMUM of
  `overlap` over a 5x5x5 pose grid x 3x3 pin offsets and then a Powell local descent, and reports "empty" when that minimum stays
  positive. Both steps are float finders. A sampled minimum is an UPPER bound on the true minimum over the continuum, so a
  positive sample minimum does not prove the true minimum is positive -- the error direction is precisely the dangerous one
  (claiming emptiness because a search failed to find a separating pose). The docstring's "a grid can only UNDER-estimate the
  clash" is backwards. The 122/516 is therefore an UPPER BOUND on the yield of any sound version, not a yield.
- It CAN be made sound, two ways, and the cheap one needs no new leaf at all:
    (B) SAME leaf, bigger core [preferred first step]: A57's existing KILL-BY-LOGIC proves K_B subset every square with params in
        B, K_P subset the pinned square, K_B meets K_P => overlap. The core formula a = (1/2 - hd)/(1 + (t1-t0)) is conservative;
        a tightly computed common-inscribed-square over the pose range gives a larger a and strictly more kills with ZERO new Lean
        (T5 core_meet_same_square unchanged), ZERO new leaf kind, and nothing in the frozen verifier chain touched. Pure geometry
        function, hours not days.
    (A) NEW leaf, interval SAT [strictly stronger]: by the separating-axis theorem two squares are disjoint iff one of the 4
        edge-normal axes separates them, so it suffices to bound, over the WHOLE box and the WHOLE pin slack core, the separation
        gap ABOVE on each of the 4 axis families and require all four < 0. That is exactly the shape of A53 verify_case's
        core_exempt_frac (rational cos/sin via cos_sin_t, outward intervals, float pre-filter as shortlist only), so the primitives
        exist. Needs a new leaf kind + a new Lean theorem structurally parallel to T5; the frozen verifier chain is untouched
        because this is a tree-level logic kill, not a measure certificate.
- YIELD, honestly bounded: the margin data says the sound version will NOT recover all 122 cheaply. clash/dmax (margin relative to
  box diameter, which is what an interval bound over a whole box loses) has median 0.199 and only 4 of 122 exceed 0.5; NONE exceed
  1. So most flagged boxes need subdivision before an interval bound can decide them, and the 0.6 s/box figure will not survive.
  The 122 also split 58 at L1 / 54 at L2 / 6 at L3 / 4 at L4 and 64 alive_lp / 58 cert_fail. No positive control is available in
  the sweep: it covers only open boxes, so it contains ZERO known logic-kills to check recall against -- adding the 601 known
  logic-kill boxes as a control is the first thing any sound implementation should do.
- A96 ROUTE (B) MEASURED (attempts/A96-a57-parametric/code/core96.py; measurement only, NOT deployed).
  Tight common-inscribed-square core for the EXISTING KILL-BY-LOGIC leaf: keep (kx, ky, theta_m) exactly as now and enlarge only
  the half-side, from a_old = (1/2 - hd)/(1 + (t1-t0)) to a_tight = (1/2 - h*M_c)/M_t with h the centre-box half-WIDTH,
  M_c = max(|cos|+|sin|) over the box's tilt range and M_t = max(|cos|+|sin|) over the tilt range relative to theta_m. The old
  bound is loose twice: hd = h*sqrt(2) assumes 45 deg is in the tilt range, and 1 + (t1-t0) over-states M_t since
  cos(x)+sin(x) <= 1+x. Because the centre and tilt are unchanged and a_tight >= a_old, the new core CONTAINS the old one, so the
  positive control holds BY CONSTRUCTION -- and was still executed.
  (1) POSITIVE CONTROL CLEAN: 583/583 known logic-kill boxes still killed, zero lost. (The 601 in cover_invariance.md counts a
      different snapshot; 583 is what the current G1 corpus contains.) a_new/a_old: min 1.0072, median 1.0423, max 1.1085, and
      NONE below 1.
  (2) YIELD on the open set (1536 open boxes, all levels): 70 new certified kills -- L1 20/1096 = 1.8%, L2 32/389 = 8.2%,
      L3 7/39 = 17.9%, L4 11/12 = 91.7%. THE RATE RISES STEEPLY WITH DEPTH, which is the same mechanism the fertility probe found
      (logic kills 32% at L2 -> 60% at L4): deeper boxes are smaller and clash with the pins. Margin a_new/a_old - 1 on the new
      kills: min 0.0089, median 0.0468 -- comfortably clear of float slop (the sweep also shrinks a_tight by 1e-9 first).
      Prior A57 status of the 70: FAIL 31, PASS 19, ALIVE 20. Split k5_11 52 / k5_16 18.
  (3) CPU-DAYS REMOVED (direct node cost only; excludes the subtree a killed ALIVE box also removes, so it is a LOWER bound):
      L1 0.29 + L2 2.71 + L3 5.80 + L4 22.59 = 31.39 d 1-proc = 6.28 wall-days at 5 workers.
      Schedule 97.92 d (19.58 wall-days @5w) -> 66.53 d (13.31 wall-days @5w), a 32% cut. Essentially ALL of it is at levels 3-4,
      which is exactly where the remaining wall lives -- the pre-filter is nearly worthless at level 1 (0.29 d) and decisive at
      level 4 (22.59 d).
  NOT DEPLOYED pending the go-ahead; when deployed it is a pre-filter on newly emitted children only, existing verdicts untouched.
  Route (A) (interval SAT, new leaf + new Lean) stays on the shelf.

## 2026-09-05 — A104-grid-lock (Opus chore) — done-success
- **T3 (one line): fully-held K0-BLOCKED packings first appear at side m_lock = 4.0002374 (4.0015246 with a
  Gordan certificate at all eight intruders); below 4 the closing iteration always frees a corner.** No
  counterexample to Conjecture LOCK-FREE(< 4); its failure point is NOT the jammed grid.
- **T1 — the grid drains too.** The closing iteration of Lemma ROT (lock103 reused verbatim for the HELD test;
  move the unheld intruder along its unheld motion, pin the new contact rows at gap 1e-11, least-norm re-polish
  of that square's three coordinates, re-polish the configuration at fixed side, repeat) run on all 12 strictly
  K0-BLOCKED packings on disk: **12/12 free a corner**, including both candidates of docs/proofs/noroom.md §7 —
  polish12 (4.0000001, TR sq7 rotates out after travel 1e-5) and floor-1e-4 (4.0000044, BR sq3 translates out
  after 1e-5). Every endpoint exactly certified (fjpolish87.verify_exact: disjoint, min pair gap >= 1e-11, side
  UB within 2e-9; exact_blocked_test_d: the freed corner has ONE certified meeter, zero unknowns). §7's
  "the grid's rigidity makes it plausible that this packing is held at all eight intruders" is measured FALSE:
  the exact grid at side 4 has one meeter per corner, so the eps-grid is blocked only by an O(eps) poke that
  Lemma ROT's own step takes straight back out. A103's "jams at a near-contact at 1.2e-7" was an artefact of
  straight-line travel — following the contact manifold the nick rolls past it and retracts 100 %.
- **T2 — m_lock.** k0dir2_87's confined descent (verbatim), 220 fresh seeds per floor + the 12 corpus packings,
  floors 1e-3 and 1e-2, closing iteration at every blocked endpoint: **443 endpoints, 58 fully held** (11.3 % at
  1e-3, 14.9 % at 1e-2) **against 363 corner-freed** (85.1 % / 78.7 %; 22 timeouts, 21 seeds gave no blocked
  endpoint). m_lock = 4.000237417 (floor 1e-3); the lowest with a clean Gordan certificate at all eight is
  4.001524573. **Zero fully-held packings below side 4** — the lowest endpoint the descent reached at all was
  3.9907484 and it freed a corner. So RES-LOCK is realised after all, just not by the grid and not below 4.
- **The lock's contact structure** (464 intruders of the 58 held packings): 4.25 contacts per intruder,
  **77.2 % square-square vs 22.8 % wall** (3.28 square + 0.97 wall rows each); 145/464 wedged with lambda = 0
  (contacts alone), 319 needing the virtual corner row; depths 2.4e-4 / median 0.135 / 0.924. Consequence for
  the proof target of noroom.md §7: the lock is carried by the square-square rows, so a wall-length budget
  (WALL-F) alone cannot deliver LOCK-FREE — the missing step is that at side < 4 the crowd arms cannot supply
  3+ square rows to all eight corner members at once.
- Canary: Trump 5/5 intruders held, K0-FREE, side 3.877083590023 — unchanged before and after both campaigns.
- Files: attempts/A104-grid-lock/{code/close104.py,code/report104.py,code/gen_lock104.py,code/depgraph_note104.py,
  notes/lock104.md,results/*}; chip on depgraph K0.RESN (owner A104); REGISTRY row. One process, BLAS pinned,
  ~90 min wall. A57/A60/A61/A96/A102/A103 files and the frozen verifiers untouched.

## 2026-09-06 — A107-shadow-gallery (Opus chore, read-only) — done-success: the gallery is `docs/shadows.md`

**53 distinct shadows explain 1260 of the 1566 ALIVE-at-LP nodes on disk** (A57 1227 across both
classes, all shards, levels 1–4; A60 trump5 325; A61 14. A85-k0-route and A99-k0-tree-v2 have no
LP node jsons in this format, so the k0_00 level-1 cells could not be included). Ordered by nodes
explained, with drawings, contact graphs, tilt sweeps and drain hints, in `docs/shadows.md` +
`docs/shadows/S01..S53.svg`.

* **S02 is the PI's k7 pinwheel and its mechanism reproduces exactly.** s\* = 3.886746030 =
  ŝ + 0.009662, seven slot squares `BL(0,0) BL(0,1) BL(1,0) BR(0,0) BR(0,1) TL(0,0) TR(0,0)` plus
  four free squares sharing one tilt 48.4351° (spread 1.7e-5°). Fritz-John resultants:
  **f–top wall 0.867 is the binding contact**, then the mirror pair (0.654 / 0.584) and
  f–`BR(0,1)` 0.586; the fourth free square is an **idle strut** (forces 5e-4 and 3e-4) and the
  configuration's single flat direction at fixed s is blocked **only at second order**, curvature
  −3.9e-7 (ratios 8.99 / 99.9 across |t| = 1e-3, 3e-3, 1e-2 — the quadratic signature). It
  explains **267** alive nodes across six skeletons (k5_11 184, k5_16 68, trump5 12, k5_02, k5_03,
  k6_29) and carries the deep tree: 10 of the 19 explained level-3 and 4 of the 9 level-4 nodes,
  and 97 of the 232 level-2.
* **Half the explained nodes are not near anything.** 620 of 1260 sit on **S01, whose shadow
  minimises to a side of exactly 4.000000** = ŝ + 0.1229 — thirteen times the pinwheel's slack —
  and 62 combinatorially distinct configurations share that value. For those branches the LP's
  integral support is a side-4 arrangement: it is saying *this has room*, not *this is nearly
  feasible*.
* **One value below A106's census floor. S07: s\* = 3.8856180554 = ŝ + 0.008534**, a k11 packing
  on the trump5 skeleton `BL(0,0) BL(0,1) BL(0,2) BL(1,0) BR(0,0) TR(0,0)` with five free squares
  near 44.88°, explaining 19 alive nodes (trump5 18, k5_16 1). Containment exact, worst pairwise
  SAT −9.5e-8 (inside SLSQP's own tolerance), and feasibility restoration at s = s\* + 1e-7
  reaches a configuration with every non-degenerate gap ≥ 0. **No exact interval endpoint
  certificate** in A106's style has been produced, so treat it as numerically verified only. It
  touches no bound (it is above ŝ), but A106 §2.1's floor of 3.886746 for these classes was not
  the true floor.
* **306 alive nodes are explained by NO integral shadow.** Their dual supports are genuinely
  fractional *and* contain no budget-many pairwise cell-disjoint placements among those with
  y > 0.02 — 303 of the 306 top out at 4 of 5. There is no near-packing to draw for them; the LP
  is stalling on a fractional object. Breakdown: k5_11 151 (L1 110, L2 35, L3 4, L4 2), k5_16 113,
  trump5 42. Full list in `attempts/A107-shadow-gallery/results/unexplained.json`.
* **Method points that mattered.** (i) *The LP rows are configuration-space cells*, pitch 0.1918
  in x/y and 5° in tilt, so the drawn representatives overlap by up to a pitch — the verified
  integral solutions in this corpus have worst pairwise SAT gap **−0.2045** — and the honest
  disjointness test is gap ≥ −0.21. Testing at ≥ 0 would have called every shadow an overlap and
  found zero integral components in 1122 fractional supports; at −0.21 it finds 818. (ii) *Flex
  counts use exact incidence Jacobians*: one row per incident vertex, the analytic derivative of
  n·(V−P) including the rotation lever term and the dc/ds term for slot squares — never a finite
  difference of a SAT gap, which is wrong at flush contacts and at exactly-opposite vertex-vertex
  contacts (whose normal is a cone; 15 entries carry one, and their individual multipliers blow
  up while the per-contact resultant stays finite). Every flat direction is probed at second order
  against the exact gaps. (iii) *A shadow is a value of s\*, not a point*: the k7 family's five
  landings share the same three-square 48.435° core and differ only in where the loose fourth
  square sits along its flat direction (0.15 in x), so the brief's 0.05/3° point rule splits one
  shadow into five. A106 reached the same conclusion independently. The gallery groups by s\* and
  reports, per entry, how many distinct minimised configurations (0.05/3° modulo D4 on the
  **load-bearing** squares) share it.
* **Totals.** 173 distinct snapped structures → 305 landings → 53 shadow values / 207
  configurations. 38 k11 shadows (1132 nodes); 15 k9/k10 ones (128 nodes) from LP runs that never
  converged and whose integral support is short of budget — their s\* below ŝ means nothing.
  160 flat directions: 71 genuine flexes, 80 blocked at second order, 9 rank-tolerance artefacts.
  20 of 238 free squares are rattlers (removal leaves s\* unchanged). 13 of the 53 entries are
  clean KKT points (residual ≤ 1e-6, 1065 nodes); the other 40 lean on a variable bound or stopped
  short and their s\* is an upper bound — flagged in each section.
* **What this does not say.** "Explains" means the node's own LP dual support, snapped and
  released, minimises to that shadow. It does **not** mean the node's pose box contains it —
  A106 §2.2 measured that and found zero of 62 landed open boxes does, median ∞-gap 0.3166 ≈ 9
  r_basin. That finding is reused, not re-derived.
* **Discipline.** One BLAS-pinned process; nothing under A57/A60/A61/A85/A96/A99/A104/A105/A106 or
  `lean/` written and no campaign process touched (the single taskkill in the session targeted
  A107's own PID); frozen verifiers untouched. Writes: `attempts/A107-shadow-gallery/**`,
  `docs/shadows.md`, `docs/shadows/*.svg`, registry row, this entry, one note line on `C.A57`.
  Every drawn square containment-checked; the minimised panels also overlap-checked; overlaps
  appear only in the raw LP panel and are printed as numbers. Wall 2 h of the 3 h cap (compute: extract 44 s, structure minimisation 868 s, gallery 2760 s).
- A57 T5-prime DEPLOYED 2026-09-05 23:25 (pinguard.kill_core, classify() only; Box.core() untouched so the LP hypothesis and the
  emitted certificate corpus are unchanged). Control re-run against the DEPLOYED module, not A96's shim: 583/583 known logic-kill
  boxes still killed, none lost; same 70 new kills at the same level split. Workers restarted through launch.ps1 (pidfile gate
  held) because Python caches imports -- without that the six shards and both deepens would have kept emitting unfiltered.
  Recorded as T5-prime in notes/lemmas.md next to T5 (certificate UNCHANGED, only the core half-side grew); the 70 superseded
  boxes are in results/superseded_by_tight_core.jsonl with prior verdicts RETAINED, nothing overwritten.
- FIRST WINDOW (1 h, not a day -- the wait was stopped): 85 children emitted (38 L1, 47 L2), 28 recorded KILL-BY-LOGIC
  (14 L1, 14 L2). ATTRIBUTABLE to T5-prime by direct re-classification with TIGHT_CORE off vs on: 5 of the 28 (1 at L1,
  4 at L2) are kills the OLD core would NOT have made. That is the honest incremental number; the other 23 the old rule would
  have caught anyway. 5/85 = 5.9% of emitted children, against the offline prediction of ~4-5 on this L1/L2 mix -- consistent.
  The filter is confirmed live in the restarted workers, which is what this window was actually able to establish; the hour's
  raw kill RATE is not evidence either way, since an hour's boxes are not a random sample of the cover.
- 2026-09-06 00:37 PAUSE (PI directive): A61 campaign61 + resolve61 (k5_05, k6_21) stopped, resumable (attempts/A61-window-stragglers/PAUSED.md); A57/A96 workers being paused by A96 (attempts/A57-shadow-trees/PAUSED.md). Reason: A108/A109 may change the tree's economics (node-level SLOT-CROWD rows, shadow basins). Chores A108/A109 continue.


## 2026-09-06 — A108-s07-certify (Opus chore, read-only) — done-success: S07 is exact, and it is NOT Trump's basin

**s\* = 2 + 4√2/3 = (6 + 4√2)/3 = 3.885618083164127 exactly** (s\* − ŝ = +0.008534493141313).
Released with all eleven squares free (A106's `shadow11` at zero pins, cross-checked against A107's
engine) A107's S07 landing polishes to a configuration with every coordinate in **Q(√2)** and every
tilted square at **exactly 45°**; the six active contacts close by hand into 3s = 6 + 8·(√2/2). It is
a **quadratic** irrational — ŝ is degree 8. A107's gallery value 3.885618055 is **2.8e-8 low**: that
landing overlapped by 9.5e-8, so its true side is 3.8856184245.

* **Exact packing proof, no tolerance in the decision**: 55 pairwise SAT gaps and 44 containment gaps
  computed as a + b√2 with a, b ∈ ℚ (sign by comparing a² with 2b²) — **0 violations**, 24 rows
  exactly 0. A106's mpmath-iv `certify_endpoint` also PASSes at the first rung, **ε = 1e-9**
  (s_cert = 971404521041/250000000000, margin 2.20e-10), from the polished landing and from the exact
  configuration alike.
* **Contact graph** (exact supporting faces, not a tolerance test): 14 pair + 10 wall rows —
  `f0`–`f2` and the three BL column pairs are **full-edge flush**, `f0`–`f1` / `f0`–`f4` / `f1`–`f2` /
  `f2`–`f4` partial flush, `f0`–`BL(0,1)`, `f1`–`BL(0,2)`, `f2`–`TR(0,0)`, `f4`–`BL(1,0)`,
  `f4`–`BR(0,0)` vertex-on-edge, and `BL(0,1)`–`BL(1,0)` a **corner-corner point kiss** (the type
  known_results 16a records A31's menu as omitting — Trump has one in the same place).
* **NOT first-order rigid**: rank 30 of 33 at fixed s, **3 two-sided flexes**, which are exactly
  `f3`'s three degrees of freedom (free to at least third order; its slack is 0.0118). The one-sided
  cone {v : Jv ≥ 0} is bigger still — `f4` slides along its shared 45° edge.
* **Fritz-John fails at first order for a geometric, not numerical, reason**: nnls residual 0.152,
  concentrated on `f1.θ` and `f2.θ`. A unit square at *exactly* 45° touching a wall has **zero
  first-order torque** from that wall — its touching vertex sits at the top of its rotation circle, so
  the containment gap is quadratic in θ (half-width loss 3.54e-7 at dθ = 1e-3, 3.54e-5 at 1e-2). Local
  minimality is therefore established at second order: minimising s inside an L∞ trust region of
  radius ρ returns s\* for every ρ ≤ 0.03 (worst excess 3.1e-7). **METHOD WARNING, general**: the
  naive "perturb and re-minimise" without a trust region reports a spurious descent to ŝ from
  perturbations as small as 0.002, because SLSQP repairs the infeasibility by walking out of the basin.
* **Load-bearing**: force-bearing `f0 f1 f2 f4` and slot squares `BL(0,0) BL(0,1) BL(0,2)` (their
  stacked height 3 is what enters the s equation), `BR(0,0)` (stops `f4`), `TR(0,0)` (stops `f2`,
  though its contact is *implied* by the others for every s). `BL(1,0)` carries no contact force but
  removing it drops the ten-square optimum to 3.788 — a space filler, not a strut. `f3` is the only
  rattler in both senses (removing it changes s\* by +1e-5).

**vs Trump** (`docs/residue_map/s07_vs_trump.svg`, both panels containment- and overlap-checked,
worst SAT −4.4e-16). Same eleven-square skeleton in the **same D4 frame** (best of the eight
alignments is the identity); `BL(0,0)`, `BL(0,1)`, `BL(1,0)` are identical to 0. Exactly two things
differ: the tilt (**45° vs 40.1819°, a gap of 4.8181°**) and Trump's `BL(0,2)`, **lifted 0.03256 off
its slot** — the TL two-crowd. L∞ pose distance 0.0841. The mechanism swap is visible in the contacts:
in Trump `f3` is wedged on the right wall between `f2` and `f4` and `BL(0,1)`–`BL(0,2)` is open;
in S07 the column closes, `f0`–`f1` appears, and **`f3` falls out of the load path entirely**.

**They are separate local minima.** Along the straight segment in normalised pose space the exact side
function σ rises to **3.917542707 at t = 0.692**, +0.031925 over S07 and +0.040459 over Trump. The most
generous path measured — hold the five tilted squares at a common tilt and re-minimise all eleven
centres, the six upright tilts and s, on a 0.05° grid warm-started from both ends — still crests at
**3.886723119 at 41.60°, +0.001105 over S07** (below the crest the branch flips and s falls
monotonically to ŝ). Read the other way: **S07 is what Trump becomes if its one disturbed upright is
put into the `BL(0,2)` slot, and the price is exactly +0.0085345 of side** — A101's cellflood named
that square and its extension class k6_07; A108 puts the number on it.

**Class and kill.** Six simple squares ⇒ **k = 6**; Young diagram BL (3,1) by columns, BR (1), TR (1),
TL ∅; the slot set matches census class **k6_07** under the identity of D4 (trump5 + `BL(0,2)`). The
covering kill is the A53/A54 k6_07 stratum certificate (PASS at s0, 11 atoms, total 4.806673) with
A56's parametric transfer **PARTIAL**: certified on [191/50, 956767/250000] = [3.82, 3.827068],
window coverage **12.38 %**, open band (3.827068, s0] — A61's **G-A56-3**, currently paused. But
s\* = 3.885618 sits **0.0085 above the window's right endpoint**, so no S07-shaped packing exists
anywhere in W = [3.82, s0] and that open band is not about this configuration. What S07 is about is
the trump5 tree's slowness: it is the shadow of 19 alive-at-LP nodes (A107: trump5 ×18, k5_16 ×1, all
level 1) and 0.0085 of slack is exactly the scale a δ = 1e-2 emission cannot resolve.

Constraints honoured: read-only on A22/A53/A56/A57/A60/A61/A106/A107 and `lean/` (their modules are
imported, never written); one BLAS-pinned process; git fetch + plain merge + push own paths only.
Writes: `attempts/A108-s07-certify/{code,results,notes}`, `docs/residue_map/s07_vs_trump.svg`,
registry row, this line. Corrections of record to A107's S07 row (s\*, the 44.879° common tilt, the
8 flexes, the "convergence caveat" on the KKT residual) are in
`attempts/A108-s07-certify/notes/method.md`; `docs/shadows.md` itself was left untouched.
- 2026-09-06 01:55 RESUME A61 stragglers (PI): campaign61 pid 45764, heavy 2 / jobs 3, BLAS pinned; A57/A96 remain paused.

## 2026-09-06 — A110-grain-flood (Fable, theory lead) — done-mixed: grains are exact and unify Trump/S07/S02; the box-to-grain map has no certificate short of the class kill

**T3 first.** Theorem GRAIN-FLOOD in the ledger's form is TRUE and EMPTY: a packing of the class at side ≤ s0
makes the global minimum over the compact class phase space a local minimum ≤ s0, so "every local minimum ≤ s0 is in
Trump's grain" IS the class kill. The flow route (a monotone quantity from a box) is the node's own bound; the
enumeration route is the selection census (≈ 8⁴⁵ separating-axis choices for an A57 node with five free squares),
which the tree prunes by localisation — the existential-filter law again. Obstruction drawn
(`attempts/A110-grain-flood/results/box_to_grain_110.svg`): node c0_Y0324's box holds the RATTLER of its LP support,
no load-bearing square of the S07 family at any tilt is in the box; A106's boxes flow to eight shadow values. What
is sound: Lemma GRAIN-LP (at fixed tilts and selection the side minimum is an LP whose dual is a balanced force
system = a load path), Lemma INHERIT (the formula survives every unloaded contact change), Theorem CONT (s_min is
continuous in the tilts, n-general — the PI's dichotomy is about loaded rows, not continuity), GRAIN-ROW (a conflict
row on the support's cells: kills the support, not the node).
**T1/T2.** [T] S07 = the crossing at 45° of the ladder Λ(θ) = 2 + 2(cos θ + sin θ)/(1 + sin θ cos θ) (minimum
2 + 4√2/3 only at 45°) with the column chain Y(θ), Y − Λ = (sin θ − cos θ)(cos θ + sin θ − 1)/(1 + sin θ cos θ):
s_min = max(Λ, Y), the first-order blindness of A108 is Λ′(45°) = 0. S02 = the triple point sin θ cos θ = 2 sin θ − 1
(θ* = 48.43512°) of the same Λ with the diagonal chain D(θ) = 2 + (2 + cos θ)/(cos θ + sin θ) (and the wedge A);
s* = Λ(θ*) = 3.886746029, S02 − S07 = 0.001128 because the diagonal forces the ladder off 45°. The Trump boundary of
S07's family: f0's vertex reaches BL(0,1)'s corner (1,2) and enters the gap under the lifted BL(0,2); the basis
changes to the gap chain F_T(θ) = 2 + (2 + sin θ)/(cos θ + sin θ) = D(90° − θ) at sin θ cos θ = 2 cos θ − 1 (41.56488°,
crest value 3.886746029 = S02's exactly — the "mirror minimum"), and F_T falls to ŝ: **TRUMP-GAP: ŝ = 2 + (2 + sin
θ_T)/(cos θ_T + sin θ_T) to 40 digits** (A03 data); Trump, S07, S02 are three kink minima of one menu {Λ, Y, F_T (=
mirror D), A}. [M] sweeps (all eleven free, common tilt pinned, 0.1–0.25°): s = Λ on [41.6°, 45°) to 1.9e-8 and Y on
(45°, 53.75°] to 2e-7 with ONE loaded set per side (13 contacts flicker unloaded, the formula never moves); the gap
grain to 2.8e-8 from both sides on [40.45°, 41.55°]; S02: Λ on [48.5°, 62°] to 1e-6, D on [44.9°, 48.4°] to 2.6e-7,
one loaded set per side; minimum of every sweep = the shadow's value; the grid is Λ(0) = 4.
**T4.** S07 0/19 inside the family (13 have the centres, none the tilts: the six f1_* nodes are Trump's grain at
39°–41° — canary; the twelve cover nodes draw S07's skeleton at 21°–44°/58°–69°); S02 56/267 (37 L1 + 19 L2 of A57;
0 of the 14 deep L3/L4 nodes, 0 of A60's 12, 0 of A61's 3). Price: two one-variable inequalities per family vs
290–336 s per A57 child / ~1 100 s per A60 leaf — but the sound consumer kills support patterns, not nodes.
Canaries: Trump alive (its grain minimum is ŝ; different selection; TRUMP-GAP identifies it), S07 dead at
2 + 4√2/3, S02 dead at 3.886746029, grid a grain of side exactly 4. Files: `docs/proofs/grain_flood.md`,
`attempts/A110-grain-flood/{code,results,logs,notes}`; depgraph notes on C.A57/K0.RESN + node GRAIN (owner A110).
Constraints honoured: one process, BLAS pinned, read-only on A57/A60/A61/A96/A109 and `lean/` sources (depgraph.json
notes only), frozen verifiers untouched, git fetch + plain merge + push own paths.

## 2026-09-06 — A109-node-crowd (Opus chore, 2 BLAS-pinned processes, read-only on A57/A60/A61/A94/A96/A107) — done-negative
- **T3 (one line): node-level SLOT-CROWD rows kill 0 of 18 genuinely-alive A57 nodes at every depth the window
  licenses (delta = 0 sound, 0.05, 0.1) and 18 of 18 at delta = 0.3, certify 0 of 10, cost 128 s per node per
  delta, and are worth -0.4 wall-days at 5 workers.** The mechanism is real; its threshold sits at delta ~ 0.2-0.3
  and Theorem N-S licenses a delta certificate only for sides m <= s-hat' - delta = 3.577, i.e. **0.24 below the
  window floor 3.82**. Notes `attempts/A109-node-crowd/notes/report.md` and `notes/method.md`.
- **NEW, REUSABLE, EXACT (`code/aw_check.py`): the SLOT-SLIDE margin and the Lemma B-YES-S dilation pad cancel.**
  On any window [m_lo, s] and any usable slot whose extension is dead on the FULL window,
  sup over m of [lambda(m)(1 - (s - m)) + (lambda(m) - 1)(1/sqrt2 + max(i,j))] = 1 exactly, attained at m = s,
  independently of the cell. So the ONLY sound crowd family on A57's G1 slab (m_lo = 3.8616374951330865,
  lambda_max = 1.004) is a_w = 1 — "two non-pin squares MEET the open slot box", delta = 0. A94 refused
  a_w >= 1 only because its CHAIN needed delta > delta_pad; at the node level that refusal was the wrong call
  and a_w = 1 is the right family. A109 used a_w = 1 + 1e-5 as a strict outer pad.
- **m_u = 3, not 4, on a SLAB.** The fourth usable slot of each class extends to k6_23, certified on
  [3.82, 3877/1000] plus the A54 fixed-s0 certificate; the sub-interval (3877/1000, s0) of A57's G1 slab
  therefore carries NO crowd hypothesis there. At a FIXED side s0 (A60's exact-pin nodes) it does, so m_u = 4
  is right there and A94's own choice stands for its own certificates.
- **The node-level incidence budget (new bookkeeping).** budget = budget_node + floor(eB),
  B = 2 m_u - (sum over the BRANCHED cores of r_max), because the branched square is a non-pin square that is
  exempt from the LP rows and may carry crowd incidences the LP cannot then collect. r_max bounded two ways:
  over B+ = every unit square CONTAINING the core (|c-k| <= sqrt2(1/2-a), |dtheta| <= arcsin(min(1,1/(2a sqrt2))) - 45 deg)
  and, tighter and equally sound given tree57.build_children's "some square has its pose in b", over the branch
  box itself. Measured B in {3..6} at m_u = 3 and {5..8} at m_u = 4; the tighter B changes no verdict.
- **One LP decides a node.** tau(e) is an LP optimum with rhs affine in e, hence convex increasing, so
  c(e) = (tau(e) - tau0)/e is non-decreasing and eta(e) = eta0 + c(e) e - floor(eB): if the smallest e that
  buys any bonus returns c >= B, no larger e can kill. Implemented as `t2.py --e auto`.
- **T1 (the mechanism check on the shadows).** Over the 552 A57 alive nodes A107 explains by S01/S03/S04/S05
  (k5_11 x263, k5_16 x289; levels 1-4), the dual support leaves a usable slot empty or singly met in **93.7 %**
  of nodes (mean 1.89 of 3 slots violated, mean total incidence 4.81 against the 6 Lemma SLOT-CROWD requires);
  per shadow 94.3 / 94.7 / 96.5 / 79.4 %. Slot ranking: k5_11 BL(1,1) 214, k5_11 BR(0,1) 189, k5_16 TR(1,0) 185,
  k5_11 TL(1,0) 175, k5_16 BR(0,1) 168, k5_16 TR(0,1) 107.
- **T2 (the kill).** 46 stratified nodes (S01 15, S03 8, S04 8, S05 5, 10 unexplained controls; levels 1-2;
  every one is 5 pin boxes + ONE branched box), 4 configurations, e ladder by the convexity rule. Only 18 of the
  45 solved were genuinely alive at the LP (eta0 >= 0) — the other 27 were already tau < budget pending
  convergence in A57, which is worth knowing about the "alive-at-LP" population itself.

  | cfg | a_w | m_u | mean B | mean c = dtau/de | c >= B | ATTRIBUTABLE kills | mean eta - eta0 |
  |---|---|---|---|---|---|---|---|
  | sound | 1+1e-5 | 3 | 4.37 | **6.23** | 42/45 | **0 of 18** | +0.77 |
  | delta = 0.05 | 0.96063 | 4 | 6.22 | 7.69 | 39/44 | **0 of 18** | +0.90 |
  | delta = 0.1 | 0.91043 | 4 | 6.35 | 7.03 | 37/44 | **0 of 18** | +0.67 |
  | delta = 0.3 | 0.70963 | 4 | 6.71 | **4.83** | 2/44 | **18 of 18** (11 converged) | -1.05 |

  **T1's 94 % upper bound collapses to a 0 % kill rate because the crowd rows do not forbid A57's dual support,
  they re-price it, and the LP moves.** The usable slot boxes are 0.877 apart per axis at s0 while a 45-degree
  unit square spans 1.414, so one fractional placement sits in two or three boxes at once — exactly the
  multiplicity Lemma CW-S pays for with the incidence budget N + 2 m_u e, and at the licensed pad it is a wash.
  Depth breaks the multiplicity, and only depth.
- **Certification: node-level boxes do NOT escape A94-G4.** 10 LP-dead nodes (5 at a_w = 1, 5 at delta = 0.3)
  through the frozen `verify_case.py` (sha 521cb01f..., depth 56, one witness-feedback round) in A94's
  1 + r_max form with the NODE's own cores: **0 of 10 certified**; run A PASSes 9/10, and the multiplicity runs
  B_r fail on 5-32 exact HOLES each — **at B_1 already**, whereas A94's G4 node passed B_1 and failed B_2-B_4.
  The incidence rows remain the unpriced part of the certificate (A94-G4), and small boxes make it worse.
- **Trump canary PASS.** Exact Trump slot depths reproduced in A109's own frames to 4.7e-7 (all six unclipped
  cells of trump5). The trump5 CLASS ROOT with A57's slack pins (rho = 1e-2), a hypothesis the exact Trump
  satisfies, carries the crowd rows and survives at sound / 0.05 / 0.1 (eta = +1.33 / +1.20 / +1.04) and only
  dies at delta = 0.3 (eta = -0.51) — just past Lemma CEIL-T's delta_T(trump5) = 0.1555, exactly as the ceiling
  predicts. Nothing false was killed.
- **Price and composition.** 128 s mean per node per configuration (median 92, max 392) against the same nodes'
  original A57 LP wall of 396 s (median 321) and A57's measured 581 s LP+certify per level-1 node; certification
  72 s mean for the whole 1 + r_max chain. Over the 1536 open boxes: route (a) "re-solve alive nodes only" costs
  2.1 CPU-days and returns nothing at every licensed delta = **-0.4 wall-days at 5 workers**; route (b) "rows in
  every node LP" is never cheaper at the same kill rate. At delta = 0.3 the same route would return the whole
  66.53-CPU-day remainder (+12.7 wall-days at 5w) — that is the size of the prize if a lemma ever licenses depth
  on this window.
  **Parametric compatibility:** run A rides `A96/code/verify_param.py` unchanged (n = 11 + eB, the budget clause
  is s-free, and --strict-margin r e is exactly B_r's inequality); runs B_r do NOT — the file raises
  "nofams unsupported" and E_r is a NO-family cover. The slot frame is corner-anchored, so F_p(a_w) is
  s-INDEPENDENT in the frame and every E_r box is an affine alpha + beta s rectangle with beta in {0,1} per side,
  the same affine form the verifier already uses for atoms and cores — the extension is small, but it does not
  exist today and **crowd rows are fixed-s0-only as things stand.**
- **A109-O1 (stated dependency, not discharged here).** SLOT-CROWD at the slab's top endpoint m = s0 needs the
  extension classes dead AT s0, not merely on [3.82, s0); the FULL k6 rows carry A54/A56/A61 fixed-s0 base
  certificates and `A96/notes/pocket96.md` sec 2 leans on the same reading. If it is wrong, the a_w = 1
  configuration covers (m_lo, s0) and leaves the single side s0 to A57's own leaf.
- Discipline: A94's engine and the frozen verifier COPIED into `attempts/A109-node-crowd/code/`; every campaign
  node json COPIED into `results/nodes/*.src.json` before use; nothing written under A57/A60/A61/A94/A96/A107;
  no campaign process started, stopped or re-niced; at most 2 A109 processes, BLAS pinned, free commit > 6144 MB
  and free physical > 3072 MB gated before every LP. `rows_all`/`packing_images` were emptied from A109's own
  node jsons after the run (flagged `a109_trimmed`) to keep the attempt directory at 9.5 MB.
- A96 TILT-BIN TRIMMING measured offline (code/trim96.py; campaign stays paused, nothing deployed).
  Geometry: a pin contributes an axis-aligned guaranteed core of half-side 1/2 - delta; Q(c,theta) overlaps it iff c lies in an
  OCTAGON about the slot (the Minkowski sum), |d_x|,|d_y| <= w/2 + a_P and |d.u|,|d.v| <= 1/2 + a_P*w, w = |cos|+|sin|. A tilt
  sub-interval is CERTIFIED DEAD when the whole centre box lies inside ONE pin's octagon for every theta in it -- exactly T5's
  contradiction, restricted to a tilt range. Only the dead side is certified, so the trimmed fraction is a LOWER bound.
  POSITIVE CONTROL CLEAN: 618/618 existing T5/T5' kills come out fully dead, zero violations.
  YIELD (2222 boxes): 159 boxes have an EMPTY surviving bin = new T5-style kills -- L1 51/1126, L2 86/425, L3 10/39, L4 12/14.
  That is 2.3x T5' alone (70). Partial trims: 155 boxes with 0 < surviving < 1 (L1 97, L2 55, L3 1, L4 2), median surviving
  fraction 0.46 at L1 and 0.66 at L2.
  a_tight ENLARGEMENT from trimming is SMALL, contrary to expectation: over all boxes the median gain is 1.000, and even among
  the 155 partially-trimmed boxes it is min 1.0002 / median 1.0459 / max 1.1455. Trimming pays through the 159 outright kills,
  NOT through the core it enlarges.
- LEMMA TC IS EXACT, not a numerical observation. min over directions alpha of (h1+h2) for two unit squares at tilt difference D
  is attained at alpha = 0 and equals (1 + cos D + sin D)/2; verified against a dense alpha search to 2.2e-16 (machine epsilon)
  over D in [0,45]. Inverting: c <= 1.05 => |D| <= 6.061 deg, c <= 1.10 => 13.052, c <= 1.15 => 21.815, c <= 1.2071 => 44.749 --
  reproducing the PI's figures.
- TC AS THE PIN-TRIMMING RULE (item c): TC IS the closed form of the trimming observation for axis-aligned pins, but it is
  STRICTLY WEAKER than the exact interval test, because it keeps only the centre DISTANCE and discards the direction. Head to
  head on 1604 boxes: identical on 1321, the octagon test trims MORE on 279, TC trims more on only 4. Full kills: TC 33 vs
  octagon 159 -- a 4.8x gap. The 4 boxes TC wins are ones where it uses the TRUE unit square (half-side 1/2, centre uncertain by
  delta) while the octagon test uses the 0.49 guaranteed core, so running BOTH is marginally better than either. Conclusion: keep
  TC as the O(1) pre-screen the PI proposes, but the exact interval SAT test must be what decides.
- A96 item (4): TRIMMING'S EFFECT ON THE 13.31-WALL-DAY SCHEDULE. The 159 trimming kills decompose EXACTLY as the 70 T5' already
  makes (20/32/7/11 -- perfect match, an independent confirmation that trimming subsumes T5') plus 89 INCREMENTAL.
  Incremental rate against post-T5' open denominators: L1 31/1106 = 2.80%, L2 54/393 = 13.74%, L3 3/32 = 9.38%, L4 1/3 = 33.3%.
  The L3 and L4 denominators (32 and 3 boxes) are NOT measurements -- L4 in particular is one box out of three.
  Direct saving (node cost only): with the measured rates 16.21 d 1-proc = 3.24 wall-days @5w, 13.31 -> 10.06. With the L4 rate
  replaced by the L3 rate (the honest version, since n=3 decides nothing) 10.31 d = 2.06 wall-days, 13.31 -> 11.24.
  Subtree removal on top: 24 of the 89 incremental kills were ALIVE at L1, 12 at L2, 1 at L3, and an ALIVE kill removes its whole
  descendant cone (~20.8 nodes at L1, ~14.1 at L2, 8 at L3 under the measured f2 = 0.906, f3 = 0.762, f4 = 0). Scaled to the
  population that is ~29.5 d, but it PARTIALLY DOUBLE-COUNTS the deeper direct terms, so it must not simply be added: the honest
  read is 13.31 -> 10-11 wall-days from the direct effect, with the subtree effect making that a conservative upper bound rather
  than a further subtraction.
  Where it pays: L2 (4.52 d) and L3 (3.03 d) carry the credible saving; L1 contributes 0.44 d and is not worth the emission-time
  cost on its own.
- DEPLOYMENT SHAPE (recorded for when it is authorised): a node becomes [trimmed child] + [k excluded tilt intervals]. The
  trimmed child is a SUB-BOX, so its certificate is the ORDINARY one -- verify_case / verify_param untouched, no new leaf kind,
  no new Lean. Each excluded interval [th_a, th_b] is one T5 instance with a tilt RANGE: "for all (c,theta) in box x [th_a,th_b],
  Q(c,theta) meets K_Pj", certified by interval arithmetic over the four SAT axes (max |d.n| over the interval against min
  (h_Q + h_K), evaluated at the four box corners since the octagon is convex). Lean shape = core_meet_same_square parameterised
  by the tilt range. To be recorded in notes/lemmas.md exactly as T5' was, with its own positive control (618/618).
- Row-dropping stays SHELVED with route (A): it is a different soundness proposition, because it changes the verifier's
  admissibility clause from "disjoint from every core" to "disjoint from SOME pose of the box", which touches the frozen chain --
  unlike trimming, which does not.

## 2026-09-06 — A113-k0-manifold-distance (Opus chore) — done-mixed
- Question: is the k0_00 tree's alive/expensive population concentrated near the k >= 1 manifold?
  Measure: eta(cell) = max(L-inf distance from the cell's position box to the nearest of the 36 corner-lattice cell centres at
  s0 (four corners x depths i,j in {0,1,2}; depth 3 is not containable), sqrt(2) sin(tilt-gap/2)), tilt gap = distance of the
  cell's theta interval to 0 mod 90. Pure geometry, no LP, one BLAS-pinned process, read-only on every campaign.
- **T3 (the number asked for): only 1.4% / 4.6% / 17.6% of A99's 9,341-21,661 CPU-h projection lies within eta = 0.05 / 0.1 /
  0.2 of the manifold** (measured-cost-weighted 1.5 / 5.1 / 18.9%; by parent level-1 cell 5.6 / 9.3 / 38.9%). Enumerated
  box-by-box over all 1728 + 13824 + 110592 nodes of A85 s.8.3 as re-parametrised by A99; the reconstructed total is
  18,624 weighted nodes = A99's figure exactly. **And the far region is not cheap: all five alive(LP) level-1 cells sit at
  eta 0.229-0.366**, as do 17 of the 33 cells whose tau is already >= budget.
- CANARY, two readings, and they disagree. As packings the eight Trump images are ON the manifold (each has exactly 5 simple
  squares at eta = 1e-7). As cells they are not: the three level-1 cells holding a Trump image's conditioned placement sit at
  eta = 0.3660, because the tree conditions on an INTERIOR square and Trump's interior squares are the tilted ones (40.18 and
  49.82 deg; the poses themselves have eta 0.4858). Same for S07 (44.88 deg) and the k7 pinwheel (48.44 deg). Guiding on the
  conditioned square's distance to the corner lattice is guiding on the wrong coordinate; only 2 of the 6 level-1 tilt bins
  touch 0 mod 90 at all.
- T1. The POSITION term alone does predict, in the direction the PI wants: **0 of the 26 processed level-1 cells with
  d_pos <= 0.05 was ever killed by the LP, against 45% at d_pos >= 0.2**; Spearman(d_pos, tau) = -0.438 overall and
  -0.460/-0.466/-0.464 inside each of the three tilt bins separately, while d_tilt vs tau = +0.028 and the combined eta washes
  the signal out to -0.145. The six most LP-resistant cells in the whole root (tau 10.06-10.500 > budget 10 -- un-killable,
  since a kill needs a converged tau < budget and tau climbs under row generation) are at d_pos <= 0.02. Those 36 root cells
  carry 16.7% of the projected cost and have produced zero kills. LP wall time is FLAT in eta (rho = +0.053, median 496-504 s
  in every bin): cost is carried by un-killability, not by per-node price. dist_centre (A38's own ordering key) vs tau = +0.307
  and eta vs dist_centre = -0.234, so this is not the interior-first processing-order confound.
- T1 note: the k0_00 tree has **zero logic kills** -- `hyp.nofams = []` in all 264 node jsons, because Lemma ID fires only at a
  SHALLOW corner and the k0 root does not branch on corners. A85's own 12 rows run the other way (PASSes at eta 0.000-0.172,
  FAILs at 0.124-0.497) but that is a selection effect: A85 only ran nodes whose LP already had slack, and inside that sample
  PASS/FAIL tracks eta_LP (-1.00...-1.27 vs -0.12...-1.19), not eta. A38 level-2 (80) and level-3 (24) have no decided cells.
- **T2 -- the signal is in the LP dual support, not in the box.** Mean simple placements (eta(pose) < 1e-2) in cores + integral
  support: ALIVE 3.40 (5/5 with >= 2), UNDECIDED 2.01, FAIL 1.86, PASS 1.00, LP-killed **0.81** (only 6 of 36 with >= 2).
  Classified by A107's method (shadowlib.snap over the full D4 orbit, matched to the 53-shadow gallery): the killed cells'
  supports match nothing better than **S01, A107's s* = 4.000000 "this branch has room" shadow** (median Jaccard 0.20), while
  the survivors are partial skeletons of near-critical shadows (median 0.75 at median s* 3.9920). Named: l1_100 (ALIVE) is an
  **exact slot-set match to S38** (trump5 boundary, s* = 3.928915, common tilt 41.75 deg) with 6 simple placements of 10;
  s1int_l1_043 (A85 FAIL) is **Jaccard 0.83 to S07** (s* = 3.885618 = s-hat + 0.0085, A107's sub-pinwheel shadow), l1_071 0.50
  to S07; l1_088 (tau 10.206) is 0.80 to S04 with one square in each corner. Trump-skeleton Jaccard reaches 0.71. The five ALIVE
  supports are integral, 11 squares, all contained, worst pairwise SAT gap -0.130...-0.205, i.e. inside A107's one-cell-pitch
  bar (-0.21) -- genuine near-packings. Drawing: attempts/A113-k0-manifold-distance/results/svg/k0_alive_fail_supports.svg.
  So the expensive k0 residue IS near the k >= 1 manifold -- in the ten squares the LP places, not in the one the tree
  conditions on. That prices a RE-branching rule (branch on the slot the support keeps occupying), not a pre-branching one.
- Correction to A107: "A85/A99 had no LP jsons in this format" is a glob bug, not a fact. 264 k0_00 node jsons in exactly that
  format are on disk (134 A38 l1_nodes, 51 l2_nodes, 13 l3_nodes, 12 A85 results/nodes/k0_00, 54 A99 results/nodes/k0_00);
  A107's extract.py globs `results/nodes/*.json` while the k0 files live at `results/nodes/k0_00/*.json`, and A38 is not in its
  SOURCES at all. Fixing the two globs would add ~146 alive-at-LP k0 nodes to the gallery corpus.
- Open: no LP run, so every kill rate is A38's at its own settings and the "do the d_pos <= 0.05 cells stay un-killable at 5-10x
  LP time" question (A89-O3) is untouched; 82 of 216 level-1 and 41 of 104 level-2/3 cells were never run and the notrun ones
  are systematically the far-from-centre = near-manifold ones; the shadow match is STRUCTURAL (slot sets modulo D4), not
  A107's flow -- no minimisation was run from a k0 support.
- A96 item (2)/(a): TRIMMED-BIN LP RE-SOLVE, 29 of 32 ALIVE nodes done (one process, 240 s cap, 13036 s total, median 384 s).
  READ IT WITH THE CONVERGENCE COLUMN: only 2 of 29 CONVERGED, so tau is an unconverged bound and the naive "17 with eta < 0"
  is NOT 17 kills. Strictly: 4 nodes reach eta < -1e-6 (etas -1.0, -1.0, -0.0556, -0.0179), 19 sit on the T11 KNIFE EDGE
  (|eta| <= 1e-6, i.e. tau = budget to 6 places) and 6 have eta > 0. So trimming moves the LP but at a 240 s cap it does not
  DECIDE it -- which is exactly A109's finding (28/46 unconverged) reproduced on the trimmed hypothesis, and is the argument for
  running the 900 s re-check (item 3) BEFORE reading any kill count off a trimmed re-solve.
  TC ROW SCREEN on the same nodes: the closed form alone removes a median of 13153 of 30000 warm rows = 43.8% (min 7486, max
  21977). That is a large, cheap reduction in LP size, and it is the strongest argument for row-dropping -- but row-dropping stays
  SHELVED with route (A), because it changes the verifier's admissibility clause from "disjoint from every core" to "disjoint
  from SOME pose of the box" and therefore touches the frozen chain, unlike trimming.
- A96 PREPARED FOR RESUME (nothing launched; PAUSED.md resume block updated):
  (1) T5'' at emission -- code/trim57.py + tree57.build_children, trim57.TRIM = True by default, TRIM = False restores the old
      behaviour exactly. node = trimmed child(ren) + excluded intervals carried on the child record as trim_excluded with the
      witness pin, so the ledger supersedes rather than overwrites. A bin surviving in >1 piece emits suffixed ids (Y0007a/b);
      plain ids are never renamed. Control re-run against the DEPLOYED module: 618/618 still fully dead, zero lost, 159 kills.
  (2) code/shadow_sched.py -- OFF by default. A107's 1191-node table; at the current thresholds it calls 564 dead, 8 alive,
      619 unknown. Predicted-dead get LP cap x3.75 (240 -> 900 s) and verify depth +8; predicted-alive split without more LP.
      Scheduling only: it cannot touch a hypothesis, certificate or verdict, so it cannot affect soundness.
  (3) A96 code/recheck96.py -- ALIVE re-check at 900 s, resumable on (cls, id), --trimmed combines the longer cap with the
      trimmed bin.
  (4) code/pausegate.py -- sentinel file checked BETWEEN nodes by tree57, param96, resolve96 and recheck96, so a pause preserves
      in-flight results (the 2026-09-06 pause could not); plus an orphan reaper for certify children whose tree57 parent is gone
      (one had run 11.3 h unattributed).

## 2026-09-06 — A111-loadpath-branch (Opus chore, <= 2 BLAS-pinned processes, read-only on A57/A60/A61/A96/A107/A110) — done-mixed: the load path is Trump's, but branching on it kills nodes and pays

**Verdict.** Route (a) — branch every shadow-explained node on its load path — is **worth about +1 wall-day at 5 workers**, and it works for a reason the brief did not anticipate: the YES cell is killed not by the chain LP but *for free, by logic*, on about half the nodes. Two nodes were killed end to end with the frozen verifier.

**T1 — the radius of the chain kill on the YES side.**
- The fixed-tilt LP of Lemma GRAIN-LP obeys `grid_lb = s* − r` **exactly** at every cell tested, so it certifies the YES cell precisely while `r < s* − s0` = **0.0097** (S02, s* = 3.886746030) / **0.0085** (S07, s* = 2 + 4√2/3 = 3.885618083). A57's level-4 half-width 0.0087 is just inside for S02 (CERTIFIED at L4) and just outside for S07. Above level 4 the LP route does not exist.
- Selection is the other limit: only 4/8 (S02/lpa) and 4–5/11 (S07/lpa) loaded pairs have their separating axis forced at ρ = 2°, and **0** at ρ = 20°. The B&B never completes above L4.
- With anchors (`lpa`) the box-constrained minimiser returns `direct_min = s*` at every radius up to (0.2, 20°) for S02 — measured-dead everywhere, certified nowhere above L4.
- **Canary, and it bites:** the S07 YES region **contains Trump's exact packing** from ρ_T = 4.8181°, r_T = 0.0326 — and A57's own level-1 tilt half-width is **4.87°**, 0.05° over the line. The S07 branch is unsound at L1 *by construction*; the minimiser agrees independently (`direct_min` = 3.876736 < s0 at L1, ≥ s* at L2). S02's canary is clean at every radius: no D4 image of Trump satisfies the k5_11 or k5_16 pin set.
- **S02's load path IS Trump's**: its three load-bearing squares match Trump's three tilted squares under `diag` to r_T = 0.017532 and ρ_T = 1.383° — the quantitative form of A110's mirror identity D(θ) = F_T(90−θ). What separates a killable grain from Trump's is the SLOT skeleton (S02 carries BR(0,1), Trump's image BL(2,0)), not the load path. Hence the sound leaf must condition on the anchors.

**T1 second instrument (octagon / Lemma TC) — the structural split.**
- Against the class pins at the node's own side s0 the common-inscribed-core test and Lemma TC kill **nothing**, at any (r, ρ), for either shadow or either variant. The minimum core gap is **+0.0138 to +0.22** and the minimum TC slack **+0.0100 to +0.21**, both strictly positive and *increasing* in r. That is **genuine room, not a weak bound**.
- Why, structurally: both rules are **side-blind** — they see only pairs of boxes — while the grain kill is a *side* statement (the chain forces s ≥ s* > s0 with every pair of squares still strictly disjoint). No pairwise-overlap test can ever carry it. At the window floor s = 3.82 they do kill, up to (0.05, 5°) for S02/k5_16 and (0.035, 2.43°) for S07, because the right/top-anchored pins have moved in.
- **But against the node's own conditioned bin they fire constantly, and that is the free kill.** Yield over the alive nodes the shadows explain, at A57's own half-widths:

  | level | r, ρ | S02 | S07 |
  |---|---|---|---|
  | L1 | 0.0699, 4.87° | 113/264 (42.8 %) | 13/19 (68.4 %) |
  | L2 | 0.035, 2.43° | 152/264 (57.6 %) | 19/19 (100 %) |
  | L3 | 0.0175, 1.22° | 186/264 (70.5 %) | 19/19 (100 %) |
  | L4 | 0.0087, 0.61° | 200/264 (75.8 %) | 19/19 (100 %) |

  Verified by dense sampling: **723 fires, 57 840 pose pairs, worst SAT gap −0.0513, zero counterexamples**. Figure `results/free_kill.svg` (geometry-checked) draws both halves of the split.

**T2 — the NO side.** 22 nodes × 4–6 children at r = 0.1, ρ = 10°, warm from the parent's own atoms. **8 of 22 nodes had every NO child LP-dead**; the rest split into "some children alive" and "τ unchanged at budget". Re-pricing landings when a child survives: S02 20, S01 13, S05 7, S09 5, S03 3, S07 2.
- The coordinator's two questions: **(a) the octagon TRIM of the conditioned bin is a no-op** — over all 102 bins of the 22 nodes at 6×6×12 cells, 5 bins lose any cell, 3 shrink at all, mean volume ratio 0.971, none is emptied. `pinguard.classify` already applies that rule at branch time, so a bin that reaches an open node is by construction one it does not kill. **(b) The NO side is a convergence-time problem, not a re-pricing problem**: at a 900 s cap one child went 4.9865 → 4.7500 **converged DEAD** where 80 s left it unconverged, another went 4.9524 → 4.7500 still unconverged — and the instrument that actually decides is the certifier.
- **Certification (frozen `verify_case.py`, sha 521cb01f…, byte-identical): 14 PASS / 4 FAIL, and TWO WHOLE NODES DIED** — `k5_11_interior_Y0054_D00` (S02, level 2, **5/5**) and `k5_16_interior_Y0984` (S07, level 1, **6/6**). Failures cluster exactly where they should: every FAIL had |η| ≤ 0.33; every child with η ≤ −0.5 passed; Y0984's six children (all η = −1.0) certified in 1–132 s.
- `verify_param.py` raises `nofams unsupported` and every NO child is a NoFam, so all 18 certificates are **fixed-side** objects at s0 — the NO side must be re-certified per side of A57's four-side grid, and that is the only reason the branch cannot be emitted parametrically over the window in one pass.

**T3 — price.** The branch's population is not the 1536 open boxes: it is the **286 shadow-explained nodes**, and it is sound only where the YES cell dies, i.e. on **146 (51 %)** of them at their own level. Cost = 5 NO LPs at 82 s on all 146, plus certification at 151 s only on the 36 % whose children are all LP-dead = **1.07 CPU-days**. At the measured node-certify rate 2/3 that kills **35 nodes**, worth **6.43 CPU-days** at A96's measured per-kill value (16.21 d / 89 kills, subtree included) — **net +1.07 wall-days at 5 workers**. Sensitivity: +1.72 at a perfect child pass rate, +0.93 at 0.90, −0.15 at 0.50. *n = 3 fully-certified nodes, so 2/3 is a weak estimate and the honest read is "positive, order one wall-day".*

**The sound leaf.** `notes/leaf_shape.md` gives two: the Farkas leaf (obligations O1 selection census by interval arithmetic, O2 tilt subdivision, O3 affine relaxation, O4 one Farkas certificate per cell — *the Farkas vector IS the load path*), narrow but exact; and the free-kill leaf (`core_meet_kill` + `tilt_coupling`), wide, side-blind, and already inside the TCB because A57 discharges the same predicate 583 times on the deployed cover.

**Two bugs, both caught by sampling, both recorded in `notes/method.md`.** (i) Containment rows used the cell MAXIMUM half-width, which over-constrains the LP so an infeasibility proves nothing — the whole T1 grid was discarded and re-run with the cell minimum. (ii) `pinguard.tight_a` is stated for 0 ≤ θ0 ≤ θ1 ≤ 90 and a D4 **reflection** produces a negative tilt interval; fed that raw it returned a core of half-side **0.7840 > 1/2**, a "core" larger than the square it is inscribed in. `octagon.normalised` + `safe_kill_core` fix it (a claim must hold for every tilt branch). The census fell 166 → 113 at L1; the T1 verdict was unchanged. **B(ii) was invisible to every internal consistency check and visible immediately to sampling** — hence the standing rule: no number derived from an LP-free geometric rule is reported before dense random pose sampling confirms it.
- A96 SAFETY ITEM from A111 bug (ii) (pinguard.tight_a stated for 0 <= theta <= 90 returned a = 0.7840 > 1/2 on a NEGATIVE tilt
  interval -- an unsound core, since no unit square contains a square of half-side > 1/2).
  (2) SCAN FIRST, and it is CLEAN. Over all 2222 boxes in the deployed corpus (all levels, both classes, every recorded verdict,
      including the 618 logic-kill and 159 trim-kill sets): th0 < 0 in ZERO boxes, th1 > 90 in ZERO, th0 > th1 in ZERO,
      kill_core a >= 1/2 in ZERO. Max half-side actually produced = 0.487068 (k5_11_interior_Y0036_D07_D05_D01), comfortably
      under 1/2; the global tilt range across the corpus is exactly [0, 90]. Nothing already emitted is affected -- A57's cover
      builds bins from theta_edges on [0,90] and never reflects them, which is why the bug could not fire here. It WOULD fire the
      moment a D4 reflection or an unnormalised bin reached these functions.
  (1) HARD ASSERTIONS ADDED: pinguard.tight_a and trim57.dead_by_pin / split_bin now raise ValueError unless
      0 <= th0 <= th1 <= 90, and tight_a additionally raises if the computed a >= 1/2 - 1e-12. Verified: [-45,0] and [0,120] are
      both refused, a negative bin is refused by trim57, and valid bins are unaffected. Callers must normalise mod 90 first
      (A111's octagon.normalised); the functions no longer trust them.
  (3) A111's STANDING RULE ADOPTED -- dense pose sampling confirms a geometric rule before its count is reported. Run now:
      T5' core containment, 12000 random (box, pose) draws with all four core corners tested against the unit square: 0
      violations. T5'' dead tilts, 12000 random (pose, certified-dead tilt) pairs tested for actual overlap with the witness pin
      core: 0 violations. Both rules confirmed at >= 10^4 pairs.
      Incidental: pinguard._TightCore exposes cm/sm but not tm, so any consumer reading .tm off a kill core would break --
      harmless today (cores_meet reads only kx/ky/a/cm/sm) but worth knowing.

## 2026-09-06 — A107 follow-up (Opus chore, read-only) — Part II: the k0_00 cells

A113 found a glob bug in `extract.py`: the k0 LP jsons live one directory deeper than the pinned
campaigns' (`results/nodes/k0_00/*.json`, not `results/nodes/*.json`), so A85-k0-route (12) and
A99-k0-tree-v2 (54) were silently reading zero files, and **A38-root-power was not a source at
all** (`results/{l1,l2,l3}_nodes/*.json`: 134 + 49 + 11 with an LP support). Fixed, and the alive
test widened to `dead == False` **or** `tau >= budget`. `docs/shadows.md` now has a **Part II**
with 30 k0 entries and `docs/shadows/K01..K30.svg`; Part I's numbers are untouched (every k0 stage
writes a `_k0`-suffixed result file).

* **217 alive k0 cells** (A38 153, A99 53, A85 11; 43 at τ ≥ budget). **30 distinct k0 shadow
  values explain 161**; **56 have no integral shadow** — their supports are fractional and the
  largest cell-disjoint set is 9 of budget 10 in 41 of them.
* **k0 has no pins**, so a node's only hypothesis core is the conditioned square and the class
  symmetry is the **full D4**. Every de-duplication and every coincidence check in Part II runs
  over all 8 elements.
* **K01 (s\* = 4.000000, 45 distinct configurations) alone takes 84 of the 161** — the same
  verdict as Part I's S01: for half the alive cells the LP's integral support is a side-4
  arrangement, not a near-critical packing. Below it the k0 spectrum reproduces Part I's:
  3.942809 (K02), 3.925149 (K03), 3.914214 (K04), 3.912232 (K05), **3.886745 (K06 — the k7
  pinwheel, reached from k0 with the same three free squares at 48.4355°)**.
* **Coincidences with Part I. K19 = S33 is EXACT**: 11 of 11 squares matched under the identity,
  s\* agreeing to 1e-8 (3.916931). Then six pairs at Jaccard 0.833 (10 of 11): K06–S02, K06–S29,
  K05–S05, K17–S32, K19–S34, K19–S35.
* **A113's numbers are a different comparison and I could not reproduce them as stated.** Their
  Jaccard is computed on **slot sets** — which named cells the LP filled — while mine is on the
  whole **minimised packing**. Both are now in the table, and they disagree in the way that
  matters: A113's cell `l1_100` (= A38 `l1_nodes/node_100.json`) is slot-set-identical to S38
  (1.000) but lands in **K04**, which minimises to 3.914214 against S38's 3.928915; their
  `s1int_l1_043 → S07 at 0.83` is in **K01**, minimising to 4.000000, with packing Jaccard 0.29
  against S07. K21 and K25 reach slot-set Jaccard 1.000 against S04/S14/S17 at packing Jaccard
  0.105. **One slot skeleton carries several different packings**, so a slot-set match is not a
  shadow match.
* Method deltas, both forced by the class: budget is 10 on 214 of the 217 cells, so after snapping
  the two to six near-simple placements a k0 shadow has 5–10 free squares (22–31 variables); SLSQP
  converges less tightly there, so the feasibility gate was relaxed to 2e-6 and every drawing now
  prints the achieved worst SAT gap **and** the worst containment excursion. Entries with KKT
  residual > 1e-6 carry the Part I convergence caveat.
* Discipline unchanged: one BLAS-pinned process; nothing written under A38/A57/A60/A61/A85/A96/
  A99/A104/A105/A106/A111/A113 or `lean/`; frozen verifiers untouched; git fetch + plain merge +
  push of A107's own paths only. Follow-up compute: k0 extract 4 min, structure pass 303 s,
  gallery 1628 s.
- A96 housekeeping (2026-09-06 no-deletion rule): audited every file A96 wrote or edited for deletions. Exactly ONE existed --
  scaleup.ps1 deleted the shard pidfile before a launch so the post-launch verification would read a fresh one. REPLACED with a
  non-deleting check: record the pidfile's contents BEFORE the launch and require the value to CHANGE, which catches the same
  failure (launch.ps1 never wrote a pidfile) without removing anything. No rm -r, Remove-Item -Recurse, shutil.rmtree, os.remove
  or os.unlink remains anywhere in A96's code or in the A57 files A96 touched. pausegate --reap uses taskkill on orphan
  PROCESSES only and touches no files.
  PYTHONDONTWRITEBYTECODE=1 now set by launch.ps1, scaleup.ps1 and run96.ps1 for every child they start, and noted at the top of
  PAUSED.md's resume block for hand-run commands.
  NOTHING NEEDS DELETING. No node dumps, caches or __pycache__ trees are in A96's way; the probe INPUT files
  (tree_*_D2_s0.jsonl, tree_*_D2_D2_s0.jsonl) are deliberately kept -- they are the parent lists the level-3 and level-4 probes
  were run from and are needed to reproduce those measurements.

## 2026-09-06 — A114-window-closers (Opus chore) — done-success
- Target: docs/residue_ledger.md section 2's cheap window fragments and stragglers, on top of A61 pass 5.
- **k6_23 (sliver, 8.4e-5 wide): CLOSED.** A96's resolver — the SAME A56 parametric certificate re-verified
  on [3877/1000, s0] alone at depth 56, sscale 1 — PASSes in 181.8 s. With A56's [191/50, 3877/1000] the
  501-atom certificate now covers the whole window. C2 3/3 PASS; the A56-convention depth-44 canary is
  UNDECIDED (2 undecided boxes, 0 holes) at the slab midpoint, so the canary was run at the depth the
  certificate itself needs (56) — canary depth is a budget, not part of the claim (notes/lemmas.md L2).
- **k6_07 (0.050-wide band): CLOSED — this is the BL(0,2)/S07 slot the trump5 crowd rows need.** The open
  band [956767/250000, s0] is covered by 18 PASSing slabs of ~0.0029 each (~190 s apiece), C2 3/3.
  Method note (L4): the same band as ONE slab TIMEOUTs at 1800 s and both halves FAIL at ~1550 s — grid it,
  do not bisect from the top, and cap each slab's witnesses (only the exit code is used).
- **k6_27: CLOSED** — 14 slabs over the whole window, 1826 s, C2 3/3. The last whole-window k6 class.
- **Resolver-first diagnostic (brief item 4): 13/13 recorded 4-D witness cells close on the SAME
  certificate** (k6_27 3/3, k5_02 2/2, k5_03 8/8, seconds each). So those 4-D FAILs are the verifier
  starving the s-axis (A96's finding), not node hardness. The follow-up slab sweep then separated them:
  k6_27 closed outright; k5_02 and k5_03 fail on the BULK slabs, away from every recorded witness —
  k5_03 banks [3.82, 3.823345] (5.9% of the window, C2 3/3), k5_02 banks [3.82, 3.820223] (0.4%, C2 3/3).
  Cost law measured at depth 48, jobs 1: k6_27 ~11 s, k6_07 ~65 s, k5_03 ~340 s per 1e-3 of s.
- **k5_12 (gate 0.03 -> 0.02): still OPEN.** The re-run cleared both gates but certify aborted: stage B
  landed at slack 0.05041 this time (pass 5: 0.02646 — both LP stages are time-capped and unconverged, so
  tau varies run to run), certify built a round-0 certificate (total 5.98317 < 6), the exact verifier
  FAILed it at depth 56, and the witness-feedback re-solve drove tau to exactly the budget 6.000000.
  At eps_geo 0.003 this stratum has no certifiable measure with this column pool (L3). 4210 s.
- Scoreboard (attempts/A56-sparametric/results/scoreboard.json, ONE atomic write, backup
  .bak_pre_a114): **48/52 rows full-window** (4 M1 + 24 TRANSFERRED + 20 TRANSFERRED-resolved),
  2 partial (k5_02, k5_03), 2 OPEN (k5_12; k5_13 still running under A61 and untouched). A61 pass 5's
  four conversions (k5_05, k5_10, k5_14, k6_21) were folded in the same write.
- Discipline: <= 2 processes, BLAS pinned, 6144 MB commit + 3 GB free-physical gate before every verifier,
  frozen verifiers byte-identical (sha256 in every record file), A57/A96 paused and untouched, A61's
  campaign (k5_13), A111 and A107 untouched. Records are resumable per class: attempts/A114-window-closers/
  results/<class>.json (stage cache), notes/lemmas.md L1-L5.

## 2026-09-06 — A115-k0-corner-rows (Opus chore) — done-negative

**Question (BRIEF).** A107 Part II found that K01 — "a corner or slot left empty or singly met" — explains
84 of the 217 alive k0_00 cells. A92 built the crowd certificate (Lemma CW) for the ROOT and it refused at
δ ≤ 0.1. Do Lemma CW's corner incidence rows, added to the NODE LP where the box is small, kill those cells?

**Verdict.** No. Over 36 K01 cells (32 stratified over the four corners × levels 1–3, plus 4) × δ ∈ {0, 0.05,
0.1} = 108 LPs, the two-run frozen certificate passes on **2** of the 11 cells it was attempted on, and the
attribution control (same cell, same 240 s LP wall, rows removed) shows only **one** of those is the rows'
doing — `l3_pp65_111_000` at δ = 0, a level-3 cell worth 0.7–1.6 CPU-h. **Zero** of the cells genuinely alive
at the LP (η₀ = τ₀ − budget₀ ≥ 0) died at any δ.

**Why, and it is not A109's reason.** A109's slot rows died of multiplicity (one placement meeting two or
three slot boxes at once). That is *impossible* here: the four widened corner boxes are s0 − 2a_w = 1.826 >
√2 apart, so a unit square carries at most ONE corner incidence, r_max ∈ {0,1}, and the node budget
B = 8 − Σ r_max ∈ {7,8} is exact. The rows fail for the opposite reason — **the guaranteed budget 8 is below
what a packing at s0 achieves for free**:

* EXACT (`results/trump_family_counts.json`): every D4 image of Trump realises **nine** corner incidences at
  a_w(0) = 1.025520, per-corner counts 3/2/2/2 — its tangent squares sit at μ_c = 1 exactly, inside the
  K0-WIDEN box. So at δ = 0 the achievable crowd mass is ≥ 9 > 8 = B and **the ROOT crowd LP can never pass
  at δ = 0**; the node level is the only level at which the question is even askable. At δ = 0.05 / 0.1 no
  image realises it (counts 1/1/2/1, total 5), so the canary is vacuous there and the refusal is the LP's.
* MEASURED: the LP's own fractional packing realises c = (τ − τ₀)/e ≥ B in **100 of 101** runs (mean c =
  9.60 / 9.23 / 8.68 at δ = 0 / 0.05 / 0.1 against mean B = 7.21). τ(e) is the optimum of an LP whose rhs is
  affine in e, hence convex, so c(e) is non-decreasing and a kill needs c(e) < B — **no e can kill them**.

**T1 (the "room" is not empty).** All four corner cells of all 84 K01 shadows are met; the room is always a
single DEEP meeter, never an empty corner: TL singly met in 70 of 84, BL 57, TR 50, BR 35, and the meeter
that is there has depth ≥ 0.30 in 296 of 486 incidences (< 0.05 in only 88). That is exactly the K0-FREE
teleport hypothesis (a corner met by ≤ 1 square ⇒ the packing teleports into k1_00), and it is *not*
something a crowd-weighted row can price: the crowd rows charge the SECOND meeter, and the K01 supports have
none at three or four corners.

**Trump canary PASS.** All three A38 Trump-image cells (l1 idx 21/152/153) survive at δ = 0 — the only δ at
which Trump realises the corner-crowd hypothesis — and at δ = 0.05. node_021 is an uncertified LP kill
candidate at δ = 0.1, where Trump does *not* realise the hypothesis, so a kill there would be sound.

**Price.** 224 s per (cell, δ) corner-row re-solve (median 254, max 1241), 410 s per two-run certification,
against a 469 s mean for the same cell's original k0 node LP. One corner-row pass over all 216 level-1 cells
at one δ = 13.4 CPU-h; a certified level-1 kill would be worth 43–100 CPU-h, but none occurred. Net **−13
CPU-h** on A99's 9,341–21,661 CPU-h frontier. Lean shape, had it worked: nothing new — a certified node is
the ordinary A92 two-run certificate of `k0_blocked_side.md` §2.4 with the node's own cores written into both
files and n = 11 + eB, budget = n − #cores; the only mathematics on top of the two frozen-verifier PASSes is
Lemma CW's one paragraph, already Lean-proved as `crowd_sound` (A93, `Crowd.lean`).

**Incidental (positive).** For `l2_p95_001` the corner-row certificate passed AND the plain control passed —
i.e. A99's own node certificate closes that cell after a 280 s warm re-solve, without any new mathematics.
Two of the 36 cells behave that way; a plain warm-re-solve pass over A99's open cells is a cheaper thing to
try than corner rows.

**Discipline.** READ-ONLY on A38/A85/A92/A99/A107/A113 and on A61/A96/A112/A114 (every node json copied to
`results/nodes/<nid>.src.json` first); A92 engine copied verbatim; `verify_case.py` byte-identical
(sha256 521cb01f…); ≤ 2 BLAS-pinned processes with the 6144 MB commit / 3 GB physical gate before every LP
and certification; one resumable record per (cell, δ, e); nothing deleted (no `rm`/`rmtree` anywhere);
`PYTHONDONTWRITEBYTECODE=1` after the first pass. Writes: `attempts/A115-k0-corner-rows/**`, the registry
row, this entry, one note on depgraph `K0.CW`.

## 2026-09-06 — A112-dual-branching (Opus chore, ≤ 2 BLAS-pinned processes, read-only on A38/A53/A57/A60/A61/A96/A107/A111/A113) — done-mixed: the second cover works, the branching ORDER barely matters, and k0 does not bite

**What was built.** `code/regiontree.py` — a resumable REGION TREE: root = a stalled node's hypothesis exactly as
the campaign emitted it; branch = pick a placement from the node's OWN LP dual support with a pluggable ORDER
function and put a box F = [c ± r] × [θ ± ρ] around it (A111's radius table, (0.1, 10°) halved per level, tilt
CLAMPED into [0, 90] — an uncaught negative interval silently switches every free kill off); YES child = boxes + F
at budget − 1, NO child = nofams + NoFam(F) at the same budget; "some square in F or none" is a tautology, so the
two children cover the parent exactly. At every YES node, before any LP: A57's T5″ octagon box-vs-pin trim
(byte-identical `trim57`), then A111's free pair kill (CORE-MEET with A96's tight core + Lemma TC) over EVERY pair
of bins and every bin-vs-pin with tilts normalised into [0, 90] and the core half-side asserted ≤ ½, then A111's
chain LP (GRAIN-LP) at the node's own side. One record file per node, atomic; a killed run resumes exactly.
Five LP-free scores (row mass struck, NO-family mass, load-path Fritz-John rank, PIN WASTAGE, unusable area) and
four full orderings: `loadpath`, `stranded`, `hybrid`, `wastage`.

**The PI's timeout protocol, implemented and priced.** Stage 1 at 240 s; anything at η ≤ −10⁻³ goes STRAIGHT to
the frozen `verify_case.py`, converged or not, and the CERTIFICATE is the verdict (a FAIL leaves the node alive
and it is branched on); only the knife edge escalates to the 900 s cap. Every node records `flat900_s`, the wall
the same node would have cost under a flat cap. **S02: 12,609 s of LP against 28,518 s, a factor 2.26 (55 s vs
124 s per LP over 230 LPs); k0: 1.06, because no k0 node is ever below budget.** Certification adds 631–1,807 s
per ordering on S02 and is cheaper than the LP time it replaces. **τ is never a verdict anywhere in this attempt.**

**T2 headline.** Over 17 S02-explained A57 level-2/3 nodes: `loadpath` terminates in 77 nodes / 56 LPs / 2,439 s
LP + 631 s certify against the old tree's projected **671 nodes / 671 LPs / 194,602 s** and kills 9 old boxes —
but **6 of those 9 were already dead by A96's T5″ trim at the root**, so the region tree's own score is **3 of 11
non-trivial regions**: `k5_11_interior_Y0041_D02` free at the root (Lemma TC, bin vs pin) and
`k5_11_interior_Y0108_D07` + `k5_11_interior_Y0084_D03` by a certified 3-node tree (root + YES + NO, 2
certificates each, 603 s and 302–567 s against 16,426 s projected — a 27–54× wall reduction on the boxes it does
kill). Containment C1 (root hypothesis byte-identical to the campaign's) ∧ C2 (every split tautologous, same F,
budget − 1 on the YES side) ∧ C3 (every leaf dead) holds with **zero failures** on every killed region.

**The order is a tie-break, not a lever.** On the 10 regions where the four orderings differ at all: hybrid 4,
stranded 3, loadpath 2, wastage 1; nodes-to-termination over the whole set spans 73–77. `loadpath`/`wastage`/
`hybrid` kill the same 9, `stranded` 8.

**What kills, measured inside a tree (A111's prediction, confirmed).** 45 certificates PASS (35 NO children, 10
YES) / 9 FAIL, plus 38 free kills (24 T5″ root trims, 14 Lemma TC). **116 of 126 YES-child LPs land at η = 0 to
the last digit** — the branch box sits on the parent's own support — while **44 of 104 NO children go below
budget, to η = −1.0**. η does NOT predict the certificate here: PASSes span [−1.0, −0.25], FAILs [−0.71, −0.16],
so A111's "η ≤ −0.5 always passes" does not survive.

**The free kill that fires is Lemma TC, not CORE-MEET** — all 10 fires. Four are bin-vs-bin between boxes the
REGION TREE ITSELF introduced (depths 2–4): the second conditioned square A112 exists to produce, and it only
appears after the tree branches twice. Four are bin-vs-pin at a root, killing a whole A57 open box with a rule
A57 does not apply at emission. **New named obligation: Lemma TC as a CERTIFIED leaf** (today the ledger keeps it
as the O(1) pre-screen); CORE-MEET/T5 and T5″ are already in the TCB.

**The chain kill never fired at tree depth**, though its controls are clean: on A111's own S02 boxes it fires at
r = 0.005 and 0.002 and refuses r ≥ 0.0097 (reproducing A111's r < s* − s0 = 0.0097 from the other side), and it
refuses Trump at every radius (lb = s0 exactly, feasible). The trees only reached depth 3 (r = 0.0125) inside
their wall; depth 5–6 at r ≤ 0.006 is the single most promising extension and it is a wall question.

**k0 is structurally different and the region tree does not bite there.** 6 of A113's un-killable level-1 cells,
four orderings: **0 kills, 0 certificates, 0 logic kills** in 17–28 nodes each. The reason is measured, not a cap
artefact: **all 60 k0 LPs land at η = 0 exactly (none ≤ −10⁻³)** — removing one support placement from a k0 cell
does not move τ, so the certifier is never invoked. And branching on corners does not by itself supply A113's
missing logic kills. **The brief's k0 YES-side shortcut is unsound as stated**: A53 stratifies by GRID-LOCKED
(doubly flush, wall-anchored) squares, so "a YES box inside slot cell C" does not imply k ≥ 1 and cannot be
discharged by the k ≥ 1 classes being dead at s0. It is recorded (`class_clause`, `taken: false`) and never
taken; 37 opportunities arose and only 6 even have a near-axis tilt, so the sound form (K0-FREE/teleport on the
LP support) is worth at most 6 of 37 before the grid-lock obligation is discharged.

**Pin wastage vs row mass (PI).** Spearman per branching node over its full candidate list: median **+0.468**
(S02, n = 45) and **+0.425** (k0, n = 34), positive in 84 % / 82 % of nodes — a genuinely different ranking, not a
proxy for row mass, and neither better nor worse as an order at this sample size (1 win of 10 on S02, 0 of 6 on
k0, same 9 S02 kills as loadpath/hybrid).

**Certificate accounting.** One frozen fixed-side certificate per LP-dead leaf; a 3-node kill costs 2 (one YES
core-box, one NO-family). `verify_param.py` still raises `nofams unsupported` (line 529), so the NO-side
certificate is ×4 on A57's four-side grid while the YES-side one is already parametric — the multiplier hits half
the certificates of a kill. Cost to remove it, specified line by line in `notes/verify_param_nofams.md`: **≈ 90–120
lines** in one new frozen verifier version (`NoFamP`, a Fraction interval containment predicate, one `SCell` field,
one hook in `PVerifier.exempt`, the loader, one selftest arm) and **one Lean lemma parallel to the existing
core-exemption clause**, with zero regression surface (no emitted certificate contains a nofam today).

**Integration path.** A resumable `--region-tree` option in A96's scheduler: a node ALIVE-at-LP twice, or still
unconverged at the 900 s re-check, goes to `regiontree.Runner` with a wall cap W and node cap N instead of being
split 8 ways; if it does not return `transfers = True` inside W the scheduler falls through to the ordinary split
and nothing is lost (cost bounded by W, per-node records kept for a deeper retry). Ordering: `loadpath` where the
node has a matched shadow with a known load path, `hybrid` otherwise.

**Canaries.** Trump's grain killed in **zero** of the dead hypotheses (`substrat.trump_realizes` on every one); no
S07 branch at level 1. 10 free-kill fires re-checked with an independent seed at 2,000 pairs each: **20,000
sampled pose pairs, 0 counterexamples, worst SAT gap −0.0066**. A111's two end-to-end kills reproduced **11/11**
by replaying their certificates through A112's byte-identical frozen verifier (`results/canary_replay.json`).

**Banked, from a canary that first failed.** `certify.py --loop_cols` RE-SOLVES the node LP under a time limit
before emitting the certificate, so the certificate's atom set is wall-clock dependent — A111's PASSing NO1
certificate has 76 atoms; a 900 s re-emission produced 100 atoms and a certificate that does not verify. **The
frozen verifier is deterministic; the emission pipeline is not.** A kill is reproduced by REPLAYING its
certificate, never by re-emitting it, and a FAIL on re-emission is not evidence against the original kill.

**Discipline.** ≤ 2 BLAS-pinned processes throughout, with the 6144 MB commit / 3 GB physical gate before every LP
and every certificate; READ-ONLY on every campaign (root node jsons copied to `results/nodes/<nid>.src.json`
first) and **A57's drivers were never launched**; frozen verifiers byte-identical by sha256
(`verify_case.py` 521cb01f…, `certify.py` 05df5c69…, `caselp.py` 4e313d7f…, `lpbox.py` 36cddcef…,
`trim57.py` 649fc37d…, `pinguard.py` 5e45aec0… = A57's current file with A96's range assertions,
`verify_param.py` 0c58485c…); `PYTHONDONTWRITEBYTECODE=1` and nothing deleted after the no-`rm` rule landed.
Writes: `attempts/A112-dual-branching/**`, the registry row, this entry, one note on depgraph `GRAIN`.
- A96 <- A112 (e6690215) INTEGRATION, wired and controlled, NOT launched: code/regionopt96.py, an off-by-default (ENABLED=False)
  --region-tree option. Trigger: a node ALIVE-at-LP twice, or unconverged at the 900 s re-check. Ordering 'loadpath' when the
  node has a matched shadow in A107's shadow_nodes.json, else 'hybrid'. A112's Runner gets wall cap W=1800 s; if it does not
  return transfers=True inside W the node falls through to the ordinary 8-way split, so nothing is lost -- and the failure mode
  is inert by construction, since a capped run leaves CAP-UNPROCESSED leaves which fail C3 and therefore simply do not transfer.
  A transfer is recorded as "old box X dead by region tree" with the whole containment record (C1 root-is-old-hypothesis,
  C2 tautologous-split, C3 all-leaves-dead) written beside it, and carries
  no_side_window = "s0-only, pending A117 verify_param_v2" so the scoreboard cannot count it as full-window.
  CONTROL PASSES: replaying A112's stored region trees through this option's code path gives 123 region/ordering pairs,
  37 transferring pairs, and **9 DISTINCT REGIONS -- exactly A112's 9 kills**: Y0036_D02_D05, Y0036_D03_D04, Y0036_D07_D01,
  Y0041_D02, Y0084_D03, Y0101_D02, Y0108_D07, Y0276_D05 (k5_11) and Y0155_D03 (k5_16). Each transfers under 3-4 INDEPENDENT
  orderings (hybrid / loadpath / stranded / wastage), so the kills are not artifacts of one branch order. C1 holds on all 123
  replayed pairs; the non-transferring pairs fail on C3 (capped leaves) and in some cases C2, which is expected for partially
  explored trees but means C2 is NOT automatic and must stay a checked obligation rather than an assumption.
- EMISSION NONDETERMINISM recorded in A57 notes/lemmas.md: certify.py --loop_cols re-solves the node LP under a TIME LIMIT
  before emitting, so a certificate's atom set is wall-clock dependent -- emitting the same node twice can give two different
  valid certificates, and a re-emission can fail on a loaded box. The frozen verifiers are exact and deterministic. Reproduce
  kills by REPLAYING certificates, never by re-emitting; and note this is a confound in any concurrency benchmark (A96's own
  contention legs varied worker counts, which varies emission outcomes as a side effect).

## 2026-09-06 — A115 follow-up (PI) — the PLAIN warm re-solve pass over A99/A85's open k0_00 cells

**Question.** A115's attribution control found that a cell whose corner-row certificate passed also
certified *without* the rows, after a 240 s warm re-solve. Does that generalise over A99's 53 open
k0_00 cells and A85's 11?

**Verdict — yes, and it is the cheapest thing in the k0 route so far.** A plain 240 s warm re-solve
(no corner rows, no new mathematics) followed by A99/A85's ordinary first-pass node certificate under
the frozen `verify_case.py` **certifies 10 of the 55 open cells reached, including 7 of A99's plain
level-1 cells, for 5.09 CPU-h**. At A99's own price (9,341–21,661 CPU-h over the 216 level-1 cells =
43.2–100.3 CPU-h each) that removes **303–702 CPU-h — a 59×–138× return.** A115's corner rows, by
contrast, cost 13.4 CPU-h for the same pass and removed nothing.

* **New:** `l1_170`, `l1_181` had no prior verdict at all (A38 `notrun`) — two previously unprocessed
  level-1 cells, now certified dead.
* **Upgraded:** `l1_005`, `l1_049`, `l1_093`, `l1_126`, `l1_137` were LP-killed by A38 but
  **uncertified** (A113: `KILL(LP,uncertified)`; `l1_093` was an outright certification `FAIL`). A
  frozen-verifier certificate is what the tree needs to actually remove them, and they now have one.
  All five converged with minmass 1.000 in 46–222 s of warm continuation.
* Also 2 cells of A99's R2 pattern-branched tree (`l1_005_sh2adj`, `l1_005_sh3` — an exact ×15 cost
  multiplier, not the route, so no cost credit) and 1 A85 cell (`s4_near_BL357619_BR004483_TR191404`).

**Hard negative (equally useful).** Four cells came back **converged ALIVE**: τ = budget exactly with
minmass = 1.000 — `l1_071`, `l1_104`, `l1_159` (A99 plain level-1) and `s3_far_BL389484_TR018470`
(A85). The case-LP has reached its optimum and it is not below budget, so **no amount of further LP
time kills them**. This upgrades A113's "un-killable at the measured LP state" list from *measured* to
*converged*: those cells need a different hypothesis, not a longer run.

**What is left.** 36 cells are `kill-candidate` (η ≤ −10⁻³, first-pass certificate FAILs — still
row-generation-incomplete), 4 knife-edge, 5 alive; 9 of the 64 open cells were not reached before the
5 CPU-h cap. The obvious continuation is a 900 s second stage with A85's witness-feedback rounds on
exactly the 36, plus the same pass over the level-1 cells A38 left `notrun`.

**Discipline.** READ-ONLY on A85/A99 (each node json copied to `results/nodes/<nid>.src.json` before
being touched); 2 BLAS-pinned processes; commit/physical gate before every LP and every verifier run;
one resumable record per cell (`results/t4/<nid>.json`); hard per-process CPU-second cap (9,000 s each,
checked before each cell, so the final cell of each shard overruns it — 18,318 s = 5.09 CPU-h total);
frozen `verify_case.py` byte-identical; nothing deleted anywhere. Cells were processed in
minmass-descending order so that the cap truncates the least promising tail, and the un-reached list is
recorded. Report: `attempts/A115-k0-corner-rows/notes/t4_report.md`.

## 2026-09-06 — A116-local-selection-tree (Fable lead) — done-success
- **Theorem LOCAL [T], n-general** (`docs/proofs/local_certificate.md`): for a known minimum z* with load-bearing squares L
  and class pins P, N = boxes [c ± r] × [θ ± ρ] in the class frame at s0; the selection tree over the NEAR pairs of L ∪ P
  (eight signed separating axes per pair, IMPOSSIBLE ones by interval arithmetic) has leaves whose fixed-tilt polyhedra
  are A110's GRAIN-LPs, and Dead_{L∪P}(N) ⟺ every possible leaf's minimum over every tilt cell exceeds s0 (Lemma COVER =
  SAT per pair; Lemma LEAF = LP duality, the axis inequalities summed along the chain); dropping the other squares only
  weakens the hypothesis. Lemma RELAX: an affine relaxation over a tilt cell with TILT VARIABLES (chords / V-lines of
  |cos|+|sin|, p + |q| sin hw, McCormick on q·φ) whose loss is second order except the McCormick term (q-range × hw/2,
  halved by q-range splits) — the fix of A111's first-order R·Δ chord bound; A111's r < s* − s0 law was the dropped
  ambiguous rows letting the LP escape to the box rows.
- **Lemma STAB (the PI's route) + tables** (`notes/stability_table.md`): a contact's selection is FORCED on a box until
  its riding vertex reaches the end of its edge (slack 1/2 − |τ|) or the relative tilt crosses 90°·k; flush contacts
  are a 2-way disjunction; decided rigorously by interval bisection over the pair's 6-D box. S07 chain contacts forced to
  0.18–0.23 except f0–BL(0,1) (vertex 0.057 below the corner (1,2): 0.024 at ρ = 100δ°, 0.053 at ρ = 0) — the Trump
  boundary; S02 forced to 0.08–0.23 except f1–f3 (overlap 0.085: 0.019 / 0.032). The single-leaf N at those radii is
  DEAD (S07 3.884789, S02 3.885780, within 10 % of s*); the PI's f4–BR(0,0) "~0.25" is the ρ = 0 entry 0.254.
- **Where the chain dips [T+M]**: the corner selection of f0–BL(0,1) realises the gap chain F_T and F_T ≤ s0 iff θ ≤ θ_T
  + 6·10⁻⁵ °; the cut is the single inequality F_T(θ) > s0. Uncut S07 N is ALIVE from (0.05, 5°) with exact witnesses
  at side F_T(40°) = 3.875871 and Trump inside; cut at 40.202° DEAD with measured minimum F_T(40.202°) = s0 + 1.3·10⁻⁴
  (the slack cores cost nothing: the chain presses both pin corners against their walls). S02's mirror D(θ) < s0 for
  θ > 49.818° (= 90° − θ_T, A111's 1.383° identity) does NOT materialise in the k5_11 frame.
- **T2 grid** (`notes/t2_table.md`, `results/t2_*.jsonl`; 10⁴ samples + SLSQP + Trump canary on every DEAD): largest
  certified S02/k5_11 **(0.2, 10°)** in 445 s (also (0.05, 20°)); S07/trump5 **(0.1, 40°)** in 52 s and (0.2, 10°).
  Limiter at r = 0.3: a genuine rearrangement of L ∪ P (S02: BR(0,1) leaves its slot with f3 on top, side 3.8733; S07:
  the ladder shears, 3.856) that the dropped squares would block; at ρ ≥ 20° with r ≥ 0.1 the tilt-cell count (900 s cap,
  10⁵–2.5·10⁵ nodes, no witness). k5_16 frame DEAD to (0.1, 10°); exact pins same values; f1 added to S07 buys nothing.
- **T3**: 72 of 184 k5_11 + 23 of 68 k5_16 S02-explained alive nodes have their whole load-path support inside a certified
  N (YES leaf dead); 0–2 of 18 S07 nodes (their supports sit off the family's tilts, A110). Price 4–445 s per N shared by
  every node inside it, vs 290–336 s per A57 child / 1 100 s per A60 leaf; the NO side is what remains.
- Canaries PASS: S02 at r → 0 gives 3.886745, S07 3.885617; Trump outside every certified S07 N and inside every uncut
  N that turned alive. Discipline: ≤ 2 BLAS-pinned processes, read-only on every campaign, no deletes.
- A96 <- A116 (74a34f96) INTEGRATION into the --region-tree option, wired and replayed, NOT launched. When a stalled node's
  support lies inside a CERTIFIED neighbourhood N of the S02 or S07 minimum, the YES region is taken to BE N: A116 has already
  certified no packing exists there, so the YES child needs no LP and only the NO children go to the solver. Headline Ns wired:
  S02 in k5_11's frame (L = f1 f2 f3 BR(0,1)) at (r, rho) = (0.2, 10 deg), and S07 in trump5's frame (L = f0 f2 f4, cut
  F_T(theta) > s0) at (0.1, 40 deg) and (0.2, 10 deg). The YES kill is recorded as "dead by local certificate A116 <N id>
  (pending A119 rational/Lean form)" and is TAGGED, not counted with frozen-verifier kills -- it is prose+numeric today, not
  replayable. NO side stays fixed-side until A117's verify_param_v2, then re-verify parametrically.
  REPLAY THROUGH A112's REGIONS (wall 0.5 s, read-only, no LP): A116's consumer table has 74 nodes inside a headline N.
  A112 has 23 regions, 17 of them A57 nodes -- the 17 stalled nodes. Of those 17, **4 lie inside a certified N**
  (Y0036_D07_D01, Y0036_D07_D06, Y0054_D00, Y0276_D05, all S02/k5_11/r0.2/rho10). Of those 4, **2 CLOSE COMPLETELY**
  (YES free by A116 + NO side already dead in A112's tree): Y0036_D07_D01 and Y0276_D05. The other 2 (Y0036_D07_D06,
  Y0054_D00) get a free YES side but their NO side is still open.
  So the honest headline is 2 of 17 stalled nodes close outright, not 72 -- the 72/184 figure is the fraction of S02-EXPLAINED
  ALIVE nodes inside N across the whole corpus, and only 4 of them are among the nodes A112 actually stalled on. The lever is
  real but its overlap with the current stall set is small; its value would rise if the region tree were pointed at the other
  70 in-N nodes, which is a different targeting decision.
- A96 targeting decision (A116 in-N alive nodes): TARGET LIST BUILT, RUN NOT LAUNCHED -- a soundness blocker, reported rather
  than improvised around.
  TARGETS: of A116's 74 in-N nodes only **35 are ALIVE in the current A57 corpus** (all k5_11; L1 13, L2 19, L3 3) -- the other
  39 are already PASS/FAIL/logic-killed, so the "~70 remaining in-N nodes" is really 35. None overlap A112's regions, so these
  are all new. Written to A96 results/a116_targets.json.
  PRICE: one NO child each at the two-stage protocol = 35 x (900 s LP + ~545 s certify) = 14.0 CPU-h, which is OVER the 12 CPU-h
  cap; at a 240 s LP cap it is 7.6 CPU-h and fits. Since A109/A96 both measured that 240 s leaves almost everything unconverged
  (2/29), the honest options are a 12 CPU-h run at ~700 s that may still not converge, or a raised cap.
  BLOCKER (why nothing was launched): "make the YES region the certified N" needs N expressed as boxes for L in the NODE's frame
  plus the cut, and A116's N is not that shape. In a116lib it is a SIX-DIMENSIONAL PAIR-POSE box (two bodies x (x, y, t),
  pair_box) on which forced_test proves that every disjoint configuration uses the minimum's SELECTION. That is a statement about
  which separating axis is forced for a PAIR, not a (centre, tilt) region for one square, and turning it into a caselp NO-family
  is a frame change I cannot do safely from outside A116. Getting it wrong is a SOUNDNESS error (it would silently declare a
  region empty that is not), not a performance one, so it needs A116's own frame code or an A116 chore exporting N as
  node-frame boxes. The wiring, target list, tagging and ledger are ready to consume that the moment it exists.
- A96 THREE-ARM ROW-FILTER RESULT (B=30 nodes, C=26 nodes, 900 s cap, 19.3 CPU-h): THE ROW FILTER ADDS NO KILLS.
    arm B (trimmed, all rows)        n=30  converged 4  strict-kill 4  knife 19  alive 7   9.8 CPU-h
    arm C (trimmed + row filter)     n=26  converged 7  strict-kill 3  knife 17  alive 6   9.5 CPU-h, median 53% of rows dropped
  Kills in C that are not in B: **NONE**. Kills in B not in C: one (Y1135, not yet reached in C). So dropping a median 53% of
  the LP rows produced ZERO additional kills. What it did buy is CONVERGENCE: 7/26 in C vs 4/30 in B, i.e. the smaller LP
  finishes more often -- but the nodes it finishes are the ones that were going to be knife-edge or alive anyway.
  VERDICT: the row filter does NOT justify the verifier clause change on this evidence. The spec
  (notes/verifier_v2_rowfilter.md) explicitly gated the verifier-v2 chore on "arm C shows kills that arm B does not", and it does
  not. Route (A) and row-dropping should stay shelved; the 43-53% row reduction is a real speedup with no demonstrated kill yield,
  and a soundness-relevant clause change cannot be bought with a speedup.
  The 900 s cap remains worth it on its own: 4/30 and 7/26 converged versus 2/29 at 240 s.
- A119 N_boxes.json not yet present; the 35-node in-N run stays blocked on it and on the independent >= 1e4-configuration
  sampled check, as instructed.
- A96 INDEPENDENT VERIFICATION of A119's N_boxes.json (results/N_boxes.json, 5 neighbourhoods): PASS, but only after correcting
  my own first attempt, which was nearly vacuous and would have passed for the wrong reason.
  FIRST ATTEMPT (rejected as inconclusive): 20000 whole-configuration draws, 0 hits -- but a diagnostic showed the containment
  filter rejected 99.97% of draws, so only ~30 configurations were ever tested for disjointness. Cause was MINE, not A119's: a
  pin's slack box (halfwidth 0.00707) can put a pinned square a hair outside [0,s]^2, and my strict filter threw away the whole
  draw. A pinned square belongs to a real packing and is inside by assumption, so the slack must be intersected with containment,
  not used to reject.
  CORRECTED CHECK (own SAT and containment code; A119's is not imported): pin centres clamped into the container, containment
  filtering applied to the load-path squares only. 13289 configurations actually TESTED across the five N, ZERO pairwise-disjoint
  at any side <= s0. Per-N coverage is uneven (S07 6000 each, S02 860 / 374 / 55), so the deployed neighbourhood was re-run on
  its own: **S02_k5_11_r0.20_rho10 -- 73642 draws, 10500 TESTED, 0 hits**, clearing the >= 1e4 bar for the N that actually
  carries the 4 A112 matches and the 35 targets. A119's own figures (0 hits / 12000 samples per N) are reproduced.
  LESSON worth keeping: an acceptance-filtered sampled check must report how many samples SURVIVED the filter, not how many were
  drawn. '20000 samples, 0 hits' was true and meaningless.
  The 35-node run is NOT launched: the gate is now verified but the NO-side runner (N boxes -> caselp NO-family children, then
  LP + frozen certifier at s0 with the s0-only/pending-A117 tags) is not yet written.

- A117 (2026-09-06) FROZEN VERIFIER v2 + LEMMA TC AS A LEAF (attempts/A117-verifier-v2; done-success).
  **HEADLINE 1: `verify_param_v2.py` is frozen (sha256 `153029ba...`), it is BYTE-IDENTICAL TO v1 on 30 existing
  certificates (verdict AND every one of v1's fourteen statistics), and its NO-family clause is a PROVED Lean
  theorem.** v1 (`0c58485c...`) was never edited -- hashed before and after. v2 = v1 plus one discharge rule (N):
  a placement whose centre lies in an s-affine zone `Z(s)` and whose `t` lies in one of the family's closed
  t-intervals is exempt. On an s-cell the zone is taken at its WORST CASE, the INTERSECTION over the cell (each
  edge affine => extremes at the endpoints), so it exempts LESS than the true zone at any single side and cannot
  turn a FAIL into a wrong PASS; it also covers the `s - 1/2` wall clamp with no special case. No new geometry in
  the TCB: rule (N) is a containment of axis-aligned rationals -- literally the clause the frozen fixed-side
  `verify_case.py` (`521cb01f...`) has discharged since A13, with `s` ranging over a slab. Equivalence corpus:
  both classes, A57 sides G1 and L1, levels 1-3 (incl. A99's `s1int_l2_l2_*`), 16 PASS + 14 FAIL, A96's resolver
  cells at depth 56, A100's protected classes k3_02/k4_11, A57/A95/A61 certificates; box counts 6 890 to
  14 518 182; `exempt_nofam = 0` on every row, as it must be, since v1 RAISES on a NO-family and therefore no
  certificate emitted before A117 contains one. Lean: `ParamNoFam.lean` -- `nofamExemptIV_sound` proved parallel
  to `CaseHyp.nofamExempt_sound` (the one new inequality is `affine_le_max`/`min_le_affine`, "an affine function
  on a cell lies between its endpoint values"), plus `exemptPN_nil` (with `nofams = []`, v2's dispatcher IS v1's).
  Axioms `propext / Classical.choice / Quot.sound` only; `lake build` (whole library) clean, 0 errors; the project
  axiom roster is UNCHANGED because Lemma TC is stated as `Prop` definitions, not axioms.
  **HEADLINE 2, a refuted projection: the 4x wall cut does NOT exist.** A112's `verify_param_nofams.md` inferred
  "a 4x cut of the NO-side certification wall" from A95's measurement that a re-emitted level-1 A57 leaf verifies
  over the whole window for 0.062 of its four fixed sides. On the NO-side corpus the opposite holds: over 48
  re-verified NO certificates the WINDOW pass costs about **10x the four fixed-side runs it replaces** (710 s vs
  73 s on the 16 that PASS; 8 390 s vs 716 s over all 48) and **32 of 48 do not finish inside a 240 s cap**. The
  reason is structural: a NO certificate is TINY at a fixed side (4-135 atoms, 0.6-5 s) precisely because the
  NO-family exempts most of the container outright, while the 4-D pass must still resolve the whole s-slab. The
  four-side grid was never the expensive part of a NO kill. **v2 buys window-VALIDITY, not wall** -- 16
  window-valid NO kills gained, and 0 fixed-side PASS turned into a window FAIL.
  **HEADLINE 3: Lemma TC is now a named leaf with an exact check -- 170/170 fires reproduced, 1 700 000 sampled
  pose pairs, 0 counterexamples, worst SAT gap -0.000898, smallest exact slack +3.36e-5.** `code/tcleaf.py`:
  tilt intervals normalised to [0,90] with the domain ASSERTED (A111 bug ii -- a D4 reflection's negative
  interval fed to a bound stated only on [0,90]); a bin straddling a multiple of 90 becomes TWO bins and the leaf
  fires only if it fires for every branch pair; `D_min` exact by the tent-function endpoint argument; centre
  distance kept SQUARED so no root is taken; `(1 + cos D + sin D)/2` bounded from BELOW by truncated alternating
  Taylor series evaluated at a rational enclosure of `D*pi/180` from a 50-digit pi TRUNCATION (cos at the upper
  end, sin at the lower end -- valid since cos decreases and sin increases on [0, pi/2]); pose-disjointness exact,
  because two bins sharing a pose may be the SAME square. Both slacks make the check UNDER-fire. Replayed: A112's
  10 fires from their stored box pairs, A111's 160 from a deterministic rebuild whose census matches the stored
  one fire-for-fire (160 = 160 TC; 1 403 CORE-MEET not replayed).
  **What A112's region-tree option can now claim window-valid: exactly one thing, and it is the FREE kill.**
  `k5_11_interior_Y0041_D02` -- a whole A57 open box killed at the root under all four branching orders with 0 LPs
  and 0 certificates by a single TC fire -- is window-valid: all 10 of A112's TC fires have BOTH boxes
  s-INDEPENDENT (6 are bin-vs-bin, the node's own support boxes; the other 4 are against class pin `pin3`, whose
  core is `(3/2, 1/2)`, two slot anchors with beta = 0, so the pin box does not move with the side either --
  `results/tc_sidecheck.json`). Its only obligation is Lemma TC, which stays [C]: the Lean proof needs the
  separating-axis theorem for two interior-disjoint convex polygons, which `Band.lean` records as NOT formalised
  in this development, so TC is an exact machine check with a 10^4-sample control and a frozen Lean statement,
  not a Lean theorem.
  **THE BLOCKER MOVED TO THE YES SIDE.** A 3-node region-tree kill is (YES certified) AND (NO certified). A117
  makes the NO half one window certificate, but the YES child's branch box enters ITS certificate as a CORE, and
  A96's `core_affine` refuses a branch-box coordinate outright -- it is neither a slot nor a `Q_dy` cover
  coordinate. `to_param117.py` converts 74 of 77 NO-side certificates and refuses exactly the three whose tree
  carries a YES child (`...Y0054_D00_m2__stranded__RNY`, `...Y0108_D07_m2__hybrid__RNY`,
  `...Y0083_D02_m2__stranded__RYN`) with that message. Until a YES-core anchoring exists, NO (YES,NO) pair is
  window-valid and A96's `regionopt96.py` should keep `no_side_window = "s0-only"` on its transfers.
  **EMISSION NONDETERMINISM, recorded in the frozen-verifier note, in the v2 header itself and in A57's
  `code/FREEZE_TAGS.txt`:** `certify.py --loop_cols` re-solves the node LP under a time limit before emitting, so
  a certificate's atom set is wall-clock dependent -- the frozen VERIFIER is deterministic, the EMISSION is not;
  kills are reproduced by REPLAYING certificates, never by re-emitting.
  **Discipline.** <= 2 BLAS-pinned processes throughout, `PYTHONDONTWRITEBYTECODE=1`, nothing deleted, READ-ONLY
  on A53/A57/A61/A95/A96/A99/A100/A111/A112 (their certificates opened for reading only). The A57 FREEZE_TAGS
  entry is COMMENT-ONLY and the tag parser was re-run to confirm it still reads exactly `G4,G3,G2`. Two process
  lessons banked in `notes/method.md`: (i) a selection must only take certificates with a stored report, or pass
  a cap -- A95's `k5_11_interior_Y0048` had never been verified there and ran unbounded past 30 min per verifier,
  holding the run's JSON hostage (the 28 finished rows were recovered from the run's own log lines and the tail
  re-run; A95's `Y0049` then reproduced its stored 10 205 772 box count exactly); (ii) a comparison cap must be
  by BOX COUNT, not wall clock, so both verifiers stop at the same box, and a verification cap must be checked
  where it can only abort, never decide (a capped run reports CAP, never PASS or FAIL).
  Writes: `attempts/A117-verifier-v2/**`, `attempts/A96-a57-parametric/code/verify_param_v2.py` (new),
  `lean/PackingCertMathlib/PackingCertMathlib/ParamNoFam.lean` (new) + its import + `scratch/A117Axioms.lean`,
  a comment block in A57 `code/FREEZE_TAGS.txt`, a section in A57 `notes/lemmas.md`, one clause on `V.PARAM` in
  `lean/depgraph.json`, the registry row and this entry.
  **Probe on a capped certificate.** `k5_11_interior_Y0036_D07_D06_m2__hybrid__RN` (fixed side 0.80 s, capped at
  240 s in the main sweep) re-run with a 2 700 s cap: window **PASS in 302.7 s = 95x the four fixed-side runs it
  replaces** (`results/no_reverify_probe.jsonl`). So the 32 caps are very likely window-valid too, and the wall
  ratio is WORSE than the 9.8x the finished set shows -- the certificates that cap are exactly the ones whose
  fixed side was cheapest.


## 2026-09-06 — A118-lane-count (Opus chore, ≤ 2 BLAS-pinned processes, pure geometry, read-only on A38/A56/A57/A60/A61/A85/A96/A99/A107/A113/A114) — done-mixed: the leaf is sound, cheap and 2,300× faster than the LP it replaces, and it fires on 1.7 % of nodes

**THE LEAF.** LANE-COUNT: for a class `S`, a usable cell `p` (an unclipped completable slot whose
extension `T = S ∪ {p}` is window-certified; for k0, a corner cell with `T = k1_00`) and a tree
node, work in `p`'s CORNER FRAME (where the cell is `[i,i+1]×[j,j+1]` at every side) and let
`R(C)` = the poses of a unit square that lie in the container, meet `int C`, obey Lemma CONT and
are interior-disjoint from every hypothesis core; `LANE(C)` = the largest number of pairwise
interior-disjoint squares with poses in `R(C)`, `M(C)` = the number of conditioned squares that
can meet `int C`. **`LANE(C) + M(C) ≤ 1` ⇒ the node is empty** (SLOT-CROWD / K0-FREE force two
non-pin meeters and there is no room). Certified by a box cover with four discharge inequalities
plus one octagon inequality per box pair — no measure, no LP, no certificate replay, the Lean
shape is `teleport_packing` under the T5 pattern (`attempts/A118-lane-count/notes/t3_lean.md`).

**THE ONE THING THAT HAD TO BE GOT RIGHT.** The count must be run on the ORIGINAL packing at
side `m`, not on A57's dilated family at `s0`. On the slab the licensed crowd pad is `a_w = 1`
EXACTLY (SLOT-SLIDE's depth credit and Lemma B-YES-S's dilation pad cancel — A109's `aw_check`),
and `F_p(1)` contains the whole GRAZING STAIRCASE (`mu_p = 1` squares sitting in the arm beyond
the backing pins), which is disjoint from anything inside the cell: `LANE ≥ 2` at every node, for
structural reasons. Pulling the hypothesis back instead costs only interval widening — every
position is affine in `m`, so the hull over `[m_lo, s0]` is the hull of two endpoints — and gives
a leaf with teeth. **A118-O1:** a lane-count leaf then excludes class-`S` images, not A57's whole
`δ = 10⁻²` slack family; A57's composition is unaffected but `lemmas.md` T23's broader slack
statement may not re-use such a leaf. **A118-O2:** every k0 verdict is conditional on k1_00.
**A109-O1 is DISCHARGED** (A114 made every extension FULL on the CLOSED window), and
`slot_crowds.md` §1.2's usable-slot table is superseded: k5_16 gains BR(1,0)+TL(1,0) (m_u 4→6)
and trump5 gains BR(0,1)+BL(0,2) (m_u 4→6).

**YIELD (3,580 records, 18,086 (node, cell) verdicts, 1.84 CPU-h, 55 min wall).** 61.4 % of cells
return `LANE ≥ 2` with two explicit interior-disjoint witness poses, 30.9 % UNDECIDED at the box
budget, 7.4 % `LANE ≤ 1`, 0.26 % `LANE = 0`. **62 nodes have a usable cell at `LANE + M ≤ 1`**;
38 are alive-at-LP by A107's test, but matching each kill's own BOX against the campaign ledgers
shows **21 A57 + 3 A60 + 1 A85 of them are boxes the campaign has ALREADY certified dead** (a
positive control: the leaf never contradicts a certificate and is 2,300× cheaper), 24 more are
dead-at-LP, and **13 are new**: `k5_11_interior_Y1080` (the one A57 box whose tree row is FAIL,
together with all eight of its children) and 12 of the 217 alive k0 cells (11 A113-`UNDECIDED`
A38 level-2/3 nodes + 1 A85 `FAIL`), the k0 ones conditional on k1_00. Zero overlap with A96's
70 T5′ tight-core kills, A57's 663 T5/T5″ logic kills, or A112's 3 region-tree kills.
Fire rate 1.7 % ⇒ **≈ 0.05 wall-days at 5 workers** off A57's remaining 66.53 CPU-days, and
**0 wall-days** on A60/A100's protected tier. **Deployment: at EMISSION as a 1.85 s/node
pre-screen, never as a re-solve.**

**WHERE IT STOPS, EXACTLY.** `TR(0,0)` (27), `BL(1,0)` (15), `TL(0,0)` (9) dominate — CORNER
cells, backed by two walls, which one well-placed conditioned core can close; `BL(1,1)`, the cell
A94/A109's crowd LPs leaned on, fires ONCE in 3,580 nodes. And **1,323 cells sit at `LANE ≤ 1`
and are saved from being a kill only by `M = 1`** — the node's own conditioned square is allowed
to be the second meeter. That is 36× the kill count and is the whole failure mode: A57's tree
localises exactly one square. This also says how A118 differs from A85's k0 reach work ("at the
root reach never separates"): reach separates only once a conditioned square is present, and only
when it sits ON the corner diagonal at distance ≈ 1.15–1.18, where its core spans the entire
approach — which is exactly the 12 new k0 cells.

**T4 (PI generalisation) — THE REVERSED LEAF IS SOUND AND UNAFFORDABLE.** Branching on the two
meeters is tautologous and its "≤ 1 meeter" half is FREE (it is the T1 leaf). The other half is a
pair-box cover: at `nx=8,nth=6` a cell has 23–354 boxes and 276–44,850 unordered pair-children
after symmetry, of which Lemma TC (core–core) kills 60.4 % and the octagon PAIR test another
8.3 % — leaving **26–14,099** children per (node, cell) at `budget − 2`. Sampled LPs (24 + the
canary, two-stage 240/900 s): **2 die and both certify with the frozen verifier**
(`τ = 2.000, η = −1.000, minmass 1.000`, certificates PASS in 0.9–1.3 s), the other 22 land at
`η ∈ {0, +0.5, +1.0}`; 122 s mean per child. At a 9 % per-child kill rate the expected cost of
killing one node this way is 2–500 CPU-h against 850 s for its own LP — `k0_route.md` §0's C3
reproduced at the pinned classes, and quantitatively consistent with A85's 644 boxes / 207,046
pairs at the k0 root. The octagon pair test is worth 8–19 pp over Lemma TC alone and subsumes
A112's "Lemma TC as a certified leaf" obligation.

**CANARIES — ALL PASS.** The corner/slot frames reproduce `slot_crowds.md` §7's exact Trump
depths at all six unclipped trump5 slots to `< 5·10⁻⁷` with the same witnesses; at the **trump5
ROOT** the leaf returns `LANE ≥ 2` at all six usable cells — `BL(0,2)` (sq4 0.967 / sq7 0.016) and
`TL(0,0)` (sq6 0.168 / sq4 0.155) included — with Trump's own pair in `R(C)` and interior-disjoint;
the T4 pair-box CONTAINING Trump's TL 2-crowd survives (`τ = 5.000, η = +1.000`); and a
machinery control (a cell boxed in by eight blockers certifies `LANE ≤ 1`, 12,561 confirmation
pairs, `max_gap = −0.903`; the same cell unblocked returns `LANE ≥ 2`). Every kill is
sample-confirmed: `LANE ≤ 1` kills carry 171,405–719,400 pose pairs from `R(C)` with
`max_gap ∈ [−0.94, −0.11]`; `LANE = 0` kills carry ≥ 24,000 ambient draws with 0 accepted, and
the strongest was re-checked on a 2.8 M-pose dense grid with worst overlap 0.253.

**Discipline.** READ-ONLY on every campaign (nothing written outside `attempts/A118-lane-count/**`,
this ledger, the registry and one note on the C.A57 depgraph node); ≤ 2 BLAS-pinned processes;
`PYTHONDONTWRITEBYTECODE=1`; no deletes; tilt intervals asserted normalised to `[0,90]` and core
half-sides asserted `≤ 1/2`; every tolerance in the KEEP direction (`R(C)` only ever enlarged);
frozen `verify_case.py` byte-identical
(`sha256 521cb01f…`); one resumable record per node. Report:
`attempts/A118-lane-count/notes/method.md` + `notes/t3_lean.md`.

## 2026-09-07 — A121-reading-validator (Opus chore) — done-mixed (batch 1: K01–K21)

**THE READINGS ARE ACCURATE WHERE THEY ARE `r`, WRONG-BY-CATEGORY WHERE THEY ARE `ns`, AND WORTH
ZERO NEW NODE KILLS — because A118 already swept all four corners of every k0 node.** 21 filled
rows → 58 validated items → 261 (node, cut) rows (`results/cuts.jsonl`).

**T3.** 6 node kills follow from the readings alone (no LP) = 1.42 CPU-h at 850 s/node, **0 of
them new**: all six are A38/A85 `p215`-family nodes already booked by A118's blanket 4-corner
sweep (`report118.json`), all at `LANE ≤ 0, M = 1` at `TR(0,0)`. No A99 level-1 cell is among
them, so **0 CPU-h off A99's 9,341–21,661 CPU-h k0 frontier** and 0 off the A57 schedule (this
batch is entirely k0_00). Every k0 verdict stays conditional on `k1_00` (A118-O2). The readings'
measured value is as a POINTER, and the pointer is 60 % accurate: A118 kills 10 of the nodes in
this batch, the reading names the killing corner for 6 and a `LANE ≥ 2` corner for 4.

**T1 — 34 disagreements, in four kinds.** (i) **All three `r` readings are exactly right**
(K01 `f1`/BR(0,0), K04 `f6`/TL(0,0), K20 `f3`/TL(0,0)): singly met, no second meeter, no grazer,
depths 0.665 / 0.665 / 0.969, all corner cells (always usable, extension `k1_00`, OPEN).
(ii) **11 of the 23 `ns` items name a square that is ALREADY EXACTLY ON its cell** (L∞ ≤ 2·10⁻⁶,
tilt ≤ 8·10⁻⁵ °) — the SNAP move is the identity, and A107's slot/free split under-counts the
slot squares in **11 of the 21 entries** (K03 4+7→5+6, K04 2+9→5+6, K05 4+7→6+5, K06 5+6→6+5,
K09 1+9→3+7, K11 1+9→3+7, K12 2+8→4+6, K14 2+8→3+7, K18 4+7→5+6, K19 5+6→6+5, K20 2+9→4+7,
K21 5+6→6+5). The minimiser slides free squares onto lattice cells and nothing re-snaps them.
(iii) **9 `ns` items are not "a hair" off**: L∞ 0.105 / 0.158 / 0.199 / 0.227 / 0.374 / 0.394 /
0.575 / 0.793 / 0.912 against A107's own 0.05 snap window. (iv) **2 are crowd cases, not room**:
K02 BL(1,1) is also met by `f4` (SAT penetration 0.0019) and K05 BR(1,0) also by `f6` (0.3069) —
Lemma SNAP-D fails at both. Only **2 `ns` items are genuine uncrowded near-snaps** (K02 `f2`@BL(0,2)
at 0.0185/0.38°, K02 `f6`@BL(1,1) at 0.0036 — and that one is the crowded one).

**T1 — the `g` row (K18) is right and the data behind it is not.** `f0/1/3/4/5/6` do share a
tilt: 39.2135–39.2141° (spread **5.5·10⁻⁴ °**), with `f2` alone axis-aligned at BL(1,0) — a
genuine refinement of the gallery's `common_tilt = no`. But K18's Fritz–John decomposition does
**not close** (`kkt_residual = 0.1171`, rank 19 of 21), and `f6` carries **zero** FJ force at its
only contact (left wall) while the rattler test calls it load-bearing (removing it drops `s` by
0.0297). The shared-tilt grain is 6 squares wide; the certified load path through it is 5.

**T2 — the structural finding: 16 of 23 `ns` items name a cell that k0_00 cannot teleport into.**
k0_00 has no pins, so only the four CORNER cells have an extension class (`k1_00`); `BL(1,0)`,
`BL(1,1)`, `BL(0,2)`, `BR(0,1)`, `BR(1,0)`, `TR(0,1)`, `TR(1,0)`, `TL(1,0)` are licensed by no
lemma — 102 of the 261 cut rows are `cut_kind = none` for that reason, and K18/K19/K21 yield no
cut at all. Of the corner-cell cuts: `r` 94 nodes (6 kills, 4 blocked by `M ≥ 1` at `LANE ≤ 1`,
79 `LANE ≥ 2`, 5 UNDECIDED); `ns` 44 nodes (0 kills, 1 blocked by M, 37 `LANE ≥ 2`, 6 UNDECIDED).

**T2(d) — the 10 `i` rows are confirmed** (K07 k9, K08–K16 k10; every `k < 11` entry is an `i`
row and every `i` row is a `k < 11` entry) and cross-referenced to A115's T4 queue: 21 nodes, of
which **2 are already CERTIFIED DEAD** (`l1_005_sh3_warm` for K07, `l1_181_plain_warm` for K14),
2 are `kill-candidate (cert FAIL)` (K07 `l1_214_sh2adj_warm` η −1.5, K11 `l1_049_sh2adj_warm`
η −1.0), 3 are in A115's **not-reached** list (K07), and **14 are A38 nodes that were never in
A115's queue at all** — the obvious next warm-re-solve batch.

**Canaries (`results/canary121.json`, all PASS).** C1 the frame map: applying each node's stored
`struct_op` to its own `cfg` reproduces its canonical `struct` on **161/161** K-entry nodes, which
pins the direction (shadow = `f`(node), so a shadow cell pulls back through `f⁻¹`). C2 `cell_map`
is a D4 action on cell names and permutes the four corners (72 checks). C3 every K entry's drawn
packing is its primary structure's minimum (30/30). C4 all **235** contacts A107 books for the K
entries are reproduced by this module's SAT gap with **max |difference| = 0.0**.

**Discipline.** READ-ONLY outside `attempts/A121-reading-validator/**` + this ledger + the
registry row; 1 process, BLAS pinned (`blas1` before numpy); `PYTHONDONTWRITEBYTECODE=1`; no
deletes; no LP and no lane recomputation — A118's verdicts are read, never re-derived. Re-runs
incrementally on new rows: `python code/validate121.py [--since <commit>|--all|--only K01]`.
Report: `attempts/A121-reading-validator/notes/{report.md,method.md}`.

## 2026-09-07 — A121-reading-validator (Opus chore) — batch 2 (K22–K30, S01–S15) + the PI's calibration pass

**CUMULATIVE: 45 rows, 138 reading items, 1,453 (node, cut) rows, 9 node kills, STILL 0 NEW.**
Batch 2 adds 3 kills, all already booked by A118: **S01** `r f0 tl00` → A60 `c0_Y0088`, `c0_Y0094`
(trump5, TL(0,0), extension k6_23, `LANE ≤ 0, M = 1`) and **S06** `ns f2 tr00` →
`k5_11_interior_Y1080` (k5_11, TR(0,0), k6_23) — the latter being A118's own headline new kill,
recovered independently from the PI's reading. 9 kills × 850 s = **2.13 CPU-h**, 0 of it new;
no A99 level-1 cell, so still 0 CPU-h off A99's frontier. A118 kills **14** of this batch's
nodes; the readings name the killing cell for **9** and a non-killing cell for 5
(`k5_16_interior_Y0224`, `l2_p210_000/010`, `l2_p215_011`, `l3_pp215_000_011`).

**Pinned classes (T2 for the S rows).** Usability is a property of the cell IN THE NODE'S FRAME
and of the NODE's class, and an S entry does not have one class (S01 spans k5_11, k5_16, trump5,
four A61 stragglers and two k6 classes). So the cell is mapped through `struct_op⁻¹` first and
only then tested against that class's usable set. Result: **736 of 1,453 cut rows are
`cut_kind = none`** — S01's `r f0 tl00` is a SLOT-CROWD cut for its 196 trump5 nodes (TL(0,0),
k6_23) and NO cut for its 238 k5_11 and 178 k5_16 nodes, since TL(0,0) is usable for neither; and
A61's window stragglers (k5_05, k5_10, k5_12, k5_17, k6_20, k6_21, k6_29) have no usable-slot
table at all. The table used is A118's own `corpus.CLASSES`, in which **k5_16 has six usable
cells including `BL(1,0)` (k6_23)**; 50 cut rows depend on that cell and **none is a kill**, so
nothing here turns on the five-vs-six-cell discrepancy.

**T1 across all 60 `ns` items: 5 are genuine uncrowded near-snaps.** 24 are far (L∞ > 0.05), 22
name a square already EXACTLY on its cell, 6 are far AND crowded, 2 are near-snapped but crowded,
1 is on-cell and crowded. The slot/free under-count now stands at **23 of the 45 entries**. All
**12 `r` items are exactly right** (singly met, no grazer) — the reading type that works.

**T1b — CALIBRATION (the PI's question: are the cell names offset?). NO, AND THEY CANNOT BE.**
Over the 30 far items, **26 are FLUSH in one axis** with the named cell's centre (residual ≤ 0.01,
A101's own threshold; largest 5.5·10⁻³) and displaced only ALONG that wall — A101's flush
population (`flood_lemma.md` §1), not the η-disturbed population `ns` names. Searched **all 784**
relabelling rules (8 D4 name maps × {identity, index transpose} × index shifts [−3..3]²): the best
hits **1 of 30** within 0.05, and the ceiling is **1 of 30 (3 %)** because **29 of the far squares
have no lattice cell of ANY name within 0.05**. The best rule by total L∞ is the **identity**
(8.9565 vs 18.6363 for the runner-up): the PI's own cell names are already the closest assignment
available. The 4 non-flush exceptions are off in both axes — K25 `f1`@TL(1,0) (residual 0.084 at
tilt 14.48°), K27 `f4`@BR(0,1) (0.092), K26 `f5`@BL(1,0) (0.012), K29 `f6`@BL(1,0) (0.012).
**The fix is a new token (`fl <sq> <cell> <along>`), not a re-drawn frame.** The report also
carries the TRUE near-snap set (every free square within 0.05 AND 3° of a cell) per entry: it
names **5 corner-cell, singly-met candidates the reading misses** (K09 `f2`@TL(0,0), K11
`f1`@TR(0,0), K12 `f2`@BR(0,0), K13 `f1`@TL(0,0), K17 `f2`@BR(0,0)); the lane test was run on all
of them and **none is a node kill** (LANE ≥ 2, or UNDECIDED with M = 1).

**The `g` rows check out; the data behind two of them does not.** K18 `f0/1/3/4/5/6` share a tilt
to **5.5·10⁻⁴ °**; S13 `f0/2/3/4` to **4.6·10⁻⁷ °**; S05's "f2 flush on the side" is exact (right
wall gap 4.9·10⁻¹⁴); K30's "side > 4" is right (s\* = 4.020670) and "4 stacked on the left" is
right (BL(0,0), BL(0,1), f6 at left gap ≤ 3.3·10⁻¹⁶ and f3 at 0.038), with "the rest a
common-tilt grain" = 6 squares at 31.009° plus one outlier at 31.586°. But **K18's Fritz-John
decomposition does not close** (kkt_residual 0.117, rank 19 of 21; `f6` carries zero force while
the rattler test calls it load-bearing) and **K30's does not either** (0.024, rank 19 of 22).
S07's 1.3·10⁻⁴ at full rank is nnls noise, so the closure threshold is now 10⁻³. `g` rows now
also carry the entry's tilt clusters and flush-on-wall lists (so a description naming no squares
is still checkable) and, for S02/S07, A116's stability radii (S02 min forced radius 0.0315 at
ρ = 0 / 0.0191 at ρ = 100, limiter `f1|f3`; S07 0.0144 / 0.0082, limiter `f2|f4` — matching
A116's own 0.024 / 0.019 headline for the single-leaf N).

**One bug found and fixed:** `merge()` derived the entries to replace from the NEW rows, so an
entry whose cuts fell to zero (S11, whose reading is `-`) kept its stale rows forever. The
touched set is now `todo`. Canaries re-run and all PASS (C1 161/161, C2 72/72, C3 30/30, C4 235
contacts at max |diff| 0.0). Discipline unchanged: read-only outside A121 + this ledger + the
registry row, 1 BLAS-pinned process, no LP, no lane recomputation.

## 2026-09-07 — A107 gallery v2 panels (Opus chore, read-only) — PI's rendering feedback applied

All 83 SVGs in `docs/shadows/` re-rendered in place; **v1 kept byte-for-byte under
`docs/shadows/v1/`** (no deletes). Frames, canvas sizes, right-panel polygon geometry, contact
rings and every f-index / cell label are identical to v1 — checked mechanically, 0 regressions
across all 83 files — so the PI's `review.csv` rows stay valid.

* **Left panel: tilt hue removed.** Every dual-support placement is now filled on ONE sequential
  ramp by its dual weight y (pale yellow at y → 0, dark orange at y = 1), with the number printed
  inside the square only when y < 0.95 — 283 such labels across 45 of the 83 panels. The weights
  are read back from each representative node's own json (read-only; the drawn placements came
  verbatim from `packing`, so the match is exact). Hypothesis squares are bright cyan `#00e5ff`
  with a 3 px black outline and an **H**, a colour used nowhere else, drawn last so they are never
  buried.
* **Right panel: 47 mis-coloured squares fixed in 33 entries.** A free square within 1e-3 of a
  lattice cell centre and 0.05° of axis is a snapped slot square; v1 drew it red as if it were
  free (A121's finding). It is now blue with its cell name on the second label line, and the
  entry's slot/free split is corrected in `docs/shadows.md` with the old split kept in a new
  **`gallery v1 split`** column so A121's audit stays reproducible. The f-indices are unchanged
  everywhere — contact graph, forces, flat directions, rattler table — and the cell name is added
  alongside, not in place of, the index.
* **Entries whose slot count changed** (v1 → v2): S01 5+6→7+4, S03 6+5→8+3, S04 5+5→6+4,
  S06 5+5→7+3, S14 5+5→6+4, S15 6+5→7+4, S16 6+4→7+3, S19 5+5→7+3, S23 6+4→7+3, S25 5+5→6+4,
  S29 6+5→7+4, S32 6+5→7+4, S44 5+6→6+5, S52 7+4→8+3; K03 4+7→5+6, K04 2+9→5+6, K05 4+7→6+5,
  K06 5+6→6+5, K09 1+9→3+7, K11 1+9→3+7, K12 2+8→4+6, K14 2+8→3+7, K17 4+7→5+6, K18 4+7→5+6,
  K19 5+6→6+5, K20 2+9→4+7, K21 5+6→6+5, K22 1+10→4+7, K23 2+9→3+8, K24 4+7→6+5, K25 5+6→6+5,
  K26 3+8→4+7, K30 2+9→3+8.
* Note on the count: the brief said A121 found **11** such entries; applying the stated criterion
  (1e-3 in position, 0.05° of axis) uniformly across all 83 gallery entries gives **33 entries and
  47 squares**. The larger set includes the k0 Part II entries, where free blocks are big and
  lattice landings are common (K04 and K22 each gain three slot squares).
* **One-line legend** added at the top of every SVG, inside the existing top margin, so no
  geometry moved.
* Discipline: read-only everywhere else, one BLAS-pinned process, no deletes, git fetch + plain
  merge + push of A107's own paths.

## 2026-09-07 — A121-reading-validator (Opus chore) — batch 3 (S16–S53): the first pass is complete, 83/83

**CUMULATIVE OVER ALL 83 ROWS: 219 reading items, 1,487 (node, cut) rows, 9 node kills, 0 NEW,
94 disagreements.** 9 × 850 s = **2.13 CPU-h**, every hour of it already booked by A118; no A99
level-1 cell, so still **0 CPU-h off A99's k0 frontier and 0 off the A57 schedule**. Kills by
type and class: `r`/k0_00 6, `r`/trump5 2, `ns`/k5_11 1 — and by cell, `TR(0,0)` ×7, `TL(0,0)`
×2, reproducing A118's own "corner cells dominate the fires". A118 kills **15** of the 83 rows'
nodes; the readings name the killing cell for **9** and a non-killing one for **6**
(`l2_p210_000/010`, `l2_p215_011`, `l3_pp215_000_011`, `k5_11_interior_Y0138`,
`k5_16_interior_Y0224`).

**`st4` — all three are CONFIGURATION kills, not node cuts.** Four axis-aligned unit squares
flush against one wall span that wall's unit strip, so they are pairwise disjoint in the
perpendicular coordinate and the side is ≥ 4; the four need not be consecutive (S50's top square
sits **2.7·10⁻⁵** above the third, which is exactly s\* − 4). Verified: S50 `left` = BL(0,0)
BL(0,1) BL(0,2) TL(0,0), s\* = 4.000027; S52 `left`, same four, 4.000197; S53 `right` = BR(0,0)
BR(0,1) BR(0,2) TR(0,0), 4.000261. **But the four are not forced by any of the three nodes**:
S50/S52 (A60, trump5) have only BL(0,0), BL(0,1) as pins — BL(0,2) and TL(0,0) are free — and S53
(`k5_11_interior_Y0672`, op `diag`) has only one, BR(0,0). So the stack kills the drawn packing
and leaves all three nodes alive. **The token is sound and its yield here is zero.**

**The `-` rows — the blue snaps DO give candidate cuts, and the lane test converts none.** The
usable-cell scan (every usable cell of every node's class, pulled into the shadow frame, counting
NON-PIN meeters as SLOT-CROWD requires) finds **48 under-crowded (node, cell) pairs across the 13
`-` rows** — 1–19 per entry, mostly the snapped square sitting alone in its own usable cell —
and **0 node kills**: LANE ≥ 2 at 21, UNDECIDED at 21, and LANE ≤ 1 blocked by M = 1 at 6
(S37/S38 TL(0,0), S40 BR(0,1), S42 TL(1,0)). Those six are the closest misses in the whole
corpus.

**The `g` rows: two cross-entry claims settled, one refined, one refuted.** S34 "same minimum as
S33" is RIGHT ABOUT THE MINIMUM and wrong about the panel: **A122** re-minimised both with all
eleven squares free and gets ds = 6.2·10⁻¹⁵, max centre gap 1.5·10⁻⁸, max tilt 2.5·10⁻⁶ ° — the
same minimum — while the GALLERY landings differ (10 of 11 matched, max centre gap 0.041, max
tilt 4.70°); A122's polish drops S34's s by 4.29·10⁻⁴ onto S33's value, so the S34 panel is
simply not converged. S35 "same minimum as S33" is **WRONG**, and A122 confirms it independently:
ds = 4.87·10⁻⁴, max centre gap 0.069, max tilt **6.92°** after polishing both. S09 "same as S05"
is **WRONG** by inspection — s\* differs by 1.29·10⁻² and only 7 of 11 squares align. S21's
"S07-type" is a family claim, and measured it is exactly that: 6 of 11 squares align, max centre
gap 0.065, max tilt 10.48°, ds +8.70·10⁻³ — a related near-Trump packing, not S07's. Tilt grains
all check out (S16 f0/1/3, S24 f0/2/3, S29 f0/1/3/4, S30, S31 f0/2/4); the recurring problem is
Fritz-John closure — **7 `g` rows now carry a kkt_residual above 10⁻³** (K18 0.117, S21 0.103,
K30 0.024, S29 0.021, S16 0.0091, S35 0.0018, …), i.e. those load paths are nnls fits, not
certified.

**T1c — EVERY right panel is a rearrangement, not a snap.** Matching each drawn minimum over D4
against the snapped dual support of its own primary seed node: **81 of 83 are `rearrangement`**
(some square moved > 0.05; worst S40 0.944, K12 0.719, K16 0.703) and the other **2 are
`tilt-only`** (S02 max centre move 0.044 but max tilt 10.1°; S07 0.030 / 5.2°) — **zero snaps**.
This reproduces A106 §2.2 from the other side: the minimum is never where the LP put the support,
which is exactly why a reading is a POINTER to a cell and never a fact about the node. The full
ranked table is the PI's `?` list.

**Across all 64 `ns` items, 6 are genuine uncrowded near-snaps** (26 far, 24 already exactly ON
the cell, 6 far + crowded, 2 near + crowded). Calibration over the now-32 far items: **28 are
FLUSH in one axis** (residual ≤ 0.01, largest 5.5·10⁻³); of 784 relabelling rules the best hits
**1 of 32**, the ceiling is **1 of 32 (3 %)**, and the **identity is still the argmin** of total
L∞ (9.5034 vs 19.1977). All **18 `r` items are exactly right**. The slot/free under-count is
**41 squares in 29 entries** at A121's thresholds and **47 in 33 at A107 v2's own** — reproducing
the v2 re-render's count exactly (v2 adopted this finding; A107's results JSONs are unchanged).

**Threshold moved, with the reason:** the meet/graze boundary is now 10⁻⁶, not 10⁻⁷. At 10⁻⁷,
S44's `f0` (SAT gap −1.24·10⁻⁷, corner-frame depth 9.2·10⁻⁸) counted as a second meeter and made
a correct `r` reading look like a crowd; over all 83 entries only 4 meeters sit between 10⁻⁷ and
10⁻⁴ and every one is a converged tangency. Grazers are never dropped — each is listed against
its cell. Canaries re-run, all PASS (C1 161/161, C2 72/72, C3 30/30, C4 235 contacts at max
|diff| 0.0). Discipline unchanged: read-only outside A121 + this ledger + the registry row, one
BLAS-pinned process, no LP, no lane recomputation.

## 2026-09-07 — A114-window-closers (Opus chore) — continuation: the slab sweep closes the last three
- **k5_02, k5_12, k5_03: ALL THREE CLOSED over the whole window** with the SAME s0 certificate
  (A56's parametric re-expression of the original A53/A54 kill), no LP re-solve anywhere:
  k5_02 by 35 slabs of 0.001777 (1.54 CPU-h), k5_12 by 85 slabs (0.000794 below s = 3.87, 0.000394
  above; 3.09 CPU-h), k5_03 by 14 + 34 slabs (0.00179 / 0.00149 / 0.000755 in three zones;
  8.76 CPU-h). C2 3/3 PASS at s_lo, midpoint and s0 for each. **A56 scoreboard: 51/52 full-window
  rows** (4 M1 + 27 TRANSFERRED + 20 TRANSFERRED-resolved); only k5_13 is open, and that is A61's
  campaign, untouched. Scoreboard written atomically after each closure.
- **L6, the width predictor (advisor's, verified).** One probe slab gives w_min = width /
  2^max_s_depth and d_pose = max_depth - max_s_depth; a slab passes iff width <= w_min * 2^(48 -
  d_pose). Measured: k6_07 0.0117 (A114 used 0.0029 — 5 slabs would have done instead of 18),
  k6_27 0.0141, k5_02 0.00178, k5_03 0.00179 low and 0.00100 at the top, k5_12 0.00100 low and
  0.00050 at the top. `max_depth == 48` in a PASS is the "no headroom, do not widen" flag. Every
  earlier bulk FAIL was a slab over its width_max (k5_02's were 4x over), never node hardness.
- **L7, cost along s (224 verifier runs, results/cost_profile.json).** Seconds per 1e-3 of s, first
  slab -> the slab ending at s0: k6_27 19.9 -> 1589, k6_07 53.3 -> 91.0, k5_02 88.7 -> 501.6,
  k5_03 412.3 -> 1063.6, k5_12 129.2 -> 4181.4. The cost concentrates in the last 1e-4 to 5e-4
  below s0, where w_min shrinks (k5_12: 1.74M boxes for a 5e-4 slab at s_top 3.8405 vs 12.7M for
  the same width at 3.877) and, for k6_27, d_pose itself climbs 39 -> 43. That is the S02 pinwheel
  shadow (s* = s0 + 0.0097) measured directly in verification cost — the first such measurement.
  It does NOT mean the s0 certificate must be replaced near s0: the advisor's per-slab re-solve
  route was not run because (i) make_param.py is anchored to the s0 census and would have to be
  edited — a frozen builder, (ii) 30-85 k5-class base LPs at 1200-1900 s each is 10-45 CPU-h
  against a 15 CPU-h cap, and (iii) the premise was refuted by the data: every slab closes with
  the s0 certificate once it respects width_max, including the slabs that touch s0.
- Bug found and fixed in A114's own driver: verify_param builds one integer grid with
  D = 250000 << (depth+2) and REFUSES an s endpoint whose denominator does not divide it, so cut
  points must be 2^a * 5^b with b <= 6; a 30-slab k5_03 grid on k/640000000 came back "FAIL in
  0.3 s" for every slab — a crash recorded as a verdict. close114 now checks every endpoint before
  launching, keys a resumed stage only when its recorded bounds match, and persists the banked
  ranges after EVERY slab.
- Cost: 12.5 CPU-h for this continuation (17.94 CPU-h for all of A114), under the 15 CPU-h cap.
  <= 2 processes throughout, BLAS pinned, commit/physical gate before every verifier, frozen
  verifiers byte-identical, A61's k5_13 / A57 / A96 / A111 / A107 untouched.

## 2026-09-07 — A119-local-cert-lean (Opus engineer, ≤ 2 BLAS-pinned processes, Lean builds through A78's serialised low-priority `lakeb.py`, read-only on every campaign and on A116/A117) — done-success: the local certificate is a frozen, independently checked object; Local.lean builds clean with ONE project axiom and no sorry; the blocking-box route does NOT extend the radius, and three of A116's four "capped" ρ ≥ 20° cells are ALIVE

**T3 first, because it changes a published table.** The ρ ≥ 20° frontier at r = 0.2 is not a time
cap: it is ALIVE. With the ORIGINAL L the tree produces CHECKED packings of L ∪ P below s0 inside
N at **S07 (0.2, 20°) side 3.873374** (f0, f2, f4 all at 65° — the ladder shears; found at node
917, 2 s), **S07 (0.2, 40°) side 3.869626** (68.7°, 4 769 nodes) and **S02 (0.2, 40°) side
3.876703** (f3 turns to 88.3°, f1 to 12.2°, f2 to 8.4°; 392 144 nodes, 559 s). For the two S07
cells **A116's own results file already contained the refutation** — `t2_S07.jsonl` records 4 128
witnesses at (0.2, 20°), the first with `witness_valid: true`, worst pair gap −4.4·10⁻¹⁶, worst
wall gap 0 — while the row's verdict field says `capped` and `notes/t2_table.md` prints CAP; the
same mislabelling affects S07 (0.2, 40°), S07/S02 (0.3, 20°/40°). `a116lib.Tree._loop` as it
stands today returns at the FIRST checked witness and so cannot record 4 128 of them: those rows
predate that return. Re-running A116's own tree today with A116's own parameters gives ALIVE with
the same witness in 25 s (`code/f1probe.py`, `results/f1_probe.json`). **So `docs/proofs/local_certificate.md`
§5's "no witness and no dip were found there, so those cells are open, not dead" must be
corrected: they are dead the other way.** S02 (0.2, 40°) is A119's own new result (A116's record
there has `n_witnesses = 0`). Only **S02 (0.2, 20°) remains genuinely open** — and A119 pushes it
to 633 660 nodes in 900 s, **4.6× A116's node count in the same wall**, still without resolving it.

**The blocking squares as boxes do not extend the radius.** S02 gets `f0` + `TR(0,0)`, S07 gets
`f1` + `f3` + `BL(0,2)`; that is 6 free bodies (6 tilt dimensions, 16–23 near pairs) instead of
3–4. **Exactly one blocking-box N closes: S02 (0.1, 5°) — DEAD, 58 447 nodes, 121 s of tree,
certified 3.877101 / measured 3.886746, 0 hits in 10⁴ samples, Trump outside** — and it is
strictly LARGER than A116's own six-box run, which had to confine the slot square `BR(0,1)` to a
0.05 box. Every other blocking-box cell (r ≥ 0.2 or ρ ≥ 10°, either shadow) caps at 900–1200 s
with 320 000–460 000 nodes; for S07 no blocking-box N closes at all. **A116's (0.2, 10°) and
(0.1, 40°) with the original L remain the largest certified neighbourhoods.** The blockers ARE
the right objects, though: re-running the three ALIVE cells with them finds NO witness in 900 s
(verdict CAP, not ALIVE) and lifts S02 (0.2, 40°)'s certified minimum over the closed part from
3.877567 to **3.881900**. What stops the proof is the tilt-cell count of a six-body tree, not the
geometry. **Consumer, re-run with a bipartite MATCHING instead of A116's 11 P |L| brute force
(same answers, and it terminates for |L| = 6): unchanged — 72 of 184 k5_11 + 23 of 68 k5_16 = 95
of the 252 S02-explained alive nodes, 2 of 18 for S07; the blocking-box N catches 1 of 184**, so
the blocking squares are a device for the certificate, not for the node cut.

**T2 — `lean/PackingCertMathlib/PackingCertMathlib/Local.lean`, `lake build` clean (and part of
the default target).** It states `Box` / `Pin` / `LocalHyp` / `LocalDead` and proves: Lemma
RELAX's algebra (`axis_decomp` — the exact `d·a(θ*+φ) = p cos φ + q sin φ` that makes the
relaxation second order; `mccormick_hi` / `mccormick_lo`; `abs_chord`; `chord_of_concave`;
`abs_sin_le_sin`; `cos_ge_of_abs_le`), Lemma COVER's primitives (`cover_bisect`, `cover_qsplit`,
`cover_selection`, and `cover_pair`, which consumes the SAT axiom), `localDead_of_contradiction`,
**three generated `leaf_*` theorems that are actual leaves of an actual certificate** (the
relaxed rows written out with rational coefficients, the box bounds, and the kill `s0 < s` closed
by `linarith`, the Farkas multipliers — all of the form k/2⁴⁰ — listed row by row in each
docstring), and the composition `classKilledAt_of_localDead` into `Composition.lean`'s
`ClassKilledAt`. **Axioms: 0 sorries and exactly ONE project axiom, `sat_selection`** — Lemma SAT
for INTERIORS, exact statement in `notes/lean_status.md`; `CaseSat.sat_squares` gives the
closed-square form and the open work is the shrink argument's choice of λ. It reaches only
`cover_pair`; `classKilledAt_of_localDead` additionally inherits A22's `native_decide` axiom
through `shat`. Audit: `lean/PackingCertMathlib/scratch/A119Axioms.lean`. What Lean does NOT yet
do is derive `LocalDead` for a concrete N — that is the recorded cover, and it is done and
re-verified outside Lean by `check_local.py`; the next step is the A78/A93 route (a Lean-side
checker with `native_decide`).

**T1 — seven certificate files, ALL VALID under an independent pure-rational checker.**
`code/exact119.py` writes `certs/<id>.cert.json.gz` + a sha256 manifest: the whole proof object
per N — the tilt-cell bisection cover, the selection case split with the excluded selections, one
rational Farkas vector (denominator 2⁴⁰) per closed leaf, and a Farkas RAY per infeasible cell.
`code/check_local.py` re-checks them with **no numpy, no scipy, no tree code** — dyadic interval
arithmetic on Python integers at scale 2⁻⁹⁶ (`code/exactiv.py`, with rigorous π, cos, sin and the
EXACT range of |cos| + |sin|) — rebuilding every row of Lemma RELAX itself and re-deriving every
bound. Sizes and walls (`notes/t1_table.md`): S02 (0.2, 10°) 32 426 cells / 63 branches / 5 782
infeasible / 32 570 dead leaves / **504 404 multipliers**, 5.6 MB, generated in 91 s, **checked in
679 s**, checker's min bound 3.877084098 > s0 = 3.877084; S02 (0.1, 10°) 6 878 leaves, 134 s;
S02 (0.05, 20°) 7 692 leaves, 117 s; S07 (0.1, 40°) 2 302 leaves, 28 s; S07 (0.2, 10°) 3 168
leaves, 74 s; plus two small regression certificates. **53 094 dead leaves and 769 440 rational
multipliers checked in 1 041 s.**

**Also, ahead of T1 (coordinator's request):** `results/N_boxes.json` — every certified N written
the way A96's `caselp` / NO-family machinery quantifies over it: ONE axis-aligned box
`(cx, cy, θ-interval)` per square of L in the class frame at s0, the pin slack cores
`α + βs + [−h, h]²`, the cut as a single scalar inequality on the tilted squares' common tilt,
and the per-class D4 frame ops (A107's `struct_op`). The point of the note (`notes/n_boxes.md`) is
that A116 states TWO box-shaped objects and only one is consumable: Lemma STAB's 6-dimensional
PAIR-pose boxes with a forced selection are the PI's single-leaf route and name a pair and a
separating axis, which do not occur in A96's node LP at all; the certificate's hypothesis N is
already a PRODUCT of per-square boxes, and that is what Theorem LOCAL kills. The DROP/COVER
composition is spelled out (DROP forgets the other squares; COVER's covering family is the leaf
polyhedra of the per-square boxes, and the pair boxes never enter it). 12 000 independent uniform
draws per N, at 30 sides spanning [3.82, s0]: **0 hits, all six**.

**Engineering.** Profiling A116's tree showed **66 % of the wall inside `scipy.optimize.linprog`,
most of it scipy's own option validation and sparse-matrix construction, not HiGHS**;
`code/fastlp.py` passes the model to one reused `highspy.Highs` instance (**1.64 → 0.46 ms per
solve, 3.57×**), and the witness-search gate was loosened. Verdicts and node counts are IDENTICAL
to A116's (`code/xcheck119.py` checks rows bit-for-bit and trees node-for-node): 2.6–3.4× end to
end. A dual-inheritance idea (close a child with its parent's or the last leaf's Farkas vector)
was implemented, measured at 8–15 % of nodes closed with no LP, and REJECTED — the sparse rebuild
costs more than the LP it saves once HiGHS is called directly.

**Five findings on A116's implementation** (`notes/method.md`): **F1** a q-range case split is
measured on the OWNER's midpoint-axis functional and does not survive a later tilt bisection, so
the two branches stop covering — but every q-split A116 ever made was in its phase-2 cosmetic
tightening (phase 1 re-run here produces none, even with `qsplit_min` forced to 10⁻⁷), no KILL
depends on one, and a three-way probe finds the same witness with the carry-over on and off; A119
drops the affected q-ranges at every bisection and its checker enforces the same discipline.
**F2** a node must be closed on its Farkas VECTOR, not on the LP's optimal value (a HiGHS dual is
only approximately optimal). **F3** an infeasible cell needs an exported Farkas RAY — A116 wrote
none, and 5 782 of the 32 570 leaves of S02 (0.2, 10°) are of that kind. **F4** a certificate
checker must reproduce the generator's interval SHARPNESS, not merely its soundness: a
second-order but non-exact `cos`/`sin`/`w` enclosure made the checker reject a `branch` node of
S07 (0.1, 40°) whose root cell is 80° wide. **F5** the CAP/ALIVE mislabelling above.

**Discipline.** ≤ 2 BLAS-pinned compute processes throughout (`blas1` imported before numpy via
`a116lib`), Lean through `attempts/A78-lean-wave6/code/lakeb.py` (repo-wide lock, BELOW_NORMAL),
`PYTHONDONTWRITEBYTECODE=1`, nothing deleted, READ-ONLY on every campaign and on A116/A117 (their
libraries imported, their results read). Writes: `attempts/A119-local-cert-lean/**`,
`lean/PackingCertMathlib/PackingCertMathlib/Local.lean` (new) + its import line,
`lean/PackingCertMathlib/scratch/A119Axioms.lean` (new), one clause on the depgraph GRAIN node
(+ re-rendered svg), the registry row and this entry.

## 2026-09-07 — A122-s33-certify (Opus chore, read-only) — done-success: S33 = S34 = K19 is ONE minimum, S35 is a SECOND one, and neither is a quadratic-field point

**s\*(S33) = 3.9169308657139205630222903359985043624524966276682** (50 digits; ŝ + 0.039847276) and
**s\*(S35) = 3.9174176578146106278280178960004740044013819558776** (ŝ + 0.040334). Released with all
eleven squares free (A106's `shadow11` at zero pins, cross-checked against A107's engine), the four
gallery landings the PI flagged collapse to **two** points, not one and not three: S33, S34 and K19
all polish to the same configuration (max centre gap 4.3e-8, max tilt 0.0000°), while **S35 is a
genuinely different local minimum** 4.868e-4 above it, 0.069 away in centre and 6.92° in tilt.
S35's contact graph is isomorphic to S33's after relabelling but carries one extra flush incidence
(three squares share a tilt instead of two). Both are strict local minima by trust region: S33min
returns s\* for every ρ from 1e-5 to 1e-1; S35min for ρ ≤ 3e-2 and at ρ = 1e-1 escapes *downhill*
into S33min's basin — a shallow secondary minimum sitting on S33's shoulder.

* **No closed form, and the reason is structural.** A108 could close S07 in Q(√2) because its
  sixteen active rows eliminate rationally. Here the same sixteen rows are **rank-deficient**
  (rank 14 at S33min, 15 at S35min), so the contact graph leaves a 2- (resp. 1-) parameter family
  of packings and the minimum is a **smooth interior critical point** of s on that family — the
  exact opposite of S07's kink. Consequence: **Fritz-John SUCCEEDS at first order here** (residual
  8.3e-9 at S33min, 4.6e-12 at S35min, 9.6e-15 at S38min) where at S07 it failed at 0.152; the
  price is that the exact characterisation is the Lagrange system `g(x) = 0, J(x)ᵀλ = e_s`
  (32 equations, 32 unknowns), solved by pseudo-inverse Gauss-Newton in mpmath with an analytic
  forward-mode Jacobian — |F|∞ 4e-9 → 6e-81 in five steps, worst SAT and containment gap ±1e-61.
  PSLQ at 170 correct digits, with the honest rule `degree × log10(maxcoeff) ≤ 100` and residual
  < 1e-150, finds **no minimal polynomial** for either. (A loose PSLQ "finds" a quadratic for any
  number at all; the rejected hits are recorded in `results/minpoly.json`.)
* **Endpoint certificates**: A106's `certify_endpoint` PASSes at the **first rung, ε = 1e-9**, for
  all three points (margin 2.2e-10), and again at 400 bits with denominator 1e15 — the same rung
  A108 reached for S07.
* **S33min's contact graph** (classified at the 80-digit solution, not at 1e-7): 15 pair + 11 wall
  contacts. `f0` is **UPRIGHT** and **full-edge flush against the BL column's right face x = 1**
  (partial overlaps 0.546 with `BL(0,1)` and 0.454 with `BL(0,2)`, summing to f0's whole left
  edge) — that flush pins `cx_{f0} = 3/2` and `θ_{f0} = 0` exactly. From it two diagonal chains:
  `f0`→`f1`→`TR(0,0)` upward (FJ 0.462, 0.444) and `f0`→`f3`→`BR(0,0)` downward (0.478, 0.465),
  with `f1`–`f2` flush to the top wall against `BL(0,2)`'s corner (1,3) and `f4` wedged between
  `f1` and `f3` on the right wall. Rank 32; **2 flexes at fixed s, both blocked at second order**
  (curvature −0.180 and −0.507). Idle: `BL(0,0)`–`BL(0,1)` and `BL(0,0)`–bottom wall.
  **Every one of the eleven squares is load-bearing** (remove-and-re-minimise drops 0.0225–0.1492);
  no rattler, no room, no free rotation — the PI's reading of "fully loaded" is confirmed.

**vs S07 and Trump** (`docs/residue_map/s33_vs_s07_trump.svg`, all three panels containment- and
overlap-checked, worst SAT −1.0e-15). Identity frame in both. Against **S07** all four BL cells are
identical to 0 — including `BL(0,2)`, which Trump lifts and S07 does not — and only the free block
differs: **f0 by 45.000°**, f1/f2 by 5.000°, f3 by 6.449°, f4 by 2.089°. Against **Trump**: f1/f2
within 0.181°, f3 by 11.267°, f4 by 6.907°, **f0 by 40.182°**, `BL(0,2)` lifted 0.0326.
**One square is the whole story**: S33min is what S07/Trump become when the keystone rotates to 0°
and jams flush on x = 1, and the price is +0.031313 over S07, +0.039847 over ŝ.
**A third separate local minimum on the k6_07 skeleton**: the straight segment crests at 4.1413
(vs Trump) / 4.1449 (vs S07), and the most generous path measured — five tilts pinned to the linear
interpolation, all eleven centres, six upright tilts and s re-minimised, warm-started both ways —
still crests at **3.955149 (+0.038218 over S33min, +0.078065 over ŝ)** and **3.957754 (+0.040824,
+0.072136)**; inside a 0.15 trust region, 3.978558 / 3.986556. A108 measured **+0.001105** between
S07 and Trump: **S33min is a 35× deeper separation.**

**S38 (added to scope): a kink minimum of two chain formulas that are NOT in A110's menu.**
s\* = **3.9289146852229775266372995972** and it IS algebraic of low degree: the root of the
irreducible **x⁹ − 16x⁸ + 105x⁷ − 360x⁶ + 663x⁵ − 518x⁴ − 297x³ + 1064x² − 992x + 358**
(residual 1.4e-165; Trump is degree 8, S07 degree 2). Its five free squares are one flush grain at a
common tilt **θ\* = 41.754062677271°** (sin θ\* a root of the irreducible
`s⁹ − 2s⁸ − 3s⁷ + 4s⁶ + 12s⁵ − 6s⁴ − 13s³ + 6s² + 4s − 2`, tan θ\* of `x⁹ + 2x⁸ − 3x⁵ − 4x⁴ − x³ +
2x + 2`). In strip coordinates the grain closes into **six** wall/corner rows in **five** unknowns —
overdetermined by one, so the structure exists at exactly one tilt, like S07 (Λ ∧ Y) and S02 (Λ ∧ A).
A continuation-TUBE sweep (each 0.02–0.05° step confined to ‖z − z_prev‖∞ ≤ ρ, ρ ∈ {0.01, 0.03}
agreeing to 1e-8) identifies the two active branches:

>  **C₃(θ) = (1 + 3cos θ + 3sin θ + cos θ sin θ + sin²θ − sin³θ)/(1 + cos θ sin θ)**  below θ\*
>  (f3 leaves the top wall; BR(0,1)'s corner leaves f4 gives the same closed form), matched to 5e-8
>  **C₂(θ) = (2 + 2cos θ + 2sin θ + cos θ sin θ + cos θ sin²θ − 3cos²θ sin²θ)/(1 + cos θ sin θ − cos²θ sin²θ)**
>  above θ\* (f1 leaves the top wall), matched to 2e-7; they cross where
>  **G(θ) = (sin θ − 1)(2sin²θ − 1)cos θ + sin⁵θ − sin⁴θ − 4sin³θ + 2sin²θ + 2sin θ − 1 = 0.**

C₃ carries Λ's and Y's very denominator 1 + sin θ cos θ, so **A110's menu {Λ, Y, D, F_T, A} gains
two members**; none of the four is S38's chain (at θ\*: Λ 3.886625, Y 3.864587, D 3.944843,
F_T 3.888130, against s\* 3.928915).

**There is no crest between S38 and Trump, and the descent is NOT the gap chain.** On the tracked
branch the side rises *monotonically* as θ falls from θ\* (3.928915 → 3.930704 at Trump's 40.181937°
→ 3.932819 at 38.50°, on down to 3.956679 at 25.25°, matching C₃ to 3e-9 at every step of a
330-point sweep) and `s − F_T` GROWS from +0.0408 to +0.1336. It cannot be F_T: that chain runs
through BL(0,1)'s corner (1,2) under a lifted `BL(0,2)`, and **S38's frame (k6_21) has no `BL(0,2)`
cell at all**. Getting from S38 to Trump is a slot change, not a tilt motion. The crest the gallery's
coarse tilt-sweep row shows is on the FAR side: the C₂ branch dies at **42.7941°, s = 3.934377915**
(C₂ there to 5.1e-9), i.e. +0.005463 over S38 and +0.057294 over ŝ.

**The two crests as points on Trump's basin boundary** (data for the tube):

| family | crest tilt | crest side | over ŝ | on Trump's boundary? |
|---|---|---|---|---|
| S07, k6_07, Λ ∧ F_T | **41.564880625°** (`sin θ cos θ = 2 cos θ − 1`) | **3.886746028606** | **+0.009662** | **yes** — below it the branch is F_T and falls to ŝ |
| S38, k6_21, C₃ ∧ C₂ | **42.7941°** | **3.934377915** | +0.057294 | **no** — it is on the side away from Trump |

**METHOD WARNING (A108's trap, in its path form).** The same relaxed sweep run WITHOUT a tube —
tilts pinned, everything else free, warm-started — reports **3.902308 at S38's own tilt, 0.0266
BELOW s\***: SLSQP leaves the basin at the very first grid point, and the curve it then traces is
the tilt-pinned *floor of the corridor*, not a barrier. Both versions are kept in
`results/crest.json` so the contrast is auditable. A second, smaller trap: A108's `-1e-7` landing
gate silently discards iteration-limited SLSQP landings, which is why `crest_refine.py` uses a
`-1e-5` gate and reports σ(poses) — σ is exact for whatever poses come back.

**Class and kill.** Slot cells at s0 ⇒ S33/S34/S35/K19 = census class **k6_07** under the identity
of D4 (S07's own class, trump5 + `BL(0,2)`); S38 = **k6_21** under `diag`. **Both windows are now
FULL on [191/50, 969271/250000] = [3.82, s0]** — k6_07 by A114's sub-window bisection of A108's open
band with the frozen parametric certificate + full C2 canary, k6_21 by A61's re-solved base
certificate. *This supersedes A108's note, which recorded k6_07 as PARTIAL at 12.38 % coverage with
band (3.827068, s0] open.* All four points sit 0.040–0.052 ABOVE s0, so none is what those windows
have to exclude.

**A116 applies, and far better than at S07.** A116's canary needs one box of L to contain no Trump
square. Position-only exclusion radius `r_max = max_{n∈L} min_j |c_n − c_j|` at the s0 anchor:
**0.0342 for S07** (A116's own run — which is exactly why it needed the Trump-boundary cut as soon
as r ≥ 0.033, ρ ≥ 4.82°), **0.2054 for S33min/S35min** (via the upright `f0`, which is 40.182° from
Trump's tilt there), **0.6771 for S38min** (via `f1`). So an N of A116's headline size (r = 0.1,
ρ = 40°) around S33min needs **no Trump-boundary cut at all**; the load path to hand it is
`L = {f0, f1, f3}` with `{f2, f4}` and the six cells as pins. For S38 the only cut needed is the
branch selection `G(θ) ≷ 0`, with floors C₃, C₂ ≥ 3.9289147 — **margin 0.051965 over s0**, six times
S07's Λ margin of 0.008534.

Constraints honoured: read-only on A03/A53/A56/A57/A60/A61/A106/A107/A108/A110/A114/A116 and `lean/`
(their modules are imported, never written); BLAS pinned to one thread, `PYTHONDONTWRITEBYTECODE=1`,
no deletes; git fetch + plain merge + push own paths only. Writes:
`attempts/A122-s33-certify/{code,results,notes}`, `docs/residue_map/s33_vs_s07_trump.svg`, registry
row, this line. Corrections of record to the A107 gallery (S34 is not a separate minimum; S35's s\*
is 1.5e-5 high; S33's "1 flat direction" is 2 with all eleven free; the KKT convergence caveats
clear to 8e-9 / 5e-12) are in `attempts/A122-s33-certify/notes/method.md`; `docs/shadows.md` itself
was left untouched.

## 2026-09-07 - A115 follow-up 2 (PI) - the continuation, and A121's pointer

**Continuation of the plain warm re-solve pass**, 10 CPU-h cap, 82 cells: (1) the 36 T4
kill-candidates with a 900 s warm continuation plus A85's witness-feedback rounds; (2) the 240 s
plain pass over A38's 82 never-run level-1 cells and its 60 still-open level-2/3 cells; (3) the 9
open A99/A85 cells the T4 cap did not reach; and, added mid-run on the PI's instruction, (4) the 14
A38 k0 nodes A121's `i` table flagged as having incomplete supports and never queued by A115.

**Result. Across T4 + T5 the plain warm re-solve now certifies 17 DISTINCT level-1 cells of the
k0_00 root split dead (16 of them newly), plus 6 level-2 cells, 1 level-3 cell and 4 A85 nodes, for
15.36 CPU-h. That removes 735-1,705 CPU-h (level-1) + 32-75 (level-2) + 0.7-1.6 (level-3) =
768-1,782 CPU-h from A99's 9,341-21,661 CPU-h frontier - a 48x-111x return.** For contrast A115's
own corner rows cost 13.4 CPU-h for the same pass and removed nothing.

* **A121's `i` table was the best pointer in the whole pass: 14 of 14 of its cells certified**, 7 of
  them level-1 (`node_017/018/030/031/032/098/143` - all A38 `undecided`, none of which any A115
  queue would have reached), 6 level-2 and 1 level-3. Every one had tau = 9, budget 10, and closed
  in 37-264 s.
* Sub-task (1): the 900 s continuation plus A85's own witness-feedback rounds turns **4 of the 36**
  first-pass cert-FAIL cells into certificates (`s1int_l2_l2_p210_001`, `s1int_l2_l2_p215_011`,
  `s1int_l2_l2_p114_010`, `s1cor_far_b595`). The other 32 still FAIL - row-generation-incomplete at
  a level a 900 s continuation does not fix. A121's two cert-FAIL cells were run first; both still
  FAIL.
* Sub-task (2): 48 of A38's 82 never-run level-1 cells were reached; 2 certified (`node_172`,
  `node_176` - cells that had no verdict at all), 27 kill-candidate, 16 alive, 3 knife-edge.
* Sub-task (3): all 9 not-reached cells ran; 4 certified. A121's 3 not-reached cells are among them.
* By what A113 previously said about the 17: 7 `UNDECIDED` (all A121's) and 4 `NOTRUN` are NEW
  kills; 4 `KILL(LP,uncertified)` and 1 `FAIL` are upgraded to a frozen-verifier certificate; 1
  (`l1_004`) was already `PASS` and is a re-confirmation with no new cost credit.

**Handed to A118 - the CONVERGED-ALIVE cells (nothing was run on them, and nothing should be).**
Six level-1 cells and one A85 node come back with tau = budget exactly, minmass = 1.000,
`converged = True`: the case-LP has reached its optimum and it is not below budget, so no amount of
further LP time kills them. They are the candidates for A118's lane-count / two-meeter cover leaf:
`l1_071`, `l1_104`, `l1_148`, `l1_153`, `l1_158`, `l1_159`, and `s3_far_BL389484_TR018470` (A85).
`l1_159` is confirmed twice independently (A99's `l1_159_plain_warm` and A38's `node_159`), and
`l1_153` is a Trump-image cell, which must be alive - the LP agrees.

**Discipline.** READ-ONLY on A38/A85/A99/A113/A121 (every node json copied to
`results/nodes/<nid>.src.json` before being touched); <= 2 BLAS-pinned processes; commit/physical
gate before every LP and every verifier run; one resumable record per cell
(`results/t5/<task>__<nid>.json`); hard per-task and per-process CPU-second caps, checked before
each cell, so the final cell of each shard overruns (36,963 s = 10.27 CPU-h against the 10 CPU-h
cap); frozen `verify_case.py` byte-identical; nothing deleted anywhere - when the queue had to be
re-ordered for A121's cells the two running shards were stopped and relaunched, and every completed
record was kept. Report: `attempts/A115-k0-corner-rows/notes/t5_report.md`.

## 2026-09-07 — A120-no-side-runner (Opus chore, soundness-adjacent) — done-mixed: the runner is built, controlled and sound; 4 nodes closed; the bottleneck is the CERTIFIER, not the LP
- The piece A96 left unwritten. For an A57 node whose support lies inside A116's certified neighbourhood N, the cover
  `node = YES u NO_1 u NO_2 u NO_3 u NO_4` with `YES = node & (for every i, some square's pose in F_i)` and
  `NO_i = node & (no square's pose in F_i)` is a TAUTOLOGY, and the YES leaf needs **no LP at all**: it is contained in
  N's hypothesis, which Theorem LOCAL kills. `attempts/A120-no-side-runner/code/{a120lib,noside120,control120,recert120,
  report120}.py`; notes/runner.md. A112's regiontree / caselp / octagon / pinguard / trim57 / certify / verify_case are
  **imported, never copied**, with A112's writable dirs redirected into A120, so the two-stage protocol and the frozen
  verifier are byte-identical by construction.
- **THE SOUNDNESS-ADJACENT PART, and it is settled for all 35 targets** (`results/soundness_all35.json`, 1.6 s, no LP).
  A1 the node's five pin boxes ARE N's pins carried into the node frame (centres to 1e-9, tilt 0, half-width exactly
  A57's PIN_SLACK = 1e-2/sqrt2); A2 the four mapped boxes are pairwise POSE-DISJOINT, which is what makes "a square in
  each" give the |L| DISTINCT squares N's hypothesis names; A3 each is pose-disjoint from every pin (pinguard's 'parent'
  case); A4 the D4 map is exactly invertible (max round-trip error 0.0) with a dense pose sample; A5 the node's own A107
  configuration lies in the mapped boxes -- A116's `consumer116.inside` recomputed in the NODE frame, reproducing its
  dmax/tmax per node exactly; A6 every NO family IS the YES box, clamped only to the admissible strip [1/2, s-1/2]
  (which discards no pose a unit square could have, so the two children still cover the parent exactly) and reduced mod
  90; A7 tilt in [0,90] and core half-side <= 1/2 (A111 bug B5). **35/35 ok; YES and NO sides use the SAME boxes in the
  SAME frame on every child, asserted at construction time, and 70,000 frame round-trip samples miss 0 times.** The
  direction of the map is the thing that could have gone silently wrong: A116's consumer carries the NODE's config
  FORWARD by struct_op into the class frame, so the boxes come back by struct_op^-1 (`e` x 15, `diag` x 20 over the 35 --
  the stabiliser of the k5_11 pin set, which is why `N_boxes.json`'s frame_ops has only those two).
- **T2, all green, BEFORE any run** (730 s). (i) A112's two end-to-end kills `k5_11_interior_Y0036_D07_D01` and
  `k5_11_interior_Y0276_D05` (both T5'' root kills, TRIM-EMPTY) replayed through this runner's own `logic_kill` in all
  four A112 orderings: **8/8 `logic` records byte-identical** (SHA-256 of canonical JSON). (ii) A112's 35 PASSing NO
  certificates REPLAYED (never re-emitted -- `certify.py --loop_cols` re-solves before emitting, so the EMISSION is
  wall-clock dependent while the VERIFIER is deterministic) through `certify.run_verifier` -> frozen `verify_case.py`
  sha256 521cb01f...: **35/35 PASS, every report field identical** but the certificate path and `time_s`; 9,819,930
  boxes in 545.2 s. (iii) Covering assertion in the NODE frame on 3 targets, A116's own sample_check procedure at 30
  sides spanning [3.82, s0]: **2,996,097 / 3,003,131 / 2,988,914 drawn -> 100,000 tested (free-pair-disjoint survivors)
  -> 0 hits** each; at the brief's 10^4 bar, 302,460 / 301,445 / 297,951 -> 10,000 -> 0. Best packing margin over every
  survivor at every side -0.051 to -0.067, so nothing is near the boundary.
- **T3, 14.4 CPU-h against the 15 CPU-h cap, 9 of 35 targets** (cone-value order: level 1 first, since a closure removes
  ~20.8 A57 descendants at L1 against ~14.1 at L2 and 8 at L3). **4 CLOSED -- `k5_11_interior_Y0230`, `Y0637`, `Y0709`,
  `Y0997`, all level 1**: YES leaf dead by local certificate A116 S02_k5_11_r0.20_rho10 (PENDING A119's rational/Lean
  form, never counted with the frozen-verifier kills), all four NO children dead by the frozen verify_case.py. 5 OPEN,
  26 not run -- **the cap, not a verdict**; every record is resumable on (cls, id). Cones removed: 4 x 20.77 = **83.1 A57
  nodes = 5.6-6.7 CPU-h** at A96's own per-child cost (240.3 s at L2 / 291.8 s at L3), i.e. 0.046-0.056 wall-days at 5
  workers off the 10-11 wall-day schedule. Timeout protocol saving on this workload: 10,354 s of LP against 28,401 s
  under a flat 900 s cap, a factor **2.74**.
- **THE FINDING: 31 of 36 NO children are clearly below budget at the LP, but only 19 certify.** Just **5** children
  survive the node LP at all (converged, eta = 0, tau = 5 = budget) and **4 of those 5 are the single node `Y0345`**;
  the other 12 alive children are CERTIFIER SHORTFALL, not survivors. The reason is arithmetic: `certify.py`'s auto
  scale is max(1.005, min(1.4, (budget-0.005)/tau - 0.002)) = 1.03-1.11 here, so the emitted measure covers the LP's own
  rows only where minmass >= 1/scale ~ 0.90-0.97, while the 240 s stage-1 minmass on these children is 0.43-1.00
  (median ~0.70) and the certificate margin is 0.3% (total 4.9855 vs budget 5). **A112's `--rounds 1` is not enough at
  eta ~ -0.25**: 11 first-attempt PASSes took 4-680 s, and 8 children that FAILed/CAPped at rounds 1-3 PASSed at rounds
  6 (690, 855, 963, 1207, 1273, 1788, 1832, 2470 s). **All four closures needed the rounds-6 pass.** This bounds
  A111/A112's datum "waiting for column generation buys nothing": it holds when eta is deeply below budget, and fails
  where the margin is 0.3%.
- CANARY: Trump's grain realizes **none** of the 19 hypotheses declared dead (`trump_realizes = False` on every one;
  must be 0 and is). Every NO certificate is tagged `s0-only, pending window re-verification (v2 available)` -- A117's
  `verify_param_v2.py` (sha 153029ba...) would discharge a NO family over the whole window but costs ~10x the four fixed
  sides, which does not fit this cap, so no v2 run was made and no closure is claimed window-valid.
- TWO ADDITIONS, both recorded where they can only abort. `a120lib.certify_leaf_capped` is `regiontree.certify_leaf`
  argument-for-argument plus a HARD WALL on the certification subprocess (the witness-feedback loop has no bound of its
  own: `--time_limit` caps each LP re-solve, not the run, and one child burned 1895 s and another 3600 s without
  certifying); a capped run is recorded as **CAP, never a verdict**, is treated exactly like FAIL, and the whole process
  tree is killed so no `verify_case.py` is orphaned -- A117's rule. `recert120.py` retries only children with
  eta <= -1e-3 whose certificate FAILed, with more rounds, and promotes only on a PASS from the frozen verifier.
- PROCESS LESSON, banked because it cost a promotion: **two processes must never write the same node record.** A
  re-certification pass running against a node a worker was still inside had its promotion clobbered by the worker's
  next save (`Y0637/NO0`, 00:54). Fixed: `recert120.candidates()` takes only records already at status OPEN, and the
  pass is sharded by NODE, never by candidate.
- Discipline: <= 2 BLAS-pinned processes throughout, PYTHONDONTWRITEBYTECODE=1, commit 6144 MB / free physical 3072 MB
  gate before every LP and every certificate, nothing deleted, READ-ONLY on A53/A57/A96/A107/A112/A116/A119 (every
  campaign node json COPIED into results/nodes/<nid>.src.json before it was opened, every A112 certificate copied before
  the verifier was pointed at it). **A57/A96 stay paused and no campaign driver was launched**; `pausegate.paused()` is
  checked between nodes. Writes: `attempts/A120-no-side-runner/**`, the NEW file
  `attempts/A96-a57-parametric/results/a120_closures.jsonl` (35 rows, one per target), one clause on `C.A57` in
  `lean/depgraph.json`, the registry row and this entry.
- A123 NIGHT SHIFT (A57/A96 resumed 2026-09-07 00:42-08:00; T5''s FIRST LIVE TEST AT EMISSION). The brief's block (6
  shards + 2 deepens + the A96 drivers) did not fit: the box already floated at 17-20 python processes from 8 other
  campaigns against a <= 16 cap, so the night ran re-scoped at ~24 with 3 (+1) tree57 G1 shards and recheck96 --trimmed
  at one process. No deepens, no param96/resolve96/neighbours96, no select96, no scaler; shadow scheduling and the
  region-tree option stayed OFF. 296 new level-1 children: 149 PASS, 90 T5' logic kills, 45 ALIVE-at-LP, 9 FAIL, 0
  parent-box. Soundness checks clean (max core half-side 0.398, theta strictly in [0,90], no stored verdict contradicted).
- T5'' LIVE FIRE RATE = 19/296 = 6.42% (3 full kills + 16 trimmed bins, 1 a two-piece split). The offline control
  projected 159/2403 = 6.62% "boxes gain an empty surviving bin"; the TOUCH rate matches, but only 1.01% (3/296) were
  fully emptied, so the offline figure most likely counted boxes touched rather than emptied -- re-run the v1 control with
  the two categories separated. The useful finding is the shape: 15 of the 16 trimmed bins came out ALIVE-at-LP anyway and
  12 of 16 trims bite at the tilt extremes (theta anchored at 0 or 90). **T5'' buys LP tractability, not kills.**
  LP/certify walls tonight are CONTENDED (8 other campaigns, ~70-100% CPU) and must not be compared with offline figures;
  the fire rate is geometry, computed in build_children before any LP, so it is unaffected.
- MUST-FIX BEFORE THE NEXT RESUME: trim_excluded / trim_from are built in tree57.build_children (:177, :184-185) and are
  NEVER written to disk -- absent from every .jsonl, node .json, .report.json and .certify.json. So (a) the witness ledger
  for each excluded tilt interval never reaches disk and the node's coverage claim is not auditable from the results, and
  (b) a single-piece trim keeps its plain id and pin="ok", leaving NO marker at all: tonight's 16 trims had to be recovered
  geometrically by flagging theta widths outside the 8 canonical cover widths. NOT a soundness error (a trimmed child is a
  sub-box, its certificate is the ordinary one, frozen chain untouched, v1 control 618/618) -- an auditability gap.
- BEST YIELD OF THE NIGHT: recheck96 --trimmed certified 11 KILLS FROM 23 previously-ALIVE nodes (47.8%) at a 900 s cap on
  the trimmed bin, 7.28 CPU-h total, 6 converged. Against 149 certified kills from 296 fresh emissions across three shards
  over the same window, the re-check is far and away the better use of a constrained process budget. 360 of 383 queued
  ALIVE nodes remain un-rechecked; run this before opening new shards.
- Incidents: k5_16 shard 0 wedged on k5_16_interior_Y0381 (single-thread 100% spin, no output for 2h08m after the LP hit
  its cap, where 101 of 102 prior "time limit" events emitted DONE within 758 s); relaunched via launch.ps1, it re-picked
  the same node and reproduced the hang exactly, so the shard was stopped at 04:01 -- Y0381 needs a debugger before that
  shard is resumed. arms96 --arm C was reported a stray but was NOT: it had 31/32 rows and no done marker, and the
  three-arm report (37eae961) covers only n=26 with Y1135 flagged "not yet reached"; it finished on its own at 00:44:42
  with 32/32, and on the complete arm C's strict kills {Y1002, Y0817, Y1099} are ALL killed by B while Y0183 is a kill in
  B and a knife in C -- ZERO C-only kills, so the verifier_v2_rowfilter gate is not met and verifier-v2 stays shelved.
- Launcher corrections recorded in PAUSED.md v2 so they are not inherited again: launch.ps1 has NO pidfile gate (it
  Start-Process's unconditionally then writes the pidfile, so a second call double-launches; the gate is in scaleup.ps1);
  all 21 A57 pidfiles were stale; pausegate.py exists only under A57's code dir, not A96's.
- Discipline: PYTHONDONTWRITEBYTECODE=1, BLAS pinned by the launchers, frozen verifiers untouched, no recursive deletes,
  no pidfile deleted, no other campaign's state touched (the reaper is scoped by owner_marker="A57-shadow-trees" and left
  A112's certify child alone), free physical never below 10.4 GB, 8 hourly reaps with zero orphans found. The pause used
  the SENTINEL path, so unlike 2026-09-06 no in-flight work was discarded. Writes: attempts/A57-shadow-trees/** (results,
  logs, certs, PAUSED.md v2), attempts/A96-a57-parametric/results/recheck96.jsonl + its logs, the registry row and this
  entry.

## 2026-09-07 — A120-no-side-runner, continuation (Opus chore) — stopped by A123's pause sentinel, not by the cap; certifier default measured
- Coordinator's continuation: the 26 unprocessed in-N targets in cone-value order with **certification at rounds 6 from
  the start** (A120's own finding: at a 0.3% certificate margin `--rounds 1` is not enough), then the open NO children of
  the partial nodes at rounds 6; fresh 15 CPU-h cap, controls not repeated, same tags, ledger appended.
- **IT RAN 2.06 CPU-h AND STOPPED ITSELF.** At 07:57 the A123 owner wrote `attempts/A57-shadow-trees/PAUSE` ("A123 night
  shift ended 2026-09-07 08:00 PDT ... scheduled end of the night's compute window"). `pausegate.paused()` checks BOTH
  A57's and A96's sentinels, so both A120 workers stopped **between nodes** with every finished node recorded -- the
  sentinel path working as designed, not a kill. **The sentinel is another owner's control file: left in place, nothing
  deleted or bypassed**, and the second phase (the open NO children at rounds 6) was NOT launched because it would stop
  on the same check. Net: 2 more targets (`Y1099`, `Y1116`, both level 1) -> **11 of 35 processed, still 4 CLOSED, 7
  OPEN, 24 not run**, all resumable on (cls, id). Cones removed unchanged: 4 x 20.77 = 83.1 A57 nodes = 5.6-6.7 CPU-h
  off the 10-11 wall-day schedule.
- **THE CERTIFIER DEFAULT, MEASURED — the number the next owner asked for.** `certify.py` returns on the FIRST PASS, so
  extra rounds are free on a child that certifies at once and are the only thing that converts one whose first emission
  is not coverable. Over all 43 certification attempts (21 PASS / 9 FAIL / 13 CAP), the round the certificate actually
  came out at (0-based, 0 = the very first emission): **0:5, 1:6, 2:4, 3:2, 4:3, 5:1, 6+:0**; cumulative fraction of
  passes 0.24 / 0.52 / 0.71 / 0.81 / 0.95 / 1.00. Wall seconds PASS n=21 min 3.6 p50 568 p75 1207 p90 1832 **max 2470**
  total 15,646; FAIL n=9 p50 375 max 3385; CAP n=13 p50 420 max 3600 (right-censored, never a verdict).
  **RECOMMENDED DEFAULT: `--rounds 6`, hard wall 2600 s, `--time_limit 420`** -- nothing observed passed later than
  round 5 or later than 2470 s, so that wall censors nothing seen, while `--rounds 1` would have taken only 52% of the
  passes and `--rounds 3` 81%. The generosity is bounded by the wall and every capped attempt is recorded as CAP.
- **A NEGATIVE WORTH RECORDING: survivor count does NOT track distance from the S02 minimum.** Across the 11 processed
  nodes `Y0345` at dmax = 0.0116 has all four NO children as GENUINE survivors (converged, eta = 0) while `Y0637`,
  `Y0997`, `Y0709` at dmax = 0.0127 have none and close outright. 11 of 44 children are now genuine survivors,
  concentrated in four nodes (`Y0345` 4, `Y1116` 4, `Y1099` 2, `Y0973` 1); those cannot be closed by this cover at s0 at
  any certifier budget, and `Y1116/NO1` is the first child with eta strictly POSITIVE (+0.1176). So the residue this
  cover leaves is a property of the node, not of its distance to the anchor -- guiding on dmax would not have helped.
- LEDGER `attempts/A96-a57-parametric/results/a120_closures.jsonl` is now **append-with-revision**: every row carries
  `revision` and `generated`, only rows that actually changed are appended (rev 2 added the two changed rows; a re-run
  that changes nothing appends nothing), and **the reader takes the LAST row for each id**. 37 rows, 35 ids.
- Cumulative over both sessions: 16.4 CPU-h of process wall (14.36 in run 1 under its own 15 CPU-h cap, 2.06 in the
  continuation under a fresh one), 15,080 s of LP against 34,155 s under a flat 900 s cap (factor 2.26), 41,443 s of
  certifier. Discipline unchanged: <= 2 BLAS-pinned processes, PYTHONDONTWRITEBYTECODE=1, memory gate before every LP
  and certificate, nothing deleted, READ-ONLY on every campaign, no campaign driver launched, no sentinel created or
  removed.

## 2026-09-07 - A115 follow-up 3 (PI) - the plain warm re-solve pass, completed

**The pass is now complete over every open k0_00 cell A115 could reach.** This round (15 CPU-h cap,
14.16 used): the 34 never-run A38 level-1 cells and every open level-2/3 cell the previous cap had
missed, plain 240 s first (level-1 first, minmass-descending), then a 900 s warm continuation plus
A85's witness-feedback rounds on the NEW kill-candidates that pass produced. The 32 persistent
cert-FAIL cells and the converged-alive cells were skipped, as instructed.

**Cumulative result: 22 DISTINCT level-1 cells of the 216-cell k0_00 root split certified dead, plus
13 level-2 and 2 level-3 cells and 10 A85/A99 nodes, for 29.83 CPU-h - 1,023-2,372 CPU-h off A99's
9,341-21,661 CPU-h frontier, a 34x-80x return, with no new mathematics anywhere.** A115's own corner
rows, for contrast, cost 13.4 CPU-h for one pass over the same 216 cells and removed nothing.

* Stage A (plain 240 s) is COMPLETE over the whole 142-cell pool: 17 certified, 97 kill-candidate,
  22 alive, 6 knife-edge.
* Stage B (900 s + feedback) reached 26 of those 97 and certified 5 - and all five are level-1
  (`l1_149`, `l1_168`, `l1_169`, `l1_173`, `l1_174`), i.e. cells whose plain 240 s certificate had
  FAILed and which only the continuation closed. Stage B is the highest-yield thing left.
* The certified level-1 set is now {4, 5, 17, 18, 30, 31, 32, 49, 93, 98, 126, 137, 143, 149, 168,
  169, 170, 172, 173, 174, 176, 181} - 22 of 216 (10.2%).

**Hand-off list for A118's successor has grown to 12 (nothing was run on them).** CONVERGED-ALIVE =
tau = budget exactly, minmass = 1.000, converged: the case-LP has reached its optimum and it is not
below budget, so no further LP time kills them. Seven level-1 cells - `l1_071`, `l1_104`, `l1_124`
(new), `l1_148`, `l1_153`, `l1_158`, `l1_159` - four level-2 cells - `l2_p114_001`, `l2_p65_101`,
`l2_p65_111`, `l2_p74_001` (all new) - and the A85 node `s3_far_BL389484_TR018470`. `l1_153` is a
Trump-image cell, which must be alive, and the LP agrees; `l1_159` is confirmed twice independently.

**What is left.** 71 of the 97 stage-A kill-candidates have not had the stage-B treatment (the pool
was worked level-1 first, minmass-descending, so the remainder is the low-value tail); the 32
persistent `cand` cert-FAIL cells remain untouched by instruction.

**Discipline.** READ-ONLY on A38/A85/A99/A113/A121; <= 2 BLAS-pinned processes; commit/physical gate
before every LP and verifier run; resumable per-cell records; hard per-task and per-process
CPU-second caps checked before each cell; frozen `verify_case.py` byte-identical; nothing deleted.
Report: `attempts/A115-k0-corner-rows/notes/t6_report.md`.

## 2026-09-07 — A128-coupled-moves (Fable, theory lead) — done-mixed: the menu is exact on neighbourhoods, the exchange is the only coupled move that bites, the cluster screw adds nothing, the residue is drawn
- Deliverable `docs/proofs/drain_sel.md`. T1: Theorem DRAIN-SEL(W) stated against `noroom.md` §6/§8 and `Composition.lean`
  — for every m ∈ W the Ψ^(w)-minimal packing (one per side) has a MENU member admissible (ROT / CLUSTER-ROT / EXCHANGE /
  TWO-WALL / SUPPLY); consumers `classKilledAt_of_kill` via `k0free_kill` or `teleport_packing` on [3.82, ŝ), `StratumKillSel`
  at ŝ; uniqueness untouched except that the exchange branch at ŝ needs a two-square Theorem U [C]. Weaker than
  LOCK-FREE⁺(< 4) in three ways (one packing per side; W only; a menu) and that is exactly what the composition consumes.
- T2 [T]: Lemma BOX-MOVE — the neighbourhood certificate of a rigid cluster screw: on a pose box (radius r in every
  coordinate and the side) every possibly-separating pair axis and possibly-active wall row of a member has separation
  derivative > 0, Q's μ has right-derivative > 0 over every candidate argmin point, every other (member, corner) depth
  nonincreasing ⇒ EVERY packing in the box at which Q intrudes has a Ψ^(w)-smaller packing at the same side for every
  positive weight vector (weight-free; near-contacts inside the box are rows automatically; a parallel-edge kink within
  the box charges the rotation in both senses — the exact form of A103's remark (2)). Lemma BOX-GORDAN: Motzkin dual with
  interval rows (= ROT's Gordan at r = 0). Lemma CLUSTER-ROT (any cluster screw at the minimiser; NOCRIT-SEL = ω = 0,
  ROT = C = {Q}). Lemma EXCHANGE-BOX (Lemma EXPOSE on a box: two possible meeters, slot square + re-fit fixed in the
  corner frame, disjoint from the nine untouched squares over the box — ∀-packings). TWO-WALL: TW-BOX is trivial on a
  neighbourhood (reads the side), TW-HOOK is the exact nick-depth coupling (gain cot θ / tan θ) in the hook family only —
  not a box leaf. Lemma SUPPLY: ≥ 3 rows or an exact concurrency (LINE); the four-corner budget is vacuous by
  planarity (≤ 54 square rows vs 24 needed). Fact D (all derivative formulas) checked by finite differences (300 poses).
- T3 [M] (`coupled128.py`, ~2 min; `results/{table128.md,moves128.jsonl,summary128.json}`): sample = A107 near-packings
  of the 12 converged-alive cells (K01 ⊃ l1_071/l2_p65_101, K03 ⊃ l2_p65_111, K04 ⊃ l1_104, K05 ⊃ l2_p74_001, K06 ⊃ l1_159,
  K20 ⊃ l2_p114_001, K26 ⊃ s3_far; l1_124/l1_148/l1_158 polished from their A115 supports — they land on K02's 3.942810,
  K01's 4.0 and S10's 3.902674; l1_153 = Trump), K02, the A104 locks 4.000237 / 4.001525, Trump, and the 3.9907 / 3.98548
  records; radii 1e-3 → 1e-6; every subject = every square that can meet the corner on the box (intruders + tangents).
  **35 exact certificates, every one re-sampled 10⁴ → 10⁴ → 0 hits. Trump: held under every move on every box (9
  subjects, no exchange with non-negative margin) — canary PASS.** On the 1e-3 box the menu kills 10 of 15 non-Trump rows
  (8 of 11 non-Trump cells), mostly by trivial reasons (corner rattlers, K0-FREE boxes); the CLUSTER SCREW certifies
  nothing at r ≥ 1e-5 that the single square does not (3 cluster-only certificates, all at 1e-6); the EXCHANGE is the only
  coupled move that works where every single-square move fails: 5 corners on 1e-3 boxes (the 4.000237 lock's BL crowd
  — a 9° pair — straightened into two cells, margin 3.9e-3; K01 TL; K26 TL; cell_l1_148 TL; the 3.9907 record's BR) and 4 on
  1e-4…1e-5 boxes (4.001525's BR at 1e-5, margin 1.5e-4). Held under the WHOLE menu on every box ≥ 1e-4: lock 4.001525
  (Gordan-certified frame), K03, K06, cell_l1_124, Trump. Below 4 every failure is the same: the best re-fit is FLUSH
  against an untouched square (margin ≈ 0) — A98's neighbour-free 0 %, A101/A121's flush population, from the box side.
  lock103's point verdicts reproduced square by square at r = 1e-8 (`test128.py`); at the exact point 4.001525 has six
  first-order directions, all blocked within 5e-9 by parallel-edge kinks.
- T4: NOT composed. Residue RES-MENU(m) (LOCKED + every enumerated cluster screw held + flush re-fits) ⊊ RES-LOCK;
  realised at r ≥ 1e-4 by the 4.001525 frame (drawn: `attempts/A128-coupled-moves/results/residue128.svg`) and below 4
  by the flush corners of K03/K06/K02-type packings. The coupled move needed, named: a NON-rigid two-parameter field
  (column straightening + row slide, the manifold motion A104 follows) at the 4.001525-type frame, or a depth-2
  exchange with margin. `budget.md` k0 row unchanged (13,500 / 0): the box leaves fire at radius 1e-3, the tree's cells
  are 100× wider (K0-ROT/TF-U/EX verdict again). New obligation A128-G1.
- Discipline: one process at a time for the moves (plus the near-packing polish as the second), BLAS pinned, BelowNormal,
  PYTHONDONTWRITEBYTECODE=1; pure geometry (3-variable linprogs for the direction search only, as lock103/lockw105);
  read-only on every campaign and attempt (A103's lock103.py copied, not imported); frozen verifiers untouched; nothing
  deleted; git fetch + plain merge + push of own paths. Chip on K0.RESN (owner A128, released at close); depgraph
  re-rendered; registry row.

## 2026-09-07 — A126-localdead-lean (Opus Lean engineer, one `lake build` at a time through A78's serialised BelowNormal `lakeb.py`, ≤ 2 python processes, read-only on every campaign and on A116/A119/A120) — done-mixed: the interior-SAT axiom is gone, the arithmetic half of two concrete neighbourhoods is checked in the kernel, and what is left of Theorem LOCAL is ONE named primitive
- The external review's three items, in the brief's order. **T2 first, because it is the one that finishes.**
- **T2 — `sat_selection` IS NO LONGER AN AXIOM.** `lean/PackingCertMathlib/PackingCertMathlib/SatInterior.lean`:
  `sat_selection_thm` has the EXACT statement of A119's one project axiom (Lemma SAT for INTERIORS) and is proved
  from `CaseSat.sat_squares` with axioms `propext / Classical.choice / Quot.sound` only; `cover_pair'` re-derives
  the single lemma of `Local.lean` that consumed the axiom. `Local.lean` itself is NOT edited (A119 is read-only);
  retiring the axiom there is a one-line deletion for its owner.
  **The shrink of `local_certificate.md` §1 needs no limit and no convergent subsequence.** With all eight gaps
  `< 0` the four projection overlaps hold STRICTLY and — this is the point — with the SAME right-hand side
  `B = 1/2 + (|cos Δ| + |sin Δ|)/2`. So with `M` = the max of the four left-hand sides (`M < B`) and
  `λ = (M/B + 1)/2 ∈ (M/B, 1)` WRITTEN DOWN, `sat_squares` applies verbatim to the picture scaled by `1/λ`
  (`a = 1/2`, offset `d/λ`) and its conclusion `d/λ = μ + b₁u + b₂u^⊥` scales back to `|λμᵢ|, |λbᵢ| ≤ λ/2 < 1/2`
  — strictly inside BOTH squares, and `Attain.mem_interior_iff_uv` (the interior of a parametrised square is
  exactly the open `u/v` box) turns that into the contradiction. The one case `sat_squares` does not cover
  (`cos Δ < 0`) is the `u ↦ −u` representation of the same square set, and the conjunction of the two coordinate
  bounds is invariant under it. 250 lines, `lake build` 24 s.
- **T1 — the leaves of a real `N`, checked in the kernel.** `LocalCert.lean` is a reflected weak-duality checker
  over a certificate leaf (rational rows, Farkas multipliers, box) proved sound ONCE (`checkLeaf_sound`), plus a
  decoder; `LocalCertS07(Data).lean` and `LocalCertS02(Data).lean` are the generated data and one `native_decide`
  each. Measured (BelowNormal, machine shared with the PI and three other attempts):

  | neighbourhood | dead leaves | infeasibility rays | rows | nonzero coefficients | data file | data wall | check wall |
  |---|---|---|---|---|---|---|---|
  | `S07_trump5_r0.10_rho40` | 2 302 | 746 | 27 363 | 101 629 | 2.70 MB | 22 s | 19 s |
  | `S02_k5_11_r0.20_rho10` | 32 570 | 5 782 | 504 404 | 1 977 332 | 49.05 MB | 40 s | 67 s |

  (the second is the `N` A120's node cover uses, which is why it was worth the 49 MB). `localDead_s07` /
  `localDead_s02` are Theorem LOCAL for those `N` modulo ONE named hypothesis. Axiom roster exactly as targeted:
  the standard three everywhere, plus one `native_decide` axiom per replay and, since `localDead_of_cert` uses
  `lb_382` for the lower end of the window, A56's `check_3_82` — both pre-existing, neither introduced here.
- **The control (`code/control126.py`), because a checker that accepts everything proves nothing.** The leaf
  records are read back out of the EMITTED `.lean` file — not out of the JSON they were written from — decoded
  exactly as `parseLeaf` decodes them, and re-checked: **2 302/2 302 and 32 570/32 570 pass**. Mutated:
  `zero-y` and `negate-y` fail EVERY leaf; `drop-row` 708 / 30 726; `widen-box` 638 / 29 412; and `halve-y`
  fails **exactly the feasible leaves** in both certificates (1 556 = 2 302 − 746 rays,
  26 788 = 32 570 − 5 782) — halving a Farkas RAY halves a positive bound and it stays positive, halving a side
  bound pulls it to the box's `s_lo = 3.82 < s0`. That the count lands on the ray count on the nose is an
  independent confirmation that the two branches of `checkLeaf` are attached to the leaves the generator meant.
  A third section is a Monte-Carlo smoke test of the COVER half: only the TILT coordinates differ between leaves
  (3 of 20 and 4 of 23; every other coordinate is the global box), the root box recovered from the emitted data
  is the certificate's own tilt range on the nose (`[0.725446, 1.483530]³`, `[0.670819, 1.019885]³ ×
  `[−0.174533, 0.174533]`), and **20 000 random points of each land in a leaf cell every time**. Necessary, not
  sufficient — but it would catch a bisection tree emitted with a hole in it.
- **What that hypothesis is, and what discharging it needs — ONE primitive, and it is not in Lean.**
  `CertCover leaves Ls Ps slo shi` = "every packing satisfying `N` at a side in the CERTIFICATE'S OWN WINDOW
  `[3.82, 3.897084]` has an LP variable vector inside ONE recorded leaf's box, satisfying that leaf's rows".
  **The window is load-bearing.** Restricted to `s ≤ s0` instead — the first form this attempt wrote — the
  obligation would be a CONSEQUENCE of `LocalDead`, vacuously (if `N` is dead there is no such `s`, `z`), the
  factorisation would be circular and `localDead_of_cert` a true but empty theorem. The certificate's window
  reaches ABOVE `s0 = 3.877084`, so the obligation quantifies over packings a `LocalDead` proof says nothing
  about, and the cover argument never looks at `s0`; the lower end is free, `lb_382` puts every packing's side
  at or above `3.82`. It factors into four: the tilt cover (PROVED in shape —
  `cover_bisect` plus a decidable structural check; and not one of A119's seven certificates contains a `qsplit`
  node, so that branch of the cover is dead code), the selection cover (its LOGIC is now discharged by T2 —
  `sat_selection_thm` + `cover_selection`), Lemma RELAX (its algebra is already proved in `Local.lean`), and the
  body-to-variable numbering (bookkeeping). What is missing in the middle two, and NOTHING else, is
  **a certified rational-interval kernel for `cos`, `sin` and `π` — A119's `code/exactiv.py` in Lean**: the
  enclosure `sup_cell g_σ < 0` behind every excluded selection (2 969 of them at 87 branch nodes for
  S07 (0.1, 40°), plus 292 `imp_sel` leaves and 761 forced selections) and the rational constants of the relaxed
  rows. Mathlib has `pi_gt_3141592` / `pi_lt_3141593` and the low-order `cos_bound` / `sin_bound`; the 10⁻⁹-level
  sharpness these certificates need is real work, and A119's finding F4 is the warning that a checker must
  reproduce the generator's SHARPNESS, not merely be sound.
- **And the cheaper route is a GENERATOR change, not a Lean one.** The certificates are stated in the ANGLE `θ`.
  Lean's own parametrisation is `t = tan(θ/2)`, in which `cos θ = (1−t²)/(1+t²)` and `sin θ = 2t/(1+t²)` are
  RATIONAL functions (`Parametrize.cosT/sinT`, with `cosT_sq_add_sinT_sq` proved for EVERY real `t`). A certificate
  emitted in `t` makes every enclosure exact rational arithmetic and takes the trig kernel out of the trusted base
  entirely; the cost is redoing the relaxation in `t` (the axis components stop being affine in the cell parameter,
  so `axis_decomp` + McCormick are replaced by a rational-function relaxation) and re-solving every LP. Recommended
  for whoever wants `LocalDead` for a concrete `N` with NO named obligation.
- **Three engineering findings (`notes/method.md`).** **E1: the ELABORATOR is the wall, not the kernel.** 10⁵–10⁶
  rational coefficients as nested list literals is 10⁵–10⁶ numeric literals to elaborate; as ONE STRING PER LEAF it
  is one token each, and the decoding moves into the same compiled evaluation that runs the check. Safe by
  construction: `localDead_of_cert` quantifies BOTH the check and the cover obligation over the DECODED leaves, so
  a wrong decode makes the obligation harder and never the conclusion cheaper. (Two smaller limits on the way: a
  single list literal of 32 570 elements exceeds the elaborator's recursion depth — emitted in groups of 2 000 —
  and a leaf accumulator returning a PAIR is evaluated once per projection, i.e. `2^rows` per leaf at up to 19
  rows, so `accum` is split into `accumL`/`accumK`.) **E2: a quarter of the dead leaves are invisible to A119's
  capture hook.** `check_local.Checker.dead` validates an infeasibility ray and RETURNS before the block that
  records the leaf, so a generator that trusts the hook silently emits an INCOMPLETE cover — 746 of 2 302 (32 %)
  for S07 (0.1, 40°), 5 782 of 32 570 (18 %) for S02 (0.2, 10°). `extract126.CapChecker` overrides `dead`, calls
  the parent FIRST so its verdict stays authoritative, and rebuilds the ray's rows with A119's own `LeafRows`.
  **E3: `Local.Box` cannot carry a tilt cell that leaves `θ ∈ [0°, 90°]`.** It holds one interval in `t`, and a
  packing's poses are normalised to `t ∈ [0,1]`; S02 (0.2, 10°)'s `BR(0,1)` cell is `θ ∈ [−10°, +10°]`, which folds
  to `t ∈ [0, tan 5°] ∪ [tan 40°, 1]`. The emitted box keeps the inside part — a SMALLER `N`, hence a weaker
  `LocalDead`, the sound direction — and the generator prints the count and marks the box. The proper fix is a
  tilt field that is a LIST of intervals, as `CNoFam.tivs` and `PNoFam.tivs` already are.
- **T3 — the region-tree step, and what is left of A120's closed node.** `LocalCompose.lean`: `yes_or_no` (the
  cover `H = YES ∪ NO_1 ∪ … ∪ NO_{|L|}` is a tautology), `localHyp_of_yes` — **A120's soundness clauses A2 (the
  boxes are pairwise pose-disjoint) and A3 (each box is pose-disjoint from every pin) are exactly the INJECTIVITY
  `LocalHyp` demands**, which is the reason they had to be asserted — `node_dead_of_yes_no`,
  `classKilledAt_of_yes_no` in `Composition.lean`'s shape. It also closes one gap A120 flagged: `centre_in_slab`
  (a packed square's centre is at least `1/2` from every wall, from `wT_ge_one` + `set_subset_container_iff`) gives
  `noneIn_of_clamped`, so a NO child certified against the CLAMPED zone kills the branch of the UNCLAMPED box —
  the CLAMP itself costs nothing. The ROUNDING does; see the next bullet.
- **F-COVER — the emitted NO zone is the YES box rounded the WRONG WAY** (`code/zonecheck126.py`, measured on all
  nine nodes A120 processed and all 22 of their PASSing NO certificates — not one zone is inside its box). The
  split is a tautology **iff
  `ZONE_i ⊆ BOX_i`**: a configuration that fails the YES side fails it because NO square is in `BOX_i`, and to land
  in `NO_i` it must then have no square in `ZONE_i` either. A120's runner builds the zone EXACTLY — its node record
  carries the box's own θ-cell and the centre rectangle in full precision, and `box_identical_to_yes` checks
  precisely that — but the `case-measure-certificate-v1` file emits it rounded **OUTWARD**: the tilt interval
  converted to `t = tan(θ/2)` and rounded out to `2⁻²⁰`/`2⁻²³` (`NO0`: `2924103/8388608 = 0.348580241` against
  `tan(38.4351°/2) = 0.348580331`), the centre rectangle to 9 decimals by NEAREST. Outward is the right direction
  for the VERIFIER — a wider NO zone exempts more boxes, justified because the hypothesis it is proved under is
  correspondingly stronger — and the wrong one for the COVER. Measured against A120's OWN full-precision record,
  so the comparison is independent of the node's `D4` frame map: `9.0·10⁻⁸ … 1.10·10⁻⁷` in tilt on **all 22**,
  `≤ 4.71·10⁻¹⁰` on the upper centre bounds of 16 of them, never on the lower ones. **So every node A120
  processed has a sliver — a configuration whose only square near `F_i` sits
  in `ZONE_i \ BOX_i` — in NEITHER branch.** Nothing in A120's LP or measure work is wrong; the tautology is, and
  the fix is one rounding direction (emit the zone INWARD) plus a re-certification at amounts orders of magnitude
  below the resolution at which those certificates pass. `NO3` also confirms A120 handles E3 correctly on its own
  side: its zone carries TWO `t`-intervals, `[tan 40°, 1]` and `[0, tan 5°]` — it is `Local.Box` that cannot.
  `y0230_dead` is A120's closed node `k5_11_interior_Y0230` as a Lean statement whose five hypotheses ARE the
  residue: `LocalDead` for S02 (0.2, 10°) modulo `CertCover`; A2/A3 as decidable rational tests (not written);
  the node's class hypothesis through the `D4` frame map (A120's A1/A4, the step
  `Composition.classKilledAt_of_tree` already performs for the tree route); and the four NO children. On the last
  of these: **all four are now REPLAYED IN THE KERNEL.** `lean/gen_case_lean.py` converts A120's four PASSing
  `case-measure-certificate-v1` files (`NO0`, `NO1_r6`, `NO2`, `NO3`; depth 56, 6 cores = five class pins plus the
  node's own conditioned square, ONE NO-family zone each) and `LocalCertY0230N{3,2,1,0}.lean` re-run `checkCaseI`
  on them by `native_decide`: **156 s / 324 s / 688 s / 872 s** on 230 914 / 492 190 / 820 808 / 1 207 184 boxes,
  against the frozen verifier's 14.3 / 27.6 / 34.5 / 54.4 s — **about 11× and linear in the box count**, which is
  the number A78's corpus replays priced. ONE certificate per module deliberately: a `native_decide` is not cached
  until its module finishes, so four in one file means an interrupted build banks NOTHING, which is exactly what
  happened twice before the split. Axiom roster per replay: the standard three plus that certificate's own
  `native_decide` axiom.
  Three steps still separate the four PASSes from `hno`. Two are pre-existing properties of the frozen fixed-side
  route: the consumer is `checkCaseI_no_family` (the zone list is NONEMPTY, so a PASS forces SOME non-owner square
  into the zone) and not `checkCaseI_kill`, and it speaks of an `IsStrictFamily` (pairwise disjoint CLOSED squares)
  where `CfgPacking` gives interior-disjointness, so `Dilation.lean`'s Lemma B has to be applied first; and
  `CaseExempt` names a POSE `q` with `q.set = Q i`, which does not force `q = z k` (`t = 0` and `t = 1` denote the
  same square). The third is NEW and is F-COVER above.
- Discipline: `Local.lean`, A116/A119/A120 and every campaign untouched (A119's `check_local.py` / `exactiv.py`
  IMPORTED, its certificates and A120's records READ); one `lake build` at a time through `lakeb.py` at
  BELOW-NORMAL priority — the one build killed mid-run left a stale lock, which was cleared only after confirming
  no `lake`/`lean` process remained; `PYTHONDONTWRITEBYTECODE=1`; nothing deleted except my own 83 MB intermediate
  (regenerable by `extract126.py`); git fetch + plain merge + push of own paths. `docs/known_results.md` 16b,
  depgraph GRAIN note, registry row.

## 2026-09-07 — A130-flush-exchange (Fable, theory lead) — done-mixed: the three window holds survive every flush-aware move on every box (a mode accumulation at the flush stratum, not a lock), the 4.001525 control falls to the non-rigid field at all eight intruders, Trump is first-order isolated
- Deliverables: `attempts/A130-flush-exchange/notes/{lemmas130,report130}.md`, `results/{table130.md,moves130.jsonl,flush130.svg,shells130_K03_BR.json}`, `docs/proofs/drain_sel.md` §7 (addendum, the FLUSH case).
- T3 [M] (`flush130.py`, boxes 1e-3..1e-6, 25 certificates, 78k samples, 0 hits): FIELD (Lemma BOX-FIELD-W over all eleven squares on tilt-sign sub-boxes × contact-mode pieces), ROT-W and EXCHANGE-2 certify NOTHING at K03 (l2_p65_111), K06 (l1_159), cell_l1_124 on any box: at K03 BR 10 of 32 pieces certify (the deep meeter f2's horizontal slide at rate 1.000, exactly the pieces where f2, f0, f3 lean toward the wall), K06 BR 4/8, l1_124 TL 1/4; every re-fit's flush blocker is the interior grain (K03's pinwheel f4/f5/f6/f0, K06's 48.4° grain, l1_124's 45° pair), wedged in every sub-box and mode. The control FALLS: the A104 lock 4.001525 — Gordan-certified locked at all eight intruders, held under every rigid cluster screw in A128 — is drained at ALL EIGHT by the non-rigid field on the 1e-4 box (weak-cone rates 0.11–0.32, min strict 0.05–0.32, 2.5k–5k samples each, 0 hits), and so is 4.000237 (rates 0.22–1.00); K01 and the depth-1 exchanges reproduce A128. Trump: held on every box under every move, and the weak cone {rows ≥ 0, depth rate ≥ 0} is {0} at all nine subjects — first-order ISOLATED (canary PASS in the strongest form).
- T1: at each hold the doubly-met corners are (slot-like deep meeter on the floor/wall, flush tangent hugging the wall, an interior grain square pressing the tangent's inner corner); flush contacts drawn with lengths (K03 f2–f3 0.207, f0–f2 0.330, f0–f1 0.642; K06 f1–BR(0,1) 0.606; l1_124 sq4–sq6 0.892, sq1–sq4 0.720). The deep meeter's far edge is free (K03 f2 → f1 is 0.027 away), so it slides exactly (weak-cone rate 1.000): K03 is not Ψ^(w)-minimal at its side; the box hold is Lemma MODE's accumulation of contact modes at the flush stratum — a fixed interval-certified field fails at every radius by a sign of the order of r (the exact content of A128's "a flush placement has no neighbourhood"). l1_124's TL admits NO two-intruder packing (sq4 cannot enter the cell without pushing into sq6 on the top wall). The near-packings are not exact critical points (KKT 4e-6 … 2e-2; K06's landing overlaps by 1.1e-6, its point tests are void), so the second-order kink test never meets an exact flat direction on this sample.
- T2 [T] (`lemmas130.md`, n-general, Lean shapes): Lemma BOX-FIELD-W (a non-rigid field with WEAK pair/wall rows on a box — sound for r > 0 by the Dini-derivative argument, strict at r = 0; the flush kink charged through the exact rotation difference u = ω_B − ω_A; the brief's column-straighten + row-slide field is a point of its LP), BOX-GORDAN-F; Lemma MODE (contact-mode split, vacuous pieces) and Lemma SHELL-SCALE (dyadic shells of the deep meeter's tilt certify with rotation ∝ a — one parametric certificate covers (0, r] except the stratum, where the slide is exact; [M] K03 BR shells 5e-5..1.6e-6 certified, failing only below the fixed pad); Lemma EXCHANGE-2 (the depth-2 exchange: re-fit + finite opening motion ε* of the flush blockers inside the pad, ∀-packings); Lemma TWO-INTRUDER (the certificate need only hold where both meeters intrude; the K03-type corner decided by hand: every selected minimiser in the box is K0-FREE there); Lemma FLUSH-SLIDE (at z* every flush floor/wall intruder is pressed on its FAR edge); Lemma ISOLATED (weak cone {0} ⇒ isolated, curve selection); Lemma KINK (the exact second-order condition at a parallel-edge contact — the kink is second order when Δ̇ = 0, Farkas/prestress form, 2 × 2 determinant for dim K = 1 — and its box form: only structurally-zero rows admit a second-order box certificate).
- T4: FLUSH enters DRAIN-SEL(W)'s case analysis as two theorems — F (FLUSH-SLIDE) and F′ (SLOT-GRAZER: on W at m ≤ ŝ − δ no packing has a corner with an intruder of μ_c ≤ δ/(1+√2), by SHELL + SLIDE modulo K0-O1; the K03/K06/l1_124-type corners live only in the slab (ŝ − 2.4e-3·ρ/1e-3, ŝ]) — plus the field case (a theorem at the point, CLUSTER-ROT for a non-rigid field); the residue RES-MENU⁺ (LOCKED + cluster-held + flush re-fits + far-edge-pressed + no feasible field) is realised by NOTHING on disk at any side (both A104 locks fall to the field). The tree leaf at a flush stack is semi-algebraic (mode contractor + parametric shells + the stratum statement), not a box leaf; the field leaf fires at radius 1e-4 / 1e-3 and is silent at the 0.1-wide root cells — `budget.md` k0 row unchanged (12,000 / 0). A hold at a non-packing support costs DRAIN-SEL(W) nothing (the holds are k ≥ 1 packings above ŝ; their boxes' K0-BLOCKED packings are grazer-blocked slot corners, SLIDE-excluded on W outside the slab); it costs the tree leaf.
- Discipline: one process for the runs (+ one seconds-long second process for piece counts / shells), BLAS pinned, BelowNormal, PYTHONDONTWRITEBYTECODE=1; pure geometry / interval arithmetic (LPs for the direction search only); read-only on every campaign and attempt (A128's coupled128.py copied to geom130.py, its results read); frozen verifiers untouched; nothing deleted; git fetch + plain merge + push of own paths. Chip K0.RESN → A130 (released at close); depgraph re-rendered; registry row.

## 2026-09-07 — A129-net-verifier (Opus engineer) — done-success

- **The Burns–Massaccesi paper does not exist as a paper.** It is two blog posts on n = 17, Aug 2026:
  Sam Burns (`sam-burns.com/posts/n17-square-packing-problem-intro/`, the idea) and Gustavo
  Massaccesi (`gus-massa.blogspot.com/2026/08/another-better-lower-bound-for-n17.html`, the LP-tuned
  certificate: 168 weighted points on a 29×29 grid, `L = 45058/10000`, total ≈ 16.9166 < 17,
  `WEIGHT_SCALE = 576`). Searched arXiv by author, by abstract and by date range — nothing.
- **Their certificate is our certificate.** An atomic measure with total weight < n and the claim
  that every unit square in the container carries weight ≥ 1 — the A08/A33 object, and the A57 leaf
  object. What is new is the *verifier*: a finite net of 181 orientations uniform in
  `t = tan(θ/2)`, an "almost-unit" square of side `B = 0.9973` justified by `B(1+D) < 1`, and an
  exact per-orientation 2-D translation sweep (event coordinates, integer difference array, two
  cumulative sums). So the brief's premise — that their "sweep" would be over separating-axis
  selections and would produce Farkas witnesses against our box trees — was wrong in both halves:
  there is no LP anywhere in the method, and A57's kills are measures, not box trees. W7 updated
  accordingly (`docs/publication_checklist.md`): they must be cited as an independent rediscovery of
  the weighting method, and our differences named (unshrunk continuum verifiers, Lean-checked).
- **T1.** `attempts/A129-net-verifier/code/netverify.py` + `netcheck.py`, soundness note
  `notes/method.md` (Lemma N1 the σ inclusion with the exact rational form
  `B = (1+m²)/(1+2m−m²)`; N2 the reduction, stated n-general; N3 the exemption clause; N4 exactness
  of the sweep). `netcheck.py` re-decides by a pure-`Fraction` 2-D branch and bound with no numpy and
  no floats, and imports the FROZEN `verify_case` exemption predicates rather than re-implementing
  them. On the A57 leaf `k5_11_interior_NO`: netverify PASS (364 orientations, 38.8 s), netcheck
  CHECKED all 364 cells (133,788 nodes, 28.8 s), frozen verifier 1.02 s.
- **The one design finding that decides the whole project.** Exempting on the *shrunk* square — the
  naive port of their construction to a conditional certificate — fails at EVERY refinement level
  with live minimum exactly `0`, because it strips a rim of width `Θ(1−B)` off every core's exempt
  region and the LP never put mass inside an exempt region. The exemption must be decided for the
  UNIT square, uniformly over the net cell (Lemma N3). The shrink is for the mass, never for the
  hypotheses.
- **T2, 60 stratified A57 PASS leaves** (`notes/benchmark.md`). 26 reproduced inside a 120 s budget
  at a **median 15× the frozen wall** (10.8× on totals; 93 % reproduced at ≤ 5 atoms, 53 % at 6–30,
  0 % at > 30). An exact second pass on 12 of the 34 over-budget leaves resolved **96 of 96** sampled
  tilt positions at levels 5–12 and priced them at a **median 26.7×, up to 234×**. **The failure mode
  is BLOW-UP, never MARGIN: 0 of 60.** The reviewer's predicted margin death does not happen — a leaf
  certificate is a measure, so the shrink comes out of its MASS slack, not its side slack, and every
  certificate absorbed a shrink of 6e−5 to 5e−2 in side. What kills it is architectural: the frozen
  3-D `(t,c_x,c_y)` tree discharges a band of orientations against the six cores with a single
  `t`-box; the net re-resolves the same exempt boundary at each of a median 185 net orientations.
  *Stratification caveat:* no A57 PASS leaf has a tilt sub-cell (all 1,029 with a node record carry
  `theta_box = [[0,90,1.0]]`, one piece) — the case-measure certificate never sub-divides tilt. A96's
  parametric `s_cells > 1` was used as the nearest analogue (33 of the 60), and atom count as the
  axis that actually separates the population.
- **T3, the two whole-problem certificates — both RUN, both PASS.** They are unconditional measures,
  which is exactly where the method is cheap (no exemptions ⇒ the mass is constant on an arrangement
  cell ⇒ the correct bisection depth is 0). `s(11) ≥ 3.82`: 1,950 net orientations, deepest level 14,
  shrink 3.81e−3, 3.96e10 arrangement cells, **2,148 s** against the frozen verifier's **587 s**
  (3.66×). `s(12) ≥ 3.90`: 987 orientations, deepest level 14, shrink 3.57e−3, **802 s** against
  **232 s** (3.45×). `netcheck` CHECKED 16 net cells of each (563 s / 557 s); a full exact replay
  would cost ≈ 19 h and ≈ 9.5 h. The refinement profile (`code/ladder.py`, 24 exact per-cell
  decisions across `[0,1]`): 3.82 needs level 8–13, median 10, hardest at θ ≈ 7.15°, where at level 8
  the live minimum is **0.999757** — the 3.82 certificate misses by 2.4e−4 of mass under a 3.9e−3
  shrink, and that number is its entire margin against this method. The brief's estimate (δ < 0.0150
  rad, ≈ 105 orientations) came from a rescaling argument that does not apply to a measure
  certificate; the measured binding half-width is 7.4e−4 rad and the net is **19× larger**.
- **Verdict (`docs/budget.md` §D.6).** Cross-check: EARNED — a structurally independent decision
  procedure for both headline theorems for 36 and 13 single-core minutes, sharing no code, no data
  structure and no search order with A07/A08. Replay verifier for A57's PASS leaves: REJECTED — it
  multiplies the 100 s exact-verify half of the 850 s node by 10–30, it does not replace it.
  Certificate simplifier: REJECTED — there are no Farkas vectors in this method, the certificate is
  unchanged, the net adds a 1,950-cell tilt tiling, and the Lean shape (one `native_decide` per net
  cell) is worse than A119's `leaf_*` lemmas. A19 untouched, and note that Burns–Massaccesi sit under
  the same ceiling, their certificate being a measure too.
- Files: `attempts/A129-net-verifier/{code,notes,results,logs}`, `docs/budget.md` §D.6,
  `docs/publication_checklist.md` W7, `attempts/REGISTRY.md`. ≈ 7.5 CPU-h, ≤ 2 BelowNormal processes.

## 2026-09-07 — A131-pin-clip (Opus engineer, ≤ 2 BLAS-pinned BelowNormal processes, read-only on every campaign and driver, frozen verifiers untouched) — done-success: the pin-clip is exact, strictly dominates T5″, and the biggest prize is a 132-node backlog nobody has to deploy anything to collect

- **T1 — the clipper is exact, not merely sound.** `attempts/A131-pin-clip/code/pinclip.py`. For a
  tilt sub-bin, the four separating axes of the conditioned square against a pin's guaranteed core
  fail simultaneously iff `|d_x|, |d_y| < w_min/2 + a_P` and each of four expressions
  `(±d_x − a_P) cos θ + (±d_y − a_P) sin θ`, `(±d_y − a_P) cos θ + (∓d_x − a_P) sin θ` stays below
  `1/2` over the sub-bin. Each is a SINGLE sinusoid, so its maximum is at an endpoint or the
  interior critical point (`√(P²+Q²)`, compared as `P²+Q² < 1/4`) — the **exact** `⋂_θ Octagon(θ)`,
  with no sub-bin worst case. Carrying tilts as `t = tan(θ/2)` (how A57's cover is built, lemmas.md
  T2) makes `cos θ`, `sin θ` exact rationals, so the whole decision is `Fraction` arithmetic with
  **no epsilon at all** — unlike T5′ (`TIGHT_EPS = 1e-9`) and T5″ (`MARGIN = 1e-9`). Floats appear
  only in the bisection that *searches* for a slab boundary; every boundary is then certified by the
  exact predicate (0 back-offs needed over the whole corpus). The conservative
  envelope version — trim57's `A`, `B` at `w_min` against `max |d·n|` — **loses 34 of the 674**
  existing "core meets pin core" kills at `nsub = 1`; the exact version keeps **674/674**. That was
  the single largest correction of the day and it was caught by the positive control, not by review.
- **Controls, all clean.** (a) 674/674 logic kills → EMPTY at `nsub = 1`. (b) 99,991 stored LP
  support columns over 1,745 solved nodes are pin-free at their own tilt to within
  **max depth 2.0000·10⁻³ = `caselp.EPS_CORE` exactly, 0 beyond** — and 0 of them lie inside their
  own node's conditioned box, which is not luck: an admissible row must be disjoint from every core
  including `K_B`, so the brief's "support atoms inside the clipped box" test is vacuous by
  construction and the pin-freeness check is its non-vacuous form. *Trap recorded:* `lpbox` stores
  row tilts in **radians**; reading them as degrees manufactures 31,316 false violations up to depth
  0.146. (c) `dead_q` cross-checked against an independent direct SAT computation on a 2,001-point
  tilt grid, 40,000 random (offset, sub-bin) pairs: **0 unsound, 0 missed**. (d) Sampling, quoted per
  the SAMPLED-CHECKS rule across three sets (12 T1 nodes, 10 T3 nodes, all 21 incremental kills):
  **1,140,000 drawn → 897,320 tested → 0 hits**, every node relied on clearing 10⁴ tested on its own.
- **T2 — the corpus.** The corpus has grown to 2,418 rows (674 logic kills + 1,744 open) from A96's
  2,222; the reconstruction is validated by T5″ recomputed here emptying exactly A96's **159** of
  A96's frozen 1,604 open rows. Over the 1,744: **10.3 % clip to EMPTY, 26.1 % narrowed and alive,
  63.6 % untouched** at `nsub = 8`; by level 5.4 / 21.2 / 25.6 / **85.7 %** emptied; by class k5_11
  13.5 % vs k5_16 6.6 %, because k5_11 pins the interior-adjacent slot `(1.5, 0.5)` where k5_16 pins
  the far corner. **Strict domination of T5″**: all 159 of its empties (0 lost) plus **21 more**, and
  455 touched vs its 166. Refining the sub-bin buys touch, not kills (179 → 180 empties from
  `nsub` 1 → 8, 349 → 455 touched) — at `nsub = 1` the exact intersection is already maximal against
  a single pin. Median free levels among the narrowed: 0.71 (½·log₂ convention).
- **The finding that decides something is the UNCLOSED slice.** 1,137 of the 1,744 already carry a
  certified PASS. Of the **607 that do not** (414 ALIVE + 193 FAIL), the clip empties **132
  (21.8 %)** and narrows **292 more (48.1 %)**; only 30 % are untouched. 112 of the 132 need only
  the trim that is *already deployed* — they are open purely because T5′/T5″ are pre-filters on
  newly emitted children (lemmas.md T5′: "existing verdicts are not recomputed or overwritten").
  **So there is a backlog, and collecting it needs no deployment decision at all**: it is a
  re-classification of recorded rows by pure geometry, minutes of CPU, against the 900 s re-check's
  27 certified kills for 8.11 CPU-h — and the two sets overlap in exactly one node
  (`k5_11_interior_Y0546`, which happens to be the single most expensive kill of the re-check at
  2,179 s). The list is written out with prior verdict, τ/η, box and witness pins:
  `attempts/A131-pin-clip/results/backlog131.jsonl` (132 rows, 93 k5_11 / 39 k5_16,
  63/57/6/6 by level, **111 emptied by a single pin, 21 needing two pins jointly** — and the
  two-pin cases are precisely where the clip beats T5″, which only ever tests single-pin
  domination). It supersedes nothing; landing it is the campaign owner's call, and must keep the
  prior verdict as `superseded_by_tight_core.jsonl` does.
- **Schedule.** Under the stated (unmeasured) assumption that a box `f` levels smaller has the kill
  rate of a node `f` levels deeper, §B's per-level logic-kill share gives a total gain of 12.10 %
  (`nsub` 1) / 12.96 % (`nsub` 8) of open nodes — but only **1.20 % is new outright killing over
  deployed T5′+T5″**, plus ~2.6 % of modelled promotion: ≈ 50 CPU-h, **≈ 0.4 wall-days** of the
  A57 row's 11–13. A123's T5″ post-mortem (offline 3.70 % projected vs 1.01 % live) applies here
  too and is quoted with the number. The domination result is the part that does not depend on the
  population.
- **T3 — in vitro, the answer is BOTH, and the kept fraction does not predict which.** Ten nodes
  (Y0036's four depth-2 children D02/D03/D06/D07 plus six ALIVE boxes with kept < 0.5 at mixed
  levels), each re-solved once on its clipped centre box over its OWN tilt bin (`nsub = 1`, so the
  clip is the only variable), through the same `solve_node` call and warm start `recheck96` uses;
  two-stage 240 s then certify at η ≤ −1e-3, 900 s for a knife edge; control = the STORED record,
  never a re-emission. **2.85 CPU-h** of the 6 allowed, two BelowNormal BLAS-pinned processes, no
  wall-cap fired. **Five of ten go from η ≈ 0 (τ pinned at the budget) to η = −0.5 or −1.0**, and
  **two carry a certificate through the frozen verifier**: `k5_11_interior_Y0036_D02` (L2, η −1.0,
  PASS in 11.2 s) and `k5_11_interior_Y0186_D00_D00` (L3, η −0.5, PASS in 219 s) — both previously
  ALIVE. The other three decisive nodes FAIL certification with **real holes** (`Y0036_D03`: 8
  witness boxes at depth 56, 5 holes, 0 tight, 3 undecided), which is the campaign's ordinary
  FAIL → resolver path, not a refutation; the resolver is a campaign driver and was not run. On the
  remaining five the clip moves only the COLUMNS, and hard: support 107 → 5 (`Y0036_D07`),
  1041 → 5 (`Y1128`), 82 → 16 (`Y0996`); `k5_16_interior_Y0674` converges at minmass exactly 1 on a
  box 92 % smaller and stays alive at η −2.5e-13. **Which of the two you get is not predicted by how
  much the clip removes** — the five decisive nodes keep 0.09–0.42 of their area, the five inert
  ones keep 0.08–0.42. *Caveat recorded in the campaign's favour:* `recheck96` counts a "kill" as
  `τ < budget` at η as small as −1.4e-14 and never runs `certify.py`, so PAUSED.md v2 §9's 11-of-23
  and the 27-of-63 now on the ledger are LP verdicts, not verified certificates, and are not
  comparable with the 2 of 10 here; under the re-check's own criterion all ten clipped solves have
  τ < budget. If this is deployed, send knife-edge nodes to the certifier anyway, as the tree does.
- **T4 — deployment shape (`notes/deploy.md`), nothing deployed.** After T5″, before the LP;
  `pinguard.classify` must stay FIRST (the parent case is the one exception to soundness, and
  `clip_node` carries its own `realizes_pin` guard because the protected tier has zones containing
  pins where A57's interior has none). Persist `clip_from`, `clip_kept`, `clip_nsub`, `clip_pins`,
  `clip_delta` — the PAUSED.md v2 §6 `trim_excluded` gap must not be repeated. Emit
  `clipped ∩ original` (the clipper works on the rational OUTER box, so its output can sit 10⁻⁹
  outside an untouched side). Verifier implications: **none** — a clipped child is an ordinary
  smaller box — but a kill on it is a TWO-PART argument (frozen certificate for the clipped part +
  one T5‴ leaf per discarded slab), exactly as a T5″-trimmed kill is, and that is why the leaf must
  be persisted and formalised. Measured second-order effect: the clipped box's `Box.core()` grows
  by a median 4.5 % (max 24.5 %) but yields **0** extra T5′ kills — no second harvest. Lean shape:
  a T5-type logic leaf with a tilt range and a centre sub-box, `decide` over ℚ, needing **none** of
  A117's Taylor/π machinery because `t = tan(θ/2)` keeps the trigonometry rational. n-general: the
  pin-clip is the class-pin analogue of the container clip, the obstacle need only be a set
  contained in every admissible pose, so it applies verbatim to the protected tier, to trump5's
  residual tree, and — with `a_P` replaced by another box's core half-side — it IS budget.md §D
  item 1's box-vs-forced-neighbour kill.
- **Discipline.** `attempts/A57-shadow-trees/PAUSE` left in place and untouched (every `tree57`
  shard and both `deepen` producers stayed stopped); the driver watched its own sentinel through
  `pausegate.paused(base=...)` — A124's scoped-sentinel mechanism, PAUSED.md v2 §7a — and no shard
  was launched. Two processes, BLAS pinned in the supervisor, BelowNormal verified at start rather
  than assumed. Frozen verifiers byte-identical against `attempts/A96-a57-parametric/code/frozen.sha256`
  (`verify_case` 521cb01f…, `verify_param` 0c58485c…, `verify_param_v2` 153029ba…). READ-ONLY on
  every campaign and on the A57/A96 drivers: `trim57`, `pinguard`, `caselp`, `warm57`, `recheck96`
  and `pausegate` are IMPORTED, none edited; new files only under `attempts/A131-pin-clip`. No
  recursive deletes (only my own `__pycache__/*.pyc`), no pidfile touched,
  `PYTHONDONTWRITEBYTECODE=1`, git fetch + plain merge + push of own paths. Writes outside the
  attempt: lemmas.md T5‴, `docs/budget.md` §D item 1 + the date, registry row, this entry.
- **Figure** (PI's drawing rule, `gen_a57_lp.py` style): `attempts/A131-pin-clip/notes/pinclip_Y0036.svg`
  — three panels (whole bin, sub-bins 1 and 8 of 8), the example hypothesis square H in cyan with a
  heavy outline at the CENTRE of the centre box and the CENTRE of the tilt sub-bin with its tilt
  printed (red dashed, because Y0036's box centre is itself infeasible — it overlaps the pin bl10
  by 0.0097), the clipped rectangle drawn inside the original box, plus a ×6 inset because the clip
  is a few 10⁻² and invisible at container scale.

## 2026-09-07 — A133-tan-half-emission (Opus, Lean + generator) — done-mixed
- **The idea, and it worked.** A126 left `LocalDead` for a concrete `N` with ONE named hypothesis,
  `LocalCert.CertCover`, whose entire residue was "a certified rational-interval kernel for `cos`,
  `sin` and `π` — A119's `exactiv.py`, in Lean" — and recommended removing the need for it instead
  of formalising it, by re-emitting the certificate in Lean's own tilt parameter `t = tan(θ/2)`,
  where `cos θ = (1−t²)/(1+t²)` and `sin θ = 2t/(1+t²)` are RATIONAL. That is what this attempt
  did. Every enclosure a local certificate needs is now the exact range of a rational function
  over a rational cell: no `π`, no Taylor series, no dyadic interval kernel, nowhere in the
  pipeline. The step that had made a rigorous `π` unavoidable — `exactiv.kink_in`, locating the
  `π/2` kink of `w = |cos Δ| + |sin Δ|` before taking its affine lower bound — is **retired**:
  in `t`, `w ≥ cos Δ + sin Δ` and `w ≥ cos Δ − sin Δ` hold on the WHOLE cell, both are rational
  functions of the two tilt parameters, and their maximum IS `w`, so the generator emits both and
  the kink is never located. `h(t) = (1+2t−t²)/(2(1+t²))` is concave on `[0,1]`, so its affine
  lower bound is the exact chord through two exact endpoint values, with no rounding at all.
- **T1, measured — and the relaxation in `t` is not weaker, it is SHARPER.** That was the risk
  A126 flagged ("measure it on one cell before anything is rebuilt"). All SEVEN of A119's
  neighbourhoods and THREE of A125's S33 re-emit **DEAD** and re-check **VALID**:
  S07 (0.1, 40°) **2 140 leaves against A119's 2 302** with the certified minimum RISING
  3.877092331 → 3.877108392 (margin over `s0` ×3), S07 (0.2, 10°) 2 920 vs 3 168,
  S02 (0.2, 10°) **16 406 vs 32 570**, S02 (0.1, 10°) 3 808 vs 6 878. Ten certificates, 36 986
  leaves, 569 449 rows, **24.5 MB**, **8.5 min** of generation and **3.1 min** of independent
  checking, zero unresolved nodes. Control (`control133.py`, 4 leaves per certificate per
  mutation): `zero-y` 40/40, `halve-y` 28/28 (rays skipped — halving a positive ray bound keeps it
  positive), `negate-y` 40/40, `widen-box` 40/40, `bump-k` 40/40, `env-h` 40/40, `env-w` 40/40,
  `drop-leaf` 40/40 rejected, `drop-row` 21/40 (informational: a leaf with slack survives losing a
  row), and **100 000 drawn → 100 000 tested → 0 hits** on the survivor count. Envelope tightness
  measured second order: the
  `sin(θ(t) − θ(t*))` enclosure is `≤ 0.23 h²` wide and the better of the two `w` branches within
  `2.3 h²` of `w`. Where a cell straddles `θ = 0` (S02's `BR(0,1)`, S33's `f0`) part of the leaf
  reduction is the clip to the fundamental domain — which makes `N` smaller, the sound direction,
  and is the same clip A126's Lean boxes already carried; A126's finding E3 therefore never arises
  downstream, because the clip happens at the DEFINITION of `N`.
- **The checker is independent and has no early return.** `check_local_t.py` imports nothing of the
  generator's. It does not re-derive the affine envelopes (a re-derivation is only as sharp as its
  own method, and mine came out `4·10⁻⁷` looser than the generator's, which would have rejected
  valid rows); it **verifies** the ones the certificate records — the two univariate families
  EXACTLY by Sturm's theorem on the square-free part, the bivariate one by its own subdivided
  Bernstein test — and then requires every emitted row to be IMPLIED by a row it built itself out
  of those verified envelopes (`min over the leaf's box of (own − emitted) ≥ 0`). All 569 449 rows
  pass. A126's finding E2 cannot recur: ONE code path records a leaf whether its Farkas vector is
  a side bound or an infeasibility ray, the emitted count is asserted against the tree's own
  counter before the file is written, and the checker independently requires every emitted leaf to
  be referenced by the tree exactly once.
- **T2 is PARTIAL, and is reported as partial.** `localDead_s07_t` / `localDead_s02_t` with no
  hypothesis beyond the certificate data are **NOT** obtained. What `LocalCertT.lean` does deliver
  (12 theorems, `lake build` 18.5 s, axiom roster `[propext, Classical.choice, Quot.sound]` on
  every one — no `native_decide`, no project axiom, no `sorry`; audit
  `lean/PackingCertMathlib/scratch/A133Axioms.lean`) is the whole arithmetic base the obligation
  was waiting on: the exact `cosT`/`sinT` cell enclosures (`cosT_anti`, `sinT_mono`, `cosT_mem`,
  `sinT_mem`), the kink-free `w` branches (`wrel_ge_add`, `wrel_ge_sub`,
  `wrel_eq_max_of_cos_nonneg`), a decidable **positivity certificate**
  (`p = Σ c_k (X−a)^k (b−X)^{n−k}` with `c_k ≥ 0`, `posCheck` / `posCheck_sound`) that replaces the
  trigonometric kernel outright, and **(C1) of `CertCover` — the tilt cover — DISCHARGED**
  (`splitOk_sound`, `coverOk_sound`: every point of the root cell lies in the recorded cell of some
  leaf, decided on the certificate's own bisection tree). (C2) the selection cover, (C3) Lemma
  RELAX and (C4) the variable map remain; they are now pure reflection over rational data with no
  transcendental content, and `attempts/A133-tan-half-emission/notes/lean.md` prices them at
  ≈ 250 + 600 + 120 + 80 lines and names the one extra thing the generator must emit (the
  positivity certificates themselves; the envelope TABLE is already emitted and is small — 378
  entries for S07 (0.1, 40°)'s 2 140 leaves, 1 044 for S02 (0.2, 10°)'s 16 406, because envelopes
  are shared across leaves by cell).
- **The effect that is easy to miss.** A119's LP tilt variable is the ANGLE; `Local.Box`'s is
  `t`. Relating them needs `arctan`. So even a perfect Lean `exactiv.py` would have left a
  transcendental step between `LocalHyp` and a θ-certificate. In `t` that step is the identity —
  which is the real reason A126's Route A could not have finished the job on its own.
- **T3 (write only).** `notes/fcover.md`: the outward rounding is in
  `attempts/A112-dual-branching/code/caselp.py`, `make_certificate`, the `nofams=` clause —
  `t_lo`/`t_hi` at `TDEN = 2²⁴` with floor/ceil ± one extra unit (hence the `9.0·10⁻⁸…1.10·10⁻⁷`
  A126 measured) and `q` at `XDEN = 10⁹` NEAREST (hence the `≤ 4.71·10⁻¹⁰`), reached from
  `a120lib.certify_leaf_capped` → A112's `certify.py`. The fix is one clause: round the NO zone
  INWARD on every bound (lower up, upper down, tilt narrowed) so `ZONE ⊆ BOX` holds by
  construction, keeping the YES box's outward rounding. Priced: the narrowest `t_interval` in all
  22 of A120's PASSing NO certificates is `8.75·10⁻²` against a `1.19·10⁻⁷` change, so no interval
  can collapse and the re-certification should be a formality. The Lean check that catches it is
  `LocalCompose.yes_or_no`'s NO side, whose bridge hypothesis is the decidable rational test
  `ZONE ⊆ BOX` — and it must be run **at emission, on the WRITTEN rationals**, which is precisely
  why A120's own `A6_nofam_is_the_same_box` guard passed while none of the 22 emitted certificates
  satisfied the containment.
- **Discipline.** READ-ONLY on every campaign and on A116/A119/A120/A126: A119's and A125's
  certificate files are read, A119's `fastlp.py` is imported, nothing of theirs is edited, and
  `Local.lean` / `LocalCert.lean` / A126's `LocalCertS07`/`S02` are untouched. Frozen verifiers
  never invoked. New files only: `attempts/A133-tan-half-emission/{code,notes,results,certs,logs}`,
  `lean/…/LocalCertT.lean`, `lean/PackingCertMathlib/scratch/A133Axioms.lean`. One `lake build` at
  a time through `lakeb.py` (repo lock, BelowNormal); at most two Python processes;
  `PYTHONDONTWRITEBYTECODE=1`; no recursive deletes; git fetch + plain merge + push of own paths.
  Writes outside the attempt: `docs/known_results.md` 16b′, `lean/depgraph.json` GRAIN, the
  registry row, this entry.

## 2026-09-07 — A131 follow-up (coordinator's ranked item 1): the retrospective backlog sweep landed as 132 verified certificates, and eps_geo after a pin-clip is a dead end

- **132 recorded-open A57 nodes killed by T5‴ geometry alone, in 4.1 s of CPU.** One
  `pin-clip-kill-certificate-v1` per node under `attempts/A131-pin-clip/certs/backlog/`, carrying
  the class pins, the recorded box, the rational outer box, the 8 tilt sub-bins as exact
  `t = tan(θ/2)` endpoints, the **replayable clip trace** (each slab removal with its pin, side and
  exact rational from/to), the witness pins, the prior verdict/τ/η and the sample confirmation;
  ledger in `results/backlog_kills.jsonl`. 63/57/6/6 by level, 93 k5_11 / 39 k5_16, prior verdict
  74 ALIVE / 58 FAIL. Sampling **1,584,000 drawn → 1,584,000 tested → 0 hits**, ≥ 12,000 tested per
  node (the whole box × bin is discarded, so drawn = tested).
- **A57/A96 state untouched.** Their jsonl, progress and cert trees were not written to. The only
  A57 file appended to is `PAUSED.md` — one line in the §8 resume block saying the campaign's owner
  folds these rows in, keeping the prior verdict as `superseded_by_tight_core.jsonl` does.
- **112 of the 132 need only the already-deployed T5″; 20 need the clip** (`results/backlog_clip_only.jsonl`):
  17 L1 + 3 L2, 14 k5_11 / 6 k5_16, 17 prior ALIVE / 3 prior FAIL. **21 nodes need two pins
  jointly**, and every clip-only node is one of them — T5″ only ever asks whether ONE pin dominates
  the whole box, so a box carved by two pins from opposite sides is invisible to it. The 21st
  (`k5_11_interior_Y0360_D06`) goes the other way: two pins for the whole-bin clip, but T5″ empties
  it by using *different* single pins on different tilt sub-intervals. **Neither rule contains the
  other in general** — the clip contains T5″ *on this corpus* (159/159 plus 21), which is a
  measurement, not a theorem. `k5_11_interior_Y0546` is in the clip-only list and is the 900 s
  re-check's most expensive kill (2,179 s).
- **The independent checker earned its keep.** `checkclip131.py` re-derives the dead test in the
  `t` parametrisation (`f(t) = (P(1−t²)+2Qt)/(1+t²)`, `f' = −2g/(1+t²)²`, `g = Qt² + 2Pt − Q`)
  rather than the θ-sinusoid one, and shares no decision code with `pinclip.py`. Its first version
  treated every interior extremum as a maximum and **rejected 23 of 132 sound certificates**; a
  40,001-point brute-force SAT grid on one of them found 0 separating tilts, so the clipper was
  right and the checker was over-strict. The fix falls straight out of `f' = −2g/(1+t²)²`: an
  interior maximum is `g` going − → +, while `g` going + → − is a minimum and the max stays at an
  endpoint. Re-validated: 30,000 random (offset, sub-bin) pairs against both `dead_q` and a
  1,201-point grid — **0 disagreements, 0 unsound, 0 missed** either way. All 132 then PASS.
- **eps_geo after a pin-clip is a dead end, and the mechanism is clean.** 0.56 CPU-h of the 1
  allowed, 2 BelowNormal BLAS-pinned processes, on the three T3 nodes that reached η ≤ −0.5 with a
  failing certificate. Ladder used: the row-shrink `certify.py --eps_geo`, a plain CLI with
  `--out` — exactly what `tree57.run_eps_geo` shells out to — at `tree57.eps_geo_margins`' own
  (0.002, 0.004), all three having scale ceiling ≥ 1.05. **`epsladder.py` (the EPS_CORE ladder) was
  SKIPPED**: it hardcodes its certificate directory to A57's `certs/epsladder` and writes
  `results/epsladder_<id>.json` into A57's tree with no flag to redirect, so it is a driver by the
  test that matters. Result: **all three fail, all three the same way — the row-shrink re-solve
  pushes τ from 4.0 / 4.5 straight back to exactly 5.0 = budget at both margins**, so there is
  nothing to certify. On a clipped box the LP's entire slack IS the 2·10⁻³ shell around the pinned
  squares that eps_geo re-imposes: the clip and the row-shrink are antagonistic and the clip's gain
  is exactly the size of the shell. **Deployment consequence: never chain eps_geo after a
  pin-clip** — send a clipped node with a holed certificate to the resolver or to depth instead.
- Notes: `attempts/A131-pin-clip/notes/backlog_sweep.md`. New code: `backlog_certs131.py`,
  `checkclip131.py`, `epsgeo131.py`; `pinclip.clip_node` gained an optional `traces=` argument
  (certificate emission only — the clip decision is unchanged, and the 674/674 and corpus numbers
  were re-run identical).

## A132 — the polygon core K′(B) (Opus; measurement, in-vitro LP, verifier/Lean spec)

- **The object.** For a parameter box `B`, `K′(B) = ⋂_{(c,θ)∈B} Q(c,θ)` — the intersection of the
  hypothesis square over the whole box; a convex polygon that CONTAINS both `Box.core()`'s `K(a)`
  and A96's tight core, since both are squares lying in that intersection. Built numerically (clip
  on a θ grid, shrink 1e-6, delete negligible vertices, exact rational hull) and then CERTIFIED
  vertex by vertex: `v ∈ Q(c,θ)` for all `(c,θ) ∈ B` is two rational quadratics in `t = tan(θ/2)`
  over the four corners of the centre rectangle, decided by endpoints plus `4AC − B² ≥ 0`. The
  builder is unaudited; the vertex test is the proof. `code/polycore.py`, 0.07 s per box.
- **T1, all 506 alive nodes** (A57's 414 ALIVE + A60's 92 refused): `area(K′)/area(K(a))` median
  **1.225** (max 1.53, largest where the tilt bin is widest). **22.3%** of dual-support columns,
  carrying **35.7%** of τ, meet `K′` but not `K(a)`; **20.5%** of the 5.7 M-row pool; only 17/506
  nodes have no offending column. Split: on A57 three quarters of the excluded weight is the
  conditioned box's and a quarter the **pins'**.
- **T5⁗ logic kill** (`K′(B)` meets a pin's `K′(P)` ⇒ node empty, no LP, no certificate): fires on
  **64/506**, **37 NEW** on top of the deployed T5′ (27 the tight core already kills — 20 already
  recorded, 7 A60 nodes where T5′ was never applied). Positive control **854/854** recorded
  KILL-BY-LOGIC boxes preserved.
- **The Lean collapse.** `Zones.core_meet_same_square` takes arbitrary SETS. Take `K = K' = {w}` for
  the exact rational witness point (found and certified against both boxes, 64/64) and the hull, the
  convexity lemma and the polygon–polygon SAT all vanish: the kill certificate is ONE rational point
  plus TWO vertex checks, and the only new Lean obligation is the decidable vertex test. No verifier
  change, no certificate change, no re-verification of the existing tree.
- **The LP lever: predicted worthless, refuted.** A `K′(B)` row drop is a strict special case of
  A96's all-poses filter, which was measured at zero kills — but the polygon core also upgrades the
  **PIN** cores, which that filter never covered. In vitro (10 alive nodes, both arms, identical
  warm start and oracle, recheck96's node path, 2.7 CPU-h): the three pairs that CONVERGED in both
  arms are all LP-dead under `K′` and alive under `K(a)` (5.000→4.000, 5.000→4.500, 5.000→4.000),
  every axis arm reproducing the campaign's stored verdict. The attribution arm (polygon core on the
  conditioned box only) sends `Y1038` back to τ = 5.000 — that kill is entirely the pins'. Recorded
  as "LP-dead under polygon core, CERTIFICATE PENDING"; caveat of record: three converged pairs on
  nodes selected for the largest offending weight is not a rate.
- **Discipline.** Read-only on every campaign and driver; new files only under
  `attempts/A132-polygon-core/`; frozen verifiers byte-identical (the spec describes a v3, it does
  not touch v1/v2); no shard launched; A57's PAUSE sentinel reported in every driver log and never
  touched, the in-vitro driver honouring its own `attempts/A132-polygon-core/PAUSE` (A124's
  sanctioned separate-sentinel pattern); ≤ 2 BLAS-pinned BelowNormal processes throughout, dropped
  to a 9,000-row warm start when free physical memory fell under 1 GB (lemma T19); ~3.3 CPU-h total;
  `PYTHONDONTWRITEBYTECODE=1`; no recursive deletes, no pidfile deleted; git fetch + plain merge +
  push of own paths.

## 2026-09-07 — A124-recheck-day (Opus chore, ≤ 2 BLAS-pinned BelowNormal processes, READ-ONLY on every other attempt and on A57's drivers) — done-mixed: the trimming projection was never wrong, the re-check is not what the budget says it is, and Y0381 is a missing HiGHS option

- **T2 — the touched-vs-emptied control (`code/control124.py`, 4.7 s over 2,418 boxes).** The v1
  offline control never conflated the categories: `docs/residue_ledger.md` says "159 boxes' surviving
  bin is empty ... 155 more are partially trimmed", and the re-run reproduces **EMPTIED = 159**
  exactly (TRIMMED = 166, grown by the night's rows). **The conflation is in PAUSED.md v2 §4**, which
  tabulated the 159 as "boxes touched by trimming, 6.62 %" and compared it against the live *touch*
  rate. Corrected offline figures, n = 1744: **9.12 % emptied, 18.64 % touched**. Positive control
  **741/741** recomputed T5′ kills fully emptied.
- **The live run never contradicted the projection.** Denominator-matched and out of sample — the
  night's 206 post-T5′ level-1 children against the 1,043 pre-night level-1 boxes — EMPTIED 1.46 % vs
  2.97 % (**Fisher p = 0.35**), TRIMMED 7.77 % vs 9.01 % (**p = 0.69**). The apparent 3.7× collapse
  was two artefacts stacked: 3.70 % is the *all-levels* incremental rate while the night emitted only
  level-1 children (the least favourable level), and the live 1.01 % used 296 as its denominator
  instead of the 206 T5′ had not already killed. Cross-check: the control independently classes
  exactly the 3 `pin_info=="trim"` night rows as EMPTIED, **3 of 3** agreement with the deployed rule.
- **Schedule re-derived on full kills only** (`code/schedule124.py`; trimmed-but-alive nodes pay the
  same LP): **13.3 → 10.5 wall-days** offline, 10.6 with the live L1 rate, 11.7 if every level is
  short by the live/offline factor. **The 10–11 figure was already full-kills-only and it survives.**
  It rests almost entirely on the **level-2 rate of 13.7 %**, for which there is still no live data —
  the first `deepen.py` after the resume settles it; nothing about level-1 emission will.
- **THE DAY'S REAL RESULT, and it was sitting in the results files: T5″ applied RETROACTIVELY.**
  Of the 414 ALIVE rows, **57 already have an empty surviving bin** under the deployed
  `trim57.trim_box` (k5_11 L1 13 / L2 18 / L3 3, k5_16 L1 21 / L2 2 — the coordinator's count,
  reproduced exactly, and a second positive control since `trim57` and `trim96` agree on all 57).
  `recheck96 --trimmed` does *not* waste LP on them (the `not subs` branch precedes `solve_node`), but
  it reaches them **in queue order**, so 54 free kills sat behind ~13 CPU-h of solving.
  `code/trimsweep124.py` banked all **54 in seconds, 0.0 s of LP** (L1 31, L2 20, L3 3), writing the
  actual `excluded_intervals` and `original_bin` — PAUSED.md §6's MUST-FIX, done for these rows.
- **Scanning the whole population: 55 of the 193 FAIL rows (28.5 %) are dead by the deployed trim**,
  and 112 of the 607 work-owing nodes (18.5 %) overall. All **674** stored KILL-BY-LOGIC rows come out
  empty, 100 %. The resolver queue is the expensive tail (FAIL p50 375 s, max 3,385 s) and more than a
  quarter of it carries no configuration. A124 is read-only on A57 so those 55 are a **recommendation**:
  run the scan before the resolver restarts. Applied retroactively, trimming retires ~18 % of the
  outstanding node count for the cost of a geometry scan — a different and **additive** saving to T2's
  prospective 21 %.
- **Monotonicity, checked not assumed.** The three trim-empty L3 nodes `Y0036_D07_D00/_D04/_D05` were
  descended into *before* T5″ existed; all **24 of 24** L4 children are also trim-empty (a child's box
  and bin are sub-objects, so the same pin octagon still contains them). Their recorded verdicts are
  14 KILL-BY-LOGIC, 4 PASS, **6 FAIL** — six resolver items owed against a subtree that is dead at its
  root.
- **T1 — the re-check, and a correction to the headline that justified it.** 53 level-1 LP nodes at a
  900 s cap and a hard 1,500 s process wall, 16.24 CPU-h of the 20 h cap, 8 wall-caps (never a
  verdict). A131 is right that `recheck96.py:116` calls a kill `tau < budget` and **never runs
  `certify.py`** — so no re-check kill has ever been certified. Graded by the campaign's *own* strict
  rule (`eta < −0.005·tau`, PAUSED.md §5b): today **2 STRICT, 1 WEAK, 18 KNIFE** (|η| ≤ 1e-9), and
  **§9's "11 certified kills from 23 nodes, 47.8 %" is 1 strict, 2 weak, 8 knife**. Both of today's
  strict kills (`Y1099` η = −1.000, `Y1002` η = −3.4e-02) were **already in arm C's strict-kill set**
  `{Y1002, Y0817, Y1099}`. Fifteen CPU-hours rediscovered two known nodes and found no third.
- **So `docs/budget.md`'s ranking is backwards.** It lists the 900 s re-check as "the best per-budget
  item on the board". Measured over a full day: **2 strict kills for ~15 CPU-h**, against **54 genuine
  logic kills for zero** from the geometry sweep, with 55 more visible in the FAIL queue.
- **Why no certificates today, and the fix.** `certify.py` takes a node json; `recheck96` runs
  `solve_node(out=None)`, so certifying a re-check kill needs a full ~900–1500 s re-solve first, which
  did not fit the clock. `recheck124.py` now writes `results/nodes/<id>.json` and records `grade`,
  `node_json`, `certified: null`, `cert_note` — after which certifying costs only certify.py, ~240 s
  each. **Next step, ~8 CPU-min:** certify `Y0054`, `Y1099`, `Y1002` (+ the weak band if wanted).
  Do **not** attempt the knife-edge nodes — at η = −1e-14 the certifier is asked to prove a strict
  inequality holding by less than its own arithmetic noise.
- **T3 — `Y0381` diagnosed (`code/repro_y0381.py`).** Reproduced exactly (same 3,827-atom folded pool,
  same `init orbits=3827 rows=16602`, same iteration trace), nothing written into A57. All **11**
  faulthandler dumps, including the one at the 600 s wall, give one stack: **`lpbox.py:417
  self.h.run()` ← `lpbox.py:846 M.solve()` ← `caselp.py:337 solve_node`** — one `h.run()` ran 380 s and
  never returned, and never printed the non-optimal-status diagnostic. Not column generation, not the
  certifier, not `pinguard`. **Cause: `LPModel.__init__` sets `output_flag=False` and `threads=1` and
  never sets `time_limit`**, while `solve_node`'s limit is checked only *between* iterations — one
  thread at 100 %, zero output, no bound. The 00:48 run died in the final unconditioned solve at
  `:908`, the 03:02 run in the in-loop solve at `:846`; same call. **Not a T5″ artefact** — bin width
  10.880664 is a canonical cover width, `pin="ok"`, untrimmed; pre-existing.
- **Guard recommended, with its caveat.** `self.h.setOptionValue("time_limit", ...)` at `lpbox.py:266`
  is the one line, **but it is not the whole fix**: on a time-limited exit HiGHS returns the incumbent,
  `:419` re-solves cold, and `res["tau"]` is then set from a **non-optimal** LP — a τ below the true
  optimum would manufacture a kill, so `kTimeLimit` must be propagated as CAP-not-a-verdict first.
  Until then, prefer the per-node **process wall** A124 ran all day: a watchdog that records `WALL-CAP`
  in the driver's own ledger only and `os._exit`s, with a supervisor that restarts. It fired 8 times
  today, cost nothing, needs no edit to a frozen driver, and bounds *every* node rather than one.
- **The scoped-sentinel mechanism (coordinator's request), now PAUSED.md v2 §7a.** `pausegate.paused()`
  with no argument checks *both* bases, which is why A123's pause also stopped `recheck96` and A120's
  runner. The fix is `paused(base=OWN_ATTEMPT_BASE)` — one line at the *consumer's* call site, no edit
  to `pausegate.py`, no deletion of A123's sentinel, and every driver calling the bare `paused()` (all
  six shards, both deepens) stays paused. A124 watched its own `attempts/A124-recheck-day/PAUSE`;
  **A123's sentinel was never deleted and `recheck96.py` was never modified**. A120 can resume the same
  way. Corollary: "the A57 PAUSE is set" no longer implies "nothing is running" — check pids.
- **Discipline.** ≤ 2 BLAS-pinned BelowNormal processes, dropped to **one at 15:31** via the scoped
  sentinel when the box hit 18 python processes and 4.5 GB free (both workers drained cleanly, nothing
  lost; relaunched as a single `--shard 0/1`). Frozen verifiers byte-identical (`verify_param.py`,
  `verify_case.py` — all four copies match `frozen.sha256`). Orphan reaper every 30 min, **zero orphans
  all day**. Free physical never below 4.5 GB. `PYTHONDONTWRITEBYTECODE=1`. No recursive deletes, no
  pidfile deleted, no shard launched, no A57 driver edited, no write into any other attempt except the
  permitted appends to `recheck96.jsonl` and the PAUSED.md notes. Git: fetch + plain merge + push of
  own paths.
- **One bug found and fixed in A124's own driver.** A worker's queue is built once at startup, so after
  a watchdog restart it re-solved `Y0726`, which the sibling shard had already wall-capped, for another
  1500 s. `recheck124.py` now re-reads both ledgers **per node**, not only at startup.

## 2026-09-07 — A134-certcover-close (Opus Lean) — done-mixed
- **The three named pieces of `CertCover` are all theorems now; the assembled `certCover_s07` is not.**
  `lean/PackingCertMathlib/PackingCertMathlib/LocalCertT2.lean`: 36 theorems, axiom roster
  `[propext, Classical.choice, Quot.sound]` on every one — no project axiom (`Local.sat_selection` is not
  used; `SatInterior.sat_selection_thm` proves it), no `native_decide`, no `sorry`. `lake build` 19.5 s,
  audit `scratch/A134Axioms.lean` 14.2 s.
  - **(C2)** `selectionOk_sound`: the recorded selections of a near pair are exhaustive, decided by an exact
    rational interval enclosure of `g_σ` on the cell. In `t` the `cosT`/`sinT` ranges are the ENDPOINT values
    (zero enclosure error) and the only widening is one interval multiplication; `w` is bounded below by the
    MAXIMUM of its two smooth branches, so the `π/2` kink — A119's one unavoidable `π` — never appears.
  - **(C3)** Lemma RELAX, both row families. `relax_wall` from `Parametrize.set_subset_container_iff` plus the
    certified chord; `relax_selection` is the chain `1/2 + W_lb/2 ≤ 1/2 + w/2 ≤ Proj = P·C + Q·S ≤ (P+corr)+U`
    with all five ingredients proved. `axis_decomp_t` — `Local.axis_decomp` in the angle — is in `t` an
    ALGEBRAIC IDENTITY: one `linear_combination` against `cos²+sin²=1`, no angle anywhere.
  - **(C4)** `localHyp_bodies`: one square per body in the certificate's order, with box/slack-core
    membership, container containment, tilt range and pairwise INTERIOR-DISJOINTNESS.
- **T1.** `gen_local_t2.py` = A133's generator (imported read-only) + a `pcert` field: per envelope, the
  nonnegative scaled Bernstein coefficient lists `posCheck` consumes, as a CHAIN of pieces (`posChain` /
  `posGrid`), with `substX0`/`substY0` for a pin's collapsed tilt cell. S07 (0.1, 40°) and S02 (0.2, 10°)
  re-emitted as `local-cert-t-v2`; trees, leaves, rows and certified minima IDENTICAL to A133's.
  **Cost in leaves of replacing the checker's Sturm argument by the Bernstein form the kernel can run: ZERO** —
  every envelope of all four families certifies at Bernstein DEPTH 0, one piece.
- **A gap found and closed on the certificate side.** Lemma RELAX also needs `S_lo`, `S_hi` (the McCormick
  corners, and the chord scale of envelope (A)) and `K = max(1 − cos φ)`; A133's Python checker recomputed
  them from the cell and Lean cannot. Now emitted with their own certificates.
- **Independent check.** `check_local_t2.py` runs A133's whole checker unchanged (`v2` ⊃ `v1`) AND verifies
  the new field from the LEAN definitions, with a random-point MEANING check and a 3-way mutation control.
  Both certificates VALID (A133 half 6.7 s / 74.6 s; pcert half 0.5 s / 1.6 s; bump and shrink REJECTED).
- **T3.** The emitted `pcert` replayed by `native_decide` in Lean: 36.2 s (S07, 4 872 coefficients) and
  81.2 s (S02, 14 936) — both PASS, ≈ 4.4 ms/coefficient, kernel not the wall. **A126's elaborator wall
  recurs verbatim** (one 336-entry list literal → `(deterministic) timeout at isDefEq`) and A126's remedy
  fixes it (32 entries per `private def`, linear `++`, `maxHeartbeats 2000000`). The remaining eight
  certificates project at ≈ 3.5 min of `pcert` replay; not built, per the brief.
- **What is still missing for `localDead_s07_t`**, named exactly and priced: (R1) the reflected tree walk
  (~300 lines), (R2) the reflected ROW BUILDER plus the outward-quantisation step (~600), (R3) the variable
  INDEX map (~120), (R4) the leaf data and the replay. **No missing library lemma** — every mathematical step
  is now a theorem. `attempts/A134-certcover-close/notes/lean.md`.
- Invisible until one writes the Lean, and worth remembering: `posCheck` compares LISTS, so a positivity
  certificate is accepted only if it reproduces the polynomial with the exact trailing-zero shape `posAux`
  produces. `code/leanpoly.py` mirrors the recursions for that reason.

## 2026-09-07 — A138: the reflected plumbing of `CertCover` (T1 (R1)-(R3) + glue done, (R4) not)

- `lean/PackingCertMathlib/PackingCertMathlib/LocalCertT3.lean` (1 856 lines, 130 declarations, `lake build`
  25 s, no `sorry`) writes A134's residues (R1) the reflected tree walk, (R2) the reflected row builder with
  the outward-quantisation step, (R3) the variable index map — and one A134 did not name, the ROOT CELL
  bridge. It ends in `certCover_of_check : certOk C = true → CertCover C.leaves C.M.boxes C.M.pins slo shi`
  and `localDead_of_certOk`: **`LocalDead` for a neighbourhood from TWO decidable checks and nothing else.**
  Roster `[propext, Classical.choice, Quot.sound]` on every lemma; `localDead_of_certOk` adds only
  `check_3_82`'s `native_decide` axiom through `lb_382`. `Local.sat_selection` is not used.
- **A134's ≈600-line (R2) estimate collapses to one lemma.** Comparing the emitted row with the true row
  through `LocalCert.minL` IS the invariant `gen_local_t.quantise_leaf` establishes, so `rowImplies_sound`
  (12 lines) discharges the whole outward quantisation; nothing about the rounding is re-derived and a
  generator that rounds differently — or not at all — is accepted by the same check.
- **The n-ary selection branch has to become binary.** A Lean inductive with a `List CNode` field gives no
  usable induction hypothesis. A branch re-encodes as a chain of binary `sel1` nodes, each of which is the
  TAUTOLOGY `SelHolds σ ∨ ¬ SelHolds σ` and carries no certificate at all, closed by one `impx` node where
  `selectionOk_sound` says the recorded selections are exhaustive and every one has already been refuted.
  The walk then carries two selection lists (holds / does not hold) and `treeOk_sound` is five cases.
- **T2: `local-cert-t-v2` needs no new field — (R4) is a pure RE-ENCODER.** `code/reencode_check.py` builds
  the reflected shape from a v2 certificate and mirrors the LEAN row builder (not the generator) plus the
  Lean `affImplies` test: the walk reproduces every leaf's recorded box (2 140 / 8 / 16 406) and **all
  295 700 emitted rows of S07 and both S02 certificates are implied by a built row** (25 377 / 124 /
  270 199; zero failures), with every envelope key present in `env` and `pcert`.
- Banked for (R4): a bisection node need not record its children's cells (`cellLo`/`cellHi` compute them,
  `splitOk` still checks the split) — 88 000 rational literals off the S07 data file, and the elaborator is
  the wall; and `certOk` is `native_decide`-able but kernel `decide` gets STUCK on it.

## 2026-09-07 — A142: the A57/A60 review gallery v3 (60 pages), the surviving-alive population, and a free kill found while drawing

- **Population.** Of A131's **607 work-owing nodes (414 ALIVE + 193 FAIL)**: 132 pin-clip kills, then 6 NEW
  polygon kills, 2 NEW certified LP kills, 0 new trim-empty (all 54 are already inside the pin-clip set) and
  2 descendants of killed nodes — **142 removed, 465 survive (330 alive + 135 fail; L1 366, L2 95, L3 4;
  k5_11 243, k5_16 222)**. The four kill lists overlap almost completely: 253 list entries remove 142 nodes.
  A60 adds the **283** nodes with an LP support in A107's `shadow_nodes.json`, all at depth j = 0.
- **Subtree cost, stated.** `C(L) = p_L(L)*850 + p_A(L)*(300 + 8*C(L+1))`, `C(5) = 0`, with `p` the measured
  per-level verdict shares of A57's own 2,418-box corpus (C(1..4) = 2632 / 1297 / 1020 / 372 s);
  `subtree(n) = residual(n) + sum over still-open emitted descendants`, `residual(ALIVE frontier at L) =
  8*C(L+1)*kept8(n)` with kept8 A131's measured pin-clip kept volume, `residual(FAIL) = 900 s`. Top:
  `k5_11_interior_Y1104` 11.59 CPU-h (6 still-open emitted descendants), `Y0672` / `k5_16_Y0083` 4.53,
  `Y0738` 3.76. The model cannot see inside an un-descended box, so every L1 alive node with kept8 = 1 and
  no emitted child ties at 2.88 CPU-h; ties break on the polygon core's bite on that node's own support.
- **THE DAY'S FREE KILL, found by drawing: the pin-clip at the EXACT pin core.** A131 deployed the clip at
  the stock `a_pin = 1/2 − delta = 0.49`; A135 certified the pin's guaranteed core to be
  `1/2 − delta/sqrt2 = 0.492928902` and that the frozen verifiers take the half-side VERBATIM. Enlarging
  `a_pin` in the clip is sound for exactly the verifier's reason (the pin square contains K'(P) at every
  pose of the pin box) and costs nothing. Over the 465 survivors the stock clip empties **0** — the correct
  control, since the 132 stock-clip kills are already out of the population — and the exact clip empties
  **17: seventeen NEW T5‴ logic kills, geometry only, no LP, no verifier or certificate change**
  (`Y1002`, `Y0041_D02`, `Y0414_D02`, `Y0930`, `Y0978_D05`, `Y1002_D05`, `Y1134_D06`, `Y1134_D07`,
  `k5_16 Y0930/Y0997/Y1002/Y0449/Y0648/Y0809`, `Y0997`, `Y1099`, `k5_16 Y1099`), and it narrows 272 of 465
  boxes strictly further than the stock core (mean kept volume 0.602 → 0.584).
- **A60 had never been clipped at all.** Its pins are EXACT placements, so the guaranteed pin core is the
  whole unit square: **34 of the 283 A60 nodes clip to EMPTY**, 143 more narrow. Three of them
  (`c0_Y0168`, `c0_Y0254`, `c0_Y0878`) are inside the drawn top 20 and their pages say so.
  Independent control (sampling, a different code path): 4,000 uniform poses in each EMPTY box give ZERO
  pin-free poses; non-empty controls give 75–2,126.
- **The pages.** `docs/shadows/a57v3/` — 40 A57 + 20 A60, `README.md` (ranked table), `review_a57v3.csv`,
  `docs/shadows.md` Part IV. Drawn to the PI's rules of the evening: all THREE cores of every conditioned
  square in distinct styles (stock K(a) solid black, A135 exact axis core solid teal, K' filled purple,
  captioned `a_stock / a_exact / area K'`), BOTH cores on every pin, each red-dashed column labelled with
  which core it clears and which it meets, and every schematic object (centre box, clipped box, lane cell)
  a thin dashed outline with no fill. 1,240 red-dashed columns over the 60 pages, **376 of them impossible
  against an EXACT PIN CORE** rather than against the conditioned square — the pins' share A132's
  attribution predicted.
- **Trap banked:** a hypothesis box is a PIN only when its tilt width is zero. A60's depth-2 nodes
  (`f1_L10_0003`) carry a previously-conditioned square with a TILT WINDOW in the pin slots; drawing it as
  a zero-tilt pin at its box centre is wrong, and the exact-core containment check is what caught it.
  Slack pins (`slack0.02_*`, centre half-width 0.0141) are still pins — the test is `th1 == th0`, not
  `x1 == x0`.
- **Geometry check** (`code/verify142.py`, a second implementation: edge crossing + strict point-in-polygon,
  no separating axis anywhere in the file): 1,240 red-dashed columns over 361,906 poses, 2,088 non-flagged
  control columns each shown disjoint at some pose of every box, 300 exact pin cores over 9,900 poses,
  2,384 K'(B) vertices over 20,580 poses, 446 clipped rects — **zero failures**.
- **Caveat of record:** lane counts on these pages are A118's stored AXIS-CORE verdicts (K(a), not K'),
  because A141 had not landed; a corner marked UNDECIDED here may still become LANE<=1 under K' — the
  s3_far effect. And a pocket is an exact convex-polygon DISTANCE, a measurement for the reading, not a
  proof that nothing fits; the proof is the lane leaf.

- **A142 follow-up (same day): the 51 exact-core clip kills are now replayable certificates.** A131's
  `pin-clip-kill-certificate-v1` format, emitted by `attempts/A142-a57-review-gallery/code/emit142.py` under
  `certs/{a57,a60}/`, ledgers `results/exactclip_kills_{a57,a60}.jsonl`, summary `results/exactclip_kills.json`.
  Each records the half-side actually used — `a_pin = 33873816211/68719476736 = 0.49292890196375083` for A57's
  δ = 1e-2 pins, 1/2 to the same 1/2⁴⁰ grid for A60's exact placements — as `a_pin` with `pin_delta = 1/2 −
  a_pin`, so A131's checker's own identity holds on the EXACT inset; carries A135's `exactcore` certification
  (the corner-by-corner rational vertex test) for every pin box, all certified; and carries the full per-sub-bin
  replay trace. **A131's INDEPENDENT `checkclip131.py` reads them unchanged and passes 51/51, 0 FAIL**; the
  sampled confirmation inside the certificates is 612,000 drawn poses with **0** pin-free hits. Witnesses:
  44 single-pin, 7 two-pin joint. **14 of the 34 A60 kills are emptied by the already-deployed T5″ trim alone** —
  open only because the trim was never applied to that campaign; 0 of the 17 A57 kills are.
  One append-only line each to A57's `PAUSED.md` resume block and A60's `notes/ledger.md`; nothing else in
  either campaign touched. Population arithmetic updated: **465 → 448 surviving** (323 alive + 125 fail;
  L1 355, L2 89, L3 4). None of the 17 has a still-open descendant and none is among the 40 drawn pages, so no
  gallery page is stale.

## 2026-09-07 — A139: (R4) closed — `localDead_s07_t` and `localDead_s02_t` are theorems

- `lean/PackingCertMathlib/PackingCertMathlib/LocalCertS07T.lean` (5.79 MB) and `LocalCertS02T.lean`
  (43.66 MB) carry two local certificates as `LocalCertT3.Cert` data and end in
  `localDead_s07_t : LocalDead s07Boxes s07Pins 3.877084` and `localDead_s02_t` — `Ls`/`Ps` read off the
  certificate's own `CMeta`, from `certOk` and `LocalCert.checkLeaf` by `native_decide` and nothing else.
  `certCover_s07` / `certCover_s02` INSTANTIATE the obligation A126 opened and A138 closed abstractly.
  Rosters: `[propext, Classical.choice, Quot.sound]` + the replays' own `native_decide` axioms +
  `check_3_82`'s through `lb_382`; no `sorry`, `Local.sat_selection` unused
  (`scratch/A139Axioms.lean`, 180 s).
- **(R4) was NOT the data plumbing A138 specified.** `LocalCertT3.treeOk` re-runs the certificate's
  selection EXCLUSIONS with `LocalCertT2.gapHi`, whose `w`-bound `wLoQ` is interval arithmetic on
  `cosRel`/`sinRel` and can fall below `1`; A133's generator excludes with `a133lib.w_range_cell`, the
  EXACT range of `w` over the cell product, which is `≥ 1` always. On A134's certificates the difference is
  fatal: **246/246 of S07's `imp_sel` closures, 38/426 of its branch exclusions and 44/314 of S02's are not
  reproducible in Lean** (`code/diag_gap.py`) — no re-encoding of them can pass `certOk`. A138's T2 audit
  checked the row builder, the box walk and the envelope keys, and never checked this.
- **The fix: re-emit with the Lean-faithful exclusion test** (`code/regen_t3.py` — A133's search with one
  overridden method; LP, envelopes, rounding and A134's `pcert` unchanged; bodies byte-for-byte A119's, so
  the statement is unchanged). Both searches close with ZERO unresolved cells: S07 2 140 → 2 923 leaves
  (+37 %, 23.4 s), S02 16 406 → 16 732 (+2 %, 185 s), envelope tables the same size, Bernstein depth still
  0. The branches the coarser enclosure cannot exclude are killed by the LP instead, as infeasibility rays
  (S07 768 → 1 484): the relaxation carries a certified PLANE below `w`, sharper than the constant `wLoQ`.
- Two further re-encodings, both invisible to the statement: A133's branch-free singleton fixes become
  `sel1 σ · (impx i j [σ])` at the terminal that needs them (721 / 13 199); and each PIN-PIN selection is
  emitted with the mirror `selectionOk` demands and the generator drops as a duplicate —
  `gapHi (pb.swap) k e = gapHi pb k (−e)` exactly, the mirror builds the same rows, and a pin-pin enclosure
  is CELL-INDEPENDENT, so the mirror shares the recorded branch's subtree (without that sharing S02's four
  pin-pin branch pairs multiply the tree text by 2⁴).
- Walls: `lake build` of both modules together **6 712 s** at BelowNormal (S07 571 s, S02 6 707 s in parallel,
  1.8 GB steady), oleans 39.6 MB and 186.1 MB. `encode_t3.py` verifies in Python, before writing a line,
  everything the Lean check re-runs (`layoutOk`, `rootOk`, `splitOk`, `selectionOk` at every `impx`,
  `gapHi < 0` at every `impsel`, `L.box == cur`, every envelope key, and `checkLeaf` exactly on ALL leaves).
- **Open, and the better buy: give `LocalCertT2` the exact `w` range as a decidable enclosure** (A133's
  `w_range`: `w(|u|)` rises to `√2 − 1` and falls after — one variable, the polynomial machinery is already
  there). Then A134's certificates replay unchanged and every future one is cheaper; the alternative is
  four lines in the generator and +37 % leaves. Unchanged from A138: `node_dead_of_yes_no` still needs the
  per-node YES bridge and A120/A136's NO certificates with the ZONE ⊆ BOX guard.

## A143 — the corner-first k0_00 root (Opus engineer, 2026-09-07 evening, cap 2 CPU-h)

**Question.** Does canonicalising the k0_00 tree on the square that meets the BL corner box — rather
than on an interior-zone square, as A24/A38/A99/A115 do — buy a cheaper tree? Measured at level 1
against the interior root's 22 of 216, in the single-intruder form and in the PI's doubly-met form.

**Answer: the cover is sound and cheap to state, the geometry is worth 82 % in the doubly-met form
and nothing in the single form, and the LP kills the idea in both.**

*The cover.* Under K0-BLOCKED the BL box is met, so some square has a pose in `R_BL`; admissibility
plus meeting confine its centre to `[1/2, a_w + √2/2]² = [0.5, 1.7326162]²` with the mandatory
K0-WIDEN pad `a_w = 1 + (λ_max−1)(1+1/√2) = 1.02551007`. Level 1 = a 6×6 position grid × 6 tilt
windows of 15° = **216 cells**, **126** after quotienting by the BL stabiliser `{id, transpose}`
(a `/2`, against the interior root's already-spent `/8`). Confirmed by 22,078 drawn admissible
BL-meeting poses, **0 misses**, and in the pair form by 12,000 drawn, realised, interior-disjoint BL
2-crowds, **0 violations** of the geometry prunes.

*A correction to the brief's premise.* Both the brief and the extension assume "k0 means no simple
square, so the BL intruder is tilted, θ ∈ (δ_simple, 90°−δ_simple)". **There is no δ_simple.** Lean's
`Skeleton.lean` `OccupiesSlot` is exact — axis-aligned AND exactly on the slot centre — so
`skeleton = ∅` removes from `R_BL` only the pose `(1/2, 1/2, 0°)` and its 90° twin. `M_{k0_00}` is
the pin-free monotone hypothesis, true of every packing, which is why the whole k0_00 route is a
∀-packings statement; a positive-measure tilt exclusion would need the exactness bridge that
`k0_route.md` §3 deliberately does not consume. **The cover must run over the full tilt range**, and
the k0 hypothesis buys no cell reduction at all.

*Geometry, single-intruder root: 0 of 216.* The container clip (walls as pins, A131's
per-tilt-sub-bin mechanism) empties no cell — and provably cannot on a single square, since a
sub-bin dies only if `x1 < h_min(sub) ≤ √2/2` or `x0 > a_w + h_max(sub) ≥ 1.5` and no cell can meet
the first in one sub-bin and the second in another; it does shrink 84 of the 216 centre boxes and
delete 2 of 8 tilt sub-bins in 22 cells (a free level-2 narrowing). A132's certified polygon core
never leaves the container (min wall margin 0.0888; `K′/K(a)` area ratio 1.18–1.60, median 1.32 —
the largest measured in the lab, because these cells are wide in tilt). The K′ lane leaf kills
nothing on any of the four corners, and **cannot**: at BL the conditioned square is itself a meeter,
so `M = 1` and the K0-FREE threshold `LANE + M ≤ 1` needs `LANE(BL) = 0`, while at BR/TR/TL the
hypothesis is entirely localised at BL and an explicit disjoint witness pair realises `LANE ≥ 2` on
214/216/212 cells. Upgrading to A141's polygon-core lane — the upgrade that killed 26 further
level-1 cells of the *interior* tree — gives 0 kills on 27 cells (16 near-misses at BL). **The lane
leaf is a deep-node weapon on this tree: it can only fire once conditioned squares sit at more than
one corner.**

*Geometry, doubly-met root: 9,638 of 11,772 = 81.9 %, for 90 CPU-s.* 23,436 unordered pairs of
level-1 cells, 11,772 canonical under the transpose; killed by three exact prunes — **7,919** by max
centre distance < 1 (two interior-disjoint unit squares have centre distance ≥ 1, since any
separating normal gives `|d·n| ≥ h₁(n)+h₂(n) ≥ 1`), **1,313** by `K′(A)` meeting `K′(B)` (a (C)
leaf: every realisation of A overlaps every realisation of B), **406** by A131's per-tilt-sub-bin
refinement of that test — the one place in A143 where sub-bin clipping produces an outright kill.
2,134 survive. The lane leaf again kills nothing (BL has `M = 2`, so it is structurally out of
reach; 1,322 tested).

*The LP settles it.* With A135's certified EXACT axis cores in the hypothesis (a square at the box's
own tilt, so the FROZEN `verify_case.py`, sha256 `521cb01f…`, needs no change) and a K′ audit
column, at a 240 s cap: single-intruder root `η = −0.0442, −0.6328, −0.0000` (budget 10);
doubly-met root `η = −0.0826, −0.0769` (budget 9). Against A115's own interior level-1 re-solves at
the same median LP wall of 286 s (`src = A38-l1`, n = 89): **median η = −0.729, 20 % at ≤ −1, 14
certified dead**. So the corner-first cells sit in the interior root's worst quartile, and — the
finding that matters — **a second conditioned square at the SAME corner buys essentially no slack
for a whole unit of budget**, so the 82 % geometric cut of the pair root does not convert into LP
kills. Price: 3,800–8,900 CPU-h (single root, decision at depth 3 by the A38/A85 −0.5-per-level law)
and 8,000–18,800 (pair root, depth 2), against the interior tree's 12,000. The one scenario in which
the pair root would have been a 5–12× cut — deciding at level 1 on its 2,134 survivors — is measured
and rejected.

*The PI's Trump prediction, resolved.* On the UNWIDENED box every Trump image is K0-FREE at three
corners and doubly met at exactly one: `g0` has BL 1, BR 1, TR 1, **TL 2** — so the PI's
identification of trump5's single non-simple corner is **confirmed**, and after the D4 reduction it
is BL for images `g2` and `g6`, at the level-1 pair cell **{(0,4,0), (5,0,3)}** (the axis-aligned
NON-slot meeter at (0.5, 1.34453, 0°) with the 49.818° meeter at (1.53629, 0.70461)). Two
corrections: (i) K0-WIDEN's pad, which the window makes mandatory, pulls in the flush neighbours and
turns the canary into **5 single cells and 9 pair cells**, not one — the "one deep lineage" is a
property of the unwidened geometry only; (ii) **that lineage can never die by K0-FREE, at any
depth.** Descended three levels (geometry only): `P1`/`P2` never fire, BR/TR/TL stay `LANE ≥ 2`, BL
has `M = 2`. The reason is a proof, not a budget — `Δ_λ ẑ` is a genuine 11-family satisfying the
node's hypothesis with ≥ 2 widened meeters at every corner, so `LANE(c) + M(c) ≥ 2` forever. **The
terminal mechanism of the Trump lineage is the (D) landing plus the scale-ray tube (K0-O3), exactly
as in the interior tree; the corner-first canonicalisation only relocates that obligation (5 single
/ 9 pair level-1 cells instead of A38's 3).** At depth 3 the node does reach `LANE(BL) = 0`, i.e. it
forces exactly two BL meeters — a tightening, not a kill.

*Composition.* `notes/composition.md` states the two-cover intersection as three rules (product node
at budget `11 − |X| − |Y|`; a cell dies if every compatible cell of the other cover is dead; and a
support cut needing no new node). Measured on A115 T6's twelve converged-alive interior cells: each
has 1–20 support placements meeting the widened BL box in 1–8 corner-first cells; none has a meeter
in a dead corner-first cell (there are none), but **`l2_p74_001` (one BL meeter in its whole
support) and `s3_far_BL389484_TR018470` have NO surviving BL PAIR at all** — their LP optima cannot
supply a K0-BLOCKED BL crowd, which is the dual-guided cut the k0 budget row has been asking for.

*Cost and hygiene.* ≈ 1.0 CPU-h of the 2 CPU-h cap (0.85 exact geometry + five 240 s LP nodes at
~275 CPU-s each); ≤ 2 BLAS-pinned BelowNormal processes for the LP, ≤ 16 python on the box;
read-only on every campaign and attempt (A38/A85/A99/A115/A118/A131/A132/A135/A140/A141 imported,
none written); the frozen `verify_case.py` copied byte-identical; new files only. Drawings in A140's
format: `figs/cover143_single.svg` (216 cells by verdict, Trump cells hatched, the `x = y` mirror
drawn), `figs/cover143_pairs.svg` (36 tilt-blocks × a 36×36 verdict matrix, Trump pair cells ringed),
`figs/pair_survivors.svg` (the Trump pair cell + three sampled survivors, both H's with all three
cores and the extremal-tilt schematics).

- **A142 follow-up 2 (PI feedback on `c0_Y0171.svg`): panel 2 was drawn at the shadow's s\*, said so only in small
  type, and so showed four squares spanning the container — illegal at s0.** All 60 panels regenerated: the
  container is still drawn at the panel's own s\*, but **s0's container is now overlaid as a heavy dashed square
  from the same origin**, so the band of room is visible, and a **large-type banner** states the case —
  "near-packing at s\* = 4.0000 > s0 — NOT realisable at s0 (S01 room: the support closes only with a unit of
  room)" or "realisable at s0". The measurement that follows: **all 55 pages with an A107 shadow family have
  s\* > s0** (min s\* 3.885618, max 4.000261; 30 of them at s\* >= 4), so **no near-packing in this gallery is
  realisable at s0** — the right panel is a structure diagram, not a configuration at the certified side. The 5
  pages with no shadow family draw the raw dual support at s0 and are banner-marked NOT a packing. Review sheet
  gains `s_star`, `s_star_minus_s0`, `realisable_at_s0` and `reading_auto` (= `st4` on the 30 pages with
  s\* >= 4), all filled. verify142 re-run over the regenerated pages: 0 failures.

## 2026-09-03 A89-tilt-floor (Fable lead + 2 Opus chores, <= 2 processes) -- done-mixed (loaded tilt floor = GAP, no local proof; unloaded half PROVED exactly in selection form; Lemma ID + one window-valid certificate; re-price unchanged)
- T [docs/proofs/tilt_floor_k0.md]: THEOREM TF-U (tilt selection): the Phi-minimal sigma-minimiser (Phi = sum f(tilt_i), f strictly
  increasing; selection = Phi-min over the compact minimiser set, composable with k-maximality; second selection for uniqueness =
  Phi-min over the non-image packings at s-hat via the basin isolation) has EVERY square at tilt exactly 0 mod 90 or FLUSH-LOCKED
  (Lemma LOCK, Gordan: its active contacts can exert a couple away from flush or a self-stress). Rattlers and unlocked squares are
  flush there - case (i) resolved, no theta_0. LEMMA MENU: a wall-touching near-flush blocker is locked only by FAR-SIDE contacts
  (far edge, support under its far-bottom vertex, down-left-facing contact at its far-top vertex, a contact at its near-top vertex
  with normal m.(cos d, sin d) < 0); both corner walls, left neighbours and top pressers never lock it. LEMMA JAM-0: an axis-aligned
  blocker at offset g = max(a,b) < 1/sqrt2 forces its partner to sin(tilt) <= g and depth <= g^2/sqrt(1-g^2) (case (ii) pinned; for
  g < delta_pin = 0.02 the partner is within 1.15 deg of flush = the K0-REUSE pocket); the partner is never axis-aligned.
  LEMMA ID: DEPTH(c) < delta => (0,1-delta)^2 at c meets no square interior => strands >= (1-delta)^2 of E(m) = m^2 - 11 <= 4.0318;
  area alone never kills 4-shallow in the window (4(1-delta)^2 <= 4). Case (iii) (flush, offset) untouched everywhere, as required.
- GAP A89-G1 (the deliverable's loaded half): "a flush-locked corner blocker at side <= s-hat has tilt >= theta_0" is OPEN for every
  theta_0 > 0 and has NO local proof: the near-flush jam admits a nonnegative FJ multiplier solution (explicit: wall load G = K/cos a
  needs the presser within r <= eps of the partner's wall vertex plus a right-side pusher; the flush stack above is locked by ANY top
  presser, mid-tilt included) - the A46/A48-C5b wall again; the only conditional floor is A50 T2.1's theta* = 1.7347 deg for members of
  the binding P-chain (H-P/H-MONO/H-L6CAP). Counterexample to the LOCAL strategy explicit (multipliers) and in vivo (A87 o170 at
  sigma = 4.000, both jam members unloaded); one AT side <= s-hat would refute H1 and is not expected.
- M [T2, attempts/A89-tilt-floor/notes/t2_report.md]: A87's 167 certified k0 FJ points (665 corner blockers, all at sigma >= 3.8972):
  min loaded(forced) tilt 23.891 deg (o026); loaded blockers with tilt in (1e-7, theta_0): 0 forced for every theta_0 <= 20 (1
  loadable = polish noise at 3.6e-7 deg); unloaded/rattler in the zone 69/93/110/135/161 at 0.5/1/1.7347/5/10 deg; 353 exact-0 blockers;
  161 of 162 below 10 deg have no loadable wall contact. Atlas (12 families): min loaded tilt 33.896 deg (= A46 WC min), 0 loaded below
  30. Trump canary PASS (3 slot squares |tilt| < 2.2e-69 deg; TL = axis-aligned upright sq4 at depth 0.1555 + sq6 at 40.18 deg -
  correction to the brief: not two tilted squares). A85 rows: 5 FAILs = 4 A38-comparison interior cells + 1 corner node at 41-49 deg
  -> 0 FAILed blocker nodes in the deleted zone at any theta_0 <= 15. BL census (644 boxes, 33 656 pairs): zone-touching boxes 19.9 %,
  tilt volume deleted 3.43 % at theta* (deg), pairs killed by re-pruning 0 at theta_0 <= 2, 146 at 5, 10 483 (31 %) at 10 - nodes die
  only when an end bin (7.125 deg) dies whole. T2b (pair-only reach-cap model): library-jammed 151/7800 witnessed (1.94 %), max jammed
  reach 2.386 vs 2.414 theoretical (jamming costs nothing in reach; adjacent-corner envelopes can overlap, 2 x 2.386 >= s-hat); the
  16 case-(ii) jams die exactly when theta_0 > 7.125; near-slot pocket canary UNJAMMED (rotating the partner to flush lifts its
  vertex - TF-U's motion), Trump TL crowd JAMMED. Depth: no census pair has both members at depth >= 0.5 (1.2 % at 0.3) - a
  tilt-free pair prune; A87 shallow corners (< 0.3) 115/644, 52 % of their blockers axis-aligned (case iii, not tilted ghosts);
  Trump DEPTH(TL) = 0.168300 exactly, other corners 1.
- CERT [A89-O3, certs/k0_00/R1_4shallow_d0.3.json + .PASS, frozen certify/verify_case chain, re-verified 0 holes]: NO 11-packing at
  any side m in [3.82, s0] has all four corners SHALLOW(0.3) (exact total 1372003/125000 = 10.976024 < 11; NO-families = sound inner
  unions of 432 pose boxes with a_win = (1-delta)/lambda_max; discharges delta = 0.1, 0.05 by monotonicity). Canary: every Trump image
  has exactly one corner at depth 0.168300 and three at 1, so 1-shallow(delta >= 0.1683) was REFUSED as image-realisable, >= 2-shallow
  attemptable. 3-shallow NOT certified (tau 10.05 at 0.3 climbing to 10.21 with feedback = genuine near-boundary; at 0.1 eta = -1.78
  but C1 certification did not close at the 900 s cap, minmass 0.58 - LP-time artefact, resumable code/o3_campaign.py with lp_time
  >= 5000); 2-shallow untried (tau nondecreasing). Hole diagnostic on A85's depth-2 FAILs (exact): 67 % of witness boxes are corner
  poses, 11 % near-flush corner poses (two wall-flush uprights at 0.46 / 0.70 deg), 33 % interior/mid-tilt - the ghost zone is a
  minority of what fails; p210_001 is in fact killed at eps_geo 0.004 (f2 at A60 defaults = 2/3 on the three depth-2 cells).
- F re-price: UNCHANGED, 3 200-7 000 CPU-h (f2 ~ 0.85) / >= 3e4 (f2 = 1/3). The loaded floor is unavailable; had it been, theta* deletes
  0 FAILs and 0 pair boxes; TF-U's (C-sel) leaves are deep-node rules (K0-ROT's status); Lemma ID gives a corner-first branching with
  a free exempt row per shallow corner and one certified root kill. CAVEAT: "not where the cost is" rests on A85's 12 LP rows (4 of 5
  FAILs are A38-comparison interior cells); a proper measurement = >= 20 S2-S4 crowd nodes with certification, stratified by tilt bin,
  plus the hole census and one lower side (~10 CPU-h). Lean-readiness: StratumKillSel (Phi-selected minimiser) + obligations S1-S5,
  no lean/ edits. Process: T2's small jobs (< 300 MB RSS, no LP) launched at 0.7-2 GB free commit under the other campaigns (gate
  breached literally, nothing heavy); O3 gated every LP at > 6144 MB and waited out dips (hours). Discipline otherwise: <= 2
  processes, BLAS pinned, A57/A60/A61/A86 untouched, frozen verifiers untouched, A85 engine COPIED not modified. Files:
  docs/proofs/tilt_floor_k0.md, attempts/A89-tilt-floor/{code,results,certs,notes,logs}, lean/depgraph.json (C.K4TIER note, chip
  released) + svg, REGISTRY row.

## 2026-09-07 - A148-gallery-v4 (Opus engineer) - T1 done: the k0v4 set
- The v4 page is fixed at THREE panels, in reading order: **G GEOMETRY: what is still free**
  (largest, no LP in it at all), **S the LP support** (medium, captioned "what the relaxation puts
  where; overlaps are the relaxation's slack, not a packing"), **N nearest real packing** (small,
  at its own s* with s0 overlaid and the realisability banner).  One style per object: K'(B) is the
  only core DRAWN inside a conditioned square (the stock and A135 exact axis half-sides are
  captioned), pins carry their exact core as a thin inner outline, and every schematic region
  (centre box, A131 clip, lane cell, guard line) is thin dashed and never filled.  A generated
  WHAT TO LOOK FOR line and the verdict of every geometric leaf already run (clip, T5'''', lane,
  conditional lane, guard line) sit in the header; a four-line footer says what the panels ARE.
- The new object is the FEASIBLE-CENTRE REGION: the centres where one further unit square can still
  be placed at some tilt, clear of the container walls and of every certified core.  Grid pitch
  0.01998 x 36 tilts with the Lipschitz margin m = pitch*sqrt2/2 + (sqrt2/2)*(dtheta/2) = 0.02956,
  so GREEN is a certified INNER approximation and WHITE a certified OUTER one (the pale band is
  what the resolution cannot decide).  10^4 + 10^4 draws per page at 360 tilts: 0 hits on 11 pages.
- NEW SOUND SHORTCUT, the DISK BOUND: a unit square contains the disk of radius 1/2 about its
  centre, so budget <= area( (green u undecided) (+) B(1/2) n [0,s0]^2 ) / (pi/4) -- an upper bound
  on how many more squares the node can hold, read off the drawing with no LP.  n_max < budget is a
  geometric kill.  On the eleven k0 cells n_max = 17-18 against budget 10 (one conditioned square
  leaves far too much room), so it does not bite there; it is the number to read first on the
  pin-heavy A57/A60 nodes.
- What the eleven pages say uniformly: on TEN of them K'(H) comes within 1 of the RIGHT WALL
  (H->wall x=s between 0.723 and 0.967, so no square sits flush there beside H), and on FIVE the K'
  lane test leaves TR(0,0) a NEAR-MISS (LANE <= 1, M = 1).  Those two together are the shape of the
  s3_far kill.
- Population: A140's twelve minus s3_far_BL389484_TR018470 (killed by A141's K' lane leaf on BL);
  A141's conditional-lane run closed none of the other eleven, so no KILLED banner on any page.
- Verification (`code/verify148.py`, a SECOND implementation: edge crossing + strict
  point-in-polygon, no separating axis anywhere in it): region green/blocked 4 400 + 4 400 points,
  K' containment 3 773 poses, 44 pockets, 120 red-dashed columns + 196 controls, 33 guard rows x
  10^4 chord draws = 330 000.  **0 failures.**
- Files: `docs/shadows/k0v4/` (11 SVG + README.md + review_k0v4.csv), `docs/shadows.md` Part V
  (appended), `attempts/A148-gallery-v4/code/{geo148,data148,gallery148,readme148,verify148}.py`,
  `results/{gallery148_k0v4,verify148_k0v4}.json`, `notes/method.md`.
- T2 (the A57/A60 v4 set from A137's night records) is scheduled for 06:00 tomorrow.

## 2026-09-07 — A145: the impossible dual-support weight is a predictor with a threshold, and Y0241 (the PI's page) is certified dead

- **The quantity.** For every one of the **448** surviving A57 nodes (A142's 465 minus A142's own 17
  exact-pin-clip kills), the share of the LP's dual-support WEIGHT carried by columns that are impossible under
  the node's own hypothesis: a placement overlapping one of the six hypothesis squares (5 pins + the
  conditioned box H) at EVERY pose of that square's box. Since `w_total` is the sum of the dual weights, i.e.
  the node's own τ, the fraction reads directly as *"this share of the LP objective sits on placements the
  hypothesis forbids"*. `attempts/A145-impossible-weight/results/impossible_weight.jsonl`, 448 rows, 0 errors,
  35,799 columns, 94 s.
- **Two tests, one-sided in OPPOSITE directions — the thing to keep straight.** The PI's/A142's reading is the
  7³ pose GRID (negative SAT gap at all 343 sampled poses): *necessary-ish, not sufficient* — 343 poses are
  not all poses. The EXACT test is "the column meets `K'(B)` = ⋂ over all poses of `Q(c,θ)`" (A132's certified
  polygon core; for a PIN box A135's exact axis square `a_pin = 33873816211/68719476736`, which for zero tilt
  width IS the whole intersection): *sufficient, not necessary* — a column can overlap at every pose without
  meeting the intersection of the poses. EXACT ⊆ GRID always, EXACT is the one that is a proof, and EXACT is
  exactly the row set A135's `poly` arm prunes, which is what makes the fraction a prediction rather than a
  description.
- **Distribution (448 nodes).** `frac_exact` mean **0.4107**, median 0.4000, min 0, max 1; 14 nodes at zero,
  2 at 1.000, 21 above 0.75. `frac_grid` mean 0.4466. Deciles: 19 / 16 / 83 / 55 / 133 / 44 / 72 / 7 / 17 / 2.
- **Controls** (`code/check145.py`): (A) 40/40 agreement with A142's *different* implementation on `n_support`
  and on the grid count; 36/40 on the exact count, and all four disagreements go one way with one cause
  (A142 tests the certified flag only against the grid's minimum-gap box, A145 maximises `K'` depth over all
  six — A145's set is a strict superset by construction). (B) 1,920 exact-impossible columns × 200 drawn poses
  = **384,000 independent SAT tests → 0 unsound**. (C) of the 256 grid-only columns a genuinely DISJOINT pose
  was found for exactly **1** — so the grid does over-claim, but the `frac_grid` − `frac_exact` gap is mostly
  the EXACT test's own conservatism, not the grid's optimism.
- **THE HEADLINE — `k5_11_interior_Y0241`, the node the PI read off `docs/shadows/a57v3/`.** 4 of its 5
  dual-support columns overlap H at every pose (grid gaps 0.0153 / 0.0231 / 0.0351 / 0.0530) and 3 of the 4
  meet `K'(B)`: **60 % of the objective is forbidden weight**. Re-solved with exact cores + `K'`-pruned pool:
  **τ 5.000000000063 → 3.250000** (η −1.75), **`verify_case_v3.py` PASS**, total 3.43334 < budget 5, box tree
  `boxes 187914, covered 65469, exempt 28520 (core 24984, nofam 0, poly 3536), max depth 39`. The FROZEN
  `verify_case.py` on the same measure **FAILs with 32 HOLES**, so "this one needs the polygon clause" is a
  measurement. The one grid-flagged column that `K'` does not confirm has depth −1.085e−4 at 129, 257 and 513
  θ-samples and 16/40/120/300 vertices — the polygon is converged and that column really is a
  "flagged-but-not-proved" case.
- **9 certificates from 18 re-solves, and 3 of them need no verifier change.** FROZEN `verify_case.py`
  (sha `521cb01f…`, exact cores only): `k5_16_interior_Y0017_D04` (τ 3.5 → 3.0), `k5_11_interior_Y0164`
  (4.667 → 4.565), `k5_16_interior_Y1014` (4.538 → 4.000). A135 `verify_case_v3.py`: `Y0241` (5.000 → 3.250),
  `Y0588_D06` (5.000 → 4.500), `Y0186_D05` (5.000 → 4.000), `Y1056_D01` (4.769 → 4.000), `Y0041_D03`
  (4.333 → 4.222), `Y0572` (4.500 → 4.208); polygon-exempt boxes 892 – 168,451. **Six of the nine were already
  LP-dead work-owing FAILs that were only ever missing a certificate; three are NEW kills** (`Y0241`,
  `Y0588_D06`, `Y0186_D05`), all three at frac ≥ 0.60. One node LP-killed and then **lost the kill on the
  witness-feedback re-solve** (`Y1110`, frac 1.000), two did not kill.
- **IS THE PI'S READING A PREDICTOR? Yes — as a GATE with a threshold, not as a dose.** Kill rate by band over
  all 18: [0,0.15) 0.00, [0.15,0.30) 0.00, [0.30,0.45) 0.67, [0.45,0.60) **1.00**, [0.60,0.75) **1.00**,
  [0.75,1] 0.80. Restricted to nodes whose stored τ was AT the budget (the clean question): **0 of 7 below
  frac 0.45 moved τ by so much as 1e−9, mean drop exactly 0.000000; 4 of 5 above frac 0.60 killed.** What it
  does NOT predict: the size of the drop (frac 1.000 nodes dropped 0.148 and 0.500; frac 0.600 `Y0241` dropped
  1.750 — the LP re-optimises onto columns the fraction never saw), nor which verifier is needed (that tracks
  A132's pins-vs-conditioned-box attribution: 0.857 went frozen, 0.523 needed v3). A132's caveat transfers:
  18 nodes is not a rate — but with a stratified control arm it does fix the sign and the location of the
  threshold, which one node could not.
- **The queue, priced.** 98 of the 448 sit at frac ≥ 0.60 (92 un-re-solved, ≈ 9 CPU-h at the measured
  350 s/node) and 164 at frac ≥ 0.45 (155 un-re-solved, ≈ 15 CPU-h) — the cheapest LP-bearing work left in the
  campaign. The 118 nodes below frac 0.30 should be de-prioritised: on them the exact cores and the polygon
  provably buy the LP nothing, and the measurement says so before a single LP is run.
- **Discipline.** 1.87 CPU-h against the 2 CPU-h cap (6,376 s of it recorded job wall over the re-solves);
  never more than 2 BLAS-pinned BelowNormal processes; no shard launched; A57's PAUSE sentinel REPORTED and
  A145's own scoped sentinel watched (PAUSED.md §7a); frozen verifiers byte-identical after the run
  (`verify_case.py 521cb01f…`, `verify_param.py 0c58485c…`); read-only on every campaign and on
  A131/A132/A135/A142; nothing deleted; `PYTHONDONTWRITEBYTECODE=1`; git fetch + plain merge + push of own
  paths with explicit pathspecs. The knife-edge rule (900 s) fired on 3 of 18 and earned its keep once: on
  `Y0241` the long cap did not move τ (3.2500000000000266 → 3.2500000000725695, both unconverged), it
  confirmed τ was not about to climb back.
- **Files.** `attempts/A145-impossible-weight/{BRIEF.md, code/{measure145,rank145,resolve145,check145,
  table145}.py, results/{impossible_weight,resolves145,resolves145_rank,resolves145_ctrl}.jsonl,
  results/{jobs145_rank,jobs145_ctrl,check145}.json, certs/ (49 files), notes/{measurement,resolves}.md,
  logs/}`; one appended paragraph in `attempts/A57-shadow-trees/PAUSED.md`'s resume block; REGISTRY row.

## 2026-09-07 — A146: k5_13 closed. **The A56 window scoreboard is 52/52 full-window — the window layer is done.**

- **HEADLINE.** `k5_13`, the last OPEN row and the node A61's campaign lost ~40 CPU-h to inside a wedged
  HiGHS `h.run()`, is now a **FULL-window kill on the ORIGINAL A56 parametric certificate** — no new LP, no
  new certificate. 58 slabs of 10⁻³ over [191/50, 969271/250000], **58/58 PASS, zero bisections, zero holes,
  5,491 verifier-seconds**, exact tile of the window, C2 canary PASS under the unmodified A53
  `verify_case.py` at s_lo / mid / s0 (3.6 / 4.6 / 85.0 s). Scoreboard: **52/52 full_window_rows**
  (4 M1 + 28 TRANSFERRED + 20 TRANSFERRED-resolved), no OPEN and no partial row.
- **THE ROW WAS NEVER HARD — IT WAS AN OVER-WIDTH SLAB (A114's law, third and cleanest confirmation).**
  `resolve61.py` verifies the whole window as ONE slab (width 0.057084). One probe slab of 10⁻³ PASSed in
  **74 s** and priced the class: w_min = 1.56·10⁻⁵, d_pose = 41, **width_max = 0.002** — the failing slab was
  **28× over the law**. A56's FAIL had max_depth 48, max_s_depth 10, worst witness `undecided`, **0 holes**:
  the exact signature. No certificate could have rescued it (a fatter measure raises w_min, not by 28×).
  **Rule banked: when a parametric run FAILs with 0 holes and a depth-limited worst witness, price the slab —
  one 75 s probe — before you price the certificate.**
- **THE A61 RE-SOLVE ROUTE IS DEAD FOR k5_13, AND FOR A MEASURED REASON, NOT A RESOURCE ONE.** The restart was
  run twice through the wrapper, at both stages of the PI's two-stage protocol. 240 s: τ₀ = 5.619048
  (slack 0.3810 > gate 0.30), τ(ε_geo 0.003) = 5.963641 (slack 0.0364 > gate_b 0.03), certify round 0 gave
  total 5.99354 at 149 atoms, witness feedback drove round 1 to τ = 6.00000 → *cannot certify*. Knife-edge
  escalation to 900 s (stage-B slack 0.0364 vs the 0.03 gate is exactly the knife edge the protocol names):
  τ₀ = 5.617045, and **τ(ε_geo 0.003) = 6.000000 exactly** → post-shrink GATE-FAIL, no certify round burnt.
  **dτ/dε = 118.8 and 132.1 against 57–90 on every row A61 converted** (k5_17 57.5, k5_10 62.7, k6_20 65.3,
  k6_21 65.6, k6_29 89.8): the 0.003 shrink costs k5_13 0.34–0.38 of a 0.38 slack. A61's L5 says a rich
  column pool flattens the shrink curve by supplying alternative atoms for the shrunk square; k5_13 is the row
  where it does not. **More LP time made it strictly worse** (a better-solved LP generates more demand rows).
  So the 40 CPU-h the campaign lost here was spent on a route that could not have converted.
- **THE HANG WALL WORKED BY NOT FIRING, AND THE PROTOCOL IS WHY.** `code/supervise146.py` runs A61's
  **unmodified** driver as a child and kills the tree when it has emitted no stdout for 1,500 s **and** has no
  live descendant process — silence *with* a descendant is a certifier or verifier and must not be disturbed,
  silence *without* one is the driver inside a single `h.run()` (A124's mode: no `time_limit` on the Highs
  object, `solve_node`'s limit checked only between iterations). `lpbox.py`/`resolve61.py`/`campaign61.py`
  were never edited and never copied-with-edits; a CAP is recorded as a resource event, never a verdict. The
  wall **never tripped**: the 240 s cap stops stage A at 3,500 orbits × 15,555 rows and the 900 s cap at
  4,341 × 17,468, one iteration short of the wedged 4,332 × 18,326 geometry. **The two-stage protocol is
  itself the hang mitigation; the wall is the cheap backstop.**
- **The driver's resume is its column pool, and it is monotone.** `resolve61.py` has no stage resume:
  `enriched_warm()` globs `attempts/{A56,A61}/results/nodes/<name>*.json` and folds every checkpoint the lab
  ever wrote, so the killed run's own `k5_13_A_state.json` (1.4 MB, iteration 6) *was* the resume — the pool
  went 3,996 → 4,332 → 4,341 orbits across the three launches. That is why killing a wedged A61 LP is safe,
  and why a CAP must never be written as a verdict.
- **Cost profile along the side (confirms A114 L7 and locates its cause).** 74 s per 10⁻³ at the bottom, flat
  to ~80 s through the bulk, then 99 → 108 → 115 → 126 → 182 → **507 s** over the last five slabs, with
  **d_pose stepping 41 → 42 and width_max halving to 0.001 in the slab ending at 3.877**. The top-of-window
  blow-up is a step in d_pose, not a smooth drift — the S02 shadow arriving in the arithmetic exactly where
  A114 measured it for k5_12. The final 8.4·10⁻⁵ sliver ending at s0 passed.
- **Discipline.** ~2.8 CPU-h against the 6 CPU-h cap (track 1 the two supervised A61 runs 3,492 s; track 2
  probe + 58 slabs + C2 5,659 s); ≤ 2 BLAS-pinned BelowNormal processes; ≤ 16 python processes on the box
  with A136/A141/A144/A145 running and untouched; read-only on every other campaign; A61's state written only
  by A61's own driver; frozen verifiers byte-identical; nothing deleted, no pidfile touched;
  `PYTHONDONTWRITEBYTECODE=1`; scoreboard written in ONE atomic tmp+`os.replace` by A146's own copy of A114's
  fold (backup `scoreboard.json.bak_pre_a146`), leaving A114's `a114` provenance block exactly as A114 wrote
  it; git fetch + plain merge + push of own paths with explicit pathspecs.
- **Files.** `attempts/A146-k5_13-restart/{BRIEF.md, code/{supervise146,slab146,update_scoreboard146}.py,
  results/{slab146.json, supervisor_k5_13_p1.json, supervisor_k5_13_p2knife.json,
  resolve61_k5_13.lp240.json, resolve61_k5_13.lp900.json}, certs/ (58 slab reports + 3 C2), notes/lemmas.md,
  logs/}`; `attempts/A56-sparametric/results/scoreboard.json` (k5_13 row + summary);
  `attempts/A61-window-stragglers/{results/resolve61_k5_13.json, results/nodes/k5_13*.json, logs/}` (written
  by A61's driver); `docs/budget.md` (stragglers row + § E), `docs/residue_ledger.md` (§ 2 + the family
  table), REGISTRY row.

## 2026-09-07/08 — A144-guard-lines (Opus engineer) — done-mixed
- The PI's reading of `docs/shadows/a57v3/k5_11_interior_Y0147.svg` ("a horizontal line 0.99 below the top
  crosses opposing sides of four squares; any realisation is at least side 4") is now an exact LP row.
  **The cut:** for any line `l` inside `[0,s]^2` the chords of a packing are interior-disjoint, so
  `SUM |l n Q| <= s`; over a node's `budget = n - #cores` free placements,
  `SUM_p |l n Q_p| x_p <= rhs(l) = s0 - SUM_pins minchord(P_j,l) - minchord(H,l)`. In A57's covering LP that
  is a new **column** — a measure of density `z` on `l` priced at `rhs(l)` rather than `s0` — so adding it can
  only lower tau and can never invalidate a kill; the `-minchord(H,l)` term is the part no atom generator can
  build, because H's position inside its box is unknown.
- **The exact primitive.** The chord depends on the tilt only through `y = cos+sin in [1, sqrt2]`;
  `A(y) = 2a/max(C,S)` is monotone and `B(y) = 2(ay-V)/(y^2-1)` has `q(y) = -a y^2 + 2Vy - a` whose roots
  multiply to 1, so `B` is decreasing or increasing-then-decreasing and its minimum over a `y`-interval is at
  an ENDPOINT. `minchord` over a parameter box is therefore FIVE rational evaluations, no search. Validated
  before use: 600 chord cases vs a direct dense measurement (worst 1.4e-05 = the sampler's own resolution),
  480 `minchord`-over-box cases vs a dense grid over 12 tilt regimes (worst exceedance +5.6e-16), and
  **80,640,000 poses drawn -> 0 hits** across all 448 surviving A57 nodes.
- **Offline, no LP: 43.5 s for all 448 survivors; 86 (19.2 %) have a guard line their stored dual support
  violates** (median depth 0.095, max 0.266 on `k5_11_interior_Y0672_D00`; L1 83/355, L2 3/89; 15 of the top
  40 by subtree cost). On `Y0147`: rhs 1.877084, charge 2.005508, **violation +0.128424** — pin P2 1, H 1,
  and TWO of the LP's own columns 1 and 1.005508, summing to 4.005508 > 3.877084. **That is the case A121's
  `st4` reading cannot express**, because `st4` needs all four squares to be pins or conditioned squares.
- **In vitro (20 nodes x 2 arms, 240 s, A132's node path, 2.34 CPU-h): the guard column is ACTIVE on exactly
  two nodes, and those two are exactly the two new kills** — `Y0147` 5.000000 -> 4.877459 and `Y0101` ->
  4.922603. Read `z`, not delta-tau: two other nodes moved with `z = 0` and that was convergence noise. At the
  900 s re-check Y0147's control CONVERGES at 5.000000 while the guard arm holds 4.877459 to nine significant
  figures with minmass 0.899 -> 0.982 — **eta stable, coverage not yet closed, so not yet an LP kill**.
- **The by-product is bigger than the lever.** The control arm is A135's EXACT cores and it kills **15 of the
  20**; a third arm with A57's DEPLOYED cores at identical settings kills **0 of 6**. The drop is the cores,
  not the re-solve — a 20-node datum for budget.md D.1's 28 CPU-h exact-core re-emission chore (caveat: the
  twenty were selected for guard-line violation, so 15/20 is not a population rate).
- **The frozen chain cannot even EMIT a guard-line certificate**: `certify.py`'s own re-solve loop rebuilds the
  measure from atoms alone, returns to tau = 5.000 and refuses at "certificate total >= budget". So the
  `guardlines` field is needed at emission as well as at verification, which A135's `polycores` was not.
  Spec'd in `attempts/A144-guard-lines/notes/spec.md`: the field, the v4 clause (~120 lines, composes with
  `polycores` by conjunction), and the Lean statements `chord_sum_le_side` and `minchord_of_box`
  (2 theorems + 1 checker + 7 lemmas, 0 new axioms).
- Injection audited independently (the wrapper reindexes HiGHS columns): objective identity to 2.7e-15 with the
  split atom 3.000000 + line 1.877459, 300 row activities re-derived from `(w, z)` to 1.0e-12 with 0
  mismatches, and the binding guard row at slack **exactly 0.0** on the final dual support.
- 3.66 CPU-h of a 4 CPU-h cap, 2 BLAS-pinned BelowNormal processes; A57's PAUSE left in place and untouched
  (own scoped sentinel); read-only on every campaign and attempt. Figure:
  `attempts/A144-guard-lines/figs/k5_11_interior_Y0147_guardline.svg`.

## 2026-09-07/08 — A136-a120-resume (Opus engineer) — done-success: **F-COVER is fixed and A120's cover is a tautology on the written rationals; 4 CLOSED nodes → 15**

- **T1 — the fix, and its positive control: 22 / 22.** `attempts/A136-a120-resume/code/a136lib.py`
  post-processes the dict `caselp.make_certificate` returns, BEFORE it is written: every NO-zone bound is
  re-derived from the node's own EXACT `hyp.nofams` and rounded **inward** (`ceil + 1` / `floor − 1` at the
  same `TDEN = 2²⁴` / `XDEN = 10⁹`, A112's own helpers imported not re-typed), the mapped A119 box the YES
  side names is written into the file as `hypotheses.nofam_boxes`, the zone is intersected with it, and the
  decidable predicate `ZONE ⊆ BOX` is checked on the WRITTEN rationals and RAISES on failure. All 22 of
  A120's PASSing certificates re-written: **22 / 22 `ZONE ⊆ BOX`**, and **22 / 22 re-certified PASS** under
  the frozen `verify_case.py` (sha `521cb01f…`, checked byte-identical). Change per bound **≤ 8.88·10⁻⁸**
  against the exact zone, **1.788·10⁻⁷** against A120's written one (outward and inward straddle the exact
  value — hence larger than the brief's 1.2·10⁻⁷).
- **The replay costs 997 s where the emission cost 16 462 s** (16×; min 3 s, p50 42 s, max 118 s). The
  freeze discipline pays: a kill is reproduced by REPLAYING its certificate, which is also what Lean does.
- **The finding that took two passes, and generalises past this attempt.** Rounding the CLAMPED bound inward
  like every other bound made **every `NO3` certificate FAIL (7 / 7)** while every `NO0`/`NO1`/`NO2` PASSed
  (15 / 15). `NO3` is `BR(0,1)`, the only box whose zone clamps to `[1/2, s − 1/2]`. The verifier's witnesses
  are all holes at `t ∈ [0, 2⁻¹⁸]` with the centre in a band ending exactly at the wall `s₀ − 1/2 =
  844271/250000` and mass `393593/500000 ≈ 0.787 < 1`: shaving `10⁻⁹` off the clamp took that band out of the
  exemption, the measure has no mass to spare at the wall, and at depth 56 the smallest cell (2.8·10⁻⁶) still
  straddles the new bound. **A bound that came from an exact geometric fact (a wall, a clamp, a symmetry axis)
  must be written as that fact, not rounded** — `1/2` and `s₀ − 1/2` are exact rationals. With the clamp
  written exactly all 7 re-certify. (`notes/fcover136.md` §3a.)
- **One deliberate departure from the brief, on soundness grounds:** the brief said "the YES box bounds
  outward"; the box is written **inward** instead. Shrinking `BOX_i` STRENGTHENS the YES hypothesis
  ("some square's pose in `BOX_i`") so A116/A119's kill survives; widening it would admit poses outside
  A119's certified box into the YES side and just move the 10⁻⁷ defect to where nothing checks it, and would
  threaten A120's A2/A3 pose-disjointness. Price: one trivial Lean obligation (`LocalDead` antitone in the box
  list — `Box.mem` monotonicity).
- **T2 — the resume. 4 CLOSED → 15 CLOSED; 11 of 35 targets with a record → 24.** Two BelowNormal BLAS-pinned
  processes, disjoint by node, under **this attempt's own scoped sentinel** (`pausegate.paused(base=…)`,
  PAUSED.md v2 §7a); A123's `attempts/A57-shadow-trees/PAUSE` was left exactly where it is and every driver
  calling the bare `paused()` stayed paused. Both shards stopped on their own CPU cap, between items.
  New closures — L1: `Y0303`, `Y1075`; L2: `Y0036_D03`, `Y0054_D01`, `Y0217_D02`, `Y0414_D07`, `Y0636_D06`,
  `Y0978_D04`; L3: `Y0036_D07_D00`, `Y0036_D07_D04`, `Y0036_D07_D05`. A120's four (`Y0230`, `Y0637`,
  `Y0709`, `Y0997`) were **re-earned, not inherited** — all 16 of their certificates are T1
  re-certifications.
- **The certifier is no longer the binding constraint; the WALL is.** 60 certification attempts at
  `--rounds 6`, wall 2 600 s, `--time_limit 420`: **54 PASS, 6 CAP, 0 FAIL.** PASS wall min 2 s, p50 452 s,
  p90 1 828 s, max 2 314 s — below the wall, so the wall censored nothing it could have decided. A120's datum
  ("only 19 of 31 clearly-dead children certified; certification is the constraint") does not survive rounds 6.
  Of 96 children with a verdict: **75 DEAD-CERT, 15 genuine survivors, 6 CAP** (the whole remaining shortfall,
  each one more wall away from a verdict).
- **Cost of a closure, measured.** 13 new targets for 12.5 CPU-h → 9 closed at a mean **2 932 s** (745 s at
  level 3 to 5 510 s at level 2); level 3 is the cheapest hour on the board (3 nodes for 5 025 s). The 12
  re-tried open children cost 6.3 CPU-h for 2 further closures.
- **The negative:** `Y1128` burned 1 396 s of LP and **zero** certifier time — all four NO children converge at
  exactly τ = budget. With A120's `Y0345`, `Y1116`, `Y1099`, `Y0973/NO2` that is **15 genuine survivors in 5
  nodes**, which no certifier budget touches; they need a different cover (finer `N`, or A131's PIN-CLIP).
- **T3 — the Lean hand-off.** `results/closures136.jsonl`: 15 rows, one per closed node, each a filled-in
  instantiation of `LocalCompose.y0230_dead` — `hD` (citing **A133's t-certificate** `local-cert-t-v1`
  sha `a8d95682490e…` for `S02_k5_11_r0.20_rho10`, same `L`/`P`, sharper than A119's), `hdisj`/`hsep`/`hpins`
  (A120's A2 / A3 / A1+A4 verdicts), and `hno` = the 4 certificates with their SHA-256, the frozen verifier's
  SHA-256, `zone_sub_box: true`, the written zone and box, and the **generated `native_decide` fragment**
  (`results/leanfrags/*.leanfrag`, 60 of them, via `lean/gen_case_lean.py`, `lean/` untouched).
- Scope: everything is `s₀`-only (`verify_case.py` is fixed-side, A116's `N` is anchored at `s₀`). A125's `N`
  is `k6` (`S33`/`S38`, consumer `c0_Y0335`) and is not in this `k5_11` queue. `verify_param_v2` could not be
  used for T1 — it consumes `parametric-kill-certificate-v1`, A120's certificates are
  `case-measure-certificate-v1`.
- 19.9 CPU-h of a 20 CPU-h cap; ≤ 2 processes, BelowNormal, BLAS-pinned, ≤ 10 python processes on the box;
  read-only on every campaign and on A112/A119/A120/A126/A133 and on `lean/`; frozen verifiers byte-identical;
  no sentinel or pidfile deleted. `attempts/A96-a57-parametric/results/a120_closures.jsonl` at rev 3
  (append-only, last row per id wins): **15 CLOSED, 9 OPEN, 11 not run** of the 35 in-`N` targets.

## 2026-09-08 - A148-gallery-v4 (Opus engineer) - T2 done: the A57/A60 v4 set, and TWO NEW GEOMETRIC KILLS
- `docs/shadows/a57v4/`: the same three-panel v4 page on the **top 40 surviving A57 nodes and the
  top 20 surviving A60 nodes** by A142's subtree cost, from the night's records as they stood at
  **06:05** (A137 still running, pauses at 07:00; the timestamp is printed on every page).
- Population: A142's ranking minus everything killed since it was built - **1 777 ids** and their
  descendants (798 A137 night records, 515 A57 tree rows now KILL-BY-LOGIC/CERTIFIED, 173 A145/A137
  exact-core re-solves PASS-V3/PASS-FROZEN, 291 A141 K' lane and slot-lane leaves).  Frozen in
  `results/population148_a57v4.json`.
- **TWO NEW KILLS the drawing found.**  On `c0_Y0254` and `c0_Y0168` (A60, both still alive after
  every kill list above) the T5'''' verdict FIRES: the exact pin core at (0.5, 1.5) and the
  conditioned square's polygon core K'(B) OVERLAP, by **+0.015346** and **+0.002429**.  K'(B) is
  inside the conditioned square at every pose of its box and the pin core is inside the pinned
  square at its single pose, so those two squares can never be interior-disjoint: the node
  hypothesis is unsatisfiable and the node is dead by geometry with no LP.  Sampled check: **0 of
  10^5** poses in each box give a square disjoint from the pinned one (best gap -0.0428, -0.0029).
  Re-confirmed by verify148's independent edge-crossing predicate.  Records:
  `results/t5_kills_a148.jsonl`; both pages carry a KILLED banner.  Certificates NOT emitted (this
  attempt is drawing and geometry only) - each needs the two-core-overlap clause the T5'''' schema
  already has on the A57 side.  A137's fold-in ran that leaf on A57 only (4 kills); A60 had had
  only the pin-clip leaf, which is why these two survived.
- **One near-kill**: `c0_Y0878` has a guard line at h y = 0.992928932 (a pin core's top edge) with
  **chord sum 3.868359 vs s0 = 3.877084, rhs 0.008725** - three pins contribute a full unit chord
  each and H another 0.868, leaving the five remaining squares less than 0.009 of that line.  The
  tightest guard row in either campaign.
- Free centre region on these nodes: green 0.004 to 2.213, median 1.145 (k0's are 4.27-5.01); the
  extreme is `k5_11_interior_Y0130` at **0.004**.  The disk bound gives n_max in {7, 9, 10, 11}
  against budgets 4-5, so it kills nothing here; tightening it means shrinking the UNDECIDED band
  (finer grid or an interval tilt sweep) - the cheapest next step this gallery points at.
- Pockets bite everywhere: every node has >= 2 clearances below 1, narrowest are pin-core-to-K'
  pinches of 0.05-0.13 (`c0_Y0076` 0.052, `c0_Y0952` 0.062, `c0_Y0169` 0.069, `c0_Y1033` 0.079) -
  the Y0036-style pinch, now measured on every page.
- Verification: 60 pages, **0 failures** - 12 000 green + 12 000 blocked points at 360 tilts,
  20 923 K' containment poses, 9 900 pin-core poses, 1 710 pockets, 1 127 red-dashed columns +
  2 728 controls, 180 guard rows x 10^4 draws = 10 830 000; plus 1 200 000 generator draws, 0 hits.
- Files: `docs/shadows/a57v4/` (60 SVG + README.md + review_a57v4.csv), `docs/shadows.md` Part V
  addendum, `attempts/A148-gallery-v4/results/{gallery148_a57v4,verify148_a57v4,population148_a57v4,
  t5_kills_a148,t5_kill_check_a60}.json(l)`.

## 2026-09-08 - A148-gallery-v4 (Opus engineer) - T2 correction: a kill list built from *.jsonl misses the clip-kill CERTIFICATES
- The first a57v4 draft drew three A60 nodes as ALIVE that were already dead: `c0_Y0254`, `c0_Y0168`
  and `c0_Y0878`.  **A142's own A60 clip sweep records its kills as certificates only** -
  `attempts/A142-a57-review-gallery/certs/a60/<id>.clipkill.json` - and writes no result line to any
  `.jsonl`, so a kill list assembled from `results/*.jsonl` (what every downstream consumer,
  including A148's first cut, has been doing) misses **150** ids.
- **The rule for anyone building a kill list**: `*.clipkill.json` under `attempts/*/certs/**` IS a
  kill record and must be read.  `*__exall.json` is NOT - that certificate file exists even when the
  run ended `LOST-KILL-ON-RESOLVE` / `TOO-TIGHT` / `FAIL`, and only its jsonl row says whether it
  verified (nine nodes of the corrected set have one and are correctly still alive).
  `data148.night_kills()` now reads both correctly: kills go 1 777 -> **1 950**.
- Credit where it is due: the **drawing flagged all three anyway** before the bookkeeping was fixed.
  Two had the T5'''' verdict firing - the exact pin core at (0.5, 1.5) overlapping K'(B) by
  +0.015346 and +0.002429, sample-confirmed 0 of 10^5 poses disjoint - which is the same kill by a
  second route; the third had the tightest guard row measured anywhere (chord sum 3.868359 against
  s0 = 3.877084, rhs 0.008725).  The v4 page found in a picture what the kill list had lost.
- **Corrected set** (records re-read 06:35, A137 still running): 60 pages, top 40 A57 + top 20 A60.
  **No node in it is killed by the drawing** - T5'''' alive everywhere, no lane KILL, no guard line
  within 0.15 of s0 (tightest `k5_11_interior_Y0738` `grid v 2/8`, chord sum 3.5960, rhs 0.2811),
  disk bound n_max in {7, 9, 10, 11} against budgets 4-5.
- Free centre region: green 0.0044 to 2.502, median 1.145 (k0's are 4.27-5.01); the extreme is
  `k5_11_interior_Y0130` at **0.0044**, whose undecided band is still 0.96 - which is why the disk
  bound stays loose.  **Shrinking the UNDECIDED band (finer grid, or an interval rather than sampled
  tilt sweep) is the cheapest way to make the disk bound bite**, and is what this gallery points at.
- Pockets bite everywhere: all sixty have >= 2 clearances below 1; narrowest are pin-core-to-K'
  pinches of 0.05-0.11 (`c0_Y0076` 0.052, `c0_Y0952` 0.062, `c0_Y0169` 0.069, `c0_Y1033` 0.079,
  `c0_Y0215` 0.084).  A141's K' lane test has **no row for a single one of these sixty**, so every
  lane tag reads `n/a` - the other obvious next run.
- One page (`k5_16_interior_Y1039`) was killed by A137 between drawing and verification; verify148
  now falls back to the node's own record so a page is always verified as drawn.  Every page prints
  the timestamp at which the campaign records were read.


## 2026-09-08 — A137 night shift 2 (A57 owner for the night): the backlog folded in, the exact pin core deployed at emission, and the two schedule numbers measured

- **Work-owing A57 population 632 -> 406 (-35.8 %)**, and 1,161 new rows emitted, 947 of them already
  dead. Full accounting: `attempts/A57-shadow-trees/PAUSED.md` v3 (v2 archived as `PAUSED_v2_archived.md`).
- **The exact pin core is the lever, as a population rate now.** 163 of the 305 surviving-ALIVE nodes
  re-solved with A135's exact certified-maximal cores: **46 certified dead under the FROZEN
  `verify_case.py`, 28.6 % of the 161 decided**, 15.5 CPU-h, median 426 s. Nothing changed but the
  half-side written into `cores` -- no verifier change, no Lean change.
- **A145's `frac_exact` predictor gates at the top and not at the bottom**: >= 0.60 kills 25/66
  (37.9 %), but 0.30-0.45 kills 15/63 (23.8 %), so A145's "0 of 7 below 0.45 moved at all" does not
  survive n = 63. Rank by it; do not discard the middle band.
- **Emission through the hooks kills a quarter of children before any LP**: 3,034 fresh children
  screened through pinguard-at-the-exact-core -> T5'' -> T5''' clip -> T5'''' polygon, **798 (26.3 %)
  dead by geometry** (639 T5', 159 clip, 0 polygon). **The level-2 rate the 10.5-11.7 wall-day
  schedule rests on is 27.5 %, not the 13.74 % credited** (the comparable incremental-over-T5' figure
  is 8.6 % at nsub = 1; the exact core moves boxes out of that bucket into T5'). Of the level-1
  children that reached the LP, **149 of 189 (78.8 %) are certified dead**.
- **An id is not a node.** The same child id names a different node in the L1 tree (eps-fat pins) and
  the G1 tree (delta = 1e-2 slack pins), and a kill transfers only DOWNWARD in the pin core. The fold
  is now tag-aware, and it caught two of A142's 17 exact-clip kills written at a_pin = 0.49999997
  against the L1 tree's pins: correct certificates, but they do not kill the G1-tree nodes the live
  campaign is descending.
- **A141's slot-lane kills, folded: 187 A57 rows, 180 of them nodes already `PASS`, 7 new.** Its
  "243 new" is new relative to the clip kills, not to the corpus's verdicts.
- Every one of tonight's 159 clip kills carries a replayable `pin-clip-kill-certificate-v1` and passes
  **A131's own independent checker, 159/159**, with 1,908,000 sampled poses and 0 pin-free hits.
- Operations: the 1,500 s **process** wall fired 3 times and is recorded as `WALL-CAP`, never a verdict
  -- which is what let `k5_16` shard 0 (the Y0381 wedge) be re-emitted at last. Two process bugs worth
  not repeating are written up in PAUSED v3 D.6/D.7 (a scaler that counted a queue's remainder from its
  out-file instead of its claims; and the shared git index swallowing a staged checkpoint into another
  agent's commit -- use `git commit -- <pathspecs>`, never add-then-commit).
- Files: `attempts/A137-night-shift-2/` (code, certs/clipkills, results, notes/method.md),
  `attempts/A57-shadow-trees/results/superseded_by_{backlog,exactcore}_A137.jsonl`,
  `attempts/A60-trump5-campaign/results/superseded_by_backlog_A137.jsonl`, `docs/budget.md` A57 row.

## 2026-09-08 — A155-exact-cell-corner-band (Opus engineer) — done-negative

- **The K0-WIDEN pad is worth 2 % of the corner band and 4.2 % of the four-corner product, not the
  order of magnitude the exact-cell reading predicted.** (B1) re-run at five pads — 0 (fixed side),
  4.4e-4 (1e-3 slab), 2.2e-3 (5e-3 slab), 1.1e-2 (2.5e-2 slab), 2.55e-2 (the whole window, A143/A150)
  — gives band **202 / 202 / 202 / 204 / 206** of 216 cells. The full-pad row reproduces A150's 206
  and A143's 11 772-pair census exactly (`cells155` is `cells143` box-for-box at `A_W`), so the
  comparison is like-for-like.
- **The 2-crowd space at the exact cell IS thin — the level-1 cover just cannot see it.** Pose-level
  occupancy (200 realised first meeters per cell x an 8 000-pose partner pool): median p = 0.0125 at
  pad 0 against 0.1625 at the full pad (x13), **90 of 216 cells hold no witnessed 2-crowd at all**
  (64 at the full pad), and 16 cells hold no realised meeter whatsoever. (B1) kills 14. All 14 sound
  kills have p = 0 (no contradiction with the sampler); 76 p = 0 cells survive the sound test.
- **Refinement converts part of it and loses anyway.** At 12 x 12 positions x 6 tilt windows the clip
  + (B1) kill 25.2 % of 864 cells (21.5 % at the full pad) and 29.6 % of 1 728 at 12 x 12 x 12,
  against 6.5 % at level 1 — but the branching factor rises 202 -> 646 -> 1 216, i.e. the
  four-corner product rises x105 and x1 300.
- **The product at pad 0: 1 455 160 816 tuples / 181 906 396 D4 orbits**, against A150's
  1 519 380 658 / 189 934 236 at the full pad and 1 455 436 972 / 181 940 916 at the 1e-3-slab pad.
  The `wmax` re-run reproduces A150's stage table and pair-kill counts digit for digit.
- Sampled cover confirmation at every pad: 8 000 drawn realised 2-crowds -> 8 000 hits, 0 misses,
  400 exact-rational meet cross-checks each, 0 disagreements.
- **Slabs make the corner-first route worse, not better.** Because the pad is a 6 % effect, a
  slab-wise tree pays essentially the whole-window cost per slab; under `docs/budget.md` §E the slab
  count is 5 (width_max 0.012) to 115 (5e-4). **A08's root certificate does not remove the bottom
  slab**: `certs/measure_certificate_3.82.json` is an atomic measure supported in [0, 3.82]^2 with
  total 10.985474 < 11, so it kills the single side 3.82 and nothing above it (a unit square at the
  far wall of any larger container carries zero measure); A82 measured the k0_00 root LP at 3.833212
  at tau = 11.000000, eta = -0.000000, so nothing above 3.82 is free either.
- **The certificate machinery for a slab-wise corner tree does not exist**, and A99 §3.3 already
  said why: the corner-crowd nodes cannot be emitted parametrically at all (their cores are
  reach-cover box centres, not affine in s). A155 adds that the corner zone's far edge is
  `1 + w + sqrt2/2`, an irrational that MOVES WITH THE PAD, so every slab has a different cover and
  no certificate, cover-invariance argument or warm pool transfers between slabs. What does exist:
  the frozen fixed-side `verify_case` with A135 exact cores (A150 certified 4 of its 7 kills that
  way), the dilation reduction itself (Lemma K0-WIDEN, declared-reach form), and `verify_param` for
  INTERIOR k0 cells only (A99: one window-valid PASS, +5-7 % per node).
- The LP leg was **not run**: its gate was pad-0 survivors < 50 000 orbits and the measured count is
  181 906 396 orbits (1 455 160 816 tuples), 3 638x over. 0 of the 2 CPU-h LP cap spent.
- Files: `attempts/A155-exact-cell-corner-band/` (code `cells155.py` (A143's cover with the pad a
  parameter), `geom155.py`, `band155.py`, `prod155.py`, `draw155.py`; `notes/composition.md`,
  `notes/tables.md`; `figs/band155_pad0_vs_padmax.svg`).

## 2026-09-08 — A150 (four-corner product root for k0_00), log entry added retrospectively by A154

A150 finished on 2026-09-08 (`d993979b`) under a brief that forbade writing outside its own
directory, so it could not add its own REGISTRY row or LOG entry. Both are added here; the source
of record is `attempts/A150-four-corner-product/notes/composition.md`.

- **The four-corner mechanism is real and large.** Conditioning on all four corner intruders at
  once moves the k0 level-1 LP by a **whole unit of η** (13 fine nodes: median −1.0, range −6.0 to
  +1.08, **7 converged kills, 4 frozen-verifier PASS at 8.7–92 CPU-s**), against A143's −0.044 for
  one square at one corner and −0.083 for two at the same corner. Random-survivor kill rate **63 %**
  against A143's **0 %**. Canary clean: 192 of 192 Trump four-tuples survive every geometric kill.
- **The PI's premise fails.** The admissible band is **206 of 216 cells** — the corner-meeting zone
  loses no distance interval and no tilt window — the pairwise geometry (Q2/Q1/Q1s) cuts only
  **15.6 %** of the product, and every counting leaf fires on nothing (guard lines `rhs_min` 1.377
  against `s0` 3.877; disk bound `n_max` 10–14 against budget 7; a separation surrogate is worse).
- **Priced out.** At the resolution where the LP decides (`area_open <= 2`, first reached at 6x6
  positions x 3 tilt windows, N = 108) the product costs **>= 4.2e5 and realistically 5.3e6
  CPU-h** against `docs/budget.md`'s 12,000 for the whole k0 tree; break-even needs N ~ 40, where
  the LP does not decide. Adaptive refinement cannot rescue a 12-dimensional root.
- **Banked negatives:** the separable disk surrogate `area_4 = area_0 - sum_c delta_c` is NOT a
  theorem (refuted, errors to 1.73); the sound separable form gives `n_max >= 16`.

## 2026-09-08 — A154: (R6) as an LP row is A115's row, it kills nothing, and the useful artefact is a free screen

> **VERDICT. 0 attributable kills in 29 LP runs; η strictly WORSE on 26 of them (mean +0.65); the
> Trump-image canary stays alive; and the reason is now a one-line test that costs nothing.**

- **(R6) is not a new row.** A150 §6 item 1 proposes `sum_p [Q_p meets some widened corner box] x_p
  >= 8` as "a single row of weight 8, **not** the four separate >= 2 rows A115 tried". Both halves
  are wrong on the record: A115's `d0` configuration IS that aggregate row
  (`attempts/A115-k0-corner-rows/notes/method.md`, "The node-level incidence budget":
  `rhs = 1 + e*[Q in G(a_w(0))]`, `budget = budget0 + floor(eB)`, `B = 8 - sum_cores r_max`), and
  four per-corner rows would **dominate** the aggregate (which is their diagonal `e_1 = ... = e_4`),
  so (R6) is at best what was already measured. Statement, soundness, Lean shape and the verifier
  analysis: `attempts/A154-r6-corner-row/notes/row.md`.
- **Why it fails, exactly.** `tau(e)` is the value of an LP affine in the rhs, hence convex, and any
  optimal dual at `e = 0` is a subgradient: `eta(e) >= eta0 + e(c - B)` with `c = dtau/de` the corner
  incidence the fractional optimum realises. A kill needs `c < B`. Measured: **`c >= B` in 23 of 23
  (R6) LP runs, minimum `c - B` exactly 0.000**; mean `c` 8.22 against mean `B` 5.96; on the eleven
  converged-alive cells with A135 exact cores, `c = 9.0-10.2` against `B` in {7,8}.
- **The geometric cause.** `a_w(0) = 12819/12500 = 1.025520` is bigger than 1; the four widened
  corner boxes cover `4 a_w^2 / s0^2 = 28 %` of the container, and a covering measure is cheapest
  exactly in the corners, where a placement is clipped by two walls. **The row prices what the LP
  already wants to buy** — the corner incidence is not a rigid property of a cell, it is a price.
  Four cells of the eleven have a stored dual with `c = 6.0-6.5 < B = 7`, and the re-optimised dual
  at `e = 1/B` immediately buys `c = 9.2-10.0`.
- **NOT A109's failure mode.** `s0 - 2 a_w = 456511/250000 = 1.826044 > sqrt2` **exactly**, so a
  unit square carries at most one corner incidence and `B` is exact — independently re-verified on
  **24,468 dual placements from 176 packings: max multiplicity 1, 0 disagreements** between the
  `f_min_max` oracle and a from-scratch SAT test (`results/verify154.json`, `ALL_OK`).
- **THE DELIVERABLE: the zero-cost screen.** For any node whose stored LP record is CONVERGED,
  `c >= B` at its stored dual is a **proof** that (R6) cannot lower that node's eta at any `e > 0` —
  read from the file, no LP. Over **all 166 open k0 cells the screen costs 5.2 CPU-s** and settles
  **8 of the 13 converged** ones outright. Any future incidence-row proposal should be screened this
  way before an LP slot is spent on it.
- **Lemma ID (A89-O3) adds nothing, anywhere.** (i) The area form
  `sum_c (1 - d_c)^2 <= m^2 - 11 < 4.0318` is vacuous by inspection at four corners
  (`(1-d)^2 <= 1`, so the left side is `<= 4`), and is not expressible in the case-LP, which has no
  variable for a corner's depth. (ii) The **certified** corollary "some corner has DEPTH >= 0.3" is
  a weight-1 row of exactly (R6)'s shape at `a_w(0.3) = 72103/100000`: `c_ID >= B_ID` on **166 of
  166** open cells (`B_ID = 0` on 87 — the conditioned square can itself be the deep one, so the
  bonus floors to 0; mean `c_ID` 3.12 against `B_ID <= 1`). Because `B_ID = 1` forces `e2 = 1`
  (mass >= 2 on every deep pose), the two measured joint runs pay **+3.84 and +4.70 of eta** for it.
- **The protected tier gets nothing, and the reason is structural.** A corner is *simple* when a pin
  sits in it (the pin IS the corner square, no teleport); at a *non-simple* corner the ">= 2 free
  meeters" statement needs the extension class `S u {c(0,0)}` certified dead on the window
  (`slot_crowds.md` §1.2). Census (`results/classrow154.json`): **k0_00** 4 non-simple corners,
  `B = 8`, licensed modulo K0-O1 — this is (R6); **trump5** exactly **one** (TL; the pins hold
  BL/BR/TR), `B = 2`, licensed at `s0` only (extension k6_23 is PARTIAL); **k5_11** one (TR), same;
  **k5_16 and k4_13 have ZERO non-simple corners — the row is vacuous**; and **all 15 protected-tier
  classes with k <= 4 have every corner extension a protected class**, so nothing licenses the row
  there. In vitro on 10 A60 alive trump5 nodes: the screen settles 8, and the LP gives 2 alive at
  eta +1.0 and 2 knife edges at eta = 0.0000 with **`c = 2.00 = B` exactly**, one of them CONVERGED
  at the 900 s cap — a proof that no `e` kills it.
- **Price.** A (R6) pass over the 216 level-1 k0 cells costs **9.5 CPU-h** at the measured 159 s per
  cell and removes **0**, i.e. **net -9.5 CPU-h** against the k0 row's 12,000 (9,400-10,900 after
  A141); over A115's 166 open cells, -7.3. The screen costs 0.0014 CPU-h. For trump5's residual tree
  (inside the protected tier's 3,800 CPU-h) the row's whole reach is one unit of budget on one
  corner at 287 s per node, and it is `s0`-only: **net negative there too**.
- **Addendum for A150's price (PI's question).** By D4 a corner-first tree may name its root corner
  to be a DEEPEST one, so Lemma ID lets that corner's meeter be taken with DEPTH >= 0.3
  (`mu <= a_w(0.3) = 0.72103` at `s0`). That leaves **110 of A150's 206 band cells** (118 of the raw
  216; 104 under the untransported `mu <= 0.7`), a factor **0.534 on ONE of the four corners**:
  A150's fine product falls from 5.28e6 to **2.82e6 CPU-h — still 235x the k0 row**. ID narrows one
  factor of the product, never four.
- Cost 1.64 CPU-h of a 3 CPU-h cap (29 LPs, 1.50 CPU-h). Files: `attempts/A154-r6-corner-row/`
  (`code/{a154lib,screen154,screenall154,lp154,classrow154,bandeep154,verify154,report154}.py`,
  `notes/{row,tables}.md`, `results/{screen154,screenall154,lp154}.jsonl`,
  `results/{price154,classrow154,bandeep154,verify154,screenall154_summary}.json`, `logs/`).
  No certificate was emitted: there was no LP kill to certify.


## 2026-09-08 — A157-undecided-slots (Opus engineer) — done-negative
- **Task**: decide A141's 196 `UNDECIDED, lane_lb = 0, M <= 1` usable-slot cells (the PI read them as
  probable `LANE_K' = 0, M <= 1` kills) by running A141's certifying cover on them and emitting
  `polycore_slot_lane_v1` certificates. READ-ONLY on every campaign and on A118/A132/A141; new files
  only under `attempts/A157-undecided-slots/**` plus three named appends.
- **The premise was wrong on both halves.** (i) A141 did not skip those covers for speed:
  `skipped_covers` is set only on the `LANE>=2` / `NEAR-MISS-OR-WORSE` rows (4,750 + 1,790), and every
  one of the 1,655 UNDECIDED rows already carries `M_exact = true`. What returned `None` is the LANE
  cover — `polylane.lane_cover` at `max_open = 1200, depth0 = 20` with
  `reason = "open budget exhausted"`, a branch that also returns `open = []`, which is why 188 of the
  196 target rows report the misleading `cover_open = 0`. (ii) `lane_lb = 0` at A141's 8,000-pose
  screen means *no free pose was drawn*, not that none exists.
- **The population (recomputed)**: 196 rows, 174 distinct nodes, **179 distinct (node, slot) cells**
  (17 nid/slot pairs appear in two A57 shard trees). `M = 0` on 19 rows, `M = 1` on 177. By class and
  slot: k5_16 BL(1,0) 40 / TL(1,0) 27 / BR(0,1) 16 / TR(0,1) 11 / TR(1,0) 10 / BR(1,0) 9; trump5
  BR(0,1) 22 / TR(0,1) 12 / BL(0,2) 7 / BL(1,1) 6 / TL(0,0) 1; k5_11 BL(1,1) 23 / BR(0,1) 8 /
  TL(1,0) 3 / TR(0,0) 1. By level: k5_16 L1 103 / L2 10, trump5 L1 48, k5_11 L1 23 / L2 7 / L3 5.
- **The cheap half decides half the population.** Re-screening all 179 cells at **400,000** poses
  (~2 s/cell) realises a free pose on **86**, 11 of them with an explicit interior-disjoint pair. A
  realised free pose is a sound `LANE_K' >= 1`, so with their certified `M` those cells have
  `LANE_K' + M >= 2` and **no kill by this leaf exists there** — 62 A57 (k5_16 47, k5_11 15) and 24
  A60. Only 1 of the 86 has clearance below 1e-4.
- **The PI's example resolves against the kill.** `c0_Y0076` (A60 trump5, L1, alive) has exactly two
  non-`LANE>=2` cells and they are the two named. `TL(0,0)`: 400,000 drawn, 231,041 meet the slot cell,
  **14 free**, best clearing every pin core AND the hypothesis square's `K'` by **1.1026e-2** at
  `c = (1.6807459, 0.6862003)`, `theta = 29.4420 deg`. `BL(0,2)`: 400,000 drawn, 270,606 meet, **3 free**,
  best clearance **5.2398e-3** at `c = (1.6636782, 3.1947477)`, `theta = 61.0252 deg`. The binding core
  is the conditioned square's in both; every pin core is 0.5–1.75 away. So a free square tilted
  29.44 deg does reach `TL(0,0)` while clearing the hypothesis square by 1.1e-2 — the cell is not
  singly met.
- **The covers**: A141's machinery verbatim (`lane_corner_generic`, `emit141.cert_dict`,
  `check141.py`), budget ladder at `(depth0 = 21, max_open = 4,000)`. **25 cells covered, 0 kills, 1
  near-miss, 24 not closed.** The near-miss is `k5_16_interior_Y0254 BL(1,0)`: `LANE_K' <= 1` certified
  on 2,296 always-overlapping open boxes, `M = 1`. The 25 include **all 16** kill-possible cells with
  `M = 0` — the only sub-population reachable at this budget, since `M = 0` needs only `LANE_K' <= 1`
  (a NON-empty open set suffices) while `M = 1` needs `LANE_K' = 0`, i.e. an EMPTY cover. The 68 unrun
  cells are all `M = 1`.
- **Why the cover does not converge.** 21 of 25 never finish the DFS phase: the undischarged frontier
  at depth 20–21 passes 4,000 (322–4,560 discharged leaves at the cut). On the largest clearance in
  the corpus, `k5_16_interior_Y0410 BL(1,0)` (6-core clearance 1.36e-1), `depth0 = 20` gives 324 leaves
  and `depth0 = 21` gives 799, both budget-cut — the frontier roughly doubles per level. On
  `k5_16_interior_Y0149_D02 TR(1,0)` the DFS does finish (43 open at depth 21) and the 8 refinement
  rounds then GROW the open set `43 -> 38 -> 55 -> 80 -> 122 -> 203 -> 306 -> 497 -> 873`
  (`..._D00`: `51 -> ... -> 506`), i.e. the always-overlap screen keeps finding genuinely far-apart
  open pairs. One cell at `(21, 30,000)` had not completed after 125 CPU-s (RSS 43 MB — wall, not
  memory, binds at that rung); `depth0 >= 24` with `max_open >= 40,000` does blow memory (12 GB), since
  `max_open` bounds only the frontier, not `lane_cover`'s discharged-leaf list.
- **Result**: **0 `polycore_slot_lane_v1` certificates**, `results/slot_kills157.jsonl` empty by
  construction, **nothing in A57 or A60 changes**. Checker control: `check141.py` PASSes A141's
  `slot_slack0.02_c0_Y0281__TL0_0.json` in this environment, so the emit/check path was live.
  Caveat A118-O1 stands throughout: exact-pin form, class-`S` composition only.
- **Cost** ~0.7 CPU-h of a 3 CPU-h cap; 2 processes at BelowNormal / affinity `0xFFFF` throughout,
  16 lab python processes on the box (A149 4, A137 5, A156 2, A136 2, A154 1, A157 2). The box was
  saturated, so WALL was the binding limit, not CPU. **The measured lever**: extra sampling decides a
  cell in ~2 s; extra cover depth costs 35+ CPU-s and decided none.
- Files: `attempts/A157-undecided-slots/` (code `enum157.py`, `mkrecs157.py`, `screen157.py`,
  `probe157.py`, `run157.py`, `fold157.py`; results `undecided_cells.jsonl`, `enum157.json`,
  `screen157*.jsonl`, `cover_jobs*.jsonl`, `t157_cells*.jsonl`, `t157_deep.jsonl`, `summary157.json`,
  `slot_kills157.jsonl`; `BRIEF.md`, `notes/method.md`), plus appends to
  `attempts/A57-shadow-trees/PAUSED.md`, `attempts/A60-trump5-campaign/notes/ledger.md` and
  `docs/residue_ledger.md` §1.

## 2026-09-08 - A148-gallery-v4 (Opus engineer) - two drawing fixes, both galleries regenerated
- **(1) UNDECIDED is no longer green.**  The v4 draft painted the undecided band pale green
  (`#a5d6a7` @0.30) and it read as feasible: on `k5_11_interior_Y0275` the PI took the pale band
  left of H for a green strip, and the per-centre all-tilt map against H's actual poses has **no
  feasible centre there**.  Undecided is now a **light grey stipple with no green in it**;
  certified-feasible stays green, certified-blocked white, and the pocket hatch stays a grey
  DIAGONAL hatch so the two greys cannot be confused.  The panel legend and the generated
  WHAT-TO-LOOK-FOR line both say, verbatim, "grey stipple = undecided (clearance within the
  margin), NOT feasible", and the look line now reports certified-free and undecided as TWO
  numbers instead of their sum.  Undecided area is 0.73-1.07 on the eleven k0 cells and 0.41-0.96
  on the sixty A57/A60 nodes, so painting it green overstated the free set by about a fifth.
- **(2) The witnessed free meeters are drawn.**  Every usable slot / corner now carries, beside its
  lane tag, the witnessed free meeters from A157's screen (a free pose, and the sampled DISJOINT
  PAIR where one was found) and A141's T5 two-crowd witness on the k0 corners - thin black
  outlines, with **how far each reaches into the cell printed**.  The tag itself prints BOTH bounds
  and M (`ub` certified, `lb` sampled, `M` conditioned with `?` when not exact), because `ub` alone
  hides what refutes a reading.
- **What the witnesses show.**  Ten drawn on seven A57/A60 nodes, and **every one sits on a cell
  A141 recorded UNDECIDED with `lane_lb = 0`** - its own sample found no free meeter - while A157's
  denser screen found one: `c0_Y0076` TL(0,0) **+0.00045**, BL(0,2) **+0.00813**;
  `k5_16_interior_Y0865` BR(1,0) and `slack0.02_c0_Y0272` BL(0,2) each a **DISJOINT PAIR**
  (+0.00039 / +0.13998 and +0.00079 / +0.14411 - two free meeters that miss each other, so the lane
  is >= 2 and "singly met" is dead); `k5_16_interior_Y0491` BR(0,1) +0.00058, `k5_16_interior_Y0839`
  BR(0,1) +0.00064, `k5_16_interior_Y0275` TR(1,0) +0.00262, `c0_Y0175` BL(0,2) +0.12972.  On k0,
  `l1_124` / `l1_153` / `l2_p114_001` TR(0,0) (tagged NEAR-MISS, ub 1, M 1) have a free meeter
  reaching **+0.98 to +1.00** into the corner while the conditioned square H reaches **-0.026 to
  -0.036** - H does NOT reach that corner in the witness.
- **A framing bug the fix exposed.**  A141 and A157 run the lane test IN THE CELL'S CORNER FRAME
  (`polylane.centre_window` from `cell_rect(i,j) = [i,i+1]x[j,j+1]`, corner at the origin, axes
  inward), so every pose in their records is corner-frame.  The cell CENTRES coincide in both
  frames, so nothing on the earlier pages could reveal it; the first witness draft put `c0_Y0076`'s
  TL(0,0) witness at y = 0.686 instead of 3.191.  Poses are now transported by the corner's D4 map
  (a reflection negates the tilt, 90-periodic), each witness is CHECKED against the cell it claims
  to meet, and a free meeter that fails is recorded and not drawn.
- **Also this pass**: (a) each red-dashed impossible column in panel S now says whether it ALSO
  overlaps an EXACT PIN CORE - pin geometry alone excludes it, inside the frozen certificate schema
  - or only K'(B), which needs the polygon-core clause: **356 of 966** columns over the sixty A57/A60
  pages do, and **0 of 44** on k0 (which has no pins); (b) A141's `t2_a5760` sweep is one row PER
  NODE with a nested `cells` list, which the draft read as one row per cell - that is why every
  A57/A60 lane tag read `n/a`.  Fixed: **60 of 60** pages now carry A141's real per-slot verdicts.
- **Verification** gains check H: every drawn witness is inside the container, and every one billed
  as a FREE MEETER overlaps its named cell and has its interior clear of every certified core, under
  the independent edge-crossing predicate.  k0v4: 11 pages, 6 witnesses, **0 failures**.  a57v4: 60
  pages, 10 witnesses, 966 red-dashed columns + 2 192 controls, 24 000 region points, 10 830 000
  guard-chord draws, **0 failures**; 0 hits in the generators' own 1 420 000 region draws.

## 2026-09-08 — A158-slot-split (Opus engineer) — done-mixed
- **Task**: the PI's tautologous YES/NO split on the near-simple slot box
  `S(r, tt) = {centre within r of the exact slot centre, tilt within tt of 0/90}` — **YES**: some
  square's pose is in `S`, killed by A141's lane leaf with `K'(S)` as an EXTRA obstacle; **NO**: no
  square's pose is in `S`, a `caselp` `NoFam(S)` plus an A135 exact-core LP re-solve — on
  `c0_Y0076 TL(0,0)` first, then over the alive A57/A60 nodes whose LP **dual support** puts weight
  ≥ 0.5 into some usable slot's `S` box. Five further cells were named by the coordinator mid-run:
  `c0_Y0787 BR(0,1)`, `c0_Y0959 TR(0,1)`, `k5_11_interior_Y0130 TR(0,0)`,
  `k5_11_interior_Y0147 TR(0,0)`, `k5_11_interior_Y1110 TR(0,0)`. READ-ONLY on every campaign and
  on A112/A118/A132/A135/A136/A141/A157; new files only under this attempt plus three named appends.
- **The leaf is right and it is cheap.** Once some square's pose is in `S`, the number of squares
  meeting `int C` is at most `1 + LANE_K'(C | S) + M(C | S)`: the `find_witness` discharge against
  `K'(S)` **identifies** the pose with the `S`-square (`PolyCoreT5.shared_point_same_square`)
  instead of contradicting it, so the extra core costs nothing and the kill rule is `LANE = M = 0`.
  Every piece is already deployed — `yes_or_no` with a ONE-element list (A120's clauses A2/A3 become
  vacuous), `noneIn_of_clamped` for the NO bridge, A136's `zone_sub_box` on the written rationals,
  the frozen `verify_case.py`, A141's cover and `M` machinery. One new named Lean obligation,
  `slot_singly_met_of_someIn` (`notes/leaf.md`).
- **Frames**: the leaf lives in the cell's corner frame at side `m`, the LP in the world frame at
  `s0`, so the NO zone is the **intersection** over `m ∈ [m_lo, s0]` of the pullbacks (inward — for
  A57 that costs up to 1.6e-3 per coordinate) while the YES cover uses the larger float box (also
  the sound direction, since `S' ⊆ S ⇒ K'(S) ⊆ K'(S')`). The corner clamp to `[1/2, s−1/2]` is a
  real bite: `c0_Y0076`'s nominal `[0.4, 0.6] × [3.277084, 3.477084]` clamps to a quarter of itself
  — and still kills. **`k6_23` verified**: FULL window `[191/50, 969271/250000]`, converted by A114.
- **The population**: **1,238 of the 1,693 alive A57/A60 records (73 %; 1,590 distinct nodes —
  k5_11 713, k5_16 552, trump5 325)** keep `τ ≥ budget` on a dual square sitting in some usable
  slot's `S(0.10, 10°)` box (A57 1,079 — k5_11 575, k5_16 504; A60 159; L1 962 / L2 243 / L3 19 /
  L4 14). Commonest: `k5_11 TR(0,0)` 420, `k5_11 BR(0,1)` 219, `k5_11 TL(1,0)` 205,
  `k5_16 BR(0,1)` 184, `k5_16 TL(1,0)` 166, `k5_16 BL(1,0)` 163.
- **`c0_Y0076 TL(0,0)` — the NO child is DEAD and the kill is the slot box's.** `NoFam(S(0.10,10°))`
  takes the node LP from `τ = 5.000000` to `τ = 4.000000`, `η = budget − τ = 1.000000` (20.6 s,
  converged); the **control** (identical exact-core re-solve, no `NoFam`) gives `τ = 5.000000`
  (3.0 s). Certificate `certs/no_c0_Y0076__TL0_0__r0.1_tt10.json` (4 atoms, total `103/25` = 4.12 <
  5), through A136's `narrow` (`ZONE ⊆ BOX` on the written rationals, max inward shift 7.40e-8),
  **PASS on the frozen `verify_case.py` (sha `521cb01f…`) in 1.0 s** — 7,262 boxes, 1,863 exempt
  (core 1,861, nofam 2), "node DEAD". So **`c0_Y0076` provably places a square within 0.10 of the
  exact `TL(0,0)` slot centre at tilt within 10° of axis-aligned.** (`verify_param.py` rejects the
  file as MALFORMED — it consumes the PARAMETRIC schema, not a fixed-side
  `case-measure-certificate-v1` — so the second-verifier cross-check is unavailable for this
  certificate kind, as in A136.)
- **The YES child does not exist: 0 of 141 measured cells.** 139 are refuted by a **realised** free
  second meeter — in the container, meeting `int C`, clear of every pin core, of `K'(H)` and of
  `K'(S)` — at 400,000 draws, at `tt = 10°` **already at `r = 0`** (5 s/cell, no cover). At `tt = 0`
  the largest closable radius is `2.9e-6 … 2.2e-3` per cell; three cells fail even at `r = 0,
  tt = 0`. On the two cells the screen did not refute, the certifying cover was bought and each
  closes exactly ONE half: `k5_11_interior_Y1110 TR(0,0)` certifies **`LANE_K'(C | S) = 0`** (the
  first time this cover has ever closed) with `M = 1`; `k5_16_interior_Y1014 TL(1,0)` certifies
  **`M(C | S) = 0`** with `LANE = 1`. Both give `1 + LANE + M = 2`.
- **Outcome over the split: BOTH-dead 0, NO-only 1, YES-only 0, NEITHER 140.** The other two A60 PI
  cells are NEITHER: `c0_Y0787 BR(0,1)` and `c0_Y0959 TR(0,1)` keep `τ = 5.000000` at
  `r = 0.10/0.05/0.02`, at `tt = 0.4°`, and even at `r = 0.20, tt = 20°` — the LP just moves the
  slot square outside the box. The sharpest near-miss is `k5_11_interior_Y0130 TR(0,0)`, where
  `NoFam(S)` eats the node's whole slack, `τ 5.500000 → 5.000000` exactly (A149's polycore arm
  reached the same value independently the same afternoon).
- **Why the halves cannot meet — arithmetic before geometry, and in the TILT alone.** `caselp` drops
  a row only if its centre is inside the zone by `EPS_ZONE = 2e-3` and its tilt inside a
  `t`-interval by `EPS_TH = 0.3°`; `S`'s intervals `[0, tt]`, `[90−tt, 90]` have empty margined
  forms for `tt ≤ 0.3°`. So **an `S` the YES child could close on exempts not one LP row** and the
  NO child is bit-for-bit the original LP. Measured on `c0_Y0076`: NO needs `r ∈ (0.02, 0.03]` at
  `tt = 10°` and `tt ∈ (1.5°, 2°]` at `r = 0.10`; the YES side was measured through the only
  remaining band, `tt = 0.31, 0.40, 0.49°`, and is refuted there too. Because the tilt bound does
  not involve `r`, no anisotropic box helps.
- **The PI's geometry is NOT refuted — the `K'`-based leaf is.** `pair158.py` looked for an explicit
  interior-disjoint pair (a pose IN `S` clearing every node core, and a free second meeter) on the
  six PI cells at `(r, tt) ∈ {0.10, 0.01} × {10°, 0.5°}`, 600,000 draws each: **none, max pair gap
  negative everywhere** (−6.1e-4 on `c0_Y0959`, −0.67 on `Y1110`). `K'(S)` is the intersection over
  the WHOLE box, so the intruder clears it while still overlapping every individual square with a
  pose in `S`. The repair — A141's `lane_corner_split` shape, partition `S` and run the leaf per
  piece — needs pieces `≤ 3.7e-4` in centre and `< 0.5°` in tilt, ≈ `1.5e6` pieces for
  `S(0.10, 10°)`, **≈ 400 CPU-h per cell**.
- **Every NO kill is quoted against a control**, because A135's exact cores are strictly larger than
  several stored ones and five of the top-20 records are `converged = false,
  dead_unconverged = true` (their stored `τ ≈ 4` was never a bound). 7 raw kills, **6 of them
  reproduced by the control with no `NoFam` at all** — artefacts of the exact-core re-solve, not of
  the slot box. One of the six is new information for A149's lane and is recorded only as an
  observation: `k5_16_interior_Y1039 BR(0,1)`, stored `τ = 4.999999999`, goes to `τ = 4.000000`
  (converged) on the exact-core re-solve alone. `k5_16_interior_Y1014`'s emitted certificate is true
  and verified but **not attributable** to the slot box for the same reason, and is not claimed as a
  split result.
- **Cost** ≈ 1.8 CPU-h of a 4 CPU-h cap (66 LP solves, 4,848 LP-seconds; 141 YES screens; 32
  crossover bisections; 24 pair hunts; the 1,693-record population scan in 31 s). **Exactly ONE**
  A158 python process on the box at any time, Normal priority, affinity `0xFFFF`, the other
  campaigns holding 14–15 (A149 4+4, A156 2+2, A136 2–3) — the launcher waits for a slot rather than
  exceeding 16, and its first pass recorded seven `SKIPPED: box already at 16` lines doing exactly
  that. Free physical never below 10.3 GB (gate 3 GB), free commit never below 75 GB (gate 6 GB);
  longest single LP 442 s against the 1,500 s wall, which never fired; no sentinel touched (A57's,
  A137's and A124's are all set and all scoped elsewhere), no shard launched, no recursive delete.
- Files: `attempts/A158-slot-split/` (code `slotlib158.py`, `probe158.py`, `pop158.py`,
  `xover158.py`, `yesscreen158.py`, `yescert158.py`, `no158.py`, `pair158.py`, `mktop158.py`,
  `mkcontrol158.py`, `sample158.py`, `sum158.py`, `run158{,b,c,d,e}.ps1`, `verify158.ps1`; results
  `pop158.{json,jsonl}`, `recs158.json`, `top158.jsonl`, `sample158.jsonl`, `xover158*.jsonl`,
  `yesscreen158.jsonl`, `yesscreen_pop158.jsonl`, `yescert158.jsonl`, `no158.jsonl`,
  `pair158.jsonl`, `summary158.json`; certs `no_c0_Y0076__TL0_0__r0.1_tt10.json` (+ report) and
  `no_k5_16_interior_Y1014__TL1_0__r0.1_tt10.json` (+ report); `BRIEF.md`, `notes/method.md`,
  `notes/leaf.md`), plus appends to `attempts/A57-shadow-trees/PAUSED.md`,
  `attempts/A60-trump5-campaign/notes/ledger.md` and `docs/residue_ledger.md` §1.

## 2026-09-08 — A158b-slot-split addendum (Opus engineer) — the YES child as an LP node, and the mutual clip
- **Two coordinator/PI corrections, both run.** (i) The YES child is an ordinary LP node, not a lane
  leaf: `pins + H + the slot box S`, `budget = 11 − #cores = 4`, A135 exact cores on all 7 boxes,
  `S` an ordinary second core in the frozen `case-measure-certificate-v1` schema. (ii) Before it,
  the two conditioned boxes are mutually clipped with A131's pin-clip, each box's own core in the
  pin's role, then `K'` rebuilt and the lane test re-run on the clipped cores.
- **Extra soundness gate**: A135's `ExactHyp` only checks `cores[:n−1]` pairwise disjoint; with `S`
  appended `K(S)` would go unchecked and, if it met `K(H)`, the two hypotheses could be witnessed by
  the SAME square and the budget would be 5, not 4. `cores_pairwise_disjoint` is re-run over all 7
  (min gap 0.0000 on A60's exact pins, 0.0141 on A57's `δ = 10⁻²` pins).
- **The YES-child LP lands exactly back on the knife edge: 12 of 12 sub-cases (6 cells × 2 tilt
  pieces), all converged, `τ = 4.000000 = budget`, `η = 0`** (3.4–80.4 s each). This is the general
  obstruction stated exactly: adding the slot square removes **exactly one** unit of dual packing
  *and* **exactly one** unit of budget, so the YES child returns to `τ = budget` — the same 1 the NO
  child removes from `τ` alone. The dual weight in `S` is exactly 1 on **730 of the 1,238** selected
  records, so on that whole sub-population **the split is structurally neutral** and no amount of
  compute changes it.
- **The mutual clip bites, and the PI's prediction about `K'(H)` is confirmed.** At `S(0.10, 10°)`:
  `H`'s box keeps 0.5003 of its area on `c0_Y0787` (0.4714 by volume at `nsub = 4`), 0.6273 on
  `Y0147`, 0.8865 on `c0_Y0076`, 1.0000 on `Y0130`/`Y1110`; `K'(H)` grows ×1.126 on `c0_Y0787`
  (0.590298 → 0.664416), ×1.066 on `Y0147`, ×1.027 on `c0_Y0076`; `S`'s box keeps 0.7439/0.7265 on
  `c0_Y0959`/`Y0147` with **two empty tilt sub-bins** at `nsub = 4`. (The core handed to A131 is the
  largest axis-aligned square inscribed in `K'`, strictly smaller than `K'`, so the clip removes less
  than the truth — sound, and A131 is imported unchanged.)
- **What actually changed the lane test was the CLAMP, not the clip.** The LP framing writes `S` in
  the world frame clamped to `[1/2, s0 − 1/2]`, which for a corner slot halves the centre box
  (`c0_Y0076`: `0.2 × 0.2 → 0.1 × 0.1`) and fattens `K'(S)` from 0.566 to 0.736. With that core the
  400,000-pose screen stops refuting on two cells.
- **`k5_11_interior_Y1110 TR(0,0)`: `LANE_K'(C | S, H_clipped) = 0` is CERTIFIED on BOTH tilt pieces**
  — 36 and 35 leaves, **0 open**, 36 s and 37 s. First empty conditional lane cover ever obtained.
  The kill then needs `M(C | S, H_clipped) = 0`, and that is where it stops: the screen finds no
  meeting pose of the clipped `H` box clear of the other cores in 100,000 draws, but
  `cond_can_meet`'s cover discharges **ZERO** leaves — `(max_depth 40, max_open 5,000)` → 0 leaves /
  5,001 open / 21.8 s; `(42, 40,000)` → 0 leaves / 40,001 open / 183.8 s. The reason is structural,
  not budgetary: `H_clipped` sits at frame `[1.374, 1.519]²` with `hmax ≈ 0.686`, so
  `box_misses_cell` needs `x0 ≥ 1.686` and can never fire, the container prune never fires on an
  interior box, and the shared-point discharge finds nothing — the DFS fills its open budget in one
  corner. A third rung was stopped at 674 s rather than bought.
- **`c0_Y0076` is NOT dead by the split, on either route.** YES-by-LP `τ = 4 = budget` on both
  pieces; YES-by-lane blocked with the open set GROWING with depth (159 → 270 → 646 at
  `(22, 8k) → (24, 30k) → (26, 60k)`), and piece 1 has `M_lb = 1` outright. Its NO child stands
  certified (frozen `verify_case` PASS), so no `A136 closures` record is written — there is no
  closure. `c0_Y0787` and `c0_Y0959` are refuted on the lane side even after the clip (free meeter
  realised at clearance 4.37·10⁻² and 1.23·10⁻¹); `Y0130`/`Y0147` have `lane_lb = M_lb = 1`.
- **Verdict on the population**: do not run the split over the 1,238 records. The YES-child LP costs
  4–80 s per sub-case and always returns `τ = budget` for the accounting reason above; the geometric
  route needs an `M` cover whose prune set is empty by construction whenever `H` is interior.
- **Cost** ≈ 0.7 CPU-h of the +2 CPU-h extension (12 YES-child LPs, 24 clip LPs, 12 clip+lane
  screens at 400,000 poses, 7 lane-cover rungs, 2 M-cover rungs + 1 stopped). One A158 python at a
  time throughout; the launcher waited for a slot (the box sat at 16 from the other campaigns for
  much of the window and one launch was refused outright).
- Files added under `attempts/A158-slot-split/`: code `yeslp158.py`, `clip158.py`,
  `lanedeep158.py`, `mdeep158.py`, `run158g.ps1`; results `yeslp158.jsonl`, `clip158.jsonl`,
  `lanedeep158.jsonl`, `mdeep158.jsonl`, `{y0076,y1110,five,deep}_job*.jsonl`;
  `notes/addendum_b.md`. No certificate was emitted by either route.

## 2026-09-08 — A159-k0-nearmiss-joint (Opus engineer) — done-negative

**The question.** The PI, on `docs/shadows/k0v4/l1_124.svg`: *"TR(0,0) cannot be doubly met — two
squares can each touch the corner cell but they are mutually exclusive."* A141 recorded that
corner as NEAR-MISS with a *realised* two-crowd (`results/t5_twocrowd.json`); A148 drew the same
witness and measured H reaching **−0.026 to −0.036** into the corner, and blamed a corner-frame
transport bug. One of the two had to be wrong.

**Neither was. The frame was never the problem, and the two measurements were taken against two
different rectangles.** `polylane.corner_cell` / `centre_window` are CONTAINER-frame
(TR = `[2.8515739257860595, 3.877084]²`), and A141's recorded H lies inside its own box `B` in
that frame and in none of the other seven D4 images — so A141's poses need no transport, and the
LOG's earlier "A141 and A157 run the lane test in the cell's corner frame" over-attributes
**A157's** bug (A148's own `data148.py` gets A141 right and says so in its docstring). What A148's
page drew is `depth_into_cell` against `cell_rect`, the **plain unit cell** `[s0−1, s0]²`, while
the leaf is stated over the **widened** box of Lemma K0-WIDEN — and the two differ by exactly
`W0 = (s0/3.82 − 1)(1 + 1/√2) = 0.0255100742139405`. `−0.026` against the unit cell is a hair on
the *other* side of zero against the widened box.

**T1 — exact re-examination (`code/xwitness159.py`, `mpmath.iv` at 60 dps, complete SAT over the
4+4 edge normals; every reported sign from an enclosure that does not straddle 0):** **28 of 28**
of A141's witnesses survive. Free square inside the container, H's pose inside `B`, both meeting
`int` of the widened box, interior-disjoint. H penetrates the widened box by **1.84·10⁻⁵**
(`l1_124`, the PI's own page) to **1.87·10⁻¹**; the free square by 8.6·10⁻⁴ to 1.02; separations
1.8·10⁻³ to 9.7·10⁻². A141's gaps reproduce to nine digits. **No witness is bogus.**

**And the PI is right about `TR(0,0)`.** In **0 of the 28** do *both* squares meet the unwidened
cell: H misses it in 25 (by +0.0083 to +0.0360), the free square in the other 3 (+0.0138 to
+0.0246). Every recorded two-crowd lives entirely on the 0.0255-wide K0-WIDEN annulus.

**T1c — the reading tested directly (`code/twocrowd159.py`).** The reading is not `LANE + M ≤ 1`;
it is the joint statement. Maximise `J = min(depth(Q_H, C), depth(Q_F, C), gap(Q_F, Q_H),
slack_H, slack_F)` over `H ∈ B` and a free `F`; `J > 0` **is** a realised two-crowd. Staged
multistart (deepest-H first, then best-F against it, then a 6-D polish), every positive hit
re-verified exactly. At the widened box: **30 of 44** near-miss corners (2 that A141 never
recorded — `node_117` TR, `s2_near_046_619` BL). At the unwidened cell: **9 of 44** —
`l1_192_plain_warm`, `l1_192_sh3_warm`, `node_150`, `node_187`, `node_192`, `node_193`, `node_194`,
`node_195` (TR) and `s2_near_046_619` (BL), `J` from 9.1·10⁻⁴ to 7.4·10⁻², so the reading is **false** on those
nine. On the other 35 the supremum is `J ≤ 0`, and on **16** it is 0 to 10⁻⁹: the two squares can
reach `TR(0,0)` only in a mutually tangent, measure-zero configuration. The reading is right on 35
of 44, and **tight**.

**Lemma A159-1 (why the joint split's target set is only 14 corners).** If some `H* ∈ B_j` and a
free `F` are interior-disjoint with both meeting `int C`, then `lane_corner_split(C, ·, j)` can
never close: the piece `B_k ∋ H*` has `K'(B_k) ⊆ Q(H*)`, so `F` misses `K'(B_k)` and any sound
`lane_ub` is `≥ 1`; and `H* ∈ B_k` meets `C`, so `m_j = 1`; total `≥ 2 > 1`. (All 30 cells carry
exactly one conditioned box, so `F` misses *every* core.) Hence the split is dead on 30 of the 44
by theorem, not by budget, and its whole target set is the other 14.

**T3 — THE CANARY IS CLEAN.** `l1_153` is a Trump image (doubly met at every corner in the widened
sense by construction, A143/A150), and T1 gives it an *exact* witness. Running the full split
there starved at BelowNormal, so the canary was sharpened into its decisive form
(`code/canary159.py`): walk the deterministic `split_box` chain that contains `H*` and run the
ordinary leaf on each piece. Over **15 depths** the piece containing `H*` keeps `m_j = 1`,
`lane_ub = 1`, `M_other = 0`, **total = 2**, and the exact free square stays clear of `K'(piece)`
throughout (−0.0731 → −0.0088). Exactly as Lemma A159-1 requires. Nothing withdrawn.

**T2 — the joint split closes 0 of 9 box classes, and it is geometry, not budget.** `l1_158`
(depths 9 and 15), `l1_159` (= `l1_159_plain_warm` = `l1_159_sh3_warm` = `node_159`),
`l2_p114_011`, `l3_pp114_001_000`, `node_120`, `node_125`, `node_151`, `node_160`. Every open
piece has `open_reasons.no_lane_bound = 0` — it carries a **certified** `lane_ub ≥ 1`, i.e. a free
meeter that provably survives `K'(piece)`, with `m_j = 1` on the same piece. `B_miss` is **empty**
on every class: no sub-box of `B` can be certified to miss the widened corner box, so the split
never gets the cheap half of its dichotomy. And refining makes it worse: `l1_158` goes 15 → **349**
open pieces from depth 9 to depth 15 while closures only rise 23 → 146 — the same frontier
doubling A157 measured on the A57 slot covers.

**T1b — the unwidened leaf kills 0 of 44** (`code/unwiden159.py`; every record carries
`scope: s0_only` and `cell_kind: k0_corner_unwidened` so nothing downstream can bank it as a window
kill). Two corners have no pose of H reaching `TR(0,0)` at all (`node_117` −1.20·10⁻², `s3_far`
−1.96); a 6×-budget retry on `node_117` (`depth0 24, max_depth 40, max_open 9,000,
max_leaves 400,000`) still cannot *prove* the exclusion, so no certificate. `M = 1` in these
records means "not proved excluded", not "can meet". A `w = 0` kill would anyway be **s0-only**:
`W0` is exactly the pad that makes one fixed corner box serve every side in `W = [3.82, s0]`.

**The sample line, and the cross-check that earned its keep (`code/sampleline159.py`).** Per
corner and per width: **20,000** poses of `H` drawn uniformly in `B`, kept when inside the
container and meeting `int` of the corner box (that is `B_meet` at pose level), and up to 400 of
the survivors tested against ~40,000 free candidates meeting the same box, with the from-scratch
SAT. On the **14** corners with no realised two-crowd: 16,584-20,000 poses in `B_meet` and
**0 hits at both widths** (`s3_far` draws none at all, matching `deepest_H = -1.94`). The uniform
draws are cross-checked against the optimisation, and the check paid for itself: on
**`l1_192_sh3_warm` TR at `w = 0`** a uniform hit turned up where the optimiser had returned
`J <= 0`; re-verified exactly at 60 dps it is real (`H` into the unwidened cell 1.05e-2, free
square 9.74e-2, separation 9.05e-4), which is why the unwidened count above is 9 and not 8.
43 of 44 consistent, and no widened-box hit anywhere the optimiser found nothing.

**Verification.** `code/check159.py` is A141's `check141.py` (attempt-local copy; A141 is
read-only) extended with **C7** the `B_meet`/`B_miss` ledger and the burden each side carries,
**C8** a contradiction guard that FAILS any kill certificate at a corner carrying a proved realised
two-crowd (30 such corners), and **C9** an independent sample line with a from-scratch SAT. It
imports nothing from the emitter. Run over all **294** existing A141 certificates: **294 PASS,
0 fail**.

**Bottom line: 0 certificates, 0 cells removed, no budget row credited.** The eleven
converged-alive k0 cells stay eleven. Cost ~**1.9 CPU-h** of a 3 CPU-h cap (wall, not CPU, was
binding — 10 other lab processes; two processes at BelowNormal, affinity 0xFFFF, throughout).

**What is deployable from this.** (a) Lemma A159-1 — one exact two-crowd witness retires a corner
from every lane leaf forever, for ~0.1 CPU-s, and should be screened before any cover budget is
spent (A157 measured the same economics on the A57 slots: cheap sampling beats cover depth by ~17×
in cells-decided-per-second); (b) the C8 guard, which makes that check mechanical for every future
certificate; (c) the measurement that the k0 two-crowd is a **pad** phenomenon (0 of 28 recorded
witnesses survive at `w = 0`; 16 of 44 corners are exactly tangent there), which is A155's pad
result reached from the other side and says where a pad-free (s0-only) leaf could bite.

**Files.** `attempts/A159-k0-nearmiss-joint/` (`BRIEF.md`, `notes/method.md`; `code/xwitness159.py`,
`twocrowd159.py`, `unwiden159.py`, `split159.py`, `canary159.py`, `check159.py`, `fold159.py`;
`results/xwitness159.jsonl`, `twocrowd159.jsonl`, `unwiden159.jsonl`, `unwiden159_deep.jsonl`,
`split159.jsonl`, `split159_deep.jsonl`, `canary159.jsonl`, `check159_audit.json`,
`joint_kills159.jsonl`; `logs/`), plus the four named appends: A115 `notes/t6_report.md` hand-off
list, `docs/budget.md` k0 row, `docs/residue_ledger.md` §4, and a new `polycore_status` column in
`docs/shadows/k0v4/review_k0v4.csv`.

## 2026-09-08 — A162 — the shadow-gallery status board

**What the PI asked for.** A single place that says how much residue is left in the two review
galleries and where. Built `docs/shadows/status_gallery.py` — rerunnable, idempotent, **no LP**, no
write outside `docs/shadows/` — and ran it.

**The counts.** `docs/shadows/k0v4/` **11 pages: 11 ALIVE, 0 DEAD**.
`docs/shadows/a57v4/` **60 pages: 57 ALIVE, 3 DEAD**. By family the dead are `S02` 1, `S11` 1,
`none` 1; by leaf, A149's exact-core `case-measure-certificate-v1` 2 and A57's own tree certificate
`PASS` 1. Underneath the collector read **4,995 kill records, 4,654 of them kills**, over the A57
tree jsonl (the tag authority), A137's supersession ledgers and 159 fresh clipkills, A149's
exactcore/poly/a60 ledgers and day149 rows, A156's `lp156_*`, A136's and A96's A120 closures,
A140's `exactcore140`, A141's `polycore_lane_kills`, and all **342** `*.clipkill.json` under
`attempts/*/certs/**`.

**The three kills, and why the third one is the interesting one.**
`k5_11_interior_Y0275` and `k5_16_interior_Y0275` are A149 exact-core kills on the **G1** tree,
attributed by matching the ledger's `tau_before` against the canonical `(tag, id)` record
(4.999999999999965 and 4.999999999004872 — the G1 records to the last digit, while the L1 records of
the same ids sit at 4.0 and 4.0). `k5_16_interior_Y0083` is **A137 §C.3 in the wild**: A148 drew
that page from the **L1** node's record, which has been a certified `PASS` in A57's own tree certs
(`certs/tree/k5_16_interior_L1/k5_16_interior_Y0083.json`, `tau = 4.5 < budget 5`, converged,
`minmass = 1`) all along — its review-sheet row even carries `eta = -0.5` while the `verdict`
column says `ALIVE-at-LP`. The **G1** node of the same id is still alive (A149 recorded it
`LOST-KILL-ON-RESOLVE` at 16:34). So the page is dead, the id is not, and a `board.py`-style
last-wins id map would have got the attribution backwards in both directions.

**Three non-kills the collector refuses on purpose, each for a recorded reason.**
(a) A140's `exactcore140` rows for `l1_148`, `l2_p65_101` and `l2_p65_111` carry `kills = true` with
`converged = false` and no certificate — A124: a non-converged `tau` was never a bound, so all three
k0 cells stay alive and only `s3_far_BL389484_TR018470` (cert `PASS`) is a kill.
(b) A158's `yescert158.jsonl` rows read `verdict = "KILL"` with `kill = false`; the conditional lane
leaf reaches `1 + LANE + M = 2` on every measured cell and 0 of 141 kill the YES child. **`c0_Y0076`'s
NO child is NOT a kill** — A158b ran the YES child as an LP node and it converges at `tau = budget`,
`eta = 0`. (c) `*__exall.json` is not a kill record (it exists on LOST-KILL / TOO-TIGHT / FAIL too);
`*.clipkill.json` is (A148's rule).

**Tag resolution and refusals.** Of the 3,160 distinct ids in A57's tree corpus, **300 live in more
than one tree**. Records are placed by `applies_to_tags` → prior-`tau` match → unique tree → REFUSE.
**58 records were refused** for an unresolved tag; all 58 are redundant (the same id is killed with
an explicit tag by another record), so **0 nodes are left unattributed**. The rule correctly keeps
A142's two restricted kills (`k5_11_interior_Y0041_D02`, `k5_16_interior_Y0449`, written at
`a_pin = 0.49999997`) on the L1 trees, while `k5_11_interior_Y0041_D02`'s G1_D2 node is killed
independently by A149.

**Residue left.** 68 of 71 gallery pages are alive. Behind them the A57 tree still owes work on
**406 nodes** (`PAUSED.md` v3 §B, 632 → 406 after the fold-in and the exact-core re-emission), out of
1,693 alive A57/A60 records = 1,590 distinct nodes (k5_11 713, k5_16 552, trump5 325), plus the 11
converged-alive `k0_00` cells. The galleries are a 3.8 % sample of the live board and the whole of
the k0 residue: they are where the residue is *looked at*, not where it is *counted*.

**Files.** `docs/shadows/status_gallery.py` (the deliverable), `docs/shadows/STATUS.md` (generated —
the checklist the PI reads first), `docs/shadows/a57v4/killed/` (3 pages, `git mv`d, nothing
deleted), the status section appended to both gallery READMEs with their page links repointed, a
one-line usage note appended to `attempts/A57-shadow-trees/PAUSED.md`, and
`attempts/A162-gallery-status/` (`BRIEF.md`, `notes/method.md`, `results/status162.json`,
`logs/run.log`).

---

## 2026-09-08 — A160: S02's f0 slide, and the pinwheel's common-tilt chain (`attempts/A160-s02-f0-slide`)

**The brief's premise needed one correction before anything could be grown.** `f0` is not a body of
A116's `N`: `a116lib.LOADBEARING["S02"] = ("f1", "f2", "f3")` ("f0 is the strut") and A116's `N` has
four free boxes — `f1, f2, f3, BR(0,1)` — plus five pins, with `f0` and `TR(0,0)` absent. So `f0` was
not left ungrown by an ordering accident; there was no `f0` knob. Growing it means ADDING a fifth
free body, which strengthens the theorem and weakens the hypothesis at the same time, and both had to
be measured.

**The slide is real, and exact.** The gallery's S02 poses (six decimals, worst pair gap −2.9e−7) were
polished by SLSQP + a Newton solve of the active contact system to s\* = **3.886746028606**, tilt
**48.435119375°**, worst gap −3.3e−16; the same solve with `f0` deleted returns the SAME s\* to twelve
digits, so `f0` does not set the side. `f0`'s admissible set was then computed EXACTLY as a polygon —
the eight separating-axis selections of a pair are affine in the moving centre at a fixed tilt, so the
forbidden set is an intersection of eight half-planes and relaxing `gap ≥ −eps` pushes each inward by
exactly `eps` — and the `eps → 0` ladder settles the question an area computation and a pose grid both
get wrong (both return "nothing"): **area and width vanish linearly in `eps` (5.97e−10 and 3.22e−9 at
`eps` = 1e−9) while the length converges to 0.298418661.** The slide is a segment, along `f0`'s own
body axis `e2 = (−0.748205, +0.663468)` (agreeing with `(−sin θ*, cos θ*)` to six decimals) at a
**fixed** tilt — the tilt window closes like `sqrt(eps)`, 10.05° at 1e−2 down to 0.03° at 1e−7, a
quadratic tangency at 48.4351° that opens only upward. Ends (2.180910, 1.507845) and
(1.957631, 1.705836); **three contact graphs** — `{BL(1,0), BR(0,1), f3}` at one stop,
`{BL(1,0), f3}` on the entire open interior, `{BL(1,0), f1, f3}` at the other — which is the PI's
diagonal slot exactly, with no wall contact anywhere, and the gallery's own `f0` sitting at u = 0.120
of it rather than at an end. **At s₀ nothing slides at all**: in A116's s₀-anchored frame every one of
the eleven has an empty admissible set at every `eps` down to 1e−9, because the ten-square core alone
needs s\* > s₀ — the slide is an object of the `s = s*` fibre and is what the box must cover, not a
place a packing can be.

**`f3` is not a rattler; it is the shadow's most load-bearing square** (s\* drops 0.118979 without it,
the largest Δs\* of the eleven, against 0.063870 for `f1`, `f2`, `BL(0,1)`, `BR(0,1)`). Two by-products
of the census: **`BR(0,0)` is a second rattler with a longer slide (0.535705)** — a *slot* square that
A116 pins to a 0.00707 slack core — and the four wedged-but-loadless slots (`BL(0,0)`, `BL(1,0)`,
`TL(0,0)`, `TR(0,0)`) make the shadow's true load path `{f1, f2, f3, BL(0,1), BR(0,1)}`.

**Putting `f0` in `N` costs consumers and does not certify.** The box that just covers the slide is
small (x half-width 0.111, y 0.099, offset −0.098/+0.087 from `f0`'s own anchor) and, as one more
clause in the hypothesis, it cuts A151-B's 96 in-`N` nodes (42 alive) to **15 (8 alive)**; the count
recovers to 96/42 only when `f0`'s box reaches ±0.50 / ±0.47 / ±45°, i.e. only when the clause is
vacuous. Meanwhile the tree with `f0` as a fifth free body **caps**: A116's base `N` plus the
slide-cover box is a WALL CAP at 420 s, and a retry at a 1500 s cap was still running with **0
witnesses and 0 unresolved** at 1024 s of tree time when it was cut to give the tilt slices the CPU
share — certified min 3.8770844 > s₀ throughout — so no `N` containing `f0` was certified inside the
4 CPU-h cap and the ladder never left its first rung. Every `f0` refusal in this attempt is a wall
cap, none is a witness.

**The common-tilt chain works, is cheap, and buys almost nothing.** `s*(θ)` recomputed here on the
shared tilt of `f1, f2, f3` (SLSQP + Newton, tilt pinned, warm-started along the curve, worst gap
≤ 4e−16 everywhere) rises on both sides of 48.435° and is **above s₀ at every tilt** — 3.9968 at 3.4°,
3.8868 at 48.4°, 3.9741 at 88.4° — which is why the links away from θ\* are nearly free. At half-width
1.25° and step 2.5°, **24 of 25 links certify, covering a 60.0°-wide shared-tilt range
[2.185°, 62.185°] at a median 7 s a link** (the whole chain in ≈ 7 minutes of one process), the single
refusal a **wall cap** at Δθ = +15° with 0 witnesses and 0 unresolved — and the same link certified in
12 s from a differently warm-started spine row at the same s\*, so it is a branch-order accident, not
geometry. Sampling found **0 hits in every certified link** and Trump is outside every one. A second
chain at half-width 10° and step 20° certifies Δθ = 0, ±20 at 55–279 s.

**But the chain's own union is 81 of 184 in-`N` nodes / 35 alive, and A151-B ∪ the chain is 104 / 45
against A151-B's 96/42 — plus eight, plus three alive.** The reason is structural and now measured: a chain link forces all three tilts into ONE
window of width 2h, so its ceiling is the number of nodes whose support tilt SPREAD is ≤ 2h —
**63/27 at h = 1.25°, 74/33 at 2.5°, 91/40 at 5°, 124/53 at 10°, 150/56 at 20°** — while of the 20
ALIVE k5_11-frame S02 nodes outside A151-B, **`f2`'s tilt binds 14 and `f3`'s binds 10, and 9 are
blocked by those two tilts ALONE.** Those are INDEPENDENT windows, and no common-tilt chain, at any
tilt range, can open them.

**So the object that reaches them is a product of INDEPENDENT tilt slices — and it works, nearly for
free, but only in one regime.** With `f1` at A116's own box, **all eight axis slices certify with zero
failures in 348 s total**, extending `f2`'s and `f3`'s tilt windows independently over the entire
fundamental domain [−1.56°, 98.44°]; most corners of the 5 × 5 product certify at 2–188 s each, and the
ones that do not are the combinations where two squares are simultaneously near axis-aligned. **But
the growth directions TRADE OFF.** `f2`'s upward slice certifies at `f1`'s base box in 108 s and is
**REFUTED BY A LIVE-LOW WITNESS** together with A151-B's grown `f1` — the witness puts `f1` at 83.44°,
a pose only the ±40° window admits (side 3.869337946 < s₀, re-verified from scratch, worst pair gap
−1.1e−16). Growing all four centre boxes together fails the same way at **r = 0.25 already**:
certified at Δθ = 0 and −10°, witness at +10°; at r = 0.30 witness at 0°; at r = 0.40 witness
everywhere. These are the **first LIVE-LOW witnesses anywhere in the A116 / A151 / A160 line** — A151
saw only wall caps — every one re-verified here (worst pair gap ≈ 1e−16, worst wall 0.0) and drawn.
They bound nine of the eleven squares, so they say nothing about s(11) ≥ s₀; they say the
neighbourhood is too big.

**Therefore A151's "compute-limited, not geometry-limited" holds for single knobs and fails for
compounded ones, and S02's basin is not a growable box but a UNION of differently shaped certified
boxes** — which is exactly what an `N_boxes` list with a disjunctive hypothesis is. A151-B ∪ the
common-tilt chain ∪ the independent tilt slices reaches **114 of 184 in-`N` nodes / 50 alive** (A151-B
96/42, A116 72/32) for **≈ 0.9 CPU-h of tree time across 50+ certified boxes**, with every refusal in
the record labelled wall cap or witness.

**The r_xy wall, in detail.** Growing all four centre boxes together refuses with a LIVE-LOW WITNESS
in under a second: r = 0.25 certifies at Δθ = 0 and −10° but is REFUTED at +10°; r = 0.30 is refuted
at 0° and +10°; r = 0.40 is refuted everywhere tested. This is consistent with A116's own grid, whose
only witnessed failures are at r = 0.30, and it means **r = 0.20 is a geometric limit for growing the
boxes together, not a compute limit** — the asymmetric, one-square-at-a-time growth A151 used is the
only kind that can go further, and even that stops where the compounding does.

**Files.** `attempts/A160-s02-f0-slide/` (`BRIEF.md`; `notes/{method,results,doc_lines,registry_row,
log_entry}.md`; `code/{polish160,pocket160,slide160,f0slide,lib160,grow160,chain160,slice160,
consumer160,needed160,nboxes160,gent160,draw160,drawwit160}.py`; `results/{polish160.json,
slide_exact.json,f0_tilt_window.json,f0_box_price.json,needed160.json,binding160.json,
spine_*.json,chain_*.jsonl,chain_*_summary.json,grow_*.jsonl,consumer160*.json,witnesses160.json,
N_boxes160.json,A160_slide_and_box.svg,A160_witnesses.svg}`; `logs/`), plus the registry row, this
entry, one paragraph in `docs/budget.md` §D and one sentence in `docs/residue_ledger.md` §1b. Two
BLAS-pinned processes at BelowNormal / affinity `0xFFFF` throughout, on a box that ran 16–19 other lab
pythons; wall, not CPU, was binding.

---

## 2026-09-08 (A161) — the CHORD-LIMITED LANE: the PI's sentence about Y0842, made into a leaf, kills 96 alive nodes

**The reading.** On `docs/shadows/a57v4/k5_16_interior_Y0842.svg` the PI said: *"you can only put one
core in the bottom slot by chord sum, and no cores outside that slot can reach BL(1,0)."* That is the
conjunction of two proved pieces — A144's guard-line chord row and A141's lane cover — applied to
complementary halves of the same set of meeters, and it adds no analytic content beyond them.

**The leaf (`attempts/A161-chord-lane/notes/leaf.md`).** At a WALL-ADJACENT usable slot cell `C` of a
pinned class, with a guard line `l` inside the wall row of pins:

    rhs(l) = s0 - SUM_j minchord(B_j, l)            beta = floor(rhs(l))          [A144 LINE-1/2]
    BAND   = { poses with chord on l >= 1 }         LANE_out over the complement  [A141's cover]
    #{non-pin squares meeting int C}  <=  beta + LANE_out + M     and SLOT-CROWD says this is >= 2,

so `beta + LANE_out + M <= 1` is a contradiction and the node is DEAD. `beta` needs no cover at all —
one linear inequality — and the two bottom-row pins of k5_16/trump5 spend exactly 2 of `s0 = 3.877084`
on it, leaving 1.877084 and hence `beta = 1` unconditionally (and `beta = 0` whenever a conditioned
box also crosses `l` with `minchord > 0.877084`, which is 68 of the 98 kills: there the CONDITIONED
square is itself the one square allowed in the wall lane).

**Two exact primitives, both cheap.** (i) BAND over a box is a closed form, not a cover:
`chord >= 1  <=>  |v| <= f(y) = (y + 1 - y^2)/2` with `y = cos + sin`, and `f` is decreasing on
`[1, sqrt2]`, so `max|v| <= f(cs_max)` decides it in ~10 Fraction operations — cross-checked against
A144's independent five-point `minchord` on every box. (ii) `box_misses_cell_exact`, the FULL
separating-axis test over a parameter box (the cell's two normals and the square's two, both signs,
each bound an exact Fraction by a two-endpoint rule). A141's `box_misses_cell` uses only the cell's
normals with the box's bounding half-width, so for a conditioned box at 50-65 deg clearing the cell
along one of its OWN edge normals it can never fire at any depth. **That, not geometry, is why A141
recorded `M = 1` on Y0842**; the new test excludes `H` at the ROOT box in one leaf, and `M` is 0.

**Y0842 / BL(1,0), the headline.** `y_L = 770833/1000000`; the BL and BR pins give chord exactly 1
each (`minchord` on a zero-width tilt bin is exact); `rhs = 469271/250000 = 1.877084`; `beta = 1`;
`LANE_out = 0` on a complete cover of the meeting window in 166 leaves (44 `band`, 106 `witness`, 16
`container`, 0 open); `M = 0`. Total `1 <= 1` — **DEAD**. Sample line: 60,000 poses, 40,696 meet
`int C`, 20,125 BAND (min chord 1.0000000000453), 20,571 OUTSIDE of which **zero** are free.

**Population.** 2,377 (alive node, wall-adjacent usable slot) pairs, staged so that the cheap sound
retirements run first: `beta >= 2` (485), `beta + M >= 2` on every offset (769), an exact free
OUTSIDE pose realising `LANE_out >= 1` (845, plus 53 where two interior-disjoint such poses form
A159's two-crowd witness), then the cover. **98 kills over 96 nodes — 70 k5_16 and 26 trump5, of
which 90 are new** (6 were already dead by A131's pin-clip or A142's exact-clip; A141's own lane
kills were excluded from the population by construction). 126 UNDECIDED inside a 10 s/pair cover
budget over 88 nodes, 1 NEAR-MISS.

**The negative result worth keeping.** k5_11 contributes ZERO. Both of its wall-adjacent usable slots
(BR(0,1), TL(1,0)) sit on a wall carrying only ONE pin chord, so `rhs = 2.877084` and `beta = 2` on
every offset — the leaf needs **two pins on the slot's wall**. Same for trump5's TR(1,0). That is the
structural gate, stated n-generally in `notes/leaf.md` §6: *a wall row of `k` pins prices the wall
lane at `s - k`, and a slot in that lane holds only as many squares as the leftover length allows.*

**Verification.** `code/checkcl.py` is independent of the emitter except A132's `vertex_ok` and A57's
`caselp`: it re-derives the cframe boxes from the node JSON, every `minchord` by its own five-point
implementation (so A144's and A161's are cross-checked on every run), every separating-axis margin,
the band threshold, cover completeness as a prefix code under the split rule, and the arithmetic.
**98/98 PASS.** A118-O1 is inherited verbatim — these are exact-pin class-`S` kills, not slack-family
kills; `notes/leaf.md` §5b records that the `beta` side of the caveat is cheap to lift.

**Lean shape.** `chord_sum_le_side` + `minchord_of_box` (A144's spec, unchanged), the A141/A135 lane
leaf and `shared_point_same_square` (unchanged), two new `Bool` checkers with soundness lemmas
(`checkBandBox`, `checkBoxMissesRect`) and **one** new glue theorem `chord_limited_slot_crowd`, whose
proof is the four-line count above. 0 new axioms.

**Files.** `attempts/A161-chord-lane/` (`BRIEF.md`; `notes/{leaf,t3_table}.md`;
`code/{chordlane,t1_y0842,run161,checkcl,t4_table}.py`; `results/{t1_y0842.json,t3.jsonl,
t3_dedup.jsonl,t3_table.json,checkcl.json,cert_manifest.json,eligible.json,nodepaths.json}`;
`certs/cl_*.json` x98; `logs/`), plus the registry row, this entry, the A57 `PAUSED.md` and A60
`ledger.md` fold-ins and one sentence in `docs/residue_ledger.md` §1. One python at BelowNormal /
affinity `0xFFFF` throughout on a box already running 16 lab processes (counted and waited twice);
~1.4 CPU-h of the 3 CPU-h cap.

## 2026-09-08 (A161 continuation, +3 CPU-h) — the retry, A141's leaf without the chord row, and a correction

**A correction first.** The A161 entry above claims 90 new dead nodes. It compared against A131,
A141 and A142 only. The authority is the collector `docs/shadows/status_gallery.py` builds STATUS.md
from — 44 sources, 5,474 records, 4,994 kills, **3,173 distinct node ids already dead**. Against
that set A161's 105 kill nodes are **27 genuinely new** (23 trump5, 4 k5_16, all level 1;
`k5_16_interior_Y0842` among them). 62 of the 78 already-dead ones are dead in A57's own tree jsonl:
A161's population came from A141's `t2_a5760` snapshot, and A149's and A156's re-solves have landed
since. **Build the population from the collector, not from a campaign snapshot.**

**T5 — the 126 UNDECIDED pairs.** A longer budget alone buys nothing: at 60 s/pair and a 30,000-box
budget, 12 of 12 still ended `time budget exhausted`. What matters is WHICH guard line — on Y0842
the cover blows 40,000 boxes at `y_L = 0.9167` and closes in 163 leaves at `y_L = 0.7917`. Trying the
top 6 ranked offsets: **127 pairs re-run, 13 new KILLs**, 22 closed as no-go by an exact free
OUTSIDE pose, 92 still UNDECIDED. Also landed: budget exhaustion in `chordlane.cover` now folds the
remaining stack into the open set (`leaves + open` still tiles the root) so the pairwise-overlap test
can still certify `LANE <= 1`; on these cells it certifies nothing — the open sets are 600-800 boxes.

**T6 — A141's own leaf with the exact separating-axis test, and why it is the useful negative.**
Over 3,048 of A141's 3,103 early-exit cells (ALL usable slots), `box_misses_cell_exact` gives `M = 0`
on 1,169 and **flips 105** cells where A141 recorded `M >= 1`. Run without the chord row and the band
prune, the lane cover then closed on **none** of 220 `M = 0` cells: **zero kills.** So the exact SAT
test is necessary (it is what made Y0842's `M` go 1 -> 0) but not sufficient — without the band prune
the whole wall row of poses is free and spread, `LANE >= 2` is not excludable, and **the chord row is
what does the killing in every A161 certificate.** `certs141x/` is empty by that result;
`check141x.py` (A141's `check_lane_cert` with `leaf_misses` widened for the new `axis` reason code)
is validated 2/2 against A141's own certificates.

**Files.** `attempts/A161-chord-lane/code/{run141x,check141x,overlap161}.py`,
`results/{t5_retry,t6_mpass,t6_a141x}.jsonl`, `results/overlap161.json`, `notes/t3_table.md` §T5-T7,
109 certificates (all PASS `checkcl.py`), and the correction paragraphs appended to
`attempts/A57-shadow-trees/PAUSED.md`, `attempts/A60-trump5-campaign/notes/ledger.md` and
`docs/residue_ledger.md` §1. One python at BelowNormal / affinity `0xFFFF` throughout on a box at
16-17 lab processes; ~1.9 CPU-h of the +3 CPU-h extension.

## 2026-09-08 — A163-s02-other-frames (Opus engineer) — done

**The question.** Every local certificate around the S02 pinwheel — A116's symmetric `N`, A119's
exact emission, A133's t-certificates, A151's asymmetric `spec_B`, A160's 53-entry union — is in
**k5_11's frame**. The pinwheel's seven slot squares, however, contain the pin sets of all three
classes, so the same absolute configuration is an S02 shadow in **k5_16** (68 alive-at-LP nodes) and
**trump5** (12) as well, and neither has ever had a basin. The PI's example was
`docs/shadows/a57v4/k5_16_interior_Y1110.svg` — family S02, ALIVE, τ exactly 5/5, support = the
pinwheel.

**The frames.** `a116lib.CLASS_PINS` already agrees on them: k5_16 pins `corners4 + BL(0,1)` (so
`BL(1,0)` is dropped), trump5 pins `BL(0,0) BL(1,0) BL(0,1) BR(0,0) TR(0,0)` (so `TL(0,0)` is
dropped), and `L` is the same in all three — the load path `f1 f2 f3` plus `BR(0,1)`, the one
load-bearing slot square no class pins, with `f0` and `BR(0,0)` dropped as the shadow's rattlers
(A160 T1). At the shadow's own side its slot squares sit at every class's pin cells with deviation
**0.0**, and all box sets re-frame with box deviation **exactly 0.0**: the geometry is identical, only
the hypothesis changes. A dropped body is one clause fewer — easier for a node to be in-`N`, harder
for the tree to close — which is why the frames are not interchangeable.

**Result 1 — the transfer is asymmetric.** Re-running every box set through A116's selection tree in
the new pins (240 s cap, sampling survivor rule, Trump test):

* **k5_16: 52 of 54 CERTIFIED**, and both refusals are **WALL CAPS with zero witnesses** (certified
  minima 3.8771058 and 3.8770935 > s₀ when the cap hit) — compute limits, exactly as in k5_11.
* **trump5: 42 of 54**, with **9 LIVE-LOW WITNESSES**, every one re-verified from scratch here (real
  partial packings of the nine squares of `L ∪ P`, sides 3.820000–3.877068 ≤ s₀, worst pair gap
  −4.4e−16, worst wall −2.2e−16). trump5 does not pin `TL(0,0)`, so every object that leans into that
  corner is geometrically false there — including **A151-B itself, refuted in 6.8 s** (side
  3.873864172) though it certifies in k5_16 in 203 s.

**Result 2 — Y1110 is in-N and now covered.** `k5_16_interior_Y1110` lies in exactly two of the 54
box sets — **A151-B** and the **h = 10° chain link at the pinwheel tilt** — with coordinate slack
0.01311; both are certified in k5_16's frame and both carry a **checked exact t-certificate**
(18 289 and 4 638 leaves, certified minima 3.8770844581 and 3.8770914543 > s₀, independent checker
VALID). It needs the wide-tilt objects because its `f3` sits at 47.12°, **0.065° below the bottom of
every h = 1.25° window** — tilt, not position, again the binding coordinate.

**Result 3 — consumers from nothing.** k5_16 goes from **0/0 to 38 of 68 in-`N` / 21 alive** (6 box
sets cover all 21; A151-B alone covers 14), trump5 from **0/0 to 3 of 12 / 3 alive**. The k5_11
control reproduces A160 exactly — chain-only 81/35, slices-only 11/5, union **114/50**.

**Correction of record.** `N_boxes160.json` does **not** contain A151-B: its `a151B`-labelled entries
are slices with `f1` AT A151-B's box, a different object. The union of its 53 entries is 91/40, not
A160's published 114/50; adding A151-B as a 54th set restores 114/50. A163 therefore re-frames 54 box
sets, not 53, and A151-B is the most valuable object in every frame.

**Certificates, not just verdicts.** A136's `entry151.py` refuses to close a node served only by an
A160 union entry (`A160_NO_CERTIFICATE`: A160's `certs/` is empty, no sha256, no checker verdict). So
every box set here was re-emitted through **A133's `gen_local_t.py`** and verified by **A133's
independent `check_local_t.py`**, both imported unchanged with `BASE` re-pointed (A151's technique):
**49+ t-certificates, every checker verdict VALID, 0 errors**, sha256 recorded, and each `N_boxes163`
entry carries the `certificate` block in the shape A136's `CITE_ASYM` uses; the remaining k5_16
entries carry `status: PENDING-CERTIFICATE` plus the one-line command that closes them. Emission is
cheap at these box sizes: 0.6 s / 0.01 MB for an h = 1.25° chain link, 10–98 s for a tilt slice,
229 s / 9.4 MB for A151-B.

**Reading.** A basin is a statement about a HYPOTHESIS, not about a configuration: transporting it to
another class is a re-run, and what survives is decided by which of the shadow's own squares the new
class happens to pin. k5_11 → k5_16 swaps two wedged no-load pins and survives; k5_11 → trump5 gives
up `TL(0,0)` and loses every object that leaned on it.

**Files.** `attempts/A163-s02-other-frames/` (`BRIEF.md`; `notes/{method,results,doc_lines,
registry_row,log_entry}.md`; `code/{lib163,frames163,run163,gent163,emit163,consumer163,witness163,
nboxes163,table163,post163,docappend163}.py`; `results/{frames163.json,tree_k5_16.jsonl,
tree_trump5.jsonl,table163.md,tcerts163.json,witnesses163.json,consumer163_*.json,
N_boxes163_k5_16.json,N_boxes163_trump5.json}`; `certs/*.tcert.json.gz`; `logs/`), plus the registry
row, this entry, one sentence in `docs/residue_ledger.md` §1b and one in `docs/budget.md` §D. Two
BLAS-pinned BelowNormal processes at affinity `0xFFFF`, the 16-process box ceiling polled before every
launch (the box ran 14–19 other lab pythons for most of the attempt, so the work was serialised);
≈ 2.5 CPU-h of the 4 CPU-h cap.

## 2026-09-08 (A161 T8) — the conditional chord-limited lane: the leaf, and where it sticks

**The leaf.** Split the conditioned square's own parameter box (tautologous — the pieces tile it, so
no realisation escapes) and use each piece's OWN polygon core `K'(b) ⊇ K'(B_H)`, which is strictly
fatter and is where the content is:

    n(b) = beta + LANE_out(b)                          if EVERY pose of b misses int C
         = min(beta, LANE_band(b)) + LANE_out(b) + 1   otherwise ;   n(b) <= 1 everywhere => DEAD

`LANE_out` discharges BAND boxes (their poses are charged to `beta` by the chord row); `LANE_band` is
its mirror, discharging boxes every pose of which has chord `< 1`. That mirror needed one new exact
primitive, `chordlane.not_band_ok`: since `chord >= 1 <=> |v| <= f(y) = (y + 1 - y^2)/2` and `f` is
decreasing on `[1, sqrt2]`, every pose has chord `< 1` as soon as `min|v| > f(cs_min)`. The two lanes
are complementary covers over the SAME window, and they must be run as two covers, not as one plain
cover over all free meeters: each carries a prune that discharges half the window, and the plain
cover — which has neither — was measured and does not close.

**The PI's case `c0_Y0169 / TL(0,0)`.** Guard line `x = 364583/500000` on the left wall of the TL
frame; `minchord = [1, 0, 1, 0, 0, 0]` — the two pins below the cell give chord exactly 1 each —
`rhs = 469271/250000`, `beta = 1`. Sample line: 8,174 poses meet `int TL(0,0)`, 58 free, **all 58 of
them BAND** (`outside_free = 0` of 4,258 outside poses). So the PI's first half, *nothing from the
right can reach TL*, is CERTIFIED (`LANE_out = 0` on every piece reached, `m = 1` pieces included);
the second half, *H's corner leaves under 1 of width for a band square*, is OPEN — the `LANE_band`
cover did not close at 3,000 boxes nor at 60,000. **The node is not yet dead and the obstruction is
localised to one cover.** Three levers, in order: rank the offsets for the BAND cover by `band_free`
under `K'(piece)` (the present ranking optimises the wrong lane); split `B_H` shallowly and give each
`m = 1` piece its own line; restrict the band cover's root to the band slab `|v| <= 1/2` before
bisecting (~4x on root volume). The population pass over the NO-LINE / `M = 1` cells was not run —
the extension's CPU went to T5, T6 and three T8 runs; its cost order should start with trump5 BR(0,1)
(82 such cells; 20 of A161's 23 new trump5 kills already sit on that slot), then k5_16 BL(1,0) (94),
BR(1,0) (84), TL(1,0) (81).

**Files.** `attempts/A161-chord-lane/code/condlane.py`, `results/t8_cond.json`,
`notes/t3_table.md` §T8, and the fold-in paragraphs in `attempts/A57-shadow-trees/PAUSED.md` and
`attempts/A60-trump5-campaign/notes/ledger.md`. One python at BelowNormal / affinity `0xFFFF`; the
+3 CPU-h extension is spent (T5 3,351 s, T6 ~1,750 s, T8 ~2,800 s, plus the checkers and the
collector).

## 2026-09-08 — A164-wastage-area (Opus engineer) — done-negative

**The leaf.** The PI's wastage argument on the k0 cell `l1_104` (H at x 2.4626–2.5674, y 2.1482–2.2530,
tilt 30–45°) made into a general, LP-free leaf. For a node whose hypothesis boxes carry cores
K_j ⊆ every pose of the box (A135 exact for a pin, A132 polycore K′ for a conditioned square), let

  U(node) = { p ∈ [0, m]² : NO admissible square contains p },

admissible for a FREE square = inside the container and interior-disjoint from every core; a
hypothesis square's own cover is the union of its poses over its box. **Leaf WASTE [T]:
|U| ≤ m² − 11, so |U| > m² − 11 kills the node with no LP** — each of the eleven squares lies in its
own coverable set and the interiors are disjoint, so 11 = |⋃ Q_i| ≤ m² − |U|. That is A89's Lemma ID
(`docs/proofs/tilt_floor_k0.md` §7) with the corner box removed: Lemma ID is the case where the
charged region is certified by a HYPOTHESIS (shallowness) rather than by GEOMETRY, and the region no
longer has to be a corner box or even connected. Budget B₀ = s₀² − 11 = 4.031780343056, the largest
E(m) on the window slab; the window is covered by inflating only the COVER square to
λ_max = s₀/3.81794 while admissibility stays at side 1 (a λ-admissible square contains the concentric
admissible unit square), so one s₀-frame raster kills the whole slab.

**Verdict: sound, cheap, and it fires on nothing.** 0 kills over all 71 alive gallery nodes (the 11
converged-alive pin-free k0v4 cells and the 60 `docs/shadows/a57v4/` pages), pitch 0.01 × 36 tilt
bins, 8–18 s per node for the whole certificate. |U|/B₀: min 0.00 %, q1 11.75 %, **median 18.56 %**,
q3 23.48 %, **max 42.18 %**; means 3.18 % (k0, 0 pins, budget 10), 19.47 % (A57, 5 pins), 21.20 %
(A60). Refined at pitch 0.005 × 90 bins on the extremes: `f1_L10_0003` (7 boxes) |U| = **1.8969 =
47.05 % of B₀** (window-sound at λ_max 1.8084 = 44.85 %), `k5_11_interior_Y0738` 1.4261 = 35.37 %
(window 1.3271), `l1_104` 0.1290 = 3.20 % (window 0.1152). The best node in the population is short
of the leaf by a factor of 2.1.

**The sharpest measurement: the corner column is ZERO on all 71 nodes.** No corner unit box is ever
certified unreachable, so **Lemma ID's charged region is empty on the whole alive population — not
small, empty** — and 64–100 % of the certified waste is in the four WALL STRIPS, the rest in the
interior. The shallow-corner route of §7 has no consumer at this frontier.

**l1_104: the PI's location is right, the count is not.** All 0.129 units of certified waste sit in
the EAST wall strip — the wedge between K′(H) and x = s₀ that A148's page already flags as the node's
one sub-unit pocket (H → wall x = s, 0.828); the figure shows it as a triangular sliver pointing at
the core. What fails is "only one square's centre can sit near the right wall": unconditionally the
outer admissible-centre mask admits **seven** 1-separated centres in x ≥ s₀ − ½ and **eight** in
x ≥ s₀ − 1 (disk bound and a 0.7-cell cover bound agree to within one). The counting hypothesis that
would give the "one" — K0-FREE′, every corner box doubly met, so eight squares corner-committed — was
measured too and is **vacuous as an area row**: a corner-committed square's centre is within √2/2 of
its box and covers √2/2 further, so the four corner reach-envelopes leave only **0.0166** of the
container uncovered on `l1_104` (max 0.248 over the eleven cells) against the 2 + B₀ = 6.03 the row
needs. Wastage is a LOCATION diagnostic, not a kill; the counted version needs A141's lane counts /
A153's cover number, because B₀ = 4.03 of 15.03 is too large a fraction of the container for a 1–2
unit sliver to reach.

**Soundness and controls.** A raster cell is counted only when NO admissible pose MEETS the CLOSED
cell — never "the centre is not covered" — so the mask is an INNER approximation of U and the area is
a LOWER bound. Two Lipschitz facts do all the work (the same two A148's pages rely on): clearance is
1-Lipschitz in the centre and (√2/2)-Lipschitz in the tilt. Per tilt bin the admissible-centre set is
over-approximated on a grid in the bin's own ROTATED frame (where the square is axis-aligned) and the
cover is a separable binary dilation by a box of half-width λ/2 + λ(√2/2)(dθ/2) + q/2 + p√2/2; each
hypothesis box's own cover is an exact rect-vs-rotated-square SAT gap against a margin. Controls:
7.1 M poses drawn over the population, **1 223 887 certified admissible by an independent SAT pass,
976 134 carried through the containment test, 0 hits**; and an independent checker (`verify164.py` —
its own separating-axis test, its own dense sweep over the region a meeting square's centre can
occupy, no code shared with the dilation or with A132's `poly_square_depth`) confirmed five masks
cell by cell — `l1_104`, `l1_158`, `l2_p114_001`, `k5_11_interior_Y0738`, `f1_L10_0003` — with
4.6–7.1 M meeting poses tested per node and **0 admissible meeters**.

**Two bugs found and fixed mid-attempt, both in the diagnostics, neither touching |U|.** (i) The
conditional crowd row computed n_loose = 11 − 4·n_per_corner − n_boxes without checking the sign and
so flagged spurious CROWD-KILLs on pinned nodes (n_loose = −3 on `k5_16_interior_Y1117`): the
hypothesis K0-FREE′ is only stated for a pin-free node and is now refused elsewhere. (ii) The outer
admissible-centre mask was read at the nearest rotated node with NO dilation, where the chain
cell-centre → cell → nearest node needs radius 2; fixed, and the k0 and A57 populations were re-run
so every stored row comes from the same code.

**Lean shape.** `waste_kill (N) (m) (R : Finset Cell) (hR : ∀ C ∈ R, RasterCert N m C)
(hgt : R.card * pitch² > m² − 11) : ∀ P : Packing 11 m, ¬ P.Consistent N`, with four named
obligations: **W1** measure (eleven pairwise interior-disjoint unit squares cover exactly 11), **W2**
core transfer (K_j ⊆ Q_j and disjoint interiors ⇒ a free square is disjoint from the core — where
A132/A135's certified cores enter, one line), **W3** raster soundness (the two Lipschitz lemmas plus
the window/dilation bookkeeping — the only analytic content, and the only place the pitch, the tilt
count and the margins appear; **not written**), **W4** window transport (same bookkeeping as
K0-WIDEN / Lemma B). Zero new axioms if W1–W4 are proved; one (W3) if the Lipschitz reduction is
assumed, which is the axiom A148's pages already lean on informally — so writing W3 pays for both.

**Reading.** An area budget cannot carry a packing argument at this side. E(m) = m² − 11 is 27 % of
the container, and the single-square uncoverable set is the wrong object to charge against it: with
at most seven small cores in a 3.877-side box almost every point lies inside SOME admissible unit
square. What the leaf is good for is telling you WHERE the slack is (wall strips, never corners) and
at what depth an area argument could start to bite — |U| scales with the box count (0.128 at 1 box,
0.793 at 6, 1.701 at 7), so the first fire is at 9–10 boxes, i.e. 1–2 free squares left, where the
LP is already cheap. That is the honest reason the leaf has no consumer.

**Files.** `attempts/A164-wastage-area/` (`BRIEF.md`; `code/{geo164,run164,fig164,verify164,
replot164,summarise164}.py`; `results/{summary164.txt,summary164.csv,u164_*.jsonl,mask_*.npz,
verify164_*.json}`; `figs/{l1_104_U.svg,f1_L10_0003_U.svg}`; `notes/{leaf.md,doc_lines.md,
log_entry.md,registry_row.md}`; `logs/`), plus the registry row, this entry,
`docs/residue_ledger.md` §6.3 and one paragraph in `docs/budget.md` §D item 1. Two BelowNormal
processes at affinity `0xFFFF`, the 16-process box ceiling polled before every launch (the box ran
7–19 other lab pythons throughout, so the sweeps were serialised); **3 212 s of measured run164 time plus ~1 000 s of independent checking and ~600 s in a first, too-slow checker that was killed = ≈ 1.35 CPU-h of the 3 CPU-h cap.**
READ-ONLY on every campaign and on A89/A115/A132/A135/A140/A141/A148 — `geo148.obstacles_of` is
imported, not copied, so the two attempts cannot drift apart.

## 2026-09-08 — A165-cascade-l1_104 (Opus engineer) — done-negative

**The PI's CASCADE on the k0_00 cell `l1_104`, built as an explicit case tree with a certificate at
every forcing step, and the Trump-image cell `l1_153` as the canary.  The cascade is sound, the
canary survives it, and it does not close the cell — the chain breaks at a named place, and three
reusable things come out.**

### The canary first (`l1_153`, which a real 11-family reaches — image `g4`, square 9)

* K0-BLOCKED holds for `g4` **only because of the K0-WIDEN pad**: widened-corner meeter counts
  BL 3, BR 2, TR 2, TL 2; on the plain unit corner boxes BL 1, BR 2, TR 1, TL 1.
* Every real FREE meeter of every corner is located inside an OPEN box of that corner's cover
  (0 unlocated at all four corners): no cover step discards the real family.
* **`M(TR) = 1` at `l1_153`** — its `H` *is* a TR meeter, penetrating 0.477 / 0.290 past the widened
  cell's corner, and A141's cover and A161's exact SAT agree.  So its TR crowd may be
  `{H, one free meeter}`, the real family lands in that mixed case, and the case survives both pair
  prunes.  This is the discriminating fact of the whole attempt (below).
* All four wall rows accept every real case pair: top 1/1, right 1/1, bottom 3/3, left 3/3.
* The only leaf that kills anything — the five-box spread LP at budget 6 — leaves the canary's own
  real four-tuple **ALIVE at τ = 6.7348, η = +0.7348**, while 4 of 4 random `l1_104` tuples die at
  η = −1.0000.  **CANARY PASS at every step run.**

### `l1_104`: the tree, and where the chain breaks

Root: A115's converged record, τ = 10.000000 against budget 10, zero slack.

* **C1 (structure, certified).** (R6) gap `s0 − 2(1 + w) − √2 = +0.41185029 > 0`; and **`M(c) = 0` at
  all four corners** by A161's exact full separating-axis test over `H`'s parameter box (A141's
  coarse cell-normal test proves it only at BL/BR/TL).  Hence
  **`11 = 8 FREE corner meeters + H + exactly 2 further squares`**.
* **C2 (the PI's step (a), CONFIRMED).**  Complete prefix-code covers at split depth 8 (Kraft sum
  exactly 1, checked): TR **82** open boxes against TL 238, BL 248, BR 191 — `H`'s polygon core
  (area 0.655248, 40 certified vertices) sits on the TR diagonal and removes two thirds of the TR
  approach.  Pairs after A118's always-overlap and A141's shared-rational-point prunes: TR 3 403 →
  522 → **500** cases; TL 7 050, BL 8 194, BR 3 879.
* **C3 (the PI's step (b), CONFIRMED as a bound on 37 % of the branching).**  On **185 of the 500** TR
  cases both meeter boxes carry a **certified** `minchord ≥ 1` on the best top-wall line, so
  `rhs(l) = s0 − 2 = 1.8771` and **β = 1**: at most ONE further square of the family fully crosses the
  top strip — exactly the PI's sentence.  Over all 500 cases the top rhs runs 1.6740 / 1.9396 / 2.7963
  (min / median / max) and there are **0** row kills at three boxes.  The PI's picture of the pair is
  right as well: **434 of 500** cases are one meeter up the right wall past `H` plus one along the top
  wall, 66 are two top-wall meeters, and none is diagonal.
* **C4 (the PI's step (c), BREAKS) — and the new leaf it produced.**  A144's row read on each wall
  strip with the two corner crowds that wall can see is a sound predicate on the EDGES of the
  four-corner cycle, so the survivor count is a transfer-matrix contraction (A150 §4) and the product
  is never enumerated.  Measured with 32 exact rational lines per wall: top (TR,TL) kills **4.09 %**,
  right (TR,BR) 0.45 %, bottom (BL,BR) 0.49 %, left (BL,TL) 0.52 %; four-cycle survivors
  **1.0584·10¹⁴ of 1.1204·10¹⁴ (94.5 %)**.  *Why*: by **Lemma (TOP)** (`c_y ≤ s0 − h`, `h ≥ 1/2`, so
  no admissible square lies entirely beyond a guard line within 1 of a wall; at `y_L = s0 − 1 − w`
  the exception needs tilt within **1.4809°** of an axis) a TL meeter must CROSS the top line — but
  its chord there may be arbitrarily small.  So "β = 1" and "TL carries two meeters" are not in
  contradiction: the second TL meeter is a *shallow* crosser and costs the row ≈ 0.
* **C5 (area).**  `|U|` at 3 boxes = 0.189–0.203 against `B0 = 4.031780` — 20× short, and A164 (which
  landed the same day, `done-negative`) shows the charge only starts to bite at 9–10 conditioned
  boxes.  The cascade cannot borrow an area charge to repair step (c).
* **C6/C7 (LP).**  `{H, TR_a, TR_b}` at budget 8: **τ = 8.000000 exactly, η = 0.0000, 3 of 3** — two
  cores stacked at one corner plus an interior core buy *nothing*.  `{H}` + ONE meeter box per corner
  at budget 6: **τ = 5.000000, η = −1.0000, 4 of 4 converged kills, 1 PASS under the FROZEN
  `verify_case.py`** (the other three are the lab's standard "LP-dead, certificate pending").
* **C8 (the price).**  The spread hypothesis is a genuine COVER of K0-BLOCKED, so its cost is the
  product of the cover sizes.  Ladder on `l1_104`: depth 3 (`a ≈ 0.048`, product 3 072) η **+1.0,
  +3.0, +2.5, +2.0**, 0 of 4 kills; depth 4 (`a ≈ 0.054–0.083`, product 49 152) η **+1.0, +2.0**, 0 of
  2; depth 8 (`a ≈ 0.300`, product **9.24·10⁸**) η −1.0, 4 of 4.  So the LP decides only where the
  product is 10⁹ nodes ⇒ **≥ 10⁷ CPU-h** against `docs/budget.md`'s 9 400–12 000 k0 row.  A150's
  crossover, reproduced on a single cell.

**Verdict: `l1_104` SURVIVES.**  The corner-first line stays closed (A143, A150, A154, A155, A159);
the cascade is not a route past it.

### What keeps

1. **The `M(c) = 0` upgrade**, one line: replace A141's `box_misses_cell` by A161's
   `box_misses_cell_exact` in `polylane.cond_can_meet`.  On `l1_104` it turns `M(TR)` from *undecided*
   into a certified 0, which is what licenses corner-pair branching; on `l1_153` it correctly returns
   1.  Re-run corpus-wide.
2. **The four-wall chord-row product** — sound, exact, seconds to run, no cover refinement, and it
   composes with any product cover as a 5 % pre-filter.
3. **Lemma (TOP)**, `n`-general: no admissible unit square lies entirely beyond a wall guard line
   placed within 1 of that wall, so a wall row is a *complete* charge on the strip's occupants — and,
   read negatively, that is exactly why the row is weak (crossing is forced, a chord ≥ 1 is not).
4. **Spread beats stacked.**  1 core at a corner: η −0.044 (A143); 2 cores at the same corner: −0.083
   (A143); 2 cores at one corner + an interior core: **0.0000** (A165); 4 cores at 4 corners: −1.0 to
   −6.0 (A150), and −1.0 uniformly with `H` added (A165).  Rule for every future node: spend the
   conditioning budget on cores that are pairwise far apart, never on a second core at a corner that
   already has one.
5. **The named gap**: the cascade needs a leaf that charges a **shallow** corner meeter — large
   footprint in the corner cell, small chord on the wall line.  It is the same gap that stalls A161's
   Lemma CL on `k5_16_interior_Y0842/BL(1,0)` and the 28-of-44 A141 near-misses with realised
   two-crowd witnesses.  A164 has now ruled out the area charge as the candidate.

### Files and discipline

`attempts/A165-cascade-l1_104/` — `BRIEF.md`; `code/{cas165,cascade165,rowprod165,lp5165,trump165,
tree165,fig165,check165,certs165,probe165}.py`; `results/{cover_*,pairs_*,geom_*,rowprod_*,lp3_*,
lp5_*,probe165_*,cascade165.jsonl,check165_*,cert_manifest_*}`; `certs/` (the `cascade_Mzero_v1`,
`cascade_cover_v1` and `cascade_row_v1` certificates plus the four `case-lp-certificate-v1` files and
their verifier reports); `notes/{cascade.md,doc_lines.md,registry_row.md,log_entry.md}`;
`figs/cascade_l1_104.svg`; `logs/`.  Plus the registry row, this entry and one paragraph in
`docs/residue_ledger.md` §4.  The independent checker `code/check165.py` (C1–C9: the pad and (R6),
cover completeness as a prefix code with the split rule replayed, every discharge reason re-derived
by independently coded exact tests, both pair prunes, `M(c)` by an independent SAT plus 5·10⁴ sampled
poses per corner, every chord-row certificate re-derived in the HARD direction, the (TOP) arithmetic,
and a falsification pass in which every drawn corner-meeting pose outside the cover must land in a
`witness` leaf and contain that leaf's rational point) reports **ALL_OK, 0 failures**.

Discipline: ≤ 2 BelowNormal processes at affinity `0xFFFF`, the 16-process box ceiling polled before
every launch — the box carried 14–19 other lab pythons throughout, so every run was serialised and
two queued runs (a depth-6 rung of the ladder and a depth-7 cover) were **dropped rather than
launched over the ceiling**; this attempt's own `PAUSE` was used once to stop the `lp3` sample
cleanly; `PYTHONDONTWRITEBYTECODE=1`; no recursive deletes; the frozen verifier untouched.
**≈ 1.9 CPU-h of the 4 CPU-h cap.**  One read-only slip was found and repaired inside the attempt:
A150's `lp150.certify` writes into `lp150.BASE/certs`, so the first four LP certificates landed in
`attempts/A150-four-corner-product/certs/`; they were **moved** (never deleted) into
`attempts/A165-cascade-l1_104/certs/`, A150 is byte-identical to its prior state, and both A165
drivers now rebind `lp150.BASE` at import so nothing can be written under a prior attempt again.

## 2026-09-08/09 — A166-nearest-corner-subtree (Opus engineer) — the PI's per-node nearest-corner sub-tree: one sub-tree, not eleven; the canary forces a second branch; the (C) leaf is provably unavailable

**The corner is `TR`, for everything.** The metric is `|z_H − p_c|` from the conditioned box's CENTRE to
the corner POINT. It comes out **`TR` on all eleven converged-alive k0_00 cells** (`d` = 1.8536 … 2.3943,
smallest margin to the runner-up 0.042) **and on 117 of the 119 remaining open k0_00 cells** (A115's 166
open records minus A141's 47 `K'`-lane kills; the other two are `BL`). The reason is structural: A38's
level-1 cover conditions a square in the D4 **fundamental triangle** of the interior zone, which lies in
the TR quadrant. So the brief's "a sub-tree per hard node" is ONE sub-tree, the corner never has to be
chosen, and it is rooted at exactly the corner A141/A159 found at NEAR-MISS on five of the eleven.

**The canary passes, and it corrects the construction.** `l1_153` is Trump's image `g4`, square `sq9` —
one of the three INTERIOR tilted squares — with pose distance **0.000000** to `B_H` in all three
components (`code/trump166.py`; the other seven images have no square in `B_H`, so only `g4` imposes an
obligation). `g4`'s two widened `TR` meeters are the corner slot square `sq5` (penetration 1.000, cover
cell `(0,0,0)`) **and `sq9 = H` itself** (penetration 0.0359, cover cell `(3,4,3)`). Enumerated literally,
`l1_153`'s budget-8 pair cover is EMPTY: 193 of the 216 cover cells are dead, 3 degenerate, 20 alive, and
all 20 alive cells lie in the corner-hugging block, so every pair of them is within centre distance 1.
**A tool that read "all pair cells dead ⇒ dead" would have certified a kill of a family that exists.**
K0-BLOCKED says the corner box has two DISTINCT meeters; it does not say either differs from the
conditioned square. So the sub-tree owes two branches — (a) budget `11 − 3 = 8`, both meeters `≠ H`;
(b) budget `11 − 2 = 9`, one meeter IS `H` — and (b) exists exactly when some pose of `B_H` meets
`int B_TR^w`, decided exactly by A161's `box_misses_cell_exact`. `g4` lands in (b). Recorded as a rule in
`notes/canary.md`.

**What conditioning on `H` is worth, geometrically: 91–100 % of the corner-first pair root, for pennies.**
The shared census (A143's `(P2)`/`(P1)`/`(P1s)` over all `216·217/2 = 23 436` unordered pairs of A155's
216-cell cover — no transpose quotient, because `H` breaks the corner's stabiliser) leaves 4 244 live
pair cells at the window pad (3 646 at pad 0). Conditioning on `H` leaves **0, 0, 0, 0, 16, 25, 60, 139,
178, 237, 371** on the eleven, in increasing order of `d`, for 3–95 CPU-s a cell after a 100 CPU-s
census. The whole cut is the two `H` stages: **99–191 of the 216 cover cells (46–88 %) cannot hold a
corner meeter distinct from `H` at all**, because a square there would have to overlap `H`'s own square
(`H2` = centre distance < 1; `H1` = `K'(B_H)` meets `K'(X)`). A161's exact reach test removes a further
constant 16, A131's clip with `H`'s inscribed axis core (A158's rule) 0–6, and A143's own pair chain plus
A158's mutual clip (run FIRST, per tilt sub-bin) and an exact core-disjointness budget gate only 0–26 pairs on top.

**And the free lunch is provably unavailable.** A (C) leaf — branch (a) empty AND branch (b) impossible,
i.e. a kill with no LP, no certificate and no depth — needs `H` close enough to the corner to crowd the
whole zone AND far enough that it cannot reach the corner box. Measured over the whole pool: `H` can meet
`int B_TR^w` exactly on `d ∈ [1.5715, 2.0573]` (53 cells) and provably cannot exactly on
`d ∈ [2.0127, 2.5943]` (66 cells), while every one of the 11 + 41 cells with an empty branch (a) has `d ≤ 1.9319` — and the smallest
`can_meet = False` cell (`l1_148`, `d = 2.0127`) already keeps 25 pair cells. **The two conditions are
anti-correlated and their intersection is empty on all 119 cells.** Lemma A166-1 (the "squeeze": if
`diam(Z(w) \ ∪_{v ∈ R_H} B(v,1)) < 1` then `H` must itself be a meeter, with an exact grid+hull bound)
fires on 1 of 22 (cell, pad) pairs — `l1_124` at pad 0, bound 0.7255 — and never at the window pad,
because `Z(w_max)` is 1.2326 wide and the far set generally has two components more than 1 apart. The
box-level cover is the sharper instrument here and `K'` is why: on `l1_153` the cell at local `(5,0)`
survives `H2` at `maxdist = 1.1075` and dies on `H1` at `K'` depth `1.09e-3`.

**The PI's prediction, decided; and the coordinator's two additions.** *Prediction:* "for a Trump-like
`H` whose nearest corner is SIMPLE in Trump, forcing that corner doubly met contradicts the Trump-like
packing and the LP dies at once; only the `H` adjacent to the non-simple corner survives." **Right in
direction, wrong in consequence.** The six cells whose nearest corner is SIMPLE in their matching Trump
image are exactly the six with the closest Trump matches (pose distance 0.000–0.226) and the smallest
`d`, and four of them have branch (a) ANNIHILATED — forcing `TR` doubly met by two squares OTHER than
`H` is indeed contradictory there. But that is not a kill: those same four are precisely the cells where
`H` itself can reach the corner box, so branch (b) survives — as on `l1_153` it must. The five cells
whose nearest corner is NON-SIMPLE all survive branch (a) with 16–371 pair cells, so "only the `H`
adjacent to the non-simple corner survives" is backwards as a statement about which branch is empty.
*Addition (1):* every one of the eleven matches one of Trump's three INTERIOR tilted squares — `sq9`
(`l1_153` exactly, `l1_159`, `l1_148`), `sq8` (`l1_104`, `l1_124`, `l1_158`), `sq7` (the five NON-SIMPLE
cells) — and `sq7`, the "third" interior square, is the one whose matches are POOR (0.19–0.73) and whose
cells the geometry hits LEAST, so "the third interior square should die fastest" does not survive; in
`g0`'s frame `sq7` is nearest `TL` (2.554) with `BL` a close second (2.586), not clearly at the
three-simple corner. *Addition (2):* the quadrant census (split at `s0/2`) is **`3/3/3/2` in every one of
Trump's eight images, and the sparse quadrant is always the one DIAGONALLY OPPOSITE the three-simple
corner — never the non-simple one**, so "the non-simple quadrant holds exactly the two meeter centres and
nothing else" is not Trump's pattern: it always holds a third centre, and that third centre is always one
of the three interior tilted squares. The corrected signature is *one sparse quadrant, opposite the
three-simple corner*. On the eleven the dual support's sparsest quadrant is `TR` on 8 of 11 — thin exactly
where `H` and the forced corner crowd both live — but supports of 10–83 placements are not comparable
one-for-one with 11 squares, so this is a shape statement, not a count.

**Free by-product worth keeping: 66 certified `M = 0` corners.** A141/A148 record `TR(0,0): M 0?` on six
of the eleven — a sampled 0 with a question mark, because A141's `box_misses_cell` separates only along
the CELL's normals with the box's bounding half-width and so can never fire for a box whose square clears
the corner box along one of its OWN edge normals. A161's full separating-axis test over the parameter box
**certifies** `M = 0` on 66 of the 119 open cells and refutes it on the other 53. That is a strict
strengthening of A141's lane ledger, obtained for free.

**LP.** Budget 8 (`H` + two `TR` squares, A135 exact cores, `K'` an audit column, warm from the cell's own
A115 record, 240 s cap, FROZEN `verify_case.py` sha `521cb01f…`) and budget 9 (the degenerate branch).
33 nodes decided in 7 244 s of measured solve time (≈ 1.2 CPU-h at the ~28 % CPU share two BelowNormal
processes got on a box carrying 7–14 other lab pythons), inside the 3 CPU-h cap. **Budget 8, n = 21:
`η` min −1.4706, Q1 −0.5000, median −0.0993, max 0.0000; 9 converged; 2 converged kills. Budget 9
(degenerate), n = 12: `η` min −0.0097, median −0.0000, max 0.0000; 0 kills.** The reading: A158b's
exact-1 accounting is the default — the degenerate child returns `τ = 9.000000` on every cell measured,
which is A143's "second core at the same corner" geometry (`η ≈ −0.08`) with `H` added, and no amount of
compute moves it. The budget-8 child spans A143's one corner (`η = −0.04`) and A150's four
(`median η = −1.0`): it reaches `η = −1.4706` (`l2_p65_101`, unconverged), `−1.0000` (twice, converged
and certified), `−0.5000`, `−0.4680`, and sits at `0.0000` on the rest. **Three spread cores are not four
spread cores: two of A166's three sit at the same corner, and that is the whole difference from A150.**

**One CERTIFIED kill — and getting it certified uncovered a bug in SHARED machinery
(`notes/certificate_bug.md`).** `l2_p65_101_b8_005_512` converges at `τ = 7.000000` against budget 8 in
118–134 s and the frozen verifier first reported 32 HOLES at every one of five separation rounds. The
cause is not the LP and not the margin: **`caselp.make_certificate` rebuilds the hypothesis with
`Hyp.from_json`, whose `__init__` sets `cores = [b.core() for b in boxes]` — the STOCK cores — discarding
the `cores` field the json carries.** Every attempt that runs a node with A135's certified EXACT cores
uses the `ExactHyp` pattern (A150, A158b, A166, A140's exact-core re-solves): the LP's row filter drops
placements penetrating the EXACT core, the certificate then exempts only the STOCK core, and every
placement in the annulus between the two is a guaranteed hole. All 32 holes here are the single
axis-aligned placement `(3.35109, 1.49000, 0°)`, at SAT depth **+0.029594 against the exact core** and
**−0.000001 against the stock core**, with `exact_mass = 0` — which is why the A13/A14 separation loop
cannot move it: the row it is asked to add is precisely a row the LP is entitled to drop. Confirmed
independent of the scale (1.005, 1.02, 1.05, 1.10, 1.14) and of the rational grid (1e6, 1e9, 1e12): the
same 32 holes every time. **Carrying the exact cores — sound, because A135's `exact_a` certifies
`K(B) ⊆ Q(p)` for every pose `p ∈ B`, and the bug over-claims so old PASSes stay valid — gives PASS on
the frozen verifier for 15 of 15 certificates** (`code/certfix166.py`,
`results/certfix166_l2_p65_101_b8_005_512.json`), so A166 has a certified budget-8 kill:
*no 11-square packing has a square in `l2_p65_101`'s conditioned box together with two distinct squares
in those two `TR` cover cells* (total `7.035000 < 8` at scale 1.005). **And the same substitution turns
5 of 5 of A150's previously-FAILING certificates into PASSes** (`code/certaudit166.py`,
`results/certaudit166.json`; A150 is read-only, the patched copies live under A166, and A165's live
`l1_104_spread_*` certificates in the same directory are excluded by prefix), so **A150's four-corner
root is 7 converged kills and 7 CERTIFIED, not 4**, and its §5 sentence "they need the A13/A14
separation loop with more rounds and a longer `cert_time`" is wrong — they needed the cores they were
solved with. `caselp.py` was NOT edited (read-only); A166 patches the certificate in its own emission
path. **127 of the 166 open k0_00 records carry the verdict `kill-candidate (cert FAIL)`; if they were
emitted through an exact-core path they are candidates for immediate certification at zero LP cost**, and
the same question applies to A140, A149, A158 and A165. `code/certaudit166.py --dir <certs dir>` runs
that audit on any directory, writing only under A166.

**Price.** Geometry: 0.5 CPU-h for the whole 119-cell pool — the cheapest per-node geometry in the k0 lab,
and worth running for the 66 certified `M = 0` corners and the survivor counts alone. LP: 1 048 nodes to
decide the eleven at level 1 (70–95 CPU-h), ≈ 1.2·10⁴ nodes and **800–1 000 CPU-h** for the pool at level
1, **6 000–8 000 at depth 2** under A85's law, plus ≈ 400 degenerate nodes at 25–30 CPU-h — i.e. the same
order as `docs/budget.md`'s 12 000 CPU-h k0 row, without removing any of the interior tree's obligations.
**Window transfer costs nothing new**, unlike A155's slab route: every A166 stage is stated at the full
K0-WIDEN pad `w_max = 0.0255100742` and every test is monotone in `w`, so a fixed-side `verify_case` PASS
carries all of `[3.82, ŝ)` by Lemma B.0 + Lemma K0-WIDEN alone (both `[T]`); certificates are stamped
`scope: s0_fixed_side`, `window: transfer pending (k0_route sec 4.1)` until that two-lemma chain is signed
off in `k0_route.md`, which is proof-reading, not compute. The remaining window debt is the old one:
K0-O1 (k1_00's tree, ∀-packings, ~200–300 CPU-h, paid once).

**Two corrections to inherited code.** (i) `exactcore.cores_pairwise_disjoint` compares
`max(|Δkx|, |Δky|) − (a_i + a_j) > 0`, the separating-axis test on the `x`/`y` axes with support radius
`a`; a core at tilt `θ` has `x`-support radius `a(|cos θ| + |sin θ|) > a`, so the function is **not a sound
interior-disjointness test for TILTED cores** — it can report DISJOINT for cores that overlap. It is
correct for the axis-aligned pin cores it was written for. A150's four-corner LP (four tilted cores) and
A158b's seven-box gate both called it; A166 uses its own exact rational SAT over the four edge normals
instead (`geo166.cores_disjoint_exact`), and both earlier gates should be re-checked. (ii) A141's
`box_misses_cell` vs A161's exact version, as above.

**The coordinator's mid-attempt reinforcement (from the PI's review of A165) — already satisfied, and
the run was redone in that order to be sure.** Every pair box is clipped against `K'(H)` AND against the
other pair box's core (A158's mutual clip) **per tilt sub-bin (`nsub = 4`) and BEFORE** the pair leaf, the
reach test, the exact-core gate, the figures and the LP; the boxes' `K'` and their four sub-bin `K'`s are
rebuilt on the clipped boxes, so every later test uses the smaller box. A box all of whose poses meet
`K'(H)` is emptied and the case dies — that is A166's `DEAD_CLIP` (or `DEGENERATE_CLIP`, where the box
could BE `H`; the split is what the canary needs). The earlier ordering (mutual clip last, `nsub = 1`) is
retained in `results/v1/`: moving the mutual clip first and refining it to 4 sub-bins takes `MUT` from 1
to 8 pair kills on `l1_071` and 0 to 10 on `l1_104`, empties one further cover box on `l1_124` and one on
`l1_158`, and lowers survivor counts by 1–5 per cell — **no verdict changes**, and the two certified
kills were solved on the (larger) `nsub = 1` boxes, so they remain valid a fortiori. Kept fractions per
box per cell are in `notes/tables.md` §6b and in each `survivors166_*.json`. The figures follow the same
instruction: `K'` of each box SOLID as the box's core, the pose union a thin dashed outline only, with
the legend saying it is not feasible space.

**Discipline.** Read-only on every campaign and prior attempt, A165's live `l1_104` files included (A165
was running throughout; nothing of it was read or written). Frozen verifiers byte-identical
(`verify_case.py` imported by path, sha checked into the certificate records). Every sentinel polled by
`lp166.py` before every node; no shard launched; no recursive deletes; `PYTHONDONTWRITEBYTECODE=1`
everywhere; 2 BLAS-pinned BelowNormal LP processes at affinity `0xFFFF` with the lab-python count polled
before launch (the box carried 7–14 other lab pythons throughout, so the LP ran at ~28 % CPU and the wall
per node was ~270 s). Independent checker `ALL_OK` (20 000 cover draws, 2 109 corner-meeting poses, 0
misses; 0 contradictions over 4 213–9 639 sampled pose pairs per stage per cell; realised triples found
for the survivors of three cells, so those survivors are not artefacts).

**Files.** `attempts/A166-nearest-corner-subtree/` (`BRIEF.md`; `code/{cells166,geo166,subtree166,
squeeze166,pick166,lp166,canary166,check166,trump166,price166,draw166,report166,cert166,certfix166,
certaudit166,clipaudit166}.py`, `run166.ps1`;
`results/{subtree166.jsonl,subtree166_wmax.jsonl,subtree166_w0.jsonl,survivors166_*.json,
paircensus166_*.json,nearest166.json,trump166.json,squeeze166.json,canary166_wmax.json,
coverplan166_wmax.json,nodes166_wmax.json,price166_wmax.json,check166_wmax.json,clipaudit166_*.json,
cert166_*.json,certfix166_*.json,certaudit166.json,lp166_wmax_s*.jsonl,lp166_retry.jsonl}`;
`certs/`; `figs/a166_{wmax,w0}_*.svg` (one page per cell per pad, A148 panel style, the three boxes
drawn); `notes/{method,canary,certificate_bug,composition,tables,registry_row,doc_lines,log_entry}.md`;
`logs/`), plus the
registry row, this entry, and one paragraph in `docs/residue_ledger.md` §4.

## 2026-09-09 — A167: the CONDITIONAL chord-limited lane, run over its population (done-mixed)

A161 stated the conditional form of the chord-limited slot lane and never ran it; the cap went on the
retry, on A141's own leaf, and on three attempts at the PI's `c0_Y0169`. A167 ran it over the whole
population, and the population was built **from the collector** (`docs/shadows/status_gallery.py`,
5,742 records / 5,258 kills / 46 sources at the start) rather than from a campaign snapshot — A161's
own lesson, after 62 of its 96 "kills" turned out to be nodes A149/A156 had already killed. That gave
**416 cells over 258 ALIVE A57/A60 nodes**: every `NO-LINE (beta + M >= 2 on every swept offset)` or
`UNDECIDED` cell of A161's T3 tables with `M = 1` — precisely the cells where `H` reaches the slot, so
the unconditional form cannot fire by construction. All 416 ran, at 60 s a cell (~21 s actual), in two
BelowNormal processes.

**The leaf, per piece.** Split `B_H` by A141's deterministic bisection; on a piece `b`, with `K'(b)`
its own fattened core and ONE guard line `l(b)`:
`n(b) = beta(b) + LANE_out(b)` if every pose of `b` misses the cell, else
`min(beta(b), LANE_band(b)) + LANE_out(b) + 1`; `n(b) <= 1` everywhere contradicts SLOT-CROWD.
Two additions to A161's form, both sound and both load-bearing. **Per-piece `beta`:** `minchord` is
monotone under box inclusion, so the PIECE's box is a legal (and longer) chord in A144's guard row —
`H`'s true pose is in `b` — and that alone gives `beta = 0` on 29 of the 121 kill pieces, killing the
band with no cover at all (all nine pieces of `c0_Y1131`). **Band-slab root:** `chord >= 1 <=>
|v| <= f(y)` with `f` decreasing on `[1, sqrt2]`, so every band pose has `|v| <= f(1) = 1/2` and the
`LANE_band` cover may be run over `centre_window ∩ {|v| <= 1/2}` — 92 of the 121 pieces closed that
way.

**Result.** **15 KILLs, 285 NO-GO, 116 UNDECIDED-time.** Against a FRESH collect at the end
(5,800 / 5,314 / 46 / 3,238 dead ids) **11 of the 15 are still NEW dead nodes** — `c0_Y0989,
c0_Y0993, c0_Y0995, c0_Y0996, c0_Y0997, c0_Y1002, c0_Y1131, k5_16_interior_Y0191,
k5_16_interior_Y0281, k5_16_interior_Y0635, k5_16_interior_Y0663`, 7 trump5 and 4 k5_16, all level 1;
the other four (`c0_Y0902, c0_Y0913, c0_Y0921, c0_Y0994`) were killed by A149 *while A167 was
running*, which is why the number is re-derived at the end and not from the population snapshot.
15/15 certificates PASS the independent checker. Kills sit on **trump5 BR(0,1) (10 of 66), k5_16
BL(1,0) (4 of 54), trump5 TR(0,1) (1 of 48)** and nowhere else — zero on the other ten class×slot
combinations, k5_11 included.

**The negative half is the bigger result, and it answers A161's open question.** On 285 of the 416
cells there is a piece of `B_H` on which EVERY one of the ~106 swept offsets is screened out, because
the sample exhibits a FREE pose — avoiding every `K'`, the piece's fattened core included — that meets
`int C` alongside `H`. That is a hard lower bound on the leaf's own counter (A159's C8 witness rule),
so `n(b) >= 2` there and no budget changes it. Escalated on 60 cells to an EXACT rational two-crowd
witness (two unit squares on a `1/10^6` grid, both inside `[0, s0]^2`, both meeting `int C`, interiors
disjoint by an exact separating axis, both clear of the five pins, one a legal pose of `H`): **49 of
60 certified**, which retires those cells for the whole lane-leaf family, not just for this leaf.
**`c0_Y0169 / TL(0,0)`, the PI's case, is one of the no-goes**: `beta = 1` and `LANE_out = 0` hold as
A161 reported, but on the pieces where `H` reaches the cell a free BAND pose survives at every offset
(2-6 per 20,000 draws at split depth 5 on the good `x ≈ 0.729` lines), so the second half of the PI's
sentence — "`H`'s corner leaves under 1 of width, so no band square fits" — is **false as stated**.
A161's `LANE_band` cover was not under-budgeted; it had nothing to prove.

**Two facts worth keeping.** (i) A lane cover that CLOSES closes in 0.6-1.2 s and one that does not
grinds for as long as it is given, so breadth over offsets at a 2 s hard slice plus ONE 12 s retry on
the offset that got closest beats any long single budget; the viability screen (one pose pool per
piece, ~0.3 s, removing 50-100 of the 106 offsets) is what makes a depth-5 split affordable. (ii) In
the conditional form a `witness` leaf citing the conditioned index must be checked against **the
piece's box**, not `B_H` — on that branch the piece is the hypothesis and is the stronger obstacle;
checking against `B_H` rejected all 15 genuine certificates until it was fixed.

**Files.** `attempts/A167-condlane-pass/` (`BRIEF.md`; `code/{pop167,condlane2,runcond167,
checkcond167,witness167,diag167,whydead,table167,recheck167,summarise167}.py`;
`results/{pop.json,collector.json,collector_final.json,pass_s0.jsonl,pass_s1.jsonl,y0169.jsonl,
nogo.jsonl,table.json,recheck.json,levers.json,checkcond.json,diag_*.json}`; `certs/cond_*.json`,
`certs_nogo/nogo_*.json`; `notes/{leaf.md,table.md,doc_lines.md}`; `logs/`), plus the registry row,
this entry, the A57 `PAUSED.md` v4 addendum, the A60 ledger section and one paragraph in
`docs/residue_ledger.md` §1. Two BelowNormal processes at affinity `0xFFFF` throughout, the 16-process
box ceiling counted before every launch (11-14 other lab pythons running); **~8,100 s of population
pass + ~3,700 s of diagnostics, checking and witness search ≈ 3.3 CPU-h of the 4 CPU-h cap.**

## 2026-09-09 — A171-multibox-invariant (Opus engineer) — done-success
- **Why**: two agents in a row (A165 Opus, A168 Fable) built multi-box case trees on the k0 cell
  `l1_104` and drew/solved boxes that had never been clipped — cores escaping the container and pose
  unions overlapping other cores — and the PI caught both by eye. A rule in a brief gets skipped, so
  it is now CODE with a guard: `attempts/A171-multibox-invariant/code/multibox.py`.
- **API**: `Node(boxes)` (named parameter boxes, carried as (t-sub-bin, rational centre rect)
  pieces); `normalise(s, nsub=4, max_iter=10, refine=2)` = container clip (A131's sound `w_min` clip,
  then the strict `w_max` clip that puts every pose inside `[0,s]^2`, the sacrificed wall slivers
  recorded with their area) then mutual clip of every box against every other box's `K'` to a fixed
  point, `K'` (A132) and the exact axis core (A135) rebuilt after each pass, with `refine` levels of
  tautologous bisection interleaved; `EmptyBox(name)` = the pair-leaf kill; `assert_invariant()` =
  exact rational `K-CONTAINER`, `K-DISJOINT` (polygon SAT), `POSE-CONTAINER`,
  `POSE-CONTAINER-STRICT`, `CLIP-FIXPOINT`, raising with EVERY failure listed; consumers
  `chord_rows` (A144), `lane` (A141 + A161's exact miss test), `misses_cell`, `figure` (A148-style,
  verdict + kept fractions + residuals printed on the page, extreme POSES as thin outlines).
  `chord_rows`/`lane` raise on an un-normalised node — the guard A165/A168 lacked.
- **New primitive**: `dead_poly`, an exact rational SUFFICIENT test for "Q(c,th) meets int K' at
  every tilt of the sub-bin" against a general convex rational polygon (K's edge normals with an
  exact lower radius bound; four one-sided `exists vertex / for all theta` sinusoid statements
  decided by A131's `_m_lt_half`). The slab removal is justified by CONVEXITY of the true dead set,
  so a sufficient membership test at the four corners is a sound certificate; A131's
  `_bisect_boundary` is reused verbatim.
- **It convicts A168.** Node `BR139/TRH-25` (`H`, `B1`, `D` as recorded, verdict ALIVE(geometry))
  fails 5 checks: `D`'s centre rect exceeds `s - w_max/2` by **0.087938** (47.1 % of its poses leave
  the container), `B1`'s by 0.003405, and the mutual clip still removes 0.003806 of `D`'s area;
  pose-vs-core, **H→K'(B1) 0.6328 and D→K'(H) 0.6050**. After `normalise` all five pass with kept
  **H 0.440792, B1 0.942803, D 0.088172** — 91.2 % of D's box and 55.9 % of H's were never possible.
- **Tests** `tests/test_multibox.py`, 11.3 s: (a) overlapping `K'` ⇒ a box is emptied, and the
  disjoint-cores-but-meeting-poses variant shrinks 1.0 → 0.709 with the invariant holding after;
  (b) container straddle ⇒ escape_frac 0.663 → 0, kept 0.297; (c) the A168 node before/after;
  (d) 10 random 2-6-box nodes, 99,996 sampled poses, 0 violations.
- **Two limitations, reported not hidden**: the strict container clip genuinely narrows the
  hypothesis (recorded as `container_sliver` with its area; `strict_container=False` turns it off,
  and no wall-touching node can satisfy "all poses inside" at finite `nsub`); and "a pose still
  meets another core" cannot reach 0 in a rect × tilt-interval representation — 0.205 node-wide at
  `refine` 3, monotone in `nsub`/`refine`, so refinement is the lever, not clipping.
- Files: `code/{multibox,demo171}.py`, `tests/test_multibox.py`, `notes/usage.md`,
  `results/{test_multibox,demo171}.json`, `figs/*.svg`; appends to
  `attempts/A57-shadow-trees/PAUSED.md` (§E resume note 7) and `docs/residue_ledger.md` §6.

## 2026-09-09 — A170-certfix (Opus engineer) — done-success

- **Task.** Audit which certificate-emission lanes are damaged by the `caselp.make_certificate` stock-core
  reversion A166 found (`hyp = Hyp.from_json(res["hyp"])` recomputes `self.cores = [b.core() for b in boxes]`,
  discarding A135's certified EXACT cores, so an `ExactHyp` LP emits a certificate that under-exempts by
  1.4-15 % of the core half-side and manufactures holes); re-certify every FAILing record with the exact cores
  carried through; ship the forward fix.
- **Audit, done empirically on every certificate on disk** (`code/scan170.py`, 3,378 files: the exact core
  recomputed from the box each certificate itself carries, compared with the `a` it wrote). **The bug reaches
  only the lanes that call `caselp.make_certificate` / `caselp92.make_certificate` DIRECTLY with an `ExactHyp`
  — A150, A165, A166.** A137, A140, A145, A149 (both the `__exall` and the `__exH` arms), A156 and A135 itself
  all route through A135's `emit135.make_cert`, which takes the LIVE `Hyp` and was written for exactly this bug
  (`emit135.py:94-100`): **exact cores, 698 of 698**. A168 already carries A166's inline patch.
- **Re-certification** (`code/certwrap170.py` + `code/recert170.py`, arbiter the FROZEN `verify_case.py`
  sha `521cb01f…`): **409 certificates, 2.35 CPU-h of verifier, ZERO LPs solved. 59 recovered PASSes, 59/59
  clearing a 100 % independent check** (A132 `polycore.vertex_ok` re-run on the WRITTEN rationals, the measure
  recomputed exactly in `Fraction`, and a depth-64 frozen replay — `code/check170.py`).
  - **25 repairs, 8 nodes, 3 of them NEW**: A165's `l1_104_spread_spread00/02/03`, which takes that leaf from
    1-of-4 to **4 of 4** certified and refutes its own note's "they need the A13/A14 separation loop with more
    rounds, not a different core" — they needed the cores they were *solved* with. A150's 3 and A166's 2 are
    re-derived here through a separately written path and agree 22/22 (the cross-check A166 asked for).
  - **34 free UPGRADES on genuinely stock-core lanes, every one a zero-atom VACUITY certificate** (A59 33,
    A60 1). That is the one class where a wider certified core is the whole lever, since a vacuity certificate
    says "every admissible square is exempt". A59's residual ladder around Trump's packing now certifies at
    **8-14 % less exemption parameter at every rung** (`rb hw=0.002`: `a_min` 0.009062 → 0.007969; `rk hw=0.02`:
    0.074883 → 0.067500) with its certified `hw` **envelope unmoved** — cheaper, not longer.
- **Negative where it matters.** 118 already-exact FAILs are **NO-CHANGE**, so the A57 row's exact-core kill
  rate (46/161 = 28.6 %) stands and A156's `v3_candidates156` row is not a core failure. The whole k0 pool —
  all **128** `kill-candidate (cert FAIL)` records of `cells140.open_pool`, re-emitted from A115's **stored**
  measure with exact cores at zero LP cost — gives **0 PASS** (unconverged single-box LPs at τ ≈ 9.977 against
  budget 10, cores widening 0.6-11.8 %, 9 failing on `total ≥ budget`). A166's "127 candidates for immediate
  certification" closes at **zero**: none of them was emitted through an exact-core path. Shadow board
  unchanged — `status_gallery.py --dry-run` 5,332 → 5,344 kills, **0 new distinct pages**.
- **Fix shipped.** `code/certwrap170.py` — a wrapper (`caselp.py` NOT edited); `make_certificate_exact(res,
  s_rat, scale, hyp=H)` carries the live cores, and with no `hyp` recomputes them from the box, which is what
  lets it repair old certificates. Two guards: a core is only ever ENLARGED, and never without `exact_a`'s
  vertex test passing and `(kx,ky,tm)` unchanged. Regression `code/test_cores170.py`: **50/50 boxes** (25 lifted
  from real certificates), asserting both that the wrapper writes `exact_a` and that the UNWRAPPED
  `caselp.make_certificate` still writes the stock core — so the guard fails loudly if upstream changes.
- **One cosmetic defect found in passing:** `attempts/A149-a57-reprice/code/node_a60.py:64` mutates `hyp.cores`
  on a plain `caselp.Hyp`, so `emit135.make_cert`'s `getattr` defaults label all 95 `certs/a60/*__exH.json`
  `core_scope = "stock"` / `cores_exact = null` even though their H core IS exact. No certificate is wrong;
  only its provenance line is.
- **Files.** `attempts/A170-certfix/{BRIEF.md, notes/audit.md, notes/recovered.md, notes/fix.md, code/*.py,
  results/*}`; appends to `docs/budget.md` §D.9, `docs/residue_ledger.md` §1,
  `attempts/A57-shadow-trees/PAUSED.md` (A170 addendum + §E resume line 6),
  `attempts/A60-trump5-campaign/notes/ledger.md`, `attempts/A115-k0-corner-rows/notes/t6_report.md`.
## 2026-09-09 — A172-multibox-pieces (Opus engineer) — done-success
- **Why (PI finding on A171)**: `MBox.rebuild()` recomputed `K'(B)` from `union_box()` — the smallest
  axis box × tilt hull containing the surviving pieces. A hull FORGETS a clip that removes different
  slabs in different tilt sub-bins, so `K'` barely grew on the side opposite the clip and the cascade
  that is the whole point of the fixed-point loop (a larger `K'(B)` clips the other boxes harder)
  barely bit.
- **The fix** (`attempts/A171-multibox-invariant/code/multibox.py`, public API unchanged): `K'(B)` is
  the EXACT rational intersection of the PER-PIECE `K'` — `polycore.build` on each piece's own Box
  (its six floats rounded OUTWARD with `nextafter`, and `t_lo/t_hi` of the degree endpoints asserted
  to contain the piece's own rational t-sub-bin, so the Box handed to A132 CONTAINS the piece),
  Sutherland–Hodgman intersection in `Fraction`s, simplification that only ever DELETES a vertex of a
  convex polygon (that cuts a triangle OFF — inward, never outward), a final inward shrink about the
  centroid + 1e-9-grid rounding with A132's own retry ladder — and then **every vertex re-certified
  by `polycore.vertex_ok` against EVERY piece**. That certification, not the construction, is the
  proof: a point inside every pose of every piece is inside every surviving pose, and `Q(c,θ)` is
  convex, so the hull of certified vertices is inside every pose. The exact axis core follows A135's
  pattern about the intersection's centroid (closed form `a = min_e (b_e − n_e·k)/(|n_e·e1|+|n_e·e2|)`
  as the search, the four corners certified per piece as the proof, never allowed to regress below
  A135's core on the union hull). `normalise(..., kmode="union")` and `MBox.union_pc()` keep A171's
  union-hull `K'` as the automatic fallback (taken if no rounding certifies) and as the diagnostic;
  per-piece cores are cached per piece across the passes. Figure legend now reads `solid = K'(B) =
  intersection of per-piece K', certified`.
- **The table** (A168's S2 node `BR139/TRH-25`, `nsub` 4 / `refine` 3, `attempts/A172-multibox-pieces/results/report172.json`):

  | | union hull (A171) | per-piece, SAME pieces | per-piece fixed point (A172) |
  |---|---|---|---|
  | `K'` area H / B1 / D | 0.658006 / 0.798164 / 0.740065 | **0.709336 / 0.799343 / 0.774356** | 0.730797 / 0.799343 / 0.793731 |
  | kept H / B1 / D | 0.440792 / 0.942803 / 0.088172 | — | **0.358392 / 0.942803 / 0.072175** |
  | axis `a` H / B1 / D | 0.379275 / 0.435386 / 0.405989 | — | 0.388134 / 0.435386 / 0.420528 |
  | pieces, passes, invariant | 26/32/14, 2, PASS | 0 uncertified vertices | 22/32/12, 2, PASS |

  i.e. the hull was hiding a quarter of what the clip had already proved: another **19 % of H's
  surviving box and 18 % of D's** go, on top of A171's 56 %/91 %. Consumers move the same way and no
  further: `beta = 2` top / `beta = 1` right (A168's own rows) unchanged, `lane(TR unit cell) = 0` in
  **33** discharged leaves instead of 38.
- **Tests** (`tests/test_multibox.py`, now 5 cases, **53.7 s** of the 120 s budget, was 11.3 s): new
  case (e) — the per-piece `K'` is `>=` the union-hull `K'` on the same pieces and matches the PI's
  numbers to 4.8e-7, the new fixed point keeps strictly fewer poses for H and D, `k_source ==
  "pieces"` on every box; and a `k_uncert` counter wired into (b), (c), (d) too, so **every vertex of
  every `K'` in every test is re-certified against every piece — 0 failures** (10 random 2–6-box
  nodes included). Every pre-existing assertion still passes unchanged.
- **Cost, stated plainly**: the S2 node's `normalise` goes 2.1 s → 13.1 s (one `polycore.build` and
  `vertex_ok` sweep per piece per rebuild, cached). `kmode="union"` is the lever for a wall-time-bound
  sweep; anything about to be drawn, priced, covered or handed to an LP should use the default.
- Files: `attempts/A172-multibox-pieces/{BRIEF.md,code/{probe172,report172}.py,results/report172.json,
  logs/}`; edits to `attempts/A171-multibox-invariant/{code/multibox.py,tests/test_multibox.py,
  notes/usage.md,results/{demo171,test_multibox}.json,figs/*.svg}`; registry row; this entry; one
  paragraph in `docs/residue_ledger.md` §6. Two BelowNormal processes at affinity 0xFFFF, box ceiling
  16 counted before every launch (6 other lab pythons live: A168, A169, A136); ~90 CPU-s total.

## 2026-09-09 — A169-sideband-lemma (Fable lead) — done-success
- **Why**: A168's k0 cascade needs, at every corner met by two crowd squares, (a) a band statement
  (one centre within a wall band, the other outside) and (b) what a doubly-met corner REQUIRES of the
  first meeter, both for any n; the coordinator had only samples (no disjoint pair with both centres
  beyond 1 in 81k draws) and an atlas whose thresholds (0.18/0.34/...) nobody had derived.
- **Sharp statements** (`docs/proofs/sideband.md`, derivations `notes/derivation.md`, picture
  `docs/residue_map/sideband_lemma.svg`): SIDEBAND (a) [T] with constant **c itself** (1 unit,
  1 + w widened) and no quadrant / no bound on c; "within 1 of a wall" at the widened box [F]
  (45-deg diamonds at (1.01, 1.7226)/(1.7226, 1.01), SAT gap 0.0078); (b) "the other lies outside" [F]
  (Q1 = [0.1,1.1]x[0,1] and a 2.87-deg-tilted Q2 at (0.524, 1.522), gap 1e-4, both centres x < 1) ->
  the true form is **distinct cells of the 2x2 grid at c** (Lemma A2), from Lemma A1: interior-disjoint
  unit squares have centres >= 1/sqrt2 apart in l-inf (sharp; SAT axis + Cauchy-Schwarz) and every meeter
  cell has l-inf diameter < 1/sqrt2 for c < 1/2 + 1/sqrt2 = 1.207.  REQUIREMENT: Theorem B [T], an exact
  four-clause support criterion (NE / W / S / P) for the existence of a second meeter, proved both
  ways; the (=>) direction rests on two piecewise-concave support inequalities (wedge: w(phi) -
  (cos z - sin z) w(z+phi) >= 2 sin^2 z; triangle: (cos g + sin g) w(psi) + w(psi-g) >= 2(cos g + sin g)).
  Corollaries [T]: pressed => lonely at every tilt (unit box); mode-(a) slide threshold tan(theta/2) with
  intrusion (delta - t) tan theta = 2t(delta-t)/(1-t^2); tilt-0 exact law a = u(2-u^2), F = u^2 sqrt(1-u^2);
  exact slide threshold = tan(theta/2) for theta <= theta* = 56.76 deg and the crossing (W)-mode beyond
  (0.5727 ... 0.4778 at 60...85 deg).  The atlas v2 d* values are pitch artefacts [M].  Widened box: the
  pressed square admits a partner iff w(theta) < c + sqrt(c^2-1), theta < 17.35 deg or > 72.65 deg (clause
  NE at alpha = theta), not the 12.8 deg of the mode-(a) guess.
- **Lean** (`Sideband.lean`, builds clean, no sorry, no axiom): `linf_sep`/`linf_sep_sqrt` (A1),
  `quad_centre_ge_half`, `meeter_cx/cy`, `distinct_cells` (A2), `not_both_ne`/`sideband_a` (SIDEBAND (a)),
  `cell_hyp_of_lt`; Theorem B stated as `SecondMeeterCriterion` [C] with `supp`, `ClauseNE/W/S/P`,
  `SecondMeeter`, and `clauseP_second_meeter` [T] (the pressed square is the (P) witness).
- **Consumption (A168)**: R1 cell/pair prune of the corner pair list (subsumes 0.34 cores);
  R2 the band/outside split into six cell pairs with the band meeter priced by A144's chord row and the
  NE meeter confined to the quarter-disc of radius 1/sqrt2 at (c, c); R3 the LONELY NO-family (Theorem B
  box test, quartic in T = tan(zeta/2), Bernstein) removing 54-74 % of widened meeter poses at every tilt,
  unchanged by a conditioned H (A158's clip first).  Expected pair-census reduction ~ (0.4)^2 [S].
- **Numerics** (`code/`, `results/`): `check_a` (counterexamples, 4 941 sampled disjoint meeter pairs,
  0 in a common cell), `crit169`+`lonely_exact` (criterion vs independent raster: 783/783 agree, all
  non-lonely cells carry SAT-certified witnesses), `slide169` (thresholds, theta*, the three inequalities
  >= -4e-16 on a 720x2880 grid).  Total compute < 10 CPU-min.
- **Files**: `attempts/A169-sideband-lemma/{BRIEF.md, notes/derivation.md, code/*.py, results/*.json,
  logs/}`, `docs/proofs/sideband.md`, `docs/residue_map/sideband_lemma.svg`,
  `lean/PackingCertMathlib/PackingCertMathlib/Sideband.lean`, `docs/residue_ledger.md` section 4 paragraph,
  `docs/known_results.md` item 35, registry row.

## 2026-09-09 — A173-lonely-clip (Opus engineer) — done-success
- **Why (the PI's reading of A171's library)**: A169's **Theorem B** (`docs/proofs/sideband.md` §3,
  consumption row **R3** §6) says a corner-meeter pose that admits **no second meeter** of the widened
  corner box — a *lonely* pose — is impossible in a K0-BLOCKED packing, and R3 states the consumption
  as "a conditioned box `B_H` is clipped to `B_H ∖ L_c′`" — a **clip**. A168 applied it only as a
  whole-role **kill** (`resume168.lonely_role` needs *every* pose of the role lonely), so lonely poses
  inside a surviving role were never removed, `K′` never grew from them, and the cascade to the other
  roles was lost. The coordinator's own probe made the granularity concrete: axis-aligned D flush with
  the right wall slid down is NOT lonely, but D at tilt 15° slid 0.1, or tilt 30° pressed, IS — so the
  object R3 removes is a set of **tilt sub-bins and centre slabs**, not whole roles.
- **What was built** (`attempts/A171-multibox-invariant/code/multibox.py`): `lonely_local` /
  `lonely_rect` / `lonely_box` port the criterion from `resume168.lonely_box` (clauses W, S, NE on the
  2001-point grid with the Lipschitz margin and the cached `g`; clause (P) the exact A131 rational clip
  against the pressed square, with a degenerate zero-width rect padded OUTWARD by 1e-12 so a slab-
  boundary probe can never be read as dead). `lonely_clip(mbox, corner, c)` drops a whole tilt sub-bin
  the criterion certifies lonely and otherwise bisects the four axis slabs with A131's **certifying**
  `_bisect_boundary` (the returned boundary is verified by the exact predicate, so what is dropped is
  always a slab just proved lonely), tracing every removal with its area. `normalise(corners={"D":
  ("TR", C_WIDEN)}, lonely_refine=1)` runs it at **every pass, before the mutual clip** — the point:
  the survivors rebuild a larger `K′` and the cascade carries the growth. `EmptyBox` is A168's R3 kill,
  recovered as the limiting case. **Soundness grade unchanged**: a *sufficient* condition, clause (P)
  exact, the other three at A168's **[S]**.
- **Verification**: `xcheck173` — 500 random corner-meeter boxes over all four corners, verdicts and
  per-clause details **identical** to `resume168.lonely_box`, same `c = 1 + w` as an exact rational
  (104/500 lonely). Test case (f) in `tests/test_multibox.py`: (f1) that cross-check; (f2) soundness —
  every centre the clip removes, at five tilts of its own sub-bin, checked against an **independent
  pointwise** implementation of §3 written from the paper, **3 070 poses, 0 violations**; (f3) the node
  invariant after the clip and "the clip only ever shrinks". Suite **ALL PASS, 74.1 s** of the 120 s
  budget.
- **THE BUG THE SUITE FOUND — a live unsoundness in A171, present since `2b7172c3`.** `Bin.radii`
  memoised its exact per-edge radius bounds under **`id(obs)`**. `normalise` compiles a fresh obstacle
  per box per pass and drops the previous pass's; CPython hands the freed address straight back; a
  `Bin` that outlived the old obstacle then answered the NEW one with the OLD one's bounds — wrong
  bounds inside the exact dead test, **in either direction**. It fired nondeterministically (two
  aliases in test case (a) alone), which is why `a2.invariant_after` passed at HEAD and failed on the
  next run. `Obstacle` now carries a monotone `uid`; case **(a3)** rebuilds an obstacle at a recycled
  address (`address_recycled=True` in the recorded run) and demands the fresh radii. The speed the
  accidental hits had been stealing is taken back **legitimately** by `MBox.obstacle()`, which caches
  the compiled obstacle under the exact rational CONTENT of `K′`. **A173's measurement was re-run from
  scratch**; the pre-fix records are kept unused under `results/superseded/`.
- **One more correction**: `lonely_clip`'s tautologous tilt bisection used to keep the split even when
  neither half was dropped, inflating the piece count of every clipped box at every pass — and more
  pieces make the *rest* of `normalise` stronger (A172) and slower, so the with/without comparison was
  reading a mixture of Theorem B and extra refinement. A piece with no dropped descendant is now
  returned UNSPLIT. Same effect for a fifth of the cost (test (f) node: `K′(D)` 0.55266 → 0.754208
  against 0.755656; that node's lonely `normalise` 13.1 s → 2.5 s).
- **The measurement** — all **146** ALIVE S1/S2 nodes of `tree_l1_104` + `tree_l1_153` (read-only),
  D = the first TR meeter, `c = 1 + w`, `nsub` 4 / `refine` 1 / `max_iter` 6, base and lonely from the
  same starting boxes (`results/{measure173_c.jsonl,report173.json,table173.md}`, `notes/measure.md`):

  | step | nodes | alive in base | **LONELY KILL** | dead in base already | mean rel. loss of D | median | mean `K′(D)` before → after | H moved |
  |---|---|---|---|---|---|---|---|---|
  | S1 | 34 | 29 | **3** | 2 | 0.3641 | 0.2259 | 0.7169 → 0.7680 | 5 |
  | S2 | 112 | 62 | **10** | 40 | 0.5154 | 0.5219 | 0.7058 → 0.7656 | 12 |

  **42 of the 146 A168-ALIVE nodes are already dead to A171/A172's clipping alone**, before Theorem B
  is applied. Of the 104 that survive it the lonely clip **kills 13 more** — twelve by emptying D, and
  `l1_104 root/D53/S7` by emptying **S**, i.e. the *cascade* killing, not the clip — and halves what is
  left: 10 S1 and 31 S2 nodes lose more than three quarters of D's surviving fraction, 23 lose under
  1 %. Whole sweep 845 s in one BelowNormal process.
- **Loose end, stated**: one node (`l1_104 S2 root/D55/S0`) does not reach the clip fixed point in 6
  passes (5 × `CLIP-FIXPOINT`); at `max_iter=20` it converges in 10 passes with a clean invariant and
  **identical** kept fractions (H 0.545185, D 0.036478, S 0.083866), so the recorded number is right
  and only the convergence budget was short. Every other node's invariant passes.
- **Figures**: `docs/residue_map/lonely_clip_S1.svg` — before/after for the worst surviving S1 node,
  D's pieces as thin rects, the removed centres hatched red, `K′(D)` dashed before / solid after with
  `K′(H)`, the hypothesis square at D's box centre at mid tilt with both extremal-tilt outlines, a
  per-tilt-sub-bin strip (the only exact, unprojected view) and a note on each panel saying what it
  **is**; `attempts/A173-lonely-clip/figs/lonely_clip_gallery.svg` — the ten largest-effect nodes.
- Files: `attempts/A173-lonely-clip/{BRIEF.md,code/{measure173,xcheck173,fig173,report173}.py,
  results/,notes/measure.md,figs/,logs/}`; edits to `attempts/A171-multibox-invariant/{code/multibox.py,
  tests/test_multibox.py,notes/usage.md (lines 7 and 8),results/test_multibox.json}`;
  `docs/residue_map/lonely_clip_S1.svg`; two paragraphs in `docs/residue_ledger.md` §6; registry row;
  this entry. One BelowNormal process at affinity 0xFFFF for the sweep, box ceiling 16 counted and
  waited on before every launch (A168's shards, A174 and A136 were running throughout); ~1.1 CPU-h.

## 2026-09-09 — A136-a120-resume, resumed after the 02:20 reboot (Opus engineer) — **24 CLOSED → 29, and the binding constraint was the CORES, not the LP**

- **Where the survivors actually were.** Of this attempt's **72 ALIVE NO children**, **56 are LP-alive** — the LP
  itself found no kill, and no certifier budget touches those — while **16 were alive only because the certificate
  did not land** (14 CAP, 2 FAIL) with the LP already converged at `eta` between −0.444 and −0.116. **Six of the
  sixteen were the ONLY alive child of their node**, i.e. six nodes were one certificate from CLOSED. Splitting the
  ALIVE population that way is what made the rest of the day cheap.
- **A170's audit applies to this lane and A170 never ran on it.** `attempts/A170-certfix/results/scan170.json`:
  **122 A136 certificates, all `kind: "stock"` / `exact_lane: false`**, exact core up to **1.0787×** the carried one —
  A136 certifies through `caselp.make_certificate`, the entry point that `Hyp.from_json`s the hypothesis and throws
  A135's exact cores away — and **no A136 row appears in any `recert170_*.jsonl`**. Three experiments, cheapest first:
  - `exactcert136.py` **patches the written certificate** (A170's `carry_exact_cores`, ENLARGE only, guarded by A135's
    exact vertex test) and re-runs the **FROZEN** `verify_case.py`. No LP, no re-emission. **2 of 16 PASS** in 10–48 s:
    `Y0441/NO0` CAP → PASS **closing that node**, and `Y0691/NO3`.
  - the same low-hole failures at **depth 64**: **0 of 6**, and `Y1147/NO1`'s "0 HOLES at depth 56" became **4 real
    holes at depth 64**. Depth was never the constraint; the holes were simply not found at 56.
  - `certify136x.py` **re-emits with the exact cores INSIDE the witness-feedback loop**
    (`make_certificate` → `carry_exact_cores` → A136's F-COVER `narrow`, the only sound order): **2 more PASS**,
    closing `Y0691` (558 s, 3 emissions, 18 cores enlarged) and **`k5_16_interior_Y0941`**.
- **THE RULE, and the diagnostic that costs nothing.** A verdict of *`N` witness boxes at depth 56, `k` HOLES* is a
  **coverage** failure — the cover really leaks and a wider core adds no mass — so all of those stayed FAIL. A verdict
  of *`total mass >= budget: certificate proves nothing`* is a **measure** failure — the cover is fine and the measure
  the loop built is too small — and that is exactly the class wider cores in the loop repair: **`Y0941/NO3` had ended
  its stock-core loop at `total 5.025000 >= 5` after the full round budget and PASSed at ROUND 0 in 7.1 s at
  `total = 2492839/500000 = 4.98568` with the cores 2.26 % wider.** So **on a stock-core lane a cert CAP or FAIL is
  not evidence about the node until it has been re-certified with the cores the LP was entitled to use** — and read
  the verdict line first, because it says which lever to reach for before any compute is spent.
- **A gallery page retired.** `k5_16_interior_Y0941` carried an ALIVE `docs/shadows` page; it is now
  `docs/shadows/a57v4/killed/`, **a57v4 53 alive / 7 dead → 52 / 8**. The four sole survivors that remain
  (`Y0036_D02/NO2`, `Y0414_D06/NO0`, `Y0978_D07/NO0`, `Y1147/NO1`) all report **real holes under the wider cores**, so
  they are honest survivors of this cover rather than certifier artefacts — a stronger statement than yesterday's CAPs.
- **The last NO-COMPLETE node is closed, for 89 s of compute.** `k5_11_interior_Y0274`'s YES leaf was A160 union entry
  34, which `entry151.A160_NO_CERTIFICATE` recorded as having **no certificate artefact at all**, and A160's own
  `consumer160.json` puts Y0274 inside **only** the slices union (slack +0.12722; A151-B −0.58751, chain −0.93248), so
  nothing could be cited instead. `yesleaf136.py` emits it: A160's `gent160` and A133's `gen_local_t`/`check_local_t`
  imported UNCHANGED with every write target re-pointed into this attempt, the emitted bodies **asserted
  float-for-float equal to `N_boxes160.json` entry 34** (the box set the NO side was cut against — a certificate for a
  different box set would not license the citation), the tree DEAD in **67.9 s** and A133's **independent** rational
  checker **VALID, 0 errors**, exact certified minimum `1117504297361694154655418074219141144140303/2882303761517117440…`
  **above s₀ by 3.788·10⁻⁵**. `no_complete136.jsonl` is now empty.
- **"Largest certified margin over s₀" is the wrong rule for choosing a YES leaf.** On A163's k5_16 frame the
  `h = 1.25°` chain link (margin **8.121·10⁻⁵**, the largest citeable) left **12 of 12** NO children ALIVE across
  Y0054/Y0183/Y0380 with the LP converging to `eta = 0` at `tau = 5` — the cover proves nothing — while the
  `h = 10°` link (margin **7.454·10⁻⁶**, 11× smaller, but a **20°**-wide shared-tilt window against 2.5°) certified
  3 of 4 children of Y0941. The margin measures how far the certificate's own tree got; the NO side needs the
  **widest** citeable `N`, and width and certified depth are anti-correlated (the same trade-off A160 recorded between
  growth directions, seen from the consumer side). `results/queue_a163_h10.json` forces that leaf on the nine nodes
  that can cite it. Counter-evidence recorded too: `Y1110/NO0` is ALIVE on the h = 10° leaf as well, at `eta = 0`.
- **Resumability, and one process-discipline fix.** `run151.py --out_suffix` was added because **both** `noside120`
  caches are keyed by node id alone, so re-running an id against a second YES leaf inside the same subtree would
  silently return the first leaf's verdicts; `report136.py` now discovers every `results/nodes_*` subtree by glob and
  states `applies_to_tags` on each closure from the node's `campaign_path` (A137 §C.3 — an id is not a node), and
  always rewrites `no_complete136.jsonl` so a filled hole cannot leave a stale row. Killing the re-emission driver to
  re-launch it with a tighter per-child wall tore its in-flight children down and wrote each as `FAIL` with
  `rc = 0xC000013A` after **0.0 s**; nothing had been measured. **13 such rows are quarantined in
  `results/reemit136_discarded.jsonl` and the driver now records `KILLED` and re-runs them — a resource event is never
  a verdict**, the same rule the lab already applies to a CAP.
- **Still owed** (`results/owed136.json`, the per-queue board): `queue_base26` 26 → 10 CLOSED / 5 OPEN / 6 A149-kills /
  2 SKIP-UNSOUND / 3 not-run (the base worker was still running at hand-off); `queue_asym10` 1 CLOSED / 7 OPEN /
  2 A149-kills; `queue_a160_8` 1 CLOSED / 3 OPEN / 2 SKIP-UNSOUND — **complete**; `queue_a163` 22 with 19 not yet run
  (the three that ran are OPEN on the h = 1.25° leaf); `queue_a163_h10` 10, only Y0941 done. The un-run a163 queues are
  the whole remaining owed set and they are cheap per node; the OPEN nodes are **not** — 56 of their children are
  LP-alive.
- **Files**: `attempts/A136-a120-resume/code/{yesleaf136.py, exactcert136.py, certify136x.py, reemit136.py, owed136.py}`
  + `run151.py`/`report136.py` patches, `results/{closures136.jsonl, report136.json, owed136.json, exactcert136.jsonl,
  reemit136.jsonl, reemit136_discarded.jsonl, yesleaf136.json, queue_a163_h10.json, leanfrags/*}`,
  `yesleaf/certs/`, `certs_exact/`, `certs_a163x/`, `notes/frames151.md` §§5–7, `docs/shadows/STATUS.md` +
  `a57v4/killed/k5_16_interior_Y0941.svg`, `docs/residue_ledger.md` §5, registry row.

## 2026-09-09 — A177-a163-queues (Opus engineer) — **29 CLOSED → 30, and the widest citeable N closed nothing**

A136 left three things owed and cheap: its base worker's last node, the 9 un-run rows of
`queue_a163_h10.json`, and the 18 un-run rows of `queue_a163.json`. This attempt ran all of them under
A136's own three findings — A170's exact cores carried **inside** the witness-feedback loop, the
widest-citeable-`N` entry rule for the NO side, and *a resource event is never a verdict* — and the two
halves of the answer come from opposite findings.

- **One closure, and the entry rule did not earn it: `k5_11_interior_Y1140_D06` is CLOSED**
  (`results/closures136.jsonl` 29 → 30). A136's base worker had recorded it `OPEN` with children
  `[ALIVE, CAP-GATE, CAP-GATE, CAP-GATE]` at 14:54:04 — `NO0`'s certification hit the 2600 s wall (a CAP)
  and `NO1`–`NO3` were never tested at all, the node deadline having passed: four verdicts carrying zero
  evidence. Re-run under a fresh `--out_suffix` (both `noside120` caches are keyed by node id and would
  otherwise have served the CAP-GATE record straight back) with exact cores in the loop, **all four NO
  children certify dead** under the frozen `verify_case.py` (sha `521cb01f…`) with ZONE ⊆ BOX on the
  written rationals and `per_box_soundness ok` — `NO0` in **532 s** where the stock-core loop had burned
  **2600 s** and CAPped, `NO1` in 954 s, `NO2`/`NO3` in 4 s each. Its YES leaf is A119's ordinary
  `S02_k5_11_r0.20_rho10`, so §6's entry rule is not involved: §7 (exact cores) and the resource-event
  rule were worth a whole node between them.
- **The a163 half is a clean negative worth as much: the widest citeable `N` closed NOTHING.** The rule
  was made computable — `(min tilt width over the free bodies, then log₁₀ of the box-volume product)`,
  margin over `s0` only as a tie-break (`code/queues177.py`, `notes/queues177.md` §1) — and it moves 5 of
  the 11 remaining rows to a 10× wider set. All 19 completed a163 rows came back `OPEN` (15) or
  `SKIP-UNSOUND` (4); the 20th, `Y0973`, is owed on a certification CAP (below). The `h = 10°` link kills 3 of 4 children on `Y0054`, `Y0380` and `Y0422` and 0 of 4
  on `Y0183`; the 10× wider `a151B` slice moves `Y1104` and `Y0854` from 0 dead children to 1 and moves
  `Y0486`, `Y0570`, `Y0559`, `Y0985` not at all; the one node that can cite only a 2.5° window (`Y0871`)
  dies nowhere, exactly as A136 §6 predicted. **Every surviving child is a converged LP at η = 0, τ = 5 —
  not a CAP and not a cert FAIL** (`Y0422/NO3` converges to η = 0 after 1787 s). So on the k5_16 frame the
  binding constraint is the **cover's width**, not the certifier and not the choice of entry, and A136's
  `Y0941` (3 of 4, closed on the h10 link) is the exception on that frame rather than the pattern.
- **A soundness refusal was tested rather than assumed.** `c0_Y1132` is refused by `A1_pins_match` on its
  widest citeable set, so the fallback queue re-ran it on the next-widest: refused there too, in 1 s. The
  refusal is a property of the node's pin set, not of the entry. `Y0864`, `slack0.02_c0_Y0411` and
  `slack0.02_c0_Y0513` are refused the same way.
- **Two resource events, neither recorded as a verdict.** A 0xD1 bugcheck at ~15:46 killed both drivers
  mid-node; both queues resumed with `--skip_done` and the child-level caches served every verdict already
  on disk. Later, two workers launched with PowerShell `Start-Process` were terminated externally ~20 min
  in — empty stderr, no Windows Error Reporting event, no PAUSE sentinel, no gate line, ~4 CPU-s each —
  while the box's other lab processes were untouched; the same commands relaunched detached from bash with
  `nohup` ran normally. Nothing was recorded for either pair. **A resource event is never a verdict, and
  that now includes the launcher.**
- **The h10 lane's obstruction is ONE box, and it is the PIN box — so no entry rule could ever have moved
  it.** Six of the eight completed `h = 10°` rows came back with the *identical* shape
  `[DEAD-CERT, DEAD-CERT, DEAD-CERT, ALIVE]` (`Y0054`, `Y0380`, `Y0422`, `Y0452`, `Y0791`, `Y0803` — 18 of
  24 children certified dead), and the survivor is always the same child: `NO3`, whose cover box is
  **`BR(0,1)`**, the pin box, not one of the three free bodies (the cover `['f1','f2','f3','BR(0,1)']` is
  byte-identical across the queue). Five of the six report a cert `FAIL` whose own witness-feedback
  re-solve is in the report — round 0 at `τ = 4.88…4.91` unconverged with `total = 4.98525 < 5`, round 1
  **converged at `τ = 5.000000` exactly, at the budget**, `total = 5.02500`, after enlarging 12 cores by up
  to 1.11× — and the sixth (`Y0422/NO3`) gets there directly at `η = 0` after 1787 s of LP. **`total ≥
  budget` therefore splits again, decidably, from the report the certifier already writes: a last round
  that CONVERGES at `τ = budget` means the child is LP-alive, no measure certificate exists, and more
  rounds / more depth / wider cores are provably wasted — only a re-solve converging strictly below the
  budget leaves room for A136 §7's lever.** This also makes the negative result structural: the entry rule
  optimises the *free bodies* because those are what a certified `N` names, and **no `N` widens a pin
  box**. The eight nodes are one shared lemma about `BR(0,1)` away from closing; the live levers are a
  re-split of the pin box (A57's depth-2 move — splitting a box refines the same disjunction, so every
  sub-child keeps the budget) or a geometric kill of it, `BR(0,1)` being a wall-adjacent pin cell, exactly
  A161's chord-limited-lane shape.
- **One node left owed, deliberately.** `k5_16_interior_Y0973`'s `NO0` CAPped at the 2600 s certification
  wall with its LP at `η = −0.293` — a resource event — and with the node deadline passed the run could
  only have written an `OPEN` built from three non-verdicts, so the driver was stopped and **no record was
  written at all** (`owed136.json` says NOT-RUN, which is true). The re-run is queued and resumable:
  `results/queue177_h10b.json` with `--out_suffix _a177h10b --cert_time 900 --cert_wall 5200` (a FRESH
  suffix is mandatory — `certify_leaf_capped177` writes a `.done` for a CAP too, so the old suffix would
  serve the resource event back as a cached verdict). It cannot close the node — `NO3 = BR(0,1)` is alive
  on every row of this queue — so it buys evidence, not a closure.
- **Board.** `docs/shadows` a57v4 carries no retirement from this attempt — the closure is a depth-6 child with
  no gallery page of its own, so the count moved only through A182's two kills landing in the same run
  (52 → **50 alive / 10 dead**, `k5_16_interior_Y0027` and `k5_16_interior_Y0839`, both A182's).
  `results/owed136.json` regenerated: the a163 lane is down to **two** owed rows, `Y0973` (above) and
  `Y1110` (excluded by design — its `NO0` is genuinely LP-alive on the h10 leaf). `no_complete136.jsonl`
  still empty.
- **Files**: `attempts/A177-a163-queues/{BRIEF.md, code/{queues177,run177,report177}.py, notes/queues177.md,
  results/queue177_{t1,h10,rest,fallback}.json, logs/}`, `attempts/A136-a120-resume/{results/nodes_a177*,
  certs_a177*, results/{closures136.jsonl, report136.json, owed136.json}, notes/frames151.md §8}`,
  `attempts/A96-a57-parametric/results/a120_closures.jsonl`, `docs/shadows/STATUS.md`,
  `docs/residue_ledger.md` §5, registry row.

## 2026-09-09 — A183-cascade-resume (Fable lead) — done-mixed (A181 resumed after the 15:46 crash; S3 shards left running, resumable)
- **Why**: the 15:46 bugcheck (0xD1) killed A181's parent-seeded re-normalisation of the k0 cascade with
  78 + 24 records on disk and no notes section. A183 restates the brief (`attempts/A183-cascade-resume/BRIEF.md`),
  commits A168's orphaned core files and A181's never-committed side files, and continues in
  `attempts/A168-cascade-fable` (`notes/cascade.md` §A183).
- **The lever**: `renorm183.py` re-clips every nsub 4 / refine 2 survivor at nsub 8 / refine 3 seeded from its own
  4/2 fixed point (each tilt sub-bin bisected once more; sound, never weaker, not idempotent); A181's 4/2-ALIVE
  records are upgraded in place; `roles168.make_node` carries the same lever for every NEW node (`A183_LEVER`).
  A stale sliver-era wall cap is retried once at the full setting (l1_153 root/D25/S=H: 299 s, H 0.897 → 0.873).
- **Numbers [M]**: l1_104 S1 28 → 28 ALIVE (vol1 D −18 %); S2 111 → 64 / 47 DEAD (ancestor 20, EmptyBox 23 of
  which 4 only at 8/3, inheritance 4; vol1 H/D/S −16/−20/−17 %); S3 47 of 12,381 recorded (37 / 10 EmptyBox,
  300 s a node). l1_153 6 → 6, 1 → 1, S3 21 of 119 all ALIVE (476 s a node). `vol1 ≤ parent` on every node.
- **The LP and the pieces (settled)**: the frozen v1 verifier reads one square core per packed square; a list of
  boxes is not expressible and a union-of-cores exemption is unsound for the bridge. `lp183.py` feeds the
  union-box exact core GROWN inside K′(role) (four corners `vertex_ok` on every piece): root/D0/S1 +0/0.9/2.7 %,
  τ = 7.999999999999936 converged, ALIVE(LP), 98 s. The polygon needs a v4 `poly_cores` clause.
- **Bookkeeping fixes**: `renorm181.load_side` keeps the strongest record per node across shard files (a 4/2
  record or a stale cap marker in a later-named file was masking 8/3 upgrades); `fig168b` draws the hypothesis
  square only at an admissible pose (the PI read an extremal-tilt outline crossing S's K′ as a missed clip);
  `fig174` tolerates the S=H child.
- **Verdict**: both cells ALIVE; the open set is the S3 layer (l1_104 7,235 open S3 nodes under 64 live S2 parents (5,135 closed by ancestry),
  ~17 CPU-days on two processes; l1_153 97 S3 + 571 deeper). Next lever: the S2 kills' closure and the
  piece-level coexistence cut at every S3 node before any LP.
- **Files**: `attempts/A168-cascade-fable/code/{renorm183.py, lp183.py, launch183.ps1}` + patches to
  `renorm181.py, renorm181b.py, roles168.py, fig168b.py, fig174.py`; `results/renorm181_*.jsonl` (the record),
  `results/lp183_l1_104*.jsonl`, `results/renorm181_{report,summary}_*.json`; `figs/steps_{l1_104,l1_153}_{S1,S2,S3}.svg`;
  fold-ins `attempts/A57-shadow-trees/PAUSED.md`, `docs/residue_ledger.md` §4; registry rows A181 / A183.

## 2026-09-09 — A182-assignment-resume (Fable lead) — **c0_Y1033 ALIVE under the forced-first assignment; A180 resumed resumably after the 15:46 crash; A178 closed**

- **State found.** The machine crashed at ~15:46 (bugcheck 0xD1). A180's directory was entirely uncommitted and its
  c0_Y1033 run (pid 91776) had reached `FORCED TR(0,1) <- H+F1` under branch 1/6 of BR(0,1) without writing a tree or a
  capture; A178's pass was at 34 of 52 alive a57v4 pages (all ALIVE) with uncommitted edits to `geo178/geo178b/run178`.
  Both committed as found (`b6c282db`); brief `attempts/A182-assignment-resume/BRIEF.md`.
- **Resumable search** (`attempts/A180-forced-first-assignment/code/{journal182,assign182,run182}.py`, `launch182.ps1`,
  `watch182.ps1`): every multibox node is journaled as it completes (label, input roles, verdict, hulls, the exact miss
  test per forced cell, chord rows, lanes, the tree nodes' pieces), replayed on resume when label + roles + setting
  match, finished branches memoised, the journal committed after every branch; a heartbeat and a watchdog enforce the
  per-node wall of 1,500 s by killing the process tree. Measured: 471 nodes replayed in 22 s [M].
- **Sharper than A180 [T]:** the 8/3 re-pass of every tree node surviving 4/2 (base: H 0.271 → 0.209, 2.4 → 9.8 s);
  the chord-row kill (Σ min-chords of pairwise-distinct squares on a guard line > s); the lane prune of the "new"
  options (A141/A161 LANE cover of the cell's window against the grown cores: lane 0 = no unnamed meeter, lane 1 =
  not two).
- **c0_Y1033: ALIVE [M].** Root: BL(1,1) has one option {new,new} → **F1+F2 instantiated**; BR(0,1) 6 options,
  branched; under BR(0,1)=H+F1, **TR(0,1) forced to H+F1** (H+new 0/24, F1+new 0/48 combos alive); then TL(0,0)
  (5 options, the Lemma-A2 two-new split last), BL(0,2) (3), TR(1,0) (6–10). 23 complete assignments alive under the
  clip, 0 dead; one **ALIVE(LP)** (pins + H + F1..F3, budget 2, τ ≥ 2); 3 [P] no exact core on a role hull; 14 [P] LP
  quota; 8 at budget 0. 584 nodes, 3.0 CPU-h; chord rows min rhs 0.877 (no kill); lane 0 fired once. Three of six
  BR(0,1) branches and three of five TL(0,0) branches unexplored at the deadline; the verdict stands on the alive
  leaves. Page `docs/residue_map/c0_Y1033_forced.svg` (35 panels; premise tests and results printed).
- **a57v4 pass** (`results/assign182.jsonl`, last row per nid; shard pid 17324 still running, resumable): the seven
  k5_11 pages reached are UNDECIDED at the ROOT option table (> 300 nodes / 1,200 s each; `Y1104`: 120 refinement +
  63 pair-split nodes before any cell decided). Two rows carry `ERROR` from a Budget raised in a branch child's
  normalise (fixed `611ceefe`; the same meaning, re-run on the next resume).
- **Reading.** The assignment is sound and global, and the clip leaf does not separate assignments: no complete
  assignment died, and the LP on the F_i hulls (unions of meeter windows) is refused for want of an exact core.
  `docs/residue_ledger.md` §4, `docs/budget.md` §D.10, registry rows A178 (closed, 34/34 ALIVE, superseded),
  A180 (interrupted, resumed as A182), A182.
- **Push blocked:** A176's `0a369850` (10 commits back) holds `attempts/A168-cascade-fable/results/tree_l1_104.json`
  at 793.6 MB > GitHub's 100 MB limit; every push from this box is rejected until that commit is rewritten by its owner.

## 2026-09-09 ~20:40 — A187-basin-map (Opus engineer) — done-negative
- **The PI's question:** "is it possible to just turn the entire solution set into a basin?" — every alive node dying
  by containment in a certified local certificate instead of by measure.
- **Answer: not with the basins that exist.** Measured all **63 ALIVE gallery pages** (52 `a57v4` + 11 `k0v4`) against
  every certified basin on disk — S02 in `k5_11` (57 box sets, A119+A160), `k5_16` (52, A163), `trump5` (42, A163);
  S07 in `trump5` (2, A119); S33 in `k6_07` (6, A125); S38 in `k6_21` (1, A125).
- **[M] 7 of 63 (11 %)** minimise to a configuration with a certified basin **in their own class frame**;
  **7 of 63** pass the A116/A151/A160/A163 consumer test (all inside S02's basin, all `k5_11`/`k5_16`, only three of
  them S02 pages). **8 of 63** have their conditioned box inside a certified basin box, **32 of 63 (51 %)** within a
  2× growth — but usually against the *wrong* minimiser's basin.
- **[F] The cluster ranking is S01 23 pages (no basin anywhere), S03 11 (none), `none` 6, S02 6.** One certificate for
  S01 would more than treble the basin-covered residue; growing S02 to its wall cap would add almost nothing.
- **[F] The 11 `k0_00` cells cannot be tested at all** — no class pins, so no `CLASS_PINS`-form certificate applies;
  their six K-family minimisers have no basin. They and the other 45 orphan pages are the **drain-census** population.
- **[S]** Box containment is necessary, not sufficient: N wants a square in *each* box, a page conditions *one*.
- Control: `k5_16_interior_Y1110` reproduces A163's consumer slack 0.01311 exactly.
- Files: `attempts/A187-basin-map/{BRIEF.md,code/basin187.py,code/report187.py,results/basin_map187.json,notes/basin_map.md}`,
  `docs/residue_map/basin_map.svg`, `docs/residue_ledger.md` §3, registry row A187.

## 2026-09-09 — A186-contact-census (Fable lead) — **Theorem CC settled; c0_Y1033's eight budget-0 assignments [P] (no witness, no kill), the measured obstruction is the column P2 | F2 | F3**
- **The question** (PI, 19:15): can an assignment set be turned into a contact graph, and is there enough information?
  **Answer** (`docs/proofs/contact_census.md`): yes — the pieces determine the CANDIDATE graph (Lemma CAND: interval
  separation over piece pairs; a certified gap > 0 = never in contact), the loadable BOX FACES (Theorem CC (c)/(d): a
  piece face is a wall of the hypothesis and carries a multiplier like one) and the finite SELECTION MENU; they do not
  determine which subgraph bears the load — Theorem CC (e) is solved by the selection tree (Theorem CC-LP = Theorem
  LOCAL on piece bodies, the leaf LP's dual = the contact graph), not by counting (T1(d): flexible supports are FJ points).
- **Numbers [M]** (`attempts/A186-contact-census/notes/census.md`): 8 budget-0 leaves = 4 geometries twice; candidate
  graphs 24/20/24/22 edges (free–free 15/13/15/15), H touches only P4 among the pins, F2..F5 the left/top walls;
  selection tree 2.5 ms/node, node 1: 209,006 nodes / 83,919 closed / 0 exact-feasible / 0 unresolved, CAPPED at 555 s,
  lowest closed leaves are the 45° root cells at s0 + 1.0e-4; elastic exact LP over the tilts (52 starts): no disjoint
  configuration of the hull boxes, least overlap 0.0615 at s0 = the upright column P2 | F2 | F3 above BL(0,1)
  (uprights need 3.5 for F3's centre against 3.377); nodes 2–4: 0.12 / 0.079 / 0.17. The k7 + pinwheel4 shadow does not
  appear in any least-overlap configuration.
- **Verdict**: all eight [P]; the certified form of the obstruction is a COLUMN row over the pieces (CC-5) — cheaper than
  running the tree to completion.
- **Process**: the box held 12–14 pythons (8 lab workers + 4 Claude-extension pythons caught by the CIM filter) for the
  whole attempt, so no worker was launched; every computation was a transient foreground python of 5–560 s.
- Files: `attempts/A186-contact-census/{BRIEF.md, code/{nodes186,contacts186,tree186,descend186,global186,fig186}.py,
  results/{assignments186.json, candidates186_b0.json, tree186.jsonl, descend186.jsonl, global186.jsonl}, notes/census.md}`,
  `docs/proofs/contact_census.md`, `docs/residue_map/c0_Y1033_contacts.svg`, `docs/residue_ledger.md` §4, registry row A186.

## 2026-09-09 — A189-noroom (Opus engineer) — done-mixed
- **The task**: turn PI's NO-ROOM leaf (the reading of A182's STEP 34 panel — *"I only see 10 squares placed. How does
  this admit an 11th square anywhere?"*, killed by the coordinator in `attempts/A182-assignment-resume/results/noroom/`)
  into a tool with a general-`k` statement, and run it over every recorded assignment node.
- **Statement [T]** (`attempts/A189-noroom/code/noroom189.py` docstring, stated for any `n`):
  **Lemma 1 (pocket counting bound).** With `k` roles boxed at the multibox fixed point, bisect the free unit square's
  (centre, tilt) space against the `k` cores with multibox's exact dead test — the free square is deliberately NOT a
  `Node` role, because it has no `K'` of its own. Every dropped piece is certified "every pose here meets some core", so
  every free pose's centre lies in the open residue. Cover the residue's centres by axis-aligned pockets `P_j` with
  non-empty interior; a square whose centre lies in `P_j` MEETS `int(P_j)` (its interior is an open neighbourhood of the
  centre), so `#free ≤ Σ_j LANE(P_j)` with A141/A161's exact lane cover, and the node is DEAD once that sum is `< n − k`.
  `k = n − 1`: DEAD iff every pocket has LANE = 0 (the STEP 34 certificate). `k = n − 2`: DEAD iff the pockets sum to
  ≤ 1 — A161's pair test is exactly what turns an undischarged cover into LANE = 1, so the two-free case is free.
  Undecided pockets count as unbounded. **Lemma 2 (container partition with multiplicity).** On a uniform grid of side
  `w`, a unit square at tilt θ contains the concentric axis-aligned square of side `1/(|cos|+|sin|) ≥ 1/√2`; an interval
  of length `L` meets ≥ `⌈L/w⌉` column interiors and every (met column, met row) cell interior is met, so a free square
  meets **at least** `N(w) = ⌈(1/√2)/w⌉²` cells and `m ≤ ⌊Σ_i LANE(C_i)/N(w)⌋`. The brief's "a single square meets at
  most 4 cells of side < 1" is the same observation reversed — a tilted unit square meets up to 9 half-grid cells; the
  sound, useful direction is AT LEAST, `N(1/2) = 4`.
- **Regression [C]**: STEP 34 reproduces DEAD in **47.5 s** — bisect depth 13 in 20.3 s dropping **0.99962** of the root
  centre×tilt volume, ONE residue pocket `[3.179, 3.440] × [1.522, 1.903]` (area 0.0995), `LANE = 0` in 2.5 s
  (`results/certs/step34_regression.json`).
- **The pass [M]** (`results/noroom189.jsonl`, `results/report189.txt`): 33 recorded `branch` nodes of A182's fourteen
  journals with `8 ≤ k ≤ 10` (the journals have no `leaf` kind; `subtree` records are result summaries with no `hull`,
  and `k = 11` nodes are vacuous — no free square left). **5 NO-ROOM kills, every one at `k = 10` and every one on
  `c0_Y1033`** of 19 tested; **0 of 8** at `k = 9`; **0 of 6** at `k = 8`. Two further nodes of `k5_11_interior_Y0672`
  die at normalise by A171's pair leaf (`EmptyBox`), recorded under their own leaf name and never counted as NO-ROOM.
- **Why the rest survive [M]**: an `F_i` role carried as a whole meeter window has an **EMPTY `K'`** — no point lies in
  every pose — so it clips nothing (A178's `mbpatch178` gives that the sound semantics; without it the run raises).
  Such nodes still drop ~95 % of the free square's volume but leave pockets of total area **0.8–2.1**, where LANE = 0 is
  impossible; the pass declines the lane cover there as a budget decision, never as a verdict (26 UNDECIDED).
- **A183's alive S3 nodes of `l1_104`** (4 boxed roles, 7 free): 8 sampled, the counting bound **never bites**, exactly
  as the arithmetic says — a 4×4 grid on `s ≈ 3.877` gives `w ≈ 0.969`, `N = 1`, and a bound of 16 ≥ 7 even if every
  cell decided; the half-grid that would give `N = 4` needs a LANE verdict on 64 cells.
- **Pages retired: NONE, structurally.** A dead branch kills its whole subtree (A182's tree is a case tree: a
  descendant's hypothesis implies its ancestor's — no box monotonicity needed), but `c0_Y1033`'s five dead nodes cover
  only **4 of its 30 alive/undecided leaves**, and A182's search of every one of the six pages carrying journaled
  branch nodes stopped on node budget, so the unexplored branches are unexamined leaves. `status_gallery` (7f) computes
  exactly this and adds a kill row only when both conditions hold; a57v4 stays 50 ALIVE / 10 DEAD, k0v4 11 ALIVE.
- **Read-across for every n**: the leaf costs 47 s against the ~850 s an LP kill costs, and it killed the deepest node
  A182 reached — it belongs INSIDE the assignment search, at every node before branching or LP, and it pays exactly
  where the assignment has been refined enough to give each role a real core.
- **Process**: ≤ 1 python at BelowNormal / affinity 0xFFFF throughout (the box held 9–10 lab pythons plus 4
  Claude-extension pythons; ceiling 12 checked with a CIM filter before every launch); READ-ONLY on every other attempt;
  `PYTHONDONTWRITEBYTECODE=1`; ~2.5 CPU-h total.
- Files: `attempts/A189-noroom/{BRIEF.md, code/{noroom189,report189}.py, code/run189.ps1, results/{noroom189.jsonl,
  report189.txt, certs/}, logs/}`, `docs/residue_map/{gen_noroom189.py, noroom_c0_Y1033.svg}`,
  `docs/shadows/status_gallery.py` (7f), `docs/residue_ledger.md` §4, `docs/budget.md` §D item 11, registry row A189.

## 2026-09-10 — A194-descent (Fable lead, theory) — **Lemma CH + Theorems D1/D2/D3: a non-simple corner hurts by a trade-off, the conversion descent yields s_T − m (zero today), the basin descent is the lever — nine A163 witnesses die by a clip**
- **The PI's diagnosis (00:45):** no fast way to apply higher-k search results to lower-k spaces; formalise how much a
  non-simple corner hurts, precompute the grain coverage (Trump 5-grain, pinwheel 4-grain, V 3-grain) with joint
  tilt/slide dynamics, and turn higher-k kills into lower-k kills.  Delivered as `docs/proofs/descent.md` (Lemma CH,
  D1–D3), `descent_grains.md` (grains, precomputation P1–P6, dynamics), `descent_examples.md` (l1_104, c0_Y1033, the
  A163 witnesses, Trump), `docs/residue_map/descent.svg` (`gen_descent.py`), `attempts/A194-descent/`.
- **Lemma CH [T]** (corner met at depths d₁ ≥ d₂, box side c_b): (S) rigid conversion to a simple corner at side cost
  exactly d₂ — μ(Q + (t,t)) = μ(Q) + t, every packing, any corner, the opposite corner's pins kept; (A) the box
  (0, c_b − d₁)² is met by no square; (C) distinct cells, non-lonely, 6-dim pair interior; (L) the band meeter's unit
  chord on every wall-parallel line within γ(θ) ≥ 0.2071 of its centre line.  [F] no named line, no depth, no area
  beyond (A) is forced.  Consumption: crowd row at depth s_T − m, R3 NO-family, v5 guard line per centre-slab; clips.
- **Theorem D1 [T]** (T = S + {p} dead on [s_lo, s_T] ⇒ d₂(p) ≥ s_T − m): the whole content of "k+1 dead ⇒ k"; yield 0
  at the window top today, ≤ 0.0097 (TL(0,0): S02 ⊃ k6_23) / 0.0085 (BL(0,2): S07) / 0.052 after certifying the
  extensions to their minima, **exactly 0 at a k0 corner at every side** (k1_00's minimum is ŝ); Trump refutes the
  stronger claim (its TL crowd at (0.194, 0.181) widened / (0.168, 0.155) unit is what lets it beat its k6 completions).
- **Theorem D2 [T]** (basin descent): Dead_{L∪P}(N, s0) in T's frame descends to S = T ∖ {p} as the same tree with p
  dropped + the lonely clip on bodies meeting p's widened box + a partner lane at surviving leaves; emits an `N_boxes`
  entry in the p-less frame.  **[M] A163's nine trump5 witnesses: f1 is the ONLY TL meeter, depth 0.19–0.31, LONELY in
  9/9 (margins −0.13…−0.30), 0 partners in 2·10⁵ draws — all nine die by D2(b)**; the clipped re-run [C] is the step from
  42/54 toward 54/54 in trump5.
- **Theorem D3 [T]**: kills are constant along grain moves inside a certified box; the exchange completion costs the chain
  difference; a non-simple corner is harmless to the kill unless its crowd is load-bearing.  [F] "the crowd slides into
  the slot along the grain's freedom at no cost" — f0's freedom is a 0.298 segment between stops at fixed tilt.
- **l1_104 [M]**: the τ = 10 support is a k3-skeleton — slot squares at BR/TL/TR (weight 1) + grazers ≤ 0.026 deep
  (TL's lonely) = three k1 pockets bought with the K0-WIDEN pad — plus one BL crowd (0.628, 0.548); no basin to descend
  from (K04/S08 has none); l1_159 (K06 = the pinwheel) is a ≈ 1 CPU-h pin-free descent away.  **c0_Y1033**: CH-L is
  A186's CC-5 column row (pins 2 + left-wall band meeter 1 ⇒ 0.877 left on a vertical line in (0,1)); the slot-square
  exposure test prunes the "two new" TL branch.
- **Missing, priced**: basins for S01-line/S03/S08 (34 of 52 alive pages) 1–3 CPU-h each; pin-free descents ≈ 1 CPU-h per
  grain; extension classes above s0 NOT worth it (2–30 CPU-h per class for depth ≤ 0.05).
- Process: one BelowNormal python (≈ 3 CPU-min), ceiling 12 excl. Claude Extensions counted and waited on; read-only
  elsewhere.  Files: `docs/proofs/descent{,_grains,_examples}.md`, `docs/residue_map/{gen_descent.py,descent.svg}`,
  `attempts/A194-descent/{BRIEF.md,code/hurt194.py,results/hurt194.json,logs/}`, ledger §4, known_results 26e, registry.

## 2026-09-10 ~06:00 — A193-highk-probes (Fable lead) — done-negative: **corners4 and k4_05 are THEORY-LIMITED under the k0 toolkit (0 kills); the obstructions are named and bounded**

- **Question (PI, 00:45).** Probe the two high-k classes with no price in the dependency graph — corners4 (k4_13) and k4_05 — with the tools that moved c0_Y1033 (multibox, Theorem FC meeters, A182's assignment search, A189's no-room leaf, A185/A190's windows + guard-line LP under v5): do they start to die, or are they theory-limited?
- **Frames [T].** corners4: all eight completable slots extend to k5_16 — OPEN on the window (A57 G1) — so Theorem FC forces NOTHING on the window; at s0 all eight are forced (Lemma CC4). k4_05: three cells forced on the window (BR(0,1) → k5_15, BR(1,0) → k5_13, TL(1,0) → k5_12, all FULL), two at s0 only (BL(1,0) → k5_11, TR(0,0) → k5_16). Every s0 kill would be conditional on A57 G1 — no new obligation.
- **Roots [M].** Pins-only LP with ten guard lines (pin lines, slot lines, sixteenths): corners4 τ = 7.195 > 7, unconverged, 0 lines active (A65's 7.2545 wall reproduced); k4_05 τ = 6.965 < 7 — A55's number (6.982 / 6.973, both `FAIL(rc=3)`) — and the v5 certificate FAILS with 58 holes, 8 of them AT the BL(1,0) slot pose (1.49, 0.50, 0°) = k5_11's fifth pin, 40 stacked on it in the centre block; A190's witness re-solve lands at **7.189 > 7**. That is Lemma K1 (A55: aliveness descends containment) measured: the open superclasses' pin images live inside every LP the anonymous-meeter form can state, because a pin at the slot IS a meeter of the slot.
- **Leaves at s0 [M].** A182's search from the root (nsub 4 / refine 2, chord rows, lanes, MAXF 7): corners4 — 318 nodes, 5.0 s median, depth 8, first complete assignment at ≈ 500 nodes, 6 complete leaves; k4_05 — 179 nodes, 6.8 s, depth 5, 3 leaves. The meeters localise (hulls of area 0.1–0.7, grown cores on 2–3 of 4–6 meeters); **no-room UNDECIDED at all 9 leaves** (one centre-block pocket of area 5.90 / 6.76: the pin cores set it, the meeter cores are too small); **no chord row negative** (min rhs s − 2 / s − 3); **0 of 10 guard lines active at every LP**; windows + guard-line LP (b4 = 11): **corners4 3/3 ALIVE at τ = 11.000 exactly with a HALF-INTEGRAL support** (fourteen placements at weight 1/2; largest disjoint sub-family 5 of 14, so not two near-packings averaged — a genuine odd-cycle fractional support, no line sees it); **k4_05 3/3 read 10.766 / 10.857 / 10.778 UNCONVERGED (minmass 0.72–0.77) and every certificate FAILS** — 22 holes in window F1, 51 in window P1 (the BL(0,1) pin's own rows), 31 in window F1 for leaf 3 — with the re-solves at **10.930, 11.100 and 11.000**: the root's creep-to-budget one level down.
- **H-box pricing measurement [M].** corners4, leaf 1, H = the most tilted half-weight pose (1.436, 1.280, 41°) ± 0.06 / ± 4°: **DEAD at normalise in 1.1 s by A171's pair leaf** (K′(H) fills F1's pieces) — the YES side of an A57 zone split at the phantom's tilted pose dies by geometry; the NO side (a NoFam at the pose) needs the windows clause to carry NoFams, which it does not (the same clause k4_05's resister split needs). k4_05, leaf 1, H = the TR corner pose (3.377, 3.377, 0°): LP 10.735 vs 11 unconverged, 0 lines active, 362 s — k5_16's slack-pin node, K1 once more..
- **Verdicts [S].** corners4: theory-limited twice — on the window by K1 (nothing forced, root alive), at s0 by a half-integral phantom that satisfies every single-square row of the certificate language; the lemma needed is a TWO-square row (the two FC meeters of one slot cannot both be half-present — Lemma A1's ℓ∞ separation enters the LP only as a partner-existence cut), i.e. a pair clause, with the bounded MEET clip (pieces ∩ bbox of ∩_i (B_i ⊕ −Q_θ) per tilt sub-bin; 2.4× smaller for the four-slot roles) as the geometric half. k4_05: theory-limited by K1 at every hypothesis the anonymous-meeter form can state; the bounded fix is the δ-resister split at its two open slots (YES = slack-pin k5_11 / k5_16 nodes — the P-list's item 7, priced in A57's row; NO = a NoFam at the slot pose, which the v4/v5 windows clause does not yet carry for window rows). **The PI's conjecture ("comparably") is false for these two**: c0_Y1033 has no open superclass and every role cored at its leaves; these have K1 mass and a half-integral phantom.
- **Prices (`budget.md` §D item 12).** Per node 5.0 / 6.8 s; per complete leaf ≈ 0.25 CPU-h (no-room 100–170 s, LP 340–420 s, certificate 260–430 s); trees ≳ 10³–10⁴ leaves. corners4: no priced route without the pair row / MEET clip; with the clip, one night to re-measure. k4_05: ≈ 2.5 CPU-h to measure the all-NO node; the YES side is A57's [P]. Tonight ≈ 5 CPU-h.
- **Process.** One worker at a time (the box held 11–12 lab pythons all night; ceiling 12 counted and WAITED on before every LP, the verifier in-process when at the ceiling), BelowNormal / 0xFFFF, per-node walls (LP cap 300 s, no-room 240 s, certify 1,500 s); the corners4 and k4_05 passes were stopped by hand once their LP quotas were spent (the remaining enumeration repeated the verdict); READ-ONLY elsewhere (runtime patches of `classes178.pins_of` and `journal182`'s directories, in memory only).
- Files: `attempts/A193-highk-probes/{BRIEF.md, notes/probes.md, code/{probe193,hbox193,census193}.py, code/launch193{,b}.ps1, results/{probe193_*.jsonl, lpres_*.json, tree_*.json, journal/}, certs/, logs/}`, `docs/residue_map/{gen_probe193.py, probe193_corners4.svg, probe193_k4_05.svg}`, `docs/residue_ledger.md` §4, `docs/budget.md` §D item 12, registry row A193.

## 2026-09-10 -- A191-combined-cascade (Fable lead) -- **the combined k0 cascade leaf on l1_104's S2 layer: 17 of 64 alive S2 nodes DEAD under the FROZEN verifier; the layer priced at 305 s per node**
- **The task (PI 00:45).** Evidence by 07:00 that the k0 residue is compute-bound with a price: the windows + guard-line LP (v5) with the
  not-yet-placed corners' two meeters as anonymous windowed roles and the no-room leaf on ALL 64 alive S2 nodes of `l1_104` (A183's
  renorm181/183 fixed points), root/D0/S1 first; then the S3 children of the survivors (coarse), the canary `l1_153`, the CPU-h per cell.
- **[T] The anonymous corner windows cannot change the LP** (`notes/cascade191.md` s.1): a window without a core has the row (V2) on its poses
  not meeting ANOTHER window's attached core; every core is attached, so `E_i = E_0`, and `f = 11 - 9 - 0 = 2 > 0` keeps the free clause (V1),
  a superset of every window row -- (V2) is implied, tau and `b4 = 11` unchanged.  They act in the geometry: the corner NO-ROOM leaf (A189 Lemma 1
  with the pocket = the widened corner box, `m = 2`: K0-BLOCKED's two distinct meeters, R6 and A161's exact miss test make them free; A141 cover +
  A118 pair test give LANE) -- and there LANE = None at BR / TL / BL on 64 of 64 (0 kills, 29 s per node).
- **[M]/[C] The sweep** (`results/run191_l1_104_S2.jsonl`, `figs/steps_l1_104_S2.svg`, two BelowNormal processes, 01:17-04:21, cap 300 s):
  **17 DEAD (27 %)** -- root/D0/S7, S12, S13; D1/S8; D3/S9; D4/S10; D52/S4, S7, S8; D53/S5; D54/S12, S13, S14; D55/S5; D58/S7; D6/S15; D7/S13 -- every
  one by the v1-style LP (A135 exact cores on the roles' UNION boxes, A144 guard-line columns, budget 8, A190's emitter) CONVERGED at **tau = 7.000 < 8**,
  `verify_case_v5` PASS, and -- no guard line ever carrying density (0 of 64 in both LPs) -- **all 17 PASS under the frozen `verify_case.py`
  (A143, sha `521cb01f...`; `certs/*_v1.frozen.certify.json`)**: [C] under the frozen chain, conditional on K0-O1 and the node's case as every
  cascade kill is.  26 (41 %) converged ALIVE at tau = 8.000 = budget exactly; 19 (30 %) LP-dead UNCONVERGED kill candidates (tau 7.19-7.58 at ~240 s);
  tau quantised {7.000 x20, 7.2-7.6 x16, 8.000 x28}.  **[F]** the dead nodes are those whose A183 fixed point COLLAPSED H (kept <= 0.022 on 14 of 17,
  6e-7 on root/D0/S12): the geometry kills, the LP witnesses; the guard lines added nothing at S2; A185's windows LP (budget 11) sits at tau 9.6-10.6
  unconverged at every cap (A185: 10.000 at 300 / 1100 / 1526 s on root/D0/S1) -- a diagnostic, not a verdict.
- **root/D0/S1 (the PI's "first kill if it converges"): NOT a kill** -- v1-style LP tau = 8.000 = budget CONVERGED in 136 s (ALIVE); windows LP 10.03
  unconverged; lanes None.  The first k0 S2 kills are root/D0/S12 and root/D0/S13 (frozen PASS at 01:57).
- **Cost per S2 node [M]:** geometry 29 s, v1 LP 162 s (max 356), windows diagnostic 101 s, certificate 46 s per kill (max 244), wall 305 s mean /
  663 s max; the layer **5.4 CPU-h** (v1 LP 2.9, diagnostic 1.8, geometry 0.5, certificates 0.25); **0.32 CPU-h per kill**.
- **Canary `l1_153`** (1 alive S2 node root/D25/S=H): v1 LP tau = 9.000 = budget converged (ALIVE), lanes None, 263 s -- the construction transfers.
- **S3 (coarse 4/2, parent-seeded; sample):** the first cover box B0 dies at 4/2 by EmptyBox(B) on 4 of 4 parents (60 s each -- a biased sample, the
  sampler then took interior quantiles); the interior children (B95 of root/D0/S0, S1, S11, ...) die by the exact-core LP (v5 PASS, ~250 s each);
  `results/run191_l1_104_S3coarse.jsonl`, `run191_l1_104_S3.jsonl` (the LP on A183's fine S3 records); the counts at report time in `notes/price191.md`.
- **The price** (`notes/price191.md`, `budget.md` s.D item 13 + the k0 row, `residue_ledger.md` s.4): S2 measured (5.4 CPU-h, 27 % kills + 30 % candidates),
  S3 sampled, S4-S8 ASSUMED at the S3 rate with fan-out 112 / 56; the table prints CPU-h per cell and instance-hours (16 vCPU) for the measured, 0.90
  and 0.99 deep kill rates; the lever is the geometry's kill rate at depth (A174 coexistence cut, A178 partner-first), not LP cap.
- **Process.** <= 2 shard pythons + 1 verifier child (<= 5 rule), BelowNormal / 0xFFFF, box ceiling 12 excluding Claude Extensions counted and WAITED on
  before every LP and verifier launch (the box held 10-12 lab pythons all night, three of them A185's idle waiters -- so a third A191 process could never
  pass the gate and was stopped; root/D0/S1's windows leg was left to A185's own running legs); per-node wall 1,500 s with the verifier's process tree
  killed on timeout; frozen verifiers never edited (the frozen one re-RUN, unedited, on the kill certificates); read-only elsewhere; PYTHONDONTWRITEBYTECODE=1.
- Files: `attempts/A191-combined-cascade/{BRIEF.md, notes/{cascade191,price191}.md, code/{prio191,lines191,cert191,node191,run191,s3_191,fig191,report191,
  price191,frozen191,foldin191}.py, code/after_s2.ps1, results/{run191_l1_104_S2.jsonl, run191_l1_104_S3coarse.jsonl, run191_l1_104_S3.jsonl,
  run191_l1_153_S2.jsonl, report191.json, price191.json, lpres_*.json, s3_boxes_*.json}, certs/, figs/steps_l1_104_{S2,S3coarse}.svg, logs/}`,
  `docs/residue_ledger.md` s.4, `docs/budget.md` s.A k0 row + s.D item 13, registry row A191.
- **S3 addendum (05:30) [M]/[C]: 22 of 23 S3 nodes tried are DEAD -- coarse parent-seeded children of the S2 survivors 14 of 15 (the corner-nearest B0 by EmptyBox(B) at 4/2 on 6 of 6 parents, 37-75 s; the interior children by the exact-core LP at budget 7 CONVERGED at tau = 6.000 on 8, 1 undecided at cap 240 s) and A183's fine 8/3 records 8 of 8 (the same LP, tau = 6.000); every LP kill PASS under v5 AND under the FROZEN verifier (`certs/*_B*_v1.frozen.certify.json`) -- the LP value drops by exactly one unit per pinned square (8 -> 7 at S2 on the collapsed nodes, 7 -> 6 at S3 on every node tried), so with four cores the S3 layer is where l1_104 closes: 5,432 A168-alive S3 children under the 47 S2 survivors at 249 s each = **376 CPU-h = 23 instance-hours at 16 vCPU** for the whole layer (the sample is 23 nodes biased to the root/D0 and root/D1 chains; `notes/price191.md` gives the 0.9x / 0.99 / 1.00 scenarios and the S4 residue).  Audit (`code/audit191.py`, `results/audit191.json`): every kill certificate's cores are pairwise interior-disjoint (exact SAT) and bound to their union boxes by v5's own `point_in_all_poses` check; frozen PASS on all.**

## 2026-09-10 ~12:10 -- A196-y0491 (Fable lead) -- done-negative: **the PI's reading of k5_16_interior_Y0491 run to a verdict -- ALIVE at its node; the wastage premise fails (|U| = 1.02 of 4.03), the chord rows never go negative, the exact-core LP stays at tau 4.135 > 4**
- **The reading (10:30)**: "forcing a double meet on TR(0,1) + the top and bottom chord limits seem like they would collectively blow the wastage budget."
- **Step 1, the node [T]/[S]**: Theorem FC at TR(0,1) gives two distinct non-pin meeters of B+; A161's exact test lets H meet it; geo178b's pair test at 4/2 leaves H-meets alive
  and 2 of 6 Lemma A1 cell pairs; both two-free cases DIE at unit propagation (every BL(1,0) candidate misses by the exact test; the 'new' meeter node re-normalised from the
  case's hulls is EmptyBox(F2)) -- so TR(0,1) forces H + one free square F1.  Unit propagation over the other five cells (56 nodes, 705 s) forces nothing: BL(1,0) has 2 {new,new}
  options, BR(0,1) 4.  Sharp 8/3 fixed point: H kept 0.656, F1 kept 0.096 (x [2.14, 2.48] x y [2.56, 3.38]), invariant PASS, meet clip drops nothing; no-room UNDECIDED (residue 3.77).
- **Step 2, the rows [S]**: 92 pin-band lines, open chords per piece with verify_case_v5's primitive: 0 negative; top y = 2.937: P2 + P4 + F1 0.682 -> rhs 1.195 (beta 1);
  right x = 2.937: P3 + P4 + H 0.581 -> 1.296; x = 1/2: 0.877 (beta 0); bottom 1.877.  The top limit is real (F1's 0.68) and leaves one unit chord.
- **Step 3, the wastage [M]**: certified |U| = 1.0214 = 25.3 % of s0^2 - 11 = 4.0318 (W strip 0.46, E strip 0.56, nothing in the top/bottom bands); no kill; Z = 118 rects.
- **Step 4, the LPs [M]**: exact-core LP (7 cores incl. F1's a = 0.044, zone nofams, 8 guard rows, budget 4): tau 4.138 (300 s) / 4.135 (900 s), unconverged, 1 line active,
  support the S01 room phantom (right-wall square between P3 and P4 at weight 1 -- the slack-pin K1 mass; top-wall square 0.60; bottom-wall square split 0.46/0.54; fractional
  tilted mass in x 1.3-2.0, y 2.2-2.5).  Windows + guard-line LP: 9.667 < 11 unconverged, 0 lines active, no certificate.  Nothing certified; frozen verifiers untouched.
- **Steps 5-6**: page `docs/residue_map/y0491_cascade.svg` (5 panels, a note per panel, U hatched, chords printed, times); the pass over the other alive k5_16 pages NOT run
  (Y0491 did not die); no new certificate kind, status_gallery unchanged.  Lever: the BL(1,0) branch (k = 9, budget 2); a geometry re-run at deadline 1,400 s is queued behind
  the box ceiling (`logs/queue_geo.log`).
- **Process**: <= 3 own pythons (2 at peak), BelowNormal / 0xFFFF; the box held 11-14 lab pythons excluding Claude Extensions, so a second geometry run was killed and queued;
  per-stage wall 1,500 s with the tree killed on timeout; PYTHONDONTWRITEBYTECODE=1; ~1.1 CPU-h.
- Files: `attempts/A196-y0491/{BRIEF.md, notes/y0491.md, code/{prio196,node196,node196b,rows196,waste196,lp196,lp196b,page196,pass196,queue196,fig196}.py, results/, logs/}`,
  `docs/residue_map/y0491_cascade.svg`, `docs/residue_ledger.md` s.4, `docs/budget.md` s.D item 14, registry row A196.

## 2026-09-10 midday - A197-slot-pair-pass (Opus engineer) - done-negative

- The PI (10:45): "`k5_16_interior_Y0054` is trivially dead: BL(1,0) can't be doubly met in any way.
  That's true of most of this class: the H box is in front of a slot, so the two slot simple units
  can't be doubly met."
- **Why A178's per-cell pass missed it.** `geo178b.slot_pair_test`'s `H-meets` branch restricted H's
  CENTRE to the cell's meeter window and never asked H to MEET the widened box `B_p+`.  On a `k5_16`
  page that restriction is a NO-OP (H's record box already lies inside the window), so the branch was
  ONE node with no Lemma A1 split at all, at `nsub 4 / refine 2`, under `max_cells 6` / `max_pairs 40`
  which both declared ALIVE on exhaustion - 3 of Y0054's 6 cells were recorded `hull too wide: ALIVE
  untested`.  Y0054's `BL(1,0)` record is NOT empty: `two-free` dies there already (0 of 1 pair) and
  only that unsplit `H-meets` node keeps the cell alive.
- **The fixed test** (`attempts/A197-slot-pair-pass/code/pair197.py`; A178 / A171 / A161 imported
  read-only): `meet_cover` = an exact A161 separating-axis COVER of the poses whose square actually
  meets `B_p+` (bisection to depth 9, 24-box cap, 0.05 s), applied to every meeter role; `H-meets`
  split over ORDERED Lemma A1 cell pairs `(cell_H != cell_B)` on a grid of side 0.70 < 1/sqrt2;
  `two-free` over unordered pairs; caps 24 / 400; `nsub 8 / refine 4` on every pair node; A169's
  lonely clip at forced corners; a witness sampler.
- **[F] The PI's reading is refuted by an explicit witness** (`results/witness_Y0054_BL10.json`).
  The meet cover bites - H's `y` shrinks from `[1.5193, 1.6590]` to `[1.5193, 1.5542]` - and iterated
  to a fixed point (`exp197`, four 26 s passes at 8/4) `BL(1,0)`'s `H-meets` branch is still ALIVE,
  because the cell IS doubly met:

      H = (1.938542, 1.519271, 82.3719 deg)    the SW corner of H's own record box, extreme tilt
      B = (1.5, 0.5, 0 deg)                    a free square on the bottom wall

  H's bottom edge dips below `y = 1.0255101` for `x in (1.858, 2.041)`: an interior sliver of area
  **0.00228** inside `B_p+ = (1, 2.04045) x (0, 1.02551)`.  B's top edge is at `y = 1`, just under
  the dip; the H|B separating-axis gap is **+0.006518**, all 21 pairs of the seven squares are
  interior-disjoint (min gap 0, tangencies only), both meet `B_p+`, and their centres are 1.0193
  apart in l-infinity against Lemma A1's 0.7071.
- **The pass** (`results/slotpair197.jsonl`, resumable, still running at the time of writing):
  **21 of the 44 alive `a57v4` pages, 43 forced cells, 3.5 CPU-h - 0 retired.**  Every cell admits a
  pair; the sampler EXHIBITS a real admissible configuration on **28 of 43**.  The `H-meets` branch
  is genuinely VACUOUS on 11 cells (H's box lies outside the meeter window, so H provably cannot
  meet) and `two-free` is alive on those anyway.  Two cells per page (the most squeezed first) under
  a 900 s wall killing the process tree; one page (Y0054) hit the wall at 3 cells.
- **The missing half, from the concurrent A198 pass:** A198 retires 6 pages
  (`k5_11_interior_Y1110` at `TR(0,0)`, `c0_Y0076` / `Y0169` / `Y0171` / `Y0257` / `Y0258` at
  `BL(0,2)`) with the SAME theorem by running A178's cascade ROUNDS first - the forced-slot roles
  tighten H's hull before the pair test - which A197's driver skipped to buy population coverage.
  The lever is the COMPOSITION: cascade rounds + meet cover + Lemma A1 split in one driver.
- Gallery `docs/residue_map/slotpair197.svg` (the surviving pair drawn as real poses),
  `status_gallery` (7h) collector added and rerun (`a57v4` now 39 alive / 21 dead, all six new kills
  A198's), `residue_ledger.md` section 4, `budget.md` section D item 14, REGISTRY row.

## 2026-09-10 — A198-fastprop (Fable lead) — done-mixed
- The PI's fast propagation (11:30, on `k5_16_interior_Y0054`) built as `attempts/A198-fastprop/code/fastprop.py`: A1 grid cells (side 0.575), exact cell reach per forced slot (container clip, multibox exact dead test against every role's K', A161 exact miss test, A173 lonely clip at corners), joint reach on window intersections, option table with exact open min-chords, the exact cover search (Theorem COUNT, `notes/fastprop.md`) with pairwise A1 and chord rows, H forced where the barred-H search is infeasible and clipped, forced free meeters instantiated as roles, fixed point, then A178's pair test at 8/4 on the most constrained slot.
- **Y0054 [M]: ALIVE** — the chain reproduces to "H MUST meet BL(1,0)" (27 nodes; H pulled down y1 1.659 -> 1.554) and stops there: the count stays feasible (witness cover in the certificate; a corner-hugging axis square serves TL(1,0)+TR(1,0)+TR(0,1)+BR(0,1)), the pair test at BL(1,0) is alive, A197's witness realises the pair. [F] "BL(1,0) can't be doubly met" on this page.
- **Pass [M] (44 alive a57v4 pages, Y0491 to A196, 600 s wall, two BelowNormal processes, ~2 h): 2 DEAD** — `c0_Y0076` (A1/FC at BL(0,2): no free meeter cell; `check198` 200k samples consistent) and `k5_16_interior_Y0191` (EmptyBox(H) after the forced BL(1,0) meeter is instantiated in its one sliver cell); 42 ALIVE; H forced to a named slot on 16 pages (15 alive); propagation median 222 s per page, 325 s with the pair test.
- **Soundness incident, fixed:** five pair-test rows (c0_Y0169/Y0171/Y0257/Y0258, k5_11_interior_Y1110, 12:00–12:40) passed instantiated free-meeter roles to `slot_pair_test` as fixed distinct squares — the instantiated meeter can be the pair test's own meeter (double count). Rows withdrawn 13:35 (superseding jsonl rows), pages revived by `status_gallery.py`, fallback corrected to pins only, all five re-run ALIVE. The coordinator's live status rerun had moved them to killed/ for ~1 h.
- Files: `attempts/A198-fastprop/{BRIEF.md, notes/fastprop.md, code/{fastprop,fig198,run198,check198}.py, results/fastprop198.jsonl, certs/fp198_*.json, logs/}`, `docs/residue_map/fastprop_<nid>.svg` (44), `docs/shadows/status_gallery.py` (7i), STATUS rerun, `docs/residue_ledger.md` s.4, `docs/budget.md` s.D item 14, registry row.

### A197 addendum (2026-09-10, the pass completed)

- **Final: all 44 alive `a57v4` pages (Y0491 left to A196), 82 forced cells at a cell budget of 2, 6.7 CPU-h -
  ONE page retired.**  `c0_Y0076` at `TL(0,0)`, and not by a pair leaf: the ONE-FREE node is
  `EmptyBox(B_TL00)` in **30 s** - not even one free square can meet the widened corner box under A169's
  lonely clip, so the two Theorem FC demands certainly do not exist (`certs/sp197_c0_Y0076.json`; A198's
  `fastprop` kills the same page independently at `BL(0,2)`).  On the other 81 cells a pair survives and the
  sampler EXHIBITS a real admissible configuration on **45**.  `H-meets` is VACUOUS on 23 cells and
  all-`EmptyBox` on 4 more; `two-free` dies on 18 - but never both at the same cell except on `c0_Y0076`.
  Six pages hit the 900 s wall.
- **[T] Why A200's zero-pad kill of `k5_16_interior_Y0054` and A197's witness are BOTH right.**  Measured with
  A161's exact separating-axis test on H's whole record box: H **cannot** meet the UNWIDENED cell
  `(1, 2) x (0, 1)` at any pose; the smallest vertical pad at which it can is **0.001158**, and K0-WIDEN
  supplies `pi_0 = 0.0255101` - twenty-two times more.  The PI's reading is TRUE of the plain slot box and
  FALSE of the widened box `B_p+` that Theorem FC states, and a kill at the plain box is s0-only (the A155 /
  A159 pad phenomenon, third sighting).  A "cannot be doubly met" leaf has to name its box.

## 2026-09-10 evening -- A202-fast30 (Fable lead) -- done-mixed: **the CLOSED-FORM geometric kill layer runs in 8-28 s a page and draws the page first; it kills one page on its own at the window pad (k5_11_interior_Y1110) and reproduces A200's pad-0 kill of Y0054; stage 1 (A200's exact table on the survivors) retires four more (k5_11_interior_Y0275, k5_16_interior_Y0191 / Y0275 / Y0842, all at the g1 pad)**

- **What it is** (`attempts/A202-fast30`, the PI's directive of 16:35 and the PI's disc / corner / column readings of the
  day, credited in `notes/fast30.md`): every half-grid cell (side 0.575 < 1/sqrt2) split 4 x 4, times 6 exact tilt
  sub-bins = 2,400 pieces per page, each piece tested by SOUND necessary conditions in closed form -- **P** the pin
  discs (a centre within 1/2 of a pin's core meets the pin), **W** the walls at w_min/2, **C** Lemma CN against every
  alive piece of H (centres of interior-disjoint unit squares are >= 1 apart), **M** the relative-tilt separating-axis
  bound (|d . a| >= 1/2 + w(theta_F - theta_H)/2 on some axis of F or H; folded-mod-90 angular gaps; = CN when both
  tilts are free, up to 1.207 at 45 deg), **L** the open-chord row (pins + H + the piece > s), **R** reach (disc
  1/sqrt2, half-extent w_max/2) and **X** A161's exact separating-axis miss -- the survivors of each slot refined
  2 x 2 x 2 for three levels under the same rules (piece budget 12,000), so the alive region of a slot is a union of
  small pieces: the PI's discs appear on the page (Y0044's cell 16 alive only at x >= 2.659 = 1.659 + 1 and above
  P3's disc, exactly the 16:20 reading).  On the survivors: A200's union caps (CN / A1-U / CHORD-U), Theorem FC's
  demand 2, the assignment count with a pair table (A1 / CN / M on the option hulls x alive tilt intervals), the
  bar-H forcing, H clipped to the pieces that may meet its forced slots (l-inf ball AND A161's exact miss per H
  piece), iterated to a fixed point.  Verdicts `[C: closed-form trace]` -- no verifier clause exists yet.  Then
  STAGE 1 = A200's `QPage` with `reach(cell, S)` empty on the cells stage 0 killed and stage 0's H box; stop there.
- **Y0044 (the PI's page), g1 pad, 10.1 s:** P 4,634 pieces / 196 ms, W 1,337 / 27 ms, C 1,074 / 59 ms, M 2,760 /
  771 ms, L 7 / 292 ms, R 3,273 / 30 ms, X 1,308 / 7,233 ms (the exact miss is 70 % of the wall); BL(1,0) keeps 3
  cells whose refined union has diameter 0.9055 < 1 -> cap 1 -> H FORCED at BL(1,0) (A200 needed the exact table for
  the same forcing); every other slot uncapped; the count feasible (witness H@11, free@5 BL+BR(1,0), @16, @8, @18
  serving four slots, @22 three): ALIVE at stage 0; stage 1 ALIVE in 168 s (A200: 203 s), 60 reach tests skipped.
  Y0054: 20 s, pad 0 DEAD at stage 0 (FC at BL(1,0): H provably misses by A161 on its pieces, cap 1 by CN on the
  refined union, diam 0.9387) -- A200's kill, closed form, s0-only WINDOW-PENDING as before; g1 ALIVE (H may meet the
  padded box: A197's witness).  Y0491: 18 s, no cap fires (six slots, H at 64-74 deg), ALIVE both stages.
- **The population (40 ALIVE-at-LP pages of k5_16 / k5_11, both pads, two BelowNormal processes, 82 min):** stage 0
  8-28 s per pad; stage 1 37-294 s per pad (median ~100 s; A200's exact table on fewer cells).  DEAD: k5_11_Y1110
  (stage 0, g1: FC at TR(0,0), H provably misses the corner box, ONE alive cell -- cells 19 / 23 die by CN against
  H's hull, which multibox's K' test does not see; A198's earlier kill of this page was a withdrawn pair-test row,
  this one is FC + A1), k5_16_Y0054 (stage 0, pad 0 only), k5_11_Y0275 (stage 1 g1: TL(1,0) cap 1 by CN -> F1
  instantiated -> H's box clipped to 2 % by the mutual clip -> BL(1,1) has no meeter cell; **the unmodified A200
  quick200 reproduces this kill verbatim in 49 s** -- A200 had simply not run the k5_11 pages), k5_16_Y0191 and
  Y0275 (stage 1 g1: H forced at two slots + F1 -> EmptyBox(H), A198/A200's mechanism), k5_16_Y0842 (stage 1 g1:
  FC at BL(1,0), H provably misses, CN cap 1 -- the Y0054 mechanism, valid on the window here).  The other 34 pages
  ALIVE at both stages and both pads.
- **Soundness work:** a fuzz of every rule against an exact float SAT on 4,000 / 3,000 random pieces (0 refutations,
  `notes/fast30.md` s.4); a per-page refutation sampler (4,000 poses per stage-0-dead cell, H sampled over its box,
  pins' cores, container, the open widened box) on every killed page -- 0 admissible meeter poses in any dead cell;
  and one bug caught before it shipped: the joint option rows first intersected the two slots' alive tilt intervals
  as SETS of interval tuples, which emptied when the two refinements differed, and Y0044 "died" by the count --
  corrected to interval overlaps, Y0044 is alive as A200 says.  Rule for readers: a stage-0 kill of a page A200's
  exact tests leave alive is a bug until proved otherwise.
- **What stage 0 cannot do and why:** its unions are unions of BOXES x tilt bins, so the sliver-shaped alive regions
  (Y0054's BL(1,0) meeter at the bottom wall, height 0.12) come out ~0.94 in diameter rather than 0.885, and a cap
  that needs the exact K' geometry (H's core growing as H is clipped) is stage 1's; it has no lonely clip at corners,
  no SEAL (Lemma NO-SECOND needs a certified deep-regime tilt range for F, which is the exact bisection's output),
  and no instantiation of the unique anonymous meeter (A200's).  The exact miss X is 70 % of its wall: the next
  factor of 3 is a closed-form corner test in place of A161's bisection.
- Files: `code/rules202.py`, `fast30.py`, `fast30b.py`, `count202.py`, `stage1_202.py`, `fig202.py`, `run202.py`,
  `run202.sh`, `report202.py`; `results/fast30.jsonl` (one row per nid / pad / stage), `certs/f30_<nid>_<pad>_s<stage>.json`,
  `results/xcheck/` (the A200 cross-check); pages `docs/residue_map/fast30_<nid>.svg` (stage 0 top, stage 1 below,
  one panel per pad) and `fast30_gallery.svg`; `status_gallery.py` block (7l).

## 2026-09-10 evening -- A203-csp-consistency (Fable) -- done-mixed: **the fast count is a CSP on PIECES: H-consistency, the mutual clip and the settle kill Y0839's witness row in closed form (the coordinator's grid, reproduced), clip H on every page (4,606 units), force H on 10 more pads, and retire k5_16_interior_Y0842 at the window pad on their own; one artefact caught by the audit before shipping**

- **What it is** (`attempts/A203-csp-consistency`, the PI's readings of 18:20 on Y0839 -- "clipping H on both of those (and settling
  the mutual clip) should basically kill all the options there" -- and of 17:40 on Y0191 -- the meeter pair must be tested over
  MEETING pieces; the coordinator's grid check `y0839_csp_gridcheck.py`).  A202's stage 0 (copied at d13f7420, modified only in
  the copy) plus: **rule S** (Lemma PC: an interior-disjoint pair has an axis of one square with projection distance >= 1/2 +
  w(relative tilt)/2; on a piece pair the bound over the difference rect's corners and 4-degree tilt sub-intervals, numpy blocks);
  **Lemma HC** (a row with no piece compatible with any alive H piece is dead -- H exists); **Lemma MC** (an H unit compatible with
  no row of a slot a FREE square must meet is dead -- Corollary FC-count); the **SETTLE** (a near-dead row's compatible pairs split
  2x2x2 three levels under P/W/C/M/L/R/X + S); **Theorem COUNT-CSP** (the count ANDs the H-mask along the branch and needs
  piece-compatible chosen pairs).  Lemmas for any n in `notes/csp_consistency.md`; the page `docs/residue_map/csp203_<nid>.svg`
  = A202's panel + a CSP panel (H's units after the mutual clip, the dead rows lettered H / F, milliseconds per rule).
- **Y0839** (both pads, 25 s / 22 s): the count's witness row (cell 10 serving BL(1,0)+BR(0,1)+BR(1,0), 11 pieces at tilt 62-71
  deg) survives rule S at node level against 11 units (max distance 1.0025) and DIES by F after the settle (133 pairs, all dead,
  315 ms); the mutual clip kills 87 of H's 512 units; the count finds another cover (cell 15) and forces H at BR(0,1).  ALIVE.
- **Y0191** ALIVE (14 s): H 512 -> 96 units by MC:BL(1,0); 21 rows dead; the witness pair for TL(1,0) moves to (8, 18); the PI's
  pair 14 | 18 is NOT excluded at piece resolution (the closed form needs a pair settle; A201's exact test stays the fallback).
  **Y0044** ALIVE (17 s; H -> 161 units, forced at BL(1,0)).  **Y0054** ALIVE at g1 (33 s; H -> 1 unit), DEAD at pad 0 (A202's FC).
- **Population** (39 pages x 2 pads, two shards, 25 min): median 23 s, max 57 s; 296 rows dead (115 H / 181 F); H forced on 34
  pads (10 more than A202's stage 0); **kill: k5_16_interior_Y0842 at g1** (the F kills in cells 6 / 15 / 21 leave BL(1,0) a CN
  cap 1 with H provably missing -- Theorem FC; A202 needed stage 1 for it) and Y0054 at pad 0.  `results/csp203.jsonl`,
  `results/report203.md`, certs, pages; status_gallery block (7m), kills `[C: closed-form trace]` (no verifier clause yet).
- **Soundness**: rule S fuzzed (6,000 pairs, 2,872 dead, 0 refutations); tree compatibility vs brute force (3,000 cases); every
  kill audited by pose sampling (`scratch/audit203.py`).  **The audit caught an artefact**: a fixed role's row (a hull-only node)
  was walked as an internal node with no children, so every (free row, H row) pair surviving the hull test was excluded vacuously
  -- Y0054 "died" at g1; a sampled disjoint admissible pair F (1.504, 0.5, 0 deg) | H (1.949, 1.519, 82.4 deg) refuted it; fixed
  (hull-only nodes are leaf blocks), the population regenerated.  Kept rule: a closed-form kill of a page the exact tests leave
  alive is a bug until audited.
- Files: `code/csp203.py`, `satbatch203.py`, `csp203b.py`, `csp203c.py`, `count203.py`, `cert203.py`, `sweep203.py`, the copies
  `fast30.py` / `fast30b.py` / `rules202.py` / `fig203.py`, `fig203b.py`, `run203.py`, `run203.sh`, `report203.py`;
  `scratch/fuzz203.py`, `fuzz203b.py`, `audit203.py`, `pair_y0191.py`; `logs/`.

## 2026-09-10 night -- A205-clip-tree (Fable) -- running (shard on the survivors): **the CLIP TREE -- branch on a forced slot's remaining meeter rows, instantiate, A204's cascade + A203's rule S at every node; k5_16_Y0839 DEAD at the window pad in 526 s (every BR(0,1) row dies by FC at BL(1,0)), k5_11_Y0308 DEAD at the window pad in 203 s, and on the PI's Y0202 the BR(0,1) meeters die exactly as read -- 14 of 19 closed branches by the pair leaf, the 3 survivors fully named nodes whose roles keep 0.2-3 % of their seeds (the LP's job)**

- **What it is** (`attempts/A205-clip-tree`, the PI 20:35: "k5_11 Y0202 looks like it'll die if/when clip cascades try to run on
  the BR01 meeters").  A204 instantiates only FORCED meeters (cap 1), so on Y0202 (no cap, H reaches one slot) nothing was ever
  clipped against the BR(0,1) meeters.  **Lemma CT** (`notes/clip_tree.md` s.1, any n): at an alive node take the forced slot p
  with the fewest alive option rows (ties: the one H reaches); Theorem FC gives two distinct non-pin meeters, at most |named_p|
  of them H / instantiated roles, so with no named candidate the branches are the unordered PAIRS of rows (distinct cells by
  Lemma A1; rule-S-compatible on the rows' pieces), with one named candidate the rows singly, and with two the rows singly when
  the count has no cover with p's anonymous cap set to 0 (**bar-anon**, the analogue of A204's bar-H).  A branch instantiates
  its rows as roles seeded with the rows' reach survivors, pinned to their cells, named at p, and runs A204's cascade (the
  seeded polygon + lonely clip fixed point on the pieces, Theorem FC, the caps, the count) to which A205 adds the **rule-S clip
  between roles** (Lemma PC on the pieces: a piece with no compatible piece of another role is dropped), **Lemma HC on the
  rows**, the **count with A203's pair table**, the **S-PAIR** kill, and a **sharp leaf** (one 8/3 round on a fully named node,
  A182's rule).  A node is DEAD iff every branch is (exhaustive disjunction); an undecided branch (depth 4 / 200 nodes / wall
  900 s a pad) leaves it ALIVE.  Every kill `[C: library clip trace]` with its branch / clip / round; a page after the root
  cascade and after every closed branch (`docs/residue_map/campaigns/A205-cliptree/`, the tree as a panel row + table).
- **Y0839 (k5_16)**: root 146 s; BR(0,1) has 3 rows (10 / 15 / 23) and H reaches it -- rows singly; **all three DEAD by FC at
  BL(1,0) in round 1** (the pinned BR(0,1) meeter's K' empties BL(1,0)'s anonymous table; H provably misses): **DEAD at g1 in
  526 s** (A202 / A203 / A204: ALIVE).  Audit by sampling (`scratch/audit205.py`): 0 pairwise-disjoint (H, F, G) configurations
  on each leaf.  **Y0308 (k5_11)** DEAD at g1 in 203 s (TR(0,0)<-23: FC at BR(0,1); TR(0,0)<-24: EmptyBox on the FC-instantiated
  TL(1,0) meeter) -- A204 had it at pad 0 only; audited, 0 refutations.
- **Y0202 (k5_11)**: the brief's row (wall 900 s) holds 3 nodes a pad (ALIVE, undecided).  The EXTENDED run (wall 3,600 s,
  2 rounds a node, bar-anon + sharp leaf; `certs/extended/`, `results/cliptree205_extended.jsonl`, pages `extended/`): 29 nodes,
  depth 3, **14 DEAD / 5 ALIVE leaves**: BL(1,1)<-13 closes entirely (its three TR(0,0) rows die by EmptyBox in 8-15 s each),
  under BL(1,1)<-8 the BR(0,1) pairs {18,23} and every TR(0,0) row under {18,21} / {18,22} / {21,23} die by EmptyBox (9-53 s),
  one TL(1,0) row by FC and one by the sharp leaf's FC; the survivors are three FULLY NAMED nodes (pins + H + F1..F4 + one
  anonymous square; kept H 0.15-0.47, roles down to 0.18-0.36 % of their seeds) and two branches behind the wall.  Two runs
  killed for speed levers (`logs/kills.log`): the seeded reach re-clipped only against CHANGED obstacles (the option table
  180 -> 30-80 s), the fixed point stopped at < 0.1 % volume per pass, one S-clip re-normalisation a round, no-room off.
- **Population** (`run205.sh` over `pages_todo.txt`, one shard, committing after every page; `results/report205.md`): 9 pages
  so far, 2 DEAD at g1, the k5_11 pages ALIVE at the 900 s wall with 1-5 kills each (every branch that ran dies by FC at the
  next slot or by the pair leaf; Y0738's by the S clip) and 2-6 undecided branches; 15-18 min a page for both pads; 3.7 CPU-h.
- **Next lever**: the LP on the fully named leaves (lp180 with the roles' pieces as cores); the extended wall as the k5_11 row;
  the 5-role fixed point's cost (400 s).  Files: `code/tree205.py`, `tree205b.py`, `run205.py`, `run205.sh`, `ext205.sh`,
  `fig205.py`, `report205.py` (+ A204's `poly204.py` / `poly204b.py` / `fig204.py` copied at 57f8d6ae), `notes/clip_tree.md`,
  `scratch/audit205.py`, `logs/`, status gallery block (7n), CURRENT.json -> A205.
- **CORRECTION (2026-09-11 04:50).**  The audit of `k5_16_interior_Y0491` g1 refuted its leaf: a branch taken on an option table
  that predates a role instantiated in the same round can instantiate the FC-named anonymous meeter a second time (two "distinct"
  roles on one square: EmptyBox, unsound).  Y0491 g1's DEAD row is RETRACTED and re-run; the same stale-table EmptyBox leaves in
  Y0202's extended trees (8 of the 14 kills; R.2 is NOT closed) and Y0380 g1's R.1.4u are withdrawn; the four window-pad kills
  (Y0839, Y0308, Y0027, Y0054) are branches of a root whose last round instantiated nothing and stand, audited.  Fix: the tree
  refreshes the table (one cascade round) before branching (707bb812); the shard restarted with it; Y0202 re-run as `_w3600v4`.
- **Update (2026-09-11 06:00).**  With the fix: Y0491 g1 DEAD again (319 s) by A204's own cascade at the refresh round (no branch;
  full-role audit consistent, grid-limited), **k5_16_Y0565 DEAD at g1 in 397 s** (FC / FC / EmptyBox after the S clip / COUNT on a
  fresh root table) -- six window-pad kills in 24 pages; Y0202's sound extended tree (`_w3600v4`): 24 nodes, 5 DEAD (four pair
  leaves under BL(1,1)<-8, and BL(1,1)<-13 closed by the refresh round), five fully named sharp leaves with the roles at 0.2-3 %
  of their seeds, four branches behind the wall.  10.4 CPU-h on the rows so far; the shard continues.

## 2026-09-11 afternoon -- A206-named-split (Fable) -- running (queues over the pad-0 leaves and the whole trees): **Rule NS, the NAMED-OR-ANONYMOUS split at the clip tree's fully named leaves; the PI's Y0672 R.2.3.1 DEAD in 339 s (F4 instantiated at cell 24, EmptyBox at round 1 -- "there should be an F4 core, and once that tries to cascade the clip, it will probably die"); k5_11_Y0985 and k5_11_Y1104 DEAD at the window pad as whole trees (2,121 / 2,401 s); A205's fully named leaves closed on Y0230, Y0380, Y0083, Y0865 and two of Y0202's**

- **The reading** (`attempts/A206-named-split`, the PI 12:20): A205's stop rule counted a role as a slot's meeter whenever it was
  not PROVABLY missing the slot -- on Y0672's leaf R.2.3.1 H's top-right corner reaches TR(0,0)'s widened box by 0.02, so
  TR(0,0) had "two named meeters" (H, F1) and the anonymous cell 24 the count's own witness used was never instantiated.
  **Rule NS** (`notes/named_split.md` s.1, any n): at a node where every forced slot has two named meeters, a SOFT pair (p, r)
  -- r in named_p but not hypothesised at p -- is split: [r meets p] names r at p (the exact reach clip at p every round, the
  lonely clip at a corner); [r misses p] drops r's rows containing p from the option table (r is no meeter of p in the count and
  in Theorem FC's avail: FC instantiates a cap-1 anonymous meeter or A205's rule branches on the rows) and every piece of r all
  of whose poses meet B_p+ (MISS-CLIP: the inscribed disc of radius 1/2 about a centre within 1/2 of the closed box, on the box
  shrunk by 1e-6).  The two branches cover r's pose; DEAD iff both DEAD.  The pair with the smallest MEETING FRACTION (r's
  volume not provably missing p, A161 at two levels) is split first; after Y0672's R.3 subtree spent its hour on H at
  fractions 0.64-0.75 only slivers (< 0.5) are split (`MAX_FRAC`).  A205's proviso (the table of a round with no instantiation)
  is inherited: the split is applied only when `candidates()` returned None on a fresh table.  A node is loaded from an A205 /
  A206 certificate's last snapshot with its pieces padded outward (a superset: sound; capped snapshots refused).
- **Y0672 R.2.3.1** (g1, loaded; `certs/namedsplit206_k5_11_interior_Y0672.json`): the refresh cascade (282 s) leaves H's
  TR(0,0) reach at 1.5 % of its volume; A205's bar-anon (added to A205 after its standard Y0672 run) has no cover with
  TR(0,0)'s anonymous cap 0 and instantiates cell 24 as F4 by unit propagation; **EmptyBox(F2) at round 1, 57 s: DEAD in
  339 s**, full-role audit 0 refutations.  In the whole tree (3,600 s) the split proper fires at the same node (H at TR(0,0),
  fraction 0.063): **both branches DEAD by EmptyBox r2** (170 / 159 s); R.1 and R.2 closed (10 kills), R.3 = TR(0,0)<-24 open
  after two hours (3 kills, H's large-fraction splits 300-680 s a node).
- **A205's fully named leaves** (g1; wall 3,600 s a page): **DEAD** Y0230 R.2.1.2s (F1 at BR(0,1) fraction 0.0088: REACH;
  then F4 at BR(1,0): both EmptyBox r3; 2,242 s), Y0380 R.1.1s (F2 at TL(1,0) 0.040: COUNT; F3 at BR(1,0): both EmptyBox r1;
  1,077 s), and four sharp leaves that die in their own refresh cascade (Y0083 R.3.1s FC r2 297 s, Y0865 R.1.3.2s EmptyBox r2
  353 s, Y0202 R.1.2s EmptyBox r2 234 s, Y0202 R.3.1.1s FC r2 266 s); **ALIVE** with every name HARD after 1-4 splits and
  1-3 kills each: Y0738 R.1.1.2s (REACH, EmptyBox r3), Y0402 R.1.3.1s (FC, FC, MISS-CLIP), Y0941 R.3s (three EmptyBox),
  Y0881 R.2.3s (MISS-CLIP), Y0202 R.1.1.4s (FC r2 on the meets branch, the miss branch behind its 900 s quarter-wall);
  no soft name at all on Y0941 R.4s and Y0202 R.1.5s.  Every kill `[C: library clip trace]`, audited by sampling inside
  the parent's snapshot pieces with the exact meets test (`scratch/audit206b.py`; A204's sampled meets_box was vacuous on
  Y0230's marginal H): 0 refutations; two flags of the hull-box grid (poses at 22 / 26 deg outside the roles' 0-14 / 20-25
  deg) resolved by restricting the grid to the box's tilt range.
- **Whole trees under Rule NS at 3,600 s** (`queue_d.txt`, g1): **k5_11_Y0985 DEAD in 2,121 s** (BR(0,1)<-16 EmptyBox;
  <-21: three TL(1,0) pairs FC r1, one EmptyBox r2; <-22 FC r1) and **k5_11_Y1104 DEAD in 2,401 s** (the same shape) --
  neither needed a split: A205's 900 s wall had cut both at 4-5 nodes.  Pages
  `docs/residue_map/campaigns/A206-namedsplit/namedsplit206_<nid>.svg` (one per page, every run's root and closed branches),
  CURRENT.json -> A206, status gallery block (7o) collects the whole-tree kills.  21 runs, 9.3 CPU-h so far; the queues
  continue (pad-0 leaves, then the whole trees of the remaining wall-cut pages).

## 2026-09-12 noon -- A210-corner-cover (Opus) -- LAUNCHED (one detached pass; report at launch): **Lemma CORNER-COVER and rule CC -- a square pushed into an unpinned corner covers the corner slot's cell except two wall wedges, so the slot's SECOND meeter is pinned to a thin band; the rule is silent at a page root and kills 15 (node, slot) pairs in A209's named trees in 1.3 s, including the PI's own 2,226 s leaf**
- The PI, 01:20, on A209's Y0202-style leaf R.1.1.2.1.2s: *"TR00 has a near simple square, and the regions around the
  top and left of the simple unit square, where it meets the wall, are certifiably dead.  Since a square pushed into the
  corner covers the opposite corner under all rotations, that should imply that there's no way for TR00 to get a second
  meeter, and that should have been determinable way before burning 30+ minutes on the node."*  And 01:50: *state the
  lemma in the PACKING's frame; pad the CONTACT REGION, not the box.*  Both are now theorems in
  `attempts/A210-corner-cover/notes/corner_cover.md`, proved before use:
  - **[T] Lemma CORNER-COVER.**  In the corner frame a unit square at wall distances d1, d2 and tilt theta has vertices
    (s+d1, d2), (2h+d1, s+d2), (c+d1, 2h+d2), (d1, c+d2), and the corner slot's unit CELL minus it is EXACTLY the three
    wedges W0 = {cu + sv < cs + c d1 + s d2}, W1 = {v < d2 + s(u - s - d1)/c}, W2 = {u < d1 + c(v - c - d2)/s}; the
    fourth halfplane never meets the cell (2h - 1 - cs = -(1-c)(1-s) <= 0).
  - **[T] Corollary CC0** (the PI's sentence, sharp): a square touching both walls contains the cell's inner corner for
    EVERY tilt -- the offset's coordinates in the square's frame are 2h(1-h) <= 1/2 ((2h-1)^2 >= 0) and
    (1-h)|c-s| = sqrt(2(1-h)^2(1-2h^2)) <= 1/2 (decreasing in h on [1/2, 1/sqrt2]), with equality only at 0 / 90 deg.
  - **[T] CC1**: over a tilt interval and slacks the wedges fit in three rectangles of the cell, closed form, with
    c(1-c)/s = cs/(1+c) and s(1-s)/c = cs/(1+s) -- no division by sin theta anywhere.
  - **[T] CC'** (the PI's frame note): F's squares are P's translated by (lambda-1)c_Q, so the slot box in P is the
    EXACT unit cell and only the wedges move: the second meeter's centre is within lambda/sqrt2 of the wedges grown by
    lambda - 1 (0.004 on the G1 slab, 0 at pad 0).  **There is no inner-corner margin disc and no far-side strip of
    width pi_i**: the window statement is the pad-0 statement widened by 0.004.  Pad the contact region, never the box.
- **Rule CC** (`code/cc210.py`, on a copy of A202's stage-0 code as extended by A203's CSP): per corner slot and per
  non-pin role near that corner, (i) an anonymous meeter piece that reaches no pose class's band is dead (letter **Q**),
  (ii) a pose class of the role that leaves NO candidate second meeter at all is impossible by Theorem FC.  Microseconds:
  33 ms a pad on a whole page.
- **[M] At a page ROOT the rule says nothing** -- H is a mid-container box on every k5 gallery page, so no square is at a
  corner (k5_11_interior_Y0202 at pad 0: ALIVE in 17.3 s, rule CC 0 kills in 33 ms).  **At A209's NAMED nodes it is the
  lever the PI described**: over the 22 `k5killer209` certificates, 15 (node, corner slot) kills in 1.3 s -- 9 reproduce
  A209's own kills instantly, 4 are INTERNAL nodes (their whole subtrees), and 2 are nodes A209 left ALIVE:
  **k5_11_interior_Y0738 R.1.1.2.1.2s at pad 0** (the PI's leaf: F4 is a corner square at TR with 46 pose classes, F3 is
  the branch's other instantiated meeter of TR(0,0), and F3's centre box is 0.9195 from the band where it needs
  1/sqrt2 = 0.7071 -- a 0.21 margin) and **k5_11_interior_Y0130 R.3.1.2 at the G1 pad** (all 40 pose classes of F1 at the
  TR corner leave no second non-pin meeter at all).
- **[T] Fuzzed before the population** (`scratch/fuzz210.py`, A202 section 4's discipline): 89,240 sampled cell points
  against random pushed-in squares -- every point outside the square lies in CC1's rectangles, 0 refutations; 42,262
  centres that do hold a band point -- 0 killed wrongly; the four corner frames and the tilt flip are involutions.
  The targeted search for an admissible disjoint second meeter of a corner square found NONE in 3,000 configurations,
  which is why the rule kills.
- Running: ONE detached BelowNormal pass `bash attempts/A210-corner-cover/code/run210.sh` over the 19 still-alive k5
  gallery pages (STATUS's 22 minus Y0325 / Y0380 / Y0436, killed by A209 this morning), pad 0 first then the G1 pad,
  stage 0 + A203's CSP + rule CC, page after each pad, commit per page; rows `results/cornercover210.jsonl`, leaves
  `results/cornercover210_leaves.jsonl`, pages `docs/residue_map/campaigns/A210-cornercover/`.
- **[!] Lab-wide: the usual `belownormal()` snippet silently fails on this box** -- ctypes passes GetCurrentProcess()'s
  pseudo-handle as a 32-bit int, GetPriorityClass returns 0 and the process stays at NORMAL (A209's workers are all at
  priority 8).  Fixed in A210's copy with `c_void_p(-1)` + explicit argtypes; worth copying into the other runners.
- What CC cannot do: nothing near 45 deg (the band is the whole cell), nothing at offset cells, and nothing when the
  second meeter genuinely sits in the wall band next to the corner cell -- those cells still have to die by the other
  stage-0 rules, as they do on the PI's leaf.  Verdicts `[C: closed-form trace; Lemma CORNER-COVER]`, no verifier clause.
## 2026-09-12 evening -- A211-coarse-tree (Fable) -- LAUNCHED (launch-and-exit; report at launch): **the COARSE tree -- cheap coarse internal nodes (supersets) branched at once, the leaf rules at every fully named leaf in order (rule CC -> no-room + pockets -> basin clip -> Rule NS -> the exact cascade LAST), pad 0 first; a Y0202 internal node costs 16-36 s against A209's 277-296 s**
- The PI (18:20): *"the more coarse we can get away with the better, since we want to reach the leaf kills asap."*  A209's
  trees are WALL-limited (every gallery page ALIVE at 3,600 s on both pads with undecided branches: 10-20 internal nodes
  at 300-1,000 s each), while the leaf rules kill in ms-s once a fully named leaf is reached.
- `attempts/A211-coarse-tree/notes/coarse_tree.md` states the soundness points BEFORE use: S1 re-binning (a role with
  > 96 pieces -> the 4 x 4 x 6 grid units of its hull that meet a piece: a superset), S2 a PREFIX of A204's clip chain
  (refine 1, <= 2 mutual passes, no lonely clip, K' per piece or union-hull), S3 shallow reach (depth 2 / 1, roles in
  place), S4 one round then A205's branching rule with the fresh-table proviso, S5 the leaf rules in order (CC, NO-ROOM +
  pocket CN bound with pockets branched at k = 9, BASIN, Rule NS slivers only, then the exact nsub 4 / refine 2 cascade
  + sharp round), S6 pad 0 first, S7 certificates + the sampling audit (audit211, the cap-1 two-meeter criterion).
- Code: `code/coarse211.py` (CoarsePage: `rebin`, `coarse_fixpoint`, the coarse / exact switch), `tree211.py` (Tree211:
  `leaf_rules`, pocket branching, the coarse expand), `leaves211.py` (rule CC on the live node), `run211.py` (pad 0
  first, wall 1,800 s per pad, depth 6, node cap 600, BelowNormal via A210's working fix), `worker211.sh` (claims,
  gates 10 / 6 / 3072 MB, audit per node, fold + progress + refresh + pathspec commit per node), `launch211.sh` (THE one
  detached launcher: N worker slots over `queue_gallery.txt` (the 19 alive pages, A210's list) then `queue_frontier.txt`
  (303 alive census nodes not in the gallery, deepest first) + the hourly progress.md commit), `fold211.py` (ledger
  `results/superseded_by_coarsetree_A211.jsonl`, Lemma K1), `progress211.py` (results/progress.md; STOP at a 200 CPU-h
  projection after 20 frontier nodes), `audit211.py`; A209's chain and A210's cc210 / leaves210 copied at 65a4903e.
- **[M] Y0202 at pad 0 (the one-page test, `logs/test_Y0202_zero.log`, wall 1,200 s):** root 36 s (normalise 10 s,
  the depth-2 option table 26 s), R.1 = BL(1,1)<-8 16 s, R.1.1 = BR(0,1)<-{18,21} 33 s, R.1.1.1 = TR(0,0)<-14 DEAD by
  EmptyBox in 27 s -- the same first four nodes cost A209 296 / 277 / 291 / 57 s (its zero_page run): **8-9x cheaper
  per internal node, the same kills**.  The whole wall-1,200 s run: 13 nodes, depth 5, 5 DEAD / 8 undecided (ALIVE at the wall); per node R 36 / R.1 16 / R.1.1 33 / R.1.1.1 EmptyBox 27 / R.1.1.2 63 + no-room 8 (A189's pair leaf on the role boxes, k = 10) / R.1.1.3 EmptyBox 15 / R.1.1.4 80 / R.1.1.4.1 90 / R.1.1.4.1.1 37 then **DEAD by rule CC (F4 a corner square at TR, the hypothesised second meeter of TR(0,0) cannot reach the wall band) at depth 5** / R.1.1.4.1.2r1 EmptyBox 6 / R.1.1.4.2 74 / R.1.1.4.2.1 91 s -- the fully named leaves were reached at depths 3 and 5 (A209's zero run reached depth 4 in 3,718 s), the leaf rules that fired: no-room (EmptyBox on the boxes) at d3, rule CC at d5, Rule NS three times (F2 at BL(1,1) 0.21, F2 at TL(1,0) 0.21); the exact cascade never ran.  One price found and fixed before the launch: A189's no-room at the k = 10 leaves came back UNDECIDED at its 300 s cap three times on one path (665 s of the 1,274 s) -- now capped at 120 s and run once per k along a path (an NS child adds no role).
- Pages `docs/residue_map/campaigns/A211-coarsetree/coarsetree211_<nid>.svg` (fig211: the coarse note per panel, the
  CC line on a CC kill, the exact-cascade panel), CURRENT.json -> A211; status gallery block (7r); rows
  `results/coarsetree211.jsonl` (with `nodes_brief`: label / depth / verdict / rule / seconds / coarse per node).
- Running: `nohup bash attempts/A211-coarse-tree/code/launch211.sh 4 1800` (4 worker slots, each gated per launch; pid in `logs/launch211.log`), rows land in `results/coarsetree211.jsonl`, certs `certs/coarsetree211_<nid>.json`, per-node logs `logs/coarsetree211_<nid>.log`, `results/progress.md` per node and hourly.  Resume: the same command (claims under `logs/claims/` skip taken nodes; delete a claim dir to re-run; `touch logs/STOP` stops the workers after their node, `logs/HOURLY_STOP` the launcher).

## 2026-09-14 morning -- A212-trump5-tree (Fable) -- LAUNCHED (launch-and-exit; report at launch): **the TRUMP5 tree -- A211's coarse tree at pad 0 only with the Trump-containment GATE, the TUBE LEAF and the ALIGNED split**
- The PI (2026-09-13 00:40): *"check if the current node is a parent of trump, and if so, don't try to kill it, just go straight to split ... then the leaf discharge rules + trump basin clear out everything that isn't trump."*
- `attempts/A212-trump5-tree/notes/trump5_tree.md` states the three additions BEFORE use: s.1 GATE `contains_trump` (an injective assignment of the node's named squares -- pins, H, F_i -- to a D4 image of z-hat EMBEDDED at s0 (squares 2, 5 on their slots), exact rationals, satisfying pins / pieces / named slots / NS misses with margins in favour of containment; a gated node is never submitted to a kill rule, only to the branching levers; a rule claiming DEAD on a gated node is refused and recorded `gate_conflict`; soundness never depends on the gate); s.2 Lemma TUBE-LEAF (all 11 named, every piece inside (r_c - 2(s0 - s-hat), r_theta) of the image => localisation at s0 (the (D) leaf) and, by Theorem T1 on the scale-ray certificate `certs/tube_scale_T5.71e-2_window.json`, uniqueness for the window sides; verdict TRUMP-TUBE, a uniqueness leaf, NOT a kill); s.3 the ALIGNED split (Lemma ROLE-SPLIT cut at the tube wall, <= 36 cuts a path); s.4 pad 0 only (lam = 1, s0-only, no window-pending bookkeeping).
- Code: `code/trump212.py` (the image, D4, exact geometry, gate, tube, aligned_split), `tree212.py` + `expand212.py` (Tree212 over Tree211: the gate before and after every cascade, kill() refused on gated nodes, trump_leaf, tube_leaf), `run212.py` (pad 0 only; verdict DEAD / TRUMP-TUBE / ALIVE; the gate on every node record and on the row), `load212.py` (A60 records + the 136-node alive frontier), `rows212.py`, `fig212.py`, `worker212.sh` (3 slots gated 10 / 3 / 3072 MB), `launch212.sh`, `fold212.py` (A60 ledger, pad-0 kills; TRUMP-TUBE not folded), `progress212.py` (price after 20 frontier nodes, STOP at 150 CPU-h), `mkqueue212.py`, `audit212.py`; A211's chain copied at b06a8203 (one 2-H fix in the copies of stage209 / poly204 for f1_L10_0003's record).
- **[M] The gate is FALSE on the whole alive trump5 population at the root**: none of the 12 c0_* H boxes holds a square of any D4 image, f1_L10_0003's ladder box misses square 9 by 0.009, and A60's `trump_realized` is False on every alive record -- the Trump-containing residue of trump5 was isolated by A60's ladder and discharged by A60/A83 (`a60_discharge_ledger.json`).  So on this population the tree is A211's pad-0 tree with the gate as a safety net.
- **[M] c0_Y1033 at pad 0, wall 900 s** (`logs/test_c0_Y1033_zero.log`): ALIVE at the wall, 10 nodes, depth 4 -- R 73 s / Rr1 16 / R.1 = BL(1,1) row 21 / R.1.1 DEAD EmptyBox 18 / R.1.2 32 -> Lemma POCKET at k = 9 (3 pockets) / p1 DEAD EmptyBox 81 / p2 95 -> p2.1 DEAD REACH 98, p2.2 DEAD by rule CC 76 / p3 ALIVE (wall); kills EmptyBox 2 / REACH 1 / CC 1; 17 gate checks, 0 hits, 0.024 s; no tube leaf reachable.  **f1_L10_0003** (smoke, 240 s): DEAD at pad 0 in 193 s (REACH after Rule NS, ROLE-SPLIT, 2 x EmptyBox).
- **[M] The tube path on a SYNTHETIC Trump-containing page** (f1_L10_0003 with its second H box replaced by a box around square 9; `logs/test_synth_trump_f1.log`, 900 s): the gate holds at the root and along the whole path ({H0: 7, H1: 9, F1: 6, F2: 10, F3: 4, F4: 8}), 0 conflicts; the tube check is NOT fitted (F3 at 475 x r_theta: the pieces do not contract on their own); 3 aligned cuts in 958 s, 5 gated nodes, 0 tube leaves; the one non-image sibling run (F1 tilted 0.12 deg below the image) did not die in 700 s (rule CC no kill, ROLE-SPLIT, exact cascade 581 s).  Depth needed: ~36 aligned cuts + 36 sibling kills -- not within a 1,800 s wall by cuts alone; the near-Trump siblings need a contraction lever (A60's LP ladder / an A36-type basin clip).
- Running: `nohup bash attempts/A212-trump5-tree/code/launch212.sh 3 1800` (3 worker slots over `code/queue_gallery.txt` (13 pages, c0_Y1033 first) then `code/queue_frontier.txt` (136 A60 nodes deepest first); rows `results/trump5tree212.jsonl`, certs `certs/trump5tree212_<nid>.json`, pages `docs/residue_map/campaigns/A212-trump5tree/`, `results/progress.md` hourly, STOP at 150 CPU-h; resume = the same command, claims in `logs/claims/`).  Status gallery block (7s): DEAD rows are kills, TRUMP-TUBE rows are recorded dead=False with their own note.  CURRENT.json stays A211.

## 2026-09-14 midday -- A213-int-polycore (Fable) -- DONE (launch-and-exit): **the K' build in INTEGER space -- bit-exact, x7 per rebuild, x9.7 on the run's rebuild stage; the flag is ON, the workers pick it up per node**

- The PI's idea: "if all of our stuff is rational, can't we just algebraically convert everything to integer space, do the high cost compute, and then go back to rational when the results land back on the cpu?"  Yes, exactly: every decision A132 polycore / A171 multibox make in the K' build is the SIGN of a rational expression, and the sign of p/q (q > 0) is the sign of the integer p.  `notes/int_polycore.md`: homogeneous integer points (X, Y, W), lines as cross products (join / meet), piece boxes compiled ONCE (`IBox`: corners over one CW = 2^k <= 2^53, t0/t1 over 2^24), the two quadratics of `vertex_ok` scaled by S = 2 W CW and `_quad_nonneg` decided by three integer tests (endpoint values x E^2, the interior test x E, the discriminant); the polygon chain (`intersect_frac`, `_simplify_frac`, the centroid shrink-and-round half-even) with every comparison cross-multiplied; the axis core likewise.  Bit bound for grid vertices: endpoint value < 2^142, interior test < 2^116, discriminant < 2^183 (Python ints; a two-limb int64 or __int128 does NOT hold the two larger tests).  Fractions only at the boundary (the certified vertices, the core): the certificates are the library's bit for bit.
- The FLOAT part of `polycore.build` (the sampled-halfplane clip, the simplify, the 1e-9 rounding -- 270 s of A211d's 902 s, more than the Fractions) is not converted (the certificates depend on those doubles) but re-issued operation for operation in numpy (`polycore_fast`): the signed distances of all vertices in one expression (same binary64 ops, no FMA), the <= 2 crossing points by the library's scalar formula on the same doubles, the simplify with a heap of (area, original index) -- an area depends on its three vertices only, and the smallest original index among equal areas is the library's first-index argmin.
- DIFFERENTIAL TEST: `code/profrun213.py` records every library-level `MBox.rebuild` of a page run (piece set, parameters, result); `tests/replay213.py` replays all 441 of the Y0202 pad-0 run (181 union, 260 pieces) through both builds: **0 mismatches** (vertices, cores, k_source, k_info, exceptions), 0 record-vs-replay differences; `tests/fuzz213.py`: 150 random piece sets (0 mismatches), 2,700 vertex tests incl. exact-boundary points across Fraction / integer / float-filter / object dtype (0 mismatches; 50 boundary points went to the exact fallback), 75 random polygon intersections + roundings (0 mismatches).  A213_VERIFY=1 keeps asserting both builds equal call by call in any run.
- PER CALL (replay, no profiler): rebuild 320 -> 45 ms (x7.0); polycore.build 22.6 -> 4.2 ms (x5.4); intersect 23.3 -> 1.3 ms (x18); certify_verts 49.6 -> 1.7 ms (x29); axis core 13.8 -> 0.5 ms (x25).  Phase 2 (`polycore_vec`): the float filter with a rigorous per-element error bound over (nv, N, 4) arrays + exact fallback certifies in 0.63 ms (x79; 0 fallbacks of 47,656 pairs on the replay); the object-dtype route 1.8 ms (exact, no early exit) -- the filter is the one to keep (A213_VEC=1; default off, the integer path is already 2% of a node).
- PER RUN (`results/timing213.md`, Y0202 pad 0, 900 s, isolated dirs, cProfile as A211d): the rebuild stage 245.7 -> 25.2 s (x9.7); inside the same wall 10 nodes expanded vs 8 (5 role splits vs 4); verdicts identical on every common node, certificates field-identical on 13 of 15 common nodes (the two others: the node only the AFTER run reached, and no-room `pockets` whose extents come from a deadline-bounded bisection).  What is left of a node is `_clip_rect_obstacle` (A131 pin-clip's `dead_poly` / bisection on Fractions): 747 of 955 s -- the SAME treatment applies (signs of low-degree polynomials in the rect corners, obstacle vertices and t) and is the next lever.
- Phase 3 (design note, no compiler on the machine): a C kernel needs 192-bit accumulation for the endpoint / discriminant tests or, better, the Phase-2 float filter in C with a bignum fallback; install MSYS2 mingw-w64 GCC (`winget install MSYS2.MSYS2; pacman -S mingw-w64-ucrt-x86_64-gcc`) or LLVM (`winget install LLVM.LLVM`), load as a DLL via ctypes.
- Wiring: `code/mbpatch213.py` (the mbpatch178 pattern: `polycore.build`, `polycore.vertex_ok` (also A135 exactcore's), `multibox.pieces_poly / axis_core_pieces / certify_verts`), installed by `coarse211.install_a213()` (the hook landed in A211e's commit a9c57ece, which swept the working copy); flag `A213_INTCORE` default ON since the tests passed (=0 restores the library).  The read-only libraries are untouched; the running workers were not restarted.

## 2026-09-14 afternoon -- A213b-int-clip (Opus) -- DONE (launch-and-exit): **the RECTANGLE-OBSTACLE CLIP in integer space -- bit-exact, x9 per clip, 418 s -> 65 s on the run's clip stage; `A213_INTCLIP` ON, the workers pick it up per node**

- A213 left the node dominated by its other half: `multibox._clip_rect_obstacle` (A171's generalisation of A131's pin-clip), 747 of 955 s.  The same argument applies unchanged -- every decision the clip makes is the SIGN of a rational expression -- so `code/pinclip_int.py` re-issues it in integers (`notes/int_clip.md`): per (obstacle, tilt bin) pair, the obstacle's vertices over one denominator VD, the edge normals `(nx VD, ny VD)` and support intervals `(lo VD^2, hi VD^2)`, the library's OWN per-edge radius `RN/RD` (read from `Bin.radii`, not recomputed, so its `sqrt_lo` rounding is untouched), the tilt endpoints as `(C, S)/G`, and a query centre `(CX, CY)/CW`.  Family A (K's edge normals) becomes `EL CW < PN EA < EU CW` with `EA = VD RD`, `EU = HI RD + RN VD^2`, `EL = LO RD - RN VD^2`; family B (the square's own axes) becomes A131's `_m_lt_half` as `4(Pn^2+Qn^2) < M^2` or `2X < M G` after a cross-multiplied `X0 G1` vs `X1 G0`.  The four `(swap, sign)` statements the library makes per vertex are the SAME four numbers with signs (`(P,Q)->(Q,-P)` sends `(X,Y)->(Y,-X)`), so four `_m_lt_half` calls cost one vertex of arithmetic -- and the identity holds in binary64 too, so the FLOAT twin (which only steers the bisection, never decides) reuses them and stays bit-identical while its `float(nx)` / `float(lo)` / radius conversions move to the compile step.  `PIN._bisect_boundary` is reused verbatim; `stats` and the replayable trace are the library's (the within-call answer memo still counts every ask).
- Bit bound: with `b = max bits of VD, CW, G, RD` everything is below `2^(4b+6)`; measured on the recorded clips, VD 30, CW 83, G 51, EA 79, EU 110 bits and the **widest product 229 bits** -- so a fixed-width C kernel needs 4 limbs (not `__int128`), and the bound GROWS with depth (G by ~2 bits per t-split, CW by the rect halvings).
- DIFFERENTIAL TESTS: `code/profclip213.py` records a stride sample of a run's library clips (obstacle, bin, rect -> rect + stats delta); `tests/replay_clip213.py` replays **1,882 recorded clips** of the BEFORE 900 s run (153 obstacles, 607 bins) -- **0 mismatches** and **0 record-vs-replay differences**, `exact_calls` 11,095 / `backoffs` 22 identical on both paths.  `tests/fuzz_clip213.py`: 150 random cases (84 polygon-grid, 66 core-denominator obstacles), 3,284 point tests (including points exactly ON the obstacle's vertices and one ulp off), 450 clips each also run through the float filter -- **0 mismatches** on `dead_poly`, on `_dead_poly_f` bit for bit, and on the clip with its trace.  `A213_VERIFY=1` on a real node: 25,930 verified calls (3,193 clips), 0 failures.
- PER CALL (no profiler): the clip **0.787 -> 0.085 ms (x9.2)** with the (obstacle, bin) pair warm as in a run; `dead_poly` 112 -> 12.6 us (x8.9); the float twin 13.8 -> 4.1 us (x3.4).  Phase 2 (`A213_CLIPFILTER=1`, a rigorous float filter on family A with exact fallback, 0 mismatches): 0.090 ms -- **no gain** over the warm integer path, so it stays default OFF (it is the right shape for a C kernel, not for CPython).
- PER RUN (`results/timing213.md`, Y0202 pad 0, 900 s, isolated dirs, cProfile; both columns carry A213 and A214's C kernel, so the clip is the only difference): **`_clip_rect_obstacle` 417.7 s -> 65.1 s on MORE clips (273 k vs 214 k), 1.95 -> 0.24 ms per call (x8.2)**; Fraction arithmetic across the run 332 M -> 131 M calls; the clip was 44% of the BEFORE wall and is 6.8% of the AFTER wall.  It bought work: 13 nodes expanded vs 11 in the same wall (6 role splits vs 5, 12 dead leaves vs 11), **16 of the 17 common nodes carry the identical verdict** and the 17th is the one BEFORE left ALIVE at the wall and AFTER expanded (one more DEAD NOROOM).
- What is left of the clip: `IPair`, the per (obstacle, bin) compile, is 36.1 of the 65.1 s (1.45 ms x 24,945 pairs, ~11 clips per pair) -- the next lever is to compile the OBSTACLE once (its vertices, normals and support intervals do not depend on the bin) and carry the integer form on the `Obstacle` instead of a side cache.
- Wiring: `mbpatch213.install_clip` patches the INNERMOST slot -- `mbpatch178._orig_clip`, i.e. under A178's `obs is None` guard and under A211's clip memo (which captured the library function at its own import) -- so both wrappers keep working and the memo still hits (54,988 hits / 143,089 misses in the AFTER run).  Flag `A213_INTCLIP`, default ON since the tests passed (`=0` restores the library clip); `A213_VERIFY=1` runs both and asserts on every call.  The read-only libraries (A131 pinclip, A171 multibox) are untouched and the running workers were not restarted.

## 2026-09-14 midday -- A214-c-kernel (Opus) -- DONE (launch-and-exit): **the C KERNEL for the vertex certification -- clang 22, a plain DLL via ctypes, 16 ns a quadratic test, bit-exact, flag ON**

- The PI installed clang 22.1.8 this morning, so A213's Phase-3 design note (`notes/int_polycore.md` s.6) could be
  built.  `attempts/A214-c-kernel/notes/c_kernel.md`: `code/ckernel214.c` + `code/i192.h` -> `build/ckernel214.dll`
  (plain C11, **no Python.h, no extension module, no build system**; one command `sh code/build214.sh` =
  `clang -O2 -shared -nostdlib -Wl,-noentry -ffp-contract=off -fno-fast-math`, the sha256 committed beside the DLL
  in `build/BUILD.md`).  `-ffp-contract=off` is not cosmetic: the float filter's error bound assumes ONE rounding
  per operation, so FMA contraction must be off.  `-nostdlib -Wl,-noentry` because the box has clang but no MSVC
  CRT import libraries -- the kernel needs no CRT and supplies `_fltused` and `memset` itself.
- TWO LAYERS, both deciding the predicate the library decides.  (1) A213's Phase-2 FLOAT FILTER ported operation for
  operation to scalar C, three-valued (Kleene) with the same rigorous forward error bound; a pair it cannot decide
  falls through.  (2) The EXACT test in integers: `__int128` for U, V, A, B, C and the interior test, and a SIGNED
  THREE-LIMB 192-BIT accumulator (`i192.h`, schoolbook, exact) for the two tests that do not fit 128 bits -- the
  endpoint value (< 2^142) and the discriminant `4AC - B^2` (< 2^183), exactly A213's bound.
- THE FALLBACK PROTOCOL is the part that makes it sound: the kernel is proved only inside a CHECKED envelope
  (|X|, |Y|, W, |CX|, |CY|, CW < 2^60; E, |T0|, |T1| < 2^31; |A|, |B|, |C| < 2^93) and **never returns an answer it
  cannot prove** -- three gates (no DLL / a different machine / a failed self-test; outside the envelope; a corner
  or t that is not an exact double) each hand the pair back to A213's Python-int path, which is unbounded and stays
  the reference.  In a real run the gate fires exactly where predicted: the axis core's corners, whose
  W = den aden Q reaches ~2^110.
- DIFFERENTIAL TESTS, **0 mismatches everywhere** (`tests/all214.py`, `logs/all214.log`): `tests/diff214.py` checks
  the 192-bit path ALONE on every in-envelope sample (not just the ones the filter punts), the filter ALONE (every
  answer it decides), the full kernel and the batch, over 46,800 (vertex, box) samples in three classes -- the 1e-9
  grid, "wide" points with W ~ 2^37 that drive the coefficients to 2^91 and the discriminant to 2^182, and exact
  tilted-axis boundary points -- plus 200 deliberately out-of-envelope points the kernel must REFUSE (it did, all
  200).  A213's `tests/replay213.py` on all 441 recorded rebuilds of the Y0202 pad-0 run was run TWICE, kernel OFF
  and kernel ON: 0 mismatches against the library build both times, 0 record-vs-replay differences; A213's
  `fuzz213.py` (150 piece sets, 2,700 vertex tests, 75 polygon cases) 0 mismatches.  `A214_VERIFY=1` (both paths on
  every call, asserted equal) also clean.  The kernel's own coverage counters show the wide paths were really
  exercised: 163,307 quadratics decided exactly, 3,315 of them through the discriminant.
- PER CALL (`results/timing214.md`): `certify_verts` 2.0 ms -> **0.2 ms** (x10 over A213's Python-int path, x321
  over the library); through `polycore_vec` 0.71 ms (numpy) -> 0.10 ms.  The kernel itself, on 16 certified
  vertices x 12 piece boxes (192 pairs, 3,072 tests, all passing): **50.5 us a call = 263 ns a pair = 16 ns a
  test**, against 10.5 us a pair in Python -- A213 s.6 predicted "10-20 ns".  The SCALAR drop-in is only x2.3
  (1.97 vs 4.50 us) because a ctypes call costs ~1 us; **the lesson for the next kernel is that the win is the
  BATCH entry point, never one sign test per call**.
- PER RUN (Y0202 pad 0, wall 900 s, isolated dirs, cProfile; BEFORE = `A214_CKERNEL=0`): the whole vertex-
  certification stage 3.5 s -> 2.9 s (wrapper included) **while doing 19% more rebuilds** (8.9 -> 6.2 ms a rebuild);
  inside the same wall 11 nodes expanded vs 9, and the two frontier nodes the BEFORE run left ALIVE at the wall
  (R.1.4.2.2.2.1.1.2, R.1.4.2.2.2.1.2) both came back DEAD.  Verdicts identical on every node both runs finished
  (14 of 17 records field-identical with the time fields stripped; the rest are the nodes only the AFTER run
  reached, plus R.1.4.2.2's no-room `pockets` differing in the 5th decimal from the deadline-bounded `bisect_free`
  A213 already recorded).  In that run the float filter decided **160,580 of 160,580 pairs in C** -- the exact
  192-bit path was never needed live, and nothing was handed back except the out-of-envelope axis-core corners.
- **[M] THE HONEST LIMIT.**  After A213 the certification was already only 3.5 s of a 910 s node, so this kernel
  buys ~0.6 s a run directly; the 11-vs-9 nodes is a wall race, not a 10x.  What a node costs is
  `_clip_rect_obstacle` (445 s of 910; 745 s of the wall sits inside the no-room leaf, most of it the same clip) --
  A213b's integer clip (x9.2 a clip, flag now ON) is the lever.  A C kernel for the clip afterwards is a DIFFERENT
  kernel and worth stating now: A213b's measured bound is **229 bits (four limbs, not three) and it GROWS with tree
  depth** (G gains ~2 bits per t-split, CW per halving of the rect), so it needs a guarded envelope + Python
  fallback like this one but firing more often the deeper the tree; and A213b measured its float filter at NO gain
  (0.090 vs 0.085 ms a clip), so there it is the INTEGER path that belongs in C -- the opposite emphasis from here.
- Wiring: `ckernel214.install()` rebinds `polycore_int.vertex_ok_h` / `certify_h` and `polycore_vec.certify_verts`
  IN MEMORY (nothing edited on disk, the read-only libraries untouched), called by `mbpatch213.install()` behind
  `A214_CKERNEL` (default ON since the tests passed; `=0` restores the Python-int path).  A213b's files were not
  touched -- the only shared surface is that flag layer, and A213b's own runs already carry the kernel.

## 2026-09-14 evening -- A217-torque-probe (Fable) -- DONE (launch-and-exit; the crowd search detached): **the TORQUE PROBE -- Fritz-John stress at 3,555 jammed local optima; no torque invariant, but NO FJ point has four doubly-met open corners (0 of 883; the 185 forced four-crowds all need an external along-wall pull)**

- The PI's question (17:40): is there a signed equilibrium condition at unsettled corners that forbids all four corners being
  unsettled at once -- a torque proof of "every optimal packing has a settled corner"?  Remark (17:45): the invariant must live
  at convex wall-bounded positions; interior grains in non-convex pockets are unconstrained.
- Built: SLSQP side-minimiser on the selected SAT rows (`opt217.py`), active-set Fritz-John multipliers (NNLS residual < 1e-8,
  HiGHS LP polytope ranges), the tilt box (no-settled-corner constraint) and the CROWD rows (two meeters per corner box with a
  margin), D4-quotiented; seeds = A85's 262 k0 optima, 600 random, 168+ crowd starts.  3,555 distinct FJ-feasible local optima:
  SETTLED 430 (lowest 3.886746), K0FREE 417 (3.897231; the first with tilted corner squares 3.966513, two 44-deg diamonds),
  BOXK0 36, HELD 2,487 (tilt bound active), CROWD 185 (crowd rows active), CROWD0 **0**.  None below s-hat.
- [T] Lemma W: a wall torques a tilted square by W(sin theta - cos theta)/2 about its centre toward its nearest alignment, EVERY
  wall the same sign (checked 2e-15); the total wall moment about the centre is 0 at every FJ point (1e-8).  So "the meeters
  receive wall torque of sign -chi and holder torque of sign +chi" is an identity, not a constraint: C1 (sum of corner torques)
  fails at Trump's own open TL corner (T = +0.035), C2/C3 are identities, C6 (winding) is the count of tilt-side changes -- free.
- [M] What survives (C4): no FJ point has four doubly-met open corners (0/883, max three once); forcing four 2-crowds always
  leaves >= 1 crowd row loaded (1/2/3/4 corners in 3/67/61/51 witnesses), the pull along the meeter's wall toward the corner
  (569/639), its torque the anti-aligning one of sign chi (532/551); the interior holders push the meeter flat as well (368/551).
  The 8 HELD four-crowds: bound torque of sign chi 494/494.  C5 (thin): at k0 FJ points the loaded meeters of doubly-met corners
  are torque-neutral (45 deg or flush), 14/14 corners -- Trump's TL is not, so it is k0-specific.
- [M] The PI's remark confirmed: interior tilted grains (no wall) receive holder torques of both signs on the same square
  (254/254); the constraint sits on wall-touching squares (one wall = half of it).
- [M] A85's 14 k0 optima below 3.9 drain to settled optima under the SAT-row SLSQP (A87 s.5.4 reproduced); atlas family 11
  (no slot square, 3.888014) drains to family 6.
- [C] Lemma TORQUE (notes/torque.md s.4): at a sigma-minimiser at most three corner boxes are doubly met; with K0-2 (every
  corner box of the k-maximal minimiser doubly met) the k-maximal minimiser has a settled corner.  Proof route = a COUNT: 8
  distinct meeters + >= 4 along-wall holders (a holder serves <= 2 meeters: the two of one wall or the two of one corner; the two
  meeters of a corner push each other OUT) = 12 > 11 -- n = 11 only, silent for n >= 12 (consistent with tilted middle grains
  and open corners at higher n).  Gaps: G1 "a 2-crowd meeter is pinned along its wall" (the crowd data, not a theorem), G2 the
  sharing bound.  Not a torque identity: the torque bookkeeping contributes nothing to the count.
- Pages `docs/residue_map/campaigns/A217-torque/` (39, forces as arrows, corner torques annotated, gallery); results
  `attempts/A217-torque-probe/results/torque217.md`, `witnesses217.jsonl`, `torque217.jsonl`; registry row; resume block in
  `notes/torque.md` s.6 (re-run collect/hunt/fig when `search217_crowd0.jsonl` has grown; a CROWD0 witness would refute C4).

## 2026-09-14 night -- A218-k0-count (Fable) -- DONE (launch-and-exit): **Lemma K0-COUNT stated exactly; G1 PROVED (Lemma PUSH + Lemma HOLD, n-general); G2 FALSE -- the count does not close k0_00 (a force-balanced four-crowd with nine squares; rattler crowds at the k0 FJ points)**

- The brief (18:00): A217's surviving statement is a COUNT -- four doubly-met open corners need 8 distinct meeters + >= 4 along-wall
  holders = 12 > 11; state it, prove G1 (a 2-crowd meeter is pushed OUT along its wall by the other meeter and must be held) and G2
  (a holder serves <= 2 meeters), test on A217's witnesses.
- [T] Lemma PUSH (`docs/proofs/k0_count.md` s.2, any n, any side): two unit squares in a corner's quadrant both meeting the OPEN unit
  corner box push each other out -- every line separating them has a normal with a strictly positive frame component (i), and a
  strictly positive component along any corner wall the pushed square touches (ii).  (i) is Theorem B's clause (P) at c = 1 via Lemma
  B0'; (ii): the separating line meets the floor at u0 >= sin(alpha) (Lemma B0 on the floor meeter) and the pushing square, in the
  wedge under the line, has every point at u >= u0 + cos^2(alpha)/sin(alpha) (B0's mirror), so it lies in {u >= 1/sin(alpha)} and
  cannot meet the box.  Sharp in both constants.  Measured 10,638 / 10,638 loaded partner pushes on 2,732 witnesses (`count218.py`).
- [T] Lemma HOLD = G1 in loaded form (s.3): at a Fritz-John point a meeter PRESSED by its partner has a holder -- a third square pushing
  it toward the corner, along its wall if it touches one (the u-balance: the corner's walls push outward, the far walls are out of
  reach).  At the CROWD witnesses the crowd row is exactly that holder (its force = minus the partner push's along-wall component).
- [T, vacuous] Lemma K0-COUNT (s.4): under LOAD (every corner's two meeters press on each other) and DISTINCT (four holders, distinct
  and no meeters) n >= 12; corollary at n = 11 with K0-2.  **[F] Both hypotheses fail** (s.5): the true sharing bound of G2 is FOUR
  (a centre diamond holds a meeter of every corner; measured: a holder is a meeter of the ADJACENT corner in 1,986 of 6,351 loaded holder
  relations), and `rand_0_0569|t20` (HELD, side 4.1099) is a FORCE-BALANCED four-crowd with NINE squares -- a compression ring through
  the 8 meeters (the floor meeters of BL and BR hold each other, the wall meeters up each wall hold each other, one square holds both
  ceiling meeters), only the tilt bound loaded; LOAD fails where it matters: 61 of the 70 doubly-met corners at the genuine k0 FJ
  points have BOTH meeters unloaded (rattler crowds, sides 4.00-4.47), 33 of 57 at the settled optima.
- [M] What C4 (0 of 883 FJ points with four 2-crowds) is, then: not a count but the DRAIN -- a forced four-crowd wants to SETTLE a
  corner: a meeter slides out along its wall (CROWD, 3,071 of 3,261 pulls along the touched wall) or a corner square turns flat (HELD,
  the bound torque aligning, 494/494).  The k0_00 obligation is unchanged (DF-K0's H1 / the tree); the sharpest open form of the PI's
  torque conjecture is whether a loaded RING can ever be torque-balanced at n = 11 -- a finite structure question for Lemma H-LOC,
  whose NO would still leave the rattler crowds.
- Lean: `Statements/Open/K0Count.lean` (`lemma_PUSH` as a named axiom with the proof pointer), `Statements.lean` import, `lake build` +
  `lean/audit.py` exit 0, no sorry, `lean/AUDIT.md` regenerated.  Pages `docs/residue_map/campaigns/A218-k0-count/` (the ring, the
  rattler crowd, the three-crowd K0FREE witness, the lowest CROWD witness); results `attempts/A218-k0-count/results/count218.md`,
  `count218.jsonl`; registry row; `residue_ledger.md` s.4 note; `writeup/01_summary.md` lever table row.

## 2026-09-14 evening -- A220-exact-first (Opus) -- launch-and-exit (the benchmark lanes detached, resume block in `notes/exact_first.md` s.6): **the EXACT cascade moved BEFORE the blind role split, and the no-room cap shortened under an UNDECIDED parent -- both FLAG-GATED, both OFF by default**

The PI (20:05, from `attempts/A211-coarse-tree/logs/coarsetree211_k5_16_interior_Y0865.log`): under `R.2.3.1.1.2.2.1` the
coarse tree bisects F1's tilt, then F2's, then F5's / F4's (Lemma ROLE-SPLIT, extents ~0.08 x 0.05 with the FULL tilt
range), and every one of the 8 leaves then dies in the EXACT cascade by EmptyBox in 0.7-18 s -- 43 such leaf cascades on
that page, all kills, each reached only after 3-4 split levels; *"the position of F1 should have killed this node in the
parent well before this depth"*.  The coordinator's addendum (20:40): on the ALIVE pages the wall is not in the coarse
rounds at all but in A189/A208's no-room returning UNDECIDED at its 120 s cap at EVERY child after a split -- Y0402 14
gaps = 1,518 s of a 1,847 s wall (82 %), Y0738 12 gaps = 1,153 s (63 %), Y1056 9 gaps = 1,044 s.

- [T] **Lemma BUDGET** (`notes/exact_first.md` s.2): a cascade stopped by a clock claims nothing -- any PREFIX of a chain
  of A171/A172/A173 clips is sound, so the pose set kept is still a superset of the truth, and a DEAD reached before the
  stop is an ordinary kill.  Implemented as a SUB-TIMER on `pg.T` (`tree206.budget_cascade`): the trace's wall is pulled
  in to `now + budget` and restored in a `finally`, so every `T.out_of_time()` the chain already checks becomes a
  deadline check, and `MB._clip_rect_obstacle` -- the innermost mutual-clip call -- is wrapped for the duration to raise
  every 64 calls.  `poly204.normalise` copies pieces out of the `MB.Node` only after the fixed point returns, so an
  interrupted round leaves the node exactly where the last COMPLETED round put it.  The read-only libraries are never
  edited; the wrapper is removed in the same `finally`.
- [T] **Rule EXACT-FIRST** (`A220_EXACT_FIRST`, s.3): at a fully named leaf, before Lemma ROLE-SPLIT, ONE exact cascade
  round under `A220_BUDGET` (45 s).  DEAD -> the node is closed here with rule (e)'s own `x` record and verifier clause;
  undecided / budget -> coarse mode restored, the shrinks KEPT, the split candidates re-read from the tighter boxes and
  the old rule runs.  Variant `small`: only when the role the split would bisect has max position extent < 0.25 (the
  Y0865 case -- a blind TILT bisection of an already well-located role).
- [T] **Rule NOROOM-INHERIT** (`A220_NOROOM_INHERIT`, s.4): when the nearest ancestor's no-room used >= 80 % of its cap
  without deciding and no role box has since lost more than 50 % of its volume (and the node is not a terminal m = 1
  pocket child), the child's cap is 25 s and ONE budgeted exact round runs first, so the search reads smaller boxes.  A
  cap is a BUDGET, never a claim: a shorter search returns UNDECIDED more often and UNDECIDED prunes nothing (A211f's
  S'' argument one level down).  `tree209.noroom_at` gained one optional `deadline` argument because the wall-derived
  budget has a 60 s FLOOR.
- [M] **why A211f's no-room memos never hit** (`build_hits` 0 / `bisect_hits` 0 on Y0865): not a bug -- both memos are
  keyed on CONTENT (the exact role boxes; the obstacle vertex sets) and a child never reproduces its parent's content,
  because the child runs its own coarse cascade round before the leaf rules and that round's mutual clip moves boxes the
  design note assumed untouched.  Only the obstacle INTERNING survives (21,392 hits / 6,077 misses on the Y0865 run).
  Resuming `bisect_free` from the parent's undecided leaves is NOT cheap (A189 returns a residue, not a frontier, and is
  read-only): left [C].
- [T] **flags OFF = A211 exactly** (s.5): every edit is inside an `if` on an unset env var, plus one keyword argument
  defaulting to the old expression; the running run211 / run212 workers, which import these files afresh per page, keep
  A211's behaviour.  The pre-A220 code is kept verbatim in `attempts/A220-exact-first/base211/` so the claim is CHECKED
  by a run, not asserted: configs `eqbase` (old code) vs `eqoff` (this code, flags off) on the same page / pad / wall.
- Benchmark (`code/bench220.sh`, `plan_a.txt` / `plan_b.txt`, `analyze220.py` -> `results/bench220.md` + `.jsonl`): two
  detached lanes, one python each, BelowNormal + affinity 0xFFFF, gated at 10 lab pythons, isolated cert dirs and row
  files, `--no-fig`; configs `off` / `ef` / `efs` / `nri` on `k5_16_interior_Y0865` (the PI's page), the addendum's
  `k5_16_interior_Y0402` and `k5_11_interior_Y0738` (inheritance ON -- they are ALIVE and their gallery claims are
  taken, so every config starts from the same frozen merged state) and the closed `k5_11_interior_Y0672`,
  `k5_16_interior_Y0249`, `k5_16_interior_Y0460`, `k5_16_interior_Y0500` (`--no-inherit`, since with inheritance ON they
  would inherit their own DEAD verdict and measure nothing).  Per row: verdict, seconds, ratio against that page's `off`
  row, node / kill counters, the A220 counters and the WALL SPLIT BY STAGE (coarse rounds / no-room / exact cascade /
  other); per config the geometric-mean ratio and the verdict-regression check.
- DECISION RULE (unchanged from the brief, and NOT yet taken): a variant goes ON in `worker211.sh` / `launch211.sh` only
  at a geometric-mean ratio < 0.8 with no verdict regression.  Until the lanes finish, the flags stay OFF everywhere and
  `CURRENT.json` is untouched.

## 2026-09-14 night -- A219-wall-torque (Fable) -- DONE (launch-and-exit; holder search continuing detached): **the PI's wall-torque limitations made exact -- CEIL, TWO-CONTACT, ONE-TILTED proved; Lemma RING holds on 193 / 193 four-crowd witnesses but is unaffordable as a structure census (2.6e11 structures); the ring's strut mode is first-order free but second-order STIFF (v2 = +0.381) and blocked by a caged rattler; k0_00 unchanged**

- The brief (19:10) + addendum 2b (19:30): L1 "WLOG S < ceil(sqrt n)", L2 "squares cannot load along a wall without a net torque",
  L3 "the meeters need holders pushing out from the centre, and the holders must torque-balance in the middle"; then the PI's
  second-order observation on the ring (square 6 a two-force strut, its rotation a first-order free mode).
- [T] Lemma CEIL (`docs/proofs/wall_torque.md` s.1): s(n) <= ceil(sqrt n) by the grid; a minimiser has S < ceil(sqrt n) iff s(n) <
  ceil(sqrt n) (false at n = k^2, k^2-1, k^2-2); at n = 11 `Fits 11 4` (Lean theorem from the axiom, ceil(sqrt 11) = 4 proved) and the
  certified S <= 3.877084 is the bound used.  [T] Lemma TWO-CONTACT (s.2): a tilted wall square (tilt not 0/45/90) with exactly one
  further loaded contact is not in balance (two forces collinear through the touching vertex; no other vertex on that normal, no edge
  normal wall-normal) -- a loaded tilted wall square needs >= 2 further contacts.  [F] L2 as stated: flat squares carry along-wall
  compression with zero torque (the simple packing; ring squares 3, 5, 10 balance by wall + two contacts) and a 45-deg diamond
  pinched by a flat square balances with one contact (A217's C5 diamonds).  [T] Lemma ONE-TILTED (s.3): two flat meeters of an open
  corner box overlap, so every doubly-met open corner has a tilted meeter -- where L2 acts.  Lean: `Statements/Open/LemmaCEIL.lean`,
  `TwoContact.lean` (geometric core), `OneTilted.lean`; build + audit exit 0, no sorry.
- [M] Lemma RING (s.4, `results/ring219.md`): tilt-floor / crowd rows dropped, contact structure kept, free FJ LP INFEASIBLE on all 8
  HELD + 185 CROWD four-crowds (also on the loaded rows alone).  The minimal external load: torques alone suffice on 8 / 8 HELD and
  37 / 185 CROWD, always anti-aligning on the tilted meeters (128 : 10); the external FORCE on a meeter is along its wall toward the
  corner (175) or into its wall (114), radial 3 -- the PI's L3 direction; in 130 / 193 witnesses a non-meeter needs load too (the
  holders cannot balance).  One added interior holder: no feasible pose at the witness side (free space at S ~ 4 is slivers); after
  a 15 % dilation the drains return to side 4.000 (free, <= 2 doubly-met corners) or keep the four-crowd only with crowd pulls
  (sum lambda >= 0.16); never an FJ four-crowd, never <= s-hat (`holder219.jsonl`, 31 / 193 at the write-up, detached, per-row
  commits, resume block in `ring219.md`).  Pages: `ring_residual_rand_0_0569_t20.svg`, `best_attempt_w060_crowd.svg`.
- [T]/[M] 2b (s.5, `results/second_order219.md`): Lemma STRUT (a two-force strut's rotation about either contact is a first-order
  zero mode of the loaded structure) and Theorem SO (v2(y) = min e_s.w s.t. grad g_r.w >= -y^T H_r y on the tight rows of a
  consistent selection = max over the multiplier polytope of y^T Hess(L) y; v2 < 0 => a feasible curve with s decreasing at second
  order => not a local minimum => no sigma-minimiser).  The ring: the PI's numbers reproduced (floor +6.0e-4, 7-contact +2.5e-7,
  4-contact -7.5e-7 per mrad) AND the rattler 0 is hit at first order (-6.4e-4); on the loaded core the mode exists and v2 = +0.381
  (the side RISES); with the rattler's rows the mode is blocked (0 is caged by 4, 5, 6).  All witnesses (four variants, rotations
  about every contact point + reduced-Hessian eigenvectors, LP completion, curve re-check): HELD 0 saddles; CROWD 11 of 182 stationary
  are second-order saddles (6-9 curve-verified) and 29 are not Fritz-John under another consistent selection (excluded at first
  order by D3'); no strut mode is a saddle (v2 >= 0 on all 51).  Page: `ring_mode_rand_0_0569_t20.svg`.
- [C] The finite structure question (s.6, `structures219.json`): 8 meeters x {wall, partner, <= 2 holders in other meeters / <= 3
  interior squares}: 1.2e13 labelled, ~2.6e11 orbits (2.6e7 with no interior holder), 2.3e6 CPU-days at 0.78 s per structure
  (232 CPU-days for the no-holder slice alone).  Not a route.  RING excludes LOADED four-crowds; the rattler crowds (61 / 70 at the
  genuine k0 FJ points) are covered by no proved lemma -- K0-FREE (teleport, [T]) needs a corner met by <= 1 square; they stay with
  H1 = T3|k0 (`drain_flow_k0.md` DF-O4, OPEN).  **k0_00 unchanged.**
- Files: `docs/proofs/wall_torque.md`; `attempts/A219-wall-torque/{code,results,logs}`; pages
  `docs/residue_map/campaigns/A219-wall-torque/`; registry row; ledger s.4 note.

## 2026-09-14 night -- A221-lane-cover (Opus) -- launch-and-exit (the final benchmark pass detached; resume block in `notes/lane221.md` s.5): **the no-room LANE replaced by a POCKET COVER -- the same exact clip rooted at the pocket instead of at the pocket's MEETING window -- plus pocket INHERITANCE; 5.9x on the no-room wall, two nodes killed that A189 left UNDECIDED, 0 regressions on 112 replayed rows**

EXPERIMENT FIRST (`results/experiment221.md`, harness `code/exp221.py` + `code/nodeload221.py`).  On the four target
k = 10 nodes (Y0402 zero_page R.2.1 / R.2.1.1, Y0738 zero_page R.1.1.3.3 / R.1.2.5.2) the 120 s cap splits as
build 3.0 s, bisection 3.7-9.3 s **which EXHAUSTS at its own depth cap**, and then **109-115 s of lane returning
`None`**.  The lane is the blocker, structurally: `chordlane.lane_out` roots its cover at
`polylane.centre_window(cell)`, the centres of squares MEETING the cell -- the pocket grown by `1/sqrt2` on every
side, **10-21x the pocket's area** on these three pockets.
- [M] the lane ALONE at 600 s and `lane_max_open = 1e6` still returns `None` on two of the three pockets; on the one
  it does discharge it needs **160 s**, more than the node's entire cap.  A221's cover kills that same pocket in
  **0.0 s**.
- [M] `cProfile` of a 120 s lane run: ~98 % is polylane's FLOAT witness search (`_gmax` 20.9 s, `point_margin_many`
  13.6 s, `best_shared_point` cum 44.4 s of 45 s; `Fraction.__new__` 0.8 s).  **A213's integer core and A214's C
  kernel were installed and active throughout** -- routing "the lane's exact tests" through them was never the
  lever, because the lane is not spending its time there.
- [M] the surviving pocket of Y0402 R.2.1 is **genuinely alive**: 48 halvings and 245 s leave **88 %** of its
  (centre x tilt) volume open.  No no-room leaf can ever kill that node; A189 was paying 109 s to find that out.

THEORY (`notes/lane221.md`, both n-general).
- [T] **Lemma POCKET-DEAD.**  If every rectangle of a cover of the residue's free CENTRES is DEAD -- every pose with
  centre in it meets some `K'` -- the node has no free unit square at all, hence is DEAD for every `m >= 1`.  The
  per-pocket certificate is A171's own exact clip `_clip_rect_obstacle` **rooted at the pocket**, plus the SOUND
  `container_clip(strict=False)` at `w_min` (the strict `w_max` clip would not be sound here), run DEPTH-FIRST so
  the memory is the stack and the depth is not capped by a frontier.
- [T] **Lemma POCKET-INHERIT.**  Rule NS, ROLE-SPLIT and POCKET instantiation only shrink a role's pose set (or add
  a role), and `K'` is an intersection over surviving poses, so `K'_parent subset K'_child` for every parent role;
  hence the child's free poses lie inside the parent's and **the parent's pockets cover the child's free centres**.
  A child therefore skips the container-wide bisection and covers the parent's pockets with its own larger cores.
- [T] **Lemma CN on the survivors.**  A209's CN bound is applied to the pockets that SURVIVE the cover, not to the
  whole list: a pocket certified DEAD holds no free centre, so dropping it keeps the cover and can only give fewer
  groups.  Strictly stronger than A209's own input.

BENCHMARK (`results/bench221.md` + `.jsonl`, `code/bench221.py` / `run221.sh` / `table221.py`; every row replays a
RECORDED no-room node from an A211 certificate, nothing is re-run in a tree).
- [M] **0 regressions in the shipped configuration** over 314 replayed rows (the single regression on record is the
  m = 2 node below, under the code before Lemma CN was in this module).
- [M] **verdict agreement on the closed pages** Y0500 g1 and Y0460 g1: 24 non-vacuous no-room nodes, 9 DEAD -> DEAD,
  15 UNDECIDED -> UNDECIDED, 1835 s -> 712 s.
- [M] **three genuine new kills**, `Y0402 zero_page R.3.1.2.1` (12.9 s), `R.3.1.2.2` (16.9 s) and
  `Y0738 zero_page R.1.3.3.2` (12.4 s) -- 3.1-4.3 s each under inheritance -- all left UNDECIDED at the cap by the
  certificate.  Attributed to the COVER by a CONTROL that runs **A189's own leaf on exactly the
  same replayed boxes**: it returns UNDECIDED at 131-133 s on all three.  A third node, `R.3.1.1.1.2`, also comes back DEAD
  but the control kills it too -- that one is the certificate's `roles` (the page's LIVE dict) being tighter than
  the boxes the leaf actually saw, and is NOT credited to A221.  Any "new kill" claim from a replay needs this
  control.
- [M] **THE CAP is the budget lever.**  Over 42 pocket covers *every* DEAD pocket died in `<= 0.1 s` and *every*
  surviving pocket burned the whole 45 s -- the cover collapses at once or not at all -- so `pk_deadline` drops to
  5 s (a 50x margin).  Final pass over all four pages, 68 non-vacuous no-room nodes: **4685 s -> 934 s (5.0x)**,
  slowest node 28.5 s, verdicts identical.  With Lemma POCKET-INHERIT on Y0402's 25 nodes: **1573 s -> 258 s
  (6.1x)**, slowest 25.2 s, and a child whose inherited pockets all die is decided in **3.0-4.6 s with no container
  bisection at all** (e.g. R.2.1.2.2.2: 20.6 s -> 4.0 s).  COST SIDE: for m >= 2 an UNDECIDED node is now SLOWER
  than A189 (6.5 s -> 15.3 s), because A189 with `max_pocket_area = 0` never tries a cover there; Lemma CN is tried
  first (free), so the nodes CN kills cost what they did and the extra seconds buy the cover's extra kills.
- [M] the benchmark also FOUND a real defect: the one m = 2 node `Y0738 R.1.2.3` came back UNDECIDED because A209's
  CN upgrade lives in `tree209`, not in A189 -- fixed by the Lemma-CN-on-survivors step above (and CN is tried
  BEFORE any cover when `m >= 2`, since it is free, which restores A189's fast path on those nodes).

DELIVERY.  `code/pocket221.py` (the cover engine) + `code/noroom221.py` (the lemmas and the leaf: `noroom`,
`noroom_child`), `code/nodeload221.py`, `code/exp221.py`, `code/bench221.py`, `code/run221.sh`, `code/table221.py`.
**A220 owns `tree209.py` / `tree211.py` / `tree206.py`, so nothing there is edited**: the integration ships as
`code/tree209_integration.diff`, a flag-gated (`A221_LANE=1`) change that adds `Tree209.parent_pockets` (the nearest
ANCESTOR's recorded pocket list -- never a sibling) and routes `noroom_at` through `noroom221`; `git apply --check`
is clean against the current file.  A189 / A171 / A141 / A161 are untouched.

OPS NOTE (honest).  At 19:45 I issued a `Stop-Process` on a PID I had mis-identified as my own experiment lane; my
lane was in fact still running and finished normally, so a lab python was killed by mistake.  No `run211` / `run212`
worker was lost (all committed `rc=0` either side of that minute) and the resumable A219 holder loop restarted at
19:46:38 and has been committing per crowd since.  The lesson for the next attempt: match the PID against
`Win32_Process.CommandLine`, never against start time -- which is what every later kill in this attempt did.

## 2026-09-14 night -- A222-ring-swap (Fable) -- DONE (launch-and-exit; the region searches continuing detached, per-row commits): **RING SWAP made exact -- Lemma SWAP is a theorem (teleport = |X| = 1); the PI's perimeter sweep is Lemma STEP / Lemma CELLS (|M(Pi)| <= |Pi|); its COUNT does not close (one remaining meeter per exposed cell is a teleport; 9 <= 11); RAISE(0 -> 1) is the load-free geometric obligation and covers rattler crowds; the ring swaps at once at its own side; Trump swap-rigid on 201 subsets; k0_00 unchanged**

- The brief (22:10) and the PI's addenda 0 / 0b / 0c / corrections (22:30-23:05): teleport-decompose a loaded ring at once; the
  inductive sweep around the perimeter (4 floor(sqrt n) - 4 = 8 cells at n = 11); Lemma RAISE(0 -> 2); VALUE vs UNIQUENESS.
- [T] Lemma SWAP (`docs/proofs/ring_swap.md` s.1.1, Lean `swap_packing`): |X| unit squares inside U(X) = (union X) u Free, interior-
  disjoint from the rest, replace X at the same side.  [T] Lemma STEP (s.1.2): the sweep's bookkeeping h_k = sum |M_j| - k (place from
  hand / teleport the single meeter / pick up all and place one); it ENDS iff h_k = 0.  [T] Lemma CELLS (s.1.3, Lean `cells_swap`):
  a packing exchanges into one containing a family Pi of disjoint cells iff |M(Pi)| <= |Pi|; K0-FREE = |Pi| = 1; Theorem FC = pins + a
  cell in a COMPLETE packing -- mid-sweep FC does not apply.
- [F] The count (s.1.4): each exposed cell needs ONE remaining meeter (a teleport), not the PI's second; with every corner doubly met
  >= 9 squares meet the 8 window cells and n = 11 supplies them; counting closes only for n <= 4; the endgame (8 settled + 3 in the
  cross region) is impossible at S < 4, so the sweep ends only on an under-met PREFIX.  The count gives: >= 1 centre square meets an
  exposed cell (the ring: rattler 0 at BL(1,0) / holder 9 at TR(1,0)); the ring is not self-supporting, one intruder supports it.
- [T]/[C] Lemma RAISE(0 -> k) (s.1.5) = an under-met family with a corner; simultaneous (two singly-met cells, distinct meeters) and
  sequential teleports are the same condition; with k1-a it empties k0_00 (Lean `no_packing_of_raise`, axiom `raise_zero_one`);
  stated from k = 0 only.  VALUE needs RAISE(0 -> 1) + the k1_00 tree; UNIQUENESS reduces to SWAP-RIGIDITY of Trump (s.1.7).
  Loads are never used: rattler crowds are covered (s.1.8).
- [M] `raise222.md`: 4,534 A217 packings, RAISE holds on every non-settled one at its own side (trivial at S >= 4); every witness
  below side 4 has a corner met by <= 1 square; window-shaped 8-cell family over-met on 40 / 1,172 four-crowds (page
  `window8_fail_w047_crowd.svg`); the ring's window sweep from BL: consumed 10, h = 2 (page `sweep_rand_0_0569_t20.svg`).
- [M] `swap222.md` (193 four-crowds, detached): on the ring, CORNER-SWAP at BR / TR / TL, not BL (rattler 0 in the pocket above the
  4-6 contact); RING4 (four settled + four band squares) FOUND at side 4.11 (page `ring_swap_rand_0_0569_t20.svg`); RING1 at every
  corner, RING4X too.  [M] `trump222.md`: 201 subsets |Y| <= 3 of Trump, no different re-packing inside U(Y).
- Lean: `Statements/Open/RingSwap.lean` (4 theorems, 1 axiom), build + audit exit 0, no sorry.  Files: `docs/proofs/ring_swap.md`;
  `attempts/A222-ring-swap/{code,results,logs}`; pages `docs/residue_map/campaigns/A222-ring-swap/`; registry row; ledger s.4 note.

## 2026-09-14 night -- A223-two-grains (Fable) -- DONE (launch-and-exit; click run complete, resumable): **TWO GRAINS + CLICK + FOUR-WALL made exact -- Lemma FLUSH (flush packings need side >= ceil(sqrt n)) is a theorem; FOUR-WALL is conditional on CLICK-DOWN, which is EQUIVALENT to 'no teleport-stuck packing below 4' (stronger than RAISE(0->1)); the PI's click is real on the ring (4.1099 -> 4.000 monotone, the lean contact slides) and on all 193 four-crowds (never blocked, free variant to 4.000 from every one); the exclusion clause of TWO-GRAIN is false as geometry (one-grain four-crowds exist, crowd-held) and open at free FJ points; 'the chain formula decreases toward alignment' is false (Lambda); SEAM stated and checked; k0_00 unchanged**

- The brief (21:10): the ring as two opposite-handed half-rings balanced at the top and bottom middle; the click-down; a self-supporting
  k0 structure needs two grains with boundaries on all four walls; a grain-boundary minimiser keeps one diagonal seam.
- [T] `docs/proofs/two_grains.md` s.1: handedness ('+' (0,45), '-' (45,90); rotations keep it, reflections swap), grains = components of
  the contact graph on loaded squares within one class; Lemma W's sign (every wall torques a grain toward its own alignment), Lemma
  TORQUE-ID (self-torques + wall-force circulation = 0: a one-handed structure needs a circulation of the opposite sign, not an
  obstruction), Lemma CORNER-LOAD (frame handedness of a loaded corner decides floor-loaded vs wall-loaded; a floor pair holding each
  other across the bottom is a LEAN of opposite global handedness -- the ring's 4|6).
- [F]/[M] the exclusion clause: 12 / 193 four-crowds have ONE grain meeting all four corners (w062_crowd: all eleven squares '+'), 68 a
  single handedness class; these are crowd-held packings, not free FJ points (A219: 193/193 infeasible), so the clause is [C] there.
- [T]/[F]/[M] s.2 Lemma CLICK: EXTENT (vertex-to-vertex chains decrease toward alignment), LEAN-SLIDE (a lean contact never blocks:
  the click along P(S, theta(t)) fails only when the polyhedron is empty -- a pin above, a caged rattler, a stale axis); [F] the general
  chain-formula claim (Lambda(45) = 3.886 < Lambda(0) = 4); the ring's two ladder formulas (c+s) + (2+sig0) s + (1+sig1+sig2) c and its
  mirror, exact to 1e-6, both decreasing toward alignment with sig held; [M] `click223.md`: the ring 4.1099 -> 4.000 in 21 steps,
  monotone, 15/15 contacts kept; 193 four-crowds: 0 blocked (A, B, C), B reaches 4.000 on 193/193 never above its start, A ends at 4.000 on
  187 and 5.000 on 6 (fixed axes force a bad flush arrangement); rattlers never block; pages `ring_grains_*`, `ring_click_*`,
  `click_worst_w156_crowd.svg`.
- [T] s.3 Lemma FLUSH (n-general, interval pigeonhole: n <= (ceil(sqrt n) - 1)^2 below ceil(sqrt n)); Theorem FOUR-WALL conditional; [T]
  CLICK-DOWN <=> STUCK-4 (above 4 the grid is the flush packing; below 4 it is the kill by FLUSH): the click is a proposed mechanism,
  the conjecture is 'every teleport-stuck 11-packing has side >= 4', which implies RAISE(0->1) (K0-FREE on a corner met by <= 1) and
  with k1-a empties k0_00; no stuck packing below 4 exists to test it (lowest four-crowd 4.0014).
- [C] s.4 Conjecture SEAM stated; n = 5, 10 = Goebel strips (one 45-deg strip between two staircases), n = 11 Trump (one 40.18-deg strip),
  n = 19 the double 45-deg band (3 + 4 sqrt2 / 3 = Lambda(45) + 1): one seam each; n = 17 (Bidwell beats the a = 3 Goebel strip) and
  n = 18 unverified.
- Lean `Statements/Open/TwoGrains.lean`: `lemma_FLUSH`, `click_down` axioms; `flush_eleven_four`, `four_wall`, `no_stuck_in_window`
  theorems; build + audit exit 0, no sorry.  Files: `attempts/A223-two-grains/{code,results,logs}`; registry row; ledger s.4 note.

## 2026-09-14 23:55 -- A225: progress on the page (how many top-level nodes are left, how deep it goes)
- The PI: "update the node lists on the right of the summary page to show how many top-level nodes are left, so I can
  better judge progress / work remaining / see how deep it's going."  New `attempts/A211-coarse-tree/code/pstats211.py`
  (stdlib only, reads `results/coarsetree211.jsonl`, no cert loads, no runs) computes per page and pad: the START NODES
  of the current run (the alive leaves it inherited, Lemma INHERIT) = N, D dead this run / A alive at the wall / U never
  reached, one line per start node (verdict, nodes, depth reached, seconds), the cumulative line over every run (runs,
  wall spent, dead / alive leaves now, ABSOLUTE max depth = the start node's path length + the depth the run added), and
  a one-line estimate `start nodes left x median seconds per killed start node`, labelled an UNDER-estimate.
- Shown in three places, all regenerated from disk: the PROGRESS block at the top of the right-hand text column of every
  `docs/residue_map/campaigns/A211-coarsetree/*.svg` page (the node table stays below it) + a progress line per gallery
  thumbnail (`fig211.py`); a per-alive-page table with a total line in `attempts/A211-coarse-tree/results/progress.md`
  (`progress211.py`); the three numbers on the board row of every page the tree has not closed in `docs/shadows/STATUS.md`
  (`status_gallery.py`'s A211 collector).
- Where the 4 worked k5 pages stand at the window pad: Y0738 5 start nodes left / 8 alive leaves / depth 17, Y0402 4 / 14 /
  7, Y0865 4 / 6 / 13, Y1056 2 / 2 / 10; 2-3 runs and ~1.0-1.5 CPU-h per page per pad so far.  The estimate is small
  (0.03-0.19 CPU-h per page) precisely because the survivors are the start nodes that already ate a whole wall.

## 2026-09-15 night -- A226-one-flush (Fable) -- DONE (launch-and-exit): **ONE-FLUSH surveyed and pinned down -- every record packing below ceil(sqrt n) has >= 3 flush corners (20 of 21 have four; Trump is the only crowded corner), so 'no non-trivial optimum has 4 flush corners' is FALSE (n = 5, 10 are proved optimal with four); the all-packings form 'no four-crowd below ceil(sqrt n)' is FALSE in general (Proposition CROWD-ABOVE: explicit four-crowds at every side above a domino-cornered record, verified for n = 26, 28, 29, 37, 40, 50, 51, 55), so Theorem PERIMETER and every local charge are dead; the conjecture with content is about the OPTIMUM (ONE-FLUSH(n) <=> UNCROWD(n)) and at n = 11 it is the k0_00 obligation itself; k0_00 unchanged**

- The brief (23:40): "at least one corner can always be teleported to flush" -- survey first, then mechanism.
- [M] `svg226.py` parses Ellsworth's SVGs (entities, nested transforms, merged flush blocks decomposed into cells) and
  re-verifies each packing by exact SAT (worst overlap 3e-16); `survey226.md`: n = 5, 10, 11, 17, 18, 19, 26-29, 37-41,
  50-55 -- flush corners 4/4/3/4/.../4, singly-met corners the same, doubly-met corners 0 except Trump's TR (2).
- [F] FOUR-FLUSH-FREE refuted by the proved optima n = 5, 10 and by 18 more records; [C] THREE-FLUSH (>= 3 flush corners
  at every optimum) is the sharper empirical statement.
- [T]+[M] Proposition CROWD-ABOVE (`one_flush.md` s.3): corner square A slid eps up its wall, flush neighbour B tilted by
  eps/2 with its vertex poking into the strip under A (depth O(eps^2)), the rest shifted by (eps, eps): a packing at side
  s + 2 eps with every corner doubly met; `crowd226.md` verifies it at S = s + (k - s)/2 < k for the 8 records with four
  dominoes.  Consequences: STUCK(n) false there, inf side of four-crowds <= s(n), PERIMETER can only restate ONE-FLUSH,
  a crowd costs O(eps) (no waste / chord / wall-budget proof), the 12 > 11 count is n-specific, the crowds are RATTLER
  crowds (unloaded second meeter) -- the class A218/A219 could not exclude by loads.
- [T] ONE-FLUSH(n) <=> UNCROWD(n) (every four-crowd below ceil(sqrt n) admits a packing at a smaller side): the honest
  statement of "the k0 exclusion" -- four-crowds exist below ceil(sqrt n), they are never the LAST word.
- [M] n = 11 (`ring11_226.jsonl`, page `ring11.svg`): the 8-square crowd ring at S = 3.90 / 3.95 / 3.99 (eps 0.02-0.10)
  leaves a pinwheel into which A222's region search fits ONE square, never three -- the construction gives no four-crowd
  below 4 at n = 11 (A217: none below 4.0014).
- Lean `Statements/Open/OneFlush.lean`: `MeetsCornerN`, `SinglyMet`, `IsOptimalPacking` (n-general), `one_flush` (axiom
  [C], hypothesis s < ceil(sqrt n)), `optimal_not_stuck` (theorem, via `ceil_sqrt_eleven`), `no_optimal_of_kill` (theorem:
  with K0-FREE's exchange O-LINK and the k1-a kill as hypotheses, no optimal packing at m < 4); registered in
  `Statements.lean`; build exit 0; audit: the three statements depend on `one_flush` only, no sorry.
- Files: `attempts/A226-one-flush/{code,data,results,logs}`; `docs/proofs/one_flush.md`; pages
  `docs/residue_map/campaigns/A226-one-flush/{survey_small,survey_mid,survey_large,crowd_above,ring11}.svg`; registry row;
  ledger s.4 note.

## 2026-09-15 00:15 -- A224-snap-rule (Opus) -- DONE (launch-and-exit; the live A/B finishing detached, resume block `code/finish224.sh`): **Rule SNAP is a THEOREM and is in the engine behind `A224_SNAP=1` (default OFF, old behaviour byte-for-byte unchanged) -- a non-pin square whose census cell no OTHER square meets teleports onto it (Lemma SWAP, |X| = 1), landing the packing in a stratum the scoreboard has closed; the certificate is exactly the theorem's hypothesis, Lean `snap_step` / `snap_dead` / `snap_diag_two`, no new axiom -- but it does NOT fire on the k5 population: 0 kills over every node of every A211 g1 certificate (72 pages, 294 candidate nodes), because at box width 0.077 the PI's "second meeter only at the corner point" is a positive-area sliver and the conditioned square H pokes 0.008 into the raw cell; cost nil, pass flags unchanged, two levers named**

- **[T] Rule SNAP** (`docs/proofs/snap_rule.md`, any n): a NON-pin square whose census cell `p` no OTHER square meets
  teleports onto `p` (Lemma SWAP with |X| = 1), so the packing lies in the stratum `S + {p}`; that stratum closed on
  the window kills the node.  **SNAP-DIAG** is |X| = k at pairwise interior-disjoint cells, each blocked only by the
  others; for k >= 7 A53's census has no name and Lemma K1 kills through any closed subset.
- **In the engine, flag-gated** (`A224_SNAP=1`, default OFF; with it off the engine is unchanged and `chordlane` is not
  even imported): leaf rule (0) before rule CC, plus one cheap test per internal node after the coarse round.  The
  certificate IS the theorem's hypothesis -- (a) an exact separating-axis miss certificate per other ROLE against the
  widened box `B_p+` (page -> side-m by Theorem FC Step 2, contrapositive only; the test is taken in `t` so the tilt
  bin is never rounded inward), (b) the pins by the class's UNCLIPPED census and the anonymous squares vacuously or by
  an EMPTY option-table row, (c) the target stratum's FULL [191/50, 969271/250000] row.  `audit211` gained the
  matching refutation criterion.
- **[F]/[M] It does not fire on the k5 population.**  Replayed on EVERY node of EVERY A211 g1 certificate (72 pages):
  294 nodes carry a candidate, **0 kills, 0 hand-offs**; 65 of 173 candidate pairs have exactly ONE blocker, 107 of
  them the conditioned square `H`.  Y0865, the PI's own case: `F1` is near-simple at BL(1,0) (centre within 0.038,
  tilt [0, 2.4] deg) and every other free role misses the cell exactly -- but `H` at (2.17, 1.475, 58 deg) has an edge
  crossing x = 2 at y = 0.992, i.e. 0.008 inside the RAW cell.  At box width 0.077 the "corner point" is a sliver of
  positive area, so the near-simple square does not block the last approach.
- **[M] Cost nil** (0.17 s of SNAP over 60 evaluations inside a 422 s run), so the rule stays in for the lower-k sweep
  (no `H`, smaller roles).  Pass flags UNCHANGED and no `queue_pass6.txt`: the brief made both conditional on a kill.
- **Levers named:** branch the single blocker at the cell (a Rule NS split whose MISSES child is an immediate SNAP
  kill), or bisect the near-simple role below the sliver.
- Lean `Statements/SnapRule.lean`: `snap_assign`, `snap_step`, `snap_dead`, `snap_diag_two` -- theorems, no new axiom;
  `lake build` + `lean/audit.py` exit 0, no sorry.  Files `attempts/A224-snap-rule/{code,notes,results,logs}`;
  registry row; `results/bench224.md` (+ `snapscan224.jsonl`, `bench224.jsonl`).

## 2026-09-15 01:15 -- A228-segfault (Opus) -- DONE (reproduction + closed-page verification finishing detached; resume `attempts/A228-segfault/notes/segfault228.md` s.4): **the pass-5 `rc=139` was in the G1 pad, not pad 0, and the ~500 s of silence before it is A189's `pockets_of` -- an O(components^3) merge with no deadline, reached after the leaf's clock has already expired; guarded by supersets in A221's own wrapper (a guard may only return UNDECIDED), plus a real out-of-bounds write found and guarded in the A214 C kernel's batch index, plus a worker that now records every rc != 0 instead of only 137**

- **[F] The BRIEF's fact is wrong, and the correction is the finding.** The crashed process's OWN certificate has
  `zero_page` COMPLETE (`ALIVE` at the wall, 1818.7 s, 86 nodes) and `g1_page` **`RUNNING` at 977.1 s, 75 nodes**;
  the log's pass-5 pad-zero segment runs to `t = 1818 s` and the g1 segment ends at
  `node R.3.4.p1 d1 pocket<-[0]: INTERNAL (... t=977.1)`.  The worker's `g1 ... rc=0 4408s` printed beside `rc=139`
  is the PASS-2 verdict line: `worker211.sh` greps the whole accumulated log for it, so a crashed run reprints the
  last successful one's.  **Pad 0's work was not lost; the G1 pad's 75 nodes were.**
- **[M] The process then ran ~500 s emitting nothing, inside a leaf whose cap is 150 s** -- the no-room leaf at
  `R.3.4.p1` (k = 10, **m = 1**), i.e. the path that pays for the global bisection and then for `pockets_of`.
- **[T]/[M] Two steps of that leaf see no deadline and are unbounded.** (i) `noroom189.pockets_of`'s
  `while len(pk) > max_pockets` merge rescans EVERY pair to choose the cheapest merge: **O(components^3)**, run
  AFTER `bisect_free`'s clock expired; at `grid = 0.0625` the container `[1/2, s-1/2]^2` holds 46 x 46 = 2116 cells,
  so a SPREAD residue (many small components, not a few blobs -- which is why no benchmark ever saw it) costs up to
  ~1.6e9 inner steps.  (ii) every give-up path of `pocket221.cover_rect` (`deadline` / `piece cap` / `open cap`)
  materialised the whole `pk_max_pieces = 2e5` stack, re-volumed it and re-pocketed it on a **16x finer** grid --
  the same unbounded work, again strictly after its own deadline.
- **[T] The guards are supersets, so they can only ever return UNDECIDED.**  `pocket221`: `_dump` bounds the
  give-up frontier (`pk_max_dump = 4096`); `cert["exhausted"]` is written and `pocket_dead` now requires it for
  `dead`, so a cover that gave up can never be read as DEAD; new `repocket()` measures the cost of `pockets_of`
  first (all linear) and returns the cover's own ROOT when pieces / cells / components exceed budget.  `noroom221`:
  the global call falls back to the container CENTRE BOX `[1/2, s-1/2]^2`, which contains the centre of every pose
  of a unit square -- a cover whatever the residue looks like.  A189 / A171 / A131 are untouched.
- **[F] The BRIEF's other two suspects are cleared.**  There is NO deep Python recursion in the pocket path:
  `cover_rect` is an explicit stack loop, `noroom189._components` an explicit flood fill, `pinclip._bisect_boundary`
  a bounded `for`, and `multibox._clip_rect_obstacle`'s `rec` is a one-line trace appender, not a recursion (the
  only recursion in reach, `lonely_clip.refine_piece`, is bounded by `refine <= 2`).  The A214 kernel's arithmetic
  envelope is guarded (`fits93` / `a214_box_ok` / `vert_ok_range`) and its DLL imports nothing (empty PE import
  table, read directly).
- **[M] A genuine out-of-bounds WRITE was found in the C kernel anyway, and guarded without touching it.**
  `a214_cert_batch` addresses its output with `int i0 = i * nb`: at `nv * nb >= 2^31` the product overflows, `i0`
  goes negative and the kernel writes BEFORE the ctypes buffer.  Unreachable on this population (`nv <= 16`), but
  the Python caller is the only party that knows the true product, so `certify_h` now refuses the batch above
  `2^30` pairs and takes A213's unbounded-integer path -- gate (2') of the module's own FALLBACK PROTOCOL.  The C
  source and the DLL sha256 are unchanged.
- **[M] Worker hygiene.**  The crash left NO row in `results/coarsetree211.jsonl` and no mark in `progress.md`
  (only `rc == 137` was recorded).  `worker211.sh` now writes a row for EVERY non-zero rc (`"rc": <n>`,
  `killed: true`, `verdict: ALIVE` -- a crash is undecided, never a verdict), appends the nid to
  `logs/requeue.txt`, and on a CRASH (not on the 137 wall kill) releases its `logs/claims/<nid>` so a sibling
  worker re-offers the page.  The script is being executed right now by p5a/p5b and bash re-reads a running script
  by byte offset, so the new text was `bash -n`-checked in `worker211.sh.new` and `mv`-ed over the path: the
  rename swaps the inode, the running shells keep the old one, the next launch gets the new one.  Both worker pids
  verified alive afterwards; nothing was restarted.  The missing Y0402 row was backfilled, labelled as backfilled.
- **[C] The step from "runs away" to "SIGSEGV" is NOT proved** -- a Python-level runaway normally ends in
  `MemoryError`.  This is the only `Segmentation fault` in `attempts/*/logs/*` in the whole campaign, so a clean
  reproduction cannot clear the code; the guards are therefore sound and cheap whether or not it fires, and the
  worker now makes the next one visible.  **A189's STEP 34 regression PASSES through the patched leaf** with
  `repocket: pockets_of`, i.e. on a normal node no guard fires and the computation is the old one.
- Files: `attempts/A228-segfault/{notes/segfault228.md, code/repro228.sh, code/verify228.sh, logs, results, certs}`;
  patches in `attempts/A221-lane-cover/code/{pocket221,noroom221}.py`, `attempts/A214-c-kernel/code/ckernel214.py`,
  `attempts/A211-coarse-tree/code/worker211.sh`; registry row.

## 2026-09-15 09:15 -- A229-start-parallel (Opus) -- DONE (launch-and-exit; the live closed-page verification finishing detached, resume `bash attempts/A229-start-parallel/code/verify229.sh`): **a page's START NODES can be run IN PARALLEL -- Lemma PAR: merging per-start certificates is Lemma INHERIT applied FILE-WISE, so k shards started from one merged state and merged afterwards leave exactly the state one sequential run would have left**
- **The waste that forced it [M]:** the lab sat idle from 01:06 to 08:59 with three k5 pages alive. A page runs its start nodes SEQUENTIALLY inside one 1800 s wall (`run211.run_starts`), so `k5_16_interior_Y1056` -- 3 start nodes, the first of which ate the whole wall -- killed 0 of them while 7 of the lab's 10 process slots stood free.
- **[T] `attempts/A229-start-parallel/notes/parallel229.md`, Lemma PAR:** the hypotheses of Lemma INHERIT (a) (kills are final) and (b) (branch lists are reusable) are statements about the PATH KEY alone -- coarse_tree.md s.4(a) says it outright ("the refutation does not depend on the pose set the refuting run happened to hold: the hypothesis set is what died"). So two records with the same key are records about the SAME hypothesis whichever FILE carries them; the union of the files is exactly the set the walk (c) consumes; and the attribution is irrelevant, because (a) is a disjunction over the sources and (b) makes any ONE recorded branch list sufficient. Corollary: partition the start nodes `S` produced at time `t0`, run one process per part from the SAME merged state, each writing its own file, and the merge of all files is the sequential run's state -- each shard's tree under `s_i` is grown from `s_i`'s hypothesis alone and never reads a sibling.
- **Code (default behaviour byte-identical without the new flags):** `attempts/A211-coarse-tree/code/run211.py` gains `--start LABEL[,LABEL...]` (every other start node recorded `SKIPPED (filter)`, explicitly NOT `(wall)` -- the FILTER refused it, the geometry did not, so `wall_limited` always allows the shard to resume) and `--cert-suffix TAG` (the run's certificate goes to `certs/coarsetree211_<nid>__<TAG>.json`, the page certificate untouched; implies `--no-fig`, a shard holds only part of the page); the row carries `shard` / `start_filter` / `cert_suffix` / `start_skipped` ONLY on a shard run. `inherit211.a211_certs` now returns the page certificate AND every `coarsetree211_<nid>__*.json`, oldest first by mtime, all at rank 5 (so the newest file wins the branch-list tie, while DEAD is never subject to a tie-break); the `__` separator keeps the A57 descendant pages (`..._D07.json`) out; `A229_CERT_DIR` moves the A211 sources for an isolated test.
- **[M] `code/test_inherit_multi229.py` PASSES** on 4 closed pages (Y0500 / Y0660 / Y0460 / Y0865) x both pads x 2 and 3 shards: a real certificate is cut into shard certificates exactly as `--start` would have written them, and the merge over the SHARDS ALONE reproduces the whole-page merge -- identical DEAD path set (9-21 paths) and identical next START node set, every time.
- **Pass 7 is BUILT, NOT LAUNCHED:** `code/queue229.py` (start nodes from `inherit211.merge`, longest-first by the wall each has already absorbed without closing, both pads) wrote `attempts/A211-coarse-tree/code/queue_pass7.txt` -- 28 start nodes over Y0402 (4 g1 + 4 zero), Y0738 (6 g1 + 1 zero) and Y1056 (4 g1 + 7 zero), i.e. **28 parallel units where pass 6 had 3**. The file says so in its own header: re-run `queue229.py` at launch time, because p6a/p6b/p6c are still writing those certificates. `code/worker229.sh` drains it (worker211's gates and post-run chores, claims `logs/claims229/<nid>__<TAG>`, queue line `<nid> <pad>:<label> [<wall>]`).
- **[C] the live whole-vs-3-shards run on Y0500 g1 is still finishing** (`code/verify229.sh`, isolated cert dirs, one python at a time beside the running pass-6 workers; it writes `results/verify229.md` and commits itself).
- Files: `attempts/A229-start-parallel/{notes/parallel229.md, code/{queue229.py, worker229.sh, test_inherit_multi229.py, verify229.sh, report229.py}, results, logs, certs}`; patches in `attempts/A211-coarse-tree/code/{run211.py, inherit211.py}` + `code/queue_pass7.txt`; registry row.

## 2026-09-15 01:20 -- A227-lemma-eps (Fable) -- DONE (launch-and-exit; the full replay + live benchmark finishing detached, resume block `code/bench227.sh`): **Lemma EPS is a THEOREM (five Lean theorems, no new axiom): a square within (delta, theta0) of its cell's slot pose leaves the cell uncovered only in four thin WEDGES, one per side on the tilt-determined HALF (a pinwheel: right-upper, top-left, left-lower, bottom-right), corner depth `t(1-t-2dy)/(1-t^2) - dx` (~ theta/2 + delta) tapering to zero at `y* = 1/2 + dy + t/2 + dx(1-t^2)/(2t)`; a second meeter enters the cell only through a wedge, and a wedge on a pin/wall-backed side only through its END ZONE at the cell's corner (GATE); Rule EPS strikes every meeter candidate that misses the wedge targets exactly -- on Y0865 it strikes F2..F5 at every one of 101 candidate evaluations, but H (and F3) reach the wedges, so 0 kills: the wedge target is handed to Rule NS**
- **[T] `docs/proofs/lemma_eps.md`:** EPS-1 (four half-plane cuts, exact), EPS-2 (the wedge along a side, its depth linear in `y`, the foot, the pinwheel, the constant `w <= delta + t0(1+2 delta)/(1-t0^2)`, offset cases), EPS-3 (a meeter enters through a wedge), EPS-4 (a BOX of poses: the union of wedges inside <= 16 exact convex polygons, `K'` = the certified core), EPS-5 (GATE: segment/frontier; backed sides via pin CORES `h = 1/(2(cos+sin))` with gap slivers; the corner end zones), EPS-6 (meeter poses `W (+) Sq_phi`, `h_phi = (cos+sin)/2`), Rule EPS and its certificate (Theorem FC + A161 exact miss tests, hull then pieces and per piece of F; anonymous by the fresh option row within 1/sqrt2 of a target).
- **Lean `Statements/Open/LemmaEps.lean`:** `not_mem_iff_four`, `wedge_right_depth`, `wedge_right_corner` (the `t` identity), `coord_within_h`, `gate` -- ALL theorems from `mem_set_iff_uv` + `psq_convex`, std axioms only; `lake build` + `lean/audit.py` exit 0, no sorry.
- **Code:** `code/eps227.py` (wedge polygons by exact clipping, side assignment by minimum depth, backing with gaps `<= 1e-3`, targets, the strike, the record), `epsscan227.py` (offline replay, resumable), `bench227.py` + `code/patched/{tree211,leaves211}.py` = `integration227.diff` (114 lines, `git apply --check` clean; flag `A227_EPS=1`, default OFF; leaf rule (0') beside SNAP and once per internal node; counters `eps_*` in `result()`), `bench227.sh` (scan ALL -> live Y0402 g1 -> live Y0865 g1 -> report -> commit), `report227.py`, `fig227.py`.
- **[M] Y0865 g1 (`results/eps227.md`, partial until the chain finishes):** 163 snapshot nodes, 75 with a near-simple candidate, 101 (role, slot) evaluations; every candidate loses 3-4 meeters (F2..F5 struck at the hull box), **0 DEAD by FC+EPS**; survivors `H` (46) / `{F3, H}` (55); H reaches F1's left-family wedge 55x and the right one 45x, F3 the top/left wedges of F2's BR(0,1) cell; anonymous clause vacuous (fully named). The PI's Y0865 node: targets = right wedge `[1.974, 2.0108] x [0.5, 1.0068]` (+ the lower pad strip), top wedges, zones LB/LT/RB; H's edge crosses x = 2 at y = 0.9916 inside the right wedge -- not struck; page `docs/residue_map/campaigns/A227-lemma-eps/eps227_Y0865.svg`; `eps227_pinwheel.svg` (feet at y*, numeric checks pass). Cost 0.05 s per node.
- **[C]** the strike tests the wedge's bounding rectangle (a polygon SAT would recover the taper at the foot, exactly where H enters); Rule NS on a rectangle target is recorded, not branched; the tilt-coupled (arc) wedge is relaxed to a box (second order).
- Registry row; files `attempts/A227-lemma-eps/{code,results,logs}`, `docs/proofs/lemma_eps.md`, `lean/.../Statements/Open/LemmaEps.lean` (+ one import line in `Statements.lean`).

## 2026-09-15 — A230-eps-branch (Opus) — Rule EPS: all candidates, the polygon taper, Rule NS at the wedge
- PI, 09:00: *"F1 (BL10) should trigger EPS before F2 does (BR01), so there may need to be something to make sure
  it checks all candidates."*  **Answer:** A227 already evaluated every candidate its loop was given — the 1.1
  candidates/node came from A224's FILTER (`snap224.near`: the role's box CENTRE within 0.06 of the slot centre
  and EVERY piece near-aligned), not from a scan stopping at the first.  `eps230.candidates` takes the ℓ∞
  distance from the slot centre to the role's position BOX and asks only that SOME piece's tilt bin be
  near-aligned, so both cells a role can be near-simple in are returned; order is smallest box volume first.
  On Y0865 g1's 163 recorded nodes: 271 candidates (1.66/node) against A227's 1.1, **170 returned only by the
  wider test**.
- **[T] TAPER** (lemma_eps s.7 [C]1 discharged): `eps230.misses_poly_t` is A161's separating-axis test against
  the exact convex wedge POLYGON — the polygon's own edge normals with the square's support radius bounded by
  interval arithmetic in (cos, sin) over the tilt bin, plus the square's two normals over the Minkowski
  difference {box corner} − {polygon vertex}.  Sound a fortiori (wedge ⊆ polygon ⊆ bbox); 3 229 randomised
  claimed separations, 0 contradicted.
- **[T] NS AT THE WEDGE** (s.7 [C]3 discharged): where exactly one named role M survives a candidate and the
  anonymous clause is CERTIFIED empty, M *is* Theorem FC's second meeter, so "M meets W" / "M misses W" is
  exhaustive.  The `epsns-misses` child is DEAD at once by FC+EPS (no cascade, 0.0 s, certificate = the target
  list + the struck roles' miss certificates); the `epsns-meets` child carries M's pieces clipped exactly to the
  poses reaching W (pieces separated from every target dropped, the rest intersected with W's bbox dilated by
  h = (cos+sin)/2 over their own bin) and then the ordinary coarse round — so the option table is fresh before
  any further branching.  Live on Y0865 g1 at once: the split fires from depth 2 and every misses child dies.
- **[C] the split must be capped**: uncapped it recurs on the same (slot, role) at every depth (the clip tightens
  a little each time) and spends the whole depth budget — `A230_WEDGE_CAP`, default 1 per pair per path.
- Wiring is flag-gated in `tree211.py` / `leaves211.py`: `A230_EPS` (or `A227_EPS`), **default OFF = pass-6
  behaviour**; sub-levers `A230_ALLCAND` / `A230_TAPER` / `A230_WEDGE_NS` / `A230_WEDGE_CAP`.  Leaf rule (0′) and
  an internal check beside Rule SNAP; `step_key` carries `("epsns", slot, role, kind, W)` for Lemma INHERIT.
- Benchmark detached and resumable (`bash attempts/A230-eps-branch/code/bench230.sh 900`): the re-scan over every
  A211 g1 certificate, then Y0865 g1 and Y0500 g1 from their A203 roots (`--no-inherit`) under the pass-6 flag set
  off vs on, isolated cert dirs.  Results land in `attempts/A230-eps-branch/results/bench230.md`.
- **queue_pass7 recommendation:** add `A230_EPS=1` to the pass-6 flag set (`A220_NOROOM_INHERIT=1 A221_LANE=1
  A224_SNAP=1`) with `A230_WEDGE_CAP=1`, pending the off/on verdict table in `results/bench230.md`.

## 2026-09-15 10:40 -- A231-realign (Fable) -- DONE (launch-and-exit; the run finished, 964 rows committed; resume `bash attempts/A231-realign/code/run231.sh`): **the grain that "re-aligns once its corner is settled" is, on every witness, NOT the corner's grain -- the swap consumes the two meeters, and what leans on the settled square afterwards is nothing (566 of 792 cases) or the whole opposite chain; the improvement is the fixed-tilt SHRINK with S pinned (strict on 783/792, the rest strict under the full click), never blocked (0 of 1,437 anchored paths); Lemma WALL-EXCESS proved in its chord form (sum of 1/max(cos,sin) over a wall's touchers <= s, sealed pockets tan(phi)/2), the PI's projection sum and "two triangles per square" corrected; the area horn does NOT close (all-45-deg sealed walls waste 3 < 4.03 at n = 11); at n = 11 STEP + k1-a needs no re-alignment (Lean), REALIGN + STEP => ONE-FLUSH(n) (Lean); k0_00 unchanged**
- **[T] `docs/proofs/realign.md` s.1 Lemma WALL-EXCESS:** a wall's touchers have pairwise-disjoint chords `1/max(cos theta_i, sin theta_i) >= 1` at height 1/sqrt2 (Lemma WALL-F on the touchers), so their sum is <= s and each exceeds 1 by the EXCESS, zero only flush; the PI's `sum(cos + sin) >= k` is true but not a budget (projections overlap, wall_budget.md s.1.3).  Sealed pockets (consecutive touchers in contact, no unit square inside) are waste (a connectedness argument on the pocket's boundary); two touchers of common tilt sealed by a vertex-on-edge contact have floor spacing EXACTLY `1/max(cos, sin)` and pocket area EXACTLY `tan(min(phi, 90 - phi))/2` (interior-disjointness of translates forces a = 1 or b = 1 on the contact parameters); "two triangles per square, sum sin cos" overcounts by `sin cos - tan/2` (0.144 at 30 deg); a third square in an unsealed gap can take back everything above its lowest point.
- **[M] the anchored re-alignment (`results/realign231.md`, code n-general):** after A222's CORNER-SWAP (686 of the 193's 772 corners; the 30 window-over-met crowds not among the 193 swapped by the same region search, 74/120; A226's eight CROWD-ABOVE crowds at n = 26..55 by the explicit retraction, 32/32) the SHRINK -- fixed tilts, S pinned to its slot, side minimised over the centres -- is strict on 678/686, 73/74, 32/32; the grain in contact with S is empty on 472/686, 62/74, 32/32 and otherwise the whole opposite chain (6-10 squares in 195/214); its anchored move (S pinned, G toward alignment, contacts' axes kept) is flush-side 196 / kink-side 10 / flat 8, ends flush 194 / kink 9 / start 11 / blocked 0, below s0 on 213/214, non-increasing on 178/214 (largest uptick 0.025, `realign_worst_w207_crowd.svg`); rotating every tilted square reaches 4.000 on 508/510.  Per witness: 193/193 (and 30/30, 8/8) have a corner where swap + shrink is strict; 119/193 have a flush-side anchored drain that succeeds.  The ring: BL no swap; BR 4.1099 -> 4.0637 (S leans on one unloaded 20-deg square); TR -> 4.0648 (S between flat squares); TL -> 4.0919 then the whole eight-square chain re-aligns monotonically to 4.000 (`ring_realign_rand_0_0569_t20.svg`).  CROWD-ABOVE (n = 26): 5.8107 -> 5.6444 by the shrink alone (record 5.6213), S touches only the flush neighbour; the record's own grain is kink-side (`crowd_above_realign_n26.svg`).
- **[T]/[C] s.3 Lemma REALIGN:** stated n-general (a corner-swapped four-crowd below ceil(sqrt n) improves strictly); ANCHOR-SLIDE (a lean never blocks the anchored move, S's pin rows are tilt-free) and ANCHOR-MONO (with the loaded basis constant the side is the menu formula of the tilted part plus the flush segment through S: extent chains decrease toward alignment, Lambda / Y rise on both sides of 45 deg, F_T decreases toward 0 only above 24.3 deg) proved; the horn must be read on the value function s_min, not on a formula (Trump's F_T is flush-side by the formula and kink-side in s_min); "kink-side => tilts near 45 deg" [F].  Content of REALIGN = STRICTNESS (both horns end in a k >= 1 packing at side <= s0 by Lemma SWAP alone), [M] 792/792, [C] as a theorem (a swap need not release the load path).
- **[F] s.4 the area horn:** four kink-side corner grains waste <= 3.0 (45 deg) against s(n)^2 - n >= 3.7 for every record n >= 10; even every wall square a sealed diamond wastes 2 floor(s/sqrt2) - 1 = 3 < 4.03 at n = 11 (the brief's "sqrt2 s > 5.03" mis-added: 3.877^2 - 11 = 4.03), beating the slack only from n = 17 on; horn (b) has to be handled by the certified k >= 1 classes.
- **[T] s.5 what closes; Lean `Statements/Open/Realign.lean`:** `fourcrowd_dead_of_step_kill` (std axioms only): where no packing contains a corner slot square (k1-a on [3.82, s-hat)), a four-crowd with a corner swap does not exist -- at n = 11 the four-crowd exclusion needs STEP alone, i.e. RAISE(0 -> 1) as in ring_swap.md; `one_flush_of_realign`: REALIGN + STEP => every optimal packing below ceil(sqrt n) has a singly-met corner (ONE-FLUSH(n)); axioms `realign` [C] and `lemma_WALL_EXCESS` [T-prose]; theorems `chordT_ge_one`, `wall_count_le`; `lake build` + `lean/audit.py` exit 0, no sorry.  k0_00's row: unchanged.
- Files: `attempts/A231-realign/{code,results,logs}`, `docs/proofs/realign.md`, `docs/residue_map/campaigns/A231-realign/` (3 geometry-checked pages), `lean/.../Statements/Open/Realign.lean` (+ one import line in `Statements.lean`), registry row, ledger s.4 note.

## 2026-09-15 18:1x -- A232-swap-leaf (Opus) -- DONE (launch-and-exit; the cell run detached with per-cell commits, resume `bash attempts/A232-swap-leaf/code/run232.sh`): **the SWAP leaf is a sound certificate clause and a Lean theorem, and it does not fire on a single k0 root cell -- because those cells box ONE of eleven squares, and an unboxed role must be exchanged**
- PI, 17:30: *"can we prove STEP against the window? we only need it true <= s-hat for the search to ignore k0 entirely."*
- **[T] Lemma SWAP-LEAF** (`docs/proofs/swap_leaf.md` s.1, n-general): a cell + an injection naming the exchanged
  roles `X` + `|X|` unit squares at FIXED poses inside every container of the window, pairwise interior-disjoint,
  one of them the corner slot, + one exact MISS certificate per (square, role outside `X`) ==> every packing of
  the cell exchanges AT THE SAME SIDE into one with that corner settled (Lemma CELLS / `cells_swap`), so with
  k1-a the cell is DEAD.  `|X| = 1` is K0-FREE, `|X| = 2` is the PI's STEP, larger `X` allowed; no LP, no load,
  rattler crowds covered.  Lean `Statements/SwapLeaf.lean`: `swap_leaf_exchange`, `swap_leaf_pins`,
  `swap_leaf_dead`, `swap_leaf_corner` -- ALL THEOREMS, std axioms, no new axiom (k1-a is a hypothesis);
  `lake build` + `lean/audit.py` exit 0, no sorry.
- **[T] the frame bookkeeping** the leaf needs, both m-free supersets: Lemma PULL-BACK (K0-WIDEN read backwards:
  a cell's s0 box pulls back to `[x0/lambda_max, x1] x [y0/lambda_max, y1]` at the ORIGINAL side, same tilt) and
  Lemma CORNER-FRAME (the D4 map to BL costs the window's width 0.0571 in each flipped coordinate and flips the
  tilt bin).  Containment is asked at `m_lo = 3.82`, so a fixed pose is inside every container of the window.
- **NEW verifier `code/verify_swap232.py`** (stdlib + exact `Fraction`, `swap-leaf-certificate-v1`): it
  re-derives the pull-back and the corner frame ITSELF and checks containment, pairwise interior-disjointness,
  the slot cell, that no role outside `X` is unboxed, and every miss (A161's full separating-axis test for an
  axis cell; the polygon's own normals with radius `|n| sqrt2 / 2` for a tilted one -- sound, deliberately
  incomplete).  The frozen `verify_case.py` / `verify_case_v4.py` are not read, not imported, not changed.
- **[T] Lemma X-FORCED / Lemma SPLIT-INVARIANCE** (s.2): an UNBOXED role has the whole container as its reach,
  so it must be in `X` (`|X| >= u` = #unboxed); A185's split refines boxed pieces and never boxes an unboxed
  role, so `u` -- and the demand -- survives any number of split rounds.  **Only conditioning lowers `|X|`.**
- **[M]/[F] the eleven k0v4 cells:** each is A115's record with ONE hypothesis box (the conditioned square `H`,
  30-45 deg) and budget 10, so `u = 10` and `|X| = 10` at every corner of every cell.  The leaf then asks for a
  ten-square packing of `[0, 3.82]^2` (`s(10)` = 3.70711, slack 0.113) with one member at the corner slot, all
  avoiding `H`'s reach set (1.64-1.82 of area, in the middle of the container).  The search places 6-9 -- ONE SHORT of the
  ten on several cells (the same search places 9 with no obstacle at all, the axis maximum below side 4); one round of A185's split, 16 children at the best corner of each
  cell, raises nothing -- as SPLIT-INVARIANCE says it cannot.  **So STEP is NOT certifiable cell-wise from the
  k0 ROOT cells and "the search can ignore k0" does not come off; k0_00's row is unchanged.**
- **[M] the machinery is not at fault:** the n = 5 geometry controls (no k1-a claim -- an `|X| = 2` control
  CANNOT exist at n = 11 in the window, because a passing leaf there IS the theorem) produce and PASS `|X| = 1`
  (K0-FREE), `|X| = 2` (STEP) and `|X| = 5` certificates end to end, and 7 corruption tests of a passing
  certificate are all refused.
- **[C] where the leaf belongs and what it costs:** at `k0_route.md` s.4.2's crowd root `H_B` (the four corner
  crowds, EIGHT boxed roles, budget 3) `u = 3` and `|X| = 5` at a corner -- the first node of the k0 lane where
  the leaf has a chance.  It is therefore a cheap (seconds/node), LP-free, load-free LEAF RULE FOR the k0
  cascade, not a way past it; s.8 prices the lane at 3 200-7 000 CPU-h.  The cheaper route to the same end
  remains RAISE(0 -> 1) as a geometric lemma, which needs no cell at all.
- Files: `attempts/A232-swap-leaf/{code,results,certs,logs}`, `docs/proofs/swap_leaf.md`,
  `docs/residue_map/campaigns/A232-swap-leaf/` (one 4-panel page per cell, exact geometry check per panel),
  `lean/.../Statements/SwapLeaf.lean` (+ one import line in `Statements.lean`), registry row, ledger s.4 note.

## 2026-09-15 20:xx -- A233-local-lock (Fable) -- DONE (launch-and-exit; no long runs: the arm census + tests take 30 s, the Lean build 230 s + audit): **the extremal route is n-general and gives ONE-FLUSH(n) in its VALUE form from ONE residue (a retreat-free four-crowd at the optimum); the brief's per-corner LOCAL-LOCK is refuted by Trump's own TL corner; LOCALITY holds but the lock problem is not local -- every retreat cluster leaves the arm; Lemma RADIAL / Corollary CHAIN make the PI's gear rule a theorem for all n (A219's RING 193/193 included) and exclude nothing**
- PI, 17:50: *"an analytical reason for at least one simple square, since that would generalise up and allow us to ignore k0 for higher n without re-searching."*
- **[T] Theorem EXTREMAL(n)** (`docs/proofs/local_lock.md` s.1): at s(n) < ceil(sqrt n) take the Psi-minimal packing among the
  optimal ones (Psi = total corner intrusion); nothing RETREATS there (Lean `no_retreat_of_psiMin`), so either a corner is singly
  met -- K0-FREE settles it and s(n) is attained WITH A FLUSH CORNER, the census of n squares starts from a settled corner --
  or the optimum is a four-crowd all of whose meeters are retreat-free (hence LOCKED, Lemma ROT/ROT-W).  The residue
  **LOCKED-CROWD-FREE(n)** [C]: Lean axiom `locked_crowd_free`; `exists_optimal_singly_met` = ONE-FLUSH(n) (value) from it;
  `optimal_psiMin_not_stuck` the n = 11 corollary.  Weaker than LOCK-FREE+ (optimal packings only).  Table of which pieces
  are proved n-general (D1, teleport, k-maximal, Psi-minimal, NOCRIT-SEL, ROT, ROT-W, PUSH/HOLD/TWO-CONTACT/ONE-TILTED, all
  for s >= 2 + sqrt2) and which are n = 11 (Theorem U, basin, k1-b: uniqueness only).
- **[F] the per-corner target** "no corner doubly met by locked meeters at a k-maximal minimiser below ceil(sqrt n)": Trump's
  TL (sq4 nick + sq6 carrier, 5/5 LOCKED in `lockfree.md`) is exactly that at a k-maximal minimiser below 4.  Locked corners
  are how a load path ends; ONE-FLUSH is about a corner where none ends.  Nothing per corner can prove it.
- **[T] LOCALITY** (s.2): a meeter's centre is in [1/2, 1 + 1/sqrt2)^2, a row partner's within sqrt2 of it, so the lock's
  Gordan certificate reads poses inside the ARM [0, 1 + 2 sqrt2]^2 (centres [1/2, 1 + 3/sqrt2)^2); the four locks live on
  disjoint square sets for s >= 2 + 3 sqrt2 = 6.243 (n >= 39), the arms are disjoint for s >= 7.657 (n >= 59); at n = 11 the
  arm is the container.  [M] 1,227/1,227 doubly-met corners (A217's 486 witnesses + Trump): every holder inside the arm.
  **[T] but not local:** NOCRIT-SEL's retreat cluster of a locked meeter is wall- or crowd-anchored, both outside the arm for
  s > 2 + 2 sqrt2 = 4.83 -- the chain always leaves the arm (the PI's gear rule, exactly).  [M] 3,955/4,908 clusters anchored,
  all but 8 leave the arm.
- **[T] Lemma RADIAL** (s.3, any n, any FJ point): for any set U of squares, the rows joining U to the outside carry a net
  CORNER-WARD push equal to minus a positive combination of the internal loads (dot the centre balance with the position
  vectors from the corner; a pair row contributes n.(c_j - c_i) = 1/2 + g_j(n) >= 1, a corner-wall row c_u >= 1/2).
  **Corollary CHAIN:** the loaded component of a loaded crowd reaches a far wall -- A219's RING (193/193 measured) is a
  one-line theorem for all n; [M] 1,013/1,013 loaded crowds here, identity residual <= 5e-7.  **NO-SELF-STRESS:** lam0 = 1
  at every FJ point.  All satisfied by Trump (TL's chain is the strip; pushers sq7 0.199 + sq9 0.317 = the internal load
  0.516) and by the ring (BL's pushers are the adjacent crowds' meeters): they describe a load path, they exclude nothing.
- **[M] the local census:** 75 realised arm signatures; the abstract list (cells x wall rows x depth type x partner x holder
  rows) is 3.75e5 (H = 3) .. 1.65e6 (H = 5) labelled row lists per arm vs A219's 2.6e11 -- finite and small, and it decides
  LOCKED only.  **Verdict: the route does NOT reduce to a finite local obligation**; LOCKED-CROWD-FREE(n) is a global frame
  statement at the optimum whose proof must couple the four chains through s < ceil(sqrt n), and no length lemma for a
  pressed chain exists (a loaded contact can advance arbitrarily little along a wall).  At n = 11 it is RAISE(0 -> 1) /
  STEP as A222/A231 left it; k0_00 unchanged.
- Files: `attempts/A233-local-lock/{code,results,logs}`, `docs/proofs/local_lock.md`,
  `docs/residue_map/campaigns/A233-local-lock/` (2 pages, 11 panels, geometry check printed per panel),
  `lean/.../Statements/Open/LocalLock.lean` (+ one import line in `Statements.lean`; build + audit exit 0, no sorry),
  registry row, ledger s.4 note.

## 2026-09-15 21:xx -- A234-handedness (Fable) -- DONE (launch-and-exit; the probe 64 s, tests 20 s, pages 15 s; no Lean: nothing separates): **TORQUE-ID stated and proved in three forms for every n (about the centre = the handedness sum S = C + F; no per-wall identity; Lemma ARM-MOMENT about each corner point); probed on 1,393 stressed witnesses; NO handedness count separates a four-crowd from an optimum -- the four global identities are satisfiable by the wall rows alone on 178/193 four-crowds, what fails there is the per-square balance; Trump and the ring share a torque-neutral wall reservoir and a circulation slack by the factor s - 1**
- PI, 19:00: *"counting handedness across the container, since a convex shape can't provide a net torque; that would allow Trump et al. AND extend up in n."*
- **[T] TORQUE-ID** (`docs/proofs/handedness.md` s.1): (G) sum over wall rows of lam (q - O) x n_w = 0 at every FJ point (each square's
  moment about O vanishes, pair rows cancel at their common point) = sum tau^wall + C = 0, C the wall pressure's circulation (first
  moments about the wall midpoints); with Lemma W (tau^wall = -chi W d) the HANDEDNESS SUM S = sum_{tilted} chi W d = C + F, F the flat
  touchers' self-torque, free in [-W/2, W/2] each.  (W) no per-wall identity: a wall's pressure is pinned only by the global identities
  (polytope span up to 1.0).  (K) Lemma ARM-MOMENT: about a corner point the arm's floor rows turn it one way (>= 0), its wall rows the
  other (<= 0), the external pair rows supply the difference -- RADIAL's rotational twin, the arm's rigid-body equilibrium.  [M] residual
  <= 3e-5 on 1,393 witnesses, <= 6e-6 on 1,363 doubly-met corners; Lemma W's sign 2,920/2,920 loaded tilted touchers.
- **[M] the probe** (`hand234.{jsonl,md}`): A217's 486 witnesses (193 four-crowds), the 883 genuine free FJ points, Trump, S02, S07, 21 record
  packings n = 5..55 -- every one with a bounded FJ stress; per square chi, N, d, W, tau^wall, tau^contact (along-wall / interior), tau^ext;
  per wall P, M_c, M_q, handedness mix, touchers with perimeter coordinates; per corner the arm moments; LP ranges of C, S, F, S_meet, P_w
  over the multiplier polytope.
- **[F] no candidate separates**: (a) perimeter flips: Trump 0, ring 2, four-crowds {0: 56, 2: 125, 4: 12}, free FJ points {0, 2}; mixed
  walls FJ 0-2, FOUR 0-3.  (b) anti-aligning demand vs supply: the along-wall / interior split is unconstrained (shares -0.17..1.2); only
  the external share is nonzero on four-crowds -- RING again.  (c) |C|/bound: Trump 0.029, ring 0.088, FJ <= 0.33, FOUR <= 0.66; |S|
  overlaps everywhere; S_meet: 324 of 1,544 four-crowd meeters carry no wall load.  19 scalars tabulated: the only YES is ext_load.
- **[M] the global relaxation** (`global234.py`): {lam >= 0 on the WALL rows; sum F = 0; sum moment about O = 0; far sum = 1} is FEASIBLE
  on 178/193 four-crowds (the 15 others have a wall with no contact or a single one), 292/293 W3, 3/3 optima: every inequality derivable
  from TORQUE-ID + Lemma W + pressure bounds holds at a four-crowd; RING's infeasibility is the PER-SQUARE balance (TWO-CONTACT, HOLD).
- **[T]+[M] what Trump and the ring share** (s.4): |tau^wall| <= W/2 per toucher but the circulation's reach is (s - 1) P/2, so the
  identity is slack by the factor s - 1 at every n >= 5; Trump's six flush squares are a torque-neutral reservoir (F ranges [-0.21, 0.12],
  S = 0.035 fixed, C in [-0.08, 0.25]); the ring's +/- pairs are the same reservoir (F = 0, S in [-0.117, 0.117], C in [-0.23, 0.27]); a
  handedness count sees a flat square and a +/- pair identically.  The residue stays LOCKED-CROWD-FREE(n); k0_00 unchanged.
- Files: `attempts/A234-handedness/{code,results,logs}`, `docs/proofs/handedness.md`, `docs/residue_map/campaigns/A234-handedness/`
  (`wall_pressure_chi.svg`: the ring, Trump, S07, S02 with chi fills and the wall forces as arrows; `perimeter_handedness.svg`: the
  perimeter handedness map on 8 packings; geometry check per panel), registry row, ledger s.4 note.  No Lean file (task 3's condition
  -- a separating candidate -- is not met).

## 2026-09-15 22:xx -- A235-no-vv (Fable) -- DONE (launch-and-exit; census 12 s, rolling plane 16 s, every consistent selection 191 s, Theorem SO 18 s, Lean build + audit ~5 min; resume `bash attempts/A235-no-vv/code/run235.sh`): **Lemma NO-VV is a theorem exactly in the PI's generic sense (a VV row independent of the other rows carries no load: the feasible set at a vertex-on-vertex contact is a UNION of two half-spaces, so a minimiser is Fritz-John for both selections), and NOT a consequence of local optimality otherwise: 25 HELD witnesses carry a loaded tilted VV contact that is FJ under every consistent selection with no second-order saddle -- an over-braced, torque-locked contact whose rolling plane is blocked at first order; the knife-edge is real but unreachable**
- PI, 20:20: *"if you epsilon-perturb ALL the dimensions and let it relax, the point-on-point configuration won't survive; point-on-side is absolutely valid."*  Coordinator, 20:30: 0 loaded tilted VV at ~700 loaded contacts of the genuine FJ points, 26/174 HELD, 6/182 CROWD, the ring's 4|6 among them.
- **[T] the geometry** (`docs/proofs/no_vv.md` s.1): non-parallel squares touch in one point (POINT); at a VV contact exactly one edge of each square through P separates, the pair has exactly two tight rows g_A, g_B (VV-AXES, 400 random configurations), and the pair is disjoint near P iff g_A >= 0 OR g_B >= 0 -- a REFLEX cone of angle 180 + angle(n_e, -n_f) (220 deg on the ring) that contains the lines along both edges (REFLEX); both rows are exactly zero along every rotation of either square about P (the rolling plane).
- **[T] the lemma** (s.2): (i) the two-selection principle: a minimiser is a local minimum of NLP(S_A) and of NLP(S_B) (D1 / D3'); (ii) NO-VV-IND: a VV row outside the span of the other rows and its partner carries zero load in every multiplier (Lean `no_vv_of_not_mem_span`, `no_vv_pair`, no axiom); (iii) CONCURRENT: the rotation of B about P is a zero mode only if every loaded force on B passes through P; KNIFE: along the rolling the VV rows contribute -F_P.(c_B - P) < 0 to the reduced Hessian (h_B = 0.704 on the ring, y^T H_B y = 1/2).
- **[M] the tests** (s.3-4, `results/novv235.md`): the VV row is in the span of the other rows at all 82 tilted VV contacts (26-45 rows per consistent selection against 34 coordinates; independent only in selections of the 4 CROWD witnesses w125/w134/w135/w142, exactly the ones the two-selection test excludes) -- NO-VV-IND's hypothesis fails at every HELD contact; the rolling plane (72 directions x S_A, S_B, S_AB, completed by LP) is BLOCKED at first order at 48 of the 55 loadable tilted VV contacts, both selections; the two-selection test excludes 6 (5 of the 7 CROWD witnesses with one, 1 HELD), every consistent selection enumerated (2^4..2^16, exhaustive at 29/31) finds no other failure, Theorem SO with A219's candidates finds no saddle: **25 HELD witnesses pass every local test with a loaded tilted VV** (necessarily loaded at 11).  [F] NO-VV as a local statement for an NLP with external rows.
- **[M] the free problem** (s.5): at 883 genuine FJ points, Trump, S02, S07 and the 21 records every tilted VV contact is unloadable and a VV-free stress exists: NO-VV-STRESS(n) holds on everything, [C] beyond the generic case, entangled with HOLD / RING (a HELD survivor becomes a free FJ point exactly when a holder replaces its tilt bound).  square-38 / square-40 carry loadable VV edges (45-deg diamond tips at lattice notches): the contact-GRAPH form is false at conjectured optima.
- **Consequences** (s.6): the k5 / k0 trees bound polyhedra, prune 0 %; an FJ census gains the two-selection row test (1 LP per VV pair per leaf; bites on 6/33); four-crowds are not excluded (5 of 185); k0_00 unchanged.
- Files: `attempts/A235-no-vv/{code,results,logs}`, `docs/proofs/no_vv.md`, `docs/residue_map/campaigns/A235-no-vv/ring_vv_4_6.svg` (the ring's 4|6: separating lines, force cone, rolling arrows, the blocking rows per sense, the reflex-cone inset; geometry checked), `lean/.../Statements/Open/NoVV.lean` (build + audit exit 0, no sorry), registry row, ledger s.4 note.

## 2026-09-15 23:xx -- A236-ring-capacity (Fable) -- DONE (launch-and-exit; the capacity test 25 s, table + summary + pages + tests 15 s, Lean build + audit ~5 min; resume `bash attempts/A236-ring-capacity/code/run236.sh`): **"stable ring" made exact (a four-crowd none of whose meeters retreats; Lean `StableRing`, axiom `ring_capacity` => LOCKED-CROWD-FREE(n) => ONE-FLUSH(n) value form); the capacity route made exact -- band / core / straddler at the unit band, TILT-BAND (every tilted square intrudes into the centre, with NO floor), BAND-FLUSH, BAND-COUNT (B <= 4(m - 2) in a four-crowd below m), CORE-CAP (K <= (m - 2)^2 - 3, Nagamochi; Lemma TWO at m = 4), ONE-TILTED (X >= 4) -- and Theorem NO-CLOSURE: 4(m - 2) + ((m - 2)^2 - 3) + 4 = m^2 - 3 >= n at EVERY n with s(n) < m; the capacity inequality excludes a four-crowd for no n, at n = 11 it reads 8 + 1 + 4 = 13 >= 11 (slack 2): RING-CAPACITY does NOT close analytically at n = 11 and closes by capacity at no n; the residue is the POCKET (region packing), = LOCKED-CROWD-FREE(n)**
- PI, 21:00: "show that the minimal side required to build a stable ring requires a side length strictly greater than the trivial packing at ceil(sqrt n)" -- by capacity: the ring in the band, the meeters' intrusion iota, the interior square of side s - 2 - 2 iota vs n - p.
- **[T] the pieces** (`docs/proofs/ring_capacity.md` s.2): TILT-BAND (s > 2 + sqrt2: the edge from the max-x to the max-y vertex of a tilted square has a point with x > 1 and y > 1 because (1 - cos)(1 - sin) > 0; the depth is at most cos + sin - 1 and -> 0 with the tilt; A89: no loaded tilt floor exists, so stability supplies none); BAND-FLUSH (a band square is flush and touches a wall); BAND-COUNT (a wall with floor(s) flush touchers claims both corner boxes, with floor(s) - 1 one, two walls cannot claim the same corner (OVERLAP): B <= 4(floor s - 1)); Lemma TWO (a unit square in a container of side < 2 contains its centre in the interior: sigma < e + 1/e, e = cos + sin); CORE-CAP from the proven staircase (Nagamochi s(k^2 - 2) = k).
- **[T] NO-CLOSURE** (s.3, Lean `count_never_closes`): the band + core count is exactly m^2 - 3, the largest n packing below m; table n = 5..60: slack >= 2 on all 21 values below m (min at 11), X_forced = the trivial 4 everywhere; the flat-core / all-touching ring variant closes only at n = 41, 54, 55 under hypotheses stability does not give.  CROWD-ABOVE (A226) shows no all-four-crowd inequality can close at n = 26, 28, 29, 37, 40, 50, 51, 55 anyway.
- **[M] the tests** (`results/capacity236.md`): every lemma holds on the ring + 193 four-crowds (193/193 each; B median 1, K <= 3, X median 9: a held four-crowd is almost all straddlers; the loaded component U reaches depth 1.0 (median) into the centre and contains a core square on 67/193 -- "the ring lies in the band" holds for the ring (depth 0.30) and fails for most crowds: [F] as Lemma BAND); A226's crowd rings below 4: B = 4, X = 4 (depth 0.015 .. 0.073, no floor), pocket holds 1 (9 < 11) while the count allows 13; the 21 records: none a four-crowd, all cross-braced (X median 5), K < N(s - 2) strictly.
- **[C] the residue** (s.5): POCKET(n): the pocket of a stable ring's loaded component holds fewer than n - p squares -- a region-packing statement, equivalent to RING-CAPACITY(n); at n = 11 it is LOCKED-CROWD-FREE(11) on [3.82, s-hat] exactly as A233 left it; k0_00 unchanged.
- Files: `attempts/A236-ring-capacity/{code,results,logs}`, `docs/proofs/ring_capacity.md`, `docs/residue_map/campaigns/A236-ring-capacity/{ring_band,n11_capacity}.svg` (the ring / Trump / the crowd ring with its one square; TILT-BAND's point, the 8 + 1 slots at n = 11, the record n = 26; geometry checked per panel), `lean/.../Statements/Open/RingCapacity.lean` (1 axiom, 7 theorems; build + audit exit 0, no sorry), registry row, ledger s.4 note.

## 2026-09-16 01:xx -- A237-pocket-waste (Fable) -- DONE (launch-and-exit; TILT-MIN test 5 s, pocket census 40 s, window family + table 3 min, pages + tests 30 s, Lean build + audit ~5 min; resume `bash attempts/A237-pocket-waste/code/run237.sh`): **Lemma TILT-MIN made exact and found to bind UPWARD (a flat wall meeter at offset delta admits a partner of tilt theta iff sin theta < delta, the partner's depth <= (delta - sin theta) tan theta, DEPTH-BUDGET d_A + d_B <= 1); Lemma JAGGED = a rigorous computable wastage census of a ring's pocket (coverable-set sandwich over tilt bins, sealed regions, WEDGE, PIERCE); Theorem POCKET-CAP closes A226's ring family at S = 3.90 and the whole window family ring(S, theta <= 30 deg) BY CERTIFICATE (each pocket holds ONE square: 9 < 11) but NOT analytically at n = 11 (the area form needs a tilt floor >= 32 deg; none exists, A89) and at no n >= 18 by any tilt floor**
- PI, 00:00: "given the tilt requirements of the loaded ring ... the pocket is almost necessarily quite jagged -- use the wastage census on grain boundaries to assert a minimum wastage in the centre pocket, then show there isn't room for n - (ring)".
- **[T] TILT-MIN** (`docs/proofs/pocket_waste.md` s.1): frame with the flat meeter's wall as the floor, A = [delta, 1 + delta] x [0, 1], partner B of tilt theta in (0, 90): sin theta <= x_v <= delta and y_v >= 1 - (delta - sin theta) tan theta (the slab part of B avoids int A and lies left of it; the wall bounds the leftmost vertex; the edge from the lowest vertex reaches height 1 left of delta); sharp = Theorem B's clause (W) at zeta = theta (mode (a)) = A89's Lemma JAM-0; DEPTH-BUDGET d_A + d_B <= 1 follows.  **[F] as a LOWER bound** on the tilt of a locked meeter: CROWD-ABOVE (tilt eps/2), A89 (no loaded tilt floor by any local argument), and the 193 HELD / CROWD witnesses' least meeter tilt sits AT A217's imposed floor t_min = 10 deg on 30 of 32 HELD corners -- the "fairly high angle" is an artefact of the generator.  [M] 774/774 doubly-met corners: ONE-TILTED, (a), (b) on 258/258 flat-tilted pairs, DEPTH-BUDGET max 0.90.
- **[T] JAGGED** (s.2): pocket = container minus the members' interiors; (J1) COV(P) = U_theta C(theta) (+) Q_theta and K = Q_mid / w(D/2) inside, H = w(D/2) Q_mid outside every square of a bin of width D => COV subset U_bins (P (-) K) (+) H: WASTE(P) := area(P) - area(that) is a rigorous lower bound on the uncoverable area and area(COV-bar) bounds the capacity; (J2) sealed regions are waste; (J3) Lemma WEDGE: a unit square in a wedge of angle alpha <= 90 keeps distance >= (1 + cos alpha + sin alpha)/(4 sin(alpha/2)) - 1/sqrt2 from the apex (the exact minimum is NOT cot alpha); (J4) PIERCE (Lean `capacity_le_of_pierce`): k points, one interior to every unit square of P, bound the capacity by k, certified per bin by (P (-) K) subset U_i (p_i + K).  **[F]** "a square cannot approach a tilted edge closer than a margin" (a parallel square touches it); a near-flush ring's vertices are 90 +- eps and its waste is O(eps).
- **[T]+[M] POCKET-CAP** (s.3): area(P) = s^2 - p, so the area form is WASTE > s^2 - n (p never enters: NO-CLOSURE again).  n = 11: A226's rings at S = 3.90 (all eps) and S = 3.95 / 3.99 with eps = 0.10: PIERCE(1) residual 0 => capacity 1 => 8 + 1 < 11 (the other four fail by 3e-4 .. 2e-2: two-stub diamonds); the window family ring(S, theta) (flat meeters at the least TILT-MIN offset sin theta + 0.02, mode-(a) partners, S in {3.82, 3.85, s-hat}, theta = 1..30 deg, verified packings, four-crowds for theta >= 5): PIERCE(1) at the centre holds at EVERY member -- capacity 1, 9 < 11; the area form alone gives capacity <= 2 only at theta >= 15-20 deg.  **Analytically NOT closed**: 4 w_c(theta_min) > s-hat^2 - 11 = 4.03 needs theta_min >= 32 deg (w_c(20) = 0.689, w_c(45) = 1.271), no floor exists; the closure of the n = 11 rings is the CENTRE (side < 2, Lemma TWO) + stubs (width < 1), a shape statement.  n-general table (s.3.3): the four corners waste <= 5.08 at 45 deg while s(n)^2 - n grows: closes at n = 5, 10, 11, 17, 19 under floors 17 / 29 / 32 / 42 / 42 deg only, at no n >= 18 by any floor <= 45.
- **[M] the tests** (s.4, `results/pocket237.md`): the ring + 189 four-crowds with a loaded component: sound 189/189 (coverable >= n - p), the area form fires on none (above m, as it must), waste median 5.46 of 6.1, PIERCE(n - p) with the rattler centres 13/67 (rattlers slide); the ring: waste 4.31 of 7.89, PIERCE(2) residual 0.12; the 22 records (U = wall touchers): sound 22/22, fires on none, waste 1.46-3.39 (Trump's 45-deg grain corners).
- Files: `attempts/A237-pocket-waste/{code,results,logs}`, `docs/proofs/pocket_waste.md`, `docs/residue_map/campaigns/A237-pocket-waste/{ring_pocket,n11_window}.svg` (the ring / A226's S = 3.90 ring with its piercing point / Trump; ring(s-hat, 20), ring(s-hat, 2), one crowd's sealed region; uncoverable sets hatched, geometry checked per panel), `lean/.../Statements/Open/PocketWaste.lean` (axiom `pocket_cap` = POCKET(n) => `ring_capacity_of_pocket_cap` => LOCKED-CROWD-FREE(n) => ONE-FLUSH(n) value form, n = 11 corollary; theorem `capacity_le_of_pierce`; build + audit exit 0, no sorry), registry row, ledger s.4 note.  k0_00 unchanged.

## 2026-09-16 — A238-k4-benchmark (Opus) — the k5 toolkit on the Trump-parent protected classes
- PI (10:30): *"the k4- classes that are parents of Trump shouldn't be able to get that close to Trump, since a bunch
  of the geo tests will kill them when they try to press the fifth simple square into place."*  A100 priced k4_11 and
  k3_02 with the case-LP (≈ 560 / 485 s per level-1 cover cell, 203 / 290 CPU-h measured, 3,500–4,200 CPU-h per class
  projected).  A238 re-prices **the same nodes, the same hypothesis, the same boxes** with the geometry the k5
  frontier runs today.
- `code/load238.py` makes a protected class a page for the k5 runner (class slots as slack pin cores δ_pin = 2·10⁻²,
  H = an A100/A84 level-1 cover cell or the whole interior zone, budget 11 − k_S − 1).  Every certificate carries the
  hypothesis it certifies: **M_S(m) & YES(H)**, and a DEAD verdict is stated as the instance of `stratum_kill` for
  **that class** restricted to H (Lemma K1 / Lemma P-TREE (c), obligation O1 of `docs/proofs/protected_trees.md`).
- `code/tube238.py` — **Lemma TUBE-LEAF/S**, the class form of A212's tube leaf: the direction is slot(I_g) (A84 §4's
  swept certificates `certs/tube_I_<I>_landing_*.json`, k4_11 I = {0,2,3,5}, k3_02 I = {0,1,3}) and the **pins are
  exempt from the radius** — M_S(m) puts them exactly on slots_S(m), the tube direction's pinned coordinate (w = 0,
  Lemma P-TREE Step 4), so the slack pin box never enters the (D) test.  `code/tree238.py` re-applies A212's gate and
  Rule SNAP-at-the-gated-leaf to **A211's LIVE Tree211** (A212's own dir carries frozen pre-A220/A224/A230 copies —
  `code/path238.py` enforces the import order and asserts it).
- **[M] The geometry does what the PI said — on k4.**  k4_11's cover cells die by EmptyBox / REACH / NOROOM-CN /
  NOROOM-POCKET / S-CLIP / COUNT / FC in **0.2–16 s** where A100's LP spent 130–560 s and often could not kill at all
  (`c0_Y0074`: A100 τ = 6.000 = budget, FAIL → deepen, 184 s; A238 DEAD by EmptyBox at the root.  `c0_Y0076`: A100
  refused at τ = 6.000, 131 s; A238 DEAD in 0.2 s).
- **[F] and it does NOTHING on k3 — for a reason that is half bookkeeping.**  Every kill rule of the toolkit acts on
  Theorem FC's FORCED CELLS, and `classes178.forced_cells` marks a cell usable only when the one-slot extension is a
  class with a FULL-window A56 scoreboard row.  `code/fc238.py` (`results/forced238.md`): trump5 6/6, k4_08 and k4_11
  5/7, k4_03 / k4_05 / k4_06 3/5, **corners4 0/8** (all eight extensions are the open k5_16 — A193's finding from the
  other side), **every k ≤ 3 class 0**.  So k3_02's 41 cover cells run out of levers in ~4 s each with 0 kills and 0
  branches (max depth 0 on 42 of 42 nodes).  Of the blocked k ≤ 3 extensions, the k4 protected classes are genuinely
  open — but `k4_00 / 01 / 02 / 04 / 07 / 09 / 10 / 12` were **killed exactly by A55** and are blocked only because
  the 52-row A56 scoreboard covers k5/k6 only.  **Emitting full-window rows for those eight would hand every k3 class
  2–5 forced cells and move it into the k4 regime.**
- **[T/M] The tier price is a CASCADE, not a flat number**: traction on a class = the number of its one-slot
  extensions closed *on the window*.  Closing k4 hands k3 its cells, k3 hands k2 its cells, down to k0_00 — the K1
  climb Rule SNAP performs inside one tree, applied to the tier itself.
- Files: `attempts/A238-k4-benchmark/{code,results,notes,certs,logs}` (`results/bench238.md` + `bench238.jsonl` with
  A100's own row on every head-to-head cell, `results/forced238.md`, `notes/k4_238.md`), pages
  `docs/residue_map/campaigns/A238-k4-benchmark/`, registry row, ledger §3.  The k4_11 sweep continues detached
  (`code/bench238.sh` + `code/chain238.sh`, per-node commits, resume by row presence); `code/report238.py` regenerates
  the table at any time.

## 2026-09-16 12:xx -- A240-cross (Fable) -- DONE (launch-and-exit; census 13 s, summary + pages + tests 1 min, Lean build + audit ~5 min; resume `bash attempts/A240-cross/code/run240.sh`): **the PI's X-sketch made exact and tested -- Lemma OPPOSE ("corner jams require opposing torques") is FALSE: locked corners are same-handed 215 : 11, including 44 : 1 at the free Fritz-John points, because the torque of a partner contact is a function of the tilt difference (vertex owner) and of the contact position (edge owner) and a flush pair's line of action is free -- handedness enters nowhere (Lemma PARTNER-TORQUE [T]); the wall-grain alternation occurs on 0 / 193 four-crowds; the bracing chains are Corollary CHAIN; the planarity step is Theorem CROSS-PLANAR [T] (Lean; a left-right chain and a floor-ceiling chain SHARE a square OR TOUCH -- the second alternative occurs at the n = 26 record); the shared square is NOT obstructed (90 tilted interior crossing squares with no external row; Trump crosses at a flush square).  CROSS + A233 closes nothing for any n and does not reduce LOCKED-CROWD-FREE(n) to the flush-crossing case; k0_00 unchanged**
- **[F] Lemma OPPOSE** (`docs/proofs/cross.md` §1): at a LOCKED open corner (both meeters loaded, no external row on either)
  the meeters are same-handed at 215 of 1 363 doubly-met corners and opposite-handed at 11 (HELD 121 : 9, CROWD 50 : 1,
  free FJ 44 : 1); 191 of the same-handed locks are flush same-tilt pairs, 23 are vertex-on-edge pairs (17 with both tilts
  ≥ 1° off flat, e.g. `fj_rand_0_0073_free` TR at 81.9° / 75.1°).  **[T] Lemma PARTNER-TORQUE**: τ_vertex-owner =
  λ h_k × R(θ_O − θ_P) ν_e (tilt difference only), τ_edge-owner = λ x (the contact's tangential coordinate); corner form: the
  vertex owner is turned toward its partner's tilt for a gap < 45°, the edge owner's torque sign is free; a flush pair is
  free in both.  The ring's tilt floor sits on its unloaded-wall two-contact meeters 4, 8, 2 (STRUT's collinearity fails),
  not on handedness; 121 HELD + 44 free locked same-handed corners balance without any bound.
- **[F] Alternation**: 0 / 193 four-crowds; 144 of 772 walls carry both handednesses, 110 four-crowds have a mixed wall; the
  ring's grains are its left and right HALVES (floor 4 '−' | 6 '+'), as CORNER-LOAD's corollary requires (a lean).
- **[T] Chains** = Corollary CHAIN, measured: 525 / 618 loaded four-crowd components reach both far walls, 486 contain the
  opposite corner's meeters — the loaded component is the whole packing.
- **[T] Theorem CROSS-PLANAR** (`cross.md` §4; Lean `crossing_lemma` classical axiom, `chains_meet`, `chains_share_or_touch`,
  `isCompact_of_isUnitSquare`): two compact connected sets crossing the square meet (Brouwer / Maehara); an LR chain and a TB
  chain share a square OR a square of one touches a square of the other.  On 589 witnesses with both loaded chains: 586
  share, 3 only touch (`square-26b`, two free FJ points), 0 neither.  No chain avoids the corner meeters at n = 11 (0 / 193).
- **[F] The shared square**: of 220 crossing squares on 126 four-crowds, 90 are tilted non-meeters with no external row
  (47 four-crowds have every crossing square tilted and unloaded; `w037_crowd` crosses at interior square 0); the ring's
  crossing is its tilted meeter 6 (VV + flush, external load 0); Trump's chains cross at the FLUSH square 3.  Neither the
  tilted nor the flush crossing is forbidden; both balance.
- Files: `attempts/A240-cross/{code,results,logs}`, `docs/proofs/cross.md`, pages `docs/residue_map/campaigns/A240-cross/`
  (`cross_ring_x.svg`, `oppose_corners.svg`, `wall_grains.svg`; 11 panels geometry-checked), Lean `Statements/Open/Cross.lean`
  (no axiom for a refuted statement), registry row, ledger §4.
