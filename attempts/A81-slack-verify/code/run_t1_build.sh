#!/bin/bash
# A81 T1 hint-tree builds (second slot; builder 4 procs).  Usage: run_t1_build.sh TAG [TAG ...]
# TAG names a primal results/pair_primal_k4_08_b1_md1_<TAG>.json (full, c0, c1, ...)
cd "$(dirname "$0")/.." || exit 1
PY=python
for TAG in "$@"; do
  SEED=results/pair_primal_k4_08_b1_md1_${TAG}.json
  CERT=certs/pair_k4_08_s0_b1_md1_${TAG}.json
  $PY code/emit81.py --seed "$SEED" --out "$CERT" > logs/emit_${TAG}.out 2>&1 || { echo "emit $TAG failed"; continue; }
  # all roots at the A77 cap (60k/root), rule certain, Rust root order
  $PY code/hintbatch81.py "$CERT" certs/pair_k4_08_s0_b1_md1_${TAG}_hbR.json --cap 60000 --maxdepth 60 \
      --jobs 4 --chunk 512 --rule certain --root_order rust --keep_open 500 \
      --holes results/hb_md1_${TAG}.json > logs/hb_${TAG}.out 2>&1
done
