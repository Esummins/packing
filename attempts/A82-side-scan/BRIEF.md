# A82 — side scan: where below s-hat do the protected classes become killable? (Opus, measurement)

PI question (2026-09-03): the protected k<=4 classes saturate at s0 because Trump's own square
family fits at every side >= s-hat (the aliveness witness). Below s-hat the family no longer
fits and the LP should gain slack ~ dtau/ds x (s-hat - m). MEASURE IT. This is a scan, not a
kill campaign.

Read first: attempts/A61-window-stragglers/code (resolve61.py — the side-parametrised case-LP
driver; A57 T19 memory trims are in), attempts/A56-sparametric/notes/soundness.md (window
semantics: pins at the side's OWN slots), attempts/A55-k4-sweep/ (the k4 class pin sets),
attempts/A65-low-k-closure/results/crowdfam.json + clique_caps.json (the alive witnesses at s0),
attempts/A57-shadow-trees/code/alivewitness.py (the ALIVE-side arbiter; note the quarantined
k5_16_m5.json lesson: unkillable needs m >= budget).

## The scan
Classes: k4_08, k4_11, k4_03, corners4 (k4_13), k3_00's protected neighbour k3_05, and k0_00.
Sides m in {3.82, 3.85, 3.86, 3.865, 3.87, 3.873, 3.875, 3.876, 3.8765, 3.877, 3.877083, s0}
(rationals; pins at m's slots). For each (class, m): (a) alive-gate: does a strictly separated
Trump-image family FIT at side m (alivewitness with the family compressed/relocated per the
standard normalisation)? report m_fam vs budget; (b) the conditioned case-LP tau(m) (column-
only warm starts across sides, descending; time cap 600 s/LP); (c) eta(m) = tau(m) - budget and
whether the A39 gate tau*1.005 < budget passes. Report the table + fitted dtau/ds per class +
the crossover side m* per class where eta <= -1 (the A60 certification law) and where the
A39 gate first passes. For ONE class at the first side that passes, EMIT + exactly verify a
certificate (verify_case.py, depth 60, corruption gates) to prove the scan's slack is real.

## Constraints
<= 2 LP slots (BLAS-pinned via an existing launch.ps1 pattern; commit headroom > 6 GB, wait
out dips); A57/A60/A61/A81 untouched; frozen verifiers untouched; certs/ new files only.
Writes inside attempts/A82-side-scan/ + registry row + LOG.md; depgraph: note on C.K4TIER
only (chip stays A81). Trump canary: at every side >= s-hat the family must fit and the LP
must saturate (if it does not, your normalisation is wrong — stop and report).

Deliverables: results/side_scan.json + a plain table in notes/; the one verified certificate;
registry row; LOG entry. Terse report: the crossover table first.
