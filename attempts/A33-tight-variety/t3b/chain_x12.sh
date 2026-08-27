#!/bin/sh
# tau*(s) at s above 3.877084, to locate the crossing tau*(s) = 12 (ceiling of the certifiable
# s(12) lower bound).  Sequential, warm-started up the ladder.
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python run_n.py --n 12 --s 3.95 --warm results/field_n12_s3.9.json --time_limit 1400 \
       --polish_rounds 3 --tag x12 > logs/x12_s395.log 2>&1
python run_n.py --n 12 --s 3.99 --warm results/field_n12_s3.95.json --time_limit 1400 \
       --polish_rounds 3 --tag x12 > logs/x12_s399.log 2>&1
echo CHAIN_X12_DONE
