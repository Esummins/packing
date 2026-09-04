# Lean wave 7 (A86, 2026-09-03): the tube checker, the atlas box checker, the zone-tree composition, the window rows

Status note for the Lean owner (the successor of `tube_obligation_A83.md` and
`k0_readiness_A85.md`).  Files: `PackingCertMathlib/{RigidTubeKernel, RigidTube, TubeSeam,
RigidTubeData, RigidTubeCheck, AtlasKernel, AtlasBridge, AtlasData, AtlasCheck, ZoneTree,
Composition, WindowRows}.lean`, `Corpus/Tube/`, generators `gen_tube_lean.py`,
`gen_atlas_lean.py`; engineer notes `attempts/A86-lean-wave7/notes/{t1_tube_data,t2_atlas}.md`.

## 1. What is proved (axioms: `propext, Classical.choice, Quot.sound` unless stated)

| theorem | file | statement |
|---|---|---|
| `checkTube` | `RigidTubeKernel.lean` | the port of `certs/verify_tube.py`: hull box `tubeArr`, pair-relative boxes `pairArr` for edge/dist rows, `[V]` on the pair boxes, `[H]` `q_vv`/`Hv`/`|H|`, `[K][E]` `β` on the pair boxes, `[P]` the monotone iteration `iterT` from `X_max` |
| `tube_basin` | `RigidTube.lean` | `checkA22 c = true`, `checkTube c tc = true` ⟹ every feasible `z ∈ Tube_v(T, r)` has `s(z) ≥ s(ẑ)`, equality only at `ẑ` (A83 T1) |
| `shift_inv_D` | `RigidTube.lean` | an expression invariant under a coordinate-pair shift has invariant symbolic derivatives (the pair-relative box is sound for the whole chain) |
| `iterT_sound`, `EtubeR_mono` | `RigidTube.lean` | the monotone iteration dominates the true norm (A83 §5) |
| `tube_tframe`, `inTube_mkVec` | `TubeSeam.lean` | the `t`-frame form: a packing at `m` inside the tube has `m ≥ ŝ_A22`, equality only for `ẑ` |
| `seam_inTube` | `TubeSeam.lean` | Lemma SEAM's per-coordinate map: pins at slots `α + β·m` (`w = 0` up to the slot residual), free squares within `r_land` of the `λ₀`-dilate of `ẑ`, `r_land + T·ε_v ≤ r_c` ⟹ in the tube at depth `ŝ − m` |
| `vfree_bound`, `pin_slot_bound` | `TubeSeam.lean` | the two certificate-data residuals from `‖ẑ − z0‖_∞ ≤ r0` (no exact structure of `ẑ`) |
| `checkAtlas` | `AtlasKernel.lean` | trivial-reach box checker in `(cx, cy, t)`: witness corner pairs, rational `cosT`/`sinT` enclosures |
| `atlas_kill`, `atlas_kill_fold` | `AtlasBridge.lean` | PASS ⟹ every container of a configuration in the (tilt-folded) box has side `≥ L` |
| `atlas_dilated_kill_fold` | `AtlasBridge.lean` | Lemma K0-ATLAS: `L ≥ s0` ⟹ no packing at any side `m < s0` has its `Δ_{s0/m}`-dilate in the box (every window side, no dilation bookkeeping) |
| `ClosedTree`, `tree_kill` | `ZoneTree.lean` | Lemma P-TREE (a)+(b): leaves (K)/(N) = `checkCaseI` at `s0` + `NodeHypC`, (C), (D) = the SEAM landing, (D′) = folded atlas box; `cover` = the tree's disjunction ⟹ every packing at `m ∈ [ŝ − T, ŝ]` whose dilate satisfies the root has `m ≥ ŝ`, and at `ŝ` is a `D4`-image of `ẑ` |
| `root_of_containsPins` | `ZoneTree.lean` | Step 1: `ContainsPins S m P` + drift budget `(s0/m − 1)·A < ρ` ⟹ slack pin cores inside distinct dilated pins (`bprime_containment`, `occupiesSlot_params`) |
| `zone_dichotomy`, `grid_cover`, `slot_outside_zone`, `pd_convex`, `pd_rule`, `d4_dil_comm` | `ZoneTree.lean` | the rule library: A57 T1, CI-1, CI-3, Lemma PD (both halves), D.S6's mod-`G` commutation |
| `ClassKilledAt`, `s_eleven_ge_of_classes`, `s_eleven_unique_of_classes` | `Composition.lean` | the two TopLevel consumers from the per-class obligation alone (no `stratum_kill`, `trump_residual`, `basin`) |
| `classKilledAt_of_tree`, `classKilledAt_of_slabs` | `Composition.lean` | a closed tree for `S ⊆ g·classRep i` gives the obligation on `[ŝ − T, ŝ]`; the slab split |
| `s_eleven_ge_of_split`, `s_eleven_unique_of_split` | `Composition.lean` | the `stratum_kill` re-split of `k0_readiness_A85.md` (`StratumKillAll` / `StratumKillMin`) |
| `SlabKill`, `slabKill_of_param/case/M1`, `windowKilled_of_slab`, `k5_06_slab` | `WindowRows.lean` | the window rows: a V.PARAM row covers its whole window, the slack-core grid, M1; the `stratum_kill` instance; the replayed k5_06 pilot composed (+ `check_k5_06_param`'s evaluation axiom) |

Evaluation axioms: `checkTube_*` (`RigidTubeCheck.lean`, `Corpus/Tube/*`), `checkAtlas_all`
(`AtlasCheck.lean`), each confined to its isolated module.

## 2. TopLevel roster: what each remaining axiom now reduces to

* `stratum_kill` + `trump_residual` → `∀ i m, ClassKilledAt i m` (per class: `classKilledAt_of_tree`
  on the tube's slab — a `ClosedTree` whose leaf facts are `checkCaseI`/`checkAtlas` PASSes,
  the SEAM landing data, and the tree's `cover`; `checkTube` for the class direction;
  `root_of_containsPins` — plus `SlabKill` rows below the slab).  `basin` is not consumed on
  this route.  The old axioms imply the new hypotheses.
* `a22_exact_structure` unchanged.

## 3. Replay cost table

REPLAY_TABLE_PLACEHOLDER

## 4. Residues

* the tree-file → `cover` emitter and CI-2 (core-constructor monotonicity): replay tooling;
* the per-class (D)-leaf landing data (`seam_inTube`'s hypotheses) and the `ClosedTree`
  instances for trump5 / k4_08 / k0_00: awaiting the campaigns' leaf corpora;
* the 9 converting C.A61 rows as `checkParamI` hypotheses of `slabKill_of_param`'s shape.
