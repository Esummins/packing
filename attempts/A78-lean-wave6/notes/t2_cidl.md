# A78 T2 — CIDL-LEAN: the (c-idl) certificate replayed in Lean

Obligation: `docs/proofs/attainment_ub.md` §7.5.  Goal: turn `TopLevel.lean`'s
`axiom shatA22_eq_shat : shatA22 = shat` (the last *open-mathematics* leaf of the
UB-at-ŝ route) into a THEOREM, backed by a `native_decide` replay of
`certs/cidl_identity.json` plus one refined A22-interface axiom.

## What landed

| module | role | tier |
|---|---|---|
| `PackingCertMathlib/CidlPoly.lean` | sparse `Poly := List (List Nat × Rat)`, `padd`/`pmulRaw`/`pnorm`/`isZero`, the `ubound` sign gate | core Lean (no Mathlib) |
| `PackingCertMathlib/CidlGen.lean` | the 13 generators REBUILT from A22's `HALF`/`NHAT`/`frame`/`corner_scaled`/`row_wall`/`row_edge`/`ROWSPEC`; the canonical octic | core Lean |
| `PackingCertMathlib/CidlData.lean` | generated from the certificate by `lean/gen_cidl_lean.py` (e, Δ, 13 cofactors, cert octic; sha256 in the header) | core Lean |
| `PackingCertMathlib/CidlCheck.lean` | the four `native_decide`/`decide` checks — ISOLATED module | core Lean |
| `PackingCertMathlib/CidlBridge.lean` | real semantics `eval`, soundness of `pnorm`/`isZero`, the sign gate, and `octic_zero_of_generators` | Mathlib |
| `TopLevel.lean` | `axiom a22_exact_structure` (new) + `theorem shatA22_eq_shat` (was an axiom) | Mathlib |

## Design decisions (and the two deviations from the brief)

1. **Monomial multiplication pads instead of `zipWith`.**  `mmul` is defined by
   `mmul [] m = m`, `mmul (a::as) [] = a::as`, `mmul (a::as) (b::bs) = (a+b) :: mmul as bs`.
   With `evalM` total on ragged input (`evalM [] xs = 1`, `evalM m [] = 1`) the lemma
   `evalM (mmul m₁ m₂) xs = evalM m₁ xs * evalM m₂ xs` holds UNCONDITIONALLY — no
   `length = 13` hypothesis has to be threaded through the whole development, and no
   `native_decide`-checked well-formedness predicate is needed.  (Brief's design item 1
   suggested `zipWith (+)` "with the length hypothesis"; this is strictly simpler.)

2. **DEVIATION: no Taylor shift for the `Δ` gate — the crude monomial interval bound
   suffices.**  For `0 ≤ a ≤ x ≤ b`, `Σ_k c_k x^k ≤ Σ_k (c_k b^k if c_k ≥ 0 else c_k a^k)`
   (`ubound`).  On `[3/10, 2/5]` this gives `e ≤ −1.8394…` and `Δ ≤ −3.4520…`, both
   strictly negative, so both sign gates fall out of ONE generic induction lemma
   (`uniR_neg_of_gateNeg`) plus a `native_decide` on a rational comparison.  No Sturm
   chain, no degree-34 `ring` identity, no Taylor coefficients.  The brief's Taylor route
   (c = 7/20, r = 1/20, `b₀ = −4.7878`, `Σ_{k≥1}|b_k| r^k = 1.9055`) would also have
   worked; the interval bound is a strictly weaker demand on the tactic framework, and the
   conclusion it certifies (`< 0` on the whole interval) is STRONGER than the checker's
   "no root in the gate interval".

3. **Soundness does not depend on the sort being a sort.**  `pnorm = pcollapse ∘ mergeSort`
   and the only lemma used is `List.mergeSort_perm` (a permutation).  `eval_perm` is proved
   by `List.Perm` induction directly on the recursive `eval` (no `List.Perm.sum_eq`
   needed), and `pcollapse` preserves `eval` unconditionally — it is not assumed to see
   equal exponents adjacently.  So a wrong `termLe` could only make the check FAIL.

4. **`pmul` normalises, `pmulRaw` does not.**  `Δ⁸` must be normalised between
   multiplications (the raw 8-fold product of a 34-term polynomial would be `35⁸ ≈ 2.3e12`
   terms); the identity's left side is assembled with `pmulRaw` and left unnormalised
   (86 728 terms) — only the final `isZero` sorts.

5. **Data-file shape.**  A 2 385-element nested list literal blows through
   `maxHeartbeats` at `«synthesize pending MVars»` (the elaborator's cost is superlinear in
   literal size); `gen_cidl_lean.py` therefore emits ONE `def … : List Int` per
   `(S-power, t-coefficients)` pair (≈300 literals each) and assembles them.  The module
   also carries `set_option maxHeartbeats 1000000`.

6. **DEVIATION (mechanical): three edits to `TopLevel.lean` fall outside the
   `shatA22_eq_shat … trump_packs_at_shat` block** — the added
   `import PackingCertMathlib.CidlBridge`, and the two header-docstring sentences the
   brief itself asks for (axiom count + CIDL-LEAN status).  Both are one-line/one-sentence
   localised insertions; the file was re-read immediately before each edit.

## Non-vacuity controls (`#eval`, one `lake env lean` run)

| control | value |
|---|---|
| `lhsPoly.length` (raw terms of `Σ q_j G_j`) | 86 728 |
| `(pnorm lhsPoly).length` / `(pnorm rhsPoly).length` | 2 682 / 2 682 |
| `gens.map length` | `[6,7,6,7,7,9,11,7,11,11,11,11,7]` — identical to `verify_cidl.py`'s |
| `isZero lhsPoly`, `isZero rhsPoly` | `false`, `false` (neither side is the zero polynomial) |
| `qcoeff` gate (+1 on one cofactor coefficient) | `isZero (lhsBad − rhs) = false` |
| `octic` gate (`−496 → −495`) | `isZero (lhs − rhsBad) = false` |

The generator term counts matching Python's exactly is independent evidence that the
`CidlGen.lean` transcription of `frame`/`corner_scaled`/`row_wall`/`row_edge` is faithful;
the identity itself passing is the end-to-end check.

## Costs (this machine, `lakeb.py`, BELOW_NORMAL priority)

* `CidlData.lean` elaboration: **162 s** (one-off; 295 KB, ≈10 070 integer literals).
* `CidlCheck.lean` (compile + all four `native_decide`/`decide` evaluations): **27 s**.
* `CidlBridge.lean`: ≈20 s.

## Axiom audit (`logs/axioms_t2.log`)

```
'PackingCert.Cidl.cidl_octic_canonical' does not depend on any axioms
'PackingCert.Cidl.cidl_identity'        [propext, Classical.choice, Quot.sound,
                                         cidl_identity._native.native_decide.ax_1_1]
'PackingCert.Cidl.cidl_gate_e'          [… , cidl_gate_e._native.native_decide.ax_1_1]
'PackingCert.Cidl.cidl_gate_delta'      [… , cidl_gate_delta._native.native_decide.ax_1_1]
'PackingCert.Cidl.octic_zero_of_generators'
                                        [propext, Classical.choice, Quot.sound,
                                         + the three native_decide axioms]
'PackingCert.S11.shatA22_eq_shat'       [propext, Classical.choice, Quot.sound,
                                         a22_exact_structure, shatA22, zhat,
                                         + the three native_decide axioms]
'PackingCert.S11.trump_packs_at_shat'   [… , + trump_packs_at_shatA22]
```

`shatA22_eq_shat` no longer appears as an axiom anywhere (it is gone from
`s_eleven_ge` / `s_eleven_eq`'s lists, replaced by `a22_exact_structure`), and no
declaration in the audit depends on `sorryAx`.

## Spec/code observations (verify_cidl.py vs the prose)

See the report; recorded here for the ledger:

* `verify_cidl.py` [G] certifies "no root in the gate interval" by Sturm on the SQUAREFREE
  part, having first checked the endpoints are non-zero; the prose (§7.3) says
  "e(t̂)Δ(t̂) ≠ 0".  Both are implied by the strictly-stronger `< 0` proved in Lean.
* The certificate's `gate_interval` is `[3/10, 2/5]` and the checker only requires it to
  CONTAIN `[3/10, 2/5]`; the Lean side hard-codes `[3/10, 2/5]` (`CidlGen.gateA/gateB`),
  which is what the composition actually needs.
* `verify_cidl.py` builds the right-hand side from its own hard-coded `OCTIC`, not from the
  certificate's `octic` field (that field is only compared, check [O]).  `CidlCheck` mirrors
  this exactly: `rhsPoly` uses `CidlGen.OCTIC`, and `cidl_octic_canonical` compares
  `Data.certOctic` to it.
* `verify_cidl.py`'s docstring says the 18 surviving rows "collapse … to the 13 distinct
  generators G_0..G_12 hard-coded below"; they are not hard-coded, they are BUILT (the
  docstring's own next sentence says so).  Cosmetic.
