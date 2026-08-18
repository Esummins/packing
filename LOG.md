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
