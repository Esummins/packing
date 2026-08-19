#!/bin/bash
# usage: ./launch.sh TAG NODE S [extra args...]
export PYTHONUTF8=1 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
TAG=$1; NODE=$2; S=$3; shift 3
cd "$(dirname "$0")"
nohup python run_node.py --node $NODE --s $S --tag $TAG "$@" > logs/$TAG.out 2>&1 &
echo "launched $TAG pid $!"
