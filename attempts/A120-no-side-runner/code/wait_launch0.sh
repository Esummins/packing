#!/bin/sh
# wait for the single-node pilot (shard 0/1) to exit, then start the real shard 0/2 worker.
cd "$(dirname "$0")"
for i in $(seq 1 720); do
  if ! grep -q "shard 0 done" ../logs/run_shard0.log 2>/dev/null; then
    sleep 20
  else
    break
  fi
done
export PYTHONDONTWRITEBYTECODE=1
exec python noside120.py --shard 0/2 --cpu_cap 23000 --node_wall 5400 --cert_time 300
