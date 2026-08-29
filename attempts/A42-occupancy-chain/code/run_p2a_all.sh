#!/usr/bin/env bash
# A39 P2a: run the three stages back to back (single process chain; memory budget ~3 GB).
set -u
cd "$(dirname "$0")/.."
echo "=== l2 stage B (48 nodes, warm, cap 180 s) ==="
python code/p2a_run.py --pop l2 --stage B --workers 3 --jobs 1 --time_limit 180
echo "=== l1u stage B (10 nodes, warm, cap 480 s) ==="
python code/p2a_run.py --pop l1u --stage B --workers 3 --jobs 1 --n 10 --time_limit 480
echo "=== l2 stage C (cold, from scratch, cap 480 s) ==="
python code/p2a_run.py --pop l2 --stage C --workers 3 --jobs 1 --time_limit 480 --n_cold 6
echo "=== P2A ALL DONE ==="
