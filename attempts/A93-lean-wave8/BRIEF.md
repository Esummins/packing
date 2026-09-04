# A93 — Lean wave 8: the k0 composition and its lemmas (Fable lead)

You are the THEORY lead (Fable) for Lean. The proof plan for k0_00 was re-based on 2026-09-03 (A92,
docs/proofs/k0_blocked_side.md; depgraph row "k0_00 residue reduction"): k0_00 = K0-FREE (teleport,
C.CC2 already Lean) + a chain of crowd-weighted certificates C(delta, m_lo) (Lemma CW, each checked by
TWO runs of the frozen verify_case.py whose soundness is V.CASE, Lean-proved) + Lemma SLIDE (a nick
costs its depth in side) => s(11) >= s-hat - delta_inf, with residue the shell RES-N. Everything on
this path that is prose must become Lean now, so that when the LP sweep lands the only remaining step
is certificate replay. Read first: docs/proofs/k0_blocked_side.md (CEIL, CW, B-YES, SLIDE, Theorem N,
RES-N), docs/proofs/nocrit_k0_blocked.md (Lemma CLUSTER: rows affine in centres => cluster translation
is an exact packing; Lemma K), docs/proofs/k0_route.md (K0-FREE), attempts/{A64,A68,A70,A75,A78,A79,
A86}-*/notes/findings.md (toolchain recipes; isolated native_decide modules; Composition.lean),
lean/PackingCertMathlib/PackingCertMathlib/{TopLevel,Selection,Census,CaseChecker,CaseBridge,
Composition,Dilation,Zones}.lean. Standing constraints: light CPU (one lake build at a time, cache-hit
isolated modules only); never touch A57/A60/A61/A92 state; depgraph shared (pull/merge; note-only on
K0.* nodes, chips stay with A92).

## T1 — Lemma CW soundness (the certificate composition)
Theorem `crowd_sound`: if run A (checkCaseI with n = 11 + 8e on the plain measure) and run B (the
measure scaled by 1/(1+e) with the complement of the crowd family exempt) both PASS, then no packing of
11 unit squares at the certificate's side has, at every corner, two squares meeting the widened corner
box [0, a_w]^2. State the crowd hypothesis exactly (open-slot intrusion at depth >= delta, transported
to the widened box by Lemma B-YES with its pad), prove the weight arithmetic (sum over 11 squares of
mu >= 11 + 8e when 8 squares carry the extra e; contradiction with total < 11 + 8e), and connect to
CaseBridge's existing "PASS => no packing satisfies the hypothesis" theorem. Isolated native_decide
replay of the first passing certificate when A92's chore delivers it (attempts/A92-blocked-side/certs/).

## T2 — Lemma SLIDE
Formalise: (a) the retreat clusters (A90 Lemma CLUSTER, affine rows) — translating a cluster by t along
a diagonal direction keeps all pair constraints and the container constraints when the container is
enlarged accordingly; (b) the depth bookkeeping (depth rate 1/sqrt2 per 1/sqrt2 of side; clusters only
enlarge, at most 10 times); (c) the conclusion: from a K0-BLOCKED packing at side m one obtains a
packing at side m + sum of nick depths that is K0-FREE, hence (by C.CC2 teleport) has a simple square
=> lies in a k >= 1 stratum. Leave "k1_00 excluded below s-hat" (K0-O1) as the named hypothesis it is.
If (b)'s constant needs a computation, isolate it as a decidable check.

## T3 — Theorem CEIL
Pure planar geometry: two interior-disjoint unit squares in a corner quadrant satisfy
max(mu_A, mu_B) >= 1/(cos a + sin a) >= 1/sqrt2 (Wedge Lemma + separating line). Prove it in Lean over
the real plane with the lab's square representation (Skeleton/ThetaT conventions). It is consumed only
as motivation by the plan, but it is short, self-contained, and the paper's cleanest new geometric
lemma; do it after T1/T2.

## T4 — Theorem N composition and the TopLevel roster
Compose in Composition.lean: `k0_kill_of_chain` — given a list of passing crowd certificates
C(delta_i, m_i) covering [3.82, s-hat - delta_inf] (Lemma B-YES transport per slab, Theorem N's
chaining), SLIDE, and K0-FREE, conclude: every packing in k0_00 at side < s-hat - delta_inf is
excluded. State the residue RES-N as a named hypothesis (`k0_shell_kill delta_inf`) feeding
`stratum_kill`'s k0_00 piece, and write the TopLevel roster note: what stratum_kill now reduces to
(protected k<=4 trees per A86 T3 + K0 chain + k0_shell_kill), what trump_residual reduces to, and the
replay obligations with the T5 cost table.

Deliverables: Lean files + CI green + axiom audit (propext/choice/Quot.sound + native_decide only),
lean/README.md, depgraph notes on K0.CW/K0.SLIDE/K0.CEIL/K0.RESN ("Lean: ..."), registry row, LOG.md,
findings. Honest partials with named obligations beat claimed closes; T1 + T4 landing clean is a full
success. Wake only on terminal events; report tersely: which of T1-T4 are Lean theorems, the roster
note, pointers.
