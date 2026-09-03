# A85 compute chore B — design note (verbatim task text)

Header: written by the Opus compute chore B agent for attempt A85 (repo C:\Users\esumm\code\packing;
lead = Fable theory lead) before starting work, per the lead's instruction. Two jobs: (1) targeted
k0 critical-point search reusing A04's local optimiser, (2) an A37 atlas containment tool.
Budget < 1 CPU-hour, single process, BLAS pinned to 1 thread. Work confined to
attempts/A85-k0-route/. No LP solves. Verbatim task text follows.

---

You are the Opus compute chore B for attempt A85 (repo C:\Users\esumm\code\packing; lead = Fable
theory lead). Terse, no emojis. Two jobs, both cheap (target < 1 CPU-hour total, single process,
BLAS pinned to 1 thread via env OMP_NUM_THREADS=1 / OPENBLAS_NUM_THREADS=1 / MKL_NUM_THREADS=1 set
before numpy import). Work ONLY inside attempts/A85-k0-route/ (code/, results/, notes/, logs/);
never modify anything under attempts/A04-*, A37-*, A57-*, A60-*, A61-*; copy what you need from A04
into attempts/A85-k0-route/code/cp85.py. No LP solves. Save this task text as
attempts/A85-k0-route/notes/cp_design.md with a short header before starting.

Constants: s-hat = 3.877083590022814 (Trump's side), s0 = 969271/250000 = 3.877084. Trump's
placements: attempts/A03-upper-reconstruct/trump11_float.json (X = 11 rows (cx, cy, theta_rad)).
Square = unit square, centre (cx, cy), tilt theta; container [0, s]^2. A packing has k = 0 ("k0_00")
iff NO square is axis-aligned at a census slot — for this job use the operational test: no square
with tilt within 1e-6 of a multiple of 90 degrees whose centre is within 1e-6 of a corner slot
(1/2, 1/2), (s-1/2, 1/2), (1/2, s-1/2), (s-1/2, s-1/2) (a "flush corner square"). Report the
stricter count too (any axis-aligned square at all).

JOB 1 — targeted k0 critical-point search with A04's local optimiser. Read
attempts/A04-upper-search/driver.py (local_opt, try_slsqp, perturb, bh_chain) and fsbh.py
(fixed_s_local, kick) and reuse their objective/penalty/relaxation code by copying into cp85.py (do
not import across attempts if that executes their main; importing functions is fine if side-effect
free). Seeds (all D4-symmetric where stated): (a) "V-crowder" seeds: at each of the four corners two
tilted unit squares both meeting the open corner box [0,1]^2 (corner frame), in mixed-sign (one at
+theta, one at -theta ~ 25-40 deg) and same-sign variants, plus 3 squares in the middle; (b) Trump's
packing rotated rigidly by +-2, +-5, +-10 degrees about the centre and re-fitted (min enclosing
side), then relaxed; (c) each A04 catalogue family (attempts/A04-upper-search/families_catalogue.json;
also local_optima.json) as a seed, and the 4 non-catalogue attractors of A37
(attempts/A37-cp-atlas/results/atlas_final.json entries whose family_id/notes mark them NEW) — read
their coordinates from the cert files A37-cp-atlas/results/certs/fam*.json (z_center). For every
seed run the free-side local optimiser (minimise side subject to no overlap, as A04 does), several
restarts with small structural perturbations, and KEEP only optima with k = 0 by the operational
test. Also run the optimiser with an explicit k0 penalty/constraint variant (e.g. penalise any
square whose centre is within 0.02 of a corner slot AND tilt within 2 degrees of axis-aligned) to
force k0 structures, then re-relax without the penalty and re-test k = 0. Output
results/cp85_k0_search.json: every distinct k0 optimum (dedupe by side at 1e-6 + D4 alignment), its
side, its tilt list, its contact graph summary (pairs/walls within 1e-6), its distance to the
nearest Trump image (min over the 8 D4 images and square relabellings of the max coordinate
deviation), and whether it lies in an atlas box (JOB 2 tool). HEADLINE numbers: the best (smallest
side) k0 optimum found; whether it is a rigid rotation of Trump (side > s-hat by O(angle)), an atlas
family, or NEW (side < 3.9 and not matching any atlas/catalogue family); the smallest side of a k0
optimum that is NOT a Trump rotation.

JOB 2 — atlas containment tool code/atlas85.py: load attempts/A37-cp-atlas/results/atlas_final.json
(37 entries; each entry has h_certified (rational) and cert_path relative to attempts/; the cert
file has z_center = the box centre, and the claim: every feasible 11-square configuration z with
||z - z_center||_inf <= h_certified has sigma(z) >= V where V >= s0). Determine and DOCUMENT (from
the cert files and attempts/A37-cp-atlas/notes/cookbook.md / code/a37_check.py) the exact coordinate
convention of z_center (order of squares, centre coords, tilt in theta radians or t = tan(theta/2),
which D4 normalisation, whether the box is in the [0,s]^2 frame of the CP's own side or normalised)
— this matters and must be stated precisely in results/atlas85_convention.md. Provide function
in_atlas(placements) -> list of (entry, margin) for a family of 11 (cx, cy, theta) in [0, s0]^2 that
tries all D4 images and all square relabellings that respect the entry's structure (Hungarian
assignment on centres per D4 image is fine), returning the max over images/relabellings of
(h_certified - ||z - z_center||_inf) with the tilt coordinate compared in the entry's own convention
(if the entry is in t = tan(theta/2) coordinates, convert theta -> t; note E.COORD's X.1:
|dt| <= |dtheta| <= 2|dt| on [0, 45 deg]). Test: Trump's own placements must land in entry
family_id 0 (margin = h_certified minus ~0); each of the 4 A37-NEW centres must land in its own
entry with margin = h. Write results/atlas85_selftest.json. Then evaluate the JOB 1 optima with it.

Report to the lead: the headline numbers of JOB 1, the atlas convention in two lines, selftest
verdicts, file paths. Nothing else.
