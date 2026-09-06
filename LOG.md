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
