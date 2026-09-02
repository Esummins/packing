# A75 — Lean wave 5: findings (Fable lead, 2026-09-02)

Labels: [T] proved, [F] finding, [C] open, [E] engineering.

Verdicts (per node):
* **V.MEAS — LEAN-PROVED.** `MeasurePy.lean` + `MeasurePyBridge.lean`: the `verify_measure.py`
  DRIVER (not just its integer core) is a Lean checker, sound for every shortlist oracle,
  `tscale`, root split and margin (`checkMeasurePy_no_packing`).
* **V.PARAM — LEAN-PROVED, one certificate replayed over the whole window.**
  `ParamChecker.lean` + `ParamBridge.lean` + `ParamData506.lean`/`ParamK506.lean`
  (`lean/gen_param_lean.py`): `verify_param.py`'s 4-D checker with the soundness theorem in
  the real-`s` window form `stratum_kill` consumes (`checkParamI_kill`); pilot
  `k5_06.param` (depth 56, `[191/50, 969271/250000]`) PASSes by `native_decide` in 215 s.
  C.WIN gets the gold verifier accent.
* **D.N1 — LEAN-PROVED** (`Zones.lean`: centre separation, at-most-one, injective/unique/
  bijective zone assignment).
* **C.M1 — LEAN-PROVED** (`Zones.lean`: `M1_transfer`, `M1_transfer_packing`).
* **C.T5T11 — LEAN-PROVED for the two RULES** (`core_meet_same_square`, `refine_cover`);
  the pinguard "parent" classification is a gate on which children may be certified — a
  code invariant, recorded, not a theorem (finding below).
* **B.SEL / C.CC2 — PARTIAL, one named obligation** (`Selection.lean`): the selection
  (`exists_kmax`) and the exchange's geometric core (`teleport_packing`) are theorems; CC-2 /
  CC-2′ (`cc2_stuck`, `cc2_two_meeters`) are theorems CONDITIONAL on the census interface
  `hinc` ("teleporting a non-simple square onto a completable slot raises `k`") — the same
  F11/H2 debt as `hface`.  The H1 degenerate-case audit is done: in the teleport form every
  listed case is absent by the shape of the statement.
* **B.EXACT — unchanged** (A68's `monotone_to_exact` + `hface`); the E.2 D4 bookkeeping is
  still prose.  Owner chip cleared.

Axiom audit (`scratch/Axioms.lean`, `logs/build_audit.log`): every new theorem depends on
`propext, Classical.choice, Quot.sound` only; the three pilot theorems add exactly
`check_k5_06_param._native.native_decide.ax_1_1`.  Full library builds (3175 jobs; the
isolated `Measure382Check` module was a cache hit, never rebuilt).

## T1a — V.MEAS: the Python driver as a checker

* [T] `checkMeasurePy c need ts k pick` (`MeasurePy.lean`) models `Verifier.run` /
  `covered` / `root_boxes` / `main`: `--tscale` (integer), `--split k` (the `4^k` grid with
  depth counter starting at `2k`, i.e. `fuel = depth − 2k`, and the `assert step << k ==
  span`), `--strict-margin` (`need = ⌈(1+m)·WD⌉`, gated `wd ≤ need`), the `known`-tuple
  inheritance (carried as its complement `rest`; nothing is ever dropped — unlike A64's
  `sift`, which drops `outsideAll` atoms), the float shortlist + its "float reject" early
  return as an ORACLE `pick : IBox → List IAtom → Int → IAtom → Bool`, and `main`'s
  `s < 1` vacuous PASS.  `checkMeasurePy_no_packing` is proved for EVERY oracle from the A64
  primitives (`clipI_sound`, `trig_enclosure`, `projI_sound`) + `coverage_no_packing`.
* [F] **No new mathematics was needed.**  The only new lemma is the grid coverage
  `grid_cell` (an exactly-divisible interval is covered by its `m` cells; the degenerate
  `step ≤ 0` case is the `s < 1` root).  The driver's generality (oracle, tscale, grid,
  margin) costs nothing in the proof: `splitPy_sound` never looks at the widths;
  `siftPy_sound` is `sift_sound` minus the drop branch.
* [F] **The residual TCB of V.MEAS is a line-by-line correspondence**, now written
  (`MeasurePy.lean` header): Python `clip_int` = `clipI` (floor/ceil via `Int./` = `ediv`,
  positive divisors), `atom_inside_int` = `projI`+`insideAll`, `(X0+X1)>>1` = `/ 2`,
  `box_trig` = `boxTrig`; `vacuous_int` is NOT on the accept path (selftest only);
  `--scale-weights` and D4 `symmetry` expansion are certificate preprocessing (the gate
  `total < n` is applied AFTER scaling in `main`, so the scaled list is the certificate);
  witnesses, `--max-witnesses(-per-box)`, multiprocessing (PASS ⟺ every root cell passes =
  `List.all`) and statistics are decision-neutral.  Not modelled: a RATIONAL `--tscale`
  (integer only; the campaign used 2).
* [F] The "second implementation" reading of the node is now sharper: `checkMeasureI`
  (A06/A64) and `verify_measure.py` (A08) are two implementations of the same integer
  decision core, and BOTH are Lean-sound (A.F2 and V.MEAS); their box trees agree up to the
  root partition (README: 5 837 883 vs 5 836 650 on the 3.80 certificate).

## T1b — V.PARAM: the 4-D window checker

* [T] `checkParamI` (`ParamChecker.lean`, core Lean) = `verify_param.py`'s `PVerifier.run`:
  clip with the wall at the cell's upper side `SB` (`ctxAt`), `core_exempt_frac_iv`
  (`coreExemptIV`), `atom_inside_int_iv` (`projIV` on `cellAtom` = `SCell.__init__`: exact
  sorted endpoints `[α+β·s_a, α+β·s_b]` over the lcm denominator), `covered` (`siftP`, oracle
  `pick`), the 4-axis split with `tscale`/`sscale` and the "never split `s` at a point or an
  odd cell" rule (`sWidth`, ties `x, y, t, s` = Python's stable sort), `4^k` root grid,
  loader gates incl. the census-window canary C3 (`windowOK`).
* [T] `ParamBridge.lean`: `checkParamI_price` = (P2) at EVERY REAL side of the window;
  `checkParamI_kill` = the per-side `hcert` of Lemma B for the whole window from one PASS
  (soundness.md P3 [S] verbatim); `checkParamI_kill_packing` = the λ-dilated form.
* [F] **The point→interval widenings are TRANSLATIONS, not new interval arguments.**
  `core_exempt_frac_iv(kx0,kx1,ky0,ky1, box)` is literally A70's `coreExempt` for the
  centre-`0` core on the box shifted by the centre interval (`dxlo = x0 − kx1`, …), so its
  soundness is `coreExempt_sound` (A70, incl. the SAT/Hahn–Banach content) applied to the
  translated square + translation invariance of `PSq.set` and `coreSet`
  (`mem_set_translate`, `coreSetP_iff`).  `atom_inside_int_iv` is `projI` with the point
  bounds weakened to interval bounds (`projIV_sound` = A64's proof with two more
  `mul_le_mul` facts).  The prose "each is the A53 one with a POINT replaced by an INTERVAL,
  so the enclosure can only grow" is exactly right and now machine-checked.
* [F] **The window quantifier is over the REALS, with no density argument.**  Because atoms
  and cores are affine in `s`, `μ_s` and `K_j(s)` are defined at every real side, and the
  cell lemmas (`affine_between`: an affine function stays between its endpoint values) hold
  for real `s`.  The C.WIN note's "dense rationals instantiate `stratum_kill` at every `m`"
  is therefore unnecessary: `checkParamI_kill` is stated at every real `s ∈ [s_lo, s_hi]`.
* [F] The exact cell endpoints over the lcm denominator denote the real endpoints
  (`numOver_cast`): `r.num · (pd / r.den) / pd = r` when `r.den ∣ pd` — the one place
  where Python's `SCell` integer packaging needs a lemma.
* [T] `priced_dichotomy_gen`: A68/A70's pigeonhole for an ABSTRACT mass functional
  (`mass ∅ = 0` + sub-additivity over disjoint families); the `IAtom` version is one
  instance, the s-dependent `massP` another.  Reusable for any future measure shape.
* [T] Pilot: `check_k5_06_param` (`native_decide`, 215 s, oracle `pickAll` =
  `--no-float-prepass`) → `k5_06_param_kill` (every real side of `[191/50, 969271/250000]`)
  and `k5_06_param_kill_packing`.
* [F/M] **The float shortlist is decision-neutral on the pilot, box for box.**  Python
  `--no-float-prepass --jobs 1` (`logs/k5_06_param_nofloat.log`, report
  `logs/k5_06.param.nofloat.report.json`): PASS, 293 854 boxes / 110 453 covered / 36 506
  exempt / 26 163 s-splits — IDENTICAL to the campaign run with the shortlist and 3 jobs
  (report `k5_06.param.report.json`; only the `s_cells` statistic differs, 161 vs 421, the
  latter being the worker-summed upper bound).  1 949 123 exact atom checks, 11.2 s.  The
  Lean `pickAll` evaluation is that tree.
* [F] Faithfulness deviations recorded (all decision-neutral): float shortlist + float core
  pre-filter → oracle / omitted (more exemptions can only be granted, the exact test
  decides); `tscale`/`sscale` integers; `S_DEN = 250000` a certificate field; `windowOK` is
  a loader gate NOT used by the soundness proof — the theorem is about the DECLARED cores,
  and the census-window relevance (P0: cores at the class's slots) is consumer-side;
  `nofams` rejected by the loader and absent.
* [C] **Corpus-wide replay** is a separately-priced wave: 52 (+A61) parametric PASS files at
  ~200 s each on the desktop ≈ 3 h serial (`lean/gen_param_lean.py` per file at the
  report's depth; `--slo/--shi` for sub-window rows).  Nothing else changes.

## T2 — B.SEL / C.CC2: selection and the teleport lemma

* [T] `exists_kmax` (any ℕ-score ≤ 11 over the packings at side `m` is maximised — pure
  `Nat.sSup_mem`), `teleport_packing` (replacing a square by the axis-aligned unit square
  on a slot box inside the container whose interior misses every OTHER square's interior
  gives a packing at the SAME side — CC-2's "P′ is a minimiser in the same frame"),
  `cc2_stuck` / `cc2_two_meeters` (CC-2 / CC-2′: at a k-maximal packing every completable
  box is interior-met by a square other than any given non-simple one; with two non-simple
  candidates: a third meeter or both of them).
* [F] **H1 degenerate-case audit, resolved by the statement's shape.**  The L6 slide
  formulation needs corridors and has the flagged cases (contact mid-slide, ties,
  σ-changing slides, simple-in-one-normalisation-only).  In the teleport formulation
  (A58 Rem. (a), `unique_transfer.md` §2) NONE appears in the Lean statement:
  `teleport_packing` has no corridor hypothesis; the side is pinned (`CfgPacking m`); ties
  need no canonical choice; double completion only strengthens `hinc`; the frame is
  `[0,m]²` (D4 handled by the census, E.2).  The audit's outcome: B.SEL's CAVEAT is void
  once B.SEL is read through CC-2 — which is how `unique_transfer.md` already reads it.
* [C → named] The single residue is the census interface `hinc`: "`k(teleport z i c) > k z`
  when `i` is non-simple, the slot is completable and its box is free of the others" — the
  Young-census facts (monotonicity of simplicity in the occupied-slot pattern;
  completability adds a cell).  Same F11/H2 debt as `hface`; discharged the day `Simp` is a
  Lean definition.  B.SEL and C.CC2 therefore stay proved-prose on the depgraph with the
  Lean pointer (statement formal, geometry formal, census interface named).
* [C] B.EXACT: A68's `monotone_to_exact` stands; E.2's D4 bookkeeping (the container
  symmetry acting on slots and on configurations) is still prose.  Not attempted this
  wave; it is the natural companion of the census definition and should land with it.

## T3 — D.N1, C.T5T11, C.M1

* [T] D.N1 (`Zones.lean`): `uv_sq_add` (`u² + v²` = squared distance to the centre),
  `mem_set_of_sqdist_le` / `mem_interior_of_sqdist_lt` (inscribed closed/open disk of
  radius 1/2), `centre_separation` (N1.0: interior-disjoint ⟹ `sqdist ≥ 1`, midpoint
  argument), `at_most_one_centre` (N1.0.1), `zone_assign_injective` / `_unique` /
  `_bijective` (N1 (i)–(iii)).  The diameter hypothesis is stated as `sqdist < 1` on the
  footprint; A42's exact instance checks (footprint diameters, pairwise disjointness) are
  the certificate side of the node and remain what they were.
* [F] N1's "at most one" needs only `mem_interior_iff_uv` (A68) — the interior of a
  parametrised square is the open `u/v` box — plus one polynomial identity; no metric
  geometry of squares beyond A68's coordinate characterisation.
* [T] C.T5T11: `core_meet_same_square` (T5: cores inside the interiors of two members that
  meet ⟹ same member; hence a child whose core meets a pin's core has no witness distinct
  from the pins) and `refine_cover` (T11: a closed cover refines the same existential with
  the same witness — same budget, no new branch).
* [F] **T5's mathematical content is two lines; its risk is entirely procedural.**  The
  "parent" case (a pin placement inside the child box) is precisely the situation where
  the identification witness = pin is CONSISTENT, i.e. where certifying at budget
  `11 − k − 1` would prove a false statement.  No lemma can replace `pinguard.classify`; the
  node's soundness rests on the gate being applied to every certified child (a code
  invariant, as the depgraph note already says).  Lean makes the split explicit: rule
  (theorem) vs gate (procedure).
* [T] C.M1: `strictFamily_mono` (identity embedding `[0,s]² ⊆ [0,s₀]²`), `M1_transfer`
  (an s₀ case certificate with s-INDEPENDENT cores kills at every `s ≤ s₀`) and
  `M1_transfer_packing` (λ-dilated form).  The "single corner" hypothesis is exactly "the
  `coreSet`s are the same at every side" (β = 0 slots); for β ≠ 0 cores the statement does
  not apply — matching soundness.md's applicability clause (≤ 2+2 D4 classes).

## Engineering notes (delta over the A64/A68/A70 recipes)

* [E] A `let ws := if … then -1 else …` INSIDE a checker def defeats `split at`: the
  tactic splits the inner `ite` first and the outer decision `if`s survive with `decide (… ≥
  -1)` baked in.  Naming the subcomputation (`sWidth`) fixed it — a second failure mode for
  A70's rule "name every checker subcomputation as a top-level def".
* [E] `rcases … with ⟨i, -, hex⟩` where `hex : (fun _ => False) (Q i)` does NOT auto-close
  the goal (the `False` is β-unreduced); `exact hex` afterwards.
* [E] `subst` on `c.n = 11` needs `rcases c with ⟨…⟩` first (projections are not variables);
  after that, `lemma_B`'s `Fin 11` unifies with the literal structure's `.n` by defeq.
* [E] Grid coverage over ℝ with integer cells: take `⌊(x − lo)/step⌋`, clamp with
  `Int.toNat_of_nonneg` + `omega`, and obtain `m = m' + 1` before touching `m − 1` (avoids
  every `Nat.cast_sub` side condition).
* [E] `push_cast` leaves `numOver`-style opaque `Int` defs alone; convert the exact-division
  identity with `div_eq_iff` rather than `div_le_iff₀`.
* [E] `Nat.pos_pow_of_pos` is gone: `Nat.two_pow_pos`.  Doc-comments must FOLLOW
  `set_option … in`.  `Set.mem_setOf_eq` is deprecated for `Set.mem_ofPred_eq`.
* [E] Pilot cost: `native_decide` on a full-window parametric certificate (10 atoms, 5
  cores, depth 56, 293 854 boxes) is ~215 s (Python exact-only: 11 s) — the `Rat`
  core-exemption test per box dominates (five `coreExempt` evaluations with denominators
  ~3e13); the corpus replay estimate above uses this figure.
