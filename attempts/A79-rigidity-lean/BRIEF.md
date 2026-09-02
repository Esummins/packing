# A79 — the rigidity replay in Lean: rungs (b) and (c) (Fable lead)

You are the THEORY lead (Fable). PI priority (stated 2026-09-02): the basin theorem E.A36 is
the terminator of both remaining fronts (trump5 residual discharge + the protected-tier basin
exclusion) and must be Lean-backed. A70 landed rung (a): exact-rational, stdlib-only re-
verification of the A22 Krawczyk chain (a22_recheck_exact.py, 1.5 s) and all 17 A36 basin
certificates (a36_check_exact.py, 339/339 checks, 10.8 s) — mpmath.iv is off the decision
path. Rungs (b)/(c) are the Lean replay. Read attempts/A70-lean-wave4/notes/findings.md FIRST
(rung (a) design: dyadic outward-rounded intervals + certified alternating-Taylor cos/sin
enclosures in the THETA frame — no t-reparametrisation was needed; the cross-toolchain recipe;
"name every checker subcomputation as a top-level def"), then A22's certificate format
(docs/specs/rigidity_krawczyk_certificate_v1.md), A36's basin statement, ThetaT.lean (A68) and
TopLevel.lean's `basin` axiom + rBasin gates.

Constraints: light CPU (lake builds; isolated native_decide modules, cache hits only elsewhere);
A57/A60/A61/A76/A77 untouched; frozen Python verifiers untouched; rBasin = 3/2000 and the
E.COORD gates must NOT change (A60's landing budgets are calibrated on them); depgraph shared
(chips pre-set on E.A22/E.A36 — clear on landing).

## Rung (b) — E.A22: Krawczyk uniqueness + feasibility in Lean
Lean port of a22_recheck_exact.py's decision core (interval Newton/Krawczyk contraction K(X) ⊂
int X over dyadic rationals; certified Taylor enclosures of cos/sin — reuse A64's rational-trig
monotonicity lemmas + A68's cosT/sinT ties where the theta frame needs them) + the soundness
theorem: PASS => a unique contact solution z-hat in the box, feasible, sigma(z-hat) = shatA22.
Then native_decide on the A22 certificate (isolated module). Discharges the shatA22 /
trump_packs_at_shatA22 axioms' certificate half (the identity shatA22 = shat is A78's CIDL-LEAN).

## Rung (c) — E.A36: the basin inequality in Lean
Lean port of a36_check_exact.py's decision core + soundness: PASS over the 17 certificates =>
sigma >= shat on box(z-hat, rBasin) with equality only at z-hat (all break sets, both FJ
branches, stratum-blind, per A36). native_decide replay of all 17 (isolated module; record wall
time). Discharges the `basin` axiom. This is the PI's named priority.

## Deliverables
Rigidity.lean (+ data modules) compiling, CI green, axiom audit (exactly one native_decide
axiom per certificate replay); E.A22/E.A36 -> lean-proved (label) with the Python exact
recheckers recorded as the second implementation (C3); E.IV node note: dependency now absent
at BOTH tiers; TopLevel axiom roster updated; lean/README.md matrix; notes/findings.md;
registry row; LOG.md; terse. Honest partial = rung (b) landed with rung (c)'s obligation named.
