# A70 — Lean wave 4: log

- 2026-09-02: attempt opened (Fable lead). Read A64/A68 findings (cross-toolchain
  recipe, renames), frozen spec `case_lp_certificate_v1.md`, canonical
  `verify_case.py` (A53 copy, sha `521cb01f` verified). Priority per BRIEF: T1
  (V.CASE) strictly before T2 (rigidity replay).
- Pilot certificate chosen for the end-to-end replay:
  `attempts/A56-sparametric/certs/c2/k5_06.lo.json` (k5_06 pin-set kill at
  s = 191/50: 10 atoms, 5 cores, 0 nofams, budget 6, depth 44; report 8 402 boxes,
  PASS 0.5 s). Cross-checked with the frozen verifier under `--no-float-prepass`:
  PASS, identical stats (8 402 boxes, 1 631 core-exempt).
- F1 found while porting: spec §1/§2 allow `a = 0` point cores ("legal and used by
  A53-lineage pin certificates"); the deployed loader REJECTS `a ≤ 0` ("bad core"),
  and a scan of all 9 217 cores in the repo's certificates finds ZERO with `a = 0`.
  Spec text is wrong on both counts.
- `CaseChecker.lean` written (core-Lean Rat exempt tests + shared A64 integer
  layer); `#eval checkCaseI` on the pilot data: `true` in ~3 s interpreted.
  Refactor: `gInf` split out as its own def (decision-identical; re-validated by
  eval) so the bridge can name it.
- `CaseSat.lean`: SAT sufficiency for two squares (`sat_squares`) — support-function
  cone argument + geometric Hahn–Banach; the four cone identities verified in sympy
  first (multipliers `(±n_i/2)(c²+s²−1)`), all four cone `nlinarith`s landed on the
  first compile. Constructive shortcuts refuted before proving (clamp-in-either-frame
  has an explicit counterexample; recorded in findings).
- `CaseHyp.lean`: exemption semantics + `core_meet` + `coreExempt_sound` /
  `nofamExempt_sound` / `exemptB_sound`; reconstruction `linear_combination`
  coefficients precomputed in sympy.
- `CaseBridge.lean`: `goC_sound`, gates, `checkCaseI_price` (P2), scaled pigeonhole,
  `checkCaseI_no_family` (B-NO) / `checkCaseI_kill` (Lemma B `hcert` producer).
- `CaseData506.lean` (gen: `lean/gen_case_lean.py`) + `CaseK506.lean`
  (native_decide PASS + `k5_06_lo_kill` + `k5_06_lo_kill_packing` via `lemma_B`).
- 2026-09-02 (post-reset resume): full T1 chain green. CaseSat/CaseHyp/CaseBridge/
  CaseK506 build; native_decide PASS on k5_06.lo; axiom audit clean (soundness
  theorems: propext/Choice/Quot.sound; pilot adds only the per-theorem
  native_decide axiom). Modules registered in the root import; full lake build
  green (Measure382Check cache hit, NOT rebuilt). Depgraph V.CASE -> lean-proved,
  svg re-rendered; lean/README matrix updated; spec erratum (a=0 point cores)
  appended to case_lp_certificate_v1.md.
- 2026-09-02: T2 rung (a) EXECUTED after all: code/a36_check_exact.py (17 certs,
  339/339 checks, 10.8 s, 5/5 corruption gates) + code/a22_recheck_exact.py
  (full A22 chain, 1.5 s, 4/4 gates) — exact rational arithmetic, stdlib only,
  mpmath.iv out of the rigidity decision path at the Python tier. Key insight:
  theta-frame + certified alternating-Taylor cos/sin enclosures needs NO
  re-derivation of certificate constants (the t-frame re-emission would have).
  Baselines re-run: both frozen originals still PASS. Depgraph E.A22/E.A36/E.IV
  notes updated. Lean rungs (b)/(c) remain open, named in findings.
