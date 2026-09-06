#!/bin/sh
# A111 T2 driver: one process, three batches (S02 inside-family, S07, S02 contrast).
cd "$(dirname "$0")"
python -u t2_no.py --tag S02 --variant lpa --r 0.1 --rho 10 --limit 12 --inside yes \
  --levels 1,2 --lp_time 80 --probe_time 80 --minutes 95 --shard 0 \
  --sink ../results/t2_runs_S02_inside.jsonl
python -u t2_no.py --tag S07 --variant lpa --r 0.1 --rho 10 --limit 8 --inside any \
  --levels 1,2 --lp_time 80 --probe_time 80 --minutes 65 --shard 1 \
  --sink ../results/t2_runs_S07.jsonl
python -u t2_no.py --tag S02 --variant lpa --r 0.1 --rho 10 --limit 6 --inside no \
  --levels 1,2 --lp_time 80 --probe_time 80 --minutes 45 --shard 2 \
  --sink ../results/t2_runs_S02_outside.jsonl
echo "T2 all batches done"
