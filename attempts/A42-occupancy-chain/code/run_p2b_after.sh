#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.."
until grep -q "P2A ALL DONE" logs/p2a_l2.log 2>/dev/null; do sleep 20; done
echo "=== P2B reseal starting ==="
python code/reseal_shat.py --iters 6 --target_scale 251/250 --jobs 3 --depth 50 \
       --deadline_h 3.0 --solver simplex
echo "=== P2B reseal loop done; scale scan on the last field ==="
LAST=$(ls -t results/p2b/certs/cert_a39_it*.json 2>/dev/null | grep -v report | grep -v witness | head -1)
if [ -n "$LAST" ]; then
  python code/seal_scan.py --cert "$LAST" --depth 50 --jobs 3 \
     --out results/p2b/seal_scan.json --sealed results/p2b/certs/A39_measure_feasible_3.877084.json
fi
echo "=== P2B ALL DONE ==="
