#!/usr/bin/env python3
"""Writes attempts/A78-lean-wave6/notes/findings.md (the lab's per-attempt findings note,
a required deliverable of the BRIEF).  Sections for T3/T5 are appended by append_notes.py
once the engineers' reports are in."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'notes', 'findings.md')
os.makedirs(os.path.dirname(OUT), exist_ok=True)
BODY = r'''# A78 — Lean wave 6: findings (Fable lead; Opus for T2/T3/T5 mechanics; 2026-09-02)

Labels: [T] proved, [F] finding, [C] open, [E] engineering.  Per-task engineer notes:
`t2_cidl.md`, `t3_alive.md`, `t5_corpus.md`.

## Verdicts (per node)

* **B.CENSUS — LEAN-PROVED (F11/H2 discharged).**  `Census.lean` is the authoritative
  Young-form definition; L3 exhaustiveness is a theorem about packings
  (`skeleton_mem_census`, at every side `s ∈ (3,4)`); the counts and A72 agreement are
  `native_decide` theorems (`CensusCheck.lean`).
* **B.EXACT — LEAN-PROVED.**  `hface` discharged (`containsPins_skeleton`); E.2's D4
  bookkeeping machine-checked (`skeleton_d4`); Lemma M→E = `class_kill`.
* **B.SEL / C.CC2 — LEAN-PROVED.**  `hinc` discharged (`card_lt_teleport`);
  `exists_kmax_skeleton`, `cc2_stuck_census`, `cc2_two_meeters_census` unconditional.
* **A.UBshat — LEAN-PROVED (CIDL-LEAN discharged, T2).**  `shatA22_eq_shat` is a theorem;
  the single new axiom `a22_exact_structure` is A22's certified content, no algebra.
* **A.UNIQ — own tier LEAN-PROVED** (node stays blocked-only red): `unique_transfer` and
  `stratify` are THEOREMS; the honest chain + collapse is `unique_via_chain`
  (`UniqueChain.lean`) with U-O1/U-O2 as explicit hypotheses.
* **D.D4 — verifier_lean:** the WLOG is the theorem `d4_wlog` (`D4Wlog.lean`), at every
  side, conditional on root occupancy exactly as D4.4 records.
* **D.ALIVE — verifier_lean (T3):** see §T3 below.
* **C.K61 / D.TRAP / D.P1 / A.THMU — corpus_replayed (T5):** see §T5 below.
* **TopLevel roster: 12 → 7 named axioms** (`stratum_kill`, `trump_residual`, `basin` +
  the four A22 interface axioms `zhat`, `shatA22`, `trump_packs_at_shatA22`,
  `a22_exact_structure`).  `s_eleven_unique` now depends on exactly `basin`,
  `stratum_kill`, `trump_residual`, `zhat` (+ propext/choice/Quot.sound); `s_eleven_ge` /
  `s_eleven_eq` on the 7 axioms + the `native_decide` axioms of `check_3_82` and the three
  CIDL checks (`logs/axioms_t1.log`, `logs/axioms_t2.log`).  Full default target builds
  (3181+ jobs), `Measure382Check` cache hit throughout, no `sorryAx`.

## T1 — the census as a definition (Census.lean, CensusCheck.lean, CensusCorpus.lean)

* [T] **Definition.**  `IsSkelCell s z a` := every cell of `a`'s down-set (inside its
  corner) is occupied by a square of `z` sitting EXACTLY on the corner grid
  (`OccupiesSlot`, the point-set equality of `Skeleton.lean`); `skeleton s z` = the skeleton
  cells among the 36 small slots.  This is L1's "largest Young set of occupied cells" read
  as a cell predicate (the union of Young sets of occupied cells IS the set of occupied
  cells whose down-set is occupied).  The eight A72 binding choices are pinned at their
  definitions; **B1, B3, B6 are THEOREMS** (`occupied_small`: at `s < 4` an occupied slot
  has offsets `< 3`; `slotCentre_injective`: at `s ∉ ℤ` distinct slots have distinct
  centres, so the corner diagrams partition the skeleton; `skeleton_card_le : k ≤ 11`).
* [T] **The B2 predicate is decided combinatorially and proved equal to the real one on the
  whole window** (`axisFar_iff`, `slotFar_iff`): for the cross-family difference
  `s − (i+j+1)` and `s ∈ (3,4)`, `|·| ≥ 1 ⟺ i + j ≤ 1 ∨ 4 ≤ i + j`.  So the census is ONE
  object on `(3, 4)` — A53 L2(iv)'s `(3.82, 3.9)` was conservative.  [F] The window
  hypotheses actually used everywhere are `3 < s < 4`; nothing in the census layer
  depends on `s₀` or on rationality of `s`.
* [T] **Exhaustiveness without computation** (`skeleton_mem_census`): the skeleton of any
  packing at `s ∈ (3,4)` is a census tuple — Young per corner by definition; small by B1;
  pairwise far because two skeleton slots are occupied by DISTINCT squares (B3) whose
  interiors are disjoint (`far_of_interior_disjoint`: the midpoint of two close centres
  lies in both open boxes).  `exists_class_skeleton` puts every packing in the class of a
  representative (`classCodes` = dedup of canonical codes; `canonCode_eq`: the fold-min is
  attained at some `g`).  Axioms: propext/choice/Quot.sound only.
* [T/M] **Counted and cross-checked (CensusCheck.lean, native_decide, 409 s compile+eval):**
  `censusL.length = 1110`, `censusL.Nodup`, `classCodes.length = 163`,
  `censusF = A72's tuple set` (decoded from `census_cleanroom.json`, generator
  `code/gen_census_corpus.py`), D4-closure, and **A72's orbit partition = the Lean orbit
  partition** (`corpus_classes_canon` + `corpus_classes_distinct`); Trump's tuple
  `((2,1),(1),(1),∅)` = A72's canary, `k = 5`, a census tuple (also by kernel `decide`,
  `trumpPins_isCensusTuple`, so `trumpStratum` needs no `native_decide`).  This is the third
  independent implementation of the census (A53 Python, A72 clean-room Python, Lean), and the
  first whose definition is the object the composition consumes.
* [T] **The D4 action** (`d4Apply`: swap-then-sign about the centre; group law `D4.mul`,
  `D4.inv`; `d4Apply_mul`, `d4Apply_inv_apply`), on squares (`d4Sq`, tilt `tRefl t =
  (1−t)/(1+t)` iff `det = −1`, with `cosT_tRefl = sinT`, `sinT_tRefl = cosT`; `d4Sq_set :
  (g·q).set = g '' q.set` via the abs-transport lemma `d4Sq_uv`), on slots (`d4Slot`; R8 is
  the theorem `d4Apply_slotCentre`), on configurations (`d4_packing`: packings at the same
  side), and **equivariance** `skeleton_d4 : Simp(g·P) = g·Simp(P)`.
  `isCtrSym_d4Apply` ties it to TopLevel's `IsCtrSym`.
* [T] **Lemma M→E** (`class_kill`): `S ⊆ g·T` + monotone kill of `S` at `s ∈ (3,4)` ⟹ no
  packing at `s` has skeleton in the class of `T`.  Proof = normalise by `g·g'⁻¹`
  (`D4.mul_inv_mul`), `skeleton_d4`, `containsPins_skeleton`, K1(i).
* [F] **`hface` was reflexivity, as A63/A68 predicted** — its whole content is B3
  (injectivity of the slot assignment), i.e. the one place `s ∉ ℤ` enters.
* [F] **TopLevel definitions are computation-free**: `StratumIdx := Fin classCodes.length`,
  `classRep i := decodePins (classCodes.get i)`, `trumpStratum` via `List.idxOf` + kernel
  `decide` membership, `InStratum i s z := InClassOf (skeleton s z) (classRep i)`.  Nothing
  in `s_eleven_*` depends on `CensusCheck.lean`.
* [E] Eight-case D4 lemmas: `cases` on the three bits + `simp only [...]` then
  `first | (left; constructor <;> rw [abs_eq_abs] <;> first | (left; ring1) | (right; ring1))
  | (right; …)` — `ring1` is essential (`ring` falls back to `ring_nf` and does NOT fail, so
  `first` never backtracks).  `simp only` errors with "no progress" on the identity case of a
  64-case lemma — use `simp`.  A `d4Slot_eq` rewrite lemma whose RHS contains `d4Slot` loops
  `simp`; state the per-case `rfl` equation instead.  `Finset.card_le_card_of_injOn` gives
  `k ≤ 11` from `containsPins_skeleton` in one line.

## T2 — CIDL-LEAN (Opus; `t2_cidl.md`)

* [T] Generators REBUILT from A22's conventions in `CidlGen.lean`; sparse 13-variable
  polynomials over `Rat` with `eval` semantics (`CidlPoly`/`CidlBridge`); identity, octic
  and both sign gates by `native_decide` in the isolated `CidlCheck.lean` (27–30 s; data
  elaboration 162 s one-off, split into ~300-literal defs to dodge `maxHeartbeats`).
* [F] **No Sturm needed in Lean**: on `[3/10, 2/5]` the crude monomial interval bound gives
  `e ≤ −1.839`, `Δ ≤ −3.452` — strictly stronger than the checker's "no root" (`e` has
  all-negative odd coefficients, `e(t) < 0` for `t > 0` outright).
* [F] Non-vacuity controls: `lhs` 86 728 raw → 2 682 normalised terms = `rhs`; `qcoeff` and
  `octic` corruptions give `isZero = false`; generator term counts match `verify_cidl.py`.
* [F] Spec/code: `verify_cidl.py`'s docstring says the generators are "hard-coded" (they are
  built); the RHS uses the checker's own `OCTIC`, the certificate's field is only compared.

## T4 — the uniqueness clause (UniqueChain.lean; TopLevel)

* [T] `unique_transfer` and `stratify` are theorems from `exists_stratum` (census
  exhaustiveness at `m ∈ wnd ⊂ (3,4)`, `wnd_subset_Ioo`), with `f = id`, `e = 1`, `z' = z`.
  §1 of `unique_transfer.md` is now literal.
* [T] `unique_via_chain`: `hstuck` (H10-stuck) + `hU` (Theorem U interface) ⟹ every packing
  at ŝ is a G-image of ẑ; strong induction on `11 − k`: not stuck ⟹ a CC-2 teleport
  (`teleport_packing`, `card_lt_teleport`, one square moved) ⟹ IH ⟹ collapse by `hU`;
  stuck ⟹ `exists_stratum` ⟹ `hstuck` forces Trump's class ⟹ `trump_residual` + `basin`.
  The `k = 11` base case is stuck because the injective slot assignment is onto `Fin 11`.
  `s_eleven_unique_of_chain` = the clause WITHOUT `stratum_kill`/`unique_transfer`; axioms
  `basin`, `trump_residual`, `zhat` only.
* [F] The formalisation confirms A63's diagnosis exactly: the uniqueness clause's open
  content is `{U-O2 = H10-stuck, U-O1 = Theorem U as interface}` plus the D-nodes; nothing
  else.  `hU` is stated as "agrees with a G-image of ẑ in all but one square ⟹ is a
  G-image" — the certificate-level Theorem U (A65) proves it for ẑ itself; the G-covariance
  step is bookkeeping A65's ledger should state when U-O1's Lean interface is built.

## D.D4 — the WLOG as a theorem (D4Wlog.lean)

* [T] `d4_cover_zone` (R4 at every side/zone width, by sign-normalisation + swap) and
  `d4_wlog` (conditional on root occupancy: a D4-image packing at the same side with a
  square centred in `T(s)`, tilts in `[0,1]`, squares = explicit images).  R6/R7 (verify_tree2
  cells/t-bins) are tree machinery and were not ported; D4.4's scope caveats unchanged.

## Engineering (delta over the A64–A75 recipes)

* [E] `attempts/A78-lean-wave6/code/lakeb.py`: serialised, BELOW_NORMAL-priority `lake build`
  wrapper with a repo lock and a refusal if `Measure382Check.olean` is missing;
  `--nolock` for light builds concurrent with a long corpus run.  Three agents built
  concurrently on a CPU-saturated box without a single rebuild collision.
* [E] `lake env lean File.lean` (no lock, no olean) is the right inner loop for a new
  Mathlib file on this machine (~35 s per check under load); `lake build` per module for
  the olean.
* [E] A second `lean_lib` (`PackingCertCorpus`, roots `PackingCertMathlib.Corpus`) keeps
  the 73 corpus modules out of the default target and CI.
'''
open(OUT, 'w', encoding='utf-8', newline='\n').write(BODY)
print('wrote', os.path.abspath(OUT))
