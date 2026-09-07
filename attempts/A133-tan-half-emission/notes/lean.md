# A133 T2 — what `LocalCertT.lean` proves, and what still stands between it and `localDead_s07_t`

**Read this together with `attempts/A126-localdead-lean/notes/obligations.md` §2, which names the
four pieces (C1)–(C4) of `LocalCert.CertCover` and the one primitive they were all waiting on.**

## The state of the brief's T2, stated plainly

The brief asked for `localDead_s07_t` and `localDead_s02_t` with **no hypothesis beyond the
certificate data**.  **That is NOT achieved in this attempt.**  What is achieved is the removal of
the obstacle that made it impossible, plus one of the four pieces:

* the **missing primitive** A126 named — "a certified rational-interval kernel for `cos`, `sin`
  and `π`, i.e. A119's `exactiv.py` in Lean" — **is no longer needed at all**.  In `t` the
  enclosures are exact rational arithmetic (`cosT_anti`, `sinT_mono`, `cosT_mem`, `sinT_mem`), the
  kink of `w` never has to be located (`wrel_ge_add`, `wrel_ge_sub`, `wrel_eq_max_of_cos_nonneg`),
  and every affine envelope reduces to one decidable rational test (`posCheck`, `posCheck_sound`);
* **(C1) the tilt cover is DISCHARGED**: `splitOk` / `splitOk_sound` / `coverOk` / `coverOk_sound`
  — a decidable well-formedness check on the certificate's own bisection tree, with the theorem
  that every point of the root cell lies in the recorded cell of some leaf;
* **(C2), (C3), (C4) remain**, and are now pure reflection work over rational data with no
  transcendental content anywhere.

Every theorem in `LocalCertT.lean` compiles with the axiom roster `[propext, Classical.choice,
Quot.sound]` — no `native_decide`, no project axiom, no `sorry` (audit:
`lean/PackingCertMathlib/scratch/A133Axioms.lean`, twelve theorems).  `lake build
PackingCertMathlib.LocalCertT` is **18.5 s** on top of the existing build.

## Priced: what (C2)–(C4) cost from here

The generator (`attempts/A133-tan-half-emission/code/gen_local_t.py`) is the specification; the
Lean side is its reflected twin plus one soundness theorem each.

| piece | what has to be written | consumes | size |
|---|---|---|---|
| **(C2) the selection cover** | a reflected `gapEnclosure : Cell → Sel → ℚ × ℚ` (the interval enclosure of `g_σ` over a cell: the exact `cosT`/`sinT` endpoint ranges of §1 times the centre-difference box, minus `1/2`, minus `w`'s exact range from §2), and `gapEnclosure_sound` — the true `gsel` lies in it.  Then `sup < 0` on the recorded excluded selections is a `decide`, and `SatInterior.sat_selection_thm` + `Local.cover_selection` finish the case split | §1, §2, `sat_selection_thm` (already a theorem) | ~250 lines; the only new mathematics is that a product of two intervals contains the product of two members, which is `mul_le_mul` bookkeeping |
| **(C3) Lemma RELAX** | a reflected row builder `rowsOf : Cell → Sel → List CRow` mirroring `RowsT._walls` / `RowsT._selection`, and `rowsOf_sound` — each row it builds is `≤ 0` at any configuration of the cell that satisfies the selection.  Six sub-lemmas: the `h` chord, the `S` enclosure, the two `w` branches (§2, done), the `corr` term, the `|Q|` chord (`Local.abs_chord`, already a theorem) and the two McCormick planes (`Local.mccormick_hi/lo`, already theorems).  Each envelope's validity arrives as a `posCheck` on the certificate's polynomial certificate — §3, done | §1–§3, `Local.abs_chord`, `Local.mccormick_hi/lo`, `Local.axis_decomp` | ~600 lines; the largest single item, and entirely mechanical once the envelopes are `posCheck`s |
| **(C4) the variable map** | `LocalHyp Ls Ps s z → ∃ x, x 0 = s ∧ InBox (rootBox) x 0`, i.e. `x_{vi} =` the free body's centre / the pin's offset from `α + β s`, `x_{ti} =` the free body's `t`.  Pure bookkeeping over `Box.mem` and `Pin.mem` | — | ~120 lines |
| **assembly** | `certCover_of_checks : (the decidable checks) = true → CertCover leaves Ls Ps slo shi`, then `localDead_s07_t := localDead_of_cert … (certCover_of_checks (by native_decide))` | all of the above + `LocalCert.localDead_of_cert` (already a theorem) | ~80 lines |

**Certificate-side cost of the assembly.**  The `posCheck` certificates are NOT in the emitted
`.tcert.json.gz` files yet — the certificate carries the envelope CONSTANTS (`env.h`, `env.S`,
`env.w`) and the Python checker verifies them by Sturm / Bernstein of its own.  Lean needs the
positivity certificate itself (the nonnegative coefficient list of
`Σ_k c_k (X − a)^k (b − X)^{n−k}`), which the generator can emit from the same Bernstein
computation it already performs: 4–5 rationals per univariate envelope and, for the bivariate `w`
bound, either a 4×4 grid per envelope or — cheaper and the recommended route — a reduction of the
two-variable test to two one-variable tests by first fixing the `t_o` endpoints (`W_ε` is affine
in nothing, but it is degree 2 in `t_o` with positive leading behaviour on the cell, so the
box-vertex + edge argument closes it).  Measured on the emitted files: S07 (0.1, 40°) has 378
envelope entries for 2 140 leaves, S02 (0.2, 10°) has 1 044 for 16 406 — envelopes are shared
across leaves by cell, so the added data is small next to the rows.

**Expected `native_decide` wall.**  A126 measured 22 s + 19 s for S07 (0.1, 40°)'s 2 302 leaves and
40 s + 67 s for S02 (0.2, 10°)'s 32 570 under `checkLeaf` alone.  A133's leaf counts are 2 140 and
16 406 — SMALLER (S02 by half) — and the added work per leaf is the envelope `posCheck`s
(a few dozen rational multiplications each) and the cover walk, both linear.  So the assembled
`localDead_s07_t` should replay in the same order: minutes, not hours.

## Why the `t` certificates are the right input for this

Three properties of the emitted files matter to the Lean side and none of them holds for A119's:

1. **every cell bound is a dyadic rational** (`2⁻²⁴` at the root, halved by each bisection), so
   the cover check is exact and `decide`-able;
2. **every row constant is a rational of those bounds**, with no `π` and no series anywhere in the
   derivation, so a row's validity is a polynomial statement;
3. **the tilt variable IS Lean's tilt variable.**  A119's LP tilt variable is the ANGLE, and
   relating `Box.t ∈ [t0, t1]` to `θ ∈ [θ0, θ1]` needs `arctan` — a transcendental step that would
   have sat between `LocalHyp` and the certificate no matter how good the trig kernel was.  In
   `t` that step is the identity.

Point 3 is the one that is easy to miss and is the real reason A126's Route A (formalise
`exactiv.py`) would not have finished the job on its own.
