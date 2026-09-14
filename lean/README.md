# lean/ — START HERE (A216, 2026-09-14)

1. **The theorem, readable:** `PackingCertMathlib/PackingCertMathlib/Main.lean` — `main_lower_bound`,
   `main_value`, `main_uniqueness` (= `s(11) = ŝ`, Trump unique), a plain-language docstring, and
   "What you must believe": the three remaining named axioms with prose/certificate pointers.
2. **One small file per key result:** `PackingCertMathlib/PackingCertMathlib/Statements/` (statement,
   docstring, proof IMPORTED, `#print axioms`); the obligations still in prose or certificates are
   named axioms in `Statements/Open/` (each file a `-- OPEN:` banner + pointer).
3. **The audit:** `lean/AUDIT.md` — every statement with the axioms it depends on and its sorry count;
   regenerate with `python lean/audit.py` (builds `PackingCertMathlib.Main` + `.Statements`, runs
   `scratch/Audit.lean`).  Trusted base = `propext, Classical.choice, Quot.sound` + `native_decide`.

# lean/ — Lean 4 certificates for the square-packing lab

Two projects:

* **`lean/PackingCert`** (Lean 4.33.0, **no Mathlib**) — decidable `Bool` checkers + certificate
  data. Fast, self-contained, kernel-checkable.
* **`lean/PackingCertMathlib`** (Lean 4.34.0-rc1 + Mathlib) — the **bridge lemmas over ℝ²**, i.e.
  the statements that give the `Bool` theorems their geometric meaning (A28). Build artefacts are
  **not** committed and were deleted after A28 for disk (see "Mathlib project" below).

## The formal top-level STATEMENT (A62, checklist F3)

`PackingCertMathlib/TopLevel.lean` defines packings over ℝ² (closed unit squares, pairwise
disjoint **interiors**, container `[0,s]²`, tan-half configuration layer — the set-level and
configuration definitions live in `Parametrize.lean` since A64, same namespace), `s(11)` as
an infimum, and **states** the composed optimality theorem `s(11) = ŝ` + uniqueness with
every leaf family of the live proof plan as a NAMED `axiom` (12 after A68:
UB-at-ŝ ×3 — configuration, certified intrinsic-side feasibility, and the OPEN identity
`shatA22_eq_shat` —, stratification, per-stratum kills with the window fused in, trump5
residual, A22/A36 basin, uniqueness transfer, plus the opaque census layer ×3). The three
theorems `s_eleven_ge / s_eleven_eq / s_eleven_unique` are proved from exactly those axioms
(`scratch/Axioms.lean` prints them; CI asserts no `sorryAx`).
**Discharged by A63 (2026-09-01): `shat` is now a definition and `shat_spec` a THEOREM
(root isolation — certificate `certs/octic_root_isolation.json`, checker
`certs/verify_sturm.py`, all-positive Taylor shift inside Lean; depends only on
`propext, Classical.choice, Quot.sound`), and `rBasin` is a definition (`3/2000`,
`docs/proofs/theta_t_transfer.md`).**
**Discharged by A64 (2026-09-02):**
* **`parametrize` is a THEOREM** (`Parametrize.lean`; prose
  `docs/proofs/parametrization.md`): every closed unit square is `PSq.set (cx, cy, t)`
  with `t = tan(θ/2) ∈ [0,1]` — the square's own 90° symmetry + the half-angle
  substitution, all polynomial algebra; axioms `propext, Classical.choice, Quot.sound`.
* **`lb_382` is a THEOREM — `s(11) ≥ 3.82` end to end** (`MeasureBridge.lean` +
  `Measure382.lean`): the measure-checker soundness bridge (A28 §7 item 4, the
  "3–5 day item") is fully formalised — exact `Int`-interval arithmetic, rational grid
  trigonometry, clip (via quasiconcavity of `w = cos + sin`), sift/split/branch-and-bound
  induction, coverage, and the scaling/shrinking + counting argument — and composed with
  the `native_decide` evaluation of `checkMeasureI` on the 3.82 certificate
  (`s_eleven_ge_382`; axioms `propext, Classical.choice, Quot.sound` + the `native_decide` axiom).
* **`trump_packs_at_shat` is a theorem** from the A64 split of the UB-at-ŝ obligation:
  `shatA22` (intrinsic side) + `trump_packs_at_shatA22` (A22 feasibility, certified
  modulo the Python-interval TCB) + `shatA22_eq_shat` (THE open algebraic identity —
  closure specs incl. the new ideal-membership route (c-idl) in
  `docs/proofs/attainment_ub.md` §6).
**Discharged by A68 (2026-09-01):**
* **`attained` is a THEOREM** (`Attain.lean`; drain lemma D1, depgraph A.D1): `{s | Fits 11 s}`
  has a least element — compactness of the coordinate feasible region (33 coordinates + the
  side in `[0,11]`; non-overlap closed via the exact interior formula `mem_interior_iff_uv`:
  interior of a parametrised square = the OPEN `u/v` box) + continuity of the side
  projection; no Hausdorff limits. Axioms `propext, Classical.choice, Quot.sound`.
  TopLevel roster 13 → 12.
* **The λ-dilation bridge (Lemma B, A.SBRIDGE) is Lean** (`Dilation.lean`): `scaleC_disjoint`
  (B.0(a)), `slot_tracking` (B.0(c)), `dilation_bridge` (interior-disjoint packing ⟹ strict
  closed-disjoint family at `λm`), `lemma_B`, the pricing pigeonhole `priced_dichotomy` /
  `hcert_of_priced` ((P1)+(P2) ⟹ the bridged claim; `Exempt`-aware, so Lemma B-NO is the
  same theorem), `bprime_containment` ((H′) ⟹ (H)) and `pullback_mem_Icc` (B.2″ widening).
* **The case-LP verifier soundness (V.CASE) is Lean** (A70; `CaseChecker.lean` +
  `CaseSat.lean` + `CaseHyp.lean` + `CaseBridge.lean`): `checkCaseI` (the
  `verify_case.py` decision core: cores / NO-families / budget over the A64 measure
  layer) with the full soundness chain — `sat_squares` (SAT sufficiency for two
  squares: geometric Hahn–Banach + 4-cone support bound), exemption-test soundness,
  `checkCaseI_price` (= claim (P2) of the frozen spec, scaled by `wd`), and
  `checkCaseI_kill` / `checkCaseI_no_family` (Lemma B's `hcert` / the B-NO form,
  produced per PASS file — A68's named residue discharged).  One certificate is
  replayed end to end (`CaseData506.lean` + `CaseK506.lean`: the k5_06 pin-set kill
  at `s = 191/50`, `native_decide`, seconds).
* **K1(i) is Lean** (`Skeleton.lean`, depgraph B.K1): slot model + `ContainsPins` +
  `containsPins_mono` / `kill_mono`; M→E as `monotone_to_exact`, conditional on the census
  interface hypothesis `hface` (F11/H2 — the census is not yet a Lean definition).
* **The θ↔t transfer is Lean** (`ThetaT.lean`, depgraph E.COORD): `cosT_eq_cos` /
  `sinT_eq_sin` tie the rational parametrisation to `θ(t) = 2·arctan t`; X.1 both directions
  (`|Δt| ≤ |Δθ| ≤ 2|Δt|`); X.2 with the sharp constant `r_c + √2·r_t`; the two rBasin gates
  are TopLevel theorems (`rBasin_gate_tilt`, `rBasin_gate_slab`).
**Discharged by A75 (2026-09-02, Lean wave 5):**
* **The `verify_measure.py` DRIVER is Lean-sound (V.MEAS)** (`MeasurePy.lean` +
  `MeasurePyBridge.lean`): `checkMeasurePy` models `Verifier.run`/`covered`/`root_boxes`/
  `main` — `--tscale`, the `4^k` `--split` root grid, `--strict-margin`, the no-drop
  `known`-inheritance, the float shortlist as an arbitrary ORACLE, the `s < 1` shortcut —
  and `checkMeasurePy_no_packing` proves PASS ⟹ `s(n) ≥ s` for every oracle/tscale/split/
  margin from the A64 primitives.  Residual TCB = the line-by-line model↔source table
  (`MeasurePy.lean` header, `attempts/A75-lean-wave5/notes/findings.md`).
* **The `verify_param.py` window checker is Lean-sound (V.PARAM)** (`ParamChecker.lean` +
  `ParamBridge.lean`): the 4-D `(t, cx, cy, s)` branch-and-bound with the point→interval
  widenings (`atom_inside_int_iv`, `core_exempt_frac_iv` = A70's `coreExempt` on a
  centre-shifted box), `checkParamI_price` (claim (P2) at EVERY REAL side of the window),
  `checkParamI_kill` (the per-side Lemma B `hcert` for the whole window from one PASS —
  the form `stratum_kill` consumes) and `checkParamI_kill_packing` (λ-dilated).  Pilot
  replay `ParamData506.lean` + `ParamK506.lean` (`lean/gen_param_lean.py`): `k5_06.param`
  over `[191/50, 969271/250000]` at depth 56, `native_decide` 215 s.  C.WIN carries the
  gold verifier accent.
* **D.N1, C.M1, C.T5T11 are Lean** (`Zones.lean`): centre separation / at-most-one / zone
  assignment injective-unique-bijective; single-corner window transfer `M1_transfer`; the
  T5 contradictory-box rule `core_meet_same_square` and the T11 refinement `refine_cover`
  (the pinguard "parent" gate stays a code invariant).
* **B.SEL / C.CC2 Lean partial** (`Selection.lean`): `exists_kmax` (k-maximal selection),
  `teleport_packing` (the CC-2 exchange preserves the packing at the same side — no
  corridor), `cc2_stuck` / `cc2_two_meeters` conditional on the census interface `hinc`
  (F11/H2, the same debt as `hface`); the H1 degenerate cases are absent in the teleport
  form by the shape of the statement.
**Discharged by A78 (2026-09-02, Lean wave 6) — roster 12 → 7 named axioms:**
* **The Young-form census is a Lean DEFINITION (F11/H2)** (`Census.lean`; counts and A72
  cross-check `CensusCheck.lean`, corpus literal `CensusCorpus.lean`): `skeleton s z`,
  `censusL` (1110), `classCodes` (163), the D4 action; L3 exhaustiveness is the theorem
  `skeleton_mem_census` at every side `s ∈ (3,4)`; `StratumIdx` / `trumpStratum` /
  `InStratum` are definitions.  `hface` (`containsPins_skeleton`) and Lemma M→E
  (`class_kill`) are theorems; `skeleton_d4` is the D4 equivariance.
* **`stratify` and `unique_transfer` are THEOREMS** (census exhaustiveness); the honest
  chain + Theorem U route is `unique_via_chain` / `s_eleven_unique_of_chain`
  (`UniqueChain.lean`, H10-stuck and Theorem U as explicit hypotheses).
* **`hinc` discharged** (`CensusSelection.lean`: `card_lt_teleport`; `cc2_stuck_census`,
  `exists_kmax_skeleton` unconditional).
* **`shatA22_eq_shat` is a THEOREM** (CIDL-LEAN: `Cidl*.lean` replay
  `certs/cidl_identity.json` by `native_decide`, generators rebuilt from A22's conventions,
  sign gates `e, Δ < 0` on `[3/10, 2/5]`); the new interface axiom `a22_exact_structure`
  carries only A22's certified content.
* **The D4 reduction (D.D4) is the theorem `d4_wlog`** (`D4Wlog.lean`).
* **`alivewitness` has a Lean checker + soundness theorem** (`AliveChecker.lean`,
  `AliveBridge.lean`: PASS ⟹ no case-LP certificate of that budget passes `checkCaseI`).
* **Fixed corpora replayed** (`PackingCertMathlib/Corpus/`, separate lake target
  `PackingCertCorpus`, generator `lean/gen_corpus_lean.py`): C.K61 (61), D.TRAP (6 ⊂ K61),
  D.P1 (1), A.THMU (11) — one `native_decide` theorem per certificate; timings in
  `attempts/A78-lean-wave6/results/t5_timings.jsonl`.
**Discharged by A79 (2026-09-02, rigidity replay rungs (b)/(c)):**
* **`zhat` / `shatA22` are DEFINITIONS and `trump_packs_at_shatA22` / `basin` are THEOREMS**
  (`Rigidity.lean`): A22's Krawczyk certificate and A36's basin certificates are replayed
  in Lean by the θ-frame port of A70's exact re-checkers (`RigidKernel.lean`: dyadic
  `2^-330` intervals, alternating-Taylor cos/sin brackets certified from Mathlib's
  `Real.hasSum_cos/sin`, a deep-embedded row language with symbolic differentiation and
  order-2 interval jets), `native_decide` in the isolated `RigidityCheck.lean`
  (`checkA22_a22`, `checkA36_universal`, `checkA36_all17`; module 140 s).  Soundness:
  `krawczyk_sound` (Banach on the true box, `Y` invertible by Neumann) ⟹ the unique contact
  solution ẑ; `zhatV_feas` (interval SAT + exact-structure witnesses searched in `S`) ⟹ ẑ is
  a packing at its own side; `a22_optimal` (A22 §5, Farkas + MVT on the box); `a36_basin`
  (the universal certificate's (V′) chain: second-order Taylor with the interval Hessian
  mass, max-form pinning, quadratic dichotomy in place of the 800-step iteration, handover to
  A22).  The composition needs only `G3_UNIVERSAL` (slab gate `rBasin(1+√2) < 3689/10⁶`);
  the 16 variant certificates are replayed but not load-bearing.  mpmath.iv (E.IV) is out of
  the rigidity chain at both tiers.  TopLevel roster: 3 named axioms
  (`stratum_kill`, `trump_residual`, `a22_exact_structure`).
**Built by A86 (2026-09-03, Lean wave 7 — the last theorems the compute nodes need):**
* **The contraction-tube checker is Lean-sound (A83's obligation, T1)**: `RigidTubeKernel.lean`
  (`checkTube`, the port of `certs/verify_tube.py`: hull box + PAIR-RELATIVE boxes for the
  edge/dist rows, the split Taylor remainder `E(x)`, the monotone iteration `iterT`) and
  `RigidTube.lean` (`tube_basin`: `checkA22 = true`, `checkTube = true` ⟹ every feasible
  point of `Tube_v(T, r) = {ẑ − t·v + w}` has `s ≥ ŝ`, equality only at `ẑ`).  The one new
  analytic ingredient is translation invariance of the pair rows AND their symbolic
  derivatives (`shift_inv_D`: an invariant expression has invariant derivatives because
  `D` is the derivative along the coordinate segment, `hasDerivAt_eval`, and derivatives
  are unique).  `TubeSeam.lean`: the `t`-frame form `tube_tframe` and Lemma SEAM's
  per-coordinate map `seam_inTube` (pins `w = 0` up to the slot residual, free squares
  `|w| ≤ r_land·(m/s0) + T·|v − ẑ/ŝ|`).  Data `RigidTubeData.lean` (54 certificates,
  `lean/gen_tube_lean.py`), isolated `RigidTubeCheck.lean` (3 load-bearing directions),
  per-certificate replays `Corpus/Tube/` (target `PackingCertCorpus`).
* **The atlas-value box checker (T2)**: `AtlasKernel.lean` (`checkAtlas`, trivial-reach /
  extent form in `(cx, cy, t)`: witness corner pairs, rational `cosT`/`sinT` enclosures) +
  `AtlasBridge.lean` (`atlas_kill`: `L ≤` every container side; `atlas_dilated_kill_fold` =
  Lemma K0-ATLAS, the (D′) leaf: with `L ≥ s0` no packing at ANY side `< s0` has its dilate
  in the box — every window side at once, no dilation bookkeeping).  Boxes are emitted with
  the tilts folded into `[0, π/4]` (`foldSq`, corner-coordinate sets invariant); 48 of 49
  A37/A85 boxes reach `L ≥ s0` at about half of A37's radius (`AtlasData.lean`, isolated
  `AtlasCheck.lean`, `attempts/A86-lean-wave7/notes/t2_atlas.md`).
* **The zone-tree composition theorem (T3)**: `ZoneTree.lean` — `ClosedTree s0 tc Root`
  (leaves (K)/(N) `checkCaseI` with node cores + NO-zones, (C), (D) landing, (D′) atlas;
  `cover` = the tree's complete disjunction, the producer's obligation) and `tree_kill`
  (Lemma P-TREE (a)+(b) / Lemma SEAM: every packing at `m ∈ [ŝ − T, ŝ]` whose dilate
  satisfies the root has `m ≥ ŝ`, and at `ŝ` is a `D4`-image of `ẑ`); Step 1
  `root_of_containsPins` (slack pin cores inside the dilated pins under the drift budget);
  the rule library `zone_dichotomy`, `grid_cover` (CI-1), `slot_outside_zone` (CI-3),
  `pd_convex`/`pd_rule` (Lemma PD), `d4_dil_comm` (D.S6's mod-`G` clause).
  `Composition.lean`: `ClassKilledAt`, `s_eleven_ge_of_classes` / `s_eleven_unique_of_classes`
  (the consumers from the per-class obligation alone — `stratum_kill`, `trump_residual`
  and `basin` are not consumed on this route), `classKilledAt_of_tree`,
  `classKilledAt_of_slabs`, and the `stratum_kill` re-split (`s_eleven_ge_of_split`).
* **Window composition for the scoreboard rows (T4)**: `WindowRows.lean` — `SlabKill` with
  the three constructors `slabKill_of_param` (V.PARAM row ⟹ its whole window),
  `slabKill_of_case` (slack-core grid, `(s″/lo − 1)·A < ρ`), `slabKill_of_M1`;
  `windowKilled_of_slab` (⟹ the `stratum_kill` instance via `class_kill`); `k5_06_slab`
  instantiated on the replayed pilot (margin `ρ = 10⁻⁹`, cores at slots, `norm_num`).
  Axioms: all new soundness theorems `propext, Classical.choice, Quot.sound` (+ the
  `checkA22` evaluation where `ẑ` is consumed); see `attempts/A86-lean-wave7/notes/findings.md`.
**Built by A93 (2026-09-04, Lean wave 8 — the k0 chain of `docs/proofs/k0_blocked_side.md`):**
* **Lemma CW / B-YES / Theorem S(δ) are Lean** (`Crowd.lean`): `cframe`/`cornerBox`/`muC`
  (A90's `μ_c`, attained, `meets_cornerBox_iff_muC_le`), `scaleC_meets_cornerBox` (B-YES with
  the pad `(λ−1)·r`, `r ≥ wT/2`), `not_meets_two_corners`, `crowd_sound` (the weight
  arithmetic of two `checkCaseI` PASSes on one measure), `crowd_cert_kill` (window form);
  the two file-level clauses are DECIDABLE: `sameMeasure` (one measure) and, in
  `CrowdZone.lean`, `crowdZones` (run B's NO-families avoid the crowd family at every corner;
  separating-axis tests + bisection) with `crowdZones_sound`; `crowdKill_of_files` packages
  4 Bool facts + rational side conditions into `CrowdKill δ m_lo s0`.  **Lemma CW-S**
  (A94's incidence form: `1 + r_max` runs, pin cores, budget `11 + 2 m_u e`) is
  `crowd_sound_incidence`.  Replay generator `lean/gen_crowd_lean.py` (isolated
  `Corpus/Crowd/Check_<tag>.lean`); no crowd certificate exists yet (A92 chore parked).
* **Lemma SLIDE and K0-FREE are Lean** (`Slide.lean`): `slide_crowd` — under K0-O1
  (`Composition.K0O1`, k1_00's monotone slab kill on `[3.82, ŝ)`) EVERY packing at side `m < ŝ`
  has two distinct squares at depth `≥ ŝ − m` at every corner; proved by translating the whole
  packing away from the corner (no clusters, no Lemma CLUSTER — see the A93 findings);
  `k0free_kill` = `teleport_packing` + K0-O1.  `PinnedSlide.lean` (A94's slot version):
  Lemma SWEEP (`sweep_core`, `sweep_packing`) and the cluster-free Lemma MOVE
  `pinnedShift_packing` (pin blocks translate with their anchoring walls, non-pins away from
  the corner: a packing containing the same pins at side `m + τ` for every `τ ≥ 0`).
* **Theorem CEIL is Lean** (`Ceil.lean`): `ceil` / `ceil_packing` — `max(μ_BL A, μ_BL B) ≥ 1/√2`
  for interior-disjoint unit squares in `[0,s]²`; `exists_sep_line` (Hahn–Banach), the Wedge
  Lemma `wedge_x`/`wedge_y` with its concavity step as the factorisation `wedge_core`.
* **Theorem N is Lean** (`Composition.lean`): `slabKill_of_tree` (K0-O1's consumer),
  `theoremN_slab`, `chain_cover`, `no_packing_of_chain`, **`s_eleven_ge_of_chain`**
  (`s(11) ≥ ŝ − δ_K` from K0-O1 + a chain of crowd certificates — class-blind),
  `classKilledAt_below_of_chain`, the named residue `ShellKill i δ` (RES-N), and
  `classKilledAt_of_chain` (the k0_00 instance of `stratum_kill` — and every class's — on
  the whole window).  Roster note in `TopLevel.lean`.  Axioms: all `propext,
  Classical.choice, Quot.sound` (`scratch/AxiomsA93.lean`).
Each axiom's docstring records the lab artefact meant to discharge it and its status; the
ambiguities the file forced are `attempts/A62-trust-ledger/notes/findings.md`, updated by
`attempts/A63-hole-closure/notes/findings.md` (bridge lemmas now in `docs/proofs/`).

## Theorem index (real-geometry statements — A28)

| theorem | file | statement | axioms |
|---|---|---|---|
| `PackingCert.eleven_unit_squares_in_3877084` | `PackingCertMathlib/Trump11.lean` | **∃ 11 pairwise-`Disjoint` closed unit squares ⊆ `[0, 969271/250000]²` in ℝ²** ⇒ `s(11) ≤ 3.877084` | `propext, Classical.choice, Quot.sound` (**no `native_decide`** — kernel `decide` on the certificate) |
| `PackingCert.checkPackingCCW_sound` | `PackingCertMathlib/Bridge.lean` | the bridge: `checkPackingCCW c = true` ⇒ unit squares, contained, pairwise disjoint | `propext, Classical.choice, Quot.sound` |
| `PackingCert.disjoint_of_strictlyBelow` | `PackingCertMathlib/Bridge.lean` | separating axis with positive margin ⇒ two closed squares are `Disjoint` (any axis `n`) | `propext, Classical.choice, Quot.sound` |
| `PackingCert.aff_sqdist` | `PackingCertMathlib/Bridge.lean` | the parametrisation `(a,b) ↦ p₀ + a·e + b·e⊥` is a Euclidean isometry ⇒ `sqSet p₀ e` is a congruent copy of `[0,1]²` | `propext, Classical.choice, Quot.sound` |
| `PackingCert.two_unit_squares_side_ge` | `PackingCertMathlib/Band.lean` | two unit squares in `[lo,lo+B]²` admitting a separating direction ⇒ `B ≥ 1 + √2/2` | `propext, Classical.choice, Quot.sound` |
| `PackingCert.band_96_25` | `PackingCertMathlib/Band.lean` | at `s = 96/25`: at most one square avoids the width-`27/25` boundary band (⇒ ≥ 10 of 11 meet it) | `propext, Classical.choice, Quot.sound` |
| `PackingCert.trump11_ccw_ok_kernel` | `PackingCertMathlib/Trump11.lean` | `checkPackingCCW Data.trump11 = true`, kernel `decide` | **none** |
| `PackingCert.S11.parametrize` | `PackingCertMathlib/Parametrize.lean` | **every packing is a configuration** `(cxᵢ, cyᵢ, tᵢ)`, `t ∈ [0,1]` (A.PARAM; was the `parametrize` axiom) | `propext, Classical.choice, Quot.sound` |
| `PackingCert.S11.checkMeasureI_no_packing` | `PackingCertMathlib/MeasureBridge.lean` | **the measure bridge (A.F2)**: `checkMeasureI c = true` ⇒ `s(c.n) ≥ c.sNum/c.sDen` over ℝ² | `propext, Classical.choice, Quot.sound` |
| `PackingCert.S11.s_eleven_ge_382` | `PackingCertMathlib/Measure382.lean` | **`s(11) ≥ 3.82` end to end**: `∀ s, Fits 11 s → 191/50 ≤ s` | + the `native_decide` axiom (`check_3_82._native.native_decide.ax_1_1`; ≈ 40 min build) |
| `PackingCert.S11.attained` | `PackingCertMathlib/Attain.lean` (+ `TopLevel.lean`) | **attainment (A.D1)**: `{s | Fits 11 s}` has a least element (drain lemma D1; was the `attained` axiom) | `propext, Classical.choice, Quot.sound` |
| `PackingCert.S11.mem_interior_iff_uv` | `PackingCertMathlib/Attain.lean` | the interior of a parametrised square is exactly the open `u/v` box | `propext, Classical.choice, Quot.sound` |
| `PackingCert.S11.dilation_bridge`, `lemma_B`, `priced_dichotomy` | `PackingCertMathlib/Dilation.lean` | **the λ-dilation bridge (A.SBRIDGE)**: interior-disjoint packing ⟹ closed-disjoint family at `λm`; Lemma B / B-NO from the frozen (P1)+(P2) claims; B′ margin condition (H′) ⟹ (H) | `propext, Classical.choice, Quot.sound` |
| `PackingCert.S11.sat_squares` | `PackingCertMathlib/CaseSat.lean` | **SAT sufficiency for two squares**: four-axis projection overlap ⇒ the squares intersect (the `core_exempt_frac` geometry) | `propext, Classical.choice, Quot.sound` |
| `PackingCert.S11.checkCaseI_kill`, `checkCaseI_no_family` | `PackingCertMathlib/CaseBridge.lean` | **the case-LP bridge (V.CASE)**: `checkCaseI c = true` ⇒ no strict family at the certified side realises the pin hypotheses (B-NO: some non-owner is NO-exempt) | `propext, Classical.choice, Quot.sound` |
| `PackingCert.S11.k5_06_lo_kill` (+`_packing`) | `PackingCertMathlib/CaseK506.lean` | **one case certificate end to end**: the k5_06 pin-set kill at `s = 191/50` (strict-family and λ-dilated packing forms) | + the `native_decide` axiom (`check_k5_06_lo._native.native_decide.ax_1_1`; seconds) |
| `PackingCert.S11.containsPins_mono`, `kill_mono`, `monotone_to_exact` | `PackingCertMathlib/Skeleton.lean` | **K1(i) (B.K1)**: kills climb the pin-set containment order; M→E conditional on the census interface `hface` | `propext, Classical.choice, Quot.sound` |
| `PackingCert.S11.checkMeasurePy_no_packing` | `PackingCertMathlib/MeasurePyBridge.lean` | **`verify_measure.py` driver soundness (V.MEAS)**: `checkMeasurePy c need ts k pick = true` ⇒ `s(c.n) ≥ c.sNum/c.sDen`, for every shortlist oracle, tscale, root split, margin | `propext, Classical.choice, Quot.sound` |
| `PackingCert.S11.checkParamI_price`, `checkParamI_kill`, `checkParamI_kill_packing` | `PackingCertMathlib/ParamBridge.lean` | **the parametric (window) bridge (V.PARAM)**: `checkParamI c ts ss k pick = true` ⇒ at every real `s ∈ [s_lo, s_hi]` no strict family realises the pin hypotheses (cores `K_j(s)`); λ-dilated packing form | `propext, Classical.choice, Quot.sound` |
| `PackingCert.S11.k5_06_param_kill` (+`_packing`) | `PackingCertMathlib/ParamK506.lean` | **one window certificate end to end**: the k5_06 pin-set kill at EVERY side of `[191/50, 969271/250000]` | + the `native_decide` axiom (`check_k5_06_param._native.native_decide.ax_1_1`; 215 s) |
| `PackingCert.S11.centre_separation`, `zone_assign_bijective`, `core_meet_same_square`, `M1_transfer` | `PackingCertMathlib/Zones.lean` | **D.N1 / C.T5T11 / C.M1**: centre separation + zone-assignment collapse; the T5/T11 logic rules; single-corner transfer down the window | `propext, Classical.choice, Quot.sound` |
| `PackingCert.S11.exists_kmax`, `teleport_packing`, `cc2_stuck` | `PackingCertMathlib/Selection.lean` | **B.SEL / C.CC2**: k-maximal selection; the CC-2 exchange preserves the packing; teleport-stuckness conditional on the census interface `hinc` | `propext, Classical.choice, Quot.sound` |
| `PackingCert.Rigid.krawczyk_sound` | `PackingCertMathlib/RigidKrawczyk.lean` | **Krawczyk soundness (E.A22)**: `krawczykOK c S Y r = true` ⇒ the 34-row contact system has exactly one zero in `box(z0, r)`, strictly inside | `propext, Classical.choice, Quot.sound` |
| `PackingCert.Rigid.zhatV_feas`, `a22_optimal` | `PackingCertMathlib/RigidA22.lean`, `RigidOptimal.lean` | **A22 feasibility + strict local optimality**: `checkA22 c = true` ⇒ ẑ is a packing at its own side; every feasible small-tilt configuration of `N` with side `≤ s(ẑ)` is ẑ | `propext, Classical.choice, Quot.sound` |
| `PackingCert.Rigid.a36_basin` | `PackingCertMathlib/RigidBasinMain.lean` | **A36 basin (E.A36, universal certificate)**: `checkA36 c a = true` ⇒ every feasible `z` with `‖z − ẑ‖_∞ ≤ h` has `s(z) ≥ s(ẑ)`, equality only at ẑ | `propext, Classical.choice, Quot.sound` |
| `PackingCert.Rigid.zhatCfg_packing`, `basin_tframe` | `PackingCertMathlib/Rigidity.lean` (+ `TopLevel.lean`: `trump_packs_at_shatA22`, `basin`) | **the certificate replays composed, t-frame**: Trump's configuration (DEFINED as the contact solution) packs at `ŝ_A22`; the `InBasin` basin theorem with `ŝ_A22` | + the `native_decide` axioms `checkA22_a22` and `checkA36_universal` (`RigidityCheck.lean`, 140 s for all three replays) |
| `PackingCert.S11.theta_lipschitz`, `sub_le_theta`, `corner_perturb`, `rBasin_gate_*` | `PackingCertMathlib/ThetaT.lean` (+ `TopLevel.lean`) | **θ↔t transfer (E.COORD)**: `|Δt| ≤ |Δθ| ≤ 2|Δt|`; corner motion ≤ `r_c + √2·r_t`; the two rBasin gates | `propext, Classical.choice, Quot.sound` |
| `PackingCert.S11.skeleton_mem_census`, `exists_class_skeleton`, `containsPins_skeleton`, `skeleton_card_le`, `skeleton_d4`, `d4_packing`, `class_kill` | `PackingCertMathlib/Census.lean` | **the Young-form census (B.CENSUS/B.EXACT, F11)**: every packing at `s ∈ (3,4)` has its skeleton in the census; exact ⟹ contains; `k ≤ 11`; D4 equivariance; Lemma M→E | `propext, Classical.choice, Quot.sound` |
| `PackingCert.S11.censusL_length`, `classCodes_length`, `census_eq_corpus`, `census_d4_closed`, `corpus_classes_canon` | `PackingCertMathlib/CensusCheck.lean` | **1110 / 163, D4-closed, = A72's tuple set and orbit partition** | + one `native_decide` axiom each |
| `PackingCert.S11.card_lt_teleport`, `exists_kmax_skeleton`, `cc2_stuck_census` | `PackingCertMathlib/CensusSelection.lean` | **B.SEL / C.CC2 unconditional**: a teleport of a non-simple square onto a completable slot raises `k`; selection; CC-2/CC-2′ | `propext, Classical.choice, Quot.sound` |
| `PackingCert.S11.stratify`, `unique_transfer` | `PackingCertMathlib/TopLevel.lean` | **were axioms**: from census exhaustiveness (`exists_stratum`) | `propext, Classical.choice, Quot.sound` |
| `PackingCert.S11.unique_via_chain`, `s_eleven_unique_of_chain` | `PackingCertMathlib/UniqueChain.lean` | **the uniqueness clause via CC-2 chain + Theorem U** (H10-stuck, Theorem U as hypotheses) | `+ basin, trump_residual, zhat` |
| `PackingCert.S11.d4_cover_zone`, `d4_wlog` | `PackingCertMathlib/D4Wlog.lean` | **the D4 reduction (D.D4)** at every side, conditional on root occupancy | `propext, Classical.choice, Quot.sound` |
| `PackingCert.S11.crowd_sound`, `crowd_cert_kill`, `crowd_sound_incidence`, `crowdKill_of_files` | `PackingCertMathlib/Crowd.lean`, `CrowdZone.lean` | **Lemma CW / CW-S (K0.CW)**: two (resp. `1 + r_max`) `checkCaseI` PASSes on one measure + `sameMeasure` + `crowdZones` ⇒ no packing at any side of `[m_lo, s0)` has two squares at depth `≥ δ` at every corner | `propext, Classical.choice, Quot.sound` |
| `PackingCert.S11.slide_crowd`, `k0free_kill`, `pinnedShift_packing` | `PackingCertMathlib/Slide.lean`, `PinnedSlide.lean` | **Lemma SLIDE / K0-FREE (K0.SLIDE, K0.FREE)** modulo K0-O1 as a hypothesis; Lemma SWEEP + the cluster-free Lemma MOVE | `propext, Classical.choice, Quot.sound` |
| `PackingCert.S11.ceil`, `ceil_packing` | `PackingCertMathlib/Ceil.lean` | **Theorem CEIL (K0.CEIL)**: `max(μ_BL A, μ_BL B) ≥ 1/√2` | `propext, Classical.choice, Quot.sound` |
| `PackingCert.S11.s_eleven_ge_of_chain`, `classKilledAt_of_chain` | `PackingCertMathlib/Composition.lean` | **Theorem N**: K0-O1 + a chain of crowd certificates ⇒ `s(11) ≥ ŝ − δ_K`; + `ShellKill` ⇒ `ClassKilledAt` on the window | `propext, Classical.choice, Quot.sound` |
| `PackingCert.Cidl.cidl_identity`, `octic_zero_of_generators`; `PackingCert.S11.shatA22_eq_shat` | `PackingCertMathlib/Cidl{Check,Bridge}.lean`, `TopLevel.lean` | **CIDL-LEAN**: the (c-idl) identity + sign gates replayed; `ŝ_A22 = ŝ` a theorem from `a22_exact_structure` | + the three CIDL `native_decide` axioms (+ `a22_exact_structure, shatA22, zhat`) |

`Band.lean` proves the A26.1 family with an *arbitrary* separating direction, hence band width
`27/25 = 1.08` rather than A26's `1`; see `attempts/A28-lean-batch/notes.md` §3, which also records
the single unformalised two-vector inequality (A28.★) that would upgrade the constant to the
**sharp** `B ≥ 2` and give A26.1 for every `s < 4`.

## `Bool`-checker theorems (`lean/PackingCert`, no Mathlib)

| what | file | theorem | proof method |
|---|---|---|---|
| **Upper bound** `s(11) ≤ 3.877084` (11 unit squares fit in `[0, 969271/250000]²`) | `PackingCert/Main.lean`, `Kernel.lean` | `PackingCert.trump11_ok : checkPacking Data.trump11 = true` | `native_decide` **and** kernel `decide` (axiom-free) |
| Upper bound `s(11) ≤ 3.877083591023` (tight variant) | same | `PackingCert.trump11_tight_ok` | same |
| **Lower bound `s(11) ≥ 3.80`** — NEW (published bound 3.7889): A07's LP measure certificate `certs/measure_certificate_3.80.json` (1069 atoms, mass 10.801639 < 11) | `PackingCertSlow.lean` (**separate target**: `lake build PackingCertSlow`, 654 s) | `PackingCert.MeasureI.s11_ge_3_80 : checkMeasureI Data.cert_3_80 = true` | `native_decide` (integer checker), 5 837 883 boxes |
| Lower bound `s(11) ≥ 3.741594` (A05's 10-point unavoidable set) | `PackingCert/MeasureIntMain.lean`, `MeasureMain.lean` | `PackingCert.MeasureI.a05_10pt_int_ok : checkMeasureI Data.a05_10pt_int = true` (Int checker, 571k boxes, 9 s) and `PackingCert.Measure.s11_ge_37416 : checkMeasure Data.a05_10pt = true` (Rat checker, 97 s) | `native_decide` |
| Lower bound `s(5) > 2.6` (perturbed Göbel 4-point measure, prototype) | same | `PackingCert.MeasureI.goebel26_int_ok`, `PackingCert.Measure.s5_gt_26`; kernel `decide` also works for the Int version (`scratch/IntKernel.lean`, 30 s, no axioms) | `native_decide` / `decide` |

Both checkers are `Bool`-valued functions; Lean proves *that the checker returns `true` on the
data*.  The bridge lemma connecting `= true` to the geometric statement over ℝ² is **proved** for
the **upper bound** (A28, `lean/PackingCertMathlib`, table at the top of this file) and — since
A64 — **also for the lower-bound (measure) checker**: `PackingCertMathlib/MeasureBridge.lean`
proves the soundness of a byte-identical copy of `checkMeasureI`
(`PackingCertMathlib/MeasureChecker.lean`), so the theorems in this project are end-to-end;
the `lean/PackingCert` theorems below remain evaluation-only (their bridge is the same
statement, proved in the sibling project).

## Toolchain / build

* elan 4.2.3, Lean **4.33.0** (`stable`), Lake 5.0.0 — pinned in `PackingCert/lean-toolchain`.
* Install elan (Windows): `elan-init.exe` from https://github.com/leanprover/elan/releases, then
  `elan default stable`. Put `%USERPROFILE%\.elan\bin` on PATH.
* Build:
  ```
  cd lean/PackingCert
  lake build                    # default target: ≈ 80 s clean (UB theorems 5 s; A05 measure theorems 71 s + 13 s; C/dynlib compilation)
  lake build PackingCertSlow    # the s(11) ≥ 3.80 theorem: 654 s ≈ 11 min (5 837 883 boxes)  [25 min without precompileModules]
  lake build measure_bench && .lake/build/bin/measure_bench int_3_80 48   # native timing / box count (≈ 9 min)
  ```
* Axioms (`lake env lean scratch/Axioms.lean`, `scratch/IntKernel.lean`):
  `trump11_ok_kernel`, `trump11_tight_ok_kernel`, `goebel26_int_kernel` → **no axioms**;
  `trump11_ok`, `a05_10pt_int_ok`, `s11_ge_3_80` → the `native_decide` axiom only (`Lean.ofReduceBool`);
  the `Rat` checker theorems (`s11_ge_37416`, `s5_gt_26`) additionally carry `propext, Classical.choice, Quot.sound` (from `Rat`'s definitions).

## Project layout (`lean/PackingCert/`)

```
PackingCert/Geometry.lean      Pt (Int×Int), add/sub/dot/perp, Square (4 corners), edges
PackingCert/Checker.lean       Cert, checkPacking : Cert → Bool                       (upper bound)
PackingCert/Example.lean       hand-made 4-square example (+ 3 negative tests)      decide/native_decide
PackingCert/Data.lean          GENERATED from certs/trump11_certificate_int.json
PackingCert/DataTight.lean     GENERATED from certs/trump11_certificate_tight_int.json
PackingCert/Main.lean          trump11_ok, trump11_tight_ok (native_decide)
PackingCert/Kernel.lean        trump11_ok_kernel, trump11_tight_ok_kernel (decide, axiom-free)
PackingCert/Measure.lean       MCert, checkMeasure : MCert → Bool        (lower bound, Rat prototype)
PackingCert/MeasureExample.lean perturbed Göbel example
PackingCert/MeasureData.lean   GENERATED from attempts/A08-measure-verify/tests/a05_10pt.json
PackingCert/MeasureMain.lean   s5_gt_26, s11_ge_37416 (native_decide, Rat checker)
PackingCert/MeasureInt.lean    MCertI, checkMeasureI : MCertI → Bool     (lower bound, all-Int, = verify_measure.py scaling)
PackingCert/MeasureIntData*.lean GENERATED (--int): 3.80 cert, 3.82 cert (fails), A05 set, Göbel
PackingCert/MeasureIntMain.lean a05_10pt_int_ok, goebel26_int_ok (native_decide)
PackingCertSlow.lean           s11_ge_3_80  — separate lib target `PackingCertSlow`
MeasureBench.lean              `lake exe measure_bench` — native timing / box counts (modes: goebel, grid, data, int_a05, int_3_80, int_3_82)
scratch/                       ad-hoc files (Axioms.lean etc.), not part of the library
```

## Upper-bound checker: `checkPacking`

Certificate `Cert = {denom, sideNum, sideDen, squares}`; every coordinate is an integer meaning
`coord/denom`; container `[0, sideNum/sideDen]²`. `checkPacking c = true` iff

1. `0 < denom`, `0 < sideDen`;
2. each square is a genuine unit square: `e = p1−p0`, `n = (−e.y, e.x)`, `e·e = denom²`,
   `p2 = p1 ± n`, `p3 = p0 ± n` (same sign);
3. each corner is strictly inside: `0 < x`, `x·sideDen < sideNum·denom` (same for `y`);
4. each of the 55 pairs is strictly separated by one of the 8 edge vectors `n` of the two squares:
   all corners of one project strictly below all corners of the other (`a·n < b·n`).

**Bridge lemma — NO LONGER ASSUMED (A28):** proved in `PackingCertMathlib/Bridge.lean` as
`checkPackingCCW_sound`; the statement below is what it says. `checkPacking c = true` ⇒ the 11 closed unit squares
`conv{corners/denom}` are contained in `[0, side]²` and pairwise disjoint (any linear functional
that strictly separates two finite point sets separates their convex hulls; the choice of axes
only affects completeness, never soundness). Hence `s(11) ≤ side`.

## Lower-bound checkers: `checkMeasureI` (Int, used for the real theorems) and `checkMeasure` (Rat prototype)

Both implement the claim in the header of `certs/verify_measure.py`: for μ = Σ wᵢ δ_{pᵢ}, wᵢ ≥ 0,
Σ wᵢ < n, **every closed unit square Q ⊆ [0,s]² has μ(Q) ≥ 1**, with θ ∈ [0,π/2] via t = tan(θ/2) ∈ [0,1],
`Q ⊆ [0,s]² ⟺ w/2 ≤ cx,cy ≤ s−w/2` (w = cos θ + sin θ), and `p ∈ Q ⟺ |u| ≤ ½ ∧ |v| ≤ ½`.
`checkMeasureI` uses exactly A08's integer scaling (t = T/2^K, K = depth+1; lengths × den(s)·2^(depth+2);
atoms over their own PD; weights over WD; NEED = WD; floor midpoints; tscale 2; outward-rounded clipping),
so its box tree coincides with the Python verifier's up to the root partition (5 837 883 vs 5 836 650 boxes on
the 3.80 certificate; 570 941 vs 570 943 Rat-vs-Int on the A05 set; 795 = 795 on Göbel). It is ~10× faster than
the Rat version (no gcds) and kernel-`decide`-able (demonstrated on the Göbel example only; millions of boxes
are far beyond kernel evaluation).

Rat prototype: certificate `MCert = {n, side, atoms : List ⟨px, py, w⟩, fuel}` (all `Rat`).
`checkMeasure c = true` iff all `w ≥ 0`, `Σ w < n`, and the branch-and-bound over
`(t, cx, cy) ∈ [0,1] × [0,side]²` (`t = tan(θ/2)`, `θ ∈ [0, π/2]`) discharges every box within
depth `fuel`, where a box `[t0,t1]×[x0,x1]×[y0,y1]` is discharged if
* after clipping the centre ranges to `wLo/2 ≤ c ≤ side − wLo/2`
  (`wLo = min(w(t0), w(t1))`, `w = cos θ + sin θ` unimodal in `t`) it is empty, or
* the atoms provably inside `Q(t,cx,cy)` for **all** parameters of the box (rational interval
  arithmetic on `u = cos·(px−cx)+sin·(py−cy)`, `v = −sin·(px−cx)+cos·(py−cy)`, `|u|,|v| ≤ ½`,
  with `cos ∈ [cos t1, cos t0]`, `sin ∈ [sin t0, sin t1]` exact rationals) have total weight ≥ 1;
* otherwise it is bisected along the widest dimension (`t`-width counted ×2), children inherit the
  mass already certified and drop atoms provably outside.

**Bridge lemma (assumed, elementary; stated in words in the header of `PackingCert/MeasureInt.lean`):**
`checkMeasure(I) c = true` ⇒ every closed unit square
`Q ⊂ [0, side]²` has `μ(Q) ≥ 1` (all such squares are covered by the box tree; interval arithmetic
over-approximates; `θ ∈ [0, π/2]` suffices by symmetry) ⇒ no `n` pairwise-disjoint closed unit
squares fit in `[0, side]²` ⇒ `s(n) ≥ side`.  Semantics match `certs/verify_measure.py` (A08).

**Caveat:** certificates must have positive margin — an atom exactly on the boundary of some
admissible square (e.g. Göbel's `(1,1)` and the wall-flush upright square `[0,1]²`) can never be
certified by boxes.  Kernel `decide` does not work for this checker (`Rat` normalisation uses
well-founded recursion); only `native_decide`.

## Regenerating the data (reproducible pipeline)

```
# upper bound: certs/*.json (A03) → Data.lean / DataTight.lean
python lean/gen_cert_lean.py certs/trump11_certificate_int.json       --name trump11
python lean/gen_cert_lean.py certs/trump11_certificate_tight_int.json --name trump11_tight -o lean/PackingCert/PackingCert/DataTight.lean
# lower bound: A08-format measure JSON → Lean data (fuel = max bisection depth; --int for the Int checker)
python lean/gen_measure_lean.py certs/measure_certificate_3.80.json --fuel 48 --int --name cert_3_80 -o lean/PackingCert/PackingCert/MeasureIntData.lean
python lean/gen_measure_lean.py attempts/A08-measure-verify/tests/a05_10pt.json --fuel 40 --int --name a05_10pt_int -o lean/PackingCert/PackingCert/MeasureIntDataA05.lean
python lean/gen_measure_lean.py attempts/A08-measure-verify/tests/a05_10pt.json --fuel 40 --name a05_10pt   # Rat version
cd lean/PackingCert && lake build && lake build PackingCertSlow
```
`gen_cert_lean.py` accepts integer corners over a common denominator, rational corners, or
centre + `t = tan(θ/2)`; it re-checks the certificate in exact `Fraction` arithmetic before
writing Lean, so a failing `lake build` means "Lean disagrees", never "bad input".
`gen_measure_lean.py` accepts the `verify_measure.py` JSON format (incl. `"symmetry": "D4"`).

How the certificates were generated: see `certs/` (A03: exact 60-digit solution of Trump's contact
system, scaled by `s_c/s*` and rounded to rationals; A05/A08: optimised 10-point unavoidable set).

## Mathlib project `lean/PackingCertMathlib` (A28, 2026-08-24)

`lake exe cache get` **succeeded** on the retry: 8691 files, 6 min 15 s, 6.5 GB `.lake` +
0.4 GB download cache + 3.0 GB extra toolchain. All artefacts were deleted afterwards (free space
on this machine fell to 0.29 GB while the sibling A27 run was going); the `.lean` sources are
committed, so the theorems above rebuild with

```
cd lean/PackingCertMathlib
lake exe cache get           # ~6 min, ~7 GB; elan re-installs toolchain v4.34.0-rc1 (3 GB)
lake build                   # Bridge 15 s, Band 22 s, Trump11 18 s, Checker/Data 1.3 s each
lake env lean scratch/Axioms.lean     # the axiom table above
```

Layout:

```
PackingCertMathlib/Checker.lean   verbatim copy of PackingCert/{Geometry,Checker}.lean
                                  + isUnitSquareCCW / checkPackingCCW (⇒ checkPacking)
PackingCertMathlib/Data.lean      copy of the generated trump11 data
PackingCertMathlib/Bridge.lean    RP, rdot, aff, sqSet, IsUnitSquare; SAT soundness; the bridge
PackingCertMathlib/Band.lean      centred squares, support function, the A26-family band lemma
PackingCertMathlib/Trump11.lean   native_decide + kernel decide + the real-plane theorem
scratch/Axioms.lean               #print axioms
BridgeSketch.lean                 A06's original sketch — superseded by Bridge.lean
```

The copy of the checker in `Checker.lean` is byte-identical to `lean/PackingCert`'s (the two
projects are pinned to different Lean toolchains, so they cannot `require` each other); that is
what makes the bridge a theorem *about the same checker*.

### Added by the advisor (2026-08-18)
| theorem | target | build | axioms |
|---|---|---|---|
| `PackingCert.MeasureI.s11_ge_3_81 : checkMeasureI Data.cert_3_81 = true` (certs/measure_certificate_3.81.json, 980 atoms, mass 10.9852) | `lake build PackingCertSlow381` | 12 min | native_decide only |
| `PackingCert.MeasureI.s11_ge_3_82 : checkMeasureI Data.cert_3_82 = true` (certs/measure_certificate_3.82.json, 1769 atoms, mass 10.985474) | `lake build PackingCertSlow382` | 26.5 min | native_decide only |
Data files generated with `python lean/gen_measure_lean.py certs/measure_certificate_3.8X.json --fuel 48 --int --name cert_3_8X -o lean/PackingCert/PackingCert/MeasureIntData38X.lean`.
