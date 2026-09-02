# A75 — Lean wave 5: the remaining green prose lemmas -> gold (Fable lead)

You are the THEORY lead (Fable). PI end-state: every node lean-proved or certificate+verifier
(with Lean-proved verifier soundness). This wave takes the remaining proved-prose (green) nodes
to Lean. Read attempts/{A64,A68,A70}-lean-wave*/notes/findings.md FIRST (the cross-toolchain
elaboration recipe + the toolchain renames + "name every checker subcomputation as a top-level
def; core Rat crosses the Mathlib boundary friction-free"). Standing constraints: light CPU
(lake builds fine; NEVER re-run the isolated 2380s Measure382Check or the case native_decide
modules — cache hits only); do not touch A57/A60/A61/A74 campaigns; depgraph shared (pull/merge;
set owner chip A75 on nodes you take, clear on landing).

Targets (all proved-prose today), priority order:

## T1 — V.MEAS + V.PARAM: the two remaining verifier-soundness nodes
These are the highest-leverage greens: making a V.* node gold Lean-backs every blue node that
consumes it (the PI's blue-accent distinction). V.MEAS: verify_measure.py soundness — the Lean
checkMeasureI soundness is ALREADY proved in A.F2 (MeasureBridge.lean); this node is the Python
verifier's equivalence to it. State and prove the bridge (or if A.F2 already subsumes it,
mark V.MEAS lean-proved with the pointer and note what the Python impl adds = the second-
implementation/C3 witness). V.PARAM: verify_param.py soundness (P0-P7) — imports the audited
A53 integer core; the new predicates are point->interval widenings. Formalize the soundness
theorem the way C.WIN consumes it (this unlocks C.WIN's gold verifier accent).

## T2 — B.SEL, B.EXACT: the stratification-layer prose
B.SEL (selection: a k-maximal slide-stuck minimiser exists) — H1, with the degenerate slide
cases the checklist flags (mid-slide contact, ties, sigma-changing slides): formalize the
STATEMENT and as much of the proof as lands; the degenerate-case audit is itself a finding.
B.EXACT (exact-skeleton vs pin-monotone bridge) — A63 closed it for the certified part;
formalize (reflexivity + D4 bookkeeping + the certificate's monotone form is stronger).

## T3 — the remaining trump5/kill prose (as time allows)
C.T5T11 (logic-kill rules T5/T11 + pinguard), C.CC2 (teleport lemma), C.M1 (single-corner
transfer), D.N1 (zone-assignment collapse). Each is a self-contained lemma; formalize
statement + proof, discharge/annotate the axiom. Honest partials with named obligations beat
claimed closes — a wave that lands T1 clean (both V.* nodes) is already a full success because
it Lean-backs the whole certificate layer.

## Deliverables
Lean files + CI green + axiom audit after each landing; depgraph labels gold + verifier_lean
flags set on newly-Lean-backed blues (C.WIN when V.PARAM lands) + re-render; prose annotations
where Lean exposes gaps; notes/findings.md; registry row; LOG.md; terse. Report verdict per
node.
