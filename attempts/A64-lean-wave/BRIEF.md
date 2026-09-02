# A64 — Lean wave 2: parametrization, measure bridge, UB identity (Fable lead)

You are the THEORY lead (Fable). PI end-state: EVERY depgraph node proved-prose or better, with
logic/theory ultimately IN LEAN — lean/depgraph.json is the live scoreboard (update labels/notes
+ re-render lean/render_depgraph.py as you land things). Do the mathematics and Lean yourself;
Opus subagents only for mechanical chores. Do NOT touch the running campaigns (A57/A60/A61);
light CPU only (lake builds fine). Keep CI green; axiom audit clean after every change.

Read: lean/depgraph.json (your targets = A.PARAM, A.F2, A.UBshat), lean/PackingCertMathlib/
PackingCertMathlib/TopLevel.lean, lean/PackingCert/* (the 3.82 checker), docs/proofs/
{attainment_ub, closed_disjoint_bridge, theta_t_transfer}.md, attempts/A28-lean-batch/notes.md,
certs/octic_root_isolation.json + verify_sturm.py (T1 pattern to imitate), docs/specs/tcb.md.

## T1 — A.PARAM: the parametrization lemma (write it, then formalize it)
"Every packing is represented in (cx,cy,t), t in [0,1]": mod the square's symmetry group, every
unit-square placement has a representative with tilt in [0, 45deg], t = tan(theta/2) rational-
izing cos/sin; the certificate families quantify over exactly this domain. Elementary, never
written, load-bearing for EVERY certificate. Write docs/proofs/parametrization.md, then prove it
in Lean (TopLevel or a new file), discharging the `parametrize` axiom. This is the axiom whose
absence undermines everything else — do it first.

## T2 — A.F2: the measure bridge in Lean
The A28-estimated 3-5 day item: checker PASS => every unit square has mass >= 1 => no 11-packing
at that side. Target: `s_eleven_ge_382` as an end-to-end Lean theorem from checkMeasureI's
native_decide evaluation + the bridge, axioms only propext/Classical.choice/Quot.sound +
Lean.ofReduceBool. This upgrades the 3.82 paper's abstract from "Lean checks the checker" to
"Lean proves s(11) >= 3.82". Uses T1's lemma. If 5 days is wrong in either direction, say so
early rather than grinding silently.

## T3 — A.UBshat: close the algebraic identity
Residue per attainment_ub.md: shat_A22 = shat_octic, agreement pinned to 2.1e-47. Attempt the
exact number-field verification (the compositum <= 56 obstacle is recorded — assess whether a
resultant/interval-arithmetic argument at rational precision beats full number-field arithmetic:
the octic' >= 152.37 Taylor bound means agreement within 2.1e-47 + octic(shat_A22) interval
enclosure may suffice for a SIGN argument entirely in rationals). If genuinely blocked, execute
the S3-fallback restatement (shat := shat_A22) cleanly in TopLevel and document what changed.
Either way A.UBshat leaves "open".

## T4 — scoreboard hygiene
Add a "lean-proved" label tier (gold) to lean/depgraph.json + render_depgraph.py COLORS so the
PI can distinguish Lean-proved from prose-proved at a glance; recolor nodes you discharge
(and A.S3, already a Lean theorem). Update TopLevel axiom annotations; keep lean/README.md
matrix current.

## Deliverables
Lean files compiling + CI green; docs/proofs/parametrization.md; depgraph updated + re-rendered;
notes/findings.md for anything discovered; registry row; LOG.md. Honest partials with named
obligations beat claimed closes.
