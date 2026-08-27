#!/bin/sh
# large-s eta sweep, strictly sequential (one process).  Coarser oracle settings: the row-oracle
# cost grows like s^4 (candidate centres x atoms), so at s ~ 5-7 the s=3.88 settings are unaffordable.
# Accuracy target is ~1e-2 in eta, ample for the n-trend; every value is bracketed by the recorded
# residual-corrected upper bound and the dual fractional-packing lower bound.
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python run_n.py --n 18 --s 4.82287565553229 --time_limit 1500 --polish_rounds 3 \
       --n_theta 121 --cstep 0.015 --resid_theta 181 --resid_cstep 0.0075 --tag a > logs/a_n18.log 2>&1
python run_n.py --n 26 --s 5.62132034355964 --time_limit 1800 --polish_rounds 3 \
       --n_theta 91 --cstep 0.02 --resid_theta 121 --resid_cstep 0.01 --tag a > logs/a_n26.log 2>&1
python run_n.py --n 41 --s 6.92669309446880 --time_limit 2400 --polish_rounds 2 \
       --n_theta 61 --cstep 0.03 --resid_theta 91 --resid_cstep 0.015 --tag a > logs/a_n41.log 2>&1
echo CHAIN_LARGE_DONE
