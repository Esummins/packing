#!/bin/sh
# small-s eta sweep, strictly sequential (one process)
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python run_n.py --n 4 --s 2.0                --time_limit 420 --polish_rounds 3 --tag a > logs/a_n4.log  2>&1
python run_n.py --n 5 --s 2.70710678118654   --time_limit 600 --polish_rounds 3 --tag a > logs/a_n5.log  2>&1
python run_n.py --n 9 --s 3.0                --time_limit 700 --polish_rounds 3 --tag a > logs/a_n9.log  2>&1
python run_n.py --n 16 --s 4.0               --time_limit 900 --polish_rounds 3 --tag a > logs/a_n16.log 2>&1
echo CHAIN_SMALL_DONE
