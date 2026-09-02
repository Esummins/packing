# A83 — the contraction tube: an anisotropic basin along the dilation ray (Fable lead)

You are the THEORY lead (Fable). PI idea (2026-09-03): grow the basin SELECTIVELY toward the
"smaller" solution space so it covers more of the dilated configurations that regime 2 of the
proof needs. Context (the seam): sides m <= s-hat - delta_LP are killed by plain certificates
(A82 measuring delta_LP ~ 2e-3 (k4_08) .. 5e-3 (k4_11), unconverged); sides m in (s-hat -
delta_LP, s-hat) are handled by the s0 residual tree + dilation + basin, which reaches down only
delta_basin = the extent to which the basin covers the CONTRACTED Trump configurations
z-hat - t*c-hat/s-hat (dilation is a pure centre scaling, tilts fixed). Uniform rBasin gives a
few e-4; A36 per-coordinate ~3.7e-3; A40 ~6.5e-3 (a40_check_exact.py, A76). The proof closes
iff delta_basin >= delta_LP. Make delta_basin large and robust.

Read first: docs/proofs/{theta_t_transfer,closed_disjoint_bridge}.md (dilation displacement
(lambda-1)*|c|; the shell bound), A36's basin construction + attempts/A70-lean-wave4/code/
a36_check_exact.py + attempts/A76-grain-discharge/code/a40_check_exact.py (exact certifiers —
the tube certificate should be a NEW certificate consumed by the same style of checker),
lean/PackingCertMathlib/PackingCertMathlib/RigidA36.lean + RigidBasin*.lean (A79: second-order
Taylor along segments with interval Hessian, quadratic dichotomy, FJ branches — the tube must
be certifiable by the same argument in (t, w) coordinates), attempts/A22-local-rigidity (Farkas
first-order certificate: positive multipliers on loaded contacts — the reason contraction is
the FAVOURABLE direction: it compresses every contact rather than breaking one; A76's hinge
wall is about BREAKING contacts), attempts/A60-trump5-campaign/notes/{ledger,resume_plan}.md
(the (D) leaves and D.S6 budget that consume the basin), A82 results/ (the crossovers).

## T1 — the tube theorem (statement + certificate)
Tube(T, r) = { z-hat - t*c-hat/s-hat + w : t in [0, T], |w|_inf <= r } (centres contracted
along the ray by t, tilts perturbed only through w). Theorem: every PACKING in Tube(T, r) has
sigma >= s-hat, equality only at z-hat. Certify it exactly with the A36 machinery re-based on
(t, w) coordinates (segments from z-hat into the tube; interval Hessian over the tube; FJ
branches at contact breaks — but note along the ray no contact breaks: state and prove the
"compression lemma" that all Trump contacts have negative slack for t > 0, so the only branching
is in w). Deliver: the largest T certifiable at r = the landing width A60 needs (its (D) boxes
land at ~1.45e-3 centre / 1.14e-3 tilt, so r >= ~1.6e-3 with widening), and the (T, r) trade-off
curve. Target: T >= 1e-2 (comfortably above any A82 crossover). Exact certificate + stdlib
checker + corruption gates (certs/tube_*, verify_tube.py). Canary: z-hat is the unique equality
point; the tube must never certify a contracted configuration as a packing.

## T2 — the seam lemma
Lemma SEAM: for every side m in [s-hat - T', s-hat], every packing of side m in a stratum whose
s0 residual tree terminates in (K)/(D) leaves is excluded: (K) by Lemma B dilation with slack
cores (state the slack needed), (D) by Tube(T, r) with T' = the side-shell that the tube's T
covers (work out the exact map m -> t: the dilated configuration lies in the (D) box; the
undilated one lies in the tube at t = (1 - m/s0)*|c-hat|/s-hat-ish — do this exactly, per
coordinate, incl. the D4/relabelling bookkeeping A60 fixed for D.S6). Then the seam condition
T' >= delta_LP is a comparison of two measured numbers; state it as the composition obligation
for trump5 AND the protected classes (with Theorem U replacing the basin at their (D) leaves —
say exactly what the tube version of Theorem U needs).

## T3 — Lean-readiness note
The tube is the A36 argument in new coordinates; write the obligation for A79's RigidBasin
machinery (what changes: the box parametrisation, the compression lemma, the segment family)
so the next rigidity wave can formalize it without redesign. Do not touch lean/ beyond notes.

Constraints: <= 2 compute slots (the certifier is CPU, no LP), BLAS-pinned, headroom > 6 GB;
A57/A60/A61/A81/A82 untouched; frozen verifiers untouched; certs/ new files only; depgraph:
note on D.SLAB (owner stays A60) + E.A36 (note only); registry row; LOG.md; notes/findings.md
(fallback: put findings in docs/proofs/contraction_tube.md §6 if the harness blocks notes/).
Deliverables: docs/proofs/contraction_tube.md, certs/tube_* + verify_tube.py, the (T, r) curve,
Lemma SEAM with the exact m -> t map, the Lean obligation note. A measured wall (T saturates
below the crossover, with the binding contact named) is a full success.
