# A40 — basin growth by selective boundary surgery (P1, Fable lead)

Goal: grow Trump's certified exclusion region from h = 3.7e-3 toward h ~ 0.03 (the top-down
depth-2/3 cell scale) by branching ONLY the binding rows. Context: attempts/A36-levers/ (the
composed certificate, kappa_eff max-form pinning, L1 over-estimate lemma — any-corner rows are
valid WITHOUT dominance; results/a36_reach.json has the per-row margin data), A35 notes/theory.md,
A37 cookbook (row [V]-validity |t| < 1/2 rule).

T1 (theory, yours): the SURGERY LEMMA — when a row's tangential/[V] validity margin binds at
radius h, split the region along that pair's corner-dominance boundary into 2-4 branches, each
with its own valid selection (over-estimate lemma makes each branch's rows sound); certificates
compose over the branch tree. Handle gained-contact pairs the same way (their rows are valid
inequalities; add to the basis with omega optimized, branch only if their selection validity
binds). State the composed theorem form: sigma >= s-hat on the UNION of branch regions.

T2 (measurement loop): iterate — measure margins at current h; surgery on the 1-2 binding rows;
re-optimize omega/kappa_eff per branch; certify (IV + corruption-gated re-checker per lab
standard); grow h; log the surgery tree. Targets: h = 0.01 (checkpoint), 0.02, 0.03 (goal).
Report the growth curve h vs (branches, total certs, wall time), the binding-constraint sequence,
and where it genuinely saturates if it does. Honest NO at some h is a success — name the
constraint. Budget: analysis-first; compute is seconds-per-certificate; <= 2 heavy processes.
Opus subagents for emission/verification runs only. A29 untouched.
