#!/bin/bash
# A81 T1 LP sequence (ONE LP at a time; BLAS pinned inside pairlp_u.py; headroom gate 6 GB)
cd "$(dirname "$0")/.." || exit 1
PY=python
CAT=results/catalog_k4_08_u.json
COMMON="--cls k4_08 --beta 1 --catalog $CAT --no_control_cols --headroom 6 --headroom_wait 3600"
# R0: sharp semantics, widened boxes, NO row -> the plain boosted value (expect 28 = dead)
$PY code/pairlp_u.py $COMMON --etas 1e-9 --mu 0 --images "" --rung 1 --tag _sharp_wide_plain \
    --consolidate_rounds 0 --stop_value 0 --max_cuts 600 --cuts_per_point 2 --lp_time 600 \
    --cls_budget 1500 --max_rounds 60 > logs/run_R0.out 2>&1
# R1: sharp semantics, widened boxes, BOTH rows at rung 1 -> the restricted rung-1 value
$PY code/pairlp_u.py $COMMON --etas 1e-9 --mu 0 --images id,diag --rung 1 --tag _sharp_wide_k1 \
    --consolidate_rounds 0 --stop_value 0 --max_cuts 600 --cuts_per_point 2 --lp_time 900 \
    --cls_budget 2400 --max_rounds 80 > logs/run_R1.out 2>&1
# R2: MIXED-DEPTH emission under both rung-1 rows; every accepted consolidation round is dumped
$PY code/pairlp_u.py $COMMON --etas 0.1,0.05,0.02,0.008,0.002,0.0005 --mu 0.03 --images id,diag \
    --rung 1 --tag _md1 --max_cuts 300 --cuts_per_point 2 --max_rows 30000 --max_nnz 14000000 \
    --purge_every 4 --purge_min 150 --stop_value 0 --lp_solver ipm --loop_crossover on \
    --final_solver ipm --lp_time 1500 --cls_budget 7200 --max_rounds 80 \
    --consolidate_rounds 14 --consol_wmin 0.0003 --consol_grow 2.5 --consol_guard 27.95 \
    > logs/run_R2.out 2>&1
