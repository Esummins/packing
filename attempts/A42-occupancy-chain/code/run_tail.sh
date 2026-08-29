#!/usr/bin/env bash
# A39 tail chain: long-limit calibration probe (A38-G7), then the P2b reseal, then the seal scan.
set -u
cd "$(dirname "$0")/.."
until grep -q "P2A ALL DONE" logs/p2a_l2.log 2>/dev/null; do sleep 20; done
echo "=== LONG-LIMIT probe (A38-G7): 1 depth-2 node, 1800 s cap, warm (runs beside P2b) ==="
nohup python code/p2a_run.py --pop l2 --stage B --workers 1 --jobs 1 --time_limit 1800 \
   --suffix _long --only l2_p61_000 > logs/p2a_long.log 2>&1 &
echo "=== P2B reseal ==="
python code/reseal_shat.py --iters 5 --target_scale 251/250 --jobs 3 --depth 50 \
       --deadline_h 1.75 --solver simplex
echo "=== P2B seal scan on the last field ==="
LAST=$(ls -t results/p2b/certs/cert_a39_it*.json 2>/dev/null | grep -v report | grep -v witness | head -1)
if [ -n "$LAST" ]; then
  python code/seal_scan.py --cert "$LAST" --depth 50 --jobs 3 \
     --out results/p2b/seal_scan.json --sealed results/p2b/certs/A39_measure_feasible_3.877084.json
fi
echo "=== A39 TAIL ALL DONE ==="
