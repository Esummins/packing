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
