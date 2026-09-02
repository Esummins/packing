# The trusted computing base (A62, checklist C1 + C5-lite)

The exact list of programs whose correctness the theorems' truth depends on, at commit
`c9980bf` (2026-09-01). Everything that **finds** certificates — HiGHS, Clarabel, CP-SAT,
the annealers, the LP row/column generators, `caselp.py`, `ladder.py`, the tree builders,
the agents — is **outside** the TCB: a wrong finder can only produce a certificate that the
verifiers reject. Raw line counts, hashes, header texts and unclassified float greps:
`attempts/A62-trust-ledger/results/tcb_raw.md`. Ambient trust shared by everything: the
Python 3 interpreter (ints, `fractions.Fraction`, `json`), the OS, and — where marked —
`mpmath.iv` and the Lean 4 kernel (+ `Lean.ofReduceBool` for `native_decide` theorems).

## Tier 1 — Track A (s(11) ≥ 3.82; also s(12) ≥ 3.90)

| program | lines | soundness claim (one line) | float audit (C5-lite) |
|---|---|---|---|
| `certs/verify_measure.py` | 808 | PASS ⇒ μ(Q) ≥ 1 for every closed unit square Q ⊆ [0,s]² and Σw < n ⇒ s(n) ≥ s (bridge in header) | numpy/floats shortlist atoms + build FAIL witnesses only; every accept decision integer/Fraction (audited line-by-line, `tcb_raw.md` §2: hits at 244–349 = shortlist, 387–446 = witness path, 290 `fneed−1e-9` = conservative shortlist target) |
| `lean/PackingCert/PackingCert/{Geometry,MeasureInt}.lean` + data | 53+244 | second implementation: kernel/`native_decide` evaluation of the same integer scheme; box tree coincides with the Python verifier's up to the root partition | no floats (Lean Int) |
| `certs/verify_certificate.py` | 168 | PASS ⇒ n disjoint closed unit squares in [0,side]² exist ⇒ s(n) ≤ side | 3 hits, all print-rendering |
| `lean/PackingCert/PackingCert/Checker.lean` (+ `PackingCertMathlib/Bridge.lean`) | 76 | second implementation of the UB check; bridge to ℝ² **proved** in Lean (A28), axioms `propext, Classical.choice, Quot.sound` only | none |

Track A status: the only family with a genuine second implementation (C3) — Python ↔ Lean.
The measure **bridge** lemma is prose (checklist F2); the Lean side proves checker = true.

## Tier 2 — Track B (optimality tree), decision programs

| program | lines | soundness claim (one line) | float audit |
|---|---|---|---|
| `attempts/A53-simple-strata/code/verify_case.py` (canonical; 16 byte-identical copies) | 957 | PASS ⇒ no family of n pairwise-disjoint closed unit squares in [0,s]² has a square containing each core while avoiding the NO-families (spec: `case_lp_certificate_v1.md`) | shortlist/witness only; exemption requires float **and** exact tests (line 473); decision path exact |
| `attempts/A56-sparametric/code/verify_param.py` | 793 | PASS ⇒ the same kill for **every** s in [s_lo, s_hi] (spec: `parametric_kill_certificate_v1.md`); imports A53's audited integer core unmodified | shortlist/witness only |
| `attempts/A53-simple-strata/code/skeletons2.py` (+ `skeletons.py`) | 116+151 | the census: every Young-form skeleton class at s0 is enumerated (163 D4 classes); exact Fractions | 3 hits, all float renderings in output |
| `attempts/A22-local-rigidity/recheck.py` | 432 | PASS ⇒ unique contact solution ẑ in the box, feasible, σ ≥ ŝ with equality iff ẑ (spec: `rigidity_krawczyk_certificate_v1.md`) | **mpmath.iv in the decision path** (validated intervals — a trusted third-party component, unlike Tier-2's stdlib-only rule); float conversions guarded by nextafter |
| `attempts/A36-levers/code/a36_check.py` | 566 | PASS ⇒ the composed basin theorem at radius 3.7e-3 | same mpmath.iv trust |
| `attempts/A37-cp-atlas/code/a37_check.py` | 719 | PASS ⇒ σ ≥ V on the entry's box (spec: `atlas_value_certificate_v1.md`); currently off the critical path | same mpmath.iv trust |
| `attempts/A27-close-384/verify_tree2.py` (A29 variant 402) | 381 | PASS ⇒ tree logic of the 3.84 case tree: exact cover, D4 reduction, core containment (3.84 track only; PAUSED) | 8 hits, rendering + float cover enumeration cross-checked exactly |

## Tier 3 — meta-arbiters (not load-bearing for the theorem)

| program | lines | claim | note |
|---|---|---|---|
| `attempts/A57-shadow-trees/code/alivewitness.py` | 233 | exact disjoint-witness family ⇒ τ* ≥ budget ⇒ no kill certificate can exist | proves nodes UNKILLABLE — steers the campaign; the theorem never cites an ALIVE result. Float hits are search-side; final gaps exact. |
| `.../check_trump_feasible.py`, `canary.py`, `selftest*.py` | ~50–330 | canaries/self-tests | quality control, not proof |

## Enumerated TCB debt (what C1 exposes)

1. **Tree-composition logic above the leaves.** A57's sub-stratification kills (k5_11,
   k5_16) and A59/A60's zone-tree compose leaf certificates through cover/branching logic
   living in `tree57.py`/`substrat.py`/`pinguard`/A60's engines — audited by in-attempt
   exact cover audits, but there is **no standalone end-to-end verifier** for these trees
   (the 3.84 track has one: `verify_tree2.py`). A `verify_tree_s0.py` analogue is owed
   before the composition is citable (the A54 `substrat.py` soundness gap lived exactly
   here, found by A57).
2. **Second implementations (C3):** exist only for the Track-A pair. `verify_case.py` and
   `verify_param.py` decide the optimality tree with ONE implementation each; the frozen
   specs in this directory are the clean-room inputs.
3. **mpmath.iv** sits in the rigidity chain's decision path (three checkers). Either the
   Lean replay via t-reparametrisation (A28's route, checklist F6) or an independent
   interval implementation removes it.
4. **Census single-sourced** (H2): `skeletons2.py` is in the TCB until an independent
   re-enumeration from the written definition diffs clean.
5. **16 copies of `verify_case.py`** are byte-identical today (verified, `tcb_raw.md`
   §1.3); any future edit must change the canonical copy and re-propagate, or better,
   deduplicate to one import point (as `verify_param.py` already does).

**A79 update (2026-09-02):** the rigidity chain (rows 31-32 above: `recheck.py`,
`a36_check.py`) is replayed in Lean — `RigidityCheck.lean` (`native_decide`) + the soundness
theorems `krawczyk_sound`, `zhatV_feas`, `a22_optimal`, `a36_basin` — with its own dyadic
interval kernel and certified Taylor trigonometry; `mpmath.iv` is no longer in the decision
path of E.A22/E.A36 at either tier (A70's stdlib re-checkers are the second implementation).
`a37_check.py` (row 33, off the critical path) is unchanged.
