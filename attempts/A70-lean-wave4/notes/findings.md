# A70 — Lean wave 4: findings (Fable lead, 2026-09-02)

Labels: [T] proved, [F] finding, [C] open, [E] engineering.

Verdicts: T1 LEAN-PROVED (V.CASE soundness + one end-to-end certificate replay;
axiom audit clean). T2 RUNG (a) LANDED for BOTH E.A22 and E.A36 (exact-rational
stdlib replays of both frozen re-checkers, every check reproduced, every
corruption gate fails as required — mpmath.iv is out of the rigidity chain's
decision path at the Python tier); Lean rungs (b)/(c) open.

## T1 — V.CASE LEAN-PROVED, one certificate replayed end to end

* [T] **The case-LP verifier soundness is now a Lean theorem chain**, and one k5
  pin-set certificate is replayed end to end.  Files (all in
  `lean/PackingCertMathlib/PackingCertMathlib/`):
  - `CaseChecker.lean` — `checkCaseI`, the port of `verify_case.py`'s decision core
    (core-Lean `Rat` exempt tests over the A64 integer measure layer; `sift`/
    `clipI`/`splitI` shared verbatim with `MeasureChecker.lean`);
  - `CaseSat.lean` — `sat_squares`: SAT sufficiency for two squares (see below);
  - `CaseHyp.lean` — `coreSet`/`InZone`/`CaseExempt` semantics; `coreExempt_sound`,
    `nofamExempt_sound`, `exemptB_sound` (every exemption discharge really meets a
    core / really sits in a zone, for EVERY placement of the box);
  - `CaseBridge.lean` — `goC_sound` (branch-and-bound with the exemption branch),
    `checkCaseI_price` = **claim (P2) of the frozen spec** (scaled by `wd`),
    `priced_dichotomy_scaled` (A68's pigeonhole at integer weights),
    `checkCaseI_no_family` (Lemma B-NO form: some non-owner is NO-exempt),
    `checkCaseI_kill` (empty `nofams`: the `hcert` input of A68's `lemma_B`,
    produced per PASS file — exactly the residue A68 named);
  - `CaseData506.lean` (generator `lean/gen_case_lean.py`) + `CaseK506.lean` — the
    pilot replay: `attempts/A56-sparametric/certs/c2/k5_06.lo.json` (k5_06 pin-set
    kill at `s = 191/50`, 10 atoms, 5 cores, budget 6, depth 44); `check_k5_06_lo`
    by `native_decide` (seconds); `k5_06_lo_kill` (no strict family of 11 closed
    unit squares in `[0,191/50]²` has designated owners containing the 5 cores);
    `k5_06_lo_kill_packing` (the λ-dilated interior-disjoint form via `lemma_B`).
  Cross-check: the frozen Python verifier under `--no-float-prepass` PASSes the
  pilot with the same tree statistics (8 402 boxes, 1 631 core-exempt).
  Axioms: every soundness theorem `propext, Classical.choice, Quot.sound` only;
  the three pilot theorems add exactly
  `check_k5_06_lo._native.native_decide.ax_1_1` (the A64 `check_3_82` pattern).

* [T] **The SAT sufficiency direction is real, load-bearing mathematics, now
  machine-checked** (`sat_squares`).  The spec cites it in one parenthesis ("SAT
  for convex polygons: non-separation on all edge normals => intersection"); no
  prose lemma in the repo covered it (A68 found the citation UNNECESSARY for
  B.0(a) — but for exemption soundness it is unavoidable: an exempt-discharged box
  must really meet the core, else a core-free placement could hide in it).
  Proof: the Minkowski body `[-a,a]² + [-1/2,1/2]u + [-1/2,1/2]u-perp` is an
  octagon; membership of the centre offset follows from geometric Hahn–Banach
  (`geometric_hahn_banach_closed_point`) plus a support bound `<d,n> ≤ h_P(n)` for
  all `n`, proved on 4 cones (× central symmetry) between consecutive generators —
  on each cone the bound is a nonnegative combination of exactly TWO of the four
  checker inequalities, `linear_combination` multiplier `(±n_i/2)·(c²+s²−1)`
  (cone identities verified in sympy first; all four `nlinarith`s landed on the
  first compile).  Degenerate angles (`s = 0`, `c = 0`) by clamping.

* [F] **The natural constructive shortcut is FALSE.**  "Clamp the centre offset in
  the unit square's frame, check the residual against the core box" fails:
  explicit counterexample `c = 0.8, s = 0.6, a = 10, w1 = 13.75, w2 = 0.5` — all
  four overlap conditions hold, yet the residual's first coordinate is
  `10.6 > a = 10`.  The intersection point must move core- and square-side
  coordinates JOINTLY (the octagon feasibility); a future "elementary" write-up of
  the exemption rule must not use the projection heuristic.

* [F] **Spec/code disagreement (the brief's promised finding class).**
  `docs/specs/case_lp_certificate_v1.md` §1 says half-side `a_j ≥ 0` and §2 says
  "`a = 0` (point core) is legal and used by A53-lineage pin certificates".  The
  deployed loader (canonical A53 copy, sha `521cb01f`, the very file the spec
  freezes) REJECTS `a ≤ 0` ("bad core"), and a scan of ALL 9 217 cores across
  the repo's certificates finds ZERO with `a = 0`.  Wrong on both counts; dated
  erratum appended to the spec (original text kept).  `checkCaseI` mirrors the
  deployed gate (`0 < a`); the soundness proof only needs `0 ≤ a`, so point cores
  would be sound if ever enabled.

* [F] Two further small gaps the Lean exposes:
  (i) `nofams` zone fields are NOT validated by the loader (no `x0 ≤ x1`,
  no t-interval sanity) — harmless for soundness (an inverted zone exempts
  nothing; the B-NO conclusion is existential), but a clean-room implementer
  should know;
  (ii) the `t = 0`/`t = 1` double parametrisation of axis-aligned squares makes
  set-level NO-exemption (`CaseExempt`) existential over parametrisations — the
  conservative reading; a B-NO consumer gets "SOME parametrisation of some
  non-owner lies in a zone".

* [E] Faithfulness deviations (all decision-neutral, in the `CaseChecker.lean`
  header): float shortlist/pre-filter layers omitted (they only shortlist; every
  Python accept decision is re-derived exactly — spec §5; omitting the core
  pre-filter can only grant MORE exemptions, which the exact test then decides);
  the `4^k` root grid of the parallel driver not reproduced (single root box,
  `fuel = depth`; integer scales `D`, `K` identical to a `--depth` run).  The Lean
  evaluation is its own evidence (native_decide), so bit-identical tree replay is
  not load-bearing.

* [E] Engineering notes (delta over the A64/A68 recipes, for the next wave):
  - core-Lean `Rat` is available WITHOUT Mathlib (arithmetic, order, decidability)
    and its operations are the SAME instances Mathlib's ℚ uses — `push_cast`/
    `exact_mod_cast` work across the checker/Mathlib boundary with no friction;
  - structure eta makes `let (a, b) := f x` in checker defs unfold to `(f x).1`/
    `(f x).2` under `simp only [f]` — bridge lemmas can be keyed on the checker's
    own helpers (`ratCosSin`, `rmul4`, `gInf`) instead of raw internals.
    COROLLARY: name every checker subcomputation as a top-level def (`rclamp0`,
    `rbabs`, `gInf`); RESTATING a checker-internal `ite` in the bridge file fails
    `rfl` (Decidable-instance mismatch), while a named def costs nothing;
  - `push_cast` can rewrite `((c.n : Int) − (len : Int)) * wd` toward a
    nat-subtraction cast — confine casts with an explicit
    `hcast : (intExpr : ℝ) = ...` (`push_cast; ring`) then `rw [← hcast]`;
  - `positivity` cannot see through `cosT`/`sinT` (plain defs) — use explicit
    `mul_nonneg`/`add_nonneg` with `cosT_nonneg`/`sinT_nonneg`;
  - `rw [hz]` where `hz : z = bigger-expr-containing-z-projections` rewrites the
    RHS occurrences too — use a `calc` through `f z = f (decomposition)` instead.

* [C] Residues after T1 (named):
  - **corpus-wide replay**: a separately-priced wave (per BRIEF).  Route: run
    `lean/gen_case_lean.py` per certificate (68 kill certs + A60/A61 leaves) at
    the report's depth, `native_decide` each (pilot cost: seconds; a depth-60
    convention run needs per-cert data at depth 60 — scales are baked into the
    emitted data, nothing else changes);
  - **B.2-prime owner-frame criterion** (tilted cores) remains prose-only;
  - `checkCaseI` speaks at the single declared side only — window/parametric
    coverage stays V.PARAM (unchanged);
  - the composed `stratum_kill` instantiation still needs the census interface
    `hface` (A68 T3, F11/H2) — unchanged by this wave.

## T2 — E.A22/E.A36 rung (a) LANDED: exact-rational replays, mpmath.iv out

* [T/M] **Both frozen rigidity re-checkers now have stdlib-only exact replays**
  (`attempts/A70-lean-wave4/code/`, frozen originals untouched):
  - `a36_check_exact.py`: the full A36 basin chain
    ([S][N][A][O][Z][G][H][K][E][P][V][L], order-2 interval jets, 70 rows) over
    all 17 certificates — 339/339 checks PASS in 10.8 s; all 5 corruption gates
    (omega-sign, h-big, drop-aux, drop-branch, wrong-branch) fail as required.
    Values reproduce the original's profile exactly (beta = 0.44591,
    psi/h = 0.9979, x* = 5.16e-58).  Logs: `logs/a36_exact*.log`.
  - `a22_recheck_exact.py`: the full A22 Krawczyk chain (G / K on r_N / K on
    r_0 / K for S2 / V / E / B (68 Farkas rows) / F feasibility) — ALL CHECKS
    PASS in 1.5 s; 4/4 corruption gates (z0-big, z0-small, mu, spec) fail as
    required.  beta = 0.6339, max|K|/r = 0.059, tangential margin 0.019 —
    matching the mpmath original to displayed precision.  Logs:
    `logs/a22_exact*.log`.
  Kernel (shared): intervals as Fraction pairs OUTWARD-rounded to the dyadic
  2^-330 grid after every operation; cos/sin enclosures by certified alternating
  Taylor partial sums (|x| <= 1 asserted; term ratio <= 1/2 so partial sums
  bracket) + monotonicity/evenness on the sign-split interval; the original's
  float upward-fudges (`nextafter`, `sum_up`'s 1+1e-12) replaced by exact values
  (sharper, still upper bounds); the [P] fixed-point iterate rounded UP each
  step (monotone map, nonnegative coefficients — the limit stays an upper
  bound), with an early divergence exit (sound: leaves the gate failing).

* [F] **Rung (a) did NOT need the t-parametrisation.**  The brief's cure
  (rational t-intervals) is one way to exactness; but the only mpmath.iv content
  in either checker is (i) interval arithmetic and (ii) cos/sin enclosures, and
  (ii) is exactly computable at rational points by alternating Taylor bracketing
  (all tilts satisfy |theta| <= 0.71).  Staying in the theta-frame means ZERO
  re-derivation of certificate constants (omega, Y, S, h, radii all consumed
  verbatim) — the t-frame re-emission would have required re-deriving the
  psi-contraction data.  For the LEAN rungs (b)/(c) the choice reopens:
  t-parametrisation gives transcendental-free native_decide computations, while
  the Taylor route needs cos/sin bounds in Lean (Mathlib has quartic
  `Real.cos_bound`-class lemmas; a chain of certified Taylor brackets is also
  formalisable).  Named obligations: rung (b) = A22 uniqueness/feasibility in
  Lean; rung (c) = the A36 basin inequality in Lean; both still open, and the
  `basin` axiom in TopLevel is UNCHANGED by rung (a) — what changed is the TCB
  tier of its certification (third-party library out of the decision path,
  checklist F6/E.IV).
* [E] Cost note: PREC = 330-bit dyadic grid; memoised endpoint Taylor brackets;
  the [K] beta triple loop (34^3 interval mults) dominates.  Do NOT feed raw
  z0 rationals (denominators up to 1e168) into Taylor — round the box endpoints
  to the grid first (the IV constructor does).
* [E] Do NOT reuse A69's sympy-Expr pipeline for any future jet work (A69 [E]:
  Expr blows up ~1000x vs plain Fraction coefficient lists).
