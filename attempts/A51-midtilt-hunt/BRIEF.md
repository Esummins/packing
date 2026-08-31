# A51 — mid-tilt flush-free basin hunt (Opus)

Goal: close A49's sampling caveat — the mid-tilt non-thin flush-free world was unsampled. Re-aim
the A49 machinery (attempts/A49-flushfree-hunt/code/: a49_common with the FIXED repair_ok,
hunt_a49, stratum_a49, audit_a49) with NEW SEEDS in the mid-tilt regime.

Seeds (design per A49 notes/seed_design.md conventions): flush-free 11-square configurations with
substantial common/mixed tilts: (i) perturbed atlas valleys with their flush contacts OPENED into
small-gap corner contacts (each genuine family, tilts intact); (ii) mid-tilt corner-contact
lattices (diamond-ish packings at 20-40 deg, corner-to-edge chains); (iii) A47's [45,0,45]-adjacent
structures fattened to non-thin; (iv) random flush-free mid-tilt feasible configs (rejection-sample
tilts in [15,45]). ~12-16 seed families x ~20 replicas, budget similar to A49 (~3 CPU-h).

Protocol identical to A49: free-descent census with feasible-path flush-acquisition tracking
(which contact flushes first, geometry at event), stratum-constrained descent + full-FJ tests,
strengthened audits (FJ stationarity + descent witness), negative controls, candidate pipeline
(A37 audit + Krawczyk) for anything surviving. Deliverables: run census (a/b/c), the mid-tilt
flush-acquisition map (compare against A49's wall-termination law — does it hold in this regime?),
candidates or zero, min s reached, gap list. <= 3 heavy processes; ONE long-poll waiter;
checkpoints; A29 untouched.
