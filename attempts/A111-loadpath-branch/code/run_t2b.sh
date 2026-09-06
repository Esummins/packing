#!/bin/sh
# A111 T2, batches 2-4: S07 nodes; S02 contrast (supports NOT in the family); a LONG-LP re-solve of
# the nodes whose five children were all dead-but-unconverged at the 80 s cap; then the
# certification sample.  One process.
cd "$(dirname "$0")"
python -u t2_no.py --tag S07 --variant lpa --r 0.1 --rho 10 --limit 6 --inside any \
  --levels 1,2 --lp_time 80 --probe_time 80 --minutes 55 --shard 0 \
  --sink ../results/t2_runs_S07.jsonl
python -u t2_no.py --tag S02 --variant lpa --r 0.1 --rho 10 --limit 4 --inside no \
  --levels 1,2 --lp_time 80 --probe_time 80 --minutes 35 --shard 0 \
  --sink ../results/t2_runs_S02_outside.jsonl
python -u long_batch.py
python -u certify111.py --from_runs ../results/t2_runs_S02_inside.jsonl,../results/t2_runs_S02_long.jsonl,../results/t2_runs_S07.jsonl,../results/t2_runs_S02_outside.jsonl \
  --n 8 --rounds 1 --depth 56 --cert_time 240
echo "T2b done"
