#!/bin/bash
# A81: mixed-depth emission under the rung-K U-rows (both images), all accepted
# consolidation rounds dumped as candidates.  Usage: run_emit.sh K [GUARD]
cd "$(dirname "$0")/.." || exit 1
PY=python
K=$1
GUARD=${2:-27.95}
ETAS=${3:-0.1,0.05,0.02,0.008,0.002,0.0005}
TAG=${4:-_md_k$K}
CAT=results/catalog_k4_08_u.json
$PY code/pairlp_u.py --cls k4_08 --beta 1 --catalog $CAT --no_control_cols --headroom 6 --headroom_wait 3600 \
    --etas $ETAS --mu 0.03 --images id,diag --rung $K --tag $TAG \
    --max_cuts 300 --cuts_per_point 2 --max_rows 30000 --max_nnz 14000000 \
    --purge_every 4 --purge_min 150 --stop_value 0 --lp_solver ipm --loop_crossover on \
    --final_solver ipm --lp_time 1500 --cls_budget 7200 --max_rounds 80 \
    --consolidate_rounds 14 --consol_wmin 0.0003 --consol_grow 2.5 --consol_guard $GUARD \
    > logs/run_emit_k$K.out 2>&1
