#!/bin/bash
# A184 -- launch ONE run184 shard detached (nohup; BelowNormal + affinity set in-process), relaunched
# after a per-node wall kill until exit 0 (done) or 2 (PAUSE sentinel).  usage: launch184.sh <name> <args...>
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
name=$1; shift
for round in $(seq 0 40); do
  python -u run184.py "$@" >> "../logs/$name.log" 2>&1
  rc=$?
  echo "$name round $round exit $rc" >> "../logs/$name.launch"
  if [ "$rc" = "0" ] || [ "$rc" = "2" ]; then break; fi
  sleep 10
done
