#!/bin/bash
# A238 -- the chain: wait for the k3_02 worker to drain its queue (it also carries the other protected-class roots),
# then put the freed slot on the BACK HALF of k4_11's queue, so the two pilots share the wall.
#   nohup bash attempts/A238-k4-benchmark/code/chain238.sh > attempts/A238-k4-benchmark/logs/chain238.log 2>&1 &
# Resume: each node's row in results/bench238.jsonl is the skip test, so re-running this script is always safe.
cd "$(dirname "$0")/../../.." || exit 1
A=attempts/A238-k4-benchmark
busy() { powershell -NoProfile -Command "(Get-CimInstance Win32_Process | Where-Object { \$_.CommandLine -like '*bench238.sh k3_02*' } | Measure-Object).Count" | tr -d '\r '; }
echo "$(date +%H:%M:%S) chain238: waiting for the k3_02 worker (busy=$(busy))"
while [ "$(busy)" != "0" ]; do sleep 60; [ -f $A/logs/STOP ] && { echo "STOP"; exit 0; } ; done
echo "$(date +%H:%M:%S) chain238: k3_02 drained -- starting the k4_11 back half"
exec bash $A/code/bench238.sh k4_11b 300
