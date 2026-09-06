# A61 PAUSED — 2026-09-06 00:36:42

PI directive (2026-09-06): pause long-running LP campaigns to free compute while A108/A109 test whether
node-level SLOT-CROWD rows and shadow basins change the tree's economics.

Stopped (taskkill /T /F): [2856, 3204, 31932, 2116] — campaign61.py (--heavy 2 --jobs 3, resumable off the per-name
RECORD files and results/campaign61_progress.json), resolve61.py for k5_05 and k6_21 (their in-flight LP/certify
rounds are lost; per-node results already on disk stand), and their certify child.
Progress file rows at pause: 4; started 2026-09-01T19:37:25.

Resume: `cd attempts/A61-window-stragglers/code; python -u campaign61.py --heavy 2 --jobs 3 --max_atoms 3500
--max_cols_add 800 --cert_rounds 6 --cert_time 420 --gate 0.30` (WITHOUT --restart, so it resumes), and the two
resolve61 commands as logged in logs/. Do not resume until the PI lifts the pause.
