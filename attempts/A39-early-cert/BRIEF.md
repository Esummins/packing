# A39 — certification-in-the-loop + field reseal (P2a + P2b, Opus lead)

Goal: measure whether A38's cost wall falls to two fixes. Context: attempts/A38-root-power/
results/rootpower_report.md (the NO-GO, levers L1/L2), notes/extrapolation_frame.md; the root
certified from an UNCONVERGED LP in 1.7 s (results/root_s0.json) while depth nodes waited forever
on convergence; 2/8 float kills evaporated under exact certification.

P2a — EARLY CERTIFICATION CALIBRATION. Invert A27's node rule: after EVERY row-generation round,
attempt the exact certificate (verify_case with witness feedback: holes become new LP rows); stop
on PASS (kill, certified) or budget. Re-run the A38 depth-2 stratified sample (results/l2_nodes/
checkpoints, warm-startable) + ~10 level-1 undecided under the new rule. Deliverable: decided
fraction + median time-to-decision vs the old rule's 0/60; the honest new (f_certified, b_eff,
cost/node) triple for the extrapolation frame. Also re-certify the 38 uncertified level-1 kill(LP)
nodes (A38 gap G1 debt) with the same loop.

P2b — RESEAL THE s-hat FIELD. A33 gap G5/G6: the certified field total is 11.4254 vs float truth
~11.243; the verifier-witness -> LP-row loop (A33 t2/refine_384.py pattern) should reclaim most of
the 0.18 margin. Target eta_cert <= 0.30, stretch 0.27. Then re-emit the W1 threshold and re-run
A38's c_core scan (results cached) to requantify W1's first-kill depth. Lab standards: every solve
a-posteriori verified; exact outward-rounded seal; checkpoints.

Report: the three numbers that re-run A38's GO/NO-GO arithmetic (decided fraction + cost, new
eta_cert, new W1 depth), plus honest failures. <= 4 heavy processes (sharing with A40). A29
untouched.
