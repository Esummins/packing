#!/bin/bash
# A238 -- the chain: wait for the k3_02 worker to drain its queue (that queue also carries the other protected-class
# roots), then put the freed slot on the BACK HALF of k4_11's queue, so the two pilots share the wall.
#
#   nohup bash attempts/A238-k4-benchmark/code/chain238.sh > attempts/A238-k4-benchmark/logs/chain238.log 2>&1 &
#
# RESUME: each node's row in results/bench238.jsonl is the skip test, so re-running this script (or either worker)
# is always safe and always picks up where it stopped.  `touch logs/STOP` stops the chain and both workers.
# Never touches the k5 frontier workers, the frontier loop, or A211 / A212 / A100's certs and results.
cd "$(dirname "$0")/../../.." || exit 1
A=attempts/A238-k4-benchmark
echo "$(date +%H:%M:%S) chain238: waiting for 'queue drained' in logs/bench_k3_02.log"
while ! grep -q "queue drained" $A/logs/bench_k3_02.log 2>/dev/null; do
  sleep 60
  if [ -f $A/logs/STOP ]; then echo "$(date +%H:%M:%S) STOP present: exiting"; exit 0; fi
done
echo "$(date +%H:%M:%S) chain238: k3_02 drained -- starting the k4_11 back half (queue_k4_11b.txt)"
exec bash $A/code/bench238.sh k4_11b 300
