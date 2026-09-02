# A69 — close shatA22_eq_shat: the (c-idl) cofactor certificate campaign (Fable lead)

You are the THEORY lead (Fable). The ENTIRE open residue of the upper bound at s-hat is one Lean
axiom: shatA22_eq_shat (TopLevel.lean, post-A64 split). A64 specced the closure route (c-idl) in
docs/proofs/attainment_ub.md — read it first, plus attempts/A64-lean-wave/notes/findings.md and
attempts/A22-local-rigidity/ (the contact system F, the enclosure z0/r0, the degree-7 coordinate).

## The task
Find and exactly verify the saturated ideal-membership certificate:
  h * octic(s) = sum_k q_k * F_k + sum_i r_i * trig_i,   h(z-hat) != 0
where F_k are the A22 contact-system polynomials (tan-half cleared), trig_i the c_i^2+s_i^2-1
relations, and the sign gate certifies h(z-hat) != 0 from the A22 interval enclosure. A PASS
proves the A22 contact solution's side satisfies the octic, i.e. shatA22 = shat given A.S3's
root isolation (state the composition precisely — which root, why the enclosure picks the second).

Search: bounded Groebner/Macaulay campaign (sympy exact rationals; or msolve/macaulay2 if
installable without disturbing the machine — ask nothing of the running campaigns; 2 processes
max, BLAS-pinned, commit headroom > 6 GB). Practical route: eliminate to the s-coordinate by
resultants/triangular elimination along the contact graph rather than one monolithic basis —
A22's system is structured (a chain of contacts); exploit it. Degree/height budgets: record them;
if the certificate explodes, STOP at a measured wall and report the size law — a decisively
priced NO beats an open-ended grind (the S3-fallback restatement remains the safety net, so this
attempt can afford an honest failure).

Verification: a small standalone checker in the verify_sturm.py style (exact rationals, stdlib
only, corruption gates), certs/ new files only. Then Lean: if feasible, discharge shatA22_eq_shat
by native_decide on the checker (imitate A64's Measure382Check isolation pattern; heed the
cross-toolchain elaboration recipe); if the Lean replay is too heavy this attempt, land the
certificate + Python checker and leave the Lean wiring as a named obligation.

## Deliverables
certs/cidl_* + checker + corruption gates; docs/proofs/attainment_ub.md updated with the found
certificate (or the measured wall); TopLevel updated if discharged; depgraph A.UBshat updated
(owner A69 while running); registry row; LOG.md; terse.
