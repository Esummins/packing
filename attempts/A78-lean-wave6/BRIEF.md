# A78 — Lean wave 6: census definition, the last prose, the small checkers, fixed-corpus replays (Fable lead)

You are the THEORY lead (Fable). PI end-state: every node gold, or blue with Lean-proved
verifier soundness AND its certificate corpus replayed. Read attempts/{A64,A68,A70,A75}-lean-
wave*/notes/findings.md first (toolchain recipes). Standing constraints: light CPU; cache hits
only on the isolated native_decide modules (never rebuild Measure382Check); A57/A60/A61/A76/
A77 untouched; depgraph shared (pull/merge; your owner chips are pre-set — clear each on landing).

## T1 — F11: the Lean census definition (unblocks FOUR nodes)
attempts/A72-census-cleanroom/notes/ambiguities.md lists the 8 binding choices (B1–B8) the
written Young-form definition leaves open; A68/A75 left `hface` (Skeleton.lean) and `hinc`
(Selection.lean) as the census interface axioms. Pin the definition in Lean (Census.lean):
simple square, Young slot-set, the D4 action (A67 R8 / d4_reduction_s0.md), exact-skeleton
class. Then COMPUTE the census in Lean (decide/native_decide over the 36-slot lattice) and
prove it equals the 1110/163 corpus (B.CENSUS -> lean-proved: census as a Lean theorem, doubly
witnessed by A53 + A72 already). Discharge hface/hinc => B.SEL, B.EXACT, C.CC2 -> lean-proved
(A75's Selection.lean + A68's Skeleton.lean are conditional only on these). Record each B-choice
resolution as a docstring so the Lean definition IS the authoritative Young-form definition.

## T2 — CIDL-LEAN: discharge shatA22_eq_shat (A.UBshat -> lean-proved)
attainment_ub.md §7.5 spec: native_decide replay of certs/cidl_identity.json's polynomial
identity + Sturm sign gates (verify_cidl.py is the reference; Measure382Check isolation pattern;
tiny coefficients — should be cheap). Then trump_packs_at_shat composes; the 12th axiom falls.

## T3 — the two small checkers (D.ALIVE, D.D4 -> verifier soundness in Lean)
alivewitness.py (D.ALIVE: exact disjoint-family bound tau* >= budget — the ALIVE-side arbiter)
and the D4 reduction check (D.D4, A67's verify_d4_s0.py over A27 verify_tree2 semantics). Each:
Lean checker port + soundness theorem stated as its consumer needs (alivewitness: "PASS => no
certificate of budget b exists for this node" — note this is a completeness-side arbiter, state
exactly what it proves; D4: the WLOG lemma, conditional on the s0 root occupancy per A67 §D4.4).
Set verifier_lean on both when landed.

## T4 — A.UNIQ own-tier: formalize the reduction (unique_transfer.md §)
The axiom-as-stated follows from census exhaustiveness (A63) — with T1's Census.lean in hand,
prove unique_transfer from stratify + the Theorem U certificate interface; own_tier -> lean-
proved (node stays blocked-only red until C.K4TIER closes — that is correct).

## T5 — fixed-corpus Lean replays (C8 for the corpora that are DONE)
Using A70's gen_case_lean.py / A75's gen_param_lean.py: replay in Lean every certificate of
C.K61 (61 pin-set kills), D.TRAP (6), D.P1 (1), A.THMU (11). Isolated per-corpus modules
(never rebuilt casually), one theorem per certificate, aggregated into one corpus theorem per
node, axiom audit listing exactly one native_decide axiom per certificate. Record wall time
per certificate (this prices the A57/A60 corpora replays later). Add "corpus_replayed": true
to those nodes. Do NOT replay C.A57/C.WIN corpora — still growing (A57 G1 / A61).

Deliverables: Lean files + CI green + audit after each landing; depgraph labels/flags + chips
cleared + re-render; docs/proofs annotations; notes/findings.md; registry row; LOG.md; terse.
Priority T1 > T2 > T5 > T3 > T4; honest partials with named obligations beat claimed closes.
