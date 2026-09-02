#!/bin/bash
# A81: the sharp (eta -> 0) restricted ladder with WIDENED boxes and BOTH image rows.
cd "$(dirname "$0")/.." || exit 1
PY=python
CAT=results/catalog_k4_08_u.json
COMMON="--cls k4_08 --beta 1 --catalog $CAT --no_control_cols --headroom 6 --headroom_wait 3600"
for K in "$@"; do
  $PY code/pairlp_u.py $COMMON --etas 1e-9 --mu 0 --images id,diag --rung $K --tag _sharp_wide_k$K \
      --consolidate_rounds 0 --stop_value 0 --max_cuts 600 --cuts_per_point 2 --lp_time 900 \
      --cls_budget 3000 --max_rounds 90 > logs/run_ladder_k$K.out 2>&1
done
