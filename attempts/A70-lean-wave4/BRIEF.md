# A70 — Lean wave 4: V.CASE soundness, then the A22/A36 rigidity replay (Fable lead)

You are the THEORY lead (Fable). PI-directed priority: (1) V.CASE — the case-LP verifier
soundness — then (2) E.A36/E.A22 — the rigidity chain replayed in Lean — AHEAD of everything
else (CIDL-LEAN and the A.UNIQ derivation wait). Rationale: the basin theorem is the terminator
for both remaining fronts (trump5 residual discharge AND the new basin-exclusion row for the
protected classes), and it is the one node whose trust chain runs through a third-party library
(mpmath.iv). Read attempts/A64-lean-wave/notes/findings.md (cross-toolchain recipe) and
attempts/A68-lean-wave3/notes/findings.md (renames, fun_prop tags) FIRST.

Standing constraints: light CPU (lake builds fine; NEVER re-run the isolated 2380s
Measure382Check module); do not touch A57/A60/A61 campaigns; frozen Python verifiers never
modified; lean/depgraph.json is shared — pull/merge before push, update labels/owner chips as
you land.

## T1 — V.CASE: formalize case-LP certificate soundness (the tree-deciding verifier)
Target: the analogue of A64's MeasureBridge for verify_case.py — a Lean checker (byte-faithful
port of the decision core) + the soundness theorem "checker PASS => no 11-packing satisfies the
certificate's pin hypotheses at its side" — stated the way stratum_kill consumes it, with the
A68 Dilation.lean pricing pigeonhole supplying the (P2) interface (A68 named exactly this
residue: (P2) from a concrete PASS file). Scope honestly: the case checker adds cores/exemptions
/nofams/pinguard semantics over the measure checker. docs/specs/case_lp_certificate_v1.md is
the frozen spec; where code and spec disagree, that is a FINDING. A full formal soundness proof
+ ONE certificate replayed end-to-end (pick a small k5 pin-set cert) = success; the corpus-wide
replay is a later, separately-priced wave.

## T2 — E.A36 (with E.A22): the rigidity replay, t-parametrized
The known F6 blocker was interval trigonometry; the cure is the lab's own tan-half
parametrization (cos/sin rational in t — A68's ThetaT.lean has cosT/sinT formally tied to
cos/sin(2 arctan t), and A69 proved every zhat coordinate lies in Q(t-hat), degree 8, with the
minimal polynomial derived). Plan of attack: re-emit the Krawczyk/basin verification over
rational t-intervals (exact rational arithmetic — no mpmath), as a Lean-checkable computation
(native_decide, Measure382Check isolation pattern). Deliverables laddered by value: (a) the
t-parametrized re-verification running in exact Python (removes mpmath.iv from the TCB even
before Lean); (b) the A22 uniqueness/feasibility replay in Lean; (c) the A36 basin inequality
replay in Lean (sigma >= shat on the box, equality only at zhat). Each rung that lands flips
real trust; name what remains after each. Interfaces: keep rBasin = 3/2000 and the E.COORD
gates exactly as TopLevel states them; coordinate with A60's landing budgets (do NOT change
rBasin).

## Deliverables
Lean files + CI green + axiom audit after each landing; depgraph updates (V.CASE gold when T1
lands; E.A36/E.A22 tier upgrades per rung; owner chips A70 while working, cleared on close);
docs/proofs annotations where Lean exposes prose gaps; notes/findings.md; registry row; LOG.md;
terse. Honest partials with named obligations beat claimed closes — T1 alone landing clean is a
successful attempt.
